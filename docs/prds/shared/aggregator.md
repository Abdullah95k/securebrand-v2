# aggregator

**Platform:** Shared · **Route:** shared · **Lane:** Processing · **Owner:** Data engineer (ClickHouse) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Clients do not read items; they read numbers: mentions of their brand per hour, how many were negative, how far they reached, what people engaged with. Ten years of those numbers must stay available, while identifiable items are purged by each platform's rules after days or months. Scanning items for every dashboard would be slow and would stop working the day the items expire.

aggregator turns hits, items, analysis rows and metrics into hourly, daily and monthly rollups in ClickHouse and keeps them correct: late sentiment scores, refreshed engagement counts, retracted hits, deleted items and replays all change the numbers after the fact.

Without it dashboards would query raw rows, history would vanish with the raw data, alert-evaluator would have no baseline to compare against, and nobody would own the question "why does this hour differ from yesterday's report".

## 2. Objective (the end state this service delivers)

End state: for every client, keyword, source, platform, sentiment and topic, `aggregates_hourly` holds the current mentions, reach and engagement of each hour, `aggregates_daily` and `aggregates_monthly` are exact sums of it, and all three survive for ten years whatever happens to the underlying items.

Measurable target: open hours refreshed every minute by default and never staler than three cycles at full scale (about 1,000,000 items a day, about 12 a second, peaks to be measured in the pilot); zero unexplained differences between the hourly table and the active hits in the last 31 days at each hourly reconciliation; every row retained ten years.

## 3. Scope

### In scope
- Hourly rollups through materialized views into `aggregates_hourly`; daily and monthly rollups; lagged recomputes; recomputation of affected hours after reprocessing, retractions and deletions; reconciliation; the freeze rule for expired classes; the update watermark for alert-evaluator.

### Out of scope
- Writing base tables (store-writer); matching (keyword-matcher); inference (analysis-sentiment, analysis-topics); alert rules (alert-evaluator); purging and deleting items (retention-purger, deletion-propagator); the dashboards' queries.

## 4. Users and consumers

- alert-evaluator evaluates its rules each time the aggregator's watermark moves; the client app reads the three tables and their `_v` views.
- Account managers and Abdullah read trend and share-of-voice reports built on them.
- Ops run `recompute` jobs after a replay or a fix.

## 5. How it works

### 5.1 Trigger and rotation

Time-driven, with three event inputs. Every `AGG_CYCLE_SECONDS` (default 60) the open hours (the current hour and the two before it, `AGG_OPEN_HOURS`) are rebuilt. Each hour is rebuilt again at fixed lags after it closes, matching the refresh policy: +1 h, +6 h, +24 h (after the +24 h metrics), +8 d (after the +7 d metrics) and +31 d (after the comment series ends). Every `AGG_RECONCILE_MINUTES` (default 60) a reconciliation compares the last 31 days of active hits with the hourly table and rebuilds mismatching hours. Events: a message on `deletions` (consumer group `aggregator`) triggers a reconciliation within 5 minutes; a `source.events` retirement or `client_ids` change triggers one for that source; a job on `jobs.aggregator` with `kind = recompute` (date range, optional client) is the ops entry point. One active instance, chosen by a Postgres advisory lock; ClickHouse does the work. Ordering does not matter: every pass is a full rebuild of its hours.

Replay: a model or rule change re-runs the backlog from the raw archive through raw-archiver's replay path; store-writer upserts the new rows; the aggregator then rebuilds the affected hours, automatically inside the 31-day window and by an ops `recompute` job beyond it.

### 5.2 Step by step

1. Pick the hours for this pass (open hours, due lags, mismatches, job range).
2. Skip frozen (hour, class) pairs (5.3 E).
3. Build the hour's rows with the rollup statement (5.3 A to C) into a staging select.
4. Compare with the existing rows of the hour (`FINAL`); groups that existed but no longer do are rewritten as zero rows.
5. Insert everything with `version = now()` as epoch seconds; older rows collapse at merge.
6. For each rebuilt hour, rebuild its day, then its month, from the level below.
7. Record the pass in `service_runs` (`last_success_at`, hours touched) so alert-evaluator sees the update.

### 5.3 The call it makes (the processing it performs)

**A. Inputs, all from store-writer's tables (read with `FINAL` or `argMax`).** `hits` where `status = 'active'` and `hit_at` in the hour (`hit_at` is the item's `created_at`), inner-joined to `items` or `comments` by `item_id` (a hit whose item is gone does not count); the latest `analysis` row per item and model; the latest `metrics_timeseries` observation per item, else the counts on the item row; `sources_dim` for followers.

**B. Grain.** `(hour, client_id, keyword_id, platform, source_id, sentiment, topic_id, retention_class)`. `source_id` is the poster's `author_source_id`; individuals roll up under the nil UUID, so no per-person row exists. `sentiment` takes the labels of analysis-sentiment plus `pending` (not analysed yet) and `unscored` (language not covered). `topic_id` comes from analysis-topics; an item with several topics counts once per topic (topic rows add up to more than the total), and `unassigned` stands for none yet.

