# ig-hashtag-search

**Platform:** Instagram · **Route:** green · **Lane:** Discover and qualify · **Owner:** Meta adapters engineer · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Instagram has no keyword search in its official API. The only green way to find public posts about a brand, a product, a city or a campaign on Instagram is the Hashtag Search edge of the Instagram Graph API, used under Instagram Public Content Access, which Meta grants precisely to "understand public sentiment around brand". Iraqi brands, telcos, banks and ministries are talked about through hashtags (Arabic and Latin spellings, campaign tags, city tags), so hashtags are the entry point to the Instagram share of the volume target, 4.5M items a month.

Without this service the platform has no green discovery on Instagram at all: the registry would hold only client-owned accounts and the accounts a client hands us by name, mentions would arrive only when someone tags the client, and every third-party conversation would depend on the optional amber route (ig-keyword-search), which is excluded from government contracts. The service also owns the scarcest Instagram resource, the 30-unique-hashtags-per-7-days allowance of each client business account, and keeps it from being burnt by ad hoc queries.

## 2. Objective (the end state this service delivers)

End state: every hashtag registered for a client is on a fixed rotation at its tier, queried through that client's own Instagram business account within the 30-per-7-days budget, and every media item returned reaches `raw.items` and, when its poster is not a registered source, `discovery.hits`, so the qualifier can grow the Instagram registry from real conversation.

Measurable target: rotation lag below one tier interval for 99% of hashtag sources per day; zero hashtag queries rejected for exceeding the 7-day allowance; 100% of returned media with an unregistered poster emitted as a `discovery.hits` message within 5 minutes of the fetch; staleness p95 of the newest item per hashtag within the tier maximum (1 h, 6 h, 24 h).

## 3. Scope

### In scope
- Resolving a hashtag name to its id once (`ig_hashtag_search`) and caching it as `platform_id` on the hashtag source.
- Polling `recent_media` on rotation and `top_media` on a slower cadence for every hashtag source with `platform = instagram`, `source_type = hashtag`, `route = green`.
- The hashtag budget ledger: which hashtags each client business account has queried in the rolling 7 days, enforced through quota-governor before every job.
- Backfill on add (as deep as the edge allows), catch-up after lag, dormant and retired handling.
- Emitting `raw.items` (kind `post`) and `discovery.hits`.

### Out of scope
- Keyword search of captions (no green route; see ig-keyword-search, amber).
- Fetching comments on hashtag media (no green route for third-party media; see ig-comments-fetcher, amber).
- Resolving posters (poster-resolver and ig-account-resolver).
- Deciding which hashtags a client gets when they ask for more than 30 (qualifier rule 5 and the client success team; this service only enforces the ledger).
- Stories, Reels-only edges, hashtag follower counts.

## 4. Users and consumers

- Clients (brands, companies, civilian government bodies) see the result as hashtag volume, sentiment and topics in dashboards, always aggregated and de-identified as Instagram Public Content Access requires.
- No `discovery.hits`: this service's media name no poster, so they reach clients only as mentions in keyword-matcher's `item.hits` (ADR-0031).
- normalize-item and raw-archiver consume `raw.items`; keyword-matcher and store-writer read what normalize-item publishes (ADR-0031).
- comment-decay-scheduler reads `comments_count` on each post to decide whether a comment series is worth scheduling when `IG_VENDOR_ROUTE` is on.
- Ops: hashtag budget view per client account; rotation lag.

## 5. How it works

### 5.1 Trigger and rotation

Trigger: a job on `jobs.ig-hashtag-search` emitted by the shared scheduler when a hashtag source's `next_poll_at` is due, or by backfill-orchestrator when a hashtag is added. Each job names one hashtag source, one edge (`recent_media` or `top_media`), the client Instagram business account (`ig_user_id`) whose token will be used, and `attempt`.

