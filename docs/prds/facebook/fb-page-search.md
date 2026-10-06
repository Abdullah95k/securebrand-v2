# fb-page-search

**Platform:** Facebook · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend engineer, discovery lane · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The registry only polls Pages it knows about. A client signing up gives us a brand name, a few competitors and a handful of keywords, not a list of Facebook Page ids, and the Iraqi Facebook landscape is full of Pages the client has never heard of: regional branches, dealer Pages, fan and impostor Pages, outlets that cover the brand, and new Pages that appear every week. fb-page-search is how the product turns names into candidate Pages. It calls the Pages Search API, the one search Meta grants under Page Public Content Access (PPCA), which finds Pages by name. It does not find posts: there is no green keyword search of Facebook posts, and the amber substitute is fb-keyword-search.

Without this service, seeding a client would be manual (ops pasting Page URLs), rediscovery would never happen, and the registry would stop at whatever the client knew on day one. For a listening product that promises to find "who is talking about you", that is the difference between a watchlist and a listening platform.

## 2. Objective (the end state this service delivers)

Every active keyword set has been searched against the Pages Search API at seeding and again every week, and every Page returned that is not already in the registry has been handed to poster-resolver through `discovery.hits` with `hit_type = page`, so that fb-page-resolver and the qualifier can decide whether it becomes a source. Target: 100% of keyword sets searched within 24 hours of creation and re-searched within 7 days of the previous run; zero duplicate candidates emitted for the same Page and keyword inside one week.

## 3. Scope

### In scope

- Seeding searches when a client's keyword set is created or changed, and weekly rediscovery searches per keyword set.
- Querying every variant stored for a keyword (Arabic, Latin script, transliterations) and merging results by Page id.
- Emitting `discovery.hits` (`hit_type = page`) for Pages not already in `sources`, with the keyword and client context the qualifier needs.
- Honoring the Pages bucket quota through quota-governor and recording cursors per keyword.

### Out of scope

- Searching posts by keyword (fb-keyword-search, amber) and groups (never green).
- Resolving candidate Pages (fb-page-resolver), deciding whether they qualify (qualifier), writing the registry (registry-writer), checking the 180-day rejected memory (poster-resolver).
- Polling or backfilling Pages once registered (fb-page-feed-poller, fb-backfill).

## 4. Users and consumers

- **Clients** experience it as "the platform found Pages I did not know about" and approve or ignore suggestions in the product; they never call the service.
- **Ops** sees search runs, result counts and candidates per keyword, and can trigger a search by hand.
- **poster-resolver** consumes `discovery.hits`, deduplicates candidates across platforms and services, applies the rejected memory, and dispatches fb-page-resolver; **qualifier** and **registry-writer** follow.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Two sources of jobs on `jobs.fb-page-search` (partitioned by `keyword_id` so one keyword is never searched twice at once): (a) a control-plane change to `keywords` (`created` or `variants changed`) for a client with Facebook in scope, emitted by registry-writer, `reason = seed`; (b) the weekly rediscovery scheduler inside this service (one leader replica, Postgres advisory lock), `reason = weekly`.

**Cadence.** One search per keyword set per 7 days. The scheduler keeps `next_search_at` per keyword in `cursors` (service `fb-page-search`, cursor = ISO timestamp of the last run start), sets it from the START of the last run (fixed weekly cadence, no drift), and emits jobs ordered by `next_search_at` then by the client's priority flag, so no keyword is skipped twice in a row. Seeding jobs jump the queue.

**Catch-up.** If the service falls behind by more than one day (`rotation_lag_seconds` above 24 hours for the most overdue keyword), it works most-overdue first and raises `rotation_behind`. A missed week is not lost: the next run returns the same Pages, and `discovery.hits` dedup (Page id + keyword within 7 days) prevents double emission.

**Backfill.** Not applicable to a name search: the first run of a keyword is the seeding search, and every run returns the current set of matching Pages rather than a history. Comment decay does not apply.

### 5.2 Step by step

