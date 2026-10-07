# ADR-0015 · Rotation state per service

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: listening-sdk (F5), and the lanes Discover and qualify and Fetch posts (every rotating service)
Source: D2-Q015 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS gives each source one `next_poll_at` and one `last_polled_at` (L36), says "the scheduler keeps `next_poll_at` per source" (L51), and has every rotating service run its own leader-elected scheduler (L278). Several services rotate the same row at different intervals (CF-031): news-feed-poller every 5 to 15 minutes for hot sites and news-sitemap-poller hourly on the same sites (`news-feed-poller §5.1 L42`, `L44`; `news-sitemap-poller §5.1 L45`); the three web engines on the same keyword-rule rows (`web-search-perplexity §5.1 L41`, `L42`); Instagram accounts and hashtags (`ig-mentions-fetcher §5.1 L41`; `ig-hashtag-search §5.1 L57`); Telegram bot channels (`tg-bot-channel-receiver §5.1 L44`; `tg-channel-posts-poller §5.1 L44`); and yt-pubsub-receiver expects registry-writer to set a channel's `next_poll_at` to now (`yt-pubsub-receiver §5.1 L42`). Three services already keep their due time in `cursors` (`ig-mentions-fetcher §5.1 L45`, `ig-keyword-search §5.1 L45`, `fb-page-search §5.1 L42`), while the SDK's rotation helper reads `sources.next_poll_at` (CF-114). ig-hashtag-search's jobs come from "the shared scheduler" (`ig-hashtag-search §5.1 L45`), which no PRD defines (AU-088). At stake: whichever service finishes last sets the next run of the others, and `last_polled_at` means "some service polled".

Settles: CF-031, CF-114, AU-088.
Depends on: ADR-0041 (the `cursors` row), ADR-0049 (the cadence table per source type).

## Options

1. **Each service schedules itself from its own row in `cursors`** (chosen): its rules are under Decision.
2. **One `sources.next_poll_at` with one owner per source type, the others deriving their schedule from it (CF-031 option 2).** Consequences: no new columns, but the secondary services (ig-mentions-fetcher, news-sitemap-poller, the second and third web engines) cannot keep the cadence their PRDs promise.
3. **One registry row per service where several rotate the same thing (CF-031 option 3).** Consequences: each scheduler owns a row, but one news site or Instagram account becomes several sources against the unique `(platform, platform_id)` (`registry-writer §5.3 L70`); for keyword rules, the rows are ADR-0044's.
4. **One shared scheduler component for all rotating services (CF-114 option 2, AU-088 option 2).** Consequences: one place to tune, but a component the build plan gives to no session, a single point of failure for all rotation, and CONVENTIONS L278 rewritten.

## Decision

Each rotating service schedules itself from its own `cursors` row (`next_due_at`, `last_started_at`). `sources.last_polled_at` and `next_poll_at` become a summary written by the primary poller and read by no scheduler, and no service writes another's due time.

Every rotating service runs its own leader-elected loop (CONVENTIONS L278), ig-hashtag-search included; a hashtag's first read is backfill-orchestrator's job (ADR-0020). Its due time and last start live in its own `cursors` row (`next_due_at`, `last_started_at`, ADR-0041, with a scope key per keyword or edge where a service needs one), set from the start of the last run. The SDK's rotation helper reads only these (ordering, `rotation_lag_seconds`, `rotation_behind`); a source with no row is due at once. `sources.last_polled_at` and `next_poll_at` remain a summary for the admin view, written in the same transaction by the primary poller that ADR-0049's cadence table names for the source type; no scheduler selects on them, and no service writes another's due time. Catch-up after a lapsed lease or a failed subscription is event-driven: the `push_coverage_change` event (`reason = lease_lapsed`, ADR-0014) makes yt-uploads-reconciler emit its reconciliation job at once, as `yt-uploads-reconciler §5.1 L51` already describes.

Why: It is what three PRDs already do, it keeps CONVENTIONS' own-scheduler rule, and each service keeps the cadence its PRD promises without overwriting another's.

## Consequences

One helper and one clock per service; F3 adds the two typed columns; the PRDs that schedule on `sources.next_poll_at` move to their own row, among them approved ones (fb-page-feed-poller, whose scheduler is CONVENTIONS' model, ig-hashtag-search, x-recent-search, web-search-perplexity; ADR-0001).

- CONVENTIONS v1.1: the registry columns (`last_polled_at` and `next_poll_at` as a summary), the `cursors` columns (with ADR-0041), the rotation mechanics ("each scheduler keeps its due time per source in its own `cursors` row") and `rotation_lag_seconds`, read from that row.
- ADR-0049's cadence table names the primary poller of each source type.

Sessions that must read this: F3, then F5, C7, C10, FB6, IG2, IG3, IG5, VIG1, TG1, VTG3, YT2, YT3, N3, N4, N5, W1, W2, W4.
