# ig-comments-fetcher

**Platform:** Instagram · **Route:** amber (optional, flag `IG_VENDOR_ROUTE`) · **Lane:** Comments · **Owner:** Backend lead, Instagram adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The question clients ask most about a competitor's or an outlet's Instagram post is what people said under it. The green route cannot answer: Business Discovery returns only a comment count for media the client does not own (ig-account-media-poller), and the comments edge works only on client-owned media (ig-own-comments-fetcher). ig-comments-fetcher closes that gap by buying the comments on third-party media from SociaVault, a screened vendor that does the collection itself.

Without it the product shows that a rival's post drew 4,000 comments and cannot say whether they were praise, complaints or a rumor. It is, however, a bought, partial and optional route: it sees about the first 15 visible comments of a post, gives no replies, and its provenance is disclosed to clients. It is switched on only by `IG_VENDOR_ROUTE = sociavault`, and its data is excluded from government contracts.

## 2. Objective (the end state this service delivers)

For every selected third-party Instagram post, the first visible comments are re-read on the amber series (+6 h, +24 h, +3 d) and reach `raw.items` with hashed authors, at a vendor cost the quota-governor keeps inside the monthly `ig_vendor` budget. Target: series completed on time for 95% of selected posts, zero credits spent when the flag is off or the client is a government body, no commenter username stored anywhere.

## 3. Scope

### In scope

- Executing comment jobs on third-party Instagram media (posts from ig-account-media-poller, ig-hashtag-search and ig-keyword-search) while `IG_VENDOR_ROUTE = sociavault`.
- One vendor request per job; hashing authors before anything is written; content-hash versions for edited comments.
- Reporting `new_count`, `seen_count`, `pages`, `cost_units` for the early-stop and extension rules.
- Writing `raw.items` (kind `comment`) with `route = amber`, `vendor = sociavault`.

### Out of scope

- Comments on client-owned media (ig-own-comments-fetcher, green).
- Replies: the route has none.
- Deciding which posts get a series and when (comment-decay-scheduler, within qualifier rule 5); inferring deletions (impossible from a partial view).
- Posts and counts (ig-account-media-poller), keyword search (ig-keyword-search), government contracts (never served).

## 4. Users and consumers

- **Clients** that accepted the amber provenance statement see "what people said under other accounts' posts, a sample of the first comments". Government clients never receive this data.
- **Ops** owns the flag, watches vendor spend and the DLQ.
- **Downstream services**: normalize-item, keyword-matcher and the analysis services through `items.normalized`; comment-decay-scheduler (reads job results), quota-governor, source-health-canary, raw-archiver, deletion-propagator.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.ig-comments-fetcher`, partitioned by `source_id`, emitted only by comment-decay-scheduler. A job names one post (`post_ref`) and one `series_step`. The scheduler opens a series only when `IG_VENDOR_ROUTE = sociavault`, the post's `comments_count` is above zero, at least one client watching the source has accepted the amber provenance, no client on the source is a government client for this data, and the source's vendor spend is under its cap (qualifier rule 5). The service re-reads the flag at the start of every job and re-checks the client list; if either fails the job completes as `skipped` with no request and no cost.

**The series (amber, Instagram other media).** Counted from the moment the post is first seen: +6 h, +24 h, +3 d. There is no +1 h step because the vendor shows only the first visible comments, and a first read after 6 hours is enough to see them.

**Early stop.** When a fetch adds fewer than 5% new comments (new share = `new_count` over the comments stored before the fetch) and fewer than 5 absolute, the remaining series is cancelled; with about 15 visible comments this in practice means a fetch with no new comment. **Extension.** When the last scheduled fetch (+3 d) still adds 20% or more, the series continues every 2 days until day 30, and quota-governor may refuse each step. **Hot posts.** The rule (extra hourly fetch for 6 hours above 100 new comments an hour) is kept as written but cannot fire in practice, because one request shows about 15 comments; quota-governor drops hot extras first anyway when the monthly budget passes 80%.

**Paging.** One request returns the visible set (about 15 comments); whether the vendor can page further: to be confirmed in the pilot. The fetch stops when it meets a comment already stored or the vendor offers no further page.

**Edits and deletions.** Each comment carries a `content_hash` (SHA-256 of its text); a changed text under the same comment id is written as a new version. Deletions are never inferred: the visible set is partial and ranked by the vendor, so absence proves nothing. Removals arrive only through deletion-propagator (client, user or Meta request).

**Replies.** None: the route returns top-level comments only.

**Keeping every selected post on its series.** A failed job returns with `attempt + 1` and keeps its `due_at`; jobs run ordered by `due_at`, so late jobs go first and a post is never skipped twice in a row. A job that starts after the next step of its series is due counts as late and raises `series_behind`.

### 5.2 Step by step

1. Consume a job (`source_id`, `post_ref`, `kind` = comments | ops_force, `series_step`, `attempt`); read `IG_VENDOR_ROUTE`; if it is not `sociavault`, complete as `skipped`.
2. Re-check that no government client is on the source; resolve the post's `permalink` from ClickHouse `items` (read-only).
3. Ask quota-governor for allowance under `budget_tag = ig_vendor` (one request, 1 credit); on wait-until, requeue; on deny, count `quota_denied_total` and keep `due_at`.
4. Send one request to the vendor with the vendor key from `vendor_keys` (Supabase Vault, for this job only).
5. Hash each author (username and any id) with a keyed hash whose key sits in Supabase Vault; drop the clear values.
6. Compute `content_hash` per comment; compare with the stored comments of the post (ClickHouse `comments`, read-only); write unseen comments and new versions to `raw.items`.
7. After Redpanda acknowledges, record the job result (`new_count`, `seen_count`, `pages`, `cost_units`) and set `last_success_at`, `consecutive_errors = 0`.
8. Record metrics and the credits spent into `budgets`.

### 5.3 The call it makes

SociaVault's Instagram post-comments endpoint, one request per job at 1 credit. Endpoint path, parameter names and response fields: to be confirmed against the vendor's documentation in the pilot. What the request carries: the post's `permalink` (the shortcode form, if the vendor prefers it: to be confirmed); auth: the vendor API key from `vendor_keys`, sent as the vendor specifies. Page size: the visible set, about 15 comments; pagination: none expected (to be confirmed). The vendor is selected by `IG_VENDOR_ROUTE`; no other vendor is wired in.

### 5.4 What it gets

About the first 15 visible comments of the post: text, author, time and like count where the vendor supplies them (list to be confirmed in the pilot). Illustrative record, after hashing:

```json
{
  "text": "ما شاء الله، متى يبدأ التوصيل؟",
  "created_time": "2026-10-06T09:41:12+0000",
  "like_count": 2,
  "author_ref": "ah1:3f9c7a1e5b2d4086a7c1e9d3b5f08a42"
}
```

What it does not get: replies; comments beyond the visible set; deleted comments; commenter profiles; any Meta-supplied data.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.ig-comments-fetcher`; `sources`, `clients` (government flag, amber acceptance), `vendor_keys`, `budgets` through quota-governor, `health` through the SDK canary hook; `IG_VENDOR_ROUTE`; ClickHouse `items` (permalink) and `comments` (stored hashes), read-only.