Tiers for hashtags (hashtags have no follower count, so tier is set by the client list and observed volume):
- Tier 1: on a client's priority list; `recent_media` every 60 minutes; `top_media` every 24 hours.
- Tier 2: every 6 hours; `top_media` every 24 hours.
- Tier 3: every 24 hours; `top_media` weekly.
- The media-per-day thresholds that separate tiers 2 and 3 are to be measured in the pilot; until then ops sets the tier at registration.
- Dormant (no new media in 30 days): weekly; a new media item promotes the hashtag back to its tier.
- Retired (no hits and no client interest for 180 days): not polled, kept in the registry.

Mechanics: `next_poll_at` is set from the start of the last poll (fixed cadence, not drift); jobs are ordered by `next_poll_at` then tier, so a hashtag is never skipped twice in a row; the queue is partitioned by `source_id`, so one hashtag is never worked twice at once. Nothing is skipped: every hashtag source with a tier other than `retired` has a non-null `next_poll_at`; a source whose `last_polled_at` is older than twice its interval raises `rotation_skipped` and is moved to the head of the queue. Catch-up: if lag exceeds one interval the service polls the most-stale hashtags first and raises `rotation_behind`; it never drops a cycle, it compresses it.

Budget rotation: before each job the service asks quota-governor for allowance under `budget_tag = ig_hashtag_<ig_user_id>`. The governor keeps, in `budgets`, the ledger of (hashtag id, first queried at) for the rolling 7 days per client business account. A hashtag already in the window costs nothing; a hashtag that would be the 31st is denied, its `next_poll_at` is set to the earliest window expiry, and the client is told through `source.events` (`fallback_on` when the amber route is on, otherwise `updated` with a `budget_wait` note). Hashtags are bound to a client account at registration so the same tag is never charged to two accounts of the same client.

Backfill on add: the first `recent_media` poll pages back as far as the edge allows (the depth cap of the edge is to be measured in the pilot, bounded by the 90-day rule), then one `top_media` fetch, then the hashtag joins the rotation with `backfill_status = done` or `capped`.

### 5.2 Step by step

1. Read the job; load the source row, the cursor row, and the client token from the vault (injected per job, never stored by the service).
2. Read `IG_VENDOR_ROUTE` and the source's `health` flag; if `health = blocked` or the token is `degraded`, return the job with `attempt + 1`.
3. Ask quota-governor for allowance (`ig_hashtag_<ig_user_id>` and `ig_graph_<client_id>`); on `wait-until`, reschedule; on `deny`, set `next_poll_at` as above.
4. If `platform_id` is null, call `ig_hashtag_search` and store the id on the source.
5. Page the edge newest-first until the first item whose `timestamp` is at or before the cursor (`recent_media`), or until the page cursor is exhausted (`top_media`, which is small and read whole).
6. Wrap each media item in the envelope and produce to `raw.items`; for each item whose poster is not a registered source, produce a `discovery.hits` message.
7. On Redpanda acknowledgement, advance the cursor to the newest `timestamp` seen, set `last_polled_at`, `next_poll_at`, and write `service_runs`.
8. Report `items_fetched`, `items_new`, `pages`, `cost_units` (one unit per call).

### 5.3 The call it makes

- Id lookup, once per hashtag: `GET /ig_hashtag_search?user_id=<ig-user-id>&q=<tag>`.
- Recent: `GET /{hashtag-id}/recent_media?user_id=<ig-user-id>&fields=id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count` with the largest page the edge allows (the maximum is to be confirmed in the pilot) and cursor pagination through the `after` cursor.
- Top: `GET /{hashtag-id}/top_media?user_id=<ig-user-id>&fields=id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count`.
- Token: the client's long-lived Instagram user access token obtained through Facebook Login; access level: Advanced Access with the Instagram Public Content Access feature approved in App Review. The `user_id` is the client's Instagram business account id; the same id is charged in the ledger.

### 5.4 What it gets

Per media item: `id`, `caption`, `media_type`, `media_url`, `permalink`, `timestamp`, `like_count`, `comments_count`. It does not get a username on hashtag media for accounts the app does not manage, so the poster of almost every item is unknown at fetch time; it does not get comments, mentions, location or audience data; `media_url` is treated as short-lived and handed to analysis-media promptly. Only business and creator accounts' public media appear on these edges, which already filters most individuals.

## 6. Inputs and outputs

