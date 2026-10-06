# li-notification-receiver

**Platform:** LinkedIn · **Route:** green · **Lane:** Comments · **Owner:** Backend lead, LinkedIn adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

li-client-posts-poller looks at a client's page every 30 to 60 minutes and li-own-comments-fetcher reads the comments at +6 h, +24 h and +3 d. Between those looks the product is blind: a hostile thread under a tender announcement could grow for hours before anyone sees it. LinkedIn's Organization Social Action Notifications close that gap: LinkedIn calls us when a member comments on or reacts to a post of a page we are subscribed to, so the comment and the reaction arrive as they happen. The Community Management API reaches only pages the client administers (the organization must grant ADMINISTRATOR, DIRECT_SPONSORED_CONTENT_POSTER or CONTENT_ADMIN), so this service exists for client pages only; there is no push for third-party pages.

Without it, LinkedIn alerts wait for the next fetch (up to 6 hours for a new post), hot-post detection (more than 100 new comments an hour) cannot see velocity between fetches, and reaction movement is visible only at poll time. The product would still work, but slower.

## 2. Objective (the end state this service delivers)

Every comment and reaction event on a subscribed client page is verified, written to `raw.items` and only then acknowledged to LinkedIn, within a latency bound set in the pilot (proposed: 60 seconds from receipt to Redpanda acknowledgement for 99% of events); every subscribed page has a live subscription each day; and whatever push misses is closed by the daily reconciliation. Target: zero unverified events processed, zero member rows older than 48 hours, every subscribed page covered by the reconciliation every 24 hours.

## 3. Scope

### In scope

- The public HTTPS endpoint LinkedIn calls: validation handshake, signature verification, fast acknowledgement.
- Subscription management per client page: create, check every 24 hours, renew or re-create, remove on retirement, offboarding or lost grant.
- Event handling: comment created or edited (kind `comment`), comment deleted (`deletions`), reaction added (kind `reaction`), reaction removed (`deletions`).
- One enrichment lookup per event when an event carries identifiers but not the comment text.

### Out of scope

- Posts (li-client-posts-poller), scheduled and reconciliation comment reads (li-own-comments-fetcher, jobs from comment-decay-scheduler), third-party pages (amber services; no push exists).
- Members' own posts that mention the organization: acknowledged and dropped (member social activity we cannot export and the product does not need; to be confirmed in the pilot).
- Profile lookups for commenters or reactors; purging (retention-purger); normalization and aggregation.

## 4. Users and consumers

- **Clients** experience it as faster LinkedIn alerts and live counts; they see aggregates, and comment text only inside the application.
- **Ops** watches signature failures, silent subscriptions and delivery lag.
- **Downstream**: normalize-item, comment-decay-scheduler (counts comments from `items.normalized`, measures velocity), li-own-comments-fetcher, aggregator, alert-evaluator, retention-purger, raw-archiver, source-health-canary, quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Push. LinkedIn calls the endpoint for a subscribed organization. There is no job queue and no rotation scheduler: the delivery is the trigger. This is the push tier of the rotation policy applied to comments and reactions: no polling for events, one reconciliation a day.

**Subscriptions.** One per client-administered page, created when registry-writer announces the page (`source.events` `added`, `owned_by_client = true`, `route = green`) and removed on `retired`, client offboarding or a lost grant. Once every 24 hours every subscribed page is checked: events received in the last 24 hours, `last_event_at`, and the subscription's state where LinkedIn lets us read it (to be confirmed in the pilot). A page whose comment count grew (observed by li-client-posts-poller) while no event arrived for 24 hours is `subscription_silent`: the service re-subscribes if the authorizing token is valid, otherwise raises `grant_lost` and the client is asked to re-authorize.

