# x-user-resolver

**Platform:** X · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend lead, X adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

An X keyword hit says who posted, an author id or a handle, and nothing more. On X a ministry, a newspaper, a minister and a private person hold the same kind of account; only the account's numbers tell a source from an individual. x-user-resolver reads them for every X candidate poster-resolver sends, and gives the qualifier the facts it needs or, for an individual, a verdict and nothing else.

Without it the qualifier cannot apply the X type rule (500 followers, verified, or on a client watchlist), count Iraqi signals or check account age for spam. No Iraqi journalist, spokesperson or brand found by x-recent-search or x-filtered-stream would ever join the registry. Profiling every poster instead would breach the X Developer Agreement and our rule that individuals are never profiled. At USD 0.010 a read, its 30-day cache also keeps discovery affordable.

## 2. Objective (the end state this service delivers)

Every X candidate from poster-resolver, and every registered X account whose profile is due, leaves as one classified message on `poster.profiles`: an organization or public figure with the qualifier's facts, an individual with no personal data, or an unavailable account. Target: 100% of requests answered (resolved, from cache, or dead-lettered after 5 attempts); at most one paid read (USD 0.010) per account per 30 days; no field of an individual stored, logged or dead-lettered; no registered profile older than 30 days plus one scan period. Answer time: target set in the pilot.

## 3. Scope

### In scope

- Resolving an X candidate (`candidate_key` = `x:<user id>` or `x:<handle>`) with one user read.
- A 30-day cache; individuals and unavailable accounts kept only as keyed hashes and a verdict.
- The `qualifies_as` hint and the qualifier's inputs: followers, following, post count, verification, an Iraqi place in the location, an `.iq` domain, a +964 number, account age.
- Re-qualification after an individual's entry expires; a 30-day refresh of registered accounts; X deletions mirrored into the cache within 24 hours.

### Out of scope

- Qualifying (qualifier), registering (registry-writer), deduplication and routing (poster-resolver).
- Posts and their language (x-user-timeline-poller); compliance jobs (x-compliance-sync).
- Anything about an individual beyond the verdict.

## 4. Users and consumers

- **poster-resolver** sends `resolve` jobs; **qualifier** consumes `poster.profiles`; **registry-writer** applies additions and tier changes.
- **x-recent-search**, **x-filtered-stream** and **x-full-archive-search** yield the hits behind candidates; **x-user-timeline-poller** polls a registered account by the id returned here.
- **Ops** watches spend, refresh lag, token health and the DLQ, and can force a resolution (`ops_force`); **clients** only see sources appear.
- Also: quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.x-user-resolver`, partitioned by `candidate_key` (a registered account uses its `source_id`), carrying `job_id`, `kind` (`resolve`, `rotation`, `ops_force`), `candidate_key`, `client_ids`, `due_at`, `attempt`. poster-resolver sends `resolve` after inserting the candidate's `poster_profiles` row (`status = resolving`); this service's loop sends `rotation`.

**Cache.** Every X answer is cached 30 days: profiles under both `x:<user id>` and `x:<handle>`, individuals and unavailable accounts only as keyed hashes, a verdict and an expiry.

**Re-qualification.** When an individual keeps drawing keyword hits, poster-resolver may ask again: within 30 days the cached verdict answers free; after expiry one read decides, so an account that has reached 500 followers or verification returns as a full profile and can become a source.

**Refresh rotation.** A leader-elected loop (Postgres advisory lock) re-resolves registered X accounts (tier not `retired`) as their 30 days end, oldest `fetched_at` first then by tier, the next refresh set from the START of the last resolution. A move across 10,000 or 100,000 followers reaches the qualifier, which proposes the tier change.

**Catch-up and backfill.** When behind (a profile older than 30 days plus one scan period), the oldest go first and `rotation_behind` fires. No backfill: one profile per account, no history.

### 5.2 Step by step

1. Consume a job; compute `candidate_ref` (HMAC-SHA256, key in Supabase Vault); unless `ops_force`, answer a valid `profile_cache` entry with `cache = hit`.
2. Plan gate: drop government end-user clients (per `clients`) unless `X_PLAN = enterprise` with that end user declared; if none remains, emit `not_resolved` without a call.
3. Ask quota-governor for one read (`x_pay_per_use`, sub-counter `user_reads`, priority 4); on wait-until or deny the job waits without using an attempt.
4. Call X (5.3).
5. Classify: `organization_or_public_figure` when followers reach 500, `verified` is true, or the id or handle is on a client watchlist (`qualifies_by` names which); else `individual`. Record the read in the UTC-day ledger as `user:<id>` for an organization or public figure, as the keyed hash otherwise.
6. Organization or public figure: derive `location_iq` (the location matched against Iraqi governorates and cities in Arabic, Sorani and Latin spellings), `url_domain`, `iq_domain`, `phone_964` (+964 or 00964 in the description) and `account_age_days`; cache; emit.
7. Individual: drop the response in memory; cache hashes, verdict and expiry; emit the verdict only.
8. Suspended, protected or deleted: `unavailable`, cached the same way, no retry before expiry.
9. Errors: section 8. After Redpanda acknowledges, update `service_runs`.

### 5.3 The call it makes

```
GET /2/users/by/username/{handle}?user.fields=public_metrics,verified,location,description,created_at
Authorization: Bearer <company app bearer token>
```

The call as the X fact sheet gives it: one object, no pagination, no page size. The bearer token is the company app's (X tokens are per app, not per client), from Supabase Vault per job, never logged.

When the key holds a user id, the service calls `GET /2/users/{id}` with the same `user.fields`, since ids survive handle changes. To be confirmed in the pilot: this form's parity in fields and price, a batch lookup by ids, the rate limit, the responses (and billing) for suspended, protected and deleted accounts, and adding `url`, `protected` and `profile_image_url` (open question 2).

### 5.4 What it gets

```json
{
  "data": {
    "id": "1456789012345678901",
    "username": "example_telecom_iq",
    "name": "شركة المثال للاتصالات",
    "created_at": "2019-03-14T08:22:51.000Z",
    "location": "بغداد، العراق",
    "description": "الحساب الرسمي لشركة المثال | example-telecom.iq",
    "verified": true,
    "public_metrics": {"followers_count": 18400, "following_count": 212, "tweet_count": 5310, "listed_count": 41}
  }
}
```

Values are illustrative. Until `url` is requested, `url_domain` comes from a domain written in the description; if X shortens such links, that is the same pilot question. Not returned: posts or their language, the profile link, protection flag, avatar, or who follows the account.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.x-user-resolver`; `deletions` for X users (from x-compliance-sync); `profile_cache`, `sources`, `clients`, client watchlists, `budgets` through quota-governor, `health` through the SDK canary hook; `source.events` (`added`, `tier change`, `retired`).

