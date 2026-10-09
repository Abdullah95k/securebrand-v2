# yt-text-purger

**Platform:** YouTube · **Route:** green · **Lane:** Support · **Owner:** Backend lead, compliance and retention · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

All YouTube collection runs on official API calls under one company API project. YouTube's Developer Policies let us keep raw comment text for no longer than 30 days unless we refresh it from the API, and YouTube may audit us at any time. A comment still held on day 31 is a breach. A breach puts the API project at risk (key cut, quota extension refused at audit), and if that happens every client loses YouTube at once.

yt-text-purger enforces that rule every day. When a comment, reply or video text reaches 30 days, it refreshes the text if a client still watches the video, pays for refresh and quota allows. Otherwise it deletes the text and keeps the scores derived from it. Without this service, text would build up in ClickHouse, the search index, archives and caches until a YouTube audit found it. With it, clients keep sentiment, topics and ten-year trends, and every run leaves proof that the rule held.

## 2. Objective (the end state this service delivers)

No YouTube comment, reply, video title or description text in ClickHouse, the Arabic text index, raw or Parquet archives or caches comes from a fetch older than 30 days. Text that a client pays to keep is refreshed while quota allows. Derived scores are kept 36 months and aggregates ten years. Target: zero text past 30 days at the end of every run (`oldest_remaining_age_seconds` below 2,592,000), every audit `pass`, the confirmation written before retention-purger's next sweep, and an offboarded client's YouTube text deleted in the run that sees the offboarding.

## 3. Scope

### In scope

- The `youtube_30d_text` clock for comments and replies (ClickHouse `comments`) and for video title and description (`items`).
- The refresh-or-delete decision, `refresh` jobs to the three YouTube fetchers, and `deletions` with reason `retention` and scope `text_only`.
- YouTube text at client offboarding, and the 36-month end of derived scores.
- Verification, plus one audit record per run.

### Out of scope

- Executing deletions (deletion-propagator, with raw-archiver for object rewrites) and calling the YouTube API (the fetchers).
- Comment series and client-requested refreshes (comment-decay-scheduler), and `platform_sync` deletions (the fetchers).
- Other retention classes and other platforms' offboarding (retention-purger).
- Aggregates: kept ten years, never selected and never recomputed here.

## 4. Users and consumers

- **retention-purger** sends the daily job and reads the audit row as confirmation.
- **Ops and the compliance owner** receive `yt_text_backlog` and show the audit rows to YouTube on request.
- **Clients** with refresh in their plan keep verbatim comments past day 30. Other clients see scores and trends, with the comment marked as expired.
- **Consumers** of its output: deletion-propagator, yt-comments-fetcher, yt-replies-fetcher, yt-video-details-fetcher and alert-evaluator.

## 5. How it works

### 5.1 Trigger and rotation

The service has three triggers:

1. retention-purger's daily `retention_sweep` job on `jobs.yt-text-purger`. The job carries `run_id`, `cutoff` (now − 30 days) and `next_sweep_at`.
2. Client offboarding. This arrives as a `remove_client` decision on `registry.decisions` for a YouTube source (retention-purger emits one per `client_sources` row), or as any `clients` row in `offboarding` found at the start of a run.
3. An `ops_force` job.

There is no tier rotation. Each item has its own deadline, `fetched_at` + 30 days, and a run covers every deadline up to `next_sweep_at` + `DELETE_MARGIN`. Every run recomputes its work from ClickHouse, so the next run repairs a missed one. For catch-up, text already past its deadline is deleted first and never refreshed. Backfilled comments carry their fetch time, so their clock starts at fetch. A Postgres advisory lock keeps a single leader.

### 5.2 Step by step

1. Take the lock and record the run start S in `service_runs`.
2. Run query A (5.3).
3. Emit `deletions` for items whose deadline falls before S + `REFRESH_LEAD`.
4. Decide the remaining videos in priority order, as `refresh` jobs or `deletions`.
5. Run the confirm loop until every due item is refreshed or deleted.
6. Handle offboarding and 36-month ends.
7. When `deletion_requests` shows every emitted deletion as `completed`, run verification.
8. Write the audit row, set the `cursors` row (`service = yt-text-purger`, cursor = cut-off) and release the lock.