1. Consume the job (`keyword_id`, `client_ids`, `reason`, `attempt`); load the keyword's variants from `keywords`.
2. Select the system-user token of the first healthy client in `client_ids` from Supabase Vault; ask quota-governor under `budget_tag = meta_graph_pages:<client_id>` for one allowance per variant.
3. For each variant, call `/pages/search` (5.3), following `paging.next` until exhausted or until the page cap set by configuration is reached (the useful depth is to be measured in the pilot; relevance ordering puts true matches first).
4. Merge results across variants by Page `id`; drop ids already present in `sources` (any route, any tier, including retired) and ids emitted for this keyword within the last 7 days (kept in `cursors.last_error` is not used for this; a per-keyword emitted-id set is kept in the control plane as `decisions`-adjacent state, see 6.3).
5. Emit one `discovery.hits` message per remaining Page, carrying the raw search fields and the keyword context.
6. After Redpanda acknowledges, write the cursor (`next_search_at = run_start + 7 days`), `service_runs`, and the metrics in section 10.

### 5.3 The call it makes

```
GET https://graph.facebook.com/v<pinned>/pages/search
  ?q=<variant text, URL-encoded, Arabic or Latin>
  &fields=id,name,location,link,is_verified
  &limit=100
  &access_token=<system-user token (PPCA)>
```

`limit` is requested at 100, the same ceiling the fact sheet gives for `/feed`; the endpoint's own ceiling is to be measured in the pilot. Pagination by `paging.next`. The token is the client's system-user token: the Pages Search API is granted by PPCA, and the call is made on behalf of the client whose keyword triggered it.

### 5.4 What it gets

Per Page: `id`, `name`, `location` (street, city, country, zip where the Page set them), `link`, `is_verified`. Example:

```json
{
  "data": [
    {"id": "100064583471102", "name": "Zain Iraq", "location": {"city": "Baghdad", "country": "Iraq"}, "link": "https://www.facebook.com/zainiraq", "is_verified": true},
    {"id": "104557812990341", "name": "زين العراق - فرع البصرة", "location": {"city": "Basra", "country": "Iraq"}, "link": "https://www.facebook.com/profile.php?id=104557812990341", "is_verified": false}
  ],
  "paging": {"cursors": {"before": "QVFI...", "after": "QVFI..."}}
}
```

What it does not get: posts, `fan_count`, `category`, `website`, `about` (fb-page-resolver reads those on the Page node); groups; profiles (the API returns Pages only, which is also why everything it returns is a potential source and never an individual).

## 6. Inputs and outputs

### 6.1 Reads

`jobs.fb-page-search`; `keywords` (variants, client ids, Facebook in scope), `clients`, `sources` (existence check by `platform_id`), `cursors`, `budgets` through quota-governor, `health` through the SDK canary hook.

### 6.2 Writes

`discovery.hits`, one message per candidate Page:

```json
{
  "platform": "facebook",
  "hit_type": "page",
  "service": "fb-page-search",
  "route": "green",
  "vendor": null,
  "found_at": "2026-10-06T06:30:12Z",
  "keyword_id": "3d9c1b2a-7e4f-4a6b-8c1d-2e5f6a7b8c9d",
  "query": "زين العراق",
  "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
  "candidate": {
    "platform_id": "104557812990341",
    "name": "زين العراق - فرع البصرة",
    "link": "https://www.facebook.com/profile.php?id=104557812990341",
    "is_verified": false,
    "location": {"city": "Basra", "country": "Iraq"}
  },
  "context": null,
  "job_id": "01J9P7K2H9D4F1G6S8A3L5Z0QX",
  "retention_class": "meta_on_request"
}
```

Also `service_runs`, `dlq.fb-page-search`. It never writes `raw.items`: a search result is a candidate, not an item.

### 6.3 State

`cursors` row per keyword (`cursor` = last run start, `next_search_at` derived, `last_success_at`, `last_error`, `consecutive_errors`); a per-keyword set of emitted Page ids with the emission date (table `decisions`, kind `fb_page_search_emitted`, pruned after 7 days) so repeated runs do not re-emit; `budgets` counters per token.

## 7. Limits, quotas and cost

