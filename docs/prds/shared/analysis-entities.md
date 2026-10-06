# analysis-entities

**Platform:** Shared · **Route:** shared · **Lane:** Processing · **Owner:** ML lead (analysis) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Keywords find posts. They do not say who or where a post is about. A client wants to see mentions by governorate, to know whether a post names the ministry or a competitor, and to group "زين", "Zain" and "زين العراق" as one company. Iraqi writing makes this hard: the same company appears in Arabic, Latin letters and Kurdish, with spelling variants, abbreviations and slang; and "زين" is also the ordinary word for "good".

This service finds named things in each item (brands, companies, institutions such as ministries and state companies, places such as governorates and cities, products) and links each to one entry in a curated knowledge base kept in the control plane, with Arabic, Kurdish and English aliases. The product promise is insight "in a way no one has seen before" for the Iraqi market, and that depends on understanding Iraqi dialect and names, not on translating them. Without this service the product cannot break results down by place or institution, cannot merge spellings, and cannot say what a post is about; with a careless one it would also risk naming private people.

## 2. Objective (the end state this service delivers)

End state: every item with text carries linked entities (one `entity_id` per mention, with type and score), a resolved governorate where a place is named, and no identity of any private individual, stamped with `model_version` and `kb_version`; new names that fit no entry reach a curator queue.

Measurable target:
- 100% of consumed items accounted for (processed, skipped with reason or dead-lettered).
- p95 `fetched_at` to publish below 15 minutes for tier-1 sources at full scale (about 1,000,000 items a day, about 12 a second on average).
- Zero stored identities of private individuals, audited on a sample each release (a hard gate, not a statistical target).
- Accuracy on the in-house Iraqi evaluation set (span F1 per type, link precision and recall, no-link accuracy, false-link rate on ambiguous aliases): to be set after the baseline is measured in the pilot. Protocol in 5.3.

## 3. Scope

### In scope
- Named-entity recognition for brands, companies, institutions, places, products and public persons; linking to the knowledge base (KB); place hierarchy (city to governorate); the person guard; candidate-name queue; KB versioning; labelling loop, evaluation, registry, re-runs.

### Out of scope
- Keyword matching (keyword-matcher), language detection (lang-dialect-id), sentiment, topics, media (analysis-sentiment, analysis-topics, analysis-media).
- Linking or storing private individuals; resolving who an author is (poster-resolver is about sources, not people).
- KB curation workflow screens (control plane tooling), storage and aggregation (store-writer, aggregator).

## 4. Users and consumers

- store-writer persists entity rows; aggregator builds mentions by governorate, institution and brand; alert-evaluator can fire on a named institution; analysis-media may use brand ids for logos.
- Curators (ops and account managers) maintain the KB and review candidates; clients add their own brands and products with aliases; annotators label spans and links.

## 5. How it works

### 5.1 Trigger and rotation

Trigger: `items.normalized`, consumer group `analysis-entities`; no polling.

Priority: the same two-lane pattern as analysis-sentiment: intake resolves the tier of `source_id` (or `author.author_source_id`) from the registry cache and writes to `jobs.analysis-entities.priority` (tier 1) or `jobs.analysis-entities`. Target: analysis within 15 minutes of `fetched_at` for tier 1.

Batching: micro-batches by token length for the model; the gazetteer runs inline on CPU. Sizes set in the pilot.

Re-run policy: every output is stamped with `model_version` and `kb_version`. A new model version re-runs the backlog: a job on `jobs.analysis-entities` with `kind = rerun` reads normalized items from raw-archiver's Parquet archive (`archive/<platform>/<yyyy>/<mm>/`), newest first, skips items no longer in ClickHouse `items`, and publishes `run_kind = rerun` rows under group `analysis-entities-rerun-<model_version>`, rate-capped, beside the old rows until switch-over. A KB release is not a model version: it changes `kb_version`; items matching a changed alias are found through the ClickHouse Arabic text index on `text_norm` and re-linked, and their row for the same key is superseded (`input_hash` changes).

