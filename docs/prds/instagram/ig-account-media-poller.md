# ig-account-media-poller

**Platform:** Instagram · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, Instagram adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Instagram is 4.5M of the 30.5M items a month at full scale, and much of what Iraqi brands, outlets, ministries, state companies and creators say on it is posts on business and creator accounts. ig-account-media-poller is the service that reads those accounts. It uses the one green route to third-party Instagram posts: the Business Discovery field of the Instagram Graph API, called from a client's own Instagram business account and token (Facebook Login, Advanced Access).

Without it the Instagram side of the product knows only what hashtag search (ig-hashtag-search, 30 hashtags per client account per week) happens to surface and what clients' own accounts push through ig-webhook-receiver. There would be no competitor tracking, no outlet monitoring and no mention baseline, and comment-decay-scheduler would have nothing to size comment series from, because the `comments_count` it needs arrives with the posts this service finds. The freshness promise, every registered account re-checked within its tier's interval, is kept or broken here.

## 2. Objective (the end state this service delivers)

Every green Instagram business or creator account in the registry with an active tier is polled on its tier's cadence, every new post reaches `raw.items` within one tier interval of Instagram making it visible, and the cursor advances only after Redpanda has acknowledged the batch. Target: rotation lag below one tier interval for 99% of accounts per day, staleness p95 within the tier maximum (1 h, 6 h, 24 h), zero jobs lost.

## 3. Scope

### In scope

- Rotation scheduling of every green Instagram account by tier (1, 2, 3, push reconciliation, dormant) and execution of the jobs on `jobs.ig-account-media-poller`.
- Incremental reads of an account's media from the cursor, requesting `like_count` and `comments_count` with every post.
- Executing `backfill` jobs (from backfill-orchestrator) and `metrics` jobs (from comment-decay-scheduler) with the same call.
- Writing `raw.items` (kind `post`); advancing `cursors`; promoting dormant accounts; `rotation_behind` catch-up.
- Sending accounts that Business Discovery stops returning to the `review_queue`.

### Out of scope

- Comment text. Third-party comment text is not available on this route, only counts. Comments on client-owned media: ig-own-comments-fetcher. Comments on other media: ig-comments-fetcher (amber, optional).
- Hashtag media (ig-hashtag-search), mentions (ig-mentions-fetcher), live events (ig-webhook-receiver), follower and profile resolution (ig-account-resolver).
- Personal accounts (Business Discovery cannot read them; they are individuals under qualifier rule 7), age-gated accounts (not returned), Stories.
- Deduplication (normalize-item), keyword matching (keyword-matcher), tier decisions (qualifier, registry-writer), comment-series scheduling (comment-decay-scheduler).

## 4. Users and consumers

- **Clients** experience it as "new posts from the Instagram accounts I watch, never older than my tier allows"; they never call it.
- **Ops** watches rotation lag, token health, the DLQ and the review queue of accounts that stopped resolving, and can force a poll of one account.
- **Downstream services**: normalize-item (consumes `raw.items`), comment-decay-scheduler (receives new posts through `items.normalized` and reads `comments_count`), raw-archiver, source-health-canary, quota-governor, backfill-orchestrator.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.ig-account-media-poller`, partitioned by `source_id`, emitted by the rotation scheduler inside this service (one leader replica elected through a Postgres advisory lock; the scan period is an environment variable well inside the shortest tier interval of 60 minutes). The scheduler selects `sources` rows with `platform = instagram`, `source_type in (account, creator)`, `route = green`, `health != blocked`, `backfill_status in (done, capped)` and `next_poll_at <= now()`.

**Cadence by tier.** Tier 1 (100,000 or more followers, or on a client's priority list): every 60 minutes, maximum staleness 1 hour. Tier 2 (10,000 to 99,999): every 6 hours. Tier 3 (below 10,000): every 24 hours. Push (client-owned accounts on ig-webhook-receiver): no polling for new posts, one reconciliation poll every 24 hours. Dormant (no post in 30 days): weekly; a new post promotes the account back to its reach tier through `source.events` (`tier change`). Retired: never polled. Every registered account is on exactly one of these cadences, so none is left unchecked.

**Keeping every account on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + interval`), so cadence is fixed and does not drift with fetch time. Jobs are emitted ordered by `next_poll_at` then by tier, so an overdue Tier 3 account is not pushed aside by Tier 1 accounts and no account is skipped twice in a row. An account is in at most one job at a time (partition key). A failed job keeps the old `next_poll_at`, making that account the first candidate on the next scan. This route is green: tier intervals are never stretched; quota-governor can only delay a call, and the account stays first in line.

