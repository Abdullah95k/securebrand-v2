# web-search-perplexity

**Platform:** Web · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend engineer (Node), discovery lane · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The product promises a brand, a company or a ministry that it hears every public mention of itself in Iraq. The per-platform services only reach what a green route exposes: registered Facebook Pages, Instagram hashtags, X search, YouTube channels, Telegram channels our bot sits in, and the roughly 500 news domains we crawl. Everything else lives on the open web: forums, blogs, marketplaces, ministry and university pages, PDF notices, Kurdish portals, and the public Instagram, X, YouTube, TikTok and Telegram pages that web engines index but no platform API lets us search by keyword. There is no green keyword search of Facebook posts, no green route to third-party TikTok content and no green search of Telegram; an index that has already crawled those pages is the only green bridge to them. web-search-perplexity is one of the two engines that give the product that bridge; web-search-mojeek is the other.

Why this index and not Google: there is no clean Google route. Custom Search is closed to new customers and ends on 1 Jan 2027; Gemini and Vertex grounding forbid building an index from the links they return; Google News RSS and Alerts sit behind robots.txt. Brave and Exa forbid storing results; Kagi resells scraped Google; Yandex is Russian with sanctions optics; Tavily and Webz.io fall under constraint 1. The Perplexity Search API is a contracted index whose output the customer owns, so results may be stored and shown to clients, and it filters by `country` and `search_language_filter`, which fits the Iraq-and-Arabic scope directly.

Without it the product loses the open-web leg of discovery and its largest green source of candidate posters on platforms without keyword search: a new TikTok creator or Telegram channel complaining about a client stays invisible until someone pastes its link. Perplexity carries a minor flag under constraint 1 (client decides); a client that declines it is still covered by web-search-mojeek.

## 2. Objective (the end state this service delivers)

Every active web keyword rule is searched on the Perplexity Search API in its 9 query variants once a day, priority terms twice a day, with `country` IQ and the Arabic language filter (Kurdish where supported); every result is on `search.results` with full provenance before the job is acknowledged; raw responses are archived; cost runs at about USD 60 a month at 60,000 queries.

Targets: 99% of keyword rules run within their interval (24 hours; 12 hours for priority) every day, the rotation SLO applied to keyword rules; zero jobs lost; monthly spend at or below the `budgets` cap for `budget_tag = perplexity_search`. The share of new registered sources whose first hit came from this engine, and the share of results that are Iraqi after search-hit-router's classification, are to be measured in the pilot.

## 3. Scope

### In scope
- Scheduling and running the daily rotation for `sources` rows with `platform = web`, `source_type = keyword_rule`, reading forms and variants from `keywords`.
- Generating the 9 query variants through the shared generator in `listening-sdk`.
- Calling the Search API, archiving raw responses to `raw.items`, publishing one `search.results` message per result.
- `site_search` jobs from other services (first user: yt-web-search-bridge, which restricts a query to `youtube.com` and pays from its own `budget_tag`).
- Cursors, allowance through quota-governor, canary queries, metrics.

### Out of scope
- URL classification, cross-engine deduplication and routing (search-hit-router); fetching pages (news-article-extractor); normalising (normalize-item); confirming matches (keyword-matcher); qualifying posters (qualifier).
- Perplexity's answer and chat endpoints: the product buys search results, never generated text.
- Any crawling, account pools or proxying.

## 4. Users and consumers

search-hit-router (sole consumer of `search.results`); raw-archiver (`raw/green/web/<yyyy>/<mm>/<dd>/web-search-perplexity/`); quota-governor; source-health-canary (empty-200 counts from canary queries); yt-web-search-bridge (`site_search` producer); ops through `service_runs`; Abdullah for coverage and the per-client Perplexity decision.

## 5. How it works

### 5.1 Trigger and rotation

