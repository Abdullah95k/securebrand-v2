# yt-replies-fetcher

**Platform:** YouTube · **Route:** green · **Lane:** Comments · **Owner:** Backend lead, YouTube adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

On a busy Iraqi video the conversation happens in the replies: a viewer reports an outage, dozens answer that they have the same problem, and the brand's own channel replies with an apology or a repair date. The thread resource that yt-comments-fetcher reads embeds only a few replies, so on every thread with more than 5 replies most of that conversation never reaches the product. yt-replies-fetcher reads the full reply list of those threads through the official YouTube Data API and keeps it current on the video's comment schedule.

Without it, a complaint that dozens endorsed counts as one voice, sentiment and topics on the busiest threads rest on their first few answers, most of a channel's answers to its audience are missing, and edited or removed replies there go unnoticed.

## 2. Objective (the end state this service delivers)

Every thread listed in `reply_candidates` has its reply series executed: each step fetched when due, or skipped at no cost when its `totalReplyCount` is known to be unchanged; every public reply YouTube lists reaches `raw.items` by the next step, edits as new versions, removals as `deletions`. Target: 95% of candidate threads complete their reply series on time (each step finished before the next falls due, the +30 d step within 24 hours), zero jobs lost, zero calls without a quota-governor allowance or for threads known to be unchanged, zero messages carrying a reply author id in clear.

## 3. Scope

### In scope

- `replies` jobs from `jobs.yt-replies-fetcher`: series steps, extensions, hot-thread extras, client refreshes.
- The skip rule; paging `comments.list` by `parentId`; author minimization; edit versions; `platform_sync` deletions of replies; the reply index; the job report.

### Out of scope

- When to fetch (comment-decay-scheduler); top-level comments and embedded replies (yt-comments-fetcher).
- Text deletion at 30 days (yt-text-purger for retention-purger); removal from stores (deletion-propagator); deduplication (normalize-item).
- Reply-author profiles and reply networks: never requested, never built.

## 4. Users and consumers

- **Clients** see the whole conversation under a comment, including the channel's own replies, current through the video's first month.
- **Ops** watch quota, skip rate, capped threads, deletion-guard holds and the DLQ.
- **Downstream**: normalize-item and store-writer (ClickHouse `comments`, `parent_id` = the thread), comment-decay-scheduler, deletion-propagator, yt-text-purger, raw-archiver, quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.yt-replies-fetcher`, partitioned by `source_id`: kind `replies`, `post_ref` (video id and thread id), `series_step`, `due_at`, `attempt`. Only comment-decay-scheduler emits it: a reply series opens when yt-comments-fetcher first lists a thread in `reply_candidates`, and the first job is raised as soon as that comments job completes.

**Series.** Replies follow the video's series: +6 h, +24 h, +3 d, +7 d, +30 d after the video is first seen. A thread joins at the step where it was first listed; each later job is raised after the video's comments job for that step completes. Early stop: comment-decay-scheduler applies it from this service's report; this service never stops a series itself (ADR-0019). Where this paragraph differs from ADR-0060 (no per-thread series; one `replies` job per video carrying `thread_ids`), ADR-0060 wins (ADR-0001). Extension: when the +7 d step still adds 20% or more, a fetch every 2 days until day 30. Hot threads: above 100 new replies an hour, an extra hourly fetch for 6 hours. A thread listed again after an early stop gets one job at that step. After day 30, only a client refresh that lists the thread raises a job.

**Skip rule.** A thread whose `totalReplyCount` has not changed since the last fetch is skipped at no cost: when yt-comments-fetcher's comment index re-observed it after this service's last fetch (`last_seen_at` later than `last_fetch_at`) with the same `total_reply_count`, the job ends `unchanged`, with no allowance request and no call. A thread not re-observed (below yt-comments-fetcher's stop point, or on a hot-thread extra) is fetched.

**Staying on time and backfill.** Workers scale on partition lag; a thread is in at most one job at a time; a late step still reads every reply not yet stored. No separate backfill: a thread's first fetch reads its whole list within the page cap.

### 5.2 Step by step

1. Consume a job; read the `sources` row (`platform_id` = channel id, `retention_class`, `client_ids`, `health`), the thread's reply-index rows and its comment-index row; stop if `health = blocked`.
2. Apply the skip rule.
3. Ask quota-governor (`youtube_data_api`, bucket `comments`, priority 3, or 4 for hot-thread extras); on wait-until requeue; on deny make no call and finish `quota_denied`. Take the API key from Supabase Vault for this job only.
4. On a thread's first fetch, seed the reply index from comment-index rows whose `parent_comment_id` is the thread, so embedded replies count as stored.
5. Request a page (5.3); per reply, `content_hash` = sha256 of the text; classify `new`, `edit` (newer `updatedAt` or different `content_hash`; a new version) or `seen`.
6. Minimize: `authorChannelId` becomes `author_ref` with yt-comments-fetcher's HMAC-SHA256 key and per-channel scope, so a person's comment and reply under one channel match; `author_is_source` marks the channel itself; display name, image and channel URL are dropped.
7. Write one `raw.items` message per reply; raw-archiver lands the batch under `raw/green/youtube/<yyyy>/<mm>/<dd>/yt-replies-fetcher/`.
8. Page in the order the pilot confirms. Newest first: stop after a page containing a reply stored with the same id and `content_hash`. Oldest first: page to the end, comparing by id and `content_hash`. Page cap (value set in the pilot): a capped fetch marks the thread `partial`, and the stop rule stays off until a fetch reaches a reply stored before the gap. The +30 d step and client refreshes read to the end. No `nextPageToken` means complete.
9. On a complete fetch, each stored reply not returned goes to `deletions` with reason `platform_sync`, subject to the deletion guard.
10. After Redpanda acknowledges, update the reply index (`reply_count_at_last_fetch` = the count read in step 1) and `cursors`; report `new_count`, `seen_count` (edits included), `stored_count`, `pages`, `cost_units` = pages, `complete`. The wrapper writes `jobs.completed/v1`; comment-decay-scheduler applies the series rules.

### 5.3 The call it makes

```
GET https://www.googleapis.com/youtube/v3/comments
  ?part=snippet
  &parentId=<thread id>
  &maxResults=100
  &pageToken=<token>          (omitted on the first page)
