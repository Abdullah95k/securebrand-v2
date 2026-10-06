# raw-archiver

**Platform:** Shared · **Route:** shared · **Lane:** Support · **Owner:** Data platform engineer, storage and replay · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Every service that fetches something from a platform or a vendor pays for it: in API quota, in vendor spend, or in crawl time. raw-archiver keeps one faithful copy of every response so that this payment is made once. When we change the schema, fix a mapper in normalize-item or swap a language or sentiment model, we replay what we already hold instead of fetching again. Re-fetching is often impossible anyway: posts get deleted, Facebook's ranked feed returns only about 600 posts per Page per year, X's recent search reaches back 7 days, and a vendor charges again for every request.

Without it the product loses four things. It loses replay: every parser bug becomes a data loss. It loses provenance: a client who asks "where did this mention come from" has no original record to show. It loses a cheap long-term store: ClickHouse holds normalized rows, not what the platform actually said. And it loses a single place where retention rules are enforced on raw data, which is where most identifiable content sits.

## 2. Objective (the end state this service delivers)

Every message on `raw.items` is stored, exactly as produced, in a checksummed zstd JSONL batch under its `raw_ref`; each closed day is compacted to Parquet; media sits once per content hash; any slice of the archive can be replayed on demand; and lifecycle rules remove data when its retention class says so. Target: zero lost records (the per-batch count equals the topic offsets, checked every night), every `raw_ref` resolvable to its record, archive lag (newest message on `raw.items` minus newest archived) within the flush time limit, and every replay run completing with a published count equal to its planned count.

## 3. Scope

### In scope

- Consuming `raw.items` and writing JSONL.zst batches plus a manifest per batch.
- Nightly compaction per platform and day into Parquet under `archive/<platform>/<yyyy>/<mm>/`.
- Media storage by content hash under `media/<sha256>`, with a reference list per hash.
- The replay API and the replay topic `raw.replay`.
- Integrity checks (offsets against counts, checksums, `raw_ref` spot reads) and lifecycle rules per retention class.
- Rewriting an archive partition when deletion-propagator asks.

### Out of scope

- Deciding what to delete and when: retention-purger decides, deletion-propagator performs the deletions in ClickHouse and caches.
- Parsing or deduplicating payloads (normalize-item), ClickHouse writes (store-writer), downloading media (analysis-media and the fetch services; this service only stores what they hand over).
- Aggregates: aggregator and ClickHouse hold the ten-year history, not this archive.

## 4. Users and consumers

- **Ops** trigger replays after a schema or model change, read integrity reports, and see archive lag.
- **normalize-item** reads archived records on replay (`raw.replay`); its `raw_ref` pointers resolve here.
- **Analysis services** (analysis-sentiment, analysis-topics, analysis-media, analysis-entities) take part in model-version replays.
- **retention-purger and deletion-propagator** call the lifecycle and rewrite functions.
- **Abdullah and account managers** rely on the provenance this archive makes provable.

## 5. How it works

### 5.1 Trigger and rotation

Four triggers. (1) Continuous: a consumer group `raw-archiver` on `raw.items`, one replica per partition set, scaling on partition lag. (2) Nightly compaction: a leader-elected loop (Postgres advisory lock) starts, for each platform, the compaction of the previous UTC day once a grace period has passed (`RAW_COMPACT_GRACE_H`, to be set in the pilot, so late batches are in). (3) Nightly reconciliation and lifecycle check, after compaction. (4) On demand: the replay API, the media endpoint and the rewrite endpoint.

Flush rules for open batches: a batch is written when its buffered bytes reach `RAW_BATCH_MAX_BYTES`, when its age reaches `RAW_BATCH_MAX_AGE_S`, or on graceful shutdown. Initial values are to be measured in the pilot.

### 5.2 Step by step

