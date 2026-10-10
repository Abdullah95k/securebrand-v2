# li-post-search

**Platform:** LinkedIn · **Route:** amber (optional, flag `LI_VENDOR_ROUTE`) · **Lane:** Discover and qualify · **Owner:** Ingestion lead (Node) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

LinkedIn is where Iraqi banks, telecom operators, oil-service firms, state companies and professionals talk about employers, tenders, outages and reputations. A client watching its brand needs to know when a post mentions it, whoever wrote it. The Community Management API, our green route, reaches only pages the client administers: it returns the client's own posts and their comments and nothing posted anywhere else, so it cannot answer "who is talking about us", and LinkedIn offers no official keyword search of posts.

harvestapi Actors on Apify are the optional route to third-party content. harvestapi does the collection itself, so the breach, if any, sits in its contract, not ours. The route is gated by `LI_VENDOR_ROUTE` (`off` or `harvestapi`), disclosed to every client in the provenance statement, and excluded from government contracts. li-post-search runs each keyword rule through the `linkedin-post-search` Actor and hands the hits to the discovery chain.

Without it the product has no LinkedIn mention detection: coverage stops at the client's own page, the registry holds only pages typed in by hand, and share-of-voice and competitor views carry a hole a bank or telecom client notices in its first week.

## 2. Objective (the end state this service delivers)

End state: every active LinkedIn keyword rule is searched once a day on the vendor route; every returned post is archived to `raw.items` with full provenance; normalize-item and keyword-matcher then write every matching post to `item.hits`, and a candidate for each unregistered poster to `discovery.hits` for poster-resolver and li-org-resolver (ADR-0031).

Target: 99% of active rules searched within their daily interval each day; zero jobs lost, `dlq.li-post-search` reviewed daily; LinkedIn vendor spend across li-post-search, li-company-posts-poller and li-post-comments-fetcher within about USD 225 to 300 a month at 0.15M items. The share search consumes is to be measured in the pilot.

## 3. Scope

### In scope

- One search a day per active LinkedIn keyword rule through harvestapi `linkedin-post-search` on Apify.
- Incremental windows per rule (cursor = newest post time seen), bounded by max items per run.
- Archiving every returned post to `raw.items` with the amber envelope.
- Allowance from quota-governor before every run; `LI_VENDOR_ROUTE` read at the start of every job.
- Backfill of a new rule: the last 90 days or the Actor's cap, whichever is smaller, once.

### Out of scope

- Keyword matching, language detection, author hashing (normalize-item, lang-dialect-id, keyword-matcher).
- Qualifying posters (poster-resolver, li-org-resolver, qualifier, registry-writer).
- Comments on found posts (li-post-comments-fetcher, driven by comment-decay-scheduler).
- Any green search (none exists) and any collection of our own (red, not built).

## 4. Users and consumers

Brand and company clients see LinkedIn mentions in dashboards and alerts labelled "amber, harvestapi"; government workspaces never do. Abdullah and product read coverage and cost per keyword. Downstream: normalize-item, keyword-matcher, poster-resolver, li-org-resolver, qualifier, store-writer, aggregator, alert-evaluator, raw-archiver, quota-governor. Ops receive rotation and budget alerts and n8n approval cards.

## 5. How it works

### 5.1 Trigger and rotation

A LinkedIn keyword rule is a registry row with `platform = linkedin`, `source_type = keyword_rule`, linked to rows in `keywords`. The scheduler keeps `next_poll_at` on it and emits a job to `jobs.li-post-search` when due. The vendor route pays per item, so rules run daily, the floor the quota governor never goes below; tier intervals apply to pages, not rules. Client pages are polled every 30 to 60 minutes by li-client-posts-poller; registry company pages follow the tier rotation, daily on the vendor route, in li-company-posts-poller.

Every rule stays on rotation: `next_poll_at` is set from the start of the last run, so cadence does not drift; jobs are ordered by `next_poll_at` then tier, so a rule is never skipped twice in a row; a rule with no hits stays daily, since silence is itself an answer. If the worker falls behind by more than one interval it serves the most-stale rules first and raises `rotation_behind`. At 80% of the vendor budget quota-governor cannot stretch below daily, so it answers wait-until or deny and the rule stays due.

Backfill on add: a new rule gets one `kind: backfill` job from backfill-orchestrator covering the last 90 days or the Actor's cap, whichever is smaller; `backfill_status` moves pending, running, then done or capped, and the rule joins the rotation.

Comments on vendor posts follow the vendor series held by comment-decay-scheduler: +24 h and +3 d after first sight, with early stop when a fetch adds fewer than 5% new comments and fewer than 5 absolute. Those jobs go to li-post-comments-fetcher only for keyword hits and posts of registered sources; posts by individuals get no comment fetch. Client posts use the 6 h, 24 h, 3 d series in li-own-comments-fetcher.

