# store-writer

**Platform:** Shared · **Route:** shared · **Lane:** Processing · **Owner:** Data engineer (ClickHouse) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Everything the product shows a client (a mention list, a sentiment share, an alert) is a query on ClickHouse. Something must put the pipeline's output there: items and comments from `items.normalized`, model outputs from `items.analysis`, engagement counts from `item.metrics`, keyword hits from `item.hits` and `discovery.hits`, and the dimension tables the dashboards join to. ClickHouse wants few large inserts, while the pipeline produces about 12 items a second.

store-writer is the single writer of the analytics store. It batches, makes every write an upsert so replays and redeliveries cannot duplicate a row, stamps each row with the expiry its retention class requires, and keeps deleted items from coming back.

Without it each consumer would write its own way: duplicate rows after every replay, no common retention rules (YouTube text must go after 30 days, LinkedIn member data after 48 hours), and too many small inserts for ClickHouse to survive.

## 2. Objective (the end state this service delivers)

End state: every record on the six input topics is in ClickHouse exactly once in effect (the latest version of its key wins), visible within seconds of publication, with its expiry columns set.

Measurable target: zero lost records (offsets commit only after the insert is acknowledged); after any replay `SELECT count() ... FINAL` equals the number of distinct keys; p95 publish-to-visible latency below three flush intervals (15 s at the defaults); 100% of rows carry `row_expires_at`, and every row of a time-bound class carries the right `content_expires_at`.

## 3. Scope

### In scope
- Consuming `items.normalized`, `items.analysis`, `item.metrics`, `item.hits`, `discovery.hits`, `source.events`; writing `items`, `comments`, `analysis`, `metrics_timeseries`, `hits`, `sources_dim`, `keywords_dim`.
- Batching and flush rules; version columns and upserts; monthly partitions; the Arabic text index; expiry columns and masked views; the resurrection guard; dimension sync.

### Out of scope
- Rollups (aggregator); purging and deletions (retention-purger, deletion-propagator); matching (keyword-matcher); inference (analysis-sentiment, analysis-topics, analysis-media, analysis-entities); raw archiving (raw-archiver).

## 4. Users and consumers

- aggregator builds `aggregates_hourly` from the tables written here; alert-evaluator reads `hits`, `items` and `aggregates_hourly`.
- The client app and account managers query `items`, `comments`, `hits` and the masked views.
- normalize-item and keyword-matcher run point lookups on `items`, `comments` and `hits`; deletion-propagator and retention-purger delete by the same keys.
- Ops watch lag and DLQ and run replays.

## 5. How it works

### 5.1 Trigger and rotation

Trigger: topics `items.normalized`, `items.analysis`, `item.metrics`, `item.hits`, `discovery.hits` and `source.events`, one consumer group `store-writer`. Partitions follow `source_id` (ADR-0004), so one worker handles one source in order; there is no ordering between topics, so an analysis row can arrive before its item, which is harmless because the tables are independent. Offsets commit only after every table in the batch is acknowledged by ClickHouse. A timer drives dimension sync: `keywords` and `clients` are polled every `DIM_POLL_SECONDS` (default 30); `sources_dim` follows `source.events`.

Replay: a model, mapper or rule change re-runs the backlog from the raw archive through raw-archiver's replay path (normalize-item republishes, the analysis services re-score, keyword-matcher re-matches). The messages reach this service under consumer group `store-writer-replay-<version>`, rate-capped, and write the same keys with a newer `row_version`, so the old rows are replaced, not duplicated.

### 5.2 Step by step

1. Collect rows per table until `STORE_BATCH_ROWS` (default 5,000) or `STORE_FLUSH_MS` (default 5,000) passes, whichever comes first; defaults to be tuned in the pilot.
2. Check each message's `schema`; an unknown version is parked in `dlq.store-writer`, never guessed.
3. Route: `kind` of `comment` or `reply` goes to `comments`, everything else to `items`.
4. Stamp `row_version`, `row_expires_at`, `content_expires_at` (5.3); drop the `candidate` block from hits; project analysis fields.
5. Resurrection guard: drop rows whose `item_id` is in `deletion_requests` with status done.
6. Insert per table with ClickHouse async inserts and `wait_for_async_insert = 1`; retry with backoff.
7. Commit offsets when all inserts of the batch are acknowledged.

### 5.3 The call it makes (the processing it performs)

