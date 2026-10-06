# backfill-orchestrator

**Platform:** Shared · **Route:** shared · **Lane:** Registry · **Owner:** Backend lead, source onboarding · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A source added today has a history. A client who adds a competitor's Page expects to see the last quarter of its posts on the first day, not to wait three months for the picture to fill. But the history of a source can only be read through that source's own route, with that route's own cap and budget, and the pollers deliberately read only what is newer than their cursor.

backfill-orchestrator is the single place that decides, for each newly registered source, which service reads its past, how far back, at what cost, and when the source is ready to join the rotation. It is the only service that emits `backfill` jobs, and the only writer of `backfill_status`.

Without it, each registry change would need every platform team to remember its own onboarding path. Sources would either be polled with no history, or sit unpolled behind a half-finished backfill, or burn vendor budget in a burst nobody scheduled. It also holds the line that individuals are never backfilled.

## 2. Objective (the end state this service delivers)

Every source that enters the registry has exactly one initial backfill job (or an explicit "no history route" outcome), capped by its route, and reaches `backfill_status = done` or `capped` with `next_poll_at = now()`, so the rotation takes over. Backfills never starve rotation and never exceed their budget.

Target: 100% of added sources leave `pending` within the backfill deadline (an environment variable, to be set in the pilot); zero individuals backfilled; zero duplicate backfill jobs per source and run.

## 3. Scope

### In scope
- Consuming `source.events` (`added`, `retired`, `updated`) and enqueueing `backfill` jobs on the source's own service.
- The route table and caps of section 5.3; the `backfill_status` state machine; setting `next_poll_at = now()` on completion.
- Pacing by tier, concurrency and budget mode; client and ops re-runs.
- Making backfilled posts recognisable (`job_kind = backfill`) so comment-decay-scheduler gives them one fetch.

### Out of scope
- Reading the history (fb-backfill, ig-account-media-poller, tt-profile-videos-poller, x-full-archive-search, li-client-posts-poller, li-company-posts-poller, tg-channel-posts-poller, yt-uploads-reconciler, news-feed-poller, news-sitemap-poller).
- Rotation after backfill (each poller) and comment series (comment-decay-scheduler).
- Qualifying sources (qualifier) and registry writes of identity columns (registry-writer).

## 4. Users and consumers

- **Clients** see "your source's last 90 days are loading", then data; they can ask for a re-run of a source they watch.
- **Ops** sees the queue, stuck runs and refused sources, and can force or cancel a run.
- **Consumers of its jobs:** the ten services above. **Neighbours:** registry-writer (events), quota-governor (budget mode), comment-decay-scheduler, normalize-item, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A `source.events` message with `event = added` (partitioned by `source_id`) creates a run. A safety-net scan, leader-elected through a Postgres advisory lock with a period well inside the backfill deadline, also picks up any `pending` source whose event was missed or deferred. `retired` cancels a pending run. A client or ops request creates a re-run.

