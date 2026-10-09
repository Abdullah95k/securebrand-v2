# ADR-0034 · Engagement observations

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F8, normalize-item, comment-decay-scheduler, store-writer, fb-reactions-fetcher, fb-client-webhook-receiver, ig-account-media-poller, yt-video-details-fetcher, tt-video-stats-refresher, tt-client-videos-fetcher, li-client-posts-poller, li-notification-receiver, li-own-comments-fetcher
Source: D2-Q034 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS refreshes counts at +24 h and +7 d "by the source's metrics or details service, or by the next poll where the API returns counts with the post" (L65). normalize-item emits "one `item.metrics` observation per record that carries counts" (`normalize-item §5.2 L56`); fb-reactions-fetcher, an approved PRD, emits another for every green Facebook post it reads on `raw.items` (`fb-reactions-fetcher §5.1 L39`), and yt-video-details-fetcher writes a `first_sight` observation "from the same response" as its record (`yt-video-details-fetcher §3 L19`), so one fetch yields two observations (CF-018 b). No PRD commits to the LinkedIn counts that li-notification-receiver and li-own-comments-fetcher read (CF-018 c). The messages have two layouts, `observation` as a string or an object, and no `item_id`, while store-writer keys `metrics_timeseries` on `item_id, observed_at` (`store-writer §5.3 L62`; CF-019). Jobs and labels differ: comment-decay-scheduler emits `kind = metrics` with `+24h` and `+7d` counted from first sight (`comment-decay-scheduler §5.1 L60`, `L68`); fb-reactions-fetcher expects `refresh_24h` and `refresh_7d` due at `created_time` plus the step (`fb-reactions-fetcher §5.1 L41`); yt-video-details-fetcher expects `24h` and `7d` from `publishedAt` (`yt-video-details-fetcher §5.1 L45`); the TikTok services label `plus_24h` (CF-081, AU-031). `webhook_reconcile` has no producer (AU-084), and li-notification-receiver asks whether reaction events become counter increments (`li-notification-receiver §14 Q4 L201`; AU-004). What is at stake: double-counted growth curves and refresh jobs nobody accepts.

Settles: CF-018, CF-019, CF-081, AU-004, AU-031, AU-084, fb-reactions-fetcher §14 Q1, ig-account-media-poller §14 Q3, li-notification-receiver §14 Q4, store-writer §14 Q5, tt-video-stats-refresher §14 Q2, tt-video-stats-refresher §14 Q4.
Depends on: ADR-0005 (`job_kind` on the raw envelope), ADR-0008 (the archive-only `metrics` kind).

## Options

1. **One observation per read, from one writer; one flat message; steps counted from the post's creation time** (chosen): its rules are under Decision.
2. **Every count read goes through `raw.items`, and normalize-item writes all of `item.metrics` (CF-019 option 3).** Consequences: one writer and one shape, but count-only responses become records normalize-item must map, against ADR-0008's archive-only `metrics` kind, and four services are rebuilt as raw producers.
3. **As option 1, but counted from first sight, as comment-decay-scheduler and the TikTok services write.** Consequences: one clock in the scheduler, but a post first seen at 20 hours gets its "+24 h" point at 44 hours, so 24-hour and 7-day engagement cannot be compared across routes; fb-reactions-fetcher and yt-video-details-fetcher change instead.
4. **Both writers kept, store-writer keeping one row per item, time and label (CF-018 option 3).** Consequences: no writer changes, but growth curves still need de-duplication by label at read time.

## Decision

Each read gives one engagement observation from one writer: normalize-item for reads whose records become items, the reading service for reads made only to observe counts. `item.metrics/v1` is one flat message with a closed label list, and the metrics lane counts its +24 h and +7 d steps from the post's creation time.

