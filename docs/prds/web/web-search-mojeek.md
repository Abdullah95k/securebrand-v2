# web-search-mojeek

**Platform:** Web · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend engineer (Node), discovery lane · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Most of the platforms we monitor have no keyword search we may use: no green search of Facebook posts, no third-party TikTok, no Telegram comments. The open web is how we notice them anyway. A news article, a forum thread or a link on a page mentions a client's name and points to a TikTok creator, a Telegram channel or a Facebook Page we have never seen. web-search-mojeek runs the client's keywords against Mojeek's own independent index every day and puts every result on `search.results`, where search-hit-router turns the links into candidate sources and article URLs.

Mojeek is the baseline web engine for three reasons. It is a UK vendor with its own crawler, so it clears the Israeli-affiliation constraint without the minor flag that Perplexity carries. On the Business plan its results may be stored, which the pipeline needs (only Business and Enterprise plans allow storing; other plans allow a 1-hour cache). And there is no clean Google route: Custom Search is closed to new customers and ends on 1 Jan 2027, and the grounding APIs forbid building an index from links.

Without this service, a client that declines Perplexity has no web search at all, a single outage or terms change at one vendor blinds the whole web leg, and the new-source rate on platforms without keyword search falls.

## 2. Objective (the end state this service delivers)

Every active web keyword rule is searched on Mojeek in its 9 query variants once a day, priority terms twice a day, with `rb=IQ` and `lb=AR`; every result is on `search.results` with full provenance before the job is acknowledged; raw responses are archived; and cost runs at about GBP 180 a month at 60,000 queries.

Targets: 99% of rules run within their interval (24 hours; 12 hours for priority) every day; zero jobs lost; monthly spend at or below the `budgets` cap for `budget_tag = mojeek_search`. Mojeek's recall of Iraqi pages compared with web-search-perplexity, and the share of results that are Iraqi after search-hit-router's classification, are to be measured in the pilot.

## 3. Scope

### In scope

- Scheduling and running the daily rotation for `sources` rows with `platform = web`, `source_type = keyword_rule`, reading forms and variants from `keywords`.
- Generating the 9 query variants through the shared generator in `listening-sdk`.
- Calling the Search API, archiving raw responses to `raw.items`, publishing one `search.results` message per result.
- Cursors, allowance through quota-governor, canary queries, the plan guard, metrics.

### Out of scope

- URL classification, cross-engine deduplication and routing (search-hit-router); fetching pages (news-article-extractor); normalising (normalize-item); confirming matches (keyword-matcher); qualifying posters (qualifier).
- `site_search` jobs: yt-web-search-bridge uses web-search-perplexity in v1 (open question 4).
- Any crawling, account pools or proxying.

## 4. Users and consumers

search-hit-router (sole consumer of `search.results`); raw-archiver (`raw/green/web/<yyyy>/<mm>/<dd>/web-search-mojeek/`); quota-governor; source-health-canary (empty-200 counts from canary queries); ops through `service_runs`; Abdullah for coverage and the per-client engine decision.

## 5. How it works

### 5.1 Trigger and rotation

