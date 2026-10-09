# news-robots-checker

**Platform:** News websites · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend lead, news crawler · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The news lane is green only because it obeys the publishers. A site tells crawlers what it allows in several places: robots.txt (RFC 9309), the `Content-Signal` directive that Cloudflare's managed robots.txt adds, an RSL licence file, and, on hosts in Cloudflare's closed pay-per-crawl beta, an HTTP 402 answer that asks for money. news-robots-checker is the one service that reads all of them. It turns them into a single per-host policy, caches it, refreshes it daily, re-checks it whenever any service gets a 4xx from the host, and publishes it on `crawl.policies`. Every other news service reads that policy before it sends a request.

Without it the lane has two bad options: fetch without looking, which exposes the company to legal and reputational harm and breaks the product's second hard constraint (no route that rests on a breach of terms), or fetch nothing. It also decides how each host may be reached (direct, headless, or through Decodo or Oxylabs egress), which is what keeps proxy spend limited to the Cloudflare-challenged quarter of Iraqi sites.

## 2. Objective (the end state this service delivers)

Every registered news host has an unexpired policy row before its first non-policy request, the row is refreshed daily and re-checked on every 4xx, and a host whose policy is `disallowed`, `paywalled` or `blocked` is never fetched by any service. Target: 100% of content requests in the lane preceded by an unexpired `crawl_policies` row; no policy older than 24 hours in use for 99% of hosts per day; first policy for a new host within 15 minutes for 99% of hosts; re-check answered within 15 minutes for 99% of requests.

## 3. Scope

### In scope

- Jobs on `jobs.news-robots-checker`: `first_check` (from news-site-resolver), `refresh` (own daily scheduler), `recheck` (from any news service after a 4xx), `ops_force`.
- Fetching and parsing robots.txt per RFC 9309; selecting our user-agent group; compiling allow and disallow rules; `Crawl-delay` and `Sitemap:` lines.
- `Content-Signal` values (robots.txt directive and response header), RSL licence discovery and parsing, HTTP 402 detection.
- Detecting a Cloudflare challenge and choosing the access mode (`direct`, `headless`, `proxy`, `blocked`).
- Writing `crawl_policies` and `crawl.policies`.

### Out of scope

- Finding feeds, sitemaps and sites (news-site-resolver); fetching articles (news-article-extractor); evaluating a single article URL against the rules (each fetching service does that with the rules stored here).
- Negotiating licences, paying for crawl, joining Cloudflare's beta: a human decision.
- Solving CAPTCHAs, rotating user agents or IPs to get around a refusal: never built.

## 4. Users and consumers

- **Clients** never see it; they see a provenance statement that the news route obeys robots.txt, signals, RSL and 402.
- **Ops** watches policy age, hosts by status and access mode, and can force a re-check.
- **Downstream:** news-site-resolver (waits for the first policy), news-feed-poller, news-sitemap-poller, news-homepage-differ, news-article-extractor and news-comments-fetcher (read `crawl_policies` before every request), registry-writer (maps `crawl_allowed = false` onto `sources.health = blocked`), quota-governor (proxy egress), source-health-canary, raw-archiver.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Jobs on `jobs.news-robots-checker`, partitioned by `source_id` (by host for a candidate not yet in the registry). `recheck` and `first_check` jobs jump ahead of `refresh` jobs. Refresh jobs come from the scheduler inside this service: one leader replica elected through a Postgres advisory lock, scan period set by an environment variable well inside the shortest lane interval of 5 minutes.

**Cadence.** Every registered host is refreshed daily. RFC 9309 asks crawlers not to use a cached robots.txt for more than 24 hours, so `expires_at = checked_at + 24 hours` and the scheduler targets a refresh margin set in the pilot (the aim is that no policy ever reaches expiry in use). Dormant and retired sites are refreshed weekly and never, but a dormant site's policy is re-checked before its first poll after promotion.

**Every host stays on rotation.** `next_refresh_at` is set from the START of the last check, so cadence is fixed and does not drift. Jobs are ordered by `next_refresh_at` then by tier, so no host is skipped twice in a row. If the lag exceeds the margin the scheduler orders most-stale-first and raises `rotation_behind`; services that find an expired policy hold the host rather than fetch.

