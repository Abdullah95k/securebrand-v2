# x-user-timeline-poller

**Platform:** X · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, X adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

On X, the accounts clients follow (ministries, state companies, outlets, brands, public figures) often speak first, and their posts open the reply threads where public reaction shows. Volume is small (0.6M of 30.5M items a month at full scale) but every post read is billed. x-user-timeline-poller keeps every registered X account checked for new posts through the official X API v2 user timeline, reading only what is newer than the last stored post.

x-filtered-stream pushes posts live, but only for accounts its rules cover (at most 1,000 rules). Without this service, other accounts would surface only through keyword hits in x-recent-search, missed pushes would stay missing, and x-replies-fetcher would get no reply series for them. The product would lose per-account history, share of voice, response tracking and the freshness promise for every X account outside the stream.

## 2. Objective (the end state this service delivers)

Every registered green X account with an active tier is checked on its cadence (stream-covered accounts reconciled daily, others polled by tier), every new post reaches `raw.items` within its tier interval, and the cursor advances only after Redpanda acknowledges the batch. Target: rotation lag below one tier interval for 99% of accounts per day; staleness p95 within the tier maximum (1 h, 6 h, 24 h); zero jobs lost; no post id counted twice in `post_reads` on one UTC day.

## 3. Scope

### In scope

- Tier rotation of every registered green X account, daily reconciliation of stream-covered accounts, execution of `jobs.x-user-timeline-poller`.
- Incremental reads from `since_id`; ledger check, quota-governor allowance and a `paid` flag per post.
- `raw.items` (kind `post`; `public_metrics` are the first metrics observation); cursors; dormant promotion; `rotation_behind` catch-up.

### Out of scope

- First read of a new account (backfill-orchestrator through x-full-archive-search); push and rules (x-filtered-stream); keyword search (x-recent-search); replies and quotes (x-replies-fetcher); handle-to-id resolution (x-user-resolver); deletion mirroring (x-compliance-sync).
- Metrics refreshes at +24 h and +7 d (old posts are never re-read here); individuals, hashtags, keyword rules; deduplication (normalize-item); tier decisions (qualifier, registry-writer).

## 4. Users and consumers

- **Clients** see new posts from the X accounts they watch, never older than their tier allows.
- **Ops** watches rotation lag, `x_pay_per_use` spend, token health and the DLQ, and can force a poll (`ops_force`).
- **Downstream**: normalize-item, comment-decay-scheduler and x-replies-fetcher (reply series), x-compliance-sync (checks stored post ids), raw-archiver, source-health-canary, quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.x-user-timeline-poller`, partitioned by `source_id`, emitted by this service's rotation scheduler (one leader replica under a Postgres advisory lock, scan period well inside 60 minutes) for `sources` rows with `platform = x`, `source_type = account`, `route = green`, `tier != retired`, `health != blocked`, `backfill_status in (done, capped)` and `next_poll_at <= now()`.

**Cadence by tier.** Tier 1 (100,000 or more followers, or on a client's priority list): every 60 minutes. Tier 2 (10,000 to 99,999): every 6 hours. Tier 3 (below 10,000): every 24 hours. Dormant (no post in 30 days): weekly; a new post promotes the account back to its reach tier through `source.events` (`tier change`). Retired: never.

**Stream-covered accounts.** Accounts covered by x-filtered-stream's rules (at most 1,000 rules, tier-1 accounts first) arrive by push and get one `reconciliation` poll every 24 hours here. Coverage is read from x-filtered-stream's `cursors` rows. `sources.tier` keeps the reach tier, so an account whose rule is dropped, or every covered account while `service_runs` shows the stream disconnected, returns to tier cadence with `next_poll_at = now()`. Reconciliation slots are spread over 22:00 to 23:59 UTC (01:00 to 03:00 Baghdad, night hours) by a hash of `source_id`, and an account entering coverage gets its next slot, so nearly every re-read of a streamed post falls on the same UTC day and is not paid twice.

**Keeping every account on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + interval`), so cadence does not drift. Jobs are ordered by `next_poll_at` then tier, so no account is skipped twice in a row; an account is in one job at most; a failed or denied job keeps its `next_poll_at` and leads the next scan.

