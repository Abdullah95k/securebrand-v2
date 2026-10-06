# ig-own-comments-fetcher

**Platform:** Instagram · **Route:** green · **Lane:** Comments · **Owner:** Backend lead, Instagram adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

For a brand or a ministry, the comments under its own Instagram posts are where complaints, questions, praise and rumors show up first, long after the post itself is forgotten. ig-own-comments-fetcher reads those comments on media of Instagram accounts that a client owns and has connected, through the official Instagram Graph API: the one green route to comment text on Instagram.

Without it the product sees how many comments a post has (`comments_count` from ig-account-media-poller) but not what people said, and a client's own account would be the one place where the platform could show us the text and we did not read it. Sentiment, topics, keyword hits and alerts on Instagram comments for client-owned accounts all start here. Comments on media the client does not own are a different, optional and amber service (ig-comments-fetcher), excluded from government contracts.

## 2. Objective (the end state this service delivers)

Every post on a client-owned Instagram account has its comments, and the replies under them, re-read on the green series (+1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30), so that every comment and reply reaches `raw.items` and every edit or deletion is reflected. Target: comment series completed on time for 95% of posts, zero jobs lost, no comment missed by a fetch that stops at the first stored comment.

## 3. Scope

### In scope

- Executing comment jobs (kinds `comments`, `replies`, `reconciliation`, `ops_force`) for client-owned media, one post and one series step per job.
- Reading top-level comments and, by field expansion, their replies; paging until already-stored comments are reached; reporting `new_count`, `seen_count`, `pages`, `cost_units` for the early-stop, extension and hot-post rules.
- Detecting edits and deletions by content hash and writing versions to `raw.items` and removals to `deletions`.
- Writing `raw.items` (kind `comment`, replies with `parent_id`).

### Out of scope

- Scheduling: the series, early stop, extension and hot-post insertion are decided by comment-decay-scheduler; this service executes and reports.
- Comments on media the client does not own (ig-comments-fetcher, amber); third-party comment text is not available on any green route.
- Posts and their counts (ig-account-media-poller), live comment events (ig-webhook-receiver), mentions (ig-mentions-fetcher).
- Deduplication, hashing of authors and language detection (normalize-item); sentiment and topics (analysis services).

## 4. Users and consumers

