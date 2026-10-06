# Conventions and shared context for the service PRDs

Product: a social-media and news listening platform for the Iraqi market, built by Abdullah's team (stack: Supabase Postgres, n8n, Node, React, FlutterFlow; plus Redpanda, ClickHouse, Backblaze B2 or Hetzner Object Storage, Hetzner servers). Clients are brands, companies and potentially Iraqi government bodies (civilian ministries and state companies). Volume target at full scale: about 1,000,000 new posts and comments a day (30.5M a month): Facebook 12.0M, TikTok 7.5M, Instagram 4.5M, YouTube 3.0M, Telegram 2.4M, X 0.6M, LinkedIn 0.15M, news 0.375M articles, plus 60,000 web-search queries a month. Retention target: ten years of history as aggregates and derived scores; identifiable raw items only as long as each platform's rules allow.

Two hard constraints decided on 6 Oct 2026:
1. No Israeli-owned or Israel-affiliated vendor anywhere in the stack. Excluded: Bright Data, NetNut/Alarum, Nimble, Tavily, Webz.io. Flagged (client decides): Cloudflare, ClickHouse Inc. (open-source server self-hosted is fine), Perplexity (minor), Yandex. Cleared vendors used below: Oxylabs/Decodo, Apify (Czechia), EnsembleData (Singapore), Telemetrio (Estonia), DataForSEO (Estonia), Mojeek (UK), Perplexity (US, minor flag), Hetzner, Backblaze, Meilisearch, Typesense, Redpanda, Supabase, Hugging Face. Weakly cleared (country known, owner not verified): ScrapeCreators, SociaVault, HikerAPI, TikHub, twitterapi.io, DataImpulse, Scrapfly.
2. No route that rests on a breach of a platform's terms. Route classes: GREEN = official API or licensed index under a contract we hold. AMBER = data bought from a screened vendor that does the collection itself; the breach, if any, sits in the vendor's contract, not ours; every amber service is optional, behind a feature flag, and its provenance is disclosed to clients and excluded from government contracts. RED = our own collection in breach of terms: not built. There is no green route to third-party TikTok content, no green comments on third-party Telegram channels, no green Facebook Groups, no green keyword search of Facebook posts, no clean Google search route.

## Naming, repository, deployment

- Service names are `<source>-<action>` (per-source) or `<action>` (shared). Prefixes: fb, ig, tt, x, li, tg, yt, news, web; shared services have no prefix.
- One repository, one shared SDK (`listening-sdk`): adapter contract, topic schemas, idempotency helpers, control-plane client, quota and canary hooks, structured logging, metrics. One container image per service, deployed on Hetzner (Kubernetes or Nomad; the PRDs say "the cluster"). Each service scales on its own queue depth or partition lag. Config by environment variables; secrets from the control plane's vault (Supabase Vault). No service holds platform accounts; official API tokens are per client (Meta, LinkedIn, TikTok Display) or per company app (X, YouTube) and are injected per job.
- Language: Node (TypeScript) for every service except the analysis workers (Python, GPU pool or model API) and the news extractor (Python, trafilatura).
- Event bus: Redpanda from day one. Topics (all partitioned by `source_id` unless noted):
  - `raw.items` — every record exactly as a fetch or push returned it, plus envelope.
  - `items.normalized` — one schema for every platform, enriched by language and dialect detection.
  - `item.hits` — keyword hits on items whose poster is already a registered source.
  - `discovery.hits` — keyword hits on items whose poster is not a registered source.
  - `poster.profiles` — resolved identities of candidate posters.
  - `registry.decisions` — the qualifier's decisions.
  - `source.events` — registry changes (added, updated, tier change, dormant, retired, fallback_on, fallback_off).
  - `items.analysis` — model outputs keyed by item and model version.
  - `item.metrics` — engagement counts observed over time.
  - `deletions` — items or posters to remove, with reason.
  - `article.urls` — news URLs found but not yet fetched.
  - `search.results` — web-search results before routing.
  - `crawl.policies` — per-host crawl permissions.
  - Per-source job queues (`jobs.<service>`) — work items for pollers, backfills, comment and reply fetches, metrics refreshes. Partitioned by `source_id` so one source is never worked twice at once.
  - Dead-letter: `dlq.<service>`.