### 5.2 Step by step

1. Pull a batch; skip items already done for the same `content_hash`, `model_version` and `kb_version`; assign a lane.
2. Input: `title` plus `text`; empty text is skipped (`reason = no_text`).
3. Gazetteer pass: match `text_norm` against folded aliases from the KB.
4. Model pass: token-classification NER finds mentions the gazetteer missed.
5. Merge; for each mention generate candidates from the alias index; rank with context; link above the threshold, otherwise no-link.
6. Person guard (below); place hierarchy lookup.
7. Publish one `items.analysis` message per item (`task = entities`); commit after the ack.
8. Sample for labelling and queue unlinked names for curators.

### 5.3 The call it makes (the processing it performs)

**Knowledge base.** Control-plane tables `kb_entities` and `kb_aliases` (proposed). Entity: `entity_id`, `type` (brand, company, institution, place, product, person_public), names in Arabic, Sorani and English, `parent_id` (city to governorate, directorate to ministry), `scope` (global or a client), `status`, `kb_version`; for persons only: `public_role` and `role_terms`. Alias: text, `lang`, `script`, folded form (same folding as `text_norm`), kind (official, colloquial, abbreviation, misspelling, transliteration), and `ambiguous` with context cues (for "زين": link as the company only when the context is about the operator or its services). Seed: governorates and cities, ministries and state companies, the main brands, and every client's own brands and products with Iraqi, Sorani and English aliases.

**Model choice.** A hybrid: the gazetteer gives precision on known names and aliases; an Arabic encoder (CAMeLBERT or MARBERTv2, token classification, fine-tuned on an in-house Iraqi NER set) finds unseen mentions; Sorani needs its own model or a multilingual fallback, decided in the pilot. Linking: alias candidates re-ranked with a multilingual sentence encoder over mention context. Choices made on pilot measurements.

**Pre-processing.** Shared module (`preproc_version`): URLs masked, elongation collapsed, emoji kept; matching on `text_norm`, model on `text`; the author reference never reaches a model.

**Thresholds.** Link threshold and no-link rule per type, chosen on the validation split per version and stored in `model_versions.thresholds`; stricter for ambiguous aliases. Below threshold a brand, company or product mention is `unlinked`.

**Person guard.** A person mention is linked only if (a) it matches a KB entry of type `person_public` (public officials and public figures), and (b) the context is the person's public role (role terms present or an institution context, and no private-life or health cue). Anything else is dropped: no `entity_id`, no surface form, no offsets; only `private_person_mentions` (a count) is kept. This also keeps health and other protected information about individuals out of the output. A guard audit sample is checked every release.

**Candidate queue.** Unlinked organisation, place and product surface forms (never persons) are counted with up to three `item_id`s as evidence and sent to `review_queue` (`kind = kb_candidate`); curators add an alias, add an entity or discard. No author references are stored.

**Human labelling loop.** `review_queue` rows (`kind = annotation:entities`) in the self-hosted annotation tool: label spans, types and KB links; sources are low-confidence links, ambiguous aliases, and a random sample per platform and dialect stratum. Examples follow the item's retention class (text purged with the item).

**Evaluation.** Frozen, versioned gold set stratified by platform and dialect, double-annotated: strict span-and-type F1 per type, link precision and recall, no-link accuracy, false-link rate on ambiguous aliases (including "زين"), place-to-governorate accuracy. Person guard: audited sample with a zero-tolerance gate. Promotion gate: no stratum below tolerance, shadow run, ML lead sign-off. Targets after the pilot baseline.

**Registry and serving.** `model_versions` (proposed), artefacts in `models/entities/<model_version>/`; the KB loads into worker memory per `kb_version`. Python workers on CPU for the gazetteer and the Hetzner GPU pool for the model, or a model API from a screened vendor; choice open (question 5).