1. Poll a batch of messages from a `raw.items` partition. Read `envelope.raw_ref` (`<object key>#<line>`, as listed in normalize-item).
2. Append the whole message (envelope plus payload, unchanged) to the open buffer for that object key; remember its topic offset.
3. When a flush rule fires, compress with zstd, upload the object, upload `<batch>.manifest.json`, then commit the consumer offsets. Nothing is committed before both uploads succeed.
4. Nightly, per platform and day: verify manifests, compact (5.3), verify the Parquet, and only then mark the day's raw batches eligible for their lifecycle clock.
5. Reconcile: compare topic offsets with the union of manifest ranges per partition and day; read back a sample of `raw_ref` values.
6. Serve replay, media and rewrite requests; write one audit line per request into `service_runs`.

### 5.3 The call it makes

This service calls no platform. It runs the following logic.

**Batch assembly.** The SDK's raw emit helper allocates each message's `raw_ref`. A key is allocated per producer replica, per partition of `raw.items` and per retention class, so all lines of one key arrive in order on one partition and a batch never mixes classes. The helper rolls to a new key when its own size or age limit is reached or after an idle period, always below the archiver's limits, so a key is not reused after the archiver has flushed it. The archiver writes lines in line order; a gap in line numbers before flush is held until the idle limit, then written as is and reported.

**Late line.** A message for an already uploaded key goes to a supplement object `<batch>.s<n>.jsonl.zst`, listed in the manifest; `raw_ref` resolution consults the manifest. Counted in `archiver_late_lines_total`.

**Manifest.** `key`, `route`, `platform`, `service`, `retention_class`, `partition`, `offset_ranges`, `lines`, `bytes_uncompressed`, `sha256` of the compressed object, `first_fetched_at`, `last_fetched_at`, `written_at`, `supplements[]`.

**Compaction.** For platform P and UTC day D: list manifests of all routes and services; stream each batch; write two Parquet files per output part, joined by `raw_ref`: an `envelope` file (flattened envelope fields, `item_id`, `content_hash` of the payload, `raw_ref`) and a `payload` file (the payload as a JSON string column). Sorted by `item_id`, so row-group statistics serve item-id lookups. News is the exception: the payload file keeps only title, excerpt (200 to 300 characters), canonical URL, dates, language and hashes, never the full text. Classes with a clock of 48 hours or less (`linkedin_48h`) are not compacted: the raw batch is the archive and expires with the class. Verify: row count equals the sum of manifest `lines`, and a sample of rows equals their source lines byte for byte. A failed verification keeps the raw batches, raises `compaction_failed` and retries the next night.

**Media.** `PUT` on the media endpoint takes bytes plus `item_id`, `retention_class`, `expires_at`. The archiver hashes the bytes with SHA-256, writes `media/<sha256>` if absent, and appends the reference to `media/<sha256>.refs`. A media object is deleted when its last reference is removed or expired.

**Replay.** `POST /v1/replays` takes `platform`, optional `service`, optional `route`, `from` and `to` (UTC dates), optional `item_ids`, `target` (`normalize-item`, `analysis` or `all`), `reason`, `rate_cap_per_s`, `dry_run`. It plans the objects from manifests and Parquet statistics, returns `run_id` and the planned counts, and on confirmation publishes each record to `raw.replay` with the original envelope plus a `replay` block. It skips records of items with a pending or in-progress row in `deletion_requests`, and never reads data past its class clock. `GET /v1/replays/{run_id}` returns progress; `POST /v1/replays/{run_id}/cancel` stops it. Access is ops-only through Supabase auth; every call is logged with the caller.

**Lifecycle by class.** Rules are set per prefix on the bucket from `retention_classes` and verified nightly; where a prefix can hold several classes the strictest clock applies, and retention-purger handles per-record clocks.

| Class | Raw batch and payload file | Envelope file |
|---|---|---|
| `x_24h_sync` | No time expiry; removed by deletions | Kept with the item |
| `youtube_30d_text` | Expires 30 days after `fetched_at` (yt-text-purger is the authority) | Kept, no text |
| `linkedin_48h` | Expires 48 hours after `fetched_at` (profile data 24 hours) | Expires with it |
| `meta_on_request` | No time expiry; removed on request or offboarding | Kept with the item |
| `vendor_agreed` | 24 months by default, or the vendor contract | Same |
| `news_excerpt` | Full-text batches expire after 7 days; excerpt Parquet kept | Kept |

