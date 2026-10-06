# ig-webhook-receiver

**Platform:** Instagram · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, Instagram adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

When a customer comments under a client's own Instagram post, or tags the client in their own, the client wants to know now, not at the next series step or the next hourly poll. Instagram offers this for accounts a client has connected: webhooks for `comments` and `mentions`. ig-webhook-receiver is the public endpoint that Meta calls, the service that proves each call is genuine, answers it fast, and turns it into items in the pipeline.

Without it the client-owned Instagram accounts would still be covered, but only on a delay: comments by the series of ig-own-comments-fetcher (the first read comes an hour after the post is seen) and mentions by the hourly reads of ig-mentions-fetcher. With it the freshest comments and mentions arrive in seconds. It also keeps the other two honest: a daily reconciliation compares what was pushed with what a read finds, so a webhook that silently stops working shows up as a number, not as a hole in a client's data.

## 2. Objective (the end state this service delivers)

Every `comments` and `mentions` notification for a connected account is verified, acknowledged with a fast 200 only after it is durably stored, and turned into `raw.items` or a targeted read, exactly once in effect even though Meta re-delivers. Every connected account is reconciled once a day (a dormant one weekly) through ig-own-comments-fetcher and ig-mentions-fetcher. Target: no verified notification lost, reconciliation lag below one interval for 99% of accounts per day, `missed_push_total` falling to near zero once the pilot has tuned both paths.

## 3. Scope

### In scope

- The verification handshake, the `X-Hub-Signature-256` check, the fast acknowledgement and the inbound queue `jobs.ig-webhook-receiver`.
- Workers that map an event to a connected account and write `raw.items` or a targeted read request.
- The daily reconciliation scheduler (leader-elected) that emits `reconciliation` jobs to the two fetching services.
- A daily check that each account's webhook subscription is alive.

### Out of scope

- Reading history, new posts of the owned account (no webhook topic announces them: ig-account-media-poller), Stories mentions (not supported), third-party media.
- The polling reads themselves (ig-own-comments-fetcher, ig-mentions-fetcher), deduplication (normalize-item), tier decisions (qualifier, registry-writer).

## 4. Users and consumers

- **Clients** experience it as "comments and mentions on my connected account, within seconds". They never call it; connecting an account is what creates its subscription.
- **Ops** watches signature failures, acknowledgement latency, subscription health and `missed_push_total`.
- **Downstream services**: normalize-item (consumes `raw.items`), ig-own-comments-fetcher and ig-mentions-fetcher (receive reconciliation and targeted jobs), source-health-canary, raw-archiver.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Two. Meta's HTTPS calls to one endpoint, `/webhooks/instagram`, for every connected account of the company's Meta app; and a leader-elected reconciliation scheduler (one replica through a Postgres advisory lock) that emits jobs when an account's reconciliation is due.

**Cadence by tier.** Connected accounts are client-owned, so they sit on the push class: no polling for new events and one reconciliation a day. A client-owned account that has gone dormant (no post in 30 days) keeps its live subscription and is reconciled weekly; a retired account has its subscription removed and is never reconciled. Tier 1, 2 and 3 do not apply: they describe discovered accounts, and a discovered account has no webhook.

**Keeping every account covered.** The scheduler keeps one due time per account in its own `cursors` row (source × `ig-webhook-receiver`), set from the START of the last reconciliation (`started_at + 24 h`, or `+ 7 d` for dormant), so cadence is fixed. Each due account gets two `reconciliation` jobs, one on `jobs.ig-own-comments-fetcher` (comments on media still inside the first 7 days of their series) and one on `jobs.ig-mentions-fetcher` (a read back to 24 hours before its cursor). The account's next due time is set when both report. Accounts are emitted ordered by due time then tier, so none is skipped twice in a row; when lag exceeds one interval the scheduler orders most-stale-first and raises `rotation_behind`. What a reconciliation finds that was never pushed is added to `missed_push_total`.

