# lang-dialect-id

**Platform:** Shared · **Route:** shared · **Lane:** Processing · **Owner:** NLP engineer (processing) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Iraqi posts are written in Modern Standard Arabic, Iraqi dialect, Sorani Kurdish and English, often inside one sentence, and the same word has several spellings (البصرة and البصره, أحمد and احمد, ي and ى and ی). A client types a keyword once and it must match every spelling; a share-of-voice chart must not count Kurdish comments as Arabic ones.

The two languages cannot be folded alike. Sorani writes ی and ک where Arabic writes ي and ك. Fold Sorani with the Arabic rules and the letters that identify it disappear, and Kurdish words collide with Arabic ones. Language must therefore be decided on the raw text before any folding, and the fold must depend on the result. lang-dialect-id owns that order of operations and the one `text_norm` that keyword-matcher matches on.

Without it Kurdish content is mislabelled or invisible, keyword matching misses spellings or matches the wrong ones, the qualifier has no language share for its Iraqi-signal rule, dashboards cannot split by language, and every consumer folds text its own way.

## 2. Objective (the end state this service delivers)

End state: every record that normalize-item publishes carries `lang`, `lang_conf`, `script`, `dialect`, `dialect_conf`, `text_norm` and `lang_model_version`, produced by one detection step and one fold per language, and the same fold is applied to every client keyword.

Measurable target: 100% of records carry `text_norm` and `lang_model_version` (`lang = "und"` is allowed, a missing field is not); every fixture marked `must_pass` in the labelled fixture set passes; language accuracy and the `und` share on the pilot's labelled Iraqi sample are reported per release and gated at thresholds set from that sample (to be measured in the pilot); the service stays inside its share of normalize-item's 60 s fetch-to-publish target (share to be measured in the pilot).

## 3. Scope

### In scope
- Language identification with fastText: `ar`, `ckb`, `en`, `mixed`, plus `other` (any other language, including Kurmanji and Persian) and `und` (too little text).
- Script profile; advisory dialect scores (Iraqi Arabic for Arabic text, Sorani for Kurdish text).
- The fold that produces `text_norm`: CAMeL Tools rules for Arabic, KLPT for Sorani.
- `POST /v1/fold`, which keyword-matcher uses for client keywords; model and fold versioning; conformance fixtures shared with `listening-sdk`.

### Out of scope
- Deciding that a post or poster is Iraqi: source geography decides (registry `country_signals`, qualifier rule 2). Dialect never filters or routes.
- Sentiment, topics, entities, OCR, speech (analysis-sentiment, analysis-topics, analysis-entities, analysis-media); translation; spelling correction; transliteration of Arabizi (Arabic in Latin letters).
- Keyword matching (keyword-matcher); persistence (store-writer).

## 4. Users and consumers

- normalize-item: the only caller of `/v1/detect`; it embeds the result in `items.normalized`, and its `lang_rescore` jobs call it again.
- keyword-matcher: calls `/v1/fold` when it compiles keyword variants and matches on `text_norm`.
- poster-resolver and qualifier: read `lang` and `dialect` of a candidate's recent posts for qualifier rule 2 (at least 40% Iraqi Arabic or Sorani on the last 20 posts, one signal of five, two needed).
- analysis-sentiment, analysis-topics, analysis-entities pick their model by `lang`; aggregator and dashboards split by language; ops run releases, fixtures and replays.

## 5. How it works

### 5.1 Trigger and rotation

Trigger: a synchronous call. normalize-item sends `POST /v1/detect` per batch (up to 500 records); keyword-matcher sends `POST /v1/fold` when it rebuilds. There is no topic, consumer group, cursor or rotation: the service is stateless and any replica can answer any call. Ordering belongs to normalize-item (one worker per `source_id`); a result never depends on order or on the other records in the batch.

Replay: any change to a model, a threshold, the CAMeL Tools or KLPT version or the fold table produces a new `lang_model_version`. Ops then starts a normalize-item job with `kind = replay` over the affected days. It reads the archive raw-archiver wrote (`raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst`), calls `/v1/detect` again and republishes each item with the same `item_id` and a higher `version`. keyword-matcher re-matches the replayed items and recompiles its automata at the same version, because text and keywords share one fold. Records published with `lang_pending = true` are corrected the same way by normalize-item's `lang_rescore` job. This service itself is never replayed.

### 5.2 Step by step

