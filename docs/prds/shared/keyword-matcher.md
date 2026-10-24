# keyword-matcher

**Platform:** Shared · **Route:** shared · **Lane:** Processing · **Owner:** Backend lead (processing) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A client does not want 1,000,000 posts a day; it wants the few that mention its brand, its service or its competitors. keyword-matcher is the point where a normalized item becomes a mention for a client. It tests every item on `items.normalized` against the keyword set of each client entitled to see it, in Arabic spellings, Kurdish forms, brand handles and hashtags, minus the client's exclusions, and writes one hit per client and keyword.

It is also where the registry grows: a hit on a post by a poster we do not track yet is the signal poster-resolver and the qualifier use to find new sources. And it is the gate that decides which client may see which item: client-owned data stays with its client, and government clients never receive amber data.

Without it nothing is counted, nothing is alerted, no source is discovered, and every consumer would match keywords its own way.

## 2. Objective (the end state this service delivers)

End state: every item on `items.normalized` is matched, within 60 s of normalization, against the active keyword set of every client entitled to it, and each (item, client, keyword) match exists once as an `active` hit on `item.hits` or `discovery.hits`, retracted when the text or the keywords change.

Measurable target: p95 normalization-to-hit latency below 60 s at about 1,000,000 items a day (about 12 a second on average, peaks to be measured in the pilot); 100% of consumed items accounted for (hit, no_hit or skipped); zero hits that breach the client gate (5.3 D); precision and recall on the labelled keyword fixtures reported per release, gates set from the pilot sample (to be measured in the pilot).

## 3. Scope

### In scope
- One Aho-Corasick automaton per client keyword set, compiled from the `keywords` table (Arabic variants, Kurdish forms, brand handles, hashtags, exclusions), matched on `text_norm`.
- Rebuild on keyword change with versioning; `rematch` jobs for history; retraction of hits that stop matching.
- The client gate; routing to `item.hits` or `discovery.hits`; the candidate block for poster-resolver; `sources.last_hit_at`.

### Out of scope
- Normalization and folding (normalize-item, lang-dialect-id); the keyword editor and its approval flow (React app, n8n); poster resolution and qualification (poster-resolver, qualifier); sentiment, topics, entities; matching text inside images or audio (analysis-media); web-search queries (the search services); counting and alerting (aggregator, alert-evaluator).

## 4. Users and consumers

- poster-resolver consumes `discovery.hits`; the qualifier reads the hit context (keyword, client, URL) from the profile.
- store-writer writes both hit topics to the ClickHouse `hits` table; aggregator and alert-evaluator count from it.
- registry-writer owns the registry; this service writes only `sources.last_hit_at`, which the qualifier's decay rule reads.
- Account managers see matched terms and offsets in the client app; ops read parked items and run `rematch` jobs.

## 5. How it works

### 5.1 Trigger and rotation

Trigger: topic `items.normalized`, consumer group `keyword-matcher`. Partitions follow normalize-item's key, `source_id` (ADR-0004), so one worker sees one source's items in order; offsets commit after Redpanda acknowledges the hit batch, and a replayed batch yields identical hits. No rotation. Control inputs: the `keywords` and `clients` tables are polled every `KEYWORD_POLL_SECONDS` (default 30) for a changed `updated_at`; `source.events` keeps the registry cache current. x-recent-search and tg-message-search may emit an early `discovery.hits` for the same candidate; poster-resolver deduplicates by `candidate_key`, so both paths are safe.

Replay: a new `lang_model_version` (fold change), a new matcher rule version or a bulk keyword change is re-run from the archive. Ops starts a replay of the affected days through raw-archiver's replay path (the one normalize-item uses); items return on `items.normalized` as new versions and are matched again, rate-capped. Hits are keyed by `hit_id`, so stores upsert. A single keyword edit uses a `rematch` job instead (5.3 H).

### 5.2 Step by step

1. Pull a batch (up to 500 items or 2 s); skip items with empty `text_norm`.
2. Resolve the automaton set for each item's `lang_model_version`; a version seen for the first time is compiled before the batch continues.
3. Select candidate clients with the gate (5.3 D).
4. Scan `text_norm` with each candidate client's automaton; apply boundary and exclusion rules (5.3 C).
5. For items with `version > 1`, read the item's existing hits from ClickHouse and mark pairs that no longer match `retracted`.
6. Route each hit (5.3 E); for `discovery.hits`, read the candidate identity from the raw record.
7. Publish; update `last_hit_at` (coalesced); commit offsets.

### 5.3 The call it makes (the processing it performs)

