# fb-group-posts-poller

**Platform:** Facebook · **Route:** amber (optional, flag `FB_VENDOR_ROUTE`) · **Lane:** Fetch posts · **Owner:** Backend lead, Facebook adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A large part of public Facebook conversation happens in groups, not on Pages: neighborhood groups, customer-complaint groups, professional and buy-and-sell groups. Meta removed the Groups API on 22 Apr 2024 and Page Public Content Access (PPCA) never covered groups, so there is no green route to group posts. The only way to read them is to buy the data from a screened vendor that does the collection itself: ScrapeCreators `/v1/facebook/group/posts`, or SociaVault's group endpoint. fb-group-posts-poller is the service that does this for every registered Facebook group.

Without it the product is blind to groups: no early sign of a service complaint spreading, no group chatter about a brand, no posts for fb-group-comments-fetcher to work on, and no poster candidates for the qualifier from inside groups. The service is optional, behind `FB_VENDOR_ROUTE`, disclosed in the provenance statement and excluded from government contracts; with the flag off the rest of the Facebook side runs unchanged.

## 2. Objective (the end state this service delivers)

While the flag is on, every amber Facebook group in the registry with an active tier is polled on its tier's cadence, every new post reaches `raw.items` within one tier interval of the vendor seeing it, and the cursor advances only after Redpanda has acknowledged the batch. Target: rotation lag below one tier interval for 99% of groups per day, staleness p95 within the tier maximum (1 h, 6 h, 24 h), zero jobs lost, spend inside the `fb_vendor` budget.

## 3. Scope

### In scope

- Rotation scheduling of every amber Facebook group by tier, and execution of jobs of kind `rotation`, `backfill` and `ops_force` on `jobs.fb-group-posts-poller`.
- Vendor selection from the flag (`scrapecreators` or `sociavault`) and fallback to the other vendor.
- Incremental reads, `raw.items` (kind `post`), `author_ref` for every poster, cursor and `next_poll_at` upkeep, dormant promotion, budget stretching, `rotation_behind` catch-up.

### Out of scope

- Finding groups (fb-keyword-search surfaces posts; qualifier rule 8 adds the group as a source through registry-writer) and tier decisions (qualifier, registry-writer).
- Comments (fb-group-comments-fetcher); green Page posts (fb-page-feed-poller); deduplication (normalize-item); keyword matching (keyword-matcher).
- Qualifying posters (poster-resolver, qualifier); profiling or backfilling any individual.
- Refreshing post counts after the first read (open question 6).

## 4. Users and consumers

- **Clients** experience it as "posts from the groups I watch, never older than my tier allows", marked as vendor-sourced in the provenance statement. Government clients never receive this data.
- **Ops** owns the flag, the vendor choice and the `fb_vendor` budget, and can force a poll of one group.
- **Downstream services**: normalize-item, keyword-matcher, comment-decay-scheduler (through `items.normalized`), raw-archiver, source-health-canary, quota-governor, backfill-orchestrator, poster-resolver (poster candidates).

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.fb-group-posts-poller`, partitioned by `source_id`, emitted by the rotation scheduler inside this service (one leader replica elected through a Postgres advisory lock; the scan period is an environment variable well inside the shortest tier interval of 60 minutes). The scheduler runs only while `FB_VENDOR_ROUTE` is `scrapecreators` or `sociavault`, and selects `sources` rows with `platform = facebook`, `source_type = group`, `route = amber`, `health != blocked`, `backfill_status in (done, capped)`, at least one client in `client_ids` that is not under a government contract, and `next_poll_at <= now()`. Backfill jobs come only from backfill-orchestrator.

**Cadence by tier.** The tier comes from member count (held in `followers`) with the account thresholds. Tier 1 (100,000 or more members, or on a client's priority list): every 60 minutes. Tier 2 (10,000 to 99,999): every 6 hours. Tier 3 (below 10,000): every 24 hours. Dormant (no post in 30 days): weekly; a new post promotes the group back to its reach tier through `source.events` (`tier change`). Retired: never polled. There is no push tier for groups, because Meta offers no webhook and no green read; even a group a client owns is polled by rotation.

**Keeping every group on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + interval`), so cadence is fixed and does not drift with fetch time. Jobs are emitted ordered by `next_poll_at` then by tier, so an overdue Tier 3 group is not pushed aside by Tier 1 groups and no group is skipped twice in a row. A group is in at most one job at a time. A failed job keeps its old `next_poll_at`, so that group is the first candidate on the next scan.

