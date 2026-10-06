# tt-client-videos-fetcher

**Platform:** TikTok · **Route:** green · **Lane:** Fetch posts · **Owner:** Ingestion lead (Node) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

TikTok has no green route to third-party content: Research Tools are academic and non-profit only, the Commercial Content API covers EU paid ads, and the Mentions API is for badged Marketing Partners. Every other TikTok service in the product (tt-keyword-search, tt-hashtag-feed-poller, tt-profile-videos-poller, tt-video-comments-fetcher, tt-video-stats-refresher, tt-user-resolver) therefore rests on an amber vendor, is optional behind `TT_VENDOR_ROUTE`, and is excluded from government contracts. tt-client-videos-fetcher is the one exception. When a client connects its own TikTok account through TikTok's OAuth, the Display API lets us read that account's own videos and their counts under a permission the client gave us, and nobody else's.

Without it a client's own TikTok account would be read through the amber vendor like a stranger's: own-brand data carrying amber provenance, costing vendor money, vanishing when the flag is off, and never available to a government client. With it, a client's own videos and stats arrive hourly at no vendor cost, on a route we can defend to anyone. It is also the cleanest data in the TikTok stream: complete (every video the account posts), not a ranked sample.

## 2. Objective (the end state this service delivers)

Every client-authorised TikTok account has its own videos and their counts read every hour with a valid token, new videos reach `raw.items` within one hour of publication, and an authorisation that is lapsing or revoked is noticed and reported to the client before data is missed. Target: rotation lag below 60 minutes for 99% of authorised accounts per day; zero tokens expired without a refresh attempt and a client notice; zero jobs lost; USD 0 of vendor spend.

## 3. Scope

### In scope

- Hourly reads of `video.list` for every authorised account; writing `raw.items` (kind `post`) for new videos with first-sight counts.
- The +24 h and +7 d count observations for each video, taken from the hourly reads and written to `item.metrics`.
- Using and refreshing the client's OAuth tokens; detecting revocation; the 90-day backfill job from backfill-orchestrator.
- Reading `user.info.basic` once at connection to record the account's display name.

### Out of scope

- The OAuth consent screen and the first token exchange (the client portal; this service uses what the portal stored in Supabase Vault).
- Comments: the Display API has no comments endpoint. Where the client's contract allows amber data, tt-video-comments-fetcher may read them; otherwise there are none.
- Any account the client has not authorised; posting or publishing; audience analytics beyond the counts; direct messages.
- Deduplication (normalize-item), tier decisions (qualifier, registry-writer).

## 4. Users and consumers

- **Clients** (including government clients) see their own TikTok performance next to their competitors', labelled green.
- **Ops** watches token health and can force a poll of one account.
- **Downstream:** normalize-item, store-writer, comment-decay-scheduler, raw-archiver, source-health-canary, quota-governor; tt-profile-videos-poller, whose daily reconciliation is the only second route for these accounts.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.tt-client-videos-fetcher`, partitioned by `source_id`, emitted by the rotation scheduler inside this service (one leader replica elected through a Postgres advisory lock; the scan period is an environment variable well inside 60 minutes). It selects `sources` rows with `platform = tiktok`, `route = green`, `owned_by_client = true`, `health != blocked`, `backfill_status in (done, capped)` and `next_poll_at <= now()`.

**Cadence.** Every authorised account every 60 minutes, whatever its follower count or recent activity: the account is the client's own, a Display API read costs no money, and a client who posts after a quiet month expects to see it within the hour, so the dormant weekly step of the rotation policy is not used here. The registry marks these accounts `tier = push`, so tt-profile-videos-poller makes only its one reconciliation poll a day for them. Retired (authorisation revoked or expired, client offboarded): never polled.

**Keeping every account on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + 60 minutes`), so cadence is fixed and does not drift with fetch time. Jobs are ordered by `next_poll_at`, so no account is skipped twice in a row. An account is in at most one job at a time (partition key), which also means one token refresh at a time. A failed job keeps its old `next_poll_at`.

**Catch-up.** When `rotation_lag_seconds` exceeds one interval the scheduler switches to most-stale-first and raises `rotation_behind`. Reads are incremental from the cursor, so a late poll still returns everything since the cursor. There is no money budget to protect, so quota-governor never stretches this cadence; it can only answer `wait-until` when TikTok's request limits bind.

**Backfill on add.** A newly authorised account arrives with `backfill_status = pending`; backfill-orchestrator emits a `kind = backfill` job, this service pages back 90 days or the API's cap, whichever is smaller, and the rotation takes over once `done` or `capped` is set.

**Metrics.** Each hourly read returns counts with every video, so the observations at +24 h and +7 d after first sight come from the first read at or after each mark. Because this service supplies them, comment-decay-scheduler must not open TikTok metrics jobs for green videos (tt-video-stats-refresher is an amber, vendor-paid service).

