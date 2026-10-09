# ADR-0056 · Lifetimes of derived data

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F3, F8, store-writer, aggregator, retention-purger, deletion-propagator, yt-text-purger, yt-channel-resolver, yt-comments-fetcher, yt-video-details-fetcher, li-client-posts-poller, li-own-comments-fetcher
Source: D2-Q056 (user decision; changed by the user's answer, which keeps the recommended option under the ten-year classes of ADR-0054) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS keeps "Aggregates and derived scores: ten years, all classes" (L81) while `youtube_30d_text` keeps "derived metrics ... up to 36 months" (L76), from the YouTube fact sheet: "raw comment text no longer than 30 days (delete or refresh), derived metrics up to 36 months for 'Analytics & Reporting' clients, no aggregation across channels of different owners except under the carve-out" (L209). The PRDs apply it three ways: store-writer expires YouTube item rows at "created + 36 months" (`store-writer §5.3 L76`); yt-text-purger deletes items, `analysis` and hit rows when "the last `fetched_at` is older than 36 months" and leaves aggregates (`yt-text-purger §5.3 L118`, `§13 L259`); retention-purger never selects aggregates (`retention-purger §5.3 L68`; AU-080); the question is still open in `yt-comments-fetcher §14 Q5 L207` and `yt-video-details-fetcher §14 Q4 L218`. For LinkedIn, store-writer deletes `linkedin_48h` rows "with its `analysis` rows" (`store-writer §5.3 L77`, asked in `§14 Q3 L183`), the comment fetchers test the same (`li-own-comments-fetcher §13 L178`), while li-client-posts-poller keeps derived scores ten years (`li-client-posts-poller §7 L135`). And the 30-day clock covers "raw comment text" in CONVENTIONS, but yt-text-purger also runs it on video titles and descriptions (`yt-text-purger §3 L19`, `§5.3 L120`, open in `§14 Q1 L266`) and yt-channel-resolver on channel profiles (`yt-channel-resolver §6.2 L113`).

The user's answer, 7 Oct 2026: "Q054, Q055, and Q056 data retention should be up to 10 years." Asked again, the user chose "10 years where allowed": every item is kept 10 years on X, Meta, Telegram, news, web and vendor routes, with deletion requests honoured; YouTube, LinkedIn and TikTok items are kept as long as their terms allow, and their counts and trends are kept 10 years. For derived data that is option 1, under the ten-year classes of ADR-0054: on YouTube, text refreshed or deleted at 30 days, item-level derived rows 36 months and per-channel rollups 36 months; every other aggregate and rollup ten years.

Settles: CF-106, AU-080, li-own-comments-fetcher §14 Q4, store-writer §14 Q3, yt-comments-fetcher §14 Q5, yt-text-purger §14 Q1, yt-text-purger §14 Q3, yt-video-details-fetcher §14 Q4.

## Options

1. **Item-level derived rows follow their item's class; aggregates keep ten years except per-channel YouTube rollups; the 30-day rule covers all stored YouTube text** (chosen): its rules are under Decision.
2. **Ten years for every derived row and aggregate, as CONVENTIONS L81 says;** the YouTube and LinkedIn limits apply only to raw text and identities. Consequences: the longest history for clients; per-item YouTube scores and metrics outlive the 36 months the fact sheet quotes, a risk at YouTube's audit ("audit at any time", L209).
3. **Per-class lifetimes for both item rows and aggregates:** every YouTube-derived aggregate also capped at 36 months. Consequences: the most conservative; YouTube disappears from ten-year trend lines after three years.

## Decision

Option 1 stands, under the ten-year classes of ADR-0054. Item-level derived rows (analysis scores, hits, metrics time series) follow their item's class, so they keep ten years wherever their item does; every aggregate and rollup keeps ten years, except rollups at the level of one YouTube channel, which keep 36 months; the 30-day refresh-or-delete clock covers all stored YouTube text.

Analysis scores, hits and metrics time series of a YouTube item expire 36 months after the item's creation (store-writer's anchor); those of a LinkedIn member item go with it at 48 hours. Rollups keep ten years, except rollups at the level of one YouTube channel, which follow the 36 months (AU-080 option 3). Rollups across channels of different owners exist only under the carve-out the fact sheet names (CONVENTIONS L209); where they exist they keep ten years, which counsel confirms (that they are not "derived metrics" capped at 36 months). The 30-day refresh-or-delete clock applies to comment text, video titles and descriptions and channel profile text, as yt-text-purger and yt-channel-resolver assume. CONVENTIONS L76 and L81 are reworded accordingly. Refresh is part of the service, not an option clients buy: yt-text-purger refreshes the text of comments on client-watched sources within a share of the `comments` bucket set in the pilot and deletes, at 30 days, the text it cannot refresh in time (metrics stay), so no `yt_text_refresh` entitlement is added to `clients` in v1 (`yt-text-purger §14 Q3`).

With the classes of ADR-0054:

- an item-level derived row keeps ten years wherever its item does (`meta_on_request`, `vendor_agreed`, `x_24h_sync`, `news_excerpt`, `telegram_bot`), follows the client's authorisation under `tiktok_display`, and goes with its item on a deletion;
- LinkedIn aggregates keep ten years like every platform's, and per-post LinkedIn rollups wait for counsel (ADR-0048);
- every other aggregate and rollup keeps ten years.

Why: It follows the fact sheet's wording where it is specific (36 months, 30 days, no cross-owner aggregation), keeps the ten-year promise for everything else, and gives retention-purger one anchor per class. The user's answer keeps counts and trends ten years on every platform, YouTube's per-channel figures excepted where its policy caps them.

## Consequences

One anchor (creation); YouTube trends older than three years survive only as cross-channel rollups; more refresh calls on the YouTube quota for titles and profiles (yt-text-purger already budgets them).

- CONVENTIONS v1.1: what the 30-day clock covers, and the 36-month anchor (v1 L76); aggregates and derived scores ten years, with the per-channel YouTube exception (v1 L81).
- F3 seeds the `derived` and `row` parts of `retention_classes` (ADR-0045); F8 sets the TTLs, the per-channel YouTube rollups at 36 months.
- `DEFERRED.md`: counsel's confirmation of the YouTube reading, ten years for cross-owner rollups under the carve-out included (owner YT7, before YouTube's go-live, G3).

Sessions that must read this: F3, F8 (TTLs), C6, C13, C14, C15, then YT1, YT4, YT5, YT7, LI2, VLI4.
