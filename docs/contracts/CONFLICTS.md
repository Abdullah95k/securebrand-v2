# Contract conflicts

D1 · 7 Oct 2026 · Status: **open, none resolved.** D2 decides each entry with the user, records the answer in an ADR and folds it into CONVENTIONS v1.1. Until an entry is decided, a build session that meets it stops and asks; it does not pick a side.

Every place where the 86 PRDs, CONVENTIONS (Draft v1) and the README's nine proposed decisions disagree about a contract: a topic or column with more than one writer, one field under several names, one field with several types, a key that two PRDs build differently, a table named in one PRD only, a job kind no producer emits, and the budget tags, flags, retention classes and partition keys they disagree on. The full inventory behind it is `docs/contracts/INVENTORY.md`.

## How to read an entry

- **Type** names the kind of conflict: *writers* (more than one writer of a topic, queue kind, table or column), *names* (one field or value under several names), *types* (one field with several types or formats), *shape* (one message with several structures), *key* (an identifier built in several ways), *enum* (a value set that differs), *job kind* (a kind with no producer, or emitted where no consumer expects it), *single-PRD* (a table or column only one PRD names), *partition*, *budget*, *flag*, *retention*, *rule* (a PRD departs from a CONVENTIONS rule), *document* (CONVENTIONS or the README disagrees with itself).
- **Where** gives each side with its reference: `service §section Lline` is that line of `docs/prds/<platform>/<service>.md`; `§14 Qn` is open question n; `CONVENTIONS Lnn` is `docs/prds/_shared/CONVENTIONS.md`; "README decision n" is the numbered list in `docs/prds/README.md`.
- **At stake** says what breaks if the disagreement reaches code. It is context, not a ruling.
- **Options** are the realistic answers, numbered for reference; the order carries no recommendation. D2 adds the recommendation and the consequences when it puts the question to the user.
- **Blocks** lists the build sessions that cannot finish their part without the answer (session IDs from `build-plan/SESSIONS.md`). F2 (contracts package), F3 (control-plane schema) and F8 (ClickHouse schema) appear wherever the answer changes a schema.


## Index

Entries CF-001 to CF-118 are in this file; AU-001 to AU-113 (contradictions found by checking every cross-service assumption against the PRD it is about) are in `docs/contracts/CONFLICTS-ASSUMPTIONS.md`. Overlaps between entries are named where they were found.

| ID | Conflict | Type | Blocks |
|---|---|---|---|
| [CF-001](#cf-001) | Message metadata: a `schema` string, a `schema_version` integer, or no version at all | names, types, shape | F2, F4, F6, C6, W3, C8, C9, C7, and every producer of a topic. |
| [CF-002](#cf-002) | Provenance and `retention_class` on messages: which topics carry them, under which names | names, shape, retention | F2, F4, F6, C5, C6, C8, A1, A2, A3, A4, N3, N4, N5, W1, W2, W3, W4,... |
| [CF-003](#cf-003) | Topic partition keys that depart from the `source_id` default, and search records without a `source_id` | partition, key | F2, F4, C4, C5, C6, C13, C14, X7, N1, N7, W1, W2, W3, W4, VLI1. |
| [CF-004](#cf-004) | `raw.items`: a nested `{envelope, payload}` message or a flat record, and where the platform record sits | shape, names | F2, F4, F6, C2, C4, FB4, IG2, VTT1, VTT2, X1, YT8, VTG1, W1, W2, W4. |
| [CF-005](#cf-005) | `raw.items` envelope: the required fields, who computes the key and class, and `batch` against `raw_ref` | shape, names, writers | F2, F4, F6, C2, C4, and every `raw.items` producer (N6, TG1, TG2, X... |
| [CF-006](#cf-006) | `raw.items`: how a record says why it was read (`metrics_observation`, `job_kind`, `origin`, `delivery`, `ingest_mode`) | names, shape | F2, F4, F6, C4, C10, C11, FB4, FB3, FB7, IG4, YT2, YT8, TG1, TG2, X... |
| [CF-007](#cf-007) | Comment records on `raw.items`: the parent link, the content hash, the edit marker and the redaction marker each go by several names | names, shape | F2, F4, C4, C13, FB5, FB7, VFB3, VIG2, IG4, IG6, LI2, LI3, VLI4, VT... |
| [CF-008](#cf-008) | `raw.items` records normalize-item has no mapper for: unlisted producers, kinds `profile`, `reaction` and `search_response`, and partial YouTube records | writers, shape | F2, F4, C2, C4, C8, YT2, YT3, YT4, YT8, VIG1, N8, LI3, VLI2, VTG2, ... |
| [CF-009](#cf-009) | `item.hits`: a second writer, hits on individuals' comments, and `matched_term` against `matched_text` | writers, names, shape | F2, C5, C6, A1, A5, VTG1. |
| [CF-010](#cf-010) | `discovery.hits` writers: services outside CONVENTIONS' list, client onboarding on the topic, and early hits keyword-matcher cannot see | writers | F2, C5, C7, C8, C9, IG2, X1, VTG1, TG1, TG2, FB6, VFB1, W3, W5. |
| [CF-011](#cf-011) | `discovery.hits` message: seven shapes, three partition keys, two of the shapes under one schema name | shape, names, partition | F2, F4, C5, C6, C8, FB6, IG2, X1, VTG1, TG1, TG2, W3, W5. |
| [CF-012](#cf-012) | `poster.profiles` writers: poster-resolver merges answers it expects on `jobs.poster-resolver`, while the eight resolvers publish their own profiles | writers | F2, C8, C9, FB1, IG1, X2, YT1, N2, VTT3, VLI2, VTG2. |
| [CF-013](#cf-013) | `poster.profiles` message: flat or `{envelope, profile}`, five names for the classification, four for the cache flag, and the key of an individual's answer | shape, names, partition | F2, C8, C9, FB1, IG1, X2, X5, YT1, N2, VTT3, VLI2, VTG2. |
| [CF-014](#cf-014) | `country_signals` and `lang_share`: nine vocabularies and three JSON types for the qualifier's Iraqi-signal inputs | names, types | F2, F3, C3, C7, C8, C9, FB1, IG1, X2, YT1, N2, VTT3, VLI2, VTG2. |
| [CF-015](#cf-015) | `registry.decisions`: writers beyond the qualifier, `decision` against `action`, and the `health_change` message | writers, names, shape, partition | F2, C7, C9, C12, C14, YT7. |
| [CF-016](#cf-016) | `source.events`: registry-writer's events or anyone's, and the shape of an event a poller writes | writers, shape | F2, C7, C10, C11, C6, FB2, FB3, FB7, VFB2, IG2, IG3, IG4, IG5, LI1,... |
| [CF-017](#cf-017) | `items.analysis`: what the four writers send against what store-writer reads, and the message key | shape, names, key | F2, F8, C6, C15, A1, A2, A3, A4. |
| [CF-018](#cf-018) | `item.metrics` writers: normalize-item and the metrics services both observe the same fetch, and LinkedIn counts have no named producer | writers | F2, C4, C6, C11, FB4, YT4, TT1, VTT6, LI1, LI2, LI3. |
| [CF-019](#cf-019) | `item.metrics` message: flat with a `metrics` object, or an envelope with an `observation` object; `observation` a string or an object; no `item_id` | shape, names, types | F2, F8, C4, C6, FB4, YT4, TT1, VTT6. |
| [CF-020](#cf-020) | `deletions` message: deletion-propagator's required fields against a short form keyed by `idempotency_key` and a long form with top-level `source_id` | shape, names | F2, C13, C14, C15, A5, X7, YT7, FB4, FB5, FB7, VFB3, IG6, LI1, LI2,... |
| [CF-021](#cf-021) | Who acts on a `deletions` message: deletion-propagator alone, or every holder of a copy, and how the others learn a deletion is done | writers, rule | F2, C13, C15, A1, A2, A3, A4, A5. |
| [CF-022](#cf-022) | `article.urls`: the news pollers' envelope against search-hit-router's flat `article.urls/v1`, and a writer CONVENTIONS does not list | shape, names, writers | F2, N3, N4, N5, N6, W3. |
| [CF-023](#cf-023) | `search.results`: yt-web-search-bridge's message against `search.results/v1`, and whether search-hit-router routes the bridge's results or skips them | shape, names, types, writers | F2, W1, W2, W3, W4, YT9. |
| [CF-024](#cf-024) | `jobs.completed` (not in CONVENTIONS): who writes it, the schema version, the report fields, and producers that report elsewhere | writers, shape, names, document | F2, F4, F6, C10, C11, X1, X3, X4, X5, X6, YT3, YT4, YT5, YT6, FB3, ... |
| [CF-025](#cf-025) | `news.dedup` (not in CONVENTIONS): a topic whose only named reader does not read it, and story fields `items.normalized` does not have | writers, shape, document | F2, C4, C6, N7, N6. |
| [CF-026](#cf-026) | `raw.replay` (not in CONVENTIONS): a replay topic with no consumer, while normalize-item replays from object storage | writers, document | F2, C2, C4, C5, C6, C13, A1, A2, A3, A4. |
| [CF-027](#cf-027) | Message fields one PRD names two ways (prose against its own example or lists) | names, document | F2, C5, N1, W1, W2, W4, C4, FB3, TG1, C2, N6, W5. |
| [CF-028](#cf-028) | News article record on `raw.items`: normalize-item maps a `date` field the extractor writes as `published_at` | names | F2, C4, N6, N7. |
| [CF-029](#cf-029) | `crawl.policies`: news-robots-checker counts on registry-writer acting on the topic, which registry-writer does not read | writers | F2, C7, N1, N2, N3, N4, N5, N6. |
| [CF-030](#cf-030) | Who writes `sources.backfill_status` (and `next_poll_at` at hand-over): one writer in three documents, eight writers in the PRDs | writers, enum | F3, F5, C10, C7, FB2, FB3, VFB1, VFB2, VTT1, VTT2, VTG3, TG1, TG2, N2 |
| [CF-031](#cf-031) | `sources.next_poll_at` and `last_polled_at` on rows that several services rotate: one column, several schedulers with different intervals | writers | F3, F5, C7, N3, N4, N5, W1, W2, W4, IG2, IG3, IG5, VIG1, TG1, VTG3,... |
| [CF-032](#cf-032) | Who writes `sources.health`: registry-writer owns it and applies route-wide changes; a dozen fetchers set one source's health directly | writers | F3, F2, C7, C12, IG3, IG4, IG5, FB7, LI1, LI3, VLI3, TT1, TG1, TG2,... |
| [CF-033](#cf-033) | Registry columns registry-writer says it owns, written or changed by other services: `tier`, `followers`, `platform_id`, `notes`, `last_hit_at` | writers, names | F3, C7, C5, C9, C10, FB2, FB3, FB7, VFB1, VFB2, IG2, IG3, VTT2,... |
| [CF-034](#cf-034) | `cursors` rows that are not "source × service": service-level progress rows, rows per class, keyword, hashtag edge or X rule, and a suffixed service name | key, shape | F3, F4, F6, C15, A1, A2, A3, A4, C5, C4, C2, C6, C14, YT7, FB6, IG2... |
| [CF-035](#cf-035) | What a `cursors` row holds beyond the CONVENTIONS columns: due times, subscription state, job progress, id sets and registry data | shape, names | F3, F5, IG1, IG4, IG5, VIG1, FB6, W1, W2, W4, X4, X5, YT9, TG2, VFB3 |
| [CF-036](#cf-036) | Writes into another service's `cursors` row, and reads of another service's rows as a contract | writers | F3, F4, C10, FB2, FB3, X3, X4, X5 |
| [CF-037](#cf-037) | `budgets`: quota-governor's counter rows against services that write usage into them, and configuration other PRDs keep there | writers, shape | F3, F5, C1, FB2, VFB2, IG1, IG3, IG5, IG6, VIG1, VIG2, LI1, VLI1, V... |
| [CF-038](#cf-038) | The two quota ledgers: X UTC-day read ledger (one table, three key forms) and the Instagram hashtag ledger (its own table or rows in `budgets`) | key, shape, single-PRD | F3, F5, C1, IG2, VIG1, X1, X2, X3, X4, X5, X6 |
| [CF-039](#cf-039) | `clients` has no column list: the government marker under four names, amber acceptance, X entitlement, token references and per-service settings | names, shape, writers | F3, C1, C5, C7, C9, C8, C12, C13, C14, A5, YT7, YT9, W1, FB1, FB2, ... |
| [CF-040](#cf-040) | `keywords` and keyword-rule `sources` rows: no column list, no writer, and no agreed link between a keyword and the rows the searchers rotate | names, shape, writers, key | F3, F2, C5, C7, C9, C6, FB6, VFB1, VIG1, VTT1, X1, X4, X5, VLI1, VT... |
| [CF-041](#cf-041) | `service_runs`: "last run, lag, errors per service" in CONVENTIONS; per-job result rows, per-page state, connection state and checkpoints in the PRDs, read across services | shape, key | F3, F4, F6, C11, C15, A5, N8, VLI1, LI3, X3, X4, W1, W5 |
| [CF-042](#cf-042) | `retention_classes`: two column models (ClickHouse TTLs and the purger's clock table) for one table with no column list and no writer | shape, names | F3, F8, C4, C2, C6, C13, C14, C15, YT7, TT1 |
| [CF-043](#cf-043) | `review_queue`: one table, about ten uses, columns defined only for the qualifier's review cards | shape, writers | F3, C9, C4, A1, A2, A3, A4, W1, W2, W3, W4, X1, X4, YT5, YT6, YT8, ... |
| [CF-044](#cf-044) | `decisions`: the qualifier's decision log, also used as fb-page-search's emitted-id set, poster-resolver's hit counter and news-dedup's ops log | writers, shape | F3, C9, C8, C7, FB6, N7, VLI2, VTG1, VTG2, N2 |
| [CF-045](#cf-045) | Comment state for change detection: one ledger with two owners, four per-service tables, ClickHouse `comments` read as state by six fetchers, and a shared table proposed | shape, writers, single-PRD | F3, F8, C6, C11, FB5, VFB3, VTT5, YT5, YT6, X6, VIG2, IG6, LI2, VLI... |
| [CF-046](#cf-046) | Resolver caches: one table name (`profile_cache`) for four different designs, three other caches, and poster-resolver's `poster_profiles` in front of them all | names, key, shape, single-PRD | F3, C8, FB1, IG1, X2, YT1, VTT3, VTG2, VLI2 |
| [CF-047](#cf-047) | `news_sites`: read by seven news services, written by news-site-resolver and (per two PRDs) by registry-writer, keyed by host or by `source_id`, possibly folded into `sources` | writers, key, single-PRD | F3, C7, C9, N2, N3, N4, N5, N1, N6, N8 |
| [CF-048](#cf-048) | `crawl_policies`: row columns against the `crawl.policies` message, and the host-gate slot that every news service writes into the robots-checker's rows | shape, writers | F3, F4, N1, N3, N4, N5, N6 |
| [CF-049](#cf-049) | ClickHouse purges: two field lists for emptying content (deletion-propagator's and store-writer's TTLs), a video title outside "text", and the author column under two names | shape, names | F8, C6, C13, C14, C4, X7, YT7 |
| [CF-050](#cf-050) | ClickHouse `analysis` apart from its key: partitioned by its own version column, and several tasks per item and service to keep apart | partition, key | F8, C6, A1, A2, A4, C15 |
| [CF-051](#cf-051) | ClickHouse tables and views beyond CONVENTIONS: `hits` (whose key cannot hold item-less discovery hits), daily and monthly aggregates, and `_v` views with no definition | single-PRD, key, shape | F8, C6, C5, C15, A5, C8, FB6, W3, W5 |
| [CF-052](#cf-052) | ClickHouse `items` and `comments`: column names readers query that store-writer does not define (`published_at`, `permalink`, a `parent_id` key) and a "same names" rule its own example breaks | names, key | F8, C6, C9, VIG2, YT5 |
| [CF-053](#cf-053) | Object storage: who may write `media/`, `raw/`, `archive/` and `cache/news/`, and what each prefix holds | writers, names, shape | F4, F6, C2, C13, C14, A1, A2, A3, A4, C4, C7, X7, W5, N6, N8 |
| [CF-054](#cf-054) | Audit tables: `registry_audit` append-only yet updated as an outbox, and audit trails with no table | writers, shape, single-PRD | F3, C7, C12, X7, C13 |
| [CF-055](#cf-055) | `deletion_requests`: intake requests and per-message propagation state in one table with no column list, read by `deletion_id`, by `item_id` and by author hash | shape, key, writers | F3, C13, C14, C6, C4, X7, YT7 |
| [CF-056](#cf-056) | Client priority lists, seed lists and watchlists: kept on `clients`, in `client_sources.priority`, or on `keywords` | names, shape | F3, C7, C8, C9, X2, LI1, N2, W1, W2, FB6 |
| [CF-057](#cf-057) | Token and key health: 40 PRDs mark a token or key `degraded` and expect later calls to skip it, but only one says where the mark is kept | shape, writers, names | F3, F4, F6, C12, FB1, FB2, FB3, FB5, FB6, FB4, FB7, IG1, IG2, IG3, ... |
| [CF-058](#cf-058) | `model_versions`: proposed by four analysis PRDs, each naming different parts of it, and read by a service that does not list it | shape, key | F3, A1, A2, A3, A4, C15, C6 |
| [CF-059](#cf-059) | Tables, views and storage paths named in one PRD only (required list) | single-PRD | F3, F8, F4, A5, C10, A1, A2, A3, A4, C1, C3, C12, W5, N7, C7, X4, X... |
| [CF-060](#cf-060) | Whose `idempotency_key` wins: the producer's envelope key or normalize-item's mapper key | key | F2, F4, F6, C4, C13, X7, every `raw.items` producer |
| [CF-061](#cf-061) | One YouTube video, two keys and two kinds: `youtube:post:` against `youtube:video:` | key, enum | F2, C4, YT2, YT3, YT4, YT8, YT9, W3 |
| [CF-062](#cf-062) | TikTok videos: `tiktok:video:` keys under `kind = post` or `kind = video`, and `tiktok:post:` in normalize-item | key, enum | F2, C4, TT1, VTT1, VTT2, VTT4, VTT5, VTT6 |
| [CF-063](#cf-063) | Telegram message keys: `telegram:post:<username>/<id>` against `telegram:message:<chat_id>:<id>` | key | F2, C4, TG1, TG2, VTG1, VTG3 |
| [CF-064](#cf-064) | LinkedIn post and comment keys differ by route: share URN, activity URN, bare id | key | F2, C4, LI1, LI2, LI3, VLI1, VLI3, VLI4 |
| [CF-065](#cf-065) | An X reply: `x:comment:<id>` from x-replies-fetcher, `x:post:<id>` from every other X reader | key, enum | F2, C4, X1, X4, X5, X6, X7 |
| [CF-066](#cf-066) | Instagram: vendor ids against Graph ids for the same post, and hash-based comment keys | key | F2, C4, IG2, IG3, IG5, VIG1, VIG2 |
| [CF-067](#cf-067) | Comments without platform ids, and how an edited comment is keyed: same key and a version, or a new key | key, rule | F2, C4, FB5, FB7, VFB3, VIG2, VLI4, N8 |
| [CF-068](#cf-068) | Item kind vocabulary: `post`/`video`, `post`/`message`, `comment`/`reply`, and kinds no consumer handles | enum | F2, C4, C5, C6, C8, LI3, VTG2, X6 |
| [CF-069](#cf-069) | Author identity: three field names, four derivations, several renderings and scopes | names, types, key | F2 (helper and golden vectors), F4, F6, C4, C6, C7, C8, C9, C13, C1... |
| [CF-070](#cf-070) | `job_id` formats: ULID in CONVENTIONS, and UUIDs, `job_…`, dated sequences and composite strings in examples | types, key | F2, F4, F6 |
| [CF-071](#cf-071) | `item_id`: uuid v5 of the key in items, ULIDs in deletion targets | types, key | F2, C4, C6, C13, C14, X7, YT7 |
| [CF-072](#cf-072) | `client_id` and `keyword_id` value formats: UUIDs against `cl_17` and `kw_0412` | types | F2, F3 |
| [CF-073](#cf-073) | `candidate_key` forms: two forms in CONVENTIONS, typed and domain forms in the routers and one resolver | key | F2, C8, IG2, VLI2, YT1, YT9, W3, W5 |
| [CF-074](#cf-074) | `post_ref` in comment, reply and metrics jobs: an object from the scheduler, a different string in every fetcher | shape, key | F2, C11, FB4, FB5, VFB3, IG4, IG6, VIG2, LI2, VLI4, VTT5, VTT6, TG2... |
| [CF-075](#cf-075) | Analysis keys and lanes (README decision 7): a four-part key from analysis-topics, a store keyed on `item_id, model`, lanes per service | key, names, document | F2, F8, C6, A1, A2, A3, A4 |
| [CF-076](#cf-076) | `deletions` reasons, scopes and modes that deletion-propagator does not list | enum | F2, C13, C14, X7, YT7, TT1, A5 |
| [CF-077](#cf-077) | The job vocabulary: `kind` or `reason`, seven kinds in CONVENTIONS and about thirty in the PRDs, and job fields outside the list | job kind, enum, names, shape | F2, F4, F5, F6, and every service that consumes or produces a job |
| [CF-078](#cf-078) | Job kinds no producer emits | job kind | F2, F4, C4, C5, C8, C11, C15, A1, A2, A3, A4, IG6, X5, W1, W2, YT9,... |
| [CF-079](#cf-079) | Job kinds a producer emits that the consumer does not accept | job kind | F2, C10, C11, C8, N3, TG2, VLI2, VTG2, IG4, IG5 |
| [CF-080](#cf-080) | Comment, reply and metrics work emitted by services other than comment-decay-scheduler | rule, writers, job kind | F2, C10, C11, IG4, IG5, IG6, YT4, YT5, YT6, YT7, LI2, VLI4, FB3, TT1 |
| [CF-081](#cf-081) | Metrics refresh jobs: `metrics` with `+24h`, or `refresh_24h` and `refresh_7d`, labels `24h`/`7d`/`client`, and the anchor | job kind, enum, rule | F2, C11, FB4, IG3, VTT6, TT1, YT4, VTG3 |
| [CF-082](#cf-082) | Count refreshes on X, LinkedIn and Telegram: +24 h and +7 d in CONVENTIONS, first sight only in the README, a Tier 1 +24 h views refresh in tg-channel-posts-poller | rule, job kind, document | C11, VTG3, LI1, VLI3, X1, X3, X4 |
| [CF-083](#cf-083) | `first_sight` jobs on `jobs.yt-video-details-fetcher`: four producers, four shapes | shape, job kind | F2, YT2, YT3, YT4, YT8, YT9 |
| [CF-084](#cf-084) | X gap and history jobs: `reconciliation` against `gap_backfill`, gap parts for x-full-archive-search, and two producers of `keyword_history` | job kind, shape, writers | F2, C10, X1, X4, X5 |
| [CF-085](#cf-085) | Resolver jobs: one request shape or eight, `rotation` or `refresh` for registered sources, producers that do not emit, and answer kinds no resolver sends | job kind, shape, writers | F2, C7, C8, C9, FB1, IG1, VTT3, X2, VLI2, VTG2, YT1, N2, W3, W4, W5... |
| [CF-086](#cf-086) | Webhook receivers' inbound buffer: a `push` job on the receiver's own queue, a raw body with no kind, or no buffer at all | job kind, shape, partition | F2, F4, IG4, FB7, YT2 |
| [CF-087](#cf-087) | Job queue partition keys other than `source_id`: candidates, keywords, keyword sets, hosts, and jobs with no source at all | partition, shape | F2, F4, F5, F6, FB1, IG1, VTT3, X2, VLI2, VTG2, YT1, N1, N2, FB6, V... |
| [CF-088](#cf-088) | Backfill jobs (README decision 4): the orchestrator's route table against the services that expect its job, services that backfill themselves, and the job's fields | job kind, rule, shape, document | F2, F5, C10, FB3, VFB1, VFB2, IG2, VIG1, IG5, VLI1, TT1, VTT1, VTT2... |
| [CF-089](#cf-089) | How a finished job reports back (README decision 1): `jobs.completed` from the SDK wrapper, from the service itself, or another channel; report fields and status values | names, shape, enum, writers, document | F2, F4, F5, F6, C10, C11, FB3, FB5, VFB3, IG6, VIG2, VTT5, VTT6, X1... |
| [CF-090](#cf-090) | What a job does with a governor `deny` or `wait-until`: requeue with `attempt + 1`, park, keep `next_poll_at`, finish `quota_denied`, end `capped`, or drop after 24 h | rule, enum | F4, F5, F6, C1, C10, C11, TT1, VTT1, VTT2, VTT3, VTT4, VTT5, FB3, X... |
| [CF-091](#cf-091) | When a job reaches its DLQ: after the fifth attempt or on the sixth failure, and Facebook error 80001 as a retry or a deferred poll | rule | F4, F6, FB2, VTG3, VTT1, VTT2, W1, W2 |
| [CF-092](#cf-092) | News hosts' 4xx: does a 429 or a feed, sitemap or homepage 404/410 send news-robots-checker a `recheck`, and does the host gate double its spacing after a 429 | rule | F4, F5, N1, N2, N3, N4, N5, N6 |
| [CF-093](#cf-093) | `recompute` jobs on `jobs.aggregator`: bucket lists with a `done` reply from deletion-propagator, a date-range ops job in aggregator | job kind, shape | F2, C13, C15 |
| [CF-094](#cf-094) | A platform 401 or 403 (README decision 5): `degraded` in CONVENTIONS and most fetchers, `blocked` in the README and the canary; and what carries the state (token, key, route, page or source) | enum, rule, document | F3, F4, F5, C7, C12, and every green fetcher (named here: TT1, LI1,... |
| [CF-095](#cf-095) | `tier`: numbers or words, and what it means on keyword rules, hashtags and news sites, whose cadences are not the reach tiers' | enum, types, rule, document | F3, F5, C1, C7, C9, W1, W2, W4, N2, N3, N4, N5, X1, YT8, YT9, IG2, ... |
| [CF-096](#cf-096) | `tier = push` (README decision 8): "no polling and one reconciliation a day" for client-owned properties, against hourly TikTok reads, Telegram health checks, LinkedIn polling, every YouTube channel and X coverage kept beside the tier | enum, rule, document | F3, F5, C1, C7, C9, TT1, VTT4, TG1, TG2, LI1, LI3, YT2, YT3, FB2, F... |
| [CF-097](#cf-097) | Vendor names: flag values, `sources.vendor` values and envelope values spelled three ways, search engines in `vendor` on green records, a source row's vendor differing from the vendor that reads its posts, and Actor publishers outside the cleared list | enum, names, document | F2, F3, F4, C7, C12, VTG2, VTG3, VLI1, VLI2, VLI3, VLI4, W1, W2, W4... |
| [CF-098](#cf-098) | `source.events` event types: `tier change` or `tier_change`, a `route` event and a lease-lapse reason nobody emits, and no event for `blocked` | enum, names | F2, C7, C12, LI1, YT2, YT3, IG2, IG3, FB2, N3, TG1, and every `sour... |
| [CF-099](#cf-099) | Budget tags: names outside the canonical list, wildcard rows in quota-governor, and external calls that ask the governor for nothing | budget, names, rule | F3, F5, C1, IG2, A1, A2, A3, A4, W5, TG1, TG2, YT2, X7, VLI2, YT4, ... |
| [CF-100](#cf-100) | Budget priorities (README decision 2): client refreshes at 1 or 3, first sight at 1 for every tier, a priority-1 history read, and priorities sent by callers | budget, enum, document | F5, C1, C11, YT4, YT5, YT6, YT7, YT8, X4, X5, X6, VTT3, VTG2, FB6 |
| [CF-101](#cf-101) | Budget modes on metered green tags (X, YouTube): README decision 2 gates priorities on every budget, CONVENTIONS stretches and sheds hot extras only on amber routes | budget, rule, document | F5, C1, C11, X1, X3, X6, YT4, YT5 |
| [CF-102](#cf-102) | Where the vendor flags live: environment variables in CONVENTIONS, read "at the start of every job" and by every shared service; and `fallback_on` as a flag or a health value | flag, document | F3, F4, F5, F6, C1, C8, C9, C10, C11, C12, IG2, VTT1, VTT2, VTT4, a... |
| [CF-103](#cf-103) | Flag values: one vendor per flag where two roles or a fallback need two, `TG_POSTS_ACTOR` missing from the flag list, a vendor value with no endpoint for one service, and the X plan gate | flag, enum, document | F3, F4, C12, VTG1, VTG2, VTG3, VTT1, VTT2, VTT3, VTT4, VTT5, VTT6, ... |
| [CF-104](#cf-104) | Retention classes for routes CONVENTIONS gives none: green TikTok (`tiktok_display`, README decision 8), green Telegram (`vendor_agreed`), web-search results (`news_excerpt`) | retention, document | F3, F8, C6, C14, TT1, TG1, TG2, W1, W2, W4, W3, YT9 |
| [CF-105](#cf-105) | LinkedIn data: amber records under `vendor_agreed` or `linkedin_48h`, one green class for organization and member fields, and member profile data at 24 hours | retention, document | F3, F8, C4, C6, C14, LI1, LI2, LI3, VLI1, VLI2, VLI3, VLI4 |
| [CF-106](#cf-106) | Derived data lifetimes: ten years for every class, against 36 months for YouTube (from creation or from the last fetch) and 48 hours for LinkedIn member analysis rows; and what `youtube_30d_text` covers | retention, rule, document | F3, F8, C6, C13, C14, C15, YT1, YT4, YT5, YT7, LI2, VLI4 |
| [CF-107](#cf-107) | Early stop (README decision 3): when it is armed, and what the 5% is measured against | rule, document | C11, FB5, VFB3, IG6, VIG2, VTT5, X6, YT5, YT6, LI2, VLI4, N8 |
| [CF-108](#cf-108) | Disqus comment series: +6 h, +24 h, +3 d in four documents, the full decay series in news-site-resolver | rule | C11, N2, N8 |
| [CF-109](#cf-109) | `raw.items` "exactly as returned" (README decision 8): edge hashing in ten other services, not only TikTok, news records that hold an extract, and services that write no raw record | rule, document | F2, F4, C2, C4, X6, YT5, YT6, FB7, VFB2, VFB3, VFB1, VIG1, VIG2, IG... |
| [CF-110](#cf-110) | The search output rule: every found item on `raw.items`, against web engines that archive whole responses with `normalize = skip` and publish results on `search.results` | rule, document | F2, C4, C5, W1, W2, W3, W4, YT9 |
| [CF-111](#cf-111) | The news 7-day full-text cache (README decision 6): the extractor as owner, a second writer for comments, and the question still open in two PRDs | writers, rule, document | F4, C4, C5, C13, C14, N6, N7, N8, A1, A2, A3 |
| [CF-112](#cf-112) | lang-dialect-id in Python: a third exception to the Node rule | rule, single-PRD | C3, F4, F6 |
| [CF-113](#cf-113) | When a missing post or comment becomes a `deletions` message: one error, a confirmed second miss, two full reads, or never | rule | F4, C13, FB4, FB5, VFB3, YT4, YT5, VTT5, VTT6, X6, VIG2 |
| [CF-114](#cf-114) | Rotation mechanics: a "shared scheduler" for Instagram hashtags, and due times kept outside `sources.next_poll_at` when two services rotate one row | rule | F3, F5, IG2, IG5, VIG1, FB6 |
| [CF-115](#cf-115) | X keyword coverage on the filtered stream: every client brand keyword set, or the tier-1 keyword rules x-recent-search names | rule | X1, X4 |
| [CF-116](#cf-116) | "Already approved; do not rewrite" (CONVENTIONS L282): twenty PRDs that sit on one side of entries in this file, several against CONVENTIONS itself | document | F2, and every session whose PRD is listed in L282 (FB6, FB2, FB3, F... |
| [CF-117](#cf-117) | Smaller CONVENTIONS and README inconsistencies (wording, lists and labels), for one batch decision | document | F2, F5, C1, YT5, YT6 |
| [CF-118](#cf-118) | News article and URL keys: `news:url:<hex>`, `news:article:<hex>` and `news:article:sha256:<hex>` | key, types | F2, C4, N3, N4, N5, N6, N7, W3 |


## 1. Topics and messages

### CF-001

**Message metadata: a `schema` string, a `schema_version` integer, or no version at all**

- **Type:** names, types, shape
- **Where:**
  - a) `schema` as a string `"<topic>/v1"` beside `message_id`, `produced_at` and a `producer {service, version, job_id}` block: `normalize-item §6.2 L95-L98` (`"schema": "items.normalized/v1"`), `keyword-matcher §6.2 L99-L102` (`"discovery.hits/v1"`), `analysis-sentiment §6.2 L93-L96` (`"items.analysis/v1"`; same in `analysis-entities §6.2 L94`, `analysis-topics §6.2 L97`, `analysis-media §6.2 L91`).
  - b) `schema` as a string with a flat `service` field: `news-dedup §6.2 L88`, `L100` (`"news.dedup/v1"`, `"service": "news-dedup"`), `news-robots-checker §6.2 L97` (`"crawl.policies/v1"`), `news-site-resolver §6.2 L83` and `tg-channel-resolver §6.2 L83` (`"poster.profiles/v1"`), `tg-message-search §6.2 L79`, `search-hit-router §6.2 L103` and `web-commoncrawl-scanner §6.2 L88` (`"discovery.hits/v1"`), `search-hit-router §6.2 L121` (`"article.urls/v1"`), `web-search-perplexity §6.2 L94-L97` (`"search.results/v1"`, `message_id`, `produced_at`, `service`; same in `web-search-mojeek §6.2 L93`, `web-gdelt-poller §6.2 L96`), `comment-decay-scheduler §5.4 L127` and `backfill-orchestrator §5.4 L92` (`"jobs.completed/v1"`).
  - c) `schema_version` as an integer: `poster-resolver §6.2 L89` (`"service":"poster-resolver","schema_version":1`), `qualifier §6.2 L84` (`registry.decisions`), `registry-writer §6.2 L95` (`source.events`).
  - d) No version field at all: every `raw.items` envelope (for example `fb-page-feed-poller §6.2 L110-L126`), the `item.metrics` examples (`fb-reactions-fetcher §6.2 L104-L123`), the `deletions` examples (`retention-purger §6.2 L96-L107`), the news pollers' `article.urls` (`news-feed-poller §6.2 L94-L112`), the canary's `registry.decisions` message (`source-health-canary §6.2 L102`), the resolvers' `poster.profiles` (`fb-page-resolver §6.2 L99-L128`) and the `discovery.hits` of `fb-page-search §6.2 L95-L116`, `ig-hashtag-search §6.2 L124`, `x-recent-search §6.2 L133`.
  - e) Consumers that branch on the field: `store-writer §5.2 L46` "Check each message's `schema`; an unknown version is parked in `dlq.store-writer`, never guessed", for six topics including `item.metrics` and `source.events` (`§5.1 L39`); `search-hit-router §5.2 L55` parks a message without `schema = search.results/v1`. `poster-resolver §1 L9` "merges their answers into one `poster.profiles` schema".
  - f) CONVENTIONS L12 puts "topic schemas" in `listening-sdk` but names no version field.
- **At stake:** as written, store-writer parks every `item.metrics` message and every `source.events` message (which carry `schema_version` or nothing), and the SDK cannot validate one topic whose producers version it three ways.
- **Options:** (1) `schema: "<topic>/v<n>"` on every message of every topic, with `message_id`, `produced_at` and `producer {service, version, job_id}`; (2) an integer `schema_version` on every message, the topic implied by the topic name, with `message_id`, `produced_at`, `service`; (3) the version travels in a Redpanda header set by the SDK, and no message carries it in the body.
- **Blocks:** F2, F4, F6, C6, W3, C8, C9, C7, and every producer of a topic.

### CF-002

**Provenance and `retention_class` on messages: which topics carry them, under which names**

- **Type:** names, shape, retention
- **Where:**
  - a) The rule: `CONVENTIONS L115` "Every item carries provenance (route class, vendor, service, fetch time)", with no field names; `CLAUDE.md L11` "Every output carries provenance (route, vendor, service, fetched_at) and `retention_class`".
  - b) Fetch time missing or under another name: the news pollers' `article.urls` envelopes carry `found_at` and no `fetched_at` (`news-feed-poller §6.2 L102`, `news-homepage-differ §6.2 L107`, `news-sitemap-poller §6.2 L114`); search-hit-router's `article.urls` carries `first_seen_at` and no `route`, `vendor`, `fetched_at` or `retention_class` (`search-hit-router §6.2 L121-L130`); `fb-page-search §6.2 L102` `found_at`; keyword-matcher's hit has no `fetched_at` (`keyword-matcher §6.2 L113-L114`); search-hit-router's and web-commoncrawl-scanner's `discovery.hits` have neither `fetched_at` nor `retention_class` (`search-hit-router §6.2 L106-L113`, `web-commoncrawl-scanner §6.2 L89-L99`); the analysis messages carry `item_fetched_at` (`analysis-sentiment §6.2 L103`); `poster.profiles` from poster-resolver and li-org-resolver carry `resolved_at` and no `fetched_at` or `retention_class` (`poster-resolver §6.2 L89`, `li-org-resolver §6.2 L101-L102`), and news-site-resolver's only inside `proposed_source` (`news-site-resolver §6.2 L91`, `L108`); `item.metrics` carries `observed_at` flat (`fb-reactions-fetcher §6.2 L114`, `yt-video-details-fetcher §6.2 L144`) or envelope `fetched_at` plus `observation.observed_at` (`tt-video-stats-refresher §6.2 L96`, `L104`).
  - c) Which `service`: keyword-matcher's hit carries `"service": "x-recent-search"`, the fetcher, beside `producer.service` (`keyword-matcher §6.2 L102`, `L113`); the analysis messages carry only `producer.service`, the analysis service, so the fetching service is lost (`analysis-sentiment §6.2 L96`, `L104`); poster-resolver writes `"service":"poster-resolver"` plus `"resolver":"ig-account-resolver"` (`poster-resolver §6.2 L89`); ig-account-resolver nests the four as `provenance {route, vendor, service, fetched_at}` (`ig-account-resolver §6.2 L119-L120`).
  - d) `retention_class` or `route`/`vendor` missing: the web engines' `raw.items` envelope lists no `retention_class` (`web-search-perplexity §6.2 L89`, `web-search-mojeek §6.2 L88`, `web-gdelt-poller §6.2 L91`); yt-web-search-bridge's `search.results` has none (`yt-web-search-bridge §6.2 L107-L123`); x-recent-search's hit carries no `route`, `vendor` or `retention_class` (`x-recent-search §6.2 L133`); ig-hashtag-search's hit no `vendor` or `retention_class` (`ig-hashtag-search §6.2 L124`); li-org-resolver calls its profile "registry metadata about an organization, kept as long as the source exists" (`li-org-resolver §7 L115`); ig-account-resolver's individual message carries "only `candidate_key_hash`, `resolution`, `account_class = individual`, `reason`, cache and provenance" (`ig-account-resolver §6.2 L127`) while `§13 L187` says every message carries `retention_class = meta_on_request`.
- **At stake:** a message without a class cannot be expired or purged by class, and one without fetch time and fetching service cannot feed the client-facing provenance statement; with four spellings (flat, `envelope`, `provenance {}`, `producer {}`) the SDK cannot stamp or check provenance in one place.
- **Options:** (1) every message on the data topics (`raw.items`, `items.normalized`, `item.hits`, `discovery.hits`, `poster.profiles`, `item.metrics`, `items.analysis`, `article.urls`, `search.results`) carries flat `route`, `vendor`, `service` (the fetching service), `fetched_at` and `retention_class`, with the producing service only in `producer`; (2) the same five as one nested `provenance {route, vendor, service, fetched_at}` object plus `retention_class`; (3) only `raw.items` and `items.normalized` carry provenance, and derived messages carry `item_id` (or `candidate_key`) for readers to join, with the exempt topics listed.
- **Blocks:** F2, F4, F6, C5, C6, C8, A1, A2, A3, A4, N3, N4, N5, W1, W2, W3, W4, W5, FB6, IG1, IG2, X1, VLI2, YT9.

### CF-003

**Topic partition keys that depart from the `source_id` default, and search records without a `source_id`**

- **Type:** partition, key
- **Where:**
  - a) The rule: `CONVENTIONS L14` "Topics (all partitioned by `source_id` unless noted)"; nothing is noted for any of the thirteen topics (L15-L27).
  - b) `search.results` by `canonical_url_hash`: `web-search-perplexity §6.2 L90`, `web-search-mojeek §6.2 L89`, `web-gdelt-poller §6.2 L92` (yt-web-search-bridge states no key, `yt-web-search-bridge §6.2 L102`).
  - c) `crawl.policies` keyed by `host`: `news-robots-checker §6.2 L93`, and "messages keyed by `host` and `policy_version`" (`§9 L144`).
  - d) `news.dedup` by `story_id`: `news-dedup §6.2 L84`.
  - e) `deletions`: `source_id`, but author-scope messages keyed by `author_hash` (`retention-purger §6.2 L94`, `x-compliance-sync §6.2 L97`); `deletion-propagator §14 Q4 L174` "the topic note in CONVENTIONS needs that exception"; `yt-text-purger §6.2 L137` keys by `source_id`.
  - f) `raw.items` from the web engines by `web:<source_id>`: `web-search-perplexity §6.2 L89`, `web-search-mojeek §6.2 L88`, `web-gdelt-poller §6.2 L91`.
  - g) `registry.decisions` by `candidate_key` (or `source_id` for sweep decisions): `qualifier §6.2 L81`. (The canary's decisions carry neither; see CF-015 d).)
  - h) Disagreement, not an agreed exception: `normalize-item §5.1 L41` says "records without a `source_id` (keyword searches, hashtag feeds, search results) are keyed by the producer on `<platform>:<poster platform_id>`", and `§6.2 L91` keys `items.normalized` "by `source_id` or poster key"; `keyword-matcher §5.1 L40` and `store-writer §5.1 L39` follow that poster key. `CONVENTIONS L281` instead has a search service set `source_id` to "the keyword-rule or hashtag source that produced the query", as the search examples do (`x-recent-search §6.2 L106-L107`, `ig-hashtag-search §6.2 L106`); `li-post-search §6.2 L87-L94` sets no `source_id`.
  - The topic-level keys of `discovery.hits` and `poster.profiles`, where producers disagree among themselves, are in CF-011 and CF-013. The job-queue partition keys are CF-087.
  - Overlaps: `AU-019` (partition of search finds on `raw.items`); `CF-087` in this file (job-queue keys).
- **At stake:** the contracts package fixes one key per topic; a search item keyed by the poster on `items.normalized` lands on another partition than its keyword rule's other items, and a consumer that assumes `source_id` everywhere mis-orders `search.results`, `crawl.policies`, `news.dedup` and author-scope `deletions`.
- **Options:** (1) record b) to g) as noted exceptions in CONVENTIONS v1.1, and require every search producer to set `source_id` to its keyword-rule or hashtag source so h) disappears; (2) record b) to g) and also allow the poster key on `items.normalized` and the hit topics when `source_id` is absent; (3) `source_id` everywhere: messages about things that are not sources carry the `source_id` of a related row (keyword rule, news site, client) and the other keys move into the body.
- **Blocks:** F2, F4, C4, C5, C6, C13, C14, X7, N1, N7, W1, W2, W3, W4, VLI1.

### CF-004

**`raw.items`: a nested `{envelope, payload}` message or a flat record, and where the platform record sits**

- **Type:** shape, names
- **Where:**
  - a) Nested `"envelope": {...}` beside `"payload": {...}`: `fb-page-feed-poller §6.2 L110-L126` and most producers, for example `ig-account-media-poller §6.2 L106-L123`, `li-post-search §6.2 L85-L102`, `tt-profile-videos-poller §6.2 L107-L124`, `x-user-timeline-poller §6.2 L114-L132`, `yt-comments-fetcher §6.2 L112-L134`.
  - b) Flat top-level fields with the record under `payload`: `ig-hashtag-search §6.2 L98-L121` (adds `edge`; no `platform_id`, `attempt`, `batch`), `yt-keyword-search §6.2 L101-L120`.
  - c) Flat top-level fields with the record under `raw` (and `includes`), plus `source_type` and `context`: `tt-keyword-search §6.2 L76-L100`, `tt-hashtag-feed-poller §6.2 L82-L105`, `x-recent-search §6.2 L101-L130`; x-recent-search's own prose still calls `context` part of "the envelope" (`§5.2 L58`).
  - d) Envelope fields given only as a prose list, nesting not stated: the web engines (`web-search-perplexity §6.2 L89` "envelope `service`, `route = green`, ..."; `web-search-mojeek §6.2 L88`; `web-gdelt-poller §6.2 L91`) and tg-message-search ("every result as returned, plus envelope", `tg-message-search §6.2 L73`; fields `tg-message-search §13 L143`).
  - e) The readers assume nesting: `raw-archiver §5.2 L50` reads `envelope.raw_ref`, `§5.2 L51` appends "envelope plus payload, unchanged", `§5.3 L67` writes "an `envelope` file (flattened envelope fields ...) and a `payload` file"; `normalize-item §5.2 L49` "read the envelope".
  - f) Both shapes are on CONVENTIONS' "already approved; do not rewrite" list (`CONVENTIONS L282`): fb-page-feed-poller, fb-backfill and li-post-search (nested) beside ig-hashtag-search, tt-keyword-search, tt-hashtag-feed-poller, x-recent-search and yt-keyword-search (flat). `CONVENTIONS L15` says only "every record exactly as a fetch or push returned it, plus envelope".
  - the required field set is CF-005.
- **At stake:** raw-archiver splits each message into envelope and payload files by the `envelope` key and normalize-item maps the payload; a flat record has no `envelope`, and `raw` or `includes` is not `payload`, so the same contracts type cannot read both and five approved PRDs would not round-trip through the archive.
- **Options:** (1) nested `{envelope, payload}` for every producer, as in fb-page-feed-poller, with `includes` and other response parts inside `payload`; (2) flat records with reserved top-level envelope names and the platform record always under `payload`; (3) both accepted on the wire, the SDK producer wrapping flat records into `{envelope, payload}` before publishing.
- **Blocks:** F2, F4, F6, C2, C4, FB4, IG2, VTT1, VTT2, X1, YT8, VTG1, W1, W2, W4.

### CF-005

**`raw.items` envelope: the required fields, who computes the key and class, and `batch` against `raw_ref`**

- **Type:** shape, names, writers
- **Where:**
  - a) The usual set, as in `fb-page-feed-poller §6.2 L112-L123`: `platform`, `kind`, `route`, `vendor`, `service`, `source_id`, `platform_id`, `idempotency_key`, `job_id`, `attempt`, `fetched_at`, `retention_class`, `client_ids`, `batch`. `raw-archiver §5.4 L86` lists the same envelope without `attempt`, with `raw_ref` and "the Facebook services' `batch`". CONVENTIONS names no envelope fields (`CONVENTIONS L15`).
  - b) Producers without some of them: no `job_id` in `news-article-extractor §6.2 L93-L106`; `update_id` instead of `job_id` in `tg-bot-channel-receiver §6.2 L123` and `tg-discussion-receiver §6.2 L127`; `"job_id": null, "attempt": null` in `x-filtered-stream §6.2 L121`; no `source_id`, `platform_id`, `client_ids` or `batch` in `li-post-search §6.2 L87-L94`; no `attempt`, `client_ids` or `batch` in `yt-video-details-fetcher §6.2 L94-L111`; no `client_ids` or `batch` in `tt-keyword-search §6.2 L76-L100`, `tt-hashtag-feed-poller §6.2 L82-L105`, `yt-keyword-search §6.2 L101-L120`; no `batch` in `news-comments-fetcher §6.2 L96-L106`; no `platform_id`, `attempt` or `batch` in `ig-hashtag-search §6.2 L98-L121`; and the web engines list no `kind` (`kind_hint = search_response` instead), `idempotency_key`, `platform_id`, `retention_class`, `client_ids`, `attempt` or `batch` (`web-search-perplexity §6.2 L89`, `web-search-mojeek §6.2 L88`, `web-gdelt-poller §6.2 L91`).
  - c) Who computes the key and the class: producers stamp `idempotency_key` and `retention_class` in the envelope (`fb-page-feed-poller §6.2 L117`, `L120`), while `normalize-item §5.2 L51` computes `idempotency_key` itself from its mapper and `§5.2 L55` stamps `retention_class` "(source row, else route and platform default)". The key formats the two sides produce differ (CF-061, CF-062, CF-063, section 3 (keys, jobs, values)).
  - d) Fields the reader needs that almost no producer writes: `normalize-item §5.2 L49` reads `job_kind` and `api_version` from the envelope and `§5.2 L50` selects the mapper "by `(service, api_version)`; no match or a missing required field raises `schema_unknown`". `api_version` is listed only by `web-search-perplexity §6.2 L89` and `web-search-mojeek §6.2 L88`; `job_kind` only by `x-full-archive-search §6.2 L112` and the three web engines (the backfill side of `job_kind` is `AU-015`).
  - e) The object reference: `raw-archiver §5.2 L50` reads `envelope.raw_ref` (`<object key>#<line>`) to pick the buffer, `§11 L157` has the SDK allocate `raw_ref`, and `normalize-item §5.2 L49` reads `raw_ref`; the producers' examples carry `batch`, an object key without a line (`fb-page-feed-poller §6.2 L122`, `tg-bot-channel-receiver §6.2 L128`, `news-article-extractor §6.2 L105`; 33 producers' examples carry `batch`), and only the web engines list `raw_ref`; `li-post-search §6.2 L83` says raw-archiver writes the batch object.
  - f) Producer-specific envelope fields with no shared definition (CONVENTIONS defines none): `edge` (`ig-hashtag-search §6.2 L110`), `mention_type`, `mention_of` (`ig-mentions-fetcher §6.2 L119`), `received_at` (`ig-webhook-receiver §6.2 L114`), `query {variant, rank}` (`fb-keyword-search §6.2 L112`), `window` (`fb-backfill §6.2 L104`), `connection_id`, `paid`, `matching_rules` (`x-filtered-stream §6.2 L121`, `L123`, `L126`), `ledger_key` (`x-replies-fetcher §6.2 L116`), `budget_tag`, `cost_units`, `paid` (`x-recent-search §6.2 L116-L118`; `cost_units` also `li-post-search §6.2 L93`, `yt-keyword-search §6.2 L117`), `partial`, `completes_partial_from`, `live_state`, `call_id` (`yt-video-details-fetcher §6.2 L103-L109`), `url_key`, `access_mode`, `usage_signals` (`news-article-extractor §6.2 L99`, `L103-L104`), `owned_by_client` (`tg-bot-channel-receiver §6.2 L126`). The fields that say why a record was read are CF-006; the comment fields are CF-007.
  - Overlaps: `CF-060` in this file (whose `idempotency_key` wins).
- **At stake:** as written, normalize-item finds no `api_version` on 46 of the 48 producers and parks their batches as `schema_unknown`; raw-archiver cannot place a record that carries `batch` but no `raw_ref`; records without `client_ids`, `job_id` or `retention_class` reach consumers that filter, log or expire on them.
- **Options:** (1) one required envelope set in the contracts package (the a) list plus `raw_ref`, `api_version` and `job_kind`), filled by the SDK producer from the job and the adapter, with an explicit optional list; (2) a small required set (`platform`, `route`, `vendor`, `service`, `source_id`, `fetched_at`, `raw_ref`, `api_version`) and everything else, key and class included, computed downstream by normalize-item; (3) required set per route family (job-driven fetchers, push receivers with `update_id`, archive-only web records), each written down.
- **Blocks:** F2, F4, F6, C2, C4, and every `raw.items` producer (N6, TG1, TG2, X4, VLI1, YT4, YT8, VTT1, VTT2, IG2, N8, W1, W2, W4).

### CF-006

**`raw.items`: how a record says why it was read (`metrics_observation`, `job_kind`, `origin`, `delivery`, `ingest_mode`)**

- **Type:** names, shape
- **Where:**
  - a) `metrics_observation` on post envelopes, with meanings that differ by producer: `poll` (`fb-page-feed-poller §6.2 L123`; also for a vendor keyword search, `ig-keyword-search §6.2 L111`), `backfill` (`fb-backfill §6.2 L103`, `x-full-archive-search §6.2 L122`, `ig-account-media-poller §5.1 L50`, `ig-keyword-search §5.1 L51`, `ig-mentions-fetcher §5.1 L49`), `search` (`fb-keyword-search §6.2 L114`), `first_sight` (`tt-client-videos-fetcher §6.2 L109`, `tt-profile-videos-poller §6.2 L120`, `yt-video-details-fetcher §6.2 L105`), `stream` (`x-filtered-stream §6.2 L130`), `refresh_24h` (`tg-channel-posts-poller §6.2 L128`), `null` (`yt-uploads-reconciler §6.2 L124`); made mandatory by `tt-profile-videos-poller §13 L182`, `x-filtered-stream §13 L201` and `fb-backfill §13 L165`. Its only reader is `fb-reactions-fetcher §3 L19` ("labelled with the envelope's `metrics_observation` (`poll`, `backfill`, `webhook_reconcile`)").
  - b) `job_kind`: written by `x-full-archive-search §6.2 L112` (beside `metrics_observation`) and the web engines (`web-search-perplexity §6.2 L89`), read by `normalize-item §5.2 L49`, and expected on `items.normalized` by `comment-decay-scheduler §5.1 L66` ("`job_kind = backfill` (carried from the raw envelope)"). The backfill case is entry `AU-015`.
  - c) The same fact under other names: `"origin": "search"` (`yt-keyword-search §6.2 L112`); `"delivery": "push"` (`fb-client-webhook-receiver §6.2 L125`, `ig-webhook-receiver §6.2 L118`, `yt-pubsub-receiver §6.2 L118`); `"ingest_mode": "webhook"` with `"event": "new"` (`tg-bot-channel-receiver §6.2 L119`, `tg-discussion-receiver §6.2 L120`). No reader is named for `origin`, `delivery` or `ingest_mode`.
  - d) CONVENTIONS defines none of these fields; `CONVENTIONS L65` only says counts are refreshed at +24 h and +7 d "by the source's metrics or details service, or by the next poll where the API returns counts with the post".
  - Overlaps: `AU-002` (backfill marker).
- **At stake:** three consumers read three different fields for one fact (backfill, push, search, first sight), so a record is labelled for one consumer and invisible to the next; `item.metrics` labels and the `once` comment fetch for backfilled posts depend on which field a producer happened to fill.
- **Options:** (1) one required `job_kind`, stamped by the SDK wrapper from the job's `kind` (with fixed values such as `push` and `stream` for jobless receivers), and `metrics_observation`, `origin`, `delivery`, `ingest_mode` dropped; (2) `metrics_observation` as the one label with a closed value list, and `job_kind`, `origin`, `delivery`, `ingest_mode` dropped; (3) both `job_kind` (why the job ran) and `metrics_observation` (what the counts in the payload are), each with a closed list, and the other names dropped.
- **Blocks:** F2, F4, F6, C4, C10, C11, FB4, FB3, FB7, IG4, YT2, YT8, TG1, TG2, X4, X5, VTG3.

### CF-007

**Comment records on `raw.items`: the parent link, the content hash, the edit marker and the redaction marker each go by several names**

- **Type:** names, shape
- **Where:**
  - a) Link to the parent: `parent_platform_id` (`fb-post-comments-fetcher §6.2 L108`, `fb-client-webhook-receiver §6.2 L118`, `fb-group-comments-fetcher §6.2 L113`, which adds `post_platform_id` for a reply's post, `L128`); `post_ref` plus `parent_id` (`ig-comments-fetcher §6.2 L108`, `ig-own-comments-fetcher §6.2 L122`, `ig-webhook-receiver §6.2 L118`, `tt-video-comments-fetcher §6.2 L107`); `post_ref` alone (`li-own-comments-fetcher §6.2 L115`, `li-post-comments-fetcher §6.2 L117`, `li-notification-receiver §6.2 L122`, `tg-discussion-receiver §6.2 L125`, beside `discussion_source_id`, `L122`); `parent_post_id`, `conversation_id`, `parent_comment_id`, `in_reply_to_ref` (`x-replies-fetcher §6.2 L117-L120`); `parent_video_id`, `parent_comment_id` (`yt-comments-fetcher §6.2 L120`, `yt-replies-fetcher §6.2 L109`); `parent_id` holding the article hash (`news-comments-fetcher §6.2 L100`). normalize-item reads none of these (its envelope list, `normalize-item §5.2 L49`) and derives `parent_id` from the payload (`normalize-item §5.3 L70`). The value formats of `post_ref` are section 3 (keys, jobs, values).
  - b) Content hash: `text_hash` as bare hex (`fb-group-comments-fetcher §6.2 L120`); `content_hash` with a `sha256:` prefix (`ig-comments-fetcher §6.2 L109`, `x-replies-fetcher §6.2 L121`, `yt-comments-fetcher §6.2 L123`); `text_sha256` inside the payload (`news-comments-fetcher §6.2 L112`). normalize-item computes its own `content_hash = sha256(title + text + media urls)` (`normalize-item §5.2 L51`). What the hash covers is entry `AU-090`.
  - c) Edit marker: a new key with `edit_of` = the old key, which "normalize-item stores ... as a new version" (`fb-post-comments-fetcher §5.2 L68`, `§6.2 L115`); the same key with `version` incremented (`fb-group-comments-fetcher §5.2 L65`, `§6.2 L120`; `version` also in `fb-client-webhook-receiver §6.2 L125`, `tt-video-comments-fetcher §6.2 L108`, and in the payload with `is_edited` in `news-comments-fetcher §6.2 L115`); `observation` = `new`, `edit` or `seen` (`x-replies-fetcher §6.2 L122`; `yt-comments-fetcher §6.2 L124`, `§13 L190`; `yt-replies-fetcher §6.2 L113`); `event` = `new` or `edit` with `edit_date` (`tg-bot-channel-receiver §5.2 L61`, `§6.2 L119`). normalize-item decides versions itself from its own key and hash (known key with a different hash → `version + 1`, unknown key → new item, `normalize-item §5.2 L52`) and never mentions `edit_of`.
  - d) Marker that the payload was altered before the write: `payload_redacted` (`fb-group-comments-fetcher §6.2 L122`, `fb-client-webhook-receiver §6.2 L127`), `removed_fields` (`x-replies-fetcher §6.2 L128`, `yt-comments-fetcher §6.2 L130`, `yt-replies-fetcher §6.2 L119`), `minimized: true` (`tg-discussion-receiver §6.2 L126`), `identity: "hashed"` (`li-post-comments-fetcher §6.2 L123`; `li-notification-receiver §5.2 L56`, position not stated). Whether edge hashing is allowed at all is CF-109.
  - Overlaps: `CF-067` in this file (how an edited comment is keyed).
- **At stake:** fb-post-comments-fetcher's edited comments arrive under a new key that normalize-item publishes as a new item, not as a version; a reader that needs the parent link, the hash or the list of removed fields from the envelope has to know every producer's spelling, and three hash renderings never compare equal.
- **Options:** (1) one comment block in the envelope (for example `post_ref`, `parent_ref`, `content_hash`, `version`, `redacted_fields`), defined in the contracts package and written by every comment producer, with edits always as same-key versions; (2) no comment fields in the envelope: normalize-item derives parent, hash and version from the payload, and the producers' extra fields are informational only; (3) as (1), with `edit_of` kept for keys that change on edit (PPCA comments) and read by normalize-item.
- **Blocks:** F2, F4, C4, C13, FB5, FB7, VFB3, VIG2, IG4, IG6, LI2, LI3, VLI4, VTT5, X6, YT5, YT6, N8, TG1, TG2.

### CF-008

**`raw.items` records normalize-item has no mapper for: unlisted producers, kinds `profile`, `reaction` and `search_response`, and partial YouTube records**

- **Type:** writers, shape
- **Where:**
  - a) The reader's rule: `normalize-item §5.2 L50` selects the mapper "by `(service, api_version)`; no match or a missing required field raises `schema_unknown`, parks the batch key in `review_queue` and skips the batch"; `§2 L15` "every record on `raw.items` is either published once to `items.normalized` ... or parked with a `schema_unknown` reason". The mapper table is `§5.3 L62-L73`.
  - b) Producers the table does not name: `yt-pubsub-receiver §6.2 L102`, `yt-uploads-reconciler §6.2 L108` and `yt-keyword-search §6.2 L96` (the YouTube line names only yt-video-details-fetcher, yt-comments-fetcher, yt-replies-fetcher, `normalize-item §5.3 L71`); `ig-keyword-search §6.2 L96-L115` (Instagram line, `normalize-item §5.3 L66`); `news-comments-fetcher §6.2 L92` (the only news line is the article, `normalize-item §5.3 L72`); `li-notification-receiver §3 L21` and `li-org-resolver §6.2 L79` ("`raw.items` (sampled posts)") (LinkedIn line, `normalize-item §5.3 L69`); fb-client-webhook-receiver's posts (`fb-client-webhook-receiver §3 L21`, kind `post` or `comment`), while its mapper line covers comments only (`normalize-item §5.3 L64`).
  - c) Kinds with no mapper: `profile` from `poster-resolver §6.2 L92` and `tg-channel-resolver §6.2 L77`; `reaction` from `li-notification-receiver §5.4 L98`, whose `§14 Q4 L201` asks whether normalize-item should "turn reaction events into counter increments"; `search_response` with `normalize = skip` from the web engines (`web-search-perplexity §5.2 L55`, `§14 Q5 L174` "Does normalize-item treat `kind_hint = search_response` as archive-only ...?"). The web-result side is CF-110.
  - d) Partial records: `yt-pubsub-receiver §6.2 L124` "`partial: true` makes normalize-item wait for details: it holds the record until yt-video-details-fetcher's full record under the same key arrives"; `yt-video-details-fetcher §3 L19` writes the full record "completing the partial one". normalize-item never mentions `partial`, and its YouTube key (`youtube:video:<id>`, `normalize-item §5.3 L71`) differs from the producers' `youtube:post:<id>` (CF-061).
  - Overlaps: `AU-052`, `AU-051` and `AU-004`; `CF-068` in this file (item kinds).
- **At stake:** under normalize-item's own rule, every batch from the producers in b) and c) is parked as `schema_unknown` and never reaches `items.normalized`, the hit topics or analysis; partial YouTube records are published or parked instead of held for completion.
- **Options:** (1) normalize-item's table covers every `raw.items` producer and kind, with `profile` and `search_response` declared archive-only (skipped, not parked), `reaction` mapped or skipped by decision, and a hold-and-merge step for `partial`; (2) only item producers write `raw.items`: profile and search-response archives move to their own path or topic, and reactions go to `item.metrics`; (3) each producer registers its own mapper in listening-sdk under `(service, api_version)`, so the table is generated from the producers rather than listed in normalize-item's PRD.
- **Blocks:** F2, F4, C2, C4, C8, YT2, YT3, YT4, YT8, VIG1, N8, LI3, VLI2, VTG2, FB7, W1, W2, W4.

### CF-009

**`item.hits`: a second writer, hits on individuals' comments, and `matched_term` against `matched_text`**

- **Type:** writers, names, shape
- **Where:**
  - a) Writers: `CONVENTIONS L281` makes keyword-matcher "the canonical writer of `item.hits` and `discovery.hits` for items" and lets a search service emit only `discovery.hits` directly; `tg-message-search §5.2 L55` "emits the message to `raw.items`, then a hit to `item.hits` (registered channel) or `discovery.hits` (unknown channel)" (`§13 L142`). The same message also reaches keyword-matcher through `raw.items` and normalize-item, and nothing tells keyword-matcher a hit was already sent.
  - b) What the topic holds: `CONVENTIONS L17` "keyword hits on items whose poster is already a registered source"; `keyword-matcher §5.3 L75` sends "Comments, replies and items with a null `author_ref`" to `item.hits` with `poster = {author_ref, author_type: "individual"}`, and `§14 Q3 L182` asks to confirm.
  - c) Shape: keyword-matcher's `item.hits` is its `discovery.hits/v1` message with `poster` in place of `candidate` (`keyword-matcher §6.2 L119`; `hit_id`, `item_id`, `client_id`, `keyword_id`, `hit_at`, L103-L110); tg-message-search gives no `item.hits` example, and its `discovery.hits/v1` example carries `keyword_ids[]`, `client_ids[]` and no `item_id`, `hit_id` or `hit_at` (`tg-message-search §6.2 L79-L91`). store-writer keys the ClickHouse `hits` table on `client_id, keyword_id, item_id` and partitions it by `hit_at` (`store-writer §5.3 L63`).
  - d) Field name: analysis-sentiment reads `matched_text` from hits (`analysis-sentiment §5.2 L59`, `§5.4 L80`) and asks to confirm "hit field names with keyword-matcher" (`§14 Q7 L174`); keyword-matcher writes `matched_term` (`keyword-matcher §5.3 L65`, `§6.2 L108`).
  - Overlaps: `AU-006` (`matched_text` against `matched_term`).
- **At stake:** a Telegram result from a registered channel yields two `item.hits` in two shapes, one of which store-writer cannot key; consumers that take `item.hits` to mean "registered poster" also receive individuals' comments; the aspect-sentiment path finds no `matched_text`.
- **Options:** (1) keyword-matcher is the only writer of `item.hits`, tg-message-search stops writing it, and CONVENTIONS' definition is widened to every hit that is not a candidate (comments and individuals included); (2) tg-message-search keeps writing `item.hits` in keyword-matcher's schema and keyword-matcher skips items whose producer already emitted hits, with CONVENTIONS' definition unchanged and individuals' mentions moved to their own topic; (3) as (1), with CONVENTIONS' definition kept and keyword-matcher sending individuals' mentions to a new mentions topic. With any option, one field name (`matched_term` or `matched_text`).
- **Blocks:** F2, C5, C6, A1, A5, VTG1.

### CF-010

**`discovery.hits` writers: services outside CONVENTIONS' list, client onboarding on the topic, and early hits keyword-matcher cannot see**

- **Type:** writers
- **Where:**
  - a) `CONVENTIONS L281` names the writers: keyword-matcher (canonical, for items), x-recent-search and tg-message-search (an early signal for unregistered authors), and fb-page-search, web-commoncrawl-scanner, search-hit-router (services that find sources). `CONVENTIONS L18` defines the topic as "keyword hits on items whose poster is not a registered source".
  - b) Writers not on that list: `ig-hashtag-search §6.2 L92` ("`discovery.hits` for media whose poster is not registered"; example `L124`); `tg-bot-channel-receiver §5.2 L70` ("a client-added candidate on `discovery.hits` (type `channel`, `origin = client_onboarding`, `proposed_source_id`, `owned_by_client`, client id)", `§6.2 L134`); `tg-discussion-receiver §5.2 L67` (a group candidate "with a pre-allocated `proposed_source_id`", `§6.2 L138`).
  - c) The path the readers describe for client-added sources is different: `poster-resolver §3 L27` "Resolving manual candidates submitted by ops or clients through `registry-writer` (same path, `origin: manual`)"; `qualifier §3 L27` "Manual candidates (`origin: manual`)". registry-writer's manual-add endpoint "publishes a `manual_candidate` to `jobs.poster-resolver` with `origin: manual`" (`registry-writer §5.2 L61`). None of the three names `client_onboarding` or `proposed_source_id`. (The onboarding records behind the pre-allocated id are entry `AU-026` in `CONFLICTS-ASSUMPTIONS.md`.)
  - d) Early hits: x-recent-search writes one hit "per unregistered author" (`x-recent-search §5.2 L58`) or "one per post with an unregistered author" (`§6.2 L98`, `§13 L184`), "flagging the envelope `context.discovery_hit_emitted = true` so keyword-matcher does not emit a second one" (`§5.2 L58`); neither normalize-item's envelope list (`normalize-item §5.2 L49`) nor keyword-matcher's PRD reads that flag. `fb-keyword-search §14 Q5 L185` proposes no early hits ("keyword-matcher does").
  - Overlaps: `AU-005` and `AU-057`.
- **At stake:** poster-resolver and the qualifier receive candidates through a path and with an `origin` they do not define, so client onboarding of Telegram channels and groups depends on fields only the two receivers know; every early hit is followed by a second one from keyword-matcher, kept harmless only by poster-resolver's `candidate_key` dedup (`CONVENTIONS L281`).
- **Options:** (1) the writer list stays as in CONVENTIONS, ig-hashtag-search joins it as a search service, and client-added channels and groups use registry-writer's manual path (`origin: manual`) instead of `discovery.hits`; (2) the list grows to the Telegram receivers, and `origin = client_onboarding` and `proposed_source_id` become schema fields that poster-resolver and the qualifier handle; (3) only keyword-matcher and the three source-finding services write the topic: the early signals stop and onboarding uses the manual path.
- **Blocks:** F2, C5, C7, C8, C9, IG2, X1, VTG1, TG1, TG2, FB6, VFB1, W3, W5.

### CF-011

**`discovery.hits` message: seven shapes, three partition keys, two of the shapes under one schema name**

- **Type:** shape, names, partition
- **Where:**
  - a) keyword-matcher, `"schema": "discovery.hits/v1"` (`keyword-matcher §6.2 L97-L117`): `message_id`, `produced_at`, `producer`, `hit_id`, `status`, `item_id`, `item_version`, `platform`, `kind`, `source_id`, `client_id`, `keyword_id`, `keyword_set_version`, `matched_term`, `offsets`, `hit_at`, `url`, `candidate {candidate_key, platform, platform_id, handle, author_ref}`, `candidate_pending`, `route`, `vendor`, `service`, `retention_class`, `raw_ref`; key `source_id`, "the source that produced the item" (`§6.2 L95`).
  - b) tg-message-search, also `"discovery.hits/v1"` (`tg-message-search §6.2 L79-L91`): `idempotency_key`, `platform`, `kind`, `poster {platform_id, handle, display_name, source_type}`, `keyword_ids[]`, `client_ids[]`, `route`, `vendor`, `service`, `fetched_at`, `retention_class`.
  - c) search-hit-router and web-commoncrawl-scanner, also `"discovery.hits/v1"`, key `candidate_key` (`search-hit-router §6.2 L99-L113`, `web-commoncrawl-scanner §6.2 L84-L99`): `message_id`, `produced_at`, `service`, `route`, `vendor`, `type`, `platform`, `candidate_key`, `poster_ref {handle, platform_id, url, post_ref, handle_hint}` or `{host, registrable_domain, url}`, `origin`, `evidence {...}` with `keyword_rule_ids` and `client_ids` inside it (router) or `keyword_rule_id` and `client_ids` at the top (scanner). Both say their field set "follows poster-resolver's approved schema where it differs" (`search-hit-router §6.2 L134`, `web-commoncrawl-scanner §6.2 L103`), but poster-resolver defines no `discovery.hits` schema: it only reads the topic, "the candidate is in the payload" (`poster-resolver §6.1 L81`).
  - d) No schema name: `fb-page-search §6.2 L95-L116` (`hit_type`, `found_at`, `keyword_id`, `query`, `client_ids`, `candidate {platform_id, name, link, is_verified, location}`, `context`, `job_id`); `ig-hashtag-search §6.2 L124` (`keyword_id` = "<hashtag source_id>", `matched_in`, `item_idempotency_key`, `permalink`, `poster {handle: null, platform_id: null, handles_in_caption}`); `x-recent-search §6.2 L133` (`item_idempotency_key`, `author_platform_id`, `author_handle`, `keyword_rule_id`, `matched_terms`, `client_ids`, `lang`, `public_metrics`, `service`, `fetched_at`); `tg-bot-channel-receiver §5.2 L70` (`type`, `origin`, `proposed_source_id`, `owned_by_client`, "client id").
  - e) One thing, several names: `candidate` / `poster` / `poster_ref` / `author_platform_id` + `author_handle`; `hit_type` / `type`; `hit_at` / `found_at` / `fetched_at` / `produced_at`; `client_id` / `client_ids` / `evidence.client_ids` / "client id"; `keyword_id` / `keyword_ids` / `keyword_rule_id` / `evidence.keyword_rule_ids`; `item_id` / `item_idempotency_key` / `idempotency_key`.
  - f) What the readers need: poster-resolver builds `candidate_key` from the message (`poster-resolver §5.2 L52`), records "the keyword and client" (`§5.2 L53`) and orders catch-up by "newest `hit_at` first" (`§5.1 L48`), partitioning "the keyword or hashtag source that produced the hit" (`§6.1 L81`); ig-hashtag-search's hit has neither handle nor platform id, so no `candidate_key` can be built (`CONVENTIONS L281` defines it as `<platform>:<platform_id>` or `<platform>:<handle>`); store-writer keys `hits` on `client_id, keyword_id, item_id` and partitions by `hit_at` (`store-writer §5.3 L63`), which the source-finding messages (c, d) do not carry. The `candidate_key` formats themselves are section 3 (keys, jobs, values).
  - Overlaps: `AU-008`; `CF-073` in this file (`candidate_key` forms).
- **At stake:** poster-resolver cannot build one decoder for seven layouts, and two layouts claim the same `discovery.hits/v1`; store-writer cannot key the source-candidate messages into `hits`; partitions by item source, by keyword source and by `candidate_key` give one candidate no stable order.
- **Options:** (1) keyword-matcher's `discovery.hits/v1` is the one schema, with `candidate` required and `type`, `origin`, `evidence` as optional fields for source-finding producers; (2) two schemas: item hits (keyword-matcher and the early-signal search services, keyed by the item's source) and source candidates (fb-page-search, search-hit-router, web-commoncrawl-scanner, onboarding, keyed by `candidate_key`), on one topic with a type field or on two topics; (3) poster-resolver's PRD defines the input schema and partition key, and every producer adopts it.
- **Blocks:** F2, F4, C5, C6, C8, FB6, IG2, X1, VTG1, TG1, TG2, W3, W5.

### CF-012

**`poster.profiles` writers: poster-resolver merges answers it expects on `jobs.poster-resolver`, while the eight resolvers publish their own profiles**

- **Type:** writers
- **Where:**
  - a) poster-resolver as the one writer: it "dispatches to the eight per-source resolvers ..., merges their answers into one `poster.profiles` schema" (`poster-resolver §1 L9`); its `resolve` job carries `"reply_to":"jobs.poster-resolver"` (`§5.3 L67`) and "The resolver answers on `jobs.poster-resolver` with `kind: resolved` ... or `kind: unresolvable`" (`§5.3 L70`, read per `§6.1 L82`); on the answer it classifies `account_type` (`§5.2 L57`), computes the language shares and `country_signals` and archives the payload as `raw.items` `kind: profile` (`§5.2 L58`), and writes `poster.profiles` (`§6.2 L86-L92`).
  - b) The resolvers publish `poster.profiles` themselves, and none writes `jobs.poster-resolver`: `fb-page-resolver §6.2 L99` ("one message per answer"; `§4 L33` "**qualifier** consumes `poster.profiles`"), `ig-account-resolver §6.2 L102`, `li-org-resolver §6.2 L79`, `news-site-resolver §6.2 L79`, `tg-channel-resolver §6.2 L77`, `tt-user-resolver §3 L22` and `§5.2 L57`, `x-user-resolver §6.2 L101`, `yt-channel-resolver §6.2 L103`. Each also classifies on its own (`resolved_type`, `qualifies_as`, `verdict`, `status`; see CF-013). x-user-resolver expects poster-resolver to match its answers on `poster.profiles` by `job_id` (`x-user-resolver §6.2 L132`), a topic poster-resolver does not read (`poster-resolver §6.1 L81-L82`).
  - c) Registered sources refreshed by the resolvers' own loops reach the topic without poster-resolver at all; three resolvers ask whether poster-resolver owns that refresh (`fb-page-resolver §14 Q1 L189`, `x-user-resolver §14 Q6 L196`, `yt-channel-resolver §14 Q5 L200`), and `tt-user-resolver §14 Q2 L170` proposes poster-resolver re-queues registered creators.
  - d) Readers: the qualifier gives "Every `poster.profiles` message ... exactly one decision" (`qualifier §2 L15`), reads "every field listed in the `poster-resolver` PRD" (`§5.4 L71`) and takes the individual flag "as classified by `poster-resolver`" (`§5.2 L52`); tg-channel-resolver also reads `poster.profiles` as a cache (`tg-channel-resolver §6.1 L73`).
  - The message shape is CF-013.
  - Overlaps: `AU-007`; `CF-085` in this file (resolver jobs).
- **At stake:** as written, poster-resolver waits on an answer queue no resolver writes, while the qualifier receives each candidate once from the resolver (in a shape it does not read) and possibly again from poster-resolver, so a candidate gets two decisions or none; the individuals rule runs in two places with two hashes.
- **Options:** (1) the resolvers answer poster-resolver on `jobs.poster-resolver` (or a dedicated answer topic) and only poster-resolver writes `poster.profiles`, in its schema; (2) the resolvers write `poster.profiles` in one common schema and poster-resolver only deduplicates and dispatches, writing nothing to the topic; (3) both write, each message marked as a resolver answer or a merged profile, and the qualifier decides only on merged profiles.
- **Blocks:** F2, C8, C9, FB1, IG1, X2, YT1, N2, VTT3, VLI2, VTG2.

### CF-013

**`poster.profiles` message: flat or `{envelope, profile}`, five names for the classification, four for the cache flag, and the key of an individual's answer**

- **Type:** shape, names, partition
- **Where:**
  - a) Flat, `"schema_version":1`: `poster-resolver §6.2 L89` with `account_type`, `individual`, `verified`, `followers`, `posts_30d`, `last_post_at`, `location_text`, `country_signals`, `lang_share`, `hits_30d`, `keywords`, `client_ids`, `resolver`, `resolved_at`, `cached`, `unresolvable` (and `schema_unknown`, `§8 L110`). The qualifier reads "every field listed in the `poster-resolver` PRD" (`qualifier §5.4 L71`).
  - b) Nested `{"envelope": {...}, "profile": {...}}`: `fb-page-resolver §6.2 L101-L126`, `x-user-resolver §6.2 L103-L130`, `yt-channel-resolver §6.2 L105-L132`, `tt-user-resolver §6.2 L88-L109` ("the topic's own schema", `§6.2 L86`).
  - c) Other flat layouts: `ig-account-resolver §6.2 L104-L125` (`resolution`, `account_class`, `cache {hit, resolved_at, expires_at}`, `provenance {...}`); `li-org-resolver §6.2 L81-L105` (`resolution`, `source_type`, `owned_by_client`, `resolved_at`); `tg-channel-resolver §6.2 L81-L102` (`"schema": "poster.profiles/v1"`, `idempotency_key`, `status`, `growth`); `news-site-resolver §6.2 L81-L110` (`"schema": "poster.profiles/v1"`, `kind: site`, `host`, `proposed_source {...}`, `site_profile {...}`, `discovered_by`).
  - d) The classification under five names: `account_type` + `individual` (poster-resolver), `resolved_type` (`fb-page-resolver §6.2 L113`, `x-user-resolver §6.2 L115`, `yt-channel-resolver §6.2 L117`) with `qualifies_as` (`x-user-resolver §6.2 L116`) or `verdict` (`yt-channel-resolver §6.2 L117`), `resolution` + `account_class` (`ig-account-resolver §6.2 L111-L112`), `resolution` (`li-org-resolver §6.2 L100`), `status` (+ `creator_threshold_met`) (`tt-user-resolver §6.2 L101`, `tg-channel-resolver §6.2 L95`). The cache flag: `cached` (poster-resolver), `"cache": "miss"` with `cached_until` (`fb-page-resolver §6.2 L108-L109`, `x-user-resolver §6.2 L110-L111`, `yt-channel-resolver §6.2 L112-L113`), `cache_hit` (`tt-user-resolver §6.2 L96`), `cache {hit, ...}` (`ig-account-resolver §6.2 L118`).
  - e) A field one reader names differently: `x-full-archive-search §5.2 L52` computes a posting rate from "`tweet_count` ÷ account age, from x-user-resolver's profile"; x-user-resolver writes `post_count` and `account_age_days` (`x-user-resolver §6.2 L121`, `L126`).
  - f) Partition and message keys: `candidate_key` (`poster-resolver §6.2 L86`); `source_id` for a registered source, else `candidate_key` (`fb-page-resolver §6.2 L99`, `yt-channel-resolver §6.2 L103`), else `candidate_ref` for individuals (`x-user-resolver §6.2 L101`); "keyed by `candidate_key` (and `source_id` when the request was a refresh)" (`ig-account-resolver §6.2 L102`); `CONVENTIONS L14` default `source_id`. For an individual, ig-account-resolver's key `candidate_key` may be `instagram:<handle>` (`§5.1 L42`) while the message must carry "no handle" (`§6.2 L127`), and tt-user-resolver's individual answer keeps "the same envelope" with `candidate_key` (`tt-user-resolver §6.2 L111`) while `§13 L156` allows no handle in the message. (The names and derivations of the individual's hash are CF-069, section 3 (keys, jobs, values).)
  - The signal blocks are CF-014. The writers are CF-012.
  - Overlaps: `AU-009`; `CF-046` in this file (resolver caches).
- **At stake:** the qualifier reads `account_type`, `individual`, `cached` and `unresolvable`, which only poster-resolver writes; a key that differs by outcome splits one candidate across partitions; a handle in the key of an individual's answer breaks the individuals rule.
- **Options:** (1) poster-resolver's flat schema is the topic schema for every writer, keyed by `candidate_key`, with individuals keyed by their hash; (2) one envelope plus a per-platform `profile` object, with the qualifier's fields (`account_type`, `individual`, `followers`, `verified`, `country_signals`, `lang_share`, `cached`) required in a common block; (3) resolver answers keep their per-platform layout on the answer channel of CF-012, and only poster-resolver's merged flat profile is on the topic.
- **Blocks:** F2, C8, C9, FB1, IG1, X2, X5, YT1, N2, VTT3, VLI2, VTG2.

### CF-014

**`country_signals` and `lang_share`: nine vocabularies and three JSON types for the qualifier's Iraqi-signal inputs**

- **Type:** names, types
- **Where:**
  - a) poster-resolver and the qualifier's decision: `country_signals {iraqi_place: true, phone_964, iq_domain, outlet_link, seed_list: false}` and `lang_share {ar_iq, ckb, ar_msa, en}` (`poster-resolver §6.2 L89`, `qualifier §6.2 L84`). The qualifier counts these signals in rule 2: an Iraqi place, a +964 number, an .iq domain or outlet link, "at least 40% Iraqi Arabic or Sorani", a client seed list (`qualifier §5.2 L53`).
  - b) Other writers of the same blocks: `li-org-resolver §6.2 L94-L95` (`country_signals {location: "Baghdad, Iraq", phone_964, iq_domain, seed_list: false}`, `lang_share {ar_iq, ckb, en}`); `news-site-resolver §6.2 L92-L93` (`{tld_iq, phone_964, iraqi_place: "Baghdad", seed_list: ["client_17"]}`, `{msa, iraqi_ar, en}`); `tg-channel-resolver §6.2 L91`, `L94` (`{vendor_country, text_signals: [...]}`, `{"ar-iq", ar, ckb, sample}`); `ig-account-resolver §6.2 L116` (`{phone_964, website_tld: "iq", city_in_bio: [...]}`).
  - c) The same evidence under `profile.signals` or `location`: `fb-page-resolver §6.2 L119`, `L121` (`location {city, country}`, `signals {iq_domain, phone_964}`), `x-user-resolver §6.2 L127` (`{location_iq: "Baghdad", iq_domain, phone_964}`), `yt-channel-resolver §6.2 L128` (`{country_iq, iq_place_names: [...], description_lang, iq_domain}`), `tt-user-resolver §6.2 L106` (`{region_iq, iraqi_place_in_bio: "البصرة", phone_964, iq_domain}`).
  - d) Types: `iraqi_place` boolean (poster-resolver) or string (news-site-resolver); `seed_list` boolean (poster-resolver, li-org-resolver) or array (news-site-resolver); `location` object (fb-page-resolver) or string (li-org-resolver).
  - e) The language labels behind `lang_share`: lang-dialect-id returns `ar`, `ckb`, `en`, `mixed`, `other`, `und` (`lang-dialect-id §3 L22`) and a separate dialect (`iraqi`, `msa`, ..., `§5.3 L67`); poster-resolver sends it the post samples (`poster-resolver §5.2 L58`) but stores `ar_iq` and `ar_msa`, names lang-dialect-id never returns. `CONVENTIONS L36` gives `sources.country_signals` and `lang_share` as jsonb with no keys.
  - Overlaps: `AU-009`.
- **At stake:** the qualifier's rule 2 and the 40% language test need fixed keys and types; with nine vocabularies (the eight resolvers' and poster-resolver's), a signal is counted for one platform and silently missed for another, and the registry's jsonb columns hold incomparable blocks.
- **Options:** (1) poster-resolver's keys and boolean types for every writer and for `sources`, with resolver-specific evidence kept in a free `evidence` object beside them; (2) `lang_share` keyed by lang-dialect-id's own labels (language shares plus a separate dialect share) and `country_signals` as a fixed boolean set with an evidence list; (3) each resolver keeps its block, and the qualifier's PRD documents a mapping per platform to its rule inputs.
- **Blocks:** F2, F3, C3, C7, C8, C9, FB1, IG1, X2, YT1, N2, VTT3, VLI2, VTG2.

### CF-015

**`registry.decisions`: writers beyond the qualifier, `decision` against `action`, and the `health_change` message**

- **Type:** writers, names, shape, partition
- **Where:**
  - a) Writers: `CONVENTIONS L20` "`registry.decisions` — the qualifier's decisions"; `registry-writer §4 L36` lists `qualifier`, `source-health-canary` (`health_change`), ops (admin page), client admins (client app) and `retention-purger` (`remove_client`); `source-health-canary §5.2 L57`, `§6.2 L99`; `retention-purger §5.3 L76` ("one `remove_client` decision per `client_sources` row"), `§6.2 L94`, with no message example. Readers: registry-writer (`registry-writer §3 L22`) and `yt-text-purger §5.1 L45`, `§6.1 L130` (`remove_client`).
  - b) The type field and the envelope: the qualifier writes `"decision":"add"` with `message_id`, `produced_at`, `service`, `schema_version`, `decision_id` (`qualifier §6.2 L84`); the canary writes `"action": "health_change"`, `actor`, `at` and no `message_id`, `produced_at`, `service` or `schema_version` (`source-health-canary §6.2 L102`); registry-writer looks up `decision_id` and applies "by decision type" (`registry-writer §5.2 L49-L51`) and stores `action` in `registry_audit` (`§5.2 L58`).
  - c) `health_change` fields: registry-writer expects `platform`, `route`, `vendor`, `health`, `fallback` (`§5.2 L54`) with "`fallback = on`" (`§13 L149`); the canary sends `"fallback": {"route": "amber", "vendor": "ensembledata"}` plus `scope`, `reason`, `evidence` (`source-health-canary §6.2 L102`) and asks for alignment (`§14 Q1 L161`); `registry-writer §14 L161` leaves open "Whether `health_change` should be carried on `registry.decisions` or on a dedicated topic".
  - d) Partition: the qualifier keys by `candidate_key` (or `source_id` for sweep decisions) (`qualifier §6.2 L81`); the canary's route-level decision carries neither (`source-health-canary §6.2 L102`); retention-purger states none.
  - The decision-type values (`reject`, `review` with no handler; `dormant`, `promote` with no producer) are section 3 (keys, jobs, values).
  - Overlaps: `AU-064` (`health_change` and the government scope).
- **At stake:** registry-writer parses the type from `decision` and cannot read the canary's `action` or its `fallback` object; without `message_id` and a key, replays and ordering of route-wide health changes against per-source decisions are undefined; the remove_client message has no written shape.
- **Options:** (1) one decision schema for every writer: a single type field, the common envelope of CF-001, `decision_id`, per-type blocks (the canary's `fallback` object, `scope`, `reason`, `evidence` included), and a stated key for route-level decisions; (2) `health_change` (and `remove_client`) move to a dedicated topic with their own schema, and `registry.decisions` stays the qualifier's; (3) one schema as in (1) but with registry-writer's fields (`fallback` as a scalar, no `scope` or `evidence`).
- **Blocks:** F2, C7, C9, C12, C14, YT7.

### CF-016

**`source.events`: registry-writer's events or anyone's, and the shape of an event a poller writes**

- **Type:** writers, shape
- **Where:**
  - a) registry-writer as the source of events: "the single writer of registry identity: one path for every change, ... and one `source.events` message per change" (`registry-writer §1 L9`), emitting `added`, `updated`, `tier_change`, `dormant`, `retired`, `fallback_on`, `fallback_off` (`§3 L24`) and owning `tier` and `health` (`§3 L27`). CONVENTIONS names no writer (`CONVENTIONS L21`).
  - b) Services that publish events themselves: `tier change` when a dormant source posts (`fb-page-feed-poller §5.2 L59`, `§6.2 L129`; `fb-group-posts-poller §5.2 L61`, `§6.2 L124`; `ig-account-media-poller §5.2 L63`, also `dormant`, `§6.2 L125`; `li-company-posts-poller §6.2 L123`; `news-feed-poller §6.2 L115`; `tg-channel-posts-poller §5.2 L66`; `tt-profile-videos-poller §5.2 L62`, `§6.2 L126`; `x-user-timeline-poller §6.2 L134`; `yt-uploads-reconciler §5.2 L65`, `§6.2 L136`); `updated` on a health or grant change (`ig-mentions-fetcher §8 L143`, `ig-webhook-receiver §5.2 L60`, `li-client-posts-poller §6.2 L126`, `li-notification-receiver §6.2 L133`, `tg-bot-channel-receiver §5.2 L72`, `tt-client-videos-fetcher §8 L130`, `x-full-archive-search §8 L148`, `x-user-timeline-poller §8 L151`); `updated` with `backfill_status` (`fb-backfill §5.2 L56`, `§6.2 L110`); `fallback_on` or `updated` with a `budget_wait` note (`ig-hashtag-search §5.1 L57`, `§6.2 L93`); an event with no type named (`tg-discussion-receiver §5.2 L69`).
  - c) Services that send the same kind of change through registry-writer instead: the first post of a dormant Page or channel "asks registry-writer to promote" it (`fb-client-webhook-receiver §5.1 L42`, `§13 L189`; `yt-pubsub-receiver §5.1 L40`, `§13 L186`), by a channel neither names; a lapsed lease makes "registry-writer set the channel's `next_poll_at` to now" (`yt-pubsub-receiver §5.1 L42`) while yt-uploads-reconciler waits for "`source.events` (`updated`, `reason = push_lease_lapsed`)" from yt-pubsub-receiver (`yt-uploads-reconciler §5.1 L51`, `§14 Q4 L201`); `news-site-resolver §5.2 L55` and `ig-account-resolver §4 L33` leave events to registry-writer.
  - d) Shape: only registry-writer gives one (`registry-writer §6.2 L95`: `message_id`, `schema_version`, `event`, the source's columns, `previous`, `decision_id`, `actor`, `at`); the direct writers give none, and name extra fields: `backfill_status` (fb-backfill), a `budget_wait` note (ig-hashtag-search), `reason` (x-full-archive-search, x-user-timeline-poller; and the `push_lease_lapsed` reason yt-uploads-reconciler expects from yt-pubsub-receiver). The spelling `tier change` against `tier_change` and the event-type list are section 3 (keys, jobs, values).
  - The `sources` columns these events describe (`tier`, `health`, `next_poll_at`) having several writers is section 2 (tables).
  - Overlaps: `AU-016`; `AU-063`; `CF-032`, `CF-033` in this file (the columns).
- **At stake:** about 46 consumers rebuild registry caches from this topic; events without `previous`, `actor` or `decision_id`, from twenty producers, cannot be audited or replayed the way registry-writer's are, and a reader waiting for an event (the lapse flag) never gets it when the change went through registry-writer by another channel.
- **Options:** (1) registry-writer is the only writer: services that see a change send a decision or request (one named channel) and registry-writer emits the event; (2) direct writes stay for operational events (`tier change` on activity, health, budget waits) in registry-writer's event schema, and the PRDs that route through registry-writer say how; (3) two topics: registry-writer's `source.events` for registry changes and a separate operational-signals topic for pollers' observations.
- **Blocks:** F2, C7, C10, C11, C6, FB2, FB3, FB7, VFB2, IG2, IG3, IG4, IG5, LI1, LI3, VLI3, N2, N3, TG1, TG2, VTG3, TT1, VTT4, X3, X5, YT2, YT3.

### CF-017

**`items.analysis`: what the four writers send against what store-writer reads, and the message key**

- **Type:** shape, names, key
- **Where:**
  - a) The key: `CONVENTIONS L22` "model outputs keyed by item and model version"; `README L184` (decision 7) "`items.analysis/v1` keyed by `item_id:task:model_version` with an `input_hash`"; the writers follow the README (`analysis-sentiment §6.2 L89` "logical key `item_id` + `task` + `model_version`"; `analysis_key` in `analysis-sentiment §6.2 L97`, `analysis-entities §6.2 L98`, `analysis-media §6.2 L95`). analysis-topics publishes "one `items.analysis` message per item per taxonomy (`task = topics:<taxonomy_id>`)" (`analysis-topics §5.2 L60`), so its key has four parts (`"analysis_key": "...:topics:global:topics-iq-2026.11.tx7"`, `§6.2 L101`).
  - b) The writers' fields: `task`, `model_version`, `result {...}`, `produced_at`, `item_fetched_at` (for example `analysis-sentiment §6.2 L93-L105`; `analysis-topics §6.2 L105`).
  - c) The reader: store-writer's `analysis` table is keyed `item_id, model`, versioned by `analyzed_at`, "a newer model version replaces the older" (`store-writer §5.3 L61`), and "`analysis` carries `model`, `model_version`, the `output` JSON and typed projections ... (names as in `items.analysis/v1` ...)" (`§5.3 L67`). No writer sends `model`, `output` or `analyzed_at`.
  - d) The topic identifier the aggregates group by: analysis-topics publishes `result.topics[]` entries with `"node_id": "outage"` (`analysis-topics §6.2 L111`); aggregator's grain column is `topic_id`, which "comes from analysis-topics", with `unassigned` for none yet (`aggregator §5.3 L55`) and values like `"topic_id": "tp_0042"` (`§6.2 L87`). (The id formats themselves are section 3 (keys, jobs, values).)
  - The fetch-time and fetching-service fields of these messages are in CF-002; the ClickHouse table's partitioning by `analyzed_at` is section 2 (tables).
  - Overlaps: `CF-075` in this file; `CF-050` in this file (the ClickHouse table).
- **At stake:** store-writer has no `model` or `output` to write and no `analyzed_at` to version by; keyed by `item_id, model`, rows for two tasks of one model (`sentiment` and `sentiment_aspect`) or two taxonomies collapse into one, and the README's three-part key does not fit analysis-topics' four-part one; the aggregates cannot group by a `topic_id` that the message calls `node_id` and spells as a slug.
- **Options:** (1) the README's key `item_id:task:model_version` with `task` free to carry a taxonomy (`topics:<taxonomy_id>`), and store-writer's table and field names follow the message (`task`, `model_version`, `result`, `produced_at`); (2) store-writer's names become the message schema (`model`, `output`, `analyzed_at`), with `task` added to its key; (3) one message per item per task, taxonomies inside `result`, and store-writer keyed `item_id, task`, the newest `model_version` replacing the older.
- **Blocks:** F2, F8, C6, C15, A1, A2, A3, A4.

### CF-018

**`item.metrics` writers: normalize-item and the metrics services both observe the same fetch, and LinkedIn counts have no named producer**

- **Type:** writers
- **Where:**
  - a) Who writes: `CONVENTIONS L65` "refreshed at +24 h and +7 d by the source's metrics or details service, or by the next poll where the API returns counts with the post"; normalize-item publishes "one `item.metrics` observation per record that carries counts" (`normalize-item §5.2 L56`), so "The same post fed three times (poller, keyword search, backfill) produces ... three `item.metrics` observations" (`§13 L167`); fb-reactions-fetcher's extract mode emits one observation "for every Facebook post on the green route" it consumes from `raw.items` (`fb-reactions-fetcher §5.1 L39`), besides its +24 h and +7 d refreshes (`§5.1 L41`); yt-video-details-fetcher writes "a `first_sight` observation to `item.metrics` from the same response" as its full `raw.items` record (`yt-video-details-fetcher §3 L19`, `§6.2 L131`); tt-client-videos-fetcher (`tt-client-videos-fetcher §6.2 L115`; `README L185`, decision 8) and tt-video-stats-refresher (`tt-video-stats-refresher §6.2 L85`) write their own.
  - b) One fetch, two observations: a Facebook poll reaches `item.metrics` from normalize-item and from fb-reactions-fetcher, and a YouTube first-sight read from normalize-item and from yt-video-details-fetcher, each with its own label vocabulary (CF-019). fb-reactions-fetcher says "the store keeps both, keyed on (`item_id`, `observed_at`)" (`fb-reactions-fetcher §5.1 L43`), store-writer keys `metrics_timeseries` the same way (`store-writer §5.3 L62`), but fb-reactions-fetcher's message carries `item_idempotency_key` and no `item_id` (`fb-reactions-fetcher §6.2 L107`).
  - c) An expected producer that names nothing: li-notification-receiver reads `item.metrics` "(comment counts, for the silence check)" (`li-notification-receiver §6.1 L108`) for counts "observed by li-client-posts-poller" (`§5.1 L42`), and li-own-comments-fetcher expects comment-decay-scheduler to compare "the latest comment count for the post (from li-client-posts-poller, through `item.metrics`)" (`li-own-comments-fetcher §5.1 L48`), which comment-decay-scheduler does not read (`comment-decay-scheduler §6.1 L135`); li-client-posts-poller never names `item.metrics` (`li-client-posts-poller §6.2 L103-L126`; counts ride in its payload, `"metrics_observation": "poll"`, `li-client-posts-poller §6.2 L120`), and normalize-item's LinkedIn mapper line names no count fields (`normalize-item §5.3 L69`).
  - Overlaps: `CF-081`, `CF-082` in this file (metrics jobs and refreshes); `AU-004`.
- **At stake:** `metrics_timeseries` gets two rows for one fetch whenever the two writers' `observed_at` differ, and growth curves double-count; the LinkedIn silence check and comment reconciliation depend on observations no PRD commits to produce.
- **Options:** (1) normalize-item is the only writer of observations taken from fetched records, and the metrics services write only their scheduled refreshes (fb-reactions-fetcher drops its extract mode); (2) the metrics and details services are the only writers on their platforms, and normalize-item emits observations only for platforms listed as having no such service; (3) both write, every observation names its producer and label, and store-writer keeps one row per item, time and label.
- **Blocks:** F2, C4, C6, C11, FB4, YT4, TT1, VTT6, LI1, LI2, LI3.

### CF-019

**`item.metrics` message: flat with a `metrics` object, or an envelope with an `observation` object; `observation` a string or an object; no `item_id`**

- **Type:** shape, names, types
- **Where:**
  - a) Flat: `fb-reactions-fetcher §6.2 L104-L123` (`item_idempotency_key`, `platform_id`, `source_id`, `service`, `route`, `vendor`, `"observation": "refresh_24h"`, `observed_at`, `post_created_time`, `age_seconds`, `metrics {like, love, haha, wow, sad, angry, care, reactions_total, comments, shares}`, `job_id`, `retention_class`) and `yt-video-details-fetcher §6.2 L133-L152` (the same plus `channel_id`, `live_state`, `call_id`; `metrics {views, likes, comments}`).
  - b) Envelope plus observation: `tt-video-stats-refresher §6.2 L87-L109` (`envelope {..., idempotency_key: "tiktok:metrics:<id>:plus_24h", item_key, fetched_at, retention_class, client_ids}`, `observation {label: "plus_24h", first_seen_at, due_at, observed_at, lateness_seconds, views, likes, shares, comments, regressed, baseline_missing}`); tt-client-videos-fetcher describes its own only in prose: "label `plus_24h` or `plus_7d`, the four counts, `observed_at`, `first_seen_at`, `lateness_seconds`, same envelope fields" (`tt-client-videos-fetcher §6.2 L115`). normalize-item gives no shape for its observations (`normalize-item §5.2 L56`).
  - c) The same thing under several names or types: `observation` a string label (fb, yt) or an object holding the counts (tt-video-stats-refresher), with the label then in `observation.label`; the item reference `item_idempotency_key` (fb, yt) or `item_key` (tt), never `item_id`; counts inside `metrics` (fb, yt) or inside `observation` (tt), per reaction type (`like`, `love`, ...) or as `likes`. `tt-video-stats-refresher §14 Q4 L176` proposes adding `saves` "as a nullable field" once the schema allows (kept out in v1, `§5.4 L75`).
  - d) The reader: store-writer keys `metrics_timeseries` on `item_id, observed_at` (`store-writer §5.3 L62`), stores "likes, comments, shares, views and reactions by type per observation" (`§5.3 L67`), takes `retention_class` "from the message, else from the item row" (`§5.3 L82`), and asks "Does `item.metrics` carry `retention_class`, `created_at` and `source_id`?" (`§14 Q5 L185`).
  - The label values (`refresh_24h`, `plus_24h`, `poll`, `first_sight`, ...) are section 3 (keys, jobs, values) (CF-081; `AU-031`, and `AU-084` for `webhook_reconcile`).
  - Overlaps: `CF-081` in this file (label vocabulary).
- **At stake:** store-writer cannot key a row without `item_id` (or a rule to derive it from `item_idempotency_key` or `item_key`) and must parse two layouts and three count vocabularies into one table; a typed contract cannot give `observation` two JSON types.
- **Options:** (1) the flat layout of fb-reactions-fetcher with `item_id` added, one `label` field and one `counts` object with fixed names (`likes`, `comments`, `shares`, `views`, `reactions_by_type`); (2) the TikTok layout (envelope plus `observation` object) for every writer, with `item_id` in the envelope; (3) only normalize-item writes `item.metrics` (CF-018 option 1 extended), and the fetchers put counts on `raw.items`, so the shape is normalize-item's alone.
- **Blocks:** F2, F8, C4, C6, FB4, YT4, TT1, VTT6.

### CF-020

**`deletions` message: deletion-propagator's required fields against a short form keyed by `idempotency_key` and a long form with top-level `source_id`**

- **Type:** shape, names
- **Where:**
  - a) The consumer's contract: "Required for any producer: `reason`, `scope`, a target (`platform`, `kind` and `platform_id` or `item_ids`, or `author_hash`, `source_id` or `client_id`). Optional: `deletion_id` ..., `mode` ..., `retention_class`, `signal_at` ..., `due_at` ..., `requested_by`, `run_id`" (`deletion-propagator §5.4 L80`); "The producers of `platform_sync` deletions (fb-reactions-fetcher and the comment fetchers) must emit the minimum shape of 5.4" (`§14 Q2 L172`).
  - b) Long form, with `source_id` and `client_id` at the top rather than as target alternatives, and `emitted_at` added: `retention-purger §6.2 L96-L107`; `x-compliance-sync §6.2 L99-L110` adds `platform_status`, `countries`, `x_job_id`, `event_at` and `target.platform_ids`; `yt-text-purger §6.2 L142-L156` adds `target.video_id`, `target.fetched_before` and `parent_run_id`.
  - c) Short form, with no `scope` or `target`, an `idempotency_key` instead, and `detected_at` instead of `signal_at`: `fb-post-comments-fetcher §6.2 L125` (`platform`, `kind`, `idempotency_key`, `parent_platform_id`, `reason`, `service`, `job_id`, `detected_at`); `fb-group-comments-fetcher §6.2 L128` (the same without `parent_platform_id`); `yt-comments-fetcher §6.2 L136` (`idempotency_key`, `parent_video_id`, `job_id`, `detected_at`); `yt-replies-fetcher §6.2 L125` (plus `parent_comment_id`).
  - d) Fields named only in passing: "item key" (`tt-video-stats-refresher §6.2 L112`); "both `call_id`s" (`yt-video-details-fetcher §6.2 L155`); no fields at all for the other `platform_sync` producers (for example `ig-own-comments-fetcher`, `li-post-comments-fetcher`, `news-comments-fetcher`, `tt-video-comments-fetcher`).
  - e) A reader that needs more: alert-evaluator asks that deletions "carry `item_id`" (`alert-evaluator §14 Q3 L165`), which the short form never has and the long form has only as `target.item_ids`.
  - The author-scope key is in CF-003; the `withhold` mode and the deletion reasons are section 3 (keys, jobs, values).
  - Overlaps: `AU-013` (`item_id` on deletions); `CF-076` in this file (reasons, scopes, modes).
- **At stake:** deletion-propagator rejects or cannot target a short-form message (no `scope`, no `target`); a typed contract cannot carry `source_id` both at the top and inside `target`; alert-evaluator cannot map a deletion to an alert without an item id.
- **Options:** (1) deletion-propagator's 5.4 is the schema for every producer: fetchers add `scope: item` and a `target` (`platform`, `kind`, `platform_id`), and the long-form extras become named optional fields; (2) two message types on the topic, a `platform_sync` short form (key plus `detected_at`, accepted and resolved by deletion-propagator) and the administrative long form; (3) the long form of retention-purger (top-level `source_id`, `client_id`, `emitted_at`) for every producer, and deletion-propagator's 5.4 rewritten to match.
- **Blocks:** F2, C13, C14, C15, A5, X7, YT7, FB4, FB5, FB7, VFB3, IG6, LI1, LI2, LI3, VLI4, N8, VTT5, VTT6, YT2, YT4, YT5, YT6.

### CF-021

**Who acts on a `deletions` message: deletion-propagator alone, or every holder of a copy, and how the others learn a deletion is done**

- **Type:** writers, rule
- **Where:**
  - a) deletion-propagator is "A continuous consumer of `deletions`" (`deletion-propagator §5.1 L43`) that publishes no message when a deletion completes: it writes ClickHouse, archives, `jobs.aggregator` recompute jobs and the Postgres `deletion_requests` status (`§6.2 L90`), and for aggregates it sends `recompute` jobs "and wait[s] for `done`" (`§5.3 L70`). The places it clears are ClickHouse, the raw and Parquet archives, media, the text index and caches (`§1 L7`, `§6.1 L86`); the analysis services' annotation stores are not among them.
  - b) aggregator also consumes the topic itself: "a message on `deletions` (consumer group `aggregator`) triggers a reconciliation within 5 minutes" (`aggregator §5.1 L37`), names its source as "`deletions` (deletion-propagator)" (`§11 L128`), and expects that "After deletion-propagator removes an item, the hour's mentions drop by one within 5 minutes of the `deletions` message" (`§13 L145`), although nothing ties its reconciliation to the removal being done.
  - c) alert-evaluator lists "deletion-propagator (`deletions`)" as a dependency (`alert-evaluator §11 L134`) and asks that "deletion-propagator must name the deletion reasons and carry `item_id`; if it deletes before the evaluator reads the message, the watch set covers it" (`§14 Q3 L165`); deletion-propagator writes no such message.
  - d) The analysis services' acceptance tests need the topic, but their inputs omit it: "A `deletions` message removes the item's text from the annotation store" (`analysis-sentiment §13 L164`, `analysis-topics §13 L171`, `analysis-entities §13 L169`; OCR text, transcript and media in `analysis-media §13 L162`), while their topic lists have no `deletions` (`analysis-sentiment §6.1 L85`, `analysis-topics §6.1 L89`, `analysis-entities §6.1 L86`, `analysis-media §6.1 L83`).
  - Overlaps: `AU-077` and `AU-082`; `CF-049` in this file.
- **At stake:** aggregator can recompute an hour before the item is gone and again when deletion-propagator's job arrives; alert-evaluator waits for a message from a service that sends none; annotation stores and media keep deleted text unless someone is defined to clear them.
- **Options:** (1) only deletion-propagator consumes `deletions`: it clears every store (annotation stores and media included, through their owners) and publishes a completion event that aggregator and alert-evaluator act on; (2) every service that holds a copy consumes `deletions` itself and reports done to deletion-propagator, which verifies; (3) caches and annotation stores consume `deletions` directly, while aggregates change only through deletion-propagator's recompute jobs (aggregator stops consuming the topic).
- **Blocks:** F2, C13, C15, A1, A2, A3, A4, A5.

### CF-022

**`article.urls`: the news pollers' envelope against search-hit-router's flat `article.urls/v1`, and a writer CONVENTIONS does not list**

- **Type:** shape, names, writers
- **Where:**
  - a) The three news pollers: `{"envelope": {platform, "kind": "article_url", route, vendor, service, source_id, url_key, job_id, attempt, found_at, found_via, retention_class, access_mode}, "payload": {url, ...}}` with no schema name, no `fetched_at` and no `idempotency_key` (`news-feed-poller §6.2 L94-L112`, `news-sitemap-poller §6.2 L106-L124`, `news-homepage-differ §6.2 L99-L115`); the payloads differ, and news-homepage-differ's has no `title` (`L111-L113`).
  - b) search-hit-router: flat `"schema": "article.urls/v1"`, `message_id`, `idempotency_key`, `service`, `found_by`, `source_id`, `url`, `canonical_url`, `canonical_url_hash`, `engines`, `keyword_rule_ids`, `client_ids`, `title`, `snippet`, `published_hint`, `first_seen_at`, with no `route`, `vendor`, `retention_class`, `found_via` or `found_at` (`search-hit-router §6.2 L119-L131`).
  - c) One thing, two names: `url_key` / `idempotency_key`; `found_via` / `found_by`; `found_at` / `first_seen_at`.
  - d) The reader orders work by `found_via` and discovery time: "live URLs (`found_via` feed, news_sitemap, homepage_diff) are fetched before backfill URLs (`sitemap_backfill`, `commoncrawl`), and older discoveries before newer ones" (`news-article-extractor §5.1 L43`; `extraction_lag_seconds` is "now minus `found_at`"); search-hit-router's messages carry neither field. (`commoncrawl` URLs have no producer: web-commoncrawl-scanner writes only `discovery.hits`; that backfill path is entry `AU-044` in `CONFLICTS-ASSUMPTIONS.md`.)
  - e) Writers: `CONVENTIONS L281` "Services that find sources rather than items (fb-page-search, web-commoncrawl-scanner, search-hit-router) write `discovery.hits` only"; search-hit-router also writes `article.urls` (`search-hit-router §3 L26`, `§6.2 L117`).
  - The key formats (`news:url:<hex>`, `news:article:<hex>` and `news:article:sha256:<hex>`) are CF-118; the missing `fetched_at` is also in CF-002.
  - Overlaps: `AU-103` and `AU-044` (news backfill through web-commoncrawl-scanner).
- **At stake:** news-article-extractor cannot schedule or deduplicate search-hit-router's URLs with the fields it reads, and one typed contract cannot read both layouts; CONVENTIONS and the router disagree on whether the router may write the topic at all.
- **Options:** (1) the news pollers' envelope for every producer, search-hit-router mapping `found_by` to `found_via` (for example `web_search`) and adding `url_key`, `found_at`, `retention_class`; (2) search-hit-router's flat `article.urls/v1` for every producer, with the pollers' `found_via`, `access_mode` and payload fields added as optional; (3) search-hit-router stops writing `article.urls` and hands news URLs to the news finders (as CONVENTIONS L281 reads), so only the envelope remains.
- **Blocks:** F2, N3, N4, N5, N6, W3.

### CF-023

**`search.results`: yt-web-search-bridge's message against `search.results/v1`, and whether search-hit-router routes the bridge's results or skips them**

- **Type:** shape, names, types, writers
- **Where:**
  - a) The three engines write `"schema": "search.results/v1"`, `message_id`, `produced_at`, `service`, `engine`, `route`, `vendor`, `job_id`, `job_kind`, `attempt`, `keyword_rule_id`, `keyword_id`, `client_ids`, `query {text, variant, lang, country, request_id}`, `result {rank, title, url, snippet, date, last_updated}`, `canonical_url`, `canonical_url_hash`, `fetched_at`, `raw_ref`, `retention_class` (`web-search-perplexity §6.2 L92-L108`; "same shape" `web-search-mojeek §6.2 L89`; plus optional `hints` `web-gdelt-poller §6.2 L92`).
  - b) yt-web-search-bridge writes `idempotency_key` (`web:result:mojeek:<hash>`), `platform`, `platform_hint`, `engine`, `route`, `vendor`, `service`, `handled_by`, `source_id`, `query` as a string, `job_id`, `fetched_at`, `cost {currency, amount}`, `extracted {kind, video_id}`, `payload {title, url, desc}`, and no `schema`, `message_id`, `result`, `canonical_url_hash` or `retention_class` (`yt-web-search-bridge §6.2 L106-L124`). `query` is an object for the engines and a string for the bridge.
  - c) The reader: search-hit-router consumes "`search.results` from the four producers", the bridge among them (`search-hit-router §1 L7`, `§3 L23`), parks any message without `schema = search.results/v1` and its required keys as `schema_unknown` (`§5.2 L55`), deduplicates on `message_id` (`§5.2 L56`), checks `canonical_url_hash` (`§5.2 L57`), and routes YouTube URLs itself (`§5.3 L79`); it never mentions `handled_by`. The bridge says the opposite: "results marked `handled_by = yt-web-search-bridge` are skipped by it" (`yt-web-search-bridge §4 L37`), and its `§13 L182` tests that the router skips them.
  - d) `query.lang` means different things: a language filter for Perplexity (`search_language_filter`, `web-search-perplexity §5.3 L67`; example `"lang": "ar"`, `§6.2 L100`), the language boost `lb` for Mojeek (`web-search-mojeek §6.2 L109`), sent as `lb=AR` (`web-search-mojeek §5.3 L67`) and recorded as `"lang": "ar"` in the example (`web-search-mojeek §6.2 L99`), and null for GDELT (`web-gdelt-poller §6.2 L102`).
  - Whether web results also enter `raw.items` as items is CF-110; the `site_search` jobs the engines describe are section 3 (keys, jobs, values).
  - Overlaps: `AU-011`; `AU-108` (`site_search`).
- **At stake:** every bridge message is parked by the router as `schema_unknown`, or, if the router accepted it, routed a second time against the bridge's own first-sight jobs; a typed `search.results` contract cannot give `query` two types.
- **Options:** (1) the bridge writes `search.results/v1` and adds `handled_by` and `extracted` as optional fields, and the router skips `handled_by` messages after counting them; (2) the bridge stops writing `search.results`, and the router's producer list drops to three; (3) the bridge writes `search.results/v1` without `handled_by`, and the router does all YouTube routing while the bridge stops emitting jobs.
- **Blocks:** F2, W1, W2, W3, W4, YT9.

### CF-024

**`jobs.completed` (not in CONVENTIONS): who writes it, the schema version, the report fields, and producers that report elsewhere**

- **Type:** writers, shape, names, document
- **Where:**
  - a) The proposal: `README L178` (decision 1) "Completion topic `jobs.completed` (schema `jobs.completed/v1`), written by the listening-sdk job wrapper after every job with a report (`new_count`, `seen_count`, `pages`, `cost_units`, `reply_candidates`)"; `comment-decay-scheduler §14 Q1 L202` proposes it "partitioned by `source_id`; alternative: poll `service_runs`". CONVENTIONS lists no such topic (`CONVENTIONS L14-L29`) and only says a fetch "reports `new_count`, `seen_count`, `pages`, `cost_units`" (`CONVENTIONS L62`).
  - b) Who writes it: the SDK wrapper (`x-replies-fetcher §5.1 L41`, `x-user-timeline-poller §5.2 L61`, `yt-comments-fetcher §5.1 L40`, `§5.2 L60`, `yt-replies-fetcher §5.2 L57`), or the service itself (`yt-uploads-reconciler §5.2 L66` "Publish to `jobs.completed`", `yt-video-details-fetcher §5.2 L63` "write one completion per job to `jobs.completed`", `x-full-archive-search §6.2 L128` with "`post_ref`, `series_step` and the window's `end_time`").
  - c) Report fields under one schema name: comment-decay-scheduler's example has `report {new_count, seen_count, pages, cost_units, reply_candidates}` and `series_step` (`comment-decay-scheduler §5.4 L127`); backfill-orchestrator's has `report {new_count, pages, cost_units, oldest_item_at, capped, capped_reason}` and no `seen_count` (`backfill-orchestrator §5.4 L92`); writers add `paid_user_reads`, `capped`, `window_partial` (`x-replies-fetcher §5.2 L62`), `stored_count`, `complete` (`yt-replies-fetcher §5.2 L57`), `end_time` (`x-full-archive-search §6.2 L128`). The counts mean different things: `seen_count` = "posts with `paid = false`" (`x-user-timeline-poller §5.2 L61`) or "with edits included" (`x-replies-fetcher §5.2 L62`).
  - d) Producers that report the same thing elsewhere or under another name: to comment-decay-scheduler with `stored_before`, `complete`, `reply_threads` (`fb-group-comments-fetcher §5.2 L66`; `fb-post-comments-fetcher §5.2 L70`, whose `§14 Q6 L192` asks whether it is "a job-result record"); "through the control-plane client" with "incomplete reply threads" (`ig-own-comments-fetcher §5.2 L64`); "the job result" (`ig-comments-fetcher §5.2 L63`); with `newest_comment_at` or "the new marker" (`li-own-comments-fetcher §5.2 L64`, `li-post-comments-fetcher §5.2 L66`); "the completion message" (`tt-video-comments-fetcher §5.2 L62`, `tt-video-stats-refresher §5.2 L59`); a result row in `service_runs` (`news-comments-fetcher §5.2 L59`); "a backfill report to backfill-orchestrator (`coverage_days`, `urls_emitted`)" (`news-sitemap-poller §6.2 L127`); `items_fetched`, `items_new` (`ig-hashtag-search §5.2 L70`).
  - e) Readers: comment-decay-scheduler (`comment-decay-scheduler §5.1 L42`), backfill-orchestrator (`backfill-orchestrator §5.2 L59`, `backfill-orchestrator §6.1 L100`), x-filtered-stream ("The gap closes when `jobs.completed` arrives for all its jobs", `x-filtered-stream §5.2 L71`), x-full-archive-search ("x-recent-search's `jobs.completed` reports", `x-full-archive-search §6.1 L102`, used for "the rule's daily `new_count`", `§5.2 L52`), while x-recent-search names no such output (`x-recent-search §6.2 L98`).
  - Overlaps: `CF-089` in this file; `AU-001` (completion events, including status values); `AU-017` (backfill completion report).
- **At stake:** comment-decay-scheduler and backfill-orchestrator advance only on this topic, so any fetcher that reports by another channel never advances its series or backfill, and a typed `jobs.completed/v1` cannot hold two different `report` blocks; x-filtered-stream and x-full-archive-search depend on reports x-recent-search does not promise.
- **Options:** (1) `jobs.completed/v1` added to CONVENTIONS, written only by the SDK wrapper after every job, with a fixed required report (`new_count`, `seen_count`, `pages`, `cost_units`) and named optional fields (`reply_candidates`, `capped`, `oldest_item_at`, `end_time`, ...); (2) as (1), but services may also publish to it directly for completions the wrapper does not see; (3) no topic: results go to `service_runs` result rows that the schedulers poll (comment-decay-scheduler's alternative).
- **Blocks:** F2, F4, F6, C10, C11, X1, X3, X4, X5, X6, YT3, YT4, YT5, YT6, FB3, FB5, VFB3, IG6, VIG2, LI2, VLI4, VTT5, VTT6, N4, N8, IG2.

### CF-025

**`news.dedup` (not in CONVENTIONS): a topic whose only named reader does not read it, and story fields `items.normalized` does not have**

- **Type:** writers, shape, document
- **Where:**
  - a) The writer: `news-dedup §6.2 L84` "`news.dedup` (partitioned by `story_id`), one message per verdict and per `story_update`"; schema `news.dedup/v1` with `type`, `idempotency_key`, `story_id`, `is_origin`, `duplicate_of`, `origin_source_id`, `origin_time`, `cluster_size`, `rank_in_cluster`, `matched_by`, `source_id`, `dedup_version`, `decided_at`, `service` (`§6.2 L86-L101`). `README L183` (decision 6) proposes "a new topic `news.dedup` from news-dedup to normalize-item"; CONVENTIONS' topic list has no such topic (`CONVENTIONS L14-L29`).
  - b) The expected reader: "normalize-item copies `story_id`, `is_origin` and `duplicate_of` onto the normalized item and re-emits the story fields as a new version when an update arrives" (`news-dedup §6.2 L104`); `§14 Q1 L167`: "with a bounded wait in normalize-item; if normalize-item prefers a table-only join, the topic is dropped".
  - c) normalize-item's inputs are "`raw.items` (live), `jobs.normalize-item` (`replay`, `lang_rescore`), `source.events`" (`normalize-item §6.1 L86`), and its `items.normalized/v1` example has no `story_id`, `is_origin` or `duplicate_of` (`§6.2 L93-L120`); no other PRD reads the topic.
  - Overlaps entry `AU-003`.
- **At stake:** the topic would be produced with no consumer, and the story fields that downstream readers would group news by never reach `items.normalized` or ClickHouse.
- **Options:** (1) `news.dedup` joins the CONVENTIONS topic list, normalize-item consumes it with a bounded wait, and `items.normalized/v1` gains `story_id`, `is_origin`, `duplicate_of`; (2) no topic: normalize-item (or store-writer) joins `news_story_members` when it maps an article, and the story fields are added as in (1); (3) no topic and no item fields: stories stay in news-dedup's tables and readers join them there.
- **Blocks:** F2, C4, C6, N7, N6.

### CF-026

**`raw.replay` (not in CONVENTIONS): a replay topic with no consumer, while normalize-item replays from object storage**

- **Type:** writers, document
- **Where:**
  - a) The writer: raw-archiver owns "The replay API and the replay topic `raw.replay`" (`raw-archiver §3 L22`); `POST /v1/replays` takes a `target` (`normalize-item`, `analysis` or `all`) and "publishes each record to `raw.replay` with the original envelope plus a `replay` block" (`§5.3 L71`); the topic is "partitioned by `source_id`, one message per record" (`§6.2 L96`). `§14 Q2 L182`: "normalize-item reads `raw/` directly on a `replay` job. Proposed: `raw.replay` is the main path, with a manifest-only mode for direct readers".
  - b) The named target replays another way: normalize-item's replay worker "reads `raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst` from object storage (never Redpanda, whose retention is days)" on a `kind = replay` job (`normalize-item §5.1 L45`), and lists no `raw.replay` among its inputs (`§6.1 L86`); keyword-matcher and store-writer only say "raw-archiver's replay path (the one normalize-item uses)" (`keyword-matcher §5.1 L42`, `store-writer §5.1 L41`). No PRD consumes `raw.replay`; the only other mention is deletion-propagator's tombstones, which guard against "a `raw.replay` of the same" item (`deletion-propagator §5.3 L62`). CONVENTIONS' topic list has no replay topic (`CONVENTIONS L14-L29`).
  - Overlaps entry `AU-072`; the replay jobs are section 3 (keys, jobs, values).
- **At stake:** a replay ordered through raw-archiver's API reaches nobody, and a replay started on `jobs.normalize-item` bypasses raw-archiver's deletion check (`deletion_requests`, `raw-archiver §5.3 L71`) and class clocks; two replay paths cannot share one rate cap or progress record.
- **Options:** (1) `raw.replay` joins the CONVENTIONS topic list as the one replay path, and normalize-item (and the analysis services, for `target = analysis`) consume it; (2) no topic: replay stays a `jobs.normalize-item` job reading `raw/` objects, and raw-archiver offers a manifest and a deletion filter to the reader; (3) both, with the topic as the main path and direct reads limited to a manifest-only mode, as raw-archiver's `§14 Q2` proposes.
- **Blocks:** F2, C2, C4, C5, C6, C13, A1, A2, A3, A4.

### CF-027

**Message fields one PRD names two ways (prose against its own example or lists)**

- **Type:** names, document
- **Where:**
  - a) keyword-matcher: the set hash is `set_version` in prose (`keyword-matcher §5.3 L58`, and `message_id = kh:<hit_id>:<item_version>:<set_version>`, `§5.3 L77`) and `keyword_set_version` in the example, where it reads `"cs:3f9a1c"` while the `message_id` embeds `cs3f9a1c` (`§6.2 L100`, `L107`).
  - b) news-robots-checker on `crawl.policies`: `robots_status = unavailable` (`news-robots-checker §5.3 L71`) against `robots.status = unavailable` (`§13 L168`; nested `robots.status` in the example, `§6.2 L102`); the Content-Signal directive values `ai-input` and `ai-train` (`§5.3 L73`) become the fields `ai_input` and `ai_train` (`§6.2 L107`), a mapping no line states.
  - c) The web engines set `normalize = skip` on their `raw.items` records (`web-search-perplexity §5.2 L55`, `web-search-mojeek §5.2 L57`, `web-gdelt-poller §5.2 L57`), but their own envelope lists have no `normalize` field (`web-search-perplexity §6.2 L89`, `web-search-mojeek §6.2 L88`, `web-gdelt-poller §6.2 L91`).
  - d) normalize-item names `items.normalized` fields its v1 example lacks: `lang_pending` (`normalize-item §8 L133`, `§13 L172`), `text_full_ref` (`§5.3 L72`, `§13 L166`), `author_followers` (`§5.4 L79`); example `§6.2 L93-L120`.
  - e) fb-backfill's envelope is "identical to fb-page-feed-poller's except `service` and `metrics_observation`" (`fb-backfill §6.2 L88`), yet its example and acceptance test add a `window` object (`§6.2 L104`, `§13 L165`).
  - f) tg-bot-channel-receiver writes "one message per post or edit, the `channel_post` object unchanged" (`tg-bot-channel-receiver §6.2 L113`), while edits arrive as `edited_channel_post` (`§5.2 L59`, `§13 L184`).
  - g) raw-archiver's `raw.replay` example envelope (`raw-archiver §6.2 L98-L115`) lacks `job_id`, `client_ids` and `batch`, which `§5.4 L86` lists as envelope fields, though replay carries "the original envelope" (`§5.3 L71`).
  - h) news-article-extractor promises "extraction code versioned in the payload" (`news-article-extractor §12 L167`); its payload shows only `"extractor": "trafilatura"` (`§6.2 L120`).
  - i) Prose against the PRD's own reads list: web-commoncrawl-scanner computes `accept_rate` "from `source.events`" (`web-commoncrawl-scanner §10 L136`), but its reads omit `source.events` (`§6.1 L80`).
- **At stake:** each owning session would type its message from whichever line it reads first, and a consumer built from the other line breaks; the contracts package needs one spelling per field.
- **Options:** (1) the 6.2 example wins in every case and the prose is corrected; (2) the prose wins and the examples are corrected; (3) decide case by case in the owning session's plan, recorded in its handoff.
- **Blocks:** F2, C5, N1, W1, W2, W4, C4, FB3, TG1, C2, N6, W5.

### CF-028

**News article record on `raw.items`: normalize-item maps a `date` field the extractor writes as `published_at`**

- **Type:** names
- **Where:**
  - a) The reader: normalize-item's mapper for "trafilatura article (news-article-extractor)" takes "`title`, an excerpt of 200 to 300 characters as `text`, `text_full_ref` to the 7-day cache, `date`, `canonical_url`" (`normalize-item §5.3 L72`).
  - b) The writer: news-article-extractor's record is its own extraction (not a platform payload) and carries `"published_at": "2026-10-06T05:41:00Z"` and no `date` (`news-article-extractor §6.2 L114`), although it reads trafilatura's `date` field (`news-article-extractor §5.3 L69`); the other reader, news-dedup, also reads `published_at` (`news-dedup §5.2 L51`, `L53`).
- **At stake:** with the mapper as written, every article misses its publication time (or fails the mapper's required fields and is parked, `normalize-item §5.2 L50`), so `created_at` on news items falls back or the batch never publishes.
- **Options:** (1) `published_at`, as the extractor and news-dedup use; (2) `date`, as normalize-item's mapper reads, with the extractor and news-dedup renamed; (3) the extractor writes both during a transition, the mapper reading `published_at` first.
- **Blocks:** F2, C4, N6, N7.

### CF-029

**`crawl.policies`: news-robots-checker counts on registry-writer acting on the topic, which registry-writer does not read**

- **Type:** writers
- **Where:**
  - a) The writer: news-robots-checker produces `crawl.policies` "on first check or any change" and says "on `crawl_allowed` flipping, registry-writer updates `sources.health`" (`news-robots-checker §5.2 L61`); "registry-writer maps `crawl_allowed = false` onto `sources.health = blocked`" (`§6.2 L117`).
  - b) registry-writer reads one topic, "`registry.decisions`" (`registry-writer §6.1 L86`), applies only decision messages from the qualifier, ops, clients and the canary (`§2 L15`), and never mentions `crawl.policies` or `crawl_allowed`. The named readers of the topic are the news services (`news-article-extractor §6.1 L85` and the other news pollers).
  - Overlaps: `AU-021` and `CF-032` in this file (who writes `sources.health`).
- **At stake:** a site whose robots policy disallows crawling keeps `health = ok`, so every service that selects sources by health keeps scheduling it unless each news service checks `crawl_allowed` itself.
- **Options:** (1) registry-writer also consumes `crawl.policies` and maps `crawl_allowed` to `health`; (2) news-robots-checker turns a flip into a `health_change` decision on `registry.decisions`; (3) `sources.health` is not used for crawl permission, and every news service reads `crawl_allowed` from `crawl.policies` or `crawl_policies` before fetching.
- **Blocks:** F2, C7, N1, N2, N3, N4, N5, N6.


## 2. Tables, columns and storage

### CF-030

**Who writes `sources.backfill_status` (and `next_poll_at` at hand-over): one writer in three documents, eight writers in the PRDs**

- **Type:** writers, enum
- **Where:**
  - a) Single writer claimed: `backfill-orchestrator §1 L9` "the only writer of `backfill_status`"; `§5.2 L57` sets `running`; `§5.1 L46` sets `done` or `capped` "and `next_poll_at = now()` in one transaction"; `README L181` (decision 4) "backfill-orchestrator is the single writer of `backfill_status`; fb-backfill's PRD also writes it with identical values, to be aligned"; `registry-writer §3 L30` gives `backfill_status` to `backfill-orchestrator` and `next_poll_at` to "the pollers".
  - b) Executing services that write it themselves: `fb-backfill §5.2 L51` "set `backfill_status = running`", `L56` "set `backfill_status = done`, or `capped`", `§6.2 L110` "`sources.backfill_status`, `next_poll_at`", `§8 L126` `capped` after the DLQ; `fb-page-feed-poller §5.1 L48` "fb-backfill ... sets `done` or `capped` and `next_poll_at = now()`"; `tg-channel-posts-poller §5.1 L54` "the service sets `done` or `capped` and `next_poll_at = now()`"; `x-user-timeline-poller §5.1 L48` "x-full-archive-search, which seeds this service's cursor and sets `done` or `capped` and `next_poll_at = now()`", against `x-full-archive-search §5.1 L41` "backfill-orchestrator sets `done` or `capped`"; `fb-group-posts-poller §6.3 L128` and `fb-keyword-search §6.3 L124` list `backfill_status` as their own state.
  - c) Services that run their own backfill and move the column: `tt-hashtag-feed-poller §5.1 L48` "`backfill_status` moves pending → running → done or capped", `§6.2 L79`; `tt-keyword-search §5.1 L44`, `§6.3 L105`.
  - d) Insert value: `registry-writer §5.2 L52` and the SQL at `§5.3 L68-L69` insert `'pending'` and `next_poll_at = now()`, although its own `§3 L30` assigns both columns to other owners; `news-site-resolver §6.2 L112` repeats "registry-writer maps ... `backfill_status = pending`"; `li-org-resolver §5.1 L46` "registry-writer sets `next_poll_at` on admission and the pollers reset it".
  - e) Value for a route with no history: `backfill-orchestrator §5.3 L76` "Telegram own channel, green | none ... | `done` at once" and `L79` "Hashtag or keyword rule without a history route; web | none | `done` at once, note `no_history_route`"; `tg-bot-channel-receiver §5.1 L50` "At onboarding `backfill_status` is set to `capped` (route cap: zero days)" (writer not named); `tg-discussion-receiver §5.1 L51` "`backfill_status` is `capped` from onboarding". (Which hashtag and keyword rules have a backfill route at all is AU-042 in `CONFLICTS-ASSUMPTIONS.md`.)
  - f) The completion report that would let the orchestrator write the column alone, with the same writers seen from the report side, is AU-017 (backfill completion) in `CONFLICTS-ASSUMPTIONS.md`, which leaves the column's writers to this entry.
- **At stake:** the state machine (`backfill-orchestrator §5.3 L81`) has several writers: an executing service's `done` and the orchestrator's deadline `capped` can race; if the orchestrator treats TikTok hashtags and keyword rules as rules "without a history route" (L79), its "`done` at once" lands while tt-keyword-search or tt-hashtag-feed-poller is still running its own backfill; and a Telegram bot channel ends `done` or `capped` depending on which code runs; pollers gate on `backfill_status in (done, capped)` so a wrong value starts or blocks rotation.
- **Options:** (1) backfill-orchestrator is the sole writer of `backfill_status` and of the hand-over `next_poll_at` (executing services only report), with `pending` as a column default rather than a registry-writer write; (2) the executing service writes the transitions and the orchestrator only emits jobs and enforces the deadline; (3) registry-writer writes `pending` at insert, the orchestrator every later transition, and one agreed value (`done` or `capped`) for routes with no history.
- **Blocks:** F3, F5, C10, C7, FB2, FB3, VFB1, VFB2, VTT1, VTT2, VTG3, TG1, TG2, N2

### CF-031

**`sources.next_poll_at` and `last_polled_at` on rows that several services rotate: one column, several schedulers with different intervals**

- **Type:** writers
- **Where:**
  - a) News sites: `news-feed-poller §5.1 L42` (tier 1 "every 5 to 15 minutes") and `L44` "`next_poll_at` is set from the START of the last poll (`poll_started_at + interval`)", `§5.2 L58`, `§6.3 L119`; `news-sitemap-poller §5.1 L45` "`poll_started_at + 60 minutes` ... Sites with a news sitemap that also have a feed are polled by both services; the overlap is intentional and harmless", `§6.3 L131`; `news-homepage-differ §5.1 L45`, `§5.2 L59`, `§6.3 L122` (rows disjoint from the feed poller's by design: it selects `news_sites.homepage_diff = true`, `§5.1 L41`, and drops a site that gains a feed or sitemap, `L45`).
  - b) Web keyword rules, one `sources` row per rule: `web-gdelt-poller §5.1 L41` "`next_poll_at = run_started_at + 1 h`", `§5.2 L60`, `§6.3 L117`; `web-search-mojeek §5.1 L42` (12 h priority, 24 h standard) and `L43`, `§5.2 L59`, `§6.3 L113`; `web-search-perplexity §5.1 L41-L42`, `§5.2 L57`, `§6.3 L113`. All three scan the same rows with `next_poll_at <= now()`.
  - c) Instagram accounts and hashtags: `ig-account-media-poller §5.2 L63` sets `last_polled_at`, `next_poll_at`; `ig-mentions-fetcher §5.1 L45` "`sources.next_poll_at` belongs to ig-account-media-poller's rotation of the same row, so this service keeps its own schedule inside its `cursors` row", yet its scheduler selects "a due `next_poll_at`" (`§5.1 L41`) and it sets `last_polled_at` (`§5.2 L60`, `§6.3 L130`); `ig-keyword-search §5.1 L45` keeps its due time in `cursors` "because ig-hashtag-search holds the same hashtag row in fallback" and still sets `last_polled_at` (`§5.2 L63`), while `ig-hashtag-search §5.1 L57`, `§5.2 L69` write both columns on that row.
  - d) Telegram channels with our bot: `tg-bot-channel-receiver §5.1 L44` sets "`check_started_at + 24 h`" on the green push row registry-writer creates (`§5.2 L70`); if the daily reconciliation read that `tg-channel-posts-poller §5.1 L44` promises these channels runs on that row, it writes `poll_started_at + interval` into the same column (`§5.1 L46`, `§5.2 L66`). Whether the poller selects that row at all (it selects `route = amber`, `§5.1 L42`), for Telegram and TikTok alike, is AU-091 (green push source, one row or two) in `CONFLICTS-ASSUMPTIONS.md`.
  - e) Through registry-writer: `yt-pubsub-receiver §5.1 L42` "registry-writer sets the channel's `next_poll_at` to now" on a lapsed lease, `§6.2 L130` "requests to registry-writer (push, promotion, `next_poll_at`, `health`)"; `registry-writer §3 L22` lists no such request among the decisions it applies and `§3 L30` leaves `next_poll_at` to "the pollers"; `yt-uploads-reconciler §5.1 L47` sets `run_started_at + 24 h`. (The missing request path to registry-writer is AU-016 in `CONFLICTS-ASSUMPTIONS.md` and AU-063 in `CONFLICTS-ASSUMPTIONS.md`.)
  - f) Baseline: `CONVENTIONS L51` "the scheduler keeps `next_poll_at` per source"; `CONVENTIONS L36` has one `next_poll_at` and one `last_polled_at` per `sources` row.
- **At stake:** each scheduler selects `next_poll_at <= now()` and writes its own interval into the same column, so whichever service finishes last sets the next run of the others: a hot news feed polled every 10 minutes waits an hour after a sitemap pass, GDELT's hourly rule runs drive the 12 h and 24 h engines (or the reverse), and ig-mentions-fetcher filters on a column it says it does not own; `last_polled_at` (used for staleness alerts) means "any service polled".
- **Options:** (1) one due time per source × service in `cursors`, with `sources.next_poll_at` kept only for the source's primary poller; (2) keep one `sources.next_poll_at` and name one owner per source type, the others deriving their schedule; (3) separate registry rows per service where several services rotate the same thing (for example one keyword-rule row per engine).
- **Blocks:** F3, F5, C7, N3, N4, N5, W1, W2, W4, IG2, IG3, IG5, VIG1, TG1, VTG3, YT2, YT3

### CF-032

**Who writes `sources.health`: registry-writer owns it and applies route-wide changes; a dozen fetchers set one source's health directly**

- **Type:** writers
- **Where:**
  - a) Owner and route-level path: `registry-writer §3 L27` lists `health` among the `sources` columns it owns; `§5.2 L54` applies `health_change` "(from the canary; carries `platform`, `route`, `vendor`, `health`, `fallback`): bulk update `health` for every source on that route and vendor"; `source-health-canary §5.2 L57` writes `health_change` to `registry.decisions`, its rules are "per route key" (`§5.3 L66-L72`, including "fallback or blocked to ok" for the route), and its example decision (`§6.2 L102`) carries no `source_id`; `CONVENTIONS L102` "the canary flips `health = degraded`".
  - b) Fetchers that set one source's health themselves (most also emit `source.events` `updated`): `ig-account-media-poller §8 L141` (`health = blocked`), `ig-mentions-fetcher §8 L143`, `ig-webhook-receiver §5.2 L60` (`health = degraded`), `fb-client-webhook-receiver §5.2 L59` and `§6.3 L137` ("`sources.health` and `tier`" as its state), `li-client-posts-poller §8 L142` and `li-notification-receiver §8 L153` (page `blocked`), `li-company-posts-poller §8 L142` (page `degraded` after three not-found runs), `tt-client-videos-fetcher §8 L130`, `tg-bot-channel-receiver §5.2 L72` and `tg-discussion-receiver §5.2 L69`, `§13 L192` (`degraded`, reason `privacy_mode`), `x-user-timeline-poller §8 L151` and `x-full-archive-search §8 L148`, `yt-uploads-reconciler §8 L154` (`health = degraded`), `web-gdelt-poller §8 L131` (a rule "marked `degraded` with the reason"), `x-recent-search §8 L154` (the keyword rule parked `degraded`, query rejected).
  - c) Per-source changes sent to services that only do route-level ones: `x-compliance-sync §5.3 L83` "The SDK canary hook asks source-health-canary to set `health = blocked`" for one registered source "and sets `health` back to `ok`"; `yt-pubsub-receiver §6.2 L130` sends "requests to registry-writer (push, promotion, `next_poll_at`, `health`)", a request type `registry-writer §3 L22` does not list. `yt-text-purger §5.3 L83` also reads a source's `health` as "set by source-health-canary". (The canary side of this is AU-070, the request path AU-063, both in `CONFLICTS-ASSUMPTIONS.md`; who sets `health = fallback` for a budget-denied Instagram hashtag is AU-087 in `CONFLICTS-ASSUMPTIONS.md`.)
  - d) The value `degraded` or `blocked` on a 401 or 403 is a section 3 (keys, jobs, values) question (CONVENTIONS L101 against README decision 5); this entry is only about who writes the column and how.
- **At stake:** a fetcher's direct write leaves no `registry_audit` row (registry-writer audits what it applies, `§2 L15`), and the next route-wide `health_change` back to `ok` (a bulk update of every source on the route) clears a source that a fetcher set to `blocked` because the bot was removed or the account was suspended; a reason column for `privacy_mode`, `query_rejected` or `uploads_playlist_missing` does not exist in `sources`.
- **Options:** (1) registry-writer is the only writer: fetchers and the canary send source-level decisions (a `health_change` with `source_id` and a reason) and route-level ones stay bulk; (2) fetchers write source health directly and the route-wide update leaves alone sources whose health a fetcher set (for example a `health_reason` or `health_set_by` column); (3) two columns: route health (canary through registry-writer) and source health (fetchers), with pollers stopping on either.
- **Blocks:** F3, F2, C7, C12, IG3, IG4, IG5, FB7, LI1, LI3, VLI3, TT1, TG1, TG2, X3, X5, X7, YT2, YT3, W4

### CF-033

**Registry columns registry-writer says it owns, written or changed by other services: `tier`, `followers`, `platform_id`, `notes`, `last_hit_at`**

- **Type:** writers, names
- **Where:**
  - a) Ownership: `registry-writer §3 L27` owns "`platform_id`, ... `tier`, ... `followers`, ... `health`, `notes`"; `§3 L30` leaves `last_hit_at` to `keyword-matcher`; `§5.2 L53` changes `tier` only on the decisions `tier_change`, `tier_down`, `promote`, `dormant`, `retire`, whose producers (`§4 L36`) are qualifier, source-health-canary, ops, client admins and retention-purger.
  - b) `tier` on dormancy: the qualifier's daily sweep "promotes dormant sources that posted again" (`qualifier §5.1 L46`), yet pollers also announce the change themselves with no decision and no column write: `fb-page-feed-poller §5.2 L59`, `fb-group-posts-poller §5.2 L61`, `ig-account-media-poller §5.2 L63` ("emit `tier change` if a dormant account posted, and `dormant` if the newest post is more than 30 days old"), `tg-channel-posts-poller §5.2 L66`, `li-company-posts-poller §5.2 L61`, `tt-profile-videos-poller §5.2 L62`, `x-user-timeline-poller §5.2 L60`, `yt-uploads-reconciler §5.2 L65`; `fb-keyword-search §5.2 L57` "promote or demote dormancy; record cost" in its after-acknowledgement step, which the inventory lists as a `sources.tier` write; `fb-client-webhook-receiver §5.1 L42` and `yt-pubsub-receiver §5.1 L40` "ask registry-writer to promote" back to push, by a channel registry-writer does not list (AU-016 in `CONFLICTS-ASSUMPTIONS.md`, AU-063 in `CONFLICTS-ASSUMPTIONS.md`; `fb-client-webhook-receiver §6.3 L137` lists "`sources.health` and `tier`" as its own state. (Who may publish `source.events` is section 1 (topics); the sweep-or-poller question is AU-058 in `CONFLICTS-ASSUMPTIONS.md`).)
  - c) `followers`: `tg-bot-channel-receiver §5.2 L72` "`getChatMemberCount` (refresh `sources.followers`)", `§6.3 L138`; registry-writer sets it on every upsert (`§5.3 L73` "`followers = EXCLUDED.followers`"); `yt-channel-resolver §6.3 L138` "`sources.followers` ... written by registry-writer, not here".
  - d) `platform_id`, part of the unique key (`registry-writer §5.3 L70` "`ON CONFLICT (platform, platform_id)`"): `ig-hashtag-search §3 L20` and `§5.2 L66` "store the id on the source"; `tt-hashtag-feed-poller §6.3 L110` "`platform_id` once learned", `§13 L158`.
  - e) `notes`: `fb-backfill §6.3 L114` "`notes` (reason for `capped`)", `§8 L126`, `L131`; `backfill-orchestrator §5.2 L55` "set `done` with a note".
  - f) `last_hit_at`: `keyword-matcher §4 L33` "this service writes only `sources.last_hit_at`", `§5.3 L79` "`greatest(current, hit_at)` ... replays cannot refresh decay"; `x-recent-search §5.2 L59` and `§6.3 L137` also update `last_hit_at` (no rule stated).
  - g) Related: the YouTube uploads playlist id has no `sources` column and each side says the other writes it (`yt-channel-resolver §6.3 L138`, `yt-uploads-reconciler §3 L30`); the full entry is AU-027 in `CONFLICTS-ASSUMPTIONS.md`.
- **At stake:** a dormant source that posts is announced as promoted by the poller while `sources.tier` stays `dormant` (weekly cadence) until the qualifier's next daily sweep, so the event and the column disagree for up to a day; a `platform_id` written by a poller can collide with another row on the unique key registry-writer relies on; two writers of `last_hit_at` with different rules let a replay move the decay clock.
- **Options:** (1) registry-writer is the only writer of these columns: pollers and receivers send decisions (`promote`, `dormant`, an `update` carrying followers, platform id or notes) and registry-writer publishes the events; (2) named exceptions written directly by one owner each (for example `followers` by the bot receivers, `platform_id` by the hashtag pollers, dormancy changes by the poller), listed in CONVENTIONS next to the operational columns; (3) a separate per-source attributes table (or jsonb) owned by the resolvers and pollers for platform facts such as the hashtag id and the uploads playlist id, with `sources` left to registry-writer.
- **Blocks:** F3, C7, C5, C9, C10, FB2, FB3, FB7, VFB1, VFB2, IG2, IG3, VTT2, VTT4, X1, X3, VLI3, TG1, VTG3, YT1, YT2, YT3

### CF-034

**`cursors` rows that are not "source × service": service-level progress rows, rows per class, keyword, hashtag edge or X rule, and a suffixed service name**

- **Type:** key, shape
- **Where:**
  - a) Baseline: `CONVENTIONS L30` "`cursors` (source × service)"; `CONVENTIONS L38` "Per source × service cursor rows in `cursors`: `source_id`, `service`, `cursor` ..., `last_success_at`, `last_error`, `consecutive_errors`".
  - b) Rows with no source, holding a service's own progress: `aggregator §6.3 L97` "(`service = aggregator`, `cursor = recompute:<job_id>:<last hour>`)"; `analysis-entities §6.3 L119`, `analysis-media §6.3 L114`, `analysis-sentiment §6.3 L115`, `analysis-topics §6.3 L122` (`cursor = rerun:<model_version>:<last archive object key>` or similar); `keyword-matcher §6.3 L122` (`rematch:<job_id>:...`); `normalize-item §6.3 L124` (`replay:<version>:<last object key>`); `raw-archiver §6.3 L122`; `store-writer §6.3 L125`; `retention-purger §6.3 L114` "per-sweep watermark per class in `cursors` (`service = retention-purger`, `cursor` = last cut-off)"; `yt-text-purger §5.2 L59` "(`service = yt-text-purger`, cursor = cut-off)".
  - c) Rows keyed by something other than one source: `fb-page-search §5.1 L42` and `§6.3 L123` "`cursors` row per keyword" (its jobs are partitioned by `keyword_id` and carry no `source_id`, `§5.1 L40`); `ig-hashtag-search §6.1 L87` "`cursors` (source × `ig-hashtag-search`)" against `§6.3 L127` "Cursor per hashtag × edge"; `x-filtered-stream §5.1 L42` and `§6.3 L149` one coverage row per X rule (`cursor` = rule id) while a rule names several sources in its tag (`§6.2 L145` "`s=<source ids>`"), and x-user-timeline-poller reads these rows to decide coverage (`§5.1 L42`, `§6.1 L108`, `§14 Q1 L191`); `li-client-posts-poller §5.1 L48` "a second `cursors` row, service `li-client-posts-poller:reconcile`".
  - d) For contrast, the searches that do key on a registry row: `tg-message-search §5.1 L41` (a keyword set is "a registry row of `source_type = keyword_rule` with its own `cursors` row"), `yt-keyword-search §6.3 L127`, `web-gdelt-poller §5.1 L41`.
- **At stake:** the control-plane schema (F3) needs one primary key for `cursors`; with `source_id` in it, the 11 service-level rows, the per-class watermarks, fb-page-search's per-keyword rows and x-filtered-stream's per-rule rows cannot be stored, and ig-hashtag-search's two edges overwrite each other in one row; x-user-timeline-poller cannot map a rule row back to the accounts it covers without reading the rule's tag.
- **Options:** (1) widen the key to `(service, scope_key)` with `source_id` nullable and `scope_key` a source id, keyword id, rule id, class or fixed value; (2) keep `cursors` strictly source × service and move service-level progress (replay, rerun, recompute, rematch, sweeps) and non-source rows to a separate progress table; (3) encode the extra dimension in `service` (as li-client-posts-poller does with `:reconcile`) or in the `cursor` string, leaving the key unchanged.
- **Blocks:** F3, F4, F6, C15, A1, A2, A3, A4, C5, C4, C2, C6, C14, YT7, FB6, IG2, X4, X3, LI1

### CF-035

**What a `cursors` row holds beyond the CONVENTIONS columns: due times, subscription state, job progress, id sets and registry data**

- **Type:** shape, names
- **Where:**
  - a) Baseline: `CONVENTIONS L38` columns `source_id`, `service`, `cursor` ("opaque string: a `since` timestamp, a page token, a `since_id`, a `max_cursor`"), `last_success_at`, `last_error`, `consecutive_errors`.
  - b) Schedules kept in `cursors` as extra columns: `ig-account-resolver §5.1 L46` and `§6.3 L131` "`refresh_due_at`" (who writes the first such row when a source is registered is AU-112 in `CONFLICTS-ASSUMPTIONS.md`); `fb-page-search §5.1 L42` "keeps `next_search_at` per keyword in `cursors` (... cursor = ISO timestamp of the last run start)", `§6.3 L123` "`next_search_at` derived", while `§5.2 L55` writes "the cursor (`next_search_at = run_start + 7 days`)"; `ig-keyword-search §5.1 L45` "The due time lives in this service's own `cursors` row"; `ig-mentions-fetcher §5.1 L45` (the cursor string holds one `since` per edge and `poll_started_at`); `ig-webhook-receiver §6.3 L129` "subscription state, `checked_at` and the reconciliation due time".
  - c) Other state: `web-search-perplexity §6.3 L113` "`last_run_started_at`, `last_success_at`, `results_last_run`, ..." (no `cursor` value named; the sibling engines keep `cursor` = start of the last run, `web-search-mojeek §6.3 L113`, `web-gdelt-poller §6.3 L117`); `x-full-archive-search §6.3 L132` "the running job's progress (`job_id`, `next_token`, oldest `created_at`, highest id, paid reads), cleared at job end"; `yt-web-search-bridge §5.1 L47` and `§6.3 L130` "the 7-day set of sent ids (hashed)"; `fb-group-comments-fetcher §5.2 L66` "update ... `cursors` health" (columns not named).
  - d) A cursor that is not a read position: `x-filtered-stream §6.3 L149` "`cursor` = rule id"; `tg-discussion-receiver §5.2 L67` and `§6.3 L142` "The group row's `cursors.cursor` holds, as JSON, the linked channel's `chat id` and `source_id`" (registry data about another source).
- **At stake:** each of these is a column the F3 migration must create or a format the SDK cursor helper must parse; if `cursor` stays one opaque string, schedulers that sort by `refresh_due_at`, `next_search_at` or a due time cannot index it, and fb-page-search's own text disagrees on whether the stored value is the last start or the next due time.
- **Options:** (1) add named, typed columns (`next_due_at`, `state`, `checked_at`) to `cursors` for schedules and a small set of states; (2) add one `state jsonb` column for per-service extras, with the due time as the only typed addition; (3) keep `cursors` as in CONVENTIONS and move schedules, subscription state and job progress to service-private tables (or `sources`, for the linked-channel link).
- **Blocks:** F3, F5, IG1, IG4, IG5, VIG1, FB6, W1, W2, W4, X4, X5, YT9, TG2, VFB3

### CF-036

**Writes into another service's `cursors` row, and reads of another service's rows as a contract**

- **Type:** writers
- **Where:**
  - a) Backfill seeding the rotation poller's row: `fb-backfill §5.2 L56` "write the fb-page-feed-poller cursor as the newest `created_time` seen (or `window_end` when the feed returned nothing)", `§6.2 L110`; accepted by `fb-page-feed-poller §5.1 L48` "fb-backfill ... writes the cursor"; `x-full-archive-search §5.1 L41`, `§5.2 L56` "raise x-user-timeline-poller's cursor to the highest id read (64-bit integer comparison; never lowered)", `§6.1 L102` reads "x-user-timeline-poller's row"; accepted by `x-user-timeline-poller §5.1 L48`.
  - b) Reading another service's rows as an interface: `x-user-timeline-poller §5.1 L42` "Coverage is read from x-filtered-stream's `cursors` rows", `§6.1 L108`, `§14 Q1 L191` asks to confirm it with x-filtered-stream.
  - c) Baseline: `CONVENTIONS L38` (one row per source × service; nothing says who may write a row) and `CONVENTIONS L71` "cursors advance only after the batch is acknowledged by Redpanda". The other backfill executors (for example `ig-account-media-poller §5.1 L50`, `tg-channel-posts-poller §5.1 L54`) write only their own row.
- **At stake:** the two sides agree in each pair, but no shared document says a service may write another service's row; the SDK cursor helper (F4) and the F3 grants must allow it, a cursor format change in fb-page-feed-poller or x-user-timeline-poller silently breaks the seeding service, and the seeding write is not covered by the poller's own "advance only after acknowledgement" rule (it follows the backfill's acknowledgement instead).
- **Options:** (1) allow named cross-service writes (backfill to rotation row, coverage rows read by the poller) and list them in CONVENTIONS with the cursor format each side relies on; (2) forbid them: the backfill service reports its high-water mark (on `jobs.completed` or to backfill-orchestrator) and the rotation poller seeds its own row on its first job; (3) one shared row per source for rotation and backfill, written by whichever service last read the source.
- **Blocks:** F3, F4, C10, FB2, FB3, X3, X4, X5

### CF-037

**`budgets`: quota-governor's counter rows against services that write usage into them, and configuration other PRDs keep there**

- **Type:** writers, shape
- **Where:**
  - a) Owner and row shape: `CONVENTIONS L30` "`budgets` (API and vendor budgets with counters)", `L85` "the governor keeps counters in `budgets`"; `quota-governor §3 L20-L21` (counters, and "Meta usage headers" among its per-API rules), `§5.2 L58` "reserve with one conditional `UPDATE` on the `budgets` row", `L59` "the governor settles ..., updates ledgers and records Meta usage"; row example `§6.2 L104` (`budget_tag`, `sub_counter`, `unit`, `currency`, `unit_price`, `period`, `limit`, `used`, `reserved`, `mode`, `stretch_factor`, `warn_50_at`, `warn_80_at`, `warn_95_at`) plus `reset_rule` (`§5.1 L53`).
  - b) Services that write into `budgets` themselves: `fb-page-feed-poller §5.2 L60` "the usage headers Meta returns (`X-App-Usage`, `X-Business-Use-Case-Usage`) into `budgets`"; the same step in `ig-account-media-poller §5.2 L65`, `ig-account-resolver §5.2 L64`, `ig-mentions-fetcher §5.2 L62`, `ig-own-comments-fetcher §5.2 L65`; "the rate-limit usage" `li-client-posts-poller §5.2 L62`; "the credits spent" `ig-comments-fetcher §5.2 L64`, `ig-keyword-search §5.2 L64`; "the requests billed" `fb-group-posts-poller §5.2 L62`; "the request count" `tt-profile-videos-poller §5.2 L63`.
  - c) Configuration kept "in `budgets`" that the row shape has no column for: per-job caps "one per job kind ... under `x_pay_per_use`, set by Abdullah and ops" (`x-full-archive-search §7 L138`, `§4 L32`); a Tier 1 interval "set in the `budgets` configuration" (`li-company-posts-poller §5.1 L43`) and a max-items floor and cap (`§5.3 L75`); the LinkedIn vendor split (`li-company-posts-poller §7 L131`, `li-post-search §7 L113`); a max-items cap per run (`li-post-comments-fetcher §5.2 L61`, `§5.3 L80`); a per-minute ceiling (`web-search-perplexity §7 L118`); a backfill allowance (`yt-keyword-search §5.1 L51`); a per-source monthly cap (`ig-keyword-search §7 L127`; per-source and per-service caps are AU-065 in `CONFLICTS-ASSUMPTIONS.md`); the bridge's share of queries (`yt-web-search-bridge §7 L136`); the Instagram hashtag ledger (CF-038).
- **At stake:** the governor reserves and settles with one conditional update per decision; a service that also writes usage into the same rows double counts or races the reservation, and nothing says which column Meta's usage percentages go in; the caps, intervals, splits and ceilings above have no column, so ops cannot set them and the services cannot read them.
- **Options:** (1) quota-governor is the only writer: services pass usage in the SDK `report` (Meta headers included) and configuration lives in named columns or one `config jsonb` per tag row; (2) services write raw usage observations to a separate table the governor folds in, and configuration goes to a separate budget-configuration table; (3) services keep writing platform-reported usage (Meta headers) into named columns of the tag row, the governor alone writes counters and configuration.
- **Blocks:** F3, F5, C1, FB2, VFB2, IG1, IG3, IG5, IG6, VIG1, VIG2, LI1, VLI1, VLI3, VLI4, VTT4, X5, W1, YT8, YT9

### CF-038

**The two quota ledgers: X UTC-day read ledger (one table, three key forms) and the Instagram hashtag ledger (its own table or rows in `budgets`)**

- **Type:** key, shape, single-PRD
- **Where:**
  - a) Where the ledgers live: `quota-governor §6.3 L107` proposes `x_read_ledger` "(UTC day, resource id)" and `ig_hashtag_ledger` "(account, hashtag, first used)"; `README L186` (decision 9) lists both; `ig-hashtag-search §5.1 L57` "The governor keeps, in `budgets`, the ledger of (hashtag id, first queried at)", `§6.1 L87`, `§6.3 L128` "Ledger per client business account in `budgets`"; `ig-keyword-search §13 L169` calls it "the ledger `ig_hashtag_<ig_user_id>`" (the budget tag of `CONVENTIONS L279`). (The hashtag-ledger name is also AU-068 d) in `CONFLICTS-ASSUMPTIONS.md`.)
  - b) Who defines the X ledger: `x-recent-search §3 L21` and `§6.3 L138` "held by quota-governor under `x_pay_per_use`"; `x-filtered-stream §11 L180`, `x-user-timeline-poller §11 L168`, `x-full-archive-search §11 L164` "the read ledger defined by x-recent-search"; `quota-governor §5.3 L68` charges "only the `resource_ids` not yet in today's ledger".
  - c) X ledger key forms: bare post ids in `quota-governor §6.2 L100` (`"resource_ids": ["1842390117700000001", ...]`), `x-filtered-stream §5.2 L62` ("`resource_ids: [<post ids>]`") and `x-user-timeline-poller §5.2 L58`; `x-replies-fetcher §5.2 L57` "Mark each returned post in the read ledger (`x:post:<id>`)" and `§6.2 L116` `"ledger_key": "x:post:1975210483926617088"`; `x-user-resolver §5.2 L57` "Record the read in the UTC-day ledger as `user:<id>` for an organization or public figure, as the keyed hash otherwise". The ledger's one "resource id" column has no type (post or user).
- **At stake:** X bills a post or user once per UTC day only if every service presents the same id for the same resource; `x:post:<id>`, a bare `<id>` and a keyed hash never match, so the same post read by x-replies-fetcher and x-user-timeline-poller is paid twice and a user read keyed by an HMAC cannot be matched by another service reading the same user; the Instagram ledger is either a table or rows in `budgets`, and F3 must create one of them.
- **Options:** (1) one ledger table per API with a typed key (`resource_type` post or user, bare platform id), filled only by quota-governor from `resource_ids`, and the hashtag ledger as `ig_hashtag_ledger`; (2) one generic ledger table `(tag, scope, resource_key, period_start)` for both APIs with one canonical key string per resource; (3) ledgers as rows or JSON inside `budgets`, as ig-hashtag-search describes, with the key format fixed in CONVENTIONS.
- **Blocks:** F3, F5, C1, IG2, VIG1, X1, X2, X3, X4, X5, X6

### CF-039

**`clients` has no column list: the government marker under four names, amber acceptance, X entitlement, token references and per-service settings**

- **Type:** names, shape, writers
- **Where:**
  - a) Baseline: `CONVENTIONS L30` names `clients` with no columns; no PRD names a writer of `clients` (every PRD reads it).
  - b) Government status: `clients.client_type = government` (`keyword-matcher §5.3 L69`; `alert-evaluator §5.3 L65`, `§8 L118` "Missing `client_type`: fail closed"); "government flag" (`ig-keyword-search §6.1 L92`, `tt-keyword-search §6.1 L69`, `tg-channel-posts-poller §6.1 L103`, `quota-governor §6.1 L94`, `registry-writer §6.1 L88`, `source-health-canary §6.1 L96`, `web-search-perplexity §6.1 L86`); "government marker" (`fb-group-posts-poller §6.1 L98`, `fb-keyword-search §6.1 L93`, `fb-group-comments-fetcher §6.1 L100`, `li-post-search §6.1 L79`); "a client flagged as a government body" (`quota-governor §5.3 L85`).
  - c) Amber acceptance: a separate "amber acceptance" (`ig-comments-fetcher §6.1 L89`, `ig-keyword-search §6.1 L92`) against "accepts amber data (the government flag in `clients` is false)" (`tg-channel-posts-poller §5.1 L42`). Which amber services filter on it is AU-092 in `CONFLICTS-ASSUMPTIONS.md`.
  - d) X Enterprise: `clients.x_enterprise` (`keyword-matcher §5.3 L69`) against an unnamed "X Enterprise entitlement" (`x-filtered-stream §6.1 L107`, `x-user-timeline-poller §6.1 L108`, `§14 Q5 L195` "Which `clients` column records a government client's X Enterprise entitlement?"). The app-level alternative and the missing registry check are AU-095 in `CONFLICTS-ASSUMPTIONS.md`.
  - e) Tokens and accounts: "token reference" (`fb-page-feed-poller §6.1 L104`, `fb-page-resolver §6.1 L95`, `fb-post-comments-fetcher §6.1 L95`, `ig-mentions-fetcher §6.1 L100`, `ig-account-resolver §6.1 L98`, `tt-client-videos-fetcher §6.1 L90`, `li-client-posts-poller §6.1 L101`); "token reference and calling account" (`ig-account-media-poller §6.1 L100`); "account to source mapping, token reference" (`ig-webhook-receiver §6.1 L99`); "webhook endpoint and secret reference" (`deletion-propagator §6.1 L86`).
  - f) Other per-client settings: `qualifier_config` jsonb (`qualifier §3 L25`) and "seed lists, priority lists" (`qualifier §6.1 L77`); "seed lists, watchlists" (`poster-resolver §6.1 L83`); a status moving to `offboarding` (`retention-purger §5.1 L43`) and `status = active` with "the `yt_text_refresh` plan entitlement" (`yt-text-purger §5.3 L81`, `§14 Q3 L274` "Where does the `yt_text_refresh` entitlement live on `clients`"); "per-client engine permission flags" (`yt-web-search-bridge §6.3 L131`); Perplexity "opt-out" (`web-search-perplexity §6.1 L86`, `§5.1 L44`); "contract terms" (`tt-profile-videos-poller §6.1 L101`); "roles" (`registry-writer §6.1 L88`).
- **At stake:** the F3 migration must create `clients`, and every amber, X and government rule reads it; with one concept under four names (and amber acceptance sometimes read as "not government"), each service builds its own filter and alert-evaluator's fail-closed rule fires for every client whose column has another name; no service owns the writes, so no PRD defines how the values get there.
- **Options:** (1) one proposal fixing the `clients` columns (identity, `status`, `client_type`, amber acceptance, X entitlement, seed, watch and priority lists, `qualifier_config`, entitlements) with the client app and ops as writers; (2) a small typed core (`status`, `client_type`, `amber_accepted`, `x_enterprise`, `updated_at`) plus one `settings jsonb` for service options; (3) split by concern: `clients` for identity and policy, a token and account reference table (pointing into Vault) and a per-client settings table.
- **Blocks:** F3, C1, C5, C7, C9, C8, C12, C13, C14, A5, YT7, YT9, W1, FB1, FB2, FB5, VFB1, VFB2, VFB3, IG1, IG3, IG4, IG5, VIG1, VIG2, TT1, VTT1, VTT4, VTG3, LI1, VLI1, X3, X4, X5

### CF-040

**`keywords` and keyword-rule `sources` rows: no column list, no writer, and no agreed link between a keyword and the rows the searchers rotate**

- **Type:** names, shape, writers, key
- **Where:**
  - a) Baseline: `CONVENTIONS L30` names `keywords` with no columns; `CONVENTIONS L36` has `source_type` `keyword_rule`; `CONVENTIONS L281` "`source_id` = the keyword-rule or hashtag source that produced the query".
  - b) Columns: `keyword-matcher §5.3 L56` "`keywords` columns read (proposed here): `keyword_id`, `client_id`, `label`, `forms` (jsonb array of `{form_id, text, lang: ar|ckb|en, kind: term|handle|hashtag, boundary: clitic|word|exact}`), `exclusions` ..., `purpose`, `enabled`, `version`, `updated_at`" (and `rematch_days`); against "variants, client ids, Facebook in scope" (`fb-page-search §6.1 L89`, `§5.2 L50`), "the query strings and variants" (`tt-keyword-search §3 L21`), "terms, variants, language, `client_ids`" (`yt-keyword-search §6.1 L92`), "a keyword rule's terms" (`ig-keyword-search §5.2 L60`), "Latin, Arabic and Sorani forms, listed misspellings, context and intent terms, `client_ids[]`, priority flag" (`web-search-mojeek §5.1 L45`, `web-search-perplexity §5.1 L44`), "keyword texts and variants" (`li-post-search §5.2 L57`). One `client_id` per row in keyword-matcher, a `client_ids` list elsewhere.
  - c) Keyword to registry row: `web-search-mojeek §5.1 L42` and `web-search-perplexity §5.1 L41` "Each active `keywords` row has one `sources` row (`platform = web`, `source_type = keyword_rule`) created by registry-writer"; registry-writer's PRD never mentions keyword rules (its decision types `§3 L22`, its columns `§3 L27`); `fb-page-search §5.1 L40` keys its jobs by `keyword_id` (no `source_id`), triggered by "a control-plane change to `keywords` ... emitted by registry-writer"; `tg-message-search §5.1 L41` rotates "a registry row of `source_type = keyword_rule`" per keyword set; `x-recent-search §5.1 L39`, `tt-keyword-search §3 L21` and the other searchers select per-platform `keyword_rule` rows. (The missing creation path in registry-writer is also AU-062 in `CONFLICTS-ASSUMPTIONS.md`.)
  - d) Writers: none; `qualifier §3 L32` puts "Keyword and client management screens" out of its scope, and every PRD only reads `keywords`.
- **At stake:** F3 must create `keywords` and the searchers and keyword-matcher must read the same columns: keyword-matcher compiles `forms` while searchers read "variants", "terms" or per-script forms; no service creates the per-platform keyword-rule rows (or keeps them in step when a client edits a keyword), so the twelve search services have nothing to rotate, and fb-page-search's jobs cannot carry a `source_id`.
- **Options:** (1) adopt keyword-matcher's column list as the base, map "variants", "terms" and "query strings" onto `forms`, and fix one client per row or a `client_ids` list; (2) `keywords` holds the client's terms only, and registry-writer creates and updates one `keyword_rule` row per keyword per platform (or one shared row, as the web engines assume) on a keywords change; (3) the searchers rotate `keywords` rows directly, keyed by `keyword_id` as fb-page-search does, with no keyword-rule rows in `sources`.
- **Blocks:** F3, F2, C5, C7, C9, C6, FB6, VFB1, VIG1, VTT1, X1, X4, X5, VLI1, VTG1, YT8, YT9, W1, W2, W4

### CF-041

**`service_runs`: "last run, lag, errors per service" in CONVENTIONS; per-job result rows, per-page state, connection state and checkpoints in the PRDs, read across services**

- **Type:** shape, key
- **Where:**
  - a) Baseline: `CONVENTIONS L30` "`service_runs` (last run, lag, errors per service)".
  - b) Per-job result rows: `news-comments-fetcher §3 L21`, `§5.2 L59` "write the result row (`new_count`, `seen_count`, `pages`, `cost_units`, `thread_id`, `newest_comment_at`) to `service_runs`", `§6.2 L120` "`service_runs` result rows" (meant for comment-decay-scheduler, which does not read `service_runs`, `comment-decay-scheduler §6.1 L135`); `li-post-search §5.2 L61` "write `service_runs` (`new_count`, `seen_count`, `pages`, `cost_units`)"; `comment-decay-scheduler §14 Q1 L202` names polling `service_runs` as the alternative to `jobs.completed` (the completion transport itself is AU-001 in `CONFLICTS-ASSUMPTIONS.md`).
  - c) Per-entity state: `li-notification-receiver §5.2 L59` "Update the per-page counters and `last_event_at` in `service_runs`", `§6.3 L137` "Per page: subscription state, `last_event_at`, daily event counts (in `service_runs`)".
  - d) Connection, scan and probe state: `x-filtered-stream §5.2 L59` "write `state = connected`, `connection_id` (ULID) and `connected_at` to `service_runs`", `L63` the high-water mark, `§6.3 L149` "`state` (connected, reconnecting, disconnected), `reason`, `connection_id`, high-water mark, last keep-alive and open gaps with job ids"; `web-commoncrawl-scanner §6.3 L107` "The scan checkpoint ... as JSON on this service's `service_runs` row"; `web-search-perplexity §6.3 L113` "`service_runs` (`ckb_supported`, lag, spend this month)"; `aggregator §5.2 L49` "(`last_success_at`, hours touched)".
  - e) Read by other services as an interface: `x-user-timeline-poller §6.1 L108` "`service_runs` (stream state)" of x-filtered-stream; `aggregator §5.2 L49` "so alert-evaluator sees the update".
- **At stake:** F3 needs a key and columns: a row per service cannot hold one row per job, per LinkedIn page or per open gap, and services with several replicas overwrite each other's heartbeat; x-user-timeline-poller and alert-evaluator read fields (stream `state`, `hours touched`) that no shared document defines.
- **Options:** (1) one row per service (and replica) with typed run, lag and error columns plus a `state jsonb` for service-specific fields, per-job results moving to the completion transport; (2) `service_runs` as an append-only run log (one row per run or job, typed counters) with a separate per-service status view; (3) separate tables for the distinct uses: run log, per-entity state (pages, connections) and checkpoints, with the cross-service reads named in CONVENTIONS.
- **Blocks:** F3, F4, F6, C11, C15, A5, N8, VLI1, LI3, X3, X4, W1, W5

### CF-042

**`retention_classes`: two column models (ClickHouse TTLs and the purger's clock table) for one table with no column list and no writer**

- **Type:** shape, names
- **Where:**
  - a) Baseline: `CONVENTIONS L30` names `retention_classes` without columns; the classes are prose (`CONVENTIONS L73-L81`).
  - b) TTL model: `store-writer §5.3 L71` "table TTL deletes the row at `row_expires_at`, read from `retention_classes` (columns `content_ttl`, `row_ttl`, proposed here)", `§14 Q1 L181`; `aggregator §5.3 L61` "`hour_end + row_ttl(class)` (from `retention_classes`)", `§6.1 L74`.
  - c) Clock model: `retention-purger §5.2 L49` "Load the clock table from `retention_classes` (class, anchor, clock, mode, executor, vendor overrides)"; `§12 L150` changes "reviewed by the compliance owner" (no writing service named).
  - d) Readers with no column named: `normalize-item §5.2 L55` stamps "`expires_at` from `retention_classes`"; `raw-archiver §5.3 L73` sets bucket lifecycle rules "from `retention_classes`"; `deletion-propagator §3 L29` "TTL rules in ClickHouse (generated from `retention_classes`)".
  - e) A row nobody else lists: `tt-client-videos-fetcher §6.2 L106` writes `"retention_class": "tiktok_display"` and `§14 Q2 L177` proposes the class (README decision 8). Which classes exist is section 3 (keys, jobs, values); this entry is the table's shape.
- **At stake:** the same class carries a content TTL and a row TTL for ClickHouse and a separate clock, anchor and mode for the purger, so the store can drop or blank rows on a different day from the one retention-purger verifies, and normalize-item's `expires_at`, raw-archiver's lifecycle rules and the ClickHouse TTLs have no agreed column to read; a row must exist for `tiktok_display` before tt-client-videos-fetcher can stamp it.
- **Options:** (1) one table carrying both sets (`class`, `anchor`, `clock`, `mode`, `executor`, vendor overrides, `content_ttl`, `row_ttl`), each column with one stated meaning; (2) the purger's clock columns are the only truth and every TTL (ClickHouse, bucket lifecycle, `expires_at`) is derived from them by the SDK; (3) two tables: a policy table (clock, anchor, mode, executor) and a storage table (TTL per store and class).
- **Blocks:** F3, F8, C4, C2, C6, C13, C14, C15, YT7, TT1

### CF-043

**`review_queue`: one table, about ten uses, columns defined only for the qualifier's review cards**

- **Type:** shape, writers
- **Where:**
  - a) Baseline: `CONVENTIONS L30` lists `review_queue` with no columns; `CONVENTIONS L103` "parks the batch for review" names no table.
  - b) Review cards with a 24-hour clock: `qualifier §5.2 L61` "Every `review` opens a `review_queue` row and posts the n8n card", `§6.3 L90` "`review_queue` (`status`, `opened_at`, `deadline_at`, `reviewer`, `answer`)", `§5.1 L46` (timeouts checked every 15 minutes); `ig-account-resolver §5.2 L62` also writes "for `review`, also a `review_queue` row" for the same candidate before the qualifier sees the profile.
  - c) Parked batches and messages: `normalize-item §5.2 L50`, `§8 L132` ("with the raw object key"); `search-hit-router §5.2 L55`; `web-gdelt-poller §8 L133`, `web-search-mojeek §8 L127`, `web-search-perplexity §8 L128`.
  - d) Annotation and curation tasks keyed by `kind`: `analysis-entities §5.3 L71` (`kind = kb_candidate`) and `L73` (`annotation:entities`); `analysis-sentiment §5.3 L72` (`annotation:sentiment`); `analysis-topics §5.2 L61` (cluster candidates) and `§5.3 L76` (`annotation:topics`); `analysis-media §5.3 L70` (`annotation:media`).
  - e) Operational holds and reports: deletion-guard holds (`yt-comments-fetcher §8 L158`, `yt-replies-fetcher §8 L146`); flooding and screened rules (`x-filtered-stream §5.2 L64` `x_rule_flood`, `§13 L199`); rejected queries (`x-recent-search §8 L154`, `yt-keyword-search §8 L142`); accounts not returned (`ig-account-media-poller §5.2 L64`, reason `not_returned`); a candidate after 5 failed attempts (`news-site-resolver §8 L130`); a daily sample of parse failures (`yt-web-search-bridge §8 L147`).
- **At stake:** F3 needs one row shape: only the qualifier's use has columns, the analysis services key on a `kind` the qualifier never writes, and nothing says who closes a parked batch, a deletion hold or a resolver's review row; if the qualifier's 15-minute timeout scan reads every open row, it default-rejects rows that are not review cards.
- **Options:** (1) one table with common columns (`kind`, `service`, `status`, `opened_at`, `deadline_at`, `reviewer`, `answer`, `payload jsonb`), each service owning its kinds and the qualifier's clock applying only to its own; (2) `review_queue` for the qualifier's cards only, with separate tables for parked batches, annotation tasks and operational holds; (3) two tables: one for anything a person must decide (cards, holds, curation) and one for machine-parked batches and messages awaiting replay.
- **Blocks:** F3, C9, C4, A1, A2, A3, A4, W1, W2, W3, W4, X1, X4, YT5, YT6, YT8, YT9, IG1, IG3, N2

### CF-044

**`decisions`: the qualifier's decision log, also used as fb-page-search's emitted-id set, poster-resolver's hit counter and news-dedup's ops log**

- **Type:** writers, shape
- **Where:**
  - a) Qualifier's table: `qualifier §3 L23` "writing `decisions` (every decision, rejections with a 180-day expiry)"; `§5.2 L63` columns "`decision_id`, `candidate_key`, `rule_hit`, `decision`, `reason`, `client_ids`, `payload`, `expires_at`" and the outbox column `published_at`. CONVENTIONS lists the table (`L30`) with no columns.
  - b) Other writers: `fb-page-search §5.2 L53` "a per-keyword emitted-id set is kept in the control plane as `decisions`-adjacent state" against `§6.3 L123` "(table `decisions`, kind `fb_page_search_emitted`, pruned after 7 days)", a `kind` and a keyword the qualifier's columns do not have; `poster-resolver §5.2 L54` "record the hit on the decision row" (no column for it in the qualifier's list); `news-dedup §8 L123` "the decision is logged in `decisions`" for an ops split of a story (no `candidate_key`); `registry-writer §14 L158` asks whether `decisions` "should carry the before/after values" instead of `registry_audit`.
  - c) Readers of the 180-day rejection memory: `poster-resolver §5.2 L54`, `li-org-resolver §5.2 L51`, `tg-channel-resolver §6.1 L74` (no use stated; its `§5.1 L44` places the 180-day check in poster-resolver), `tg-message-search §5.2 L54`, `news-site-resolver §5.1 L39` (the `candidate_key` forms they look up are a section 3 (keys, jobs, values) question).
- **At stake:** F3 defines `decisions` once; fb-page-search's emitted-id rows and news-dedup's log rows sit next to the rejection memory five services query by `candidate_key`, a 7-day prune runs on a table whose rows must live 180 days, and poster-resolver writes into rows the qualifier owns without a column to write to.
- **Options:** (1) `decisions` stays the qualifier's log with its column list; fb-page-search's set, news-dedup's log and poster-resolver's hit count move to their own tables (or to `cursors`, `news_stories` and `poster_profiles`); (2) `decisions` becomes a generic decision log with `kind`, `scope_key` and `payload`, the qualifier's rows being one kind and every reader filtering on it; (3) the qualifier's columns plus one `hits_since` column that only poster-resolver writes, with the other uses moved out.
- **Blocks:** F3, C9, C8, C7, FB6, N7, VLI2, VTG1, VTG2, N2

### CF-045

**Comment state for change detection: one ledger with two owners, four per-service tables, ClickHouse `comments` read as state by six fetchers, and a shared table proposed**

- **Type:** shape, writers, single-PRD
- **Where:**
  - a) `comment_ledger`, owned or shared: `fb-post-comments-fetcher §6.3 L129` "(control-plane Postgres, owned by this service): per post and comment key, the hash, `created_time`, `state` ..., `superseded_by`, `first_seen_at`, `last_seen_at`"; `fb-group-comments-fetcher §6.3 L132` "(control-plane Postgres, shared design with fb-post-comments-fetcher): per post and comment, the id (if any), `text_hash`, ..." with no `superseded_by`; edits are recorded as a new key with `edit_of` in `fb-post-comments-fetcher §5.2 L68` and as the same key with `version` incremented in `fb-group-comments-fetcher §5.2 L65`; `fb-post-comments-fetcher §14 Q6 L192` asks whether the ledger stays in Postgres rather than ClickHouse.
  - b) Per-service tables: `tt-video-comments-fetcher §6.3 L123` `tt_comment_state` "(one row per video): newest stored `create_time`, stored count, last fetch time, last reply-count per parent comment" and `§14 Q2 L182` "Should per-video comment state live in a shared `comment_state` table used by all comment fetchers"; `yt-comments-fetcher §6.3 L140` "The comment index (Supabase Postgres, owned by this service)", read by `yt-replies-fetcher §5.1 L42` and `§6.1 L95`, which keeps its own "reply index" (`§6.3 L129`); `x-replies-fetcher §6.3 L138` "The reply index (Supabase Postgres, owned by this service)".
  - c) ClickHouse `comments` read as state: `ig-comments-fetcher §5.2 L62` and `§6.3 L119` "No per-post state of its own: stored comments are read from ClickHouse"; `ig-own-comments-fetcher §6.1 L103`; `li-own-comments-fetcher §6.1 L101`; `li-post-comments-fetcher §6.1 L103`; `tt-video-comments-fetcher §6.1 L93` (as well as `tt_comment_state`); `news-comments-fetcher §6.3 L124` "Stored comment ids and content hashes live in the analytics store". The stored hash is normalize-item's `sha256(title + text + media urls)` (`normalize-item §5.2 L51`; the mismatch with the fetchers' hash is AU-090 in `CONFLICTS-ASSUMPTIONS.md`), and `linkedin_48h` rows are deleted at 48 hours (`store-writer §5.3 L77`).
  - d) Series-level state (LinkedIn marker and running total) kept in comment-decay-scheduler's `comment_series` is AU-020 in `CONFLICTS-ASSUMPTIONS.md`.
  - e) Who removes these rows on a deletion or at expiry (`fb-post-comments-fetcher §6.3 L129` "removed by retention-purger with the post's comments", `x-replies-fetcher §6.3 L138` "Rows removed by deletion-propagator when x-compliance-sync reports a deletion") is AU-077 in `CONFLICTS-ASSUMPTIONS.md`.
- **At stake:** the same function (tell new, edited and deleted comments from stored ones) is built five ways; F3 must create `comment_ledger` with one owner and one column list (the two Facebook PRDs disagree on both), plus `tt_comment_state`, the comment index and two reply indexes; the six fetchers that read ClickHouse depend on store-writer's columns, its write delay and the class TTLs (a LinkedIn post's rows are gone before its +3 d fetch).
- **Options:** (1) one shared control-plane `comment_state` table (per post and per comment: ids or keys, hash, state, first and last seen, last complete fetch, reply counts) used by every comment fetcher, as tt-video-comments-fetcher asks; (2) per-service tables as written, with `comment_ledger` given one owner and one column list (or split into a Pages and a groups table); (3) ClickHouse `comments` as the only stored state, with the hash definition, write delay and TTLs fixed so fetchers can rely on it.
- **Blocks:** F3, F8, C6, C11, FB5, VFB3, VTT5, YT5, YT6, X6, VIG2, IG6, LI2, VLI4, N8

### CF-046

**Resolver caches: one table name (`profile_cache`) for four different designs, three other caches, and poster-resolver's `poster_profiles` in front of them all**

- **Type:** names, key, shape, single-PRD
- **Where:**
  - a) `profile_cache` in four PRDs, four keys and column sets: `fb-page-resolver §6.3 L132` "for Pages, `candidate_key`, the profile, `fetched_at`, `expires_at`; for individuals, only the keyed hash and `expires_at`" (`§5.2 L54`); `ig-account-resolver §6.3 L131` "(`candidate_key_hash`, `result`, `resolved_at`, `expires_at`)", keyed "under the SHA-256 of `candidate_key`" (`§5.1 L50`) and proposed in `§14 Q3 L193`; `x-user-resolver §6.3 L136` "profiles under both keys with `fetched_at` and `expires_at`; individuals and unavailable accounts as keyed hashes, verdict and `expires_at` only" (`§5.2 L53` keys individuals by `candidate_ref`); `yt-channel-resolver §6.3 L138` "`candidate_key`, handle aliases, the profile or verdict, `fetched_at`, `expires_at`". Neither CONVENTIONS (`L30`) nor README decision 9 (`L186`) lists it.
  - b) Other resolver caches: `tt-user-resolver §5.1 L43` and `§6.3 L115` `tt_user_cache` "`candidate_key`, the message written, `resolved_at`, `expires_at` (30 days)"; `tg-channel-resolver §5.2 L54` and `§6.1 L73` use the `poster.profiles` topic itself as the 30-day cache; `li-org-resolver §6.3 L109` keeps none ("`decisions` supplies the 180-day memory").
  - c) The cache in front: `poster-resolver §5.2 L53` answers any candidate resolved within 30 days from `poster_profiles` and re-emits the cached profile; `§6.3 L96` columns "`candidate_key` (unique), `status`, `profile` (jsonb, empty for individuals), `author_hash`, `individual`, `followers`, `resolved_at`, `expires_at` (+30 days), `hits_30d`, `unresolvable_reason`"; `§14 L153` asks to add it to the CONVENTIONS list; `§5.2 L59` keeps `platform` and `verified` in an individual's row, which the `§6.3 L96` list does not have.
  - d) How an individual's key is hashed (plain SHA-256, HMAC `candidate_ref`, salted `author_hash`) is a section 3 (keys, jobs, values) question.
- **At stake:** F3 cannot create four tables named `profile_cache`, and one shared table needs one key (plain `candidate_key`, its SHA-256, or a keyed hash) and one set of columns (`fetched_at` or `resolved_at`, `profile` or `result`); with poster-resolver caching every candidate for 30 days as well, a resolver's own cache is reached only on refresh jobs and the two caches can disagree about an account for up to 30 days.
- **Options:** (1) one shared `profile_cache` (platform, key, key form for individuals, profile jsonb, verdict, `fetched_at`, `expires_at`) used by every resolver, TikTok and Telegram included; (2) one cache per resolver under platform-specific names, each defined by its PRD; (3) one cache layer only: `poster_profiles` (resolvers keep none), or the resolvers' caches (poster-resolver keeps only its in-flight `status`).
- **Blocks:** F3, C8, FB1, IG1, X2, YT1, VTT3, VTG2, VLI2

### CF-047

**`news_sites`: read by seven news services, written by news-site-resolver and (per two PRDs) by registry-writer, keyed by host or by `source_id`, possibly folded into `sources`**

- **Type:** writers, key, single-PRD
- **Where:**
  - a) Status: neither `CONVENTIONS L30` nor `README L186` lists `news_sites` (README lists `news_urls`, `news_stories`, `news_story_members`).
  - b) Writers: `news-site-resolver §5.2 L54` "write `news_sites` with `status: candidate`", `§6.2 L79`, `§6.3 L116`; and registry-writer according to `news-site-resolver §4 L32` "registry-writer (materialises the `sources` row and the `news_sites` profile)", `§6.2 L112` "`site_profile` onto `news_sites`, keyed by `source_id`", and `news-feed-poller §5.1 L48` "registry-writer writes the `sources` row and the `news_sites` profile"; registry-writer's own PRD names no `news_sites` (its tables, `§6.1 L88`: `sources`, `client_sources`, `clients`, `registry_audit`). (AU-021 a) in `CONFLICTS-ASSUMPTIONS.md` records the same gap from registry-writer's side, with the crawl-policy health mapping.)
  - c) Key: "one row per host" (`news-site-resolver §6.3 L116`, idempotency on "the canonical host" `§9 L136`) against "keyed by `source_id`" (`§6.2 L112`); `§14 Q2 L172` "Does `news_sites` stay a control-plane table or fold into `sources.notes` as jsonb?"
  - d) Readers: `news-feed-poller §5.1 L40` (`feeds`), `news-sitemap-poller §3 L19` (`news_sitemap`), `news-homepage-differ §3 L19` (`homepage_diff`), `news-robots-checker §6.1 L89`, `news-article-extractor §6.1 L85`, and `news-comments-fetcher §6.1 L88`, which reads "`news_sites` (provider, shortname, identifier template)". The identifier template the profile does not carry (`news-site-resolver §6.2 L96-L104`) and a comments-only health mark are AU-028 (Disqus site fields) in `CONFLICTS-ASSUMPTIONS.md`.
- **At stake:** a candidate host has no `source_id`, so a table keyed by `source_id` cannot hold the resolver's `status: candidate` row, and a table keyed by host needs someone to add the `source_id` after acceptance; registry-writer has no code path that writes `news_sites`, so the pollers' selectors (`feeds`, `news_sitemap`, `homepage_diff`) find nothing for an accepted site.
- **Options:** (1) `news_sites` keyed by host and written only by news-site-resolver (candidate and accepted), with `source_id` added when the site is registered; (2) keyed by `source_id` and written only by registry-writer from the profile carried in the decision, candidates kept by the resolver elsewhere; (3) fold the profile into `sources` (a jsonb column, as the PRD's open question suggests), owned by registry-writer.
- **Blocks:** F3, C7, C9, N2, N3, N4, N5, N1, N6, N8

### CF-048

**`crawl_policies`: row columns against the `crawl.policies` message, and the host-gate slot that every news service writes into the robots-checker's rows**

- **Type:** shape, writers
- **Where:**
  - a) Baseline: `CONVENTIONS L30` lists `crawl_policies` with no columns; `README L183` (decision 6) proposes "a per-host gate in listening-sdk enforcing one connection and 2 to 5 seconds between requests across all news services" without saying where its state lives.
  - b) Row against message: `news-robots-checker §6.2 L117` "the `crawl_policies` row (same fields plus `next_refresh_at` and `next_slot_at`)" against `§6.3 L121` "(one row per host: `status`, `crawl_allowed`, `access_mode`, `crawl_delay_seconds`, `robots` ..., `usage_signals`, `rsl`, `payment`, `checked_at`, `expires_at`, `next_refresh_at`, `policy_version`, `next_slot_at`)", which drops the message's `reason`, `changed_fields`, `requested_by` (example `§6.2 L96-L115`).
  - c) The host-gate slot: `news-feed-poller §5.3 L66` "slot state in `crawl_policies.next_slot_at`", `§6.3 L119`; `news-sitemap-poller §6.3 L131`; `news-homepage-differ §6.3 L122`; `news-article-extractor §6.3 L129`; `news-robots-checker §6.3 L121`. The robots-checker upserts the whole row (`§5.2 L61`) and, on a first check, takes a slot from the gate (`§5.2 L54`) before the host has a row.
  - d) The row's `crawl_allowed = false` mapped onto `sources.health = blocked` by registry-writer (`news-robots-checker §5.2 L61`, `§6.2 L117`) is AU-021 a) in `CONFLICTS-ASSUMPTIONS.md`.
- **At stake:** five services and the robots-checker's full-row upsert write the same row, so a policy refresh can overwrite a slot just taken (or a slot write can clash with the policy upsert), and a first check has no row to hold its slot; `reason` (for example `robots_unreachable`) lives in the message only, so a service reading the row cannot tell why a host is blocked.
- **Options:** (1) keep the gate's `next_slot_at` in `crawl_policies`, with the robots-checker's upsert leaving that column alone and the row created before the first slot; (2) move gate state to its own table (`host_gate`: host, `next_slot_at`, holder) written only by the SDK gate; (3) keep gate state outside the control plane (for example in one gate service's memory or a cache), leaving `crawl_policies` to the robots-checker alone. In each case the row's columns are listed once, with or without `reason` and `changed_fields`.
- **Blocks:** F3, F4, N1, N3, N4, N5, N6

### CF-049

**ClickHouse purges: two field lists for emptying content (deletion-propagator's and store-writer's TTLs), a video title outside "text", and the author column under two names**

- **Type:** shape, names
- **Where:**
  - a) Tombstone rows, the version they need and the `deletion_requests` guard (status `done` against `completed`) are AU-022 in `CONFLICTS-ASSUMPTIONS.md` (`deletion-propagator §5.3 L62`, `store-writer §5.2 L49`, `§5.3 L67`); this entry keeps the field lists and the author column.
  - b) What a text purge empties: `deletion-propagator §5.3 L62` (c) "`text`, `text_norm`, `author_hash` and `url` emptied"; `store-writer §5.3 L71` blanks by column TTL "`text`, `title`, `text_norm`, `url`, `platform_id`, `author_ref`, `media`, `hashtags`, `at_mentions`, `links` and `metrics_snapshot`"; `yt-text-purger §5.3 L108` asks for "`text`, `text_norm` and the author reference null" and treats a video's title and description as `text` (`§5.3 L69`), while `normalize-item §5.3 L71` maps `snippet.title` to a separate `title`.
  - c) Author column: `store-writer §6.2 L110` and `§5.3 L71` name it `author_ref`; `deletion-propagator §5.3 L60` "`scope = author`: select by `author_hash` in `items` and `comments`"; `x-compliance-sync §5.3 L81` and `retention-purger §5.3 L78` produce `author_hash` targets. (How the hash is computed is section 3 (keys, jobs, values).)
- **At stake:** a `purge_text` deletion (the YouTube 30-day purge among them) empties `text`, `text_norm`, the author column and (per deletion-propagator) `url`, and leaves `title`, `platform_id`, `media`, `hashtags`, `at_mentions`, `links` and `metrics_snapshot`, which the TTL list blanks, so a YouTube video keeps its title; an author-scope deletion selects `author_hash`, a column store-writer does not create.
- **Options:** (1) one purge field list in listening-sdk, used by deletion-propagator, by yt-text-purger's requests and by store-writer's TTLs, with one author column name; (2) two lists on purpose (a deletion empties every content field, the TTL only what the class expires), both written out in CONVENTIONS, with one author column name; (3) deletions remove whole rows (or write tombstones, AU-022) instead of emptying fields, leaving store-writer's TTL list as the only field list, with one author column name.
- **Blocks:** F8, C6, C13, C14, C4, X7, YT7

### CF-050

**ClickHouse `analysis` apart from its key: partitioned by its own version column, and several tasks per item and service to keep apart**

- **Type:** partition, key
- **Where:**
  - a) The sorting key itself (`(item_id, model)` with version `analyzed_at`, against `item_id` + `task` + `model_version` in `README L184` and the producers) and the fields the messages do not carry are AU-023 in `CONFLICTS-ASSUMPTIONS.md` (`store-writer §5.3 L61`, `§5.3 L67`); this entry keeps what AU-023 does not cover.
  - b) Partition: `store-writer §5.3 L61` partitions `analysis` by `toYYYYMM(analyzed_at)`, its version column, while `§5.3 L67` states the identity rule that every version of a key lands in one partition ("`created_at` never changes between versions of an item, so every version lands in one partition"); a re-score in a later month lands in another partition, where background merges never replace the older row.
  - c) Tasks per item and service, each needing its own row under whatever key is chosen: `sentiment` and `sentiment_aspect` (`analysis-sentiment §6.2 L89`), five media tasks including `media_fetch` (`analysis-media §6.2 L87`), "one `items.analysis` message per item per taxonomy (`task = topics:<taxonomy_id>`)" (`analysis-topics §5.2 L60`); analysis-media also reads its `media_fetch` rows back as "the url-to-`sha256` lookup" (`analysis-media §6.3 L114`), a lookup by URL in a table sorted by item (where that index lives is AU-025 b) in `CONFLICTS-ASSUMPTIONS.md`).
- **At stake:** with monthly partitions on `analyzed_at` an older score is never merged away, so only readers that take the latest row per key at query time (as `aggregator §5.3 L53` does) see one score per item; whatever key AU-023 settles has to give each task in c) its own row, analysis-media's URL lookup included.
- **Options:** (1) partition `analysis` by the item's `created_at` month, as `items` and `comments` are; (2) keep `toYYYYMM(analyzed_at)` and require every reader to take the latest row per key at query time; (3) partition by `task` (or not at all), with expiry by TTL only.
- **Blocks:** F8, C6, A1, A2, A4, C15

### CF-051

**ClickHouse tables and views beyond CONVENTIONS: `hits` (whose key cannot hold item-less discovery hits), daily and monthly aggregates, and `_v` views with no definition**

- **Type:** single-PRD, key, shape
- **Where:**
  - a) Baseline: `CONVENTIONS L32` lists `items`, `comments`, `analysis`, `metrics_timeseries`, `aggregates_hourly`, `sources_dim`, `keywords_dim`.
  - b) `hits`: `keyword-matcher §14 Q1 L180` "CONVENTIONS lists no hits table. This PRD assumes store-writer fills a ClickHouse `hits` table"; `store-writer §5.3 L63` "`hits` | `row_version` | `client_id, keyword_id, item_id` | `toYYYYMM(hit_at)` | `item.hits`, `discovery.hits`", `§14 Q1 L181` "this PRD adds it"; `keyword-matcher §5.3 L77` `hit_id = uuid_v5(ns_hits, "<item_id>:<client_id>:<keyword_id>")`. The source-finding writers of `discovery.hits` carry no item (`CONVENTIONS L281` "Services that find sources rather than items ... write `discovery.hits` only"; `fb-page-search §6.2 L94-L112` has `keyword_id`, `client_ids` and a `candidate` Page; `search-hit-router §6.2 L101-L115` has `candidate_key`, `poster_ref` and `evidence.keyword_rule_ids`, `client_ids`, no `item_id` or `keyword_id`). (The message shapes themselves are section 1 (topics).)
  - c) Aggregates: `aggregator §6.2 L77` writes "`aggregates_hourly`, `aggregates_daily`, `aggregates_monthly`" and runs the open hour as a refreshable materialized view `mv_aggregates_hourly` (`§5.3 L59`); `§4 L29` "the client app reads the three tables and their `_v` views"; `alert-evaluator §6.1 L78` reads "`aggregates_hourly_v`, `aggregates_daily_v`, `aggregates_monthly_v`"; aggregator names the `_v` views as its own ("the `_v` views hide superseded versions", `aggregator §5.3 L59`; `§4 L29`) and reads `aggregates_hourly_v` (`§5.3 L63`), but gives no definition, and CONVENTIONS lists none. `store-writer §5.3 L82` defines its own masked views `items_v` and `comments_v`.
  - d) Readers each side names: `store-writer §4 L30` "alert-evaluator reads `hits`, `items` and `aggregates_hourly`"; `keyword-matcher §4 L32` "aggregator and alert-evaluator count from it [`hits`]"; `alert-evaluator §6.1 L78` reads neither `hits` nor `items`.
- **At stake:** the F8 schema has to create `hits` and the daily, monthly and view objects that only individual PRDs mention; with `(client_id, keyword_id, item_id)` as the collapsing key, a Page or site candidate from fb-page-search, web-commoncrawl-scanner or search-hit-router has no `item_id` (and often a `client_ids` list instead of one client), so its row cannot be keyed or collapses with others; alert-evaluator's queries target views that no PRD defines.
- **Options:** (1) add `hits`, `aggregates_daily`, `aggregates_monthly` and the views to the CONVENTIONS list, owned by store-writer (`hits`, `items_v`, `comments_v`) and aggregator (aggregate tables and their `_v` views), with item-less discovery hits kept out of `hits` (in Postgres with the candidates, or in a separate ClickHouse table); (2) one `hits` table with a nullable `item_id` and a `candidate_key`, one row per client; (3) no aggregate views: alert-evaluator and the client app query the aggregate tables with `FINAL`.
- **Blocks:** F8, C6, C5, C15, A5, C8, FB6, W3, W5

### CF-052

**ClickHouse `items` and `comments`: column names readers query that store-writer does not define (`published_at`, `permalink`, a `parent_id` key) and a "same names" rule its own example breaks**

- **Type:** names, key
- **Where:**
  - a) Store-writer's columns: `store-writer §5.3 L67` "`items` and `comments` keep every field of `items.normalized/v1` under the same name, plus `likes`, `comments_count`, `shares`, `views` projected from `metrics_snapshot`"; its row example (`§6.2 L99-L119`) flattens `author` into `author_ref`, `author_type`, `author_source_id` and stores the message's `expires_at` as `content_expires_at`; the message (`normalize-item §6.2 L105-L106`) has `url` and `created_at`, no `permalink` or `published_at`.
  - b) `qualifier §5.3 L67` sweep "`SELECT source_id, max(published_at) FROM items GROUP BY source_id`".
  - c) `ig-comments-fetcher §5.2 L58` "resolve the post's `permalink` from ClickHouse `items`".
  - d) `yt-comments-fetcher §4 L34` "ClickHouse `comments`, keyed by `parent_id`" against `store-writer §5.3 L60` (sorting key `item_id`, `parent_id` bloom index) and `CONVENTIONS L70` "stores are upserts keyed on `item_id`".
  - e) The author column (`author_ref` against `author_hash`) is in CF-049 c).
- **At stake:** the qualifier's daily sweep, which drives dormancy and decay for every source, queries a column that does not exist; ig-comments-fetcher cannot find the post URL its vendor call needs; F8 and the SDK's typed readers need one list of column names; if "keyed by" in d) means only "looked up by", d) is wording.
- **Options:** (1) store-writer's column list is the contract published with F8 and readers use its names (`created_at`, `url`), the PRDs corrected; (2) store-writer adds the names readers use (`published_at`, `permalink`) as alias or materialized columns, and its "same name" rule is restated to match its example; (3) readers that need one fact per source or post read it from Postgres or the message instead of ClickHouse (for example a last-post time kept on `sources`).
- **Blocks:** F8, C6, C9, VIG2, YT5

### CF-053

**Object storage: who may write `media/`, `raw/`, `archive/` and `cache/news/`, and what each prefix holds**

- **Type:** writers, names, shape
- **Where:**
  - a) Baseline: `CONVENTIONS L31` "raw payloads under `raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst`; media under `media/<sha256>`; Parquet archive under `archive/<platform>/<yyyy>/<mm>/`"; `raw-archiver §6.2 L96` lists them as its objects, with manifests and `media/<sha256>.refs`.
  - b) `media/<sha256>`, written through raw-archiver's media endpoint (with `.refs`) and directly by analysis-media, is AU-025 in `CONFLICTS-ASSUMPTIONS.md` (`raw-archiver §5.3 L69`, `analysis-media §5.2 L52`); not repeated here.
  - c) `archive/` content: `raw-archiver §5.3 L67` compacts `raw.items` batches into an `envelope` and a `payload` Parquet file; the four analysis services re-run by reading "normalized items from raw-archiver's Parquet archive" (`analysis-sentiment §5.1 L51`, `analysis-entities §5.1 L46`, `analysis-topics §5.1 L50`, `analysis-media §5.1 L47`), which is AU-010 in `CONFLICTS-ASSUMPTIONS.md`; `registry-writer §12 L140` exports `registry_audit` "to the Parquet archive under `archive/registry/<yyyy>/<mm>/`", inside the per-platform namespace.
  - d) `raw/` prefix: batch keys are allocated by the SDK's raw emit helper (`raw-archiver §5.3 L61`) and their width differs (`000123` in `raw-archiver §6.2 L108`, `0007` in `normalize-item §6.2 L119`; `raw-archiver §14 Q1 L181` proposes six digits); `x-compliance-sync §5.2 L56` stores its run evidence ("ids, statuses and X timestamps only") as `raw/green/x/<yyyy>/<mm>/<dd>/x-compliance-sync/<run_id>.jsonl.zst`, files that are not `raw.items` messages, in the prefix raw-archiver manifests and compacts (`raw-archiver §5.2 L52`, `§5.3 L67`); web-commoncrawl-scanner's direct write under the raw path (`web-commoncrawl-scanner §5.2 L54`) is AU-029 in `CONFLICTS-ASSUMPTIONS.md`.
  - e) News full text: `README L183` (decision 6) "news-article-extractor owns the 7-day full-text cache"; `news-article-extractor §5.3 L75` writes `cache/news/<yyyy>/<mm>/<dd>/<canonical_url_hash>.json.zst` and says "raw-archiver never archives full text"; `news-comments-fetcher §5.2 L57` also writes "the full text to the 7-day cache", one object per article and step (`§6.2 L113` `cache/news/comments/.../<article hash>-6h.jsonl.zst`); `raw-archiver §5.3 L82` gives `news_excerpt` "Full-text batches expire after 7 days"; `deletion-propagator §5.3 L68` deletes "by `item_id`" in the 7-day news cache.
- **At stake:** a per-item erasure cannot delete one comment from a per-article cache object; files under `raw/` without a manifest break compaction and the archive's integrity checks or end up compacted as if they were items; the raw-path width is part of every `raw_ref` the stores keep.
- **Options:** (1) raw-archiver is the only writer of `raw/` and `archive/` (and of `media/`, AU-025), and every other writer gets its own named prefix (`cache/news/` for the news services, an evidence prefix for x-compliance-sync, an export prefix for registry-writer); (2) one owner per prefix listed in CONVENTIONS, with the news cache shared by both news writers as per-item objects and x-compliance-sync's evidence kept under `raw/` with a manifest; (3) shared prefixes allowed, with every writer registering its objects in the manifests and the SDK purge registry.
- **Blocks:** F4, F6, C2, C13, C14, A1, A2, A3, A4, C4, C7, X7, W5, N6, N8

### CF-054

**Audit tables: `registry_audit` append-only yet updated as an outbox, and audit trails with no table**

- **Type:** writers, shape, single-PRD
- **Where:**
  - a) `retention_audit`, written by retention-purger and by yt-text-purger with different columns, is AU-024 in `CONFLICTS-ASSUMPTIONS.md` (`retention-purger §6.2 L94`, `§6.2 L110`; `yt-text-purger §6.2 L159`). yt-text-purger's example row (`§6.2 L161-L175`) also carries `executor`, `trigger`, `refreshed`, `text_deleted` and `derived_deleted`, which AU-024 does not list, and `README L186` does not list the table.
  - b) `registry_audit`, append-only and an outbox: `registry-writer §3 L26` "The audit log `registry_audit` ... that doubles as the event outbox"; `§5.2 L58` writes the row with "`event_published_at = null`" and `§5.2 L59` "Commit, publish to `source.events`, set `event_published_at`"; `§9 L123` "`registry_audit` is append-only (no UPDATE or DELETE grant)" and `§13 L154` "An attempt to `UPDATE` ... with the service role fails"; `§14 L158` asks whether `decisions` should carry the before and after values instead.
  - c) Other audit stores: `source-health-canary §5.2 L57` "write the audit row first" and `§6.3 L108` "the audit trail" (no table named; not in CONVENTIONS); `x-compliance-sync §5.2 L59` its own append-only `x_compliance_audit` (`§6.2 L97`); deletion-propagator keeps its audit record in `deletion_requests` (`§5.2 L53`, `§6.2 L90` "status, verification, notice status, `sla_met`").
- **At stake:** registry-writer's outbox step is an `UPDATE` its own grant forbids, so either the relay cannot mark events published or the table is not append-only; the canary's audit trail, from which it rebuilds its 15-minute window after a restart (`source-health-canary §6.3 L108`), has no table in F3.
- **Options:** (1) `registry_audit` split into an append-only audit table and a separate outbox table (or an outbox column under a column-level grant), and the canary's trail given a table of its own; (2) the append-only rule relaxed for `event_published_at` only, and one audit table per service (`registry_audit`, a canary audit, `x_compliance_audit`), each defined by its PRD; (3) one platform-wide append-only `audit_log` (service, kind, subject, `payload jsonb`), with outboxes kept apart.
- **Blocks:** F3, C7, C12, X7, C13

### CF-055

**`deletion_requests`: intake requests and per-message propagation state in one table with no column list, read by `deletion_id`, by `item_id` and by author hash**

- **Type:** shape, key, writers
- **Where:**
  - a) Baseline: `CONVENTIONS L30` lists `deletion_requests` with no columns.
  - b) Writers: `deletion-propagator §5.2 L47` "upsert a `deletion_requests` row keyed by `deletion_id` (status `received`)", `§5.2 L53` status `completed`, `§6.2 L90` "(status, verification, notice status, `sla_met`)", `§7 L119` rows "kept for the life of the contract"; `retention-purger §5.3 L78` "The deletion channel creates a `deletion_requests` row with the requester's contact and the author's handle or profile URL ... erases the handle from the row", `§5.1 L43` (intake from the n8n form and mailbox), `§6.2 L94` "`deletion_requests` (intake and status)".
  - c) Lookups: by `deletion_id` (`retention-purger §5.2 L51`, `x-compliance-sync §5.2 L58` and `yt-text-purger §5.2 L58` wait for `completed`); by `item_id` with status `done` (`store-writer §5.2 L49`) and by author hash (`retention-purger §14 Q2 L171`), which AU-022 c) and d) in `CONFLICTS-ASSUMPTIONS.md` record against the `deletion_id` key.
- **At stake:** one table has to hold a person's intake request (contact details, a handle until hashed) and the processing state of every `deletions` message, whose target may be a list of items, an author, a source or a client; store-writer's per-item guard and a per-author re-ingestion check need rows per item or per hash that a row per `deletion_id` does not provide.
- **Options:** (1) two tables: an intake table for requests from people and a propagation table keyed by `deletion_id`, plus a child table of deleted `item_id`s (and author hashes) for guards; (2) one table keyed by `deletion_id` with the target as jsonb, and a separate permanent deleted-subjects index for guards and re-ingestion checks; (3) one table as deletion-propagator describes, intake being its first status, with every reader using `deletion_id` only and the guards moved to ClickHouse tombstones (AU-022 in `CONFLICTS-ASSUMPTIONS.md`).
- **Blocks:** F3, C13, C14, C6, C4, X7, YT7

### CF-056

**Client priority lists, seed lists and watchlists: kept on `clients`, in `client_sources.priority`, or on `keywords`**

- **Type:** names, shape
- **Where:**
  - a) Baseline: `CONVENTIONS L45` "Tier 1 (100,000 or more followers, or on a client's priority list)"; `CONVENTIONS L243` (qualifier rule 2) "membership of a client seed list"; `CONVENTIONS L276` hashtags tiered by "the client's priority setting". None says where these lists are stored.
  - b) On `clients`: `qualifier §6.1 L77` "`clients` (seed lists, priority lists, `qualifier_config`)"; `poster-resolver §6.1 L83` "`keywords` and `clients` (seed lists, watchlists)".
  - c) In `client_sources`: `registry-writer §5.3 L77` "`client_sources` is upserted on `(client_id, source_id)` with `added_at`, `priority`, `added_by`", its manual add taking `tier_override?` and `priority?` (`§5.2 L61`, `§14 L160`); `li-client-posts-poller §6.1 L101` "`client_sources` (priority list)" and `§14 Q4 L190` "Is the 30-minute priority list the same flag that makes a source Tier 1 in `client_sources`?"; `news-site-resolver §6.1 L75` "`clients` and `client_sources` (seed and priority lists)".
  - d) On keywords: `web-search-mojeek §5.1 L45` and `web-search-perplexity §5.1 L44` read a "priority flag" on the `keywords` row.
  - e) Store not named: `x-user-resolver §6.1 L97` reads "client watchlists" as a separate item beside `clients`; `fb-page-search §5.1 L42` orders jobs "by the client's priority flag".
- **At stake:** tier-1 placement, li-client-posts-poller's 30-minute cadence, the qualifier's decay exemption for listed sources (`qualifier §12 L134`) and rule 2's seed-list signal all read one concept stored in three places, so a client who edits the list in one place changes nothing for the services that read another.
- **Options:** (1) per-source flags in `client_sources` (priority, seed) and per-keyword priority on `keywords`, `clients` holding no lists; (2) lists on `clients` (arrays of source keys or handles) read by every service, with `client_sources.priority` dropped; (3) the lists on `clients` as entered by the client, copied by registry-writer into `client_sources.priority` and `sources.tier` when a source is added or the list changes.
- **Blocks:** F3, C7, C8, C9, X2, LI1, N2, W1, W2, FB6

### CF-057

**Token and key health: 40 PRDs mark a token or key `degraded` and expect later calls to skip it, but only one says where the mark is kept**

- **Type:** shape, writers, names
- **Where:**
  - a) Baseline: `CONVENTIONS L101` "the service marks the token or route `degraded`"; `CONVENTIONS L12` tokens are per client or per company app, from Supabase Vault, "injected per job"; `vendor_keys` is listed with no columns (`L30`).
  - b) Readers that need a stored mark shared across services: `fb-page-feed-poller §5.2 L55` uses "the system-user token of the first client in `client_ids` whose token is healthy" and `§13 L183` "no further call uses that token", while its state (`§6.3 L133`) names no token store; `ig-account-media-poller §8 L141` "When no client in `client_ids` has a healthy token, `health = blocked`"; `tt-client-videos-fetcher §5.2 L55` reads "the account's token record from Supabase Vault" and `§5.2 L56` refreshes it and "store[s] the new access and refresh tokens together in Vault", a service writing Vault where `CONVENTIONS L12` has tokens injected per job.
  - c) The one named store and the key-level columns: `tt-keyword-search §8 L117` "the vendor key is marked `degraded` in `vendor_keys`"; `web-search-mojeek §8 L125` and `web-search-perplexity §8 L126` "the key is marked `degraded`" (store not named); `web-search-mojeek §5.1 L50` and `quota-governor §6.1 L94` read a key's `plan` from `vendor_keys`.
  - d) The same mark with no store named (each in §8): `fb-backfill L127`, `fb-client-webhook-receiver L150`, `fb-page-resolver L144`, `fb-page-search L136`, `fb-post-comments-fetcher L141`, `fb-reactions-fetcher L143`, `ig-account-resolver L145`, `ig-hashtag-search L142`, `ig-mentions-fetcher L143`, `ig-own-comments-fetcher L145`, `ig-webhook-receiver L143`, `li-client-posts-poller L142`, `li-notification-receiver L153`, `li-own-comments-fetcher L142`, `news-comments-fetcher L138`, `tg-bot-channel-receiver L150`, `tg-channel-posts-poller L145`, `tt-hashtag-feed-poller L123`, `x-filtered-stream L162`, `x-full-archive-search L146`, `x-recent-search L151`, `x-replies-fetcher L151`, `x-user-timeline-poller L150`, `yt-channel-resolver L150`, `yt-comments-fetcher L155`, `yt-keyword-search L140`, `yt-replies-fetcher L143`, `yt-uploads-reconciler L153`, `yt-video-details-fetcher L171`, `yt-web-search-bridge L145`, `tt-profile-videos-poller L142`, `tt-user-resolver L126`, `tt-video-comments-fetcher L135`, `tt-video-stats-refresher L128` ("the vendor key and route"), `tg-discussion-receiver L153` (the token). (Whether a 401 or 403 means `degraded` or `blocked` is section 3 (keys, jobs, values).)
- **At stake:** a client's Meta token is shared by fb-page-feed-poller, fb-backfill, fb-page-resolver, fb-page-search and fb-reactions-fetcher; if the `degraded` mark lives in one service's memory, the others keep calling with a revoked token, and "the first client whose token is healthy" cannot be chosen; the F3 schema and the SDK need one place and one column for token and key state.
- **Options:** (1) a token-state column (state, reason, changed_at) in `vendor_keys` for vendor keys and in a client-token reference table (beside `clients`) for per-client and company-app tokens, written through the SDK; (2) one `credentials` table for every token and key (owner, Vault reference, scope, state, plan), read and written only through the SDK; (3) token state kept as `sources.health` or route health only (no token-level mark), so a revoked client token degrades the sources that use it.
- **Blocks:** F3, F4, F6, C12, FB1, FB2, FB3, FB5, FB6, FB4, FB7, IG1, IG2, IG3, IG4, IG5, IG6, LI1, LI2, LI3, N8, TG1, VTG3, VTT1, VTT2, X1, X3, X4, X5, X6, YT1, YT3, YT4, YT5, YT6, YT8, YT9, W1, W2

### CF-058

**`model_versions`: proposed by four analysis PRDs, each naming different parts of it, and read by a service that does not list it**

- **Type:** shape, key
- **Where:**
  - a) Listed by `README L186` (decision 9), not by `CONVENTIONS L30`.
  - b) Parts named: `analysis-sentiment §5.3 L76` "Status lives in control-plane table `model_versions` (proposed): candidate, shadow, active, retired. Switch-over flips one row; aggregator then reads the new version"; `analysis-entities §5.3 L67` and `analysis-topics §5.3 L72` keep thresholds per version in "`model_versions.thresholds`"; `analysis-media §5.3 L74` "`model_versions` (proposed) per task (`media_ocr`, `media_tags`, `media_asr`, `media_logo`)"; `analysis-entities §5.3 L77` and `analysis-topics §5.3 L80` "`model_versions` (proposed)". No PRD gives the key (task, model version, or both) or the full column list.
  - c) Reader: aggregator is said to read the new version after a switch-over (`analysis-sentiment §5.3 L76`), but its control-plane reads are `retention_classes`, `cursors`, `service_runs` (`aggregator §6.1 L74`); how ClickHouse `analysis` keeps one or several versions per item is AU-023 in `CONFLICTS-ASSUMPTIONS.md` (its d) records this reader point too), and its partition is CF-050.
- **At stake:** F3 needs one key and column list for a table four services write; without a task column, the two sentiment tasks and four media tasks cannot each have an active version, and aggregator has no stated way to know which version is active.
- **Options:** (1) one row per (task, `model_version`) with `status`, `thresholds` (jsonb), artefact path and dates, read by aggregator and store-writer for the active version; (2) one row per service and version, tasks inside a jsonb; (3) no table: the active version per task is configuration in each analysis service, and aggregator always takes the newest `produced_at`.
- **Blocks:** F3, A1, A2, A3, A4, C15, C6

### CF-059

**Tables, views and storage paths named in one PRD only (required list)**

- **Type:** single-PRD
- **Where:** each line gives the store, the one PRD that names it with its refs, whether `CONVENTIONS L30` (Postgres), `L32` (ClickHouse), `L31` (object storage) or `README L186` (decision 9) lists it, and who writes it. "README 9" means decision 9 lists it; "neither" means neither document does.
  - a) Postgres:
    - `alert_rules`: `alert-evaluator §5.3 L56`, `§6.1 L80`, `§14 Q1 L163` ("new control-plane tables, absent from CONVENTIONS. Confirm"); neither; read by alert-evaluator, written by the rule editor of the React app (`§3 L27`, no PRD).
    - `alerts`, `alert_deliveries`, `alert_watch_items`: `alert-evaluator §5.3 L61`, `L67`, `L69`, `§6.2 L83`, `§6.3 L105`, `§14 Q1 L163`; neither; alert-evaluator.
    - `backfill_runs`: `backfill-orchestrator §5.2 L57`, `§6.3 L112`; README 9; backfill-orchestrator.
    - `brand_assets`: `analysis-media §5.3 L68`, `§6.1 L84`; README 9; read by analysis-media, writer not named (client reference logos).
    - `budget_reservations`, `budget_history`: `quota-governor §6.3 L107`; README 9; quota-governor.
    - `x_read_ledger`, `ig_hashtag_ledger`: `quota-governor §3 L21`, `§6.3 L107`; README 9; quota-governor. The X PRDs speak of "the read ledger" without the name, and ig-hashtag-search puts its ledger "in `budgets`" (CF-038).
    - `cc_hosts_seen`: `web-commoncrawl-scanner §5.2 L56`, `§6.1 L80`, `§6.3 L107`; neither; web-commoncrawl-scanner.
    - `kb_entities`, `kb_aliases`: `analysis-entities §5.3 L61`, `§6.1 L87`; README 9; read by analysis-entities, filled by curators from `review_queue` candidates (`§5.3 L71`), no writing service named.
    - `taxonomy_nodes`: `analysis-topics §5.3 L68`, `§6.1 L90`; README 9; analysis-topics.
    - `news_stories`, `news_story_members`: `news-dedup §5.2 L58`, `§6.3 L108`; README 9; news-dedup.
    - `registry_audit`: `registry-writer §3 L26`, `§5.2 L58`, `§9 L123`, `§14 L158`; neither; registry-writer (CF-054).
    - x-replies-fetcher's "reply index" (no table name): `x-replies-fetcher §3 L21`, `§6.3 L138`; neither; x-replies-fetcher (CF-045).
    - yt-replies-fetcher's "reply index" (no table name): `yt-replies-fetcher §3 L20`, `§6.3 L129`; neither; yt-replies-fetcher (CF-045).
    - `search_url_seen`, `search_candidate_seen`, `search_parked_urls`: `search-hit-router §5.2 L58`, `L61`, `§6.3 L138`; neither; search-hit-router. (Its `§12 L174` says "the router stores only URL hashes, counts and references", while `search_url_seen` holds the canonical URL and `search_parked_urls` the URL.)
    - `tt_client_video_state`: `tt-client-videos-fetcher §5.2 L60`, `§6.3 L119`; neither; tt-client-videos-fetcher.
    - `tt_comment_state`: `tt-video-comments-fetcher §6.1 L93`, `§6.3 L123`, `§14 Q2 L182`; neither; tt-video-comments-fetcher (CF-045).
    - `tt_user_cache`: `tt-user-resolver §5.1 L43`, `§6.3 L115`; neither; tt-user-resolver (CF-046).
    - `x_compliance_runs`, `x_compliance_audit`: `x-compliance-sync §5.2 L51`, `L59`, `§6.2 L97` ("both to be added to the control-plane table list"), `§6.3 L134`; neither; x-compliance-sync.
    - `yt_live_watch`: `yt-video-details-fetcher §5.1 L54`, `§6.3 L159`; neither; yt-video-details-fetcher.
    - `yt_subscriptions`: `yt-pubsub-receiver §5.1 L42`, `§6.3 L134`; neither; yt-pubsub-receiver.
    - `tg_thread_map`: `tg-discussion-receiver §5.2 L61`, `§6.1 L110`, `§6.3 L142`; neither; tg-discussion-receiver.
    - Telegram onboarding records (no table name): `tg-bot-channel-receiver §5.2 L67`, `§6.1 L109`; neither; "the control plane" (admin page, no PRD); AU-026 in `CONFLICTS-ASSUMPTIONS.md`.
  - b) ClickHouse:
    - `aggregates_monthly`: `aggregator §2 L15`, `§5.3 L59`, `§6.2 L77`; not in `CONVENTIONS L32`; aggregator. (`aggregates_daily` is also named by alert-evaluator; CF-051.)
    - `mv_aggregates_hourly`: `aggregator §5.3 L59`; no; aggregator.
    - `aggregates_daily_v`, `aggregates_monthly_v`: `alert-evaluator §6.1 L78`; no; named by alert-evaluator; aggregator owns them without a definition (CF-051).
    - `items_v`, `comments_v`: `store-writer §5.3 L82`, `§13 L170`; no; store-writer.
    - `system.mutations`: `deletion-propagator §5.3 L62`, `§6.2 L101`; ClickHouse's own system table, read only.
  - c) Object storage (beyond the three patterns of `CONVENTIONS L31`):
    - `<batch>.s<n>.jsonl.zst` supplements: `raw-archiver §5.3 L63`; no; raw-archiver.
    - `archive/<platform>/<yyyy>/<mm>/<dd>-<part>.envelope.parquet` and `.payload.parquet`: `raw-archiver §5.3 L67`, `§6.2 L96`; refines the CONVENTIONS archive pattern; raw-archiver.
    - `media/<sha256>.refs` and the compaction ledger (one marker object per platform and day): `raw-archiver §5.3 L69`, `§6.2 L96`, `§6.3 L122`; no; raw-archiver.
    - `raw/_quarantine/`: `raw-archiver §8 L138`; no; raw-archiver.
    - `archive/registry/<yyyy>/<mm>/`: `registry-writer §12 L140`; no; registry-writer (CF-053).
    - `cache/news/<yyyy>/<mm>/<dd>/<canonical_url_hash>.json.zst`: `news-article-extractor §5.3 L75`, `§6.2 L116`; README decision 6 (`L183`) names the cache, not the path; news-article-extractor.
    - `cache/news/comments/<yyyy>/<mm>/<dd>/<article hash>-<step>.jsonl.zst`: `news-comments-fetcher §5.2 L57`, `§6.2 L113`; no; news-comments-fetcher (CF-053).
    - `raw/green/x/<yyyy>/<mm>/<dd>/x-compliance-sync/<run_id>.jsonl.zst`: `x-compliance-sync §5.2 L56`; inside the CONVENTIONS raw pattern but not a `raw.items` batch; x-compliance-sync (CF-053).
    - The per-host scan aggregate "under the standard raw path": `web-commoncrawl-scanner §5.2 L54`; no path given; web-commoncrawl-scanner (AU-029 in `CONFLICTS-ASSUMPTIONS.md`).
    - `models/entities/<model_version>/`, `models/media/<task>/<model_version>/`, `models/sentiment/<model_version>/`, `models/topics/<model_version>/`: `analysis-entities §5.3 L77`, `analysis-media §5.3 L74`, `analysis-sentiment §5.3 L76`, `analysis-topics §5.3 L80` (one path each); no; writer not named (training pipeline).
    - Client reference logos (no path): `analysis-media §5.3 L68`; no; writer not named.
    - The versioned model bundle (no path): `lang-dialect-id §6.1 L100`; no; writer not named.
  - d) Other stores named once, as possible tables: x-filtered-stream's "blocked-terms list" (`§6.1 L107`, `§14 Q6 L210` "who owns the blocked-terms list?"); source-health-canary's "audit trail" (`§6.3 L108`, CF-054); a fb-reactions-fetcher "small due-time table owned by this service" as an alternative (`§14 Q1 L186`); an aggregator "minute-grain recent table" asked about in `alert-evaluator §14 Q2 L164`.
  - e) Not single-PRD but missing from both lists, for the record: `profile_cache` (4 PRDs, CF-046), `poster_profiles` (CF-046), `comment_ledger` (2, CF-045), yt-comments-fetcher's comment index (2, CF-045), `news_sites` (7, CF-047), `retention_audit` (2, AU-024 in `CONFLICTS-ASSUMPTIONS.md`), ClickHouse `hits` (3, CF-051), `aggregates_daily` and `aggregates_hourly_v` (2 each, CF-051).
- **At stake:** the F3 and F8 schema sessions create only what CONVENTIONS lists plus what is agreed here; each table above is otherwise invented by its own build session, with no review of its key, its retention (several hold ids, hashes or URLs) or its place in the deletion purge registry (for the service-private indexes, AU-077 in `CONFLICTS-ASSUMPTIONS.md`).
- **Options:** (1) add every listed store to CONVENTIONS with the owning PRD's columns as written, service-private tables marked private; (2) add only the stores another service reads (ledgers, `registry_audit`, `news_stories`, `x_compliance_audit`, aggregate tables and views, model and KB tables) and leave service-private state to each session under a naming rule (for example a service prefix); (3) review each store one by one in D2, folding the duplicates into the shared designs of CF-045, CF-046 and CF-054.
- **Blocks:** F3, F8, F4, A5, C10, A1, A2, A3, A4, C1, C3, C12, W5, N7, C7, X4, X6, YT6, W3, TT1, VTT5, VTT3, X7, YT4, YT2, TG2, TG1, C15, C6, C13, C2, N6, N8, FB4


## 3. Keys, jobs, values, budgets, flags, retention, rules and documents

### Keys and identifiers

#### CF-060

**Whose `idempotency_key` wins: the producer's envelope key or normalize-item's mapper key**

- **Type:** key
- **Where:**
  - a) normalize-item computes the key itself: `normalize-item §5.2 L51` "compute `idempotency_key`, `item_id = uuid_v5(ns_items, idempotency_key)`"; the per-route key forms are in its mapper table, `normalize-item §5.3 L62` to `L73`; versions are decided under that key (`§5.2 L52`: "known with a different hash → `version + 1`").
  - b) Producers put a key in the `raw.items` envelope (for example `yt-pubsub-receiver §6.2 L112`, `tt-client-videos-fetcher §6.2 L103`, `tg-bot-channel-receiver §6.2 L122`), and raw-archiver lists `idempotency_key` among the envelope fields it receives (`raw-archiver §5.4 L86`).
  - c) Two deletion paths derive `item_id` from platform ids without the payload: deletion-propagator "derive `item_id` from `<platform>:<kind>:<platform_id>` with the SDK helper that normalize-item uses" (`deletion-propagator §5.3 L60`); x-compliance-sync maps X post ids to `item_id` "through ClickHouse, or through the raw envelope" (`x-compliance-sync §5.3 L81`).
  - d) `CONVENTIONS L69` gives the form `<platform>:<kind>:<platform_id>` but not who applies it; `CONVENTIONS L70` "`normalize-item` deduplicates; stores are upserts keyed on `item_id`".
- **At stake:** where the envelope key and the mapper key differ (CF-061 to CF-066), `item_id` is the uuid v5 of whichever key wins, so dedup, versions, `post_ref` joins and deletion lookups follow that choice; deletion-propagator's derivation from `<platform>:<kind>:<platform_id>` only finds the item when `kind` and the id basis match the stored key.
- **Options:** (1) the producer's envelope key is authoritative; normalize-item validates it against the SDK helper and uses it; (2) normalize-item computes the key and the envelope key is informational (producers may omit it); (3) one SDK key helper with golden vectors per route, used by producers, normalize-item and deletion paths, and a mismatch raises `schema_unknown`.
- **Blocks:** F2, F4, F6, C4, C13, X7, every `raw.items` producer

#### CF-061

**One YouTube video, two keys and two kinds: `youtube:post:` against `youtube:video:`**

- **Type:** key, enum
- **Where:**
  - a) `youtube:post:<id>` with envelope `kind: "post"`: `yt-pubsub-receiver §6.2 L107`, `L112`; `yt-uploads-reconciler §6.2 L113`, `L117`; `yt-video-details-fetcher §6.2 L96`, `L97`, `L136` (`item_idempotency_key`), `§9 L180` ("records keyed `youtube:post:<video id>`"). yt-pubsub-receiver's partial record waits for "yt-video-details-fetcher's full record under the same key" (`yt-pubsub-receiver §6.2 L124`).
  - b) `youtube:video:<videoId>` with `kind: "video"`: `yt-keyword-search §5.1 L48` ("duplicates collapse in normalize-item on `youtube:video:<videoId>`"), `§6.2 L102`, `L104`, `L118` (`"partial": true`), `§13 L174`; normalize-item's YouTube mapper, which names yt-video-details-fetcher: `normalize-item §5.3 L71` (`youtube:video:<id>`).
  - c) Same video in other ids: search-hit-router's candidate key for a watch URL `youtube:video:<id>` (`search-hit-router §5.3 L79`); yt-web-search-bridge's `"extracted": { "kind": "video", ... }` (`yt-web-search-bridge §6.2 L121`).
  - d) `CONVENTIONS L69`: `<platform>:<kind>:<platform_id>`.
- **At stake:** a video found by yt-keyword-search and the same video pushed or reconciled get different keys and `item_id`s; yt-keyword-search's `partial: true` record is never completed by the details fetcher's `youtube:post:` record; normalize-item's mapper adds a third outcome depending on CF-060.
- **Options:** (1) `youtube:post:<id>` with `kind = post` everywhere (yt-keyword-search and normalize-item change); (2) `youtube:video:<id>` with `kind = video` everywhere (yt-pubsub-receiver, yt-uploads-reconciler, yt-video-details-fetcher change); (3) item kind `video` for YouTube and TikTok videos platform-wide (with CF-062), recorded in CONVENTIONS.
- **Blocks:** F2, C4, YT2, YT3, YT4, YT8, YT9, W3

#### CF-062

**TikTok videos: `tiktok:video:` keys under `kind = post` or `kind = video`, and `tiktok:post:` in normalize-item**

- **Type:** key, enum
- **Where:**
  - a) Envelope `kind: "post"` with key `tiktok:video:<id>`: `tt-client-videos-fetcher §6.2 L99`, `L103`, `§9 L140`; `tt-profile-videos-poller §6.2 L110`, `L114`, `§9 L151`.
  - b) `kind: "video"` with key `tiktok:video:<id>`: `tt-hashtag-feed-poller §6.2 L83`, `L85`; `tt-keyword-search §6.2 L77`, `L79`.
  - c) The key reused as a reference: `post_ref` `tiktok:video:<id>` (`tt-video-comments-fetcher §5.1 L41`, `§6.2 L107`); `item_key: "tiktok:video:<id>"` and observation key `tiktok:metrics:<id>:plus_24h` (`tt-video-stats-refresher §6.2 L93`, `L94`).
  - d) normalize-item's TikHub and EnsembleData mapper: `tiktok:post:<aweme_id>` (`normalize-item §5.3 L67`).
  - e) `CONVENTIONS L69` builds the key from `<kind>`.
- **At stake:** the key segment and `kind` disagree inside two PRDs, and normalize-item derives a third form, so the same video from the Display API, a profile poll, a hashtag feed and a keyword search, and the comments and stats that point at it, do not join on one `item_id`.
- **Options:** (1) `kind = post`, key `tiktok:post:<id>` (the six TikTok PRDs change); (2) `kind = video`, key `tiktok:video:<id>` (normalize-item and the two `kind: post` examples change); options 1 and 2 both satisfy `CONVENTIONS L69`; (3) keep `tiktok:video:` with `kind = post`, as a named exception to `CONVENTIONS L69`.
- **Blocks:** F2, C4, TT1, VTT1, VTT2, VTT4, VTT5, VTT6

#### CF-063

**Telegram message keys: `telegram:post:<username>/<id>` against `telegram:message:<chat_id>:<id>`**

- **Type:** key
- **Where:**
  - a) `telegram:post:<username or chat id>/<message_id>`: `tg-bot-channel-receiver §6.2 L121`, `L122`, `§9 L159`.
  - b) `telegram:post:<username>/<message_id>`: `tg-channel-posts-poller §6.2 L115`, `L116`, `§9 L156`; its proposal "`<lowercase username>/<message_id>` on every route, to be agreed with tg-bot-channel-receiver and tg-channel-resolver" (`tg-channel-posts-poller §14 Q4 L194`).
  - c) `telegram:post:<channel_username>/<message_id>`, no case rule: `tg-message-search §5.2 L54`, `§6.2 L80`.
  - d) Comments `telegram:comment:<group chat id>/<message_id>` with `post_ref` in the username form: `tg-discussion-receiver §6.2 L123`, `L124`, `L125`, `§9 L163`.
  - e) normalize-item: `telegram:message:<chat_id>:<message_id>` for the two Bot API services and "same key shape" for tg-message-search and tg-channel-posts-poller (`normalize-item §5.3 L70`); lang-dialect-id's example `record_id` `telegram:message:-1001234567:5521` (`lang-dialect-id §6.2 L116`).
- **At stake:** the kind segment (`post`/`comment` against `message`), the id basis (username against numeric chat id), the separator (`/` against `:`) and case all differ, so a channel reached by the bot and by a vendor is stored twice unless one form wins; a username-based key changes when a channel is renamed, and a private channel has only a chat id.
- **Options:** (1) `telegram:post:<lowercase username>/<message_id>` and `telegram:comment:<chat_id>/<message_id>`, chat id only where no username exists (the Telegram PRDs; normalize-item changes); (2) `telegram:message:<chat_id>:<message_id>` everywhere (normalize-item; the vendor routes must learn the numeric chat id); (3) numeric chat id with `post`/`comment` kinds and `/`.
- **Blocks:** F2, C4, TG1, TG2, VTG1, VTG3

#### CF-064

**LinkedIn post and comment keys differ by route: share URN, activity URN, bare id**

- **Type:** key
- **Where:**
  - a) Posts: `linkedin:post:urn:li:share:<id>` on the green route (`li-client-posts-poller §6.2 L113`, `L114`); `linkedin:post:urn:li:activity:<id>`, else `linkedin:post:<sha256(url)>` (`li-post-search §6.2 L91`, `L105`); `linkedin:post:<bare id>` (`li-company-posts-poller §6.2 L110`, `L111`). A page a client starts administering moves from li-company-posts-poller to the green poller (`li-company-posts-poller §3 L26`).
  - b) Comments: `linkedin:comment:urn:li:comment:(<post urn>,<id>)` with a share-URN `post_ref` (`li-own-comments-fetcher §6.2 L113` to `L115`; `li-notification-receiver §6.2 L120` to `L122`); `linkedin:comment:<bare id>` with a bare `post_ref` (`li-post-comments-fetcher §6.2 L115` to `L117`), else `linkedin:comment:<post_id>:<sha256(created_time + text)>` (`§6.2 L129`).
  - c) normalize-item: "share and comment urns" (`normalize-item §5.3 L69`).
- **At stake:** a client's post read by the green poller and found again by the vendor search or company poller is stored twice; a page moving from amber to green re-keys its history; normalize-item expects URNs that the amber routes do not send.
- **Options:** (1) one URN form (share or activity) on every route, converted in the adapter; (2) bare numeric ids everywhere; (3) route-specific keys plus a cross-route join key in normalize-item.
- **Blocks:** F2, C4, LI1, LI2, LI3, VLI1, VLI3, VLI4

#### CF-065

**An X reply: `x:comment:<id>` from x-replies-fetcher, `x:post:<id>` from every other X reader**

- **Type:** key, enum
- **Where:**
  - a) `x:comment:<id>` with envelope `kind: "comment"`: `x-replies-fetcher §6.2 L111`, `L115` (its read-ledger key is `x:post:<id>`, `L116`); `§14 Q5 L203`: "A reply also delivered as a post by x-recent-search or x-filtered-stream arrives as `x:post:<id>`; normalize-item must decide how it links to `x:comment:<id>`".
  - b) `x:post:<id>` for whatever the reader returns, replies included: `x-recent-search §5.2 L57`; `x-filtered-stream §9 L170`. x-full-archive-search says `x:post:<id>` (`x-full-archive-search §9 L155`) but also that its replies messages "otherwise match x-replies-fetcher's" (`§6.2 L128`).
  - c) normalize-item maps all five X readers to `x:post:<id>`, with `referenced_tweets` deciding the item kind `reply`, `quote` or `post` (`normalize-item §5.3 L68`).
- **At stake:** one reply read by the recent search and again by the replies fetcher becomes two items with two `item_id`s; x-compliance-sync maps post ids to `item_id` with one rule (`x-compliance-sync §5.3 L81`), so a deleted reply can survive under the other key.
- **Options:** (1) `x:post:<id>` for every X post including replies, with `reply`/`quote` as the item kind (normalize-item; x-replies-fetcher and x-full-archive-search change); (2) `x:comment:<id>` for replies whichever service reads them (the other readers classify by `referenced_tweets` before keying); (3) both keys kept and linked by normalize-item.
- **Blocks:** F2, C4, X1, X4, X5, X6, X7

#### CF-066

**Instagram: vendor ids against Graph ids for the same post, and hash-based comment keys**

- **Type:** key
- **Where:**
  - a) Posts: ig-keyword-search keys `instagram:post:<platform_id>` on vendor ids and says "Vendor ids may differ from Graph ids, so the same post can arrive by two routes" (`ig-keyword-search §9 L144`); it proposes that "normalize-item also joins on the shortcode in `permalink`" (`§14 Q2 L182`); ig-mentions-fetcher asks whether its ids equal Business Discovery's and the webhook's, "which the deduplication relies on" (`ig-mentions-fetcher §14 Q3 L192`). Graph routes key on the media id (`ig-account-media-poller §6.2 L113`; `ig-hashtag-search §6.2 L91`). normalize-item has no shortcode join and no SociaVault Instagram mapper (`normalize-item §5.3 L65`, `L66`).
  - b) Comments without a vendor id: ig-comments-fetcher builds `instagram:comment:<post id>:<hash>`, "the construction already used for Facebook comments under PPCA" (`ig-comments-fetcher §6.2 L102`, `L115`), while normalize-item lists ig-comments-fetcher under the Graph mapper with `instagram:comment:<id>` only (`normalize-item §5.3 L66`). The hash form is a CONVENTIONS rule for Facebook PPCA comments only (`CONVENTIONS L69`); see CF-067.
- **At stake:** a post seen on a Graph route and through the vendor is stored twice; a vendor comment without an id gets a key normalize-item's mapper does not produce.
- **Options:** (1) a cross-route join on the shortcode in normalize-item, Graph media id as the canonical key; (2) the adapter resolves vendor ids to Graph ids before writing (where it can); (3) accept duplicates across routes and mark the route on each item.
- **Blocks:** F2, C4, IG2, IG3, IG5, VIG1, VIG2

#### CF-067

**Comments without platform ids, and how an edited comment is keyed: same key and a version, or a new key**

- **Type:** key, rule
- **Where:**
  - a) The hash key `<platform>:comment:<post_id>:<sha256(created_time + text)>` is a CONVENTIONS form "for Facebook comments under PPCA (no ids)" (`CONVENTIONS L69`). It is also used by fb-group-comments-fetcher for vendor comments without ids (`fb-group-comments-fetcher §5.4 L94`), by ig-comments-fetcher (`ig-comments-fetcher §6.2 L102`, `L115`) and by li-post-comments-fetcher (`li-post-comments-fetcher §6.2 L129`).
  - b) An edit becomes a new key: fb-post-comments-fetcher's edit candidate is a new hash whose message "carries `edit_of` (the old idempotency key) and normalize-item stores it as a new version" (`fb-post-comments-fetcher §5.2 L68`, `§13 L176`); news-comments-fetcher puts a version in the key, `news:comment:6203918455:v1` (`news-comments-fetcher §6.2 L101`), "with a version suffix for edits" (`§9 L149`), "a new version (`:v2`)" (`§13 L175`), and its step 6 calls the change a new version (`§5.2 L58`); fb-group-comments-fetcher without ids: a new hash as an edit candidate, the old row `superseded`, with no `edit_of` named (`fb-group-comments-fetcher §5.2 L65`).
  - c) An edit is a new version of the same key: fb-group-comments-fetcher, with ids (`fb-group-comments-fetcher §5.2 L65`, `§13 L179`); fb-client-webhook-receiver (`fb-client-webhook-receiver §5.2 L56`); ig-comments-fetcher (`ig-comments-fetcher §5.1 L49`); tg-bot-channel-receiver (`tg-bot-channel-receiver §9 L159`); tg-discussion-receiver (`tg-discussion-receiver §9 L163`). normalize-item versions only under one key ("known with a different hash → `version + 1`", `normalize-item §5.2 L52`) and reads no `edit_of` field.
  - d) Inside CONVENTIONS: "changed text becomes a new version" (`CONVENTIONS L63`) against the hash key, under which changed text is a new key (`CONVENTIONS L69`).
- **At stake:** with a new key per edit, normalize-item creates a second item instead of a second version, so mentions, hits and comment counts double and the old text is not superseded; with the hash key, nothing links the old and new comment except `created_time`.
- **Options:** (1) same key with a `version` field everywhere; id-less routes carry the link to the old hash in a field (`edit_of`) that normalize-item reads; (2) a new key per edit plus `edit_of` (or a `:vN` suffix), and normalize-item links them as versions; (3) as written per route, with normalize-item handling both `edit_of` and `:vN`.
- **Blocks:** F2, C4, FB5, FB7, VFB3, VIG2, VLI4, N8

#### CF-068

**Item kind vocabulary: `post`/`video`, `post`/`message`, `comment`/`reply`, and kinds no consumer handles**

- **Type:** enum
- **Where:**
  - a) Videos as `post` or `video`: CF-061 and CF-062.
  - b) Telegram: envelope `kind: "post"` and `"comment"` (`tg-bot-channel-receiver §6.2 L118`; `tg-discussion-receiver §6.2 L119`) against normalize-item's `telegram:message:` key (`normalize-item §5.3 L70`) and keyword-matcher's post-like kind `message` (`keyword-matcher §5.3 L74`).
  - c) X replies: envelope `kind: "comment"` (`x-replies-fetcher §6.2 L111`) against normalize-item's item kind `reply` (`normalize-item §5.3 L68`); store-writer routes "`kind` of `comment` or `reply`" to `comments` (`store-writer §5.2 L47`).
  - d) `quote`: produced by normalize-item (`normalize-item §5.3 L68`) and stored in `items` (`store-writer §5.3 L59`), but keyword-matcher routes only "post, video, article, message, result" to discovery and "Comments, replies" to mentions (`keyword-matcher §5.3 L74`, `L75`), so a quote by an unregistered author (non-null `author_ref`) fits neither the discovery branch (`L74`) nor the mention branch (`L75`); quotes by registered sources go to `item.hits` (`keyword-matcher §5.3 L73`).
  - e) Non-content kinds on `raw.items`: `profile` (`poster-resolver §5.2 L58`, `§6.2 L92`; `tg-channel-resolver §5.2 L57`) and `reaction` (`li-notification-receiver §3 L21`, `§5.4 L98`). normalize-item's mapper table has no entry for them (`normalize-item §5.3 L62` to `L73`), and store-writer sends every kind other than comment or reply to `items` (`store-writer §5.2 L47`).
  - f) CONVENTIONS lists no item kinds; the word `kind` names both the item kind inside keys (`CONVENTIONS L69`) and the job kind (`CONVENTIONS L277`), see CF-077.
- **At stake:** keyword-matcher, store-writer and normalize-item branch on the item kind; a kind one of them does not list is dropped, misrouted into `items`, or parked as `schema_unknown`.
- **Options:** (1) one closed item-kind list in F2 (for example post, video, comment, reply, quote, article, message, result), with each consumer's handling stated and `profile` and `reaction` records flagged so normalize-item skips them; (2) a closed list of content kinds only, with profile and reaction records moved off `raw.items` (a section 1 (topics) follow-up); (3) open per-platform kinds with a default branch stated in each consumer.
- **Blocks:** F2, C4, C5, C6, C8, LI3, VTG2, X6

#### CF-069

**Author identity: three field names, four derivations, several renderings and scopes**

- **Type:** names, types, key
- **Where:**
  - a) normalize-item's helper: `author_ref = hmac_sha256(AUTHOR_HASH_KEY, platform + ':' + author_platform_id)` (`normalize-item §5.2 L54`), rendered `"hmac:9c1f…"` (`§6.2 L111`); stored as ClickHouse `author_ref` (`store-writer §6.2 L110`, column TTL `§5.3 L71`) and carried in hits (`keyword-matcher §6.2 L111`).
  - b) A different function under another name: poster-resolver `author_hash = sha256(platform || platform_id || salt)`, salt in Vault (`poster-resolver §5.2 L59`, `§6.3 L96`, `§9 L118`), carried by qualifier's `mention_only` (`qualifier §5.2 L58`) and registry-writer's audit rows (`registry-writer §9 L124`).
  - c) The deletion paths call normalize-item's helper but name the result `author_hash`, and look for that column: retention-purger "computes `author_hash` with the SDK helper that normalize-item uses (`AUTHOR_HASH_KEY`)" (`retention-purger §5.3 L78`); x-compliance-sync maps X user ids to `author_hash` with the same helper (`x-compliance-sync §5.3 L81`); deletion-propagator selects and empties `author_hash` in `items` and `comments` (`deletion-propagator §5.3 L60`, `L62`, `§5.4 L80`, `§13 L161`).
  - d) Edge hashes written before `raw.items`, under several names and renderings: `author_ref` as 64 bare hex (`fb-client-webhook-receiver §6.2 L126`; `fb-group-comments-fetcher §6.2 L121`; `fb-group-posts-poller §6.2 L117`; `fb-keyword-search §6.2 L113`); `ah1:` plus 32 hex (`ig-comments-fetcher §5.4 L79`); `hmac:` plus 16 or 20 hex (`tg-discussion-receiver §6.2 L126`, secret in `vendor_keys` per `§6.1 L110`; `x-replies-fetcher §6.2 L119`; `yt-comments-fetcher §6.2 L122`; `yt-replies-fetcher §6.2 L111`); `author_hash` `hmac256:` plus 16 hex of the vendor user id, called "the same function every platform uses" (`tt-video-comments-fetcher §5.3 L68`, `§5.4 L82`); `author_hash` as HMAC of `"disqus:" + author id`, bare 64 hex (`news-comments-fetcher §5.3 L76`, `§6.2 L109`); `{"ref": sha256(salt + profile identifier)}` in the payload (`li-post-comments-fetcher §5.2 L63`, `§5.4 L84`).
  - e) Scoped hashes that cannot equal a platform-wide one: "scoped to the video's channel" (`yt-comments-fetcher §5.2 L56`, `§14 Q4 L206`; `yt-replies-fetcher §5.2 L53`); "scoped to the post's source", so "one author under posts of two sources gets two different `author_ref` values" (`x-replies-fetcher §5.2 L59`, `§13 L189`); guests hashed per thread (`news-comments-fetcher §5.3 L76`).
  - f) Individuals in resolver answers: `candidate_ref`, a keyed hash (`fb-page-resolver §6.2 L128`; `x-user-resolver §5.2 L53`, `§6.2 L132`); `candidate_key_hash`, a plain SHA-256 of `candidate_key` (`ig-account-resolver §5.1 L50`, `§6.2 L127`); tt-user-resolver's individual answer keeps the clear `candidate_key` (`tt-user-resolver §5.1 L41`, `§6.2 L111`), and `§14 Q3 L171` asks whether poster-resolver should hash it.
  - g) Two PRDs ask for one shared function: `ig-comments-fetcher §14 Q2 L179` ("sharing the key so one person keeps one reference across services"); `tt-video-comments-fetcher §14 Q4 L184` (does normalize-item accept a pre-computed `author_hash`).
- **At stake:** an author request or an X user deletion computes one hash and searches ClickHouse for a column name and value no writer produces; one person gets different references on different routes and services, so distinct-author counts and author-scope deletions miss, and per-channel or per-source scopes cannot match a platform-wide request.
- **Options:** (1) one SDK function and one field name (`author_ref` or `author_hash`) for every producer and consumer: input `<platform>:<author platform id>`, one key, one rendering, and edge hashing (CF-109) calls it; (2) as (1), plus declared scoped variants (per channel, per source, per guest thread) in a second field for the routes that need them; (3) route-specific edge hashes stay, and normalize-item re-derives the canonical reference from the archive (which then must hold the clear id, against CF-109's edge hashing).
- **Blocks:** F2 (helper and golden vectors), F4, F6, C4, C6, C7, C8, C9, C13, C14, X7, and every fetcher that hashes at the edge

#### CF-070

**`job_id` formats: ULID in CONVENTIONS, and UUIDs, `job_…`, dated sequences and composite strings in examples**

- **Type:** types, key
- **Where:**
  - a) Rule: "a job carries `job_id` (ULID)" (`CONVENTIONS L277`). Deterministic ULIDs where replay needs a stable id: comment-decay-scheduler "a ULID whose time part is `due_at` and whose random part is the first 10 bytes of `sha256(item_id | lane | series_step)`" (`comment-decay-scheduler §5.3 L84`); backfill-orchestrator (`backfill-orchestrator §5.3 L85`); li-notification-receiver "a ULID assigned at receipt" (`li-notification-receiver §6.2 L133`).
  - b) UUIDs: `li-org-resolver §6.2 L103`; `li-post-search §6.2 L90`.
  - c) `job_` plus 10 characters: `news-site-resolver §6.2 L107`; `tt-hashtag-feed-poller §6.2 L92`; `tt-keyword-search §6.2 L86`; `x-recent-search §6.2 L111`.
  - d) `<prefix>-<yyyymmdd>-<nnnn>`: `web-gdelt-poller §6.2 L100`; `web-search-mojeek §6.2 L97`; `web-search-perplexity §6.2 L98`; `yt-keyword-search §6.2 L113`; `yt-web-search-bridge §6.2 L118`.
  - e) Composite: poster-resolver's resolve job `"job_id":"res:x:1234567890"` (`poster-resolver §5.3 L67`); `producer.job_id` values `analysis-entities:priority:0009` and the like (`analysis-entities §6.2 L97`, `analysis-sentiment §6.2 L96`, `analysis-topics §6.2 L100`, `analysis-media §6.2 L94`) and `fb-page-feed-poller:2026-10-06T09:00Z:7c1e` (`normalize-item §6.2 L98`).
  - f) No job id: `"job_id": null` for stream records (`x-filtered-stream §6.2 L121`) and in keyword-matcher's `producer` (`keyword-matcher §6.2 L102`); the Telegram receivers carry `update_id` instead (`tg-bot-channel-receiver §6.2 L123`; `tg-discussion-receiver §6.2 L127`).
- **At stake:** F2 needs one validator and the DLQ and replay tooling deduplicate on `job_id`; a UUID or composite id fails a ULID check, and an envelope `job_id` that is null or absent breaks the log rule "logs carry `job_id`" for push records.
- **Options:** (1) ULID everywhere, deterministic where the PRD needs replay-stable ids, and a stated rule for push records (assigned at receipt, as li-notification-receiver does); (2) ULID for jobs, free-form strings allowed in `producer.job_id` provenance fields; (3) accept UUID or ULID in the validator.
- **Blocks:** F2, F4, F6

#### CF-071

**`item_id`: uuid v5 of the key in items, ULIDs in deletion targets**

- **Type:** types, key
- **Where:**
  - a) Derivation: `item_id = uuid_v5(ns_items, idempotency_key)` (`normalize-item §5.2 L51`); examples in the v5 pattern `6f1d2c3e-9a4b-5c6d-…` in `normalize-item §6.2 L99`, `store-writer §6.2 L101`, `keyword-matcher §6.2 L104`, `analysis-sentiment §6.2 L98`, `analysis-topics §6.2 L102`, `analysis-entities §6.2 L99`, `analysis-media §6.2 L96`, and in comment-decay-scheduler's `post_ref.item_id` (`comment-decay-scheduler §6.2 L141`); deletion-propagator derives `item_id` "with the SDK helper that normalize-item uses" (`deletion-propagator §5.3 L60`).
  - b) ULID-shaped `target.item_ids` in deletion messages: `retention-purger §6.2 L102`; `x-compliance-sync §6.2 L105`; `yt-text-purger §6.2 L149`.
- **At stake:** the three deletion producers fill `item_ids` with values no store holds, so deletion-propagator's `scope = item` lookup by `target.item_ids` finds nothing; F2 fixtures and validators need one format.
- **Options:** (1) uuid v5 of the idempotency key everywhere (the three deletion examples change); (2) ULIDs everywhere, which are not derivable from the key, so deletion paths must look ids up instead of deriving them; (3) another named deterministic hash of the key, applied everywhere.
- **Blocks:** F2, C4, C6, C13, C14, X7, YT7

#### CF-072

**`client_id` and `keyword_id` value formats: UUIDs against `cl_17` and `kw_0412`**

- **Type:** types
- **Where:**
  - a) UUIDs: `keyword-matcher §6.2 L106` (`client_id`, `keyword_id`); `aggregator §6.2 L82`, `L83`; `alert-evaluator §6.2 L91`, `L92`; `fb-page-search §6.2 L103` (`keyword_id`); `client_ids` UUIDs in most platform examples (for example `tg-bot-channel-receiver §6.2 L127`, `tt-client-videos-fetcher §6.2 L107`).
  - b) Short prefixed ids: `"client_ids":["cl_17"]` in `poster-resolver §6.2 L89`, `qualifier §6.2 L84`, `registry-writer §6.2 L95`, `search-hit-router §6.2 L112`, `L129`, `web-search-perplexity §6.2 L99`, `web-search-mojeek §6.2 L98`, `web-gdelt-poller §6.2 L101`; `cl_a1b2` in `tg-message-search §6.2 L85`; keyword ids `kw_0412` (`poster-resolver §6.2 L89`; the three web engines, next to a UUID `keyword_rule_id` on the same line), `kw_7f3a` (`tg-message-search §6.2 L84`), `kw_zain_4g` (`tt-keyword-search §6.2 L90`); a seed-list entry `client_17` (`news-site-resolver §6.2 L92`).
- **At stake:** F2 fixtures, F3 column types (`uuid` or `text`) and every join from hits to `clients` and `keywords` follow the answer; mixed fixtures make contract tests pass on one side and fail on the other.
- **Options:** (1) UUID for `client_id` and `keyword_id` everywhere; (2) short prefixed text ids everywhere; (3) UUID storage with a prefixed display form that never appears in messages.
- **Blocks:** F2, F3

#### CF-073

**`candidate_key` forms: two forms in CONVENTIONS, typed and domain forms in the routers and one resolver**

- **Type:** key
- **Where:**
  - a) Rule: `<platform>:<platform_id>` or `<platform>:<handle>` (`CONVENTIONS L281`; `poster-resolver §3 L22`; `keyword-matcher §5.3 L74`), the forms x-user-resolver and yt-channel-resolver resolve (`x-user-resolver §3 L19`; `yt-channel-resolver §3 L19`).
  - b) Other forms: li-org-resolver computes `linkedin:org:<handle>` (`li-org-resolver §5.2 L50`, `§6.2 L83`) while search-hit-router emits `linkedin:<slug>` for the same company page (`search-hit-router §5.3 L81`); search-hit-router also emits `instagram:post:<shortcode>` when no handle is readable (`§5.3 L74`), `facebook:group:<id or slug>` (`§5.3 L75`), `youtube:video:<id>` for watch URLs (`§5.3 L79`) and `news:<registrable domain>` (`§5.3 L83`), the last also used by web-commoncrawl-scanner (`web-commoncrawl-scanner §6.2 L93`).
  - c) References a resolver does not accept: yt-web-search-bridge extracts `c/<name>` and `user/<name>` channel references and sends them as `resolve` jobs (`yt-web-search-bridge §5.2 L59`, `L61`); yt-channel-resolver resolves only `youtube:<channel id>` and `youtube:<handle>` (`yt-channel-resolver §3 L19`).
  - d) No key can be formed: ig-hashtag-search's discovery hit carries `"poster":{"handle":null,"platform_id":null,...}` (`ig-hashtag-search §6.2 L124`).
- **At stake:** poster-resolver deduplicates and routes by `candidate_key`; `linkedin:org:x` and `linkedin:x` never meet, a three-part or domain key reaches a resolver that cannot parse it, and a hit with neither handle nor id cannot become a candidate at all.
- **Options:** (1) the two CONVENTIONS forms only, with routers mapping posts, groups, videos and legacy channel URLs to a resolvable id or handle before emitting; (2) a typed form `<platform>:<type>:<id>` that poster-resolver and every resolver parse, CONVENTIONS restated; (3) the two forms plus named exceptions (`news:<registrable domain>`, `facebook:group:<id>`).
- **Blocks:** F2, C8, IG2, VLI2, YT1, YT9, W3, W5

#### CF-074

**`post_ref` in comment, reply and metrics jobs: an object from the scheduler, a different string in every fetcher**

- **Type:** shape, key
- **Where:**
  - a) Rule: `post_ref` "for comment, reply and metrics jobs", no shape given (`CONVENTIONS L277`).
  - b) Object from the only emitter of those jobs: `"post_ref": {"item_id": …, "platform": "facebook", "platform_id": …}` (`comment-decay-scheduler §6.2 L141`).
  - c) What each consumer reads: no `post_ref` at all but `platform_id` in fb-reactions-fetcher's metrics job (`fb-reactions-fetcher §5.2 L53`); `<page-id>_<post-id>` (`fb-post-comments-fetcher §5.1 L42`); "the post's platform id and permalink; for `replies` also the parent `comment_id`" (`fb-group-comments-fetcher §5.1 L40`); no shape stated (`ig-comments-fetcher §5.1 L41`), while its vendor call needs the post's `permalink` (`§5.3 L68`); a media id (`ig-own-comments-fetcher §5.1 L41`); "the post URN" (`li-own-comments-fetcher §5.1 L38`); a bare post id (`li-post-comments-fetcher §5.1 L40`, example `§6.2 L117`); `tiktok:video:<id>`, "or the parent comment's key for replies" (`tt-video-comments-fetcher §5.1 L41`; `tt-video-stats-refresher §5.1 L42`); "the video" (`yt-comments-fetcher §5.1 L40`); "video id and thread id" (`yt-replies-fetcher §5.1 L38`; `§14 Q3 L192` asks to align the shape); a video id (`yt-video-details-fetcher §6.1 L86`); a composite of article item id, canonical URL, `disqus_shortname`, thread identifier or id, and newest stored comment time (`news-comments-fetcher §5.1 L41`).
  - d) Other producers on the same queues: an array of up to 50 video ids (`yt-uploads-reconciler §6.2 L133`) and a single id string (`yt-pubsub-receiver §6.2 L127`) on `jobs.yt-video-details-fetcher`; a media id in ig-webhook-receiver's targeted reads (`ig-webhook-receiver §5.2 L58`); `post_ref` plus `thread_ids` in yt-text-purger's refresh jobs (`yt-text-purger §5.3 L102`).
  - e) The fetchers copy their form into the `raw.items` envelope, where it is the comment-to-post join: media id (`ig-comments-fetcher §6.2 L108`), full key (`tt-video-comments-fetcher §6.2 L107`), URN or bare id (`li-own-comments-fetcher §6.2 L115`; `li-post-comments-fetcher §6.2 L117`), the channel post's `platform_id` (`tg-discussion-receiver §6.2 L125`).
- **At stake:** every comment and metrics fetcher parses `post_ref`; an object from the scheduler fails each string-based consumer on the first job, and the envelope `post_ref` joins a comment to its post only if every route uses the same form.
- **Options:** (1) the scheduler's object `{item_id, platform, platform_id}` on every queue, with optional route fields beside it (permalink, thread ids, parent comment id); (2) a string `platform_id` per platform, extras as separate job fields; (3) the post's full idempotency key as a string (CF-060 decides which key).
- **Blocks:** F2, C11, FB4, FB5, VFB3, IG4, IG6, VIG2, LI2, VLI4, VTT5, VTT6, TG2, YT2 to YT7, X5, X6, N8

#### CF-075

**Analysis keys and lanes (README decision 7): a four-part key from analysis-topics, a store keyed on `item_id, model`, lanes per service**

- **Type:** key, names, document
- **Where:**
  - a) Proposal: "a priority lane per task (`jobs.analysis-<task>.priority`) for tier-1 sources; `items.analysis/v1` keyed by `item_id:task:model_version` with an `input_hash`" (`README L184`, decision 7).
  - b) A task name with a colon: analysis-topics publishes "one `items.analysis` message per item per taxonomy (`task = topics:<taxonomy_id>`)" (`analysis-topics §5.2 L60`), so its key has four colon-separated parts, `…:topics:global:topics-iq-2026.11.tx7` (`§6.2 L101`, `L105`), against three in `analysis-sentiment §6.2 L97`, `analysis-media §6.2 L95` and `analysis-entities §6.2 L98`.
  - c) The store's identity: `analysis` sorted on `item_id, model`, "a newer model version replaces the older" (`store-writer §5.3 L61`), carrying `model`, `model_version` and `output` (`§5.3 L67`), while all four analysis PRDs declare the logical key `item_id` + `task` + `model_version` (`analysis-sentiment §6.2 L89`; `analysis-topics §6.2 L93`; `analysis-media §6.2 L87`; `analysis-entities §6.2 L90`). The column side is also a section 2 (tables) question.
  - d) Lanes per service, not per task: analysis-media's five tasks share `jobs.analysis-media.priority` (`analysis-media §5.1 L43`, `§6.1 L83`, `§6.2 L87`); analysis-sentiment's `sentiment` and `sentiment_aspect` share `jobs.analysis-sentiment.priority` (`analysis-sentiment §6.1 L85`, `§6.2 L89`).
- **At stake:** a consumer that splits `analysis_key` on `:` misreads the topics key; store-writer's ReplacingMergeTree on `item_id, model` collapses different tasks of one model (sentiment and aspect, or two taxonomies) into one row; the queue names in README decision 7 are not the ones the PRDs consume.
- **Options:** (1) README decision 7 (per-task lanes, key `item_id:task:model_version`), completed by a task-name rule without `:` (for example `topics.global`) and a store keyed on `item_id, task` with the newest `model_version` winning; (2) the same key, with per-service lanes `jobs.<analysis service>.priority` recorded instead of per-task lanes; (3) structured key fields (`item_id`, `task`, `model_version`) instead of a concatenated string, and the store keyed on them.
- **Blocks:** F2, F8, C6, A1, A2, A3, A4

#### CF-076

**`deletions` reasons, scopes and modes that deletion-propagator does not list**

- **Type:** enum
- **Where:**
  - a) The consumer's sets: reasons `platform_sync`, `retention`, `author_request`, `client_offboarding`, `legal` (`deletion-propagator §3 L19`); a target by `platform`, `kind` and `platform_id`, `item_ids`, `author_hash`, `source_id` or `client_id`, and "`mode` (default `delete`)" (`§5.4 L80`); scopes `item`, `author`, `source`, `client` and modes `delete`, `purge_text` (`§5.3 L60`, `L62`).
  - b) yt-text-purger: scope `text_only` with mode `purge_text` and a `fetched_before` guard (`yt-text-purger §5.3 L106`), and scope `derived` with "the new mode `purge_derived`" (`§5.3 L118`).
  - c) x-compliance-sync: mode `withhold`, "Hidden from Iraqi clients; `countries` carried" (`x-compliance-sync §5.3 L77`), where CONVENTIONS defines the topic as "items or posters to remove, with reason" (`CONVENTIONS L24`).
  - d) tt-client-videos-fetcher proposes reason `authorization_revoked` (`tt-client-videos-fetcher §14 Q3 L178`); its own alert is spelt `authorisation_revoked` (`§10 L146`).
  - e) alert-evaluator fires on "`platform_sync`, or the X compliance reason as named by deletion-propagator" (`alert-evaluator §5.3 L61`) and asks deletion-propagator to name the reasons (`§14 Q3 L165`); x-compliance-sync uses `platform_sync` (`x-compliance-sync §5.3 L81`), so no distinct X reason exists.
  - f) `deletion_id`: x-compliance-sync hashes one `platform_id` (`del:platform_sync:<scope>:<sha256(platform_id, status, signal day)>`) for a message that groups several posts per source and status (`x-compliance-sync §5.3 L81`, example `§6.2 L105`).
- **At stake:** deletion-propagator rejects or misreads scopes and modes it does not list; a `withhold` handled as a delete removes content that should only be hidden from Iraqi clients; alert-evaluator cannot tell an X compliance deletion from other `platform_sync` deletions; a grouped message has no stable id for its members.
- **Options:** (1) extend deletion-propagator's sets with every value above, defined once in F2; (2) map them onto the existing set (`text_only` as `item` plus `purge_text`; `derived` as `item` plus a derived-rows delete) and move `withhold` out of `deletions` to its own field or topic; (3) keep `deletions` for removal only and give retention text purges and withholding their own mechanisms.
- **Blocks:** F2, C13, C14, X7, YT7, TT1, A5

### Jobs and job kinds

#### CF-077

**The job vocabulary: `kind` or `reason`, seven kinds in CONVENTIONS and about thirty in the PRDs, and job fields outside the list**

- **Type:** job kind, enum, names, shape
- **Where:**
  - a) Rule: "a job carries `job_id` (ULID), `source_id`, `kind` (rotation, reconciliation, backfill, comments, replies, metrics, ops_force), `due_at`, `attempt`, `post_ref` (for comment, reply and metrics jobs), `series_step` (for comment jobs)" (`CONVENTIONS L277`). The same word `kind` is the item kind inside keys (`CONVENTIONS L69`); on `raw.items` the job kind travels as `job_kind` (`normalize-item §5.2 L49`; `comment-decay-scheduler §5.1 L66`; `x-full-archive-search §6.2 L128`; `web-search-perplexity §6.2 L89`).
  - b) The job-type field named `reason`: `reason` = rotation | reconciliation | ops_force, plus `tier` (`fb-page-feed-poller §5.2 L54`, the poller CONVENTIONS L278 names as the reference); `reason = add | ops | client` with `window_start`, `window_end` (`fb-backfill §5.1 L41`); `reason = seed | weekly`, keyed by `keyword_id` with no `source_id` (`fb-page-search §5.1 L40`, `§5.2 L50`); `reason` = rotation | first_run | gap_backfill | ops_force, plus `tier` (`x-recent-search §5.2 L53`); `reason = lease_lapsed` beside `kind = reconciliation` (`yt-uploads-reconciler §5.1 L51`). Sibling pollers call the same field `kind` (`fb-group-posts-poller §5.2 L56`).
  - c) Kinds outside the list (consumer, line): `resolve` (`fb-page-resolver §5.1 L42`; `ig-account-resolver §5.1 L42`, which says "job schema gains `kind = resolve`" at `§11 L165`; `x-user-resolver §5.1 L41`; `yt-channel-resolver §5.1 L44`; `news-site-resolver §5.1 L38`; `tt-user-resolver §3 L19`; emitter `poster-resolver §4 L37`, `§5.3 L67`); `resolved`, `unresolvable`, `manual_candidate` (`poster-resolver §5.1 L46`); `refresh` (`li-org-resolver §5.1 L44`; `tg-channel-resolver §5.1 L44`; `news-site-resolver §5.1 L38`; `news-robots-checker §3 L19`; `yt-text-purger §5.3 L96`); `first_check`, `recheck` (`news-robots-checker §3 L19`); `first_sight` (`yt-video-details-fetcher §5.1 L44`; "missing from the addendum's job-kind list; add it", `yt-pubsub-receiver §14 Q5 L194`); `refresh_24h`, `refresh_7d`, `refresh_client` (`fb-reactions-fetcher §5.1 L41`, `L47`); `site_search` (`web-search-perplexity §6.1 L85`); `keyword_history` ("The addendum's job kinds have no `keyword_history`", `x-full-archive-search §3 L20`, `§14 Q1 L189`); `push` ("job schema gains `kind = push`", `ig-webhook-receiver §5.2 L55`, `§11 L162`); `health` (`comment-decay-scheduler §5.1 L57`); `replay`, `lang_rescore` (`normalize-item §6.1 L86`); `rematch`, `candidate_retry` (`keyword-matcher §6.1 L90`); `analyze`, `rerun` (`analysis-sentiment §6.1 L85`; `rerun` also `analysis-entities §5.1 L46`, `analysis-topics §5.1 L50`, `analysis-media §5.1 L47`); `recompute` (`aggregator §5.1 L37`; `deletion-propagator §5.3 L70`); `retention_sweep` (`retention-purger §5.3 L63`; `yt-text-purger §5.1 L44`).
  - d) A client's refresh of one post has no kind in CONVENTIONS although `CONVENTIONS L61` allows it: `kind = refresh_client` (`fb-reactions-fetcher §5.1 L47`); `ops_force` "uses the same job kind" (`fb-post-comments-fetcher §4 L35`); `comments` with `series_step = refresh:<request_id>` (`comment-decay-scheduler §5.1 L70`); `metrics` with `series_step` `client` (`yt-video-details-fetcher §5.1 L45`).
  - e) Fields outside the CONVENTIONS list: `tier` (b above); `candidate_key`, `client_ids`, `origin`, `url_or_handle`, `seed_list` in resolver jobs (`li-org-resolver §5.1 L44`; `tg-channel-resolver §5.2 L52`, which has no `source_id` and no `kind`); `set_id`, `keyword_ids`, `window_start`, `window_end` with no `source_id`, `kind` or `due_at` (`tg-message-search §5.2 L51`); `run_id`, `cap`, `route`, `vendor` (`backfill-orchestrator §6.2 L106`); `profile`, `route`, `vendor` (`comment-decay-scheduler §6.2 L141`), `thread_ids` (`§5.3 L94`); `query`, `source_ids`, `client_ids`, `window_start`, `window_end`, priority (`x-filtered-stream §5.2 L70`); `priority` (`tt-user-resolver §5.1 L41`).
- **At stake:** F2's job schema and the SDK job wrapper reject a field or kind they do not know, or accept everything; a consumer dispatching on `kind` never sees a `reason`, and a producer cannot know which of `kind`, `reason` and `job_kind` to set.
- **Options:** (1) one closed list of kinds in F2, extended with every kind above that D2 keeps, one field name `kind`, and kind-specific fields declared per kind; (2) a common job envelope (CONVENTIONS' fields) plus service-private kinds and fields declared per queue in each PRD, validated per queue; (3) the CONVENTIONS list only, with the extra kinds folded into it (for example `refresh_24h` as `metrics`, `first_sight` as `metrics` or `reconciliation`, `keyword_history` as `backfill`) and the extra meaning carried in `series_step` or `reason` fields.
- **Blocks:** F2, F4, F5, F6, and every service that consumes or produces a job

#### CF-078

**Job kinds no producer emits**

- **Type:** job kind
- **Where:** each sub-point names the consumer that accepts the kind and what the named producer's own PRD says. Sub-points with their own entry are listed with a pointer.
  - a) Ops and client requests with no writing component: `ops_force` on most queues, with "producer not stated" or "ops can force …" (for example `ig-mentions-fetcher §4 L34`, `fb-post-comments-fetcher §4 L35`); `rerun` that "ops creates" (`analysis-sentiment §5.1 L51`; `analysis-media §5.1 L47`) or with no producer named (`analysis-entities §5.1 L46`; `analysis-topics §5.1 L50`, which also re-runs "only that client's window" when a client adds a topic); `replay` that "ops creates" (`normalize-item §5.1 L45`); `rematch` run by ops (`keyword-matcher §4 L34`) and on a keyword change with no emitter (`keyword-matcher §5.3 L81`, `§13 L172`); `recompute` as "the ops entry point" (`aggregator §5.1 L37`); `refresh_client` that "a client can request" (`fb-reactions-fetcher §5.1 L47`); fb-backfill's on-demand `reason = ops | client` (`fb-backfill §5.1 L41`); backfill re-runs "on request from `client_admin` … or `ops`" (`backfill-orchestrator §5.1 L50`). No PRD or CONVENTIONS line names the component (admin API, n8n flow, CLI) that writes these messages.
  - b) `resolved` and `unresolvable` on `jobs.poster-resolver` (`poster-resolver §5.1 L46`, `§5.3 L70`): none of the eight resolvers writes that queue; see CF-085.
  - c) `replies` on `jobs.ig-own-comments-fetcher`: the fetcher lists `replies` (`ig-own-comments-fetcher §3 L19`) and expects comment-decay-scheduler to emit one when nested replies are incomplete (`§5.1 L51`); the scheduler's `ig_own` profile says "field expansion; no job" (`comment-decay-scheduler §5.1 L50`).
  - d) `replies` on `jobs.x-full-archive-search`: it names comment-decay-scheduler, "the only emitter of reply jobs" (`x-full-archive-search §5.1 L39`); the scheduler's `x` profile has replies "by `conversation_id:`; no job" (`comment-decay-scheduler §5.1 L53`) and its write list has no `jobs.x-full-archive-search` (`§6.2 L138`). See also CF-084.
  - e) `site_search` on `jobs.web-search-perplexity`, named as coming from yt-web-search-bridge and charged to the bridge's own `budget_tag` (`web-search-perplexity §3 L25`, `§5.2 L53`, `§13 L165`; `web-search-mojeek §3 L31`, `§14 Q4 L172`); yt-web-search-bridge emits no such job: it calls both engines itself "through the shared vendor clients" and asks for `mojeek_search` and `perplexity_search` (`yt-web-search-bridge §3 L21`, `§5.2 L56`, `L58`).
  - f) `refresh` on `jobs.li-org-resolver` "from qualifier" (`li-org-resolver §5.1 L44`); qualifier's PRD puts resolving identities out of scope and writes no job (`qualifier §3 L31`, `§6.2 L81`, `L87`). See CF-085.
  - g) The daily reconciliation job on `jobs.li-own-comments-fetcher`: "comment-decay-scheduler emits one reconciliation job a day" while a post is younger than 7 days, when the comment count from li-client-posts-poller "through `item.metrics`" differs from the running total of comments seen (`li-own-comments-fetcher §5.1 L48`, `§13 L183`); li-notification-receiver calls it "the safety net" it relies on (`li-notification-receiver §5.1 L44`, `§5.2 L57`). comment-decay-scheduler's `li_own` profile has only "+6 h, +24 h, +3 d" (`comment-decay-scheduler §5.1 L55`), its PRD never mentions a reconciliation job or reading `item.metrics`, and the fetcher runs the daily reconciliation as one of its `kind = comments` jobs (`li-own-comments-fetcher §3 L19`, `§5.1 L38`), so the reconciliation job has no producer, and nothing in a `comments` job marks it as a whole-thread reconciliation.
  - h) `metrics` on `jobs.tg-channel-posts-poller`: see CF-082. `refresh_24h` and `refresh_7d` on `jobs.fb-reactions-fetcher`: see CF-081. `gap_backfill` on `jobs.x-recent-search`: see CF-084. `backfill` on queues missing from backfill-orchestrator's route table (fb-keyword-search, ig-keyword-search, ig-mentions-fetcher, li-post-search, tt-client-videos-fetcher) and fb-backfill's `reason = add`: see CF-088.
  - i) `reason = seed` on `jobs.fb-page-search`, "emitted by registry-writer" on a `keywords` change (`fb-page-search §5.1 L40`); registry-writer's writes name no such job (`registry-writer §6.2 L91`): see AU-062 in `CONFLICTS-ASSUMPTIONS.md`.
- **At stake:** each consumer builds and tests a path that nothing in production triggers, or (for ops and client jobs) a path that only a component nobody builds can trigger; the features behind them (re-runs, replays, reply threads, client refreshes, Perplexity site search for YouTube, the LinkedIn comment reconciliation) do not happen.
- **Options:** per sub-point: (1) name the producer and add the kind to its PRD; (2) remove the kind from the consumer; for (a): (3) one admin component (API or n8n flow, to be named) writes every ops and client job, with a schema per kind in F2.
- **Blocks:** F2, F4, C4, C5, C8, C11, C15, A1, A2, A3, A4, IG6, X5, W1, W2, YT9, VLI2, LI2, LI3

#### CF-079

**Job kinds a producer emits that the consumer does not accept**

- **Type:** job kind
- **Where:**
  - a) `backfill` on `jobs.news-feed-poller`: backfill-orchestrator's route table sends news sites to "news-feed-poller and news-sitemap-poller (whichever the site has)" (`backfill-orchestrator §5.3 L78`); news-feed-poller consumes `kind` = rotation | ops_force only (`news-feed-poller §5.2 L52`). news-feed-poller, news-site-resolver and news-sitemap-poller name news-sitemap-poller, or web-commoncrawl-scanner where there is no sitemap, as the backfill route (`news-feed-poller §5.1 L48`; `news-site-resolver §5.1 L41`; `news-sitemap-poller §3 L29`), while web-commoncrawl-scanner has no backfill role (`web-commoncrawl-scanner §5.1 L44`) and no row in the route table (AU-103 in `CONFLICTS-ASSUMPTIONS.md`).
  - b) `health` on `jobs.tg-discussion-receiver`: comment-decay-scheduler's `tg_own` profile sends "one daily `health` job" (`comment-decay-scheduler §5.1 L57`); tg-discussion-receiver consumes `reconciliation` and `ops_force` (`tg-discussion-receiver §6.1 L110`), says "comment-decay-scheduler emits no jobs for this route" (`§5.1 L45`) and runs its own daily health check as `reconciliation` (`§5.1 L47`).
  - c) `resolve` on `jobs.li-org-resolver` and `jobs.tg-channel-resolver` (`poster-resolver §5.2 L56`, `§5.3 L67`), whose consumers name only `refresh` and origins (`li-org-resolver §5.1 L44`; `tg-channel-resolver §5.2 L52`): see CF-085.
  - d) A targeted `ops_force` "one id" on `jobs.ig-mentions-fetcher` (`ig-webhook-receiver §5.2 L57`), whose jobs carry only `source_id`, `kind`, `attempt` (`ig-mentions-fetcher §5.2 L55`) and whose `ops_force` is a forced poll of one account (`§4 L34`): see CF-080.
  - e) `refresh` from yt-text-purger on the three YouTube fetcher queues: see CF-080. `metrics` on `jobs.fb-reactions-fetcher`: see CF-081. `first_sight` shapes on `jobs.yt-video-details-fetcher`: see CF-083. `reconciliation` gap jobs on `jobs.x-recent-search`: see CF-084. `backfill` with `cap` and `run_id` on `jobs.fb-backfill`: see CF-088.
- **At stake:** the consumer parks or drops the job (unknown kind, `schema_unknown`, DLQ after 5 attempts), so the producer's work silently never happens: news history is not backfilled through feeds, a Telegram group's health is checked twice or not at all.
- **Options:** per sub-point: (1) the consumer accepts the producer's kind (its PRD and F2 change); (2) the producer sends a kind the consumer lists, or stops sending; (3) for (a) and (b): drop the producer's row (news backfill only through news-sitemap-poller; no `tg_own` profile in comment-decay-scheduler).
- **Blocks:** F2, C10, C11, C8, N3, TG2, VLI2, VTG2, IG4, IG5

#### CF-080

**Comment, reply and metrics work emitted by services other than comment-decay-scheduler**

- **Type:** rule, writers, job kind
- **Where:**
  - a) Rule: "comment, reply and metrics jobs are emitted only by comment-decay-scheduler" (`CONVENTIONS L278`); comment-decay-scheduler: "It is the only service that emits comment, reply and metrics jobs" (`comment-decay-scheduler §1 L9`).
  - b) ig-webhook-receiver's own scheduler sends "two `reconciliation` jobs" per due account, one on `jobs.ig-own-comments-fetcher` covering "media still inside the first 7 days of their series" (`ig-webhook-receiver §5.1 L43`), and targeted `ops_force` reads to both fetchers (`§5.2 L57`, `L58`); ig-own-comments-fetcher accepts the reconciliation job (`ig-own-comments-fetcher §5.1 L41`) while saying in the same paragraph that "A job names one post (`post_ref` = media id) and one `series_step`"; ig-mentions-fetcher's `ops_force` is "force a poll of one account" with no id field (`ig-mentions-fetcher §4 L34`, `§5.2 L55`).
  - c) yt-text-purger emits `kind = refresh` jobs on `jobs.yt-comments-fetcher` (one per video, "listing the due thread ids"), `jobs.yt-replies-fetcher` (one per thread above 5 replies) and `jobs.yt-video-details-fetcher` (50 videos a job), carrying `post_ref`, `thread_ids`, `run_id`, `must_finish_by`, `refresh_for_client_ids` (`yt-text-purger §5.3 L96`, `L98` to `L100`, `L102`). The consumers say "Only comment-decay-scheduler emits these jobs" with kind `comments` (`yt-comments-fetcher §5.1 L40`) or `replies` (`yt-replies-fetcher §5.1 L38`), and yt-video-details-fetcher lists "the 30-day text refresh (yt-text-purger)" as out of scope (`yt-video-details-fetcher §3 L27`).
  - d) Backfilled posts get comment jobs three ways: backfill-orchestrator "emits one comments job each" for the last 30 days of a new LinkedIn page (`li-own-comments-fetcher §3 L19`, `§5.1 L52`; `li-post-comments-fetcher §3 L19`, `§5.1 L54`), although both PRDs say their jobs are "emitted only by comment-decay-scheduler" (`li-own-comments-fetcher §5.1 L38`; `li-post-comments-fetcher §5.1 L40`); backfill-orchestrator itself says comment-decay-scheduler "opens one `once` fetch for each and closes the series" (`backfill-orchestrator §5.1 L48`; `comment-decay-scheduler §5.1 L66`); fb-backfill aligns the series to `created_time`, so a post older than 30 days "gets no automatic fetch" (`fb-backfill §5.1 L47`, `§14 Q1 L170`).
  - e) Metrics outside the scheduler: tt-client-videos-fetcher takes its own +24 h and +7 d observations from its hourly reads (`tt-client-videos-fetcher §5.1 L51`; `README L185`, decision 8), while comment-decay-scheduler's metrics lane covers "TikTok amber" (`comment-decay-scheduler §5.1 L68`) and the routing of green videos is an open question (`tt-client-videos-fetcher §14 Q5 L180`).
- **At stake:** the rule exists so that one place owns each post's schedule and keeps one job in flight per post (`comment-decay-scheduler §5.1 L62`); a second emitter can run a fetch alongside a series step, and consumers built on "only the scheduler emits" reject or mis-parse the other jobs (reconciliation covering a whole account, refresh with `thread_ids`).
- **Options:** (1) widen the rule: named producers may emit named kinds into another service's queue, listed in a producer table F2 enforces (ig-webhook-receiver reconciliation and targeted reads, yt-text-purger refresh, backfill-orchestrator one-off comment jobs); (2) keep the rule and route the work through comment-decay-scheduler (reconciliation and text refresh become scheduler requests; backfilled posts always get the scheduler's `once` fetch); (3) drop the rule and let each consumer list its producers.
- **Blocks:** F2, C10, C11, IG4, IG5, IG6, YT4, YT5, YT6, YT7, LI2, VLI4, FB3, TT1

#### CF-081

**Metrics refresh jobs: `metrics` with `+24h`, or `refresh_24h` and `refresh_7d`, labels `24h`/`7d`/`client`, and the anchor**

- **Type:** job kind, enum, rule
- **Where:**
  - a) Emitter: "`metrics` jobs at +24 h and +7 d" to fb-reactions-fetcher, ig-account-media-poller, tt-video-stats-refresher and yt-video-details-fetcher (`comment-decay-scheduler §5.1 L68`), with offsets "measured from the post's first-seen time ..., not its creation time" (`§5.1 L60`) and steps written like `"series_step": "+6h"` (`§6.2 L141`); a client refresh is `series_step = refresh:<request_id>` (`§5.1 L70`). `CONVENTIONS L277` lists kind `metrics`; `CONVENTIONS L65` refreshes at +24 h and +7 d.
  - b) fb-reactions-fetcher expects comment-decay-scheduler to send "`kind = refresh_24h` due at `created_time + 24 h` and `kind = refresh_7d` due at `created_time + 7 d`" (`fb-reactions-fetcher §5.1 L41`), `refresh_client` from clients (`§5.1 L47`), refreshes "only for the steps still in the future relative to `created_time`" for backfilled posts (`§5.1 L45`), and asks the scheduler's PRD to confirm (`§14 Q1 L186`).
  - c) yt-video-details-fetcher expects `metrics` with `series_step` `24h` or `7d` "(due at `publishedAt` plus 24 h or 7 d)" or `client`, and "steps already past at first sight are not emitted" (`yt-video-details-fetcher §5.1 L45`; `§13 L204`), while its objective promises "at least three observations" per video (`§2 L13`).
  - d) tt-video-stats-refresher matches (a): `kind = metrics`, `series_step` `+24h` or `+7d` (`tt-video-stats-refresher §5.1 L42`), first sight = the video's first `items.normalized` message (`§5.1 L44`). tt-client-videos-fetcher uses its own first read as first sight (`tt-client-videos-fetcher §5.1 L51`, `§6.3 L119`).
  - e) The observation labels on `item.metrics` (this entry holds the label vocabulary; the message shape is section 1 (topics)'s CF-019, the `raw.items` field CF-006): `refresh_24h`, `refresh_7d`, `refresh_client` (`fb-reactions-fetcher §5.2 L53`, `§6.2 L113`; `yt-video-details-fetcher §5.2 L61`, `§6.2 L143`), with `first_sight` and `ops_force` (`yt-video-details-fetcher §5.2 L61`) and, in extract mode, the envelope's `poll`, `backfill`, `webhook_reconcile` (`fb-reactions-fetcher §3 L19`); against `plus_24h`, `plus_7d` (`tt-video-stats-refresher §6.2 L93`; `tt-client-videos-fetcher §6.2 L115`); and `metrics_observation = refresh_24h` on a Telegram views re-read (`tg-channel-posts-poller §6.2 L128`). No document lists the labels.
- **At stake:** fb-reactions-fetcher dispatches on `kind` and has no branch for `metrics`, so Facebook refreshes are parked or never run; yt-video-details-fetcher's `24h` never equals the scheduler's `+24h`; a "+24 h" observation lands at different post ages depending on the anchor, so trends across platforms are not comparable.
- **Options:** (1) `kind = metrics` with `series_step` `+24h`, `+7d`, `refresh:<request_id>`, anchored on first sight (comment-decay-scheduler, CONVENTIONS kind list); (2) kinds `refresh_24h`, `refresh_7d`, `refresh_client` added to the list, anchored on the platform's creation time (`created_time`, `publishedAt`); (3) `kind = metrics` with bare labels `24h`, `7d`, `client`, anchored on creation time. In each case, one closed list of `item.metrics` labels in F2 (first sight, the two refreshes, client refresh, poll, backfill, ops) named after the chosen steps.
- **Blocks:** F2, C11, FB4, IG3, VTT6, TT1, YT4, VTG3

#### CF-082

**Count refreshes on X, LinkedIn and Telegram: +24 h and +7 d in CONVENTIONS, first sight only in the README, a Tier 1 +24 h views refresh in tg-channel-posts-poller**

- **Type:** rule, job kind, document
- **Where:**
  - a) `CONVENTIONS L65`: metrics "are refreshed at +24 h and +7 d by the source's metrics or details service, or by the next poll where the API returns counts with the post".
  - b) `README L25`: counts are refreshed at +24 h and +7 d by four services; "on X, LinkedIn and Telegram they are recorded at first sight (adding refreshes there is an open question in comment-decay-scheduler)". The same README line names tt-video-stats-refresher for TikTok, while decision 8 has tt-client-videos-fetcher write its own +24 h and +7 d metrics (`README L185`).
  - c) comment-decay-scheduler: "On X, LinkedIn, Telegram and news the counts are recorded at first sight" (`comment-decay-scheduler §5.1 L68`; `§14 Q6 L207`); its write list has no `jobs.tg-channel-posts-poller` (`§6.2 L138`).
  - d) tg-channel-posts-poller: "v1 refreshes only Tier 1 posts, once, at +24 h, on a `metrics` job from comment-decay-scheduler; the +7 d refresh is off" (`tg-channel-posts-poller §5.1 L56`), consumes kind `metrics` (`§6.1 L103`), names comment-decay-scheduler as the source of "views-refresh jobs" (`§4 L36`), labels the re-read `metrics_observation = refresh_24h` (`§6.2 L128`), and asks whether the refresh is worth its cost (`§14 Q5 L195`).
  - e) li-company-posts-poller: "Counts are a snapshot at first sight; whether they are refreshed at +24 h and +7 d is open" (`li-company-posts-poller §5.4 L92`, `§14 Q3 L186`).
- **At stake:** tg-channel-posts-poller's `metrics` path has no producer, so Tier 1 Telegram views are never refreshed; if the scheduler adds the lane it needs a Tier-1-only, +24-h-only rule it does not have; CONVENTIONS promises +24 h and +7 d counts that X and LinkedIn data will not have.
- **Options:** (1) first-sight counts only on X, LinkedIn and Telegram in v1 (README; CONVENTIONS L65 amended; tg-channel-posts-poller drops `metrics`); (2) a Telegram Tier 1 +24 h lane in comment-decay-scheduler, first sight elsewhere; (3) +24 h and +7 d refreshes on all routes as CONVENTIONS says, priced per route (X paid reads, Apify and harvestapi items).
- **Blocks:** C11, VTG3, LI1, VLI3, X1, X3, X4

#### CF-083

**`first_sight` jobs on `jobs.yt-video-details-fetcher`: four producers, four shapes**

- **Type:** shape, job kind
- **Where:**
  - a) Consumer: `post_ref` = one video id, with `due_at` and `series_step` (`yt-video-details-fetcher §6.1 L86`); backfill ids marked "`series_step = backfill`" (`§5.1 L44`); jobs for one id share a slot in a collector buffered per governor priority (`§5.1 L48`); first sight at priority 1 for every tier and keyword rule, 5 for backfill (`§5.1 L50`, `§14 Q1 L215`).
  - b) yt-pubsub-receiver: one id as a string, `due_at`, `"series_step": null` (`yt-pubsub-receiver §6.2 L127`).
  - c) yt-uploads-reconciler: `"post_ref": [<up to 50 ids>]`, `"origin_kind": "reconciliation"`, no `due_at` (`yt-uploads-reconciler §6.2 L133`), "carrying the originating kind so details are fetched at the same priority" (`§5.2 L64`).
  - d) yt-keyword-search: "one `jobs.yt-video-details-fetcher` message with the batch of video ids" per run (`yt-keyword-search §5.2 L59`, `§13 L175`).
  - e) yt-web-search-bridge: `origin = web_bridge`, the rule's `source_id` and "the list of video ids", batches of up to 50 (`yt-web-search-bridge §5.2 L61`, `§6.2 L126`).
- **At stake:** the consumer parses `post_ref` as one id, so array and batch messages fail validation; priority comes from the consumer's table in one PRD and from the originating job in another, so quota-governor gets different priorities for the same call.
- **Options:** (1) one id per job (`post_ref` string, `due_at`, `series_step` for backfill), batching only inside the consumer's collector; (2) a list of up to 50 ids per job with an `origin` field, and the consumer splits it; (3) a list per job plus `series_step` per id, priority fixed by the consumer's table whatever the origin.
- **Blocks:** F2, YT2, YT3, YT4, YT8, YT9

#### CF-084

**X gap and history jobs: `reconciliation` against `gap_backfill`, gap parts for x-full-archive-search, and two producers of `keyword_history`**

- **Type:** job kind, shape, writers
- **Where:**
  - a) Gap jobs on `jobs.x-recent-search`: x-filtered-stream emits "`kind = reconciliation` (backfill jobs come only from backfill-orchestrator)" with `source_id` = the rule's first source, `query`, `source_ids`, `client_ids`, `window_start`, `window_end` and the rule's priority (`x-filtered-stream §5.2 L70`; `§14 Q3 L207` asks to confirm the shape); x-recent-search consumes `reason` = rotation | first_run | gap_backfill | ops_force and lists no query or window fields (`x-recent-search §5.2 L53`; "gap backfill for x-filtered-stream", `§3 L22`).
  - b) Gap parts older than 7 days "go to `jobs.x-full-archive-search`" (`x-filtered-stream §5.2 L70`); x-full-archive-search accepts `backfill` and `keyword_history` from backfill-orchestrator and `replies` from comment-decay-scheduler, and names no gap kind or stream producer (`x-full-archive-search §5.1 L39`).
  - c) `keyword_history`: x-full-archive-search names backfill-orchestrator, on a client request, as its producer (`x-full-archive-search §5.1 L39`); x-recent-search says "a cursor older than that triggers one `keyword_history` job on x-full-archive-search" (`x-recent-search §5.1 L45`, `§13 L188`) and, two paragraphs later, that history jobs are "created by backfill-orchestrator on client request" (`§5.1 L49`); backfill-orchestrator's route table names x-full-archive-search for "X account or keyword rule" (`backfill-orchestrator §5.3 L72`) but never names `keyword_history`.
  - d) `replies` on `jobs.x-full-archive-search` has no producer: CF-078 (d).
- **At stake:** x-recent-search drops or mis-handles every gap job (unknown kind, missing window), so stream outages leave holes the PRD says are filled; gap parts older than 7 days are rejected; a stale cursor either triggers a history read nobody emits or is emitted by a service that does not own backfill.
- **Options:** (1) x-recent-search accepts x-filtered-stream's `reconciliation` job with its window fields; x-full-archive-search adds a gap kind from x-filtered-stream; `keyword_history` emitted only by backfill-orchestrator (x-recent-search asks it); (2) gap jobs use `reason = gap_backfill` with window fields added to x-recent-search's job; old gap parts become `keyword_history` requests to backfill-orchestrator; (3) x-filtered-stream fills its own gaps by calling recent search through the SDK client, and no cross-service gap jobs exist.
- **Blocks:** F2, C10, X1, X4, X5

#### CF-085

**Resolver jobs: one request shape or eight, `rotation` or `refresh` for registered sources, producers that do not emit, and answer kinds no resolver sends**

- **Type:** job kind, shape, writers
- **Where:**
  - a) The round trip: poster-resolver publishes `resolve` to `jobs.<resolver>` "chosen by `platform`" (`poster-resolver §5.2 L56`) with `candidate_key`, `platform`, `platform_id`, `handle`, `hit_url`, `origin`, `"reply_to":"jobs.poster-resolver"`, `sample_posts` (`§5.3 L67`) and waits for `kind: resolved` or `kind: unresolvable` on `jobs.poster-resolver` (`§4 L37`; `§5.3 L70`); with no answer in 15 minutes it re-publishes, and after 5 attempts marks the candidate `unresolvable: timeout` (`§8 L107`). No resolver lists `jobs.poster-resolver` among its writes; each publishes `poster.profiles` itself (`fb-page-resolver §6.2 L99`; `ig-account-resolver §6.2 L102`; `tt-user-resolver §6.2 L86`; `x-user-resolver §6.2 L101`; `li-org-resolver §6.2 L79`; `tg-channel-resolver §6.2 L77`; `yt-channel-resolver §6.2 L103`; `news-site-resolver §6.2 L79`). Who writes `poster.profiles` is section 1 (topics)'s entry CF-012; this entry is the job half.
  - b) Kind of a request, and of a registered source's refresh: `resolve`, `rotation` (the resolver's own loop) and `ops_force` (`fb-page-resolver §5.1 L42`; `x-user-resolver §5.1 L41`; `yt-channel-resolver §5.1 L44`; `ig-account-resolver §5.1 L42`); `resolve` and `refresh` (`news-site-resolver §5.1 L38`); `refresh` named, other requests told apart by `origin` (`li-org-resolver §5.1 L44`); no `kind` field, `origin (discovery|client|ops|refresh)`, with the scheduler's "`refresh` job" (`tg-channel-resolver §5.2 L52`, `§5.1 L44`); "A job per candidate" with no kind (`tt-user-resolver §5.1 L41`).
  - c) Request fields: `job_id`, `kind`, `candidate_key`, `client_ids`, `due_at`, `attempt` (`fb-page-resolver §5.1 L42`; `x-user-resolver §5.1 L41`; `yt-channel-resolver §5.1 L44`, plus `source_id`); `candidate_key`, "the handle", `client_ids` (`ig-account-resolver §5.1 L42`); `{candidate_key, url_or_handle, origin, client_ids, seed_list, kind, attempt}` (`li-org-resolver §5.1 L44`); `{job_id, candidate (username or t.me URL), origin (discovery|client|ops|refresh), client_ids, hit_item_keys, attempt}`, with no `candidate_key` (`tg-channel-resolver §5.2 L52`); "the lookup identifier, the `client_ids` ..., `attempt` and a priority" (`tt-user-resolver §5.1 L41`). None of them reads `reply_to`, `hit_url` or `sample_posts`.
  - d) Producers a resolver names that do not emit: news-site-resolver names "search-hit-router, web-commoncrawl-scanner, web-gdelt-poller, the seed-list flow and the qualifier" (`news-site-resolver §5.1 L38`), but search-hit-router and web-commoncrawl-scanner reach it "through poster-resolver" (`search-hit-router §4 L37`; `web-commoncrawl-scanner §11 L140`), web-gdelt-poller writes no resolver queue (`web-gdelt-poller §6.2 L91`, `L92`, `L113`), and poster-resolver, which does send it `resolve` (`poster-resolver §5.2 L56`), is not named; li-org-resolver expects `kind: refresh` "from qualifier" and origin `seed` "from registry-writer on client onboarding" (`li-org-resolver §5.1 L44`), while the qualifier writes only `registry.decisions`, `decisions`, `review_queue` and n8n cards (`qualifier §6.2 L81`, `L87`) and registry-writer sends manual adds to `jobs.poster-resolver` as `manual_candidate` (`registry-writer §5.2 L61`, writes `§6.2 L91`).
  - e) A producer outside poster-resolver: yt-web-search-bridge publishes "`jobs.yt-channel-resolver` (kind `resolve`, origin `web_bridge`)" itself (`yt-web-search-bridge §5.2 L61`), while yt-channel-resolver lists the bridge among "candidate origins, through poster-resolver" (`yt-channel-resolver §11 L168`); such a job has no `poster_profiles` row behind it.
- **At stake:** F2 cannot define one resolver job type, so poster-resolver's single request shape fails validation on at least four queues (no `candidate`, no `url_or_handle`, no `kind`); as written, every candidate times out on `jobs.poster-resolver` and goes to its DLQ after 5 attempts, and the qualifier-driven LinkedIn and news refreshes never run.
- **Options:** (1) one resolver job schema in F2 for all eight queues (`kind` `resolve` | `rotation` | `ops_force`, `candidate_key`, `platform_id` or handle, `origin`, `client_ids`, `attempt`, `reply_to`), emitted by poster-resolver for candidates and by each resolver's own loop for registered sources; (2) as (1) with `refresh` instead of `rotation`, and the qualifier and the news pollers allowed to emit `refresh`; (3) per-resolver job schemas as written, poster-resolver adapting its request per queue, each PRD's producer list corrected to the services that actually emit.
- **Blocks:** F2, C7, C8, C9, FB1, IG1, VTT3, X2, VLI2, VTG2, YT1, N2, W3, W4, W5, YT9

#### CF-086

**Webhook receivers' inbound buffer: a `push` job on the receiver's own queue, a raw body with no kind, or no buffer at all**

- **Type:** job kind, shape, partition
- **Where:**
  - a) Baseline: job queues hold "work items for pollers, backfills, comment and reply fetches, metrics refreshes. Partitioned by `source_id`" (`CONVENTIONS L28`), each job carrying the fields of `CONVENTIONS L277`.
  - b) ig-webhook-receiver appends "the verified body, headers and `received_at`" to `jobs.ig-webhook-receiver` as "message `kind = push`" before answering Meta (`ig-webhook-receiver §5.2 L55`), says the "job schema gains `kind = push` for this queue" (`§11 L162`), and finds the source only after consuming the message (`§5.2 L56`), so the message has no `source_id` to be partitioned by; the PRD names no partition key.
  - c) fb-client-webhook-receiver makes "Each POST entry ... durable on `jobs.fb-client-webhook-receiver` (partitioned by `source_id`)" (`fb-client-webhook-receiver §5.1 L40`, `§5.2 L55`; "the internal buffer", `§6.2 L133`) and yt-pubsub-receiver produces "the body" to `jobs.yt-pubsub-receiver`, partitioned by `source_id` (`yt-pubsub-receiver §5.1 L38`, `§5.2 L54`); neither names a kind or the job fields.
  - d) The other receivers keep no buffer and write `raw.items` before acknowledging: `tg-bot-channel-receiver §5.2 L62`; `tg-discussion-receiver §5.2 L64`; li-notification-receiver ("There is no job queue", `li-notification-receiver §5.1 L40`, `§5.2 L57`).
- **At stake:** the SDK job wrapper expects `job_id`, `due_at` and `attempt` and applies the 5-attempt DLQ rule, so a raw webhook body on a `jobs.` queue is either rejected or retried and dead-lettered as if it were a job; F2 has no message type for these queues.
- **Options:** (1) a `push` job kind in F2 (body, headers, `received_at`, optional `source_id`), used by every receiver that buffers; (2) a separate inbound topic per receiver outside the job schema, with its own retry and DLQ rule; (3) no buffer: every receiver writes `raw.items` before acknowledging, as the Telegram and LinkedIn receivers do.
- **Blocks:** F2, F4, IG4, FB7, YT2

#### CF-087

**Job queue partition keys other than `source_id`: candidates, keywords, keyword sets, hosts, and jobs with no source at all**

- **Type:** partition, shape
- **Where:**
  - a) Rule: per-source job queues are "Partitioned by `source_id` so one source is never worked twice at once" (`CONVENTIONS L28`), and every job carries `source_id` (`CONVENTIONS L277`). Topic partition keys are section 1 (topics)'s entry CF-003; this entry is the job-queue half.
  - b) Resolver queues by candidate, then by `source_id` once registered: "partitioned by `candidate_key` (a candidate has no `source_id` yet; a registered Page uses its `source_id`)" (`fb-page-resolver §5.1 L42`; the same in `x-user-resolver §5.1 L41` and `yt-channel-resolver §5.1 L44`); by `candidate_key` only (`ig-account-resolver §5.1 L42`; `tt-user-resolver §5.1 L41`; `li-org-resolver §5.1 L44`); "by `source_id` (or by handle for candidates without a row)" (`tg-channel-resolver §5.1 L45`); `jobs.news-robots-checker` "by host for a candidate not yet in the registry" (`news-robots-checker §5.1 L41`).
  - c) Other keys: `jobs.fb-page-search` "partitioned by `keyword_id` so one keyword is never searched twice at once" (`fb-page-search §5.1 L40`); `jobs.tg-message-search` jobs carry `set_id` and `keyword_ids` and no `source_id` (`tg-message-search §5.2 L51`); a multi-source X rule's gap job takes "`source_id` = the rule's first source" (`x-filtered-stream §5.2 L70`).
  - d) Jobs with no source, and no partition key stated: `rematch` with `client_id`, `keyword_ids` and a window (`keyword-matcher §5.3 L81`); `replay` with "a date range and an optional platform filter" (`normalize-item §5.1 L45`); `rerun` with a date range and a platform filter (`analysis-sentiment §5.1 L51`); `retention_sweep` with `run_id`, `cutoff`, `next_sweep_at` (`yt-text-purger §5.1 L44`); the answers and manual candidates on `jobs.poster-resolver` (`poster-resolver §6.1 L82`).
- **At stake:** F2's job type and the SDK producer key every job on `source_id`, so the jobs in (c) and (d) either cannot be produced through the common client or get a made-up key; in (b) a candidate's `resolve` job and the same account's later `rotation` job sit on different partitions, so the "never worked twice at once" guarantee does not hold across registration.
- **Options:** (1) a per-queue partition key declared in F2 (`source_id` by default; `candidate_key`, `keyword_id`, `set_id`, host as listed), and `source_id` optional on queues that declare another key; (2) `source_id` required on every job, with keyword sets, candidates and ops work given a row or a synthetic id to key on; (3) a generic `partition_key` field on every job, set by the producer, with `source_id` carried as data where it exists.
- **Blocks:** F2, F4, F5, F6, FB1, IG1, VTT3, X2, VLI2, VTG2, YT1, N1, N2, FB6, VTG1, X4, C4, C5, C8, A1, A2, A3, A4, YT7

#### CF-088

**Backfill jobs (README decision 4): the orchestrator's route table against the services that expect its job, services that backfill themselves, and the job's fields**

- **Type:** job kind, rule, shape, document
- **Where:**
  - a) Rule and proposal: "backfill jobs only by backfill-orchestrator" (`CONVENTIONS L278`); README decision 4 makes backfill-orchestrator "the single writer of `backfill_status`", says "A failed or slow backfill ends `capped`" and names fb-group-posts-poller as the target for groups (`README L181`). Who writes `backfill_status` is section 2 (tables)'s entry CF-030; this entry is the job side.
  - b) Consumers that say backfill-orchestrator sends them a `backfill` job, with no row in its route table (`backfill-orchestrator §5.3 L66` to `L79`): fb-keyword-search (`fb-keyword-search §3 L19`, `§5.1 L48`), ig-keyword-search (`ig-keyword-search §5.1 L51`, `§5.2 L57`), ig-mentions-fetcher (`ig-mentions-fetcher §5.1 L49`, `§5.2 L55`), li-post-search (`li-post-search §5.1 L48`), tt-client-videos-fetcher (`tt-client-videos-fetcher §5.1 L49`, `§5.2 L55`) and ig-hashtag-search (`ig-hashtag-search §5.1 L45`, `L59`). The table's only rule row is "X account or keyword rule" (`backfill-orchestrator §5.3 L72`); every other "Hashtag or keyword rule without a history route; web" gets no job and "`done` at once, note `no_history_route`" (`backfill-orchestrator §5.3 L79`), without a list of which rules have a history route.
  - c) Services that backfill on their own first job, with no orchestrator job: "Backfill on add: the first job pages the feed until the oldest video ... is older than 90 days" (`tt-hashtag-feed-poller §5.1 L48`); "one deep search that pages until ..." (`tt-keyword-search §5.1 L44`); "A 90-day first run per new keyword set (the search backfill)" from the service's own scheduler (`tg-message-search §3 L21`, `§5.1 L44`, `§13 L144`).
  - d) Route rows whose consumer does not take the job: news sites go to "news-feed-poller and news-sitemap-poller (whichever the site has)" (`backfill-orchestrator §5.3 L78`), and news-feed-poller accepts no `backfill` (CF-079 a), while three news PRDs name news-sitemap-poller, or web-commoncrawl-scanner without a sitemap, as the route (`news-feed-poller §5.1 L48`; `news-site-resolver §5.1 L41`; `news-sitemap-poller §3 L29`) and web-commoncrawl-scanner has no backfill role (`web-commoncrawl-scanner §5.1 L44`); Telegram own channels get "none" and "`done` at once" (`backfill-orchestrator §5.3 L76`) while the Telegram receivers set `capped` (CF-030 e).
  - e) The job's fields: `job_id`, `source_id`, `kind: backfill`, `due_at`, `attempt`, `run_id`, `cap` (`max_age_days`, `max_items`), `route`, `vendor` (`backfill-orchestrator §6.2 L106`); fb-backfill reads `window_start = added_at − 90 days`, `window_end = added_at`, `reason = add`, and on demand `reason = ops | client` with an explicit window (`fb-backfill §5.1 L41`); the other consumers read `source_id`, `kind`, `attempt` (for example `ig-keyword-search §5.2 L57`) and apply their own 90-day cap. fb-backfill is itself split on the window: "between `since = now − 90 days` and `until = now`" (`fb-backfill §3 L20`) against `window_start = added_at − 90 days` (`§5.1 L41`).
  - f) The window: "the last 90 days (or the route's cap, whichever is smaller)" (`CONVENTIONS L53`) against "last 90 days by default, longer on client request" for X accounts (`x-full-archive-search §2 L13`, `§3 L19`).
- **At stake:** as written, keyword rules, hashtags, Instagram mentions and client TikTok accounts never get the backfill their PRDs promise, or get it only on a path nothing triggers; the orchestrator marks TikTok rules `done` while the searches are still paging; fb-backfill finds no window or `reason` in the orchestrator's job.
- **Options:** (1) the orchestrator owns every backfill: a route-table row per source type that has history (keyword rules, hashtags, mentions, client TikTok accounts included), the TikTok searches wait for its job, and one job schema (`run_id`, `cap`, optional window) every consumer reads; (2) the orchestrator only tracks status: each poller or search backfills on its first job and reports through the completion channel (CF-089), and the backfill clause of `CONVENTIONS L278` is dropped; (3) a split written into the route table: orchestrator jobs for accounts, pages, groups and channels; self-backfill on the first run for keyword rules and hashtags, reported to the orchestrator.
- **Blocks:** F2, F5, C10, FB3, VFB1, VFB2, IG2, VIG1, IG5, VLI1, TT1, VTT1, VTT2, VTG1, N3, N4, TG1, TG2

#### CF-089

**How a finished job reports back (README decision 1): `jobs.completed` from the SDK wrapper, from the service itself, or another channel; report fields and status values**

- **Type:** names, shape, enum, writers, document
- **Where:**
  - a) Proposal: "**Completion topic `jobs.completed`** (schema `jobs.completed/v1`), written by the listening-sdk job wrapper after every job with a report (`new_count`, `seen_count`, `pages`, `cost_units`, `reply_candidates`); comment-decay-scheduler and backfill-orchestrator consume it" (`README L178`, decision 1); "CONVENTIONS lists no completion topic", alternative "poll `service_runs`" (`comment-decay-scheduler §14 Q1 L202`); consumers `comment-decay-scheduler §5.1 L42` and `backfill-orchestrator §5.2 L59`. CONVENTIONS has each comment fetch report "`new_count`, `seen_count`, `pages`, `cost_units`" (`CONVENTIONS L62`) but names no topic, table or job field that carries it.
  - b) Written by the service, not the wrapper: x-full-archive-search lists `jobs.completed` among its own writes, for replies "with `post_ref`, `series_step` and the window's `end_time`" (`x-full-archive-search §6.2 L128`), while its step 9 says "The listening-sdk wrapper writes `jobs.completed/v1`" (`§5.2 L57`); "Publish to `jobs.completed`" (`yt-uploads-reconciler §5.2 L66`); "write one completion per job to `jobs.completed`" (`yt-video-details-fetcher §5.2 L63`).
  - c) Other channels and names for the report: "the fetch report" (`fb-post-comments-fetcher §3 L21`; `§14 Q6 L192` asks whether it is "sent to comment-decay-scheduler as a job-result record"); "the job result" recorded "through the control-plane client" (`ig-own-comments-fetcher §5.2 L64`; `ig-comments-fetcher §5.2 L63`); "the completion message" (`tt-video-comments-fetcher §5.2 L62`; `tt-video-stats-refresher §6.2 L112`); "the result row ... to `service_runs`" (`news-comments-fetcher §5.2 L59`, `§6.3 L124`; also `li-post-search §5.2 L61`, which writes `new_count`, `seen_count`, `pages`, `cost_units` to `service_runs`); "a backfill report to backfill-orchestrator (`coverage_days`, `urls_emitted`)" (`news-sitemap-poller §6.2 L127`).
  - d) Reports read from a service whose PRD never writes them: x-full-archive-search estimates cost from "the rule's daily `new_count` in x-recent-search's last 7 days of reports" (`x-full-archive-search §5.2 L52`) and x-filtered-stream closes a gap "when `jobs.completed` arrives for all its jobs" (`x-filtered-stream §5.2 L71`); x-recent-search never mentions `jobs.completed` (writes: `x-recent-search §6.2 L98`).
  - e) Report fields beyond the five: `oldest_item_at`, `capped`, `capped_reason`, and no `seen_count` (`backfill-orchestrator §5.4 L92`, against `comment-decay-scheduler §5.4 L127`); `stored_before`, `complete` (`fb-post-comments-fetcher §13 L181`); `reply_threads` (`fb-group-comments-fetcher §5.1 L53`); incomplete reply threads (`ig-own-comments-fetcher §5.2 L64`); `newest_comment_at` (`li-own-comments-fetcher §5.2 L64`); comments above the reply threshold (`tt-video-comments-fetcher §5.2 L62`); `stored_count` (`yt-replies-fetcher §5.2 L57`); `thread_id` (`news-comments-fetcher §5.2 L59`); `paid_user_reads`, `capped`, `window_partial` and no `reply_candidates` (`x-replies-fetcher §5.2 L62`); other names, `items_fetched` and `items_new` (`ig-hashtag-search §5.2 L70`). One field, two meanings: `seen_count` is stored replies seen again, "edits included" (`x-replies-fetcher §5.2 L62`), but "posts with `paid = false`" (`x-user-timeline-poller §5.2 L61`).
  - f) Status values: `ok` in both examples (`comment-decay-scheduler §5.4 L127`; `backfill-orchestrator §5.4 L92`); `done`, `skipped_flag_off`, `video_gone` (`tt-video-stats-refresher §6.2 L112`); `skipped` (`ig-comments-fetcher §5.2 L57`); `skipped_flag_off` (`fb-group-comments-fetcher §5.2 L59`; `tg-message-search §5.1 L47`); `skipped_flag_off`, `skipped_government` (`li-post-comments-fetcher §5.1 L52`); `quota_denied` (`yt-comments-fetcher §5.2 L53`; `x-replies-fetcher §5.2 L55`); `not_root`, `outside_window`, `not_permitted` (`x-replies-fetcher §5.2 L53`, `L54`); `comments_disabled` and `video_not_found`, each ending the series (`yt-comments-fetcher §13 L193`, `§8 L156`). No document lists the statuses or says which of them end a series.
- **At stake:** comment-decay-scheduler and backfill-orchestrator advance only on a completion; a fetcher that reports through `service_runs`, a control-plane record or an unnamed "message" never advances its series or closes its backfill, and a status the consumer does not know leaves the post `in_flight`.
- **Options:** (1) README decision 1 (`jobs.completed/v1` from the SDK wrapper with the five-field report), extended with optional route-specific report fields and one closed status list in F2, the wrapper as the only writer; (2) as (1), and services may also write it themselves where the report needs data the wrapper lacks (x-full-archive-search, yt-uploads-reconciler, yt-video-details-fetcher); (3) no topic: a result row in `service_runs` (or a job-results table) that the two consumers poll.
- **Blocks:** F2, F4, F5, F6, C10, C11, FB3, FB5, VFB3, IG6, VIG2, VTT5, VTT6, X1, X4, X5, X6, LI2, VLI4, YT3, YT4, YT5, YT6, N4, N8

#### CF-090

**What a job does with a governor `deny` or `wait-until`: requeue with `attempt + 1`, park, keep `next_poll_at`, finish `quota_denied`, end `capped`, or drop after 24 h**

- **Type:** rule, enum
- **Where:**
  - a) Baseline: the governor "returns allow / wait-until / deny" (`CONVENTIONS L85`) with no rule for the caller; quota-governor denies with `flag_off`, or `period_full` when "period (month, cycle, cap) would overflow", or `priority_gate` on monthly tags (`quota-governor §5.3 L67`, `L70`, `L71`), so a deny lasts until the period resets. README decision 2: at `exhausted` "The +24 h comment step is held, never cancelled" (`README L179`; `comment-decay-scheduler §13 L194`). CONVENTIONS' retry rule counts attempts to the DLQ for 429s (`CONVENTIONS L100`).
  - b) `deny` requeues with `attempt + 1`: `tt-hashtag-feed-poller §5.2 L56`; `tt-keyword-search §5.2 L50`; `tt-profile-videos-poller §5.2 L59`; `tt-user-resolver §5.2 L54`; `tt-video-comments-fetcher §5.2 L58`; fb-backfill on "a quota deny mid-way" stops and requeues with `attempt + 1` (`fb-backfill §5.2 L55`).
  - c) `deny` keeps `next_poll_at`: `tt-client-videos-fetcher §5.2 L57`; for the month, "rules keep `next_poll_at`" (`web-search-mojeek §7 L118`; `web-search-perplexity §8 L130`).
  - d) `deny` finishes the job with status `quota_denied`, no call: `yt-comments-fetcher §5.2 L53`; `x-replies-fetcher §5.2 L55`.
  - e) `deny` makes the job wait: "the job waits" (`news-comments-fetcher §8 L143`); "makes the job wait, not fail" (`tg-message-search §13 L147`); a denied step "waits; one still unserved 24 hours after `due_at` is dropped" (`li-post-comments-fetcher §5.1 L52`, `§13 L188`), which for a +24 h step is what README decision 2 rules out.
  - f) `deny` ends the work: x-full-archive-search ends the job `capped` at once (`x-full-archive-search §5.1 L43`); yt-text-purger deletes the text it could not refresh (`yt-text-purger §5.3 L92`, `§8 L193`).
  - g) `wait-until`: "sleeps" in the worker (`tt-hashtag-feed-poller §5.2 L56`; `tt-keyword-search §5.2 L50`) or "requeues for that time" (`tt-profile-videos-poller §5.2 L59`; `yt-comments-fetcher §5.2 L53`; `x-replies-fetcher §5.2 L55`).
- **At stake:** with requeue-and-increment, a budget that is full for the month dead-letters every job of the tag within five tries and fires DLQ alerts; a sleeping worker holds its partition and delays other sources; the scheduler and the orchestrator cannot tell a budget skip from a failure unless the outcome has an agreed status (CF-089).
- **Options:** (1) one SDK rule: `wait-until` requeues for that time without counting an attempt, and `deny` ends the job with status `quota_denied` (no attempt, no DLQ), leaving the scheduler or poller to try again at its next due time; (2) `deny` parks the job until the governor's period or mode changes (held, as README decision 2 says for the +24 h step), and only provider errors count attempts; (3) per-route rules as written, each recorded in its PRD, with quota outcomes excluded from the 5-attempt DLQ count.
- **Blocks:** F4, F5, F6, C1, C10, C11, TT1, VTT1, VTT2, VTT3, VTT4, VTT5, FB3, X5, X6, YT5, YT7, VLI4, VTG1, W1, W2, N8

#### CF-091

**When a job reaches its DLQ: after the fifth attempt or on the sixth failure, and Facebook error 80001 as a retry or a deferred poll**

- **Type:** rule
- **Where:**
  - a) Rule: "after 5 attempts the job goes to `dlq.<service>` and an alert fires" (`CONVENTIONS L100`); most acceptance criteria repeat it ("after 5 attempts the job is in `dlq.…`", for example `fb-page-feed-poller §13 L182`, `x-recent-search §13 L186`, `yt-comments-fetcher §13 L198`).
  - b) Five PRDs test a sixth failure instead, while their own section 8 says "after 5 attempts": "the sixth failure lands in `dlq.tg-channel-posts-poller`" (`tg-channel-posts-poller §13 L186` against `§8 L144`); `tt-hashtag-feed-poller §13 L162` against `§8 L122`; `tt-keyword-search §13 L152` against `§8 L116`; `web-search-mojeek §13 L162` against `§8 L124`; `web-search-perplexity §13 L163` against `§8 L125`.
  - c) Error 80001 ("too many calls to this Page"): "per-Page backoff and the next poll deferred by one interval" (`fb-page-feed-poller §7 L138`) against "exponential backoff with jitter from 30 s to 15 min, requeue with `attempt + 1`; after 5 attempts the job goes to `dlq.fb-page-feed-poller`" (`§8 L145`, `§13 L182`).
- **At stake:** F4's job wrapper implements one count; five services' acceptance tests then fail against it, and a Page that answers 80001 is either skipped for one interval or dead-lettered with an alert.
- **Options:** (1) the DLQ on the fifth failed attempt (attempts 1 to 5), the five acceptance criteria corrected; (2) five retries after the first attempt (the sixth failure), CONVENTIONS L100 reworded; and for 80001: (3) treat it as a rate limit under the retry rule, or (4) as a per-Page deferral of one interval with no attempt counted.
- **Blocks:** F4, F6, FB2, VTG3, VTT1, VTT2, W1, W2

#### CF-092

**News hosts' 4xx: does a 429 or a feed, sitemap or homepage 404/410 send news-robots-checker a `recheck`, and does the host gate double its spacing after a 429**

- **Type:** rule
- **Where:**
  - a) news-robots-checker: "Any news service that receives a 4xx from a host (401, 402, 403, 429, 451, and a 404 or 410 on a feed or sitemap URL) sends `recheck` and stops its batch for that host. The only exception is a 404 or 410 on an individual article URL" (`news-robots-checker §5.1 L47`).
  - b) 429 backs off and retries instead (no recheck): `news-feed-poller §8 L131`; `news-article-extractor §5.2 L54`, `§8 L140`; `news-sitemap-poller §8 L143`; `news-homepage-differ §8 L134`. Inside news-feed-poller, section 8 backs off on 429 while its acceptance criterion says "Any 4xx from a host produces one `recheck` job" (`news-feed-poller §13 L170`).
  - c) A sitemap or homepage 404/410 sends news-site-resolver a `refresh` and no recheck: "Any 4xx other than 404 and 410" (`news-sitemap-poller §8 L144`, `§13 L183`; `news-homepage-differ §8 L135`, `§13 L173`). news-feed-poller sends a `refresh` for a feed 404/410 and, by `§13 L170` ("Any 4xx from a host produces one `recheck` job"), also a `recheck`; its `§8 L132` is ambiguous. news-robots-checker exempts only article URLs.
  - d) The host gate (README decision 6, `README L183`): five PRDs list "Lane-wide rules, identical in every news service" (`news-article-extractor §5.3 L62`), but only news-article-extractor adds "after a 429 or 503 the spacing for that host doubles" (`news-article-extractor §5.3 L65`); the others stop at 2 to 5 seconds or `Crawl-delay` (`news-feed-poller §5.3 L66`; `news-sitemap-poller §5.3 L69`; `news-homepage-differ §5.3 L67`; `news-robots-checker §5.3 L68`).
- **At stake:** the policy of a host that starts rate-limiting or moves its feed is re-checked by one service and not by the others, so `crawl_policies` can stay stale while the pollers keep fetching; the SDK host gate has one implementation, so either four PRDs or one is wrong about the doubling.
- **Options:** (1) news-robots-checker's rule: every 4xx including 429, and feed, sitemap and homepage 404/410, sends one `recheck` (coalesced per host), besides any back-off or `refresh`; (2) the pollers' rule: 429 only backs off, a feed, sitemap or homepage 404/410 only sends `refresh`, and news-robots-checker's list is narrowed; (3) either, plus the doubling after 429 or 503 written into the SDK host gate for all news services, or removed from news-article-extractor.
- **Blocks:** F4, F5, N1, N2, N3, N4, N5, N6

#### CF-093

**`recompute` jobs on `jobs.aggregator`: bucket lists with a `done` reply from deletion-propagator, a date-range ops job in aggregator**

- **Type:** job kind, shape
- **Where:**
  - a) deletion-propagator: "collect the distinct (`source_id`, hour) buckets and keyword ids of the removed items and send `recompute` jobs to `jobs.aggregator`; wait for `done`" (`deletion-propagator §5.3 L70`), a step of its state machine (`recomputed`, `§5.3 L76`).
  - b) aggregator: "a job on `jobs.aggregator` with `kind = recompute` (date range, optional client) is the ops entry point", while "a message on `deletions` ... triggers a reconciliation within 5 minutes" (`aggregator §5.1 L37`); "Hours older than the reconciliation window: only an ops `recompute` job changes them" (`aggregator §8 L111`). No reply or `done` is named. See AU-082 in `CONFLICTS-ASSUMPTIONS.md`; the kind itself is in CF-077 (c).
- **At stake:** aggregator rejects or misreads bucket-list jobs, and deletion-propagator waits for a `done` that never comes, so every deletion stalls before `recomputed` and the deletion deadline is missed; deletions older than 31 days leave old aggregates unchanged unless the job is understood.
- **Options:** (1) aggregator accepts bucket-list `recompute` jobs (source and hour list, keyword ids) and reports completion on the completion channel (CF-089); (2) deletion-propagator sends date-range `recompute` jobs in aggregator's shape and waits on the completion channel; (3) no jobs from deletion-propagator: aggregator's `deletions` reconciliation covers any age, and deletion-propagator verifies the affected hours itself before `recomputed`.
- **Blocks:** F2, C13, C15

### Values and enumerations

#### CF-094

**A platform 401 or 403 (README decision 5): `degraded` in CONVENTIONS and most fetchers, `blocked` in the README and the canary; and what carries the state (token, key, route, page or source)**

- **Type:** enum, rule, document
- **Where:**
  - a) CONVENTIONS: "HTTP 401 and 403: the service marks the token or route `degraded`, stops the batch, and alerts" (`CONVENTIONS L101`); the only health state is the per-source column `health` (ok, degraded, fallback, blocked) (`CONVENTIONS L36`), no rule sets `blocked`, and no token or route state has a column.
  - b) README decision 5: "A 401 or 403 from a platform means `blocked`, with no automatic fallback and an n8n approval card; a vendor key or plan error is `degraded` and may fall back. A green source watched by a government client is never moved to an amber fallback (`scope = non_government`)" (`README L182`); source-health-canary applies it per route: "any to blocked | the platform returns 401 or 403 on every active target and every token in use" (`source-health-canary §5.3 L72`, `§8 L119`, `§13 L151`), vendor 401/402/403 to degraded (`§5.3 L70`), fallback only with "no government client on the source" (`§5.3 L71`).
  - c) Fetchers that mark a platform 401/403 `degraded` (the token, key or route): "a 401 marks the token `degraded`" (`x-recent-search §13 L186`; `ig-own-comments-fetcher §13 L187`); "a 401 marks the key `degraded`" (`yt-channel-resolver §13 L192`); "any other 403 marks it `degraded`" (`yt-video-details-fetcher §13 L209`); the same in most section 8s.
  - d) Fetchers that set `health = blocked` on the source, each on its own condition: a 401 after one failed token refresh, and a 403 (`tt-client-videos-fetcher §8 L130`, `L131`, `§13 L165`); when "the same token succeeded on another page in the last 15 minutes" (`li-client-posts-poller §8 L142`); when no client in `client_ids` has a healthy token (`ig-account-media-poller §8 L141`); a revoked token (`ig-mentions-fetcher §8 L143`); "a 403 on one page blocks only that page; a 401 degrades the token" (`li-own-comments-fetcher §13 L182`); "HTTP 403 on one chat means the bot was removed from it: that channel is `blocked`, the token is fine" (`tg-bot-channel-receiver §8 L150`; the same for a group, `tg-discussion-receiver §8 L153`).
  - e) Fallback for a green client-owned source: "No amber fallback is ever set here: the vendor is not a fallback for a green route" (`tt-client-videos-fetcher §8 L132`), for any client, while CONVENTIONS sets `fallback_on` "where an amber or alternate route exists and the flag is on" (`CONVENTIONS L102`) and README decision 5 excludes only government clients (`README L182`).
  - f) Neither `degraded` nor `blocked`: a Posts API 403 is "not a route failure but a missing grant; n8n card to the client" (`li-org-resolver §8 L122`).
- **At stake:** a revoked client token either degrades the source (and lets the canary try a fallback route) or blocks it with an approval card, depending on which code runs first; the fallback a government client must never get is guarded only where `scope` is known; token-level and route-level "degraded" have nowhere to be stored, so each service invents a place (where a token mark is kept is section 2 (tables)'s entry CF-057; who writes `sources.health` is CF-032).
- **Options:** (1) README decision 5: platform 401/403 = `blocked` (no fallback, approval card), vendor key or plan error = `degraded`, with CONVENTIONS L101 amended and the fetchers' section 8s aligned; (2) `CONVENTIONS L101` as written (a fetcher marks the token or route `degraded`), plus a rule CONVENTIONS lacks: only the canary, from route-wide evidence, sets `blocked`; (3) two levels: per-token or per-key state (in `vendor_keys` or a token table) set by fetchers, and per-source `health` (`blocked` for a lost grant on one source) set by one writer.
- **Blocks:** F3, F4, F5, C7, C12, and every green fetcher (named here: TT1, LI1, LI2, IG3, IG5, IG6, X1, X2, YT1, YT3, YT4, TG1, TG2, VLI2)

#### CF-095

**`tier`: numbers or words, and what it means on keyword rules, hashtags and news sites, whose cadences are not the reach tiers'**

- **Type:** enum, types, rule, document
- **Where:**
  - a) Values: `tier` (1, 2, 3, push, dormant, retired) (`CONVENTIONS L36`); examples carry numbers (`"tier":2` in `qualifier §6.2 L84` and `registry-writer §6.2 L95`; `previous: {"tier": 3}` in `registry-writer §6.2 L98`; `"proposed_tier": 1` in `news-site-resolver §6.2 L94`), while registry-writer's SQL compares `sources.tier = 'retired'` and calls `least_tier(...)` (`registry-writer §5.3 L72`).
  - b) Tier 1 and the priority list: "Tier 1 (100,000 or more followers, or on a client's priority list)" (`CONVENTIONS L45`; `README L22`) against "Tier by reach (1: 100k+, 2: 10k to 99,999, 3: below 10k; push for client-owned)" in qualifier rule 6 (`CONVENTIONS L247`); registry-writer assumes a client `tier_override` may place a source in tier 1 (`registry-writer §14 Q3 L160`).
  - c) Keyword rules: "`tier = 1` means priority (a client's priority list) and runs every 12 hours; `tier = 2` or `3` means the standard run every 24 hours. Dormant and retired do not apply" (`web-search-perplexity §5.1 L41`; `web-search-mojeek §5.1 L42`); "Every active rule, priority or standard, runs every hour" (`web-gdelt-poller §5.1 L41`); on X "tier means priority: tier 1 ... every 15 minutes; tier 2, tier 3 and dormant rules every 60 minutes" (`x-recent-search §5.1 L41`); on YouTube "`tier = 1` means API search, `tier = 2` or `3` means the web bridge" (`yt-keyword-search §5.1 L46`). Hashtags: "tier is set by the client list and observed volume" (`ig-hashtag-search §5.1 L47`) against "the client's priority setting in place of followers" (`CONVENTIONS L276`).
  - d) News sites: tier proposed from publishing rate, "1 (hot) if on a client priority list or publishing above the hot threshold ...; 2 if daily; 3 if less often" (`news-site-resolver §5.2 L53`); tier 1 every 5 to 15 minutes, tiers 2 and 3 every 60 minutes (`news-feed-poller §5.1 L42`); "every 60 minutes for every tier" (`news-sitemap-poller §5.1 L43`; `news-homepage-differ §5.1 L43`). Accounts and pages read at one cadence whatever the tier: amber LinkedIn company pages "every 24 hours, whatever its tier" (`li-company-posts-poller §5.1 L43`); every connected Instagram account "every 60 minutes" (`ig-mentions-fetcher §2 L13`).
  - e) The README's own lists: the pollers are "re-checked on its tier: tier 1 ... every 60 minutes, tier 2 every 6 hours, tier 3 every 24 hours" (`README L22`), while its index gives li-client-posts-poller 30 to 60 minutes, li-company-posts-poller daily, news-feed-poller 5 to 15 minutes or hourly, news-sitemap-poller and news-homepage-differ hourly, and yt-uploads-reconciler daily (`README L96`, `L97`, `L133`, `L134`, `L135`, `L120`).
- **At stake:** F3 must type the column (a smallint cannot hold `push`, a text column breaks `least_tier` ordering and the numeric examples); shared code that maps tier to an interval (the SDK scheduler, quota-governor's priorities, the canary) gives keyword rules and news sites the reach cadences their PRDs replace.
- **Options:** (1) one text enum (`1`, `2`, `3`, `push`, `dormant`, `retired`) with an ordering function, and a cadence table per source type (reach sources, keyword rules, news sites) written into CONVENTIONS; (2) a numeric reach tier plus a separate state column for `push`, `dormant`, `retired`, and a separate `priority` flag for keyword rules and news sites; (3) the reach tiers only for accounts, pages and channels, with keyword rules and news sites given their own cadence field and no `tier`.
- **Blocks:** F3, F5, C1, C7, C9, W1, W2, W4, N2, N3, N4, N5, X1, YT8, YT9, IG2, IG5, VLI3

#### CF-096

**`tier = push` (README decision 8): "no polling and one reconciliation a day" for client-owned properties, against hourly TikTok reads, Telegram health checks, LinkedIn polling, every YouTube channel and X coverage kept beside the tier**

- **Type:** enum, rule, document
- **Where:**
  - a) Definition: "Push (client-owned properties with webhooks, PubSubHubbub or a bot): no polling for new posts; one reconciliation poll a day to catch missed pushes" (`CONVENTIONS L48`), and "push for client-owned" in qualifier rule 6 (`CONVENTIONS L247`); pushed sources "are reconciled once a day by their poller" (`README L23`); decision 8: "client-authorised accounts are `tier = push`" (`README L185`), while the index has tt-client-videos-fetcher read them "hourly" (`README L73`). Facebook and Instagram follow the definition (`fb-client-webhook-receiver §5.1 L42`; `ig-account-media-poller §5.1 L44`).
  - b) TikTok: tt-client-videos-fetcher reads "Every authorised account every 60 minutes", and "The registry marks these accounts `tier = push`, so tt-profile-videos-poller makes only its one reconciliation poll a day for them" (`tt-client-videos-fetcher §5.1 L43`): the daily reconciliation of a green client account comes from the amber poller (see AU-091 in `CONFLICTS-ASSUMPTIONS.md`).
  - c) Telegram bot channels, "a client's own channels and cooperating channels whose owners agreed to add the bot" (`tg-bot-channel-receiver §1 L9`): "`tier = push`, tiered by nothing: there is nothing to poll", the daily check being a `reconciliation` health job on the receiver's own queue (`tg-bot-channel-receiver §5.1 L44`); the Bot API has "no history method" (`CONVENTIONS L196`) the addendum's comment profile for own channels (tg-discussion-receiver) is "push (live), daily health check" (`CONVENTIONS L268`), and no CONVENTIONS line gives the posts' reconciliation for bot channels, against README L23's "by their poller" (the only Telegram poller is amber).
  - d) LinkedIn client pages: polled every 30 or 60 minutes; "The generic push tier does not apply either" (`li-client-posts-poller §5.1 L42`), while li-notification-receiver calls itself "the push tier of the rotation policy applied to comments and reactions" (`li-notification-receiver §5.1 L40`); neither says which `tier` value the row holds.
  - e) YouTube: "Channels sit in the push tier because yt-pubsub-receiver covers them", with the reach tier kept as "the secondary sort key and the quota priority" (`yt-uploads-reconciler §5.1 L45`); "A channel with a verified lease sits in the push tier, client-owned or not", dormant channels reconciled weekly (`yt-pubsub-receiver §5.1 L40`) against "every 24 hours, dormant ones included" (`yt-uploads-reconciler §5.1 L45`; AU-100 in `CONFLICTS-ASSUMPTIONS.md`), although `tier` has room for one value.
  - f) X: "A covered account is in the push tier: no polling for new posts, one reconciliation poll a day ..., while `sources.tier` keeps the reach tier" (`x-filtered-stream §5.1 L42`; `x-user-timeline-poller §5.1 L42`): push as a coverage state beside the tier, not a tier value.
- **At stake:** a scheduler that reads `push` as "one reconciliation a day" polls client TikTok accounts daily instead of hourly, or routes a green account's reconciliation through an amber vendor; YouTube channels in `push` lose the reach tier quota-governor prioritises on, because the column holds one value.
- **Options:** (1) `push` means "covered by a push channel" for any source, each poller's PRD stating its cadence, and the reach tier kept in a separate column for priority; (2) `push` only for client-owned properties whose new posts arrive by push (Facebook, Instagram, Telegram bot channels, client YouTube channels); client TikTok accounts and LinkedIn client pages keep a reach or client tier and their own cadence, and third-party YouTube channels keep their reach tier with a daily reconciliation rule; (3) no `push` tier: a separate push-coverage flag on the source, with `tier` used for cadence and priority only.
- **Blocks:** F3, F5, C1, C7, C9, TT1, VTT4, TG1, TG2, LI1, LI3, YT2, YT3, FB2, FB7, IG3, IG4, X3, X4

#### CF-097

**Vendor names: flag values, `sources.vendor` values and envelope values spelled three ways, search engines in `vendor` on green records, a source row's vendor differing from the vendor that reads its posts, and Actor publishers outside the cleared list**

- **Type:** enum, names, document
- **Where:**
  - a) Telegram Actors: `sources.vendor` values `apify_tugelbay`, `apify_sovereigntaylor` (`CONVENTIONS L36`); flag values "`TG_POSTS_ACTOR` off | tugelbay | sovereigntaylor" (`CONVENTIONS L280`); the poller starts "the Actor named by `TG_POSTS_ACTOR` (`tugelbay/telegram-posts-scraper` or `sovereigntaylor/telegram-scraper`)" (`tg-channel-posts-poller §5.3 L70`) and writes `"vendor": "apify_tugelbay"` (`§6.2 L112`).
  - b) Green records with a vendor: the web engines write `vendor = gdelt`, `mojeek` or `perplexity` with `route = green` (`web-gdelt-poller §6.2 L99`; `web-search-mojeek §6.2 L96`; `web-search-perplexity §6.2 L97`; `yt-web-search-bridge §6.2 L113`, `§9 L157`), next to a separate `engine` field; `CONVENTIONS L36` lists none of them, and other green examples carry `"vendor": null` (`fb-client-webhook-receiver §6.2 L114`; `yt-pubsub-receiver §6.2 L107`).
  - c) The source row's vendor against the reading vendor: accepted Telegram channels get "`route = amber`, `vendor = telemetrio`" from the resolver's stats (`tg-channel-resolver §4 L34`), while their posts are read through an Apify Actor and carry `"vendor": "apify_tugelbay"` (`tg-channel-posts-poller §6.2 L112`).
  - d) Clearance: CONVENTIONS lists Apify as cleared and SociaVault, ScrapeCreators, TikHub among the weakly cleared (`CONVENTIONS L6`), but not the Actor publishers whose names are the vendor values (`harvestapi`, `tugelbay`, `sovereigntaylor`; "harvestapi Actors on Apify", `CONVENTIONS L190`).
- **At stake:** the SDK compares the flag value with `sources.vendor` and the envelope's `vendor` to decide whether a source may be read and how provenance is labelled; with three spellings a Telegram source never matches its flag, and a `vendor` value outside the list fails F2's enum or lets an engine name pass as an amber vendor in provenance filters (amber data is excluded for government clients).
- **Options:** (1) one vocabulary used by flags, `sources.vendor` and envelopes (for example `apify_tugelbay` everywhere, the Actor path held in configuration); (2) short flag values mapped to registry values in the SDK, recorded in F2; and for (b): (3) add the engines to the vendor list, or (4) keep `vendor = null` on green engine records and name the engine only in `engine`. For (c), `sources.vendor` names the vendor that reads the posts, or the registry holds one vendor per role (stats, posts). For (d), the vendor list in CONVENTIONS records the Actor publishers explicitly, or the vendor values name only the cleared platform (Apify).
- **Blocks:** F2, F3, F4, C7, C12, VTG2, VTG3, VLI1, VLI2, VLI3, VLI4, W1, W2, W4, YT9

#### CF-098

**`source.events` event types: `tier change` or `tier_change`, a `route` event and a lease-lapse reason nobody emits, and no event for `blocked`**

- **Type:** enum, names
- **Where:**
  - a) The list: "registry changes (added, updated, tier change, dormant, retired, fallback_on, fallback_off)" (`CONVENTIONS L21`), one name with a space among underscored ones; registry-writer emits `tier_change` (`registry-writer §3 L24`, `§6.2 L98`); the pollers and readers write `tier change` (for example `fb-page-feed-poller §6.2 L129`, `news-feed-poller §6.2 L115`, `ig-account-media-poller §6.2 L125`, which also emits `dormant`). Who may write the topic is section 1 (topics)'s entry CF-016.
  - b) Types read that no writer emits: li-client-posts-poller reads "`source.events` (`added`, `updated`, `route` change, `retired`)" (`li-client-posts-poller §6.1 L101`); yt-uploads-reconciler waits for "`updated`, `reason = push_lease_lapsed`" (`yt-uploads-reconciler §5.1 L51`; overlaps AU-016 in `CONFLICTS-ASSUMPTIONS.md`); ig-hashtag-search writes "budget waits" (`ig-hashtag-search §6.2 L93`) under no listed type.
  - c) Health: registry-writer maps the canary's `health_change` to "`fallback_on` or `fallback_off` per source, or `updated` for `degraded` and `ok`" (`registry-writer §5.2 L54`), with no event for `blocked`, which the canary produces (`source-health-canary §5.3 L72`); tg-bot-channel-receiver writes "`updated`, health" (`tg-bot-channel-receiver §6.2 L134`).
- **At stake:** consumers filter on the event string, so a cache that listens for `tier_change` never sees a poller's `tier change`; a `route` change or a lease lapse is waited for and never comes; a route-wide `blocked` reaches no consumer as an event.
- **Options:** (1) one closed list in F2 with underscores (`added`, `updated`, `tier_change`, `dormant`, `retired`, `fallback_on`, `fallback_off`), `updated` carrying a `reason` (for example `route_changed`, `push_lease_lapsed`, `budget_wait`, `health`); (2) the same list extended with explicit types for the reasons (`route_change`, `health_change` including `blocked`, `lease_lapsed`); (3) CONVENTIONS' spelling kept and registry-writer aligned to it.
- **Blocks:** F2, C7, C12, LI1, YT2, YT3, IG2, IG3, FB2, N3, TG1, and every `source.events` consumer

### Budgets

#### CF-099

**Budget tags: names outside the canonical list, wildcard rows in quota-governor, and external calls that ask the governor for nothing**

- **Type:** budget, names, rule
- **Where:**
  - a) Rule: "Every service that calls an external API or vendor declares a `budget_tag` and asks `quota-governor` for allowance before a batch" (`CONVENTIONS L85`); "Budget tags (canonical; use exactly these)", mixing `:` and `_` before the placeholder (`meta_graph_pages:<client_id>`, `tt_display:<client_id>`, `linkedin_cm:<client_id>` against `ig_graph_<ig_user_id>`, `ig_hashtag_<ig_user_id>`, `li_vendor_<action>`) (`CONVENTIONS L279`).
  - b) Names outside the list: `ig_graph_<client_id>` (`ig-hashtag-search §5.2 L65`, `§7 L136`) against `ig_graph_<ig_user_id>`; `analysis_model_api` "(new, to be added to the canonical list)" if a model API is chosen (`analysis-sentiment §7 L119`; `analysis-entities §7 L123`; `analysis-topics §7 L126`; `analysis-media §7 L118`; `README L184`, decision 7), which quota-governor's tag table does not have.
  - c) quota-governor's tag table uses wildcards the canonical list does not: `tg_*`, `news_*`, `meta_*` (`quota-governor §5.3 L82`, `L83`).
  - d) External calls with no tag, each PRD saying so: Common Crawl ("The addendum lists no budget tag for it and none is used", `web-commoncrawl-scanner §7 L111`); the Telegram Bot API (`tg-bot-channel-receiver §7 L142`; `tg-discussion-receiver §7 L146`); the PubSubHubbub hub (`yt-pubsub-receiver §7 L138`); X compliance jobs, metered under `x_pay_per_use` "only if they are" post reads (`x-compliance-sync §7 L138`); LinkedIn Posts API confirmation calls, where "Green confirmation calls carry no price" (`li-org-resolver §5.2 L52`, `§7 L113`), on an API other LinkedIn services meter under `linkedin_cm:<client_id>`.
  - e) Buckets: YouTube details lookups come "from the `list` bucket" (`yt-web-search-bridge §7 L137`), a bucket the tag does not have (`search`, `ingest`, `comments`, `reserve`, `CONVENTIONS L279`), while yt-video-details-fetcher charges them to `ingest` (`yt-video-details-fetcher §5.2 L59`, `§7 L163`).
  - f) Granularity: one `tt_vendor` tag "for all amber TikTok services, with per-service sub-counters" (`CONVENTIONS L279`; "so a comment surge cannot starve this sub-counter", `tt-profile-videos-poller §7 L137`), against "should discovery and comments have separate lines so a comment surge cannot starve discovery?" (`tt-keyword-search §14 Q3 L160`, which also counts "five amber TikTok services" where the index has six).
  - Overlaps AU-068 in `CONFLICTS-ASSUMPTIONS.md` (tag, bucket and alert names the governor does not have).
- **At stake:** quota-governor denies an unknown tag as `flag_off` (`quota-governor §5.3 L67`), so `ig_graph_<client_id>` and `analysis_model_api` calls are refused; wildcard rows give F3 no concrete `budgets` rows to seed; the untagged calls are invisible to spend and rate tracking, against the CONVENTIONS rule.
- **Options:** (1) the canonical list as written, extended with `analysis_model_api` and with explicit Telegram and news tags in place of the wildcards; the PRDs aligned (`ig_graph_<ig_user_id>`); the untagged calls given zero-cost tags (for counting) or recorded as exempt in CONVENTIONS; (2) the same, with one separator rule for placeholders (`:` throughout); (3) wildcard families allowed in the governor's configuration, with each service's concrete tag recorded in its PRD.
- **Blocks:** F3, F5, C1, IG2, A1, A2, A3, A4, W5, TG1, TG2, YT2, X7, VLI2, YT4, YT9, VTT1, VTT4, VTT5

#### CF-100

**Budget priorities (README decision 2): client refreshes at 1 or 3, first sight at 1 for every tier, a priority-1 history read, and priorities sent by callers**

- **Type:** budget, enum, document
- **Where:**
  - a) The table: "1 tier-1 rotation, client refresh, ops, canaries; 2 tier-2 rotation, client keyword searches, comment steps up to +24 h; 3 tier-3 and dormant rotation, later comment steps, replies, +7 d metrics; 4 hot-post extras and resolvers; 5 backfill" (`README L179`, decision 2); in quota-governor, priorities are "derived from job kind and tier by an SDK helper; a caller cannot claim more than its kind allows" (`quota-governor §5.1 L39`, table `L43` to `L47`), "validated server-side" (`§12 L149`).
  - b) Client refresh: priority 1 (`README L179`; `quota-governor §5.1 L43`; `comment-decay-scheduler §5.1 L70`) against "the priority of client refreshes (proposed 3)" (`yt-comments-fetcher §14 Q2 L204`; `yt-replies-fetcher §14 Q3 L192`), "3 = +3 d, extensions and refreshes" (`x-replies-fetcher §7 L145`), and "`reserve` is for priority 1, which no job here carries" (`yt-comments-fetcher §7 L145`).
  - c) First sight: "The approved order does not place first sight from other tiers and keyword rules; this PRD proposes 1" (`yt-video-details-fetcher §5.1 L50`, `§14 Q1 L215`), and a merged call "asks at priority 1" for priority-1 and priority-3 ids together (`§13 L205`); the table would derive 2 or 3 from the tier.
  - d) History read on a client request: `keyword_history` at priority 1, backfill at 5 (`x-full-archive-search §5.2 L53`, `§13 L175`); the table has no row for it.
  - e) Priority set by the caller: "priority from `series_step`" (`yt-comments-fetcher §5.2 L53`; `x-replies-fetcher §5.2 L55`); fixed numbers set by the caller ("priority 3, or 4 for hot-thread extras", `yt-replies-fetcher §5.2 L50`, matching the table's rows) or outside the table (text refresh "at priority 3", `yt-text-purger §5.3 L84`); jobs that carry a priority (`tt-user-resolver §5.1 L41`; `x-filtered-stream §5.2 L70`); orderings the table does not give: "quota-governor ranks search last among green Facebook services" (`fb-page-search §7 L127`, `§12 L161`), while the table puts client keyword searches at 2 and "discovery lookups" at 4; resolver discovery and client jobs "are never stretched, only denied" (`tg-channel-resolver §5.1 L47`), while resolvers sit at 4, which `stretch` does not admit.
  - f) The YouTube `reserve` bucket: "for priority 1" (`quota-governor §5.3 L79`), against "the rest is reserve for catch-up, hot posts and client-requested refreshes" (`yt-keyword-search §7 L133`).
  - Overlaps AU-067 and AU-039 in `CONFLICTS-ASSUMPTIONS.md`.
- **At stake:** the SDK helper produces one number per job kind and tier; services whose tests assume another number fail, and in `stretch` (priorities 1 to 3, then 1 and 2 from 95%) a client refresh or a YouTube first sight is admitted or held depending on which table wins.
- **Options:** (1) README decision 2 and the governor's table as written, the PRDs aligned (client refresh 1, first sight by tier, `keyword_history` as backfill at 5); (2) the table extended with explicit rows (first sight at 1, text refresh at 3, client history reads at 1), still derived by the SDK helper and never sent by callers; (3) callers send a priority, validated against a per-kind maximum held by the governor.
- **Blocks:** F5, C1, C11, YT4, YT5, YT6, YT7, YT8, X4, X5, X6, VTT3, VTG2, FB6

#### CF-101

**Budget modes on metered green tags (X, YouTube): README decision 2 gates priorities on every budget, CONVENTIONS stretches and sheds hot extras only on amber routes**

- **Type:** budget, rule, document
- **Where:**
  - a) CONVENTIONS: tier intervals "on amber routes may be stretched ... when the monthly budget is 80% consumed, never below daily" (`CONVENTIONS L51`); "on amber routes the quota-governor may drop the hot-post extra fetches first when the monthly budget passes 80%" (`CONVENTIONS L271`).
  - b) README decision 2: "`stretch` from 80% of a budget (priorities 1 to 3; from 95% only 1 and 2; amber intervals stretched by a factor, never beyond 24 hours)", with hot-post extras at priority 4 (`README L179`), so on any tag, green ones included, hot extras stop at 80%; quota-governor applies the modes to "the tag's period budget" (`quota-governor §5.1 L49`) and `stretch_factor` to amber tags only (`§5.1 L51`).
  - c) Still open in the two PRDs that implement it: "Should the 80% stretch also cover metered green routes (X, YouTube), for hot extras only?" (`quota-governor §14 Q2 L171`; `comment-decay-scheduler §14 Q4 L205`); comment-decay-scheduler's stretch row stops hot windows and lengthens steps after +24 h (`comment-decay-scheduler §5.3 L101`).
  - d) A green route that expects interval stretching: at 80% of the X cap the governor "cuts x-full-archive-search jobs first, then stretches tier-2 and tier-3 searches to daily" and drops reply steps after +24 h (`x-recent-search §7 L143`), while x-replies-fetcher has the same 80% admit priorities 1 to 3, "so hot extras stop first" (`x-replies-fetcher §7 L145`); see AU-067 (d) in `CONFLICTS-ASSUMPTIONS.md`.
- **At stake:** on the X and YouTube tags, hot-post extras and priority-4 resolver lookups either stop at 80% (README) or continue to 100% (CONVENTIONS); the governor and the scheduler cannot both implement the modes until the scope is fixed, and x-recent-search's cascade has no counterpart in the governor.
- **Options:** (1) README decision 2 as written: priority gating on every tag, interval stretching on amber tags only; (2) `CONVENTIONS L51` and `L271` as written: stretching and hot-extra shedding on amber tags only; on green metered tags nothing is gated before the cap; (3) priority gating on every tag plus interval stretching on metered green tags too (X, YouTube), with x-recent-search's cascade written into the governor.
- **Blocks:** F5, C1, C11, X1, X3, X6, YT4, YT5

### Flags

#### CF-102

**Where the vendor flags live: environment variables in CONVENTIONS, read "at the start of every job" and by every shared service; and `fallback_on` as a flag or a health value**

- **Type:** flag, document
- **Where:**
  - a) "Config by environment variables" (`CONVENTIONS L12`); "the poller reads the flag at the start of every job" (`CONVENTIONS L102`); CONVENTIONS states no default value (flags are "off, or the vendor name", `CONVENTIONS L238`). PRDs read "environment `LI_VENDOR_ROUTE`" (`li-org-resolver §6.1 L75`; `li-post-search §6.1 L79`), "read at the start of every job" (`li-post-search §3 L26`), "the flag is never cached" (`tg-channel-posts-poller §5.2 L60`).
  - b) Shared services that read other services' flags: quota-governor denies `flag_off` when "its platform flag `off`" and reads "platform flags" (`quota-governor §5.3 L67`, `§6.1 L94`); source-health-canary keeps a `flag_name` per target and reads "the platform flags" (`source-health-canary §5.1 L47`, `§6.1 L96`, `§6.3 L108`); backfill-orchestrator reads "the platform flag" and sets `done` with note `flag_off` (`backfill-orchestrator §5.2 L56`); comment-decay-scheduler opens amber profiles "only when the platform flag ... is not `off`" (`comment-decay-scheduler §5.1 L44`); poster-resolver routes on `TT_VENDOR_ROUTE`, `LI_VENDOR_ROUTE`, `TG_VENDOR_ROUTE` (`poster-resolver §5.2 L56`).
  - c) Fallback: CONVENTIONS has the canary set "`fallback_on`; the poller reads the flag" (`CONVENTIONS L102`), while the registry has a `health` value `fallback` and no `fallback_on` column (`CONVENTIONS L36`); the canary moves to fallback when "its flag not `off`" (`source-health-canary §5.3 L71`) and tests "`TT_VENDOR_ROUTE` on" (`§13 L152`), a value the flag does not have; TikTok readers "use the flag's vendor, or the alternate ... vendor with a row in `vendor_keys` while `fallback_on` is in force" (`tt-profile-videos-poller §5.2 L58`); ig-hashtag-search sends `fallback_on` for a hashtag budget wait "when the amber route is on" (`ig-hashtag-search §5.1 L57`), a trigger that is neither the canary nor health, with no government-client exclusion (AU-087 in `CONFLICTS-ASSUMPTIONS.md`).
  - d) Behaviour with the flag `off`: the scheduler "emits nothing while `TT_VENDOR_ROUTE = off`" (`tt-profile-videos-poller §5.1 L41`), while its own acceptance test and two siblings expect a day of scheduled jobs "each ... counted as `flag_off`" (`tt-profile-videos-poller §13 L177`; `tt-keyword-search §13 L145`; `tt-hashtag-feed-poller §13 L154`).
- **At stake:** an environment variable is fixed per process, so a flip needs a redeploy of every service that reads it, and four shared services must be configured with every platform's flag; "read at the start of every job" then means nothing, and the amber code's off switch can disagree between a poller and quota-governor during a rollout.
- **Options:** (1) flags in a control-plane table read through the SDK at the start of every job (environment variables only as bootstrap defaults, `off`), with `fallback` state in `sources.health` or the canary's table; (2) environment variables as written, with every reading service listed and a restart on change; (3) environment variables for the per-platform route flag, and the canary's runtime `fallback_on` state in the control plane. In each case, one rule for a scheduler while its flag is `off` (emit nothing, or emit jobs that end `skipped_flag_off`) and one trigger for `fallback_on` (the canary only, or also budget waits).
- **Blocks:** F3, F4, F5, F6, C1, C8, C9, C10, C11, C12, IG2, VTT1, VTT2, VTT4, and every amber service

#### CF-103

**Flag values: one vendor per flag where two roles or a fallback need two, `TG_POSTS_ACTOR` missing from the flag list, a vendor value with no endpoint for one service, and the X plan gate**

- **Type:** flag, enum, document
- **Where:**
  - a) Lists: the flag list names five flags (`CONVENTIONS L238`); the addendum adds `TG_POSTS_ACTOR` with Actor names as values (`CONVENTIONS L280`).
  - b) Telegram: "`TG_VENDOR_ROUTE` carries one vendor name, but Telegram's amber route uses Telemetrio for search and stats and Apify for posts; this service treats any value other than `off` as on. Confirm or split the flag" (`tg-message-search §14 Q2 L153`; the same in `tg-channel-resolver §14 Q3 L166`).
  - c) TikTok: one value (`off | tikhub | ensembledata`, `CONVENTIONS L280`) while EnsembleData is "used as primary or fallback per the flag" (`CONVENTIONS L177`) and the canary falls back from TikHub to EnsembleData under the same flag (`source-health-canary §5.1 L47`, `§13 L152`); see CF-102 (c).
  - d) Facebook: `FB_VENDOR_ROUTE` "selects the vendor for all amber Facebook services", but ScrapeCreators has "a keyword-search endpoint, if one exists" (`fb-keyword-search §5.3 L63`, `L69`), and the PRD asks "should all amber Facebook services run on `sociavault`, or should a per-service override exist?" (`§14 Q1 L181`), while fb-group-posts-poller proposes ScrapeCreators as primary (`fb-group-posts-poller §14 Q3 L195`).
  - e) The X plan gate for government clients, one setting under three representations: a global "`X_PLAN = enterprise` with that end user declared" (`x-user-resolver §5.2 L54`); "the company app's X plan setting" (`x-replies-fetcher §5.2 L54`); a per-client "X Enterprise entitlement" in `clients` (`x-filtered-stream §6.1 L107`; `x-full-archive-search §6.1 L102`; `x-user-timeline-poller §5.2 L55`, `§6.1 L108`); the column `clients.x_enterprise` in the shared keyword-matcher (`keyword-matcher §5.3 L69`). See AU-095 in `CONFLICTS-ASSUMPTIONS.md`.
- **At stake:** a flag value that names one vendor cannot express "Telemetrio for search, Apify for posts" or a primary and a fallback, so services read it differently ("any value other than `off` as on"); with `FB_VENDOR_ROUTE = scrapecreators`, fb-keyword-search has no vendor to call; the X services filter government clients on three different settings, so one job serves a government client that another drops.
- **Options:** (1) one flag per vendor role (for example `TG_SEARCH_VENDOR`, `TG_POSTS_ACTOR`, a per-service override for Facebook), each value one vendor or `off`; (2) flags as on/off switches per platform, with the vendor per service and the fallback order held in `vendor_keys` or `canary_targets`; (3) the CONVENTIONS values as written, with the meaning "any non-`off` value enables every role" recorded and the fallback vendor taken from `vendor_keys` rows. For (e): one X plan setting (global flag or per-client column), named once and read by the seven X services and keyword-matcher.
- **Blocks:** F3, F4, C12, VTG1, VTG2, VTG3, VTT1, VTT2, VTT3, VTT4, VTT5, VTT6, VFB1, VFB2, VFB3, X1, X2, X3, X4, X5, X6

### Retention classes

#### CF-104

**Retention classes for routes CONVENTIONS gives none: green TikTok (`tiktok_display`, README decision 8), green Telegram (`vendor_agreed`), web-search results (`news_excerpt`)**

- **Type:** retention, document
- **Where:**
  - a) Rule: "retention class by route" (`CONVENTIONS L247`); the six classes (`CONVENTIONS L75` to `L80`) name no class for the TikTok Display API, the Telegram Bot API or web search.
  - b) TikTok Display API: README decision 8 has tt-client-videos-fetcher propose "a retention class `tiktok_display`" (`README L185`); the PRD writes `"retention_class": "tiktok_display"` (`tt-client-videos-fetcher §6.2 L106`), "proposed and not yet in `retention_classes`" (`§6.2 L115`), kept "while the authorisation is active and deleted on revocation, client offboarding or TikTok's request, as `meta_on_request` does" (`§14 Q2 L177`).
  - c) Green Telegram: `"retention_class": "vendor_agreed"` on Bot API data (`tg-bot-channel-receiver §6.2 L125`, `§7 L145`; `tg-discussion-receiver §6.2 L129`, `§7 L148`), a class defined "per the vendor contract" (`CONVENTIONS L79`), with no vendor on the route; both ask whether a dedicated class is wanted (`tg-bot-channel-receiver §14 Q5 L198`; `tg-discussion-receiver §14 Q5 L202`).
  - d) Web search: results carry `news_excerpt` (`web-search-perplexity §6.2 L106`, `§7 L121`; `web-search-mojeek §6.2 L105`; `web-gdelt-poller §6.2 L109`, `§7 L125`), a class whose clock is "`fetched_at` of the full text ... 7 days for the full-text cache" (`retention-purger §5.3 L67`), for records that hold no full text; retention-purger leaves "Retention class for Telegram bot content and for web-search results beyond `news_excerpt`: to be set with counsel" (`retention-purger §14 Q3 L172`).
- **At stake:** F3 seeds `retention_classes` and F8 sets ClickHouse TTLs from it; a class missing from the seed fails store-writer's lookup or gets no TTL, and a borrowed class applies the wrong clock (24 months by vendor contract for bot data with no vendor; a 7-day text purge for records with no text).
- **Options:** (1) add `tiktok_display`, a Telegram bot class and a web-search class to the seed, each with its clock; (2) map each route to an existing class (`tiktok_display` as `meta_on_request`, Telegram bot data as `vendor_agreed`, web results as `news_excerpt`) and record the mapping in CONVENTIONS; (3) a mix: `tiktok_display` added as README decision 8 proposes, the other two mapped.
- **Blocks:** F3, F8, C6, C14, TT1, TG1, TG2, W1, W2, W4, W3, YT9

#### CF-105

**LinkedIn data: amber records under `vendor_agreed` or `linkedin_48h`, one green class for organization and member fields, and member profile data at 24 hours**

- **Type:** retention, document
- **Where:**
  - a) CONVENTIONS: "`linkedin_48h`: member social-activity data purged after 48 hours; organization data as the API terms allow" (`CONVENTIONS L77`); "`vendor_agreed`: per the vendor contract ...; default 24 months for raw text" (`CONVENTIONS L79`); class by route (`CONVENTIONS L247`); the fact sheet: "member social-activity data stored at most 48 hours; most member profile data 24 hours; organization social activity data six weeks (six months if authenticated)" (`CONVENTIONS L192`).
  - b) Amber LinkedIn, two classes: posts carry `vendor_agreed` (`li-post-search §6.2 L92`; `li-company-posts-poller §6.2 L114`), except member reposts in li-company-posts-poller, held as `linkedin_48h` until legal decides (`li-company-posts-poller §7 L133`), comments `linkedin_48h`, "the stricter option, until legal decides" (`li-post-comments-fetcher §6.2 L120`, `§7 L139`); each asks the other way round (`li-post-search §14 Q2 L164`, member-authored posts; `li-company-posts-poller §14 Q5 L188`, reposts of member posts; `li-post-comments-fetcher §14 Q1 L192`).
  - c) Green LinkedIn, one class for different clocks: the envelope "carries `linkedin_48h`, the class for everything this route stores; retention-purger applies it by field: the page's own posts and counts as the organization rule allows (six weeks, six months if authenticated), any member-level field ... at 48 hours" (`li-client-posts-poller §7 L135`), while comment and reaction events are deleted "within 48 hours of `fetched_at`" by class (`li-notification-receiver §7 L142`); whether six weeks or six months applies is open and also sets the backfill cap (`li-client-posts-poller §5.1 L50`, `§14 Q2 L188`). See AU-078 in `CONFLICTS-ASSUMPTIONS.md`.
  - d) Member profile data: the PRDs repeat "most member profile data at most 24 hours" (`li-post-search §7 L115`; `li-org-resolver §7 L115`) or "most member profile data 24 hours" (`li-company-posts-poller §7 L133`), but no class has a 24-hour clock.
- **At stake:** retention-purger runs one clock per class, so an amber member post is kept 24 months under `vendor_agreed` against LinkedIn's 48-hour rule, or organization posts under `linkedin_48h` are deleted at 48 hours unless the purger has a per-field rule no PRD of its own defines; a 24-hour profile field has no class at all.
- **Options:** (1) `linkedin_48h` on every LinkedIn record (green and amber) with retention-purger's per-field rules (organization fields six weeks, member fields 48 hours, profile fields 24 hours) written into its PRD and CONVENTIONS; (2) separate classes per clock (for example `linkedin_org`, `linkedin_48h`, `linkedin_profile_24h`), assigned per record or field by the writing service; (3) `vendor_agreed` for amber LinkedIn as the class-by-route rule gives, `linkedin_48h` for green, after legal confirms the vendor contract.
- **Blocks:** F3, F8, C4, C6, C14, LI1, LI2, LI3, VLI1, VLI2, VLI3, VLI4

#### CF-106

**Derived data lifetimes: ten years for every class, against 36 months for YouTube (from creation or from the last fetch) and 48 hours for LinkedIn member analysis rows; and what `youtube_30d_text` covers**

- **Type:** retention, rule, document
- **Where:**
  - a) CONVENTIONS: "Aggregates and derived scores: ten years, all classes" (`CONVENTIONS L81`) against "`youtube_30d_text`: ... derived metrics kept up to 36 months" (`CONVENTIONS L76`).
  - b) YouTube: store-writer expires `youtube_30d_text` rows at "created + 36 months" (`store-writer §5.3 L76`); yt-text-purger deletes items, `analysis` and keyword-hit rows when "the last `fetched_at` is older than 36 months" and leaves aggregates unchanged (`yt-text-purger §5.3 L118`, `§13 L259`); still asked in `yt-comments-fetcher §14 Q5 L207` and `yt-video-details-fetcher §14 Q4 L218`. See AU-080 in `CONFLICTS-ASSUMPTIONS.md`.
  - c) LinkedIn: store-writer deletes `linkedin_48h` rows at 48 hours "with its `analysis` rows" (`store-writer §5.3 L77`) and asks whether they may outlive 48 hours "(derived scores are kept ten years elsewhere)" (`§14 Q3 L183`); the comment fetchers test deletion of "per-comment analysis row[s]" at 48 hours (`li-own-comments-fetcher §13 L178`; `li-post-comments-fetcher §7 L139`), while li-client-posts-poller keeps "Aggregates and derived scores ... ten years" (`li-client-posts-poller §7 L135`).
  - d) What `youtube_30d_text` covers: "raw comment text" (`CONVENTIONS L76`), but yt-text-purger runs the clock "for comments and replies ... and for video title and description" (`yt-text-purger §3 L19`, `§5.3 L120`, open in `§14 Q1 L266`), and yt-channel-resolver puts channel profiles in the class, "refreshed or dropped at 30 days" (`yt-channel-resolver §6.2 L113`, `§9 L160`).
- **At stake:** F8's TTLs and retention-purger's sweeps implement one lifetime per class and table; YouTube item-level metrics and analysis either disappear at 36 months (from one of two anchors) or stay ten years, and LinkedIn per-item scores either feed ten-year analysis or vanish at 48 hours.
- **Options:** (1) ten years for aggregates only; item-level derived rows follow the class (YouTube 36 months from creation, LinkedIn member rows 48 hours), with CONVENTIONS L81 reworded; (2) ten years for all derived rows as CONVENTIONS L81 says, with the YouTube and LinkedIn limits applied only to raw text and identities; (3) per-class lifetimes for both item-level derived rows and aggregates (YouTube aggregates also capped at 36 months), anchored on a named timestamp. For (d): the 30-day clock on comment text only, as CONVENTIONS words it, or also on titles, descriptions and channel profiles, as yt-text-purger and yt-channel-resolver assume.
- **Blocks:** F3, F8, C6, C13, C14, C15, YT1, YT4, YT5, YT7, LI2, VLI4

### Rules where a PRD departs from CONVENTIONS

#### CF-107

**Early stop (README decision 3): when it is armed, and what the 5% is measured against**

- **Type:** rule, document
- **Where:**
  - a) CONVENTIONS has no arming condition: "when a fetch adds fewer than 5% new comments (and fewer than 5 absolute), the remaining series is cancelled" (`CONVENTIONS L57`, `L271`). README decision 3: "Early stop is armed only once a post has 5 stored comments or after its +24 h step" (`README L180`); comment-decay-scheduler: "armed once `before >= 5` or the +24 h step has been reached ...; this arming rule is this PRD's addition" (`comment-decay-scheduler §5.3 L88`, `L89`; `§14 Q2 L203`); the same in `x-replies-fetcher §5.1 L45` and `yt-replies-fetcher §5.1 L40`.
  - b) Other arming: "From the second fetch of a post onward" (`li-own-comments-fetcher §5.1 L42`; `li-post-comments-fetcher §5.1 L44`); no arming, the CONVENTIONS rule restated (`fb-post-comments-fetcher §5.1 L48`, which asks whether "the +24 h sweep [should] be exempt from early stop", `§14 Q2 L188`; `news-comments-fetcher §5.1 L43`, `§13 L171`; `tt-video-comments-fetcher §5.1 L44`; `ig-comments-fetcher §5.1 L45`).
  - c) The denominator: the scheduler's `growth = new_count / max(before, 1)` over the stored total before the fetch (`comment-decay-scheduler §5.3 L87`); the same "over the comments stored before the fetch" (`ig-comments-fetcher §5.1 L45`; `tt-video-comments-fetcher §5.1 L44`); but "over the post's total comment count as the API reports it, not over comments held, because held comments expire at 48 hours" (`li-own-comments-fetcher §5.1 L42`).
- **At stake:** comment-decay-scheduler applies the rule centrally, so the fetchers' acceptance tests (LinkedIn from the second fetch, Facebook and news without arming) fail against it, or the scheduler needs per-profile arming and denominators; on LinkedIn, the stored total falls to zero after 48 hours, so the scheduler's ratio stops the series on the wrong basis.
- **Options:** (1) README decision 3 for every profile (armed at 5 stored or after +24 h, ratio over stored total), the fetcher PRDs aligned, with a LinkedIn exception for the denominator (API count) recorded in the scheduler; (2) per-profile arming and denominator columns in the scheduler's profile table, filled from the fetcher PRDs; (3) CONVENTIONS as written (no arming), with the +24 h step exempt from early stop as fb-post-comments-fetcher proposes.
- **Blocks:** C11, FB5, VFB3, IG6, VIG2, VTT5, X6, YT5, YT6, LI2, VLI4, N8

#### CF-108

**Disqus comment series: +6 h, +24 h, +3 d in four documents, the full decay series in news-site-resolver**

- **Type:** rule
- **Where:**
  - a) "+6 h, +24 h, +3 d" for "News (Disqus sites), green" (`CONVENTIONS L269`; `comment-decay-scheduler §5.1 L58`; `news-comments-fetcher §5.1 L43`; `news-article-extractor §5.1 L47`).
  - b) news-site-resolver's onboarding contract: "for Disqus sites comments on the decay series (+1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30)" (`news-site-resolver §5.1 L41`). See AU-041 in `CONFLICTS-ASSUMPTIONS.md`.
- **At stake:** a site onboarded under news-site-resolver's promise gets half the fetches it describes; `news_disqus` spend estimates differ by the extra five steps.
- **Options:** (1) the short series of CONVENTIONS and the scheduler, news-site-resolver corrected; (2) the full decay series for Disqus, with CONVENTIONS, the scheduler's profile and news-comments-fetcher changed and `news_disqus` re-estimated.
- **Blocks:** C11, N2, N8

#### CF-109

**`raw.items` "exactly as returned" (README decision 8): edge hashing in ten other services, not only TikTok, news records that hold an extract, and services that write no raw record**

- **Type:** rule, document
- **Where:**
  - a) Rule and proposal: `raw.items` holds "every record exactly as a fetch or push returned it, plus envelope" (`CONVENTIONS L15`); README decision 8 makes one exception: "commenter identity is hashed inside the adapter before the first write (so `raw.items` is not byte-for-byte the vendor payload)" for TikTok (`README L185`; `tt-video-comments-fetcher §3 L21`, `§5.3 L68`).
  - b) Other routes that minimise before `raw.items`: X replies (`x-replies-fetcher §5.2 L59`); YouTube comments and replies (`yt-comments-fetcher §5.2 L56`; `yt-replies-fetcher §5.2 L53`); Facebook webhooks ("The payload loses `from`", `fb-client-webhook-receiver §5.2 L58`) and vendor group comments (`fb-group-comments-fetcher §5.4 L94`); Instagram vendor comments ("unchanged except that author fields are replaced by `author_ref`", `ig-comments-fetcher §6.2 L93`); LinkedIn vendor comments (`li-post-comments-fetcher §5.2 L63`) and client-page reactions on the green webhook (`li-notification-receiver §5.2 L56`; comments there stay as received); Telegram group comments (`tg-discussion-receiver §5.2 L63`); Disqus comments (`news-comments-fetcher §5.2 L57`). Three of them ask for confirmation of "the one departure from 'exactly as returned'" (`li-post-comments-fetcher §14 Q5 L196`; `li-notification-receiver §14 Q5 L202`; `tg-discussion-receiver §14 Q4 L201`). Routes that keep identities in the raw payload and hash downstream: "usernames stay in the raw payload" (`ig-own-comments-fetcher §7 L139`), which also splits nested replies out of the comment record (`§5.1 L51`); "The author's handle stays in the raw payload" (`ig-keyword-search §5.4 L86`); "The poster's id and name stay in the payload" (`fb-group-posts-poller §6.2 L124`; `fb-keyword-search §6.2 L120`); LinkedIn client comments arrive "as a person URN" (`li-own-comments-fetcher §5.4 L95`).
  - c) News articles: "`raw.items` carries only `text_full_ref`, so raw-archiver never archives full text" (`news-article-extractor §5.3 L75`, `§7 L136`), an extracted record rather than the page as fetched.
  - d) Services that write no raw record at all: "No `raw.items` message and no archive object is ever produced by this service" (`tt-user-resolver §13 L165`; on a schema change "the response is dropped", `§8 L128`); tt-video-stats-refresher writes `item.metrics`, `deletions` and its completion message only (`tt-video-stats-refresher §6.2 L112`) and parks an unknown reading (`§8 L131`), against "the raw payload is still archived" on a schema change (`CONVENTIONS L103`).
  - Where the hash is computed and under which name is entry CF-069 (and AU-048 in `CONFLICTS-ASSUMPTIONS.md`).
- **At stake:** raw-archiver and replay assume `raw.items` can rebuild every downstream record (and services with no raw record cannot be replayed at all); with edge hashing on some routes and not others, a replay re-derives identities on one route and cannot on the next, and normalize-item must know per route whether to hash or pass `author_ref` through.
- **Options:** (1) README decision 8 widened into a rule: every adapter minimises personal identities before the first write, on every route, and CONVENTIONS L15 is reworded ("as returned, minus identities"); (2) the CONVENTIONS rule kept: raw records as returned, hashing only in normalize-item, the edge-hashing PRDs reverted (TikTok included); (3) a per-route list in CONVENTIONS of the routes that minimise at the edge (with the reason), the rest as returned; news articles recorded as an extract by rule, and the services with no raw record either given one or exempted by name.
- **Blocks:** F2, F4, C2, C4, X6, YT5, YT6, FB7, VFB2, VFB3, VFB1, VIG1, VIG2, IG6, LI2, VLI4, LI3, TG2, N6, N8, VTT3, VTT5, VTT6

#### CF-110

**The search output rule: every found item on `raw.items`, against web engines that archive whole responses with `normalize = skip` and publish results on `search.results`**

- **Type:** rule, document
- **Where:**
  - a) CONVENTIONS: "a search service writes every item it finds to `raw.items`, with `source_id` = the keyword-rule or hashtag source that produced the query, so the item enters the pipeline like any polled item"; source finders "(fb-page-search, web-commoncrawl-scanner, search-hit-router) write `discovery.hits` only" (`CONVENTIONS L281`). The topic list also has "`search.results` — web-search results before routing" (`CONVENTIONS L26`), which the rule never mentions.
  - b) The web engines write "each full response body to `raw.items` with `kind_hint = search_response` and `normalize = skip`" and one `search.results` message per result (`web-search-perplexity §5.2 L55`, `§6.2 L89`, `L90`; `web-search-mojeek §5.2 L57`, `§6.2 L88`, `L89`; `web-gdelt-poller §5.2 L57`, `§6.2 L91`, `L92`); yt-web-search-bridge writes `search.results` and jobs only, no `raw.items` (`yt-web-search-bridge §3 L23`, `§6.2 L102`); search-hit-router, a "source finder" in the rule, also writes `article.urls` (`search-hit-router §3 L26`).
  - c) normalize-item still maps "Perplexity and Mojeek (search-hit-router): `web:result:<sha256(canonical url)>`" as items (`normalize-item §5.3 L73`), from a service that writes no `raw.items`. The topics' writers and readers are section 1 (topics) (CF-008, CF-010) and AU-052 in `CONFLICTS-ASSUMPTIONS.md`.
- **At stake:** under the rule, each web result is an item that keyword-matcher and the analysis services see; under the PRDs, results reach the pipeline only if search-hit-router routes them to a platform or a news extractor, so web results that are neither never become items, and normalize-item's web mapper has no input.
- **Options:** (1) the PRDs' path recorded as the rule for web search: responses archived with `normalize = skip`, results on `search.results`, items only through search-hit-router's routing, normalize-item's `web:result` mapper removed; (2) the CONVENTIONS rule: each result also written to `raw.items` as a `web:result` item by the engines (or by search-hit-router), so results enter the pipeline as items; (3) both: results on `search.results` for routing, and search-hit-router writes a `web:result` item for results it cannot route.
- **Blocks:** F2, C4, C5, W1, W2, W3, W4, YT9

#### CF-111

**The news 7-day full-text cache (README decision 6): the extractor as owner, a second writer for comments, and the question still open in two PRDs**

- **Type:** writers, rule, document
- **Where:**
  - a) Proposal: "news-article-extractor owns the 7-day full-text cache and passes `text_full_ref`" (`README L183`, decision 6); the extractor writes `cache/news/<yyyy>/<mm>/<dd>/<canonical_url_hash>.json.zst` (`news-article-extractor §5.3 L75`) and normalize-item maps `text_full_ref` "to the 7-day cache" (`normalize-item §5.3 L72`), yet both PRDs still ask who owns it: "Does the 7-day cache live under this service ... or under a key written by normalize-item?" (`news-article-extractor §14 Q3 L189`; `normalize-item §14 Q2 L179`).
  - b) A second writer: news-comments-fetcher "write[s] the full text to the 7-day cache" under `cache/news/comments/...` (`news-comments-fetcher §5.2 L57`, `§6.2 L113`).
  - c) Readers not agreed: "May keyword-matcher and the analysis services read the 7-day cache ...? Proposed: yes" (`news-article-extractor §14 Q1 L187`); news-dedup does not read it (`news-dedup §5.4 L74`); deletion-propagator deletes "the 7-day news full-text cache" by `item_id` through the SDK's purge registry (`deletion-propagator §5.3 L68`). Matching on the excerpt or the full text is AU-055 in `CONFLICTS-ASSUMPTIONS.md`; the object prefixes are section 2 (tables)'s entry CF-053.
- **At stake:** with two writers and an open owner, retention-purger, deletion-propagator and the purge registry need to know every prefix and its key; a comment's full text under a prefix nobody registers survives its 7 days, and keyword-matcher cannot rely on the cache it may or may not read.
- **Options:** (1) README decision 6 as written, extended: each writer owns its prefix (`cache/news/` for articles, `cache/news/comments/` for Disqus comments), both registered in the purge registry, with the reader list fixed; (2) one cache writer for all news full text (normalize-item or an SDK cache client), the fetchers passing text to it; (3) articles only: Disqus comments keep no full text beyond the excerpt.
- **Blocks:** F4, C4, C5, C13, C14, N6, N7, N8, A1, A2, A3

#### CF-112

**lang-dialect-id in Python: a third exception to the Node rule**

- **Type:** rule, single-PRD
- **Where:**
  - a) "Language: Node (TypeScript) for every service except the analysis workers (Python, GPU pool or model API) and the news extractor (Python, trafilatura)" (`CONVENTIONS L13`).
  - b) "Runtime: Python, because CAMeL Tools and KLPT are Python libraries" (`lang-dialect-id §9 L150`), with "Python or Node? ... this a third exception. Confirm, or port the fold to TypeScript and keep only fastText and the dialect model in Python" (`§14 Q1 L187`).
- **At stake:** the session builds on the Node SDK (F4) or the Python SDK (F6) and in a different test stack; normalize-item, poster-resolver and the analysis services call it either way.
- **Options:** (1) Python, recorded as a third exception in CONVENTIONS; (2) the fold ported to TypeScript (Node), with only fastText and the dialect model kept in Python, so the Python exception narrows rather than disappears.
- **Blocks:** C3, F4, F6

#### CF-113

**When a missing post or comment becomes a `deletions` message: one error, a confirmed second miss, two full reads, or never**

- **Type:** rule
- **Where:**
  - a) Rule: "missing comments (when the API is complete) become `deletions` with reason `platform_sync`" (`CONVENTIONS L63`); CONVENTIONS has no rule for posts.
  - b) A post, on one error: "Post not found or no longer accessible: emit `deletions` with reason `platform_sync`; no retry" (`fb-reactions-fetcher §8 L144`, `§5.4 L92`, `§13 L176`); against "A single Graph error never produces a `deletions` event for the post" (`fb-post-comments-fetcher §8 L143`) and "no `deletions` event for the post from one error" (`fb-group-comments-fetcher §8 L145`), on the same Facebook posts.
  - c) A post, after confirmation: "A missing id stays for exactly one more call; missing again, it becomes one `deletions` message" (`yt-video-details-fetcher §5.2 L62`, `§6.2 L155`); "a confirming second request" (`tt-video-stats-refresher §5.2 L60`, `§13 L164`); never from a comment fetcher: "Video not found ...: status `video_not_found`, series ends, no deletions" (`yt-comments-fetcher §8 L156`).
  - d) A comment: after "two consecutive full reads miss it" (`tt-video-comments-fetcher §8 L138`, `§13 L173`); never: "Absence is never deletion ...; deletions come only from x-compliance-sync" (`x-replies-fetcher §8 L154`) and "a comment missing from a later fetch is never reported as deleted" (`ig-comments-fetcher §13 L171`); one complete fetch, as CONVENTIONS says, elsewhere ("only when the fetch was complete", `fb-post-comments-fetcher §5.2 L69`; `yt-comments-fetcher §13 L191`). A post deleted where a comment fetcher sees it first is AU-085 in `CONFLICTS-ASSUMPTIONS.md`.
- **At stake:** deletion-propagator removes the item and its derived rows on the first message it gets, so one Facebook post is erased by fb-reactions-fetcher's single error while fb-post-comments-fetcher, reading the same post, would have kept it; the confirmation rule belongs in the SDK if every route is to share it.
- **Options:** (1) one rule for every route: a post or comment is deleted only after a confirmed second miss (or a platform deletion signal), implemented once in the SDK; (2) CONVENTIONS' rule extended to posts: one complete read that misses the item is enough, the confirmation steps removed; (3) per route, as written, with fb-reactions-fetcher aligned to the other Facebook services and X replies and Instagram vendor comments recorded as "no deletion on absence" in CONVENTIONS.
- **Blocks:** F4, C13, FB4, FB5, VFB3, YT4, YT5, VTT5, VTT6, X6, VIG2

#### CF-114

**Rotation mechanics: a "shared scheduler" for Instagram hashtags, and due times kept outside `sources.next_poll_at` when two services rotate one row**

- **Type:** rule
- **Where:**
  - a) Rule: "Every service that polls keeps its own rotation scheduler as a leader-elected loop (Postgres advisory lock) that emits due jobs, exactly as described in fb-page-feed-poller" (`CONVENTIONS L278`); "the scheduler keeps `next_poll_at` per source and emits a job when it is due" (`CONVENTIONS L51`).
  - b) ig-hashtag-search's jobs are "emitted by the shared scheduler when a hashtag source's `next_poll_at` is due" (`ig-hashtag-search §5.1 L45`), a scheduler no PRD defines (AU-088 in `CONFLICTS-ASSUMPTIONS.md`).
  - c) Due times outside the registry column: "`sources.next_poll_at` belongs to ig-account-media-poller's rotation of the same row, so this service keeps its own schedule inside its `cursors` row" (`ig-mentions-fetcher §5.1 L45`), although its scheduler "selects `sources` rows with ... a due `next_poll_at`" (`§5.1 L41`); "The due time lives in this service's own `cursors` row ..., because ig-hashtag-search holds the same hashtag row in fallback" (`ig-keyword-search §5.1 L45`); "`next_search_at` per keyword in `cursors`" (`fb-page-search §5.1 L42`). Several schedulers on one `next_poll_at` (the web engines, two news pollers) are section 2 (tables)'s entry CF-031; the extra `cursors` columns are CF-035.
- **At stake:** the SDK's rotation helper reads `sources.next_poll_at` (rotation lag, `rotation_behind`, ordering), so services that schedule from `cursors` either need a second helper or report lag on the wrong clock; no build session owns the "shared scheduler".
- **Options:** (1) the CONVENTIONS rule: every rotating service runs its own leader-elected scheduler, and a service sharing a row with another keeps its due time in a per-service column or table the SDK helper reads; (2) one shared scheduler component in the SDK for all rotating services, driven by per-service due times; (3) as written, with ig-hashtag-search given its own scheduler and the `cursors` due times recorded in CONVENTIONS as the rule for shared rows.
- **Blocks:** F3, F5, IG2, IG5, VIG1, FB6

#### CF-115

**X keyword coverage on the filtered stream: every client brand keyword set, or the tier-1 keyword rules x-recent-search names**

- **Type:** rule
- **Where:**
  - a) x-filtered-stream fills its rules in order "client brand keyword sets (one rule each, priority 1), tier-1 accounts (priority 1), tier-2 (2), tier-3 (3)" (`x-filtered-stream §5.1 L40`, `§13 L191`).
  - b) x-recent-search: "Tier-1 keyword rules also run as stream rules on x-filtered-stream; the 15-minute search stays on as the safety net" (`x-recent-search §5.1 L47`). The line names tier-1 keyword rules; it does not say whether other keyword rules are streamed or excluded.
- **At stake:** the 1,000-rule budget is filled first with keyword coverage, then accounts; how many rules keyword coverage takes (every brand set, or the tier-1 keyword rules) decides how many accounts get real-time coverage and how x-recent-search's cost split between stream and search works out.
- **Options:** (1) every client brand keyword set on the stream, as x-filtered-stream says, with x-recent-search's split rewritten; (2) only tier-1 keyword rules on the stream, one reading of x-recent-search, which names tier-1 rules without excluding others; (3) streamed rules chosen by priority within a fixed share of the 1,000 rules, recorded in both PRDs.
- **Blocks:** X1, X4

### Baseline documents

#### CF-116

**"Already approved; do not rewrite" (CONVENTIONS L282): twenty PRDs that sit on one side of entries in this file, several against CONVENTIONS itself**

- **Type:** document
- **Where:**
  - a) "Written PRDs to stay consistent with (already approved; do not rewrite): fb-page-search, fb-page-feed-poller, fb-backfill, fb-reactions-fetcher, ig-hashtag-search, tt-keyword-search, tt-hashtag-feed-poller, x-recent-search, li-post-search, li-org-resolver, tg-message-search, tg-channel-resolver, yt-keyword-search, yt-web-search-bridge, news-site-resolver, web-search-perplexity, normalize-item, poster-resolver, qualifier, registry-writer" (`CONVENTIONS L282`); CONVENTIONS also makes fb-page-feed-poller the model every rotation scheduler follows "exactly" (`CONVENTIONS L278`).
  - b) Approved PRDs that depart from CONVENTIONS in this file: fb-page-feed-poller, fb-backfill, fb-page-search and x-recent-search name the job type `reason`, not `kind` (CF-077 b); fb-page-search keys its queue on `keyword_id` (CF-087 c); fb-reactions-fetcher expects `refresh_24h` and `refresh_7d` kinds (CF-081 b); ig-hashtag-search charges `ig_graph_<client_id>` (CF-099 b); tt-keyword-search, tt-hashtag-feed-poller and tg-message-search backfill on their own first run (CF-088 c); li-org-resolver and tg-channel-resolver take jobs without the CONVENTIONS fields (CF-085 b, c); tg-message-search's job has no `source_id`, `kind` or `due_at` (CF-077 e); web-search-perplexity and yt-web-search-bridge publish results on `search.results` instead of items on `raw.items` (CF-110 b); registry-writer spells `tier_change` (CF-098 a).
  - c) Approved PRDs on one side of a disagreement with unapproved PRDs: normalize-item's mapper keys (CF-060 to CF-066) and yt-keyword-search's `youtube:video:` (CF-061); poster-resolver's resolver round trip (CF-085 a) and author hash (entry CF-069); news-site-resolver's Disqus series (CF-108) and producer list (CF-085 d); web-search-perplexity's `site_search` (CF-078 e).
  - d) Approved against approved, where L282 and option (1) decide nothing: normalize-item against tt-keyword-search and tt-hashtag-feed-poller on TikTok keys (CF-062); normalize-item against tg-message-search on Telegram keys (CF-063; `normalize-item §5.3 L70` against `tg-message-search §5.2 L54`); normalize-item against li-post-search on LinkedIn keys (CF-064); li-org-resolver's `linkedin:org:` against poster-resolver's `candidate_key` rule (CF-073); web-search-perplexity expecting `site_search` jobs from yt-web-search-bridge, which emits none (CF-078 e); li-org-resolver expecting `refresh` from qualifier, which emits no job (CF-078 f); poster-resolver against li-org-resolver and tg-channel-resolver on the resolver round trip (CF-085); registry-writer's `tier_change` against fb-page-feed-poller's `tier change` (CF-098); normalize-item's `web:result` mapper against web-search-perplexity, which writes no result items (CF-110).
- **At stake:** D2 cannot settle the entries above by "align the PRD" without lifting L282, and cannot settle them by "align CONVENTIONS" without CONVENTIONS contradicting its own rules; a build session that follows L282 literally keeps every departure.
- **Options:** (1) the approved PRDs win: where one of them departs from CONVENTIONS, CONVENTIONS v1.1 records the PRD's version; (2) CONVENTIONS wins: L282 is lifted for the points D2 decides, and the approved PRDs are revised; (3) per entry, D2 states which side moves, and L282 is reworded to "approved except where D2 decided otherwise"; (4) for the d) cases: per entry, D2 names which approved PRD moves.
- **Blocks:** F2, and every session whose PRD is listed in L282 (FB6, FB2, FB3, FB4, IG2, VTT1, VTT2, X1, VLI1, VLI2, VTG1, VTG2, YT8, YT9, N2, W1, C4, C8, C9, C7)

#### CF-117

**Smaller CONVENTIONS and README inconsistencies (wording, lists and labels), for one batch decision**

- **Type:** document
- **Where:**
  - a) Replies "through the same service with job kind `replies`" (`CONVENTIONS L60`) against the YouTube row, where replies have their own service, yt-replies-fetcher (`CONVENTIONS L265`).
  - b) The X cap "per billing cycle" (`CONVENTIONS L87`; `quota-governor §5.1 L53`, `§5.3 L78`) against "per month on pay-per-use" (`CONVENTIONS L187`; `x-full-archive-search §7 L139`).
  - c) Route values: "GREEN", "AMBER", "RED" (`CONVENTIONS L7`), `route` (green or amber) in the registry (`CONVENTIONS L36`), and `shared` in the PRD template (`CONVENTIONS L122`); lanes: six in the template (`CONVENTIONS L122`), seven in the addendum, adding "Comments and stats" (`CONVENTIONS L275`).
  - d) Service names take a platform prefix (`CONVENTIONS L11`), yet search-hit-router is listed under Web without `web-` (`CONVENTIONS L234`).
  - e) README: "the amber services are the only way to those" includes "Google search results" (`README L18`), but every web-search service is green (`README L143` to `L147`) and CONVENTIONS has "no Google route" (`CONVENTIONS L217`); tt-hashtag-feed-poller "Keeps registered hashtags on rotation" (`README L70`) but is listed among the search services, not the pollers (`README L22`, `L30`); the decisions are "consistent across the PRDs that use them" (`README L176`), while decision 4 itself says fb-backfill's PRD writes the same column "to be aligned" (`README L181`), and this file finds conflicts against all nine decisions (section 4).
- **At stake:** none of these breaks a contract alone, but build sessions quote CONVENTIONS and the README literally: a replies job sent to yt-comments-fetcher, an X budget period whose reset time depends on which line is read, a route enum with `shared`, or a lane value the template rejects.
- **Options:** (1) one editorial pass on CONVENTIONS v1.1 and the README, with each sub-point decided on its own: for (a), replies as job kind `replies` on the comments service (`CONVENTIONS L60`) or through their own service, yt-replies-fetcher (`CONVENTIONS L265`); for (b), per billing cycle (`CONVENTIONS L87`) or per calendar month (`CONVENTIONS L187`); for (c), upper-case or lower-case route values, `shared` as a route value or only a PRD header label, and six or seven lanes; for (d), every service name takes the platform prefix (search-hit-router renamed) or search-hit-router stays as named as a listed exception to `CONVENTIONS L11`; for (e), the README statements are reworded to match the service lists, or the service lists change to match the statements; (2) leave the documents and record the readings in the D2 decision log only.
- **Blocks:** F2, F5, C1, YT5, YT6


### Keys added in verification

#### CF-118

**News article and URL keys: `news:url:<hex>`, `news:article:<hex>` and `news:article:sha256:<hex>`**

- **Type:** key, types
- **Where:**
  - a) The rule: "for news, `news:article:<canonical_url_hash>`" (`CONVENTIONS L69`), with no rendering given for the hash; normalize-item's mapper builds the same form (`normalize-item §5.3 L72`, `§13 L166`).
  - b) Bare hex after `news:article:`: news-article-extractor's `"idempotency_key": "news:article:e7a41b09..."` (`news-article-extractor §6.2 L98`; `§9 L152` `news:article:<canonical_url_hash>`); news-dedup's `idempotency_key` and `duplicate_of` (`news-dedup §6.2 L90`, `L93`).
  - c) A `sha256:` prefix inside the key: search-hit-router's `"idempotency_key": "news:article:sha256:9c1e4b…"` on `article.urls` (`search-hit-router §6.2 L123`), where the router and the web engines render `canonical_url_hash` as `"sha256:…"` (`search-hit-router §6.2 L128`; `web-search-perplexity §6.2 L103`, `web-search-mojeek §6.2 L102`, `web-gdelt-poller §6.2 L106`); the router's own prose and acceptance test give `news:article:<canonical_url_hash>` (`search-hit-router §9 L159`, `§13 L184`).
  - d) A URL key on the same topic: the three news pollers key `article.urls` by `url_key = news:url:<sha256 of normalised URL>`, a hash of the found URL rather than the canonical one (`news-feed-poller §6.2 L100`, `§9 L142`; `news-sitemap-poller §6.2 L112`, `§9 L154`; `news-homepage-differ §6.2 L105`, `§9 L145`), while search-hit-router's `article.urls` carries the article key of c); the extractor's record carries both, `url_key` beside `idempotency_key` (`news-article-extractor §6.2 L98-L99`).
  - The field names `url_key` against `idempotency_key` and the two `article.urls` layouts are CF-022.
  - Overlaps: `CF-022` in this file; `AU-106` in `CONFLICTS-ASSUMPTIONS.md` (the key of a same-canonical copy).
- **At stake:** one article reaches the pipeline under up to three strings (`news:url:<hex>` from a poller, `news:article:sha256:<hex>` from search-hit-router, `news:article:<hex>` from the extractor and news-dedup) that never compare equal, so a consumer that deduplicates or joins on the key splits it; the contracts package's key helper cannot render the hash two ways, and `article.urls` has no single key field.
- **Options:** (1) `news:article:<64 hex>` with the bare hex everywhere (search-hit-router strips the `sha256:` prefix), and `url_key = news:url:<hex>` kept as the URL-level key every `article.urls` producer writes; (2) the `sha256:` rendering everywhere (`news:article:sha256:<hex>`, `news:url:sha256:<hex>`), `CONVENTIONS L69`, the extractor and news-dedup changed; (3) `article.urls` carries only the URL key `news:url:<hex>` for every producer, search-hit-router included, and `news:article:<hex>` exists only from the extractor onward.
- **Blocks:** F2, C4, N3, N4, N5, N6, N7, W3


## 4. The README's nine proposed decisions: what D1 found


The build plan's foundation table says of "The nine decisions proposed in `docs/prds/README.md`": "Accept as written unless D1 finds a conflict" (`build-plan/README.md` L51). For each proposal (`README L178` to `L186`), whether a conflict was found and where:

| # | Proposal | Conflict found | Entries |
|---|---|---|---|
| 1 | Completion topic `jobs.completed` (`jobs.completed/v1`) written by the SDK job wrapper, with `new_count`, `seen_count`, `pages`, `cost_units`, `reply_candidates` (`README L178`) | Yes: other report channels and names (fetch report, job result, completion message, `service_runs` result rows, a backfill report); three services write the topic themselves; report fields, `seen_count`'s meaning and status values differ; x-recent-search, whose reports two services read, never mentions the topic | CF-089 (also AU-001) |
| 2 | Budget priorities 1 to 5 and modes; the +24 h comment step held, never cancelled (`README L179`) | Yes: client refresh at 3 in yt-comments-fetcher, yt-replies-fetcher and x-replies-fetcher; first sight at 1 for every tier; priorities sent by callers; the YouTube `reserve` bucket's use; modes on metered green tags against CONVENTIONS' amber-only stretch; a denied LinkedIn step dropped after 24 h | CF-100, CF-101, CF-090 (also AU-067) |
| 3 | Early stop armed once a post has 5 stored comments or after its +24 h step (`README L180`) | Yes: the LinkedIn fetchers arm it from the second fetch; four fetchers restate CONVENTIONS with no arming; li-own-comments-fetcher measures against the API's count | CF-107 |
| 4 | backfill-orchestrator the single writer of `backfill_status`; a failed or slow backfill ends `capped`; fb-group-posts-poller the target for groups (`README L181`) | Yes: other writers of the column; services that expect an orchestrator job the route table never sends, or backfill themselves; job fields; "done at once" against `capped` for Telegram | CF-088; CF-030 |
| 5 | A platform 401 or 403 means `blocked`, no automatic fallback; a vendor error `degraded`; `scope = non_government` (`README L182`) | Yes: `CONVENTIONS L101` and most fetchers mark `degraded`; per-page and per-chat `blocked` variants; fallback triggered outside the canary (hashtag budget waits) | CF-094, CF-102 (c) |
| 6 | News: topic `news.dedup`; a per-host gate in the SDK; news-article-extractor owns the 7-day cache (`README L183`) | Yes: only the extractor doubles the gate's spacing after 429 or 503; a second cache writer (Disqus comments) and the owner still asked in two PRDs; `news.dedup`'s only named reader (normalize-item) does not read it | CF-092 (d), CF-111; CF-025 |
| 7 | Analysis: a priority lane per task; `items.analysis/v1` keyed `item_id:task:model_version`; `analysis_model_api`; YouTube thumbnails only (`README L184`) | Yes: a four-part key from analysis-topics; lanes per service, not per task; the store keyed on `item_id, model`; `analysis_model_api` not in the governor's tags. No conflict found on thumbnails. | CF-075, CF-099 (b); CF-050, AU-023 |
| 8 | TikTok: commenter identity hashed in the adapter; tt-client-videos-fetcher writes its own +24 h and +7 d metrics; `tiktok_display`; client-authorised accounts `tier = push` (`README L185`) | Yes: edge hashing in ten other services; metrics outside comment-decay-scheduler, against the README's own count list; `tiktok_display` not in the class list; `push` on an hourly-polled account reconciled by the amber poller | CF-109, CF-080 (e), CF-082 (b), CF-104 (b), CF-096 |
| 9 | New control-plane tables (fourteen tables and `canary_targets` columns) (`README L186`) | Yes: the X read ledger has three key forms and the Instagram hashtag ledger is its own table or rows in `budgets`; `model_versions` is named differently by four analysis PRDs and read by a service that does not list it; tables named in one PRD only and missing from `CONVENTIONS L30` | CF-038, CF-058, CF-059 |



## Appendix. Candidates the consolidation passes noted for another category

Each consolidation pass listed what it met outside its own category, so nothing seen is lost; most are covered by an entry above or in the assumptions file.


- C: 401 and 403 mean `degraded` (`CONVENTIONS L101`, `fb-page-feed-poller §8 L146`) or `blocked` (README proposal 5, `README L182`).
- B: `backfill_status` writers: backfill-orchestrator as single writer (`README L181`), fb-backfill (`fb-backfill §5.2 L56`), registry-writer's `backfill_status = pending` on `add` (`registry-writer §5.2 L52`).
- C: job type field `reason` (`fb-page-feed-poller §5.2 L54`, `x-recent-search §5.2 L53`, `fb-backfill §5.1 L41`) against `kind` (`CONVENTIONS L277`).
- C: job kinds outside the CONVENTIONS list: `push` (`ig-webhook-receiver §11 L162`), `first_sight` (`yt-pubsub-receiver §14 Q5 L194`), `resolve` (`fb-page-resolver §5.1 L42`), `rerun` (`analysis-entities §5.1 L46`, `analysis-media §5.1 L47`).
- C: job queues partitioned by `keyword_id` (`fb-page-search §5.1 L40`), `candidate_key` (`fb-page-resolver §5.1 L42`) or host (`news-robots-checker §5.1 L41`) instead of `source_id`.
- C: comment, reply and metrics jobs emitted outside comment-decay-scheduler (`CONVENTIONS L278`): `reconciliation` jobs on `jobs.ig-own-comments-fetcher` (`ig-webhook-receiver §5.1 L43`), yt-text-purger's refresh jobs (`yt-text-purger §5.3 L102`).
- C: idempotency key forms: `youtube:video:` (`yt-keyword-search §6.2 L102`) against `youtube:post:` (`yt-pubsub-receiver §6.2 L112`); `tiktok:video:` (`tt-client-videos-fetcher §6.2 L103`); `telegram:message:<chat_id>:<message_id>` (`normalize-item §5.3 L70`); `news:article:sha256:` (`search-hit-router §6.2 L123`); `news:comment:6203918455:v1` (`news-comments-fetcher §6.2 L101`); `linkedin:post:urn:li:activity:` (`li-post-search §6.2 L91`); `x:comment:` (`x-replies-fetcher §6.2 L115`).
- C: author hash names and derivations: `author_ref` as a keyed HMAC (`normalize-item §5.2 L54`, `x-replies-fetcher §5.2 L59`) against `author_hash = sha256(platform || platform_id || salt)` (`poster-resolver §5.2 L59`).
- C: id formats: ULID `item_ids` (`retention-purger §6.2 L102`) against `item_id = uuid_v5(ns_items, idempotency_key)` (`normalize-item §5.2 L51`); a composite `message_id` (`poster-resolver §6.2 L89`); uuid `client_id` (`keyword-matcher §6.2 L106`) against `"cl_17"` (`qualifier §6.2 L84`); `job_id` values that are not ULIDs (`tt-keyword-search §6.2 L86`, `li-post-search §6.2 L90`; ULID per `CONVENTIONS L277`).
- C: `candidate_key` forms: `instagram:<handle>` or `instagram:post:<shortcode>` (`search-hit-router §5.3 L74`), `news:<registrable domain>` (`search-hit-router §5.3 L83`), `linkedin:org:example-bank` (`li-org-resolver §6.2 L83`).
- C: tier values mix numbers and words, `tier` (1, 2, 3, push, dormant, retired) (`CONVENTIONS L36`), written as an integer (`qualifier §6.2 L84`) and as `"proposed_tier": 1` (`news-site-resolver §6.2 L94`; the field itself is in CF-013 c).
- C: `source.events` event names: `tier change` (`CONVENTIONS L21`), `tier_change` (`registry-writer §3 L24`), `route` change (`li-client-posts-poller §6.1 L101`).
- C: decision types: registry-writer applies `add`, `update`, `tier_change`, `tier_down`, `dormant`, `promote`, `retire`, `health_change`, `remove_client`, `queued` (`registry-writer §3 L22`); the qualifier also yields `reject`, `review` and `mention_only` (`qualifier §5.2 L52`, `qualifier §5.2 L61`).
- C: the canary's "any to blocked" transition (`source-health-canary §5.3 L72`) against registry-writer's `health_change` handling (`registry-writer §5.2 L54`).
- C: deletion reasons and modes: `withhold` (`x-compliance-sync §5.3 L77`), `"reason": "retention", "scope": "text_only", "mode": "purge_text"` (`yt-text-purger §6.2 L145`), `authorization_revoked` (`tt-client-videos-fetcher §14 Q3 L178`).
- C: observation labels: `webhook_reconcile` (`fb-reactions-fetcher §3 L19`), `"label": "plus_24h"` (`tt-video-stats-refresher §6.2 L101`).
- C: series step formats: `"+6h"` (`tt-video-comments-fetcher §6.2 L108`; series `tt-video-comments-fetcher §5.1 L43`) against `24h` or `7d` (`yt-video-details-fetcher §5.1 L45`).
- C: TikTok reply jobs' `post_ref` is "the parent comment's key for replies" (`tt-video-comments-fetcher §5.1 L41`).
- C: TikTok first-sight clock: the first `items.normalized` message (`tt-video-stats-refresher §5.1 L44`) against "the first read at or after each mark" (`tt-client-videos-fetcher §5.1 L51`).
- C: `raw.items` "exactly as a fetch or push returned it" (`CONVENTIONS L15`; README proposal 8 for TikTok, `README L185`) against edge changes: `from` removed (`tg-discussion-receiver §6.2 L134`), the author replaced by a hash (`li-post-comments-fetcher §5.2 L63`), name and avatar dropped (`news-comments-fetcher §5.2 L57`), nested replies split out (`ig-own-comments-fetcher §6.2 L125`).
- C: vendor responses never archived (`tt-user-resolver §5.3 L61`), or a service that writes only `item.metrics` (`tt-video-stats-refresher §6.2 L85`) and parks a reading on a schema change (`tt-video-stats-refresher §8 L131`), against "the raw payload is still archived" (`CONVENTIONS L103`).
- C: the poster's id and name kept in the payload (`fb-group-posts-poller §6.2 L124`) against the individuals rule (`CONVENTIONS L114`).
- C: retention class by route: `vendor_agreed` on green Bot API data (`tg-bot-channel-receiver §6.2 L125`); `linkedin_48h` on an amber route (`li-post-comments-fetcher §7 L139`).
- C: vendor values `mojeek` and `perplexity` in provenance (`web-search-mojeek §6.2 L88`, `web-search-perplexity §6.2 L89`) are not in the `vendor` list (`CONVENTIONS L36`).
- C: li-notification-receiver has no job queue (`li-notification-receiver §5.1 L40`) yet writes `job_id` and `attempt` (`li-notification-receiver §6.2 L133`) and counts `dlq_total` (`li-notification-receiver §10 L166`).
- C: `found_via` for URLs from the hourly regular-sitemap rotation (`news-sitemap-poller §3 L20`; the example `news-sitemap-poller §6.2 L114` shows `news_sitemap`) is not among the values the extractor orders by (`news-article-extractor §5.1 L43`).
- C: brand identifiers: KB `entity_id` such as `kb-pl-0007` (`analysis-entities §6.2 L108`) against `brand_id` from `brand_assets` (`analysis-media §5.3 L68`, `analysis-media §13 L158`).
- C: `"schema": "alert/v1"` (`alert-evaluator §6.2 L87`) is the payload of "n8n webhook calls and client webhook posts" (`alert-evaluator §6.2 L83`), not a Redpanda topic.
- C (assumption): the engines count on search-hit-router to verify that results are Iraqi (`web-search-perplexity §5.4 L80`, `web-search-mojeek §5.4 L77`); the router gets no "proof that a result is Iraqi" (`search-hit-router §5.4 L89`). Filed as `AU-110`.
- B: stores named in one PRD or shaped there: `comment_ledger` (`fb-post-comments-fetcher §6.3 L129`), `profile_cache` (`fb-page-resolver §6.3 L132`), the `hits` table fed by both hit topics (`store-writer §5.3 L63`), `news_urls` (`news-article-extractor §6.3 L129`), the `crawl_policies` row (`news-robots-checker §6.2 L117`), `review_queue` parking (`normalize-item §5.2 L50`), replay progress in `cursors` (`normalize-item §6.3 L124`), stream state in `service_runs` (`x-filtered-stream §6.3 L149`).
- B: the raw archive: re-runs read "normalized items" from raw-archiver's Parquet archive (`analysis-entities §5.1 L46`, `analysis-media §5.1 L47`), which holds envelopes and payloads (`raw-archiver §5.3 L67`); `raw_ref` batch names `000123.jsonl.zst#17` (`raw-archiver §6.2 L108`) against `0007.jsonl.zst#1532` (`normalize-item §6.2 L119`).
- No D1 category: X read-counter metric names `x_post_reads_paid_total` (`x-recent-search §10 L164`) against `post_reads_total{paid,kind}` (`x-filtered-stream §10 L176`); metric names are each PRD's section 10 (`CLAUDE.md L52`).

Seen while reading the inputs; each disagrees between PRDs (or with CONVENTIONS or the README) but is about messages (A) or keys, jobs, values, budgets, flags, retention and rules (C), not about a store. Refs are the extractor's (`out/conflicts-noticed.md`), checked here only for line and section; the D files' IDs are given where one covers the point.

- A · `raw.items` record shape: flat fields against an `envelope` plus `payload`, and payloads that are not the record as fetched (authors replaced, replies split off, minimised or extracted records): `ig-hashtag-search §6.2 L97-L122`, `ig-account-media-poller §6.2 L106-L123`, `tt-client-videos-fetcher §6.2 L96-L113`, `tt-profile-videos-poller §6.2 L107-L124`, `raw-archiver §5.4 L86`, `ig-own-comments-fetcher §6.2 L125`, `li-post-comments-fetcher §5.2 L63`, `news-article-extractor §5.3 L75`.
- A · `discovery.hits`: field sets, cardinality, receivers that write it, and the `candidate_key` partition: `x-recent-search §5.2 L58`, `tg-bot-channel-receiver §6.2 L134`, `tg-discussion-receiver §6.2 L138`, `tg-message-search §6.2 L79-L91`, `search-hit-router §6.2 L99`, `search-hit-router §6.2 L101-L115`, `web-commoncrawl-scanner §6.2 L84`, `ig-hashtag-search §6.2 L124` (AU-008 in `CONFLICTS-ASSUMPTIONS.md`).
- A · `poster.profiles`: `post_count` against `tweet_count`, `lang_share` keys lang-dialect-id does not produce, no `retention_class`, partition by `candidate_key`, and `country_signals` keys that differ per resolver: `x-user-resolver §6.2 L121`, `x-full-archive-search §5.2 L52`, `poster-resolver §6.2 L89`, `li-org-resolver §6.2 L101-L102`, `fb-page-resolver §6.2 L99`, `x-user-resolver §6.2 L101`, `ig-account-resolver §6.2 L116`, `news-site-resolver §6.2 L92`, `li-org-resolver §6.2 L94`, `tg-channel-resolver §6.2 L91` (AU-009 in `CONFLICTS-ASSUMPTIONS.md`).
- A · `item.metrics` shapes (flat `item_idempotency_key`, the raw envelope, `item_key`) and a comment count no producer emits: `fb-reactions-fetcher §6.2 L107`, `tt-client-videos-fetcher §6.2 L115`, `tt-video-stats-refresher §6.2 L87-L109`, `li-notification-receiver §6.1 L108`.
- A · `deletions` shapes from fetchers, purgers and x-compliance-sync, its producer as aggregator names it, and analysis services whose tests purge on `deletions` they do not read: `fb-post-comments-fetcher §6.2 L125`, `yt-text-purger §6.2 L142-L157`, `retention-purger §6.2 L96-L107`, `x-compliance-sync §5.3 L81`, `aggregator §5.1 L37`, `analysis-sentiment §6.1 L85`, `analysis-topics §6.1 L89`, `analysis-entities §6.1 L86`, `analysis-media §6.1 L83` (AU-013 and AU-077 in `CONFLICTS-ASSUMPTIONS.md`).
- A · `article.urls` and `search.results` fields (`found_at` without `fetched_at`; the bridge's results without `schema`, `message_id` or `canonical_url_hash`; `handled_by`): `news-feed-poller §6.2 L102`, `news-sitemap-poller §6.2 L114`, `news-homepage-differ §6.2 L107`, `search-hit-router §5.2 L55`, `search-hit-router §6.2 L117-L132`, `yt-web-search-bridge §6.2 L102` (AU-011 in `CONFLICTS-ASSUMPTIONS.md`).
- A · `crawl.policies` field names (`robots_status` against `robots.status`; signal names with hyphens or underscores): `news-robots-checker §5.3 L71`, `news-robots-checker §5.3 L73`, `news-robots-checker §6.2 L102`, `news-robots-checker §6.2 L107`.
- A · `registry.decisions`: `action` against `decision`, decision types each side handles, and no `source_id` on a route-level `health_change`: `source-health-canary §6.2 L102`, `qualifier §6.2 L84`, `registry-writer §3 L22`.
- A · `source.events` written by services other than registry-writer (`tier change`, `fallback_on`, `route change`) and `tier change` against `tier_change`: `news-feed-poller §6.2 L115`, `yt-uploads-reconciler §5.2 L65`, `ig-hashtag-search §5.1 L57`, `li-client-posts-poller §6.1 L101`, `x-user-timeline-poller §8 L151`, `fb-client-webhook-receiver §5.1 L42`, `registry-writer §3 L24`.
- A · `jobs.completed` transport and report fields (`reply_candidates` against `reply_threads` and other counters; reports through `service_runs` or the control-plane client): `fb-group-comments-fetcher §5.2 L66`, `ig-hashtag-search §5.2 L70`, `ig-own-comments-fetcher §5.2 L64`, `tt-video-comments-fetcher §5.2 L62`, `x-replies-fetcher §5.2 L62`, `li-post-search §5.2 L61`, `yt-replies-fetcher §5.2 L57` (AU-001 in `CONFLICTS-ASSUMPTIONS.md`, AU-017 in `CONFLICTS-ASSUMPTIONS.md`).
- A · backfill and observation markers (`job_kind` on `items.normalized`, `metrics_observation` values such as `webhook_reconcile`): `comment-decay-scheduler §5.1 L66`, `fb-reactions-fetcher §3 L19`, `fb-backfill §6.2 L88` (AU-002 in `CONFLICTS-ASSUMPTIONS.md`; AU-015 and AU-084 in `CONFLICTS-ASSUMPTIONS.md`).
- A · other field names: `item_fetched_at` against `fetched_at`, `matched_text` against `matched_term`, `keyword_set_version` against `set_version`, a news `date` against `published_at`, `push_lease_lapsed`, and the `news.dedup` story fields: `analysis-sentiment §6.2 L103`, `analysis-sentiment §5.2 L59`, `keyword-matcher §5.3 L58`, `news-article-extractor §6.2 L114`, `yt-uploads-reconciler §5.1 L51`, `news-dedup §6.2 L104` (AU-003 and AU-006 in `CONFLICTS-ASSUMPTIONS.md`, AU-016 in `CONFLICTS-ASSUMPTIONS.md`).
- A · hit routing: comments by unregistered authors sent to `item.hits`, and search results assumed to carry no keyword-rule `source_id`: `keyword-matcher §5.3 L75`, `keyword-matcher §5.1 L40`, `normalize-item §5.1 L41` (AU-019 in `CONFLICTS-ASSUMPTIONS.md`).
- C · 401 and 403: token or route `degraded` (`CONVENTIONS L101`) against `blocked` with an n8n card (`README L182`), in about forty PRD lines, for example `fb-page-feed-poller §8 L146`, `fb-backfill §8 L127`, `ig-account-media-poller §8 L141`, `ig-hashtag-search §8 L142`, `tt-client-videos-fetcher §8 L130` (where the mark is kept is CF-057).
- C · job-type field and kinds: `reason` against `kind`, and kinds outside `CONVENTIONS L277` (`resolve`, `refresh_24h`, `refresh_7d`, `push`, gap kinds): `fb-page-feed-poller §5.2 L54`, `fb-backfill §5.1 L41`, `x-recent-search §5.2 L53`, `fb-page-search §5.1 L40`, `fb-page-resolver §5.1 L42`, `fb-reactions-fetcher §5.1 L41`, `ig-webhook-receiver §5.2 L55`.
- C · job queues partitioned by `candidate_key`, `keyword_id`, host or handle instead of `source_id` (`CONVENTIONS L28`): `ig-account-resolver §5.1 L42`, `x-user-resolver §5.1 L41`, `li-org-resolver §5.1 L44`, `yt-channel-resolver §5.1 L44`, `tt-user-resolver §5.1 L41`, `tg-channel-resolver §5.1 L45`, `news-robots-checker §5.1 L41`, `fb-page-search §5.1 L40`.
- C · `job_id` examples that are not ULIDs: `tt-hashtag-feed-poller §6.2 L92`, `tt-keyword-search §6.2 L86`, `x-recent-search §6.2 L111`, `li-org-resolver §6.2 L103`, `li-post-search §6.2 L90`, `yt-keyword-search §6.2 L113`, `web-gdelt-poller §6.2 L100`.
- C · jobs emitted by a service CONVENTIONS does not name (a service's own backfill run, comment jobs from backfill-orchestrator, ig-webhook-receiver or yt-text-purger, a "shared scheduler"): `tg-message-search §5.1 L44`, `tt-keyword-search §5.1 L44`, `tt-hashtag-feed-poller §5.1 L48`, `li-own-comments-fetcher §5.1 L52`, `li-post-comments-fetcher §5.1 L54`, `ig-own-comments-fetcher §5.1 L41`, `yt-text-purger §5.3 L96-L102`, `ig-hashtag-search §5.1 L45`, `fb-backfill §5.1 L41` (AU-088 in `CONFLICTS-ASSUMPTIONS.md`).
- C · budget tags, priorities and units (`ig_graph_<client_id>` against `ig_graph_<ig_user_id>`, wildcard tags, sub-counters, items against USD, metrics order): `ig-hashtag-search §5.2 L65`, `ig-account-media-poller §5.2 L60`, `quota-governor §5.3 L82-L83`, `tt-profile-videos-poller §7 L137`, `tg-channel-posts-poller §5.2 L61`, `fb-reactions-fetcher §7 L134`, `fb-page-search §7 L127`, `tg-message-search §5.1 L46` (AU-065 to AU-068 in `CONFLICTS-ASSUMPTIONS.md`).
- C · flags: `TG_VENDOR_ROUTE` read as on for any value but `off`, the X plan gate in three forms, and flag-off handling: `tg-channel-resolver §14 Q3 L166`, `tg-message-search §14 Q2 L153`, `x-user-resolver §5.2 L54`, `x-user-timeline-poller §5.2 L55`, `x-replies-fetcher §5.2 L54`, `tt-profile-videos-poller §5.1 L41` (AU-095 in `CONFLICTS-ASSUMPTIONS.md`).
- C · vendor values outside `CONVENTIONS L36` (`gdelt`, `mojeek`, `perplexity`) and `telemetrio` on channels whose posts come through Apify: `web-gdelt-poller §6.2 L91`, `web-search-mojeek §6.2 L88`, `web-search-perplexity §6.2 L89`, `tg-channel-resolver §4 L34`.
- C · retention classes: `vendor_agreed` on green Telegram data, `youtube_30d_text` on profiles, titles and descriptions, `linkedin_48h` on an amber route, derived scores at 36 months, six weeks or six months for LinkedIn organization data, messages without `retention_class`: `tg-bot-channel-receiver §6.2 L118`, `tg-discussion-receiver §6.2 L129`, `yt-channel-resolver §6.2 L113`, `yt-text-purger §3 L19`, `yt-text-purger §2 L13`, `li-post-comments-fetcher §7 L139`, `li-org-resolver §7 L115`, `ig-account-resolver §6.2 L127` (AU-078 and AU-080 in `CONFLICTS-ASSUMPTIONS.md`).
- C · item keys: `youtube:video` against `youtube:post`, a `video` kind segment on TikTok `post` records, `x:comment` against `x:post`, LinkedIn URNs against bare ids, Telegram post-id case, an extra `org` segment in a `candidate_key`, a version suffix on news keys, and edits as a new key or a new version: `yt-keyword-search §5.1 L48`, `tt-client-videos-fetcher §6.2 L99`, `x-replies-fetcher §6.2 L115`, `li-post-comments-fetcher §6.2 L115`, `tg-channel-posts-poller §9 L156`, `li-org-resolver §5.2 L50`, `news-comments-fetcher §9 L149`, `fb-post-comments-fetcher §5.2 L68`, `fb-group-comments-fetcher §5.2 L65` (AU-049, AU-050 and AU-051 in `CONFLICTS-ASSUMPTIONS.md`, AU-096 in `CONFLICTS-ASSUMPTIONS.md`).
- C · author hashing: where (at the edge or in normalize-item), how (keyed HMAC, plain SHA-256 of `candidate_key`, scoped per source) and under which name (`author_ref`, `author_hash`, `candidate_ref`): `ig-comments-fetcher §5.2 L61`, `ig-account-resolver §5.1 L50`, `ig-own-comments-fetcher §3 L29`, `x-replies-fetcher §5.2 L59`, `x-compliance-sync §5.3 L81`, `x-user-resolver §5.2 L53`, `tt-video-comments-fetcher §5.3 L68`, `news-comments-fetcher §5.3 L76`, `li-notification-receiver §5.2 L56`, `fb-group-posts-poller §6.2 L124` (AU-048 in `CONFLICTS-ASSUMPTIONS.md`; the column name in ClickHouse is CF-049).
- C · id formats: `client_id` as `cl_a1b2` against uuids, short keyword and client ids against uuids, brand ids as KB `entity_id` or `brand_id`, `series_step` as `+6 h` or `+6h`: `tg-message-search §6.2 L85`, `poster-resolver §6.2 L89`, `analysis-entities §6.2 L108`, `tt-video-comments-fetcher §5.1 L43`, `yt-comments-fetcher §5.1 L44`, `yt-replies-fetcher §5.1 L40`.
- C · rotation cadences and tiers: hourly whatever the tier, no dormant tier, push for sources that are not client-owned, news tiers by publishing rate, keyword-rule cadences: `ig-mentions-fetcher §5.1 L43`, `tt-client-videos-fetcher §5.1 L43`, `li-client-posts-poller §5.1 L42`, `li-company-posts-poller §5.1 L43`, `tg-bot-channel-receiver §5.1 L44`, `yt-pubsub-receiver §5.1 L40`, `x-filtered-stream §5.1 L42`, `x-recent-search §5.1 L41`, `news-site-resolver §5.2 L53`, `news-homepage-differ §5.1 L43`, `news-sitemap-poller §5.1 L43`, `web-gdelt-poller §5.1 L41`.
- C · comment-series and metrics steps: early-stop arming, the +24 h step held or dropped, extension inside 7 days, reply steps at 80%, metrics steps: `ig-comments-fetcher §5.1 L45`, `li-own-comments-fetcher §5.1 L42`, `li-post-comments-fetcher §5.1 L44`, `li-post-comments-fetcher §5.1 L52`, `fb-post-comments-fetcher §12 L166`, `x-replies-fetcher §5.1 L45`, `x-recent-search §7 L143`, `tg-channel-posts-poller §5.1 L56`, `news-comments-fetcher §5.1 L43`.
- C · first-sight clock of TikTok metrics (the service's own first read, or the first `items.normalized`): `tt-client-videos-fetcher §5.1 L51`, `tt-video-stats-refresher §5.1 L44`.
- C · deletion by absence (one error, one complete read or two; search not a complete listing): `fb-reactions-fetcher §5.4 L92`, `tt-video-comments-fetcher §8 L138`, `x-replies-fetcher §5.4 L96`.
- C · news host rules (429 a recheck or a back-off, 404 and 410 a recheck or a refresh, doubling after 429 or 503): `news-robots-checker §5.1 L47`, `news-article-extractor §5.2 L54`, `news-article-extractor §5.3 L65`, `news-feed-poller §8 L131`, `news-homepage-differ §8 L135`, `news-sitemap-poller §8 L144` (AU-104 in `CONFLICTS-ASSUMPTIONS.md`).
- C · web results: `normalize = skip` against normalize-item mapping them, the Iraqi check expected of search-hit-router, and the bridge's engine for `site_search`: `web-search-mojeek §5.2 L57`, `web-search-perplexity §5.2 L55`, `web-gdelt-poller §5.2 L57`, `search-hit-router §5.4 L89`, `web-search-mojeek §3 L31`, `web-search-perplexity §3 L25` (AU-108 and AU-110 in `CONFLICTS-ASSUMPTIONS.md`).
- C · YouTube: cadence without a subscription and for dormant channels, `first_sight` job shapes, `made_for_kids`, channel reference forms: `yt-pubsub-receiver §5.1 L40`, `yt-uploads-reconciler §5.1 L45`, `yt-keyword-search §5.2 L59`, `yt-pubsub-receiver §6.2 L127`, `yt-channel-resolver §5.2 L62`, `yt-channel-resolver §3 L19`, `yt-web-search-bridge §5.2 L59` (AU-100, AU-101 and AU-109 in `CONFLICTS-ASSUMPTIONS.md`).
- C · X: gap jobs from x-filtered-stream, the reply hand-back, the meaning of `new_count`, a backfill window "longer on client request": `x-filtered-stream §5.2 L70`, `x-recent-search §5.2 L53`, `x-full-archive-search §5.1 L39`, `x-full-archive-search §6.2 L128`, `x-replies-fetcher §5.3 L69`, `x-user-timeline-poller §5.2 L61`, `x-full-archive-search §2 L13` (AU-093 and AU-096 in `CONFLICTS-ASSUMPTIONS.md`).
- C · DLQ threshold (fifth or sixth failure) and quota answers (`wait-until` sleeps or requeues; what `deny` does): `tt-hashtag-feed-poller §8 L122`, `tt-keyword-search §8 L116`, `tg-channel-posts-poller §8 L144`, `web-search-mojeek §8 L124`, `web-search-perplexity §8 L125`, `tt-client-videos-fetcher §5.2 L57`, `tt-keyword-search §5.2 L50`, `tt-profile-videos-poller §5.2 L59`.
- C · internal APIs: raw-archiver's rewrite and media endpoints, `/capacity`, callers of `/v1/detect` besides normalize-item: `deletion-propagator §5.3 L64`, `quota-governor §3 L22`, `analysis-media §5.3 L66`, `poster-resolver §5.2 L58` (AU-074 in `CONFLICTS-ASSUMPTIONS.md`).

- `discovery.hits` defined as hits on items while three source-finding services write it (`CONVENTIONS L18`, `L281`): section 1 (topics) (CF-010).
- Default `source_id` partitioning for topics about non-sources (`CONVENTIONS L14`, `L19`, `L24`, `L27`) and `search.results` with no writer in the rule (`CONVENTIONS L26`, `L281`): section 1 (topics) (CF-003; the rule side is CF-110).
- `poster.profiles` writers and the resolver answer path (`poster-resolver §5.3 L70`): section 1 (topics) (CF-012); the job half is CF-085.
- `item.metrics` written twice for one fetch (`normalize-item §5.2 L56`; `fb-reactions-fetcher §3 L19`) and LinkedIn counts with no producer (`li-notification-receiver §6.1 L108`): section 1 (topics) (CF-018).
- Ledgers with no table (`CONVENTIONS L279`, `L30`): section 2 (tables) (CF-038).
- `client_sources` against `sources.client_ids[]` (`CONVENTIONS L30`, `L36`) and state used by rules with no column (priority lists, seed lists, watchlists, 180-day rejections, last post time; `CONVENTIONS L45`, `L49`, `L250`): section 2 (tables) (CF-056 and the table entries).
- Services that write Meta usage headers into `budgets` themselves (for example `ig-account-media-poller §5.2 L65`; `li-client-posts-poller §5.2 L62`, rate-limit usage): section 2 (tables) (CF-037).
- One `next_poll_at` and `last_polled_at` written by several schedulers (`ig-mentions-fetcher §5.2 L60`; the web engines; two news pollers): section 2 (tables) (CF-031).
- Who writes `sources.health` and `backfill_status` (`registry-writer §3 L27`; `fb-backfill §5.2 L51`): section 2 (tables) (CF-032, CF-030).
- Internal endpoints with no agreed definition, no D1 category: qualifier's `POST /capacity` (`qualifier §5.3 L67`) against "a capacity query" in quota-governor (`quota-governor §3 L22`); deletion-propagator's call to "raw-archiver's rewrite endpoint (`POST /v1/...`)" (`deletion-propagator §5.3 L64`), which raw-archiver describes without a path (`raw-archiver §5.1 L44`).
