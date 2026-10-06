# li-own-comments-fetcher

**Platform:** LinkedIn · **Route:** green · **Lane:** Comments · **Owner:** Backend lead, LinkedIn adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A post on a company page is half of the story; the other half is what people answer. For a client's own LinkedIn page the answers are the reputation signal: praise, complaints, questions, job seekers, partner reactions. li-own-comments-fetcher reads those comments through the Community Management API, Comments API, on the posts that li-client-posts-poller found. That API reaches only pages the client administers: the organization must grant ADMINISTRATOR, DIRECT_SPONSORED_CONTENT_POSTER or CONTENT_ADMIN.

Without it the product knows that the client posted but not what the audience said: no sentiment, no themes, no early warning on a post that turns hostile, and li-notification-receiver would be the only source, with no safety net for a missed webhook. The comments are member data under LinkedIn's terms, so this service is also where the strictest rule of the product is applied: a comment is stored for at most 48 hours, then only its aggregates survive.

## 2. Objective (the end state this service delivers)

Every post of every client-administered page has its comments fetched at +6 h, +24 h and +3 d after it is first seen, plus a daily reconciliation while the post is younger than 7 days, each comment held for at most 48 hours and turned into aggregates before it is purged, and no member-level datum shown or sent outside the application. Target: comment series completed on time for 95% of posts; zero `linkedin_48h` rows older than 48 hours in any store; hourly aggregates available within one hour of each fetch.

## 3. Scope

### In scope

- Executing comment jobs (kind `comments`) for client posts: series steps, the daily reconciliation, hot-post extras, extension steps, client-requested refreshes, and the one-off job per backfilled post from backfill-orchestrator.
- Paging, replies, content-hash comparison for edits and deletions, writing `raw.items` (kind `comment`) under `linkedin_48h`, reporting `new_count`, `seen_count`, `pages`, `cost_units` to comment-decay-scheduler.

### Out of scope

- Emitting jobs (comment-decay-scheduler only), posts (li-client-posts-poller), live events (li-notification-receiver), comments on third-party posts (li-post-comments-fetcher, amber).
- Purging (retention-purger does it; this service tags the data), aggregation (aggregator), sentiment and topics (analysis-sentiment, analysis-topics).
- Commenters are individuals: never sources, never profiled, not passed to poster-resolver or qualifier. Reactor identity is not fetched.

## 4. Users and consumers

- **Clients** see aggregates (counts, sentiment shares, themes per post) and, inside the application only, the comment text during its 48-hour life.
- **Ops** watches series lateness, token and grant health, purge age and the DLQ.
- **Downstream**: normalize-item, aggregator, analysis-sentiment, analysis-topics, alert-evaluator (alerts carry counts and themes, never text), comment-decay-scheduler, retention-purger, raw-archiver, quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Jobs on `jobs.li-own-comments-fetcher`, partitioned by `source_id`, emitted only by comment-decay-scheduler: `kind = comments`, `post_ref` (the post URN), `series_step`, `due_at`, `attempt`. This service has no scheduler of its own.

**Series for LinkedIn client posts.** After a post is first seen: +6 h, +24 h, +3 d. Replies come in the same call; there is no reply threshold and no separate replies job.

**Early stop.** From the second fetch of a post onward, when a fetch adds fewer than 5% new comments and fewer than 5 absolute, the remaining series is cancelled. The percentage is `new_count` over the post's total comment count as the API reports it, not over comments held, because held comments expire at 48 hours.

**Extension.** When the last scheduled fetch (+3 d) still adds 20% or more new comments, the series continues every 2 days until day 30.

**Hot posts.** When velocity exceeds 100 new comments an hour (fetch deltas plus li-notification-receiver events), an extra fetch is inserted every hour for the next 6 hours.

**Daily reconciliation.** While a post is younger than 7 days, comment-decay-scheduler emits one reconciliation job a day when the latest comment count for the post (from li-client-posts-poller, through `item.metrics`) differs from its running total of comments seen (a number kept in the series state, no member data). A difference means a missed webhook or a missed fetch. A reconciliation job reads the whole thread and is where deletions and edits of held comments are detected. This is the safety net li-notification-receiver relies on.

**Paging and the stop marker.** A fetch pages until it reaches comments older than the newest one already seen (newest-first), or until the page token is exhausted (oldest-first). Because member data expires at 48 hours, the marker is the series state's `newest_comment_at` when no comment is held. A comment older than the marker that is no longer held is never re-ingested, not even on a full read: we do not rebuild a purged record.

**Beyond day 30 and backfill.** No automatic fetches after day 30; a client can request a refresh of one post, budget permitting. For posts of a newly added page (last 30 days) backfill-orchestrator emits one comments job each, so historical aggregates exist; their text lives 48 hours like any other.

**Catch-up.** Jobs are taken in `due_at` order, oldest due first. A late job is still correct: it reads from the marker.

### 5.2 Step by step

