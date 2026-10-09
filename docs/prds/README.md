# Service PRDs — Iraq social listening platform

Draft v1, 6 Oct 2026; decided in D2 on 7 Oct 2026: where this page or a PRD differs from an ADR in `docs/decisions/`, the ADR wins (ADR-0001, ADR-0070); `_shared/CONVENTIONS.md` v1.1 folds the decisions in, each changed rule citing its ADR, which holds the full rule (CONVENTIONS v1.1 L3). One product requirement document per service: 86 services, each its own Markdown file, each following the same 14-section template (why it exists, objective, scope, consumers, how it works with trigger and rotation, the exact call, inputs and outputs with example messages, limits and cost, failure handling, non-functional requirements, metrics, dependencies, risks, acceptance criteria, open questions).

## How the set is organised

- `_shared/CONVENTIONS.md` is the base specification every PRD follows: the Redpanda topics, the registry (`sources`) table, the rotation policy, idempotency keys, retention classes, quotas and prices, error handling, the qualifier rules, the per-platform fact sheets and the PRD template. Read it first.
- One folder per platform (`facebook/`, `instagram/`, `tiktok/`, `x/`, `linkedin/`, `telegram/`, `youtube/`, `news/`, `web/`) and `shared/` for the processing, registry and support services.
- `OPEN-QUESTIONS.md` collects section 14 of every PRD (about 390 questions) in one place.

## Route classes

Two constraints decided on 6 Oct 2026 shape every PRD: no Israeli-owned or Israel-affiliated vendor anywhere in the stack, and no route that rests on a breach of a platform's terms (the Iraqi government is a prospective client).

- **green** (48 services): the platform's own API, a licensed index, or our own robots-compliant crawler, under a contract we hold.
- **amber** (18 services): data bought from a screened vendor that does the collection; optional, behind a feature flag (`FB_VENDOR_ROUTE`, `IG_VENDOR_ROUTE`, `TT_VENDOR_ROUTE`, `LI_VENDOR_ROUTE`, `TG_VENDOR_ROUTE`, `TG_POSTS_ACTOR`), disclosed to clients in the provenance statement and excluded from government contracts. Every amber service emits exactly the same record shape as its green neighbours, so turning a flag off removes the data without touching the pipeline.
- **shared** (20 services): processing, registry and support services that every route uses.
- **red** (our own collection in breach of terms): not built. There is no green route to third-party TikTok content, to comments on third-party Telegram channels, to Facebook Groups or Facebook keyword search, or to third-party LinkedIn pages; the amber services are the only way to those, and the PRDs say so. There is no route at all to Google search results: web search runs on the green services Perplexity, Mojeek, GDELT and Common Crawl (ADR-0070).

## How the data stays up to date

