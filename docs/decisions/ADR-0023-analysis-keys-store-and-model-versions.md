# ADR-0023 · Analysis keys, store and model versions

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, F8, analysis-sentiment, analysis-topics, analysis-entities, analysis-media, store-writer, aggregator, alert-evaluator
Source: D2-Q023 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

README decision 7 proposes "a priority lane per task (`jobs.analysis-<task>.priority`) for tier-1 sources; `items.analysis/v1` keyed by `item_id:task:model_version` with an `input_hash`; budget tag `analysis_model_api` if a hosted model is chosen; YouTube audio and video are not downloaded in v1 (thumbnails only), pending legal review" (`README L184`). D1 found no conflict on thumbnails, and these elsewhere:

- lanes (CF-075 d): every analysis PRD has one priority lane per service, analysis-media's five tasks sharing `jobs.analysis-media.priority` (`analysis-media §5.1 L43`, `§6.2 L87`) and analysis-sentiment's two sharing `jobs.analysis-sentiment.priority` (`analysis-sentiment §6.1 L85`, `§6.2 L89`);
- the key (CF-075 b, CF-017 a): analysis-topics sends one message per taxonomy with `task = topics:<taxonomy_id>`, so its key has four colon-separated parts (`analysis-topics §5.2 L60`, `§6.2 L101`);
- the store (CF-017 c, CF-050, AU-023): store-writer keys `analysis` on `item_id, model`, versions it by `analyzed_at`, lets "a newer model version" replace the older, and reads `model` and `output`, which no writer sends (`store-writer §5.3 L61`, `L67`); its monthly partitions on `analyzed_at` never merge a re-score with the older row; the analysis PRDs keep re-runs "beside the old" until switch-over (`analysis-sentiment §5.1 L51`);
- `model_versions` (CF-058): four PRDs name parts of it (statuses, `analysis-sentiment §5.3 L76`; `thresholds`, `analysis-topics §5.3 L72`; one per media task, `analysis-media §5.3 L74`) and none a key, while aggregator, which should follow a switch-over, reads neither it nor more than "the latest `analysis` row per item and model" (`aggregator §5.3 L53`, `§6.1 L74`); topic ids are `node_id` in the message and `topic_id` in aggregator's grain (`analysis-topics §6.2 L111`, `aggregator §5.3 L55`).

At stake: rows of different tasks collapsing into one, and switch-overs that cannot be undone.

Settles: RD-7, CF-017, CF-050, CF-058, CF-075, AU-023, analysis-entities §14 Q1, analysis-media §14 Q4, analysis-sentiment §14 Q6, analysis-topics §14 Q5.
Depends on: ADR-0042 (the `analysis_model_api` tag), ADR-0068 (the legal basis for platform media).

## Options

1. **The README's key and versioning, with lanes per service** (chosen): its rules are under Decision.
2. **README decision 7 literally: a lane per task, `jobs.analysis-<task>.priority`.** Consequences: matches the README, but analysis-media goes from two queues to ten (five tasks, two lanes each), task names must lose their colon to be valid topic names, and every analysis PRD's queue names change, for no gain over per-task worker pools.
3. **store-writer's design kept: its names become the message (CF-017 option 2) and the newest version replaces the older (CF-075 option 1, AU-023 option 2).** Consequences: fewer edits on the store side, but no side-by-side re-run, and a switch-over becomes an overwrite that cannot be rolled back.

## Decision

README decision 7's key and versioning stand, with one priority lane per analysis service: `items.analysis` is keyed `item_id:task:model_version` with an `input_hash`, re-runs sit beside live rows in ClickHouse `analysis`, and `model_versions` names the one active version per task, which every reader takes.

- Lanes: `jobs.<service>.priority` and `jobs.<service>` for each analysis service, with tier 1 and client priority lists on the priority lane and push-covered sources by their tier (ADR-0049); a service with several tasks keeps a worker pool per task, as analysis-media does so that "slow video ASR never blocks image OCR" (`analysis-media §5.1 L43`).
- Message: `analysis_key = item_id:task:model_version` with `input_hash`, plus `item_id`, `task` and `model_version` as separate fields, so nobody splits the string; task names contain no colon (`topics.<taxonomy_id>`); partitioned by `source_id` (ADR-0004); the item's `created_at` added as `item_created_at`.
- ClickHouse `analysis` (store-writer): sorting key (`item_id`, `task`, `model_version`), version `produced_at`, partitioned by the item's `created_at` month like `items` (CF-050 option 1); columns named as in the message (`task`, `model_version`, `result`, `produced_at`); typed projections kept, entity ids among them, with no separate entity table (AU-023 c). Re-runs sit beside live rows.
- `model_versions`: one row per (`task`, `model_version`) with `service`, `status` (`candidate`, `shadow`, `active`, `retired`), `thresholds` (jsonb), the artefact path under `models/`, the evaluation report and dates; at most one `active` row per task; written by each analysis service's release step, a switch-over being one status change (`analysis-sentiment §5.3 L76`). aggregator, and every other reader of `analysis`, takes the active version per task.
- Topic ids: one field, `topic_id`, holding the `taxonomy_nodes` id namespaced by taxonomy (ADR-0048).
- `analysis_model_api` joins the canonical tags (ADR-0042), used only if A1 to A4 choose a hosted model. Media: YouTube stays thumbnails only unless the register of permitted uses says otherwise, and other media is downloaded where that register allows it (ADR-0068).
- OCR and transcript text as a second input (`analysis-media §14 Q4 L171`, `analysis-topics §14 Q5 L179`): deferred to A4, as an additive field when it comes.

It also answers: A knowledge-base release is a new `model_version` of analysis-entities, re-run side by side and switched over like any model (`analysis-entities §14 Q1`).

Why: It keeps the README's key, `input_hash` and side-by-side versions, and makes the active version an explicit row that every reader consults; per-service lanes are what the four PRDs specify, with per-task isolation inside the service.

## Consequences

Store-writer and aggregator change columns and reads (C6, C15); analysis-topics renames its task; the README's lane names change; no approved PRD moves.

- CONVENTIONS v1.1: the `items.analysis` key and its fields; the priority lanes `jobs.<service>.priority`; `model_versions` among the control-plane tables; the `analysis` sorting key and partition in the analytics store.
- `DEFERRED.md`: OCR and transcript text as a second input (A4); GPU pool or model API (A1 to A4, build plan L65).

Sessions that must read this: F2, F3, F8, then C6, C15, A1, A2, A3, A4, A5.