- **Unit of rotation: the keyword rule.** Each active `keywords` row has one `sources` row (`platform = web`, `source_type = keyword_rule`) created by registry-writer and a `cursors` row for `service = web-search-mojeek`. Rules are not reach-tiered: `tier = 1` means priority (a client's priority list) and runs every 12 hours; `tier = 2` or `3` means the standard run every 24 hours. A rule runs until its client removes it; dormant and retired do not apply.
- **Scheduler.** One leader replica (Postgres advisory lock) scans `sources` for rules with `next_poll_at <= now()` and `health != blocked`, orders them by `next_poll_at` then by tier, and emits one job per rule to `jobs.web-search-mojeek`, partitioned by the rule's `source_id`, so a rule is never worked twice at once and none is skipped twice in a row. `next_poll_at` is set from the START of the run (fixed cadence, no drift).
- **Volume and pacing.** 200 keywords × 9 variants = 1,800 queries a day, about 54,000 a month; the second daily run of priority terms takes the month to about 60,000. That is about 2,000 queries a day, one every 43 seconds on average; runs are spread across the day, with the pacing inside a job set by quota-governor's `wait-until`.
- **Reading the keyword set.** At the start of every job, never from a cache, so a client's edit is honoured on the next run: the `keywords` row (Latin, Arabic and Sorani forms, listed misspellings, context and intent terms, `client_ids[]`, priority flag). Mojeek is cleared under constraint 1, so no per-client opt-out is expected; rules whose clients declined Perplexity are served by this engine alone.
- **Arabic and Kurdish variants.** The 9 variants come from the same shared generator, in the same slot order, as web-search-perplexity, so the two engines can be compared slot by slot; this PRD does not redefine them. Arabic variants run with `lb=AR`. Sorani variants also run under `lb=AR` until the pilot confirms a Kurdish language boost.
- **Catch-up.** If the most overdue rule is more than one interval late, the most stale rules go first and `rotation_behind` is raised; missed runs are not repeated with extra queries.
- **Backfill.** Web search has no history cursor. The first run of a new rule sends the nine variants as they are, so the engine returns its best results regardless of age, which stands in for the 90-day backfill. v1 uses no date filter on later runs either; search-hit-router's deduplication absorbs repeated URLs (date parameters are open question 1).
- **Canary.** Every run includes one query from `canary_targets` (platform web) known to return results; an empty answer is an empty 200 for source-health-canary.
- **Plan guard.** Before each job the service reads the plan of the active key from `vendor_keys`. Only Business and Enterprise allow storing results; on any other plan no query is sent and `plan_not_storable` is raised, because the pipeline archives and republishes every result.

### 5.2 Step by step

1. Read the job; load the rule, its `keywords` row and the cursor; run the plan guard.
2. Ask quota-governor for allowance under `budget_tag = mojeek_search` for 9 queries plus the canary; `wait-until` requeues the job for that time; `deny` counts `quota_denied_total` and keeps `next_poll_at`.
3. Build the 9 variants with the shared generator.
4. Call the API once per query, paced; write each full response body to `raw.items` as the archive-only record kind `search_response`, which normalize-item skips (ADR-0008, ADR-0070).
5. Parse the results; compute `canonical_url` and `canonical_url_hash` with the shared canonicaliser; publish one `search.results` message per result.
6. On Redpanda's acknowledgement, advance the cursor, update `last_polled_at` and `next_poll_at`, report `cost_units = 9` to the governor, write `service_runs`.

### 5.3 The call it makes

```
GET <Mojeek Web Search API endpoint, per the Business-plan documentation>
  ?q=<one query variant>
  &rb=IQ        region boost: Iraq
  &lb=AR        language boost: Arabic
  &<API key, response format, number of results, offset>
```

Auth: the Mojeek API key from `vendor_keys` through Supabase Vault. Parameter names, the number of results per query, depth beyond the first page, whether a request can carry more than one query, and rate limits are to be confirmed in the pilot; v1 reads the first page of each query only. `rb` and `lb` are boosts, not filters: results from outside Iraq or in other languages still appear.

### 5.4 What it gets

Per result: title, URL, the engine's description of the page as snippet, rank, and a date where the engine supplies one (to be confirmed in the pilot). Titles of Instagram, X, YouTube and TikTok pages usually carry the account name, which search-hit-router uses as a handle hint.

It does not get page text beyond the snippet, author identity, engagement counts, a total result count, a Kurdish-only filter, anything behind a login wall, or a guarantee that a result is Iraqi: the router verifies that.

## 6. Inputs and outputs

### 6.1 Reads

- Queue `jobs.web-search-mojeek` (kind `rotation`).
- Control plane: `sources`, `keywords`, `clients`, `cursors`, `budgets` through quota-governor, `vendor_keys` (key and plan), `canary_targets`, `service_runs`.

### 6.2 Writes

- `raw.items`: one record per API response; envelope `service`, `route = green`, `vendor = mojeek`, `platform = web`, `source_id` (the rule), `job_id`, `job_kind`, `kind = search_response` (ADR-0070), `fetched_at`, `api_version`, `raw_ref`; partition key `source_id` (ADR-0004).
- `search.results`, same shape as web-search-perplexity, partition key `canonical_url_hash`:

```json
{
  "schema": "search.results/v1",
  "message_id": "01M47P1SFRP93VMPD2QC6WP5HA",
  "produced_at": "2026-10-06T04:02:51Z",
  "service": "web-search-mojeek", "engine": "mojeek", "route": "green", "vendor": "mojeek",
  "job_id": "01M47P07P0M1V49VADF6SRK5BM", "job_kind": "rotation", "attempt": 1,
  "keyword_rule_id": "7d2b0c4e-1f3a-4b5c-8d6e-9f0a1b2c3d4e", "keyword_id": "0cd402b6-9015-45f8-86b4-d90cc086d320", "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
  "query": {"text": "\"فايبر اكس\" العراق", "variant": "arabic_context", "lang": "ar", "country": "IQ", "request_id": null},
  "result": {"rank": 5, "title": "فايبر اكس تطلق باقة جديدة في واسط", "url": "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit?utm_source=fb", "snippet": "أعلنت شركة فايبر اكس عن …", "date": "2026-10-05", "last_updated": null},
  "canonical_url": "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit",
  "canonical_url_hash": "sha256:4be07a…",
  "fetched_at": "2026-10-06T04:02:50Z",
  "raw_ref": "raw/green/web/2026/10/06/web-search-mojeek/0007.jsonl.zst#41",
  "retention_class": "news_excerpt"
}
```

Ids in this example follow ADR-0002 and ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

`country` records the region boost sent (`rb`), `lang` the language boost (`lb`); `request_id` is the engine's id when it returns one, else null. Also `service_runs` and `dlq.web-search-mojeek` after 5 failed attempts.

### 6.3 State

`cursors.cursor` = start time of the last successful run, plus `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`; `budgets` counters (queries and GBP, per month); `vendor_keys.plan`.

## 7. Limits, quotas and cost

- Mojeek Web Search API, Business plan: GBP 3 per 1,000 queries. The standard run alone (54,000 queries a month) is GBP 162 a month; with priority second runs, about 60,000 queries, about GBP 180 a month (derived from the rate).
- Budget tag `mojeek_search`; the cap is held in GBP in `budgets`; on `deny` for the month rules keep `next_poll_at`, `quota_denied_total` increments, and the admin page tells the client that web coverage is paused for budget.
- Storage rights: results may be stored only on Business and Enterprise plans; on others they may be cached for 1 hour, which is why the plan guard exists.
- API rate limits: to be confirmed in the pilot; the steady load is about 83 queries an hour.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, then requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.web-search-mojeek` and an alert fires.
- HTTP 401 or 403: the key is marked `degraded`, the run stops, an alert fires; no second key, account or IP is tried.
- Empty 200 on the canary query: counted per route; above 5% in 15 minutes source-health-canary sets the web route `degraded`; open-web recall then rests on web-search-perplexity, which runs the same rotation independently, so no `fallback_on` flag is needed.
- Unknown response shape: the raw body is archived, the job raises `schema_unknown`, parks the batch in `review_queue` and does not advance the cursor.
- A boost value the API rejects: the query is retried once with `lb=AR` only and the rejection is counted.
- Plan guard fails: no query is sent; `plan_not_storable` pages ops.

## 9. Non-functional requirements

- Throughput: about 2,000 queries a day, one every 43 seconds when spread; one replica suffices, a second for failover; scaling on queue lag.
- Latency: a rule's results reach `search.results` within its run; latency to a `discovery.hits` message is set by search-hit-router and poster-resolver and is to be measured in the pilot.
- Idempotency: `message_id = sr:mojeek:<canonical_url_hash>:<job_id>`, so a replayed job republishes identical messages that search-hit-router absorbs; the cursor advances only after acknowledgement.
- Security: key in Supabase Vault; logs carry `job_id`, `source_id`, `route`, `vendor`, `keyword_id`, never the query text; `/healthz` and `/metrics`; Node (TypeScript); generator and canonicaliser in `listening-sdk`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `cost_units_total` (queries), `quota_denied_total`, `dlq_total`, plus `queries_total{variant}`, `results_per_query`, `variant_yield{variant}` (results that search-hit-router classifies as Iraqi), `empty_canary_total`. Alerts: `rotation_behind`, `key_degraded`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`, `plan_not_storable`. SLO: rotation lag below one interval for 99% of rules per day.

## 11. Dependencies

`listening-sdk`, quota-governor, raw-archiver, search-hit-router (downstream), registry-writer (keyword-rule rows), source-health-canary, web-search-perplexity (parallel engine), web-gdelt-poller (complement), Redpanda, Supabase Postgres and Vault, a Mojeek Business-plan contract.

## 12. Risks and mitigations

- Mojeek's independent index is smaller than the big engines', and its Iraqi and Arabic coverage is unmeasured: the pilot compares recall with web-search-perplexity per variant, and the two engines plus web-gdelt-poller and web-commoncrawl-scanner are designed to complement one another.
- Boosts are not filters: search-hit-router's Iraqi-signal check and the per-variant yield metric retire variants that never produce Iraqi results.
- A plan change or contract lapse would make stored results a terms breach: the plan guard blocks queries on a non-storable plan, and the contract text is checked before the first production run.
- Brand names that are common words inflate results: variants are quoted phrases, and keyword-matcher confirms the match on the fetched page before anything counts as a mention.
- Price change: the governor cap stops spend; the engine is one adapter behind the `listening-sdk` contract.

## 13. Acceptance criteria

1. A rule with Latin, Arabic and Sorani forms produces exactly 9 queries, in the generator's slot order and identical to the order web-search-perplexity uses, identical on two consecutive runs.
2. Every request in the recorded request log carries `rb=IQ` and `lb=AR` and one query.
3. A `tier = 1` rule runs twice within 24 hours and a `tier = 3` rule once; `next_poll_at` equals the run start plus the interval, even when the run took 20 minutes.
4. Every result in a recorded response produces one `search.results` message with the same keys as web-search-perplexity's, `engine = mojeek`, `retention_class = news_excerpt`, partitioned by `canonical_url_hash`.
5. Replaying a completed job republishes identical `message_id` values and commits no second batch to `raw.items`; the cursor does not advance when the produce fails.
6. With a non-storable plan in `vendor_keys`, no query is sent and `plan_not_storable` fires.
7. A 429 is retried with backoff starting at 30 s; the fifth failed attempt lands in `dlq.web-search-mojeek` with an alert (ADR-0057); a 401 stops the run, marks the key `degraded` and sends no second request.
8. An edit to a rule's keyword forms is used by its next run without a restart.
9. A canary query that returns nothing increments the empty-200 counter for the web route.
10. Over a 30-day pilot month with 200 rules, queries are between 54,000 and 60,000, spend is at or below the governor cap and 99% of rules met their interval every day.

## 14. Open questions

1. API specifics: endpoint, parameter names, results per request, a date filter, `site:` support, rate limits, and whether one request can carry several queries. The pilot answers them.
2. Does Mojeek offer a language boost for Sorani? Until then Sorani variants run under `lb=AR`.
3. Should the priority second run use all 9 variants or the shorter set that web-search-perplexity considers? The two engines should decide together.
4. Should `site_search` jobs from yt-web-search-bridge also be served here, once `site:` is confirmed?
