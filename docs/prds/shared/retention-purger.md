# retention-purger

**Platform:** Shared · **Route:** shared · **Lane:** Support · **Owner:** Backend lead, compliance and retention · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

We hold content that belongs to other people, under rules that differ by source. X wants deletions mirrored within 24 hours. YouTube wants raw comment text deleted or refreshed after 30 days. LinkedIn lets us keep member social-activity data for 48 hours and most member profile data for 24 hours. Meta wants Platform Data deleted when it is no longer necessary, on its request, when a client leaves, or when a user asks. Vendor contracts and our author notice set 24 months for raw text by default. News full text may sit in a cache for 7 days only. Against that, clients are buying ten years of history, which we deliver as aggregates and derived scores.

retention-purger is the service that owns these clocks. It decides what is due, asks for it to be deleted, and proves afterwards that each clock was met. Without it, each rule would live in a different service or in nobody's head, and the first sign of a breach would be a platform audit, a revoked API key (X, YouTube and Meta can all end access), a lost government tender, or a client or author who learns their data was kept. It also keeps the ten-year promise honest: it deletes identifiable raw data on time and never touches aggregates.

## 2. Objective (the end state this service delivers)

Every record in ClickHouse, object storage and caches is removed or stripped of text no later than its retention clock allows; every client offboarding and author request is carried out inside its service level; and every run leaves an audit record that shows, with query results, that each clock was met. Target: zero clock breaches, every audit record `pass`, X deletions complete within 24 hours of the compliance signal, author requests within 7 days and client offboarding within 30 days (the last two to be confirmed with counsel).

## 3. Scope

### In scope

- The clock table per retention class and the scheduled sweeps that apply it.
- Emitting `deletions` with reasons `retention`, `author_request` and `client_offboarding`; watching the `platform_sync` deletions that x-compliance-sync emits for the 24-hour X clock.
- Delegating the `youtube_30d_text` clock to yt-text-purger and verifying the result.
- Client offboarding: `remove_client` decisions, the purge plan, and revoking client credentials.
- The deletion channel: intake of author requests, hashing, tracking to completion.
- One audit record per run and per request.

### Out of scope

- Doing the deletion in ClickHouse, archives, caches and the text index, recomputing aggregates and notifying clients (deletion-propagator).
- Polling X compliance (x-compliance-sync); refreshing or deleting YouTube text (yt-text-purger); object-store lifecycle rules and partition rewrites (raw-archiver).
- Deleting aggregates or derived scores: kept ten years, all classes.

## 4. Users and consumers

- **Ops and the compliance owner** read audit records, enter legal and platform requests, and approve offboarding.
- **Clients** see offboarding confirmations and, through their account manager, the audit evidence.
- **Authors** (people whose posts we hold) use the deletion channel.
- **Downstream services**: deletion-propagator (consumes `deletions`), yt-text-purger (receives jobs), registry-writer (applies `remove_client`), alert-evaluator (alerts), raw-archiver (lifecycle), store-writer.

## 5. How it works

### 5.1 Trigger and rotation

Five triggers. (1) A scheduled sweep from a leader-elected loop (Postgres advisory lock); the period is an environment variable set well inside the shortest clock it serves (24 hours), initial value to be measured in the pilot. (2) `source.events` of type `retired` or `updated` for sources whose `client_ids` became empty, which opens the `meta_on_request` necessity clock. (3) A `clients` row moving to `offboarding`. (4) A new `deletion_requests` row from the deletion channel (n8n intake form and mailbox). (5) Every `deletions` message that x-compliance-sync emits, which starts the 24-hour X deadline watch.

No backfill and no catch-up queue are needed: each sweep recomputes what is due from the data, so a missed sweep is repaired by the next one, and `sweep_missed` alerts when two periods pass without a run.

### 5.2 Step by step

