# web-gdelt-poller

**Platform:** Web · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend engineer (Node), discovery lane · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

GDELT is a free, open index of news published around the world, and its DOC 2.0 API lets us ask it, with a keyword query, which articles mentioned a client in a given window. web-gdelt-poller asks that question every hour for every keyword rule and puts each article on `search.results`, where search-hit-router decides what to do with it.

It is a complement, not a main engine, and the PRD says so up front: GDELT's Arabic coverage is thin and Iraqi outlets are nearly absent. What it adds is different from what web-search-perplexity and web-search-mojeek add. It is hourly where they are daily; it is free where they cost USD or GBP per thousand queries; it is a third independent index; and it sees regional and international outlets that write about a client or a ministry (the Gulf, the wider Arab press, international wires), and occasionally a new outlet the registry has not met. GDELT permits governmental use, so it is the one web source with no condition attached to a government contract.

Without it, the web leg has no hourly view, no free source to fall back on if a paid engine changes terms or price, and no systematic cross-border coverage signal. With it, the cost is one small service and a pacing rule.

## 2. Objective (the end state this service delivers)

Every active web keyword rule is queried on GDELT DOC 2.0 every hour, never faster than one request per 5 seconds across the whole cluster, and every article found is on `search.results` with full provenance before the job is acknowledged.

Targets: rotation lag below one hour for 99% of rules per day; zero jobs lost; zero requests inside the 5-second spacing. The share of results from Iraqi hosts and the share of domains that neither Perplexity nor Mojeek returned are to be measured in the pilot; they decide whether GDELT stays on per client.

## 3. Scope

### In scope

- Hourly rotation of `sources` rows with `platform = web`, `source_type = keyword_rule`; one combined keyword query per rule, built from its `keywords` row.
- Pacing every request through quota-governor; time windows from the cursor; splitting saturated responses.
- Archiving raw responses to `raw.items` and publishing one `search.results` message per article; canary queries; metrics.

### Out of scope

- URL classification, deduplication across engines and routing (search-hit-router); fetching article pages (news-article-extractor, through `article.urls`); normalising (normalize-item); confirming matches (keyword-matcher).
- GDELT's other datasets and APIs, and its tone and theme scores: the product runs its own analysis services.
- Crawling, account pools, proxies.

## 4. Users and consumers

search-hit-router (consumer of `search.results`); raw-archiver (`raw/green/web/<yyyy>/<mm>/<dd>/web-gdelt-poller/`); quota-governor (pacing); source-health-canary (canary empties); ops through `service_runs`; Abdullah for the per-client keep-or-drop decision after the pilot.

## 5. How it works

### 5.1 Trigger and rotation

