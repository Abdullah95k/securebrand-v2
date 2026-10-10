# news-comments-fetcher

**Platform:** News websites · **Route:** green · **Lane:** Comments · **Owner:** Backend lead, news crawler · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

An article tells a client what an outlet said; the comments under it tell the client how readers reacted. For brands, companies and ministries that reaction is often the point of monitoring: a service outage story with 400 angry replies is a different event from the same story with none. On Iraqi news sites the reader-comment layer, where there is one, is most often Disqus. The Meta Comments plugin, the other common option, was discontinued on 10 Feb 2026, so Disqus is the one comment provider with an API we can read.

news-comments-fetcher reads the Disqus comments of every article on a Disqus site, on a schedule, with threaded replies in the same call, and writes them to `raw.items` as kind `comment` with the commenter hashed. Without it the news stream is one-way: counts and sentiment of reader reaction, and the comment-based alerts that clients expect from every other platform, are missing for news.

## 2. Objective (the end state this service delivers)

Every article on a site whose `comments_provider` is `disqus` has its comments fetched at +6 h, +24 h and +3 d after the article was first seen, extended or stopped by the decay rules, each fetch reading newest-first until it reaches comments already stored, with replies included and commenters stored only as hashes. Target: comment series completed on time for 95% of articles (SLO), zero commenter names, usernames or avatars stored, zero jobs lost, and no request to the publisher's own host.

## 3. Scope

### In scope

- Jobs of kind `comments` (and `ops_force`) on `jobs.news-comments-fetcher`, emitted only by comment-decay-scheduler.
- Resolving the Disqus thread of an article; paging `posts/list`; hashing commenters; content hashes; versions for edits; `deletions` for removed comments.
- Writing `raw.items` kind `comment`; reporting `new_count`, `seen_count`, `pages`, `cost_units`, `thread_id`, `newest_comment_at` to `service_runs` for the scheduler.
- Skipping jobs for hosts whose policy is no longer `allowed`.

### Out of scope

- Emitting jobs and deciding early stop, extension and hot-post extras (comment-decay-scheduler).
- Sites without Disqus (`comments_provider = none`); the discontinued Meta Comments plugin; native on-site comment systems.
- Fetching or extracting articles (news-article-extractor); resolving commenters or building profiles (never done).
- Disqus user profiles, avatars, follower graphs.

## 4. Users and consumers

