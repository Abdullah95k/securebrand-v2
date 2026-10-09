# ADR-0046 · Comment state and comment series

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, F8, listening-sdk, comment-decay-scheduler, deletion-propagator, and the lanes Comments and Comments and stats (every comment and replies fetcher)
Source: D2-Q046 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

- One job, five designs (CF-045). Telling new, edited and deleted comments from stored ones (`CONVENTIONS L62`, `L63`) runs on `comment_ledger`, owned by fb-post-comments-fetcher and "shared" by fb-group-comments-fetcher with other columns and another edit rule (`fb-post-comments-fetcher §6.3 L129`, `§5.2 L68`; `fb-group-comments-fetcher §6.3 L132`, `§5.2 L65`); on `tt_comment_state` (`tt-video-comments-fetcher §6.3 L123`), whose PRD asks for a shared `comment_state` (`§14 Q2 L182`); on yt-comments-fetcher's comment index, which yt-replies-fetcher reads beside its own (`yt-comments-fetcher §6.3 L140`, `yt-replies-fetcher §5.1 L42`); on x-replies-fetcher's reply index (`x-replies-fetcher §6.3 L138`); and on ClickHouse `comments`, read by six fetchers (for example `ig-comments-fetcher §6.3 L119`, `news-comments-fetcher §6.3 L124`), where the stored hash is normalize-item's (`normalize-item §5.2 L51`) and LinkedIn rows go at 48 hours (`store-writer §5.3 L77`).
- Per-post markers (AU-020). The LinkedIn fetchers keep `newest_comment_at` and a running total "in the series state owned by comment-decay-scheduler" (`li-post-comments-fetcher §5.1 L50`, `li-own-comments-fetcher §6.3 L130`), and news-comments-fetcher passes its thread id through the scheduler (`news-comments-fetcher §6.3 L124`); `comment_series`, the job and the report carry neither (`comment-decay-scheduler §6.3 L147`, `§6.2 L141`, `§5.4 L127`).
- RN-16. The inventory gives `comment_series` the key (`item_id`, `lane`) (`INVENTORY L1871`) and omits "one `comment_series` row per post" (`x-replies-fetcher §5.1 L41`) and "exactly one `comment_series` row per lane" (`comment-decay-scheduler §13 L188`).

At stake: ADR-0062's confirmed-absence rule and ADR-0009's single hash need stored state every fetcher can rely on; built five ways, it is built, tested and purged five times.

Settles: CF-045, AU-020, RN-16, tt-video-comments-fetcher §14 Q2.
Depends on: ADR-0009 (one content hash; edits), ADR-0041 (per-post `cursors` rows), ADR-0060 (the replies job), ADR-0062 (deletion on absence).

## Options

1. **One shared `comment_state` table behind one SDK helper; per-post state in the fetcher's `cursors` rows; `comment_series` keyed by post and lane** (chosen): its rules are under Decision.
2. **Per-service tables of one design (CF-045 (2)).** The same columns in a table per service under the naming rule, through the same helper. Consequences: no rows shared between services and separate purges, but eleven tables to create, migrate and register.
3. **ClickHouse `comments` as the only state (CF-045 (3)), with the markers in `comment_series` or carried as an opaque `fetch_state` on job and report (AU-020 (1), (3)).** Consequences: no Postgres table, but ADR-0062's first-miss mark has nowhere to live, a LinkedIn post's rows are gone before its +3 d fetch, fetchers depend on store-writer's write delay, and fetcher data sits in the scheduler's table.

## Decision

One shared `comment_state` table, behind one SDK helper, tells new, edited and deleted comments apart for every fetcher; per-post fetch state lives in the fetcher's own `cursors` row; `comment_series` stays comment-decay-scheduler's, keyed by post and lane.

- `comment_state`, one row per (`service`, `post_item_id`, `comment_key`): `parent_key`, `content_hash` (ADR-0009), `version`, `state` (`live`, `missing` after one miss, `deleted`), `first_seen_at`, `last_seen_at`, `reply_count` (as last seen, for reply thresholds); no text, no author. Only the service named in the row writes it, through an SDK helper that compares a fetch with the stored set and returns new comments, new versions and deletions confirmed under ADR-0062. Edits follow ADR-0009 (same key and a new version where the platform gives ids, otherwise a new key and the old key's deletion), so `superseded_by` and `edit_of` go. Rows are kept while the post can still be fetched (a margin set in the pilot) and always removed with it through the purge registry (ADR-0035); a `linkedin_48h` post's rows go at 48 hours.
- Per-post fetch state (last complete fetch, stored count, partial bounds, `newest_comment_at`, the Disqus thread id) lives in the fetcher's own `cursors` row for the post (`scope_key = post:<item_id>`, ADR-0041), dropped when the series ends. The LinkedIn marker survives the 48-hour purge there; the running total stays the scheduler's `last_total`.
- This replaces `comment_ledger`, `tt_comment_state`, the comment index, both reply indexes and the six ClickHouse reads. yt-replies-fetcher's skip rule, which ADR-0060 keeps (`yt-replies-fetcher §5.1 L42`), reads the parent comment's `reply_count` and `last_seen_at` in yt-comments-fetcher's rows through the helper, the table's one named cross-service read.
- `comment_series` stays comment-decay-scheduler's, primary key (`item_id`, `lane`), lanes `comments` and `metrics` (`comment-decay-scheduler §6.3 L147`, `§5.1 L68`). x-replies-fetcher's "one row per post" is the comments lane, since X has no metrics lane (ADR-0058). RN-16 closes by recording the key with both statements.

Why: One helper and one table do the same job once; Postgres state gives ADR-0062 its first-miss mark, and per-post markers in `cursors` follow ADR-0041's single cursor rule.

## Consequences

F3 creates one table, partitioned by service if volume needs it (a setting); eleven comment and replies PRDs reword their state lines; `tt-video-comments-fetcher §14 Q2 L182` and `fb-post-comments-fetcher §14 Q6 L192` are answered.

- CONVENTIONS v1.1: `comment_state` and `comment_series`, with their keys, among the control-plane tables (v1 L30); the stored state the comment rules use (v1 L62, L63).
- F3 creates `comment_state` and `comment_series`; F4 builds the helper.
- `DEFERRED.md`: how long `comment_state` rows are kept while a post can still be fetched (owner C11, after the pilot).

Sessions that must read this: F2, F3, F8, C6, C11, FB5, VFB3, IG6, VIG2, VTT5, YT5, YT6, X6, LI2, VLI4, N8.
