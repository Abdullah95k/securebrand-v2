# analysis-topics

**Platform:** Shared · **Route:** shared · **Lane:** Processing · **Owner:** ML lead (analysis) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Sentiment says how people feel; topics say what they are talking about. A telecom client needs to know that this week's negative mood is about an outage in Basra, not about pricing; a ministry needs to see which of its services draw complaints. Without topics every mention is one undifferentiated pile, and the product cannot say why a number moved.

Topics also catch what nobody thought to look for. Iraqi conversation moves fast: a new tariff, a new rumour, a local service failure. A fixed list of categories misses it for weeks. So the service does two jobs: it sorts every item into the client's own categories, and it finds new themes that fit none of them and puts them in front of a person each week.

The product promise is insight "in a way no one has seen before" for the Iraqi market. That depends on reading Iraqi dialect well enough to tell "النت ضعيف" (the internet is weak, a service-quality complaint) from "النت مقطوع" (the internet is cut, an outage). Without this service the product counts mentions; with it, it explains them.

## 2. Objective (the end state this service delivers)

End state: every item with text carries multi-label topic scores against its client's taxonomy (and the global default one) and one intent label, stamped with `model_version`; new themes appear in a weekly review queue within a day of emerging; a client can add a topic and see it applied the same day.

Measurable target:
- 100% of consumed items accounted for (classified, skipped with reason or dead-lettered).
- p95 `fetched_at` to publish below 15 minutes for tier-1 sources at full scale (about 1,000,000 items a day, about 12 a second on average).
- Accuracy on the in-house Iraqi evaluation set (per-topic and macro F1, intent macro-F1, zero-shot F1 on held-out topics, share of weekly clusters accepted by reviewers): to be set after the baseline is measured in the pilot. Protocol in 5.3: gold set stratified by platform and dialect, double-annotated, a leave-topics-out test for the zero-shot path.

## 3. Scope

### In scope
- Multi-label topic classification over a client-configurable taxonomy; the global default taxonomy (service quality, pricing, outage, customer support, product launch, corporate news and others) applied to every item.
- Single-label intent (complaint, question, praise, request, announcement, other).
- Zero-shot fallback for topics without enough labelled examples.
- Emerging-topic clustering with a weekly human review; taxonomy validation; labelling loop, evaluation, registry, re-runs.

### Out of scope
- Sentiment (analysis-sentiment), entities (analysis-entities), media (analysis-media), language detection (lang-dialect-id), keyword matching (keyword-matcher).
- Any topic describing a person's attributes; taxonomy validation rejects them (5.3).
- Storage, aggregation, alerts (store-writer, aggregator, alert-evaluator).

## 4. Users and consumers

- store-writer persists rows; aggregator builds topic volumes and topic-by-sentiment views; alert-evaluator reads topic spikes ("outage mentions up").
- Account managers and clients edit taxonomies through the control plane; the weekly reviewer (account manager plus ML lead) accepts, merges or discards cluster candidates; annotators label.

## 5. How it works

### 5.1 Trigger and rotation

Trigger: `items.normalized`, consumer group `analysis-topics`; no polling. Clustering is a scheduled batch job (daily) reading the ClickHouse `analysis` and `items` tables.

Priority: same two-lane pattern as analysis-sentiment. Intake resolves the tier of `source_id` (or `author.author_source_id`) from the registry cache fed by `source.events` and writes to `jobs.analysis-topics.priority` (tier 1) or `jobs.analysis-topics`; target analysis within 15 minutes of `fetched_at` for tier 1. The global taxonomy runs on every item; a client taxonomy runs only on items relevant to that client (a hit, or a source in `client_sources`).

Batching: micro-batches by token length; sizes set in the pilot.

