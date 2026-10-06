# fb-post-comments-fetcher

**Platform:** Facebook · **Route:** green · **Lane:** Comments · **Owner:** Backend lead, Facebook adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Most of what people say about a brand, a ministry or an outlet on Facebook is said in the comments, not in the post. Comments are also most of the Facebook volume: 12.0M items a month at full scale, posts and comments together. fb-post-comments-fetcher reads the comments under every post that the green Facebook services find, through the Meta Graph API comments edge under Page Public Content Access (PPCA).

Without it the product shows a post and a number ("312 comments") but never what the 312 people wrote: no comment sentiment, no complaint about a network or a tariff, no brand mention under a competitor's or an outlet's post, no keyword hit inside a comment. Every post found by fb-page-feed-poller, fb-backfill or fb-client-webhook-receiver would sit in the product without its most valuable half.

## 2. Objective (the end state this service delivers)

Every post on a green Facebook Page has its comments fetched on the decay series, each new comment reaches `raw.items` exactly once, and edited or deleted comments are recognized even though PPCA returns no comment ids. Target: comment series completed on time for 95% of posts, no comment stored twice, and a `deletions` event only ever after a complete read of the post's comment stream.

## 3. Scope

### In scope

- Jobs of kind `comments` from comment-decay-scheduler, one post per job, each with its `series_step`.
- Newest-first paging with an early exit at the first stored hash, and complete sweeps at fixed steps.
- Writing `raw.items` (kind `comment`), `deletions`, the fetch report to comment-decay-scheduler and the per-post `comment_ledger`.
- Replies, which arrive inside the same stream.

### Out of scope

- Finding posts (fb-page-feed-poller, fb-backfill, fb-client-webhook-receiver) and the series timing, early stop, extension and hot-post decisions (comment-decay-scheduler).
- Reactions and counts (fb-reactions-fetcher); comments on group posts (fb-group-comments-fetcher, amber).
- Comment ids and commenter identity under PPCA: not returned, so not requested.
- Refreshing `like_count` of comments already stored (open question 4).
- Deduplication (normalize-item), keyword matching (keyword-matcher), executing deletions (deletion-propagator).

## 4. Users and consumers

