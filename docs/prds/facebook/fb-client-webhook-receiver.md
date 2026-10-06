# fb-client-webhook-receiver

**Platform:** Facebook · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, Facebook adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The Pages a client owns are the one place where Facebook gives us complete data: every post and every comment as it happens, with the commenter's identity, instead of the ranked, up-to-24-hours-late, anonymous view that Page Public Content Access (PPCA) gives for third-party Pages. fb-client-webhook-receiver is the public HTTPS endpoint that receives Meta Webhooks for Pages from the Pages our clients connect, and turns each event into a `raw.items` record.

Without it, a client's own Page would be treated like anyone else's: polled by fb-page-feed-poller, with comments read by fb-post-comments-fetcher without ids, always an hour or more behind. The product would lose its most accurate, most live Facebook source, and the cheapest one: a pushed Page costs one reconciliation poll a day instead of an hourly poll.

## 2. Objective (the end state this service delivers)

Every connected client-owned Page has an active webhook subscription, every post and comment event is verified, made durable and turned into exactly one item, and no Page is left unwatched if its subscription fails. Target: 200 returned only for events already durable in Redpanda; every push Page's subscription audited within 24 hours for 99% of Pages per day; zero events lost between acknowledgement and `raw.items`.

## 3. Scope

### In scope

- The HTTPS endpoint: Meta's verification handshake (`hub.mode`, `hub.verify_token`, `hub.challenge`) and signature-checked deliveries (`X-Hub-Signature-256`).
- Subscription lifecycle for Pages with `owned_by_client = true`: `POST /{page-id}/subscribed_apps?subscribed_fields=feed` on connection, daily audit, removal on retirement.
- Asynchronous processing of `feed` and `comments` events into `raw.items` (kind `post` or `comment`) and `deletions`.
- Hashed author references; promotion of dormant Pages; fallback of Pages whose subscription fails.

### Out of scope

- The Facebook Login connection screen (web app) and the Page access token exchange.
- Backfill of past posts (fb-backfill); the daily reconciliation poll (fb-page-feed-poller); metrics (fb-reactions-fetcher).
- Third-party Pages, groups, deduplication (normalize-item), keyword matching (keyword-matcher).

## 4. Users and consumers

- **Clients** connect a Page once and experience it as "my own Page, live"; they never call the endpoint.
- **Ops** watches subscription health, signature failures and the DLQ.
- **Downstream services**: normalize-item (consumes `raw.items`), comment-decay-scheduler (through `items.normalized`), deletion-propagator, raw-archiver, fb-page-feed-poller (reconciliation), registry-writer, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Meta calls the endpoint: a GET for the verification handshake, a POST per delivery. Each POST entry is made durable on `jobs.fb-client-webhook-receiver` (partitioned by `source_id`) and worked asynchronously. A second trigger is this service's own audit loop (one leader replica, Postgres advisory lock).

