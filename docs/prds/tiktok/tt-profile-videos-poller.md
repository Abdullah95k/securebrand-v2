# tt-profile-videos-poller

**Platform:** TikTok · **Route:** amber (optional, flag `TT_VENDOR_ROUTE`) · **Lane:** Fetch posts · **Owner:** Ingestion lead (Node) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

TikTok is the second-largest stream in the product: 7.5M of the 30.5M items a month at full scale, videos and the comments under them. Search finds a creator by accident; this service is what keeps watching that creator afterwards. It reads the latest videos of every registered TikTok creator (the brands, outlets, public figures and influencers the qualifier admitted at 2,000 followers or verified) on the tier rotation, so a watched creator's new video is in the product within one tier interval whether or not any keyword matched it.

Plainly: TikTok has no green route to third-party content. Research Tools are academic and non-profit only, the Commercial Content API covers EU paid ads, and the Mentions API is for badged Marketing Partners. So this service is optional, runs only behind `TT_VENDOR_ROUTE` (off | tikhub | ensembledata), is disclosed in the provenance statement to clients, and is excluded from government contracts. Without it, TikTok coverage is limited to what tt-keyword-search and tt-hashtag-feed-poller happen to surface and to client-authorised accounts (tt-client-videos-fetcher): no competitor tracking, no outlet monitoring, no creator timelines, and no videos for tt-video-comments-fetcher and tt-video-stats-refresher to work on from registered creators.

## 2. Objective (the end state this service delivers)

Every registered TikTok creator with an active tier is checked for new videos on its tier's cadence, every new video reaches `raw.items` within one tier interval of publication with amber provenance, and the cursor moves only after Redpanda has acknowledged the batch. Target: rotation lag below one tier interval for 99% of creators per day, staleness p95 within the tier maximum (1 h, 6 h, 24 h), zero jobs lost.

## 3. Scope

### In scope

- Rotation scheduling of every amber TikTok creator by tier (1, 2, 3, push reconciliation, dormant) and execution of the jobs on `jobs.tt-profile-videos-poller`.
- Incremental reads of the creator's videos from the cursor; the 90-day backfill job emitted by backfill-orchestrator (TikTok has no separate backfill service).
- Writing `raw.items` (kind `post`) with first-sight counts in the payload; advancing `cursors`; dormant promotion; `rotation_behind` catch-up.
- TikHub and EnsembleData adapters selected by the flag value, with vendor fallback.

### Out of scope

- Finding creators (tt-keyword-search, tt-hashtag-feed-poller), resolving them (tt-user-resolver) and admitting them (qualifier, registry-writer).
- Comments and replies (tt-video-comments-fetcher); the +24 h and +7 d refreshes (tt-video-stats-refresher); a client's own authorised account (tt-client-videos-fetcher, green).
- Individuals below the creator threshold: never polled, never backfilled.
- Deduplication (normalize-item), keyword matching (keyword-matcher), tier decisions (qualifier, registry-writer).

## 4. Users and consumers

- **Clients** experience it as "new videos from the creators I watch, never older than my tier allows", with the amber label visible. They never call it.
- **Ops** watches rotation lag, vendor health and the DLQ, can force a poll of one creator, and flips the flag.
- **Downstream:** normalize-item (consumes `raw.items`), comment-decay-scheduler (opens comment and metrics series from `items.normalized`), tt-video-stats-refresher (uses the first-sight counts as its baseline), raw-archiver, source-health-canary, quota-governor, backfill-orchestrator.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.tt-profile-videos-poller`, partitioned by `source_id`, emitted by the rotation scheduler inside this service (one leader replica elected through a Postgres advisory lock; the scan period is an environment variable well inside 60 minutes). It selects `sources` rows with `platform = tiktok`, `source_type = creator`, `route = amber`, `health != blocked`, `backfill_status in (done, capped)` and `next_poll_at <= now()`, and emits nothing while `TT_VENDOR_ROUTE = off`. A creator watched only by government clients is never selected.

**Cadence by tier.** Tier 1 (100,000 or more followers, or on a client's priority list): every 60 minutes. Tier 2 (10,000 to 99,999): every 6 hours. Tier 3 (below 10,000): every 24 hours. Push (client-authorised creators whose videos arrive hourly from tt-client-videos-fetcher): no rotation polling, one reconciliation poll every 24 hours, skipped where the client's contract excludes amber data. Dormant (no video in 30 days): weekly; a new video promotes the creator back to its reach tier through `source.events` (`tier change`). Retired: never polled.

**Keeping every creator on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + interval`), so cadence is fixed and does not drift with fetch time. Jobs are emitted ordered by `next_poll_at` then by tier, so an overdue Tier 3 creator is not pushed aside by Tier 1 and no creator is skipped twice in a row. A creator is in at most one job at a time (partition key). A failed job keeps its old `next_poll_at`, making that creator first in line on the next scan.

