# ig-mentions-fetcher

**Platform:** Instagram · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, Instagram adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The most valuable Instagram content for a client is often not on the client's own account or under a hashtag but on other people's accounts: a customer who tags the brand in a photo, a creator who names it in a caption, a follower who @mentions it in a comment. ig-mentions-fetcher reads exactly that, for the Instagram business accounts that clients have connected, through three official Instagram Graph API reads: `/{ig-user-id}/tags`, `mentioned_media` and `mentioned_comment`.

Without it the product would find a mention only if the author happened to be a registered account (ig-account-media-poller) or used a hashtag a client tracks (ig-hashtag-search), and would depend wholly on the live webhook (ig-webhook-receiver) for the rest. A webhook that is down for an hour, or a delivery Meta never retries, would leave a hole in the one signal clients care about most. This service is the hourly safety net that closes it.

## 2. Objective (the end state this service delivers)

Every connected client Instagram account is checked for new tags and mentions every 60 minutes, every mention reaches `raw.items` within one hour of Instagram exposing it (or sooner through the webhook, without duplicates), and each cursor advances only after Redpanda has acknowledged the batch. Target: rotation lag below 60 minutes for 99% of connected accounts per day, zero jobs lost, zero mentions found by the daily reconciliation that neither the webhook nor the hourly poll had stored, once the pilot has tuned both.

## 3. Scope

### In scope

- Hourly rotation over every connected client account (`owned_by_client = true`) and execution of jobs on `jobs.ig-mentions-fetcher`.
- Reading `/{ig-user-id}/tags`, `mentioned_media` and `mentioned_comment` since the per-edge cursors.
- The daily `reconciliation` job from ig-webhook-receiver's scheduler (a deeper read) and `backfill` jobs from backfill-orchestrator.
- Writing `raw.items` (kind `post` for tagged and mentioning media, kind `comment` for mentioning comments).

### Out of scope

- Stories mentions: the API does not support them, so they are not collected and the provenance statement says so.
- Live events (ig-webhook-receiver), the client's own media (ig-account-media-poller), comments under the client's own media (ig-own-comments-fetcher), hashtag media (ig-hashtag-search).
- The comments under a mentioning post (not read on the green route; ig-comments-fetcher is optional and amber).
- Deciding whether a mention's author becomes a source (poster-resolver, qualifier); individuals are never profiled.

## 4. Users and consumers

