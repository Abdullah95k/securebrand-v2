# tg-channel-posts-poller

**Platform:** Telegram · **Route:** amber (optional, flag `TG_POSTS_ACTOR`) · **Lane:** Fetch posts · **Owner:** Backend lead, Telegram adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Telegram is 2.4M of the 30.5M items a month at full scale, and outlets, officials and brands run public channels there. Telegram offers no clean way to read other people's channels. The Bot API sees only channels where our bot is an administrator and discussion groups where it is a member. Telegram's Content Licensing Terms prohibit access "for any purpose other than ordinary, legitimate, and intended use of the Telegram platform as its user", which rules out user-account readers and, on our reading, t.me previews as our own collection. So the posts of a third-party channel can only be bought from a vendor that does the collection itself: the Apify t.me preview Actors (tugelbay/telegram-posts-scraper and sovereigntaylor/telegram-scraper). That is why the route is amber: optional, behind the flag `TG_POSTS_ACTOR` (off, tugelbay or sovereigntaylor), disclosed in the provenance statement, and excluded from government contracts. Comments on third-party channels have no route at all; the Actors return them mostly not at all.

tg-channel-posts-poller reads the registered third-party channels through those Actors. Without it, Telegram in the product is limited to channels that added our bot (tg-bot-channel-receiver) and to keyword hits inside tg-message-search's windows: no monitoring of the outlets, official channels and competitors nobody has onboarded, no views or forwards, and no way to keep the freshness promise (every registered channel re-checked within its tier's interval) on Telegram. Telegram data is also politically exposed for a government client after Iraq's blocks in Aug 2023 and from 3 Apr to 9 May 2026, so the service runs outside Iraq and the flag is a one-step kill switch.

## 2. Objective (the end state this service delivers)

Every amber Telegram channel in the registry with an active tier is read on its tier's cadence, every new post reaches `raw.items` within one tier interval of appearing in the channel, and a channel's cursor advances only after Redpanda has acknowledged the batch. Target: rotation lag below one tier interval for 99% of channels per day, staleness p95 within the tier maximum (1 h, 6 h, 24 h), zero jobs lost, and monthly spend inside the `tg_apify_posts` cap of about USD 2,900 to 7,200 a month at 2.4M items.

## 3. Scope

### In scope

- Rotation scheduling of every amber Telegram channel by tier (1, 2, 3, push reconciliation, dormant) and execution of the jobs on `jobs.tg-channel-posts-poller`.
- Grouping due channels into batches and running one Apify Actor run per batch.
- Incremental reads from the cursor; the first read of a new channel on a `backfill` job from backfill-orchestrator.
- Writing `raw.items` (kind `post`) with views and forwards; advancing cursors; promoting dormant channels; `rotation_behind` catch-up.
- The +24 h views refresh for Tier 1 posts (5.1); switching between the two Actors through the flag.

### Out of scope

- Comments: no route exists; comments under a client's own channel come from tg-discussion-receiver.
- Keyword search (tg-message-search); finding and resolving channels (tg-channel-resolver); channels where our bot is administrator (tg-bot-channel-receiver); tier and registry decisions (qualifier, registry-writer).
- Any collection of our own: no user-account reader, no t.me requests from our servers, no private channels.
- Deduplication (normalize-item) and keyword matching (keyword-matcher).

## 4. Users and consumers

- **Clients** experience it as "new posts from the Telegram channels I watch, never older than my tier allows", with a provenance note that the route is vendor-sourced. Clients under a government contract never receive amber data.
- **Ops** watches rotation lag, spend and Actor health, can switch the flag and can force a read of one channel.
- **Downstream:** normalize-item (consumes `raw.items`), comment-decay-scheduler (views-refresh jobs), raw-archiver, source-health-canary, quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.tg-channel-posts-poller`, partitioned by `source_id`, emitted by the rotation scheduler inside this service (one leader replica elected through a Postgres advisory lock; the scan period is an environment variable well inside the 60-minute Tier 1 interval). The scheduler selects `sources` rows with `platform = telegram`, `source_type = channel`, `route = amber`, `health != blocked`, `backfill_status in (done, capped)` and `next_poll_at <= now()`. A channel is selected only if at least one of its clients accepts amber data (the government flag in `clients` is false); a channel watched only by government clients is never read here, so nothing is paid for data nobody may use. With the flag `off` the scheduler emits nothing and cursors stay untouched.

**Cadence by tier** (subscribers take the place of followers). Tier 1 (100,000 or more subscribers, or on a client's priority list): every 60 minutes, maximum staleness 1 hour. Tier 2 (10,000 to 99,999): every 6 hours. Tier 3 (below 10,000): every 24 hours. Push (channels where tg-bot-channel-receiver holds our bot as administrator): no polling for new posts; one reconciliation read a day, because the bot has no history method and this read is the only way to see a post the receiver missed. Dormant (no post in 30 days): weekly; a new post promotes the channel back to its reach tier through `source.events` (`tier change`). Retired: never read.

**Keeping every channel on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + interval`), so cadence is fixed and does not drift with run time. Jobs are emitted ordered by `next_poll_at` then by tier, so an overdue Tier 3 channel is not pushed aside by Tier 1 channels and no channel is skipped twice in a row. A channel is in at most one job at a time (partition key). A failed job keeps its old `next_poll_at`, making the channel the first candidate on the next scan.

