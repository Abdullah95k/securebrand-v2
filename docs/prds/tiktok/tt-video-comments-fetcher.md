# tt-video-comments-fetcher

**Platform:** TikTok · **Route:** amber (optional, flag `TT_VENDOR_ROUTE`) · **Lane:** Comments · **Owner:** Ingestion lead (Node) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

On TikTok the reaction to a video lives in its comments: the complaint under a telecom offer, the praise under a ministry announcement, the argument under an outlet's clip. Comments are expected to be the larger share of the 7.5M TikTok items a month at full scale (the split is to be measured in the pilot). tt-video-comments-fetcher reads the comments and replies under the videos that tt-profile-videos-poller, tt-keyword-search and tt-hashtag-feed-poller find, on the schedule comment-decay-scheduler sets.

Plainly: TikTok has no green route to third-party content. Research Tools are academic and non-profit only, the Commercial Content API covers EU paid ads, and the Mentions API is for badged Marketing Partners. So this service is optional, runs only behind `TT_VENDOR_ROUTE` (off | tikhub | ensembledata), is disclosed in the provenance statement to clients, and is excluded from government contracts. Without it the product knows how many comments a TikTok video has (from the counts) but not what they say: no sentiment, no campaign reaction, no early warning on a video that turns into a complaint thread. The Display API has no comments endpoint, so even a client's own videos get no comments from the green route.

## 2. Objective (the end state this service delivers)

Every comment series that comment-decay-scheduler opens for a TikTok video runs to its end, every new comment and reply reaches `raw.items` with the commenter held only as a hash, and nothing identifying a commenter ever enters Redpanda, the raw archive or ClickHouse. Target: 95% of series completed on time, zero commenter handles in any store, zero jobs lost.

## 3. Scope

### In scope

- Executing `comments` and `replies` jobs from `jobs.tt-video-comments-fetcher` for videos of registered creators and for videos found by search.
- Paging until already-stored comments are reached; edit and deletion detection by content hash; replies for comments with more than 10 replies.
- Replacing commenter identity with `author_hash` before the first write; writing `raw.items` (kind `comment`); reporting `new_count`, `seen_count`, `pages`, `cost_units` to comment-decay-scheduler.
- TikHub and EnsembleData adapters behind the flag, with vendor fallback.

### Out of scope

