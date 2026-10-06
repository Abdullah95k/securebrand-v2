# fb-keyword-search

**Platform:** Facebook · **Route:** amber (optional, flag `FB_VENDOR_ROUTE`) · **Lane:** Discover and qualify · **Owner:** Backend lead, Facebook adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Meta's official routes can find Pages by name (fb-page-search) and read the posts of Pages we already know (fb-page-feed-poller), but there is no official way to ask Facebook which public posts mention a brand: the green route has no post search. The only way is to buy it from a screened vendor that does the collection itself: SociaVault's Facebook keyword search, with ScrapeCreators as the alternative. fb-keyword-search runs every client's keywords through it once a day and puts what it finds into the pipeline like any polled item.

Without it, a brand mentioned in a post on a Page or in a group we do not watch is invisible. The Facebook side would also lose its main way to discover new sources: hits found here are how keyword-matcher, poster-resolver and the qualifier learn about unregistered Pages, and how a hit inside a group adds that group as a source (qualifier rule 8). The service is optional, behind `FB_VENDOR_ROUTE`, disclosed in the provenance statement and excluded from government contracts.

## 2. Objective (the end state this service delivers)

While the flag is on, every active keyword rule of every non-government client is searched once every 24 hours with its query variants, and every new post found reaches `raw.items` under the rule's source, with its Page or group context and poster id. Target: every rule run within 24 hours for 99% of rules per day, zero jobs lost, spend inside the `fb_vendor` budget, and the main form of every rule searched every day even when the budget is under pressure.

## 3. Scope

### In scope

- Rotation over every Facebook keyword rule and execution of `rotation`, `backfill` and `ops_force` jobs on `jobs.fb-keyword-search`.
- Query variants from the client's keyword set: Arabic forms, Kurdish (Sorani) forms, brand handles.
- Vendor selection by flag and fallback; incremental reads with one cursor per variant.
- Writing `raw.items` (kind `post`) with `source_id` = the keyword rule; `author_ref` for every poster.

### Out of scope

- Matching keywords on items and writing `item.hits` and `discovery.hits` (keyword-matcher); resolving and qualifying posters and groups (poster-resolver, fb-page-resolver, qualifier).
- Finding Pages by name (fb-page-search); reading registered Pages and groups (fb-page-feed-poller, fb-group-posts-poller); comments.
- Creating keyword rules (client set-up and registry-writer).

## 4. Users and consumers

- **Clients** experience it as "mentions of my brand from places I do not watch yet", marked as vendor-sourced. Government clients never receive it.
- **Ops** owns the flag, the vendor and the `fb_vendor` budget, and can force a search.
- **Downstream services**: normalize-item, keyword-matcher, poster-resolver (through discovery hits), qualifier, raw-archiver, quota-governor, source-health-canary, backfill-orchestrator.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.fb-keyword-search`, partitioned by `source_id` (the keyword rule), emitted by the rotation scheduler inside this service (one leader replica elected through a Postgres advisory lock; the scan period is an environment variable well inside 24 hours). It runs only while `FB_VENDOR_ROUTE` is `sociavault` or `scrapecreators`, and selects `sources` rows with `platform = facebook`, `source_type = keyword_rule`, `route = amber`, `health != blocked`, `backfill_status in (done, capped)`, at least one client in `client_ids` that is not under a government contract, and `next_poll_at <= now()`. Backfill jobs come only from backfill-orchestrator.

**Cadence.** Search is the exception to the tier intervals of the post pollers (60 minutes, 6 hours, 24 hours): a keyword has no reach, and every request costs a credit, so every active rule, whatever its tier, runs once every 24 hours. Push does not apply. Dormant (no new post found in 30 days): weekly; a new find promotes the rule back to daily. Retired (no hits and no client interest for 180 days): never searched. A keyword shared by several clients is one rule with several `client_ids`, searched once.

**Keeping every rule covered.** `next_poll_at` is set from the START of the last run (`poll_started_at + interval`), so cadence is fixed. Jobs are ordered by `next_poll_at` then by tier (the client's priority), so no rule is skipped twice in a row; a failed job keeps its old `next_poll_at`. At 80% of the monthly `fb_vendor` budget quota-governor may stretch intervals, never beyond daily; a rule is already daily, so the lever is the variants: low-ranked variants are shed first, and the main form of every rule still runs each day.

**Catch-up.** `rotation_lag_seconds` is now minus `next_poll_at` of the most overdue rule. Above one interval the scheduler works the most stale first and raises `rotation_behind`. Reads are incremental from the cursor, so a late run still returns everything since the cursor, within the vendor's depth.

**Backfill on add.** A new rule has `backfill_status = pending`. backfill-orchestrator sends a `backfill` job: all variants, the last 90 days or the vendor's search depth, whichever is smaller. The cursors are then written, `backfill_status` becomes `done` or `capped`, and `next_poll_at = now()`. Backfill is per rule, never per poster.

### 5.2 Step by step

1. Consume a job; read the flag. If `off`, acknowledge as `skipped_flag_off`: no call, cursor and `next_poll_at` untouched. Read the `sources`, `keywords` and `cursors` rows; stop if `health = blocked`.
2. Build the variant list the client's keyword set defines, ranked, main form first; remove duplicates.
3. Pick the vendor: the flag value, or the other vendor when `health = fallback` and it offers search. Fetch its key from `vendor_keys` in Supabase Vault for this job only.
4. For each variant in rank order: ask quota-governor for allowance under `fb_vendor` (1 credit per request); call the vendor; page until a result older than the variant's cursor or the page cap (environment variable `FB_SEARCH_MAX_PAGES`, value to be set in the pilot).
5. For each new post: compute `author_ref`; keep the Page or group context and the poster id; write one `raw.items` message with `source_id` = the rule. One post found by several variants of the rule is emitted once per run.
6. After Redpanda acknowledges: update the per-variant cursors, `last_success_at`, `consecutive_errors = 0`, `last_polled_at`, `next_poll_at`; promote or demote dormancy; record cost.

### 5.3 The call it makes

```
SociaVault:     its Facebook keyword-search endpoint (path to be confirmed in the pilot), 1 credit per request
ScrapeCreators: a keyword-search endpoint, if one exists (to be confirmed in the pilot)
  query:  the variant string                              (parameter name to be confirmed in the pilot)
  paging: the vendor's cursor from the previous response  (to be confirmed in the pilot)
  auth:   the vendor key from Supabase Vault, in the header the vendor specifies
