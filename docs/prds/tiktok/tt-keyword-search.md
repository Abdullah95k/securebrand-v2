# tt-keyword-search

**Platform:** TikTok · **Route:** amber (optional, flag `TT_VENDOR_ROUTE`) · **Lane:** Discover and qualify · **Owner:** Ingestion lead (Node) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

TikTok is the second-largest line in the volume plan, 7.5M of the 30.5M items a month, and it is where an Iraqi product complaint or a competitor's campaign often surfaces first. tt-keyword-search is the discovery engine for TikTok: it runs every client keyword against the platform's search, filtered server-side to Iraq, and pushes the videos it finds into the pipeline so that keyword-matcher can raise `discovery.hits` for posters nobody is watching yet, and poster-resolver, tt-user-resolver and qualifier can turn the good ones into registered sources. Without it, TikTok coverage is frozen at the seed list and a brand hears about a viral complaint from a journalist, not its dashboard.

There is no green way to do this. TikTok has no green route to third-party content: the Research Tools are for academic and non-profit researchers only, the Commercial Content API covers paid ads in the EU, and the Mentions API is reserved for badged Marketing Partners. The only route is amber: data bought from a screened vendor that does the collection itself (TikHub, or EnsembleData, which the team already uses), so any breach of TikTok's terms sits in the vendor's contract, not ours. The service is therefore optional, runs only when `TT_VENDOR_ROUTE` names a vendor, stamps `route = amber` and the vendor on every record, is disclosed to clients in the provenance statement, and is excluded from government contracts: a keyword rule watched only by government clients is never searched.

## 2. Objective (the end state this service delivers)

End state: every active TikTok keyword rule is searched on its rotation, every video the search returns is in `raw.items` within one rotation interval of publication with full provenance, and vendor spend stays inside the budget quota-governor manages.

Measurable target: 99% of keyword rules searched within their tier interval every day, zero jobs lost, and a precision baseline (share of returned videos that keyword-matcher confirms as true hits) to be measured in the pilot and reported per keyword.

## 3. Scope

### In scope

- Searches for `sources` rows with `platform = tiktok` and `source_type = keyword_rule`, using the query strings and variants in `keywords`, country filter set to Iraq, Arabic, Sorani and Latin-script variants as separate queries.
- Incremental paging, every returned video written to `raw.items`, cursor advance after Redpanda acknowledges the batch, cost reporting.
- TikHub and EnsembleData adapters selected by the flag value; vendor fallback when source-health-canary flips `fallback_on`; one deep search (backfill) when a rule is added.

### Out of scope

- Deciding whether a video is a hit (keyword-matcher), who the poster is (poster-resolver, tt-user-resolver), whether the poster becomes a source (qualifier); comments (tt-video-comments-fetcher), metric refresh (tt-video-stats-refresher), hashtag feeds (tt-hashtag-feed-poller), registered creators' uploads (tt-profile-videos-poller).
- Any collection by us: no Research Tools application, no scraping, no account pools, no proxies.

## 4. Users and consumers

- Clients on amber-enabled contracts: new mentions and newly discovered creators on TikTok, with amber provenance shown.
- normalize-item reads the messages; keyword-matcher confirms the hit and splits it into `item.hits` or `discovery.hits`; poster-resolver consumes discovery hits and asks tt-user-resolver for the profile.
- Ops: cost and precision per keyword, rotation lag. Management: proof that TikTok discovery is live, what it costs, and that no government client receives it.

## 5. How it works

### 5.1 Trigger and rotation

A keyword rule is a registry source and follows the rotation policy, with tiers mapped by priority rather than followers. Tier 1: rules on a client's priority list, every 60 minutes, maximum staleness 1 hour. Tier 2: the default for a new rule, every 6 hours. Tier 3: set by ops for broad or noisy terms, every 24 hours. Dormant: no new video in 30 days, weekly; a new video promotes the rule back. Retired: no hits and no client interest for 180 days; not searched, kept in the registry.

Mechanics: the scheduler keeps `next_poll_at` per rule and emits a job to `jobs.tt-keyword-search` when due. Jobs are ordered by `next_poll_at` then by tier, so a rule is never skipped twice in a row. The next run is set from the start of the last run (fixed cadence, no drift). When the service is behind by more than one interval it searches the most-stale rules first and raises `rotation_behind`; a catch-up job searches only back to its cursor plus one page of overlap, so a long outage costs one sweep. Because the route pays per request, quota-governor may stretch intervals once 80% of the monthly TikTok budget is consumed, never beyond daily. Every job reads `TT_VENDOR_ROUTE` at its start; `off` acknowledges the job without a call (`jobs_total{status="flag_off"}`).

Backfill on add: one deep search that pages until the oldest video on a page is older than 90 days, the vendor stops returning pages, or quota-governor denies the next page; `backfill_status` moves pending → running → done (or capped), then the rule joins the rotation. Rotation runs are incremental: only what is newer than the cursor (newest `create_time` per rule and variant), with one page of overlap.

