# deletion-propagator

**Platform:** Shared · **Route:** shared · **Lane:** Support · **Owner:** Backend lead, compliance and retention · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A deletion that is only recorded is not a deletion. One post sits in several places at once: the ClickHouse tables `items`, `comments`, `analysis` and `metrics_timeseries`, the raw JSONL batches and the Parquet archive, a media object, the text index, caches, the hourly aggregates it was counted in, and the copies our clients already hold. If any one of them keeps it, we have kept it. deletion-propagator is the service that takes one `deletions` message and removes the item from every place, in the right order, within a deadline, and then proves it.

Without it, the work of retention-purger (which decides what is due) and x-compliance-sync (which learns what X says is gone) would stop at a message. X could end our access for missing its 24-hour rule. An author who asked to be forgotten would still appear in a client report. A client who left would still have its Meta data on our disks. Aggregates would keep counting posts that no longer exist, and clients would never be told their copies are stale.

## 2. Objective (the end state this service delivers)

Every `deletions` message is applied to every store that holds the target, aggregates are recomputed without it, affected clients are notified, and an audit record with verification query results shows the item is gone, all by the deadline carried in the message. Targets: 24 hours from the compliance signal for X; 7 days for author requests; 30 days for client offboarding (the last two to be confirmed with counsel). Reasons `retention`, non-X `platform_sync` and `legal` complete by the `due_at` the emitter sets. Zero deletions lost.

## 3. Scope

### In scope

- Consuming `deletions` (reasons `platform_sync`, `retention`, `author_request`, `client_offboarding`, `legal`) and resolving each message to item ids.
- ClickHouse tombstones (ReplacingMergeTree versions with `is_deleted`), lightweight deletes, and forced merges of affected partitions.
- Rewriting the affected raw and Parquet archive partitions through raw-archiver; removing media references.
- Purging caches and the text index.
- Recomputing affected aggregates through aggregator.
- Client webhook notices; one audit record per deletion with verification results.

### Out of scope

- Deciding what is due (retention-purger), watching X compliance (x-compliance-sync), refreshing YouTube text (yt-text-purger).
- Object lifecycle by age (raw-archiver) and TTL rules in ClickHouse (generated from `retention_classes`).
- Deleting aggregates or derived scores for their own sake: kept ten years; they change only through a recompute.

## 4. Users and consumers

- **Clients** receive deletion webhooks and, via their account manager, evidence.
- **Authors** are served indirectly through the deletion channel handled by retention-purger.
- **Ops and the compliance owner** watch deadlines, re-drive failed steps and read audit records.
- **Downstream services**: raw-archiver (rewrites), aggregator (recompute jobs), store-writer (must honour tombstones), normalize-item, alert-evaluator, retention-purger (reads completion).

## 5. How it works

### 5.1 Trigger and rotation

A continuous consumer of `deletions`, consumer group `deletion-propagator`. Messages are scheduled by `due_at`, earliest first, in two worker pools: an urgent pool (`platform_sync`, `legal`) and a bulk pool (`retention`, `author_request`, `client_offboarding`), so a large retention purge never sits in front of an X deletion. A reconciliation loop (leader-elected through a Postgres advisory lock, period an environment variable) re-drives any `deletion_requests` row that is open and idle, and re-verifies completed deletions after the next ClickHouse merge cycle and after any raw-archiver compaction of an affected day. A coalescing window (`DELETION_BATCH_WINDOW`, to be measured in the pilot) groups bulk deletions that touch the same archive object; it never applies to a message whose remaining time to `due_at` is short.

### 5.2 Step by step

1. Consume a message; upsert a `deletion_requests` row keyed by `deletion_id` (status `received`). A repeat of a completed id is acknowledged and dropped.
2. Resolve the target to `item_id`s and read each item's `client_ids`, `source_id`, `raw_ref`, media hashes and timestamps (status `resolved`).
3. Make the data invisible: ClickHouse tombstones, then the text index.
4. Erase physically: ClickHouse deletes and merges, archive rewrites, media references, caches.
5. Recompute aggregates (mode `delete` only).
6. Notify clients by webhook.
7. Run the verification queries, write the audit record, set the status `completed`, and record whether `completed_at` met `due_at`.
8. Commit the Redpanda offset only after step 1 has been stored; later steps resume from the stored status after a crash.