### 6.2 Writes

`raw.items`, one message per comment. The vendor's record is unchanged except that author fields are replaced by `author_ref`:

```json
{
  "envelope": {
    "platform": "instagram", "kind": "comment", "route": "amber", "vendor": "sociavault",
    "service": "ig-comments-fetcher",
    "source_id": "c81f5a27-3d94-4be6-8a02-7e6b1f9d4c33",
    "platform_id": null,
    "idempotency_key": "instagram:comment:17912345678901234:b4c7e1d09a2f5836c1d8e7a0f3b95264d1c8a7e0f2b4693c5d1e8a7f0b2c4d96",
    "job_id": "01J9N5D2P8F4Y3A6W9S1V7KJTE", "attempt": 1,
    "fetched_at": "2026-10-06T16:02:31Z",
    "retention_class": "vendor_agreed",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/amber/instagram/2026/10/06/ig-comments-fetcher/000031.jsonl.zst",
    "post_ref": "17912345678901234", "parent_id": null, "series_step": "+6h",
    "content_hash": "sha256:2e7a9c41d05b38f6a1c4e9d7b0825f3a6c1d9e8b7a40f2c5d3e6b19a8c7f0d24"
  },
  "payload": { "...": "the comment object from 5.4" }
}
```

When the vendor returns a comment id, `platform_id` holds it and the key is `instagram:comment:<id>`; otherwise the key is built as above, the construction already used for Facebook comments under PPCA (to be confirmed in the pilot which case applies). `client_ids` lists only non-government clients. Also the job result for comment-decay-scheduler, `service_runs`, and `dlq.ig-comments-fetcher` after 5 failed attempts.

### 6.3 State

No per-post state of its own: stored comments are read from ClickHouse. `cursors` (source × service) holds `last_success_at`, `last_error`, `consecutive_errors`; `budgets` holds the `ig_vendor` counters, with a counter per service; in memory only backoff state.

## 7. Limits, quotas and cost

- SociaVault: USD 1.99 to USD 4.83 per 1,000 credits depending on the volume bought, 1 credit per request for most endpoints, credits never expire. At 1 request per fetch that is USD 0.00199 to USD 0.00483 per request; the full 3-step series is USD 0.0060 to USD 0.0145 per post (USD 59.70 to USD 144.90 per 10,000 posts); at about 15 comments a request, about USD 0.00013 to USD 0.00032 per comment. The credit price of this endpoint and the plan: to be fixed in the pilot and the contract.
- Budget tag `ig_vendor`, shared with ig-keyword-search; the monthly budget in USD sits in `budgets`. At 80% consumed quota-governor drops hot-post extras first; any further stretch is an open question; no step is ever sent after a deny.
- Green-route limits that frame this service: 50 comments per query and replies by field expansion exist only on client-owned media; Business Discovery returns no third-party comment text and no age-gated accounts; hashtag media carry no username. This vendor route is not covered by Instagram Public Content Access: its basis is the vendor contract and our author notice (`vendor_agreed`, default 24 months for raw text), and we still publish only aggregated, de-identified analytics from it.
- Government contracts: excluded, always.

