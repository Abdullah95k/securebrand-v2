# yt-comments-fetcher

**Platform:** YouTube · **Route:** green · **Lane:** Comments · **Owner:** Backend lead, YouTube adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Under an Iraqi video, the comments are where viewers answer a brand, an outlet or a ministry in their own words: a complaint about a price, praise for a service, anger at an announcement. YouTube carries 3.0M of the product's 30.5M items a month at full scale, most of them comments (exact split to be measured in the pilot). yt-comments-fetcher reads those comments through the official YouTube Data API and keeps each video's comments current through its first month.

Without it, YouTube in the product is a list of titles and view counts: no sentiment, no topics, no answer to "what are people saying about our ad", nothing for yt-replies-fetcher to deepen, and no record of which comments were edited or removed. It is also where two YouTube rules are applied first: commenters enter the system only as hashed references, and every comment is labeled for the 30-day text limit.

## 2. Objective (the end state this service delivers)

Every video in an open comment series has each step fetched when due; every public top-level comment and embedded reply that YouTube lists reaches `raw.items` by the next step; edits arrive as new versions; comments removed on YouTube reach `deletions`; comment-decay-scheduler receives an exact report for every job. Target: 95% of videos complete their series on time (each step finished before the next falls due, the +30 d step within 24 hours of falling due), zero jobs lost, zero API calls without a quota-governor allowance, zero messages carrying a commenter id in clear.

## 3. Scope

### In scope

- Executing `comments` jobs from `jobs.yt-comments-fetcher`: series steps, extensions, hot-post extras, client refreshes.
- Paging `commentThreads.list` newest first with the stop rule, page cap and full sweep; embedded replies; `reply_candidates`.
- Author minimization, edit versions, `platform_sync` deletions, comments-disabled handling, the per-video comment index, the job report.

### Out of scope

- Deciding when to fetch (comment-decay-scheduler); replies beyond those embedded (yt-replies-fetcher).
- Finding videos (yt-pubsub-receiver, yt-uploads-reconciler, yt-keyword-search); video statistics and video state, including deleted or private videos (yt-video-details-fetcher).
- Deleting or refreshing text at 30 days (yt-text-purger for retention-purger); removing deleted comments from stores (deletion-propagator); deduplication (normalize-item).
- Commenter profiles: never requested, never built.

## 4. Users and consumers

