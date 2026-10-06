# li-client-posts-poller

**Platform:** LinkedIn · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, LinkedIn adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

LinkedIn is the smallest stream in the product, 0.15M of the 30.5M items a month at full scale, but it is where a company speaks as a company: announcements, tenders, hiring, partnerships. li-client-posts-poller reads the posts of the company pages a client itself administers, through the only green LinkedIn route: the Community Management API, Posts API, scope `r_organization_social`, with the organization URN as author. That API reaches only pages the client administers: the organization must grant the connecting user ADMINISTRATOR, DIRECT_SPONSORED_CONTENT_POSTER or CONTENT_ADMIN. It does not reach competitors, ministries or outlets the client does not run; those are the optional amber route (li-company-posts-poller, flag `LI_VENDOR_ROUTE`), which government contracts exclude.

Without this service a client's own LinkedIn presence is invisible to the product: no own-post history, no baseline to compare competitors against, no new-post trigger for the comment series, and nothing for li-own-comments-fetcher to fetch comments under. For a government client this is the whole LinkedIn product, because amber data is excluded from their contracts.

## 2. Objective (the end state this service delivers)

Every client-administered page with a valid grant is read every 30 to 60 minutes, every new or edited post reaches `raw.items` within one interval, deletions are mirrored, and the cursor advances only after Redpanda has acknowledged the batch. Target: rotation lag below one interval for 99% of pages per day, staleness p95 within 60 minutes, every page reconciled over its last 7 days once a day, zero jobs lost.

## 3. Scope

### In scope

- Rotation scheduling of every `route = green`, `owned_by_client = true` LinkedIn company page: 30 minutes for the client's priority list, 60 minutes for the rest, plus a daily reconciliation read.
- Incremental reads from the cursor (new and edited posts), mirrored deletions, and the reaction and comment counts that come with a post.
- Writing `raw.items` (kind `post`), advancing `cursors`, `rotation_behind` catch-up, executing the backfill jobs that backfill-orchestrator emits.

### Out of scope

- Comments (li-own-comments-fetcher) and live comment and reaction events (li-notification-receiver).
- Third-party company pages (li-company-posts-poller, amber), keyword search (li-post-search, amber), resolving third-party pages (li-org-resolver, amber).
- Posts on members' personal profiles: the scope reads organization posts only.
- Deduplication (normalize-item), registry changes (qualifier, registry-writer), purging (retention-purger), media download.

## 4. Users and consumers

- **Clients** experience it as "my company page's posts, never more than an hour old"; they connect LinkedIn by OAuth and choose which administered pages to add (`added_by = client`). They never call it.
- **Ops** watches rotation lag, grant and token health, and the DLQ, and can force a poll of one page (`ops_force`).
- **Downstream**: normalize-item, comment-decay-scheduler (opens the +6 h, +24 h, +3 d series from `items.normalized`), li-own-comments-fetcher, li-notification-receiver (matches events to the posts stored here), raw-archiver, retention-purger, source-health-canary, quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.li-client-posts-poller`, partitioned by `source_id`, emitted by the rotation scheduler inside this service (one leader replica elected through a Postgres advisory lock; scan period an environment variable well inside 30 minutes). It selects `sources` rows with `platform = linkedin`, `source_type = company_page`, `route = green`, `owned_by_client = true`, `health != blocked`, `backfill_status in (done, capped)` and `next_poll_at <= now()`.

**Cadence.** Pages on a client's priority list: every 30 minutes. All other client-administered pages: every 60 minutes. The follower tiers do not apply: the page is the client's own property, the cost is quota and not money, and freshness is what the client buys. There is no dormant tier: a quiet page that wakes up is the case the client cares about most, so it is still read every 60 minutes. Only `blocked` or retired pages are not polled. The generic push tier does not apply either: Organization Social Action Notifications report social actions on posts, not the publication of a post (to be confirmed in the pilot, section 14), so new posts are found by polling and li-notification-receiver covers comments and reactions in between.

**Keeping every page on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + interval`), so cadence is fixed and does not drift with fetch time. Jobs are emitted ordered by `next_poll_at` then tier (priority-list pages first on a tie), so a 60-minute page is never pushed aside by 30-minute pages and no page is skipped twice in a row. A page is in at most one job at a time (partition key). A failed job keeps the old `next_poll_at`, making that page the first candidate on the next scan.

