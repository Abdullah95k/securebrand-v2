# tt-user-resolver

**Platform:** TikTok · **Route:** amber (optional, flag `TT_VENDOR_ROUTE`) · **Lane:** Discover and qualify · **Owner:** Ingestion lead (Node) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

TikTok discovery works from the video outwards. tt-keyword-search and tt-hashtag-feed-poller find videos, keyword-matcher marks the ones whose author is not yet watched as `discovery.hits`, and poster-resolver gathers those authors as candidates. A candidate is only a name and an id. The qualifier cannot decide whether it is a creator worth watching (2,000 followers or verified, qualifier rule 1), whether it looks Iraqi (rule 2) or which tier it belongs to (rule 6) without numbers. tt-user-resolver fetches them: one user-info request per candidate, answered from a 30-day cache when possible, written to `poster.profiles` for the qualifier.

Plainly: TikTok has no green route to third-party content. Research Tools are academic and non-profit only, the Commercial Content API covers EU paid ads, and the Mentions API is for badged Marketing Partners. So this service is optional, runs only behind `TT_VENDOR_ROUTE` (off | tikhub | ensembledata), is disclosed in the provenance statement to clients, and is excluded from government contracts. Without it, TikTok authors stay unknown: no new creator is ever admitted to the registry, tt-profile-videos-poller only watches creators someone added by hand, and the product sees TikTok only through the keywords and hashtags it already knows. It is also the service where the individuals rule bites hardest: TikTok's Developer Terms forbid building profiles or databases on any individual, so everything below the creator threshold is kept as a hashed reference and nothing else.

## 2. Objective (the end state this service delivers)

Every candidate poster-resolver hands over is resolved at most once per 30 days, and the qualifier receives either a full profile (creators) or a bare verdict (individuals) for it. Target: 95% of candidates resolved within one hour of the job being queued (initial value, to be tuned in the pilot); zero identity fields (handle, bio, region, counts) stored for any candidate below the threshold; zero jobs lost.

## 3. Scope

### In scope

- Executing resolve jobs from `jobs.tt-user-resolver`: one user-info request per uncached candidate.
- Applying the creator threshold (2,000 followers or verified) to decide how much may be kept.
- Extracting the inputs for qualifier rule 2 from the profile: region, Iraqi city or governorate named in the bio, a +964 number, an .iq domain or Iraqi outlet link in the bio link.
- Writing `poster.profiles`; the 30-day cache; TikHub and EnsembleData adapters behind the flag, with vendor fallback.

### Out of scope

- The decision itself (qualifier), candidate counting and deduplication (poster-resolver), registry writes (registry-writer).
- The language share of a candidate's last 20 posts (open question 1).
- Watching creators once admitted (tt-profile-videos-poller) and their backfill (backfill-orchestrator).
- Any information about individuals below the threshold beyond the verdict.

## 4. Users and consumers