**A. Keyword model.** `keywords` columns read (proposed here): `keyword_id`, `client_id`, `label`, `forms` (jsonb array of `{form_id, text, lang: ar|ckb|en, kind: term|handle|hashtag, boundary: clitic|word|exact}`), `exclusions` (array of `{text, lang}`), `purpose`, `enabled`, `version`, `updated_at`, `rematch_days`. Handles keep their `@`, hashtags their `#`.

**B. Compile.** One automaton per client set. Every form is folded with lang-dialect-id `/v1/fold` (the SDK's identical TypeScript fold if the service is down) under both the Arabic and the Sorani fold; a Latin-only form folds alike and is stored once. So a keyword typed with Arabic letters matches a Sorani text and the reverse, and the folds cannot cross-match because they never produce the same ك/ک or ي/ی. Patterns carry `keyword_id`, `form_id`, `boundary`. Exclusions are folded the same way. A set is built per `lang_model_version` and identified by `keyword_set_version` = hash of (`keyword_id`, `version`, `enabled`) over the client's keywords, rendered `cs:<hex>` (ADR-0070). A new set replaces the old one between batches; the old one stays until the replay ends.

**C. Scan.** One linear pass over `text_norm` per candidate client, then a boundary test per match:
- `word` (Latin, digits): neighbours must not be letters, digits or `_`.
- `clitic` (default for Arabic script): start at a token start or after proclitics `و ف ب ل ك ال` and chains of them (وبال); end at a token end or before one suffix from `ه ها هم هن ك كم كن ي نا ات ان ين ون`. So `زين` hits "زين" and "بزين" but not "زينب".
- `exact`: the whole token only (handles, hashtags).

A keyword is suppressed for the item when any of its exclusion forms occurs (same boundary rules). Otherwise one hit per (item, client, keyword): `matched_term` is the longest matching form as the client wrote it, `occurrences` the count, `offsets` the `[start, end)` code-point spans in `text_norm`.

**D. Client gate (before the scan).** Candidate clients are those with an active set, then:
1. Items from `owned_by_client` sources, and items with `retention_class` `meta_on_request` or `linkedin_48h`, go only to clients listed in the source's `client_ids` (platform data is processed on behalf of the client it was fetched for).
2. Government clients (`clients.client_type = government`) get no hit on `route = amber` items, none on X items unless `clients.x_enterprise = true`, and only keywords with `purpose` `reputation` or `service_quality` are compiled for them (others are refused and counted). A client row missing these fields fails closed.
3. Everything else is the shared pool: every client with an active set.

**E. Routing and identity.**
- `author.author_type = source` goes to `item.hits` with `poster = {author_source_id, author_ref}`.
- An unregistered post-like item (post, video, article, message, result) with a non-null `author_ref` goes to `discovery.hits` with a `candidate` block. normalize-item hashes authors, so `platform_id` and `handle` are read from the raw record at `raw_ref` with the SDK's per-platform extractor; `candidate_key` is `<platform>:<platform_id>` or `<platform>:<handle>`. If the raw object is not readable yet, the hit is sent at once with `candidate_pending = true` and a `candidate_retry` job on `jobs.keyword-matcher` (30 s to 15 min backoff, 5 attempts) re-sends it with the same `hit_id`.
- Comments, replies and items with a null `author_ref` go to `item.hits` with `poster = {author_ref, author_type: "individual"}`: a mention, never a candidate (qualifier rule 7).

**F. Identity of hits.** `hit_id = uuid_v5(ns_hits, "<item_id>:<client_id>:<keyword_id>")`; `message_id` is a ULID whose time part is `hit_at` and whose random part is the first 10 bytes of SHA-256 over `hit_id`, `item_version` and `keyword_set_version`, so a replay reproduces it (ADR-0006, ADR-0070). `hit_at` is the item's `created_at`.

**G. `last_hit_at`.** `sources.last_hit_at = greatest(current, hit_at)` for the item's `source_id` and its `author_source_id`, coalesced to one write per source per minute. Backfills and replays cannot refresh decay.

**H. Rematch.** A `jobs.keyword-matcher` job (`kind = rematch`: `client_id`, `keyword_ids`, window from `rematch_days`) pages ClickHouse `items` and `comments` by month partition, runs the new automaton, emits new hits and retracts hits (read from `hits`) that no longer match, with progress in `cursors`. Disabling or deleting a keyword retracts its history.

### 5.4 What it gets

Per item: identity, `kind`, `source_id`, `author`, `text_norm`, `lang_model_version`, `version`, provenance, `retention_class`, `raw_ref`. It does not get author names or handles (hashed upstream), full article text, or text in media. A hit carries no item text, only the matched term and offsets.

## 6. Inputs and outputs

### 6.1 Reads
- Topics: `items.normalized`, `source.events`, `jobs.keyword-matcher` (`rematch`, `candidate_retry`).
- Control plane: `keywords`, `clients`, `sources` (cache), `cursors`, `service_runs`.
- lang-dialect-id `/v1/fold`; ClickHouse `hits`, `items`, `comments`; the raw archive through the SDK reader.

### 6.2 Writes
`item.hits` (key `source_id`, the source that produced the item) and `discovery.hits` (key `candidate_key`; ADR-0004, ADR-0031), `jobs.keyword-matcher`, `dlq.keyword-matcher`; `sources.last_hit_at`. In the example, `message_id`, `producer.job_id` and `keyword_set_version` follow ADR-0006 and ADR-0070; where its other fields differ from an ADR, the ADR wins (ADR-0001, ADR-0031):

```json
{
  "schema": "discovery.hits/v1",
  "message_id": "01M486JMB0K5QZM1RWBPZ5NJ95",
  "produced_at": "2026-10-06T09:14:41Z",
  "producer": {"service": "keyword-matcher", "version": "1.0.0", "job_id": "01M4871WM0NJ5SWYGET3ZGFGSP"},
  "hit_id": "b7e1c9d4-2a53-5f08-9c61-3d4e5f6a7b8c", "status": "active",
  "item_id": "6f1d2c3e-9a4b-5c6d-8e7f-0a1b2c3d4e5f", "item_version": 1,
  "platform": "x", "kind": "post", "source_id": "c41b7a90-3d2e-4f5a-8b6c-7d8e9f0a1b2c",
  "client_id": "e2a9d0b1-6c7f-4a38-9d5e-0f1a2b3c4d5e", "keyword_id": "9a8b7c6d-5e4f-4321-a0b9-c8d7e6f5a4b3",
  "keyword_set_version": "cs:3f9a1c", "lang_model_version": "lid-iq-2026.09",
  "matched_term": "زين العراق", "form_id": "f2", "occurrences": 1,
  "offsets": [[5, 15]], "offsets_in": "text_norm",
  "hit_at": "2026-10-06T08:51:40Z", "url": "https://x.com/iraqi_outlet/status/1",
  "candidate": {"candidate_key": "x:1234567890", "platform": "x", "platform_id": "1234567890", "handle": "iraqi_outlet", "author_ref": "hmac:9c1f…"},
  "candidate_pending": false,
  "route": "green", "vendor": null, "service": "x-recent-search",
  "retention_class": "x_24h_sync", "expires_at": null,
  "raw_ref": "raw/green/x/2026/10/06/x-recent-search/0042.jsonl.zst#310"
}
```

The matched text was "خدمه زين العراق ضعيفه اليوم". An `item.hits` message is identical except that `candidate` and `candidate_pending` are replaced by `poster`.

### 6.3 State
Compiled automata per client and `lang_model_version`; keyword and client caches with their `updated_at` marks; the registry cache (last `source.events` offset); the `last_hit_at` coalescing buffer; offsets; rematch progress in `cursors` (`service = keyword-matcher`, `cursor = rematch:<job_id>:<last month, last item_id>`).

## 7. Limits, quotas and cost

No external API or vendor is called: no `budget_tag`, no quota-governor round trip. Cost is cluster CPU and memory for the automata, plus ClickHouse reads for retractions and rematch. Scan cost grows with items times candidate clients times text length; at 12 items a second one worker is enough in principle, three replicas run for partition spread and failover, and the pool scales on consumer lag. Memory per set, client count and peak rates are to be measured in the pilot. Rematch jobs are throttled and run against ClickHouse off-peak. Hetzner pricing in USD is confirmed at order time.

## 8. Failure handling and fallback

- lang-dialect-id down at compile: the SDK fold compiles instead; the conformance suite keeps both identical.
- Bad keyword row: the client's previous automaton stays, the row is quarantined, an alert fires; other clients are unaffected.
- Raw record unreadable: `candidate_pending` flow (5.3 E); after 5 attempts `candidate.platform_id` stays null and `candidate_missing_total` counts it.
- ClickHouse unavailable for retraction lookups: retry with backoff; after 5 minutes emit active hits without retractions and count `retract_degraded_total`; a later replay reconciles.
- Stale registry cache: an author registered a moment ago is routed to `discovery.hits`; poster-resolver drops hits whose poster is already registered.
- Produce failure: offsets stay uncommitted; a poison item (5 failed attempts) goes to `dlq.keyword-matcher` with an alert.
- Missing gate fields: fail closed for government clients, alert.

## 9. Non-functional requirements

- Throughput: about 12 items a second on average at full scale; peaks and items a second per worker to be measured in the pilot.
- Latency: normalize within 60 s of fetch, matching within 60 s of normalization (this service), analysis within 15 min for tier-1 sources, alerts within 5 min of the aggregate update. A keyword change applies within the poll interval plus compile time.
- Idempotency: `hit_id` and `message_id` are deterministic; the same item version and set version produce the same message; stores upsert.
- Scaling: one consumer group, stateless apart from in-memory automata; replicas rebuild them at start.
- Security: no item text in logs; candidate identity exists only in `discovery.hits` (Redpanda retention, days), never in ClickHouse, `item.hits` or logs; TLS inside the cluster. Node (TypeScript); matching rules in `listening-sdk`.

## 10. Metrics and alerts

Prometheus: `items_in_total{result=hit|no_hit|skipped}`, `hits_out_total{topic,status}`, `match_latency_seconds`, `consumer_lag_seconds`, `keyword_set_age_seconds`, `compile_seconds`, `suppressed_total{reason}`, `gate_blocked_total{reason}`, `keyword_refused_total`, `candidate_missing_total`, `retract_degraded_total`, `dlq_total`. Alerts: lag above 60 s for 5 minutes; `keyword_set_age_seconds` above poll interval plus compile time; any `gate_blocked_total` for a missing field; `candidate_missing_total` rising for 10 minutes; DLQ non-empty.

## 11. Dependencies

normalize-item, lang-dialect-id, `listening-sdk`, Redpanda, Supabase Postgres, ClickHouse (`hits`), raw-archiver (archive reader and replay), registry-writer (`source.events`); consumers poster-resolver, store-writer, aggregator, alert-evaluator, qualifier.

## 12. Risks and mitigations

- Arabic clitics and short brand names (زين against زينب, Asia against Asiacell): boundary classes, per-keyword exclusions, `exact` for handles; recall measured on pilot fixtures; a morphological analyser can later sit behind the boundary test.
- A fold change silently changes matches: automata are built per `lang_model_version`.
- Gate misconfiguration breaches a contract: fail closed, an acceptance test, a weekly audit query on `hits` for government clients.
- Fan-out cost grows with clients: one union automaton with client filtering is the planned optimisation; measured in the pilot.
- Candidate identity leaking: confined to one topic with days of retention; hits carry no text.
- Rematch load on ClickHouse: throttled, partition by partition.

## 13. Acceptance criteria

1. Fixtures pass for each form class: an Arabic variant (البصرة and البصره), a Kurdish form, a handle (`@zain_iraq`), a hashtag, and an exclusion that suppresses the hit.
2. `زين` hits "اشتراك زين شهري" and "بزين" and does not hit "زينب"; Latin `ali` does not hit inside "alibaba".
3. A keyword typed with Arabic letters hits a Sorani text typed with Kurdish letters, and the reverse.
4. A registered-source post yields `item.hits`; an unregistered post yields `discovery.hits` with `candidate_key`; a comment by an unregistered author yields `item.hits` with `author_type = individual` and never `discovery.hits`.
5. An item from an `owned_by_client` source yields hits only for clients in `client_ids`; a government client gets no hit on an `amber` item and none on an X item without `x_enterprise`.
6. The same item version processed twice yields identical `hit_id` and `message_id`, and `hits` holds one row per (item, client, keyword).
7. Item `version = 2` whose text lost the keyword yields a `retracted` hit for that triple; one that kept it yields the same `hit_id` with new offsets.
8. A keyword added in `keywords` hits new items within the poll interval plus compile time, and its `rematch` job emits hits for the window; deleting it retracts its history.
9. At a synthetic 50 items a second for 10 minutes with the fixture keyword sets, p95 normalization-to-hit latency stays below 60 s with three replicas.
10. A raw object unreadable for the first attempt yields a hit with `candidate_pending = true`, then the same `hit_id` re-sent with the candidate filled.
11. After a hit, `sources.last_hit_at` equals the item's `created_at` for the source and the registered author, and replaying older items never moves it back.
12. A new `lang_model_version` triggers a compile before the first item of that version is matched.

## 14. Open questions

1. CONVENTIONS lists no hits table. This PRD assumes store-writer fills a ClickHouse `hits` table from both hit topics (see store-writer); confirm.
2. normalize-item hashes authors, so candidate identity is read from the raw archive through `raw_ref`. Confirm raw-archiver makes objects readable within the 60 s target, or add a transient candidate field to normalize-item. poster-resolver must treat `candidate_pending = true` as mention-only.
3. Comment hits by unregistered authors go to `item.hits`, not `discovery.hits` (individuals are never candidates). Confirm.
4. May Meta-origin items be fanned out to clients outside `client_ids` (shared pool)? The draft says no.
5. Default `rematch_days` (30 or 90) and whether exclusion changes also rematch history.
6. Does the clitic and suffix list need a morphological analyser before launch, or do the pilot fixtures settle it?
