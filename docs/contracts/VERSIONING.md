# Contract versioning

Written by F2 from ADR-0002 and the answer to Q1 in `docs/plans/F2.md`. Every change to `packages/contracts` follows it (`.claude/rules/contracts.md`). Where a line is F2's reading of an ADR rather than the ADR's own words, it says so and names the finding of the orchestrator's check that asked for it (F-nn).

## Every message names its schema

- Every message carries `schema`, `message_id` (a ULID), `produced_at` and `producer {service, version, job_id}`, and the SDK stamps all four (ADR-0002). `schema` is `<topic>/v<n>` on a topic and `job/v<n>` on every job queue. A dead-letter topic's records carry `dlq.<service>/v1`: one shared definition whose `schema` is a pattern, so `dlq.normalize-item/v1` is read as the schema id `dlq.<service>/v1` (Q5, F-52). An n8n notice carries `n8n.alert/v1` or `n8n.card/v1` (ADR-0067).
- Times in messages are RFC 3339 in UTC with `Z`, seconds required, up to three fractional digits (F2's choice). Key and hash inputs render a time as exactly `YYYY-MM-DDTHH:MM:SSZ` (ADR-0006).
- A data message (one that carries or derives from a platform fetch) carries `provenance {route, vendor, service, fetched_at}` and `retention_class`. A control message (`job/v1`, `jobs.completed/v1`, `source.events/v1`, the dead letters and the n8n notices) carries `producer` and no `provenance` (ADR-0003); a source event's `retention_class` is the source's registry column, not a class of the message. The exceptions are under "F2's readings".

## What stays in a version

A change that only adds an optional field stays in its version (ADR-0002). Anything else is a new version: a removed or renamed field, an optional field made required, a changed type or meaning, a narrowed type (for example a typed map replaced by fixed keys, which Q11 names for the n8n alert metrics), a new value of a closed list, and a helper that returns a different output for the same input.

How the lists grow (Q1, decided by the orchestrator on 25 Oct 2026):

1. **Registry data grows inside the version.** Service names (the 86 services of the service index and the D3 writers `admin-api`, `client-portal` and `admin-console`, Q4) and vendors are not schema enums. `producer.service`, `provenance.service`, a `requested_by` that is a service by definition (a `recheck`'s, on the job and on the crawl policy, F-43), and `provenance.vendor` are lower-case patterned strings (`^[a-z0-9]+(-[a-z0-9]+)*$`), which `validate()` checks in producer mode against `packages/contracts/registries/*.json` (F-09). A `requested_by` or `actor` that may hold either a service or a person (on decisions, source events, deletions, every job but a `recheck`, and the crawl policy of an `ops_force`) is a string of 1 to 256 characters: one that matches the service pattern is a service, which `validate()` checks in producer mode against the same registry data, and any other is a person's reference, unchecked in both modes; D3's person reference never matches the pattern (it holds a colon, as the fixtures' `person:<ULID>` does) (Q18, decided by the orchestrator on 25 Oct 2026). A new service or vendor adds rows there (services, vendors, the producer table, topic writers, decision producers, partition keys, visibility, its `context` keys) through `/contract-change`, and no schema changes version.
2. **Optional keys grow inside the version.** Each producer's `context` keys, each resolver's `extras` keys and each `evidence_type`'s `evidence` keys are optional fields (ADR-0002). The first two are declared in `registries/context-keys.json` and `registries/extras-keys.json`, the evidence keys in the `discovery.hits/v1` schema.
3. **Every other closed list grows only through a new version.** Platforms, routes, retention classes, record and item kinds, job kinds and `job_kind`, deletion reasons, scopes and modes, completion statuses, `capped_reason` and the terminal reasons, decision and event types, the registry `reason` list, profile statuses, reasons and `review_flags`, `account_type`, `found_via`, `evidence_type`, observation labels, the lang-dialect-id labels, the analysis tasks, statuses and skip reasons, the n8n channels, audiences, severities, rule types and card types, and every other list in `packages/contracts/src/vocabulary.ts` (each with its source; `schemas/vocabulary.json` is the same data for Python). A new value is a new version of every schema that carries the list, published beside the old one for the dual-publish window.

The marks on `account_type` (organisation kind or person kind, Q7) are data the listing reads, not part of a message's shape. Changing a mark, as counsel's answer on Instagram creators may, changes no schema (the plan's table of DEFERRED rows).

## Producers validate strictly, consumers tolerantly

- `validate(schemaId, value, mode, options)` in TypeScript and `validate(schema_id, value, mode, queue=..., client_type=...)` in Python run the schema, then the cross-field rules JSON Schema cannot express, then, in producer mode, the registry checks. Producer mode refuses an unknown field. Consumer mode accepts an unknown field of a known version and drops it (A32; the `tolerant/` fixtures).
- Before the schema, both languages check the message as JSON, in both modes: every string and object key is well-formed Unicode, UTF-8 encodable (ADR-0006), so a lone surrogate is refused with `not_unicode` at its path (review finding 5). A producer cuts text by code point, never through a surrogate pair.
- A consumer reads the versions it reads, skips a version the package knows that it does not read, and parks a version the package does not know (ADR-0002). `classifyVersion(schemaId, reads)` and `classify_version(schema_id, reads)` return `read`, `skip` or `park`.
- The package ships a new version before any producer emits it (ADR-0002), so a consumer on the new package skips the new version until it reads it, and parks nothing.

## Dual-publish window

**Decided by the orchestrator on 25 Oct 2026 (Q17), as ADR-0002 L23 and L32 leave to this file.** No schema has a second version yet, so nothing depends on the length until the first one ships.

1. The window opens with the producer's first message in the new version, vN+1. While it lasts, the producer publishes each message in both versions.
2. A consumer moves by releasing a reader of vN+1. It switches once its committed offsets are past the first vN+1 message, so no message is published only in a version it no longer reads, and from then on it skips vN.
3. The window closes, and the producer stops publishing vN, when every consumer of the topic reads vN+1, and no sooner than 14 days after it opened, so that a consumer can still roll back to its vN reader.
4. An old version outlives the window wherever messages are kept. normalize-item replays archived `raw.items` records through raw-archiver (ADR-0039), so it keeps a reader of every `raw.items` version the archive still holds. A dead letter keeps the version it was written in, so re-driving it needs a reader of that version; without one it is parked.

## Catalogue of schema ids and versions

Every schema id the package knows. The A31 test (`packages/contracts/test/unit/versioning-doc.test.ts`) fails when this table and the catalogue in `packages/contracts/src/catalogue.ts` differ.

| Schema id | Version | Class | JSON Schema (`packages/contracts/schemas/`) | Python models (`listening_contracts.models.{strict,consumer}`) | Written by |
|---|---|---|---|---|---|
| `raw.items/v1` | v1 | data | `raw.items/v1.json` | `raw_items_v1` | the fetchers, receivers and resolvers in `registries/topic-writers.json` |
| `items.normalized/v1` | v1 | data | `items.normalized/v1.json` | `items_normalized_v1` | normalize-item |
| `item.hits/v1` | v1 | data | `item.hits/v1.json` | `item_hits_v1` | keyword-matcher |
| `discovery.hits/v1` | v1 | data | `discovery.hits/v1.json` | `discovery_hits_v1` | keyword-matcher, x-recent-search, tg-message-search, fb-page-search, search-hit-router, web-commoncrawl-scanner |
| `poster.profiles/v1` | v1 | data | `poster.profiles/v1.json` | `poster_profiles_v1` | the eight resolvers; poster-resolver only to re-emit a cached profile |
| `registry.decisions/v1` | v1 | data | `registry.decisions/v1.json` | `registry_decisions_v1` | per decision type, `registries/decision-producers.json` |
| `source.events/v1` | v1 | control | `source.events/v1.json` | `source_events_v1` | registry-writer |
| `items.analysis/v1` | v1 | data | `items.analysis/v1.json` | `items_analysis_v1` | analysis-sentiment, analysis-topics, analysis-entities, analysis-media |
| `item.metrics/v1` | v1 | data | `item.metrics/v1.json` | `item_metrics_v1` | normalize-item and the count-only readers |
| `deletions/v1` | v1 | data | `deletions/v1.json` | `deletions_v1` | the deleting fetchers, retention-purger, yt-text-purger, x-compliance-sync, `admin-api` |
| `article.urls/v1` | v1 | data | `article.urls/v1.json` | `article_urls_v1` | the news finders, search-hit-router, web-commoncrawl-scanner |
| `search.results/v1` | v1 | data | `search.results/v1.json` | `search_results_v1` | web-search-perplexity, web-search-mojeek, web-gdelt-poller, yt-web-search-bridge |
| `crawl.policies/v1` | v1 | data | `crawl.policies/v1.json` | `crawl_policies_v1` | news-robots-checker |
| `news.dedup/v1` | v1 | data | `news.dedup/v1.json` | `news_dedup_v1` | news-dedup |
| `jobs.completed/v1` | v1 | control | `jobs.completed/v1.json` | `jobs_completed_v1` | the SDK job wrapper |
| `job/v1` | v1 | control | `job/v1.json` | `job_v1` | per queue and kind, `registries/producers.json` |
| `dlq.<service>/v1` | v1 | control | `dlq/v1.json` | `dlq_v1` | the SDK wrapper |
| `n8n.alert/v1` | v1 | control | `n8n.alert/v1.json` | `n8n_alert_v1` | any service, through the SDK n8n client (HTTP, not a topic) |
| `n8n.card/v1` | v1 | control | `n8n.card/v1.json` | `n8n_card_v1` | any service, through the SDK n8n client (HTTP, not a topic) |

The topic writers named here are a summary; the registry files are the record the SDK enforces.

## Frozen namespaces and golden vectors

- `ns_items` = `b0eeaa44-bf4b-4c44-b977-bb8c9485f06e`: `item_id = uuid_v5(ns_items, idempotency_key)` (ADR-0006).
- `ns_hits` = `889d9f7d-7cd6-4556-8f5e-3cebf0938434`: `hit_id = uuid_v5(ns_hits, "<item_id>:<client_id>:<keyword_id>")` (ADR-0006).
- `ns_cards` = `68861d52-0265-403a-a35d-493238d31f4b`: `card_id = uuid_v5(ns_cards, "<card_type>:<subject key>:<decision_id or request_id>")` (Q11, F-47).

The three namespaces never change, since every stored id is derived from them.

Every key, id and hash helper normalises with NFC and lower-cases with the mappings of Unicode 15.1.0, in both languages (D-2). A code point Unicode 15.1 leaves unassigned (`registries/unicode-15.1-unassigned.json`, 707 ranges, surrogates excluded) passes through both unchanged and is never refused. Under 15.1 such a code point is a starter with no decomposition, composition or case, so the helpers split text at it, and the runtime normalises and lower-cases the runs between, which any runtime at 15.1 or later does as 15.1 does (normalisation stability; `unicode.test.ts` checks every code point). Each package refuses at import a runtime whose Unicode version is below 15.1 (`unicode_version`). Node 24 implements Unicode 17.0 and Python 3.13 implements 15.1.0; the `unicode_15_1` vectors of `golden/keys.json` hold both to 15.1. Moving to another Unicode version changes keys, so it is a new version of every schema that carries them. One difference is known and left unfixed: a final sigma depends on the letters around it, and Unicode 17.0 no longer treats U+0295 as cased, while 16.0 made U+1171E a spacing mark that is not case-ignorable, so Node 24 and Python 3.13 lower-case a capital sigma next to either differently ("AΣʕ" gives σ in Python and ς in Node).

The golden files under `fixtures/contracts/golden/` were written once from the plan's specification, and TypeScript and Python reproduce them byte for byte. A golden vector never changes inside a version. A helper whose output changes for the same input is a new version of every schema that carries that output, with the dual-publish window, and the old vectors stay as the record of the old version. Moving a platform's `query_key` folding profile from `exact` to `folded` changes registry data (`registries/query-folding.json`) and the test that pins every platform at `exact`, through a `/contract-change` (Q10); no message carries `query_key`, and the vectors of both profiles stay.

The `author_ref` key and the n8n signing secret in the golden files are published test values and are named so there; real keys come from Vault at run time (ADR-0010).

## F2's readings

### Retention class (F-04)

The SDK stamps a `raw.items` record's `retention_class` from the source row only when the record was read on the source's own route. A record read on another route takes the default class of the route actually used and the platform: a client's revoked TikTok account read by the vendor in fallback is `vendor_agreed` (ADR-0035 L33). LinkedIn records take the class of their content as the adapter declares it, `linkedin_48h` for member content and `linkedin_org` for organisation content, on every route (ADR-0005, ADR-0054 L43, ADR-0055 L30, CONVENTIONS v1.1 L186). The class depends on the source row, which the message does not carry, so `validate()` does not check it. The fixtures under `fixtures/contracts/raw.items/v1/valid/` show each case: `prd-fb-page-feed-poller.json` (the source's own route), `video-fallback-vendor-agreed.json` (another route), `prd-li-post-comments-fetcher.json` (member content on the vendor route), and `prd-li-client-posts-poller.json` and `prd-li-company-posts-poller.json` (organisation content on the green and vendor routes).

### Topic-driven producers (F-05) and backfilled first sights (F-06)

F2's reading of ADR-0005 L27 and L31 and ADR-0006 L31, for the producers that write `raw.items` with no job of their own (news-article-extractor and search-hit-router): `job_id` is the input message's `producer.job_id`; `attempt` is the consumer's own attempt, from 1; `job_kind` is `backfill` for news-article-extractor when the article URL's `found_via` is `sitemap_backfill` or `commoncrawl` and `rotation` otherwise (so a Disqus article found by backfill gets the single `once` comment fetch, news-article-extractor.md L43), and `rotation` for search-hit-router's `result`. Fixtures in `raw.items/v1/valid/`: `prd-news-article-extractor.json` (its `job_id` is the `producer.job_id` of `article.urls/v1/valid/prd-news-feed-poller.json`), `article-backfill.json` and `result.json`.

A record read for a `first_sight` job whose `origin_kind` is `backfill` carries `job_kind = backfill` (ADR-0065 L37): `raw.items/v1/valid/video-first-sight-backfill.json`.

### `producer.job_id` (F-17)

`producer.job_id` is a ULID, never a composite or null (ADR-0006 L31). It is set as follows:

- A job's own messages carry its `job_id`: `raw.items/v1/valid/prd-fb-page-feed-poller.json`, whose `envelope.job_id` it equals, and every `jobs.completed/v1` report.
- A topic consumer copies its input's `producer.job_id`: `items.normalized/v1/valid/prd-normalize-item.json` from that `raw.items` record, and `raw.items/v1/valid/prd-news-article-extractor.json` from `article.urls/v1/valid/prd-news-feed-poller.json`.
- A jobless receiver's record carries its receipt ULID, which is also the record's `job_id`: `raw.items/v1/valid/prd-ig-webhook-receiver.json`.
- A job that a scheduler emits outside any job of its own carries that job's own `job_id`: `job/v1/valid/prd-comment-decay-scheduler.json`.
- A D3 writer's message carries the request's `request_id`: `job/v1/valid/ops-force.json`, whose `request_id` it equals, and `registry.decisions/v1/valid/add-keyword.json`. This needs D3 to stamp a ULID `request_id` on every client-portal and admin-console write (open item O-12, for the orchestrator).
- A time-driven loop's messages (alert-evaluator, source-health-canary) carry one ULID per evaluation run: `n8n.alert/v1/valid/prd-alert-evaluator.json` and `registry.decisions/v1/valid/prd-source-health-canary.json`.

`validate()` checks the form, a ULID; which case applies depends on what the producer was handling, which the message does not show.

### Multi-item deletions (F-07)

F2's reading of ADR-0003 L28: the SDK deletion builder splits an item-scope target so that every message's items share the key (`source_id`), `platform`, `kind`, `provenance.route`, `provenance.vendor`, `provenance.service` and `retention_class`, and sets `provenance.fetched_at` to the newest `fetched_at` in the chunk. The split is deterministic (ids sorted, a fixed chunk size in the SDK), so a repeated sweep emits the same messages with the same `deletion_id`s (retention-purger §5.3 L72). Fixture: `deletions/v1/valid/item-multi.json`.

### Decisions with and without provenance (F-14)

`registry.decisions/v1` is a data topic, but a decision carries `provenance` and `retention_class`, or neither, as its producer row in `registries/decision-producers.json` says (the plan's producer rows). They are required where the decision reports what a fetch or a platform call returned (ADR-0003 L26 names the qualifier's decisions from resolver profiles, news-robots-checker's crawl refusal and the canary's `health_change`). They are refused where a person entered the decision, which carries `requested_by` instead (the D3 writers, ADR-0003 L26), and where the decision reports state with no fetch behind it (a lease or subscription, a budget, an offboarding, a sweep over stored statistics, except a rule-3 `dormant`, below). The qualifier's `tier_change` and `dormant` are bound to `rule_hit` (`rule_hits` in `registries/decision-producers.json`). A `tier_change` under rule 6 or 10, which applies a resolver profile, requires provenance. A `tier_change` or `dormant` under rule 9, the sweep, refuses it. A `dormant` under rule 3, which runs both in the sweep and on a profile, accepts either, because the message does not say which. Any other `rule_hit` for these two decisions is refused (`decision_not_allowed`, at `["producer", "service"]`). Decided by the orchestrator on 25 Oct 2026 (D-3); review finding 8. The two travel together in both modes. Producer mode checks the row (`provenance_required`, `provenance_refused`, at `provenance`); consumer mode accepts either. Fixtures: `registry.decisions/v1/valid/add-keyword.json` (refused), `prd-source-health-canary.json` (required), `tier-change-profile.json` and `tier-change-review.json` (rules 6 and 10, required), `tier-change-sweep.json` and `dormant-decay.json` (rule 9, refused), `dormant.json` (rule 3, either); `registry.decisions/v1/invalid/provenance-required.json`, `provenance-refused.json`, `tier-change-profile-without-provenance.json`, `tier-change-sweep-with-provenance.json`, `dormant-decay-with-provenance.json` and `tier-change-rule-not-allowed.json`.

### Dead letters (F-21, F-42)

`dlq.<service>/v1` holds one record per failed message; a failed batch gives one record per message (raw-archiver.md L118). A record carries `stage` (`consume` or `produce`), `original {topic, partition, offset, key, schema, message_id}`, the original as `message` (JSON) or as `raw` (base64, when it did not parse), `error {class, message, attempts, first_failed_at, last_failed_at}` and `consumer {service, group}`. A produce-side entry, such as retention-purger's failed chunk (retention-purger.md L128), has no consumed offset: its `original.partition`, `original.offset` and `consumer.group` are null (F-21). The record is keyed by the original message's key, or, on the produce side, by the key the SDK would have set.

A record copies its original's `provenance` to its top level under the original's own type: the signal provenance for an author-, source- or client-scope deletion, whose `route` and `vendor` are null when its signal is no fetch (F-08), and the data provenance for every other original. It copies the original's `retention_class` with it only when that is one of the nine classes: a null, absent or unknown class is never copied, and a non-item deletion has none. When the original's provenance fails its own type, or the original carries none (a job, or a `raw` entry), the record carries neither (F-42; decided by the orchestrator on 25 Oct 2026, D-1 and D-12, review findings 1 and 4). So a record carries a null route only when its original is an author-, source- or client-scope deletion. `validate()` checks the copy in both modes and never throws on it: the producer's strict type decides whether a copy is due, and the mode's own type judges a copy made, so a consumer tolerates a provenance field that a newer package adds. A `raw` entry can still hold platform data, so it is a stated exception to ADR-0003, and the dead-letter topics keep a short retention (ADR-0010 L49). Fixtures: `fixtures/contracts/dlq/v1/`, among them `valid/consume-author-deletion.json`, `consume-source-deletion.json`, `produce-client-offboarding.json` and `consume-malformed-provenance.json`, and `invalid/invented-class.json`, `null-class-copied.json` and `null-route-not-a-deletion.json`.

### The n8n notices (F-49, F-51, O-11)

- **Classification (F-51, F2's choice; plan revision note R-5).** Both are producer-only notices: `producer`, no `provenance`. An alert carries aggregates only, never item text, an `author_ref` or a handle (alert-evaluator.md L65, L128). A card may show a public account's identity in `facts` but never an individual's data (qualifier.md L118).
- **Signing (F-49).** ADR-0067 fixes one HMAC scheme over the body with a timestamp and an idempotency key; the header names, the signed string and the tolerance are F2's choices. A signed request carries `X-SB-Timestamp` (Unix seconds, digits only), `Idempotency-Key` (the notice's `idempotency_key`) and `X-SB-Signature: v1=<hex>`, where `<hex>` is the lower-case hex HMAC-SHA256, under the secret, of the UTF-8 of `<timestamp>.<idempotency key>.` followed by the body's bytes. The idempotency key holds no dot, so the three fields of the signed string stay apart: a key `a.b` over the body `c` and a key `a` over the body `b.c` would otherwise sign alike. The notices' own keys (`<alert_id>:<channel>`, `<card_id>:<channel>`) hold none. `signN8n` and `sign_n8n` refuse a key holding a dot (`bad_idempotency_key`). `verifyN8n(body, headers, secret, now, toleranceSeconds = 300)` and `verify_n8n(...)` read the header names in any case and refuse with `missing_header`, `bad_idempotency_key` (empty, or holding a dot, a space or a control character), `bad_timestamp`, `stale_timestamp` (further than the tolerance from `now`, either way) or `bad_signature` (also a scheme other than `v1`, or an empty secret). The caller passes `now`; no helper reads a clock. A `now` or a tolerance that is not a finite non-negative number is the caller's error and throws (`bad_now`, `bad_tolerance`), so a NaN cannot switch the staleness check off. The SDK signs again at each send attempt, so a retry carries a fresh timestamp. Golden vectors: `fixtures/contracts/golden/n8n-signing.json`.
- **Channels (O-11, settled in the build).** An alert's `channel` is `email`, `telegram`, `slack` or `webhook`, the last for a client's own webhook, which alert-evaluator posts itself (alert-evaluator.md L69; Q15). `fallthrough_channel` and a card's `channel` take the n8n channels only (`email`, `telegram`, `slack`). Adding `webhook` now was additive; adding it later would have widened a closed list.
- **The government rule** (alert-evaluator §6.2 L102; F-50) needs the client's type, which an alert does not carry. The producer passes it to `validate()` (`clientType` in TypeScript, `client_type` in Python). Producer mode refuses a client or account-manager alert validated without it (`no_client_type`).

### Keys of the open maps

The maps whose keys are platform data, `reactions_by_type` on `items.normalized/v1` and `item.metrics/v1` and `public_metrics` and `language_share` in `discovery.hits/v1` evidence, take snake_case keys (`^[a-z][a-z0-9_]*$`): reaction types in lower case (F-34), a platform's count names (X's `retweet_count`, Telegram's `forwards`) and the index's language codes (`ara`). `validate()` checks the keys in both languages rather than the JSON Schema, because a key pattern is a construct the Python model generator cannot render (ADR-0030). The metrics map of the eight other alert rule types takes any string key (Q11).

## How a change is made

1. The session that needs a change writes `docs/proposals/<session>-<topic>.md` from `build-plan/templates/PROPOSAL.md`, naming the kind of change (above), and stops.
2. `/contract-change` applies an approved proposal on `sb/CC-<proposal>`. It edits the Zod source in `packages/contracts/src/` (never a generated file) and the registry data, then regenerates: `pnpm --filter contracts export:schemas` (JSON Schema), `pnpm --filter contracts gen:python` (the Pydantic models) and `pnpm --filter contracts gen:fixtures` (the fixtures, from `packages/contracts/scripts/fixtures/`).
3. It adds the valid, invalid and tolerant fixtures the change needs. Both conformance suites, the A2 and A3 freshness tests and `make check` pass.
4. A new version adds its row to the catalogue above, keeps the old version's schema and fixtures, and follows the dual-publish window.
5. It raises the package version in `packages/contracts/package.json` and `packages/contracts/pyproject.toml` together; the two stay equal (A33).
