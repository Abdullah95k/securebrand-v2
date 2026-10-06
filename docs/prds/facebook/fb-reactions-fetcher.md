# fb-reactions-fetcher

**Platform:** Facebook · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, Facebook adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A post's text tells a client what a Page said; its reactions tell the client how Iraq responded. The split between like, love, haha, wow, sad, angry and care is the cheapest sentiment signal on Facebook, it needs no model, and it is the one number marketing teams already understand. It is also time-dependent: a post that has 40 angry reactions one hour after publication and 4,000 a day later is a different story from one that stays flat, and the product's "velocity" and "engagement at 24 h / 7 d" views depend on seeing the counts more than once.

fb-reactions-fetcher turns the reaction, comment and share summaries that fb-page-feed-poller and fb-backfill already request on `/feed` into `item.metrics` observations, and makes the two scheduled refresh calls at +24 h and +7 d that the rotation policy promises. Without it the product would show a single, stale engagement number captured whenever the feed happened to be polled, no reaction breakdown, and no engagement timeseries for `metrics_timeseries` and `aggregates_hourly` in ClickHouse.

## 2. Objective (the end state this service delivers)

Every green Facebook post has at least three engagement observations in `item.metrics`: one at first sight (free, from the feed payload), one at +24 h and one at +7 d, each carrying the seven reaction counts plus comment and share totals, with observations continuing at every rotation poll while the post sits inside the poller's 24-hour overlap window. Target: +24 h and +7 d observations recorded within one tier interval of their due time for 95% of posts; zero extra Graph calls for the first-sight observation.

## 3. Scope

### In scope

- Extract mode: consuming `raw.items` messages of kind `post`, `platform = facebook`, `route = green`, and emitting an `item.metrics` observation from the summary fields in the payload, labelled with the envelope's `metrics_observation` (`poll`, `backfill`, `webhook_reconcile`).
- Refresh mode: jobs on `jobs.fb-reactions-fetcher` at +24 h and +7 d after `created_time`, making one Graph call per post for the seven reaction types, comment total and share count.
- Client-requested refreshes of a specific post after day 7, budget permitting.

### Out of scope

- Fetching posts (fb-page-feed-poller, fb-backfill), comments (fb-post-comments-fetcher), reactor identity (never returned under PPCA and never wanted).
- Group posts on the amber route: their engagement counts come inside the vendor payload of fb-group-posts-poller and are extracted by normalize-item.
- Aggregation and timeseries storage (store-writer, aggregator); sentiment inference from reactions (analysis-sentiment).

## 4. Users and consumers

- **Clients** see reaction breakdowns, engagement-at-24 h and 7 d, and velocity charts; they never call the service.
- **Ops** watches refresh lag and quota use.
- **store-writer** and **aggregator** consume `item.metrics` into ClickHouse `metrics_timeseries` and `aggregates_hourly`; **alert-evaluator** uses velocity for spike alerts; **comment-decay-scheduler** emits the refresh jobs (see 5.1).

## 5. How it works

### 5.1 Trigger and rotation

**Trigger 1, extract (runs with each feed poll).** The service consumes `raw.items` (consumer group `fb-reactions-fetcher`) and, for every Facebook post on the green route, emits one `item.metrics` message from the payload's `like … care`, `comments.summary.total_count` and `shares.count` fields. No Graph call is made. Because fb-page-feed-poller reads `since = cursor − 24 h`, a Tier 1 Page's post is re-read on every hourly poll during its first day, so this mode alone yields an hourly reaction series for Tier 1 posts during the window that matters most; Tier 2 and Tier 3 posts get the observations their tier cadence allows (every 6 hours, every 24 hours).

**Trigger 2, scheduled refresh at +24 h and +7 d.** The rotation policy refreshes metrics at +24 h and +7 d "by the source's metrics or details service"; for Facebook that is this service. comment-decay-scheduler, which already tracks every post's `created_time` from `items.normalized`, emits two jobs per post onto `jobs.fb-reactions-fetcher` (partitioned by `source_id`): `kind = refresh_24h` due at `created_time + 24 h` and `kind = refresh_7d` due at `created_time + 7 d`. Jobs are ordered by due time; when the service falls behind by more than one Tier 1 interval (60 minutes), it works most-overdue first and raises `metrics_behind`. A late refresh is still recorded with its true `observed_at`, never back-dated.

**Catch-up and dedup.** If an extract observation already exists within the due window (for example a Tier 1 post polled at +24 h exactly), the refresh job is still executed, because the poll may have missed the post through ranking; the store keeps both, keyed on (`item_id`, `observed_at`).

**Backfill.** Posts arriving through fb-backfill get an extract observation labelled `backfill`; comment-decay-scheduler emits refresh jobs only for the steps still in the future relative to `created_time` (a post backfilled at age 3 days gets `refresh_7d` only; older than 7 days, none).