- **Clients** experience it as "what people write under the posts I watch, within hours of the post being found". They never call it.
- **Ops** watches series lateness, token health and the DLQ, and can force a complete refresh of one post (`ops_force`); a client's request to refresh a post beyond day 30 uses the same job kind.
- **Downstream services**: normalize-item (consumes `raw.items`), keyword-matcher and the analysis services through `items.normalized`, comment-decay-scheduler (consumes the fetch report), deletion-propagator (consumes `deletions`), raw-archiver, quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.fb-post-comments-fetcher`, partitioned by `source_id`, so one Page is never worked twice at once. Only comment-decay-scheduler emits these jobs; this service holds no timer. A job carries `job_id`, `source_id`, `kind = comments`, `post_ref` (the post's platform id, `<page-id>_<post-id>`), `series_step`, `due_at`, `attempt`. The series for a post opens when the post is first seen on `items.normalized`, whichever service found it.

**Every post is covered.** The Page's tier sets how often posts are discovered, not how often their comments are read: every post of every Page gets the same series, counted from the moment the post is first seen. Posts from fb-backfill enter the same way. A dormant or retired Page produces no new series; a series already open runs to its end.

**Series.** +1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30. comment-decay-scheduler applies the general rules to this service's report:

- Early stop: a fetch that adds fewer than 5% new comments and fewer than 5 in absolute cancels the rest of the series.
- Extension: if the day-7 fetch still adds 20% or more new comments, fetches continue every 2 days until day 30.
- Hot posts: above 100 new comments an hour (`new_count` divided by the hours since the previous fetch), an extra fetch every hour for the next 6 hours.
- Beyond day 30: no automatic fetch.

**Paging.** Every fetch reads newest first and stops at the first comment whose hash is already in the ledger, so an incremental fetch usually costs one call. The +24 h step, the +7 d step, the last step of the series and every `ops_force` job are *sweeps*: they ignore the stop rule and page until `paging.next` is absent. A post's first fetch is complete by construction, because its ledger is empty. Comments that Meta surfaces late (public content can be up to 24 hours late) and edits sit behind the stop point, so only sweeps can see them; this is why +24 h is a sweep.

**Replies.** `filter=stream` returns replies flattened into the same stream as top-level comments, so this route has no `replies` job and no reply threshold: every reply is read with the comments and deduplicated by the same hash. Whether a reply's parent is returned is to be confirmed in the pilot.

**Catch-up.** If the queue falls behind, the oldest `due_at` runs first. A step is delayed, never skipped; `series_late` fires when fewer than 95% of steps ran on time over a day.

### 5.2 Step by step

1. Consume a job; read the `sources` row and the post's `active` ledger rows. If `health = blocked`, requeue with `due_at` unchanged and make no call.
2. Select the token: the system-user token from Supabase Vault for this job only; for `owned_by_client` Pages, the client's Page access token.
3. Ask quota-governor for allowance under `meta_graph_pages:<client_id>`. Wait-until: requeue for that time. Deny: count `quota_denied_total` and requeue; hot-post extra fetches are dropped first, series steps never.
4. Call the comments edge (5.3) and compute `sha256(created_time + text)` for each comment.
5. Follow `paging.next` until the stop rule (incremental) or the last page (sweep or first fetch). Hold the new comments in memory until the fetch ends.
6. Emit one `raw.items` message per new hash. After Redpanda acknowledges the whole batch, write the ledger rows and `last_fetch_at` (and `last_complete_sweep_at` after a complete read). A fetch that fails midway leaves the ledger untouched, so the retry restarts at the newest comment and cannot stop early on a comment stored while an older gap was still unread.
7. Edits and deletions, by hash. Let T_min be the `created_time` of the oldest comment this fetch returned. An `active` ledger hash with `created_time` not older than T_min that the fetch did not return is *absent in range*.
   - Edit candidate: a new hash whose `created_time` equals that of an absent-in-range hash. The old row becomes `superseded`; the new message carries `edit_of` (the old idempotency key) and normalize-item stores it as a new version. It stays a candidate, because without ids an edit cannot be told from two comments written in the same second.
   - Deletion: only when the fetch was complete, meaning it ran to the last page without error. Each absent hash that is not superseded gets a `deletions` event with reason `platform_sync`, and its row becomes `deleted`. An incremental fetch, a fetch that failed midway or one denied by quota emits no `deletions` event, whatever is missing. A complete read that returns zero comments for a post with stored comments is treated as an empty 200 and deletes nothing.
8. Report to comment-decay-scheduler `new_count`, `seen_count`, `pages`, `cost_units`, plus `stored_before` (so it can compute percentages) and `complete`; update `service_runs` and the `cursors` health fields.

### 5.3 The call it makes

```
GET https://graph.facebook.com/v<pinned>/{post-id}/comments
  ?filter=stream
  &order=reverse_chronological
  &limit=100
  &fields=message,created_time,like_count
  &access_token=<system-user token (PPCA); Page access token for owned_by_client Pages>
```

`{post-id}` is `post_ref`. On `owned_by_client` Pages `id,from` are added to `fields`. Pagination: cursor-based, follow `paging.next`. Page size: 100. The Graph version is pinned by the one environment variable shared by all fb-* services. `cost_units` is the number of Graph calls made.

### 5.4 What it gets

Under PPCA, per comment: `message`, `created_time`, `like_count`. The idempotency key is `facebook:comment:<post_id>:<sha256(created_time + text)>`, hashing `created_time` as returned plus `message` as returned, with no trimming and no separator; a comment without `message` (a sticker or a photo) hashes from `created_time` alone. On client-owned Pages `id` and `from` also arrive: the key becomes `facebook:comment:<comment-id>`, edits are exact (same id, new text hash), deletions are exact (id missing from a complete read), and `from` is replaced in the payload by `author_ref`, a keyed hash in the envelope (the envelope lists `payload_redacted: ["from"]`), because individuals are never profiled.

What it does not get: comment ids, commenter identity or reply parents under PPCA; comments Meta has not yet surfaced; refreshed `like_count` for stored comments. Two identical comments written in the same second collapse into one key, an accepted loss to be measured in the pilot.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.fb-post-comments-fetcher`; `sources`, `clients` (token reference), `comment_ledger`, `budgets` through quota-governor, `health` through the SDK canary hook; `source.events` (`retired`, `updated`).

