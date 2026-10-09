# li-post-comments-fetcher

**Platform:** LinkedIn · **Route:** amber (optional, flag `LI_VENDOR_ROUTE`) · **Lane:** Comments · **Owner:** Backend lead, LinkedIn adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

When a competitor, a partner or a ministry posts on LinkedIn, the comments under the post show how the audience took it: applause, doubt, complaints, questions. The official route cannot read them: the Community Management API reaches only pages the client administers (the organization must grant ADMINISTRATOR, DIRECT_SPONSORED_CONTENT_POSTER or CONTENT_ADMIN), and li-own-comments-fetcher covers exactly those. The harvestapi Actors on Apify are the optional route to third-party company pages. harvestapi does the collection itself, so the breach, if any, sits in its contract, not ours. The route is gated by `LI_VENDOR_ROUTE` (`off` or `harvestapi`), disclosed to every client in the provenance statement, and excluded from government contracts.

li-post-comments-fetcher runs the `linkedin-post-comments` Actor on the posts that li-company-posts-poller found. Without it, third-party LinkedIn posts have engagement counts but no audience voice: no sentiment on a competitor's announcement, no themes, no comparison with the client's own comments. With the flag off the product still works; the audience view stays limited to the client's own posts.

## 2. Objective (the end state this service delivers)

Every registered third-party post that comment-decay-scheduler selects has its comments fetched at +24 h and +3 d after it is first seen, extended only when the thread is still growing, with every commenter kept as a hashed reference and no name or profile link in any store, inside the `li_vendor_post_comments` budget. Target: comment series completed on time for 95% of posts, zero identity fields in `raw.items`, spend within the monthly budget.

## 3. Scope

### In scope

- Executing comment jobs (kind `comments`) for vendor-route posts: series steps, extension steps, hot-post extras, client-requested refreshes, and the one-off job per backfilled post from backfill-orchestrator.
- One Actor run per job: start, wait, read the dataset; hashing commenters at the edge; content-hash comparison; writing `raw.items` (kind `comment`); reporting `new_count`, `seen_count`, `pages`, `cost_units` to comment-decay-scheduler.
- Reading `LI_VENDOR_ROUTE` at the start of every job.

### Out of scope

- Emitting jobs (comment-decay-scheduler only); posts (li-company-posts-poller); client posts and their comments (li-client-posts-poller, li-own-comments-fetcher).
- Replies: the series profile for this route has none, so only top-level comments are requested.
- Commenters as individuals: never sources, never profiled, never passed to poster-resolver or qualifier.
- Purging (retention-purger), aggregation (aggregator), sentiment and topics (analysis workers).

## 4. Users and consumers

- **Clients** (non-government) see aggregates on third-party posts: comment counts, sentiment shares, themes, unique commenters. Government clients never receive this data.
- **Ops** watches vendor spend, series lateness and the DLQ, and switches the flag.
- **Downstream**: normalize-item, aggregator, analysis-sentiment, analysis-topics, comment-decay-scheduler, retention-purger, raw-archiver, quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Jobs on `jobs.li-post-comments-fetcher`, partitioned by `source_id`, emitted only by comment-decay-scheduler: `kind = comments`, `post_ref`, `series_step`, `due_at`, `attempt`. This service has no scheduler of its own. By default the series opens for posts of registered third-party company pages; posts matched by keyword through li-post-search get one only if the budget allows (section 14).

**Series for other posts, amber.** After a post is first seen: +24 h, +3 d. No replies.

**Early stop.** comment-decay-scheduler applies it from this service's report; this service never stops a series itself. On this route growth is measured over this service's running total of comments seen, which the report carries (ADR-0019).

**Extension.** When the last scheduled fetch (+3 d) still adds 20% or more new comments, the series continues every 2 days until day 30. Each extension fetch asks quota-governor like any other step.

**Hot posts.** When a fetch implies more than 100 new comments an hour, an extra fetch is inserted every hour for the next 6 hours. Once the monthly budget passes 80%, quota-governor drops these extras first.