- Unit of rotation: the keyword rule. Each active `keywords` row has one `sources` row (`platform = web`, `source_type = keyword_rule`) created by registry-writer and a `cursors` row for `service = web-search-perplexity`. Keyword rules are not reach-tiered: `tier = 1` means priority (a client's priority list) and runs every 12 hours; `tier = 2` or `3` means the standard run every 24 hours. Dormant and retired do not apply; a rule runs until its client removes it.
- Scheduler: one leader replica (Postgres advisory lock) scans `sources` for rules with `next_poll_at <= now()` and `health != blocked`, orders them by `next_poll_at` then by tier, and emits one job per rule to `jobs.web-search-perplexity`, partitioned by the rule's `source_id`, so a rule is never worked twice at once. `next_poll_at` is set from the start of the run (fixed cadence, no drift). Runs are spread across the day: a steady 400 requests a day rather than a burst.
- Volume: 200 keywords × 9 variants = 1,800 queries a day, about 54,000 a month; the second run for priority terms takes the month to about 60,000 queries, about 12,000 requests at 5 queries a request.
- Reading the keyword set: at the start of every job, never from a cache, so a client's edit is honoured on the next run. The job reads the `keywords` row (Latin, Arabic and Sorani forms, listed misspellings, context and intent terms, `client_ids[]`, priority flag) and the `clients` rows for the Perplexity opt-out under constraint 1. A rule whose clients have all declined Perplexity is skipped here and served by web-search-mojeek alone.
- Variants, in a fixed slot order so results compare across engines and days: (1) `latin_exact`, the Latin form quoted; (2) `latin_context`, plus Iraq or the client's governorate; (3) `arabic_exact`; (4) `arabic_alt_spelling`, the first alternative from the orthography rules (hamza and alef forms, taa marbuta and haa, yaa and alef maqsura) or the client's listed misspelling; (5) `arabic_joined_or_split`, the token-boundary variant (فايبراكس for فايبر اكس); (6) `arabic_context`, plus العراق or the governorate; (7) `arabic_intent`, plus the client's intent term (default أخبار); (8) `sorani_exact` in Kurdish orthography (ە ێ ۆ ڤ ک گ); (9) `sorani_arabic_keyboard`, the Sorani form as typed on an Arabic keyboard (ە→ه, ێ→ي, ۆ→و, ک→ك, ی→ي). A missing Arabic or Sorani form is generated from the transliteration table and flagged for the client to confirm.
- Catch-up: if the most overdue rule is more than one interval late, the most stale rules go first and `rotation_behind` is raised; missed runs are not repeated with extra queries.
- Backfill: web search has no history cursor. The first run of a new rule sends the nine variants without a date filter, so the engine returns its best results regardless of age, which stands in for the 90-day backfill. Later runs set `search_after_date_filter` to the day of the last successful run.
- Canary: every run includes one query from `canary_targets` (platform web) known to return results; an empty answer is an empty 200 for source-health-canary.

### 5.2 Step by step

1. Read the job; load the rule, its `keywords` row, the opt-outs and the cursor.
2. Ask quota-governor for allowance under `budget_tag = perplexity_search` (or the tag a `site_search` job carries) for 2 requests; `wait-until` requeues the job for that time; `deny` counts `quota_denied_total` and keeps `next_poll_at`.
3. Build the 9 variants and pack them into 2 requests of 5 and 4 queries, both for the same keyword, so attribution is safe at keyword level even if the API merges results across queries.
4. Call the API; write each full response body to `raw.items` as the archive-only record kind `search_response`, which normalize-item skips (ADR-0008, ADR-0070).
5. Parse the results; compute `canonical_url` and `canonical_url_hash` with the shared canonicaliser; publish one `search.results` message per result.
6. On Redpanda's acknowledgement, advance the cursor, update `last_polled_at` and `next_poll_at`, report `cost_units = 2` to the governor, write `service_runs`.

### 5.3 The call it makes

`POST https://api.perplexity.ai/search`, header `Authorization: Bearer <key>`, key read from `vendor_keys` through Supabase Vault. Request for the first five variants of a rule:

```json
{
  "query": ["\"FiberX\"", "\"FiberX\" العراق", "\"فايبر اكس\"", "\"فايبر إكس\"", "\"فايبراكس\""],
  "country": "IQ",
  "search_language_filter": ["ar"],
  "max_results": "<the API's documented maximum per query>",
  "max_tokens_per_page": "<set in the pilot>",
  "search_after_date_filter": "10/05/2026"
}
```

The second request carries variants 6 to 9 with `search_language_filter: ["ar", "ckb"]` where the API accepts `ckb`; the service probes `ckb` once at start-up with the canary query and records `ckb_supported` in `service_runs`; when it is rejected the Sorani variants go out under `["ar"]` with `country: "IQ"`. `search_domain_filter` is used only for `site_search` jobs (`["youtube.com"]` for yt-web-search-bridge). `query` is a string or an array of up to 5 strings; `search_language_filter` takes ISO 639-1 codes; date filters take MM/DD/YYYY. Result fields read from each entry: `title`, `url`, `snippet`, `date`, `last_updated`. There is no pagination: one request returns one ranked list.

### 5.4 What it gets

Per result: title, URL, a snippet extracted from the page (not engine prose), publication and last-updated dates where the engine has them, and the response `id` kept as `request_id`. Titles of Instagram, X, YouTube and TikTok pages usually carry the account name, which search-hit-router uses as a handle hint.

It does not get page text beyond the snippet, author identity, engagement counts, a total result count, per-query grouping guaranteed by the documentation (hence packing per keyword), Kurdish filtering until `ckb` is confirmed, anything behind a login wall, or a guarantee that a result is Iraqi: `country` is a preference the router verifies.

## 6. Inputs and outputs

### 6.1 Reads
- Queue `jobs.web-search-perplexity` (kinds `rotation`, `site_search`).
- Control plane: `sources`, `keywords`, `clients` (opt-out, government flag), `cursors`, `budgets` through quota-governor, `vendor_keys`, `canary_targets`, `service_runs`.

### 6.2 Writes
- `raw.items`: one record per API response; envelope `service`, `route = green`, `vendor = perplexity`, `platform = web`, `source_id` (the rule), `job_id`, `job_kind`, `kind = search_response` (ADR-0070), `fetched_at`, `api_version`, `raw_ref`; partition key `web:<source_id>`.
- `search.results`, partition key `canonical_url_hash`, so every engine's sighting of one URL lands on one partition for search-hit-router:

```json
{
  "schema": "search.results/v1",
  "message_id": "sr:perplexity:sha256:9c1e4b…:wsp-20261006-0117",
  "produced_at": "2026-10-06T03:14:09Z",
  "service": "web-search-perplexity", "engine": "perplexity", "route": "green", "vendor": "perplexity",
  "job_id": "wsp-20261006-0117", "job_kind": "rotation", "attempt": 1,
  "keyword_rule_id": "7d2b0c4e-1f3a-4b5c-8d6e-9f0a1b2c3d4e", "keyword_id": "kw_0412", "client_ids": ["cl_17"],
  "query": {"text": "\"فايبر اكس\" العراق", "variant": "arabic_context", "lang": "ar", "country": "IQ", "request_id": "pplx-01J9…"},
  "result": {"rank": 3, "title": "فايبر اكس تطلق باقة جديدة في واسط", "url": "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit?utm_source=fb", "snippet": "أعلنت شركة فايبر اكس عن …", "date": "2026-10-05", "last_updated": "2026-10-05"},
  "canonical_url": "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit",
  "canonical_url_hash": "sha256:9c1e4b…",
  "fetched_at": "2026-10-06T03:14:08Z",
  "raw_ref": "raw/green/web/2026/10/06/web-search-perplexity/0003.jsonl.zst#17",
  "retention_class": "news_excerpt"
}
```

- `dlq.web-search-perplexity`; `service_runs`.

### 6.3 State
`cursors` per rule (`last_run_started_at`, `last_success_at`, `results_last_run`, `last_error`, `consecutive_errors`); `sources.next_poll_at` and `last_polled_at`; `service_runs` (`ckb_supported`, lag, spend this month); governor counters in `budgets`; the leader lock.

## 7. Limits, quotas and cost

- Price: USD 5 per 1,000 requests, up to 5 queries a request. 200 rules × 2 requests = 400 requests a day, about 12,000 a month: about USD 60 a month at 60,000 queries, priority run included. The governor cap for `perplexity_search` starts at USD 60 a month and is raised by ops when the priority list grows; `site_search` jobs are charged to the requesting service's tag.
- API rate limits: not in the fact sheet; to be measured in the pilot and recorded in `budgets` as a per-minute ceiling.
- Terms: the customer owns the output, so results are stored, normalised and shown to clients; US export screening applies to the account holder and end users, and Iraq is not embargoed, so Iraqi clients, ministries included, are permitted. The minor flag under constraint 1 is a client decision recorded in `clients`.
- Not used: Brave and Exa, because they forbid storing results; Google, because no clean route exists.
- Retention: results are excerpt and metadata only (`news_excerpt`).

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, then requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.web-search-perplexity` and an alert fires.
- HTTP 401 or 403: the key is marked `degraded`, the run stops, an alert fires; no second key, account or IP is tried.
- Empty 200 on the canary query: counted per route; above 5% in 15 minutes source-health-canary sets the web route `degraded`; open-web recall then rests on web-search-mojeek, which runs the same rotation independently, so no `fallback_on` flag is needed.
- Unknown response shape: the raw body is archived, the job raises `schema_unknown`, parks the batch in `review_queue` and does not advance the cursor.
- `ckb` rejected mid-run: retried once under `["ar"]`; `ckb_supported` set to false.
- Governor `deny` for the month: rules keep `next_poll_at`, `quota_denied_total` increments, and the admin page tells the client that web coverage is paused for budget.

## 9. Non-functional requirements

- Throughput: 400 requests a day, about 2 a minute when spread; one replica suffices, a second for failover; scaling on queue lag.
- Latency: a rule's results reach `search.results` within its run; latency to a `discovery.hits` message is set by search-hit-router and poster-resolver and is to be measured in the pilot.
- Idempotency: `message_id = sr:perplexity:<canonical_url_hash>:<job_id>`, so a replayed job republishes identical messages that search-hit-router's dedup absorbs; the cursor advances only after acknowledgement.
- Security: key in Supabase Vault; logs carry `job_id`, `source_id`, `route`, `vendor`, `keyword_id`, never the query text; `/healthz` and `/metrics`; Node (TypeScript), generator and canonicaliser in `listening-sdk`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total` (first sightings as reported back by search-hit-router), `jobs_total{status,kind}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, `results_per_query`, `empty_canary_total`, `ckb_supported`. Alerts: `rotation_behind`; any DLQ entry; spend above 80% of the monthly cap before day 24; `results_per_query` below half its 7-day median for a day; canary empty-200 above 5% in 15 minutes.

## 11. Dependencies

`listening-sdk`, quota-governor, raw-archiver, search-hit-router (downstream), registry-writer (keyword-rule rows), source-health-canary, web-search-mojeek (parallel engine), yt-web-search-bridge, Redpanda, Supabase Postgres and Vault, the Perplexity Search API contract and export-screening clearance.

## 12. Risks and mitigations

- A large client declines Perplexity under constraint 1: per-rule opt-out, Mojeek covers; the pilot measures each engine's recall so the decision is informed.
- The index favours non-Iraqi pages for Latin variants: `country` IQ and the Arabic filter on every request; the router's Iraqi-signal check and a per-variant yield metric retire variants that never produce Iraqi results.
- Orthographic variants of brand names that are common words inflate results: variants are quoted phrases, and keyword-matcher confirms the match on the fetched page before anything counts as a mention.
- Price or terms change: the governor cap stops spend; the engine is one adapter behind the `listening-sdk` contract, so a replacement is a new adapter, not a redesign.
- The date filter hides pages without dates: the pilot compares one week with and without it.

## 13. Acceptance criteria

1. A rule with Latin, Arabic and Sorani forms produces exactly 9 queries in the slot order of 5.1, identical on two consecutive runs.
2. A rule produces exactly 2 API requests with `country: "IQ"` and `search_language_filter` containing `"ar"`, verified in the recorded request log.
3. A `tier = 1` rule runs twice within 24 hours and a `tier = 3` rule once; `next_poll_at` equals the run start plus the interval.
4. Every result in a recorded response produces one `search.results` message with `canonical_url_hash`, `keyword_rule_id`, `client_ids`, `raw_ref` and `retention_class = news_excerpt`, partitioned by `canonical_url_hash`.
5. Replaying a completed job republishes messages with identical `message_id` values and commits no second batch to `raw.items`.
6. A rule whose only client has opted out of Perplexity produces no job here and still runs on web-search-mojeek.
7. A 429 is retried with backoff starting at 30 s; the sixth failure lands in `dlq.web-search-perplexity` with an alert.
8. A 401 stops the run, marks the key `degraded` and fires an alert without a second request.
9. A `site_search` job from yt-web-search-bridge is charged to the job's `budget_tag`, not to `perplexity_search`, verified in `budgets`.
10. Over a 30-day pilot month with 200 rules, `cost_units_total` is at or below the governor cap and 99% of rules met their interval every day.

## 14. Open questions

1. Does the Search API accept `ckb`? The start-up probe answers it; until then Sorani variants run under `ar`.
2. Should the priority second run use all 9 variants or a shorter set (1, 3, 6, 8) to hold the month at 60,000 queries if the priority list grows?
3. `search_after_date_filter` on daily runs or no filter: decided after the one-week pilot comparison.
4. Column names in `keywords` for forms, misspellings, context and intent terms belong to the control-plane schema; this PRD names the attributes.
5. Does normalize-item treat `kind_hint = search_response` as archive-only, or does raw-archiver take those records on a separate path?
