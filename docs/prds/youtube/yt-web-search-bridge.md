# yt-web-search-bridge

**Platform:** YouTube · **Route:** green · **Lane:** Discover and qualify · **Owner:** Discovery engineer, web-search lane (Node/TypeScript) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

`search.list` costs 100 units, so yt-keyword-search can afford 20 to 30 priority terms a day and no more. Clients will register far more terms than that: product names, executives, campaign slogans, competitor brands, misspellings. The web-search plan already budgets 200 keywords × 9 variants once a day (about 54,000 to 60,000 queries a month) through Perplexity and Mojeek, and both engines index `youtube.com` watch and channel pages. A `site:youtube.com` query on Mojeek costs GBP 0.003 and on Perplexity USD 0.005 per request of up to 5 queries, against 100 API units for one `search.list` call. The bridge turns those cheap web results into YouTube video and channel ids, which yt-video-details-fetcher then confirms and enriches at 1 unit per 50 videos.

Without it, every keyword outside the priority list has no YouTube coverage at all: a client with 80 terms would get YouTube discovery on 20 of them, and the other 60 would only ever surface if a registered channel happened to mention them. The bridge is the long-tail route; it is lower-recall than the API for fresh uploads, and the product says so.

## 2. Objective (the end state this service delivers)

End state: every YouTube keyword rule that is not on the priority list is queried once a day on at least one engine with a `site:youtube.com` query; every YouTube URL in the results is parsed into a video id or channel reference; new video ids go to yt-video-details-fetcher and channel references to yt-channel-resolver, so the long tail feeds keyword-matcher, poster-resolver and the qualifier through the same path as the API search.

Measurable target: 100% of long-tail rules queried every day; URL parse success at or above 99% of YouTube URLs returned; the bridge's monthly query count inside its share of the 60,000-query web-search budget (the share itself to be measured in the pilot); zero YouTube API units spent on search by this service.

## 3. Scope

### In scope

- Daily `site:youtube.com` queries on Mojeek (default) and Perplexity (where the client accepts the minor vendor flag) for keyword rules with `platform = youtube`, `source_type = keyword_rule`, `tier = 2` or `3`.
- Parsing of every YouTube URL form (watch, youtu.be, shorts, live, mobile, channel, handle, legacy custom and user URLs).
- Publishing results to `search.results` and work to `jobs.yt-video-details-fetcher` and `jobs.yt-channel-resolver`.
- Daily deduplication so a video id is not re-sent while its first-sight job is pending.

### Out of scope

- Priority terms (yt-keyword-search); any call to the YouTube Data API (yt-video-details-fetcher, yt-channel-resolver).
- Non-YouTube web results (web-search-perplexity, web-search-mojeek, search-hit-router).
- Keyword matching, qualification and registry writes (keyword-matcher, poster-resolver, qualifier, registry-writer).
- Google search in any form: there is no clean Google route.

## 4. Users and consumers

- yt-video-details-fetcher consumes the first-sight jobs; normalize-item and keyword-matcher turn the resulting items into `item.hits` or `discovery.hits`.
- yt-channel-resolver resolves channel references for poster-resolver and the qualifier.
- search-hit-router reads `search.results`; results marked `handled_by = yt-web-search-bridge` are skipped by it.
- quota-governor meters the web-search budgets; client success configures which engines a client allows.
- Abdullah reads the discovery report split by route (API search versus bridge) to decide which terms deserve promotion to the priority list.

## 5. How it works

### 5.1 Trigger and rotation

