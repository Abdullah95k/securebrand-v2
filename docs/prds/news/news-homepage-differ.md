# news-homepage-differ

**Platform:** News websites · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, news crawler · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Not every Iraqi news site publishes a feed or a sitemap. Many are small provincial outlets, party or ministry sites and blogs-turned-newspapers running on a template that exposes neither. They are still sources a client cares about: a governorate council's site may be the only place a decision is announced. news-homepage-differ covers exactly those sites. Every hour it reads the homepage and the main section pages, compares the article links with what it saw last time, and writes each link that is new to `article.urls`.

Without it, a site with no feed and no sitemap would be registered and never checked, which breaks the product's promise that every registered site is re-checked for new articles on a rotation. The only trace of such a site would be the monthly Common Crawl scan, up to a month late and incomplete.

## 2. Objective (the end state this service delivers)

Every registered site flagged `homepage_diff = true` is read hourly (homepage plus section pages), every article link that appears on those pages reaches `article.urls` within one hour of appearing, a headless browser is used only on sites whose policy or markup requires it, and no request is made that the host's policy forbids. Target: rotation lag below one hour for 99% of sites per day, at least 95% of emitted links accepted as articles by news-article-extractor (the rest refine the URL patterns), zero jobs lost.

## 3. Scope

### In scope

- Hourly rotation of every site with `news_sites.homepage_diff = true`.
- Fetching the homepage and section pages, extracting article-candidate links, diffing against stored link hashes, emitting `article.urls`.
- Deciding per site, from evidence, whether plain HTTP is enough or the page needs the shared headless browser.
- Reporting layout changes and low-precision patterns to news-site-resolver; reporting any 4xx to news-robots-checker.

### Out of scope

- Finding feeds, sitemaps and URL patterns, and setting `homepage_diff` (news-site-resolver); permissions (news-robots-checker).
- Feeds (news-feed-poller) and sitemaps (news-sitemap-poller): a site that gains either leaves this service's rotation after the resolver's next refresh.
- Fetching article pages and extraction (news-article-extractor).
- Storing page HTML: only link hashes and counts are kept.

## 4. Users and consumers