1. Validate the batch: per record `record_id`, `kind`, `title`, `text`. Author, source and client fields are rejected.
2. Build the detection copy: NFKC; delete bidi and zero-width marks; drop URLs, @mentions, emoji and digits; keep hashtag words; flatten newlines.
3. Profile scripts (Arabic-script, Latin, other letters) and set `script`: `arab`, `latn`, `mixed` or `none`.
4. Run fastText on the detection copy and decide `lang` and `lang_conf` (5.3 A).
5. For `ar`, `ckb` and the Arabic part of `mixed`, compute dialect scores (5.3 B).
6. Fold the original text, title first, with the fold chosen by language and token (5.3 C).
7. Return results in request order with `lang_model_version`; count metrics; log no text.

### 5.3 The call it makes (the processing it performs)

**A. Language decision.** Model: fastText `lid.176` (labels such as `ar`, `arz`, `ckb`, `ku`, `fa`, `en`), fine-tuned on the pilot's labelled Iraqi sample when it exists. Rules, in order:
1. No letters: `lang = und`, `script = none`.
2. Fewer than `LID_MIN_LETTERS` letters: the model is not trusted. Arabic script holding a Sorani-only letter (ڕ ڵ ۆ ێ ە) gives `ckb`, other Arabic script gives `ar`, anything else gives `und`; `lang_conf` is capped at `LID_SHORT_CAP`.
3. Otherwise collapse labels: `ar` and `arz` become `ar` (fastText often tags Iraqi dialect as `arz`); `ckb` and `en` stay; every other label becomes `other`.
4. Count letters per token: Latin tokens count as `en`; Arabic-script tokens with a Sorani-only letter count as `ckb`; other Arabic-script tokens count for the document's stronger `ar` or `ckb` probability.
5. If two of `ar`, `ckb`, `en` each hold at least `LID_MIXED_MIN_SHARE` of the letters, `lang = mixed` and `lang_conf` is the minority language's share.
6. Otherwise the dominant label wins with its fastText probability as `lang_conf`; below `LID_MIN_CONF` the result is `und`.

**B. Dialect scores (advisory).** For `ar`, a classifier over MADAR-style classes (CAMeL Tools `DialectIdentifier` as baseline, replaced by an Iraqi-tuned model after the pilot): the Baghdad, Basra and Mosul classes sum into `iraqi`; the rest collapse to `gulf`, `levantine`, `egyptian`, `maghrebi`, `msa`, `other`. `dialect` is the top class, `dialect_conf` its score. For `ckb`: `dialect = sorani`, `dialect_conf` = the `ckb` share of the Kurdish probability mass against `ku` (Kurmanji); a Kurmanji-dominant text is `lang = other`. Under `DIALECT_MIN_TOKENS` tokens: `dialect = null`.

Country-level dialect identification scores 29 to 50 F1 in the literature, so the contract is fixed: `dialect` describes the wording of one text, never the author or the country, and no filter, route, alert or report may decide "Iraqi" on it. Source geography decides (registry `country_signals`; qualifier rule 2, where the Iraqi or Sorani share of the last 20 posts is one signal of five).

**C. Fold.** Detection runs on the raw text; the fold is chosen afterwards. The Arabic fold applies to `ar`, `en`, `other` and the Arabic-script tokens of `mixed`; the Sorani fold applies to `ckb` and to any token holding a Sorani-only letter. Steps, in order:

| # | Step | Arabic fold (CAMeL Tools) | Sorani fold (KLPT) |
|---|---|---|---|
| 1 | Unicode | NFKC; delete U+200B–U+200F, U+202A–U+202E, U+2066–U+2069, U+FEFF | same |
| 2 | Marks | delete harakat U+064B–U+0652, U+0670, U+06D6–U+06ED and tatweel U+0640 | same |
| 3 | Alef | أ إ آ ٱ → ا | same |
| 4 | Taa marbuta | ة → ه | KLPT standardisation, pinned version |
| 5 | Kaf | ک → ك | ك → ک |
| 6 | Yaa | ى and ی → ي | ي and ى → ی |
| 7 | Kept as written | چ گ پ ڤ ژ (Iraqi letters), ؤ ئ ء | ڕ ڵ ۆ ێ ە چ گ پ ڤ ژ ئ |
| 8 | Digits | ٠–٩ and ۰–۹ → 0–9 | same |
| 9 | Latin | casefold | same |
| 10 | Tokens | URLs deleted (they stay in `links`); `@`, `#`, `_` kept inside mention and hashtag tokens; other punctuation (، ؛ ؟ « » and ASCII), symbols and emoji become one space; collapse and trim | same |

Example: "النت منقطع بالبصرة من الصبح، شنو السالفة؟" becomes "النت منقطع بالبصره من الصبح شنو السالفه". `text_norm` covers `title` then `text`, joined by a space. Offsets reported by keyword-matcher count code points in `text_norm`. Thresholds `LID_MIN_LETTERS`, `LID_SHORT_CAP`, `LID_MIXED_MIN_SHARE`, `LID_MIN_CONF`, `DIALECT_MIN_TOKENS` ship inside the model bundle with values set from the pilot sample (to be measured in the pilot).

