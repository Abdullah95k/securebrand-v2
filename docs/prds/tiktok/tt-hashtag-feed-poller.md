# tt-hashtag-feed-poller

**Platform:** TikTok · **Route:** amber (optional, flag `TT_VENDOR_ROUTE`) · **Lane:** Discover and qualify · **Owner:** Ingestion lead (Node) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Campaigns on TikTok live under hashtags: a telecom launch, a bank promotion, a boycott, a ministry initiative. Keyword search finds videos whose captions mention a term; it does not reliably return everything posted under a tag, because the platform ranks search results. tt-hashtag-feed-poller treats every registered hashtag as a source and polls its feed on the rotation, so every video published under a client's tag enters `raw.items`, every poster gets a chance to be qualified through poster-resolver, tt-user-resolver and qualifier, and every video starts its comment series through comment-decay-scheduler. Without it, campaign tracking on the platform that supplies 7.5M of the 30.5M monthly items has no reliable denominator: the client sees a sample of its campaign, not the campaign.

There is no green route for this. TikTok has no green route to third-party content: the Research Tools are for academic and non-profit researchers only, the Commercial Content API covers paid ads in the EU, and the Mentions API is reserved for badged Marketing Partners. The only route is amber: hashtag feed data bought from a screened vendor that does the collection itself (TikHub, or EnsembleData, which the team already uses), so any breach of TikTok's terms sits in the vendor's contract, not ours. The service is therefore optional, runs only when `TT_VENDOR_ROUTE` names a vendor, stamps `route = amber` and the vendor on every record, is disclosed to clients in the provenance statement, and is excluded from government contracts: a hashtag watched only by government clients is never polled.

## 2. Objective (the end state this service delivers)

End state: every TikTok hashtag in the registry is re-checked for new videos on its tier's cadence, every new video is in `raw.items` within one tier interval of publication with provenance, and no hashtag is skipped twice in a row.

Measurable target: rotation lag below one tier interval for 99% of hashtag sources per day; `staleness_seconds_p95` under the tier's maximum; the share of videos the poller finds that tt-keyword-search did not (the coverage gain that justifies the service) to be measured in the pilot.

## 3. Scope

### In scope

- Polling `sources` rows with `platform = tiktok` and `source_type = hashtag` through the vendor's hashtag feed, incremental against the cursor, with a 90-day backfill on add.
- Writing every video to `raw.items`, reporting cost, keeping `next_poll_at`, `cursors` and `backfill_status`.
- TikHub and EnsembleData adapters behind the flag value, with vendor fallback from source-health-canary.
- Learning hashtag platform ids from videos already fetched, so a client can add a tag by name.

### Out of scope

- Keyword search (tt-keyword-search), creator uploads (tt-profile-videos-poller), comments (tt-video-comments-fetcher), metric refresh (tt-video-stats-refresher), poster identity (tt-user-resolver), registry decisions (qualifier).
- Trend discovery (finding hashtags nobody asked for) and any collection by us.

## 4. Users and consumers

- Clients running or watching a campaign tag, and clients watching a competitor's tag; amber provenance is shown on every item.
- normalize-item and keyword-matcher: a video from a hashtag source is a hit for each of the hashtag's clients who passes the client gate, under the source's keyword, with `matched_by = source` when the text does not match. Every hit goes to `item.hits`, with a `discovery.hits` candidate for an unregistered poster (ADR-0031, ADR-0044); poster-resolver takes the candidates.
- comment-decay-scheduler starts the comment series on each new video; aggregator builds the campaign view.
- Ops: cost per hashtag, pages per run, rotation lag. Management: campaign coverage on TikTok as a sellable feature.

## 5. How it works

### 5.1 Trigger and rotation

Hashtags have no follower count, so the tier is set by interest and activity: Tier 1 for a tag on a client's priority list, polled every 60 minutes with maximum staleness 1 hour; Tier 2 as the default for a client-added tag, every 6 hours; Tier 3 for ops-added broad tags, every 24 hours; Dormant when no new video appears in 30 days, weekly, promoted back by the next new video; Retired after 180 days without hits or client interest, not polled, kept in the registry. Promotion from Tier 2 to Tier 1 by posting rate is possible once the pilot has measured typical rates.

