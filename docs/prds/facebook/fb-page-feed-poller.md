# fb-page-feed-poller

**Platform:** Facebook · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, Facebook adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Facebook is the largest stream in the product: 12.0M of the 30.5M items a month at full scale, almost all of it public posts on Pages (brands, outlets, ministries, state companies, creators) and the comments under them. fb-page-feed-poller is the service that reads those Pages, through the only green route to third-party Page posts: the Meta Graph API `/feed` edge under Page Public Content Access (PPCA) on our verified Tech Provider app.

Without it the Facebook side of the product is empty apart from client-owned Pages (fb-client-webhook-receiver) and vendor-sourced group posts (fb-group-posts-poller, amber, optional, excluded from government contracts): no competitor tracking, no outlet monitoring, no mention baseline, and nothing for fb-post-comments-fetcher or fb-reactions-fetcher to work on, because both key off the posts this service finds. The freshness promise, every registered Page re-checked within its tier's interval, is kept or broken here.

## 2. Objective (the end state this service delivers)

Every green Facebook Page in the registry with an active tier is polled on its tier's cadence, every new post reaches `raw.items` within one tier interval of Meta making it visible, and the cursor advances only after Redpanda has acknowledged the batch. Target: rotation lag below one tier interval for 99% of Pages per day, staleness p95 within the tier maximum (1 h, 6 h, 24 h), zero jobs lost.

## 3. Scope

### In scope

- Rotation scheduling of every green Facebook Page by tier (1, 2, 3, push reconciliation, dormant) and execution of the jobs on `jobs.fb-page-feed-poller`.
- Incremental reads with `since`, including a 24-hour overlap that absorbs Meta's content latency.
- Requesting reaction, comment and share summaries on the same call, so fb-reactions-fetcher gets its first observation free.
- Writing `raw.items` (kind `post`); advancing `cursors`; promoting dormant Pages; `rotation_behind` catch-up.

### Out of scope

- The first 90-day read of a new Page (fb-backfill); comments (fb-post-comments-fetcher); metrics refreshes at +24 h and +7 d (fb-reactions-fetcher); groups (fb-group-posts-poller); client-owned Page events (fb-client-webhook-receiver).
- Reels: not returned on `/feed` under PPCA, so not fetched on the green route.
- Deduplication (normalize-item), keyword matching (keyword-matcher), tier decisions (qualifier, registry-writer).

## 4. Users and consumers

- **Clients** experience it as "new posts from the Pages I watch, never older than my tier allows"; they never call it.
- **Ops** watches rotation lag, token health and the DLQ, and can force a poll of one Page.
- **Downstream services**: normalize-item (consumes `raw.items`), comment-decay-scheduler (receives new posts through `items.normalized`), fb-reactions-fetcher (reads the summaries in the payload), raw-archiver, source-health-canary, quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.fb-page-feed-poller`, partitioned by `source_id`, emitted by the rotation scheduler inside this service (one leader replica elected through a Postgres advisory lock; the scan period is an environment variable well inside the shortest tier interval of 60 minutes). The scheduler selects `sources` rows with `platform = facebook`, `source_type = page`, `route = green`, `health != blocked`, `backfill_status in (done, capped)` and `next_poll_at <= now()`.

**Cadence by tier.** Tier 1 (100,000 or more followers, or on a client's priority list): every 60 minutes, maximum staleness 1 hour. Tier 2 (10,000 to 99,999): every 6 hours. Tier 3 (below 10,000): every 24 hours. Push (client-owned Pages on fb-client-webhook-receiver): no polling for new posts, one reconciliation poll every 24 hours. Dormant (no post in 30 days): weekly; a new post promotes the Page back to its reach tier through `source.events` (`tier change`). Retired: never polled.

**Keeping every Page on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + interval`), so cadence is fixed and does not drift with fetch time. Jobs are emitted ordered by `next_poll_at` then by tier, so an overdue Tier 3 Page is not pushed aside by Tier 1 Pages and no Page is skipped twice in a row. A Page is in at most one job at a time (partition key). A failed job keeps the old `next_poll_at`, making that Page the first candidate on the next scan.

**Catch-up.** `rotation_lag_seconds` is now minus `next_poll_at` of the most overdue Page. When it exceeds one interval, the scheduler switches to most-stale-first ordering and raises `rotation_behind`. Every poll is incremental from the cursor, so a late poll still returns everything since the cursor (within the ranked-feed cap): being behind costs freshness, not completeness.

**Backfill on add.** A new Page arrives with `backfill_status = pending`. fb-backfill reads the last 90 days (or the cap), writes the cursor, sets `done` or `capped` and `next_poll_at = now()`; only then does this scheduler pick the Page up.

