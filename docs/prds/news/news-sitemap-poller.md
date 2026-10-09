# news-sitemap-poller

**Platform:** News websites · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, news crawler · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Most Iraqi news sites that care about Google News publish a news sitemap, `sitemap-news.xml`: a short, machine-readable list of the articles published in the last two days, each with its title, language and publication time. news-sitemap-poller reads that file every hour for every site that has one, and writes each new article URL to `article.urls`. It is the second surface for finding articles, independent of the feed, and the only one that is complete by design: a feed shows what the site chose to syndicate, while the news sitemap shows what the site told Google it published.

Without it, a site with a sitemap but no feed is invisible until the monthly Common Crawl scan; a busy site whose feed scrolls past unread entries between polls loses articles for good; and the 90-day backfill of a newly added site has no source of old URLs except the coarse Common Crawl index. The product's promise that every registered site is checked for new articles on a rotation would rest on feeds alone.

## 2. Objective (the end state this service delivers)

Every registered site with a news sitemap is read once an hour, every article it lists reaches `article.urls` within one hour of appearing in the file, every newly accepted site gets its last 90 days of URLs from its regular sitemaps where they reach that far, and no request is made that the host's policy forbids. Target: rotation lag below one hour for 99% of sites per day, 100% of URLs in a sitemap emitted at least once, zero jobs lost.

## 3. Scope

### In scope

- Hourly rotation of every site with `news_sites.news_sitemap` set; reading the sitemap, or the sitemap index and its child news sitemaps.
- Hourly rotation, through the regular sitemap index and its `lastmod` values, of sites that have no feed and no news sitemap but do have a regular sitemap (otherwise no finder would cover them).
- Backfill jobs (`kind: backfill`) from backfill-orchestrator: reading regular sitemaps for URLs dated in the last 90 days.
- Conditional requests, gzip sitemaps, Google news-sitemap parsing, URL normalisation, emitting `article.urls`.
- Reporting 404 or 410 on a sitemap URL to news-site-resolver and any other 4xx to news-robots-checker.

### Out of scope

- Finding sitemaps and deciding which is the news sitemap (news-site-resolver); permissions (news-robots-checker).
- Feeds (news-feed-poller); homepage diff (news-homepage-differ); articles for sites with neither feed nor sitemap nor pattern are covered there.
- Fetching article pages (news-article-extractor); backfill through Common Crawl where a site has no usable sitemap (web-commoncrawl-scanner).

## 4. Users and consumers

- **Clients** never call it; they see articles from outlets they watch, including from sites that publish no feed.
- **Ops** watches rotation lag, the sitemap-error list and the backfill coverage report.
- **Downstream:** news-article-extractor (consumes `article.urls`), backfill-orchestrator (receives `coverage_days` and the done signal), news-site-resolver (refresh requests), news-robots-checker (re-checks), source-health-canary, quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Jobs on `jobs.news-sitemap-poller`, partitioned by `source_id`. Rotation jobs come from the scheduler inside this service: one leader replica elected through a Postgres advisory lock, scan period set by an environment variable well inside one hour. Backfill jobs come only from backfill-orchestrator. The scheduler selects `sources` rows with `platform = news`, `health != blocked`, `tier != retired`, a sitemap surface in `news_sites` (news sitemap, or regular sitemap when the site has no feed and no news sitemap), an unexpired `crawl_policies` row with `crawl_allowed = true`, and `next_poll_at <= now()`.

**Cadence.** News sitemaps: every 60 minutes for every tier. Regular-sitemap-only sites: every 60 minutes. Dormant sites (no article in 30 days): weekly. Retired: never polled. A news sitemap holds only the last two days, so an hourly pass reads every article about 48 times, which is what makes the file safe to read with a single missed poll.