**Re-check on every 4xx.** Any news service that receives a 4xx from a host (401, 402, 403, 429, 451, and a 404 or 410 on a feed or sitemap URL) sends `recheck` and stops its batch for that host. The only exception is a 404 or 410 on an individual article URL, which is a missing article, not a changed policy. A per-host cooldown set in the pilot coalesces a burst of 4xx into one re-check.

**Onboarding a new site.** news-site-resolver canonicalises the host with DNS and TLS only, enqueues `first_check`, and waits for the `crawl.policies` message or an unexpired row. Only with `crawl_allowed = true` does the resolver fetch the homepage; the pollers and the extractor start after registry-writer emits `source.events` `added`. Nothing but robots.txt, the RSL file and the homepage probe described below touches the host before the policy exists.

### 5.2 Step by step

1. Consume a job (`host`, `kind`, `attempt`, `requested_by`); read the current `crawl_policies` row.
2. Take a slot from the host gate and GET `https://<host>/robots.txt` with the lane user agent.
3. Interpret the response as RFC 9309 requires: 2xx parse; 3xx follow up to five redirects; 4xx means no rules are published; 5xx or network failure means the file is unreachable. A 401 or 403 on robots.txt, with no challenge marker, is treated as a refusal: `blocked`.
4. Select the group: the longest matching user-agent product token (`ListeningBot`, provisional), case-insensitive, else `*`. Compile rules (`Allow`, `Disallow`, `*`, `$`; the most specific path wins and `Allow` wins ties); read `Crawl-delay`, `Sitemap:` lines, `Content-Signal` and `License:` lines.
5. Read `Content-Signal` values from robots.txt and from the robots.txt and homepage response headers.
6. Discover an RSL file (`License:` line, `<link rel="license" type="application/rsl+xml">` on the homepage, or a `Link` header); fetch and parse it.
7. Probe the homepage once to detect a 402 and a Cloudflare challenge; choose the access mode (5.3).
8. Compute `status`, `crawl_allowed`, `access_mode`, `crawl_delay_seconds`, `usage_signals`, `policy_version` (incremented on any change) and `changed_fields`.
9. Upsert `crawl_policies`; on first check or any change, produce `crawl.policies`; on `crawl_allowed` flipping, registry-writer updates `sources.health`.

### 5.3 The call it makes

No vendor API. Plain HTTP GETs. Lane-wide rules, identical in every news service:

- User agent from `CRAWLER_USER_AGENT`: `ListeningBot/1.0 (+<bot information page>; <contact mailbox>)`, naming the company and a contact address; the product token must match what publishers see in their logs.
- Per-host politeness through the shared host gate: concurrency 1 per host across all news services, 2 to 5 seconds between requests (or the `Crawl-delay` if larger).
- Egress by `access_mode`, never to override a refusal.

**robots.txt (RFC 9309).** Parse at least the first 500 KiB; ignore the rest. 4xx: `robots_status = unavailable`, no restrictions published. 5xx or network failure on a refresh: keep the last known rules for a limit set in the pilot and retry with backoff; with no previous rules the host is `disallowed`, reason `robots_unreachable`. The compiled rules are stored in the row so the extractor can test each article path without refetching.

**`Content-Signal`.** Values for `search`, `ai-input` and `ai-train` (yes, no, unset) from the robots.txt directive or the response header, stored as `search`, `ai_input` and `ai_train` (each hyphen becomes an underscore; ADR-0070). Our proposed handling: `search = no` makes the host `disallowed` (reason `content_signal_search_no`), because the product indexes excerpts for search; `ai-train` and `ai-input` are recorded and copied to every article as `usage_signals`; the product trains no model on news. The share of Iraqi hosts that set signals: to be confirmed in the pilot.

**RSL.** An RSL licence file's permits, prohibits and payment elements are stored as `rsl` (URL, permitted and prohibited usages, payment type and amount). A licence that prohibits our use makes the host `disallowed`; one that requires payment makes it `paywalled`; one that permits our use is recorded and honoured. Mapping of RSL usage categories to our use, and how many Iraqi hosts publish RSL: to be confirmed in the pilot.

**HTTP 402 (pay-per-crawl, Cloudflare, closed beta).** A 402 on the homepage probe, or reported by another service, makes the host `paywalled`; a price header, if sent, is recorded. This service sends no `crawler-max-price` and pays nothing; joining the beta is a human decision.