Re-run policy: every output is stamped with `model_version`, which includes the taxonomy version (`topics-iq-2026.11.tx7`). A new model or taxonomy version re-runs the backlog: a job on `jobs.analysis-topics` with `kind = rerun` reads normalized items from raw-archiver's Parquet archive (`archive/<platform>/<yyyy>/<mm>/`), newest first, skips items no longer in ClickHouse `items`, and publishes `run_kind = rerun` rows under group `analysis-topics-rerun-<model_version>`, rate-capped, beside the old rows until switch-over. A client adding a topic re-runs only that client's window.

### 5.2 Step by step

1. Pull a batch; skip items already done for the same `content_hash` and `model_version`; assign a lane.
2. Build the input: `title` plus `text`; skip empty text (`status = skipped`, `reason = no_text`) and unsupported languages.
3. Embed once with the shared encoder; run the supervised head for each applicable taxonomy.
4. For taxonomy nodes with `status = zero_shot`, score the item against the node's description and examples.
5. Apply per-node thresholds; keep nodes above threshold, always the top node.
6. Classify intent.
7. Publish one `items.analysis` message per item per taxonomy (`task = topics:<taxonomy_id>`); commit after the ack.
8. Daily clustering: collect items whose best topic score is below threshold, plus items in fast-growing clusters; cluster; write candidates to `review_queue`.
9. Sample for labelling.

### 5.3 The call it makes (the processing it performs)

**Model choice.** A shared Arabic encoder (CAMeLBERT-DA or MARBERTv2, the same bake-off as analysis-sentiment) with a sigmoid multi-label head per taxonomy version and a softmax intent head, fine-tuned on the in-house Iraqi set. Sorani needs its own encoder route or a multilingual fallback, decided in the pilot. The zero-shot path uses a multilingual sentence encoder (for example LaBSE or multilingual-e5; chosen in the pilot) comparing the item with each node's description and examples, or an NLI model; choice by held-out F1.

**Taxonomy.** Control-plane table `taxonomy_nodes` (proposed): `taxonomy_id` (global or a client), `node_id`, labels in Arabic, Sorani and English, description, examples, `status` (zero_shot, supervised, retired), `taxonomy_version`. A new node starts `zero_shot` and becomes `supervised` once enough labelled examples exist (count set in the pilot), which creates a new `model_version`. Validation rejects any node that infers a protected attribute of an individual (religion, ethnicity, political affiliation, health) or monitors sensitive events (protests, rallies); such nodes are never evaluated on X data or in government taxonomies.

**Pre-processing.** As analysis-sentiment (URLs masked, mentions removed, emoji kept, elongation collapsed), shared module versioned `preproc_version`; the author reference never reaches a model.

**Thresholds and outputs.** Per-node thresholds chosen on the validation split per version and stored in `model_versions.thresholds`; zero-shot nodes use a stricter threshold set until promoted. Output: `topics[]` with `node_id`, `score`, `source` (supervised or zero_shot); `top_topic`; `intent` with `label` and `score`; `low_confidence` when no node passes.

**Emerging-topic clustering.** Embeddings of unassigned or fast-growing items are reduced and clustered (UMAP and HDBSCAN, or an equivalent chosen in the pilot); clusters are labelled with distinctive terms and matched to yesterday's clusters by centroid so ids stay stable. A candidate carries size, growth, distinct sources and ten representative `item_id`s, never author references. Clusters whose terms match a sensitive-event or protected-attribute lexicon are flagged and suppressed for X data. The weekly reviewer accepts (becoming a `zero_shot` node, global or client), merges or discards; accept rates are tracked. Cluster membership is published as `task = topic_cluster`.

**Human labelling loop.** `review_queue` rows (`kind = annotation:topics`) feed the same self-hosted annotation tool as analysis-sentiment: low-confidence items, zero-shot hits for review, items no node covers, and a random sample per stratum. Labelled text follows the item's retention class (purged with the item; label kept).

**Evaluation.** Frozen gold set stratified by platform and dialect, double-annotated; per-node precision, recall and F1, macro-F1, intent macro-F1, calibration; a leave-topics-out run treats supervised nodes as new to measure zero-shot quality; cluster purity on a labelled sample. Promotion gate as analysis-sentiment: no stratum below tolerance, shadow run, ML lead sign-off.