**Backfill on add.** Connecting an account creates its subscription here; its history comes from backfill-orchestrator (mentions through ig-mentions-fetcher), ig-account-media-poller (posts) and the comment series (comments). This service reads no history.

**Comment decay.** Pushes do not replace the series (+1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30) of ig-own-comments-fetcher. Because a pushed comment is stored before the next fetch reads it, that fetch can report few new comments on a busy post; the worker therefore counts pushed comments per post and exposes the count so comment-decay-scheduler can include it in the early-stop, extension and hot-post rules (open question 3).

**Idempotency and re-delivery.** Meta re-delivers a notification it did not see acknowledged (schedule and deadline: to be confirmed in the pilot). Every output carries a stable `idempotency_key`, so a repeat changes nothing downstream.

### 5.2 Step by step

1. `GET /webhooks/instagram` (handshake): when `hub.mode` is `subscribe` and `hub.verify_token` equals the token in Supabase Vault, answer 200 with `hub.challenge` as the body; otherwise 403.
2. `POST /webhooks/instagram`: read the raw body, compute HMAC-SHA256 with the app secret from Supabase Vault, compare it in constant time with `X-Hub-Signature-256`; on mismatch answer 403, store nothing, count `signature_failed_total`.
3. Append the verified body, headers and `received_at` to `jobs.ig-webhook-receiver` (message `kind = push`), wait for Redpanda to acknowledge, answer 200 with an empty body. If the append fails, answer 500 so Meta re-delivers. Nothing else happens before the 200.
4. A worker consumes the message and, for each `entry`, finds the source by `platform_id` (`owned_by_client = true`, `route = green`); an unknown account is dropped and counted; a source is never created from a webhook.
5. For each `changes` item with `field` `comments`: write a `raw.items` message of kind `comment`, the event value unchanged. For `mentions`: when the event carries the item, write it; when it carries identifiers only, emit a targeted read (`ops_force`, one id) to `jobs.ig-mentions-fetcher`, whose message is then the stored record.
6. If a `comments` event lacks the text, emit a targeted read (`ops_force`, `post_ref` = media id) to `jobs.ig-own-comments-fetcher`.
7. Commit the inbound offset only after Redpanda acknowledges every output; a repeated request for the same id within an hour is skipped (kept in memory; a restart only costs a duplicate, which the keys absorb).
8. Once a day, check each account's subscription; re-create a lost one; if that fails, set `health = degraded` and emit `source.events` `updated`.

### 5.3 The call it makes

This service is called, and makes no Graph call on the event path.

```
GET  https://<webhook host>/webhooks/instagram
       ?hub.mode=subscribe&hub.verify_token=<token>&hub.challenge=<value>
     -> 200 with body = hub.challenge, only if hub.mode = subscribe and the token matches
POST https://<webhook host>/webhooks/instagram
       X-Hub-Signature-256: sha256=<HMAC-SHA256 of the raw body, key = app secret>
     -> 200 once the body is durably appended; 403 on a bad signature
```