1. Consume a job; read the `sources` row; stop if `health = blocked`. Take the client's token from Supabase Vault for this job only.
2. Ask quota-governor for allowance under `budget_tag = linkedin_cm:<client_id>`; on wait-until requeue; on deny count `quota_denied_total` and report the step late.
3. Read the marker from the series state and, from ClickHouse `comments`, the ids and content hashes of the post's held comments (younger than 48 hours).
4. Page through the Comments API for the post (5.3) until the stop condition.
5. For each comment: not held and newer than the marker means new; held with the same hash means seen; held with a different hash is an edit, written with the same key and a new hash (normalize-item stores a new version). On a full read, a held comment missing from the response becomes a `deletions` message with reason `platform_sync`. A fetch that stopped at the marker infers no deletions.
6. Write `raw.items` (kind `comment`, `retention_class = linkedin_48h`). raw-archiver lands the batch under `raw/green/linkedin/<yyyy>/<mm>/<dd>/li-own-comments-fetcher/`, a prefix on which retention-purger applies the 48-hour rule to the raw copy too.
7. After Redpanda acknowledges, report `new_count`, `seen_count`, `pages`, `cost_units` and the new `newest_comment_at` to comment-decay-scheduler, which applies early stop, extension and the hot-post rule.

### 5.3 The call it makes

Comments API on the post URN, with the client's OAuth token (scope `r_organization_social`; whether comments need a further scope is to be confirmed in the pilot). Path, `Linkedin-Version` value, page parameters and sort order are to be confirmed in the pilot:

```
GET <Comments API, comments of a post>
  object=<post URN>   count=<page size: API maximum, to be confirmed>   start=<offset or token>
  Authorization: Bearer <client's OAuth token>
  Linkedin-Version: <pinned in one environment variable shared by all li-* services>
```

Replies are requested in the same call where the API offers expansion. If the API is oldest-first the fetch pages to exhaustion and deduplicates by id and hash.

### 5.4 What it gets

Per comment (illustrative; field names to be confirmed in the pilot):

```json
{
  "id": "urn:li:comment:(urn:li:share:7247000000000000001,7247000000000000099)",
  "object": "urn:li:share:7247000000000000001",
  "actor": "urn:li:person:AbCdEfGh12",
  "message": {"text": "مبارك، نتمنى لكم التوفيق"},
  "created": {"time": 1791293400000}, "lastModified": {"time": 1791293400000},
  "parentComment": null,
  "likesSummary": {"totalLikes": 2}
}
```

