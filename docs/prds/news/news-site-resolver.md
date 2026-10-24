# news-site-resolver

**Platform:** News · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend lead, news lane (Node) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The news lane watches about 500 Iraqi and regional domains publishing about 25 articles a day each. A domain is only useful to the pollers once somebody has established where its articles are announced (RSS, Atom or Turbo RSS feeds, a news sitemap, or only the homepage), whether a plain HTTP client can reach it or a Cloudflare challenge stands in the way, whether it runs Disqus, how fast it publishes, and whether it is Iraqi at all. Without it every poller would guess those facts on every run, the qualifier would have nothing to decide on, and onboarding would be a manual ticket. The product would lose its ability to grow the news registry from what search-hit-router, web-commoncrawl-scanner, web-gdelt-poller and client seed lists already surface, and the guarantee the green route rests on: no host is fetched before news-robots-checker has issued a crawl policy for it.

## 2. Objective (the end state this service delivers)

End state: every candidate domain is resolved by one job into a site profile (the fields in 5.4) and handed to the qualifier as a `poster.profiles` message; an accepted site is on rotation at the pollers' next scheduler tick. Targets: 99% of candidates resolved within one hour of queueing; 100% of content fetches in the lane preceded by a `crawl.policies` row for the host; every registered site re-resolved every 30 days; zero duplicate registry rows per canonical host.

## 3. Scope

### In scope

- Candidate intake from search-hit-router, web-commoncrawl-scanner, web-gdelt-poller, client seed lists and ops (n8n flow).
- Host canonicalisation: `www` versus apex, `http` to `https`, redirect chains, mirrors as aliases.
- Feed, news sitemap and sitemap index discovery; article URL pattern inference; the homepage-diff decision.
- Comment provider detection: Disqus shortname and identifier scheme (the Meta Comments plugin, discontinued 10 Feb 2026, is recorded as `none`).
- Access mode (direct, headless, proxy, blocked) from the policy issued by news-robots-checker.
- Iraqi signals, language share, tier proposal; re-resolution of registered sites.

### Out of scope

- Fetching articles (news-article-extractor), polling (news-feed-poller, news-sitemap-poller, news-homepage-differ), issuing the policy (news-robots-checker), the decision (qualifier), writing `sources` (registry-writer).
- An outlet's social accounts; the per-platform resolvers handle those.
- Login-only or paywalled sites: recorded as `blocked`, never worked around.

## 4. Users and consumers

qualifier (consumes `poster.profiles`; news domains always qualify by type, the Iraqi signals decide accept, review or reject); registry-writer (materialises the `sources` row and the `news_sites` profile); the three pollers, news-article-extractor, news-comments-fetcher and comment-decay-scheduler (read the profile); source-health-canary (expected publishing rate); backfill-orchestrator (90-day backfill on accept); ops and Abdullah (review cards, registry UI).

## 5. How it works

### 5.1 Trigger and rotation

- Trigger: jobs on `jobs.news-site-resolver`, `kind: resolve` (new host) or `kind: refresh` (registered site), produced by search-hit-router, web-commoncrawl-scanner, web-gdelt-poller, the seed-list flow and the qualifier.
- Dedup: a host already in `sources` becomes a refresh; a host in the 180-day rejected memory (`decisions`) is dropped without a fetch.
- Rotation: every registered site is refreshed every 30 days, and at once when source-health-canary flips it to `degraded` or a poller reports a feed or sitemap 404 or 410.
- Onboarding contract: (1) canonicalise the host without touching the site (DNS and TLS only); (2) enqueue `jobs.news-robots-checker` and wait for the host's `crawl.policies` message, or read an unexpired `crawl_policies` row; (3) only with `crawl_allowed = true` fetch the homepage and feed candidates in the policy's access mode; (4) emit `poster.profiles`; (5) the qualifier decides, registry-writer writes the row and emits `source.events` `added`, backfill-orchestrator schedules the last 90 days through news-sitemap-poller (or web-commoncrawl-scanner where there is no sitemap); (6) the pollers pick the site up at their next tick: feeds every 5 to 15 minutes for hot sites and hourly for the rest, sitemaps hourly, homepage diff hourly for sites without feeds, and for Disqus sites comments on the short series (+6 h, +24 h, +3 d, extended every 2 days to day 30 while a thread still grows; ADR-0061).