### 5.2 Step by step

1. Consume a job (`source_id`, `kind` = rotation | backfill | ops_force, `attempt`); read `sources`, `cursors` and the account's token record from Supabase Vault; stop if `health = blocked`.
2. If the access token's remaining life is below the margin (an environment variable; value set in the pilot), refresh it (section 5.3) and store the new access and refresh tokens together in Vault before using them.
3. Ask quota-governor for allowance under `budget_tag = tt_display:<client_id>`; `wait-until` requeues, `deny` keeps `next_poll_at`.
4. Call `video.list` newest first, following the page cursor, until the 7-day window is covered and a video already stored is reached.
5. For each video not yet stored, write one `raw.items` message. For each stored video whose +24 h or +7 d mark has passed with no observation recorded, write one `item.metrics` message.
6. After Redpanda acknowledges: set `cursor`, `last_success_at`, `consecutive_errors = 0`, `last_polled_at`, `next_poll_at`, and record the observations in `tt_client_video_state`.
7. Record the metrics of section 10.

### 5.3 The call it makes

Display API `video.list`, with the scopes `user.info.basic,video.list` granted in the client's OAuth. Auth: the client's access token as bearer, never a company-wide token. Fields requested: video id, title and description, creation time, share URL, duration, cover image, and the view, like, comment and share counts (exact request path, parameter names, page size and cursor fields: to be confirmed in the pilot). Pagination: cursor with a has-more flag.

Token refresh: a call to TikTok's OAuth token endpoint with `grant_type = refresh_token`, our app's client key and secret (from Vault) and the client's refresh token. The response is stored whole, because it may carry a new refresh token that replaces the old one. Lifetimes are read from the response (`expires_in`, `refresh_expires_in`; names to be confirmed in the pilot), never hard-coded.

### 5.4 What it gets

Per video, as TikTok returns it (illustrative; field names to be confirmed in the pilot):

```json
{
  "id": "7421538806219533573",
  "title": "افتتاح فرع جديد في البصرة #البصرة",
  "create_time": 1759734729,
  "share_url": "https://www.tiktok.com/@basra.store/video/7421538806219533573",
  "duration": 24,
  "view_count": 18420, "like_count": 1310, "comment_count": 142, "share_count": 87
}
```

Not obtained: comments, viewers, likers, audience demographics, other people's videos, videos the account has not made visible to the API.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.tt-client-videos-fetcher`; `sources`, `cursors`, `clients` (token reference), `tt_client_video_state`, `budgets` through quota-governor; Supabase Vault (tokens, app key and secret); `source.events` (`added`, `retired`) to refresh its view of the rotation.

### 6.2 Writes

`raw.items`, one message per new video, envelope plus the record exactly as returned:

```json
{
  "envelope": {
    "platform": "tiktok", "kind": "post", "route": "green", "vendor": null,
    "service": "tt-client-videos-fetcher",
    "source_id": "9a47e0b1-5c3d-4f82-b6e9-1d0c8a3f7e25",
    "platform_id": "7421538806219533573",
    "idempotency_key": "tiktok:video:7421538806219533573",
    "job_id": "01J9N7H4S2P9D6K1X8V3B5WEMC", "attempt": 1,
    "fetched_at": "2026-10-06T09:15:42Z",
    "retention_class": "tiktok_display",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/tiktok/2026/10/06/tt-client-videos-fetcher/000031.jsonl.zst",
    "metrics_observation": "first_sight"
  },
  "payload": { "...": "the video object from 5.4, unchanged" }
}
```

Also `item.metrics` (one message per observation, label `plus_24h` or `plus_7d`, the four counts, `observed_at`, `first_seen_at`, `lateness_seconds`, same envelope fields), `source.events` (`updated` on a token state change, `retired` on revocation), `service_runs`, `dlq.tt-client-videos-fetcher` after 5 failed attempts. `retention_class = tiktok_display` is proposed and not yet in `retention_classes` (question 2).

### 6.3 State

`cursors.cursor` = `create_time` (ISO, UTC) of the newest stored video plus its id, with `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`; `tt_client_video_state` (video id, `first_seen_at`, observation labels written); tokens and expiry times only in Vault; `budgets` counters under `tt_display:<client_id>`; in memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- Price: USD 0 per Display API call; the cost is request quota. TikTok's rate limits per token and per app: to be confirmed in the pilot, held by quota-governor under `tt_display:<client_id>` (green), one counter per client. Nothing is charged to `tt_vendor`.
- Requests per account per day: 24 reads, plus one more page per read for every page of videos beyond the first inside the 7-day window. Accounts and video rates: to be measured in the pilot.
- The scopes `user.info.basic` and `video.list` depend on TikTok's approval of our developer app; lead time to be confirmed in the pilot.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.tt-client-videos-fetcher` and an alert fires.
- HTTP 401: refresh once and retry once. If the refresh fails (refresh token expired or revoked), set `health = blocked`, emit `source.events` `updated`, alert ops and notify the client to reconnect; polling stops for that account, stored data stays.
- HTTP 403 (scope missing or authorisation withdrawn): same handling; the account is `retired` once the client confirms revocation. Never any attempt to get around a block.
- Empty 200 (no videos from an account known to post): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. No amber fallback is ever set here: the vendor is not a fallback for a green route. The only second route is tt-profile-videos-poller's daily reconciliation, and only where the client's contract allows amber data.
- Schema change: payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: cursors move only after acknowledgement; a replayed job re-emits the same videos and normalize-item deduplicates them. A token refresh is idempotent: the new token set is committed to Vault before it is used.