- **Clients** never call it; they see articles from small outlets that no other service could see.
- **Ops** watches rotation lag, headless usage, and the sites with the lowest link precision; can pin section pages for a site.
- **Downstream:** news-article-extractor (consumes `article.urls`, returns `not_article` outcomes), news-site-resolver (refresh requests), news-robots-checker (re-checks), source-health-canary, quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.news-homepage-differ`, partitioned by `source_id`, emitted by the rotation scheduler inside this service: one leader replica elected through a Postgres advisory lock, scan period set by an environment variable well inside one hour. The scheduler selects `sources` rows with `platform = news`, `health != blocked`, `tier != retired`, `news_sites.homepage_diff = true`, an unexpired `crawl_policies` row with `crawl_allowed = true`, and `next_poll_at <= now()`.

**Cadence.** Every 60 minutes for every tier (homepage and section diff are hourly by design: a diff is the most expensive surface, so it is never run more often). Dormant sites (no article in 30 days): weekly; a new link promotes the site back. Retired: never polled.

**Every site stays on rotation.** `next_poll_at` is set from the START of the last poll (`poll_started_at + 60 minutes`), so cadence is fixed and does not drift with the number of section pages or a slow headless render. Jobs are ordered by `next_poll_at` then by tier, so no site is skipped twice in a row, and a site is in at most one job at a time. A failed job keeps its old `next_poll_at`. A site is also a candidate for every other finder if it gains a feed or sitemap: the resolver's refresh flips `homepage_diff` off and this service drops it.

**Catch-up.** `rotation_lag_seconds` is now minus `next_poll_at` of the most overdue site. Above one hour the scheduler orders most-stale-first and raises `rotation_behind`. A homepage shows only the newest articles, so a late poll can miss those that scrolled off; the loss is counted as `diff_gap_suspected` when the new-link count equals the page's full link count.

**Onboarding a new site.** news-site-resolver canonicalises the host, obtains the policy from news-robots-checker before any fetch, decides `homepage_diff = true` because it found no feed and no sitemap, and proposes URL patterns when it can; the qualifier accepts; registry-writer emits `source.events` `added`; this scheduler polls the site at the next tick. The first poll is a baseline: every article-pattern link on the page is emitted with `baseline = true`, because those links are recent articles.

### 5.2 Step by step

1. Consume a job (`source_id`, `kind` = rotation | ops_force, `attempt`); read the `sources`, `news_sites`, `crawl_policies` and `cursors` rows; stop if the policy is missing, expired or not `allowed`.
2. Build the page list: the homepage plus section pages from the cursor (discovered from the homepage's navigation links and pinned by ops), capped by a per-site setting chosen in the pilot.
3. For each page, take a slot from the host gate and fetch it in the policy's access mode (plain GET, or the headless pool when `render = headless`).
4. Extract candidate links: anchors inside `<main>`, `<article>` or headline containers (`h1` to `h3`), same host, normalised.
5. Keep links matching `article_url_patterns`; where the site has no patterns, apply the heuristics in 5.3.
6. Diff: hash each link (`url_hash`), drop those in the stored `link_hashes` of the last three snapshots and those in `news_urls`; emit the rest to `article.urls`, then wait for acknowledgement.
7. Store the new hash set, ETag and Last-Modified, `render` mode and section list in the cursor; set `last_polled_at`, `next_poll_at`.
8. Record metrics; if the link count dropped to zero or doubled against the median, raise `layout_changed` and send news-site-resolver a `refresh`.

### 5.3 The call it makes

No vendor API. Plain HTTP GETs, or a headless render, under the host policy. Lane-wide rules, identical in every news service:

- User agent from `CRAWLER_USER_AGENT`: `ListeningBot/1.0 (+<bot information page>; <contact mailbox>)`, naming the company and a contact address.
- Per-host politeness through the shared host gate in `listening-sdk`: concurrency 1 per host across all news services, 2 to 5 seconds between requests (or the policy's `Crawl-delay` if larger). A homepage plus ten sections is eleven requests, about one minute of a host's hour.
- Permissions come from news-robots-checker (robots.txt under RFC 9309, `Content-Signal`, RSL licence files, HTTP 402); this service reads the result only. A section page that robots.txt disallows is dropped from the page list.
- Egress follows the policy's `access_mode`: `direct`; `headless`; or `proxy` (Decodo or Oxylabs), only for Cloudflare-challenged hosts, about a quarter of Iraqi sites. No CAPTCHA solving; an interactive challenge means `blocked`.

Conditional GET: `If-None-Match` and `If-Modified-Since` where the page returns validators; a 304 is a completed fetch. Many dynamic homepages return none, so a body hash equal to the stored one is also treated as unchanged.

Headless only where needed. A site starts with plain HTTP. It switches to `render = headless` when (a) the policy says `access_mode = headless` or `proxy`, or (b) the plain response contains fewer article-pattern links than a floor set in the pilot and carries a script-app marker (`<div id="root">`, `__NEXT_DATA__`, `window.__NUXT__`), and it switches back when a plain response again yields links. The shared Playwright Chromium pool uses the same user agent, waits for network idle with a timeout, blocks images, fonts, media and third-party scripts (which keeps proxy bytes low; saving to be measured in the pilot), and keeps no cookies between jobs.

Heuristics for sites without patterns (thresholds set in the pilot): same-host link, path with at least two segments or a numeric id or a date segment, anchor text long enough to be a headline, and not under `/tag/`, `/category/`, `/author/`, `/page/`, `/search`, `/about`, `/contact`.

### 5.4 What it gets

Per link: normalised URL, anchor text (kept only as a hint, discarded after the diff), the page it was found on and its rank on the page. Example:

```json
{"url": "https://www.example-council.iq/news/20261006-session-decision",
 "anchor": "قرار مجلس المحافظة بشأن المشاريع",
 "section_url": "https://www.example-council.iq/news/", "rank": 3}
```

It does not get publication time (the extractor reads it from the page), author, language, canonical URL, article text or images, nor articles that scrolled off the page between polls.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.news-homepage-differ`; control-plane `sources`, `news_sites`, `crawl_policies`, `cursors`, `news_urls` (read-only); `source.events`; `crawl.policies`; `article.urls` outcomes only through the resolver's pattern refreshes.

### 6.2 Writes

`article.urls`, one message per new link, partitioned by `source_id`. Hosts in the example are illustrative.

```json
{
  "envelope": {
    "platform": "news", "kind": "article_url", "route": "green", "vendor": null,
    "service": "news-homepage-differ",
    "source_id": "a82e1c47-5d3b-49f0-8e6a-2c9b7d1f0e35",
    "url_key": "news:url:c15d8e02a7f94b36d0e1a58c3b7f2946e80d1a5c7b3f96e204d8a1c5b7e3f092",
    "job_id": "01J9N3F1V6S4B9Y2D7K0Q8T5NA", "attempt": 1,
    "found_at": "2026-10-06T07:03:51Z", "found_via": "homepage_diff",
    "retention_class": "news_excerpt", "access_mode": "headless"
  },
  "payload": {
    "url": "https://www.example-council.iq/news/20261006-session-decision",
    "published_at": null, "baseline": false,
    "section_url": "https://www.example-council.iq/news/", "rank": 3
  }
}
```

Also `jobs.news-site-resolver` (`refresh`), `jobs.news-robots-checker` (`recheck`), `service_runs`, `dlq.news-homepage-differ`.

### 6.3 State

`cursors.cursor` per (`source_id`, `news-homepage-differ`): JSON `{etag, last_modified, page_hash, link_hashes (last three snapshots), sections, render}`; `last_success_at`, `last_error`, `consecutive_errors`. `sources.last_polled_at`, `next_poll_at`, `health`. Host-gate slots live in `host_gate`, written only by the SDK gate (ADR-0040). No page HTML is stored.

## 7. Limits, quotas and cost