- Cadence: one run a day at `YT_BRIDGE_RUN_AT` (default 05:00 Asia/Baghdad, before yt-keyword-search so both feeds reach the details fetcher in one batch window). Every long-tail rule is queried once per enabled engine.
- Order: rules sorted by `last_polled_at` ascending, then by the number of watching clients; if the governor denies budget part-way, the leftover rules run first the next day, never skipped twice in a row.
- Cursor: the engines offer no reliable `publishedAfter`; freshness comes from re-querying daily and discarding video ids already known. The `cursors` row stores the last run time and the hash set of ids sent in the last 7 days.
- Variants: a rule's curated variants form one query per engine when the engine supports the `OR` operator, otherwise one query per variant up to `YT_BRIDGE_MAX_VARIANTS` (default 3), so the query count per rule is bounded.
- Catch-up: a missed day is not replayed; the next run covers it because results are ranked, not time-windowed.
- Backfill: none; a newly added long-tail rule simply joins the next run. Promotion to `tier = 1` moves the rule to yt-keyword-search, which backfills 90 days through the API.
- Rotation to the API: a long-tail rule that produces new video ids on 3 consecutive days is proposed for promotion in the discovery report; the decision stays with client success because the 100-call cap is a zero-sum budget.

### 5.2 Step by step

1. Load long-tail rules and their variants from `sources` and `keywords`; load client engine permissions from `clients`.
2. Ask quota-governor for allowance on `budget_tag = mojeek_search` and `perplexity_search` (queries and requests respectively).
3. Build queries: `site:youtube.com "<term>"` with the variants as above; Perplexity requests carry up to 5 queries each.
4. Call the engines through the shared vendor clients in `listening-sdk` (the same clients web-search-perplexity and web-search-mojeek use).
5. Parse every result URL; extract `videoId` (11 characters from `watch?v=`, `youtu.be/`, `shorts/`, `live/`) or a channel reference (`channel/UC…`, `@handle`, `c/<name>`, `user/<name>`); drop playlists and non-YouTube hosts.
6. Publish each result to `search.results` with the extracted reference and `handled_by = yt-web-search-bridge`.
7. Publish `jobs.yt-video-details-fetcher` (kind `first_sight`, origin `web_bridge`, batches of up to 50 ids) for ids not in the 7-day sent set, and `jobs.yt-channel-resolver` (kind `resolve`, origin `web_bridge`) for channel references.
8. After Redpanda acknowledges, update `cursors`, `service_runs` and the budget counters with the actual request and query counts.

### 5.3 The call it makes

Perplexity Search API (through the shared client; the client owns the exact request shape):

```
POST https://api.perplexity.ai/search
Authorization: Bearer <key from Supabase Vault>
{
  "query": ["site:youtube.com \"فايبر اكس\"", "site:youtube.com \"FiberX\"", ...up to 5],
  "country": "IQ",
  "search_language_filter": ["ar"]
}
```

Cost USD 5 per 1,000 requests; up to 5 queries per request; the customer owns the output. Sorani queries use `ckb` where the engine supports it.

Mojeek Web Search API, Business plan (through the shared client):

```
GET https://www.mojeek.com/search?q=site:youtube.com+"<term>"&fmt=json&rb=IQ&lb=AR&api_key=<key from Supabase Vault>
```

Cost GBP 3 per 1,000 queries; results may be stored. No pagination is requested from either engine: one page of ranked results per query is the design, since a second page costs the same as a new query and adds little for a `site:` search.

### 5.4 What it gets

From both engines: result title, URL, a text snippet, and a date where the engine has one. From the URL the bridge derives the video id or channel reference; from the title and snippet nothing is stored as item text, because the authoritative title and description come from `videos.list`.

