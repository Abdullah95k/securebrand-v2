# tt-video-stats-refresher

**Platform:** TikTok · **Route:** amber (optional, flag `TT_VENDOR_ROUTE`) · **Lane:** Comments and stats · **Owner:** Ingestion lead (Node) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

When tt-profile-videos-poller, tt-keyword-search or tt-hashtag-feed-poller first sees a video, its counts are almost always small: the video is minutes or hours old. What a client wants to know is what happened next: did the offer video take off, did the ministry's announcement get shared, did the competitor's clip flop. tt-video-stats-refresher answers that. It re-reads each video twice after first sight, at +24 h and +7 d, and writes views, likes, shares and comment counts to `item.metrics`.

Plainly: TikTok has no green route to third-party content. Research Tools are academic and non-profit only, the Commercial Content API covers EU paid ads, and the Mentions API is for badged Marketing Partners. So this service is optional, runs only behind `TT_VENDOR_ROUTE` (off | tikhub | ensembledata), is disclosed in the provenance statement to clients, and is excluded from government contracts. Without it every TikTok video stays frozen at its first-sight counts: engagement rates are understated, share of voice and creator benchmarks rest on newborn numbers, and nobody notices when a video disappears. The same call is the only way the amber route learns that a video was deleted.

## 2. Objective (the end state this service delivers)

Every TikTok video the amber route has seen gets exactly two observations, at +24 h and +7 d after first sight, each written once to `item.metrics` with its true observation time, and a video that has disappeared is reported for deletion. Target: 95% of observations written within one hour of `due_at` (initial value, to be tuned in the pilot), zero duplicate observations, zero jobs lost.

## 3. Scope

### In scope

- Executing `metrics` jobs from `jobs.tt-video-stats-refresher`, emitted by comment-decay-scheduler.
- One video-detail request per observation; writing views, likes, shares and comment counts to `item.metrics`; labelling each with `plus_24h` or `plus_7d`, `observed_at` and `lateness_seconds`.
- Comparing each reading with the first-sight baseline and flagging a count that fell.
- Detecting removed or private videos and sending `deletions` (reason `platform_sync`).
- TikHub and EnsembleData adapters behind the flag, with vendor fallback.

### Out of scope

- The first-sight counts (they ride in the post payload from the finding service).
- Scheduling: comment-decay-scheduler decides what is due and when.
- Comments (tt-video-comments-fetcher); creator follower counts (tt-user-resolver); a client's own videos (tt-client-videos-fetcher gets their stats from the Display API).
- Any observation beyond +7 d in version 1, and any information about viewers, likers or sharers.

## 4. Users and consumers

- **Clients** see growth between first sight and day 7 on any TikTok video they watch, with the amber label.
- **Ops** watches lateness, vendor health and deleted-video counts, and can force an observation of one video (`ops_force`).
- **Downstream:** store-writer (into `metrics_timeseries`), aggregator and alert-evaluator (engagement scores, spike alerts), deletion-propagator (removes deleted videos), comment-decay-scheduler (cancels remaining steps for a vanished video), source-health-canary, quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Jobs on `jobs.tt-video-stats-refresher`, partitioned by `source_id`, emitted only by comment-decay-scheduler; this service has no scheduler of its own. A job carries `job_id`, `source_id`, `kind = metrics`, `due_at`, `attempt`, `post_ref` (`tiktok:video:<id>`) and `series_step` (`+24h` or `+7d`).

**Series.** First sight is the time of the video's first `items.normalized` message, the same clock comment-decay-scheduler uses for the comment series. Two jobs follow: +24 h and +7 d. Creator tiers do not apply: every video gets the same two observations, so coverage is guaranteed by the scheduler's series, not by a per-source rotation.

**Catch-up.** Jobs are taken most-overdue-first by `due_at`. A late observation is still taken and still labelled `plus_24h` or `plus_7d`, with `lateness_seconds` recording how late; downstream reads growth against the true `observed_at`. `rotation_behind` fires when the oldest job is more than the on-time window late.