**Order and pacing.** Pending runs are emitted by tier (a client's priority list and Tier 1 first, then Tier 2, then Tier 3), then by `added_at`, so no source waits behind a later arrival of the same tier. Per-platform concurrency is an environment variable (to be set in the pilot). Backfill is the lowest priority for quota-governor, so it only ever uses budget that rotation and comment series have left. While a route's budget mode is `stretch` or `exhausted`, new runs for it are not emitted and stay `pending`.

**Hand-over to rotation.** On completion the orchestrator sets `backfill_status` to `done` or `capped` and `next_poll_at = now()` in one transaction; the poller's scheduler, which selects only `done` or `capped` sources, picks the source up. Rotation never waits indefinitely: when a run is still `running` or `pending` at the backfill deadline, or fails to the DLQ, the source is set to `capped` with a reason and rotation starts anyway; late history is still ingested because the stores deduplicate.

**Comment series for backfilled posts.** Backfilled posts travel as ordinary traffic with `job_kind = backfill`; comment-decay-scheduler opens one `once` fetch for each and closes the series. A client who wants more asks from the client app; each backfilled post then gets a refresh through the scheduler, at lowest priority.

**Re-runs.** On request from `client_admin` (for sources in `client_sources`) or `ops`, a new run with the same route cap (or a smaller window) is created. A re-run never changes `sources.backfill_status`, so the source stays in rotation.

### 5.2 Step by step

1. Consume `added`; load the `sources` row; refuse when `source_type` is not a supported source type (individuals are never sources) or `tier = retired`.
2. Look up the route in the table (5.3); if there is no history route, set `done` with a note and `next_poll_at = now()`.
3. Read the platform flag and the budget mode; if the amber flag is `off`, set `done` with note `flag_off` (an amber source added while the flag is off needs a re-run once it is on).
4. Insert a `backfill_runs` row (`run_id = initial`); set `backfill_status = running`.
5. Emit the job to `jobs.<service>` with the cap; the job id is deterministic.
6. Consume the completion event from `jobs.completed`; write `done` or `capped`, `backfill_runs` counters, and `next_poll_at = now()`.
7. On timeout, re-emit with the same job id; on DLQ, apply the failure rule of 5.1.

### 5.3 The call it makes

No external call. The logic it runs: route and cap table, then the state machine.

| Source | Service on `jobs.<service>` | Cap (default: last 90 days, or the route's cap if smaller) |
|---|---|---|
| Facebook Page, green | fb-backfill | about 600 ranked posts per Page per year; `meta_graph_pages:<client_id>` |
| Facebook group, amber | fb-group-posts-poller (proposed) | vendor budget `fb_vendor` |
| Instagram account | ig-account-media-poller | `ig_graph_<ig_user_id>` |
| TikTok creator, amber | tt-profile-videos-poller | `tt_vendor`; 20 items a page |
| X account or keyword rule | x-full-archive-search | post reads at USD 0.005 each under `x_pay_per_use` |
| LinkedIn company page, client-administered | li-client-posts-poller | `linkedin_cm:<client_id>` |
| LinkedIn company page, amber | li-company-posts-poller | `li_vendor_company_posts` |
| Telegram channel, amber | tg-channel-posts-poller | `tg_apify_posts` |
| Telegram own channel, green | none: the Bot API has no history | `done` at once |
| YouTube channel | yt-uploads-reconciler | `youtube_data_api`, 1 unit a page of 50 |
| News site | news-feed-poller and news-sitemap-poller (whichever the site has) | what the feed or sitemap exposes |
| Hashtag or keyword rule without a history route; web | none | `done` at once, note `no_history_route` |

**State machine.** `pending` to `running` when the job is emitted; `running` to `done` when the service reports the window fully read; `running` to `capped` when it stopped on the cap, the budget, the deadline or failure (`capped_reason`: `route_cap`, `budget`, `deadline`, `failed`); no transition leaves `done` or `capped` except a re-run, which does not touch the column.

**Cost of a run.** Estimated before emission and compared with the budget: X, post reads times USD 0.005; TikTok, ceil(videos / 20) requests at USD 0.50 to 1.00 per 1,000; YouTube, ceil(videos / 50) units; Telegram and LinkedIn amber, items times the Apify rate (USD 1.21 to 3.00 per 1,000 Telegram items; USD 1.50 to 2.00 per 1,000 LinkedIn items, derived from the monthly prices); Meta, quota only; news, crawl politeness only.

**Job id.** ULID with the random part from `sha256(source_id | backfill | run_id)`; re-emission is idempotent.

### 5.4 What it gets

A `source.events` `added` message (registry-writer's shape) and a completion event:

```json
{"schema": "jobs.completed/v1", "job_id": "01J9P3Y6B2N7C4D8F0G5H1JKQR", "service": "fb-backfill", "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11", "kind": "backfill", "status": "ok", "attempt": 1, "finished_at": "2026-10-06T10:42:17Z", "report": {"new_count": 143, "pages": 2, "cost_units": 2, "oldest_item_at": "2026-07-08T06:55:12Z", "capped": false, "capped_reason": null}}
```

It does not get any platform data; it never calls a platform.

## 6. Inputs and outputs

### 6.1 Reads
`source.events`; `jobs.completed`; tables `sources`, `client_sources`, `budgets` (mode), `backfill_runs`; the client re-run endpoint.

### 6.2 Writes
`jobs.<service>`, partitioned by `source_id`:

```json
{"job_id": "01J9P3Y6B2N7C4D8F0G5H1JKQR", "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11", "kind": "backfill", "due_at": "2026-10-06T10:14:44Z", "attempt": 1, "run_id": "initial", "cap": {"max_age_days": 90, "max_items": 600}, "route": "green", "vendor": null}
```

Also `sources.backfill_status` and `next_poll_at`, `backfill_runs`, `service_runs`, `dlq.backfill-orchestrator`.

### 6.3 State
`backfill_runs` (proposed): `run_id`, `source_id`, `service`, `requested_by` (system, client, ops), `cap`, `status`, `capped_reason`, `started_at`, `finished_at`, `items_new`, `cost_units`, `attempt`. `sources.backfill_status` is the summary the pollers read.

## 7. Limits, quotas and cost

No budget tag of its own; the backfill services ask quota-governor at the lowest priority. Volume is a one-off burst at launch (every existing source) plus a trickle per added source, both to be measured in the pilot; steady state does not touch the 1,000,000 items a day, which is rotation. Cost per source follows the formulas in 5.3 and is bounded by the route's cap; USD 0 on Meta, YouTube (quota only) and news. The X cap is the most expensive per item and is set per source in `budgets` (to be set in the pilot); no individual is ever read.

## 8. Failure handling and fallback

- Service failure: the standard rules apply inside the service (429 backoff 30 s to 15 min, 5 attempts, DLQ); a DLQ outcome sets `capped` (`failed`) and starts rotation.
- 401 and 403, or `health = blocked`: the run is held, an alert fires, rotation is not affected; no account or IP is rotated.
- Budget `wait-until`: the service requeues; the deadline rule bounds the wait.
- Lost completion: timeout and same-id re-emission.
- Amber fallback (`fallback_on`): the backfill service reads the flag per job; the orchestrator does nothing.

## 9. Non-functional requirements

- Throughput: a handful of events a second at most; the load is the fetchers'.
- Latency: a job is emitted within one scan period of `added` when the budget allows.
- Idempotency: deterministic job ids; replaying `added` or a completion changes nothing.
- Security: no tokens; individuals refused; Meta, X, LinkedIn and YouTube data keep their retention class from the raw envelope; amber backfills carry provenance.

## 10. Metrics and alerts

`backfill_pending{platform}`, `backfill_running`, `backfill_wait_seconds`, `backfill_duration_seconds`, `backfill_items_total`, `backfill_capped_total{reason}`, `backfill_cost_units_total`, `individual_refused_total`, `jobs_total{status}`, `dlq_total`. Alerts: `backfill_stuck`, `backfill_deadline_breached`, `individual_refused`, `dlq_nonempty`.

## 11. Dependencies

listening-sdk, registry-writer, quota-governor, the ten backfill services, comment-decay-scheduler, normalize-item, source-health-canary, Supabase Postgres, Redpanda.

## 12. Risks and mitigations

- A burst at launch exhausts an amber budget: lowest priority, per-platform concurrency, stretch-mode hold.
- A client asks for deep comments on 90 days of posts: priced and paced through the governor; the client is told the queue position.
- Duplicate history from a late run: stores upsert on `item_id`.

## 13. Acceptance criteria

1. An `added` event for a Facebook Page produces one job on `jobs.fb-backfill` with `cap.max_age_days = 90` and sets `running`.
2. Each source type in the table in 5.3 reaches the named service; a Telegram own channel and a hashtag source go to `done` with no job.
3. Replaying the same `added` event produces no second job (same `job_id`).
4. A completion with `capped = false` writes `done`; with `capped = true` writes `capped`; both set `next_poll_at <= now()`.
5. A source whose `source_type` is not a supported source type is refused, gets no job and raises `individual_refused`.
6. While `tt_vendor` is in `stretch`, no TikTok run is emitted and rows stay `pending`; when it returns to `normal`, runs are emitted in tier order.
7. A re-run on a `done` source leaves `backfill_status = done`; a client without the source in `client_sources` gets 403.
8. A job in `dlq.<service>` sets `capped` (`failed`), starts rotation and raises an alert.
9. A backfilled fixture post arrives with `job_kind = backfill`, and comment-decay-scheduler creates one `once` fetch.
10. A `running` run with no completion at the timeout is re-emitted with the same `job_id`; a `retired` event cancels a pending run.

## 14. Open questions

1. fb-group-posts-poller is not in the list of backfill targets; proposed to receive `backfill` jobs, with vendor history depth to be measured in the pilot.
2. fb-backfill's approved PRD also sets `done` or `capped` and `next_poll_at`; proposed that this service becomes the single writer at its next revision (the values are identical meanwhile).
3. Backfill deadline value and the per-source X read cap: to be set in the pilot.
4. Should an amber source added while its flag is off be backfilled automatically when the flag is switched on? Proposed: yes, in tier order.