**Every site stays on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + 60 minutes`), so cadence is fixed and does not drift. Jobs are ordered by `next_poll_at` then by tier, so an overdue tier 3 site is not pushed aside by tier 1 sites and no site is skipped twice in a row. A site is in at most one job at a time. A failed job keeps its old `next_poll_at` and is first in line on the next scan. Sites with a news sitemap that also have a feed are polled by both services; the overlap is intentional and harmless.

**Catch-up.** `rotation_lag_seconds` is now minus `next_poll_at` of the most overdue site. Above one interval the scheduler orders most-stale-first and raises `rotation_behind`. Because a news sitemap holds two days, the service can fall behind by up to 48 hours without losing an article; beyond that the gap is only recoverable through the regular sitemap's `lastmod`, which a catch-up job reads automatically when the stored cursor is older than two days.

**Onboarding a new site.** news-site-resolver canonicalises the host, asks news-robots-checker for the policy and fetches nothing until `crawl.policies` arrives; the qualifier accepts and registry-writer emits `source.events` `added`. This scheduler picks the site up at the next tick for the hourly pass; backfill-orchestrator sends one `backfill` job in parallel, and both share the host gate, so the first request still follows the policy and never exceeds the per-host limit.

**Backfill.** A `backfill` job reads the regular sitemap index, selects child sitemaps whose `lastmod` falls within 90 days, and emits URLs whose `lastmod` (or `news:publication_date` where present) is within 90 days with `found_via = sitemap_backfill`. It reports `coverage_days` (how far back the sitemaps reach). If coverage is under 90 days, backfill-orchestrator sets `backfill_status = capped` and asks web-commoncrawl-scanner for the remainder.

### 5.2 Step by step

1. Consume a job (`source_id`, `kind` = rotation | backfill | ops_force, `attempt`); read the `sources`, `news_sites`, `crawl_policies` and `cursors` rows; stop if the policy is missing, expired or not `allowed`.
2. Take a slot from the host gate and send the conditional GET for the news sitemap in the policy's access mode; follow a sitemap index to its child news sitemaps.
3. On 304: record and finish. On 200: decompress if gzip; parse `<url>` elements.
4. For each URL take `<loc>`, `<news:publication_date>`, `<news:title>`, `<news:publication><news:language>`; for regular sitemaps take `<loc>` and `<lastmod>`.
5. Normalise (lowercase scheme and host, drop fragment, strip `utm_*`, `fbclid`, `gclid`, sort parameters) and compute `url_hash`.
6. Skip URLs already in `news_urls` (read-only) and URLs failing the site's `article_url_patterns`; emit the rest to `article.urls`; wait for acknowledgement.
7. Advance the cursor and `next_poll_at`; on backfill, report `coverage_days` and completion.
8. Record metrics; route errors as in section 8.

### 5.3 The call it makes

No vendor API. Plain HTTP GETs under the host policy. Lane-wide rules, identical in every news service:

- User agent from `CRAWLER_USER_AGENT`: `ListeningBot/1.0 (+<bot information page>; <contact mailbox>)`, naming the company and a contact address.
- Per-host politeness through the shared host gate in `listening-sdk`: concurrency 1 per host across all news services, 2 to 5 seconds between requests (or the policy's `Crawl-delay` if larger).
- Permissions come from news-robots-checker (robots.txt under RFC 9309, `Content-Signal`, RSL licence files, HTTP 402); this service reads the result only.
- Egress follows the policy's `access_mode`: `direct`; `headless`; or `proxy` (Decodo or Oxylabs), only for Cloudflare-challenged hosts, about a quarter of Iraqi sites. No CAPTCHA solving.

Sitemap URLs come from `news_sites`. For re-discovery the resolver tries `/sitemap-news.xml`, `/news-sitemap.xml`, `/sitemap_news.xml`, `/sitemap.xml`, `/sitemap_index.xml`, `/sitemap-index.xml` and the `Sitemap:` lines of robots.txt.

Google news-sitemap rules applied: root `<urlset>` with the `news` namespace (`http://www.google.com/schemas/sitemap-news/0.9`); each `<url>` carries `<news:news>` with `<news:publication>` (`<news:name>`, `<news:language>`), `<news:publication_date>` (W3C format) and `<news:title>`; only articles from the last two days; at most 1,000 URLs per file, larger sites splitting through a sitemap index. The generic sitemap protocol limits (50,000 URLs and 50 MB uncompressed per file) apply to regular sitemaps. A file listing more than 1,000 news URLs or articles older than two days is accepted but counted as `sitemap_rule_violation`.