- **Clients** experience it as "everyone who tagged or mentioned my brand, within the hour". They never call it.
- **Ops** watches rotation lag, token health, the DLQ and the webhook-versus-poll comparison (`missed_push_total`), and can force a poll of one account.
- **Downstream services**: normalize-item, keyword-matcher and poster-resolver through `items.normalized` and the hit topics, comment-decay-scheduler, raw-archiver, source-health-canary, quota-governor, backfill-orchestrator.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.ig-mentions-fetcher`, partitioned by `source_id`, emitted by the rotation scheduler inside this service (one leader replica elected through a Postgres advisory lock; the scan period is an environment variable well inside 60 minutes). The scheduler selects `sources` rows with `platform = instagram`, `source_type in (account, creator)`, `route = green`, `owned_by_client = true`, `tier != retired`, `health != blocked`, `backfill_status in (done, capped)` and a due `next_poll_at`.

**Cadence.** The sources here are the client's own accounts, not discovered ones, so the reach tiers do not slow them: tier 1, 2 and 3 accounts are all polled every 60 minutes. Push accounts (those with webhooks on ig-webhook-receiver) are polled hourly as well, because the webhook is the fast path and this poll is its safety net; in addition one `reconciliation` job a day reads deeper (back to 24 hours before the cursor) and counts what neither path had stored. A dormant poster account is still polled hourly, because mentions arrive whether or not the account posts. Retired accounts (client offboarded or access revoked) are never polled.

**Keeping every account on rotation.** `sources.next_poll_at` belongs to ig-account-media-poller's rotation of the same row, so this service keeps its own schedule inside its `cursors` row (source × `ig-mentions-fetcher`): the cursor string holds one `since` timestamp per edge and `poll_started_at`. The next poll is `poll_started_at + 60 minutes`, set from the START of the last poll, so cadence is fixed and does not drift with fetch time. Jobs are emitted ordered by that due time then by tier, so no account is skipped twice in a row; an account is in at most one job at a time (partition key); a failed job keeps its due time and is first in line on the next scan.

**Catch-up.** `rotation_lag_seconds` is now minus the due time of the most overdue account. When it exceeds 60 minutes the scheduler orders most-stale-first and raises `rotation_behind`. Reads are incremental from the cursors, so a late poll still returns everything since them (within the depth of each edge, to be measured in the pilot).

**Backfill on add.** When a client connects an account it arrives with `backfill_status = pending`; backfill-orchestrator emits one `backfill` job, the service reads each edge back 90 days or as far as the edge goes (whichever is smaller) and reports `done` or `capped`, and the account joins the rotation. Backfill messages carry `metrics_observation = backfill`.

**Comment decay.** A mentioning post enters `items.normalized`; because it belongs to someone else's account, its comments are covered only by the optional amber ig-comments-fetcher series (+6 h, +24 h, +3 d) when `IG_VENDOR_ROUTE` is on. A `mentioned_comment` is itself a comment and needs no series.

### 5.2 Step by step

1. Consume a job (`source_id`, `kind` = rotation | reconciliation | backfill | ops_force, `attempt`); read `sources` and the `cursors` row; stop if `health = blocked`.
2. Take the owning client's token from Supabase Vault for this job only; the `ig-user-id` is the source's `platform_id`.
3. Ask quota-governor for allowance under `budget_tag = ig_graph_<ig_user_id>` for the three reads; on wait-until, requeue; on deny, count `quota_denied_total` and keep the due time.
4. Read `/tags`, `mentioned_media` and `mentioned_comment` since their cursors (for a `reconciliation` job, since cursor minus 24 hours), following pagination to the end.
5. Write one `raw.items` message per mention; raw-archiver lands the batch under `raw/green/instagram/<yyyy>/<mm>/<dd>/ig-mentions-fetcher/`.
6. After Redpanda acknowledges: advance each edge cursor to the newest `timestamp` seen, set `last_success_at`, `consecutive_errors = 0`, `last_polled_at` and the next due time.
7. For a `reconciliation` job, compare with what ig-webhook-receiver stored and add the difference to `missed_push_total`.
8. Record metrics and the usage headers Meta returns into `budgets`.

### 5.3 The call it makes

```
GET https://graph.facebook.com/v<pinned>/{ig-user-id}/tags
  ?fields=id,caption,media_type,permalink,timestamp,like_count,comments_count,username
GET https://graph.facebook.com/v<pinned>/{ig-user-id}
  ?fields=mentioned_media{...}        (how the edge is listed or addressed: to be confirmed in the pilot)
GET https://graph.facebook.com/v<pinned>/{ig-user-id}
  ?fields=mentioned_comment{...}      (how the edge is listed or addressed: to be confirmed in the pilot)
