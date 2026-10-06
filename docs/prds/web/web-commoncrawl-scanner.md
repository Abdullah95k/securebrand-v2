# web-commoncrawl-scanner

**Platform:** Web · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend engineer (Node), discovery lane · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The news side of the product rests on a registry of about 500 Iraqi and regional domains, at about 25 articles a day each, which is where the 0.375M news articles a month come from. A site enters that registry only when someone finds it: a search hit routed by search-hit-router, a decision by the qualifier, or an ops entry. Search finds a site only when it ranks for a client's keyword, and ops finds only what ops remembers. Nobody takes a census.

Common Crawl publishes a public index of the pages it has captured in each monthly crawl, free of charge. web-commoncrawl-scanner reads that index once a month, lists every host under `.iq` and every sibling host of a known Iraqi outlet (including outlets on `.com`, `.net` and other domains), drops what the registry already has, and sends the rest as candidate news sites for poster-resolver to hand to news-site-resolver. It reads an index, not the sites themselves.

Without it the registry grows by luck: provincial outlets, small independent sites and ministry and state-company news pages stay unknown until something happens to rank, and a client's "no mention found" may mean "we never looked at the site that wrote it".

## 2. Objective (the end state this service delivers)

Every month, after Common Crawl publishes a new crawl, the latest crawl is scanned for Iraqi hosts; every host that is not registered, not recently emitted and plausibly publishes news is sent exactly once as a `discovery.hits` message of type `site`; and no site is ever fetched by this service.

Targets: a published crawl scanned within a window set in the pilot; zero hosts emitted twice for the same crawl; hosts found, hosts new to the registry and the share news-site-resolver accepts, all to be measured in the pilot.

## 3. Scope

### In scope

- A daily check for a new published crawl; one scan per new crawl.
- Reading the index for hosts under `.iq` and for hosts sharing a registrable domain with a registered news site or an ops-listed outlet.
- Per-host aggregation, scoring, deduplication against the registry and against earlier scans, and emission of `discovery.hits`.

### Out of scope

- Fetching any site, reading page bodies from the crawl archives, checking robots.txt, feeds or sitemaps (news-robots-checker, news-site-resolver).
- Deciding registration (news-site-resolver, qualifier, registry-writer); extraction, polling and deduplication of articles.
- Scanning past crawls, and link-graph analysis (open question 4).

## 4. Users and consumers

poster-resolver (consumer of `discovery.hits`, which routes sites to news-site-resolver); ops, who read the yield and the pending list; Abdullah for the coverage story ("how many Iraqi sites exist that we do not yet read").

## 5. How it works

### 5.1 Trigger and rotation

- **Schedule.** Monthly. Common Crawl publishes about once a month, so a daily check asks for the list of published crawls (one cheap request) and starts a scan when it sees a crawl id it has not scanned. A scan is one job of kind `rotation` on `jobs.web-commoncrawl-scanner`; ops can start one with `ops_force`. The scheduler is a leader-elected loop (Postgres advisory lock); the next check is set from the START of the last check, so cadence is fixed.
- **Unit of rotation: the crawl.** Registered news sites are not polled here, but every one of them (any tier, dormant included) is a seed in every scan, so every registered outlet is covered each month by the sibling search. Work is cut into partitions (the `.iq` zones, and batches of seed domains); the scan is complete only when every partition is done, and each completed partition emits its hosts at once.
- **Catch-up.** A scan interrupted by an error or restart resumes from its checkpoint, partition by partition. If a newer crawl is published while a scan is running, the running scan finishes first and only the newest crawl is scanned next; older unscanned crawls are skipped, because each crawl is a snapshot. `scan_behind` is raised when a published crawl is still unscanned after the target window (set in the pilot).
- **Backfill on add.** None applies. The first scan scans the latest crawl and finds the whole backlog of unregistered hosts at once, so emission is capped per scan (`CC_MAX_HITS_PER_SCAN`, set in the pilot) and rate-limited; surplus hosts stay `pending` and are emitted by the next scan, highest score first.
- **Re-emission.** A host emitted before and still unregistered is not emitted again unless its capture count has grown markedly or a long interval has passed (both set in the pilot); poster-resolver's own 180-day memory of rejected candidates applies on top.

### 5.2 Step by step