**Comment decay.** Each new post flows `raw.items` → normalize-item → `items.normalized`, where comment-decay-scheduler opens the series for fb-post-comments-fetcher: +1 h, +6 h, +24 h, +3 d, +7 d, then weekly until day 30; early stop when a fetch adds fewer than 5% new comments and fewer than 5 absolute; extension to every 2 days until day 30 when the day-7 fetch still adds 20% or more; an extra hourly fetch for 6 hours when velocity exceeds 100 new comments per hour.

### 5.2 Step by step

1. Consume a job (`source_id`, `tier`, `attempt`, `reason` = rotation | reconciliation | ops_force); read the `sources` row and the `cursors` row for (`source_id`, `fb-page-feed-poller`); stop if `health = blocked`.
2. Select the token: the system-user token of the first client in `client_ids` whose token is healthy, fetched from Supabase Vault for this job only; for `owned_by_client` Pages, the client's Page access token.
3. Ask quota-governor for allowance under `budget_tag = meta_graph_pages:<client_id>`; on wait-until, requeue for that time; on deny, count `quota_denied_total` and keep `next_poll_at`.
4. Call `/feed` with `since = cursor − 24 h` and `limit = 100`; follow `paging.next` until a page is empty.
5. Write one `raw.items` message per post; raw-archiver lands the batch under `raw/green/facebook/<yyyy>/<mm>/<dd>/fb-page-feed-poller/`.
6. After Redpanda acknowledges: set `cursor` to the newest `created_time` seen, `last_success_at`, `consecutive_errors = 0`, `last_polled_at`, `next_poll_at`; emit `tier change` if a dormant Page posted.
7. Record the metrics of section 10 and the usage headers Meta returns (`X-App-Usage`, `X-Business-Use-Case-Usage`) into `budgets`.

### 5.3 The call it makes

```
GET https://graph.facebook.com/v<pinned>/{page-id}/feed
  ?fields=id,message,story,created_time,updated_time,permalink_url,status_type,
          full_picture,attachments{media_type,type,url,title,description},shares,
          comments.summary(total_count).limit(0),
          reactions.type(LIKE).summary(total_count).limit(0).as(like),
          <same for LOVE, HAHA, WOW, SAD, ANGRY, CARE, aliased love, haha, wow, sad, angry, care>
  &limit=100
  &since=<unix timestamp: cursor minus 24 h>
  &access_token=<system-user token (PPCA); Page access token for owned_by_client Pages>
```

Pagination: cursor-based, follow `paging.next`. Page size: `limit` max 100. `from` is not requested: under PPCA user information comes only with a Page access token, and on a Page's own feed the poster is the Page itself. The Graph version is pinned by one environment variable shared by all fb-* services.

### 5.4 What it gets

Per post, the fields requested above; `id` is `<page-id>_<post-id>`. Example:

```json
{
  "id": "100064583471102_1198837625012734",
  "message": "عرض الباقة الجديدة متوفر الآن في جميع فروعنا",
  "created_time": "2026-10-06T07:12:09+0000",
  "permalink_url": "https://www.facebook.com/100064583471102/posts/1198837625012734",
  "status_type": "added_photos",
  "shares": {"count": 41},
  "comments": {"summary": {"total_count": 312}},
  "like": {"summary": {"total_count": 1840}}, "love": {"summary": {"total_count": 95}},
  "haha": {"summary": {"total_count": 12}}, "wow": {"summary": {"total_count": 3}},
  "sad": {"summary": {"total_count": 0}}, "angry": {"summary": {"total_count": 27}},
  "care": {"summary": {"total_count": 8}}
}
```

What it does not get: Reels; comment text or ids (fb-post-comments-fetcher); commenter or reactor identity (never under PPCA); posts Meta's ranking drops, because `/feed` returns about 600 ranked posts per Page per year; posts Meta has not yet surfaced (up to 24 hours late), hence the overlap.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.fb-page-feed-poller`; `sources`, `cursors`, `clients` (token reference), `budgets` through quota-governor, `health` through the SDK canary hook; `source.events` (`added`, `tier change`, `retired`) to refresh its view of the rotation.

### 6.2 Writes

`raw.items`, one message per post, envelope plus the record exactly as returned:

```json
{
  "envelope": {
    "platform": "facebook", "kind": "post", "route": "green", "vendor": null,
    "service": "fb-page-feed-poller",
    "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
    "platform_id": "100064583471102_1198837625012734",
    "idempotency_key": "facebook:post:100064583471102_1198837625012734",
    "job_id": "01J9N2Q7Z4T8X1V6M3K0H5R2WB", "attempt": 1,
    "fetched_at": "2026-10-06T09:15:42Z",
    "retention_class": "meta_on_request",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/facebook/2026/10/06/fb-page-feed-poller/000123.jsonl.zst",
    "metrics_observation": "poll"
  },
  "payload": { "...": "the post object from 5.4, unchanged" }
}
```