- **Clients** never call it; they see reader reaction on the articles of outlets they watch, as counts, themes and sentiment, never as named people.
- **Ops** watches series timeliness, Disqus budget burn, and the list of sites whose threads cannot be found.
- **Downstream:** normalize-item (reads `raw.items`), keyword-matcher, the analysis services, store-writer, raw-archiver, deletion-propagator (receives `deletions`), comment-decay-scheduler (reads the results), quota-governor (`news_disqus`), source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.news-comments-fetcher`, partitioned by `source_id`, emitted only by comment-decay-scheduler (this service has no scheduler of its own). A job carries `job_id` (ULID), `source_id`, `kind`, `due_at`, `attempt`, `post_ref` (article item id, canonical URL, `disqus_shortname`, thread identifier or thread id when known, newest stored comment time) and `series_step`.

**Series.** For Disqus sites the profile is: +6 h, +24 h, +3 d after the article is first seen. The general rules of the addendum apply, each applied by comment-decay-scheduler from this service's report: early stop (this service never stops a series itself; ADR-0019); extension (when the last scheduled fetch, at +3 d, still adds 20% or more new comments, the series continues every 2 days until day 30); hot posts (when velocity exceeds 100 new comments an hour, an extra fetch every hour for the next 6 hours). Replies need no separate job: Disqus returns the whole thread, replies included, in the same call. Beyond day 30 no automatic fetch; a client may request a refresh of one article, budget permitting (`ops_force`).

**Thread not yet created.** Disqus creates a thread when the embed first loads, so an unread article has none. A thread not found at +6 h is retried at +24 h; not found at +24 h, the series stops with `no_thread`.

**Keeping the rotation on time.** Jobs are ordered by `due_at`, so a +6 h job is never starved by newer ones. `comment_lag_seconds` is now minus `due_at` of the most overdue job; when it exceeds one hour the service works the most overdue first and raises `comments_behind`. When the `news_disqus` budget passes 80%, quota-governor drops hot-post extra fetches first and never the scheduled steps.

**Onboarding.** A site gets here only after news-site-resolver has recorded `comments_provider = disqus` and the `disqus_shortname` (and an identifier template if the site uses one), news-robots-checker has issued an allowing policy, registry-writer has added the site, and articles have flowed through the extractor. The first job for an article arrives from comment-decay-scheduler 6 hours after the article is first seen.

### 5.2 Step by step

1. Consume a job; read the site's `news_sites` and `crawl_policies` rows; if the policy is no longer `allowed`, cancel the job (the publisher refused our crawler; we do not read its comments either).
2. Ask quota-governor for allowance under `budget_tag = news_disqus`; on wait-until requeue, on deny keep the job and count `quota_denied_total`.
3. Resolve the thread if `thread_id` is not in `post_ref`: by `ident:<identifier>` when the resolver's template yields one, else by `link:<canonical URL>`, else `link:<URL as found>`.
4. Page `posts/list` newest-first with `limit = 100` until a page reaches a comment already stored (by id, or `createdAt` not newer than the newest stored, with one page of overlap), or the cursor is exhausted. The last scheduled fetch of a series reads to the end, so edits and deletions can be compared.
5. For each comment: drop name, username, avatar and profile URL; compute `author_hash`; compute `text_sha256`; build the excerpt; write the full text to the 7-day cache.
6. Compare with stored comments: unseen ids are new; changed `text_sha256` is a new version; on a complete read, stored ids that are missing or flagged deleted become `deletions` (reason `platform_sync`).
7. Produce `raw.items` and the `deletions` messages; after Redpanda acknowledges, write the result row (`new_count`, `seen_count`, `pages`, `cost_units`, `thread_id`, `newest_comment_at`) to `service_runs`.

### 5.3 The call it makes

The Disqus API, one registered application of the company, public API key from the vault (`vendor_keys`). No request goes to the publisher's host, so the news host gate does not apply; the call rate is bounded by the `news_disqus` budget and a per-second cap set in the pilot. The lane's user agent (`ListeningBot/1.0 (+<bot information page>; <contact mailbox>)`) is sent on every request, naming the company and a contact address.

```
GET https://disqus.com/api/3.0/threads/details.json
  ?api_key=<key>&forum=<shortname>&thread=ident:<identifier>   (or thread=link:<canonical URL>)

GET https://disqus.com/api/3.0/posts/list.json
  ?api_key=<key>&forum=<shortname>&thread=<thread_id>
  &order=desc&limit=100&include=approved&cursor=<cursor.next>