**Budget stretching.** A vendor route pays per request. When the monthly `fb_vendor` budget is 80% consumed, quota-governor may stretch the Tier 1 and Tier 2 intervals, never beyond 24 hours; Tier 3 is already daily and dormant stays weekly. The stretch ends when the budget month rolls over or ops raises the budget. Every group is still checked at least daily.

**Catch-up.** `rotation_lag_seconds` is now minus `next_poll_at` of the most overdue group. When it exceeds one interval (the stretched interval while a stretch is on), the scheduler switches to most-stale-first ordering and raises `rotation_behind`. Every poll is incremental from the cursor, so a late poll still returns everything since the cursor, within the vendor's pagination depth: being behind costs freshness, not completeness.

**Backfill on add.** A new group arrives with `backfill_status = pending`. backfill-orchestrator sends a `backfill` job here: the last 90 days or the vendor's pagination depth, whichever is smaller, written to `raw.items` like any poll. On completion the cursor is written, `backfill_status` becomes `done` or `capped`, and `next_poll_at = now()`. Backfill is per group, never per poster.

**Comment decay.** Each new post flows `raw.items` → normalize-item → `items.normalized`, where comment-decay-scheduler opens the series for fb-group-comments-fetcher: +1 h, +6 h, +24 h, +3 d.

### 5.2 Step by step

1. Consume a job (`source_id`, `tier`, `attempt`, `kind`); read the flag. If `off`, acknowledge as `skipped_flag_off`: no call, cursor and `next_poll_at` untouched. Read the `sources` and `cursors` rows; stop if `health = blocked`.
2. Pick the vendor: the flag value, or the other vendor when this source's `health = fallback`. Fetch its key from `vendor_keys` in Supabase Vault for this job only.
3. Ask quota-governor for allowance under `fb_vendor`; on wait-until requeue, on deny count `quota_denied_total` and keep `next_poll_at`.
4. Call the vendor (5.3), newest posts first, and follow its pagination until a page adds no post newer than the cursor, or, for backfill, until posts are older than 90 days.
5. For each post compute `author_ref` and write one `raw.items` message; raw-archiver lands the batch under `raw/amber/facebook/<yyyy>/<mm>/<dd>/fb-group-posts-poller/`.
6. After Redpanda acknowledges: set `cursor` to the newest `created_time` seen, `last_success_at`, `consecutive_errors = 0`, `last_polled_at`, `next_poll_at`; emit `tier change` if a dormant group posted.
7. Record the metrics of section 10 and the requests billed into `budgets`.

### 5.3 The call it makes

```
ScrapeCreators:  GET <host to be confirmed in the pilot>/v1/facebook/group/posts
SociaVault:      its Facebook group-posts endpoint (path to be confirmed in the pilot)
  group:  the group's url or platform_id from `sources`   (parameter name to be confirmed in the pilot)
  paging: the vendor's cursor from the previous response  (to be confirmed in the pilot)
  auth:   the vendor key from Supabase Vault, in the header the vendor specifies
```

`FB_VENDOR_ROUTE` selects the vendor: `scrapecreators` or `sociavault`. Fields needed: post id, text, created time, permalink, poster id and name, reaction, comment and share counts, media links. Page size, ordering (chronological or by activity) and pagination depth are the vendor's: to be confirmed in the pilot. The stop rule is therefore "a page with no new post", not "first known post", so an old post bumped by activity cannot hide new ones.

### 5.4 What it gets

Group posts with poster names and ids. The shape below is illustrative; field names are the vendor's and are to be confirmed in the pilot.

