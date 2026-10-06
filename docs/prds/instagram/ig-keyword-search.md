# ig-keyword-search

**Platform:** Instagram · **Route:** amber (optional, flag `IG_VENDOR_ROUTE`) · **Lane:** Discover and qualify · **Owner:** Backend lead, Instagram adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Clients want to know what Instagram says about a topic, not only about accounts they already follow: a product name, a campaign slogan, a competitor, a phrase of the day. The green route covers only part of that. ig-hashtag-search reads hashtags, but Instagram allows 30 unique hashtags per business account per rolling 7 days, and there is no green keyword search of captions at all. ig-keyword-search buys the rest from SociaVault, a screened vendor that does the collection itself: a daily search of every keyword and every overflow hashtag in a client's set, written into the same pipeline as every other post.

Without it a client with 60 hashtags gets 30, a client who cares about a phrase that is not a hashtag gets nothing, and when the green hashtag route degrades the hashtags go dark. The route is optional, flag-gated, disclosed to clients in the provenance statement, and excluded from government contracts.

## 2. Objective (the end state this service delivers)

When `IG_VENDOR_ROUTE = sociavault`, every Instagram keyword rule and every overflow or fallback hashtag of a non-government client that accepted the amber provenance is searched every 24 hours, and what is found reaches `raw.items` under its keyword-rule or hashtag source. Target: rotation lag below 24 hours for 99% of sources per day, monthly spend inside the `ig_vendor` budget, zero requests sent when the flag is off or the only client is a government body.

## 3. Scope

### In scope

- Rotation of every amber Instagram source of type `keyword_rule` or `hashtag`, daily by default, and execution of the jobs on `jobs.ig-keyword-search`.
- Hashtag mode for hashtags beyond the 30-tag cap (registry `route = amber`) and, while `fallback_on` holds, for hashtags that ig-hashtag-search normally covers.
- Incremental reads from the cursor, backfill jobs from backfill-orchestrator, one vendor request per page.
- Writing `raw.items` (kind `post`) with `route = amber`, `vendor = sociavault`.

### Out of scope

- Hashtags within the 30-tag cap (ig-hashtag-search, green) and the hashtag ledger `ig_hashtag_<ig_user_id>`.
- Writing `item.hits` and `discovery.hits`: keyword-matcher is the canonical writer; poster-resolver and ig-account-resolver handle the authors downstream.
- Comments (ig-comments-fetcher), accounts (ig-account-media-poller), mentions (ig-mentions-fetcher).
- Government clients: never served. Deciding which hashtags a client gets beyond 30 (qualifier rule 5 and the client success team).

## 4. Users and consumers