**Tables.** All are `ReplacingMergeTree`, partitioned by month.

| Table | Version column | Sorting key | Partition | Source |
|---|---|---|---|---|
| `items` | `row_version` | `item_id` | `toYYYYMM(created_at)` | `items.normalized`, posts, videos, articles, messages, quotes, results |
| `comments` | `row_version` | `item_id` | `toYYYYMM(created_at)` | `items.normalized`, `kind` comment or reply; `parent_id` bloom index |
| `analysis` | `analyzed_at` (ms) | `item_id, model` | `toYYYYMM(analyzed_at)` | `items.analysis`; a newer model version replaces the older |
| `metrics_timeseries` | `observed_at` | `item_id, observed_at` | `toYYYYMM(observed_at)` | `item.metrics` |
| `hits` | `row_version` | `client_id, keyword_id, item_id` | `toYYYYMM(hit_at)` | `item.hits`, `discovery.hits`; `status` active or retracted |
| `sources_dim` | `updated_at` | `source_id` | none | `source.events`, reading the current `sources` row |
| `keywords_dim` | `updated_at` | `keyword_id` | none | `keywords` and `clients`, polled |

The sorting key is the identity key, because ReplacingMergeTree collapses on it. `item_id` never changes, and `created_at` never changes between versions of an item, so every version lands in one partition. `row_version = (version << 32) | produced_at` (epoch seconds): a higher item version always wins, and for equal versions the later production (a replay with a new model) wins, whatever the arrival order. `analysis` carries `model`, `model_version`, the `output` JSON and typed projections of the fields aggregator needs (names as in `items.analysis/v1`: sentiment label and score, topic ids, entity ids). `metrics_timeseries` holds likes, comments, shares, views and reactions by type per observation. `items` and `comments` keep every field of `items.normalized/v1` under the same name, plus `likes`, `comments_count`, `shares`, `views` projected from `metrics_snapshot` and the raw `metrics_snapshot` as JSON; `display_name` is not stored per item, it joins from `sources_dim`.

**Text index.** On `text_norm`: `tokenbf_v1` for token search and `ngrambf_v1` for substring search, parameters tuned in the pilot. Search terms must be folded with lang-dialect-id `/v1/fold` before they are queried.

**Expiry.** ClickHouse TTL expressions cannot be NULL, so a class without a content expiry gets the sentinel `2106-01-01 00:00:00`. `content_expires_at` is the message's `expires_at`. Column TTL on `text`, `title`, `text_norm`, `url`, `platform_id`, `author_ref`, `media`, `hashtags`, `at_mentions`, `links` and `metrics_snapshot` blanks them at `content_expires_at`; table TTL deletes the row at `row_expires_at`, read from `retention_classes` (columns `content_ttl`, `row_ttl`, proposed here).