```json
{
  "id": "4118203958217764",
  "group_id": "271936048205533",
  "text": "السلام عليكم، منو يعرف سبب انقطاع الإنترنت بالكرادة اليوم؟",
  "created_time": "2026-10-06T07:48:30+0000",
  "url": "https://www.facebook.com/groups/271936048205533/posts/4118203958217764",
  "author": {"id": "61552270194836", "name": "مستخدم تجريبي"},
  "reactions": 12, "comments": 9, "shares": 0
}
```

What it does not get: comments (fb-group-comments-fetcher); reactor identities; private-group content (whether a closed group returns anything is to be confirmed in the pilot); Reels; a complete record if the vendor's pagination is shallower than a busy group's volume.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.fb-group-posts-poller`; `sources`, `cursors`, `clients` (government marker), `vendor_keys`, `budgets` through quota-governor; the flag `FB_VENDOR_ROUTE` at the start of every job; `health` through the SDK canary hook; `source.events` (`added`, `tier change`, `retired`, `fallback_on`, `fallback_off`).

### 6.2 Writes

`raw.items`, one message per post, envelope plus the vendor record as returned:

```json
{
  "envelope": {
    "platform": "facebook", "kind": "post", "route": "amber", "vendor": "scrapecreators",
    "service": "fb-group-posts-poller",
    "source_id": "a3d8f0c2-5b17-4e69-8c0d-72e1b94a6f35",
    "platform_id": "4118203958217764",
    "idempotency_key": "facebook:post:4118203958217764",
    "job_id": "01J9N4B2M8R5V7Y3D1F6H0KQXE", "attempt": 1,
    "fetched_at": "2026-10-06T09:02:17Z",
    "retention_class": "vendor_agreed",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/amber/facebook/2026/10/06/fb-group-posts-poller/000052.jsonl.zst",
    "author_ref": "e4c91a07b5d3f2886a0c1d9e47b3a5f6c2d80e19a7b4c3f5d6e2a1b09c8d7f34",
    "metrics_observation": "poll"
  },
  "payload": { "...": "the post object from 5.4, unchanged" }
}
```

`author_ref` is a keyed hash of the poster id (key in Supabase Vault). The poster's id and name stay in the payload so keyword-matcher and poster-resolver can treat the poster as a candidate separately from the group (qualifier rule 8); an individual is kept only as `author_ref` (rule 7). `client_ids` never lists a government client. Also `source.events` (`tier change`), `service_runs`, `dlq.fb-group-posts-poller` after 5 failed attempts.

### 6.3 State

`cursors.cursor` = ISO `created_time` of the newest stored post, with `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`, `backfill_status`; `budgets` counters for `fb_vendor`; in memory only the leader lock, the vendor page token and backoff state.

## 7. Limits, quotas and cost

- ScrapeCreators: USD 0.99 to 1.88 per 1,000 requests. SociaVault: USD 1.99 to 4.83 per 1,000 credits, 1 credit per request, credits never expire. Vendor rate limits: to be confirmed in the pilot.
- At one request per poll, a group costs per month:

| Tier | Requests | ScrapeCreators | SociaVault |
|---|---|---|---|
| 1 (hourly) | 720 | USD 0.71 to 1.35 | USD 1.43 to 3.48 |
| 2 (6 h) | 120 | USD 0.12 to 0.23 | USD 0.24 to 0.58 |
| 3 (daily) | 30 | USD 0.03 to 0.06 | USD 0.06 to 0.14 |

Extra pages add requests. Group count at full scale and requests per poll: to be measured in the pilot.
- Budget tag `fb_vendor`, shared with fb-group-comments-fetcher and fb-keyword-search; stretching starts at 80% of the monthly budget (5.1).

## 8. Failure handling and fallback

- Vendor 429 and rate-limit responses: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.fb-group-posts-poller` and an alert fires.
- HTTP 401 and 403: mark the route `degraded`, stop the batch, alert; never rotate accounts or IPs.
- Empty 200 (no posts from a group known to be active): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded` and, with the flag on and the other vendor's key present, emits `fallback_on`; this service reads the flag and health at the start of every job and switches vendor. `fallback_off` restores the flag's vendor. Whether the vendor bills empty 200s is to be confirmed in the pilot.
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: cursors move only after acknowledgement; a replayed job re-emits the same posts and normalize-item deduplicates them.
- Flag `off`: no calls, no cursor movement; stored items stay under their retention class.

## 9. Non-functional requirements

- Throughput: Facebook's full-scale share is 12.0M items a month; the group share, group count and requests per day are to be measured in the pilot.
- Latency: a post visible to the vendor reaches `raw.items` within its tier interval plus fetch time.
- Idempotency: `facebook:post:<platform_id>`; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag; one leader scheduler.
- Security: vendor keys from Supabase Vault per job, never logged; no account pools, no proxies, no CAPTCHA solving, no Facebook login of ours; individuals never profiled; amber data excluded from government contracts; Meta data never processed for law-enforcement or national-security purposes; provenance on every message.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `vendor_requests_total{vendor,status}`, `groups_in_rotation{tier}`, `stretch_active` and `fallback_active`. Alerts: `rotation_behind`, `vendor_degraded`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `quota_deny_rate`, `budget_80_percent`. SLO: rotation lag below one tier interval for 99% of groups per day.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, keyword-matcher, comment-decay-scheduler, fb-group-comments-fetcher, fb-keyword-search, backfill-orchestrator, poster-resolver, qualifier, registry-writer, Supabase Postgres and Vault, Redpanda, a vendor contract with ScrapeCreators or SociaVault.

## 12. Risks and mitigations

- Platform terms: any breach sits in the vendor's contract, not ours; the route is optional, flagged, disclosed and excluded from government contracts.
- Both vendors are weakly cleared (country known, owner not verified): ownership is checked before go-live, since the product bans any Israeli-affiliated vendor.
- Personal data in group posts: individuals are kept only as `author_ref`, never backfilled or profiled.
- Cost grows with tier mix: stretching at 80%, never beyond daily.
- Vendor outage or block: automatic fallback to the other vendor; otherwise `rotation_behind` and degraded health.

## 13. Acceptance criteria

1. With `FB_VENDOR_ROUTE = off` no vendor call is made, jobs are acknowledged `skipped_flag_off`, and cursors and `next_poll_at` do not move.
2. A Tier 1 group whose poll started at 09:00:00 has `next_poll_at = 10:00:00` even when the fetch took 4 minutes.
3. With 100 fixture groups across three tiers against a simulated vendor for 24 hours, no group's `rotation_lag_seconds` exceeds its tier interval.
4. With the `fb_vendor` budget at 80%, Tier 1 and Tier 2 intervals stretch but never exceed 24 hours, Tier 3 is unchanged, and every group is still polled at least daily.
5. Replaying one job twice yields two `raw.items` messages with the same `idempotency_key`; normalize-item stores one item.
6. The cursor does not advance when the Redpanda produce fails; the next attempt re-emits the batch.
7. Every message carries `route = amber`, `vendor`, `service`, `fetched_at`, `retention_class = vendor_agreed` and `author_ref`; `client_ids` contains no government client.
8. An empty-200 rate above 5% in 15 minutes makes the next jobs use the other vendor; after recovery `fallback_off` restores the flag's vendor.
9. A dormant group is polled weekly; a new post emits a `tier change` event and returns it to its reach tier.
10. A group with `backfill_status = pending` is never emitted as a rotation job; its backfill job stops at 90 days or the vendor's depth, sets `done` or `capped`, and sets `next_poll_at = now()`.
11. A new post opens a +1 h, +6 h, +24 h, +3 d series for fb-group-comments-fetcher, and vendor keys never appear in logs.

## 14. Open questions

1. Vendor parameters, page size, ordering and pagination depth: to be confirmed in the pilot.
2. Does the vendor's response carry member count for tiering and counts per post?
3. Which vendor is primary? Proposed: ScrapeCreators, at USD 0.99 to 1.88 per 1,000 requests against USD 1.99 to 4.83 per 1,000 credits.
4. Who verifies the owners of both vendors, and by when?
5. Should raw-archiver redact the plain poster id and name once the poster is classed as an individual?
6. Should post counts be refreshed after the first read, and by which service?
