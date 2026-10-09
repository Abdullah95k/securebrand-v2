# fb-backfill

**Platform:** Facebook · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, Facebook adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A client who adds a competitor's Page today wants to see what that Page said last month, not only what it says from tomorrow. The rotation (fb-page-feed-poller) is deliberately incremental: it reads only what is newer than the cursor, so without a separate first read every new Page would start with an empty history. fb-backfill is that first read. Once per added Page it fetches the last 90 days of posts from the Graph API `/feed` edge under Page Public Content Access (PPCA), within the route's cap, and then hands the Page to the rotation with a cursor set at the newest post.

Without it, dashboards for newly added Pages would be blank for weeks, share-of-voice comparisons would be skewed toward Pages added earlier, and ops would be tempted into ad-hoc reads that bypass cursors, quotas and provenance. The service also answers "re-read this Page" requests from ops or a client, for instance after a token outage.

## 2. Objective (the end state this service delivers)

Every green Facebook Page added to the registry has its last 90 days of posts (or everything the ranked feed returns, whichever is smaller) in `raw.items` within 24 hours of being added, with `backfill_status` set to `done` or `capped` and the rotation cursor seeded, so fb-page-feed-poller continues seamlessly. Target: 100% of added Pages reach `done` or `capped`; no Page is polled by rotation before its backfill finishes; zero jobs lost.

## 3. Scope

### In scope

- One backfill job per `source.events` `added` event for a green Facebook Page, dispatched by backfill-orchestrator onto `jobs.fb-backfill`.
- Paging backwards through `/feed` between `since = now − 90 days` and `until = now`, with the same field list as fb-page-feed-poller so reaction summaries land with each post.
- Resumable progress (the moving `until` is the cursor), `capped` detection, cursor hand-over to fb-page-feed-poller, `backfill_status` transitions `pending → running → done | capped`.
- On-demand re-runs with an explicit window, requested by ops or a client.

### Out of scope

- Rotation polling (fb-page-feed-poller); comments on backfilled posts (fb-post-comments-fetcher via comment-decay-scheduler); metrics refresh (fb-reactions-fetcher).
- Groups (fb-group-posts-poller, amber). Client-owned Pages are backfilled here with the Page access token, since fb-client-webhook-receiver has no history.
- Individuals: never backfilled; a job whose source is not `source_type = page` is rejected without a call.
- Reels: not on `/feed` under PPCA.

## 4. Users and consumers

- **Clients** see history appear for a Page shortly after adding it; they never call the service.
- **Ops** triggers re-runs and watches `backfill_status` and the queue of Pages waiting on quota.
- **backfill-orchestrator** dispatches jobs here; **fb-page-feed-poller** takes over at the cursor this service writes; **normalize-item**, **comment-decay-scheduler** and **fb-reactions-fetcher** consume the items like any other.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** backfill-orchestrator consumes `source.events` `added` and emits a job on `jobs.fb-backfill` (partitioned by `source_id`) with `window_start = added_at − 90 days`, `window_end = added_at`, `reason = add`. A second trigger is an on-demand job (`reason = ops | client`) carrying an explicit window; the window is clipped to 90 days.

**Not a rotation.** This service runs once per Page per trigger; it has no tier cadence. Its place in the rotation story is the hand-over: a Page with `backfill_status in (pending, running)` is excluded from fb-page-feed-poller's scheduler, and the moment this service writes `done` or `capped` it also sets `next_poll_at = now()` so the Page is picked up on the scheduler's next scan without waiting for a full tier interval.

**Ordering and catch-up.** When many Pages are added at once (a seed list at onboarding), backfill-orchestrator orders jobs by tier then by `added_at`, and quota-governor meters them so that rotation polls keep priority. A job denied by quota is requeued with the governor's wait-until and the Page stays `pending`; `backfill_lag_seconds` (now minus `added_at` for the oldest pending Page) above 24 hours raises an alert.

**Comment decay for backfilled posts.** Backfilled posts reach comment-decay-scheduler through `items.normalized` like any post. The series (+1 h, +6 h, +24 h, +3 d, +7 d, weekly until day 30; early stop below 5% and 5 new comments; extension every 2 days when day 7 still adds 20% or more; hourly inserts for 6 hours above 100 new comments per hour) is aligned to `created_time`, so a post 10 days old on arrival enters at the weekly step and a post older than 30 days gets no automatic fetch (open question 1). The envelope's `metrics_observation = backfill` tells fb-reactions-fetcher to record the counts as an observation at fetch time, not as a +24 h or +7 d point.

### 5.2 Step by step

