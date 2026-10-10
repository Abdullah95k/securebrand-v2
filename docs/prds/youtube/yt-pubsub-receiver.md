# yt-pubsub-receiver

**Platform:** YouTube · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, YouTube adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

YouTube is the one platform where we can be told about new third-party content instead of asking for it. Google's PubSubHubbub hub notifies a subscriber within seconds when any public channel uploads or updates a video, and it spends no API quota. yt-pubsub-receiver holds one subscription per registered channel, receives the notifications on a public HTTPS endpoint, and turns each one into the first sight of a video.

Without it, every channel would be polled through its uploads playlist at its reach tier, a Tier 1 channel 24 times a day, all paid from the 10,000-unit daily quota that must also carry details and comments for 3.0M items a month. New videos would surface up to an hour late on Tier 1 and a day late on Tier 3, and their comment series would start late. With it, a channel's only poll is one reconciliation a day.

## 2. Objective (the end state this service delivers)

Every registered, non-retired channel holds a verified, unexpired subscription; every notification is durable before it is acknowledged and becomes exactly one partial post and one details job; a lapsed lease never leaves a channel unwatched. Targets: a verified lease on 99% of channel-days; zero notifications lost between acknowledgement and `raw.items`; zero `youtube_data_api` units spent by this service; every lapse flagged to yt-uploads-reconciler within one renewal tick; notification to `raw.items` within seconds (p95 target set in the pilot).

## 3. Scope

### In scope

- Subscription lifecycle per registered channel: subscribe on add, renew before expiry, unsubscribe on retirement, re-sync against the registry.
- The endpoint: verification GETs and Atom notification POSTs, with an `X-Hub-Signature` check if the pilot confirms signing.
- Output: partial `raw.items` posts, `first_sight` jobs, `deletions`; lapse catch-up and push-tier changes through registry-writer.

### Out of scope

- Details and metrics (yt-video-details-fetcher), comments (yt-comments-fetcher), channel ids (yt-channel-resolver).
- Backfill and daily reconciliation (yt-uploads-reconciler), keyword search (yt-keyword-search), deduplication (normalize-item).

## 4. Users and consumers

- **Clients** see every watched channel as live; they never touch the endpoint.
- **Ops** watches leases, lapses, missed pushes and the DLQ.
- **Downstream services**: normalize-item, yt-video-details-fetcher, comment-decay-scheduler (through `items.normalized`), yt-uploads-reconciler, deletion-propagator, raw-archiver, registry-writer, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** `source.events` for YouTube channels; the hub's GETs and POSTs; and a renewal loop on one leader replica (Postgres advisory lock). Each POST is made durable on `jobs.yt-pubsub-receiver` (partitioned by `source_id`) and worked asynchronously.