- Writers. A read whose records go to `raw.items` as items (polls, searches, backfills, pushes, first-sight details reads) gets its observation from normalize-item, labelled from the envelope's `job_kind` (ADR-0005). A read made only to observe counts (a `metrics` job, a client refresh, tt-client-videos-fetcher's +24 h and +7 d, ADR-0024) is written by the reading service, which writes no item record for it and may archive the response as the archive-only kind `metrics` (ADR-0008). So fb-reactions-fetcher drops its extract mode and its `refresh_*` kinds, yt-video-details-fetcher drops its `first_sight` observation, and ig-account-media-poller writes the observation for a `metrics` job's posts instead of re-emitting them (`ig-account-media-poller §5.1 L52`). normalize-item's LinkedIn mapper names the count fields of li-client-posts-poller's records, which makes it the producer of LinkedIn counts. A record that carries no counts, such as a Page webhook's change value (`fb-client-webhook-receiver §6.2 L129`), gives no observation (AU-084).
- `item.metrics/v1`, flat: ADR-0002's metadata, `item_id`, the item's `idempotency_key`, `platform`, `platform_id`, `source_id`, `created_at` (the post's creation time), `observation {label, step, observed_at}`, `metrics {views, likes, comments, shares, reactions_by_type}` (null where a platform has none), provenance and `retention_class` (ADR-0003), so store-writer needs no lookup (`store-writer §14 Q5 L185`). Route extras (`channel_id`, `live_state`, `regressed`) are optional declared fields; `age_seconds` and `lateness_seconds` are derived by readers.
- Labels, closed: `first_sight` (an item's first observation), `poll`, `backfill`, `refresh` (`step` `+24h`, `+7d` or `refresh:<request_id>`), `ops_force`, `live_end`; `webhook_reconcile`, `refresh_24h`, `refresh_7d`, `refresh_client`, `plus_24h`, `24h` and `7d` go. normalize-item stamps `observed_at` with the record's `fetched_at`, so a replay rewrites the same row; a metrics service checks (`item_id`, `step`) before it calls, so a replayed job writes nothing new.
- Jobs: `kind = metrics` with `post_ref` (ADR-0011) and `series_step` `+24h`, `+7d` or `refresh:<request_id>`, emitted by comment-decay-scheduler only (ADR-0012). The metrics lane counts from the platform's creation time, so "engagement at 24 h" is the same post age on every platform; a step already past at first sight is skipped. The comment lane keeps first sight (ADR-0060).
- LinkedIn: absolute observations only; reaction events produce no counter increments.

It also answers: `item.metrics` carries `source_id` (its partition key) and the item's `created_at`, so store-writer needs no lookup (`store-writer §14 Q5`); `saves` is an optional count where the platform returns it (`tt-video-stats-refresher §14 Q4`).

Why: It removes the duplicate without moving work: polls already carry counts into normalize-item, and only the services that make count-only calls write their own. Counting steps from creation time is what makes the 24-hour and 7-day views comparable.

## Consequences

One row per read in `metrics_timeseries`; approved PRDs move under ADR-0001 (fb-reactions-fetcher, normalize-item's LinkedIn mapper); the hourly first-day Facebook series comes from normalize-item's metrics-only outcomes on each re-poll (`normalize-item §5.2 L52`); comment-decay-scheduler keeps two anchors; tt-video-stats-refresher and tt-client-videos-fetcher move from first sight to creation time.

- CONVENTIONS v1.1: the `item.metrics` message (v1 L23); who writes which observation, and the creation-time anchor of the +24 h and +7 d steps (v1 L65); the steps of a `metrics` job (v1 L277).
- F2 types `item.metrics/v1` and the closed label list; F8 keys `metrics_timeseries` on (`item_id`, `observed_at`), as store-writer does.
- The engagement-spike alerts of ADR-0048 read the velocity of these observations.

Sessions that must read this: F2, F8, C4, C6, C11, FB2, FB4, FB7, IG3, TT1, VTT6, LI1, LI2, LI3, VTG3, YT4.
