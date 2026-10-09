# Contract inventory

D1 · 7 Oct 2026 · Status: inventory of the drafts, nothing decided. Sources: the 86 service PRDs in `docs/prds/` (Draft v1, 6 Oct 2026), `docs/prds/_shared/CONVENTIONS.md` (Draft v1), the nine proposed decisions in `docs/prds/README.md` and `docs/prds/OPEN-QUESTIONS.md`. No ADR existed when this was written.

This file lists, for every PRD, each topic, job queue and job kind, table and column, budget tag, flag and retention class it reads or writes, with section and line references. It records what the PRDs say and decides nothing. Where they disagree, the disagreement is in `docs/contracts/CONFLICTS.md`; D2 decides those with the user and freezes the contracts in ADRs and CONVENTIONS v1.1. Until then a name in this file means "as written in that PRD", never "the contract".

## How it was built

- One extraction pass per PRD folder (`facebook`, `instagram`, `linkedin`, `news`, `shared`, `telegram`, `tiktok`, `web`, `x`, `youtube`) and one for `_shared` (CONVENTIONS, the README and OPEN-QUESTIONS). Each PRD was read in full, all 14 sections, because contracts also sit in 5.1 (rotation), 5.2 (steps), 7 (budgets), 8 (failure handling), 13 (acceptance criteria) and 14 (open questions). Every element was recorded with its section and line, names copied exactly, every example message field by field.
- The folder results were merged by a script and cross-checked in the D1 session: section 6 of all 86 PRDs was read again by hand, and every key format, topic writer, column writer and job kind behind a conflict was checked with `grep` against the PRD text.
- Limits. PRD examples are illustrative: a field missing from an example may still be intended, and a field present may be a placeholder. Where a PRD describes a column or a secret in words instead of naming it, the words are kept. Access is what the PRD says: a PRD that writes `sources.next_poll_at` "through registry-writer" is listed with that note, not as a direct writer.

## How to read it

- A reference `fb-page-feed-poller 6.2 L110-L126` means section 6.2, lines 110 to 126, of `docs/prds/facebook/fb-page-feed-poller.md` (every service name maps to one file; the appendix gives the folder and the build session). `13.4` is acceptance criterion 4, `14.2` open question 2, `header` the status line.
- Access: a topic is written or read (`write`, `read`) or only mentioned; a job queue is consumed or produced into; a table or column is read, written or both (`read_write`); a budget tag is used, defined or mentioned; a flag is read, defined or mentioned; a retention class is assigned, read, proposed or mentioned.
- "As written": names keep the PRD's spelling, case and placeholders. Two spellings of one thing appear as two rows on purpose: each such pair is a conflict, never a synonym.
- JSON types are the types of the example values (`string`, `integer`, `number`, `boolean`, `null`, `object`, `array`). A `null` example says nothing about the type.

## Known corrections from the review

A fresh verification pass checked 16 PRDs (every folder) against this inventory. Its systematic findings are fixed: services that schedule their own jobs are now shown as producers of their own queue, for the kinds their PRD gives to their own scheduler (kinds their PRD says another service emits, such as `backfill` from backfill-orchestrator, are not attributed to them), reader and writer lists are no longer cut, dead letters separate writers from mentions, and the raw batch path no longer names x-compliance-sync as its writer. These row-level corrections were found and are not yet applied to the tables below; read the rows with them in mind:

- `jobs.<service>`: comment-decay-scheduler also writes this spelling (comment-decay-scheduler 3 L21, 6.2 L138), next to `jobs.<comment service>`.
- `clients`: quota-governor (6.1 L94), registry-writer (6.1 L88, also `roles`) and x-user-resolver (5.2 L54) read the government marking.
- `deletion_requests`: retention-purger writes `status` (intake and status, 6.2 L94) and keeps the author hash (5.3 L78).
- `service_runs`: registry-writer keeps lag, unpublished-event count and pending manual requests (6.3 L102); yt-text-purger records its run start.
- `budgets`: tg-channel-resolver (6.3 L108) and tg-message-search (6.3 L96) keep counters through quota-governor as fb-reactions-fetcher and tt-hashtag-feed-poller do; fb-reactions-fetcher names no store for its usage headers (5.2 L53).
- Section 8, job partition key: tt-hashtag-feed-poller (5.2 L54) and comment-decay-scheduler (3 L21) also partition by `source_id`; the concept is split across several differently named rows.
- Section 7: retention-purger assigns `retention_class` on its `deletions` messages (6.2 L100); search-hit-router only mentions `news_excerpt` (7 L144), its messages carry no class.
- Small attributions: fb-reactions-fetcher's job has no field named `due_at` (5.1 L41); ig-webhook-receiver also writes mention items (9 L152); li-notification-receiver names no `jobs.` queue; yt-text-purger also reads `items.item_id` and `source_id` (5.3 L75); `stretch_factor` 1.0 is an example value, not a default.
- Companion file: the `alerts` row covers only some folders' alert names; news-robots-checker also spells `robots_status` (5.3 L71); quota-governor's decision values are written "allow, wait-until and deny" (3 L20).

Sections 9 (enumerations other services see) and 10 (internal calls between services) are in the companion file `docs/contracts/INVENTORY-VALUES-AND-CALLS.md`, to keep this file readable.

## Contents

- [1. Summary](#1-summary)
- [2. By topic](#2-by-topic)
- [3. By job queue](#3-by-job-queue)
- [4. By table](#4-by-table)
- [5. By budget tag](#5-by-budget-tag)
- [6. Flags and configuration](#6-flags-and-configuration)
- [7. Retention classes](#7-retention-classes)
- [8. Keys and identifiers](#8-keys-and-identifiers)
- [Appendix A. Per-service index](#appendix-a-per-service-index)

## 1. Summary

- PRDs read: 86 (plus CONVENTIONS, the README's nine proposals and OPEN-QUESTIONS).
- Topics named: 16: 13 of CONVENTIONS' 13, and 3 not in CONVENTIONS (`jobs.completed`, `news.dedup`, `raw.replay`).
- Job queues named: 75 (`jobs.*`, including priority lanes and wildcards as written), dead letters named: 85.
- Control-plane tables named: 54: 14 of CONVENTIONS' 14 and 40 others.
- ClickHouse tables named: 18: 7 of CONVENTIONS' 7 and 11 others (`aggregates_daily`, `aggregates_daily_v`, `aggregates_hourly_v`, `aggregates_monthly`, `aggregates_monthly_v`, `analytics store (stored comment ids and content hashes; table not named)`, `comments_v`, `hits`, `items_v`, `mv_aggregates_hourly`, `system.mutations`).
- Budget tags as written: 29; flags and settings: 270; retention classes: 8 (2 not in CONVENTIONS).

### 1.1 Topics at a glance

| Topic | In CONVENTIONS | Producers | Consumers |
|---|---|---|---|
| `raw.items` | yes | 48: fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-post-comments-fetcher, ig-account-media-poller, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-org-resolver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-article-extractor, news-comments-fetcher, poster-resolver, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-video-comments-fetcher, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-timeline-poller, yt-comments-fetcher, yt-keyword-search, yt-pubsub-receiver, yt-replies-fetcher, yt-uploads-reconciler, yt-video-details-fetcher | 5: fb-reactions-fetcher, news-dedup, normalize-item, raw-archiver, tt-hashtag-feed-poller |
| `items.normalized` | yes | 1: normalize-item | 8: analysis-entities, analysis-media, analysis-sentiment, analysis-topics, comment-decay-scheduler, keyword-matcher, store-writer, tg-channel-resolver |
| `item.hits` | yes | 2: keyword-matcher, tg-message-search | 4: alert-evaluator, analysis-media, analysis-sentiment, store-writer |
| `discovery.hits` | yes | 9: fb-page-search, ig-hashtag-search, keyword-matcher, search-hit-router, tg-bot-channel-receiver, tg-discussion-receiver, tg-message-search, web-commoncrawl-scanner, x-recent-search | 4: analysis-media, analysis-sentiment, poster-resolver, store-writer |
| `poster.profiles` | yes | 9: fb-page-resolver, ig-account-resolver, li-org-resolver, news-site-resolver, poster-resolver, tg-channel-resolver, tt-user-resolver, x-user-resolver, yt-channel-resolver | 2: qualifier, tg-channel-resolver |
| `registry.decisions` | yes | 3: qualifier, retention-purger, source-health-canary | 2: registry-writer, yt-text-purger |
| `source.events` | yes | 20: fb-backfill, fb-group-posts-poller, fb-page-feed-poller, ig-account-media-poller, ig-hashtag-search, ig-mentions-fetcher, ig-webhook-receiver, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, news-feed-poller, registry-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-discussion-receiver, tt-client-videos-fetcher, tt-profile-videos-poller, x-full-archive-search, x-user-timeline-poller, yt-uploads-reconciler | 46: aggregator, alert-evaluator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, backfill-orchestrator, comment-decay-scheduler, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, fb-post-comments-fetcher, ig-account-media-poller, ig-keyword-search, ig-mentions-fetcher, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, news-feed-poller, news-homepage-differ, news-robots-checker, news-sitemap-poller, normalize-item, quota-governor, raw-archiver, retention-purger, search-hit-router, source-health-canary, store-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-discussion-receiver, tt-client-videos-fetcher, tt-profile-videos-poller, web-commoncrawl-scanner, x-filtered-stream, x-recent-search, x-user-resolver, x-user-timeline-poller, yt-channel-resolver, yt-pubsub-receiver, yt-uploads-reconciler |
| `items.analysis` | yes | 4: analysis-entities, analysis-media, analysis-sentiment, analysis-topics | 1: store-writer |
| `item.metrics` | yes | 5: fb-reactions-fetcher, normalize-item, tt-client-videos-fetcher, tt-video-stats-refresher, yt-video-details-fetcher | 2: li-notification-receiver, store-writer |
| `deletions` | yes | 19: fb-client-webhook-receiver, fb-group-comments-fetcher, fb-post-comments-fetcher, fb-reactions-fetcher, ig-own-comments-fetcher, li-client-posts-poller, li-notification-receiver, li-own-comments-fetcher, li-post-comments-fetcher, news-comments-fetcher, retention-purger, tt-video-comments-fetcher, tt-video-stats-refresher, x-compliance-sync, yt-comments-fetcher, yt-pubsub-receiver, yt-replies-fetcher, yt-text-purger, yt-video-details-fetcher | 6: aggregator, alert-evaluator, comment-decay-scheduler, deletion-propagator, retention-purger, x-user-resolver |
| `article.urls` | yes | 4: news-feed-poller, news-homepage-differ, news-sitemap-poller, search-hit-router | 1: news-article-extractor |
| `search.results` | yes | 4: web-gdelt-poller, web-search-mojeek, web-search-perplexity, yt-web-search-bridge | 1: search-hit-router |
| `crawl.policies` | yes | 1: news-robots-checker | 5: news-article-extractor, news-feed-poller, news-homepage-differ, news-site-resolver, news-sitemap-poller |
| `jobs.completed` | **no** | 7: x-full-archive-search, x-replies-fetcher, x-user-timeline-poller, yt-comments-fetcher, yt-replies-fetcher, yt-uploads-reconciler, yt-video-details-fetcher | 4: backfill-orchestrator, comment-decay-scheduler, x-filtered-stream, x-full-archive-search |
| `news.dedup` | **no** | 1: news-dedup | 0:  |
| `raw.replay` | **no** | 1: raw-archiver | 0:  |

### 1.2 Job kinds at a glance

Each kind as written, the queues that consume it (by the consumer's own PRD) and the PRDs that emit it (into which queue). A kind consumed with no emitter, or emitted into a queue whose consumer does not list it, is a conflict (CONFLICTS.md, job kinds).

| Kind as written | Consumed on | Emitted by → into |
|---|---|---|
| `add` | jobs.fb-backfill |  |
| `analyze` | jobs.analysis-sentiment, jobs.analysis-sentiment.priority | analysis-sentiment → jobs.analysis-sentiment; analysis-sentiment → jobs.analysis-sentiment.priority |
| `backfill` | jobs.fb-group-posts-poller, jobs.fb-keyword-search, jobs.ig-account-media-poller, jobs.ig-keyword-search, jobs.ig-mentions-fetcher, jobs.li-client-posts-poller, jobs.li-company-posts-poller, jobs.li-post-search, jobs.news-sitemap-poller, jobs.tg-channel-posts-poller, jobs.tt-client-videos-fetcher, jobs.tt-profile-videos-poller, jobs.x-full-archive-search, jobs.yt-uploads-reconciler | backfill-orchestrator → jobs.<service>; backfill-orchestrator → jobs.fb-backfill |
| `candidate_retry` | jobs.keyword-matcher | keyword-matcher → jobs.keyword-matcher |
| `client` | jobs.fb-backfill |  |
| `comments` | jobs.fb-group-comments-fetcher, jobs.fb-post-comments-fetcher, jobs.ig-comments-fetcher, jobs.ig-own-comments-fetcher, jobs.li-own-comments-fetcher, jobs.li-post-comments-fetcher, jobs.news-comments-fetcher, jobs.tt-video-comments-fetcher, jobs.x-replies-fetcher, jobs.yt-comments-fetcher | comment-decay-scheduler → jobs.<comment service> |
| `first_check` | jobs.news-robots-checker | news-site-resolver → jobs.news-robots-checker (the kind is named only by the consumer, news-robots-checker 3 L19; news-site-resolver 5.1 L41 names the queue, not the kind) |
| `first_run` | jobs.x-recent-search |  |
| `first_sight` | jobs.yt-video-details-fetcher | yt-keyword-search → jobs.yt-video-details-fetcher; yt-pubsub-receiver → jobs.yt-video-details-fetcher; yt-uploads-reconciler → jobs.yt-video-details-fetcher; yt-web-search-bridge → jobs.yt-video-details-fetcher |
| `gap_backfill` | jobs.x-recent-search |  |
| `health` |  | comment-decay-scheduler → jobs.<comment service> |
| `keyword_history` | jobs.x-full-archive-search | x-recent-search → jobs.x-full-archive-search |
| `lang_rescore` | jobs.normalize-item | normalize-item → jobs.normalize-item |
| `manual_candidate` | jobs.poster-resolver | registry-writer → jobs.poster-resolver |
| `metrics` | jobs.ig-account-media-poller, jobs.tg-channel-posts-poller, jobs.tt-video-stats-refresher, jobs.yt-video-details-fetcher | comment-decay-scheduler → jobs.fb-reactions-fetcher; comment-decay-scheduler → jobs.ig-account-media-poller; comment-decay-scheduler → jobs.tt-video-stats-refresher; comment-decay-scheduler → jobs.yt-video-details-fetcher |
| `ops` | jobs.fb-backfill |  |
| `ops_force` | jobs.fb-group-comments-fetcher, jobs.fb-group-posts-poller, jobs.fb-keyword-search, jobs.fb-page-feed-poller, jobs.fb-page-resolver, jobs.fb-post-comments-fetcher, jobs.ig-account-media-poller, jobs.ig-comments-fetcher, jobs.ig-keyword-search, jobs.ig-mentions-fetcher, jobs.ig-own-comments-fetcher, jobs.li-client-posts-poller, jobs.li-company-posts-poller, jobs.news-comments-fetcher, jobs.news-feed-poller, jobs.news-homepage-differ, jobs.news-robots-checker, jobs.news-sitemap-poller, jobs.tg-bot-channel-receiver, jobs.tg-channel-posts-poller, jobs.tg-discussion-receiver, jobs.tt-client-videos-fetcher, jobs.tt-profile-videos-poller, jobs.tt-video-stats-refresher, jobs.web-commoncrawl-scanner, jobs.x-compliance-sync, jobs.x-recent-search, jobs.x-user-resolver, jobs.x-user-timeline-poller, jobs.yt-channel-resolver, jobs.yt-text-purger, jobs.yt-uploads-reconciler, jobs.yt-video-details-fetcher | ig-webhook-receiver → jobs.ig-mentions-fetcher; ig-webhook-receiver → jobs.ig-own-comments-fetcher |
| `push` | jobs.ig-webhook-receiver | ig-webhook-receiver → jobs.ig-webhook-receiver |
| `recheck` | jobs.news-robots-checker | news-article-extractor → jobs.news-robots-checker; news-feed-poller → jobs.news-robots-checker; news-homepage-differ → jobs.news-robots-checker; news-sitemap-poller → jobs.news-robots-checker |
| `recompute` | jobs.aggregator | deletion-propagator → jobs.aggregator |
| `reconciliation` | jobs.fb-page-feed-poller, jobs.ig-account-media-poller, jobs.ig-mentions-fetcher, jobs.ig-own-comments-fetcher, jobs.li-client-posts-poller, jobs.tg-bot-channel-receiver, jobs.tg-channel-posts-poller, jobs.tg-discussion-receiver, jobs.tt-profile-videos-poller, jobs.x-user-timeline-poller, jobs.yt-uploads-reconciler | fb-page-feed-poller → jobs.fb-page-feed-poller; ig-account-media-poller → jobs.ig-account-media-poller; ig-webhook-receiver → jobs.ig-mentions-fetcher; ig-webhook-receiver → jobs.ig-own-comments-fetcher; tg-bot-channel-receiver → jobs.tg-bot-channel-receiver; tg-channel-posts-poller → jobs.tg-channel-posts-poller; tg-discussion-receiver → jobs.tg-discussion-receiver; x-filtered-stream → jobs.x-recent-search; yt-uploads-reconciler → jobs.yt-uploads-reconciler |
| `refresh` | jobs.li-org-resolver, jobs.news-robots-checker, jobs.news-site-resolver, jobs.tg-channel-resolver | news-comments-fetcher → jobs.news-site-resolver; news-feed-poller → jobs.news-site-resolver; news-homepage-differ → jobs.news-site-resolver; news-sitemap-poller → jobs.news-site-resolver; tg-channel-resolver → jobs.tg-channel-resolver; yt-text-purger → jobs.yt-comments-fetcher; yt-text-purger → jobs.yt-replies-fetcher; yt-text-purger → jobs.yt-video-details-fetcher |
| `refresh_24h` | jobs.fb-reactions-fetcher |  |
| `refresh_7d` | jobs.fb-reactions-fetcher |  |
| `refresh_client` | jobs.fb-reactions-fetcher |  |
| `rematch` | jobs.keyword-matcher |  |
| `replay` | jobs.normalize-item |  |
| `replies` | jobs.fb-group-comments-fetcher, jobs.ig-own-comments-fetcher, jobs.tt-video-comments-fetcher, jobs.x-full-archive-search, jobs.yt-replies-fetcher | comment-decay-scheduler → jobs.<comment service> |
| `rerun` | jobs.analysis-entities, jobs.analysis-media, jobs.analysis-sentiment, jobs.analysis-topics |  |
| `resolve` | jobs.fb-page-resolver, jobs.ig-account-resolver, jobs.news-site-resolver, jobs.tt-user-resolver, jobs.x-user-resolver, jobs.yt-channel-resolver | poster-resolver → jobs.<resolver>; poster-resolver → jobs.ig-account-resolver; yt-web-search-bridge → jobs.yt-channel-resolver |
| `resolved` | jobs.poster-resolver |  |
| `retention_sweep` | jobs.yt-text-purger | retention-purger → jobs.yt-text-purger |
| `rotation` | jobs.fb-group-posts-poller, jobs.fb-keyword-search, jobs.fb-page-feed-poller, jobs.fb-page-resolver, jobs.ig-account-media-poller, jobs.ig-account-resolver, jobs.ig-keyword-search, jobs.ig-mentions-fetcher, jobs.li-client-posts-poller, jobs.li-company-posts-poller, jobs.news-feed-poller, jobs.news-homepage-differ, jobs.news-sitemap-poller, jobs.tg-channel-posts-poller, jobs.tt-client-videos-fetcher, jobs.tt-profile-videos-poller, jobs.web-commoncrawl-scanner, jobs.web-gdelt-poller, jobs.web-search-mojeek, jobs.web-search-perplexity, jobs.x-recent-search, jobs.x-user-resolver, jobs.x-user-timeline-poller, jobs.yt-channel-resolver | fb-group-posts-poller → jobs.fb-group-posts-poller; fb-keyword-search → jobs.fb-keyword-search; fb-page-feed-poller → jobs.fb-page-feed-poller; fb-page-resolver → jobs.fb-page-resolver; ig-account-media-poller → jobs.ig-account-media-poller; ig-account-resolver → jobs.ig-account-resolver; ig-keyword-search → jobs.ig-keyword-search; ig-mentions-fetcher → jobs.ig-mentions-fetcher; tg-channel-posts-poller → jobs.tg-channel-posts-poller; yt-channel-resolver → jobs.yt-channel-resolver |
| `seed` | jobs.fb-page-search |  |
| `site_search` | jobs.web-search-perplexity |  |
| `unresolvable` | jobs.poster-resolver |  |
| `weekly` | jobs.fb-page-search | fb-page-search → jobs.fb-page-search |

### 1.3 Tables at a glance

| Store | Table | In CONVENTIONS | PRDs naming it | Writers |
|---|---|---|---|---|
| postgres | `budgets` | yes | 55 | fb-backfill, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-search, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, li-client-posts-poller, li-company-posts-poller, quota-governor, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-gdelt-poller, web-search-mojeek, web-search-perplexity, yt-keyword-search, yt-uploads-reconciler, yt-web-search-bridge |
| postgres | `canary_targets` | yes | 15 | source-health-canary |
| postgres | `client_sources` | yes | 19 | registry-writer |
| postgres | `clients` | yes | 57 |  |
| postgres | `crawl_policies` | yes | 7 | news-article-extractor, news-feed-poller, news-homepage-differ, news-robots-checker, news-sitemap-poller |
| postgres | `cursors` | yes | 64 | aggregator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-search, fb-post-comments-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-feed-poller, news-homepage-differ, news-sitemap-poller, normalize-item, raw-archiver, retention-purger, store-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-timeline-poller, yt-comments-fetcher, yt-keyword-search, yt-pubsub-receiver, yt-replies-fetcher, yt-text-purger, yt-uploads-reconciler, yt-web-search-bridge |
| postgres | `decisions` | yes | 9 | fb-page-search, news-dedup, poster-resolver, qualifier |
| postgres | `deletion_requests` | yes | 6 | deletion-propagator, retention-purger |
| postgres | `keywords` | yes | 19 |  |
| postgres | `retention_classes` | yes | 11 |  |
| postgres | `review_queue` | yes | 21 | analysis-entities, analysis-media, analysis-sentiment, analysis-topics, ig-account-media-poller, ig-account-resolver, news-site-resolver, normalize-item, qualifier, search-hit-router, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-recent-search, yt-comments-fetcher, yt-keyword-search, yt-replies-fetcher, yt-web-search-bridge |
| postgres | `service_runs` | yes | 85 | aggregator, alert-evaluator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, backfill-orchestrator, comment-decay-scheduler, deletion-propagator, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, fb-page-search, fb-post-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, lang-dialect-id, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-org-resolver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-article-extractor, news-comments-fetcher, news-dedup, news-feed-poller, news-homepage-differ, news-robots-checker, news-site-resolver, news-sitemap-poller, normalize-item, poster-resolver, qualifier, raw-archiver, registry-writer, retention-purger, search-hit-router, source-health-canary, store-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-commoncrawl-scanner, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-compliance-sync, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-resolver, x-user-timeline-poller, yt-channel-resolver, yt-comments-fetcher, yt-keyword-search, yt-pubsub-receiver, yt-replies-fetcher, yt-text-purger, yt-uploads-reconciler, yt-video-details-fetcher, yt-web-search-bridge |
| postgres | `sources` | yes | 80 | backfill-orchestrator, fb-backfill, fb-client-webhook-receiver, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, ig-account-media-poller, ig-hashtag-search, ig-mentions-fetcher, ig-webhook-receiver, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-own-comments-fetcher, li-post-search, news-feed-poller, news-homepage-differ, news-sitemap-poller, registry-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-full-archive-search, x-recent-search, x-user-timeline-poller, yt-uploads-reconciler |
| postgres | `vendor_keys` | yes | 26 | retention-purger, tt-keyword-search |
| postgres | `alert_deliveries` | **no** | 1 | alert-evaluator |
| postgres | `alert_rules` | **no** | 1 | alert-evaluator |
| postgres | `alert_watch_items` | **no** | 1 | alert-evaluator |
| postgres | `alerts` | **no** | 1 | alert-evaluator |
| postgres | `backfill_runs` | **no** | 1 | backfill-orchestrator |
| postgres | `brand_assets` | **no** | 1 |  |
| postgres | `budget_history` | **no** | 1 | quota-governor |
| postgres | `budget_reservations` | **no** | 1 | quota-governor |
| postgres | `cc_hosts_seen` | **no** | 1 | web-commoncrawl-scanner |
| postgres | `comment index (yt-comments-fetcher's)` | **no** | 2 | yt-comments-fetcher |
| postgres | `comment_ledger` | **no** | 2 | fb-group-comments-fetcher, fb-post-comments-fetcher |
| postgres | `comment_series` | **no** | 3 | comment-decay-scheduler |
| postgres | `ig_hashtag_ledger` | **no** | 1 | quota-governor |
| postgres | `kb_aliases` | **no** | 1 |  |
| postgres | `kb_entities` | **no** | 1 |  |
| postgres | `model_versions` | **no** | 4 | analysis-sentiment |
| postgres | `news_sites` | **no** | 7 | news-site-resolver |
| postgres | `news_stories` | **no** | 1 | news-dedup |
| postgres | `news_story_members` | **no** | 1 | news-dedup |
| postgres | `news_urls` | **no** | 5 | news-article-extractor |
| postgres | `onboarding records` | **no** | 1 |  |
| postgres | `poster_profiles` | **no** | 2 | poster-resolver |
| postgres | `profile_cache` | **no** | 4 | fb-page-resolver, ig-account-resolver, x-user-resolver, yt-channel-resolver |
| postgres | `registry` | **no** | 1 |  |
| postgres | `registry_audit` | **no** | 1 | registry-writer |
| postgres | `reply index (x-replies-fetcher's)` | **no** | 1 | x-replies-fetcher |
| postgres | `reply index (yt-replies-fetcher's)` | **no** | 1 | yt-replies-fetcher |
| postgres | `retention_audit` | **no** | 2 | retention-purger, yt-text-purger |
| postgres | `search_candidate_seen` | **no** | 1 | search-hit-router |
| postgres | `search_parked_urls` | **no** | 1 | search-hit-router |
| postgres | `search_url_seen` | **no** | 1 | search-hit-router |
| postgres | `taxonomy_nodes` | **no** | 1 | analysis-topics |
| postgres | `tt_client_video_state` | **no** | 1 | tt-client-videos-fetcher |
| postgres | `tt_comment_state` | **no** | 1 | tt-video-comments-fetcher |
| postgres | `tt_user_cache` | **no** | 1 | tt-user-resolver |
| postgres | `x_compliance_audit` | **no** | 1 | x-compliance-sync |
| postgres | `x_compliance_runs` | **no** | 1 | x-compliance-sync |
| postgres | `x_read_ledger` | **no** | 1 | quota-governor |
| postgres | `yt_live_watch` | **no** | 1 | yt-video-details-fetcher |
| postgres | `yt_subscriptions` | **no** | 1 | yt-pubsub-receiver |
| clickhouse | `aggregates_hourly` | yes | 7 | aggregator |
| clickhouse | `analysis` | yes | 10 | deletion-propagator, store-writer |
| clickhouse | `comments` | yes | 17 | deletion-propagator, store-writer |
| clickhouse | `items` | yes | 15 | deletion-propagator, store-writer |
| clickhouse | `keywords_dim` | yes | 3 | store-writer |
| clickhouse | `metrics_timeseries` | yes | 7 | deletion-propagator, store-writer |
| clickhouse | `sources_dim` | yes | 3 | store-writer |
| clickhouse | `aggregates_daily` | **no** | 2 | aggregator |
| clickhouse | `aggregates_daily_v` | **no** | 1 |  |
| clickhouse | `aggregates_hourly_v` | **no** | 2 |  |
| clickhouse | `aggregates_monthly` | **no** | 1 | aggregator |
| clickhouse | `aggregates_monthly_v` | **no** | 1 |  |
| clickhouse | `analytics store (stored comment ids and content hashes; table not named)` | **no** | 1 |  |
| clickhouse | `comments_v` | **no** | 1 | store-writer |
| clickhouse | `hits` | **no** | 3 | store-writer |
| clickhouse | `items_v` | **no** | 1 | store-writer |
| clickhouse | `mv_aggregates_hourly` | **no** | 1 | aggregator |
| clickhouse | `system.mutations` | **no** | 1 |  |

## 2. By topic

Every Redpanda topic a PRD names, CONVENTIONS' thirteen first in CONVENTIONS order, then the topics PRDs add. Job queues (`jobs.<service>`) and dead letters are in section 3.

### 2.1 `raw.items`

- In CONVENTIONS: yes
- Partition or message key as stated: `the hashtag source_id` (ig-hashtag-search); `source_id` (news-dedup); `source_id; records without source_id keyed by the producer on <platform>:<poster platform_id>` (normalize-item); `message key: <platform>:<poster platform_id> when source_id is absent` (normalize-item); `the hashtag's source_id` (tt-hashtag-feed-poller); `the keyword rule's source_id` (tt-keyword-search, yt-keyword-search); `web:<source_id>` (web-gdelt-poller, web-search-mojeek, web-search-perplexity)
- Producers: 48; consumers: 5; mention only: 5

| Producer | Kinds or event types written | Refs |
|---|---|---|
| fb-backfill | post | 2 L13; 4 L35; 5.1 L47; 6.2 L88-L107; +3 more |
| fb-client-webhook-receiver | post, comment | 3 L21; 4 L34; 5.2 L56; 5.2 L58; +4 more |
| fb-group-comments-fetcher | comment | 2 L13; 5.2 L62; 5.2 L64; 5.4 L82-L94; +2 more |
| fb-group-posts-poller | post | 3 L21; 5.2 L60; 5.4 L78-L90; 6.2 L102-L124; +3 more |
| fb-keyword-search | post | 2 L13; 3 L22; 5.2 L56; 5.4 L73-L85; +4 more |
| fb-page-feed-poller | post | 3 L22; 4 L34; 5.2 L58; 5.3 L64-L76; +5 more |
| fb-post-comments-fetcher | comment | 3 L21; 4 L36; 5.2 L66; 5.2 L68; +5 more |
| ig-account-media-poller | post | 3 L22; 5.1 L50; 5.1 L52; 5.2 L62; +7 more |
| ig-comments-fetcher | comment | 2 L13; 3 L22; 5.2 L61; 5.2 L62; +7 more |
| ig-hashtag-search | post | 2 L13; 3 L24; 4 L37; 5.2 L68; +4 more |
| ig-keyword-search | post | 2 L13; 3 L22; 5.1 L51; 5.2 L62; +6 more |
| ig-mentions-fetcher | post, comment | 2 L13; 3 L22; 5.1 L49; 5.2 L59; +7 more |
| ig-own-comments-fetcher | comment | 2 L13; 3 L21; 3 L22; 5.1 L49; +9 more |
| ig-webhook-receiver | comment | 2 L13; 3 L20; 4 L33; 5.1 L49; +6 more |
| li-client-posts-poller | post | 6.2 L103-L124; 3 L21; 5.2 L59-L60; 5.3 L77; +5 more |
| li-company-posts-poller | post | 6.2 L100-L121; 3 L20; 5.2 L60; 5.4 L77-L92; +3 more |
| li-notification-receiver | comment, reaction | 6.2 L110-L133; 3 L21; 5.2 L56; 5.2 L58; +6 more |
| li-org-resolver | (not stated) | 5.2 L57; 6.2 L79; 7 L115; 13.10 L159 |
| li-own-comments-fetcher | comment | 6.2 L103-L124; 3 L20; 5.2 L62-L63; 5.4 L79-L95; +3 more |
| li-post-comments-fetcher | comment | 6.2 L105-L129; 3 L20; 5.2 L63-L65; 5.4 L82-L97; +4 more |
| li-post-search | post | 6.2 L81-L105; 2 L15; 3 L25; 5.2 L60; +4 more |
| news-article-extractor | article | 6.2 L89-L123; 5.2 L58; 2 L13; 3 L22; +1 more |
| news-comments-fetcher | comment | 6.2 L90-L118; 3 L21; 5.2 L57-L59; 2 L13 |
| poster-resolver | profile | 3 L26; 5.2 L58; 5.2 L59; 6.2 L92; +1 more |
| tg-bot-channel-receiver | post | 2 L15; 3 L23; 5.2 L59-L62; 6.2 L113-L132; +7 more |
| tg-channel-posts-poller | post | 2 L13; 3 L22; 5.2 L65; 5.2 L66; +7 more |
| tg-channel-resolver | profile | 5.2 L57; 6.2 L77; 13.7 L156 |
| tg-discussion-receiver | comment | 2 L15; 3 L22; 5.2 L59-L65; 6.2 L114-L136; +8 more |
| tg-message-search | (not stated) | 2 L15; 3 L22; 5.2 L54; 5.2 L55; +5 more |
| tt-client-videos-fetcher | post | 3 L19; 5.2 L59; 5.4 L71-L82; 6.2 L94-L113; +4 more |
| tt-hashtag-feed-poller | video | 1 L7; 3 L22; 5.2 L59; 6.2 L79-L106; +3 more |
| tt-keyword-search | video | 1 L7; 2 L13; 3 L22; 5.2 L52; +4 more |
| tt-profile-videos-poller | post | 3 L21; 5.2 L61; 5.4 L81-L95; 6.2 L105-L124; +3 more |
| tt-video-comments-fetcher | comment | 2 L13; 3 L21; 5.2 L60; 5.2 L61; +6 more |
| web-gdelt-poller | search_response | 5.2 L57; 6.2 L91; 3 L25; 3 L29; +2 more |
| web-search-mojeek | search_response | 5.2 L57; 6.2 L88; 3 L25; 4 L36; +1 more |
| web-search-perplexity | search_response | 5.2 L55; 6.2 L89; 3 L24; 4 L35; +2 more |
| x-filtered-stream | post | 2 L13; 3 L21; 5.2 L61-L63; 5.4 L88-L101; +4 more |
| x-full-archive-search | post | 5.1 L45; 5.2 L54; 6.2 L106-L128; 13.2 L176; +2 more |
| x-recent-search | post | 2 L13; 3 L22; 5.2 L57-L58; 6.2 L98-L131; +2 more |
| x-replies-fetcher | comment | 2 L13; 5.2 L59-L60; 6.2 L106-L134; 9 L162; +1 more |
| x-user-timeline-poller | post | 2 L13; 3 L21; 5.2 L59; 6.2 L112-L132; +2 more |
| yt-comments-fetcher | comment | 2 L13; 5.2 L57; 6.2 L110-L134; 9 L165-L166; +2 more |
| yt-keyword-search | video | 2 L15; 2 L17; 3 L25; 5.2 L59; +3 more |
| yt-pubsub-receiver | post | 2 L13; 3 L21; 5.2 L55; 6.2 L102-L124; +2 more |
| yt-replies-fetcher | comment | 2 L13; 5.2 L54; 6.2 L99-L123; 9 L154; +2 more |
| yt-uploads-reconciler | post | 2 L15; 3 L24; 5.2 L63; 6.2 L108-L128; +2 more |
| yt-video-details-fetcher | post | 2 L13; 3 L19; 5.2 L61; 6.2 L90-L129; +2 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| fb-reactions-fetcher | post | 3 L19; 5.1 L39; 5.2 L51; 6.1 L98; +1 more |
| news-dedup | article | 3 L19; 5.1 L41; 5.1 L43; 5.2 L51; +1 more |
| normalize-item | eleven payload families (5.3 mapper table) | 5.1 L41; 5.1 L45; 5.2 L49; 5.3 L60-L73; +1 more |
| raw-archiver | post (example), every raw record | 2 L13; 3 L19; 5.1 L44; 5.2 L50-L52; +2 more |
| tt-hashtag-feed-poller | video | 5.2 L57; 6.1 L75 |

Mentioned without reading or writing: deletion-propagator, fb-page-search, source-health-canary, tt-user-resolver, web-commoncrawl-scanner.

Common written fields (each path found in at least half of the 48 producer examples, with its usual JSON type):

`envelope`: object, `envelope.attempt`: integer, `envelope.batch`: string, `envelope.client_ids`: array, `envelope.client_ids[]`: string, `envelope.fetched_at`: string, `envelope.idempotency_key`: string, `envelope.job_id`: string, `envelope.kind`: string, `envelope.platform`: string, `envelope.platform_id`: string, `envelope.retention_class`: string, `envelope.route`: string, `envelope.service`: string, `envelope.source_id`: string, `envelope.vendor`: string, `payload`: object

Fields per PRD, exactly as written. For a producer, `common` stands for the set above, `+` lists the fields it adds, `−` the common fields its example lacks, and `type` a common field it gives another JSON type (null counts as compatible). A producer whose example has no `envelope` wrapper is marked **flat** and listed in full. Payload fields are the platform's or vendor's native record and are named by their top-level key only. 

| PRD | Access | Fields |
|---|---|---|
| fb-backfill | write | common; + `envelope.metrics_observation`: string, `envelope.window`: object, `envelope.window.start`: string, `envelope.window.end`: string |
| fb-client-webhook-receiver | write | common; + `envelope.parent_platform_id`: string, `envelope.delivery`: string, `envelope.version`: integer, `envelope.author_ref`: string, `envelope.payload_redacted`: array, `envelope.payload_redacted[]`: string |
| fb-group-comments-fetcher | write | common; + `envelope.parent_platform_id`: string, `envelope.post_platform_id`: , `envelope.series_step`: string, `envelope.version`: integer, `envelope.text_hash`: string, `envelope.author_ref`: string, `envelope.payload_redacted`: array, `envelope.payload_redacted[]`: string |
| fb-group-posts-poller | write | common; + `envelope.author_ref`: string, `envelope.metrics_observation`: string |
| fb-keyword-search | write | common; + `envelope.query`: object, `envelope.query.variant`: string, `envelope.query.rank`: integer, `envelope.author_ref`: string, `envelope.metrics_observation`: string |
| fb-page-feed-poller | write | common; + `envelope.metrics_observation`: string |
| fb-post-comments-fetcher | write | common; + `envelope.parent_platform_id`: string, `envelope.series_step`: string, `envelope.edit_of`: null, `envelope.author_ref`: null, `envelope.payload_redacted`:  |
| fb-reactions-fetcher | read | `envelope.platform`: ; `envelope.kind`: ; `envelope.route`: ; `envelope.fetched_at`: ; `envelope.metrics_observation`:  |
| ig-account-media-poller | write | common; + `envelope.metrics_observation`: string |
| ig-comments-fetcher | write | common; + `envelope.post_ref`: string, `envelope.parent_id`: null, `envelope.series_step`: string, `envelope.content_hash`: string |
| ig-hashtag-search | write | **flat**: `idempotency_key`: string; `platform`: string; `kind`: string; `route`: string; `vendor`: null; `service`: string; `job_id`: string; `source_id`: string; `client_ids`: array; `client_ids[]`: string; `fetched_at`: string; `retention_class`: string; `edge`: string; `payload`: object |
| ig-keyword-search | write | common; + `envelope.metrics_observation`: string |
| ig-mentions-fetcher | write | common; + `envelope.mention_type`: string, `envelope.mention_of`: string, `envelope.metrics_observation`: string |
| ig-own-comments-fetcher | write | common; + `envelope.post_ref`: string, `envelope.parent_id`: null, `envelope.series_step`: string, `envelope.content_hash`: string |
| ig-webhook-receiver | write | common; + `envelope.received_at`: string, `envelope.post_ref`: string, `envelope.parent_id`: null, `envelope.delivery`: string, `envelope.content_hash`: string |
| li-client-posts-poller | write | common; + `envelope.metrics_observation`: string |
| li-company-posts-poller | write | common; + `envelope.metrics_observation`: string |
| li-notification-receiver | write | common; + `envelope.post_ref`: string, `identity`: string |
| li-org-resolver | write | **flat**: `service`: string; `retention_class`: string |
| li-own-comments-fetcher | write | common; + `envelope.post_ref`: string, `envelope.series_step`: string, `content hash (field name and position not stated)`:  |
| li-post-comments-fetcher | write | common; + `envelope.post_ref`: string, `envelope.series_step`: string, `envelope.identity`: string, `content hash (field name and position not stated)`:  |
| li-post-search | write | common; + `envelope.cost_units`: integer; − `envelope.batch`, `envelope.client_ids`, `envelope.client_ids[]`, `envelope.platform_id`, `envelope.source_id` |
| news-article-extractor | write | common; + `envelope.url_key`: string, `envelope.access_mode`: string, `envelope.usage_signals`: object, `envelope.usage_signals.search`: string, `envelope.usage_signals.ai_input`: string, `envelope.usage_signals.ai_train`: string; − `envelope.job_id` |
| news-comments-fetcher | write | common; + `envelope.parent_id`: string, `envelope.series_step`: string; − `envelope.batch` |
| news-dedup | read | `canonical_url`: ; `title_sha256`: ; `text_sha256`: ; `excerpt`: ; `published_at`: ; `language`: ; `envelope.source_id`: ; `envelope.idempotency_key`: ; `envelope.fetched_at`:  |
| normalize-item | read | `service`: string; `route`: string; `vendor`: string; `platform`: string; `source_id`: string; `job_id`: string; `job_kind`: string; `fetched_at`: string; `api_version`: string; `raw_ref`: string |
| poster-resolver | write | **flat**: `kind`: string; `individual`: boolean; `author_hash (hash)`: ; `platform`:  |
| raw-archiver | read | `envelope`: object; `envelope.platform`: ; `envelope.kind`: ; `envelope.route`: ; `envelope.vendor`: ; `envelope.service`: ; `envelope.source_id`: ; `envelope.platform_id`: ; `envelope.idempotency_key`: ; `envelope.job_id`: ; `envelope.fetched_at`: ; `envelope.retention_class`: ; `envelope.client_ids`: ; `envelope.raw_ref`: string; `envelope.batch`: ; `payload`: object |
| tg-bot-channel-receiver | write | common; + `envelope.event`: string, `envelope.ingest_mode`: string, `envelope.update_id`: integer, `envelope.owned_by_client`: boolean, `edit_date`: ; − `envelope.job_id` |
| tg-channel-posts-poller | write | common; + `envelope.metrics_observation`: string |
| tg-channel-resolver | write | **flat**: `kind`: string |
| tg-discussion-receiver | write | common; + `envelope.event`: string, `envelope.ingest_mode`: string, `envelope.discussion_source_id`: string, `envelope.post_ref`: string, `envelope.unthreaded`: boolean, `envelope.author_ref`: string, `envelope.minimized`: boolean, `envelope.update_id`: integer, `envelope.owned_by_client`: boolean, `edit_date`: ; − `envelope.job_id` |
| tg-message-search | write | **flat**: `route`: string; `vendor`: string; `service`: string; `fetched_at`: ; `idempotency_key`: string; `payload`:  |
| tt-client-videos-fetcher | write | common; + `envelope.metrics_observation`: string |
| tt-hashtag-feed-poller | write | **flat**: `idempotency_key`: string; `platform`: string; `kind`: string; `platform_id`: string; `source_id`: string; `source_type`: string; `route`: string; `vendor`: string; `service`: string; `job_id`: string; `attempt`: integer; `fetched_at`: string; `retention_class`: string; `context`: object; `context.hashtag_id`: string; `context.hashtag_name`: string; `context.page`: integer; `context.backfill`: boolean; `raw`: object |
| tt-keyword-search | write | **flat**: `idempotency_key`: string; `platform`: string; `kind`: string; `platform_id`: string; `source_id`: string; `source_type`: string; `route`: string; `vendor`: string; `service`: string; `job_id`: string; `attempt`: integer; `fetched_at`: string; `retention_class`: string; `context`: object; `context.keyword_id`: string; `context.variant`: string; `context.country`: string; `context.page`: integer; `raw`: object |
| tt-profile-videos-poller | write | common; + `envelope.metrics_observation`: string |
| tt-video-comments-fetcher | write | common; + `envelope.post_ref`: string, `envelope.parent_id`: null, `envelope.series_step`: string, `envelope.version`: integer |
| web-gdelt-poller | write | common; + `envelope.job_kind`: , `envelope.kind_hint`: string, `envelope.raw_ref`: , `normalize`: string; − `envelope`, `envelope.attempt`, `envelope.batch`, `envelope.client_ids`, `envelope.client_ids[]`, `envelope.idempotency_key`, `envelope.kind`, `envelope.platform_id`, `envelope.retention_class` |
| web-search-mojeek | write | common; + `envelope.job_kind`: , `envelope.kind_hint`: string, `envelope.api_version`: , `envelope.raw_ref`: , `normalize`: string; − `envelope`, `envelope.attempt`, `envelope.batch`, `envelope.client_ids`, `envelope.client_ids[]`, `envelope.idempotency_key`, `envelope.kind`, `envelope.platform_id`, `envelope.retention_class` |
| web-search-perplexity | write | common; + `envelope.job_kind`: , `envelope.kind_hint`: string, `envelope.api_version`: , `envelope.raw_ref`: , `normalize`: string; − `envelope`, `envelope.attempt`, `envelope.batch`, `envelope.client_ids`, `envelope.client_ids[]`, `envelope.idempotency_key`, `envelope.kind`, `envelope.platform_id`, `envelope.retention_class` |
| x-filtered-stream | write | common; + `envelope.connection_id`: string, `envelope.paid`: boolean, `envelope.matching_rules`: array, `envelope.matching_rules[].id`: string, `envelope.matching_rules[].tag`: string, `envelope.metrics_observation`: string |
| x-full-archive-search | write | common; + `envelope.job_kind`: string, `envelope.paid`: boolean, `envelope.metrics_observation`: string, `envelope.post_ref`:  |
| x-recent-search | write | **flat**: `idempotency_key`: string; `platform`: string; `kind`: string; `platform_id`: string; `source_id`: string; `source_type`: string; `route`: string; `vendor`: null; `service`: string; `job_id`: string; `attempt`: integer; `fetched_at`: string; `retention_class`: string; `client_ids`: array; `client_ids[]`: string; `budget_tag`: string; `cost_units`: integer; `paid`: boolean; `context`: object; `context.query_arm`: string; `context.matched_terms`: array; `context.matched_terms[]`: string; `context.discovery_hit_emitted`: boolean; `raw`: object; `includes`: object |
| x-replies-fetcher | write | common; + `envelope.ledger_key`: string, `envelope.paid`: boolean, `envelope.parent_post_id`: string, `envelope.conversation_id`: string, `envelope.parent_comment_id`: null, `envelope.author_ref`: string, `envelope.author_source_id`: null, `envelope.author_is_source`: boolean, `envelope.in_reply_to_ref`: string, `envelope.content_hash`: string, `envelope.observation`: string, `envelope.series_step`: string, `envelope.removed_fields`: array, `envelope.removed_fields[]`: string |
| x-user-timeline-poller | write | common; + `envelope.paid`: boolean, `envelope.metrics_observation`: string |
| yt-comments-fetcher | write | common; + `envelope.parent_video_id`: string, `envelope.parent_comment_id`: null, `envelope.video_channel_id`: string, `envelope.author_ref`: string, `envelope.author_is_source`: boolean, `envelope.content_hash`: string, `envelope.observation`: string, `envelope.series_step`: string, `envelope.removed_fields`: array, `envelope.removed_fields[]`: string |
| yt-keyword-search | write | **flat**: `idempotency_key`: string; `platform`: string; `kind`: string; `platform_id`: string; `channel_id`: string; `source_id`: string; `source_type`: string; `route`: string; `vendor`: null; `service`: string; `origin`: string; `job_id`: string; `attempt`: integer; `fetched_at`: string; `retention_class`: string; `cost_units`: integer; `partial`: boolean; `payload`: object |
| yt-pubsub-receiver | write | common; + `envelope.parent_platform_id`: null, `envelope.delivery`: string, `envelope.version`: integer, `envelope.partial`: boolean |
| yt-replies-fetcher | write | common; + `envelope.parent_video_id`: string, `envelope.parent_comment_id`: string, `envelope.video_channel_id`: string, `envelope.author_ref`: string, `envelope.author_is_source`: boolean, `envelope.content_hash`: string, `envelope.observation`: string, `envelope.series_step`: string, `envelope.removed_fields`: array, `envelope.removed_fields[]`: string |
| yt-uploads-reconciler | write | common; + `envelope.partial`: boolean, `envelope.metrics_observation`: null |
| yt-video-details-fetcher | write | common; + `envelope.partial`: boolean, `envelope.completes_partial_from`: string, `envelope.metrics_observation`: string, `envelope.live_state`: string, `envelope.call_id`: string; − `envelope.attempt`, `envelope.batch`, `envelope.client_ids`, `envelope.client_ids[]` |

### 2.2 `items.normalized`

- In CONVENTIONS: yes
- Partition or message key as stated: `normalize-item's keys: source_id, or the poster key for search results` (keyword-matcher); `source_id or poster key` (normalize-item); `message key: source_id or poster key <platform>:<poster platform_id>` (normalize-item); `source_id (or the poster key)` (store-writer)
- Schema names: `items.normalized/v1` (lang-dialect-id, normalize-item, store-writer)
- Producers: 1; consumers: 8; mention only: 26

| Producer | Kinds or event types written | Refs |
|---|---|---|
| normalize-item | post, reply, quote, comment (implied by keys) | 2 L15; 5.2 L56; 6.2 L91; 6.2 L93-L120; +1 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| analysis-entities | (all) | 2 L13; 5.1 L40; 5.1 L42; 5.2 L50-L52; +2 more |
| analysis-media | (all) | 2 L13; 5.1 L41; 5.4 L78; 6.1 L83; +1 more |
| analysis-sentiment | post, comment, article, web result | 2 L15; 5.1 L45; 5.2 L55-L57; 5.4 L80; +1 more |
| analysis-topics | (all) | 2 L15; 5.1 L44; 5.1 L46; 5.2 L54-L55; +2 more |
| comment-decay-scheduler | post (version = 1) | 3 L20; 5.1 L42; 5.1 L60; 5.1 L66; +2 more |
| keyword-matcher | post, video, article, message, result, comment, reply | 5.1 L40; 5.2 L46-L52; 5.4 L85; 6.1 L90 |
| store-writer | post, video, article, message, quote, result, comment, reply | 1 L7; 3 L22; 5.1 L39; 5.2 L46-L48; +2 more |
| tg-channel-resolver | (all) | 3 L21; 5.2 L58; 6.1 L73; 11 L139 |

Mentioned without reading or writing: fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-page-feed-poller, fb-post-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller, ig-comments-fetcher, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, lang-dialect-id, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-post-search, news-article-extractor, poster-resolver, tt-profile-videos-poller, tt-video-stats-refresher, x-replies-fetcher, x-user-timeline-poller, yt-comments-fetcher, yt-pubsub-receiver, yt-uploads-reconciler.

Fields per PRD, exactly as written (`path`: JSON type of the example).

| PRD | Access | Fields |
|---|---|---|
| analysis-entities | read | `title`: ; `text`: ; `text_norm`: ; `lang`: ; `dialect`: ; `script`: ; `kind`: ; `retention_class`: ; `content_hash`: ; `source_id`: ; `author.author_source_id`: ; `fetched_at`:  |
| analysis-media | read | `media[]`: ; `media[].url`: ; `media[].type`: ; `platform`: ; `kind`: ; `route`: ; `retention_class`: ; `source_id`: ; `fetched_at`:  |
| analysis-sentiment | read | `title`: ; `text`: ; `lang`: ; `dialect`: ; `script`: ; `kind`: ; `retention_class`: ; `content_hash`: ; `source_id`: ; `author.author_source_id`: ; `fetched_at`:  |
| analysis-topics | read | `title`: ; `text`: ; `lang`: ; `dialect`: ; `script`: ; `kind`: ; `retention_class`: ; `content_hash`: ; `source_id`: ; `author.author_source_id`: ; `fetched_at`:  |
| comment-decay-scheduler | read | `kind`: ; `version`: ; `item_id`: ; `source_id`: ; `platform`: ; `route`: ; `vendor`: ; `fetched_at`: ; `job_kind`:  |
| keyword-matcher | read | `item_id`: ; `kind`: ; `source_id`: ; `author.author_type`: ; `author.author_source_id`: ; `author.author_ref`: ; `text_norm`: ; `lang_model_version`: ; `version`: ; `route`: ; `platform`: ; `retention_class`: ; `raw_ref`: ; `created_at`:  |
| lang-dialect-id | mention | `lang`: string; `lang_conf`: number; `script`: string; `dialect`: string; `dialect_conf`: number; `text_norm`: string; `lang_model_version`: string; `lang_pending`: boolean |
| normalize-item | write | `schema`: string; `message_id`: string; `produced_at`: string; `producer`: object; `producer.service`: string; `producer.version`: string; `producer.job_id`: string; `item_id`: string; `idempotency_key`: string; `platform`: string; `kind`: string; `source_id`: string; `parent_id`: null; `root_id`: null; `parent_seen`: boolean; `platform_id`: string; `url`: string; `created_at`: string; `fetched_at`: string; `title`: null; `text`: string; `text_norm`: string; `lang`: string; `lang_conf`: number; `dialect`: string; `dialect_conf`: number; `script`: string; `author`: object; `author.author_ref`: string; `author.author_type`: string; `author.author_source_id`: string; `author.display_name`: string; `author.author_followers`: ; `media`: array; `media[].type`: string; `media[].url`: string; `hashtags`: array; `at_mentions`: array; `links`: array; `metrics_snapshot`: object; `metrics_snapshot.likes`: integer; `metrics_snapshot.comments`: integer; `metrics_snapshot.shares`: integer; `metrics_snapshot.reactions_by_type`: object; `metrics_snapshot.reactions_by_type.LIKE`: integer; `metrics_snapshot.reactions_by_type.LOVE`: integer; `route`: string; `vendor`: null; `service`: string; `retention_class`: string; `expires_at`: null; `content_hash`: string; `version`: integer; `normalizer_version`: string; `lang_model_version`: string; `raw_ref`: string; `lang_pending`: boolean; `text_full_ref`: string |
| store-writer | read | `schema`: ; `kind`: ; `version`: ; `produced_at`: ; `expires_at`: ; `metrics_snapshot`: ; `parent_seen`: ; `created_at`:  |

### 2.3 `item.hits`

- In CONVENTIONS: yes
- Partition or message key as stated: `source_id` (alert-evaluator); `source_id (the source that produced the item)` (keyword-matcher); `message key: source_id` (keyword-matcher)
- Producers: 2; consumers: 4; mention only: 10

| Producer | Kinds or event types written | Refs |
|---|---|---|
| keyword-matcher | active, retracted | 2 L15; 5.3 L73; 5.3 L75; 6.2 L95; +2 more |
| tg-message-search | hit on a registered channel | 2 L15; 3 L22; 5.2 L55; 6.2 L73; +1 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| alert-evaluator | hit | 5.1 L40; 5.3 L61; 6.1 L79; 11 L134 |
| analysis-media | (all) | 5.1 L41; 6.1 L83; 13.4 L157 |
| analysis-sentiment | (all) | 3 L26; 5.1 L45; 5.2 L59; 6.1 L85 |
| store-writer | active, retracted | 1 L7; 3 L22; 5.1 L39; 5.3 L63 |

Mentioned without reading or writing: fb-keyword-search, ig-keyword-search, li-post-search, tt-hashtag-feed-poller, tt-keyword-search, tt-video-comments-fetcher, x-recent-search, x-replies-fetcher, yt-keyword-search, yt-web-search-bridge.

Fields per PRD, exactly as written (`path`: JSON type of the example).

| PRD | Access | Fields |
|---|---|---|
| alert-evaluator | read | `item_id`: ; `client_id`: ; `keyword_id`: ; `source_id`: ; `hit_at`:  |
| analysis-media | read | `item_id`:  |
| analysis-sentiment | read | `keyword_id`: ; `matched_text`: ; `item_id`:  |
| keyword-matcher | write | `schema`: string; `message_id`: string; `produced_at`: string; `producer`: object; `producer.service`: string; `producer.version`: string; `producer.job_id`: null; `hit_id`: string; `status`: string; `item_id`: string; `item_version`: integer; `platform`: string; `kind`: string; `source_id`: string; `client_id`: string; `keyword_id`: string; `keyword_set_version`: string; `lang_model_version`: string; `matched_term`: string; `form_id`: string; `occurrences`: integer; `offsets`: array; `offsets[]`: array; `offsets[][]`: integer; `offsets_in`: string; `hit_at`: string; `url`: string; `route`: string; `vendor`: null; `service`: string; `retention_class`: string; `expires_at`: null; `raw_ref`: string; `poster`: object; `poster.author_source_id`: string; `poster.author_ref`: string; `poster.author_type`: string |
| store-writer | read | `status`: ; `hit_at`: ; `client_id`: ; `keyword_id`: ; `item_id`:  |

### 2.4 `discovery.hits`

- In CONVENTIONS: yes
- Partition or message key as stated: `source_id (the source that produced the item)` (keyword-matcher); `message key: source_id` (keyword-matcher); `the keyword or hashtag source that produced the hit` (poster-resolver); `candidate_key` (search-hit-router, web-commoncrawl-scanner)
- Schema names: `discovery.hits/v1` (keyword-matcher, search-hit-router, tg-message-search, web-commoncrawl-scanner)
- Producers: 9; consumers: 4; mention only: 15

| Producer | Kinds or event types written | Refs |
|---|---|---|
| fb-page-search | page | 2 L13; 3 L21; 4 L34; 5.2 L54; +4 more |
| ig-hashtag-search | hashtag | 2 L13; 2 L15; 3 L24; 4 L36; +5 more |
| keyword-matcher | active, retracted | 2 L15; 5.3 L74; 6.2 L95; 6.2 L97-L117; +1 more |
| search-hit-router | account, group, page, channel, company_page, creator, site | 6.2 L99-L115; 1 L9; 2 L15; 3 L26; +6 more |
| tg-bot-channel-receiver | client-added candidate | 3 L23; 4 L36; 5.2 L70; 6.2 L134; +2 more |
| tg-discussion-receiver | group candidate | 5.2 L67; 6.2 L138 |
| tg-message-search | post | 2 L15; 3 L22; 4 L34; 5.2 L55; +3 more |
| web-commoncrawl-scanner | site | 6.2 L84-L103; 1 L9; 2 L15; 3 L25; +8 more |
| x-recent-search | (not stated) | 2 L13; 3 L22; 5.2 L58; 6.2 L98; +3 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| analysis-media | (all) | 5.1 L41; 6.1 L83 |
| analysis-sentiment | (all) | 3 L26; 5.1 L45; 6.1 L85 |
| poster-resolver | (all) | 5.1 L46; 5.1 L48; 5.2 L52; 6.1 L81; +1 more |
| store-writer | active, retracted | 1 L7; 3 L22; 5.1 L39; 5.2 L48; +2 more |

Mentioned without reading or writing: fb-keyword-search, ig-keyword-search, li-org-resolver, li-post-search, tg-channel-resolver, tt-hashtag-feed-poller, tt-keyword-search, tt-user-resolver, tt-video-comments-fetcher, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-replies-fetcher, yt-keyword-search, yt-web-search-bridge.

Common written fields (each path found in at least half of the 9 producer examples, with its usual JSON type):

`client_ids`: array, `platform`: string, `route`: string, `service`: string, `vendor`: string

Fields per PRD, exactly as written. For a producer, `common` stands for the set above, `+` lists the fields it adds, `−` the common fields its example lacks, and `type` a common field it gives another JSON type (null counts as compatible). A producer whose example has no `envelope` wrapper is marked **flat** and listed in full. 

| PRD | Access | Fields |
|---|---|---|
| analysis-media | read | `item_id`:  |
| analysis-sentiment | read | `keyword_id`: ; `matched_text`: ; `item_id`:  |
| fb-page-search | write | common; + `hit_type`: string, `found_at`: string, `keyword_id`: string, `query`: string, `client_ids[]`: string, `candidate`: object, `candidate.platform_id`: string, `candidate.name`: string, `candidate.link`: string, `candidate.is_verified`: boolean, `candidate.location`: object, `candidate.location.city`: string, `candidate.location.country`: string, `context`: null, `job_id`: string, `retention_class`: string |
| ig-hashtag-search | write | common; + `keyword_id`: string, `matched_in`: string, `item_idempotency_key`: string, `permalink`: string, `poster`: object, `poster.handle`: null, `poster.platform_id`: null, `poster.handles_in_caption`: array, `poster.handles_in_caption[]`: string, `client_ids[]`: string, `fetched_at`: string; − `vendor` |
| keyword-matcher | write | common; + `schema`: string, `message_id`: string, `produced_at`: string, `producer`: object, `producer.service`: string, `producer.version`: string, `producer.job_id`: null, `hit_id`: string, `status`: string, `item_id`: string, `item_version`: integer, `kind`: string, `source_id`: string, `client_id`: string, `keyword_id`: string, `keyword_set_version`: string, `lang_model_version`: string, `matched_term`: string, `form_id`: string, `occurrences`: integer, `offsets`: array, `offsets[]`: array, `offsets[][]`: integer, `offsets_in`: string, `hit_at`: string, `url`: string, `retention_class`: string, `expires_at`: null, `raw_ref`: string, `candidate`: object, `candidate.candidate_key`: string, `candidate.platform`: string, `candidate.platform_id`: string, `candidate.handle`: string, `candidate.author_ref`: string, `candidate_pending`: boolean; − `client_ids` |
| poster-resolver | read | `candidate (payload)`: ; `platform`: ; `hit_at`: ; `keyword and client`:  |
| search-hit-router | write | common; + `schema`: string, `message_id`: string, `produced_at`: string, `type`: string, `candidate_key`: string, `poster_ref`: object, `poster_ref.handle`: string, `poster_ref.platform_id`: null, `poster_ref.url`: string, `poster_ref.post_ref`: string, `poster_ref.handle_hint`: null, `origin`: string, `evidence`: object, `evidence.canonical_url_hash`: string, `evidence.engines`: array, `evidence.engines[]`: string, `evidence.sightings`: integer, `evidence.first_seen_at`: string, `evidence.keyword_rule_ids`: array, `evidence.keyword_rule_ids[]`: string, `evidence.client_ids`: array, `evidence.client_ids[]`: string, `evidence.title`: string, `evidence.snippet`: string; − `client_ids` |
| store-writer | read | `candidate`:  |
| tg-bot-channel-receiver | write | common; + `type`: string, `origin`: string, `proposed_source_id`: , `owned_by_client`: , `client id`: ; − `client_ids`, `platform`, `route`, `service`, `vendor` |
| tg-discussion-receiver | write | common; + `proposed_source_id`: ; − `client_ids`, `platform`, `route`, `service`, `vendor` |
| tg-message-search | write | common; + `schema`: string, `idempotency_key`: string, `kind`: string, `poster`: object, `poster.platform_id`: string, `poster.handle`: string, `poster.display_name`: string, `poster.source_type`: string, `keyword_ids`: array, `keyword_ids[]`: string, `client_ids[]`: string, `fetched_at`: string, `retention_class`: string |
| web-commoncrawl-scanner | write | common; + `schema`: string, `message_id`: string, `produced_at`: string, `type`: string, `candidate_key`: string, `poster_ref`: object, `poster_ref.host`: string, `poster_ref.registrable_domain`: string, `poster_ref.url`: string, `origin`: string, `evidence`: object, `evidence.crawl_id`: string, `evidence.captures`: integer, `evidence.first_capture`: string, `evidence.last_capture`: string, `evidence.sample_urls`: array, `evidence.sample_urls[]`: string, `evidence.path_signals`: array, `evidence.path_signals[]`: string, `evidence.language_share`: object, `evidence.language_share.ara`: number, `evidence.news_score`: number, `keyword_rule_id`: null |
| x-recent-search | write | common; + `item_idempotency_key`: , `author_platform_id`: , `author_handle`: , `keyword_rule_id`: , `matched_terms`: , `lang`: , `public_metrics`: , `fetched_at`: ; − `route`, `vendor` |

### 2.5 `poster.profiles`

- In CONVENTIONS: yes
- Partition or message key as stated: `source_id for a registered Page, candidate_key otherwise` (fb-page-resolver); `message key: candidate_key (and source_id when the request was a refresh)` (ig-account-resolver); `candidate_key` (poster-resolver); `message key: candidate_key` (poster-resolver); `source_id for a registered account; candidate_key for an organization or public figure; else candidate_ref` (x-user-resolver); `source_id for a registered channel; candidate_key otherwise` (yt-channel-resolver)
- Schema names: `poster.profiles/v1` (news-site-resolver, tg-channel-resolver); `1 (schema_version field)` (poster-resolver)
- Producers: 9; consumers: 2; mention only: 1

| Producer | Kinds or event types written | Refs |
|---|---|---|
| fb-page-resolver | page, individual | 2 L13; 3 L23; 4 L33; 5.2 L58; +6 more |
| ig-account-resolver | resolved, individual, review | 1 L7; 3 L23; 4 L33; 5.1 L50; +8 more |
| li-org-resolver | resolved, unresolved, remembered_reject, grant_missing | 6.2 L77-L105; 2 L15; 5.2 L57; 8 L124; +9 more |
| news-site-resolver | site | 6.2 L79-L110; 5.2 L54; 2 L11; 5.1 L41; +1 more |
| poster-resolver | resolved, individual, unresolvable, cached | 2 L15; 5.2 L53; 5.2 L58-L60; 6.2 L86-L89; +1 more |
| tg-channel-resolver | profile, unresolved | 2 L15; 5.2 L57-L59; 6.2 L77; 6.2 L79-L104; +6 more |
| tt-user-resolver | full profile (creator), bare verdict (individual), verdict with status not_found or private | 1 L7; 3 L22; 5.2 L56; 5.2 L57; +5 more |
| x-user-resolver | account, individual, unavailable, not_resolved | 2 L13; 4 L32; 5.2 L58-L60; 6.2 L101-L132; +3 more |
| yt-channel-resolver | resolved, unavailable | 2 L13; 3 L23; 4 L35; 5.2 L63; +4 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| qualifier | (all) | 2 L15; 3 L22; 5.1 L46; 5.4 L71; +1 more |
| tg-channel-resolver | profile | 3 L23; 5.2 L54; 6.1 L73; 13.4 L153 |

Mentioned without reading or writing: yt-keyword-search.

Common written fields (each path found in at least half of the 9 producer examples, with its usual JSON type):

`platform`: string, `profile`: object, `profile.followers`: integer

Fields per PRD, exactly as written. For a producer, `common` stands for the set above, `+` lists the fields it adds, `−` the common fields its example lacks, and `type` a common field it gives another JSON type (null counts as compatible). A producer whose example has no `envelope` wrapper is marked **flat** and listed in full. 

| PRD | Access | Fields |
|---|---|---|
| fb-page-resolver | write | common; + `envelope`: object, `envelope.platform`: string, `envelope.route`: string, `envelope.vendor`: null, `envelope.service`: string, `envelope.candidate_key`: string, `envelope.candidate_ref`: , `envelope.source_id`: null, `envelope.job_id`: string, `envelope.attempt`: integer, `envelope.fetched_at`: string, `envelope.cached_until`: string, `envelope.cache`: string, `envelope.retention_class`: string, `envelope.client_ids`: array, `envelope.client_ids[]`: string, `profile.resolved_type`: string, `profile.reason`: , `profile.platform_id`: string, `profile.handle`: string, `profile.display_name`: string, `profile.url`: string, `profile.category`: string, `profile.location`: object, `profile.location.city`: string, `profile.location.country`: string, `profile.website_domains`: array, `profile.website_domains[]`: string, `profile.signals`: object, `profile.signals.iq_domain`: boolean, `profile.signals.phone_964`: boolean, `profile.is_verified`: boolean, `profile.about`: string; − `platform` |
| ig-account-resolver | write | common; + `candidate_key`: string, `candidate_key_hash`: , `platform_id`: string, `handle`: string, `source_id`: null, `resolution`: string, `account_class`: string, `profile.name`: string, `profile.media_count`: integer, `profile.biography`: string, `profile.website`: string, `country_signals`: object, `country_signals.phone_964`: boolean, `country_signals.website_tld`: string, `country_signals.city_in_bio`: array, `country_signals.city_in_bio[]`: string, `reason`: null, `cache`: object, `cache.hit`: boolean, `cache.resolved_at`: string, `cache.expires_at`: string, `provenance`: object, `provenance.route`: string, `provenance.vendor`: null, `provenance.service`: string, `provenance.fetched_at`: string, `retention_class`: string, `client_ids`: array, `client_ids[]`: string, `job_id`: string, `attempt`: integer |
| li-org-resolver | write | common; + `candidate_key`: string, `source_type`: string, `platform_id`: string, `handle`: string, `url`: string, `display_name`: string, `route`: string, `vendor`: string, `owned_by_client`: boolean, `followers`: integer, `country_signals`: object, `country_signals.location`: string, `country_signals.phone_964`: boolean, `country_signals.iq_domain`: boolean, `country_signals.seed_list`: boolean, `lang_share`: object, `lang_share.ar_iq`: number, `lang_share.ckb`: number, `lang_share.en`: number, `last_post_at`: string, `posts_per_day`: number, `duplicate_text_share`: number, `posts_sampled`: integer, `resolution`: string, `service`: string, `resolved_at`: string, `job_id`: string, `reason`: , `type`: ; − `profile`, `profile.followers` |
| news-site-resolver | write | common; + `schema`: string, `kind`: string, `host`: string, `proposed_source`: object, `proposed_source.platform`: string, `proposed_source.source_type`: string, `proposed_source.platform_id`: string, `proposed_source.handle`: string, `proposed_source.url`: string, `proposed_source.display_name`: string, `proposed_source.route`: string, `proposed_source.vendor`: null, `proposed_source.retention_class`: string, `proposed_source.followers`: null, `proposed_source.country_signals`: object, `proposed_source.country_signals.tld_iq`: boolean, `proposed_source.country_signals.phone_964`: boolean, `proposed_source.country_signals.iraqi_place`: string, `proposed_source.country_signals.seed_list`: array, `proposed_source.country_signals.seed_list[]`: string, `proposed_source.lang_share`: object, `proposed_source.lang_share.msa`: number, `proposed_source.lang_share.iraqi_ar`: number, `proposed_source.lang_share.en`: number, `proposed_source.proposed_tier`: integer, `proposed_source.added_by`: string, `site_profile`: object, `site_profile.feeds`: array, `site_profile.feeds[].url`: string, `site_profile.feeds[].format`: string, `site_profile.feeds[].items`: integer, `site_profile.feeds[].newest_at`: string, `site_profile.feeds[].has_body`: boolean, `site_profile.news_sitemap`: string, `site_profile.sitemaps`: array, `site_profile.sitemaps[]`: string, `site_profile.homepage_diff`: boolean, `site_profile.article_url_patterns`: array, `site_profile.article_url_patterns[]`: string, `site_profile.comments_provider`: string, `site_profile.disqus_shortname`: string, `site_profile.access_mode`: string, `site_profile.articles_per_day_estimate`: integer, `site_profile.last_article_at`: string, `discovered_by`: string, `service`: string, `job_id`: string, `resolved_at`: string, `crawl_allowed`: ; − `profile`, `profile.followers` |
| poster-resolver | write | common; + `message_id`: string, `produced_at`: string, `service`: string, `schema_version`: integer, `candidate_key`: string, `platform_id`: string, `handle`: string, `url`: string, `display_name`: string, `account_type`: string, `individual`: boolean, `verified`: boolean, `followers`: integer, `posts_30d`: integer, `last_post_at`: string, `location_text`: string, `country_signals`: object, `country_signals.iraqi_place`: boolean, `country_signals.phone_964`: boolean, `country_signals.iq_domain`: boolean, `country_signals.outlet_link`: boolean, `country_signals.seed_list`: boolean, `lang_share`: object, `lang_share.ar_iq`: number, `lang_share.ckb`: number, `lang_share.ar_msa`: number, `lang_share.en`: number, `hits_30d`: integer, `keywords`: array, `keywords[]`: string, `client_ids`: array, `client_ids[]`: string, `route`: string, `vendor`: null, `resolver`: string, `resolved_at`: string, `cached`: boolean, `unresolvable`: null, `author_hash`: string, `schema_unknown`: boolean, `ambiguous`: ; − `profile`, `profile.followers` |
| qualifier | read | `candidate_key`: ; `individual`: ; `unresolvable`: ; `account_type`: ; `country_signals`: ; `lang_share`: ; `followers`: ; `cached`: ; `schema_unknown`: ; `resolved_at`: ; `author_hash`: ; `verified`: ; `origin`:  |
| tg-channel-resolver | write | common; + `schema`: string, `idempotency_key`: string, `source_type`: string, `platform_id`: string, `handle`: string, `display_name`: string, `followers`: integer, `country_signals`: object, `country_signals.vendor_country`: string, `country_signals.text_signals`: array, `country_signals.text_signals[]`: string, `category`: string, `growth`: object, `growth.subscribers_30d`: integer, `lang_share`: object, `lang_share.ar-iq`: number, `lang_share.ar`: number, `lang_share.ckb`: number, `lang_share.sample`: integer, `status`: string, `route`: string, `vendor`: string, `service`: string, `fetched_at`: string, `retention_class`: string; − `profile`, `profile.followers` |
| tt-user-resolver | write | common; + `envelope`: object, `envelope.platform`: string, `envelope.route`: string, `envelope.vendor`: string, `envelope.service`: string, `envelope.candidate_key`: string, `envelope.idempotency_key`: string, `envelope.job_id`: string, `envelope.attempt`: integer, `envelope.fetched_at`: string, `envelope.cache_hit`: boolean, `envelope.retention_class`: string, `envelope.client_ids`: array, `envelope.client_ids[]`: string, `profile.status`: string, `profile.creator_threshold_met`: boolean, `profile.platform_id`: string, `profile.handle`: string, `profile.display_name`: string, `profile.verified`: boolean, `profile.video_count`: integer, `profile.region`: string, `profile.bio`: string, `profile.bio_link`: string, `profile.signals`: object, `profile.signals.region_iq`: boolean, `profile.signals.iraqi_place_in_bio`: string, `profile.signals.phone_964`: boolean, `profile.signals.iq_domain`: boolean; − `platform` |
| x-user-resolver | write | common; + `envelope`: object, `envelope.platform`: string, `envelope.route`: string, `envelope.vendor`: null, `envelope.service`: string, `envelope.candidate_key`: string, `envelope.candidate_ref`: , `envelope.source_id`: null, `envelope.job_id`: string, `envelope.attempt`: integer, `envelope.fetched_at`: string, `envelope.cached_until`: string, `envelope.cache`: string, `envelope.retention_class`: string, `envelope.client_ids`: array, `envelope.client_ids[]`: string, `profile.resolved_type`: string, `profile.qualifies_as`: string, `profile.qualifies_by`: array, `profile.qualifies_by[]`: string, `profile.platform_id`: string, `profile.handle`: string, `profile.display_name`: string, `profile.url`: string, `profile.following`: integer, `profile.post_count`: integer, `profile.verified`: boolean, `profile.location_text`: string, `profile.description`: string, `profile.url_domain`: string, `profile.created_at`: string, `profile.account_age_days`: integer, `profile.signals`: object, `profile.signals.location_iq`: string, `profile.signals.iq_domain`: boolean, `profile.signals.phone_964`: boolean, `profile.reason`: ; − `platform` |
| yt-channel-resolver | write | common; + `envelope`: object, `envelope.platform`: string, `envelope.route`: string, `envelope.vendor`: null, `envelope.service`: string, `envelope.candidate_key`: string, `envelope.source_id`: null, `envelope.job_id`: string, `envelope.attempt`: integer, `envelope.fetched_at`: string, `envelope.cached_until`: string, `envelope.cache`: string, `envelope.ids_in_call`: integer, `envelope.retention_class`: string, `envelope.client_ids`: array, `envelope.client_ids[]`: string, `profile.resolved_type`: string, `profile.verdict`: string, `profile.platform_id`: string, `profile.handle`: string, `profile.display_name`: string, `profile.url`: string, `profile.description`: string, `profile.country`: string, `profile.country_source`: string, `profile.default_language`: string, `profile.subscribers_hidden`: boolean, `profile.video_count`: integer, `profile.view_count`: integer, `profile.published_at`: string, `profile.uploads_playlist_id`: string, `profile.website_domains`: array, `profile.website_domains[]`: string, `profile.signals`: object, `profile.signals.country_iq`: boolean, `profile.signals.iq_place_names`: array, `profile.signals.iq_place_names[]`: string, `profile.signals.description_lang`: string, `profile.signals.iq_domain`: boolean, `profile.made_for_kids`: null, `profile.review_flags`: array; − `platform` |

### 2.6 `registry.decisions`

- In CONVENTIONS: yes
- Partition or message key as stated: `candidate_key (or source_id for sweep decisions)` (qualifier)
- Schema names: `1 (schema_version field)` (qualifier)
- Producers: 3; consumers: 2; mention only: 1

| Producer | Kinds or event types written | Refs |
|---|---|---|
| qualifier | add, reject, review, queued, mention_only, tier_down, retire, tier_change | 2 L15; 3 L23; 5.2 L63; 6.2 L81-L84 |
| retention-purger | remove_client | 3 L22; 5.3 L76; 6.2 L94; 13.6 L162 |
| source-health-canary | health_change | 3 L24; 5.2 L57; 5.2 L58; 6.2 L99-L102; +1 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| registry-writer | add, update, tier_change, tier_down, dormant, promote, retire, health_change, remove_client, queued, mention_only | 2 L15; 3 L22; 4 L36; 5.2 L49-L57; +2 more |
| yt-text-purger | remove_client | 5.1 L45; 6.1 L130 |

Mentioned without reading or writing: tg-channel-resolver.

Fields per PRD, exactly as written (`path`: JSON type of the example).

| PRD | Access | Fields |
|---|---|---|
| qualifier | write | `message_id`: string; `produced_at`: string; `service`: string; `schema_version`: integer; `decision_id`: string; `candidate_key`: string; `source_id`: null; `decision`: string; `rule_hit`: integer; `reason`: string; `origin`: string; `platform`: string; `source_type`: string; `platform_id`: string; `handle`: string; `url`: string; `display_name`: string; `route`: string; `vendor`: null; `tier`: integer; `retention_class`: string; `client_ids`: array; `client_ids[]`: string; `owned_by_client`: boolean; `followers`: integer; `country_signals`: object; `country_signals.iraqi_place`: boolean; `country_signals.phone_964`: boolean; `country_signals.iq_domain`: boolean; `country_signals.outlet_link`: boolean; `country_signals.seed_list`: boolean; `lang_share`: object; `lang_share.ar_iq`: number; `lang_share.ckb`: number; `lang_share.ar_msa`: number; `lang_share.en`: number; `added_by`: string; `review`: null; `expires_at`: null; `author_hash`: string |
| registry-writer | read | `decision_id`: ; `decision`: ; `origin`: ; `source_id`: ; `platform`: ; `route`: ; `vendor`: ; `health`: ; `fallback`: ; `author_hash`:  |
| source-health-canary | write | `decision_id`: string; `action`: string; `actor`: string; `platform`: string; `route`: string; `vendor`: string; `health`: string; `fallback`: object; `fallback.route`: string; `fallback.vendor`: string; `scope`: string; `reason`: string; `evidence`: object; `evidence.window_minutes`: integer; `evidence.samples`: integer; `evidence.empty_200`: integer; `evidence.rate`: number; `evidence.targets`: integer; `at`: string |

### 2.7 `source.events`

- In CONVENTIONS: yes
- Partition or message key as stated: `source_id` (backfill-orchestrator, registry-writer)
- Schema names: `1 (schema_version field)` (registry-writer)
- Producers: 20; consumers: 46; mention only: 3

| Producer | Kinds or event types written | Refs |
|---|---|---|
| fb-backfill | updated | 5.2 L56; 6.2 L110 |
| fb-group-posts-poller | tier change | 5.1 L42; 5.2 L61; 6.2 L124; 13.9 L187 |
| fb-page-feed-poller | tier change, updated | 5.1 L42; 5.2 L59; 6.2 L129; 8 L150; +1 more |
| ig-account-media-poller | tier change, dormant, updated | 5.1 L44; 5.2 L63; 6.2 L125; 8 L141 |
| ig-hashtag-search | fallback_on, updated | 5.1 L57; 6.2 L93; 13.3 L176 |
| ig-mentions-fetcher | updated | 8 L143 |
| ig-webhook-receiver | updated | 5.2 L60; 6.2 L125; 13.10 L183 |
| li-client-posts-poller | updated | 6.2 L126; 8 L142 |
| li-company-posts-poller | tier change, updated | 5.1 L43; 5.2 L61; 6.2 L123; 8 L142; +1 more |
| li-notification-receiver | updated | 6.2 L133 |
| news-feed-poller | tier change | 6.2 L115; 5.1 L42 |
| registry-writer | added, updated, tier_change, dormant, retired, fallback_on, fallback_off | 2 L15; 3 L24; 4 L37; 5.2 L52-L59; +1 more |
| tg-bot-channel-receiver | updated | 3 L23; 5.2 L72; 6.2 L134; 13.7 L187 |
| tg-channel-posts-poller | tier change | 3 L22; 5.1 L44; 5.2 L66; 6.2 L128 |
| tg-discussion-receiver | (not stated) | 5.2 L69; 6.2 L138; 13.8 L192 |
| tt-client-videos-fetcher | updated, retired | 6.2 L115; 8 L130; 8 L131; 13.4 L165 |
| tt-profile-videos-poller | tier change | 5.1 L43; 5.2 L62; 6.2 L126 |
| x-full-archive-search | updated | 6.2 L128; 8 L148 |
| x-user-timeline-poller | tier change, updated | 5.1 L40; 5.2 L60; 6.2 L134; 8 L151; +1 more |
| yt-uploads-reconciler | tier change | 3 L25; 5.2 L65; 6.2 L136 |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| aggregator | retirement, client_ids change | 5.1 L37; 6.1 L73; 11 L128 |
| alert-evaluator | (all) | 5.3 L61; 6.1 L79; 6.3 L105; 11 L134 |
| analysis-entities | (all) | 5.1 L42; 6.1 L86 |
| analysis-media | (all) | 5.1 L43; 6.1 L83 |
| analysis-sentiment | (all) | 5.1 L47; 6.1 L85 |
| analysis-topics | (all) | 5.1 L46; 6.1 L89 |
| backfill-orchestrator | added, retired, updated | 3 L22; 5.1 L42; 5.2 L54; 5.4 L89; +1 more |
| comment-decay-scheduler | retired | 4 L36; 5.1 L42; 6.1 L135; 13.11 L198 |
| fb-client-webhook-receiver | added, updated, tier change, retired | 5.2 L54; 6.1 L105 |
| fb-group-comments-fetcher | fallback_on, fallback_off, retired | 6.1 L100; 8 L144 |
| fb-group-posts-poller | added, tier change, retired, fallback_on, fallback_off | 6.1 L98; 8 L148; 13.8 L186 |
| fb-keyword-search | (all) | 6.1 L93 |
| fb-page-feed-poller | added, tier change, retired | 6.1 L104 |
| fb-page-resolver | added, tier change, retired | 6.1 L95 |
| fb-post-comments-fetcher | retired, updated | 6.1 L95 |
| ig-account-media-poller | added, tier change, retired | 6.1 L100 |
| ig-keyword-search | added, tier change, retired, fallback_on, fallback_off | 3 L20; 6.1 L92; 13.5 L170 |
| ig-mentions-fetcher | added, retired | 6.1 L100 |
| keyword-matcher | (all) | 5.1 L40; 6.1 L90; 6.3 L122; 11 L152 |
| li-client-posts-poller | added, updated, route change, retired | 6.1 L101 |
| li-company-posts-poller | (all) | 6.1 L98 |
| li-notification-receiver | added, retired | 5.1 L42; 6.1 L108; 13.11 L193 |
| news-feed-poller | added, updated, tier change, retired | 6.1 L88; 5.1 L48 |
| news-homepage-differ | (all) | 6.1 L93; 5.1 L49 |
| news-robots-checker | added, tier change, retired | 6.1 L89; 5.1 L49 |
| news-sitemap-poller | (all) | 6.1 L100; 5.1 L49 |
| normalize-item | (all) | 5.2 L54; 6.1 L86; 6.3 L124; 8 L136; +1 more |
| quota-governor | added | 6.1 L94; 11 L143 |
| raw-archiver | (all) | 6.1 L92 |
| retention-purger | retired, updated | 5.1 L43; 5.3 L74; 6.1 L90 |
| search-hit-router | added | 5.1 L47; 6.1 L95; 6.3 L138; 11 L168; +1 more |
| source-health-canary | added, retired | 6.1 L96 |
| store-writer | tier change (13.10), (any event: batch of up to 500 ids) | 3 L22; 5.1 L39; 5.3 L84; 13.10 L176 |
| tg-bot-channel-receiver | (all) | 5.2 L60; 6.1 L109 |
| tg-channel-posts-poller | (all) | 6.1 L103 |
| tg-discussion-receiver | (all) | 6.1 L110 |
| tt-client-videos-fetcher | added, retired | 6.1 L90 |
| tt-profile-videos-poller | added, tier change, retired, fallback_on, fallback_off | 6.1 L101 |
| web-commoncrawl-scanner | (all) | 10 L136 |
| x-filtered-stream | retired, tier change | 5.1 L38; 6.1 L107; 13.2 L192 |
| x-recent-search | added, tier change, retired | 6.1 L94 |
| x-user-resolver | added, tier change, retired | 6.1 L97 |
| x-user-timeline-poller | added, tier change, dormant, retired | 6.1 L108 |
| yt-channel-resolver | added, tier change, retired | 6.1 L99 |
| yt-pubsub-receiver | added, updated, retired | 5.1 L38; 5.2 L50; 5.2 L53; 6.1 L98; +2 more |
| yt-uploads-reconciler | added, updated, tier change, dormant, retired | 5.1 L51; 6.1 L104; 13.6 L189; 14.4 L201 |

Mentioned without reading or writing: ig-account-resolver, news-site-resolver, qualifier.

Common written fields (each path found in at least half of the 4 producer examples, with its usual JSON type):

`reason`: null

Fields per PRD, exactly as written. For a producer, `common` stands for the set above, `+` lists the fields it adds, `−` the common fields its example lacks, and `type` a common field it gives another JSON type (null counts as compatible). A producer whose example has no `envelope` wrapper is marked **flat** and listed in full. 

| PRD | Access | Fields |
|---|---|---|
| aggregator | read | `client_ids`:  |
| alert-evaluator | read | `followers`:  |
| backfill-orchestrator | read | `event`: ; `source_id`:  |
| fb-backfill | write | common; + `backfill_status`: ; − `reason` |
| registry-writer | write | common; + `message_id`: string, `produced_at`: string, `service`: string, `schema_version`: integer, `event`: string, `source_id`: string, `platform`: string, `source_type`: string, `platform_id`: string, `handle`: string, `route`: string, `vendor`: null, `tier`: integer, `retention_class`: string, `client_ids`: array, `client_ids[]`: string, `owned_by_client`: boolean, `followers`: integer, `previous`: null, `previous.tier`: integer, `previous.health`: string, `previous.route`: string, `previous.vendor`: null, `health`: string, `decision_id`: string, `actor`: string, `at`: string; − `reason` |
| retention-purger | read | `client_ids`:  |
| store-writer | read | `source_id`:  |
| x-full-archive-search | write | common |
| x-user-timeline-poller | write | common |
| yt-uploads-reconciler | read | `reason`:  |

### 2.8 `items.analysis`

- In CONVENTIONS: yes
- Partition or message key as stated: `source_id` (analysis-entities, analysis-media, analysis-sentiment, analysis-topics); `message key: logical key item_id + task + model_version` (analysis-entities, analysis-media, analysis-sentiment, analysis-topics)
- Schema names: `items.analysis/v1` (analysis-entities, analysis-media, analysis-sentiment, analysis-topics, store-writer)
- Producers: 4; consumers: 1; mention only: 0

| Producer | Kinds or event types written | Refs |
|---|---|---|
| analysis-entities | entities | 2 L13; 4 L33; 5.2 L56; 6.2 L90-L115; +1 more |
| analysis-media | media_fetch, media_ocr, media_tags, media_asr, media_logo | 2 L13; 4 L34; 5.2 L52-L56; 6.2 L87-L110; +1 more |
| analysis-sentiment | sentiment, sentiment_aspect | 2 L15; 4 L37; 5.2 L59-L60; 6.2 L89-L111; +1 more |
| analysis-topics | topics:<taxonomy_id>, topics:global, topic_cluster | 2 L15; 4 L37; 5.2 L60; 5.3 L72; +3 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| store-writer | (all) | 1 L7; 3 L22; 5.1 L39; 5.3 L61; +2 more |

Common written fields (each path found in at least half of the 4 producer examples, with its usual JSON type):

`analysis_key`: string, `content_hash`: string, `dialect`: string, `expires_at`: null, `input_hash`: string, `item_fetched_at`: string, `item_id`: string, `item_version`: integer, `kind`: string, `lane`: string, `lang`: string, `message_id`: string, `model_version`: string, `platform`: string, `produced_at`: string, `producer`: object, `producer.job_id`: string, `producer.service`: string, `producer.version`: string, `reason`: string, `result`: object, `result.low_confidence`: boolean, `retention_class`: string, `route`: string, `run_kind`: string, `schema`: string, `source_id`: string, `status`: string, `task`: string, `vendor`: null

Fields per PRD, exactly as written. For a producer, `common` stands for the set above, `+` lists the fields it adds, `−` the common fields its example lacks, and `type` a common field it gives another JSON type (null counts as compatible). A producer whose example has no `envelope` wrapper is marked **flat** and listed in full. 

| PRD | Access | Fields |
|---|---|---|
| analysis-entities | write | common; + `kb_version`: integer, `degraded`: boolean, `result.entities`: array, `result.entities[].type`: string, `result.entities[].entity_id`: string, `result.entities[].name_en`: string, `result.entities[].level`: string, `result.entities[].governorate_id`: string, `result.entities[].surface`: string, `result.entities[].start`: integer, `result.entities[].end`: integer, `result.entities[].link_score`: number, `result.entities[].source`: string, `result.unlinked`: array, `result.private_person_mentions`: integer; − `result.low_confidence` |
| analysis-media | write | common; + `result.media`: array, `result.media[].index`: integer, `result.media[].type`: string, `result.media[].sha256`: string, `result.media[].reused`: boolean, `result.media[].text`: string, `result.media[].lang`: string, `result.media[].script`: string, `result.media[].confidence`: number, `result.media[].frames`: null, `result.media[].truncated`: boolean, `result (media_tags)`: , `result (media_asr)`: , `result (media_logo)`: ; − `dialect`, `lang`, `result.low_confidence` |
| analysis-sentiment | write | common; + `preproc_version`: string, `result.label`: string, `result.score`: number, `result.confidence`: number, `result.probs`: object, `result.probs.positive`: number, `result.probs.negative`: number, `result.probs.neutral`: number, `result.probs.mixed`: number, `result.sarcasm_prob`: number, `result.sarcasm_flag`: boolean, `result.code_switched`: boolean, `result.truncated`: boolean, `result.model_route`: string, `result.targets[]`: array, `result.targets[].keyword_id`: , `result.targets[].matched_text`: , `result.targets[].label`: , `result.targets[].score`: , `result.targets[].confidence`:  |
| analysis-topics | write | common; + `taxonomy_version`: integer, `result.topics`: array, `result.topics[].node_id`: string, `result.topics[].score`: number, `result.topics[].source`: string, `result.top_topic`: string, `result.intent`: object, `result.intent.label`: string, `result.intent.score`: number, `zero_shot_unavailable`: boolean |
| store-writer | read | `model`: ; `model_version`: ; `output`: ; `analyzed_at`: ; `sentiment label and score`: ; `topic ids`: ; `entity ids`: ; `retention_class`:  |

### 2.9 `item.metrics`

- In CONVENTIONS: yes
- Partition or message key as stated: `message key: observations keyed on (item_id, observed_at)` (fb-reactions-fetcher)
- Producers: 5; consumers: 2; mention only: 2

| Producer | Kinds or event types written | Refs |
|---|---|---|
| fb-reactions-fetcher | poll, backfill, webhook_reconcile, refresh_24h, refresh_7d, refresh_client | 2 L13; 3 L19; 4 L33; 5.1 L39; +8 more |
| normalize-item | observation | 3 L24; 4 L33; 5.2 L56; 6.2 L91; +1 more |
| tt-client-videos-fetcher | plus_24h, plus_7d | 3 L20; 5.1 L51; 5.2 L59; 6.2 L115; +3 more |
| tt-video-stats-refresher | plus_24h, plus_7d | 1 L7; 2 L13; 3 L20; 3 L21; +8 more |
| yt-video-details-fetcher | first_sight, ops_force, refresh_24h, refresh_7d, refresh_client, live_end | 2 L13; 3 L19-L20; 5.1 L54; 5.2 L61; +5 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| li-notification-receiver | (all) | 6.1 L108; 5.1 L42; 13.8 L190 |
| store-writer | observation | 1 L7; 3 L22; 5.1 L39; 5.3 L62; +2 more |

Mentioned without reading or writing: fb-post-comments-fetcher, li-own-comments-fetcher.

Common written fields (each path found in at least half of the 4 producer examples, with its usual JSON type):

`age_seconds`: integer, `item_idempotency_key`: string, `job_id`: string, `metrics`: object, `metrics.comments`: integer, `observation`: string, `observed_at`: string, `platform`: string, `platform_id`: string, `post_created_time`: string, `retention_class`: string, `route`: string, `service`: string, `source_id`: string, `vendor`: null

Fields per PRD, exactly as written. For a producer, `common` stands for the set above, `+` lists the fields it adds, `−` the common fields its example lacks, and `type` a common field it gives another JSON type (null counts as compatible). A producer whose example has no `envelope` wrapper is marked **flat** and listed in full. 

| PRD | Access | Fields |
|---|---|---|
| fb-reactions-fetcher | write | common; + `metrics.like`: integer, `metrics.love`: integer, `metrics.haha`: integer, `metrics.wow`: integer, `metrics.sad`: integer, `metrics.angry`: integer, `metrics.care`: integer, `metrics.reactions_total`: integer, `metrics.shares`: integer |
| store-writer | read | `observed_at`: ; `likes`: ; `comments`: ; `shares`: ; `views`: ; `reactions by type`: ; `retention_class`: ; `created_at`: ; `source_id`:  |
| tt-client-videos-fetcher | write | common; + `label`: , `the four counts`: , `first_seen_at`: , `lateness_seconds`: , `envelope (same envelope fields)`: ; − `age_seconds`, `item_idempotency_key`, `job_id`, `metrics`, `metrics.comments`, `observation`, `platform`, `platform_id`, `post_created_time`, `retention_class`, `route`, `service`, `source_id`, `vendor` |
| tt-video-stats-refresher | write | common; + `envelope`: object, `envelope.platform`: string, `envelope.route`: string, `envelope.vendor`: string, `envelope.service`: string, `envelope.source_id`: string, `envelope.idempotency_key`: string, `envelope.item_key`: string, `envelope.job_id`: string, `envelope.attempt`: integer, `envelope.fetched_at`: string, `envelope.retention_class`: string, `envelope.client_ids`: array, `envelope.client_ids[]`: string, `observation.label`: string, `observation.first_seen_at`: string, `observation.due_at`: string, `observation.observed_at`: string, `observation.lateness_seconds`: integer, `observation.views`: integer, `observation.likes`: integer, `observation.shares`: integer, `observation.comments`: integer, `observation.regressed`: boolean, `observation.baseline_missing`: boolean; − `age_seconds`, `item_idempotency_key`, `job_id`, `metrics`, `metrics.comments`, `observed_at`, `platform`, `platform_id`, `post_created_time`, `retention_class`, `route`, `service`, `source_id`, `vendor`; type `observation`: object |
| yt-video-details-fetcher | write | common; + `channel_id`: string, `live_state`: string, `metrics.views`: integer, `metrics.likes`: integer, `call_id`: string |

### 2.10 `deletions`

- In CONVENTIONS: yes
- Partition or message key as stated: `author_hash for author-scope messages (14.4); otherwise not stated` (deletion-propagator); `source_id; author-scope messages keyed by author_hash` (retention-purger); `message key: source_id or author_hash` (retention-purger); `source_id` (x-compliance-sync); `message key: author_hash (author-scope messages)` (x-compliance-sync); `message key: source_id` (yt-text-purger)
- Producers: 19; consumers: 6; mention only: 8

| Producer | Kinds or event types written | Refs |
|---|---|---|
| fb-client-webhook-receiver | platform_sync | 3 L21; 4 L34; 5.2 L56; 6.2 L133; +1 more |
| fb-group-comments-fetcher | platform_sync | 5.2 L65; 6.2 L128; 8 L145; 13.6 L180 |
| fb-post-comments-fetcher | platform_sync | 2 L13; 3 L21; 5.2 L69; 6.2 L125; +1 more |
| fb-reactions-fetcher | platform_sync | 5.4 L92; 6.2 L126; 8 L144; 13.3 L176 |
| ig-own-comments-fetcher | platform_sync | 3 L21; 4 L35; 5.1 L47; 5.1 L49; +3 more |
| li-client-posts-poller | platform_sync | 5.1 L48; 5.2 L60; 6.2 L126; 13.6 L179 |
| li-notification-receiver | platform_sync | 3 L21; 5.2 L56; 5.4 L97; 5.4 L99; +2 more |
| li-own-comments-fetcher | platform_sync | 5.1 L48; 5.2 L62; 6.2 L126; 13.5 L177 |
| li-post-comments-fetcher | platform_sync | 5.2 L64; 6.2 L129; 13.7 L183; 14.3 L194 |
| news-comments-fetcher | platform_sync | 3 L20; 4 L35; 5.2 L58-L59; 6.2 L120; +1 more |
| retention-purger | retention, author_request, client_offboarding, legal | 3 L20; 5.3 L62-L67; 5.3 L72; 5.3 L76; +2 more |
| tt-video-comments-fetcher | platform_sync | 6.2 L119; 8 L138; 13.7 L173 |
| tt-video-stats-refresher | platform_sync | 3 L22; 5.2 L60; 6.2 L112; 8 L130; +1 more |
| x-compliance-sync | platform_sync | 3 L20; 4 L36; 5.2 L57; 5.3 L73-L81; +5 more |
| yt-comments-fetcher | platform_sync | 2 L13; 5.2 L59; 6.2 L136; 8 L158; +2 more |
| yt-pubsub-receiver | platform_sync | 3 L21; 5.2 L55; 6.2 L130; 13.6 L180 |
| yt-replies-fetcher | platform_sync | 2 L13; 5.2 L56; 6.2 L125; 8 L146; +2 more |
| yt-text-purger | retention (scope text_only, mode purge_text), client_offboarding (scope text_only, client_id set), retention (scope derived, mode purge_derived) | 3 L20; 5.2 L54; 5.3 L104-L118; 6.2 L137; +5 more |
| yt-video-details-fetcher | platform_sync | 2 L13; 3 L22; 4 L34; 5.2 L62; +3 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| aggregator | (all) | 5.1 L37; 6.1 L73; 11 L128; 13.5 L145 |
| alert-evaluator | platform_sync (fires), X compliance reason as named by deletion-propagator (fires), retention (never fires), client offboarding (never fires), user privacy request (never fires) | 5.1 L40; 5.3 L61; 6.1 L79; 11 L134; +2 more |
| comment-decay-scheduler | (all) | 5.1 L42; 6.1 L135; 13.11 L198 |
| deletion-propagator | platform_sync, retention, author_request, client_offboarding, legal | 2 L13; 3 L19; 5.1 L43; 5.4 L80; +3 more |
| retention-purger | platform_sync | 3 L20; 5.1 L43; 5.4 L84; 6.1 L90 |
| x-user-resolver | (all) | 3 L22; 6.1 L97; 10 L161; 13.10 L186 |

Mentioned without reading or writing: analysis-entities, analysis-media, analysis-sentiment, analysis-topics, li-company-posts-poller, tg-discussion-receiver, tt-client-videos-fetcher, x-replies-fetcher.

Common written fields (each path found in at least half of the 11 producer examples, with its usual JSON type):

`reason`: string

Fields per PRD, exactly as written. For a producer, `common` stands for the set above, `+` lists the fields it adds, `−` the common fields its example lacks, and `type` a common field it gives another JSON type (null counts as compatible). A producer whose example has no `envelope` wrapper is marked **flat** and listed in full. 

| PRD | Access | Fields |
|---|---|---|
| alert-evaluator | read | `reason`: ; `item_id`:  |
| deletion-propagator | read | `reason`: ; `scope`: ; `target`: ; `target.platform`: ; `target.kind`: ; `target.platform_id`: ; `target.item_ids`: ; `target.author_hash`: ; `target.source_id`: ; `target.client_id`: ; `deletion_id`: ; `mode`: ; `retention_class`: ; `signal_at`: ; `due_at`: ; `requested_by`: ; `run_id`:  |
| fb-client-webhook-receiver | write | common |
| fb-group-comments-fetcher | write | common; + `platform`: , `kind`: , `idempotency_key`: , `service`: , `job_id`: , `detected_at`:  |
| fb-post-comments-fetcher | write | common; + `platform`: string, `kind`: string, `idempotency_key`: string, `parent_platform_id`: string, `service`: string, `job_id`: string, `detected_at`: string |
| retention-purger | read | `signal_at`:  |
| retention-purger | write | common; + `deletion_id`: string, `scope`: string, `mode`: string, `retention_class`: string, `source_id`: string, `target`: object, `target.platform`: string, `target.kind`: string, `target.item_ids`: array, `target.item_ids[]`: string, `client_id`: null, `requested_by`: string, `run_id`: string, `signal_at`: string, `due_at`: string, `emitted_at`: string, `author_hash`: string |
| tt-video-comments-fetcher | write | common |
| tt-video-stats-refresher | write | common; + `item key`:  |
| x-compliance-sync | write | common; + `deletion_id`: string, `scope`: string, `mode`: string, `retention_class`: string, `source_id`: string, `target`: object, `target.platform`: string, `target.kind`: string, `target.item_ids`: array, `target.item_ids[]`: string, `target.platform_ids`: array, `target.platform_ids[]`: string, `target.user_ids`: , `platform_status`: string, `countries`: null, `client_id`: null, `requested_by`: string, `run_id`: string, `x_job_id`: string, `event_at`: string, `signal_at`: string, `due_at`: string, `emitted_at`: string |
| yt-comments-fetcher | write | common; + `idempotency_key`: , `parent_video_id`: , `job_id`: , `detected_at`:  |
| yt-replies-fetcher | write | common; + `idempotency_key`: , `parent_video_id`: , `parent_comment_id`: , `job_id`: , `detected_at`:  |
| yt-text-purger | write | common; + `deletion_id`: string, `scope`: string, `mode`: string, `retention_class`: string, `source_id`: string, `target`: object, `target.platform`: string, `target.kind`: string, `target.video_id`: string, `target.item_ids`: array, `target.item_ids[]`: string, `target.fetched_before`: string, `client_id`: null, `requested_by`: string, `run_id`: string, `parent_run_id`: string, `signal_at`: string, `due_at`: string, `emitted_at`: string |
| yt-video-details-fetcher | write | common; + `call_id (both)`:  |

### 2.11 `article.urls`

- In CONVENTIONS: yes
- Partition or message key as stated: `source_id` (news-article-extractor, news-feed-poller, news-homepage-differ, news-sitemap-poller, search-hit-router)
- Schema names: `article.urls/v1` (search-hit-router)
- Producers: 4; consumers: 1; mention only: 1

| Producer | Kinds or event types written | Refs |
|---|---|---|
| news-feed-poller | article_url | 6.2 L92-L113; 5.2 L57; 2 L13; 3 L20; +1 more |
| news-homepage-differ | article_url | 6.2 L97-L116; 5.2 L58; 5.1 L49; 2 L13; +1 more |
| news-sitemap-poller | article_url | 6.2 L104-L125; 5.2 L60; 2 L13; 5.1 L51 |
| search-hit-router | (not stated) | 6.2 L117-L132; 1 L9; 3 L26; 5.1 L47; +4 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| news-article-extractor | (all) | 3 L19; 5.1 L41-L43; 6.1 L85; 2 L13; +1 more |

Mentioned without reading or writing: web-gdelt-poller.

Common written fields (each path found in at least half of the 4 producer examples, with its usual JSON type):

`envelope`: object, `envelope.access_mode`: string, `envelope.attempt`: integer, `envelope.found_at`: string, `envelope.found_via`: string, `envelope.job_id`: string, `envelope.kind`: string, `envelope.platform`: string, `envelope.retention_class`: string, `envelope.route`: string, `envelope.service`: string, `envelope.source_id`: string, `envelope.url_key`: string, `envelope.vendor`: null, `payload`: object, `payload.published_at`: string, `payload.title`: string, `payload.url`: string

Fields per PRD, exactly as written. For a producer, `common` stands for the set above, `+` lists the fields it adds, `−` the common fields its example lacks, and `type` a common field it gives another JSON type (null counts as compatible). A producer whose example has no `envelope` wrapper is marked **flat** and listed in full. 

| PRD | Access | Fields |
|---|---|---|
| news-article-extractor | read | `found_via`: ; `found_at`:  |
| news-feed-poller | write | common; + `payload.feed_url`: string, `payload.feed_format`: string |
| news-homepage-differ | write | common; + `payload.baseline`: boolean, `payload.section_url`: string, `payload.rank`: integer; − `payload.title` |
| news-sitemap-poller | write | common; + `payload.language`: string, `payload.publication_name`: string, `payload.sitemap_url`: string |
| search-hit-router | write | **flat**: `schema`: string; `message_id`: string; `idempotency_key`: string; `service`: string; `found_by`: string; `source_id`: string; `url`: string; `canonical_url`: string; `canonical_url_hash`: string; `engines`: array; `engines[]`: string; `keyword_rule_ids`: array; `keyword_rule_ids[]`: string; `client_ids`: array; `client_ids[]`: string; `title`: string; `snippet`: string; `published_hint`: string; `first_seen_at`: string |

### 2.12 `search.results`

- In CONVENTIONS: yes
- Partition or message key as stated: `canonical_url_hash` (search-hit-router, web-gdelt-poller, web-search-mojeek, web-search-perplexity)
- Schema names: `search.results/v1` (search-hit-router, web-gdelt-poller, web-search-mojeek, web-search-perplexity)
- Producers: 4; consumers: 1; mention only: 1

| Producer | Kinds or event types written | Refs |
|---|---|---|
| web-gdelt-poller | (not stated) | 6.2 L92-L111; 2 L15; 3 L25; 4 L35; +5 more |
| web-search-mojeek | (not stated) | 6.2 L89-L109; 2 L15; 3 L25; 4 L36; +4 more |
| web-search-perplexity | (not stated) | 6.2 L90-L108; 2 L15; 3 L24; 4 L35; +4 more |
| yt-web-search-bridge | video, channel | 3 L23; 4 L37; 5.2 L60; 6.2 L102-L124; +3 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| search-hit-router | (all) | 1 L7; 3 L23; 5.1 L43; 5.1 L49; +6 more |

Mentioned without reading or writing: web-commoncrawl-scanner.

Common written fields (each path found in at least half of the 4 producer examples, with its usual JSON type):

`attempt`: integer, `canonical_url`: string, `canonical_url_hash`: string, `client_ids`: array, `client_ids[]`: string, `engine`: string, `fetched_at`: string, `job_id`: string, `job_kind`: string, `keyword_id`: string, `keyword_rule_id`: string, `message_id`: string, `produced_at`: string, `query`: object, `query.country`: string, `query.lang`: string, `query.request_id`: string, `query.text`: string, `query.variant`: string, `raw_ref`: string, `result`: object, `result.date`: string, `result.last_updated`: string, `result.rank`: integer, `result.snippet`: string, `result.title`: string, `result.url`: string, `retention_class`: string, `route`: string, `schema`: string, `service`: string, `vendor`: string

Fields per PRD, exactly as written. For a producer, `common` stands for the set above, `+` lists the fields it adds, `−` the common fields its example lacks, and `type` a common field it gives another JSON type (null counts as compatible). A producer whose example has no `envelope` wrapper is marked **flat** and listed in full. 

| PRD | Access | Fields |
|---|---|---|
| search-hit-router | read | `schema`: string; `message_id`: ; `result`: object; `query`: object; `keyword rule (field name not stated)`: ; `client_ids`: ; `engine`: ; `canonical_url`: ; `canonical_url_hash`: ; `raw_ref`: ; `hints`: object |
| web-gdelt-poller | write | common; + `hints`: object, `hints.domain`: string, `hints.language`: string, `hints.source_country`: string |
| web-search-mojeek | write | common |
| web-search-perplexity | write | common |
| yt-web-search-bridge | write | common; + `idempotency_key`: string, `platform`: string, `platform_hint`: string, `handled_by`: string, `source_id`: string, `cost`: object, `cost.currency`: string, `cost.amount`: number, `extracted`: object, `extracted.kind`: string, `extracted.video_id`: string, `payload`: object, `payload.title`: string, `payload.url`: string, `payload.desc`: string; − `attempt`, `canonical_url`, `canonical_url_hash`, `client_ids`, `client_ids[]`, `job_kind`, `keyword_id`, `keyword_rule_id`, `message_id`, `produced_at`, `query.country`, `query.lang`, `query.request_id`, `query.text`, `query.variant`, `raw_ref`, `result`, `result.date`, `result.last_updated`, `result.rank`, `result.snippet`, `result.title`, `result.url`, `retention_class`, `schema`; type `query`: string |

### 2.13 `crawl.policies`

- In CONVENTIONS: yes
- Partition or message key as stated: `message key: host` (news-robots-checker)
- Schema names: `crawl.policies/v1` (news-robots-checker)
- Producers: 1; consumers: 5; mention only: 0

| Producer | Kinds or event types written | Refs |
|---|---|---|
| news-robots-checker | (not stated) | 6.2 L91-L117; 5.2 L61; 9 L144; 13.11 L175; +1 more |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| news-article-extractor | (all) | 6.1 L85 |
| news-feed-poller | (all) | 6.1 L88; 5.1 L48 |
| news-homepage-differ | (all) | 6.1 L93 |
| news-site-resolver | (all) | 5.1 L41; 6.1 L75; 2 L11; 13.1 L159; +1 more |
| news-sitemap-poller | (all) | 6.1 L100; 5.1 L49 |

Fields per PRD, exactly as written (`path`: JSON type of the example).

| PRD | Access | Fields |
|---|---|---|
| news-robots-checker | write | `schema`: string; `host`: string; `status`: string; `crawl_allowed`: boolean; `reason`: null; `access_mode`: string; `crawl_delay_seconds`: integer; `robots`: object; `robots.status`: string; `robots.http_status`: integer; `robots.fetched_at`: string; `robots.group`: string; `robots.sha256`: string; `robots.disallow`: array; `robots.disallow[]`: string; `robots.allow`: array; `robots.allow[]`: string; `robots.sitemaps`: array; `robots.sitemaps[]`: string; `usage_signals`: object; `usage_signals.search`: string; `usage_signals.ai_input`: string; `usage_signals.ai_train`: string; `rsl`: object; `rsl.found`: boolean; `payment`: object; `payment.http_402`: boolean; `payment.price`: null; `checked_at`: string; `expires_at`: string; `policy_version`: integer; `changed_fields`: array; `changed_fields[]`: string; `requested_by`: string; `kind`: string; `service`: string; `job_id`: string |
| news-site-resolver | read | `crawl_allowed`: ; `status`: ; `access mode`: ; `Sitemap: lines`: ; `Crawl-delay`:  |

### 2.14 `jobs.completed`

- In CONVENTIONS: **no** (added by a PRD)
- Partition or message key as stated: `source_id` (comment-decay-scheduler)
- Schema names: `jobs.completed/v1` (backfill-orchestrator, comment-decay-scheduler, x-full-archive-search, x-replies-fetcher, x-user-timeline-poller, yt-comments-fetcher, yt-replies-fetcher)
- Producers: 7; consumers: 4; mention only: 0

| Producer | Kinds or event types written | Refs |
|---|---|---|
| x-full-archive-search | backfill, keyword_history, replies | 5.1 L41; 5.2 L57; 6.2 L128; 12 L168; +3 more |
| x-replies-fetcher | comments | 4 L35; 5.1 L41; 5.2 L53-L55; 5.2 L62; +4 more |
| x-user-timeline-poller | rotation, reconciliation, ops_force | 5.2 L61; 6.2 L134; 12 L172; 13.10 L187 |
| yt-comments-fetcher | job report | 4 L34; 5.1 L40; 5.2 L53; 5.2 L60; +5 more |
| yt-replies-fetcher | job report | 5.1 L42; 5.2 L50; 5.2 L57; 8 L143; +3 more |
| yt-uploads-reconciler | job report | 3 L25; 5.1 L53; 5.2 L66; 6.2 L136; +3 more |
| yt-video-details-fetcher | job completion | 5.2 L63; 6.2 L155; 9 L180; 13.3 L203 |

| Consumer | Kinds or event types read | Refs |
|---|---|---|
| backfill-orchestrator | backfill completion | 5.2 L59; 5.4 L89-L92; 6.1 L100 |
| comment-decay-scheduler | completion events (comments, replies, metrics) | 5.1 L42; 5.2 L77; 5.4 L124-L127; 6.1 L135; +1 more |
| x-filtered-stream | (all) | 5.2 L71; 6.1 L107 |
| x-full-archive-search | (all) | 5.2 L52; 6.1 L102 |

Common written fields (each path found in at least half of the 6 producer examples, with its usual JSON type):

`cost_units`: null, `new_count`: null, `pages`: null, `seen_count`: null, `status`: null

Fields per PRD, exactly as written. For a producer, `common` stands for the set above, `+` lists the fields it adds, `−` the common fields its example lacks, and `type` a common field it gives another JSON type (null counts as compatible). A producer whose example has no `envelope` wrapper is marked **flat** and listed in full. 

| PRD | Access | Fields |
|---|---|---|
| backfill-orchestrator | read | `schema`: string; `job_id`: string; `service`: string; `source_id`: string; `kind`: string; `status`: string; `attempt`: integer; `finished_at`: string; `report`: object; `report.new_count`: integer; `report.pages`: integer; `report.cost_units`: integer; `report.oldest_item_at`: string; `report.capped`: boolean; `report.capped_reason`: null |
| comment-decay-scheduler | read | `schema`: string; `job_id`: string; `service`: string; `source_id`: string; `kind`: string; `series_step`: string; `status`: string; `attempt`: integer; `finished_at`: string; `report`: object; `report.new_count`: integer; `report.seen_count`: integer; `report.pages`: integer; `report.cost_units`: integer; `report.reply_candidates`: array |
| x-full-archive-search | read | `new_count`:  |
| x-full-archive-search | write | common; + `post_ref`: , `series_step`: , `end_time`:  |
| x-replies-fetcher | write | common; + `paid_user_reads`: , `capped`: , `window_partial`:  |
| x-user-timeline-poller | write | common; − `status` |
| yt-comments-fetcher | write | common; + `reply_candidates`:  |
| yt-replies-fetcher | write | common; + `stored_count`: , `complete`:  |
| yt-uploads-reconciler | write | common; − `status` |

### 2.15 `news.dedup`

- In CONVENTIONS: **no** (added by a PRD)
- Partition or message key as stated: `story_id` (news-dedup)
- Schema names: `news.dedup/v1` (news-dedup)
- Producers: 1; consumers: 0; mention only: 0

| Producer | Kinds or event types written | Refs |
|---|---|---|
| news-dedup | verdict, story_update | 3 L21; 5.2 L57-L58; 6.2 L84-L104; 14.1 L167 |

Fields per PRD, exactly as written (`path`: JSON type of the example).

| PRD | Access | Fields |
|---|---|---|
| news-dedup | write | `schema`: string; `type`: string; `idempotency_key`: string; `story_id`: string; `is_origin`: boolean; `duplicate_of`: string; `origin_source_id`: string; `origin_time`: string; `cluster_size`: integer; `rank_in_cluster`: integer; `matched_by`: string; `hamming_distance`: integer; `title_overlap`: number; `source_id`: string; `dedup_version`: integer; `decided_at`: string; `service`: string; `previous_story_id`: ; `previous_origin`:  |

### 2.16 `raw.replay`

- In CONVENTIONS: **no** (added by a PRD)
- Partition or message key as stated: `source_id` (raw-archiver)
- Producers: 1; consumers: 0; mention only: 1

| Producer | Kinds or event types written | Refs |
|---|---|---|
| raw-archiver | replayed raw record | 3 L22; 4 L35-L36; 5.3 L71; 6.2 L96-L115; +1 more |

Mentioned without reading or writing: deletion-propagator.

Fields per PRD, exactly as written (`path`: JSON type of the example).

| PRD | Access | Fields |
|---|---|---|
| raw-archiver | write | `envelope`: object; `envelope.platform`: string; `envelope.kind`: string; `envelope.route`: string; `envelope.vendor`: null; `envelope.service`: string; `envelope.source_id`: string; `envelope.platform_id`: string; `envelope.idempotency_key`: string; `envelope.fetched_at`: string; `envelope.retention_class`: string; `envelope.raw_ref`: string; `payload`: object; `replay`: object; `replay.run_id`: string; `replay.target`: string; `replay.reason`: string; `replay.requested_by`: string; `replay.planned`: integer; `replay.seq`: integer |

## 3. By job queue

Every queue a PRD consumes from or produces into: `jobs.<service>` queues, priority lanes and named dead letters. A queue's consumer is the service named in it; producers are every PRD that says it writes there. Kinds are listed as each PRD writes them.

### 3.1 Job queues

| Queue | Consumer and kinds it handles | Producers and kinds they emit | Refs |
|---|---|---|---|
| `jobs.<comment service>` | (no PRD consumes it) | comment-decay-scheduler: comments, replies, health | comment-decay-scheduler 1 L9; 3 L21; +5 more |
| `jobs.<resolver>` | (no PRD consumes it) | poster-resolver: resolve | poster-resolver 3 L23; 4 L37; +3 more |
| `jobs.<service>` | (no PRD consumes it) | backfill-orchestrator: backfill | backfill-orchestrator 2 L15; 3 L22; +3 more |
| `jobs.aggregator` | aggregator: recompute | deletion-propagator: recompute | aggregator 4 L31; 5.1 L37; +2 more; deletion-propagator 3 L23; 5.2 L51; +2 more |
| `jobs.analysis-entities` | analysis-entities: rerun | analysis-entities: (kinds not stated) | analysis-entities 5.1 L46; 6.1 L86; analysis-entities 5.1 L42; 6.1 L86 |
| `jobs.analysis-entities.priority` | analysis-entities: (kinds not stated) | analysis-entities: (kinds not stated) | analysis-entities 5.1 L42; 6.1 L86; analysis-entities 5.1 L42; 6.1 L86 |
| `jobs.analysis-media` | analysis-media: rerun | analysis-media: (kinds not stated) | analysis-media 5.1 L47; 6.1 L83; analysis-media 5.1 L43; 6.1 L83 |
| `jobs.analysis-media.priority` | analysis-media: (kinds not stated) | analysis-media: (kinds not stated) | analysis-media 5.1 L43; 6.1 L83; analysis-media 5.1 L43; 6.1 L83 |
| `jobs.analysis-sentiment` | analysis-sentiment: analyze, rerun | analysis-sentiment: analyze | analysis-sentiment 5.1 L51; 6.1 L85; analysis-sentiment 5.1 L47; 6.1 L85 |
| `jobs.analysis-sentiment.priority` | analysis-sentiment: analyze | analysis-sentiment: analyze | analysis-sentiment 5.1 L47; 6.1 L85; analysis-sentiment 5.1 L47; 6.1 L85 |
| `jobs.analysis-topics` | analysis-topics: rerun | analysis-topics: (kinds not stated) | analysis-topics 5.1 L50; 6.1 L89; analysis-topics 5.1 L46; 6.1 L89 |
| `jobs.analysis-topics.priority` | analysis-topics: (kinds not stated) | analysis-topics: (kinds not stated) | analysis-topics 5.1 L46; 6.1 L89; analysis-topics 5.1 L46; 6.1 L89 |
| `jobs.fb-backfill` | fb-backfill: add, ops, client | backfill-orchestrator: backfill | fb-backfill 3 L19; 3 L22; +7 more; backfill-orchestrator 13.1 L149 |
| `jobs.fb-client-webhook-receiver` | fb-client-webhook-receiver: (kinds not stated) | fb-client-webhook-receiver: (kinds not stated) | fb-client-webhook-receiver 5.1 L40; 5.2 L56; +1 more; fb-client-webhook-receiver 5.1 L40; 5.2 L54; +3 more |
| `jobs.fb-group-comments-fetcher` | fb-group-comments-fetcher: comments, replies, ops_force | (no PRD produces into it) | fb-group-comments-fetcher 3 L19; 5.1 L40; +5 more |
| `jobs.fb-group-posts-poller` | fb-group-posts-poller: rotation, backfill, ops_force | fb-group-posts-poller: rotation | fb-group-posts-poller 3 L19; 5.1 L40; +3 more; fb-group-posts-poller 5.1 L40; 5.1 L44; +2 more |
| `jobs.fb-keyword-search` | fb-keyword-search: rotation, backfill, ops_force | fb-keyword-search: rotation | fb-keyword-search 3 L19; 4 L33; +4 more; fb-keyword-search 5.1 L40; 5.1 L42; +2 more |
| `jobs.fb-page-feed-poller` | fb-page-feed-poller: rotation, reconciliation, ops_force | fb-page-feed-poller: rotation, reconciliation | fb-page-feed-poller 3 L19; 5.1 L40; +3 more; fb-page-feed-poller 5.1 L40; 5.1 L42; +2 more |
| `jobs.fb-page-resolver` | fb-page-resolver: resolve, rotation, ops_force | fb-page-resolver: rotation | fb-page-resolver 4 L35; 5.1 L42; +4 more; fb-page-resolver 5.1 L42; 5.1 L46; +1 more |
| `jobs.fb-page-search` | fb-page-search: seed, weekly | fb-page-search: weekly | fb-page-search 5.1 L40; 5.2 L50; +2 more; fb-page-search 5.1 L40; 5.1 L42; +1 more |
| `jobs.fb-post-comments-fetcher` | fb-post-comments-fetcher: comments, ops_force | (no PRD produces into it) | fb-post-comments-fetcher 3 L19; 4 L35; +5 more |
| `jobs.fb-reactions-fetcher` | fb-reactions-fetcher: refresh_24h, refresh_7d, refresh_client | comment-decay-scheduler: metrics | fb-reactions-fetcher 3 L20; 3 L21; +6 more; comment-decay-scheduler 5.1 L68; 5.3 L120; +1 more |
| `jobs.ig-account-media-poller` | ig-account-media-poller: rotation, reconciliation, backfill, metrics, ops_force | comment-decay-scheduler: metrics<br>ig-account-media-poller: rotation, reconciliation | ig-account-media-poller 3 L19; 3 L21; +10 more; comment-decay-scheduler 4 L35; 5.1 L68; +1 more; ig-account-media-poller 3 L19; 5.1 L42; +5 more |
| `jobs.ig-account-resolver` | ig-account-resolver: resolve, rotation | ig-account-resolver: rotation<br>poster-resolver: resolve | ig-account-resolver 5.1 L42; 5.1 L46; +3 more; ig-account-resolver 5.1 L42; 5.1 L44; +4 more; poster-resolver 13.1 L140 |
| `jobs.ig-comments-fetcher` | ig-comments-fetcher: comments, ops_force | (no PRD produces into it) | ig-comments-fetcher 5.1 L41; 5.1 L53; +3 more |
| `jobs.ig-hashtag-search` | ig-hashtag-search: (kinds not stated) | (no PRD produces into it) | ig-hashtag-search 5.1 L45; 5.1 L55; +5 more |
| `jobs.ig-keyword-search` | ig-keyword-search: rotation, backfill, ops_force | ig-keyword-search: rotation | ig-keyword-search 3 L19; 3 L21; +5 more; ig-keyword-search 5.1 L41; 5.1 L43; +4 more |
| `jobs.ig-mentions-fetcher` | ig-mentions-fetcher: rotation, reconciliation, backfill, ops_force | ig-mentions-fetcher: rotation<br>ig-webhook-receiver: reconciliation, ops_force | ig-mentions-fetcher 3 L19; 3 L21; +8 more; ig-mentions-fetcher 5.1 L41; 5.1 L43; +5 more; ig-webhook-receiver 2 L13; 3 L21; +5 more |
| `jobs.ig-own-comments-fetcher` | ig-own-comments-fetcher: comments, replies, reconciliation, ops_force | ig-webhook-receiver: reconciliation, ops_force | ig-own-comments-fetcher 3 L19; 4 L34; +6 more; ig-webhook-receiver 2 L13; 3 L21; +4 more |
| `jobs.ig-webhook-receiver` | ig-webhook-receiver: push | ig-webhook-receiver: push | ig-webhook-receiver 5.2 L56; 5.2 L59; +2 more; ig-webhook-receiver 3 L19; 5.2 L55; +2 more |
| `jobs.keyword-matcher` | keyword-matcher: rematch, candidate_retry | keyword-matcher: candidate_retry | keyword-matcher 3 L23; 4 L34; +4 more; keyword-matcher 5.3 L74; 6.2 L95 |
| `jobs.li-client-posts-poller` | li-client-posts-poller: rotation, reconciliation, backfill, ops_force | li-client-posts-poller (own scheduler, as its PRD says): rotation, reconciliation<br>mentioned by: li-notification-receiver | li-client-posts-poller 5.1 L40; 5.1 L48; +5 more; li-client-posts-poller 5.1 L40; 5.1 L48; +5 more |
| `jobs.li-company-posts-poller` | li-company-posts-poller: rotation, backfill, ops_force | li-company-posts-poller (own scheduler, as its PRD says): rotation | li-company-posts-poller 3 L19; 3 L21; +5 more; li-company-posts-poller 3 L19; 3 L21; +5 more |
| `jobs.li-org-resolver` | li-org-resolver: refresh | (no PRD produces into it) | li-org-resolver 5.1 L44; 6.1 L75; +1 more |
| `jobs.li-own-comments-fetcher` | li-own-comments-fetcher: comments | (no PRD produces into it)<br>mentioned by: li-notification-receiver | li-own-comments-fetcher 3 L19; 5.1 L38; +6 more |
| `jobs.li-post-comments-fetcher` | li-post-comments-fetcher: comments | (no PRD produces into it)<br>mentioned by: li-post-search | li-post-comments-fetcher 3 L19; 5.1 L40; +5 more |
| `jobs.li-post-search` | li-post-search: backfill | "the scheduler" (li-post-search 5.1 L44; owner not stated): (kinds not stated) | li-post-search 5.1 L44; 5.1 L48; +3 more; li-post-search 5.1 L44; 5.1 L48; +3 more |
| `jobs.news-comments-fetcher` | news-comments-fetcher: comments, ops_force | (no PRD produces into it) | news-comments-fetcher 3 L19; 5.1 L41; +3 more |
| `jobs.news-feed-poller` | news-feed-poller: rotation, ops_force | news-feed-poller (own scheduler, as its PRD says): rotation | news-feed-poller 3 L19; 5.1 L40; +2 more; news-feed-poller 3 L19; 5.1 L40; +2 more |
| `jobs.news-homepage-differ` | news-homepage-differ: rotation, ops_force | news-homepage-differ (own scheduler, as its PRD says): rotation | news-homepage-differ 5.1 L41; 5.2 L53; +1 more; news-homepage-differ 5.1 L41; 5.2 L53; +1 more |
| `jobs.news-robots-checker` | news-robots-checker: first_check, refresh, recheck, ops_force | news-article-extractor: recheck<br>news-feed-poller: recheck<br>news-homepage-differ: recheck<br>news-site-resolver: (kinds not stated)<br>news-sitemap-poller: recheck<br>news-robots-checker (own scheduler, as its PRD says): refresh | news-robots-checker 3 L19; 5.1 L41; +3 more; news-article-extractor 3 L23; 5.2 L54; +6 more; news-feed-poller 3 L22; 6.2 L115; +2 more; news-homepage-differ 3 L22; 6.2 L118; +2 more; news-site-resolver 5.1 L41; 6.2 L79; +1 more; news-sitemap-poller 3 L23; 6.2 L127; +2 more; news-robots-checker 3 L19; 5.1 L41; +3 more |
| `jobs.news-site-resolver` | news-site-resolver: resolve, refresh | news-comments-fetcher: refresh<br>news-feed-poller: refresh<br>news-homepage-differ: refresh<br>news-sitemap-poller: refresh<br>news-site-resolver (own scheduler, as its PRD says): refresh | news-site-resolver 5.1 L38-L40; 6.1 L75; +2 more; news-comments-fetcher 8 L139; news-feed-poller 3 L21; 5.2 L59; +4 more; news-homepage-differ 3 L22; 5.2 L60; +3 more; news-sitemap-poller 3 L23; 6.2 L127; +4 more; news-site-resolver 5.1 L38-L40; 6.1 L75; +2 more |
| `jobs.news-sitemap-poller` | news-sitemap-poller: rotation, backfill, ops_force | news-sitemap-poller (own scheduler, as its PRD says): rotation | news-sitemap-poller 3 L21; 5.1 L41; +3 more; news-sitemap-poller 3 L21; 5.1 L41; +3 more |
| `jobs.normalize-item` | normalize-item: replay, lang_rescore | normalize-item: lang_rescore | normalize-item 5.1 L45; 6.1 L86; +2 more; normalize-item 8 L133; 13.9 L172 |
| `jobs.poster-resolver` | poster-resolver: resolved, unresolvable, manual_candidate | registry-writer: manual_candidate | poster-resolver 4 L37; 5.1 L46; +3 more; registry-writer 3 L25; 4 L38; +1 more |
| `jobs.tg-bot-channel-receiver` | tg-bot-channel-receiver: reconciliation, ops_force | tg-bot-channel-receiver: reconciliation | tg-bot-channel-receiver 5.1 L44; 6.1 L109; +1 more; tg-bot-channel-receiver 5.1 L44; 5.1 L48; +2 more |
| `jobs.tg-channel-posts-poller` | tg-channel-posts-poller: rotation, reconciliation, backfill, metrics, ops_force | tg-channel-posts-poller: rotation, reconciliation | tg-channel-posts-poller 3 L19; 3 L21; +6 more; tg-channel-posts-poller 5.1 L42; 5.1 L44; +5 more |
| `jobs.tg-channel-resolver` | tg-channel-resolver: refresh | tg-channel-resolver: refresh | tg-channel-resolver 2 L15; 5.1 L44; +5 more; tg-channel-resolver 3 L22; 5.1 L44; +2 more |
| `jobs.tg-discussion-receiver` | tg-discussion-receiver: reconciliation, ops_force | tg-discussion-receiver: reconciliation | tg-discussion-receiver 5.1 L47; 6.1 L110; +1 more; tg-discussion-receiver 5.1 L47; 5.1 L49; +1 more |
| `jobs.tg-message-search` | tg-message-search: (kinds not stated) | tg-message-search: (kinds not stated) | tg-message-search 5.1 L43; 5.1 L44; +3 more; tg-message-search 5.1 L43; 5.1 L45; +2 more |
| `jobs.tt-client-videos-fetcher` | tt-client-videos-fetcher: rotation, backfill, ops_force | tt-client-videos-fetcher (own scheduler, as its PRD says): rotation | tt-client-videos-fetcher 4 L34; 5.1 L41; +6 more; tt-client-videos-fetcher 4 L34; 5.1 L41; +6 more |
| `jobs.tt-hashtag-feed-poller` | tt-hashtag-feed-poller: (kinds not stated) | tt-hashtag-feed-poller (own scheduler, as its PRD says): (kinds not stated) | tt-hashtag-feed-poller 5.1 L44; 5.1 L46; +7 more; tt-hashtag-feed-poller 5.1 L44; 5.1 L46; +7 more |
| `jobs.tt-keyword-search` | tt-keyword-search: (kinds not stated) | tt-keyword-search (own scheduler, as its PRD says): (kinds not stated) | tt-keyword-search 5.1 L42; 5.1 L44; +5 more; tt-keyword-search 5.1 L42; 5.1 L44; +5 more |
| `jobs.tt-profile-videos-poller` | tt-profile-videos-poller: rotation, reconciliation, backfill, ops_force | tt-profile-videos-poller (own scheduler, as its PRD says): rotation, reconciliation | tt-profile-videos-poller 3 L19; 3 L20; +8 more; tt-profile-videos-poller 3 L19; 3 L20; +8 more |
| `jobs.tt-user-resolver` | tt-user-resolver: resolve | (no PRD produces into it) | tt-user-resolver 3 L19; 4 L35; +5 more |
| `jobs.tt-video-comments-fetcher` | tt-video-comments-fetcher: comments, replies | (no PRD produces into it) | tt-video-comments-fetcher 3 L19; 5.1 L41; +4 more |
| `jobs.tt-video-stats-refresher` | tt-video-stats-refresher: metrics, ops_force | comment-decay-scheduler: metrics | tt-video-stats-refresher 3 L19; 4 L35; +3 more; comment-decay-scheduler 5.1 L68; 6.2 L138 |
| `jobs.web-commoncrawl-scanner` | web-commoncrawl-scanner: rotation, ops_force | web-commoncrawl-scanner (own scheduler, as its PRD says): rotation | web-commoncrawl-scanner 5.1 L41; 5.1 L42; +4 more; web-commoncrawl-scanner 5.1 L41; 5.1 L42; +4 more |
| `jobs.web-gdelt-poller` | web-gdelt-poller: rotation | web-gdelt-poller (own scheduler, as its PRD says): rotation | web-gdelt-poller 5.1 L42; 6.1 L86; +4 more; web-gdelt-poller 5.1 L42; 6.1 L86; +4 more |
| `jobs.web-search-mojeek` | web-search-mojeek: rotation | web-search-mojeek (own scheduler, as its PRD says): rotation | web-search-mojeek 5.1 L43; 6.1 L83; +2 more; web-search-mojeek 5.1 L43; 6.1 L83; +2 more |
| `jobs.web-search-perplexity` | web-search-perplexity: rotation, site_search | web-search-perplexity (own scheduler, as its PRD says): rotation | web-search-perplexity 5.1 L42; 6.1 L85; +7 more; web-search-perplexity 5.1 L42; 6.1 L85; +7 more |
| `jobs.x-compliance-sync` | x-compliance-sync: ops_force | (no PRD produces into it) | x-compliance-sync 5.1 L45; 6.1 L93; +1 more |
| `jobs.x-full-archive-search` | x-full-archive-search: backfill, keyword_history, replies | x-filtered-stream: (kinds not stated)<br>x-recent-search: keyword_history | x-full-archive-search 3 L19-L21; 5.1 L39; +2 more; x-filtered-stream 5.2 L70; 6.2 L145; x-recent-search 5.1 L45; 5.1 L49; +1 more |
| `jobs.x-recent-search` | x-recent-search: rotation, first_run, gap_backfill, ops_force | x-filtered-stream: reconciliation<br>x-recent-search (own scheduler, as its PRD says): rotation, first_run, gap_backfill | x-recent-search 3 L19-L22; 4 L32; +3 more; x-filtered-stream 4 L32; 5.1 L44; +4 more; x-recent-search 3 L19-L22; 4 L32; +3 more |
| `jobs.x-replies-fetcher` | x-replies-fetcher: comments | (no PRD produces into it) | x-replies-fetcher 3 L19; 5.1 L41; +1 more |
| `jobs.x-user-resolver` | x-user-resolver: resolve, rotation, ops_force | x-user-resolver (own scheduler, as its PRD says): rotation | x-user-resolver 3 L19; 4 L32-L34; +3 more; x-user-resolver 3 L19; 4 L32-L34; +3 more |
| `jobs.x-user-timeline-poller` | x-user-timeline-poller: rotation, reconciliation, ops_force | x-user-timeline-poller (own scheduler, as its PRD says): rotation, reconciliation | x-user-timeline-poller 3 L19; 4 L31; +3 more; x-user-timeline-poller 3 L19; 4 L31; +3 more |
| `jobs.yt-channel-resolver` | yt-channel-resolver: resolve, rotation, ops_force | yt-channel-resolver: rotation<br>yt-web-search-bridge: resolve | yt-channel-resolver 4 L37; 5.1 L44; +3 more; yt-channel-resolver 5.1 L50; yt-web-search-bridge 2 L13; 3 L23; +3 more |
| `jobs.yt-comments-fetcher` | yt-comments-fetcher: comments | yt-text-purger: refresh | yt-comments-fetcher 3 L19; 5.1 L40; +1 more; yt-text-purger 3 L20; 5.3 L96-L102; +3 more |
| `jobs.yt-pubsub-receiver` | yt-pubsub-receiver: (kinds not stated) | yt-pubsub-receiver: (kinds not stated) | yt-pubsub-receiver 5.1 L38; 5.2 L55; +1 more; yt-pubsub-receiver 5.1 L38; 5.2 L54 |
| `jobs.yt-replies-fetcher` | yt-replies-fetcher: replies | yt-text-purger: refresh<br>mentioned by: yt-comments-fetcher | yt-replies-fetcher 3 L19; 5.1 L38; +2 more; yt-text-purger 3 L20; 5.3 L99; +3 more |
| `jobs.yt-text-purger` | yt-text-purger: retention_sweep, ops_force | retention-purger: retention_sweep | yt-text-purger 4 L33; 5.1 L44; +2 more; retention-purger 4 L37; 5.3 L63; +2 more |
| `jobs.yt-uploads-reconciler` | yt-uploads-reconciler: reconciliation, backfill, ops_force | yt-uploads-reconciler: reconciliation | yt-uploads-reconciler 3 L21; 5.1 L43; +4 more; yt-uploads-reconciler 5.1 L43; 5.1 L47; +1 more |
| `jobs.yt-video-details-fetcher` | yt-video-details-fetcher: first_sight, metrics, ops_force | comment-decay-scheduler: metrics<br>yt-keyword-search: first_sight<br>yt-pubsub-receiver: first_sight<br>yt-text-purger: refresh<br>yt-uploads-reconciler: first_sight<br>yt-web-search-bridge: first_sight | yt-video-details-fetcher 3 L19-L21; 5.1 L42-L46; +2 more; comment-decay-scheduler 5.1 L68; 6.2 L138; yt-keyword-search 2 L15; 3 L25; +4 more; yt-pubsub-receiver 3 L21; 5.2 L55; +4 more; yt-text-purger 3 L20; 5.3 L100; +4 more; yt-uploads-reconciler 3 L24; 5.2 L64; +3 more; yt-web-search-bridge 2 L13; 3 L23; +5 more |
| `normalize-item job (queue name not written)` | (no PRD consumes it) | (no PRD produces into it)<br>mentioned by: lang-dialect-id |  |

### 3.2 Who the consumers say produces their jobs

| Queue | Consumer | Producers it names |
|---|---|---|
| `jobs.aggregator` | aggregator | ops |
| `jobs.analysis-entities` | analysis-entities | analysis-entities intake stage; re-run requests (new model version) |
| `jobs.analysis-entities.priority` | analysis-entities | analysis-entities intake stage |
| `jobs.analysis-media` | analysis-media | analysis-media intake stage; ops (rerun) |
| `jobs.analysis-media.priority` | analysis-media | analysis-media intake stage |
| `jobs.analysis-sentiment` | analysis-sentiment | analysis-sentiment intake stage (analyze); ops (rerun) |
| `jobs.analysis-sentiment.priority` | analysis-sentiment | analysis-sentiment intake stage |
| `jobs.analysis-topics` | analysis-topics | analysis-topics intake stage; rerun requests (new model or taxonomy version; a client adding a topic re-runs only that client's window) |
| `jobs.analysis-topics.priority` | analysis-topics | analysis-topics intake stage |
| `jobs.fb-backfill` | fb-backfill | backfill-orchestrator (reason = add, on source.events added); on-demand job (reason = ops \| client): producer not stated |
| `jobs.fb-client-webhook-receiver` | fb-client-webhook-receiver | fb-client-webhook-receiver (HTTP handler) |
| `jobs.fb-group-comments-fetcher` | fb-group-comments-fetcher | comment-decay-scheduler (only) |
| `jobs.fb-group-posts-poller` | fb-group-posts-poller | fb-group-posts-poller (own rotation scheduler) for rotation; backfill-orchestrator (only producer of backfill jobs); ops_force: producer not stated |
| `jobs.fb-keyword-search` | fb-keyword-search | fb-keyword-search (own rotation scheduler) for rotation; backfill-orchestrator (only producer of backfill jobs); ops_force: producer not stated (ops can force a search) |
| `jobs.fb-page-feed-poller` | fb-page-feed-poller | fb-page-feed-poller (own rotation scheduler, leader elected through a Postgres advisory lock) |
| `jobs.fb-page-resolver` | fb-page-resolver | poster-resolver (resolve); fb-page-resolver own refresh loop (rotation); ops_force: producer not stated (ops can force a resolution) |
| `jobs.fb-page-search` | fb-page-search | registry-writer (reason = seed, on a keywords change: created or variants changed, for a client with Facebook in scope); fb-page-search own weekly rediscovery scheduler (reason = weekly) |
| `jobs.fb-post-comments-fetcher` | fb-post-comments-fetcher | comment-decay-scheduler (only) |
| `jobs.fb-reactions-fetcher` | fb-reactions-fetcher | comment-decay-scheduler (refresh_24h, refresh_7d); refresh_client: client request; producer not stated |
| `jobs.ig-account-media-poller` | ig-account-media-poller | ig-account-media-poller (own rotation scheduler: rotation, reconciliation); backfill-orchestrator (backfill); comment-decay-scheduler (metrics at +24 h and +7 d after a post is first seen); ops (force a poll of one account; mechanism not stated) |
| `jobs.ig-account-resolver` | ig-account-resolver | poster-resolver (resolve); ig-account-resolver (own refresh scheduler: rotation) |
| `jobs.ig-comments-fetcher` | ig-comments-fetcher | comment-decay-scheduler (only) |
| `jobs.ig-hashtag-search` | ig-hashtag-search | the shared scheduler (when a hashtag source's next_poll_at is due); backfill-orchestrator (when a hashtag is added) |
| `jobs.ig-keyword-search` | ig-keyword-search | ig-keyword-search (own rotation scheduler: rotation); backfill-orchestrator (backfill) |
| `jobs.ig-mentions-fetcher` | ig-mentions-fetcher | ig-mentions-fetcher (own rotation scheduler: rotation); ig-webhook-receiver's scheduler (daily reconciliation); backfill-orchestrator (backfill); ops (force a poll of one account; mechanism not stated) |
| `jobs.ig-own-comments-fetcher` | ig-own-comments-fetcher | comment-decay-scheduler (comments, replies; the only emitter of comment and reply jobs); ig-webhook-receiver's scheduler (reconciliation, once a day per owned account); a client or ops (ops_force refresh of one post beyond day 30; mechanism not stated) |
| `jobs.ig-webhook-receiver` | ig-webhook-receiver | ig-webhook-receiver (front replicas) |
| `jobs.keyword-matcher` | keyword-matcher | ops (rematch); keyword change (rematch for a new or edited keyword; creator not named); keyword-matcher (candidate_retry) |
| `jobs.li-client-posts-poller` | li-client-posts-poller | li-client-posts-poller (own rotation scheduler, one leader replica via Postgres advisory lock); backfill-orchestrator (backfill jobs); ops (ops_force, forced poll of one page) |
| `jobs.li-company-posts-poller` | li-company-posts-poller | li-company-posts-poller (own rotation scheduler, one leader replica via Postgres advisory lock); backfill-orchestrator (one-off backfill jobs); ops (force a poll of one page) |
| `jobs.li-org-resolver` | li-org-resolver | poster-resolver (origin discovery); registry-writer (origin seed, on client onboarding); ops (origin manual); qualifier (kind: refresh, when a dormant source gets a new hit, at the 90-day decay review, or when a source retires at 180 days) |
| `jobs.li-own-comments-fetcher` | li-own-comments-fetcher | comment-decay-scheduler (series steps, daily reconciliation, hot-post extras, extension steps, client-requested refreshes); backfill-orchestrator (one-off comments job per post of a newly added page, last 30 days) |
| `jobs.li-post-comments-fetcher` | li-post-comments-fetcher | comment-decay-scheduler (series steps, extension steps, hot-post extras, client-requested refreshes); backfill-orchestrator (one-off comments job per post of a newly added page, last 30 days) |
| `jobs.li-post-search` | li-post-search | the scheduler (keeps next_poll_at on the rule; owner not stated); backfill-orchestrator (one kind: backfill job per new rule) |
| `jobs.news-comments-fetcher` | news-comments-fetcher | comment-decay-scheduler (only; this service has no scheduler of its own) |
| `jobs.news-feed-poller` | news-feed-poller | news-feed-poller's own rotation scheduler (one leader replica through a Postgres advisory lock) |
| `jobs.news-homepage-differ` | news-homepage-differ | news-homepage-differ's own rotation scheduler (one leader replica through a Postgres advisory lock) |
| `jobs.news-robots-checker` | news-robots-checker | news-site-resolver (first_check); news-robots-checker's own daily scheduler (refresh; one leader replica through a Postgres advisory lock); any news service after a 4xx (recheck); ops (ops_force: 'can force a re-check', 4 L34) |
| `jobs.news-site-resolver` | news-site-resolver | search-hit-router; web-commoncrawl-scanner; web-gdelt-poller; the seed-list flow; the qualifier; ops (n8n flow) (3 L17); news-site-resolver's own 30-day refresh ticker (one leader instance, 9 L137); refresh 'at once when source-health-canary flips it to degraded or a poller reports a feed or sitemap 404 or 410' (5.1 L40; emitter not named) |
| `jobs.news-sitemap-poller` | news-sitemap-poller | news-sitemap-poller's own rotation scheduler (one leader replica through a Postgres advisory lock); backfill-orchestrator (backfill jobs only) |
| `jobs.normalize-item` | normalize-item | ops (replay); normalize-item itself (lang_rescore, 8) |
| `jobs.poster-resolver` | poster-resolver | the eight per-source resolvers (answers); registry-writer (manual_candidate) |
| `jobs.tg-bot-channel-receiver` | tg-bot-channel-receiver | tg-bot-channel-receiver leader replica (Postgres advisory lock) for reconciliation; ops_force producer not stated |
| `jobs.tg-channel-posts-poller` | tg-channel-posts-poller | tg-channel-posts-poller rotation scheduler (rotation, reconciliation); backfill-orchestrator (backfill); comment-decay-scheduler (metrics: the +24 h views refresh for Tier 1 posts); ops (ops_force: 'can force a read of one channel'; mechanism not stated) |
| `jobs.tg-channel-resolver` | tg-channel-resolver | poster-resolver (discovery jobs); client adds (producer service not named); ops adds (producer service not named); tg-channel-resolver scheduler (refresh) |
| `jobs.tg-discussion-receiver` | tg-discussion-receiver | tg-discussion-receiver leader replica (Postgres advisory lock) for reconciliation; ops_force producer not stated |
| `jobs.tg-message-search` | tg-message-search | tg-message-search scheduler |
| `jobs.tt-client-videos-fetcher` | tt-client-videos-fetcher | tt-client-videos-fetcher (own rotation scheduler, one leader replica via Postgres advisory lock) for rotation; backfill-orchestrator for kind = backfill; ops ('can force a poll of one account'; emitter not named) for ops_force |
| `jobs.tt-hashtag-feed-poller` | tt-hashtag-feed-poller | tt-hashtag-feed-poller (own scheduler; one leader runs the scheduler loop) |
| `jobs.tt-keyword-search` | tt-keyword-search | tt-keyword-search (own scheduler, leader replica) |
| `jobs.tt-profile-videos-poller` | tt-profile-videos-poller | tt-profile-videos-poller (own rotation scheduler, one leader replica via Postgres advisory lock) for rotation and reconciliation; backfill-orchestrator for kind = backfill; ops ('can force a poll of one creator'; emitter not named) for ops_force |
| `jobs.tt-user-resolver` | tt-user-resolver | poster-resolver |
| `jobs.tt-video-comments-fetcher` | tt-video-comments-fetcher | comment-decay-scheduler (only emitter) |
| `jobs.tt-video-stats-refresher` | tt-video-stats-refresher | comment-decay-scheduler ('emitted only by comment-decay-scheduler') for metrics; ops ('can force an observation of one video (`ops_force`)'; emitter not named) |
| `jobs.web-commoncrawl-scanner` | web-commoncrawl-scanner | web-commoncrawl-scanner (own leader-elected scheduler: a daily check of the published-crawl list starts one rotation job per new crawl id); ops (ops_force) |
| `jobs.web-gdelt-poller` | web-gdelt-poller | web-gdelt-poller (own rotation scheduler: leader replica, Postgres advisory lock) |
| `jobs.web-search-mojeek` | web-search-mojeek | web-search-mojeek (own rotation scheduler: leader replica, Postgres advisory lock) |
| `jobs.web-search-perplexity` | web-search-perplexity | web-search-perplexity (own rotation scheduler: leader replica, Postgres advisory lock); yt-web-search-bridge (site_search) |
| `jobs.x-compliance-sync` | x-compliance-sync | ops (after a request from X, before a government review, or after an incident) |
| `jobs.x-full-archive-search` | x-full-archive-search | backfill-orchestrator (backfill for each X account added with backfill_status = pending; keyword_history on a client request); comment-decay-scheduler (replies; 'the only emitter of reply jobs', when a client asks for replies of a post older than 7 days) |
| `jobs.x-recent-search` | x-recent-search | x-recent-search (own rotation scheduler: one leader replica, Postgres advisory lock); gap_backfill 'for x-filtered-stream' (producer not named in this PRD); ops ('it can force one rule from the control plane') |
| `jobs.x-replies-fetcher` | x-replies-fetcher | comment-decay-scheduler (the only emitter) |
| `jobs.x-user-resolver` | x-user-resolver | poster-resolver (resolve, after inserting the candidate's poster_profiles row with status = resolving); x-user-resolver (own refresh loop: rotation); ops (ops_force) |
| `jobs.x-user-timeline-poller` | x-user-timeline-poller | x-user-timeline-poller (own rotation scheduler: one leader replica under a Postgres advisory lock); ops (ops_force) |
| `jobs.yt-channel-resolver` | yt-channel-resolver | poster-resolver (resolve); yt-channel-resolver (own leader-elected refresh loop: rotation); ops (ops_force, bypasses the cache) |
| `jobs.yt-comments-fetcher` | yt-comments-fetcher | comment-decay-scheduler (only emitter) |
| `jobs.yt-pubsub-receiver` | yt-pubsub-receiver | yt-pubsub-receiver (webhook handler) |
| `jobs.yt-replies-fetcher` | yt-replies-fetcher | comment-decay-scheduler (only emitter) |
| `jobs.yt-text-purger` | yt-text-purger | retention-purger (daily retention_sweep); ops (ops_force) |
| `jobs.yt-uploads-reconciler` | yt-uploads-reconciler | yt-uploads-reconciler (own rotation scheduler: reconciliation, incl. reason = lease_lapsed); backfill-orchestrator (backfill); ops (ops_force) |
| `jobs.yt-video-details-fetcher` | yt-video-details-fetcher | yt-pubsub-receiver (first_sight); yt-uploads-reconciler (first_sight; backfill ids carry series_step = backfill); yt-keyword-search (first_sight); yt-web-search-bridge (first_sight, treated identically); comment-decay-scheduler (metrics: series_step 24h, 7d or client); ops (ops_force) |

### 3.3 Job fields per PRD

Fields of job messages as each PRD writes them (consumed or produced). CONVENTIONS' job fields are `job_id` (ULID), `source_id`, `kind`, `due_at`, `attempt`, `post_ref`, `series_step`.

| Queue | PRD | Access | Fields |
|---|---|---|---|
| `jobs.<comment service>` | comment-decay-scheduler | produce | `job_id`: string [ULID: time part = due_at, random part = first 10 bytes of sha256(item_id \| lane \| series_step)]; `source_id`: string [uuid]; `kind`: string [comments \| replies \| metrics \| health]; `due_at`: string [ISO 8601]; `attempt`: integer; `post_ref`: object; `post_ref.item_id`: string [uuid]; `post_ref.platform`: string; `post_ref.platform_id`: string; `series_step`: string [+<n>h/+<n>d \| once \| hot:<n> \| refresh:<request_id>]; `profile`: string [fb_page \| fb_group \| ig_own \| ig_other \| tt \| x \| yt \| li_own \| li_other \| tg_own \| news]; `route`: string; `vendor`: null; `thread_ids`: array |
| `jobs.<resolver>` | poster-resolver | produce | `job_id`: string; `kind`: string; `candidate_key`: string; `platform`: string; `platform_id`: string; `handle`: string; `hit_url`: string; `origin`: string [discovery \| manual]; `reply_to`: string; `attempt`: integer; `sample_posts`: integer |
| `jobs.<service>` | backfill-orchestrator | produce | `job_id`: string [ULID with the random part from sha256(source_id \| backfill \| run_id)]; `source_id`: string [uuid]; `kind`: string; `due_at`: string [ISO 8601]; `attempt`: integer; `run_id`: string; `cap`: object; `cap.max_age_days`: integer; `cap.max_items`: integer; `route`: string; `vendor`: null |
| `jobs.aggregator` | aggregator | consume | `kind`: string; `date range`: ; `client`: ; `job_id`:  |
| `jobs.aggregator` | deletion-propagator | produce | `(source_id, hour) buckets`: ; `keyword ids`: ; `mode`:  |
| `jobs.analysis-entities` | analysis-entities | consume | `kind`: string |
| `jobs.analysis-media` | analysis-media | consume | `kind`: string; `task`:  |
| `jobs.analysis-sentiment` | analysis-sentiment | consume | `kind`: string [analyze \| rerun]; `date range`: ; `platform filter`:  |
| `jobs.analysis-topics` | analysis-topics | consume | `kind`: string |
| `jobs.fb-backfill` | fb-backfill | consume | `source_id`: ; `window_start`: ; `window_end`: ; `reason`:  [enum: add \| ops \| client]; `attempt`: ; `job_id`: string |
| `jobs.fb-client-webhook-receiver` | fb-client-webhook-receiver | produce | `source_id`: ; `object`: string; `entry`: array; `entry[].id`: string; `entry[].time`: integer; `entry[].changes`: array; `entry[].changes[].field`: string; `entry[].changes[].value`: object; `entry[].changes[].value.item`: string; `entry[].changes[].value.verb`: string; `entry[].changes[].value.post_id`: string; `entry[].changes[].value.comment_id`: string; `entry[].changes[].value.from`: object; `entry[].changes[].value.from.id`: string; `entry[].changes[].value.from.name`: string; `entry[].changes[].value.message`: string; `entry[].changes[].value.created_time`: integer |
| `jobs.fb-group-comments-fetcher` | fb-group-comments-fetcher | consume | `job_id`: ; `source_id`: ; `kind`:  [enum: comments \| replies \| ops_force]; `post_ref`:  [the post's platform id and permalink; for replies also the parent comment_id]; `series_step`: ; `due_at`: ; `attempt`:  |
| `jobs.fb-group-posts-poller` | fb-group-posts-poller | consume | `source_id`: ; `tier`: ; `attempt`: ; `kind`:  [enum: rotation \| backfill \| ops_force]; `job_id`: string |
| `jobs.fb-keyword-search` | fb-keyword-search | consume | `source_id`: ; `attempt`: ; `job_id`: string |
| `jobs.fb-page-feed-poller` | fb-page-feed-poller | consume | `source_id`: ; `tier`: ; `attempt`: ; `reason`:  [enum: rotation \| reconciliation \| ops_force]; `job_id`: string |
| `jobs.fb-page-resolver` | fb-page-resolver | consume | `job_id`: ; `kind`:  [enum: resolve \| rotation \| ops_force]; `candidate_key`:  [facebook:<platform_id> \| facebook:<handle>]; `client_ids`: ; `due_at`: ; `attempt`:  |
| `jobs.fb-page-search` | fb-page-search | consume | `keyword_id`: ; `client_ids`: ; `reason`:  [enum: seed \| weekly]; `attempt`:  |
| `jobs.fb-post-comments-fetcher` | fb-post-comments-fetcher | consume | `job_id`: ; `source_id`: ; `kind`:  [comments (5.1); ops_force also used (4, 5.1 Paging, 13.8)]; `post_ref`:  [the post's platform id, <page-id>_<post-id>]; `series_step`: ; `due_at`: ; `attempt`:  |
| `jobs.fb-reactions-fetcher` | fb-reactions-fetcher | consume | `source_id`: ; `platform_id`: ; `kind`:  [enum: refresh_24h \| refresh_7d \| refresh_client]; `attempt`: ; `due_at`:  [created_time + 24 h (refresh_24h); created_time + 7 d (refresh_7d)] |
| `jobs.ig-account-media-poller` | ig-account-media-poller | consume | `job_id`: ; `source_id`: ; `kind`:  [enum: rotation\|reconciliation\|backfill\|metrics\|ops_force]; `attempt`:  |
| `jobs.ig-account-resolver` | ig-account-resolver | consume | `candidate_key`:  [instagram:<platform_id> \| instagram:<handle>]; `source_id`: ; `handle`: ; `client_ids`: ; `kind`:  [enum: resolve\|rotation]; `attempt`:  |
| `jobs.ig-comments-fetcher` | ig-comments-fetcher | consume | `source_id`: ; `post_ref`: ; `kind`:  [enum: comments\|ops_force]; `series_step`: ; `attempt`: ; `due_at`:  |
| `jobs.ig-hashtag-search` | ig-hashtag-search | consume | `source_id`: ; `edge`:  [enum: recent_media\|top_media]; `ig_user_id`: ; `attempt`: ; `job_id`:  |
| `jobs.ig-keyword-search` | ig-keyword-search | consume | `source_id`: ; `kind`:  [enum: rotation\|backfill\|ops_force]; `attempt`:  |
| `jobs.ig-mentions-fetcher` | ig-mentions-fetcher | consume | `source_id`: ; `kind`:  [enum: rotation\|reconciliation\|backfill\|ops_force]; `attempt`:  |
| `jobs.ig-mentions-fetcher` | ig-webhook-receiver | produce | `kind`:  [enum: reconciliation\|ops_force]; `one id`:  |
| `jobs.ig-own-comments-fetcher` | ig-own-comments-fetcher | consume | `source_id`: ; `post_ref`:  [media id]; `kind`:  [enum: comments\|replies\|reconciliation\|ops_force]; `series_step`: ; `attempt`: ; `due_at`:  |
| `jobs.ig-own-comments-fetcher` | ig-webhook-receiver | produce | `kind`:  [enum: reconciliation\|ops_force]; `post_ref`:  [media id] |
| `jobs.ig-webhook-receiver` | ig-webhook-receiver | produce | `kind`:  [push]; `body`: object; `headers`: ; `received_at`: ; `body.object`: string; `body.entry`: array; `body.entry[].id`: string; `body.entry[].time`: integer; `body.entry[].changes`: array; `body.entry[].changes[].field`: string [enum: comments\|mentions]; `body.entry[].changes[].value`: object; `body.entry[].changes[].value.id`: string; `body.entry[].changes[].value.text`: string; `body.entry[].changes[].value.media`: object; `body.entry[].changes[].value.media.id`: string |
| `jobs.keyword-matcher` | keyword-matcher | consume | `kind`: string [rematch \| candidate_retry]; `client_id`:  [uuid]; `keyword_ids`: ; `window`:  [from keywords.rematch_days]; `job_id`: ; `hit_id`:  |
| `jobs.li-client-posts-poller` | li-client-posts-poller | consume | `job_id`: ; `source_id`: ; `kind`:  [enum: rotation \| reconciliation \| backfill \| ops_force]; `attempt`:  |
| `jobs.li-company-posts-poller` | li-company-posts-poller | consume | `job_id`: ; `source_id`: ; `kind`:  [enum: rotation \| backfill \| ops_force]; `attempt`:  |
| `jobs.li-org-resolver` | li-org-resolver | consume | `candidate_key`:  [linkedin:org:<handle>]; `url_or_handle`: ; `origin`:  [enum: discovery \| seed \| manual]; `client_ids`: ; `seed_list`: ; `kind`: ; `attempt`: ; `force`:  |
| `jobs.li-own-comments-fetcher` | li-own-comments-fetcher | consume | `kind`:  [enum: comments]; `post_ref`:  [the post URN]; `series_step`: ; `due_at`: ; `attempt`: ; `source_id`:  |
| `jobs.li-post-comments-fetcher` | li-post-comments-fetcher | consume | `kind`:  [enum: comments]; `post_ref`: ; `series_step`: ; `due_at`: ; `attempt`: ; `source_id`:  |
| `jobs.li-post-search` | li-post-search | consume | `job_id`: ; `source_id`: ; `kind`: ; `attempt`:  |
| `jobs.news-comments-fetcher` | news-comments-fetcher | consume | `job_id`:  [ULID]; `source_id`: ; `kind`:  [comments\|ops_force]; `due_at`: ; `attempt`: ; `post_ref`:  [composite: article item id, canonical URL, disqus_shortname, thread identifier or thread id when known, newest stored comment time]; `post_ref.disqus_shortname`: ; `post_ref.thread_id`: ; `post_ref.(article item id)`: ; `post_ref.(canonical URL)`: ; `post_ref.(thread identifier)`: ; `post_ref.(newest stored comment time)`: ; `series_step`:  |
| `jobs.news-feed-poller` | news-feed-poller | consume | `source_id`: ; `tier`: ; `attempt`: ; `kind`:  [rotation\|ops_force] |
| `jobs.news-homepage-differ` | news-homepage-differ | consume | `source_id`: ; `kind`:  [rotation\|ops_force]; `attempt`:  |
| `jobs.news-robots-checker` | news-robots-checker | consume | `host`: ; `kind`:  [first_check\|refresh\|recheck\|ops_force]; `attempt`: ; `requested_by`:  |
| `jobs.news-site-resolver` | news-site-resolver | consume | `kind`: string [enum: resolve\|refresh]; `attempt`: ; `(URL to normalise to a host)`:  |
| `jobs.news-sitemap-poller` | news-sitemap-poller | consume | `source_id`: ; `kind`:  [rotation\|backfill\|ops_force]; `attempt`:  |
| `jobs.normalize-item` | normalize-item | consume | `kind`: string [replay \| lang_rescore]; `date range`: ; `platform filter`:  |
| `jobs.poster-resolver` | poster-resolver | consume | `kind`: string [resolved \| unresolvable \| manual_candidate]; `platform_id`: ; `handle`: ; `url`: ; `display_name`: ; `account-type field`: ; `verified`: ; `followers`: ; `posts_30d`: ; `last_post_at`: ; `location_text`: ; `website`: ; `biography`: ; `created_at`: ; `recent post texts`:  [up to 20]; `raw payload`:  |
| `jobs.poster-resolver` | registry-writer | produce | `origin`: string |
| `jobs.tg-bot-channel-receiver` | tg-bot-channel-receiver | consume | `attempt`:  |
| `jobs.tg-channel-posts-poller` | tg-channel-posts-poller | consume | `source_id`: ; `attempt`: ; `job_id`: string |
| `jobs.tg-channel-resolver` | tg-channel-resolver | consume | `job_id`: ; `candidate`:  [username or t.me URL]; `origin`:  [enum: discovery\|client\|ops\|refresh]; `client_ids`: ; `hit_item_keys`: ; `attempt`:  |
| `jobs.tg-discussion-receiver` | tg-discussion-receiver | consume | `attempt`:  |
| `jobs.tg-message-search` | tg-message-search | consume | `job_id`: ; `set_id`: ; `keyword_ids`: ; `window_start`: ; `window_end`: ; `attempt`:  |
| `jobs.tt-client-videos-fetcher` | tt-client-videos-fetcher | consume | `source_id`: ; `kind`:  [enum: rotation\|backfill\|ops_force]; `attempt`: ; `job_id`: string |
| `jobs.tt-hashtag-feed-poller` | tt-hashtag-feed-poller | consume | `source_id`: ; `attempt`: ; `job_id`: string |
| `jobs.tt-keyword-search` | tt-keyword-search | consume | `source_id`: ; `attempt`: ; `job_id`: string |
| `jobs.tt-profile-videos-poller` | tt-profile-videos-poller | consume | `source_id`: ; `kind`:  [enum: rotation\|reconciliation\|backfill\|ops_force]; `attempt`: ; `job_id`: string |
| `jobs.tt-user-resolver` | tt-user-resolver | consume | `candidate_key`:  [tiktok:<platform_id> or tiktok:<handle>]; `lookup identifier`:  [user id when the job has one, else handle]; `client_ids`: ; `attempt`: ; `priority`:  |
| `jobs.tt-video-comments-fetcher` | tt-video-comments-fetcher | consume | `job_id`: ; `source_id`: ; `kind`:  [enum: comments\|replies]; `due_at`: ; `attempt`: ; `post_ref`:  [tiktok:video:<id>, or the parent comment's key for replies]; `series_step`:  |
| `jobs.tt-video-stats-refresher` | tt-video-stats-refresher | consume | `job_id`: ; `source_id`: ; `kind`:  [metrics]; `due_at`: ; `attempt`: ; `post_ref`:  [tiktok:video:<id>]; `series_step`:  [+24h \| +7d] |
| `jobs.web-commoncrawl-scanner` | web-commoncrawl-scanner | consume | `kind`: string [enum: rotation\|ops_force]; `attempt`:  |
| `jobs.web-gdelt-poller` | web-gdelt-poller | consume | `source_id`: ; `kind`: string [enum: rotation]; `job_id`: string; `attempt`: integer |
| `jobs.web-search-mojeek` | web-search-mojeek | consume | `source_id`: ; `kind`: string [enum: rotation]; `job_id`: string; `attempt`: integer |
| `jobs.web-search-perplexity` | web-search-perplexity | consume | `source_id`: ; `kind`: string [enum: rotation\|site_search]; `job_id`: string; `attempt`: integer; `budget_tag`:  |
| `jobs.x-full-archive-search` | x-full-archive-search | consume | `job_id`: ; `source_id`: ; `kind`:  [enum: backfill\|keyword_history\|replies]; `attempt`: ; `window_start`: ; `window_end`: ; `requested_by`: ; `post_ref`: ; `series_step`:  |
| `jobs.x-recent-search` | x-filtered-stream | produce | `kind`:  [enum: reconciliation]; `source_id`: ; `query`: ; `source_ids`: ; `client_ids`: ; `window_start`: ; `window_end`: ; `priority`:  |
| `jobs.x-recent-search` | x-recent-search | consume | `source_id`: ; `tier`: ; `attempt`: ; `reason`:  [enum: rotation\|first_run\|gap_backfill\|ops_force] |
| `jobs.x-replies-fetcher` | x-replies-fetcher | consume | `kind`:  [enum: comments]; `post_ref`: ; `series_step`: ; `due_at`: ; `attempt`: ; `source_id`: ; `job_id`:  |
| `jobs.x-user-resolver` | x-user-resolver | consume | `job_id`: ; `kind`:  [enum: resolve\|rotation\|ops_force]; `candidate_key`:  [x:<user id> or x:<handle>]; `client_ids`: ; `due_at`: ; `attempt`:  |
| `jobs.x-user-timeline-poller` | x-user-timeline-poller | consume | `job_id`: ; `source_id`: ; `kind`:  [enum: rotation\|reconciliation\|ops_force]; `attempt`:  |
| `jobs.yt-channel-resolver` | yt-channel-resolver | consume | `job_id`: ; `kind`:  [enum: resolve\|rotation\|ops_force]; `candidate_key`:  [youtube:<channel id> or youtube:<handle>]; `source_id`: ; `client_ids`: ; `due_at`: ; `attempt`:  |
| `jobs.yt-channel-resolver` | yt-web-search-bridge | produce | `kind`:  [enum: resolve]; `origin`:  [web_bridge]; `channel reference`:  [channel/UC…, @handle, c/<name>, user/<name>] |
| `jobs.yt-comments-fetcher` | yt-comments-fetcher | consume | `kind`:  [enum: comments]; `post_ref`: ; `series_step`: ; `due_at`: ; `attempt`: ; `source_id`: ; `job_id`:  |
| `jobs.yt-comments-fetcher` | yt-text-purger | produce | `kind`:  [enum: refresh]; `post_ref`: ; `thread_ids`: ; `run_id`: ; `must_finish_by`:  [earliest deadline minus DELETE_MARGIN]; `refresh_for_client_ids`:  |
| `jobs.yt-pubsub-receiver` | yt-pubsub-receiver | produce | `body`:  [Atom XML] |
| `jobs.yt-replies-fetcher` | yt-replies-fetcher | consume | `kind`:  [enum: replies]; `post_ref`:  [video id and thread id]; `series_step`: ; `due_at`: ; `attempt`: ; `source_id`:  |
| `jobs.yt-replies-fetcher` | yt-text-purger | produce | `kind`:  [enum: refresh]; `post_ref`: ; `thread_ids`: ; `run_id`: ; `must_finish_by`:  [earliest deadline minus DELETE_MARGIN]; `refresh_for_client_ids`:  |
| `jobs.yt-text-purger` | retention-purger | produce | `cut-off`:  |
| `jobs.yt-text-purger` | yt-text-purger | consume | `run_id`: ; `cutoff`:  [now - 30 days]; `next_sweep_at`:  |
| `jobs.yt-uploads-reconciler` | yt-uploads-reconciler | consume | `source_id`: ; `kind`:  [enum: reconciliation\|backfill\|ops_force]; `reason`:  [lease_lapsed]; `attempt`: ; `window start`: ; `cap`:  |
| `jobs.yt-video-details-fetcher` | yt-keyword-search | produce | `kind`:  [enum: first_sight]; `batch of video ids`:  |
| `jobs.yt-video-details-fetcher` | yt-pubsub-receiver | produce | `job_id`: string; `source_id`: string; `kind`: string; `due_at`: string; `attempt`: integer; `post_ref`: string [<videoId>]; `series_step`: null |
| `jobs.yt-video-details-fetcher` | yt-text-purger | produce | `kind`:  [enum: refresh]; `post_ref`: ; `thread_ids`: ; `run_id`: ; `must_finish_by`:  [earliest deadline minus DELETE_MARGIN]; `refresh_for_client_ids`:  |
| `jobs.yt-video-details-fetcher` | yt-uploads-reconciler | produce | `job_id`: string; `source_id`: string; `kind`: string; `origin_kind`: string; `post_ref`: array [up to 50 video ids]; `post_ref[]`: string; `attempt`: integer |
| `jobs.yt-video-details-fetcher` | yt-video-details-fetcher | consume | `job_id`: ; `source_id`: ; `kind`:  [enum: first_sight\|metrics\|ops_force]; `post_ref`:  [video id]; `due_at`: ; `attempt`: ; `series_step`:  [enum: backfill\|24h\|7d\|client] |
| `jobs.yt-video-details-fetcher` | yt-web-search-bridge | produce | `kind`:  [enum: first_sight]; `origin`:  [web_bridge]; `source_id`: ; `list of video ids`:  [up to 50 ids] |
| `normalize-item job (queue name not written)` | lang-dialect-id | mention | `kind`: string [replay \| lang_rescore] |

### 3.4 Dead-letter queues

| Dead letter | Written by | Mentioned by |
|---|---|---|
| `dlq.<fetcher>` |  | yt-text-purger |
| `dlq.<service>` |  | backfill-orchestrator, comment-decay-scheduler |
| `dlq.aggregator` | aggregator |  |
| `dlq.alert-evaluator` | alert-evaluator |  |
| `dlq.analysis-entities` | analysis-entities |  |
| `dlq.analysis-media` | analysis-media |  |
| `dlq.analysis-sentiment` | analysis-sentiment |  |
| `dlq.analysis-topics` | analysis-topics |  |
| `dlq.backfill-orchestrator` | backfill-orchestrator |  |
| `dlq.comment-decay-scheduler` | comment-decay-scheduler |  |
| `dlq.deletion-propagator` | deletion-propagator |  |
| `dlq.fb-backfill` | fb-backfill |  |
| `dlq.fb-client-webhook-receiver` | fb-client-webhook-receiver |  |
| `dlq.fb-group-comments-fetcher` | fb-group-comments-fetcher |  |
| `dlq.fb-group-posts-poller` | fb-group-posts-poller |  |
| `dlq.fb-keyword-search` | fb-keyword-search |  |
| `dlq.fb-page-feed-poller` | fb-page-feed-poller |  |
| `dlq.fb-page-resolver` | fb-page-resolver |  |
| `dlq.fb-page-search` | fb-page-search |  |
| `dlq.fb-post-comments-fetcher` | fb-post-comments-fetcher |  |
| `dlq.fb-reactions-fetcher` | fb-reactions-fetcher |  |
| `dlq.ig-account-media-poller` | ig-account-media-poller |  |
| `dlq.ig-account-resolver` | ig-account-resolver |  |
| `dlq.ig-comments-fetcher` | ig-comments-fetcher |  |
| `dlq.ig-hashtag-search` | ig-hashtag-search |  |
| `dlq.ig-keyword-search` | ig-keyword-search |  |
| `dlq.ig-mentions-fetcher` | ig-mentions-fetcher |  |
| `dlq.ig-own-comments-fetcher` | ig-own-comments-fetcher |  |
| `dlq.ig-webhook-receiver` | ig-webhook-receiver |  |
| `dlq.keyword-matcher` | keyword-matcher |  |
| `dlq.li-client-posts-poller` | li-client-posts-poller |  |
| `dlq.li-company-posts-poller` | li-company-posts-poller |  |
| `dlq.li-org-resolver` | li-org-resolver |  |
| `dlq.li-own-comments-fetcher` | li-own-comments-fetcher |  |
| `dlq.li-post-comments-fetcher` | li-post-comments-fetcher |  |
| `dlq.li-post-search` | li-post-search |  |
| `dlq.news-article-extractor` | news-article-extractor |  |
| `dlq.news-comments-fetcher` | news-comments-fetcher |  |
| `dlq.news-dedup` | news-dedup |  |
| `dlq.news-feed-poller` | news-feed-poller |  |
| `dlq.news-homepage-differ` | news-homepage-differ |  |
| `dlq.news-robots-checker` | news-robots-checker |  |
| `dlq.news-site-resolver` | news-site-resolver |  |
| `dlq.news-sitemap-poller` | news-sitemap-poller |  |
| `dlq.normalize-item` | normalize-item |  |
| `dlq.poster-resolver` | poster-resolver |  |
| `dlq.qualifier` | qualifier |  |
| `dlq.raw-archiver` | raw-archiver |  |
| `dlq.registry-writer` | registry-writer |  |
| `dlq.retention-purger` | retention-purger |  |
| `dlq.search-hit-router` | search-hit-router |  |
| `dlq.source-health-canary` | source-health-canary |  |
| `dlq.store-writer` | store-writer |  |
| `dlq.tg-bot-channel-receiver` | tg-bot-channel-receiver |  |
| `dlq.tg-channel-posts-poller` | tg-channel-posts-poller |  |
| `dlq.tg-channel-resolver` | tg-channel-resolver |  |
| `dlq.tg-discussion-receiver` | tg-discussion-receiver |  |
| `dlq.tg-message-search` | tg-message-search |  |
| `dlq.tt-client-videos-fetcher` | tt-client-videos-fetcher |  |
| `dlq.tt-hashtag-feed-poller` | tt-hashtag-feed-poller |  |
| `dlq.tt-keyword-search` | tt-keyword-search |  |
| `dlq.tt-profile-videos-poller` | tt-profile-videos-poller |  |
| `dlq.tt-user-resolver` | tt-user-resolver |  |
| `dlq.tt-video-comments-fetcher` | tt-video-comments-fetcher |  |
| `dlq.tt-video-stats-refresher` | tt-video-stats-refresher |  |
| `dlq.web-commoncrawl-scanner` | web-commoncrawl-scanner |  |
| `dlq.web-gdelt-poller` | web-gdelt-poller |  |
| `dlq.web-search-mojeek` | web-search-mojeek |  |
| `dlq.web-search-perplexity` | web-search-perplexity |  |
| `dlq.x-compliance-sync` | x-compliance-sync |  |
| `dlq.x-filtered-stream` | x-filtered-stream |  |
| `dlq.x-full-archive-search` | x-full-archive-search |  |
| `dlq.x-recent-search` | x-recent-search |  |
| `dlq.x-replies-fetcher` | x-replies-fetcher |  |
| `dlq.x-user-resolver` | x-user-resolver |  |
| `dlq.x-user-timeline-poller` | x-user-timeline-poller |  |
| `dlq.yt-channel-resolver` | yt-channel-resolver |  |
| `dlq.yt-comments-fetcher` | yt-comments-fetcher |  |
| `dlq.yt-keyword-search` | yt-keyword-search |  |
| `dlq.yt-pubsub-receiver` | yt-pubsub-receiver |  |
| `dlq.yt-replies-fetcher` | yt-replies-fetcher |  |
| `dlq.yt-text-purger` | yt-text-purger |  |
| `dlq.yt-uploads-reconciler` | yt-uploads-reconciler |  |
| `dlq.yt-video-details-fetcher` | yt-video-details-fetcher |  |
| `dlq.yt-web-search-bridge` | yt-web-search-bridge |  |

## 4. By table

Every table, path and store a PRD names. For each column: who writes it (and how, when the PRD says) and who reads it. `read_write` counts as both. Column names are exactly as written; a few PRDs describe a column in words instead of naming it, and those descriptions are kept as written.

### 4.1 Control plane (Supabase Postgres)

| Table | In CONVENTIONS | PRDs naming it |
|---|---|---|
| `budgets` | yes | 55: backfill-orchestrator, comment-decay-scheduler, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, fb-page-search, fb-post-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-org-resolver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-comments-fetcher, qualifier, quota-governor, source-health-canary, tg-channel-posts-poller, tg-channel-resolver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-resolver, x-user-timeline-poller, yt-channel-resolver, yt-comments-fetcher, yt-keyword-search, yt-replies-fetcher, yt-uploads-reconciler, yt-video-details-fetcher, yt-web-search-bridge |
| `canary_targets` | yes | 15: fb-keyword-search, fb-page-search, source-health-canary, tg-bot-channel-receiver, tg-channel-posts-poller, tg-discussion-receiver, tg-message-search, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-full-archive-search, x-user-timeline-poller |
| `client_sources` | yes | 19: analysis-topics, backfill-orchestrator, comment-decay-scheduler, ig-hashtag-search, li-client-posts-poller, li-company-posts-poller, li-org-resolver, li-post-comments-fetcher, news-site-resolver, qualifier, quota-governor, registry-writer, retention-purger, source-health-canary, tg-channel-resolver, tg-message-search, x-compliance-sync, x-filtered-stream, yt-text-purger |
| `clients` | yes | 57: alert-evaluator, deletion-propagator, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, fb-page-search, fb-post-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-org-resolver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-site-resolver, poster-resolver, qualifier, quota-governor, raw-archiver, registry-writer, retention-purger, source-health-canary, store-writer, tg-channel-posts-poller, tg-channel-resolver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-resolver, x-user-timeline-poller, yt-text-purger, yt-web-search-bridge |
| `crawl_policies` | yes | 7: news-article-extractor, news-comments-fetcher, news-feed-poller, news-homepage-differ, news-robots-checker, news-site-resolver, news-sitemap-poller |
| `cursors` | yes | 64: aggregator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-search, fb-post-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-comments-fetcher, news-feed-poller, news-homepage-differ, news-site-resolver, news-sitemap-poller, normalize-item, raw-archiver, retention-purger, store-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-video-stats-refresher, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-timeline-poller, yt-channel-resolver, yt-comments-fetcher, yt-keyword-search, yt-pubsub-receiver, yt-replies-fetcher, yt-text-purger, yt-uploads-reconciler, yt-video-details-fetcher, yt-web-search-bridge |
| `decisions` | yes | 9: fb-page-search, li-org-resolver, news-dedup, news-site-resolver, poster-resolver, qualifier, registry-writer, tg-channel-resolver, tg-message-search |
| `deletion_requests` | yes | 6: deletion-propagator, raw-archiver, retention-purger, store-writer, x-compliance-sync, yt-text-purger |
| `keywords` | yes | 19: fb-keyword-search, fb-page-search, ig-keyword-search, keyword-matcher, lang-dialect-id, li-post-search, poster-resolver, qualifier, store-writer, tg-message-search, tt-keyword-search, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-full-archive-search, x-recent-search, yt-keyword-search, yt-web-search-bridge |
| `retention_classes` | yes | 11: aggregator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, normalize-item, raw-archiver, retention-purger, store-writer, tt-client-videos-fetcher, yt-text-purger |
| `review_queue` | yes | 21: analysis-entities, analysis-media, analysis-sentiment, analysis-topics, ig-account-media-poller, ig-account-resolver, li-org-resolver, news-site-resolver, normalize-item, qualifier, search-hit-router, tg-channel-resolver, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-recent-search, yt-comments-fetcher, yt-keyword-search, yt-replies-fetcher, yt-web-search-bridge |
| `service_runs` | yes | 85: aggregator, alert-evaluator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, backfill-orchestrator, comment-decay-scheduler, deletion-propagator, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, fb-page-search, fb-post-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, keyword-matcher, lang-dialect-id, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-org-resolver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-article-extractor, news-comments-fetcher, news-dedup, news-feed-poller, news-homepage-differ, news-robots-checker, news-site-resolver, news-sitemap-poller, normalize-item, poster-resolver, qualifier, raw-archiver, registry-writer, retention-purger, search-hit-router, source-health-canary, store-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-commoncrawl-scanner, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-compliance-sync, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-resolver, x-user-timeline-poller, yt-channel-resolver, yt-comments-fetcher, yt-keyword-search, yt-pubsub-receiver, yt-replies-fetcher, yt-text-purger, yt-uploads-reconciler, yt-video-details-fetcher, yt-web-search-bridge |
| `sources` | yes | 80: analysis-entities, analysis-media, analysis-sentiment, analysis-topics, backfill-orchestrator, comment-decay-scheduler, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, fb-page-search, fb-post-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-org-resolver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-article-extractor, news-comments-fetcher, news-dedup, news-feed-poller, news-homepage-differ, news-robots-checker, news-site-resolver, news-sitemap-poller, normalize-item, poster-resolver, qualifier, registry-writer, retention-purger, search-hit-router, source-health-canary, store-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-commoncrawl-scanner, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-compliance-sync, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-resolver, x-user-timeline-poller, yt-channel-resolver, yt-comments-fetcher, yt-keyword-search, yt-pubsub-receiver, yt-replies-fetcher, yt-text-purger, yt-uploads-reconciler, yt-video-details-fetcher, yt-web-search-bridge |
| `vendor_keys` | yes | 26: fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, ig-comments-fetcher, ig-keyword-search, li-company-posts-poller, li-org-resolver, li-post-comments-fetcher, li-post-search, news-comments-fetcher, quota-governor, retention-purger, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-search-mojeek, web-search-perplexity, yt-web-search-bridge |
| `alert_deliveries` | **no** | 1: alert-evaluator |
| `alert_rules` | **no** | 1: alert-evaluator |
| `alert_watch_items` | **no** | 1: alert-evaluator |
| `alerts` | **no** | 1: alert-evaluator |
| `backfill_runs` | **no** | 1: backfill-orchestrator |
| `brand_assets` | **no** | 1: analysis-media |
| `budget_history` | **no** | 1: quota-governor |
| `budget_reservations` | **no** | 1: quota-governor |
| `cc_hosts_seen` | **no** | 1: web-commoncrawl-scanner |
| `comment index (yt-comments-fetcher's)` | **no** | 2: yt-comments-fetcher, yt-replies-fetcher |
| `comment_ledger` | **no** | 2: fb-group-comments-fetcher, fb-post-comments-fetcher |
| `comment_series` | **no** | 3: comment-decay-scheduler, x-replies-fetcher, yt-comments-fetcher |
| `ig_hashtag_ledger` | **no** | 1: quota-governor |
| `kb_aliases` | **no** | 1: analysis-entities |
| `kb_entities` | **no** | 1: analysis-entities |
| `model_versions` | **no** | 4: analysis-entities, analysis-media, analysis-sentiment, analysis-topics |
| `news_sites` | **no** | 7: news-article-extractor, news-comments-fetcher, news-feed-poller, news-homepage-differ, news-robots-checker, news-site-resolver, news-sitemap-poller |
| `news_stories` | **no** | 1: news-dedup |
| `news_story_members` | **no** | 1: news-dedup |
| `news_urls` | **no** | 5: news-article-extractor, news-dedup, news-feed-poller, news-homepage-differ, news-sitemap-poller |
| `onboarding records` | **no** | 1: tg-bot-channel-receiver |
| `poster_profiles` | **no** | 2: poster-resolver, x-user-resolver |
| `profile_cache` | **no** | 4: fb-page-resolver, ig-account-resolver, x-user-resolver, yt-channel-resolver |
| `registry` | **no** | 1: lang-dialect-id |
| `registry_audit` | **no** | 1: registry-writer |
| `reply index (x-replies-fetcher's)` | **no** | 1: x-replies-fetcher |
| `reply index (yt-replies-fetcher's)` | **no** | 1: yt-replies-fetcher |
| `retention_audit` | **no** | 2: retention-purger, yt-text-purger |
| `search_candidate_seen` | **no** | 1: search-hit-router |
| `search_parked_urls` | **no** | 1: search-hit-router |
| `search_url_seen` | **no** | 1: search-hit-router |
| `taxonomy_nodes` | **no** | 1: analysis-topics |
| `tt_client_video_state` | **no** | 1: tt-client-videos-fetcher |
| `tt_comment_state` | **no** | 1: tt-video-comments-fetcher |
| `tt_user_cache` | **no** | 1: tt-user-resolver |
| `x_compliance_audit` | **no** | 1: x-compliance-sync |
| `x_compliance_runs` | **no** | 1: x-compliance-sync |
| `x_read_ledger` | **no** | 1: quota-governor |
| `yt_live_watch` | **no** | 1: yt-video-details-fetcher |
| `yt_subscriptions` | **no** | 1: yt-pubsub-receiver |

#### `budgets`

In CONVENTIONS: yes. Named by 55 PRD(s).

- Table-level writers: fb-backfill, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-search, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, li-client-posts-poller, li-company-posts-poller, li-org-resolver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, quota-governor, tg-channel-posts-poller, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-gdelt-poller, web-search-mojeek, web-search-perplexity, yt-keyword-search, yt-uploads-reconciler, yt-video-details-fetcher, yt-web-search-bridge
- Table-level readers: backfill-orchestrator, comment-decay-scheduler, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, fb-page-search, fb-post-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-org-resolver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-comments-fetcher, qualifier, quota-governor, source-health-canary, tg-channel-posts-poller, tg-channel-resolver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-resolver, x-user-timeline-poller, yt-channel-resolver, yt-comments-fetcher, yt-keyword-search, yt-replies-fetcher, yt-uploads-reconciler, yt-video-details-fetcher, yt-web-search-bridge
- Keys as stated: one row per budget_tag and sub_counter (implied by the example); per client business account (ig_user_id)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `(unnamed) cap for mojeek_search` |  |  | web-search-mojeek |  |
| `(unnamed) counters (queries and GBP, per month)` |  | web-search-mojeek (through quota-governor (allowance request, then cost_units report)) | web-search-mojeek |  |
| `(unnamed) governor counters` |  | web-search-perplexity (through quota-governor (allowance request, then cost_units report)) | web-search-perplexity |  |
| `(unnamed) money cap` |  |  |  | web-gdelt-poller |
| `(unnamed) monthly cap for perplexity_search` |  |  | web-search-perplexity |  |
| `(unnamed) per-minute ceiling` |  |  |  | web-search-perplexity |
| `(unnamed) request counters under gdelt_doc_api` |  | web-gdelt-poller (through quota-governor (allowance per request, then cost_units report)) | web-gdelt-poller |  |
| `(unnamed) counters` |  | yt-video-details-fetcher (through quota-governor, 6.3 L159) | yt-video-details-fetcher |  |
| `backfill allowance` |  |  | yt-keyword-search |  |
| `budget counters per engine` |  | yt-web-search-bridge (through quota-governor (6.1); updated with actual request and query counts after acknowledgement (5.2 step 8)) | yt-web-search-bridge |  |
| `budget_tag` | string (quota-governor) | quota-governor | quota-governor |  |
| `counters for li_vendor_company_posts (column names not stated)` |  | li-company-posts-poller (state per 6.3; allowance asked of quota-governor and cost_units reported to quota-governor after acknowledgement) | li-company-posts-poller |  |
| `counters for li_vendor_post_comments (column names not stated)` |  | li-post-comments-fetcher (state per 6.3 L133) | li-post-comments-fetcher |  |
| `counters in USD` |  | tg-channel-posts-poller (state per 6.3 L132) | tg-channel-posts-poller |  |
| `counters per client token (column names not stated)` |  | li-client-posts-poller (read through quota-governor (6.1); 5.2 step 7 'Record the metrics of section 10 and the rate-limit usage into budgets' (write path not st...)<br>li-own-comments-fetcher (state per 6.3 L130) | li-client-posts-poller, li-own-comments-fetcher |  |
| `counters per token` |  | fb-backfill (through quota-governor)<br>fb-page-search (through quota-governor)<br>fb-reactions-fetcher (through quota-governor) | fb-backfill, fb-page-search, fb-reactions-fetcher |  |
| `counters per token per 24 h` |  | fb-page-feed-poller (through quota-governor) | fb-page-feed-poller |  |
| `counters under li_vendor_org_resolver (column names not stated)` |  | li-org-resolver (state per 6.3 L109) | li-org-resolver |  |
| `counters under li_vendor_post_search (column names not stated)` |  | li-post-search (state per 6.3 L109) | li-post-search |  |
| `counters under tt_display:<client_id>` |  | tt-client-videos-fetcher (through quota-governor) | tt-client-videos-fetcher |  |
| `counters under tt_vendor (sub-counter profile_videos)` |  | tt-profile-videos-poller (6.1: through quota-governor; 5.2 step 7: 'Record ... the request count into `budgets`' (that step does not say through quota-governor)) | tt-profile-videos-poller |  |
| `currency` | string (quota-governor) | quota-governor | quota-governor |  |
| `distinct channels queried` |  |  | tg-channel-resolver |  |
| `fb_vendor counters` |  | fb-group-comments-fetcher (through quota-governor)<br>fb-group-posts-poller (through quota-governor; requests billed recorded into budgets (5.2 step 7))<br>fb-keyword-search (through quota-governor; cost recorded after ack) | fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search |  |
| `first queried at` |  | ig-hashtag-search (ledger per client business account, 6.3 L128) | ig-hashtag-search |  |
| `hashtag id` |  | ig-hashtag-search (ledger per client business account, 6.3 L128) | ig-hashtag-search |  |
| `keywords this month` |  |  | tg-message-search |  |
| `limit` | integer (quota-governor) | quota-governor (raised only by an audited ops raise) | quota-governor |  |
| `LinkedIn vendor budget split (name not stated)` |  |  | li-company-posts-poller, li-post-comments-fetcher, li-post-search |  |
| `max items cap per run (name not stated)` |  |  | li-post-comments-fetcher |  |
| `max items per run floor and cap (name not stated)` |  |  | li-company-posts-poller |  |
| `mode` | string (quota-governor); normal, stretch, exhausted (backfill-orchestrator); normal, stretch, exhausted (quota-governor) | quota-governor (re-evaluated after each decision) | backfill-orchestrator, quota-governor |  |
| `per-job caps` |  |  | x-full-archive-search |  |
| `period` | string (quota-governor); billing_cycle (quota-governor) | quota-governor | quota-governor |  |
| `requests this month` |  |  | tg-channel-resolver, tg-message-search |  |
| `reserved` | integer (quota-governor) | quota-governor (one conditional UPDATE per decision) | quota-governor |  |
| `reset_rule` | UTC day, billing cycle, rolling 24 hours, rolling 7 days, daily at the provider's reset time, calendar month or contract cycle (quota-governor) |  | quota-governor |  |
| `search bucket calls today; pages per term today` |  | yt-keyword-search (governor counters, through quota-governor) |  |  |
| `stretch_factor` | number (quota-governor) | quota-governor (max(1, projected / limit) on amber tags in stretch) | quota-governor |  |
| `sub_counter` | string (quota-governor); post_reads, user_reads, search, ingest, comments, reserve, (per-service sub-counters for tt_vendor) (quota-governor) | quota-governor | quota-governor |  |
| `Tier 1 shortened interval (budgets configuration; name not stated)` |  |  | li-company-posts-poller |  |
| `unit` | string (quota-governor) | quota-governor | quota-governor |  |
| `unit_price` | number (quota-governor) | quota-governor | quota-governor |  |
| `usage headers` |  | fb-reactions-fetcher (recorded in refresh step 6) |  |  |
| `usage headers (X-App-Usage, X-Business-Use-Case-Usage)` |  | fb-page-feed-poller (recorded into budgets by this service (5.2 step 7); mechanism not stated) |  |  |
| `used` | integer (quota-governor) | quota-governor (settled after report) | quota-governor |  |
| `warn_50_at` | string (timestamp) (quota-governor) | quota-governor (alert fired once per period) | quota-governor |  |
| `warn_80_at` |  | quota-governor | quota-governor |  |
| `warn_95_at` |  | quota-governor | quota-governor |  |

#### `canary_targets`

In CONVENTIONS: yes. Named by 15 PRD(s).

- Table-level writers: source-health-canary
- Table-level readers: fb-keyword-search, source-health-canary, tg-bot-channel-receiver, tg-channel-posts-poller, tg-discussion-receiver, tg-message-search, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, web-gdelt-poller, web-search-mojeek, web-search-perplexity
- Mention only: fb-page-search, x-full-archive-search, x-user-timeline-poller

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `active` | boolean (source-health-canary) | source-health-canary (set false on quarantine) | source-health-canary |  |
| `alternate_route` |  |  | source-health-canary |  |
| `alternate_vendor` |  |  | source-health-canary |  |
| `call_params` |  |  | source-health-canary |  |
| `expect_min_items` |  |  | source-health-canary |  |
| `flag_name` | TT_VENDOR_ROUTE, FB_VENDOR_ROUTE, TG_POSTS_ACTOR (source-health-canary) |  | source-health-canary |  |
| `last_ok_at` |  | source-health-canary |  |  |
| `platform` | web (web-gdelt-poller); web (web-search-mojeek); web (web-search-perplexity) |  | source-health-canary, web-gdelt-poller, web-search-mojeek, web-search-perplexity |  |
| `quarantined_at` |  | source-health-canary (on quarantine) |  |  |
| `route` |  |  | source-health-canary |  |
| `service` |  |  | source-health-canary |  |
| `source_id` |  |  | source-health-canary |  |
| `target_id` |  |  | source-health-canary |  |
| `vendor` |  |  | source-health-canary |  |

#### `client_sources`

In CONVENTIONS: yes. Named by 19 PRD(s).

- Table-level writers: registry-writer
- Table-level readers: analysis-topics, backfill-orchestrator, comment-decay-scheduler, ig-hashtag-search, li-client-posts-poller, li-company-posts-poller, li-org-resolver, li-post-comments-fetcher, news-site-resolver, qualifier, quota-governor, registry-writer, retention-purger, source-health-canary, tg-channel-resolver, tg-message-search, x-compliance-sync, x-filtered-stream, yt-text-purger
- Keys as stated: (client_id, source_id)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `added_at` |  | registry-writer (upsert) |  |  |
| `added_by` |  | registry-writer (upsert) |  |  |
| `client_id` |  | registry-writer (upsert on (client_id, source_id)) |  |  |
| `priority` |  | registry-writer (upsert) |  |  |
| `priority list (column name not stated)` |  |  | li-client-posts-poller, li-company-posts-poller |  |
| `source_id` |  | registry-writer (upsert on (client_id, source_id)) |  |  |

#### `clients`

In CONVENTIONS: yes. Named by 57 PRD(s).

- Table-level writers: none
- Table-level readers: alert-evaluator, deletion-propagator, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, fb-page-search, fb-post-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-org-resolver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-site-resolver, poster-resolver, qualifier, quota-governor, raw-archiver, registry-writer, retention-purger, source-health-canary, store-writer, tg-channel-posts-poller, tg-channel-resolver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-resolver, x-user-timeline-poller, yt-text-purger, yt-web-search-bridge

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `(unnamed) government flag` |  |  | web-search-perplexity |  |
| `(unnamed) Perplexity opt-out` |  |  | web-search-perplexity |  |
| `amber acceptance` |  |  | ig-comments-fetcher, ig-keyword-search |  |
| `client's priority flag` |  |  | fb-page-search |  |
| `client_type` | government (alert-evaluator); government (keyword-matcher) |  | alert-evaluator, keyword-matcher |  |
| `contract terms` |  |  | tt-profile-videos-poller |  |
| `engine permission flags` | Mojeek-only, Perplexity opt-in (yt-web-search-bridge) |  | yt-web-search-bridge |  |
| `Enterprise contract` |  |  |  | x-recent-search |
| `government body` |  |  | tg-message-search |  |
| `government client marker (column name not stated)` |  |  | li-org-resolver |  |
| `government flag` |  |  | ig-comments-fetcher, ig-keyword-search, tg-channel-posts-poller, tg-channel-resolver, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher |  |
| `government flag (column name not stated)` |  |  | li-company-posts-poller, li-post-comments-fetcher |  |
| `government marker` |  |  | fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search |  |
| `government marker (column name not stated)` |  |  | li-post-search |  |
| `qualifier_config` | jsonb (qualifier) |  | qualifier |  |
| `status` | active, offboarding (yt-text-purger); offboarding (retention-purger) |  | retention-purger, yt-text-purger |  |
| `token reference` |  |  | fb-page-feed-poller, fb-page-resolver, fb-post-comments-fetcher, tt-client-videos-fetcher |  |
| `token reference (column name not stated)` |  |  | li-client-posts-poller, li-own-comments-fetcher |  |
| `updated_at` |  |  | keyword-matcher |  |
| `X Enterprise entitlement` |  |  | x-filtered-stream, x-full-archive-search, x-user-timeline-poller |  |
| `x_enterprise` | boolean (keyword-matcher); true, false (keyword-matcher) |  | keyword-matcher |  |
| `yt_text_refresh` |  |  | yt-text-purger |  |

#### `crawl_policies`

In CONVENTIONS: yes. Named by 7 PRD(s).

- Table-level writers: news-article-extractor, news-feed-poller, news-homepage-differ, news-robots-checker, news-sitemap-poller
- Table-level readers: news-article-extractor, news-comments-fetcher, news-feed-poller, news-homepage-differ, news-robots-checker, news-site-resolver, news-sitemap-poller
- Keys as stated: one row per host (6.3 L121, 9 L144)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `access_mode` | direct, headless, proxy (news-article-extractor); direct, headless, proxy (news-sitemap-poller); direct, headless, proxy, blocked (news-feed-poller); direct,... | news-robots-checker (upsert of the host's row before the message is produced (5.2 step 9, 8 L138)) | news-article-extractor, news-feed-poller, news-homepage-differ, news-sitemap-poller |  |
| `changed_fields` |  | news-robots-checker (row has 'same fields' as the message (6.2 L117); not in 6.3's list) |  |  |
| `checked_at` |  | news-robots-checker (upsert of the host's row before the message is produced (5.2 step 9, 8 L138)) |  |  |
| `crawl_allowed` | boolean (news-robots-checker); True (news-feed-poller); True (news-homepage-differ); True (news-sitemap-poller); True, False (news-article-extractor); True, ... | news-robots-checker (upsert of the host's row before the message is produced (5.2 step 9, 8 L138)) | news-article-extractor, news-feed-poller, news-homepage-differ, news-site-resolver, news-sitemap-poller |  |
| `crawl_delay_seconds` |  | news-robots-checker (upsert of the host's row before the message is produced (5.2 step 9, 8 L138)) |  |  |
| `expires_at` |  | news-robots-checker (checked_at + 24 hours) | news-article-extractor, news-feed-poller, news-homepage-differ, news-site-resolver, news-sitemap-poller |  |
| `host` |  | news-robots-checker (one row per host; upsert of the host's row before the message is produced (5.2 step 9, 8 L138)) |  |  |
| `next_refresh_at` |  | news-robots-checker (set from the START of the last check; scheduler orders by next_refresh_at then tier) | news-robots-checker |  |
| `next_slot_at` |  | news-article-extractor (host gate slot state)<br>news-feed-poller (host gate slot state in listening-sdk)<br>news-homepage-differ (host gate slot state)<br>news-robots-checker (listed in the row (6.2, 6.3); this PRD takes 'a slot from the host gate' (5.2 step 2) but does not say the slot is stored here)<br>news-sitemap-poller (host gate slot state) | news-article-extractor, news-feed-poller, news-homepage-differ, news-robots-checker, news-sitemap-poller |  |
| `payment` |  | news-robots-checker (upsert of the host's row before the message is produced (5.2 step 9, 8 L138)) |  |  |
| `policy_version` |  | news-robots-checker (incremented on any change; a replay produces the same policy_version once) |  |  |
| `reason` | robots_unreachable, content_signal_search_no (news-robots-checker) | news-robots-checker (row has 'same fields' as the message (6.2 L117); not in 6.3's list) |  |  |
| `robots` |  | news-robots-checker (upsert of the host's row before the message is produced (5.2 step 9, 8 L138); includes the compiled rules so fetching services can test a...) |  |  |
| `rsl` |  | news-robots-checker (upsert of the host's row before the message is produced (5.2 step 9, 8 L138)) |  |  |
| `status` | allowed, disallowed, paywalled, blocked (news-robots-checker) | news-robots-checker (upsert of the host's row before the message is produced (5.2 step 9, 8 L138)) | news-article-extractor, news-comments-fetcher, news-feed-poller, news-homepage-differ, news-sitemap-poller |  |
| `usage_signals` | yes, no, unset (news-robots-checker) | news-robots-checker (upsert of the host's row before the message is produced (5.2 step 9, 8 L138)) |  |  |

#### `cursors`

In CONVENTIONS: yes. Named by 64 PRD(s).

- Table-level writers: aggregator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-search, fb-post-comments-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-feed-poller, news-homepage-differ, news-sitemap-poller, normalize-item, raw-archiver, retention-purger, store-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-timeline-poller, yt-comments-fetcher, yt-keyword-search, yt-pubsub-receiver, yt-replies-fetcher, yt-text-purger, yt-uploads-reconciler, yt-web-search-bridge
- Table-level readers: aggregator, fb-backfill, fb-client-webhook-receiver, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-search, ig-account-media-poller, ig-account-resolver, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-webhook-receiver, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-own-comments-fetcher, li-post-search, news-feed-poller, news-homepage-differ, news-sitemap-poller, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-timeline-poller, yt-comments-fetcher, yt-keyword-search, yt-pubsub-receiver, yt-replies-fetcher, yt-uploads-reconciler, yt-web-search-bridge
- Mention only: fb-reactions-fetcher, news-comments-fetcher, news-site-resolver, tt-video-stats-refresher, yt-channel-resolver, yt-video-details-fetcher
- Keys as stated: (source × ig-hashtag-search) in 6.1; 'per hashtag × edge' in 6.3; (source × ig-keyword-search); (source × ig-mentions-fetcher); (source × ig-webhook-receiver); (source × service); (source, service); (source_id, fb-post-comments-fetcher); (source_id, news-feed-poller); (source_id, news-homepage-differ); (source_id, news-sitemap-poller); (source_id, service); (source_id, tt-profile-videos-poller); (source_id, x-replies-fetcher); (source_id, yt-comments-fetcher); (source_id, yt-pubsub-receiver); (source_id, yt-replies-fetcher); (source_id, yt-uploads-reconciler); keyword x service (row per keyword); one row per hashtag; one row per keyword rule (rule x yt-keyword-search); one row per rule; one row per rule for service = web-gdelt-poller (5.1 L41); one row per rule for service = web-search-mojeek (5.1 L42); one row per rule for service = web-search-perplexity (5.1 L41); one row per source for rotation plus a second reconciliation row with service = li-client-posts-poller:reconcile; per rule; rule x yt-web-search-bridge; service = yt-text-purger (no source_id stated)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `7-day set of sent ids (hashed)` |  | yt-web-search-bridge (ids not re-sent while in the set) | yt-web-search-bridge |  |
| `checked_at` |  | ig-webhook-receiver (daily subscription check) |  |  |
| `consecutive_errors` |  | fb-backfill<br>fb-client-webhook-receiver<br>fb-group-posts-poller (set to 0 after ack)<br>fb-keyword-search (set to 0 after ack)<br>fb-page-feed-poller (set to 0 after Redpanda ack)<br>fb-page-search<br>fb-post-comments-fetcher (health fields updated in step 8)<br>ig-account-media-poller (reset to 0 after ack)<br>ig-account-resolver (reset to 0)<br>ig-comments-fetcher (reset to 0)<br>ig-hashtag-search<br>ig-keyword-search (reset to 0 after ack)<br>ig-mentions-fetcher (reset to 0 after ack)<br>ig-own-comments-fetcher (reset to 0)<br>li-client-posts-poller (reset to 0 after Redpanda acknowledges)<br>li-company-posts-poller (reset to 0 after Redpanda acknowledges)<br>li-own-comments-fetcher<br>li-post-comments-fetcher<br>li-post-search<br>news-feed-poller (set to 0 after a successful poll)<br>news-homepage-differ<br>news-sitemap-poller<br>tg-bot-channel-receiver<br>tg-channel-posts-poller (set to 0 on success; repeated unreadable-channel failures raise it)<br>tg-discussion-receiver<br>tg-message-search<br>tt-client-videos-fetcher (reset to 0 after Redpanda acknowledges)<br>tt-hashtag-feed-poller (not stated)<br>tt-keyword-search (not stated)<br>tt-profile-videos-poller (reset to 0 after Redpanda acknowledges)<br>web-gdelt-poller<br>web-search-mojeek<br>web-search-perplexity<br>x-full-archive-search (own row)<br>x-recent-search<br>x-replies-fetcher<br>x-user-timeline-poller (set to 0 after success)<br>yt-comments-fetcher<br>yt-keyword-search<br>yt-uploads-reconciler (= 0 on success)<br>yt-web-search-bridge | ig-hashtag-search, tg-channel-posts-poller |  |
| `cursor` | JSON (news-feed-poller); JSON (news-homepage-differ); JSON (news-sitemap-poller); JSON (tg-discussion-receiver); JSON (tt-hashtag-feed-poller); JSON (tt-keyw... | aggregator (recompute progress)<br>analysis-entities (re-run and alias re-link progress)<br>analysis-media (rerun progress)<br>analysis-sentiment (rerun progress)<br>analysis-topics (rerun progress)<br>fb-backfill (own row (source_id, fb-backfill): oldest created_time reached, written after each page is acknowledged by Redpanda; read at start as the ...)<br>fb-backfill (row (source_id, fb-page-feed-poller): written on completion as the newest created_time seen, or window_end when the feed returned nothing)<br>fb-client-webhook-receiver (updated after the raw.items acknowledgement)<br>fb-group-posts-poller (after Redpanda ack, set to the newest created_time seen)<br>fb-keyword-search (after Redpanda ack, per-variant cursors updated)<br>fb-page-feed-poller (after Redpanda ack, set to the newest created_time seen; read to compute since = cursor - 24 h)<br>fb-page-search (ISO timestamp of the last run start; written after Redpanda acknowledges)<br>ig-account-media-poller (set to the newest `timestamp` seen, only after Redpanda acknowledges)<br>ig-hashtag-search (advanced to the newest timestamp seen only on Redpanda acknowledgement)<br>ig-keyword-search (advanced to the newest timestamp seen after Redpanda acknowledges)<br>ig-mentions-fetcher (each edge's since timestamp advanced to the newest timestamp seen only after Redpanda acknowledges; poll_started_at kept for the due time)<br>keyword-matcher (rematch progress)<br>li-client-posts-poller (read at job start; set after Redpanda acknowledges to the newest lastModifiedAt seen)<br>li-company-posts-poller (read at job start; set after Redpanda acknowledges to the newest post time seen)<br>li-post-search (timestamp of the newest post seen; advanced only after acknowledgement; unchanged on skip or failed run)<br>news-feed-poller (JSON map from feed URL to {etag, last_modified, newest_published_at, first50_hash}; stored only after Redpanda acknowledgement)<br>news-homepage-differ (JSON {etag, last_modified, page_hash, link_hashes (last three snapshots), sections, render}; moves only after Redpanda acknowledges)<br>news-sitemap-poller (JSON map from sitemap URL to {etag, last_modified, newest_date, urls_hash}; advanced only after Redpanda acknowledges)<br>normalize-item (replay progress)<br>raw-archiver (replay progress)<br>retention-purger (last cut-off)<br>tg-bot-channel-receiver (set after Redpanda ack to the newest message id stored; cursors is listed under reads in 6.1)<br>tg-channel-posts-poller (read to build since (oldest cursor in the batch) and to drop older items; set after Redpanda acknowledges to the newest post time seen; n...)<br>tg-channel-resolver (not stated; holds the last profile time)<br>tg-discussion-receiver (written at onboarding step two with the linked channel's chat id and source_id; also holds the newest message id stored)<br>tg-message-search (advanced after Redpanda acknowledges the batch)<br>tt-client-videos-fetcher (read for incremental reads; set after Redpanda acknowledges; does not advance when the produce fails)<br>tt-hashtag-feed-poller (advanced after Redpanda acknowledges the batch)<br>tt-keyword-search (advanced after Redpanda acknowledges the batch)<br>tt-profile-videos-poller (read at job start; set after Redpanda acknowledges; does not advance when the produce fails)<br>web-gdelt-poller (advanced to the run's start on Redpanda's acknowledgement)<br>web-search-mojeek (advanced on Redpanda's acknowledgement)<br>x-filtered-stream (= X rule id; coverage rows upserted after X confirms, cleared for uncovered sources (and on retired / budget shedding))<br>x-full-archive-search (x-user-timeline-poller's row: raised to the highest id read (64-bit integer comparison; never lowered), after the Redpanda ack and before...)<br>x-recent-search (= newest_id per rule (the next since_id); advanced to meta.newest_id only after the Redpanda acknowledgement)<br>x-user-timeline-poller (= highest stored post id as a decimal string (the next since_id), compared as 64-bit integers; advanced only after the Redpanda ack; empt...)<br>yt-keyword-search (RFC 3339 timestamp of the last successful run start; advanced after Redpanda acknowledges the batch)<br>yt-pubsub-receiver (newest updated)<br>yt-text-purger (cursor = cut-off, set at the end of a run)<br>yt-uploads-reconciler (ISO publishedAt of the newest video already stored; set after acknowledgement to the newest publishedAt seen) | fb-backfill, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-search, ig-account-media-poller, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, li-client-posts-poller, li-company-posts-poller, li-post-search, news-feed-poller, news-homepage-differ, news-sitemap-poller, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, x-recent-search, x-user-timeline-poller, yt-keyword-search, yt-pubsub-receiver, yt-uploads-reconciler | ig-account-resolver, li-own-comments-fetcher |
| `due time` |  | ig-keyword-search (set from the START of the last search (`poll_started_at + interval`); a failed job keeps its due time) | ig-keyword-search |  |
| `health (columns not named)` |  | fb-group-comments-fetcher ('cursors health' updated with the report) |  |  |
| `highest id` |  | x-full-archive-search (own progress row) | x-full-archive-search |  |
| `job_id` |  | x-full-archive-search (own progress row) | x-full-archive-search |  |
| `last run time` |  | yt-web-search-bridge | yt-web-search-bridge |  |
| `last_error` | hashtag_id_unknown (tt-hashtag-feed-poller) | fb-backfill<br>fb-client-webhook-receiver<br>fb-group-posts-poller<br>fb-keyword-search<br>fb-page-feed-poller<br>fb-page-search<br>fb-post-comments-fetcher (health fields updated in step 8)<br>ig-account-media-poller<br>ig-account-resolver<br>ig-comments-fetcher<br>ig-keyword-search<br>ig-mentions-fetcher<br>ig-own-comments-fetcher<br>li-client-posts-poller<br>li-company-posts-poller<br>li-own-comments-fetcher<br>li-post-comments-fetcher<br>li-post-search<br>news-feed-poller<br>news-homepage-differ<br>news-sitemap-poller<br>tg-bot-channel-receiver<br>tg-channel-posts-poller<br>tg-discussion-receiver<br>tg-message-search<br>tt-client-videos-fetcher (not stated)<br>tt-hashtag-feed-poller (the job ends with last_error = hashtag_id_unknown when the id is not resolvable)<br>tt-keyword-search (not stated)<br>tt-profile-videos-poller (not stated)<br>web-gdelt-poller<br>web-search-mojeek<br>web-search-perplexity<br>x-filtered-stream (rule rejection reason; the source stays on poller rotation)<br>x-full-archive-search (own row)<br>x-recent-search<br>x-replies-fetcher<br>x-user-timeline-poller<br>yt-comments-fetcher<br>yt-keyword-search (recorded on HTTP 400 for the term)<br>yt-uploads-reconciler |  |  |
| `last_run_started_at` |  | web-search-perplexity |  |  |
| `last_success_at` |  | fb-backfill<br>fb-client-webhook-receiver (= last successful audit; the audit orders Pages by oldest last_success_at then tier)<br>fb-group-posts-poller (after Redpanda ack)<br>fb-keyword-search (after ack)<br>fb-page-feed-poller (after Redpanda ack)<br>fb-page-search<br>fb-post-comments-fetcher (health fields updated in step 8)<br>ig-account-media-poller (after ack)<br>ig-account-resolver (for a registered source after a refresh)<br>ig-comments-fetcher (after Redpanda acknowledges)<br>ig-keyword-search (after ack)<br>ig-mentions-fetcher (after ack)<br>ig-own-comments-fetcher (after Redpanda acknowledges)<br>ig-webhook-receiver<br>li-client-posts-poller (set after Redpanda acknowledges)<br>li-company-posts-poller (set after Redpanda acknowledges)<br>li-own-comments-fetcher<br>li-post-comments-fetcher<br>li-post-search<br>news-feed-poller<br>news-homepage-differ<br>news-sitemap-poller<br>tg-bot-channel-receiver<br>tg-channel-posts-poller (after Redpanda acknowledges)<br>tg-discussion-receiver<br>tg-message-search<br>tt-client-videos-fetcher (set after Redpanda acknowledges)<br>tt-hashtag-feed-poller (not stated)<br>tt-keyword-search (not stated)<br>tt-profile-videos-poller (set after Redpanda acknowledges)<br>web-gdelt-poller<br>web-search-mojeek<br>web-search-perplexity<br>x-filtered-stream<br>x-full-archive-search (own row)<br>x-recent-search<br>x-replies-fetcher (after the Redpanda ack)<br>x-user-timeline-poller<br>yt-comments-fetcher (updated only after Redpanda acknowledges)<br>yt-keyword-search<br>yt-pubsub-receiver (last verified lease)<br>yt-uploads-reconciler (set after acknowledgement; most-stale-first ordering uses the oldest last_success_at) | fb-client-webhook-receiver, yt-uploads-reconciler |  |
| `next_search_at` |  | fb-page-search (kept per keyword in cursors; = run_start + 7 days, from the START of the last run) | fb-page-search |  |
| `next_token` |  | x-full-archive-search (own progress row; if X rejects it the job restarts with end_time = the oldest created_at read) | x-full-archive-search |  |
| `oldest created_at` |  | x-full-archive-search (own progress row) | x-full-archive-search |  |
| `paid reads` |  | x-full-archive-search (own progress row) | x-full-archive-search |  |
| `reconciliation due time` |  | ig-webhook-receiver (`started_at + 24 h` (+ 7 d for dormant), set from the START of the last reconciliation, written when both fetchers report) | ig-webhook-receiver |  |
| `refresh_due_at` |  | ig-account-resolver (direct write by the service: `refresh_started_at + 30 days`, set from the START of the last refresh; a failed refresh keeps its due time) | ig-account-resolver |  |
| `results_last_run` |  | web-search-perplexity |  |  |
| `service` | aggregator (aggregator); analysis-entities (analysis-entities); analysis-media (analysis-media); analysis-sentiment (analysis-sentiment); analysis-topics (an... | aggregator (recompute progress)<br>analysis-entities (re-run and alias re-link progress)<br>analysis-media (rerun progress)<br>analysis-sentiment (rerun progress)<br>analysis-topics (rerun progress)<br>fb-backfill (own row (source_id, fb-backfill); also writes the fb-page-feed-poller row)<br>keyword-matcher (rematch progress)<br>li-client-posts-poller (a second cursors row tracks the daily reconciliation under service li-client-posts-poller:reconcile)<br>normalize-item (replay progress row)<br>raw-archiver (replay progress)<br>retention-purger (per-sweep watermark per class)<br>store-writer (replay progress)<br>yt-comments-fetcher (row key)<br>yt-text-purger | fb-backfill, fb-client-webhook-receiver, fb-page-feed-poller, fb-page-search, ig-account-media-poller, ig-account-resolver, li-client-posts-poller, web-gdelt-poller, web-search-mojeek, web-search-perplexity, yt-comments-fetcher |  |
| `source_id` |  | yt-comments-fetcher (row per (source_id, yt-comments-fetcher)) | fb-backfill, fb-client-webhook-receiver, fb-page-feed-poller, ig-account-media-poller, ig-account-resolver, yt-comments-fetcher |  |
| `subscription state` |  | ig-webhook-receiver (daily subscription check) | ig-webhook-receiver |  |

#### `decisions`

In CONVENTIONS: yes. Named by 9 PRD(s).

- Table-level writers: fb-page-search, news-dedup, poster-resolver, qualifier
- Table-level readers: fb-page-search, li-org-resolver, news-site-resolver, poster-resolver, qualifier, tg-channel-resolver, tg-message-search
- Mention only: registry-writer

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `candidate_key` |  | qualifier (insert; read for duplicates and rejection memory) | poster-resolver, qualifier |  |
| `client_ids` |  | qualifier |  |  |
| `decision` | add, reject, review, queued, mention_only, tier_down, retire, tier_change (qualifier) | qualifier |  |  |
| `decision_id` |  | qualifier (insert per decision; deterministic) |  |  |
| `emission date` |  | fb-page-search (pruned after 7 days) | fb-page-search |  |
| `emitted Page id` |  | fb-page-search (read to drop ids emitted for this keyword within 7 days) | fb-page-search |  |
| `expires_at` |  | qualifier (180-day expiry on rejections) |  |  |
| `keyword` |  | fb-page-search (per-keyword set) | fb-page-search |  |
| `kind` | fb_page_search_emitted (fb-page-search) | fb-page-search (rows of the per-keyword emitted-Page-id set) |  |  |
| `payload` |  | qualifier |  |  |
| `published_at` |  | qualifier (outbox column, same transaction as the registry.decisions publish) |  |  |
| `reason` |  | qualifier |  |  |
| `rejection and its age (column names not stated)` |  |  | li-org-resolver |  |
| `rule_hit` |  | qualifier |  |  |

#### `deletion_requests`

In CONVENTIONS: yes. Named by 6 PRD(s).

- Table-level writers: deletion-propagator, retention-purger
- Table-level readers: deletion-propagator, raw-archiver, retention-purger, store-writer, x-compliance-sync, yt-text-purger
- Keys as stated: deletion_id

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `author's handle or profile URL` |  | retention-purger (erased after hashing) |  |  |
| `completion status (column not named)` | completed (yt-text-purger) |  | yt-text-purger |  |
| `deletion_id` |  | deletion-propagator (upsert keyed by deletion_id (status received)) | deletion-propagator, retention-purger, x-compliance-sync |  |
| `item_id` |  |  | store-writer |  |
| `notice status` | delivered, undelivered (deletion-propagator) | deletion-propagator |  |  |
| `requester's contact` |  | retention-purger (intake from the deletion channel) |  |  |
| `sla_met` | boolean (deletion-propagator) | deletion-propagator |  |  |
| `status` | completed (retention-purger); completed (x-compliance-sync); done (store-writer); received, resolved, hidden, erased, recomputed, notified, verified, complet... | deletion-propagator (each transition stored) | deletion-propagator, retention-purger, store-writer, x-compliance-sync |  |
| `step` |  | deletion-propagator | deletion-propagator |  |
| `verification` | JSON audit record (deletion-propagator) | deletion-propagator (written at completion) |  |  |
| `verification.completed_at` | string (ISO 8601) (deletion-propagator) | deletion-propagator |  |  |
| `verification.deletion_id` | string (deletion-propagator) | deletion-propagator |  |  |
| `verification.due_at` | string (ISO 8601) (deletion-propagator) | deletion-propagator |  |  |
| `verification.found` | integer (deletion-propagator) | deletion-propagator |  |  |
| `verification.items_resolved` | integer (deletion-propagator) | deletion-propagator |  |  |
| `verification.mode` | string (deletion-propagator); delete, purge_text (deletion-propagator) | deletion-propagator |  |  |
| `verification.notices[]` | array of objects (deletion-propagator) | deletion-propagator |  |  |
| `verification.notices[].client_id` | string (uuid) (deletion-propagator) | deletion-propagator |  |  |
| `verification.notices[].notice_status` | string (deletion-propagator); delivered, undelivered (deletion-propagator) | deletion-propagator |  |  |
| `verification.reason` | string (deletion-propagator) | deletion-propagator |  |  |
| `verification.retention_class` | string (deletion-propagator) | deletion-propagator |  |  |
| `verification.signal_at` | string (ISO 8601) (deletion-propagator) | deletion-propagator |  |  |
| `verification.sla_met` | boolean (deletion-propagator) | deletion-propagator |  |  |
| `verification.verification[]` | array of objects (deletion-propagator) | deletion-propagator |  |  |
| `verification.verification[].check` | string (deletion-propagator); archive_rewrite, text_index, aggregator_job (deletion-propagator) | deletion-propagator |  |  |
| `verification.verification[].hits` | integer (deletion-propagator) | deletion-propagator |  |  |
| `verification.verification[].lines_with_ids` | integer (deletion-propagator) | deletion-propagator |  |  |
| `verification.verification[].objects` | integer (deletion-propagator) | deletion-propagator |  |  |
| `verification.verification[].query` | string (deletion-propagator) | deletion-propagator |  |  |
| `verification.verification[].result` | integer (deletion-propagator) | deletion-propagator |  |  |
| `verification.verification[].status` | string (deletion-propagator); done (deletion-propagator) | deletion-propagator |  |  |

#### `keywords`

In CONVENTIONS: yes. Named by 19 PRD(s).

- Table-level writers: none
- Table-level readers: fb-keyword-search, fb-page-search, ig-keyword-search, keyword-matcher, li-post-search, poster-resolver, qualifier, store-writer, tg-message-search, tt-keyword-search, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-full-archive-search, x-recent-search, yt-keyword-search, yt-web-search-bridge
- Mention only: lang-dialect-id
- Keys as stated: keyword_id

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `(unnamed) Arabic forms` |  |  | web-gdelt-poller |  |
| `(unnamed) context and intent terms` |  |  | web-search-mojeek |  |
| `(unnamed) context terms` |  |  | web-search-perplexity |  |
| `(unnamed) generated-form confirmation flag` |  |  |  | web-search-perplexity |
| `(unnamed) intent terms` |  |  | web-search-perplexity |  |
| `(unnamed) Latin forms` |  |  | web-gdelt-poller |  |
| `(unnamed) Latin, Arabic and Sorani forms` |  |  | web-search-mojeek, web-search-perplexity |  |
| `(unnamed) listed misspellings` |  |  | web-search-mojeek, web-search-perplexity |  |
| `(unnamed) priority flag` |  |  | web-search-mojeek, web-search-perplexity |  |
| `(unnamed) Sorani forms` |  |  | web-gdelt-poller |  |
| `client ids` |  |  | fb-page-search |  |
| `client_id` |  |  | keyword-matcher |  |
| `client_ids` |  |  | yt-keyword-search |  |
| `client_ids[]` |  |  | web-search-mojeek, web-search-perplexity |  |
| `enabled` |  |  | keyword-matcher |  |
| `exclusions` | array of {text, lang} (keyword-matcher) |  | keyword-matcher |  |
| `Facebook in scope` |  |  | fb-page-search |  |
| `forms` | jsonb array of {form_id, text, lang: ar\|ckb\|en, kind: term\|handle\|hashtag, boundary: clitic\|word\|exact} (keyword-matcher) |  | keyword-matcher |  |
| `keyword texts and variants (column names not stated)` |  |  | li-post-search |  |
| `keyword_id` | uuid (example) (keyword-matcher) |  | keyword-matcher |  |
| `label` |  |  | keyword-matcher |  |
| `language` |  |  | yt-keyword-search |  |
| `purpose` | reputation, service_quality, (others) (keyword-matcher) |  | keyword-matcher |  |
| `query strings` |  |  | tt-keyword-search |  |
| `rematch_days` |  |  | keyword-matcher |  |
| `terms` |  |  | ig-keyword-search, yt-keyword-search |  |
| `updated_at` |  |  | keyword-matcher, store-writer |  |
| `variant list (ranked; column name not stated)` |  |  | fb-keyword-search |  |
| `variants` |  |  | fb-page-search, tt-keyword-search, yt-keyword-search, yt-web-search-bridge |  |
| `version` |  |  | keyword-matcher |  |

#### `retention_classes`

In CONVENTIONS: yes. Named by 11 PRD(s).

- Table-level writers: none
- Table-level readers: aggregator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, normalize-item, raw-archiver, retention-purger, store-writer, yt-text-purger
- Mention only: tt-client-videos-fetcher

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `anchor` | signal_at, fetched_at, event (retention-purger) |  | retention-purger |  |
| `class` | x_24h_sync, youtube_30d_text, linkedin_48h, meta_on_request, vendor_agreed, news_excerpt (retention-purger) |  | retention-purger |  |
| `clock` | 24 hours, 30 days, 48 hours / 24 hours, event, 24 months, 7 days (retention-purger) |  | retention-purger |  |
| `content_ttl` |  |  | store-writer |  |
| `executor` | deletion-propagator, yt-text-purger, none (retention-purger) |  | retention-purger |  |
| `mode` | delete, purge_text (retention-purger) |  | retention-purger |  |
| `row_ttl` |  |  | aggregator, store-writer |  |
| `vendor overrides` |  |  | retention-purger |  |

#### `review_queue`

In CONVENTIONS: yes. Named by 21 PRD(s).

- Table-level writers: analysis-entities, analysis-media, analysis-sentiment, analysis-topics, ig-account-media-poller, ig-account-resolver, news-site-resolver, normalize-item, qualifier, search-hit-router, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-recent-search, yt-comments-fetcher, yt-keyword-search, yt-replies-fetcher, yt-web-search-bridge
- Table-level readers: analysis-entities, analysis-media, analysis-sentiment, analysis-topics, normalize-item, qualifier
- Mention only: li-org-resolver, tg-channel-resolver

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `answer` |  | qualifier (add (with tier) \| reject \| mention_only) |  |  |
| `deadline_at` |  | qualifier |  |  |
| `kind` | annotation:media (analysis-media); annotation:sentiment (analysis-sentiment); annotation:topics (analysis-topics); kb_candidate, annotation:entities (analysi... | analysis-entities<br>analysis-media (annotation tasks)<br>analysis-sentiment (rows point to tasks in the annotation tool)<br>analysis-topics (annotation tasks) |  |  |
| `opened_at` |  | qualifier (24-hour clock starts here) | qualifier |  |
| `reason` | not_returned (ig-account-media-poller) | ig-account-media-poller (row inserted on the second consecutive poll with no business_discovery object) |  |  |
| `reviewer` |  | qualifier (from the n8n callback) |  |  |
| `status` |  | qualifier | qualifier |  |

#### `service_runs`

In CONVENTIONS: yes. Named by 85 PRD(s).

- Table-level writers: aggregator, alert-evaluator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, backfill-orchestrator, comment-decay-scheduler, deletion-propagator, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, fb-page-search, fb-post-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, lang-dialect-id, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-org-resolver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-article-extractor, news-comments-fetcher, news-dedup, news-feed-poller, news-homepage-differ, news-robots-checker, news-site-resolver, news-sitemap-poller, normalize-item, poster-resolver, qualifier, raw-archiver, registry-writer, retention-purger, search-hit-router, source-health-canary, store-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-commoncrawl-scanner, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-compliance-sync, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-resolver, x-user-timeline-poller, yt-channel-resolver, yt-comments-fetcher, yt-keyword-search, yt-pubsub-receiver, yt-replies-fetcher, yt-text-purger, yt-uploads-reconciler, yt-video-details-fetcher, yt-web-search-bridge
- Table-level readers: aggregator, alert-evaluator, analysis-sentiment, keyword-matcher, lang-dialect-id, li-notification-receiver, normalize-item, store-writer, web-commoncrawl-scanner, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-user-timeline-poller

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `(unnamed) lag` |  | web-search-perplexity |  |  |
| `(unnamed) scan checkpoint` | JSON (web-commoncrawl-scanner) | web-commoncrawl-scanner (JSON on this service's service_runs row; advanced only after the partition's messages are acknowledged) | web-commoncrawl-scanner |  |
| `(unnamed) spend this month` |  | web-search-perplexity |  |  |
| `Apify run id (column name not stated)` |  | li-company-posts-poller ('The Apify run id goes into the structured logs and service_runs') |  |  |
| `ckb_supported` | true, false (web-search-perplexity) | web-search-perplexity (recorded after the start-up probe with the canary query; set to false when ckb is rejected mid-run) |  |  |
| `connected_at` |  | x-filtered-stream (on connect) |  |  |
| `connection_id` | ULID (x-filtered-stream) | x-filtered-stream (on connect) |  |  |
| `cost_units` |  | li-post-search<br>news-comments-fetcher (as new_count; one request is one unit) |  |  |
| `evaluation time, rules evaluated, alerts fired` |  | alert-evaluator |  |  |
| `event counts (per page, daily; name not stated)` |  | li-notification-receiver (per-page counters updated per event; events received in the last 24 hours read by the check) | li-notification-receiver |  |
| `gap_possible` |  | tg-channel-posts-poller (a channel whose gap exceeds the max-posts cap is marked gap_possible in service_runs and ops is told) |  |  |
| `high-water mark` |  | x-filtered-stream (receipt time up to which every post is acknowledged; persisted with each `service_runs` heartbeat) |  |  |
| `hours touched` |  | aggregator (recorded per pass) |  |  |
| `ids sent` |  | yt-web-search-bridge |  |  |
| `lag of the most overdue refresh job` |  | fb-reactions-fetcher |  |  |
| `last keep-alive` |  | x-filtered-stream |  |  |
| `last run` |  | yt-keyword-search |  |  |
| `last run and errors (column names not stated)` |  | li-org-resolver (written per job) |  |  |
| `last run and lag (column names not stated)` |  | tt-video-stats-refresher (written after Redpanda acknowledges) |  |  |
| `last_event_at (per page)` |  | li-notification-receiver (updated after each event; read by the 24-hour subscription check) | li-notification-receiver |  |
| `last_success_at` |  | aggregator (recorded per pass) | alert-evaluator |  |
| `new_count` |  | li-post-search (written per job)<br>news-comments-fetcher (result row written after Redpanda acknowledges) |  |  |
| `newest_comment_at` |  | news-comments-fetcher (as new_count) |  |  |
| `open gaps with job ids` |  | x-filtered-stream |  |  |
| `outage window` |  | tg-bot-channel-receiver (written when an outage is longer than Telegram keeps updates (receiver_outage)) |  |  |
| `pages` |  | li-post-search<br>news-comments-fetcher (as new_count) |  |  |
| `parse failures` |  | yt-web-search-bridge |  |  |
| `queries per engine` |  | yt-web-search-bridge |  |  |
| `reason` | budget (x-filtered-stream) | x-filtered-stream (e.g. reason = budget when the budget is exhausted) |  |  |
| `rules queried` |  | yt-web-search-bridge |  |  |
| `seen_count` |  | li-post-search<br>news-comments-fetcher (as new_count) |  |  |
| `state` | connected, reconnecting, disconnected (x-filtered-stream) | x-filtered-stream (on connect, on reconnect, past the grace period, on 401/403, and on budget exhaustion) |  |  |
| `subscription state (per page; name not stated)` |  | li-notification-receiver (6.3 lists it with last_event_at and daily event counts '(in service_runs)') | li-notification-receiver |  |
| `terms run and skipped` |  | yt-keyword-search |  |  |
| `thread_id` |  | news-comments-fetcher (as new_count) |  |  |
| `units spent` |  | yt-keyword-search |  |  |
| `URLs parsed` |  | yt-web-search-bridge |  |  |

#### `sources`

In CONVENTIONS: yes. Named by 80 PRD(s).

- Table-level writers: backfill-orchestrator, fb-backfill, fb-client-webhook-receiver, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, ig-account-media-poller, ig-hashtag-search, ig-mentions-fetcher, ig-webhook-receiver, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-own-comments-fetcher, li-post-search, news-feed-poller, news-homepage-differ, news-sitemap-poller, registry-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-full-archive-search, x-recent-search, x-user-timeline-poller, yt-uploads-reconciler
- Table-level readers: analysis-entities, analysis-media, analysis-sentiment, analysis-topics, backfill-orchestrator, comment-decay-scheduler, fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, fb-page-search, fb-post-comments-fetcher, fb-reactions-fetcher, ig-account-media-poller, ig-account-resolver, ig-comments-fetcher, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-org-resolver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-article-extractor, news-comments-fetcher, news-dedup, news-feed-poller, news-homepage-differ, news-robots-checker, news-site-resolver, news-sitemap-poller, normalize-item, poster-resolver, qualifier, registry-writer, retention-purger, search-hit-router, source-health-canary, store-writer, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-commoncrawl-scanner, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-compliance-sync, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-resolver, x-user-timeline-poller, yt-channel-resolver, yt-comments-fetcher, yt-keyword-search, yt-pubsub-receiver, yt-replies-fetcher, yt-text-purger, yt-uploads-reconciler, yt-video-details-fetcher, yt-web-search-bridge
- Keys as stated: unique index on (platform, platform_id); ON CONFLICT (platform, platform_id) DO UPDATE

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `(unnamed) degraded reason` | query_rejected (web-gdelt-poller) | web-gdelt-poller (not stated) |  |  |
| `(unnamed) host and registrable domain` |  |  | web-commoncrawl-scanner |  |
| `(unnamed) registered handles and ids by platform` |  |  | search-hit-router |  |
| `(unnamed) registered news domains` |  |  | search-hit-router |  |
| `added_at` |  | registry-writer (now() on insert) | backfill-orchestrator, fb-backfill, x-full-archive-search |  |
| `added_by` | client (fb-client-webhook-receiver); client (li-client-posts-poller); client (tg-bot-channel-receiver); qualifier (news-site-resolver); qualifier, client, op... | registry-writer (from the decision's origin) |  | fb-client-webhook-receiver, li-client-posts-poller, news-site-resolver, tg-bot-channel-receiver |
| `backfill_status` | capped (news-sitemap-poller); capped (tg-bot-channel-receiver); capped (tg-discussion-receiver); done, capped (ig-hashtag-search); done, capped (yt-pubsub-re... | backfill-orchestrator (direct write by the orchestrator; done/capped and next_poll_at in one transaction)<br>fb-backfill (set directly by this service: running when the job is consumed; done or capped on completion; capped after 5 failed attempts or when the ...)<br>fb-group-posts-poller (read: filter backfill_status in (done, capped); on backfill-job completion 'backfill_status becomes done or capped' (passive; writer not ...)<br>fb-keyword-search (read: filter backfill_status in (done, capped); after the backfill job 'backfill_status becomes done or capped' (13.8: its backfill job s...)<br>registry-writer ('pending' on insert only)<br>tg-bot-channel-receiver ('At onboarding backfill_status is set to capped (route cap: zero days)'; the writer is not named)<br>tg-channel-posts-poller (after the backfill job 'the service sets `done` or `capped` and `next_poll_at = now()`'; write mechanism not stated)<br>tg-discussion-receiver ('backfill_status is capped from onboarding'; the writer is not named)<br>tt-hashtag-feed-poller (written by this service: moves pending -> running -> done or capped during the first job after add)<br>tt-keyword-search (this service moves it pending -> running -> done (or capped) during the deep search) | backfill-orchestrator, fb-backfill, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, ig-account-media-poller, ig-keyword-search, ig-mentions-fetcher, li-client-posts-poller, li-company-posts-poller, news-sitemap-poller, tg-channel-posts-poller, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, x-filtered-stream, x-user-timeline-poller, yt-pubsub-receiver, yt-uploads-reconciler | ig-hashtag-search, li-post-search, news-site-resolver, tt-user-resolver, x-full-archive-search |
| `client_ids` |  | registry-writer (insert; on conflict array union) | fb-backfill, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-reactions-fetcher, ig-account-media-poller, ig-comments-fetcher, ig-keyword-search, keyword-matcher, li-company-posts-poller, li-notification-receiver, li-post-search, retention-purger, tt-hashtag-feed-poller, tt-keyword-search, x-replies-fetcher, yt-comments-fetcher, yt-pubsub-receiver, yt-replies-fetcher | x-recent-search |
| `country_signals` |  | registry-writer (insert) |  | news-site-resolver |
| `display_name` |  | registry-writer (insert; updated on conflict) |  | news-site-resolver |
| `followers` |  | registry-writer (insert; updated on conflict)<br>tg-bot-channel-receiver (refreshed from getChatMemberCount at the daily check; write mechanism not stated) | yt-pubsub-receiver | fb-group-posts-poller, fb-page-resolver, ig-account-resolver, news-site-resolver, tg-channel-posts-poller, x-user-resolver, yt-channel-resolver |
| `handle` |  | registry-writer (insert; updated on conflict) | ig-account-media-poller, tg-channel-posts-poller, x-filtered-stream, x-full-archive-search | news-site-resolver |
| `health` | blocked (backfill-orchestrator); blocked (li-notification-receiver); blocked (news-robots-checker); blocked (web-search-mojeek); blocked (web-search-perplexi... | fb-client-webhook-receiver (set by this service when the daily subscription audit fails)<br>fb-group-posts-poller (read: filter health != blocked, stop if blocked, fallback selects the other vendor; listed in 6.3 as this service's state)<br>fb-keyword-search (read: filter health != blocked, stop if blocked; fallback -> other vendor if it offers search; 6.3 lists it as this service's state)<br>fb-page-feed-poller (read: scheduler filter health != blocked and job stops if health = blocked; write: token expiry sets health = blocked (writer not named e...)<br>ig-account-media-poller (read: scheduler filter `health != blocked`, job stops if blocked; write: `health = blocked` when no client in client_ids has a healthy to...)<br>ig-mentions-fetcher (read: filter `health != blocked`, stop if blocked; write: a revoked token sets `health = blocked`)<br>ig-webhook-receiver (set degraded when a lost subscription cannot be re-created (mechanism not stated))<br>li-client-posts-poller (read by the scheduler (health != blocked) and at job start (stop if blocked); health also read 'through the SDK canary hook'; set to bloc...)<br>li-company-posts-poller (read by the scheduler (health != blocked) and through the SDK canary hook; set to degraded by this service when a page no longer resolves...)<br>li-notification-receiver (on enrichment 401/403: 'token degraded or page blocked as in li-own-comments-fetcher')<br>li-own-comments-fetcher (read at job start (stop if blocked) and through the SDK canary hook; a 403 on one page while the token works elsewhere blocks only that p...)<br>registry-writer ('ok' on insert; bulk UPDATE ... WHERE route = $1 AND vendor = $2 AND platform = $3 on health_change)<br>tg-bot-channel-receiver (lost administrator role (daily check or my_chat_member) or HTTP 403 on one chat sets blocked; re-adding the bot restores ok; a missing ca...)<br>tg-discussion-receiver (removal or HTTP 403 on one group -> blocked; changed link or privacy mode on -> degraded with the reason; a missing hourly canary comment...)<br>tt-client-videos-fetcher (read: selection `health != blocked`, stop at job start if blocked; write: this service sets `blocked` when a 401 refresh fails and on 403...)<br>tt-hashtag-feed-poller (passive in the PRD: 'the source goes to `health = degraded`' when the hashtag id is not resolvable; setter not stated)<br>tt-profile-videos-poller (read: selection health != blocked, stop at job start if blocked; write: a creator the vendor reports as private or not found is marked he...)<br>web-gdelt-poller (scheduler selects health != blocked; a non-JSON 200 marks the rule degraded (write mechanism not stated))<br>x-compliance-sync (indirect: the SDK canary hook asks source-health-canary to set `health = blocked`, and back to `ok` when X stops reporting the source)<br>x-full-archive-search (read: stop if health = blocked; write: health = blocked when the account is not found, suspended or protected (method not stated))<br>x-recent-search (read: scheduler filter health != blocked; write: a rule whose query is rejected (HTTP 400) 'is parked `degraded`')<br>x-user-timeline-poller (read: filter health != blocked and stop if blocked; write: health = blocked when the account is not found, suspended or protected)<br>yt-pubsub-receiver (via request to registry-writer: degraded after 5 failed subscription attempts)<br>yt-uploads-reconciler (read: stop if blocked, scheduler skips blocked; write: health = degraded on HTTP 404 on the playlist) | backfill-orchestrator, comment-decay-scheduler, fb-backfill, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-post-comments-fetcher, ig-account-media-poller, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, li-client-posts-poller, li-company-posts-poller, li-own-comments-fetcher, li-post-search, news-feed-poller, news-homepage-differ, news-sitemap-poller, source-health-canary, tg-channel-posts-poller, tt-client-videos-fetcher, tt-keyword-search, tt-profile-videos-poller, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-full-archive-search, x-recent-search, x-replies-fetcher, x-user-timeline-poller, yt-comments-fetcher, yt-replies-fetcher, yt-text-purger, yt-uploads-reconciler | li-org-resolver, li-post-comments-fetcher, news-robots-checker, news-site-resolver |
| `lang_share` |  | registry-writer (insert) |  | news-site-resolver |
| `last_hit_at` |  | keyword-matcher (direct write: greatest(current, hit_at) for the item's source_id and author_source_id, coalesced to one write per source per minute)<br>x-recent-search (after the Redpanda ack) | qualifier | registry-writer |
| `last_polled_at` |  | fb-group-posts-poller (after Redpanda ack)<br>fb-keyword-search (after Redpanda ack)<br>fb-page-feed-poller (set by this service after Redpanda ack (5.2 step 6))<br>ig-account-media-poller (after Redpanda acknowledges (5.2 step 6))<br>ig-hashtag-search (set on Redpanda ack)<br>ig-keyword-search (set after Redpanda acknowledges (5.2 step 7))<br>ig-mentions-fetcher (set after Redpanda acknowledges)<br>li-client-posts-poller (set after Redpanda acknowledges (5.2 step 6))<br>li-company-posts-poller (set after Redpanda acknowledges)<br>news-feed-poller (set after Redpanda acknowledgement (5.2 step 7))<br>news-homepage-differ (set at 5.2 step 7)<br>news-sitemap-poller (listed under 6.3 State)<br>tg-bot-channel-receiver (not stated (listed as state in 6.3))<br>tg-channel-posts-poller (set after Redpanda acknowledges; mechanism not stated)<br>tg-discussion-receiver (not stated (listed as state))<br>tt-client-videos-fetcher (set after Redpanda acknowledges)<br>tt-hashtag-feed-poller (written by this service)<br>tt-keyword-search (not stated)<br>tt-profile-videos-poller (set after Redpanda acknowledges)<br>web-gdelt-poller (updated on Redpanda's acknowledgement (mechanism not stated))<br>web-search-mojeek (updated on Redpanda's acknowledgement (mechanism not stated))<br>web-search-perplexity (updated on Redpanda's acknowledgement (mechanism not stated))<br>x-recent-search (after the Redpanda ack)<br>x-user-timeline-poller (after the Redpanda ack)<br>yt-uploads-reconciler (direct write after acknowledgement) | ig-hashtag-search, yt-keyword-search, yt-web-search-bridge | registry-writer |
| `next_poll_at` |  | backfill-orchestrator (set to now() on completion, capped or 'no history route')<br>fb-backfill (set to now() when done or capped is written, so fb-page-feed-poller picks the Page up on its next scan)<br>fb-group-posts-poller (read: next_poll_at <= now(); written after Redpanda ack as poll_started_at + interval; kept on failure, on quota deny and when the flag i...)<br>fb-keyword-search (read: next_poll_at <= now(); written after ack as poll_started_at + interval; failed job keeps it; untouched when the flag is off; = now(...)<br>fb-page-feed-poller (read: next_poll_at <= now(); write by this service after Redpanda ack, = poll_started_at + interval (fixed cadence); failed job keeps the...)<br>ig-account-media-poller (direct write by the service after Redpanda ack: `poll_started_at + interval` (fixed cadence from the START of the last poll); a failed jo...)<br>ig-hashtag-search (set from the start of the last poll on Redpanda ack; on a ledger deny set to the earliest window expiry)<br>li-client-posts-poller (read by the scheduler (<= now()); set after Redpanda acknowledges to poll_started_at + interval (30 min priority list, 60 min others); a ...)<br>li-company-posts-poller (read by the scheduler (<= now()); set after Redpanda acknowledges to poll_started_at + interval; kept on skip (flag off, government-only)...)<br>li-post-search (kept by 'the scheduler', set from the start of the last run; rule stays due on wait-until or deny)<br>news-feed-poller (set after Redpanda acknowledgement from the START of the last poll (poll_started_at + interval); a failed job keeps the old value)<br>news-homepage-differ (set from the START of the last poll (poll_started_at + 60 minutes); a failed job keeps the old value)<br>news-sitemap-poller (set from the START of the last poll (poll_started_at + 60 minutes), advanced after acknowledgement; a failed job keeps the old value)<br>registry-writer (now() on insert only)<br>tg-bot-channel-receiver (set from the START of the last check: check_started_at + 24 h; a failed check keeps its old value; writer mechanism not stated beyond 'is...)<br>tg-channel-posts-poller (set from the START of the last poll (poll_started_at + interval) after Redpanda acknowledges; now() after a backfill; a failed job or a q...)<br>tg-discussion-receiver (next_poll_at = check_started_at + 24 h, from the START of the last check; a failed check keeps its old value; write mechanism not stated)<br>tg-message-search ('The scheduler keeps next_poll_at' per keyword set; the next run is set from the start of the last run; write mechanism not stated)<br>tt-client-videos-fetcher (selection `next_poll_at <= now()`; set after Redpanda acknowledges to poll_started_at + 60 minutes; a failed job and a quota `deny` keep ...)<br>tt-hashtag-feed-poller (scheduler selects next_poll_at <= now(); this service writes it, set from the start of the last poll (fixed cadence))<br>tt-keyword-search (scheduler selects next_poll_at <= now(); next run set from the start of the last run)<br>tt-profile-videos-poller (selection next_poll_at <= now(); set after Redpanda acknowledges to poll_started_at + interval; a failed job keeps the old value)<br>web-gdelt-poller (scheduler selects next_poll_at <= now(); set to run_started_at + 1 h on Redpanda's acknowledgement (write mechanism not stated))<br>web-search-mojeek (scheduler selects next_poll_at <= now(); set from the START of the run plus the interval on Redpanda's acknowledgement (write mechanism n...)<br>web-search-perplexity (scheduler selects next_poll_at <= now(); set to the run start plus the interval on Redpanda's acknowledgement (write mechanism not stated))<br>x-recent-search (read: due when <= now(); write: from the START of the last run (fixed cadence) after the Redpanda ack; a failed job keeps its old value)<br>x-user-timeline-poller (read: due when <= now(); write: poll_started_at + interval after the Redpanda ack; kept on failure or deny; set to now() when a rule is d...)<br>yt-pubsub-receiver (via request to registry-writer: set to now when a lease lapses)<br>yt-uploads-reconciler (direct write after acknowledgement: run_started_at + 24 h (not for backfill); failed or denied job keeps the old value) | fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, ig-account-media-poller, ig-hashtag-search, ig-mentions-fetcher, li-client-posts-poller, li-company-posts-poller, li-post-search, news-feed-poller, news-homepage-differ, news-sitemap-poller, tg-bot-channel-receiver, tg-channel-posts-poller, tg-discussion-receiver, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-recent-search, x-user-timeline-poller, yt-uploads-reconciler | fb-client-webhook-receiver, li-org-resolver, x-full-archive-search |
| `notes` | jsonb (proposed alternative) (news-site-resolver) | fb-backfill (reason for capped)<br>registry-writer |  | news-site-resolver |
| `organization URN mapping (column name not stated)` |  |  | li-notification-receiver |  |
| `owned_by_client` | bool (keyword-matcher); false (li-company-posts-poller); true (fb-client-webhook-receiver); true (ig-mentions-fetcher); true (ig-own-comments-fetcher); true ... | registry-writer (insert) | comment-decay-scheduler, fb-backfill, fb-client-webhook-receiver, fb-page-feed-poller, fb-page-resolver, fb-post-comments-fetcher, fb-reactions-fetcher, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, keyword-matcher, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, qualifier, retention-purger, tt-client-videos-fetcher | li-org-resolver, tg-bot-channel-receiver, tg-discussion-receiver |
| `page identifier (column name not stated)` |  |  | li-company-posts-poller |  |
| `platform` | facebook (fb-group-posts-poller); facebook (fb-keyword-search); facebook (fb-page-feed-poller); instagram (ig-account-media-poller); instagram (ig-hashtag-se... | registry-writer (insert/upsert; part of the unique key) | fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, ig-account-media-poller, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-post-search, news-feed-poller, news-homepage-differ, news-sitemap-poller, tg-channel-posts-poller, tg-message-search, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, web-commoncrawl-scanner, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-recent-search, x-user-timeline-poller, yt-channel-resolver, yt-keyword-search, yt-uploads-reconciler, yt-web-search-bridge | news-site-resolver |
| `platform_id` |  | ig-hashtag-search (if null, call ig_hashtag_search and 'store the id on the source' (mechanism not stated))<br>registry-writer (insert; part of the unique key)<br>tt-hashtag-feed-poller (learned from the newest raw.items video whose hashtag entries carry the name, or from the vendor; stored 'once learned') | fb-group-posts-poller, fb-page-search, ig-hashtag-search, ig-mentions-fetcher, ig-webhook-receiver, tg-message-search, tt-hashtag-feed-poller, x-compliance-sync, x-filtered-stream, x-recent-search, x-user-timeline-poller, yt-comments-fetcher, yt-pubsub-receiver, yt-replies-fetcher | ig-account-resolver, news-site-resolver |
| `retention_class` | news_excerpt (news-site-resolver) | registry-writer (insert) | normalize-item, x-replies-fetcher, yt-comments-fetcher, yt-pubsub-receiver, yt-replies-fetcher, yt-uploads-reconciler, yt-video-details-fetcher | news-site-resolver |
| `route` | amber (fb-group-posts-poller); amber (fb-keyword-search); amber (ig-keyword-search); amber (tg-channel-posts-poller); amber (tg-channel-resolver); amber (tt-... | registry-writer (insert; update decision emits updated with previous) | fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, ig-account-media-poller, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-webhook-receiver, li-client-posts-poller, li-company-posts-poller, source-health-canary, tg-channel-posts-poller, tg-channel-resolver, tt-client-videos-fetcher, tt-profile-videos-poller, tt-video-stats-refresher, x-filtered-stream, x-user-timeline-poller, yt-uploads-reconciler | li-notification-receiver, news-site-resolver, tg-bot-channel-receiver, tg-discussion-receiver |
| `source_id` | uuid (registry-writer) | registry-writer (gen_random_uuid() on insert) | fb-client-webhook-receiver, fb-page-feed-poller, fb-page-resolver, ig-account-media-poller, ig-account-resolver, news-robots-checker, search-hit-router, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tt-client-videos-fetcher, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-video-comments-fetcher, web-gdelt-poller, web-search-mojeek, web-search-perplexity, yt-channel-resolver, yt-keyword-search |  |
| `source_type` | account (x-user-timeline-poller); account, creator (ig-account-media-poller); account, creator (ig-account-resolver); account, creator (ig-mentions-fetcher);... | registry-writer (insert) | backfill-orchestrator, fb-backfill, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, ig-account-media-poller, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, li-client-posts-poller, li-company-posts-poller, li-post-search, tg-channel-posts-poller, tg-message-search, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-full-archive-search, x-recent-search, x-user-timeline-poller, yt-keyword-search, yt-uploads-reconciler, yt-web-search-bridge | ig-account-resolver, news-site-resolver, tg-channel-resolver, tg-discussion-receiver |
| `stored uploads playlist id` |  |  | yt-uploads-reconciler | yt-channel-resolver |
| `tier` | 1 (analysis-sentiment); 1, 2, 3 (web-search-mojeek); 1, 2, 3 (web-search-perplexity); 1, 2, 3 (yt-keyword-search); 1, 2, 3, dormant (li-org-resolver); 1, 2, ... | fb-client-webhook-receiver (changes requested from registry-writer (promotion of a dormant Page back to push; return to reach tier on audit failure or token 401/403)...)<br>fb-keyword-search (read: ordering by tier (the client's priority); write: step 6 'promote or demote dormancy' after ack (mechanism not stated))<br>registry-writer (insert; on conflict least_tier(sources.tier, EXCLUDED.tier) or restore from retired; tier decisions update it) | analysis-sentiment, backfill-orchestrator, comment-decay-scheduler, fb-client-webhook-receiver, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-resolver, ig-account-media-poller, ig-account-resolver, ig-hashtag-search, ig-keyword-search, ig-mentions-fetcher, ig-webhook-receiver, li-company-posts-poller, news-feed-poller, news-homepage-differ, news-robots-checker, news-sitemap-poller, qualifier, search-hit-router, source-health-canary, tg-bot-channel-receiver, tg-channel-posts-poller, tg-discussion-receiver, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, web-commoncrawl-scanner, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-recent-search, x-user-resolver, x-user-timeline-poller, yt-channel-resolver, yt-keyword-search, yt-pubsub-receiver, yt-text-purger, yt-uploads-reconciler, yt-video-details-fetcher, yt-web-search-bridge | fb-backfill, fb-group-comments-fetcher, fb-post-comments-fetcher, ig-comments-fetcher, li-client-posts-poller, li-org-resolver, li-post-search, news-site-resolver, tg-channel-resolver, tt-client-videos-fetcher |
| `url` |  | registry-writer | fb-group-posts-poller | news-site-resolver |
| `vendor` | None (tg-bot-channel-receiver); harvestapi (li-company-posts-poller); sociavault (ig-keyword-search); telemetrio (tg-channel-resolver) | registry-writer (insert; update decision) | ig-keyword-search, li-company-posts-poller, source-health-canary, tt-video-stats-refresher | news-site-resolver, tg-bot-channel-receiver, tg-channel-resolver |

#### `vendor_keys`

In CONVENTIONS: yes. Named by 26 PRD(s).

- Table-level writers: retention-purger, tt-keyword-search
- Table-level readers: fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, ig-comments-fetcher, ig-keyword-search, li-company-posts-poller, li-org-resolver, li-post-comments-fetcher, li-post-search, news-comments-fetcher, quota-governor, retention-purger, tg-bot-channel-receiver, tg-channel-posts-poller, tg-channel-resolver, tg-discussion-receiver, tg-message-search, tt-hashtag-feed-poller, tt-keyword-search, tt-profile-videos-poller, tt-user-resolver, tt-video-comments-fetcher, tt-video-stats-refresher, web-search-mojeek, web-search-perplexity, yt-web-search-bridge

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `(key state; column not named)` | degraded (tt-keyword-search) | tt-keyword-search (on HTTP 401 or 403 'the vendor key is marked `degraded` in `vendor_keys`') |  |  |
| `(unnamed) key degraded mark` | degraded (web-search-mojeek); degraded (web-search-perplexity) | web-search-mojeek (not stated)<br>web-search-perplexity (not stated) |  |  |
| `(unnamed) Mojeek API key` |  |  | web-search-mojeek |  |
| `(unnamed) Perplexity API key` |  |  | web-search-perplexity |  |
| `Apify token (column name not stated)` |  |  | li-company-posts-poller, li-org-resolver, li-post-comments-fetcher, li-post-search |  |
| `plan` | Business, Enterprise, other plans (web-search-mojeek) |  | quota-governor, web-search-mojeek |  |

#### `alert_deliveries`

Not in CONVENTIONS. Named only by **alert-evaluator** (read_write). Keys: one row per alert and channel. Refs: 5.2 L50; 5.3 L69; 6.1 L80; +2 more.

#### `alert_rules`

Not in CONVENTIONS. Named only by **alert-evaluator** (read_write). Refs: 5.2 L47; 5.3 L56; 6.1 L80; +1 more.

Columns as written: `rule_id`; `client_id`; `type` (volume_spike, negative_share, new_high_reach_poster, keyword_first_seen, post...); `keyword_id`; `scope` (keyword, keyword_source); `platform`; `params` (jsonb); `severity`; `channels` (jsonb); `cooldown_minutes`; `enabled`.

#### `alert_watch_items`

Not in CONVENTIONS. Named only by **alert-evaluator** (read_write). Refs: 5.3 L61; 6.1 L80; 6.2 L83; +2 more.

Columns as written: `item id`; `client`; `keyword`; `source`; `followers`; `hit time`.

#### `alerts`

Not in CONVENTIONS. Named only by **alert-evaluator** (read_write). Keys: unique (fingerprint, window_key). Refs: 5.2 L50; 5.3 L67; 6.1 L80; +3 more.

Columns as written: `status` (open, resolved); `fingerprint`; `window key`; `renotify` (boolean).

#### `backfill_runs`

Not in CONVENTIONS. Named only by **backfill-orchestrator** (read_write). Refs: 5.2 L57; 5.2 L59; 6.1 L100; +2 more.

Columns as written: `run_id` (initial); `source_id`; `service`; `requested_by` (system, client, ops); `cap`; `status`; `capped_reason` (route_cap, budget, deadline, failed); `started_at`; `finished_at`; `items_new`; `cost_units`; `attempt`.

#### `brand_assets`

Not in CONVENTIONS. Named only by **analysis-media** (read). Refs: 4 L35; 5.3 L68; 6.1 L84.

#### `budget_history`

Not in CONVENTIONS. Named only by **quota-governor** (write). Refs: 6.3 L107.

#### `budget_reservations`

Not in CONVENTIONS. Named only by **quota-governor** (read_write). Refs: 3 L20; 6.3 L107.

Columns as written: `id`; `tag`; `charge`; `expires`.

#### `cc_hosts_seen`

Not in CONVENTIONS. Named only by **web-commoncrawl-scanner** (read_write). Refs: 6.1 L80; 5.1 L44; 5.1 L45; +5 more.

Columns as written: `host`; `first emitted`; `last emitted`; `captures at emission`; `state` (emitted, pending, suppressed).

#### `comment index (yt-comments-fetcher's)`

In CONVENTIONS: **no**. Named by 2 PRD(s). Named as: `comment index`.

- Table-level writers: yt-comments-fetcher
- Table-level readers: yt-comments-fetcher, yt-replies-fetcher
- Keys as stated: per comment and per video (key columns not stated)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `comment_id` |  | yt-comments-fetcher (per comment) | yt-comments-fetcher |  |
| `comments_disabled_at` |  | yt-comments-fetcher (per video; recorded on the comments-disabled 403) | yt-comments-fetcher |  |
| `content_hash` |  | yt-comments-fetcher (per comment; compared for edit detection and the stop rule) | yt-comments-fetcher |  |
| `last_complete_fetch_at` |  | yt-comments-fetcher (per video; set by a fetch that ends with no nextPageToken) | yt-comments-fetcher |  |
| `last_seen_at` |  | yt-comments-fetcher (per comment) | yt-comments-fetcher, yt-replies-fetcher |  |
| `parent_comment_id` |  | yt-comments-fetcher (per comment) | yt-comments-fetcher, yt-replies-fetcher |  |
| `partial` |  | yt-comments-fetcher (per video; set when a fetch is stopped by the page cap) | yt-comments-fetcher |  |
| `stored_count` |  | yt-comments-fetcher (per video) | yt-comments-fetcher |  |
| `total_reply_count` |  | yt-comments-fetcher (per comment; reply candidates relisted when it changes) | yt-comments-fetcher, yt-replies-fetcher |  |
| `updated_at` |  | yt-comments-fetcher (per comment) | yt-comments-fetcher |  |
| `video_id` |  | yt-comments-fetcher (per comment) | yt-comments-fetcher |  |

#### `comment_ledger`

In CONVENTIONS: **no**. Named by 2 PRD(s).

- Table-level writers: fb-group-comments-fetcher, fb-post-comments-fetcher
- Table-level readers: fb-group-comments-fetcher, fb-post-comments-fetcher
- Keys as stated: per post and comment (exact key columns not stated); per post and comment key

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `comment key` |  | fb-post-comments-fetcher (per post and comment key) | fb-post-comments-fetcher |  |
| `created_time` |  | fb-group-comments-fetcher (used to pair edit candidates without ids)<br>fb-post-comments-fetcher (absent-in-range test against T_min; edit pairing) | fb-group-comments-fetcher, fb-post-comments-fetcher |  |
| `first_seen_at` |  | fb-group-comments-fetcher<br>fb-post-comments-fetcher |  |  |
| `id` |  | fb-group-comments-fetcher (per post and comment; the comment id if any) | fb-group-comments-fetcher |  |
| `last_complete_sweep_at` |  | fb-group-comments-fetcher (per post)<br>fb-post-comments-fetcher (per post; after a complete read) |  |  |
| `last_fetch_at` |  | fb-group-comments-fetcher (per post; written after Redpanda acknowledges the whole batch)<br>fb-post-comments-fetcher (per post; after Redpanda acknowledges the whole batch) |  |  |
| `last_seen_at` |  | fb-group-comments-fetcher<br>fb-post-comments-fetcher |  |  |
| `state` | active, superseded, deleted (fb-group-comments-fetcher); active, superseded, deleted (fb-post-comments-fetcher) | fb-group-comments-fetcher (old row superseded on an edit candidate; deleted on a complete read)<br>fb-post-comments-fetcher (superseded on an edit candidate; deleted on a complete read) | fb-group-comments-fetcher, fb-post-comments-fetcher |  |
| `superseded_by` |  | fb-post-comments-fetcher |  |  |
| `text_hash` |  | fb-group-comments-fetcher (sha256(created_time + text); compared to detect edits) | fb-group-comments-fetcher |  |
| `the hash` |  | fb-post-comments-fetcher (sha256(created_time + text); stop rule and edit/deletion detection) | fb-post-comments-fetcher |  |

#### `comment_series`

In CONVENTIONS: **no**. Named by 3 PRD(s).

- Table-level writers: comment-decay-scheduler
- Table-level readers: comment-decay-scheduler
- Mention only: x-replies-fetcher, yt-comments-fetcher
- Keys as stated: one row per video; primary key (item_id, lane)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `anchor_at` |  | comment-decay-scheduler (first-seen time) |  |  |
| `extended` | boolean (comment-decay-scheduler) | comment-decay-scheduler | comment-decay-scheduler |  |
| `hot_count` |  | comment-decay-scheduler | comment-decay-scheduler |  |
| `hot_next_at` |  | comment-decay-scheduler | comment-decay-scheduler |  |
| `hot_until` |  | comment-decay-scheduler | comment-decay-scheduler |  |
| `in_flight_job_id` |  | comment-decay-scheduler (set when a job is emitted) | comment-decay-scheduler |  |
| `item_id` |  | comment-decay-scheduler (insert ON CONFLICT (item_id, lane) DO NOTHING) |  |  |
| `lane` | metrics, (comments) (comment-decay-scheduler) | comment-decay-scheduler |  |  |
| `last_fetched_at` |  | comment-decay-scheduler | comment-decay-scheduler |  |
| `last_new_count` |  | comment-decay-scheduler |  |  |
| `last_total` |  | comment-decay-scheduler (updated from completions; stale completions only update it if newer) | comment-decay-scheduler |  |
| `next_due_at` |  | comment-decay-scheduler (anchor + offset) | comment-decay-scheduler |  |
| `next_step` |  | comment-decay-scheduler | comment-decay-scheduler |  |
| `profile` | fb_page, fb_group, ig_own, ig_other, tt, x, yt, li_own, li_other, tg_own, news (comment-decay-scheduler) | comment-decay-scheduler |  |  |
| `route` |  | comment-decay-scheduler |  |  |
| `source_id` |  | comment-decay-scheduler |  |  |
| `status` | scheduled, in_flight, done, stopped_early, cancelled (comment-decay-scheduler) | comment-decay-scheduler | comment-decay-scheduler |  |

#### `ig_hashtag_ledger`

Not in CONVENTIONS. Named only by **quota-governor** (read_write). Refs: 3 L21; 5.3 L68; 6.3 L107.

Columns as written: `account`; `hashtag`; `first used`.

#### `kb_aliases`

Not in CONVENTIONS. Named only by **analysis-entities** (read). Refs: 5.3 L61; 6.1 L87.

Columns as written: `text`; `lang`; `script`; `folded form`; `kind` (official, colloquial, abbreviation, misspelling, transliteration); `ambiguous`.

#### `kb_entities`

Not in CONVENTIONS. Named only by **analysis-entities** (read). Refs: 5.3 L61; 6.1 L87.

Columns as written: `entity_id`; `type` (brand, company, institution, place, product, person_public); `names in Arabic, Sorani and English`; `parent_id`; `scope` (global, (a client)); `status`; `kb_version`; `public_role`; `role_terms`.

#### `model_versions`

In CONVENTIONS: **no**. Named by 4 PRD(s).

- Table-level writers: analysis-sentiment
- Table-level readers: analysis-entities, analysis-media, analysis-sentiment, analysis-topics

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `status` | candidate, shadow, active, retired (analysis-sentiment) | analysis-sentiment (switch-over flips one row) | analysis-sentiment |  |
| `thresholds` |  |  | analysis-entities, analysis-topics |  |

#### `news_sites`

In CONVENTIONS: **no**. Named by 7 PRD(s).

- Table-level writers: news-site-resolver
- Table-level readers: news-article-extractor, news-comments-fetcher, news-feed-poller, news-homepage-differ, news-robots-checker, news-site-resolver, news-sitemap-poller
- Keys as stated: 'one row per host' (6.3 L116) versus 'keyed by source_id' (6.2 L112)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `access_mode` | direct, headless, proxy, blocked (news-site-resolver) | news-site-resolver (as feeds) | news-site-resolver |  |
| `article_url_patterns` |  | news-site-resolver (as feeds) | news-feed-poller, news-homepage-differ, news-site-resolver, news-sitemap-poller |  |
| `articles_per_day_estimate` |  | news-site-resolver (as feeds) | news-feed-poller, news-site-resolver |  |
| `comments_provider` | disqus (news-article-extractor); disqus, none (news-comments-fetcher); disqus, none (news-site-resolver) | news-site-resolver (as feeds) | news-comments-fetcher, news-site-resolver | news-article-extractor |
| `disqus_shortname` |  | news-site-resolver (as feeds) | news-comments-fetcher, news-site-resolver |  |
| `feeds` |  | news-site-resolver (candidate row by this service; profile mapped by registry-writer from site_profile) | news-feed-poller, news-site-resolver |  |
| `homepage_diff` | boolean (news-homepage-differ); boolean (news-site-resolver); True, False (news-homepage-differ); True, False (news-site-resolver) | news-site-resolver (as feeds) | news-homepage-differ, news-site-resolver |  |
| `identifier template` |  |  | news-comments-fetcher |  |
| `last_article_at` |  | news-site-resolver (as feeds) | news-site-resolver |  |
| `news_sitemap` |  | news-site-resolver (as feeds) | news-site-resolver, news-sitemap-poller |  |
| `profile_version` |  | news-site-resolver (part of this service's state row; a replay leaves it unchanged) |  |  |
| `resolved_at` |  | news-site-resolver (part of this service's state row) |  |  |
| `sitemaps` |  | news-site-resolver (as feeds) | news-site-resolver |  |
| `source_id` |  |  |  | news-site-resolver |
| `status` | candidate (news-site-resolver) | news-site-resolver (this service writes news_sites with status candidate (5.2 step 10)) |  |  |

#### `news_stories`

Not in CONVENTIONS. Named only by **news-dedup** (read_write). Keys: story_id. Refs: 3 L21; 5.2 L58; 6.1 L80; +1 more.

Columns as written: `story_id`; `origin_key`; `origin_source_id`; `origin_time`; `cluster_size`; `first_seen_at`; `last_member_at`; `merged_into`.

#### `news_story_members`

Not in CONVENTIONS. Named only by **news-dedup** (read_write). Keys: idempotency_key primary key; index on each simhash block plus fetched_at. Refs: 3 L21; 5.2 L54; 5.2 L58; +4 more.

Columns as written: `idempotency_key`; `story_id`; `source_id`; `canonical_key`; `simhash and its four 16-bit blocks`; `title_sha256`; `text_sha256`; `language`; `origin_time`; `fetched_at`; `role`; `matched_by` (simhash); `hamming_distance`.

#### `news_urls`

In CONVENTIONS: **no**. Named by 5 PRD(s).

- Table-level writers: news-article-extractor
- Table-level readers: news-article-extractor, news-dedup, news-feed-poller, news-homepage-differ, news-sitemap-poller
- Keys as stated: url_hash (lookup key; primary key not stated)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `canonical_url_hash` |  | news-article-extractor (written with done; looked up at step 7 to detect duplicate_canonical) | news-article-extractor |  |
| `fetched_at` |  | news-article-extractor (written with done) |  |  |
| `first_seen_at` |  | news-article-extractor |  |  |
| `found_via` |  | news-article-extractor |  |  |
| `source_id` |  | news-article-extractor |  |  |
| `status` | done, gone, not_article, paywalled, skipped_policy, failed (news-article-extractor) | news-article-extractor (done written only after Redpanda acknowledges (5.2 step 8); skipped_policy at step 2; done or gone ends processing at step 1) | news-article-extractor |  |
| `url` |  | news-article-extractor |  |  |
| `url_hash` |  | news-article-extractor (computed per message and looked up first (5.2 step 1)) | news-article-extractor, news-feed-poller, news-homepage-differ, news-sitemap-poller |  |

#### `onboarding records`

Not in CONVENTIONS. Named only by **tg-bot-channel-receiver** (read). Refs: 4 L35; 5.2 L67; 5.2 L69; +2 more.

Columns as written: `one-time code`; `source_id`; `username`; `onboarding status`.

#### `poster_profiles`

In CONVENTIONS: **no**. Named by 2 PRD(s).

- Table-level writers: poster-resolver
- Table-level readers: poster-resolver
- Mention only: x-user-resolver
- Keys as stated: unique on candidate_key

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `author_hash` |  | poster-resolver (sha256(platform \|\| platform_id \|\| salt)) |  |  |
| `candidate_key` |  | poster-resolver (insert with status = resolving; unique) | poster-resolver |  |
| `expires_at` |  | poster-resolver (+30 days) |  |  |
| `followers` |  | poster-resolver |  |  |
| `hits_30d` |  | poster-resolver (incremented on a cache hit) | poster-resolver |  |
| `individual` |  | poster-resolver |  |  |
| `platform` |  | poster-resolver (kept for individuals) |  |  |
| `profile` | jsonb (poster-resolver) | poster-resolver (empty for individuals) |  |  |
| `resolved_at` |  | poster-resolver (cache hit if within 30 days) | poster-resolver |  |
| `status` | resolving (x-user-resolver); resolving, pending (poster-resolver) | poster-resolver (insert resolving; returns to pending on resolver timeout) | poster-resolver | x-user-resolver |
| `unresolvable_reason` |  | poster-resolver |  |  |
| `verified` |  | poster-resolver (kept for individuals) |  |  |

#### `profile_cache`

In CONVENTIONS: **no**. Named by 4 PRD(s).

- Table-level writers: fb-page-resolver, ig-account-resolver, x-user-resolver, yt-channel-resolver
- Table-level readers: fb-page-resolver, ig-account-resolver, x-user-resolver, yt-channel-resolver
- Keys as stated: SHA-256 of candidate_key (candidate_key_hash); candidate_key (Pages); keyed hash of the key (individuals); candidate_key or handle alias (a resolved handle is cached under both the handle and the channel id)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `candidate_key` |  | fb-page-resolver (Pages cached by key)<br>yt-channel-resolver (looked up by key or alias (5.2 step 1); written with the emit (8)) | fb-page-resolver, yt-channel-resolver |  |
| `candidate_key_hash` |  | ig-account-resolver (SHA-256 of candidate_key; lookup key) | ig-account-resolver |  |
| `expires_at` |  | fb-page-resolver (30 days for Pages and for individuals' hashes)<br>ig-account-resolver (resolved_at + 30 days)<br>x-user-resolver (30 days)<br>yt-channel-resolver (30 days after resolution) | fb-page-resolver, ig-account-resolver, x-user-resolver, yt-channel-resolver |  |
| `fetched_at` |  | fb-page-resolver (refresh loop orders by oldest fetched_at)<br>x-user-resolver (refresh order: oldest fetched_at first)<br>yt-channel-resolver (refresh loop orders by oldest fetched_at) | fb-page-resolver, x-user-resolver, yt-channel-resolver |  |
| `handle aliases` |  | yt-channel-resolver (a resolved handle is cached under both the handle and the channel id) | yt-channel-resolver |  |
| `keyed hash (individuals)` |  | fb-page-resolver (only the hash of the key for individuals) | fb-page-resolver |  |
| `resolved_at` |  | ig-account-resolver | ig-account-resolver |  |
| `result` |  | ig-account-resolver (the outcome, negative ones included; for individuals only the hash is held (13.3 L179)) | ig-account-resolver |  |
| `the profile` |  | fb-page-resolver (stored for 30 days on a Page answer) | fb-page-resolver |  |
| `the profile or verdict` | resolved, unavailable (yt-channel-resolver) | yt-channel-resolver (cached for 30 days, written with the emit so a replay answers identically) | yt-channel-resolver |  |
| `verdict` |  | x-user-resolver (individuals and unavailable accounts: keyed hashes, verdict and expires_at only) | x-user-resolver |  |
| `x:<user id> / x:<handle> keys` |  | x-user-resolver (profiles cached under both keys; individuals and unavailable accounts only as keyed hashes) | x-user-resolver |  |

#### `registry`

Not in CONVENTIONS. Named only by **lang-dialect-id** (mention). Refs: 3 L28; 5.3 L69.

Columns as written: `country_signals`.

#### `registry_audit`

Not in CONVENTIONS. Named only by **registry-writer** (read_write). Refs: 3 L26; 5.2 L49; 5.2 L58; +4 more.

Columns as written: `decision_id`; `source_id`; `action` (rejected, (decision actions)); `actor`; `before`; `after`; `applied_at`; `event_published_at`.

#### `reply index (x-replies-fetcher's)`

Not in CONVENTIONS. Named only by **x-replies-fetcher** (read_write). Refs: 3 L21; 5.2 L53; 5.2 L61-L62; +5 more.

Columns as written: `post_id`; `reply_id`; `parent_comment_id`; `content_hash`; `first_seen_at`; `is_root`; `post_created_at`; `newest_reply_id`; `stored_count`; `last_complete_fetch_at`; `partial`; `window_partial`.

#### `reply index (yt-replies-fetcher's)`

Not in CONVENTIONS. Named only by **yt-replies-fetcher** (read_write). Keys: per reply and per thread (key columns not stated). Refs: 3 L20; 5.2 L48; 5.2 L51; +3 more.

Columns as written: `thread_id`; `reply_id`; `content_hash`; `updated_at`; `last_seen_at`; `video_id`; `stored_count`; `reply_count_at_last_fetch`; `last_fetch_at`; `last_complete_fetch_at`; `partial`.

#### `retention_audit`

In CONVENTIONS: **no**. Named by 2 PRD(s).

- Table-level writers: retention-purger, yt-text-purger
- Table-level readers: none
- Keys as stated: run_id (one row per run)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `candidates` |  | retention-purger<br>yt-text-purger |  |  |
| `class` | youtube_30d_text (yt-text-purger) | retention-purger<br>yt-text-purger |  |  |
| `clock` | 30 days (yt-text-purger) | retention-purger<br>yt-text-purger |  |  |
| `completed` |  | retention-purger<br>yt-text-purger |  |  |
| `cutoff` |  | retention-purger<br>yt-text-purger |  |  |
| `delegated_to` |  | retention-purger |  |  |
| `derived_deleted` |  | yt-text-purger |  |  |
| `emitted` |  | retention-purger<br>yt-text-purger |  |  |
| `executor` | yt-text-purger (yt-text-purger) | yt-text-purger |  |  |
| `failures` |  | yt-text-purger (items that ended neither refreshed nor completely deleted; must be 0 to pass) |  |  |
| `finished_at` |  | retention-purger<br>yt-text-purger |  |  |
| `holds` |  | retention-purger<br>yt-text-purger |  |  |
| `oldest_remaining_age_seconds` |  | retention-purger<br>yt-text-purger |  |  |
| `parent_run_id` |  | yt-text-purger (retention-purger's run) |  |  |
| `refresh_missed` |  | yt-text-purger (items whose refresh did not land in time and fell back to deletion) |  |  |
| `refreshed` |  | yt-text-purger |  |  |
| `run_id` |  | retention-purger (append-only insert, one row per run)<br>yt-text-purger (one append-only row per run) |  |  |
| `started_at` |  | retention-purger<br>yt-text-purger |  |  |
| `status` | pass, fail (retention-purger); pass, fail (yt-text-purger) | retention-purger<br>yt-text-purger (pass only when failures = 0 and every verification count is 0) |  |  |
| `text_deleted` |  | yt-text-purger |  |  |
| `trigger` | retention_sweep (yt-text-purger) | yt-text-purger |  |  |
| `verification` |  | retention-purger (query text, result count, executed at)<br>yt-text-purger (object {query, result, executed_at}) |  |  |
| `verification.executed_at` |  | yt-text-purger |  |  |
| `verification.query` |  | yt-text-purger |  |  |
| `verification.result` |  | yt-text-purger |  |  |

#### `search_candidate_seen`

Not in CONVENTIONS. Named only by **search-hit-router** (read_write). Keys: candidate_key (5.2 step 7). Refs: 5.2 L61; 6.3 L138; 13.8 L188.

Columns as written: `candidate key`; `first emitted`; `evidence`.

#### `search_parked_urls`

Not in CONVENTIONS. Named only by **search-hit-router** (read_write). Refs: 3 L26; 5.1 L47; 5.2 L63; +3 more.

Columns as written: `domain`; `URL`; `parked time`.

#### `search_url_seen`

Not in CONVENTIONS. Named only by **search-hit-router** (read_write). Keys: upsert per canonical URL (5.2 step 4); unique key not stated. Refs: 6.3 L138; 5.2 L58; 7 L144; +2 more.

Columns as written: `canonical URL hash`; `canonical URL`; `first seen`; `last seen`; `sightings`; `engines`; `rules (bounded list)`; `clients (bounded list)`; `platform`; `candidate_key`; `routed time`; `outcome` (duplicate, unroutable, already_registered, web, unparseable).

#### `taxonomy_nodes`

Not in CONVENTIONS. Named only by **analysis-topics** (read_write). Refs: 5.3 L68; 6.1 L90; 13.4 L165.

Columns as written: `taxonomy_id` (global, (a client)); `node_id`; `labels in Arabic, Sorani and English`; `description`; `examples`; `status` (zero_shot, supervised, retired); `taxonomy_version`.

#### `tt_client_video_state`

Not in CONVENTIONS. Named only by **tt-client-videos-fetcher** (read_write). Refs: 5.2 L59; 5.2 L60; 6.1 L90; +1 more.

Columns as written: `video id`; `first_seen_at`; `observation labels written` (plus_24h, plus_7d).

#### `tt_comment_state`

Not in CONVENTIONS. Named only by **tt-video-comments-fetcher** (read_write). Keys: one row per video. Refs: 5.2 L56; 5.2 L62; 6.1 L93; +2 more.

Columns as written: `newest stored `create_time``; `stored count`; `last fetch time`; `last reply-count per parent comment`.

#### `tt_user_cache`

Not in CONVENTIONS. Named only by **tt-user-resolver** (read_write). Keys: candidate_key (lookup key; primary key not stated). Refs: 5.1 L43; 5.2 L52; 5.2 L57; +4 more.

Columns as written: `candidate_key`; `the message written`; `resolved_at`; `expires_at`.

#### `x_compliance_audit`

Not in CONVENTIONS. Named only by **x-compliance-sync** (write). Refs: 5.2 L59; 6.2 L97; 6.2 L113-L128; +3 more.

Columns as written: `run_id` (string); `trigger` (string, daily); `started_at` (string); `finished_at` (string); `x_jobs` (array); `x_jobs[].type` (string, tweets, users); `x_jobs[].job_id` (string); `x_jobs[].signal_at` (string); `ids_submitted` (object); `ids_submitted.posts` (integer); `ids_submitted.users` (integer); `ids_returned` (object); `ids_returned.deleted` (integer); `ids_returned.protected` (integer); `ids_returned.suspended` (integer); `ids_returned.withheld` (integer); `ids_returned.deactivated` (integer); `ids_returned.other` (integer); `withheld_in_iq` (integer); `class_mismatch` (integer); `ids_actioned` (integer); `ids_completed` (integer); `signal_to_deleted_seconds` (object); `signal_to_deleted_seconds.p50` (integer); `signal_to_deleted_seconds.p95` (integer); `signal_to_deleted_seconds.max` (integer); `evidence` (array); `evidence[]` (string); `status` (string, pass, fail).

#### `x_compliance_runs`

Not in CONVENTIONS. Named only by **x-compliance-sync** (read_write). Refs: 5.2 L51; 6.2 L97; 6.3 L134; +2 more.

Columns as written: `run_id` (ULID); `trigger`; `started_at`; `job ids`; `step status`.

#### `x_read_ledger`

Not in CONVENTIONS. Named only by **quota-governor** (read_write). Keys: (UTC day, resource id). Refs: 3 L21; 5.3 L68; 6.3 L107.

Columns as written: `UTC day`; `resource id`.

#### `yt_live_watch`

Not in CONVENTIONS. Named only by **yt-video-details-fetcher** (read_write). Refs: 5.1 L54; 6.1 L86; 6.3 L159.

Columns as written: `platform_id`; `source_id`; `live_state` (live, upcoming, none); `next_check_at`.

#### `yt_subscriptions`

Not in CONVENTIONS. Named only by **yt-pubsub-receiver** (read_write). Refs: 5.1 L42; 5.2 L50; 6.1 L98; +1 more.

Columns as written: `source_id`; `topic`; `state` (requested, active, lapsed, unsubscribing, unsubscribed, failed); `verified_at`; `lease_expires_at`; `last_notification_at`; `consecutive_errors`.

### 4.2 Analytics store (ClickHouse)

| Table | In CONVENTIONS | PRDs naming it |
|---|---|---|
| `aggregates_hourly` | yes | 7: aggregator, deletion-propagator, fb-reactions-fetcher, retention-purger, store-writer, yt-text-purger, yt-video-details-fetcher |
| `analysis` | yes | 10: aggregator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, deletion-propagator, li-own-comments-fetcher, li-post-comments-fetcher, store-writer, yt-text-purger |
| `comments` | yes | 17: aggregator, analysis-sentiment, deletion-propagator, ig-comments-fetcher, ig-own-comments-fetcher, keyword-matcher, li-own-comments-fetcher, li-post-comments-fetcher, normalize-item, retention-purger, store-writer, tt-video-comments-fetcher, x-compliance-sync, x-replies-fetcher, yt-comments-fetcher, yt-replies-fetcher, yt-text-purger |
| `items` | yes | 15: aggregator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, deletion-propagator, ig-comments-fetcher, keyword-matcher, normalize-item, qualifier, retention-purger, store-writer, x-compliance-sync, yt-keyword-search, yt-text-purger |
| `keywords_dim` | yes | 3: aggregator, alert-evaluator, store-writer |
| `metrics_timeseries` | yes | 7: aggregator, deletion-propagator, fb-reactions-fetcher, store-writer, tt-video-stats-refresher, yt-text-purger, yt-video-details-fetcher |
| `sources_dim` | yes | 3: aggregator, alert-evaluator, store-writer |
| `aggregates_daily` | **no** | 2: aggregator, alert-evaluator |
| `aggregates_daily_v` | **no** | 1: alert-evaluator |
| `aggregates_hourly_v` | **no** | 2: aggregator, alert-evaluator |
| `aggregates_monthly` | **no** | 1: aggregator |
| `aggregates_monthly_v` | **no** | 1: alert-evaluator |
| `analytics store (stored comment ids and content hashes; table not named)` | **no** | 1: news-comments-fetcher |
| `comments_v` | **no** | 1: store-writer |
| `hits` | **no** | 3: aggregator, keyword-matcher, store-writer |
| `items_v` | **no** | 1: store-writer |
| `mv_aggregates_hourly` | **no** | 1: aggregator |
| `system.mutations` | **no** | 1: deletion-propagator |

#### `aggregates_hourly`

In CONVENTIONS: yes. Named by 7 PRD(s).

- Table-level writers: aggregator
- Table-level readers: aggregator
- Mention only: deletion-propagator, fb-reactions-fetcher, retention-purger, store-writer, yt-text-purger, yt-video-details-fetcher
- Keys as stated: ReplacingMergeTree(version); partitioned by month; sorted by client_id, keyword_id, hour, platform, source_id, sentiment, topic_id, retention_class; TTL hour + INTERVAL 10 YEAR

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `client_id` | string (uuid) (aggregator) | aggregator (grain; sorting key) |  |  |
| `engagement` | integer (aggregator) | aggregator (likes + comments + shares of the latest counts) |  |  |
| `hour` | string ('2026-10-06 08:00:00') (aggregator) | aggregator (grain; sorting key) |  |  |
| `keyword_id` | string (uuid) (aggregator) | aggregator (grain; sorting key) |  |  |
| `mentions` | integer (aggregator) | aggregator (distinct items) |  |  |
| `platform` | string (aggregator) | aggregator (grain) |  |  |
| `reach` | integer (aggregator) | aggregator (followers of the posting source summed over its mentions (gross); individuals 0) |  |  |
| `retention_class` | string (aggregator) | aggregator (grain) |  |  |
| `sentiment` | string (aggregator); (analysis-sentiment labels), pending, unscored (aggregator) | aggregator (grain) |  |  |
| `source_id` | string (uuid) (aggregator) | aggregator (the poster's author_source_id; individuals under the nil UUID) |  |  |
| `topic_id` | string (aggregator); (analysis-topics ids), unassigned (aggregator) | aggregator (grain; one row per topic (fan-out)) |  |  |
| `version` | integer (epoch seconds) (aggregator) | aggregator (now() as epoch seconds; ReplacingMergeTree(version)) |  |  |
| `views` | integer (aggregator) | aggregator |  |  |

#### `analysis`

In CONVENTIONS: yes. Named by 10 PRD(s).

- Table-level writers: deletion-propagator, store-writer
- Table-level readers: aggregator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, deletion-propagator, yt-text-purger
- Mention only: li-own-comments-fetcher, li-post-comments-fetcher
- Keys as stated: ReplacingMergeTree; version analyzed_at (ms); sorting key item_id, model; partition toYYYYMM(analyzed_at)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `analyzed_at` | ms (store-writer) | store-writer (version column; partition toYYYYMM(analyzed_at)) |  |  |
| `entity ids` |  | store-writer (typed projection) |  |  |
| `item_id` |  | store-writer (sorting key (item_id, model)) |  |  |
| `model` |  | store-writer (sorting key) |  |  |
| `model_version` |  | store-writer |  |  |
| `output` | JSON (store-writer) | store-writer |  |  |
| `retention_class` |  | store-writer (from the message, else the item row) |  |  |
| `row_expires_at` |  | store-writer (follows the item's) |  |  |
| `sentiment label and score` |  | store-writer (typed projection) |  |  |
| `topic ids` |  | store-writer (typed projection) |  |  |

#### `comments`

In CONVENTIONS: yes. Named by 17 PRD(s).

- Table-level writers: deletion-propagator, store-writer
- Table-level readers: aggregator, analysis-sentiment, deletion-propagator, ig-comments-fetcher, ig-own-comments-fetcher, keyword-matcher, li-own-comments-fetcher, li-post-comments-fetcher, normalize-item, retention-purger, tt-video-comments-fetcher, x-compliance-sync, yt-text-purger
- Mention only: x-replies-fetcher, yt-comments-fetcher, yt-replies-fetcher
- Keys as stated: ReplacingMergeTree; version row_version; sorting key item_id; partition toYYYYMM(created_at); keyed by parent_id (as written)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `(same columns as items)` |  | store-writer |  |  |
| `author reference` |  |  |  | yt-text-purger |
| `author_hash` |  |  | deletion-propagator, x-compliance-sync |  |
| `comment ids` |  |  | ig-own-comments-fetcher |  |
| `content hash` |  |  | li-own-comments-fetcher |  |
| `content hashes` |  |  | ig-own-comments-fetcher, li-post-comments-fetcher |  |
| `created_at` |  | store-writer (partition toYYYYMM(created_at)) |  |  |
| `fetched_at` |  |  | retention-purger, yt-text-purger |  |
| `id` |  |  | li-own-comments-fetcher |  |
| `ids` |  |  | li-post-comments-fetcher |  |
| `is_deleted` | 1 (deletion-propagator) | deletion-propagator (tombstone rows) |  |  |
| `item_id` |  |  | retention-purger, x-compliance-sync, yt-text-purger |  |
| `parent_id` |  | store-writer (bloom index) | deletion-propagator | x-replies-fetcher, yt-comments-fetcher, yt-replies-fetcher |
| `platform` | x (x-compliance-sync) |  | x-compliance-sync |  |
| `reply count` |  |  | yt-text-purger |  |
| `retention_class` | x_24h_sync (x-compliance-sync); youtube_30d_text (yt-text-purger) |  | retention-purger, x-compliance-sync, yt-text-purger |  |
| `row_version` |  | store-writer (version column) |  |  |
| `source_id` |  |  | x-compliance-sync, yt-text-purger |  |
| `stored content hashes (column name not stated)` |  |  | tt-video-comments-fetcher |  |
| `stored hashes` |  |  | ig-comments-fetcher |  |
| `text` |  |  | yt-text-purger |  |
| `text_norm` |  |  |  | yt-text-purger |
| `thread id` |  |  | yt-text-purger |  |
| `time` |  |  | li-own-comments-fetcher |  |
| `video id` |  |  | yt-text-purger |  |

#### `items`

In CONVENTIONS: yes. Named by 15 PRD(s).

- Table-level writers: deletion-propagator, store-writer
- Table-level readers: aggregator, analysis-entities, analysis-media, analysis-sentiment, analysis-topics, deletion-propagator, ig-comments-fetcher, keyword-matcher, normalize-item, qualifier, retention-purger, x-compliance-sync, yt-text-purger
- Mention only: yt-keyword-search
- Keys as stated: ReplacingMergeTree versions; monthly partitions; ReplacingMergeTree; version row_version; sorting key item_id; partition toYYYYMM(created_at)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `at_mentions` |  | store-writer (column TTL) |  |  |
| `author_hash` |  | deletion-propagator (author scope selects by author_hash; emptied for purge_text) | deletion-propagator, x-compliance-sync |  |
| `author_ref` | string (store-writer) | store-writer (column TTL) |  |  |
| `author_source_id` | string (uuid) (store-writer) | store-writer | aggregator |  |
| `author_type` | string (store-writer) | store-writer |  |  |
| `client_ids` |  | deletion-propagator (client scope: new version removes this client's id from shared items) | deletion-propagator |  |
| `comments_count` | integer (store-writer) | store-writer (projected from metrics_snapshot) |  |  |
| `content_expires_at` | string ('2106-01-01 00:00:00') (store-writer) | store-writer (the message's expires_at; sentinel 2106-01-01 00:00:00 when no content expiry) |  |  |
| `content_hash` | string (store-writer) | store-writer |  |  |
| `created_at` | string ('2026-10-06 08:51:40.000') (store-writer) | store-writer (partition toYYYYMM(created_at); never changes between versions) |  |  |
| `dialect` | string (store-writer) | store-writer |  |  |
| `dialect_conf` | number (store-writer) | store-writer |  |  |
| `fetched_at` | string ('2026-10-06 09:13:58.000') (store-writer) | store-writer | retention-purger, yt-text-purger |  |
| `hashtags` |  | store-writer (column TTL) |  |  |
| `idempotency_key` | string (store-writer) | store-writer |  |  |
| `is_deleted` | 1, 0 (deletion-propagator) | deletion-propagator (tombstone rows inserted with is_deleted = 1, permanent, no TTL) |  |  |
| `item_id` | string (uuid) (store-writer) | store-writer (sorting key; identity) | aggregator, deletion-propagator, retention-purger, x-compliance-sync |  |
| `kind` | string (store-writer); video (yt-text-purger) | store-writer (routing: comment or reply -> comments, else items) | yt-text-purger |  |
| `lang` | string (store-writer) | store-writer |  |  |
| `lang_conf` | number (store-writer) | store-writer |  |  |
| `lang_model_version` | string (store-writer) | store-writer |  |  |
| `likes` | integer (store-writer) | store-writer (projected from metrics_snapshot) |  |  |
| `likes / comments / shares (item-row counts)` |  |  | aggregator |  |
| `links` |  | store-writer (column TTL) |  |  |
| `media` |  | store-writer (column TTL) |  |  |
| `metrics_snapshot` | JSON (store-writer) | store-writer (raw metrics_snapshot as JSON; column TTL) |  |  |
| `normalizer_version` | string (store-writer) | store-writer |  |  |
| `parent_id` | null (store-writer) | store-writer | deletion-propagator |  |
| `parent_seen` | integer (1/0) (store-writer) | store-writer |  |  |
| `permalink` |  |  | ig-comments-fetcher |  |
| `platform` | string (store-writer); x (x-compliance-sync) | store-writer | aggregator, x-compliance-sync |  |
| `platform_id` |  | store-writer (column TTL) |  |  |
| `published_at` |  |  | qualifier |  |
| `raw_ref` | string (store-writer) | store-writer | deletion-propagator |  |
| `retention_class` | string (store-writer); x_24h_sync (x-compliance-sync); youtube_30d_text (yt-text-purger) | store-writer | aggregator, retention-purger, x-compliance-sync, yt-text-purger |  |
| `root_id` | null (store-writer) | store-writer |  |  |
| `route` | string (store-writer) | store-writer |  |  |
| `row_expires_at` | string ('2036-10-06 08:51:40') (store-writer) | store-writer (table TTL deletes the row; from retention_classes.row_ttl) |  |  |
| `row_version` | integer (store-writer) | store-writer ((version << 32) \| produced_at (epoch seconds); ReplacingMergeTree version column) |  |  |
| `script` | string (store-writer) | store-writer |  |  |
| `service` | string (store-writer) | store-writer |  |  |
| `shares` | integer (store-writer) | store-writer (projected from metrics_snapshot) |  |  |
| `source_id` | string (uuid) (store-writer) | store-writer | deletion-propagator, qualifier, x-compliance-sync |  |
| `text` | string (store-writer) | deletion-propagator (emptied in a new version for purge_text)<br>store-writer (column TTL blanks at content_expires_at) | yt-text-purger |  |
| `text_norm` | string (store-writer) | deletion-propagator (emptied for purge_text)<br>store-writer (column TTL; text index tokenbf_v1 and ngrambf_v1) | analysis-entities |  |
| `title` |  | store-writer (column TTL) |  |  |
| `url` |  | deletion-propagator (emptied for purge_text)<br>store-writer (column TTL) |  |  |
| `vendor` | null (store-writer) | store-writer |  |  |
| `version` | integer (store-writer) | deletion-propagator (tombstone version = deletion time, greater than any content version)<br>store-writer |  |  |
| `views` | null (store-writer) | store-writer (projected from metrics_snapshot) |  |  |

#### `keywords_dim`

In CONVENTIONS: yes. Named by 3 PRD(s).

- Table-level writers: store-writer
- Table-level readers: aggregator, alert-evaluator
- Keys as stated: ReplacingMergeTree; version updated_at; sorting key keyword_id; no partition

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `keyword_id` |  | store-writer (sorting key) |  |  |
| `purpose` | reputation, service_quality (alert-evaluator) |  | alert-evaluator |  |
| `updated_at` |  | store-writer (version column) |  |  |

#### `metrics_timeseries`

In CONVENTIONS: yes. Named by 7 PRD(s).

- Table-level writers: deletion-propagator, store-writer
- Table-level readers: aggregator, deletion-propagator, tt-video-stats-refresher
- Mention only: fb-reactions-fetcher, yt-text-purger, yt-video-details-fetcher
- Keys as stated: (item_id, observed_at); ReplacingMergeTree; version observed_at; sorting key item_id, observed_at; partition toYYYYMM(observed_at)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `comments` |  | store-writer |  |  |
| `first-sight point (columns not named)` |  |  | tt-video-stats-refresher |  |
| `item_id` |  | store-writer (sorting key (item_id, observed_at)) |  |  |
| `likes` |  | store-writer |  |  |
| `observed_at` |  | store-writer (version column; partition toYYYYMM(observed_at)) |  |  |
| `reactions by type` |  | store-writer |  |  |
| `retention_class` |  | store-writer (from the message, else the item row) |  |  |
| `row_expires_at` |  | store-writer (follows the item's) |  |  |
| `shares` |  | store-writer |  |  |
| `views` |  | store-writer |  |  |

#### `sources_dim`

In CONVENTIONS: yes. Named by 3 PRD(s).

- Table-level writers: store-writer
- Table-level readers: aggregator, alert-evaluator
- Keys as stated: ReplacingMergeTree; version updated_at; sorting key source_id; no partition

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `display_name` |  | store-writer (items join display_name from sources_dim) |  |  |
| `followers` |  |  | aggregator |  |
| `source_id` |  | store-writer (sorting key) |  |  |
| `updated_at` |  | store-writer (version column) |  |  |

#### `aggregates_daily`

In CONVENTIONS: **no**. Named by 2 PRD(s).

- Table-level writers: aggregator
- Table-level readers: aggregator, alert-evaluator
- Keys as stated: same keys without the hour (day); ten-year TTL

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `(same keys and measures as aggregates_hourly)` |  | aggregator (sum of the hourly level) |  |  |
| `day` |  | aggregator (in place of hour) |  |  |

#### `aggregates_daily_v`

Not in CONVENTIONS. Named only by **alert-evaluator** (read). Refs: 6.1 L78.

#### `aggregates_hourly_v`

In CONVENTIONS: **no**. Named by 2 PRD(s).

- Table-level writers: none
- Table-level readers: aggregator, alert-evaluator

#### `aggregates_monthly`

Not in CONVENTIONS. Named only by **aggregator** (read_write). Keys: same keys without the hour (month); ten-year TTL. Refs: 2 L15; 5.2 L48; 5.3 L59; +2 more.

Columns as written: `month`; `(same keys and measures as aggregates_hourly)`.

#### `aggregates_monthly_v`

Not in CONVENTIONS. Named only by **alert-evaluator** (read). Refs: 5.3 L60; 6.1 L78.

#### `analytics store (stored comment ids and content hashes; table not named)`

Not in CONVENTIONS. Named only by **news-comments-fetcher** (read). Refs: 6.1 L88; 6.3 L124.

#### `comments_v`

Not in CONVENTIONS. Named only by **store-writer** (write). Refs: 5.3 L82.

#### `hits`

In CONVENTIONS: **no**. Named by 3 PRD(s).

- Table-level writers: store-writer
- Table-level readers: aggregator, keyword-matcher
- Keys as stated: ReplacingMergeTree; version row_version; sorting key client_id, keyword_id, item_id; partition toYYYYMM(hit_at); one row per (item, client, keyword) (13.6); upsert keyed by hit_id (5.1)

| Column as written | Type and values as stated | Written by (how) | Read by | Mentioned by |
|---|---|---|---|---|
| `client_id` |  | store-writer (sorting key) | aggregator |  |
| `hit_at` |  | store-writer (partition toYYYYMM(hit_at)) | aggregator |  |
| `item_id` |  | store-writer (sorting key) | aggregator |  |
| `keyword_id` |  | store-writer (sorting key) | aggregator |  |
| `retention_class` |  | store-writer (from the message, else the item row) |  |  |
| `row_expires_at` |  | store-writer (follows the item's) |  |  |
| `row_version` |  | store-writer (version column) |  |  |
| `status` | active (aggregator); active, retracted (store-writer) | store-writer | aggregator |  |

#### `items_v`

Not in CONVENTIONS. Named only by **store-writer** (write). Refs: 5.3 L82; 13.4 L170.

#### `mv_aggregates_hourly`

Not in CONVENTIONS. Named only by **aggregator** (write). Refs: 5.3 L59.

#### `system.mutations`

Not in CONVENTIONS. Named only by **deletion-propagator** (read). Refs: 5.3 L62; 6.2 L101.

Columns as written: `table`; `is_done`.

### 4.3 Object storage paths

| Name as written | Written by | Read by | Mentioned by | Refs |
|---|---|---|---|---|
| `48-hour prefix (path not stated)` |  |  | li-notification-receiver | li-notification-receiver 8 L150 |
| `48-hour prefix, redacted quarantine path (path not stated)` | li-post-comments-fetcher |  |  | li-post-comments-fetcher 8 L148; 12 L170; +1 more |
| `7-day full-text cache (news-article-extractor's)` |  |  | news-dedup | news-dedup 5.4 L74; 7 L115 |
| `<batch>.manifest.json (beside the batch)` | raw-archiver | raw-archiver |  | raw-archiver 3 L19; 5.2 L52; +2 more |
| `<batch>.s<n>.jsonl.zst (supplement)` | raw-archiver |  |  | raw-archiver 5.3 L63 |
| `archive/<platform>/<yyyy>/<mm>/` | raw-archiver | analysis-entities, analysis-media, analysis-sentiment, analysis-topics |  | analysis-entities 5.1 L46; 6.1 L87; analysis-media 5.1 L47; 6.1 L84; analysis-sentiment 5.1 L51; 6.1 L86; analysis-topics 5.1 L50; 6.1 L90; raw-archiver 3 L20 |
| `archive/<platform>/<yyyy>/<mm>/<dd>-<part>.envelope.parquet` | raw-archiver |  |  | raw-archiver 5.3 L67; 6.2 L96 |
| `archive/<platform>/<yyyy>/<mm>/<dd>-<part>.payload.parquet` | raw-archiver |  |  | raw-archiver 5.3 L67; 6.2 L96 |
| `archive/registry/<yyyy>/<mm>/` | registry-writer |  |  | registry-writer 12 L140 |
| `archive/youtube/<yyyy>/<mm>/` |  |  | yt-text-purger | yt-text-purger 5.3 L112; 13.4 L253; +1 more |
| `cache/news/<yyyy>/<mm>/<dd>/<canonical_url_hash>.json.zst` | news-article-extractor |  |  | news-article-extractor 3 L22; 5.2 L58; +4 more |
| `cache/news/comments/<yyyy>/<mm>/<dd>/<article hash>-<step>.jsonl.zst` | news-comments-fetcher |  |  | news-comments-fetcher 5.2 L57; 6.2 L113; +2 more |
| `client reference logos (path not stated)` |  | analysis-media |  | analysis-media 5.3 L68 |
| `compaction ledger (one marker object per platform and day)` | raw-archiver |  |  | raw-archiver 6.3 L122 |
| `media objects and references (via raw-archiver media endpoint)` | deletion-propagator |  |  | deletion-propagator 3 L21; 5.3 L66 |
| `media/<sha256>` | analysis-media, raw-archiver | analysis-media |  | analysis-media 3 L23; 5.1 L47; +4 more; raw-archiver 3 L21; 5.3 L69; +2 more |
| `media/<sha256>.refs` | raw-archiver | raw-archiver |  | raw-archiver 5.3 L69; 6.2 L96; +1 more |
| `models/entities/<model_version>/` |  | analysis-entities |  | analysis-entities 5.3 L77; 6.1 L87 |
| `models/media/<task>/<model_version>/` |  | analysis-media |  | analysis-media 5.3 L74; 6.1 L84 |
| `models/sentiment/<model_version>/` |  | analysis-sentiment |  | analysis-sentiment 5.3 L76; 6.1 L86 |
| `models/topics/<model_version>/` |  | analysis-topics |  | analysis-topics 5.3 L80; 6.1 L90 |
| `raw JSONL batches and Parquet envelope/payload files (via raw-archiver rewrite)` | deletion-propagator |  |  | deletion-propagator 1 L7; 3 L21; +2 more |
| `raw and Parquet archives` |  | x-compliance-sync |  | x-compliance-sync 1 L7; 5.1 L43; +1 more |
| `raw archive (path not stated)` |  |  | tt-hashtag-feed-poller, tt-keyword-search, tt-user-resolver | tt-hashtag-feed-poller 8 L125; 12 L149; tt-keyword-search 8 L119; tt-user-resolver 5.3 L61; 13.10 L165 |
| `raw archive object at raw_ref (e.g. raw/green/x/2026/10/06/x-recent-search/0042.jsonl.zst#310)` |  | keyword-matcher |  | keyword-matcher 5.3 L74; 6.1 L92; +1 more |
| `raw response archive (path not stated)` |  |  | yt-web-search-bridge | yt-web-search-bridge 8 L148 |
| `raw-archiver manifests` |  | retention-purger |  | retention-purger 5.2 L52; 6.1 L90 |
| `raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst` | raw-archiver | normalize-item, raw-archiver | lang-dialect-id | lang-dialect-id 5.1 L45; normalize-item 5.1 L45; 6.1 L88; raw-archiver 2 L13; 3 L19; +2 more |
| `raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst (per-service prefixes)` |  |  | fb-backfill, fb-client-webhook-receiver, fb-group-comments-fetcher, fb-group-posts-poller, fb-keyword-search, fb-page-feed-poller, fb-page-search, fb-post-comments-fetcher, ig-account-media-poller, ig-comments-fetcher, ig-keyword-search, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, li-client-posts-poller, li-company-posts-poller, li-notification-receiver, li-own-comments-fetcher, li-post-comments-fetcher, li-post-search, news-article-extractor, tg-bot-channel-receiver, tg-channel-posts-poller, tg-discussion-receiver, tt-client-videos-fetcher, tt-profile-videos-poller, tt-video-comments-fetcher, web-gdelt-poller, web-search-mojeek, web-search-perplexity, x-filtered-stream, x-full-archive-search, x-replies-fetcher, x-user-timeline-poller, yt-comments-fetcher, yt-pubsub-receiver, yt-replies-fetcher, yt-text-purger, yt-uploads-reconciler | fb-backfill 6.2 L102; fb-client-webhook-receiver 6.2 L124; 8 L151; fb-group-comments-fetcher 6.2 L119; fb-group-posts-poller 5.2 L60; 6.2 L116; fb-keyword-search 6.2 L111; fb-page-feed-poller 5.2 L58; 6.2 L122; fb-page-search 8 L138; fb-post-comments-fetcher 6.2 L114; ig-account-media-poller 5.2 L62; 6.2 L118; ig-comments-fetcher 6.2 L107; 9 L143; ig-keyword-search 5.2 L62; 6.2 L110; ig-mentions-fetcher 5.2 L59; 6.2 L118; ig-own-comments-fetcher 6.2 L121; ig-webhook-receiver 6.2 L117; li-client-posts-poller 5.2 L60; 6.2 L119; li-company-posts-poller 5.2 L60; 6.2 L116; li-notification-receiver 6.2 L127; li-own-comments-fetcher 5.2 L63; 6.2 L120; +1 more; li-post-comments-fetcher 5.2 L65; 6.2 L122; li-post-search 6.2 L83; news-article-extractor 6.2 L105; 5.3 L75; tg-bot-channel-receiver 6.2 L128; tg-channel-posts-poller 5.2 L65; 6.2 L121; tg-discussion-receiver 6.2 L132; tt-client-videos-fetcher 6.2 L108; tt-profile-videos-poller 5.2 L61; 6.2 L119; tt-video-comments-fetcher 5.2 L61; 6.2 L113; +1 more; web-gdelt-poller 4 L35; 6.2 L108; web-search-mojeek 4 L36; 6.2 L104; web-search-perplexity 4 L35; 6.2 L105; x-filtered-stream 5.2 L63; 6.2 L129; x-full-archive-search 5.2 L54; 6.2 L121; x-replies-fetcher 5.2 L60; 6.2 L127; x-user-timeline-poller 5.2 L59; 6.2 L127; yt-comments-fetcher 5.2 L57; 6.2 L129; yt-pubsub-receiver 6.2 L117; yt-replies-fetcher 5.2 L54; 6.2 L118; yt-text-purger 5.3 L112; 13.4 L253; yt-uploads-reconciler 6.2 L122; 8 L156 |
| `raw/_quarantine/` | raw-archiver |  |  | raw-archiver 8 L138 |
| `raw/green/x/<yyyy>/<mm>/<dd>/x-compliance-sync/<run_id>.jsonl.zst` | x-compliance-sync |  |  | x-compliance-sync 5.2 L56; 6.2 L97; +2 more |
| `standard raw path (scan per-host aggregate)` | web-commoncrawl-scanner |  |  | web-commoncrawl-scanner 5.2 L54; 8 L123 |
| `versioned model bundle (fastText, dialect model, CAMeL Tools data, KLPT data)` |  | lang-dialect-id |  | lang-dialect-id 6.1 L100; 11 L158 |

### 4.4 Supabase Vault secrets

Secrets as each PRD describes them, grouped by service. Names are descriptions unless the PRD gives a name.

| Service | Secrets named or described |
|---|---|
| alert-evaluator | webhook and flow secrets (HMAC) |
| deletion-propagator | client webhook secrets |
| fb-backfill | Page access token (owned_by_client Pages); system-user token (per client, PPCA) |
| fb-client-webhook-receiver | Page access tokens; app secret; verify token |
| fb-group-comments-fetcher | vendor_keys (ScrapeCreators / SociaVault key) |
| fb-group-posts-poller | author_ref hash key; vendor_keys (ScrapeCreators / SociaVault key) |
| fb-keyword-search | vendor_keys (SociaVault / ScrapeCreators key) |
| fb-page-feed-poller | Page access token (owned_by_client Pages); system-user token (per client, PPCA) |
| fb-page-resolver | Page access token (owned_by_client Pages); system-user token (per client, PPCA) |
| fb-page-search | system-user token (per client, PPCA) |
| fb-post-comments-fetcher | Page access token (owned_by_client Pages); author_ref hash key; system-user token (PPCA) |
| fb-reactions-fetcher | Page access token (owned_by_client Pages); system-user token (per client, PPCA) |
| ig-account-media-poller | client Instagram user access token (per client; Facebook Login, Advanced Access) |
| ig-account-resolver | client Instagram user access token (calling client's business account) |
| ig-comments-fetcher | SociaVault vendor API key (via vendor_keys); author hash key |
| ig-hashtag-search | client token (long-lived Instagram user access token) |
| ig-keyword-search | SociaVault vendor API key (via vendor_keys) |
| ig-mentions-fetcher | owning client's Instagram user access token (connected account) |
| ig-own-comments-fetcher | owning client's Instagram user access token |
| ig-webhook-receiver | app secret; client token (subscription management); verify token |
| li-client-posts-poller | client OAuth token (secret name not stated) |
| li-company-posts-poller | Apify token (secret name not stated) |
| li-notification-receiver | app client secret (secret name not stated); client OAuth tokens (secret names not stated) |
| li-org-resolver | Apify token (secret name not stated); per-client LinkedIn tokens (secret names not stated) |
| li-own-comments-fetcher | client OAuth token (secret name not stated) |
| li-post-comments-fetcher | Apify token (secret name not stated); hashing salt (secret name not stated) |
| li-post-search | Apify token (secret name not stated) |
| news-article-extractor | proxy credentials (Decodo or Oxylabs keys) |
| news-comments-fetcher | Disqus API key; HMAC key (commenter hashing) |
| news-feed-poller | proxy credentials (Decodo or Oxylabs keys) |
| news-homepage-differ | proxy credentials (Decodo or Oxylabs keys) |
| news-robots-checker | proxy credentials (Decodo or Oxylabs keys) |
| news-site-resolver | proxy and headless credentials (Decodo or Oxylabs keys) |
| news-sitemap-poller | proxy credentials (Decodo or Oxylabs keys) |
| normalize-item | AUTHOR_HASH_KEY |
| poster-resolver | author_hash salt |
| qualifier | n8n callback signing secret |
| quota-governor | Supabase Vault (unspecified) |
| registry-writer | secrets (unnamed) |
| retention-purger | AUTHOR_HASH_KEY; client secrets |
| search-hit-router | (unnamed) database credentials |
| source-health-canary | platform tokens (per call) |
| store-writer | ClickHouse and Redpanda credentials |
| tg-bot-channel-receiver | bot token |
| tg-channel-posts-poller | vendor token (Apify) |
| tg-channel-resolver | Telemetrio API key |
| tg-discussion-receiver | discussion bot token; hashing secret |
| tg-message-search | Telemetrio API key |
| tt-client-videos-fetcher | app client key and secret; the account's token record (access and refresh tokens, expiry times) |
| tt-hashtag-feed-poller | vendor keys (TikHub, EnsembleData) |
| tt-keyword-search | vendor keys (TikHub, EnsembleData) |
| tt-profile-videos-poller | TikHub API key (vendor_keys) |
| tt-user-resolver | vendor key (TikHub, EnsembleData) |
| tt-video-comments-fetcher | author_hash HMAC key; vendor key (TikHub, EnsembleData) |
| tt-video-stats-refresher | vendor key (TikHub, EnsembleData) |
| web-search-mojeek | (unnamed) Mojeek API key |
| web-search-perplexity | (unnamed) Perplexity API key |
| x-compliance-sync | AUTHOR_HASH_KEY; X app token |
| x-filtered-stream | company X app bearer token |
| x-full-archive-search | app bearer token of the company X app |
| x-recent-search | app bearer token of the company X app |
| x-replies-fetcher | author-hash key; company app's bearer token |
| x-user-resolver | candidate_ref HMAC key; company app bearer token |
| x-user-timeline-poller | app bearer token of the company X app |
| yt-channel-resolver | company app API key (YouTube Data API v3) |
| yt-comments-fetcher | author-hash key; company app API key (YouTube Data API v3) |
| yt-keyword-search | company app API key (YouTube Data API v3) |
| yt-pubsub-receiver | hub secrets |
| yt-replies-fetcher | author-hash key; company app API key (YouTube Data API v3) |
| yt-uploads-reconciler | company app API key (YouTube Data API v3) |
| yt-video-details-fetcher | company app API key (YouTube Data API v3) |
| yt-web-search-bridge | Mojeek API key; Perplexity API key |

### 4.5 Other state

In-process and other state each PRD names (leader locks, caches, in-memory maps, spools), grouped by service. Listed for completeness; none of it is a shared contract unless another section names it.

| Service | State named |
|---|---|
| aggregator | leader lock (Postgres advisory lock) |
| alert-evaluator | rule cache, registry cache, consumer offsets, leader lock (Postgres advisory lock) |
| analysis-entities | KB and alias index in memory by kb_version; annotation tool store (self-hosted); registry cache, LRU of done keys, consumer offsets |
| analysis-media | LRU of recent hashes, consumer offsets; annotation tool store (self-hosted) |
| analysis-sentiment | LRU of analysed keys, hit-join buffer, registry cache, consumer offsets; annotation tool store (Argilla or Label Studio) |
| analysis-topics | LRU of done keys, registry and taxonomy caches, consumer offsets; annotation tool store (same as analysis-sentiment); centroid table of yesterday's clusters |
| backfill-orchestrator | Postgres advisory lock (safety-net scan leader election) |
| comment-decay-scheduler | Postgres advisory lock (leader-elected scan loop) |
| deletion-propagator | 7-day news full-text cache; consumer offsets and leader lock (Postgres advisory lock); purge registry (listening-sdk); text index |
| fb-client-webhook-receiver | Postgres advisory lock (audit loop leader election); in-memory source map (copy of sources) |
| fb-group-comments-fetcher | in-memory buffer of new comments (per fetch) |
| fb-group-posts-poller | Postgres advisory lock (scheduler leader election) |
| fb-keyword-search | Postgres advisory lock (scheduler leader election) |
| fb-page-feed-poller | Postgres advisory lock (scheduler leader election); token health (healthy / degraded) |
| fb-page-resolver | Postgres advisory lock (refresh loop leader election) |
| fb-page-search | Postgres advisory lock (weekly scheduler leader election) |
| fb-post-comments-fetcher | in-memory buffer of new comments (per fetch) |
| fb-reactions-fetcher | Redpanda consumer group fb-reactions-fetcher (raw.items offsets) |
| ig-account-media-poller | Postgres advisory lock (rotation scheduler leader); in-memory leader lock and backoff state |
| ig-account-resolver | Postgres advisory lock (refresh scheduler leader); in-memory leader lock and backoff state |
| ig-comments-fetcher | in-memory backoff state |
| ig-keyword-search | Postgres advisory lock (rotation scheduler leader); in-memory leader lock and backoff state |
| ig-mentions-fetcher | Postgres advisory lock (rotation scheduler leader); in-memory leader lock and backoff state; what ig-webhook-receiver stored |
| ig-own-comments-fetcher | in-memory backoff state |
| ig-webhook-receiver | Postgres advisory lock (reconciliation scheduler leader); in-memory one-hour request memory; job results of the two fetching services; pushed comment count per post |
| keyword-matcher | compiled automata per client and lang_model_version (in memory); keyword and client caches with updated_at marks; last_hit_at coalescing buffer; registry cache (last source.events offset) |
| lang-dialect-id | in-memory models, thresholds and lang_model_version |
| li-client-posts-poller | Postgres advisory lock (rotation scheduler leader); in-memory backoff state; stored post ids of the last 7 days (store not named) |
| li-company-posts-poller | Postgres advisory lock (rotation scheduler leader); in-memory backoff state |
| li-notification-receiver | held copy of the comment (store not named) |
| li-own-comments-fetcher | series state (owned by comment-decay-scheduler; table not named) |
| li-post-comments-fetcher | in-memory backoff state; series state (owned by comment-decay-scheduler; table not named); stored post (post URL; store not named) |
| news-article-extractor | per-host queues and backoff state (in memory); parked URLs awaiting a policy |
| news-comments-fetcher | backoff state (in memory) |
| news-dedup | Postgres advisory lock (hourly sweep leader); consumer offsets |
| news-feed-poller | Postgres advisory lock (leader scheduler) |
| news-homepage-differ | Postgres advisory lock (leader scheduler) |
| news-robots-checker | Postgres advisory lock (leader scheduler); per-host cooldown timers (in memory) |
| news-sitemap-poller | Postgres advisory lock (leader scheduler) |
| normalize-item | LRU dedup cache (last 1,000,000 keys, in memory); consumer offsets per partition (Redpanda); registry cache (in memory, version = last source.events offset) |
| quota-governor | short row cache and leader lock (Postgres advisory lock) |
| raw-archiver | Postgres advisory lock (nightly compaction leader); consumer offsets and open buffers (in memory) |
| retention-purger | cache (verification at the same cut-off); leader lock (Postgres advisory lock) |
| search-hit-router | registered-domain cache (in memory) |
| source-health-canary | Postgres advisory lock (leader-elected loop); SDK per-call route counters (Prometheus); audit trail (health flips; table not named); rolling 15-minute window per route (in memory), current state and last flip time |
| store-writer | per-table in-memory batches, consumer offsets, dimension sync marks |
| tg-bot-channel-receiver | chat map (in memory); getUpdates offset; leader lock (Postgres advisory lock) |
| tg-channel-posts-poller | backoff state (in memory); batch buffers (in memory); leader lock (Postgres advisory lock) |
| tg-channel-resolver | cache (poster.profiles younger than 30 days); cost_units |
| tg-discussion-receiver | getUpdates offset; group map (in memory); leader lock (Postgres advisory lock); tg_thread_map |
| tt-client-videos-fetcher | Postgres advisory lock (rotation scheduler leader election); in-memory backoff state |
| tt-hashtag-feed-poller | in-run set of video ids seen; scheduler leader (mechanism not stated) |
| tt-keyword-search | scheduler leader replica (mechanism not stated) |
| tt-profile-videos-poller | Postgres advisory lock (rotation scheduler leader election); in-memory backoff state |
| tt-user-resolver | in-memory backoff state; route health (location not stated) |
| tt-video-comments-fetcher | in-memory backoff state; route health (location not stated) |
| tt-video-stats-refresher | in-memory backoff state; route health (location not stated); written observation keys (store not stated) |
| web-commoncrawl-scanner | leader lock (Postgres advisory lock) |
| web-gdelt-poller | leader lock (Postgres advisory lock) |
| web-search-mojeek | leader lock (Postgres advisory lock) |
| web-search-perplexity | leader lock (Postgres advisory lock) |
| x-compliance-sync | audit exports (CSV and JSON Lines with SHA-256 manifest); caches; leader lock (Postgres advisory lock); raw-archiver archive index; text index |
| x-filtered-stream | blocked-terms list; in-memory state (lock, buffer, author map, per-rule rates); leader lock (Postgres advisory lock); read ledger; spool (pod volume) |
| x-full-archive-search | read ledger; x-user-resolver's last profile |
| x-recent-search | in-memory state (leader lock, backoff state, rate-limit headers); leader lock (Postgres advisory lock); read ledger |
| x-replies-fetcher | in-memory backoff state; read ledger |
| x-user-resolver | client watchlists; in-memory backoff state; leader lock (Postgres advisory lock); read ledger |
| x-user-timeline-poller | in-memory backoff state; leader lock (Postgres advisory lock); read ledger |
| yt-channel-resolver | backoff state (in memory); leader lock (Postgres advisory lock); open batches (in memory) |
| yt-comments-fetcher | backoff state (in memory) |
| yt-keyword-search | leader lock in the control plane |
| yt-pubsub-receiver | channel map (in-memory copy of sources); leader lock (Postgres advisory lock); seen ledger (listening-sdk idempotency helper) |
| yt-text-purger | Arabic text index; caches; leader lock (Postgres advisory lock); raw-archiver manifests |
| yt-uploads-reconciler | backoff state (in memory); leader lock (Postgres advisory lock); listening-sdk idempotency helper; per-channel missed-push history |
| yt-video-details-fetcher | missed-once mark; priority buffers and slots (worker memory) |
| yt-web-search-bridge | leader lock |

## 5. By budget tag

Every budget tag as written, with the services that use, define or mention it, the sub-counters or buckets they name, the priority they assign and the unit.

| Tag as written | Service (access) | Sub-counters or buckets | Priority as stated | Unit | Refs |
|---|---|---|---|---|---|
| `YouTube Data API units (tag string not written in this PRD)` | yt-web-search-bridge (mention) | list, search, reserve |  | units | 2 L15; 7 L137-L138; 8 L149; +1 more |
| `analysis_model_api` | analysis-entities (defines) |  |  |  | 7 L123 |
| `analysis_model_api` | analysis-media (defines) |  |  |  | 7 L118 |
| `analysis_model_api` | analysis-sentiment (defines) |  |  |  | 7 L119 |
| `analysis_model_api` | analysis-topics (defines) |  |  |  | 7 L126 |
| `fb_vendor` | backfill-orchestrator (mention) |  | lowest (backfill) |  | 5.3 L69 |
| `fb_vendor` | comment-decay-scheduler (mention) |  |  | credits/requests | 5.3 L96; 7 L153 |
| `fb_vendor` | fb-group-comments-fetcher (uses) |  | hot-post extra fetches dropped first past 80% of the monthly budget; series steps delayed, never dropped | requests (ScrapeCreators) / credits (SociaVault); cost_units = billed requests | 2 L13; 5.1 L48; 5.2 L61; +3 more |
| `fb_vendor` | fb-group-posts-poller (uses) |  |  | requests (ScrapeCreators) / credits (SociaVault, 1 credit per request) | 2 L13; 5.1 L46; 5.2 L58; +4 more |
| `fb_vendor` | fb-keyword-search (uses) |  | variants in rank order; at 80% low-ranked variants are shed first, the main form of every rule still runs daily | credits (SociaVault, 1 credit per request) / requests (ScrapeCreators) | 2 L13; 5.1 L44; 5.2 L55; +2 more |
| `fb_vendor` | quota-governor (defines) |  |  | monthly spend (requests, credits or items) | 5.3 L82 |
| `gdelt_doc_api` | quota-governor (defines) |  |  | requests | 5.3 L69; 5.3 L83 |
| `gdelt_doc_api` | web-gdelt-poller (uses) |  |  | requests | 5.1 L43; 5.2 L55; 5.2 L60; +3 more |
| `ig_graph_<client_id>` | ig-hashtag-search (uses) |  |  | calls (one cost unit per call) | 5.2 L65; 5.2 L70; 6.3 L129; +1 more |
| `ig_graph_<ig_user_id>` | backfill-orchestrator (mention) |  | lowest (backfill) |  | 5.3 L70 |
| `ig_graph_<ig_user_id>` | ig-account-media-poller (uses) |  |  | calls (per-account call limits to be measured in the pilot) | 5.2 L60; 7 L134 |
| `ig_graph_<ig_user_id>` | ig-account-resolver (uses) |  |  | calls | 5.2 L58; 7 L136; 7 L137; +1 more |
| `ig_graph_<ig_user_id>` | ig-mentions-fetcher (uses) |  |  | calls (three reads per poll, 72 per connected account per day before paging) | 5.2 L57; 7 L134 |
| `ig_graph_<ig_user_id>` | ig-own-comments-fetcher (uses) |  |  | calls (50 comments per query; about N / 50 calls per full read plus nested replies) | 5.2 L59; 7 L137 |
| `ig_graph_<ig_user_id>` | ig-webhook-receiver (mention) |  |  |  | 7 L133 |
| `ig_graph_<ig_user_id>` | quota-governor (defines) |  |  |  | 5.3 L83 |
| `ig_hashtag_<ig_user_id>` | ig-account-media-poller (mention) |  |  | unique hashtags (30 per account per 7 days) | 7 L134 |
| `ig_hashtag_<ig_user_id>` | ig-hashtag-search (uses) |  |  | unique hashtags per client business account per rolling 7 days (30) | 3 L22; 5.1 L57; 5.2 L65; +1 more |
| `ig_hashtag_<ig_user_id>` | ig-keyword-search (mention) |  |  |  | 3 L26; 13.4 L169 |
| `ig_hashtag_<ig_user_id>` | quota-governor (defines) |  |  | unique hashtags | 5.3 L81; 13.6 L160 |
| `ig_vendor` | comment-decay-scheduler (mention) |  |  | credits | 5.3 L96; 7 L153 |
| `ig_vendor` | ig-comments-fetcher (uses) | per service (ig-comments-fetcher) |  | credits (1 credit per request); the counter equals credits times the contracted USD rate; monthly budget in USD | 2 L13; 5.2 L59; 6.3 L119; +4 more |
| `ig_vendor` | ig-keyword-search (uses) | per service (ig-keyword-search), monthly spend counter per source |  | credits (1 credit per request / page); counter equals credits times the contracted USD rate; monthly budget in USD | 2 L13; 5.1 L49; 5.2 L59; +5 more |
| `ig_vendor` | quota-governor (defines) |  |  | monthly spend | 5.3 L82 |
| `li_vendor_<action>` | quota-governor (defines) |  |  | monthly spend | 5.3 L82 |
| `li_vendor_company_posts` | backfill-orchestrator (mention) |  | lowest (backfill) |  | 5.3 L74 |
| `li_vendor_company_posts` | li-company-posts-poller (uses) |  |  | items (one unit per returned item, including items dropped as already seen) | 2 L13; 5.2 L58; 6.3 L127; +3 more |
| `li_vendor_org_resolver` | li-org-resolver (uses) |  |  | items (20 units per candidate; cost_units = dataset items read, at most 20) | 5.2 L54; 6.3 L109; 7 L113; +1 more |
| `li_vendor_post_comments` | comment-decay-scheduler (mention) |  |  | items (Apify) | 5.3 L96; 7 L153 |
| `li_vendor_post_comments` | li-post-comments-fetcher (uses) |  |  | items (one unit per returned item) | 2 L13; 5.2 L61; 6.3 L133; +2 more |
| `li_vendor_post_search` | li-post-search (uses) |  |  | items (one unit per returned item) | 5.2 L58; 6.3 L109; 7 L113; +1 more |
| `linkedin_cm:<client_id>` | backfill-orchestrator (mention) |  | lowest (backfill) |  | 5.3 L73 |
| `linkedin_cm:<client_id>` | li-client-posts-poller (uses) |  |  | calls (one unit per API call) | 5.2 L58; 7 L136 |
| `linkedin_cm:<client_id>` | li-notification-receiver (uses) |  |  | calls (one unit per call) | 5.3 L74; 6.1 L108; 7 L143 |
| `linkedin_cm:<client_id>` | li-own-comments-fetcher (uses) |  |  | calls (one unit per API call) | 5.2 L59; 7 L137 |
| `linkedin_cm:<client_id>` | quota-governor (defines) |  |  |  | 5.3 L83 |
| `meta_*` | quota-governor (defines) |  |  |  | 5.3 L83 |
| `meta_graph_pages:<client_id>` | backfill-orchestrator (mention) |  | lowest (backfill) | quota | 5.3 L68 |
| `meta_graph_pages:<client_id>` | fb-backfill (uses) |  | metered below rotation polls (no number given) | calls | 5.1 L45; 5.2 L53; 7 L118; +3 more |
| `meta_graph_pages:<client_id>` | fb-client-webhook-receiver (uses) |  |  | calls | 5.2 L57; 7 L141 |
| `meta_graph_pages:<client_id>` | fb-page-feed-poller (uses) |  |  | calls | 5.2 L56; 6.3 L133; 7 L137; +1 more |
| `meta_graph_pages:<client_id>` | fb-page-resolver (uses) |  | yields to feed polling: on wait-until or deny the job waits | calls | 5.2 L56; 7 L136; 7 L139 |
| `meta_graph_pages:<client_id>` | fb-page-search (uses) |  | below rotation polls and comment series; last among green Facebook services | calls | 2 L13; 5.2 L51; 7 L127; +2 more |
| `meta_graph_pages:<client_id>` | fb-post-comments-fetcher (uses) |  | hot-post extra fetches dropped first; series steps never dropped | calls (cost_units = number of Graph calls made) | 5.2 L63; 5.3 L83; 7 L133; +2 more |
| `meta_graph_pages:<client_id>` | fb-reactions-fetcher (uses) |  | third: rotation polls first, comment series second, metrics refreshes third; +7 d refreshes dropped before +24 h ones when short | calls (cost_units_total 1 per call) | 5.2 L53; 7 L134; 7 L136; +1 more |
| `meta_graph_pages:<client_id>` | quota-governor (defines) |  |  | calls | 5.3 L80; 13.5 L159 |
| `mojeek_search` | quota-governor (defines) |  |  |  | 5.3 L83 |
| `mojeek_search` | web-search-mojeek (uses) |  |  | queries (cap held in GBP) | 2 L17; 5.1 L44; 5.2 L55; +4 more |
| `mojeek_search` | yt-web-search-bridge (uses) |  |  | queries (GBP 3 per 1,000) | 5.2 L56; 7 L136; 13.1 L178 |
| `news_*` | quota-governor (defines) |  |  |  | 5.3 L83 |
| `news_disqus` | news-article-extractor (mention) |  |  |  | 7 L135 |
| `news_disqus` | news-comments-fetcher (uses) |  | scheduled steps outrank hot-post extras; past 80% quota-governor drops hot-post extras first and never the scheduled steps | requests (one request is one unit, cost_units) | 5.1 L47; 5.2 L54; 7 L128; +2 more |
| `news_disqus` | news-dedup (mention) |  |  |  | 7 L114 |
| `news_disqus` | news-feed-poller (mention) |  |  |  | 7 L125 |
| `news_disqus` | news-homepage-differ (mention) |  |  |  | 7 L130 |
| `news_disqus` | news-robots-checker (mention) |  |  |  | 7 L127 |
| `news_disqus` | news-sitemap-poller (mention) |  |  |  | 7 L139 |
| `news_proxy_egress` | news-article-extractor (uses) |  |  | not stated (price per GB to be measured in the pilot; page weight with images blocked is the key number) | 5.3 L67; 7 L135 |
| `news_proxy_egress` | news-comments-fetcher (mention) |  |  |  | 7 L131 |
| `news_proxy_egress` | news-dedup (mention) |  |  |  | 7 L114 |
| `news_proxy_egress` | news-feed-poller (uses) |  |  | proxy bytes (cost_units_total); price per GB to be measured in the pilot | 7 L125; 10 L148 |
| `news_proxy_egress` | news-homepage-differ (uses) |  |  | not stated (price per GB to be measured in the pilot) | 7 L128 |
| `news_proxy_egress` | news-robots-checker (uses) |  |  | not stated (price per GB to be measured in the pilot) | 5.3 L79; 7 L127; 12 L161 |
| `news_proxy_egress` | news-site-resolver (uses) |  |  | not stated (price per GB to be measured in the pilot) | 7 L122 |
| `news_proxy_egress` | news-sitemap-poller (uses) |  |  | bytes (price per GB to be measured in the pilot) | 7 L137; 12 L169 |
| `perplexity_search` | quota-governor (defines) |  |  |  | 5.3 L83 |
| `perplexity_search` | web-search-perplexity (uses) |  |  | requests | 2 L17; 5.2 L53; 5.2 L57; +3 more |
| `perplexity_search` | yt-web-search-bridge (uses) |  |  | requests (USD 5 per 1,000; up to 5 queries a request) | 5.2 L56; 7 L136; 13.2 L179 |
| `tg_*` | quota-governor (defines) |  |  | monthly spend | 5.3 L82 |
| `tg_apify_posts` | backfill-orchestrator (mention) |  | lowest (backfill) |  | 5.3 L75 |
| `tg_apify_posts` | tg-channel-posts-poller (uses) |  | no number given: at 80% of the monthly budget the governor stretches in the order backfill jobs first, then views refreshes, then Tier 2, then Tier 1; backfill is 'the lowest priority at the governor'; no tier stretched beyond 24 hours, Tier 3 stays daily, dormant weekly | USD (monthly cap; usage cost Apify reports per run); allowance is asked 'for the batch's expected item count' | 2 L13; 5.1 L52; 5.1 L54; +5 more |
| `tg_telemetrio_search` | tg-message-search (uses) | requests, keywords | no number given: at 80% of the monthly budget quota-governor answers wait-until for the sets lowest on client priority lists; at 100% it denies (a denied set is reported to its client); a daily cadence cannot be stretched below daily | requests and keywords (two cost_units counters) | 5.1 L46; 5.2 L52; 5.3 L60; +3 more |
| `tg_telemetrio_stats` | tg-channel-resolver (uses) | requests this month, distinct channels queried | no number given: refresh jobs are stretched by quota-governor at 80% of the plan's channel allowance; discovery and client jobs are never stretched, only denied with a reason the client sees | units: 'one unit' per channel stats request; plan allowance counted in channels | 5.1 L47; 5.2 L55; 6.3 L108; +2 more |
| `tt_display:<client_id>` | quota-governor (defines) |  |  |  | 5.3 L83 |
| `tt_display:<client_id>` | tt-client-videos-fetcher (uses) |  |  | requests (request quota; USD 0 per Display API call) | 5.2 L57; 6.3 L119; 7 L123; +1 more |
| `tt_vendor` | backfill-orchestrator (mention) |  | lowest (backfill) | requests (20 items a page) | 5.3 L71; 13.6 L154 |
| `tt_vendor` | comment-decay-scheduler (mention) |  |  | requests | 5.3 L96; 7 L153 |
| `tt_vendor` | quota-governor (defines) | per-service sub-counters |  | monthly spend | 5.3 L82; 7 L115 |
| `tt_vendor` | tt-client-videos-fetcher (mention) |  |  |  | 7 L123; 12 L157; 13.8 L169 |
| `tt_vendor` | tt-hashtag-feed-poller (uses) |  |  | requests (cost_units = HTTP 200 responses; an empty 200 still costs) | 5.1 L44; 5.2 L56; 5.2 L59; +3 more |
| `tt_vendor` | tt-keyword-search (uses) |  |  | requests (cost_units = HTTP 200 responses; an empty 200 still costs) | 5.1 L42; 5.2 L50; 5.2 L53; +4 more |
| `tt_vendor` | tt-profile-videos-poller (uses) | profile_videos |  | requests (TikHub bills HTTP 200 only) | 5.1 L49; 5.2 L59; 6.3 L130; +4 more |
| `tt_vendor` | tt-user-resolver (uses) | user_info |  | requests (one per uncached candidate; TikHub billed on HTTP 200 only) | 5.2 L54; 6.3 L115; 7 L119; +2 more |
| `tt_vendor` | tt-video-comments-fetcher (uses) | video_comments |  | requests (20 comments a page; TikHub billed on HTTP 200 only) | 5.1 L46; 5.2 L58; 6.3 L123; +5 more |
| `tt_vendor` | tt-video-stats-refresher (uses) | video_stats |  | requests (two per video; TikHub billed on HTTP 200 only) | 5.1 L50; 5.2 L56; 6.3 L116; +3 more |
| `x_pay_per_use` | backfill-orchestrator (mention) |  | lowest (backfill) | post reads at USD 0.005 | 5.3 L72 |
| `x_pay_per_use` | comment-decay-scheduler (mention) |  |  | USD 0.005 per reply read | 7 L153 |
| `x_pay_per_use` | quota-governor (defines) | post_reads, user_reads |  | post_reads (USD 0.005 each), user_reads (USD 0.010 each) | 5.3 L78; 6.2 L100-L104 |
| `x_pay_per_use` | x-compliance-sync (uses) |  | not stated; 14.3 proposes quota-governor reserve compliance ahead of all other X reads and never deny it | post reads (only if compliance jobs are metered) | 4 L36; 5.2 L53; 7 L138; +2 more |
| `x_pay_per_use` | x-filtered-stream (uses) | post_reads | <highest matched> rule priority: 1 = brand keyword sets and tier-1 accounts, 2 = tier-2, 3 = tier-3 | post reads | 2 L13; 4 L31; 5.2 L62; +3 more |
| `x_pay_per_use` | x-full-archive-search (uses) | post_reads, user_reads | 5 for backfill; 1 for client requests (keyword_history, replies) | post reads (USD 0.005); user reads (USD 0.010) only if the author_id expansion is billed | 5.2 L53-L54; 7 L136-L140; 13.1 L175; +2 more |
| `x_pay_per_use` | x-recent-search (uses) |  | not numeric here: at 80% of the cap quota-governor cuts x-full-archive-search jobs first, then stretches tier-2 and tier-3 searches to daily, then drops reply steps after +24 h; tier-1 searches, the stream and tier-1 timelines go last | post reads (USD 0.005); user reads (USD 0.010) | 5.2 L55; 5.2 L59; 6.2 L116-L118; +5 more |
| `x_pay_per_use` | x-replies-fetcher (uses) | post_reads, user_reads | from series_step: 2 = +1 h, +6 h, +24 h; 3 = +3 d, extensions and refreshes; 4 = hot-post extras | post reads (a reply is a post, USD 0.005); user reads (USD 0.010) | 5.2 L55; 5.2 L57; 7 L142-L145; +1 more |
| `x_pay_per_use` | x-user-resolver (uses) | user_reads | 4 | user reads (USD 0.010) | 5.2 L55; 7 L140-L142; 13.1 L177; +1 more |
| `x_pay_per_use` | x-user-timeline-poller (uses) | post_reads | 1 for tier 1 and ops_force, 2 for tier 2, 3 otherwise | post reads (USD 0.005); amount 100 per page | 5.2 L56; 5.2 L58; 7 L142-L144; +3 more |
| `youtube_data_api` | backfill-orchestrator (mention) |  | lowest (backfill) | units (1 a page of 50) | 5.3 L77 |
| `youtube_data_api` | quota-governor (defines) | search, ingest, comments, reserve |  | units | 5.3 L79; 13.4 L158 |
| `youtube_data_api` | yt-channel-resolver (uses) | search, ingest, comments, reserve | 4 | units (1 unit per channels.list call, batched up to 50 ids; one per handle) | 5.2 L60; 7 L142-L144; 8 L150; +2 more |
| `youtube_data_api` | yt-comments-fetcher (uses) | comments | from series_step: 2 = steps up to +24 h; 3 = later steps and extensions; 4 = hot-post extras; client refreshes proposed 3 (14.2) | units (1 unit per commentThreads.list page) | 5.2 L53; 7 L144-L148; 13.10 L197; +1 more |
| `youtube_data_api` | yt-keyword-search (uses) | search |  | units (100 per search.list call; amount requested = terms x 100) | 5.2 L56; 7 L132-L134; 10 L157; +1 more |
| `youtube_data_api` | yt-pubsub-receiver (mention) |  |  | units | 2 L13; 7 L138-L140; 13.10 L184 |
| `youtube_data_api` | yt-replies-fetcher (uses) | comments | 3 for steps, extensions and client refreshes; 4 for hot-thread extras | units (1 unit per comments.list page of up to 100 replies) | 5.2 L50; 7 L133-L136; 13.11 L185 |
| `youtube_data_api` | yt-text-purger (uses) | comments, ingest | 3 | units (estimate: 1 per 100 threads; 1 per comments.list page for each due thread above 5 replies; 1 per 50 videos) | 5.3 L84-L92; 7 L185; 7 L187-L188; +1 more |
| `youtube_data_api` | yt-uploads-reconciler (uses) | ingest | the job's priority: reach tier 1, 2 or 3; dormant 3; ops_force and source-health-canary probes 1; backfill 5 | units (1 per playlistItems.list page of up to 50) | 5.1 L45; 5.2 L61; 7 L144-L147; +1 more |
| `youtube_data_api` | yt-video-details-fetcher (uses) | ingest | 1 for Tier 1 first sight, client refreshes and ops_force; 2 for metrics at +24 h; 3 for metrics at +7 d and live re-checks; 5 for backfill first sight; proposed 1 for first sight from other tiers and keyword rules; asks at the priority of the call's highest member | units (1 per videos.list call of up to 50 ids) | 5.1 L50; 5.2 L59; 7 L163-L164; +3 more |

## 6. Flags and configuration

### 6.1 Vendor route flags

| Flag | Service (access) | Values as stated | Default | Refs |
|---|---|---|---|---|
| `FB_VENDOR_ROUTE` | comment-decay-scheduler (reads) | off |  | 5.1 L44 |
| `FB_VENDOR_ROUTE` | fb-group-comments-fetcher (reads) | off, scrapecreators, sociavault |  | header L3; 1 L7; +4 more |
| `FB_VENDOR_ROUTE` | fb-group-posts-poller (reads) | off, scrapecreators, sociavault |  | header L3; 3 L20; +5 more |
| `FB_VENDOR_ROUTE` | fb-keyword-search (reads) | off, sociavault, scrapecreators |  | header L3; 1 L9; +4 more |
| `FB_VENDOR_ROUTE` | qualifier (reads) | off, sociavault |  | 5.2 L59; 11 L128; +1 more |
| `FB_VENDOR_ROUTE` | source-health-canary (reads) |  |  | 5.1 L47 |
| `IG_VENDOR_ROUTE` | comment-decay-scheduler (reads) | off |  | 5.1 L44 |
| `IG_VENDOR_ROUTE` | ig-account-media-poller (mention) |  |  | 5.1 L54 |
| `IG_VENDOR_ROUTE` | ig-comments-fetcher (reads) | off, sociavault |  | header L3; 1 L9; +9 more |
| `IG_VENDOR_ROUTE` | ig-hashtag-search (reads) |  |  | 4 L38; 5.2 L64; +2 more |
| `IG_VENDOR_ROUTE` | ig-keyword-search (reads) | off, sociavault |  | header L3; 2 L13; +6 more |
| `IG_VENDOR_ROUTE` | ig-mentions-fetcher (mention) |  |  | 5.1 L51 |
| `IG_VENDOR_ROUTE` | qualifier (reads) |  |  | 11 L128 |
| `LI_VENDOR_ROUTE` | comment-decay-scheduler (reads) | off |  | 5.1 L44 |
| `LI_VENDOR_ROUTE` | li-client-posts-poller (mention) |  |  | 1 L7 |
| `LI_VENDOR_ROUTE` | li-company-posts-poller (reads) | off, harvestapi |  | header L3; 1 L7; +8 more |
| `LI_VENDOR_ROUTE` | li-org-resolver (reads) | off, harvestapi |  | header L3; 1 L9; +4 more |
| `LI_VENDOR_ROUTE` | li-post-comments-fetcher (reads) | off, harvestapi |  | header L3; 1 L7; +7 more |
| `LI_VENDOR_ROUTE` | li-post-search (reads) | off, harvestapi |  | header L3; 1 L9; +6 more |
| `LI_VENDOR_ROUTE` | poster-resolver (reads) | off |  | 5.2 L56 |
| `LI_VENDOR_ROUTE` | qualifier (reads) |  |  | 11 L128 |
| `TG_POSTS_ACTOR` | source-health-canary (reads) |  |  | 5.1 L47 |
| `TG_POSTS_ACTOR` | tg-channel-posts-poller (reads) | off, tugelbay, sovereigntaylor |  | header L3; 1 L7; +7 more |
| `TG_VENDOR_ROUTE` | poster-resolver (reads) | off |  | 5.2 L56 |
| `TG_VENDOR_ROUTE` | qualifier (reads) |  |  | 11 L128 |
| `TG_VENDOR_ROUTE` | tg-channel-resolver (reads) | off, any value other than off (treated as on) | off | header L3; 1 L9; +6 more |
| `TG_VENDOR_ROUTE` | tg-message-search (reads) | off, any value other than off (treated as on) | off | header L3; 1 L9; +6 more |
| `TT_VENDOR_ROUTE` | comment-decay-scheduler (reads) | off |  | 5.1 L44 |
| `TT_VENDOR_ROUTE` | poster-resolver (reads) | off |  | 5.2 L56; 5.4 L76; +1 more |
| `TT_VENDOR_ROUTE` | qualifier (reads) |  |  | 11 L128 |
| `TT_VENDOR_ROUTE` | source-health-canary (reads) | off, (on) |  | 5.1 L47; 13.6 L152 |
| `TT_VENDOR_ROUTE` | tt-client-videos-fetcher (mention) | off |  | 1 L7; 13.9 L170 |
| `TT_VENDOR_ROUTE` | tt-hashtag-feed-poller (reads) | off, tikhub, ensembledata |  | header L3; 1 L9; +6 more |
| `TT_VENDOR_ROUTE` | tt-keyword-search (reads) | off, tikhub, ensembledata |  | header L3; 1 L9; +6 more |
| `TT_VENDOR_ROUTE` | tt-profile-videos-poller (reads) | off, tikhub, ensembledata |  | header L3; 1 L9; +6 more |
| `TT_VENDOR_ROUTE` | tt-user-resolver (reads) | off, tikhub, ensembledata |  | header L3; 1 L9; +3 more |
| `TT_VENDOR_ROUTE` | tt-video-comments-fetcher (reads) | off, tikhub, ensembledata |  | header L3; 1 L9; +3 more |
| `TT_VENDOR_ROUTE` | tt-video-stats-refresher (reads) | off, tikhub, ensembledata |  | header L3; 1 L9; +3 more |

### 6.2 Other switches and settings

Every other named flag, mode or setting, grouped by name. Kinds as the extraction recorded them: `feature_flag`, `config` (an environment or service setting), `registry_flag` (a flag held in a table).

| Name as written | Kind | Services (access) | Values or default as stated |
|---|---|---|---|
| `(unnamed) .iq second-level zone list` | config | web-commoncrawl-scanner (defines) |  |
| `(unnamed) clients government flag` | registry_flag | web-search-perplexity (reads) |  |
| `(unnamed) deduplication row expiry` | config | search-hit-router (defines) | default 180 days after the last sighting |
| `(unnamed) implausible-scan threshold` | config | web-commoncrawl-scanner (defines) |  |
| `(unnamed) keywords priority flag` | registry_flag | web-search-mojeek (reads), web-search-perplexity (reads) |  |
| `(unnamed) news-like rule` | config | search-hit-router (defines) | engine is GDELT, two of: publication date; date or news path segment; host under .iq |
| `(unnamed) parked-URL expiry` | config | search-hit-router (defines) | default 30 days (proposed; set in the pilot) |
| `(unnamed) per-client GDELT on/off` | registry_flag | web-gdelt-poller (mention) |  |
| `(unnamed) per-client Perplexity opt-out` | registry_flag | web-search-perplexity (reads) |  |
| `(unnamed) re-emission thresholds` | config | web-commoncrawl-scanner (defines) |  |
| `(unnamed) re-route window` | config | search-hit-router (defines) | default 30 days (proposed; set in the pilot) |
| `(unnamed) scan target window` | config | web-commoncrawl-scanner (defines) |  |
| `(unnamed) score weights` | config | web-commoncrawl-scanner (defines) |  |
| `(unnamed) time-window overlap` | config | web-gdelt-poller (defines) |  |
| `access_mode` | registry_flag | news-article-extractor (reads), news-feed-poller (reads), news-homepage-differ (reads), news-robots-checker (writes), news-site-resolver (reads), news-sitemap-poller (reads) | direct, headless, proxy, blocked; direct, headless, proxy |
| `AGG_CYCLE_SECONDS` | config | aggregator (defines) | default 60 |
| `AGG_MV_MODE` | config | aggregator (defines) | service |
| `AGG_OPEN_HOURS` | config | aggregator (defines) | default the current hour and the two before it |
| `AGG_RECONCILE_MINUTES` | config | aggregator (defines) | default 60 |
| `alert thresholds` | config | quota-governor (defines) | 50%, 80%, 95% |
| `ALERT_CLEAR_CYCLES` | config | alert-evaluator (defines) | default 5 |
| `ALERT_MAX_AGE_HOURS` | config | alert-evaluator (defines) | default 3 |
| `ALERT_POLL_SECONDS` | config | alert-evaluator (defines) | default 30 |
| `ALERT_RULE_POLL_SECONDS` | config | alert-evaluator (defines) | default 30 |
| `ALERT_STORM_LIMIT` | config | alert-evaluator (defines) | default from the pilot |
| `amber acceptance` | registry_flag | ig-comments-fetcher (reads), ig-keyword-search (reads) |  |
| `anchor-length threshold and heuristic thresholds` | config | news-homepage-differ (reads) |  |
| `API key degraded` | registry_flag | yt-channel-resolver (writes), yt-comments-fetcher (writes), yt-keyword-search (writes), yt-replies-fetcher (writes), yt-uploads-reconciler (writes), yt-video-details-fetcher (writes) | degraded |
| `Apify concurrency cap (environment variable, name not stated)` | config | li-company-posts-poller (reads), li-post-comments-fetcher (reads) |  |
| `Apify run wait interval (environment variable, name not stated)` | config | li-company-posts-poller (reads), li-post-comments-fetcher (reads) |  |
| `AUTHOR_HASH_KEY` | config | normalize-item (reads), retention-purger (reads) |  |
| `backfill deadline` | config | backfill-orchestrator (reads) | default environment variable, to be set in the pilot |
| `backfill_capped_rate alert threshold (name not stated)` | config | fb-backfill (defines) |  |
| `batch size` | config | keyword-matcher (defines), normalize-item (defines), tg-channel-posts-poller (reads) | default 500 items or 2 s; default 500 records or 2 s |
| `batch size and maximum wait` | config | analysis-sentiment (defines) | default set in the pilot |
| `batch sizes` | config | analysis-entities (defines), analysis-topics (defines) | default set in the pilot |
| `BATCH_WINDOW_MS` | config | yt-channel-resolver (reads) |  |
| `body size limit (name and value not stated)` | config | li-notification-receiver (reads) |  |
| `budget mode` | registry_flag | backfill-orchestrator (reads), comment-decay-scheduler (reads) | normal, stretch, exhausted |
| `cache lifetime` | config | tt-user-resolver (reads) | default 30 days |
| `canary period (per route)` | config | source-health-canary (reads) | default 5 minutes or less (at least three cycles per 15 minutes); longer on metered routes |
| `CANARY_MIN_SAMPLES` | config | source-health-canary (defines) | default to be set in the pilot |
| `capped heuristic threshold (posting-rate gap; name not stated)` | config | fb-backfill (defines) |  |
| `CC_MAX_HITS_PER_SCAN` | config | web-commoncrawl-scanner (defines) |  |
| `challenged share alert threshold` | config | news-site-resolver (reads) |  |
| `ckb_supported` | registry_flag | web-search-perplexity (writes) | true, false |
| `client's priority flag` | registry_flag | fb-page-search (reads) |  |
| `cluster size floor` | config | analysis-topics (defines) | default set in the pilot |
| `code-switch share` | config | analysis-sentiment (defines) | default chosen in the pilot |
| `combined or split-by-form query mode` | config | web-gdelt-poller (defines) | combined (one OR group per rule), split by language form (Latin, Arabic, Sorani) default combined (5.2 step 2, 13.1) |
| `company app's X plan setting` | config | x-replies-fetcher (reads) | Enterprise |
| `CONFIRM_INTERVAL` | config | yt-text-purger (reads) |  |
| `content expiry sentinel` | config | store-writer (defines) | default 2106-01-01 00:00:00 |
| `crawl_allowed` | registry_flag | news-article-extractor (reads), news-feed-poller (reads), news-homepage-differ (reads), news-robots-checker (writes), news-site-resolver (reads), news-sitemap-poller (reads) | True, False |
| `CRAWLER_USER_AGENT` | config | news-article-extractor (reads), news-feed-poller (reads), news-homepage-differ (reads), news-robots-checker (reads), news-site-resolver (reads), news-sitemap-poller (reads) | ListeningBot/1.0 (+<bot information page>; <contact mailbox>) |
| `creator threshold` | config | tt-user-resolver (reads) | default followers >= 2000 or verified |
| `creator_followers_tiktok` | config | qualifier (defines) | raise only default 2,000 |
| `cursor overlap` | config | yt-keyword-search (defines) | 6 hours default 6 hours |
| `cursor overlap (environment variable, name not stated)` | config | li-client-posts-poller (reads) |  |
| `deadline defaults` | config | deletion-propagator (defines) | default X 24 hours from the signal; author requests 7 days; client offboarding 30 days |
| `decay_days` | config | qualifier (defines) | shorten only default 90 |
| `degraded` | feature_flag | analysis-entities (defines) | true |
| `DELETE_MARGIN` | config | yt-text-purger (reads) |  |
| `deletion guard threshold` | config | yt-comments-fetcher (reads), yt-replies-fetcher (reads) |  |
| `deletion inference threshold` | config | tt-video-comments-fetcher (reads) | default two consecutive full reads (initial value, to be tuned in the pilot) |
| `DELETION_BATCH_WINDOW` | config | deletion-propagator (defines) | default to be measured in the pilot |
| `DIALECT_MIN_TOKENS` | config | lang-dialect-id (defines) | default set from the pilot sample |
| `DIM_POLL_SECONDS` | config | store-writer (defines) | default 30 |
| `Disqus per-second cap` | config | news-comments-fetcher (reads) |  |
| `dormant_days` | config | qualifier (defines) | fixed default 30 |
| `drift tolerance` | config | quota-governor (defines) | default set in the pilot |
| `early stop` | config | comment-decay-scheduler (defines) | default new_count < 5 and growth < 0.05, armed when before >= 5 or the +24 h step is reached |
| `empty 200 threshold (above 5% in 15 minutes)` | config | news-feed-poller (mention), news-homepage-differ (mention), news-sitemap-poller (mention) |  |
| `empty-200 threshold` | config | source-health-canary (defines) | default above 5% in a sliding 15-minute window |
| `engine degraded (canary)` | registry_flag | yt-web-search-bridge (mention) | degraded |
| `engine key degraded` | registry_flag | yt-web-search-bridge (writes) | degraded |
| `error outcome cache` | config | poster-resolver (defines) | default 24 hours for 5xx or timeouts |
| `estimate_drift threshold` | config | x-full-archive-search (reads) |  |
| `extension` | config | comment-decay-scheduler (defines) | default growth >= 0.20 at day 7 -> every 2 days to day 30 |
| `extra pages per term per day` | config | yt-keyword-search (defines) | 2 default 2 |
| `fallback mode` | config | ig-keyword-search (defines) |  |
| `fallback_off` | registry_flag | ig-hashtag-search (mention), ig-keyword-search (reads), source-health-canary (mention), tg-channel-posts-poller (mention) |  |
| `fallback_on` | registry_flag | backfill-orchestrator (mention), deletion-propagator (mention), fb-keyword-search (reads), fb-page-feed-poller (mention), fb-page-resolver (mention), fb-post-comments-fetcher (mention), ig-account-media-poller (mention), ig-account-resolver (mention), ig-comments-fetcher (mention), ig-hashtag-search (writes), ig-keyword-search (reads), ig-mentions-fetcher (mention), ig-own-comments-fetcher (mention), li-client-posts-poller (mention), li-company-posts-poller (mention), li-org-resolver (mention), li-post-comments-fetcher (mention), li-post-search (mention), news-comments-fetcher (mention), raw-archiver (mention), retention-purger (mention), source-health-canary (mention), tg-bot-channel-receiver (mention), tg-channel-posts-poller (mention), tg-discussion-receiver (mention), tt-hashtag-feed-poller (reads), tt-keyword-search (reads), tt-profile-videos-poller (reads), tt-user-resolver (reads), tt-video-comments-fetcher (reads), tt-video-stats-refresher (reads), web-commoncrawl-scanner (mention), web-gdelt-poller (mention), web-search-mojeek (mention), web-search-perplexity (mention), x-compliance-sync (mention), x-filtered-stream (mention), x-full-archive-search (mention), x-replies-fetcher (mention), x-user-resolver (mention), x-user-timeline-poller (mention), yt-channel-resolver (mention), yt-comments-fetcher (mention), yt-replies-fetcher (mention), yt-uploads-reconciler (mention) | fallback_on, fallback_off; fallback_on |
| `fallback_on / fallback_off` | registry_flag | fb-group-comments-fetcher (reads), fb-group-posts-poller (reads) | fallback_on, fallback_off |
| `FB_GROUP_REPLY_THRESHOLD` | config | fb-group-comments-fetcher (defines) |  |
| `FB_SEARCH_MAX_PAGES` | config | fb-keyword-search (defines) |  |
| `FIRST_SIGHT_FLUSH_SECONDS` | config | yt-video-details-fetcher (reads) |  |
| `flap guard` | config | source-health-canary (defines) | default at most one flip per route per 15-minute window |
| `flood threshold` | config | x-filtered-stream (reads) |  |
| `force` | config | li-org-resolver (reads) |  |
| `forced evaluation interval` | config | alert-evaluator (defines) | default 300 s |
| `frame interval / frame cap / duration cap / tier rules` | config | analysis-media (defines) | default set in the pilot |
| `government body (clients)` | registry_flag | tg-message-search (reads) |  |
| `government flag` | registry_flag | ig-comments-fetcher (reads), ig-keyword-search (reads) |  |
| `government flag (clients / client_ids)` | registry_flag | x-recent-search (mention) |  |
| `government flag (clients)` | registry_flag | li-company-posts-poller (reads), li-post-comments-fetcher (reads), quota-governor (reads), tg-channel-posts-poller (reads), tg-channel-resolver (reads) |  |
| `government marker (clients)` | registry_flag | li-post-search (reads) |  |
| `grace period` | config | x-filtered-stream (reads) |  |
| `Graph API version (environment variable, name not stated)` | config | ig-account-media-poller (reads), ig-mentions-fetcher (reads) |  |
| `Graph API version (v<pinned>)` | config | fb-backfill (reads), fb-page-search (reads), fb-reactions-fetcher (reads) |  |
| `Graph API version `v<pinned>`` | config | ig-account-resolver (reads), ig-own-comments-fetcher (reads) |  |
| `Graph API version pin (environment variable shared by all fb-* services; name not stated)` | config | fb-client-webhook-receiver (reads), fb-page-feed-poller (reads), fb-page-resolver (reads), fb-post-comments-fetcher (reads) |  |
| `green-route emergency allowance` | config | quota-governor (defines) | default small; size open (14.5) |
| `hashtag mode` | config | ig-keyword-search (defines) |  |
| `hashtag tier media-per-day thresholds` | config | ig-hashtag-search (mention) | default ops sets the tier at registration |
| `headroom reserve` | config | x-filtered-stream (reads) |  |
| `health` | registry_flag | registry-writer (writes), source-health-canary (defines), yt-channel-resolver (reads), yt-comments-fetcher (reads), yt-pubsub-receiver (writes), yt-replies-fetcher (reads), yt-text-purger (reads), yt-uploads-reconciler (writes), yt-video-details-fetcher (mention) | ok, degraded, fallback default ok; ok, degraded, fallback, blocked; degraded; blocked, degraded; ok, degraded |
| `homepage_diff` | registry_flag | news-homepage-differ (reads), news-site-resolver (writes) | True, False |
| `host spacing doubling period after 429 or 503` | config | news-article-extractor (reads) |  |
| `hot post` | config | comment-decay-scheduler (defines) | default velocity > 100 -> hourly extras for 6 h |
| `hot threshold (publishing rate for tier 1)` | config | news-site-resolver (reads) |  |
| `hot-site interval mapping (articles_per_day_estimate to 5, 10 or 15 minutes)` | config | news-feed-poller (reads) | 5, 10, 15 |
| `ig-keyword-search hashtag mode` | config | ig-hashtag-search (mention) |  |
| `iraqi_signals_required` | config | qualifier (defines) | 1 to 3 default 2 |
| `JOB_MAX_IDS` | config | x-compliance-sync (reads) |  |
| `JOB_POLL_SECONDS` | config | x-compliance-sync (reads) |  |
| `KEYWORD_POLL_SECONDS` | config | keyword-matcher (defines) | default 30 |
| `lag schedule` | config | aggregator (defines) | +1 h, +6 h, +24 h, +8 d, +31 d |
| `lane user agent (ListeningBot/1.0)` | config | news-comments-fetcher (reads) | ListeningBot/1.0 (+<bot information page>; <contact mailbox>) |
| `lang fallback threshold` | config | normalize-item (defines) | default 5 minutes of lang-dialect-id failures |
| `lang_model_version` | config | lang-dialect-id (defines) | default lid-iq-2026.09 (example) |
| `lang_share_min` | config | qualifier (defines) | 0.30 to 0.80 default 0.40 |
| `lapsed (yt_subscriptions.state)` | registry_flag | yt-pubsub-receiver (writes) | lapsed |
| `last_hit_at coalescing` | config | keyword-matcher (defines) | default one write per source per minute |
| `LEASE_RENEWAL_MARGIN` | config | yt-pubsub-receiver (reads) |  |
| `LEASE_SECONDS` | config | yt-pubsub-receiver (reads) |  |
| `legal hold` | config | retention-purger (defines) |  |
| `LID_MIN_CONF` | config | lang-dialect-id (defines) | default set from the pilot sample |
| `LID_MIN_LETTERS` | config | lang-dialect-id (defines) | default set from the pilot sample (to be measured) |
| `LID_MIXED_MIN_SHARE` | config | lang-dialect-id (defines) | default set from the pilot sample |
| `LID_SHORT_CAP` | config | lang-dialect-id (defines) | default set from the pilot sample |
| `link threshold and no-link rule per type` | config | analysis-entities (reads) | default validation split per version, stored in model_versions.thresholds |
| `link-count floor (headless switch)` | config | news-homepage-differ (reads) |  |
| `Linkedin-Version (environment variable shared by all li-* services, name not stated)` | config | li-client-posts-poller (reads), li-own-comments-fetcher (reads) |  |
| `LinkedIn-Version (monthly version pinned in the SDK)` | config | li-org-resolver (reads) |  |
| `live re-check interval` | config | yt-video-details-fetcher (reads) |  |
| `longest wait for a batch to fill` | config | tg-channel-posts-poller (reads) |  |
| `lookup window` | config | news-dedup (reads) | default 7 days (proposed starting window) |
| `LRU size` | config | normalize-item (defines) | default 1,000,000 keys |
| `margin` | config | x-filtered-stream (reads) |  |
| `max items cap per run (budgets)` | config | li-post-comments-fetcher (reads) |  |
| `max items per run` | config | li-post-search (reads) |  |
| `max items per run floor and cap (budgets)` | config | li-company-posts-poller (reads) |  |
| `max posts per channel (route cap)` | config | tg-channel-posts-poller (reads) |  |
| `MAX_BODY_BYTES` | config | yt-pubsub-receiver (reads) |  |
| `maximum Hamming distance` | config | news-dedup (reads) |  |
| `member pruning period` | config | news-dedup (reads) |  |
| `Meta bucket gate` | config | quota-governor (defines) | default 80% of the reported bucket gates priority 4 and 5 |
| `meta_on_request grace period` | config | retention-purger (defines) | default to be agreed with counsel |
| `min_conf` | config | analysis-sentiment (defines) | default chosen on the validation split per version; stored in the registry |
| `minimum excerpt word count` | config | news-dedup (reads) |  |
| `missed_push_rate threshold` | config | x-user-timeline-poller (reads) |  |
| `mode` | registry_flag | quota-governor (writes) | normal, stretch, exhausted default normal |
| `monthly ig_vendor budget (USD)` | config | ig-keyword-search (mention) |  |
| `news_disqus budget at zero (kill switch)` | config | news-comments-fetcher (reads) |  |
| `news_urls pruning period` | config | news-article-extractor (reads) |  |
| `normalizer_version` | config | normalize-item (defines) | default 1.4.0 (example) |
| `not-returned error table` | config | ig-account-resolver (reads) | individual, review default review for seed-list or registered candidates, individual for every other one (until the table exists) |
| `on-time window` | config | tt-user-resolver (reads), tt-video-stats-refresher (reads) | default one hour (initial value, to be tuned in the pilot) |
| `order mode (newest first / oldest first)` | config | yt-replies-fetcher (reads) | newest first, oldest first |
| `page cap` | config | x-replies-fetcher (reads), yt-comments-fetcher (reads), yt-replies-fetcher (reads) |  |
| `page cap per variant (configuration; name not stated)` | config | fb-page-search (reads) |  |
| `page ceiling (environment variable; name not stated)` | config | tt-video-comments-fetcher (reads) |  |
| `per-brand thresholds` | config | analysis-media (defines) |  |
| `per-client engine permission flags` | registry_flag | yt-web-search-bridge (reads) | Mojeek-only, Perplexity opt-in default Mojeek (government clients default to Mojeek only) |
| `per-host re-check cooldown` | config | news-robots-checker (reads) |  |
| `per-job cap` | config | x-full-archive-search (reads) |  |
| `per-node thresholds` | config | analysis-topics (reads) | default validation split per version, stored in model_versions.thresholds |
| `per-platform concurrency` | config | backfill-orchestrator (reads) | default environment variable, to be set in the pilot |
| `per-run page cap` | config | tg-message-search (reads) |  |
| `per-run page cap (from quota-governor; name not stated)` | config | tt-hashtag-feed-poller (reads) |  |
| `per-site section cap` | config | news-homepage-differ (reads) |  |
| `per-source monthly cap (qualifier rule 5)` | config | ig-keyword-search (mention) |  |
| `per-source page cap` | config | ig-keyword-search (reads) |  |
| `per-tag thresholds` | config | analysis-media (defines) |  |
| `platform flag (amber)` | vendor_route_flag | backfill-orchestrator (reads), quota-governor (reads) | off |
| `posting-rate threshold for Tier 2 to Tier 1 promotion (name not stated)` | config | tt-hashtag-feed-poller (mention) |  |
| `priority list (client_sources)` | registry_flag | li-client-posts-poller (reads), li-company-posts-poller (reads) |  |
| `probe budget per resolution` | config | news-site-resolver (reads) |  |
| `profile cache period (30 days)` | config | fb-page-resolver (defines) | 30 days default 30 days |
| `profile cache TTL` | config | poster-resolver (defines) | default 30 days |
| `public_figure_followers_x` | config | qualifier (defines) | raise only default 500 |
| `publishing-rate threshold (tier 1, hot)` | config | news-feed-poller (reads) |  |
| `push_gap` | registry_flag | ig-webhook-receiver (writes) |  |
| `push_lease_lapsed` | registry_flag | yt-uploads-reconciler (reads) | push_lease_lapsed |
| `quota-governor mode` | config | x-filtered-stream (reads), x-full-archive-search (reads), x-user-timeline-poller (reads) | stretch, exhausted; normal, stretch, exhausted |
| `rate_cap_per_s` | config | raw-archiver (defines) |  |
| `RAW_BATCH_MAX_AGE_S` | config | raw-archiver (defines) | default to be measured in the pilot |
| `RAW_BATCH_MAX_BYTES` | config | raw-archiver (defines) | default to be measured in the pilot |
| `RAW_COMPACT_GRACE_H` | config | raw-archiver (defines) | default to be set in the pilot |
| `receipt-to-acknowledgement latency bound` | config | li-notification-receiver (mention) | default proposed: 60 seconds for 99% of events |
| `reconciliation loop period` | config | deletion-propagator (reads) | default environment variable |
| `reconciliation window` | config | aggregator (defines) | default 31 days |
| `recovery probe backoff` | config | source-health-canary (defines) | default exponential up to 60 minutes |
| `refresh loop scan period (name not stated)` | config | fb-page-resolver (reads) |  |
| `refresh margin` | config | news-robots-checker (reads) |  |
| `REFRESH_FLUSH_SECONDS` | config | yt-video-details-fetcher (reads) |  |
| `REFRESH_LEAD` | config | yt-text-purger (reads) |  |
| `registry refresh interval` | config | normalize-item (defines) | default 60 s |
| `reject skip list` | config | poster-resolver (defines) | default 180 days |
| `relay loop interval` | config | registry-writer (defines) | default 5 seconds |
| `removal confirmation` | config | tt-video-stats-refresher (reads) | default second request: the alternate vendor when one is configured, otherwise a retry after 30 s |
| `render` | registry_flag | news-homepage-differ (writes) | headless |
| `replay rate cap` | config | normalize-item (defines) | default 200 records a second |
| `reply threshold` | config | fb-post-comments-fetcher (mention), tt-video-comments-fetcher (reads) | default more than 10 replies |
| `reply thresholds` | config | comment-decay-scheduler (defines) | TikTok 10, YouTube 5 |
| `rerun rate cap` | config | analysis-sentiment (defines) |  |
| `reservation TTL` | config | quota-governor (defines) |  |
| `resolver timeout` | config | poster-resolver (defines) | default 15 minutes, 5 attempts |
| `retire_days` | config | qualifier (defines) | shorten only default 180 |
| `retraction degrade threshold` | config | keyword-matcher (defines) | default 5 minutes of ClickHouse unavailability |
| `review_timeout_hours` | config | qualifier (defines) | fixed default 24 |
| `rotation scheduler scan period (environment variable, name not stated)` | config | ig-account-media-poller (reads), ig-mentions-fetcher (reads) |  |
| `rotation scheduler scan period (environment variable; name not stated)` | config | fb-group-posts-poller (reads), fb-keyword-search (reads), fb-page-feed-poller (reads), tt-client-videos-fetcher (reads), tt-profile-videos-poller (reads) |  |
| `route degraded` | registry_flag | yt-keyword-search (mention) | degraded |
| `RUN_AT_UTC` | config | x-compliance-sync (reads) |  |
| `RUN_WINDOW_HOURS` | config | x-compliance-sync (reads) |  |
| `sample_posts` | config | poster-resolver (defines) | default 20 |
| `sarcasm_cut` | config | analysis-sentiment (defines) | default chosen per version; stored in the registry |
| `scan period` | config | comment-decay-scheduler (reads), yt-uploads-reconciler (reads) | default environment variable well inside 1 hour |
| `scan period (to be set in the pilot)` | config | ig-account-resolver (reads) |  |
| `scheduler scan period` | config | tg-channel-posts-poller (reads) |  |
| `scheduler scan period (environment variable, name not stated)` | config | li-client-posts-poller (reads), li-company-posts-poller (reads), news-feed-poller (reads), news-homepage-differ (reads), news-robots-checker (reads), news-sitemap-poller (reads) |  |
| `seen-page rule recent id window length (name not stated)` | config | tt-hashtag-feed-poller (reads) |  |
| `series for keyword-matched posts (li-post-search)` | feature_flag | li-post-comments-fetcher (mention) | no, yes default no |
| `series lateness tolerance of due_at` | config | li-own-comments-fetcher (mention), li-post-comments-fetcher (mention) |  |
| `signing (hub.secret / X-Hub-Signature)` | feature_flag | yt-pubsub-receiver (reads) |  |
| `sources.health` | registry_flag | li-post-search (reads) |  |
| `spam_duplicate_share` | config | qualifier (defines) | 0.40 to 0.90 default 0.60 |
| `spam_posts_per_day` | config | qualifier (defines) | 20 to 200 default 50 |
| `spelling variants per keyword cap` | config | tg-message-search (reads) |  |
| `staleness threshold` | config | alert-evaluator (defines) | default three aggregator cycles |
| `STORE_BATCH_ROWS` | config | store-writer (defines) | default 5,000 |
| `STORE_FLUSH_MS` | config | store-writer (defines) | default 5,000 |
| `stretch_factor` | registry_flag | comment-decay-scheduler (reads), quota-governor (writes) | default 1.0 |
| `SUBSCRIBE_RATE` | config | yt-pubsub-receiver (reads) |  |
| `subscribed_fields` | config | fb-client-webhook-receiver (defines) | feed, comments default feed |
| `subscription state` | registry_flag | ig-webhook-receiver (writes) |  |
| `sweep period` | config | retention-purger (reads) | default environment variable well inside 24 hours; initial value to be measured |
| `sweep schedule` | config | qualifier (defines) | default daily at 03:00 Baghdad time |
| `TG_BOT_UPDATE_MODE` | config | tg-bot-channel-receiver (reads), tg-discussion-receiver (reads) | webhook, getUpdates default webhook |
| `thread_ids per replies job` | config | comment-decay-scheduler (defines) | default a configured number |
| `Tier 1 shortened interval (budgets configuration)` | config | li-company-posts-poller (reads) |  |
| `tier1_followers` | config | qualifier (defines) | raise only default 100,000 |
| `tier2_followers` | config | qualifier (defines) | raise only default 10,000 |
| `title-overlap threshold` | config | news-dedup (reads) |  |
| `token `degraded`` | registry_flag | ig-hashtag-search (reads), ig-hashtag-search (writes), ig-webhook-receiver (writes) | degraded |
| `token refresh margin (environment variable; name not stated)` | config | tt-client-videos-fetcher (reads) |  |
| `unreachable-file limit (keep last known rules)` | config | news-robots-checker (reads) |  |
| `user_reads monthly ceiling` | config | x-user-resolver (reads) |  |
| `vendor_keys.plan (plan guard)` | registry_flag | web-search-mojeek (reads) | Business, Enterprise, other plans |
| `VERIFY_TIMEOUT` | config | yt-pubsub-receiver (reads) |  |
| `wait_for_async_insert` | config | store-writer (defines) | 1 default 1 |
| `X_COMPLIANCE_METERED` | feature_flag | x-compliance-sync (reads) | on, off |
| `x_deadline_at_risk warning age` | config | retention-purger (defines) | default to be set in the pilot |
| `x_enterprise` | registry_flag | keyword-matcher (reads) | true, false |
| `X_PLAN` | config | x-user-resolver (reads) | enterprise |
| `YouTube media rule (v1)` | config | analysis-media (defines) | thumbnails only default thumbnails only |
| `YT_BRIDGE_MAX_VARIANTS` | config | yt-web-search-bridge (reads) | default 3 |
| `YT_BRIDGE_RUN_AT` | config | yt-web-search-bridge (reads) | default 05:00 Asia/Baghdad |
| `YT_SEARCH_RUN_AT` | config | yt-keyword-search (reads) | default 06:00 Asia/Baghdad |
| `yt_text_refresh` | registry_flag | yt-text-purger (reads) |  |
| `zero_shot to supervised promotion count` | config | analysis-topics (defines) | default set in the pilot |
| `zero_shot_unavailable` | feature_flag | analysis-topics (defines) | true |

## 7. Retention classes

| Class as written | In CONVENTIONS | Service (access) | Applies to | Refs |
|---|---|---|---|---|
| `x_24h_sync` | yes | deletion-propagator (mention) | audit example (platform_sync deletion of an X item) | 6.2 L95 |
| `x_24h_sync` | yes | keyword-matcher (assigns) | hits on X items (copied from the item, example) | 6.2 L114 |
| `x_24h_sync` | yes | normalize-item (assigns) | X items (by route) | 5.3 L75 |
| `x_24h_sync` | yes | qualifier (assigns) | X sources | 5.2 L57 |
| `x_24h_sync` | yes | raw-archiver (reads) | raw batch and payload file: no time expiry, removed by deletions; envelope kept with the item | 5.3 L77 |
| `x_24h_sync` | yes | retention-purger (reads) | anchor signal_at; 24 hours; nothing by time; watches X deletions to completed within 24 h; executor deletion-propagator | 5.3 L62 |
| `x_24h_sync` | yes | store-writer (reads) | content never blanked by time; row deleted created + 10 years | 5.3 L75; 13.4 L170 |
| `x_24h_sync` | yes | x-compliance-sync (assigns) | every `deletions` message this service emits (retention_class field) | 3 L20; 6.2 L103; 13.3 L184 |
| `x_24h_sync` | yes | x-compliance-sync (reads) | ClickHouse items and comments rows: a class other than x_24h_sync is counted `class_mismatch` (still submitted) | 3 L23; 5.2 L52; 6.1 L93 |
| `x_24h_sync` | yes | x-filtered-stream (assigns) | every raw.items message (envelope.retention_class) | 6.2 L124; 7 L156; 13.11 L201 |
| `x_24h_sync` | yes | x-full-archive-search (assigns) | every raw.items message (envelope.retention_class) | 6.2 L119; 7 L141; 13.11 L185 |
| `x_24h_sync` | yes | x-recent-search (assigns) | every raw.items message | 6.2 L114; 9 L160 |
| `x_24h_sync` | yes | x-replies-fetcher (assigns) | every raw.items reply message | 1 L9; 6.2 L125; 7 L146; +1 more |
| `x_24h_sync` | yes | x-user-resolver (assigns) | poster.profiles messages (envelope.retention_class) | 6.2 L111; 9 L157 |
| `x_24h_sync` | yes | x-user-timeline-poller (assigns) | every raw.items message | 6.2 L125; 7 L145; 13.9 L186 |
| `youtube_30d_text` | yes | aggregator (reads) | hours still rebuild at +8 d | 13.6 L146 |
| `youtube_30d_text` | yes | comment-decay-scheduler (mention) | series never extend retention | 9 L169 |
| `youtube_30d_text` | yes | normalize-item (assigns) | YouTube items (by route) | 5.3 L75 |
| `youtube_30d_text` | yes | qualifier (assigns) | YouTube sources | 5.2 L57 |
| `youtube_30d_text` | yes | raw-archiver (reads) | raw batch and payload expire 30 days after fetched_at (yt-text-purger is the authority); envelope kept, no text | 5.3 L78 |
| `youtube_30d_text` | yes | retention-purger (reads) | anchor fetched_at of the text; 30 days; retention_sweep job to yt-text-purger, verified | 5.3 L63 |
| `youtube_30d_text` | yes | store-writer (reads) | content blanked at 30 days; row deleted created + 36 months | 5.3 L76; 13.4 L170 |
| `youtube_30d_text` | yes | yt-channel-resolver (assigns) | poster.profiles channel profile messages (envelope.retention_class) and cached profiles, refreshed or dropped at 30 days | 6.2 L113; 9 L160 |
| `youtube_30d_text` | yes | yt-comments-fetcher (assigns) | every raw.items comment message and batch (every copy: archive batches, DLQ, raw.items) | 1 L9; 6.2 L127; 7 L149; +2 more |
| `youtube_30d_text` | yes | yt-keyword-search (assigns) | every raw.items video record from search | 6.2 L116; 13.4 L174 |
| `youtube_30d_text` | yes | yt-pubsub-receiver (assigns) | raw.items partial video posts | 6.2 L115 |
| `youtube_30d_text` | yes | yt-replies-fetcher (assigns) | every raw.items reply message | 6.2 L116; 7 L137; 13.9 L183 |
| `youtube_30d_text` | yes | yt-text-purger (reads) | ClickHouse comments (comments and replies) and items of kind video (title and description); query A filter | 3 L19; 5.3 L71 |
| `youtube_30d_text` | yes | yt-text-purger (assigns) | deletions messages (retention_class field) and retention_audit rows (class column) | 6.2 L146; 6.2 L165 |
| `youtube_30d_text` | yes | yt-uploads-reconciler (assigns) | raw.items partial video posts (copied from the source's retention_class) | 6.2 L120; 13.11 L194 |
| `youtube_30d_text` | yes | yt-video-details-fetcher (assigns) | raw.items full video records and every item.metrics observation | 6.2 L110; 6.2 L151; 9 L182; +1 more |
| `linkedin_48h` | yes | aggregator (reads) | hours freeze at 48 hours (not rebuilt after base rows are gone) | 5.3 L61; 13.6 L146 |
| `linkedin_48h` | yes | comment-decay-scheduler (mention) | series never extend retention | 9 L169 |
| `linkedin_48h` | yes | keyword-matcher (reads) | gate: items go only to clients in the source's client_ids | 5.3 L68 |
| `linkedin_48h` | yes | li-client-posts-poller (assigns) | every raw.items post message (envelope.retention_class); 'the class for everything this route stores' | 6.2 L117; 7 L135; 13.10 L183; +1 more |
| `linkedin_48h` | yes | li-company-posts-poller (assigns) | an item whose original author is a member (a repost), 'until legal decides (shared with li-post-search)' | 7 L133; 14.5 L188 |
| `linkedin_48h` | yes | li-notification-receiver (assigns) | comment events, reaction events and their raw objects (raw.items rows and raw objects written by this service) | 5.2 L56; 6.2 L125; 7 L142; +1 more |
| `linkedin_48h` | yes | li-org-resolver (assigns) | sampled organization posts written to raw.items on the green route | 7 L115 |
| `linkedin_48h` | yes | li-own-comments-fetcher (assigns) | comment text, commenter references and raw batches (raw.items comment messages) | 3 L20; 5.2 L63; 6.2 L118; +3 more |
| `linkedin_48h` | yes | li-post-comments-fetcher (assigns) | vendor comments in raw.items, held comment rows, per-comment analysis rows and raw objects | 6.2 L120; 7 L139; 9 L155; +1 more |
| `linkedin_48h` | yes | li-post-search (mention) | member-authored vendor posts, if legal so decides | 7 L115; 14.2 L164 |
| `linkedin_48h` | yes | normalize-item (assigns) | LinkedIn items (by route) | 5.3 L75 |
| `linkedin_48h` | yes | qualifier (assigns) | LinkedIn sources | 5.2 L57 |
| `linkedin_48h` | yes | raw-archiver (reads) | expires 48 hours after fetched_at (profile data 24 hours); envelope expires with it; never compacted | 5.3 L67; 5.3 L79; 13.9 L176 |
| `linkedin_48h` | yes | retention-purger (reads) | anchor fetched_at; 48 h member social activity, 24 h member profile data, organization data as the terms allow; deletions mode delete by kind | 5.3 L64; 13.5 L161 |
| `linkedin_48h` | yes | store-writer (reads) | content blanked at 48 hours; row deleted at 48 hours with its analysis rows | 5.3 L77; 13.4 L170; 14.3 L183 |
| `meta_on_request` | yes | aggregator (mention) | example aggregate row | 6.2 L88 |
| `meta_on_request` | yes | analysis-entities (assigns) | items.analysis output (copied from the item; example) | 6.2 L105; 9 L139 |
| `meta_on_request` | yes | analysis-media (assigns) | items.analysis output (copied from the item; example) | 6.2 L102 |
| `meta_on_request` | yes | analysis-sentiment (assigns) | items.analysis output (copied from the item; example) | 6.2 L104; 9 L135 |
| `meta_on_request` | yes | analysis-topics (assigns) | items.analysis output (copied from the item; example) | 6.2 L108; 9 L142 |
| `meta_on_request` | yes | comment-decay-scheduler (mention) | series never extend retention | 9 L169 |
| `meta_on_request` | yes | fb-backfill (assigns) | backfilled Page posts in raw.items | 6.2 L100; 9 L139; 13.8 L165 |
| `meta_on_request` | yes | fb-client-webhook-receiver (assigns) | client-owned Page posts and comments in raw.items | 6.2 L122; 9 L160; 13.5 L184 |
| `meta_on_request` | yes | fb-page-feed-poller (assigns) | Page posts written to raw.items | 6.2 L120; 9 L158; 13.8 L184 |
| `meta_on_request` | yes | fb-page-resolver (assigns) | poster.profiles messages (Page profiles) | 6.2 L109; 9 L155 |
| `meta_on_request` | yes | fb-page-search (assigns) | discovery.hits candidate Page messages | 6.2 L115; 9 L147 |
| `meta_on_request` | yes | fb-post-comments-fetcher (assigns) | Page comments in raw.items | 6.2 L112; 9 L153 |
| `meta_on_request` | yes | fb-reactions-fetcher (assigns) | item.metrics observations | 6.2 L122; 9 L155 |
| `meta_on_request` | yes | ig-account-media-poller (assigns) | every raw.items post message (envelope.retention_class) | 6.2 L116; 9 L152; 13.12 L184 |
| `meta_on_request` | yes | ig-account-resolver (assigns) | every poster.profiles message | 6.2 L121; 9 L157; 13.11 L187 |
| `meta_on_request` | yes | ig-hashtag-search (assigns) | every raw.items post message | 6.2 L109; 13.10 L183 |
| `meta_on_request` | yes | ig-mentions-fetcher (assigns) | every raw.items message (posts and comments) | 6.2 L116; 9 L155; 13.12 L186 |
| `meta_on_request` | yes | ig-own-comments-fetcher (assigns) | every raw.items comment and reply message | 6.2 L119; 9 L157; 12 L173; +1 more |
| `meta_on_request` | yes | ig-webhook-receiver (assigns) | every raw.items message | 6.2 L115; 9 L154; 13.11 L184 |
| `meta_on_request` | yes | keyword-matcher (reads) | gate: items go only to clients in the source's client_ids | 5.3 L68 |
| `meta_on_request` | yes | normalize-item (assigns) | Meta items (by route); example Facebook post | 5.3 L75; 6.2 L116 |
| `meta_on_request` | yes | qualifier (assigns) | Facebook and Instagram green sources | 5.2 L57; 13.1 L139 |
| `meta_on_request` | yes | raw-archiver (reads) | no time expiry; removed on request or offboarding; envelope kept with the item | 5.3 L80 |
| `meta_on_request` | yes | registry-writer (mention) | source.events example; remove_client announced so retention-purger can act on meta_on_request data | 6.2 L95; 9 L124 |
| `meta_on_request` | yes | retention-purger (reads) | event-anchored: necessity review, offboarding, author requests, Meta's instruction entered by ops | 5.3 L65; 5.3 L74 |
| `meta_on_request` | yes | store-writer (reads) | content never by time; row created + 10 years | 5.3 L78 |
| `meta_on_request` | yes | tt-client-videos-fetcher (mention) | model for tiktok_display | 14.2 L177 |
| `vendor_agreed` | yes | fb-group-comments-fetcher (assigns) | group comments (amber) in raw.items | 6.2 L117 |
| `vendor_agreed` | yes | fb-group-posts-poller (assigns) | group posts (amber) in raw.items | 6.2 L114; 8 L151; 13.7 L185 |
| `vendor_agreed` | yes | fb-keyword-search (assigns) | posts found by keyword search (amber) in raw.items | 6.2 L109; 13.5 L171 |
| `vendor_agreed` | yes | ig-comments-fetcher (assigns) | every raw.items comment message | 6.2 L105; 7 L125; 13.4 L166 |
| `vendor_agreed` | yes | ig-keyword-search (assigns) | every raw.items post message | 6.2 L108; 7 L128; 13.7 L172 |
| `vendor_agreed` | yes | li-company-posts-poller (assigns) | company-authored post items in raw.items (envelope.retention_class) | 6.2 L114; 7 L133; 13.9 L179 |
| `vendor_agreed` | yes | li-org-resolver (assigns) | sampled organization posts written to raw.items on the amber route (default 24 months for raw text) | 7 L115 |
| `vendor_agreed` | yes | li-post-comments-fetcher (mention) | alternative class for vendor comment text under legal review (24 months) | 7 L139; 14.1 L192 |
| `vendor_agreed` | yes | li-post-search (assigns) | every raw.items post record, including member-authored posts | 6.2 L92; 7 L115; 13.3 L152 |
| `vendor_agreed` | yes | normalize-item (assigns) | amber vendor items (by route) | 5.3 L75 |
| `vendor_agreed` | yes | qualifier (assigns) | every amber route, incl. Facebook groups | 5.2 L57; 5.2 L59; 13.5 L143 |
| `vendor_agreed` | yes | raw-archiver (reads) | 24 months by default, or the vendor contract | 5.3 L81 |
| `vendor_agreed` | yes | retention-purger (reads) | anchor fetched_at; 24 months raw text or vendor override; deletions mode purge_text | 5.3 L66; 6.2 L100 |
| `vendor_agreed` | yes | store-writer (reads) | content blanked at 24 months by default; row created + 10 years | 5.3 L79 |
| `vendor_agreed` | yes | tg-bot-channel-receiver (assigns) | raw.items posts and edits from channels where the bot is administrator (green route, vendor null) | 6.2 L125; 7 L145; 13.2 L182; +1 more |
| `vendor_agreed` | yes | tg-channel-posts-poller (assigns) | raw.items posts read through the Apify Actors (amber) | 6.2 L119; 7 L140; 13.10 L187 |
| `vendor_agreed` | yes | tg-channel-resolver (assigns) | poster.profiles messages (the class of the raw.items profile record is not stated) | 6.2 L100; 11 L139 |
| `vendor_agreed` | yes | tg-discussion-receiver (assigns) | raw.items comments and replies from registered discussion groups (green route, vendor null) | 6.2 L129; 7 L148; 13.2 L186; +1 more |
| `vendor_agreed` | yes | tg-message-search (assigns) | discovery.hits messages (example); the class on raw.items is not stated | 6.2 L90; 11 L126 |
| `vendor_agreed` | yes | tt-hashtag-feed-poller (assigns) | every raw.items video message | 6.2 L95; 13.8 L161 |
| `vendor_agreed` | yes | tt-keyword-search (assigns) | every raw.items video message | 6.2 L89; 13.7 L151 |
| `vendor_agreed` | yes | tt-profile-videos-poller (assigns) | every raw.items video message | 6.2 L117; 9 L153; 13.11 L182 |
| `vendor_agreed` | yes | tt-user-resolver (assigns) | poster.profiles messages | 6.2 L97; 9 L137 |
| `vendor_agreed` | yes | tt-video-comments-fetcher (assigns) | raw.items comment and reply messages | 6.2 L111; 9 L148 |
| `vendor_agreed` | yes | tt-video-stats-refresher (assigns) | item.metrics observations | 6.2 L97; 9 L140; 13.9 L168 |
| `news_excerpt` | yes | news-article-extractor (assigns) | raw.items kind article (excerpt and metadata kept; full text only in the 7-day cache) | 6.2 L101; 7 L136 |
| `news_excerpt` | yes | news-comments-fetcher (assigns) | raw.items kind comment (excerpt up to 300 characters; full text only in the 7-day cache) | 6.2 L104; 7 L133; 5.4 L82; +1 more |
| `news_excerpt` | yes | news-dedup (mention) | articles (full text stays in the extractor's 7-day cache) | 7 L115 |
| `news_excerpt` | yes | news-feed-poller (assigns) | article.urls messages (envelope.retention_class) | 6.2 L103; 7 L127 |
| `news_excerpt` | yes | news-homepage-differ (assigns) | article.urls messages (envelope.retention_class) | 6.2 L108; 7 L130 |
| `news_excerpt` | yes | news-robots-checker (mention) | articles (excerpts plus metadata and hashes; full text only in a 7-day cache) | 7 L129 |
| `news_excerpt` | yes | news-site-resolver (assigns) | proposed_source.retention_class of a news site (the sources row registry-writer writes) | 6.2 L91; 7 L123 |
| `news_excerpt` | yes | news-sitemap-poller (assigns) | article.urls messages (envelope.retention_class) | 6.2 L115; 7 L139 |
| `news_excerpt` | yes | normalize-item (assigns) | news articles (by route) | 5.3 L75 |
| `news_excerpt` | yes | qualifier (assigns) | news sources | 5.2 L57 |
| `news_excerpt` | yes | raw-archiver (reads) | full-text batches expire after 7 days; excerpt Parquet kept | 5.3 L82; 13.6 L173 |
| `news_excerpt` | yes | retention-purger (reads) | anchor fetched_at of the full text; 7 days full-text cache; purge_text; excerpt and metadata stay | 5.3 L67 |
| `news_excerpt` | yes | search-hit-router (assigns) | excerpts (title, snippet) carried in discovery.hits evidence and article.urls messages | 7 L144 |
| `news_excerpt` | yes | store-writer (reads) | content never (excerpt and metadata kept); row created + 10 years | 5.3 L80 |
| `news_excerpt` | yes | web-gdelt-poller (assigns) | search.results messages | 6.2 L109; 7 L125; 13.6 L167 |
| `news_excerpt` | yes | web-search-mojeek (assigns) | search.results messages | 6.2 L105; 13.4 L159 |
| `news_excerpt` | yes | web-search-perplexity (assigns) | search.results messages (results are excerpt and metadata only) | 6.2 L106; 7 L121; 13.4 L160 |
| `Telegram bot content / web-search results (class not set)` | **no** | retention-purger (mention) | retention class to be set with counsel | 14.3 L172 |
| `tiktok_display` | **no** | tt-client-videos-fetcher (assigns) | raw.items video messages (envelope.retention_class) and, by 'same envelope fields', item.metrics observations | 6.2 L106; 6.2 L115 |
| `tiktok_display` | **no** | tt-client-videos-fetcher (proposes) | Display API data | 6.2 L115; 14.2 L177 |

## 8. Keys and identifiers

Every key, id, hash or cursor format a PRD defines, as written, grouped by name. Formats longer than 140 characters are cut; the reference points to the full text.

| Name as written | Service: format as written (first ref) |
|---|---|
| `7-day sent set` | yt-web-search-bridge: `hashed video ids sent in the last 7 days` (5.1 L47) |
| `account mapping` | ig-webhook-receiver: `entry id -> sources.platform_id (owned_by_client = true, route = green)` (5.2 L56) |
| `account rule bucket` | x-filtered-stream: `account rules OR `from:` handles in buckets keyed by a stable hash of source_id, so one change rewrites one...` (5.1 L40) |
| `Actor input channels` | tg-channel-posts-poller: `usernames from sources.handle, no @, no t.me prefix` (5.2 L62) |
| `aggregate grain` | aggregator: `(hour, client_id, keyword_id, platform, source_id, sentiment, topic_id, retention_class)` (5.3 L55) |
| `alert uniqueness` | alert-evaluator: `unique (fingerprint, window_key)` (5.3 L63) |
| `alert_id` | alert-evaluator: `ULID (example 01J9W5A2M7Q0R4T8V1X3Y5Z7B9)` (6.2 L88) |
| `analysis_key` | analysis-entities: `<item_id>:<task>:<model_version>; example …:entities:ent-iq-2026.11` (6.2 L90)<br>analysis-media: `<item_id>:<task>:<model_version>; example …:media_ocr:ocr-iq-2026.11` (6.2 L87)<br>analysis-sentiment: `<item_id>:<task>:<model_version>` (6.2 L89)<br>analysis-topics: `<item_id>:<task>:<model_version>; example 6f1d…:topics:global:topics-iq-2026.11.tx7` (6.2 L93) |
| `anchor` | comment-decay-scheduler: `fetched_at of the post's first items.normalized message` (5.1 L60) |
| `answer idempotency` | fb-page-resolver: `one answer per candidate_key per cache period` (9 L153)<br>yt-channel-resolver: `one answer per candidate_key per cache period` (9 L159) |
| `answer matching` | x-user-resolver: `every answer carries the request's job_id` (6.2 L132) |
| `Apify run id` | li-company-posts-poller: `run id returned by POST .../runs` (5.3 L70) |
| `Apify runId / defaultDatasetId` | li-org-resolver: `{runId}, {defaultDatasetId}` (5.3 L61) |
| `article.urls idempotency_key` | search-hit-router: `news:article:<canonical_url_hash>` (9 L159; 13.4 L184) |
| `article.urls message_id` | search-hit-router: `au:…:<canonical_url_hash>` (9 L159) |
| `article.urls partition key` | search-hit-router: `source_id (the news site's)` (6.2 L117) |
| `author reference` | ig-own-comments-fetcher: `hashed author reference on downstream items (made by normalize-item)` (3 L29)<br>ig-webhook-receiver: `hashed reference downstream (not made here)` (7 L135) |
| `author_hash` | poster-resolver: `sha256(platform \|\| platform_id \|\| salt), salt from Supabase Vault` (5.2 L59)<br>retention-purger: `computed with the SDK helper normalize-item uses (AUTHOR_HASH_KEY from Supabase Vault)` (5.3 L78)<br>tt-video-comments-fetcher: `HMAC-SHA-256 (keyed, key from Supabase Vault) of the vendor's user id, not the handle; same function every ...` (3 L21)<br>x-compliance-sync: `listening-sdk author_hash helper keyed with AUTHOR_HASH_KEY from Vault` (5.3 L81) |
| `author_hash (guest)` | news-comments-fetcher: `HMAC-SHA-256(key, "disqus:anon:" + thread id + ":" + name)` (5.3 L76) |
| `author_hash (registered)` | news-comments-fetcher: `HMAC-SHA-256(key from Vault, "disqus:" + author id)` (5.3 L76) |
| `author_ref` | fb-client-webhook-receiver (3 L22)<br>fb-group-comments-fetcher: `keyed hash` (5.2 L62)<br>fb-group-posts-poller: `keyed hash of the poster id (key in Supabase Vault)` (3 L21)<br>fb-keyword-search: `keyed hash of the poster id` (3 L22)<br>fb-post-comments-fetcher: `keyed hash (key in Vault)` (5.4 L87)<br>ig-comments-fetcher: `keyed hash of username and any id, key in Supabase Vault; example ah1:<32 hex>` (5.2 L61)<br>normalize-item: `hmac_sha256(AUTHOR_HASH_KEY, platform + ':' + author_platform_id); example 'hmac:9c1f…'` (5.2 L54)<br>tg-discussion-receiver: `HMAC-SHA-256 keyed hash of the Telegram user id with a Supabase Vault secret; example hmac:7f3a91c0d4e2b856` (5.2 L63)<br>x-replies-fetcher: `HMAC-SHA256 keyed from Vault, scoped to the post's source (example `hmac:<hex>`)` (5.2 L59)<br>yt-comments-fetcher: `HMAC-SHA256 of authorChannelId keyed from Vault, scoped to the video's channel (example prefixed hmac:)` (5.2 L56)<br>yt-replies-fetcher: `HMAC-SHA256 with yt-comments-fetcher's key and per-channel scope (example prefixed hmac:)` (5.2 L53) |
| `author_source_id` | tt-video-comments-fetcher: `source_id of the registered source` (5.3 L68)<br>x-replies-fetcher: `source_id of the registered author` (5.2 L59) |
| `backfill job_id` | backfill-orchestrator: `ULID with the random part from sha256(source_id \| backfill \| run_id)` (5.3 L85) |
| `backfill window` | news-sitemap-poller: `URLs whose lastmod (or news:publication_date) is within 90 days; child sitemaps with lastmod within 90 days` (5.1 L51) |
| `baseline` | news-homepage-differ: `boolean; true on a site's first poll` (5.1 L49) |
| `batch` | fb-backfill (6.2 L102)<br>fb-group-posts-poller: `raw/amber/facebook/<yyyy>/<mm>/<dd>/fb-group-posts-poller/<batch>.jsonl.zst` (5.2 L60)<br>fb-page-feed-poller: `raw/green/facebook/<yyyy>/<mm>/<dd>/fb-page-feed-poller/<batch>.jsonl.zst` (5.2 L58)<br>ig-account-media-poller: `raw/green/instagram/<yyyy>/<mm>/<dd>/ig-account-media-poller/<nnnnnn>.jsonl.zst` (5.2 L62)<br>ig-keyword-search: `raw/amber/instagram/<yyyy>/<mm>/<dd>/ig-keyword-search/<nnnnnn>.jsonl.zst` (5.2 L62)<br>ig-mentions-fetcher: `raw/green/instagram/<yyyy>/<mm>/<dd>/ig-mentions-fetcher/<nnnnnn>.jsonl.zst` (5.2 L59)<br>ig-own-comments-fetcher: `raw/green/instagram/<yyyy>/<mm>/<dd>/ig-own-comments-fetcher/<nnnnnn>.jsonl.zst` (6.2 L121)<br>ig-webhook-receiver: `raw/green/instagram/<yyyy>/<mm>/<dd>/ig-webhook-receiver/<nnnnnn>.jsonl.zst` (6.2 L117)<br>news-article-extractor: `example raw/green/news/2026/10/06/news-article-extractor/000412.jsonl.zst` (6.2 L105)<br>tg-bot-channel-receiver: `raw/green/telegram/2026/10/06/tg-bot-channel-receiver/000311.jsonl.zst (example only)` (6.2 L128)<br>tg-channel-posts-poller: `raw/amber/telegram/2026/10/06/tg-channel-posts-poller/000045.jsonl.zst (example only)` (5.2 L65)<br>tt-client-videos-fetcher (6.2 L108)<br>tt-profile-videos-poller: `raw/amber/tiktok/<yyyy>/<mm>/<dd>/tt-profile-videos-poller/` (5.2 L61)<br>tt-video-comments-fetcher (6.2 L113) |
| `batch number width` | raw-archiver: `six digits proposed (normalize-item examples show four, fb-page-feed-poller six)` (14.1 L181) |
| `batch path` | x-filtered-stream: `raw/green/x/<yyyy>/<mm>/<dd>/x-filtered-stream/` (5.2 L63)<br>x-full-archive-search: `raw/green/x/<yyyy>/<mm>/<dd>/x-full-archive-search/` (5.2 L54)<br>x-user-timeline-poller: `raw/green/x/<yyyy>/<mm>/<dd>/x-user-timeline-poller/` (5.2 L59)<br>yt-comments-fetcher: `raw/green/youtube/<yyyy>/<mm>/<dd>/yt-comments-fetcher/<batch>.jsonl.zst` (5.2 L57)<br>yt-replies-fetcher: `raw/green/youtube/<yyyy>/<mm>/<dd>/yt-replies-fetcher/<batch>.jsonl.zst` (5.2 L54)<br>yt-uploads-reconciler: `raw/green/youtube/<yyyy>/<mm>/<dd>/yt-uploads-reconciler/<batch>.jsonl.zst` (6.2 L122) |
| `brand_id` | analysis-media: `not stated` (5.3 L68) |
| `call_id` | yt-video-details-fetcher (5.2 L63) |
| `calling account `{ig-user-id}`` | ig-account-media-poller: `the calling client's Instagram business account id` (5.2 L59)<br>ig-account-resolver: `the calling client's Instagram business account id` (5.2 L57) |
| `candidate_key` | fb-page-resolver: `facebook:<platform_id> \| facebook:<handle>` (3 L19)<br>ig-account-resolver: `instagram:<platform_id> \| instagram:<handle>` (5.1 L42)<br>keyword-matcher: `<platform>:<platform_id> or <platform>:<handle>` (5.1 L40)<br>li-org-resolver: `linkedin:org:<handle>` (5.1 L44)<br>poster-resolver: `<platform>:<platform_id>, or <platform>:<handle> when the hit carries only a handle` (3 L22)<br>search-hit-router: `instagram:<handle>` (5.3 L74)<br>search-hit-router: `instagram:post:<shortcode>` (5.3 L74)<br>search-hit-router: `facebook:group:<id or slug>` (5.3 L75)<br>search-hit-router: `facebook:<vanity or id>` (5.3 L76)<br>search-hit-router: `telegram:<name>` (5.3 L77)<br>search-hit-router: `youtube:<id or handle>` (5.3 L78)<br>search-hit-router: `youtube:video:<id>` (5.3 L79)<br>search-hit-router: `x:<handle>` (5.3 L80)<br>search-hit-router: `linkedin:<slug>` (5.3 L81)<br>search-hit-router: `tiktok:<handle>` (5.3 L82)<br>search-hit-router: `news:<registrable domain>` (5.3 L83)<br>tt-user-resolver: `tiktok:<platform_id> or tiktok:<handle>` (5.1 L41)<br>web-commoncrawl-scanner: `news:<registrable domain>` (6.2 L93)<br>x-user-resolver: `x:<user id> or x:<handle>` (3 L19)<br>yt-channel-resolver: `youtube:<channel id> \| youtube:<handle>` (3 L19) |
| `candidate_key_hash` | ig-account-resolver: `SHA-256 of candidate_key` (5.1 L50) |
| `candidate_ref` | fb-page-resolver: `keyed hash` (6.2 L128)<br>x-user-resolver: `HMAC-SHA256 with a key in Supabase Vault` (5.2 L53) |
| `canonical post id (proposed)` | tg-channel-posts-poller: `<lowercase username>/<message_id>` (14.4 L194) |
| `canonical_key` | news-dedup: `sha256 of the canonical URL normalised further: https, lowercase host without leading www., no default port...` (5.3 L64) |
| `canonical_url / canonical_url_hash` | web-gdelt-poller: `computed by the shared canonicaliser; example hash sha256:b27d93…` (5.2 L59)<br>web-search-mojeek: `computed by the shared canonicaliser in listening-sdk; example hash sha256:4be07a…` (5.2 L58)<br>web-search-perplexity: `computed by the shared canonicaliser in listening-sdk; example hash sha256:9c1e4b…` (5.2 L56) |
| `canonical_url_hash` | news-article-extractor: `sha256(canonical URL)` (5.3 L71) |
| `channel lookup` | tg-message-search: `platform = telegram, platform_id = username` (5.2 L54) |
| `channel reference` | yt-web-search-bridge: `channel/UC…, @handle, c/<name>, user/<name>` (5.2 L59) |
| `channel url` | yt-channel-resolver: `https://www.youtube.com/channel/<id>` (6.2 L120) |
| `chat map key` | tg-bot-channel-receiver: `chat id and lowercase username` (5.2 L60) |
| `client_ids` | tg-message-search: `not stated (example cl_a1b2)` (6.2 L85) |
| `client_ids[]` | web-gdelt-poller: `format not stated (example cl_17)` (6.2 L101)<br>web-search-mojeek: `format not stated (example cl_17)` (6.2 L98)<br>web-search-perplexity: `format not stated (example cl_17)` (6.2 L99) |
| `client_sources key` | registry-writer: `(client_id, source_id)` (5.3 L77) |
| `cluster id` | analysis-topics: `stable by centroid matching to yesterday's clusters` (5.3 L74) |
| `comment index key` | yt-comments-fetcher: `per comment (video_id, comment_id); per video` (6.3 L140) |
| `comment URN` | li-notification-receiver: `urn:li:comment:(urn:li:share:<post id>,<comment id>) (example)` (5.4 L89)<br>li-own-comments-fetcher: `urn:li:comment:(urn:li:share:<post id>,<comment id>) (example)` (5.4 L85) |
| `comment_series key` | comment-decay-scheduler: `(item_id, lane)` (5.2 L75) |
| `commenter reference (payload.author.ref)` | li-post-comments-fetcher: `sha256(salt + profile identifier), salt in Supabase Vault` (5.2 L63) |
| `completion key` | yt-video-details-fetcher: `job_id` (9 L180) |
| `connection_id` | x-filtered-stream: `ULID` (5.2 L59) |
| `consumer group` | aggregator: `aggregator` (5.1 L37)<br>alert-evaluator: `alert-evaluator` (5.1 L40)<br>deletion-propagator: `deletion-propagator` (5.1 L43)<br>fb-reactions-fetcher: `fb-reactions-fetcher` (5.1 L39)<br>keyword-matcher: `keyword-matcher` (5.1 L40)<br>raw-archiver: `raw-archiver` (5.1 L44) |
| `consumer groups` | analysis-entities: `analysis-entities \| analysis-entities-rerun-<model_version>` (5.1 L40)<br>analysis-media: `analysis-media \| analysis-media-rerun-<model_version>` (5.1 L41)<br>analysis-sentiment: `analysis-sentiment \| analysis-sentiment-aspect \| analysis-sentiment-rerun-<model_version>` (5.1 L45)<br>analysis-topics: `analysis-topics \| analysis-topics-rerun-<model_version>` (5.1 L44)<br>normalize-item: `normalize-item \| normalize-item-replay-<version>` (5.1 L41)<br>store-writer: `store-writer \| store-writer-replay-<version>` (5.1 L39) |
| `content hash` | li-own-comments-fetcher: `hash per comment (function not stated)` (5.2 L60)<br>li-post-comments-fetcher: `per comment (function not stated)` (5.2 L63)<br>tt-video-comments-fetcher: `content hash of the comment text (function not stated)` (3 L20) |
| `content_expires_at` | store-writer: `the message's expires_at, else sentinel 2106-01-01 00:00:00` (5.3 L71) |
| `content_hash` | ig-comments-fetcher: `sha256:<hex>, SHA-256 of the comment text` (5.1 L49)<br>ig-own-comments-fetcher: `sha256:<hex>, SHA-256 of `text`` (5.1 L49)<br>normalize-item: `sha256(title + text + media urls); example 'sha256:4b2e…'` (5.2 L51)<br>x-replies-fetcher: `sha256 of `text` (example `sha256:<hex>`)` (5.2 L58)<br>yt-comments-fetcher: `sha256 of textOriginal (example prefixed sha256:)` (5.2 L55)<br>yt-replies-fetcher: `sha256 of the text (example prefixed sha256:)` (5.2 L52) |
| `context.keyword_id` | tt-keyword-search (6.2 L90) |
| `conversation root` | x-replies-fetcher: `a post whose conversation_id equals its id` (5.1 L43) |
| `coverage cursor` | x-filtered-stream: `cursors.cursor = X rule id` (5.1 L42) |
| `crawl.policies idempotency` | news-robots-checker: `host + policy_version` (9 L144) |
| `crawl.policies message key` | news-robots-checker: `host` (6.2 L93) |
| `crawl_id` | web-commoncrawl-scanner: `Common Crawl crawl id (example CC-MAIN-2026-38)` (6.2 L96) |
| `crawl_policies row key` | news-robots-checker: `one row per host` (6.3 L121) |
| `cross-route dedup key (proposed)` | ig-keyword-search: `shortcode in `permalink`` (14.2 L182) |
| `cursor` | fb-client-webhook-receiver: `time of the newest event` (6.3 L137)<br>fb-group-posts-poller: `ISO created_time of the newest stored post` (5.2 L61)<br>fb-keyword-search: `small JSON map from variant to the newest created_time seen` (6.3 L124)<br>fb-page-feed-poller: `ISO created_time of the newest stored post` (5.2 L59)<br>fb-page-search: `ISO timestamp of the last run start` (5.1 L42)<br>ig-account-media-poller: `ISO `timestamp` of the newest stored post` (5.2 L63)<br>ig-hashtag-search: `newest timestamp acknowledged, per hashtag × edge` (5.2 L67)<br>ig-keyword-search: `JSON with the newest media `timestamp` and `poll_started_at`` (5.1 L47)<br>ig-mentions-fetcher: `JSON string: one `since` timestamp per edge (tags, mentioned_media, mentioned_comment) + `poll_started_at`` (5.1 L45)<br>li-client-posts-poller: `newest lastModifiedAt stored` (5.2 L61)<br>li-company-posts-poller: `newest post time stored` (5.2 L61)<br>li-post-search: `timestamp of the newest post seen (per rule)` (3 L24)<br>x-recent-search: `newest_id of the last acknowledged run, sent as since_id` (5.3 L67)<br>x-user-timeline-poller: `highest stored post id as a decimal string; compared as 64-bit integers, not strings; the next since_id` (5.2 L60)<br>yt-keyword-search: `RFC 3339 timestamp of the term's last successful run start; publishedAfter = cursor minus 6 hours` (5.1 L48)<br>yt-pubsub-receiver: `newest updated` (6.3 L134)<br>yt-text-purger: `cut-off` (5.2 L59)<br>yt-uploads-reconciler: `ISO publishedAt of the newest video already stored for the channel` (5.2 L65) |
| `cursor (fb-backfill row)` | fb-backfill: `oldest created_time reached (the resume until)` (3 L21) |
| `cursor (fb-page-feed-poller row, seeded)` | fb-backfill: `newest created_time seen, or window_end when the feed returned nothing` (5.2 L56) |
| `cursor (watermark)` | retention-purger: `last cut-off per class` (6.3 L114) |
| `cursor semantics` | web-gdelt-poller: `cursors.cursor = start time of the last successful run; advanced to the run's start after acknowledgement; ...` (5.1 L46)<br>web-search-mojeek: `cursors.cursor = start time of the last successful run; advanced only after acknowledgement; v1 sends no da...` (6.3 L113)<br>web-search-perplexity: `per rule: last_run_started_at, last_success_at, results_last_run, last_error, consecutive_errors; advanced ...` (5.1 L47)<br>yt-comments-fetcher: `no cursor value; no page token kept between fetches` (6.3 L140) |
| `cursor value` | news-comments-fetcher: `no cursor per source; the job carries the newest stored comment time and the thread id, returned in the res...` (6.3 L124)<br>news-feed-poller: `JSON map feed URL -> {etag, last_modified, newest_published_at, first50_hash}` (6.3 L119)<br>news-homepage-differ: `JSON {etag, last_modified, page_hash, link_hashes (last three snapshots), sections, render}` (6.3 L122)<br>news-sitemap-poller: `JSON map sitemap URL -> {etag, last_modified, newest_date, urls_hash}` (6.3 L131) |
| `cursors row` | li-own-comments-fetcher: `(source, service)` (6.3 L130)<br>li-post-comments-fetcher: `(source, service)` (6.3 L133) |
| `cursors.cursor` | tg-bot-channel-receiver: `newest message id stored per channel` (5.2 L63)<br>tg-channel-posts-poller: `ISO time of the newest post stored through this service` (5.2 L66)<br>tg-channel-resolver: `last profile time` (6.3 L107)<br>tg-discussion-receiver: `JSON: linked chat id, linked source_id, newest message id stored` (5.2 L67)<br>tg-message-search: `last window end as an ISO timestamp` (6.3 L95)<br>tt-client-videos-fetcher: ``create_time` (ISO, UTC) of the newest stored video plus its id` (6.3 L119)<br>tt-hashtag-feed-poller: `JSON of newest create_time, the vendor cursor of an unfinished backfill, and the recent window of video ids` (5.2 L59)<br>tt-keyword-search: `JSON of newest create_time per variant plus the vendor cursor of an unfinished backfill` (5.1 L44)<br>tt-profile-videos-poller: ``create_time` (ISO, UTC) of the newest stored video plus its id` (5.2 L62) |
| `cut-off` | retention-purger: `now() - clock (plus one sweep period of look-ahead)` (5.3 L58) |
| `deadline` | yt-text-purger: `fetched_at + 30 days` (5.1 L48) |
| `decision_id` | qualifier: `deterministic for the same candidate_key and profile resolved_at; example 01J9Z...` (9 L115)<br>registry-writer: `unit of idempotency` (5.2 L49)<br>source-health-canary: `derived from route, state and window start (example 01J9Q4R8T2V6W0X3Y5Z7A1B9CD)` (9 L126) |
| `defaultDatasetId` | li-company-posts-poller: `<defaultDatasetId>` (5.3 L72) |
| `deleted entry ref` | yt-pubsub-receiver: `yt:video:<id>` (5.4 L92) |
| `deletion_id` | deletion-propagator: `derived deterministically if absent; example del:platform_sync:item:3b9d5f1a7c2e4086b1d3f5a7c9e0b2d4f6a8c0e...` (5.4 L80)<br>retention-purger: `del:<reason>:<scope>:<sha256(target, class, cut-off day)>` (5.3 L72)<br>x-compliance-sync: `del:platform_sync:<scope>:<sha256(platform_id, status, signal day)>` (5.3 L81)<br>yt-text-purger: `del:retention:text_only:<sha256(target, class, cut-off day)>` (5.3 L114) |
| `deletions grouping` | x-compliance-sync: `one message per source_id and status for posts; one per author_hash for users` (5.3 L81) |
| `deletions message key` | yt-text-purger: `source_id; one message per source_id and chunk` (5.3 L106) |
| `deterministic order` | news-dedup: `earliest origin time, then earliest fetched_at, then the smaller canonical_url_hash` (5.1 L43) |
| `discovery.hits keyword_id` | ig-hashtag-search: `<hashtag source_id>` (6.2 L124) |
| `discovery.hits message_id` | search-hit-router: `dh:…:<candidate_key>:<canonical_url_hash>` (9 L159) |
| `discovery.hits partition key` | search-hit-router: `candidate_key` (6.2 L99)<br>web-commoncrawl-scanner: `candidate_key` (6.2 L84) |
| `discussion_source_id` | tg-discussion-receiver: `not stated (example d2e96b1a-47c0-4f8d-b35a-0c71e8a49f26)` (6.2 L122) |
| `disqus_shortname` | news-site-resolver: `Disqus forum shortname from '<shortname>.disqus.com/embed.js'` (5.2 L47) |
| `done key` | analysis-entities: `content_hash + model_version + kb_version` (5.2 L50) |
| `due time` | ig-keyword-search: `poll_started_at + interval` (5.1 L45)<br>ig-mentions-fetcher: `poll_started_at + 60 minutes` (5.1 L45) |
| `duplicate_of` | news-dedup: `the origin's idempotency_key (from the example)` (6.2 L93) |
| `edit_of` | fb-post-comments-fetcher: `the old idempotency key` (5.2 L68) |
| `emission dedup key` | fb-page-search: `Page id + keyword within 7 days` (2 L13) |
| `entity_id` | analysis-entities: `kb-pl-0007 (place), kb-pl-0003 (governorate) (examples)` (6.2 L108-L109) |
| `envelope.batch` | li-client-posts-poller: `raw/green/linkedin/<yyyy>/<mm>/<dd>/li-client-posts-poller/<nnnnnn>.jsonl.zst (example)` (5.2 L60)<br>li-company-posts-poller: `raw/amber/linkedin/<yyyy>/<mm>/<dd>/li-company-posts-poller/<nnnnnn>.jsonl.zst (example)` (5.2 L60) |
| `estimate` | x-full-archive-search: `expected posts x USD 0.005; expected posts = tweet_count / account age x window days, or the rule's daily n...` (5.2 L52) |
| `evidence path` | x-compliance-sync: `raw/green/x/<yyyy>/<mm>/<dd>/x-compliance-sync/<run_id>.jsonl.zst` (5.2 L56) |
| `fingerprint` | alert-evaluator: `<type>:<rule_id>:<scope_key> (scope_key = keyword, keyword and source, or item id); example volume_spike:5d...` (5.3 L63) |
| `first sight` | tt-video-stats-refresher: `time of the video's first items.normalized message` (5.1 L44) |
| `form_id` | keyword-matcher: `e.g. f2` (5.3 L56) |
| `gap job source_id` | x-filtered-stream: `the rule's first source` (5.2 L70) |
| `gap window` | x-filtered-stream: `[high-water mark - margin, first message on the new connection + margin]` (5.2 L69) |
| `getUpdates offset` | tg-bot-channel-receiver: `last acknowledged update_id + 1` (5.2 L62)<br>tg-discussion-receiver: `last acknowledged update_id + 1` (5.3 L77) |
| `gold set version` | analysis-sentiment: `gold-v1, ...` (5.3 L74) |
| `handle normalisation` | tg-channel-resolver: `t.me/, @ and case stripped` (5.2 L53) |
| `handshake answer` | li-notification-receiver: `the challenge and its HMAC-SHA256 under the app's client secret` (5.3 L66-L68) |
| `hashed author reference` | li-post-search: `written by normalize-item for member-authored hits (format not stated)` (3 L31) |
| `hashed candidate_key for individuals (open question)` | tt-user-resolver: `hash of candidate_key (function not stated)` (14.3 L171) |
| `hashtag id (platform_id)` | ig-hashtag-search: `id from ig_hashtag_search` (3 L20) |
| `hashtag ledger entry` | ig-hashtag-search: `(hashtag id, first queried at) per client business account, rolling 7 days` (5.1 L57) |
| `hashtag platform_id` | tt-hashtag-feed-poller: `learned from raw.text_extra[].hashtag_id of the newest stored video carrying the name, or from the vendor` (3 L24) |
| `high-water mark` | x-filtered-stream: `receipt time up to which every post is acknowledged` (5.2 L63) |
| `hit_at` | keyword-matcher: `the item's created_at` (5.3 L77) |
| `hit_id` | keyword-matcher: `uuid_v5(ns_hits, "<item_id>:<client_id>:<keyword_id>")` (5.3 L77) |
| `hit_item_keys` | tg-channel-resolver: `not stated` (5.2 L52) |
| `host dedup` | web-commoncrawl-scanner: `hosts already in sources (match on host and registrable domain) and hosts suppressed by earlier scans are d...` (5.2 L52) |
| `hub.callback` | yt-pubsub-receiver: `https://<cluster-ingress>/webhooks/youtube` (5.3 L62) |
| `hub.topic` | yt-pubsub-receiver: `https://www.youtube.com/xml/feeds/videos.xml?channel_id=<channel_id> (URL-encoded)` (5.3 L63) |
| `id mapping` | x-compliance-sync: `post id -> item_id and source_id (ClickHouse, or the raw envelope for archive-only ids); user id -> author_...` (5.3 L81) |
| `Idempotency-Key` | alert-evaluator: `<alert_id>:<channel>` (5.3 L69) |
| `idempotency_key` | fb-backfill: `facebook:post:<platform_id>` (6.2 L97)<br>fb-group-comments-fetcher: `facebook:comment:<comment_id> when the vendor returns an id, otherwise facebook:comment:<post_id>:<sha256(c...` (5.4 L94)<br>fb-group-posts-poller: `facebook:post:<platform_id>` (6.2 L111)<br>fb-keyword-search: `facebook:post:<platform_id>` (6.2 L106)<br>fb-page-feed-poller: `facebook:post:<platform_id>` (6.2 L117)<br>ig-account-media-poller: `instagram:post:<platform_id>` (6.2 L113)<br>ig-comments-fetcher: `instagram:comment:<id> when the vendor returns a comment id; otherwise the hash-based key (the construction...` (6.2 L102)<br>ig-hashtag-search: `instagram:post:<media-id>` (6.2 L91)<br>ig-keyword-search: `instagram:post:<platform_id>` (6.2 L105)<br>ig-mentions-fetcher: `instagram:post:<platform_id> \| instagram:comment:<platform_id>` (6.2 L113)<br>ig-own-comments-fetcher: `instagram:comment:<platform_id>` (6.2 L116)<br>ig-webhook-receiver: `instagram:comment:<id> \| instagram:post:<id>` (5.1 L49)<br>li-client-posts-poller: `linkedin:post:<platform_id>` (9 L152)<br>li-company-posts-poller: `linkedin:post:<platform_id>` (9 L149)<br>li-own-comments-fetcher: `linkedin:comment:<platform_id>` (9 L152)<br>li-post-comments-fetcher: `linkedin:comment:<platform_id>` (9 L156)<br>li-post-search: `linkedin:post:<activity id> where present, otherwise linkedin:post:<sha256(url)>` (6.2 L91)<br>news-article-extractor: `news:article:<canonical_url_hash>` (9 L152)<br>news-comments-fetcher: `news:comment:<disqus post id> with a version suffix (:v1, :v2)` (9 L149)<br>tg-bot-channel-receiver: `telegram:post:<username or chat id>/<message_id>` (6.2 L122)<br>tg-channel-posts-poller: `telegram:post:<username>/<message_id>` (6.2 L116)<br>tg-channel-resolver: `telegram:profile:<username>` (6.2 L84)<br>tg-discussion-receiver: `telegram:comment:<group chat id>/<message_id>` (6.2 L124)<br>tg-message-search: `telegram:post:<channel_username>/<message_id>` (5.2 L54)<br>tt-client-videos-fetcher: `tiktok:video:<id>` (6.2 L103)<br>tt-hashtag-feed-poller: `tiktok:video:<video_id>` (6.2 L83)<br>tt-keyword-search: `tiktok:video:<video_id>` (6.2 L77)<br>tt-profile-videos-poller: `tiktok:video:<id>` (6.2 L114)<br>tt-user-resolver: `tiktok:profile:<platform_id>` (6.2 L94)<br>tt-video-comments-fetcher: `tiktok:comment:<cid>` (6.2 L106)<br>x-filtered-stream: `x:post:<id>` (6.2 L120)<br>x-full-archive-search: `x:post:<id>` (6.2 L115)<br>x-recent-search: `x:post:<id>` (5.2 L57)<br>x-replies-fetcher: `x:comment:<id>` (6.2 L115)<br>x-user-timeline-poller: `x:post:<id>` (6.2 L121)<br>yt-comments-fetcher: `youtube:comment:<comment id>` (6.2 L119)<br>yt-keyword-search: `youtube:video:<videoId>` (5.1 L48)<br>yt-pubsub-receiver: `youtube:post:<videoId>` (5.1 L44)<br>yt-replies-fetcher: `youtube:comment:<reply id>` (6.2 L108)<br>yt-uploads-reconciler: `youtube:post:<video id>` (5.2 L63)<br>yt-video-details-fetcher: `youtube:post:<video id>` (6.2 L97) |
| `idempotency_key (comment)` | fb-client-webhook-receiver: `facebook:comment:<id>` (6.2 L119)<br>li-notification-receiver: `linkedin:comment:<platform_id>; table form linkedin:comment:<comment URN>` (5.4 L96) |
| `idempotency_key (Instagram)` | normalize-item: `instagram:post:<media id> \| instagram:comment:<id>` (5.3 L66) |
| `idempotency_key (LinkedIn)` | normalize-item: `share and comment urns` (5.3 L69) |
| `idempotency_key (Meta Graph /feed)` | normalize-item: `facebook:post:<id>` (5.3 L62) |
| `idempotency_key (news)` | normalize-item: `news:article:<canonical_url_hash>` (5.3 L72) |
| `idempotency_key (no comment id)` | li-post-comments-fetcher: `linkedin:comment:<post_id>:<sha256(created_time + text)>` (6.2 L129) |
| `idempotency_key (owned_by_client)` | fb-post-comments-fetcher: `facebook:comment:<comment-id>` (5.4 L87) |
| `idempotency_key (Page webhooks)` | normalize-item: `facebook:comment:<id>` (5.3 L64) |
| `idempotency_key (post)` | fb-client-webhook-receiver: `facebook:post:<post_id>` (6.2 L133) |
| `idempotency_key (PPCA comments)` | normalize-item: `facebook:comment:<post_id>:<sha256(created_time + text)>` (5.3 L63) |
| `idempotency_key (PPCA)` | fb-post-comments-fetcher: `facebook:comment:<post_id>:<sha256(created_time + text)>` (5.4 L87) |
| `idempotency_key (reaction)` | li-notification-receiver: `linkedin:reaction:<platform_id>` (9 L161) |
| `idempotency_key (SociaVault/ScrapeCreators)` | normalize-item: `vendor ids` (5.3 L65) |
| `idempotency_key (Telegram)` | normalize-item: `telegram:message:<chat_id>:<message_id>` (5.3 L70) |
| `idempotency_key (TikTok)` | normalize-item: `tiktok:post:<aweme_id> \| tiktok:comment:<cid>` (5.3 L67) |
| `idempotency_key (web)` | normalize-item: `web:result:<sha256(canonical url)>` (5.3 L73) |
| `idempotency_key (X)` | normalize-item: `x:post:<id>` (5.3 L68) |
| `idempotency_key (YouTube)` | normalize-item: `youtube:video:<id> \| youtube:comment:<id>` (5.3 L71) |
| `IG hashtag ledger key` | quota-governor: `account + hashtag (rolling 7 days)` (5.3 L68) |
| `ig-user-id` | ig-mentions-fetcher: `the source's platform_id` (5.2 L56) |
| `ig_user_id` | ig-hashtag-search: `client's Instagram business account id; 'the same id is charged in the ledger'` (5.1 L45) |
| `in-run dedup` | tt-keyword-search: `duplicates across variants collapsed within the run` (5.2 L52) |
| `in_reply_to_ref` | x-replies-fetcher: `same mapping as the author (example `source:<source_id>`)` (5.2 L59) |
| `individual source_id` | aggregator: `nil UUID` (5.3 L55) |
| `input_hash` | analysis-sentiment: `sha256 (example sha256:91a7…)` (6.2 L99) |
| `iq_domain / phone_964 derivation` | fb-page-resolver: `iq_domain: a website domain ending .iq; phone_964: a +964 or 00964 number in about` (5.2 L58) |
| `item_id` | normalize-item: `uuid_v5(ns_items, idempotency_key)` (5.2 L51) |
| `item_id derivation` | deletion-propagator: `from <platform>:<kind>:<platform_id> with the SDK helper normalize-item uses` (5.3 L60) |
| `item_idempotency_key` | fb-reactions-fetcher: `facebook:post:<platform_id>` (6.2 L107)<br>ig-hashtag-search: `instagram:post:<media-id>` (6.2 L124)<br>x-recent-search: `the raw item's idempotency_key (x:post:<id>)` (6.2 L133)<br>yt-video-details-fetcher: `youtube:post:<video id>` (6.2 L136) |
| `item_key` | tt-video-stats-refresher: `tiktok:video:<id>` (6.2 L94) |
| `job / poster.profiles partition key` | fb-page-resolver: `candidate_key for candidates; source_id for registered Pages` (5.1 L42) |
| `job key` | news-site-resolver: `the canonical host` (9 L136) |
| `job partition key` | fb-backfill: `source_id` (5.1 L41)<br>fb-client-webhook-receiver: `source_id` (5.1 L40)<br>fb-group-comments-fetcher: `source_id` (5.1 L40)<br>fb-group-posts-poller: `source_id` (5.1 L40)<br>fb-page-feed-poller: `source_id` (5.1 L40)<br>fb-page-search: `keyword_id` (5.1 L40)<br>fb-post-comments-fetcher: `source_id` (5.1 L42)<br>fb-reactions-fetcher: `source_id` (5.1 L41)<br>ig-account-media-poller: `source_id` (5.1 L42)<br>ig-account-resolver: `candidate_key` (5.1 L42)<br>ig-comments-fetcher: `source_id` (5.1 L41)<br>ig-hashtag-search: `source_id` (5.1 L55)<br>ig-keyword-search: `source_id` (5.1 L41)<br>ig-mentions-fetcher: `source_id` (5.1 L41)<br>ig-own-comments-fetcher: `source_id (the owning account)` (5.1 L41)<br>li-client-posts-poller: `source_id` (5.1 L40)<br>li-company-posts-poller: `source_id` (5.1 L41)<br>li-org-resolver: `candidate_key` (5.1 L44)<br>li-own-comments-fetcher: `source_id` (5.1 L38)<br>li-post-comments-fetcher: `source_id` (5.1 L40)<br>li-post-search: `source_id (one partition per rule)` (5.2 L54)<br>news-feed-poller: `source_id` (5.1 L40)<br>tg-channel-posts-poller: `source_id` (5.1 L42)<br>tg-channel-resolver: `source_id, or handle for candidates without a row` (5.1 L45)<br>x-recent-search: `the keyword rule's source_id` (5.1 L39)<br>x-user-resolver: `candidate_key (a registered account uses its source_id)` (5.1 L41) |
| `job window` | fb-backfill: `window_start = added_at - 90 days, window_end = added_at; on-demand windows clipped to 90 days` (5.1 L41) |
| `job_id` | comment-decay-scheduler: `ULID: time part = due_at; random part = first 10 bytes of sha256(item_id \| lane \| series_step)` (5.3 L84)<br>ig-hashtag-search (6.2 L105)<br>li-notification-receiver: `ULID assigned at receipt` (6.2 L133)<br>li-org-resolver: `UUID-shaped example 2b6f0d9c-7a1e-4f3b-8c5d-9e0a1b2c3d4e` (6.2 L103)<br>li-post-search: `UUID-shaped example f3a9c2b1-5d7e-4c0a-9b2f-1e6d8a4c7b30` (6.2 L90)<br>news-robots-checker: `example '01J9N3Q8D5W2K7X1R4T9V0MZBC'` (6.2 L113)<br>news-site-resolver: `example 'job_01JA5X7R2M'` (6.2 L107)<br>tg-channel-posts-poller: `01J9N5C3R8V2K7T4X0M6Q1HZDE (example only)` (6.2 L117)<br>tt-client-videos-fetcher (6.2 L104)<br>tt-hashtag-feed-poller (6.2 L92)<br>tt-keyword-search (6.2 L86)<br>tt-profile-videos-poller (6.2 L115)<br>tt-user-resolver (6.2 L95)<br>tt-video-comments-fetcher (5.1 L41)<br>tt-video-stats-refresher (5.1 L42)<br>web-gdelt-poller: `format not stated (example wgd-20261006-0905)` (6.2 L100)<br>web-search-mojeek: `format not stated (example wsm-20261006-0231)` (6.2 L97)<br>web-search-perplexity: `format not stated (example wsp-20261006-0117)` (6.2 L98)<br>x-recent-search (6.2 L111)<br>yt-keyword-search (6.2 L113)<br>yt-web-search-bridge (6.2 L118) |
| `jobs.web-gdelt-poller partition key` | web-gdelt-poller: `source_id` (5.1 L42) |
| `jobs.web-search-mojeek partition key` | web-search-mojeek: `the rule's source_id` (5.1 L43) |
| `jobs.web-search-perplexity partition key` | web-search-perplexity: `the rule's source_id` (5.1 L42) |
| `jobs.yt-pubsub-receiver partition key` | yt-pubsub-receiver: `source_id` (5.1 L38) |
| `kb_version` | analysis-entities: `integer (example 14)` (5.1 L46) |
| `keyword_id` | tg-message-search: `not stated (example kw_7f3a)` (5.2 L51)<br>web-gdelt-poller: `format not stated (example kw_0412)` (6.2 L101)<br>web-search-mojeek: `format not stated (example kw_0412)` (6.2 L98)<br>web-search-perplexity: `format not stated (example kw_0412)` (6.2 L99) |
| `keyword_rule_id` | x-recent-search (6.2 L133) |
| `lang_model_version` | lang-dialect-id: `lid-iq-2026.09 (example)` (6.2 L109) |
| `ledger entry` | x-user-resolver: `user:<id> for an organization or public figure; the keyed hash otherwise` (5.2 L57) |
| `ledger_key` | x-replies-fetcher: `x:post:<id>` (5.2 L57) |
| `mapper selection key` | normalize-item: `(service, api_version)` (5.2 L50) |
| `media key` | analysis-media: `media/<sha256> (content-addressed)` (3 L23)<br>raw-archiver: `media/<sha256> (SHA-256 of the bytes)` (5.3 L69) |
| `member key` | news-dedup: `idempotency_key (news:article:<canonical_url_hash>) as primary key` (6.3 L108) |
| `mention_of` | ig-mentions-fetcher: `the connected account's ig-user-id` (6.2 L119) |
| `merge key across variants` | fb-page-search: `Page id` (3 L20) |
| `message idempotency` | ig-account-resolver: `candidate_key + resolved_at` (8 L149) |
| `message_id` | keyword-matcher: `kh:<hit_id>:<item_version>:<set_version>` (5.3 L77)<br>poster-resolver: `pp:<candidate_key>:<resolved_at>` (9 L117)<br>qualifier: `dec:<decision_id> (example dec:01J9Z...)` (6.2 L84)<br>web-commoncrawl-scanner: `dh:web-commoncrawl-scanner:<candidate_key>:<crawl_id>` (9 L130)<br>web-gdelt-poller: `sr:gdelt:<canonical_url_hash>:<job_id>` (9 L141)<br>web-search-mojeek: `sr:mojeek:<canonical_url_hash>:<job_id>` (9 L135)<br>web-search-perplexity: `sr:perplexity:<canonical_url_hash>:<job_id>` (9 L136) |
| `model_version` | analysis-sentiment: `e.g. sent-iq-2026.11` (6.2 L101)<br>analysis-topics: `includes the taxonomy version, e.g. topics-iq-2026.11.tx7` (5.1 L50) |
| `must_finish_by` | yt-text-purger: `earliest deadline minus DELETE_MARGIN` (5.3 L102) |
| `negative cache key` | fb-page-resolver: `hash of the key` (5.2 L54) |
| `news.dedup partition key` | news-dedup: `story_id` (6.2 L84) |
| `news_sites row key` | news-site-resolver: `one row per host (6.3) / keyed by source_id (6.2)` (6.3 L116) |
| `next refresh derivation` | fb-page-resolver: `from the START of the last resolution, 30-day cycle` (5.1 L46) |
| `next_poll_at` | news-feed-poller: `poll_started_at + interval` (5.1 L44)<br>news-homepage-differ: `poll_started_at + 60 minutes` (5.1 L45)<br>news-sitemap-poller: `poll_started_at + 60 minutes` (5.1 L45)<br>yt-uploads-reconciler: `run_started_at + 24 h (from the START of the last run)` (5.1 L47) |
| `next_poll_at derivation` | fb-group-posts-poller: `poll_started_at + interval` (5.1 L44)<br>fb-keyword-search: `poll_started_at + interval` (5.1 L44)<br>fb-page-feed-poller: `poll_started_at + interval` (5.1 L44)<br>tt-client-videos-fetcher: `poll_started_at + 60 minutes` (5.1 L45)<br>tt-profile-videos-poller: `poll_started_at + interval` (5.1 L45) |
| `next_poll_at rule` | web-gdelt-poller: `run_started_at + 1 h` (5.1 L41)<br>x-user-timeline-poller: `poll_started_at + interval (from the START of the last poll)` (5.1 L44) |
| `next_refresh_at` | news-robots-checker: `start of the last check + cadence (daily; weekly for dormant)` (5.1 L43) |
| `next_search_at derivation` | fb-page-search: `run_start + 7 days, from the START of the last run` (5.1 L42) |
| `normalized page URL` | li-org-resolver: `https://www.linkedin.com/company/<handle>/` (5.2 L50) |
| `observation key` | fb-reactions-fetcher: `(item_id, observed_at)` (5.1 L43)<br>tt-client-videos-fetcher: `tiktok:metrics:<video_id>:<label>` (9 L140)<br>yt-video-details-fetcher: `(item_id, observed_at)` (9 L180) |
| `observation key / idempotency_key` | tt-video-stats-refresher: `tiktok:metrics:<video_id>:<label>` (5.2 L54) |
| `observed_at` | fb-reactions-fetcher: `extract: envelope.fetched_at; refresh: now (true time, never back-dated)` (5.1 L41) |
| `one fetch per canonical URL` | news-article-extractor: `one fetch and one raw.items message per canonical URL` (5.3 L73) |
| `one-time code` | tg-bot-channel-receiver: `not stated` (5.2 L67) |
| `organization URN` | li-client-posts-poller: `urn:li:organization:<organization id>` (5.3 L70)<br>li-notification-receiver: `urn:li:organization:<id>` (5.2 L54) |
| `origin_kind` | yt-uploads-reconciler: `the originating job kind` (5.2 L64) |
| `origin_time` | news-dedup: `published_at when present and not later than fetched_at, otherwise fetched_at` (5.2 L53) |
| `page cursor` | ig-own-comments-fetcher: `paging.next` (5.2 L61) |
| `parent_comment_id` | x-replies-fetcher: `the `replied_to` id when it is not the root` (5.2 L60) |
| `parent_id` | ig-own-comments-fetcher: `the comment id (for replies)` (3 L22)<br>news-comments-fetcher: `the article's hash (example equals the article canonical_url_hash)` (6.2 L100)<br>tt-video-comments-fetcher: `the parent comment's id` (6.2 L107) |
| `parent_platform_id` | fb-client-webhook-receiver (6.2 L118) |
| `parent_platform_id / post_platform_id` | fb-group-comments-fetcher: `parent_platform_id = post id (comment) or parent comment id (reply); post_platform_id = the post (reply)` (6.2 L113) |
| `per-run dedup` | fb-keyword-search: `one post found by several variants of the rule is emitted once per run` (5.2 L56) |
| `permalink (or shortcode)` | ig-comments-fetcher: `the post's permalink; the shortcode form if the vendor prefers it (to be confirmed)` (5.2 L58) |
| `person URN` | li-notification-receiver: `urn:li:person:<id> (example)` (5.4 L87) |
| `pinned-video stop rule` | tt-profile-videos-poller: `stop at a non-pinned video at or before the stored cursor` (5.2 L60) |
| `platform_id` | ig-account-media-poller: `Instagram media id (payload.id), e.g. 17912345678901234` (6.2 L112)<br>ig-account-resolver: `discovered account's `id` (whether returned is to be confirmed)` (5.3 L74)<br>ig-comments-fetcher: `vendor comment id or null` (6.2 L101)<br>li-client-posts-poller: `urn:li:share:<id> (example)` (6.2 L113)<br>li-company-posts-poller: `<numeric post id> (example 7246999999999999999)` (6.2 L110)<br>li-org-resolver: `urn:li:organization:<id>` (6.2 L86)<br>news-article-extractor: `the canonical_url_hash (from the example)` (6.2 L97)<br>news-comments-fetcher: `Disqus post id` (6.2 L100)<br>tg-bot-channel-receiver: `<username or chat id>/<message_id>` (6.2 L121)<br>tg-channel-posts-poller: `<username>/<message_id>` (6.2 L115)<br>tg-channel-resolver: `<username>` (6.2 L87)<br>tg-discussion-receiver: `<group chat id>/<message_id>` (6.2 L123) |
| `platform_id (post id)` | fb-page-feed-poller: `<page-id>_<post-id>` (5.4 L80) |
| `policy_version` | news-robots-checker: `integer, incremented on any change` (5.2 L60) |
| `poller cursor seed` | x-full-archive-search: `highest id read, compared as 64-bit integers; only raises, never lowers` (5.1 L41) |
| `post_ref` | comment-decay-scheduler: `{item_id, platform, platform_id}` (6.2 L141)<br>fb-group-comments-fetcher: `the post's platform id and permalink; for replies also the parent comment_id` (5.1 L40)<br>fb-post-comments-fetcher: `the post's platform id, <page-id>_<post-id>` (5.1 L42)<br>ig-comments-fetcher: `Instagram media id, e.g. 17912345678901234` (5.1 L41)<br>ig-own-comments-fetcher: `media id` (5.1 L41)<br>ig-webhook-receiver: `media id (value.media.id)` (5.2 L58)<br>li-notification-receiver: `post URN urn:li:share:<id> (example)` (6.2 L122)<br>li-own-comments-fetcher: `the post URN` (5.1 L38)<br>li-post-comments-fetcher: `bare post id (example 7246999999999999999)` (5.1 L40)<br>search-hit-router: `video id for YouTube watch, shorts and youtu.be URLs; shortcode in the Instagram example` (5.3 L79)<br>tg-discussion-receiver: `the channel post's platform_id (example iq_example_owned/5127)` (5.2 L62)<br>tt-video-comments-fetcher: `tiktok:video:<id>, or the parent comment's key for replies` (5.1 L41)<br>tt-video-stats-refresher: `tiktok:video:<id>` (5.1 L42)<br>x-full-archive-search (5.2 L49)<br>x-replies-fetcher (5.1 L41)<br>yt-comments-fetcher: `the video` (5.1 L40)<br>yt-pubsub-receiver: `<videoId>` (6.2 L127)<br>yt-replies-fetcher: `video id and thread id` (5.1 L38)<br>yt-uploads-reconciler: `array of up to 50 video ids` (6.2 L133)<br>yt-video-details-fetcher: `video id` (6.1 L86) |
| `poster partition key` | normalize-item: `<platform>:<poster platform_id>` (5.1 L41) |
| `poster.profiles message key` | ig-account-resolver: `candidate_key (and source_id when the request was a refresh)` (6.2 L102) |
| `poster.profiles partition key` | x-user-resolver: `source_id (registered) / candidate_key (organization or public figure) / candidate_ref (else)` (6.2 L101)<br>yt-channel-resolver: `source_id for a registered channel; candidate_key otherwise` (6.2 L103) |
| `preproc_version` | analysis-sentiment: `e.g. pp-2026.10` (6.2 L101) |
| `producer.job_id (example)` | analysis-entities: `analysis-entities:priority:0009` (6.2 L97)<br>analysis-media: `analysis-media:priority:0003` (6.2 L94)<br>analysis-sentiment: `analysis-sentiment:priority:0007` (6.2 L96)<br>analysis-topics: `analysis-topics:priority:0011` (6.2 L100)<br>normalize-item: `fb-page-feed-poller:2026-10-06T09:00Z:7c1e` (6.2 L98) |
| `profile_cache key and alias` | yt-channel-resolver: `candidate_key; a resolved handle cached under both the handle and the channel id` (5.1 L48) |
| `profile_cache keys` | x-user-resolver: `profiles under both x:<user id> and x:<handle>; individuals and unavailable accounts as keyed hashes` (5.1 L43) |
| `profile_version` | news-site-resolver: `version of the stored profile` (6.3 L116) |
| `progress row` | x-full-archive-search: `job_id, next_token, oldest created_at, highest id, paid reads; cleared at job end` (6.3 L132) |
| `proposed_source.platform_id / handle` | news-site-resolver: `apex host (example 'example-daily.iq')` (6.2 L89) |
| `proposed_source_id` | tg-bot-channel-receiver: `pre-allocated source_id; format not stated` (5.2 L67)<br>tg-discussion-receiver: `pre-allocated source_id; format not stated` (5.2 L67) |
| `q` | yt-keyword-search: `term and curated variants joined with \|, quoted when they contain spaces` (3 L27) |
| `qualifier upsert key` | tt-user-resolver: `candidate_key` (8 L129) |
| `query` | ig-keyword-search: `a keyword rule's terms from keywords, or the hashtag without `#`` (5.2 L60)<br>x-replies-fetcher: `conversation_id:<post id> -is:retweet` (5.3 L68)<br>yt-web-search-bridge: `site:youtube.com "<term>"` (5.2 L57) |
| `query builder` | x-recent-search: `Arabic arm: (variants OR-ed, multi-word quoted, handles as plain terms) -is:retweet (lang:ar OR place_count...` (5.2 L54) |
| `query by kind` | x-full-archive-search: `backfill: `from:<handle> -is:retweet`; keyword_history: the rule's terms as x-recent-search builds them + `...` (5.2 L51) |
| `queue partition key` | news-robots-checker: `source_id, or host for a candidate not yet in the registry` (5.1 L41) |
| `raw batch path` | li-post-search: `raw/amber/linkedin/<yyyy>/<mm>/<dd>/li-post-search/<batch>.jsonl.zst` (6.2 L83) |
| `raw.items partition key` | ig-hashtag-search: `the hashtag source_id` (6.2 L91)<br>web-gdelt-poller: `web:<source_id>` (6.2 L91)<br>web-search-mojeek: `web:<source_id>` (6.2 L88)<br>web-search-perplexity: `web:<source_id>` (6.2 L89)<br>yt-keyword-search: `the keyword rule's source_id` (6.2 L96) |
| `raw_ref` | normalize-item: `raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst#<n> (from example)` (6.2 L119)<br>raw-archiver: `<object key>#<line>` (5.2 L50)<br>web-gdelt-poller: `format not stated (example raw/green/web/2026/10/06/web-gdelt-poller/0009.jsonl.zst#6)` (6.2 L108)<br>web-search-mojeek: `format not stated (example raw/green/web/2026/10/06/web-search-mojeek/0007.jsonl.zst#41)` (6.2 L104)<br>web-search-perplexity: `format not stated (example raw/green/web/2026/10/06/web-search-perplexity/0003.jsonl.zst#17)` (6.2 L105) |
| `reactor hashed reference` | li-notification-receiver: `hashed reference replacing the actor (function, key and field name not stated)` (5.2 L56) |
| `reason format` | qualifier: `iraqi_signals=2;followers=48200 (example)` (6.2 L84) |
| `recompute cursor` | aggregator: `recompute:<job_id>:<last hour>` (6.3 L97) |
| `reconciliation cursor row` | li-client-posts-poller: `service = li-client-posts-poller:reconcile` (5.1 L48) |
| `reconciliation due time` | ig-webhook-receiver: `started_at + 24 h (or + 7 d for dormant)` (5.1 L43) |
| `reconciliation slot` | x-user-timeline-poller: `spread over 22:00 to 23:59 UTC by a hash of source_id; an account entering coverage gets its next slot` (5.1 L42) |
| `reconciliation window` | ig-mentions-fetcher: `since cursor minus 24 hours` (5.1 L43) |
| `record_id` | lang-dialect-id: `the item's idempotency key (examples: facebook:post:1234567890_9876543210, telegram:message:-1001234567:5521)` (5.2 L49) |
| `refresh due times` | fb-reactions-fetcher: `refresh_24h at created_time + 24 h; refresh_7d at created_time + 7 d` (5.1 L41) |
| `refresh job dedup key` | yt-text-purger: `post_ref + run_id` (9 L207) |
| `refresh_due_at` | ig-account-resolver: `refresh_started_at + 30 days` (5.1 L46) |
| `registry.decisions partition key` | qualifier: `candidate_key, or source_id for sweep decisions` (6.2 L81) |
| `rematch cursor` | keyword-matcher: `rematch:<job_id>:<last month, last item_id>` (6.3 L122) |
| `replay cursor` | normalize-item: `replay:<version>:<last object key>` (6.3 L124)<br>raw-archiver: `replay:<run_id>:<last raw_ref>` (6.3 L122) |
| `replay dedup` | search-hit-router: `a search.results message_id already processed is skipped` (5.2 L56) |
| `replay run_id` | raw-archiver: `ULID (example 01J9P4K2M8E5T7C0Q1W3X6YZAB)` (5.3 L71) |
| `replay seq` | raw-archiver: `integer per record` (6.2 L113) |
| `reply index key` | yt-replies-fetcher: `per reply (thread_id, reply_id); per thread` (6.3 L129) |
| `request_id` | quota-governor: `ULID (example 01J9R5S3V7W1X4Y8Z0A2B6C9DE)` (5.1 L37)<br>registry-writer: `returned by POST /registry/sources` (5.2 L61)<br>web-search-mojeek: `the engine's id when it returns one, else null` (6.2 L109)<br>web-search-perplexity: `the Perplexity response id (example pplx-01J9…)` (5.4 L78) |
| `rerun cursor` | analysis-entities: `rerun:<model_version>:<last archive object key>` (6.3 L119)<br>analysis-media: `rerun:<task>:<model_version>:<last archive object key>` (6.3 L114)<br>analysis-sentiment: `rerun:<model_version>:<last archive object key>` (6.3 L115)<br>analysis-topics: `rerun:<model_version>:<last archive object key>` (6.3 L122) |
| `reservation_id` | quota-governor: `ULID (example 01J9R5S3V9K2M6P0Q4T8W1ZXYB)` (5.1 L37) |
| `resolve job_id` | poster-resolver: `res:x:1234567890 (example; res:<candidate_key>)` (5.3 L67) |
| `reuse key` | analysis-media: `same sha256, task and model_version` (5.2 L53) |
| `robots.sha256` | news-robots-checker: `sha256 of the robots.txt file` (6.2 L103) |
| `route key` | source-health-canary: `(platform, route class, vendor)` (2 L15) |
| `row_version` | store-writer: `(version << 32) \| produced_at (epoch seconds)` (5.3 L67) |
| `rule tag` | x-filtered-stream: `v1\|<acct\|brand>\|p<priority>\|s=<source ids>\|c=<client ids>` (5.4 L97) |
| `rule value` | x-filtered-stream: `account rules: `from:<handle>` OR-ed, no filters; brand rules: quoted terms OR-ed plus `-is:retweet`, and `...` (5.1 L40) |
| `run_id` | backfill-orchestrator: `initial (first run)` (5.2 L57)<br>retention-purger: `ULID (example 01J9P8A3V5N7B2D4F6H0K1M9QS)` (6.2 L104)<br>x-compliance-sync: `ULID` (5.2 L51) |
| `run_id / parent_run_id` | yt-text-purger (5.1 L44) |
| `scan checkpoint` | web-commoncrawl-scanner: `JSON on the service_runs row: crawl id, partitions done, position inside a partition` (6.3 L107) |
| `search.results idempotency_key` | yt-web-search-bridge: `web:result:<engine>:<url hash>` (6.2 L108) |
| `search.results partition key` | web-gdelt-poller: `canonical_url_hash` (6.2 L92)<br>web-search-mojeek: `canonical_url_hash` (6.2 L89)<br>web-search-perplexity: `canonical_url_hash` (6.2 L90) |
| `search.results partition key (read)` | search-hit-router: `canonical_url_hash` (5.1 L43) |
| `seed_list entry` | news-site-resolver: `example 'client_17'` (6.2 L92) |
| `seen ledger key` | yt-pubsub-receiver: `(yt:videoId, updated) per video; last_updated and version kept 90 days` (5.2 L55) |
| `seen-page rule` | tt-hashtag-feed-poller: `a rotation poll pages until a whole page holds no video new to this hashtag` (5.1 L50) |
| `series_step` | comment-decay-scheduler: `+6h (example) \| once \| hot:<n> \| refresh:<request_id>` (5.1 L66)<br>news-comments-fetcher: `example '+6h'` (6.2 L102)<br>tt-video-stats-refresher: `+24h \| +7d` (5.1 L42) |
| `series_step label` | x-replies-fetcher: `as comment-decay-scheduler labels it (example `+6h`)` (6.2 L123) |
| `set_id` | tg-message-search: `not stated` (5.2 L51) |
| `set_version / keyword_set_version` | keyword-matcher: `hash of (keyword_id, version, enabled) over the client's keywords; example cs:3f9a1c` (5.3 L58) |
| `signal_at` | x-compliance-sync: `earlier of X's completion time on the job object and our first observation of `complete`; due_at = signal_a...` (5.2 L55) |
| `signature` | li-notification-receiver: `HMAC-SHA256 of the raw body with the app's client secret, constant-time compare with the signature header` (5.2 L53) |
| `simhash` | news-dedup: `64-bit simhash of the normalised excerpt: NFKC, tashkeel and tatweel removed, alef and ya folding, Arabic-I...` (5.3 L66) |
| `since` | tg-channel-posts-poller: `ISO date-time: the oldest cursor in the batch` (5.2 L62) |
| `since_id` | x-replies-fetcher: `newest stored reply (omitted when none is stored)` (5.3 L69) |
| `slot` | yt-video-details-fetcher: `one slot per video id; jobs for one id share it` (5.1 L48) |
| `sorting keys` | store-writer: `items/comments item_id; analysis item_id, model; metrics_timeseries item_id, observed_at; hits client_id, k...` (5.3 L57-L67) |
| `source identity` | registry-writer: `(platform, platform_id), unique index` (2 L15) |
| `source.events message_id` | registry-writer: `se:<source_id>:<event> (example se:7f1c...:added)` (6.2 L95) |
| `source_id` | fb-keyword-search: `the keyword rule that produced the query` (3 L22)<br>registry-writer: `gen_random_uuid()` (5.3 L69) |
| `source_id attribution` | x-filtered-stream: `covered account whose platform_id = author_id, else the first matched brand rule's keyword-rule source` (5.2 L61) |
| `source_id of a mention` | ig-mentions-fetcher: `the connected account's source` (6.2 L126) |
| `stop marker` | li-own-comments-fetcher: `series state newest_comment_at` (5.1 L50)<br>li-post-comments-fetcher: `series state newest_comment_at` (5.1 L50) |
| `story_id` | news-dedup: `ULID` (5.2 L56) |
| `target_id` | source-health-canary: `e.g. ct_tt_03` (5.4 L88) |
| `targeted-read dedup` | ig-webhook-receiver: `same id within one hour, in memory` (5.2 L59) |
| `task` | analysis-topics: `topics:<taxonomy_id> (e.g. topics:global) \| topic_cluster` (5.2 L60) |
| `text_full_ref` | news-article-extractor: `cache/news/<yyyy>/<mm>/<dd>/<canonical_url_hash>.json.zst` (5.3 L75) |
| `text_hash` | fb-group-comments-fetcher: `sha256(created_time + text)` (5.2 L62) |
| `text_norm composition` | lang-dialect-id: `fold(title) + ' ' + fold(text)` (5.3 L86) |
| `text_norm offsets` | lang-dialect-id: `code points in text_norm` (5.3 L86) |
| `text_sha256, title_sha256` | news-article-extractor: `sha256 of the normalised body; sha256 of the title` (5.3 L71) |
| `thread id` | yt-replies-fetcher: `the id yt-comments-fetcher reports in reply_candidates` (5.3 L69) |
| `thread lookup key` | news-comments-fetcher: `thread=ident:<identifier> \| link:<canonical URL> \| link:<URL as found>` (5.2 L55) |
| `thread map key` | tg-discussion-receiver: `(group id, root message id) to channel post key` (5.2 L61) |
| `thread_id` | news-comments-fetcher: `Disqus thread id` (5.2 L55) |
| `timeline {id}` | x-user-timeline-poller: `numeric user id in sources.platform_id (from x-user-resolver), never the handle` (5.3 L75) |
| `tombstone version` | deletion-propagator: `deletion time (greater than any content version)` (5.3 L62) |
| `topic_id (example)` | aggregator: `tp_0042` (6.2 L87) |
| `update_id` | tg-bot-channel-receiver: `Telegram update id (integer in the example)` (5.4 L92) |
| `uploads_playlist_id` | yt-channel-resolver: `contentDetails.relatedPlaylists.uploads, never derived from the channel id` (5.2 L62) |
| `URL normalisation` | news-feed-poller: `lowercase scheme and host, drop the fragment, strip utm_*, fbclid, gclid, sort remaining parameters, resolv...` (5.2 L55) |
| `URL normalisation and url_hash` | news-sitemap-poller: `lowercase scheme and host, drop fragment, strip utm_*, fbclid, gclid, sort parameters; then compute url_hash` (5.2 L59) |
| `URL normalisation before matching` | search-hit-router: `host loses www., m. and mobile.; twitter.com is read as x.com; query strings and fragments are dropped exce...` (5.3 L70) |
| `url_hash` | news-article-extractor: `not stated` (5.2 L51)<br>news-feed-poller: `not stated` (5.2 L56)<br>news-homepage-differ: `hash of each normalised link (not stated further)` (5.2 L58) |
| `url_key` | news-article-extractor: `news:url:<...>, carried from article.urls` (6.2 L99)<br>news-feed-poller: `news:url:<sha256 of normalised URL>` (9 L142)<br>news-homepage-differ: `news:url:<sha256 of normalised URL>` (9 L145)<br>news-sitemap-poller: `news:url:<sha256 of normalised URL>` (9 L154) |
| `vendor switch rule` | tt-profile-videos-poller: `stored cursor is our own create_time high-water mark; no video re-emitted as new after a switch` (5.3 L77) |
| `version` | aggregator: `now() as epoch seconds` (5.2 L47)<br>fb-client-webhook-receiver: `integer; an edited event becomes a new version of the same item` (5.2 L56)<br>fb-group-comments-fetcher: `integer incremented on edit, same key` (5.2 L65)<br>news-comments-fetcher: `integer; new version when text_sha256 changes` (5.2 L58)<br>tt-video-comments-fetcher: `integer, 1 then 2 on an edit` (6.2 L108)<br>yt-pubsub-receiver: `1 for a new video, incremented per newer updated` (5.2 L55) |
| `videoId` | yt-web-search-bridge: `11 characters from watch?v=, youtu.be/, shorts/, live/ (also m.youtube.com/watch)` (5.2 L59) |
| `watermark` | tt-video-comments-fetcher: `newest stored create_time and stored count` (5.2 L56) |
| `webhook signature` | deletion-propagator: `HMAC-signed` (5.3 L72) |
| `window by kind` | x-full-archive-search: `backfill: job start minus 90 days (or the requested start) to job start; keyword_history: the client's wind...` (5.2 L51) |
| `X compliance job name` | x-compliance-sync: `<run_id>-<type>-<n>` (5.3 L65) |
| `X read ledger key` | quota-governor: `UTC day + resource id` (5.3 L68) |
| `X-Hub-Signature-256` | fb-client-webhook-receiver: `sha256=<hex>; HMAC-SHA256 of the raw body with the app secret` (5.2 L53)<br>ig-webhook-receiver: `sha256=<HMAC-SHA256 of the raw body, key = app secret>` (5.2 L54) |

## Appendix A. Per-service index

One row per PRD: the contracts it touches, for a build session to find its own line. W = writes or produces, R = reads or consumes.

| Service | Session | Folder | Header | Topics W | Topics R | Queues consumed (kinds) | Queues produced into | Tables written | Budget tags | Vendor route flags read | Retention |
|---|---|---|---|---|---|---|---|---|---|---|---|
| aggregator | C15 | shared | Shared, shared, Processing |  | deletions, source.events | jobs.aggregator (recompute) |  | aggregates_daily, aggregates_hourly, aggregates_monthly, cursors, mv_aggregates_hourly, service_runs |  |  |  |
| alert-evaluator | A5 | shared | Shared, shared, Processing |  | deletions, item.hits, source.events |  |  | alert_deliveries, alert_rules, alert_watch_items, alerts, service_runs |  |  |  |
| analysis-entities | A3 | shared | Shared, shared, Processing | items.analysis | items.normalized, source.events | jobs.analysis-entities.priority (); jobs.analysis-entities (rerun) | jobs.analysis-entities, jobs.analysis-entities.priority | cursors, review_queue, service_runs | analysis_model_api |  | meta_on_request |
| analysis-media | A4 | shared | Shared, shared, Processing | items.analysis | discovery.hits, item.hits, items.normalized, source.events | jobs.analysis-media.priority (); jobs.analysis-media (rerun) | jobs.analysis-media, jobs.analysis-media.priority | cursors, review_queue, service_runs | analysis_model_api |  | meta_on_request |
| analysis-sentiment | A1 | shared | Shared, shared, Processing | items.analysis | discovery.hits, item.hits, items.normalized, source.events | jobs.analysis-sentiment.priority (analyze); jobs.analysis-sentiment (analyze, rerun) | jobs.analysis-sentiment, jobs.analysis-sentiment.priority | cursors, model_versions, review_queue, service_runs | analysis_model_api |  | meta_on_request |
| analysis-topics | A2 | shared | Shared, shared, Processing | items.analysis | items.normalized, source.events | jobs.analysis-topics.priority (); jobs.analysis-topics (rerun) | jobs.analysis-topics, jobs.analysis-topics.priority | cursors, review_queue, service_runs, taxonomy_nodes | analysis_model_api |  | meta_on_request |
| backfill-orchestrator | C10 | shared | Shared, shared, Registry |  | jobs.completed, source.events |  | jobs.<service>, jobs.fb-backfill | backfill_runs, service_runs, sources |  | platform flag (amber) |  |
| comment-decay-scheduler | C11 | shared | Shared, shared, Registry |  | deletions, items.normalized, jobs.completed, source.events |  | jobs.<comment service>, jobs.fb-reactions-fetcher, jobs.ig-account-media-poller, jobs.tt-video-stats-refresher, jobs.yt-video-details-fetcher | comment_series, service_runs |  | FB_VENDOR_ROUTE, IG_VENDOR_ROUTE, LI_VENDOR_ROUTE, TT_VENDOR_ROUTE |  |
| deletion-propagator | C13 | shared | Shared, shared, Support |  | deletions |  | jobs.aggregator | analysis, comments, deletion_requests, items, metrics_timeseries, service_runs |  |  |  |
| fb-backfill | FB3 | facebook | Facebook, green, Fetch posts | raw.items, source.events |  | jobs.fb-backfill (add, ops, client) |  | budgets, cursors, service_runs, sources | meta_graph_pages:<client_id> |  | meta_on_request |
| fb-client-webhook-receiver | FB7 | facebook | Facebook, green, Fetch posts | deletions, raw.items | source.events | jobs.fb-client-webhook-receiver () | jobs.fb-client-webhook-receiver | cursors, service_runs, sources | meta_graph_pages:<client_id> |  | meta_on_request |
| fb-group-comments-fetcher | VFB3 | facebook | Facebook, amber (optional, flag FB_VENDOR_ROUTE), FB_VENDOR_ROUTE, Comments | deletions, raw.items | source.events | jobs.fb-group-comments-fetcher (comments, replies, ops_force) |  | budgets, comment_ledger, cursors, service_runs | fb_vendor | FB_VENDOR_ROUTE | vendor_agreed |
| fb-group-posts-poller | VFB2 | facebook | Facebook, amber (optional, flag FB_VENDOR_ROUTE), FB_VENDOR_ROUTE, Fetch posts | raw.items, source.events | source.events | jobs.fb-group-posts-poller (rotation, backfill, ops_force) | jobs.fb-group-posts-poller | budgets, cursors, service_runs, sources | fb_vendor | FB_VENDOR_ROUTE | vendor_agreed |
| fb-keyword-search | VFB1 | facebook | Facebook, amber (optional, flag FB_VENDOR_ROUTE), FB_VENDOR_ROUTE, Discover and qualify | raw.items | source.events | jobs.fb-keyword-search (rotation, backfill, ops_force) | jobs.fb-keyword-search | budgets, cursors, service_runs, sources | fb_vendor | FB_VENDOR_ROUTE | vendor_agreed |
| fb-page-feed-poller | FB2 | facebook | Facebook, green, Fetch posts | raw.items, source.events | source.events | jobs.fb-page-feed-poller (rotation, reconciliation, ops_force) | jobs.fb-page-feed-poller | budgets, cursors, service_runs, sources | meta_graph_pages:<client_id> |  | meta_on_request |
| fb-page-resolver | FB1 | facebook | Facebook, green, Discover and qualify | poster.profiles | source.events | jobs.fb-page-resolver (resolve, rotation, ops_force) | jobs.fb-page-resolver | profile_cache, service_runs | meta_graph_pages:<client_id> |  | meta_on_request |
| fb-page-search | FB6 | facebook | Facebook, green, Discover and qualify | discovery.hits |  | jobs.fb-page-search (seed, weekly) | jobs.fb-page-search | budgets, cursors, decisions, service_runs | meta_graph_pages:<client_id> |  | meta_on_request |
| fb-post-comments-fetcher | FB5 | facebook | Facebook, green, Comments | deletions, raw.items | source.events | jobs.fb-post-comments-fetcher (comments, ops_force) |  | comment_ledger, cursors, service_runs | meta_graph_pages:<client_id> |  | meta_on_request |
| fb-reactions-fetcher | FB4 | facebook | Facebook, green, Fetch posts | deletions, item.metrics | raw.items | jobs.fb-reactions-fetcher (refresh_24h, refresh_7d, refresh_client) |  | budgets, service_runs | meta_graph_pages:<client_id> |  | meta_on_request |
| ig-account-media-poller | IG3 | instagram | Instagram, green, Fetch posts | raw.items, source.events | source.events | jobs.ig-account-media-poller (rotation, reconciliation, backfill, metrics, ops_force) | jobs.ig-account-media-poller | budgets, cursors, review_queue, service_runs, sources | ig_graph_<ig_user_id> |  | meta_on_request |
| ig-account-resolver | IG1 | instagram | Instagram, green, Discover and qualify | poster.profiles |  | jobs.ig-account-resolver (resolve, rotation) | jobs.ig-account-resolver | budgets, cursors, profile_cache, review_queue, service_runs | ig_graph_<ig_user_id> |  | meta_on_request |
| ig-comments-fetcher | VIG2 | instagram | Instagram, amber (optional, flag `IG_VENDOR_ROUTE`), IG_VENDOR_ROUTE, Comments | raw.items |  | jobs.ig-comments-fetcher (comments, ops_force) |  | budgets, cursors, service_runs | ig_vendor | IG_VENDOR_ROUTE | vendor_agreed |
| ig-hashtag-search | IG2 | instagram | Instagram, green, Discover and qualify | discovery.hits, raw.items, source.events |  | jobs.ig-hashtag-search () |  | budgets, cursors, service_runs, sources | ig_graph_<client_id>, ig_hashtag_<ig_user_id> | IG_VENDOR_ROUTE | meta_on_request |
| ig-keyword-search | VIG1 | instagram | Instagram, amber (optional, flag `IG_VENDOR_ROUTE`), IG_VENDOR_ROUTE, Discover and qualify | raw.items | source.events | jobs.ig-keyword-search (rotation, backfill, ops_force) | jobs.ig-keyword-search | budgets, cursors, service_runs | ig_vendor | IG_VENDOR_ROUTE | vendor_agreed |
| ig-mentions-fetcher | IG5 | instagram | Instagram, green, Fetch posts | raw.items, source.events | source.events | jobs.ig-mentions-fetcher (rotation, reconciliation, backfill, ops_force) | jobs.ig-mentions-fetcher | budgets, cursors, service_runs, sources | ig_graph_<ig_user_id> |  | meta_on_request |
| ig-own-comments-fetcher | IG6 | instagram | Instagram, green, Comments | deletions, raw.items |  | jobs.ig-own-comments-fetcher (comments, replies, reconciliation, ops_force) |  | budgets, cursors, service_runs | ig_graph_<ig_user_id> |  | meta_on_request |
| ig-webhook-receiver | IG4 | instagram | Instagram, green, Fetch posts | raw.items, source.events |  | jobs.ig-webhook-receiver (push) | jobs.ig-mentions-fetcher, jobs.ig-own-comments-fetcher, jobs.ig-webhook-receiver | cursors, service_runs, sources |  |  | meta_on_request |
| keyword-matcher | C5 | shared | Shared, shared, Processing | discovery.hits, item.hits | items.normalized, source.events | jobs.keyword-matcher (rematch, candidate_retry) | jobs.keyword-matcher | cursors, sources |  |  | x_24h_sync |
| lang-dialect-id | C3 | shared | Shared, shared, Processing |  |  |  |  | service_runs |  |  |  |
| li-client-posts-poller | LI1 | linkedin | LinkedIn, green, Fetch posts | deletions, raw.items, source.events | source.events | jobs.li-client-posts-poller (rotation, reconciliation, backfill, ops_force) |  | budgets, cursors, service_runs, sources | linkedin_cm:<client_id> |  | linkedin_48h |
| li-company-posts-poller | VLI3 | linkedin | LinkedIn, amber (optional, flag `LI_VENDOR_ROUTE`), LI_VENDOR_ROUTE, Fetch posts | raw.items, source.events | source.events | jobs.li-company-posts-poller (rotation, backfill, ops_force) |  | budgets, cursors, service_runs, sources | li_vendor_company_posts | LI_VENDOR_ROUTE | linkedin_48h, vendor_agreed |
| li-notification-receiver | LI3 | linkedin | LinkedIn, green, Comments | deletions, raw.items, source.events | item.metrics, source.events |  |  | service_runs, sources | linkedin_cm:<client_id> |  | linkedin_48h |
| li-org-resolver | VLI2 | linkedin | LinkedIn, amber (optional, flag `LI_VENDOR_ROUTE`), LI_VENDOR_ROUTE, Discover and qualify | poster.profiles, raw.items |  | jobs.li-org-resolver (refresh) |  | budgets, service_runs | li_vendor_org_resolver | LI_VENDOR_ROUTE | linkedin_48h, vendor_agreed |
| li-own-comments-fetcher | LI2 | linkedin | LinkedIn, green, Comments | deletions, raw.items |  | jobs.li-own-comments-fetcher (comments) |  | budgets, cursors, service_runs, sources | linkedin_cm:<client_id> |  | linkedin_48h |
| li-post-comments-fetcher | VLI4 | linkedin | LinkedIn, amber (optional, flag `LI_VENDOR_ROUTE`), LI_VENDOR_ROUTE, Comments | deletions, raw.items |  | jobs.li-post-comments-fetcher (comments) |  | budgets, cursors, service_runs | li_vendor_post_comments | LI_VENDOR_ROUTE | linkedin_48h |
| li-post-search | VLI1 | linkedin | LinkedIn, amber (optional, flag `LI_VENDOR_ROUTE`), LI_VENDOR_ROUTE, Discover and qualify | raw.items |  | jobs.li-post-search (backfill) |  | budgets, cursors, service_runs, sources | li_vendor_post_search | LI_VENDOR_ROUTE | vendor_agreed |
| news-article-extractor | N6 | news | News websites, green, Fetch posts | raw.items | article.urls, crawl.policies |  | jobs.news-robots-checker | crawl_policies, news_urls, service_runs | news_proxy_egress |  | news_excerpt |
| news-comments-fetcher | N8 | news | News websites, green, Comments | deletions, raw.items |  | jobs.news-comments-fetcher (comments, ops_force) | jobs.news-site-resolver | service_runs | news_disqus |  | news_excerpt |
| news-dedup | N7 | news | News websites, green, Processing | news.dedup | raw.items |  |  | decisions, news_stories, news_story_members, service_runs |  |  |  |
| news-feed-poller | N3 | news | News websites, green, Fetch posts | article.urls, source.events | crawl.policies, source.events | jobs.news-feed-poller (rotation, ops_force) | jobs.news-robots-checker, jobs.news-site-resolver | crawl_policies, cursors, service_runs, sources | news_proxy_egress |  | news_excerpt |
| news-homepage-differ | N5 | news | News websites, green, Fetch posts | article.urls | crawl.policies, source.events | jobs.news-homepage-differ (rotation, ops_force) | jobs.news-robots-checker, jobs.news-site-resolver | crawl_policies, cursors, service_runs, sources | news_proxy_egress |  | news_excerpt |
| news-robots-checker | N1 | news | News websites, green, Discover and qualify | crawl.policies | source.events | jobs.news-robots-checker (first_check, refresh, recheck, ops_force) |  | crawl_policies, service_runs | news_proxy_egress |  |  |
| news-site-resolver | N2 | news | News, green, Discover and qualify | poster.profiles | crawl.policies | jobs.news-site-resolver (resolve, refresh) | jobs.news-robots-checker | news_sites, review_queue, service_runs | news_proxy_egress |  | news_excerpt |
| news-sitemap-poller | N4 | news | News websites, green, Fetch posts | article.urls | crawl.policies, source.events | jobs.news-sitemap-poller (rotation, backfill, ops_force) | jobs.news-robots-checker, jobs.news-site-resolver | crawl_policies, cursors, service_runs, sources | news_proxy_egress |  | news_excerpt |
| normalize-item | C4 | shared | Shared, shared, Processing | item.metrics, items.normalized | raw.items, source.events | jobs.normalize-item (replay, lang_rescore) | jobs.normalize-item | cursors, review_queue, service_runs |  |  | linkedin_48h, meta_on_request, news_excerpt, vendor_agreed, x_24h_sync, youtube_30d_text |
| poster-resolver | C8 | shared | Shared, shared, Registry | poster.profiles, raw.items | discovery.hits | jobs.poster-resolver (resolved, unresolvable, manual_candidate) | jobs.<resolver>, jobs.ig-account-resolver | decisions, poster_profiles, service_runs |  | LI_VENDOR_ROUTE, TG_VENDOR_ROUTE, TT_VENDOR_ROUTE |  |
| qualifier | C9 | shared | Shared, shared, Registry | registry.decisions | poster.profiles |  |  | decisions, review_queue, service_runs |  | FB_VENDOR_ROUTE, IG_VENDOR_ROUTE, LI_VENDOR_ROUTE, TG_VENDOR_ROUTE, TT_VENDOR_ROUTE | linkedin_48h, meta_on_request, news_excerpt, vendor_agreed, x_24h_sync, youtube_30d_text |
| quota-governor | C1 | shared | Shared, shared, Support |  | source.events |  |  | budget_history, budget_reservations, budgets, ig_hashtag_ledger, x_read_ledger | fb_vendor, gdelt_doc_api, ig_graph_<ig_user_id>, ig_hashtag_<ig_user_id>, ig_vendor, li_vendor_<action>, linkedin_cm:<client_id>, meta_*, meta_graph_pages:<client_id>, mojeek_search, news_*, perplexity_search, tg_*, tt_display:<client_id>, tt_vendor, x_pay_per_use, youtube_data_api | platform flag (amber) |  |
| raw-archiver | C2 | shared | Shared, shared, Support | raw.replay | raw.items, source.events |  |  | cursors, service_runs |  |  |  |
| registry-writer | C7 | shared | Shared, shared, Registry | source.events | registry.decisions |  | jobs.poster-resolver | client_sources, registry_audit, service_runs, sources |  |  |  |
| retention-purger | C14 | shared | Shared, shared, Support | deletions, registry.decisions | deletions, source.events |  | jobs.yt-text-purger | cursors, deletion_requests, retention_audit, service_runs, vendor_keys |  |  |  |
| search-hit-router | W3 | web | Web, green, Discover and qualify | article.urls, discovery.hits | search.results, source.events |  |  | review_queue, search_candidate_seen, search_parked_urls, search_url_seen, service_runs |  |  | news_excerpt |
| source-health-canary | C12 | shared | Shared, shared, Support | registry.decisions | source.events |  |  | canary_targets, service_runs |  | FB_VENDOR_ROUTE, TG_POSTS_ACTOR, TT_VENDOR_ROUTE |  |
| store-writer | C6 | shared | Shared, shared, Processing |  | discovery.hits, item.hits, item.metrics, items.analysis, items.normalized, source.events |  |  | analysis, comments, comments_v, cursors, hits, items, items_v, keywords_dim, metrics_timeseries, service_runs, sources_dim |  |  |  |
| tg-bot-channel-receiver | TG1 | telegram | Telegram, green, Fetch posts | discovery.hits, raw.items, source.events | source.events | jobs.tg-bot-channel-receiver (reconciliation, ops_force) | jobs.tg-bot-channel-receiver | cursors, service_runs, sources |  |  | vendor_agreed |
| tg-channel-posts-poller | VTG3 | telegram | Telegram, amber, TG_POSTS_ACTOR, Fetch posts | raw.items, source.events | source.events | jobs.tg-channel-posts-poller (rotation, reconciliation, backfill, metrics, ops_force) | jobs.tg-channel-posts-poller | budgets, cursors, service_runs, sources | tg_apify_posts | TG_POSTS_ACTOR | vendor_agreed |
| tg-channel-resolver | VTG2 | telegram | Telegram, amber, TG_VENDOR_ROUTE, Discover and qualify | poster.profiles, raw.items | items.normalized, poster.profiles | jobs.tg-channel-resolver (refresh) | jobs.tg-channel-resolver | cursors, service_runs | tg_telemetrio_stats | TG_VENDOR_ROUTE | vendor_agreed |
| tg-discussion-receiver | TG2 | telegram | Telegram, green, Comments | discovery.hits, raw.items, source.events | source.events | jobs.tg-discussion-receiver (reconciliation, ops_force) | jobs.tg-discussion-receiver | cursors, service_runs, sources |  |  | vendor_agreed |
| tg-message-search | VTG1 | telegram | Telegram, amber, TG_VENDOR_ROUTE, Discover and qualify | discovery.hits, item.hits, raw.items |  | jobs.tg-message-search () | jobs.tg-message-search | cursors, service_runs, sources | tg_telemetrio_search | TG_VENDOR_ROUTE | vendor_agreed |
| tt-client-videos-fetcher | TT1 | tiktok | TikTok, green, Fetch posts | item.metrics, raw.items, source.events | source.events | jobs.tt-client-videos-fetcher (rotation, backfill, ops_force) |  | budgets, cursors, service_runs, sources, tt_client_video_state | tt_display:<client_id> |  | tiktok_display |
| tt-hashtag-feed-poller | VTT2 | tiktok | TikTok, amber (optional, flag `TT_VENDOR_ROUTE`), TT_VENDOR_ROUTE, Discover and qualify | raw.items | raw.items | jobs.tt-hashtag-feed-poller () |  | budgets, cursors, service_runs, sources | tt_vendor | TT_VENDOR_ROUTE | vendor_agreed |
| tt-keyword-search | VTT1 | tiktok | TikTok, amber (optional, flag `TT_VENDOR_ROUTE`), TT_VENDOR_ROUTE, Discover and qualify | raw.items |  | jobs.tt-keyword-search () |  | budgets, cursors, service_runs, sources, vendor_keys | tt_vendor | TT_VENDOR_ROUTE | vendor_agreed |
| tt-profile-videos-poller | VTT4 | tiktok | TikTok, amber (optional, flag `TT_VENDOR_ROUTE`), TT_VENDOR_ROUTE, Fetch posts | raw.items, source.events | source.events | jobs.tt-profile-videos-poller (rotation, reconciliation, backfill, ops_force) |  | budgets, cursors, service_runs, sources | tt_vendor | TT_VENDOR_ROUTE | vendor_agreed |
| tt-user-resolver | VTT3 | tiktok | TikTok, amber (optional, flag `TT_VENDOR_ROUTE`), TT_VENDOR_ROUTE, Discover and qualify | poster.profiles |  | jobs.tt-user-resolver (resolve) |  | budgets, service_runs, tt_user_cache | tt_vendor | TT_VENDOR_ROUTE | vendor_agreed |
| tt-video-comments-fetcher | VTT5 | tiktok | TikTok, amber (optional, flag `TT_VENDOR_ROUTE`), TT_VENDOR_ROUTE, Comments | deletions, raw.items |  | jobs.tt-video-comments-fetcher (comments, replies) |  | budgets, service_runs, tt_comment_state | tt_vendor | TT_VENDOR_ROUTE | vendor_agreed |
| tt-video-stats-refresher | VTT6 | tiktok | TikTok, amber (optional, flag `TT_VENDOR_ROUTE`), TT_VENDOR_ROUTE, Comments and stats | deletions, item.metrics |  | jobs.tt-video-stats-refresher (metrics, ops_force) |  | budgets, service_runs | tt_vendor | TT_VENDOR_ROUTE | vendor_agreed |
| web-commoncrawl-scanner | W5 | web | Web, green, Discover and qualify | discovery.hits | source.events | jobs.web-commoncrawl-scanner (rotation, ops_force) |  | cc_hosts_seen, service_runs |  |  |  |
| web-gdelt-poller | W4 | web | Web, green, Discover and qualify | raw.items, search.results |  | jobs.web-gdelt-poller (rotation) |  | budgets, cursors, review_queue, service_runs, sources | gdelt_doc_api |  | news_excerpt |
| web-search-mojeek | W2 | web | Web, green, Discover and qualify | raw.items, search.results |  | jobs.web-search-mojeek (rotation) |  | budgets, cursors, review_queue, service_runs, sources | mojeek_search |  | news_excerpt |
| web-search-perplexity | W1 | web | Web, green, Discover and qualify | raw.items, search.results |  | jobs.web-search-perplexity (rotation, site_search) |  | budgets, cursors, review_queue, service_runs, sources | perplexity_search |  | news_excerpt |
| x-compliance-sync | X7 | x | X, green, Support | deletions |  | jobs.x-compliance-sync (ops_force) |  | service_runs, x_compliance_audit, x_compliance_runs | x_pay_per_use |  | x_24h_sync |
| x-filtered-stream | X4 | x | X, green, Fetch posts | raw.items | jobs.completed, source.events |  | jobs.x-full-archive-search, jobs.x-recent-search | cursors, review_queue, service_runs | x_pay_per_use |  | x_24h_sync |
| x-full-archive-search | X5 | x | X, green, Fetch posts | jobs.completed, raw.items, source.events | jobs.completed | jobs.x-full-archive-search (backfill, keyword_history, replies) |  | cursors, service_runs, sources | x_pay_per_use |  | x_24h_sync |
| x-recent-search | X1 | x | X, green, Discover and qualify | discovery.hits, raw.items | source.events | jobs.x-recent-search (rotation, first_run, gap_backfill, ops_force) | jobs.x-full-archive-search | cursors, review_queue, service_runs, sources | x_pay_per_use |  | x_24h_sync |
| x-replies-fetcher | X6 | x | X, green, Comments | jobs.completed, raw.items |  | jobs.x-replies-fetcher (comments) |  | cursors, reply index, service_runs | x_pay_per_use |  | x_24h_sync |
| x-user-resolver | X2 | x | X, green, Discover and qualify | poster.profiles | deletions, source.events | jobs.x-user-resolver (resolve, rotation, ops_force) |  | profile_cache, service_runs | x_pay_per_use |  | x_24h_sync |
| x-user-timeline-poller | X3 | x | X, green, Fetch posts | jobs.completed, raw.items, source.events | source.events | jobs.x-user-timeline-poller (rotation, reconciliation, ops_force) |  | cursors, service_runs, sources | x_pay_per_use |  | x_24h_sync |
| yt-channel-resolver | YT1 | youtube | YouTube, green, Discover and qualify | poster.profiles | source.events | jobs.yt-channel-resolver (resolve, rotation, ops_force) | jobs.yt-channel-resolver | profile_cache, service_runs | youtube_data_api |  | youtube_30d_text |
| yt-comments-fetcher | YT5 | youtube | YouTube, green, Comments | deletions, jobs.completed, raw.items |  | jobs.yt-comments-fetcher (comments) |  | comment index, cursors, review_queue, service_runs | youtube_data_api |  | youtube_30d_text |
| yt-keyword-search | YT8 | youtube | YouTube, green, Discover and qualify | raw.items |  |  | jobs.yt-video-details-fetcher | budgets, cursors, review_queue, service_runs | youtube_data_api |  | youtube_30d_text |
| yt-pubsub-receiver | YT2 | youtube | YouTube, green, Fetch posts | deletions, raw.items | source.events | jobs.yt-pubsub-receiver () | jobs.yt-pubsub-receiver, jobs.yt-video-details-fetcher | cursors, service_runs, yt_subscriptions |  |  | youtube_30d_text |
| yt-replies-fetcher | YT6 | youtube | YouTube, green, Comments | deletions, jobs.completed, raw.items |  | jobs.yt-replies-fetcher (replies) |  | cursors, reply index, review_queue, service_runs | youtube_data_api |  | youtube_30d_text |
| yt-text-purger | YT7 | youtube | YouTube, green, Support | deletions | registry.decisions | jobs.yt-text-purger (retention_sweep, ops_force) | jobs.yt-comments-fetcher, jobs.yt-replies-fetcher, jobs.yt-video-details-fetcher | cursors, retention_audit, service_runs | youtube_data_api |  | youtube_30d_text |
| yt-uploads-reconciler | YT3 | youtube | YouTube, green, Fetch posts | jobs.completed, raw.items, source.events | source.events | jobs.yt-uploads-reconciler (reconciliation, backfill, ops_force) | jobs.yt-uploads-reconciler, jobs.yt-video-details-fetcher | budgets, cursors, service_runs, sources | youtube_data_api |  | youtube_30d_text |
| yt-video-details-fetcher | YT4 | youtube | YouTube, green, Fetch posts | deletions, item.metrics, jobs.completed, raw.items |  | jobs.yt-video-details-fetcher (first_sight, metrics, ops_force) |  | budgets, service_runs, yt_live_watch | youtube_data_api |  | youtube_30d_text |
| yt-web-search-bridge | YT9 | youtube | YouTube, green, Discover and qualify | search.results |  |  | jobs.yt-channel-resolver, jobs.yt-video-details-fetcher | budgets, cursors, review_queue, service_runs | mojeek_search, perplexity_search |  |  |

