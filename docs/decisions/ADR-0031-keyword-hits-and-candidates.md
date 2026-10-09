# ADR-0031 · Keyword hits and candidates

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, keyword-matcher, poster-resolver, store-writer, analysis-sentiment, tg-bot-channel-receiver, tg-discussion-receiver, and the lane Discover and qualify (every search service and source finder)
Source: D2-Q031 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS splits hits by whether the poster is registered (L17, L18) and makes keyword-matcher "the canonical writer of `item.hits` and `discovery.hits` for items", with early signals from x-recent-search and tg-message-search and candidates from three source finders (L281). The PRDs depart from this:

- Writers. tg-message-search also writes `item.hits` (`tg-message-search §5.2 L55`), so one Telegram post gives two hits in two shapes (CF-009 a); ig-hashtag-search and the two Telegram receivers write `discovery.hits` without being listed (CF-010 b; client onboarding is ADR-0066's).
- Meaning. keyword-matcher sends comments and author-less items to `item.hits` as individuals' mentions (`keyword-matcher §5.3 L75`, `§14 Q3 L182`), which L17 does not cover, while a mention on an unregistered poster's post exists only on the candidate topic.
- Shape. Seven layouts, two under one schema name, three partition keys (CF-011). The source finders defer to "poster-resolver's approved schema" (`search-hit-router §6.2 L134`, `web-commoncrawl-scanner §6.2 L103`), which does not exist (`poster-resolver §6.1 L81`; AU-008). analysis-sentiment reads `matched_text`; keyword-matcher writes `matched_term` (`analysis-sentiment §5.2 L59`, `keyword-matcher §5.3 L65`; AU-006).
- Gaps. x-recent-search's `context.discovery_hit_emitted` flag never reaches keyword-matcher (`x-recent-search §5.2 L58`; AU-005); two PRDs name readers that read other topics (AU-012); a hashtag-feed video is a hit "without text matching" for tt-hashtag-feed-poller (`tt-hashtag-feed-poller §4 L34`) but needs a match in keyword-matcher (AU-054); nobody emits the group behind an amber group hit, so rule 8 never fires (`fb-keyword-search §1 L9`, `qualifier §5.2 L59`; AU-061).

What is at stake: mentions counted twice or not at all, and a poster-resolver that cannot decode its own input.

Settles: CF-009, CF-010, CF-011, AU-005, AU-006, AU-008, AU-012, AU-054, AU-061, analysis-sentiment §14 Q7, fb-keyword-search §14 Q5, keyword-matcher §14 Q2, keyword-matcher §14 Q3, search-hit-router §14 Q3, tt-hashtag-feed-poller §14 Q4, web-commoncrawl-scanner §14 Q3, yt-channel-resolver §14 Q1.
Depends on: ADR-0010 (`author_ref`), ADR-0032 (candidate keys and the group resolver), ADR-0044 (the keyword behind a hashtag source).

## Options

1. **Every keyword hit on `item.hits`; `discovery.hits` carries candidates only** (chosen): its rules are under Decision.
2. **CONVENTIONS' split kept, with keyword-matcher's `discovery.hits/v1` as the one schema, `candidate` required and source-finder fields optional (CF-011 option 1).** Consequences: fewer moves, but store-writer must store some `discovery.hits` messages and drop others, one schema serves two purposes, and the pending-candidate message stays.
3. **tg-message-search keeps writing `item.hits`, and keyword-matcher skips items whose producer already did (CF-009 option 2).** Consequences: two writers to keep in step, and a skip rule resting on a flag that, as AU-005 shows, does not travel.

## Decision

Every keyword hit on an item is one `item.hits` message, written only by keyword-matcher, whoever the poster is; `discovery.hits` carries candidate sources only, in one F2 schema keyed by `candidate_key`, from the writers named below.

- `item.hits/v1` is keyword-matcher's message (`keyword-matcher §6.2 L97-L117`) with `poster {author_ref, author_type, author_source_id}` and a new `matched_by` (`text` or `source`): one per (item, client, keyword), keyed by `source_id`, whoever the poster is; comments and individuals' posts carry `author_ref` only. keyword-matcher is its only writer; tg-message-search stops. store-writer fills `hits` from this topic only (ADR-0047), and analysis-sentiment reads only this topic.
- `discovery.hits/v1`, one F2 schema for every candidate, keyed by `candidate_key` (a named exception in ADR-0004): `candidate {candidate_key, platform, type, platform_id, handle, url}`, `evidence_type` (closed: `keyword_hit`, `container`, `early_signal`, `page_search`, `web_search`, `commoncrawl`), `item_id` or `url`, the producing `source_id`, `keyword_ids`, `client_ids`, `hit_at`, provenance and `retention_class` (ADR-0003), and one optional typed `evidence` block per type. `poster`, `poster_ref`, `origin`, `found_at`, `item_idempotency_key` and the singular client and keyword fields go.
- Writers: keyword-matcher, once a poster's identity is readable (the `candidate_pending` message goes, since the mention is already out); x-recent-search and tg-message-search as early signals, both kept, poster-resolver deduplicating by `candidate_key` (the flag goes); fb-page-search, search-hit-router, web-commoncrawl-scanner. ig-hashtag-search writes none: its media of unmanaged accounts name no poster (`ig-hashtag-search §6.2 L124`) and stay mentions with a null `author_ref`; its caption-handle path (`§12 L169`) goes, as a handle in a caption is not the poster. The Telegram receivers write none: client onboarding takes registry-writer's manual path (ADR-0066). A web result that ADR-0038 turns into a `web` item raises no candidate for its domain: search-hit-router writes a candidate only for a platform account or a news site it routes.
- Groups: for a hit on a post in an unregistered Facebook group, keyword-matcher also emits a `container` candidate `facebook:group:<id>`, read from the raw record; ADR-0032 gives it a resolver.
- Hashtag sources: an item from a hashtag source is a hit for each client of that source who passes the client gate, under the source's keyword (ADR-0044), with `matched_by = source` when the text does not match; the `hit_id` formula (`keyword-matcher §5.3 L77`) makes the two one hit.
- `matched_term` plus `offsets` in `text_norm` is the one form; analysis-sentiment cuts its window from `offsets`.
- Readers: `raw.items` is read by normalize-item, raw-archiver and news-dedup, `discovery.hits` by poster-resolver; the PRDs' reader lists are corrected.

It also answers: keyword-matcher reads an unregistered poster's id from a transient `poster_platform_id` field that normalize-item sets on `items.normalized` only for posters not yet classed, and that store-writer never stores; `candidate_pending` is dropped (`keyword-matcher §14 Q2`).

Why: Each topic gets one meaning, a mention for a client or a candidate for the registry, so a mention counts once wherever its poster stands, and every candidate reaches poster-resolver in one layout, ordered per candidate.

## Consequences

One counting path for mentions; one candidate message per item and candidate, not per client and keyword; approved PRDs move under ADR-0001 (tg-message-search, x-recent-search, ig-hashtag-search, fb-page-search, tt-hashtag-feed-poller, poster-resolver's partition note, and the "split into `item.hits` or `discovery.hits`" reader lines of tt-keyword-search, li-post-search and yt-keyword-search).

- CONVENTIONS v1.1: the meanings of `item.hits` and `discovery.hits` (v1 L17, L18), a mention for a client whoever the poster is and a candidate for the registry; the search output rule (v1 L281): keyword-matcher the only writer of `item.hits`, the named writers and early signals of `discovery.hits`, and no `item.hits` from a search service; the partition note of the topic list: `discovery.hits` by `candidate_key`.
- F2 types `item.hits/v1` with `matched_by`, `discovery.hits/v1` with the closed `evidence_type` list, and the transient `poster_platform_id` on `items.normalized/v1`.

Sessions that must read this: F2, F4, C4, C5, C6, C7, C8, C9, A1, A5, FB6, VFB1, VFB2, IG2, VTT2, X1, TG1, TG2, VTG1, W3, W5.