```

`FB_VENDOR_ROUTE` selects the vendor for all amber Facebook services; if the pilot shows ScrapeCreators has no search, see open question 1. Recency sort, date filters, page size and depth are the vendor's, to be confirmed in the pilot. Fields needed: post id, text, created time, URL, poster id and name, Page or group context, counts.

### 5.4 What it gets

Public posts matching the query, with context. Illustrative shape; field names are the vendor's and are to be confirmed in the pilot.

```json
{
  "id": "4118203958217764",
  "text": "الإنترنت من شركة المثال بطيء جداً هالأيام، منو عنده نفس المشكلة؟",
  "created_time": "2026-10-06T06:30:12+0000",
  "url": "https://www.facebook.com/groups/271936048205533/posts/4118203958217764",
  "author": {"id": "61552270194836", "name": "مستخدم تجريبي"},
  "context": {"type": "group", "id": "271936048205533", "name": "مجموعة أهالي المنطقة"},
  "reactions": 12, "comments": 9, "shares": 0
}
```

Not obtained: a complete record of every matching post (vendor search is a sample, and the provenance statement says so); comments; private content.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.fb-keyword-search`; `sources` (keyword rules), `keywords`, `cursors`, `clients` (government marker), `vendor_keys`, `canary_targets`, `budgets` through quota-governor; the flag at the start of every job; `health` through the SDK canary hook; `source.events`.

### 6.2 Writes

`raw.items`, one message per found post, following the search output rule: `source_id` is the keyword rule that produced the query.

```json
{
  "envelope": {
    "platform": "facebook", "kind": "post", "route": "amber", "vendor": "sociavault",
    "service": "fb-keyword-search",
    "source_id": "c7e41b95-0a3d-4f82-b6c9-18d5e2a07f43",
    "platform_id": "4118203958217764",
    "idempotency_key": "facebook:post:4118203958217764",
    "job_id": "01J9N7E3H2M6T9X1V4K8B0QRWD", "attempt": 1,
    "fetched_at": "2026-10-06T03:12:48Z",
    "retention_class": "vendor_agreed",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/amber/facebook/2026/10/06/fb-keyword-search/000019.jsonl.zst",
    "query": {"variant": "شركة المثال", "rank": 1},
    "author_ref": "9a3f6d12c8e5b07a4d1c93e6f2b8a5071e4c9d3b6a8f0e2c5d7b1a93f4e6c820",
    "metrics_observation": "search"
  },
  "payload": { "...": "the post object from 5.4, unchanged" }
}
```

`author_ref` is a keyed hash of the poster id. The poster id and name stay in the payload so keyword-matcher and poster-resolver can treat the poster as a candidate (rule 8: the group is a source, the poster is qualified separately); an individual is kept only as `author_ref`. This service writes neither `item.hits` nor `discovery.hits`; keyword-matcher does. Also `service_runs` and `dlq.fb-keyword-search` after 5 failed attempts.

### 6.3 State

`cursors.cursor` = a small JSON map from variant to the newest `created_time` seen, with `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`, `backfill_status`; `budgets` counters for `fb_vendor`; in memory only the leader lock, the vendor page token and backoff state.

## 7. Limits, quotas and cost

