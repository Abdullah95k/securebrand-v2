# ADR-0020 · Backfill

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, listening-sdk (F4, F5), backfill-orchestrator, registry-writer, comment-decay-scheduler, web-commoncrawl-scanner, tg-discussion-receiver, and the lanes Discover and qualify and Fetch posts (every service in the route table)
Source: D2-Q020 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

README decision 4 makes backfill-orchestrator "the single writer of `backfill_status`", ends a failed or slow backfill `capped` with the source entering rotation anyway, and names fb-group-posts-poller the target for Facebook groups (`README L181`); the orchestrator agrees (`backfill-orchestrator §1 L9`, `§5.1 L46`). D1 found:

- other writers (CF-030, AU-017): fb-backfill (approved) sets the status, `next_poll_at`, `notes` and an event (`fb-backfill §5.2 L51`, `L56`), as do tg-channel-posts-poller (`§5.1 L54`) and the TikTok searches (`tt-keyword-search §5.1 L44`, `tt-hashtag-feed-poller §5.1 L48`); registry-writer inserts `pending` and `next_poll_at = now()` (`registry-writer §5.2 L52`) though `§3 L30` gives both to others; the Telegram receivers set `capped` where the orchestrator sets `done` (`tg-bot-channel-receiver §5.1 L50`, `backfill-orchestrator §5.3 L76`);
- routes (CF-088, AU-042): six services wait for a job the route table never sends, since keyword rules and hashtags get "`done` at once" (`backfill-orchestrator §5.3 L79`); three backfill on their own first run (`tg-message-search §5.1 L44` and the TikTok searches); the news row names news-feed-poller, which takes no backfill;
- job and report (AU-043, AU-017): `run_id` and `cap` (`backfill-orchestrator §6.2 L106`) against `window_start`, `window_end` and `reason` (`fb-backfill §5.1 L41`); the orchestrator waits for `oldest_item_at` and `capped_reason` (`backfill-orchestrator §5.4 L92`), which no service sends;
- sequencing (AU-046, AU-047): ig-account-resolver expects the orchestrator to wait for a tier (`ig-account-resolver §5.1 L52`); a re-added retired source emits both `updated` and `added` (`registry-writer §5.2 L52`), and a second `initial` run repeats the first job id (`backfill-orchestrator §5.3 L85`).

At stake: sources that never get the history their PRDs promise, and rotation started or held by the wrong writer.

Settles: RD-4, CF-030, CF-088, AU-017, AU-042, AU-043, AU-046, AU-047, backfill-orchestrator §14 Q1, backfill-orchestrator §14 Q2, registry-writer §14 Q2.
Depends on: ADR-0014 (the re-add event), ADR-0015 (hand-over without `next_poll_at`), ADR-0017 (the report), ADR-0059 (X keyword rules and news sites).

## Options

1. **README decision 4, completed** (chosen): its rules are under Decision.
2. **The executing service writes the transitions; the orchestrator only emits and enforces the deadline (CF-030 option 2).** Consequences: matches fb-backfill as written, but a service's `done` races the deadline `capped`, and every target carries the state machine.
3. **Self-backfill on the first run for keyword rules and hashtags, orchestrator jobs for the rest (CF-088 option 3, AU-042 option 3).** Consequences: no job for the searches, but their deep first run is paid at rotation priority, outside the orchestrator's cap and report.
4. **The route table as written: keyword rules and hashtags get no history (AU-042 option 2).** Consequences: the cheapest, but six PRDs drop a promised feature.

## Decision

README decision 4 stands, completed: backfill-orchestrator writes every `backfill_status` transition, from one job schema and one report on `jobs.completed`; the route table names a target for every source type; no service backfills on its own first run; a slow or failed backfill ends `capped` and never holds a source out of rotation.