### 6.2 Writes

`raw.items`, one message per new comment:

```json
{
  "envelope": {
    "platform": "facebook", "kind": "comment", "route": "green", "vendor": null,
    "service": "fb-post-comments-fetcher",
    "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
    "platform_id": null,
    "parent_platform_id": "100064583471102_1198837625012734",
    "idempotency_key": "facebook:comment:100064583471102_1198837625012734:3b7e5a0c9d21f84e6a1b0c7d93e2f5a8416b0d7c2e9f3a58b1d04c6e7f29a3d5",
    "job_id": "01J9N3A8K2P6W4T1X7Z9C0Q5RD", "attempt": 1, "series_step": "+6h",
    "fetched_at": "2026-10-06T15:20:11Z",
    "retention_class": "meta_on_request",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/facebook/2026/10/06/fb-post-comments-fetcher/000417.jsonl.zst",
    "edit_of": null, "author_ref": null
  },
  "payload": {
    "message": "الله يوفقكم، بس الشبكة ضعيفة بالمنصور من الصبح",
    "created_time": "2026-10-06T08:41:55+0000",
    "like_count": 4
  }
}
```

`deletions`, one event per deleted comment: `{"platform": "facebook", "kind": "comment", "idempotency_key": "<as above>", "parent_platform_id": "<post id>", "reason": "platform_sync", "service": "fb-post-comments-fetcher", "job_id": "<ulid>", "detected_at": "<ISO time>"}`. Also the fetch report to comment-decay-scheduler, `service_runs`, and `dlq.fb-post-comments-fetcher` after 5 failed attempts.

### 6.3 State

`comment_ledger` (control-plane Postgres, owned by this service): per post and comment key, the hash, `created_time`, `state` (`active`, `superseded`, `deleted`), `superseded_by`, `first_seen_at`, `last_seen_at`; per post, `last_fetch_at` and `last_complete_sweep_at`. It holds hashes and times only, never text, and is removed by retention-purger with the post's comments. `cursors` (`source_id`, `fb-post-comments-fetcher`) holds health only: `last_success_at`, `last_error`, `consecutive_errors`.

## 7. Limits, quotas and cost

- The Pages bucket allows 4,800 calls × engaged users per 24 h with a system-user token. Comments are its heaviest consumer: every post is read several times, and a sweep of N comments costs ceil(N / 100) calls, while an incremental fetch costs one call when the stored hash sits in the first 100. quota-governor keeps the counter under `meta_graph_pages:<client_id>`.
- Error 80001 ("too many calls to this Page") defers that Page's jobs by backoff; hot-post extra fetches are the first work dropped.
- Cost: USD 0 per Graph call; the cost is quota. Calls per day at full scale: to be measured in the pilot.
- Latency: public content can surface up to 24 hours late (Sprinklr documents "Latency: Up to 24 hours").

## 8. Failure handling and fallback

- HTTP 429 and 80001: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.fb-post-comments-fetcher` and an alert fires.
- HTTP 401 and 403: mark the token `degraded`, stop the batch, alert; never rotate accounts, tokens or IPs.
- Empty 200 (no `data` for a post whose latest summary shows comments): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. No amber fallback is wired for Page comments in v1 (open question 5), so `fallback_on` is never set here.
- Post no longer available: the service stops that post's series, tells comment-decay-scheduler (`post_unavailable`) and ops. A single Graph error never produces a `deletions` event for the post; the code that separates a removed post from a permission failure is to be confirmed in the pilot.
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: the ledger moves only after acknowledgement; a replay re-emits the same keys and normalize-item deduplicates them.

## 9. Non-functional requirements

- Throughput: Facebook's share of the full-scale target is 12.0M items a month; the comment share and calls per day are to be measured in the pilot.
- Latency: a step is on time when its job completes before the next step of the series falls due; a tighter tolerance is to be set in the pilot.
- Idempotency: the keys of 5.4; ledger written after acknowledgement; every job is replay-safe.
- Scaling: stateless workers scaled on partition lag of `jobs.fb-post-comments-fetcher`; no leader needed.
- Security: tokens from Supabase Vault per job, never logged; comment text never logged; `author_ref` is a keyed hash with its key in Vault and is used only to count distinct authors; Meta data never processed for law-enforcement or national-security purposes; provenance on every message; retention `meta_on_request`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds` (now minus `due_at` of the most overdue job), `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `fetches_total{kind}` (incremental, sweep), `edit_candidates_total`, `deletions_emitted_total`, `pages_per_fetch`, `graph_error_total{code}`. Alerts: `series_late`, `token_degraded`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`, `sweep_held` (a complete read stopped by the zero-comment guard). SLO: comment series completed on time for 95% of posts.

