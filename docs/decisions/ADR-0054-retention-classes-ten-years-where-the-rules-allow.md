# ADR-0054 · Retention classes: ten years where the rules allow

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all (every record carries a `retention_class`), F3, F8, I1, retention-purger, store-writer, raw-archiver, deletion-propagator, aggregator, tt-client-videos-fetcher, tg-bot-channel-receiver, tg-discussion-receiver, web-search-perplexity, web-search-mojeek, web-gdelt-poller
Source: D2-Q054 (user decision; changed by the user's answer) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

Every record carries a `retention_class` chosen by route (`CONVENTIONS L247`), and the six classes (`CONVENTIONS L75` to `L80`) name none for three routes:

- TikTok Display API (green, client-authorised accounts): README decision 8 proposes `tiktok_display` (`README L185`); tt-client-videos-fetcher writes it, "proposed and not yet in `retention_classes`" (`tt-client-videos-fetcher §6.2 L106`, `L115`), kept "while the authorisation is active and deleted on revocation, client offboarding or TikTok's request, as `meta_on_request` does" (`§14 Q2 L177`).
- Telegram Bot API (green, channels and groups whose owners added the bot): both receivers write `vendor_agreed` (`tg-bot-channel-receiver §6.2 L125`, `tg-discussion-receiver §6.2 L129`), a class defined "per the vendor contract" with a default of 24 months for raw text (`CONVENTIONS L79`), although no vendor is involved; both ask for a dedicated class (`tg-bot-channel-receiver §14 Q5 L198`, `tg-discussion-receiver §14 Q5 L202`).
- Web-search results (Perplexity, Mojeek, GDELT): they carry `news_excerpt` (`web-search-perplexity §6.2 L106`, `web-search-mojeek §6.2 L105`, `web-gdelt-poller §6.2 L109`), whose only clock is the 7-day full-text cache (`retention-purger §5.3 L67`), for records that hold a title, a snippet and a URL but no full text; retention-purger leaves both open "to be set with counsel" (`retention-purger §14 Q3 L172`).

The user's answer, 7 Oct 2026: "Q054, Q055, and Q056 data retention should be up to 10 years." Asked again, the user chose "10 years where allowed": every item is kept 10 years on X, Meta, Telegram, news, web and vendor routes, with deletion requests honoured; YouTube, LinkedIn and TikTok items are kept as long as their terms allow, and their counts and trends are kept 10 years. The answer covers ADR-0054 to ADR-0056 together: this ADR records the classes, ADR-0055 LinkedIn's and ADR-0056 the lifetimes of derived data.

Settles: CF-104, retention-purger §14 Q3, tg-bot-channel-receiver §14 Q5, tg-discussion-receiver §14 Q5, tt-client-videos-fetcher §14 Q2.

## Options

1. **Add `tiktok_display` and `telegram_bot`; keep web results under `news_excerpt`.** _Taken for its two new classes and for web results, under the ten-year default the user set (see Decision); its `telegram_bot` clock, which ended when the bot left the channel or its owner removed it, is not._ `tiktok_display`: kept while the client's authorisation is active; deleted on revocation, client offboarding or TikTok's request (the `meta_on_request` clock under TikTok's name). `telegram_bot`: kept while the bot stays in the channel; for a client's own channel also only while the client relationship lasts, and for a cooperating channel whose owner agreed to add the bot (`tg-bot-channel-receiver §1 L9`) until the owner removes it or asks; deleted on the owner's or client's request, on offboarding, or on a member's request; commenters' identities are already hashed at the edge (ADR-0010). Web results stay `news_excerpt`, with CONVENTIONS stating that the class keeps excerpts and metadata and that its 7-day clock applies only where full text is cached. Consequences: F3 seeds two more classes; each route's clock matches its terms; counsel reviews the two new clocks before production (G4).
2. **Add all three, with a `web_result` class of its own.** _Not taken._ Consequences: as option 1, plus a clock for web snippets that can differ from news excerpts (for example a shorter one if a search provider's terms require it).
3. **Map each route to an existing class.** _Not taken._ `tiktok_display` as `meta_on_request`, Telegram bot data as `vendor_agreed`, web results as `news_excerpt`, with the mapping written in CONVENTIONS. Consequences: no new classes, but Telegram bot data keeps a vendor-contract clock with no vendor behind it (24 months by default), and the provenance statement names Meta's rule for TikTok data.

Also not taken: the lifetimes CONVENTIONS v1 gives the existing classes (L75 to L80): `x_24h_sync` with nothing purged by time, `meta_on_request` deleted when no longer necessary, `vendor_agreed` with a 24-month default for raw text. The user set ten years as the default lifetime of stored items wherever the rules allow, so items, not only aggregates, can be kept ten years.

## Decision

Ten years is the default lifetime of every stored item, except where a platform's terms, a vendor contract or copyright set a shorter limit, which then applies; every aggregate and rollup keeps ten years, YouTube's per-channel rollups excepted (ADR-0056). Two classes are added, `tiktok_display` and `telegram_bot`, and web results stay under `news_excerpt`. Every class honours deletion requests, and counsel confirms each reading before production (G4).

| Class                          | What it holds                                                                   | How long                                                                                                                                                                                          |
| ------------------------------ | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `meta_on_request`              | Meta Platform Data: Facebook Pages and Instagram on the green route             | until a deletion request, at most ten years: deleted on Meta's request, on the person's request (ADR-0069) and at the offboarding of the client it was fetched for (ADR-0053)                     |
| `vendor_agreed`                | data bought from a vendor, LinkedIn's excepted (ADR-0055)                       | per the vendor contract and our author notice: ten years where the contract allows it, otherwise the contract's limit; each vendor contract is checked                                            |
| `x_24h_sync`                   | X content                                                                       | ten years, with X deletions applied within 24 hours (ADR-0069 (c))                                                                                                                                |
| `news_excerpt`                 | news excerpts and metadata, and web-search results (title, snippet, URL)        | excerpts and metadata ten years; the 7-day full-text cache stays, for copyright, and applies only where full text is cached (ADR-0022)                                                            |
| `telegram_bot` (new)           | the posts and comments our bot receives in channels and their discussion groups | ten years; deleted on the channel owner's, a member's or the client's request, and at offboarding                                                                                                 |
| `tiktok_display` (new)         | a client's own TikTok videos and their stats, through the Display API           | while the client's authorisation lasts, within the ten years; deleted on revocation, as TikTok's terms require (reason `authorization_revoked`, ADR-0035), at offboarding and on TikTok's request |
| `linkedin_48h`, `linkedin_org` | LinkedIn member content; LinkedIn organisation posts                            | LinkedIn's limits: 48 hours; six weeks, or six months if counsel confirms (ADR-0055)                                                                                                              |
| `youtube_30d_text`             | YouTube items                                                                   | text refreshed or deleted at 30 days; item rows and item-level derived rows 36 months (ADR-0056)                                                                                                  |

- Ten years is a ceiling, not a promise: a deletion request (a person's, a client's or a platform's) removes what it names in any class (ADR-0035, ADR-0069), and a class with a shorter limit keeps its limit.
- A record's class still follows its route (CONVENTIONS v1 L247), except LinkedIn's, which follows its content (ADR-0055). Item-level derived rows follow their item's class, and aggregates keep ten years (ADR-0056).
- The raw archive and its copy (ADR-0027) and ClickHouse (ADR-0029) keep each item as long as its class allows, so up to ten years.
- `telegram_bot` replaces `vendor_agreed` on the two Telegram receivers (`tg-bot-channel-receiver §6.2 L125`, `tg-discussion-receiver §6.2 L129`). Removing the bot from a channel ends collection, not the data, which goes on a request or at offboarding.
- Web results keep `news_excerpt`, worded for records with no full text: the class keeps excerpts and metadata, and its 7-day clock applies only where full text is cached.

Why: The user wants history kept as long as the rules allow, not only as aggregates. Ten years wherever the routes' terms, contracts and copyright allow it, and each platform's own limit where it is shorter, gives clients the longest history the platform can defend, while deletion requests stay honoured everywhere.

## Consequences

Items, not only aggregates, stay available up to ten years wherever the rules allow; the stores grow accordingly, and I1 sizes them for it (ADR-0027, ADR-0029); counsel reviews every reading before production.

- CONVENTIONS v1.1: the retention target (v1 L3) and the retention classes (v1 L73 to L81) rewritten as the table above.
- F3 seeds `retention_classes` with these clocks (ADR-0045); F8 sets the ClickHouse TTLs from them; retention-purger, store-writer and raw-archiver apply them.
- tt-client-videos-fetcher writes `tiktok_display`; tg-bot-channel-receiver and tg-discussion-receiver write `telegram_bot`.
- `DEFERRED.md`, counsel's confirmation of each reading before production (G4): Meta's "delete when no longer necessary" (CONVENTIONS v1 L163) under a ten-year ceiling with deletion on request, with the grace period of ADR-0069 (e) if counsel sets a necessity clock; the limit in each vendor's contract (one entry per vendor); ten years for X content with deletions mirrored; ten years for news excerpts and metadata under Law No. 3 of 1971, and for web results under the engines' terms; the `telegram_bot` and `tiktok_display` clocks.

Sessions that must read this: F3 (it seeds `retention_classes`), F8 (TTLs by class), C6, C14, then TT1, TG1, TG2, W1, W2, W3, W4, YT9, C2, C13, I1.