### 5.4 What it gets

`title`, `text`, `text_norm`, `lang`, `dialect`, `script`, `kind`, `retention_class`, source tier. Not the author's identity, media content, or thread context. Place from text only; the source's `country_signals` are not used.

## 6. Inputs and outputs

### 6.1 Reads
- Topics: `items.normalized`, `source.events`, `jobs.analysis-entities` and `.priority`.
- Control plane: `kb_entities`, `kb_aliases`, `model_versions`, `sources`, `retention_classes`, `review_queue`; ClickHouse `items`, `analysis` (text index on `text_norm`); object storage `archive/`, `models/entities/`.

### 6.2 Writes
`items.analysis` (partitioned by `source_id`; logical key `item_id` + `task` + `model_version`), `review_queue`, `dlq.analysis-entities`.

```json
{
  "schema": "items.analysis/v1",
  "message_id": "01J9W4ZD5F7H9K1M3N5P7Q9R1S",
  "produced_at": "2026-10-06T09:15:14Z",
  "producer": {"service": "analysis-entities", "version": "0.2.0", "job_id": "analysis-entities:priority:0009"},
  "analysis_key": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f:entities:ent-iq-2026.11",
  "item_id": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f", "item_version": 1,
  "content_hash": "sha256:4b2e…", "input_hash": "sha256:7a42…",
  "platform": "facebook", "kind": "post", "source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566",
  "task": "entities", "model_version": "ent-iq-2026.11", "kb_version": 14,
  "run_kind": "live", "lane": "priority", "status": "ok",
  "lang": "ar", "dialect": "iraqi", "item_fetched_at": "2026-10-06T09:13:58Z",
  "route": "green", "vendor": null, "retention_class": "meta_on_request", "expires_at": null,
  "result": {
    "entities": [{
      "type": "place", "entity_id": "kb-pl-0007", "name_en": "Basra", "level": "city",
      "governorate_id": "kb-pl-0003", "surface": "بالبصرة", "start": 12, "end": 19,
      "link_score": 0.96, "source": "both"
    }],
    "unlinked": [],
    "private_person_mentions": 0
  }
}
```

### 6.3 State
Consumer offsets; the KB and alias index in memory by `kb_version` (reloaded on release); registry cache; LRU of done keys; re-run and alias re-link progress in `cursors` (`service = analysis-entities`, `cursor = rerun:<model_version>:<last archive object key>`); `service_runs`.

## 7. Limits, quotas and cost

No platform API is called. Cost is CPU for the gazetteer, the GPU pool for NER and re-ranking, and curator time. Every item with text (about 1,000,000 a day, about 12 a second) passes the gazetteer; the model runs on all items too unless the pilot shows gazetteer-only is enough on some strata. GPU hours, per-item cost in USD and peaks are to be measured in the pilot; Hetzner pricing is confirmed at order time. A full re-run of 12 months at target volume is about 366 million items (30.5 million a month times 12), so full re-runs use a separate burst allocation; KB releases re-link only matching items. A model API would need a `budget_tag` `analysis_model_api` (new) and a quota-governor allowance.

## 8. Failure handling and fallback

- Model server down: gazetteer-only results are published with `source = gazetteer`, `degraded = true`, and a rescore job is queued for the window; backoff with jitter from 30 s to 15 min; after 5 attempts to `dlq.analysis-entities`.
- KB load fails or a release fails validation: the last valid `kb_version` keeps serving; alert.
- Person guard unavailable: person mentions are dropped (fail closed), never linked.
- Poison item after 5 attempts: dead-lettered by `item_id`, never with text.
- Unknown `lang` or schema value: skipped with a reason, counted.

## 9. Non-functional requirements

