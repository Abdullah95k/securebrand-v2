# news-article-extractor

**Platform:** News websites · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, news crawler (Python service) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The three finders (news-feed-poller, news-sitemap-poller, news-homepage-differ) only learn that an article exists. news-article-extractor is the service that reads it: it takes each URL from `article.urls`, checks that the host's policy allows the fetch, downloads the page politely, and uses trafilatura to pull out the title, author, publication time, canonical URL, language, image URLs and the body. It stores an excerpt of 200 to 300 characters with the metadata and hashes, puts the full text in a cache that expires after 7 days, and writes the article to `raw.items`. At full scale that is about 375,000 articles a month across about 500 domains.

Without it the lane produces a list of links and no content: no keyword hits on news, no sentiment, no entity or topic analysis, nothing for news-dedup to cluster and nothing for comment-decay-scheduler to schedule comments against. It is also the single place where the legal line is held: the excerpt-only storage that Iraqi copyright law (Law No. 3 of 1971) requires of us is enforced here, before anything reaches the archive.

## 2. Objective (the end state this service delivers)

Every URL on `article.urls` for a host whose policy allows it is fetched once, extracted, and written to `raw.items` as kind `article` within one finder interval of discovery; nothing is ever fetched from a host whose policy is missing, `disallowed`, `paywalled` or `blocked`; only the excerpt and metadata are persisted, with the full text gone from the cache after 7 days. Target: 95% of articles on `raw.items` within 15 minutes of `found_at` for tier 1 sites and within 60 minutes for the rest, zero full text outside the cache, zero requests that break the host's policy, zero jobs lost.

## 3. Scope

### In scope

- Consuming `article.urls`; the once-only ledger `news_urls`; policy and path checks against `crawl_policies` before every request.
- Fetching pages in the policy's access mode (direct, headless, proxy), per-host rate limiting through the shared host gate.
- trafilatura extraction, canonical URL resolution, excerpt, hashes, language hint, image URLs.
- Writing the 7-day full-text cache and `raw.items` kind `article`; `not_article`, `gone`, `paywalled` and `skipped_policy` outcomes.
- Requesting a policy re-check on every 4xx except an article-level 404 or 410.

### Out of scope

- Finding URLs (the three finders); site profiles (news-site-resolver); permissions (news-robots-checker).
- Duplicates across sites and syndicated copies (news-dedup); normalisation (normalize-item); keyword matching (keyword-matcher); analysis.
- Comments (news-comments-fetcher); downloading images or video (only image URLs are kept).

## 4. Users and consumers

- **Clients** never call it; they see articles with title, excerpt, author, time and a link back to the publisher.
- **Ops** watches extraction lag, outcome ratios per site, and the cache size.
- **Downstream:** news-dedup and normalize-item (read `raw.items`), raw-archiver (archives it), keyword-matcher and the analysis services (may read the cache within its 7 days), comment-decay-scheduler (through `items.normalized`), news-site-resolver (receives `not_article` rates for pattern refinement), source-health-canary, quota-governor, retention-purger (cache expiry).

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Every message on `article.urls` (partitioned by `source_id`). This service has no site rotation of its own: the rotation that keeps every site checked for new articles belongs to the finders (feeds every 5 to 15 minutes for hot sites and hourly for the rest, news sitemaps hourly, homepage and section diff hourly), and this service makes sure that what they find is read. Each consumer works a bounded window of its partitions, groups messages by host in memory, and runs fetches for different hosts in parallel with exactly one in flight per host; offsets are committed up to the lowest unfinished message, so a slow host never blocks others sharing the partition.

**Ordering and fairness.** Within a host, live URLs (`found_via` feed, news_sitemap, homepage_diff) are fetched before backfill URLs (`sitemap_backfill`, `commoncrawl`), and older discoveries before newer ones, so a 90-day backfill of one site cannot starve fresh articles of the same or any other site. `extraction_lag_seconds` (now minus `found_at`) is tracked per tier; when it exceeds one finder interval the service raises `extraction_behind` and the autoscaler adds workers on partition lag.

**Onboarding.** A new site reaches this service only after news-site-resolver has obtained its policy from news-robots-checker and registry-writer has written the row; its first URLs come from the finders at their next tick. A URL for a host with no unexpired policy row is not fetched: it is parked for the policy wait, and after one hour an alert fires.

**Comment decay.** Each extracted article flows `raw.items` then normalize-item then `items.normalized`, where comment-decay-scheduler opens the Disqus series for news-comments-fetcher (+6 h, +24 h, +3 d) when the site's `comments_provider` is `disqus`.