Mechanics: the scheduler keeps `next_poll_at` per hashtag and emits a job to `jobs.tt-hashtag-feed-poller` when due; jobs are ordered by `next_poll_at` then by tier, so no hashtag is skipped twice in a row; the next poll is set from the start of the last poll (fixed cadence, no drift). If the poller is behind by more than one interval it polls the most-stale hashtags first and raises `rotation_behind`. Because the route pays per request, quota-governor may stretch the intervals once 80% of the monthly TikTok budget is consumed, never beyond daily. Every job reads `TT_VENDOR_ROUTE` at its start; `off` acknowledges the job without a call.

Catch-up: after an outage, one job per overdue hashtag, most stale first; a catch-up poll uses the same stop rules as a normal poll, so the cost of an outage is one sweep.

Backfill on add: the first job pages the feed until the oldest video on a page is older than 90 days, the vendor stops returning pages, or quota-governor denies the next page (whichever comes first); `backfill_status` moves pending → running → done or capped; then the hashtag joins the rotation. The vendor's feed depth is to be measured in the pilot.

Incremental: the feed is ranked, not strictly chronological, so a rotation poll pages until a whole page holds no video that is new to this hashtag (seen-page rule), with a per-run page cap from quota-governor; a video older than the cursor that is new is still emitted, and normalize-item removes anything already stored. A full re-read happens only for backfill.

### 5.2 Step by step

1. The scheduler selects hashtags with `next_poll_at <= now()`, skips those whose `client_ids` contain no non-government client, and writes one job per hashtag to `jobs.tt-hashtag-feed-poller`, partitioned by `source_id`.
2. A worker reads the flag and the route's `health` and picks the adapter: the flag's vendor, or the alternate TikTok vendor with a row in `vendor_keys` while `fallback_on` is in force.
3. It asks quota-governor for allowance under `budget_tag = tt_vendor`; `wait-until` sleeps, `deny` requeues with `attempt + 1`.
4. It resolves the hashtag's `platform_id`; if the source was added by name and has no id yet, it takes the id from the newest `raw.items` video whose hashtag entries carry that name, or asks the vendor if the feed accepts a name (to be confirmed in the pilot).
5. It calls the hashtag feed page by page, keeps a set of video ids seen in this run and the ids stored for this hashtag in the cursor's recent window, and stops by the rules in 5.1.
6. Every video becomes one `raw.items` message (6.2); after Redpanda acknowledges the batch the worker advances the cursor (newest `create_time` and the recent id window), writes `service_runs`, and reports `cost_units` (HTTP 200 responses).

### 5.3 The call it makes

- TikHub: the hashtag feed endpoint family. Parameters: the hashtag platform id, page size 20, the vendor's cursor for the next page. Authentication: the TikHub API key from `vendor_keys`, injected per job. Ceiling 10 requests a second per endpoint, enforced by the listening-sdk rate limiter. Billed on HTTP 200 only.
- EnsembleData: the equivalent hashtag feed endpoint; its paging semantics and whether it accepts a tag name are to be verified in the pilot.
- The listening-sdk adapter contract `hashtagFeed(hashtag_id, cursor) → {items[], next_cursor, raw}` hides which vendor answered.

### 5.4 What it gets

Per video: the platform video id, caption, creation time, author block (user id, `sec_uid`, handle, display name, follower count, verification flag), statistics at call time (plays, likes, comments, shares, collects), all hashtag entries with their ids, region, duration, cover and play URLs. Not returned: comments (tt-video-comments-fetcher), a guarantee of chronological order or completeness (the feed is ranked by the platform), the hashtag's own total video or view count on every vendor (to be verified), private or removed videos.

## 6. Inputs and outputs

### 6.1 Reads

`sources`, `clients` (government flag), `cursors`, `vendor_keys`, `canary_targets` and route health, `budgets` through quota-governor; the queue `jobs.tt-hashtag-feed-poller`; the flag `TT_VENDOR_ROUTE` (off, tikhub, ensembledata); `raw.items` history only to learn hashtag ids.

### 6.2 Writes

`raw.items` (primary), one message per video, partitioned by the hashtag's `source_id`; `cursors`, `service_runs`, `sources.next_poll_at`, `last_polled_at`, `backfill_status`; `dlq.tt-hashtag-feed-poller` after five failed attempts. Example `raw.items` message (vendor payload abridged; `raw` is stored exactly as returned):