### 5.3 The call it makes

This service makes no YouTube call. The fetchers make the calls and spend the units. Three environment variables control timing, each with an initial value to be measured in the pilot:

- `REFRESH_LEAD`: the time a refresh needs.
- `DELETE_MARGIN`: the time a `text_only` deletion needs to complete.
- `CONFIRM_INTERVAL`: how often the confirm loop wakes.

**Query A (the due set).** Query `comments` (comments and replies) and `items` (kind `video`, where `text` holds title and description) with `FINAL`, filtered on:

- `retention_class = 'youtube_30d_text'`
- text present
- `fetched_at + INTERVAL 30 DAY <= next_sweep_at + DELETE_MARGIN`

It returns `item_id`, `source_id`, video id, thread id, reply count and `fetched_at`. Deadline = `fetched_at` + 30 days. Results are grouped by video.

**Decision per video** (the first match wins):

1. If the earliest deadline falls before S + `REFRESH_LEAD`, delete.
2. If the video is not under active watch, delete. Active watch means all of the following hold:
   - the video's `source_id` (its channel, or the keyword-rule source that found it) has a `client_sources` row for a client with `status = active` and the `yt_text_refresh` plan entitlement;
   - the source is not `retired`;
   - the source's `health` (set by source-health-canary) is `ok`.
3. Ask quota-governor on `youtube_data_api`, bucket `comments` (`ingest` for video metadata), at priority 3, for this estimate:
   - 1 unit per 100 threads (`commentThreads.list`, `maxResults=100`);
   - 1 unit per `comments.list` page for each due thread above 5 replies;
   - 1 unit per 50 videos (`videos.list`).

   The answer decides the outcome:
   - Allow: refresh.
   - Wait-until earlier than the earliest deadline minus `REFRESH_LEAD`: ask again at that time.
   - Wait-until later than that, or deny: delete.

Videos are taken by client priority (tier 1 and priority-list sources first), then newest first. When the bucket runs dry, the oldest material is deleted.

**Refresh jobs** (`kind = refresh`):

- **Comment threads:** one job per video on `jobs.yt-comments-fetcher`, listing the due thread ids. Replies in threads with 5 or fewer replies come back with their thread.
- **Long reply threads:** one job per thread above 5 replies on `jobs.yt-replies-fetcher`.
- **Video metadata:** 50 videos to a job on `jobs.yt-video-details-fetcher`.

Each job carries `post_ref`, `thread_ids`, `run_id`, `must_finish_by` (earliest deadline minus `DELETE_MARGIN`) and `refresh_for_client_ids`. The fetcher drops a job that is past `must_finish_by`, or whose clients are no longer active. The refreshed version reaches ClickHouse through store-writer with new text, new metadata and a new `fetched_at`; that is what resets the clock. An item the API no longer returns is not reset (the fetcher emits `platform_sync` when the API answer is complete). A comment-decay-scheduler series job for the same video runs first on the same `source_id` partition. Series fetches read only newer comments and reset no clock.

**Confirm loop.** On each wake, the service re-runs query A limited to `fetched_at < S`, since anything refreshed in this run is newer. It then deletes every item whose deadline minus `DELETE_MARGIN` falls before the next wake. No per-item state is kept.

**Deleting the text.** The service emits one `deletions` message per `source_id` and chunk, with reason `retention`, scope `text_only`, mode `purge_text`, `due_at` = the earliest deadline and `fetched_before` = S. deletion-propagator must do all of the following:

1. Write a new ReplacingMergeTree version with `text`, `text_norm` and the author reference null and derived columns unchanged, only over versions fetched before `fetched_before`, so a late refresh survives.
2. Force the merge of the touched monthly partitions (`OPTIMIZE TABLE comments PARTITION <yyyymm> FINAL`) so that no superseded version keeps text.
3. Remove the item from the Arabic text index.
4. Purge caches.
5. Have raw-archiver rewrite the affected `raw/green/youtube/…` batches and `archive/youtube/<yyyy>/<mm>/` partitions without text. A refreshed item always has a newer copy, so raw-archiver can strip whole fetch days older than 30 days.

Derived scores (sentiment, topics, entities, keyword-hit ids) stay, and aggregates are not recomputed. `deletion_id` = `del:retention:text_only:<sha256(target, class, cut-off day)>`.

**Offboarding.** For each video whose active watch rests only on the offboarding client, the service emits `deletions` with reason `client_offboarding`, scope `text_only` and `client_id` set. These cover all of that video's text, whatever its age. A video that another active client watches keeps its own clock.

**36-month end.** For items whose text is already purged and whose last `fetched_at` is older than 36 months, the service emits `deletions` with reason `retention`, scope `derived` and the new mode `purge_derived`. deletion-propagator then removes the item row, its `analysis` rows and its keyword-hit ids. `aggregates_hourly` stays and is not recomputed.

**Video metadata** follows the same rule, to be confirmed with the YouTube policy text in the pilot.

### 5.4 What it gets

The service gets ids, `source_id`, video and thread ids, reply counts, `fetched_at` and whether text is present; client status and entitlements; quota answers; and deletion completion status. It never reads comment or video text.

## 6. Inputs and outputs

### 6.1 Reads

- Topics: `jobs.yt-text-purger` and `registry.decisions` (`remove_client`).
- Postgres: `clients`, `client_sources`, `sources` (`tier`, `health`), `deletion_requests` and `retention_classes`.
- ClickHouse: `items`, `comments` and `analysis` (select and count only).
- Other: quota-governor answers and raw-archiver manifests.

### 6.2 Writes

- Topics: `deletions` (keyed by `source_id`), `jobs.yt-comments-fetcher`, `jobs.yt-replies-fetcher` and `jobs.yt-video-details-fetcher`.
- Postgres: `retention_audit`, `service_runs` and `cursors`.

Example `deletions` message:

```json
{
  "deletion_id": "del:retention:text_only:9a4e1c7b2d8f3a6e0b5c9d2f7a1e4b8c3d6f0a9e2b5c8d1f4a7e0b3c6d9f2a5e",
  "reason": "retention", "scope": "text_only", "mode": "purge_text",
  "retention_class": "youtube_30d_text",
  "source_id": "2d7e9b41-5c3a-4f8e-b1d6-7a0c9e3f5b28",
  "target": {"platform": "youtube", "kind": "comment", "video_id": "dQ3x7Lk9PzA",
             "item_ids": ["e68d6e4b-56fd-52b1-9f72-f7018e8fe162", "3ed679f4-bac6-52e0-ba34-8d00cf816ef4"],
             "fetched_before": "2026-10-06T02:00:00Z"},
  "client_id": null,
  "requested_by": "yt-text-purger", "run_id": "01J9P9C6E2G8J4L0N5Q1S7U3WY",
  "parent_run_id": "01J9P8A3V5N7B2D4F6H0K1M9QS",
  "signal_at": "2026-10-06T02:00:00Z", "due_at": "2026-10-06T19:42:10Z",
  "emitted_at": "2026-10-06T02:07:31Z"
}
```

Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

The audit record is a `retention_audit` row. retention-purger treats this row as the delegate's confirmation, then runs its own verification. A run passes only when `failures` (items that ended neither refreshed nor completely deleted) is 0 and every verification count is 0. `refresh_missed` counts items whose refresh did not land in time; those items fell back to deletion.

