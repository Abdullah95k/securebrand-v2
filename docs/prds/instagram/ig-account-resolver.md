# ig-account-resolver

**Platform:** Instagram · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend lead, Instagram adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Every Instagram item that reaches a client has an author, and the registry has to decide whether that author is a source worth watching (a business or creator account, Iraqi, active) or just a person. That decision needs numbers: followers, number of posts, biography, website, name. ig-account-resolver turns an Instagram handle into that profile, through the Business Discovery field of the Instagram Graph API, and hands it to the qualifier as a `poster.profiles` message.

Without it the Instagram registry would grow only by hand. Mention authors (ig-mentions-fetcher) and keyword hits would stay anonymous candidates, no account would ever be added to the rotation of ig-account-media-poller on its own evidence, and the follower counts that set each account's tier (60 minutes, 6 hours or 24 hours) would age without anyone noticing. This service also makes sure the line the product never crosses is held in one place: a personal account is classed as an individual and is never profiled.

## 2. Objective (the end state this service delivers)

Every Instagram candidate from poster-resolver ends in exactly one outcome, `resolved` (a business or creator account with its numbers), `individual`, or `review`, with at most one Graph call per candidate per 30 days; and every registered Instagram account has its profile refreshed at least every 30 days so that tiers follow reach. Target: profile age below 30 days for 99% of registered accounts, cache hit rate reported daily, zero profiles stored on individuals.

## 3. Scope

### In scope

- Resolving candidate handles requested by poster-resolver, and refreshing registered accounts every 30 days.
- The 30-day cache, including negative results.
- Classifying each response: business or creator account, individual, age-gated or otherwise unreadable (review).
- Extracting the Iraqi signals a profile can show (+964 number, Iraqi city or governorate in the biography, `.iq` domain in the website).
- Writing `poster.profiles` and, for the review cases, `review_queue` rows.

### Out of scope

- Deciding to register, tier and retention (qualifier, registry-writer); deduplicating and routing candidates (poster-resolver).
- Posts (ig-account-media-poller), language evidence from posts (qualifier rule 2), keyword search (ig-keyword-search, ig-hashtag-search).
- Personal accounts: Business Discovery cannot read them, so they stay individuals; no amber route resolves them either.

## 4. Users and consumers