1. Daily check: compare the published crawl list with the last scanned id; a new id creates a scan with its partitions.
2. Build seeds: the registrable domains of all `sources` rows with `platform = news`, plus `.iq` and its second-level zones such as `gov.iq` and `com.iq` (zone list to be confirmed in the pilot).
3. Read the index per partition and aggregate by host: number of captures, first and last capture time in the crawl, up to 5 sample URLs, path signals (date segments, `/news/`, `/article/`, Arabic news words in paths), and the share of Arabic or Kurdish captures where the index exposes language.
4. Drop hosts already in `sources` (match on host and registrable domain) and hosts suppressed by earlier scans; keep, but do not emit, hosts with only a root-page capture.
5. Score each remaining host from its signals (a number from 0 to 1, weights set in the pilot).
6. Write the scan's per-host aggregate to object storage under the standard raw path (a direct write; this service has no `raw.items`).
7. If the host count is far below the previous scan's, hold the scan for review and emit nothing; otherwise emit `discovery.hits` in descending score order up to the cap.
8. Record the checkpoint and `cc_hosts_seen`; write `service_runs`.

### 5.3 The call it makes

Free, public, no key. Logically two kinds of read against the latest crawl's index:

```
crawl list : the published crawls (id, publication date)
read 1     : captures with domain match "*.iq", grouped by host
read 2     : captures with domain match "<seed registrable domain>", for each seed, grouped by host
```