### 5.3 The call it makes

This service calls no platform. It runs the following logic.

**Resolve.** `scope = item`: use `target.item_ids`, or derive `item_id` from `<platform>:<kind>:<platform_id>` with the SDK helper that normalize-item uses. A deleted post cascades to its comments (`parent_id`), except on X, where replies are posts of their own and leave only on their own signal. `scope = author`: select by `author_hash` in `items` and `comments`. `scope = source`: all items of the `source_id`. `scope = client`: items whose `client_ids` contain only that client are deleted; for items shared with another client, a new version removes this client's id. A target that is not found is a success with `found = 0`, and the tombstone is still written (see below).

**ClickHouse.** (a) Insert tombstone rows into `items` and `comments` with `is_deleted = 1` and a version greater than any content version (deletion time). Tombstones have no TTL and are permanent, so a late `raw.items` record or a `raw.replay` of the same `item_id` cannot bring the item back: store-writer drops upserts for an id that has a tombstone. (b) `DELETE FROM` the item rows, and for `delete` mode also `analysis` and `metrics_timeseries` rows. (c) For `purge_text`, insert a new version with `text`, `text_norm`, `author_hash` and `url` emptied and keep `analysis`, `metrics_timeseries` and aggregates. (d) Force a merge of each affected monthly partition and check `system.mutations` shows no pending mutation, so removal is physical and does not wait for background merges.

