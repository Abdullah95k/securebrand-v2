# ADR-0047 · ClickHouse columns, purges and tables

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F8, listening-sdk (F4), store-writer, aggregator, alert-evaluator, deletion-propagator, retention-purger, yt-text-purger, x-compliance-sync, qualifier, keyword-matcher, ig-comments-fetcher, yt-comments-fetcher, normalize-item, poster-resolver, search-hit-router, web-commoncrawl-scanner, fb-page-search
Source: D2-Q047 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

- Purges (CF-049). deletion-propagator's `purge_text` empties `text`, `text_norm`, `author_hash` and `url` (`deletion-propagator §5.3 L62`); store-writer's content TTL blanks eleven columns, `title` among them (`store-writer §5.3 L71`); yt-text-purger nulls `text`, `text_norm` and the author reference and counts a video's title and description as `text` (`yt-text-purger §5.3 L108`, `L69`), while normalize-item maps `snippet.title` to `title` (`normalize-item §5.3 L71`). So a purged YouTube video keeps its title. The author column is `author_ref` in store-writer (`store-writer §6.2 L110`) and `author_hash` in deletion-propagator, x-compliance-sync and retention-purger (`deletion-propagator §5.3 L60`, `x-compliance-sync §5.3 L81`, `retention-purger §5.3 L78`).
- Tables (CF-051). `CONVENTIONS L32` lists seven. store-writer adds `hits`, keyed (`client_id`, `keyword_id`, `item_id`) and fed by both hit topics (`store-writer §5.3 L63`, `§14 Q1 L181`), though source finders send discovery hits with no item (`CONVENTIONS L281`); aggregator writes daily and monthly tables and a refreshable view (`aggregator §6.2 L77`, `§5.3 L59`); alert-evaluator reads `_v` views no PRD defines (`alert-evaluator §6.1 L78`).
- Names (CF-052). The qualifier's daily sweep reads `max(published_at)` (`qualifier §5.3 L67`) and ig-comments-fetcher a `permalink` (`ig-comments-fetcher §5.2 L58`); store-writer creates neither, and the message has `created_at` and `url` (`normalize-item §6.2 L105-L106`). yt-comments-fetcher calls `comments` "keyed by `parent_id`" (`yt-comments-fetcher §4 L34`) where `item_id` is the key (`store-writer §5.3 L60`, `CONVENTIONS L70`).

At stake: the sweep that drives dormancy for every source queries a column that does not exist, a YouTube title outlives the 30-day rule, and F8 needs one list.

Settles: CF-049, CF-051, CF-052, keyword-matcher §14 Q1, store-writer §14 Q1.
Depends on: ADR-0010 (`author_ref` and `public_accounts_dim`), ADR-0011 (`post_ref.url`), ADR-0031 (item hits), ADR-0035 (tombstones and the guard), ADR-0048 (the alert types that read `metrics_timeseries` and `item_stories`), ADR-0056 (what YouTube's 30-day rule covers).

## Options

1. **store-writer's columns are the contract, one purge list per class, `hits` for item hits only, aggregates and views in the contract** (chosen): its rules are under Decision.
2. **Readers' names added as alias columns (`published_at`, `permalink`), and two purge lists kept on purpose, both written into CONVENTIONS (CF-052 (2), CF-049 (2)).** Consequences: no reader edits, but two names for one fact, and the YouTube title still needs a rule for which list it is on.
3. **One `hits` table with a nullable `item_id` and a `candidate_key` (CF-051 (2)), and no `_v` views, readers querying with `FINAL` (CF-051 (3)).** Consequences: candidate evidence becomes countable beside client hits and collapses under one key, and every reader repeats the version logic a view would hold once.

## Decision

store-writer's column list is the ClickHouse contract, published by F8; the SDK holds one purge field list per retention class, used by every executor; `hits` holds item hits only; the aggregate tables and the `_v` views join the contract.

- Names: F8 publishes store-writer's list (`store-writer §5.3 L60` to `L67`, example `§6.2 L99-L119`) as the contract, with its flattenings stated once (`author` into `author_ref`, `author_type`, `author_source_id`; `expires_at` as `content_expires_at`; `row_expires_at`; counts projected from `metrics_snapshot`). Readers use those names: the sweep reads `max(created_at)` (the approved qualifier moves under ADR-0001), ig-comments-fetcher takes the post's `url` from `post_ref` (ADR-0011) rather than a `permalink` column, and "keyed by `parent_id`" means looked up through the bloom index.
- The author column is `author_ref` everywhere (ADR-0010): deletion-propagator selects by it, and x-compliance-sync and retention-purger send `author_ref` targets.
- Purges: the SDK holds one field list per class, used by every executor (store-writer's column TTL, deletion-propagator's `purge_text`, yt-text-purger). For `youtube_30d_text` it is `text`, `title`, `text_norm`, `hashtags`, `at_mentions`, `links` and `author_ref`, so titles and descriptions go with the text (ADR-0056); `platform_id` and `url` stay, because the refresh re-reads by id, and counts follow the derived data. For the other classes with a content clock it is store-writer's full list (`store-writer §5.3 L71`). deletion-propagator's step (c) uses the item's class list. Tombstones and the resurrection guard are ADR-0035's.
- `hits` holds item hits only, from `item.hits`, keyed as store-writer proposes. Every match a client sees is an item hit, whoever the poster is (ADR-0031); `discovery.hits` carry candidates only, for poster-resolver, and stay out of ClickHouse.
- `aggregates_daily`, `aggregates_monthly` and `mv_aggregates_hourly` (aggregator) and the `_v` views (aggregator's over the aggregate tables; store-writer's `items_v` and `comments_v`, `store-writer §5.3 L82`) join the CONVENTIONS list, and F8 creates them. A `_v` view returns the latest version per key, and the item views blank expired content. alert-evaluator reads the aggregate views, not `hits` or `items` (`store-writer §4 L30` corrected); the alert types ADR-0048 adds also read `metrics_timeseries` (engagement spikes, ADR-0034) and `item_stories` (story alerts, ADR-0022).
- ADR-0010 adds one table to the contract, `public_accounts_dim` (`author_ref`, `platform`, kind, `source_id`, handle, display name, followers, verified flag), filled from `sources` and the public rows of `poster_profiles`, less the kinds a platform's terms forbid listing. An author is listed, ranked or exported only through it; no item row holds a public person's handle.

Why: One published list ends the name drift, one per-class purge list empties the same fields whoever runs it, and keeping candidates out of `hits` keeps client counts to matches on items.

## Consequences

F8 has one list; nine PRDs reword a column name, a field list or a reader line (the approved qualifier among them).

- CONVENTIONS v1.1: every analytics table and view with its owner (v1 L32), `hits`, `item_stories` (ADR-0022), `public_accounts_dim` (ADR-0010) and the aggregate tables and views included; where the column list lives (v1 L70); one purge list per class beside the retention classes (v1 L73 to L81).
- F8 publishes the column list and creates the tables and views; F4 holds the purge lists.
- `DEFERRED.md`: which service fills `public_accounts_dim` (F8 with C6; proposed: store-writer, which keeps `sources_dim` from the same `source.events`).

Sessions that must read this: F8, F4 (the per-class purge lists), C4, C5, C6, C8, C9, C13, C14, C15, A5, FB6, VIG2, X7, W3, W5, YT5, YT7.
