# comment-decay-scheduler

**Platform:** Shared · **Route:** shared · **Lane:** Registry · **Owner:** Backend lead, comment pipeline · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Most of the 30.5M items a month are comments, and a comment appears after its post, over hours and days. A post is read once by a poller; its comments keep arriving long afterwards. Somebody has to decide when to go back, how often, and when to stop. If each comment fetcher decided for itself, there would be eleven schedules with eleven ideas of "recent", and no one could say whether a client's comment data is current.

comment-decay-scheduler is that one decision-maker. It is the only service that emits comment, reply and metrics jobs. It opens a series for every new post, fetches often while the post is young or busy, backs off when it goes quiet, and spends vendor money only where the profile says so. Without it, "comments always up to date" is not a promise the product can keep: either comments are fetched once and go stale, or they are re-fetched blindly on every poll and the amber budgets and the YouTube quota are gone in days.

## 2. Objective (the end state this service delivers)

Every post that has a comment route has a series in the control plane from the moment it is first seen. Each step is emitted when due, once, and the series ends by its own rules (early stop, day 30, route window) or stays open while the post is still growing.

Target: 95% of series complete every step on time (each step emitted within one scan period of `next_due_at`, finished before the next step is due); zero posts with two jobs in flight; zero lost steps (every step ends as completed, stopped, or visible in a DLQ).

## 3. Scope

### In scope
- Opening a series per post consumed from `items.normalized`, using the route's profile (section 5.1), and storing it in `comment_series`.
- Emitting `comments` jobs to `jobs.<comment service>`, `replies` jobs, and `metrics` jobs, partitioned by `source_id`.
- Early stop, extension to day 30, hot-post extras, shortened series for backfilled posts, client-requested refresh after day 30.
- Budget-aware behaviour on amber routes; catch-up when behind.