```json
{
  "run_id": "01J9P9C6E2G8J4L0N5Q1S7U3WY", "parent_run_id": "01J9P8A3V5N7B2D4F6H0K1M9QS",
  "executor": "yt-text-purger", "trigger": "retention_sweep",
  "class": "youtube_30d_text", "clock": "30 days", "cutoff": "2026-09-06T02:00:00Z",
  "started_at": "2026-10-06T02:00:00Z", "finished_at": "2026-10-07T01:31:44Z",
  "candidates": 104212, "refreshed": 18840, "text_deleted": 85372,
  "refresh_missed": 312, "failures": 0, "derived_deleted": 0,
  "emitted": 1873, "completed": 1873,
  "verification": {"query": "SELECT count() FROM comments WHERE retention_class = 'youtube_30d_text' AND text IS NOT NULL AND fetched_at < now() - INTERVAL 30 DAY",
                   "result": 0, "executed_at": "2026-10-07T01:30:02Z"},
  "oldest_remaining_age_seconds": 2548800,
  "status": "pass", "holds": []
}
```

Verification runs without `FINAL` so that superseded versions count. The same count runs on `items`.

### 6.3 State

The service keeps the leader lock, the run row, the cursor and the audit rows. There is no per-item state, because the confirm loop recomputes from ClickHouse.

## 7. Limits, quotas and cost

- The YouTube Data API is paid in quota units (10,000 a day by default), not USD. The fetchers spend them on `youtube_data_api`.
- At full scale, YouTube brings 3.0M items a month, so about 100,000 items reach 30 days each day.
- Refresh lower bound: 100,000 comments at 100 per page is about 1,000 units a day. Refreshed text comes due again every 30 days, so each further month kept under refresh adds about 1,000 units a day. By the tenth month the bound uses the whole default quota. Real pages are rarely full, so actual use is to be measured in the pilot. This is why refresh is an entitlement at priority 3, its bucket share is set in quota-governor, and deletion is the default.
- Video metadata refresh costs 1 unit per 50 videos.
- Deletion load (partition merges, object rewrites) is to be measured in the pilot.

## 8. Failure handling and fallback

- **Quota deny, or a wait past the deadline:** delete.
- **Fetcher failures:** the fetcher retries per the conventions (backoff from 30 s to 15 min, 5 attempts, then `dlq.<fetcher>`). The confirm loop deletes regardless.
- **401 or 403 on the API project:** the fetchers mark the route `degraded`. Health is then not `ok`, so all due text is deleted.
- **ClickHouse or Postgres unavailable:** the run stops and retries within the period. A deadline that passes raises `yt_text_backlog`, and the next run deletes past-due text first.
- **Redpanda produce failure:** the chunk is retried with the same `deletion_id`. After 5 attempts it goes to `dlq.yt-text-purger` and an alert fires.
- **Deletion open near its `due_at`:** `yt_text_at_risk` fires.
- **Nonzero verification:** the audit is `fail`, `yt_text_backlog` goes to ops and the ids are re-emitted.
- **Leader dies:** another replica takes the lock and recomputes.
- **No amber route:** YouTube has none, so there is no fallback.

## 9. Non-functional requirements

- Throughput: about 100,000 decisions a day at steady state. A run finishes before `next_sweep_at`. Query A is pruned on `fetched_at`. Timings are to be measured in the pilot.
- Latency: every `text_only` deletion completes before its item's deadline.
- Idempotency: deterministic `deletion_id`. Fetchers deduplicate refresh jobs on `post_ref` + `run_id`.
- Scaling: one leader. The decision pass can be sharded by `source_id`.
- Security: the service selects nullness, never text. Logs and messages carry ids only. Its ClickHouse role is read-only, and `retention_audit` is append-only.

## 10. Metrics and alerts

Metrics:

- `yt_text_due_total{kind}`, `yt_text_refreshed_total{kind}`, `yt_text_deleted_total{reason}`
- `yt_refresh_missed_total`, `yt_refresh_quota_denied_total`
- `yt_text_oldest_age_seconds`, `yt_text_past_clock`
- `yt_derived_deleted_total`, `run_duration_seconds`, `dlq_total`

Alerts:

- `yt_text_backlog`: any text past 30 days; pages ops.
- `yt_text_at_risk`: a deletion still open within `DELETE_MARGIN` of its deadline.
- `run_missed`, `audit_failed`, `dlq_nonempty`.