| Class | Content blanked | Row deleted |
|---|---|---|
| `x_24h_sync` | never by time (deletion-propagator mirrors X deletions within 24 h) | created + 10 years |
| `youtube_30d_text` | 30 days | created + 36 months |
| `linkedin_48h` | 48 hours | 48 hours, with its `analysis` rows |
| `meta_on_request` | never by time (deletion on Meta's request, offboarding, user request) | created + 10 years |
| `vendor_agreed` | 24 months by default | created + 10 years |
| `news_excerpt` | never (excerpt and metadata kept) | created + 10 years |

`analysis`, `metrics_timeseries` and `hits` rows take `retention_class` from the message, else from the item row, and follow the item's `row_expires_at`. TTL runs at merge time, so two controls make it exact: queries use the views `items_v` and `comments_v`, which return empty content where `content_expires_at` is past, and retention-purger issues exact deletes at expiry. Aggregates are not touched here: ten years.

**Dimensions.** On each `source.events` batch (up to 500 ids) the current `sources` rows are read and upserted into `sources_dim`; a full resync runs at start-up and nightly. `keywords_dim` is rebuilt from changed `keywords` and `clients` rows.

### 5.4 What it gets

Messages in the schemas of the six topics. It does not get raw payloads, media files or author identity beyond the hash: the `candidate` block of a `discovery.hits` message (platform id, handle) is never written. Orphan comments (`parent_seen = false`) are stored as they are; the link is `parent_id`, derived from the post's key, so nothing is rewritten when the post arrives.

## 6. Inputs and outputs

### 6.1 Reads
- Topics: the six above.
- Control plane: `retention_classes`, `deletion_requests`, `sources`, `keywords`, `clients`, `service_runs`.

### 6.2 Writes
ClickHouse tables of 5.3, `dlq.store-writer`, a `service_runs` row. Example `items` row for the post of normalize-item's 6.2 (`JSONEachRow`):

```json
{
  "item_id": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f",
  "idempotency_key": "facebook:post:1234567890_9876543210",
  "platform": "facebook", "kind": "post",
  "source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566",
  "parent_id": null, "root_id": null, "parent_seen": 1,
  "created_at": "2026-10-06 08:51:40.000", "fetched_at": "2026-10-06 09:13:58.000",
  "text": "النت منقطع بالبصرة من الصبح، شنو السالفة؟",
  "text_norm": "النت منقطع بالبصره من الصبح شنو السالفه",
  "lang": "ar", "lang_conf": 0.98, "dialect": "iraqi", "dialect_conf": 0.84, "script": "arab",
  "author_ref": "hmac:9c1f…", "author_type": "source",
  "author_source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566",
  "likes": 120, "comments_count": 14, "shares": 3, "views": null,
  "route": "green", "vendor": null, "service": "fb-page-feed-poller",
  "retention_class": "meta_on_request",
  "content_expires_at": "2106-01-01 00:00:00", "row_expires_at": "2036-10-06 08:51:40",
  "content_hash": "sha256:4b2e…", "version": 1, "row_version": 6086245339,
  "normalizer_version": "1.4.0", "lang_model_version": "lid-iq-2026.09",
  "raw_ref": "raw/green/facebook/2026/10/06/fb-page-feed-poller/0007.jsonl.zst#1532"
}
```

`url`, `platform_id`, `media`, `hashtags`, `at_mentions`, `links`, `title`, `metrics_snapshot` and `dialect_scores`-free versions of the remaining fields follow `items.normalized/v1` and are omitted here for length.

### 6.3 State
Consumer offsets; per-table in-memory batches; the dimension sync marks (`updated_at` seen, last `source.events` offset); replay progress in `cursors` (`service = store-writer`).

## 7. Limits, quotas and cost

No external API or vendor is called: no `budget_tag`. Cost is ClickHouse (open-source server, self-hosted on Hetzner) plus two small replicas of this service. Row rates at full scale from the CONVENTIONS volumes: 1,000,000 `items` and `comments` rows a day (about 12 a second), at most about 4,000,000 `analysis` rows (four models), about 3,000,000 `metrics_timeseries` rows (first sight, +24 h, +7 d), and `hits` rows per item to be measured in the pilot. At the default flush that is about one insert a second across all tables. Bytes per row, disk per month and ClickHouse sizing are to be measured in the pilot; the ten-year horizon applies to aggregates and derived scores, while content is purged by class. Hetzner pricing in USD is confirmed at order time.

## 8. Failure handling and fallback

- ClickHouse down or slow: nothing is committed; consumers pause and lag grows; on recovery the backlog drains at the maximum rate. An alert fires at 60 s of lag, well inside Redpanda's days of retention.
- `TOO_MANY_PARTS` or merge pressure: the flush interval doubles automatically until inserts succeed; an alert fires.
- Unknown `schema` version or a row that fails typing: parked in `dlq.store-writer` with the message; an alert; the rest of the batch proceeds.
- Duplicates (redelivery, replay): collapse at merge; reads use `FINAL` or the views; the aggregator's live path uses distinct-count states.
- Resurrection: a late message for a deleted item is dropped by the guard and counted. If `deletion_requests` is unreachable, inserts pause rather than risk restoring deleted content.
- Dimension lag: dashboards show the previous dimension row until the sync catches up.

## 9. Non-functional requirements

- Throughput: the average rows in 7 are well below ClickHouse's capacity; catch-up and replay must sustain at least 212 records a second (live 12 plus normalize-item's replay cap of 200); peaks to be measured in the pilot.
- Latency: the chain is normalize within 60 s of fetch, matching within 60 s of normalization, analysis within 15 min for tier-1 sources, alerts within 5 min of the aggregate update. This service adds at most one flush interval plus insert time between publication and visibility.
- Idempotency: `row_version` is deterministic, so redelivery and replay produce the same final row; arrival order does not matter.
- Scaling: one consumer group, stateless; replicas scale on partition lag.
- Security: no item text in logs; TLS to ClickHouse and Redpanda; credentials from Supabase Vault; a write-only ClickHouse user. Node (TypeScript); row builders and the version formula in `listening-sdk`.