- Control plane: Supabase Postgres. Tables: `sources`, `keywords`, `clients`, `client_sources` (which client watches which source), `cursors` (source × service), `budgets` (API and vendor budgets with counters), `decisions`, `review_queue`, `deletion_requests`, `crawl_policies`, `retention_classes`, `vendor_keys`, `canary_targets`, `service_runs` (last run, lag, errors per service). The registry is the `sources` table.
- Object storage: raw payloads under `raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst`; media under `media/<sha256>`; Parquet archive under `archive/<platform>/<yyyy>/<mm>/`.
- Analytics store: ClickHouse (open-source, self-hosted), tables `items`, `comments` (same schema as items with `parent_id`), `analysis`, `metrics_timeseries`, `aggregates_hourly`, `sources_dim`, `keywords_dim`; partitioned by month; Arabic text index on `text_norm`; TTL rules by retention class.

## The registry (`sources` table)

Columns every service may rely on: `source_id` (uuid), `platform` (facebook, instagram, tiktok, x, linkedin, telegram, youtube, news, web), `source_type` (page, group, account, creator, channel, company_page, site, hashtag, keyword_rule), `platform_id`, `handle`, `url`, `display_name`, `route` (green or amber), `vendor` (null, sociavault, scrapecreators, tikhub, ensembledata, harvestapi, apify_tugelbay, apify_sovereigntaylor, telemetrio), `tier` (1, 2, 3, push, dormant, retired), `retention_class`, `client_ids[]`, `owned_by_client` (bool: client-owned property with our webhook or bot), `followers`, `country_signals` (jsonb), `lang_share` (jsonb), `added_by` (qualifier, client, ops), `added_at`, `last_hit_at`, `last_polled_at`, `next_poll_at`, `backfill_status` (pending, running, done, capped), `health` (ok, degraded, fallback, blocked), `notes`.

Per source × service cursor rows in `cursors`: `source_id`, `service`, `cursor` (opaque string: a `since` timestamp, a page token, a `since_id`, a `max_cursor`), `last_success_at`, `last_error`, `consecutive_errors`.

## Rotation policy (decided 6 Oct 2026: tiered by reach)

Freshness is a product promise: every registered page, group, account, channel, company page and site is re-checked for new posts on a rotation, and every post's comments are re-checked on a schedule, so the data is never older than the tier allows.

