# x-full-archive-search

**Platform:** X · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, X adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Every other X service looks forward: x-user-timeline-poller reads what is newer than its cursor, x-filtered-stream pushes what is posted now, x-recent-search and x-replies-fetcher reach back 7 days. x-full-archive-search is the only one that reads the past, through the official full-archive search, and only on demand: once for every newly added account, and when a client asks for brand-term history or for replies older than the recent window.

Without it, a new account would have no baseline for 90 days, so trends, share of voice and response comparisons would start empty; a client could not see how its brand was discussed before it signed up; old reply threads could never be completed. Every result is a billed post read, so the service also carries the cost discipline: estimate first, ask the governor, stop at a cap, never hold an account out of rotation.

## 2. Objective (the end state this service delivers)

Every newly added green X account has its last 90 days (longer on client request) read once, or as much as its per-job cap and the monthly budget allow, then enters rotation; client history requests return what they asked for or stop at a known cost. Target: every backfill job ends (`done` or `capped`) within the account's first tier interval after `added_at` (1 h, 6 h, 24 h); paid reads never exceed the per-job cap; no post id counted twice in `post_reads` on one UTC day; zero jobs lost.

## 3. Scope

### In scope

- `backfill` jobs from backfill-orchestrator for every newly added green X account: last 90 days by default, longer on client request.
- `keyword_history` jobs: a client's registered brand terms over a window it chooses.
- `replies` jobs: replies older than the 7-day recent-search window, on client request, handed back to x-replies-fetcher's series bookkeeping.
- Cost estimate, quota-governor allowance, per-job cap, ledger settlement; resumable progress; seeding x-user-timeline-poller's cursor.

### Out of scope

- `backfill_status` and `next_poll_at` (backfill-orchestrator); rotation (x-user-timeline-poller); live push (x-filtered-stream); recent search (x-recent-search); scheduled reply series (comment-decay-scheduler, x-replies-fetcher); profiles (x-user-resolver); deletions (x-compliance-sync); deduplication (normalize-item).
- Individuals (never backfilled), reposts, media files, metrics refreshes.

## 4. Users and consumers

- **Clients** see a new account with 90 days of history from day one, and brand-term history or old threads on request.
- **Abdullah and ops** set per-job caps in `budgets`, watch history spend by job kind and see which accounts ended `capped`.
- **Downstream**: backfill-orchestrator, x-user-timeline-poller, comment-decay-scheduler, x-replies-fetcher, normalize-item, raw-archiver, quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.x-full-archive-search`, partitioned by `source_id`. The service has no scheduler and never polls. backfill-orchestrator emits `backfill` for each X account added with `backfill_status = pending`, and `keyword_history` on a client request (source = the client's `keyword_rule` row); comment-decay-scheduler, the only emitter of reply jobs, emits `replies` when a client asks for the replies of a post older than 7 days.

**Hand-off to rotation.** x-user-timeline-poller never polls a `pending` account. This job reads newest first, so wherever it stops, the newest posts are stored. It seeds the poller's cursor with the highest id read and reports on `jobs.completed`; backfill-orchestrator sets `done` or `capped` and `next_poll_at = now()`, and the poller rotates the account from the seed. With nothing read, no seed is written and the poller's empty cursor reads one page.

**Budget never blocks rotation.** A governor `deny`, or a `wait_until` later than `added_at` plus the account's tier interval, ends the job `capped` at once; the account enters rotation with the history it has.

**Comment series.** Backfilled posts reach comment-decay-scheduler marked `job_kind = backfill` and get a shortened series: one fetch only unless the client asks for more.

### 5.2 Step by step

1. Consume a job (`job_id`, `source_id`, `kind`, `attempt`, `window_start`, `window_end`, `requested_by`; `post_ref` and `series_step` on replies); load the `sources` row and this service's progress row; stop if `health = blocked`.
2. Eligibility: `backfill` only for a green X `account` the qualifier admitted (organization or public figure, never an individual); `keyword_history` only on terms in `keywords` for the requesting client, never free text. Remove government clients without an X Enterprise plan naming them from `client_ids`; if none remain, report `done` without a call.
3. Query and window: backfill `from:<handle> -is:retweet`, job start minus 90 days (or the requested start) to job start; keyword_history the rule's terms as x-recent-search builds them, plus `-is:retweet`, over the client's window; replies `conversation_id:<root id>`, root `created_at` to job start minus 7 days.
4. Estimate expected posts × USD 0.005, with expected posts = posting rate (`tweet_count` ÷ account age, from x-user-resolver's profile) × window days; or the rule's daily `new_count` in x-recent-search's last 7 days of reports × window days; or the root's latest `reply_count`. Unknown or above the per-job cap: the cap.
5. Ask quota-governor `{budget_tag: x_pay_per_use, amount: <expected posts>, service: x-full-archive-search, priority, sub_counter: post_reads, resource_ids: []}`, priority 5 for backfill and 1 for client requests. `allow` runs; `wait_until` requeues (5.1); `deny` reports `capped`. A used-up allowance is topped up 100 per page, up to the cap.
6. Call search (5.3); settle each page through the ledger (ids already read today get `paid = false`, the rest `paid = true` and count in `post_reads`); write one `raw.items` message per post, landed by raw-archiver under `raw/green/x/<yyyy>/<mm>/<dd>/x-full-archive-search/`.
7. After Redpanda acknowledges, store progress. Stop `done` when `next_token` is absent, `capped` when paid reads reach the cap or the governor denies.
8. Backfill: raise x-user-timeline-poller's cursor to the highest id read (64-bit integer comparison; never lowered). Replies: hand back (6.2).
9. The listening-sdk wrapper writes `jobs.completed/v1` with the status and `new_count` = posts returned, `seen_count` = posts with `paid = false`, `pages`, `cost_units` = paid reads; the progress row is cleared.

### 5.3 The call it makes

```
GET /2/tweets/search/all
  ?query=from:<handle> -is:retweet
  &start_time=<window start, UTC>
  &end_time=<window end, UTC>
  &max_results=100
  &tweet.fields=created_at,public_metrics,conversation_id,lang,geo,entities
  &expansions=author_id,attachments.media_keys
  &next_token=<meta.next_token of the previous page; absent on the first>
