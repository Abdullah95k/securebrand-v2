# normalize-item

**Platform:** Shared · **Route:** shared · **Lane:** Processing · **Owner:** Backend lead (processing) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Every fetcher and receiver writes to `raw.items` exactly what its API or vendor returned: a Meta Graph `/feed` page, a TikHub video detail, an X v2 search response, a Telegram Bot API update, a trafilatura article, a Mojeek result list. Eleven payload families, nine platforms, two route classes, three timestamp formats. Nothing downstream can work on that: keyword-matcher needs one `text_norm`, the analysis services need one `text` and one `media[]`, store-writer needs one row shape, and the client-facing provenance statement needs route, vendor and fetch time on every record.

normalize-item is the single translation point. It turns every raw payload into one `items.normalized` record, assigns the idempotency key every store relies on, drops duplicates (the same post seen by the poller, a keyword search and a backfill is one item), hashes individual authors so no individual is ever profiled, stamps the retention class, and calls lang-dialect-id so the record leaves with language, dialect and `text_norm` filled.

Without it every per-source service would carry its own mapping and dedup key, a schema change at one platform would break every consumer instead of parking one batch, and an item without a normalizer version could not be re-run when a mapping bug is found.

## 2. Objective (the end state this service delivers)

End state: every record on `raw.items` is either published once to `items.normalized` in the one schema, or parked with a `schema_unknown` reason, within 60 seconds of its `fetched_at`.

Measurable target: 100% of raw records accounted for (published, deduplicated, metrics-only or parked; none silently dropped); p95 fetch-to-publish latency below 60 s at full scale (about 1,000,000 items a day, about 12 a second on average, peaks to be measured in the pilot); repeat `item_id` with an identical `content_hash` below 0.1% of daily output; zero records without an `idempotency_key`.

## 3. Scope

### In scope
- Consuming `raw.items` and mapping every route's payload: Meta Graph, Instagram Graph, TikHub and EnsembleData, TikTok Display API, X v2, LinkedIn Community Management API, harvestapi Actors, Telegram Bot API, Telemetrio and the Apify Telegram preview Actors, YouTube Data API, trafilatura articles from news-article-extractor, Perplexity and Mojeek results forwarded by search-hit-router.
- Idempotency keys, including the Facebook PPCA comment hash and the news canonical-URL hash; dedup and edit detection by content hash.
- Author hashing and typing (registered source versus individual); `retention_class` and `expires_at`; parent and root linking; `item.metrics` observations from the counts a payload carries.
- Calling lang-dialect-id; replay from the raw archive when `normalizer_version` or `lang_model_version` changes.

### Out of scope
- Keyword matching (keyword-matcher), inference beyond language id (analysis-sentiment, analysis-topics, analysis-media, analysis-entities), ClickHouse writes (store-writer), raw archiving (raw-archiver), fetch decisions (per-source services, comment-decay-scheduler), purging (retention-purger, deletion-propagator), media downloads (analysis-media).
- Guessing at an unknown payload shape: it is parked, never repaired by heuristics.

## 4. Users and consumers

- keyword-matcher is the primary consumer of `items.normalized`; store-writer, comment-decay-scheduler (learns a post was first seen and starts its series) and raw-archiver (monthly Parquet of normalized items) consume it too; store-writer also consumes the `item.metrics` observations emitted here.
- deletion-propagator and retention-purger derive the same `item_id` from the same key, so the derivation lives in `listening-sdk`.
- Ops read parked batches in `review_queue` and run replays; Abdullah and account managers rely on the provenance fields that every client report shows.

## 5. How it works

### 5.1 Trigger and rotation

Trigger: the `raw.items` topic, consumer group `normalize-item`. Partitions follow `source_id`, so every record of one source is processed in order by one worker; records without a `source_id` (keyword searches, hashtag feeds, search results) are keyed by the producer on `<platform>:<poster platform_id>`, which keeps a poster's post and its later comments together. Offsets are committed only after Redpanda acknowledges the batch on `items.normalized`; a crash replays the batch and dedup makes that harmless.

Ordering: a comment can arrive before its post (Page webhooks, newest-first comment APIs). It is published with `parent_id` set and `parent_seen = false`; store-writer and comment-decay-scheduler tolerate orphans and link them when the post arrives.

Replay: when `normalizer_version` or `lang_model_version` changes, ops creates a job on `jobs.normalize-item` with `kind = replay`, a date range and an optional platform filter. The replay worker reads `raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst` from object storage (never Redpanda, whose retention is days), re-normalizes and publishes with the same `item_id`; the stores upsert, so consumers see a new version, not a duplicate. Replay runs under consumer group `normalize-item-replay-<version>` with a rate cap (default 200 records a second). Backfill traffic from fb-backfill and backfill-orchestrator is ordinary live traffic with `job_kind = backfill` in the envelope.

