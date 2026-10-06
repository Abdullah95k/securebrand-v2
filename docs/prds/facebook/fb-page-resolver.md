# fb-page-resolver

**Platform:** Facebook · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend lead, Facebook adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A keyword hit, a search result or a mention gives us a poster's name or id and nothing more. Before the qualifier can decide whether a Facebook poster is a Page worth watching (a source) or a person (an individual, never a source), someone has to look it up: is it a Page at all, how many followers does it have, where is it based, does it link to an .iq website, is it verified. fb-page-resolver does that lookup through the Meta Graph API `/{page-id-or-username}` node, for every Facebook candidate that poster-resolver sends.

Without it the qualifier has no reach number for a Facebook candidate (so no tier), no Iraqi signals (so the two-signal rule of qualifier rule 2 cannot run), and no way to tell a Page from a person. Either every candidate would have to be treated as a person and nothing new would ever join the registry, or people would be profiled to find out: both unacceptable. The registry would grow only through sources that clients or ops type in.

## 2. Objective (the end state this service delivers)

Every Facebook candidate sent by poster-resolver, and every registered Page whose profile is due, leaves as one classified message on `poster.profiles`: a Page with the facts the qualifier needs, or an individual with no personal data at all. Target: 100% of requests answered (resolved, or dead-lettered after 5 attempts), no Page profile older than 30 days reaching the qualifier, nothing of an individual stored beyond a hashed key; the answer-time target is to be set in the pilot.

## 3. Scope

### In scope

- Resolving a Facebook candidate (`candidate_key` = `facebook:<platform_id>` or `facebook:<handle>`) with one Graph call.
- The 30-day profile cache, including a negative cache that stores only hashes.
- Deriving the signals the qualifier reads: followers, location, website domains, `.iq` domain, a +964 number in `about`, category, verification.
- A refresh loop that re-resolves registered Pages so tiers by reach never rest on old numbers.
- Writing `poster.profiles`.

### Out of scope

- Qualifying (qualifier), registering (registry-writer), candidate deduplication and routing (poster-resolver); groups (qualifier rule 8, amber).
- Reading a Page's posts or their language: the 40% Iraqi-language signal comes from elsewhere.
- Reading anything about a person.

## 4. Users and consumers

- **poster-resolver** sends the requests; **qualifier** consumes `poster.profiles`; registry-writer applies the resulting tier changes.
- **Clients** never see it; they see sources appear in their registry.
- **Ops** watches refresh lag, token health and the DLQ, and can force a resolution (`ops_force`).
- Also: quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.fb-page-resolver`, partitioned by `candidate_key` (a candidate has no `source_id` yet; a registered Page uses its `source_id`), carrying `job_id`, `kind` (`resolve`, `rotation`, `ops_force`), `candidate_key`, `client_ids`, `due_at`, `attempt`. `resolve` jobs come from poster-resolver, `rotation` jobs from this service's own loop. Groups are never sent here.

**Cache.** A resolved Page profile is cached for 30 days. A request for a cached candidate is answered from the cache (`cache = hit`) with no Graph call.

**Refresh rotation.** Post pollers use tier intervals of 60 minutes, 6 hours and 24 hours; reach changes slowly, so this service refreshes every registered Facebook Page on one 30-day cycle. A leader-elected loop (Postgres advisory lock) selects registered Pages (`source_type = page`, `route = green`, tier not `retired`) whose cached profile is at the end of its 30 days, ordered oldest `fetched_at` first and then by tier, so no Page is skipped twice in a row. The next refresh is set from the START of the last resolution, so the cycle does not drift. Dormant Pages are refreshed on the same cycle, since they can grow; push Pages (client-owned) use the client's Page token; retired Pages are never refreshed. A Page that moves across 10,000 or 100,000 followers reaches the qualifier, which proposes the tier change through registry-writer.

**Catch-up.** If the loop falls behind (a profile older than 30 days plus one scan period), it works the oldest first and raises `rotation_behind`. Being behind costs freshness of tiers, not completeness.

**Backfill.** None: this service holds one profile per Page, no history. A source added by a client or ops with no follower count is resolved once before its tier is set.

### 5.2 Step by step

1. Consume a job; read `profile_cache` (Pages by key, individuals by the hash of the key). On a hit, emit the cached result with `cache = hit` and stop.
2. Select the token: the system-user token of the first client in `client_ids` whose token is healthy, from Supabase Vault for this job only; the client's Page token for `owned_by_client` Pages.
3. Ask quota-governor for allowance under `meta_graph_pages:<client_id>`. Resolution is not time-critical: on wait-until or deny the job waits, so feed polling keeps priority.
4. Call the Graph node (5.3).
5. A Page object: classify `page`; derive `website_domains`, `iq_domain` (a domain ending `.iq`) and `phone_964` (a +964 or 00964 number written in `about`); store the profile in the cache for 30 days; emit.
6. An error that says the node is not a readable Page (a personal profile, a group, a missing Page): classify `individual`; request and store nothing else; cache only the hash of the key for 30 days; emit an `individual` message without profile fields.
7. A transient error: back off and retry (section 8).
8. After Redpanda acknowledges, update `service_runs`.

### 5.3 The call it makes

```
GET https://graph.facebook.com/v<pinned>/{page-id-or-username}
  ?fields=id,name,category,fan_count,location,website,is_verified,link,about
  &access_token=<system-user token (PPCA); Page access token for owned_by_client Pages>