### 6.2 Writes

`poster.profiles`, one message per answer, partitioned by `source_id` for a registered account, `candidate_key` for an organization or public figure, else `candidate_ref`, so no individual's handle travels in a key:

```json
{
  "envelope": {
    "platform": "x", "route": "green", "vendor": null,
    "service": "x-user-resolver",
    "candidate_key": "x:1456789012345678901", "source_id": null,
    "job_id": "01J9N8F4C2X7W1R5T3M6Q0ZKDA", "attempt": 1,
    "fetched_at": "2026-10-06T11:02:37Z", "cached_until": "2026-11-05T11:02:37Z",
    "cache": "miss", "retention_class": "x_24h_sync",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]
  },
  "profile": {
    "resolved_type": "account",
    "qualifies_as": "organization_or_public_figure",
    "qualifies_by": ["followers_500", "verified"],
    "platform_id": "1456789012345678901", "handle": "example_telecom_iq",
    "display_name": "شركة المثال للاتصالات",
    "url": "https://x.com/example_telecom_iq",
    "followers": 18400, "following": 212, "post_count": 5310,
    "verified": true,
    "location_text": "بغداد، العراق",
    "description": "الحساب الرسمي لشركة المثال | example-telecom.iq",
    "url_domain": "example-telecom.iq",
    "created_at": "2019-03-14T08:22:51Z", "account_age_days": 2763,
    "signals": {"location_iq": "Baghdad", "iq_domain": true, "phone_964": false}
  }
}
```

An individual answer carries `candidate_ref` instead of `candidate_key` and `profile = {"resolved_type": "individual", "qualifies_as": "individual"}`; an unavailable one `{"resolved_type": "unavailable", "reason": "suspended" | "protected" | "not_found"}`; a plan-gated one `{"resolved_type": "not_resolved", "reason": "plan_not_enterprise"}`. Each carries the request's `job_id`, so poster-resolver matches it without the key. Also `service_runs` and `dlq.x-user-resolver`.

### 6.3 State

`profile_cache` (control-plane Postgres): profiles under both keys with `fetched_at` and `expires_at`; individuals and unavailable accounts as keyed hashes, verdict and `expires_at` only. The ledger is quota-governor's, `poster_profiles` poster-resolver's, `sources.followers` registry-writer's. In memory: leader lock, backoff state.

## 7. Limits, quotas and cost

- USD 0.010 per user read, deduplicated per resource per UTC day; budget tag `x_pay_per_use`, sub-counter `user_reads`, priority 4: resolution waits when the budget is tight.
- A cache hit costs USD 0, so an account costs at most USD 0.010 per 30 days however often it posts; the refresh loop costs USD 10.00 per 30 days per 1,000 registered accounts.
- The 3,000,000 post-read cap does not cover user reads, and the fact sheet gives no user-read cap; ops sets a monthly `user_reads` ceiling after the pilot.
- Candidate volume, hit rate and spend: to be measured in the pilot. Enterprise pricing is not in the fact sheet.

## 8. Failure handling and fallback