### 5.2 Step by step

1. Read the job, normalise the URL to a host, check `sources` and the rejected memory.
2. Request the policy. If its status is `disallowed`, `paywalled` or `blocked`, emit a profile with `crawl_allowed: false` so the site is registered with `health = blocked` and never polled; finish.
3. Fetch the homepage. Parse `<title>`, `og:site_name`, `<link rel="alternate">` of type `application/rss+xml` or `application/atom+xml`, `<link rel="canonical">`, `<html lang>`, JSON-LD `NewsMediaOrganization`, the Disqus embed (`<shortname>.disqus.com/embed.js` and the `disqus_config` identifier template), and internal links.
4. Validate declared feeds, then probe the list in 5.3 within the probe budget. A feed counts only if it parses as RSS 2.0, Atom or Turbo RSS with at least one linked item; record URL, format, item count, date range, and whether items carry `content:encoded` or `turbo:content`.
5. Discover sitemaps from the policy's `Sitemap:` lines and the probe paths; classify each as news sitemap (`news:` namespace), regular sitemap or index; record entry counts and newest `lastmod`.
6. Infer one to three article URL patterns from feed and sitemap URLs (date segments, numeric ids, section slugs), with homepage links as hold-out to measure precision.
7. Estimate the publishing rate as items per day over the dates the feeds and news sitemap expose; record `last_article_at`.
8. Compute Iraqi signals: `.iq` domain; a +964 number on contact, about or footer areas; an Iraqi city or governorate in the masthead or address; language share from lang-dialect-id over the last 20 titles; seed-list membership. News prose is mostly Modern Standard Arabic, so the 40% dialect signal rarely fires; domain, phone, city and seed list carry most sites.
9. Propose a tier: 1 (hot) if on a client priority list or publishing above the hot threshold (to be measured in the pilot); 2 if daily; 3 if less often.
10. Emit `poster.profiles`; write `news_sites` with `status: candidate`.
11. On refresh, repeat 3 to 9, diff against the stored profile, and send changes to registry-writer, which emits `source.events` `updated`.

### 5.3 The call it makes

No vendor API. HTTP GETs under the host policy: user agent from `CRAWLER_USER_AGENT`, format `ListeningBot/1.0 (+<bot information page>; <contact mailbox>)`, identical across all news services so robots.txt groups match; per-host concurrency 1; 2 to 5 seconds between requests, or the policy's `Crawl-delay` if larger; `If-None-Match` and `If-Modified-Since` on any URL seen before; a probe budget per resolution (set in the pilot).

Feed paths, tried after declared feeds: `/feed`, `/feed/`, `/rss`, `/rss/`, `/rss.xml`, `/feed.xml`, `/atom.xml`, `/index.xml`, `/?feed=rss2`, `/feeds/posts/default`, `/rssturbo`, `/rss/turbo`, `/turbo`, `/ar/rss`, `/ar/feed`, then `/<section>/feed` and `/category/<section>/feed` for sections linked from the homepage. Turbo RSS is accepted when the `turbo:` or `yandex:` namespace is present.

Sitemap paths: `/sitemap-news.xml`, `/news-sitemap.xml`, `/sitemap_news.xml`, `/sitemap.xml`, `/sitemap_index.xml`, `/sitemap-index.xml`, plus the policy's `Sitemap:` lines. A news sitemap follows Google's rules: articles from the last two days only, at most 1,000 URLs per file, larger sites splitting through an index.

Headless fetch (the shared Playwright Chromium pool, same user agent, no CAPTCHA solving) only when the policy says `headless` or `proxy`; Decodo or Oxylabs egress only for `proxy` hosts, the Cloudflare-challenged quarter.

### 5.4 What it gets