**Paging and the marker.** Billing is per item produced, so the cost control is the run's max items, not the reading of the dataset. The service reads the dataset in pages and, on a newest-first run, stops at the first comment older than the newest one already seen; otherwise it reads to the end. The newest-seen marker (`newest_comment_at`) and the running total of comments seen live in the series state owned by comment-decay-scheduler, because held comments expire at 48 hours (section 7). A comment older than the marker that is no longer held is never re-ingested.

**Flag, government and budget.** If `LI_VENDOR_ROUTE` is `off`, the step is acknowledged `skipped_flag_off`; steps skipped while the flag was off are not replayed when it is turned on, so spend stays predictable. If every client of the post's page is a government client, the step is acknowledged `skipped_government`. A step denied by quota-governor waits; one still unserved 24 hours after `due_at` is dropped and counted.

**Beyond day 30 and backfill.** No automatic fetches after day 30; a client may request a refresh of one post, budget permitting. For posts of a newly added page (last 30 days) backfill-orchestrator emits one comments job each.

**Catch-up.** Jobs are taken in `due_at` order, oldest due first; a late step is still correct because it reads from the marker.

### 5.2 Step by step

1. Consume a job; read `LI_VENDOR_ROUTE`, the `sources` row, the post URL from the stored post. Apply the flag and government rules above.
2. Load the Apify token from `vendor_keys`. Ask quota-governor for `budget_tag = li_vendor_post_comments` with the planned max items (comments seen so far plus headroom, bounded by the cap in `budgets`).
3. Start the Actor run (5.3), wait for a terminal status, read the dataset.
4. For each comment: replace the vendor's author object by `{"ref": <hash>}` (5.4) and drop name, headline, profile link and picture; compute the content hash; compare with the held comments (ids and hashes from ClickHouse `comments`).
5. Not held and newer than the marker: new. Held with the same hash: seen. Held with a different hash: an edit, written with the same key and a new hash. If the run read to the end (fewer items than max items), a held comment missing from the dataset becomes a `deletions` message with reason `platform_sync`; a run that hit max items infers none.
6. Write `raw.items`; raw-archiver lands the batch under `raw/amber/linkedin/<yyyy>/<mm>/<dd>/li-post-comments-fetcher/`, a prefix with the 48-hour rule.
7. After Redpanda acknowledges, report `new_count`, `seen_count`, `pages`, `cost_units` (items returned) and the new marker to comment-decay-scheduler.

### 5.3 The call it makes

```
POST https://api.apify.com/v2/acts/harvestapi~linkedin-post-comments/runs
  Authorization: Bearer <Apify token from vendor_keys>
  body (JSON): the post URL, the maximum number of items, a sort option where offered
               (input field names to be confirmed in the pilot)
-> wait until status SUCCEEDED | FAILED | TIMED-OUT | ABORTED
   (GET /v2/actor-runs/<run id>, wait interval an environment variable)
GET https://api.apify.com/v2/datasets/<defaultDatasetId>/items?offset=<n>&limit=<n>
```

Max items per run is bounded by a cap held in `budgets` (value to be measured in the pilot); the Actor's input schema is pinned in `listening-sdk`.

### 5.4 What it gets

Per comment, as the Actor's output schema defines it (illustrative; field names to be confirmed in the pilot): comment id, text, created time, like count, and the commenter's name, headline, profile link and picture. The service never forwards the last four. The commenter reference is `sha256(salt + profile identifier)`, the salt held in Supabase Vault, so the same commenter has the same reference across runs without being identifiable. Message payload after hashing:

```json
{
  "id": "7246999999999999888",
  "post_id": "7246999999999999999",
  "text": "تهانينا لكم، إنجاز يستحق التقدير",
  "createdAt": "2026-10-06T14:12:40.000Z",
  "engagement": {"likes": 3},
  "author": {"ref": "9c1f3a5e7b2d4086af31c8e5d7b90a42e6f1038b5c7d9e2a4f60813b5d7c9e1a"}
}
```

What it does not get: replies, comments beyond the run's cap, reactor identities, and any guarantee that the thread is complete (to be measured in the pilot).

## 6. Inputs and outputs

### 6.1 Reads