1. Load the clock table from `retention_classes` (class, anchor, clock, mode, executor, vendor overrides).
2. For each class, run the class procedure of 5.3, which ends in emitted `deletions` or a delegated job.
3. Wait for completion by polling `deletion_requests` for the sweep's `deletion_id`s.
4. Run the verification queries (a count of rows past their clock in ClickHouse `items` and `comments`, a check of raw-archiver manifests and the cache for the same cut-off).
5. Write the audit record: `pass` only if every verification count is zero for the cut-off; otherwise `fail` and `clock_breach`.
6. Process pending offboarding and author requests (5.3).

### 5.3 The call it makes

This service calls no platform. It runs this logic. The cut-off for a clock is `now() − clock`; the sweep also selects records due within the next sweep period, so a record is deleted before its deadline, not after.

| Class | Anchor | Clock | What the sweep does | Executor |
|---|---|---|---|---|
| `x_24h_sync` | `signal_at` (X compliance signal) | 24 hours | Nothing by time. Watches `deletions` from x-compliance-sync; each open deletion must reach `completed` within 24 hours of `signal_at` | deletion-propagator |
| `youtube_30d_text` | `fetched_at` of the text | 30 days | Sends a `retention_sweep` job with the cut-off to `jobs.yt-text-purger`; verifies afterwards | yt-text-purger |
| `linkedin_48h` | `fetched_at` | 48 hours for member social activity; 24 hours for member profile data; organization data as the API terms allow | Emits `deletions` (mode `delete`) by `kind` | deletion-propagator |
| `meta_on_request` | Event, not time | Delete when no longer necessary, on Meta's request, on offboarding, on a user's request | Necessity review, offboarding, author requests; Meta's instruction is entered by ops with `signal_at` | deletion-propagator |
| `vendor_agreed` | `fetched_at` | 24 months for raw text, or the vendor override | Emits `deletions` (mode `purge_text`) | deletion-propagator |
| `news_excerpt` | `fetched_at` of the full text | 7 days for the full-text cache | Emits `deletions` (mode `purge_text`); excerpt and metadata stay | deletion-propagator |
| Aggregates and derived scores | Not applicable | Ten years, all classes | Never selected; the audit records that none was touched | none |

**Modes.** `delete` removes the item and its derived rows and triggers an aggregate recompute (aggregator). `purge_text` removes text and author reference but keeps derived scores and aggregates.

**Selection.** Candidate ids come from ClickHouse `items` and `comments` (the columns the TTL rules already use: `retention_class`, `fetched_at`, `item_id`), pruned by monthly partition. Ids go out in chunks as one `deletions` message per `source_id`. The `deletion_id` is deterministic: `del:<reason>:<scope>:<sha256(target, class, cut-off day)>`, so a repeated sweep emits the same ids and deletion-propagator acts once.

**Necessity review (`meta_on_request`).** When a source is `retired` with empty `client_ids`, the clock starts; after a grace period (to be agreed with counsel) the sweep emits `deletions` for the source's items under reason `retention`.

**Client offboarding.** On `clients.status = offboarding`: (1) emit one `remove_client` decision per `client_sources` row to `registry.decisions`; registry-writer retires client-added sources left without a client and announces it on `source.events`; (2) plan the scope: everything fetched with the client's own tokens or webhooks (`owned_by_client`), all `meta_on_request` items whose `client_ids` contain only this client, and the client's keyword, alert and webhook configuration; (3) emit `deletions` with reason `client_offboarding`, scope `client`, one per affected `source_id`; items shared with another client keep that client and lose this id; (4) revoke the client's tokens and delete their Vault secrets and `vendor_keys` rows; (5) hold the offboarding record open until deletion-propagator completes, then close it with the audit record. Due in 30 days (to be confirmed with counsel).

**Author requests.** The deletion channel creates a `deletion_requests` row with the requester's contact and the author's handle or profile URL. The service computes `author_hash` with the SDK helper that normalize-item uses (`AUTHOR_HASH_KEY` from Supabase Vault), erases the handle from the row, and emits `deletions` with reason `author_request`, scope `author`. Due in 7 days (to be confirmed with counsel). The requester gets a confirmation when the audit record passes.