```json
{
  "idempotency_key": "tiktok:video:7420000000000000456",
  "platform": "tiktok",
  "kind": "video",
  "platform_id": "7420000000000000456",
  "source_id": "9b1e4d2c-7a3f-4e8b-b2c1-5f6a7d8e9c01",
  "source_type": "hashtag",
  "route": "amber",
  "vendor": "ensembledata",
  "service": "tt-hashtag-feed-poller",
  "job_id": "01M4872SXGZPDRA21SXW1ZYD7N",
  "attempt": 1,
  "fetched_at": "2026-10-06T09:00:41Z",
  "retention_class": "vendor_agreed",
  "context": { "hashtag_id": "1650000000000000002", "hashtag_name": "زين_الخير", "page": 1, "backfill": false },
  "raw": {
    "aweme_id": "7420000000000000456",
    "desc": "#زين_الخير حملة التبرعات بالموصل",
    "create_time": 1759735200,
    "author": { "uid": "6800000000000000777", "sec_uid": "MS4wLjABAAAB…", "unique_id": "mosul.daily", "follower_count": 120500, "verification_type": 1 },
    "statistics": { "play_count": 40100, "digg_count": 2210, "comment_count": 310, "share_count": 95 },
    "text_extra": [ { "hashtag_name": "زين_الخير", "hashtag_id": "1650000000000000002" } ]
  }
}
```

Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

### 6.3 State

`cursors`: one row per hashtag, cursor = JSON of newest `create_time`, the vendor cursor of an unfinished backfill, and the recent window of video ids used by the seen-page rule (window length to be measured in the pilot); `last_success_at`, `last_error`, `consecutive_errors`. `sources.next_poll_at`, `last_polled_at`, `backfill_status`, `platform_id` once learned. Counters in `budgets` through quota-governor. Flags are read, never written.

## 7. Limits, quotas and cost

- Vendor limits: 20 items a page, 10 requests a second per endpoint, billing on HTTP 200 only (an empty 200 still costs).
- Price: TikHub USD 0.50 to 1.00 per 1,000 requests by daily volume tier; EnsembleData at the team's contract price.
- Volume: hashtags × polls a day × pages a poll. A Tier 1 tag polled 24 times a day at one page costs 24 requests a day, USD 0.012 to 0.024; a busy campaign tag paging deeper costs proportionally more. Pages a poll are to be measured in the pilot.
- Monthly estimate: the whole TikHub bill for discovery (tt-keyword-search, this service, tt-user-resolver, tt-profile-videos-poller, tt-video-stats-refresher) plus 7.5M comments a month is about USD 280 to 560 a month; this service's share is to be measured in the pilot.
- Budget control: `budget_tag = tt_vendor`; intervals stretched at 80% of the monthly budget, never beyond daily; the per-source vendor spend cap applies, so over the cap new hashtags queue by client priority and the client is told.

## 8. Failure handling and fallback