**Batches.** A batch assembler in the worker groups due jobs of the same tier into one Actor run. Batches never mix tiers, so the cursors in a batch lie within one interval of each other and the shared `since` over-reads little. Batch size and the longest wait for a batch to fill are environment variables fixed in the pilot; Tier 1 batches are sent without waiting.

**Catch-up.** `rotation_lag_seconds` is now minus `next_poll_at` of the most overdue channel. When it exceeds one interval, the scheduler orders by most-stale-first and raises `rotation_behind`. Every read is incremental from the cursor, so a late read still returns everything since the cursor, within the max-posts cap; a channel whose gap exceeds the cap is marked `gap_possible` in `service_runs` and ops is told.

**Stretching on cost.** Every batch asks quota-governor for allowance under `tg_apify_posts`. When 80% of the monthly budget is consumed, the governor stretches intervals: backfill jobs pause first, then views refreshes, then Tier 2, then Tier 1. No tier is ever stretched beyond 24 hours; Tier 3 stays daily and dormant stays weekly. The admin page tells clients when freshness has been relaxed.

**Backfill on add.** A new channel arrives with `backfill_status = pending`. backfill-orchestrator emits one `backfill` job: read the last 90 days or the route's max-posts cap, whichever is smaller; the service sets `done` or `capped` and `next_poll_at = now()`, and only then does the rotation pick the channel up. Backfill is billed per item and is the lowest priority at the governor.

**Views refresh.** Views and forwards keep growing after a post appears. Because every re-read item is billed like a new one and would multiply the 2.4M items behind the cost estimate, v1 refreshes only Tier 1 posts, once, at +24 h, on a `metrics` job from comment-decay-scheduler; the +7 d refresh is off. There is no comment series on this route.

### 5.2 Step by step

1. Consume jobs; read `TG_POSTS_ACTOR` at the start of the batch (the flag is never cached). Drop channels with no amber-accepting client, acknowledging them with reason `no_amber_client`.
2. Ask quota-governor for allowance under `tg_apify_posts` for the batch's expected item count; on wait-until requeue for that time; on deny count `quota_denied_total` and keep `next_poll_at`.
3. Build the Actor input: channel usernames from `sources.handle`; max posts per channel, adaptive: twice the channel's median posts per interval over the last 14 days, bounded by the route cap; `since` = the oldest cursor in the batch.
4. Start the run with the vendor token from `vendor_keys`; wait for completion; read the dataset.
5. Group items by channel; drop items older than that channel's cursor. If every item returned is newer than the cursor and the count equals max posts, the read was saturated: requeue the channel at once with a doubled cap, up to the route cap.
6. Write one `raw.items` per post; raw-archiver lands the batch under `raw/amber/telegram/<yyyy>/<mm>/<dd>/tg-channel-posts-poller/`.
7. After Redpanda acknowledges: per channel set `cursor` to the newest post time seen, `last_success_at`, `consecutive_errors = 0`, `last_polled_at`, `next_poll_at`; emit `tier change` for a dormant channel that posted; report the run's cost to the governor.

### 5.3 The call it makes

Start one run of the Actor named by `TG_POSTS_ACTOR` (`tugelbay/telegram-posts-scraper` or `sovereigntaylor/telegram-scraper`) on the Apify platform with the vendor token from `vendor_keys` (Supabase Vault), then read the run's dataset. The input carries three things; the field names are to be confirmed in the pilot and differ between the two Actors, so each has its own input mapper behind the `listening-sdk` adapter contract:

```
channels  : ["iq_example_news", "iq_example_gov", ...]   usernames from sources.handle, no @, no t.me prefix
max posts : <per-channel cap>                             adaptive, never above the route cap
since     : <ISO date-time: oldest cursor in the batch>
```

