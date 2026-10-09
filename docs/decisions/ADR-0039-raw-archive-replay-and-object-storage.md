# ADR-0039 · Raw archive, replay and object storage

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F8, listening-sdk (F4, F6), raw-archiver, normalize-item, analysis-sentiment, analysis-topics, analysis-entities, analysis-media, x-compliance-sync, registry-writer, web-commoncrawl-scanner, deletion-propagator, news-article-extractor, news-comments-fetcher
Source: D2-Q039 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

raw-archiver owns a replay topic `raw.replay` that no PRD consumes (`raw-archiver §3 L22`, `§5.3 L71`, `§6.2 L96`). normalize-item replays by reading `raw/` objects on a `replay` job (`normalize-item §5.1 L45`), which skips raw-archiver's deletion and class-clock checks, while raw-archiver proposes the topic as the main path (`raw-archiver §14 Q2 L182`; CF-026, AU-072). The four analysis services re-run from a Parquet archive of normalized items (`analysis-sentiment §5.1 L51`) that raw-archiver does not write: its `archive/` holds `raw.items` envelopes and payloads (`raw-archiver §5.3 L67`; AU-010). Several prefixes have a second writer (CF-053): analysis-media writes `media/<sha256>` directly, without the `.refs` list deletions rely on (`analysis-media §5.2 L52`, `raw-archiver §5.3 L69`; AU-025); x-compliance-sync stores evidence files under `raw/` (`x-compliance-sync §5.2 L56`); web-commoncrawl-scanner writes there directly (AU-029); registry-writer exports `registry_audit` under `archive/registry/` (`registry-writer §12 L140`); two news services write under `cache/news/` (ADR-0022); and batch numbers differ in width (`raw-archiver §14 Q1 L181`). x-compliance-sync expects an archive index by X post and author id that raw-archiver does not keep (`x-compliance-sync §5.1 L43`, `raw-archiver §5.4 L86`; AU-073). What is at stake: replays that bring deleted items back, foreign files compacted as if they were items, and media that outlives its item.

Settles: CF-026, CF-053, AU-010, AU-025, AU-072, AU-073, analysis-media §14 Q3, raw-archiver §14 Q1, raw-archiver §14 Q2, yt-text-purger §14 Q4.
Depends on: ADR-0012 (who writes `replay` jobs), ADR-0022 (the news cache prefixes), ADR-0035 (the deletion guard).

## Options

1. **One replay path through raw-archiver's reader, no normalized archive, one owner per prefix** (chosen): its rules are under Decision.
2. **`raw.replay` as the one replay path, read by normalize-item and the analysis services, plus a Parquet archive of normalized items written by raw-archiver from `items.normalized` (CF-026 option 1, AU-010 option 1).** Consequences: the replay guards stay as written, but a second archive must be compacted, purged and rewritten on every deletion, and two services gain a topic.
3. **Shared prefixes, every writer registering its objects in the manifests and the purge registry, plus an id index in raw-archiver (CF-053 option 3, AU-073 option 1).** Consequences: fewer moves, but compaction and integrity checks must tell foreign files from items, and the index is one more store deletions must reach.

## Decision

There is one guarded way back into the pipeline, a `replay` job on normalize-item that reads through raw-archiver, with no `raw.replay` topic and no Parquet archive of normalized items in v1; every object-storage prefix has one writer.

- Replay: no `raw.replay` topic. A replay is a `replay` job on `jobs.normalize-item`, written by the admin API (ADR-0012). normalize-item's worker takes the plan (objects, counts, `run_id`) from raw-archiver's replay API and reads each object through raw-archiver's read endpoint, which drops records of items with an open deletion or a tombstone and records past their class clock; the rate cap and progress stay as written. Replayed items reach keyword-matcher, store-writer and the analysis services on `items.normalized` as new versions; `target = analysis` goes.
- No Parquet archive of normalized items in v1: analysis re-runs (`kind = rerun`) read ClickHouse `items` and `comments`, and `hits` for the matched keyword, while the text is retained; older content returns through a replay.
- Prefixes, one writer each. `raw/` (batches, manifests, `raw/_quarantine/`) and `archive/` (Parquet of `raw.items`): raw-archiver only, with six-digit batch numbers fixed in listening-sdk. `media/<sha256>` and `.refs`: only through raw-archiver's media endpoint, analysis-media included. `cache/news/`: news-article-extractor; `cache/news/comments/`: news-comments-fetcher (ADR-0022). `models/<task>/<model_version>/`: the analysis services' release step (ADR-0023). `audit/x-compliance-sync/<yyyy>/<mm>/<dd>/<run_id>.jsonl.zst`: x-compliance-sync's evidence, moved out of `raw/`. `audit/registry-writer/<yyyy>/<mm>/`: registry-writer's export, moved out of `archive/`. web-commoncrawl-scanner writes through `raw.items` (ADR-0037). deletion-propagator reaches `raw/`, `archive/` and `media/` through raw-archiver's rewrite and media endpoints and the caches through the purge registry (ADR-0035); the `audit/` prefixes are kept as long as ADR-0069 decides for audit records.
- Lookups by X id: no archive index. x-compliance-sync takes post ids from ClickHouse `items` and `comments`, whose rows carry `raw_ref` to the archived copy, and user ids from `sources.platform_id`; individuals keep only `author_ref` (ADR-0010), so their content is checked through the posts job; ids found only in batches parked as `schema_unknown` come from scanning the parked objects that `review_queue` lists (`normalize-item §8 L132`).

It also answers: YouTube payloads are archived with their text and rewritten when the 30-day clock removes it, as raw-archiver's purge path does for every class (`yt-text-purger §14 Q4`); the batch number in `raw_ref` is six digits, an SDK constant (`raw-archiver §14 Q1`).

Why: It keeps one copy of what was fetched and one way back into the pipeline, both guarded by the archive's owner; ClickHouse already holds what re-runs read; and every object in storage has one owner who answers for its lifetime.

## Consequences

One guarded way back into the pipeline; raw-archiver gains a read endpoint and loses the topic; normalize-item reads through raw-archiver rather than the bucket, and its line on a normalized Parquet (`normalize-item §4 L33`) goes, and registry-writer exports to its own prefix (both approved PRDs move under ADR-0001); the analysis services' re-run lines and x-compliance-sync's evidence path change; deletion-propagator's `raw.replay` wording becomes "a replayed record".

- CONVENTIONS v1.1: the object-storage line (v1 L31) becomes a prefix table with one owner each; the topic list (v1 L14 to L29) has no `raw.replay`.
- F4 and F6 fix the six-digit batch number; raw-archiver builds the read and media endpoints; the `audit/` prefixes are kept as long as ADR-0069 sets for audit records.

Sessions that must read this: F2, F8, F4, F6, C2, C4, C5, C6, C7, C13, C14, A1, A2, A3, A4, X7, N6, N8, W5.
