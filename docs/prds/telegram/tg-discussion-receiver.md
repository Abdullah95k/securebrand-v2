# tg-discussion-receiver

**Platform:** Telegram · **Route:** green · **Lane:** Comments · **Owner:** Backend lead, Telegram adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

On Telegram, the comments under a channel post are not stored in the channel. They live in a separate discussion group that the channel owner links to the channel: each post is copied into the group, and a comment is a reply to that copy. The Bot API sees only channels where our bot is an administrator and discussion groups where it is a member. Telegram's Content Licensing Terms prohibit access "for any purpose other than ordinary, legitimate, and intended use of the Telegram platform as its user", which rules out user-account readers and, on our reading, t.me previews as our own collection. So there is exactly one green route to Telegram comments: our bot, invited into the linked discussion group by the channel's owner. Comments on third-party channels have no route at all: the amber preview Actors (tg-channel-posts-poller) return them mostly not at all, and we build nothing of our own.

tg-discussion-receiver receives every message in the registered discussion groups, ties each comment to the channel post it answers, and checks daily that the bot is still in the group and still able to read it.

Without it the Telegram side of the product has posts but no audience reaction for a client's own channels, and reaction is where sentiment lives. A government client, who can receive no amber data, would have no Telegram comments at all. Telegram data is politically exposed for a government client after Iraq's blocks in Aug 2023 and from 3 Apr to 9 May 2026, so the service runs outside Iraq, reads only groups that invited it, and keeps no commenter identity.

## 2. Objective (the end state this service delivers)

Every comment and reply in every registered discussion group reaches `raw.items` within seconds of Telegram delivering it, threaded to its channel post, with the commenter reduced to a hashed reference, and every group's bot membership and read access verified once a day. Target: no update lost while the service is up, 100% of registered groups health-checked within 24 hours, and the share of comments threaded to a post and the p95 from receipt to acknowledgement to be measured in the pilot.

## 3. Scope

### In scope

- Receiving `message`, `edited_message` and `my_chat_member` updates from registered discussion groups, by webhook or `getUpdates`.
- Threading each comment to its channel post; hashing the commenter; writing `raw.items` (kind `comment`).
- Step two of onboarding (adding the discussion bot to the linked group) and the daily health check.

### Out of scope

- The channel's own posts and step one of onboarding (tg-bot-channel-receiver); comments on channels that have not onboarded (no route).
- History before the bot joined (no history method) and deletions (Telegram sends bots no update when a message is deleted).
- Moderation of any kind: the bot never posts, edits, deletes or bans.
- Media bytes, deduplication (normalize-item), keyword matching (keyword-matcher), profiling of individuals (never).

## 4. Users and consumers

- **Channel owners** add the discussion bot to the linked group during onboarding.
- **Clients** see comments next to their posts, with commenters shown only as hashed references.
- **Ops** sees group health, privacy-mode and link alerts.
- **Downstream:** normalize-item, raw-archiver, source-health-canary, registry-writer, poster-resolver; comment-decay-scheduler holds a `push` row for this route and emits nothing for it.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Push, live. The discussion bot is a second company bot, so this service owns its own update consumer (webhook by default, `getUpdates` by `TG_BOT_UPDATE_MODE`). `allowed_updates` includes `message`, `edited_message` and `my_chat_member`.

**No comment series.** The addendum's profile for Telegram own channels is "push (live), daily health check". There is no +1 h, +6 h, +24 h series, no early stop, no extension and no hot-post extra fetch: comments arrive as they are written, so a post that trends costs nothing extra. comment-decay-scheduler emits no jobs for this route.

**Rotation: the daily health check.** Registered groups carry `tier = push`. A leader replica (Postgres advisory lock) emits one `reconciliation` job per group to `jobs.tg-discussion-receiver` when `next_poll_at <= now()`, ordered by `next_poll_at` then tier; `next_poll_at = check_started_at + 24 h`, from the START of the last check, so the cadence is fixed. A failed check keeps its old `next_poll_at` and goes first next time, so no group is skipped twice in a row. A group with no comment in 30 days is dormant: nothing to poll weekly, the daily check continues. A retired group is not checked; the service never leaves a group by itself.