## 11. Dependencies

listening-sdk, comment-decay-scheduler, quota-governor, source-health-canary, raw-archiver, normalize-item, deletion-propagator, retention-purger, fb-page-feed-poller, fb-backfill, fb-client-webhook-receiver, Supabase Postgres and Vault, Redpanda. Meta prerequisites: Business Verification, App Review for PPCA, Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- No ids: an edit looks like a new comment plus a missing one, and identical comments in the same second collapse. Edits are labeled candidates, the collision rate is measured in the pilot, and client-owned Pages return ids.
- Early stop can cancel the +24 h sweep on a quiet post, leaving late comments and edits unseen (open question 2).
- Comments are the heaviest user of the Pages bucket, and a first fetch of a viral post is expensive: quota-governor can defer it, and hot-post fetches are dropped first.
- If Meta alters `message` between fetches, false edits appear: checked in the pilot (open question 1).
- App Review takes up to several weeks: the pilot runs on client-owned Pages, where ids are available.

## 13. Acceptance criteria

1. A post's first fetch against a 250-comment fixture makes 3 calls, emits 250 messages and reports `complete = true`.
2. An incremental fetch against 7 new comments on top of 240 stored ones makes 1 call, emits 7 messages and stops at the first stored hash (`new_count = 7`, `pages = 1`).
3. The same comment fetched twice produces the same `idempotency_key`, `facebook:comment:<post_id>:<sha256(created_time + text)>`; normalize-item stores one item.
4. A comment edited in place (same `created_time`, new text), read by a sweep, yields one message with `edit_of` set, the old row `superseded`, and no `deletions` event.
5. A comment removed from the stream causes no deletion on an incremental fetch; the next sweep emits exactly one `deletions` event with reason `platform_sync`.
6. A sweep that hits a 5xx on page 3 emits no `deletions` event and leaves the ledger unchanged; the retry restarts at page 1 and completes.
7. A sweep returning zero comments for a post with 40 active hashes emits no `deletions`, counts an empty 200 and raises `sweep_held`.
8. The +24 h, +7 d and day-30 steps and an `ops_force` job run as sweeps; the other steps are incremental.
9. The report carries `new_count`, `seen_count`, `pages`, `cost_units`, `stored_before` and `complete`; with 3 new comments on 100 stored, comment-decay-scheduler can apply the early stop.
10. A 401 marks the token `degraded`, stops the batch and raises `token_degraded`; tokens and comment text never appear in logs.
11. On an `owned_by_client` Page the call requests `id,from`, the key is `facebook:comment:<comment-id>`, and the message carries `author_ref` with no commenter name.

## 14. Open questions

1. Does Graph return `message` byte-identical across fetches, and is a reply's parent returned? To be confirmed in the pilot.
2. Should the +24 h sweep be exempt from early stop? Proposed: yes, because it is the only catch for late comments.
3. Does `comments.summary(total_count)` under `filter=stream` include replies? If so, it gives a cheap completeness check.
4. Should the `like_count` of stored comments be refreshed on sweeps through `item.metrics`? Not in v1.
5. While PPCA is pending, should the vendor's post-comments endpoint serve as an amber fallback for Page posts?
6. Is the fetch report sent to comment-decay-scheduler as a job-result record, and does `comment_ledger` stay in Postgres rather than ClickHouse?
