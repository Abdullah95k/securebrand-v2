# analysis-media

**Platform:** Shared · **Route:** shared · **Lane:** Processing · **Owner:** ML lead (analysis) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A large part of Iraqi social media is not text. A Facebook post can be a screenshot of a bill, an Instagram post a photo of a shop front, a TikTok clip a person talking over music. Banners, memes and screenshots carry Arabic or Kurdish words that no text pipeline sees; a video's meaning is in its audio. A client whose logo appears in a viral video, or whose outage is described only in a voice message, is invisible to a text-only listening product.

This service reads what the text does not: it extracts words from images and video frames (OCR), describes images with a small set of tags, transcribes speech in Iraqi Arabic dialect, and spots the logos of the client's brands. The product promise is insight "in a way no one has seen before" for the Iraqi market, and that depends on Iraqi quality here too: Arabic dialect speech and Arabic and Sorani script in photographs are where generic tools fail most. Without this service the product misses what many Iraqis actually post; with a poor one, it invents words nobody said.

## 2. Objective (the end state this service delivers)

End state: every item with media is analysed per task (OCR, tags, speech-to-text, logo spotting) within the cost rules, each result stamped with its own `model_version`, every media file stored once by hash and every task re-runnable.

Measurable target:
- 100% of items with `media[]` accounted for per task (analysed, skipped by a named cost rule, `media_unavailable` or dead-lettered).
- p95 `fetched_at` to publish below 15 minutes for tier-1 items for the first-pass tasks (OCR, tags, logos, and speech-to-text up to the duration cap), at full scale (about 1,000,000 items a day, about 12 a second on average).
- Accuracy on the in-house Iraqi evaluation sets (character and word error rate per script for OCR, word error rate per dialect for ASR, tag precision and recall, logo precision and recall per brand): to be set after the baseline is measured in the pilot. Protocol in 5.3.

## 3. Scope

### In scope
- Download of media from `media[].url` into object storage by hash (`media/<sha256>`); OCR on images and video frames (Arabic and Kurdish script); image tags from a closed vocabulary; speech-to-text for video and audio; logo spotting for client brands.
- Frame sampling, cost rules, deduplication by hash, per-task `model_version`, evaluation, registry, re-runs.

### Out of scope
- Face detection or recognition, person identification, voice prints, and any inference of age, gender, ethnicity, religion or health from images or audio.
- Sentiment, topics and entities on the extracted text (analysis-sentiment, analysis-topics, analysis-entities; open question 4).
- Crowd, protest, rally or security-scene detection.
- Storage, aggregation, alerting (store-writer, aggregator, alert-evaluator).

## 4. Users and consumers

- store-writer persists rows; aggregator builds brand-appearance and tag views; alert-evaluator can fire on a client logo in high-reach media.
- Client brand managers upload logo reference sets through the control plane; annotators transcribe and check OCR; the ML lead owns the registry.

## 5. How it works

### 5.1 Trigger and rotation

Trigger: `items.normalized` messages whose `media[]` is non-empty, consumer group `analysis-media`; no polling. A hit on `item.hits` or `discovery.hits` for an item skipped earlier enqueues it again at standard priority.

Priority: an intake stage resolves the source tier from the registry cache fed by `source.events` and writes the item to `jobs.analysis-media.priority` (tier 1, which includes client priority lists), `jobs.analysis-media` (tier 2 and items with hits) or applies a skip rule (5.3). Target: first-pass analysis within 15 minutes of `fetched_at` for tier 1. Media pools are separate per task so slow video ASR never blocks image OCR.

Batching: images in micro-batches per task; video work runs per file; sizes set in the pilot.

Re-run policy: every output is stamped with its task's `model_version`. For a new version of one task, ops creates a job on `jobs.analysis-media` with `kind = rerun` and that task; the worker reads normalized items from raw-archiver's Parquet archive (`archive/<platform>/<yyyy>/<mm>/`), newest first, skips items no longer in ClickHouse `items`, reads media from `media/<sha256>` (never the platform URL), and publishes `run_kind = rerun` rows under group `analysis-media-rerun-<model_version>`, rate-capped, beside the old rows until switch-over.