**Catch-up.** `rotation_lag_seconds` is now minus `next_poll_at` of the most overdue account. When it exceeds one interval, the scheduler switches to most-stale-first ordering and raises `rotation_behind`. Every poll reads from the cursor, so a late poll still returns everything since the cursor (subject to the depth of the media edge, to be measured in the pilot): being behind costs freshness, not completeness.

**Backfill on add.** A new account arrives with `backfill_status = pending`. backfill-orchestrator emits one `backfill` job to this service's queue; the service reads the last 90 days (or the cap, whichever is smaller) with the same call, writes the cursor and reports `done` or `capped`; backfill-orchestrator then sets `next_poll_at = now()` and the scheduler picks the account up. Messages from a backfill read carry `metrics_observation = backfill`.

**Counts refresh.** Instagram has no separate metrics service. comment-decay-scheduler emits `metrics` jobs to this queue at +24 h and +7 d after a post is first seen; the service serves them with the same call, reading back to that post's `timestamp` instead of to the cursor. Jobs for one account due in the same hour are served by one read.

**Comment decay.** Each new post flows `raw.items` → normalize-item → `items.normalized`. For posts on client-owned accounts, comment-decay-scheduler opens the ig-own-comments-fetcher series (+1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30) and uses `comments_count` to decide how many pages to budget. For posts on other accounts there is no comment text on this route; a series for ig-comments-fetcher (+6 h, +24 h, +3 d) is opened only when `IG_VENDOR_ROUTE` is on and `comments_count` is above zero.

### 5.2 Step by step

1. Consume a job (`source_id`, `kind` = rotation | reconciliation | backfill | metrics | ops_force, `attempt`); read the `sources` row and the `cursors` row for (`source_id`, `ig-account-media-poller`); stop if `health = blocked`.
2. Choose the calling account: the Instagram business account and token of the first client in `client_ids` whose token is healthy, fetched from Supabase Vault for this job only.
3. Ask quota-governor for allowance under `budget_tag = ig_graph_<ig_user_id>` (the calling account); on wait-until, requeue for that time; on deny, count `quota_denied_total` and keep `next_poll_at`.
4. Call Business Discovery for the account's handle; follow the media paging until a page holds nothing newer than the cursor (or, for `metrics` and `backfill` jobs, nothing newer than the job's stop time).
5. Write one `raw.items` message per post; raw-archiver lands the batch under `raw/green/instagram/<yyyy>/<mm>/<dd>/ig-account-media-poller/`.
6. After Redpanda acknowledges: set `cursor` to the newest `timestamp` seen, `last_success_at`, `consecutive_errors = 0`, `last_polled_at`, `next_poll_at`; emit `tier change` if a dormant account posted, and `dormant` if the newest post is more than 30 days old.
7. If the response has no `business_discovery` object, record `not_returned`; on the second consecutive occurrence put the source in `review_queue` (reasons: age-gated, converted to a personal account, renamed, deleted).
8. Record the metrics of section 10 and the usage headers Meta returns into `budgets`.

### 5.3 The call it makes

```
GET https://graph.facebook.com/v<pinned>/{ig-user-id}
  ?fields=business_discovery.username(<handle>){
            media{id,caption,media_type,permalink,timestamp,like_count,comments_count}}
  &access_token=<client's Instagram user access token, Facebook Login, Advanced Access>
```

`{ig-user-id}` is the calling client's Instagram business account; `<handle>` is the registered account's `handle`. Auth: the client's long-lived token with Instagram Public Content Access approved in App Review, injected per job. Page size and cursor syntax of the nested `media` edge: to be confirmed in the pilot. The Graph version is pinned by one environment variable shared by all Graph-based services.