**Legal holds.** Ops can enter a `legal` deletion, or a hold that suspends a sweep for named ids; a hold is recorded in the audit.

### 5.4 What it gets

Reads: clock definitions, ClickHouse candidate ids and counts, `deletion_requests` status, `source.events`, `clients`, `deletions` from x-compliance-sync (with `signal_at`). It does not get platform content, text or media; it handles ids, hashes, classes and dates only.

## 6. Inputs and outputs

### 6.1 Reads

`source.events`, `deletions` (X signals), Postgres `retention_classes`, `clients`, `client_sources`, `sources`, `deletion_requests`, `vendor_keys`; ClickHouse `items` and `comments` (select and count only); raw-archiver manifests for the verification step.

### 6.2 Writes

`deletions`; `registry.decisions` (`remove_client`); `jobs.yt-text-purger`; Postgres `deletion_requests` (intake and status), `service_runs`, and the new append-only table `retention_audit` (to be added to the control-plane table list). Partition key of `deletions` is `source_id`; author-scope messages are keyed by `author_hash`. Example `deletions` message:

```json
{
  "deletion_id": "del:retention:item:7c1f0a9e3b52d6e48a0c9d1f5b7e2a34c8d6f01b9e3a5c7d2f4b6a8c0e1d3f5a",
  "reason": "retention", "scope": "item", "mode": "purge_text",
  "retention_class": "vendor_agreed",
  "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
  "target": {"platform": "tiktok", "kind": "post", "item_ids": ["01J9N2Q7Z4T8X1V6M3K0H5R2WB"]},
  "client_id": null,
  "requested_by": "retention-purger", "run_id": "01J9P8A3V5N7B2D4F6H0K1M9QS",
  "signal_at": "2026-10-06T00:00:00Z", "due_at": "2026-10-06T06:00:00Z",
  "emitted_at": "2026-10-06T00:05:12Z"
}
```

Audit record (`retention_audit`): `run_id`, `started_at`, `finished_at`, `class`, `clock`, `cutoff`, `candidates`, `emitted`, `completed`, `delegated_to`, `verification` (query text, result count, executed at), `oldest_remaining_age_seconds`, `status`, `holds`.

### 6.3 State

`retention_audit` and `deletion_requests` in Postgres; the leader lock; per-sweep watermark per class in `cursors` (`service = retention-purger`, `cursor` = last cut-off); nothing else in memory.

## 7. Limits, quotas and cost

- No external API and no vendor spend. Cost is compute and ClickHouse query load.
- Volume at full scale (about 1,000,000 items a day, 30.5M a month): the upper bound of daily purge work at steady state follows the monthly shares: YouTube 3.0M a month is about 100,000 text purges a day; news 0.375M articles a month is about 12,500 full-text purges a day; LinkedIn 0.15M a month is about 5,000 a day; the share of amber data on the 24-month clock and the share of `meta_on_request` data leaving through offboarding are to be measured in the pilot.
- Ten-year horizon: aggregates and derived scores are never selected, so ClickHouse `aggregates_hourly` grows for ten years; sizing belongs to aggregator.
- Storage of audit records is small; their growth is to be measured in the pilot and they are kept for the life of the contract, to be confirmed with counsel.

## 8. Failure handling and fallback

- Postgres or ClickHouse unavailable: the sweep stops, raises `sweep_missed` after two periods, and the next sweep recomputes; nothing is marked done without a verification result.
- Redpanda produce failure: the chunk is retried; `deletion_id` determinism makes a repeat harmless; after 5 attempts with backoff from 30 s to 15 min the chunk goes to `dlq.retention-purger` and an alert fires.
- yt-text-purger silent: no confirmation within a sweep period raises `delegate_unresponsive`; the verification still runs and fails if text is past 30 days.
- Deletion-propagator slow: `x_deadline_at_risk` fires when an open X deletion passes a warning age (value to be set in the pilot) and `clock_breach` at 24 hours.
- Verification fails: audit `fail`, `clock_breach`, the same ids are re-emitted at the next sweep.
- No amber fallback exists; `fallback_on` is never set here.

