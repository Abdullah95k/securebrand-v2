# yt-uploads-reconciler

**Platform:** YouTube · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, YouTube adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

YouTube tells us about new videos by push: yt-pubsub-receiver subscribes to every registered channel through PubSubHubbub and receives each upload within seconds, at no quota cost. Push is fast but not guaranteed. A notification can be lost on the way, a subscription lease can lapse, our receiver can be down during a deploy, and none of this announces itself: a video that never arrives looks exactly like a video that was never published.

yt-uploads-reconciler is the safety net. Once a day it reads each channel's uploads playlist, YouTube's own list of everything the channel has published, and captures whatever we do not already hold. It is also how a new channel gets its history, because push only covers uploads from the moment we subscribe.

Without it, YouTube (3.0M of the 30.5M items a month at full scale) would have silent holes, and each hole costs more than one video: yt-comments-fetcher only works on videos we know, so their comments go missing too. New channels would start with no 90-day baseline, and nobody would notice failing subscriptions, because the missed-push share measured here is the only check of push against the truth.

## 2. Objective (the end state this service delivers)

Every registered YouTube channel that has finished its backfill is checked against its uploads playlist once in every 24 hours; every video not yet stored reaches `raw.items` and yt-video-details-fetcher in the same run; every new channel gets its last 90 days (or the cap) before joining the rotation. Target: rotation lag below 24 hours for 99% of channels per day; 99% of videos first seen here reach `raw.items` within 24 hours of publication (outside quota deferrals); zero jobs lost; the missed-push share published daily and alerted when it rises.

## 3. Scope

### In scope

- Daily rotation of every non-retired YouTube channel; execution of `reconciliation`, `backfill` and `ops_force` jobs on `jobs.yt-uploads-reconciler`.
- Immediate catch-up for channels whose push lease lapsed.
- Incremental reads back to the cursor; 90-day backfill reads at priority 5.
- Partial `raw.items` records (kind `post`, `partial: true`) and `first_sight` jobs for videos not yet stored.
- The missed-push measure and alerts; reports to `jobs.completed`; promotion of a dormant channel that uploads.

### Out of scope

- Subscriptions and leases (yt-pubsub-receiver); statistics, duration and tags (yt-video-details-fetcher); comments (yt-comments-fetcher, scheduled by comment-decay-scheduler).
- Storing the uploads playlist id (yt-channel-resolver); backfill status (backfill-orchestrator); tiers (qualifier, registry-writer); deduplication (normalize-item).
- Deletions: a run reads only what is newer than the cursor, so absence is never read as deletion.

## 4. Users and consumers

