# tg-bot-channel-receiver

**Platform:** Telegram · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, Telegram adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Telegram lets a program read a channel only if the channel's owner invites it. The Bot API sees only channels where our bot is an administrator and discussion groups where it is a member. Telegram's Content Licensing Terms prohibit access "for any purpose other than ordinary, legitimate, and intended use of the Telegram platform as its user", which rules out user-account readers and, on our reading, t.me previews as our own collection. So the Bot API, used in channels whose owners add our bot, is the only green route to Telegram posts: complete, live, within the terms, and open to every kind of client, including government. Posts of third-party channels come only through the amber Apify preview Actors (tg-channel-posts-poller), and comments on third-party channels have no route at all.

tg-bot-channel-receiver is the service behind that invitation. It receives every post and edit from channels where the bot is an administrator: a client's own channels and cooperating channels whose owners agreed to add the bot. It also walks the owner through adding the bot and checks every day that the bot is still an administrator.

Without it a government client has no Telegram data at all (amber data is excluded from their contracts), a commercial client's own channels depend on a vendor preview that is neither complete nor live, and the product has no clean Telegram story to show a client's lawyer. Telegram data is politically exposed for a government client after Iraq's blocks in Aug 2023 and from 3 Apr to 9 May 2026, so the service runs outside Iraq and takes nothing from channels that did not invite it.

## 2. Objective (the end state this service delivers)

Every post and edit in every channel where the bot is an administrator reaches `raw.items` within seconds of Telegram delivering it, with nothing acknowledged to Telegram before Redpanda has acknowledged it; every such channel's admin status is verified once a day; and a channel owner can add the bot and see the first post stored in minutes. Target: no update lost while the service is up, 100% of registered channels health-checked within 24 hours, and the p95 from receipt to Redpanda acknowledgement to be measured in the pilot.

## 3. Scope

### In scope

- Receiving `channel_post`, `edited_channel_post` and `my_chat_member` updates, by webhook or `getUpdates`.
- The onboarding flow for a channel owner, and the daily health check of every registered channel.
- Writing `raw.items` (kind `post`); emitting the client-added source candidate; reporting lost administrator status.

### Out of scope

- History before the bot joined: the Bot API has no history method, so none is available on this route. An opted-in client can get pre-join posts through tg-channel-posts-poller (amber) only.
- Comments (tg-discussion-receiver); third-party channels (tg-channel-posts-poller); keyword search (tg-message-search); resolving channels (tg-channel-resolver).
- Downloading media bytes, view and forward counts, deduplication (normalize-item), keyword matching (keyword-matcher), tier and registry decisions (qualifier, registry-writer).

## 4. Users and consumers

- **Channel owners** (client staff, or a cooperating outlet) add the bot and see their channel go live in the admin page.
- **Clients** receive their own channels' posts live, with provenance `green`.
- **Ops** sees webhook health, lost-administrator alerts and the onboarding queue.
- **Downstream:** normalize-item, raw-archiver, source-health-canary, registry-writer, poster-resolver (for the candidate).

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Push. Telegram delivers an update to our HTTPS endpoint (webhook mode) or the service long-polls `getUpdates` (the mode is the environment variable `TG_BOT_UPDATE_MODE`; webhook is the default). A bot token has one update consumer, so this service owns the channel bot's; tg-discussion-receiver uses a second bot (open question 3). `allowed_updates` includes `channel_post` and `edited_channel_post`, plus `my_chat_member` to see the bot being promoted or removed.

**No rotation for posts.** Registered channels have `tier = push`, tiered by nothing: there is nothing to poll. The rotation that keeps every channel checked is the health check. A leader replica (Postgres advisory lock) emits one `reconciliation` job per channel to `jobs.tg-bot-channel-receiver` when `next_poll_at <= now()`, ordered by `next_poll_at` then tier. `next_poll_at` is set from the START of the last check (`check_started_at + 24 h`), so cadence is fixed. A failed check keeps its old `next_poll_at` and is first on the next scan, so no channel is skipped twice in a row.

**Dormant and retired.** A channel with no post in 30 days is dormant: nothing to poll weekly, the daily check continues because it is one cheap call. A retired channel is not checked; the bot stays wherever the owner left it and the service never leaves a channel by itself.