Conditional request: `If-None-Match` and `If-Modified-Since` from the stored ETag and Last-Modified; a 304 is a completed poll. A response whose body hash equals the stored `urls_hash` is treated like a 304.

### 5.4 What it gets

Per URL: location, title, publication time, language and publication name (news sitemaps); location and `lastmod` (regular sitemaps). Example entry:

```xml
<url>
  <loc>https://www.example-daily.iq/economy/2026/10/06/oil-exports</loc>
  <news:news>
    <news:publication><news:name>Example Daily</news:name><news:language>ar</news:language></news:publication>
    <news:publication_date>2026-10-06T09:05:00+03:00</news:publication_date>
    <news:title>ارتفاع صادرات النفط في أيلول</news:title>
  </news:news>
</url>
```

It does not get article text, canonical URL, author or images (the extractor), comments, or any article older than two days from a news sitemap. Publication dates in sitemaps are the site's claim; they are not verified here.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.news-sitemap-poller`; control-plane `sources`, `news_sites`, `crawl_policies`, `cursors`, `news_urls` (read-only); `source.events`; `crawl.policies`.

### 6.2 Writes

`article.urls`, one message per new URL, partitioned by `source_id`. Hosts in the example are illustrative.

```json
{
  "envelope": {
    "platform": "news", "kind": "article_url", "route": "green", "vendor": null,
    "service": "news-sitemap-poller",
    "source_id": "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90",
    "url_key": "news:url:4e0a7d91c3b2f685a1d0e9c7b3f46a25d8e1c0b97f3a5d2e6c8b1a04f7d93e60",
    "job_id": "01J9N3C7P2M5Q8W1Z4T0B6F3JD", "attempt": 1,
    "found_at": "2026-10-06T06:10:03Z", "found_via": "news_sitemap",
    "retention_class": "news_excerpt", "access_mode": "direct"
  },
  "payload": {
    "url": "https://www.example-daily.iq/economy/2026/10/06/oil-exports",
    "title": "ارتفاع صادرات النفط في أيلول",
    "published_at": "2026-10-06T06:05:00Z", "language": "ar",
    "publication_name": "Example Daily",
    "sitemap_url": "https://www.example-daily.iq/sitemap-news.xml"
  }
}
```

Also `jobs.news-site-resolver` (`refresh`), `jobs.news-robots-checker` (`recheck`), a backfill report to backfill-orchestrator (`coverage_days`, `urls_emitted`), `service_runs`, `dlq.news-sitemap-poller`.

### 6.3 State

`cursors.cursor` per (`source_id`, `news-sitemap-poller`): JSON map from sitemap URL to `{etag, last_modified, newest_date, urls_hash}`; `last_success_at`, `last_error`, `consecutive_errors`. `sources.last_polled_at`, `next_poll_at`, `health`, `backfill_status` (read). Host-gate slots live in `host_gate`, written only by the SDK gate (ADR-0040).

## 7. Limits, quotas and cost