### 5.4 What it gets

Messages of `raw.items`: the envelope (`platform`, `kind`, `route`, `vendor`, `service`, `source_id`, `platform_id`, `idempotency_key`, `job_id`, `fetched_at`, `retention_class`, `client_ids`, `raw_ref`, and the Facebook services' `batch`) and the payload, as produced. It does not get anything parsed, no author identity beyond what the payload holds, and never platform credentials: the SDK strips tokens before emission.

## 6. Inputs and outputs

### 6.1 Reads

`raw.items`; the control-plane tables `retention_classes`, `deletion_requests`, `clients` (for offboarding scope); `source.events`; object storage (its own batches, for compaction, replay and rewrite).

### 6.2 Writes

Objects: `raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst`, the manifest beside it, `archive/<platform>/<yyyy>/<mm>/<dd>-<part>.envelope.parquet` and `.payload.parquet`, `media/<sha256>` and `.refs`. Topic `raw.replay`, partitioned by `source_id`, one message per record:

```json
{
  "envelope": {
    "platform": "facebook", "kind": "post", "route": "green", "vendor": null,
    "service": "fb-page-feed-poller",
    "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
    "platform_id": "100064583471102_1198837625012734",
    "idempotency_key": "facebook:post:100064583471102_1198837625012734",
    "fetched_at": "2026-10-06T09:15:42Z",
    "retention_class": "meta_on_request",
    "raw_ref": "raw/green/facebook/2026/10/06/fb-page-feed-poller/000123.jsonl.zst#17"
  },
  "payload": { "...": "the original post object, unchanged" },
  "replay": {
    "run_id": "01J9P4K2M8E5T7C0Q1W3X6YZAB", "target": "normalize-item",
    "reason": "normalizer_version 14 to 15", "requested_by": "ops", "planned": 48210, "seq": 17
  }
}
```

Also `service_runs`, `dlq.raw-archiver` for batches that fail five attempts.

### 6.3 State

Consumer offsets; open buffers in memory only (rebuilt from uncommitted offsets); manifests and `.refs` objects in storage; replay progress in `cursors` keyed `service = raw-archiver`, `cursor = replay:<run_id>:<last raw_ref>`; the compaction ledger as one marker object per platform and day.

## 7. Limits, quotas and cost

- Volume at full scale: about 1,000,000 items a day (30.5M a month), roughly 12 messages a second on average; the peak factor is to be measured in the pilot. Facebook is 12.0M of the monthly total, TikTok 7.5M, Instagram 4.5M, YouTube 3.0M, Telegram 2.4M, X 0.6M, LinkedIn 0.15M, news 0.375M.
- Storage: raw bytes a day, compression ratio and Parquet size are to be measured in the pilot. Growth is bounded by the class clocks (30 days, 48 hours, 7 days, 24 months by default); only `x_24h_sync` and `meta_on_request` data grows until deleted, and media grows with unique content. At ten years the envelope-only Parquet covers 9 platforms by 120 months, about 1,080 month prefixes; their bytes are to be measured.
- Prices are to be confirmed with the chosen object store (Backblaze B2 or Hetzner Object Storage), including egress and request charges for replays.
- Compute: stateless Node (TypeScript) workers for streaming; compaction runs as a nightly job per platform and day (Parquet writer in Node); CPU and memory to be measured in the pilot.
- A replay is rate-capped and runs in its own consumer groups so it cannot starve live traffic.

## 8. Failure handling and fallback

- Object store errors: retry with exponential backoff and jitter from 30 s to 15 min; after 5 attempts the batch goes to `dlq.raw-archiver` and an alert fires. Offsets are not committed past a batch that is not stored.
- Redpanda produce failure on replay: the run pauses at the last published `raw_ref` and resumes from the cursor.
- Partial upload: the manifest is written last; an object without a manifest is treated as incomplete and rewritten from the uncommitted offsets.
- Schema change: payloads are never parsed here, so a new shape is archived unchanged.
- Checksum mismatch: quarantine the object under `raw/_quarantine/`, rebuild from `raw.items` if still in topic retention, else alert and record the loss.
- Compaction failure: keep the raw batches and retry the next night.
- No amber fallback exists; `fallback_on` is never set here.

## 9. Non-functional requirements

- Throughput: sustain full-scale ingest plus a rate-capped replay at the same time; figures to be measured in the pilot.
- Latency: an item is readable by `raw_ref` within the flush time limit of its arrival.
- Idempotency: the key and line number are deterministic, so reprocessing a partition rewrites identical objects; replays carry `run_id` and `seq`, and consumers deduplicate on `item_id`.
- Scaling: archiver replicas on partition lag; compaction one job per platform and day.
- Security: encryption at rest and in transit; write-only credentials for the archiver, read credentials for replay and compaction; payloads never logged; tokens never present in payloads.
- Compliance: provenance retained for the client-facing statement; no object outlives its class clock.

## 10. Metrics and alerts

`archive_lag_seconds`, `batches_written_total`, `bytes_written_total`, `archiver_late_lines_total`, `compaction_duration_seconds`, `compaction_rows_total`, `integrity_failures_total`, `replay_records_published_total`, `overdue_objects_total`, `dlq_total`. Alerts: `archive_lag_high`, `archive_gap` (offsets without a manifest), `compaction_failed`, `integrity_failed`, `lifecycle_overdue`, `dlq_nonempty`. SLO: zero lost records; DLQ reviewed daily.

## 11. Dependencies

listening-sdk (`raw_ref` allocation and envelope), Redpanda, object storage (Backblaze B2 or Hetzner Object Storage), Supabase Postgres, normalize-item, the analysis services, retention-purger, deletion-propagator, store-writer, source-health-canary.

## 12. Risks and mitigations

- Raw data holds identifiable content that must be removed on schedule: lifecycle rules by prefix, a nightly check and retention-purger as the authority; the envelope and payload are split so text can go while identifiers stay.
- A replay resurrects a deleted item: replays skip items with open deletion requests and deletion-propagator rewrites partitions; the ReplacingMergeTree tombstone version outranks replayed content.
- The object store lifecycle feature differs between B2 and Hetzner: tested on the chosen store before launch; the nightly check is the backstop.
- A producer allocates `raw_ref` wrongly: the reconciliation job reports keys without lines and lines without keys.

## 13. Acceptance criteria

1. A fixture of 10,000 messages across 5 services produces batches whose manifests list `lines` equal to the messages produced, and the offset ranges cover the partition range exactly.
2. Killing the archiver after the upload but before the offset commit, then restarting, writes an identical object (same checksum) and no duplicate line.
3. Every `raw_ref` in the fixture resolves to the original message byte for byte.
4. A message for an already uploaded key lands in a supplement object and `archiver_late_lines_total` increases by one.
5. Compaction of a fixture day yields a row count equal to the sum of manifest lines; deliberately corrupting one Parquet row makes verification fail, keeps the raw batches and raises `compaction_failed`.
6. News payloads in Parquet contain the excerpt and no full text; a raw news batch older than 7 days is gone.
7. Uploading the same media bytes twice produces one `media/<sha256>` object and two references; removing one reference keeps the object, removing both deletes it.
8. A replay by platform, service and date range publishes exactly the planned count to `raw.replay`, honours `rate_cap_per_s`, and skips an item with an in-progress deletion request.
9. A `linkedin_48h` batch is absent from storage 48 hours after `fetched_at` and is never compacted.
10. A flipped byte in a stored batch is detected by the nightly checksum check, the object is quarantined and `integrity_failed` fires.

## 14. Open questions

1. Batch number width: normalize-item's examples show four digits, fb-page-feed-poller six. Proposed: six, a constant in `listening-sdk`.
2. normalize-item reads `raw/` directly on a `replay` job. Proposed: `raw.replay` is the main path, with a manifest-only mode for direct readers; confirm which one ships first.
3. How long may envelope-only Parquet outlive the text clock for `youtube_30d_text` and `meta_on_request`? To be confirmed with counsel.
4. Redpanda topic retention for `raw.items`, needed for gap repair: to be set after the pilot.
