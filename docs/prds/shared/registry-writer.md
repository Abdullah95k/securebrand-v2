# registry-writer

**Platform:** Shared · **Route:** shared · **Lane:** Registry · **Owner:** Registry backend engineer · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The `sources` table is read by more than sixty services and written, in principle, by a handful: the qualifier's decisions, ops adding a source by hand, a client adding its own page, the canary flipping a route into fallback. If each of those wrote to the table directly, four code paths would race on the same row, nobody would know which write changed the tier, and every downstream service would have to poll the table to learn that something changed.

`registry-writer` is the single writer of registry identity: one path for every change, one idempotent upsert, one audit row per change, and one `source.events` message per change so the pollers, `backfill-orchestrator`, `comment-decay-scheduler`, `retention-purger`, `quota-governor` and `store-writer` react within seconds instead of discovering the change on their next scan.

Without it, the registry drifts: a source added twice under two ids is polled twice and billed twice; a retired source keeps getting polled because nobody told the scheduler; a client offboarding leaves Meta data that `retention-purger` never hears about; and when a client asks why a page is being watched, there is no answer.

## 2. Objective (the end state this service delivers)

Every `registry.decisions` message, from `qualifier`, from ops, from a client, or from `source-health-canary`, is applied to `sources` and `client_sources` exactly once, with an audit row that records who changed what and why, and is announced on `source.events` within 10 seconds of the commit. Replaying a decision changes nothing. A source exists once, keyed on `(platform, platform_id)`, whatever path added it.

Targets: 100% of applied decisions have an audit row and an event; event latency p99 under 10 seconds; zero duplicate sources per `(platform, platform_id)` (enforced by a unique index, verified daily).

## 3. Scope

### In scope
- Consuming `registry.decisions` and applying `add`, `update`, `tier_change`, `tier_down`, `dormant`, `promote`, `retire`, `health_change`, `remove_client`, `queued` (recorded, not written to `sources`) and `mention_only` (recorded only).
- Idempotent upserts into `sources` and `client_sources`.
- Emitting `source.events`: `added`, `updated`, `tier_change`, `dormant`, `retired`, `fallback_on`, `fallback_off`.
- The manual-add path: an HTTP endpoint for the ops admin page and the client app that resolves the candidate through `poster-resolver` and `qualifier` before writing.
- The audit log `registry_audit` (proposed here; one row per applied or rejected decision, before and after values) that doubles as the event outbox.
- Owning the identity and policy columns of `sources`: `platform`, `source_type`, `platform_id`, `handle`, `url`, `display_name`, `route`, `vendor`, `tier`, `retention_class`, `client_ids`, `owned_by_client`, `followers`, `country_signals`, `lang_share`, `added_by`, `added_at`, `health`, `notes`.

### Out of scope
- The operational columns written by their owners through the SDK's control-plane client: `last_hit_at` (`keyword-matcher`), `last_polled_at` and `next_poll_at` (the pollers), `backfill_status` (`backfill-orchestrator`).
- Deciding anything: tier, route and class arrive decided.
- Subscribing webhooks or PubSubHubbub leases for client-owned sources: `fb-client-webhook-receiver`, `ig-webhook-receiver`, `li-notification-receiver`, `yt-pubsub-receiver` and `tg-bot-channel-receiver` react to `added` themselves.

## 4. Users and consumers

- Producers of decisions: `qualifier`, `source-health-canary` (`health_change`), ops (admin page), client admins (client app), `retention-purger` (`remove_client` on offboarding).
- Consumers of `source.events`: `backfill-orchestrator`, every poller's scheduler, `comment-decay-scheduler`, `retention-purger`, `quota-governor`, `store-writer` (`sources_dim`), `aggregator`, the webhook and PubSubHubbub receivers.
- `poster-resolver`: receives manual candidates from this service.
- Account managers and auditors: read `registry_audit`.

## 5. How it works

### 5.1 Trigger and rotation

Event-driven: a message on `registry.decisions`, or an HTTP call on the manual-add endpoint. A relay loop every 5 seconds re-publishes any audit row whose `event_published_at` is null (the outbox). No rotation and no backfill, except a one-time migration that loads the pilot's hand-maintained source list through the manual path with `added_by = ops`.

### 5.2 Step by step