**Archives.** Group item ids by object using `raw_ref` (or raw-archiver's item-id lookup when absent). For each object call raw-archiver's rewrite endpoint (`POST /v1/rewrites`) with the ids and the mode: it writes a new object without those lines (or with the payload emptied for `purge_text`), writes a new manifest, and deletes the earlier object version explicitly, because versioned buckets keep old versions (behaviour to be confirmed on the chosen store). The same applies to the Parquet `envelope` and `payload` files. Raw records that were parked by `schema_unknown` and never became items are found by platform id.

**Media.** For each media hash of the deleted items, call raw-archiver's media endpoint to remove the reference; the object is deleted when the last reference goes.

**Caches and text index.** Delete by `item_id` in every store registered in the purge registry in `listening-sdk` (today the text index and the 7-day news full-text cache). A store that holds text and is not in the registry is a defect.

**Aggregates.** For `delete`, collect the distinct (`source_id`, hour) buckets and keyword ids of the removed items and send `recompute` jobs to `jobs.aggregator`; wait for `done`. For `purge_text`, no recompute: counts do not change.

**Webhooks.** For each client in the deleted items' `client_ids`, post `deletion.completed` to the client's registered webhook: HMAC-signed, containing the item references the client knows, the reason category and the time, never text or author data; retries with backoff from 30 s to 15 min and up to 5 attempts. Erasure does not wait for a client's endpoint: a failed notice is recorded as `notice_status = undelivered`.

**Verification.** After the steps: ClickHouse count of the ids in `items`, `comments`, `analysis`, `metrics_timeseries` equals 0 (or, for `purge_text`, the text columns are empty); no pending mutation on the partitions; rewritten objects contain no line with those ids; media references gone; text-index query for the ids returns 0 hits; aggregator job `done`. The results are stored with the audit record.

**State machine.** `received → resolved → hidden → erased → recomputed → notified → verified → completed`; each transition is stored, so every step is repeatable.

### 5.4 What it gets

A `deletions` message. Required for any producer: `reason`, `scope`, a target (`platform`, `kind` and `platform_id` or `item_ids`, or `author_hash`, `source_id` or `client_id`). Optional: `deletion_id` (derived deterministically if absent), `mode` (default `delete`), `retention_class`, `signal_at` (default arrival time), `due_at` (default from the reason), `requested_by`, `run_id`. It does not get text; it learns what exists only from ClickHouse and the archives, and it never reads content except to verify absence.

## 6. Inputs and outputs

### 6.1 Reads

`deletions`; ClickHouse `items`, `comments`, `analysis`, `metrics_timeseries`; Postgres `deletion_requests`, `clients` (webhook endpoint and secret reference, from Supabase Vault); raw-archiver manifests; aggregator job status.

### 6.2 Writes

ClickHouse tombstones, deletes and text-less versions; archive rewrites and media removals (through raw-archiver); `jobs.aggregator` recompute jobs; client webhooks; Postgres `deletion_requests` (status, verification, notice status, `sla_met`), `service_runs`; `dlq.deletion-propagator`. The audit record, stored in `deletion_requests.verification`:

```json
{
  "deletion_id": "del:platform_sync:item:3b9d5f1a7c2e4086b1d3f5a7c9e0b2d4f6a8c0e1b3d5f7a9c1e3b5d7f9a0c2e",
  "reason": "platform_sync", "retention_class": "x_24h_sync", "mode": "delete",
  "signal_at": "2026-10-06T08:00:00Z", "due_at": "2026-10-07T08:00:00Z",
  "completed_at": "2026-10-06T09:41:07Z", "sla_met": true,
  "items_resolved": 1, "found": 1,
  "verification": [
    {"query": "SELECT count() FROM items FINAL WHERE item_id IN (...) AND is_deleted = 0", "result": 0},
    {"query": "SELECT count() FROM system.mutations WHERE table IN ('items','comments') AND is_done = 0", "result": 0},
    {"check": "archive_rewrite", "objects": 2, "lines_with_ids": 0},
    {"check": "text_index", "hits": 0},
    {"check": "aggregator_job", "status": "done"}
  ],
  "notices": [{"client_id": "0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60", "notice_status": "delivered"}]
}
```

### 6.3 State

`deletion_requests` rows with status and step; consumer offsets; permanent tombstones in ClickHouse; the leader lock; nothing else in memory.

## 7. Limits, quotas and cost

- No external API and no vendor cost. The cost is ClickHouse merge load, object store reads and writes for rewrites, and recompute work in aggregator.
- Throughput at full scale (about 1,000,000 items a day): the volume of `deletions` is bounded by retention-purger's clocks (for example YouTube 3.0M a month is about 100,000 text purges a day) plus platform deletions (to be measured in the pilot). Rewrite cost depends on the number of archive objects touched, not items, which is why bulk deletions are coalesced.
- Ten-year horizon: `aggregates_hourly` holds up to 87,600 hourly buckets per series over ten years; a deletion of old content recomputes only the buckets its items fell in, never the history.
- Storage: tombstones are small and permanent, growth to be measured in the pilot; `deletion_requests` audit rows are kept for the life of the contract, to be confirmed with counsel.
- Object store request, egress and rewrite charges: to be confirmed with the chosen object store (Backblaze B2 or Hetzner Object Storage).

## 8. Failure handling and fallback

- ClickHouse, object store or aggregator unavailable: the step retries with exponential backoff and jitter from 30 s to 15 min; after 5 attempts the deletion goes to `dlq.deletion-propagator` with its status intact and an alert fires; it is never dropped and never marked complete.
- Archive step blocked: the item is already invisible (tombstone and index); `sla_at_risk` fires on the remaining time to `due_at`.
- Webhook failure: recorded as undelivered with `webhook_undelivered`; erasure still completes.
- Verification fails: status stays `erased`, `verification_failed` fires, the failed check is retried by the reconciliation loop.
- Unknown shape in a message: stored in `deletion_requests` as `rejected` with the reason, and alerted; a deletion is never silently ignored.
- Crash mid-step: resumes from the stored status; all steps are idempotent.
- No amber fallback exists; `fallback_on` is never set here.

## 9. Non-functional requirements

- Throughput: keep pace with the daily volume of retention and platform deletions plus bursts from an offboarding; figures to be measured in the pilot.
- Latency: an item is invisible to clients within the time of step 3 (to be measured in the pilot), and physically gone before `due_at`.
- Idempotency: `deletion_id` is the unit; a repeat changes nothing and sends no second webhook.
- Scaling: workers scale on `deletions` lag and on open `deletion_requests` ordered by `due_at`; one leader reconciler.
- Security: no text, handles or tokens in logs; webhook secrets from Supabase Vault; the verification role on ClickHouse is read-only, the deletion role is separate; every call is audited.

## 10. Metrics and alerts

`deletions_consumed_total{reason}`, `deletions_completed_total{reason}`, `deletion_open_age_seconds{reason}`, `sla_breach_total{reason}`, `step_duration_seconds{step}`, `archive_objects_rewritten_total`, `webhook_failures_total`, `verification_failed_total`, `mutations_pending`, `dlq_total`. Alerts: `sla_at_risk`, `sla_breach`, `verification_failed`, `webhook_undelivered`, `mutation_backlog`, `dlq_nonempty`. SLO: every deletion completed before `due_at`; DLQ reviewed daily.

## 11. Dependencies

listening-sdk (`item_id` derivation, purge registry), Redpanda, ClickHouse, raw-archiver, aggregator, store-writer, normalize-item, retention-purger, x-compliance-sync, yt-text-purger, alert-evaluator, Supabase Postgres and Vault, object storage.

## 12. Risks and mitigations

- A deletion is applied in ClickHouse but not in an archive or cache: the verification covers every store and the status cannot reach `completed` without it.
- Resurrection through replay or a late fetch: permanent tombstones, store-writer's tombstone rule, and raw-archiver's replay skip for open deletions.
- Backups and snapshots hold deleted data: see section 14.
- A bulk offboarding overloads ClickHouse merges: the bulk pool is rate-capped and the urgent pool is separate.

## 13. Acceptance criteria

1. A fixture item present in ClickHouse, a raw batch, a Parquet part, the text index and an hourly aggregate is removed by one `platform_sync` message; every verification query returns zero and the affected aggregate equals a recompute without the item.
2. With ClickHouse blocked in the fixture, an X deletion with `signal_at` T raises `sla_at_risk` before T + 24 h and `sla_breach` at T + 24 h, and the message is still in `deletion_requests`, not lost.
3. Processing the same `deletion_id` twice, or crashing after each step and resuming, gives the same end state, one audit record and one webhook per client.
4. A `raw.replay` record and a late `raw.items` record for a deleted `item_id` do not create a row in `items`.
5. In `purge_text` mode the text, `text_norm`, `author_hash` and `url` are empty, `analysis`, `metrics_timeseries` and aggregates are unchanged, and no pending mutation remains.
6. After an archive rewrite, the new raw and Parquet objects hold no line with the id, the manifest carries the new checksum, and no earlier version of the object remains.
7. A media object referenced by two items survives the first deletion and is gone after the second.
8. An author-scope deletion removes the author's items and comments on two platforms from every store, completes within the fixture's 7-day window, and its webhooks carry item references but no author data.
9. A client-scope deletion removes items held only for that client, keeps shared items with the other client's id, and recomputes the affected aggregates.
10. With a webhook endpoint failing all attempts, erasure still completes, `notice_status` is `undelivered` and `webhook_undelivered` fires.
11. With 100,000 queued `retention` deletions, a newly arrived X deletion starts first.

## 14. Open questions

1. Backups and snapshots of ClickHouse and Postgres are not described in CONVENTIONS; any backup that holds deleted data must expire inside the shortest deadline or be excluded. To be decided with counsel.
2. The producers of `platform_sync` deletions (fb-reactions-fetcher and the comment fetchers) must emit the minimum shape of 5.4; their PRDs and store-writer's tombstone rule need to be aligned.
3. An author request that matches a registered source needs a registry decision; no producer for it is listed in registry-writer. Proposed: retention-purger emits it.
4. Author-scope messages are keyed by `author_hash`, not `source_id`; the topic note in CONVENTIONS needs that exception.
5. Cost and duration of forced merges and archive rewrites at full scale: to be measured in the pilot.
6. SLAs for non-X `platform_sync` and for `legal`: to be set with counsel.