1. Consume the job; set `backfill_status = running`; read the `cursors` row for (`source_id`, `fb-backfill`), which holds the last `until` reached if this is a resumed attempt.
2. Select the token as fb-page-feed-poller does: the system-user token of the first healthy client in `client_ids`, or the client's Page access token for `owned_by_client` Pages, injected from Supabase Vault for this job.
3. Ask quota-governor for allowance under `budget_tag = meta_graph_pages:<client_id>` for the first page; ask again before every further page.
4. Call `/feed` with `since = window_start`, `until = <cursor or window_end>`, `limit = 100`; follow `paging.next` (which carries the moving `until` and paging token) until the response is empty or every post is older than `window_start`.
5. After each page is acknowledged by Redpanda, write the page's oldest `created_time` as the `fb-backfill` cursor; on error 80001 or a quota deny mid-way, stop, keep the cursor, requeue with `attempt + 1` (the next attempt resumes from the cursor; posts re-read on the boundary are deduplicated by normalize-item).
6. On completion: write the fb-page-feed-poller cursor as the newest `created_time` seen (or `window_end` when the feed returned nothing); set `backfill_status = done`, or `capped` when the run ended before `window_start` for a route reason (paging exhausted while the oldest post is newer than `window_start` and the Page's observed posting rate implies more, or 5 failed attempts); set `next_poll_at = now()`; emit `source.events` `updated`.
7. Record the metrics of section 10.

### 5.3 The call it makes

```
GET https://graph.facebook.com/v<pinned>/{page-id}/feed
  ?fields=id,message,story,created_time,updated_time,permalink_url,status_type,
          full_picture,attachments{media_type,type,url,title,description},shares,
          comments.summary(total_count).limit(0),
          reactions.type(LIKE).summary(total_count).limit(0).as(like),
          <same for LOVE, HAHA, WOW, SAD, ANGRY, CARE>
  &limit=100
  &since=<unix timestamp: window_start>
  &until=<unix timestamp: window_end, then the moving until from paging.next>
  &access_token=<system-user token (PPCA); Page access token for owned_by_client Pages>
```

Page size `limit` max 100; pagination by `paging.next`. The field list is a shared SDK constant with fb-page-feed-poller.

### 5.4 What it gets

The same post objects as fb-page-feed-poller (section 5.4 there). It does not get Reels, comments, commenter identity, or posts Meta's ranking drops: `/feed` returns about 600 ranked posts per Page per year, so a Page that posts far more often than that has a 90-day window with gaps, which is what `capped` records.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.fb-backfill`; `sources` (`client_ids`, `owned_by_client`, `backfill_status`), `cursors`, `clients`, `budgets` through quota-governor, `health` through the SDK canary hook.

### 6.2 Writes

`raw.items`, one message per post, kind `post`, envelope identical to fb-page-feed-poller's except `service` and `metrics_observation`, with `window` as a declared field of the envelope's `context` (ADR-0005, ADR-0070):

```json
{
  "envelope": {
    "platform": "facebook", "kind": "post", "route": "green", "vendor": null,
    "service": "fb-backfill",
    "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
    "platform_id": "100064583471102_1176002458962861",
    "idempotency_key": "facebook:post:100064583471102_1176002458962861",
    "job_id": "01J9N3A1C7Q2W8E5R4T6Y9U0I3", "attempt": 2,
    "fetched_at": "2026-10-06T11:02:17Z",
    "retention_class": "meta_on_request",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/facebook/2026/10/06/fb-backfill/000007.jsonl.zst",
    "metrics_observation": "backfill",
    "window": {"start": "2026-07-08T11:00:00Z", "end": "2026-10-06T11:00:00Z"}
  },
  "payload": { "id": "100064583471102_1176002458962861", "message": "...", "created_time": "2026-08-19T14:03:55+0000", "...": "unchanged post object" }
}
```

Also `source.events` `updated` (with `backfill_status`), `sources.backfill_status`, `next_poll_at`, the fb-page-feed-poller cursor, `service_runs`, `dlq.fb-backfill`.

### 6.3 State

`cursors` row (`source_id`, `fb-backfill`): `cursor` = oldest `created_time` reached (the resume point), `last_success_at`, `last_error`, `consecutive_errors`. `sources.backfill_status`, `notes` (reason for `capped`). `budgets` counters per token.

## 7. Limits, quotas and cost

- The Pages bucket allows 4,800 calls × engaged users per 24 h on a system-user token; a backfill is the most call-hungry thing a Page causes (one call per 100 posts over 90 days), so quota-governor meters it below rotation.
- Error 80001 ("too many calls to this Page") stops the run and keeps the resume cursor.
- `/feed` returns about 600 ranked posts per Page per year with `limit` max 100: the 90-day window is only as complete as the ranking allows; `capped` and the provenance statement disclose this.
- The 90-day window is the rotation policy's cap for every route; it is never extended by this service.
- Cost: USD 0 per Graph call. Calls per added Page and the daily backfill capacity per token: to be measured in the pilot.

## 8. Failure handling and fallback

- HTTP 429 and 80001: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1` and the resume cursor; after 5 attempts `dlq.fb-backfill`, `backfill_status = capped` with the reason in `notes`, and an alert.
- HTTP 401 and 403: token marked `degraded`, run stopped, alert; no retries with other tokens or IPs.
- Empty 200 on a Page known to have posts: counted; above 5% in 15 minutes source-health-canary flips `health = degraded`; there is no amber fallback for Page history.
- Schema change: payload archived; normalize-item parks the batch with `schema_unknown`; paging continues.
- Partial writes: the cursor advances per acknowledged page, so a replayed attempt re-reads at most one page.
- A Page retired or deleted mid-run: the job ends, `backfill_status = capped`, `notes` says why.

## 9. Non-functional requirements

- Throughput: bounded by quota, not compute; the service drains a seed list of Pages (count to be measured in the pilot) without starving rotation.
- Latency: `done` or `capped` within 24 hours of `added_at` when quota allows.
- Idempotency: `facebook:post:<platform_id>`; jobs replayable from the resume cursor; `raw.items` append-only.
- Scaling: workers scale on partition lag of `jobs.fb-backfill`; one Page in one job at a time.
- Security: tokens per job from Supabase Vault, never logged; no proxies or account pools; Meta data never processed for law-enforcement or national-security purposes; provenance on every message; retention `meta_on_request`.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `backfill_lag_seconds`, `backfill_duration_seconds`, `backfills_total{status = done | capped}` and `pages_pending_backfill`. Alerts: `backfill_lag` (oldest pending above 24 hours), `backfill_capped_rate` (share of `capped` runs rising, threshold to be measured in the pilot), `token_degraded`, `dlq_nonempty`.

## 11. Dependencies

listening-sdk (shared `/feed` field list and envelope), backfill-orchestrator, quota-governor, source-health-canary, raw-archiver, normalize-item, comment-decay-scheduler, fb-reactions-fetcher, fb-page-feed-poller (cursor hand-over), registry-writer, Supabase Postgres and Vault, Redpanda. Meta prerequisites: Business Verification, App Review for PPCA, Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- Onboarding spikes exhaust the Pages bucket and stall rotation: backfill is metered below rotation and ordered by tier; the client is told which Pages are queued.
- Ranked feed makes history incomplete: `capped` is explicit in the registry and the provenance statement; clients are encouraged to connect their own Pages, where webhooks are complete going forward.
- Comment history: backfilled posts older than 30 days get no comment series under the current policy, so their comment counts come only from the feed summary; see open question 1.
- Repeated re-reads of one Page: re-runs require a recorded ops or client request and count against the client's budget.

## 13. Acceptance criteria

1. Adding a fixture Page with 250 simulated posts over 90 days produces 250 `raw.items` messages with `service = fb-backfill`, `backfill_status = done`, and the fb-page-feed-poller cursor at the newest `created_time`.
2. fb-page-feed-poller emits no job for the Page while `backfill_status in (pending, running)`, and emits one within its next scan after `done`.
3. A simulated 80001 on API page 3 of 5 stops the run with the resume cursor at the oldest post of page 2; the next attempt starts from that `until` and the total set of distinct `idempotency_key`s equals the fixture.
4. After 5 failed attempts the job is in `dlq.fb-backfill`, `backfill_status = capped`, `notes` names the reason, and an alert fired.
5. A fixture Page whose feed ends 40 days back despite a posting rate of several posts a day is marked `capped`; one that only started posting 40 days ago is marked `done`.
6. A job for a source with `source_type != page` is rejected without any Graph call.
7. The field list used in the request is byte-identical to fb-page-feed-poller's (shared SDK constant test).
8. Every message carries `metrics_observation = backfill`, `retention_class = meta_on_request`, `route = green`, `fetched_at`, and the window.
9. An on-demand re-run with a 200-day window is clipped to 90 days and logged as `reason = ops`; tokens never appear in logs or envelopes.

## 14. Open questions

1. Comment fetches for backfilled posts: the policy gives no automatic fetches beyond day 30, which leaves 60 of the 90 backfilled days without comment text. Proposal for comment-decay-scheduler: one comment fetch per backfilled post older than 30 days, budget permitting; Abdullah to decide against the quota measured in the pilot.
2. The `capped` heuristic (posting-rate gap) needs a threshold: to be measured in the pilot against Pages with known histories.
3. Whether on-demand re-runs are exposed to clients or stay an ops action in the first release.