### 5.4 What it gets

Per post, the fields requested above, inside `business_discovery.media.data`. Example:

```json
{
  "id": "17912345678901234",
  "caption": "افتتاح فرعنا الجديد في البصرة، بانتظاركم من الأحد",
  "media_type": "IMAGE",
  "permalink": "https://www.instagram.com/p/DAbCdEfGhIj/",
  "timestamp": "2026-10-06T07:12:09+0000",
  "like_count": 1840,
  "comments_count": 312
}
```

What it does not get: comment text or commenters (counts only); personal accounts; age-gated accounts; Stories; anything about the account itself beyond its media (followers, biography and website come from ig-account-resolver).

## 6. Inputs and outputs

### 6.1 Reads

`jobs.ig-account-media-poller`; `sources`, `cursors`, `clients` (token reference and calling account), `budgets` through quota-governor, `health` through the SDK canary hook; `source.events` (`added`, `tier change`, `retired`) to refresh its view of the rotation.

### 6.2 Writes

`raw.items`, one message per post, envelope plus the record exactly as returned:

```json
{
  "envelope": {
    "platform": "instagram", "kind": "post", "route": "green", "vendor": null,
    "service": "ig-account-media-poller",
    "source_id": "a3d94c10-5e7b-4f28-b6c1-92e0d4a7f835",
    "platform_id": "17912345678901234",
    "idempotency_key": "instagram:post:17912345678901234",
    "job_id": "01J9N3B8K2D5W7Y4T1P6Q0ZRMC", "attempt": 1,
    "fetched_at": "2026-10-06T09:31:18Z",
    "retention_class": "meta_on_request",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/instagram/2026/10/06/ig-account-media-poller/000087.jsonl.zst",
    "metrics_observation": "poll"
  },
  "payload": { "...": "the media object from 5.4, unchanged" }
}
```

Also `source.events` (`tier change`, `dormant`), `review_queue` rows, `service_runs`, and `dlq.ig-account-media-poller` after 5 failed attempts.

### 6.3 State

