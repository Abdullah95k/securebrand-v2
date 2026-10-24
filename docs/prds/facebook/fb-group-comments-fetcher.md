# fb-group-comments-fetcher

**Platform:** Facebook · **Route:** amber (optional, flag `FB_VENDOR_ROUTE`) · **Lane:** Comments · **Owner:** Backend lead, Facebook adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

In a Facebook group the post is usually only the question; the answers are in the comments: which district has no service, which operator is blamed, which brand people recommend. fb-group-posts-poller finds the posts of every registered group, but it cannot read what people wrote under them. fb-group-comments-fetcher does, through ScrapeCreators `/v1/facebook/post/comments` (SociaVault's post-comments endpoint is the alternative flag value).

Groups have no green route: Meta removed the Groups API on 22 Apr 2024. Without this service a group post enters the product as text and counts with no conversation under it, so group complaints, recommendations and brand mentions in replies are never seen. The service is optional, behind `FB_VENDOR_ROUTE`, disclosed in the provenance statement and excluded from government contracts.

## 2. Objective (the end state this service delivers)

While the flag is on, every group post found by fb-group-posts-poller has its comments read on the series +1 h, +6 h, +24 h, +3 d, each new comment reaches `raw.items` once with its author kept only as a hashed reference, and spend stays inside the `fb_vendor` budget. Target: comment series completed on time for 95% of posts, no comment stored twice, no commenter name stored.

## 3. Scope

### In scope

- Jobs of kind `comments`, `replies` and `ops_force` from comment-decay-scheduler on `jobs.fb-group-comments-fetcher`.
- Vendor selection by flag, paging, content-hash edit and deletion detection, `author_ref`, the fetch report, the per-post `comment_ledger`.
- Replies by comment id, when the vendor exposes ids.

### Out of scope

- Finding posts (fb-group-posts-poller) and all series timing, early stop, extension and hot-post decisions (comment-decay-scheduler).
- Comments on Page posts (fb-post-comments-fetcher, green); reactions and counts.
- Identifying, qualifying or profiling commenters: individuals are never sources.
- Deduplication (normalize-item), keyword matching (keyword-matcher), executing deletions (deletion-propagator).

## 4. Users and consumers

- **Clients** experience it as "what members answer under the group posts I watch", flagged as vendor-sourced. Government clients never receive it.
- **Ops** owns the flag, the vendor choice and the `fb_vendor` budget, and can force a complete refresh of one post.
- **Downstream services**: normalize-item, keyword-matcher and the analysis services (through `items.normalized`), comment-decay-scheduler (consumes the report), deletion-propagator, raw-archiver, quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Jobs on `jobs.fb-group-comments-fetcher`, partitioned by `source_id`, emitted only by comment-decay-scheduler; this service holds no timer. A job carries `job_id`, `source_id`, `kind` (`comments`, `replies`, `ops_force`), `post_ref` (the post's platform id and permalink; for `replies` also the parent `comment_id`), `series_step`, `due_at`, `attempt`. The series opens when a group post is first seen on `items.normalized`.

**Every post is covered.** The group's tier decides how often posts are found, not how often comments are read: every post of every polled group gets the same series from the moment it is first seen. A series already open runs to its end if the group turns dormant or retired; it is cancelled if the flag turns off or the last non-government client leaves the group.

**Series.** +1 h, +6 h, +24 h, +3 d. comment-decay-scheduler applies the general rules to this service's report:

- Early stop: comment-decay-scheduler applies it from this service's report; this service never stops a series itself (ADR-0019).
- Extension: the series is short, so the rule for shorter series applies at the +3 d fetch: if it still adds 20% or more new comments, fetches continue every 2 days until day 30.
- Hot posts: above 100 new comments an hour, an extra fetch every hour for the next 6 hours; on this paid route quota-governor drops these first when the monthly budget passes 80%.
- Beyond day 30: no automatic fetch.

**Paging.** If the vendor returns comments newest first, a fetch stops at the first comment already in the ledger; if it does not, the fetch pages until the vendor returns no further cursor and ids or hashes decide what is new. The ordering is to be confirmed in the pilot. The +24 h step, the +3 d step and every `ops_force` job are *sweeps*: they page to the end whatever the order, because only a complete read can see edits and deletions. A post's first fetch is complete by construction.

**Replies.** The vendor reports a reply count per comment (to be confirmed in the pilot). Comments above the reply threshold, set by the environment variable `FB_GROUP_REPLY_THRESHOLD` (initial value to be set in the pilot), are listed in the fetch report as `reply_threads`; comment-decay-scheduler then emits a `replies` job per thread through this same service, fetched by comment id. If the vendor exposes no comment id or replies call, no `replies` job exists and replies the vendor nests inline are stored as comments.

**Catch-up.** If the queue falls behind, the oldest `due_at` runs first. A step is delayed, never skipped; `series_late` fires when fewer than 95% of steps ran on time over a day.

### 5.2 Step by step

1. Consume a job; read the flag. If `off`, acknowledge as `skipped_flag_off`: no call. Read the `sources` row and the post's ledger rows; if `health = blocked`, requeue with `due_at` unchanged.
2. Pick the vendor: the flag value, or the other vendor when `health = fallback`. Fetch its key from `vendor_keys` in Supabase Vault for this job only.
3. Ask quota-governor for allowance under `fb_vendor`. Wait-until: requeue. Deny: count `quota_denied_total` and requeue; the step is delayed, never dropped.
4. Call the vendor (5.3) and, for each comment, compute the key, `text_hash = sha256(created_time + text)` and `author_ref`.
5. Page until the stop rule or the end of the cursor. Hold new comments in memory until the fetch ends.
6. Emit one `raw.items` message per new comment; after Redpanda acknowledges the whole batch, write the ledger and `last_fetch_at`. A fetch that fails midway leaves the ledger untouched, so the retry starts again from the first page.
7. Edits and deletions, by hash. With ids, a stored id returned with a different `text_hash` is an edit: the comment is emitted again with the same key, `version` incremented and `text_hash` in the envelope. Without ids, a new hash whose `created_time` equals a missing stored hash is an edit candidate and the old row is `superseded`. A `deletions` event (reason `platform_sync`) is emitted only when the read was complete: the cursor ran out, no page failed, and the response was not empty while the ledger held active comments. Incremental or failed fetches never delete.
8. Report `new_count`, `seen_count`, `pages`, `cost_units`, plus `stored_before`, `complete` and `reply_threads`, to comment-decay-scheduler; update `service_runs` and `cursors` health.

### 5.3 The call it makes

```
ScrapeCreators:  GET <host to be confirmed in the pilot>/v1/facebook/post/comments
SociaVault:      its Facebook post-comments endpoint (1 credit per request; path to be confirmed in the pilot)
  post:   the post's permalink from `post_ref`            (parameter name to be confirmed in the pilot)
  paging: the vendor's cursor from the previous response  (to be confirmed in the pilot)
  auth:   the vendor key from Supabase Vault, in the header the vendor specifies
```

`FB_VENDOR_ROUTE` selects the vendor. Replies by comment id use the vendor's replies call or parameter, to be confirmed in the pilot. Page size is the vendor's. `cost_units` is the number of billed requests.

### 5.4 What it gets

Comment text, time, reply count and the commenter's name, plus an id and reactions if the vendor returns them. The shape below is illustrative; field names are the vendor's and are to be confirmed in the pilot.

```json
{
  "id": "5520817364092218",
  "text": "والله من الصبح الشبكة ميتة عدنا بالكرادة",
  "created_time": "2026-10-06T08:15:02+0000",
  "reply_count": 0, "reactions": 3,
  "author": {"name": "مستخدم تجريبي"}
}
```

The key is `facebook:comment:<comment_id>` when the vendor returns an id, otherwise `facebook:comment:<post_id>:<sha256(created_time + text)>`. The commenter's name and id are never stored: `author_ref`, a keyed hash, goes in the envelope and the payload loses `author` (`payload_redacted: ["author"]`), because individuals are never profiled. Not obtained: reactor identities, private-group comments (to be confirmed in the pilot), a complete thread if the vendor truncates it.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.fb-group-comments-fetcher`; `sources`, `clients` (government marker), `comment_ledger`, `vendor_keys`, `budgets` through quota-governor; the flag at the start of every job; `health` through the SDK canary hook; `source.events` (`fallback_on`, `fallback_off`, `retired`).

### 6.2 Writes

`raw.items`, one message per new comment:

```json
{
  "envelope": {
    "platform": "facebook", "kind": "comment", "route": "amber", "vendor": "scrapecreators",
    "service": "fb-group-comments-fetcher",
    "source_id": "a3d8f0c2-5b17-4e69-8c0d-72e1b94a6f35",
    "platform_id": "5520817364092218",
    "parent_platform_id": "4118203958217764",
    "idempotency_key": "facebook:comment:5520817364092218",
    "job_id": "01J9N4Z6T3K8Q1W5B7D2M9RXHA", "attempt": 1, "series_step": "+1h",
    "fetched_at": "2026-10-06T10:03:44Z",
    "retention_class": "vendor_agreed",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/amber/facebook/2026/10/06/fb-group-comments-fetcher/000031.jsonl.zst",
    "version": 1, "text_hash": "7a1d03c9e5b2f4680d3e1c9a5b7f2468e0d1c3a5b79f2e4d6c8a0b1e3f5d7c92",
    "author_ref": "b90e2d41f7a3c6850e1d9b3a7c5f4e2d8a6b0c1f3e5d7a9b2c4e6f8a0d1b3c57",
    "payload_redacted": ["author"]
  },
  "payload": { "id": "5520817364092218", "text": "…", "created_time": "2026-10-06T08:15:02+0000", "reply_count": 0, "reactions": 3 }
}
```

A reply carries `parent_platform_id` = the parent comment id and `post_platform_id` = the post. `deletions`: one event per deleted comment with `platform`, `kind`, `idempotency_key`, `reason = platform_sync`, `service`, `job_id`, `detected_at`. Also the fetch report, `service_runs`, and `dlq.fb-group-comments-fetcher` after 5 failed attempts.

### 6.3 State

`comment_ledger` (control-plane Postgres, shared design with fb-post-comments-fetcher): per post and comment, the id (if any), `text_hash`, `created_time`, `state` (`active`, `superseded`, `deleted`), `first_seen_at`, `last_seen_at`; per post `last_fetch_at` and `last_complete_sweep_at`; hashes only, never text. `cursors` holds health only; `budgets` counters for `fb_vendor`.

## 7. Limits, quotas and cost

- ScrapeCreators: USD 0.99 to 1.88 per 1,000 requests. SociaVault: USD 1.99 to 4.83 per 1,000 credits, 1 credit per request. Vendor rate limits and page size: to be confirmed in the pilot.
- Minimum cost: 4 series requests per post, so per 1,000 group posts USD 3.96 to 7.52 (ScrapeCreators) or USD 7.96 to 19.32 (SociaVault). Extra pages, sweeps, replies, extension and hot-post fetches add to this; volume per post is to be measured in the pilot.
- Budget tag `fb_vendor`, shared with fb-group-posts-poller and fb-keyword-search. Past 80% of the monthly budget, quota-governor drops hot-post extra fetches first.

## 8. Failure handling and fallback

- Vendor 429 and rate-limit responses: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.fb-group-comments-fetcher` and an alert fires.
- HTTP 401 and 403: mark the route `degraded`, stop the batch, alert; never rotate accounts or IPs.
- Empty 200 (no comments for a post known to have them): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded` and, with the flag on and the other vendor's key present, emits `fallback_on`; jobs read the flag and health at the start. After a vendor switch, comments may be re-emitted under different keys.
- Post gone (vendor reports not found): stop that post's series and tell comment-decay-scheduler; no `deletions` event for the post from one error.
- Schema change: payload still archived; normalize-item raises `schema_unknown`.
- Partial write: the ledger moves only after acknowledgement; replays re-emit the same keys.

## 9. Non-functional requirements

- Throughput: Facebook's full-scale share is 12.0M items a month; the group-comment share is to be measured in the pilot.
- Latency: a step is on time when its job completes before the next step falls due; a tighter tolerance is to be set in the pilot.
- Idempotency: the keys of 5.4; ledger written after acknowledgement; replay-safe jobs.
- Scaling: stateless workers on partition lag; no leader.
- Security: vendor keys from Supabase Vault per job, never logged; comment text never logged; no account pools, no proxies, no Facebook login of ours; amber data excluded from government contracts; Meta data never processed for law-enforcement or national-security purposes; provenance on every message.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds` (now minus `due_at`), `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `vendor_requests_total{vendor,status}`, `fetches_total{kind}`, `edit_candidates_total`, `deletions_emitted_total`, `reply_threads_total`. Alerts: `series_late`, `vendor_degraded`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`, `budget_80_percent`. SLO: comment series completed on time for 95% of posts.

## 11. Dependencies

listening-sdk, comment-decay-scheduler, quota-governor, source-health-canary, raw-archiver, normalize-item, deletion-propagator, fb-group-posts-poller, fb-keyword-search, Supabase Postgres and Vault, Redpanda, a vendor contract with ScrapeCreators or SociaVault.

## 12. Risks and mitigations

- Platform terms: any breach sits in the vendor's contract; the route is optional, flagged, disclosed and excluded from government contracts.
- Both vendors are weakly cleared (owner not verified): checked before go-live, since no Israeli-affiliated vendor is allowed.
- Vendor lists may be truncated or ranked, so a "complete" read may be partial: deletions need a complete cursor and a non-empty response, and a pilot test measures truncation (open question 5).
- Cost: extension to day 30 and hot-post fetches multiply requests; hot-post fetches go first at 80%.
- Personal data: names are never stored; `author_ref` only counts distinct authors.

## 13. Acceptance criteria

1. With `FB_VENDOR_ROUTE = off` no vendor call is made and jobs are acknowledged `skipped_flag_off`.
2. A post's first fetch pages to the end of the vendor's cursor and reports `complete = true`.
3. A fixture post runs steps +1 h, +6 h, +24 h, +3 d; the report carries `new_count`, `seen_count`, `pages`, `cost_units` and `stored_before`, so a +3 d fetch adding 30% lets comment-decay-scheduler extend to day 30.
4. The same comment fetched twice has one `idempotency_key` (`facebook:comment:<comment_id>`, or the hash form without ids); normalize-item stores one item.
5. A stored id returned with different text is re-emitted with `version` incremented and a new `text_hash`.
6. A comment missing from a complete read yields exactly one `deletions` event (`platform_sync`); an incremental read, a read failing on page 2, or an empty response yields none.
7. A comment above `FB_GROUP_REPLY_THRESHOLD` appears in `reply_threads` and a `replies` job fetches by comment id; with no vendor ids, no `replies` job is created.
8. No `raw.items` message contains a commenter name; `author_ref` is set and `payload_redacted` lists `author`.
9. At 80% of the `fb_vendor` budget hot-post extra fetches are dropped first and series steps are delayed, never dropped.
10. An empty-200 rate above 5% in 15 minutes switches later jobs to the other vendor.
11. `client_ids` never lists a government client, and vendor keys never appear in logs.

## 14. Open questions

1. Does the vendor return comment ids, reply counts and a replies call, and in which order does it return comments?
2. What initial value for `FB_GROUP_REPLY_THRESHOLD`?
3. Should extension fetches be dropped second, after hot-post fetches, at 80% of the budget?
4. What happens to steps missed while the flag is off: no catch-up, or one complete fetch for posts still inside their 3-day window?
5. On this route, should a deletion require two consecutive complete reads?