**No backfill.** A video first seen more than 7 days after publication (for example during a creator's 90-day backfill) has only its first-sight counts; comment-decay-scheduler opens no metrics jobs for it (to be confirmed, question 3).

**Budget.** quota-governor answers allow, wait-until or deny as for every amber service; a delayed observation keeps its label and records the delay.

### 5.2 Step by step

1. Consume a job; check the observation key `tiktok:metrics:<video_id>:<label>` has not already been written (a replayed job stops here).
2. Read `TT_VENDOR_ROUTE` and route health: use the flag's vendor, or the alternate vendor with a row in `vendor_keys` while `fallback_on` is in force. Flag off: count `flag_off`, return the job as `skipped_flag_off`.
3. Ask quota-governor for allowance under `budget_tag = tt_vendor` (sub-counter `video_stats`).
4. Call video detail for the video id; read views, likes, shares and comment count.
5. Read the first-sight point from ClickHouse `metrics_timeseries` (read-only); set `regressed = true` for any count below its baseline; set `baseline_missing = true` if the point is not stored yet. Neither flag blocks the write: TikTok recounts, and the reading is still the truth the vendor gave.
6. Write one `item.metrics` message; after Redpanda acknowledges, send the completion message to comment-decay-scheduler and write `service_runs`.
7. If the vendor reports the video removed or private, run the confirmation in section 8 and, once confirmed, write `deletions` and return `video_gone`.

### 5.3 The call it makes

TikHub, endpoint family **video detail** (by video id). Exact path and parameter names, and whether a batch form exists: to be confirmed in the pilot; until then, one video per request. EnsembleData: the equivalent video-detail endpoint behind the flag value `ensembledata`. Limits: 10 requests a second per endpoint, TikHub billed on HTTP 200 only. Auth: the vendor key from Supabase Vault (`vendor_keys`), per job.

### 5.4 What it gets

The four counts, as the vendor returns them (illustrative; field names to be confirmed in the pilot):

```json
{"id": "7421538806219533573",
 "statistics": {"play_count": 61250, "digg_count": 4410, "share_count": 312, "comment_count": 498}}
```

Other counts the vendor may return (for example saves) stay out of `item.metrics` in version 1. Not obtained: who viewed, liked or shared; watch time; audience breakdowns; the author's profile (any author fields in the response are ignored).

## 6. Inputs and outputs

### 6.1 Reads

`jobs.tt-video-stats-refresher`; ClickHouse `metrics_timeseries` (read-only, first-sight point); `sources` (route, vendor), `clients` (government flag), `vendor_keys`, route health, `budgets` through quota-governor; the flag `TT_VENDOR_ROUTE`.

### 6.2 Writes

`item.metrics`, one message per observation, envelope plus the observation:

```json
{
  "envelope": {
    "platform": "tiktok", "route": "amber", "vendor": "tikhub",
    "service": "tt-video-stats-refresher",
    "source_id": "3d8a51c2-7e04-4b9f-8c16-2a9e5d70f4b8",
    "idempotency_key": "tiktok:metrics:7421538806219533573:plus_24h",
    "item_key": "tiktok:video:7421538806219533573",
    "job_id": "01J9N5D6T3K8R2W7Y0A4F1HXQB", "attempt": 1,
    "fetched_at": "2026-10-07T09:31:15Z",
    "retention_class": "vendor_agreed",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]
  },
  "observation": {
    "label": "plus_24h",
    "first_seen_at": "2026-10-06T09:15:42Z",
    "due_at": "2026-10-07T09:15:42Z",
    "observed_at": "2026-10-07T09:31:15Z",
    "lateness_seconds": 933,
    "views": 61250, "likes": 4410, "shares": 312, "comments": 498,
    "regressed": false, "baseline_missing": false
  }
}
```

Also `deletions` (item key, reason `platform_sync`), the completion message to comment-decay-scheduler (`done`, `skipped_flag_off` or `video_gone`), `service_runs`, `dlq.tt-video-stats-refresher` after 5 failed attempts.

### 6.3 State

No per-source cursor: the observation key is the guard against duplicates. `budgets` counters under `tt_vendor`; `service_runs` for last run and lag; in memory only backoff state.

## 7. Limits, quotas and cost

- Price: TikHub USD 0.50 to 1.00 per 1,000 requests by daily volume tier; EnsembleData at the team's contract price. Two requests per video, so every 100,000 videos costs 200,000 requests, USD 100 to 200. Videos per month: to be measured in the pilot.
- Rate: 10 requests a second per endpoint is far above a day's observations at any plausible video count, so the limiter smooths bursts after an outage.
- Route budget: about USD 280 to 560 a month for discovery plus comments at full scale across all amber TikTok services; this service's share, a small fraction because it makes two requests per video, is to be measured in the pilot.
- Budget tag `tt_vendor` (amber), sub-counter `video_stats`; one tag for all amber TikTok services.

## 8. Failure handling and fallback

- HTTP 429 and vendor rate-limit responses: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.tt-video-stats-refresher` and an alert fires.
- HTTP 401 and 403: mark the vendor key and route `degraded`, stop, alert; never rotate accounts or IPs.
- Empty 200 above 5% of calls in 15 minutes: source-health-canary flips the route to `degraded` and, with the flag on, `fallback_on`; the next job uses the alternate vendor until `fallback_off`.
- Removed or private video: the vendor's own status field separates it from an empty 200. A removal is confirmed by a second request (the alternate vendor when one is configured, otherwise a retry after 30 s) before `deletions` is written, because a vendor glitch must not delete data.
- Schema change: the reading is parked and `schema_unknown` raised; no partial counts are written.
- Partial write: observation keys make a replay harmless; downstream stores upsert on the key.

## 9. Non-functional requirements

- Throughput: two requests per newly seen video; the video count is to be measured in the pilot.
- Latency: an observation is written within the on-time window of `due_at` (one hour, initial value).
- Idempotency: `tiktok:metrics:<video_id>:<label>`; replayable jobs.
- Scaling: stateless workers on partition lag; no leader needed.
- Security: keys from Supabase Vault per job, never logged; no account pools, no proxies; only counts are kept, no author data (TikTok's Developer Terms forbid databases on individuals); provenance on every message; retention `vendor_agreed`.

## 10. Metrics and alerts

`items_fetched_total`, `jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `observations_written_total{label}`, `observation_lateness_seconds`, `regressed_total`, `baseline_missing_total`, `videos_gone_total` and `flag_off_total`. Alerts: `rotation_behind`, `vendor_degraded`, `dlq_nonempty`, `empty_200_rate`, `videos_gone_spike`. SLO: 95% of observations within the on-time window.

## 11. Dependencies

listening-sdk, comment-decay-scheduler, quota-governor, source-health-canary, normalize-item, store-writer, deletion-propagator, tt-profile-videos-poller, tt-keyword-search, tt-hashtag-feed-poller, tt-video-comments-fetcher, Supabase Vault, ClickHouse (read-only), Redpanda, TikHub and EnsembleData contracts.

## 12. Risks and mitigations

- Vendor counts can differ from the app's display (rounding, delay): disclosed in provenance; the label and `observed_at` let analysts judge.
- Counts can fall when TikTok removes spam views: flagged `regressed`, never dropped.
- Two observations give two points, not a curve: stated to clients; a denser series is a later decision.
- A false removal would delete real data: two-request confirmation before `deletions`.
- TikHub's ownership is only weakly cleared: contract review before the pilot; EnsembleData as the ready alternate.

## 13. Acceptance criteria

1. A video first seen at 09:15:42 on day 0 receives jobs due 09:15:42 on day 1 and day 7, labelled `plus_24h` and `plus_7d`, and no others.
2. Replaying the same job twice writes one `item.metrics` message per observation key.
3. An observation taken 4 hours late is written with `lateness_seconds` of at least 14,400 and an unchanged label.
4. A reading below the first-sight baseline is written with `regressed = true`; a missing baseline sets `baseline_missing = true` and does not block the write.
5. A vendor "not found" followed by a confirming second request produces one `deletions` message with reason `platform_sync` and a `video_gone` completion; a "not found" contradicted by the second request produces none.
6. With `TT_VENDOR_ROUTE = off`, no vendor call is made and the job is returned as `skipped_flag_off`; switching between `tikhub` and `ensembledata` yields messages with the same schema and `vendor` set accordingly.
7. After 5 simulated 429s the job is in `dlq.tt-video-stats-refresher` and an alert fired; a 401 marks the route `degraded` and stops the batch.
8. Empty 200s above 5% of calls in 15 minutes flip the route to `degraded` and, with the flag on, `fallback_on`.
9. Every `item.metrics` message carries `route = amber`, `vendor`, `service`, `fetched_at`, `retention_class = vendor_agreed` and the four counts; no author field appears.
10. A job for a video that belongs only to government-contract sources is refused and counted.

## 14. Open questions

1. Does the vendor offer a batch video-detail form? If so, the +24 h jobs for many videos could share requests: to be confirmed in the pilot.
2. Should a third observation at +30 d be added for long-tail videos? Proposed: not in version 1.
3. Does comment-decay-scheduler skip metrics jobs for videos older than 7 days at first sight? To be agreed before the pilot.
4. Should saves be promoted to `item.metrics` once the schema allows? Proposed: yes, as a nullable field.