- **Clients** experience it as "every video from my channels, even when YouTube's notification was lost" and as 90 days of history on a newly added channel; they never call it.
- **Ops** watches rotation lag, the missed-push share, key health and the DLQ, and can force a run of one channel.
- **Services**: fed by yt-channel-resolver, registry-writer, yt-pubsub-receiver and backfill-orchestrator; read by normalize-item, yt-video-details-fetcher, comment-decay-scheduler, backfill-orchestrator, raw-archiver and source-health-canary; governed by quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.yt-uploads-reconciler`, partitioned by `source_id`, emitted by the rotation scheduler inside this service (one leader replica elected through a Postgres advisory lock; scan period an environment variable well inside 24 hours). It selects `sources` rows with `platform = youtube`, `source_type = channel`, `route = green`, `tier != retired`, `health != blocked`, `backfill_status in (done, capped)`, a stored uploads playlist id and `next_poll_at <= now()`.

**Cadence.** Channels sit in the push tier because yt-pubsub-receiver covers them, so each gets one reconciliation every 24 hours, dormant ones included (open question 3). The reach tier (1: 100,000 or more subscribers or on a client's priority list; 2: 10,000 to 99,999; 3: below 10,000) is the secondary sort key and the quota priority; dormant runs at 3, `ops_force` and source-health-canary probes at 1, backfill at 5.

**Keeping every channel on rotation.** `next_poll_at = run_started_at + 24 h`, from the START of the last run, so cadence never drifts. Jobs are ordered by `next_poll_at` then reach tier, so no channel is skipped twice in a row; a channel is in at most one job at a time; a failed or denied job keeps its old `next_poll_at`, so runs deferred by the 95% mode are the most overdue when the budget resets and go first.

**Catch-up.** When `rotation_lag_seconds` exceeds 24 hours, the scheduler orders most-stale-first (oldest `last_success_at`) and raises `rotation_behind`. Runs read back to the cursor, so lateness costs freshness, not completeness.

**Lapsed lease.** yt-pubsub-receiver flags the channel on `source.events` (`updated`, `reason = push_lease_lapsed`); the scheduler emits a `reconciliation` job with `reason = lease_lapsed` at once, ignoring `next_poll_at`. Reading back to the cursor covers the whole lapse.

**Backfill on add.** A channel with `backfill_status = pending` is ignored by the scheduler. backfill-orchestrator sends a `backfill` job; this service pages back over 90 days (or the job's cap) at priority 5 and reports; backfill-orchestrator sets `done` or `capped` and `next_poll_at = now()`, handing the channel to the rotation.

**Comment decay.** New videos flow through normalize-item to `items.normalized`, where comment-decay-scheduler opens the series for yt-comments-fetcher (+6 h, +24 h, +3 d, +7 d, +30 d after first sight). A video first seen here starts it up to a day late.

### 5.2 Step by step

1. Consume a job (`source_id`, `kind`, `reason`, `attempt`; for backfill the window start and cap); read `sources` and the `cursors` row for (`source_id`, `yt-uploads-reconciler`); stop if `health = blocked`; note `run_started_at`.
2. Fetch the company app's API key from Supabase Vault for this job only.
3. Before each page ask quota-governor for 1 unit (`budget_tag = youtube_data_api`, bucket `ingest`, the job's priority); on wait-until requeue for that time; on deny count `quota_denied_total`, end the job, keep `next_poll_at`.
4. Call `playlistItems` (5.3) and follow page tokens until an item older than the cursor (backfill: the window start), the end of the playlist, or the backfill cap.
5. Check newer video ids with the listening-sdk idempotency helper (`youtube:post:<video id>`); write one `raw.items` message per id not yet stored. The video that set the cursor is checked but not counted.
6. Emit `first_sight` jobs to `jobs.yt-video-details-fetcher`, up to 50 ids each, carrying the originating kind so details are fetched at the same priority.
7. After Redpanda acknowledges everything: set the cursor to the newest `publishedAt` seen, `last_success_at`, `consecutive_errors = 0`, `last_polled_at` and (not for backfill) `next_poll_at`; emit `tier change` if a dormant channel uploaded. An interrupted run moves nothing; its retry restarts from the first page.
8. Publish to `jobs.completed`: `new_count` (first seen here), `seen_count` (newer than the cursor, already stored), `pages`, `cost_units`.

### 5.3 The call it makes

```
GET https://www.googleapis.com/youtube/v3/playlistItems
  ?part=contentDetails,snippet
  &playlistId=<uploads playlist id stored by yt-channel-resolver>
  &maxResults=50
  &pageToken=<token from the previous page; omitted on the first page>
```

Auth: the API key of our company YouTube app, injected per job, never logged. Cost: 1 unit a page. Page size: 50. Pagination: `pageToken`. The playlist id came from `channels.list` `contentDetails.relatedPlaylists.uploads` via yt-channel-resolver; this service never calls `channels.list`. To be confirmed in the pilot: the response field carrying the next token; that items come newest first, which the stop rule relies on; whether the rule compares `snippet.publishedAt` or `contentDetails.videoPublishedAt`; how the key is attached.

### 5.4 What it gets

Per item: video id, title, description, thumbnails, channel id and title, playlist position and publication timestamps. Example (field names as Google documents them, exact shape to be confirmed in the pilot; description and thumbnails omitted):

```json
{
  "kind": "youtube#playlistItem",
  "snippet": {
    "publishedAt": "2026-10-06T07:00:04Z",
    "channelId": "UCq0x7Rk2f9Hc4nT1bW8mZ3A",
    "title": "نشرة الصباح: أسعار صرف الدولار في بغداد اليوم",
    "position": 0,
    "resourceId": {"kind": "youtube#video", "videoId": "Xk3vQ9pL2aE"}
  },
  "contentDetails": {"videoId": "Xk3vQ9pL2aE", "videoPublishedAt": "2026-10-06T07:00:00Z"}
}
```

Enough for normalize-item to build the item and for keyword matching on title and description before details arrive. Not included: view, like and comment counts, duration, tags (yt-video-details-fetcher completes the item from `videos.list`); comments; anything older than the cursor on a daily run. Whether Shorts and live streams appear is to be confirmed in the pilot.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.yt-uploads-reconciler`; `source.events` (`added`, `updated` including `push_lease_lapsed`, `tier change`, `dormant`, `retired`); `sources` (with the uploads playlist id), `cursors`, `budgets` through quota-governor, `health` through the SDK canary hook; the key from Supabase Vault.