**Catch-up.** `rotation_lag_seconds` is now minus `next_poll_at` of the most overdue page. When it exceeds one interval the scheduler switches to most-stale-first and raises `rotation_behind`. Every poll reads incrementally from the cursor, so a late poll still returns everything since the cursor: being behind costs freshness, not completeness.

**Daily reconciliation.** Once every 24 hours per page (kind `reconciliation`, tracked in a second `cursors` row, service `li-client-posts-poller:reconcile`) the poll ignores the cursor and re-reads the last 7 days of posts in full, with counts. It catches posts a poll missed, edits and state changes, and deletions: a stored post of those 7 days that the API no longer returns becomes a `deletions` message with reason `platform_sync`. It also refreshes counts, which gives the +24 h and +7 d observations without a metrics service. li-notification-receiver's events are reconciled against this read and against li-own-comments-fetcher's daily comment read.

**Backfill on add.** A new page arrives with `backfill_status = pending`. backfill-orchestrator reads the last 90 days or the route's cap, whichever is smaller; here the cap is how long we may keep organization social activity data, six weeks (six months if the data is authenticated, to be confirmed in the pilot). It sets `done` or `capped` and `next_poll_at = now()`; only then does this scheduler pick the page up.

**Comment decay.** Each new post flows `raw.items` → normalize-item → `items.normalized`, where comment-decay-scheduler opens the series for li-own-comments-fetcher: +6 h, +24 h, +3 d.

### 5.2 Step by step

1. Consume a job (`job_id`, `source_id`, `kind` = rotation | reconciliation | backfill | ops_force, `attempt`); read the `sources` and `cursors` rows; stop if `health = blocked`.
2. Take the OAuth token of the client who connected the page from Supabase Vault, for this job only.
3. Ask quota-governor for allowance under `budget_tag = linkedin_cm:<client_id>`; on wait-until requeue for that time; on deny count `quota_denied_total` and keep `next_poll_at`.
4. Call the Posts API for the organization (5.3), newest first, from the cursor minus the overlap (rotation), the last 7 days (reconciliation) or the backfill window, until a post older than the window or the last page.
5. Write one `raw.items` message per post; on reconciliation compare returned ids with stored ids and emit `deletions` for the missing ones. raw-archiver lands the batch under `raw/green/linkedin/<yyyy>/<mm>/<dd>/li-client-posts-poller/`.
6. After Redpanda acknowledges: set `cursor` to the newest `lastModifiedAt` seen, `last_success_at`, `consecutive_errors = 0`, `last_polled_at`, `next_poll_at`.
7. Record the metrics of section 10 and the rate-limit usage into `budgets`.

### 5.3 The call it makes

Posts API, find by author, scope `r_organization_social`. Path, `Linkedin-Version` value and parameter names are to be confirmed in the pilot; the shape is:

```
GET <Posts API, find by author>
  author=urn:li:organization:<organization id>        (organization URN as author)
  count=<page size: API maximum, to be confirmed>  start=<offset>
  sort: last modified, newest first
  Authorization: Bearer <client's OAuth token, scope r_organization_social>
  Linkedin-Version: <pinned in one environment variable shared by all li-* services>
```

Pagination: offset paging, newest first, stop at the window start. The window starts at the cursor minus an overlap (environment variable; value to be measured in the pilot) to absorb publication delay. Counts: read with the post where the API returns them; otherwise one batched social-metadata lookup per poll for posts younger than 7 days (to be confirmed in the pilot). Auth: always the client's own token, never a token of ours.

### 5.4 What it gets