### 5.2 Step by step

1. Pull a batch; apply cost rules; assign lane.
2. Fetch each media URL once (plain HTTP GET of the URL the payload gave; no accounts, no proxies, no CAPTCHA solving), compute `sha256`, store `media/<sha256>` if absent, publish `task = media_fetch`. Expired or refused URLs give `media_unavailable`, retried up to 5 attempts.
3. Reuse: a result for the same `sha256`, task and `model_version` is copied into the item's message with `reused = true`.
4. Video: extract the audio track and sample frames; drop near-identical frames by perceptual hash.
5. Run the tasks (below) from object storage by hash.
6. Publish one message per item per task; commit after the ack.

### 5.3 The call it makes (the processing it performs)

**Cost rules (applied before any model runs).** Frames are sampled at a fixed interval plus scene changes, up to a frame cap per video; audio is transcribed up to a duration cap; longer media are cut and marked `truncated`. Interval and caps are set in the pilot. Tier-3 and dormant sources without a hit are skipped (`reason = low_priority_source`); tier 2 gets images in full and video sampled; tier 1 gets everything within the caps. YouTube audio and video are not downloaded in v1 (our reading of the Developer Policies; thumbnails only, question 2).

**OCR.** Arabic and Sorani script on images and frames. Candidates (chosen in the pilot on an in-house set of Iraqi screenshots, banners, memes and shop signs): Tesseract with Arabic and Central Kurdish models, PaddleOCR, and a fine-tuned open model. Output per medium: text, `lang`, `script`, confidence, per-frame time for video. OCR text is derived text and keeps the item's retention class.

**Image tags.** An image encoder with a closed, reviewed vocabulary (for example screenshot, meme, document, product, storefront, vehicle, cable or equipment, food, landscape). Excluded for ever: any tag describing people or their attributes, crowds, protests, rallies, military or security scenes. Output: tags with scores above per-tag thresholds.

**Speech-to-text.** Arabic dialect ASR: an open-weight multilingual model (the Whisper family as baseline) fine-tuned on an in-house transcribed Iraqi set; voice-activity detection skips silence and music; segments carry time and confidence; the transcript goes to lang-dialect-id for `lang` and `dialect`. No speaker identification. Sorani ASR is a separate decision in the pilot.

**Logo spotting.** For each client, reference logos in object storage and control-plane table `brand_assets` (proposed). A detector plus embedding match scores candidate regions against that client's references; only brands in active client sets are searched, only on items relevant to that client. Output: `brand_id`, score, box, frame time. No face detection.

**Human labelling loop.** `review_queue` rows (`kind = annotation:media`) in the self-hosted annotation tool: transcribe or correct ASR segments, correct OCR text, confirm tags, confirm or reject logo hits. Low-confidence results, new-brand reference gaps and a random sample per platform and dialect stratum are queued. Examples follow the item's retention class; media is purged with the item.

**Evaluation.** Separate frozen, versioned sets per task, stratified by platform and dialect: OCR (character and word error rate per script and per image type: screenshot, banner, meme, photo), ASR (word error rate per dialect and platform), tags (precision and recall on the vocabulary), logos (precision and recall per brand at the shipped threshold and false-positive rate on look-alikes). Promotion gate: no stratum below tolerance, shadow run, ML lead sign-off. Targets are set after the pilot baseline.

**Registry and serving.** `model_versions` (proposed) per task (`media_ocr`, `media_tags`, `media_asr`, `media_logo`), artefacts under `models/media/<task>/<model_version>/`. ffmpeg runs on CPU workers; models on a Hetzner GPU pool or a model API from a screened vendor; the choice per task is open (question 5).

### 5.4 What it gets

Media bytes by hash, `type`, `url`, `platform`, `kind`, `route`, `retention_class`, source tier, and for logos the client's reference set. It does not get: private or login-gated media, Stories, audio of YouTube videos, faces or voices as identities, or anything beyond the cost caps.