```

All three use the client's Instagram user access token (Facebook Login, Advanced Access) of the connected account, injected per job. The field lists mirror ig-account-media-poller's media fields plus the author's `username` where an edge returns it; page sizes, the cursor syntax of each edge and the permission set: to be confirmed in the pilot. The Graph version is pinned by one environment variable shared by all Graph-based services.

### 5.4 What it gets

Per tagged or mentioning media, the fields above. Example:

```json
{
  "id": "17895432167098765",
  "caption": "جربنا خدمة الإنترنت الجديدة اليوم وكانت ممتازة @client_brand",
  "media_type": "IMAGE",
  "permalink": "https://www.instagram.com/p/DAxYzWvUtSr/",
  "timestamp": "2026-10-06T11:20:33+0000",
  "like_count": 12,
  "comments_count": 1,
  "username": "demo_poster_02"
}
```

A `mentioned_comment` item carries the comment's text, id and time and the media it sits under (fields to be confirmed in the pilot). What it does not get: Stories mentions (not supported); the mentioning post's own comment text; mentions in private messages; anything about the author's profile (poster-resolver and ig-account-resolver decide whether the author is a business or creator account, else an individual with a hashed reference only).

## 6. Inputs and outputs

### 6.1 Reads

`jobs.ig-mentions-fetcher`; `sources`, `cursors`, `clients` (token reference), `budgets` through quota-governor, `health` through the SDK canary hook; `source.events` (`added`, `retired`) to refresh its view of the rotation.

### 6.2 Writes

`raw.items`, one message per mention, envelope plus the record as returned:

```json
{
  "envelope": {
    "platform": "instagram", "kind": "post", "route": "green", "vendor": null,
    "service": "ig-mentions-fetcher",
    "source_id": "e52b7a90-1c36-4d8f-a7e4-3b9c0d1f6a28",
    "platform_id": "17895432167098765",
    "idempotency_key": "instagram:post:17895432167098765",
    "job_id": "01J9N6E4Q7G9Z1B3X5T8W2MHVF", "attempt": 1,
    "fetched_at": "2026-10-06T12:00:41Z",
    "retention_class": "meta_on_request",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/instagram/2026/10/06/ig-mentions-fetcher/000058.jsonl.zst",
    "mention_type": "mentioned_media", "mention_of": "17841405822304914",
    "metrics_observation": "poll"
  },
  "payload": { "...": "the media object from 5.4, unchanged" }
}
```

`mention_type` is `tag`, `mentioned_media` or `mentioned_comment`; `mention_of` is the connected account's `ig-user-id`. `source_id` is the connected account's source, because the mention was found by reading that source. A `mentioned_comment` is written with `kind = comment` and key `instagram:comment:<id>`. Also `service_runs` and `dlq.ig-mentions-fetcher` after 5 failed attempts.

### 6.3 State

`cursors.cursor` (source × service) = a JSON string with one `since` timestamp per edge and `poll_started_at`, plus `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at` and `health`; `budgets` counters per account; in memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- Three reads per poll and 24 polls a day: 72 calls per connected account per day before paging. Per-account call limits: to be measured in the pilot, and quota-governor keeps one counter per account under `ig_graph_<ig_user_id>`.
- Stories mentions are not supported by the API. Mentions are available for client accounts only, so the service reads nothing about accounts a client has not connected.
- The 30-unique-hashtag limit per business account per 7 days belongs to ig-hashtag-search; the 50-comments-per-query limit to ig-own-comments-fetcher; Business Discovery (business and creator accounts only, age-gated accounts not returned) to ig-account-media-poller and ig-account-resolver. None is consumed here.
- Under Instagram Public Content Access, analytics leave the platform only as aggregated, de-identified output; mention authors are never listed to clients.
- Cost: USD 0 per Graph call; the cost is quota. Connected accounts and calls per day at full scale (inside Instagram's 4.5M items a month): to be measured in the pilot.

## 8. Failure handling and fallback

- HTTP 429 and Meta rate-limit errors: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.ig-mentions-fetcher` and an alert fires.
- HTTP 401 and 403: mark the token `degraded`, stop the batch, alert; never rotate accounts, tokens or IPs around a block; a revoked token sets `health = blocked`, emits `source.events` `updated`, and notifies ops and the client.
- Empty 200 (no `data` where mentions are expected): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. No fallback exists, so `fallback_on` is never set here.
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: each edge's cursor moves only after acknowledgement; a replayed job re-emits the same mentions and normalize-item deduplicates them.
- A mention whose media was deleted between listing and reading is skipped and counted, not retried forever.

## 9. Non-functional requirements