### 5.2 Step by step

1. Consume `{job_id, source_id, kind, attempt}` from `jobs.li-post-search`; the `source_id` partition keeps a rule from running twice at once.
2. Read `LI_VENDOR_ROUTE`; if `off`, acknowledge with `skipped_flag_off`, cursor unchanged.
3. If every client in `client_ids` is a government client, acknowledge with `skipped_government`.
4. Load keyword texts and variants from `keywords`, the cursor from `cursors`, the Apify token from `vendor_keys`.
5. Ask quota-governor for `budget_tag = li_vendor_post_search` with the planned max items; on wait-until or deny, re-queue and count `quota_denied_total`.
6. Start the Actor run with keyword, max items and the window since the cursor; poll until it ends.
7. Read the dataset in pages, build one envelope per item with its idempotency key, publish to `raw.items` in batches, wait for the Redpanda acknowledgement.
8. Advance the cursor to the newest posted time seen, write `service_runs` (`new_count`, `seen_count`, `pages`, `cost_units`), report consumed items to quota-governor.

### 5.3 The call it makes

Run: `POST https://api.apify.com/v2/acts/harvestapi~linkedin-post-search/runs`, header `Authorization: Bearer <Apify token from vendor_keys>`, Actor input as JSON body. Input, keys per the Actor's published schema pinned in `listening-sdk`: the keyword (one run per variant), the maximum number of items, and the date or sort filter where offered. Max items per run is set from the pilot's observed daily volume per rule; backfill runs use the Actor's cap.

Status: `GET https://api.apify.com/v2/actor-runs/{runId}` until `SUCCEEDED`, `FAILED`, `TIMED-OUT` or `ABORTED`. Items: `GET https://api.apify.com/v2/datasets/{defaultDatasetId}/items?format=json&clean=true`, paged with `offset` and `limit`. Run timeout, page size and the Actor's cap are to be measured in the pilot. No LinkedIn credential is involved.

### 5.4 What it gets

Per post, as the Actor returns it: URL and activity id, text, posted time, author (name, URL, member or company), engagement counts (reactions, comments, reposts), media references, repost context. Any shape outside the pinned schema is archived and parked.

