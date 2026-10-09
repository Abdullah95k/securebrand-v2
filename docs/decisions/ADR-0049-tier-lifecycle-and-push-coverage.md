# ADR-0049 · Tier, lifecycle and push coverage

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F3, listening-sdk (F5), registry-writer, qualifier, quota-governor, and the lanes Discover and qualify and Fetch posts (every poller, receiver and searcher)
Source: D2-Q049 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS gives `tier` six values, `1`, `2`, `3`, `push`, `dormant`, `retired` (L36), with cadences for reach sources (L45 to L50); the examples write numbers (`"tier":2`, `qualifier §6.2 L84`) while registry-writer compares `tier = 'retired'` and calls `least_tier(...)` (`registry-writer §5.3 L72`). Two other meanings share the column (CF-095): for keyword rules, tier is a priority with its own cadences (`web-search-perplexity §5.1 L41`, `x-recent-search §5.1 L41`, `yt-keyword-search §5.1 L46`, `web-gdelt-poller §5.1 L41`); for news sites it comes from publishing rate (`news-site-resolver §5.2 L53`, `news-feed-poller §5.1 L42`). `push` mixes in a third meaning (CF-096): CONVENTIONS defines it for client-owned properties with "no polling for new posts; one reconciliation poll a day" (L48), but client TikTok accounts are read hourly while marked `push`, LinkedIn client pages are polled and "the generic push tier does not apply" (`li-client-posts-poller §5.1 L42`), every YouTube channel with a PubSubHubbub lease "sits in the push tier, client-owned or not" while its reach tier is still needed as "the secondary sort key and the quota priority" (`yt-uploads-reconciler §5.1 L45`, `yt-pubsub-receiver §5.1 L40`), and X treats stream coverage as push "while `sources.tier` keeps the reach tier" (`x-filtered-stream §5.1 L42`). A dormant source also needs its reach tier back when it posts again (L49).

Settles: CF-095, CF-096, ig-account-media-poller §14 Q2.

## Options

1. **Three columns: `tier` (1, 2, 3, always kept), `lifecycle` (`active`, `dormant`, `retired`) and `push_covered` (boolean), with one cadence table per source type in CONVENTIONS** (chosen): its rules are under Decision.
2. **One text enum as written (`1`, `2`, `3`, `push`, `dormant`, `retired`) with an ordering function, plus the cadence table per source type.** Consequences: no schema change from CONVENTIONS, but a pushed YouTube or X source loses its reach tier, and a dormant source must recompute its tier from followers when it wakes.
3. **The reach tier only for accounts, pages and channels; keyword rules and news sites get a separate `cadence` field and no tier.** Consequences: clean for searches, but `push` and the lifecycle states still share the column, so CF-096 stays open.

## Decision

`tier` keeps only the reach tier, 1, 2 or 3 (for keyword rules, hashtags and news sites a priority that sets cadence only); `lifecycle` (`active`, `dormant`, `retired`) and `push_covered` (boolean) are columns of their own; one cadence table per source type, read by F5's scheduler helper, sets every interval.

- `tier` is the reach tier for pages, accounts, channels and groups; a source on a client's priority list is tier 1 whatever its followers (CONVENTIONS L45, ADR-0043; `registry-writer §14 Q3 L160`), and rule 6 (L247) is reworded to say so. For keyword rules and hashtags it is the client priority, and for news sites the client priority or publishing rate (`news-site-resolver §5.2 L53`).
- For keyword rules, hashtags and news sites, `tier` sets cadence only. The quota priority always comes from ADR-0018's table, which gives client keyword and hashtag searches priority 2 whatever their tier (`quota-governor §5.1 L44`); F5's helper reads the table, never `tier`, for these source types.
- `lifecycle` replaces `dormant` and `retired` as tier values.
- `push_covered` is true only when new posts arrive by webhook, PubSubHubbub, bot or stream; the poller then makes one reconciliation read a day instead of its tier cadence. It is false for client TikTok accounts and LinkedIn client pages, which are polled (`tt-client-videos-fetcher §5.1 L43`, `li-client-posts-poller §5.1 L42`); their cadence comes from an `owned_by_client` row of the cadence table (TikTok hourly, LinkedIn every 30 to 60 minutes).
- A Telegram bot channel is `push_covered` with its reach tier used only for ordering ("tiered by nothing", `tg-bot-channel-receiver §5.1 L44`); its daily job is the receiver's own health check that the bot is still an administrator, not a reconciliation read, since the Bot API has no history method (CONVENTIONS L196).
- The cadence table, read by F5's scheduler helper, has a row per source type (reach, `owned_by_client` per platform, keyword rules per engine, hashtags, news sites per poller).

It also answers: Volume and publishing rate still set cadence, through the cadence table, not through `tier`: a hashtag's or news site's observed volume or rate picks its row (thresholds are pilot values), and a client's priority sets `tier` (`ig-hashtag-search §14 Q3`, `tt-hashtag-feed-poller §14 Q3`, `news-site-resolver §14 Q3`, `news-feed-poller §14 Q1`, `yt-web-search-bridge §14 Q4`, where tier 1 keeps the API search). A client-owned Instagram account is not `push_covered`, since its webhooks announce comments and mentions but not posts; it is polled at its tier's cadence (`ig-account-media-poller §14 Q2`).

Why: Each of the three meanings gets its own column, so no service overloads one value; `push_covered` keeps one meaning, so F3 and F5 can trust it; the cadences the PRDs need become rows of one table; and priority stays with ADR-0018 alone.

## Consequences

F3 types `tier` as a small integer; registry-writer's `least_tier` becomes a plain minimum and its `'retired'` test reads `lifecycle`, and qualifier rule 6 and news-site-resolver's tier keep numbers (approved PRDs move under ADR-0001); `tier_change` events keep numbers; README decision 8's "`tier = push`" becomes `owned_by_client` plus the hourly row (ADR-0024), and the amber poller never reconciles these accounts (ADR-0052).

- CONVENTIONS v1.1: the three columns (v1 L36); the cadence table per source type, with its `owned_by_client` rows (v1 L44 to L51, L276); rule 6 sets `tier`, a priority-listed source tier 1, and `push_covered` (v1 L247).
- F3 types `tier` as a small integer and adds `lifecycle` and `push_covered`; F5's scheduler helper reads the cadence table, never `tier`, for priorities.

Sessions that must read this: F3 (the column types), F5 (the scheduler's cadence lookup), C1, C7, C9, then TT1, VTT4, TG1, TG2, LI1, LI3, YT2, YT3, FB2, FB7, IG3, IG4, X3, X4, W1, W2, W4, N2, N3, N4, N5, X1, YT8, YT9, IG2, IG5, VLI3.