It does not get view, like or comment counts, publish time (only the engine's crawl date), comment text, the channel id for a watch URL, or any guarantee of freshness: engine index lag for new uploads is to be measured in the pilot and is expected to run from hours to days.

## 6. Inputs and outputs

### 6.1 Reads

- Control plane: `sources` (long-tail keyword rules), `keywords`, `clients` (engine permissions), `cursors` (rule × `yt-web-search-bridge`), `budgets` through quota-governor, `vendor_keys` through Supabase Vault. No topics are consumed.

### 6.2 Writes

- `search.results`; `jobs.yt-video-details-fetcher`; `jobs.yt-channel-resolver`; `cursors`; `service_runs`.

Example `search.results` message:

```json
{
  "idempotency_key": "web:result:mojeek:9f2c6c1e4d0a7b3e5f8a1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f",
  "platform": "web",
  "platform_hint": "youtube",
  "engine": "mojeek",
  "route": "green",
  "vendor": "mojeek",
  "service": "yt-web-search-bridge",
  "handled_by": "yt-web-search-bridge",
  "source_id": "7b3e5f8a-1c2d-4e4f-9a6b-7c8d9e0f1a2b",
  "query": "site:youtube.com \"فايبر اكس\"",
  "job_id": "ywb-20261006-0117",
  "fetched_at": "2026-10-06T02:03:44Z",
  "cost": { "currency": "GBP", "amount": 0.003 },
  "extracted": { "kind": "video", "video_id": "dQw4w9WgXcQ" },
  "payload": { "title": "...", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "desc": "..." }
}
```

The matching job message to `jobs.yt-video-details-fetcher` carries `kind = first_sight`, `origin = web_bridge`, the `source_id` of the rule and the list of video ids.

### 6.3 State

- `cursors`: per rule, last run time, the 7-day set of sent ids (hashed), `consecutive_errors`.
- Budget counters per engine in `budgets`; per-client engine permission flags in `clients`.
- `service_runs`: rules queried, queries per engine, URLs parsed, parse failures, ids sent.

## 7. Limits, quotas and cost

- Web search: Perplexity USD 5 per 1,000 requests (5 queries a request), about USD 60 a month at 60,000 queries; Mojeek GBP 3 per 1,000 queries, about GBP 180 a month. The bridge's share of the 60,000 monthly queries is set in `budgets` and measured in the pilot; a long-tail list of 200 rules at one Mojeek query each is 6,000 queries a month, GBP 18.
- YouTube Data API: 10,000 units a day by default; `search.list` 100 units (100 calls a day cap); `playlistItems.list`, `videos.list`, `commentThreads.list`, `comments.list`, `channels.list` 1 unit each. The bridge spends no units itself; the ids it sends cost 1 unit per 50 in yt-video-details-fetcher, from the `list` bucket.
- Quota-governor split (planning figures, to be measured in the pilot): about 4,000 to 5,000 units a day for the 1-unit endpoints carrying the 3.0M items a month; the `search` bucket planned at 20 to 30 of its 100-call cap; the rest reserve. The bridge exists so the long tail never touches the `search` bucket.
- Vendor status: Mojeek cleared; Perplexity cleared with a minor flag, client decides; both are green routes (licensed index under our contract), so bridge data is not amber and is not excluded from government contracts, but the engine is named in provenance and government clients default to Mojeek only.
- Developer Policies on the YouTube data the bridge leads to: raw comment text no longer than 30 days (delete or refresh, enforced by yt-text-purger); derived metrics up to 36 months for Analytics & Reporting clients; no aggregation across channels of different owners except under the carve-out; no profiling on protected attributes; audit at any time.

## 8. Failure handling and fallback

- Vendor 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`, after 5 attempts to `dlq.yt-web-search-bridge` with an alert.
- Vendor 401 or 403: mark that engine's key `degraded`, stop its batch, alert; the other engine keeps running, which is the built-in fallback.
- Empty 200: a query with zero results is normal for a rare term; a run where every query on one engine returns zero is counted by source-health-canary (5% in 15 minutes flips that engine `degraded`).
- Parse failure (a `youtube.com` URL the regexes do not recognise): the result is still written to `search.results`, counted in `yt_bridge_parse_failures_total`, and a daily sample goes to `review_queue` so the parser is extended.
- Engine schema change: the raw response is archived by raw-archiver; the normaliser for `search.results` raises `schema_unknown` and parks the batch.
- Budget denied: the run ends, leftover rules lead the next day; no borrowing from the YouTube unit buckets.

## 9. Non-functional requirements

- Throughput: a few hundred queries a day; a run of 200 rules on two engines completes in under 15 minutes with per-vendor concurrency of 2.
- Idempotency: `search.results` keys on engine plus URL hash; first-sight jobs are deduplicated against the 7-day sent set and again by yt-video-details-fetcher, so a replayed run costs at most one extra `videos.list` call per 50 ids.
- Scaling: one replica with a leader lock; no partition lag to scale on.
- Security: vendor keys from Supabase Vault per job; no proxies, no scraping of YouTube pages, no Google; structured JSON logs with `job_id`, `source_id`, `route`, `vendor`; `/healthz`, `/metrics`.
- Provenance: `route = green`, `vendor = mojeek` or `perplexity`, `service`, `fetched_at` on every result; the eventual item's provenance names both the bridge and yt-video-details-fetcher.

## 10. Metrics and alerts

- Standard: `items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total` (vendor money, labelled by currency), `quota_denied_total`, `dlq_total`.
- Service-specific: `yt_bridge_queries_total{engine}`, `yt_bridge_urls_parsed_total{kind}`, `yt_bridge_parse_failures_total`, `yt_bridge_new_ids_total`.
- Alerts: parse failure rate above 1% in a run; an engine `degraded`; a rule unqueried for 2 days; monthly spend above 80% of the bridge's share.

## 11. Dependencies

web-search-perplexity and web-search-mojeek (shared vendor clients, keys, budget tags), quota-governor, yt-video-details-fetcher, yt-channel-resolver, search-hit-router, normalize-item, keyword-matcher, poster-resolver, qualifier, raw-archiver, source-health-canary, `listening-sdk`, Supabase Vault, Redpanda.

## 12. Risks and mitigations

- Engine index lag makes the bridge blind to uploads from the last hours or days. Mitigation: it is positioned as long-tail coverage; fresh coverage comes from registry channels through yt-pubsub-receiver and from the priority terms; lag is measured in the pilot and reported to clients.
- Perplexity's minor flag. Mitigation: Mojeek is the default; Perplexity per client opt-in; the engine is in provenance.
- Variant explosion multiplies queries. Mitigation: `YT_BRIDGE_MAX_VARIANTS` and the per-rule budget; curation prefers `OR` queries.
- URL formats change. Mitigation: parser tests on a fixture of every known form; parse failures sampled daily.

## 13. Acceptance criteria

1. With 120 long-tail rules and Mojeek only, a run issues exactly 120 queries when every rule has one query, and the Mojeek counter in `budgets` rises by 120.
2. A Perplexity run packs 5 queries into one request; 23 queries produce 5 requests and a counter increase of 5.
3. Each of the URL forms `watch?v=`, `youtu.be/`, `shorts/`, `live/`, `m.youtube.com/watch`, `channel/UC…`, `@handle`, `c/<name>`, `user/<name>` is parsed into the right reference in the fixture test; `playlist?list=` is dropped.
4. A video id seen on day 1 is not re-sent to `jobs.yt-video-details-fetcher` on day 2; after 7 days it may be sent again.
5. Every `search.results` message carries `handled_by = yt-web-search-bridge`, and search-hit-router skips it (verified by zero duplicate first-sight jobs from the router).
6. A client marked Mojeek-only never has a Perplexity query issued for its rules (verified from `service_runs` and the vendor log).
7. A 403 from one engine stops only that engine; the other completes the run.
8. The run refuses to start on a governor `deny` and leaves the unqueried rules first in order the next day.
9. The bridge's `cost_units_total` for YouTube API units stays at 0 over a full day of operation.

## 14. Open questions

- Which engine operators are reliable for `OR` and exact-phrase Arabic queries on Mojeek and Perplexity? To be tested in the pilot before variant curation rules are fixed.
- What share of the 60,000 monthly queries does the bridge get once news and general web discovery are budgeted?
- Should Perplexity's domain allow-list be used instead of, or in addition to, the `site:` operator?
- What promotion rule (days with new ids, hits per day) moves a term from the bridge to yt-keyword-search?