### 5.2 Step by step

1. Pull a batch (up to 500 records or 2 s) and read the envelope: `service`, `route`, `vendor`, `platform`, `source_id`, `job_id`, `job_kind`, `fetched_at`, `api_version`, `raw_ref`.
2. Select the mapper by `(service, api_version)`; no match or a missing required field raises `schema_unknown`, parks the batch key in `review_queue` and skips the batch (raw-archiver already holds the payload).
3. Map fields (5.3); compute `idempotency_key`, `item_id = uuid_v5(ns_items, idempotency_key)` and `content_hash = sha256(title + text + media urls)`.
4. Decide the outcome against an in-memory LRU of the last 1,000,000 keys and, on a miss, a batched ClickHouse point lookup on `items` and `comments`: new → publish; known with an equal hash → metrics-only; known with a different hash → `version + 1`.
5. Call lang-dialect-id `POST /v1/detect` with the batch texts and embed `lang`, `lang_conf`, `dialect`, `dialect_conf`, `script`, `text_norm`, `lang_model_version`.
6. Hash authors: `author_ref = hmac_sha256(AUTHOR_HASH_KEY, platform + ':' + author_platform_id)`. An author found in the registry cache (fed by `source.events`) gets `author_type = source`, `author_source_id` and its display name; anyone else is `individual` with no name, handle or avatar.
7. Stamp `retention_class` (source row, else route and platform default) and `expires_at` from `retention_classes`.
8. Publish to `items.normalized` and one `item.metrics` observation per record that carries counts; commit offsets after the acks.

### 5.3 The call it makes (the processing it performs)

The mapper table, versioned by `normalizer_version` in `listening-sdk` (key, then the fields that fill `text`, `created_at`, author and `metrics_snapshot`):

- Meta Graph `/feed` (fb-page-feed-poller, fb-backfill): `facebook:post:<id>`; `message`, `created_time`; `from` only on client-owned Pages; reactions by type, `shares.count`, `comments.summary`.
- Meta Graph PPCA comments (fb-post-comments-fetcher): no id, so `facebook:comment:<post_id>:<sha256(created_time + text)>`; `message`, `created_time`, `like_count`; `author_ref` null.
- Page webhooks (fb-client-webhook-receiver): `facebook:comment:<id>`; commenter id hashed, never stored in clear.
- SociaVault and ScrapeCreators (fb-keyword-search, fb-group-posts-poller, fb-group-comments-fetcher): vendor ids; poster hashed unless a registered source; `route = amber`.
- Instagram Graph (ig-hashtag-search, ig-account-media-poller, ig-mentions-fetcher, ig-own-comments-fetcher, ig-webhook-receiver, ig-comments-fetcher): `instagram:post:<media id>`, `instagram:comment:<id>`; `caption` or `text`, `timestamp`, `like_count`, `comments_count`; `username` hashed; none on hashtag media of unmanaged accounts.
- TikHub and EnsembleData (tt-keyword-search, tt-hashtag-feed-poller, tt-profile-videos-poller, tt-video-comments-fetcher, tt-video-stats-refresher): `tiktok:post:<aweme_id>`, `tiktok:comment:<cid>`; `desc`, `create_time` (Unix seconds), `digg_count`, `comment_count`, `share_count`, `play_count`; `author.uid` hashed unless a creator source. TikTok Display (tt-client-videos-fetcher): the client's own videos and counts.
- X v2 (x-recent-search, x-full-archive-search, x-filtered-stream, x-user-timeline-poller, x-replies-fetcher): `x:post:<id>`; `text`, `created_at`, `public_metrics`; author from `includes.users`; `conversation_id` → `root_id`; `referenced_tweets` decides `reply`, `quote` or `post`.
- LinkedIn (li-client-posts-poller, li-own-comments-fetcher; harvestapi through li-post-search, li-company-posts-poller, li-post-comments-fetcher): share and comment urns; `commentary` or `message.text`, `created.time` in milliseconds; member actors hashed.
- Telegram Bot API (tg-bot-channel-receiver, tg-discussion-receiver): `telegram:message:<chat_id>:<message_id>`; `text` or `caption`, `date`; discussion replies link through `forward_from_message_id` → `parent_id`; no views. Telemetrio and the Apify preview Actors (tg-message-search, tg-channel-posts-poller): same key shape; text, date, views, forwards; no comments.
- YouTube Data API (yt-video-details-fetcher, yt-comments-fetcher, yt-replies-fetcher): `youtube:video:<id>`, `youtube:comment:<id>`; `snippet.title` → `title`, `description` or `textOriginal` → `text`, `publishedAt`, `statistics`; `authorChannelId` hashed.
- trafilatura article (news-article-extractor): `news:article:<canonical_url_hash>`; `title`, an excerpt of 200 to 300 characters as `text`, `text_full_ref` to the 7-day cache, `date`, `canonical_url`.
- Perplexity and Mojeek (search-hit-router): `web:result:<sha256(canonical url)>`; title, snippet, result date; the domain is the poster.