Subscription management (the `comments` and `mentions` fields per connected account, using the client's token): call and permissions to be confirmed in the pilot. Auth for inbound calls: the signature, the verify token and the app secret, all from Supabase Vault.

### 5.4 What it gets

Meta's notification for object `instagram`, with `entry[]` per account and `changes[]` per event. Illustrative shape (exact payloads of `comments` and `mentions`: to be confirmed in the pilot):

```json
{
  "object": "instagram",
  "entry": [{
    "id": "17841405822304914", "time": 1791280800,
    "changes": [{"field": "comments", "value": {
      "id": "17858893269123456", "text": "الخدمة ممتازة، شكراً لكم",
      "media": {"id": "17912345678901234"}}}]
  }]
}
```

What it does not get: new posts of the account, Stories mentions (not supported), history, anything for accounts not connected, events on third-party media.

## 6. Inputs and outputs

### 6.1 Reads

Inbound HTTPS from Meta; `jobs.ig-webhook-receiver`; `sources` and `clients` (account to source mapping, token reference), `cursors` (reconciliation schedule), Supabase Vault (app secret, verify token), job results of the two fetching services.

### 6.2 Writes

`raw.items`, one message per event that carries an item:

```json
{
  "envelope": {
    "platform": "instagram", "kind": "comment", "route": "green", "vendor": null,
    "service": "ig-webhook-receiver",
    "source_id": "a3d94c10-5e7b-4f28-b6c1-92e0d4a7f835",
    "platform_id": "17858893269123456",
    "idempotency_key": "instagram:comment:17858893269123456",
    "job_id": "01J9N7F8R2H4A6C9Y1V3X5MKWG", "attempt": 1,
    "received_at": "2026-10-06T12:14:07Z", "fetched_at": "2026-10-06T12:14:08Z",
    "retention_class": "meta_on_request",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/instagram/2026/10/06/ig-webhook-receiver/000412.jsonl.zst",
    "post_ref": "17912345678901234", "parent_id": null, "delivery": "push",
    "content_hash": "sha256:5d3b1e9a07c24f86b2a1c9d0e47f3a68b15c2d9e8f0a7b4c63d1e2f9a8b7c6d5"
  },
  "payload": { "...": "the event value, unchanged" }
}
```

Also `reconciliation` and targeted `ops_force` jobs on `jobs.ig-own-comments-fetcher` and `jobs.ig-mentions-fetcher`, `source.events` (`updated`), `service_runs`, and `dlq.ig-webhook-receiver` after 5 failed attempts.

### 6.3 State

Secrets in Supabase Vault; per account, in `cursors` (source × service): `last_success_at`, subscription state, `checked_at` and the reconciliation due time; in memory only the leader lock and the one-hour request memory.

## 7. Limits, quotas and cost

- Meta re-delivers notifications and expects a prompt 200; the deadline and re-delivery timing: to be confirmed in the pilot. The inbound path spends no Graph quota; the reconciliation reads spend quota of the connected account under `ig_graph_<ig_user_id>` (one counter per account), through ig-own-comments-fetcher (50 comments per query) and ig-mentions-fetcher.
- Stories mentions are not supported. Webhooks exist only for client-owned accounts; Business Discovery (business and creator accounts only, age-gated accounts not returned) and the hashtag limit of 30 unique hashtags per business account per 7 days belong to other services.
- Under Instagram Public Content Access, analytics leave the platform only as aggregated, de-identified output; pushed authors keep only a hashed reference downstream unless they are business or creator accounts.
- Cost: USD 0 per notification and per Graph call; the cost is compute and quota. Event volume at full scale (inside Instagram's 4.5M items a month): to be measured in the pilot.

## 8. Failure handling and fallback

- Bad signature: 403, nothing stored, `signature_failed_rate` alert when repeated.
- Redpanda unavailable: answer 500 so Meta re-delivers; an outage longer than Meta's re-delivery window is covered by the hourly reads of ig-mentions-fetcher, the series of ig-own-comments-fetcher and the daily reconciliation. This is the fallback.
- Worker failure: the message is retried with backoff from 30 s to 15 min and `attempt + 1`; after 5 attempts it goes to `dlq.ig-webhook-receiver` and an alert fires.
- HTTP 401 and 403 on subscription management: mark the token `degraded`, alert, never rotate accounts or tokens around a block.
- Silence: an account whose reconciliation keeps finding unpushed items is flagged `push_gap`; source-health-canary may flip `health = degraded` for it.
- Schema change (unknown event shape): the verified body is still kept; normalize-item raises `schema_unknown` and parks the batch.
- Unknown account: dropped and counted.

## 9. Non-functional requirements

- Throughput: Instagram's share of the full-scale target is 4.5M items a month; the push share is to be measured in the pilot.
- Latency: the 200 follows only the signature check and the durable append; an event reaches `raw.items` within seconds of receipt under normal load; the internal time budget is set once Meta's deadline is confirmed.
- Idempotency: `instagram:comment:<id>`, `instagram:post:<id>`; replayable inbound messages; append-only `raw.items`.
- Scaling: stateless front replicas behind the cluster's ingress; workers on partition lag; one leader scheduler.
- Security: signature check in constant time; secrets from Supabase Vault, never logged; no account pools, no proxies; Meta data never processed for law-enforcement or national-security purposes; provenance on every message; retention `meta_on_request`.

## 10. Metrics and alerts

`webhooks_received_total{field}`, `signature_failed_total`, `ack_latency_seconds`, `events_processed_total`, `events_duplicate_total`, `unknown_account_total`, `missed_push_total`, `subscriptions_active`, `reconciliation_lag_seconds`, `dlq_total`. Alerts: `signature_failed_rate`, `ack_latency_high`, `push_gap`, `subscription_lost`, `rotation_behind`, `dlq_nonempty`. SLO: reconciliation lag below one interval for 99% of accounts per day.

## 11. Dependencies

listening-sdk (job schema gains `kind = push` for this queue), ig-own-comments-fetcher, ig-mentions-fetcher, comment-decay-scheduler, normalize-item, raw-archiver, source-health-canary, registry-writer, quota-governor, Supabase Postgres and Vault, Redpanda, the cluster's ingress with a public TLS certificate. Meta prerequisites: Business Verification, App Review (Advanced Access) with the Webhooks product enabled, Access Verification for Tech Providers, annual Data Use Checkup.

## 12. Risks and mitigations

- Endpoint downtime or a slow 200 makes Meta stop delivering: ack only after a fast append, health checks on the ingress, and the polling paths as backstop.
- Duplicate or out-of-order deliveries: stable keys and downstream deduplication.
- Event payloads may carry identifiers only: targeted reads close the gap (open question 2).
- A leaked app secret would let anyone forge events: held in Supabase Vault, rotated through Meta's app settings, never logged.
- Pushed comments understate fetch activity: the pushed count is shared with comment-decay-scheduler.

## 13. Acceptance criteria

1. A handshake `GET` with `hub.mode=subscribe` and the right `hub.verify_token` returns 200 with exactly `hub.challenge` as the body; a wrong token or mode returns 403.
2. A `POST` with a valid `X-Hub-Signature-256` returns 200 only after the body is acknowledged by Redpanda, even when the worker is stopped.
3. A `POST` with an altered body, a wrong signature or no signature returns 403, appends nothing and raises `signature_failed_total`.
4. When the Redpanda append fails the response is 500 and nothing is marked processed.
5. The same notification delivered 3 times produces messages with identical `idempotency_key`s, one item in normalize-item, and one targeted read for the same id within an hour.
6. A notification for an account with no registered owned source writes nothing, raises `unknown_account_total` and creates no source.
7. A `mentions` event carrying identifiers only produces a targeted read for ig-mentions-fetcher and no empty item.
8. Over 7 simulated days every push account gets one `reconciliation` job per day on each of the two queues, due times set from the start of the previous run, and no account's lag exceeds 24 hours; a dormant account is reconciled weekly; a retired account never.
9. A comment present in a reconciliation read but never pushed increases `missed_push_total` by one.
10. A removed subscription is detected by the daily check and re-created; when that fails the source is `degraded` and `source.events` carries `updated`.
11. Every `raw.items` message carries `route`, `vendor`, `service`, `received_at`, `fetched_at`, `delivery = push` and `retention_class = meta_on_request`; the app secret, verify token and tokens never appear in logs.
12. No Stories mention is ever written.

## 14. Open questions

1. Meta's response deadline, retry count and re-delivery schedule: to be confirmed in the pilot.
2. Exact payloads of the `comments` and `mentions` events, which carry items and which identifiers only, and the subscription call and permissions: to be confirmed in the pilot.
3. Does comment-decay-scheduler accept a pushed count per post for its early-stop, extension and hot-post rules? Proposed: yes.
