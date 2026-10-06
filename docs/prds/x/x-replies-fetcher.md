# x-replies-fetcher

**Platform:** X · **Route:** green · **Lane:** Comments · **Owner:** Backend lead, X adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

On X, the reaction to a post lives in its replies: people answer a ministry's announcement, argue with an outlet's headline or complain to a brand in public. x-replies-fetcher reads those replies through the official X API v2 and keeps every registered post's replies current during the week the conversation is alive, which is also the only week recent search can see.

Without it, X in the product is a list of posts with counts: no sentiment or topics on the answers, no "what are people replying to our campaign", no hot-thread signal for alerts. It is also where three X rules are applied first: reply authors who are individuals enter the system only as hashed references, every reply carries `x_24h_sync` so deletions can be mirrored, and every read passes the UTC-day read ledger so the same post is never paid twice in a day.

## 2. Objective (the end state this service delivers)

Every post in an open reply series has each step fetched when due; every reply that recent search returns for the conversation reaches `raw.items` by the next step, with its parent post id and conversation id; edits arrive as new versions; nothing is deleted on absence; comment-decay-scheduler receives an exact report for every job. Target: 95% of posts complete their series on time (each step finished before the next falls due; the +3 d step and extensions within 24 hours of falling due and always inside the 7-day window), zero jobs lost, zero calls without a quota-governor allowance, zero post reads paid twice in one UTC day, zero messages carrying an individual's X id or username in clear.

## 3. Scope

### In scope

- Executing `comments` jobs from `jobs.x-replies-fetcher`: series steps, extensions, hot-post extras, client refreshes inside the 7-day window.
- Paging recent search by `conversation_id:` from the newest stored reply; read-ledger marking; nested replies; edit versions.
- Author minimization, source links for registered authors, government-client gating, the per-post reply index, the job report.

### Out of scope

- Deciding when to fetch (comment-decay-scheduler); replies older than 7 days (x-full-archive-search, on a client request only).
- Finding posts (x-user-timeline-poller, x-filtered-stream, x-recent-search); post metrics.
- Deletions (x-compliance-sync, then deletion-propagator); deduplication (normalize-item); `item.hits` and `discovery.hits` (keyword-matcher).
- Quote posts, until the pilot decides (question 2).
- Reply-author profiles and source discovery from reply authors: never built here.

## 4. Users and consumers

- **Clients** see "what people answered under the posts I watch, through the post's first week" and can request a refresh inside the window.
- **Ops** watch paid reads against the monthly cap, series lateness, coverage gaps and the DLQ.
- **Downstream**: normalize-item and store-writer (ClickHouse `comments`, keyed by `parent_id`), keyword-matcher, comment-decay-scheduler (`jobs.completed`), raw-archiver, deletion-propagator, quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.x-replies-fetcher`, partitioned by `source_id`, with kind `comments`, `post_ref`, `series_step`, `due_at` and `attempt`. Only comment-decay-scheduler emits these jobs; it keeps one `comment_series` row per post and advances or ends it from the `jobs.completed/v1` event the listening-sdk job wrapper writes when this service finishes. X needs no separate `replies` jobs: `conversation_id:` returns every depth of a thread. This service runs no scheduler.

**Which posts.** A series opens when an X post first reaches `items.normalized`: posts of registered accounts (x-user-timeline-poller, x-filtered-stream) and posts found by x-recent-search under a keyword-rule source. Only conversation roots (the post's `conversation_id` equals its id) are fetched; a post that is itself a reply already belongs to another conversation.

**Series.** +1 h, +6 h, +24 h, +3 d after the post is first seen; no +7 d step, because the recent-search window ends at 7 days. Early stop: a fetch adding under 5% new replies and under 5 absolute cancels the rest; armed only once the post has 5 or more stored replies or after the +24 h step. Extension: when the last step adds 20% or more, a fetch every 2 days while still inside the 7-day window (in practice +5 d). Hot posts: above 100 new replies an hour, an extra hourly fetch for 6 hours. After the window, nothing is automatic; older replies come only through x-full-archive-search on a client request.

**Staying on time.** Workers scale on partition lag; a post is in at most one job at a time. A late step still reads everything newer than the newest stored reply, so lateness costs freshness, not completeness, while the step stays inside the window. When budget is short, quota-governor's priorities decide (section 7).

**Backfill.** None separate: a post's first fetch reads everything the window holds. A post first seen more than 7 days after it was created (backfill-orchestrator, x-full-archive-search) gets what the window allows and is marked `window_partial`.

### 5.2 Step by step

1. Consume a job; read the `sources` row (`retention_class`, `client_ids`, `health`) and the post's index row; stop if `health = blocked`. Not a conversation root: status `not_root`, no call. Post older than 7 days on a refresh: status `outside_window`, no call.
2. Read `clients` for `client_ids`: government end users stay on the job only when the company app's X plan setting is Enterprise; none left: status `not_permitted`, no call.
3. Ask quota-governor for allowance (`x_pay_per_use`, sub-counter `post_reads`, priority from `series_step`). On wait-until, requeue for that time; on deny, no call, count `quota_denied_total`, status `quota_denied`.
4. Fetch the company app's bearer token from Supabase Vault for this job only.
5. Request a page (5.3). Mark each returned post in the read ledger (`x:post:<id>`): first read of the UTC day `paid = true`, repeats `paid = false`; returned user objects count under `user_reads` the same way.
6. `content_hash` = sha256 of `text`; classify `new`, `edit` (`edit_history_tweet_ids` lists a stored id; behaviour to be confirmed in the pilot) or `seen`.
7. Minimize: an `author_id` that is a registered source becomes `author_source_id` (with `author_is_source` when it is the post's own account); any other becomes `author_ref`, an HMAC-SHA256 keyed from Vault and scoped to the post's source. `in_reply_to_user_id` and `entities.mentions` ids are mapped the same way. `includes.users` is dropped.
8. Set `parent_post_id` and `conversation_id` (the root) and `parent_comment_id` (the `replied_to` id when it is not the root); write one `raw.items` message per reply; raw-archiver lands the batch under `raw/green/x/<yyyy>/<mm>/<dd>/x-replies-fetcher/`.
9. Paging: follow `next_token` until none (complete) or the page cap (value set in the pilot from the budget): the post is marked `partial` and the gap between the old floor and the oldest reply read is recorded.
10. After Redpanda acknowledges: update the index and `cursors`; return the report (`new_count`, `seen_count` with edits included, `pages`, `cost_units` = paid post reads, plus `paid_user_reads`, `capped`, `window_partial`).

### 5.3 The call it makes

```
GET /2/tweets/search/recent
  ?query=conversation_id:<post id> -is:retweet
  &since_id=<newest stored reply>      (omitted when none is stored)
  &max_results=100
  &tweet.fields=created_at,public_metrics,conversation_id,lang,entities,in_reply_to_user_id,referenced_tweets
  &expansions=author_id
  &next_token=<token>                  (omitted on the first page)