**C. Measures.** `mentions` = distinct items; `reach` = followers of the posting source summed over its mentions (gross reach; individuals count 0; followers as of the rebuild); `engagement` = likes + comments + shares of the latest counts; `views`. Shares are not stored: the negative share of a keyword is negative mentions divided by positive, neutral and negative mentions (`pending` and `unscored` left out), computed at read time.

**D. Rebuild semantics.** `aggregates_hourly` is `ReplacingMergeTree(version)`, partitioned by month, sorted by `client_id, keyword_id, hour, platform, source_id, sentiment, topic_id, retention_class`, with `TTL hour + INTERVAL 10 YEAR`. A rebuild replaces rows by key and writes zero rows for vanished groups, so an hour is a pure function of the base tables, repeating it changes nothing, and a `pending` row becomes zero when its sentiment arrives. The open-hour pass is a refreshable materialized view (`mv_aggregates_hourly`, `REFRESH EVERY 1 MINUTE APPEND`); lagged, reconciliation and ad-hoc passes run the same statement from the service. If the deployed ClickHouse lacks refreshable views, `AGG_MV_MODE = service` runs the open pass from the timer; results are identical. `aggregates_daily` and `aggregates_monthly` have the same keys without the hour (day, month) and are sums of the level below, also with a ten-year TTL; the `_v` views hide superseded versions.

**E. Freeze rule.** A pair (hour, class) is not rebuilt once `hour_end + row_ttl(class)` (from `retention_classes`) has passed, because its base rows are gone and a rebuild would erase real history. In practice `linkedin_48h` hours freeze at 48 hours; the others rebuild through the +31 d pass. Counts of a frozen hour are never reduced by a later deletion.

**F. Reconciliation.** Every hour: per hour of the last 31 days, compare `count()` of active hits (frozen classes excluded) with `sum(mentions)` from `aggregates_hourly_v`; any difference marks the hour for rebuild. This catches deletions, retractions, rematches and replays without coupling to those services.

### 5.4 What it gets

Hits, items, comments, analysis rows, metric observations and source dimensions as stored by store-writer. It does not get item text, author identity or any per-person key; and it does not see hours that store-writer has not yet flushed, so a result is current to the last flush plus one cycle.

## 6. Inputs and outputs

### 6.1 Reads
- ClickHouse: `hits`, `items`, `comments`, `analysis`, `metrics_timeseries`, `sources_dim`, `keywords_dim`, `aggregates_*`.
- Topics: `deletions`, `source.events`, `jobs.aggregator`.
- Control plane: `retention_classes` (`row_ttl`), `cursors`, `service_runs`.

### 6.2 Writes
`aggregates_hourly`, `aggregates_daily`, `aggregates_monthly`; `service_runs`; `cursors` (recompute progress); `dlq.aggregator` for unreadable jobs.

```json
{
  "hour": "2026-10-06 08:00:00",
  "client_id": "e2a9d0b1-6c7f-4a38-9d5e-0f1a2b3c4d5e",
  "keyword_id": "9a8b7c6d-5e4f-4321-a0b9-c8d7e6f5a4b3",
  "platform": "facebook",
  "source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566",
  "sentiment": "negative",
  "topic_id": "tp_0042",
  "retention_class": "meta_on_request",
  "mentions": 3, "reach": 750000, "engagement": 412, "views": 0,
  "version": 1791278400
}
```

Three posts by a source with 250,000 followers, all negative, on one topic. The daily and monthly rows have `day` or `month` in place of `hour`.

### 6.3 State
Hours scheduled and done, kept in `cursors` (`service = aggregator`, `cursor = recompute:<job_id>:<last hour>`); the lag schedule is computed from the clock, so a restart loses nothing. The leader lock. No other state.

## 7. Limits, quotas and cost

No external API or vendor: no `budget_tag`. Cost is ClickHouse CPU and memory for the rebuild statements, on servers at Hetzner (USD price confirmed at order time). Per pass the work is the hits of three open hours: about 42,000 items an hour at the average rate, times hits per item (to be measured in the pilot). Scheduled lags add five rebuilds per hour of history and the reconciliation scans 31 days of hits once an hour; both are bounded and their durations are to be measured in the pilot. Rows kept for ten years: hourly rows are at most the number of hits, so the table grows by up to about 1,000,000 times hits per item rows a day; the daily and monthly tables answer long ranges. Growth in rows and bytes is to be measured in the pilot.

## 8. Failure handling and fallback