- Throughput: about 12 items a second average at full scale; per-worker rates and peaks to be measured in the pilot.
- Latency: priority lane p95 below 15 minutes; standard lane to be set in the pilot.
- Idempotency: key `item_id` + `task` + `model_version`; same input twice gives one row; a changed `input_hash` (edit or new `kb_version`) supersedes; a new `model_version` adds rows.
- Scaling: stateless workers; each lane scales on its lag; re-run and re-link pools separate.
- Data protection: private individuals are never linked and their names, handles and spans are never stored; public officials and public figures are linked only acting in their public role. No profiling of individuals and no inference of protected attributes (religion, ethnicity, political affiliation, health about individuals), including from names. YouTube data is never used to profile on protected attributes; X data is never used for sensitive-attribute profiling. Outputs carry `route`, `vendor`, `retention_class`; no text in logs.

## 10. Metrics and alerts

Prometheus: `items_in_total`, `items_out_total{result}`, `analysis_latency_seconds{lane}`, `consumer_lag_seconds{lane}`, `entities_linked_total{type}`, `unlinked_total{type}`, `person_mentions_dropped_total`, `kb_candidates_total`, `degraded_total`, `kb_version`, `rerun_progress`, `dlq_total`. Alerts: priority p95 above 15 minutes; DLQ entry; `degraded_total` rising; candidate queue older than one week; any person guard audit failure.

## 11. Dependencies

normalize-item, lang-dialect-id (`text_norm` folding), keyword-matcher (alias overlap with keywords), raw-archiver, store-writer, aggregator, alert-evaluator, retention-purger and deletion-propagator, analysis-media (consumer of brand ids), Redpanda, Supabase Postgres (KB tables), ClickHouse, Hetzner, Hugging Face, annotation tool, `listening-sdk`.

## 12. Risks and mitigations

- Ambiguous aliases such as "زين": ambiguity flag with context cues, dedicated evaluation slice, no-link allowed.
- KB goes stale: weekly candidate review, client-supplied aliases, release versioning.
- A private person is stored by mistake: the guard fails closed, drops surface forms, and is audited every release.
- Sorani and spelling variants: aliases in all three languages and folded matching; Sorani model decided on measurements.
- KB releases cause churn in aggregates: `kb_version` stamped on rows; supersession only for matching items.

## 13. Acceptance criteria

1. A fixture per platform yields a valid `items.analysis/v1` message with `task = entities`, `model_version` and `kb_version`.
2. A fixture naming "البصرة" links to the Basra city entry with its governorate; an alias in Kurdish and one in English link to the same entry as the Arabic name.
3. "زين" in a sentence about the word "good" is not linked; in a sentence about the operator's service it links to the company.
4. A fixture naming a private individual produces no `entity_id`, no surface form and no offsets, and increments `private_person_mentions`.
5. A fixture naming a minister in the context of the ministry's policy links; the same name in a private-life or health sentence does not.
6. An unknown company name appears once in `review_queue` as `kb_candidate` with at most three `item_id`s and no author reference.
7. A KB release that adds an alias re-links items matching it, supersedes only their rows and stamps the new `kb_version`.
8. With the model server stopped for 6 minutes, gazetteer-only messages publish with `degraded = true` and a rescore job is queued.
9. A re-run of one archived day writes `run_kind = rerun` rows for items still in ClickHouse and none for deleted items.
10. At 12 items a second for 30 minutes with tier-1 items injected, priority p95 `fetched_at` to publish stays below 15 minutes.
11. A `deletions` message removes the item's text from the annotation store; its labels remain.

## 14. Open questions

1. Should a KB release create a new `model_version` (clean audit, heavy re-run) or supersede in place as drafted?
2. Who curates the global KB, and may clients add global entries?
3. Does `person_public` need a list of named public officials maintained by ops, and who decides who counts as a public figure?
4. Sorani NER: own model or multilingual fallback?
5. CPU gazetteer plus GPU model, or a model API for linking?
6. Should aspect sentiment in analysis-sentiment use linked entities as targets in a later version?
7. May platform content be used to train and evaluate this model (legal, as analysis-sentiment question 3)?