Site identity, feeds with format and freshness, sitemaps with type and size, URL patterns with precision, comment provider and shortname, access mode, publishing rate, `last_article_at`, country signals, language share, tier proposal. It does not get article bodies (sampled titles are discarded), social handles, traffic figures, or reliable dates from sites that omit them. A site with no feed, sitemap or inferable pattern is marked `homepage_diff: true`.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.news-site-resolver`; `crawl.policies` and `crawl_policies`; `sources`; `decisions`; `clients` and `client_sources` (seed and priority lists); `news_sites`.

### 6.2 Writes

`poster.profiles`, `jobs.news-robots-checker`, `news_sites`, `service_runs`. Hosts in the example are illustrative.

```json
{
  "schema": "poster.profiles/v1",
  "kind": "site",
  "platform": "news",
  "host": "www.example-daily.iq",
  "proposed_source": {
    "platform": "news", "source_type": "site",
    "platform_id": "example-daily.iq", "handle": "example-daily.iq",
    "url": "https://www.example-daily.iq/", "display_name": "Example Daily",
    "route": "green", "vendor": null, "retention_class": "news_excerpt", "followers": null,
    "country_signals": {"tld_iq": true, "phone_964": true, "iraqi_place": "Baghdad", "seed_list": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]},
    "lang_share": {"msa": 0.90, "iraqi_ar": 0.05, "en": 0.05},
    "proposed_tier": 1, "added_by": "qualifier"
  },
  "site_profile": {
    "feeds": [{"url": "https://www.example-daily.iq/feed", "format": "rss2", "items": 50, "newest_at": "2026-10-06T08:41:00+03:00", "has_body": false}],
    "news_sitemap": "https://www.example-daily.iq/sitemap-news.xml",
    "sitemaps": ["https://www.example-daily.iq/sitemap_index.xml"],
    "homepage_diff": false,
    "article_url_patterns": ["^https://www\\.example-daily\\.iq/[a-z-]+/\\d{4}/\\d{2}/\\d{2}/[^/?#]+$"],
    "comments_provider": "disqus", "disqus_shortname": "exampledaily",
    "access_mode": "direct", "articles_per_day_estimate": 31,
    "last_article_at": "2026-10-06T08:41:00+03:00"
  },
  "discovered_by": "search-hit-router",
  "service": "news-site-resolver", "job_id": "01M486K7W0KPR5FKH5ET9K2SFS",
  "resolved_at": "2026-10-06T08:52:40Z"
}
```

Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

registry-writer maps `proposed_source` onto the `sources` row, inserting it under the `proposed_source_id` this service allocated with the candidate row (`tier` from the qualifier, `health = ok`, `backfill_status` at its default, `pending`). `site_profile` stays in `news_sites`, which only this service writes, keyed by that `source_id` (ADR-0040, ADR-0020).

### 6.3 State

`news_sites` (one row per host: the profile plus `status`, `resolved_at`, `profile_version`); job `attempt`; `service_runs`. No cursors: every resolution re-reads the site's discovery surface.

## 7. Limits, quotas and cost

- No external quota. Cost is politeness: a resolution is a few to a few dozen requests 2 to 5 seconds apart; 500 sites at onboarding plus one refresh per site per 30 days is negligible against the lane's 375,000 article fetches a month.
- Hosting: shares the news lane's nodes in the cluster; the lane as a whole costs in the low tens of USD a month on Hetzner.
- Proxy egress: only for `proxy` hosts (the challenged quarter), a handful of requests per site per month, metered by quota-governor under `budget_tag = news_proxy_egress`; price per GB to be measured in the pilot.
- Legal basis: the resolver stores site metadata and feed, sitemap and pattern facts only; robots.txt, Content Signals, RSL and HTTP 402 are honoured through the policy; nothing is fetched before the policy exists. Excerpts of 200 to 300 characters under Iraqi copyright law (Law No. 3 of 1971) and the 7-day full-text cache are the extractor's concern; this service stores no article text.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts to `dlq.news-site-resolver` with an alert.
- HTTP 401 or 403 without a challenge marker: `access_mode: blocked`, profile emitted with `crawl_allowed: false`, no retry through another IP or user agent.
- Cloudflare challenge on the homepage: one re-evaluation by news-robots-checker (which may set `headless` or `proxy`); an interactive CAPTCHA means `blocked`.
- Timeouts and DNS failures: same backoff; after 5 attempts the candidate is parked in `review_queue`.
- Policy wait beyond one hour: requeue; never fetch without a policy.

## 9. Non-functional requirements

- Throughput: hosts resolve in parallel (never within one host), each in about two minutes of wall time.
- Idempotency: the job key is the canonical host; a replay produces the same profile and one `news_sites` row.
- Scaling on `jobs.news-site-resolver` depth; one leader instance owns the 30-day refresh ticker.
- Security: no site credentials, no account pools, no CAPTCHA solving; proxy and headless credentials from Supabase Vault.
- `/healthz`, `/metrics`, structured JSON logs with `job_id`, `source_id`, `route`, `vendor`.

## 10. Metrics and alerts

`jobs_total{status,kind}`, `resolver_duration_seconds`, `resolver_policy_wait_seconds`, `resolver_feeds_found_total`, `resolver_access_mode_total{mode}`, `resolver_signals_total{count}`, `dlq_total`. Alerts: any DLQ entry; policy wait p95 above 10 minutes; challenged share materially above the expected quarter (threshold set in the pilot); refresh ticker idle for more than a day.

## 11. Dependencies

news-robots-checker, qualifier, registry-writer, lang-dialect-id, search-hit-router, web-commoncrawl-scanner, web-gdelt-poller, backfill-orchestrator, source-health-canary, quota-governor, `listening-sdk`, Supabase Postgres (`news_sites`, `crawl_policies`, `sources`), the shared headless pool, Decodo or Oxylabs keys in the vault.

## 12. Risks and mitigations

- Feeds that lie (truncated, section-only, stale): the publishing rate is cross-checked against the news sitemap.
- CMS migrations move feeds silently: 30-day refresh plus canary-triggered refresh within the hour.
- Challenges hide sites that robots.txt allows: headless mode, never CAPTCHA solving; sites that stay interactive are `blocked`.
- Regional outlets fail the two-signal test: seed-list membership counts as a signal; one signal goes to review with the 24-hour default reject.
- Wrong URL patterns make news-homepage-differ emit non-article links: news-article-extractor's `not_article` outcome feeds pattern refinement.

## 13. Acceptance criteria

1. For a host with no `crawl_policies` row, the lane's first request is `GET /robots.txt` by news-robots-checker; the resolver makes none before `crawl.policies` arrives (request-log test).
2. A site declaring an RSS feed with `<link rel="alternate">` is resolved with that feed; a site with only a valid `/feed` is resolved by probe; a Turbo RSS feed at `/rssturbo` is recognised.
3. A site publishing `sitemap-news.xml` gets `news_sitemap` set; one with only `sitemap_index.xml` gets it under `sitemaps`.
4. A page embedding Disqus yields `comments_provider: disqus` with the shortname; a page without yields `none`.
5. A homepage answered with a Cloudflare challenge is never recorded as `direct`; an interactive challenge is recorded as `blocked`.
6. A `.iq` site with a +964 number produces two signals and an accept; a regional `.net` site with only an Iraqi city mention produces one signal and a review card.
7. A job for a registered host runs the refresh path, creates no second `news_sites` row, and a replay leaves `profile_version` unchanged.
8. A moved feed (old URL 404, new URL declared) is detected on the canary-triggered refresh within one hour and yields a `source.events` `updated` event.
9. No two requests to one host are closer than 2 seconds and none are concurrent, over a full onboarding run.

## 14. Open questions

1. The product token in `CRAWLER_USER_AGENT` is provisional (`ListeningBot`) until the venture's name is fixed; the contact mailbox follows.
2. Does `news_sites` stay a control-plane table or fold into `sources.notes` as jsonb?
3. The hot-tier publishing-rate threshold: to be measured in the pilot.
4. Regional outlets: accept by default when on a client seed list, or always through review?