- No external quota. A news sitemap is one request an hour per site, usually a 304 or a small file; about 500 sites make about 12,000 requests a day for the whole lane before overlap with feeds.
- Hosting: a few small stateless containers; the whole news lane costs in the low tens of USD a month on Hetzner.
- Proxy egress: only for `proxy` hosts (the Cloudflare-challenged quarter), metered under `budget_tag = news_proxy_egress`; price per GB to be measured in the pilot. Backfill reads of large regular sitemaps are the main byte cost and are throttled by quota-governor on that tag.
- Volume: about 375,000 articles a month across about 500 domains at about 25 articles a day each.
- Legal basis: URLs, titles and dates only; excerpts of 200 to 300 characters plus metadata and hashes under Iraqi copyright law (Law No. 3 of 1971), full text only in a 7-day cache (`news_excerpt`), are the extractor's concern; robots.txt and signals are honoured through the policy. `news_disqus` belongs to news-comments-fetcher.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts to `dlq.news-sitemap-poller` with an alert.
- Any 4xx other than 404 and 410: stop the batch for the host and send a `recheck` job to news-robots-checker; no retry through another IP or user agent. A 404 or 410 on a sitemap URL sends news-site-resolver a `refresh`.
- Empty 200 (a sitemap with no URLs from a site that publishes): counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`.
- Malformed XML or truncated gzip: one retry, then `refresh` request; feeds and the homepage diff keep covering the site.
- Partial write: the cursor moves only after Redpanda acknowledges; a replay re-emits, the extractor's ledger drops duplicates.
- Policy missing or expired: requeue; never fetch without a policy.

## 9. Non-functional requirements

- Throughput: about 500 sites, one hourly request each plus child sitemaps; backfill adds a bounded burst per new site shared through the host gate.
- Latency: an article listed in a news sitemap reaches `article.urls` within 60 minutes plus fetch time.
- Idempotency: `url_key = news:url:<sha256 of normalised URL>`; replayable jobs.
- Scaling: stateless workers on partition lag; one leader scheduler.
- Security: proxy credentials from the vault per job, never logged; no account pools; provenance on every message.

## 10. Metrics and alerts

Standard set: `items_fetched_total` (URLs read), `items_new_total` (URLs emitted), `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`; plus `sitemap_not_modified_total`, `sitemap_rule_violation_total`, `backfill_coverage_days`, `sites_in_rotation{kind}`. Alerts: `rotation_behind`, `dlq_nonempty`, `empty_200_rate`, `sitemap_broken_sites`, `backfill_short`. SLO: rotation lag below one hour for 99% of sites per day.

## 11. Dependencies

`listening-sdk`, news-site-resolver, news-robots-checker, news-article-extractor, news-feed-poller, news-homepage-differ, backfill-orchestrator, web-commoncrawl-scanner, source-health-canary, quota-governor, registry-writer, Supabase Postgres, Redpanda, the shared headless pool, Decodo or Oxylabs keys in the vault.

## 12. Risks and mitigations

- Sites publish stale or wrong `publication_date`: kept as a claim; the extractor records the page's own date and news-dedup uses first-seen time when they disagree.
- Large regular sitemaps (tens of thousands of URLs) make backfill heavy: only child sitemaps with a recent `lastmod` are read, and bytes are metered.
- Sitemaps that list non-articles: `article_url_patterns` filter them; `not_article` outcomes refine patterns.
- Two services read the same host: the shared host gate bounds total load.

## 13. Acceptance criteria

1. A site whose poll started at 09:00:00 has `next_poll_at = 10:00:00` even when the fetch took 90 seconds.
2. With 100 fixture sites against simulated hosts for 24 hours, no site's `rotation_lag_seconds` exceeds one hour and none is skipped twice in a row.
3. A fixture news sitemap with 40 URLs yields 40 `article.urls` messages on the first poll and zero on an identical second poll; the second request carries `If-None-Match` and `If-Modified-Since`.
4. A sitemap index with two child news sitemaps is followed and both are read.
5. A gzip sitemap is decompressed; a truncated gzip is retried once, then a `refresh` is sent.
6. A site with no feed and no news sitemap but a regular sitemap is polled hourly and only URLs with `lastmod` newer than the cursor are emitted.
7. A backfill job emits only URLs dated within 90 days, reports `coverage_days`, and a 60-day sitemap leads to `capped`.
8. A host with a missing, expired or disallowing policy receives zero requests (request-log test).
9. Any 4xx other than 404 and 410 produces one `recheck` job; a 404 on the sitemap produces a `refresh`.
10. The cursor does not advance when the produce fails; the next attempt re-emits.
11. A file with 1,500 news URLs is accepted and counted as `sitemap_rule_violation`.

## 14. Open questions

1. Should regular-sitemap-only sites be polled here (proposed) or by news-homepage-differ? Proposed: here, because `lastmod` ordering is cheaper and more complete than a diff.
2. How many Iraqi sites publish a news sitemap, and how many regular sitemaps carry reliable `lastmod`: to be confirmed in the pilot.
3. Whether the backfill should also use `news:publication_date` older than the two-day rule on sites that keep a long news sitemap: to be confirmed in the pilot.
