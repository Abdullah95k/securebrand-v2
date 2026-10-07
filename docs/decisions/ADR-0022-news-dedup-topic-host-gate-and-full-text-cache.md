# ADR-0022 · News: dedup topic, host gate and full-text cache

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F8, listening-sdk (F4, F5), news, normalize-item, store-writer, aggregator, alert-evaluator, keyword-matcher, analysis-sentiment, analysis-topics, analysis-entities, analysis-media, deletion-propagator, retention-purger
Source: D2-Q022 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

README decision 6 proposes three things (`README L183`), and D1 found a conflict in each:

- The topic `news.dedup`, from news-dedup "to normalize-item". news-dedup writes one message per verdict and per `story_update` (`news-dedup §6.2 L84` to `L101`) and expects normalize-item to copy the story fields onto the item and re-emit a version on updates (`§6.2 L104`), "with a bounded wait", or else drop the topic for a table-only join (`§14 Q1 L167`). normalize-item reads no such topic and has no story fields (`normalize-item §6.1 L86`; CF-025); aggregator and alert-evaluator expect them (AU-003).
- A per-host gate in listening-sdk, one connection and 2 to 5 seconds between requests. Only news-article-extractor doubles the spacing after a 429 or 503 (`news-article-extractor §5.3 L65`; CF-092 d). Which errors re-check the crawl policy differs: news-robots-checker wants a `recheck` on every 4xx, 429 included, and on a feed or sitemap 404/410 (`news-robots-checker §5.1 L47`); the fetchers back off on 429 and send a feed, sitemap or homepage 404/410 to news-site-resolver as `refresh` (`news-feed-poller §8 L131`, `news-sitemap-poller §8 L144`), while news-feed-poller's test says "Any 4xx from a host produces one `recheck` job" (`§13 L170`; CF-092, AU-104).
- news-article-extractor owns the 7-day full-text cache (`news-article-extractor §5.3 L75`) and passes `text_full_ref`, yet it and normalize-item still ask who owns it (`news-article-extractor §14 Q3 L189`, `normalize-item §14 Q2 L179`); news-comments-fetcher writes a second cache under `cache/news/comments/` (`news-comments-fetcher §5.2 L57`, `§6.2 L113`); and whether keyword-matcher and the analysis services may read it is open (`news-article-extractor §14 Q1 L187`, proposed yes, "to be confirmed with counsel"; CF-111, AU-055).

Settles: RD-6, CF-025, CF-092, CF-111, AU-003, AU-055, AU-104, news-article-extractor §14 Q1, news-article-extractor §14 Q3, news-dedup §14 Q1, normalize-item §14 Q2.

## Options

1. **Keep all three, with these precisions** (chosen): its rules are under Decision.
2. **README decision 6 as written: normalize-item consumes `news.dedup` with a bounded wait and re-emits story fields as item versions.** Consequences: story fields reach every consumer of `items.normalized`, at the cost of a wait and a second emit in the busiest shared service; the gate and cache as in option 1.
3. **No topic: store-writer (or readers) join news-dedup's `news_story_members` table when they need stories.** Consequences: one topic fewer, but a cross-database join from ClickHouse readers into Postgres, and story updates are not events; the gate and cache as in option 1.

## Decision

README decision 6 stands in all three parts: store-writer consumes `news.dedup` into a ClickHouse table `item_stories`, the per-host gate lives in the SDK with one rule for errors, and each news cache has one writer and its own prefix, with keyword-matcher the only reader of the 7-day full text.

- `news.dedup` joins the topic list, keyed by `story_id`. store-writer, not normalize-item, consumes it and writes a separate ClickHouse table, `item_stories` (`item_id`, `story_id`, `is_origin`, `duplicate_of`, `cluster_size`, `version`), one row per item, versioned like `items` so a `story_update` replaces the older row. aggregator and alert-evaluator join it to `items` on `item_id`. A content version from `items.normalized` (`normalize-item §5.2 L52`) and a story version never overwrite each other. news-dedup's `news_story_members` stays its own store; normalize-item stays a pure mapper with no wait.
- The host gate lives in the SDK, for every news service: one connection per host, 2 to 5 seconds between requests or the host's `Crawl-delay`, and the spacing doubles after a 429 or 503 until a success. A 429 or a plain 503 backs off and never re-checks the policy; a 401, 402, 403, 451, any other 4xx not named here, or a challenge page whatever its status (Cloudflare's can be a 503) sends one `recheck` per host (coalesced) and stops the batch (`news-feed-poller §8 L132`); a 404 or 410 on a feed, sitemap or homepage sends `refresh` to news-site-resolver; a 404 or 410 on an article does neither.
- Each cache writer owns its prefix, news-article-extractor `cache/news/`, news-comments-fetcher `cache/news/comments/`; both are registered in the SDK purge registry with the 7-day clock and deletion by `item_id`. Only keyword-matcher reads the cache, within the 7 days, and persists only derived values (hit offsets), so a brand named after the excerpt is still matched (AU-055). The analysis services read the stored title and excerpt, never the cache, "so a re-run reproduces live analysis" (`analysis-sentiment §5.1 L51`). Counsel confirms this reading of Law No. 3 of 1971 before G2 (`DEFERRED.md`, owner N6).

Why: It keeps every part of the README proposal, gives the topic a consumer that already writes to ClickHouse while keeping story and content versions apart, fixes the gate once for all five news services, and lets matching see full text while analysis stays reproducible.

## Consequences

One news topic with a consumer, and one more ClickHouse table for F8; one gate; two registered cache prefixes; full-text matching within the cache window. News sentiment, topics and entities rest on the title and the 200 to 300 character excerpt (CONVENTIONS L213): shallower scores on long articles, but every score is reproducible after the cache expires.

- CONVENTIONS v1.1: `news.dedup` in the topic list; `item_stories` among the analytics tables; the host gate and its error rules under the news fact sheet; the cache prefixes and their readers under object storage. The 7-day full-text cache stays under ADR-0054's `news_excerpt` class, for copyright.
- `DEFERRED.md`: counsel confirms keyword matching over the cache under Law No. 3 of 1971 before G2 (owner N6).

Sessions that must read this: F2 (the topic), F8 (`item_stories`), F4 and F5 (the host gate and the cache client), C4, C5, C6, C13, C14, C15, A5, then N1 to N8, A1, A2, A3.