- **Clients** meet it indirectly: the creators that appear in their coverage without anyone adding them.
- **Ops** reads the review cards the qualifier builds from these profiles, and watches resolution lag and vendor health.
- **Downstream:** qualifier (consumes `poster.profiles`), poster-resolver (sends the jobs), registry-writer (acts on the decision), quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job per candidate on `jobs.tt-user-resolver`, emitted by poster-resolver and keyed by `candidate_key` (`tiktok:<platform_id>` or `tiktok:<handle>`; a candidate has no `source_id` yet). The job carries the lookup identifier, the `client_ids` whose hits produced it, `attempt` and a priority (a client's seed list or priority hashtag first). This service has no scheduler and no rotation of its own: it does not walk the registry, because every registered creator is already checked for new videos by tt-profile-videos-poller on the tier rotation.

**Cache.** A candidate resolved in the last 30 days is answered from `tt_user_cache` with no vendor call (`cache_hit`). The cache is the throttle: a candidate that keeps matching keywords costs one request a month, not one per hit.

**Catch-up.** Jobs run priority first, then oldest first. When the oldest job is more than the on-time window late, `resolve_backlog` fires. Resolution is not time-critical for the rotation: a late profile delays a creator's admission, never the polling of creators already registered.

**Backfill.** None here. A creator the qualifier admits arrives with `backfill_status = pending`, and backfill-orchestrator sends the 90-day video backfill to tt-profile-videos-poller. Individuals are never backfilled (qualifier rule 7).

### 5.2 Step by step

1. Consume a job; refuse and count `gov_excluded` if every client behind the hit is a government contract.
2. Look up `candidate_key` in `tt_user_cache`; if fresh, re-emit the cached message with `cache_hit = true` and stop.
3. Read `TT_VENDOR_ROUTE` and route health: use the flag's vendor, or the alternate vendor with a row in `vendor_keys` while `fallback_on` is in force. Flag off: count `flag_off`, return the job as `skipped_flag_off`; poster-resolver keeps the candidate waiting and the matched videos remain mentions with a hashed author reference.
4. Ask quota-governor for allowance under `budget_tag = tt_vendor` (sub-counter `user_info`); `wait-until` requeues, `deny` requeues with `attempt + 1`.
5. Call user info (one request): by user id when the job has one, else by handle.
6. Set `creator_threshold_met = followers >= 2000 or verified`. Creator: build the full profile with the rule 2 signals. Individual: build the bare verdict only. Not found or private: build a verdict with `status`.
7. Write `poster.profiles`; after Redpanda acknowledges, write the cache entry and discard the lookup identifier and the vendor response.

### 5.3 The call it makes

TikHub, endpoint family **user info**. Exact path, whether it takes a user id, a handle or both, and the field names: to be confirmed in the pilot. EnsembleData: the equivalent user-info endpoint behind the flag value `ensembledata`. One request per candidate, no paging; 10 requests a second per endpoint; TikHub billed on HTTP 200 only. Auth: the vendor key from Supabase Vault (`vendor_keys`), per job. The vendor response is never written to `raw.items` or the raw archive: for individuals it must not be stored, and for creators the `poster.profiles` message is the record.

### 5.4 What it gets

As the vendor returns it (illustrative; field names to be confirmed in the pilot):

```json
{
  "user": {"id": "6812345678901234567", "unique_id": "basra.store", "nickname": "متجر البصرة",
           "verified": false, "region": "IQ",
           "signature": "أفضل الأسعار في البصرة | 07701234567", "bio_link": "https://basra-store.iq"},
  "stats": {"follower_count": 18400, "video_count": 212}
}
```

Not obtained: the person's posts (the language-share signal, question 1), followers or following lists, location beyond the region field, private data. The region field is where the account was registered, not where the person lives, so it counts as one signal, never as proof.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.tt-user-resolver`; `tt_user_cache`; `sources` (skip a candidate that is already registered), `clients` (government flag), `vendor_keys`, route health, `budgets` through quota-governor; the flag `TT_VENDOR_ROUTE`.

### 6.2 Writes

`poster.profiles`, one message per candidate, the topic's own schema. A creator candidate:

```json
{
  "envelope": {
    "platform": "tiktok", "route": "amber", "vendor": "tikhub",
    "service": "tt-user-resolver",
    "candidate_key": "tiktok:6812345678901234567",
    "idempotency_key": "tiktok:profile:6812345678901234567",
    "job_id": "01J9N6F1V8B3H5Q2Z7C4M0TXRA", "attempt": 1,
    "fetched_at": "2026-10-06T10:02:31Z", "cache_hit": false,
    "retention_class": "vendor_agreed",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]
  },
  "profile": {
    "status": "ok", "creator_threshold_met": true,
    "platform_id": "6812345678901234567", "handle": "basra.store",
    "display_name": "متجر البصرة", "followers": 18400, "verified": false,
    "video_count": 212, "region": "IQ",
    "bio": "أفضل الأسعار في البصرة | 07701234567", "bio_link": "https://basra-store.iq",
    "signals": {"region_iq": true, "iraqi_place_in_bio": "البصرة", "phone_964": false, "iq_domain": true}
  }
}
```

An individual gets the same envelope and `"profile": {"status": "ok", "creator_threshold_met": false}`, nothing else. Also `service_runs` and `dlq.tt-user-resolver` after 5 failed attempts.

### 6.3 State

`tt_user_cache`: `candidate_key`, the message written, `resolved_at`, `expires_at` (30 days); an individual's entry holds only the verdict, and every entry is deleted at expiry, with no archive. `budgets` counters under `tt_vendor`; in memory only backoff state.

## 7. Limits, quotas and cost

- Price: TikHub USD 0.50 to 1.00 per 1,000 requests by daily volume tier; EnsembleData at the team's contract price. One request per uncached candidate, so every 100,000 candidates costs 100,000 requests, USD 50 to 100. Candidates per month and the cache hit rate: to be measured in the pilot.
- Route budget: about USD 280 to 560 a month for discovery plus comments at full scale across all amber TikTok services; this service's share is small and to be measured in the pilot.
- Budget tag `tt_vendor` (amber), sub-counter `user_info`; one tag for all amber TikTok services. Per-source vendor spend caps (qualifier rule 5) are the qualifier's to enforce.

## 8. Failure handling and fallback

- HTTP 429 and vendor rate-limit responses: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.tt-user-resolver` and an alert fires.
- HTTP 401 and 403: mark the vendor key and route `degraded`, stop, alert; never rotate accounts or IPs.
- Empty 200 above 5% of calls in 15 minutes: source-health-canary flips the route to `degraded` and, with the flag on, `fallback_on`. A user the vendor reports as not found or private is a verdict (`status = not_found` or `private`), not an empty 200.
- Schema change: the response is dropped, `schema_unknown` raised and the job parked; no partial profile is written.
- Partial write: the cache entry is written only after acknowledgement; a replayed job re-emits the same message and the qualifier's upsert on `candidate_key` absorbs it.

## 9. Non-functional requirements

- Throughput: bounded by the discovery rate, not by volume; at most one request per candidate per 30 days. Candidate rate: to be measured in the pilot.
- Latency: a queued candidate is resolved within the on-time window (one hour, initial value).
- Idempotency: `tiktok:profile:<platform_id>`; replayable jobs.
- Scaling: stateless workers on partition lag; no leader needed.
- Security: keys from Supabase Vault per job, never logged; no account pools, no proxies; no identity field for an individual leaves the process; the lookup identifier and vendor response are discarded after the write; provenance on every message; retention `vendor_agreed`.

## 10. Metrics and alerts

`jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `candidates_resolved_total{outcome}` (creator, individual, not_found, private), `cache_hit_ratio`, `resolve_latency_seconds`, `flag_off_total` and `individual_identity_fields_total`, which must stay zero. Alerts: `resolve_backlog`, `vendor_degraded`, `dlq_nonempty`, `empty_200_rate`, any non-zero `individual_identity_fields_total`.

## 11. Dependencies

listening-sdk, poster-resolver, qualifier, registry-writer, backfill-orchestrator, tt-profile-videos-poller, tt-keyword-search, tt-hashtag-feed-poller, quota-governor, source-health-canary, Supabase Postgres and Vault, Redpanda, TikHub and EnsembleData contracts.

## 12. Risks and mitigations

- A candidate near the threshold flips between runs: the qualifier decides on each message; the 30-day cache stops churn.
- A weak region signal admits non-Iraqi creators: it is one signal of rule 2, which needs two.
- Profile data of an individual leaks into a store: the minimal-verdict rule, the zero-tolerance metric and a payload check in CI.
- TikHub's ownership is only weakly cleared: contract review before the pilot; EnsembleData as the ready alternate.

## 13. Acceptance criteria

1. A candidate with 1,999 followers and no verified badge produces a message with `creator_threshold_met = false` and no handle, bio, region or count in the message, the cache or the logs.
2. A candidate with 2,000 followers, and one who is verified with 50, each produce a full profile with `creator_threshold_met = true`.
3. A second job for the same `candidate_key` within 30 days makes no vendor call and re-emits the message with `cache_hit = true`; on day 31 it calls the vendor again.
4. A bio with a +964 number, an Iraqi governorate, and an .iq link yields `phone_964`, `iraqi_place_in_bio` and `iq_domain` signals; the region field `IQ` yields `region_iq`.
5. A vendor "not found" yields `status = not_found` and is not counted as an empty 200.
6. With `TT_VENDOR_ROUTE = off`, no vendor call is made and the job is returned as `skipped_flag_off`; with `tikhub` then `ensembledata`, the same candidate yields messages with the same schema and `vendor` set accordingly.
7. After 5 simulated 429s the job is in `dlq.tt-user-resolver` and an alert fired; a 401 marks the route `degraded` and stops the batch.
8. The cache entry is written only after Redpanda acknowledges the message; a failed produce leaves no cache entry.
9. A job whose clients are all government contracts is refused and counted `gov_excluded`.
10. No `raw.items` message and no archive object is ever produced by this service.

## 14. Open questions

1. Should the resolver also read the candidate's latest 20 videos (one request) for the language-share signal of rule 2, for creator candidates with exactly one Iraqi signal? Proposed: yes, creators only, never individuals.
2. Who refreshes the follower counts of registered creators so tiers stay right? Proposed: poster-resolver re-queues each registered creator here when its cache entry expires, and the qualifier applies rule 6.
3. Should poster-resolver replace `candidate_key` by its hash for individuals before sending jobs? The lookup identifier would still travel in the job and be discarded after the call.
4. Do both vendors return the account's region and bio link? To be confirmed in the pilot.