- A pass fails or exceeds its cycle: it is abandoned; the next cycle starts with the current hour first; `agg_staleness_seconds` grows and alerts. Passes are idempotent, so retries are safe.
- ClickHouse down: nothing is written; the watermark stops; alert-evaluator marks its evaluation `stale` rather than alerting on old data.
- Source dimension missing for a poster: reach counts 0 until the row arrives; the next rebuild corrects it.
- Analysis missing: mentions count under `pending`.
- Partial insert visible for seconds: hours are inserted per statement and replace by key; readers may see old and new groups together briefly.
- Refreshable views unavailable or failing: `AGG_MV_MODE = service` takes over.
- Hours older than the reconciliation window: only an ops `recompute` job changes them; a single old deletion changes a count by one and is not scanned for.
- Poison job (bad range): `dlq.aggregator` with an alert.

## 9. Non-functional requirements

- Throughput: hits arrive at about 12 items a second at full scale; rebuild cost depends on hits per item (to be measured in the pilot).
- Latency: the chain is normalize within 60 s of fetch, matching within 60 s of normalization, analysis within 15 min for tier-1 sources, alerts within 5 min of the aggregate update. This service defines the aggregate update: open hours refresh every `AGG_CYCLE_SECONDS` plus rebuild time.
- Idempotency: every pass is a pure function of the base tables; reruns change values by nothing and `version` by one.
- Scaling: one active instance; scaling is ClickHouse capacity; the open window can be split by `client_id` range if a pass exceeds its cycle.
- Security: no item text read; no per-person grain; TLS to ClickHouse; read access to base tables, write access to `aggregates_*` only. Node (TypeScript) issuing versioned SQL files from the repository.

## 10. Metrics and alerts

Prometheus: `agg_cycle_seconds`, `agg_staleness_seconds`, `agg_rows_written_total{table}`, `agg_rebuild_hours_total{reason}`, `agg_zero_rows_total`, `agg_reconcile_mismatch_hours`, `agg_frozen_skips_total`, `agg_query_seconds`, `dlq_total`. Alerts: staleness above three cycles; a pass longer than its cycle for 10 minutes; `agg_reconcile_mismatch_hours` above zero in two consecutive reconciliations; DLQ non-empty.

## 11. Dependencies

store-writer (all base tables and dimensions); ClickHouse; Supabase Postgres (`retention_classes`, `service_runs`, `cursors`, advisory lock); `deletions` (deletion-propagator), `source.events` (registry-writer); keyword-matcher and the analysis services as upstream producers; alert-evaluator as consumer; raw-archiver (replay).

## 12. Risks and mitigations

- Rebuild cost grows with hits per item: hour-sized statements, open window only, measured in the pilot, split by client range if needed.
- A rebuild erasing history after raw rows expire: the freeze rule and an acceptance test.
- Topic fan-out misread as a total: documented in `_v` view comments and the client app; totals use the topic-free query.
- Followers drift (reach uses followers at rebuild time): accepted for v1; see 14.
- Hourly table size over ten years: daily and monthly tables for long ranges; growth measured in the pilot.
- Reconciliation blind to old hours: ops `recompute` after any large replay.

## 13. Acceptance criteria

1. A fixture set of hits, items, analysis rows, metrics and sources produces exactly the golden `aggregates_hourly` rows, including topic fan-out, the nil `source_id` for individuals and zero reach for individuals.
2. Running one hour's rebuild three times leaves identical values under `FINAL`.
3. An item counted under `pending` moves to its real sentiment at the next cycle after its analysis row arrives, the `pending` row becomes a zero row, and total mentions are unchanged.
4. A hit set to `retracted` lowers mentions at the next cycle, and the vanished group is a zero row.
5. After deletion-propagator removes an item, the hour's mentions drop by one within 5 minutes of the `deletions` message.
6. A `linkedin_48h` hour older than 48 hours is not rebuilt: its row survives after the base rows are deleted; a `youtube_30d_text` hour still rebuilds at +8 d.
7. Rebuilding an old hour updates its day and month; each daily row equals the sum of its hourly rows and each monthly row the sum of its days.
8. At the synthetic 50 items a second of normalize-item's test, `agg_staleness_seconds` stays below three cycles, and an alert-evaluator run follows each watermark move.
9. Deleting hits rows directly is detected by the next reconciliation and corrected; `agg_reconcile_mismatch_hours` returns to zero.
10. `SHOW CREATE TABLE` for the three tables shows a ten-year TTL; deleting every base row of a frozen hour changes no aggregate.
11. No aggregate row carries `author_ref`, a handle or any per-person key.
12. An ops `recompute` job over a date range rebuilds those hours and cascades to days and months, with progress in `cursors`.

## 14. Open questions

1. Does the chosen ClickHouse release run refreshable materialized views in production? If not, `AGG_MV_MODE = service` is the default.
2. Reach: gross followers of the posting source as of the rebuild, or frozen at first sight? Frozen values need a stored column on `hits`.
3. Do clients need posts and comments separated in the hourly grain? The draft keeps one `mentions` count.
4. Retention of the hourly grain at ten years versus hourly for a shorter period with daily and monthly for the rest; row growth is to be measured in the pilot.
5. Sentiment labels and topic ids: names follow `items.analysis/v1`; confirm against analysis-sentiment and analysis-topics.