### 5.2 Step by step

1. Consume a message; compute `url_hash`; look it up in `news_urls`. Status `done` or `gone`: acknowledge and stop.
2. Read the host's `crawl_policies` row. Missing or expired: park. `crawl_allowed = false` (`disallowed`, `paywalled`, `blocked`): write ledger status `skipped_policy`, make no request, stop. Then test the URL path against the stored robots.txt rules for our user-agent group; a disallowed path is `skipped_policy` with reason `robots_path`.
3. Take a slot from the host gate and GET the page in the policy's access mode. Follow up to 5 redirects; a redirect to another host is re-checked against that host's policy first.
4. Classify the response: 2xx continue; 404 or 410 on the article is outcome `gone` (a content fact, not a policy fact); 402 is `paywalled` plus a `recheck`; other 4xx send a `recheck` job and stop the batch for the host; 429 and 5xx back off.
5. Detect a Cloudflare challenge (challenge page, `cf-mitigated: challenge`): send one `recheck`, which may set `headless` or `proxy`; never solve a CAPTCHA.
6. Extract with trafilatura (5.3). No main text or a section-like page: outcome `not_article`.
7. Resolve the canonical URL and hash it. If `news_urls` already holds that canonical hash from another URL, record both URLs, write nothing new (`duplicate_canonical`).
8. Write the full text to the cache; build the excerpt, `text_sha256` and `title_sha256`; produce `raw.items`; after Redpanda acknowledges, write the ledger row `done` with `canonical_url_hash` and `fetched_at`.

### 5.3 The call it makes

No vendor API. Plain HTTP GET, or a headless render, under the host policy. Lane-wide rules, identical in every news service:

- User agent from `CRAWLER_USER_AGENT`: `ListeningBot/1.0 (+<bot information page>; <contact mailbox>)`, naming the company and a contact address.
- Per-host politeness through the shared host gate in `listening-sdk`: concurrency 1 per host across all news services, 2 to 5 seconds between requests (or the policy's `Crawl-delay` if larger); after a 429 or 503 the spacing for that host doubles for a period set in the pilot.
- Permissions are decided by news-robots-checker: robots.txt under RFC 9309, `Content-Signal`, RSL licence files, HTTP 402 pay-per-crawl (Cloudflare, closed beta). This service reads the result and never overrides it.
- Egress follows `access_mode`: `direct`; `headless` (shared Playwright Chromium pool); `proxy` (Decodo or Oxylabs), only for Cloudflare-challenged hosts, about a quarter of Iraqi sites, which is about 94,000 articles a month. Metered under `news_proxy_egress`.

Extraction with trafilatura (`bare_extraction`, precision favoured, comments excluded, images included), reading these fields: `title`; `text` (main body); `author`; `date` (publication time; fallbacks JSON-LD `datePublished`, `article:published_time`, `<time datetime>`); canonical URL (`<link rel="canonical">`, else `og:url`, else the final URL after redirects, with tracking parameters stripped); `language`; image URLs (`og:image`, trafilatura image, in-body images, URLs only); `sitename`, `categories` and `tags` when present.

Excerpt: the first 300 characters of the cleaned body, cut back to the last whole word, never shorter than 200 characters when the body is long enough. Hashes: `text_sha256` of the normalised body, `title_sha256`, `canonical_url_hash = sha256(canonical URL)`.

Duplicates: this service enforces one fetch and one `raw.items` message per canonical URL. Syndicated copies on other sites are clustered by news-dedup using the canonical URL and a simhash of the excerpt.

Full text: written to `cache/news/<yyyy>/<mm>/<dd>/<canonical_url_hash>.json.zst` in object storage with `expires_at = fetched_at + 7 days`; retention-purger deletes expired objects and a bucket lifecycle rule is the second guard where the provider supports it. `raw.items` carries only `text_full_ref`, so raw-archiver never archives full text.

### 5.4 What it gets

Title, excerpt, author, published time, canonical URL, language, image URLs and the full text (cache only). Example payload below, in 6.2. It does not get: comments (news-comments-fetcher); video or image bytes; reliable authors or dates on sites that omit them (stored as null); content behind a paywall or a 402; the text of pages the policy forbids.

## 6. Inputs and outputs

### 6.1 Reads

`article.urls`; control-plane `crawl_policies`, `news_sites`, `sources`, `news_urls`; `crawl.policies` for policy changes; the cache for nothing (write-only).

### 6.2 Writes

`raw.items` kind `article`, one message per article, envelope plus the record. Hosts in the example are illustrative.

```json
{
  "envelope": {
    "platform": "news", "kind": "article", "route": "green", "vendor": null,
    "service": "news-article-extractor",
    "source_id": "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90",
    "platform_id": "e7a41b09c35d28f6a1d0b94c7e3f5a82d6c1b0e947f3a5d82c6b1e0a49d7f315",
    "idempotency_key": "news:article:e7a41b09c35d28f6a1d0b94c7e3f5a82d6c1b0e947f3a5d82c6b1e0a49d7f315",
    "url_key": "news:url:9b1f0c6e4a7d2358e1f6a0b3c9d47e52f81a6c3b0d5e9f274a8c1b6e3d0f5a97",
    "attempt": 1, "fetched_at": "2026-10-06T05:52:30Z",
    "retention_class": "news_excerpt",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
    "access_mode": "direct",
    "usage_signals": {"search": "yes", "ai_input": "unset", "ai_train": "no"},
    "batch": "raw/green/news/2026/10/06/news-article-extractor/000412.jsonl.zst"
  },
  "payload": {
    "url": "https://www.example-daily.iq/politics/2026/10/06/budget-session?utm_source=rss",
    "final_url": "https://www.example-daily.iq/politics/2026/10/06/budget-session",
    "canonical_url": "https://www.example-daily.iq/politics/2026/10/06/budget-session",
    "title": "البرلمان يحدد موعد جلسة الموازنة",
    "excerpt": "حدد مجلس النواب يوم الأحد المقبل موعدا لعقد جلسة مخصصة لمناقشة مشروع قانون الموازنة الاتحادية، بحسب بيان لرئاسة المجلس، وسط مطالبات من كتل نيابية بإدراج الخدمات...",
    "excerpt_chars": 247, "word_count": 412,
    "author": "فريق التحرير", "published_at": "2026-10-06T05:41:00Z",
    "language": "ar", "image_urls": ["https://www.example-daily.iq/uploads/2026/10/budget.jpg"],
    "text_full_ref": "cache/news/2026/10/06/e7a41b09c35d28f6a1d0b94c7e3f5a82d6c1b0e947f3a5d82c6b1e0a49d7f315.json.zst",
    "text_expires_at": "2026-10-13T05:52:30Z",
    "text_sha256": "5d0c9a7e1b3f4682a1c0d9e7b5f34a86c2d1e0f9a7b5c3d18e6f4a2b0c9d7e53",
    "title_sha256": "b3f60a1d9c7e4825f1a0d3c9b7e65a24d8f1c0b9a7e3d5f21c6b4a0e9d8f7c13",
    "http_status": 200, "extractor": "trafilatura", "extractor_version": "1.12.2"
  }
}
```

Also `news_urls` rows, the cache objects, `jobs.news-robots-checker` (`recheck`), outcome counts to news-site-resolver (`not_article` rate per site), `service_runs`, `dlq.news-article-extractor` after 5 failed attempts.

### 6.3 State

`news_urls` (`url_hash`, `source_id`, `url`, `found_via`, `first_seen_at`, `status` = done | gone | not_article | paywalled | skipped_policy | failed, `canonical_url_hash`, `fetched_at`), pruned after a period set in the pilot; `crawl_policies.next_slot_at`; the cache; in memory only the per-host queues and backoff state.

## 7. Limits, quotas and cost

- No external quota. Politeness bounds the rate: at 2 to 5 seconds spacing one host can absorb thousands of fetches a day, against about 25 articles a day each. Average full-scale load is about 12,500 articles a day across the lane.
- Hosting: Python containers with trafilatura plus a share of the headless pool; the whole news lane costs in the low tens of USD a month on Hetzner. Cache storage is bounded by 7 days of full text; size per article to be measured in the pilot.
- Proxy egress: only for the challenged quarter (about 94,000 articles a month), budget tag `news_proxy_egress`, price per GB to be measured in the pilot; page weight with images blocked is the key number. `news_disqus` belongs to news-comments-fetcher.
- Legal basis: excerpts of 200 to 300 characters plus metadata and hashes are stored under Iraqi copyright law (Law No. 3 of 1971); full text lives only in the 7-day cache (retention class `news_excerpt`); robots.txt, Content Signals, RSL and 402 are honoured through the policy; no full text enters `raw.items`.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts to `dlq.news-article-extractor` and an alert; `Retry-After` honoured.
- 401, 402, 403, 451 and other 4xx: `recheck` job to news-robots-checker, stop the host's batch, no retry through another IP or user agent. Article-level 404 or 410: ledger `gone`, counted, no re-check.
- 5xx and timeouts: backoff as above; after 5 attempts the URL goes to the DLQ.
- Cloudflare challenge: one `recheck`; an interactive challenge means `blocked`.
- Extraction empty or not an article: ledger `not_article`; the rate per site is reported to the resolver.
- Partial write: the ledger row is written only after Redpanda acknowledges; a replay finds no `done` row and re-emits the same `idempotency_key`, which normalize-item stores once.
- Cache write failure: the article is not emitted until the cache write succeeds.

## 9. Non-functional requirements

- Throughput: about 12,500 articles a day average at full scale (375,000 a month); bursts when a backfill starts are absorbed by per-host spacing and worker count.
- Latency: see the objective; per-fetch time is dominated by the host gate.
- Idempotency: `news:article:<canonical_url_hash>`; replayable; one `raw.items` message per canonical URL.
- Scaling: stateless Python workers on partition lag.
- Security: no cookies or logins; proxy credentials from the vault per job; no full text in logs; provenance on every message.

## 10. Metrics and alerts

Standard set: `items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `staleness_seconds_p95`, `cost_units_total`, `quota_denied_total`, `dlq_total`; plus `extract_outcome_total{outcome}`, `extraction_lag_seconds{tier}`, `host_slot_wait_seconds`, `excerpt_chars` histogram, `cache_objects` and `cache_bytes`, `cloudflare_challenge_total`. Alerts: `extraction_behind`, `dlq_nonempty`, `not_article_rate_high`, `policy_wait_over_1h`, `cache_overdue` (objects older than 7 days). SLO: extraction lag as in section 2.

## 11. Dependencies

`listening-sdk`, news-feed-poller, news-sitemap-poller, news-homepage-differ, news-site-resolver, news-robots-checker, news-dedup, normalize-item, raw-archiver, retention-purger, source-health-canary, quota-governor, Supabase Postgres, Redpanda, object storage, the shared headless pool, Decodo or Oxylabs keys in the vault.

## 12. Risks and mitigations

- Law No. 3 of 1971 and full-text use: excerpt-only persistence, 7-day expiry, hashes; counsel review before launch.
- trafilatura fails on unusual templates: `not_article` and low-excerpt-length rates per site trigger resolver refresh; extraction code versioned in the payload as `extractor` and `extractor_version` (ADR-0070).
- Cloudflare challenges: the challenged quarter costs proxy bytes; only `proxy` hosts use egress.
- Publishers object to crawling: the user agent names the company and a contact address; a disallowed host is dropped at once.

## 13. Acceptance criteria

1. For a host whose policy is `disallowed`, `paywalled`, `blocked`, missing or expired, the service makes zero requests to it (request-log test); the ledger shows `skipped_policy` or the URL is parked.
2. A URL whose path is disallowed by the host's robots.txt group for our user agent is never fetched.
3. A fixture article yields title, author, published time, canonical URL, language and image URLs; the excerpt is between 200 and 300 characters, cut at a word boundary.
4. `raw.items` never contains the full text; the cache object exists, `text_full_ref` points to it, and an object older than 7 days is deleted by retention-purger.
5. Two URLs with the same canonical URL produce one `raw.items` message and one ledger entry per URL; replaying one message yields one stored article after normalize-item.
6. Requests to one host never overlap and are spaced 2 to 5 seconds apart (or the `Crawl-delay`) across all news services; a slow host does not delay messages for another host in the same partition.
7. A 404 on an article gives `gone` and no re-check; a 403 gives one `recheck` job and no retry from another IP or user agent; a 402 gives `paywalled`.
8. A section page returns outcome `not_article` and increments the site's rate.
9. A Cloudflare challenge fixture triggers one `recheck`; a CAPTCHA fixture ends in `blocked` with no solving attempt.
10. The ledger row is written only after Redpanda acknowledges; a produce failure leaves it absent and the retry re-emits.
11. With a backfill and live URLs queued for one host, live URLs are fetched first.

## 14. Open questions

1. May keyword-matcher and the analysis services read the 7-day cache and persist only derived values (hit offsets, scores)? Proposed: yes, otherwise a brand named after the first 300 characters is missed; to be confirmed with counsel on Law No. 3 of 1971.
2. How an `ai-input = no` Content Signal affects analysis of the excerpt: carried in `usage_signals`; the rule is to be decided with news-robots-checker and the analysis services.
3. Does the 7-day cache live under this service (proposed, with `text_full_ref` in the payload) or under a key written by normalize-item? normalize-item's open question 2 asks the same.
4. Retention period of `news_urls` rows: to be set in the pilot.
