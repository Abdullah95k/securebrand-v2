# x-recent-search

**Platform:** X · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend lead, X adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

X is the only platform in the stack with a green keyword search over third-party public posts: Facebook has none under PPCA, Instagram offers hashtags only, TikTok, Telegram and LinkedIn search are amber. x-recent-search runs every client keyword set against `GET /2/tweets/search/recent` on the X API v2 pay-per-use plan and turns matches into raw items and discovery hits.

Without it the X lane has no mentions from accounts we do not already watch, the registry on X grows only through client seed lists (nothing for poster-resolver, x-user-resolver or the qualifier to work on), x-filtered-stream cannot fill the gap after a disconnect, and x-replies-fetcher has no endpoint, because threads are read through the same search with `conversation_id:`. X is 0.6M of the 30.5M items a month at full scale.

## 2. Objective (the end state this service delivers)

Every X keyword rule is searched on a fixed cadence (tier 1 every 15 minutes, every other active rule hourly), every match reaches `raw.items` within one interval of being posted, every unregistered poster becomes a `discovery.hits` message, and no post read is paid twice within a UTC day. Target: staleness p95 below 15 minutes for tier-1 rules and 60 minutes for the rest; rotation lag below one interval for 99% of rules per day; paid reads in our ledger and on X's invoice agree within 1%; zero jobs lost.

## 3. Scope

### In scope

- Rotation of keyword-rule searches with `since_id` cursors; catch-up after outages.
- The query builder: Arabic spelling variants, Kurdish (Sorani) forms, transliterations and brand handles from the client keyword sets, with `-is:retweet`, `lang:ar` and `place_country:IQ`.
- The UTC-day read ledger: a read counts as paid only on its first read of the day, and queries never ask again for posts read on an earlier day.
- Writing `raw.items` (kind `post`) and `discovery.hits`; gap backfill for x-filtered-stream.

### Out of scope

- Anything older than 7 days (x-full-archive-search), threads (x-replies-fetcher), registry timelines (x-user-timeline-poller), real time (x-filtered-stream), profiles (x-user-resolver), deletions (x-compliance-sync).
- Qualification (poster-resolver, qualifier, registry-writer); deduplication (normalize-item); `item.hits` for registered posters (keyword-matcher).

## 4. Users and consumers

