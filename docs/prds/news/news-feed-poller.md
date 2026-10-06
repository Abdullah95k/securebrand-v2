# news-feed-poller

**Platform:** News websites · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, news crawler · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

News is the one stream in the product where the publisher itself offers a machine-readable list of what is new: the RSS, Atom or rssturbo feed. news-feed-poller reads those feeds for every registered Iraqi and regional news site and turns each new entry into a URL on `article.urls`, the cheapest and most polite way to learn that an article exists. At full scale the lane carries about 375,000 articles a month across about 500 domains, roughly 25 articles a day per domain, and a feed is the first place most of them appear.

Without it the product hears about an article only from the slower surfaces (the hourly news sitemap, the hourly homepage diff, the monthly Common Crawl scan), so a ministry statement or a brand crisis would reach a client up to an hour late, and hot sites would be served no faster than the quietest ones. The freshness promise for news, every registered site checked for new articles on a rotation, is kept or broken first here.

## 2. Objective (the end state this service delivers)

Every registered site that has a usable feed is polled on its cadence (every 5 to 15 minutes for hot sites, hourly for the rest), and every new entry reaches `article.urls` within one interval of the site publishing it, without a single request that the host's policy forbids. Target: rotation lag below one interval for 99% of sites per day, a new feed entry on `article.urls` within 15 minutes of publication on tier 1 sites and within 60 minutes on the rest, zero jobs lost.

## 3. Scope

### In scope

- Rotation of every site whose `news_sites.feeds` is not empty, by tier, with a leader-elected scheduler and jobs on `jobs.news-feed-poller`.
- Conditional GETs (ETag, If-Modified-Since) of RSS 2.0, Atom and Turbo RSS (rssturbo) feeds, parsing entries, normalising URLs, emitting `article.urls`.
- Reporting feed breakage (404, 410, malformed, empty) to news-site-resolver as a refresh request.
- Requesting a policy re-check from news-robots-checker on every 4xx.

### Out of scope

- Finding feeds and classifying sites (news-site-resolver); permissions (news-robots-checker); news sitemaps (news-sitemap-poller); homepage diff (news-homepage-differ).
- Fetching article pages and extraction (news-article-extractor); comments (news-comments-fetcher); duplicates across sites (news-dedup).
- Using feed bodies (`content:encoded`, `turbo:content`) as article text: the extractor fetches the page, so that the canonical URL, language and image URLs come from one place.

## 4. Users and consumers

- **Clients** never call it; they experience "an article from an outlet I watch shows up within minutes".
- **Ops** watches rotation lag, the list of sites with broken feeds, and can force a poll of one site.
- **Downstream:** news-article-extractor (consumes `article.urls`), news-site-resolver (receives refresh requests), news-robots-checker (receives re-check jobs), source-health-canary (expected publishing rate), quota-governor, raw-archiver (feed snapshots are not archived; only extracted articles are).

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.news-feed-poller`, partitioned by `source_id`, emitted by the rotation scheduler inside this service: one leader replica elected through a Postgres advisory lock, scan period set by an environment variable well inside the shortest interval of 5 minutes. The scheduler selects `sources` rows with `platform = news`, `health != blocked`, `tier != retired`, a non-empty `news_sites.feeds`, a `crawl_policies` row with `crawl_allowed = true` that has not expired, and `next_poll_at <= now()`.

**Cadence.** Tier 1 (hot: on a client's priority list or above the publishing-rate threshold set in the pilot): every 5 to 15 minutes, chosen per site from its `articles_per_day_estimate` (the mapping is set in the pilot). Tiers 2 and 3: every 60 minutes. Dormant sites (no article in 30 days): weekly; a new entry promotes the site back through `source.events`. Retired: never polled.

**Every site stays on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + interval`), so cadence is fixed and does not drift with fetch time. Jobs are ordered by `next_poll_at` then by tier, so an overdue hourly site is not pushed aside by hot sites and no site is skipped twice in a row. A site is in at most one job at a time (partition key). A failed job keeps its old `next_poll_at`, making that site the first candidate on the next scan. Sites with several feeds (main plus sections) are polled in one job, one feed after another through the host gate.