**Catch-up.** When `rotation_lag_seconds` exceeds 24 hours, the most stale groups are checked first and `rotation_behind` is raised.

**Backfill on add.** None is possible: the Bot API has no history method, so comments written before the bot joined are not available on this route. `backfill_status` is `capped` from onboarding.

**Gaps while we are down.** As for tg-bot-channel-receiver: a webhook is redelivered until acknowledged; `getUpdates` keeps unread updates for a limited time (documented as 24 hours, to be confirmed in the pilot); a longer outage loses comments for good and raises `receiver_outage`.

### 5.2 Step by step

**Update path**

1. Receive an update (webhook with the secret-token header checked, or a `getUpdates` batch); keep `message`, `edited_message`, `my_chat_member`.
2. Map the group chat id to its registry row. An unregistered group writes nothing; `unregistered_chat_total` counts it and ops is alerted once.
3. Classify. A message with `is_automatic_forward` is the copy of a channel post: it is not a comment. Its forward origin (channel and original message id) is stored in the thread map as (group id, root message id) to channel post. Service messages (joins, pins) are ignored. Everything else is a comment.
4. Thread. A comment replying to the post copy carries that copy's forward origin in `reply_to_message`, which gives the channel post at once. A reply to another comment is resolved through `message_thread_id` and the thread map. When neither works the comment is written with `unthreaded = true` and counted in `comments_unthreaded_total`; it still belongs to the channel.
5. Minimise. `from` (a user) is replaced by `author_ref`, a keyed hash (HMAC-SHA-256) of the user id with a secret from Supabase Vault; name, username and language fields are dropped. `sender_chat` is kept when the sender is a channel or the group itself, because those are organisations. The envelope says `minimized = true`.
6. Write one `raw.items` message (kind `comment`) and wait for Redpanda's acknowledgement; only then answer HTTP 200 or advance the offset.
7. An `edited_message` is written again with `event = edit` and `edit_date`.

**Onboarding step two.** The admin page shows, after the channel is verified, the instruction to add the discussion bot to the channel's linked group as a member with read access to all messages. `my_chat_member` triggers verification: `getChat` on the group returns its linked channel; the service checks that this channel is a registered source of the same client; registry-writer creates the group row (`source_type = group`, `route = green`, `tier = push`, `owned_by_client` as for the channel) from a `discovery.hits` candidate with a pre-allocated `proposed_source_id`. The group row's `cursors.cursor` holds, as JSON, the linked channel's `chat id` and `source_id`. If the channel is not registered yet the group waits in state `awaiting_channel` and nothing is stored.

**Daily check.** `getChatMember` (the bot is still `member` or `administrator`), `getChat` (the linked channel is unchanged), `getMe` (`can_read_all_group_messages`, or administrator status in the group), `getChatMemberCount`; once a day `getWebhookInfo`. Removal sets `health = blocked`; a changed link or privacy mode turned on sets `health = degraded` with the reason, because a bot in privacy mode silently sees only commands and mentions. Each change emits `source.events` and notifies ops and the client.

### 5.3 The call it makes

```
POST https://api.telegram.org/bot<token>/setWebhook      (webhook mode)
  allowed_updates = ["message", "edited_message", "my_chat_member"]
POST https://api.telegram.org/bot<token>/getUpdates      (getUpdates mode)
  allowed_updates = the same list; offset = last acknowledged update_id + 1
Daily: getChatMember, getChat, getMe, getChatMemberCount, getWebhookInfo
```

Auth: the discussion bot's token from `vendor_keys` through Supabase Vault. Parameters beyond `allowed_updates`, the exact method set, and whether `message_thread_id` is set for comment threads in linked groups are to be confirmed against the Bot API documentation in the pilot.

### 5.4 What it gets

Per message: message id, group chat, sender (user or chat), date, text or caption with entities, media type with file ids, the replied-to message (with its forward origin on a post copy), `message_thread_id`, and `edit_date` on edits. Illustrative update (a reply to the post copy):