**Daily reconciliation.** Push is best-effort, so the product never relies on it alone. (1) li-client-posts-poller re-reads every page's last 7 days of posts and counts once a day. (2) When a post's comment count differs from the running total of comments seen, comment-decay-scheduler emits a reconciliation job for li-own-comments-fetcher, which reads the whole thread. (3) The +6 h, +24 h, +3 d series run as usual. Comments received here are counted from `items.normalized` like any others, so a later fetch reports them as `seen_count` and early stop stays meaningful.

**Hot posts.** Live events give comment-decay-scheduler the velocity between fetches; above 100 new comments an hour it inserts an hourly fetch for the next 6 hours.

**Catch-up and backfill.** Push has no history. After an outage of this endpoint the reconciliation recovers the window within 24 hours. A new page's past comes from backfill-orchestrator (li-client-posts-poller's backfill and one-off li-own-comments-fetcher jobs); the subscription covers everything after the page is added.

### 5.2 Step by step

1. LinkedIn sends a delivery. The endpoint reads the raw body bytes.
2. Verify the signature: HMAC-SHA256 of the raw body with the app's client secret (from Supabase Vault), compared in constant time with the signature header (header name and encoding to be confirmed in the pilot). Mismatch: respond 401, store nothing, count `signature_failed_total`.
3. Parse the events (a delivery may carry several). For each, map the organization URN to a `sources` row (`platform = linkedin`, `owned_by_client = true`); an unknown organization is counted `unknown_org_total` and dropped, with a 200 so LinkedIn does not retry.
4. Classify by event type (table in 5.4); drop and count types that are out of scope.
5. Write to `raw.items` (comments: payload as received, `linkedin_48h`; reactions: the actor replaced by a hashed reference, `identity: "hashed"`, because no consumer needs a reactor's identity and a comment's author is shown inside the application while a reactor never is) or to `deletions`.
6. After Redpanda acknowledges, respond 2xx. If the produce fails, respond 5xx so LinkedIn can redeliver (retry behavior to be confirmed in the pilot); the reconciliation is the safety net either way.
7. After the response, if a comment event carried no text, make one Comments API lookup of that comment with the client's token and write a second `raw.items` message with the same `idempotency_key` and the full comment; on quota deny or error, leave it for the next li-own-comments-fetcher read.
8. Update the per-page counters and `last_event_at` in `service_runs`.

### 5.3 The call it makes

```
Inbound   POST <our webhook host>/linkedin/organization-social-actions   (HTTPS only; path to be set)
          header: signature (name to be confirmed in the pilot)   body: one or more events
Handshake GET same path with a challenge parameter
          -> 200 with the challenge and its HMAC-SHA256 under the app's client secret
             (parameter names to be confirmed in the pilot)
Outbound  registration: LinkedIn's event-subscription call for (our app, the authorizing
          administrator, the organization URN, event type Organization Social Action
          Notifications) with our webhook URL; path, key structure and body to be confirmed
          in the pilot. Used on page add, 24-hour check, re-subscribe and removal.
Outbound  enrichment (only when an event lacks the text): Comments API single-comment lookup,
          as in li-own-comments-fetcher, budget tag linkedin_cm:<client_id>
```

Authentication outbound: the client's OAuth token. The subscription may be tied to the authorizing administrator's token (to be confirmed in the pilot, section 14).

### 5.4 What it gets

An event, illustratively (field names to be confirmed in the pilot):

```json
{
  "organizationalEntity": "urn:li:organization:12345678",
  "action": "COMMENT",
  "actor": "urn:li:person:AbCdEfGh12",
  "sourcePost": "urn:li:share:7247000000000000001",
  "generatedActivity": "urn:li:comment:(urn:li:share:7247000000000000001,7247000000000000100)",
  "eventTime": 1791298934000
}
```

| Event (names to be confirmed) | Handling |
|---|---|
| comment created or edited | `raw.items` kind `comment`, key `linkedin:comment:<comment URN>` |
| comment deleted | `deletions`, reason `platform_sync`; held copy removed |
| reaction added | `raw.items` kind `reaction`, actor hashed |
| reaction removed | `deletions`, reason `platform_sync` |
| member post mentioning the organization | acknowledged, dropped |