- **Clients** that accepted the amber provenance see "posts matching my keywords and extra hashtags, searched daily". Government clients never receive this data.
- **Ops** owns the flag, watches spend, rotation lag and the DLQ.
- **Downstream services**: normalize-item, keyword-matcher, poster-resolver (through the hit topics), comment-decay-scheduler, quota-governor, source-health-canary, raw-archiver.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.ig-keyword-search`, partitioned by `source_id`, emitted by the rotation scheduler inside this service (one leader replica through a Postgres advisory lock). The scheduler runs only while `IG_VENDOR_ROUTE = sociavault` and selects `sources` rows with `platform = instagram`, `source_type in (keyword_rule, hashtag)`, `tier != retired`, `backfill_status in (done, capped)`, and either `route = amber` and `vendor = sociavault`, or `health = fallback`. Identical queries of several clients are one source with several `client_ids` and are searched once.

**Cadence by tier.** Daily is the floor and the norm on this route, because every request costs credits: every source, whatever its tier, is searched every 24 hours. Shorter intervals exist only in fallback mode, so that a hashtag keeps its promise while the green route is down: Tier 1 (the client's priority setting) every 60 minutes, Tier 2 every 6 hours, Tier 3 daily. Push does not exist for search. Dormant (no new media found for 30 days): weekly; a new find promotes the source back to its tier. Retired (no hits and no client interest for 180 days): never searched.

**Keeping every source on rotation.** The due time lives in this service's own `cursors` row (source × `ig-keyword-search`), because ig-hashtag-search holds the same hashtag row in fallback; it is set from the START of the last search (`poll_started_at + interval`), so cadence is fixed. Jobs are emitted ordered by due time then tier, so no source is skipped twice in a row; a failed job keeps its due time and goes first on the next scan. First due times are staggered over the 24 hours so the load is flat. When the flag is turned back on after an off period, due times are re-staggered instead of all falling due at once.

**Catch-up.** `rotation_lag_seconds` is now minus the due time of the most overdue source. Above one interval the scheduler orders most-stale-first and raises `rotation_behind`. Reads are incremental from the cursor (the newest media `timestamp` seen), so a late search still returns what is newer, within the vendor's page limit.

**Budget stretch.** At 80% of the monthly `ig_vendor` budget quota-governor may stretch the shorter fallback intervals toward daily, never beyond daily, and then queues sources by tier (qualifier rule 5), telling the client; a daily search is never stretched to two days.

**Backfill on add.** A new source arrives with `backfill_status = pending`; backfill-orchestrator emits one `backfill` job; the service searches back 90 days or as far as the vendor's search and the per-source page cap allow (whichever is smaller), reports `done` or `capped`, and the source joins the rotation. Backfill messages carry `metrics_observation = backfill`.

**Comment decay.** Media found here enter `items.normalized`; comment-decay-scheduler may open the ig-comments-fetcher series (+6 h, +24 h, +3 d) for posts with comments, while the flag is on. This service fetches no comments.

### 5.2 Step by step

1. Consume a job (`source_id`, `kind` = rotation | backfill | ops_force, `attempt`); read `IG_VENDOR_ROUTE`; if it is not `sociavault`, complete as `skipped`.
2. Remove government clients from `client_ids` and keep only clients that accepted the amber provenance; if none remain, complete as `skipped`.
3. Ask quota-governor for allowance under `budget_tag = ig_vendor` for the pages expected, counting the source's own monthly spend; on wait-until, requeue; on deny, count `quota_denied_total` and keep the due time.
4. Build the query from the source (a keyword rule's terms from `keywords`, or the hashtag without `#`) and send the vendor request with the key from `vendor_keys` (Supabase Vault, per job).
5. Follow the vendor's pagination until a page holds nothing newer than the cursor or the per-source page cap is reached.
6. Write one `raw.items` message per found media; raw-archiver lands the batch under `raw/amber/instagram/<yyyy>/<mm>/<dd>/ig-keyword-search/`.
7. After Redpanda acknowledges, advance the cursor to the newest `timestamp` seen and set `last_success_at`, `consecutive_errors = 0`, `last_polled_at` and the due time.
8. Record metrics and the credits spent into `budgets`.

### 5.3 The call it makes

SociaVault's Instagram search, one request per page at 1 credit: a keyword search for `keyword_rule` sources and a hashtag search for `hashtag` sources. Endpoint paths, parameter names (query, page cursor, any date or country filter), response fields and page size: to be confirmed against the vendor's documentation in the pilot. Pagination: the vendor's cursor, followed until the cursor of the previous run is reached or the page cap is hit. Auth: the vendor API key from `vendor_keys`. The vendor is selected by `IG_VENDOR_ROUTE`; no other vendor is wired in. The 30-tag Instagram limit does not apply, because no Instagram business account of a client is used.

### 5.4 What it gets

Media matching the query, with the fields the vendor supplies. Illustrative record, field names to be confirmed in the pilot:

```json
{
  "id": "3012345678901234567",
  "caption": "عرض خاص على باقات الإنترنت المنزلي في البصرة #البصرة",
  "permalink": "https://www.instagram.com/p/DAxYzWvUtSr/",
  "timestamp": "2026-10-06T08:15:00+0000",
  "like_count": 230,
  "comments_count": 14,
  "username": "demo_shop_iq"
}
```