- HTTP 429 or a vendor rate-limit body: exponential backoff with jitter from 30 s to a maximum of 15 min, then requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.tt-hashtag-feed-poller` and an alert fires.
- HTTP 401 or 403: the vendor key is marked `degraded`, the batch stops, an alert fires; no key, account or IP rotation.
- Empty 200 above 5% of calls in 15 minutes: source-health-canary flips the route to `degraded` and, with the flag on, `fallback_on`; the next job uses the alternate vendor until `fallback_off`. A genuinely empty feed for a dormant tag is distinguished by the vendor's own status fields and is not counted as an empty 200.
- Unknown payload shape: the raw message is still written and archived; normalize-item raises `schema_unknown` and parks the batch.
- Hashtag id not resolvable: the job ends with `last_error = hashtag_id_unknown`, the source goes to `health = degraded`, and ops are alerted after 3 consecutive failures.

## 9. Non-functional requirements

- Throughput: set by the hashtag count; all replicas together stay under 10 requests a second per endpoint and finish each tier's sweep inside the tier interval. Latency: a Tier 1 tag's new video reaches `raw.items` within 60 minutes of publication plus vendor delay (to be measured in the pilot).
- Idempotency: `tiktok:video:<video_id>`; jobs carry `attempt` and are safe to replay; cursors advance only after Redpanda acknowledges the batch.
- Scaling: stateless workers on `jobs.tt-hashtag-feed-poller` partition lag, one hashtag never worked twice at once; one leader runs the scheduler loop.
- Security and compliance: vendor keys from Supabase Vault per job; no platform accounts, no proxies; structured JSON logs with `job_id`, `source_id`, `route`, `vendor`; `/healthz` and `/metrics`; nothing emitted for government-only hashtags; author identities never indexed by this service.

## 10. Metrics and alerts

Metrics: `items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total{vendor}`, `quota_denied_total`, `dlq_total`, plus `pages_per_poll` and `empty_200_ratio`.

Alerts: `rotation_behind`; `dlq_total > 0` (reviewed daily); `vendor_degraded` on 401/403; `empty_200_ratio > 5%` over 15 minutes; `budget_80pct` from quota-governor; `hashtag_id_unknown` after 3 consecutive failures. SLOs: rotation lag below one tier interval for 99% of hashtags per day; zero jobs lost.

## 11. Dependencies

listening-sdk (adapter contract, scheduler helper, rate limiter, idempotency); quota-governor; source-health-canary; normalize-item and keyword-matcher downstream; poster-resolver, tt-user-resolver and qualifier; comment-decay-scheduler; raw-archiver; Redpanda; Supabase and Vault; TikHub and EnsembleData contracts.

## 12. Risks and mitigations

- The feed is ranked, so a low-engagement video under a tag may never surface: tt-keyword-search on the tag text and tt-profile-videos-poller on registered creators cover part of the gap; the coverage gain is measured in the pilot and told to the client honestly.
- Deep pages on a viral tag burn budget: per-run page cap from quota-governor, `pages_per_poll` alert, Tier 3 for generic tags.
- Vendor shape change or outage: two adapters, canary fallback, raw payload archived.
- TikHub's ownership is only weakly cleared: contract review before the pilot; EnsembleData as the ready alternate.

## 13. Acceptance criteria

1. With `TT_VENDOR_ROUTE = off`, no vendor call is made during a day: the scheduler emits no job, and a job already queued ends `skipped_flag_off` at its start, never as an attempt (ADR-0050, ADR-0017).
2. With the flag set to `tikhub` and then `ensembledata`, the same hashtag produces `raw.items` messages that pass the normalize-item schema, with `vendor` set accordingly.
3. A Tier 1 hashtag is polled at a fixed 60-minute cadence over 24 hours; Tier 2 and Tier 3 hashtags show 6-hour and 24-hour cadences; a dormant hashtag is polled weekly and returns to its tier on the next new video.
4. After a simulated 3-hour outage, the most-stale hashtags are polled first and `rotation_behind` fires once, then clears.
5. A hashtag added by name obtains its `platform_id` from stored videos or the vendor and completes a backfill reaching 90 days or the feed's depth, with `backfill_status` ending `done` or `capped`.
6. A rotation poll stops at the first page holding no new video; `items_new_total` for a quiet hashtag is zero and `pages_per_poll` is one.
7. A hashtag whose `client_ids` all belong to government clients never produces a job.
8. Every message carries `route = amber`, `vendor`, `service`, `source_type = hashtag`, `fetched_at`, `retention_class = vendor_agreed` and an `idempotency_key` of the form `tiktok:video:<id>`.
9. A stubbed 429 triggers backoff from 30 s with jitter, capped at 15 min; the fifth failed attempt lands the job in `dlq.tt-hashtag-feed-poller` with an alert (ADR-0057).
10. A stubbed run with more than 5% empty 200s over 15 minutes flips the route to `degraded` and the next job uses the alternate vendor.
11. `cost_units_total` for a run equals the number of HTTP 200 responses in that run.

## 14. Open questions

1. Does either vendor's hashtag feed accept a tag name, or only the platform id? This decides whether step 4 needs the stored-video lookup at all.
2. What is the feed's effective depth (backfill cap) and ordering per vendor?
3. What posting-rate threshold should promote a Tier 2 campaign tag to Tier 1 automatically?
4. Should keyword-matcher treat hashtag-source videos as hits by construction (this PRD assumes yes), or require a text match as well for noisy tags?