**Cadence by tier.** A channel with a verified lease sits in the push tier, client-owned or not: no polling for new videos, one reconciliation every 24 hours by yt-uploads-reconciler. Dormant (no video in 30 days): weekly reconciliation; the subscription stays on, and the first new-video notification asks registry-writer to promote the channel back to push. Retired: never polled; subscription removed. A channel whose subscription cannot be established keeps its reach tier by subscribers, polled by yt-uploads-reconciler: Tier 1 (100,000 or more, or on a client's priority list) every 60 minutes, Tier 2 (10,000 to 99,999) every 6 hours, Tier 3 (below 10,000) every 24 hours.

**Renewal and catch-up.** Each tick, the loop re-sends the subscribe call for active leases expiring within `LEASE_RENEWAL_MARGIN`, ordered by `lease_expires_at` then tier and paced by `SUBSCRIBE_RATE`, and subscribes any non-retired channel missing from `yt_subscriptions`. A lease that expires without a verified renewal becomes `lapsed`, and registry-writer sets the channel's `next_poll_at` to now, so yt-uploads-reconciler reads the uploads playlist back past the lapse at once. A lapse caused by the loop falling behind, not by the hub, raises `rotation_behind`.

**Backfill on add.** This service subscribes first so no upload is missed; backfill-orchestrator hands the channel to yt-uploads-reconciler for the last 90 days; overlaps are deduplicated by `idempotency_key`. The channel becomes push once its lease is verified and `backfill_status` is `done` or `capped`.

**Comments.** The hub carries none. Once yt-video-details-fetcher's full record is normalized, comment-decay-scheduler opens the YouTube series (+6 h, +24 h, +3 d, +7 d, +30 d) for yt-comments-fetcher, hours earlier than a tier poll would.

### 5.2 Step by step

1. Subscribe: on `added`, or on the `updated` event that brings the channel id from yt-channel-resolver, insert a `yt_subscriptions` row (`requested`) and send the call in 5.3; no verification within `VERIFY_TIMEOUT` counts as a failed attempt. On `retired`, the same with `unsubscribing`.
2. Verify (GET): if the topic matches a registered channel with an outstanding request, return 200 with the `hub.challenge` value as plain text and set `active`, `verified_at`, `lease_expires_at`; otherwise 404, no challenge.
3. Notify (POST): reject bodies above `MAX_BODY_BYTES`; with signing enabled, check `X-Hub-Signature` in constant time and return 403 on mismatch.
4. Map `yt:channelId` (or a deleted entry's channel URI) to `source_id` from an in-memory copy of `sources` refreshed by `source.events`; unregistered or retired channels get 2xx and are dropped and counted.
5. Produce the body to `jobs.yt-pubsub-receiver`, wait for the Redpanda acknowledgement, return 2xx; if Redpanda is down, 5xx so the hub redelivers.
6. The worker checks each entry's (`yt:videoId`, `updated`) against the seen ledger: already seen or older, dropped; unknown video, a partial post (version 1) plus a `first_sight` job; known video with a newer `updated`, a partial post with the next version and no job. A deleted entry becomes a `deletions` event (reason `platform_sync`).
7. After the acknowledgements, update the ledger, `cursors` and `last_notification_at`, then commit the offset, so a crash replays rather than loses.

### 5.3 The call it makes

```
POST https://pubsubhubbub.appspot.com/subscribe
  hub.callback=https://<cluster-ingress>/webhooks/youtube
  hub.topic=https://www.youtube.com/xml/feeds/videos.xml?channel_id=<channel_id>
  hub.mode=subscribe
  hub.verify=async
  hub.lease_seconds=<LEASE_SECONDS>
```

The topic carries its own query string, so it is URL-encoded. No API key is sent and no quota unit is spent. To be confirmed in the pilot: request encoding and acceptance status; the hub's maximum lease and its behaviour on a longer request; whether adding `hub.secret` makes the hub sign with `X-Hub-Signature`, and how; unsubscribing as the same call with `hub.mode=unsubscribe`.

Inbound, on the cluster's own ingress with a valid certificate and no third-party proxy: `GET /webhooks/youtube` with `hub.challenge` (other parameters to be confirmed in the pilot) and `POST /webhooks/youtube` with Atom XML.

### 5.4 What it gets

One Atom `entry` per new or updated video. Illustrative; to be confirmed in the pilot:

```xml
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>yt:video:k7Qm2Xv9TbE</id>
    <yt:videoId>k7Qm2Xv9TbE</yt:videoId>
    <yt:channelId>UCx3Kp9vQ2mLwR7tYb4nJ8sA</yt:channelId>
    <title>جولة في سوق الشورجة قبل العيد</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=k7Qm2Xv9TbE"/>
    <author><name>قناة تجريبية</name><uri>https://www.youtube.com/channel/UCx3Kp9vQ2mLwR7tYb4nJ8sA</uri></author>
    <published>2026-10-06T09:12:03+00:00</published>
    <updated>2026-10-06T09:12:41.118204512+00:00</updated>
  </entry>
</feed>
```

A removed video arrives as an `at:deleted-entry` with `ref="yt:video:<id>"`. Not obtained: description, duration, statistics and topics (yt-video-details-fetcher), comments, channel statistics (yt-channel-resolver), anything before the subscription. No individual's data arrives: the author is the registered channel, so no `author_ref` is computed.

## 6. Inputs and outputs

### 6.1 Reads

The hub's requests; `jobs.yt-pubsub-receiver`; `source.events`; `sources` (`platform_id`, `tier`, `followers`, `backfill_status`, `client_ids`, `retention_class`); `cursors`; `yt_subscriptions`; the seen ledger; Supabase Vault (hub secrets, if signing is confirmed).

### 6.2 Writes

`raw.items`, one message per new or updated video:

```json
{
  "envelope": {
    "platform": "youtube", "kind": "post", "route": "green", "vendor": null,
    "service": "yt-pubsub-receiver",
    "source_id": "3c9a7e52-1f4b-4d8e-b6a0-8e2f5c1d7a94",
    "platform_id": "k7Qm2Xv9TbE",
    "parent_platform_id": null,
    "idempotency_key": "youtube:post:k7Qm2Xv9TbE",
    "job_id": "01J9N7QV8D2K6M4P0R3S5T7W9X", "attempt": 1,
    "fetched_at": "2026-10-06T09:12:44Z",
    "retention_class": "youtube_30d_text",
    "client_ids": ["9e4d2b17-6a3c-4f81-a5d9-2c7b0e6f3a18"],
    "batch": "raw/green/youtube/2026/10/06/yt-pubsub-receiver/000117.jsonl.zst",
    "delivery": "push", "version": 1, "partial": true
  },
  "payload": { "id": "yt:video:k7Qm2Xv9TbE", "yt:videoId": "k7Qm2Xv9TbE", "yt:channelId": "UCx3Kp9vQ2mLwR7tYb4nJ8sA", "title": "جولة في سوق الشورجة قبل العيد", "link": "https://www.youtube.com/watch?v=k7Qm2Xv9TbE", "published": "2026-10-06T09:12:03+00:00", "updated": "2026-10-06T09:12:41.118204512+00:00" }
}
```

The payload is the Atom `entry` transliterated field by field. `partial: true` makes normalize-item wait for details: it holds the record until yt-video-details-fetcher's full record under the same key arrives. Alongside, on `jobs.yt-video-details-fetcher`:

```json
{ "job_id": "01J9N7QW3E5R8T2Y6V0H4M9P1A", "source_id": "3c9a7e52-1f4b-4d8e-b6a0-8e2f5c1d7a94", "kind": "first_sight", "due_at": "2026-10-06T09:12:44Z", "attempt": 1, "post_ref": "k7Qm2Xv9TbE", "series_step": null }
```

Also `deletions`, requests to registry-writer (push, promotion, `next_poll_at`, `health`), `service_runs`, and `dlq.yt-pubsub-receiver` after 5 failed attempts.

### 6.3 State

`yt_subscriptions` (owned here): `source_id`, `topic`, `state` (requested, active, lapsed, unsubscribing, unsubscribed, failed), `verified_at`, `lease_expires_at`, `last_notification_at`, `consecutive_errors`. `cursors` (`source_id`, `yt-pubsub-receiver`): `cursor` = newest `updated`, `last_success_at` = last verified lease. Seen ledger (listening-sdk idempotency helper): per video `last_updated` and `version`, kept 90 days. In memory: the channel map and leader lock.

Owner (ADR-0025): `yt_subscriptions` is private to this service. No other service reads it, F3's `TABLE-OWNERS.md` lists it, and it is registered in the SDK purge registry where it holds item ids, hashes or URLs.

## 7. Limits, quotas and cost

- No `youtube_data_api` units, no budget tag, no quota-governor call; the hub costs USD 0 per call.
- What it triggers is paid elsewhere under `youtube_data_api`: one id in a `videos.list` call (1 unit for up to 50 ids) by yt-video-details-fetcher, then the comment series.
- The saving: hourly polling of a Tier 1 channel costs at least 24 `playlistItems.list` units a day; push costs at least one reconciliation page. With about 4,000 to 5,000 units a day planned for all 1-unit endpoints, that gap leaves room for details and comments. Quota arithmetic to be measured in the pilot.
- To be confirmed in the pilot: maximum lease, subscribe rate limits, retry schedule, delivery deadline, notification volume.

## 8. Failure handling and fallback

- Subscription refused or never verified: backoff from 30 s to 15 min with jitter; after 5 attempts the row is `failed`, `health = degraded`, `subscription_failed` fires, the channel keeps its reach tier, and a retry runs daily. Callback hosts and IPs are never changed to get around a refusal.
- Hub-wide failure (source-health-canary sees renewals fail or notifications stop across channels): no mass move to reach tiers; yt-uploads-reconciler catches up most-stale-first within quota-governor's allowance, and ops decides on wider polling.
- Endpoint down: the hub's retries (to be confirmed in the pilot), then daily reconciliation; ops can force reconciliation of all push channels, most-stale-first.
- Malformed XML: parked in `dlq.yt-pubsub-receiver`, counted, never an item.

## 9. Non-functional requirements

- Throughput: notification volume to be measured in the pilot; YouTube's 3.0M items a month are mostly comments.
- Latency: 2xx once durable; p95 to `raw.items` within seconds, target set in the pilot.
- Idempotency: `youtube:post:<videoId>`, versioned by `updated`; repeated and out-of-order deliveries are harmless.
- Scaling: stateless handlers on request rate, workers on partition lag, one leader with failover.
- Security and compliance: DTDs and external entities disabled; links in bodies never fetched; secrets from Supabase Vault, never logged; no comment text or individual's data; provenance on every record so a Developer Policies audit can be answered at any time.

## 10. Metrics and alerts

`notifications_received_total{type}`, `notifications_dropped_total{reason}`, `webhook_requests_total{method,status}`, `signature_failed_total`, `ack_latency_seconds`, `subscriptions{state}`, `lease_lapsed_total`, `renewals_total{status}`, `first_sight_jobs_total`, `rotation_lag_seconds` (most overdue renewal), `push_missed_ratio`, `cost_units_total` (always 0), `dlq_total`. A missed push is a new video on a push channel first seen by yt-uploads-reconciler. Alerts: `lease_lapsed`, `subscription_failed`, `rotation_behind`, `notification_silence`, `push_missed_rate`, `webhook_5xx_rate`, `dlq_nonempty`. SLO: a verified lease on 99% of channel-days.

## 11. Dependencies

listening-sdk; the hub; public ingress with TLS; Redpanda; Supabase Postgres and Vault; yt-channel-resolver (supplies the channel id the topic needs), yt-uploads-reconciler, yt-video-details-fetcher, yt-comments-fetcher, backfill-orchestrator, comment-decay-scheduler, normalize-item, registry-writer, source-health-canary, raw-archiver, deletion-propagator.

## 12. Risks and mitigations

- Best-effort delivery: daily reconciliation, lapse catch-up, measured missed pushes.
- Leases dropped silently: renewal margin, re-sync every tick, `notification_silence`.
- Forged notifications if unsigned: a notification is only a hint, and nothing reaches `items.normalized` until `videos.list` returns the video; a per-channel random token can go in the callback path.
- A hub outage draining quota: no mass fallback.

## 13. Acceptance criteria

1. An `added` event with a channel id yields exactly one subscribe call with all five parameters and a URL-encoded topic within one tick; without a channel id, none until yt-channel-resolver supplies it.
2. A verification GET for a topic with an outstanding request returns 200 with exactly the `hub.challenge` value; any other topic gets 404.
3. A notification gets 2xx only after Redpanda's acknowledgement; with Redpanda down, 5xx.
4. A new-video notification yields one `raw.items` message (`kind = post`, `route = green`, `partial = true`, `delivery = push`, `idempotency_key = youtube:post:<videoId>`) and one `first_sight` job with `post_ref = <videoId>`.
5. The same notification twice yields one message and one job; a later `updated` yields version 2 and no job; an older one arriving afterwards is dropped.
6. A deleted entry yields one `deletions` event with reason `platform_sync`.
7. With 100 fixture leases, each entering `LEASE_RENEWAL_MARGIN` is re-requested within one tick, most urgent first; one left to expire becomes `lapsed`, fires `lease_lapsed`, and has `next_poll_at` set to now within one tick.
8. A push channel is never emitted as a rotation job; after 5 failed subscription attempts it is `degraded` and polled at its reach tier.
9. After `retired`, an unsubscribe call is sent and later notifications are dropped.
10. Over a 24-hour fixture run, `cost_units_total` is 0 and quota-governor receives no request.
11. A body with an external entity is rejected unresolved; secrets never appear in logs.
12. The first new-video notification of a dormant channel requests promotion to push.

## 14. Open questions

1. What is the hub's maximum lease, what happens to a longer request, and does the verification GET return the granted lease?
2. Does the hub sign with `hub.secret`, and how? If not, adopt the callback token.
3. What are its retry schedule, delivery deadline and subscribe rate limits?
4. Edits to videos published over 90 days ago: proposed counted and ignored in v1.
5. `first_sight` is missing from the addendum's job-kind list; add it.