**Catch-up.** `rotation_lag_seconds` is now minus `next_poll_at` of the most overdue site. Above one interval the scheduler switches to most-stale-first ordering and raises `rotation_behind`. A late poll still sees everything the feed still holds, so being behind costs freshness, not completeness, except on a very hot site whose feed has scrolled past unread entries; those gaps are closed by news-sitemap-poller's hourly pass.

**Onboarding a new site.** news-site-resolver canonicalises the host, asks news-robots-checker for the host's policy and fetches nothing until `crawl.policies` arrives; the qualifier accepts, registry-writer writes the `sources` row and the `news_sites` profile and emits `source.events` `added`; backfill-orchestrator schedules the 90-day backfill through news-sitemap-poller or web-commoncrawl-scanner. This scheduler does not wait for the backfill: the site's first feed poll runs at the next scheduler tick after `added`.

### 5.2 Step by step

1. Consume a job (`source_id`, `tier`, `attempt`, `kind` = rotation | ops_force); read the `sources`, `news_sites` and `crawl_policies` rows and the `cursors` row for (`source_id`, `news-feed-poller`); stop if the policy is missing, expired or not `allowed`.
2. For each feed URL, take a slot from the host gate (section 5.3), send the conditional GET in the policy's access mode.
3. On 304: record the poll and move on. On 200: parse the feed; for each entry take `link` (or `guid` when it is a permalink, or the Atom `rel="alternate"` href), `published`, `title`.
4. Normalise each URL: lowercase scheme and host, drop the fragment, strip tracking parameters (`utm_*`, `fbclid`, `gclid`), sort remaining parameters, resolve against the feed URL.
5. Drop entries whose URL is already in `news_urls` (read-only check by `url_hash`) or does not match the site's `article_url_patterns` when patterns exist; duplicates that slip through are harmless, the extractor's ledger is the final guard.
6. Write one `article.urls` message per new URL; wait for Redpanda acknowledgement.
7. After acknowledgement: store ETag, Last-Modified, newest `published` and a hash of the feed's first 50 entry URLs in the cursor; set `last_polled_at`, `next_poll_at`, `consecutive_errors = 0`.
8. Record metrics; on an empty or malformed feed, 404 or 410, send `jobs.news-site-resolver` a `refresh`.

### 5.3 The call it makes

No vendor API. Plain HTTP GETs under the host policy. Lane-wide rules, identical in every news service:

- User agent from `CRAWLER_USER_AGENT`: `ListeningBot/1.0 (+<bot information page>; <contact mailbox>)`, naming the company and a contact address.
- Per-host politeness through the shared host gate in `listening-sdk`: concurrency 1 per host across all news services, 2 to 5 seconds between requests (or the policy's `Crawl-delay` if larger), slot state in `crawl_policies.next_slot_at`.
- The host's permissions come from news-robots-checker (robots.txt under RFC 9309, `Content-Signal`, RSL licence files, HTTP 402); this service reads the result and never evaluates robots.txt itself.
- Egress follows the policy's `access_mode`: `direct`; `headless` (shared Playwright pool); `proxy` (Decodo or Oxylabs) only for Cloudflare-challenged hosts, about a quarter of Iraqi sites. No CAPTCHA solving; a feed behind an interactive challenge is `blocked`.

Conditional request: `If-None-Match: <stored ETag>` and `If-Modified-Since: <stored Last-Modified>`; a 304 costs a few hundred bytes, which is what keeps proxy egress small. Formats accepted: RSS 2.0, Atom, Turbo RSS (recognised by the `turbo:` or `yandex:` namespace). Feeds are read from `news_sites.feeds`, never guessed here. When a feed breaks, news-site-resolver re-discovers it by probing, in order: `/feed`, `/feed/`, `/rss`, `/rss/`, `/rss.xml`, `/feed.xml`, `/atom.xml`, `/index.xml`, `/?feed=rss2`, `/feeds/posts/default`, `/rssturbo`, `/rss/turbo`, `/turbo`, `/ar/rss`, `/ar/feed`, then `/<section>/feed` for sections linked from the homepage.

### 5.4 What it gets

Per entry: URL, title, `published` (RSS `pubDate`, Atom `published` or `updated`), optional `category`, optional `dc:creator`, and sometimes `content:encoded` or `turbo:content`. Example entry reduced to what is kept:

```json
{"link": "https://www.example-daily.iq/politics/2026/10/06/budget-session",
 "title": "البرلمان يحدد موعد جلسة الموازنة",
 "published": "2026-10-06T08:41:00+03:00"}
```

It does not get: the article text (title only is kept; the body is discarded here), the canonical URL, language or images (the extractor), comments, or entries a feed has already scrolled past.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.news-feed-poller`; control-plane `sources`, `news_sites`, `crawl_policies`, `cursors`, `news_urls` (read-only); `source.events` (`added`, `updated`, `tier change`, `retired`) to refresh its view of the rotation; `crawl.policies` for policy changes between scans.

### 6.2 Writes

`article.urls`, one message per new URL, partitioned by `source_id`. Hosts in the example are illustrative.

```json
{
  "envelope": {
    "platform": "news", "kind": "article_url", "route": "green", "vendor": null,
    "service": "news-feed-poller",
    "source_id": "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90",
    "url_key": "news:url:9b1f0c6e4a7d2358e1f6a0b3c9d47e52f81a6c3b0d5e9f274a8c1b6e3d0f5a97",
    "job_id": "01J9N3A4K8R2T7V5X0M6C1D9HE", "attempt": 1,
    "found_at": "2026-10-06T05:47:12Z", "found_via": "feed",
    "retention_class": "news_excerpt",
    "access_mode": "direct"
  },
  "payload": {
    "url": "https://www.example-daily.iq/politics/2026/10/06/budget-session",
    "title": "البرلمان يحدد موعد جلسة الموازنة",
    "published_at": "2026-10-06T05:41:00Z",
    "feed_url": "https://www.example-daily.iq/feed", "feed_format": "rss2"
  }
}
```

Also: `jobs.news-site-resolver` (`refresh`), `jobs.news-robots-checker` (`recheck`), `source.events` (`tier change`), `service_runs`, `dlq.news-feed-poller` after 5 failed attempts.

### 6.3 State

`cursors.cursor` per (`source_id`, `news-feed-poller`): a JSON map from feed URL to `{etag, last_modified, newest_published_at, first50_hash}`, plus `last_success_at`, `last_error`, `consecutive_errors`. `sources.last_polled_at`, `next_poll_at`, `health`. `crawl_policies.next_slot_at` (host gate). In memory only the leader lock and backoff state.

## 7. Limits, quotas and cost

- No external quota. The cost is politeness: at a 5-minute interval a hot site takes at most 288 feed requests a day, most of them 304s, against a host gate that admits thousands a day at 2 to 5 seconds spacing.
- Hosting: a few small stateless containers in the cluster; the whole news lane costs in the low tens of USD a month on Hetzner.
- Proxy egress: only for `proxy` hosts, the Cloudflare-challenged quarter; metered by quota-governor under `budget_tag = news_proxy_egress`; price per GB to be measured in the pilot. `news_disqus` belongs to news-comments-fetcher and is not used here.
- Volume: about 375,000 articles a month across about 500 domains at about 25 articles a day each; the feed poller emits URLs for the share of them that appear in feeds.
- Legal basis: this service stores only URLs, titles and timestamps. Excerpts of 200 to 300 characters plus metadata and hashes under Iraqi copyright law (Law No. 3 of 1971), and full text only in a 7-day cache (retention class `news_excerpt`), are the extractor's concern. robots.txt and signals are honoured through the policy.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.news-feed-poller` and an alert fires. `Retry-After` is honoured when larger.
- HTTP 401, 402, 403, 451 and any other 4xx: stop the batch for that host, send a `recheck` job to news-robots-checker, never retry through another IP or user agent. A 404 or 410 on a feed URL is sent to news-site-resolver as a `refresh`.
- Feed returns 200 with no entries from a site known to publish (an "empty 200"): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`; the site stays covered by news-sitemap-poller or news-homepage-differ.
- Malformed XML: parsed leniently once; if still unreadable, `refresh` request and the site's other surfaces carry it.
- Partial write: cursors move only after Redpanda acknowledges; a replayed job re-emits the same URLs and the extractor's ledger drops them.
- Policy expired or missing: the job is requeued; never fetch without a policy.

## 9. Non-functional requirements

- Throughput: about 500 sites; at most 288 feed requests a day per hot site; the URL volume is bounded by the lane's 375,000 articles a month, far below any single-partition limit.
- Latency: an entry published on a tier 1 site reaches `article.urls` within its interval plus fetch time.
- Idempotency: `url_key = news:url:<sha256 of normalised URL>`; replayable jobs; the extractor's `news_urls` ledger makes the fetch once-only.
- Scaling: stateless workers on partition lag; one leader scheduler.
- Security: credentials only for proxy egress, from the vault per job, never logged; no account pools; provenance on every message.

## 10. Metrics and alerts

`items_fetched_total` (entries read), `items_new_total` (URLs emitted), `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total` (proxy bytes), `quota_denied_total`, `dlq_total`, plus `feed_not_modified_total`, `feed_error_total{code}`, `sites_in_rotation{tier}`. Alerts: `rotation_behind`, `dlq_nonempty`, `empty_200_rate` (above 5% in 15 minutes), `feed_broken_sites`, `recheck_storm`. SLO: rotation lag below one interval for 99% of sites per day.

## 11. Dependencies

`listening-sdk` (host gate, adapter contract), news-site-resolver, news-robots-checker, news-article-extractor, news-sitemap-poller, news-homepage-differ, source-health-canary, quota-governor, registry-writer, backfill-orchestrator, raw-archiver, Supabase Postgres, Redpanda, the shared headless pool, Decodo or Oxylabs keys in the vault.

## 12. Risks and mitigations

- Feeds truncate or lag behind the site: the hourly news sitemap and homepage diff provide a second surface; source-health-canary compares expected and observed publishing rate.
- A feed carries non-article items (ads, live blogs): `article_url_patterns` filter them; the extractor's `not_article` outcome feeds pattern refinement.
- Cloudflare-challenged feeds cost proxy bytes: conditional requests and 5-to-15-minute intervals only for tier 1; byte price to be measured in the pilot.
- Shared politeness slows a host when five services want it: the gate orders requests by due time, and the lane's real demand is a few hundred requests a day per host.

## 13. Acceptance criteria

1. A tier 1 site whose poll started at 09:00:00 with a 10-minute interval has `next_poll_at = 09:10:00` even when the fetch took 40 seconds.
2. With 100 fixture sites across tiers against simulated hosts for 24 hours, no site's `rotation_lag_seconds` exceeds its interval and no site is skipped twice in a row.
3. A second poll sends `If-None-Match` and `If-Modified-Since` from the first response; a 304 emits no messages and still advances `next_poll_at`.
4. An RSS 2.0 feed, an Atom feed and a Turbo RSS feed each yield the expected `article.urls` messages from fixtures.
5. Replaying one job twice yields no second fetch downstream: the extractor stores one article.
6. The cursor does not advance when the Redpanda produce fails; the next attempt re-emits.
7. A host with no unexpired `crawl_policies` row, or `crawl_allowed = false`, receives zero requests from this service (request-log test).
8. Any 4xx from a host produces one `recheck` job and no retry from another IP or user agent; a feed 404 produces a resolver `refresh`.
9. With the poller delayed past one interval, the scheduler orders by most stale first and `rotation_behind` fires.
10. Tracking parameters are stripped and the same article from two feeds yields one `url_key`.
11. Requests to one host never overlap and are spaced 2 to 5 seconds apart (or the `Crawl-delay`) across all news services in a concurrent test.

## 14. Open questions

1. The mapping from `articles_per_day_estimate` to a 5, 10 or 15-minute interval for hot sites: to be measured in the pilot.
2. Should hot sites' feeds also be read through WebSub (PubSubHubbub) hubs where a site declares one, replacing polling? Proposed: yes, as a later optimisation once the pilot shows which Iraqi hosts declare a hub.
3. Whether entries with `published` far in the past (re-surfaced old articles) should be emitted. Proposed: emit, and let news-dedup and the extractor ledger absorb them.
