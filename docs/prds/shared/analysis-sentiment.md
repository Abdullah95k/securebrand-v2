# analysis-sentiment

**Platform:** Shared · **Route:** shared · **Lane:** Processing · **Owner:** ML lead (analysis) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A client watching Iraq online wants to know whether people are pleased or angry, and about what, not only how many mentioned them. Counting answers the first question; sentiment answers the second, and every other view leans on it: share of voice split by mood, the alert when negative mentions of a ministry's service jump, the trend line shown to a board.

Off-the-shelf Arabic sentiment tools are trained mostly on Modern Standard Arabic news and on Gulf, Levantine and Egyptian tweets. Iraqi writing breaks them: "كلش زين" (very good) and "مو خوش" (not good) are ordinary Iraqi, sarcasm is common after an outage, one post can mix Arabic, an English brand name, Arabic in Latin letters and Kurdish, and Sorani Kurdish is often not read at all. Confident charts that are wrong are worse than no charts.

The product promise is insight "in a way no one has seen before" for the Iraqi market, and that depends on Iraqi-dialect quality. This service is where that quality is first won or lost. Without it the product shows volume without meaning; with a weak version it shows the wrong meaning.

## 2. Objective (the end state this service delivers)

End state: every item on `items.normalized` that has text is published to `items.analysis` with a four-label sentiment result (positive, negative, neutral, mixed) and a score, stamped with `model_version`, or is accounted for with a skip reason. Items that matched a keyword also carry sentiment toward that keyword. Any model version can be re-run over the archive without disturbing the version in service.

Measurable target:
- 100% of consumed items accounted for (analysed, skipped with reason or dead-lettered; none silently dropped).
- p95 from `fetched_at` to publish below 15 minutes for tier-1 sources at full scale (about 1,000,000 items a day, about 12 a second on average); other tiers to be set in the pilot.
- Accuracy on the in-house Iraqi evaluation set (macro-F1 overall, worst stratum, aspect-level macro-F1, calibration error): to be set after the baseline is measured in the pilot. The protocol is fixed now (5.3): frozen gold set stratified by platform and dialect, double-annotated, unmodified CAMeLBERT-DA as baseline, no stratum allowed to regress at promotion.

## 3. Scope

### In scope
- Item-level sentiment (label, probabilities, score, confidence) for Iraqi and other Arabic, Sorani Kurdish and English text.
- Aspect-level sentiment toward the matched keyword or brand on items present on `item.hits` or `discovery.hits`.
- Sarcasm and code-switching flags; Arabic in Latin letters.
- Annotation sampling, labelled and gold sets, training, evaluation, registry entries, re-runs.

### Out of scope
- Language and dialect detection (lang-dialect-id), keyword matching (keyword-matcher), topics (analysis-topics), entities (analysis-entities), media (analysis-media).
- Storage (store-writer), aggregation (aggregator), alerting (alert-evaluator).
- Any score about a person: sentiment belongs to an item, never to an author.

## 4. Users and consumers

- store-writer writes rows to ClickHouse `analysis`; aggregator builds sentiment series from the active version; alert-evaluator reads them for negative-spike rules.
- Iraqi Arabic and Sorani annotators work the queue; the ML lead owns registry and promotion; ops runs re-runs and reads the DLQ.
- Account managers show sentiment in client reports with model version and evaluation date.

## 5. How it works

### 5.1 Trigger and rotation

Trigger: `items.normalized`, consumer group `analysis-sentiment`; no polling, so no rotation or cursor. The aspect path consumes `item.hits` and `discovery.hits` under group `analysis-sentiment-aspect`.

Priority: an intake stage looks up the tier of the item's `source_id` (or `author.author_source_id`) in a registry cache fed by `source.events` and refreshed from `sources`, and writes the item to `jobs.analysis-sentiment.priority` (tier 1, which includes sources on a client's priority list) or `jobs.analysis-sentiment`. GPU workers drain the priority topic first; target: analysis within 15 minutes of `fetched_at`. Intake never waits on the GPU, so a standard backlog cannot delay a tier-1 item. Aspect messages follow their item's lane.

Batching: micro-batches filled by token-length bucket; a priority item flushes its batch at once. Batch size and maximum wait are set in the pilot.