- **Clients** see "mentions of my brand on X, never older than 15 minutes for priority terms, one hour for the rest", plus the candidates the qualifier admits from these hits.
- **Ops** watches rotation lag, the paid-read counter against the 3,000,000 monthly cap and the DLQ; it can force one rule from the control plane.
- **Downstream**: normalize-item, lang-dialect-id, poster-resolver, qualifier, keyword-matcher, raw-archiver, quota-governor, x-filtered-stream, alert-evaluator. The provenance statement names this service as the green fetcher of every mention it found.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.x-recent-search`, partitioned by the keyword rule's `source_id`, emitted by the rotation scheduler inside this service (one leader replica, Postgres advisory lock) for `sources` rows with `platform = x`, `source_type = keyword_rule`, `health != blocked` and `next_poll_at <= now()`.

**Cadence.** A keyword rule has no follower count, so tier means priority: tier 1 (on a client's priority list) every 15 minutes; tier 2, tier 3 and dormant rules every 60 minutes (an empty result costs USD 0 in reads); retired rules are not searched.

**Keeping every rule on rotation.** `next_poll_at` is set from the START of the last run (fixed cadence, no drift). Jobs are ordered by `next_poll_at` then by tier, so an overdue hourly rule is never skipped twice in a row behind tier-1 rules. A failed job keeps its old `next_poll_at` and is first on the next scan.

**Catch-up.** When `rotation_lag_seconds` exceeds one interval the scheduler orders most-stale-first and raises `rotation_behind`; workers scale on partition lag. Runs are incremental from `since_id` inside a 7-day window, so a late rule loses nothing for up to 7 days; a cursor older than that triggers one `keyword_history` job on x-full-archive-search (budget gated) before the rule resumes here.

**Split with the stream.** Tier-1 keyword rules also run as stream rules on x-filtered-stream; the 15-minute search stays on as the safety net, and posts the stream already delivered that UTC day are free under X's per-day deduplication.

**Backfill on add.** A new rule is searched once over the full 7-day window (no `since_id`), then joins the rotation; older history is a `keyword_history` job on x-full-archive-search, created by backfill-orchestrator on client request.

### 5.2 Step by step

1. Consume a job (`source_id`, `tier`, `attempt`, `reason` = rotation | first_run | gap_backfill | ops_force); read the `sources`, `keywords` and `cursors` rows.
2. Build the queries (5.3); a query over the length limit (to be measured in the pilot) is split by variant group.
3. Ask quota-governor for allowance under `budget_tag = x_pay_per_use`, sized at the rule's trailing average of new posts per run; `wait-until` requeues for that time, `deny` counts `quota_denied_total`.
4. Call with `since_id` from the cursor and `max_results=100`; follow `meta.next_token` until absent.
5. Per post: `idempotency_key = x:post:<id>`; `paid = false` when the ledger already holds the id for today; look `author_id` up in the registry's `platform_id` index.
6. Write one `raw.items` message per post and one `discovery.hits` message per unregistered author, flagging the envelope `context.discovery_hit_emitted = true` so keyword-matcher does not emit a second one.
7. After the Redpanda acknowledgement: advance the cursor to `meta.newest_id`, update `last_polled_at`, `next_poll_at`, `last_hit_at`; report paid and free reads to quota-governor; write `service_runs`.

### 5.3 The call it makes

```
GET /2/tweets/search/recent
  ?query=<built query, below>
  &max_results=100
  &since_id=<cursor: newest_id of the last acknowledged run>
  &tweet.fields=created_at,public_metrics,conversation_id,lang,geo,entities
  &expansions=author_id,attachments.media_keys
  &next_token=<meta.next_token of the previous page>
