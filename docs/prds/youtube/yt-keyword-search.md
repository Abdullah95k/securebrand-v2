# yt-keyword-search

**Platform:** YouTube · **Route:** green · **Lane:** Discover and qualify · **Owner:** YouTube lane backend engineer (Node/TypeScript) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

YouTube is the only large platform in our stack where keyword search over third-party content exists on a green route: `search.list` in the YouTube Data API v3 returns public videos matching a query, limited to videos viewable in Iraq and ranked for Arabic relevance.

Without it the YouTube lane only sees channels already in the registry. A new channel that starts talking about a client (a complaint video about an ISP, a review of a bank's app) stays invisible until a person adds it by hand. The product loses its YouTube discovery feed (`discovery.hits` would carry only what yt-web-search-bridge finds through Perplexity and Mojeek, which index a fraction of fresh uploads) and the qualifier starves.

The constraint that shapes the service is cost: one `search.list` call is 100 units, one percent of the default 10,000-unit daily quota, so the hard cap is 100 calls a day and quota-governor plans for 20 to 30.

## 2. Objective (the end state this service delivers)

End state: every priority term (20 to 30 across all clients, curated by client success) is searched once a day, newest first, from the previous run's cursor; every matching video reaches `raw.items` the same day with a first-sight job queued for yt-video-details-fetcher, so keyword-matcher, poster-resolver and the qualifier see it without a human step.

Measurable target: 100% of priority terms searched every day; 20 to 30 `search.list` calls a day in steady state, never above 100; a video matching a priority term is in `raw.items` within 24 hours of upload (`staleness_seconds_p95` under 86,400).

## 3. Scope

### In scope

- Daily `search.list` runs for keyword rules with `platform = youtube`, `source_type = keyword_rule`, `tier = 1` (the priority list), one cursor (`publishedAfter`) per rule.
- A second page only when the first is full and every item is newer than the cursor, with governor approval.
- Raw video records to `raw.items`; first-sight jobs to `jobs.yt-video-details-fetcher`.
- A one-time backfill when a term is promoted to the priority list.
- Spelling variants of one term joined with the `|` operator so one call covers several variants.

### Out of scope

- The long tail of keywords (yt-web-search-bridge); channel lookups (yt-channel-resolver).
- Statistics, duration and topics (yt-video-details-fetcher); comments (yt-comments-fetcher, yt-replies-fetcher).
- Keyword matching (keyword-matcher); qualification (poster-resolver, qualifier, registry-writer). The API has no keyword search over comments.

## 4. Users and consumers

- normalize-item deduplicates the raw video records; keyword-matcher turns every match into `item.hits`, with a `discovery.hits` candidate when the channel is unknown (ADR-0031).
- poster-resolver, through yt-channel-resolver, turns `discovery.hits` into `poster.profiles` for the qualifier.
- yt-video-details-fetcher receives first-sight jobs; quota-governor grants or denies the daily search allowance.
- Client success managers curate the priority list of 20 to 30 terms; Abdullah reads the weekly discovery report (terms run, videos found, channels qualified).

## 5. How it works

### 5.1 Trigger and rotation

- Cadence: one run a day at `YT_SEARCH_RUN_AT` (default 06:00 Asia/Baghdad), one `search.list` call per priority term. Keyword rules are not reach-tiered; `tier = 1` means API search, `tier = 2` or `3` means the web bridge.
- Order: terms sorted by `last_polled_at` ascending (most stale first), then by the number of clients watching the term. If the governor denies allowance part-way, the leftover terms are first in line the next day, so no term is skipped twice in a row.
- Cursor: `publishedAfter` = the start time of the term's last successful run minus a 6-hour overlap; duplicates collapse in normalize-item on `youtube:video:<videoId>`.
- Paging: one page of 50 is normally enough for a daily window. When all 50 items are newer than the cursor and `nextPageToken` is present, the service asks the governor for one more call; at most 2 extra pages per term per day, so a viral term cannot drain the bucket.
- Catch-up: a missed run is not replayed; the next run starts from the old cursor and may trigger the extra-page rule.
- Backfill: when a term is promoted to `tier = 1`, the first run uses `publishedAfter` = now minus 90 days and may page up to the governor's backfill allowance (set in `budgets`, to be measured in the pilot); then the term joins the daily rotation. Every other keyword rule goes to yt-web-search-bridge, which spends web-search money rather than API units.

### 5.2 Step by step

1. Read the priority keyword rules from `sources` joined to `keywords` for the term, its variants and `client_ids`.
2. Request allowance from quota-governor for `budget_tag = youtube_data_api`, bucket `search`, amount = terms × 100 units; on `wait-until` sleep and retry, on `deny` record `quota_denied_total` and end the run.
3. Build `q` per term: the term and its curated variants joined with `|`, quoted when they contain spaces.
4. Call `search.list` (5.3); stop paging when an item's `publishedAt` is older than the cursor.
5. Publish each item in the envelope to `raw.items` (kind `video`, origin `search`), then one `jobs.yt-video-details-fetcher` message with the batch of video ids (kind `first_sight`).
6. After Redpanda acknowledges the batch, advance the term's `cursors` row, write `service_runs` and report `cost_units` to the governor for every call made, failed calls included.

### 5.3 The call it makes

```
GET https://www.googleapis.com/youtube/v3/search
  ?part=snippet
  &q=<term|variant1|variant2>
  &type=video
  &regionCode=IQ
  &relevanceLanguage=ar
  &order=date
  &publishedAfter=<RFC 3339 cursor>
  &safeSearch=none
  &maxResults=50
  &pageToken=<extra pages only>
  &key=<company app API key, injected per job from Supabase Vault>
```

- Cost: 100 units per call; every page is a call. `maxResults=50` is the maximum for `search.list`. Auth is an API key for public data; no OAuth, no account pool.
- `relevanceLanguage=ar` is a ranking hint, not a filter; Sorani terms run with `relevanceLanguage=ku` (the only ISO 639-1 Kurdish code), effect on recall to be measured in the pilot. `regionCode=IQ` returns videos viewable in Iraq, not videos uploaded from Iraq.

### 5.4 What it gets

Per item: `id.videoId`, `snippet.publishedAt`, `snippet.channelId`, `snippet.channelTitle`, `snippet.title`, `snippet.description` (truncated), `snippet.thumbnails`, `snippet.liveBroadcastContent`. Per response: `nextPageToken` and `pageInfo.totalResults` (an estimate).

It does not get view, like or comment counts, duration, tags, `topicDetails`, the full description, comment text or channel statistics; those come from yt-video-details-fetcher and yt-channel-resolver.

## 6. Inputs and outputs

### 6.1 Reads

- Control plane: `sources` (keyword rules), `keywords` (terms, variants, language, `client_ids`), `cursors` (rule × `yt-keyword-search`), `budgets` through quota-governor, the API key through Supabase Vault. No topics are consumed.

### 6.2 Writes

- `raw.items` (partitioned by the keyword rule's `source_id`); `jobs.yt-video-details-fetcher` (kind `first_sight`); `service_runs`, `cursors`, `budgets` counters through the governor.

Example `raw.items` message:

```json
{
  "idempotency_key": "youtube:video:dQw4w9WgXcQ",
  "platform": "youtube",
  "kind": "video",
  "platform_id": "dQw4w9WgXcQ",
  "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
  "source_id": "3f1c2a6e-9d2b-4c1e-9a6f-2b7d8e5f4a10",
  "source_type": "keyword_rule",
  "route": "green",
  "vendor": null,
  "service": "yt-keyword-search",
  "origin": "search",
  "job_id": "01M47JP18081JQQZ19WYHA1ZH3",
  "attempt": 1,
  "fetched_at": "2026-10-06T03:04:11Z",
  "retention_class": "youtube_30d_text",
  "cost_units": 100,
  "partial": true,
  "payload": { "kind": "youtube#searchResult", "id": { "videoId": "dQw4w9WgXcQ" }, "snippet": { "publishedAt": "2026-10-06T01:12:00Z", "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw", "title": "...", "description": "..." } }
}
```

Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

`partial: true` tells normalize-item that statistics follow from yt-video-details-fetcher.

### 6.3 State

- `cursors`: one row per keyword rule; `cursor` = RFC 3339 timestamp of the last successful run start, plus `last_success_at`, `last_error`, `consecutive_errors`.
- Governor counters: `search` bucket calls today, pages per term today. `service_runs`: last run, terms run and skipped, units spent.

## 7. Limits, quotas and cost

- YouTube Data API: 10,000 units a day by default; `search.list` costs 100 units, hence a hard cap of 100 search calls a day, which would consume the entire quota if reached. Extensions are granted by audit only.
- Quota-governor split for the YouTube lane (planning figures; the quota arithmetic is to be measured in the pilot): about 4,000 to 5,000 units a day for the 1-unit endpoints (`playlistItems.list`, `videos.list`, `commentThreads.list`, `comments.list`, `channels.list`) that carry the 3.0M items a month; the `search` bucket holds the 100-call cap but is planned at 20 to 30 calls a day (2,000 to 3,000 units); the rest is reserve for catch-up, hot posts and client-requested refreshes.
- This service draws only from the `search` bucket, extra pages and backfills included, never from the reserve, so a discovery spike cannot starve comment fetching. Money: USD 0 at the default quota.
- Developer Policies binding the data produced: raw comment text kept no longer than 30 days (delete or refresh, enforced by yt-text-purger); derived metrics kept up to 36 months for Analytics & Reporting clients; no aggregation across channels of different owners except under the carve-out; no profiling on protected attributes; audit at any time, so provenance and purge logs must be producible on request.

## 8. Failure handling and fallback

- HTTP 403 `quotaExceeded`: stop the run at once, report to quota-governor (which marks the YouTube budget exhausted for every service), alert; no retry before the governor's next day boundary.
- HTTP 403 with any other reason, or 401: mark the API key `degraded`, stop the batch, alert; never rotate keys or projects to get around it.
- HTTP 429 or 5xx: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the run goes to `dlq.yt-keyword-search` and an alert fires.
- HTTP 400 (bad query or `publishedAfter`): the term records `last_error`, is skipped for the day and lands in `review_queue` without blocking other terms.
- Empty 200: one term returning zero items is normal; a run in which every term returns zero counts as an empty-200 event for source-health-canary (5% in 15 minutes flips the route `degraded`). There is no amber alternative; discovery recall falls back to yt-web-search-bridge on its own budget.
- Schema change: the unknown shape is still archived; normalize-item raises `schema_unknown` and parks the batch.

## 9. Non-functional requirements

- Throughput: at most 100 calls a day; a run of 30 terms completes in under 5 minutes.
- Idempotency: replaying a run is safe; the cursor advances only after Redpanda acknowledges the batch; duplicates collapse in normalize-item.
- Scaling: one replica with a leader lock in the control plane.
- Security: API key from Supabase Vault per job; no account pools, proxies or CAPTCHA solving; structured JSON logs with `job_id`, `source_id`, `route`, `vendor`; `/healthz` and `/metrics` exposed. Every record carries `route = green`, `vendor = null`, `service` and `fetched_at` for the provenance statement.

## 10. Metrics and alerts

- Standard: `items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`.
- Service-specific: `yt_search_calls_total{page}`, `yt_search_terms_skipped_total`, `yt_search_zero_result_terms_total`.
- Alerts: `search` bucket above 80% of its daily allowance; a term skipped two days running; `quotaExceeded` seen; every term returning zero in one run; `rotation_lag_seconds` above 86,400.

## 11. Dependencies

quota-governor, normalize-item, keyword-matcher, poster-resolver and yt-channel-resolver, qualifier and registry-writer, yt-video-details-fetcher, source-health-canary, raw-archiver, the `listening-sdk` (adapter contract, envelope, governor client), Supabase Vault, Redpanda.

## 12. Risks and mitigations

- The 100-call cap makes search scarce; a client who wants 50 terms cannot have them. Mitigation: variants joined with `|`, the priority list as an explicit product decision, the web bridge for the rest, a quota extension request once the pilot has audit-ready evidence.
- Search is not exhaustive and recall is not guaranteed. Mitigation: registry channels are also covered by yt-pubsub-receiver and yt-uploads-reconciler; recall is measured in the pilot against their uploads.
- `regionCode=IQ` passes any video viewable in Iraq, so Arabic results from other countries flood the list. Mitigation: the qualifier's Iraqi-signals rule and keyword-matcher's dialect awareness decide what becomes a hit.

## 13. Acceptance criteria

1. With 25 priority terms configured, a daily run makes exactly 25 `search.list` calls when no term needs a second page, and `cost_units_total` rises by 2,500.
2. The run refuses to start without a governor `allow` and records `quota_denied_total` on `deny`.
3. A term whose first page returns 50 items all newer than the cursor triggers at most 2 further pages, each with governor approval.
4. Every item is published to `raw.items` with `idempotency_key = youtube:video:<videoId>`, `route = green`, `vendor = null`, `retention_class = youtube_30d_text`.
5. One `jobs.yt-video-details-fetcher` message of kind `first_sight` is published per batch, listing every video id from the run.
6. Killing the service mid-run and restarting it re-fetches the same window with no missing videos, because the cursor advances only after Redpanda acknowledges the batch.
7. A 403 `quotaExceeded` stops the run within one call, raises the alert and leaves the remaining terms first in order the next day.
8. A term with a malformed query records `last_error` without stopping the other terms.
9. Running the same day twice produces no duplicate rows in ClickHouse `items`, and the provenance statement for a video found by search names `yt-keyword-search`, the green route and the fetch time.

## 14. Open questions

- Which 20 to 30 terms form the launch priority list, and who signs off changes (proposal: client success, with Abdullah's approval for additions that displace an existing term)?
- Does `relevanceLanguage=ku` help or hurt Sorani recall? To be measured in the pilot.
- Should a quota extension be requested after the pilot, and should the daily run align to the quota day boundary used by quota-governor rather than a fixed Baghdad time?