**Catch-up.** `rotation_lag_seconds` is now minus `next_poll_at` of the most overdue creator. Above one interval the scheduler switches to most-stale-first and raises `rotation_behind`. Every poll reads from the cursor, so a late poll still returns everything since the cursor: being behind costs freshness, not completeness.

**Budget stretching.** When quota-governor reports 80% of the monthly `tt_vendor` budget consumed, it may stretch Tier 1 and Tier 2 intervals, never beyond daily. Tier 3 is already daily and is not stretched. A stretched creator is marked in the metrics so the staleness SLO is read against the stretched interval.

**Backfill on add.** A new creator arrives with `backfill_status = pending`. backfill-orchestrator emits a `kind = backfill` job to this queue; the service pages back through the creator's videos until 90 days or the vendor's cap, whichever is smaller, and reports `oldest_seen` and `pages`. backfill-orchestrator sets `done` or `capped` and `next_poll_at = now()`; only then does the rotation pick the creator up.

**Hand-off.** Each new video flows `raw.items` → normalize-item → `items.normalized`, where comment-decay-scheduler opens the comment series for tt-video-comments-fetcher (+1 h, +6 h, +24 h, +3 d, +7 d) and the metrics jobs for tt-video-stats-refresher (+24 h, +7 d).

### 5.2 Step by step

1. Consume a job (`source_id`, `kind` = rotation | reconciliation | backfill | ops_force, `attempt`); read the `sources` and `cursors` rows (`source_id`, `tt-profile-videos-poller`); stop if `health = blocked`.
2. Read `TT_VENDOR_ROUTE` and route health: use the flag's vendor, or the alternate TikTok vendor with a row in `vendor_keys` while `fallback_on` is in force. Flag off: count `flag_off` and stop.
3. Ask quota-governor for allowance under `budget_tag = tt_vendor` (sub-counter `profile_videos`); `wait-until` requeues for that time, `deny` requeues with `attempt + 1` and counts `quota_denied_total`.
4. Call user posts by cursor, newest first, 20 videos a page, following the vendor's page cursor until a non-pinned video at or before the stored cursor appears, or the pages run out. Pinned videos sit at the top of a profile regardless of date, so they never trigger the stop.
5. Write one `raw.items` message per video newer than the cursor; raw-archiver lands the batch under `raw/amber/tiktok/<yyyy>/<mm>/<dd>/tt-profile-videos-poller/`.
6. After Redpanda acknowledges: set `cursor` to the newest `create_time` stored, `last_success_at`, `consecutive_errors = 0`, `last_polled_at` and `next_poll_at`; emit `tier change` if a dormant creator posted.
7. Record the metrics of section 10 and the request count into `budgets`.

### 5.3 The call it makes

TikHub, endpoint family **user posts by cursor** (exact path and parameter names to be confirmed in the pilot):

```
user posts by cursor
  creator identifier: the id the endpoint expects (to be confirmed in the pilot)
  cursor:             the vendor's page cursor, empty on the first page
  page size:          20 videos
  auth:               TikHub API key from Supabase Vault (vendor_keys), per job
```