```

Auth: the company app's API key, from Supabase Vault per job; no OAuth, public replies only. Cost: 1 unit per page. Page size: `maxResults=100`. Pagination: `nextPageToken` becomes `pageToken`; no token means the end. `<thread id>` is the id yt-comments-fetcher reports in `reply_candidates`. To be confirmed in the pilot: the order of results, the `textFormat` choice, and anything else (a `fields` filter, passing the key as a header).

### 5.4 What it gets

Per reply: `id`, `snippet.parentId`, `snippet.authorChannelId`, the text (`textOriginal`, or `textDisplay` per the pilot), `likeCount`, `publishedAt`, `updatedAt`; per page, `nextPageToken`. Example from the thread shown in yt-comments-fetcher (`totalReplyCount` 7), author display fields omitted:

```json
{
  "kind": "youtube#comment",
  "id": "UgzK7pQ2mV9xR4tL1bN6AaABAg.9TqNw5Hc3Kp",
  "snippet": {
    "parentId": "UgzK7pQ2mV9xR4tL1bN6AaABAg",
    "authorChannelId": {"value": "UCp4Wd9sK2tY7mR1xN6bL3eQ"},
    "textOriginal": "نفس المشكلة عدنا بالكوت، اتصلت بالدعم ثلاث مرات وماكو رد",
    "likeCount": 3,
    "publishedAt": "2026-10-06T23:12:47Z", "updatedAt": "2026-10-06T23:12:47Z"
  }
}
```

What it does not get: the thread's `totalReplyCount` (read from the comment index), the top-level comment, replies YouTube does not list publicly, anything about authors beyond the hashed reference.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.yt-replies-fetcher`; `sources`, `cursors`, `budgets` through quota-governor, `health` through the SDK canary hook; the reply index; yt-comments-fetcher's comment index, read only; the API key and author-hash key from Supabase Vault.

### 6.2 Writes

`raw.items`, one message per reply, in yt-comments-fetcher's envelope with `parent_comment_id` set:

```json
{
  "envelope": {
    "platform": "youtube", "kind": "comment", "route": "green", "vendor": null,
    "service": "yt-replies-fetcher",
    "source_id": "3a9e5c1d-7f2b-4e8a-b6d0-91c4f2e7a835",
    "platform_id": "UgzK7pQ2mV9xR4tL1bN6AaABAg.9TqNw5Hc3Kp",
    "idempotency_key": "youtube:comment:UgzK7pQ2mV9xR4tL1bN6AaABAg.9TqNw5Hc3Kp",
    "parent_video_id": "q3Vt8LmZ2xA", "parent_comment_id": "UgzK7pQ2mV9xR4tL1bN6AaABAg",
    "video_channel_id": "UC7xQe2lW9pK3bN5aV1rT8sQ",
    "author_ref": "hmac:b81d5e2a9c07f4e3d6a1", "author_is_source": false,
    "content_hash": "sha256:2f8a6c1e9b4d07e3a5c2f9b1d6e8a4c07b3e5f1a9d2c6b8e4f0a7d3c1b5e9f26",
    "observation": "new",
    "job_id": "01J9P4F7M2R8T5W0Y3B6D9H1KN", "attempt": 1, "series_step": "+24h",
    "fetched_at": "2026-10-07T07:05:42Z",
    "retention_class": "youtube_30d_text",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/youtube/2026/10/07/yt-replies-fetcher/000031.jsonl.zst",
    "removed_fields": ["authorChannelId", "authorDisplayName", "authorProfileImageUrl", "authorChannelUrl"]
  },
  "payload": { "...": "the reply from 5.4 without the removed fields" }
}
```

Also: `deletions` (`idempotency_key`, `parent_video_id`, `parent_comment_id`, reason `platform_sync`, `job_id`, `detected_at`), `service_runs`, `review_queue` (deletion-guard holds), `dlq.yt-replies-fetcher`.

### 6.3 State

The reply index (Supabase Postgres, owned here): per reply `thread_id`, `reply_id`, `content_hash`, `updated_at`, `last_seen_at`; per thread `video_id`, `stored_count`, `reply_count_at_last_fetch`, `last_fetch_at`, `last_complete_fetch_at`, `partial`. No text, no author. `cursors` per (`source_id`, `yt-replies-fetcher`). No page token is kept between fetches (question 1).

## 7. Limits, quotas and cost

- Default quota 10,000 units a day; extensions by audit. `comments.list`: 1 unit per page of up to 100 replies.
- Budget tag `youtube_data_api`, bucket `comments`, shared with yt-comments-fetcher inside the planning split of about 4,000 to 5,000 units a day for `ingest` and `comments` (to be measured in the pilot); no job here touches `reserve`.
- Priorities: 3 for steps, extensions and client refreshes; 4 for hot-thread extras. From 80% of the day's units quota-governor admits 1 to 3, so hot extras stop first; from 95% only 1 and 2, so replies wait while the +6 h and +24 h comment steps run.
- Newest first, a step costs about one page per 100 new replies; oldest first, every fetch re-reads the thread up to the cap. Candidate threads a day and skip rate: to be measured in the pilot.
- Developer Policies: raw text no longer than 30 days (`youtube_30d_text`, enforced by yt-text-purger); derived metrics up to 36 months; no aggregation across owners except under the carve-out; no profiling on protected attributes; audit at any time.
- Cost: USD 0 per call; the cost is quota.

## 8. Failure handling and fallback

- HTTP 429: backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts, `dlq.yt-replies-fetcher` and an alert.
- HTTP 403 by error reason (strings to be confirmed in the pilot): comments disabled ends the thread's series with status `comments_disabled`, no deletions; quota exhausted requeues at quota-governor's wait-until; any other 403, and 401, mark the key `degraded`, stop and alert, never switching keys or projects.
- Parent comment not found: status `thread_not_found`, series ends, no deletions (question 4).
- Empty 200: an empty first page for a thread with stored replies is never complete; above 5% in 15 minutes source-health-canary flips `health = degraded`; no amber route exists, so no `fallback_on`.
- Deletion guard: a fetch deleting more than a set share of stored replies (threshold set in the pilot) parks them in `review_queue`, alert `deletion_guard_hold`.
- Comment index unreadable: no call; requeue with `attempt + 1`.
- Partial write: index and `cursors` change only after acknowledgement; deletions follow the acknowledged reply messages; normalize-item deduplicates replays.

