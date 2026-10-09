# search-hit-router

**Platform:** Web · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend engineer (Node), discovery lane · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Four services search the open web for a client's keywords: web-search-perplexity, web-search-mojeek, web-gdelt-poller and yt-web-search-bridge. Each writes `search.results`: a title, a URL and a snippet. A URL is only a link. It may be an Instagram reel by a creator we have never seen, a Facebook Page, a Telegram channel, a YouTube video, an account on X, a LinkedIn company page, a TikTok creator, an article from an outlet we already read, an outlet we do not read yet, or a blog nobody cares about. Three engines will often return the same article on the same day, and every engine returns it again tomorrow.

search-hit-router is the one place where search results become work. It removes duplicates by canonical URL, decides what kind of URL each one is, and passes the interesting ones on: a platform link goes to poster-resolver as a candidate source, with the platform and a reference to the poster; a news URL on a registered domain goes to `article.urls` for fetching.

Without it the four engines would need their own routing logic, the same finding would reach poster-resolver dozens of times, a creator or channel found on the open web would stay invisible, and a news article that search found would wait until the site's own feed happened to list it.

## 2. Objective (the end state this service delivers)

Every `search.results` message is validated, deduplicated by canonical URL, classified, and either routed (a `discovery.hits` message, an `article.urls` message, or both for a news URL on a site still to be registered) or counted with a reason; none is lost and none is routed twice inside the re-route window.

Targets: zero messages lost; no URL routed twice within the window; consumer lag and the p95 from message arrival to routing are to be measured in the pilot; the share of results that end as `web` (no route) and each engine's unique yield are to be measured in the pilot.

## 3. Scope

### In scope

- Consuming `search.results` from the four producers; schema validation; verification of `canonical_url_hash`.
- Deduplication by canonical URL across engines, rules and days; candidate-level deduplication.
- URL classification by the table in 5.3; extraction of the poster reference and a handle hint from the title.
- Writing `discovery.hits` and `article.urls`; parking news URLs of unregistered domains and releasing them when the domain is registered.
- Yield metrics per engine and per query variant.

### Out of scope

- Calling any search engine; fetching any URL, even to follow a redirect (the router never touches the network apart from Redpanda and Postgres).
- Resolving posters and profiles (poster-resolver and the platform resolvers); registry decisions (qualifier, registry-writer); confirming a mention (keyword-matcher); fetching and extracting articles (news-article-extractor).
- Storing search results beyond the deduplication state; the engines archive their raw responses.

## 4. Users and consumers

poster-resolver (consumer of `discovery.hits`, which it deduplicates again by `candidate_key`); news-article-extractor (consumer of `article.urls`); news-site-resolver (receives site candidates through poster-resolver); the four engines (yield feedback through metrics); ops through `service_runs`; Abdullah for "what did web search find that nothing else did".

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Event-driven: every message on `search.results`, partitioned by `canonical_url_hash`, read by one consumer group. Because every engine's sighting of a URL lands on the same partition, one worker sees all sightings of a URL and deduplication needs no cross-worker coordination. Arrival follows the producers' schedules: Perplexity and Mojeek daily per rule (twice for priority), GDELT hourly, yt-web-search-bridge on demand.

**No source rotation.** The router polls nothing. Its cadence guarantee is consumer lag: partitions are read in order, and the group scales on lag. After an outage the backlog is read from the committed offset, oldest first, with no skipped message; `router_lag` is the alert.

**Late registration.** News URLs of unregistered news-like domains are parked. When `source.events` reports a new news site (`added`), its parked URLs are released to `article.urls` once; parked URLs expire after 30 days (proposed; set in the pilot).

**Backfill.** None. At first deployment the retained `search.results` is read from the earliest offset.

**Re-route window.** A URL, and a candidate, routed once is not routed again for 30 days (proposed; set in the pilot). Later sightings still update the evidence (engines, sightings, rules, clients).

### 5.2 Step by step