Re-run policy: every output is stamped with `model_version` and `preproc_version`. For a new version, ops creates a job on `jobs.analysis-sentiment` with `kind = rerun`, a date range and a platform filter. The worker reads normalized items from raw-archiver's Parquet archive (`archive/<platform>/<yyyy>/<mm>/`), newest month first, skips items no longer in ClickHouse `items`, and publishes with `run_kind = rerun` under group `analysis-sentiment-rerun-<model_version>` with a rate cap. New rows sit beside the old; nothing is overwritten until the switch-over. Models read only fields present in the archive (`title`, `text`, language fields, matched keyword), never the 7-day news cache, so a re-run reproduces live analysis.

### 5.2 Step by step

1. Pull a batch; drop items already analysed for the same `content_hash` and active `model_version` (LRU, then ClickHouse lookup); assign a lane.
2. Input: `title` plus `text` for articles and web results, `text` otherwise. Empty or link-only text is published with `status = skipped`, `reason = no_text`.
3. Route by `lang`, `dialect`, `script`: Arabic to the Arabic model; Arabic in Latin letters through transliteration to it; Sorani to the Sorani route; English to the multilingual fallback; other languages skipped with `reason = unsupported_lang`. Never a default label.
4. Pre-process, tokenize, truncate (set `truncated`), infer, calibrate.
5. Aspect path: join each hit to its item (buffer keyed by `item_id`, ClickHouse lookup for late hits), cut the sentence window around `matched_text`, classify, publish one `sentiment_aspect` message with all targets known.
6. Publish to `items.analysis`; commit after the ack; sample for labelling.

### 5.3 The call it makes (the processing it performs)

**Model choice.** CAMeLBERT-DA (start from `CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment`, three labels, new four-way head adding `mixed`) and MARBERTv2 are both fine-tuned on the in-house Iraqi set; the pilot picks by per-stratum macro-F1. The unmodified CAMeLBERT-DA checkpoint is the baseline for every target. Sorani needs its own model or a multilingual fallback (multilingual encoder fine-tuned on Sorani labels, or a Sorani-specific model), decided in the pilot. English uses the multilingual fallback.

**Pre-processing** (one Python module shared with training, `preproc_version`): URLs become `[URL]`; @-mentions removed; emoji and hashtag words kept; diacritics and tatweel removed; elongation collapsed and recorded; the model reads `text`, not folded `text_norm` (lexicon lookups only); Arabic in Latin letters transliterated first; `code_switched` set when Arabic-script and Latin-script tokens each pass a share chosen in the pilot. The author reference never reaches a model.

**Inference and thresholds.** Shared encoder, four-way sentiment head, binary sarcasm head; probabilities calibrated by temperature scaling per version. `score` = `p_positive` minus `p_negative` in [-1, 1]; `confidence` = highest probability; `label` = argmax. Below `min_conf` the label stays, `low_confidence = true` and the item goes to annotators; `sarcasm_prob` above `sarcasm_cut` sets `sarcasm_flag`. Annotators label the intended sentiment, so sarcastic praise is negative. Thresholds are chosen on the validation split per version, stored in the registry, never hard-coded.

**Aspect-level.** Sentence containing `matched_text` plus neighbours, target marked, pair classifier returns label, score and confidence per target; a post praising one operator and criticising another yields two results. v1 targets are matched keywords only.

**Human labelling loop.** `review_queue` rows (`kind = annotation:sentiment`) point to tasks in a self-hosted open-source annotation tool (Argilla or Label Studio). Tasks: low-confidence and sarcasm-flagged results, candidate-versus-active disagreements, and a random sample per platform and dialect stratum. Annotators label sentiment, sarcasm and target sentiment against a versioned guideline; a fraction is double-annotated and adjudicated (fraction and agreement floor set in the pilot). Corrected labels feed a weekly retrain. Each example keeps `item_id`, `retention_class`, `expires_at`: its text is purged with the item (deletion-propagator, retention-purger) and only the label stays, so short-retention strata (X, YouTube comments, LinkedIn, Meta on request) are topped up continuously.

**Evaluation.** Frozen, versioned gold set (`gold-v1`, ...), never trained on, double-annotated, stratified by platform (facebook, tiktok, instagram, youtube, telegram, x, linkedin, news) and dialect (Iraqi, other Arabic, Modern Standard Arabic, Sorani, English), with flags for sarcasm, code-switching and Latin-letter Arabic. Metrics: macro-F1 overall and per stratum, per-class precision and recall, confusion matrix, expected calibration error (labels carry no intensity, so `score` is judged by calibration), aspect macro-F1 on its own subset. A weekly sample of live predictions per stratum is labelled to estimate live precision and watch label-share drift. Promotion gate: candidate matches or beats active overall, no stratum below tolerance (set in the pilot), acceptable drift in a live shadow run, ML lead sign-off.