What it does not get: history, events for unsubscribed pages, new-post announcements (to be confirmed in the pilot), profile data.

## 6. Inputs and outputs

### 6.1 Reads

Inbound deliveries; `sources` (organization to `source_id`, `client_ids`), `clients` and Supabase Vault (client secret, tokens), `budgets` through quota-governor (enrichment and subscription calls only), `source.events`, `item.metrics` (comment counts, for the silence check).

### 6.2 Writes

`raw.items`, one message per event:

```json
{
  "envelope": {
    "platform": "linkedin", "kind": "comment", "route": "green", "vendor": null,
    "service": "li-notification-receiver",
    "source_id": "3d2f8a14-6b7c-4e19-8a05-c1f7e2b94d36",
    "platform_id": "urn:li:comment:(urn:li:share:7247000000000000001,7247000000000000100)",
    "idempotency_key": "linkedin:comment:urn:li:comment:(urn:li:share:7247000000000000001,7247000000000000100)",
    "post_ref": "urn:li:share:7247000000000000001",
    "job_id": "01J9N5K2W8T4R6Y1B3D7F0GHMQ", "attempt": 1,
    "fetched_at": "2026-10-06T15:02:15Z",
    "retention_class": "linkedin_48h",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "batch": "raw/green/linkedin/2026/10/06/li-notification-receiver/000003.jsonl.zst"
  },
  "payload": { "...": "the event from 5.4 as received, plus the comment text if the lookup returned it" }
}
```

`job_id` is a ULID assigned at receipt; `attempt` is 1. `fetched_at` is the receipt time. Also `deletions`, `service_runs` (per-page `last_event_at`, event counts), `source.events` (`updated` when a grant is lost).

### 6.3 State

Per page: subscription state, `last_event_at`, daily event counts (in `service_runs`); no event store of its own; in memory nothing that cannot be rebuilt.

## 7. Limits, quotas and cost

- **Restricted-use facts (LinkedIn terms).** Member social-activity data stored at most 48 hours; most member profile data 24 hours; organization social activity data six weeks (six months if authenticated); no social-feed use; member data never exported or transferred to clients, client-facing output is aggregated.
- **Retention.** Comment events, reaction events and their raw objects carry `linkedin_48h` and are deleted by retention-purger within 48 hours of `fetched_at`; hourly aggregates (comments and reactions per post per hour) are computed first and kept ten years. Comment text and commenter references are shown only inside the application, never in an export, report, API or alert.
- **Quota.** Inbound deliveries cost no quota. Outbound calls (subscription management, enrichment lookups) use `linkedin_cm:<client_id>`, one unit per call. LinkedIn's limits on subscriptions per app and on delivery rate: to be measured in the pilot.
- **Cost.** No per-call fee is listed for the Community Management API (USD 0 as far as the fact sheet shows).

## 8. Failure handling and fallback

- Signature mismatch: 401, nothing stored; a spike alerts (secret rotated or spoofing).
- Redpanda produce failure: 5xx, no acknowledgement; the reconciliation closes any loss.
- Malformed body: 400. Unknown event shape: 200, payload archived under the 48-hour prefix, batch parked as `schema_unknown`.
- Duplicate deliveries: harmless; normalize-item deduplicates on the key.
- Subscription lapse: detected by the 24-hour check, re-subscribed or `grant_lost`.
- Enrichment 429: backoff with jitter from 30 s to 15 min, then left for the next li-own-comments-fetcher read; HTTP 401 or 403: token `degraded` or page `blocked` as in li-own-comments-fetcher; no token or IP rotation.
- Endpoint outage: events in the gap are recovered by the daily reconciliation. No amber fallback exists or is wanted.

## 9. Non-functional requirements