## 9. Non-functional requirements

- Throughput: YouTube's 3.0M items a month cover comments and replies; the reply share is to be measured in the pilot. Quota is the ceiling.
- Latency: a reply reaches `raw.items` at the thread's next step plus fetch time.
- Idempotency: `youtube:comment:<reply id>` plus `content_hash`; replayable jobs.
- Security: keys per job, never logged; no text or author ids in logs; no OAuth, account pools or proxies; provenance on every message.

## 10. Metrics and alerts

Standard set (`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`) plus `threads_skipped_unchanged_total`, `pages_per_fetch`, `versions_total`, `deletions_total`, `deletions_held_total`, `fetch_capped_total`, `youtube_error_total{reason}`. Alerts: `series_late` (on-time share below 95% over a day), `key_degraded`, `dlq_nonempty`, `empty_200_rate`, `deletion_guard_hold`.

## 11. Dependencies

listening-sdk, comment-decay-scheduler, yt-comments-fetcher (`reply_candidates`, comment index), quota-governor, source-health-canary, raw-archiver, normalize-item, store-writer, deletion-propagator, retention-purger, yt-text-purger; Supabase Postgres and Vault; Redpanda; the company Google Cloud project and API key.

## 12. Risks and mitigations

- One busy thread can cost more than its video's comments: skip rule, early stop, priorities 3 and 4, page cap.
- Oldest-first order makes every fetch a full read, and a thread above the cap loses its newest replies: the pilot settles order first; `fetch_capped_total` names those threads.
- Threads below yt-comments-fetcher's stop point are never skipped on a guess, so each step costs a fetch.
- False deletions: complete fetches only, guard to `review_queue`.
- Re-identification through reply chains: per-channel keyed hash; no per-person reply analysis.

## 13. Acceptance criteria

1. A thread re-observed after the last fetch with unchanged `total_reply_count` gets zero API calls and zero quota-governor requests; report `unchanged`, `cost_units = 0`.
2. The same count on a thread not re-observed, or on a hot-thread extra, is fetched.
3. A first fetch of a thread with 7 replies, 5 embedded and stored, reports `new_count = 2`, `seen_count = 5`, `pages = 1`, `cost_units = 1`.
4. A thread with 250 replies and nothing stored takes 3 pages, ends without `nextPageToken` and sets `last_complete_fetch_at`, in both order modes.
5. With 250 stored and 30 new: newest-first reads 1 page (`new_count = 30`, `seen_count = 70`); oldest-first reads 3 pages (`new_count = 30`, `seen_count = 250`).
6. A stored reply with a newer `updatedAt` and changed text yields `observation = edit` and a new `content_hash`; an unchanged one yields `seen`.
7. A complete fetch missing a stored reply, seeded ones included, emits one `deletions` message with reason `platform_sync`; capped or stop-rule fetches emit none.
8. An empty first page for a thread with 40 stored replies emits no deletions and increments the empty-200 counter.
9. Every message carries `kind = comment`, `parent_comment_id`, `parent_video_id`, `route = green`, `vendor = null`, `series_step` and `retention_class = youtube_30d_text`.
10. No message, log line, DLQ entry or batch contains author channel ids, names, images or URLs; a person's comment and reply under one channel share an `author_ref`, under two channels they differ.
11. At 80% quota a hot-thread extra makes no call while a +3 d reply job runs; at 95% that job waits while a +6 h comments job runs.
12. When the Redpanda produce fails, the reply index is unchanged and the replay reports the same `new_count`.

## 14. Open questions

1. Order of `comments.list` results, and whether a page token stays valid between steps so an oldest-first thread can resume.
2. `textFormat`: is `textOriginal` returned for every public reply with an API key, or only `textDisplay`?
3. Status values, `post_ref` shape, client-refresh priority (proposed 3) and the one-job rule after early stop: align with comment-decay-scheduler.
4. When a parent comment is removed, does deletion-propagator cascade to its replies (proposed) or does this service emit them?
5. A thread falling to 5 replies or fewer leaves `reply_candidates`; who detects later removals of replies stored here?