- **The qualifier** consumes `poster.profiles` and decides; registry-writer then writes the registry and `source.events`.
- **Ops and the review approvers** see age-gated and unreadable candidates in the n8n approval card (default after 24 hours is reject, qualifier rule 10).
- **Clients** never call it; they see its effect as new accounts appearing among the sources they watch.
- **Other services**: poster-resolver (sends requests), backfill-orchestrator (waits for a source's tier), quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Two. A resolution request from poster-resolver on `jobs.ig-account-resolver` (`kind = resolve`), carrying `candidate_key` (`instagram:<platform_id>` or `instagram:<handle>`), the handle, and the `client_ids` whose hit produced the candidate; partitioned by `candidate_key`, since a candidate has no `source_id` yet. And a refresh scheduler inside this service (one leader replica elected through a Postgres advisory lock) that emits `rotation` jobs for registered accounts whose profile is due.

**Cadence.** Profiles move slowly, so one interval serves every class: each registered Instagram account (tier 1, 2, 3, push and dormant alike) is refreshed every 30 days; a retired account is not refreshed and stays in the registry. Post polling keeps its own tier cadence in ig-account-media-poller; this service does not slow or speed it, it only keeps the follower count current so the tier is right.

**Keeping every account on rotation.** The scheduler keeps `refresh_due_at` per source in its own `cursors` row (source × `ig-account-resolver`), set from the START of the last refresh (`refresh_started_at + 30 days`). The candidate resolution that registered a source counts as its first refresh, so no source starts without a due time, and due times spread over the month by themselves. Jobs are emitted ordered by `refresh_due_at` then tier, so no account is skipped twice in a row; a failed refresh keeps its due time and goes first on the next scan.

**Catch-up.** When the most overdue account is more than one day past its due time, the scheduler orders most-stale-first and raises `rotation_behind`. A stale profile costs a late tier change, not data: the refresh is a full read each time, so there is no cursor to lose.

**Cache.** Every outcome, negative ones included, is cached for 30 days under the SHA-256 of `candidate_key`. A repeat request inside the window makes no call and re-emits the cached message with `cache.hit = true`. An `individual` result expires like any other, so an account that later turns into a creator is found at the next hit after 30 days.

**Backfill on add.** A source added by a client or ops, with no followers value yet, is resolved immediately so that its tier is known before backfill-orchestrator schedules the 90-day read of ig-account-media-poller; this service itself reads no history. There is no comment series: this service fetches no comments.

### 5.2 Step by step

1. Consume a job (`candidate_key` or `source_id`, `kind`, `client_ids`, `attempt`); look up the cache by the SHA-256 of `candidate_key`; on a live entry, re-emit it and stop.
2. Choose the calling account: the Instagram business account and token of the first client in `client_ids` whose token is healthy, fetched from Supabase Vault for this job only.
3. Ask quota-governor for allowance under `budget_tag = ig_graph_<ig_user_id>` (the calling account); on wait-until, requeue; on deny, count `quota_denied_total` and keep the due time.
4. Call Business Discovery for the handle.
5. Classify: an object returned means `business_or_creator`; no object is classified from the error code and message as `individual` (personal account) or `review` (age-gated, renamed, deleted, unclassified).
6. Extract signals from the biography and website: `phone_964`, `website_tld`, `city_in_bio`.
7. Write the cache entry, then the `poster.profiles` message; for `review`, also a `review_queue` row.
8. For a registered source, set `last_success_at`, `consecutive_errors = 0`, `refresh_due_at = refresh_started_at + 30 days`; on the second consecutive not-returned result for a registered source, send it to `review_queue` as ig-account-media-poller does.
9. Record metrics and the usage headers Meta returns into `budgets`.

### 5.3 The call it makes

```
GET https://graph.facebook.com/v<pinned>/{ig-user-id}
  ?fields=business_discovery.username(<handle>){followers_count,media_count,biography,website,name}
  &access_token=<Instagram user access token of the calling client's business account>
```

`{ig-user-id}` is the calling client's Instagram business account; `<handle>` is the candidate's. Auth: the client's long-lived token (Facebook Login, Advanced Access, Instagram Public Content Access approved in App Review), injected per job. The response is one object, so there is no page size and no pagination. Whether the response also carries the discovered account's `id` and `username`, which the registry needs for `platform_id`: to be confirmed in the pilot.

### 5.4 What it gets

For a business or creator account, the five fields requested. Example:

```json
{
  "business_discovery": {
    "followers_count": 48200,
    "media_count": 913,
    "biography": "مطعم عراقي في البصرة. للحجز: +964 770 000 0000",
    "website": "https://example.iq",
    "name": "مطعم الفرات"
  }
}
```

What it does not get: anything for a personal account; anything for an age-gated account (not returned); posts, languages and activity (other services); a distinction between business and creator accounts, unless the pilot finds a field that gives it.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.ig-account-resolver`; `sources`, `clients` (token reference), `cursors`, `budgets` through quota-governor, `health` through the SDK canary hook; the `profile_cache` table.

### 6.2 Writes

`poster.profiles`, one message per outcome, keyed by `candidate_key` (and `source_id` when the request was a refresh). Example for a resolved account:

```json
{
  "candidate_key": "instagram:furat_restaurant",
  "platform": "instagram",
  "platform_id": "17841400112233445",
  "handle": "furat_restaurant",
  "source_id": null,
  "resolution": "resolved",
  "account_class": "business_or_creator",
  "profile": {"name": "مطعم الفرات", "followers": 48200, "media_count": 913,
              "biography": "مطعم عراقي في البصرة. للحجز: +964 770 000 0000",
              "website": "https://example.iq"},
  "country_signals": {"phone_964": true, "website_tld": "iq", "city_in_bio": ["البصرة"]},
  "reason": null,
  "cache": {"hit": false, "resolved_at": "2026-10-06T12:40:11Z", "expires_at": "2026-11-05T12:40:11Z"},
  "provenance": {"route": "green", "vendor": null, "service": "ig-account-resolver",
                 "fetched_at": "2026-10-06T12:40:11Z"},
  "retention_class": "meta_on_request",
  "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
  "job_id": "01J9N8H3S5J7B9D2Z4W6Y8NPXK", "attempt": 1
}
```

For `individual` the message carries only `candidate_key_hash`, `resolution`, `account_class = individual`, `reason`, cache and provenance: no handle and no profile. For `review`, `resolution = review` and `reason` (for example `age_gated`, `unclassified`). Also `review_queue` rows, `profile_cache` rows, `service_runs`, and `dlq.ig-account-resolver` after 5 failed attempts.

### 6.3 State

`profile_cache` (`candidate_key_hash`, `result`, `resolved_at`, `expires_at`); `cursors` (source × service) with `refresh_due_at`, `last_success_at`, `last_error`, `consecutive_errors`; `budgets` counters per calling account; in memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- Business Discovery works for business and creator accounts only, and does not return age-gated accounts. Hashtag media carry no username on the green route, so a hashtag poster cannot be resolved by handle unless another route supplies it.
- Per-account call limits on the calling account: to be measured in the pilot. Budget tag `ig_graph_<ig_user_id>`, one counter per calling account.
- Load: one call per new candidate per 30 days, plus the refresh load of the registry divided by 30: for every 10,000 registered accounts, about 333 calls a day. Candidate volume: to be measured in the pilot.
- The 30-unique-hashtag limit per business account per 7 days belongs to ig-hashtag-search; the 50-comments-per-query limit to ig-own-comments-fetcher.
- Under Instagram Public Content Access, analytics leave the platform only as aggregated, de-identified output; profile fields are for qualification, not for client reports.
- Cost: USD 0 per Graph call; the cost is quota.

## 8. Failure handling and fallback

- HTTP 429 and Meta rate-limit errors: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.ig-account-resolver` and an alert fires.
- HTTP 401 and 403: mark the token `degraded`, stop the batch, alert; never rotate accounts, tokens or IPs around a block.
- Not-returned responses: classified by a table of error codes and messages to be built in the pilot. Until it exists, a not-returned candidate on a client seed list or a registered source goes to `review`, and every other one is classed `individual`; each is counted by reason in `not_returned_total` so the table is built from real responses.
- Empty 200 on a candidate that resolved before: counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. No amber resolver exists for Instagram, so `fallback_on` is never set here.
- Unknown response shape: the response is archived through raw-archiver, the job goes to the DLQ, an alert fires.
- Partial write: the cache entry is written before the message, and the message is idempotent on `candidate_key` and `resolved_at`, so a replay re-emits the same result.

## 9. Non-functional requirements

- Throughput: candidates plus 1/30 of the registry per day; both to be measured in the pilot.
- Latency: a candidate is resolved within one scan period of its request when quota allows (period to be set in the pilot).
- Idempotency: results keyed by `candidate_key`; replayable jobs; the cache makes repeats free.
- Scaling: stateless workers on partition lag; one leader scheduler.
- Security: tokens from Supabase Vault per job, never logged; no account pools, no proxies; Meta data never processed for law-enforcement or national-security purposes; individuals are stored only as a hash and never profiled; provenance on every message; retention `meta_on_request`, and the 30-day cache is shorter than any deletion request window.

## 10. Metrics and alerts

`jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `candidates_resolved_total{resolution}`, `cache_hit_total`, `not_returned_total{reason}`, `profile_age_seconds_p95`, `refresh_lag_seconds`, `review_rows_total`. Alerts: `rotation_behind`, `token_degraded`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`, `not_returned_spike`. SLO: profile age below 30 days for 99% of registered accounts.

## 11. Dependencies

listening-sdk (job schema gains `kind = resolve`), poster-resolver, qualifier, registry-writer, quota-governor, source-health-canary, backfill-orchestrator, raw-archiver, ig-account-media-poller, ig-mentions-fetcher and ig-keyword-search (sources of candidates), Supabase Postgres and Vault (including the `profile_cache` table, to be added to the control plane), Redpanda. Meta prerequisites: Business Verification, App Review (Advanced Access and Instagram Public Content Access), Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- Personal and age-gated accounts look alike in a not-returned response: the pilot builds the error table; seed-list and registered candidates go to review meanwhile so they are never silently dropped.
- Stale follower counts put an account on the wrong tier: refresh every 30 days, ordered by due time, with `rotation_behind`.
- A review flood: individuals never reach review; only age-gated or unclassified seed-list and registered candidates do, and the default after 24 hours is reject.
- Dependence on a client's calling account: another watching client's token is used; if none, the job waits and ops are told.
- Storing identities of private people: forbidden by design; individuals are a hash only.

## 13. Acceptance criteria

1. A second request for the same `candidate_key` within 30 days makes zero Graph calls and returns the same resolution with `cache.hit = true`; a request after 30 days makes one call.
2. A fixture business account yields `resolution = resolved`, `account_class = business_or_creator`, the five profile fields, and `country_signals` showing `phone_964 = true`, `website_tld = iq` and the city found in the biography.
3. A personal-account response yields `resolution = individual`, a message with no handle and no profile, and a 30-day cache entry holding only the hash.
4. An age-gated response for a seed-list candidate yields `resolution = review` and one `review_queue` row; a repeat request inside 30 days adds no second row.
5. With 300 fixture registered accounts over 30 simulated days, every account is refreshed within 30 days of its previous refresh, `refresh_due_at` equals `refresh_started_at + 30 days`, and jobs are ordered by due time then tier.
6. When the scheduler is more than one day behind, `rotation_behind` fires and the next scan orders most-stale-first.
7. A refresh that returns 120,000 followers for a Tier 2 account reaches the qualifier in `poster.profiles` with `source_id` set, and the qualifier fixture emits a `tier change`.
8. A source added by a client with no followers value is resolved before backfill-orchestrator starts its backfill.
9. A simulated 429 triggers backoff from 30 s to at most 15 min; after 5 attempts the job is in `dlq.ig-account-resolver` and an alert fired; a 401 marks the token `degraded` and stops the batch.
10. Calls are charged to `ig_graph_<ig_user_id>` of the calling account; a quota-governor deny sends no call and keeps the due time.
11. Every message carries `provenance` (route `green`, vendor null, service, `fetched_at`) and `retention_class = meta_on_request`; tokens never appear in logs or messages.

## 14. Open questions

1. The table of Business Discovery error codes and messages that separates a personal account, an age-gated account, a renamed or deleted account and the rest: to be built in the pilot.
2. Whether the response carries the discovered account's `id` and `username`, and whether business and creator accounts can be told apart (registry `source_type` account or creator).
3. Control-plane additions: the `profile_cache` table, and `kind = resolve` in the SDK job schema. Proposed: yes to both.
4. How the qualifier gets the language share of the last 20 posts for an Instagram candidate: proposed from the matched item, then from the first backfill read after registration.
