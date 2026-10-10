# ADR-0018 · Budget priorities and modes

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q018 (user decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

README decision 2 sets five priorities (the table in option 1, less the added rows) and three modes: `normal`; `stretch` from 80% of a budget, admitting priorities 1 to 3, from 95% only 1 and 2, amber intervals stretched by a factor never beyond 24 hours; `exhausted` at 100% (`README L179`). quota-governor derives them "from job kind and tier by an SDK helper ... so backfill is always 5" (`quota-governor §5.1 L39`, L43 to L47). D1 found:

- Client refresh: 1 in the README, quota-governor and `comment-decay-scheduler §5.1 L70`; 3 in `yt-comments-fetcher §14 Q2 L204`, `yt-replies-fetcher §14 Q3 L192`, `x-replies-fetcher §7 L145`; "at lowest priority" for backfilled posts (`backfill-orchestrator §5.1 L48`); three labels (AU-039).
- First sight: `yt-video-details-fetcher §5.1 L50` proposes 1 for new videos from every tier and keyword rule (5 for backfill first sight); the table derives 2 or 3 from the tier. A client's X history read is 1 in `x-full-archive-search §5.2 L53`, with no row.
- Orderings outside the table (AU-067): priorities carried on jobs (`yt-comments-fetcher §5.2 L53`, `tt-user-resolver §5.1 L41`, `x-filtered-stream §5.2 L70`); the text refresh at 3 (`yt-text-purger §5.3 L84`); the Meta bucket gating 4 and 5 above 80% (`quota-governor §5.3 L80`); "rotation polls first, comment series second, metrics refreshes third" (`fb-reactions-fetcher §7 L134`) and search ranked "below rotation polls and comment series" (`fb-page-search §7 L127`); daily vendor rules answered wait-until at 80% (`li-post-search §5.1 L46`), the lowest sets on client priority lists first (`tg-message-search §5.1 L46`); resolver discovery "never stretched, only denied" (`tg-channel-resolver §5.1 L47`); the YouTube `reserve` for priority 1 only (`quota-governor §5.3 L79`) or for catch-up, hot posts and client refreshes (`yt-keyword-search §7 L133`).
- Modes on green tags (CF-101): CONVENTIONS stretches and drops hot extras only on amber (`CONVENTIONS L51`, `L271`), the README gates every tag (open in `quota-governor §14 Q2 L171`); x-recent-search has its own X cascade (`x-recent-search §7 L143`).

At stake: what still runs near the X cap, YouTube's 10,000 daily units and each vendor budget.

Settles: RD-2, CF-100, CF-101, AU-039, AU-067, comment-decay-scheduler §14 Q4, fb-group-comments-fetcher §14 Q3, ig-comments-fetcher §14 Q4, quota-governor §14 Q2, x-compliance-sync §14 Q3, yt-comments-fetcher §14 Q2, yt-video-details-fetcher §14 Q1.
Depends on: ADR-0057 (what a job does with `deny` and `wait-until`).

## Options

1. **The README's table, completed with explicit rows and derived only by the SDK helper; priority gating on every tag, interval stretching on amber tags only** (chosen): its rules are under Decision.
2. **The README's table exactly as written, the PRDs aligned.** First sight by tier, X history reads at 5; modes as in option 1. Consequences: fewer rows; at 95% of the YouTube quota, new videos from tier-2 and tier-3 channels stay partial, and a client's X history request waits behind all rotation.
3. **Per-tag priority profiles in `budgets`, or callers sending priorities checked against a per-kind maximum.** Consequences: each vendor keeps its own order, but behaviour becomes configuration, and two services can rank one job differently.

   A variant of any option: CONVENTIONS' modes (amber only), so nothing on X or YouTube is gated before 100%.

## Decision

README decision 2's five priorities stand, completed with explicit rows and derived only by the SDK helper. The modes `stretch` and `exhausted` gate priorities on every budget tag, green ones included; interval stretching applies to amber tags only.

- 1: tier-1 rotation, every client request (refreshes, including of backfilled posts, and history reads), `ops_force`, canaries, and `first_sight` jobs from live discovery on any tier (on YouTube, the details call).
- 2: tier-2 rotation, client keyword and hashtag searches, comment steps to +24 h, +24 h metrics.
- 3: tier-3 and dormant rotation, later comment steps, replies, +7 d metrics, the 30-day text refresh.
- 4: hot-post extras, resolvers and discovery lookups.
- 5: backfill, first sight of backfilled ids, and X history reads nobody asked for.
- No caller sends a priority; the YouTube `reserve` serves priority 1 only; one label, `refresh:<request_id>`.
- Modes: `stretch` and `exhausted` gate priorities on every tag, so hot extras and resolver lookups stop at 80% on X and YouTube; `stretch_factor` (never beyond 24 hours) applies to amber tags only.
- Other orderings: the Meta rule (L80) is kept, being this gating; tg-message-search's client order is the tie-break within a priority; a daily rule that cannot stretch gets wait-until (li-post-search); tg-channel-resolver's "only denied" holds, since resolvers are priority 4; fb-reactions-fetcher's and fb-page-search's orders and x-recent-search's cascade give way to the table. Approved PRDs move under ADR-0001 (x-recent-search, fb-page-search, yt-keyword-search's `reserve`).

It also answers: X compliance jobs (`x-compliance-sync §14 Q3`) run at priority 1 and are never gated, since a missed compliance run breaks the 24-hour rule.

Why: It keeps README decision 2, closes every gap with a row rather than an exception, and keeps priorities out of callers' hands.

## Consequences

One table and one helper, testable in F5; client requests run first, so the admin console (D3) caps them per client; new items are never left half-recorded (a YouTube details call costs 1 unit for 50 ids); from 80% to 95% priority 3 still runs, and only the last 5% is kept for priorities 1 and 2.

- CONVENTIONS v1.1, quotas section: the priority table and the mode rules; the rotation mechanics (v1 L51) and the addendum's hot-post rule (v1 L271) are reworded to match.
- The coverage ADR-0059 adds runs inside this table: the automatic X keyword history and the news history at priority 5, and the X reply steps after day 7 at priority 3 with the other later comment steps.
- F2 carries the one label `refresh:<request_id>`; F5 builds the helper; D3 caps client requests per client in the admin console.

Sessions that must read this: F2, F5, C1, C10, C11, then YT4, YT5, YT6, YT7, YT8, X1, X3, X4, X5, X6, FB4, FB6, VLI1, VTG1, VTG2, VTT3, D3.