- **Clients** see "the comments under the videos I watch, current through their first month" and can request a refresh of one video after its series ends.
- **Ops** watch quota use, series lateness, deletion-guard holds and the DLQ.
- **Downstream**: normalize-item and store-writer (ClickHouse `comments`, keyed by `parent_id`), comment-decay-scheduler (`jobs.completed`), yt-replies-fetcher (`replies` jobs built from `reply_candidates`), deletion-propagator, yt-text-purger, raw-archiver, aggregator (cross-owner rule via `video_channel_id`), quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.yt-comments-fetcher`, partitioned by `source_id`, with kind `comments`, `post_ref` (the video), `series_step`, `due_at` and `attempt`. Only comment-decay-scheduler emits these jobs; it keeps one `comment_series` row per video and advances or ends the series from the `jobs.completed/v1` event the listening-sdk job wrapper writes when this service finishes. This service runs no scheduler of its own.

**Which videos.** A series opens when a video first reaches `items.normalized`: uploads on registered channels (yt-pubsub-receiver, with yt-uploads-reconciler catching missed pushes) and videos found by yt-keyword-search, whose `source_id` is the keyword-rule source.

**Series.** +6 h, +24 h, +3 d, +7 d, +30 d after the video is first seen. Early stop: comment-decay-scheduler applies it from this service's report; this service never stops a series itself (ADR-0019). Extension: when the last scheduled step before day 30 (+7 d) still adds 20% or more, a fetch every 2 days until day 30. Hot posts: above 100 new comments an hour, an extra hourly fetch for 6 hours. After the series nothing is automatic; a client can request a refresh through comment-decay-scheduler, budget permitting.

**Staying on time.** Workers scale on partition lag; a video is in at most one job at a time. A late step still reads everything newer than the newest stored thread, so lateness costs freshness, not completeness. When quota is short, quota-governor's priorities decide which steps run (section 7).

**Backfill.** None separate: a video's first fetch, including videos that backfill-orchestrator brings in for a new channel, pages from the newest thread to the end of the list within the page cap.

### 5.2 Step by step

1. Consume a job; read the `sources` row (`platform_id` = channel id, `retention_class`, `client_ids`, `health`) and the video's comment-index rows; stop if `health = blocked`.
2. Ask quota-governor for allowance (`youtube_data_api`, bucket `comments`, priority from `series_step`). On wait-until, requeue for that time; on deny, make no call, count `quota_denied_total`, finish with status `quota_denied`.
3. Fetch the company app's API key from Supabase Vault for this job only.
4. Request a page (5.3). For each thread and embedded reply, `content_hash` = sha256 of `textOriginal`; classify `new` (id not in the index), `edit` (same id with a newer `updatedAt` or a different `content_hash`; written as a new version) or `seen`.
5. Minimize: replace `authorChannelId` with `author_ref`, an HMAC-SHA256 keyed from Vault and scoped to the video's channel; set `author_is_source` when the commenter is the channel itself; drop `authorDisplayName`, `authorProfileImageUrl`, `authorChannelUrl`.
6. Write one `raw.items` message per comment; raw-archiver lands the batch under `raw/green/youtube/<yyyy>/<mm>/<dd>/yt-comments-fetcher/`.
7. Paging. Stop rule: stop after a page containing a thread whose id and `content_hash` are already stored. Page cap (value set in the pilot from the `comments` bucket): a fetch stopped by it marks the video `partial`, and the stop rule stays off until a fetch reaches a thread stored before the gap or the end of the list. The +30 d step and client refreshes are full sweeps: stop rule off, cap on. Otherwise follow `nextPageToken`; a fetch that ends with no token is complete.
8. On a complete fetch of a video with comments enabled: each stored top-level comment not returned, and each stored reply of a thread whose embedded replies equal its `totalReplyCount`, goes to `deletions` with reason `platform_sync`, subject to the deletion guard (section 8).
9. After Redpanda acknowledges: update the comment index and `cursors`; return the report (`new_count`, `seen_count` with edits included, `pages`, `cost_units` = pages, `reply_candidates`: threads with more than 5 replies, listed when first seen or when `totalReplyCount` changed). The wrapper writes `jobs.completed/v1`; comment-decay-scheduler sends each candidate to yt-replies-fetcher.

### 5.3 The call it makes

```
GET https://www.googleapis.com/youtube/v3/commentThreads
  ?part=snippet,replies
  &videoId=<id>
  &maxResults=100
  &order=time
  &pageToken=<token>          (omitted on the first page)
