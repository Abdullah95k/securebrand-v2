# ADR-0019 · Early stop

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: comment-decay-scheduler, and the lanes Comments and Comments and stats (every comment fetcher)
Source: D2-Q019 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS stops a series "when a fetch adds fewer than 5% new comments (and fewer than 5 absolute)" with no arming condition (`CONVENTIONS L57`, `L271`). README decision 3 arms early stop "only once a post has 5 stored comments or after its +24 h step", so a post with no comments at +1 h keeps its series (`README L180`); comment-decay-scheduler implements it (`comment-decay-scheduler §5.3 L88`, `L89`; asked to confirm in `§14 Q2 L203`), as do `x-replies-fetcher §5.1 L45` and `yt-replies-fetcher §5.1 L40`. The LinkedIn fetchers arm it "from the second fetch of a post onward" (`li-own-comments-fetcher §5.1 L42`; `li-post-comments-fetcher §5.1 L44`); four fetchers restate CONVENTIONS without arming (`fb-post-comments-fetcher §5.1 L48`, which asks whether the +24 h step should be exempt, `§14 Q2 L188`; `news-comments-fetcher §5.1 L43`; `tt-video-comments-fetcher §5.1 L44`; `ig-comments-fetcher §5.1 L45`). The denominator: the scheduler measures growth over the comments stored before the fetch (`comment-decay-scheduler §5.3 L87`), while li-own-comments-fetcher measures over the platform's reported count, "because held comments expire at 48 hours" (`li-own-comments-fetcher §5.1 L42`).

Settles: RD-3, CF-107, comment-decay-scheduler §14 Q2, fb-post-comments-fetcher §14 Q2.

## Options

1. **README decision 3 on every profile, applied only by comment-decay-scheduler, with the +24 h step kept and a LinkedIn denominator** (chosen): its rules are under Decision.
2. **Per-profile arming and denominator columns, filled from each fetcher's PRD.** Consequences: every route keeps what its PRD wrote (LinkedIn from the second fetch, Facebook and news unarmed), so the same post shape stops at different times on different routes with no stated reason.
3. **CONVENTIONS as written (no arming), with the +24 h step exempt.** Consequences: a post with no comments at +1 h loses +6 h and every step after +24 h, the case the README added the arming rule for.

## Decision

README decision 3 applies on every comment profile, and only comment-decay-scheduler applies it: early stop is armed once a post has 5 stored comments or its +24 h step has run, the +24 h step always runs, and LinkedIn measures growth over the platform's count or the fetcher's running total.

Early stop is armed once the post has 5 stored comments or its +24 h step has run, as the README says; once it fires it cancels the remaining steps except the +24 h step, which always runs as the sweep for late comments (fb-post-comments-fetcher's proposal, `§14 Q2 L188`); a +24 h sweep that adds 20% or more of the stored comments reopens the cancelled steps as an extension (the extension threshold of CONVENTIONS L271). Growth is measured over the comments stored before the fetch, except on LinkedIn, where held comments expire at 48 hours: li-own-comments-fetcher measures over the API's reported comment count (`li-own-comments-fetcher §5.1 L42`), li-post-comments-fetcher over its own running total of comments seen (`li-post-comments-fetcher §6.1 L103`, `§6.3 L133`). The fetchers report counts and never stop a series themselves; their PRDs drop their own early-stop text.

Why: The README's rule fixes a real failure (quiet posts that pick up comments later), the scheduler already implements it, the +24 h sweep is the cheapest catch for late comments, and LinkedIn's 48-hour purge is the one case where the stored count is the wrong basis.

## Consequences

One rule in one service; one extra fetch for posts that settle before +24 h; the LinkedIn denominators are one column in the profile table, filled from the fetcher's report.

- CONVENTIONS v1.1: the early-stop rule (v1 L57) and the general rules of the series profiles (v1 L271) gain the arming condition, the reopening rule and the LinkedIn denominators.
- The fetchers' PRDs drop their own early-stop text. The thresholds stay as written; tuning them after real data belongs to the sessions after G2 (build plan L65; `DEFERRED.md`).

Sessions that must read this: C11, then FB5, VFB3, IG6, VIG2, VTT5, X6, YT5, YT6, LI2, VLI4, N8.