**Catch-up.** When `rotation_lag_seconds` exceeds one interval, the scheduler polls most-stale-first and raises `rotation_behind`. Every poll reads from `since_id`, so lateness costs freshness, not completeness.

**Backfill on add.** A new account (`backfill_status = pending`) is first read by backfill-orchestrator through x-full-archive-search, which seeds this service's cursor and sets `done` or `capped` and `next_poll_at = now()`.

**Reply series.** New posts reach comment-decay-scheduler through `items.normalized`, and it opens the X series x-replies-fetcher works by `conversation_id:` (+1 h, +6 h, +24 h, +3 d).

### 5.2 Step by step

1. Consume a job (`job_id`, `source_id`, `kind` = rotation | reconciliation | ops_force, `attempt`); load the `sources` row and cursor; stop if `health = blocked`.
2. Remove government clients without an X Enterprise plan naming them from `client_ids`; skip the job if they were its only clients.
3. Before each page, ask quota-governor `{budget_tag: x_pay_per_use, amount: 100, service: x-user-timeline-poller, priority, sub_counter: post_reads, resource_ids: []}` (a full page: ids are unknown until it returns); priority 1 for tier 1 and `ops_force`, 2 for tier 2, 3 otherwise. `wait_until` requeues; `deny` keeps `next_poll_at`.
4. Call the timeline (5.3) with `since_id = cursor`; an empty cursor reads one page without `since_id`.
5. Settle each page by sending its post ids to the ledger: ids already held today get `paid = false`; the rest are `paid = true` and count in `post_reads`.
6. Write one `raw.items` message per post; raw-archiver lands the batch under `raw/green/x/<yyyy>/<mm>/<dd>/x-user-timeline-poller/`.
7. After Redpanda acknowledges: cursor = highest id seen (compared as 64-bit integers, not strings); set `last_success_at`, `consecutive_errors = 0`, `last_polled_at`, `next_poll_at`; emit `tier change` if a dormant account posted.
8. The listening-sdk wrapper writes `jobs.completed/v1` with `new_count` = posts returned, `seen_count` = posts with `paid = false`, `pages`, and `cost_units` = paid reads.

### 5.3 The call it makes

```
GET /2/users/{id}/tweets
  ?since_id=<cursor>
  &max_results=100
  &tweet.fields=created_at,public_metrics,conversation_id,lang,geo,entities
  &expansions=author_id,attachments.media_keys
  &pagination_token=<next_token of the previous page; absent on the first>
Authorization: Bearer <app bearer token of the company X app, from Supabase Vault per job>
```

`{id}` is the numeric user id in `sources.platform_id` (from x-user-resolver), never the handle, so a renamed account stays on rotation. Page size 100; follow `next_token` until absent. Anything else (base URL, the request rate limit on pay-per-use, how far back `since_id` paging reaches) is to be confirmed in the pilot.

### 5.4 What it gets

Per post: `id`, `text`, `edit_history_tweet_ids` and the requested fields; `includes.users` holds the author (`id`, `name`, `username`), `includes.media` each `media_key` and `type`. Example:

```json
{
  "data": {
    "id": "2107360526334088839",
    "edit_history_tweet_ids": ["2107360526334088839"],
    "text": "افتتاح فرعنا الجديد في #البصرة يوم الخميس",
    "created_at": "2026-10-06T06:41:17.000Z",
    "author_id": "1172893456012345344",
    "conversation_id": "2107360526334088839",
    "lang": "ar",
    "public_metrics": {"retweet_count": 18, "reply_count": 46, "like_count": 412, "quote_count": 5, "bookmark_count": 9, "impression_count": 38120},
    "entities": {"hashtags": [{"start": 23, "end": 30, "tag": "البصرة"}]},
    "attachments": {"media_keys": ["3_2107360398765432832"]}
  },
  "includes": {
    "users": [{"id": "1172893456012345344", "name": "Basra Retail Group", "username": "basraretailgrp"}],
    "media": [{"media_key": "3_2107360398765432832", "type": "photo"}]
  }
}
```