- No external quota. Cost is politeness and compute: one request an hour for the homepage plus one per section; headless renders cost more CPU and are bounded by the pool's concurrency. The share of Iraqi sites needing this service is to be measured in the pilot.
- Hosting: a few small containers plus a share of the headless pool; the whole news lane costs in the low tens of USD a month on Hetzner.
- Proxy egress: only for `proxy` hosts (the Cloudflare-challenged quarter), metered under `budget_tag = news_proxy_egress`; headless pages are the largest per-request byte cost, which is why images, fonts and media are blocked; price per GB to be measured in the pilot.
- Volume: about 375,000 articles a month across about 500 domains at about 25 articles a day each; the share found by diff is small.
- Legal basis: link hashes and counts only. Excerpts of 200 to 300 characters plus metadata and hashes under Iraqi copyright law (Law No. 3 of 1971), full text only in a 7-day cache (`news_excerpt`), are the extractor's concern; robots.txt and signals are honoured through the policy. `news_disqus` belongs to news-comments-fetcher.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts to `dlq.news-homepage-differ` with an alert.
- Any 4xx other than 404 and 410, including 401, 402 and 403: stop the batch, send a `recheck` job to news-robots-checker, no retry through another IP or user agent. A homepage 404 or 410 sends news-site-resolver a `refresh`.
- Empty 200 or a page with zero article links from a site known to publish: counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`.
- Headless timeout: one retry, then the poll is recorded as failed and the site keeps its `next_poll_at`.
- Partial write: cursors move only after Redpanda acknowledges; a replay re-emits, the extractor's ledger drops duplicates.
- Policy missing or expired: requeue; never fetch without a policy.

## 9. Non-functional requirements

- Throughput: bounded by the number of diff sites, one homepage and a few sections an hour each; headless renders limited by pool size.
- Latency: a link appearing on a page reaches `article.urls` within 60 minutes plus fetch time.
- Idempotency: `url_key = news:url:<sha256 of normalised URL>`; replayable jobs.
- Scaling: stateless workers on partition lag; one leader scheduler; the headless pool scales separately.
- Security: proxy credentials from the vault per job, never logged; no cookies kept; no account pools; provenance on every message.

## 10. Metrics and alerts

Standard set: `items_fetched_total` (links read), `items_new_total` (links emitted), `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`; plus `links_per_page`, `headless_renders_total`, `not_article_ratio`, `layout_changed_total`. Alerts: `rotation_behind`, `dlq_nonempty`, `layout_changed`, `diff_precision_low` (below 95% accepted), `empty_200_rate`. SLO: rotation lag below one hour for 99% of sites per day.

## 11. Dependencies

`listening-sdk`, news-site-resolver, news-robots-checker, news-article-extractor, news-feed-poller, news-sitemap-poller, source-health-canary, quota-governor, registry-writer, the shared Playwright Chromium pool, Supabase Postgres, Redpanda, Decodo or Oxylabs keys in the vault.

## 12. Risks and mitigations

- Non-article links (menus, ads, tag pages) reach the extractor: patterns and heuristics filter; `not_article` outcomes feed the resolver's pattern refinement; `diff_precision_low` alerts at 95%.
- Template redesigns break link extraction: `layout_changed` raises a resolver refresh the same hour.
- Headless load grows with the challenged share: headless only where needed, images and scripts blocked, pool concurrency capped.
- Articles scroll off between polls: the hourly cadence is the floor; a busy site that needs more should have a feed, which the resolver keeps probing for.

## 13. Acceptance criteria

1. A site whose poll started at 09:00:00 has `next_poll_at = 10:00:00` even when five section pages took four minutes.
2. With 100 fixture sites for 24 hours, no site's `rotation_lag_seconds` exceeds one hour and none is skipped twice in a row.
3. On a fixture homepage with 30 links of which 12 match the patterns, the first poll emits 12 messages with `baseline = true`; a second identical poll emits none; adding one article link emits exactly one.
4. A link seen in the last three snapshots, or present in `news_urls`, is never emitted again.
5. A fixture JavaScript-rendered page yields zero links over plain HTTP and the expected links after the site switches to `render = headless`; a plain server-rendered page never uses the headless pool.
6. A host with a missing, expired or disallowing policy receives zero requests; a section page disallowed by robots.txt is never fetched.
7. A page whose link count falls to zero raises `layout_changed` and sends a resolver `refresh`.
8. Any 4xx other than 404 and 410 produces one `recheck` job and no retry through another IP or user agent.
9. Requests to one host across all news services never overlap and are spaced 2 to 5 seconds apart (or the `Crawl-delay`).
10. The cursor does not advance when the produce fails; the next attempt re-emits.

## 14. Open questions

1. The link-count floor that triggers the headless switch, the per-site section cap and the anchor-length threshold: to be measured in the pilot.
2. How many Iraqi sites truly lack both feed and sitemap, and what share of them are behind a Cloudflare challenge: to be confirmed in the pilot.
3. Should ops be able to pin a section page per site from the review card? Proposed: yes, stored in the cursor's `sections`.
