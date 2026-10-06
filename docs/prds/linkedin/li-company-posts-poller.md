# li-company-posts-poller

**Platform:** LinkedIn · **Route:** amber (optional, flag `LI_VENDOR_ROUTE`) · **Lane:** Fetch posts · **Owner:** Backend lead, LinkedIn adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Clients want to see what their competitors, partners, ministries and outlets post on LinkedIn, not only their own page. The official route cannot give that: the Community Management API reaches only pages the client administers (the organization must grant ADMINISTRATOR, DIRECT_SPONSORED_CONTENT_POSTER or CONTENT_ADMIN), so li-client-posts-poller covers the client's own pages and nothing else. The harvestapi Actors on Apify are the optional route to third-party company pages. harvestapi does the collection itself, so the breach, if any, sits in its contract, not ours. The route is gated by `LI_VENDOR_ROUTE` (`off` or `harvestapi`), disclosed to every client in the provenance statement, and excluded from government contracts.

li-company-posts-poller runs the `linkedin-company-posts` Actor once per registered third-party company page on a daily rotation. Without it, li-post-search finds posts by keyword but nothing reads the pages systematically: no competitor timeline, no "what did this ministry post this week", and nothing for li-post-comments-fetcher to work on. With the flag off the product still works, with the LinkedIn view limited to the client's own pages.

## 2. Objective (the end state this service delivers)

Every registered third-party company page on the vendor route is checked for new posts at least every 24 hours, every new post reaches `raw.items` within one interval of the page being polled, and the vendor spend stays inside the `li_vendor_company_posts` budget. Target: rotation lag below one interval for 99% of pages per day, no non-dormant page more than 24 hours between poll starts, zero jobs lost, spend within the monthly budget.

## 3. Scope

### In scope

- Rotation scheduling of every `route = amber`, `vendor = harvestapi` LinkedIn company page by tier, with executing jobs on `jobs.li-company-posts-poller`.
- One Apify Actor run per page per job: start, wait, read the dataset, write `raw.items` (kind `post`), advance the cursor.
- Executing the one-off backfill jobs from backfill-orchestrator; promoting dormant pages; `rotation_behind` catch-up.
- Reading `LI_VENDOR_ROUTE` at the start of every job; skipping pages whose only clients are government bodies.

### Out of scope

- Client-administered pages (li-client-posts-poller, green): when a client starts administering a page, registry-writer flips it to `route = green` and this service stops selecting it.
- Comments (li-post-comments-fetcher), keyword search (li-post-search), resolving a company URL to an organization (li-org-resolver), the decision to register a page (qualifier, registry-writer).
- Poster resolution: the poster of every item here is the registered page, so poster-resolver is not involved.
- Deduplication (normalize-item), purging (retention-purger).

## 4. Users and consumers

- **Clients** (non-government) see "competitor and partner pages, checked daily". Government clients never receive this data.
- **Ops** watches rotation lag, vendor spend and the DLQ, switches the flag, and can force a poll of one page.
- **Downstream**: normalize-item, keyword-matcher (through `items.normalized`), comment-decay-scheduler (opens the +24 h, +3 d series for li-post-comments-fetcher), raw-archiver, quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.li-company-posts-poller`, partitioned by `source_id`, emitted by the rotation scheduler inside this service (one leader replica through a Postgres advisory lock; scan period an environment variable well inside the shortest interval). It selects `sources` rows with `platform = linkedin`, `source_type = company_page`, `route = amber`, `vendor = harvestapi`, `owned_by_client = false`, `health != blocked`, `backfill_status in (done, capped)` and `next_poll_at <= now()`. `LI_VENDOR_ROUTE` is read at the start of every scan and every job.

**Cadence.** Every registered third-party company page is read every 24 hours, whatever its tier: maximum staleness 24 hours. Tier 1 pages (100,000 or more followers, or on a client's priority list) may carry a shorter interval, set in the `budgets` configuration, only while the monthly budget allows; the value is decided after the pilot has measured cost per item. quota-governor stretches any shortened interval when 80% of the monthly budget is consumed, and never beyond 24 hours. Dormant pages (no post in 30 days, so nothing to miss at daily cadence) are read weekly, as in the rotation policy; a new post promotes the page back to its reach tier through `source.events` (`tier change`). Retired pages are not polled.

**Keeping every page on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + interval`), so cadence is fixed and does not drift with run time. Jobs are emitted ordered by `next_poll_at` then tier, so an overdue Tier 3 page is not pushed aside by Tier 1 pages and no page is skipped twice in a row. A page is in at most one job at a time. A job that is skipped or waits (flag off, government-only, quota wait-until) keeps its `next_poll_at`, so the page is first in line next time and never silently dropped.

