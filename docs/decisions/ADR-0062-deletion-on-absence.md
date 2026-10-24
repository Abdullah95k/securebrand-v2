# ADR-0062 · Deletion on absence

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: listening-sdk (F4), deletion-propagator, and the lanes Fetch posts, Comments and Comments and stats (every fetcher that refetches)
Source: D2-Q062 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS turns missing comments into `deletions` with reason `platform_sync` "when the API is complete" (L63) and has no rule for posts. The PRDs differ (CF-113): fb-reactions-fetcher deletes a post on one "not found" (`fb-reactions-fetcher §8 L144`) while the two Facebook comment fetchers never delete a post on one error (`fb-post-comments-fetcher §8 L143`, `fb-group-comments-fetcher §8 L145`); yt-video-details-fetcher and tt-video-stats-refresher confirm with a second request (`yt-video-details-fetcher §5.2 L62`, `tt-video-stats-refresher §5.2 L60`); tt-video-comments-fetcher waits for two consecutive full reads (`§8 L138`); X replies and Instagram vendor comments never delete on absence (`x-replies-fetcher §8 L154`, `ig-comments-fetcher §13 L171`). A post that a comment fetcher finds deleted is handed to a poller that cannot detect it on Instagram, or on LinkedIn after day 7 (AU-085). deletion-propagator acts on the first message it receives, so the strictest reader decides.

Settles: CF-113, AU-085, fb-group-comments-fetcher §14 Q5, yt-comments-fetcher §14 Q3, yt-replies-fetcher §14 Q5.
Depends on: ADR-0035 (the `deletions` message).

## Options

1. **One rule in the SDK: absence becomes a deletion only after a confirmed second miss, or on a platform deletion signal; and routes whose reads are not complete listings never delete on absence** (chosen): its rules are under Decision.
2. **CONVENTIONS extended to posts: one complete read that misses the item is enough.** Consequences: faster removal, but a transient error or a partial page on one service erases a post others still see.
3. **Per route as written**, with fb-reactions-fetcher aligned to the other Facebook readers and the never-delete routes recorded. Consequences: the least change, but five behaviours to build and test.

## Decision

Through one SDK rule, absence becomes a deletion only after a confirmed second miss, or on a platform deletion signal; routes whose reads are not complete listings never delete on absence.

A fetcher that misses an item records a suspicion; the next read (or one confirming request within the job) that misses it again emits `deletions` with `platform_sync`. A platform signal (a webhook `remove`, X compliance, a 404 on the item's own endpoint where the platform documents it as deleted) counts as confirmation. Routes listed in CONVENTIONS as "no deletion on absence": X replies (x-compliance-sync is the deletion source), Instagram vendor comments (about 15 visible comments), li-company-posts-poller's vendor posts ("an absent post cannot be told from a post the Actor did not return", `li-company-posts-poller §5.4 L92`), keyword and hashtag searches. li-client-posts-poller's daily reconciliation reads back over the class's retention period, six weeks under ADR-0055, instead of 7 days (`li-client-posts-poller §5.1 L48`, `§13 L179`; AU-085 option 1), so a green post deleted after its comment series is still mirrored. A comment fetcher that finds the post itself gone emits the post's deletion under the same rule rather than handing it to a poller.

It also answers: Removed YouTube replies are detected by yt-replies-fetcher's own thread read while the thread is a reply candidate, and by yt-comments-fetcher's thread read (a complete listing at 5 replies or fewer) after (`yt-replies-fetcher §14 Q5`).

Why: Deletion is irreversible downstream (deletion-propagator removes derived rows and recomputes aggregates), so one confirmation costs little; listing the routes where absence means nothing removes the false deletions D1 found.

## Consequences

One implementation and one test in F4; fb-reactions-fetcher, an approved PRD, is aligned under ADR-0001; a deleted post stays visible for one more read cycle; the LinkedIn reconciliation reads up to six weeks of posts a day, a quota cost rather than money.

- CONVENTIONS v1.1: the absence rule (v1 L63) extended to posts, with the confirmation rule, the routes that never delete on absence and li-client-posts-poller's reconciliation window.
- F4 builds the rule and its test.

Sessions that must read this: F4 (the shared rule in the SDK), C13, then FB4, FB5, VFB3, YT4, YT5, VTT5, VTT6, X6, VIG2, IG3, IG6, LI1, LI2, VLI3.