It does not get comments (li-post-comments-fetcher), private posts, member profile data beyond what the post carries, or any guarantee of completeness or order, hence the timestamp cursor and the max-items bound.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.li-post-search` (one partition per rule); `sources`, `keywords`, `clients` (government marker), `cursors`, `vendor_keys`, `budgets` through quota-governor; environment `LI_VENDOR_ROUTE`.

### 6.2 Writes

`raw.items` (one append-only record per post), `cursors`, `service_runs`, `dlq.li-post-search`; raw-archiver writes `raw/amber/linkedin/<yyyy>/<mm>/<dd>/li-post-search/<batch>.jsonl.zst`.

```json
{
  "envelope": {
    "platform": "linkedin", "kind": "post", "route": "amber", "vendor": "harvestapi",
    "service": "li-post-search",
    "job_id": "01M4871WM0G35N2F2R5GBPWABM",
    "idempotency_key": "linkedin:post:urn:li:activity:7281234567890123456",
    "retention_class": "vendor_agreed",
    "fetched_at": "2026-10-06T03:12:44Z", "attempt": 1, "cost_units": 1
  },
  "payload": {
    "url": "https://www.linkedin.com/posts/example-bank_activity-7281234567890123456-ab12",
    "text": "post text exactly as returned",
    "postedAt": "2026-10-05T19:40:00Z",
    "author": { "type": "company", "name": "Example Bank", "url": "https://www.linkedin.com/company/example-bank/" },
    "engagement": { "reactions": 41, "comments": 6, "reposts": 2 }
  }
}
```

Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

The payload is the vendor record exactly as returned. The key uses the activity id where present, otherwise `linkedin:post:<sha256(url)>`.

### 6.3 State

Per rule in `cursors`: `cursor` (timestamp of the newest post seen), `last_success_at`, `last_error`, `consecutive_errors`. Counters in `budgets` under `li_vendor_post_search`. Flags read per job: `LI_VENDOR_ROUTE`, `sources.health`. Nothing is held between jobs.

## 7. Limits, quotas and cost

Vendor cost: harvestapi on Apify is about USD 225 to 300 a month at 0.15M LinkedIn items, about USD 1.50 to 2.00 per 1,000 items. That is the whole LinkedIn vendor budget, shared by the three amber services; the split is set in `budgets` and measured in the pilot. This service's `budget_tag` is `li_vendor_post_search`, one unit per returned item.

LinkedIn's restricted uses are carried on every LinkedIn item regardless of route: member social-activity data stored at most 48 hours; most member profile data at most 24 hours; organization social activity data six weeks, or six months if authenticated; no social-feed use; member data never exported to clients. On this route the items are vendor data under `vendor_agreed` (default 24 months for raw text), and the product's own rule applies: individuals are never profiled, so a member-authored hit becomes a mention with a hashed author reference written by normalize-item, no member profile is fetched, and no member field reaches a client export. Whether such posts should inherit `linkedin_48h` instead is for legal.

Amber provenance is disclosed to clients and excluded from government contracts; no job is emitted for a rule whose only clients are government bodies. Apify rate and concurrency limits are to be measured in the pilot.

## 8. Failure handling and fallback

- HTTP 429 or a vendor rate-limit response: exponential backoff with jitter from 30 s to 15 min, then back to the queue with `attempt + 1`; after 5 attempts, `dlq.li-post-search` and an alert.
- HTTP 401 or 403 from Apify: route marked `degraded`, batch stopped, alert fired; no key or IP rotation.
- Actor run `FAILED`, `TIMED-OUT` or `ABORTED`: transient, same backoff, cursor untouched.
- Empty 200 (a `SUCCEEDED` run with an empty dataset for a rule that produced items on recent days): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. No alternate route exists, so no `fallback_on`.
- Schema change: payload archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: cursors advance only after acknowledgement, so a replay with `attempt + 1` completes the batch; normalize-item deduplicates.

## 9. Non-functional requirements

Throughput: LinkedIn is 0.15M items a month at full scale, about 5,000 a day across all LinkedIn services; the search share is to be measured in the pilot. Latency: a daily run inside its interval suffices. Idempotency: `attempt` on every job, cursor advance after acknowledgement, keys as in 6.2. Scaling: one container image scaled on partition lag. Security: Apify token injected per job from Supabase Vault; no proxies, account pools or CAPTCHA solving; JSON logs with `job_id`, `source_id`, `route`, `vendor`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}` (including `skipped_flag_off`, `skipped_government`), `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, `actor_runs_total{status}`. Alerts: `rotation_behind` (lag above one day), DLQ non-empty, route degraded, vendor budget at 80%, empty-200 above 5% in 15 minutes.

## 11. Dependencies

`listening-sdk`, Redpanda, Supabase Postgres and Vault, quota-governor, raw-archiver, normalize-item, keyword-matcher, poster-resolver, li-org-resolver, qualifier, backfill-orchestrator, source-health-canary, retention-purger; externally Apify and harvestapi `linkedin-post-search`.

## 12. Risks and mitigations

- Actor changes shape or is withdrawn: schema pin and `schema_unknown` parking; harvestapi is the only screened LinkedIn vendor, so withdrawal pauses search until a replacement passes the screen.
- Cost overrun from broad keywords: per-rule max items, governor allowance, 80% alert, daily floor.
- Vendor gaps (missing posts, stale counts): `new_count` tracked per rule; provenance names the route.
- Member-authored content: hashed author references, no profiles, retention question to legal.
- Government leakage: `skipped_government` per job, `route = amber` on every item.

## 13. Acceptance criteria

1. With `LI_VENDOR_ROUTE=off`, a due job ends with `jobs_total{status="skipped_flag_off"}` incremented, no request to `api.apify.com`, and the cursor unchanged.
2. With `LI_VENDOR_ROUTE=harvestapi`, a due rule gets exactly one run per day, and over a 7-day test `rotation_lag_seconds` stays below 86,400 for 99% of rules.
3. Every `raw.items` record carries `route = amber`, `vendor = harvestapi`, `service = li-post-search`, `fetched_at`, `retention_class = vendor_agreed` and a `linkedin:post:<id>` key.
4. A rule whose `client_ids` are all government clients never produces an Actor run.
5. When quota-governor returns deny, no run starts, `quota_denied_total` increments and the job is re-queued.
6. A crash injected between dataset read and Redpanda acknowledgement, then a replay with `attempt + 1`, yields no duplicate on `items.normalized` and one cursor advance.
7. Five consecutive 429 responses send the job to `dlq.li-post-search` with the backoff sequence (30 s start, 15 min cap, jitter) logged, and an alert fires.
8. A 403 from Apify marks the route `degraded`, stops the batch and fires an alert; no second key is tried.
9. A new rule produces one backfill job bounded to 90 days or the Actor's cap, and `backfill_status` ends `done` or `capped`.
10. `cost_units_total` for a period equals the number of dataset items read from Apify in that period, and an item of unknown shape is archived and parked with `schema_unknown` while the rest of the batch proceeds.

## 14. Open questions

1. Does `linkedin-post-search` accept a date window, and in what order does it return items?
2. Should member-authored vendor posts carry `linkedin_48h` rather than `vendor_agreed`? For legal.
3. How many rules will be LinkedIn-active, how many items does one return a day, and does Apify add per-run overhead that makes one run per variant uneconomic?