- HTTP 429: backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts, `dlq.x-user-resolver` and an alert.
- HTTP 401 and 403 on the token: mark the X route `degraded`, stop the batch, alert; never rotate tokens, apps or IPs. An account reported suspended, protected or missing is an answer (`unavailable`), whatever the status code.
- Empty 200 (no `data`, no `errors`): above 5% in 15 minutes source-health-canary flips `health = degraded`; no amber route exists, so no `fallback_on`.
- Schema change: parked in the DLQ with field names only, never values; `schema_unknown` raised.
- Partial write: cache and emit go together; a replay answers from the cache, counted once in the ledger.

## 9. Non-functional requirements

- Throughput: set by unique unregistered X authors, to be measured in the pilot; a cache hit is a database read.
- Latency: one call plus any quota wait. Idempotency: one answer per candidate per cache period. Scaling: stateless workers on partition lag, one loop leader.
- Security and X terms: fixed fields only; an individual's response never reaches a log, object storage, the DLQ or the cache; nothing about religion, sect, ethnicity, politics or health is inferred; no surveillance use; retention `x_24h_sync`.

## 10. Metrics and alerts

`jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `resolutions_total{result}` (account, individual, unavailable, not_resolved, error), `cache_hits_total`, `cache_misses_total`, `requalified_total`, `refresh_lag_seconds`, `x_error_total{status}`. Alerts: `rotation_behind`, `token_degraded`, `dlq_nonempty`, `empty_200_rate`, `quota_deny_rate`, `schema_unknown`, `compliance_purge_late`. SLOs: no registered account profile older than 30 days plus one scan period for 99% of accounts per day; every X deletion applied to the cache within 24 hours.

## 11. Dependencies

listening-sdk, poster-resolver, qualifier, registry-writer, quota-governor, source-health-canary, x-recent-search, x-filtered-stream and x-full-archive-search (candidate origins), x-user-timeline-poller, x-compliance-sync, Supabase Postgres and Vault, Redpanda. X prerequisites: the company app on pay-per-use with its bearer token; Enterprise, with the end user named at use-case review, before any government client or multi-client use.

## 12. Risks and mitigations

- `verified` may include paid checkmarks: the qualifier still needs two Iraqi signals and activity; open question 3.
- Free-text locations are noisy: only a named Iraqi city or governorate counts; open question 5.
- A watchlist could name private persons: watchlist-only passes carry `qualifies_by = ["watchlist"]` for review; open question 1.
- Handle reuse: profiles key on the id; handle entries expire in 30 days.
- Spend grows with unique authors: the cache, ledger and `user_reads` ceiling bound it; open question 4.

## 13. Acceptance criteria

1. A candidate cached less than 30 days ago gets `cache = hit`, no X call and no `user_reads` increment.
2. A miss on `x:<handle>` makes one `GET /2/users/by/username/{handle}` call, a miss on `x:<user id>` one `GET /2/users/{id}` call, each with `user.fields=public_metrics,verified,location,description,created_at` and one ledger read.
3. The 5.4 fixture yields `resolved_type = account`, `qualifies_by = ["followers_500", "verified"]`, `post_count = 5310`, `iq_domain = true` and, on 6 Oct 2026, `account_age_days = 2763`.
4. At 499 followers, unverified, on no watchlist: `individual`, with no profile field in the message, cache, ledger, logs or DLQ; at 500, or on a client watchlist (`qualifies_by = ["watchlist"]`): `account`.
5. "البصرة" or "Erbil" sets `location_iq`; "Iraq" alone or "Dubai" does not; "+964" or "00964" in the description sets `phone_964`.
6. Suspended, protected and not-found fixtures yield `unavailable` and are not retried within 30 days.
7. An individual cached at 420 followers is served from cache on day 10; on day 31, at 650 followers, one read yields `account`.
8. HTTP 429 backs off 30 s to 15 min with `attempt + 1` and reaches `dlq.x-user-resolver` after 5 attempts; a 401 raises `token_degraded` and no log contains the token.
9. A job whose only client is a government end user, with `X_PLAN` not `enterprise`, makes no call and yields `not_resolved`.
10. A `deletions` message for a cached X user leaves a verdict-only entry within 24 hours.
11. With 100 registered fixture accounts over 60 days, none exceeds 30 days plus one scan period; a refresh crossing 10,000 followers emits a message with its `source_id`.

## 14. Open questions

1. Where are client X watchlists held, and should a watchlist-only pass (under 500 followers, unverified) always go to review?
2. Add `url`, `protected` and `profile_image_url` to `user.fields` (the `.iq` signal, protected accounts, the default-avatar spam check) at no extra price?
3. Can the verification type be read, so a paid checkmark alone does not qualify?
4. Could x-recent-search and x-filtered-stream request these `user.fields` on their `author_id` expansion, and are expanded users billed as user reads?
5. Does "Iraq" alone count as a location signal? Proposed: no; rule 2 names a city or governorate.
6. Does poster-resolver already own refreshing registered accounts? If so, this loop is removed.