### Out of scope
- The fetches themselves, paging, hash comparison, edits and deletions: the comment services.
- Polling for new posts (each poller's own scheduler) and backfill (backfill-orchestrator).
- Budget decisions (quota-governor): this service only reads the mode it publishes.
- Receiving live comments on Telegram (tg-discussion-receiver).

## 4. Users and consumers

- **Clients** experience it as "the comments under a post keep arriving, fast at first, then less often"; they can request a refresh of one post.
- **Ops** sees overdue series, stopped series, and can force a step.
- **Consumers of its jobs:** fb-post-comments-fetcher, fb-group-comments-fetcher, ig-own-comments-fetcher, ig-comments-fetcher, tt-video-comments-fetcher, x-replies-fetcher, yt-comments-fetcher, yt-replies-fetcher, li-own-comments-fetcher, li-post-comments-fetcher, tg-discussion-receiver, news-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller (metrics jobs only), tt-video-stats-refresher, yt-video-details-fetcher.
- **Neighbours:** normalize-item (feeds it), registry-writer (`source.events`), quota-governor (budget mode), source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Triggers.** (1) A message on `items.normalized` with `kind = post` and `version = 1`: opens the series. (2) A completion event on `jobs.completed` (proposed topic, section 14): advances or ends it. (3) A leader-elected scan loop (Postgres advisory lock, period an environment variable well inside the shortest step of 1 hour) that emits due jobs. (4) `source.events` (`retired`) and `deletions`: cancel series. (5) A refresh request from the client app or ops.

**Profiles.** Chosen from the post's platform, `owned_by_client` and route. Amber profiles open only when the platform flag (`FB_VENDOR_ROUTE`, `IG_VENDOR_ROUTE`, `TT_VENDOR_ROUTE`, `LI_VENDOR_ROUTE`) is not `off`; when a flag is switched on, posts still inside the profile's window get a catch-up series.

| Profile | Comment service | Steps after first seen | Replies |
|---|---|---|---|
| fb_page | fb-post-comments-fetcher | +1 h, +6 h, +24 h, +3 d, +7 d, +14 d, +21 d, +28 d | in the stream; no job |
| fb_group (amber) | fb-group-comments-fetcher | +1 h, +6 h, +24 h, +3 d | `replies` job by comment id when the vendor exposes it |
| ig_own | ig-own-comments-fetcher | as fb_page | field expansion; no job |
| ig_other (amber) | ig-comments-fetcher | +6 h, +24 h, +3 d | none |
| tt (amber) | tt-video-comments-fetcher | +1 h, +6 h, +24 h, +3 d, +7 d | `replies` job per comment with more than 10 replies |
| x | x-replies-fetcher | +1 h, +6 h, +24 h, +3 d; window ends at 7 d | by `conversation_id:`; no job |
| yt | yt-comments-fetcher | +6 h, +24 h, +3 d, +7 d, +30 d | `replies` job to yt-replies-fetcher for threads with more than 5 replies |
| li_own | li-own-comments-fetcher | +6 h, +24 h, +3 d | same call; member data purged after 48 h |
| li_other (amber) | li-post-comments-fetcher | +24 h, +3 d | none |
| tg_own | tg-discussion-receiver | push; one daily `health` job | live |
| news (Disqus) | news-comments-fetcher | +6 h, +24 h, +3 d | threaded, same call |

"Weekly to day 30" means +14 d, +21 d, +28 d. Step offsets are measured from the post's first-seen time (`fetched_at` of its first `items.normalized` message), not its creation time.

**Keeping every series moving.** `next_due_at` is computed from the anchor, not from when the previous job finished, so steps do not drift. Jobs are emitted most overdue first, then by source tier. A post has one job in flight: its row is `in_flight` until the completion event arrives; a hot extra due at the same time as a regular step is merged into it.

**Catch-up.** `comment_lag_seconds` is now minus `next_due_at` of the most overdue series. When it exceeds that step's interval, the scan switches to most-overdue-first with a larger batch and raises `rotation_behind`. Late steps are still emitted, never dropped: being behind costs freshness, not coverage.

**Backfilled and old posts.** Posts with `job_kind = backfill` (carried from the raw envelope), or first seen when older than the profile's last step, get one fetch (`series_step = once`) at the lowest priority, then `done`, unless a client asks for more.

**Metrics.** A second row (`lane = metrics`) per post on Facebook green, Instagram green, TikTok amber and YouTube: `metrics` jobs at +24 h and +7 d to fb-reactions-fetcher, ig-account-media-poller (which serves them by re-reading the account's recent media back to the post's timestamp), tt-video-stats-refresher and yt-video-details-fetcher. On X, LinkedIn, Telegram and news the counts are recorded at first sight; whether to add +24 h and +7 d refreshes there is open question 6. Early stop does not touch the metrics lane.

**After day 30.** No automatic fetches. A client refresh creates one `comments` job (`series_step = refresh:<request_id>`), priority tier 1 (client-facing); the fetcher asks quota-governor, and a wait-until decision is shown to the client as "queued for budget".

### 5.2 Step by step

1. Consume a post from `items.normalized`; resolve the profile; skip if no profile applies or the source is `retired`.
2. Insert `comment_series` (and the metrics row) with `ON CONFLICT (item_id, lane) DO NOTHING`; set `next_step` to the first step and `next_due_at = anchor + offset`.
3. Scan: select due rows, `FOR UPDATE SKIP LOCKED`; read the amber budget mode (5.3); build the job; set `status = in_flight` and `in_flight_job_id`; commit; produce to `jobs.<service>`.
4. Consume the completion event, apply the rules of 5.3, and write the new state in one transaction.
5. If the report names reply candidates above the route threshold, emit a `replies` job after step 4, never alongside the comment job.

### 5.3 The call it makes

No external call. The logic it runs:

**Job id.** `job_id` is a ULID whose time part is `due_at` and whose random part is the first 10 bytes of `sha256(item_id | lane | series_step)`. Re-emitting a step after a crash yields the same id, so consumers and the DLQ deduplicate.

**On each completion** (regular step; `before` = `last_total` before the fetch):
- `growth = new_count / max(before, 1)`; `velocity = new_count / max(hours since last_fetched_at or anchor_at, 1)` (the floor of 1 hour means a short gap can never inflate velocity).
- Early stop is armed once `before >= 5` or the +24 h step has been reached (a post with no comments at +1 h is normal, not finished; this arming rule is this PRD's addition).
- **Early stop:** armed and `new_count < 5` and `growth < 0.05` → status `stopped_early`, pending steps and hot extras cancelled.
- **Extension:** at the day-7 step (or the profile's last step when it is shorter than 7 days), `growth >= 0.20` → `extended = true`; remaining steps become every 2 days to day 30 (+9 d to +29 d; capped at the route window, 7 d on X). Both limits are replaced by the profile's last step on YouTube (+30 d stays final).
- **Hot post:** a regular step with `velocity > 100` and no open hot window sets `hot_until = now + 6 h`, `hot_next_at = now + 1 h`, then one `hot:<n>` extra per hour until `hot_until`. Hot extras never re-arm the window; only a regular step can, which bounds extras to six per regular step.
- Otherwise advance `next_step`; after the last step status `done`.

**Replies.** A thread becomes a candidate when its reported reply count exceeds the threshold (TikTok 10, YouTube 5) and exceeds the replies already stored; one `replies` job per post carries up to a configured number of `thread_ids`.

**Budget mode** (read from `budgets` for the route's tag: `fb_vendor`, `ig_vendor`, `tt_vendor`, `li_vendor_post_comments`):

| Mode | Behaviour |
|---|---|
| normal | all rules |
| stretch (monthly use at 80% or more) | stop opening hot windows and cancel pending hot extras; then multiply every step after +24 h by the governor's `stretch_factor` |
| exhausted | hold steps as `scheduled`, due again after the reset |

The +24 h step is never skipped or moved later; it is held, not cancelled, when a budget is exhausted. Mode is re-read on every scan.

**Stale and failed completions.** A completion whose `job_id` is not `in_flight_job_id` only updates `last_total` if newer. A job that reached `dlq.<service>` marks the step `missed` in the counters and moves the row to its next step. An `in_flight` row older than the fetcher's five-attempt backoff ceiling is re-emitted with the same id and raises `series_stuck`.

**Worked example.** Facebook Page post first seen 2026-10-06 09:14 (profile fb_page):

| Time | Step | New | Total | Decision |
|---|---|---|---|---|
| 10:14 | +1 h | 160 | 160 | velocity 160/h: hot window to 16:14 |
| 11:14 to 14:14 | hot:1 to hot:4 | 120, 70, 40, 20 | 410 | extras every hour |
| 15:14 | +6 h merged with hot:5 | 15 | 425 | 15 new is not under 5: continue |
| 16:14 | hot:6 | 9 | 434 | window ends |
| 7 Oct 09:14 | +24 h | 52 | 486 | growth 12%: continue |
| 9 Oct 09:14 | +3 d | 31 | 517 | continue |
| 13 Oct 09:14 | +7 d | 4 | 521 | 4 new, growth 0.8%: early stop |

Metrics jobs go to fb-reactions-fetcher at 7 Oct 09:14 and 13 Oct 09:14. Had the +7 d fetch added 120 (23%), steps +9 d to +29 d would follow.

### 5.4 What it gets

Posts from `items.normalized` (item_id, source_id, platform, route, vendor, `fetched_at`, `owned_by_client` from `sources`), and one completion event per job:

```json
{"schema": "jobs.completed/v1", "job_id": "01J9N5W2D8E4Q0RZ7K3T6B1XCM", "service": "fb-post-comments-fetcher", "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11", "kind": "comments", "series_step": "+6h", "status": "ok", "attempt": 1, "finished_at": "2026-10-06T15:15:09Z", "report": {"new_count": 15, "seen_count": 410, "pages": 5, "cost_units": 5, "reply_candidates": []}}
```

It does not get comment text; it never calls a platform.

## 6. Inputs and outputs

### 6.1 Reads
`items.normalized`; `jobs.completed`; `source.events`; `deletions`; tables `sources`, `client_sources`, `budgets`, `comment_series`.

### 6.2 Writes
`jobs.<comment service>`, `jobs.fb-reactions-fetcher`, `jobs.ig-account-media-poller` (metrics), `jobs.tt-video-stats-refresher`, `jobs.yt-video-details-fetcher`, partitioned by `source_id`:

```json
{"job_id": "01J9N5W2D8E4Q0RZ7K3T6B1XCM", "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11", "kind": "comments", "due_at": "2026-10-06T15:14:00Z", "attempt": 1, "post_ref": {"item_id": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f", "platform": "facebook", "platform_id": "100064583471102_1198837625012734"}, "series_step": "+6h", "profile": "fb_page", "route": "green", "vendor": null}
```

Also `comment_series`, `service_runs`, `dlq.comment-decay-scheduler`.

### 6.3 State
`comment_series` (item_id, source_id, route, profile, next_step, next_due_at, last_new_count, last_total, status) plus proposed columns `lane`, `anchor_at`, `last_fetched_at`, `extended`, `hot_next_at`, `hot_until`, `hot_count`, `in_flight_job_id`; primary key (`item_id`, `lane`). Status: `scheduled`, `in_flight`, `done`, `stopped_early`, `cancelled`. In memory only the leader lock.

## 7. Limits, quotas and cost

No external call and no budget tag of its own. Full scale: about 1,000,000 items a day, roughly a quarter posts (to be measured in the pilot) = about 250,000 series opened a day, about 3 a second. Ceiling on jobs: at most 8 steps per series gives about 2,000,000 comment jobs a day (about 23 a second) plus up to 500,000 metrics jobs; the real figure is lower because most profiles are shorter and early stop cuts most series. Postgres handles that write rate comfortably; the load is the fetchers'.

Cost sits in the fetchers, but the schedule sets it. At one page per fetch (a floor): a TikTok series of 5 requests costs USD 0.0025 to 0.0050 at TikHub's USD 0.50 to 1.00 per 1,000 requests; a Facebook group series of 4 costs USD 0.0080 to 0.0193 on SociaVault (USD 1.99 to 4.83 per 1,000 credits) or USD 0.0040 to 0.0075 on ScrapeCreators (USD 0.99 to 1.88 per 1,000 requests); an Instagram other-media series of 3 costs USD 0.0060 to 0.0145 on SociaVault. LinkedIn amber is priced per item on Apify: to be measured in the pilot. On YouTube at 1 unit a page, 5 units a series, the whole 10,000-unit day pays for at most 2,000 series, so the schedule is quota-bound before cost-bound. On X each reply read costs USD 0.005 under `x_pay_per_use`.

## 8. Failure handling and fallback

- Fetcher failures follow the standard rules inside the fetcher (429 backoff 30 s to 15 min, 5 attempts, then DLQ); this service sees the outcome through the completion event.
- Redpanda produce failure: row stays `in_flight`; the reaper re-emits with the same `job_id`.
- Scheduler crash: state is in Postgres; the next leader resumes the scan. Series open is idempotent.
- `health = blocked` or `degraded` on the source: steps are held, not cancelled; they resume when health returns.
- Schema change on `items.normalized`: message parked, `schema_unknown` alert; no series lost because normalize-item republishes on replay.
- No fallback route: this service never calls a platform.

## 9. Non-functional requirements

- Throughput: section 7; scale consumers on `items.normalized` and `jobs.completed` lag; one leader scanner.
- Latency: a step is emitted within one scan period of `next_due_at`; a completion updates state within seconds.
- Idempotency: series open on (`item_id`, `lane`); deterministic job ids; replaying either input changes nothing.
- Security: no tokens held; amber jobs carry `route` and `vendor` for provenance; series on `youtube_30d_text`, `linkedin_48h` and `meta_on_request` data never extend retention.

## 10. Metrics and alerts

`series_open_total{profile}`, `series_state{status}`, `jobs_emitted_total{kind,service}`, `comment_lag_seconds`, `early_stop_total`, `extension_total`, `hot_window_total`, `hot_extras_dropped_total`, `steps_missed_total`, `inflight_stuck`, `quota_mode{tag}`, `jobs_total{status}`, `dlq_total`. Alerts: `rotation_behind`, `series_stuck`, `dlq_nonempty`, `steps_missed_rate`, `budget_stretch_active`. SLO: 95% of series on time.

## 11. Dependencies

listening-sdk, normalize-item, registry-writer, quota-governor, source-health-canary, all comment, replies and metrics services named in section 4, backfill-orchestrator, Supabase Postgres, Redpanda.

## 12. Risks and mitigations

- Viral posts multiply cost: hot extras are bounded (six per regular step) and are the first thing dropped under budget pressure.
- A missing completion event stalls a series: the reaper re-emits after a timeout and alerts.
- Extension on a tiny base (1 new on 4) opens 11 extra fetches: open question 3.
- YouTube and X quotas are small relative to the post count: series on those routes are priority-ordered and the governor decides.

## 13. Acceptance criteria

1. A post on `items.normalized` produces exactly one `comment_series` row per lane; replaying the message produces none.
2. For an fb_page post first seen at 09:14, rows show `next_due_at` of 10:14, 15:14, 09:14 next day, and +3 d, +7 d, +14 d, +21 d, +28 d in turn, regardless of fetch duration.
3. A fetch with 3 new on 100 stored (armed) cancels the series; 3 new on 100 on a series not yet armed does not.
4. A fetch with 5 new on 100 stored does not stop the series (both thresholds must hold).
5. At day 7, 20 new on 100 stored switches to +9 d, +11 d, ..., +29 d; on X it stops at 7 d.
6. A step with velocity above 100 an hour creates six hourly extras; a hot extra due with a regular step yields one job; extras never re-arm the window.
7. With the budget mode `stretch`, no new hot extras appear, pending ones are cancelled, steps after +24 h move by `stretch_factor`, and the +24 h step is still emitted on time; with `exhausted` it is held, not cancelled.
8. Two completion events or a replayed scan never leave two jobs in flight for one post; re-emitting a step reuses the same `job_id`.
9. A backfilled post gets a single `once` job; a client refresh on a day-35 post gets one job with `series_step = refresh:<request_id>`.
10. With 5,000 overdue series, jobs are emitted most overdue first and `rotation_behind` fires.
11. A `retired` source event cancels its open series; a deleted post cancels its rows.

## 14. Open questions

1. CONVENTIONS lists no completion topic. This PRD proposes `jobs.completed`, written by the listening-sdk job wrapper of every fetcher, partitioned by `source_id`; alternative: poll `service_runs`.
2. Is the early-stop arming rule (section 5.3) accepted? Without it, a post with no comments at +1 h loses its series.
3. Should extension also require at least 5 new comments, mirroring early stop?
4. Should the 80% stretch rule also cover metered green routes (X, YouTube), for hot extras only?
5. X replies cost USD 0.005 each: a per-post read cap is to be decided after the pilot.
6. Should X, LinkedIn and Telegram posts also get +24 h and +7 d count refreshes? Their pollers read incrementally, so counts after first sight change only when a client refreshes a post; on X each refresh is a paid post read.