**Model registry and serving.** Artefacts in a private Hugging Face repository or Hetzner Object Storage (`models/sentiment/<model_version>/`) with a model card (training-set version, `preproc_version`, thresholds, calibration, gold report). Status lives in control-plane table `model_versions` (proposed): candidate, shadow, active, retired. Switch-over flips one row; aggregator then reads the new version. History that cannot be re-run keeps the old version's rows, and dashboards mark the switch date as a possible trend break. Serving: Python workers on a Hetzner GPU pool, or a model API from a vendor passing the same ownership screening (Hugging Face Inference Endpoints is the cleared candidate); the choice per route (Arabic, Sorani, aspect) is open (question 5).

### 5.4 What it gets

`title`, `text`, `lang`, `dialect`, `script`, `kind`, `retention_class`, source tier and, for aspects, `keyword_id` and `matched_text`. Not the author's identity, images or video, the parent post's text (a comment is judged alone in v1) or article text beyond the excerpt.

## 6. Inputs and outputs

### 6.1 Reads
- Topics: `items.normalized`, `item.hits`, `discovery.hits`, `source.events`, `jobs.analysis-sentiment` and `.priority` (`analyze`, `rerun`).
- Control plane: `sources`, `model_versions`, `retention_classes`, `review_queue`, `service_runs`; ClickHouse `items`, `comments`, `analysis`; object storage `archive/`, `models/sentiment/`.

### 6.2 Writes
`items.analysis` (partitioned by `source_id`; logical key `item_id` + `task` + `model_version`), `review_queue`, `dlq.analysis-sentiment`. Tasks: `sentiment` and `sentiment_aspect` (same envelope; `result.targets[]` with `keyword_id`, `matched_text`, `label`, `score`, `confidence`).

```json
{
  "schema": "items.analysis/v1",
  "message_id": "01J9W4Z6D3N8P2Q4R5S6T7U8V9",
  "produced_at": "2026-10-06T09:15:12Z",
  "producer": {"service": "analysis-sentiment", "version": "0.3.0", "job_id": "analysis-sentiment:priority:0007"},
  "analysis_key": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f:sentiment:sent-iq-2026.11",
  "item_id": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f", "item_version": 1,
  "content_hash": "sha256:4b2e…", "input_hash": "sha256:91a7…",
  "platform": "facebook", "kind": "post", "source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566",
  "task": "sentiment", "model_version": "sent-iq-2026.11", "preproc_version": "pp-2026.10",
  "run_kind": "live", "lane": "priority", "status": "ok",
  "lang": "ar", "dialect": "iraqi", "item_fetched_at": "2026-10-06T09:13:58Z",
  "route": "green", "vendor": null, "retention_class": "meta_on_request", "expires_at": null,
  "result": {
    "label": "negative", "score": -0.63, "confidence": 0.68,
    "probs": {"positive": 0.05, "negative": 0.68, "neutral": 0.21, "mixed": 0.06},
    "low_confidence": false, "sarcasm_prob": 0.04, "sarcasm_flag": false,
    "code_switched": false, "truncated": false, "model_route": "ar"
  }
}
```

### 6.3 State
Consumer offsets; LRU of analysed keys and the hit-join buffer (rebuilt lazily); registry cache version; re-run progress in `cursors` (`service = analysis-sentiment`, `cursor = rerun:<model_version>:<last archive object key>`); `model_versions` rows; a `service_runs` row.

## 7. Limits, quotas and cost

No platform API is called. Cost is the GPU pool, ClickHouse lookups and annotator time. Load at full scale: about 1,000,000 items a day, about 12 a second on average, all through the item-level model; the aspect model runs only on items with hits, and the hit share is to be measured in the pilot. GPU hours, per-item cost in USD and peak multiples are to be measured in the pilot; Hetzner pricing is confirmed at order time. Re-runs are the large job: 12 months of archive at target volume is about 366 million items (30.5 million a month times 12), so re-runs use a separate burst allocation sized from the pilot cost per item. If a model API is chosen, the service declares `budget_tag` `analysis_model_api` (new, to be added to the canonical list) and asks quota-governor before each batch.

## 8. Failure handling and fallback

- Model server down: backoff with jitter from 30 s to 15 min; after 5 attempts the job goes to `dlq.analysis-sentiment` and an alert fires. No default label ever fills a gap; items wait.
- Degraded capacity: the priority lane is served first; the standard lane waits and its lag alert fires; no weaker model unless the pilot shows one that meets the 15-minute target.
- Poison item (exception after 5 attempts): dead-lettered by `item_id`, never with text.
- Hit before item visible: held in the join buffer, then ClickHouse lookup, then retry and DLQ.
- Unknown `lang` value or schema version: skipped with a reason, counted, alerted.