**Registry and serving.** `model_versions` (proposed) with artefacts under `models/topics/<model_version>/`. Python workers on a Hetzner GPU pool or a model API from a screened vendor; the choice per task (supervised head, zero-shot, clustering) is open.

### 5.4 What it gets

`title`, `text`, `lang`, `dialect`, `script`, `kind`, `retention_class`, source tier. Not the author's identity, not media content, not the thread context. Topics in images and video appear only if analysis-media text is added later (question 5).

## 6. Inputs and outputs

### 6.1 Reads
- Topics: `items.normalized`, `source.events`, `jobs.analysis-topics` and `.priority`.
- Control plane: `taxonomy_nodes`, `model_versions`, `sources`, `client_sources`, `retention_classes`, `review_queue`; ClickHouse `items`, `analysis`; object storage `archive/`, `models/topics/`.

### 6.2 Writes
`items.analysis` (partitioned by `source_id`; logical key `item_id` + `task` + `model_version`), `review_queue` (cluster candidates, annotation tasks), `dlq.analysis-topics`.

```json
{
  "schema": "items.analysis/v1",
  "message_id": "01J9W4Z8H5K2M6N7P8Q9R0S1T2",
  "produced_at": "2026-10-06T09:15:15Z",
  "producer": {"service": "analysis-topics", "version": "0.2.0", "job_id": "analysis-topics:priority:0011"},
  "analysis_key": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f:topics:global:topics-iq-2026.11.tx7",
  "item_id": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f", "item_version": 1,
  "content_hash": "sha256:4b2e…", "input_hash": "sha256:c03d…",
  "platform": "facebook", "kind": "post", "source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566",
  "task": "topics:global", "model_version": "topics-iq-2026.11.tx7", "taxonomy_version": 7,
  "run_kind": "live", "lane": "priority", "status": "ok",
  "lang": "ar", "dialect": "iraqi", "item_fetched_at": "2026-10-06T09:13:58Z",
  "route": "green", "vendor": null, "retention_class": "meta_on_request", "expires_at": null,
  "result": {
    "topics": [
      {"node_id": "outage", "score": 0.93, "source": "supervised"},
      {"node_id": "customer_support", "score": 0.41, "source": "supervised"}
    ],
    "top_topic": "outage",
    "intent": {"label": "question", "score": 0.72},
    "low_confidence": false
  }
}
```

### 6.3 State
Consumer offsets; the LRU of done keys; registry and taxonomy caches (by `taxonomy_version`); centroid table of yesterday's clusters; re-run progress in `cursors` (`service = analysis-topics`, `cursor = rerun:<model_version>:<last archive object key>`); `service_runs`.

## 7. Limits, quotas and cost

No platform API is called. Cost is the GPU pool, the daily clustering job and reviewer time. The global taxonomy runs on every item (about 1,000,000 a day, about 12 a second); client taxonomies run only on client-relevant items, whose share is to be measured in the pilot. The encoder runs once per item and is shared by all heads. GPU hours, per-item cost in USD and peaks are to be measured in the pilot; Hetzner pricing is confirmed at order time. A re-run of 12 months at target volume is about 366 million items (30.5 million a month times 12), so re-runs use a separate burst allocation; a client taxonomy change re-runs only that client's items. A model API would need a `budget_tag` `analysis_model_api` (new) and a quota-governor allowance.

## 8. Failure handling and fallback

- Model server down: backoff with jitter from 30 s to 15 min; after 5 attempts to `dlq.analysis-topics` with an alert; no default topic is ever published.
- Taxonomy cache stale or a taxonomy fails validation: the last valid version keeps serving and an alert fires.
- Zero-shot encoder down: zero-shot nodes are skipped (`zero_shot_unavailable = true`), supervised nodes continue.
- Clustering failure: the previous day's candidates stay; an alert fires; no partial candidates are written.
- Poison item after 5 attempts: dead-lettered by `item_id`, never with text.