### 6.1 Reads
- Queue `jobs.ig-hashtag-search`.
- Tables `sources` (hashtag rows), `client_sources`, `cursors` (source × `ig-hashtag-search`), `budgets` (hashtag ledger and call budget), `clients` (which business account owns the tag).
- Vault: the client token for the job.

### 6.2 Writes
- `raw.items`, kind `post`, `idempotency_key = instagram:post:<media-id>`, partitioned by the hashtag `source_id`.
- `discovery.hits` for media whose poster is not registered.
- `cursors`, `service_runs`, `source.events` (budget waits).

Example `raw.items` message:

```json
{
  "idempotency_key": "instagram:post:17895695668004550",
  "platform": "instagram",
  "kind": "post",
  "route": "green",
  "vendor": null,
  "service": "ig-hashtag-search",
  "job_id": "01J9Q0ZK4V8N3M2X7C5B1A6D9E",
  "source_id": "6f1c2a4e-9b3d-4c7a-8e21-5a0d3b9f7c11",
  "client_ids": ["2b7e8d1a-4f3c-4a9e-b6d2-1c0e9f8a7b65"],
  "fetched_at": "2026-10-06T09:00:12Z",
  "retention_class": "meta_on_request",
  "edge": "recent_media",
  "payload": {
    "id": "17895695668004550",
    "caption": "افتتاح الفرع الجديد في المنصور #بغداد #فايبر_اكس",
    "media_type": "IMAGE",
    "media_url": "https://scontent.cdninstagram.com/...",
    "permalink": "https://www.instagram.com/p/C9xAbCdEfGh/",
    "timestamp": "2026-10-06T08:41:03+0000",
    "like_count": 128,
    "comments_count": 14
  }
}
```

Example `discovery.hits` message: `{"platform":"instagram","keyword_id":"<hashtag source_id>","matched_in":"hashtag","item_idempotency_key":"instagram:post:17895695668004550","permalink":"https://www.instagram.com/p/C9xAbCdEfGh/","poster":{"handle":null,"platform_id":null,"handles_in_caption":["@fiberx_iq"]},"client_ids":["2b7e8d1a-..."],"route":"green","service":"ig-hashtag-search","fetched_at":"2026-10-06T09:00:12Z"}`.

### 6.3 State
- Cursor per hashtag × edge: newest `timestamp` acknowledged.
- Ledger per client business account in `budgets`: hashtag ids with first-query time in the rolling 7 days.
- Counters: calls per client token per day; `consecutive_errors` per source.
- Flags read: `IG_VENDOR_ROUTE`, source `health`, token `degraded`.

## 7. Limits, quotas and cost

- 30 unique hashtags per Instagram business account per rolling 7 days (Instagram fact sheet). This is the binding limit; it is per client account, so a client with two business accounts has two ledgers, and a client wanting more than 30 tags per account must drop tags, wait for the window, or use ig-keyword-search (amber, not for government clients).
- No username on hashtag media for accounts the app does not manage; analytics under Instagram Public Content Access only as aggregated, de-identified output.
- The Instagram Graph API's per-app and per-user call ceilings are not in our fact sheet; quota-governor meters calls under `ig_graph_<client_id>` and the ceiling is to be measured in the pilot.
- Cost: Meta Graph calls carry no per-call price (USD 0); the cost is the client's allowance and our compute. If all 30 tags of one account were tier 1, the account would make at most 30 × 24 = 720 `recent_media` first-page calls a day plus 30 `top_media` calls, before pagination.

## 8. Failure handling and fallback

- 429: exponential backoff with jitter from 30 s to 15 min, then back to the queue with `attempt + 1`; after 5 attempts to `dlq.ig-hashtag-search` and an alert.
- 401 or 403: mark the client token `degraded`, stop the batch, alert; never use another client's token for this client's hashtags.
- Allowance error for a hashtag over the 7-day window: treated as a ledger bug (the ledger should have prevented it); alert, set `next_poll_at` to window expiry.
- Empty 200 above 5% in 15 minutes: source-health-canary flips `health = degraded`; if `IG_VENDOR_ROUTE` is set to a vendor, `fallback_on` lets ig-keyword-search cover the hashtag in hashtag mode until `fallback_off`.
- Unknown payload shape: archive raw, let normalize-item raise `schema_unknown`.
- Partial batch: cursors advance only after Redpanda acks, so a replayed job completes the batch; `raw.items` is append-only and normalize-item deduplicates.