**Catch-up.** `rotation_lag_seconds` is now minus `next_poll_at` of the most overdue page. When it exceeds one interval the scheduler switches to most-stale-first and raises `rotation_behind`. After an outage, or after the flag has been off, overdue pages drain most-stale-first at the pace quota-governor allows (wait-until), not as one burst. Every read is incremental from the cursor, so a late poll still returns everything since the cursor within the run's max items.

**Backfill on add.** A new page arrives with `backfill_status = pending` after li-post-search or a client request led qualifier to register it and li-org-resolver resolved the organization. backfill-orchestrator reads the last 90 days or the Actor's cap, whichever is smaller, once, sets `done` or `capped` and `next_poll_at = now()`; only then does this scheduler pick the page up.

**Comment decay.** Each new post flows `raw.items` → normalize-item → `items.normalized`, where comment-decay-scheduler opens the series for li-post-comments-fetcher: +24 h, +3 d.

### 5.2 Step by step

1. Consume a job (`job_id`, `source_id`, `kind` = rotation | backfill | ops_force, `attempt`); read the `sources` and `cursors` rows; read `LI_VENDOR_ROUTE`. If it is `off`, acknowledge with `skipped_flag_off` and keep `next_poll_at`.
2. If every client in `client_ids` is a government client, acknowledge with `skipped_government`; no run is started.
3. Load the page identifier from `sources` and the Apify token from `vendor_keys`.
4. Ask quota-governor for allowance under `budget_tag = li_vendor_company_posts` with the planned max items; on wait-until requeue; on deny count `quota_denied_total` and keep `next_poll_at`.
5. Start the Actor run (5.3), wait for a terminal status, read the run's dataset.
6. Drop items at or before the cursor (counted as `seen_count`, still billed); write one `raw.items` message per new post; raw-archiver lands the batch under `raw/amber/linkedin/<yyyy>/<mm>/<dd>/li-company-posts-poller/`.
7. After Redpanda acknowledges: set `cursor` to the newest post time seen, `last_success_at`, `consecutive_errors = 0`, `last_polled_at`, `next_poll_at`; report `cost_units` (items returned) to quota-governor; emit `tier change` if a dormant page posted.

### 5.3 The call it makes

```
POST https://api.apify.com/v2/acts/harvestapi~linkedin-company-posts/runs
  Authorization: Bearer <Apify token from vendor_keys>
  body (JSON): the company page URL, the maximum number of items, a recency filter where offered
               (input field names to be confirmed in the pilot)
-> run id; wait until status SUCCEEDED | FAILED | TIMED-OUT | ABORTED
   (GET /v2/actor-runs/<run id>, wait interval an environment variable)
GET https://api.apify.com/v2/datasets/<defaultDatasetId>/items?offset=<n>&limit=<n>
```

One run per page in v1, so a cursor or a failure is never shared between pages. Max items per run comes from the page's observed posting rate, with a floor and a cap held in `budgets` (values to be measured in the pilot); backfill runs use the Actor's cap. The Actor's input schema is pinned in `listening-sdk`. Pagination is the dataset's offset and limit; the run itself is not paged.

### 5.4 What it gets

Per post, as the Actor's output schema defines it (illustrative; field names to be confirmed in the pilot): post id and URL, text, the company as author, post time, media references, engagement counts (reactions, comments, shares).