Authorization: Bearer <app bearer token of the company X app, from Supabase Vault per job>
```

Only `query` changes by kind: keyword_history uses the rule's terms with `-is:retweet` (and `lang:ar` or `place_country:IQ` when the rule sets them); replies use `conversation_id:<root id>`. Page size 100; follow `next_token` until absent. `<handle>` is `sources.handle` as x-user-resolver last confirmed it. Anything else (base URL, the pay-per-use request rate limit, maximum query length, `next_token` lifetime, newest-first order, whether `end_time` is exclusive, whether `from:` accepts the numeric id) is to be confirmed in the pilot.

### 5.4 What it gets

Per page: `data` (posts with `id`, `text`, `edit_history_tweet_ids` and the requested fields), `includes.users` (`id`, `name`, `username`), `includes.media` (`media_key`, `type`) and `meta.next_token`. One post from a backfill page:

```json
{
  "data": [{
    "id": "2087514290017763328",
    "edit_history_tweet_ids": ["2087514290017763328"],
    "text": "تخفيضات نهاية الصيف في جميع فروعنا في الكوت",
    "created_at": "2026-08-12T15:20:04.000Z",
    "author_id": "1489203345671204864",
    "conversation_id": "2087514290017763328",
    "lang": "ar",
    "public_metrics": {"retweet_count": 7, "reply_count": 21, "like_count": 164, "quote_count": 2, "bookmark_count": 3, "impression_count": 15230}
  }],
  "includes": {"users": [{"id": "1489203345671204864", "name": "Kut Home Electronics", "username": "kuthomeelec"}]},
  "meta": {"next_token": "b26v89c19zqg8o3fpzbkk0n6yt"}
}
```

Not returned: reposts (excluded), deleted or protected posts, media URLs, place details (`geo` holds only a `place_id`), follower counts.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.x-full-archive-search`; `sources`, `cursors` (own progress rows and x-user-timeline-poller's row), `keywords`, `clients` (X Enterprise entitlement), `budgets` (per-job caps; counters and the read ledger through quota-governor); x-user-resolver's last profile; x-recent-search's `jobs.completed` reports.

### 6.2 Writes

`raw.items`, one message per post: the poller's envelope plus `job_kind`, and the post with its `includes`, unchanged:

```json
{
  "envelope": {
    "platform": "x", "kind": "post", "route": "green", "vendor": null,
    "service": "x-full-archive-search", "job_kind": "backfill",
    "source_id": "c71e5a90-3d2b-4f86-9a14-8e0b6d2f5c37",
    "platform_id": "2087514290017763328",
    "idempotency_key": "x:post:2087514290017763328",
    "job_id": "01J9P7Q3M5X8C2V6B9N4K1H0TZ", "attempt": 1,
    "fetched_at": "2026-10-06T09:14:22Z",
    "paid": true,
    "retention_class": "x_24h_sync",
    "client_ids": ["3e8f1a2b-7c4d-4b9e-a1f0-6d2c5e8b7a14"],
    "batch": "raw/green/x/2026/10/06/x-full-archive-search/000012.jsonl.zst",
    "metrics_observation": "backfill"
  },
  "payload": { "...": "the post and its includes from 5.4, unchanged" }
}
```

`job_kind` is `backfill`, `keyword_history` or `replies`; keyword_history messages carry the keyword-rule `source_id`; replies messages add `post_ref` and otherwise match x-replies-fetcher's. Also written: the poller's cursor seed; progress rows; `jobs.completed` (for replies with `post_ref`, `series_step` and the window's `end_time`, which comment-decay-scheduler records as that step so x-replies-fetcher reads only newer replies); `source.events` (`updated` when an account is unavailable); ledger entries; `service_runs`; `dlq.x-full-archive-search`.

### 6.3 State

This service's `cursors` row per source holds the running job's progress (`job_id`, `next_token`, oldest `created_at`, highest id, paid reads), cleared at job end, plus `last_success_at`, `last_error`, `consecutive_errors`. A replay resumes from it; if X rejects the `next_token`, the job restarts with `end_time` = the oldest `created_at` read. Ledger and counters live in quota-governor.

## 7. Limits, quotas and cost

- Price: USD 0.005 per post read and USD 0.010 per user read, deduplicated per resource per UTC day. Every result is a post read, paid unless today's ledger holds its id. 1,000 posts cost USD 5.00; a 90-day backfill costs USD 0.45 per post a day of the account's posting rate.
- A re-read on a later UTC day is paid again, so retries resume from stored progress.
- Per-job caps, one per job kind, sit in `budgets` under `x_pay_per_use`, set by Abdullah and ops; this PRD sets no value.
- Cap: 3,000,000 post reads per month on pay-per-use (USD 15,000), shared by the seven x-* services. Quota-governor runs normal below 80%, stretch from 80% (priorities 1 to 3; from 95% only 1 and 2), exhausted at 100%. Backfill is priority 5 always, so from 80% new accounts enter rotation without history; client requests stop only at their cap or exhaustion. History's share is to be measured in the pilot.
- If the `author_id` expansion is billed as a user read, keyword_history and replies jobs pay USD 0.010 per distinct author per UTC day on `user_reads` (to be confirmed in the pilot).
- Terms: no surveillance, no monitoring of sensitive events (protests, rallies), no sensitive-attribute profiling; a Government End User needs Enterprise; deletions mirrored within 24 hours (`x_24h_sync`, via x-compliance-sync).

## 8. Failure handling and fallback

- HTTP 429: backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts, `dlq.x-full-archive-search`, an alert, and a `capped` report for what was read, so the account still enters rotation.
- HTTP 401 and 403: mark the app token `degraded`, stop, alert; never rotate tokens or IPs.
- HTTP 400 on a query: no retry; DLQ with `query_rejected`; the requester is told.
- Account not found, suspended or protected: `health = blocked`, `source.events` `updated` with the reason, report `done`.
- Empty 200: normal for quiet accounts and rare terms, so counted only on source-health-canary's one-page searches of `canary_targets` accounts that post daily; above 5% in 15 minutes it sets `health = degraded`. X has no amber route: `fallback_on` is never set.
- Budget deny: `capped`, not an error. Schema change: payload archived; normalize-item raises `schema_unknown`.

## 9. Non-functional requirements

- Throughput: bounded by budget, not compute; the whole x-* cap is 3,000,000 reads (30,000 full pages) a month; this service's share and new accounts a day are to be measured in the pilot. Pages within a job are sequential; jobs run in parallel across sources.
- Latency: a backfill ends within the account's first tier interval. Idempotency: `x:post:<id>`; replayable jobs; progress and seed only after acknowledgement. Scaling: stateless workers on queue depth.
- Security: bearer token per job from Supabase Vault, never logged; no account pools or proxies; `from:` only on qualified accounts; keyword history only on registered client terms; government clients only under an Enterprise plan naming them.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status,kind}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `post_reads_total{paid,job_kind}`, `jobs_capped_total{reason}`, `estimate_ratio` (paid reads ÷ estimate) and `backfill_age_seconds` (oldest pending account); rotation metrics do not apply. Alerts: `backfill_overdue` (pending past its first tier interval), `token_degraded`, `dlq_nonempty`, `query_rejected`, `empty_200_rate` (above 5% in 15 minutes), `estimate_drift` (threshold from pilot data).

## 11. Dependencies

listening-sdk, quota-governor (allowance and the read ledger defined by x-recent-search), backfill-orchestrator, x-user-timeline-poller, x-recent-search, x-filtered-stream, x-replies-fetcher, x-user-resolver, comment-decay-scheduler, normalize-item, raw-archiver, source-health-canary, x-compliance-sync, Supabase Postgres and Vault, Redpanda; an X pay-per-use developer app.

## 12. Risks and mitigations

- A window back to 2006 or a busy term drains the month: per-job caps, estimate before allowance, cost per job kind in `jobs.completed`.
- A client seed list adds many accounts at once: priority 5 sheds backfill first; every account still enters rotation.
- History used for sensitive-event monitoring: qualifier-admitted accounts and registered client terms only; government only under Enterprise.
- A late or repeated backfill would lower the poller's cursor: the seed only raises it.

## 13. Acceptance criteria

1. A `backfill` job with no known posting rate asks quota-governor for exactly the per-job cap at priority 5 on `post_reads`; a `keyword_history` job asks at priority 1.
2. On a simulated X API, a 90-day backfill of three pages follows `next_token`, sends `-is:retweet`, writes one `raw.items` message per post with `job_kind = backfill`, and reports `done` with `pages = 3`.
3. After that job, x-user-timeline-poller's cursor equals the highest id read (numeric comparison), written before `jobs.completed`; a higher existing cursor is left unchanged.
4. When paid reads reach the per-job cap mid-window, the job stops, seeds the cursor with the newest id read and reports `capped`; x-user-timeline-poller polls the account within one scan after backfill-orchestrator sets `next_poll_at = now()`.
5. Above 80% of the period budget, a backfill is reported `capped` with `pages = 0` on its first attempt and no cursor written, while a priority-1 replies job runs.
6. A post already in today's ledger is written `paid = false` and leaves `post_reads` unchanged; `cost_units` equals the job's paid reads.
7. A worker killed after page 2 of 5 resumes on replay from stored progress, re-emits at most one page with the same `idempotency_key` values, and normalize-item stores each post once.
8. A `replies` job for a 20-day-old post queries `conversation_id:<root id>` from the post's `created_at` to job start minus 7 days and reports with its `post_ref` and `series_step`.
9. A backfill for an individual or a keyword rule, a keyword_history job on terms not registered for its client, and a job whose only clients are government clients without X Enterprise all end without an API call.
10. After 5 failed attempts on HTTP 429, the job is in `dlq.x-full-archive-search`, an alert fired, and the account was reported `capped`.
11. Every message carries `route = green`, `vendor = null`, `paid`, `retention_class = x_24h_sync`; the bearer token never appears in logs or envelopes.

## 14. Open questions

1. The addendum's job kinds have no `keyword_history`: add it to the listening-sdk schema, or carry it as `backfill` with a client flag (and a priority exception)?
2. Align the replies hand-back with the x-replies-fetcher PRD: where the boundary `end_time` is stored.
3. Is the `author_id` expansion billed as a user read? keyword_history and replies pages hold many authors.
4. Who screens a client's terms for sensitive events before a history request, and where is that recorded?
5. Should keyword_history posts feed discovery (old authors becoming candidates and new backfills), or be marked history-only for keyword-matcher?
6. Does backfill-orchestrator re-request a `capped` account's missing history when a new billing cycle opens?
