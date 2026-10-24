# ADR-0058 · Count refreshes on X, LinkedIn and Telegram

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: comment-decay-scheduler, tg-channel-posts-poller, li-client-posts-poller, li-company-posts-poller, fb-group-posts-poller, x (x-recent-search, x-filtered-stream, x-user-timeline-poller)
Source: D2-Q058 (user decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS refreshes likes, shares, views and comment counts at +24 h and +7 d on every route (L65). The README records counts on X, LinkedIn and Telegram at first sight only, leaving refreshes as an open question (`README L25`); comment-decay-scheduler does the same and asks (`comment-decay-scheduler §5.1 L68`, `§14 Q6 L207`). tg-channel-posts-poller expects a +24 h views refresh for tier-1 posts on a `metrics` job that the scheduler never emits, and asks whether it is worth its cost (`tg-channel-posts-poller §5.1 L56`, `§14 Q5 L195`; AU-032); li-company-posts-poller leaves it open (`li-company-posts-poller §5.4 L92`, `§14 Q3 L186`). Prices from the fact sheets: X USD 0.005 per post read (about 0.6 million X posts a month, CONVENTIONS L3), Apify Telegram Actors about USD 2,900 to 7,200 a month at 2.4 million items, harvestapi about USD 225 to 300 a month at 0.15 million LinkedIn items (L87, L93, L94).

Settles: CF-082, AU-032, comment-decay-scheduler §14 Q6, fb-group-posts-poller §14 Q6, li-company-posts-poller §14 Q3, tg-channel-posts-poller §14 Q5.

## Options

1. **First-sight counts only on X, LinkedIn and Telegram in v1** (chosen): its rules are under Decision.
2. **A Telegram tier-1 +24 h views refresh only**, as tg-channel-posts-poller describes, first sight elsewhere. Consequences: one more lane in comment-decay-scheduler; Apify charges per item re-read.
3. **+24 h and +7 d refreshes on every route, as CONVENTIONS says.** Consequences: about two extra paid reads per X post (at 0.6 million posts a month, roughly USD 6,000 a month more at list price) and two extra vendor reads per LinkedIn and Telegram item.

## Decision

In v1, engagement counts are recorded at first sight only on X, LinkedIn, Telegram and Facebook groups; Facebook Pages, Instagram, TikTok and YouTube refresh them at +24 h and +7 d. The question comes back after the pilot, with measured costs.

CONVENTIONS L65 is amended to name the routes that refresh (Facebook Pages, Instagram, TikTok, YouTube) and those that record counts at first sight (X, LinkedIn, Telegram, news, as `comment-decay-scheduler §5.1 L68` already says, and amber Facebook groups, whose post counts no service refreshes either, `fb-group-posts-poller §14 Q6`); tg-channel-posts-poller drops its `metrics` job.

Why: It matches the README and the scheduler as written and avoids a cost that is large on X before the pilot shows clients need it.

## Consequences

No extra spend; trend charts on these routes show counts as first seen, and the engagement-spike alerts of ADR-0048 have no count velocity on them in v1; the question can come back after the pilot with measured costs.

- CONVENTIONS v1.1: the metrics rule (v1 L65) names the routes that refresh counts and those that record them at first sight.
- tg-channel-posts-poller drops its `metrics` job.
- `DEFERRED.md`: refreshes on these routes, revisited after G2 with measured costs (owner C11).

Sessions that must read this: C11, VTG3, LI1, VLI3, VFB2, X1, X3, X4.