## 8. Failure handling and fallback

- HTTP 429 and vendor rate-limit responses: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.ig-comments-fetcher` and an alert fires.
- HTTP 401 and 403, or an out-of-credits response (code to be confirmed in the pilot): the route is marked `degraded`, the batch stops, quota-governor denies `ig_vendor`, and ops are alerted (`vendor_credits_low` where credits are the cause); no keys or accounts are rotated.
- Empty 200 (no comments for a post whose `comments_count` is above zero): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`; credits wasted on empty responses are counted if the vendor bills them (to be confirmed in the pilot). There is no second vendor, so there is no `fallback_on`.
- Flag turned off mid-series: remaining jobs complete as `skipped`; messages already written stay, with their provenance.
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: results move only after acknowledgement; a replayed job re-emits the same keys and normalize-item deduplicates.

## 9. Non-functional requirements

- Throughput: bounded by the monthly `ig_vendor` budget rather than by capacity; the number of selected posts is to be measured in the pilot.
- Latency: a comment visible to the vendor reaches `raw.items` at the next series step plus fetch time.
- Idempotency: `instagram:comment:<id>` or the hash-based key; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag; request rate set by quota-governor.
- Security: vendor key from Supabase Vault per job, never logged; authors hashed before any write, so the username never reaches `raw.items`, the archive or logs; no account pools, no CAPTCHA solving, no proxies; amber data excluded from government contracts; provenance (route, vendor, service, fetch time) on every message and in the client-facing statement.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}` (including `skipped`), `fetch_latency_seconds`, `cost_units_total` (credits), `quota_denied_total`, `dlq_total`, plus `spend_usd_total`, `empty_200_total` and `versions_total`. Alerts: `series_behind`, `vendor_credits_low`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`, `budget_80_percent`. SLO: series completed on time for 95% of selected posts.

## 11. Dependencies

listening-sdk, comment-decay-scheduler, quota-governor, source-health-canary, raw-archiver, normalize-item, deletion-propagator, ig-account-media-poller, ig-hashtag-search and ig-keyword-search (sources of posts), Supabase Postgres and Vault, ClickHouse (read-only), Redpanda, and the SociaVault contract.

## 12. Risks and mitigations

- SociaVault is only weakly cleared (country known, owner not verified): the owner is verified before the contract; an Israeli affiliation ends the service.
- Vendor breach exposure sits in the vendor's contract, not ours: the route is optional, flag-gated, disclosed and excluded from government contracts.
- A thin sample of about 15 comments can mislead: the product labels these comments as a sample and shows `comments_count` beside it.
- Cost growth: the quota-governor budget and per-source caps hold spend; early stop cancels series for quiet posts.
- Vendor endpoint changes: canary on empty 200 and `schema_unknown` parking.

## 13. Acceptance criteria

1. With `IG_VENDOR_ROUTE = off`, no vendor request is made, jobs complete as `skipped`, zero credits are spent and nothing is written.
2. With the flag `sociavault`, a post with `comments_count` above zero gets jobs at +6 h, +24 h and +3 d and no others; a post with `comments_count = 0` gets none.
3. A source watched only by a government client never produces a job; on a source watched by both kinds, every message's `client_ids` lists the non-government clients only.
4. Every message has `route = amber`, `vendor = sociavault`, `retention_class = vendor_agreed`; no username or author id appears in a message, an archive batch or a log line; one commenter on two posts has the same `author_ref`.
5. A fetch with `new_count = 0` cancels the rest of the series; a fetch with 1 new comment against 15 stored does not.
6. A +3 d fetch that adds 3 new comments against 15 stored continues the series every 2 days until day 30, subject to quota-governor.
7. When quota-governor returns deny, no request is sent and `quota_denied_total` rises; at 80% of the monthly budget the hot-post extras are dropped first.
8. `cost_units` per job equals the requests sent, and the `ig_vendor` counter equals credits times the contracted USD rate.
9. A comment with the same id and a changed text is written as a new version; a comment missing from a later fetch is never reported as deleted.
10. Replaying one job twice yields messages with identical `idempotency_key`s; normalize-item stores one item per comment.
11. A 429 triggers backoff from 30 s to at most 15 min; after 5 attempts the job is in `dlq.ig-comments-fetcher` and an alert fired; a 401 marks the route `degraded` and stops the batch with no key rotation.
12. Turning the flag off mid-series completes the remaining jobs as `skipped`.

## 14. Open questions

1. SociaVault endpoint, response fields (ids, timestamps, likes), whether one request can page beyond about 15 comments, whether empty 200s are billed, and the credit price of this endpoint: to be confirmed in the pilot and the contract.
2. Hash at this service (proposed, so usernames never enter the pipeline) or in normalize-item, and sharing the key so one person keeps one reference across services.
3. Which selected posts deserve a series within the monthly budget: proposed order by `comments_count`, then source tier; for comment-decay-scheduler to confirm.
4. Beyond dropping hot-post extras at 80% of the budget, should extension steps be dropped next?
