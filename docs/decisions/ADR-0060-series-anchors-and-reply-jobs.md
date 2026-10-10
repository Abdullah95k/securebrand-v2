# ADR-0060 · Series anchors and reply jobs

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, comment-decay-scheduler, backfill-orchestrator, fb-backfill, fb-reactions-fetcher, yt-video-details-fetcher, and the lanes Comments and Comments and stats (every comment, reply and metrics service)
Source: D2-Q060 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

- Anchor (AU-030): comment-decay-scheduler counts steps "from the post's first-seen time ... not its creation time" (`§5.1 L60`), as CONVENTIONS does (L56), and gives backfilled posts, or posts first seen when older than the profile's last step, one `once` fetch (`§5.1 L66`). The approved fb-backfill aligns the comment series to `created_time` (`fb-backfill §5.1 L47`); fb-reactions-fetcher and yt-video-details-fetcher set metrics due at creation plus 24 hours or 7 days (`fb-reactions-fetcher §5.1 L41`, `yt-video-details-fetcher §5.1 L45`); ig-own-comments-fetcher proposes the media's timestamp when first sight lags by over an hour (`§14 Q2 L193`); tt-video-stats-refresher counts from first sight but expects no metrics jobs after day 7 (`§5.1 L44`, `L48`).
- Replies (AU-035): comment-decay-scheduler sends one `replies` job per post with `thread_ids` (`§5.3 L94`), though its table says per comment (`§5.1 L52`); three fetchers read one thread in `post_ref` (`fb-group-comments-fetcher §5.1 L40`, `tt-video-comments-fetcher §5.1 L41`, `yt-replies-fetcher §5.1 L38`); yt-replies-fetcher runs a per-thread series (`§5.1 L40`) that `comment_series`, one row per post and lane (`comment-decay-scheduler §6.3 L147`), cannot hold; ig-own-comments-fetcher expects `replies` jobs (`§5.1 L51`) where the profile says "no job" (`comment-decay-scheduler §5.1 L50`).

At stake: a late or backfilled post is scheduled differently on each side, metrics land at different post ages, and reply jobs do not parse.

Settles: AU-030, AU-035, ig-own-comments-fetcher §14 Q2, tt-video-stats-refresher §14 Q3, yt-video-details-fetcher §14 Q3.
Depends on: ADR-0005 (the backfill marker), ADR-0011 (`post_ref`), ADR-0034 (metrics jobs), ADR-0046 (`comment_series`), ADR-0059 (which backfilled posts get a fetch).

## Options

1. **Comments from first sight, metrics from creation, one `replies` job per post** (chosen): its rules are under Decision.
2. **Creation time for both lanes** (AU-030 option 2). Consequences: one clock, but a post found three days late gets its first comment fetch at +3 d at best.
3. **First sight unless it lags creation by a threshold** (AU-030 option 4). Consequences: two clocks and a threshold to tune, for a case the first fetch already catches up.
4. **One `replies` job per thread, with a YouTube replies lane** (AU-035 options 2 and 3). Consequences: the fetchers keep their trigger lines; the scheduler loses its one-job-in-flight rule and needs per-thread rows.

## Decision

Comment steps count from the post's first sight and metrics steps from its creation time; a backfilled post gets one `once` comment fetch on green routes and none on amber; reply threads are fetched by one `replies` job per post carrying `thread_ids`, with no per-thread series.

- Comment steps count from first sight, so a post found late still gets its whole series; one first seen after its profile's last step gets the `once` fetch; ig-own-comments-fetcher's threshold is not adopted.
- Backfilled posts (`job_kind = backfill`, and the posts of an X `keyword_history` read, which count as backfill reads, ADR-0059) get no series: on green comment routes one `once` fetch at priority 5, whatever the post's age, and on amber routes none in v1 (ADR-0059 a); fb-backfill's alignment sentence goes (an approved PRD moves under ADR-0001).
- Metrics count from the platform's creation time, and steps already past at first sight are not emitted (ADR-0034); tt-video-stats-refresher moves to that clock (its §14 Q3: yes).
- Replies: one `replies` job per post, `post_ref` carrying `thread_ids` (the parent comments' platform ids, capped by a setting tuned in the pilot); the fetcher loops over them and reports per thread; further candidates wait for the next job, so a post keeps one job in flight (`comment-decay-scheduler §5.1 L62`).
- Reply jobs only on the addendum's profiles: `fb_group` (vendor comment ids), `tt` (more than 10 replies), `yt` (more than 5, to yt-replies-fetcher); and X's steps after +3 d, `replies` jobs on `jobs.x-full-archive-search` that read the whole conversation from `window_start` rather than `thread_ids` (ADR-0059, ADR-0064); ig-own-comments-fetcher pages nested replies inside its `comments` job and drops kind `replies`.
- No per-thread series: a thread is a candidate again whenever a comment step reports more replies than are stored (`comment-decay-scheduler §5.3 L94`, `yt-comments-fetcher §5.2 L60`), so growing threads are re-read at the post's steps; yt-replies-fetcher keeps only its skip rule (`§5.1 L42`).

Why: Comment coverage is about not missing a conversation, so its clock starts at first sight; engagement counts are compared across posts, so they are read at the same post age. One job per post keeps the scheduler's one-in-flight rule, and re-reading only grown threads does the per-thread series' work for less quota.

## Consequences

`comment_series` keeps one row per post and lane (ADR-0046); one reply-job shape, so three fetchers change their trigger lines; fb-backfill, tt-video-stats-refresher and yt-replies-fetcher rewrite their series text.

- CONVENTIONS v1.1: first sight as the comment anchor, a backfilled post's one `once` fetch (v1 L56); metrics counted from creation (v1 L65); one `replies` job per post with `thread_ids` (v1 L60 and the addendum's Replies column).
- F2 types `thread_ids` in `post_ref` (ADR-0011); F3 keeps one `comment_series` row per post and lane (ADR-0046).

Sessions that must read this: F2 (the `replies` job), F3 (`comment_series`), C10, C11, then FB3, FB4, VFB3, IG6, VTT5, VTT6, YT4, YT5, YT6.