`jobs.li-post-comments-fetcher`; `sources`, `client_sources` and `clients` (government flag), `vendor_keys`, `budgets` through quota-governor; the flag `LI_VENDOR_ROUTE`; the series state (marker, running total); ClickHouse `comments` (ids and content hashes of held comments, read-only); the post URL from the stored post.

### 6.2 Writes

`raw.items`, one message per new or changed comment:

```json
{
  "envelope": {
    "platform": "linkedin", "kind": "comment", "route": "amber", "vendor": "harvestapi",
    "service": "li-post-comments-fetcher",
    "source_id": "8a4e1c27-5d3b-4f60-b9a2-7e0c6d1f3a58",
    "platform_id": "7246999999999999888",
    "idempotency_key": "linkedin:comment:7246999999999999888",
    "post_ref": "7246999999999999999", "series_step": "+24h",
    "job_id": "01J9N4H6P3R8T1V5X7Z0C2DMKE", "attempt": 1,
    "fetched_at": "2026-10-07T08:43:19Z",
    "retention_class": "linkedin_48h",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/amber/linkedin/2026/10/07/li-post-comments-fetcher/000011.jsonl.zst",
    "identity": "hashed"
  },
  "payload": { "...": "the comment object from 5.4 after hashing" }
}
```

Where the Actor gives no comment id, the key is `linkedin:comment:<post_id>:<sha256(created_time + text)>`. Also `deletions` (reason `platform_sync`), the job result, `service_runs`, `dlq.li-post-comments-fetcher` after 5 failed attempts.

### 6.3 State

The marker and running total in the series state; `cursors` carries `last_success_at`, `last_error`, `consecutive_errors` for (source, service); `budgets` counters for `li_vendor_post_comments`; in memory only backoff state.

## 7. Limits, quotas and cost

- **Vendor cost.** harvestapi on Apify is about USD 225 to 300 a month at 0.15M LinkedIn items for all its use, about USD 1.50 to 2.00 per 1,000 items, shared by the vendor services of this platform. Comments are the most numerous items, so this service carries the largest share risk; its tag is `li_vendor_post_comments`, one unit per returned item, and the per-run cap is the main brake. The split is set in `budgets` and measured in the pilot.
- **Restricted-use facts (LinkedIn terms).** Member social-activity data stored at most 48 hours; most member profile data 24 hours; organization social activity data six weeks (six months if authenticated); no social-feed use; member data never exported or transferred to clients, client-facing output is aggregated.
- **Retention.** Comments are member data, so they carry `linkedin_48h`, the stricter option, until legal decides whether the vendor contract and our author notice allow `vendor_agreed` (section 14). Held comment rows, per-comment analysis rows and raw objects are purged after 48 hours; unique-commenter counts, comment counts and sentiment aggregates per post are computed before the purge and kept ten years.
- **Governance.** Amber provenance is disclosed to clients and excluded from government contracts. Apify rate and concurrency limits: to be measured in the pilot.

## 8. Failure handling and fallback

- HTTP 429 or a vendor rate-limit response: backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts `dlq.li-post-comments-fetcher` and an alert.
- HTTP 401 or 403 from Apify: route marked `degraded`, batch stopped, alert; no key or IP rotation.
- Run `FAILED`, `TIMED-OUT` or `ABORTED`: transient, same backoff, marker untouched.
- Empty dataset for a post whose count is above zero: counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. No second vendor exists, so `fallback_on` is never set; ops can turn the flag off.
- Unknown shape: the item is archived under the 48-hour prefix with identity-like keys redacted (name, headline, picture, any string containing `linkedin.com/in/`) and the batch is parked as `schema_unknown`.
- Identity guard: a pre-produce check rejects any payload with such keys; the batch stops and an alert fires.

## 9. Non-functional requirements