- Every call counts against the Pages bucket: 4,800 calls × engaged users per 24 h on the system-user token, shared with fb-page-feed-poller, fb-backfill, fb-post-comments-fetcher and fb-reactions-fetcher. quota-governor ranks search below rotation polls and comment series.
- Calls per run = variants × pages followed; keyword sets, variants and depth at full scale are to be measured in the pilot.
- Cost: USD 0 per Graph call; the cost is quota.
- Error 80001 does not apply to search (it is per Page), but HTTP 429 on the bucket does.
- The search is by name only: a Page whose name does not contain the brand (for example an outlet) is found through fb-keyword-search (amber) or through keyword-matcher hits on already registered Pages, not here.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts `dlq.fb-page-search` and an alert.
- HTTP 401 and 403: token marked `degraded`, run stopped, alert; no retries with other tokens or IPs.
- Empty 200 on a variant known to match (canary keyword in `canary_targets`, for instance the client's own Page name): counted; above 5% in 15 minutes source-health-canary flips `health = degraded`. There is no amber fallback for Page name search; fb-keyword-search is a different capability, not a substitute.
- Schema change: the response is archived under `raw/green/facebook/<yyyy>/<mm>/<dd>/fb-page-search/` by raw-archiver and the run parks with `schema_unknown`.
- Replays: emission dedup by Page id and keyword within 7 days makes a replayed job idempotent.

## 9. Non-functional requirements

- Throughput: weekly runs for every keyword set at full scale (count to be measured in the pilot) finish inside the week with quota to spare for seeding.
- Latency: seeding search within 24 hours of keyword creation; in practice minutes, quota permitting.
- Idempotency: candidates deduplicated per Page id and keyword per 7 days; jobs replayable.
- Scaling: workers on partition lag of `jobs.fb-page-search`; one leader scheduler.
- Security: tokens per job from Supabase Vault, never logged; Pages only, never profiles; Meta data never processed for law-enforcement or national-security purposes; provenance (route, vendor, service, time) on every hit; retention `meta_on_request`.

## 10. Metrics and alerts

`items_fetched_total` (Pages returned), `items_new_total` (candidates emitted), `jobs_total{status,reason}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `candidates_per_keyword` and `keywords_in_rotation`. Alerts: `rotation_behind` (most overdue keyword above 24 hours), `token_degraded`, `dlq_nonempty`, `empty_200_rate`, `zero_results_streak` (a keyword returning nothing for 3 consecutive weekly runs, for ops review of its variants).

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, poster-resolver, fb-page-resolver, qualifier, registry-writer, Supabase Postgres (`keywords`, `sources`, `cursors`, `decisions`, `budgets`) and Vault, Redpanda. Meta prerequisites: Business Verification, App Review for PPCA (the Pages Search API is part of the grant), Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- Name search returns impostor and fan Pages: that is a feature for brand-protection clients and a qualifier job for everyone else; `is_verified` and `location` travel with the hit so the qualifier and the review card have them.
- Arabic spelling variation (hamza, ta marbuta, Sorani forms) misses Pages: variants are curated per keyword and `zero_results_streak` flags keywords whose variants need work.
- Quota contention with rotation during a large onboarding: quota-governor ranks search last among green Facebook services; seeding may take longer than minutes but never starves polling.
- The endpoint's depth and ordering are not documented in the fact sheet: measured in the pilot, then capped by configuration.

## 13. Acceptance criteria

1. Creating a keyword with 3 variants for a client with Facebook in scope produces one `jobs.fb-page-search` job with `reason = seed` within the scheduler's scan period, and 3 Graph calls (plus paging).
2. A simulated search returning 12 Pages, 4 of which exist in `sources`, emits exactly 8 `discovery.hits` messages with `hit_type = page`, each carrying `keyword_id`, `client_ids`, `candidate.platform_id`, `candidate.name`, `candidate.link`, `candidate.is_verified`, `candidate.location`, `route = green`, `service = fb-page-search`.
3. Running the same keyword again 2 days later with the same results emits zero new hits; running it 8 days later emits them again (7-day dedup window test).
4. A weekly run started at Monday 03:00 sets `next_search_at` to the following Monday 03:00 regardless of how long the run took.
5. With 50 fixture keywords and the scheduler running for 14 simulated days, every keyword is searched twice and `rotation_lag_seconds` never exceeds 24 hours.
6. A simulated 429 triggers backoff from 30 s to 15 min with `attempt + 1`; after 5 attempts the job is in `dlq.fb-page-search` and an alert fired.
7. A 401 marks the token `degraded` and no further call uses it.
8. The service never produces a `raw.items` message and never emits a hit whose `platform_id` belongs to a profile (fixture includes a non-Page id in the response; it is dropped and logged).
9. Tokens never appear in logs or messages; `/healthz` and `/metrics` respond.

## 14. Open questions

1. Depth: how many pages of results per variant are worth following before relevance decays into noise; to be measured in the pilot and then fixed in configuration.
2. Whether a client should be able to mark a candidate "never suggest again" directly from the product, which would feed the rejected memory without a qualifier round-trip.
3. Whether weekly rediscovery should run for keyword sets whose clients have Facebook in scope but no Facebook Pages registered yet (proposed: yes, that is exactly when discovery matters most).