EnsembleData: the equivalent user-posts endpoint behind the flag value `ensembledata`; paging semantics to be verified in the pilot. Limits: 20 items a page, 10 requests a second per endpoint; TikHub bills only on HTTP 200. The vendor's page cursor lives only inside one poll; the stored cursor is our own `create_time` high-water mark, so switching vendor never loses the creator's position.

### 5.4 What it gets

Per video, as the vendor returns it (illustrative; field names to be confirmed in the pilot):

```json
{
  "id": "7421538806219533573",
  "desc": "افتتاح فرع جديد في البصرة #البصرة #عروض",
  "create_time": 1759734729,
  "author": {"id": "6812345678901234567", "unique_id": "basra.store", "verified": false},
  "statistics": {"play_count": 18420, "digg_count": 1310, "share_count": 87, "comment_count": 142},
  "is_pinned": false,
  "hashtags": ["البصرة", "عروض"]
}
```

The four counts are the first-sight observation: the envelope marks them `metrics_observation = first_sight`, and tt-video-stats-refresher takes its +24 h and +7 d readings against them. Not obtained: comment text (tt-video-comments-fetcher), the viewers, likers or sharers, deleted or private videos, and anything about other users beyond the caption text.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.tt-profile-videos-poller`; `sources`, `cursors`, `clients` (government flag, contract terms), `vendor_keys`, route health and `canary_targets`, `budgets` through quota-governor; the flag `TT_VENDOR_ROUTE`; `source.events` (`added`, `tier change`, `retired`, `fallback_on`, `fallback_off`) to refresh its view of the rotation.

### 6.2 Writes

`raw.items`, one message per video, envelope plus the record exactly as returned:

```json
{
  "envelope": {
    "platform": "tiktok", "kind": "post", "route": "amber", "vendor": "tikhub",
    "service": "tt-profile-videos-poller",
    "source_id": "3d8a51c2-7e04-4b9f-8c16-2a9e5d70f4b8",
    "platform_id": "7421538806219533573",
    "idempotency_key": "tiktok:video:7421538806219533573",
    "job_id": "01J9N3A8Q2W6C5Y1T4R7K0D9ZE", "attempt": 1,
    "fetched_at": "2026-10-06T09:15:42Z",
    "retention_class": "vendor_agreed",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/amber/tiktok/2026/10/06/tt-profile-videos-poller/000045.jsonl.zst",
    "metrics_observation": "first_sight"
  },
  "payload": { "...": "the video object from 5.4, unchanged" }
}
```

Also `source.events` (`tier change`), `service_runs`, `dlq.tt-profile-videos-poller` after 5 failed attempts.

### 6.3 State

`cursors.cursor` = `create_time` (ISO, UTC) of the newest stored video plus its id, with `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`; `budgets` counters under `tt_vendor`; in memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- Price: TikHub USD 0.50 to 1.00 per 1,000 requests by daily volume tier; EnsembleData at the team's contract price. 10 requests a second per endpoint is 864,000 a day, far above the rotation's need, so the limiter smooths bursts after a catch-up rather than rationing.
- Requests per creator per day: Tier 1 24, Tier 2 4, Tier 3 1, dormant one in seven, push 1, plus one more page for every 20 videos beyond the first page in a poll. Creators per tier: to be measured in the pilot.
- Route budget: about USD 280 to 560 a month for discovery plus comments at full scale across all amber TikTok services, which at the tier prices implies about 560,000 requests a month. This service's share: to be measured in the pilot.
- Budget tag `tt_vendor` (amber), sub-counter `profile_videos`; one tag for all amber TikTok services, so a comment surge cannot starve this sub-counter. At 80% of the monthly budget intervals stretch, never beyond daily.

## 8. Failure handling and fallback

- HTTP 429 and vendor rate-limit responses: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.tt-profile-videos-poller` and an alert fires.
- HTTP 401 and 403: mark the vendor key and route `degraded`, stop the batch, alert; never rotate accounts or IPs around a block.
- Empty 200 above 5% of calls in 15 minutes: source-health-canary flips the route to `degraded` and, with the flag on, `fallback_on`; the next job uses the alternate vendor until `fallback_off`. A creator the vendor reports as private or not found is not an empty 200: it is marked `health = blocked` with a note, checked weekly, and left to decay (qualifier rule 9).
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: cursors move only after acknowledgement; a replayed job re-emits the same videos and normalize-item deduplicates them.