```

One object, so no pagination and no page size. `{page-id-or-username}` is the numeric id or the vanity username taken from `candidate_key`. The Graph version is pinned by the one environment variable shared by all fb-* services. Whether PPCA alone returns these fields for third-party Pages, or Meta requires a further Page-metadata permission, is to be confirmed in the pilot (open question 2).

### 5.4 What it gets

```json
{
  "id": "100064583471102",
  "name": "شركة المثال للاتصالات",
  "category": "Telecommunication Company",
  "fan_count": 412000,
  "location": {"city": "Baghdad", "country": "Iraq"},
  "website": "https://example-telecom.iq",
  "is_verified": true,
  "link": "https://www.facebook.com/exampletelecom.iq",
  "about": "خدمة الإنترنت والاتصالات في بغداد والمحافظات"
}
```

What it does not get: anything about a personal profile (it cannot be read, so it is classed an individual); `followers_count` (not requested; `fan_count` counts likes and can be lower than followers); a Page's posts or their language; admins; groups.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.fb-page-resolver`; `profile_cache`, `sources`, `clients` (token reference), `budgets` through quota-governor, `health` through the SDK canary hook; `source.events` (`added`, `tier change`, `retired`).

### 6.2 Writes

`poster.profiles`, one message per answer, partitioned by `source_id` for a registered Page and by `candidate_key` otherwise:

```json
{
  "envelope": {
    "platform": "facebook", "route": "green", "vendor": null,
    "service": "fb-page-resolver",
    "candidate_key": "facebook:100064583471102", "source_id": null,
    "job_id": "01J9N6D1W5Q8Z2T7K4V0M3RXBH", "attempt": 1,
    "fetched_at": "2026-10-06T10:41:09Z", "cached_until": "2026-11-05T10:41:09Z",
    "cache": "miss", "retention_class": "meta_on_request",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]
  },
  "profile": {
    "resolved_type": "page",
    "platform_id": "100064583471102", "handle": "exampletelecom.iq",
    "display_name": "شركة المثال للاتصالات",
    "url": "https://www.facebook.com/exampletelecom.iq",
    "category": "Telecommunication Company",
    "followers": 412000,
    "location": {"city": "Baghdad", "country": "Iraq"},
    "website_domains": ["example-telecom.iq"],
    "signals": {"iq_domain": true, "phone_964": false},
    "is_verified": true,
    "about": "خدمة الإنترنت والاتصالات في بغداد والمحافظات"
  }
}
```

An individual answer carries `candidate_ref` (a keyed hash) instead of `candidate_key`, and `profile = {"resolved_type": "individual", "reason": "not_a_readable_page"}`. Also `service_runs` and `dlq.fb-page-resolver` after 5 failed attempts.

### 6.3 State

`profile_cache` (control-plane Postgres): for Pages, `candidate_key`, the profile, `fetched_at`, `expires_at`; for individuals, only the keyed hash and `expires_at`. `sources.followers` is updated by registry-writer, not by this service. In memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- One Graph call per cache miss; cost USD 0 per call, the cost is quota. The Pages bucket allows 4,800 calls × engaged users per 24 h with a system-user token, shared with every other fb-* service; error 80001 means "too many calls to this Page".
- The 30-day cache means a Page costs at most one call every 30 days, however often it is mentioned.
- Candidate volume, cache hit rate and calls per day: to be measured in the pilot.
- Budget tag `meta_graph_pages:<client_id>`; resolver jobs yield to polling when quota is tight.

