# ADR-0070 · Editorial corrections

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all; by name the nine CF-027 PRDs: keyword-matcher, news-robots-checker, web-search-perplexity, web-search-mojeek, web-gdelt-poller, normalize-item, fb-backfill, tg-bot-channel-receiver, raw-archiver, news-article-extractor, web-commoncrawl-scanner
Source: D2-Q070 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CF-027 lists nine places where one PRD names a message field two ways, prose against its own example: a) keyword-matcher's `set_version` (`keyword-matcher §5.3 L58`) against `keyword_set_version`, rendered `"cs:3f9a1c"` while the `message_id` embeds `cs3f9a1c` (`§6.2 L100`, `L107`); b) news-robots-checker's `robots_status` (`§5.3 L71`) against `robots.status` (`§6.2 L102`), with `ai-input` and `ai-train` mapped to `ai_input` and `ai_train` unstated (`§5.3 L73`); c) the web engines' `normalize = skip` on records whose envelope lists have no such field (`web-search-perplexity §5.2 L55`, `§6.2 L89`, and the other two engines); d) `lang_pending`, `text_full_ref` and `author_followers` missing from normalize-item's example (`normalize-item §8 L133`, `§5.3 L72`, `§5.4 L79`); e) fb-backfill's envelope "identical to fb-page-feed-poller's" yet with a `window` object (`fb-backfill §6.2 L88`, `L104`); f) tg-bot-channel-receiver's "the `channel_post` object unchanged" while edits arrive as `edited_channel_post` (`§6.2 L113`, `§5.2 L59`); g) raw-archiver's `raw.replay` example short of its own field list (`raw-archiver §6.2 L98-L115`); h) news-article-extractor's promised code version, shown as `"extractor": "trafilatura"` (`§12 L167`, `§6.2 L120`); i) web-commoncrawl-scanner's `accept_rate` "from `source.events`", which its reads omit (`§10 L136`, `§6.1 L80`).

CF-117 collects five inconsistencies sessions would quote literally: a) replies "through the same service with job kind `replies`" (`CONVENTIONS L60`) against YouTube's own yt-replies-fetcher (`L265`); b) the X cap "per billing cycle" (`CONVENTIONS L87`; `quota-governor §5.3 L78`) against "per month on pay-per-use" (`CONVENTIONS L187`; `x-full-archive-search §7 L139`); c) route values "GREEN", "AMBER", "RED" (`L7`), green or amber (`L36`), `shared` in the PRD header template, with six lanes (`L122`) against seven in the addendum (`L275`); d) the platform prefix rule (`L11`) against search-hit-router under Web (`L234`); e) README sentences on Google results (`README L18` against `L143` to `L147` and `CONVENTIONS L217`), tt-hashtag-feed-poller (`L70` against `L22`, `L30`) and the nine decisions being "consistent" (`L176`). D1's review note 17 adds that `docs/contracts/INVENTORY.md` lists "Known corrections from the review" (L20 to L34) without applying them to its rows.

Settles: CF-027, CF-117, RN-17.

## Options

1. **One editorial pass, each point decided here so F2 has one spelling** (chosen): its rules are under Decision.
2. **A blanket rule for CF-027: the section 6.2 example always wins** (or the prose always wins), with CF-117 as in option 1. Consequences: simpler to state, but the example rule deletes `text_full_ref` and `lang_pending`, which ADR-0022 relies on, and the prose rule keeps `set_version` beside a message id that no longer embeds it.
3. **Leave the documents and let each owning session pick.** Consequences: no edits now, but F2 freezes before those sessions run, so it would guess, and sessions keep quoting the inconsistent lines.

## Decision

One editorial pass: each place where a document disagrees with itself gets one answer here, so F2 has one spelling for every field, and the PRD, CONVENTIONS and README lines are corrected in this pull request, each edit citing this ADR.

- CF-027: a) `keyword_set_version`, rendered `cs:<hex>`, with keyword-matcher's replay-stable `message_id` derived from it (ADR-0002, ADR-0006); b) `crawl.policies` uses the flat names of the `crawl_policies` row (ADR-0040), `robots_status`, each Content-Signal directive mapped by replacing the hyphen with an underscore (`ai_input`, `ai_train`, `search`), stated once; c) `normalize = skip` disappears, the engines' responses taking the archive-only record kind of ADR-0008; d) `lang_pending` and `text_full_ref` join `items.normalized/v1`, and `author_followers` only for registered sources (ADR-0010); e) `window` is a declared `context` field (ADR-0005); f) each update is written as returned, an edit reusing the post's key (ADR-0009); g) moot, there is no `raw.replay` topic (ADR-0039); h) `extractor` and `extractor_version`; i) web-commoncrawl-scanner's reads gain `source.events`.
- CF-117 a): replies are job kind `replies` on the comment service's queue, except where a route has a dedicated replies service, which CONVENTIONS lists (YouTube); X's reply steps after +3 d go to `jobs.x-full-archive-search` with `window_start` (ADR-0059, ADR-0060). Rejected: a replies service on every route, services with no API of their own.
- b): the cap is "per billing cycle", the term of CONVENTIONS L87 and `quota-governor §5.3 L78`, and quota-governor's period follows the cycle; L187 is aligned. Rejected: per calendar month, which would mis-time the cap whenever the cycle does not start on the 1st.
- c): lower-case `green` and `amber` in data; "RED" stays prose for what is never built; `shared` is a header label only; seven lanes, the template updated. Rejected: `shared` as a `route` value, which no data record needs since every fetch is green or amber, and six lanes, which would re-label tt-video-stats-refresher.
- d): search-hit-router keeps its name as the one listed exception to the prefix rule, since it routes results of several platforms. Rejected: `web-search-hit-router`, which edits every PRD naming it and implies web only.
- e): the README's sentences reworded to match the service lists and point to D2. RN-17: `INVENTORY.md` stays D1's record "as written in the PRDs"; CONVENTIONS v1.1 names the ADRs, CONVENTIONS, F2's `VERSIONING.md` and F3's `TABLE-OWNERS.md` as the contract, the inventory as background.

Why: Each answer matches how the PRDs behave and what the other decisions decide, and F2 needs one spelling before it freezes; fixing the text once is cheaper than every session asking.

## Consequences

One pass by phase 2; nothing in the contracts changes except the route enum's case.

- CONVENTIONS v1.1: v1 L7, L11, L60, L87 and L187, L122, L234 and L275, and a sentence naming the contract documents (the ADRs, CONVENTIONS, F2's `VERSIONING.md` and F3's `TABLE-OWNERS.md`; the inventory as background).
- `docs/prds/README.md` L18, L22, L30, L70 and L176 reworded, each citing this ADR; the README's proposed decisions point to the ADRs that decided them.
- The CF-027 lines of the nine PRDs are corrected in this pull request, each citing this ADR; F2 takes the spellings from here.

Sessions that must read this: F2 first (one spelling per field), then F5, C1, C2, C4, C5, FB3, N1, N6, TG1, W1, W2, W4, W5, YT5, YT6 (and every session that quotes CONVENTIONS or the README literally).