```

Auth: the company app's API key, from Supabase Vault per job; no OAuth, public comments only. Cost: 1 unit per page. Page size: `maxResults=100`. Pagination: `nextPageToken` from each response becomes `pageToken`; no token means the end of the list. `order=time` returns newest threads first, which the stop rule relies on. Anything else (a `fields` filter dropping author display fields at the source, `textFormat`, passing the key as a header to keep it out of access logs) is to be confirmed in the pilot.

### 5.4 What it gets

Per thread: `id`, `snippet.videoId`, `snippet.channelId`, `totalReplyCount`, `canReply`, `isPublic`; the top-level comment's `id`, `authorChannelId`, `textOriginal`, `likeCount`, `publishedAt`, `updatedAt`; and the replies embedded under `replies.comments`, each with `parentId`. Example, author display fields omitted:

```json
{
  "kind": "youtube#commentThread",
  "id": "UgzK7pQ2mV9xR4tL1bN6AaABAg",
  "snippet": {
    "channelId": "UC7xQe2lW9pK3bN5aV1rT8sQ", "videoId": "q3Vt8LmZ2xA",
    "canReply": true, "isPublic": true, "totalReplyCount": 7,
    "topLevelComment": {
      "kind": "youtube#comment", "id": "UgzK7pQ2mV9xR4tL1bN6AaABAg",
      "snippet": {
        "authorChannelId": {"value": "UCm2Lr8dT0vX5kQ9wE3jH7nA"},
        "textOriginal": "الخدمة صارت أسرع بعد التحديث، بس الأسعار بعدها غالية",
        "likeCount": 14,
        "publishedAt": "2026-10-06T21:40:05Z", "updatedAt": "2026-10-06T21:40:05Z"
      }
    }
  },
  "replies": {"comments": [{"id": "UgzK7pQ2mV9xR4tL1bN6AaABAg.9TqLm2Wx8Rb", "snippet": {"parentId": "UgzK7pQ2mV9xR4tL1bN6AaABAg"}}]}
}
```

What it does not get: replies beyond those embedded (yt-replies-fetcher); comments YouTube does not list publicly; video statistics, including comment counts (yt-video-details-fetcher); anything about commenters beyond the hashed reference.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.yt-comments-fetcher`; `sources`, `cursors`, `budgets` through quota-governor, `health` through the SDK canary hook; the comment index; the API key and author-hash key from Supabase Vault.

### 6.2 Writes

`raw.items`, one message per comment (a top-level message carries the thread without its `replies` part; each embedded reply is its own message), envelope plus the record as returned minus the removed author fields:

```json
{
  "envelope": {
    "platform": "youtube", "kind": "comment", "route": "green", "vendor": null,
    "service": "yt-comments-fetcher",
    "source_id": "3a9e5c1d-7f2b-4e8a-b6d0-91c4f2e7a835",
    "platform_id": "UgzK7pQ2mV9xR4tL1bN6AaABAg",
    "idempotency_key": "youtube:comment:UgzK7pQ2mV9xR4tL1bN6AaABAg",
    "parent_video_id": "q3Vt8LmZ2xA", "parent_comment_id": null,
    "video_channel_id": "UC7xQe2lW9pK3bN5aV1rT8sQ",
    "author_ref": "hmac:4e7b1c9a0f2d8e5b6a3c", "author_is_source": false,
    "content_hash": "sha256:9c1e4b7a02f35d8e6b1a7c4f0e2d9b3a5c8f1e6d4b2a0c9e7f3d5b1a8c6e4f20",
    "observation": "new",
    "job_id": "01J9P4D2K8W6Y3N0Q5T7V1X9ZC", "attempt": 1, "series_step": "+24h",
    "fetched_at": "2026-10-07T07:03:11Z",
    "retention_class": "youtube_30d_text",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/youtube/2026/10/07/yt-comments-fetcher/000057.jsonl.zst",
    "removed_fields": ["authorChannelId", "authorDisplayName", "authorProfileImageUrl", "authorChannelUrl"]
  },
  "payload": { "...": "the thread from 5.4 without replies and without the removed fields" }
}
```

`series_step` is passed through exactly as comment-decay-scheduler labels it. Also: `deletions` (`idempotency_key`, `parent_video_id`, reason `platform_sync`, `job_id`, `detected_at`), `service_runs`, `review_queue` (deletion-guard holds), `dlq.yt-comments-fetcher` after 5 failed attempts.

### 6.3 State

The comment index (Supabase Postgres, owned by this service): per comment `video_id`, `comment_id`, `parent_comment_id`, `content_hash`, `updated_at`, `total_reply_count`, `last_seen_at`; per video `stored_count`, `last_complete_fetch_at`, `partial`, `comments_disabled_at`. No text, no author. `cursors` per (`source_id`, `yt-comments-fetcher`): `last_success_at`, `last_error`, `consecutive_errors`. No page token is kept between fetches. In memory: backoff state only.