```json
{
  "id": "7246999999999999999",
  "linkedinUrl": "https://www.linkedin.com/posts/example-company_activity-7246999999999999999",
  "content": "نبارك للفريق الفائز بجائزة الابتكار لهذا العام",
  "author": {"name": "Example Company", "linkedinUrl": "https://www.linkedin.com/company/example-company", "type": "company"},
  "postedAt": {"timestamp": 1791271800000, "date": "2026-10-06T07:30:00.000Z"},
  "engagement": {"likes": 41, "comments": 7, "shares": 3}
}
```

What it does not get: comments (li-post-comments-fetcher); reactor identities; impressions; posts beyond the Actor's cap; and no deletion signal, because an absent post cannot be told from a post the Actor did not return, so this route never emits `deletions`. Counts are a snapshot at first sight; whether they are refreshed at +24 h and +7 d is open (section 14).

## 6. Inputs and outputs

### 6.1 Reads

`jobs.li-company-posts-poller`; `sources`, `cursors`, `client_sources` (priority list, government flag through `clients`), `vendor_keys`, `budgets` through quota-governor; `source.events`; the flag `LI_VENDOR_ROUTE`; `health` through the SDK canary hook.

### 6.2 Writes

`raw.items`, one message per new post:

```json
{
  "envelope": {
    "platform": "linkedin", "kind": "post", "route": "amber", "vendor": "harvestapi",
    "service": "li-company-posts-poller",
    "source_id": "8a4e1c27-5d3b-4f60-b9a2-7e0c6d1f3a58",
    "platform_id": "7246999999999999999",
    "idempotency_key": "linkedin:post:7246999999999999999",
    "job_id": "01J9N3D2M6V4Q8S1X7C5E0A3RJ", "attempt": 1,
    "fetched_at": "2026-10-06T08:41:07Z",
    "retention_class": "vendor_agreed",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/amber/linkedin/2026/10/06/li-company-posts-poller/000007.jsonl.zst",
    "metrics_observation": "poll"
  },
  "payload": { "...": "the dataset item from 5.4, unchanged" }
}
```

Also `source.events` (`tier change`, `updated` when a page stops resolving), `service_runs`, `dlq.li-company-posts-poller` after 5 failed attempts. The Apify run id goes into the structured logs and `service_runs`.

### 6.3 State

`cursors.cursor` = newest post time stored; `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`; `budgets` counters for `li_vendor_company_posts`; in memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- **Vendor cost.** harvestapi on Apify costs about USD 225 to 300 a month at 0.15M LinkedIn items for all its use, about USD 1.50 to 2.00 per 1,000 items; that is the whole LinkedIn vendor budget, shared by li-post-search, li-org-resolver and the two services in this lane; the split lives in `budgets` and is measured in the pilot. This service's tag is `li_vendor_company_posts`, one unit per returned item, including items dropped as already seen. Whether an empty run costs anything beyond Apify platform usage: to be measured in the pilot.
- **Stretch.** At 80% of the monthly budget quota-governor stretches shortened intervals back to 24 hours, never beyond; at 100% it denies, jobs wait, and `rotation_behind` fires as a budget alarm, not a silent skip.
- **Restricted-use facts (LinkedIn terms).** Member social-activity data at most 48 hours; most member profile data 24 hours; organization social activity data six weeks (six months if authenticated); no social-feed use; member data never exported or transferred to clients, client-facing output is aggregated. Company-authored items carry `vendor_agreed`. An item whose original author is a member (a repost) is treated as `linkedin_48h` until legal decides (shared with li-post-search).
- Apify rate and concurrency limits: to be measured in the pilot.

## 8. Failure handling and fallback