### 5.2 Step by step

1. The scheduler (leader replica) selects rules with `next_poll_at <= now()`, skips rules whose `client_ids` contain no non-government client, and writes one job per rule to `jobs.tt-keyword-search`, partitioned by `source_id`.
2. A worker reads the flag and the route's `health` and picks the adapter: the flag's vendor, or the alternate TikTok vendor with a row in `vendor_keys` while `fallback_on` is in force.
3. It asks quota-governor for allowance under `budget_tag = tt_vendor`; `wait-until` sleeps, `deny` requeues with `attempt + 1` and counts `quota_denied_total`.
4. For each variant it calls the vendor page by page, stopping when a page's oldest video is older than the cursor, the page holds nothing unseen in this run, or the allowance is spent.
5. Every video becomes one `raw.items` message (envelope in 6.2); duplicates across variants are collapsed within the run, the rest is left to normalize-item.
6. After Redpanda acknowledges the batch the worker advances the cursor, writes `service_runs` and reports `cost_units` (HTTP 200 responses).

### 5.3 The call it makes

- TikHub: the keyword search endpoint family with server-side country. Parameters: the query string (one variant per call), `country = IQ`, page size 20, the vendor's cursor or offset for the next page, sort by recency where supported. Authentication: the TikHub API key from `vendor_keys`, injected per job. Ceiling 10 requests a second per endpoint, enforced by the listening-sdk rate limiter. Billed on HTTP 200 only.
- EnsembleData: the equivalent keyword search endpoint; its paging and sort semantics are to be verified in the pilot.
- The listening-sdk adapter contract `search(query, country, cursor) → {items[], next_cursor, raw}` hides which vendor answered.

### 5.4 What it gets

Per video: the platform video id, caption, creation time, the author block (user id, `sec_uid`, handle, display name, follower count, verification flag), statistics at call time (plays, likes, comments, shares, collects), hashtag entries with platform ids, region, duration, cover and play URLs. Not returned: comments (tt-video-comments-fetcher), completeness (search is ranked), Iraqi signals beyond the author block (tt-user-resolver).

## 6. Inputs and outputs

### 6.1 Reads

`sources`, `keywords`, `clients` (government flag), `cursors`, `vendor_keys`, `canary_targets` and route health, `budgets` through quota-governor; the queue `jobs.tt-keyword-search`; the flag `TT_VENDOR_ROUTE` (off, tikhub, ensembledata).

### 6.2 Writes

`raw.items` (primary), one message per video, partitioned by the keyword rule's `source_id`; `cursors`, `service_runs`; `dlq.tt-keyword-search` after five failed attempts. Example `raw.items` message (vendor payload abridged; `raw` is stored exactly as returned):

```json
{
  "idempotency_key": "tiktok:video:7421000000000000123",
  "platform": "tiktok",
  "kind": "video",
  "platform_id": "7421000000000000123",
  "source_id": "3f9c2a1e-6b4d-4f7a-9c1e-2d5b8a7e4c10",
  "source_type": "keyword_rule",
  "route": "amber",
  "vendor": "tikhub",
  "service": "tt-keyword-search",
  "job_id": "job_01J9Q7M3K2",
  "attempt": 1,
  "fetched_at": "2026-10-06T14:05:12Z",
  "retention_class": "vendor_agreed",
  "context": { "keyword_id": "kw_zain_4g", "variant": "زين عراق", "country": "IQ", "page": 2 },
  "raw": {
    "aweme_id": "7421000000000000123",
    "desc": "تجربتي مع انترنت زين بالبصرة...",
    "create_time": 1759750800,
    "author": { "uid": "6800000000000000001", "sec_uid": "MS4wLjABAAAA…", "unique_id": "basra.reviews", "follower_count": 48200, "verification_type": 0 },
    "statistics": { "play_count": 15300, "digg_count": 912, "comment_count": 87, "share_count": 41 },
    "text_extra": [ { "hashtag_name": "زين", "hashtag_id": "1650000000000000002" } ],
    "region": "IQ"
  }
}
```

### 6.3 State

`cursors`: one row per rule, cursor = JSON of newest `create_time` per variant plus the vendor cursor of an unfinished backfill, with `last_success_at`, `last_error`, `consecutive_errors`; `sources.next_poll_at`, `last_polled_at`, `backfill_status`; counters in `budgets` through quota-governor. Flags are read, never written.

## 7. Limits, quotas and cost