All timestamps become UTC ISO 8601; hashtags, @-mentions and links are extracted into arrays; `root_id` is the thread root; the retention class follows the route (`x_24h_sync`, `youtube_30d_text`, `linkedin_48h`, `meta_on_request`, `vendor_agreed`, `news_excerpt`).

### 5.4 What it gets

One record per raw item in the shape of the example in 6.2: identity, tree, time, content, language, author (`display_name` and `author_followers` for sources only), provenance, retention and versions.

What it does not get, by route: commenter identity or comment ids under PPCA; usernames on Instagram hashtag media of unmanaged accounts; comment text on third-party Instagram media on the green route; views on Bot API channel posts; comments on Apify preview posts; full article text beyond the 7-day cache; any Facebook Group content on the green route.

## 6. Inputs and outputs

### 6.1 Reads
- Topics: `raw.items` (live), `jobs.normalize-item` (`replay`, `lang_rescore`), `source.events` (registry cache refresh).
- Control plane: `sources` (cache), `retention_classes`, `service_runs` (lag), `review_queue` (parked batches).
- Object storage `raw/` for replay; ClickHouse `items` and `comments` for dedup lookups.

### 6.2 Writes
`items.normalized` (keyed by `source_id` or poster key), `item.metrics`, `dlq.normalize-item`, `review_queue`.

```json
{
  "schema": "items.normalized/v1",
  "message_id": "01J9W4Q7K2M8R3T5V6X7Y8Z9A0",
  "produced_at": "2026-10-06T09:14:03Z",
  "producer": {"service": "normalize-item", "version": "1.4.0", "job_id": "fb-page-feed-poller:2026-10-06T09:00Z:7c1e"},
  "item_id": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f",
  "idempotency_key": "facebook:post:1234567890_9876543210",
  "platform": "facebook", "kind": "post",
  "source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566",
  "parent_id": null, "root_id": null, "parent_seen": true,
  "platform_id": "1234567890_9876543210",
  "url": "https://www.facebook.com/1234567890/posts/9876543210",
  "created_at": "2026-10-06T08:51:40Z", "fetched_at": "2026-10-06T09:13:58Z",
  "title": null,
  "text": "النت منقطع بالبصرة من الصبح، شنو السالفة؟",
  "text_norm": "النت منقطع بالبصره من الصبح شنو السالفه",
  "lang": "ar", "lang_conf": 0.98, "dialect": "iraqi", "dialect_conf": 0.84, "script": "arab",
  "author": {"author_ref": "hmac:9c1f…", "author_type": "source", "author_source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566", "display_name": "Example Page"},
  "media": [{"type": "image", "url": "https://scontent.example/abc.jpg"}],
  "hashtags": [], "at_mentions": [], "links": [],
  "metrics_snapshot": {"likes": 120, "comments": 14, "shares": 3, "reactions_by_type": {"LIKE": 100, "LOVE": 20}},
  "route": "green", "vendor": null, "service": "fb-page-feed-poller",
  "retention_class": "meta_on_request", "expires_at": null,
  "content_hash": "sha256:4b2e…", "version": 1,
  "normalizer_version": "1.4.0", "lang_model_version": "lid-iq-2026.09",
  "raw_ref": "raw/green/facebook/2026/10/06/fb-page-feed-poller/0007.jsonl.zst#1532"
}
```

### 6.3 State
Consumer offsets per partition; the LRU dedup cache (rebuilt lazily after a restart); the registry cache version (last `source.events` offset); replay progress in `cursors` keyed `service = normalize-item`, `cursor = replay:<version>:<last object key>`; a `service_runs` row with lag and error counts.

## 7. Limits, quotas and cost

No external API or vendor is called, so there is no `budget_tag` and no quota-governor round trip. Cost is cluster CPU plus lang-dialect-id calls and ClickHouse lookups. At 12 records a second on average one worker is enough; three replicas run for partition spread and failover, and the pool scales on consumer lag. Peak multiples (a hot post adding hundreds of comments an hour, a tier-1 backfill of 600 posts) are to be measured in the pilot. Hetzner pricing in USD is confirmed at order time; the replay rate cap keeps replays from starving live traffic.

## 8. Failure handling and fallback