### 6.2 Writes

`raw.items`, one message per video not yet stored, envelope plus the item exactly as returned:

```json
{
  "envelope": {
    "platform": "youtube", "kind": "post", "route": "green", "vendor": null,
    "service": "yt-uploads-reconciler",
    "source_id": "a3d9f1c4-5e27-4b8a-9f60-2c1e7d4b8a93",
    "platform_id": "Xk3vQ9pL2aE",
    "idempotency_key": "youtube:post:Xk3vQ9pL2aE",
    "job_id": "01J9P4D2R7X5K8M1Q3V6T0B9ZC", "attempt": 1,
    "fetched_at": "2026-10-06T11:04:27Z",
    "retention_class": "youtube_30d_text",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/youtube/2026/10/06/yt-uploads-reconciler/000045.jsonl.zst",
    "partial": true,
    "metrics_observation": null
  },
  "payload": { "...": "the playlistItem from 5.4, unchanged" }
}
```

`jobs.yt-video-details-fetcher`, one job per up to 50 ids:

```json
{"job_id": "01J9P4D3A1M6W2C8F5H0K7N4QS", "source_id": "a3d9f1c4-5e27-4b8a-9f60-2c1e7d4b8a93", "kind": "first_sight", "origin_kind": "reconciliation", "post_ref": ["Xk3vQ9pL2aE", "b7Tz0qR4mWc"], "attempt": 1}
```

Also `jobs.completed`, `source.events` (`tier change`), `service_runs`, `dlq.yt-uploads-reconciler` after 5 failed attempts.

### 6.3 State