- HTTP 429 or a vendor rate-limit response: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.li-company-posts-poller` and an alert fires.
- HTTP 401 or 403 from Apify: route marked `degraded`, batch stopped, alert; no key or IP rotation.
- Run `FAILED`, `TIMED-OUT` or `ABORTED`: transient, same backoff, cursor untouched.
- Empty dataset for a page known to post: counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. No second LinkedIn vendor exists, so `fallback_on` is never set; the flag can be turned off by ops.
- Page no longer resolves (three consecutive not-found runs): page marked `degraded`, `source.events` `updated`, re-resolution by li-org-resolver.
- Schema change: payload archived, normalize-item raises `schema_unknown` and parks the batch. Partial write: cursors move only after acknowledgement; replays are deduplicated.

## 9. Non-functional requirements

- Throughput: one run per page per day plus weekly dormant runs; items per month within the share of 0.15M that `budgets` assigns (page count to be measured in the pilot).
- Latency: a post reaches `raw.items` within its interval plus run time (minutes).
- Idempotency: `linkedin:post:<platform_id>`; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag; one leader scheduler; Apify concurrency capped by an environment variable.
- Security: Apify token from Supabase Vault via `vendor_keys`, never logged; no account pools, no proxies; provenance on every message.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `apify_runs_total{status}`, `items_seen_dropped_total` and `budget_used_ratio`. Alerts: `rotation_behind`, `budget_80pct`, `route_degraded`, `dlq_nonempty`, `empty_200_rate`. SLO: rotation lag below one interval for 99% of pages per day.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, comment-decay-scheduler, li-post-comments-fetcher, li-post-search, li-org-resolver, qualifier, registry-writer, backfill-orchestrator, retention-purger, Supabase Postgres and Vault, Redpanda; externally Apify and the harvestapi `linkedin-company-posts` Actor.

## 12. Risks and mitigations

- The vendor route can be withdrawn or break: it is optional behind `LI_VENDOR_ROUTE`; clients are told in the provenance statement; the green route is unaffected.
- Cost overrun: per-service budget tag, 80% stretch, 100% deny.
- Actor output changes: schema pinned, `schema_unknown` parks batches.
- Ownership of the harvestapi publisher is not verified in the clearance list (Apify, Czechia, is cleared): verify before launch, per the no-Israeli-vendor rule.
- Counts are snapshots: stated in the product.

## 13. Acceptance criteria

1. With `LI_VENDOR_ROUTE = off` no job is emitted and no Apify call is made; switching to `harvestapi` resumes within one scan and drains overdue pages most-stale-first, paced by quota-governor.
2. A page whose run started at 09:00:00 has `next_poll_at = 09:00:00` the next day even if the run took 6 minutes.
3. With 200 fixture pages across tiers against a simulated Apify for 7 days, no non-dormant page goes more than 24 hours between poll starts, including a day on which the budget crosses 80%.
4. At 80% of the monthly budget a Tier 1 page with a shortened interval is stretched back to 24 hours, and no interval above 24 hours is ever set for a non-dormant page.
5. A page whose clients are all government bodies is acknowledged `skipped_government` and no run is started.
6. `cost_units_total` for a period equals the number of dataset items read in that period.
7. The cursor does not advance when a run is `FAILED` or `TIMED-OUT`; the replayed job re-emits posts with the same `idempotency_key` and normalize-item stores one item per post.
8. A simulated 429 triggers backoff from 30 s to at most 15 min with `attempt + 1`; after 5 attempts the job is in `dlq.li-company-posts-poller` and an alert fired. A 403 from Apify marks the route `degraded`, stops the batch and no second key is tried.
9. Every `raw.items` message carries `route = amber`, `vendor = harvestapi`, `service`, `fetched_at` and `retention_class`; an item of unknown shape is archived and parked as `schema_unknown` while the rest of the batch proceeds.
10. A page that registry-writer flips to `route = green` is no longer selected; a page with `backfill_status = pending` is never emitted as a rotation job.

## 14. Open questions

1. One run per page or several pages per run: per-run overhead and the cost of an empty run are to be measured in the pilot.
2. The Tier 1 shortened interval: which value, and how many pages the budget affords.
3. Refreshing counts at +24 h and +7 d means re-reading posts, which costs items: restrict it to priority-list pages, or accept first-sight counts?
4. Owner and country of the harvestapi publisher: to be verified before launch.
5. Reposts of member posts: `linkedin_48h` or `vendor_agreed`? For legal, shared with li-post-search.