- Throughput: comment items per month within the share of 0.15M that `budgets` assigns; posts and comments per post are to be measured in the pilot.
- Latency: a step completes within a lateness tolerance of `due_at` (to be set in the pilot).
- Privacy: no identity field leaves the service; every `linkedin_48h` row gone within 48 hours of `fetched_at`.
- Idempotency: `linkedin:comment:<platform_id>`; replayable jobs; scaling on partition lag with Apify concurrency capped by an environment variable.
- Security: Apify token and the hashing salt from Supabase Vault, never logged; no account pools, no proxies.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `apify_runs_total{status}`, `items_seen_dropped_total`, `steps_dropped_budget_total`, `identity_guard_blocked_total` and `budget_used_ratio`. Alerts: `series_behind`, `budget_80pct`, `route_degraded`, `identity_guard_blocked`, `dlq_nonempty`, `empty_200_rate`. SLO: series completed on time for 95% of posts.

## 11. Dependencies

listening-sdk, comment-decay-scheduler, li-company-posts-poller, li-post-search, quota-governor, normalize-item, aggregator, analysis-sentiment, analysis-topics, retention-purger, raw-archiver, backfill-orchestrator, source-health-canary, Supabase Postgres and Vault, ClickHouse (read), Redpanda; externally Apify and the harvestapi `linkedin-post-comments` Actor.

## 12. Risks and mitigations

- Cost: comments dominate vendor items; per-run cap, budget tag, hot-post extras cut first, steps dropped rather than overspent.
- Identity leaks into the archive: hashing at the edge plus the pre-produce guard and the redacted quarantine path.
- Incomplete Actor output: no deletions are inferred from a run that hit its cap.
- Legal reading of vendor comments: the strict class is the default until decided.
- Vendor withdrawal: optional behind the flag; the green route is unaffected. The harvestapi publisher's ownership is not verified in the clearance list (Apify, Czechia, is cleared): verify before launch.

## 13. Acceptance criteria

1. With `LI_VENDOR_ROUTE = off` no job runs and no Apify call is made; steps due while it was off are acknowledged `skipped_flag_off` and are not replayed after it is switched on.
2. A post first seen at 08:41 receives comments jobs due at +24 h and +3 d only, emitted by comment-decay-scheduler; none at +1 h, +6 h or +7 d.
3. A post whose page has only government clients is acknowledged `skipped_government` and no run starts.
4. A +3 d fetch adding 25% new comments schedules fetches every 2 days to day 30; adding 19% does not; an extension fetch adding 2 of 100 reports them and cancels nothing itself, comment-decay-scheduler applying early stop (ADR-0019).
5. A fetch implying 120 new comments an hour inserts hourly extras for 6 hours; at 80% of the monthly budget quota-governor denies the extras while series steps still run.
6. No `raw.items` message contains a commenter name, headline, profile link or picture; `author.ref` is identical for the same commenter across runs; an unknown-shape item is archived redacted under the 48-hour prefix.
7. An edited comment yields a message with the same key and a new hash; a held comment missing from a run that returned fewer items than max items yields one `deletions` message; a run that hit max items yields none.
8. `cost_units_total` equals the dataset items read, and no run's max items exceeds the cap in `budgets`.
9. The marker does not advance when a run is `FAILED` or `TIMED-OUT`; a replay yields messages with the same keys and one stored item per comment.
10. Five consecutive 429 responses send the job to `dlq.li-post-comments-fetcher` with the backoff logged; a 403 marks the route `degraded` and no second key is tried.
11. With a simulated clock every `linkedin_48h` row and raw object is deleted within 48 hours of `fetched_at` while the post's aggregates remain.
12. A denied step still unserved 24 hours after `due_at` is dropped and counted in `steps_dropped_budget_total`.

## 14. Open questions

1. Should vendor comment text carry `linkedin_48h` (proposed) or `vendor_agreed` (24 months)? For legal; shared with li-post-search question 2.
2. Does the Actor return comment ids, timestamps and a sort option? This decides the marker and newest-first reading; to be confirmed in the pilot.
3. Is a run below its max items a complete thread? Needed for deletions; to be measured in the pilot.
4. Should posts matched by keyword (li-post-search) get a series? Default no, pending the budget.
5. Are minimized records acceptable in `raw.items` (the one departure from "exactly as returned")? To confirm with the raw-archiver owners.
6. Owner and country of the harvestapi publisher: to be verified before launch.