Also `source.events` (`tier change`), `service_runs`, `dlq.fb-page-feed-poller` after 5 failed attempts.

### 6.3 State

`cursors.cursor` = ISO `created_time` of the newest stored post, plus `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`; `budgets` counters per token per 24 h; in memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- Rate limit: the Pages bucket allows 4,800 calls × engaged users per 24 h with a system-user token; quota-governor keeps the counter per token.
- Error 80001 means "too many calls to this Page": per-Page backoff and the next poll deferred by one interval; repeated 80001 on one Page is reported to ops.
- `/feed` returns about 600 ranked posts per Page per year with `limit` max 100: this service is not a complete record of a very active Page, and the provenance statement says so.
- Latency: public content surfaces up to 24 hours late (Sprinklr documents "Latency: Up to 24 hours", "Refresh rate: 2 to 3 hours"); the 24-hour overlap on `since` catches late posts.
- Cost: USD 0 per Graph call; the cost is quota. Calls per day at full scale and Pages per PPCA token (qualifier rule 5): to be measured in the pilot.

## 8. Failure handling and fallback

- HTTP 429 and 80001: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.fb-page-feed-poller` and an alert fires.
- HTTP 401 and 403: mark the token `degraded`, stop the batch, alert; never rotate accounts, tokens or IPs around a block.
- Empty 200 (no `data` from a Page known to post): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. No amber fallback exists for Page feeds, so `fallback_on` is never set here.
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: cursors move only after acknowledgement; a replayed job re-emits the same posts and normalize-item deduplicates them.
- Token expiry: `health = blocked`, `source.events` `updated`, ops and client notified.

## 9. Non-functional requirements

- Throughput: Facebook's share of the full-scale target is 12.0M items a month; the post share, Page count and calls per day are to be measured in the pilot.
- Latency: a post visible to Meta reaches `raw.items` within its tier interval plus fetch time.
- Idempotency: `facebook:post:<platform_id>`; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag; one leader scheduler.
- Security: tokens from Supabase Vault per job, never logged; no account pools, no proxies; Meta data never processed for law-enforcement or national-security purposes; provenance on every message; retention `meta_on_request`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `graph_error_total{code}` and `pages_in_rotation{tier}`. Alerts: `rotation_behind`, `token_degraded`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`. SLO: rotation lag below one tier interval for 99% of Pages per day.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, comment-decay-scheduler, fb-reactions-fetcher, fb-backfill, registry-writer, Supabase Postgres and Vault, Redpanda. Meta prerequisites: Business Verification, App Review for PPCA, Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- Ranked feed drops posts (about 600 a year per Page): disclosed in provenance; clients are encouraged to connect their own Pages, where webhooks are complete.
- 24-hour platform latency weakens the Tier 1 promise: worded to clients as "within 1 hour of Meta surfacing it".
- App Review takes up to several weeks: the pilot runs on client-owned Pages through fb-client-webhook-receiver until PPCA is granted.
- Field or version changes by Meta: version pinned; `schema_unknown` parks batches instead of dropping them.

## 13. Acceptance criteria

1. A Tier 1 Page whose poll started at 09:00:00 has `next_poll_at = 10:00:00` even when the fetch took 4 minutes.
2. With 100 fixture Pages across three tiers against a simulated Graph API for 24 hours, no Page's `rotation_lag_seconds` exceeds its tier interval.
3. A post with `created_time` 20 hours before the cursor, injected after the cursor advanced, is fetched on the next poll.
4. Replaying one job twice yields two `raw.items` messages with the same `idempotency_key`; normalize-item stores one item.
5. The cursor does not advance when the Redpanda produce fails; the next attempt re-emits the batch.
6. A simulated 80001 triggers backoff from 30 s to at most 15 min with `attempt + 1`; after 5 attempts the job is in `dlq.fb-page-feed-poller` and an alert fired.
7. A 401 marks the token `degraded`, stops the batch, raises `token_degraded`, and no further call uses that token.
8. Every `raw.items` message carries `route`, `vendor`, `service`, `fetched_at`, `retention_class = meta_on_request` and the seven reaction summaries.
9. A dormant Page that posts gets a `tier change` event; a Page with `backfill_status = pending` is never emitted as a rotation job; tokens never appear in logs or envelopes.

## 14. Open questions

1. Whether `since` on `/feed` filters on `created_time` or `updated_time`: to be confirmed in the pilot; if `updated_time`, edited old posts reappear and normalize-item must treat them as versions.
2. Should the push-tier reconciliation poll use the Page access token or the system-user token? Proposed: the Page token, since the data belongs to the client.