## 9. Non-functional requirements

- Throughput: about 12 items a second average at full scale; per-worker rates and peaks to be measured in the pilot.
- Latency: priority lane p95 below 15 minutes; standard lane to be set in the pilot; clustering finishes before the weekly review.
- Idempotency: key `item_id` + `task` + `model_version`; same input twice gives one row, a changed `input_hash` supersedes, a new version adds rows.
- Scaling: stateless workers; priority and standard pools scale on their own lag; clustering runs as a batch job.
- Data protection: item-level outputs only; no `author_ref` to any model and none in clusters. No profiling of individuals and no inference of protected attributes (religion, ethnicity, political affiliation, health about individuals); taxonomy validation enforces it. YouTube data is never used to profile on protected attributes; X data is never used for sensitive-attribute profiling or sensitive-event monitoring. Outputs carry `route`, `vendor`, `retention_class`; no text in logs.

## 10. Metrics and alerts

Prometheus: `items_in_total`, `items_out_total{result}`, `analysis_latency_seconds{lane}`, `consumer_lag_seconds{lane}`, `no_topic_total`, `zero_shot_share`, `cluster_candidates_total`, `cluster_accept_ratio`, `taxonomy_validation_failures_total`, `rerun_progress`, `dlq_total`. Alerts: priority p95 above 15 minutes; any DLQ entry; `no_topic_total` share rising; clustering job failed; review queue older than one week.

## 11. Dependencies

normalize-item, lang-dialect-id, store-writer, aggregator, alert-evaluator, raw-archiver (re-run source), retention-purger and deletion-propagator, Redpanda, Supabase Postgres, ClickHouse, Hetzner GPU pool or model API, Hugging Face, annotation tool, `listening-sdk`.

## 12. Risks and mitigations

- Taxonomies drift toward sensitive categories: validation denylist and sensitive-lexicon flag on clusters.
- Zero-shot noise looks like fact: nodes marked `zero_shot` in every client view until promoted.
- Cluster churn confuses reviewers: stable ids by centroid matching, a size floor set in the pilot.
- Dialect mismatch lowers recall on Iraqi slang: dialect strata and weekly sampling.
- Re-run cost after every taxonomy change: re-run per client window only.

## 13. Acceptance criteria

1. A fixture per platform yields a valid `items.analysis/v1` message with `task = topics:<taxonomy_id>`, scored `topics[]`, an `intent` and the active `model_version`.
2. The same message twice yields one row; a new `model_version` adds a second row and leaves the first.
3. A topic added to a client taxonomy scores items as `zero_shot` within one scheduled cycle and appears with `source = zero_shot`.
4. A taxonomy node named for a protected attribute or a protest is rejected by validation and never evaluated on X items.
5. At 12 items a second for 30 minutes with tier-1 items injected, priority p95 `fetched_at` to publish stays below 15 minutes.
6. A re-run of one archived day writes `run_kind = rerun` rows for items still in ClickHouse and none for deleted items.
7. A seeded fixture of unrelated posts about one new theme produces one cluster candidate in `review_queue` with representative `item_id`s and no author references.
8. Accepting a candidate creates a `zero_shot` node; discarding it leaves no node.
9. With the model server stopped for 6 minutes, no default topic is published and the backlog drains without loss.
10. A `deletions` message removes the item's text from the annotation store; its label remains.

## 14. Open questions

1. Which encoder and zero-shot approach win on held-out topics?
2. Sorani: own route or multilingual fallback?
3. How many labelled examples promote a `zero_shot` node to `supervised`?
4. Who staffs the weekly review, and may a client approve its own nodes?
5. Should text from images and video (analysis-media) feed topics?
6. Is one global taxonomy plus client taxonomies enough, or do government clients need separate defaults?
7. May platform content be used to train these models (legal, as analysis-sentiment question 3)?