## 8. Failure handling and fallback

- HTTP 429 and 80001: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.fb-page-resolver` and an alert fires.
- HTTP 401 and 403: mark the token `degraded`, stop the batch, alert; never rotate accounts, tokens or IPs. A "not a readable Page" error is an answer, not a failure, and is never retried.
- Empty 200 (a 200 with no `id`): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. No amber route exists for Page profiles, so `fallback_on` is never set here.
- Schema change: the job is parked in the DLQ with the response, which holds Page data only, and `schema_unknown` is raised.
- Partial write: the cache entry is written with the emit; a replayed job answers from the cache and emits the same message.

## 9. Non-functional requirements

- Throughput: demand is set by candidate volume, to be measured in the pilot; a cache hit is a database read.
- Latency: a cache miss takes one Graph call plus any quota wait.
- Idempotency: one answer per `candidate_key` per cache period; replaying a job is safe.
- Scaling: stateless workers on partition lag; one leader for the refresh loop.
- Security: tokens from Supabase Vault per job, never logged; no field beyond the fixed list is requested; individuals leave no name, id or photo, only a keyed hash; Meta data never processed for law-enforcement or national-security purposes; retention `meta_on_request`.

## 10. Metrics and alerts

`jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `resolutions_total{result}` (page, individual, error), `cache_hits_total`, `cache_misses_total`, `refresh_lag_seconds` (age of the oldest profile past its 30 days) and `graph_error_total{code}`. Alerts: `rotation_behind`, `token_degraded`, `dlq_nonempty`, `empty_200_rate`, `quota_deny_rate`. SLO: no registered Page profile older than 30 days plus one scan period for 99% of Pages per day.

## 11. Dependencies

listening-sdk, poster-resolver, qualifier, registry-writer, quota-governor, source-health-canary, fb-page-search and fb-keyword-search (candidate sources), Supabase Postgres and Vault, Redpanda. Meta prerequisites: Business Verification, App Review for PPCA, Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- `fan_count` counts likes and can understate followers, tiering a Page too low: measured in the pilot (open question 3).
- Many Iraqi Pages show no location or website, so the two-signal rule may send them to review: the qualifier's n8n approval card handles it.
- PPCA may not cover every field for third-party Pages: confirmed in the pilot before launch.
- A cached 30-day profile can show an outdated verification or name: acceptable; the refresh cycle bounds it.
- A person's id passed by mistake: never profiled, because nothing but the hash is kept.

## 13. Acceptance criteria

1. A candidate cached less than 30 days ago is answered with `cache = hit` and no Graph call.
2. A cache miss makes exactly one call with `fields=id,name,category,fan_count,location,website,is_verified,link,about` and emits one `poster.profiles` message with `followers = fan_count`.
3. A Page with website `https://example-telecom.iq` yields `iq_domain = true` and `website_domains = ["example-telecom.iq"]`; a Page without a website yields an empty list and `false`.
4. A personal profile yields `resolved_type = individual` with no name or other profile field, and a cache entry holding only a hash.
5. The same candidate requested twice within 30 days costs one Graph call and yields identical profile content.
6. With 100 fixture registered Pages over 60 days, none is older than 30 days plus one scan period, refreshed oldest first.
7. A refresh that moves a Page from 9,500 to 10,400 followers emits a message with its `source_id`, so the qualifier can propose a tier change.
8. HTTP 429 or 80001 triggers backoff from 30 s to 15 min with `attempt + 1`; after 5 attempts the job is in `dlq.fb-page-resolver` and an alert fired.
9. A 401 marks the token `degraded`, stops the batch and raises `token_degraded`; tokens never appear in logs.
10. A "not a readable Page" error is not retried and not counted as a failure.
11. Retired Pages are never refreshed; groups are never resolved.

## 14. Open questions

1. Does poster-resolver already own refreshing registered Pages? If so, this service's loop is removed.
2. Does PPCA alone return `fan_count`, `location`, `website` and `about` for third-party Pages?
3. Should `followers_count` be added to the fixed field list?
4. Can several candidates be resolved in one call (Graph batching) to save quota?
5. Should the negative cache last 30 days, as for Pages, or 180 days like the qualifier's rejections? Proposed: 30.