- Throughput: events per day are to be measured in the pilot; LinkedIn is 0.15M of 30.5M items a month in total.
- Latency: receipt to Redpanda acknowledgement within the bound set in the pilot (proposed: 60 seconds, 99% of events); the response to LinkedIn never waits for the enrichment lookup.
- Availability: stateless replicas behind a load balancer; TLS only; body size limit.
- Idempotency: `linkedin:comment:<platform_id>`; `linkedin:reaction:<platform_id>`; redelivery is safe.
- Security: secret from Supabase Vault, constant-time comparison; logs carry ids only, never bodies, person URNs or comment text.

## 10. Metrics and alerts

`events_received_total{type}`, `events_written_total{kind}`, `events_dropped_total{reason}`, `signature_failed_total`, `unknown_org_total`, `ack_latency_seconds`, `delivery_lag_seconds` (receipt minus event time), `enrichment_calls_total{status}`, `subscriptions_active`, `subscriptions_silent`, `dlq_total`. Alerts: `signature_failed_spike`, `subscription_silent`, `grant_lost`, `produce_failing`, `endpoint_down`.

## 11. Dependencies

listening-sdk, quota-governor, source-health-canary, raw-archiver, normalize-item, comment-decay-scheduler, li-own-comments-fetcher, li-client-posts-poller, registry-writer, backfill-orchestrator, retention-purger, aggregator, alert-evaluator, Supabase Postgres and Vault, Redpanda, a public HTTPS ingress with a certificate.

## 12. Risks and mitigations

- Delivery is best-effort: the daily reconciliation is part of the design, not an extra.
- The subscription may lapse silently with the authorizing token: the 24-hour check and `grant_lost`.
- Spoofed deliveries: signature verification before any parsing of content; secret in Vault.
- Viral posts produce event bursts: stateless scaling, Redpanda buffering.
- Webhook access may need separate LinkedIn approval: the pilot starts with polling and the reconciliation, which already work without push.
- Member data in logs: ids only.

## 13. Acceptance criteria

1. A delivery with a valid signature is written to `raw.items` and acknowledged 2xx only after Redpanda acknowledges; with Redpanda unavailable it returns 5xx.
2. A delivery with a wrong or missing signature returns 401, stores nothing and increments `signature_failed_total`.
3. The validation handshake returns the HMAC of the challenge; a different secret gives a different answer.
4. The same comment-created event delivered twice yields two messages with the same `idempotency_key` and one stored comment.
5. A comment-deleted event yields one `deletions` message with reason `platform_sync` and the held copy is removed.
6. A reaction event leaves no reactor person URN in any message, log line or store; the message carries `identity = hashed`.
7. An event for an organization not in `sources` returns 200, writes nothing and increments `unknown_org_total`.
8. A page whose comment count grows while no event arrives for 24 hours raises `subscription_silent`, and the next li-own-comments-fetcher reconciliation brings the stored count in line.
9. With the endpoint down for 3 hours in a simulation, every comment of that window is in the store within 24 hours without duplicates.
10. Every `linkedin_48h` row and raw object written by this service is deleted within 48 hours of `fetched_at`.
11. When a page is retired or its client offboards, the subscription is removed within one check and later events for it are dropped.
12. An event without comment text triggers one lookup after the response was sent; on quota deny the event stays without text and no error reaches LinkedIn.

## 14. Open questions

1. Event types, payload fields (does an event carry the comment text? announce new posts?), retry behavior, signature header and handshake parameters: all to be confirmed in the pilot.
2. Is the subscription bound to the authorizing administrator's token, and does it lapse when that token expires?
3. Do notifications cover replies and reaction removal? Assumed yes.
4. Should normalize-item turn reaction events into counter increments, or should counts come only from li-client-posts-poller's reads? Proposed: both, with the poller's absolute counts as the baseline.
5. Hashing the reactor at the edge departs from "exactly as received" in `raw.items`, as in li-post-comments-fetcher: to confirm with the raw-archiver owners.