## 7. Limits, quotas and cost

- YouTube Data API default quota: 10,000 units a day; extensions by audit. `commentThreads.list` costs 1 unit per page of up to 100 threads.
- Budget tag `youtube_data_api`, bucket `comments`. `ingest` and `comments` may borrow from each other; `search` never borrows; `reserve` is for priority 1, which no job here carries.
- Planning split: about 4,000 to 5,000 units a day for the 1-unit endpoints carrying YouTube's 3.0M items a month, shared by `ingest` and `comments` (quota arithmetic to be measured in the pilot); search planned at 20 to 30 calls a day; the rest reserve.
- Priorities: 2 = steps up to +24 h; 3 = later steps and extensions; 4 = hot-post extras. From 80% of the day's units (stretch) quota-governor admits priorities 1 to 3, so hot extras stop first; from 95% only 1 and 2, so only the +6 h and +24 h steps run.
- Every step costs at least 1 unit, so an uninterrupted series costs at least 5; the shared allowance therefore bounds how many new videos a day get a full series (per-video cost and video count to be measured in the pilot).
- Developer Policies: raw comment text kept no longer than 30 days, deleted or refreshed (yt-text-purger does it for retention-purger; class `youtube_30d_text` on every message and batch); derived metrics up to 36 months for Analytics & Reporting clients; no aggregation across channels of different owners except under the carve-out; no profiling on protected attributes; YouTube may audit at any time.
- Cost: USD 0 per call; the cost is quota.

## 8. Failure handling and fallback