1. Read the decision; look up `registry_audit` by `decision_id`. Found → re-publish its event if unpublished, acknowledge, stop (replay).
2. Open a transaction. Lock the `sources` row by `(platform, platform_id)` (`SELECT ... FOR UPDATE`), or none if new.
3. Apply by decision type:
   - `add`: insert `sources` with the decision's columns, `added_by` from `origin` (qualifier, client, ops), `added_at = now`, `health = ok`, `backfill_status = pending`, `next_poll_at = now`; insert `client_sources` for each client. If the row exists (re-add of a retired source, or a second client adding a watched source): append the clients, keep the lower tier number (higher reach wins), restore `tier` from `retired` to the decision's tier, and emit `updated` plus `tier_change` instead of `added`. A re-added retired source emits `added` so `backfill-orchestrator` fills the gap.
   - `tier_change`, `tier_down`, `promote`, `dormant`, `retire`: update `tier`; emit `tier_change`, `dormant` or `retired`.
   - `health_change` (from the canary; carries `platform`, `route`, `vendor`, `health`, `fallback`): bulk update `health` for every source on that route and vendor; emit `fallback_on` or `fallback_off` per source, or `updated` for `degraded` and `ok`.
   - `remove_client`: delete the `client_sources` row; if no client remains and `added_by = client`, set `tier = retired`; emit `updated` (and `retired`).
   - `update`: identity and policy columns only; a change to `route` or `vendor` emits `updated` with `previous`.
   - `queued`, `mention_only`: audit row only.
4. Write the `registry_audit` row (`decision_id`, `source_id`, `action`, `actor`, `before`, `after`, `applied_at`, `event_published_at = null`).
5. Commit, publish to `source.events`, set `event_published_at`.

Manual add: `POST /registry/sources` with `{platform, url_or_handle, client_id, tier_override?, priority?, owned_by_client?, notes}` from the admin page or the client app. The service validates the caller's role, publishes a `manual_candidate` to `jobs.poster-resolver` with `origin: manual`, and returns a `request_id`. `qualifier` answers through `registry.decisions`; the caller polls `GET /registry/requests/{request_id}` or receives the n8n notification. A client cannot add an individual (rule 7), cannot set `route = amber` when the client is a government body, and cannot add a source to another client.

### 5.3 The call it makes

No external call. The SQL is the logic:

```sql
INSERT INTO sources (source_id, platform, source_type, platform_id, handle, url, display_name, route, vendor, tier, retention_class, client_ids, owned_by_client, followers, country_signals, lang_share, added_by, added_at, health, backfill_status, next_poll_at)
VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, now(), 'ok', 'pending', now())
ON CONFLICT (platform, platform_id) DO UPDATE SET
  client_ids = (SELECT array_agg(DISTINCT c) FROM unnest(sources.client_ids || EXCLUDED.client_ids) c),
  tier = CASE WHEN sources.tier = 'retired' THEN EXCLUDED.tier ELSE least_tier(sources.tier, EXCLUDED.tier) END,
  followers = EXCLUDED.followers, display_name = EXCLUDED.display_name, handle = EXCLUDED.handle
RETURNING source_id, (xmax = 0) AS inserted;
```

`client_sources` is upserted on `(client_id, source_id)` with `added_at`, `priority`, `added_by`.

### 5.4 What it gets