- Status: backfill-orchestrator writes every transition; `pending` is the column default, so registry-writer writes neither it nor `next_poll_at`; executing services only report. A route with no history ends `capped` at once with `capped_reason = no_history`. `capped_reason` is closed: `route_cap`, `budget`, `deadline`, `failed`, `no_history`, `flag_off`; reasons live in `backfill_runs`, not `sources.notes`.
- Route table: Facebook Page fb-backfill, group fb-group-posts-poller, keyword rule fb-keyword-search; Instagram account ig-account-media-poller, plus ig-mentions-fetcher for a client-owned one (the status waits for both jobs), hashtag ig-hashtag-search, keyword rule ig-keyword-search; TikTok creator tt-profile-videos-poller, client account tt-client-videos-fetcher, keyword rule tt-keyword-search, hashtag tt-hashtag-feed-poller; X account x-full-archive-search; LinkedIn client page li-client-posts-poller, amber page li-company-posts-poller, keyword rule li-post-search; Telegram channel tg-channel-posts-poller, keyword set tg-message-search; YouTube channel yt-uploads-reconciler, and a term promoted to tier 1 yt-keyword-search (`yt-keyword-search §5.1 L51`). X keyword rule: x-full-archive-search, through an automatic `keyword_history` job of 90 days rather than a `backfill` job, since ADR-0064 keeps that kind apart (ADR-0059). News site: news-sitemap-poller, from the site's regular sitemaps; for the part of the 90 days its sitemaps do not reach, or for a site with none, web-commoncrawl-scanner lists the host's captured article URLs from the Common Crawl index (ADR-0059); the status waits for both jobs. None (`no_history`): Telegram own channels, web engine rules, yt-web-search-bridge rules. No service backfills on its own first run (tt-keyword-search, tt-hashtag-feed-poller and tg-message-search, all approved, move under ADR-0001); a first rotation reads from an empty cursor.
- One job: ADR-0011's envelope with `kind = backfill`, `run_id`, `reason` (`add`, `client`, `ops`), `window_start`, `window_end` and `cap {max_age_days, max_items}`. An initial window ends at emission and starts the route's age cap earlier (at most 90 days), as `fb-backfill §3 L20` reads; a re-run carries an explicit window, clipped to 90 days except where the route's PRD allows more on a client's request (`x-full-archive-search §2 L13`).
- One report: `jobs.completed` (ADR-0017) with status `done` or `capped`, `capped_reason`, `oldest_item_at` and the counts; the orchestrator writes the status from it, or `capped` on its deadline or the DLQ. The hand-over writes nothing else: a source with no rotation row is due at once (ADR-0015), and backfill services stop seeding the pollers' cursors (ADR-0041).
- Sequencing: a run waits in `pending` until the source has a tier (the `updated` event that brings one). A re-added retired source arrives as one `updated` event with `previous.lifecycle = retired` (ADR-0014); the orchestrator opens a run whose `run_id` comes from that decision (a replay emits no second job, a later re-add gets its own), with a window from retirement to now within the cap, and the pollers restart from an empty cursor.

Why: One writer and one job schema remove the races and the jobs nobody sends, while keeping the README's rule that a slow or failed backfill never holds a source out of rotation.

## Consequences

One state machine and one job schema for C10 and every target; six services get the backfill their PRDs promise; fb-backfill (approved) drops its status writes, `notes`, event and cursor seeding.

- CONVENTIONS v1.1: the backfill rule (v1 L53) carries the route table, the window and the `no_history` rule; backfill jobs come only from backfill-orchestrator, and no service backfills on its own first run (v1 L278); `backfill_status` defaults to `pending` (v1 L36).
- F2 types the `backfill` job and its report fields (`oldest_item_at`, `capped_reason`); F3 creates `backfill_runs` with the window and the reason, and the column default.

Sessions that must read this: F2, F3, then F4, F5, C7, C10, FB2, FB3, VFB1, VFB2, IG1, IG2, IG3, IG4, IG5, VIG1, TT1, VTT1, VTT2, VTT4, X5, VLI1, TG1, TG2, VTG1, VTG3, YT3, N2, N3, N4, W5.