**Beyond day 7.** No automatic refresh; a client can request one for a specific post, which arrives as `kind = refresh_client`, subject to quota-governor.

### 5.2 Step by step

Extract: 1. consume the `raw.items` message; 2. verify `platform = facebook`, `kind = post`, `route = green`; 3. read the seven `*.summary.total_count` fields, `comments.summary.total_count`, `shares.count`; 4. emit `item.metrics` with `observed_at = envelope.fetched_at` and `observation = envelope.metrics_observation`; 5. commit the consumer offset after Redpanda acknowledges the produce.

Refresh: 1. consume the job (`source_id`, `platform_id`, `kind`, `attempt`); 2. select the token as fb-page-feed-poller does (system-user token of the first healthy client in `client_ids`; Page access token for `owned_by_client` Pages), injected from Supabase Vault; 3. ask quota-governor under `budget_tag = meta_graph_pages:<client_id>`; 4. make the call in 5.3; 5. emit `item.metrics` with `observed_at = now`, `observation = refresh_24h | refresh_7d | refresh_client`; 6. record `cost_units_total` (1 per call) and the usage headers.

### 5.3 The call it makes

Refresh mode only (extract mode makes no call):

```
GET https://graph.facebook.com/v<pinned>/{post-id}
  ?fields=id,created_time,shares,
          comments.summary(total_count).limit(0),
          reactions.type(LIKE).summary(total_count).limit(0).as(like),
          reactions.type(LOVE).summary(total_count).limit(0).as(love),
          reactions.type(HAHA).summary(total_count).limit(0).as(haha),
          reactions.type(WOW).summary(total_count).limit(0).as(wow),
          reactions.type(SAD).summary(total_count).limit(0).as(sad),
          reactions.type(ANGRY).summary(total_count).limit(0).as(angry),
          reactions.type(CARE).summary(total_count).limit(0).as(care)
  &access_token=<system-user token (PPCA); Page access token for owned_by_client Pages>
```

One post per call; no pagination (`limit(0)` suppresses the reactor edge, only the summary is returned). Batching several post ids into one request with `ids=` is an optimization to be measured in the pilot.

### 5.4 What it gets

Seven integers (like, love, haha, wow, sad, angry, care), the comment total and the share count, plus `id` and `created_time`:

```json
{
  "id": "100064583471102_1198837625012734",
  "created_time": "2026-10-06T07:12:09+0000",
  "shares": {"count": 58},
  "comments": {"summary": {"total_count": 403}},
  "like": {"summary": {"total_count": 2210}}, "love": {"summary": {"total_count": 131}},
  "haha": {"summary": {"total_count": 19}}, "wow": {"summary": {"total_count": 4}},
  "sad": {"summary": {"total_count": 1}}, "angry": {"summary": {"total_count": 44}},
  "care": {"summary": {"total_count": 12}}
}
```

What it does not get: who reacted (never under PPCA); views or reach (not public for third-party Pages); per-comment likes (fb-post-comments-fetcher carries `like_count` per comment); a post that has been deleted returns an error, which becomes a `deletions` message with reason `platform_sync`.

## 6. Inputs and outputs

### 6.1 Reads

`raw.items` (extract), `jobs.fb-reactions-fetcher` (refresh); `sources` (`client_ids`, `owned_by_client`), `clients`, `budgets` through quota-governor, `health` through the SDK canary hook.

### 6.2 Writes

`item.metrics`, one message per observation:

```json
{
  "platform": "facebook",
  "item_idempotency_key": "facebook:post:100064583471102_1198837625012734",
  "platform_id": "100064583471102_1198837625012734",
  "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
  "service": "fb-reactions-fetcher",
  "route": "green",
  "vendor": null,
  "observation": "refresh_24h",
  "observed_at": "2026-10-07T07:14:51Z",
  "post_created_time": "2026-10-06T07:12:09Z",
  "age_seconds": 86562,
  "metrics": {
    "like": 2210, "love": 131, "haha": 19, "wow": 4, "sad": 1, "angry": 44, "care": 12,
    "reactions_total": 2421, "comments": 403, "shares": 58
  },
  "job_id": "01J9Q1M4V8N2B6X0C3Z7A5S9DF",
  "retention_class": "meta_on_request"
}
```

Also `deletions` (post gone on refresh), `service_runs`, `dlq.fb-reactions-fetcher`.

### 6.3 State

No cursors: extract mode is offset-based on `raw.items`; refresh jobs carry everything they need. `budgets` counters per token; `service_runs` (lag of the most overdue refresh job).

## 7. Limits, quotas and cost