- HTTP 429 and rate-limit errors: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.yt-comments-fetcher` and an alert fires.
- HTTP 403 is classified by error reason first (reason strings to be confirmed in the pilot). Comments disabled: record `comments_disabled_at`, finish with status `comments_disabled` so comment-decay-scheduler ends the series; no deletions, key untouched. Daily quota exhausted: reported to quota-governor, requeued at its wait-until. Any other 403, and 401: mark the key `degraded`, stop the batch, alert; never switch to another key or project to obtain more quota.
- Video not found (deleted or private): status `video_not_found`, series ends, no deletions (question 3).
- Empty 200: a first page with no threads for a video with stored comments is never treated as complete; counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. YouTube has no amber route, so `fallback_on` is never set.
- Deletion guard: a complete fetch that would delete more than a set share of a video's stored comments (threshold set in the pilot) parks the deletions in `review_queue` and raises `deletion_guard_hold`.
- Schema change: payload archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: the index and `cursors` change only after acknowledgement; a retry restarts from the newest thread; normalize-item deduplicates; deletions are emitted only after the fetch's comment messages are acknowledged.

## 9. Non-functional requirements

- Throughput: YouTube's full-scale share is 3.0M items a month; videos in open series and jobs a day are to be measured in the pilot. Quota, not compute, is the ceiling.
- Latency: a public comment reaches `raw.items` at the next step plus fetch time.
- Idempotency: `youtube:comment:<comment id>` plus `content_hash`; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag; no leader election.
- Security and privacy: keys from Vault per job, never logged; comment text and commenter ids never logged; YouTube data is never used to profile people on protected attributes; no OAuth, account pools or proxies; provenance on every message.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds` (now minus `due_at` of the most overdue queued job), `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `series_step_lateness_seconds`, `versions_total`, `deletions_total`, `deletions_held_total`, `comments_disabled_total`, `reply_candidates_total`, `fetch_capped_total`, `youtube_error_total{reason}`. Alerts: `series_late` (on-time share below 95% over a day), `key_degraded`, `dlq_nonempty`, `empty_200_rate`, `quota_deny_rate`, `deletion_guard_hold`. SLO: comment series on time for 95% of videos; zero jobs lost.

## 11. Dependencies

listening-sdk (job wrapper, idempotency, quota and canary hooks), comment-decay-scheduler, quota-governor, source-health-canary, raw-archiver, normalize-item, store-writer, deletion-propagator, retention-purger, yt-text-purger, yt-replies-fetcher; upstream yt-pubsub-receiver, yt-uploads-reconciler, yt-keyword-search, yt-video-details-fetcher; Supabase Postgres and Vault; Redpanda. YouTube prerequisites: the company Google Cloud project with YouTube Data API v3 and an API key, Developer Policies compliance as an Analytics & Reporting client, the audit for a quota extension.

## 12. Risks and mitigations

- Quota is the binding constraint: priority ladder, early stop, stop rule and page cap; extension applied for by audit once pilot numbers exist.
- Text outliving 30 days in a copy (archive batches, DLQ, `raw.items` retention): every copy carries `youtube_30d_text`; logs never hold text; topic retention under 30 days to be confirmed with raw-archiver.
- False deletions from a truncated or empty response: deletions only on complete fetches, empty first pages never complete, guard to `review_queue`.
- Edits below the stop point missed by incremental steps: caught by the +30 d full sweep; disclosed in provenance.
- Re-identification of commenters: keyed hash scoped per channel, display fields dropped before anything is written.

## 13. Acceptance criteria

1. Against a simulated API, a video with 250 stored threads and 30 new ones on top costs 1 page and reports `new_count = 30`, `seen_count = 70`, `pages = 1`, `cost_units = 1`.
2. A first fetch of a video with 250 threads and nothing stored requests 3 pages, ends with no `nextPageToken`, and sets `last_complete_fetch_at`.
3. A stored comment returned with the same id, a newer `updatedAt` and changed text yields one message with `observation = edit` and a new `content_hash`; an unchanged one yields `seen`.
4. On a complete fetch with comments enabled, a missing stored top-level comment produces one `deletions` message with reason `platform_sync`; a fetch ended by the stop rule or the cap produces none; a reply of a thread whose embedded replies are fewer than its `totalReplyCount` is never deleted.
5. An empty first page for a video with 40 stored comments emits no deletions and increments the empty-200 counter.
6. The comments-disabled error yields status `comments_disabled` in `jobs.completed`, no deletions, no retry, no `degraded` key, and the series ends.
7. A thread with `totalReplyCount = 6` is in `reply_candidates`, one with 5 is not, and the same thread unchanged at the next step is not listed again; its embedded replies are written with `parent_comment_id` set.
8. No `raw.items` message, log line, DLQ message or archived batch contains `authorChannelId`, `authorDisplayName`, `authorProfileImageUrl` or `authorChannelUrl`; one commenter on two channels gets two different `author_ref` values.
9. Every message carries `route = green`, `vendor = null`, `service`, `fetched_at`, `retention_class = youtube_30d_text`, `parent_video_id` and `series_step`.
10. With quota-governor at 95%, +3 d and hot-extra jobs make zero calls while a +6 h job proceeds; no job draws on `reserve`.
11. A simulated 429 backs off from 30 s to at most 15 min with `attempt + 1`; after 5 attempts the job is in `dlq.yt-comments-fetcher` and an alert fired.
12. When the Redpanda produce fails, the comment index is unchanged and the replayed job reports the same `new_count`.

## 14. Open questions

1. Is `textOriginal` returned for every public comment with an API key? YouTube documents it as guaranteed only for the author; fallback `textDisplay`. To be confirmed in the pilot.
2. Status values (`quota_denied`, `comments_disabled`, `video_not_found`) and the priority of client refreshes (proposed 3) must be aligned with comment-decay-scheduler.
3. Should a not-found video trigger removal of its stored comments? Proposed: yt-video-details-fetcher owns video state and decides.
4. Author-hash scope: per channel (proposed, blocks linking a commenter across owners) or per owner, so a client with several channels can count unique commenters.
5. CONVENTIONS keeps aggregates ten years for all classes, while YouTube allows derived metrics up to 36 months: retention-purger's rule for YouTube aggregates needs a decision.