- Vendor limits: 20 items a page, 10 requests a second per endpoint, billing on HTTP 200 only (an empty 200 still costs).
- Price: TikHub USD 0.50 to 1.00 per 1,000 requests by daily volume tier; EnsembleData at the team's contract price.
- Monthly estimate: the whole TikHub bill for discovery (this service, tt-hashtag-feed-poller, tt-user-resolver, tt-profile-videos-poller, tt-video-stats-refresher) plus 7.5M comments a month is about USD 280 to 560 a month; this service's share is to be measured in the pilot.
- Budget control: `budget_tag = tt_vendor`; intervals stretched at 80% of the monthly budget; the per-source vendor spend cap applies, so over the cap new rules queue by client priority and the client is told.

## 8. Failure handling and fallback

- HTTP 429 or a vendor rate-limit body: exponential backoff with jitter from 30 s to a maximum of 15 min, then requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.tt-keyword-search` and an alert fires.
- HTTP 401 or 403: the vendor key is marked `degraded` in `vendor_keys`, the batch stops, an alert fires; the service never rotates keys, accounts or IPs.
- Empty 200 above 5% of calls in 15 minutes: source-health-canary flips the route to `degraded` and, with the flag on, `fallback_on`; the next job uses the alternate vendor until `fallback_off`.
- Unknown payload shape: the raw message is still written and archived; normalize-item raises `schema_unknown` and parks the batch.

## 9. Non-functional requirements

- Throughput: set by the rule count; all replicas together stay under 10 requests a second per endpoint and finish each tier's sweep inside the tier interval. Latency: a Tier 1 video reaches `raw.items` within 60 minutes of publication plus vendor indexing delay (to be measured in the pilot).
- Idempotency: `tiktok:video:<video_id>`; jobs carry `attempt` and are safe to replay. Scaling: stateless workers on `jobs.tt-keyword-search` partition lag; one leader runs the scheduler loop.
- Security and compliance: vendor keys from Supabase Vault per job; no platform accounts, no proxies; structured JSON logs with `job_id`, `source_id`, `route`, `vendor`; `/healthz` and `/metrics`; nothing emitted for government-only rules.

## 10. Metrics and alerts

Metrics: `items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total{vendor}`, `quota_denied_total`, `dlq_total`, plus `empty_200_ratio`.

Alerts: `rotation_behind`; `dlq_total > 0` (reviewed daily); `vendor_degraded` on 401/403; `empty_200_ratio > 5%` over 15 minutes; `budget_80pct` from quota-governor; `precision_drop` against the pilot baseline. SLOs: rotation lag below one tier interval for 99% of rules per day; zero jobs lost.

## 11. Dependencies

listening-sdk (adapter contract, scheduler helper, rate limiter, idempotency); quota-governor; source-health-canary; normalize-item and keyword-matcher downstream; poster-resolver, tt-user-resolver and qualifier for the discovery loop; raw-archiver; Redpanda; Supabase and Vault; TikHub and EnsembleData contracts.

## 12. Risks and mitigations

- Low precision on broad Arabic terms: keyword-matcher re-checks text; ops move the rule to Tier 3 or add negative variants.
- Search is ranked, not exhaustive: tt-hashtag-feed-poller and tt-profile-videos-poller cover what search misses once a hashtag or creator is registered.
- TikHub's ownership is only weakly cleared: contract review before the pilot; EnsembleData as the ready alternate.

## 13. Acceptance criteria

1. With `TT_VENDOR_ROUTE = off`, no vendor call is made during a day of scheduled jobs and every job is counted as `flag_off`.
2. With the flag set to `tikhub` and then `ensembledata`, the same rule produces `raw.items` messages that pass the normalize-item schema, with `vendor` set accordingly.
3. A Tier 1 rule runs at a fixed 60-minute cadence over 24 hours; Tier 2 and Tier 3 rules show 6-hour and 24-hour cadences.
4. After a simulated 3-hour outage, the most-stale rules are searched first and `rotation_behind` fires once, then clears.
5. A newly added rule completes a backfill reaching 90 days or the vendor's depth, sets `backfill_status` to `done` or `capped`, and joins the rotation.
6. A rule whose `client_ids` all belong to government clients never produces a job.
7. Every message carries `route = amber`, `vendor`, `service`, `fetched_at`, `retention_class = vendor_agreed` and an `idempotency_key` of the form `tiktok:video:<id>`.
8. A stubbed 429 triggers backoff from 30 s with jitter, capped at 15 min; the sixth failure lands the job in `dlq.tt-keyword-search` with an alert.
9. A stubbed run with more than 5% empty 200s over 15 minutes flips the route to `degraded` and the next job uses the alternate vendor.
10. `cost_units_total` for a run equals the number of HTTP 200 responses in that run.

## 14. Open questions

1. Does the vendor's keyword search offer sort by recency and a stable cursor, or only ranked pages?
2. What is the effective backfill depth of search per vendor (pilot measurement)?
3. Does one `tt_vendor` budget tag serve all five amber TikTok services, or should discovery and comments have separate lines so a comment surge cannot starve discovery?