`cursors.cursor` = ISO `timestamp` of the newest stored post, plus `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`; `budgets` counters per calling account; in memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- Business Discovery returns business and creator accounts only; age-gated accounts are not returned; there is no comment text for third-party media. The product therefore covers the Instagram accounts that can be read this way, and says so in the provenance statement.
- Per-account call limits on the calling account: to be measured in the pilot. quota-governor keeps one counter per calling account under `ig_graph_<ig_user_id>` and returns allow, wait-until or deny. The hashtag ledger (`ig_hashtag_<ig_user_id>`, 30 unique hashtags per account per 7 days) and the 50-comments-per-query limit belong to ig-hashtag-search and ig-own-comments-fetcher and are not consumed here.
- Instagram Public Content Access allows understanding public sentiment around a brand: output to clients is aggregated and de-identified, never a list of individuals.
- Cost: USD 0 per Graph call; the cost is quota. Accounts in rotation and calls per day at full scale (Instagram's share is about 150,000 items a day): to be measured in the pilot.

## 8. Failure handling and fallback

- HTTP 429 and Meta rate-limit errors: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.ig-account-media-poller` and an alert fires. The list of Instagram error codes: to be catalogued in the pilot.
- HTTP 401 and 403: mark the token `degraded`, stop the batch, alert; never rotate accounts, tokens or IPs around a block. When no client in `client_ids` has a healthy token, `health = blocked`, `source.events` `updated`, ops and client notified.
- Empty 200 (no `business_discovery` for an account known to post): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. No amber fallback for account media is defined in the service index, so `fallback_on` is never set here.
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: cursors move only after acknowledgement; a replayed job re-emits the same posts and normalize-item deduplicates them.

## 9. Non-functional requirements

- Throughput: Instagram's share of the full-scale target is 4.5M items a month; the post share, account count and calls per day are to be measured in the pilot.
- Latency: a post visible to Instagram reaches `raw.items` within its tier interval plus fetch time.
- Idempotency: `instagram:post:<platform_id>`; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag; one leader scheduler.
- Security: tokens from Supabase Vault per job, never logged; no account pools, no proxies; Meta data never processed for law-enforcement or national-security purposes; business and creator accounts only, no individuals profiled; provenance on every message; retention `meta_on_request`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `graph_error_total{code}`, `accounts_in_rotation{tier}` and `not_returned_total`. Alerts: `rotation_behind`, `token_degraded`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`, `not_returned_spike`. SLO: rotation lag below one tier interval for 99% of accounts per day.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, comment-decay-scheduler, backfill-orchestrator, registry-writer, ig-account-resolver (keeps follower counts, and so tiers, current), ig-own-comments-fetcher and ig-comments-fetcher (consumers of its posts), Supabase Postgres and Vault, Redpanda. Meta prerequisites: Business Verification, App Review (Advanced Access and Instagram Public Content Access), Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- Coverage gap: personal and age-gated accounts cannot be read. Mitigation: coverage stated in the provenance statement; unresolved accounts reviewed, not dropped silently.
- No third-party comment text on the green route: the product shows counts; text on other media comes only from the optional amber ig-comments-fetcher, excluded from government contracts.
- Unknown per-account call limits: measured in the pilot before tier intervals are promised to clients; quota-governor delays rather than drops.
- App Review delay: the pilot runs on the company's own business account and on client-owned accounts until Instagram Public Content Access is granted.
- Renamed handles make an account unreachable by username: caught by `not_returned`, resolved through the review queue and ig-account-resolver.
- A client disconnecting its account removes the calling token: another watching client's token is used; if none, the source is blocked and the client notified.

## 13. Acceptance criteria

1. A Tier 1 account whose poll started at 09:00:00 has `next_poll_at = 10:00:00` even when the fetch took 4 minutes.
2. With 100 fixture accounts across Tier 1, 2, 3, push and dormant against a simulated Graph API for 7 simulated days, no account's `rotation_lag_seconds` exceeds its interval (1 h, 6 h, 24 h, 24 h, 7 d).
3. After the leader replica is killed mid-scan, the next leader emits the overdue jobs ordered by `next_poll_at` then tier, and no account is skipped twice in a row.
4. When lag exceeds one interval, `rotation_behind` fires and the next scan orders by most-stale-first.
5. Replaying one job twice yields two `raw.items` messages with the same `idempotency_key`; normalize-item stores one item.
6. The cursor does not advance when the Redpanda produce fails; the next attempt re-emits the batch.
7. A simulated 429 triggers backoff from 30 s to at most 15 min with `attempt + 1`; after 5 attempts the job is in `dlq.ig-account-media-poller` and an alert fired.
8. A 401 marks the token `degraded`, stops the batch, raises `token_degraded`, and no further call uses that token.
9. An account with `backfill_status = pending` is never emitted as a rotation job; a `backfill` job reads 90 days (or the cap) and the account joins the rotation only after `done` or `capped`.
10. A `metrics` job for a post 24 h old re-reads the media edge back to that post's `timestamp` and emits it again with fresh `like_count` and `comments_count`.
11. An account with no `business_discovery` object on two consecutive polls appears in `review_queue` with reason `not_returned`, and its cadence is unchanged.
12. Every `raw.items` message carries `route`, `vendor`, `service`, `fetched_at`, `retention_class = meta_on_request` and `comments_count`; tokens never appear in logs or envelopes.

## 14. Open questions

1. Page size, ordering and cursor syntax of the `media` edge nested in `business_discovery`, and how far back it can be read (this fixes the backfill cap): to be confirmed in the pilot.
2. Whether Business Discovery can be pointed at the calling client's own username. For owned accounts the webhooks (`comments`, `mentions`) do not announce new posts, so under the push rule an owned account's own posts would be found within 24 hours; proposed: clients who need hourly freshness put their account on the priority list (Tier 1).
3. Whether normalize-item records a re-emitted post as a new count observation rather than a duplicate, which the `metrics` jobs rely on: to be confirmed with its owner.