Pagination: the dataset is read in pages until exhausted (page size to be confirmed in the pilot). Run mode (wait or webhook), memory, timeout, concurrency and channels per run: to be confirmed in the pilot. No proxy, cookie, login or account parameter is ever set: the vendor does the collection and this service never contacts t.me.

### 5.4 What it gets

Per post: channel username, message id, permalink, post time, text, view count, forward count, and media indicators where the preview exposes them (to be confirmed in the pilot). Illustrative item (field names depend on the Actor):

```json
{
  "channel": "iq_example_news",
  "messageId": 48213,
  "url": "https://t.me/iq_example_news/48213",
  "date": "2026-10-06T08:47:31+00:00",
  "text": "الدوام الرسمي غدا في جميع الدوائر",
  "views": 18420,
  "forwards": 233,
  "hasMedia": true
}
```

What it does not get: comments (mostly unavailable); reactions by type; the identity of a post's author beyond the channel; private channels and channels whose owners disabled the web preview; deleted posts; guaranteed completeness (a preview is not an API).

## 6. Inputs and outputs

### 6.1 Reads

`jobs.tg-channel-posts-poller` (kinds `rotation`, `reconciliation`, `backfill`, `metrics`, `ops_force`); `sources`, `cursors`, `clients` (government flag), `vendor_keys`, `budgets` through quota-governor, `canary_targets`; `source.events` to refresh its view of the rotation; the flag `TG_POSTS_ACTOR`.

### 6.2 Writes

`raw.items`, one message per post, envelope plus the record exactly as the Actor returned it:

```json
{
  "envelope": {
    "platform": "telegram", "kind": "post", "route": "amber", "vendor": "apify_tugelbay",
    "service": "tg-channel-posts-poller",
    "source_id": "3a7d9e54-6c0b-4f12-8e37-b1c24d90f6a8",
    "platform_id": "iq_example_news/48213",
    "idempotency_key": "telegram:post:iq_example_news/48213",
    "job_id": "01J9N5C3R8V2K7T4X0M6Q1HZDE", "attempt": 1,
    "fetched_at": "2026-10-06T09:21:17Z",
    "retention_class": "vendor_agreed",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/amber/telegram/2026/10/06/tg-channel-posts-poller/000045.jsonl.zst",
    "metrics_observation": "poll"
  },
  "payload": { "...": "the item object from 5.4, unchanged" }
}
```

`client_ids` lists only clients that accept amber data. A views refresh carries `metrics_observation = refresh_24h`. Also `source.events` (`tier change`), `service_runs`, `dlq.tg-channel-posts-poller` after 5 failed attempts.

### 6.3 State

`cursors.cursor` = ISO time of the newest post stored through this service, plus `last_success_at`, `last_error`, `consecutive_errors`; `sources.last_polled_at`, `next_poll_at`, `health`; `budgets` counters in USD; in memory only the leader lock, batch buffers and backoff state.

## 7. Limits, quotas and cost