## 6. Inputs and outputs

### 6.1 Reads
- Topics: `items.normalized`, `item.hits`, `discovery.hits`, `source.events`, `jobs.analysis-media` and `.priority`.
- Control plane: `sources`, `brand_assets`, `model_versions`, `retention_classes`, `review_queue`; ClickHouse `items`, `analysis`; object storage `media/<sha256>`, `archive/`, `models/media/`.

### 6.2 Writes
`items.analysis` (partitioned by `source_id`; logical key `item_id` + `task` + `model_version`), tasks `media_fetch`, `media_ocr`, `media_tags`, `media_asr`, `media_logo`; `media/<sha256>` objects; `review_queue`; `dlq.analysis-media`.

```json
{
  "schema": "items.analysis/v1",
  "message_id": "01J9W4ZB2C4D6E8F0G1H2J3K4M",
  "produced_at": "2026-10-06T09:16:02Z",
  "producer": {"service": "analysis-media", "version": "0.2.0", "job_id": "01M4886GG0GDQ0Y9RD0QSBJD30"},
  "analysis_key": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f:media_ocr:ocr-iq-2026.11",
  "item_id": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f", "item_version": 1,
  "content_hash": "sha256:4b2e…", "input_hash": "sha256:5e19…",
  "platform": "facebook", "kind": "post", "source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566",
  "task": "media_ocr", "model_version": "ocr-iq-2026.11",
  "run_kind": "live", "lane": "priority", "status": "ok",
  "item_fetched_at": "2026-10-06T09:13:58Z",
  "route": "green", "vendor": null, "retention_class": "meta_on_request", "expires_at": null,
  "result": {
    "media": [{
      "index": 0, "type": "image", "sha256": "d41f…a9c2", "reused": false,
      "text": "لا يوجد اتصال بالانترنت", "lang": "ar", "script": "arab",
      "confidence": 0.88, "frames": null, "truncated": false
    }]
  }
}
```

Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

### 6.3 State
Consumer offsets; the url-to-`sha256` lookup via `media_fetch` rows in ClickHouse `analysis`; LRU of recent hashes; re-run progress in `cursors` (`service = analysis-media`, `cursor = rerun:<task>:<model_version>:<last archive object key>`); `service_runs`.

## 7. Limits, quotas and cost

No platform API is called beyond GETs of CDN URLs; no `budget_tag` unless a model API is chosen (`analysis_model_api`, new). Cost is object storage (Backblaze B2 or Hetzner Object Storage), egress, CPU for ffmpeg and the GPU pool, with speech-to-text and video frames dominant. Items a day with media, average duration, frames per video and bytes per item are to be measured in the pilot; TikTok, Instagram and Facebook are the media-heavy platforms at 7.5M, 4.5M and 12.0M items a month. Hash deduplication means reposted memes are analysed once. GPU hours and per-item cost in USD are to be measured in the pilot; storage and Hetzner pricing are confirmed at order time. A re-run is bounded by retained media, not by 12 months of text; media cost per re-run follows the same pilot numbers.

## 8. Failure handling and fallback

- URL expired, refused or login-gated: `media_unavailable`, 5 attempts, then a recorded result; no circumvention.
- HTTP 429: backoff with jitter from 30 s to 15 min, then back to the queue with `attempt + 1`; after 5 attempts to `dlq.analysis-media`.
- Corrupt or unsupported file: `status = skipped`, `reason = unsupported_media`.
- GPU pool down: priority first; heavy video ASR waits; image tasks continue on CPU only if the pilot shows a path meeting the target; otherwise they wait. No weaker fallback model.
- Storage unavailable: the item waits; offsets are not committed.

## 9. Non-functional requirements

