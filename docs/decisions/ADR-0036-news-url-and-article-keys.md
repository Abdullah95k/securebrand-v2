# ADR-0036 · News URL and article keys

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, normalize-item, search-hit-router, web-commoncrawl-scanner, and news: news-feed-poller, news-sitemap-poller, news-homepage-differ, news-article-extractor, news-dedup, news-site-resolver
Source: D2-Q036 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

The article key is `news:article:<canonical_url_hash>` (CONVENTIONS L69), with no rendering for the hash: news-article-extractor and news-dedup write bare hex (`news-article-extractor §6.2 L98`, `news-dedup §6.2 L90`), while search-hit-router writes `news:article:sha256:<hex>` (`search-hit-router §6.2 L123`) against its own prose and test (`§9 L159`, `§13 L184`). The news pollers key `article.urls` by a URL-level `url_key = news:url:<sha256 of normalised URL>` (`news-feed-poller §9 L142`; CF-118). `article.urls` has two layouts: the pollers' `{envelope, payload}` with `url_key`, `found_via` and `found_at` and no schema name (`news-feed-poller §6.2 L94-L112`), and the router's flat `article.urls/v1` with `idempotency_key`, `found_by` and `first_seen_at` and no provenance or class (`search-hit-router §6.2 L119-L131`); the extractor orders its work by `found_via` and `found_at` (`news-article-extractor §5.1 L43`), and CONVENTIONS lets source finders write `discovery.hits` only (L281; CF-022). normalize-item maps a `date` field the extractor writes as `published_at` (`normalize-item §5.3 L72`, `news-article-extractor §6.2 L114`; CF-028). The extractor's ledger `news_urls` is keyed by `url_hash` (`news-article-extractor §5.2 L51`, `§6.3 L129`), possibly the same hash as `url_key` (RN-10). Copies naming another URL as canonical are recorded `duplicate_canonical`, a status the ledger lacks, and news-dedup's sweep would add them under the origin's key, its members' primary key (`news-dedup §5.3 L64`, `§6.3 L108`; AU-106). Four PRDs count on `not_article` rates reaching news-site-resolver, which reads no outcome (`news-article-extractor §6.2 L125`, `news-site-resolver §6.1 L75`; AU-105). What is at stake: one article under three keys that never compare equal.

Settles: CF-022, CF-028, CF-118, AU-105, AU-106, RN-10, news-dedup §14 Q3.
Depends on: ADR-0003 (provenance), ADR-0059 (the Common Crawl URL lister for news history).

## Options

1. **Bare hex everywhere, one URL key on `article.urls`, one ledger hash** (chosen, with the Common Crawl URL lister of ADR-0059 as a fourth finder): its rules are under Decision.
2. **The `sha256:` rendering everywhere (`news:article:sha256:<hex>`, `news:url:sha256:<hex>`) and the pollers' envelope as the one layout (CF-118 option 2, CF-022 option 1).** Consequences: CONVENTIONS L69, the extractor and news-dedup change, for a key that names its algorithm.
3. **search-hit-router stops writing `article.urls` and hands news URLs to the news finders (CF-022 option 3).** Consequences: matches L281's wording, but an article that search found waits until the site's own feed lists it (`search-hit-router §1 L11`), and the finders need an input they lack.

## Decision

Article keys are bare hex everywhere, built by the contracts package's key helper. `article.urls/v1` is one flat message for every finder, keyed by one URL key, and the extractor's ledger `news_urls` uses the same URL hash.

- Keys: `news:article:<64 lower-case hex>`, built by the contracts package's key helper (ADR-0006); search-hit-router strips `sha256:`, and `canonical_url_hash` is bare hex on `search.results` and `article.urls` too (ADR-0037).
- `article.urls/v1`, flat, one schema for the three pollers, search-hit-router and web-commoncrawl-scanner's news-history lister (ADR-0059): ADR-0002's metadata, `source_id` (the site), `url`, `url_key`, `found_via` (closed: `feed`, `news_sitemap`, `homepage_diff`, `sitemap_backfill`, `web_search`, `commoncrawl`; `commoncrawl` is written by web-commoncrawl-scanner, which lists a site's captured article URLs from the Common Crawl index for the part of its 90 days the sitemaps do not reach, ADR-0059 and ADR-0020), `found_at`, provenance and `retention_class` (ADR-0003); optional finder fields (`title`, `published_at`, `feed_url`, `feed_format`, `canonical_url`, `canonical_url_hash`, `snippet`, `engines`, `keyword_ids`, `client_ids`). The router maps `found_by` to `found_via = web_search` and `first_seen_at` to `found_at`, and CONVENTIONS L281 names it, and web-commoncrawl-scanner, as writers of `article.urls`. The message carries no article key: the extractor derives it from the canonical URL it reads on the page (`news-article-extractor §5.2 L57`), which may differ from the engine's URL, so the router's `idempotency_key` goes. The access mode comes from `crawl_policies` (ADR-0040).
- RN-10: one SDK helper, `url_hash = sha256(normalised URL)`, with one normaliser for every finder and the extractor; `url_key = news:url:<url_hash>`, and `news_urls` is keyed by `url_hash`.
- normalize-item maps `published_at` (an approved PRD moves under ADR-0001).
- Same-canonical copies: `news_urls.status` gains `duplicate_canonical`; the copy keeps its own `url_key`, under which the sweep adds it to `news_story_members` (text fields null, `matched_by = canonical`), so it never collides with the origin's key.
- `not_article` feedback, no new message: the extractor's outcomes are its `news_urls` rows, and news-site-resolver reads them for the site (`status`, `found_via`) on every refresh and infers patterns from accepted and `not_article` URLs, which also gives homepage-diff sites patterns. news-site-resolver adds the read (an approved PRD moves under ADR-0001).

The proposal assumed no Common Crawl lister in v1. ADR-0059 adds one, so `commoncrawl` has a producer, and the extractor already fetches `sitemap_backfill` and `commoncrawl` finds after live ones (`news-article-extractor §5.1 L43`).

Why: It is what the extractor, news-dedup and the three pollers already write, it removes the one key that never matches, and it leaves the extractor alone to decide what an article is.

## Consequences

One key per article and one per found URL; the pollers' envelope and the router's flat message become one message; the router's test and prose change.

- CONVENTIONS v1.1: the `article.urls` message (v1 L25); bare hex in the article key, and the `news:url:` key (v1 L69); search-hit-router and web-commoncrawl-scanner as writers of `article.urls` (v1 L281). RN-10 is closed.
- F2 types `article.urls/v1` with its closed `found_via` list and ships the URL normaliser and `url_hash` helper with golden vectors; F3 adds `duplicate_canonical` to `news_urls.status`.

Sessions that must read this: F2, F3, C4, N2, N3, N4, N5, N6, N7, N8, W3, W5.
