# news-dedup

**Platform:** News websites · **Route:** green · **Lane:** Processing · **Owner:** Backend lead, processing pipeline · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

One press statement from a ministry can appear on forty Iraqi sites within the hour, and a wire story is often republished word for word with only the dateline changed. If the product counted every copy as a separate story, a single announcement would look like forty events: mention counts, share of voice and alert thresholds would all be inflated, and a client's dashboard would repeat the same headline forty times. If it threw the copies away, it would lose the one thing a client also wants to know: which outlets carried the story.

news-dedup groups the copies into one story. It matches articles by canonical URL and by a simhash of the excerpt, marks every later copy as a duplicate, keeps the earliest publisher as the origin, and passes the verdict to normalize-item, so that every normalized news item carries `story_id`, `is_origin` and `duplicate_of`. Without it the news stream is correct item by item and wrong in every count.

## 2. Objective (the end state this service delivers)

Every article that reaches `raw.items` as kind `article` is assigned to exactly one story, within minutes, with one origin per story (the earliest publisher), all copies kept and marked, and verdicts corrected when a late article changes the origin or bridges two stories. Target: a verdict for 99% of articles within 5 minutes of the article reaching `raw.items`; zero stories with two origins; replaying any message changes nothing; no article text stored by this service.

## 3. Scope

### In scope

- Consuming `raw.items` (platform `news`, kind `article`) in its own consumer group.
- Canonical-URL matching and simhash matching of the excerpt; story creation, joining, merging; origin selection and origin flips.
- Writing the verdict to `news_story_members` and `news_stories` and publishing it on `news.dedup` for normalize-item; publishing `story_update` when a verdict changes.
- An hourly reconciliation sweep that repairs fragments and adds same-canonical copies the extractor recorded but did not emit.

### Out of scope

- Fetching and extraction (news-article-extractor); normalisation (normalize-item); keyword matching (keyword-matcher).
- Matching across languages (a translation is a different story) and rewrites that share meaning but not wording.
- Deleting duplicates: they stay in the product, marked, so outlet-level reach is preserved.
- Deduplicating anything other than news articles; comments are not clustered.

## 4. Users and consumers

