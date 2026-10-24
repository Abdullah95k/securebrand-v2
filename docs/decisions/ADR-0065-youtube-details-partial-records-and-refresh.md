# ADR-0065 · YouTube details, partial records and refresh

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, normalize-item, registry-writer, store-writer, search-hit-router, quota-governor, qualifier, comment-decay-scheduler, youtube (yt-keyword-search, yt-web-search-bridge, yt-channel-resolver, yt-pubsub-receiver, yt-uploads-reconciler, yt-video-details-fetcher, yt-comments-fetcher, yt-replies-fetcher, yt-text-purger)
Source: D2-Q065 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

- Details jobs (CF-083, AU-101): yt-video-details-fetcher reads `post_ref` as one id and marks backfill ids `series_step = backfill` (`§6.1 L86`, `§5.1 L44`); yt-pubsub-receiver sends one id (`§6.2 L127`), yt-uploads-reconciler lists of up to 50 with `origin_kind` (`§6.2 L133`), yt-keyword-search every id of a run in one message (`§5.2 L59`), yt-web-search-bridge lists with `origin = web_bridge` on a `list` bucket that does not exist (`§6.2 L126`, `§7 L137`; `CONVENTIONS L279`).
- Partial records (AU-051): three PRDs expect normalize-item to hold `partial: true` records until the details record (`yt-pubsub-receiver §6.2 L124`, `yt-keyword-search §6.2 L123`, `yt-video-details-fetcher §4 L33`); normalize-item has no hold and maps only the three fetchers (`§5.2 L52`, `§5.3 L71`).
- Playlist id (AU-027): yt-uploads-reconciler selects only channels with a stored uploads playlist id (`§5.1 L43`); yt-channel-resolver returns it and says registry-writer stores it (`yt-channel-resolver §6.2 L126`, `§6.3 L138`); no column exists (`registry-writer §5.3 L68`), so no channel is reconciled.
- Cadence (AU-100): an unsubscribed channel keeps its reach-tier cadence, dormant weekly (`yt-pubsub-receiver §5.1 L40`), against one daily read for every channel (`yt-uploads-reconciler §5.1 L45`, `§14 Q3 L200`).
- Refresh (AU-102): no fetcher accepts yt-text-purger's `refresh` jobs (`§5.3 L96` to `L102`), and normalize-item turns an unchanged re-read into metrics only (`§5.2 L52`), so the 30-day clock never resets.

At stake: as written, YouTube reconciles no channel, parks or double-publishes every video, and spends refresh quota that resets nothing.

Settles: CF-083, AU-027, AU-051, AU-100, AU-101, AU-102, yt-text-purger §14 Q2, yt-uploads-reconciler §14 Q3, yt-video-details-fetcher §14 Q2.
Depends on: ADR-0007 and ADR-0008 (key and kind), ADR-0012 (producer rows), ADR-0013 (registry columns), ADR-0018 (priority), ADR-0049 (push coverage), ADR-0056 (who gets the refresh).

## Options

1. **One video per job, partial versions, a registry column, tier cadence when push fails, refresh as a version** (chosen): its rules are under Decision.
2. **The YouTube PRDs as written: lists of up to 50 ids, and a hold in normalize-item with a timeout** (CF-083 option 2, AU-051 option 1). Consequences: one version per video, but dedup, retries and the DLQ work per id inside a message, one bad id retries 49 others, and normalize-item gains held state.
3. **Refresh as a store-side update** (AU-102 option 2): the fetcher reports refreshed ids and `fetched_at` moves without a new version. Consequences: no reprocessing of unchanged text, but a second write path into ClickHouse beside store-writer's item flow.
4. **One daily read for every channel without a working subscription** (AU-100 option 2). Consequences: 1 unit a channel a day whatever its tier, but a Tier 1 channel whose subscription failed can be 24 hours stale until ops repairs it.

## Decision

Every job on `jobs.yt-video-details-fetcher` carries one video, and only the consumer's collector batches; a finder's record is a partial version that the details record completes; `sources.platform_meta` holds the uploads playlist id; a channel whose own subscription failed is read at its tier's cadence; a refresh re-read is a new version, which resets the 30-day clock.

