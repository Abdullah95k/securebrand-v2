# ADR-0001 · Decisions override approved PRDs

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q001 (user decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

D2 took this decision first, because every other decision assumes its answer. CONVENTIONS L282 lists twenty PRDs "to stay consistent with (already approved; do not rewrite)": fb-page-search, fb-page-feed-poller, fb-backfill, fb-reactions-fetcher, ig-hashtag-search, tt-keyword-search, tt-hashtag-feed-poller, x-recent-search, li-post-search, li-org-resolver, tg-message-search, tg-channel-resolver, yt-keyword-search, yt-web-search-bridge, news-site-resolver, web-search-perplexity, normalize-item, poster-resolver, qualifier and registry-writer. CONVENTIONS L278 also makes fb-page-feed-poller the model every rotation scheduler follows "exactly". D1 found these PRDs on one side of many entries (CF-116):

- Some depart from CONVENTIONS itself. fb-page-feed-poller, fb-backfill, fb-page-search and x-recent-search name the job type `reason`, not `kind` (CF-077 b). fb-page-search keys its queue on `keyword_id` (CF-087 c). fb-reactions-fetcher expects `refresh_24h` and `refresh_7d` kinds (CF-081 b). ig-hashtag-search charges `ig_graph_<client_id>` (CF-099 b). tt-keyword-search, tt-hashtag-feed-poller and tg-message-search backfill on their own first run (CF-088 c). web-search-perplexity and yt-web-search-bridge publish results on `search.results` instead of items on `raw.items` (CF-110 b). li-org-resolver and tg-channel-resolver take jobs without the CONVENTIONS fields (CF-085 b, c); tg-message-search's job has no `source_id`, `kind` or `due_at` (CF-077 e); registry-writer spells `tier_change` (CF-098 a).
- Some stand against unapproved PRDs, so where D2 decides for the other side the approved PRD moves: normalize-item's mapper keys (CF-060 to CF-066), poster-resolver's author hash (CF-069) and resolver round trip (CF-085 a), news-site-resolver's Disqus series (CF-108) and producer list (CF-085 d), web-search-perplexity's `site_search` (CF-078 e) (CONFLICTS.md L1903).
- In nine places two approved PRDs contradict each other, so L282 cannot decide them: normalize-item against tt-keyword-search and tt-hashtag-feed-poller on TikTok keys (CF-062), against tg-message-search on Telegram keys (CF-063) and against li-post-search on LinkedIn keys (CF-064); li-org-resolver's `linkedin:org:` against poster-resolver's `candidate_key` rule (CF-073); web-search-perplexity expecting `site_search` jobs that yt-web-search-bridge never sends (CF-078 e); li-org-resolver expecting `refresh` from qualifier (CF-078 f); poster-resolver against li-org-resolver and tg-channel-resolver on the resolver round trip (CF-085); registry-writer's `tier_change` against fb-page-feed-poller's `tier change` (CF-098); normalize-item's `web:result` mapper against web-search-perplexity, which writes no result items (CF-110).

Read literally, L282 leaves those nine undecidable and makes CONVENTIONS adopt every departure. Several decisions move an approved PRD (the `raw.items` shape in ADR-0005, the job field `kind` in ADR-0011, key formats in ADR-0007).

Settles: CF-116.

## Options

1. **Each decision states which side moves, and L282 is reworded** (chosen): its rules are under Decision.
2. **The approved PRDs win.** Where an approved PRD departs from CONVENTIONS, CONVENTIONS v1.1 takes the PRD's version (for example `reason` beside `kind`, flat and nested `raw.items` side by side, `ig_graph_<client_id>`). Consequences: the fewest PRD edits, but two spellings of several contracts survive into F2, against ADR-0005, ADR-0007 and ADR-0011; and the nine approved-against-approved conflicts still need an answer each, so this option alone does not close CF-116.
3. **CONVENTIONS wins.** L282 is lifted for every point D2 decides, and the approved PRDs are revised to match CONVENTIONS. Consequences: a simple rule, but CONVENTIONS is silent on most points (no envelope fields, no topic beyond its thirteen, no table columns beyond `sources` and `cursors`), so most entries still need their own answer; in practice this is option 1 without its flexibility.

## Decision

An ADR wins over every PRD, approved or not. Each ADR says which side of a conflict moves, and every PRD edit cites its ADR. The twenty PRDs that CONVENTIONS v1 L282 called approved keep their standing on everything no ADR touches.

CONVENTIONS v1.1 replaces L282 with: "These PRDs were reviewed first. Where an ADR decides a contract question, the ADR wins over every PRD, approved or not, and each PRD edit cites its ADR." The approved PRDs keep their standing on everything no ADR touches.

Why: Option 1 is the only one that closes every case in CF-116, including the approved-against-approved ones (D1's option 4 is a special case of it), and it is the rule F2 already works to.

## Consequences

Every entry becomes decidable on its merits; the twenty PRDs are edited like the others where a decision goes against them; F2 builds the contracts from the ADRs, which its brief already requires ("When PRD examples disagree on a field, the ADR decides, never a majority of examples").

- CONVENTIONS v1.1 replaces L282 with the sentence above. In L278, "exactly as described in fb-page-feed-poller" becomes "as described in fb-page-feed-poller, with the job fields this document defines".
- F2, F3 and F8 build the contracts from the ADRs, never from a majority of PRD examples, as the F2 brief already says.
- D2 edits a PRD line only where an ADR names the edit, and that edit cites the ADR. Every other PRD line an ADR overrides stays as written, so a build session finds the override through the ADR's "Applies to" line and follows the ADR.

Sessions that must read this: F2 first, then every session whose PRD was on the approved list: FB6, FB2, FB3, FB4, IG2, VTT1, VTT2, X1, VLI1, VLI2, VTG1, VTG2, YT8, YT9, N2, W1, C4, C8, C9, C7.
