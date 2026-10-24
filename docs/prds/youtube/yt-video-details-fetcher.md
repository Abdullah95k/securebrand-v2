# yt-video-details-fetcher

**Platform:** YouTube · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, YouTube adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Each way we discover a YouTube video yields a fragment. A PubSubHubbub notification carries an id, a title and two timestamps; the uploads playlist adds a description; a keyword search returns a snippet. None says how long it runs, its language, its topics, or how many people watched, liked and commented: the facts a client's YouTube report is built on.

yt-video-details-fetcher asks YouTube for the complete record when a video is first seen, and for fresh counts at +24 h and +7 d. One call takes up to 50 ids for 1 quota unit, so ids from many channels share each call and the cost is close to nothing. Without it, every YouTube video stays a partial record that normalize-item never releases: no YouTube posts, no comment series, no views or likes, no engagement at 24 h and 7 d, and deleted videos stay visible to clients.

## 2. Objective (the end state this service delivers)

Every YouTube video id that reaches the platform becomes one complete record in `raw.items` and at least three observations in `item.metrics` (first sight, +24 h, +7 d), and leaves the product through `deletions` once YouTube stops returning it. Targets: 99% of `first_sight` jobs completed within 60 minutes (one Tier 1 interval) of `due_at`; 95% of +24 h and +7 d observations within 60 minutes of due time; units per 1,000 videos reported daily against the full-batch floor of 60 (three lookups per video, 50 ids per call), with the achieved fill to be measured in the pilot.

## 3. Scope

### In scope

- `first_sight` jobs: the full record to `raw.items` (kind `post`, `partial: false`), completing the partial one, and a `first_sight` observation to `item.metrics` from the same response.
- `metrics` jobs at +24 h, +7 d and on client request: counts only, to `item.metrics`.
- `ops_force` re-lookups, handled like first sight.
- Ids missing from a response: `deletions` with reason `platform_sync`, closing the video's series.
- Live streams and premieres: state recorded, refreshed when the stream ends (to be confirmed in the pilot).

### Out of scope

- Finding ids (yt-pubsub-receiver, yt-uploads-reconciler, yt-keyword-search, yt-web-search-bridge), comments and replies (yt-comments-fetcher, yt-replies-fetcher), the 30-day text refresh (yt-text-purger).
- Language detection (lang-dialect-id), thumbnail download (analysis-media), storage and aggregation (store-writer, aggregator).

## 4. Users and consumers

- **Clients** see duration, topics, views, likes, comment counts and engagement at 24 h and 7 d; **ops** watches latency, ids per call and quota.
- **normalize-item** holds each YouTube post (`partial: true`) until this service's full record arrives, then releases it.
- **comment-decay-scheduler** opens the comment series for the released post, emits this service's `metrics` jobs, and closes both series on `deletions`.
- **store-writer** and **aggregator** load `item.metrics` into `metrics_timeseries` and `aggregates_hourly`; `channel_id` lets aggregator keep owners apart.
- **deletion-propagator** removes deleted and private videos; **raw-archiver** keeps raw records for audit.

## 5. How it works

### 5.1 Trigger and rotation

No rotation of its own: the service never lists a channel. It works `jobs.yt-video-details-fetcher`, partitioned by `source_id`:

- `first_sight` from yt-pubsub-receiver (push), yt-uploads-reconciler (daily reconciliation; ids from a backfill listing carry `series_step = backfill`) and yt-keyword-search; an id from yt-web-search-bridge arrives the same way and is treated identically.
- `metrics` from comment-decay-scheduler, `series_step` `24h` or `7d` (due at `publishedAt` plus 24 h or 7 d) or `client` (a client's refresh, budget permitting); steps already past at first sight are not emitted.
- `ops_force` from ops.

**Collector.** Each worker pools due ids from its partitions, across channels, in one buffer per governor priority and flushes a call at 50 ids or when the oldest id has waited `FIRST_SIGHT_FLUSH_SECONDS` or `REFRESH_FLUSH_SECONDS`, both to be measured in the pilot. Highest-priority ids go first; spare slots take lower-priority due ids, oldest first, since a call costs 1 unit for 3 ids or 50. Jobs for one id share a slot.

**Priorities** (quota-governor): 1 for Tier 1 first sight, client refreshes and `ops_force`; 2 for metrics at +24 h; 3 for metrics at +7 d and live re-checks; 5 for backfill first sight. The approved order does not place first sight from other tiers and keyword rules; this PRD proposes 1 (open question 1).

**Catch-up.** When the oldest due job is more than 60 minutes late, each lane drains most-overdue first and `details_behind` fires; a late observation carries its true `observed_at`.

**Live streams and premieres** (to be confirmed in the pilot). A first sight showing `liveBroadcastContent` `live` or `upcoming` is still emitted, with `live_state`, and the id joins `yt_live_watch`, falling due again at a re-check interval to be measured in the pilot. When the state turns `none`, the service emits an updated record (final duration) and a `live_end` observation.

### 5.2 Step by step

1. Attach each job to its id's slot in the right priority buffer.
2. On flush, ask quota-governor for 1 unit (`youtube_data_api`, bucket `ingest`) at the priority of the call's highest member; wait-until holds the buffer, deny keeps the ids due.
3. Call 5.3 with the company app's API key from Supabase Vault.
4. Match results by `id`, never by position. `first_sight` and `ops_force`: one `raw.items` record per distinct `source_id` sharing the slot, so each partial record is completed on its own partition, plus one observation (`first_sight` or `ops_force`). `metrics`: one observation (`refresh_24h`, `refresh_7d`, `refresh_client`), no record.
5. A missing id stays for exactly one more call; missing again, it becomes one `deletions` message. If every id in a call is missing, that is an empty 200 (section 8), not 50 deletions.
6. After Redpanda acknowledges, write one completion per job to `jobs.completed`, commit offsets per partition up to the oldest unfinished job, and log the `call_id` with its ids.

### 5.3 The call it makes

```
GET https://www.googleapis.com/youtube/v3/videos
  ?part=snippet,statistics,contentDetails,topicDetails
  &id=<up to 50 comma-separated video ids>
  &key=<API key>
```

1 unit per call regardless of the number of ids; API key only, no OAuth and no client token. One call shape serves first sight, refreshes and live re-checks, so every job kind can share a call. To be confirmed in the pilot: that an id lookup returns no page token, the error reasons separating quota exhaustion from a revoked key, and how a malformed id is reported.

### 5.4 What it gets

`snippet` (`title`, `description`, `tags`, `publishedAt`, `channelId`, `defaultAudioLanguage`, `thumbnails`, `liveBroadcastContent`), `contentDetails.duration` (ISO 8601, `PT12M41S`), `statistics` (`viewCount`, `likeCount`, `commentCount` as decimal strings, parsed to integers) and `topicDetails.topicCategories` (Wikipedia URLs); example in 6.2. A hidden or switched-off count is absent and becomes `null`, never 0 (which counts can be absent: to be confirmed in the pilot).

It does not get dislikes (not public), who viewed or liked, comment text (yt-comments-fetcher), subscriber counts (yt-channel-resolver), watch time or audience data (owner-only). A deleted or private video is simply absent.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.yt-video-details-fetcher` (`job_id`, `source_id`, `kind`, `post_ref` = video id, `due_at`, `attempt`, `series_step`); `sources` (`tier`, `retention_class`); `budgets` through quota-governor; the API key from Supabase Vault; `yt_live_watch`.

### 6.2 Writes

`raw.items`, first sight (payload exactly as returned; trimmed here to the fields used):

```json
{
  "envelope": {
    "platform": "youtube",
    "kind": "post",
    "idempotency_key": "youtube:post:Xy12AbCdEfG",
    "platform_id": "Xy12AbCdEfG",
    "source_id": "2b7d4e90-1c3a-4f6e-8d25-7a9b0c1e3f42",
    "service": "yt-video-details-fetcher",
    "route": "green",
    "vendor": null,
    "partial": false,
    "completes_partial_from": "yt-pubsub-receiver",
    "metrics_observation": "first_sight",
    "live_state": "none",
    "fetched_at": "2026-10-06T07:14:03Z",
    "job_id": "01JAB3K7T2W9M4Q8R1X5Y6Z0NC",
    "call_id": "01JAB3K7V0H5D2E8F1G3J4K6MN",
    "retention_class": "youtube_30d_text"
  },
  "payload": {
    "id": "Xy12AbCdEfG",
    "snippet": {
      "publishedAt": "2026-10-06T07:12:09Z",
      "channelId": "UCq3Ov8nVbT0xY1zKp2LmA4w",
      "title": "جولة في سوق الشورجة",
      "description": "جولة مصورة في أقدم أسواق بغداد",
      "tags": ["بغداد", "الشورجة"],
      "defaultAudioLanguage": "ar",
      "liveBroadcastContent": "none",
      "thumbnails": {"high": {"url": "https://i.ytimg.com/vi/Xy12AbCdEfG/hqdefault.jpg"}}
    },
    "contentDetails": {"duration": "PT12M41S"},
    "statistics": {"viewCount": "312", "likeCount": "41", "commentCount": "6"},
    "topicDetails": {"topicCategories": ["https://en.wikipedia.org/wiki/Society"]}
  }
}
```

`item.metrics`, one message per observation:

```json
{
  "platform": "youtube",
  "item_idempotency_key": "youtube:post:Xy12AbCdEfG",
  "platform_id": "Xy12AbCdEfG",
  "channel_id": "UCq3Ov8nVbT0xY1zKp2LmA4w",
  "source_id": "2b7d4e90-1c3a-4f6e-8d25-7a9b0c1e3f42",
  "service": "yt-video-details-fetcher",
  "route": "green",
  "vendor": null,
  "observation": "refresh_24h",
  "observed_at": "2026-10-07T07:21:40Z",
  "post_created_time": "2026-10-06T07:12:09Z",
  "age_seconds": 86971,
  "live_state": "none",
  "metrics": {"views": 48213, "likes": 1904, "comments": 377},
  "job_id": "01JAD6P2R8S4T0V5W7X9Y3Z1AB",
  "call_id": "01JAD6P3C5E7G9H1J3K5M7N9PQ",
  "retention_class": "youtube_30d_text"
}
```

Also `deletions` (reason `platform_sync`, with both `call_id`s that missed the id), `jobs.completed`, `service_runs`, `dlq.yt-video-details-fetcher`.

### 6.3 State

No cursors; jobs carry everything. Buffers live in worker memory and are rebuilt from uncommitted offsets after a crash; a lost missed-once mark only delays a deletion. `yt_live_watch` (`platform_id`, `source_id`, `live_state`, `next_check_at`); `budgets` through quota-governor; `service_runs`.

Owner (ADR-0025): `yt_live_watch` is private to this service. No other service reads it, F3's `TABLE-OWNERS.md` lists it, and it is registered in the SDK purge registry where it holds item ids, hashes or URLs.

## 7. Limits, quotas and cost

- `videos.list`: 1 unit per call of up to 50 ids, from the default 10,000 units a day shared by all YouTube services under `youtube_data_api`, bucket `ingest`. The planning split gives 1-unit endpoints about 4,000 to 5,000 units a day for 3.0M items a month; this service's share: to be measured in the pilot.
- Arithmetic: three lookups per video (first sight, +24 h, +7 d) cost 60 units per 1,000 videos at full calls and 300 at 10 ids a call; the video count and real fill are to be measured in the pilot.
- Cost: USD 0 per call; the cost is quota, raised only through Google's audit, never by a second key or project.
- Developer Policies: derived metrics up to 36 months (Analytics & Reporting), no cross-owner aggregation outside the carve-out, audit at any time.

## 8. Failure handling and fallback

- HTTP 429 and 5xx: backoff with jitter from 30 s to 15 min, `attempt + 1` for every job in the call; after 5 attempts, `dlq.yt-video-details-fetcher` and an alert.
- A quota-exhausted 403 goes to quota-governor as an exhausted bucket, key healthy; any other 401 or 403 marks the key `degraded`, stops its calls and alerts.
- Missing ids: confirmed once, then `deletions`. A 200 with no items for a non-empty request is an empty 200: no deletions, jobs retried; above 5% in 15 minutes source-health-canary flips `health = degraded`. There is no amber YouTube route to fall back to.
- Schema change: payload archived, `schema_unknown` raised, item parked, never zero-filled.
- Replays: first-sight records reuse their `idempotency_key`; a replayed refresh records a true second observation at its own `observed_at`, never a copy.

## 9. Non-functional requirements

- Throughput: all YouTube first-sight and metrics jobs at full scale with lag under 60 minutes; quota, not compute, is the bound.
- Latency: targets in section 2.
- Idempotency: records keyed `youtube:post:<video id>`, observations on (`item_id`, `observed_at`), completions on `job_id`.
- Scaling: on partition lag only, with as few workers as lag allows, since each extra worker lowers ids per call.
- Security: API key never logged; no account, OAuth token or viewer identity; provenance, `retention_class` and `channel_id` on every message; calls logged with their ids for audit.

## 10. Metrics and alerts

Standard set (`items_fetched_total`, `items_new_total`, `jobs_total{status,kind}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`) plus `ids_per_call`, `first_sight_latency_seconds`, `metrics_lag_seconds`, `observations_total{observation}`, `deletions_total`, `live_watch_size`. Alerts: `details_behind` (oldest due job 60 minutes late), `key_degraded`, `quota_exhausted`, `dlq_nonempty`, `empty_200_rate`, `schema_unknown`; `deletion_spike` and `low_fill` with thresholds set after the pilot.

## 11. Dependencies

listening-sdk; the id producers (yt-pubsub-receiver, yt-uploads-reconciler, yt-keyword-search, yt-web-search-bridge); comment-decay-scheduler; yt-comments-fetcher (same daily quota); normalize-item, store-writer, aggregator, quota-governor, source-health-canary, raw-archiver, deletion-propagator; Supabase Postgres and Vault, Redpanda, ClickHouse. Google: a Cloud project with YouTube Data API v3 and an API key.

## 12. Risks and mitigations

- Glitchy responses could remove existing videos: confirm-once, all-missing treated as empty 200, `deletion_spike`.
- Half-empty calls at small scale: flush timers, spare-slot filling, few workers, `low_fill`.
- A stall holds every YouTube post in normalize-item: `details_behind` at 60 minutes, daily DLQ review, `ops_force`.
- Shared daily quota: backfill slips first, then +7 d, then +24 h; first sight last.

## 13. Acceptance criteria

1. Fifty `first_sight` jobs for distinct ids from 10 channels in one flush window produce one call, 1 `ingest` unit, 50 records with `partial: false` and 50 `first_sight` observations.
2. A lone `first_sight` job is sent when `FIRST_SIGHT_FLUSH_SECONDS` expires, not held for a full call.
3. Three jobs for one id from three producers take one slot and yield three `jobs.completed` entries.
4. A `24h` metrics job yields one `refresh_24h` observation, integer counts, `age_seconds` = `observed_at` − `publishedAt`, and no record.
5. With 30 priority-1 and 40 priority-3 ids due, the call carries all 30 plus the 20 oldest priority-3 and asks at priority 1.
6. An id missing once yields no `deletions`; missing twice, exactly one, with reason `platform_sync`.
7. A 200 with no items for 50 ids yields no `deletions` and counts toward the empty-200 rate.
8. A video without `commentCount` yields `"comments": null`, never 0.
9. A 429 backs off 30 s to 15 min with `attempt + 1`, reaching the DLQ with an alert after 5 attempts; a quota-exhausted 403 leaves the key healthy, any other 403 marks it `degraded`.
10. Killing a worker between produce and commit loses no job and duplicates no (`item_id`, `observed_at`).
11. No message or log line contains the API key; every observation carries `channel_id` and `retention_class`.

## 14. Open questions

1. Priority for first sight from Tier 2, Tier 3, push and keyword-rule sources (proposed 1); confirm in the quota-governor PRD.
2. The `series_step` values on this queue and series close on `deletions`: confirm in the comment-decay-scheduler and yt-uploads-reconciler PRDs.
3. Live streams: re-check interval, and whether +24 h and +7 d anchor on the stream's end.
4. Whether YouTube per-video observations may live past 36 months inside ten-year aggregates.