Posts (pollers):
- Tier 1 (100,000 or more followers, or on a client's priority list): polled every 60 minutes; maximum staleness 1 hour.
- Tier 2 (10,000 to 99,999 followers): every 6 hours; maximum staleness 6 hours.
- Tier 3 (below 10,000): every 24 hours; maximum staleness 24 hours.
- Push (client-owned properties with webhooks, PubSubHubbub or a bot): no polling for new posts; one reconciliation poll a day to catch missed pushes.
- Dormant (no post in 30 days): weekly; a new post promotes the source back to its reach tier.
- Retired (no hits and no client interest for 180 days): not polled; stays in the registry.
- Mechanics: the scheduler keeps `next_poll_at` per source and emits a job when it is due; jobs are ordered by `next_poll_at` then by tier, so a source is never skipped twice in a row; a source's next poll is set from the START of its last poll (fixed cadence, not drift); if a poller falls behind (lag above one interval), it polls the most-stale sources first and raises a `rotation_behind` alert; a vendor route pays per request, so tier intervals on amber routes may be stretched by the quota governor when the monthly budget is 80% consumed, never below daily.
- Incremental: every poll reads only what is newer than the cursor; a full re-read happens only for backfill.
- Backfill: when a source is added, the last 90 days (or the route's cap, whichever is smaller) are fetched once, then the source joins the rotation.

Comments (comment fetchers, driven by `comment-decay-scheduler`):
- Series after a post is first seen: +1 h, +6 h, +24 h, +3 d, +7 d, then weekly until day 30.
- Early stop: when a fetch adds fewer than 5% new comments (and fewer than 5 absolute), the remaining series is cancelled.
- Extension: when a fetch at day 7 still adds 20% or more new comments, the series continues every 2 days until day 30.
- Hot posts: when comment velocity exceeds 100 new comments per hour, an extra fetch is inserted every hour for the next 6 hours.
- Replies: fetched only for threads above the route's reply threshold (listed per service), through the same service with job kind `replies`.
- Beyond day 30: no automatic fetches; a client can request a refresh of a specific post, budget permitting.
- Each fetch pages until it reaches comments older than the newest one already stored (newest-first APIs) or until the page token is exhausted (oldest-first APIs); it reports `new_count`, `seen_count`, `pages`, `cost_units`.
- Edits and deletions: on refetch, the service compares content hashes of comments it already stored; changed text becomes a new version, missing comments (when the API is complete) become `deletions` with reason `platform_sync`.

Metrics (likes, shares, views, comment counts) are refreshed at +24 h and +7 d by the source's metrics or details service, or by the next poll where the API returns counts with the post.

## Idempotency and deduplication

- `idempotency_key` = `<platform>:<kind>:<platform_id>` where the platform gives ids; for Facebook comments under PPCA (no ids), `<platform>:comment:<post_id>:<sha256(created_time + text)>`; for news, `news:article:<canonical_url_hash>`.
- `raw.items` is append-only; `normalize-item` deduplicates; stores are upserts keyed on `item_id`.
- A job carries `attempt` and is safe to replay; a fetch that was partially written is completed by the next attempt because cursors advance only after the batch is acknowledged by Redpanda.

## Retention classes

- `x_24h_sync`: X content; deletions mirrored within 24 hours of X's compliance signal; nothing else purged by time.
- `youtube_30d_text`: raw comment text deleted or refreshed after 30 days; derived metrics kept up to 36 months; no aggregation across channel owners except under the analytics carve-out.
- `linkedin_48h`: member social-activity data purged after 48 hours; organization data as the API terms allow.
- `meta_on_request`: Meta Platform Data deleted when no longer necessary, on Meta's request, on client offboarding, or on a user's request.
- `vendor_agreed`: per the vendor contract and our author notice; default 24 months for raw text.
- `news_excerpt`: excerpt and metadata kept; full text only in a 7-day cache.
- Aggregates and derived scores: ten years, all classes.

## Quotas, budgets and the quota governor

Every service that calls an external API or vendor declares a `budget_tag` and asks `quota-governor` for allowance before a batch; the governor keeps counters in `budgets` and returns allow / wait-until / deny. Budget facts (list prices read 2 to 6 Oct 2026):
- Meta Graph (PPCA): 4,800 calls × engaged users per 24 h on the Pages bucket with a system-user token; about 600 ranked posts per Page per year on `/feed`; `limit` max 100; error 80001 means "too many calls to this Page".
- X pay-per-use: USD 0.005 per post read, USD 0.010 per user read, deduplicated per resource per UTC day; hard cap 3,000,000 post reads per billing cycle; filtered stream up to 1,000 rules; a government end user or a multi-client product requires an Enterprise plan.
- YouTube Data API: 10,000 units a day by default; `search.list` 100 units (100 calls a day cap), `commentThreads.list`, `comments.list`, `playlistItems.list`, `channels.list`, `videos.list` 1 unit each.
- Instagram: 30 unique hashtags per Instagram business account per 7 days; `/{media}/comments` 50 per query; Business Discovery does not return age-gated accounts.
- LinkedIn Community Management API: client-administered pages only; member data stored at most 48 hours; no social-feed use; no export to clients.
- TikHub: about USD 0.50 to 1.00 per 1,000 requests by tier, 10 requests a second per endpoint, 20 items a page, billed on HTTP 200 only. EnsembleData: the alternative the team already uses; same role.
- SociaVault: USD 1.99 to 4.83 per 1,000 credits, 1 credit per request for most endpoints, credits never expire. ScrapeCreators: USD 0.99 to 1.88 per 1,000 requests.
- Telemetrio: subscription plans USD 65 to 499 (500 to 2,500 channels), search priced per request and per keyword. Apify Telegram preview Actors: about USD 2,900 to 7,200 a month at 2.4M items.
- harvestapi (Apify): about USD 225 to 300 a month at 0.15M LinkedIn items.
- Perplexity Search API: USD 5 per 1,000 requests, up to 5 queries per request; about USD 60 a month at 60,000 queries. Mojeek Business: GBP 3 per 1,000 queries, results may be stored; about GBP 180 a month.
- GDELT DOC API: free, 1 request per 5 seconds. Common Crawl: free, monthly.

## Error handling, canaries and fallback

- HTTP 429 and vendor rate-limit responses: exponential backoff with jitter starting at 30 s, max 15 min, then the job returns to the queue with `attempt + 1`; after 5 attempts the job goes to `dlq.<service>` and an alert fires.
- HTTP 401 and 403: the service marks the token or route `degraded`, stops the batch, and alerts; it never rotates accounts or IPs to get around a block.
- "Empty 200" (a 200 response with no data where data is expected): counted per route; above 5% in 15 minutes the canary flips `health = degraded` and, where an amber or alternate route exists and the flag is on, `fallback_on`; the poller reads the flag at the start of every job.
- Schema change (unknown shape): the raw payload is still archived; the normalizer raises `schema_unknown` and parks the batch for review.
- Every service exposes `/healthz`, `/metrics` (Prometheus), structured JSON logs with `job_id`, `source_id`, `route`, `vendor`.

## Observability and SLOs

Per service: `items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds` (now minus `next_poll_at` for the most overdue source), `staleness_seconds_p95` (age of the newest item per source at poll time), `cost_units_total`, `quota_denied_total`, `dlq_total`. SLOs: rotation lag below one tier interval for 99% of sources per day; comment series completed on time for 95% of posts; zero jobs lost (DLQ reviewed daily).

## Security and compliance in every service

- No account pools, no CAPTCHA solving, no residential proxies on platform APIs; proxies only on the news crawler for Cloudflare-challenged hosts.
- Government clients: X data only under an Enterprise plan with the end user declared; no surveillance, sensitive-event monitoring or sensitive-attribute profiling; Meta data never processed for law-enforcement or national-security purposes; amber data excluded from government contracts.
- Individuals are never profiled: a mention keeps a hashed author reference; no backfill of individuals.
- Every item carries provenance (route class, vendor, service, fetch time) to the client-facing provenance statement.

## PRD template (every file follows this, in this order)

```
# <service-name>

**Platform:** <platform or Shared> · **Route:** <green | amber (optional, flag `<FLAG_NAME>`) | shared> · **Lane:** <Discover and qualify | Fetch posts | Comments | Processing | Registry | Support> · **Owner:** <team role> · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists
## 2. Objective (the end state this service delivers)
## 3. Scope
### In scope
### Out of scope
## 4. Users and consumers
## 5. How it works
### 5.1 Trigger and rotation   <- mandatory for pollers, comment fetchers, searches, receivers: cadence by tier, rotation mechanics, catch-up, backfill
### 5.2 Step by step
### 5.3 The call it makes      <- endpoint or vendor call, parameters, fields requested, page size, pagination, auth
### 5.4 What it gets           <- fields, examples, what it does not get
## 6. Inputs and outputs
### 6.1 Reads                  <- topics, queues, control-plane tables
### 6.2 Writes                 <- topics, envelope, example message
### 6.3 State                  <- cursors, counters, flags
## 7. Limits, quotas and cost
## 8. Failure handling and fallback
## 9. Non-functional requirements   <- throughput at full scale, latency, idempotency, scaling, security
## 10. Metrics and alerts
## 11. Dependencies
## 12. Risks and mitigations
## 13. Acceptance criteria        <- testable, numbered
## 14. Open questions
```

Writing rules: concrete, specific to this service, no placeholders, no generic filler; numbers only from this file's fact sheets or marked "to be measured in the pilot"; USD explicit on every cost; British or American spelling consistently; 1,200 to 2,200 words per PRD; use the exact service names from the index; cross-reference other services by name; write for an engineer who will build it next week and for Abdullah who will read why it exists.

## Per-platform fact sheets

### Facebook (green = Meta Graph API under Page Public Content Access on a verified Tech Provider app; amber = SociaVault or ScrapeCreators)
- Approvals: Business Verification (days), App Review (up to several weeks), Access Verification for Tech Providers (about 5 days), annual Data Use Checkup. Reviewers want to see a working analytics product.
- PPCA grants: Pages Search API and public Page posts, comments, reactions; no Groups (Groups API removed 22 Apr 2024), no Reels on `/feed`, no keyword search of posts, no commenter identity, comment ids not returned under PPCA.
- `/feed`: about 600 ranked posts per Page per year; `limit` max 100; `since` and `until` supported; user information only with a Page access token (client-owned Pages).
- Comments: `GET /{post-id}/comments?filter=stream&limit=100`, fields message, created_time, like_count; no id and no `from` under PPCA.
- Reactions: `reactions.type(LIKE).summary(total_count)` per type, requested on the feed call.
- Webhooks for Pages (client-owned): topics `feed`, `comments`; subscribe with `/{page-id}/subscribed_apps`; events include commenter identity.
- Pages Search: `GET /pages/search?q=<name>&fields=id,name,location,link,is_verified` — finds Pages by name, not posts.
- Rate limit: Pages bucket 4,800 calls × engaged users per 24 h; use a system-user token; error 80001 on per-Page overload; latency of public content up to 24 hours in practice (Sprinklr documents "Latency: Up to 24 hours", "Refresh rate: 2 to 3 hours").
- Amber: SociaVault Facebook endpoints (search, group posts, post comments; 1 credit per request); ScrapeCreators `/v1/facebook/group/posts`, `/v1/facebook/post/comments` (USD 0.99 to 1.88 per 1,000 requests). Vendor data includes poster names and ids.
- Platform Terms: no surveillance (law enforcement or national security), no sale or licensing of Platform Data, Tech Provider processes only on behalf of its client, delete when no longer necessary.

### Instagram (green = Instagram Graph API with Facebook Login, Advanced Access and Instagram Public Content Access; amber = SociaVault)
- Hashtag search: `GET /ig_hashtag_search?user_id=<ig-user-id>&q=<tag>` then `/{hashtag-id}/recent_media` and `/top_media` with fields id, caption, media_type, media_url, permalink, timestamp, like_count, comments_count; 30 unique hashtags per Instagram business account per rolling 7 days; no username on hashtag media for accounts the app does not manage.
- Business Discovery: `GET /{ig-user-id}?fields=business_discovery.username(<handle>){followers_count,media_count,biography,website,name,media{id,caption,media_type,permalink,timestamp,like_count,comments_count}}`; business and creator accounts only; age-gated accounts not returned; no comment text for third-party media.
- Mentions: `/{ig-user-id}/tags`, `mentioned_media`, `mentioned_comment` for client accounts; Stories mentions not supported.
- Webhooks: `comments`, `mentions` on client-owned accounts.
- Comments on client media: `GET /{media-id}/comments?fields=id,text,username,timestamp,like_count,replies{...}` (50 per query, replies by field expansion).
- Instagram Public Content Access allows "understand public sentiment around brand"; analytics only as aggregated, de-identified output.
- Amber: SociaVault Instagram search and comments; third-party comments show about the first 15 visible comments.

### TikTok (amber = TikHub or EnsembleData; green only for the client's own account through the Display API)
- Research Tools: academic and non-profit only; Commercial Content API: EU paid ads only; Mentions API: badged Marketing Partners only. No green route to third-party content.
- Display API: `video.list` with scopes `user.info.basic,video.list` after the client's OAuth; own videos and stats only; no comments endpoint.
- TikHub: keyword search with server-side country, hashtag feed, user posts by cursor, user info, video detail, comments and replies; 20 items a page; 10 requests a second per endpoint; billed on HTTP 200; USD 0.50 to 1.00 per 1,000 requests by daily volume tier. EnsembleData: equivalent endpoints; already contracted by the team; used as primary or fallback per the flag.
- Developer Terms forbid building profiles or databases on any individual.

### X (green = X API v2 pay-per-use; Enterprise once a government end user or several clients are on board)
- Recent search: `GET /2/tweets/search/recent?query=...&max_results=100&tweet.fields=created_at,public_metrics,conversation_id,lang,geo,entities&expansions=author_id,attachments.media_keys`; 7-day window; operators `lang:ar`, `place_country:IQ`, `conversation_id:`, `from:`, `-is:retweet`.
- Full-archive search: `GET /2/tweets/search/all` back to 2006 on pay-per-use.
- Filtered stream: `GET /2/tweets/search/stream` with up to 1,000 rules managed through `/2/tweets/search/stream/rules`.
- User timeline: `GET /2/users/{id}/tweets?since_id=...&max_results=100`.
- User lookup: `GET /2/users/by/username/{handle}?user.fields=public_metrics,verified,location,description,created_at`.
- Compliance: batch compliance jobs for post and user ids; deletions must be mirrored within 24 hours.
- Cost: USD 0.005 per post read, USD 0.010 per user read, deduplicated per resource per UTC day; cap 3,000,000 post reads per month on pay-per-use.
- Developer Agreement: no surveillance, no monitoring of sensitive events (protests, rallies), no profiling on sensitive attributes; a Government End User requires an Enterprise plan, must be named at use-case review, and X may refuse; self-serve plans are for a limited number of end users.

### LinkedIn (green = Community Management API for client-administered pages; amber = harvestapi Actors on Apify)
- Posts API with `r_organization_social`; Comments API; Organization Social Action Notifications (webhooks) for client pages; organization must grant ADMINISTRATOR, DIRECT_SPONSORED_CONTENT_POSTER or CONTENT_ADMIN.
- Restricted uses: member social-activity data stored at most 48 hours; most member profile data 24 hours; organization social activity data six weeks (six months if authenticated); no social-feed use; member data cannot be exported to customers.
- Amber: harvestapi `linkedin-post-search`, `linkedin-company-posts`, `linkedin-post-comments` Actors on Apify; about USD 225 to 300 a month at 0.15M items.

### Telegram (green = Bot API in channels that add our bot; amber = Telemetrio and Apify preview Actors)
- Bot API: `channel_post` updates for channels where the bot is an administrator; messages in linked discussion groups where the bot is a member; no history method; bots see nothing in channels they are not added to.
- Content Licensing Terms: access "for any purpose other than ordinary, legitimate, and intended use of the Telegram platform as its user is prohibited"; this covers user-account readers and, on our reading, t.me previews, so neither is built.
- Telemetrio: `/v1/search/messages` (alpha; 7 to 90 day windows; priced per request and per keyword), channel stats (subscribers, category, country, growth); plans USD 65 (500 channels) to USD 499.
- Apify t.me preview Actors (tugelbay/telegram-posts-scraper, sovereigntaylor/telegram-scraper): posts, views, forwards of public channels; comments mostly unavailable; about USD 2,900 to 7,200 a month at 2.4M items.
- Iraq blocked Telegram in Aug 2023 and from 3 Apr to 9 May 2026; host outside Iraq.

### YouTube (green = YouTube Data API v3 with PubSubHubbub)
- PubSubHubbub: subscribe per channel at `https://pubsubhubbub.appspot.com/subscribe` with topic `https://www.youtube.com/xml/feeds/videos.xml?channel_id=<id>`; lease renewal before expiry; Atom notification with video id, title, published, updated.
- `playlistItems.list` on the channel's uploads playlist (1 unit a page of 50) for daily reconciliation.
- `videos.list?part=snippet,statistics,contentDetails,topicDetails&id=<up to 50 ids>` (1 unit).
- `commentThreads.list?part=snippet,replies&videoId=<id>&maxResults=100&order=time` (1 unit a page); `comments.list?parentId=<id>` for replies beyond those embedded (1 unit a page).
- `search.list?q=...&type=video&regionCode=IQ&relevanceLanguage=ar&order=date&publishedAfter=...` (100 units; 100 calls a day cap).
- `channels.list?part=snippet,statistics,brandingSettings&id=<id>` (1 unit).
- Default quota 10,000 units a day; extensions by audit; Developer Policies: raw comment text no longer than 30 days (delete or refresh), derived metrics up to 36 months for "Analytics & Reporting" clients, no aggregation across channels of different owners except under the carve-out, no profiling on protected attributes, audit at any time.

### News websites (green = our own crawler obeying robots.txt, Cloudflare Content Signals, RSL and HTTP 402)
- About 500 Iraqi and regional domains, about 25 articles a day each; feeds (RSS, Atom, rssturbo), news sitemaps (`sitemap-news.xml`, Google news-sitemap rules), homepage diff for sites without feeds; about a quarter of Iraqi sites sit behind a Cloudflare challenge (headless fallback or Decodo/Oxylabs egress only for those).
- Extraction with trafilatura: title, body, author, date, canonical URL, language, images; store an excerpt of 200 to 300 characters plus metadata and hashes; full text only in a 7-day cache; honor `Content-Signal` headers, RSL licence files, HTTP 402 pay-per-crawl (Cloudflare, closed beta), and Iraqi copyright law (Law No. 3 of 1971) by storing excerpts.
- Comments: Disqus API where a site uses Disqus; the Meta Comments plugin was discontinued 10 Feb 2026.
- Crawl politeness: per-host concurrency 1, 2 to 5 seconds between requests, ETag and If-Modified-Since, user agent that names the company and a contact address.

### Web search (green = Perplexity Search API and Mojeek Business; Common Crawl and GDELT free; no Google route)
- Perplexity Search API: `country` IQ, `search_language_filter` ar (ckb where supported), up to 5 queries a request, USD 5 per 1,000 requests; customer owns the output; US export screening applies (Iraq is not embargoed).
- Mojeek Web Search API, Business plan: `rb=IQ`, `lb=AR`, results may be stored; GBP 3 per 1,000 queries.
- Common Crawl index: monthly, free; GDELT DOC 2.0 API: free, 1 request per 5 seconds; GDELT permits governmental use.
- Not used: Google Custom Search (closed to new customers, ends 1 Jan 2027), Gemini and Vertex grounding (forbid building an index from links), Google News RSS and Alerts (behind robots.txt), Brave and Exa (forbid storing results), Kagi (resells scraped Google), Yandex (Russian, sanctions optics), Tavily and Webz.io (Israeli).
- 200 keywords × 9 variants once a day is about 54,000 to 60,000 queries a month.

## Service index (file path = `prds/<platform>/<service>.md`)

Facebook (10): fb-page-search, fb-keyword-search (amber), fb-page-resolver, fb-page-feed-poller, fb-backfill, fb-group-posts-poller (amber), fb-client-webhook-receiver, fb-post-comments-fetcher, fb-group-comments-fetcher (amber), fb-reactions-fetcher.
Instagram (8): ig-hashtag-search, ig-keyword-search (amber), ig-account-resolver, ig-account-media-poller, ig-mentions-fetcher, ig-webhook-receiver, ig-own-comments-fetcher, ig-comments-fetcher (amber).
TikTok (7): tt-keyword-search (amber), tt-hashtag-feed-poller (amber), tt-user-resolver (amber), tt-profile-videos-poller (amber), tt-client-videos-fetcher (green), tt-video-comments-fetcher (amber), tt-video-stats-refresher (amber).
X (7): x-recent-search, x-full-archive-search, x-user-resolver, x-filtered-stream, x-user-timeline-poller, x-replies-fetcher, x-compliance-sync.
LinkedIn (7): li-post-search (amber), li-org-resolver (amber), li-client-posts-poller, li-company-posts-poller (amber), li-notification-receiver, li-own-comments-fetcher, li-post-comments-fetcher (amber).
Telegram (5): tg-message-search (amber), tg-channel-resolver (amber), tg-bot-channel-receiver, tg-channel-posts-poller (amber), tg-discussion-receiver.
YouTube (9): yt-keyword-search, yt-web-search-bridge, yt-channel-resolver, yt-pubsub-receiver, yt-uploads-reconciler, yt-video-details-fetcher, yt-comments-fetcher, yt-replies-fetcher, yt-text-purger.
News (8): news-site-resolver, news-robots-checker, news-feed-poller, news-sitemap-poller, news-homepage-differ, news-article-extractor, news-comments-fetcher, news-dedup.
Web (5): web-search-perplexity, web-search-mojeek, web-commoncrawl-scanner, web-gdelt-poller, search-hit-router.
Shared, processing (10): normalize-item, lang-dialect-id, keyword-matcher, analysis-sentiment, analysis-topics, analysis-media, analysis-entities, store-writer, aggregator, alert-evaluator.
Shared, registry and support (10): poster-resolver, qualifier, registry-writer, backfill-orchestrator, comment-decay-scheduler, raw-archiver, retention-purger, deletion-propagator, source-health-canary, quota-governor.

Feature flags for amber services: `FB_VENDOR_ROUTE`, `IG_VENDOR_ROUTE`, `TT_VENDOR_ROUTE`, `LI_VENDOR_ROUTE`, `TG_VENDOR_ROUTE` (value: off, or the vendor name).

## Qualifier rules (the registry logic every discovery and resolver service feeds)

1. Type. Facebook: Page or group (profiles are individuals). Instagram: business or creator account_type. TikTok: creator when followers reach 2,000 or verified. X: public figure or organization when followers reach 500, verified, or on a client watchlist. YouTube channels, Telegram channels, LinkedIn company pages and news domains always qualify as sources. Everything else is an individual.
2. Iraqi signals: any two of a location naming an Iraqi city or governorate, a +964 number, an .iq domain or Iraqi outlet link, at least 40% Iraqi Arabic or Sorani on the last 20 posts, membership of a client seed list. None: reject. One: review.
3. Activity: at least one post in 30 days, else dormant (weekly).
4. Spam: more than 50 posts a day with over 60% duplicate text rejects; default avatar on an account under 30 days old goes to review.
5. Route cap and budget: PPCA Pages per token, YouTube quota share, vendor monthly spend per source; over the cap, new sources queue by reach and the client is told.
6. Tier by reach (1: 100k+, 2: 10k to 99,999, 3: below 10k; push for client-owned), retention class by route.
7. Individuals: never sources, never profiled; the matched post is a mention with a hashed author reference; no backfill; re-qualified as a creator only when resolver numbers cross the creator threshold.
8. Groups: a hit inside a Facebook group (amber only) adds the group as a source; the poster is qualified separately.
9. Decay: 90 days without hits or client interest moves a source down a tier; 180 days retires it; rejected candidates are remembered 180 days.
10. Review: borderline cases go to an n8n approval card (Telegram or Slack); default after 24 hours is reject.

## Addendum (6 Oct 2026, applies to every PRD)

### Comment series profiles per route (comment-decay-scheduler config; each comment fetcher uses its row)

| Route | Comment service | Series after the post is first seen | Replies |
|---|---|---|---|
| Facebook Pages, green | fb-post-comments-fetcher | +1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30 | in the stream (`filter=stream`); no ids, dedup by hash |
| Facebook groups, amber | fb-group-comments-fetcher | +1 h, +6 h, +24 h, +3 d | by comment id when the vendor exposes it |
| Instagram client media, green | ig-own-comments-fetcher | +1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30 | field expansion on the same call |
| Instagram other media, amber | ig-comments-fetcher | +6 h, +24 h, +3 d | none (about 15 visible comments) |
| TikTok, amber | tt-video-comments-fetcher | +1 h, +6 h, +24 h, +3 d, +7 d | per comment with more than 10 replies |
| X, green | x-replies-fetcher | +1 h, +6 h, +24 h, +3 d (recent search window ends at 7 d) | replies and quotes by `conversation_id:` |
| YouTube, green | yt-comments-fetcher, yt-replies-fetcher | +6 h, +24 h, +3 d, +7 d, +30 d | `comments.list` for threads with more than 5 replies |
| LinkedIn client posts, green | li-own-comments-fetcher | +6 h, +24 h, +3 d | in the same call; member data purged after 48 h |
| LinkedIn other posts, amber | li-post-comments-fetcher | +24 h, +3 d | none |
| Telegram own channels, green | tg-discussion-receiver | push (live), daily health check | live |
| News (Disqus sites), green | news-comments-fetcher | +6 h, +24 h, +3 d | threaded in the same call |

The general rules apply on every row: early stop when a fetch adds fewer than 5% new comments and fewer than 5 absolute; extension every 2 days to day 30 when a fetch at day 7 (or the last scheduled fetch, on shorter series) still adds 20% or more; an extra hourly fetch for 6 hours when velocity exceeds 100 new comments an hour; on amber routes the quota-governor may drop the hot-post extra fetches first when the monthly budget passes 80%.

### Other shared decisions

- Lanes used in PRD header lines: Discover and qualify; Fetch posts; Comments; Comments and stats; Processing; Registry; Support.
- Groups, channels and hashtags are tiered with the same thresholds as accounts, using member, subscriber or (for hashtags) the client's priority setting in place of followers.
- Job queues are Redpanda topics `jobs.<service>`; a job carries `job_id` (ULID), `source_id`, `kind` (rotation, reconciliation, backfill, comments, replies, metrics, ops_force), `due_at`, `attempt`, `post_ref` (for comment, reply and metrics jobs), `series_step` (for comment jobs).
- Every service that polls keeps its own rotation scheduler as a leader-elected loop (Postgres advisory lock) that emits due jobs, exactly as described in fb-page-feed-poller; comment, reply and metrics jobs are emitted only by comment-decay-scheduler; backfill jobs only by backfill-orchestrator.
- Budget tags (canonical; use exactly these): Facebook Graph `meta_graph_pages:<client_id>`; Facebook vendor `fb_vendor`; Instagram Graph `ig_graph_<ig_user_id>`; Instagram hashtag ledger `ig_hashtag_<ig_user_id>`; Instagram vendor `ig_vendor`; TikTok vendor `tt_vendor` (one tag for all amber TikTok services, with per-service sub-counters); TikTok Display API `tt_display:<client_id>`; X `x_pay_per_use` (sub-counters `post_reads` and `user_reads`, deduplicated per resource per UTC day through the read ledger); YouTube `youtube_data_api` (buckets `search`, `ingest`, `comments`, `reserve`); LinkedIn official `linkedin_cm:<client_id>`; LinkedIn vendor `li_vendor_<action>` (`li_vendor_post_search`, `li_vendor_org_resolver`, `li_vendor_company_posts`, `li_vendor_post_comments`); Telegram vendor `tg_telemetrio_search`, `tg_telemetrio_stats`, `tg_apify_posts`; web search `perplexity_search`, `mojeek_search`, `gdelt_doc_api`; news `news_proxy_egress`, `news_disqus`.
- Vendor flag values: `FB_VENDOR_ROUTE` off | sociavault | scrapecreators; `IG_VENDOR_ROUTE` off | sociavault; `TT_VENDOR_ROUTE` off | tikhub | ensembledata; `LI_VENDOR_ROUTE` off | harvestapi; `TG_VENDOR_ROUTE` off | telemetrio (search and stats) and `TG_POSTS_ACTOR` off | tugelbay | sovereigntaylor (channel posts).
- Search output rule: a search service writes every item it finds to `raw.items`, with `source_id` = the keyword-rule or hashtag source that produced the query, so the item enters the pipeline like any polled item; keyword-matcher is the canonical writer of `item.hits` and `discovery.hits` for items. A search service may also emit `discovery.hits` directly for unregistered authors as an early signal (x-recent-search and tg-message-search do); poster-resolver deduplicates candidates by `candidate_key` (`<platform>:<platform_id>` or `<platform>:<handle>`), so both paths are safe. Services that find sources rather than items (fb-page-search, web-commoncrawl-scanner, search-hit-router) write `discovery.hits` only.
- Written PRDs to stay consistent with (already approved; do not rewrite): fb-page-search, fb-page-feed-poller, fb-backfill, fb-reactions-fetcher, ig-hashtag-search, tt-keyword-search, tt-hashtag-feed-poller, x-recent-search, li-post-search, li-org-resolver, tg-message-search, tg-channel-resolver, yt-keyword-search, yt-web-search-bridge, news-site-resolver, web-search-perplexity, normalize-item, poster-resolver, qualifier, registry-writer.
