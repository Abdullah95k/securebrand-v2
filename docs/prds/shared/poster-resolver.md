# poster-resolver

**Platform:** Shared · **Route:** shared · **Lane:** Registry · **Owner:** Registry backend engineer · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Every keyword hit on a post whose poster is not yet in the registry lands on `discovery.hits`. A hit says that a page, channel, account or site is talking about something a client cares about; it does not say who the poster is, how large it is, whether it is Iraqi, or whether it is an individual we must never profile. `qualifier` cannot apply the ten rules on a bare hit: rule 1 needs the account type, rule 2 needs location, phone, domain and language signals, rule 3 the date of the last post, rule 6 the follower count.

`poster-resolver` turns a candidate poster into a profile. It dispatches to the eight per-source resolvers (each knows its platform's lookup call, token and budget), merges their answers into one `poster.profiles` schema, caches the result for 30 days, and applies the individuals rule before anything identifying is stored.

Without it the registry does not grow on its own: every source would be added by hand and discovery hits dropped. Without the cache and the rejection memory, the resolvers would pay for the same lookup again and again (X charges USD 0.010 per user read; TikHub USD 0.50 to 1.00 per 1,000 requests). Without the individuals gate, profiles of private people would be written to disk, which the TikTok Developer Terms and our own compliance rule forbid.

## 2. Objective (the end state this service delivers)

Every candidate poster on `discovery.hits` is resolved into exactly one `poster.profiles` message within 15 minutes of the first hit, complete enough for `qualifier` to decide rules 1 to 7 without a second lookup. Repeat hits on a poster resolved in the last 30 days cost nothing. Individuals leave no trace beyond a hashed author reference.

Targets: 99% of first hits resolved (profile or `unresolvable` emitted) within 15 minutes; cache hit rate on repeat hits above 95% after the first month (the share of repeat hits is to be measured in the pilot); zero rows anywhere holding the handle, name, biography or URL of an individual.

## 3. Scope

### In scope
- Consuming `discovery.hits` and deduplicating candidates by `candidate_key` (`<platform>:<platform_id>`, or `<platform>:<handle>` when the hit carries only a handle).
- Dispatching a `resolve` job to the platform's resolver: `fb-page-resolver`, `ig-account-resolver`, `tt-user-resolver`, `x-user-resolver`, `li-org-resolver`, `tg-channel-resolver`, `yt-channel-resolver`, `news-site-resolver`.
- Receiving the answer, classifying the account type, computing `lang_share` on the sample of recent posts, assembling the profile, emitting `poster.profiles`.
- A 30-day profile cache and a 180-day skip list for candidates `qualifier` has rejected.
- Archiving the raw resolver payload to `raw.items` for non-individuals; a redacted envelope only for individuals.
- Resolving manual candidates submitted by ops or clients through `registry-writer` (same path, `origin: manual`).

### Out of scope
- Platform or vendor calls: the per-source resolvers hold the tokens, the `budget_tag` and the fallback logic.
- Deciding whether a poster becomes a source (`qualifier`) and writing to `sources` (`registry-writer`).
- Resolving comment authors: comments keep the hashed author reference from `normalize-item`.

## 4. Users and consumers

- `qualifier`: the only consumer of `poster.profiles`.
- The eight per-source resolvers: receive `resolve` jobs on `jobs.<resolver>`, answer on `jobs.poster-resolver`.
- `registry-writer`: submits manual candidates before a manual add.
- `raw-archiver`: archives the profile payloads this service forwards.
- Ops: the admin page shows resolution lag, unresolvable candidates, cache hit rate.

## 5. How it works

### 5.1 Trigger and rotation

Event-driven, no rotation. Triggers: a message on `discovery.hits`; a `resolved` or `unresolvable` answer on `jobs.poster-resolver`; a `manual_candidate` from `registry-writer`. A candidate seen again within 30 days is served from the cache. A cached individual is re-resolved only on the first hit after its cache entry expires, so rule 7 (re-qualified as a creator only when resolver numbers cross the threshold) is re-checked at most once every 30 days. No backfill: hits produced before deployment are not re-read.

Catch-up: if partition lag exceeds 15 minutes, hits are processed newest `hit_at` first (a fresh hit is more likely to be a fresh story) and `resolver_behind` is raised.

### 5.2 Step by step

1. Read a `discovery.hits` message; build `candidate_key`.
2. Look up `poster_profiles`. If a row exists with `resolved_at` within 30 days: increment `hits_30d`, append the keyword and client, re-emit the cached profile with `cached: true`, stop.
3. Look up `decisions` for a `reject` on this `candidate_key` within 180 days. If found and the hit is not from a client seed list or watchlist: record the hit on the decision row, emit nothing, stop (rule 9).
4. Insert a `poster_profiles` row with `status = resolving` (unique on `candidate_key`; a concurrent duplicate hit sees the row and stops).
5. Publish a `resolve` job to `jobs.<resolver>` chosen by `platform` (`web` hits arrive already mapped to a platform by `search-hit-router`). Amber resolvers (`tt-user-resolver`, `li-org-resolver`, `tg-channel-resolver`) are called only when `TT_VENDOR_ROUTE`, `LI_VENDOR_ROUTE` or `TG_VENDOR_ROUTE` is not `off`; otherwise the candidate is marked `unresolvable: route_off`.
6. On the `resolved` answer, classify `account_type` with rule 1: Facebook page or group; Instagram business or creator; TikTok creator at 2,000 followers or verified; X public figure or organisation at 500 followers, verified, or on a client watchlist; YouTube channel, Telegram channel, LinkedIn company page and news domain always qualify; everything else is an individual.
7. Non-individual: send the sample of up to 20 recent post texts to `lang-dialect-id` (the classifier that enriches `items.normalized`) and store the shares; extract `country_signals` (Iraqi city or governorate in the location text, +964 number, .iq domain or Iraqi outlet link, seed-list membership from `keywords` and `clients`); write the raw payload to `raw.items` with `kind: profile`; update the cache row; emit `poster.profiles`.
8. Individual: compute `author_hash = sha256(platform || platform_id || salt)` with the salt from Supabase Vault; keep in the cache only `author_hash`, `platform`, `followers`, `verified`, `resolved_at`; write a redacted envelope to `raw.items` (hash, platform, `individual: true`, no payload); emit a minimal `poster.profiles` message with `individual: true`.
9. On `unresolvable` (deleted or private account, age-gated Instagram account, 404, empty vendor answer): cache the outcome for 30 days and emit `poster.profiles` with the reason so `qualifier` can close the candidate.

### 5.3 The call it makes

No external call. The internal call is the `resolve` job:

```json
{"job_id":"res:x:1234567890","kind":"resolve","candidate_key":"x:1234567890","platform":"x","platform_id":"1234567890","handle":"iraqi_outlet","hit_url":"https://x.com/iraqi_outlet/status/1","origin":"discovery","reply_to":"jobs.poster-resolver","attempt":1,"sample_posts":20}
```

The resolver answers on `jobs.poster-resolver` with `kind: resolved` (profile fields, up to 20 recent post texts, the raw payload) or `kind: unresolvable`. Each resolver uses its own fact-sheet call: `x-user-resolver` calls `GET /2/users/by/username/{handle}?user.fields=public_metrics,verified,location,description,created_at` at USD 0.010 per user read; `yt-channel-resolver` calls `channels.list?part=snippet,statistics,brandingSettings` at 1 unit; `fb-page-resolver` calls `GET /pages/search?q=<name>&fields=id,name,location,link,is_verified` within the PPCA bucket.

### 5.4 What it gets

From the resolvers: `platform_id`, `handle`, `url`, `display_name`, the platform's own account-type field where one exists, `verified`, `followers`, `posts_30d`, `last_post_at`, `location_text`, `website`, `biography`, `created_at`, up to 20 recent post texts, the raw payload.

Not obtained: comment text, follower lists, email addresses, audience data, Facebook Group members, age-gated Instagram accounts (Business Discovery does not return them), TikTok accounts while `TT_VENDOR_ROUTE` is `off`, commenter identity of any kind.

## 6. Inputs and outputs

### 6.1 Reads
- Topic `discovery.hits` (partition key: the keyword or hashtag source that produced the hit; the candidate is in the payload).
- Queue `jobs.poster-resolver` (resolver answers, manual candidates).
- Tables: `poster_profiles` (cache, proposed here), `decisions` (rejection memory), `keywords` and `clients` (seed lists, watchlists), `sources` (to drop hits whose poster was registered after the hit was produced).

### 6.2 Writes
- Topic `poster.profiles`, partition key `candidate_key`:

```json
{"message_id":"pp:instagram:17841400000000000:2026-10-06T10:13:58Z","produced_at":"2026-10-06T10:14:02Z","service":"poster-resolver","schema_version":1,"candidate_key":"instagram:17841400000000000","platform":"instagram","platform_id":"17841400000000000","handle":"baghdad_eats","url":"https://instagram.com/baghdad_eats","display_name":"Baghdad Eats","account_type":"business","individual":false,"verified":false,"followers":48200,"posts_30d":22,"last_post_at":"2026-10-05T19:40:00Z","location_text":"Baghdad, Iraq","country_signals":{"iraqi_place":true,"phone_964":false,"iq_domain":false,"outlet_link":false,"seed_list":false},"lang_share":{"ar_iq":0.70,"ckb":0.00,"ar_msa":0.20,"en":0.10},"hits_30d":3,"keywords":["kw_0412"],"client_ids":["cl_17"],"route":"green","vendor":null,"resolver":"ig-account-resolver","resolved_at":"2026-10-06T10:13:58Z","cached":false,"unresolvable":null}
```

- Topic `raw.items` with `kind: profile` (full payload for non-individuals, redacted envelope for individuals).
- Queues `jobs.<resolver>` (`resolve` jobs).

### 6.3 State
- `poster_profiles`: `candidate_key` (unique), `status`, `profile` (jsonb, empty for individuals), `author_hash`, `individual`, `followers`, `resolved_at`, `expires_at` (+30 days), `hits_30d`, `unresolvable_reason`.
- `service_runs`: lag and errors. No cursors: the topic offset is the cursor.

## 7. Limits, quotas and cost

This service spends nothing itself; the resolvers spend, each under its own `budget_tag` with `quota-governor`. Per resolve, from the fact sheets: X USD 0.010 per user read (deduplicated per resource per UTC day); YouTube 1 unit of the 10,000-unit daily quota; TikHub USD 0.50 to 1.00 per 1,000 requests, billed on HTTP 200 only; SociaVault 1 credit at USD 1.99 to 4.83 per 1,000 credits; ScrapeCreators USD 0.99 to 1.88 per 1,000 requests; harvestapi, Telemetrio and Meta Pages Search within their monthly plan or PPCA bucket.

The number of distinct new candidates a day at 1,000,000 items a day is to be measured in the pilot; the cache and the 180-day skip list keep the resolver bill flat as hit volume grows. One Node replica handles the full-scale rate, which is at most the keyword-hit rate on unregistered posters.

## 8. Failure handling and fallback

- Resolver timeout (no answer within 15 minutes): the cache row returns to `pending` and the job is re-published with `attempt + 1`; after 5 attempts the candidate is marked `unresolvable: timeout`, the job goes to `dlq.poster-resolver` and an alert fires.
- Resolver reports `degraded` (401, 403 or canary fallback): the candidate waits until `source-health-canary` emits `fallback_off` or the route returns to `ok`. No retry on another token, account or IP.
- Vendor flag turned `off` mid-flight: in-flight answers are accepted; new candidates on that platform become `unresolvable: route_off`.
- Unknown answer shape: the raw payload is archived, the profile carries `schema_unknown: true` and `qualifier` sends it to review.
- Outcomes caused by 5xx or timeouts are cached for 24 hours only, so a vendor outage cannot poison the 30-day cache.

## 9. Non-functional requirements

- Throughput: one replica; scales on partition lag of `discovery.hits`; stateless apart from Postgres.
- Latency: profile within 15 minutes of the first hit; the resolver's latency is the dominant term.
- Idempotency: `candidate_key` is the unit of work; `message_id` is deterministic (`pp:<candidate_key>:<resolved_at>`), so a replay produces the same message.
- Security: the `author_hash` salt lives in Supabase Vault and is rotated only with a documented re-hash; no profile field of an individual is logged, cached or archived; logs carry `job_id`, `candidate_key`, `route`, `vendor`, never an individual's handle.
- Government clients: amber-resolved profiles carry `route: amber` so `qualifier` keeps them out of government contracts.

## 10. Metrics and alerts

Prometheus: `hits_consumed_total`, `resolves_requested_total{platform,route}`, `profiles_emitted_total{outcome=resolved|individual|unresolvable|cached}`, `cache_hit_ratio`, `resolve_latency_seconds`, `jobs_total{status}`, `dlq_total`, `quota_denied_total` (relayed from resolver answers). Alerts: `resolver_behind` (lag above 15 minutes), `resolver_dlq` (any DLQ message), `unresolvable_rate_high` (above 20% of resolves on one platform in an hour: a token or vendor problem), `individual_leak` (a cache row for an individual with a non-empty `profile`; must never fire; tested in CI).

## 11. Dependencies

- Upstream: `keyword-matcher` (produces `discovery.hits`), `search-hit-router`, `registry-writer` (manual candidates).
- Resolvers: `fb-page-resolver`, `ig-account-resolver`, `tt-user-resolver`, `x-user-resolver`, `li-org-resolver`, `tg-channel-resolver`, `yt-channel-resolver`, `news-site-resolver`.
- `lang-dialect-id`; `quota-governor` through each resolver's `budget_tag`; `source-health-canary`; `raw-archiver`.
- Downstream: `qualifier`. Infrastructure: Redpanda, Supabase Postgres, Supabase Vault.

## 12. Risks and mitigations

- A handle-only hit resolves to the wrong account on platforms that recycle handles: the cache is re-keyed on the returned `platform_id`; a mismatch with the hit URL's id marks the profile `ambiguous` and routes it to review.
- Resolver spend jumps after a client adds broad keywords: `quota-governor` denies the resolver, the candidate waits, the admin page shows the backlog per platform.
- TikTok terms on profiling individuals: the individuals gate runs before any write; a fixture of sub-threshold TikTok accounts must produce only a hash.

## 13. Acceptance criteria

1. A `discovery.hits` message for an unseen Instagram business account produces exactly one `resolve` job on `jobs.ig-account-resolver` and, after the answer, exactly one `poster.profiles` message with `individual: false` and every rule-1 to rule-6 field populated.
2. A second hit on the same candidate within 30 days produces a `poster.profiles` message with `cached: true` and no resolver job.
3. A hit on a candidate with a `reject` decision dated 100 days ago produces no job and no profile; the same hit from a client seed list does produce a job.
4. A TikTok account with 1,500 followers and no verification produces `individual: true`, an `author_hash`, and no handle, name, biography or URL in `poster.profiles`, `poster_profiles` or `raw.items`.
5. A TikTok hit while `TT_VENDOR_ROUTE = off` produces `unresolvable: route_off` with no job.
6. Replaying the last 1,000 `discovery.hits` offsets produces zero additional resolver jobs.
7. A resolver silent for 15 minutes is retried with `attempt` incremented; after 5 attempts the candidate is in `dlq.poster-resolver` and an alert has fired.
8. `lang_share` on a candidate whose 20 sample posts are 14 Iraqi Arabic and 6 English reads `ar_iq: 0.70, en: 0.30`.
9. The `individual_leak` CI test fails the build if any code path writes a profile field for an individual.
10. `resolve_latency_seconds` p99 is below 15 minutes over a 24-hour pilot run with healthy resolvers.

## 14. Open questions

- `poster_profiles` is a new control-plane table; confirm it joins the CONVENTIONS table list.
- Whether the per-source resolvers archive raw payloads themselves or leave it to this service (assumed here, so the individuals redaction has one owner).
- Whether `lang-dialect-id` exposes a batch call for profile samples or the SDK bundles the classifier in-process.
- Which domains count as an "Iraqi outlet link": a list in `keywords` or a static list in the SDK.