- Deciding which videos get a series, when, and what extra fetches run (comment-decay-scheduler).
- Finding videos (tt-profile-videos-poller, tt-keyword-search, tt-hashtag-feed-poller) and refreshing counts (tt-video-stats-refresher).
- Commenter profiles, follower counts or histories: never fetched (TikTok's Developer Terms forbid building profiles or databases on any individual).
- Sentiment and topics (analysis-sentiment, analysis-topics); deduplication (normalize-item).

## 4. Users and consumers

- **Clients** see "what people say under the videos I watch", with the amber label; they never see a commenter handle.
- **Ops** watches series completion, vendor health and spend, and can force a refresh of one video.
- **Downstream:** normalize-item, comment-decay-scheduler (reads the completion message and applies the series rules), analysis-sentiment, raw-archiver, source-health-canary, quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Jobs on `jobs.tt-video-comments-fetcher`, partitioned by `source_id`, emitted only by comment-decay-scheduler; this service has no scheduler of its own. A job carries `job_id`, `source_id`, `kind` (comments or replies), `due_at`, `attempt`, `post_ref` (`tiktok:video:<id>`, or the parent comment's key for replies) and `series_step`.

**Series.** From the moment a video is first seen: +1 h, +6 h, +24 h, +3 d, +7 d. There is no weekly tail on TikTok: the series ends at +7 d unless extended.
- **Early stop.** When a fetch adds fewer than 5% new comments (against the comments already stored) and fewer than 5 in absolute terms, the remaining steps are cancelled.
- **Extension.** When the +7 d fetch still adds 20% or more new comments, the series continues every 2 days until day 30.
- **Hot posts.** When velocity exceeds 100 new comments an hour, comment-decay-scheduler inserts an hourly fetch for the next 6 hours. At 80% of the monthly budget quota-governor drops these extra fetches first.
- **Replies.** The completion message lists comments reported with more than 10 replies; comment-decay-scheduler emits a `replies` job for each one whose reply count has grown since the last replies read.
- **Beyond day 30** nothing runs automatically; a client may request a refresh of one video, budget permitting.

**Which videos.** Every new video of a registered creator, and the videos found by search that comment-decay-scheduler selects (proposed: those with an `item.hits` or `discovery.hits` match, or from a client's priority hashtag).

**Paging.** Each fetch reads newest first and stops at the first page containing a comment already stored, or when the vendor's cursor ends, or at the page ceiling (an environment variable, value set in the pilot). A fetch that runs late still reads everything since the watermark: lateness costs freshness, not completeness. Overdue jobs are taken most-overdue-first by `due_at`, and `rotation_behind` fires when the oldest job is more than one series step late.

### 5.2 Step by step

1. Consume a job; read the video's state (watermark: newest stored `create_time` and stored count). Refuse and count `gov_excluded` if the video belongs only to government-contract sources.
2. Read `TT_VENDOR_ROUTE` and route health: use the flag's vendor, or the alternate vendor with a row in `vendor_keys` while `fallback_on` is in force. Flag off: count `flag_off`, return the job as `skipped_flag_off` so the series is not marked failed.
3. Ask quota-governor for allowance under `budget_tag = tt_vendor` (sub-counter `video_comments`); `wait-until` requeues, `deny` requeues with `attempt + 1`.
4. Call the comments endpoint (or replies for a `replies` job), 20 items a page, and page as described in 5.1.
5. For each comment: replace the commenter's identity with `author_hash`; compute the content hash of the text; look up the stored hash for that comment id; a changed hash is written as a new version, an unchanged one counts as seen.
6. Write one `raw.items` message per new or changed comment; raw-archiver lands the batch.
7. After Redpanda acknowledges: advance the watermark; send the completion message (`new_count`, `seen_count`, `pages`, `cost_units`, comments above the reply threshold) to comment-decay-scheduler; write `service_runs`.

### 5.3 The call it makes

TikHub, endpoint families **comments** (by video id) and **replies** (by video id and parent comment id). Exact paths and parameter names, including whether a newest-first ordering exists: to be confirmed in the pilot. EnsembleData: the equivalent comment and reply endpoints behind the flag value `ensembledata`. Common limits: 20 items a page, 10 requests a second per endpoint, TikHub billed on HTTP 200 only. Auth: the vendor key from Supabase Vault (`vendor_keys`), per job. The video id is the last segment of `post_ref`.

**Commenter identity.** `author_hash` is a keyed hash (HMAC-SHA-256, key from Supabase Vault, the same function every platform uses) of the vendor's user id, not the handle, which people change. User id, handle, nickname and avatar fields are dropped in the adapter, before the first write. This is the one place where `raw.items` is not byte for byte what the vendor returned, by design: no handle ever reaches the archive. A commenter who is a registered source (for example the creator answering under their own video) also gets `author_source_id`.

### 5.4 What it gets

Per comment, as written (illustrative; field names to be confirmed in the pilot):

```json
{
  "cid": "7421601187764085510",
  "video_id": "7421538806219533573",
  "text": "الله يعطيكم العافية، متى يوصل التوصيل لبغداد؟",
  "create_time": 1759738315,
  "digg_count": 14,
  "reply_comment_total": 3,
  "author_hash": "hmac256:9f2c41e7b0a3d58c",
  "author_source_id": null
}
```

Not obtained: the commenter's identity, profile or history; comments TikTok hides or filters from the vendor's view; likers. `@mentions` inside the text stay as text and are not resolved or followed.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.tt-video-comments-fetcher`; the service's own `tt_comment_state` table; ClickHouse `comments` (read-only, stored content hashes for the ids on a page); `sources` (registered creators, for `author_source_id`), `clients` (government flag), `vendor_keys`, route health, `budgets` through quota-governor; the flag `TT_VENDOR_ROUTE`.

### 6.2 Writes

`raw.items`, one message per new or changed comment or reply:

```json
{
  "envelope": {
    "platform": "tiktok", "kind": "comment", "route": "amber", "vendor": "tikhub",
    "service": "tt-video-comments-fetcher",
    "source_id": "3d8a51c2-7e04-4b9f-8c16-2a9e5d70f4b8",
    "platform_id": "7421601187764085510",
    "idempotency_key": "tiktok:comment:7421601187764085510",
    "post_ref": "tiktok:video:7421538806219533573", "parent_id": null,
    "series_step": "+6h", "version": 1,
    "job_id": "01J9N4C2M7X0B8E5V1Q3S6TKHD", "attempt": 1,
    "fetched_at": "2026-10-06T15:20:08Z",
    "retention_class": "vendor_agreed",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/amber/tiktok/2026/10/06/tt-video-comments-fetcher/000212.jsonl.zst"
  },
  "payload": { "...": "the comment object from 5.4" }
}
```

Replies use the same shape with `parent_id` set to the parent comment's id. Also `deletions` (reason `platform_sync`), the completion message to comment-decay-scheduler, `service_runs`, `dlq.tt-video-comments-fetcher` after 5 failed attempts.

### 6.3 State

`tt_comment_state` (one row per video): newest stored `create_time`, stored count, last fetch time, last reply-count per parent comment; written only after acknowledgement. `budgets` counters under `tt_vendor`; in memory only backoff state.

## 7. Limits, quotas and cost

- Price: TikHub USD 0.50 to 1.00 per 1,000 requests by daily volume tier; EnsembleData at the team's contract price. 20 comments a page means 1,000 new comments cost at least 50 requests, USD 0.025 to 0.050.
- Floor for the route: 7.5M TikTok items a month at 20 items a page is at least 375,000 requests, USD 188 to 375; the estimate of about USD 280 to 560 a month for discovery plus comments at full scale (about 560,000 requests) covers partial pages, the extra page that reaches a stored comment, replies and discovery. This service's share: to be measured in the pilot.
- A hot post costs at least 6 extra fetches on top of its series; replies add one request per page per busy thread.
- Budget tag `tt_vendor` (amber), sub-counter `video_comments`; at 80% of the monthly budget the governor drops hot-post extra fetches first.

## 8. Failure handling and fallback

- HTTP 429 and vendor rate-limit responses: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.tt-video-comments-fetcher` and an alert fires.
- HTTP 401 and 403: mark the vendor key and route `degraded`, stop, alert; never rotate accounts or IPs.
- Empty 200 on a video whose stored count says it has comments: counted per route; above 5% in 15 minutes source-health-canary flips the route to `degraded` and, with the flag on, `fallback_on`. A video with no comments is distinguished by the vendor's own total or status and is not counted.
- Video removed or private: the job returns `video_gone`, the series is cancelled; tt-video-stats-refresher owns the video's deletion record.
- Deletions: a stored comment inside the time range covered by a full read (cursor exhausted, ceiling not hit) that is absent becomes a `deletions` message only after two consecutive full reads miss it (initial value, to be tuned in the pilot); partial reads infer nothing.
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: the watermark moves only after acknowledgement; a replayed job re-emits the same comments and normalize-item deduplicates.

## 9. Non-functional requirements

- Throughput: TikTok's full-scale share is 7.5M items a month; the comment share and pages per fetch are to be measured in the pilot.
- Latency: a comment visible to the vendor reaches `raw.items` within its series step plus fetch time.
- Idempotency: `tiktok:comment:<cid>` (replies are comments with `parent_id`); an edit is a new `version` under the same key; append-only `raw.items`.
- Scaling: stateless workers on partition lag; one video's jobs never run in parallel.
- Security: keys and the hash key from Supabase Vault, never logged; no account pools, no proxies; no commenter handle stored anywhere; provenance on every message; retention `vendor_agreed`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `series_on_time_ratio`, `pages_per_fetch`, `hot_posts_active`, `replies_jobs_total`, `deletions_inferred_total` and `commenter_identity_leak_total`, which must stay zero. Alerts: `rotation_behind`, `vendor_degraded`, `dlq_nonempty`, `empty_200_rate`, `quota_deny_rate`, any non-zero `commenter_identity_leak_total`. SLO: series completed on time for 95% of videos.

## 11. Dependencies

listening-sdk, comment-decay-scheduler, quota-governor, source-health-canary, raw-archiver, normalize-item, tt-profile-videos-poller, tt-keyword-search, tt-hashtag-feed-poller, tt-video-stats-refresher, analysis-sentiment, Supabase Postgres and Vault, ClickHouse (read-only), Redpanda, TikHub and EnsembleData contracts.

## 12. Risks and mitigations

- Vendor comment lists may be relevance-ranked or incomplete: the page ceiling bounds cost, deletions are inferred conservatively, and provenance says the list is not guaranteed complete.
- A hot post can consume the budget: hourly extras are dropped first at 80%, and the sub-counter stops comments starving the pollers.
- Personal data: only hashes leave the adapter; the key sits in Vault; the leak counter and a CI check guard the payload.
- TikHub's ownership is only weakly cleared: contract review before the pilot; EnsembleData as the ready alternate.

## 13. Acceptance criteria

1. Against a simulated vendor, a video first seen at 10:00 gets fetches at 11:00, 16:00, 10:00 next day, +3 d and +7 d; no TikTok series has a weekly step.
2. A fetch that adds 2 comments to 100 stored (2%, fewer than 5) cancels the remaining steps; one that adds 4 to 20 stored (20%) does not.
3. A +7 d fetch adding 20% or more new comments leads to a fetch every 2 days until day 30.
4. Velocity above 100 new comments an hour yields an hourly fetch for the next 6 hours; at 80% of the monthly budget those extra fetches are dropped first.
5. Paging stops at the first page that holds a stored comment, and never exceeds the page ceiling.
6. No message in `raw.items`, the archive or ClickHouse contains a commenter handle, nickname, avatar or user id; every comment has `author_hash`.
7. A comment whose text changes between fetches is written once more with `version = 2` under the same `idempotency_key`; a comment absent from one full read is not deleted, absent from two it becomes a `deletions` message with reason `platform_sync`.
8. A comment reported with 11 replies leads to a `replies` job; one with 10 does not.
9. Replaying one job twice yields the same `idempotency_key`s; normalize-item stores each comment once, and the watermark does not advance when the Redpanda produce fails.
10. With `TT_VENDOR_ROUTE = off`, no vendor call is made and jobs are returned as `skipped_flag_off`; switching between `tikhub` and `ensembledata` mid-series loses no comment.
11. After 5 simulated 429s a job is in `dlq.tt-video-comments-fetcher` with an alert; a 401 marks the route `degraded` and stops the batch.

## 14. Open questions

1. Does the vendor return comments newest-first, and does it expose a sort parameter? If it ranks by relevance, the stop rule changes to paging to the end under the page ceiling: to be confirmed in the pilot.
2. Should per-video comment state live in a shared `comment_state` table used by all comment fetchers instead of `tt_comment_state`?
3. Which found videos get a series? Proposed: only those with a keyword hit or from a client's priority hashtag, to bound spend.
4. Does normalize-item accept a pre-computed `author_hash` and never expect a handle? To be agreed before the pilot.