Authorization: Bearer <app bearer token of the company X app, from Supabase Vault, injected per job>
```

Query builder for one rule, "Dijlah Telecom", with Arabic, Kurdish and handle variants:

```
Arabic arm:  ("دجلة تيليكوم" OR "دجله تيليكوم" OR "دجلة تلكوم" OR dijlahtelecom) -is:retweet (lang:ar OR place_country:IQ)
Kurdish arm: ("دیجلە تێلیکۆم" OR "دیجله تیلیکۆم") -is:retweet
```

Variants are OR-grouped, multi-word variants quoted, handles added as plain terms, client exclusions with a leading minus. `-is:retweet` always, because retweet counts arrive in `public_metrics`; `lang:ar OR place_country:IQ` keeps geo-tagged Iraqi posts in any language and Arabic posts from anywhere for lang-dialect-id to grade; the Kurdish arm has no `lang:` operator because the Sorani words are the filter.

### 5.4 What it gets

Per post: `id`, `text`, `author_id`, `conversation_id`, `created_at`, `lang`, `public_metrics` (`retweet_count`, `reply_count`, `like_count`, `quote_count`, further counters stored as is), `geo.place_id` when geo-tagged, `entities` (hashtags, mentions, urls, annotations); `includes.users` with `id`, `name`, `username` (default fields only) and `includes.media` with `media_key` and `type`; `meta` with `newest_id`, `oldest_id`, `result_count`, `next_token`.

What it does not get: posts older than 7 days; posts of protected, deleted or suspended accounts; follower counts, verification, location or description (x-user-resolver); threads (x-replies-fetcher); standalone quote posts unless they match the terms.

## 6. Inputs and outputs

### 6.1 Reads

- Control plane: `sources` (keyword rules and the `platform_id` index of registered X accounts), `keywords`, `clients`, `cursors`, `budgets` through quota-governor.
- Queue `jobs.x-recent-search`; topic `source.events` (`added`, `tier change`, `retired`).

### 6.2 Writes

`raw.items` (one message per post), `discovery.hits` (one per post with an unregistered author), `cursors`, `service_runs`, `dlq.x-recent-search` after five failed attempts. Example `raw.items` message:

```json
{
  "idempotency_key": "x:post:1843201122334455667",
  "platform": "x",
  "kind": "post",
  "platform_id": "1843201122334455667",
  "source_id": "7c1d9a2e-55b4-4f1e-8a0c-3e9f6b2d4a71",
  "source_type": "keyword_rule",
  "route": "green",
  "vendor": null,
  "service": "x-recent-search",
  "job_id": "job_01J9R4V2PX",
  "attempt": 1,
  "fetched_at": "2026-10-06T09:15:04Z",
  "retention_class": "x_24h_sync",
  "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
  "budget_tag": "x_pay_per_use",
  "cost_units": 1,
  "paid": true,
  "context": { "query_arm": "ar", "matched_terms": ["دجلة تيليكوم"], "discovery_hit_emitted": true },
  "raw": {
    "id": "1843201122334455667",
    "text": "شبكة دجلة تيليكوم بالبصرة صارت أحسن من قبل بس السعر غالي",
    "author_id": "1290000000000000045",
    "conversation_id": "1843201122334455667",
    "created_at": "2026-10-06T09:02:31.000Z",
    "lang": "ar",
    "public_metrics": { "retweet_count": 2, "reply_count": 5, "like_count": 38, "quote_count": 1 }
  },
  "includes": { "users": [ { "id": "1290000000000000045", "username": "abuali_basra" } ] }
}
```

`discovery.hits` carries `platform`, `item_idempotency_key`, `author_platform_id`, `author_handle`, `keyword_rule_id`, `matched_terms`, `client_ids`, `lang`, `public_metrics`, `service`, `fetched_at`.

### 6.3 State

- `cursors`: cursor = `newest_id` per rule; `last_success_at`, `last_error`, `consecutive_errors`. `sources`: `next_poll_at`, `last_polled_at`, `last_hit_at`.
- The UTC-day read ledger (post ids read today, shared by all seven x-* services) is held by quota-governor under `x_pay_per_use`; this service reports to it and queries it.
- In memory: leader lock, backoff state, the rate-limit headers of the last response.

## 7. Limits, quotas and cost

- Pay-per-use: USD 0.005 per post read, USD 0.010 per user read, deduplicated per resource per UTC day; hard cap 3,000,000 post reads per billing cycle; filtered stream up to 1,000 rules (x-filtered-stream). Budget tag `x_pay_per_use`, one pool for all x-* services; quota-governor keeps the monthly paid-read counter and answers allow / wait-until / deny before every job. At 80% of the cap it cuts x-full-archive-search jobs first, then stretches tier-2 and tier-3 searches to daily, then drops reply steps after +24 h; tier-1 searches, the stream and tier-1 timelines go last.
- Cost at full scale: if all 0.6M X posts a month were first read here, USD 3,000 a month; the split with x-filtered-stream and x-user-timeline-poller, and whether `expansions=author_id` is billed as user reads (the expansion is dropped if so), are to be measured in the pilot.
- Per-endpoint request-rate ceilings are not in our fact sheet; the service honours the rate-limit headers X returns; to be measured in the pilot.
- Developer Agreement: no surveillance; no monitoring of sensitive events (protests, rallies), so keyword rules naming such events are rejected at registry review and refused by the builder; no profiling on sensitive attributes; a Government End User requires an Enterprise plan, must be named at use-case review, and X may refuse; self-serve plans serve a limited number of end users, so the company moves to Enterprise once a government end user or several clients are on board; deletions mirrored within 24 hours by x-compliance-sync.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.x-recent-search` and an alert fires.
- HTTP 401 and 403: the app token is marked `degraded`, the batch stops, ops is alerted; no second app, account or IP is ever tried.
- Empty 200 (`result_count = 0` on a rule that had hits in the last 7 days): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. There is no amber fallback on X.
- Schema change: raw payload archived; normalize-item raises `schema_unknown` and parks the batch. Partial write: cursors advance only after the Redpanda acknowledgement; a replayed job re-emits the same posts, which normalize-item deduplicates and the ledger marks free.
- Query rejected (HTTP 400): the rule is parked `degraded` with the query in `review_queue` until ops fixes it.