## 9. Non-functional requirements

- Throughput: a handful of requests an hour per account; the number of authorised accounts is to be measured in the pilot.
- Latency: a new video reaches `raw.items` within 60 minutes plus fetch time.
- Idempotency: `tiktok:video:<id>`; observation keys `tiktok:metrics:<video_id>:<label>`; replayable jobs.
- Scaling: stateless workers on partition lag; one leader scheduler; one worker per account at a time.
- Security: tokens per client in Supabase Vault, never logged, never used for another client or for any other account; green items carry only the authorising client's id in `client_ids` and are shown only to that client; no account pools, no proxies; provenance on every message.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `quota_denied_total`, `dlq_total`, plus `accounts_authorised`, `tokens_refreshed_total`, `token_refresh_failed_total`, `tokens_expiring_soon` and `accounts_blocked`. Alerts: `rotation_behind`, `token_refresh_failed`, `authorisation_revoked`, `dlq_nonempty`, `empty_200_rate`. SLO: rotation lag below 60 minutes for 99% of accounts per day.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, store-writer, comment-decay-scheduler, backfill-orchestrator, tt-profile-videos-poller, registry-writer, the client portal (OAuth consent), Supabase Postgres and Vault, Redpanda, and TikTok's approval of our developer app for `user.info.basic` and `video.list`.

## 12. Risks and mitigations

- A token lapses silently and a client's data stops: refresh before every use, the expiring-soon gauge, and a client notice on failure.
- App review for the scopes is slow: the pilot starts with one internal test account.
- `video.list` may not return every video or the full 90 days: provenance says so; the daily reconciliation is the check where amber data is allowed.
- Green and amber data mixed up: separate budget tags (`tt_display:<client_id>` against `tt_vendor`), `route` on every message, and comment-decay-scheduler routing by route.
- Client revokes access: polling stops at once; what happens to stored data is question 3.

## 13. Acceptance criteria

1. An account whose poll started at 09:00:00 has `next_poll_at = 10:00:00` even when the fetch took 4 minutes.
2. With 50 fixture accounts against a simulated Display API for 24 hours, no account's `rotation_lag_seconds` exceeds 60 minutes, and an account with no video for 60 days is still polled hourly.
3. A token with remaining life below the margin is refreshed before the read; the new access and refresh tokens are committed together, and a response carrying a new refresh token replaces the old one.
4. A 401 followed by a failed refresh sets `health = blocked`, emits `source.events` `updated`, alerts ops, and no further call uses that token.
5. A 403 stops the batch without retries on other tokens or accounts.
6. A video first seen at 09:15 gets one `item.metrics` message labelled `plus_24h` from the first read at or after 09:15 the next day and one labelled `plus_7d` after seven days, and no other observation; replaying a read writes none twice.
7. Replaying one job twice yields the same `idempotency_key`; normalize-item stores one video; the cursor does not advance when the Redpanda produce fails.
8. Every message carries `route = green`, `vendor = null`, `service`, `fetched_at`, and `client_ids` holding only the authorising client; no call is charged to `tt_vendor`.
9. With `TT_VENDOR_ROUTE = off`, the service runs unchanged; no code path calls TikHub or EnsembleData.
10. A backfill job reads back 90 days or the API's cap and the account joins the rotation only after `done` or `capped`.
11. After 5 simulated 429s the job is in `dlq.tt-client-videos-fetcher` and an alert fired.

## 14. Open questions

1. TikTok's request limits for `video.list` per token and per app, its page size, and whether it returns every video: to be confirmed in the pilot.
2. Which retention class applies to Display API data? Proposed: a new `tiktok_display` class, data kept while the authorisation is active and deleted on revocation, client offboarding or TikTok's request, as `meta_on_request` does.
3. When a client revokes access, are stored items deleted through `deletions` (reason `authorization_revoked`)? Proposed: yes, unless TikTok's terms allow keeping them.
4. May green items be shown only to the authorising client? Proposed: yes, since the permission is the client's.
5. Should comment-decay-scheduler route TikTok metrics jobs by the video's `route`, so green videos never reach tt-video-stats-refresher? Proposed: yes.