**Catch-up.** When `rotation_lag_seconds` exceeds 24 hours the scheduler checks the most stale channels first and raises `rotation_behind`.

**Backfill on add.** None is possible. At onboarding `backfill_status` is set to `capped` (route cap: zero days); the first post received after the bot joined is the first record, and the admin page says so.

**Gaps while we are down.** With a webhook, Telegram redelivers what we did not acknowledge; with `getUpdates`, unread updates are kept for a limited time (documented as 24 hours, to be confirmed in the pilot). An outage longer than that loses posts that no history method can recover; `receiver_outage` is raised and the window is written to `service_runs`. For channels watched by a client that accepts amber data, tg-channel-posts-poller's daily reconciliation read fills the gap.

### 5.2 Step by step

**Update path**

1. Receive an update: webhook (the secret-token header is checked in constant time) or a `getUpdates` batch.
2. Keep `channel_post`, `edited_channel_post` and `my_chat_member`; anything else is archived, counted and ignored.
3. Map the chat to a `source_id` from an in-memory map of registered chats (by chat id and lowercase username), refreshed from `source.events`. An unregistered chat writes nothing: the content is dropped, `unregistered_chat_total` counts it, ops is alerted once per chat.
4. Write one `raw.items` message (`event = new`, or `edit` with `edit_date`) and wait for Redpanda's acknowledgement.
5. Only then answer HTTP 200 (webhook) or advance the `getUpdates` offset. A failed produce returns a non-2xx or leaves the offset, so Telegram redelivers.
6. Set `cursors.cursor` to the newest message id stored; record gaps in message ids as `post_id_gap_total` (deletions and service messages make gaps normal, so this is a signal, not an error).

**Onboarding path**

1. In the admin page the owner enters the channel username, or chooses "private channel". The control plane creates an onboarding record with a one-time code and a pre-allocated `source_id`, and shows the instruction: add the channel bot as an administrator, with the fewest rights Telegram's dialog allows (the bot never posts, edits or deletes). If the channel has a linked discussion group, the same page shows the second step for tg-discussion-receiver.
2. Telegram sends `my_chat_member` (status administrator). The service verifies with `getChatMember` (its own status), reads title, username and type with `getChat` and subscribers with `getChatMemberCount`.
3. It matches the record by username; for a private channel the owner posts the one-time code and the service reads it from the resulting `channel_post` without storing that post.
4. It emits a client-added candidate on `discovery.hits` (type `channel`, `origin = client_onboarding`, `proposed_source_id`, `owned_by_client`, client id). poster-resolver and the qualifier treat it as always qualifying; registry-writer creates the row (`route = green`, `vendor` null, `tier = push`, `added_by = client`). Because the id was pre-allocated, posts arriving before the row exists already land under the right `source_id`.

**Daily check.** For each due channel: `getChatMember` (still administrator?), `getChat` (still reachable, username unchanged), `getChatMemberCount` (refresh `sources.followers`); once a day for the bot, `getWebhookInfo`. A lost administrator role sets `health = blocked`, emits `source.events` (`updated`) and notifies ops and the client; re-adding the bot restores `ok`.

### 5.3 The call it makes

```
POST https://api.telegram.org/bot<token>/setWebhook      (webhook mode)
  allowed_updates = ["channel_post", "edited_channel_post", "my_chat_member"]
POST https://api.telegram.org/bot<token>/getUpdates      (getUpdates mode)
  allowed_updates = the same list; offset = last acknowledged update_id + 1
Daily: getChatMember (the bot's own status), getChat, getChatMemberCount, getWebhookInfo
```

Auth: the bot token, read from `vendor_keys` through Supabase Vault. Parameters other than `allowed_updates` (webhook URL and secret token, long-poll timeout, connection limits) and the exact method set are to be confirmed against the Bot API documentation in the pilot, including that `my_chat_member` fires for promotions and removals in channels.

### 5.4 What it gets

Per post: message id, chat (id, title, username, type), sender chat, date, text or caption with entities, media type with Telegram file ids, `forward_origin` for forwarded posts, `author_signature` where the channel shows signatures, and `edit_date` on edits. Illustrative update:

```json
{
  "update_id": 704118532,
  "channel_post": {
    "message_id": 5127,
    "sender_chat": {"id": -1001849302761, "title": "قناة المثال", "username": "iq_example_owned", "type": "channel"},
    "chat": {"id": -1001849302761, "title": "قناة المثال", "username": "iq_example_owned", "type": "channel"},
    "date": 1791278100,
    "text": "إعلان: صيانة مجدولة للشبكة يوم الخميس"
  }
}
```

What it does not get: posts before the bot joined; view and forward counts (not expected in bot updates, to be confirmed in the pilot, so this route has none and the amber route does); deletions (no update is sent); media bytes (file ids only); comments; anything from a channel where the bot is not an administrator.

## 6. Inputs and outputs

### 6.1 Reads

Telegram updates; `jobs.tg-bot-channel-receiver` (kind `reconciliation`, `ops_force`); `sources`, `cursors`, `vendor_keys`, `canary_targets`, the onboarding records; `source.events` to refresh the chat map.

### 6.2 Writes

`raw.items`, one message per post or edit, the `channel_post` object unchanged:

```json
{
  "envelope": {
    "platform": "telegram", "kind": "post", "route": "green", "vendor": null,
    "service": "tg-bot-channel-receiver", "event": "new", "ingest_mode": "webhook",
    "source_id": "8c41f2d7-5a3e-4b96-a0d1-7e2c9b3f4a58",
    "platform_id": "iq_example_owned/5127",
    "idempotency_key": "telegram:post:iq_example_owned/5127",
    "update_id": 704118532, "attempt": 1,
    "fetched_at": "2026-10-06T09:15:02Z",
    "retention_class": "vendor_agreed",
    "owned_by_client": true,
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/telegram/2026/10/06/tg-bot-channel-receiver/000311.jsonl.zst"
  },
  "payload": { "...": "the channel_post object from 5.4, unchanged" }
}
```

Also `discovery.hits` (client-added candidate), `source.events` (`updated`, health), `service_runs`, `dlq.tg-bot-channel-receiver` after 5 failed attempts on a check.

### 6.3 State

`cursors.cursor` = newest message id stored per channel, plus `last_success_at`, `last_error`, `consecutive_errors`; `sources.next_poll_at`, `last_polled_at`, `health`, `followers`; the `getUpdates` offset; in memory the chat map and the leader lock.

## 7. Limits, quotas and cost

- No price or budget tag applies: CONVENTIONS lists none for the Bot API, which has no per-call charge we know of; confirmed in the pilot. The cost is hosting.
- Outbound calls are three per channel per day plus one `getWebhookInfo`, paced by a client-side limiter; Telegram's flood limits are to be confirmed in the pilot. Inbound updates are not metered and ask quota-governor for nothing.
- Undelivered `getUpdates` retention: documented as 24 hours, to be confirmed in the pilot.
- Retention: `vendor_agreed` (default 24 months for raw text) is proposed; open question 5.

## 8. Failure handling and fallback