## 9. Non-functional requirements

- Throughput: about 12 items a second average at full scale; items a second per GPU worker and peaks to be measured in the pilot.
- Latency: priority lane p95 below 15 minutes; standard lane to be set in the pilot.
- Idempotency: key `item_id` + `task` + `model_version`. Same input twice, one row; an edited item (new `content_hash`) or new late hit (new `input_hash`) supersedes the row for that key; a new `model_version` creates a new row and leaves the old.
- Scaling: stateless workers; priority pool scales on priority lag, standard pool on partition lag, re-run pools separate.
- Data protection: item-level outputs only; no `author_ref` to any model, no output joined to authors. No profiling of individuals and no inference of protected attributes (religion, ethnicity, political affiliation, health about individuals). YouTube data is never used to profile on protected attributes; X data is never used for sensitive-attribute profiling. Every output carries `route`, `vendor`, `retention_class`; no item text in logs.

## 10. Metrics and alerts

Prometheus: `items_in_total`, `items_out_total{result=ok|skipped|dlq}`, `analysis_latency_seconds{lane}`, `consumer_lag_seconds{lane}`, `low_confidence_total`, `annotation_queue_depth`, `label_share{platform,dialect,label}`, `rerun_progress`, `rerun_skipped_deleted_total`, `dlq_total`. Alerts: priority p95 above 15 minutes; standard lag rising; any DLQ entry (reviewed daily); label-share drift beyond tolerance; annotation queue older than the labelling cycle.

## 11. Dependencies

normalize-item and lang-dialect-id (inputs), keyword-matcher (hits), raw-archiver (re-run source), store-writer, aggregator, alert-evaluator, retention-purger and deletion-propagator (annotation store), Redpanda, Supabase Postgres, ClickHouse, Hetzner GPU pool or model API, Hugging Face, annotation tool, `listening-sdk`.

## 12. Risks and mitigations

- Dialect and sarcasm errors: dialect strata, sarcasm head, weekly live sampling.
- Weak Sorani: separate model or fallback decided on measurements; client views mark Sorani as lower confidence until a target is set.
- Platform terms may limit training on content: legal review before the training set is built (question 3); examples follow item retention.
- Trend break at switch-over: re-run the live window first; mark the date.

## 13. Acceptance criteria

1. A fixture per platform's normalized item yields a valid `items.analysis/v1` message with `task = sentiment`, one of the four labels, `score` in [-1, 1], probabilities summing to 1 and the active `model_version`.
2. The same message twice yields one stored row; an edited item supersedes it; a new `model_version` adds a second row and leaves the first unchanged.
3. At 12 items a second for 30 minutes with tier-1 items injected, priority-lane p95 `fetched_at` to publish stays below 15 minutes.
4. A re-run of one archived day writes `run_kind = rerun` rows for every item still in ClickHouse, none for deleted items, and changes no old row.
5. An item with hits on two keywords yields two independent `targets[]`; an item with no hit yields none.
6. Fixtures for Iraqi Arabic, Modern Standard Arabic, Sorani, English, Latin-letter Arabic and an unsupported language give the expected `model_route` or a `skipped` result with a reason, never a default label.
7. A contract test shows no `author_ref` in the inference payload; a log scan finds no item text.
8. Low-confidence and sarcasm fixtures appear in `review_queue` (`kind = annotation:sentiment`); a labelled result returns to the training set with its `retention_class`.
9. With the model server stopped for 6 minutes, no default label is published, the backlog drains after restart without loss, and a job reaches the DLQ only after 5 attempts.
10. A candidate that regresses any stratum beyond tolerance cannot be set `active`.
11. A `deletions` message removes the item's text from the annotation store and its example from stratum counts; the label remains.

## 14. Open questions

1. CAMeLBERT-DA or MARBERTv2; one model for Modern Standard Arabic and dialect, or two?
2. Sorani: own model or multilingual fallback, and are there enough labelled examples?
3. May each platform's content and vendor data be used to train and evaluate in-house models, and for how long? Legal to confirm.
4. Argilla or Label Studio, and who staffs annotation?
5. GPU pool or model API per route; full model on every item or only on hits and client-watched sources (a cost lever)?
6. Should OCR and transcript text from analysis-media feed sentiment in a second pass, and should push sources use the priority lane?
7. Confirm `lang` codes and any Latin-letter Arabic flag with lang-dialect-id, and hit field names with keyword-matcher.