```json
{
  "update_id": 704118977,
  "message": {
    "message_id": 9312, "message_thread_id": 9288,
    "from": {"id": 5120098831, "is_bot": false, "first_name": "Example"},
    "chat": {"id": -1001849302999, "title": "نقاش قناة المثال", "type": "supergroup"},
    "date": 1791278410,
    "reply_to_message": {
      "message_id": 9288, "is_automatic_forward": true,
      "forward_origin": {"type": "channel", "chat": {"id": -1001849302761, "username": "iq_example_owned", "type": "channel"}, "message_id": 5127}
    },
    "text": "شكرا على التوضيح"
  }
}
```

What it does not get: comments before the bot joined; deletions; view counts of comments; anything in a group where the bot is not a member or cannot read all messages; comments on any channel that has not onboarded.

## 6. Inputs and outputs

### 6.1 Reads

Telegram updates; `jobs.tg-discussion-receiver` (kinds `reconciliation`, `ops_force`); `sources`, `cursors`, `vendor_keys` (bot token and hashing secret), `canary_targets`; `source.events`; a service-private table `tg_thread_map` (group id, root message id, channel post key), written at step 3 and read at step 4.

### 6.2 Writes

`raw.items`, one message per comment, the message object with the commenter minimised:

```json
{
  "envelope": {
    "platform": "telegram", "kind": "comment", "route": "green", "vendor": null,
    "service": "tg-discussion-receiver", "event": "new", "ingest_mode": "webhook",
    "source_id": "8c41f2d7-5a3e-4b96-a0d1-7e2c9b3f4a58",
    "discussion_source_id": "d2e96b1a-47c0-4f8d-b35a-0c71e8a49f26",
    "platform_id": "-1001849302999/9312",
    "idempotency_key": "telegram:comment:-1001849302999/9312",
    "post_ref": "iq_example_owned/5127", "unthreaded": false,
    "author_ref": "hmac:7f3a91c0d4e2b856", "minimized": true,
    "update_id": 704118977, "attempt": 1,
    "fetched_at": "2026-10-06T09:20:11Z",
    "retention_class": "vendor_agreed",
    "owned_by_client": true,
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/telegram/2026/10/06/tg-discussion-receiver/000087.jsonl.zst"
  },
  "payload": { "...": "the message object from 5.4 with `from` removed and nothing else changed" }
}
```

Also `discovery.hits` (group candidate), `source.events` (health), `service_runs`, `dlq.tg-discussion-receiver`.

### 6.3 State

`cursors.cursor` (JSON: linked chat id, linked `source_id`, newest message id stored), `last_success_at`, `last_error`, `consecutive_errors`; `sources.next_poll_at`, `last_polled_at`, `health`; the `getUpdates` offset; the thread map; in memory the group map and the leader lock.

## 7. Limits, quotas and cost

- No price or budget tag applies: CONVENTIONS lists none for the Bot API, which has no per-call charge we know of; confirmed in the pilot. Outbound daily checks are four calls per group, paced by a client-side limiter; Telegram's flood limits are to be confirmed in the pilot. Inbound updates ask quota-governor for nothing.
- Undelivered-update retention in `getUpdates` mode: documented as 24 hours, to be confirmed.
- Retention: `vendor_agreed` (default 24 months for raw text) is proposed. Raw payloads never hold a commenter's id, name or username.

## 8. Failure handling and fallback

- HTTP 429 on checks: backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts `dlq.tg-discussion-receiver` and an alert.
- HTTP 401 on the token: `degraded`, stop, alert; no other token. HTTP 403 on one group: that group is `blocked`.
- Produce failure: nothing is acknowledged to Telegram; redelivery or the held offset replays it, and the same `idempotency_key` makes that safe.
- Privacy mode on, bot removed, or link changed: found by the daily check; comments in the meantime are not recoverable.
- Canary: the company-owned test channel from tg-bot-channel-receiver has a linked test group; an hourly test comment from the canary-only bot must arrive; a missing one above 5% in 15 minutes flips `health = degraded`. No fallback route exists, so `fallback_on` is never set.
- Unknown message shape: archived, `schema_unknown`, batch parked.