1. Consume a message; check `schema = search.results/v1` and the required keys. Unknown shape: park the message in `review_queue` and raise `schema_unknown`.
2. Skip a `message_id` already processed (replay); replays never add a sighting.
3. Recompute the canonical URL hash with the shared canonicaliser and compare it with the message's; a mismatch is counted and the message parked.
4. Upsert `search_url_seen`: first sighting, or add engine, rule and clients to an existing row. If the URL was routed inside the window, stop with outcome `duplicate`.
5. Classify with the table in 5.3. A platform URL yields a poster reference and a `candidate_key`; a private invite or reserved path ends as `unroutable` with its reason.
6. Check the registry: a candidate already in `sources` ends as `already_registered`; no `discovery.hits` is needed.
7. Upsert `search_candidate_seen` on `candidate_key`; the worker whose upsert inserts the row emits, so two workers handling two URLs of one poster never both emit.
8. Write `discovery.hits`, wait for Redpanda's acknowledgement.
9. Everything else: if its registrable domain is a registered news site (any tier, dormant and retired included), write `article.urls` with that site's `source_id`. If the domain is not registered and the URL is news-like, write a `discovery.hits` of type `site` for the domain and park the URL. Otherwise the outcome is `web`: counted, nothing emitted.
10. Commit the offset only after the produce is acknowledged.

### 5.3 The call it makes

None. The router makes no external call and never fetches a URL. Its work is the classification table and three lookups in the control plane (registered sources, registered news domains, the service-private deduplication tables).

Before matching, the host loses `www.`, `m.` and `mobile.`, `twitter.com` is read as `x.com`, and query strings and fragments are dropped except `v=` on YouTube watch URLs and `id=` on `profile.php`.

| URL pattern | Platform | `type` | Poster reference and `candidate_key` |
|---|---|---|---|
| instagram.com/p/…, /reel/…, also /handle/p/…, /handle/reel/… | instagram | account | handle from the path, else `handle_hint` from the title; `instagram:<handle>`, or `instagram:post:<shortcode>` when no handle is readable |
| facebook.com/groups/… | facebook | group | group id or slug; `facebook:group:<id or slug>` |
| facebook.com/<vanity>, /pages/<name>/<id>, /profile.php?id=… (optionally with /posts/<id>) | facebook | page | vanity or id; `facebook:<vanity or id>`; fb-page-resolver checks that it is a Page, not an individual |
| t.me/<name>, t.me/<name>/<id>, t.me/s/<name> | telegram | channel | username; `telegram:<name>`. t.me/c/…, t.me/+… and t.me/joinchat/… are private: `unroutable` |
| youtube.com/@handle, /channel/…, /c/…, /user/… | youtube | channel | handle or channel id; `youtube:<id or handle>` |
| youtube.com/watch?v=…, /shorts/…, youtu.be/… | youtube | channel | video id as `post_ref`; `youtube:video:<id>`; yt-channel-resolver finds the channel |
| x.com/<handle>, x.com/<handle>/status/… (reserved paths such as /i, /home, /search, /hashtag, /intent, /share, /explore excluded) | x | account | handle; `x:<handle>` |
| linkedin.com/company/<slug> | linkedin | company_page | slug; `linkedin:<slug>` |
| tiktok.com/@<handle>, /@<handle>/video/… | tiktok | creator | handle; `tiktok:<handle>` |
| everything else | news or web | site | host; `news:<registrable domain>` |

News-like means: the engine is GDELT, or at least two of (a) the result carries a publication date, (b) the path has a date segment or a news segment (`/news/`, `/article/`, `/story/`, or the Arabic word for news), (c) the host is under `.iq` (rule proposed; tuned in the pilot).

### 5.4 What it gets

Only what `search.results` carries: the result (rank, title, URL, snippet, date), the query (text, variant, language, country), the keyword rule, `client_ids`, the engine, `canonical_url`, `canonical_url_hash`, `raw_ref`, and from GDELT an optional `hints` object. It does not get the page, the poster's profile, any follower count, or proof that a result is Iraqi: poster-resolver and the qualifier judge that.

## 6. Inputs and outputs

### 6.1 Reads

`search.results`; `source.events`; `sources` (registered news domains; registered handles and ids by platform); the service-private tables of 6.3; the shared canonicaliser and classifier in `listening-sdk`.

### 6.2 Writes

`discovery.hits`, partition key `candidate_key`, one message per new candidate:

```json
{
  "schema": "discovery.hits/v1",
  "message_id": "dh:search-hit-router:instagram:example_creator_iq:sha256:5d18c2…",
  "produced_at": "2026-10-06T03:15:02Z",
  "service": "search-hit-router", "route": "green", "vendor": null,
  "type": "account", "platform": "instagram",
  "candidate_key": "instagram:example_creator_iq",
  "poster_ref": {"handle": "example_creator_iq", "platform_id": null, "url": "https://www.instagram.com/example_creator_iq/reel/Cx4kQ2LsT9m/", "post_ref": "Cx4kQ2LsT9m", "handle_hint": null},
  "origin": "web_search",
  "evidence": {"canonical_url_hash": "sha256:5d18c2…", "engines": ["perplexity", "mojeek"], "sightings": 3, "first_seen_at": "2026-10-05T03:14:09Z",
               "keyword_rule_ids": ["7d2b0c4e-1f3a-4b5c-8d6e-9f0a1b2c3d4e"], "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
               "title": "…", "snippet": "…"}
}
```

Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

`article.urls`, partition key `source_id` (the news site's):

```json
{
  "schema": "article.urls/v1",
  "message_id": "au:search-hit-router:sha256:9c1e4b…",
  "idempotency_key": "news:article:sha256:9c1e4b…",
  "service": "search-hit-router", "found_by": "web_search",
  "source_id": "a41f7d02-93be-4c58-8e16-2b5d70c9f3e4",
  "url": "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit?utm_source=fb",
  "canonical_url": "https://www.example-daily.iq/economy/2026/10/05/fiberx-wasit",
  "canonical_url_hash": "sha256:9c1e4b…",
  "engines": ["perplexity", "gdelt"], "keyword_rule_ids": ["7d2b0c4e-1f3a-4b5c-8d6e-9f0a1b2c3d4e"], "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],
  "title": "…", "snippet": "…", "published_hint": "2026-10-05", "first_seen_at": "2026-10-05T03:14:09Z"
}
```

Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

The field set beyond `candidate_key`, `platform` and `type` follows poster-resolver's approved schema where it differs (open question 3). Also `service_runs`, `review_queue` (parked messages), `dlq.search-hit-router`.

### 6.3 State

Three service-private Postgres tables, partitioned by month: `search_url_seen` (canonical URL hash, canonical URL, first and last seen, sightings, engines, bounded lists of rules and clients, platform, `candidate_key`, routed time, outcome), `search_candidate_seen` (candidate key, first emitted, evidence) and `search_parked_urls` (domain, URL, parked time). Rows expire 180 days after the last sighting, matching the qualifier's memory of rejected candidates. In memory: the registered-domain cache, refreshed from `source.events`.

Owner (ADR-0025): `search_url_seen`, `search_candidate_seen` and `search_parked_urls` are private to this service. No other service reads them, F3's `TABLE-OWNERS.md` lists them, and they are registered in the SDK purge registry where they hold item ids, hashes or URLs.

## 7. Limits, quotas and cost

- No external call, no vendor, no budget tag, no price: the cost is worker and Postgres time, USD 0 in vendor charges.
- Volume is set by the producers: web-search-perplexity about 1,800 queries a day, web-search-mojeek about 2,000 a day, web-gdelt-poller up to 720 requests an hour, each returning several results; messages a day are to be measured in the pilot.
- Retention: deduplication rows 180 days after the last sighting; parked URLs 30 days; excerpts in messages follow `news_excerpt`.

## 8. Failure handling and fallback

- The router makes no external call, so the HTTP rules (429, 401, 403) and the empty-200 rule do not apply; its failures are internal.
- Unknown shape or hash mismatch: parked in `review_queue`, never dropped, `schema_unknown` raised.
- Produce failure: nothing is committed; the replay produces the same deterministic `message_id` values, which poster-resolver and the extractor absorb.
- Postgres unavailable: the consumer pauses without committing; `router_lag` fires; no message is lost.
- A message that fails 5 times goes to `dlq.search-hit-router` with an alert; an unparseable URL ends as `unparseable` and is counted, not retried.
- No fallback exists or is needed; a second replica takes over partitions on failure.

## 9. Non-functional requirements

- Throughput: sized for the sum of the producers; to be measured in the pilot; scaling on partition lag.
- Latency: seconds from arrival to routing; p95 measured in the pilot.
- Idempotency: `message_id` is deterministic (`dh:…:<candidate_key>:<canonical_url_hash>`, `au:…:<canonical_url_hash>`); `article.urls` carries `news:article:<canonical_url_hash>`.
- Security: no secrets beyond database credentials from Vault; the router never fetches a URL; logs carry `message_id`, `engine` and outcome, not snippets; Node (TypeScript); the classifier lives in `listening-sdk`.

## 10. Metrics and alerts

`messages_consumed_total{engine}`, `duplicates_total{engine}`, `routed_total{platform,outcome}`, `unroutable_total{reason}`, `already_registered_total{platform}`, `news_registered_total`, `news_parked_total`, `news_released_total`, `web_unrouted_total`, `router_lag`, `route_latency_seconds`, `engine_unique_yield{engine}`, `variant_yield{engine,variant}`, `dlq_total`. Alerts: `router_lag`, `schema_unknown`, `dlq_nonempty`, `unroutable_spike`.

## 11. Dependencies

`listening-sdk`, web-search-perplexity, web-search-mojeek, web-gdelt-poller, yt-web-search-bridge, poster-resolver, news-site-resolver, news-article-extractor, registry-writer (through `source.events`), qualifier, source-health-canary, Redpanda, Supabase Postgres.

## 12. Risks and mitigations

- URL patterns change or are misread: fixtures in the SDK, unknown shapes fall to `web` and are counted, ops reviews a weekly sample.
- Noisy candidates: the re-route window, candidate deduplication, the registry check and reserved paths cut volume; the qualifier applies the Iraqi-signal, type and spam rules.
- Individuals: the router stores only URL hashes, counts and references and never fetches a profile; personal pages that slip through are rejected by the qualifier's type rule, and no individual is profiled.
- A search hit is not a mention: keyword-matcher confirms it on the fetched article or item.
- Short links hide platform links: only `youtu.be` is treated as a platform short link, since the router never follows redirects (open question 1).
- State growth: monthly partitions and 180-day expiry.

## 13. Acceptance criteria

1. The same article arriving from perplexity, mojeek and gdelt with different tracking parameters yields one routed message inside the window, and `search_url_seen` shows 3 sightings and 3 engines.
2. For each row of the 5.3 table at least two fixture URLs give the expected platform, `type` and `candidate_key`, including `youtu.be`, `twitter.com`, `m.facebook.com`, `instagram.com/p/…` and `/reel/…`.
3. `t.me/+abc` and `t.me/joinchat/…` produce no `discovery.hits` and the outcome `unroutable` with reason `private_invite`; `x.com/i/…`, `/search` and `/hashtag/…` produce none.
4. A news URL on a registered domain yields one `article.urls` message with that site's `source_id` and `idempotency_key = news:article:<canonical_url_hash>`; a second sighting yields none.
5. A news-like URL on an unregistered domain yields one `discovery.hits` of type `site` and is parked; when `source.events` adds that domain, the parked URL is released once.
6. A URL that is not news-like on an unregistered domain yields no output and the outcome `web`.
7. Replaying 1,000 messages adds no output and no sightings; with Redpanda down nothing is committed and the outputs appear once it is back.
8. Two workers handling two URLs of one new poster at the same moment emit exactly one `discovery.hits` for that candidate.
9. A candidate already in `sources` yields no `discovery.hits` and increments `already_registered_total`.
10. A message with an unknown schema or a hash mismatch is parked in `review_queue`, not dropped, and raises `schema_unknown`.

## 14. Open questions

1. Instagram profile URLs (`instagram.com/<handle>/`) and platform short links (`fb.watch`, `vm.tiktok.com`, `instagr.am`) are not in the specified list. Proposed: add profile URLs as Instagram accounts and leave short links as `web` while their share is measured.
2. The 30-day re-route window, the 30-day parking period and the news-like rule are set in the pilot.
3. The exact field sets of `discovery.hits` and `article.urls` are to be aligned with poster-resolver and the news services.
4. Should the router feed variant yield back to the engines automatically, to retire variants that never produce Iraqi results? Proposed: metrics only in v1.