**Cadence by tier.** Client-owned Pages sit in the push tier: no polling for new posts, one reconciliation poll every 24 hours by fb-page-feed-poller (`next_poll_at` set from the start of the last poll). Dormant (no post in 30 days): weekly reconciliation; the subscription stays on, and the first new-post event asks registry-writer to promote the Page back to push. Retired: never polled, subscription removed. A Page whose subscription fails falls back to its reach tier in fb-page-feed-poller: Tier 1 (100,000 or more followers, or on a client's priority list) every 60 minutes, Tier 2 (10,000 to 99,999) every 6 hours, Tier 3 (below 10,000) every 24 hours. No Page is ever unwatched.

**Keeping every Page covered.** Every push Page is covered three ways: the live webhook; the daily reconciliation, which reads `since = cursor − 24 h` and therefore also repairs any gap shorter than a day; and a daily subscription audit by this service. The audit orders Pages by oldest `cursors.last_success_at` then tier, so no Page is skipped twice in a row, and it runs most-stale-first with a `rotation_behind` alert when the most overdue audit passes 24 hours. After an outage of this endpoint, ops can force reconciliation of all push Pages, most-stale-first.

**Backfill on add.** When a client connects a Page, registry-writer adds it (`added_by = client`, `owned_by_client = true`), this service subscribes it first so no event is missed, then backfill-orchestrator sends fb-backfill the last 90 days (or the cap) with the Page access token. The overlap with live events is deduplicated by `idempotency_key`. Only then is the Page marked push.

**Comments.** Comment events arrive live. The series of fb-post-comments-fetcher (+1 h, +6 h, +24 h, +3 d, +7 d, weekly to day 30, with early stop, extension and hot-post rules) still runs on client-owned Pages with the Page token, where comment ids make edits and deletions exact; it is the reconciliation for comments.

### 5.2 Step by step

1. Handshake (GET): if `hub.mode = subscribe` and `hub.verify_token` equals the configured token (constant-time comparison), return 200 with the `hub.challenge` value as plain text; otherwise 403.
2. Delivery (POST): read the raw body, compute HMAC-SHA256 with the app secret (Supabase Vault) and compare it in constant time with `X-Hub-Signature-256`; on mismatch return 403, count `signature_failed_total`, process nothing.
3. Check `object = page`, split by `entry`, map `entry.id` to `source_id` from an in-memory copy of `sources` (refreshed by `source.events`). Unregistered or retired Pages are dropped and counted.
4. Produce each entry to `jobs.fb-client-webhook-receiver`, wait for the Redpanda acknowledgement, then return 200. If Redpanda is unavailable, return 5xx so Meta redelivers.
5. The worker reads each `change` by `field`, `item` and `verb`. `add` of a post or comment becomes an item; `edited` becomes a new version of the same item; `remove` becomes a `deletions` event with reason `platform_sync`; reaction events are counted and dropped, since reactor identity is never stored and counts come from fb-reactions-fetcher.
6. If an event carries ids but not the content (open question 2), fetch the object once with the Page access token under `meta_graph_pages:<client_id>`.
7. Compute `author_ref` for any `from` that is not the Page itself; the Page's own posts and replies keep the Page as author. The payload loses `from` (`payload_redacted: ["from"]`).
8. Emit `raw.items`; after acknowledgement commit the offset and update `cursors`. Daily audit: for each push Page, check the subscription (a GET on the same `subscribed_apps` edge, to be confirmed in the pilot); on failure set `health = degraded`, notify ops and the client, and ask registry-writer to return the Page to its reach tier.

### 5.3 The call it makes

Inbound (Meta to us): `GET /webhooks/facebook` with `hub.mode`, `hub.verify_token`, `hub.challenge`; `POST /webhooks/facebook` with a JSON body and `X-Hub-Signature-256: sha256=<hex>`. The endpoint is public HTTPS with a valid certificate, served from the cluster's own ingress with no third-party proxy.

Outbound, on connection:

```
POST https://graph.facebook.com/v<pinned>/{page-id}/subscribed_apps
  ?subscribed_fields=feed
  &access_token=<the client's Page access token, from Supabase Vault>
```

The Page access token comes from the client's Facebook Login connection. The Graph version is pinned by the one environment variable shared by all fb-* services. Whether comment events arrive inside `feed` or need a `comments` field added to the subscription is to be confirmed in the pilot, as are the permissions App Review grants for this flow.

### 5.4 What it gets

Events on the client's own Page, including commenter identity. Illustrative shape; field names to be confirmed in the pilot:

```json
{
  "object": "page",
  "entry": [{
    "id": "100064583471102", "time": 1791278625,
    "changes": [{
      "field": "feed",
      "value": {
        "item": "comment", "verb": "add",
        "post_id": "100064583471102_1198837625012734",
        "comment_id": "1198837625012734_5520817364092219",
        "from": {"id": "61552270194836", "name": "مستخدم تجريبي"},
        "message": "ممكن تفاصيل الباقة؟",
        "created_time": 1791278623
      }
    }]
  }]
}
```

Not obtained: events for Pages that have not connected, reactor identities, anything before the subscription (fb-backfill covers the past 90 days).

## 6. Inputs and outputs

### 6.1 Reads

Meta's HTTPS requests; `jobs.fb-client-webhook-receiver`; `sources`, `cursors`, `clients`, `budgets` through quota-governor; Supabase Vault (app secret, verify token, Page access tokens); `source.events` (`added`, `updated`, `tier change`, `retired`).

### 6.2 Writes

`raw.items`, one message per post or comment event:

```json
{
  "envelope": {
    "platform": "facebook", "kind": "comment", "route": "green", "vendor": null,
    "service": "fb-client-webhook-receiver",
    "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
    "platform_id": "1198837625012734_5520817364092219",
    "parent_platform_id": "100064583471102_1198837625012734",
    "idempotency_key": "facebook:comment:1198837625012734_5520817364092219",
    "job_id": "01J9N5C4R7V2X8K3M1T6B0QZYF", "attempt": 1,
    "fetched_at": "2026-10-06T09:23:46Z",
    "retention_class": "meta_on_request",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/facebook/2026/10/06/fb-client-webhook-receiver/000208.jsonl.zst",
    "delivery": "push", "version": 1,
    "author_ref": "5d0c7e91a3b84f26c1e9d07a5b3f8e64a2c0d19b7e5f3a8c6d4b2e0f9a1c7385",
    "payload_redacted": ["from"]
  },
  "payload": { "item": "comment", "verb": "add", "post_id": "100064583471102_1198837625012734", "comment_id": "1198837625012734_5520817364092219", "message": "ممكن تفاصيل الباقة؟", "created_time": 1791278623 }
}
```

Posts use `facebook:post:<post_id>`. Also `deletions` (reason `platform_sync`), the internal buffer on `jobs.fb-client-webhook-receiver`, `service_runs`, and `dlq.fb-client-webhook-receiver` after 5 failed attempts.

### 6.3 State

`cursors` (`source_id`, `fb-client-webhook-receiver`): `cursor` = time of the newest event, `last_success_at` = last successful audit, `last_error`, `consecutive_errors`. `sources.health` and `tier`. In memory only the app secret, the source map and the leader lock.

## 7. Limits, quotas and cost

- Webhook deliveries do not use the Pages API bucket. The subscription call, the audit and any follow-up fetch use the client's Page token under `meta_graph_pages:<client_id>`; cost USD 0 per call.
- Meta's retry schedule and response deadline are to be confirmed in the pilot, as are event volume and endpoint capacity.
- A pushed Page replaces polling: one reconciliation call a day instead of up to 24 hourly polls (Tier 1).

## 8. Failure handling and fallback

- Bad signature or verify token: 403, nothing processed, counted; a spike raises `signature_failed_rate`.
- Redpanda unavailable: 5xx, and Meta re-delivers; delivery is idempotent, because the same event yields the same `idempotency_key`.
- This endpoint down: Meta retries for a period to be confirmed in the pilot; the daily reconciliation repairs gaps under 24 hours.
- HTTP 401 and 403 from Graph (token revoked or expired): mark the token `degraded`, stop, alert, notify the client; the Page returns to its reach tier so PPCA polling keeps it watched. Never rotate accounts, tokens or IPs.
- Unknown `field` or `item`: the entry is archived raw, counted in `unknown_event_total` and not turned into an item.
- Partial write: offsets commit after the `raw.items` acknowledgement; replays are deduplicated.

## 9. Non-functional requirements

- Throughput: client-owned Pages only; events per second to be measured in the pilot.
- Latency: 200 returned once the entry is durable; target to be set in the pilot against Meta's deadline; an event reaches `raw.items` within seconds.
- Idempotency: `facebook:post:<id>`, `facebook:comment:<id>`; out-of-order and repeated events are harmless.
- Scaling: stateless handlers and workers scaled on request rate and partition lag.
- Security: signature and token checks in constant time; secrets from Supabase Vault, never logged; bodies and commenter names never logged; individuals only as `author_ref`; Meta data never processed for law-enforcement or national-security purposes; retention `meta_on_request`, deleted on client offboarding.

## 10. Metrics and alerts

`events_received_total{field,item,verb}`, `events_dropped_total{reason}`, `webhook_requests_total{method,status}`, `signature_failed_total`, `ack_latency_seconds`, `processing_lag_seconds`, `subscriptions_active`, `subscription_audit_failed_total`, `items_new_total`, `jobs_total{status}`, `rotation_lag_seconds` (audit), `dlq_total`. Alerts: `signature_failed_rate`, `webhook_5xx_rate`, `subscription_lost`, `rotation_behind`, `dlq_nonempty`. SLO: every push Page audited within 24 hours for 99% of Pages per day.

## 11. Dependencies

listening-sdk, fb-page-feed-poller, fb-backfill, backfill-orchestrator, registry-writer, comment-decay-scheduler, normalize-item, deletion-propagator, raw-archiver, quota-governor, source-health-canary, Supabase Postgres and Vault, Redpanda, public ingress with TLS. Meta prerequisites: Business Verification, App Review, Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- Missed or late deliveries: daily reconciliation with a 24-hour overlap.
- A subscription lost silently (token revoked, app removed): daily audit and fallback to the reach tier.
- Forged requests: signature check on every POST.
- Commenter identity is sensitive: only `author_ref` is stored; reactors never.
- App Review takes weeks: the pilot starts on test Pages the team administers.

## 13. Acceptance criteria

1. A GET with `hub.mode = subscribe` and the correct `hub.verify_token` returns 200 with exactly the `hub.challenge` value; a wrong token returns 403.
2. A POST whose `X-Hub-Signature-256` matches the HMAC-SHA256 of the raw body is accepted; the same body altered by one byte gets 403 and produces no message.
3. The endpoint returns 200 only after Redpanda has acknowledged the entry; with Redpanda unavailable it returns 5xx.
4. The same delivery posted twice produces one stored item (identical `idempotency_key`).
5. A new-comment event produces one `raw.items` message of kind `comment` with `route = green`, `retention_class = meta_on_request`, `delivery = push`, an `author_ref` and no `from` in the payload; a comment authored by the Page itself keeps the Page as author.
6. A `remove` event produces one `deletions` event with reason `platform_sync`.
7. An event for an unregistered or retired Page returns 200, is dropped and counted.
8. A push Page is never emitted as a rotation job and gets one reconciliation a day; a failed audit sets `health = degraded` and returns the Page to its reach tier.
9. With 100 fixture push Pages over 24 hours, no audit is later than 24 hours, ordered oldest first.
10. The first new-post event of a dormant Page requests promotion back to push.
11. The app secret, verify token, Page tokens and commenter names never appear in logs.

## 14. Open questions

1. Do comment events arrive inside `feed` or as a separate `comments` field, and must the subscription add it?
2. Do events carry full content, or only ids that need a follow-up fetch?
3. What are Meta's retry schedule and response deadline?
4. Should hidden comments (`hide`, `unhide`) be treated as deletions? Proposed: ignored in v1.
5. How are missed pushes measured? Proposed: reconciliation items whose key was not yet seen.
