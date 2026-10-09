# ADR-0059 · Coverage bought by default: X and news history, and X replies to day 30

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, backfill-orchestrator, comment-decay-scheduler, normalize-item, keyword-matcher, quota-governor, web-commoncrawl-scanner, x (every X service), news (every news service), and the lanes Comments and Comments and stats (every comment fetcher)
Source: D2-Q059 (user decision; changed by the user's answer) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS backfills 90 days (L53) and fetches comments on a series, nothing after day 30 unless a client asks (L56, L61). The PRDs disagree:

- Backfilled posts: one `once` fetch each (`comment-decay-scheduler §5.1 L66`); none beyond day 30, "Abdullah to decide" (`fb-backfill §5.1 L47`, `§14 Q1 L170`); one job per post of the last 30 days from backfill-orchestrator (`li-own-comments-fetcher §5.1 L52`, `li-post-comments-fetcher §5.1 L54`) (AU-045).
- X: keyword rules get a backfill that x-full-archive-search refuses, and a `keyword_history` job on a stale cursor that it takes only on a client request (`backfill-orchestrator §5.3 L72`, `x-full-archive-search §13 L183`, `x-recent-search §5.1 L45`, `x-full-archive-search §5.1 L39`) (AU-094); replies after day 7 have no emitter (`comment-decay-scheduler §5.1 L53`) (AU-040).
- News: backfill goes to news-feed-poller, which takes none, and the remainder to web-commoncrawl-scanner, which lists hosts, not articles (`backfill-orchestrator §5.3 L78`, `news-sitemap-poller §5.1 L51`, `web-commoncrawl-scanner §5.1 L44`) (AU-044, AU-103).
- Series: opened for every post with a comment route (`comment-decay-scheduler §2 L13`), while fetchers expect gates on `comments_count`, Disqus, keyword hits and individuals (`ig-comments-fetcher §13 L164`, `news-article-extractor §5.1 L47`, `tt-video-comments-fetcher §5.1 L50`) (AU-037); LinkedIn keyword finds by default (`li-post-search §5.1 L50`) or "only if the budget allows" (`li-post-comments-fetcher §5.1 L40`) (AU-098); none on X posts about protests, and terms screened before X history (`x-replies-fetcher §14 Q7 L205`, `x-full-archive-search §14 Q4 L192`, `CONVENTIONS L188`).

At stake: what each new source and found post costs before a client asks.

The user's answer, 7 Oct 2026: "I dont understand Q059 question nor recommendation." The orchestrator put the question to the user again, and the user chose "Maximum history", which is option 3.

Settles: AU-037, AU-040, AU-044, AU-045, AU-094, AU-098, AU-103, fb-backfill §14 Q1, ig-comments-fetcher §14 Q3, li-post-comments-fetcher §14 Q4, tt-video-comments-fetcher §14 Q3, x-full-archive-search §14 Q5, x-replies-fetcher §14 Q7.
Depends on: ADR-0018 (priorities), ADR-0052 (amber consent), ADR-0069 (the X terms screen).

## Options

1. **Green history and comments by default, none on amber; older X history and replies on request.** _Taken for its green defaults (a) and (f), with (e) following from (f); its (b), (c) and (d) give way to option 3 (see Decision)._ Each default can be changed alone:
   - (a) Every backfilled post on a green comment route gets one `once` fetch at priority 5, whatever its age (fb-backfill Q1: yes; LinkedIn through the scheduler, not the orchestrator); none on amber in v1. Cost: about 150 comment calls per added Facebook Page (90 days at 600 ranked posts a year, L86), paid in quota (`fb-page-feed-poller §7 L141`); 1 YouTube unit a page (L88); on X USD 0.005 a reply, only the last 7 days visible (`x-replies-fetcher §5.1 L49`).
   - (b) X keyword rules: 7 days from the first recent-search pass (`x-recent-search §5.1 L49`); older history only on a client's request (`keyword_history` from backfill-orchestrator), never on a stale cursor (ADR-0064).
   - (c) News: backfill only through news-sitemap-poller, from regular sitemaps; a site whose sitemaps reach less than 90 days, or that has none, ends `capped`; no Common Crawl URL lister; news pollers start at `added`. Up to about 2,250 article fetches per site (25 a day for 90 days, L212), no per-request price.
   - (d) No X replies for posts older than 7 days in v1; x-full-archive-search drops `replies`.
   - (e) LinkedIn keyword finds get no series unless a client asks (li-post-comments-fetcher Q4).
   - (f) A series opens for posts of registered sources and client-owned properties (amber ones per ADR-0052 and only with a first-sight `comments_count` above zero where given), for keyword finds on green routes and for Disqus sites' articles; never for an X post containing a term on the blocked-terms list x-filtered-stream screens rules with (`x-filtered-stream §5.2 L52`), the F3 table `screened_terms` of ADR-0069, marked by normalize-item on `items.normalized` (x-replies-fetcher Q7). The same screen checks every X term, live or history; refusals go to `review_queue` (`x_terms_screen`) for the account manager's recorded decision; the list is the user's (x-full-archive-search Q4). Budget order unchanged (`comment-decay-scheduler §5.1 L62`).

   Consequences: the scheduler reads `clients`, `news_sites` and the new marker (F2); backfill-orchestrator sends news to news-sitemap-poller only and X keyword rules nowhere; fb-backfill, x-recent-search, li-post-search and news-site-resolver (approved) move under ADR-0001; unless they ask, clients get 7 days of X history and conversation and no comments on backfilled vendor posts.

2. **Comment fetches on amber too:** _Not taken: no comment history on amber routes in v1._ a `once` fetch per backfilled amber post and series for amber keyword finds with a client hit, within each source's vendor cap. Consequences: vendor-route comment history; at one page per fetch, USD 0.50 to 1.00 (TikHub), 0.99 to 1.88 (ScrapeCreators) or 1.99 to 4.83 (SociaVault) per 1,000 backfilled posts (L91, L92), LinkedIn USD 1.50 to 2.00 per 1,000 items (USD 225 to 300 a month for 0.15 million, L94); a five-step TikTok series USD 0.0025 to 0.0050 a video (`comment-decay-scheduler §7 L153`).
3. **More history on X and news:** _Taken, with option 1's green defaults (a) and (f) kept and the budget priorities of ADR-0018 over all of it (see Decision)._ automatic `keyword_history` for new X rules, X replies to day 30, a Common Crawl URL lister (AU-103 option 2). Consequences: fuller history; if keyword rules found all 0.6 million X posts a month (L3), 90 days for the whole set would be about 1.8 million post reads, USD 9,000 and 60% of one cycle's 3,000,000-read cap (L87); old replies USD 0.005 each; a new mode in web-commoncrawl-scanner.

## Decision

Option 3, with option 1's green defaults (a) and (f) kept. Every new X keyword rule gets 90 days of history automatically, X replies are followed to day 30, and news history reaches back 90 days through a Common Crawl URL lister where a site's sitemaps fall short. All of it runs inside the budget priorities of ADR-0018, history at priority 5, and every X term passes the sensitive-terms screen of ADR-0069.

**From option 1, kept**

- (a) Every backfilled post on a green comment route gets one `once` fetch at priority 5, whatever its age (fb-backfill Q1: yes; LinkedIn through the scheduler, not the orchestrator); none on amber in v1. Cost: about 150 comment calls per added Facebook Page (90 days at 600 ranked posts a year, L86), paid in quota (`fb-page-feed-poller §7 L141`); 1 YouTube unit a page (L88); on X USD 0.005 a reply, only the last 7 days visible (`x-replies-fetcher §5.1 L49`).
- (f) A series opens for posts of registered sources and client-owned properties (amber ones per ADR-0052 and only with a first-sight `comments_count` above zero where given), for keyword finds on green routes and for Disqus sites' articles; never for an X post containing a term on the blocked-terms list x-filtered-stream screens rules with (`x-filtered-stream §5.2 L52`), the F3 table `screened_terms` of ADR-0069, marked by normalize-item on `items.normalized` (x-replies-fetcher Q7). The same screen checks every X term, live or history; refusals go to `review_queue` (`x_terms_screen`) for the account manager's recorded decision; the list is the user's (x-full-archive-search Q4). Budget order unchanged (`comment-decay-scheduler §5.1 L62`).
- By (f), keyword finds on amber routes open no series, so LinkedIn keyword finds get comments only on a client's request, as option 1 (e) had it (li-post-comments-fetcher Q4).

**From option 3**

- X keyword history: every new X keyword rule gets an automatic `keyword_history` job of 90 days, which backfill-orchestrator emits on the rule's `added` event with `reason = add` and x-full-archive-search runs at priority 5 (ADR-0018, ADR-0020, ADR-0064); a client's request still runs at priority 1. Only screened terms reach it, since a flagged keyword joins no X rule (ADR-0044, ADR-0069).
- X replies to day 30: after x-replies-fetcher's steps up to +3 d inside the recent-search window, comment-decay-scheduler continues the X series on the general steps (+7 d, then weekly until day 30, CONVENTIONS v1 L56) as `replies` jobs on `jobs.x-full-archive-search`, at priority 3 with the other later comment steps (ADR-0018). Each job carries `window_start`, the start of the previous step's read, and x-full-archive-search reads `conversation_id:<root id>` from there to the job's start (ADR-0011, ADR-0017); it keeps its `replies` kind (`x-full-archive-search §5.1 L39`).
- News history: backfill-orchestrator sends a new news site's backfill to news-sitemap-poller, which reads the site's regular sitemaps, and, for the part of the 90 days the sitemaps do not reach or for a site with none, to web-commoncrawl-scanner, which lists the host's captured article URLs from the Common Crawl index and writes them to `article.urls` with `found_via = commoncrawl` (ADR-0020, ADR-0036); the status waits for both jobs. The scanner reads the index only and never fetches a news site; news-article-extractor fetches what it lists after live finds (`news-article-extractor §5.1 L43`), through the host gate (ADR-0022).

**Budget, screen and cost**

- The budget priorities of ADR-0018 gate all of it: the automatic X history and the news history run at priority 5 and stop first as a budget fills; the X reply steps after +3 d run at priority 3.
- The X sensitive-terms screen of ADR-0069 applies to every X term, live or history, automatic or requested.
- Cost of the X history: if keyword rules found all 0.6 million X posts a month (CONVENTIONS L3), a full 90-day pass for the whole set would be about 1.8 million post reads, up to about USD 9,000 and 60% of one billing cycle's 3,000,000-read cap (CONVENTIONS L87); each rule added later brings its own 90 days. X replies after +3 d cost USD 0.005 each.

It also answers: An X `keyword_history` read, automatic or a client's, is history only: its items are stored and matched for the clients it was read for (keyword-matcher writes the hits, ADR-0031) but feed no discovery or backfill, recognised by `job_kind = backfill` (`x-full-archive-search §14 Q5`). The sensitive-events mark of (f) is set by normalize-item from ADR-0069's screened-terms list, as a boolean `sensitive_event` on `items.normalized` (`x-replies-fetcher §14 Q7`).

Why: The user chose the most history: without a client asking, a new X keyword rule starts with 90 days of past posts, an X conversation is followed for a month, and a news site starts with 90 days of articles. Green comment history stays a default, as it costs quota, not money. The budget priorities keep the history from crowding out live work, and the X screen keeps sensitive terms out of it.

## Consequences

Fuller history on X and news from the first day of a rule or a site, at a cost: up to about USD 9,000 and 60% of one month's X read cap for a full 90-day pass, and USD 0.005 per X reply after +3 d. web-commoncrawl-scanner gains a URL-listing mode; x-full-archive-search keeps its `replies` kind and serves automatic jobs as well as client requests.

- CONVENTIONS v1.1: backfill per source type (v1 L53), with the automatic X keyword history and the Common Crawl lister; the `once` fetch (v1 L61); which posts open a series, and the X row of the series table to day 30 (the addendum, v1 L255 to L271).
- F2 adds `sensitive_event` to `items.normalized`; comment-decay-scheduler reads `clients`, `news_sites` and that marker.
- The approved fb-backfill, x-recent-search, li-post-search and news-site-resolver move under ADR-0001 where their lines differ.
- `DEFERRED.md`: comment history on amber routes (option 2), after G2 with pilot costs (owner C11).

Sessions that must read this: F2, then C4, C10, C11, X1, X5, X6, N2, N3, N4, N6, N8, W3, W5, IG2, IG3, VIG2, LI2, LI3, VLI1, VLI4, VTT5, X4.