**D. `POST /v1/fold`.** Takes `{items: [{text, lang}]}` with an explicit `lang` (`ar`, `ckb`, `en`), never detects, and returns `text_norm` from the same code. `listening-sdk` carries a TypeScript copy of the table for normalize-item's fallback; a conformance suite keeps the two identical.

### 5.4 What it gets

Input: `title`, `text`, `kind`, `record_id`. Output per record: `lang`, `lang_conf`, `script`, `dialect`, `dialect_conf`, `text_norm`, plus the full `dialect_scores` vector in the response only.

It does not get: author, source, client or platform facts; text inside images or video (analysis-media); full news text (normalize-item sends the excerpt). It does not produce: Arabizi as Arabic, a Kurmanji dialect score, a country.

## 6. Inputs and outputs

### 6.1 Reads
- HTTP: `POST /v1/detect` from normalize-item, `POST /v1/fold` from keyword-matcher (and from tools in CI).
- Object storage: the versioned model bundle (fastText, dialect model, CAMeL Tools data, KLPT data), loaded at start-up; nothing is downloaded at run time.
- Control plane: `service_runs` (heartbeat, version).

### 6.2 Writes

No topic and no table. The response goes back to the caller; normalize-item copies `lang`, `lang_conf`, `script`, `dialect`, `dialect_conf`, `text_norm` and `lang_model_version` into `items.normalized/v1`. Per-record `status` is `ok`, `skipped` (no usable text) or `error`.

```json
{
  "lang_model_version": "lid-iq-2026.09",
  "results": [
    {"record_id": "facebook:post:1234567890_9876543210", "status": "ok",
     "lang": "ar", "lang_conf": 0.98, "script": "arab",
     "dialect": "iraqi", "dialect_conf": 0.84,
     "dialect_scores": {"iraqi": 0.84, "gulf": 0.09, "levantine": 0.03, "egyptian": 0.01, "maghrebi": 0.0, "msa": 0.03, "other": 0.0},
     "text_norm": "النت منقطع بالبصره من الصبح شنو السالفه"},
    {"record_id": "telegram:message:-1001234567:5521", "status": "ok",
     "lang": "ckb", "lang_conf": 0.97, "script": "arab",
     "dialect": "sorani", "dialect_conf": 0.91,
     "dialect_scores": {"sorani": 0.91, "kurmanji": 0.09},
     "text_norm": "ئاوی خواردنەوە نییە لە بەسرە"}
  ]
}
```

The second record arrived as "ئاوي خواردنەوە نييە لە بەسرە", typed with Arabic yaa.

### 6.3 State

None persisted. In memory: the loaded models, thresholds and `lang_model_version`. A `service_runs` row carries heartbeat and version.

## 7. Limits, quotas and cost

No external API or vendor is called, so there is no `budget_tag` and no quota-governor round trip. Compute is CPU only (fastText, the dialect model, the fold); no GPU. Load at full scale is about 1,000,000 texts a day, about 12 a second on average; peaks and texts a second per replica are to be measured in the pilot. Two replicas run for availability. A replay adds load: at normalize-item's default cap of 200 records a second, one archived day (about 1,000,000 items) takes about 83 minutes and a month (30.5M items) about 42 hours, so the pool is sized for live traffic plus 200 a second. Hetzner pricing in USD is confirmed at order time.

## 8. Failure handling and fallback

- Service down or slow: normalize-item backs off from 30 s to 15 min and, after 5 minutes of failures, publishes `lang = "und"` with the TypeScript fold and `lang_pending = true`, then enqueues `lang_rescore`. The fallback applies the Arabic fold with the Sorani-token override; Sorani tokens without a Sorani-only letter are folded wrongly until the rescore.
- Model load failure: readiness stays false, no traffic is served, an alert fires; a partial model is never served.
- Bad record (empty text, oversize text, library exception): that record returns `skipped` or `error`; the batch still succeeds; normalize-item treats it like the outage fallback for that record. Oversize text is detected on a prefix and folded in full.
- Dialect model failure: `dialect = null`; language and `text_norm` are still returned, because dialect is advisory.
- Rolling release: old and new versions answer side by side; each response names its version; the replay removes the mix.
- Fold drift between Python and TypeScript: the nightly conformance job fails and alerts.

## 9. Non-functional requirements