- `schema_unknown`: the batch is parked in `review_queue` with the raw object key, an alert fires per `(service, api_version)`, and ops replays the parked keys once the mapper is fixed.
- lang-dialect-id unavailable: exponential backoff from 30 s to 15 min; after 5 minutes of failures the service publishes with `lang = "und"`, `text_norm` from the folding rules shared in `listening-sdk` and `lang_pending = true`, and enqueues a `lang_rescore` job for the window.
- ClickHouse lookup unavailable: dedup falls back to the LRU alone; duplicates become harmless store upserts; `dedup_degraded_total` increments.
- Produce failure: retry, offsets uncommitted until the ack. A poison record (mapper exception after 5 attempts) goes to `dlq.normalize-item` with an alert.
- Stale registry cache: a just-registered author is typed `individual` for at most one refresh interval (default 60 s); the next version corrects it.

## 9. Non-functional requirements

- Throughput: 1,000,000 items a day, 12 a second average; peaks and records a second per worker to be measured in the pilot.
- Latency: p95 fetch-to-publish below 60 s; p99 to be measured in the pilot.
- Idempotency: the same raw record processed twice yields the same `item_id` and `content_hash` and is dropped the second time; replays produce versions, never duplicates.
- Scaling: stateless workers in one consumer group; a backlog above 60 s adds a replica.
- Security: `AUTHOR_HASH_KEY` in Supabase Vault, rotated only with a full replay; no item text in logs; TLS inside the cluster; individuals carry no name, handle or avatar. Node (TypeScript); mappers and folding rules in `listening-sdk`.

## 10. Metrics and alerts

Prometheus: `items_fetched_total` (consumed), `items_new_total`, `items_out_total{result=new|version|metrics_only|parked}`, `jobs_total{status}`, `normalize_latency_seconds`, `consumer_lag_seconds`, `schema_unknown_total{service,api_version}`, `lang_fallback_total`, `dedup_degraded_total`, `dlq_total`. Alerts: lag above 60 s for 5 minutes; any `schema_unknown` for 15 minutes; parked batches older than 24 hours; `lang_fallback_total` rising for 10 minutes; DLQ non-empty (reviewed daily).

## 11. Dependencies

`listening-sdk` (mapper table, key derivation, folding rules, envelope), lang-dialect-id, Redpanda, Supabase Postgres (`sources`, `retention_classes`, `review_queue`, `service_runs`, Vault), ClickHouse (dedup lookups), raw-archiver (`raw_ref` and the replay source), every producer named in 5.3; keyword-matcher and store-writer as consumers.

## 12. Risks and mitigations

- Vendor payload drift (TikHub, SociaVault, harvestapi, the Apify Actors): mappers pinned per `api_version`, nightly contract tests against recorded fixtures, unknown shapes park rather than corrupt.
- PPCA hash collisions (two identical comments in the same second) merge into one item; the loss is one count, accepted.
- Timestamp mistakes (LinkedIn milliseconds, TikTok seconds) would silently shift rotations and aggregates: every mapper has a fixture asserting UTC output.
- A replay floods store-writer and the analysis queue: rate cap and a separate consumer group.
- A leaked author hash key would allow re-identification by brute force over platform ids: HMAC with a vault-held key and a defined rotation procedure.

## 13. Acceptance criteria

1. A recorded fixture for each payload family in 5.3 normalizes to a record that validates against `items.normalized/v1` with the expected `idempotency_key`.
2. A PPCA comment fixture with no id yields `facebook:comment:<post_id>:<sha256(created_time + text)>`, identical on a second run.
3. A news fixture yields `news:article:<canonical_url_hash>`, `text` of 200 to 300 characters and a set `text_full_ref`.
4. The same post fed three times (poller, keyword search, backfill) produces one `items.normalized` message and three `item.metrics` observations.
5. An edited comment fixture produces a second message with `version = 2` and a new `content_hash`.
6. An individual author fixture produces `author_type = individual`, an HMAC `author_ref` and no name, handle or avatar in the message or the logs; a registered source fixture produces `author_type = source` with the registry's `author_source_id`.
7. At a synthetic 50 records a second for 10 minutes, p95 fetch-to-publish latency stays below 60 s with three replicas.
8. An unknown `api_version` parks the batch in `review_queue`, publishes nothing from it and raises the alert within 15 minutes.
9. With lang-dialect-id stopped for 6 minutes, records are published with `lang = "und"` and `lang_pending = true`, and a `lang_rescore` job appears on `jobs.normalize-item`.
10. A replay of one archived day with a new `normalizer_version` republishes every item with the same `item_id`, and store-writer shows no duplicate rows.
11. Every record carries `retention_class` and, where the class is time-bound, a non-null `expires_at`.

## 14. Open questions

1. Should vendor-supplied poster names on amber routes be kept for creators below the qualifier thresholds, or hashed like individuals from the start (current draft: hashed)?
2. Which service owns the 7-day full-text cache for news: news-article-extractor through the raw payload, or a cache key written here?
3. Is a 60 s registry refresh from `source.events` enough, or should a cache miss query `sources` directly?
4. Peak records a second and worker count are to be measured in the pilot before the replica policy is fixed.