```

Auth: the company app's bearer token (app-only), from Supabase Vault per job; no user context. Page size: `max_results=100`. Pagination: `meta.next_token` becomes `next_token`; no token means the end. Cost: USD 0.005 per post read. Anything else (host, sort order, `until_id` to close gaps, `tweet.fields=author_id` instead of the expansion, a quote query) is to be confirmed in the pilot.

### 5.4 What it gets

Per reply: `id`, `text`, `edit_history_tweet_ids`, `created_at`, `public_metrics`, `conversation_id`, `lang`, `entities`, `in_reply_to_user_id`, `referenced_tweets`, `author_id`; `includes.users` (`id`, `name`, `username`); `meta` (`newest_id`, `oldest_id`, `result_count`, `next_token`). Example, user objects omitted:

```json
{
  "data": [{
    "id": "1975210483926617088", "conversation_id": "1975163027415552001",
    "author_id": "1630094875512037376", "in_reply_to_user_id": "1102938475647382016",
    "created_at": "2026-10-06T18:22:41.000Z", "lang": "ar",
    "text": "الانترنت يطفي كل ليلة بعد الساعة ١٢، شوكت يتصلح؟",
    "referenced_tweets": [{"type": "replied_to", "id": "1975163027415552001"}],
    "public_metrics": {"retweet_count": 0, "reply_count": 2, "like_count": 9, "quote_count": 0}
  }],
  "meta": {"result_count": 1, "newest_id": "1975210483926617088"}
}
```

What it does not get: replies older than the window; quote posts (separate conversations); deletions (x-compliance-sync); anything X search leaves out, since search is not a complete listing; profiles of authors.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.x-replies-fetcher`; `sources`, `clients`, `cursors`; `budgets` and the read ledger through quota-governor; `health` through the SDK canary hook; the reply index; the bearer token and author-hash key from Supabase Vault.

### 6.2 Writes

`raw.items`, one message per reply, envelope plus the record as returned minus the removed fields:

```json
{
  "envelope": {
    "platform": "x", "kind": "comment", "route": "green", "vendor": null,
    "service": "x-replies-fetcher",
    "source_id": "7c2e9a41-3b6d-4f8e-a1c5-0d9b2e6f4a73",
    "platform_id": "1975210483926617088",
    "idempotency_key": "x:comment:1975210483926617088",
    "ledger_key": "x:post:1975210483926617088", "paid": true,
    "parent_post_id": "1975163027415552001", "conversation_id": "1975163027415552001",
    "parent_comment_id": null,
    "author_ref": "hmac:8d3f0a6c1e9b4d27a5f1", "author_source_id": null, "author_is_source": false,
    "in_reply_to_ref": "source:7c2e9a41-3b6d-4f8e-a1c5-0d9b2e6f4a73",
    "content_hash": "sha256:4b8e1d7c0a3f9e2b6d5c8a1f7e4b0d3c9a6f2e8b5d1c7a4f0e3b9d6c2a8f5e1b",
    "observation": "new",
    "job_id": "01J9Q2M7T4X8B1R6V0Z3N5K9WD", "attempt": 1, "series_step": "+6h",
    "fetched_at": "2026-10-06T18:31:07Z",
    "retention_class": "x_24h_sync",
    "client_ids": ["5e1a7c3d-9b2f-4d6e-8a0c-3f7b1e9d2a64"],
    "batch": "raw/green/x/2026/10/06/x-replies-fetcher/000112.jsonl.zst",
    "removed_fields": ["author_id", "in_reply_to_user_id", "entities.mentions.id", "entities.mentions.username", "includes.users"]
  },
  "payload": { "...": "the reply from 5.4 without the removed fields" }
}
```

`series_step` is passed through as comment-decay-scheduler labels it. Also: `service_runs`, `dlq.x-replies-fetcher` after 5 failed attempts. No `deletions`, no `discovery.hits`.

### 6.3 State

The reply index (Supabase Postgres, owned by this service): per reply `post_id`, `reply_id`, `parent_comment_id`, `content_hash`, `first_seen_at`; per post `is_root`, `post_created_at`, `newest_reply_id`, `stored_count`, `last_complete_fetch_at`, `partial` with gap bounds, `window_partial`. No text, no author. Rows removed by deletion-propagator when x-compliance-sync reports a deletion. `cursors` per (`source_id`, `x-replies-fetcher`): `last_success_at`, `last_error`, `consecutive_errors`. The read ledger belongs to quota-governor. In memory: backoff state only.

## 7. Limits, quotas and cost