- **New posts, on rotation.** Every registered page, group, account, creator, channel, company page and site is re-checked on its tier: tier 1 (100,000+ followers or a client priority) every 60 minutes, tier 2 every 6 hours, tier 3 every 24 hours, dormant sources weekly. Each service that rotates a source keeps the source's due time in its own `cursors` row, set from the start of its last run; jobs are ordered so no source is skipped twice in a row, and a poller that falls behind polls the most stale sources first and raises `rotation_behind`. `sources.next_poll_at` is only a summary for the admin view, written by the source's primary poller (ADR-0015, ADR-0049). Each poll is incremental from the source's cursor. The search services below rotate their keyword-rule and hashtag sources the same way, tt-hashtag-feed-poller among them (ADR-0044, ADR-0070). The pollers: fb-page-feed-poller, fb-group-posts-poller, ig-account-media-poller, tt-profile-videos-poller, x-user-timeline-poller, li-client-posts-poller, li-company-posts-poller, tg-channel-posts-poller, yt-uploads-reconciler, news-feed-poller, news-sitemap-poller, news-homepage-differ.
- **Push where the platform offers it, with a daily safety net.** What a platform pushes arrives in seconds (fb-client-webhook-receiver, ig-webhook-receiver, li-notification-receiver, tg-bot-channel-receiver, tg-discussion-receiver, yt-pubsub-receiver, x-filtered-stream). A source whose new posts are pushed (`push_covered`) is reconciled once a day by its poller, so a missed push is never lost; a Telegram bot channel's daily job is instead the receiver's check that the bot is still an administrator, since the Bot API has no history method. Client TikTok accounts, LinkedIn client pages and client Instagram accounts are polled, not pushed (ADR-0049).
- **Comments, on a decay series.** comment-decay-scheduler opens a series for every new post (+1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30 on the main green routes; route-specific shorter series on amber and capped routes), stops early when a fetch adds under 5% new comments, extends when a thread is still growing at day 7, adds hourly fetches for hot posts above 100 new comments an hour, and sends reply jobs for large threads. Each comment fetcher pages until it reaches comments already stored and detects edits and deletions by content hash.
- **Engagement counts** are refreshed at +24 h and +7 d by fb-reactions-fetcher, ig-account-media-poller, tt-video-stats-refresher and yt-video-details-fetcher; on X, LinkedIn, Telegram and Facebook groups they are recorded at first sight in v1, a choice revisited after the pilot (ADR-0058).
- **History on add.** backfill-orchestrator reads the last 90 days (or the route's cap) of every newly added source through its own service, then hands the source to the rotation.

## From a keyword to a new page, account or group in the list

1. The search services (fb-keyword-search, ig-hashtag-search, ig-keyword-search, tt-keyword-search, tt-hashtag-feed-poller, x-recent-search, x-filtered-stream, li-post-search, tg-message-search, yt-keyword-search, yt-web-search-bridge, web-search-perplexity, web-search-mojeek, web-gdelt-poller), each rotating its keyword-rule or hashtag sources, write what they find to `raw.items` (ADR-0044, ADR-0070).
2. normalize-item, lang-dialect-id and keyword-matcher turn every item, searched or polled, into hits: every keyword hit on an item goes to `item.hits`, whoever the poster is, and a poster that is not yet a registered source goes to `discovery.hits` as a candidate (ADR-0031). search-hit-router routes open-web results to the right platform.
3. poster-resolver deduplicates candidates and calls the platform resolver (fb-page-resolver, ig-account-resolver, tt-user-resolver, x-user-resolver, li-org-resolver, tg-channel-resolver, yt-channel-resolver, news-site-resolver).
4. qualifier applies the ten registry rules: pages, creators, channels, groups and company pages with Iraqi signals and activity are added; private individuals stay mentions (a keyed `author_ref`, never profiled, listed or backfilled), while public accounts may be listed (ADR-0010); borderline cases go to an n8n review card. A hit inside a group adds the group, and its poster is qualified separately.
5. registry-writer writes the source with its route, tier and retention class; backfill-orchestrator reads its history; the poller's rotation and comment-decay-scheduler keep it current from then on.

## Service index

### Facebook (10)

| Service | Lane | Route | What it does |
|---|---|---|---|
| [fb-keyword-search](facebook/fb-keyword-search.md) | Discover and qualify | amber (`FB_VENDOR_ROUTE`) | Finds Facebook posts by keyword through SociaVault or ScrapeCreators, the only route to keyword search on Facebook. |
| [fb-page-resolver](facebook/fb-page-resolver.md) | Discover and qualify | green | Reads a candidate Page's name, category, fans, location, website and verification for the qualifier. |
| [fb-page-search](facebook/fb-page-search.md) | Discover and qualify | green | Finds candidate Pages for client keywords and brands through the Pages Search API (Pages, not posts); weekly rediscovery. |
| [fb-backfill](facebook/fb-backfill.md) | Fetch posts | green | Reads the last 90 days of a newly added Page (within the 600-posts-a-year cap) before it joins the rotation. |
| [fb-client-webhook-receiver](facebook/fb-client-webhook-receiver.md) | Fetch posts | green | Receives real-time post and comment events from client-owned Pages through Meta Webhooks. |
| [fb-group-posts-poller](facebook/fb-group-posts-poller.md) | Fetch posts | amber (`FB_VENDOR_ROUTE`) | Keeps every registered Facebook group on rotation and fetches its new posts through the vendor. |
| [fb-page-feed-poller](facebook/fb-page-feed-poller.md) | Fetch posts | green | Keeps every registered Page on rotation and fetches its new posts from /feed under Page Public Content Access. |
| [fb-reactions-fetcher](facebook/fb-reactions-fetcher.md) | Fetch posts | green | Records the seven reaction counts per post at first sight, +24 h and +7 d. |
| [fb-group-comments-fetcher](facebook/fb-group-comments-fetcher.md) | Comments | amber (`FB_VENDOR_ROUTE`) | Fetches comments on group posts on the decay series through the vendor, authors hashed. |
| [fb-post-comments-fetcher](facebook/fb-post-comments-fetcher.md) | Comments | green | Fetches comments on Page posts on the decay series; no comment ids under PPCA, so dedup by hash. |

### Instagram (8)

| Service | Lane | Route | What it does |
|---|---|---|---|
| [ig-account-resolver](instagram/ig-account-resolver.md) | Discover and qualify | green | Reads a candidate business or creator account's numbers through Business Discovery for the qualifier. |
| [ig-hashtag-search](instagram/ig-hashtag-search.md) | Discover and qualify | green | Searches registered hashtags (recent and top media) within the 30-hashtags-per-7-days budget per client account. |
| [ig-keyword-search](instagram/ig-keyword-search.md) | Discover and qualify | amber (`IG_VENDOR_ROUTE`) | Searches Instagram by keyword and beyond the 30-tag cap through SociaVault. |
| [ig-account-media-poller](instagram/ig-account-media-poller.md) | Fetch posts | green | Keeps every registered business and creator account on rotation and fetches its new media. |
| [ig-mentions-fetcher](instagram/ig-mentions-fetcher.md) | Fetch posts | green | Fetches tags and mentions of client accounts hourly. |
| [ig-webhook-receiver](instagram/ig-webhook-receiver.md) | Fetch posts | green | Receives real-time comment and mention events on client-owned accounts. |
| [ig-comments-fetcher](instagram/ig-comments-fetcher.md) | Comments | amber (`IG_VENDOR_ROUTE`) | Fetches the visible comments on third-party media through SociaVault, authors hashed. |
| [ig-own-comments-fetcher](instagram/ig-own-comments-fetcher.md) | Comments | green | Fetches comments and replies on client-owned media on the full decay series. |

### TikTok (7)

| Service | Lane | Route | What it does |
|---|---|---|---|
| [tt-hashtag-feed-poller](tiktok/tt-hashtag-feed-poller.md) | Discover and qualify | amber (`TT_VENDOR_ROUTE`) | Searches registered hashtags on rotation, like the other search services, and fetches their new videos through the vendor (ADR-0070). |
| [tt-keyword-search](tiktok/tt-keyword-search.md) | Discover and qualify | amber (`TT_VENDOR_ROUTE`) | Searches TikTok by keyword with a server-side country signal through TikHub or EnsembleData. |
| [tt-user-resolver](tiktok/tt-user-resolver.md) | Discover and qualify | amber (`TT_VENDOR_ROUTE`) | Reads a candidate creator's followers, region, bio and verification for the qualifier. |
| [tt-client-videos-fetcher](tiktok/tt-client-videos-fetcher.md) | Fetch posts | green | Reads a client's own videos and stats hourly through the Display API (the only green TikTok service). |
| [tt-profile-videos-poller](tiktok/tt-profile-videos-poller.md) | Fetch posts | amber (`TT_VENDOR_ROUTE`) | Keeps every registered creator on rotation and fetches new videos through the vendor. |
| [tt-video-comments-fetcher](tiktok/tt-video-comments-fetcher.md) | Comments | amber (`TT_VENDOR_ROUTE`) | Fetches comments and replies on the decay series through the vendor, commenters hashed. |
| [tt-video-stats-refresher](tiktok/tt-video-stats-refresher.md) | Comments and stats | amber (`TT_VENDOR_ROUTE`) | Refreshes views, likes, shares and comment counts at +24 h and +7 d. |

### X (7)

| Service | Lane | Route | What it does |
|---|---|---|---|
| [x-recent-search](x/x-recent-search.md) | Discover and qualify | green | Searches the last 7 days for client keyword rules every 15 minutes to hourly; first-read deduplication. |
| [x-user-resolver](x/x-user-resolver.md) | Discover and qualify | green | Reads a candidate account's followers, verification, location and age for the qualifier. |
| [x-filtered-stream](x/x-filtered-stream.md) | Fetch posts | green | Streams posts for up to 1,000 rules (tier-1 accounts and brand terms) in real time. |
| [x-full-archive-search](x/x-full-archive-search.md) | Fetch posts | green | Backfills a newly added account's last 90 days and serves historical keyword and reply requests. |
| [x-user-timeline-poller](x/x-user-timeline-poller.md) | Fetch posts | green | Keeps every registered account outside the stream rules on rotation; reconciles stream-covered accounts daily. |
| [x-replies-fetcher](x/x-replies-fetcher.md) | Comments | green | Fetches replies by conversation_id on the decay series inside the 7-day window. |
| [x-compliance-sync](x/x-compliance-sync.md) | Support | green | Mirrors X deletions and status changes within 24 hours through daily batch compliance jobs, with an audit trail. |

### LinkedIn (7)

| Service | Lane | Route | What it does |
|---|---|---|---|
| [li-org-resolver](linkedin/li-org-resolver.md) | Discover and qualify | amber (`LI_VENDOR_ROUTE`) | Reads a candidate company page's followers, industry and headquarters for the qualifier. |
| [li-post-search](linkedin/li-post-search.md) | Discover and qualify | amber (`LI_VENDOR_ROUTE`) | Searches LinkedIn posts by keyword through the harvestapi Actor. |
| [li-client-posts-poller](linkedin/li-client-posts-poller.md) | Fetch posts | green | Reads posts of client-administered pages every 30 to 60 minutes through the Community Management API. |
| [li-company-posts-poller](linkedin/li-company-posts-poller.md) | Fetch posts | amber (`LI_VENDOR_ROUTE`) | Keeps every registered third-party company page on a daily rotation through the vendor. |
| [li-notification-receiver](linkedin/li-notification-receiver.md) | Comments | green | Receives real-time comment and reaction events on client pages. |
| [li-own-comments-fetcher](linkedin/li-own-comments-fetcher.md) | Comments | green | Fetches comments on client posts on the decay series; member data purged after 48 hours. |
| [li-post-comments-fetcher](linkedin/li-post-comments-fetcher.md) | Comments | amber (`LI_VENDOR_ROUTE`) | Fetches comments on registered third-party posts through the vendor, commenters hashed. |

### Telegram (5)

| Service | Lane | Route | What it does |
|---|---|---|---|
| [tg-channel-resolver](telegram/tg-channel-resolver.md) | Discover and qualify | amber (`TG_VENDOR_ROUTE`) | Reads a candidate channel's subscribers, category, country and growth through Telemetrio. |
| [tg-message-search](telegram/tg-message-search.md) | Discover and qualify | amber (`TG_VENDOR_ROUTE`) | Searches Telegram messages by keyword through Telemetrio (daily, 7 to 90-day windows). |
| [tg-bot-channel-receiver](telegram/tg-bot-channel-receiver.md) | Fetch posts | green | Receives every post in channels that add our bot as administrator. |
| [tg-channel-posts-poller](telegram/tg-channel-posts-poller.md) | Fetch posts | amber (`TG_POSTS_ACTOR`) | Keeps every registered third-party channel on rotation and fetches its posts through an Apify preview Actor. |
| [tg-discussion-receiver](telegram/tg-discussion-receiver.md) | Comments | green | Receives the comments in discussion groups our bot belongs to, threaded to their channel posts. |

### YouTube (9)

| Service | Lane | Route | What it does |
|---|---|---|---|
| [yt-channel-resolver](youtube/yt-channel-resolver.md) | Discover and qualify | green | Reads a candidate channel's statistics, country and uploads playlist for the qualifier. |
| [yt-keyword-search](youtube/yt-keyword-search.md) | Discover and qualify | green | Searches YouTube for 20 to 30 priority terms a day within the 100-call search cap. |
| [yt-web-search-bridge](youtube/yt-web-search-bridge.md) | Discover and qualify | green | Finds YouTube videos for the long tail of keywords through site:youtube.com queries on Perplexity and Mojeek. |
| [yt-pubsub-receiver](youtube/yt-pubsub-receiver.md) | Fetch posts | green | Holds a PubSubHubbub subscription per registered channel and receives new videos in seconds at no quota cost. |
| [yt-uploads-reconciler](youtube/yt-uploads-reconciler.md) | Fetch posts | green | Reconciles every channel's uploads playlist daily so no video a push missed is lost; backfills new channels. |
| [yt-video-details-fetcher](youtube/yt-video-details-fetcher.md) | Fetch posts | green | Turns video ids into full records and refreshes counts at +24 h and +7 d, 50 ids per unit. |
| [yt-comments-fetcher](youtube/yt-comments-fetcher.md) | Comments | green | Fetches comment threads on the decay series (+6 h to +30 d). |
| [yt-replies-fetcher](youtube/yt-replies-fetcher.md) | Comments | green | Fetches full reply lists for threads with more than 5 replies. |
| [yt-text-purger](youtube/yt-text-purger.md) | Support | green | Refreshes or deletes YouTube comment text older than 30 days, keeping derived metrics up to 36 months. |

### News websites (8)

| Service | Lane | Route | What it does |
|---|---|---|---|
| [news-robots-checker](news/news-robots-checker.md) | Discover and qualify | green | Keeps a crawl policy per host from robots.txt, Content Signals, RSL and HTTP 402; no fetch without it. |
| [news-site-resolver](news/news-site-resolver.md) | Discover and qualify | green | Profiles a new news domain: feeds, sitemaps, CMS, language, sections, comment provider. |
| [news-article-extractor](news/news-article-extractor.md) | Fetch posts | green | Fetches and extracts each new article (excerpt and metadata stored, full text cached 7 days). |
| [news-feed-poller](news/news-feed-poller.md) | Fetch posts | green | Keeps every site with a feed on rotation (5 to 15 min hot, hourly others) and emits new article URLs. |
| [news-homepage-differ](news/news-homepage-differ.md) | Fetch posts | green | Diffs homepages and section pages hourly for sites without feeds or sitemaps. |
| [news-sitemap-poller](news/news-sitemap-poller.md) | Fetch posts | green | Reads every site's news sitemap hourly and emits new article URLs. |
| [news-comments-fetcher](news/news-comments-fetcher.md) | Comments | green | Fetches reader comments on Disqus sites on the decay series. |
| [news-dedup](news/news-dedup.md) | Processing | green | Groups syndicated copies into one story with one origin publisher. |

### Web search (5)

| Service | Lane | Route | What it does |
|---|---|---|---|
| [search-hit-router](web/search-hit-router.md) | Discover and qualify | green | Deduplicates search results by canonical URL and routes them to the right platform or news resolver. |
| [web-commoncrawl-scanner](web/web-commoncrawl-scanner.md) | Discover and qualify | green | Scans each monthly Common Crawl for Iraqi hosts the registry lacks. |
| [web-gdelt-poller](web/web-gdelt-poller.md) | Discover and qualify | green | Queries GDELT hourly for keyword coverage in its translated news stream. |
| [web-search-mojeek](web/web-search-mojeek.md) | Discover and qualify | green | Searches Mojeek's independent index with an Iraq and Arabic boost, storage licensed. |
| [web-search-perplexity](web/web-search-perplexity.md) | Discover and qualify | green | Searches the open web for client keywords on Perplexity's own index, results stored. |

### Shared services (20)

| Service | Lane | Route | What it does |
|---|---|---|---|
| [aggregator](shared/aggregator.md) | Processing | shared | Builds hourly, daily and monthly rollups kept for ten years. |
| [alert-evaluator](shared/alert-evaluator.md) | Processing | shared | Evaluates alert rules on every aggregate update and delivers through n8n and client webhooks. |
| [analysis-entities](shared/analysis-entities.md) | Processing | shared | Links brands, institutions, places and products to a curated knowledge base; never private individuals. |
| [analysis-media](shared/analysis-media.md) | Processing | shared | Runs OCR, image tagging, speech-to-text and logo spotting on media. |
| [analysis-sentiment](shared/analysis-sentiment.md) | Processing | shared | Scores Iraqi-dialect sentiment per item and per matched brand, stamped with a model version. |
| [analysis-topics](shared/analysis-topics.md) | Processing | shared | Classifies topics and intent against each client's taxonomy; clusters emerging themes. |
| [keyword-matcher](shared/keyword-matcher.md) | Processing | shared | Matches every item against every client's keyword set; splits hits on known and unknown posters. |
| [lang-dialect-id](shared/lang-dialect-id.md) | Processing | shared | Detects language and Iraqi or Sorani dialect and produces the normalized text used for matching. |
| [normalize-item](shared/normalize-item.md) | Processing | shared | Maps every route's raw payload to one item schema and deduplicates. |
| [store-writer](shared/store-writer.md) | Processing | shared | Writes items, comments, analysis and metrics into ClickHouse exactly once in effect. |
| [backfill-orchestrator](shared/backfill-orchestrator.md) | Registry | shared | Starts each new source's history read on its own service and hands it to the rotation when done. |
| [comment-decay-scheduler](shared/comment-decay-scheduler.md) | Registry | shared | Keeps every post's comments up to date: opens, advances, stops, extends and speeds up comment series. |
| [poster-resolver](shared/poster-resolver.md) | Registry | shared | Deduplicates candidate posters from keyword hits and calls the right platform resolver. |
| [qualifier](shared/qualifier.md) | Registry | shared | Applies the ten registry rules: add, mention-only, review or reject. |
| [registry-writer](shared/registry-writer.md) | Registry | shared | Applies registry decisions to the sources table exactly once, with an audit trail. |
| [deletion-propagator](shared/deletion-propagator.md) | Support | shared | Applies every deletion to every store, recomputes aggregates and notifies clients. |
| [quota-governor](shared/quota-governor.md) | Support | shared | Holds every API and vendor budget; allows, delays or denies each call by priority. |
| [raw-archiver](shared/raw-archiver.md) | Support | shared | Archives every raw payload to object storage and replays it for reprocessing. |
| [retention-purger](shared/retention-purger.md) | Support | shared | Runs each source's retention clock and proves it with audit records. |
| [source-health-canary](shared/source-health-canary.md) | Support | shared | Probes every route, flips health and fallback flags, never evades a block. |

## Decisions proposed while drafting (decided in D2)

The PRDs introduce a few cross-cutting choices that `_shared/CONVENTIONS.md` did not fix. D1 found conflicts against all nine, so D2 decided each of them in an ADR, sometimes differently from the proposal; the proposals stay below as they were made, except decision 8, which ADR-0024 rewords to the decisions that shape it, and the ADR named after each one is the decision (ADR-0070, ADR-0024):

1. **Completion topic `jobs.completed`** (schema `jobs.completed/v1`), written by the listening-sdk job wrapper after every job with a report (`new_count`, `seen_count`, `pages`, `cost_units`, `reply_candidates`); comment-decay-scheduler and backfill-orchestrator consume it. (comment-decay-scheduler) Decided in ADR-0017.
2. **Budget priorities 1 to 5 and modes** in quota-governor: 1 tier-1 rotation, client refresh, ops, canaries; 2 tier-2 rotation, client keyword searches, comment steps up to +24 h; 3 tier-3 and dormant rotation, later comment steps, replies, +7 d metrics; 4 hot-post extras and resolvers; 5 backfill. Modes `normal`, `stretch` from 80% of a budget (priorities 1 to 3; from 95% only 1 and 2; amber intervals stretched by a factor, never beyond 24 hours), `exhausted` at 100%. The +24 h comment step is held, never cancelled. Decided in ADR-0018, with explicit rows for every kind of work.
3. **Early stop is armed** only once a post has 5 stored comments or after its +24 h step, so a post with no comments at +1 h keeps its series. (comment-decay-scheduler) Decided in ADR-0019.
4. **backfill-orchestrator is the single writer of `backfill_status`**; fb-backfill's PRD also writes it with identical values, to be aligned. A failed or slow backfill ends `capped` and the source enters the rotation anyway. fb-group-posts-poller is the backfill target for Facebook groups. Decided in ADR-0020, with a route table for every source type.
5. **Fallback scope.** A 401 or 403 from a platform means `blocked`, with no automatic fallback and an n8n approval card; a vendor key or plan error is `degraded` and may fall back. A green source watched by a government client is never moved to an amber fallback (`scope = non_government`). (source-health-canary) Superseded by ADR-0021: a 401 or 403 is classified by reason first, and a blocked source, a client-owned property included, falls back to its vendor automatically where the flag is on, never for a government-watched green source, with an n8n notice to ops instead of an approval card (the user's answer of 9 Oct 2026).
6. **News**: a new topic `news.dedup` from news-dedup to normalize-item; a per-host gate in listening-sdk enforcing one connection and 2 to 5 seconds between requests across all news services; news-article-extractor owns the 7-day full-text cache and passes `text_full_ref`. Decided in ADR-0022: store-writer, not normalize-item, consumes `news.dedup`.
7. **Analysis**: a priority lane per task (`jobs.analysis-<task>.priority`) for tier-1 sources; `items.analysis/v1` keyed by `item_id:task:model_version` with an `input_hash`; budget tag `analysis_model_api` if a hosted model is chosen; YouTube audio and video are not downloaded in v1 (thumbnails only), pending legal review. Decided in ADR-0023, with one priority lane per analysis service; media downloads follow the register of permitted uses of ADR-0068.
8. **TikTok**: every commenter's, replier's, reactor's and member's identity, on every route and not only TikTok's, is replaced by a keyed `author_ref` inside the adapter before the first write, so `raw.items` holds the record as returned, minus identities (ADR-0010); tt-client-videos-fetcher writes its own +24 h and +7 d observations (ADR-0012, ADR-0034) under the retention class `tiktok_display` (ADR-0054); a client-authorised account keeps its reach tier and `push_covered = false`, is read hourly (ADR-0049) and is never reconciled through a vendor (ADR-0052), though, like any other source, it falls back to its vendor route under ADR-0021's conditions when its green access is lost (ADR-0021). Decided in ADR-0024.
9. **New control-plane tables** proposed by individual PRDs: `comment_series`, `backfill_runs`, `x_read_ledger`, `ig_hashtag_ledger`, `budget_reservations`, `budget_history`, `canary_targets` columns, `news_urls`, `news_stories`, `news_story_members`, `model_versions`, `taxonomy_nodes`, `kb_entities`, `kb_aliases`, `brand_assets`. Decided in ADR-0025, with the stores other services read added to CONVENTIONS.

## Reading notes

- Numbers come only from the study's fact sheets (list prices read 2 to 6 Oct 2026); anything not yet known is marked "to be measured in the pilot" or "to be confirmed in the pilot", including exact vendor endpoint paths not documented publicly.
- PRDs run about 2,000 to 3,000 words each (about 210,000 words in total, code and JSON examples included); section 5.1 of every fetcher states its trigger and rotation, and section 13 gives the acceptance tests.