- Throughput: 12 texts a second on average, 200 more during replays; per-replica rate to be measured in the pilot.
- Latency: the chain is normalize within 60 s of fetch, matching within 60 s of normalization, analysis within 15 min for tier-1 sources, alerts within 5 min of the aggregate update. This service sits in the first hop; its per-call budget is a fixed share of the 60 s (to be measured in the pilot).
- Idempotency: deterministic; the same text under the same `lang_model_version` returns identical output on any replica; no randomness at inference.
- Scaling: stateless replicas, at least two, scaled on request latency and CPU.
- Security: no item text in logs or metric labels; TLS inside the cluster; the request schema carries no author or source field. Runtime: Python, because CAMeL Tools and KLPT are Python libraries (see 14).

## 10. Metrics and alerts

Prometheus: `lang_requests_total{endpoint,status}`, `lang_texts_total{lang}`, `lang_conf_bucket`, `lang_und_ratio`, `lang_mixed_ratio`, `dialect_null_total`, `detect_latency_seconds`, `fold_errors_total`, `model_load_seconds`, `fold_conformance_failures_total`. Alerts: p95 latency over budget for 5 minutes; error rate above zero for 10 minutes; `lang_und_ratio` or `lang_mixed_ratio` far from the 7-day baseline (margin set in the pilot); conformance failure; readiness flapping.

## 11. Dependencies

normalize-item and keyword-matcher (callers); `listening-sdk` (schema, TypeScript fold, fixtures); raw-archiver (replay source); fastText `lid.176` model; CAMeL Tools; KLPT; object storage (model bundle; Hugging Face is a cleared source for model files); Supabase Postgres (`service_runs`).

## 12. Risks and mitigations

- Weak dialect identification: advisory only; source geography decides; never a filter.
- Short comments and emoji: `und` or a capped `lang_conf`; no consumer drops a record on `und`.
- Arabizi is read as `en` or `und`: documented gap; Latin-script keyword variants come from the `keywords` table.
- Over-folding (ي and ى merge, so علي and على collide; hamza carriers stay unfolded): folding is for matching only, `text` is never altered; keyword exclusions handle collisions; revisit with pilot recall.
- Python and TypeScript folds diverge: one conformance suite, a nightly job, a version bump on any change.
- A fold change makes stored `text_norm` stale: a new `lang_model_version` triggers replay and automaton rebuild.
- Model and data licences (fastText `lid.176` is CC BY-SA 3.0; CAMeL Tools and KLPT terms): legal check before bundling.

## 13. Acceptance criteria

1. Every row of the 5.3 C table has fixture pairs (input, expected `text_norm`) and all pass, including both examples in 6.2.
2. "کوردستان وڵاتێکی جوانە" and the same sentence typed with Arabic kaf and yaa both return `lang = ckb` and `text_norm = "کوردستان وڵاتێکی جوانە"`; a build that folds before detecting fails this test.
3. Fixtures with چ گ پ ڤ in Iraqi Arabic text return them unchanged; ک in Arabic text becomes ك.
4. Every `must_pass` language fixture returns the expected `lang`: Iraqi Arabic post, MSA excerpt, Sorani post, English post, Arabic with an English brand name (`mixed`), emoji only (`und`), Persian sentence (`other`).
5. Gulf-dialect text from an Iraqi source and Iraqi-dialect text from a non-Iraqi source give the same keyword-matcher and aggregator output with `dialect` set to null: no consumer branches on it.
6. 10,000 archived texts sent twice, once through a restarted replica, return byte-identical results.
7. `/v1/fold` and the `listening-sdk` TypeScript fold agree on every fixture and on 10,000 sampled archived texts; CI fails otherwise.
8. With this service in the path, normalize-item's 50 records a second for 10 minutes test keeps p95 fetch-to-publish below 60 s with two replicas.
9. With the service stopped for 6 minutes, normalize-item publishes `lang = "und"` and `lang_pending = true`; after restart the `lang_rescore` job yields versions with `lang_pending = false`.
10. After a 10-minute run no log line or metric label contains fixture text, and a request with an author field is rejected.
11. A replica is not ready until all models are loaded; a rolling restart at 50 texts a second leaves no request failed after client retry.
12. Changing any model file, threshold or fold row changes `lang_model_version`; no response lacks it.

## 14. Open questions

1. Python or Node? The convention reserves Python for analysis workers and the news extractor; CAMeL Tools and KLPT make this a third exception. Confirm, or port the fold to TypeScript and keep only fastText and the dialect model in Python.
2. Kurmanji (Badini, Duhok) lands in `other` in v1. Does Kurdistan Region coverage need its own label?
3. Arabizi is common among young Iraqi users. Add a Latin-script Arabic class after the pilot?
4. Should the full `dialect_scores` vector be stored, or only the top class and its confidence (current draft)?
5. Who labels the Iraqi sample, how large is it, and which thresholds gate a release (to be measured in the pilot)?