`cursors.cursor` = ISO `publishedAt` of the newest video already stored for the channel, plus `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`; bucket counters in `budgets`; per-channel missed-push history from the `jobs.completed` reports; in memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- YouTube Data API: 10,000 units a day by default, extensions only through Google's audit; `playlistItems.list` costs 1 unit a page of up to 50. No second key or project is used to add quota.
- Budget `youtube_data_api`, bucket `ingest` (may borrow from `comments`; `reserve` serves priority 1 only; `search` never borrows). The planning split gives the 1-unit endpoints about 4,000 to 5,000 units a day for 3.0M items a month; this service's share is to be measured in the pilot.
- Arithmetic: 1 unit per channel per day, plus 1 per further 50 new videos, plus catch-ups; a backfill costs 1 unit per 50 videos in its window, and the same again in `videos.list` calls. The channel count this supports is qualifier rule 5's YouTube quota cap, to be measured in the pilot.
- Modes: from 80% of the day's budget only priorities 1 to 3 run, so backfill waits; from 95% only 1 and 2, so Tier 3 and dormant runs wait for the reset.
- Cost: USD 0 per call; the cost is quota.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.yt-uploads-reconciler` and an alert fires.
- HTTP 401 and 403: mark the key `degraded`, stop the batch, alert; never rotate keys, projects or IPs around a block. A 403 meaning quota exhaustion, or concerning one playlist only (reasons to be confirmed in the pilot), is treated as exhaustion or as that channel's fault.
- HTTP 404 on the playlist: no retry; channel `health = degraded`, alert `uploads_playlist_missing`; ops re-runs yt-channel-resolver; a vanished channel is retired through registry-writer.
- Empty 200 on a channel known to upload: above 5% in 15 minutes source-health-canary flips `health = degraded`. No amber route exists, so `fallback_on` is never set.
- Schema change: payload archived by raw-archiver; normalize-item raises `schema_unknown` and parks the batch.
- Replays re-emit already-read pages; normalize-item deduplicates; a repeated `first_sight` id costs at most 1 unit per 50 ids.

## 9. Non-functional requirements

- Throughput: channel count and the video share of YouTube's 3.0M items a month to be measured in the pilot; a typical daily run is one page.
- Latency: a video whose push was lost reaches `raw.items` within 24 hours of publication plus fetch time; a lapsed channel runs as soon as its flag is consumed and quota allows.
- Idempotency: `youtube:post:<video id>`, shared by partial and full records, which normalize-item upserts into one item; replayable jobs.
- Scaling: stateless workers on partition lag; one leader scheduler.
- Security: key never in logs, envelopes or jobs; no account pools, no proxies; provenance on every message; YouTube Developer Policies, including audit at any time.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status,kind}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `yt_missed_push_ratio` (`new_count` ÷ (`new_count` + `seen_count`) over daily runs, rolling 24 hours; lapse catch-ups excluded so known lapses do not hide silent ones) and `yt_missed_video_delay_seconds` (`fetched_at` minus `publishedAt`). Alerts: `rotation_behind`; `missed_push_rising` (share above its baseline by a margin, both set in the pilot); `push_silent_channel` (every new video first seen here on consecutive runs, count set in the pilot; sent to yt-pubsub-receiver's owner for resubscription); `key_degraded`; `uploads_playlist_missing`; `dlq_nonempty`; `empty_200_rate`; `quota_deny_rate`. SLO: rotation lag below 24 hours for 99% of channels per day.

## 11. Dependencies

listening-sdk, quota-governor, yt-channel-resolver, yt-pubsub-receiver, backfill-orchestrator, yt-video-details-fetcher, normalize-item, comment-decay-scheduler, yt-comments-fetcher, source-health-canary, raw-archiver, registry-writer, Supabase Postgres and Vault, Redpanda; a YouTube Data API v3 project on the company app.

## 12. Risks and mitigations

- Push fails silently and freshness drops to 24 hours unnoticed: `missed_push_rising` and `push_silent_channel` surface it within a day.
- Channels outgrow quota (1 unit each a day is the floor): qualifier rule 5 caps channels by quota share and tells the client; extension through the audit; backfill yields first.
- A video lands behind the cursor (scheduled, premiered, private turned public) and is never read: open question 1; the pilot compares full first pages with the store on canary channels and adds an overlap, as fb-page-feed-poller does, if gaps appear.
- A push lands mid-run: the video may be written twice and counted as missed; videos stored first by yt-keyword-search count as pushed. Both biases are small and accepted.

## 13. Acceptance criteria

1. A run that started at 03:00:00 and took 3 minutes sets `next_poll_at` to 03:00:00 the next day.
2. With 200 fixture channels across reach tiers and dormant, against a simulated API for 72 hours, every non-retired channel runs once in every 24 hours.
3. A channel publishes 3 videos and the simulated hub delivers 1: the next run writes exactly 2 `raw.items` messages (`partial: true`), one `first_sight` job with those 2 ids, and reports `new_count = 2`, `seen_count = 1`.
4. With 120 unstored videos newer than the cursor, the run reads 3 pages, reports `cost_units = 3` and emits `first_sight` jobs of 50, 50 and 20 ids; with none newer, it reads 1 page.
5. When quota-governor denies page 2 of 3, cursor and `next_poll_at` stay unchanged and the retry loses no video.
6. A `push_lease_lapsed` event yields a `lease_lapsed` job before the next scan, and the run writes every video published during the simulated lapse.
7. A `backfill` job on a channel with 260 videos in 90 days and 40 older reads 6 pages at priority 5 and reports `new_count = 260`, `pages = 6`; no rotation job is emitted while `backfill_status` is `pending` or `running`.
8. After a day in the 95% mode, deferred priority 3 runs are emitted before every channel with a later `next_poll_at`.
9. With the hub dropping a configured share of notifications, `yt_missed_push_ratio` reports that share within test tolerance and `missed_push_rising` fires.
10. A simulated 429 backs off from 30 s to at most 15 min; after 5 attempts the job is in `dlq.yt-uploads-reconciler`; a 401 marks the key `degraded` and no further call uses it.
11. Every message carries `route`, `vendor`, `service`, `fetched_at`, `partial` and the source's `retention_class`; the key never appears in logs, envelopes or jobs.

## 14. Open questions

1. Are uploads listed strictly newest first, which timestamp should the stop rule use, and do scheduled or premiered videos land behind the cursor? To be confirmed in the pilot.
2. Do Shorts and live streams appear in the uploads playlist? To be confirmed in the pilot.
3. The rotation policy polls dormant sources weekly; this PRD keeps dormant channels daily (1 unit each) because a quiet channel's broken subscription is the hardest to notice. Confirm, or go weekly if quota is tight.
4. The lapse flag's shape must match yt-pubsub-receiver's PRD when it is written.