- Budget tag `tg_apify_posts`. Apify Telegram preview Actors cost about USD 2,900 to 7,200 a month at 2.4M items, which is about USD 1.2 to 3.0 per 1,000 items (derived from that range; each Actor's own price list is to be confirmed in the pilot).
- The governor holds the monthly cap in USD and counts the usage cost Apify reports for each run (field to be confirmed in the pilot); it stretches intervals at 80% and denies at 100%.
- Actor concurrency, memory, run time and max posts per channel: to be confirmed in the pilot.
- Re-reads are billed: the 24 h views refresh for Tier 1 and the saturation requeue add items on top of 2.4M; their share is to be measured in the pilot.
- Retention class `vendor_agreed`: default 24 months for raw text. Amber data is excluded from government contracts.

## 8. Failure handling and fallback

- HTTP 429 and vendor rate-limit responses: exponential backoff with jitter from 30 s to 15 min, then requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.tg-channel-posts-poller` and an alert fires.
- HTTP 401 and 403: mark the vendor token `degraded`, stop the batch, alert; never rotate accounts, tokens or IPs around a block.
- A run that fails or times out: its channels are requeued individually; a batch that fails twice is split in two, so one channel that breaks the Actor is isolated.
- Empty run (run succeeds, no items for channels known to post): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`. The alternate route is the other Actor: ops, or the canary where ops has approved it, switches `TG_POSTS_ACTOR`, recorded as `fallback_on` and later `fallback_off` in `source.events`. If both Actors fail the route is `off` and the coverage page says so.
- Channel unreadable (not found, preview disabled): counted in `channel_unreadable_total`; repeated failures raise `consecutive_errors` and are reported to ops and the qualifier.
- Schema change: the raw payload is still archived; normalize-item raises `schema_unknown` and parks the batch. The envelope's `vendor` tells normalize-item which mapper applies.
- Partial write: cursors move only after acknowledgement; a replayed job re-emits the same posts and normalize-item deduplicates them.

## 9. Non-functional requirements

- Throughput: 2.4M items a month is about 80,000 a day and about 3,300 an hour on average; channel count and Actor concurrency are to be measured in the pilot.
- Latency: a post visible in the preview reaches `raw.items` within its tier interval plus run time.
- Idempotency: `telegram:post:<username>/<message_id>`; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on queue depth; one leader scheduler.
- Security: vendor token from Supabase Vault per job, never logged; hosted outside Iraq; no account pools, no proxies, no CAPTCHA solving; provenance (route, vendor, service, fetch time) on every message; Node (TypeScript).

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total` (USD), `quota_denied_total`, `dlq_total`, plus `actor_runs_total{actor,status}`, `channels_in_rotation{tier}`, `channel_unreadable_total`, `saturated_reads_total`. Alerts: `rotation_behind`, `token_degraded`, `dlq_nonempty`, `empty_run_rate` (above 5% in 15 minutes), `budget_80_percent`, `quota_deny_rate`. SLO: rotation lag below one tier interval for 99% of channels per day.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, comment-decay-scheduler, backfill-orchestrator, tg-channel-resolver (supplies handles), tg-bot-channel-receiver (push channels), registry-writer, Supabase Postgres and Vault, Redpanda, an Apify contract.

## 12. Risks and mitigations

- The vendor's collection may breach Telegram's terms: the breach, if any, sits in the vendor's contract; the route is optional, flag-gated, disclosed and excluded from government contracts; `TG_POSTS_ACTOR = off` stops it at once.
- Cost overrun: the governor's cap, the 80% stretch and the cost-aware views refresh; the pilot measures real USD per 1,000 items before any client is promised Tier 1 coverage of many channels.
- An Actor breaks when Telegram changes the preview: two Actors, canary targets, `fallback_on`.
- An Iraqi block changes what Iraqis post, not what an Actor can read: canary targets include channels outside Iraq, so a block is not mistaken for a fault.
- The preview omits posts: the provenance statement says coverage is not guaranteed.

## 13. Acceptance criteria

1. A Tier 1 channel whose poll started at 09:00:00 has `next_poll_at = 10:00:00` even when the run took 6 minutes.
2. With 100 fixture channels across three tiers against a simulated Actor for 24 hours, no channel's `rotation_lag_seconds` exceeds its tier interval.
3. A batch never contains channels of two tiers.
4. With `TG_POSTS_ACTOR = off` no Actor run starts and no cursor changes; switching it to `sovereigntaylor` makes the next batch use that Actor's input mapper and envelope `vendor = apify_sovereigntaylor`.
5. A channel watched only by a government client is never selected; a channel watched by one government and one commercial client produces messages whose `client_ids` contain only the commercial client.
6. A read that returns max posts items, all newer than the cursor, requeues the channel at once with a doubled cap; the cursor does not advance past the oldest unread gap.
7. Replaying one job twice yields two `raw.items` messages with the same `idempotency_key`; normalize-item stores one item. The cursor does not advance when the Redpanda produce fails.
8. At 80% of the `tg_apify_posts` monthly budget the governor stretches Tier 2 before Tier 1, no interval exceeds 24 hours, and backfill jobs are deferred first.
9. A 429 is retried with backoff from 30 s to at most 15 min; the fifth failed attempt lands in `dlq.tg-channel-posts-poller` with an alert (ADR-0057). A 401 stops the batch, marks the token `degraded` and fires `token_degraded`.
10. Every `raw.items` message carries `route = amber`, `vendor`, `service`, `fetched_at`, `retention_class = vendor_agreed` and the raw item unchanged.

## 14. Open questions

1. Field names, and whether each Actor returns views and forwards for every post: confirmed in the pilot.
2. Does `since` take a time or only a date? If only a date, hourly Tier 1 reads re-read up to a day of posts and the tier model must be re-costed; the adaptive max-posts cap and saturation rule are the fallback.
3. Which Actor is primary? Proposed: run both on one fixture of 50 channels for a week and compare completeness, USD per 1,000 items and failure rate.
4. Canonical post id when a channel is reached by both routes: proposed `<lowercase username>/<message_id>` on every route, to be agreed with tg-bot-channel-receiver and tg-channel-resolver.
5. Is the Tier 1 +24 h views refresh worth its cost, and should Tier 2 get it?