## 9. Non-functional requirements

- Throughput: a sweep for one class completes inside its sweep period at full scale; to be measured in the pilot.
- Latency: any record is requested for deletion before its deadline; X deletions complete within 24 hours of `signal_at`.
- Idempotency: deterministic `deletion_id`; a repeated sweep is a no-op.
- Scaling: one leader sweeps; ClickHouse queries are partition-pruned; workers for offboarding and author requests scale on `deletion_requests` depth.
- Security: no text, handles or tokens in logs or messages; `AUTHOR_HASH_KEY` and client secrets only from Supabase Vault; audit table append-only with no delete role; access limited to ops and the compliance owner.

## 10. Metrics and alerts

`records_past_clock{class}`, `oldest_past_clock_age_seconds{class}`, `deletions_emitted_total{reason}`, `deletions_open{reason}`, `sweep_duration_seconds`, `audit_status{class}`, `delegation_pending`, `requests_open{reason}`, `dlq_total`. Alerts: `clock_breach`, `x_deadline_at_risk`, `sweep_missed`, `delegate_unresponsive`, `request_sla_at_risk`, `audit_failed`, `dlq_nonempty`. SLO: zero breaches; DLQ reviewed daily.

## 11. Dependencies

listening-sdk (`item_id`, `author_hash`), Redpanda, Supabase Postgres and Vault, ClickHouse, deletion-propagator, x-compliance-sync, yt-text-purger, registry-writer, raw-archiver, aggregator, alert-evaluator, n8n for the deletion channel.

## 12. Risks and mitigations

- A wrong clock deletes data a contract allows us to keep, or keeps what we must delete: the clock table lives in `retention_classes`, changes are reviewed by the compliance owner, and every change is audited.
- A deletion that reaches ClickHouse but not archives or caches: the verification step checks all three, not only the store.
- An author request for someone else's data: identity checks are open (section 14); no handle is stored after hashing.
- Clients dispute offboarding scope: the audit lists counts per source and class.

## 13. Acceptance criteria

1. With fixture rows of each class aged past, inside and just outside their clock, one sweep emits `deletions` for exactly the past-due rows with the reason and mode of the table in 5.3.
2. Running the same sweep twice emits identical `deletion_id`s and deletion-propagator acts once.
3. For `x_24h_sync`, a deletion with `signal_at` T that stays open raises `x_deadline_at_risk` before T + 24 h and `clock_breach` at T + 24 h; a completed one passes.
4. The `youtube_30d_text` sweep puts one job on `jobs.yt-text-purger`; if text older than 30 days remains afterwards, the audit is `fail` and `clock_breach` fires.
5. LinkedIn member post data older than 48 hours and member profile data older than 24 hours are selected; organization data is not selected before its terms allow.
6. A client moved to `offboarding` produces a `remove_client` decision for every `client_sources` row, `deletions` with reason `client_offboarding`, revoked tokens, and a closed audit record; an item also watched by a second client survives with the first client's id removed.
7. An author request produces `deletions` with `author_hash` and no handle in any message, log or row; the audit passes within the fixture's 7-day window.
8. No sweep ever selects an `aggregates_hourly` row or a derived score, and the audit says so.
9. A killed leader mid-sweep is replaced by another replica with no duplicate emissions.
10. Every run, pass or fail, writes exactly one `retention_audit` row that includes the verification query and its result.

## 14. Open questions

1. Who verifies the identity of an author who files a request? Proposed: a confirmation sent to the platform account's public contact, to be agreed with counsel.
2. Completed author requests should block re-ingestion: proposed a check in normalize-item against `deletion_requests` hashes; not in its approved PRD yet.
3. Retention class for Telegram bot content and for web-search results beyond `news_excerpt`: to be set with counsel.
4. Grace period for the `meta_on_request` necessity clock, and how long audit records are kept: to be agreed with counsel.