- **Clients** experience it as "what people say under my own posts, within hours". They never call it.
- **Ops** watches series lateness, token health and the DLQ, and can force a refresh of one post.
- **Downstream services**: normalize-item (consumes `raw.items`), keyword-matcher and the analysis services through `items.normalized`, comment-decay-scheduler (reads each job's result), deletion-propagator (consumes `deletions`), raw-archiver, source-health-canary, quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.ig-own-comments-fetcher`, partitioned by `source_id` (the owning account), so one account is never worked twice at once. A job names one post (`post_ref` = media id) and one `series_step`. Comment and reply jobs are emitted only by comment-decay-scheduler, from the moment ig-account-media-poller (or ig-webhook-receiver) first shows it a post on an owned account; this service has no scheduler of its own for comments. `reconciliation` jobs are emitted once a day per owned account by ig-webhook-receiver's scheduler and cover media still inside the first 7 days of their series; comments found there that were never pushed are counted as `missed_push_total`.

**The series (green, Instagram client media).** Counted from the moment the post is first seen: +1 h, +6 h, +24 h, +3 d, +7 d, then weekly (+14 d, +21 d, +28 d) until day 30. Beyond day 30 nothing runs automatically; a client or ops can request a refresh of one post (`ops_force`), budget permitting.

**Early stop.** When a fetch adds fewer than 5% new comments (new share = `new_count` over the comments stored before the fetch) and fewer than 5 in absolute terms, comment-decay-scheduler cancels the rest of the series. **Extension.** When the day-7 fetch still adds 20% or more, the series continues every 2 days until day 30. **Hot posts.** When velocity (new comments since the previous fetch, per hour) exceeds 100, an extra fetch is inserted every hour for the next 6 hours; on this green route these extras are deferred, never dropped, if quota-governor delays them.

**Paging and completeness.** Each fetch reads pages of 50 newest first (order to be confirmed in the pilot) and stops at the first comment already stored; a fetch that ends because the pagination is exhausted is a complete listing. The +7 d fetch and the last fetch of every series are full sweeps (read until exhausted). Only a full sweep may infer deletions.

**Edits and deletions.** Each comment's `content_hash` is the SHA-256 of its `text`. Same id with a different hash is written as a new version; a stored comment missing from a full sweep becomes a `deletions` message with reason `platform_sync`. Changes in `like_count` alone are not versions.

**Replies.** They arrive with the same call, nested under their comment, and are split into one message per reply with `parent_id` = the comment id. When a comment's nested replies are incomplete, the job result lists that comment so comment-decay-scheduler can emit a `replies` job for this service; the nested page size and cursor syntax: to be confirmed in the pilot.

**Keeping every post on its series.** A failed job returns to the queue with `attempt + 1` and keeps its `due_at`; jobs are served ordered by `due_at`, so late jobs run most-overdue-first and a post is never skipped twice in a row. A job that starts after the next step of its own series is due counts as late and raises `series_behind` when the late share threatens the 95% target.

### 5.2 Step by step

1. Consume a job (`source_id`, `post_ref`, `kind`, `series_step`, `attempt`); stop if `health = blocked` or the series was cancelled.
2. Take the owning client's token from Supabase Vault for this job only (`owned_by_client = true`).
3. Ask quota-governor for allowance under `budget_tag = ig_graph_<ig_user_id>` for the pages expected (from `comments_count` and the stored count); on wait-until, requeue; on deny, count `quota_denied_total` and keep `due_at`.
4. Load the stored comment ids and content hashes of the post from ClickHouse `comments` (read-only).
5. Call the comments edge; follow `paging.next` until a stored comment is reached (or exhaustion, on a full sweep).
6. For every comment and reply: unseen id, write to `raw.items`; known id with a different hash, write a new version; known id with the same hash, nothing.
7. On a full sweep, write `deletions` for stored comments absent from the listing.
8. After Redpanda acknowledges, record the job result (`new_count`, `seen_count`, `pages`, `cost_units`, incomplete reply threads) through the control-plane client, set `last_success_at`, `consecutive_errors = 0`.
9. Record metrics and the usage headers Meta returns into `budgets`.

### 5.3 The call it makes

```
GET https://graph.facebook.com/v<pinned>/{media-id}/comments
  ?fields=id,text,username,timestamp,like_count,
          replies{id,text,username,timestamp,like_count}
  &limit=50
  &access_token=<owning client's Instagram user access token>
```

Pagination: cursor-based, follow `paging.next`; page size 50 per query. Replies come by field expansion on the same call. Auth: the client's token (Facebook Login, Advanced Access) with the comment permissions granted at onboarding; the exact permission list: to be confirmed in the pilot.

### 5.4 What it gets

Per comment, the fields above; each reply has the same five fields. Example:

```json
{
  "id": "17858893269123456",
  "text": "الخدمة ممتازة، شكراً لكم",
  "username": "demo_commenter_01",
  "timestamp": "2026-10-06T07:58:44+0000",
  "like_count": 3,
  "replies": {"data": [
    {"id": "17841112223334445", "text": "شكراً لتواصلكم", "username": "brand_account",
     "timestamp": "2026-10-06T08:20:10+0000", "like_count": 1}
  ]}
}
```

What it does not get: comments on media the client does not own; profiles of commenters; comments Instagram hides or removes (they simply vanish from a full sweep); an edit history (versions come from our own hashing).

## 6. Inputs and outputs

### 6.1 Reads

`jobs.ig-own-comments-fetcher`; `sources`, `cursors`, `clients` (token reference), `budgets` through quota-governor, `health` through the SDK canary hook; ClickHouse `comments` (stored ids and hashes of one post, read-only).

### 6.2 Writes

`raw.items`, one message per comment and per reply:

```json
{
  "envelope": {
    "platform": "instagram", "kind": "comment", "route": "green", "vendor": null,
    "service": "ig-own-comments-fetcher",
    "source_id": "a3d94c10-5e7b-4f28-b6c1-92e0d4a7f835",
    "platform_id": "17858893269123456",
    "idempotency_key": "instagram:comment:17858893269123456",
    "job_id": "01J9N4C6M3E8X2Z5V7R1T9HQAD", "attempt": 1,
    "fetched_at": "2026-10-06T10:31:05Z",
    "retention_class": "meta_on_request",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/instagram/2026/10/06/ig-own-comments-fetcher/000214.jsonl.zst",
    "post_ref": "17912345678901234", "parent_id": null, "series_step": "+1h",
    "content_hash": "sha256:5d3b1e9a07c24f86b2a1c9d0e47f3a68b15c2d9e8f0a7b4c63d1e2f9a8b7c6d5"
  },
  "payload": { "...": "the comment object from 5.4 without its nested replies, which are separate messages" }
}
```

Also `deletions` (reason `platform_sync`), the job result for comment-decay-scheduler, `service_runs`, and `dlq.ig-own-comments-fetcher` after 5 failed attempts.

### 6.3 State

No per-post state of its own: what is already stored is read from ClickHouse. `cursors` (source × service) holds `last_success_at`, `last_error`, `consecutive_errors`; `budgets` counters per owning account; in memory only backoff state.

## 7. Limits, quotas and cost

- 50 comments per query: a full read of a post with N comments costs about N / 50 calls (rounded up), plus the nested replies. Per-account call limits: to be measured in the pilot. Budget tag `ig_graph_<ig_user_id>`, one counter per owning account.
- This route reads client-owned media only. Business Discovery (business and creator accounts only, age-gated accounts not returned) gives no third-party comment text, and the 30-unique-hashtag limit per business account per 7 days belongs to ig-hashtag-search.
- Under Instagram Public Content Access, analytics leave the platform only as aggregated, de-identified output: usernames stay in the raw payload and downstream items carry a hashed author reference.
- Cost: USD 0 per Graph call; the cost is quota. Comment volume at full scale (inside Instagram's 4.5M items a month): to be measured in the pilot.

## 8. Failure handling and fallback

- HTTP 429 and Meta rate-limit errors: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.ig-own-comments-fetcher` and an alert fires.
- HTTP 401 and 403: mark the token `degraded`, stop the batch, alert; never rotate accounts, tokens or IPs around a block; a disconnected client's series are cancelled and ops notified.
- Empty 200 (no `data` for a post whose `comments_count` is above zero): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. No fallback exists for owned media: ig-comments-fetcher is third-party only, so `fallback_on` is never set here.
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: results and cursors move only after acknowledgement; a replayed job re-emits the same comments and normalize-item deduplicates by key.
- A deleted post: the edge errors; the series is cancelled and the post is left to ig-account-media-poller's next read.

## 9. Non-functional requirements

- Throughput: comments are the bulk of Instagram's share of the full-scale target (4.5M items a month together with posts and hashtag media); the split is to be measured in the pilot.
- Latency: a comment visible to Instagram reaches `raw.items` at the next series step plus fetch time, or live through ig-webhook-receiver.
- Idempotency: `instagram:comment:<platform_id>`; replayable jobs; append-only `raw.items`; versions keyed by `content_hash`.
- Scaling: stateless workers on partition lag; no leader needed.
- Security: tokens from Supabase Vault per job, never logged; no account pools, no proxies; Meta data never processed for law-enforcement or national-security purposes; no profile of any commenter is built; retention `meta_on_request`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `comments_new_total`, `replies_new_total`, `versions_total`, `deletions_total`, `pages_per_job`, `series_late_total` and `missed_push_total`. Alerts: `series_behind`, `token_degraded`, `dlq_nonempty`, `empty_200_rate`, `quota_deny_rate`. SLO: comment series completed on time for 95% of posts.

## 11. Dependencies

listening-sdk, comment-decay-scheduler, ig-account-media-poller, ig-webhook-receiver, quota-governor, source-health-canary, raw-archiver, normalize-item, deletion-propagator, Supabase Postgres and Vault, ClickHouse (read-only), Redpanda. Meta prerequisites: Business Verification, App Review (Advanced Access), Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- The series starts when a post is first seen, which for an owned account on the push tier can be up to 24 hours after publication: ig-webhook-receiver delivers live comments in the meantime; open question 2.
- ClickHouse lag makes a fetch re-read comments it has just written: harmless because keys are idempotent, only calls are wasted.
- Viral posts exhaust the per-account call allowance: the hot-post rule is deferred, never dropped, and ops are alerted through `quota_deny_rate`.
- Nested replies are cut off: the job result flags the thread and a `replies` job completes it.
- Client revokes access: series cancelled; data kept only as `meta_on_request` allows.

## 13. Acceptance criteria

1. With 130 comments stored and 20 new, a fetch reads one page of 50, stops at the first stored id, and reports `new_count = 20`, `pages = 1`.
2. With 0 stored and 120 comments on the post, the fetch reads 3 pages until exhaustion and reports `new_count = 120`.
3. A fetch that adds 2 new comments to 100 stored is reported as under 5% and under 5 absolute, and the remaining series is cancelled.
4. A day-7 fetch that adds 25% new comments leads to a fetch every 2 days until day 30.
5. A post with 150 new comments in one hour gets a fetch every hour for the next 6 hours.
6. A comment with two nested replies yields three messages; each reply has `parent_id` = the comment id and the same `post_ref`.
7. A comment whose `text` changed yields a new version with a different `content_hash` and the same id; a change in `like_count` alone yields none.
8. On a full sweep, a stored comment absent from the listing yields one `deletions` message with reason `platform_sync`; on a non-full fetch no deletion is inferred.
9. Replaying one job twice yields messages with identical `idempotency_key`s; normalize-item stores one item per comment.
10. The job result is not recorded when the Redpanda produce fails; the next attempt re-emits the batch.
11. A 429 triggers backoff from 30 s to at most 15 min; after 5 attempts the job is in `dlq.ig-own-comments-fetcher` and an alert fired. A 401 marks the token `degraded`, stops the batch and no further call uses it.
12. Every message carries `route`, `vendor`, `service`, `fetched_at`, `retention_class = meta_on_request`, `post_ref` and `content_hash`; tokens never appear in logs or envelopes.

## 14. Open questions

1. Order of the comments edge, and the nested replies page size and cursor syntax: to be confirmed in the pilot.
2. Should the series be counted from the media's own `timestamp` when first-seen lags it by more than 1 hour? Proposed: yes, a decision for comment-decay-scheduler.
3. Whether Instagram allows comment text to be edited; the hash mechanism is built either way.