## 9. Non-functional requirements

- Throughput: TikTok's full-scale share is 7.5M items a month; the video share and creator count are to be measured in the pilot.
- Latency: a video visible to the vendor reaches `raw.items` within its tier interval plus fetch time; the vendor's own lag is to be measured in the pilot.
- Idempotency: `tiktok:video:<id>`; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag; one leader scheduler.
- Security: keys from Supabase Vault per job, never logged; no account pools, no proxies; individuals are never profiled (TikTok's Developer Terms forbid databases on individuals); provenance on every message; retention `vendor_agreed`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `creators_in_rotation{tier}`, `flag_off_total`, `vendor_empty_200_total` and `creators_blocked`. Alerts: `rotation_behind`, `vendor_degraded`, `dlq_nonempty`, `empty_200_rate`, `quota_deny_rate`. SLO: rotation lag below one tier interval for 99% of creators per day.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, comment-decay-scheduler, tt-video-comments-fetcher, tt-video-stats-refresher, backfill-orchestrator, tt-client-videos-fetcher, qualifier and registry-writer, Supabase Postgres and Vault, Redpanda, TikHub and EnsembleData contracts.

## 12. Risks and mitigations

- TikHub's ownership is only weakly cleared: contract review before the pilot; EnsembleData as the ready alternate.
- Vendor lists may omit or lag videos: disclosed in provenance; the stats refresher's deleted-video signal and the next poll expose gaps.
- Cost growth with creator count: the per-source spend cap and the 80% stretch; over the cap new creators queue by reach and the client is told.
- A client or regulator objects to amber data: the flag turns the service off in one change, and government contracts never see it.

## 13. Acceptance criteria

1. A Tier 1 creator whose poll started at 09:00:00 has `next_poll_at = 10:00:00` even when the fetch took 4 minutes.
2. With 100 fixture creators across three tiers against a simulated vendor for 24 hours, no creator's `rotation_lag_seconds` exceeds its tier interval.
3. A pinned video older than the cursor at the top of the list does not stop the read: the newer videos behind it are fetched.
4. Replaying one job twice yields two `raw.items` messages with the same `idempotency_key`; normalize-item stores one video.
5. The cursor does not advance when the Redpanda produce fails; the next attempt re-emits the batch.
6. With `TT_VENDOR_ROUTE = off`, no vendor call is made in a day: the scheduler emits no job, and a job already queued ends `skipped_flag_off` at its start, never as an attempt (ADR-0050, ADR-0017).
7. With the flag set to `tikhub` and then `ensembledata`, the same creator yields messages that pass the normalize-item schema, `vendor` set accordingly, and no video is re-emitted as new after the switch.
8. A simulated 429 backs off from 30 s to at most 15 min with `attempt + 1`; after 5 attempts the job is in `dlq.tt-profile-videos-poller` and an alert fired.
9. At 80% of the monthly budget a Tier 1 interval stretches but never beyond 24 hours; a Tier 3 interval is unchanged.
10. A creator watched only by a government client is never emitted as a job; a creator with `backfill_status = pending` is never emitted as a rotation job.
11. Every `raw.items` message carries `route = amber`, `vendor`, `service`, `fetched_at`, `retention_class = vendor_agreed` and `metrics_observation = first_sight`.

## 14. Open questions

1. How far back the vendor's user-posts listing reaches (the backfill cap), and the name of its pinned-video flag: to be confirmed in the pilot.
2. Do TikHub and EnsembleData return identical video ids and `create_time` precision? If not, the cursor needs a small overlap to survive a vendor switch.
3. Should the daily reconciliation of client-authorised creators run through the amber vendor at all, or is the hourly Display API read treated as complete? Proposed: run it only where the client's contract allows amber data.