Per post: URN, author organization, commentary, visibility, lifecycle state, created, published and last-modified times, distribution, a content reference (article, image, video, document, poll), reaction and comment counts. Illustrative shape; field names to be confirmed in the pilot:

```json
{
  "id": "urn:li:share:7247000000000000001",
  "author": "urn:li:organization:12345678",
  "commentary": "يسرّنا الإعلان عن افتتاح مركز الخدمة الجديد في بغداد، بانتظار زيارتكم",
  "visibility": "PUBLIC", "lifecycleState": "PUBLISHED",
  "createdAt": 1791271740000, "publishedAt": 1791271800000, "lastModifiedAt": 1791271800000,
  "content": {"article": {"source": "https://example.iq/news/service-centre", "title": "مركز الخدمة الجديد"}},
  "socialMetadata": {"reactionSummaries": {"LIKE": {"count": 41}, "PRAISE": {"count": 12}}, "commentSummary": {"count": 7}}
}
```

What it does not get: personal-profile posts; pages the client does not administer; commenter identity; media files (references only); anything for a page whose grant has been lost.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.li-client-posts-poller`; `sources`, `cursors`, `clients` (token reference), `client_sources` (priority list), `budgets` through quota-governor, `health` through the SDK canary hook; `source.events` (`added`, `updated`, `route` change, `retired`) to refresh its view of the rotation.

### 6.2 Writes

`raw.items`, one message per post, envelope plus the record as returned:

```json
{
  "envelope": {
    "platform": "linkedin", "kind": "post", "route": "green", "vendor": null,
    "service": "li-client-posts-poller",
    "source_id": "3d2f8a14-6b7c-4e19-8a05-c1f7e2b94d36",
    "platform_id": "urn:li:share:7247000000000000001",
    "idempotency_key": "linkedin:post:urn:li:share:7247000000000000001",
    "job_id": "01J9N3C5K8W2R7T4Y1B6D0F9GH", "attempt": 1,
    "fetched_at": "2026-10-06T08:20:11Z",
    "retention_class": "linkedin_48h",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/linkedin/2026/10/06/li-client-posts-poller/000041.jsonl.zst",
    "metrics_observation": "poll"
  },
  "payload": { "...": "the post object from 5.4, unchanged" }
}
```

Also `deletions` (reason `platform_sync`), `source.events` (`updated` when a grant is lost), `service_runs`, and `dlq.li-client-posts-poller` after 5 failed attempts.

### 6.3 State

`cursors.cursor` = newest `lastModifiedAt` stored, with `last_success_at`, `last_error`, `consecutive_errors`; the reconciliation cursor row; `sources.last_polled_at`, `next_poll_at`, `health`; `budgets` counters per client token; in memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- **Restricted-use facts (LinkedIn terms).** Member social-activity data may be stored at most 48 hours; most member profile data 24 hours; organization social activity data six weeks (six months if authenticated). No social-feed use: the application shows analysis and aggregates of the client's pages, never a browsable LinkedIn feed. Member data is never exported or transferred to clients; client-facing output is aggregated.
- **Retention.** The envelope carries `linkedin_48h`, the class for everything this route stores; retention-purger applies it by field: the page's own posts and counts as the organization rule allows (six weeks, six months if authenticated), any member-level field that appears (an administrator or a mentioned member) at 48 hours. Aggregates and derived scores (posts and engagement per page per day) are kept ten years.
- **Quota.** Budget tag `linkedin_cm:<client_id>`, one unit per API call. LinkedIn's per-app and per-member limits are not in our fact sheet; calls per day and the limit per client token are to be measured in the pilot.
- **Cost.** No per-call fee is listed for the Community Management API (USD 0 per call as far as the fact sheet shows); the constraint is quota.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.li-client-posts-poller` and an alert fires.
- HTTP 401 or 403: stop the batch. If the same token succeeded on another page in the last 15 minutes, the page is `blocked` (administrator role removed) and `source.events` `updated` notifies the client; otherwise the token is `degraded`. Alert either way; never rotate tokens or IPs around a block.
- Empty 200 from a page known to post: counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`.
- No amber fallback: a client's own page is never read through the vendor route, so its provenance stays green and government clients are unaffected; `fallback_on` is never set here.
- Schema change: payload archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: cursors move only after acknowledgement; a replayed job re-emits the same posts and normalize-item deduplicates.

## 9. Non-functional requirements

- Throughput: the LinkedIn share of the full-scale target is 0.15M items a month across all routes; the green share, page count and calls per day are to be measured in the pilot.
- Latency: a post visible through the API reaches `raw.items` within its interval plus fetch time.
- Idempotency: `linkedin:post:<platform_id>`; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag; one leader scheduler.
- Security: tokens from Supabase Vault per job, never logged; no account pools, no proxies; provenance on every message.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `pages_in_rotation{interval}` and `grant_lost_total`. Alerts: `rotation_behind`, `token_degraded`, `grant_lost`, `dlq_nonempty`, `empty_200_rate`, `quota_deny_rate`. SLO: rotation lag below one interval for 99% of pages per day.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, comment-decay-scheduler, li-own-comments-fetcher, li-notification-receiver, backfill-orchestrator, registry-writer, retention-purger, Supabase Postgres and Vault, Redpanda. LinkedIn prerequisites: Community Management API approved for our app; each client's OAuth grant with ADMINISTRATOR, DIRECT_SPONSORED_CONTENT_POSTER or CONTENT_ADMIN on the page.

## 12. Risks and mitigations

- Product approval or tier limits for the Community Management API delay launch: the pilot runs on one or two friendly client pages.
- A client's administrator leaves and the role disappears: the page goes `blocked` and the client is told to re-grant; no silent gap.
- 48-hour and no-feed rules constrain the product: output is aggregated; the UI checklist forbids feed views and exports of member data.
- Version sunsets: version pinned in one variable; `schema_unknown` parks batches rather than dropping them.
- Unknown rate limits: the 30-minute cadence can fall back to 60 minutes by registry change.

## 13. Acceptance criteria

1. A priority-list page whose poll started at 09:00:00 has `next_poll_at = 09:30:00`, and any other page 10:00:00, even when the fetch took 4 minutes.
2. With 100 fixture pages against a simulated API for 24 hours, no page's `rotation_lag_seconds` exceeds its interval.
3. With the scheduler held back, `rotation_behind` fires, the most stale page is emitted first, and no page is skipped in two consecutive scans.
4. An edited post (later `lastModifiedAt`) yields a second `raw.items` message with the same `idempotency_key`; normalize-item stores one item with a new version.
5. The cursor does not advance when the Redpanda produce fails; the next attempt re-emits the batch.
6. The daily reconciliation turns a stored post of the last 7 days that the simulated API no longer returns into one `deletions` message with reason `platform_sync`, and touches nothing older.
7. A simulated 429 triggers backoff from 30 s to at most 15 min with `attempt + 1`; after 5 attempts the job is in `dlq.li-client-posts-poller` and an alert fired.
8. A 403 on one page while another page on the same token returns 200 marks only that page `blocked`; a 401 marks the token `degraded`, stops the batch and no further call uses it.
9. A page with `backfill_status = pending` is never emitted as a rotation job; a finished backfill never reaches back beyond min(90 days, the retention cap).
10. Every `raw.items` message carries `route = green`, `vendor = null`, `service`, `fetched_at` and `retention_class = linkedin_48h`; tokens never appear in logs or envelopes; no request goes to the vendor route.

## 14. Open questions

1. Do Organization Social Action Notifications announce new posts? If yes, client pages can move to the push-tier rule (one reconciliation poll a day) by a registry change; to be confirmed in the pilot.
2. Does our access count as "authenticated" for the six-month organization-data allowance, or is it six weeks? Decides the backfill cap; for legal and the pilot.
3. Does the Posts API return counts, or is the second social-metadata call needed? To be confirmed in the pilot.
4. Is the 30-minute priority list the same flag that makes a source Tier 1 in `client_sources`? Proposed: yes.