- a) Every job on `jobs.yt-video-details-fetcher` carries one video in `post_ref` (ADR-0011); producers split their lists, and only the consumer's collector batches (`yt-video-details-fetcher §5.1 L48`), 50 ids for 1 unit (`CONVENTIONS L205`). `first_sight` (a producer row for the four finders, ADR-0012) carries `origin_kind`, the kind of the job that found the id; the SDK derives priority from it (`backfill` 5, otherwise 1, ADR-0018), so `series_step = backfill` and `origin` go. The bridge's `list` bucket is `ingest`.
- b) A finder's record is version 1, keyed `youtube:video:<videoId>` with kind `video` (ADR-0007, ADR-0008) and `partial: true` in its `context` (ADR-0005), through a normalize-item mapper per finder; the details record is the next version of the same key, published even when the content hash is equal because the stored version is partial. No hold: a stalled details fetcher leaves partial videos visible, not missing. The proposal wrote this key as `youtube:post:<id>` with kind `post` (D2-PROPOSALS L2010); ADR-0007 and ADR-0008 make every YouTube video `youtube:video:` with kind `video`, as recorded here.
- c) `sources` gains `platform_meta` (jsonb, typed per platform in F2; YouTube: `uploads_playlist_id`), written only by registry-writer from the decision carrying yt-channel-resolver's profile; copied, never derived (`yt-channel-resolver §5.2 L62`).
- d) A channel whose own subscription failed loses push coverage (yt-pubsub-receiver's decision, ADR-0013, ADR-0049) and is read at its reach-tier cadence (`CONVENTIONS L45` to `L47`), with `subscription_failed` to ops (`yt-pubsub-receiver §8 L145`); a hub-wide failure moves no channel, so all stay daily while ops decides (`§8 L146`); dormant channels are read weekly (`CONVENTIONS L49`). Quota: an hourly read costs 24 `playlistItems.list` units a channel a day against 1 (`CONVENTIONS L204`); at the 99% verified-lease target (`yt-pubsub-receiver §2 L13`), even an all-Tier-1 worst case adds at most 0.23 units per registered channel a day (1% of channel-days × 23), under a quarter of the 1 unit per channel that daily reconciliation already costs.
- e) yt-text-purger is the named producer of `refresh` on the three YouTube queues (ADR-0012), with `post_ref` (and its `thread_ids`), `run_id`, `must_finish_by` and `refresh_for_client_ids`, one video per job. The fetcher re-reads what is listed and writes every returned item, changed or not, with `job_kind = refresh`; normalize-item publishes each as a new version with the new `fetched_at` even when the hash is equal, which resets the clock (`yt-text-purger §5.3 L102`). Who gets refresh is ADR-0056's.

It also answers: The `series_step` values on `jobs.yt-video-details-fetcher` are those of ADR-0034 (`+24h`, `+7d`, `refresh:<request_id>`); a backfilled first sight is marked by `job_kind = backfill`, not by a step (`yt-video-details-fetcher §14 Q2`).

Why: One id per job keeps the queue contract simple while the collector still pays 1 unit per 50 ids; a partial version fails visibly; the playlist id sits with the identity columns its one writer owns; one failed subscription should not quietly break a tier's freshness promise at so small a cost; and a refresh that creates no version cannot reset the clock.

## Consequences

The approved yt-keyword-search, yt-web-search-bridge, normalize-item and registry-writer move under ADR-0001; normalize-item's equal-hash rule gains two named exceptions (completing a partial version, a refresh); F3 adds `platform_meta`.

- CONVENTIONS v1.1: `platform_meta` among the registry columns (v1 L36); `first_sight` and `refresh` (v1 L277); no `list` bucket (v1 L279); lost push coverage means the tier's cadence, dormant weekly (v1 L48, L49); a refresh is a new version (v1 L76).
- F2 types `platform_meta` per platform; F3 adds the column.

Sessions that must read this: F2, F3, then C1, C4, C6, C7, C9, C11, YT1, YT2, YT3, YT4, YT5, YT6, YT7, YT8, YT9.