From `registry.decisions`: the full decided row (see the `qualifier` PRD's example). From the manual endpoint: a URL or handle, a client, optional overrides. From the canary: a route-level health change. What it does not get: items, metrics, cursors, or anything about individuals beyond a `mention_only` audit row that carries an `author_hash` and no identity.

## 6. Inputs and outputs

### 6.1 Reads
- Topic `registry.decisions`.
- HTTP: manual-add and request-status endpoints (authenticated through Supabase Auth roles: `ops`, `client_admin`).
- Tables: `sources`, `client_sources`, `clients` (government flag, roles), `registry_audit`.

### 6.2 Writes
- Tables `sources`, `client_sources`, `registry_audit`.
- Topic `source.events`, partition key `source_id`:

```json
{"message_id":"se:7f1c...:added","produced_at":"2026-10-06T10:14:41Z","service":"registry-writer","schema_version":1,"event":"added","source_id":"7f1c2a9e-5d1b-4c7e-9a3f-2b8e6d4c1a00","platform":"instagram","source_type":"account","platform_id":"17841400000000000","handle":"baghdad_eats","route":"green","vendor":null,"tier":2,"retention_class":"meta_on_request","client_ids":["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],"owned_by_client":false,"followers":48200,"previous":null,"decision_id":"01J9Z...","actor":"qualifier","at":"2026-10-06T10:14:40Z"}
```

Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

A `tier_change` event carries `previous: {"tier": 3}`; a `fallback_on` event carries `previous: {"health": "ok", "route": "green", "vendor": null}` and the new `health: "fallback"`.

### 6.3 State
- `registry_audit`: the idempotency record and the outbox.
- `service_runs`: lag, unpublished-event count, manual requests pending.
- No cursors.
- Owners (ADR-0025): `registry_audit` and `registry_outbox` are shared control-plane tables whose one writer is this service (ADR-0045).

## 7. Limits, quotas and cost

No platform spend. Load at full scale: the decision rate is the qualifier's decision rate plus sweep output, to be measured in the pilot; a `health_change` on a busy route can touch every source on it in one statement and emit one event per source (the number of sources per route is to be measured; the bulk update is a single `UPDATE ... WHERE route = $1 AND vendor = $2 AND platform = $3`). One replica; Postgres row locks serialise writes per source. The audit table grows by one row per decision and is retained ten years, as the registry's history is part of the ten-year aggregate promise.

## 8. Failure handling and fallback

- Postgres unavailable: the consumer pauses; nothing is acknowledged; Redpanda retains the decisions.
- Commit succeeded, publish failed: the relay loop publishes from the audit row within 5 seconds; consumers may see an event twice and must treat `message_id` as idempotent (every consumer PRD states this).
- Unique-index violation from a race between two `add` decisions for the same `(platform, platform_id)`: the second becomes an `update` that merges clients.
- A decision referencing an unknown `source_id` (sweep output for a source deleted by hand): audit row with `action = rejected`, alert `orphan_decision`.
- Manual-add validation failure: HTTP 422 with the rule that failed; no candidate is published.
- Poison message: 5 failed attempts → `dlq.registry-writer` and alert; the audit row records the failure.

## 9. Non-functional requirements

- Idempotency: `decision_id` is the unit; replaying the whole `registry.decisions` topic from offset 0 against a populated registry produces zero row changes.
- Latency: commit within 2 seconds, event within 10 seconds, p99.
- Scaling: one replica; partitions of `registry.decisions` allow more, with row locks keeping per-source order.
- Security: role checks on the manual endpoint; `registry_audit` is append-only (no UPDATE or DELETE grant); secrets from Supabase Vault; logs carry `decision_id`, `source_id`, `route`, `vendor`.
- Compliance: `mention_only` audit rows hold only the `author_hash`; a client offboarding (`remove_client`) is announced so `retention-purger` can act on `meta_on_request` data.

## 10. Metrics and alerts

`decisions_applied_total{action}`, `decisions_noop_total`, `events_published_total{event}`, `event_publish_latency_seconds`, `outbox_unpublished`, `manual_requests_total{status}`, `jobs_total{status}`, `dlq_total`. Alerts: `outbox_stuck` (unpublished events older than 60 seconds), `registry_duplicate` (the daily uniqueness check finds two rows for one `(platform, platform_id)`), `orphan_decision`, `registry_writer_dlq`.

## 11. Dependencies

- Upstream: `qualifier`, `source-health-canary`, `retention-purger`, admin page, client app.
- Sideways: `poster-resolver` (manual candidates), Supabase Auth, Supabase Vault, n8n (request notifications).
- Downstream: every consumer of `source.events` listed in section 4.

## 12. Risks and mitigations

- Operational columns written by other services collide with this service's row locks: the SDK's control-plane client updates only its own columns with short transactions and never takes `FOR UPDATE`.
- An event storm from a route-wide `health_change`: events are published in batches per partition and consumers are built to coalesce; the canary flips a route at most once per 15-minute window.
- The audit table becomes the only history and is edited: append-only grants and a nightly export to the Parquet archive under `archive/registry/<yyyy>/<mm>/`.
- A client with many admins adds the same page repeatedly: the upsert merges, and the request status shows "already watched".

## 13. Acceptance criteria

1. An `add` decision for a new `(platform, platform_id)` creates one `sources` row, one `client_sources` row, one `registry_audit` row and one `added` event, in that order, within 10 seconds.
2. The same decision replayed produces no row change, no new audit row, and at most one re-published event with the same `message_id`.
3. A second `add` from another client for a watched source appends the client, emits `updated`, emits no `added`, and the tier is the higher-reach of the two.
4. A `retire` decision sets `tier = retired`, emits `retired`, and the row remains in `sources`.
5. A `health_change` with `fallback = on` for `platform = tiktok, route = amber, vendor = tikhub` sets `health = fallback` on every matching source and emits one `fallback_on` event per source with `previous.health`.
6. Killing the service between commit and publish leaves `event_published_at` null; the relay publishes the event within 5 seconds of restart.
7. A client admin posting a manual add for an individual account receives HTTP 422 citing rule 7 and no `sources` row is created.
8. A government client posting a manual add with `route = amber` receives HTTP 422; the same request from a non-government client passes to `poster-resolver`.
9. A `remove_client` decision for a source watched by one client leaves the row with empty `client_ids`, `tier = retired`, and emits `updated` then `retired`.
10. An attempt to `UPDATE` or `DELETE` on `registry_audit` with the service role fails with a permission error.

## 14. Open questions

- `registry_audit` is a new control-plane table; confirm it joins the CONVENTIONS list, or whether `decisions` should carry the before/after values.
- Whether a source re-added after retirement should keep its old `source_id` (assumed yes, so history joins).
- Whether `tier_override` from a client (priority list) can place a source in tier 1 without the follower threshold (CONVENTIONS allows "on a client's priority list"; assumed yes).
- Whether `health_change` should be carried on `registry.decisions` or on a dedicated topic.