```

Pagination: follow `cursor.next` while `cursor.hasNext` is true, stopping at the first page that reaches already-stored comments. Page size 100. Fields read: post `id`, `parent` (null for a top-level comment), `thread`, `raw_message` (plain text; `message` is HTML), `createdAt`, `likes`, `dislikes`, `isDeleted`, `isEdited`, and the author's `id`, `isAnonymous` and `name` for hashing only. Field and parameter names are to be confirmed against live responses in the pilot, as are the key's rate limit and Disqus's terms for reading public comments of forums we do not administer.

Commenter hashing: `author_hash = HMAC-SHA-256(key from Vault, "disqus:" + author id)` for registered commenters; for guests `HMAC-SHA-256(key, "disqus:anon:" + thread id + ":" + name)`, so a guest name is not linkable across threads. The raw identifiers are discarded before anything is produced or logged.

Politeness, permissions and egress rules of the lane (robots.txt under RFC 9309, `Content-Signal`, RSL, HTTP 402, headless and proxy egress) are enforced by news-robots-checker and the fetching services; this service needs none of the egress options, because it talks only to Disqus.

### 5.4 What it gets

Per comment: id, parent id, plain text, creation time, like and dislike counts, edit and deleted flags, and the author fields used for hashing. The excerpt rule applies: a comment of up to 300 characters is within the limit and is stored as it is; a longer one is cut to 300 characters at a word boundary, with the full text in the 7-day cache only. It does not get: commenter identity beyond the hash, moderation-queue comments, comments of sites that do not use Disqus, or anything about the publisher's page.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.news-comments-fetcher`; control-plane `sources`, `news_sites` (provider, shortname, identifier template), `crawl_policies`, `budgets` through quota-governor, `vendor_keys`; stored comment hashes for the article (from the job's `post_ref` and the analytics store through the SDK).

### 6.2 Writes

`raw.items` kind `comment`, one message per new or changed comment. Hosts and ids in the example are illustrative.

```json
{
  "envelope": {
    "platform": "news", "kind": "comment", "route": "green", "vendor": null,
    "service": "news-comments-fetcher",
    "source_id": "3c7f9d52-1e4a-4b86-a0d3-7b2e5c8f1a90",
    "platform_id": "6203918455", "parent_id": "e7a41b09c35d28f6a1d0b94c7e3f5a82d6c1b0e947f3a5d82c6b1e0a49d7f315",
    "idempotency_key": "news:comment:6203918455:v1",
    "job_id": "01J9N4B2X7H1M5T8Q3V6D0RYKE", "attempt": 1, "series_step": "+6h",
    "fetched_at": "2026-10-06T11:52:40Z",
    "retention_class": "news_excerpt",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]
  },
  "payload": {
    "thread_id": "9418273650", "reply_to": null,
    "author_hash": "a9d04f27c18e63b5d0f2a7c41e9b8d36f5a0c2e17b4d9863a1f5c0e72d8b9a64",
    "author_kind": "registered",
    "excerpt": "الخدمة متوقفة في منطقتنا منذ الصباح ولا أحد يرد على الاتصالات",
    "excerpt_chars": 61, "text_sha256": "2c8e5f1a9d047b36e0c1f8a5d3b7e94a6f2c0d1b9e5a7f38c4d6b0a2e8f1d975",
    "text_full_ref": "cache/news/comments/2026/10/06/e7a41b09c35d28f6a1d0b94c7e3f5a82d6c1b0e947f3a5d82c6b1e0a49d7f315-6h.jsonl.zst",
    "created_at": "2026-10-06T10:31:02Z", "likes": 12, "dislikes": 1,
    "is_edited": false, "version": 1
  }
}
```

Also `deletions` (reason `platform_sync`), `service_runs` result rows, `dlq.news-comments-fetcher` after 5 failed attempts.

### 6.3 State

No cursor per source. Per article, the job carries the newest stored comment time and the thread id; the result row returns them to comment-decay-scheduler. Stored comment ids and content hashes live in the analytics store; the HMAC key and API key live in the vault. In memory only backoff state.

## 7. Limits, quotas and cost

- Budget tag `news_disqus`: counters in `budgets`; quota-governor returns allow, wait-until or deny before each batch. One request is one unit (`cost_units`). A budget set to zero is the kill switch for the whole service.
- The key's rate limit, any price, and Disqus's commercial-use terms: to be confirmed in the pilot. The share of the roughly 500 sites that run Disqus, and so the call volume, is to be measured in the pilot.
- Pages: most Iraqi article threads fit in one page of 100, so a fetch is usually one `posts/list` call plus a thread lookup on the first step.
- Hosting: a small container; the whole news lane costs in the low tens of USD a month on Hetzner. Proxy egress (`news_proxy_egress`) is not used here.
- Volume context: about 375,000 articles a month across about 500 domains at about 25 articles a day each; only those on Disqus sites get comment jobs, up to three scheduled fetches each.
- Legal basis: commenters are hashed; excerpts of 200 to 300 characters plus metadata and hashes are stored under Iraqi copyright law (Law No. 3 of 1971); full text only in a 7-day cache (retention class `news_excerpt`); robots.txt and signals are honoured through the policy.

## 8. Failure handling and fallback

- HTTP 429 or a Disqus rate-limit error: exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts to `dlq.news-comments-fetcher` with an alert.
- HTTP 401 and 403: mark the key `degraded`, stop the batch, alert; never rotate keys or IPs to get around a block.
- Thread not found: `no_thread` per 5.1; a forum shortname that Disqus rejects marks the site's comments `degraded` and sends news-site-resolver a `refresh`.
- Empty 200 on a thread known to have comments: counted per route; above 5% in 15 minutes source-health-canary flips `health = degraded`; no amber fallback exists, so `fallback_on` is never set.
- Schema change: raw payload still archived; normalize-item raises `schema_unknown` and parks the batch.
- Partial write: results and cursors are written only after Redpanda acknowledges; a replayed job re-emits the same idempotency keys.
- Budget denied: the job waits; scheduled steps outrank hot-post extras.

## 9. Non-functional requirements

- Throughput: bounded by Disqus-site articles times at most three fetches, plus extensions and hot-post extras; to be sized in the pilot.
- Latency: a fetch runs within one hour of `due_at` for 95% of jobs.
- Idempotency: `news:comment:<disqus post id>` with a version suffix for edits; replayable jobs; append-only `raw.items`.
- Scaling: stateless workers on partition lag.
- Security: API key and HMAC key from Supabase Vault per job, never logged; commenter names, usernames and avatars never leave the process; provenance on every message.

## 10. Metrics and alerts

Standard set: `items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`; plus `comment_lag_seconds`, `series_on_time_ratio`, `no_thread_total`, `comments_per_fetch`, `pages_per_fetch`, `edits_total`, `deletions_total`, `news_disqus_budget_used_ratio`. Alerts: `comments_behind`, `dlq_nonempty`, `key_degraded`, `empty_200_rate`, `budget_80_percent`. SLO: comment series completed on time for 95% of articles.

## 11. Dependencies

`listening-sdk`, comment-decay-scheduler, news-site-resolver, news-robots-checker, news-article-extractor, normalize-item, deletion-propagator, raw-archiver, quota-governor, source-health-canary, Supabase Postgres and Vault, Redpanda, object storage for the 7-day cache.

## 12. Risks and mitigations

- Disqus terms or rate limits restrict third-party reading: confirmed in the pilot before launch; the `news_disqus` budget at zero switches the service off.
- Disqus adoption in Iraq is small or falling: the share is measured in the pilot; the service costs little if so.
- Hashing is reversible by guessing names: keyed HMAC with a vault key, never a bare hash.
- Comments quote articles at length: the 300-character excerpt cap and the 7-day cache apply to comments too.

## 13. Acceptance criteria

1. For an article first seen at 06:00, jobs are due at 12:00, 06:00 the next day and 06:00 three days later; each is executed within one hour of `due_at` in a fixture run.
2. A fetch reports its new comments and the comments stored before it and cancels no step itself, comment-decay-scheduler applying early stop (ADR-0019); a +3 d fetch adding 20% or more extends the series every 2 days to day 30.
3. A fixture thread of 250 comments with 60 stored is paged newest-first and stops at the first page reaching a stored comment; the last scheduled fetch reads to the end.
4. Replies arrive in the same call with `parent` set; no separate reply job exists.
5. No output field, log line or message contains a commenter name, username, avatar or profile URL; guest hashes differ between two threads for the same name.
6. A comment edited upstream yields a new version (`:v2`); a comment missing on a complete read yields a `deletions` message with reason `platform_sync`.
7. A comment of 500 characters is stored with a 300-character excerpt and its full text only in the 7-day cache.
8. A thread not found at +6 h is retried at +24 h and the series stops with `no_thread` if still absent.
9. A 429 triggers backoff from 30 s to at most 15 min with `attempt + 1`; after 5 attempts the job is in `dlq.news-comments-fetcher`; a 401 marks the key `degraded` and no further call uses it.
10. With the `news_disqus` budget at 85% used, hot-post extras are dropped and scheduled steps still run; at zero, no request is made.
11. A job for a host whose policy has turned `disallowed` is cancelled without a Disqus call.

## 14. Open questions

1. Disqus API terms for reading comments of forums we do not administer, the key's rate limit, and any price: to be confirmed in the pilot.
2. What share of Iraqi news sites use Disqus: to be measured in the pilot; if small, the series could be restricted to tier 1 sites.
3. Does the extractor capture `disqus_identifier` from the page so the thread lookup never needs the URL form? Proposed: yes, as an optional payload field.
4. HMAC key rotation: rotation breaks linkability of commenter hashes across time; proposed policy to be decided with counsel.