- X pay-per-use: USD 0.005 per post read (a reply is a post), USD 0.010 per user read, deduplicated per resource per UTC day; hard cap 3,000,000 post reads a month, shared by every x-* service through `x_pay_per_use` (sub-counters `post_reads`, `user_reads`).
- Because each step starts from the newest stored reply, a reply is normally read once: about USD 0.005 per stored reply (USD 5 per 1,000). If the `author_id` expansion is billed as user reads, a reply by an author not yet read that day costs up to USD 0.015, three times as much (to be confirmed in the pilot, question 1).
- Scale check: X's full-scale volume is 0.6M items a month; read once each, that is 600,000 post reads (USD 3,000), 20% of the cap. The replies' share and re-read rate are to be measured in the pilot.
- Priorities: 2 = +1 h, +6 h, +24 h; 3 = +3 d, extensions and refreshes; 4 = hot-post extras. From 80% of the month's budget (stretch) quota-governor admits 1 to 3, so hot extras stop first; from 95% only 1 and 2.
- Terms: no surveillance, no monitoring of sensitive events (protests, rallies), no profiling on sensitive attributes; a Government End User or a multi-client product requires Enterprise (pricing not in the fact sheet); deletions mirrored within 24 hours (`x_24h_sync`).

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.x-replies-fetcher` and an alert fires.
- HTTP 401 and 403: mark the token `degraded`, stop the batch, alert; never switch to another app, token or IP.
- HTTP 400 on `since_id` (for example an id outside the window or of a deleted reply): behaviour to be confirmed in the pilot; proposed retry once with the next-newest stored id, then status `cursor_rejected`.
- Empty 200: zero results after `since_id` is normal. A first fetch returning nothing for a post whose `reply_count` is above zero counts as empty; above 5% in 15 minutes source-health-canary flips `health = degraded`. X has no amber route, so `fallback_on` is never set.
- Absence is never deletion: a stored reply missing from a later fetch keeps its row; deletions come only from x-compliance-sync.
- Schema change: payload archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: the index and `cursors` change only after acknowledgement; a replay restarts from the same `since_id`, and the ledger returns `paid = false` for that day's repeats.

## 9. Non-functional requirements

- Throughput: X totals 0.6M items a month at full scale; posts in open series and jobs a day are to be measured in the pilot. Budget, not compute, is the ceiling; X request rate limits to be confirmed in the pilot.
- Latency: a public reply reaches `raw.items` at the next step plus fetch time; the first replies within about an hour of the post being seen.
- Idempotency: `x:comment:<id>` plus `content_hash`; ledger check-and-mark atomic in quota-governor; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag; no leader election.
- Security and privacy: token and HMAC key from Vault per job, never logged; reply text and X user ids never logged; the only query is `conversation_id:` of a registered post, so the service cannot be aimed at a person, place or event; no account pools or proxies; provenance on every message.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds` (now minus `due_at` of the most overdue queued job), `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `post_reads_paid_total`, `post_reads_repeat_total`, `user_reads_paid_total`, `series_step_lateness_seconds`, `versions_total`, `window_partial_total`, `fetch_capped_total`, `reply_coverage_ratio` (stored replies over the parent's `reply_count`), `x_error_total{status}`. Alerts: `series_late` (on-time share below 95% over a day), `token_degraded`, `dlq_nonempty`, `empty_200_rate`, `quota_deny_rate`, `coverage_gap`. SLO: series on time for 95% of posts; zero jobs lost.

## 11. Dependencies

listening-sdk (job wrapper, idempotency, quota and canary hooks), comment-decay-scheduler, quota-governor (budget and read ledger), source-health-canary, raw-archiver, normalize-item, keyword-matcher, store-writer, deletion-propagator, x-compliance-sync; upstream x-user-timeline-poller, x-filtered-stream, x-recent-search; x-full-archive-search for older replies; Supabase Postgres and Vault; Redpanda. X prerequisites: the company developer app on pay-per-use with a bearer token; Enterprise, with end users named at use-case review, before any government client or several clients.

## 12. Risks and mitigations

- Viral threads drain the shared cap: priority ladder, early stop, page cap, hot extras dropped first.
- Search is not a complete listing: `reply_coverage_ratio` monitored; disclosed in provenance; no deletion inferred.
- A late step falls outside the window: series ends by +3 d (+5 d with extension), well inside 7 days; lateness alerted.
- Misuse as surveillance: no author, place or keyword queries; individuals hashed per source; no discovery from repliers; government gating in step 2.
- Plan risk: the product is multi-client, so Enterprise is needed before broad rollout.

## 13. Acceptance criteria

1. Against a simulated API, a post with 40 stored replies and 12 new ones sends `since_id` = the newest stored id and reports `new_count = 12`, `seen_count = 0`, `pages = 1`, `cost_units = 12`.
2. A first fetch with nothing stored omits `since_id`, requests 3 pages for 230 replies, ends with no `next_token` and sets `last_complete_fetch_at`.
3. A reply already read today by x-recent-search is written with `paid = false` and excluded from `cost_units`; read again after 00:00 UTC it is `paid = true`.
4. A stored reply absent from a later complete fetch produces zero `deletions` messages and keeps its index row.
5. A reply whose `replied_to` id is another reply gets that id as `parent_comment_id`; `parent_post_id` and `conversation_id` equal the root.
6. No message, log line, DLQ message or archived batch contains an unregistered author's `author_id` or username; one author under posts of two sources gets two different `author_ref` values; a registered author carries `author_source_id`.
7. With quota-governor at 95%, +3 d and hot-extra jobs make zero calls while a +1 h job proceeds; at 80%, only hot extras are refused.
8. A job for a non-root post ends `not_root`, and a refresh for a post created 8 days ago ends `outside_window`, both with zero calls.
9. A post watched only by a government client while the plan is not Enterprise ends `not_permitted` with zero calls; with a brand client also watching, messages carry only the brand's id.
10. Every message carries `route = green`, `vendor = null`, `service`, `fetched_at`, `retention_class = x_24h_sync`, `parent_post_id`, `conversation_id`, `series_step` and `paid`.
11. A simulated 429 backs off from 30 s to at most 15 min with `attempt + 1`; after 5 attempts the job is in `dlq.x-replies-fetcher` and an alert fired; a 401 marks the token `degraded` and no other token is tried.
12. When the Redpanda produce fails, index and `cursors` are unchanged; the same-day replay reports the same `new_count` with `cost_units = 0`.

## 14. Open questions

1. Is the `author_id` expansion billed as user reads? If so, request `tweet.fields=author_id` instead and match registered authors by id. To be confirmed in the pilot.
2. Quote posts: capture them with a dedicated query, or leave them to x-recent-search? To be confirmed in the pilot.
3. Page-cap value and gap closing with `until_id` on capped fetches. To be confirmed in the pilot.
4. Status values (`quota_denied`, `not_root`, `outside_window`, `not_permitted`, `cursor_rejected`), the extension count, series for posts first seen after day 7 and for deleted parents must be aligned with comment-decay-scheduler.
5. A reply also delivered as a post by x-recent-search or x-filtered-stream arrives as `x:post:<id>`; normalize-item must decide how it links to `x:comment:<id>`.
6. Should unregistered repliers that may be organizations reach poster-resolver in clear for qualification, against the hash-first rule? Proposed: no.
7. How posts about protests or rallies are marked so comment-decay-scheduler never opens a series on them.