## 9. Non-functional requirements

- Throughput at full scale: the hashtag share of Instagram's 4.5M items a month is to be measured in the pilot; the service must sustain the worst case of every client account running 30 tier-1 tags (720 first-page calls per account per day) with latency p95 under one minute per job.
- Idempotent jobs; one container image; scales on `jobs.ig-hashtag-search` partition lag.
- Security: tokens injected per job from Supabase Vault, never logged; no account pools, no proxies; structured logs with `job_id`, `source_id`, `route`, `vendor`.
- Compliance: items carry provenance (green, Meta Graph, this service, fetch time); client output aggregated and de-identified; Meta data never processed for law-enforcement or national-security purposes.

## 10. Metrics and alerts

Metrics: `items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `hashtag_budget_used{ig_user_id}` (0 to 30), `hashtag_budget_waits_total`, `discovery_hits_total`, `empty_200_total`.

Alerts: `rotation_behind` (lag above one interval), `rotation_skipped`, `hashtag_budget_exhausted{ig_user_id}` at 30, token `degraded`, DLQ non-empty (reviewed daily), canary `degraded`.

## 11. Dependencies

quota-governor (ledger and call budget), source-health-canary, backfill-orchestrator, registry-writer (hashtag sources and tiers), poster-resolver and qualifier (downstream), normalize-item, raw-archiver, `listening-sdk`, Supabase Vault, Redpanda, Meta App Review (Advanced Access and Instagram Public Content Access), ig-keyword-search as the optional fallback.

## 12. Risks and mitigations

- App Review delay or refusal of Instagram Public Content Access: build the service to run in a sandbox with the company's own business account; show reviewers the working aggregated dashboard; keep ig-keyword-search as the amber bridge for non-government clients.
- 30-tag cap too small for large clients: per-account ledgers, tier discipline, and a client-facing budget view; excess tags queue by tier (qualifier rule 5).
- Posters unknown on hashtag media: discovery hits carry caption handles and the permalink; poster-resolver matches them against the registry and ig-account-resolver confirms account type; unresolved items remain de-identified mentions.
- Media volume spikes on a campaign tag: pagination bounded by the cursor; `rotation_behind` compresses rather than drops cycles.

## 13. Acceptance criteria

1. A hashtag source added for a client receives `platform_id` from one `ig_hashtag_search` call and no second lookup is made for 180 days.
2. A tier-1 hashtag is polled every 60 minutes measured from the start of the previous poll, with drift under 60 seconds over 24 hours.
3. With 31 hashtags registered on one client account, the 31st is not queried; its `next_poll_at` equals the earliest ledger expiry and a `source.events` message explains the wait.
4. Re-querying a hashtag already in the 7-day window does not increase `hashtag_budget_used`.
5. A `recent_media` poll stops paging at the first item with `timestamp` at or before the cursor, and the cursor advances only after Redpanda acknowledges the batch.
6. Replaying a job with the same `job_id` produces no duplicate rows after normalize-item.
7. Every media item without a registered poster yields exactly one `discovery.hits` message carrying the permalink and caption handles.
8. A 403 on a client token marks only that token `degraded` and leaves other clients' rotations running.
9. After a simulated 3-hour outage, the most-stale hashtags are polled first, `rotation_behind` fires, and no hashtag is skipped in the following full cycle.
10. Every `raw.items` message carries `route = green`, `service = ig-hashtag-search`, `retention_class = meta_on_request` and a `fetched_at` timestamp.

## 14. Open questions

- The maximum page size and depth of `recent_media` and `top_media`: to be measured in the pilot.
- Whether `top_media` membership should feed a "trending" score in aggregator.
- The tier-2 and tier-3 media-volume thresholds for hashtags: to be measured in the pilot.
- Whether a client with several Instagram business accounts may spread one tag list across them (ledger per account suggests yes; confirm with legal reading of the per-account allowance).