The author's handle stays in the raw payload because discovery needs it: poster-resolver and ig-account-resolver decide whether the author is a business or creator account; for an individual only a hashed reference survives downstream, and individuals are never backfilled. What it does not get: comments (ig-comments-fetcher); any guarantee of Iraqi relevance, because the vendor search is not known to filter by country (to be confirmed), so Iraqi relevance comes from the keyword set and from the qualifier rule on Iraqi signals.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.ig-keyword-search`; `sources`, `keywords`, `clients` (government flag, amber acceptance), `vendor_keys`, `cursors`, `budgets` through quota-governor, `health` through the SDK canary hook; `source.events` (`added`, `tier change`, `retired`, `fallback_on`, `fallback_off`); `IG_VENDOR_ROUTE`.

### 6.2 Writes

`raw.items`, one message per found media, with `source_id` = the keyword-rule or hashtag source that produced the query (search output rule):

```json
{
  "envelope": {
    "platform": "instagram", "kind": "post", "route": "amber", "vendor": "sociavault",
    "service": "ig-keyword-search",
    "source_id": "d07a3b64-9e12-4c85-b3f0-6a1e8c2d5f97",
    "platform_id": "3012345678901234567",
    "idempotency_key": "instagram:post:3012345678901234567",
    "job_id": "01J9N9J5T6K8C1E3A5X7Z9QRYM", "attempt": 1,
    "fetched_at": "2026-10-06T03:20:17Z",
    "retention_class": "vendor_agreed",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/amber/instagram/2026/10/06/ig-keyword-search/000017.jsonl.zst",
    "metrics_observation": "poll"
  },
  "payload": { "...": "the vendor's media object, unchanged" }
}
```

`client_ids` lists only non-government clients that accepted the amber provenance. Also `service_runs`, and `dlq.ig-keyword-search` after 5 failed attempts. No `item.hits` or `discovery.hits` are written here.

### 6.3 State

`cursors.cursor` (source × service) = JSON with the newest media `timestamp` and `poll_started_at`, plus `last_success_at`, `last_error`, `consecutive_errors`; `budgets` holds the `ig_vendor` counters with a sub-counter per service and a monthly spend counter per source; in memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- SociaVault: USD 1.99 to USD 4.83 per 1,000 credits depending on the volume bought, 1 credit per request for most endpoints, credits never expire; the credit price of the search endpoints and the plan: to be fixed in the pilot and the contract.
- Worked cost, per page read: one daily search of 50 sources is 1,500 requests a month, USD 2.99 to USD 7.25. A Tier 1 hashtag in fallback, searched hourly, is about 720 requests a month, USD 1.43 to USD 3.48. Pages per search: to be measured in the pilot.
- Budget tag `ig_vendor`, shared with ig-comments-fetcher; the monthly budget in USD and the per-source monthly cap (qualifier rule 5) sit in `budgets`; values to be decided with Abdullah.
- Instagram facts that frame it: 30 unique hashtags per business account per 7 days on the green route; no username on green hashtag media (here the vendor supplies authors); Business Discovery covers business and creator accounts only, and age-gated accounts are not returned; 50 comments per query applies only to client-owned media. This route is outside Instagram Public Content Access: its basis is the vendor contract and our author notice (`vendor_agreed`, default 24 months for raw text), and we still publish only aggregated, de-identified analytics from it.
- Government contracts: excluded, always.

## 8. Failure handling and fallback