- Throughput: about 12 items a second average at full scale, of which the share with media is to be measured in the pilot; per-task rates to be measured in the pilot.
- Latency: priority first pass p95 below 15 minutes; others to be set in the pilot.
- Idempotency: key `item_id` + `task` + `model_version`; `media/<sha256>` is content-addressed so storing twice is harmless; same input twice gives one row; a new version adds a row.
- Scaling: separate worker pools per task, each on its own queue depth; re-run pools separate.
- Data protection: no face recognition, no voice prints, no person attributes; the tag vocabulary excludes people, crowds and events. Individuals are not profiled and protected attributes (religion, ethnicity, political affiliation, health) are never inferred. YouTube data is never used to profile on protected attributes; X data is never used for sensitive-attribute profiling. Media objects and OCR text and transcripts inherit the item's retention class and are deleted with the item; no media content or text in logs.

## 10. Metrics and alerts

Prometheus: `media_items_in_total`, `media_out_total{task,result}`, `media_skipped_total{reason}`, `media_fetch_failures_total{status}`, `analysis_latency_seconds{task,lane}`, `frames_sampled_total`, `asr_audio_seconds_total`, `reuse_ratio`, `storage_bytes`, `rerun_progress`, `dlq_total`. Alerts: priority p95 above 15 minutes; `media_unavailable` share rising; skipped share beyond the pilot band; DLQ entry; storage growth beyond forecast.

## 11. Dependencies

normalize-item (`media[]`), lang-dialect-id (transcript language), keyword-matcher (hits that revive skipped items), analysis-entities (brand ids for logos, optional), raw-archiver, store-writer, aggregator, alert-evaluator, retention-purger and deletion-propagator (media objects), Redpanda, Supabase Postgres, ClickHouse, object storage, Hetzner GPU pool or model API, Hugging Face, `listening-sdk`.

## 12. Risks and mitigations

- Cost of video: sampling caps, tier rules, hash reuse, pilot measurement before scale.
- Dialect ASR errors invent words: confidence kept per segment, low confidence flagged, word error rate per dialect gated at promotion.
- Platform terms on storing media (Meta, TikTok vendor routes, YouTube): media follows item retention; TikTok vendor media stays on amber routes; legal review (question 2).
- Logo false positives embarrass a client: per-brand thresholds, human confirmation queue.
- Scope creep into people analysis: vocabulary whitelist and the exclusions in 3.

## 13. Acceptance criteria

1. An image fixture yields `media_fetch`, `media_ocr`, `media_tags` messages with the file stored at `media/<sha256>` and a `model_version` per task.
2. Two items sharing the same image bytes store one object and analyse once; the second message has `reused = true`.
3. A video fixture is sampled within the frame and duration caps, `truncated` is set when cut, and `media_asr` carries timed segments.
4. A tier-3 item without a hit is skipped with `reason = low_priority_source`; a later hit enqueues and analyses it.
5. A fixture with a client's reference logo returns `brand_id`, score and box; a look-alike returns none at the shipped threshold.
6. A YouTube item produces thumbnail OCR only and no audio or video download.
7. An expired URL gives `media_unavailable` after 5 attempts, with no proxy or account used.
8. A re-run of one archived day reads media from `media/<sha256>`, writes `run_kind = rerun` rows for items still in ClickHouse and none for deleted items.
9. A `deletions` message removes the item's OCR text, transcript and, when no live item references it, the media object.
10. At 12 items a second with a media mix for 30 minutes, priority first-pass p95 stays below 15 minutes.
11. No output contains a face box, a voice identity or a person tag.

## 14. Open questions

1. Which OCR engine and which ASR baseline win on the Iraqi sets; is a Sorani ASR viable?
2. May platform media be stored under each platform's terms and each vendor contract, and is thumbnail-only right for YouTube? Legal to confirm.
3. Where does the url-to-hash and reference-count index live, and how does retention-purger find unreferenced `media/<sha256>`?
4. Should OCR text and transcripts feed analysis-sentiment, analysis-topics and analysis-entities in a second pass?
5. GPU pool or model API per task?
6. Frame interval, frame cap, duration cap and the tier rules: values from the pilot.
7. Do clients upload logo sets themselves, and who approves them?