## 10. Metrics and alerts

Prometheus: `rows_in_total{table}`, `rows_written_total{table}`, `batches_total{table,status}`, `batch_rows`, `flush_latency_seconds`, `publish_to_visible_seconds`, `consumer_lag_seconds{topic}`, `insert_errors_total{table,code}`, `dropped_total{reason}`, `dim_sync_age_seconds`, `dlq_total`. Alerts: lag above 60 s for 5 minutes; any `TOO_MANY_PARTS`; DLQ non-empty; insert error rate above zero for 10 minutes; `dim_sync_age_seconds` above three poll intervals; rows past `content_expires_at` still holding content in a table (checked hourly).

## 11. Dependencies

Redpanda; ClickHouse; Supabase Postgres (`retention_classes`, `deletion_requests`, `sources`, `keywords`, `clients`, `service_runs`, Vault); `listening-sdk`; producers normalize-item, analysis-sentiment, analysis-topics, analysis-media, analysis-entities, keyword-matcher, registry-writer; consumers aggregator, alert-evaluator; deletion-propagator, retention-purger, raw-archiver (replay).

## 12. Risks and mitigations

- Too many small parts: batch rules, async inserts, monthly partitions, automatic back-off.
- An item whose `created_at` changes between versions would sit in two partitions and never collapse: mapper fixtures assert stable `created_at`; a daily check counts cross-partition duplicates.
- Expired content served before TTL merges: masked views plus exact deletes by retention-purger.
- Replays starve live traffic: separate consumer group and rate cap.
- Arabic text index weak on substring and clitic forms: bloom parameters tuned in the pilot; keyword-matcher, not the index, decides matches.
- A single ClickHouse node is a single point of failure: replication and backup are an infrastructure decision (see 14).

## 13. Acceptance criteria

1. The seven tables exist with the engine, version column, sorting key and partition of 5.3; a post lands in `items`, a comment and a reply in `comments`.
2. The same `items.normalized` batch inserted twice leaves one row per `item_id` after `OPTIMIZE FINAL`, and `count() ... FINAL` is unchanged; the same holds for `hits` and `metrics_timeseries`.
3. Item version 2 inserted before version 1 still wins; a replay of version 1 with a later `produced_at` and a new `lang_model_version` replaces the earlier row.
4. A `youtube_30d_text` fixture gets `content_expires_at` 30 days after fetch and `row_expires_at` 36 months after creation; `items_v` returns empty text for it once 30 days pass, counts intact; a `linkedin_48h` fixture and its `analysis` rows are deleted at 48 hours; an `x_24h_sync` fixture carries the sentinel.
5. A token query and a substring query on Arabic `text_norm` return the fixture rows, and `EXPLAIN` shows the skip indexes used.
6. At a synthetic 200 rows a second for 10 minutes no table reaches the parts limit and p95 publish-to-visible latency stays below three flush intervals.
7. With ClickHouse stopped for 3 minutes mid-run, no record is lost, offsets stay uncommitted during the outage, and lag returns below 60 s after recovery.
8. A message for an `item_id` listed in `deletion_requests` (done) is dropped and counted in `dropped_total{reason="tombstoned"}`.
9. A `discovery.hits` fixture leaves no `candidate`, platform id or handle in `hits`, in logs or in the DLQ.
10. A `source.events` tier change updates `sources_dim` within 60 s; a changed `keywords` row updates `keywords_dim` within two poll intervals.
11. A message with an unknown `schema` version lands in `dlq.store-writer`, the rest of the batch is written, and an alert fires.

## 14. Open questions

1. CONVENTIONS lists no `hits` table; this PRD adds it, assumes store-writer also owns `keywords_dim`, and adds `content_ttl` and `row_ttl` to `retention_classes`. Confirm all three.
2. Topology: one ClickHouse node, or a replicated pair with backups on Hetzner Object Storage or Backblaze?
3. May per-item `analysis` rows from LinkedIn member data outlive 48 hours (derived scores are kept ten years elsewhere)? The draft deletes them.
4. Horizon for item-level `metrics_timeseries`: ten years, or shorter with hourly aggregates carrying the long history? Bytes per row decide; to be measured in the pilot.
5. Does `item.metrics` carry `retention_class`, `created_at` and `source_id`? The draft reads them from `items` when absent.