SLO: `yt_text_past_clock` = 0.

## 11. Dependencies

- Infrastructure: listening-sdk, Redpanda, Supabase Postgres and ClickHouse.
- Retention chain: retention-purger and deletion-propagator.
- Storage: raw-archiver, store-writer and aggregator. Aggregator builds from derived scores only, so purges leave aggregates unchanged.
- YouTube fetchers: yt-comments-fetcher, yt-replies-fetcher and yt-video-details-fetcher.
- Scheduling and control: comment-decay-scheduler, quota-governor, source-health-canary and alert-evaluator.

## 12. Risks and mitigations

- **A superseded ReplacingMergeTree version still holds text.** Mitigation: a forced partition merge, and verification without `FINAL`.
- **A refresh silently never lands.** Mitigation: the confirm loop deletes by deadline.
- **A purge overwrites a fresh refresh.** Mitigation: the `fetched_before` guard.
- **Refresh demand outgrows quota.** Mitigation: entitlement, priority 3, ordering and delete-by-default.
- **We misread the policy** (video metadata, the derived-score anchor, statistics). Mitigation: conservative defaults, confirmed in the pilot.

## 13. Acceptance criteria

1. Use fixtures with deadlines before S + `REFRESH_LEAD`, inside the window and after `next_sweep_at` + `DELETE_MARGIN`, varied by watch, entitlement, health and quota answer. Every fixture is decided exactly as 5.3 says, and items outside the window are untouched.
2. A refreshed comment has new text and a new `fetched_at`, and is absent from the next run's due set.
3. When a refresh job ends in DLQ, its items' text is deleted before the deadline. The audit counts them in `refresh_missed` and still shows `pass`.
4. After a run, all of the following hold:
   - the verification queries on `comments` and `items` without `FINAL` return 0;
   - a text-index search for purged ids returns nothing;
   - cache lookups miss;
   - no object under `raw/green/youtube/` or `archive/youtube/` from a fetch day older than 30 days contains text.
5. Purged comments still return sentiment, topics, entities and keyword-hit ids, and `aggregates_hourly` is identical before and after the run.
6. A refresh that lands between the decision and the purge keeps its text.
7. Running the same job twice gives identical `deletion_id`s, no duplicate refresh jobs and one completion per id.
8. A 31-day-old text is deleted, not refreshed. `yt_text_backlog` fires and the audit is `fail`.
9. Offboarding client A deletes all A-only YouTube text in that run, whatever its age. A video shared with active client B keeps its text. A pending refresh job for A alone is dropped.
10. An item with purged text and a last `fetched_at` older than 36 months loses its item, `analysis` and keyword-hit rows, and aggregates are unchanged. A 35-month item is untouched.
11. A video without entitlement has its title and description nulled at the deadline. With entitlement and quota allowance, it is refreshed through yt-video-details-fetcher with a new `fetched_at`.
12. Every run writes exactly one `retention_audit` row with `parent_run_id` before `next_sweep_at`, and retention-purger raises no `delegate_unresponsive`. Killing the leader mid-run produces no duplicates and no missed items.

## 14. Open questions

1. Policy text, to be confirmed in the pilot:
   - Does the 30-day rule cover video title and description (assumed yes)?
   - Does it cover statistics in `metrics_timeseries`?
   - What anchors the 36-month clock? The design uses the last `fetched_at`.
2. Interface changes to agree:
   - The `refresh` job kind and the fields `must_finish_by` and `refresh_for_client_ids` (addendum and the fetcher PRDs).
   - The `fetched_before` guard, forced merge and `purge_derived` mode (deletion-propagator).
   - The new `retention_audit` columns.
   - The offboarding hand-off (retention-purger's next revision).
3. Where does the `yt_text_refresh` entitlement live on `clients`, and what share of the `comments` bucket may refresh use?
4. Should the YouTube Parquet archive drop text at write time, so the daily rewrite is no longer needed?