- HTTP 429 and vendor rate-limit responses: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.ig-keyword-search` and an alert fires.
- HTTP 401 and 403, or an out-of-credits response (code to be confirmed in the pilot): the route is marked `degraded`, the batch stops, quota-governor denies `ig_vendor`, ops are alerted; no keys or accounts are rotated.
- Empty 200 (no media for a query that normally returns some): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. This service is itself the fallback for ig-hashtag-search; it has none of its own, so it never sets `fallback_on`.
- Flag turned off: no new jobs; running jobs complete as `skipped`; items already written stay, with their provenance.
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: cursors move only after acknowledgement; a replayed job re-emits the same posts and normalize-item deduplicates them.

## 9. Non-functional requirements

- Throughput: bounded by the `ig_vendor` budget, not by capacity; the number of sources and pages is to be measured in the pilot.
- Latency: a media visible to the vendor reaches `raw.items` within 24 hours plus fetch time (within the fallback interval in fallback mode).
- Idempotency: `instagram:post:<platform_id>`; replayable jobs; append-only `raw.items`. Vendor ids may differ from Graph ids, so the same post can arrive by two routes; open question 2.
- Scaling: stateless workers on partition lag; one leader scheduler; request rate set by quota-governor.
- Security: vendor key from Supabase Vault per job, never logged; no account pools, no CAPTCHA solving, no proxies; amber data excluded from government contracts; provenance on every message and in the client-facing statement; individuals are never profiled.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}` (including `skipped`), `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total` (credits), `quota_denied_total`, `dlq_total`, plus `spend_usd_total{source}`, `pages_per_search`, `sources_in_rotation{tier}` and `empty_200_total`. Alerts: `rotation_behind`, `vendor_credits_low`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`, `budget_80_percent`. SLO: rotation lag below one interval for 99% of sources per day.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, keyword-matcher, comment-decay-scheduler, backfill-orchestrator, registry-writer, qualifier, ig-hashtag-search (the green counterpart and fallback source), Supabase Postgres and Vault, Redpanda, and the SociaVault contract.

## 12. Risks and mitigations

- SociaVault is only weakly cleared (country known, owner not verified): the owner is verified before the contract; an Israeli affiliation ends the service.
- Vendor breach exposure sits in the vendor's contract: optional, flag-gated, disclosed, excluded from government contracts.
- A global, unfiltered search wastes credits on non-Iraqi results: Arabic keyword sets, a per-source monthly cap and the qualifier's Iraqi-signal rule limit it.
- Cost growth from many sources: the budget, the per-source cap and queueing by tier hold spend.
- Vendor endpoint changes: canary on empty 200 and `schema_unknown` parking.

## 13. Acceptance criteria

1. With `IG_VENDOR_ROUTE = off`, the scheduler emits no job, running jobs complete as `skipped`, and no request is sent; when it is turned on again, no more than one twenty-fourth of the sources fall due in any hour.
2. With 100 keyword-rule sources over 7 simulated days, every source is searched every 24 hours; a search that started at 03:00:00 and took 5 minutes has its next due time at 03:00:00 the next day; no source is skipped twice in a row.
3. A source with no new media for 30 days is searched weekly and goes back to its tier at the next find; a retired source is never searched.
4. A client's 31st hashtag (registry `route = amber`) is searched here and not by ig-hashtag-search, and the ledger `ig_hashtag_<ig_user_id>` is untouched.
5. After `fallback_on` for a Tier 1 hashtag it is searched every 60 minutes until `fallback_off`; at 80% of the monthly `ig_vendor` budget quota-governor stretches that interval to daily and never beyond.
6. A keyword rule watched only by a government client is never searched; on a shared rule every message's `client_ids` lists only non-government clients that accepted the amber provenance.
7. Every found media is in `raw.items` with `source_id` = the source that produced the query, `route = amber`, `vendor = sociavault`, `retention_class = vendor_agreed`; no `item.hits` or `discovery.hits` message comes from this service.
8. Two clients with the same keyword produce one source and one search a day.
9. `cost_units` per job equals the requests sent, the `ig_vendor` counter equals credits times the contracted USD rate, and no request is sent after a quota-governor deny.
10. The cursor does not advance when the Redpanda produce fails; a replayed job yields the same `idempotency_key`s and normalize-item stores one item per post.
11. A `backfill` job searches back 90 days or as far as the vendor and the page cap allow, sets `capped` when it ends earlier, and the source joins the rotation only afterwards.
12. A 429 triggers backoff from 30 s to at most 15 min; after 5 attempts the job is in `dlq.ig-keyword-search` and an alert fired; a 401 marks the route `degraded` and stops the batch with no key rotation.

## 14. Open questions

1. SociaVault's search endpoints: whether results can be ordered by recency or filtered by date, page size and pagination, whether captions are searched, whether any country filter exists, and which fields (author handle, ids) come back: to be confirmed in the pilot.
2. Cross-route deduplication: vendor media ids may differ from Graph ids. Proposed: normalize-item also joins on the shortcode in `permalink`; to be confirmed with its owner.
3. The monthly `ig_vendor` budget in USD and the per-source monthly cap (qualifier rule 5): to be decided with Abdullah.