- **Clients** experience it as one story with "also published by N outlets", unique-story counts, and the origin outlet named.
- **Ops** watches cluster sizes, merge and flip rates, and can split a wrongly merged story.
- **Downstream:** normalize-item (attaches `story_id`, `is_origin`, `duplicate_of`), store-writer and aggregator (count stories and mentions separately), alert-evaluator (alerts on unique stories, not copies), keyword-matcher (matches each copy, since each outlet's mention counts), raw-archiver.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** Every `raw.items` message with `platform = news` and `kind = article`, read by this service's consumer group. It is a stream consumer: there is no site rotation here. The rotation that keeps every registered site checked for new articles belongs to the finders (feeds every 5 to 15 minutes for hot sites and hourly for the rest, news sitemaps hourly, homepage and section diff hourly), and the extractor feeds this service, so a story's copies arrive in the order the sites are polled.

**Ordering and races.** `raw.items` is partitioned by `source_id`, so two copies of one story arrive on different partitions and may be processed at the same moment. The service therefore inserts the member row first, then searches for neighbours excluding itself, and resolves every disagreement by one deterministic order: earliest origin time, then earliest `fetched_at`, then the smaller `canonical_url_hash`. Both racing workers converge on the same story whatever the interleaving. The hourly sweep re-reads the last window and repairs any fragment that still slipped through.

**Catch-up.** `dedup_lag_seconds` is now minus the article's `fetched_at` at the time of the verdict. When it exceeds the 5-minute target the autoscaler adds workers on partition lag and `dedup_behind` fires. A message that arrives late changes verdicts only through the correction path (5.2, step 7), never by being skipped.

**Onboarding.** Nothing to onboard: a new site's articles are clustered as soon as the first one reaches `raw.items`, after news-site-resolver, news-robots-checker and the extractor have done their work.

### 5.2 Step by step

1. Consume an article message; read `canonical_url`, `title_sha256`, `text_sha256`, `excerpt`, `published_at`, `language` and the envelope's `source_id`, `idempotency_key`, `fetched_at`. A member row for this `idempotency_key` already exists: re-publish its stored verdict and stop (replay).
2. Compute the story canonical key from `canonical_url` (5.3) and the 64-bit simhash of the normalised excerpt.
3. Compute `origin_time`: `published_at` when it is present and not later than `fetched_at`, otherwise `fetched_at`.
4. Insert the member row (`idempotency_key`, `source_id`, `canonical_key`, `simhash` and its four 16-bit blocks, `title_sha256`, `text_sha256`, `language`, `origin_time`, `fetched_at`).
5. Find neighbours within the lookup window: members with the same `canonical_key`, the same `text_sha256`, or a block equal to ours whose full simhash is within the maximum Hamming distance and whose title token overlap passes the threshold (both set in the pilot); same language only.
6. No neighbour: create a story (`story_id` ULID), this article is the origin. Neighbours in one story: join it. Neighbours in several stories: merge them into the one with the earliest origin, which keeps its `story_id`.
7. Choose the origin (the member with the earliest `origin_time`, tie-break as above). If the origin changed, or a merge moved members, publish `story_update` for every member whose verdict changed.
8. Write the verdict to `news_story_members` and `news_stories`; publish it on `news.dedup`.

### 5.3 The call it makes

No external call. Internal reads and writes on Supabase Postgres and Redpanda; no request to any news host, so the lane's user agent, host gate, robots.txt, `Content-Signal`, RSL, HTTP 402 and egress rules do not apply here; they were applied upstream, and this service sees only what the extractor was allowed to emit.

**Canonical URL key.** The extractor's canonical URL is normalised further: https scheme, lowercase host with a leading `www.` removed, default ports and fragments dropped, tracking parameters removed, remaining parameters sorted, trailing slash removed except at the root, and Arabic slugs converted to one form (UTF-8 percent-encoded, uppercase hex, NFC). The key is `sha256` of the result. A cross-host canonical, a copy that declares the origin's URL as canonical, maps to the origin's key, so copies the extractor did not emit (it records them as `duplicate_canonical`) are added as members by the hourly sweep from the `news_urls` ledger.

**Simhash of the excerpt.** Input is the stored excerpt (200 to 300 characters), never the full text. Normalisation: Unicode NFKC; remove diacritics (tashkeel) and tatweel; fold alef variants to bare alef, alef maqsura to ya; Arabic-Indic digits to ASCII; strip URLs, punctuation and emoji; lowercase Latin letters; strip a leading dateline (a city or agency name before the first dash or slash within the first 40 characters). Tokenise on whitespace, form 3-word shingles, hash each with a 64-bit hash (xxHash64), and combine by weighted bit votes into a 64-bit simhash. For excerpts under a minimum word count set in the pilot the service relies on the title hash and canonical key only.

**Candidate lookup.** The simhash is split into four 16-bit blocks; two hashes within Hamming distance 3 share at least one identical block, so the lookup is four indexed probes on `news_story_members` restricted to the lookup window (set in the pilot). The maximum distance, the title-overlap threshold and the window length are to be tuned in the pilot against a hand-labelled sample of Iraqi wire stories.

**Origin.** The earliest publisher: the member with the smallest `origin_time`. A `published_at` after `fetched_at` is treated as untrustworthy and replaced by `fetched_at`. "Earliest" means earliest seen when the site's own date is missing or wrong, and the product says so.

### 5.4 What it gets

Per article: canonical URL, title hash, text hash, excerpt, publication time, language, source id and fetch time, all from the extractor's message. It does not get full text (the 7-day cache is not read), images, comments, or any article from a host the policy forbids. Matching is by wording: a translation, or a rewrite that shares no phrasing, is a different story.

## 6. Inputs and outputs

### 6.1 Reads

`raw.items` (news articles); control-plane `news_story_members`, `news_stories`, `news_urls` (hourly sweep, read-only), `sources` (publisher names for `origin_source_id`).

### 6.2 Writes

`news.dedup` (partitioned by `story_id`), one message per verdict and per `story_update`; `news_story_members` and `news_stories` rows; `service_runs`; `dlq.news-dedup`. Hosts and ids in the example are illustrative.

```json
{
  "schema": "news.dedup/v1",
  "type": "verdict",
  "idempotency_key": "news:article:b81c3e5f0a2d7946e1f0c8a5d3b9e72f46a1c0d8e5b3f97a2c4d6e0b1a8f5c39",
  "story_id": "01J9N4W6C2R8T5K1V7X3M0DPZA",
  "is_origin": false,
  "duplicate_of": "news:article:e7a41b09c35d28f6a1d0b94c7e3f5a82d6c1b0e947f3a5d82c6b1e0a49d7f315",
  "origin_source_id": "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90",
  "origin_time": "2026-10-06T05:41:00Z",
  "cluster_size": 5, "rank_in_cluster": 3,
  "matched_by": "simhash", "hamming_distance": 2, "title_overlap": 0.83,
  "source_id": "a82e1c47-5d3b-49f0-8e6a-2c9b7d1f0e35",
  "dedup_version": 1, "decided_at": "2026-10-06T06:07:44Z",
  "service": "news-dedup"
}
```

A `story_update` has the same shape with `type = "story_update"` and `previous_story_id` or `previous_origin` set. normalize-item copies `story_id`, `is_origin` and `duplicate_of` onto the normalized item and re-emits the story fields as a new version when an update arrives.

### 6.3 State

`news_stories` (`story_id`, `origin_key`, `origin_source_id`, `origin_time`, `cluster_size`, `first_seen_at`, `last_member_at`, `merged_into`); `news_story_members` (`idempotency_key` primary key, `story_id`, `source_id`, `canonical_key`, simhash and blocks, `title_sha256`, `text_sha256`, `language`, `origin_time`, `fetched_at`, `role`, `matched_by`, `hamming_distance`), index on each block plus `fetched_at`; consumer offsets. Only hashes and ids are stored, never text; rows leave the lookup index after the window and are pruned after a period set in the pilot.

## 7. Limits, quotas and cost

- No external quota and no vendor. Volume is about 375,000 articles a month across about 500 domains at about 25 articles a day each, roughly 12,500 a day: four index probes per article, trivial for Postgres.
- Hosting: one small Node container (TypeScript) in the cluster; the whole news lane costs in the low tens of USD a month on Hetzner. Table growth is bounded by the pruning period, to be set in the pilot.
- `news_proxy_egress` and `news_disqus` are not used here.
- Legal basis: the service reads only the stored excerpt of 200 to 300 characters, metadata and hashes, and stores only hashes and ids; full text stays in the extractor's 7-day cache (retention class `news_excerpt`) under Iraqi copyright law (Law No. 3 of 1971); robots.txt and signals were honoured upstream.

## 8. Failure handling and fallback

- Postgres unavailable or lock contention: retry with exponential backoff and jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts to `dlq.news-dedup` with an alert. The article is still in `raw.items`, so normalize-item proceeds with a null verdict and the verdict arrives later as a `story_update`.
- Excerpt missing or too short: cluster on canonical key and title hash only; counted as `dedup_weak_input`.
- Malformed message or unknown schema version: parked with `schema_unknown`; the raw record stays archived.
- Partial write: the member row is idempotent on `idempotency_key`; a replay re-publishes the stored verdict and creates nothing.
- Wrong merge found by ops: a split command re-assigns the members and publishes `story_update` for each; the decision is logged in `decisions`.
- No amber fallback exists or is needed.

## 9. Non-functional requirements

- Throughput: about 12,500 articles a day on average at full scale, with headroom for a backfill burst of the 90-day archive of new sites.
- Latency: a verdict within 5 minutes of the article reaching `raw.items` for 99% of articles.
- Idempotency: one member row per `idempotency_key`; deterministic ordering; replayable.
- Scaling: stateless workers on partition lag; the sweep runs as a leader-elected hourly job (Postgres advisory lock).
- Security: hashes and ids only; no text in logs; provenance carried from the envelope.

## 10. Metrics and alerts

Standard set: `items_fetched_total` (articles read), `items_new_total` (stories created), `jobs_total{status}`, `staleness_seconds_p95`, `dlq_total`; plus `dedup_lag_seconds`, `stories_total`, `cluster_size` histogram, `matches_total{matched_by}`, `merges_total`, `origin_flips_total`, `story_updates_total`, `dedup_weak_input_total`, `sweep_repairs_total`. Alerts: `dedup_behind`, `dlq_nonempty`, `merge_rate_high` (a sudden rise suggests a bad threshold or template spam), `origin_flip_rate_high`.

## 11. Dependencies

`listening-sdk`, news-article-extractor, normalize-item, raw-archiver, store-writer, aggregator, alert-evaluator, keyword-matcher, source-health-canary, Supabase Postgres, Redpanda.

## 12. Risks and mitigations

- False merges on templated text (sports results, Eid greetings, official notices): the title-overlap condition, the same-language condition, hand-labelled tuning in the pilot, `merge_rate_high` alert and ops split.
- False splits on rewritten copies: accepted; counts err on the side of showing more stories, never fewer.
- The earliest publisher we saw is not always the true origin (an aggregator may be crawled before the source): the product says "earliest seen"; hot-site feed intervals of 5 to 15 minutes keep the error small.
- Unreliable site dates: future-dated or missing `published_at` is replaced by `fetched_at`.
- Hand-off with normalize-item is new: see open question 1.

## 13. Acceptance criteria

1. Two articles with the same canonical key, including a cross-host canonical, join one story; the earlier is the origin.
2. A fixture wire story republished by three outlets with a different dateline and one edited word lands in one story; an unrelated story from the same agency with the same dateline stays separate.
3. Excerpts that differ only in diacritics, alef variants, ya forms or Arabic-Indic digits produce the same simhash.
4. An article published at 10:00 and crawled after one published at 10:30 becomes the origin; a `story_update` marks the 10:30 article as a duplicate.
5. A future-dated or null `published_at` is replaced by `fetched_at` for the origin decision.
6. Two near-identical articles processed concurrently on different partitions end in one story in 100 shuffled runs.
7. An article bridging two stories merges them into the one with the earlier origin, which keeps its `story_id`; every moved member gets a `story_update`.
8. Replaying one `raw.items` message creates no new member or story and re-publishes the identical verdict.
9. Duplicates are marked, not dropped: every copy stays on `raw.items` and reaches normalize-item with `duplicate_of` set, and exactly one member per story has `is_origin = true`.
10. Articles in different languages never cluster.
11. No table or message of this service contains excerpt or full text; only hashes and ids.
12. With the hourly sweep, a copy recorded by the extractor as `duplicate_canonical` appears as a member of the origin's story.

## 14. Open questions

1. The hand-off to normalize-item is proposed as the table `news_story_members` plus the topic `news.dedup` (one topic added to the Redpanda list) with a bounded wait in normalize-item; if normalize-item prefers a table-only join, the topic is dropped.
2. Maximum Hamming distance, title-overlap threshold, minimum excerpt length and lookup window: to be tuned in the pilot on a hand-labelled sample; proposed starting window is 7 days.
3. Should the extractor emit cross-host canonical copies as ordinary `raw.items` so the sweep is unnecessary? Proposed: keep the ledger-based sweep, so `raw.items` stays one message per canonical URL.
4. Should unique-story and mention counts both be first-class in aggregator? Proposed: yes, with `is_origin` as the story flag.