- Throughput: Instagram's share of the full-scale target is 4.5M items a month; the mention share is to be measured in the pilot.
- Latency: a mention exposed by Instagram reaches `raw.items` within 60 minutes plus fetch time, or live through ig-webhook-receiver.
- Idempotency: `instagram:post:<platform_id>` and `instagram:comment:<platform_id>`, the same keys the webhook and the other Instagram services use, so a mention seen twice is stored once; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag; one leader scheduler.
- Security: tokens from Supabase Vault per job, never logged; no account pools, no proxies; Meta data never processed for law-enforcement or national-security purposes; mention authors keep only a hashed reference unless they are business or creator accounts; provenance on every message; retention `meta_on_request`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `graph_error_total{code}`, `accounts_in_rotation`, `mentions_new_total{mention_type}` and `missed_push_total`. Alerts: `rotation_behind`, `token_degraded`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`, `missed_push_rising`. SLO: rotation lag below 60 minutes for 99% of accounts per day.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, backfill-orchestrator, ig-webhook-receiver (live path and daily reconciliation jobs), ig-account-media-poller (shares the account rows), poster-resolver and qualifier (downstream), registry-writer, Supabase Postgres and Vault, Redpanda. Meta prerequisites: Business Verification, App Review (Advanced Access), Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- `mentioned_media` and `mentioned_comment` may be readable only for ids a webhook supplies: open question 1; the design then reads ids ig-webhook-receiver could not resolve, and `/tags` stays fully polled.
- Webhook and poll both deliver one mention: identical idempotency keys make that harmless; whether mention media ids equal the ids other routes use is checked in the pilot.
- Stories mentions are invisible: disclosed in the provenance statement.
- Per-account limits too tight for hourly reads: measured first; the fallback is a longer interval for Tier 3 accounts, decided with Abdullah.
- Authors of mentions are mostly individuals: no profile is built; only a hashed reference survives unless the author is a business or creator account.

## 13. Acceptance criteria

1. A connected account whose poll started at 09:00:00 is next due at 10:00:00 even when the three reads took 4 minutes.
2. With 100 fixture accounts across Tier 1, 2, 3, push and dormant against a simulated Graph API for 24 hours, every account is polled every 60 minutes and no `rotation_lag_seconds` exceeds 3,600.
3. A retired account is never emitted as a job; a dormant poster account is still polled hourly.
4. When lag exceeds 60 minutes, `rotation_behind` fires and the next scan orders most-stale-first.
5. A mention delivered first by the webhook and then by this service yields two `raw.items` messages with the same `idempotency_key`; normalize-item stores one item.
6. An edge cursor does not advance when the Redpanda produce fails; the next attempt re-emits the batch.
7. A `reconciliation` job reads back to 24 hours before the cursor and adds a mention that neither path had stored to `missed_push_total`.
8. A `backfill` job reads each edge back 90 days or as far as it goes, sets `capped` when it ends earlier, and the account joins the rotation only afterwards.
9. A `mentioned_comment` is written with `kind = comment`; a tagged media with `kind = post`; both carry `mention_type` and `mention_of`.
10. A simulated 429 triggers backoff from 30 s to at most 15 min; after 5 attempts the job is in `dlq.ig-mentions-fetcher` and an alert fired.
11. A 401 marks the token `degraded`, stops the batch, raises `token_degraded`, and no further call uses that token.
12. Every message carries `route`, `vendor`, `service`, `fetched_at` and `retention_class = meta_on_request`; tokens never appear in logs or envelopes; no Stories item is ever written.

## 14. Open questions

1. Whether `mentioned_media` and `mentioned_comment` can be listed or are read only by an id supplied in a webhook event; this decides whether the hourly poll covers them or only `/tags`: to be confirmed in the pilot.
2. Page sizes, cursor syntax and depth of each edge, and so the real backfill cap and the reconciliation window.
3. Whether the ids returned here equal the ids from Business Discovery and the webhook, which the deduplication relies on.
4. Proposed: hourly for every connected account until the per-account limits are measured; Tier 3 relief only if they force it.