- HTTP 429 on outbound checks: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.tg-bot-channel-receiver` and an alert fires.
- HTTP 401 on the bot token: mark the token `degraded`, stop, alert; no other token is tried. HTTP 403 on one chat means the bot was removed from it: that channel is `blocked`, the token is fine.
- Produce failure: nothing is acknowledged to Telegram; redelivery or the held offset replays the update, and the same `idempotency_key` makes it safe.
- Empty-200 equivalent: a company-owned canary channel where the bot is administrator receives a timestamp post once an hour from a canary-only bot; a missing heartbeat above 5% in 15 minutes flips `health = degraded`. No amber fallback exists for owned channels (tg-channel-posts-poller covers third-party channels), so `fallback_on` is never set here.
- Unknown update or message shape: archived, `schema_unknown` raised, batch parked.

## 9. Non-functional requirements

- Throughput: bounded by the number of owned and cooperating channels, a small fraction of Telegram's 2.4M items a month; to be measured in the pilot.
- Latency: seconds from Telegram's delivery to acknowledgement; p95 measured in the pilot.
- Idempotency: `telegram:post:<username or chat id>/<message_id>`; edits reuse the key and normalize-item stores a new version when the content hash changes.
- Scaling: webhook mode runs two replicas behind a load balancer; `getUpdates` mode runs one consumer chosen by advisory lock.
- Security: bot token from Vault; the bot never posts, edits or deletes in a client channel (enforced by a contract test over the SDK client); post text never logged; hosted outside Iraq; a private channel's posts are visible only to the owning client; Node (TypeScript).

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `rotation_lag_seconds` (health checks), `staleness_seconds_p95`, `dlq_total`, plus `updates_received_total{type}`, `unregistered_chat_total`, `ack_latency_seconds`, `webhook_pending_updates`, `bot_admin_lost_total`, `post_id_gap_total`. Alerts: `bot_admin_lost`, `webhook_backlog`, `receiver_outage`, `rotation_behind`, `token_degraded`, `canary_missing`, `dlq_nonempty`. SLO: 99% of channels checked within 24 hours.

## 11. Dependencies

listening-sdk, source-health-canary, raw-archiver, normalize-item, poster-resolver, qualifier, registry-writer, tg-discussion-receiver (second step of onboarding), tg-channel-posts-poller (amber gap fill), Supabase Postgres and Vault, Redpanda, a public HTTPS endpoint outside Iraq.

## 12. Risks and mitigations

- Owners forget or remove the bot: the daily check and `my_chat_member` set `blocked` and notify; the admin page keeps a visible onboarding status.
- No history: clients may expect past posts; the onboarding page says "from the day the bot is added", and an opt-in amber history is open question 6.
- An outage longer than Telegram retains updates loses posts: two replicas, `receiver_outage` alert, amber gap fill for non-government clients.
- Telegram's blocks in Iraq make it harder for an owner inside Iraq to add the bot: delivery is unaffected because everything runs outside Iraq; the admin page explains the steps.
- Cooperating channels are public by definition; only a client's own channel may be private.

## 13. Acceptance criteria

1. The recorded `setWebhook` or `getUpdates` call contains `allowed_updates` with `channel_post` and `edited_channel_post`.
2. A `channel_post` from a registered chat yields one `raw.items` message with the unchanged post, `route = green`, `vendor = null`, `retention_class = vendor_agreed`; with Redpanda down the webhook returns non-2xx and the redelivered update is stored once it is up.
3. In `getUpdates` mode, killing the process mid-batch loses no update and the offset advances only after acknowledgement.
4. An `edited_channel_post` yields a message with `event = edit` and `edit_date` and the same `idempotency_key`; normalize-item stores a new version.
5. An update from an unregistered chat writes nothing to `raw.items`, raises `unregistered_chat_total` and one alert.
6. With a fixture channel, adding the bot produces verification, a `discovery.hits` candidate with `proposed_source_id`, and a first post stored under that `source_id`.
7. Removing the bot sets `health = blocked`, emits `source.events` and notifies ops and the client within 24 hours (immediately when `my_chat_member` arrives); no further `raw.items` follow.
8. With 100 fixture channels, no channel's health check exceeds 24 hours of lag over 72 simulated hours, and `next_poll_at` equals check start plus 24 hours.
9. A jump of 3 in message ids between consecutive posts raises `post_id_gap_total` once and records the range without an error.
10. A contract test shows the service never calls a method that posts, edits or deletes in a channel; the token never appears in logs or envelopes.

## 14. Open questions

1. Does a bot with the lowest administrator rights still receive `channel_post`, and does `my_chat_member` fire for channel promotions and removals?
2. Does the Bot API expose views or forwards for channel posts at all? If not, this route never has them.
3. One bot or two? Proposed two, because a token has one update consumer; revisit if onboarding friction appears in the pilot.
4. Is a client-added channel accepted by registry-writer with a pre-allocated `source_id` (`proposed_source_id`), and is the `discovery.hits` field set agreed with poster-resolver?
5. Is `vendor_agreed` the right retention class for green Telegram data, or is a dedicated class wanted?
6. Should an opted-in client get 90 days of pre-join history through the amber poller, marked amber on those items?