## 9. Non-functional requirements

- Throughput: bounded by the audience of owned and cooperating channels, a small part of Telegram's 2.4M items a month; to be measured in the pilot.
- Latency: seconds from delivery to acknowledgement; p95 measured in the pilot.
- Idempotency: `telegram:comment:<group chat id>/<message_id>`; replayable; edits reuse the key and become new versions.
- Scaling: two replicas behind a load balancer in webhook mode; one advisory-locked consumer in `getUpdates` mode.
- Security: both secrets from Vault; `author_ref` is stable per user so repeat commenters can be counted, but the id cannot be recovered without the secret, which is rotated under ops control; no individual is profiled; hosted outside Iraq; text never logged; Node (TypeScript).

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `jobs_total{status}`, `rotation_lag_seconds`, `dlq_total`, plus `comments_received_total`, `comments_unthreaded_total`, `ack_latency_seconds`, `groups_degraded{reason}`, `unregistered_chat_total`, `thread_map_rows`. Alerts: `bot_removed`, `privacy_mode_on`, `link_changed`, `receiver_outage`, `rotation_behind`, `canary_missing`, `dlq_nonempty`. SLO: 99% of groups checked within 24 hours.

## 11. Dependencies

listening-sdk, tg-bot-channel-receiver (posts, onboarding step one), comment-decay-scheduler (push row), normalize-item, registry-writer, poster-resolver, qualifier, source-health-canary, raw-archiver, Supabase Postgres and Vault, Redpanda, a public HTTPS endpoint outside Iraq.

## 12. Risks and mitigations

- Privacy mode left on: the bot sees almost nothing; the daily `getMe` check and the onboarding instruction address it.
- An owner unlinks the group or removes the bot: detected within 24 hours, client notified.
- Commenters are private individuals: hashed at the edge, no profile, no backfill, deletion requests handled through `deletions`.
- Deleted comments stay in our store because Telegram tells bots nothing: the provenance statement says so; deletion requests still apply.
- Threading depends on Telegram's reply fields: the unthreaded share is a tracked metric, and the pilot decides whether a fallback is needed.

## 13. Acceptance criteria

1. The recorded `setWebhook` or `getUpdates` call contains `allowed_updates` with `message`, `edited_message` and `my_chat_member`.
2. A comment replying to a post copy yields one `raw.items` message with `kind = comment`, `post_ref` equal to the channel post's `platform_id`, `route = green`, `retention_class = vendor_agreed`.
3. A reply to a comment is threaded through `message_thread_id` and the thread map; with the map row deleted the message is written with `unthreaded = true` and the counter increments.
4. The stored payload and envelope contain no user id, first name, last name or username; two comments by one user carry the same `author_ref`.
5. A message with `is_automatic_forward` creates a thread-map row and no `raw.items` message.
6. The webhook returns 200 only after Redpanda acknowledges; with Redpanda down it returns non-2xx and the redelivered update is stored once; replaying one update twice leaves one stored comment.
7. An `edited_message` yields `event = edit` with the same `idempotency_key`, stored as a new version.
8. With privacy mode on in a fixture group, the next daily check sets `health = degraded`, reason `privacy_mode`, emits `source.events` and an alert.
9. With 100 fixture groups, no group's check lags more than 24 hours over 72 simulated hours; `next_poll_at` equals check start plus 24 hours.
10. An update from an unregistered group writes nothing and raises one alert; the bot token and hashing secret never appear in logs or envelopes.

## 14. Open questions

1. Is `message_thread_id` set on comment threads in linked groups, and does every top-level comment carry the post copy in `reply_to_message`? The pilot answers both and sets the unthreaded target.
2. Privacy mode off, or administrator rights in the group? Proposed: privacy mode off, since administrator rights are more than a reader needs.
3. Where should the group-to-channel link live: the group row's cursor JSON (proposed), or a registry column?
4. Hashing at the edge departs from the `raw.items` rule of "exactly as returned"; confirm with normalize-item and raw-archiver that `author_ref` is accepted as given.
5. One bot or two, and the retention class for green Telegram data: as in tg-bot-channel-receiver.