**Access mode.** `direct` when the homepage probe succeeds. On a Cloudflare challenge (challenge page, `cf-mitigated: challenge`) one attempt through the shared Playwright pool: success gives `headless`; failure gives one attempt through Decodo or Oxylabs egress, allowed by quota-governor under `news_proxy_egress`: success gives `proxy`; failure, or an interactive CAPTCHA, gives `blocked`. No CAPTCHA solving. About a quarter of Iraqi sites are expected to need `headless` or `proxy`; the exact share is to be confirmed in the pilot.

### 5.4 What it gets

robots.txt rules and directives; `Content-Signal` values; RSL terms; the status of the homepage probe; challenge markers. It does not get: article content, whether a site's terms of service (outside robots.txt) restrict crawling (a human review item), or hosts' intentions beyond what they publish. A host with no robots.txt and no signals is `allowed`.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.news-robots-checker`; control-plane `crawl_policies`, `sources`, `news_sites`; `source.events` (`added`, `tier change`, `retired`) to maintain the refresh set.

### 6.2 Writes

`crawl.policies`, one message per host on first check and on every change, keyed by `host`. Hosts in the example are illustrative.

```json
{
  "schema": "crawl.policies/v1",
  "host": "www.example-daily.iq",
  "status": "allowed", "crawl_allowed": true, "reason": null,
  "access_mode": "proxy", "crawl_delay_seconds": 5,
  "robots_status": "ok",
  "robots_rules": {
    "http_status": 200, "fetched_at": "2026-10-06T06:30:11Z",
    "group": "ListeningBot", "sha256": "7f3a1c9e5b2d48a6f0c1e9d7b3a5f482c6d0e1a9b7f3c5d2e8a4b6c0f1d9e373",
    "disallow": ["/wp-admin/", "/search"], "allow": ["/wp-admin/admin-ajax.php"],
    "sitemaps": ["https://www.example-daily.iq/sitemap_index.xml"]
  },
  "usage_signals": {"search": "yes", "ai_input": "unset", "ai_train": "no"},
  "rsl": {"found": false},
  "payment": {"http_402": false, "price": null},
  "checked_at": "2026-10-06T06:30:14Z", "expires_at": "2026-10-07T06:30:14Z",
  "policy_version": 3, "changed_fields": ["access_mode"],
  "requested_by": "news-article-extractor", "kind": "recheck",
  "service": "news-robots-checker", "job_id": "01J9N3Q8D5W2K7X1R4T9V0MZBC"
}
```

Also the `crawl_policies` row (same fields plus `next_refresh_at` and `next_slot_at`), `service_runs`, `dlq.news-robots-checker` after 5 failed attempts. registry-writer maps `crawl_allowed = false` onto `sources.health = blocked`.

### 6.3 State

`crawl_policies` (one row per host: `status`, `crawl_allowed`, `access_mode`, `crawl_delay_seconds`, `robots` including compiled rules, `usage_signals`, `rsl`, `payment`, `checked_at`, `expires_at`, `next_refresh_at`, `policy_version`, `next_slot_at`); job `attempt`; per-host cooldown timers in memory.

## 7. Limits, quotas and cost

- No external quota. About 500 hosts mean about 500 robots.txt requests a day plus a homepage probe and an RSL fetch where one exists; re-checks add a few more. This is the cheapest service in the lane.
- Hosting: one small container plus the leader scheduler; the whole news lane costs in the low tens of USD a month on Hetzner.
- Proxy egress: only for the egress test on challenged hosts (a handful of requests per host per refresh), metered under `budget_tag = news_proxy_egress`; price per GB to be measured in the pilot. `news_disqus` belongs to news-comments-fetcher.
- Volume: about 375,000 articles a month across about 500 domains at about 25 articles a day each are only fetched from hosts this service allows.
- Legal basis: excerpts of 200 to 300 characters plus metadata and hashes under Iraqi copyright law (Law No. 3 of 1971), full text only in a 7-day cache (`news_excerpt`); this service is what makes "robots.txt and signals honoured" literally true.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts to `dlq.news-robots-checker` with an alert; `Retry-After` honoured.
- robots.txt 401 or 403 without a challenge marker: `blocked`, no retry through another IP or user agent.
- robots.txt 5xx, timeouts, DNS errors: last known rules kept for a limit set in the pilot, otherwise `disallowed`; retried with backoff; `robots_unreachable_hosts` alert.
- Malformed robots.txt: parsed leniently per RFC 9309 (unknown lines ignored); an empty file means no rules.
- Policy cannot be written: the previous row stays and consumers hold the host until it expires; alert.
- Partial write: the row is upserted before the message is produced; a replay produces the same `policy_version` once.

## 9. Non-functional requirements

- Throughput: about 500 hosts a day plus re-checks; trivial.
- Latency: first policy within 15 minutes; re-check within 15 minutes.
- Idempotency: one row per host; messages keyed by `host` and `policy_version`; replayable jobs.
- Scaling: one or two workers; one leader scheduler.
- Security: proxy credentials from the vault per job, never logged; no cookies; no account pools; every policy keeps its `robots.sha256` as evidence.

## 10. Metrics and alerts

Standard set: `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`; plus `policy_age_seconds` (max and p99), `hosts_by_status{status}`, `hosts_by_access_mode{mode}`, `recheck_total{requested_by}`, `policy_changed_total`, `signals_total{signal,value}`, `rsl_found_total`, `payment_402_total`. Alerts: `rotation_behind`, `policy_near_expiry`, `dlq_nonempty`, `robots_unreachable_hosts`, `blocked_hosts_rising`. SLO: no policy in use older than 24 hours for 99% of hosts per day.

## 11. Dependencies

`listening-sdk` (host gate), news-site-resolver, news-feed-poller, news-sitemap-poller, news-homepage-differ, news-article-extractor, news-comments-fetcher, registry-writer, quota-governor, source-health-canary, raw-archiver, Supabase Postgres, Redpanda, the shared Playwright pool, Decodo or Oxylabs keys in the vault.

## 12. Risks and mitigations

- Signals are new and ambiguous (`ai-input`, `search`): recorded and shown to ops; handling decided with counsel; conservative default for `search = no`.
- A host's terms of service forbid crawling while robots.txt is silent: a review item on the registry card; the policy cannot see it.
- Over-blocking from misparsed rules: compiled rules are stored with the file hash and re-tested in fixtures.
- Cloudflare egress test costs bytes: attempted once per refresh and only for challenged hosts.

## 13. Acceptance criteria

1. For a host with no `crawl_policies` row, the first request to it by any news service is `GET /robots.txt` from this service (request-log test); no other news service makes a request before `crawl.policies` or an unexpired row exists.
2. A robots.txt with `User-agent: ListeningBot` and `Disallow: /` gives `status = disallowed`, `crawl_allowed = false`; the same rule under `*` also does, unless a `ListeningBot` group overrides it.
3. Fixtures confirm longest-match precedence, `Allow` winning ties, and the `*` and `$` wildcards.
4. robots.txt 404 gives `allowed` with `robots_status = unavailable` (ADR-0070); 503 with no previous rules gives `disallowed` (`robots_unreachable`); 503 with previous rules keeps them and retries.
5. `Content-Signal: search=yes, ai-input=no, ai-train=no` yields the three values; `search=no` yields `disallowed`; the values appear in `usage_signals`.
6. An RSL file requiring payment gives `paywalled`; one permitting our use is recorded and `allowed`.
7. A 402 on the homepage probe gives `paywalled`; the request never carries a price-offer header.
8. A Cloudflare challenge fixture gives `headless` when the pool passes it, `proxy` when only egress passes, `blocked` for an interactive CAPTCHA; no CAPTCHA solving is attempted.
9. A 403 reported by news-article-extractor creates one `recheck`; ten 403s within the cooldown create one.
10. Over a simulated 48 hours with 500 hosts, no policy used by a fetch is older than 24 hours and no host is skipped twice in a row.
11. `crawl.policies` is produced on first check and on change, not on an unchanged refresh; a flip to `disallowed` stops all requests to the host within one scan.

## 14. Open questions

1. Is `search = no` a stop (proposed) or a signal only? A media-monitoring index of excerpts is search-like, so the proposal is conservative; decision with counsel.
2. How `ai-input = no` affects model analysis of excerpts and of the 7-day cache: carried in `usage_signals`; rule to be decided with the analysis services.
3. The RSL usage-category mapping and the number of Iraqi hosts with RSL or pay-per-crawl: to be confirmed in the pilot.
4. The refresh margin and the unreachable-file limit: to be set in the pilot.
5. Whether to join Cloudflare's pay-per-crawl beta for hosts of high client value: a business decision.