The access route (the public index server's per-URL query API with domain match, or bulk reads of the columnar index with a query engine), every parameter name, page size and rate limit are to be confirmed in the pilot. The service paces its requests sequentially with a pause, sends a user agent naming the company and a contact address, never fetches a site's own pages, and in v1 never reads page bodies from the crawl archives.

### 5.4 What it gets

Per capture: URL, host, capture time, HTTP status, MIME type, and language where exposed. Per host (after aggregation): captures, first and last capture, sample URLs, path signals, language share.

It does not get page text or titles, feed or sitemap status, authorship, whether the site is alive today (a capture is a month-old snapshot), sites the crawl never reached (small sites, sites that block its crawler, some sites behind a challenge), or outlets that exist only on social media.

## 6. Inputs and outputs

### 6.1 Reads

The published-crawl list and the index of the latest crawl; `sources` (news site rows, all tiers); `service_runs`; the service-private table `cc_hosts_seen` (host, first and last emitted, captures at emission, state `emitted`, `pending` or `suppressed`).

### 6.2 Writes

`discovery.hits` of type `site`, partition key `candidate_key`; no `raw.items`, no `search.results`:

```json
{
  "schema": "discovery.hits/v1",
  "message_id": "dh:web-commoncrawl-scanner:news:example-daily.iq:CC-MAIN-2026-38",
  "produced_at": "2026-10-09T02:14:55Z",
  "service": "web-commoncrawl-scanner", "route": "green", "vendor": null,
  "type": "site", "platform": "news",
  "candidate_key": "news:example-daily.iq",
  "poster_ref": {"host": "www.example-daily.iq", "registrable_domain": "example-daily.iq", "url": "https://www.example-daily.iq/"},
  "origin": "commoncrawl_index",
  "evidence": {"crawl_id": "CC-MAIN-2026-38", "captures": 1840, "first_capture": "2026-09-14", "last_capture": "2026-09-27",
               "sample_urls": ["https://www.example-daily.iq/economy/2026/09/26/fiberx-wasit"],
               "path_signals": ["date_path", "news_path"], "language_share": {"ara": 0.93}, "news_score": 0.82},
  "keyword_rule_id": null, "client_ids": []
}
```

The field set beyond `type`, `platform` and `candidate_key` follows poster-resolver's approved schema where it differs (open question 3). Also `service_runs` and `dlq.web-commoncrawl-scanner` after 5 failed attempts.

### 6.3 State

The scan checkpoint (crawl id, partitions done, position inside a partition) as JSON on this service's `service_runs` row; `cc_hosts_seen`; in memory only the leader lock.

## 7. Limits, quotas and cost

- Cost: USD 0 for the data. Common Crawl is free, with a monthly cadence. The addendum lists no budget tag for it and none is used; the service asks quota-governor for nothing.
- Compute: the scan's data volume and worker time on Hetzner servers are to be measured in the pilot, and decide whether the index API or bulk reads are used.
- Politeness limits and any fair-use expectations of the index server: to be confirmed in the pilot.
- Output is bounded by `CC_MAX_HITS_PER_SCAN`, so news-site-resolver is never flooded.
- Nothing personal is stored: hosts, counts and up to 5 sample URLs per host; page content is never copied.

## 8. Failure handling and fallback

- HTTP 429 or 503 from the index server: exponential backoff with jitter from 30 s to 15 min, then requeue the partition with `attempt + 1`; after 5 attempts it goes to `dlq.web-commoncrawl-scanner` and an alert fires. The scan resumes later from its checkpoint.
- HTTP 401 or 403: the route is marked `degraded`, the scan stops, an alert fires; no other route or identity is tried to get around a block.
- Crawl list unreachable: retried the next day; `scan_behind` is the alert if it persists.
- Empty or implausible result (zero `.iq` hosts, or far fewer than last time): this is the equivalent of an empty 200; the scan is held for review and nothing is emitted. source-health-canary is told so it can flip `health = degraded`; no alternate route exists, so `fallback_on` is never set.
- Unknown index shape: the sample is archived, `schema_unknown` is raised, the partition is parked and emits nothing.
- Partial run: checkpoints advance only after the partition's messages are acknowledged; identical `message_id` values make a replay safe.

## 9. Non-functional requirements

- Throughput: one scan a month; duration to be measured in the pilot; partitions run in parallel on queue depth.
- Latency: hits within the target window after a crawl is published; nothing here is real time.
- Idempotency: `message_id = dh:web-commoncrawl-scanner:<candidate_key>:<crawl_id>`; poster-resolver also deduplicates by `candidate_key`.
- Scaling: stateless partition workers; one leader scheduler.
- Security: no key or secret; egress limited to the index and data hosts of Common Crawl; no personal data; `/healthz`, `/metrics`, structured logs; Node (TypeScript).

## 10. Metrics and alerts

`scans_total{status}`, `scan_duration_seconds`, `hosts_found_total`, `hosts_new_total`, `hosts_emitted_total`, `hosts_suppressed_total`, `partitions_pending`, `scan_age_seconds` (age of the newest unscanned crawl), `accept_rate` (share of emitted hosts that become registered news sites, from `source.events`), `dlq_total`. Alerts: `scan_behind`, `scan_held_for_review`, `emission_capped`, `dlq_nonempty`.

## 11. Dependencies

`listening-sdk`, poster-resolver, news-site-resolver (through poster-resolver), qualifier, registry-writer, source-health-canary, Redpanda, Supabase Postgres, object storage, Common Crawl's public index.

## 12. Risks and mitigations

- The crawl does not cover every site, and a month-old snapshot can show a dead site: news-site-resolver verifies liveness and feeds; this scan is one of several discovery paths beside search-hit-router, the qualifier and ops.
- Noise: `.iq` holds many hosts that are not news (services, shops, universities): the score, the cap and the resolver's decision keep it manageable; the pilot sets thresholds and tracks `accept_rate`.
- Government sites under `.gov.iq` often publish real news: they are not filtered out; the resolver and qualifier decide.
- A new outlet on a non-`.iq` domain with no relation to a known outlet is not found here: search-hit-router and the web search services cover that.
- A change in the index's access route or terms: the scan is one adapter, and the two access routes are interchangeable in design.
- The first scan floods the pipeline: cap and rate limit, surplus kept `pending`.

## 13. Acceptance criteria

1. With a fixture crawl list containing a new id, the next daily check starts exactly one scan; with no new id none starts.
2. A fixture index with three `.iq` hosts (one registered, two not) and one sibling host of a registered non-`.iq` outlet produces `discovery.hits` for exactly the two unregistered `.iq` hosts and the sibling, and none for the registered host.
3. Every message has `type = site`, `platform = news`, `candidate_key = news:<registrable domain>`, `evidence.crawl_id`, `evidence.captures` and at most 5 sample URLs.
4. With a cap of 10 and 25 candidate fixtures, 10 are emitted in descending score order and 15 stay `pending`; the next scan emits them before newer hosts of lower score.
5. A host emitted in the previous scan, still unregistered and with unchanged captures, is not emitted again.
6. A scan killed halfway resumes from its checkpoint and no host is emitted twice (same `message_id`).
7. A fixture scan whose host count is far below the previous scan's is held for review and emits nothing.
8. An egress test shows the service sends no request to any host other than Common Crawl's; it never fetches a news site.
9. A crawl published while a scan runs is scanned only after the running scan finishes, and older unscanned crawls are skipped.
10. `scan_behind` fires when a published crawl stays unscanned beyond the target window.

## 14. Open questions

1. Access route: the index API or bulk columnar reads? The pilot measures time and data volume for one scan.
2. Does the index expose language per capture, and what is the exact list of `.iq` second-level zones?
3. Emission cap, score weights and the accept-rate target are set in the pilot; the `discovery.hits` field set is to be aligned with poster-resolver's schema.
4. Is Common Crawl's host-level web graph worth adding in v2, to find non-`.iq` outlets that known outlets link to?
5. Should ops be able to add outlet hosts by hand as seeds, separate from registered news rows?