- Every refresh call counts against the Pages bucket: 4,800 calls × engaged users per 24 h on a system-user token, shared with fb-page-feed-poller, fb-backfill and fb-post-comments-fetcher; quota-governor orders rotation polls first, comment series second, metrics refreshes third.
- Two calls per post (+24 h, +7 d) is the whole refresh cost; the extract path is free. At full scale the Facebook post count is to be measured in the pilot, so refresh calls per day are to be measured in the pilot.
- Error 80001 ("too many calls to this Page") defers the job per Page with backoff; a Page hitting 80001 repeatedly has its refresh jobs spread by quota-governor rather than dropped.
- Cost: USD 0 per Graph call; the cost is quota.
- The feed cap (about 600 ranked posts per Page per year, `limit` max 100) does not apply to a direct post read, so refreshes work for posts the ranking later drops, as long as we captured the id once.

## 8. Failure handling and fallback

- HTTP 429 and 80001: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts `dlq.fb-reactions-fetcher` and an alert.
- HTTP 401 and 403: token marked `degraded`, batch stopped, alert; no workaround with other tokens or IPs.
- Post not found or no longer accessible: emit `deletions` with reason `platform_sync`; no retry.
- Empty 200 (a response without the summary fields): counted; above 5% in 15 minutes source-health-canary flips `health = degraded`; there is no amber fallback for Page reactions.
- Schema change (a reaction type missing or renamed): the payload is archived, `schema_unknown` is raised, the observation is parked rather than written with zeros.
- Extract mode replays: observations are keyed on (`item_id`, `observed_at`), so re-consuming `raw.items` after a restart writes the same observation again, which store-writer upserts.

## 9. Non-functional requirements

- Throughput: extract mode must keep pace with Facebook's full-scale share of 12.0M items a month without lag above one Tier 1 interval; refresh mode is quota-bound.
- Latency: +24 h and +7 d observations within one tier interval of due time for 95% of posts.
- Idempotency: observations keyed on item and `observed_at`; jobs replayable.
- Scaling: extract workers on `raw.items` partition lag; refresh workers on `jobs.fb-reactions-fetcher` partition lag.
- Security: tokens per job from Supabase Vault, never logged; no reactor identity requested or stored; Meta data never processed for law-enforcement or national-security purposes; provenance on every message; retention `meta_on_request` (counts are derived metrics and may be kept ten years as aggregates).

## 10. Metrics and alerts

`items_fetched_total{mode}`, `items_new_total`, `jobs_total{status,kind}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `metrics_lag_seconds` (now minus due time of the most overdue refresh), `observations_total{observation}`. Alerts: `metrics_behind` (lag above 60 minutes), `token_degraded`, `dlq_nonempty`, `empty_200_rate`, `schema_unknown`.

## 11. Dependencies

listening-sdk, fb-page-feed-poller and fb-backfill (summary fields in the payload), comment-decay-scheduler (refresh jobs), quota-governor, source-health-canary, normalize-item (item ids), store-writer, aggregator, alert-evaluator, deletion-propagator, Supabase Postgres and Vault, Redpanda, ClickHouse (`metrics_timeseries`). Meta prerequisites: Business Verification, App Review for PPCA, Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- Refresh calls compete with rotation for the Pages bucket: quota-governor ranks them below polls and comment series; if the bucket is short, +7 d refreshes are dropped before +24 h ones and the gap is logged.
- Dependency on comment-decay-scheduler for job emission couples two lanes: the job contract is in the SDK; if the scheduler's PRD assigns refresh emission elsewhere, only the producer changes (open question 1).
- Reaction summaries may differ slightly between the feed call and the direct read: observations are labelled with their origin so analysts can tell them apart.
- Meta may change reaction types: `schema_unknown` parks rather than zero-fills.

## 13. Acceptance criteria

1. A `raw.items` post message from fb-page-feed-poller with the seven summaries produces exactly one `item.metrics` message with `observation = poll`, the seven counts, `comments`, `shares` and `reactions_total` equal to the sum of the seven, and no Graph call.
2. A `refresh_24h` job due at T produces one Graph call and one observation with `observed_at` within one tier interval of T in the 24-hour fixture run.
3. A `refresh_7d` job for a deleted post produces a `deletions` message with reason `platform_sync` and no retry.
4. A simulated 80001 triggers backoff from 30 s to 15 min and `attempt + 1`; after 5 attempts the job is in `dlq.fb-reactions-fetcher` and an alert fired.
5. A 401 marks the token `degraded` and stops further calls with it.
6. A post backfilled at age 3 days receives a `backfill` observation and exactly one later refresh (`refresh_7d`); a post backfilled at age 10 days receives the `backfill` observation only.
7. Re-consuming a `raw.items` partition from an earlier offset produces observations with identical (`item_id`, `observed_at`) keys and no duplicates in `metrics_timeseries`.
8. A payload with a missing reaction alias raises `schema_unknown` and writes no observation with zero-filled counts.
9. No message, log line or envelope contains reactor identity or a token.

## 14. Open questions

1. Confirm in the comment-decay-scheduler PRD that it emits the +24 h and +7 d metrics refresh jobs for Facebook; the alternative is a small due-time table owned by this service.
2. Whether to batch refreshes with `ids=`: the per-call ceiling and its effect on the Pages bucket are to be measured in the pilot.