## 9. Non-functional requirements

- Throughput: with the 200-keyword planning set the web-search sheet uses, a quarter tier 1, the rotation makes about 8,400 requests a day before pagination; posts a day are to be measured in the pilot, with 20,000 a day (0.6M a month) as the X-wide ceiling.
- Latency: `staleness_seconds_p95` under 15 minutes (tier 1) and 60 minutes (others). Idempotency: `x:post:<id>`; jobs replayable; `raw.items` append-only. Scaling: stateless workers on partition lag; one leader scheduler.
- Security: bearer token from Supabase Vault per job, never logged; no account pools, no proxies; every message carries route, vendor, service and fetch time; retention class `x_24h_sync`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `x_post_reads_paid_total`, `x_post_reads_free_total`, `x_cap_consumed_ratio`, `quota_denied_total`, `dlq_total`, `rules_in_rotation{tier}`, `discovery_hits_total`. Alerts: `rotation_behind`, `token_degraded`, `dlq_nonempty`, `empty_200_rate`, `x_cap_80_percent`, `query_rejected`. SLO: rotation lag below one interval for 99% of rules per day.

## 11. Dependencies

listening-sdk, quota-governor (budget and the read ledger), source-health-canary, raw-archiver, normalize-item, lang-dialect-id, keyword-matcher, poster-resolver, qualifier, registry-writer, backfill-orchestrator, x-full-archive-search, x-filtered-stream, Supabase Postgres and Vault, Redpanda. X prerequisites: the company app on pay-per-use with a completed use-case review; Enterprise before any government end user.


## 12. Risks and mitigations

- A broad term (a common Arabic word) burns the cap: the builder requires one distinctive variant per rule, ops sets broad rules to tier 3, the governor denies at pool level before the cap.
- Expansions billed as user reads double the cost: measured in the first pilot week; expansion dropped if so.
- A government end user before Enterprise: the registry refuses X rules whose `client_ids` carry a government flag until the Enterprise contract is recorded in `clients`.

## 13. Acceptance criteria

1. A tier-1 rule run at 09:00:00 has `next_poll_at = 09:15:00` even when the run took 3 minutes; a tier-2 rule gets `10:00:00`.
2. With 100 rules across tiers and a simulated API for 24 hours, no rule's `rotation_lag_seconds` exceeds its interval.
3. The builder turns the fixture set (4 Arabic variants, 2 Kurdish forms, 1 handle, 1 exclusion) into exactly the two query strings in 5.3.
4. A run sends `since_id` equal to the previous run's `newest_id`, follows `next_token` until absent, and advances the cursor only after the Redpanda acknowledgement.
5. A post returned by two rules on the same UTC day appears twice in `raw.items` with one `idempotency_key`, once `paid = true` and once `paid = false`; the governor's counter rises by one.
6. A post by a registered X account yields no `discovery.hits`; one by an unregistered author yields exactly one.
7. On `deny` from quota-governor no HTTP call is made and `quota_denied_total` rises by one.
8. A simulated 429 sequence backs off from 30 s to at most 15 min and lands the job in `dlq.x-recent-search` after 5 attempts; a 401 marks the token `degraded`, stops the batch and alerts.
9. A rule carrying a sensitive-event term is refused by the builder and never produces a request.
10. A rule whose cursor is 8 days old produces one `keyword_history` request for x-full-archive-search and no recent-search call beyond the window.

## 14. Open questions

1. Maximum query length, and whether `lang:ckb` is accepted on pay-per-use: to be measured in the pilot.
2. Whether plain handle terms match mentions, or a mention operator is needed: to be measured in the pilot.
3. Timing of the Enterprise move: first government end user or second paying client, whichever comes first.