- SociaVault: 1 credit per request, USD 1.99 to 4.83 per 1,000 credits, credits never expire. ScrapeCreators: USD 0.99 to 1.88 per 1,000 requests. Vendor rate limits: to be confirmed in the pilot.
- For scale, a set the size of the web-search plan (200 keywords × 9 variants once a day, about 54,000 to 60,000 queries a month) at one request per query costs about USD 107 to 290 a month in SociaVault credits, or USD 53 to 113 with ScrapeCreators. Extra pages multiply this; the real keyword count, variants and pages per query are to be measured in the pilot.
- Budget tag `fb_vendor`, shared with fb-group-posts-poller and fb-group-comments-fetcher.

## 8. Failure handling and fallback

- Vendor 429 and rate-limit responses: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.fb-keyword-search` and an alert fires.
- HTTP 401 and 403: mark the route `degraded`, stop the batch, alert; never rotate accounts or IPs.
- Empty 200: an empty result is normal for a rare keyword, so it is counted only on canary queries (`canary_targets`, very common Arabic and Kurdish terms) and on rules that returned results in the last 7 days; above 5% in 15 minutes source-health-canary flips `health = degraded` and, with the flag on and the other vendor's key present and offering search, emits `fallback_on`. Jobs read the flag and health at the start.
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: cursors move only after acknowledgement; a replay re-emits the same posts and normalize-item deduplicates them.

## 9. Non-functional requirements

- Throughput: Facebook's full-scale share is 12.0M items a month; the share found by search is to be measured in the pilot.
- Latency: a post indexed by the vendor reaches `raw.items` within 24 hours plus run time.
- Idempotency: `facebook:post:<platform_id>`; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag; one leader scheduler.
- Security: vendor keys from Supabase Vault per job, never logged; no account pools, no proxies, no Facebook login of ours; individuals never profiled; amber data excluded from government contracts; Meta data never processed for law-enforcement or national-security purposes; provenance on every message.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `queries_total{vendor,rank}`, `variants_skipped_total`, `keyword_rules_in_rotation`, `backfill_jobs_total` and `fallback_active`. Alerts: `rotation_behind`, `vendor_degraded`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`, `budget_80_percent`. SLO: rotation lag below 24 hours for 99% of rules per day.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, keyword-matcher, poster-resolver, fb-page-resolver, qualifier, registry-writer, backfill-orchestrator, fb-page-search, fb-group-posts-poller, Supabase Postgres and Vault, Redpanda, a vendor contract with SociaVault (and ScrapeCreators for the alternative).

## 12. Risks and mitigations

- Platform terms: any breach sits in the vendor's contract; the route is optional, flagged, disclosed and excluded from government contracts.
- Both vendors are weakly cleared (owner not verified): checked before go-live, since no Israeli-affiliated vendor is allowed.
- Vendor search is a sample, not a census: the provenance statement says so, and counts are not shown as complete.
- Cost grows with keywords × variants × pages: shared keywords are searched once, low-ranked variants are shed first at 80%.
- Weak Kurdish and dialect coverage: measured in the pilot per variant form.
- Personal data in results: individuals are kept only as `author_ref`, never backfilled.

## 13. Acceptance criteria

1. With `FB_VENDOR_ROUTE = off` no vendor call is made, jobs are acknowledged `skipped_flag_off`, and cursors and `next_poll_at` do not move.
2. A rule whose run started at 09:00:00 has `next_poll_at` at 09:00:00 the next day even if the run took 20 minutes.
3. With 200 fixture rules of 9 variants over 3 days against a simulated vendor, every rule runs once per 24 hours and none is skipped twice in a row.
4. Variants run in rank order; at 80% of the `fb_vendor` budget low-ranked variants may be shed, but the main form of every rule still runs each day.
5. Every `raw.items` message carries `source_id` = the rule, `route = amber`, `vendor`, `retention_class = vendor_agreed`, the Page or group context, the poster id and `author_ref`; `client_ids` has no government client.
6. One post found by two variants of a rule is emitted once in that run; found by two rules it yields two messages with one `idempotency_key` and one stored item.
7. A variant skipped for quota resumes from its own cursor the next day with no post lost.
8. A rule with `backfill_status = pending` is never a rotation job; its backfill job stops at 90 days or the vendor's depth, sets `done` or `capped`, and sets `next_poll_at = now()`.
9. A rule with no new post in 30 days runs weekly; a new find returns it to daily.
10. An empty-200 rate on canary queries above 5% in 15 minutes switches later jobs to the other vendor, only if it offers search.
11. The cursor does not advance when the Redpanda produce fails, and vendor keys never appear in logs.

## 14. Open questions

1. If ScrapeCreators has no keyword search, should all amber Facebook services run on `sociavault`, or should a per-service override exist?
2. Which sort order, date filter, page size and depth does the vendor search offer, and how well does it cover Kurdish and dialect spellings?
3. Who ranks the variants, and where is the list kept: the `keywords` table?
4. Should a client's priority keywords run more often than daily, at higher cost? Proposed: not in v1.
5. Should this service also emit early `discovery.hits` for unregistered Pages and groups, as x-recent-search does? Proposed: no, keyword-matcher does.