Not returned: other users' replies and quotes (x-replies-fetcher); follower counts (x-user-resolver); place details (`geo` holds only a `place_id`, on geotagged posts); media URLs (`media.fields` not requested); later deletions (x-compliance-sync).

## 6. Inputs and outputs

### 6.1 Reads

`jobs.x-user-timeline-poller`; `sources`, `cursors` (own rows and x-filtered-stream's coverage rows), `clients` (X Enterprise entitlement), `service_runs` (stream state); `budgets` and the read ledger through quota-governor; `source.events` (`added`, `tier change`, `dormant`, `retired`).

### 6.2 Writes

`raw.items`, one message per post: envelope plus the post and its referenced `includes`, unchanged:

```json
{
  "envelope": {
    "platform": "x", "kind": "post", "route": "green", "vendor": null,
    "service": "x-user-timeline-poller",
    "source_id": "a4d2c9e1-5b7f-4e3a-8c60-2f1b9d7e4a35",
    "platform_id": "2107360526334088839",
    "idempotency_key": "x:post:2107360526334088839",
    "job_id": "01J9P4K8W2R6T0Y3N7B5D1F9HC", "attempt": 1,
    "fetched_at": "2026-10-06T07:00:41Z",
    "paid": true,
    "retention_class": "x_24h_sync",
    "client_ids": ["3e8f1a2b-7c4d-4b9e-a1f0-6d2c5e8b7a14"],
    "batch": "raw/green/x/2026/10/06/x-user-timeline-poller/000087.jsonl.zst",
    "metrics_observation": "poll"
  },
  "payload": { "...": "the post and its includes from 5.4, unchanged" }
}
```

Also `jobs.completed`, `source.events` (`tier change`; `updated` when an account becomes unavailable), ledger entries, `service_runs`, and `dlq.x-user-timeline-poller` after 5 failed attempts.

### 6.3 State

`cursors.cursor` = highest stored post id as a decimal string (the next `since_id`), plus `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`; ledger and `x_pay_per_use` counters in quota-governor; in memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- Price: USD 0.005 per post read and USD 0.010 per user read, deduplicated per resource per UTC day. Every returned post is a post read, paid unless today's ledger holds its id; a poll with nothing new reads no post and costs USD 0 (to be confirmed in the pilot). Reading each of X's 0.6M items a month once would cost USD 3,000 across the x-* services; this service's share is to be measured in the pilot.
- No overlap window, unlike Facebook: a re-read on a later UTC day is paid again, so `since_id` is used exactly.
- Cap: 3,000,000 post reads per month on pay-per-use, shared by the seven x-* services under `x_pay_per_use`. Quota-governor runs normal below 80% of the period budget, stretch from 80% (priorities 1 to 3; from 95% only 1 and 2), exhausted at 100%; with the budget at the cap, stretch starts at 2,400,000 reads and the 95% band at 2,850,000. The stream's 1,000-rule limit bounds how many accounts leave the tier rotation.
- Terms (Developer Agreement): no surveillance, no monitoring of sensitive events (protests, rallies), no profiling on sensitive attributes; a Government End User requires an Enterprise plan, must be named at use-case review, and X may refuse; deletions are mirrored within 24 hours (retention class `x_24h_sync`, through x-compliance-sync).

## 8. Failure handling and fallback

- HTTP 429: backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts, `dlq.x-user-timeline-poller` and an alert.
- HTTP 401 and 403: mark the app token `degraded`, stop the batch, alert, emit nothing until ops restores it; never rotate tokens or IPs around a block.
- Account not found, suspended or protected: `health = blocked` and `source.events` `updated` with the reason.
- Empty 200: normal for a quiet account, so counted only on `canary_targets` accounts that post more often than they are polled; above 5% in 15 minutes source-health-canary sets `health = degraded`. X has no amber route: `fallback_on` is never set.
- Budget: priorities the governor's mode no longer admits are not emitted, rather than asked every scan.
- Schema change: payload archived; normalize-item raises `schema_unknown` and parks the batch.

## 9. Non-functional requirements

- Throughput: X is 0.6M items a month at full scale; calls a day ≈ 24 × uncovered tier-1 + 4 × tier-2 + tier-3 + covered + dormant ÷ 7 accounts, plus extra pages; account counts to be measured in the pilot.
- Latency: tier interval plus fetch time; missed pushes within 24 hours. Idempotency: `x:post:<id>`, replayable jobs. Scaling: stateless workers on partition lag, one leader scheduler.
- Security: bearer token per job from Supabase Vault, never logged; no account pools or proxies; organizations and public figures only, never individuals; government clients only under an Enterprise plan naming them.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status,kind}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `post_reads_total{paid}` and `reconciliation_paid_reads_total`. Alerts: `rotation_behind`, `token_degraded`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`, `missed_push_rate` (threshold from pilot data). SLO: rotation lag below one tier interval for 99% of accounts per day.

## 11. Dependencies

listening-sdk, quota-governor (allowance and the read ledger defined by x-recent-search), x-filtered-stream, backfill-orchestrator, x-full-archive-search, x-user-resolver, comment-decay-scheduler, x-replies-fetcher, normalize-item, x-compliance-sync, source-health-canary, raw-archiver, registry-writer, Supabase Postgres and Vault, Redpanda; an X pay-per-use developer app.

## 12. Risks and mitigations

- Spend grows with the registry: governor modes shed tier 3, dormant and reconciliation first; monthly cost per tier comes from `jobs.completed`.
- The stream misses posts silently: reconciliation catches them within 24 hours; `missed_push_rate` alerts.
- Sensitive-event monitoring: only qualifier-admitted accounts are polled; `ops_force` cannot target an account outside the registry.

## 13. Acceptance criteria

1. A tier-1 account whose poll started at 09:00:00 gets `next_poll_at = 10:00:00` although the fetch took 4 minutes.
2. With 100 fixture accounts across tiers 1 to 3 and dormant on a simulated X API for 24 hours, no account's lag exceeds its interval.
3. A three-page response is followed through `next_token`; the cursor becomes the highest id returned, compared numerically.
4. A post already in today's ledger is written `paid = false` and leaves `post_reads` unchanged; read again after 00:00 UTC it is `paid = true`.
5. If the Redpanda produce fails the cursor does not advance; the retry re-emits the same `idempotency_key` values and normalize-item stores each post once.
6. A covered account is polled once in 24 hours, between 22:00 and 23:59 UTC; when its rule is removed or the stream disconnects, it is polled within one scan, then on tier cadence.
7. A simulated 429 backs off from 30 s to at most 15 min; after 5 attempts the job is in `dlq.x-user-timeline-poller` and an alert fired.
8. Above 95% of the period budget, tier-3, dormant and reconciliation jobs keep their `next_poll_at` while tier-1 and tier-2 jobs run.
9. Every message carries `route = green`, `vendor = null`, `paid`, `retention_class = x_24h_sync` and `public_metrics`; a `pending` account is never emitted; the bearer token never appears in logs or envelopes.
10. Each job writes one `jobs.completed/v1` event whose `cost_units` equals its paid reads; a dormant account that posts gets `tier change`.

## 14. Open questions

1. Confirm with the x-filtered-stream PRD that coverage is published as its `cursors` rows and its connection state in `service_runs`.
2. Should reposts and the account's own replies be excluded to save reads? Decided from their pilot share.
3. Is the `author_id` expansion billed as a user read (at most USD 0.010 per account per UTC day)? If so, drop it.
4. Confirm with quota-governor's owner that a 100-read page reservation is trued up to the ids returned.
5. Which `clients` column records a government client's X Enterprise entitlement?