The commenter arrives as a person URN and whatever display fields the API returns (to be confirmed). What it does not get: reactor identity, private messages, comments on posts of pages without a valid grant.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.li-own-comments-fetcher`; `sources`, `cursors`, `clients` (token reference), `budgets` through quota-governor; the series state (marker, running total); ClickHouse `comments` (id, content hash and time of the post's held comments, read-only); `health` through the SDK canary hook.

### 6.2 Writes

`raw.items`, one message per new or changed comment:

```json
{
  "envelope": {
    "platform": "linkedin", "kind": "comment", "route": "green", "vendor": null,
    "service": "li-own-comments-fetcher",
    "source_id": "3d2f8a14-6b7c-4e19-8a05-c1f7e2b94d36",
    "platform_id": "urn:li:comment:(urn:li:share:7247000000000000001,7247000000000000099)",
    "idempotency_key": "linkedin:comment:urn:li:comment:(urn:li:share:7247000000000000001,7247000000000000099)",
    "post_ref": "urn:li:share:7247000000000000001", "series_step": "+6h",
    "job_id": "01J9N3F8T2K5W7Y1B4C6D0RGMA", "attempt": 1,
    "fetched_at": "2026-10-06T13:33:02Z",
    "retention_class": "linkedin_48h",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/linkedin/2026/10/06/li-own-comments-fetcher/000019.jsonl.zst"
  },
  "payload": { "...": "the comment object from 5.4, unchanged" }
}
```

Also `deletions` (reason `platform_sync`), the job result to comment-decay-scheduler, `service_runs`, `dlq.li-own-comments-fetcher` after 5 failed attempts.

### 6.3 State

No per-source cursor of its own: the marker and running total sit in the series state owned by comment-decay-scheduler; `cursors` carries `last_success_at`, `last_error`, `consecutive_errors` for (source, service); `budgets` counters per client token.

## 7. Limits, quotas and cost

- **Restricted-use facts (LinkedIn terms).** Member social-activity data stored at most 48 hours; most member profile data 24 hours; organization social activity data six weeks (six months if authenticated); no social-feed use; member data never exported or transferred to clients, client-facing output is aggregated.
- **What that means here.** Comment text, commenter references and raw batches carry `linkedin_48h`; the purge clock starts at each copy's `fetched_at`. retention-purger deletes the rows in `comments`, the per-comment rows in `analysis` and the raw objects. aggregator computes hourly aggregates (comments per post per hour, sentiment shares, themes) before the purge; aggregates and derived post-level scores are kept ten years.
- **Never shown outside the application.** No CSV, API, report, e-mail or alert carries comment text or a commenter reference; the application shows them to the client's own users, inside its screens, for their 48-hour life.
- **Quota and cost.** Tag `linkedin_cm:<client_id>`, one unit per API call; LinkedIn's limits are not in our fact sheet and are to be measured in the pilot. No per-call fee is listed (USD 0 as far as the fact sheet shows).

## 8. Failure handling and fallback

- HTTP 429: backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts `dlq.li-own-comments-fetcher` and an alert.
- HTTP 401 or 403: stop the batch; if the same token succeeded on another page recently the page is `blocked` (role removed), otherwise the token is `degraded`; alert; no token or IP rotation.
- A post that no longer exists (404): series cancelled; the deletion is li-client-posts-poller's to mirror.
- Empty 200 for a post whose count is above zero: counted per route; above 5% in 15 minutes the canary flips `health = degraded`. No amber fallback: a client's own comments are never fetched through the vendor route.
- Schema change: payload archived, `schema_unknown`, batch parked. Partial write: the marker moves only after acknowledgement; replays deduplicate.

## 9. Non-functional requirements

- Throughput: comment volume of client pages is to be measured in the pilot; LinkedIn is 0.15M of 30.5M items a month in total.
- Latency: each step completes within a lateness tolerance of `due_at` (to be set in the pilot); aggregates within one hour of a fetch.
- Privacy: every `linkedin_48h` row gone within 48 hours of `fetched_at`.
- Idempotency: `linkedin:comment:<platform_id>`; replayable jobs; scaling on partition lag.
- Security: tokens from Supabase Vault per job, never logged; no account pools, no proxies.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `comments_deleted_total`, `series_steps_late_total`, `reconcile_jobs_total` and `held_rows_oldest_age_seconds`. Alerts: `series_behind`, `member_data_overdue` (any `linkedin_48h` row older than 48 hours), `token_degraded`, `grant_lost`, `dlq_nonempty`, `empty_200_rate`. SLO: series completed on time for 95% of posts.

## 11. Dependencies

listening-sdk, comment-decay-scheduler, li-client-posts-poller, li-notification-receiver, backfill-orchestrator, normalize-item, aggregator, analysis-sentiment, analysis-topics, retention-purger, raw-archiver, quota-governor, source-health-canary, Supabase Postgres and Vault, ClickHouse (read), Redpanda.

## 12. Risks and mitigations

- A late purge is a terms breach: purge age is a gauge and an alert; the raw prefix has its own rule.
- Analysis must finish inside the window: aggregator and analysis workers run hourly, and a comment not analyzed within 24 hours raises an alert.
- Webhook and fetch overlap: deduplicated by key and hash.
- Unknown API ordering and rate limits: both handled by the oldest-first path and by measuring in the pilot.
- Few commenter fields returned: the application shows what exists; nothing is enriched from elsewhere.

## 13. Acceptance criteria

1. A post first seen at 08:00 receives comments jobs due at +6 h, +24 h and +3 d from comment-decay-scheduler only; this service emits none.
2. A +24 h fetch adding 3 new of 100 total cancels the +3 d step; adding 4 of 40 does not; adding 5 of 200 does not (absolute threshold).
3. A +3 d fetch adding 25% new comments schedules fetches every 2 days to day 30; adding 19% does not.
4. A fetch pages until the marker on a newest-first fixture and to exhaustion on an oldest-first fixture; `new_count`, `seen_count`, `pages`, `cost_units` are reported.
5. An edited comment yields a second message with the same `idempotency_key` and a new hash; on a full read a held comment missing from the response yields one `deletions` message with reason `platform_sync`; a fetch that stopped at the marker yields none.
6. With a simulated clock, every `linkedin_48h` row, per-comment analysis row and raw batch object is deleted within 48 hours of `fetched_at`, while the post's hourly aggregates remain.
7. A purged comment older than the marker is not re-ingested by a full read.
8. No export, report, API response or alert payload in the test suite contains comment text or a person URN of a `linkedin_48h` comment.
9. The marker does not advance when the Redpanda produce fails; the replay re-emits and normalize-item stores one item.
10. A simulated 429 backs off from 30 s to 15 min and after 5 attempts reaches `dlq.li-own-comments-fetcher`; a 403 on one page blocks only that page; a 401 degrades the token.
11. A reconciliation job is emitted only when the stored count and the running total differ, and only for posts younger than 7 days.

## 14. Open questions

1. Ordering, paging and reply expansion of the Comments API: to be confirmed in the pilot.
2. Does the 48-hour clock run from our `fetched_at` (assumed here) or from the comment's creation? For legal; creation would shorten the window.
3. Which member fields does the API return, and what can the application therefore show?
4. Per-comment derived scores: purged with the text (proposed) or kept as derived scores for ten years? For legal.