- **Unit and cadence.** The keyword rule, as in web-search-perplexity: one `sources` row per rule (`platform = web`, `source_type = keyword_rule`) and a `cursors` row for `service = web-gdelt-poller`. Every active rule, priority or standard, runs every hour; rules are not reach-tiered and a rule runs until its client removes it. `next_poll_at = run_started_at + 1 h`, from the START of the run, so cadence is fixed.
- **Scheduler.** One leader replica (Postgres advisory lock) scans for rules with `next_poll_at <= now()` and `health != blocked`, orders them by `next_poll_at` then tier, and emits one job per rule to `jobs.web-gdelt-poller`, partitioned by `source_id`, so a rule is never worked twice at once and none is skipped twice in a row.
- **Pacing.** One request every 5 seconds allows at most 720 requests an hour. Every request first asks quota-governor for allowance under `gdelt_doc_api`; the governor answers with a `wait-until` that keeps request starts at least 5 seconds apart across all replicas. No replica calls GDELT without it.
- **Capacity.** 200 rules at one request each is 200 requests, about 17 minutes of every hour (derived: 200 × 5 s). If the pilot shows that a combined query joining a rule's forms with OR is truncated or misread, a rule is split by language form (Latin, Arabic, Sorani), up to 600 requests, about 50 minutes of the hour. The 9-variant generator used by the paid engines is not used here: 200 × 9 = 1,800 requests would need 2.5 hours at this rate. If a scan's plan exceeds 720 requests in the hour, priority rules keep their hourly slot, the others go most-stale-first inside the capacity, each at least every 24 hours, and `rotation_behind` is raised.
- **Reading the keyword set.** At the start of every job, never from a cache: Latin and Arabic forms always, Sorani where GDELT covers it (to be confirmed in the pilot).
- **Time window.** Each query covers the time since the last successful run's start plus an overlap for GDELT's own update delay (overlap and update cadence to be confirmed in the pilot). Duplicates from the overlap are absorbed by search-hit-router.
- **Catch-up.** When the most overdue rule is more than one interval late, the most stale go first and `rotation_behind` is raised. Missed hours are not re-queried one by one: the next query's window widens to cover the gap.
- **Backfill.** The first run of a new rule asks for the longest window the API accepts, up to 90 days, which stands in for the 90-day backfill (the API's maximum span is to be confirmed in the pilot).
- **Canary.** Every cycle includes one query from `canary_targets` (platform web) known to return articles. An empty answer is normal for most Iraqi rules, so only the canary counts as an empty 200.

### 5.2 Step by step

1. Read the job; load the rule, its `keywords` row and the cursor.
2. Build the query (the rule's forms in one parenthesised OR group) and the time window.
3. Ask quota-governor for allowance under `gdelt_doc_api` for 1 request; `wait-until` holds the job until then; `deny` counts `quota_denied_total` and keeps `next_poll_at`.
4. Call the API. A body that is not JSON is `query_rejected`, not an empty result.
5. Write the full response to `raw.items` as the archive-only record kind `search_response`, which normalize-item skips (ADR-0008, ADR-0070).
6. If the response holds the maximum record count it is saturated: split the window in two and query both halves.
7. Parse the articles; compute `canonical_url` and `canonical_url_hash` with the shared canonicaliser; publish one `search.results` message per article.
8. On Redpanda's acknowledgement, advance the cursor to the run's start, update `last_polled_at` and `next_poll_at`, report `cost_units = 1` per request to the governor, write `service_runs`.

### 5.3 The call it makes

```
GET <GDELT DOC 2.0 API endpoint>
  query = (“FiberX” OR “فايبر اكس” OR “فايبر إكس”)     the rule's forms joined with OR
  <article-list mode, JSON format, time window, maximum records, newest first>
```

No key is needed. Rate: 1 request per 5 seconds. Expected parameter names (`query`, `mode`, `format`, `startdatetime` and `enddatetime` or `timespan`, `maxrecords`, `sort`), the maximum records per response, the minimum phrase length, the query-length limit, the maximum time span and how a bad query is reported are to be confirmed in the pilot. There is no pagination in article-list mode as far as we know (to be confirmed); the saturation split in 5.2 replaces it. No source-language or source-country filter is applied in v1: coverage of Iraq is thin, and a country filter would discard the regional coverage that is this engine's value; search-hit-router judges what is Iraqi.

### 5.4 What it gets

Expected per article (to be confirmed in the pilot): URL, title, the time GDELT saw it, domain, language, source country. Illustrative:

```json
{"url": "https://www.example-gulf-news.com/2026/10/05/fiberx-expands", "title": "FiberX expands fibre network in southern Iraq", "seendate": "20261005T143000Z", "domain": "example-gulf-news.com", "language": "English", "sourcecountry": "United Arab Emirates"}
```

It does not get a snippet or article text, most Iraqi outlets, much Arabic or Kurdish coverage, social-media posts, engagement counts, or a completeness guarantee.

## 6. Inputs and outputs

### 6.1 Reads

- Queue `jobs.web-gdelt-poller` (kind `rotation`).
- Control plane: `sources`, `keywords`, `cursors`, `budgets` through quota-governor, `canary_targets`, `service_runs`.

### 6.2 Writes

- `raw.items`: one record per API response; envelope `service`, `route = green`, `vendor = gdelt`, `platform = web`, `source_id` (the rule), `job_id`, `job_kind`, `kind = search_response` (ADR-0070), `fetched_at`, `raw_ref`; partition key `web:<source_id>`.
- `search.results`, the shape of web-search-perplexity with `snippet` null and one optional addition, `hints` (domain, language, source country), partition key `canonical_url_hash`:

```json
{
  "schema": "search.results/v1",
  "message_id": "sr:gdelt:sha256:b27d93…:wgd-20261006-0905",
  "produced_at": "2026-10-06T09:05:44Z",
  "service": "web-gdelt-poller", "engine": "gdelt", "route": "green", "vendor": "gdelt",
  "job_id": "wgd-20261006-0905", "job_kind": "rotation", "attempt": 1,
  "keyword_rule_id": "7d2b0c4e-1f3a-4b5c-8d6e-9f0a1b2c3d4e", "keyword_id": "kw_0412", "client_ids": ["cl_17"],
  "query": {"text": "(\"FiberX\" OR \"فايبر اكس\" OR \"فايبر إكس\")", "variant": "or_group", "lang": null, "country": null, "request_id": null},
  "result": {"rank": 2, "title": "FiberX expands fibre network in southern Iraq", "url": "https://www.example-gulf-news.com/2026/10/05/fiberx-expands", "snippet": null, "date": "2026-10-05", "last_updated": null},
  "hints": {"domain": "example-gulf-news.com", "language": "English", "source_country": "United Arab Emirates"},
  "canonical_url": "https://www.example-gulf-news.com/2026/10/05/fiberx-expands",
  "canonical_url_hash": "sha256:b27d93…",
  "fetched_at": "2026-10-06T09:05:43Z",
  "raw_ref": "raw/green/web/2026/10/06/web-gdelt-poller/0009.jsonl.zst#6",
  "retention_class": "news_excerpt"
}
```

Also `service_runs` and `dlq.web-gdelt-poller` after 5 failed attempts.

### 6.3 State

`cursors.cursor` = start time of the last successful run, plus `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`; `budgets` request counters under `gdelt_doc_api`.

## 7. Limits, quotas and cost

- Cost: USD 0. GDELT DOC 2.0 is free and permits governmental use.
- Rate limit: 1 request per 5 seconds, which is 720 an hour and 17,280 a day (derived). At 200 rules the plan is 4,800 requests a day, about 28% of capacity; with every rule split into three forms it is 14,400 a day, about 83%.
- Budget tag `gdelt_doc_api` counts requests and enforces the spacing through quota-governor; there is no money cap unless ops sets one.
- Attribution: whether GDELT's terms require a citation is to be confirmed in the pilot; if so it goes into the provenance statement.
- Retention: `news_excerpt`; GDELT gives metadata only, never article text.

## 8. Failure handling and fallback

- HTTP 429 or a slow-down response: exponential backoff with jitter from 30 s to 15 min, then requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.web-gdelt-poller` and an alert fires. A 429 also raises `pacing_breach`, because it means the spacing failed.
- HTTP 403 or a block: the route is marked `degraded`, the run stops, an alert fires; no IP or identity is rotated.
- Non-JSON 200 (a plain-text rejection of the query, to be confirmed): `query_rejected`; the rule is marked `degraded` with the reason and skipped until its forms are edited; it is never counted as empty.
- Empty 200: only the canary counts; above 5% of canary queries in 15 minutes source-health-canary sets the web route `degraded`. GDELT is a complement, so no `fallback_on` is needed.
- Unknown response shape: raw body archived, `schema_unknown` raised, batch parked in `review_queue`, cursor not advanced.
- Saturated response: split in two windows and queried again (5.2), so nothing is silently cut.
- A long GDELT outage: `rotation_behind`, then the widened window recovers the gap when it ends.

## 9. Non-functional requirements

- Throughput: up to 720 requests an hour by design, about 200 an hour at 200 rules; results per hour are to be measured in the pilot. One replica sends at a time in practice, a second for failover; pacing is global.
- Latency: an article reaches `search.results` within the hour of the rule's run plus GDELT's own delay (to be measured in the pilot).
- Idempotency: `message_id = sr:gdelt:<canonical_url_hash>:<job_id>`; a replayed job republishes identical messages that search-hit-router absorbs; the cursor advances only after acknowledgement.
- Security: no key to protect; logs carry `job_id`, `source_id`, `route`, `vendor`, `keyword_id`, never the query text; the user agent names the company and a contact address; `/healthz` and `/metrics`; Node (TypeScript).

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `cost_units_total` (requests), `quota_denied_total`, `dlq_total`, plus `pacing_wait_seconds`, `saturated_total`, `query_rejected_total`, `empty_canary_total`, `iraqi_host_share`, `unique_domain_share` (domains no other engine returned, from search-hit-router). Alerts: `rotation_behind`, `pacing_breach`, `route_degraded`, `dlq_nonempty`, `query_rejected_rules`. SLO: rotation lag below one hour for 99% of rules per day.

## 11. Dependencies

`listening-sdk`, quota-governor, raw-archiver, search-hit-router (downstream), registry-writer (keyword-rule rows), source-health-canary, web-search-perplexity and web-search-mojeek (parallel engines), news-article-extractor (through `article.urls`), Redpanda, Supabase Postgres.

## 12. Risks and mitigations

- Thin Arabic coverage and near-absent Iraqi outlets: success is measured by cross-border coverage and new domains, not Iraqi recall; if the pilot shows no unique yield for a client, GDELT is switched off for that client.
- A free service has no SLA: the paid engines carry the web leg; GDELT is optional and nothing depends on it.
- Several replicas breaking the spacing: allowance is global through the governor, and a test with three replicas is in the acceptance criteria.
- Query syntax limits, including short Arabic phrases: forms below the API's minimum are dropped with a log line, and `query_rejected` surfaces the rest to ops.
- Language and country tags from GDELT are machine-made: search-hit-router uses them as hints, never as proof of Iraqi origin.

## 13. Acceptance criteria

1. With 200 fixture rules in combined mode, one hourly cycle sends exactly 200 requests, and every rule's `next_poll_at` equals its run start plus 1 hour.
2. With three replicas running for one simulated hour, no two request starts are less than 5 seconds apart in the request log.
3. When a scan plans more than 720 requests in an hour, priority rules still run that hour, the rest go most-stale-first with none older than 24 hours, and `rotation_behind` is raised.
4. A response at the maximum record count is split into two half windows, both are queried, and the union of the articles is published once.
5. A non-JSON 200 marks the rule `degraded` with reason `query_rejected`, is not counted as empty and does not advance the cursor.
6. Every article produces one `search.results` message with `engine = gdelt`, `snippet = null`, `hints`, `canonical_url_hash`, `keyword_rule_id`, `client_ids`, `raw_ref`, `retention_class = news_excerpt`, partitioned by `canonical_url_hash`.
7. Replaying a completed job republishes identical `message_id` values and commits no second batch to `raw.items`; the cursor does not advance when the produce fails.
8. An empty answer to the canary query increments the empty-200 counter; an empty answer to an ordinary rule does not.
9. After a simulated 6-hour outage the next run's window covers the gap, and no fixture article from the gap is missed.
10. A new rule's first run uses the widest accepted window; an edit to a rule's forms is used by its next run without a restart.

## 14. Open questions

1. API specifics: parameter names, maximum records, minimum phrase length, query length, maximum span, and how a rejected query is reported. The pilot answers them.
2. Is a combined OR query reliable with mixed Arabic and Latin forms, or must every rule split by form?
3. Does search-hit-router accept the optional `hints` field, or should the hints travel only in `raw.items`?
4. Does GDELT require attribution?
5. Should priority rules get a second pass restricted to Arabic sources or Iraqi source country, if the pilot shows the unfiltered pass hides them?
