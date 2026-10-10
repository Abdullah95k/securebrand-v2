# D2 proposals · Decisions and contract freeze

D2 phase 1 · 7 Oct 2026 · Status: **proposals for the user; nothing is decided.** The orchestrator puts these decisions to the user. Phase 2, a fresh session, writes the ADRs, CONVENTIONS v1.1 and `docs/decisions/DEFERRED.md` from the answers. Until a decision is answered, a build session that meets one of its entries stops and asks, as `docs/contracts/CONFLICTS.md` says.

`docs/decisions/D2-SUMMARY.md` lists only the decisions that need the user, with one-line options, and the technical decisions as a table to object to.

## What this covers

Every input the D2 brief and `/decide-session D2` name, each placed in exactly one decision or marked "no decision needed" with the reason:

- the 118 entries of `docs/contracts/CONFLICTS.md` (CF-001 to CF-118) and the 113 of `docs/contracts/CONFLICTS-ASSUMPTIONS.md` (AU-001 to AU-113), read with `docs/contracts/INVENTORY.md`;
- the nine decisions proposed in `docs/prds/README.md` (L176 to L186), written RD-1 to RD-9 below;
- the thirteen foundation choices in `build-plan/README.md` (L47 to L63), written FC-01 to FC-13;
- the 387 open questions of `docs/prds/OPEN-QUESTIONS.md` (section 14 of the 86 PRDs; six PRDs list theirs as bullets, numbered here in order as D1 did), written `<service> §14 Qn`;
- the D1 review notes left open for D2 (`docs/reviews/D1.md`, notes 8 to 13, 16 and 17), written RN-08 to RN-17.

Appendix A maps every CF and AU entry to its decision; Appendix B does the same for the README decisions, the foundation choices and the review notes; Appendix C places every open question.

The order follows the brief: first the ground rule on the "already approved" PRDs (D2-Q001, CF-116), because every other recommendation assumes its answer; then the cross-cutting groups D1 named (Group 1); then the README's nine proposals (Group 2); then the foundation choices (Group 3); then the rest, by area (Groups 4 to 9).

## How to read a decision

- **Class.** _user_: a business, product, vendor, legal or cost choice only the user can make. _technical_: a choice an engineer makes on the evidence; the recommendation stands unless the user objects.
- **Settles** lists the entries the answer closes. Ids as above; `CF-nnn` and `AU-nnn` are entries of the two conflict files.
- **Blocks** lists the build sessions that cannot finish without the answer, F2 (contracts package), F3 (control-plane schema) and F8 (ClickHouse schema) first.
- **Depends on** names decisions whose answer this one assumes. Where a decision depends on another, its recommendation assumes the other's recommendation.
- **Options** come with the recommendation first, marked "recommended", and the consequences of each. The options are D1's where D1's fit, renumbered; a reference such as "CF-004 (1)" points to D1's numbering.
- **Phase 2 records** says what the ADR and CONVENTIONS v1.1 would say if the recommendation is accepted, so the session that writes them can do it without re-deriving.
- References follow D1: `service §5.2 L54` is that line of `docs/prds/<platform>/<service>.md`; `CONVENTIONS L36` is `docs/prds/_shared/CONVENTIONS.md`; `README L182` is `docs/prds/README.md`.
- "Approved PRD" means one of the twenty PRDs CONVENTIONS L282 calls "already approved; do not rewrite". D2-Q001 decides what that means; the other decisions say when their recommendation moves an approved PRD.

## Reference: the README decisions and foundation choices

| Id    | Source         | Proposal as written                                                                                                                                                                                                                                                                                                        |
| ----- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RD-1  | README L178    | Completion topic `jobs.completed` (`jobs.completed/v1`), written by the listening-sdk job wrapper after every job, with `new_count`, `seen_count`, `pages`, `cost_units`, `reply_candidates`; read by comment-decay-scheduler and backfill-orchestrator                                                                    |
| RD-2  | README L179    | Budget priorities 1 to 5 and the modes `normal`, `stretch` (from 80%; from 95% only priorities 1 and 2; amber intervals stretched, never beyond 24 hours), `exhausted`; the +24 h comment step held, never cancelled                                                                                                       |
| RD-3  | README L180    | Early stop armed only once a post has 5 stored comments or after its +24 h step                                                                                                                                                                                                                                            |
| RD-4  | README L181    | backfill-orchestrator the single writer of `backfill_status`; a failed or slow backfill ends `capped` and the source enters rotation anyway; fb-group-posts-poller the backfill target for Facebook groups                                                                                                                 |
| RD-5  | README L182    | A platform 401 or 403 means `blocked`, no automatic fallback, an n8n approval card; a vendor key or plan error is `degraded` and may fall back; a green source watched by a government client never moves to an amber fallback (`scope = non_government`)                                                                  |
| RD-6  | README L183    | News: topic `news.dedup` from news-dedup to normalize-item; a per-host gate in listening-sdk (one connection, 2 to 5 s between requests, across all news services); news-article-extractor owns the 7-day full-text cache and passes `text_full_ref`                                                                       |
| RD-7  | README L184    | Analysis: a priority lane per task (`jobs.analysis-<task>.priority`) for tier-1 sources; `items.analysis/v1` keyed by `item_id:task:model_version` with an `input_hash`; budget tag `analysis_model_api` if a hosted model is chosen; YouTube audio and video not downloaded in v1 (thumbnails only), pending legal review |
| RD-8  | README L185    | TikTok: commenter identity hashed inside the adapter before the first write; tt-client-videos-fetcher writes its own +24 h and +7 d metrics and proposes the retention class `tiktok_display`; client-authorised accounts are `tier = push`                                                                                |
| RD-9  | README L186    | New control-plane tables: `comment_series`, `backfill_runs`, `x_read_ledger`, `ig_hashtag_ledger`, `budget_reservations`, `budget_history`, `canary_targets` columns, `news_urls`, `news_stories`, `news_story_members`, `model_versions`, `taxonomy_nodes`, `kb_entities`, `kb_aliases`, `brand_assets`                   |
| FC-01 | build plan L51 | The nine README decisions: accept as written unless D1 finds a conflict (blocks F2, F3)                                                                                                                                                                                                                                    |
| FC-02 | build plan L52 | One writer per topic and per column: every registry change goes through `registry.decisions` to registry-writer (F2, F3)                                                                                                                                                                                                   |
| FC-03 | build plan L53 | `item_id` derivation and canonical idempotency keys: a deterministic hash of the idempotency key, with golden vectors in both languages (F2)                                                                                                                                                                               |
| FC-04 | build plan L54 | Schema versioning: additive changes within a version; a breaking change is a new version with a dual-publish window (F2)                                                                                                                                                                                                   |
| FC-05 | build plan L55 | Kafka clients: `@confluentinc/kafka-javascript` for Node and `confluent-kafka` for Python, both on librdkafka (F4, F6)                                                                                                                                                                                                     |
| FC-06 | build plan L56 | Cluster: k3s on Hetzner, unless the team already runs Nomad (I1)                                                                                                                                                                                                                                                           |
| FC-07 | build plan L57 | Object storage: Hetzner Object Storage as primary, Backblaze B2 as the off-site copy of the raw archive (C2, I1)                                                                                                                                                                                                           |
| FC-08 | build plan L58 | Language of lang-dialect-id: Python (CAMeL Tools and KLPT), with a TypeScript copy of the fold for fallback (C3, F7)                                                                                                                                                                                                       |
| FC-09 | build plan L59 | ClickHouse topology: one node with backups in staging; a replicated pair before production (F8, I1)                                                                                                                                                                                                                        |
| FC-10 | build plan L60 | Tooling: pnpm and Turborepo, TypeScript strict, Vitest; uv, ruff, pytest; Zod 4 to JSON Schema to Pydantic (F1, F2)                                                                                                                                                                                                        |
| FC-11 | build plan L61 | Local stack: docker compose with Redpanda, Supabase CLI, ClickHouse and SeaweedFS as local S3 (F1)                                                                                                                                                                                                                         |
| FC-12 | build plan L62 | Environments: local (fake platform only), staging (real APIs on small budgets), production (I1)                                                                                                                                                                                                                            |
| FC-13 | build plan L63 | Dependency policy: a line in `docs/dependencies.md` per runtime dependency, checked against the vendor screen (F1 onward)                                                                                                                                                                                                  |

The build plan also leaves three choices to their owning sessions (L65): GPU pool or model API (A1 to A4), fold details beyond the PRD table (F7), and series and threshold tuning after real data (after G2). They are not D2's; phase 2 lists them in `DEFERRED.md`.

## Index of decisions

| Id                  | Decision                                                                                                                | Class     | Settles                                       | First sessions blocked                                                                             |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| [D2-Q001](#d2-q001) | How D2's decisions apply to the twenty "already approved" PRDs                                                          | user      | 1 CF/AU                                       | F2 first, then every session whose PRD is on the list: FB6, FB2, FB3, FB4, IG2                     |
| [D2-Q002](#d2-q002) | Message metadata and schema versioning                                                                                  | technical | FC-04; 1 CF/AU                                | F2 first, F4, F6, then C6, C7, C8                                                                  |
| [D2-Q003](#d2-q003) | Provenance and `retention_class` on every message                                                                       | user      | 1 CF/AU                                       | F2, F4, F6, then C5, C6, C8                                                                        |
| [D2-Q004](#d2-q004) | Partition keys for topics and job queues                                                                                | technical | 3 CF/AU; 1 open questions                     | F2, F4, F5, F6, then C4, C5                                                                        |
| [D2-Q005](#d2-q005) | The `raw.items` message: shape, envelope fields, and why a record was read                                              | technical | 5 CF/AU                                       | F2, F4, F6, C2, C4, C10                                                                            |
| [D2-Q006](#d2-q006) | Identifiers: key authority, `item_id`, `job_id`, client and keyword ids                                                 | technical | FC-03; 4 CF/AU                                | F2, F3, F8, then F4, F6, C4                                                                        |
| [D2-Q007](#d2-q007) | Item keys per platform                                                                                                  | technical | 8 CF/AU; 4 open questions                     | F2, F3, then C4, C13, IG2, IG3                                                                     |
| [D2-Q008](#d2-q008) | Item kinds and normalize-item's mappers                                                                                 | technical | 3 CF/AU; 1 open questions                     | F2, F4, then C2, C4, C5, C6                                                                        |
| [D2-Q009](#d2-q009) | Comment records: fields, content hash, edits                                                                            | technical | RN-13; 4 CF/AU                                | F2, F4, then C4, C6, C13, FB5                                                                      |
| [D2-Q010](#d2-q010) | Individuals' identities: one keyed reference, and where it is computed                                                  | user      | 4 CF/AU; 11 open questions                    | F2, F3, F8, F4, F6, C2                                                                             |
| [D2-Q011](#d2-q011) | The job envelope and the kind list                                                                                      | technical | RN-11; 4 CF/AU; 3 open questions              | F2, F4, F5, F6, then C11, FB4                                                                      |
| [D2-Q012](#d2-q012) | Who emits which job: the producer table, ops and client requests                                                        | technical | 7 CF/AU; 2 open questions                     | F2, F4, then C4, C5, C8, C10                                                                       |
| [D2-Q013](#d2-q013) | Registry ownership: one writer for identity and policy, named owners for operational columns, requests as decisions     | technical | FC-02; 6 CF/AU; 2 open questions              | F2, F3, then C1, C5, C7, C9                                                                        |
| [D2-Q014](#d2-q014) | `source.events`: one writer and a closed list of event types                                                            | technical | 2 CF/AU; 1 open questions                     | F2, then C6, C7, C10, C11, C12                                                                     |
| [D2-Q015](#d2-q015) | Rotation state when several services rotate one row                                                                     | technical | 3 CF/AU                                       | F3, then F5, C7, C10, FB6, IG2                                                                     |
| [D2-Q016](#d2-q016) | Source health and credential state                                                                                      | technical | 4 CF/AU                                       | F2, F3, then F4, F6, C7, C12                                                                       |
| [D2-Q017](#d2-q017) | How a finished job reports back: `jobs.completed` (README decision 1)                                                   | technical | RD-1, RN-12; 3 CF/AU; 3 open questions        | F2, F3, then F4, F5, F6, C10                                                                       |
| [D2-Q018](#d2-q018) | Budget priorities and modes (README decision 2)                                                                         | user      | RD-2; 4 CF/AU; 7 open questions               | F2, F5, C1, C10, C11, then YT4                                                                     |
| [D2-Q019](#d2-q019) | Early stop of a comment series (README decision 3)                                                                      | technical | RD-3; 1 CF/AU; 2 open questions               | C11, then FB5, VFB3, IG6, VIG2, VTT5                                                               |
| [D2-Q020](#d2-q020) | Backfill: one writer of `backfill_status`, a complete route table, one job and one report (README decision 4)           | technical | RD-4; 7 CF/AU; 3 open questions               | F2, F3, then F4, F5, C7, C10                                                                       |
| [D2-Q021](#d2-q021) | A platform 401 or 403, fallback, and the government exclusion (README decision 5)                                       | user      | RD-5; 2 CF/AU; 3 open questions               | F3, F4, F5, C7, C12, then every green fetcher                                                      |
| [D2-Q022](#d2-q022) | News: the `news.dedup` topic, the per-host gate and the 7-day full-text cache (README decision 6)                       | technical | RD-6; 6 CF/AU; 4 open questions               | F2, F8, F4 and F5, C4, C5, C6                                                                      |
| [D2-Q023](#d2-q023) | Analysis: lanes, the `items.analysis` key, the ClickHouse `analysis` table and `model_versions` (README decision 7)     | technical | RD-7; 5 CF/AU; 4 open questions               | F2, F3, F8, then C6, C15, A1                                                                       |
| [D2-Q024](#d2-q024) | TikTok: README decision 8 confirmed part by part                                                                        | technical | RD-8                                          | F2, F3, then C11, TT1, VTT4, VTT5                                                                  |
| [D2-Q025](#d2-q025) | New tables and stores named in one PRD (README decision 9)                                                              | technical | RD-9, RN-08, RN-09; 1 CF/AU; 1 open questions | F3, F8, then F4, C1, C2, C3                                                                        |
| [D2-Q026](#d2-q026) | Kafka client libraries for the two SDKs                                                                                 | technical | FC-05                                         | F4, F6                                                                                             |
| [D2-Q027](#d2-q027) | Where the platform runs: the cluster and object storage                                                                 | user      | FC-06, FC-07                                  | I1, then C2, I2, E2 and the gates G2 to G4; the account itself is something only the user can open |
| [D2-Q028](#d2-q028) | lang-dialect-id in Python, its callers, and Arabizi                                                                     | technical | FC-08; 3 CF/AU; 5 open questions              | F4, C3, F7, F6, then C8, VLI2                                                                      |
| [D2-Q029](#d2-q029) | ClickHouse topology and the three environments                                                                          | user      | FC-09, FC-12; 1 open questions                | F8, I1, E2, G2, G4                                                                                 |
| [D2-Q030](#d2-q030) | Ratify the tooling, local stack and dependency policy F1 built                                                          | technical | FC-10, FC-11, FC-13                           | F2, every session                                                                                  |
| [D2-Q031](#d2-q031) | Keyword hits: what `item.hits` and `discovery.hits` carry, and who writes them                                          | technical | 9 CF/AU; 8 open questions                     | F2, F4, C4, C5, C6, C7                                                                             |
| [D2-Q032](#d2-q032) | Resolvers: who publishes profiles, one `resolve` job, and refreshes of registered sources                               | technical | 8 CF/AU; 5 open questions                     | F2, F4, C7, C8, C9, FB1                                                                            |
| [D2-Q033](#d2-q033) | The `poster.profiles` message and the Iraqi-signal vocabulary                                                           | technical | 3 CF/AU; 4 open questions                     | F2, F3, F4, C3, C7, C8                                                                             |
| [D2-Q034](#d2-q034) | Engagement counts: one writer per observation, the `item.metrics` message and metrics jobs                              | technical | 6 CF/AU; 6 open questions                     | F2, F8, C4, C6, C11, FB2                                                                           |
| [D2-Q035](#d2-q035) | Deletions: one message, one remover, a guard against resurrection, and recompute                                        | technical | 10 CF/AU; 7 open questions                    | F2, F3, F8, F4, C2, C4                                                                             |
| [D2-Q036](#d2-q036) | News URLs and articles: keys, the `article.urls` message and the URL ledger                                             | technical | RN-10; 5 CF/AU; 1 open questions              | F2, F3, C4, N2, N3, N4                                                                             |
| [D2-Q037](#d2-q037) | The web-search path: `search.results`, raw archiving, the YouTube bridge and routing                                    | technical | 6 CF/AU; 3 open questions                     | F2, C1, C2, C4, C8, FB1                                                                            |
| [D2-Q038](#d2-q038) | Should web pages that are neither news nor social posts become mentions that clients see?                               | user      | 1 CF/AU                                       | F2, C4, C5, YT9, W1, W2                                                                            |
| [D2-Q039](#d2-q039) | The raw archive: replay, object-storage prefixes and lookups by id                                                      | technical | 6 CF/AU; 4 open questions                     | F2, F8, F4, F6, C2, C4                                                                             |
| [D2-Q040](#d2-q040) | News tables: who writes `news_sites` and `crawl_policies`, and where the host gate keeps its state                      | technical | 4 CF/AU; 2 open questions                     | F2, F3, F4, C7, C9, N1                                                                             |
| [D2-Q041](#d2-q041) | The `cursors` table: its key, its columns, and who may write a row                                                      | technical | 3 CF/AU; 2 open questions                     | F3, F4, F5, F6, C2, C4                                                                             |
| [D2-Q042](#d2-q042) | Budgets: one writer for the counters, a home for caps, the two ledgers and the tag list                                 | technical | 5 CF/AU; 2 open questions                     | F3, F5, C1, C9, A1, A2                                                                             |
| [D2-Q043](#d2-q043) | The `clients` table, and where a client's lists live                                                                    | technical | 2 CF/AU; 3 open questions                     | F3, C1, C5, C7, C8, C9                                                                             |
| [D2-Q044](#d2-q044) | The `keywords` table, and the keyword-rule sources the searchers rotate                                                 | technical | 2 CF/AU; 2 open questions                     | F2, F3, C5, C6, C7, C9                                                                             |
| [D2-Q045](#d2-q045) | The other shared tables: run status, retention classes, the review queue, decisions, resolver caches and audit trails   | technical | 7 CF/AU; 4 open questions                     | F3, F8, F4, F6, C2, C4                                                                             |
| [D2-Q046](#d2-q046) | Comment state for change detection, and the keys of `comment_series`                                                    | technical | RN-16; 2 CF/AU; 1 open questions              | F2, F3, F8, C6, C11, FB5                                                                           |
| [D2-Q047](#d2-q047) | ClickHouse: the column names readers use, what a purge empties, and the tables beyond CONVENTIONS                       | technical | 3 CF/AU; 2 open questions                     | F8, F4, C4, C5, C6, C8                                                                             |
| [D2-Q048](#d2-q048) | What clients can slice and be alerted on in v1                                                                          | user      | 3 CF/AU; 5 open questions                     | F8, then C15, A5, A1, A2, A3                                                                       |
| [D2-Q049](#d2-q049) | What `tier` holds, and what "push" means                                                                                | technical | 2 CF/AU; 1 open questions                     | F3, F5, C1, C7, C9, then TT1                                                                       |
| [D2-Q050](#d2-q050) | Where the vendor flags live, what happens while one is off, and the X plan gate                                         | technical | 2 CF/AU; 2 open questions                     | F3, F4, F5, F6, C1, C5                                                                             |
| [D2-Q051](#d2-q051) | Vendors: which vendor serves which role, how they are screened, how they are named                                      | user      | 2 CF/AU; 7 open questions                     | F2, F3, then F4, C7, C12, the vendor probes VFB0                                                   |
| [D2-Q052](#d2-q052) | Amber data and clients: consent, the 31st hashtag, and clients' own properties                                          | user      | 6 CF/AU; 3 open questions                     | F2, F3, then C1, C5, C7, C9                                                                        |
| [D2-Q053](#d2-q053) | Who may see an item: a shared pool or per-client data                                                                   | user      | 4 open questions                              | F2, F3, then C5, C13, Q1, U2                                                                       |
| [D2-Q054](#d2-q054) | Retention classes for the routes CONVENTIONS gives none: TikTok Display, the Telegram bot, web-search results           | user      | 1 CF/AU; 4 open questions                     | F3, F8, C6, C14, then TT1, TG1                                                                     |
| [D2-Q055](#d2-q055) | LinkedIn data: which class holds what, and the 24-hour and six-week rules                                               | user      | 2 CF/AU; 6 open questions                     | F3, F8, C4, C6, C13, C14                                                                           |
| [D2-Q056](#d2-q056) | How long derived data lives: ten years, YouTube's 36 months, LinkedIn's 48 hours, and what YouTube's 30-day rule covers | user      | 2 CF/AU; 6 open questions                     | F3, F8, C6, C13, C14, C15                                                                          |
| [D2-Q057](#d2-q057) | What a job does with a quota answer, when it reaches the DLQ, and who stretches amber rotation                          | technical | 4 CF/AU                                       | F4, F5, F6, C1, C10, C11                                                                           |
| [D2-Q058](#d2-q058) | Engagement-count refreshes on X, LinkedIn, Telegram and Facebook groups                                                 | user      | 2 CF/AU; 4 open questions                     | C11, VTG3, LI1, VLI3, VFB2, X1                                                                     |
| [D2-Q059](#d2-q059) | Coverage bought by default: history on add and extra comment fetches                                                    | user      | 7 CF/AU; 6 open questions                     | F2, then C4, C10, C11, X1, X5                                                                      |
| [D2-Q060](#d2-q060) | When comment and metrics steps fall due, and how reply threads are fetched                                              | technical | 2 CF/AU; 3 open questions                     | F2, F3, C10, C11, then FB3, FB4                                                                    |
| [D2-Q061](#d2-q061) | The Disqus comment series                                                                                               | technical | 3 CF/AU                                       | C11, N2, N8                                                                                        |
| [D2-Q062](#d2-q062) | When a missing post or comment becomes a deletion                                                                       | technical | 2 CF/AU; 3 open questions                     | F4, C13, then FB4, FB5, VFB3, YT4                                                                  |
| [D2-Q063](#d2-q063) | Which X keyword rules go on the filtered stream                                                                         | technical | 1 CF/AU; 1 open questions                     | X1, X4                                                                                             |
| [D2-Q064](#d2-q064) | Filling X stream gaps, X history jobs, and the key of an X reply                                                        | technical | 3 CF/AU; 2 open questions                     | F2, then F4, C4, C10, X1, X3                                                                       |
| [D2-Q065](#d2-q065) | YouTube: details jobs, partial records, the uploads playlist id, channels without push, and the text refresh            | technical | 6 CF/AU; 3 open questions                     | F2, F3, then C1, C4, C6, C7                                                                        |
| [D2-Q066](#d2-q066) | How a client's own properties, and the sources it asks for, enter the registry                                          | technical | 3 CF/AU; 1 open questions                     | F3, then C7, C8, C9, IG4, TG1                                                                      |
| [D2-Q067](#d2-q067) | One interface for the n8n flows, and who specifies and builds them                                                      | technical | 1 CF/AU                                       | F2, then A5, C1, C7, C9, C12                                                                       |
| [D2-Q068](#d2-q068) | Using platform content for models and media: training and evaluation data, Content Signals, stored media                | user      | 7 open questions                              | F2, A0, then C4, C13, A1, A2                                                                       |
| [D2-Q069](#d2-q069) | Legal policies the deletion and audit paths need: author requests, deadlines, backups, audit retention, the X rules     | user      | 1 CF/AU; 11 open questions                    | F2, F3, then C7, C13, C14, X7                                                                      |
| [D2-Q070](#d2-q070) | One editorial pass: the documents that disagree with themselves                                                         | technical | RN-17; 2 CF/AU                                | F2 first, then F5, C1, C2, C4, C5                                                                  |

## Group 0 · The ground rule

### D2-Q001 · How D2's decisions apply to the twenty "already approved" PRDs

- **Class:** user (whether D2 may change PRDs marked approved is the owner's call)
- **Settles:** CF-116
- **Blocks:** F2 first (it builds the contracts package from the ADRs and must know whether an approved PRD's example or the ADR wins), then every session whose PRD is on the list: FB6, FB2, FB3, FB4, IG2, VTT1, VTT2, X1, VLI1, VLI2, VTG1, VTG2, YT8, YT9, N2, W1, C4, C8, C9, C7

**Context.** This decision comes first because every other recommendation in this document assumes its answer. CONVENTIONS L282 lists twenty PRDs "to stay consistent with (already approved; do not rewrite)": fb-page-search, fb-page-feed-poller, fb-backfill, fb-reactions-fetcher, ig-hashtag-search, tt-keyword-search, tt-hashtag-feed-poller, x-recent-search, li-post-search, li-org-resolver, tg-message-search, tg-channel-resolver, yt-keyword-search, yt-web-search-bridge, news-site-resolver, web-search-perplexity, normalize-item, poster-resolver, qualifier and registry-writer. CONVENTIONS L278 also makes fb-page-feed-poller the model every rotation scheduler follows "exactly". D1 found these PRDs on one side of many entries (CF-116):

- Some depart from CONVENTIONS itself. fb-page-feed-poller, fb-backfill, fb-page-search and x-recent-search name the job type `reason`, not `kind` (CF-077 b). fb-page-search keys its queue on `keyword_id` (CF-087 c). fb-reactions-fetcher expects `refresh_24h` and `refresh_7d` kinds (CF-081 b). ig-hashtag-search charges `ig_graph_<client_id>` (CF-099 b). tt-keyword-search, tt-hashtag-feed-poller and tg-message-search backfill on their own first run (CF-088 c). web-search-perplexity and yt-web-search-bridge publish results on `search.results` instead of items on `raw.items` (CF-110 b). li-org-resolver and tg-channel-resolver take jobs without the CONVENTIONS fields (CF-085 b, c); tg-message-search's job has no `source_id`, `kind` or `due_at` (CF-077 e); registry-writer spells `tier_change` (CF-098 a).
- Some stand against unapproved PRDs, so where D2 decides for the other side the approved PRD moves: normalize-item's mapper keys (CF-060 to CF-066), poster-resolver's author hash (CF-069) and resolver round trip (CF-085 a), news-site-resolver's Disqus series (CF-108) and producer list (CF-085 d), web-search-perplexity's `site_search` (CF-078 e) (CONFLICTS.md L1903).
- In nine places two approved PRDs contradict each other, so L282 cannot decide them: normalize-item against tt-keyword-search and tt-hashtag-feed-poller on TikTok keys (CF-062), against tg-message-search on Telegram keys (CF-063) and against li-post-search on LinkedIn keys (CF-064); li-org-resolver's `linkedin:org:` against poster-resolver's `candidate_key` rule (CF-073); web-search-perplexity expecting `site_search` jobs that yt-web-search-bridge never sends (CF-078 e); li-org-resolver expecting `refresh` from qualifier (CF-078 f); poster-resolver against li-org-resolver and tg-channel-resolver on the resolver round trip (CF-085); registry-writer's `tier_change` against fb-page-feed-poller's `tier change` (CF-098); normalize-item's `web:result` mapper against web-search-perplexity, which writes no result items (CF-110).

Read literally, L282 leaves those nine undecidable and makes CONVENTIONS adopt every departure. Several recommendations below move an approved PRD (the `raw.items` shape in D2-Q005, the job field `kind` in D2-Q011, key formats in D2-Q007).

**Options**

1. **Each decision states which side moves, and L282 is reworded (recommended).** CONVENTIONS v1.1 replaces L282 with: "These PRDs were reviewed first. Where an ADR decides a contract question, the ADR wins over every PRD, approved or not, and each PRD edit cites its ADR." The approved PRDs keep their standing on everything no ADR touches. Consequences: every entry becomes decidable on its merits; the twenty PRDs are edited like the others where a decision goes against them; F2 builds the contracts from the ADRs, which its brief already requires ("When PRD examples disagree on a field, the ADR decides, never a majority of examples").
2. **The approved PRDs win.** Where an approved PRD departs from CONVENTIONS, CONVENTIONS v1.1 takes the PRD's version (for example `reason` beside `kind`, flat and nested `raw.items` side by side, `ig_graph_<client_id>`). Consequences: the fewest PRD edits, but two spellings of several contracts survive into F2, against the recommendations of D2-Q005, D2-Q007 and D2-Q011; and the nine approved-against-approved conflicts still need an answer each, so this option alone does not close CF-116.
3. **CONVENTIONS wins.** L282 is lifted for every point D2 decides, and the approved PRDs are revised to match CONVENTIONS. Consequences: a simple rule, but CONVENTIONS is silent on most points (no envelope fields, no topic beyond its thirteen, no table columns beyond `sources` and `cursors`), so most entries still need their own answer; in practice this is option 1 without its flexibility.

**Why the recommendation.** Option 1 is the only one that closes every case in CF-116, including the approved-against-approved ones (D1's option 4 is a special case of it), and it is the rule F2 already works to.

**Phase 2 records.** ADR "Decisions override approved PRDs" (Applies to: all). CONVENTIONS v1.1: L282 reworded as in option 1; in L278, "exactly as described in fb-page-feed-poller" becomes "as described in fb-page-feed-poller, with the job fields this document defines".

## Group 1 · Cross-cutting contracts

D1 named these first because many other entries follow from them: message metadata and provenance (CF-001, CF-002), the `raw.items` envelope (CF-004, CF-005), keys and `item_id` (CF-060 to CF-072), author identity (CF-069), the job vocabulary and its producers (CF-077 to CF-089) and registry ownership (CF-015, CF-016, CF-030 to CF-033). Where an entry of those ranges belongs to a README proposal (CF-024, CF-030, CF-088, CF-089), it is decided with that proposal in Group 2.

### D2-Q002 · Message metadata and schema versioning

- **Class:** technical
- **Settles:** FC-04, CF-001
- **Blocks:** F2 first (every schema), F4, F6, then C6, C7, C8, C9, W3 and every producer of a topic

**Context.** The PRDs version their messages three ways (CF-001): a string `schema` such as `"items.normalized/v1"` beside `message_id`, `produced_at` and a `producer {service, version, job_id}` block (`normalize-item §6.2 L95-L98`, `keyword-matcher §6.2 L99-L102`, the four analysis services); a string `schema` with a flat `service` field (news-dedup, news-robots-checker, news-site-resolver, tg-channel-resolver, tg-message-search, search-hit-router, web-commoncrawl-scanner, the web engines, the `jobs.completed` examples in comment-decay-scheduler and backfill-orchestrator, `comment-decay-scheduler §5.4 L127`, `backfill-orchestrator §5.4 L92`); an integer `schema_version` (`poster-resolver §6.2 L89`, `qualifier §6.2 L84`, `registry-writer §6.2 L95`); or nothing at all (every `raw.items` envelope, `item.metrics`, `deletions`, the news pollers' `article.urls`, the resolvers' `poster.profiles`, several `discovery.hits`). Two consumers branch on the string: store-writer parks any message whose `schema` it does not know (`store-writer §5.2 L46`) and search-hit-router parks a message without `schema = search.results/v1` (`search-hit-router §5.2 L55`), so as written store-writer would park every `item.metrics` and `source.events` message. CONVENTIONS puts "topic schemas" in listening-sdk (L12) but names no field. The build plan's foundation choice is "additive changes within a version; a breaking change is a new version with a dual-publish window" (FC-04), and `.claude/rules/contracts.md` already points to F2's `docs/contracts/VERSIONING.md`.

**Options**

1. **A `schema` string on every message, with one metadata block, and the build plan's versioning rule (recommended).** Every message on every topic carries `schema: "<topic>/v<n>"`, and every job on every queue `schema: "job/v<n>"` (one job envelope for all queues, its kind-specific fields validated by `kind`, D2-Q011); each also carries `message_id` (a ULID, derived deterministically where a replay must reproduce the same id, as D2-Q006 describes for `job_id`), `produced_at`, and `producer {service, version, job_id}`; the SDK stamps all four, so no service writes them by hand. Versioning: a change that only adds an optional field stays in the version; anything else (a removed or renamed field, a changed type or meaning) is a new version, published on the same topic beside the old one for a dual-publish window long enough for every consumer to move (F2's `VERSIONING.md` sets its length). The contracts package ships the new version before any producer emits it, so a consumer skips a known version it does not read and keeps reading the old one; it parks only versions the contracts package does not know, as store-writer does. Consequences: the majority form, and the one the two branching consumers already read; three approved PRDs (poster-resolver, qualifier, registry-writer) change `schema_version` to `schema` under D2-Q001; a message archived to object storage still says what it is, without its Kafka headers.
2. **An integer `schema_version` on every message, the topic implied by the topic name, with `message_id`, `produced_at` and a flat `service`.** Consequences: shorter, but a message copied out of its topic (the raw archive, a DLQ, a replay) no longer says what it is, and store-writer and search-hit-router change.
3. **The version in a Kafka header set by the SDK, nothing in the body.** Consequences: clean bodies, but the archive and the DLQ lose the version unless they copy headers, and every PRD example changes.

**Why the recommendation.** It is what most producers and both branching consumers already do, it survives archiving and replay, and the SDK can stamp it in one place.

**Phase 2 records.** ADR "Message metadata and schema versioning" (Applies to: all). CONVENTIONS v1.1, event bus section (L14 to L29): the four metadata fields and the versioning rule; F2 writes `VERSIONING.md` from it.

### D2-Q003 · Provenance and `retention_class` on every message

- **Class:** user (it reads the non-negotiable "every output carries provenance" in `CLAUDE.md`, the user's rule, as "every data output")
- **Settles:** CF-002
- **Blocks:** F2, F4, F6, then C5, C6, C8, A1, A2, A3, A4, N3, N4, N5, W1, W2, W3, W4, W5, FB6, IG1, IG2, X1, VLI2, YT9
- **Depends on:** D2-Q002

**Context.** "Every item carries provenance (route class, vendor, service, fetch time)" (`CONVENTIONS L115`). The repository rules go further: "Every output carries provenance (route, vendor, service, fetched_at) and `retention_class`" (`CLAUDE.md` L11); "Every topic payload carries provenance ... and retention_class" (F2 brief L36); the definition of done and the review checklist say the same (`build-plan/README.md` L40, `.claude/skills/review-session/SKILL.md` L22, `.claude/agents/prd-reviewer.md` L16). The PRDs miss it or rename it (CF-002): `article.urls` carries `found_at` or `first_seen_at` and no fetch time, search-hit-router's no route, vendor or class either; keyword-matcher's hit has no `fetched_at`; analyses carry `item_fetched_at`, profiles `resolved_at`, `item.metrics` `observed_at` flat or nested; the web engines' raw envelopes and yt-web-search-bridge's results have no class. Which `service` is meant varies (the fetching one in keyword-matcher's hit, the analysis service in analyses); only ig-account-resolver nests all four as `provenance {route, vendor, service, fetched_at}` (`ig-account-resolver §6.2 L119-L120`). Two classes are unclear: a profile is "registry metadata about an organization, kept as long as the source exists" for li-org-resolver (`li-org-resolver §7 L115`), while ig-account-resolver's acceptance test gives every message `meta_on_request` (`ig-account-resolver §13 L187`) and its individual message lists no class (`§6.2 L127`).

**Options**

1. **One nested `provenance {route, vendor, service, fetched_at}` object and a top-level `retention_class` on every message that carries or derives from a platform fetch; `producer` only on internal control messages (recommended).**
   - Meaning: `provenance.service` is the service that fetched the data and `fetched_at` the time it was fetched; `producer.service` (D2-Q002) is the service that emitted this message. The SDK copies `provenance` and `retention_class` from the input record to every derived message (normalized item, hit, analysis, metrics, profile, item-scope deletion), so no service rebuilds them; the `raw.items` envelope carries the same object (D2-Q005).
   - Data messages, with full provenance: `raw.items`, `items.normalized`, `item.hits`, `discovery.hits`, `poster.profiles`, `item.metrics`, `items.analysis`, `article.urls`, `search.results`, `deletions`, `news.dedup`; `crawl.policies`, since it records a fetch of robots.txt; and `registry.decisions` that derive from a fetch (qualifier's decisions from resolver profiles, news-robots-checker's crawl refusal, the canary's `health_change`). A decision entered by a person carries `requested_by` instead.
   - Control messages, `producer` only: the job queues, `jobs.completed` and `source.events`, which carry no platform data.
   - Deletions: an item-scope deletion copies the item's provenance and class. An author-, source- or client-scope deletion derives from no single record (`retention-purger §5.3 L78`, `deletion-propagator §5.3 L60`): it carries the signal's provenance (the service that received the request or compliance signal, its route and vendor, and `fetched_at` = when the signal arrived) and no `retention_class`, the one named exception, since it is kept as an audit row (D2-Q069 (e)).
   - Profiles: a `poster.profiles` message carries the class of the route that fetched the profile, individuals' messages included. The registry columns filled from a profile of a non-individual (name, followers, signals) are registry metadata, refreshed by re-resolution and kept while the source exists, as li-org-resolver says; counsel confirms that reading for LinkedIn under D2-Q055.

   Consequences: one type and one SDK check, and every data message can feed the client-facing provenance statement. This reads CLAUDE.md L11's "every output" as "every data output"; the user confirms that reading, and the repository rules that say "every output" are reworded (Phase 2). The PRD examples change shape (flat to nested) under D2-Q001.

2. **The same five fields flat on every data message (`route`, `vendor`, `service`, `fetched_at`, `retention_class`), the producing service only in `producer`.** Consequences: closest to most raw envelopes today; a flat `service` beside `producer.service` invites the confusion D1 found, and the SDK must copy five fields instead of one object.
3. **Provenance on every message, control messages included.** Consequences: the rules hold word for word, but jobs, completions and `source.events` would carry a route and fetch time for data they do not hold.
4. **Provenance only on `raw.items` and `items.normalized`; derived messages carry `item_id` (or `candidate_key`) and readers join.** Consequences: smaller messages, but every consumer that must show provenance or expire by class has to join.

**Why the recommendation.** Provenance exists so that whatever reaches a client can say where the data came from and how long it may live; that applies to every message derived from a fetch, and to nothing in a job or a completion report. The nested object is the only form the SDK can stamp, copy and validate as one unit.

**Phase 2 records.** ADR "Provenance and retention class on messages" (Applies to: all). CONVENTIONS v1.1, L115 and the event bus section: the object, the field meanings, the list of data and control messages, the deletion exception. Rewordings, each citing the ADR (CLAUDE.md is the user's file, so the text is proposed for the user to apply): `CLAUDE.md` L11, "Every data output (a message that carries or derives from a platform fetch) carries provenance (route, vendor, service, fetched_at) and `retention_class`; job and control messages carry `producer`."; F2 brief L36, "Every data payload carries provenance (route, vendor, service, fetched_at) and retention_class; jobs, `jobs.completed` and `source.events` carry `producer` (ADR 'Provenance and retention class on messages')"; `build-plan/README.md` L40, `.claude/skills/review-session/SKILL.md` L22 and `.claude/agents/prd-reviewer.md` L16, "every data output" in place of "every output" and "outputs".

### D2-Q004 · Partition keys for topics and job queues

- **Class:** technical
- **Settles:** CF-003, CF-087, AU-019, deletion-propagator §14 Q4
- **Blocks:** F2, F4, F5, F6, then C4, C5, C6, C8, C13, C14, A1, A2, A3, A4, FB1, FB6, IG1, IG2, VTT1, VTT2, VTT3, X2, X4, X7, VLI1, VLI2, VTG1, VTG2, YT1, YT7, YT8, N1, N2, N7, W1, W2, W3, W4
- **Depends on:** D2-Q010 (the name `author_ref`), D2-Q031 and D2-Q033 (the keys of `discovery.hits` and `poster.profiles`), D2-Q032 (candidate keys), D2-Q044 (keyword-rule rows)

**Context.** CONVENTIONS partitions every topic "by `source_id` unless noted" and notes nothing (L14), and every job queue by `source_id` "so one source is never worked twice at once" (L28). Writers chose other keys for good reasons (CF-003 b to g, CF-087 b to d): `search.results` by `canonical_url_hash`, so every engine's sighting of a URL reaches one router partition (`web-search-perplexity §6.2 L90`); `crawl.policies` by `host` (`news-robots-checker §6.2 L93`); `news.dedup` by `story_id` (`news-dedup §6.2 L84`); author-scope `deletions` by the author hash (`retention-purger §6.2 L94`); `registry.decisions` by `candidate_key` or `source_id` (`qualifier §6.2 L81`); resolver queues by `candidate_key` (`fb-page-resolver §5.1 L42`); fb-page-search by `keyword_id` (`fb-page-search §5.1 L40`). Others name none: the canary's decisions, tg-message-search's keyword sets (`tg-message-search §5.2 L51`) and the ops jobs.

One point is a real disagreement (CF-003 h, AU-019). normalize-item has search finds "keyed by the producer on `<platform>:<poster platform_id>`" (`normalize-item §5.1 L41`), and keyword-matcher and store-writer follow (`keyword-matcher §5.1 L40`, `store-writer §5.1 L39`); CONVENTIONS sets a find's `source_id` to "the keyword-rule or hashtag source that produced the query" (L281), as the approved search producers do (`ig-hashtag-search §6.2 L91`, `tt-keyword-search §6.2 L73`), while li-post-search sets none (`li-post-search §6.2 L87-L94`) and the web engines write `web:<source_id>` (`web-search-perplexity §6.2 L89`). At stake: the SDK producer sets the key, so a key the contract does not name cannot be produced, and readers that assume `source_id` mis-order the rest.

**Options**

1. **One declared key per topic and per queue, `source_id` by default, the exceptions named (recommended).** F2 records the key of every topic and queue, per scope or kind where one carries several subjects; the SDK producer sets the Kafka key from that record, never from the caller. `source_id` stays required on every message and job about a source.
   - Topic exceptions: `search.results` by `canonical_url_hash`; `crawl.policies` by `host`; `news.dedup` by `story_id`; `deletions` by `author_ref` for author scope and `client_id` for client scope; `registry.decisions` by `candidate_key` about a candidate, `source_id` about a source, `platform` for a route-level `health_change`; `discovery.hits` and `poster.profiles` by `candidate_key` (D2-Q031, D2-Q033), as are `raw.items` records about a candidate not yet a source (D2-Q005); `jobs.completed` by the key of the job it reports.
   - Search finds: every search producer sets `source_id` to its keyword-rule or hashtag row (li-post-search adds it, the web engines drop `web:`), and the poster key goes. A found post's comment jobs carry the post's `source_id`, so post and comments still share a partition.
   - Queue exceptions: the eight resolver queues and `jobs.poster-resolver` by `candidate_key` on every job, a registered source's `refresh` carrying its `<platform>:<platform_id>` key, so registration does not move an account; `jobs.news-robots-checker` by `host`; `rematch` by `client_id`; `replay`, `rerun`, `recompute` and `retention_sweep` by their `request_id` or `run_id`, since order does not matter there (`aggregator §5.1 L37`). fb-page-search and tg-message-search key on their keyword-rule row's `source_id` (D2-Q044; tg-message-search already calls its set a `keyword_rule` row, `§5.1 L41`), and an X gap job on its rule's first source (`x-filtered-stream §5.2 L70`), so both are the default.

   Consequences: five approved PRDs change under D2-Q001 (normalize-item, li-post-search, web-search-perplexity, fb-page-search, tg-message-search); keyword-matcher and store-writer drop the poster key; a post found by two rules can reach two normalize-item workers, which derive the same `item_id` (D2-Q006), so the stores upsert one item.

2. **As 1, with the poster key also allowed on `items.normalized` and the hit topics when `source_id` is absent (CF-003 option 2).** Consequences: no search producer changes, but three topics carry two keys and every consumer handles both.
3. **`source_id` on everything (CF-003 option 3, CF-087 option 2).** Candidates, hosts, stories, authors and ops runs get a registry row or a synthetic id. Consequences: one key, but registry rows for things that are not sources, and the per-host and per-story order the news services rely on is lost.
4. **A free `partition_key` field set by each producer (CF-087 option 3).** Consequences: flexible, but nothing says which key a queue uses, so its producers can disagree again.

**Why the recommendation.** It keeps CONVENTIONS' default and search output rule, records the exceptions the writers chose for good reasons (order per host, story or candidate), and lets the SDK, not each service, set the key.

**Phase 2 records.** ADR "Partition keys" (Applies to: all). CONVENTIONS v1.1: L14 and L28 gain the key table and the rule that a message or job about no source names its key in the contract; L281 adds that the search `source_id` is also the partition key; normalize-item §5.1 L41 and §6.2 L91, keyword-matcher §5.1 L40 and store-writer §5.1 L39 lose the poster key.

### D2-Q005 · The `raw.items` message: shape, envelope fields, and why a record was read

- **Class:** technical
- **Settles:** CF-004, CF-005, CF-006, AU-002, AU-015
- **Blocks:** F2, F4, F6, C2, C4, C10, C11, then every `raw.items` producer (D1 names FB4, IG2, VTT1, VTT2, X1, YT8, VTG1, W1, W2, W4, N6, TG1, TG2, X4, X5, VLI1, YT4, N8, FB3, FB7, IG3, IG4, IG5, VIG1, VFB1, VFB2, VTG3, YT2)
- **Depends on:** D2-Q002, D2-Q003, D2-Q006 (who computes the key), D2-Q008 (the record kinds)

**Context.** Most producers write a nested `{"envelope": {...}, "payload": {...}}` message (`fb-page-feed-poller §6.2 L110-L126`, `ig-account-media-poller §6.2 L106-L123`, `li-post-search §6.2 L85-L102` and others); ig-hashtag-search and yt-keyword-search write flat fields with the record under `payload`; tt-keyword-search, tt-hashtag-feed-poller and x-recent-search under `raw` and `includes`; the web engines and tg-message-search give only a prose list (CF-004). The readers assume nesting: raw-archiver reads `envelope.raw_ref` and writes an envelope file and a payload file (`raw-archiver §5.2 L50`, `§5.3 L67`), normalize-item "read[s] the envelope" (`normalize-item §5.2 L49`). Both shapes are on the approved list. The envelope's fields differ too (CF-005): the usual set (`fb-page-feed-poller §6.2 L112-L123`) is missing pieces in a dozen producers; normalize-item selects its mapper by `(service, api_version)` and reads `job_kind`, but `api_version` is written by two producers and `job_kind` by four (CF-005 d); producers stamp `retention_class` while normalize-item stamps it again "(source row, else route and platform default)" (`normalize-item §5.2 L55`; CF-005 c); raw-archiver needs `raw_ref` (`<object key>#<line>`, allocated by the SDK, `raw-archiver §11 L157`) where 33 producers write `batch`; and some twenty producer-specific fields (`edge`, `window`, `matching_rules`, `url_key` and others) have no shared definition. Some records cannot fill that set: resolver profiles of candidates have no `source_id` yet (`poster-resolver §5.2 L58`, `§6.2 L92`; `tg-channel-resolver §5.2 L57`; `tt-user-resolver §5.1 L41`), the web engines write one record per API response with no `platform_id` or `idempotency_key` (`web-search-perplexity §6.2 L89`), and the stream writes `"job_id": null, "attempt": null` (`x-filtered-stream §6.2 L121`). Why a record was read travels as `metrics_observation`, `job_kind`, `origin`, `delivery` or `ingest_mode` (CF-006): the first two have three readers between them (fb-reactions-fetcher labels observations from `metrics_observation`; normalize-item reads `job_kind`, and comment-decay-scheduler expects `job_kind = backfill` "carried from the raw envelope" onto `items.normalized`, `comment-decay-scheduler §5.1 L66`; AU-002, AU-015); `origin`, `delivery` and `ingest_mode` have none (CF-006 c).

**Options**

1. **Nested `{envelope, payload}` for every producer, one envelope type built by the SDK with conditional fields, and one `job_kind` (recommended).**
   - Shape: `payload` holds the platform record as returned (minus identities, D2-Q010), with `includes` and other response parts inside it; the envelope holds everything else.
   - Envelope, always required: `platform`, `kind` (the record kind from D2-Q008, archive-only kinds such as `profile` and `search_response` included), `provenance` (D2-Q003), `retention_class`, `client_ids`, `job_id`, `attempt`, `job_kind`, `api_version`, `raw_ref`; plus `schema`, `message_id`, `produced_at`, `producer` (D2-Q002).
   - Required by condition: `source_id`, or `candidate_key` for a record about a candidate that is not yet a source (D2-Q004 names `candidate_key` as that record's key); `platform_id` and `idempotency_key` for item kinds, while archive-only kinds carry a defined key instead (for `search_response`, the rule's `source_id` plus the request time); on push and stream records, a `job_id` made at receipt (a ULID, D2-Q006) with `attempt = 1`, the delivery id (`update_id`, `connection_id`) going in `context`; on a comment, `parent_id`, `root_id` and the optional `redacted_fields`, as D2-Q009 defines them.
   - Optional: a typed `context` object, its keys declared per producer in the contracts package (the producer-specific fields go there, each defined). `batch` is dropped: `raw_ref` names the object and line.
   - The SDK producer fills the envelope from the job and the adapter, and stamps `retention_class` from the source row, else the route and platform default; normalize-item copies it. Services hand over the payload and the adapter's fields, never a hand-built envelope.
   - `job_kind` is the job's `kind` (for jobless receivers and the stream, the fixed values `push` and `stream`); it travels onto `items.normalized`, which is how backfilled records are recognised (AU-002, AU-015). `metrics_observation`, `origin`, `delivery` and `ingest_mode` are dropped; `item.metrics` labels derive from `job_kind` and the series step (D2-Q034).

   Consequences: one contracts type that all 48 producers can satisfy; raw-archiver and normalize-item work as written; the five flat-shape approved PRDs change their examples under D2-Q001.

2. **Flat records with reserved top-level envelope names and the platform record always under `payload`.** Consequences: shorter messages; raw-archiver and normalize-item change how they split and read; reserved names can collide with platform fields.
3. **Both shapes on the wire, the SDK wrapping flat records before publishing.** Consequences: no PRD changes, but the SDK carries two input shapes forever, and fixtures must cover both.

   The envelope and label alternatives D1 named, rejected with option 1: a small required set with key and class computed downstream by normalize-item (CF-005 option 2; the key then differs by who computes it, CF-060); a required set per route family (CF-005 option 3; three envelope types where one with conditions does); `metrics_observation` as the one label, or both fields (CF-006 options 2 and 3; `job_kind` and the series step already say what the counts are).

**Why the recommendation.** It is the majority shape and the one both readers expect; an SDK-built envelope with written conditions removes the missing fields at their source; one `job_kind` answers "why was this read" for every consumer.

**Phase 2 records.** ADR "The raw.items message" (Applies to: F2, F4, F6, all `raw.items` producers, raw-archiver, normalize-item, listening-sdk). CONVENTIONS v1.1, L15: the shape, the required, conditional and optional envelope fields, `raw_ref`, `job_kind` and its fixed values.

### D2-Q006 · Identifiers: key authority, `item_id`, `job_id`, client and keyword ids

- **Class:** technical
- **Settles:** FC-03, CF-060, CF-070, CF-071, CF-072
- **Blocks:** F2, F3, F8, then F4, F6, C4, C6, C13, C14, X7, YT7, and every `raw.items` producer
- **Depends on:** D2-Q002 (`message_id`, `producer.job_id`), D2-Q007 (the key forms the golden vectors cover)

**Context.** CONVENTIONS gives the key form `<platform>:<kind>:<platform_id>` (L69) but not who applies it (CF-060). normalize-item "assigns the idempotency key every store relies on" (`normalize-item §1 L9`) from its own mapper (`§5.2 L51`), while most producers stamp a key in the envelope (for example `yt-pubsub-receiver §6.2 L112`), raw-archiver receives it (`raw-archiver §5.4 L86`), and deletion-propagator derives `item_id` "with the SDK helper that normalize-item uses" (`deletion-propagator §5.3 L60`). Where the two keys differ (D2-Q007), dedup, versions and deletions follow whichever wins. The build plan's foundation choice is "a deterministic hash of the idempotency key, with golden vectors in both languages" (FC-03, build plan L53). The formats differ too:

- `item_id` is `uuid_v5(ns_items, idempotency_key)` (`normalize-item §5.2 L51`), but the three deletion producers put ULIDs in their targets (`retention-purger §6.2 L102`, `x-compliance-sync §6.2 L105`, `yt-text-purger §6.2 L149`), values no store holds (CF-071).
- `job_id` is a ULID (CONVENTIONS L277), with deterministic ULIDs where replay needs them (`comment-decay-scheduler §5.3 L84`, `backfill-orchestrator §5.3 L85`), but examples show UUIDs, `job_…`, dated sequences, composites such as `res:x:1234567890` (`poster-resolver §5.3 L67`), `null` (`x-filtered-stream §6.2 L121`) and `update_id` instead (`tg-bot-channel-receiver §6.2 L123`) (CF-070).
- `client_id` and `keyword_id` are UUIDs in most PRDs and `cl_17` or `kw_0412` in a few, approved ones among them (`poster-resolver §6.2 L89`) (CF-072).

**Options**

1. **One key helper in the contracts package, run by producers and checked by normalize-item; uuid v5 item ids; ULID job ids; UUID client and keyword ids (recommended).**
   - Authority (CF-060): the producer stamps `idempotency_key` with the contracts package's helper (TypeScript and Python twins), from the record and the envelope fields a key needs (the post reference of an id-less comment). normalize-item recomputes it with the same helper and parks a mismatch as `schema_unknown` (`normalize-item §5.2 L50`); deletion-propagator and x-compliance-sync derive keys with the same helper; nothing downstream edits a key.
   - `item_id` (FC-03, CF-071): `uuid_v5(ns_items, key)` everywhere, `ns_items` one UUID constant frozen in the contracts package; deletion targets carry these ids. Byte rules for the golden vectors: the key is the UTF-8 bytes of its NFC form; platform and kind segment in lower case; the id rendered as D2-Q007 says; a hash inside a key is SHA-256 over NFC text, 64 lower-case hex, with times as UTC `YYYY-MM-DDTHH:MM:SSZ`; a hash over structured data uses canonical JSON (RFC 8785). Vectors cover every key form of D2-Q007, decomposed Arabic, emoji and the id-less comment key.
   - Other deterministic ids follow the same two patterns: a uuid v5 under its own frozen namespace (`hit_id`, `keyword-matcher §5.3 L77`), or a ULID whose time part is the event's own time and whose random part is the first 10 bytes of SHA-256 over a declared input (`comment-decay-scheduler §5.3 L84`). keyword-matcher's replay-stable `message_id` becomes such a ULID (time `hit_at`, input `hit_id`, `item_version`, `keyword_set_version`).
   - `job_id` (CF-070): a ULID on every job, deterministic where replay needs it; a record made without a job (the push receivers, x-filtered-stream) gets a ULID at receipt with `attempt = 1`, as li-notification-receiver does (`§6.2 L133`), and `update_id` and `connection_id` move into the producer's declared context (D2-Q005); `producer.job_id` (D2-Q002) carries the ULID of the job behind the message, copied by topic consumers, never a composite or `null`.
   - `client_id`, `keyword_id` (CF-072): UUIDs in messages, tables and the budget tags that embed a client (`meta_graph_pages:<client_id>`, CONVENTIONS L279; lower-case canonical form, D2-Q042); a keyword-rule source is named by its `source_id` (D2-Q044); the prefixed forms are example errors.

   Consequences: one implementation tested byte for byte in two languages; a producer bug parks records instead of silently forking an item; F3 and F8 type the id columns `uuid`; examples with other id formats are corrected in phase 2, approved PRDs among them under D2-Q001.

2. **normalize-item alone computes the key; envelope keys are informational or absent (CF-060 option 2).** Formats as in 1. Consequences: one place to change a key, but producers lose the key they use for their own state (read ledgers, comment hashes, the reconciler's check, `yt-uploads-reconciler §5.2 L63`), raw-archiver files records without one, and a mapper bug forks items unnoticed.
3. **The producer's key is used unchecked and the validators are loosened (CF-060 option 1, CF-070 option 3, CF-072 option 2).** Consequences: fewest edits, but nothing catches two routes keying one object differently (the CF-061 to CF-066 problem), fixtures mix id formats, and F3 types ids as text.

**Why the recommendation.** It makes the build plan's choice concrete: the key is computed by one piece of shared code, checked at the single translation point, and reproducible from either language, so dedup, versions, deletions and replays agree.

**Phase 2 records.** ADR "Identifiers and key authority" (Applies to: all, F2, F3 and F8 included). CONVENTIONS v1.1: L69 and L70 (who stamps and who checks the key, the `item_id` derivation, the byte rules), L277 (`job_id`, deterministic ids, jobless records). F2 writes the helper, the namespaces and the golden vectors.

### D2-Q007 · Item keys per platform

- **Class:** technical
- **Settles:** CF-061, CF-062, CF-063, CF-064, CF-065, CF-066, AU-050, AU-053, ig-keyword-search §14 Q2, ig-mentions-fetcher §14 Q3, tg-channel-posts-poller §14 Q4, x-replies-fetcher §14 Q5
- **Blocks:** F2, F3 (the Instagram id map), then C4, C13, IG2, IG3, IG5, VIG1, VIG2, TT1, VTT1, VTT2, VTT4, VTT5, VTT6, X1, X4, X5, X6, X7, LI1, LI2, LI3, VLI1, VLI3, VLI4, TG1, TG2, VTG1, VTG3, YT2, YT3, YT4, YT8, YT9, W3
- **Depends on:** D2-Q006 (the key helper), D2-Q008 (the kind list), D2-Q009 (the key of a comment without an id)

**Context.** CONVENTIONS keys an item `<platform>:<kind>:<platform_id>` (L69) without fixing the kind word or the id. On six platforms the PRDs differ, so one object read by two routes becomes two items, and what points at it misses:

- YouTube (CF-061): `youtube:post:<id>` in yt-pubsub-receiver, yt-uploads-reconciler and yt-video-details-fetcher (`yt-video-details-fetcher §9 L180`); `youtube:video:<id>` on the approved side: yt-keyword-search (`§6.2 L102`), normalize-item (`§5.3 L71`), yt-web-search-bridge's `extracted.kind` (`§6.2 L121`).
- TikTok (CF-062): `tiktok:video:<id>` in six PRDs, under envelope `kind` `post` (`tt-client-videos-fetcher §6.2 L99`) or `video`; `tiktok:post:<aweme_id>` in normalize-item (`§5.3 L67`).
- X (CF-065, AU-050): `x:post:<id>` in five readers, the approved x-recent-search (`§5.2 L57`) and normalize-item (`§5.3 L68`) among them; `x:comment:<id>` in x-replies-fetcher (`§6.2 L115`).
- Telegram (CF-063): `telegram:post:<username>/<id>` and `telegram:comment:<group chat id>/<id>` in the four content PRDs (`tg-message-search §5.2 L54`); `telegram:message:<chat_id>:<id>` in normalize-item (`§5.3 L70`).
- LinkedIn (CF-064): a share URN on the green route (`li-client-posts-poller §6.2 L114`), an activity URN or a URL hash (`li-post-search §6.2 L91`, `L105`), a bare id (`li-company-posts-poller §6.2 L111`).
- Instagram (CF-066, AU-053): Graph media ids on the green routes and in normalize-item (`ig-hashtag-search §6.2 L91`, `normalize-item §5.3 L66`); vendor ids that "may differ from Graph ids" (`ig-keyword-search §9 L144`).

**Options**

1. **The majority form per platform, the kind segment equal to the item kind of D2-Q008 (recommended).** Keys split on the first two colons only, so the id may hold `:` or `/`; adapters build them with the shared helper (D2-Q006).
   - YouTube: `youtube:video:<videoId>`, `youtube:comment:<id>`; partial and full records share the key (D2-Q065); the three `youtube:post:` PRDs move. search-hit-router's candidate key and the bridge's `extracted.kind` are not item keys.
   - TikTok: `tiktok:video:<id>`, `tiktok:comment:<cid>`; normalize-item, the two `kind: post` envelopes and retention-purger's TikTok target (`§6.2 L102`) move.
   - X: `x:post:<id>` for every tweet; x-replies-fetcher and x-full-archive-search's replies move. Compliance signals name a tweet by its id alone (`x-compliance-sync §5.3 L81`), so the key never depends on whether it is a reply; the reply link is `parent_id` (D2-Q009) and its item kind `comment` (D2-Q008), the one exception to the segment rule.
   - Telegram: `telegram:post:<lowercase username>/<message_id>` for channel posts, `telegram:comment:<group chat id>/<message_id>` for discussion messages; a channel without a username uses its chat id. Every route has the username: the Apify Actors are fed usernames (`tg-channel-posts-poller §5.2 L62`), Telemetrio returns the username (`tg-channel-resolver §5.4 L67`), the bot knows both (`tg-bot-channel-receiver §5.2 L60`); VTG0, which could show otherwise, runs after F2 freezes keys. Risks: a renamed channel's posts can duplicate on a re-read (`tg-message-search §5.1 L44`), and a reused username can collide with the old channel's posts. normalize-item moves.
   - LinkedIn: the activity URN, `linkedin:post:urn:li:activity:<id>` and `linkedin:comment:urn:li:comment:(urn:li:activity:<post id>,<comment id>)`. Every amber route has it (`li-post-search §5.4 L71`; li-company-posts-poller's `id` is the number in its post URL, `§5.4 L83-L84`), so the URL hash and the bare ids go. The green adapter converts its share URN, kept as an attribute. LI0 confirms where the green API gives the activity URN; if nowhere, green keeps share-URN keys and no amber route reads a client-administered page (li-company-posts-poller already stops, `§3 L26`; li-post-search drops such posts). normalize-item moves.
   - Instagram: `instagram:post:<Graph media id>`, as both approved parties key posts, and `instagram:comment:<id>`. Vendor records map to the Graph id through a shared Instagram id map (shortcode, Graph media id, key), written only by the key helper and fed by the `permalink` of Graph reads (CONVENTIONS L166, L167); VIG0 checks whether the vendor returns Graph ids. A post only the vendor has seen gets a proposed shortcode key, `instagram:post:sc:<shortcode>`, from its `permalink` (`ig-keyword-search §5.4 L78`), which a Graph route that later reads the shortcode reuses. Instagram keys therefore depend on the map, not on the record alone; their golden vectors test the lookup rule. An id-less vendor comment takes D2-Q009's hash key.
   - Unchanged here: Facebook; news (D2-Q036); web items `web:result:<canonical_url_hash>` (D2-Q038).

   Consequences: F2 writes golden vectors per platform; the PRDs named above change, normalize-item (approved) under D2-Q001; F3 creates the Instagram id map.

2. **Keys from the record alone: the Instagram shortcode (AU-053 option 1) and the Telegram chat id (CF-063 option 2).** Consequences: no id map and rename-proof Telegram keys, but both approved Instagram parties move, Graph-only paths must look the shortcode up, and the Telegram vendor routes need a chat id no PRD shows them receiving.
3. **Route-specific keys joined in normalize-item (CF-064 option 3, CF-065 option 3, CF-066 option 1).** Consequences: no producer changes, but `item_id` stops being a function of one key, so the deletion paths and replays of D2-Q006 cannot derive it.

**Why the recommendation.** It keeps the forms most PRDs and the approved ones use, picks the id every route can see, and confines the one stateful fallback to Instagram, pending the vendor probe.

**Phase 2 records.** ADR "Item keys per platform" (Applies to: F2, F3, every platform service, normalize-item, deletion-propagator, x-compliance-sync, listening-sdk). CONVENTIONS v1.1: L69 gains the per-platform table and the parse rule; the Instagram id map joins the table list (L30). LI0 and VIG0 confirm the LinkedIn and Instagram assumptions.

### D2-Q008 · Item kinds and normalize-item's mappers

- **Class:** technical
- **Settles:** CF-008, CF-068, AU-052, web-search-perplexity §14 Q5
- **Blocks:** F2, F4, then C2, C4, C5, C6, C8, FB7, LI3, VLI2, VIG1, VTG2, VTG3, X6, YT2, YT3, YT4, YT8, N8, W1, W2, W3, W4
- **Depends on:** D2-Q005 (the envelope), D2-Q007 (the keys), D2-Q038 (web items), D2-Q065 (partial YouTube records)

**Context.** CONVENTIONS lists no item kinds, and `kind` names both the item in a key (L69) and the job (L277). Three consumers branch on the item kind: store-writer files "`comment` or `reply`" in `comments` (`store-writer §5.2 L47`); keyword-matcher sends unregistered "post, video, article, message, result" to discovery and "Comments, replies" to mentions (`keyword-matcher §5.3 L74`, `L75`); comment-decay-scheduler opens series on `kind = post` (`comment-decay-scheduler §5.1 L42`). Producers write `post` or `video` for a video, `post` or `message` on Telegram, `comment` or `reply` for an X reply, and normalize-item's `quote` fits neither keyword-matcher branch (CF-068 a to d).

normalize-item parks any record without a mapper "by `(service, api_version)`" as `schema_unknown` (`normalize-item §5.2 L50`), yet eight producers have none (CF-008 b, AU-052 b), three record kinds are not content (`profile`, `poster-resolver §6.2 L92`; `reaction`, `li-notification-receiver §5.4 L98`; `search_response`, `web-search-perplexity §5.2 L55`), and partial YouTube records expect a hold normalize-item lacks (`yt-pubsub-receiver §6.2 L124`). At stake: those batches park for ever, and a kind one consumer does not list is dropped or misfiled.

**Options**

1. **Five content kinds, four archive-only record kinds, and a mapper registry (recommended).**
   - Content kinds, which are also the key's kind segment (D2-Q007): `post`, `video`, `comment`, `article`, `result`. `post`, `video`, `article` and `result` are top-level; `comment` is reply-level and always has a `parent_id` (D2-Q009). `video` is YouTube's and TikTok's; `result` is D2-Q038's web item, keyed `web:result:<canonical_url_hash>`. Platform nouns become attributes: normalize-item's `reply` is a `comment` with a parent; an X quote is a `post` with the quoted tweet's `item_id` in `quoted_id`; Telegram's `message` is a `post` in a channel and a `comment` in its discussion group. An X reply is a `comment` keyed `x:post:<id>` (D2-Q007), the one place where the key segment and the kind differ: X has one object type for every tweet, and as a `post` a reply would open its own paid series, send its author to discovery and be filed in `items`.
   - Consumers: store-writer files `comment` in `comments`, the rest in `items`; keyword-matcher sends unregistered top-level items, quotes included, to discovery and comments to mentions; comment-decay-scheduler opens series on `post` and `video` (and `article` on Disqus sites, D2-Q061).
   - Archive-only record kinds: `profile` (each resolver archiving its own lookups, D2-Q032), `reaction` (li-notification-receiver; counts come from li-client-posts-poller's absolute reads, D2-Q034), `search_response` (the web engines; `kind_hint` and `normalize = skip` go, D2-Q037) and `metrics` (a refresh read archived by a metrics service that writes its own `item.metrics`, D2-Q034). raw-archiver keeps them; normalize-item acknowledges and counts them and never parks them.
   - Mappers (CF-008 a, b; AU-052 a, b, d): a registry in listening-sdk keyed `(service, api_version)`, each mapper written with its producer's fixtures and run by normalize-item; a record with neither a mapper nor an archive-only kind parks as `schema_unknown`. Where a service reads several vendor schemas, `api_version` names the one used, so `vendor` never selects the mapper (`tg-channel-posts-poller §8 L149`). New mappers: yt-pubsub-receiver, yt-uploads-reconciler, yt-keyword-search, ig-keyword-search, news-comments-fetcher, li-notification-receiver's comments, li-org-resolver's sampled posts (`li-org-resolver §13 L159`) and fb-client-webhook-receiver's posts.
   - Partial YouTube records (CF-008 d): the details record completes the partial one as a new version of the same key, with no hold (D2-Q065). Web results (AU-052 c): search-hit-router writes the `result` items of D2-Q038 to `raw.items`, mapped by normalize-item's web line.

   Consequences: one enum in F2 and three consumers aligned; normalize-item (approved) reads its table from the registry, under D2-Q001; each producer's session writes its mapper; web-search-perplexity's question (`§14 Q5 L174`) is answered: archive-only.

2. **`post` for every top-level platform item, `video` only an attribute.** Consequences: consumers test fewer words, but three approved PRDs (tt-keyword-search, tt-hashtag-feed-poller, yt-keyword-search) and normalize-item's YouTube line move, and every video key changes (D2-Q007).
3. **Only content on `raw.items`: profiles, reactions and search responses move to their own paths (CF-008 option 2, CF-068 option 2).** Consequences: normalize-item sees only items, but raw-archiver gains three write paths with their own replay rules, and reactions need a writer on `item.metrics`.

**Why the recommendation.** It keeps the words most producers and the approved PRDs already use, gives every consumer one rule for top-level and reply-level items, and turns "parked for ever" into an explicit skip for records that were never meant to become items.

**Phase 2 records.** ADR "Item kinds and mappers" (Applies to: F2, every `raw.items` producer, normalize-item, store-writer, keyword-matcher, comment-decay-scheduler, raw-archiver, listening-sdk). CONVENTIONS v1.1: the content and archive-only kinds beside L15 and L69; L103 adds that an archive-only kind is skipped, not parked.

### D2-Q009 · Comment records: fields, content hash, edits

- **Class:** technical
- **Settles:** CF-007, CF-067, AU-049, AU-090, RN-13
- **Blocks:** F2, F4, then C4, C6, C13, FB5, FB7, VFB3, IG4, IG6, VIG2, LI2, LI3, VLI4, VTT5, X6, YT5, YT6, N8, TG1, TG2
- **Depends on:** D2-Q006 (the key helper), D2-Q007 (keys), D2-Q010 (what an adapter removes), D2-Q062 (deletion on absence)

**Context.** Every comment producer spells the same four facts its own way (CF-007): the parent link (`parent_platform_id`, `post_ref`, `parent_post_id`, `parent_video_id` and more); the content hash (`text_hash` in bare hex, `content_hash` with a `sha256:` prefix, `text_sha256`); the edit marker (`edit_of`, `version`, `observation`, `event`); and the redaction marker (`payload_redacted`, `removed_fields`, `minimized`, `identity: "hashed"`). normalize-item reads none of them and derives its own (`normalize-item §5.2 L49`, `L51`, `§5.3 L70`).

The Instagram fetchers hash "the SHA-256 of its `text`" (`ig-own-comments-fetcher §5.1 L49`) and compare it with normalize-item's stored `sha256(title + text + media urls)` (`normalize-item §5.2 L51`), so a comment with a media URL looks edited at every read (AU-090). CONVENTIONS says "changed text becomes a new version" (L63) but keys comments without platform ids on their text (L69), a form three vendor routes also use (`fb-group-comments-fetcher §5.4 L94`, `ig-comments-fetcher §6.2 L115`, `li-post-comments-fetcher §6.2 L129`) (CF-067 a, d). fb-post-comments-fetcher sends an edited PPCA comment under a new key with `edit_of` and expects a version (`§5.2 L68`), which normalize-item never reads (AU-049); news-comments-fetcher puts the version in the key, `news:comment:6203918455:v1` (`§6.2 L101`); the routes with ids keep the key (`fb-group-comments-fetcher §5.2 L65`, `tg-discussion-receiver §9 L163`) (CF-067 b, c). At stake: double-counted comments, false edits, and a parent link no reader can rely on.

**Options**

1. **One comment field set, one hash helper, versions under one key where the platform gives ids, and a new comment where it gives none (recommended).**
   - Fields (CF-007 a), normalize-item's names on `items.normalized`: `parent_id`, the parent's `item_id` (the post for a top-level comment, the parent comment for a reply); `root_id`, the post's `item_id`; `parent_seen` for orphans (`normalize-item §5.1 L43`); `content_hash`; `version`. A comment's `raw.items` envelope carries `parent_id` and `root_id`, stamped by the producer from the job's `post_ref` (D2-Q011) and the key helper, since PPCA and vendor payloads name no post; normalize-item checks them where the payload has a reference. The envelope spellings above go.
   - Redaction (CF-007 d): `redacted_fields`, one optional envelope field on any record: the payload paths an adapter removed or replaced (what it removes is D2-Q010's).
   - Hash (CF-007 b, AU-090): one SDK helper, `content_hash = "sha256:"` plus the hex SHA-256 of the NFC text, preceded by the NFC title and U+001F when the item has a title. A comment has none, so its hash covers its text only; media URLs are left out, since signed URLs change. Producers hash their registered mapper's output (D2-Q008), so both sides hash the same string.
   - Edits where the platform gives a stable id (CF-067 c, d): the key stays and normalize-item publishes `version + 1` when the hash changes (`normalize-item §5.2 L52`); producers send no edit marker (those above and `is_edited` go; the platform's edit time stays in the payload); news-comments-fetcher drops its `:vN` suffix. RN-13: D1 notes that CF-067 c) cites `tg-bot-channel-receiver §9 L159`, a post line; the rule covers posts too, and that line agrees.
   - Edits where the platform gives none (CF-067 a, b, AU-049): the CONVENTIONS hash form becomes the rule for every id-less comment route, `<platform>:comment:<post id>:<sha256(created_time + text)>`, so changed text is a new comment. The old key becomes a `deletions` message (reason `platform_sync`) under D2-Q062's confirmed-miss rule, and on a route that never deletes on absence (Instagram vendor comments) the old text stays until retention removes it. fb-post-comments-fetcher drops `edit_of` and its `superseded` outcome (`§5.2 L68`, `§13 L176`), fb-group-comments-fetcher its id-less `superseded` (`§5.2 L65`). Vendor probes first confirm that creation times are stable across reads.

   Consequences: one field set and one helper in F2, with golden vectors; normalize-item (approved) changes its hash formula under D2-Q001; an edited id-less comment shows as one deletion plus one new comment, counts stay right, the link between the texts is lost.

2. **As 1, but id-less edits linked: the fetcher keeps `edit_of` and normalize-item publishes the new text as a version of the old key's `item_id` (CF-067 option 1, AU-049 option 1).** Consequences: an edit stays one item, but `item_id` stops being derivable from the key (D2-Q006), and two real comments can be merged, since "an edit cannot be told from two comments written in the same second" (`fb-post-comments-fetcher §5.2 L68`).
3. **No comment fields in the envelope: normalize-item derives parent, hash and version from the payload (CF-007 option 2).** Consequences: thinner envelopes, but PPCA and vendor payloads name no post, so those comments cannot be placed, and producers still need the hash.

**Why the recommendation.** One helper on both sides ends the false versions AU-090 found; one key with versions is what CONVENTIONS L63 and normalize-item already do; where no platform id exists, nothing reliably links old and new text, so the record shows one comment gone and one new.

**Phase 2 records.** ADR "Comment records, content hash and edits" (Applies to: F2, every comment fetcher and receiver, normalize-item, store-writer, deletion-propagator, listening-sdk). CONVENTIONS v1.1: L63 (versions where ids exist; an id-less edit is a new comment plus a deletion), L69 (the hash form for every id-less comment route), the comment fields and `redacted_fields` with the envelope (D2-Q005). RN-13 is closed by this record.

### D2-Q010 · Individuals' identities: one keyed reference, and where it is computed

- **Class:** user (how far the platform can link one person's activity, and whether the raw archive may hold their identity, are privacy choices behind the rule "individuals are never profiled")
- **Settles:** CF-069, CF-109, AU-048, AU-089, fb-group-posts-poller §14 Q5, ig-comments-fetcher §14 Q2, li-notification-receiver §14 Q5, li-post-comments-fetcher §14 Q5, news-comments-fetcher §14 Q4, normalize-item §14 Q1, tg-discussion-receiver §14 Q4, tt-user-resolver §14 Q3, tt-video-comments-fetcher §14 Q4, x-replies-fetcher §14 Q6, yt-comments-fetcher §14 Q4
- **Blocks:** F2 (the helper and its golden vectors), F3 (the `poster_profiles` hash column), F8 (ClickHouse `author_ref`), F4, F6, C2, C4, C6, C7, C8, C9, C13, C14, X7, and every fetcher that writes people's ids: VTT3, VTT5, VTT6, X6, YT5, YT6, FB7, VFB1, VFB2, VFB3, VIG1, VIG2, IG4, IG5, IG6, LI2, LI3, VLI4, TG2, N6, N8
- **Depends on:** D2-Q005 (the `raw.items` envelope that carries the reference)

**Context.** Individuals are never profiled and a mention keeps a hashed author reference (CONVENTIONS L114, L248). The PRDs implement it five ways (CF-069):

- normalize-item: `author_ref = hmac_sha256(AUTHOR_HASH_KEY, platform + ':' + author_platform_id)` (`normalize-item §5.2 L54`), stored and carried as `author_ref` (`store-writer §6.2 L110`, `keyword-matcher §6.2 L111`).
- poster-resolver: `author_hash = sha256(platform || platform_id || salt)` (`poster-resolver §5.2 L59`), carried by qualifier and registry-writer; the deletion paths use normalize-item's helper but search a column `author_hash` (`retention-purger §5.3 L78`, `x-compliance-sync §5.3 L81`, `deletion-propagator §5.3 L60`) that no writer fills.
- Eleven fetchers hash at the edge, each with its own name and rendering (CF-069 d, AU-048), against "every record exactly as a fetch or push returned it" (`CONVENTIONS L15`); README decision 8 excepts only TikTok commenters (`README L185`; CF-109 b); other routes keep identities raw (`ig-own-comments-fetcher §7 L139`).
- Some scope the hash, so one person gets several references: per YouTube channel (`yt-comments-fetcher §5.2 L56`, `§14 Q4 L206`), per X source (`x-replies-fetcher §5.2 L59`), per Disqus thread (`news-comments-fetcher §5.3 L76`).
- Resolvers answer for individuals with `candidate_ref`, a plain `candidate_key_hash`, or the clear `candidate_key` (CF-069 f).

ig-comments-fetcher asks for one shared key (`§14 Q2 L179`); tt-video-comments-fetcher and tg-discussion-receiver ask whether normalize-item accepts a reference computed at the edge (`§14 Q4 L184`, `§14 Q4 L201`). Also open: whether unregistered business accounts keep their identity (`ig-webhook-receiver §7 L135` against `normalize-item §5.2 L54`; AU-089), and what `raw.items` holds for services that write an extract or no raw record (`news-article-extractor §5.3 L75`, `tt-user-resolver §13 L165`, `tt-video-stats-refresher §6.2 L112`; CF-109 c, d).

**Options**

1. **One platform-wide keyed reference, computed at the edge for everyone who can never become a source (recommended).**
   - One SDK function, in both languages with golden vectors: `author_ref = HMAC-SHA256(AUTHOR_HASH_KEY, "<platform>:<author platform id>")`, 64 lower-case hex; one name, `author_ref`, everywhere (`author_hash`, `candidate_ref` and `candidate_key_hash` renamed; an approved PRD moves under D2-Q001). The key lives in Vault and is rotated only after a compromise; the new key covers new data, and a deletion by author tries every key still covering retained data.
   - Not scoped, so deletion by author and distinct-author counts work. The safeguard is on the query side: no client-facing view, export or query lists or ranks individual references, and YouTube rollups follow D2-Q056.
   - Where: the adapter replaces every commenter's, replier's, reactor's and member's identity before the first write, on every route (README decision 8 widened). normalize-item passes an edge `author_ref` through as given and computes it with the same helper for posters whose ids are still clear (AU-048). Registered sources keep `author_source_id` (an SDK registry-cache lookup) and are the only authors with a name downstream (AU-089 option 1). Discovery posters keep their platform id until poster-resolver classes them; once classed individual, raw-archiver replaces the id in the archive through the deletions' rewrite path, and the resolver's answer carries `author_ref` only, with no clear `candidate_key` (`tt-user-resolver §6.2 L111`, `§14 Q3 L171`).
   - `raw.items` is "the record as returned, minus identities"; news articles are an extract by rule (copyright). tt-user-resolver writes no raw record because its answers are mostly about individuals, whose profiles are never kept; tt-video-stats-refresher writes none because its reads are counts of archived videos, carried by `item.metrics`, so it parks an unknown reading.

   Consequences: no individual's clear identity is stored past classification, except on the event bus: discovery posters' ids sit in `raw.items`, the `discovery.hits` candidate and DLQs until topic retention expires (a setting, kept short). Replays cannot recover identities.

2. **As option 1, plus scoped references for analytics.** The platform-wide reference serves deletions only, in a column no client query reads; analytics rows carry one scoped per source, as x-replies-fetcher and yt-comments-fetcher propose. Consequences: cross-source linking is impossible, not only forbidden; distinct-author counts work only inside one source; two references per person.
3. **CONVENTIONS as written: `raw.items` keeps every record as returned, and only normalize-item hashes.** Edge hashing is reverted, TikTok's included. Consequences: replay can re-derive references, but the archive holds individuals' ids and names for its whole retention (24 months under `vendor_agreed`), against README decision 8.

**Why the recommendation.** It extends what most PRDs and README decision 8 already do, so archive and pipeline treat people alike; one reference keeps deletion by author workable, and the profiling rule is enforced where profiling would happen, in what clients can query.

**Phase 2 records.** ADR "Individuals' identities" (Applies to: all). CONVENTIONS v1.1: L15 ("as returned, minus identities"), L114 and L248 (the function and name, edge minimisation, archive redaction, the bus bound, no per-author view); L103 gains the exception for tt-video-stats-refresher's parked readings; README decision 8's first clause generalised. The function and golden vectors go to F2; the registry-cache lookup to F4 and F6.

### D2-Q011 · The job envelope and the kind list

- **Class:** technical
- **Settles:** CF-074, CF-077, CF-086, AU-036, RN-11, x-full-archive-search §14 Q1, yt-pubsub-receiver §14 Q5, yt-replies-fetcher §14 Q3
- **Blocks:** F2, F4, F5, F6, then C11, FB4, FB5, FB7, VFB3, IG4, IG6, VIG2, LI2, VLI4, VTT5, VTT6, TG2, YT2, YT3, YT4, YT5, YT6, YT7, X1, X5, X6, N8, and every service that consumes or produces a job
- **Depends on:** D2-Q004 (keys), D2-Q006 (`job_id`), D2-Q007 (the id in `post_ref`), D2-Q012 (producers), and the decisions cited for single kinds

**Context.** CONVENTIONS gives a job seven `kind` values and six other fields (L277). The PRDs use about thirty kinds (CF-077 c), name the type `reason` in four approved PRDs (`fb-page-feed-poller §5.2 L54`, `fb-backfill §5.1 L41`, `fb-page-search §5.1 L40`, `x-recent-search §5.2 L53`), send jobs with no type (`tg-message-search §5.2 L51`), and add undeclared fields (CF-077 e). `post_ref` is an object from its only emitter (`comment-decay-scheduler §6.2 L141`) but a different string in each consumer, from `<page-id>_<post-id>` (`fb-post-comments-fetcher §5.1 L42`) to a URN (`li-own-comments-fetcher §5.1 L38`) or nothing (`fb-reactions-fetcher §5.2 L53`) (CF-074, AU-036). Webhook receivers buffer three ways (CF-086): ig-webhook-receiver appends the body as `kind = push` and finds the source afterwards (`§5.2 L55`, `L56`); fb-client-webhook-receiver and yt-pubsub-receiver map the source first and buffer with no kind (`fb-client-webhook-receiver §5.2 L54`, `yt-pubsub-receiver §5.2 L53`); the Telegram and LinkedIn receivers write `raw.items` before answering (`tg-bot-channel-receiver §5.2 L62`). RN-11: `first_run` on `jobs.x-recent-search` has no emitter (`x-recent-search §5.1 L39`). At stake: the SDK wrapper validates every job, so whatever it does not know is refused or slips through.

**Options**

1. **One envelope, one field `kind`, a closed kind list with declared fields (recommended).**
   - Envelope (CF-077 a, b): `job_id` (D2-Q006), `kind`, `source_id` or the queue's declared key (D2-Q004), `due_at`, `attempt` and D2-Q002's metadata; ops and client requests add `request_id` and `requested_by` (D2-Q012). Priority (derived by the SDK, D2-Q018), route and vendor (read from the source row) do not travel in a job. On `raw.items` the job's kind is `job_kind` (D2-Q005). `reason` is never the type; it survives only as a field saying why a job was sent (backfill `add`, `client`, `ops`, D2-Q020; reconciliation `lease_lapsed`, `yt-uploads-reconciler §5.1 L51`).
   - Kinds (CF-077 c to e), fields per kind in F2, producers in D2-Q012: `rotation` (optional `tier`); `reconciliation` (X gap fields, D2-Q064; or `post_ref` for a whole-thread read); `backfill` (D2-Q020); `keyword_history` (D2-Q064); `comments`, `replies` (`post_ref`, `series_step`, `profile`; `thread_ids`, D2-Q060); `metrics` (D2-Q034); `first_sight` (D2-Q065); `refresh` (resolvers' own sources, D2-Q032; news-robots-checker's hosts; yt-text-purger, D2-Q065); `resolve` (D2-Q032); `manual_candidate`; `first_check`, `recheck` (D2-Q022); `ops_force` (optional `post_ref` or `target_ids` for a targeted read); `push`; `replay`, `rerun`, `rematch`, `recompute`; `retention_sweep`; `analyze` (D2-Q023); `candidate_retry`. Dropped: `refresh_24h`, `refresh_7d`, `refresh_client` (D2-Q034), `gap_backfill` (D2-Q064), `site_search` (D2-Q037), `resolved`, `unresolvable` (D2-Q032), `health` (D2-Q012), `lang_rescore` (a model change triggers `replay`, `normalize-item §5.1 L45`). A client or ops refresh of one post is a `comments` or `metrics` job with `series_step = refresh:<request_id>` (`comment-decay-scheduler §5.1 L70`).
   - RN-11: `first_run` goes; a new rule's first `rotation` is due at once and runs with an empty cursor (D2-Q012).
   - `post_ref` (CF-074, AU-036): the scheduler's object `{item_id, platform, platform_id, url}` on every queue; `platform_id` is the id in the post's key (D2-Q007); the optional `url` is the post's `url` on `items.normalized`, needed by ig-comments-fetcher's vendor call (`§5.3 L68`) and fb-group-comments-fetcher (`§5.1 L40`). Replies jobs add `thread_ids`, the parent comments' platform ids. Anything else a fetcher looks up by `item_id` or keeps itself: Disqus data in `news_sites` (D2-Q040), its newest comment time in `cursors` (D2-Q046), a LinkedIn share URN on the item (D2-Q007). The envelope copies of `post_ref` give way to `parent_id` and `root_id` (CF-074 e, D2-Q009).
   - `push` (CF-086): only for the three receivers whose work continues after the answer and needs retries (a missing-content fetch, `fb-client-webhook-receiver §5.2 L57`; targeted reads, `ig-webhook-receiver §5.2 L57`; a `first_sight` job, `yt-pubsub-receiver §5.2 L55`). One message per pushed entry, keyed by the `source_id` the receiver finds in its in-memory registry copy before answering, with `body` as received, `received_at`, the headers its worker reads, a `job_id` made at receipt, `attempt` and `due_at = received_at`; the wrapper's retries and DLQ apply. The Telegram and LinkedIn receivers keep writing `raw.items` before answering.

   Consequences: one job type the SDK validates; four approved PRDs rename `reason`, and tg-message-search and tg-channel-resolver add `kind`, under D2-Q001; every comment and metrics consumer parses the object; ig-webhook-receiver answers Meta after an in-memory lookup.

2. **CONVENTIONS' seven kinds only, the extra meaning in other fields (CF-077 option 3).** Consequences: the shortest list, but resolver, ops and news jobs have no natural kind, and every consumer dispatches on `series_step` or `reason` itself.
3. **A common envelope plus kinds each service declares for its own queue (CF-077 option 2).** Consequences: nothing to agree centrally, but one word can mean two things on two queues.
4. **As 1, but `post_ref` the post's key string and no push buffer (CF-074 option 3, CF-086 option 3).** Consequences: simpler messages, but `url` and `thread_ids` become loose fields, and three receivers' follow-up work runs before the answer or without retries.

**Why the recommendation.** One closed list is what F2 and the SDK wrapper can validate; the scheduler's object is the only `post_ref` anyone emits; the push buffer stays only where work follows the answer.

**Phase 2 records.** ADR "Jobs: envelope, kinds and `post_ref`" (Applies to: all, F2 included). CONVENTIONS v1.1: L277 (the envelope, the closed list with its fields, `post_ref`, `push`) and L28 (push buffers keyed by `source_id`); x-recent-search §5.2 L53 loses `first_run` and `gap_backfill`; RN-11 is closed by this record.

### D2-Q012 · Who emits which job: the producer table, ops and client requests

- **Class:** technical
- **Settles:** CF-078, CF-079, CF-080, AU-033, AU-034, AU-086, AU-099, ig-webhook-receiver §14 Q3, tt-client-videos-fetcher §14 Q5
- **Blocks:** F2, F4, then C4, C5, C8, C10, C11, C15, A1, A2, A3, A4, FB3, IG4, IG5, IG6, LI2, LI3, VLI2, VLI4, TT1, TG2, VTG2, X5, YT4, YT5, YT6, YT7, YT9, W1, W2, W3, N2, N3, N4, N5, N8
- **Depends on:** D2-Q011 (the kind list), D2-Q017 (`jobs.completed`), and the decisions cited for single rows

**Context.** CONVENTIONS gives every poller its own scheduler, comment, reply and metrics jobs to comment-decay-scheduler alone, and backfill to backfill-orchestrator alone (L278). Three gaps remain:

- Kinds no producer emits (CF-078), above all the ops and client requests that many consumers accept and nothing writes (CF-078 a).
- Kinds a consumer refuses (CF-079), such as the scheduler's daily `health` job for Telegram groups (`comment-decay-scheduler §5.1 L57`), which tg-discussion-receiver does not accept and already runs as `reconciliation` (`tg-discussion-receiver §5.1 L47`, `§6.1 L110`; AU-033, AU-099).
- Comment work from other services (CF-080): ig-webhook-receiver's reconciliations and targeted reads (`ig-webhook-receiver §5.1 L43`, `§5.2 L57`; AU-086); yt-text-purger's `refresh` jobs (`yt-text-purger §5.3 L96`); backfill-orchestrator's comment jobs for new LinkedIn pages (`li-own-comments-fetcher §5.1 L52`). The LinkedIn daily reconciliation expected from the scheduler (`li-own-comments-fetcher §5.1 L48`, `li-notification-receiver §5.1 L44`) is not there; the scheduler reads no `item.metrics` (`comment-decay-scheduler §6.1 L135`) (CF-078 g, AU-034).

At stake: features nothing triggers, and jobs their consumer parks.

**Options**

1. **A producer table in F2, checked by the SDK; the single-emitter rules kept with named exceptions; ops and client requests through the admin API (recommended).**
   - The table: one row per (queue, `kind`) with its allowed producers; the SDK producer refuses, and the consumer's wrapper dead-letters, a job whose (queue, `kind`, `producer.service`) is not listed; a kind with no row leaves its consumer.
   - Rows: each rotating service's scheduler emits `rotation`, `reconciliation` and `refresh` on its own queue, tg-discussion-receiver's daily check per group included (the `tg_own` row emits nothing; no `health` kind), and fb-page-search makes a keyword-rule row due at once when it is `added` or `updated` (its `seed`, D2-Q044). comment-decay-scheduler: `comments`, `replies`, `metrics`; backfill-orchestrator: `backfill`, `keyword_history`; poster-resolver: `resolve`; registry-writer: `manual_candidate`; each analysis service: `analyze`; keyword-matcher: `candidate_retry`; each buffering receiver: `push`.
   - Named cross-service producers: ig-webhook-receiver (below); yt-text-purger, `refresh` to the YouTube fetchers (D2-Q065); the three news pollers and news-comments-fetcher, event-triggered `refresh` to news-site-resolver (D2-Q032); x-filtered-stream, `reconciliation` on `jobs.x-recent-search` (D2-Q064); yt-pubsub-receiver, yt-uploads-reconciler, yt-keyword-search and search-hit-router, `first_sight` (D2-Q037, D2-Q065); retention-purger, `retention_sweep`; deletion-propagator, `recompute` (D2-Q035); news-site-resolver, `first_check`, and the news services through the SDK host gate, `recheck` (D2-Q022). tt-client-videos-fetcher's own metrics need no job (D2-Q024).
   - Ops and client requests (CF-078 a): the admin API (D3 specifies it) is their only writer, through one SDK call with a schema per kind, `request_id`, `requested_by` and an audit record: `ops_force`, `replay`, `rerun` (a client's new topic included), `rematch` (also on a keyword change), `recompute`. A request touching a post's schedule or a backfill goes to its owner, which emits the job, so one job stays in flight per post (`comment-decay-scheduler §5.1 L62`): post refreshes to comment-decay-scheduler (`series_step = refresh:<request_id>`), backfill re-runs to backfill-orchestrator (`backfill-orchestrator §5.1 L50`).
   - Push routes (AU-034): for LinkedIn, comment-decay-scheduler reads li-client-posts-poller's comment counts on `item.metrics` and, while a post is under 7 days old, emits a daily whole-thread `reconciliation` when the count differs from its series' running total; Instagram keeps ig-webhook-receiver's scheduler. Pushed comments in early stop are D2-Q019's.
   - ig-webhook-receiver (AU-086, CF-079 d): ig-own-comments-fetcher expands the per-account reconciliation to the account's media inside their first 7 days, from ClickHouse `items`; a targeted read is `ops_force` with `post_ref` (a media) or `target_ids` (mention ids), which ig-mentions-fetcher adds; both fetchers report on `jobs.completed` (D2-Q017); the receiver sets the next due time from the reconciliation's start (CONVENTIONS L51).
   - The rest, by decision: CF-078 b, f and CF-079 c (D2-Q032); CF-078 c (D2-Q060); d, `replies` on `jobs.x-full-archive-search` only if bought (D2-Q059 d); e (D2-Q037); h and CF-079 e (D2-Q020, D2-Q034, D2-Q058, D2-Q064, D2-Q065); CF-079 a, news backfill only through news-sitemap-poller (D2-Q020, D2-Q059 c); CF-080 d, the scheduler's `once` step (`backfill-orchestrator §5.1 L48`, D2-Q060).

   Consequences: F2 publishes the table; comment-decay-scheduler gains `item.metrics` as an input; the LinkedIn and Instagram comment fetchers change; approved PRDs change under D2-Q001 (web-search-perplexity loses `site_search`, poster-resolver its answer kinds, li-org-resolver the qualifier as a producer).

2. **The strict rule: every comment, reply and metrics job through comment-decay-scheduler (CF-080 option 2).** Consequences: no exceptions, but the scheduler must take requests from ig-webhook-receiver and yt-text-purger.
3. **No rule: each consumer lists its own producers (CF-080 option 3).** Consequences: least change now, but nothing says who may write a queue, two jobs can be in flight on one post, and ops jobs have no schema or audit.
4. **As 1, but push routes reconcile from their own receiver or poller, or not at all (AU-034 options 2, 3).** Consequences: the scheduler reads no counts, but LinkedIn needs a new scheduler or relies on its series steps to catch missed webhooks.

**Why the recommendation.** It keeps one owner per post schedule and per backfill, names the few services that rightly write into another's queue, and gives ops and client requests one audited writer.

**Phase 2 records.** ADR "Who emits which job" (Applies to: all, F2 included). CONVENTIONS v1.1: L278 becomes the producer table with its named exceptions and the admin API as the writer of ops and client requests; L268's daily check is tg-discussion-receiver's `reconciliation`. D3 specifies the admin API and its request schemas.

### D2-Q013 · Registry ownership: one writer for identity and policy, named owners for operational columns, requests as decisions

- **Class:** technical
- **Settles:** FC-02, CF-015, CF-033, AU-016, AU-021, AU-058, AU-063, registry-writer §14 Q4, source-health-canary §14 Q1
- **Blocks:** F2, F3, then C1, C5, C7, C9, C10, C12, C14, FB2, FB3, FB7, VFB1, VFB2, IG2, IG3, VTT2, VTT4, X1, X3, VLI3, TG1, VTG3, YT1, YT2, YT3, YT7, N1, N2, N3
- **Depends on:** D2-Q002 (message metadata), D2-Q049 (`lifecycle` and `push_covered`)

**Context.** For "one writer per topic and per column" the build plan proposes "every registry change goes through `registry.decisions` to registry-writer" (build plan L52), yet registry-writer owns only the identity and policy columns (`registry-writer §3 L27`) and leaves `last_hit_at`, `last_polled_at`, `next_poll_at` and `backfill_status` to their owners through the SDK (`§3 L30`). The topic's writers and shape disagree (CF-015): "the qualifier's decisions" (CONVENTIONS L20) against five producers (`registry-writer §4 L36`); `"decision":"add"` with full metadata (`qualifier §6.2 L84`) against the canary's `"action": "health_change"` with a `fallback` object, `scope`, `reason`, `evidence` and no key (`source-health-canary §6.2 L102`, `§14 Q1 L161`). Services change owned columns themselves (CF-033): pollers announce a dormant source's promotion (`fb-page-feed-poller §5.2 L59`) that the qualifier's sweep also makes (`qualifier §5.1 L46`; AU-058); hashtag pollers store `platform_id`, part of the unique key (`ig-hashtag-search §5.2 L66`); x-recent-search writes `last_hit_at` (`x-recent-search §5.2 L59`) beside keyword-matcher (`keyword-matcher §5.3 L79`). Receivers "ask registry-writer" to promote a source, return it to its reach tier, set `next_poll_at` or retire it (`fb-client-webhook-receiver §5.2 L59`, `yt-pubsub-receiver §6.2 L130`, `yt-uploads-reconciler §8 L154`) by a channel that does not exist (AU-016, AU-063), and other PRDs expect registry-writer to write five stores or columns it does not own (AU-021). At stake: one writer and one audit row for every registry change.

**Options**

1. **Two ownership classes and one request path (recommended).**
   - Columns (FC-02, CF-033): registry-writer alone writes the identity and policy columns (those of `registry-writer §3 L27` plus `lifecycle` and `push_covered` (D2-Q049), the health columns (D2-Q016) and `platform_meta` (D2-Q065)), applying `registry.decisions`. Operational columns have one owner each, written through the SDK without row locks (`registry-writer §12 L138`): the rotation summary by the primary poller (D2-Q015); `backfill_status` by backfill-orchestrator, `pending` being the column default (D2-Q020); `last_hit_at` by keyword-matcher only. Backfill reasons move from `notes` to `backfill_runs`.
   - One schema (CF-015 a to d): `registry.decisions/v1` with D2-Q002's metadata, `decision_id`, the type in one field `decision` (the canary's `action` moves; `registry_audit.action` keeps the applied outcome), `requested_by` (stored as `registry_audit.actor`), `reason`, the subject, and a block per type (the canary's `fallback` object, `scope` and `evidence` included). Closed types: `add`, `update`, `remove_client`, `tier_change` (absorbs `tier_down`; a decay step below tier 3 is `dormant`), `dormant`, `promote`, `retire`, `push_coverage`, `health_change` (route or source level), and the audit-only `queued`, `mention_only`, `reject`, `review`. Key: `candidate_key`, or `source_id` for a registered source (D2-Q004), and `platform` for a route-level change, so successive states of a platform's routes stay in order (D2-Q004). The producers allowed per type are rows of F2's producer table (D2-Q012); registry-writer audits and rejects any other. It stays the topic's only consumer: yt-text-purger takes offboarding from `source.events` or `clients` (`yt-text-purger §5.1 L45`).
   - Requests (AU-016, AU-058, AU-063): a poller or receiver that sees a dormant source post sends `promote` at once; the qualifier's sweep stays as the safety net, and a `promote` of an active source is a no-op. A lapsed lease or failed subscription is `push_coverage` off with a `reason` (`lease_lapsed`, `subscription_failed`), whose event makes the reconciler read at once (D2-Q014, D2-Q015), so no service writes another's `next_poll_at`. A confirmed vanished channel is `retire`. Learned facts (hashtag ids, member counts) are `update`; an id that would duplicate `(platform, platform_id)` is rejected with an audit row and `registry_duplicate`.
   - Stores (AU-021): a) `news_sites` is news-site-resolver's (D2-Q040); a crawl refusal reaches `health` as a source-level decision from news-robots-checker (reason `crawl_disallowed`), and registry-writer reads no `crawl.policies`; b) the uploads playlist id goes in `platform_meta`, from yt-channel-resolver's profile (D2-Q065); c) a hashtag's bound Instagram account comes with its `add` decision, in `platform_meta`; d) a page a client starts administering gets an `update` (route, vendor, `owned_by_client`, `push_covered`, which stays false for TikTok Display accounts and LinkedIn client pages, D2-Q049) from the onboarding flow (D2-Q066); e) client flags are written by the client portal and admin console (D3, D2-Q043).

   Consequences: registry-writer (approved, D2-Q001) accepts more producers, `push_coverage` and source-level `health_change`; the qualifier (approved) sends `tier_change` where it sent `tier_down`; the pollers and receivers of CF-033 b) and AU-063 replace direct writes with decisions; F3's `TABLE-OWNERS.md` names the owner of every `sources` column.

2. **FC-02 literally: every `sources` change is a decision, operational columns included.** Consequences: one audit trail, but every poll and hit becomes a decision through one replica and an audit table kept ten years (`registry-writer §7 L107`), reversing the approved `§3 L30`.
3. **Named direct writers, listed in CONVENTIONS (CF-033 option 2).** Consequences: fewer messages, but no audit row for those changes, about twenty producers of `source.events` (CF-016), `platform_id` collisions on the unique key, and a route-wide `ok` that erases a fetcher's `blocked` (CF-032).
4. **A per-source attributes table owned by the resolvers and pollers (CF-033 option 3).** Consequences: platform facts get their own owners, but every scheduler joins a second table, and dormancy and push requests still need a path.

**Open questions this also answers.** The canary's route-level `health_change` carries `scope`, `reason`, `evidence` and the `fallback` object as its type block (`source-health-canary §14 Q1`).

**Why the recommendation.** It keeps FC-02's guarantee (one writer, one audit row, one event) for every identity, tier, lifecycle and health change, keeps the approved carve-out for busy columns, and gives requests that had no carrier one schema.

**Phase 2 records.** ADR "Registry ownership and `registry.decisions`" (Applies to: registry-writer, qualifier, source-health-canary, retention-purger, yt-text-purger, every poller, receiver and resolver, listening-sdk). CONVENTIONS v1.1: L20 (producers and schema of `registry.decisions`), L36 (the owner of each column), and the closed list of decision types. F3's `TABLE-OWNERS.md` follows the ADR.

### D2-Q014 · `source.events`: one writer and a closed list of event types

- **Class:** technical
- **Settles:** CF-016, CF-098, yt-uploads-reconciler §14 Q4
- **Blocks:** F2, then C6, C7, C10, C11, C12, FB2, FB3, FB7, VFB2, IG2, IG3, IG4, IG5, LI1, LI3, VLI3, N2, N3, TG1, TG2, VTG3, TT1, VTT4, X3, X5, YT2, YT3, and every `source.events` consumer
- **Depends on:** D2-Q013 (changes arrive as decisions), D2-Q049 (`lifecycle`, `push_covered`)

**Context.** CONVENTIONS names no writer and spells one type with a space: "added, updated, tier change, dormant, retired, fallback_on, fallback_off" (L21). registry-writer describes itself as the one path that emits "one `source.events` message per change" (`registry-writer §1 L9`), with `tier_change` (`§3 L24`) and the only defined shape (`§6.2 L95`: `message_id`, `schema_version`, `event`, the source's columns, `previous`, `decision_id`, `actor`, `at`). About twenty services publish events themselves (CF-016 b): `tier change` when a dormant source posts (`fb-page-feed-poller §6.2 L129`, `ig-account-media-poller §6.2 L125`), `updated` on a health or grant change (`li-client-posts-poller §6.2 L126`, `x-user-timeline-poller §8 L151`), `updated` with `backfill_status` (`fb-backfill §6.2 L110`), budget waits (`ig-hashtag-search §5.1 L57`). Readers wait for types nobody emits (CF-098 b): a `route` change (`li-client-posts-poller §6.1 L101`) and `reason = push_lease_lapsed` (`yt-uploads-reconciler §5.1 L51`). A route `blocked` has no event: registry-writer maps health only to `fallback_on`, `fallback_off` or `updated` (`registry-writer §5.2 L54`; CF-098 c). At stake: about 46 consumers rebuild their registry caches from this topic (CF-016).

**Options**

1. **registry-writer is the only writer, from its outbox, with one closed list (recommended).**
   - Writers (CF-016): every change a PRD published directly becomes a decision (D2-Q013) or leaves the topic. Promotion, dormancy, source health, grants and push coverage are decisions. `backfill_status` changes are not events: pollers read the column, and completion travels on `jobs.completed` (D2-Q020). A budget wait is not a registry change: the job ends `quota_denied` (D2-Q057), the portal shows it (D3), and a hashtag beyond the cap is D2-Q052's.
   - Shape `source.events/v1`: D2-Q002's metadata, `event`, `reason`, `source_id`, the source's identity and policy columns after the change, `previous` (the old value of every changed column), `decision_id`, `actor` (the decision's `requested_by`), `at`. One event per applied decision and source; its `message_id` is kept on the `registry_audit` row, so an outbox re-publish repeats it. Consumers follow a column through `previous`, not through the type alone.
   - Types (CF-098), in snake_case: `added`; `updated` (an identity or policy change, route and vendor included, shown in `previous`; clients added or removed; a re-added retired source, never one retired at its owner's request, D2-Q069); `tier_change`; `lifecycle_change` (to `dormant` or `retired`, or reactivated to `active`; replaces `dormant` and `retired`); `health_change` (`ok`, `degraded` or `blocked`, route or source level); `fallback_on` and `fallback_off` (they change provenance); `push_coverage_change`. `reason` values are one closed list in F2 (for example `lease_lapsed`, `subscription_failed`, `bot_removed`, `client_removed`).

   Consequences: one shape for every consumer; registry-writer (approved, D2-Q001) replaces two types and adds three; about twenty PRDs drop their direct events; yt-uploads-reconciler listens for `push_coverage_change` with `reason = lease_lapsed`, li-client-posts-poller for `updated` with `previous.route`.

2. **Direct writes stay for operational events, in registry-writer's shape (CF-016 option 2).** Consequences: no extra decisions, but events with no audit row or `decision_id`, and an event that says "promoted" while the column says dormant (CF-033).
3. **Two topics: `source.events` for registry changes and an operational-signals topic for pollers' observations (CF-016 option 3).** Consequences: a clean separation, but a new topic, schema and readers, and the observations still need a path into the registry.
4. **CONVENTIONS' list in underscores, everything else as `updated` with a free `reason` (CF-098 option 1).** Consequences: the smallest change, but `blocked`, lifecycle and push coverage hide inside `updated`, and every consumer parses reasons.

**Why the recommendation.** One writer gives every event an audit row, a `decision_id` and `previous`, so caches can be rebuilt and a replay changes nothing; typed events for the states consumers act on spare them from parsing free text.

**Phase 2 records.** ADR "`source.events`: writer, shape and types" (Applies to: registry-writer, every `source.events` consumer, the PRDs of CF-016 b). CONVENTIONS v1.1: L21 (the writer, the shape and the closed list).

### D2-Q015 · Rotation state when several services rotate one row

- **Class:** technical
- **Settles:** CF-031, CF-114, AU-088
- **Blocks:** F3, then F5, C7, C10, FB6, IG2, IG3, IG5, VIG1, TG1, VTG3, YT2, YT3, N3, N4, N5, W1, W2, W4
- **Depends on:** D2-Q041 (the `cursors` row), D2-Q049 (the cadence table per source type)

**Context.** CONVENTIONS gives each source one `next_poll_at` and one `last_polled_at` (L36), says "the scheduler keeps `next_poll_at` per source" (L51), and has every rotating service run its own leader-elected scheduler (L278). Several services rotate the same row at different intervals (CF-031): news-feed-poller every 5 to 15 minutes for hot sites and news-sitemap-poller hourly on the same sites (`news-feed-poller §5.1 L42`, `L44`; `news-sitemap-poller §5.1 L45`); the three web engines on the same keyword-rule rows (`web-search-perplexity §5.1 L41`, `L42`); Instagram accounts and hashtags (`ig-mentions-fetcher §5.1 L41`; `ig-hashtag-search §5.1 L57`); Telegram bot channels (`tg-bot-channel-receiver §5.1 L44`; `tg-channel-posts-poller §5.1 L44`); and yt-pubsub-receiver expects registry-writer to set a channel's `next_poll_at` to now (`yt-pubsub-receiver §5.1 L42`). Three services already keep their due time in `cursors` (`ig-mentions-fetcher §5.1 L45`, `ig-keyword-search §5.1 L45`, `fb-page-search §5.1 L42`), while the SDK's rotation helper reads `sources.next_poll_at` (CF-114). ig-hashtag-search's jobs come from "the shared scheduler" (`ig-hashtag-search §5.1 L45`), which no PRD defines (AU-088). At stake: whichever service finishes last sets the next run of the others, and `last_polled_at` means "some service polled".

**Options**

1. **Each service schedules itself from its own row in `cursors` (recommended).** Every rotating service runs its own leader-elected loop (CONVENTIONS L278), ig-hashtag-search included; a hashtag's first read is backfill-orchestrator's job (D2-Q020). Its due time and last start live in its own `cursors` row (`next_due_at`, `last_started_at`, D2-Q041, with a scope key per keyword or edge where a service needs one), set from the start of the last run. The SDK's rotation helper reads only these (ordering, `rotation_lag_seconds`, `rotation_behind`); a source with no row is due at once. `sources.last_polled_at` and `next_poll_at` remain a summary for the admin view, written in the same transaction by the primary poller that D2-Q049's cadence table names for the source type; no scheduler selects on them, and no service writes another's due time. Catch-up after a lapsed lease or a failed subscription is event-driven: the `push_coverage_change` event (`reason = lease_lapsed`, D2-Q014) makes yt-uploads-reconciler emit its reconciliation job at once, as `yt-uploads-reconciler §5.1 L51` already describes. Consequences: one helper and one clock per service; F3 adds the two typed columns; the PRDs that schedule on `sources.next_poll_at` move to their own row, among them approved ones (fb-page-feed-poller, whose scheduler is CONVENTIONS' model, ig-hashtag-search, x-recent-search, web-search-perplexity; D2-Q001).
2. **One `sources.next_poll_at` with one owner per source type, the others deriving their schedule from it (CF-031 option 2).** Consequences: no new columns, but the secondary services (ig-mentions-fetcher, news-sitemap-poller, the second and third web engines) cannot keep the cadence their PRDs promise.
3. **One registry row per service where several rotate the same thing (CF-031 option 3).** Consequences: each scheduler owns a row, but one news site or Instagram account becomes several sources against the unique `(platform, platform_id)` (`registry-writer §5.3 L70`); for keyword rules, the rows are D2-Q044's.
4. **One shared scheduler component for all rotating services (CF-114 option 2, AU-088 option 2).** Consequences: one place to tune, but a component the build plan gives to no session, a single point of failure for all rotation, and CONVENTIONS L278 rewritten.

**Why the recommendation.** It is what three PRDs already do, it keeps CONVENTIONS' own-scheduler rule, and each service keeps the cadence its PRD promises without overwriting another's.

**Phase 2 records.** ADR "Rotation state per service" (Applies to: every rotating service, listening-sdk). CONVENTIONS v1.1: L36 (`last_polled_at` and `next_poll_at` as a summary written by the primary poller), L38 (the typed `cursors` columns, with D2-Q041), L51 ("each scheduler keeps its due time per source in its own `cursors` row"), L108 (`rotation_lag_seconds` read from that row).

### D2-Q016 · Source health and credential state

- **Class:** technical
- **Settles:** CF-032, CF-057, AU-069, AU-070
- **Blocks:** F2, F3, then F4, F6, C7, C12, FB1, FB2, FB3, FB4, FB5, FB6, FB7, IG1, IG2, IG3, IG4, IG5, IG6, LI1, LI2, LI3, VLI3, TT1, VTT1, VTT2, TG1, TG2, VTG3, X1, X3, X4, X5, X6, X7, YT1, YT2, YT3, YT4, YT5, YT6, YT8, YT9, N2, N3, N8, W1, W2, W4, W5
- **Depends on:** D2-Q021 (what a 401 or 403 means), D2-Q013 (health changes as decisions)

**Context.** registry-writer owns `health` (`registry-writer §3 L27`) and applies the canary's route-level `health_change` as a bulk update of every source on the route (`§5.2 L54`); the canary works per route (`source-health-canary §2 L15`, `§5.3 L66`). A dozen fetchers set one source's health themselves (CF-032 b): a removed bot (`tg-bot-channel-receiver §5.2 L72`), privacy mode (`tg-discussion-receiver §5.2 L69`), a lost administrator role (`li-client-posts-poller §8 L142`), a suspended account (`x-user-timeline-poller §8 L151`), a rejected query (`x-recent-search §8 L154`). Others ask the canary for per-source flips it cannot make (AU-070: `x-compliance-sync §5.3 L83`, `news-feed-poller §12 L156`, `web-commoncrawl-scanner §8 L122`, `ig-webhook-receiver §8 L144`). The receivers expect the canary to watch push heartbeats (`tg-bot-channel-receiver §8 L152`, `tg-discussion-receiver §8 L156`, `yt-pubsub-receiver §8 L146`), which it leaves out of scope (`source-health-canary §3 L30`; AU-069). Separately, 40 PRDs mark a token or key `degraded` and expect later calls to skip it (`CONVENTIONS L101`; `fb-page-feed-poller §5.2 L55`, `§13 L183`), but only one names a store (`tt-keyword-search §8 L117`, `vendor_keys`), and tt-client-videos-fetcher writes refreshed tokens to Vault itself (`tt-client-videos-fetcher §5.2 L56`; CF-057). At stake: a route-wide return to `ok` clears a source that a fetcher set to `blocked`, with no audit row, and the other services that share a revoked client token keep calling with it.

**Options**

1. **Two levels, each with one writer (recommended).**
   - Source health (CF-032, AU-070): `sources.health` (`ok`, `degraded`, `fallback`, `blocked`) with `health_reason`, `health_set_by` and `health_changed_at`, written only by registry-writer from `health_change` decisions (D2-Q013). Route level comes from the canary (`platform`, `route`, `vendor`, `health`, the `fallback` object, `scope`, `reason`, `evidence`, as `source-health-canary §6.2 L102`) and is applied, within D2-Q021's government rule, to sources whose state is `ok` or was set at route level. Source level comes from the service that saw it: `source_id`, `health` and a `reason` from a closed list (`bot_removed`, `privacy_mode`, `grant_missing`, `account_unavailable`, `credential_revoked`, `not_found`, `uploads_playlist_missing`, `query_rejected`, `feed_gone`, `push_gap`, `crawl_disallowed`). A source-level state is cleared only by a source-level decision (the service that set it, or ops), and the source then takes its route's current state. x-compliance-sync, the news pollers, web-commoncrawl-scanner and ig-webhook-receiver send their own source-level decisions; per-site publishing-rate checks are not the canary's in v1.
   - Push and stream routes (AU-069): the canary reads the receivers' heartbeat counters (the Telegram canary channel and test group, PubSubHubbub renewals and notifications, Instagram webhook deliveries, the X stream's canary accounts) beside the SDK route counters it already reads (`source-health-canary §6.1 L96`), and flips the route; its `§3 L30` exclusion goes. Reconnecting the stream stays x-filtered-stream's own job.
   - Credentials (CF-057): one `credentials` table for every client token, company-app key and vendor key: owner (client, app or vendor), Vault reference, scope, `state` (`ok`, `degraded`, `revoked`), `reason`, `changed_at`, `plan`; `vendor_keys` becomes its vendor rows. It is read and written only through the SDK's credential client, which injects the credential per job (`CONVENTIONS L12`), never hands out a `revoked` one, picks the first healthy token among the source's clients (`fb-page-feed-poller §5.2 L55`), stores refreshed OAuth tokens, and on a revoked platform credential sends a source-level `health_change` (`credential_revoked`) for each source no other credential can read (D2-Q021). A new grant or key returns a credential to `ok`; a successful call clears `degraded`.

   Consequences: registry-writer (approved, D2-Q001) applies source-level decisions and keeps them apart from route changes; F3 adds the health columns and `credentials`; about forty section 8 lines name one store; the canary's scope grows to push heartbeats.

2. **Direct source-level writes with a guard (CF-032 option 2):** fetchers write `health` and `health_set_by`; the route-wide update skips rows a fetcher set. Consequences: fewer messages, but no audit row and no event for those writes.
3. **Two columns, route health and source health (CF-032 option 3), with token state in `vendor_keys` and a client-token table (CF-057 option 1).** Consequences: a clean separation, but every reader combines two columns and two token stores.
4. **No token-level mark (CF-057 option 3):** a revoked token degrades the sources that use it. Consequences: the simplest schema, but every service sharing the token keeps calling until each fails on its own.

**Why the recommendation.** Every health change gets one writer and one audit row, a route recovery can no longer erase a source's own problem, and token state lives where every service already gets its token, in the SDK.

**Phase 2 records.** ADR "Source health and credentials" (Applies to: all fetchers and receivers, source-health-canary, registry-writer, listening-sdk). CONVENTIONS v1.1: L30 (`credentials` replaces `vendor_keys`), L36 (the health columns), L101 and L102 with D2-Q021's wording.

## Group 2 · The README's nine proposals

The build plan says to accept the nine proposals "as written unless D1 finds a conflict" (FC-01). D1 found conflicts against all nine (`docs/contracts/CONFLICTS.md` section 4), so each comes here with the entries that contradict it, and FC-01 itself needs no decision of its own (Appendix B). RD-n is README decision n (`docs/prds/README.md` L178 to L186).

### D2-Q017 · How a finished job reports back: `jobs.completed` (README decision 1)

- **Class:** technical
- **Settles:** RD-1, CF-024, CF-089, AU-001, RN-12, comment-decay-scheduler §14 Q1, fb-post-comments-fetcher §14 Q6, x-replies-fetcher §14 Q4
- **Blocks:** F2, F3, then F4, F5, F6, C10, C11, FB3, FB5, VFB3, IG2, IG6, VIG2, LI2, VLI4, VTT5, VTT6, X1, X3, X4, X5, X6, YT3, YT4, YT5, YT6, N4, N8
- **Depends on:** D2-Q002 (message metadata), D2-Q011 (the job envelope), D2-Q057 (quota answers and the DLQ)

**Context.** README decision 1 proposes a completion topic `jobs.completed` (`jobs.completed/v1`), "written by the listening-sdk job wrapper after every job with a report (`new_count`, `seen_count`, `pages`, `cost_units`, `reply_candidates`)", read by comment-decay-scheduler and backfill-orchestrator (`README L178`; `comment-decay-scheduler §14 Q1 L202`). CONVENTIONS has no such topic; a fetch only "reports" four counts (L62). D1 found (CF-024, CF-089, AU-001): three services publish the topic themselves (`yt-uploads-reconciler §5.2 L66`, `yt-video-details-fetcher §5.2 L63`, `x-full-archive-search §6.2 L128`); others report through `service_runs` (`news-comments-fetcher §5.2 L59`, `li-post-search §5.2 L61`), "the job result" (`ig-comments-fetcher §5.2 L63`) or "the completion message" (`tt-video-stats-refresher §6.2 L112`); the two consumers' examples carry different report blocks (`comment-decay-scheduler §5.4 L127`, `backfill-orchestrator §5.4 L92`); `seen_count` means "posts with `paid = false`" in one PRD and "edits included" in another (`x-user-timeline-poller §5.2 L61`, `x-replies-fetcher §5.2 L62`); no document lists the statuses or says which end a series (`yt-comments-fetcher §8 L155`, `L156`; `x-replies-fetcher §14 Q4 L202`); and x-recent-search, whose reports two services read (`x-filtered-stream §5.2 L71`, `x-full-archive-search §5.2 L52`), never names the topic. D1's review note 12 adds that CONFLICTS.md section 4 row 1 cites CF-089 and AU-001 but not CF-024. At stake: a series or a backfill advances only on a report its consumer can read.

**Options**

1. **README decision 1, with one schema and the wrapper as the only writer (recommended).**
   - Writer: the SDK job wrapper, exactly once per job, a job that ends in the DLQ included. Services return a report object and never publish themselves; a service that serves several jobs with one call (yt-video-details-fetcher's collector) returns one report per job.
   - Common fields: D2-Q002's metadata, `job_id`, `queue`, `kind`, `source_id`, `post_ref` and `series_step` where the job had them, `attempt`, `status`, `finished_at`, and `report {new_count, seen_count, pages, cost_units, reply_candidates}`. `new_count` counts items not stored before; `seen_count` items read that were already stored, edits included; billing detail (X's free re-reads, `paid_user_reads`) goes in kind fields.
   - `status`, closed, one meaning each: `done`, `partial` (stopped early, what was read is stored) and `capped` (with `capped_reason`) advance the series; `quota_denied` is never an attempt (a series step is held, a backfill ends `capped`, D2-Q057); `failed` (the DLQ) marks the step missed or ends a backfill `capped`; `skipped_flag_off`, `not_allowed` (government client, outside the route's window, not a conversation root) and `gone` (video or post not found, comments disabled) end the series, each with a `reason`. `ok` gives way to `done`.
   - Kind fields, declared per kind in F2: backfill `oldest_item_at` and `capped_reason` (replacing `coverage_days`, `oldest_seen`, `urls_emitted`); comments and replies `complete`, with every thread list (`reply_threads`, incomplete threads) folded into `reply_candidates`. Per-post markers (`newest_comment_at`, `thread_id`) live in the fetcher's `cursors` rows (D2-Q046), not in reports; x-full-archive-search's replies hand-back is not built in v1 (D2-Q064).
   - Keyed like the job it reports on (D2-Q004). Readers: comment-decay-scheduler, backfill-orchestrator, x-filtered-stream, x-full-archive-search, and deletion-propagator for recomputes (D2-Q035). `service_runs` keeps per-service status only (D2-Q045).
   - RN-12: CF-024 is settled here with CF-089 and AU-001; CONFLICTS.md stays D1's record.

   Consequences: x-recent-search (approved, D2-Q001) reports through the wrapper with no code of its own; li-post-search and ig-hashtag-search (approved) move or rename their counters; F2 defines the schema and the status table; F4 and F6 build it once.

2. **As 1, and services may also publish completions the wrapper does not see (CF-089 option 2).** Consequences: x-full-archive-search's hand-back could stay as written, but two writers can report one job twice and the once-per-job guarantee is lost.
3. **No topic: result rows in `service_runs` or a job-results table that the consumers poll (`comment-decay-scheduler §14 Q1 L202`).** Consequences: no new topic, but polling delay on every series step and a hot table with one row per job.
4. **A small required core plus a free `extra` object stored uninterpreted (AU-001 option 3).** Consequences: flexible, but consumers cannot validate the fields they act on.

**Why the recommendation.** The wrapper already runs after every job, so it is the one place that can guarantee exactly one report per job, and a closed status list with fixed meanings is what lets comment-decay-scheduler and backfill-orchestrator end a series or a run correctly.

**Phase 2 records.** ADR "Job completion reports" (Applies to: listening-sdk, comment-decay-scheduler, backfill-orchestrator, x-filtered-stream, x-full-archive-search, every service that consumes jobs). CONVENTIONS v1.1: the topic list (L14 to L29) gains `jobs.completed`; L62's "reports" points to it; the status table goes to F2.

### D2-Q018 · Budget priorities and modes (README decision 2)

- **Class:** user (which work keeps running when a budget or quota runs short is a business choice)
- **Settles:** RD-2, CF-100, CF-101, AU-039, AU-067, comment-decay-scheduler §14 Q4, fb-group-comments-fetcher §14 Q3, ig-comments-fetcher §14 Q4, quota-governor §14 Q2, x-compliance-sync §14 Q3, yt-comments-fetcher §14 Q2, yt-video-details-fetcher §14 Q1
- **Blocks:** F2 (the single `refresh:<request_id>` label in the job schema), F5 (the SDK priority helper), C1 (quota-governor), C10, C11, then YT4, YT5, YT6, YT7, YT8, X1, X3, X4, X5, X6, FB4, FB6, VLI1, VTG1, VTG2, VTT3
- **Depends on:** D2-Q057 (what a job does with `deny` and `wait-until`)

**Context.** README decision 2 sets five priorities (the table in option 1, less the added rows) and three modes: `normal`; `stretch` from 80% of a budget, admitting priorities 1 to 3, from 95% only 1 and 2, amber intervals stretched by a factor never beyond 24 hours; `exhausted` at 100% (`README L179`). quota-governor derives them "from job kind and tier by an SDK helper ... so backfill is always 5" (`quota-governor §5.1 L39`, L43 to L47). D1 found:

- Client refresh: 1 in the README, quota-governor and `comment-decay-scheduler §5.1 L70`; 3 in `yt-comments-fetcher §14 Q2 L204`, `yt-replies-fetcher §14 Q3 L192`, `x-replies-fetcher §7 L145`; "at lowest priority" for backfilled posts (`backfill-orchestrator §5.1 L48`); three labels (AU-039).
- First sight: `yt-video-details-fetcher §5.1 L50` proposes 1 for new videos from every tier and keyword rule (5 for backfill first sight); the table derives 2 or 3 from the tier. A client's X history read is 1 in `x-full-archive-search §5.2 L53`, with no row.
- Orderings outside the table (AU-067): priorities carried on jobs (`yt-comments-fetcher §5.2 L53`, `tt-user-resolver §5.1 L41`, `x-filtered-stream §5.2 L70`); the text refresh at 3 (`yt-text-purger §5.3 L84`); the Meta bucket gating 4 and 5 above 80% (`quota-governor §5.3 L80`); "rotation polls first, comment series second, metrics refreshes third" (`fb-reactions-fetcher §7 L134`) and search ranked "below rotation polls and comment series" (`fb-page-search §7 L127`); daily vendor rules answered wait-until at 80% (`li-post-search §5.1 L46`), the lowest sets on client priority lists first (`tg-message-search §5.1 L46`); resolver discovery "never stretched, only denied" (`tg-channel-resolver §5.1 L47`); the YouTube `reserve` for priority 1 only (`quota-governor §5.3 L79`) or for catch-up, hot posts and client refreshes (`yt-keyword-search §7 L133`).
- Modes on green tags (CF-101): CONVENTIONS stretches and drops hot extras only on amber (`CONVENTIONS L51`, `L271`), the README gates every tag (open in `quota-governor §14 Q2 L171`); x-recent-search has its own X cascade (`x-recent-search §7 L143`).

At stake: what still runs near the X cap, YouTube's 10,000 daily units and each vendor budget.

**Options**

1. **The README's table, completed with explicit rows and derived only by the SDK helper; priority gating on every tag, interval stretching on amber tags only (recommended).**
   - 1: tier-1 rotation, every client request (refreshes, including of backfilled posts, and history reads), `ops_force`, canaries, and `first_sight` jobs from live discovery on any tier (on YouTube, the details call).
   - 2: tier-2 rotation, client keyword and hashtag searches, comment steps to +24 h, +24 h metrics.
   - 3: tier-3 and dormant rotation, later comment steps, replies, +7 d metrics, the 30-day text refresh.
   - 4: hot-post extras, resolvers and discovery lookups.
   - 5: backfill, first sight of backfilled ids, and X history reads nobody asked for.
   - No caller sends a priority; the YouTube `reserve` serves priority 1 only; one label, `refresh:<request_id>`.
   - Modes: `stretch` and `exhausted` gate priorities on every tag, so hot extras and resolver lookups stop at 80% on X and YouTube; `stretch_factor` (never beyond 24 hours) applies to amber tags only.
   - Other orderings: the Meta rule (L80) is kept, being this gating; tg-message-search's client order is the tie-break within a priority; a daily rule that cannot stretch gets wait-until (li-post-search); tg-channel-resolver's "only denied" holds, since resolvers are priority 4; fb-reactions-fetcher's and fb-page-search's orders and x-recent-search's cascade give way to the table. Approved PRDs move under D2-Q001 (x-recent-search, fb-page-search, yt-keyword-search's `reserve`).

   Consequences: one table and one helper, testable in F5; client requests run first, so the admin console (D3) caps them per client; new items are never left half-recorded (a YouTube details call costs 1 unit for 50 ids); from 80% to 95% priority 3 still runs, and only the last 5% is kept for priorities 1 and 2.

2. **The README's table exactly as written, the PRDs aligned.** First sight by tier, X history reads at 5; modes as in option 1. Consequences: fewer rows; at 95% of the YouTube quota, new videos from tier-2 and tier-3 channels stay partial, and a client's X history request waits behind all rotation.
3. **Per-tag priority profiles in `budgets`, or callers sending priorities checked against a per-kind maximum.** Consequences: each vendor keeps its own order, but behaviour becomes configuration, and two services can rank one job differently.

   A variant of any option: CONVENTIONS' modes (amber only), so nothing on X or YouTube is gated before 100%.

**Open questions this also answers.** X compliance jobs (`x-compliance-sync §14 Q3`) run at priority 1 and are never gated, since a missed compliance run breaks the 24-hour rule.

**Why the recommendation.** It keeps README decision 2, closes every gap with a row rather than an exception, and keeps priorities out of callers' hands.

**Phase 2 records.** ADR "Budget priorities and modes" (Applies to: F2, F5, quota-governor, listening-sdk, comment-decay-scheduler, backfill-orchestrator, every service with a `budget_tag`). CONVENTIONS v1.1: the table and mode rules under "Quotas, budgets and the quota governor"; L51 and L271 reworded.

### D2-Q019 · Early stop of a comment series (README decision 3)

- **Class:** technical
- **Settles:** RD-3, CF-107, comment-decay-scheduler §14 Q2, fb-post-comments-fetcher §14 Q2
- **Blocks:** C11, then FB5, VFB3, IG6, VIG2, VTT5, X6, YT5, YT6, LI2, VLI4, N8

**Context.** CONVENTIONS stops a series "when a fetch adds fewer than 5% new comments (and fewer than 5 absolute)" with no arming condition (`CONVENTIONS L57`, `L271`). README decision 3 arms early stop "only once a post has 5 stored comments or after its +24 h step", so a post with no comments at +1 h keeps its series (`README L180`); comment-decay-scheduler implements it (`comment-decay-scheduler §5.3 L88`, `L89`; asked to confirm in `§14 Q2 L203`), as do `x-replies-fetcher §5.1 L45` and `yt-replies-fetcher §5.1 L40`. The LinkedIn fetchers arm it "from the second fetch of a post onward" (`li-own-comments-fetcher §5.1 L42`; `li-post-comments-fetcher §5.1 L44`); four fetchers restate CONVENTIONS without arming (`fb-post-comments-fetcher §5.1 L48`, which asks whether the +24 h step should be exempt, `§14 Q2 L188`; `news-comments-fetcher §5.1 L43`; `tt-video-comments-fetcher §5.1 L44`; `ig-comments-fetcher §5.1 L45`). The denominator: the scheduler measures growth over the comments stored before the fetch (`comment-decay-scheduler §5.3 L87`), while li-own-comments-fetcher measures over the platform's reported count, "because held comments expire at 48 hours" (`li-own-comments-fetcher §5.1 L42`).

**Options**

1. **README decision 3 on every profile, applied only by comment-decay-scheduler, with the +24 h step kept and a LinkedIn denominator (recommended).** Early stop is armed once the post has 5 stored comments or its +24 h step has run, as the README says; once it fires it cancels the remaining steps except the +24 h step, which always runs as the sweep for late comments (fb-post-comments-fetcher's proposal, `§14 Q2 L188`); a +24 h sweep that adds 20% or more of the stored comments reopens the cancelled steps as an extension (the extension threshold of CONVENTIONS L271). Growth is measured over the comments stored before the fetch, except on LinkedIn, where held comments expire at 48 hours: li-own-comments-fetcher measures over the API's reported comment count (`li-own-comments-fetcher §5.1 L42`), li-post-comments-fetcher over its own running total of comments seen (`li-post-comments-fetcher §6.1 L103`, `§6.3 L133`). The fetchers report counts and never stop a series themselves; their PRDs drop their own early-stop text. Consequences: one rule in one service; one extra fetch for posts that settle before +24 h; the LinkedIn denominators are one column in the profile table, filled from the fetcher's report.
2. **Per-profile arming and denominator columns, filled from each fetcher's PRD.** Consequences: every route keeps what its PRD wrote (LinkedIn from the second fetch, Facebook and news unarmed), so the same post shape stops at different times on different routes with no stated reason.
3. **CONVENTIONS as written (no arming), with the +24 h step exempt.** Consequences: a post with no comments at +1 h loses +6 h and every step after +24 h, the case the README added the arming rule for.

**Why the recommendation.** The README's rule fixes a real failure (quiet posts that pick up comments later), the scheduler already implements it, the +24 h sweep is the cheapest catch for late comments, and LinkedIn's 48-hour purge is the one case where the stored count is the wrong basis.

**Phase 2 records.** ADR "Early stop" (Applies to: comment-decay-scheduler and every comment fetcher). CONVENTIONS v1.1, L57 and L271: the arming condition, the reopening rule and the LinkedIn denominators. The thresholds stay as written; tuning them after real data is left to the sessions after G2 (build plan L65).

### D2-Q020 · Backfill: one writer of `backfill_status`, a complete route table, one job and one report (README decision 4)

- **Class:** technical
- **Settles:** RD-4, CF-030, CF-088, AU-017, AU-042, AU-043, AU-046, AU-047, backfill-orchestrator §14 Q1, backfill-orchestrator §14 Q2, registry-writer §14 Q2
- **Blocks:** F2, F3, then F4, F5, C7, C10, FB2, FB3, VFB1, VFB2, IG1, IG2, IG3, IG4, IG5, VIG1, TT1, VTT1, VTT2, VTT4, X5, VLI1, TG1, TG2, VTG1, VTG3, YT3, N2, N3, N4
- **Depends on:** D2-Q014 (the re-add event), D2-Q015 (hand-over without `next_poll_at`), D2-Q017 (the report), D2-Q059 (X keyword rules and news sites)

**Context.** README decision 4 makes backfill-orchestrator "the single writer of `backfill_status`", ends a failed or slow backfill `capped` with the source entering rotation anyway, and names fb-group-posts-poller the target for Facebook groups (`README L181`); the orchestrator agrees (`backfill-orchestrator §1 L9`, `§5.1 L46`). D1 found:

- other writers (CF-030, AU-017): fb-backfill (approved) sets the status, `next_poll_at`, `notes` and an event (`fb-backfill §5.2 L51`, `L56`), as do tg-channel-posts-poller (`§5.1 L54`) and the TikTok searches (`tt-keyword-search §5.1 L44`, `tt-hashtag-feed-poller §5.1 L48`); registry-writer inserts `pending` and `next_poll_at = now()` (`registry-writer §5.2 L52`) though `§3 L30` gives both to others; the Telegram receivers set `capped` where the orchestrator sets `done` (`tg-bot-channel-receiver §5.1 L50`, `backfill-orchestrator §5.3 L76`);
- routes (CF-088, AU-042): six services wait for a job the route table never sends, since keyword rules and hashtags get "`done` at once" (`backfill-orchestrator §5.3 L79`); three backfill on their own first run (`tg-message-search §5.1 L44` and the TikTok searches); the news row names news-feed-poller, which takes no backfill;
- job and report (AU-043, AU-017): `run_id` and `cap` (`backfill-orchestrator §6.2 L106`) against `window_start`, `window_end` and `reason` (`fb-backfill §5.1 L41`); the orchestrator waits for `oldest_item_at` and `capped_reason` (`backfill-orchestrator §5.4 L92`), which no service sends;
- sequencing (AU-046, AU-047): ig-account-resolver expects the orchestrator to wait for a tier (`ig-account-resolver §5.1 L52`); a re-added retired source emits both `updated` and `added` (`registry-writer §5.2 L52`), and a second `initial` run repeats the first job id (`backfill-orchestrator §5.3 L85`).

At stake: sources that never get the history their PRDs promise, and rotation started or held by the wrong writer.

**Options**

1. **README decision 4, completed (recommended).**
   - Status: backfill-orchestrator writes every transition; `pending` is the column default, so registry-writer writes neither it nor `next_poll_at`; executing services only report. A route with no history ends `capped` at once with `capped_reason = no_history`. `capped_reason` is closed: `route_cap`, `budget`, `deadline`, `failed`, `no_history`, `flag_off`; reasons live in `backfill_runs`, not `sources.notes`.
   - Route table: Facebook Page fb-backfill, group fb-group-posts-poller, keyword rule fb-keyword-search; Instagram account ig-account-media-poller, plus ig-mentions-fetcher for a client-owned one (the status waits for both jobs), hashtag ig-hashtag-search, keyword rule ig-keyword-search; TikTok creator tt-profile-videos-poller, client account tt-client-videos-fetcher, keyword rule tt-keyword-search, hashtag tt-hashtag-feed-poller; X account x-full-archive-search; LinkedIn client page li-client-posts-poller, amber page li-company-posts-poller, keyword rule li-post-search; Telegram channel tg-channel-posts-poller, keyword set tg-message-search; YouTube channel yt-uploads-reconciler, and a term promoted to tier 1 yt-keyword-search (`yt-keyword-search §5.1 L51`). X keyword rules and news sites as D2-Q059 decides. None (`no_history`): Telegram own channels, web engine rules, yt-web-search-bridge rules. No service backfills on its own first run (tt-keyword-search, tt-hashtag-feed-poller and tg-message-search, all approved, move under D2-Q001); a first rotation reads from an empty cursor.
   - One job: D2-Q011's envelope with `kind = backfill`, `run_id`, `reason` (`add`, `client`, `ops`), `window_start`, `window_end` and `cap {max_age_days, max_items}`. An initial window ends at emission and starts the route's age cap earlier (at most 90 days), as `fb-backfill §3 L20` reads; a re-run carries an explicit window, clipped to 90 days except where the route's PRD allows more on a client's request (`x-full-archive-search §2 L13`).
   - One report: `jobs.completed` (D2-Q017) with status `done` or `capped`, `capped_reason`, `oldest_item_at` and the counts; the orchestrator writes the status from it, or `capped` on its deadline or the DLQ. The hand-over writes nothing else: a source with no rotation row is due at once (D2-Q015), and backfill services stop seeding the pollers' cursors (D2-Q041).
   - Sequencing: a run waits in `pending` until the source has a tier (the `updated` event that brings one). A re-added retired source arrives as one `updated` event with `previous.lifecycle = retired` (D2-Q014); the orchestrator opens a run whose `run_id` comes from that decision (a replay emits no second job, a later re-add gets its own), with a window from retirement to now within the cap, and the pollers restart from an empty cursor.

   Consequences: one state machine and one job schema for C10 and every target; six services get the backfill their PRDs promise; fb-backfill (approved) drops its status writes, `notes`, event and cursor seeding.

2. **The executing service writes the transitions; the orchestrator only emits and enforces the deadline (CF-030 option 2).** Consequences: matches fb-backfill as written, but a service's `done` races the deadline `capped`, and every target carries the state machine.
3. **Self-backfill on the first run for keyword rules and hashtags, orchestrator jobs for the rest (CF-088 option 3, AU-042 option 3).** Consequences: no job for the searches, but their deep first run is paid at rotation priority, outside the orchestrator's cap and report.
4. **The route table as written: keyword rules and hashtags get no history (AU-042 option 2).** Consequences: the cheapest, but six PRDs drop a promised feature.

**Why the recommendation.** One writer and one job schema remove the races and the jobs nobody sends, while keeping the README's rule that a slow or failed backfill never holds a source out of rotation.

**Phase 2 records.** ADR "Backfill" (Applies to: backfill-orchestrator, registry-writer, every service in the route table, comment-decay-scheduler). CONVENTIONS v1.1: L53 (the route table, the window and the `no_history` rule), L278 (backfill jobs only from backfill-orchestrator, no self-backfill), L36 (`backfill_status` defaults to `pending`).

### D2-Q021 · A platform 401 or 403, fallback, and the government exclusion (README decision 5)

- **Class:** user (whether the platform switches a client's data to a vendor automatically, and the guarantee given to government clients, are product and compliance choices)
- **Settles:** RD-5, CF-094, AU-064, fb-post-comments-fetcher §14 Q5, source-health-canary §14 Q2, source-health-canary §14 Q4
- **Blocks:** F3 (the states the schema holds), F4, F5 (the SDK's error handling), C7, C12, then every green fetcher (TT1, LI1, LI2, IG3, IG5, IG6, X1, X2, YT1, YT3, YT4, TG1, TG2, VLI2 are named in CF-094)
- **Depends on:** D2-Q016 (where token and source state are stored and who writes them)

**Context.** CONVENTIONS says a 401 or 403 makes the service mark "the token or route `degraded`", stop the batch and alert (`CONVENTIONS L101`); the canary sets `fallback_on` "where an amber or alternate route exists and the flag is on" (`CONVENTIONS L102`). README decision 5: a platform 401 or 403 means `blocked`, no automatic fallback, an n8n approval card; a vendor key or plan error is `degraded` and may fall back; a government-watched green source never moves to amber (`README L182`). The repository rules repeat CONVENTIONS (`CLAUDE.md` L47). source-health-canary follows the README (`source-health-canary §5.3 L70` to `L72`); most fetchers follow CONVENTIONS (`x-recent-search §13 L186`, `ig-own-comments-fetcher §13 L187`); some block one source under their own conditions (`tt-client-videos-fetcher §8 L130`, `li-client-posts-poller §8 L142`, `tg-bot-channel-receiver §8 L150`); tt-client-videos-fetcher refuses any amber fallback for a client-owned account (`§8 L132`); the YouTube fetchers classify a 403 by reason (`yt-video-details-fetcher §8 L171`, `yt-comments-fetcher §8 L155`). The government exclusion has no enforcement point: registry-writer's `health_change` updates every source on the route and reads no `scope` (`registry-writer §5.2 L54`; AU-064; asked in `source-health-canary §14 Q2 L162`).

**Options**

1. **README decision 5, made precise at two levels (recommended).**
   - A 403 is classified by reason first. A quota reason (YouTube's `quotaExceeded`) goes to quota-governor as `quota_exceeded`, key healthy (D2-Q057; `yt-video-details-fetcher §8 L171`). A 403 about one item (comments disabled, a private video) ends that item's series, key untouched (`yt-comments-fetcher §8 L155`). Only an authorisation 401 or 403 touches the credential.
   - An authorisation 401 or 403 on a client token or company app key marks that credential `revoked` (one attempt to refresh it first, where the platform allows) and stops the batch; every source that only that credential could read becomes `blocked`. No automatic fallback: an n8n card goes to ops and, for client-owned properties, to the client.
   - An authorisation 403 that concerns one source only (a removed bot, a suspended or private account, a missing page grant) makes that source `blocked`, not the credential.
   - A vendor key or plan error (401, 402, 403 or out of credits from a vendor) marks the key `degraded`; the route may fall back, decided by the canary only.
   - Route-wide states (`degraded`, `fallback`, back to `ok`) come only from the canary, from evidence across targets. The canary's route-wide `blocked`, when every active target and every token in use returns 401 or 403 (`source-health-canary §5.3 L72`, `§13 L151`), is kept, and only the canary sets it.
   - No government-watched green source ever moves to an amber route; registry-writer enforces it when applying a route-wide change (AU-064 option 1); a client-owned green property never falls back to a vendor (D2-Q052).
   - A green route not yet approved has no amber stand-in: while Page Public Content Access is pending, Page comments are not read through the vendor (`fb-post-comments-fetcher §14 Q5`).

   Consequences: a revoked client token never silently turns into vendor data; government contracts are protected in one place; F3 needs a credential state and reason beside `sources.health` (D2-Q016); every green fetcher's section 8 (CF-094 names fourteen sessions), CONVENTIONS L101 and the repository's error rule are aligned.

2. **CONVENTIONS L101 as written: fetchers mark the token or route `degraded`; only the canary sets `blocked`.** Consequences: fewer states; a revoked client token degrades its sources and the canary may fall back to a vendor automatically; the README's approval card disappears.
3. **Two levels without the README's no-fallback rule:** credential state set by fetchers, `blocked` for a lost grant on one source, and automatic fallback wherever a flag is on except for government-watched sources. Consequences: maximum coverage, but a client's revoked token can lead to vendor data about that client's property without anyone deciding it.

**Why the recommendation.** A platform's authorisation 401 or 403 usually means a client withdrew consent or a grant lapsed; answering with vendor data is a compliance risk, while a vendor's key problem is ours to route around. Option 1 keeps both README rules and gives each state one writer.

**Phase 2 records.** ADR "Platform 401/403, fallback and the government exclusion" (Applies to: F3, F4, F5, all fetchers, source-health-canary, registry-writer, quota-governor, listening-sdk). CONVENTIONS v1.1: L101 and L102 rewritten as in option 1; L113 gains "a government-watched green source never moves to an amber route; registry-writer enforces it". Rewordings citing the ADR (CLAUDE.md is the user's file; the text is proposed): `CLAUDE.md` L47, "401 and 403 are classified by reason: quota goes to quota-governor, an item-scoped one ends that item's series, an authorisation one marks the credential revoked or the source blocked and stops the batch; route-wide states come only from the canary"; `.claude/skills/review-session/SKILL.md` L22 and `.claude/agents/prd-reviewer.md` L16, "401 and 403 classified by reason (credential or source state, never a route state)" in place of "401 and 403 mark the route degraded and stop the batch" and "401 and 403 degrade and stop".

### D2-Q022 · News: the `news.dedup` topic, the per-host gate and the 7-day full-text cache (README decision 6)

- **Class:** technical (counsel confirms the cache reading before G2; see the last point of option 1)
- **Settles:** RD-6, CF-025, CF-092, CF-111, AU-003, AU-055, AU-104, news-article-extractor §14 Q1, news-article-extractor §14 Q3, news-dedup §14 Q1, normalize-item §14 Q2
- **Blocks:** F2 (the topic), F8 (the `item_stories` table), F4 and F5 (the host gate and the cache client in the SDK), C4, C5, C6, C13, C14, C15, A5, then N1 to N8, A1, A2, A3

**Context.** README decision 6 proposes three things (`README L183`), and D1 found a conflict in each:

- The topic `news.dedup`, from news-dedup "to normalize-item". news-dedup writes one message per verdict and per `story_update` (`news-dedup §6.2 L84` to `L101`) and expects normalize-item to copy the story fields onto the item and re-emit a version on updates (`§6.2 L104`), "with a bounded wait", or else drop the topic for a table-only join (`§14 Q1 L167`). normalize-item reads no such topic and has no story fields (`normalize-item §6.1 L86`; CF-025); aggregator and alert-evaluator expect them (AU-003).
- A per-host gate in listening-sdk, one connection and 2 to 5 seconds between requests. Only news-article-extractor doubles the spacing after a 429 or 503 (`news-article-extractor §5.3 L65`; CF-092 d). Which errors re-check the crawl policy differs: news-robots-checker wants a `recheck` on every 4xx, 429 included, and on a feed or sitemap 404/410 (`news-robots-checker §5.1 L47`); the fetchers back off on 429 and send a feed, sitemap or homepage 404/410 to news-site-resolver as `refresh` (`news-feed-poller §8 L131`, `news-sitemap-poller §8 L144`), while news-feed-poller's test says "Any 4xx from a host produces one `recheck` job" (`§13 L170`; CF-092, AU-104).
- news-article-extractor owns the 7-day full-text cache (`news-article-extractor §5.3 L75`) and passes `text_full_ref`, yet it and normalize-item still ask who owns it (`news-article-extractor §14 Q3 L189`, `normalize-item §14 Q2 L179`); news-comments-fetcher writes a second cache under `cache/news/comments/` (`news-comments-fetcher §5.2 L57`, `§6.2 L113`); and whether keyword-matcher and the analysis services may read it is open (`news-article-extractor §14 Q1 L187`, proposed yes, "to be confirmed with counsel"; CF-111, AU-055).

**Options**

1. **Keep all three, with these precisions (recommended).**
   - `news.dedup` joins the topic list, keyed by `story_id`. store-writer, not normalize-item, consumes it and writes a separate ClickHouse table, `item_stories` (`item_id`, `story_id`, `is_origin`, `duplicate_of`, `cluster_size`, `version`), one row per item, versioned like `items` so a `story_update` replaces the older row. aggregator and alert-evaluator join it to `items` on `item_id`. A content version from `items.normalized` (`normalize-item §5.2 L52`) and a story version never overwrite each other. news-dedup's `news_story_members` stays its own store; normalize-item stays a pure mapper with no wait.
   - The host gate lives in the SDK, for every news service: one connection per host, 2 to 5 seconds between requests or the host's `Crawl-delay`, and the spacing doubles after a 429 or 503 until a success. A 429 or a plain 503 backs off and never re-checks the policy; a 401, 402, 403, 451, any other 4xx not named here, or a challenge page whatever its status (Cloudflare's can be a 503) sends one `recheck` per host (coalesced) and stops the batch (`news-feed-poller §8 L132`); a 404 or 410 on a feed, sitemap or homepage sends `refresh` to news-site-resolver; a 404 or 410 on an article does neither.
   - Each cache writer owns its prefix, news-article-extractor `cache/news/`, news-comments-fetcher `cache/news/comments/`; both are registered in the SDK purge registry with the 7-day clock and deletion by `item_id`. Only keyword-matcher reads the cache, within the 7 days, and persists only derived values (hit offsets), so a brand named after the excerpt is still matched (AU-055). The analysis services read the stored title and excerpt, never the cache, "so a re-run reproduces live analysis" (`analysis-sentiment §5.1 L51`). Counsel confirms this reading of Law No. 3 of 1971 before G2 (`DEFERRED.md`, owner N6).

   Consequences: one news topic with a consumer, and one more ClickHouse table for F8; one gate; two registered cache prefixes; full-text matching within the cache window. News sentiment, topics and entities rest on the title and the 200 to 300 character excerpt (CONVENTIONS L213): shallower scores on long articles, but every score is reproducible after the cache expires.

2. **README decision 6 as written: normalize-item consumes `news.dedup` with a bounded wait and re-emits story fields as item versions.** Consequences: story fields reach every consumer of `items.normalized`, at the cost of a wait and a second emit in the busiest shared service; the gate and cache as in option 1.
3. **No topic: store-writer (or readers) join news-dedup's `news_story_members` table when they need stories.** Consequences: one topic fewer, but a cross-database join from ClickHouse readers into Postgres, and story updates are not events; the gate and cache as in option 1.

**Why the recommendation.** It keeps every part of the README proposal, gives the topic a consumer that already writes to ClickHouse while keeping story and content versions apart, fixes the gate once for all five news services, and lets matching see full text while analysis stays reproducible.

**Phase 2 records.** ADR "News: dedup topic, host gate and full-text cache" (Applies to: F8, every news service, normalize-item, store-writer, aggregator, alert-evaluator, keyword-matcher, the analysis services, listening-sdk, deletion-propagator, retention-purger). CONVENTIONS v1.1: `news.dedup` in the topic list; `item_stories` added to the analytics store's tables (L32); the host gate and error rules under the news fact sheet (L215); the cache prefixes and readers under object storage (L31). `DEFERRED.md`: counsel on matching over the cache (owner N6).

### D2-Q023 · Analysis: lanes, the `items.analysis` key, the ClickHouse `analysis` table and `model_versions` (README decision 7)

- **Class:** technical
- **Settles:** RD-7, CF-017, CF-050, CF-058, CF-075, AU-023, analysis-entities §14 Q1, analysis-media §14 Q4, analysis-sentiment §14 Q6, analysis-topics §14 Q5
- **Blocks:** F2, F3, F8, then C6, C15, A1, A2, A3, A4, A5
- **Depends on:** D2-Q042 (the `analysis_model_api` tag), D2-Q068 (the legal basis for platform media)

**Context.** README decision 7 proposes "a priority lane per task (`jobs.analysis-<task>.priority`) for tier-1 sources; `items.analysis/v1` keyed by `item_id:task:model_version` with an `input_hash`; budget tag `analysis_model_api` if a hosted model is chosen; YouTube audio and video are not downloaded in v1 (thumbnails only), pending legal review" (`README L184`). D1 found no conflict on thumbnails, and these elsewhere:

- lanes (CF-075 d): every analysis PRD has one priority lane per service, analysis-media's five tasks sharing `jobs.analysis-media.priority` (`analysis-media §5.1 L43`, `§6.2 L87`) and analysis-sentiment's two sharing `jobs.analysis-sentiment.priority` (`analysis-sentiment §6.1 L85`, `§6.2 L89`);
- the key (CF-075 b, CF-017 a): analysis-topics sends one message per taxonomy with `task = topics:<taxonomy_id>`, so its key has four colon-separated parts (`analysis-topics §5.2 L60`, `§6.2 L101`);
- the store (CF-017 c, CF-050, AU-023): store-writer keys `analysis` on `item_id, model`, versions it by `analyzed_at`, lets "a newer model version" replace the older, and reads `model` and `output`, which no writer sends (`store-writer §5.3 L61`, `L67`); its monthly partitions on `analyzed_at` never merge a re-score with the older row; the analysis PRDs keep re-runs "beside the old" until switch-over (`analysis-sentiment §5.1 L51`);
- `model_versions` (CF-058): four PRDs name parts of it (statuses, `analysis-sentiment §5.3 L76`; `thresholds`, `analysis-topics §5.3 L72`; one per media task, `analysis-media §5.3 L74`) and none a key, while aggregator, which should follow a switch-over, reads neither it nor more than "the latest `analysis` row per item and model" (`aggregator §5.3 L53`, `§6.1 L74`); topic ids are `node_id` in the message and `topic_id` in aggregator's grain (`analysis-topics §6.2 L111`, `aggregator §5.3 L55`).

At stake: rows of different tasks collapsing into one, and switch-overs that cannot be undone.

**Options**

1. **The README's key and versioning, with lanes per service (recommended).**
   - Lanes: `jobs.<service>.priority` and `jobs.<service>` for each analysis service, with tier 1 and client priority lists on the priority lane and push-covered sources by their tier (D2-Q049); a service with several tasks keeps a worker pool per task, as analysis-media does so that "slow video ASR never blocks image OCR" (`analysis-media §5.1 L43`).
   - Message: `analysis_key = item_id:task:model_version` with `input_hash`, plus `item_id`, `task` and `model_version` as separate fields, so nobody splits the string; task names contain no colon (`topics.<taxonomy_id>`); partitioned by `source_id` (D2-Q004); the item's `created_at` added as `item_created_at`.
   - ClickHouse `analysis` (store-writer): sorting key (`item_id`, `task`, `model_version`), version `produced_at`, partitioned by the item's `created_at` month like `items` (CF-050 option 1); columns named as in the message (`task`, `model_version`, `result`, `produced_at`); typed projections kept, entity ids among them, with no separate entity table (AU-023 c). Re-runs sit beside live rows.
   - `model_versions`: one row per (`task`, `model_version`) with `service`, `status` (`candidate`, `shadow`, `active`, `retired`), `thresholds` (jsonb), the artefact path under `models/`, the evaluation report and dates; at most one `active` row per task; written by each analysis service's release step, a switch-over being one status change (`analysis-sentiment §5.3 L76`). aggregator, and every other reader of `analysis`, takes the active version per task.
   - Topic ids: one field, `topic_id`, holding the `taxonomy_nodes` id namespaced by taxonomy (D2-Q048).
   - `analysis_model_api` joins the canonical tags (D2-Q042), used only if A1 to A4 choose a hosted model. YouTube: thumbnails only in v1; the legal basis is D2-Q068's.
   - OCR and transcript text as a second input (`analysis-media §14 Q4 L171`, `analysis-topics §14 Q5 L179`): deferred to A4, as an additive field when it comes.

   Consequences: store-writer and aggregator change columns and reads (C6, C15); analysis-topics renames its task; the README's lane names change; no approved PRD moves.

2. **README decision 7 literally: a lane per task, `jobs.analysis-<task>.priority`.** Consequences: matches the README, but analysis-media goes from two queues to ten (five tasks, two lanes each), task names must lose their colon to be valid topic names, and every analysis PRD's queue names change, for no gain over per-task worker pools.
3. **store-writer's design kept: its names become the message (CF-017 option 2) and the newest version replaces the older (CF-075 option 1, AU-023 option 2).** Consequences: fewer edits on the store side, but no side-by-side re-run, and a switch-over becomes an overwrite that cannot be rolled back.

**Open questions this also answers.** A knowledge-base release is a new `model_version` of analysis-entities, re-run side by side and switched over like any model (`analysis-entities §14 Q1`).

**Why the recommendation.** It keeps the README's key, `input_hash` and side-by-side versions, and makes the active version an explicit row that every reader consults; per-service lanes are what the four PRDs specify, with per-task isolation inside the service.

**Phase 2 records.** ADR "Analysis keys, store and model versions" (Applies to: analysis-sentiment, analysis-topics, analysis-entities, analysis-media, store-writer, aggregator). CONVENTIONS v1.1: L22 (the key and its fields), L28 (priority lanes `jobs.<service>.priority`), L30 (`model_versions`), L32 (the `analysis` key and partition). DEFERRED.md: OCR and transcripts as a second input (A4); GPU pool or model API (A1 to A4, build plan L65).

### D2-Q024 · TikTok: README decision 8 confirmed part by part

- **Class:** technical
- **Settles:** RD-8
- **Blocks:** F2, F3, then C11, TT1, VTT4, VTT5, VTT6
- **Depends on:** D2-Q010, D2-Q012, D2-Q034, D2-Q049, D2-Q052, D2-Q054

**Context.** README decision 8: "commenter identity is hashed inside the adapter before the first write (so `raw.items` is not byte-for-byte the vendor payload); tt-client-videos-fetcher writes its own +24 h and +7 d metrics and proposes a retention class `tiktok_display`; client-authorised accounts are `tier = push`" (`README L185`). D1 found a conflict in each part (CONFLICTS.md section 4, row 8): ten other services hash at the edge too (CF-109); the metrics come from outside comment-decay-scheduler and against the README's own list of count refreshers (CF-080 e, CF-082 b; `README L25`); `tiktok_display` is not in the class list (CF-104 b); and `push` sits on an account read hourly (`tt-client-videos-fetcher §5.1 L43`) and reconciled daily by the amber poller (CF-096 b). Each conflict is settled by another decision; this one confirms the README text as those decisions shape it.

**Options**

1. **Confirm each part, as settled elsewhere (recommended).**
   - Edge hashing: confirmed and generalised to every route (D2-Q010), so TikTok comments (`tt-video-comments-fetcher §5.3 L68`) are no longer an exception.
   - Metrics: tt-client-videos-fetcher is a named producer of its own +24 h and +7 d observations, taken from the first hourly read at or after each mark (`tt-client-videos-fetcher §5.1 L51`; D2-Q012), anchored and published as D2-Q034 decides; comment-decay-scheduler opens no metrics lane for green TikTok videos, so they never reach the amber tt-video-stats-refresher (`tt-client-videos-fetcher §14 Q5 L180`).
   - `tiktok_display`: whether the class is added, and with which clock, is D2-Q054's (user class).
   - "`tier = push`": the Display API is polled, not pushed (`tt-client-videos-fetcher §5.1 L43`), so the account keeps `push_covered = false` and its reach tier, and takes its cadence from the `owned_by_client` row of the cadence table (hourly, D2-Q049); a green client account is never reconciled through tt-profile-videos-poller (D2-Q052's recommendation).

   Consequences: nothing beyond the referenced decisions; tt-client-videos-fetcher's PRD cites them.

2. **Accept the README text literally.** Consequences: TikTok-only hashing, a `push` tier value that D2-Q049 removes, and a daily amber reconciliation of a green account; it contradicts D2-Q010, D2-Q049 and D2-Q052.
3. **Green TikTok metrics through comment-decay-scheduler like every other route (CF-080 option 2), as `metrics` jobs on tt-client-videos-fetcher's queue.** Consequences: no exception to the single emitter of metrics jobs, but a job for counts the hourly read already returns, and the scheduler must route TikTok metrics by `route`.

**Why the recommendation.** Each part of the README survives with the precision its conflict needed, and TT1 has nothing left to guess.

**Phase 2 records.** No ADR of its own: the ADRs of D2-Q010, D2-Q012, D2-Q034, D2-Q049, D2-Q052 and D2-Q054 each name tt-client-videos-fetcher. The README's decision 8 is reworded to point to them, with D2-Q070's README edits.

### D2-Q025 · New tables and stores named in one PRD (README decision 9)

- **Class:** technical
- **Settles:** RD-9, CF-059, RN-08, RN-09, alert-evaluator §14 Q1
- **Blocks:** F3, F8, then F4, C1, C2, C3, C6, C7, C10, C12, C13, C15, A1, A2, A3, A4, A5, FB4, TT1, VTT3, VTT5, X4, X6, X7, YT2, YT4, YT6, TG1, TG2, N6, N7, N8, W3, W5
- **Depends on:** D2-Q023, D2-Q036, D2-Q039, D2-Q040, D2-Q042, D2-Q045, D2-Q046, D2-Q047

**Context.** README decision 9 lists new control-plane tables proposed by single PRDs: `comment_series`, `backfill_runs`, `x_read_ledger`, `ig_hashtag_ledger`, `budget_reservations`, `budget_history`, `canary_targets` columns, `news_urls`, `news_stories`, `news_story_members`, `model_versions`, `taxonomy_nodes`, `kb_entities`, `kb_aliases`, `brand_assets` (`README L186`). CONVENTIONS lists the shared stores (Postgres L30, object storage L31, ClickHouse L32). D1 found the ledgers' keys and `model_versions` disputed (CF-038, CF-058; CONFLICTS.md section 4 row 9) and, counting CF-059's lines, 31 Postgres stores, seven ClickHouse names and twelve object-storage entries that only one PRD names, several holding item ids, hashes or URLs, plus stores several PRDs name that neither list has (CF-059 e). D1's review notes add `tg_thread_map`, "a service-private table" of tg-discussion-receiver (`tg-discussion-receiver §6.1 L110`) missing from INVENTORY §4.1 (RN-08), and lang-dialect-id's "registry `country_signals`" (`lang-dialect-id §3 L28`, `§5.3 L69`), a table name CF-059 does not list (RN-09). At stake: F3 and F8 create only what is agreed; anything else is invented by a build session, with no review of its key, its retention or its place in the purge registry.

**Options**

1. **Decision 9 accepted, stores another service reads join CONVENTIONS, private stores follow one rule (CF-059 option 2) (recommended).**
   - Decision 9's tables, with the owning PRD's columns: `comment_series` (`comment-decay-scheduler §6.3 L147`, key per D2-Q046), `backfill_runs` (`backfill-orchestrator §6.3 L112`, plus D2-Q020's window and reason), the two ledgers, `budget_reservations` and `budget_history` (`quota-governor §6.3 L107`, keys per D2-Q042), the `canary_targets` columns of `source-health-canary §6.3 L108`, `news_urls` (news-article-extractor's, D2-Q036), `news_stories` and `news_story_members` (`news-dedup §6.3 L108`), `model_versions` (D2-Q023), `taxonomy_nodes` (`analysis-topics §5.3 L68`), `kb_entities` and `kb_aliases` (`analysis-entities §5.3 L61`), `brand_assets` (`analysis-media §5.3 L68`).
   - Other stores that another service or an app reads join CONVENTIONS with a named owner: `registry_audit` (registry-writer, audit shape per D2-Q045), `x_compliance_audit` (x-compliance-sync), `alerts` (alert-evaluator) and `alert_rules` (read by alert-evaluator); the ClickHouse aggregates and views (D2-Q047); object-storage prefixes with one owner each (D2-Q039), model artefacts under `models/` written by each model's release step. Where a PRD names a writer only as an app, an admin page or curators (`alert_rules`, `brand_assets`, `kb_entities`, `kb_aliases`, x-filtered-stream's blocked-terms list, `x-filtered-stream §14 Q6 L210`), D3 specifies the writer.
   - Everything else is service-private: named with its owner's platform prefix or a short form of its name, read by no other service, listed in F3's `TABLE-OWNERS.md`, and registered in the SDK's purge registry (`deletion-propagator §5.3 L68`) when it holds item ids, hashes or URLs. Today: `tg_thread_map`, `yt_subscriptions`, `yt_live_watch`, `tt_client_video_state`, `x_compliance_runs`, `cc_hosts_seen`, `search_url_seen`, `search_candidate_seen`, `search_parked_urls`, `alert_deliveries`, `alert_watch_items`.
   - Settled by other decisions: the resolver caches (`profile_cache`, `poster_profiles`, `tt_user_cache`), `retention_audit` and the canary's audit trail (D2-Q045); the reply indexes, `comment_ledger` and `tt_comment_state` (D2-Q046); `news_sites` (D2-Q040); `hits` and the other ClickHouse names (D2-Q047); the Telegram onboarding records (D2-Q066). fb-reactions-fetcher's due-time table is not needed (D2-Q015, D2-Q046); aggregator's minute-grain table is not built in v1, and a later need goes through a proposal.
   - RN-08: `tg_thread_map` is tg-discussion-receiver's private table under the rule; INVENTORY stays D1's record (D2-Q070). RN-09: "registry" there means `sources` (`CONVENTIONS L30`), so the PRD reads `sources.country_signals`, a wording fix.

   Consequences: F3 and F8 build the shared list and nothing else; each build session creates its private tables under the rule, and its review checks them; the PRDs that name these stores gain an owner line; registry-writer's `registry_audit` (approved) is confirmed.

2. **Every listed store joins CONVENTIONS with its PRD's columns, private ones marked private (CF-059 option 1).** Consequences: one complete list, but F3 freezes every private schema before its service exists, duplicates included (the resolver caches, the comment indexes).
3. **Each store reviewed one by one in D2 (CF-059 option 3).** Consequences: the most precise, but D2 designs tables that belong to build sessions, and the duplicates are D2-Q045's and D2-Q046's anyway.

**Why the recommendation.** Only stores another service reads need to be contract; a naming rule, an owner list and the purge registry keep private state reviewable and deletable without freezing it early.

**Phase 2 records.** ADR "New tables and service-private stores" (Applies to: all). CONVENTIONS v1.1: L30 (the shared Postgres tables with their owners), L31 and L32 (with D2-Q039 and D2-Q047), and the rule for private stores (naming, `TABLE-OWNERS.md`, purge registry). `lang-dialect-id §3 L28` and `§5.3 L69` reworded.

## Group 3 · The foundation choices

The build plan's foundation table (FC-01 to FC-13) lists the choices D2 settles before the foundation sessions start. Three of them are settled inside earlier decisions: FC-02 (one writer per column) in D2-Q013, FC-03 (`item_id` derivation) in D2-Q006 and FC-04 (schema versioning) in D2-Q002. FC-01 ("accept the nine README decisions unless D1 finds a conflict") needs no decision of its own: D1 found conflicts against all nine (CONFLICTS.md section 4), so each is decided on its own in Group 2. The decisions below take the rest. F1, already merged, built three of them (FC-10, FC-11, FC-13), so D2-Q030 only ratifies what exists.

### D2-Q026 · Kafka client libraries for the two SDKs

- **Class:** technical
- **Settles:** FC-05
- **Blocks:** F4, F6 (and every service through them)

**Context.** The build plan proposes `@confluentinc/kafka-javascript` for Node and `confluent-kafka` for Python, both on librdkafka (build plan L55). F1 already uses the Node client in the stack acceptance tests (`docs/handoffs/F1.md` L81) and recorded it in `docs/dependencies.md` (MIT, bundling librdkafka under BSD-2-Clause; Confluent, Inc., US; screen "clear"); its prebuilt binary installs on the pinned Node 24 (`onlyBuiltDependencies` in `pnpm-workspace.yaml`, `docs/handoffs/F1.md` L81). Redpanda speaks the Kafka API, so any Kafka client works. What matters for the contracts is that the Node SDK (F4) and the Python SDK (F6) produce and consume identically: "partitioned by `source_id` so one source is never worked twice at once" (CONVENTIONS L28) holds only if both SDKs put the same key on the same partition, and the cursor rule ("cursors advance only after the batch is acknowledged by Redpanda", CONVENTIONS L71) needs the same acknowledgement and idempotent-producer semantics in both.

**Options**

1. **Both clients on librdkafka, as proposed, with the partitioner set explicitly (recommended).** F4 uses `@confluentinc/kafka-javascript`, F6 uses `confluent-kafka`; both SDKs set `partitioner = murmur2_random` (the Java-compatible hash, which Redpanda's own tools and other Kafka clients also use), `enable.idempotence = true` and `acks = all`, and a shared conformance test proves a key lands on the same partition from both languages. Consequences: one underlying library, so retries, batching and error codes match across languages; the explicit partitioner avoids librdkafka's default (`consistent_random`, a CRC32 hash) disagreeing with any non-librdkafka producer, for example a tool or an n8n flow that writes to a topic. F6 adds `confluent-kafka` (Apache-2.0, Confluent, Inc., US) to `docs/dependencies.md`.
2. **Pure-language clients: KafkaJS for Node and aiokafka for Python.** Consequences: no native binary, but two unrelated implementations whose default partitioners differ, so both SDKs must pin one by hand; KafkaJS's maintenance status would have to be checked before relying on it.
3. **`node-rdkafka` for Node with `confluent-kafka` for Python.** Consequences: also librdkafka, but `node-rdkafka` is a separate binding with its own release cadence; F1's tests would move to it.

**Why the recommendation.** Option 1 is what F1 already proved, keeps one engine under both SDKs and fixes the one setting (the partitioner) that would otherwise break per-source ordering between languages.

**Phase 2 records.** ADR "Kafka clients" (Applies to: F4, F6, all services). CONVENTIONS v1.1, under the event bus: the client per language and the three producer settings.

### D2-Q027 · Where the platform runs: the cluster and object storage

- **Class:** user (a hosting provider, its accounts and its running cost are the owner's to choose)
- **Settles:** FC-06, FC-07
- **Blocks:** I1 (it cannot start without this), then C2 (raw-archiver's buckets), I2, E2 and the gates G2 to G4; the account itself is something only the user can open (`docs/orchestration/README.md`, "What only the user can supply")

**Context.** CONVENTIONS already names Hetzner servers and "Backblaze B2 or Hetzner Object Storage" (CONVENTIONS L3) and leaves the orchestrator open: "Kubernetes or Nomad; the PRDs say 'the cluster'" (CONVENTIONS L12). The build plan proposes k3s (a lightweight, standard distribution of Kubernetes, the common system for running containers on a group of servers) on Hetzner "unless your team already runs Nomad" (HashiCorp's simpler alternative to Kubernetes) (FC-06) and Hetzner Object Storage as primary with Backblaze B2 as the off-site copy of the raw archive (FC-07). Both vendors are on CONVENTIONS' cleared list (L6). Constraints from the briefs: TLS from Let's Encrypt with no Cloudflare dependency, and the Telegram webhook endpoint outside Iraq (I1 brief, "Watch for"; CONVENTIONS L200). The raw archive is the platform's replay source (raw-archiver), so losing it loses the ability to reprocess; that is the reason for an off-site copy.

**Options**

1. **k3s on Hetzner, Hetzner Object Storage primary, Backblaze B2 off-site copy of `raw/` (recommended).** Consequences: one vendor for compute and primary storage in the EU, outside Iraq; k3s is standard Kubernetes, so ready-made install packages (Helm charts) and operators (programs that install and run a database such as Redpanda or ClickHouse on the cluster) and ordinary Kubernetes skills apply; the B2 copy covers the loss of a Hetzner region or account. The B2 copy holds identifiable raw data, so it is a second archive, not a backup: every lifecycle rule and deletion rewrite that retention-purger and deletion-propagator apply to the primary (`raw-archiver §4 L37`, `§5.3 L73`) is applied to it too, and the lifecycle feature, which differs between B2 and Hetzner, is tested on both (`raw-archiver §12 L163`); backups in the sense of D2-Q069 (d) are the databases' snapshots; I1 prices both before staging, and the user opens the Hetzner and Backblaze accounts.
2. **Nomad on Hetzner instead of k3s, same storage.** Consequences: worth it only if the team already runs Nomad, as the build plan says; fewer ready-made operators for Redpanda and ClickHouse, so I1 writes more of its own job specifications.
3. **Hetzner Object Storage only, no off-site copy.** Consequences: lower cost and one account fewer; a provider-level loss would lose the raw archive and with it every replay and reprocessing.
4. **Another provider (named by the user).** Consequences: it goes through the vendor screen (CONVENTIONS L6) and `docs/dependencies.md` first; I1's brief, which is written for Hetzner, changes.

**Why the recommendation.** It matches CONVENTIONS and the build plan, uses only cleared vendors, keeps the hosting outside Iraq and protects the one store that cannot be rebuilt.

**Phase 2 records.** ADR "Hosting: cluster and object storage" (Applies to: I1, I2, C2, E2, all services through "the cluster"). CONVENTIONS v1.1, L12: "the cluster" is k3s on Hetzner; L3 and the object storage line (L31): Hetzner Object Storage primary, Backblaze B2 off-site copy of `raw/`.

### D2-Q028 · lang-dialect-id in Python, its callers, and Arabizi

- **Class:** technical
- **Settles:** FC-08, CF-112, AU-074, AU-075, lang-dialect-id §14 Q1, lang-dialect-id §14 Q2, lang-dialect-id §14 Q3, lang-dialect-id §14 Q4, poster-resolver §14 Q3
- **Blocks:** F4 (the Node SDK's language client), C3, F7 (the fold in both languages), F6 (the Python SDK carries one more service), then C8, VLI2, A1, A4

**Context.** CONVENTIONS allows Python only for the analysis workers and the news extractor (CONVENTIONS L13). lang-dialect-id needs CAMeL Tools and KLPT, which are Python libraries: "Runtime: Python, because CAMeL Tools and KLPT are Python libraries" (`lang-dialect-id §9 L150`), and it asks to confirm a third exception or port the fold to TypeScript (`lang-dialect-id §14 Q1 L187`; CF-112). The build plan proposes Python with a TypeScript copy of the fold for fallback (FC-08), and the session plan already assumes it: C3 needs F6 (the Python SDK) and F7 (the fold and its golden corpus) first (`build-plan/SESSIONS.md`). F7 builds the folds "in TypeScript exactly as lang-dialect-id section 5.3 C defines them" with a golden corpus "both languages' code must pass" (F7 brief). Two smaller points ride on the same service. Its callers: lang-dialect-id names normalize-item as "the only caller of `/v1/detect`" (`lang-dialect-id §4 L34`, `§6.1 L99`), while poster-resolver sends it a sample of up to 20 recent posts per candidate (`poster-resolver §5.2 L58`), li-org-resolver asks the SDK's "language client" for a language share (`li-org-resolver §5.2 L56`), news-site-resolver takes one "from lang-dialect-id over the last 20 titles" (`news-site-resolver §5.2 L52`) and analysis-media sends transcripts (`analysis-media §5.3 L66`) (AU-074). And Arabic written in Latin letters (Arabizi): analysis-sentiment routes it through transliteration (`analysis-sentiment §5.2 L57`), but lang-dialect-id reads Arabizi "as `en` or `und`" (`lang-dialect-id §12 L164`), keeps transliteration out of scope (`§3 L29`) and asks whether to add a Latin-script Arabic class after the pilot (`§14 Q3 L189`); F7's brief records Arabizi as "not transliterated (documented gap)" (AU-075). The service already sets `script` (`arab`, `latn`, `mixed` or `none`, `lang-dialect-id §5.2 L51`, `§5.4 L92`), which normalize-item copies (`§6.2 L105`); but `latn` cannot tell Arabizi from English, since Latin tokens count as `en` (`§5.3 L63`).

**Options**

1. **Python service, recorded as the third exception, with the fold also in TypeScript (recommended).** lang-dialect-id runs on the Python SDK (F6) with CAMeL Tools, KLPT and fastText; F7's TypeScript fold is byte-identical to the Python one on the golden corpus; it is a fallback only, used if the service is unreachable, since keyword-matcher and CI tools call `/v1/fold` (`lang-dialect-id §6.1 L99`). Its callers are named: normalize-item; the resolvers that compute `lang_share` under D2-Q033, ig-account-resolver, li-org-resolver and news-site-resolver (profile samples, through a batch form of `/v1/detect` wrapped by the SDK's language client), not poster-resolver, which reads their shares; and analysis-media (transcripts), and the service's pool is sized for them (AU-074 option 1). Arabizi gets no route in v1: `script` stays exactly as defined, the model does not measure Arabizi, and analysis-sentiment drops its transliteration branch. The pilot measures it by hand-labelling a sample of `latn` items, and an Arabizi class is considered after the pilot as `lang-dialect-id §14 Q3 L189` asks (AU-075 option 3). Consequences: CONVENTIONS L13 gains one exception; one golden corpus guards both implementations; no new field for F2 or C3; Arabizi posts are read as `en` or `und` and scored by the fallback model or left unscored in v1, a known gap measured only by the pilot's sample.
2. **Port the fold to TypeScript and keep only fastText and the dialect model in Python.** Consequences: the exception narrows to a model server but does not disappear; the CAMeL and KLPT behaviour the PRD relies on must be reimplemented and kept equal by hand.
3. **Node only, with fastText through WebAssembly and no CAMeL Tools or KLPT.** Consequences: no Python exception, but the Iraqi-dialect and Sorani features the PRD names are lost or rebuilt from scratch; not recommended.

**Open questions this also answers.** lang-dialect-id's other open points: Kurmanji (Badini) stays `other` in v1, a documented gap like Arabizi, with a label considered after the pilot (`§14 Q2`); `items.normalized` carries the top dialect class and its confidence, the full `dialect_scores` vector staying in lang-dialect-id's own evaluation log (`§14 Q4`, a vector can be added later under D2-Q002). The callers that send profile samples are the resolvers that compute `lang_share` (D2-Q033), through the SDK's batch call (`poster-resolver §14 Q3`).

**Why the recommendation.** It is the plan the build sequence already follows, it uses the libraries the PRD is built on, and the shared golden corpus removes the risk of two folds drifting. Naming the callers sizes the service for its real load, and the Arabizi gap stays as F7 and lang-dialect-id planned it, sized by the pilot before any class is built.

**Phase 2 records.** ADR "lang-dialect-id in Python" (Applies to: C3, F4, F6, F7, normalize-item, keyword-matcher, poster-resolver, ig-account-resolver, li-org-resolver, news-site-resolver, analysis-media, analysis-sentiment). CONVENTIONS v1.1, L13: "... and lang-dialect-id (Python, CAMeL Tools and KLPT; the fold also in TypeScript, both checked against F7's golden corpus)". `DEFERRED.md`: the pilot's hand-labelled `latn` sample and an Arabizi class after it, owner C3.

### D2-Q029 · ClickHouse topology and the three environments

- **Class:** user (how much to pay for redundancy before production, and when, is the owner's call)
- **Settles:** FC-09, FC-12, store-writer §14 Q2
- **Blocks:** F8 (replication settings in the migrations), I1, E2, G2, G4

**Context.** The build plan proposes one ClickHouse node with backups in staging and a replicated pair before production (FC-09), and three environments: local with the fake platform only, staging with real APIs on small budgets, and production (FC-12). The volume target is about 1,000,000 new posts and comments a day and ten years of aggregates (CONVENTIONS L3). F8 writes the migrations. Replication (two ClickHouse servers holding the same data, so one can fail) needs ClickHouse Keeper, a small coordination service that tracks which server has which data, and "replicated" table types, either from the first migration or through a later migration that converts the tables. Staging is where real API keys and vendor spend first appear (G2: "staging with real data"); the probes (FB0, X0, YT0 and the others) and their spend need the user's yes per call list anyway (`docs/orchestration/README.md`).

**Options**

1. **As proposed (recommended).** Staging: one ClickHouse node with daily backups. Production: a replicated pair with ClickHouse Keeper (three small Keeper nodes, or Keeper on the cluster's control-plane nodes) before G4. F8 writes the tables with replicated engines from the start, so the same migrations run on one node and on the pair. Prerequisite: an embedded Keeper and the `{shard}` and `{replica}` macros in the local, CI and staging ClickHouse configs, since F1's local stack has neither (`compose.yaml`, `stack/`; F8 changes the `clickhouse-local` config, `docs/handoffs/F1.md` L120). Environments: local (fake platform, no network), staging (real APIs, each budget tag capped at a small figure the user sets per tag before G2), production. Consequences: the lowest cost until production; replication is proven in G4 rather than from day one.
2. **Replicated from staging.** Consequences: a higher ClickHouse cost from G2 (two nodes instead of one, plus Keeper); replication and failover are exercised for longer before production.
3. **One node in production as well, with backups.** Consequences: cheapest; a node loss stops ingestion and dashboards until a restore, and the restore point is the last backup.

**Why the recommendation.** The data volume reaches production scale only in production; one node is enough to prove the pipeline in staging, while writing replicated engines from the first migration keeps the move to a pair a deployment change rather than a schema change.

**Phase 2 records.** ADR "ClickHouse topology and environments" (Applies to: I1, F8, E2, G2, G4). CONVENTIONS v1.1, analytics store (L32): replicated engines from the first migration; one node in staging, a pair in production; the embedded Keeper and macros in the local, CI and staging configs (F8, with I1 for staging). The staging caps per budget tag go into G2's plan.

### D2-Q030 · Ratify the tooling, local stack and dependency policy F1 built

- **Class:** technical
- **Settles:** FC-10, FC-11, FC-13
- **Blocks:** F2 (the schema pipeline), every session (the toolchain)

**Context.** F1 merged with the tooling, local stack and dependency policy of the build plan (FC-10, FC-11, FC-13): pnpm 10.34.6 and Turborepo 2.10.13 with strict TypeScript 6.0.3, ESLint and Vitest 4.1.11; uv 0.12.23 with ruff, pyright and pytest 9.1.1; a docker compose stack with Redpanda v26.1.18, the Supabase CLI 2.120.0, ClickHouse 26.3.38.2 and SeaweedFS 4.48 as local S3; and `docs/dependencies.md` with a CI policy check (`docs/handoffs/F1.md`, "Decisions made here" and "For the sessions that depend on this"). One part of FC-10 is not built yet: "Zod 4 to JSON Schema to Pydantic", which is F2's pipeline (F2 brief: "Zod schemas for every topic, job and envelope; JSON Schema export; Pydantic models for Python").

**Options**

1. **Ratify what F1 built, and fix F2's pipeline as Zod 4 to JSON Schema to Pydantic (recommended).** F2 writes the schemas in Zod 4, exports JSON Schema (draft 2020-12) with Zod's own exporter, and generates Pydantic v2 models from it (for example with `datamodel-code-generator`, recorded in `docs/dependencies.md`); conformance tests in both languages run the same valid and invalid fixtures. Consequences: no change to anything merged; TypeScript is the source of truth, which matches the Node majority of services.
2. **JSON Schema as the hand-written source, generating Zod and Pydantic from it.** Consequences: a language-neutral source, but every schema is written in a format nobody runs, and Zod types lose the refinements Zod expresses directly.
3. **A schema registry with Avro or Protobuf (Redpanda ships one).** Consequences: compatibility checks enforced by the broker, but every PRD example and the SDKs move from JSON to a binary format; a larger change than the PRDs assume.

**Why the recommendation.** It ratifies a merged, tested foundation and keeps F2's pipeline as the build plan wrote it.

**Phase 2 records.** ADR "Tooling, local stack and dependency policy" (Applies to: all). No CONVENTIONS change beyond naming the schema pipeline in the repository section (L12).

## Group 4 · Topics and messages

### D2-Q031 · Keyword hits: what `item.hits` and `discovery.hits` carry, and who writes them

- **Class:** technical
- **Settles:** CF-009, CF-010, CF-011, AU-005, AU-006, AU-008, AU-012, AU-054, AU-061, analysis-sentiment §14 Q7, fb-keyword-search §14 Q5, keyword-matcher §14 Q2, keyword-matcher §14 Q3, search-hit-router §14 Q3, tt-hashtag-feed-poller §14 Q4, web-commoncrawl-scanner §14 Q3, yt-channel-resolver §14 Q1
- **Blocks:** F2, F4, C4, C5, C6, C7, C8, C9, A1, A5, FB6, VFB1, VFB2, IG2, VTT2, X1, TG1, TG2, VTG1, W3, W5
- **Depends on:** D2-Q010 (`author_ref`), D2-Q032 (candidate keys and the group resolver), D2-Q044 (the keyword behind a hashtag source)

**Context.** CONVENTIONS splits hits by whether the poster is registered (L17, L18) and makes keyword-matcher "the canonical writer of `item.hits` and `discovery.hits` for items", with early signals from x-recent-search and tg-message-search and candidates from three source finders (L281). The PRDs depart from this:

- Writers. tg-message-search also writes `item.hits` (`tg-message-search §5.2 L55`), so one Telegram post gives two hits in two shapes (CF-009 a); ig-hashtag-search and the two Telegram receivers write `discovery.hits` without being listed (CF-010 b; client onboarding is D2-Q066's).
- Meaning. keyword-matcher sends comments and author-less items to `item.hits` as individuals' mentions (`keyword-matcher §5.3 L75`, `§14 Q3 L182`), which L17 does not cover, while a mention on an unregistered poster's post exists only on the candidate topic.
- Shape. Seven layouts, two under one schema name, three partition keys (CF-011). The source finders defer to "poster-resolver's approved schema" (`search-hit-router §6.2 L134`, `web-commoncrawl-scanner §6.2 L103`), which does not exist (`poster-resolver §6.1 L81`; AU-008). analysis-sentiment reads `matched_text`; keyword-matcher writes `matched_term` (`analysis-sentiment §5.2 L59`, `keyword-matcher §5.3 L65`; AU-006).
- Gaps. x-recent-search's `context.discovery_hit_emitted` flag never reaches keyword-matcher (`x-recent-search §5.2 L58`; AU-005); two PRDs name readers that read other topics (AU-012); a hashtag-feed video is a hit "without text matching" for tt-hashtag-feed-poller (`tt-hashtag-feed-poller §4 L34`) but needs a match in keyword-matcher (AU-054); nobody emits the group behind an amber group hit, so rule 8 never fires (`fb-keyword-search §1 L9`, `qualifier §5.2 L59`; AU-061).

What is at stake: mentions counted twice or not at all, and a poster-resolver that cannot decode its own input.

**Options**

1. **Every keyword hit on `item.hits`; `discovery.hits` carries candidates only (recommended).**
   - `item.hits/v1` is keyword-matcher's message (`keyword-matcher §6.2 L97-L117`) with `poster {author_ref, author_type, author_source_id}` and a new `matched_by` (`text` or `source`): one per (item, client, keyword), keyed by `source_id`, whoever the poster is; comments and individuals' posts carry `author_ref` only. keyword-matcher is its only writer; tg-message-search stops. store-writer fills `hits` from this topic only (D2-Q047), and analysis-sentiment reads only this topic.
   - `discovery.hits/v1`, one F2 schema for every candidate, keyed by `candidate_key` (a named exception in D2-Q004): `candidate {candidate_key, platform, type, platform_id, handle, url}`, `evidence_type` (closed: `keyword_hit`, `container`, `early_signal`, `page_search`, `web_search`, `commoncrawl`), `item_id` or `url`, the producing `source_id`, `keyword_ids`, `client_ids`, `hit_at`, provenance and `retention_class` (D2-Q003), and one optional typed `evidence` block per type. `poster`, `poster_ref`, `origin`, `found_at`, `item_idempotency_key` and the singular client and keyword fields go.
   - Writers: keyword-matcher, once a poster's identity is readable (the `candidate_pending` message goes, since the mention is already out); x-recent-search and tg-message-search as early signals, both kept, poster-resolver deduplicating by `candidate_key` (the flag goes); fb-page-search, search-hit-router, web-commoncrawl-scanner. ig-hashtag-search writes none: its media of unmanaged accounts name no poster (`ig-hashtag-search §6.2 L124`) and stay mentions with a null `author_ref`; its caption-handle path (`§12 L169`) goes, as a handle in a caption is not the poster. The Telegram receivers write none: client onboarding takes registry-writer's manual path (D2-Q066). A web result that D2-Q038 turns into a `web` item raises no candidate for its domain: search-hit-router writes a candidate only for a platform account or a news site it routes.
   - Groups: for a hit on a post in an unregistered Facebook group, keyword-matcher also emits a `container` candidate `facebook:group:<id>`, read from the raw record; D2-Q032 gives it a resolver.
   - Hashtag sources: an item from a hashtag source is a hit for each client of that source who passes the client gate, under the source's keyword (D2-Q044), with `matched_by = source` when the text does not match; the `hit_id` formula (`keyword-matcher §5.3 L77`) makes the two one hit.
   - `matched_term` plus `offsets` in `text_norm` is the one form; analysis-sentiment cuts its window from `offsets`.
   - Readers: `raw.items` is read by normalize-item, raw-archiver and news-dedup, `discovery.hits` by poster-resolver; the PRDs' reader lists are corrected.

   Consequences: one counting path for mentions; one candidate message per item and candidate, not per client and keyword; approved PRDs move under D2-Q001 (tg-message-search, x-recent-search, ig-hashtag-search, fb-page-search, tt-hashtag-feed-poller, poster-resolver's partition note, and the "split into `item.hits` or `discovery.hits`" reader lines of tt-keyword-search, li-post-search and yt-keyword-search).

2. **CONVENTIONS' split kept, with keyword-matcher's `discovery.hits/v1` as the one schema, `candidate` required and source-finder fields optional (CF-011 option 1).** Consequences: fewer moves, but store-writer must store some `discovery.hits` messages and drop others, one schema serves two purposes, and the pending-candidate message stays.
3. **tg-message-search keeps writing `item.hits`, and keyword-matcher skips items whose producer already did (CF-009 option 2).** Consequences: two writers to keep in step, and a skip rule resting on a flag that, as AU-005 shows, does not travel.

**Open questions this also answers.** keyword-matcher reads an unregistered poster's id from a transient `poster_platform_id` field that normalize-item sets on `items.normalized` only for posters not yet classed, and that store-writer never stores; `candidate_pending` is dropped (`keyword-matcher §14 Q2`).

**Why the recommendation.** Each topic gets one meaning, a mention for a client or a candidate for the registry, so a mention counts once wherever its poster stands, and every candidate reaches poster-resolver in one layout, ordered per candidate.

**Phase 2 records.** ADR "Keyword hits and candidates" (Applies to: F2, keyword-matcher, poster-resolver, store-writer, analysis-sentiment, the search services and source finders). CONVENTIONS v1.1: L17 and L18 (the two meanings), L281 (writers, early signals, no `item.hits` from search services), the topic partition note (`discovery.hits` by `candidate_key`).

### D2-Q032 · Resolvers: who publishes profiles, one `resolve` job, and refreshes of registered sources

- **Class:** technical
- **Settles:** CF-012, CF-073, CF-085, AU-007, AU-056, AU-059, AU-111, AU-112, fb-page-resolver §14 Q1, poster-resolver §14 Q2, tt-user-resolver §14 Q2, x-user-resolver §14 Q6, yt-channel-resolver §14 Q5
- **Blocks:** F2, F4, C7, C8, C9, FB1, IG1, IG2, VTT3, VTT6, X2, VLI2, VLI3, VTG2, VTG3, YT1, YT9, N2, W3, W4, W5
- **Depends on:** D2-Q017 (`jobs.completed`), D2-Q033 (the profile schema), D2-Q050 (flags)

**Context.** poster-resolver, an approved PRD, sends each candidate a `resolve` job with `"reply_to":"jobs.poster-resolver"`, waits there for `resolved` or `unresolvable`, merges the answers into `poster.profiles`, and after 5 unanswered attempts marks the candidate `unresolvable: timeout` (`poster-resolver §1 L9`, `§5.3 L67`, `L70`, `§8 L107`). No resolver writes that queue: all eight publish `poster.profiles` themselves (`fb-page-resolver §6.2 L99`, `ig-account-resolver §6.2 L102`, `tt-user-resolver §6.2 L86`, `x-user-resolver §6.2 L101`, `li-org-resolver §6.2 L79`, `tg-channel-resolver §6.2 L77`, `yt-channel-resolver §6.2 L103`, `news-site-resolver §6.2 L79`), so as written every candidate times out (CF-012, AU-007). The job differs per queue (CF-085, AU-056, AU-111): most resolvers read `client_ids`, which poster-resolver's job lacks; li-org-resolver re-keys candidates as `linkedin:org:<handle>` (`li-org-resolver §5.2 L50`); a flag that is off ends three ways (`poster-resolver §5.2 L56`, `tt-user-resolver §5.2 L53`, `li-org-resolver §5.2 L53`). Routers emit keys no resolver parses (`search-hit-router §5.3 L74-L83`; CF-073), and some producers that resolvers name emit nothing (CF-085 d, e). Six resolvers refresh registered sources on their own loops under two kind names; tt-user-resolver has no loop, and li-org-resolver waits for `refresh` jobs from the qualifier, which emits none (`li-org-resolver §5.1 L44`, `qualifier §6.2 L81`; AU-059, AU-112). What is at stake: as written no candidate is ever resolved, and tiers on TikTok and LinkedIn go stale.

**Options**

1. **Resolvers publish their own profiles; poster-resolver dispatches, deduplicates and caches (recommended).**
   - Each resolver classifies `account_type` with rule 1 and applies the individuals rule through one SDK function, then writes `poster.profiles` in D2-Q033's schema, archiving its raw response as `profile` (D2-Q008) for non-individuals only. poster-resolver consumes `poster.profiles` into `poster_profiles` (the one cache, D2-Q045) and drops `reply_to`, the answer kinds, merging and its own signal computation, and tg-channel-resolver stops reading `poster.profiles` as a cache (`tg-channel-resolver §6.1 L73`); it writes the topic only to re-emit a cached profile with `cached: true` on a repeat hit (`poster-resolver §5.2 L53`). It learns from `jobs.completed` that a job ended without a profile, instead of a 15-minute timer: the candidate waits, and the next hit dispatches it again.
   - One `resolve` job for all eight queues: `job_id`, `kind`, the issued `candidate_key` (echoed, never re-keyed; poster-resolver aliases a handle to the returned id, `§12 L134`), `platform`, `platform_id`, `handle` or `url`, `origin` (`discovery`, `manual`), `client_ids`, `seed_list`, `attempt`, `due_at`; priority derived by the SDK (D2-Q018). `reply_to`, `hit_url`, `sample_posts`, `url_or_handle` and tg-channel-resolver's `candidate` go. Kinds: `resolve` (poster-resolver), `refresh`, `ops_force` (the admin API, D2-Q012).
   - Flag off, one outcome: poster-resolver sends no job (D2-Q050); a queued job ends `skipped_flag_off`; no profile, the candidate waits. `unresolvable: route_off` and `vendor_route_off` go, so no candidate is rejected for 180 days because a flag was off.
   - Keys: CONVENTIONS' two forms for accounts, plus `facebook:group:<id>` and `news:site:<registrable domain>` for candidates that are not accounts; routers map every other form before emitting (D2-Q037). Group candidates go to fb-page-resolver, which gains an amber path behind `FB_VENDOR_ROUTE`: one vendor read of the group's recent posts (name, member count where returned, last post, a sample), built after the Facebook vendor probe (VFB0).
   - Producers: `resolve` comes only from poster-resolver, which also carries registry-writer's manual candidates (`registry-writer §5.2 L61`; li-org-resolver's `seed` origin goes); the qualifier, web-gdelt-poller and yt-web-search-bridge send none. The event-triggered `refresh` jobs to news-site-resolver from the three news pollers and news-comments-fetcher (`news-comments-fetcher §8 L139`) stay, as named producers (D2-Q012). An unreadable Telegram channel goes to registry-writer as a source-level `health_change` (D2-Q016) and to ops, not to the qualifier.
   - Refresh: every resolver refreshes its registered sources on its own 30-day loop with `kind = refresh` (`rotation` renamed); tt-user-resolver and li-org-resolver gain one, its cadence a setting the pilot can lengthen on amber routes; ig-account-resolver seeds a due time for registered accounts that lack one. A refreshed profile carries `source_id`, and the qualifier turns a crossed tier boundary into `tier_change` (`qualifier §8 L106`).

   Consequences: one decision per resolution; approved PRDs move under D2-Q001 (poster-resolver above all, li-org-resolver, tg-channel-resolver, news-site-resolver, the qualifier, registry-writer, yt-web-search-bridge); the `individual_leak` test moves to the SDK function.

2. **Resolvers answer on `jobs.poster-resolver` and only poster-resolver writes `poster.profiles`, as its PRD says.** Consequences: eight resolver PRDs change their writes and need an answer schema; poster-resolver keeps merging and stays the single writer, at the cost of one more hop; the job, key, flag and refresh points stand as in option 1.
3. **Both write, each message marked answer or merged profile, and the qualifier decides only on merged ones.** Consequences: two layouts on one topic and twice the messages for the same facts.

**Open questions this also answers.** Each resolver archives its own raw lookups as `profile` records on `raw.items` (D2-Q008), individuals minimised as D2-Q010 says (`poster-resolver §14 Q2`).

**Why the recommendation.** It keeps what eight PRDs already do and changes one, needs no answer queue, and gives every key a router emits a resolver that can parse it.

**Phase 2 records.** ADR "Resolvers and the resolve job" (Applies to: F2, listening-sdk, poster-resolver, the eight resolvers, the qualifier, registry-writer, search-hit-router, web-commoncrawl-scanner, yt-web-search-bridge). CONVENTIONS v1.1: L19 (writers of `poster.profiles`), L277 (`resolve` and `refresh` kinds), L281 (the typed candidate forms). `DEFERRED.md`: the refresh cadence on amber resolvers, owners VTT3 and VLI2.

### D2-Q033 · The `poster.profiles` message and the Iraqi-signal vocabulary

- **Class:** technical
- **Settles:** CF-013, CF-014, AU-009, ig-account-resolver §14 Q4, li-org-resolver §14 Q3, poster-resolver §14 Q4, qualifier §14 Q2
- **Blocks:** F2, F3, F4, C3, C7, C8, C9, FB1, IG1, VTT3, X2, X5, VLI2, VTG2, YT1, N2
- **Depends on:** D2-Q010 (`author_ref`), D2-Q032 (resolvers publish profiles)

**Context.** The qualifier reads "every field listed in the `poster-resolver` PRD" (`qualifier §5.4 L71`): a flat message with `account_type`, `individual`, `cached`, `unresolvable`, `country_signals {iraqi_place, phone_964, iq_domain, outlet_link, seed_list}` and `lang_share {ar_iq, ckb, ar_msa, en}` (`poster-resolver §6.2 L89`). The eight resolvers write four nested and four other flat layouts, with five names for the classification and four for the cache flag (CF-013), nine signal vocabularies in three JSON types (CF-014), and keys that change with the outcome, one of which can carry an individual's handle (CF-013 f). `ar_iq` and `ar_msa` are labels lang-dialect-id never returns (`lang-dialect-id §3 L22`, `§5.3 L67`). The profile lacks what rules 4 and 6 read, and three resolvers expect outcomes the rules do not produce (AU-009). Two open questions ask where the Iraqi city, governorate and outlet lists live: "a list in `keywords` or a static list in the SDK" (`poster-resolver §14 Q4 L156`, `qualifier §14 Q2 L153`). What is at stake: a signal counted on one platform and missed on another, and rules the qualifier cannot evaluate.

**Options**

1. **One flat schema built from the ten rules, closed vocabularies, one shared reference table (recommended).**
   - `poster.profiles/v1`, flat, with D2-Q002's metadata, D2-Q003's provenance and `retention_class` (the class of the route that fetched the profile, D2-Q003). Required, null where the platform gives nothing: `candidate_key`, `source_id` (refreshes), `platform`, `source_type`, `account_type`, `individual`, `status` (`resolved`, `review`, `unresolvable`) with a closed `reason`, `platform_id`, `handle`, `url`, `display_name`, `followers`, `verified`, `posts_30d`, `last_post_at`, `posts_per_day`, `duplicate_text_share`, `default_avatar`, `account_created_at`, `owned_by_client`, `country_signals`, `lang_share`, `client_ids`, `keyword_ids`, `route`, `vendor`, `resolved_at`, `cached`, `cached_until`, `review_flags`. Resolver-specific fields (category, `uploads_playlist_id`, growth, the news `site_profile`) go in an optional `extras` object. One name each: `account_type` (`individual` is true exactly when `account_type` is `individual`), `cached`, and `post_count`, which x-full-archive-search reads instead of `tweet_count` (`x-full-archive-search §5.2 L52`). A news site's profile (news-site-resolver's `proposed_source`) also carries the pre-allocated `proposed_source_id`, which the qualifier's `add` passes on (D2-Q040).
   - Expected outcomes: `review` with its reason covers Telegram's `not_indexed` and age-gated Instagram accounts; `review_flags` carry watchlist-only X passes and hidden YouTube subscriber counts; an empty LinkedIn sample sets `last_post_at = null`, which rule 3 reads as dormant, as li-org-resolver intends.
   - Keys: partition key `candidate_key` as issued (a refresh uses the source's id form). An individual's answer is keyed by `author_ref` (D2-Q010), carries no handle, no handle-based key and none of `display_name`, `url`, `country_signals` or `signal_evidence`, only what the qualifier may read of an individual (the hash, follower count and verified flag, `qualifier §5.4 L71`), plus the resolve `job_id` so poster-resolver can match it (`x-user-resolver §6.2 L132` already does this).
   - `country_signals`: six booleans, `iraqi_place` (an Iraqi city or governorate named in the location, bio, title or masthead), `platform_country_iq` (the platform's or vendor's own country field says Iraq), `phone_964`, `iq_domain`, `outlet_link`, `seed_list`, plus `signal_evidence` (what matched, and where) for review cards. Rule 2 counts `iraqi_place` or `platform_country_iq` as one location signal, never two, as two resolvers assume (`tg-channel-resolver §5.4 L67`, `tt-user-resolver §12 L150`).
   - `lang_share`: shares over the sample keyed by lang-dialect-id's labels (`ar`, `ckb`, `en`, `mixed`, `other`, `und`), plus `ar_iraqi` (posts labelled `ar` with dialect `iraqi`) and `sample`; rule 2 reads `ar_iraqi + ckb`. Below a minimum sample (a setting, tuned in the pilot) it is null and not counted. The sample is the posts the resolver's own call returns (Instagram Business Discovery media, the LinkedIn Actor's posts, news titles), else the candidate's items already labelled in ClickHouse, found by `author_ref`.
   - Each resolver computes the signals with one SDK function. Its lists (Iraqi governorates and cities in Arabic, Sorani and Latin spellings; Iraqi outlet domains, registered news sites included) live in one control-plane reference table read through the SDK, created and seeded by F3, edited through the admin console (D3 specifies the writer).

   Consequences: F2 types one message; every resolver's example changes; the qualifier reads the rule-4 and rule-6 fields and the location rule above; approved PRDs move under D2-Q001 (the qualifier, poster-resolver, li-org-resolver, tg-channel-resolver, news-site-resolver); F3 adds the reference table.

2. **One envelope plus a per-platform `profile` object, with a required common block of the qualifier's fields (CF-013 option 2).** Consequences: resolvers keep most of their layouts, but the vocabularies of option 1 are still needed and every consumer parses two levels.
3. **Each resolver keeps its block, and the qualifier documents a mapping per platform (CF-014 option 3).** Consequences: no resolver changes, but nine mappings to test, and `sources.country_signals` holds blocks that cannot be compared.

**Why the recommendation.** The qualifier's rules define what a profile must say, so the schema follows them, and fixed keys make rule 2 count the same evidence on every platform. One table keeps resolvers and review cards on the same lists; a static SDK list would change only with a release, and rows in `keywords` are per client, so a candidate could be Iraqi for one client and not another.

**Phase 2 records.** ADR "Poster profiles and Iraqi signals" (Applies to: F2, F3, the eight resolvers, poster-resolver, the qualifier, registry-writer, listening-sdk). CONVENTIONS v1.1: L36 (keys and types of `country_signals` and `lang_share`), L243 (the location signal), L30 (the reference table). `DEFERRED.md`: the minimum language sample, owner C9.

### D2-Q034 · Engagement counts: one writer per observation, the `item.metrics` message and metrics jobs

- **Class:** technical
- **Settles:** CF-018, CF-019, CF-081, AU-004, AU-031, AU-084, fb-reactions-fetcher §14 Q1, ig-account-media-poller §14 Q3, li-notification-receiver §14 Q4, store-writer §14 Q5, tt-video-stats-refresher §14 Q2, tt-video-stats-refresher §14 Q4
- **Blocks:** F2, F8, C4, C6, C11, FB2, FB4, FB7, IG3, TT1, VTT6, LI1, LI2, LI3, VTG3, YT4
- **Depends on:** D2-Q005 (`job_kind` on the raw envelope), D2-Q008 (the archive-only `metrics` kind)

**Context.** CONVENTIONS refreshes counts at +24 h and +7 d "by the source's metrics or details service, or by the next poll where the API returns counts with the post" (L65). normalize-item emits "one `item.metrics` observation per record that carries counts" (`normalize-item §5.2 L56`); fb-reactions-fetcher, an approved PRD, emits another for every green Facebook post it reads on `raw.items` (`fb-reactions-fetcher §5.1 L39`), and yt-video-details-fetcher writes a `first_sight` observation "from the same response" as its record (`yt-video-details-fetcher §3 L19`), so one fetch yields two observations (CF-018 b). No PRD commits to the LinkedIn counts that li-notification-receiver and li-own-comments-fetcher read (CF-018 c). The messages have two layouts, `observation` as a string or an object, and no `item_id`, while store-writer keys `metrics_timeseries` on `item_id, observed_at` (`store-writer §5.3 L62`; CF-019). Jobs and labels differ: comment-decay-scheduler emits `kind = metrics` with `+24h` and `+7d` counted from first sight (`comment-decay-scheduler §5.1 L60`, `L68`); fb-reactions-fetcher expects `refresh_24h` and `refresh_7d` due at `created_time` plus the step (`fb-reactions-fetcher §5.1 L41`); yt-video-details-fetcher expects `24h` and `7d` from `publishedAt` (`yt-video-details-fetcher §5.1 L45`); the TikTok services label `plus_24h` (CF-081, AU-031). `webhook_reconcile` has no producer (AU-084), and li-notification-receiver asks whether reaction events become counter increments (`li-notification-receiver §14 Q4 L201`; AU-004). What is at stake: double-counted growth curves and refresh jobs nobody accepts.

**Options**

1. **One observation per read, from one writer; one flat message; steps counted from the post's creation time (recommended).**
   - Writers. A read whose records go to `raw.items` as items (polls, searches, backfills, pushes, first-sight details reads) gets its observation from normalize-item, labelled from the envelope's `job_kind` (D2-Q005). A read made only to observe counts (a `metrics` job, a client refresh, tt-client-videos-fetcher's +24 h and +7 d, D2-Q024) is written by the reading service, which writes no item record for it and may archive the response as the archive-only kind `metrics` (D2-Q008). So fb-reactions-fetcher drops its extract mode and its `refresh_*` kinds, yt-video-details-fetcher drops its `first_sight` observation, and ig-account-media-poller writes the observation for a `metrics` job's posts instead of re-emitting them (`ig-account-media-poller §5.1 L52`). normalize-item's LinkedIn mapper names the count fields of li-client-posts-poller's records, which makes it the producer of LinkedIn counts. A record that carries no counts, such as a Page webhook's change value (`fb-client-webhook-receiver §6.2 L129`), gives no observation (AU-084).
   - `item.metrics/v1`, flat: D2-Q002's metadata, `item_id`, the item's `idempotency_key`, `platform`, `platform_id`, `source_id`, `created_at` (the post's creation time), `observation {label, step, observed_at}`, `metrics {views, likes, comments, shares, reactions_by_type}` (null where a platform has none), provenance and `retention_class` (D2-Q003), so store-writer needs no lookup (`store-writer §14 Q5 L185`). Route extras (`channel_id`, `live_state`, `regressed`) are optional declared fields; `age_seconds` and `lateness_seconds` are derived by readers.
   - Labels, closed: `first_sight` (an item's first observation), `poll`, `backfill`, `refresh` (`step` `+24h`, `+7d` or `refresh:<request_id>`), `ops_force`, `live_end`; `webhook_reconcile`, `refresh_24h`, `refresh_7d`, `refresh_client`, `plus_24h`, `24h` and `7d` go. normalize-item stamps `observed_at` with the record's `fetched_at`, so a replay rewrites the same row; a metrics service checks (`item_id`, `step`) before it calls, so a replayed job writes nothing new.
   - Jobs: `kind = metrics` with `post_ref` (D2-Q011) and `series_step` `+24h`, `+7d` or `refresh:<request_id>`, emitted by comment-decay-scheduler only (D2-Q012). The metrics lane counts from the platform's creation time, so "engagement at 24 h" is the same post age on every platform; a step already past at first sight is skipped. The comment lane keeps first sight (D2-Q060).
   - LinkedIn: absolute observations only; reaction events produce no counter increments.

   Consequences: one row per read in `metrics_timeseries`; approved PRDs move under D2-Q001 (fb-reactions-fetcher, normalize-item's LinkedIn mapper); the hourly first-day Facebook series comes from normalize-item's metrics-only outcomes on each re-poll (`normalize-item §5.2 L52`); comment-decay-scheduler keeps two anchors; tt-video-stats-refresher and tt-client-videos-fetcher move from first sight to creation time.

2. **Every count read goes through `raw.items`, and normalize-item writes all of `item.metrics` (CF-019 option 3).** Consequences: one writer and one shape, but count-only responses become records normalize-item must map, against D2-Q008's archive-only `metrics` kind, and four services are rebuilt as raw producers.
3. **As option 1, but counted from first sight, as comment-decay-scheduler and the TikTok services write.** Consequences: one clock in the scheduler, but a post first seen at 20 hours gets its "+24 h" point at 44 hours, so 24-hour and 7-day engagement cannot be compared across routes; fb-reactions-fetcher and yt-video-details-fetcher change instead.
4. **Both writers kept, store-writer keeping one row per item, time and label (CF-018 option 3).** Consequences: no writer changes, but growth curves still need de-duplication by label at read time.

**Open questions this also answers.** `item.metrics` carries `source_id` (its partition key) and the item's `created_at`, so store-writer needs no lookup (`store-writer §14 Q5`); `saves` is an optional count where the platform returns it (`tt-video-stats-refresher §14 Q4`).

**Why the recommendation.** It removes the duplicate without moving work: polls already carry counts into normalize-item, and only the services that make count-only calls write their own. Counting steps from creation time is what makes the 24-hour and 7-day views comparable.

**Phase 2 records.** ADR "Engagement observations" (Applies to: F2, F8, normalize-item, comment-decay-scheduler, store-writer, fb-reactions-fetcher, ig-account-media-poller, yt-video-details-fetcher, tt-video-stats-refresher, tt-client-videos-fetcher, the LinkedIn services). CONVENTIONS v1.1: L23 (the message), L65 (who writes which observation, and the creation-time anchor), L277 (`metrics` steps).

### D2-Q035 · Deletions: one message, one remover, a guard against resurrection, and recompute

- **Class:** technical
- **Settles:** CF-020, CF-021, CF-055, CF-076, CF-093, AU-013, AU-022, AU-076, AU-077, AU-082, alert-evaluator §14 Q3, deletion-propagator §14 Q2, retention-purger §14 Q2, tt-client-videos-fetcher §14 Q3, x-compliance-sync §14 Q4, x-compliance-sync §14 Q5, yt-replies-fetcher §14 Q4
- **Blocks:** F2, F3, F8, F4, C2, C4, C6, C13, C14, C15, A1, A2, A3, A4, A5, FB4, FB5, FB7, VFB3, IG6, TT1, VTT5, VTT6, X6, X7, LI1, LI2, LI3, VLI4, YT2, YT4, YT5, YT6, YT7, N8
- **Depends on:** D2-Q006 (the `item_id` helper), D2-Q010 (`author_ref`), D2-Q017 (`jobs.completed`)

**Context.** deletion-propagator requires `reason`, `scope` and a target (`deletion-propagator §5.4 L80`). Producers send a long form with `source_id` and `client_id` at the top (`retention-purger §6.2 L96-L107`), a short form with just `idempotency_key` and `detected_at` (`fb-post-comments-fetcher §6.2 L125`; CF-020), and unlisted values (CF-076, AU-076): `text_only`, `fetched_before`, `derived` with `purge_derived` (`yt-text-purger §5.3 L106`, `L118`), `withhold` with `countries` and `user_ids` (`x-compliance-sync §5.3 L77`, `L81`), a TikTok revocation reason. aggregator reconciles on the topic before the item is gone (`aggregator §5.1 L37`), alert-evaluator needs `item_id` (`alert-evaluator §14 Q3 L165`; AU-013), several stores sit outside the purge registry (`deletion-propagator §5.3 L68`; AU-077), and deletion-propagator waits for a `done` aggregator never sends (CF-021, CF-093, AU-082). `deletion_requests` mixes people's requests with per-message state (CF-055), and the resurrection guard exists twice: tombstones that store-writer's version formula ranks below content, and a check by `item_id` on a table keyed by `deletion_id` (`deletion-propagator §5.3 L62`, `store-writer §5.2 L49`, `§5.3 L67`; AU-022). Open questions: a removed parent's replies (`yt-replies-fetcher §14 Q4 L193`) and X withholding (`x-compliance-sync §14 Q4 L201`, `§14 Q5 L202`). What is at stake: deletions rejected, stalled or undone by a replay, under X's 24-hour rule.

**Options**

1. **One schema, one remover, one guard (recommended).**
   - `deletions/v1`, deletion-propagator's 5.4 completed: D2-Q002's metadata, `deletion_id` (an SDK hash of the whole sorted target), `reason`, `scope`, `mode`, `target`, `retention_class`, `signal_at`, `due_at`, optional `requested_by`, `run_id`, `event_at`. `source_id` appears once, at the top, as the partition key (author scope `author_ref`, client scope `client_id`, D2-Q004). Fetchers build it with the SDK from the item's key, so an item-scope target carries `item_ids` (D2-Q006) besides `platform`, `kind` and `platform_ids`; `detected_at` becomes `signal_at`.
   - Closed lists in F2. Reasons: `platform_sync` (X compliance included), `retention`, `author_request`, `client_offboarding`, `legal`, `authorization_revoked` (`tiktok_display`, D2-Q054; the alert spelt the same). Scopes: `item`, `author`, `source`, `client`. Modes: `delete`, `purge_text`, `purge_derived` (rows and analysis removed, no recompute; anchor per D2-Q056), `withhold`. Target extras: `fetched_before`, `countries`, and `user_ids` for registered X sources only (an individual is targeted by `author_ref`, D2-Q010). yt-text-purger sends `text_only` as `item` with `purge_text`, as retention-purger does (`retention-purger §6.2 L99`), and `derived` as `item` with `purge_derived`.
   - `withhold` (Iraq among `countries`) hides the item from clients, recomputes and notifies, erasing nothing; content withheld only outside Iraq is counted, with no message, as proposed. The X fetchers do not request `withheld` in v1; the daily compliance run is the one source unless its results prove to carry no country codes (`x-compliance-sync §14 Q2 L199`).
   - Only deletion-propagator removes data. Every store of item text, ids or hashes joins the SDK purge registry: the text index, both news caches (D2-Q022), the annotation store and A0's evaluation sets (D2-Q068), analysis-media's OCR and transcripts (media through raw-archiver's references), x-replies-fetcher's reply index, fb-post-comments-fetcher's `comment_ledger`, poster-resolver's cache and every service-private table under D2-Q025's rule. alert-evaluator (from its watch set, whose rows the registry clears), comment-decay-scheduler and retention-purger still read the topic to react; aggregator stops.
   - Cascades by `parent_id`: a deleted post removes its comments and a deleted comment its replies, except on X (`deletion-propagator §5.3 L60`); yt-replies-fetcher emits nothing.
   - Recompute: deletion-propagator sends bucket-list `recompute` jobs (`source_id`, hours, keyword ids) for any age; aggregator (which also takes the admin API's date-range job) reports on `jobs.completed`, closing the `recomputed` step; a frozen bucket (`aggregator §5.3 L61`) is reported as such and accepted.
   - Tables: `deletion_requests` keeps people's requests only (contact, handle until hashed, status, resulting `deletion_id`s); a propagation table keyed by `deletion_id`, with a child table of resolved `item_id`s, holds state, verification, notices and `sla_met`, written by deletion-propagator, read by the purgers and raw-archiver's replay filter.
   - Guard: tombstones only: `items` and `comments` gain `is_deleted`, one SDK version formula ranks a tombstone above every content version, store-writer drops upserts for tombstoned ids and its `deletion_requests` check goes. Re-ingestion after an author request is D2-Q069's (`retention-purger §14 Q2 L171`).

   Consequences: one schema and one remover to test; F3 adds two tables, F8 a column; fetchers stop hand-building messages, fb-reactions-fetcher included (an approved PRD moves under D2-Q001, with D2-Q062); aggregates change once per deletion.

2. **A short form beside the long form, and every holder consuming `deletions` itself (CF-020 option 2, CF-021 option 2).** Consequences: each holder builds its own purge and report, and more consumers must meet X's 24 hours.
3. **`deletions` for removal only; YouTube text purges and X withholding through their own paths (CF-076 option 3).** Consequences: deletion-propagator stays as written, but two producers build their own purge or hide logic, each with its own archive rewrite.

**Open questions this also answers.** A client's revocation of a TikTok Display grant deletes its items with reason `authorization_revoked`, one of the closed reasons (`tt-client-videos-fetcher §14 Q3`). X `withheld` status is requested by every X reader and recorded on the item, never as a deletion (`x-compliance-sync §14 Q5`).

**Why the recommendation.** One missed store is a breach, so one service removes everything and proves it, from one message built the same way by every producer; one version rule makes a deletion survive replays.

**Phase 2 records.** ADR "Deletions" (Applies to: F2, F3, F8, deletion-propagator, every `deletions` producer, store-writer, aggregator, alert-evaluator, raw-archiver, the services with registered stores, listening-sdk). CONVENTIONS v1.1: L24 (the topic and its closed lists), L30 (the two tables), L32 (`is_deleted`), L63 (the SDK helper for `platform_sync`). `DEFERRED.md`: reversing a lifted X withholding, owner X7.

### D2-Q036 · News URLs and articles: keys, the `article.urls` message and the URL ledger

- **Class:** technical
- **Settles:** CF-022, CF-028, CF-118, AU-105, AU-106, RN-10, news-dedup §14 Q3
- **Blocks:** F2, F3, C4, N2, N3, N4, N5, N6, N7, N8, W3
- **Depends on:** D2-Q003 (provenance), D2-Q059 (no Common Crawl backfill in v1)

**Context.** The article key is `news:article:<canonical_url_hash>` (CONVENTIONS L69), with no rendering for the hash: news-article-extractor and news-dedup write bare hex (`news-article-extractor §6.2 L98`, `news-dedup §6.2 L90`), while search-hit-router writes `news:article:sha256:<hex>` (`search-hit-router §6.2 L123`) against its own prose and test (`§9 L159`, `§13 L184`). The news pollers key `article.urls` by a URL-level `url_key = news:url:<sha256 of normalised URL>` (`news-feed-poller §9 L142`; CF-118). `article.urls` has two layouts: the pollers' `{envelope, payload}` with `url_key`, `found_via` and `found_at` and no schema name (`news-feed-poller §6.2 L94-L112`), and the router's flat `article.urls/v1` with `idempotency_key`, `found_by` and `first_seen_at` and no provenance or class (`search-hit-router §6.2 L119-L131`); the extractor orders its work by `found_via` and `found_at` (`news-article-extractor §5.1 L43`), and CONVENTIONS lets source finders write `discovery.hits` only (L281; CF-022). normalize-item maps a `date` field the extractor writes as `published_at` (`normalize-item §5.3 L72`, `news-article-extractor §6.2 L114`; CF-028). The extractor's ledger `news_urls` is keyed by `url_hash` (`news-article-extractor §5.2 L51`, `§6.3 L129`), possibly the same hash as `url_key` (RN-10). Copies naming another URL as canonical are recorded `duplicate_canonical`, a status the ledger lacks, and news-dedup's sweep would add them under the origin's key, its members' primary key (`news-dedup §5.3 L64`, `§6.3 L108`; AU-106). Four PRDs count on `not_article` rates reaching news-site-resolver, which reads no outcome (`news-article-extractor §6.2 L125`, `news-site-resolver §6.1 L75`; AU-105). What is at stake: one article under three keys that never compare equal.

**Options**

1. **Bare hex everywhere, one URL key on `article.urls`, one ledger hash (recommended).**
   - Keys: `news:article:<64 lower-case hex>`, built by the contracts package's key helper (D2-Q006); search-hit-router strips `sha256:`, and `canonical_url_hash` is bare hex on `search.results` and `article.urls` too (D2-Q037).
   - `article.urls/v1`, flat, one schema for the three pollers and search-hit-router: D2-Q002's metadata, `source_id` (the site), `url`, `url_key`, `found_via` (closed: `feed`, `news_sitemap`, `homepage_diff`, `sitemap_backfill`, `web_search`; `commoncrawl` has no producer in v1, D2-Q059), `found_at`, provenance and `retention_class` (D2-Q003); optional finder fields (`title`, `published_at`, `feed_url`, `feed_format`, `canonical_url`, `canonical_url_hash`, `snippet`, `engines`, `keyword_ids`, `client_ids`). The router maps `found_by` to `found_via = web_search` and `first_seen_at` to `found_at`, and CONVENTIONS L281 names it as a writer of `article.urls`. The message carries no article key: the extractor derives it from the canonical URL it reads on the page (`news-article-extractor §5.2 L57`), which may differ from the engine's URL, so the router's `idempotency_key` goes. The access mode comes from `crawl_policies` (D2-Q040).
   - RN-10: one SDK helper, `url_hash = sha256(normalised URL)`, with one normaliser for every finder and the extractor; `url_key = news:url:<url_hash>`, and `news_urls` is keyed by `url_hash`.
   - normalize-item maps `published_at` (an approved PRD moves under D2-Q001).
   - Same-canonical copies: `news_urls.status` gains `duplicate_canonical`; the copy keeps its own `url_key`, under which the sweep adds it to `news_story_members` (text fields null, `matched_by = canonical`), so it never collides with the origin's key.
   - `not_article` feedback, no new message: the extractor's outcomes are its `news_urls` rows, and news-site-resolver reads them for the site (`status`, `found_via`) on every refresh and infers patterns from accepted and `not_article` URLs, which also gives homepage-diff sites patterns. news-site-resolver adds the read (an approved PRD moves under D2-Q001).

   Consequences: one key per article and one per found URL; the pollers' envelope and the router's flat message become one message; the router's test and prose change.

2. **The `sha256:` rendering everywhere (`news:article:sha256:<hex>`, `news:url:sha256:<hex>`) and the pollers' envelope as the one layout (CF-118 option 2, CF-022 option 1).** Consequences: CONVENTIONS L69, the extractor and news-dedup change, for a key that names its algorithm.
3. **search-hit-router stops writing `article.urls` and hands news URLs to the news finders (CF-022 option 3).** Consequences: matches L281's wording, but an article that search found waits until the site's own feed lists it (`search-hit-router §1 L11`), and the finders need an input they lack.

**Why the recommendation.** It is what the extractor, news-dedup and the three pollers already write, it removes the one key that never matches, and it leaves the extractor alone to decide what an article is.

**Phase 2 records.** ADR "News URL and article keys" (Applies to: F2, F3, the news pollers, news-article-extractor, news-dedup, news-site-resolver, search-hit-router, normalize-item). CONVENTIONS v1.1: L25 (the `article.urls` message), L69 (bare hex and `news:url:`), L281 (search-hit-router writes `article.urls`). RN-10 closed.

### D2-Q037 · The web-search path: `search.results`, raw archiving, the YouTube bridge and routing

- **Class:** technical
- **Settles:** CF-023, AU-011, AU-029, AU-108, AU-109, AU-110, search-hit-router §14 Q1, search-hit-router §14 Q4, web-search-mojeek §14 Q4
- **Blocks:** F2, C1, C2, C4, C8, FB1, IG1, YT1, YT4, YT9, W1, W2, W3, W4, W5
- **Depends on:** D2-Q008 (the archive-only `search_response` kind), D2-Q032 (candidate keys), D2-Q036 (hash rendering)

**Context.** The three engines write `search.results/v1` with a `query` object, a `result` object, `canonical_url_hash` and `retention_class` (`web-search-perplexity §6.2 L92-L108`; web-search-mojeek and web-gdelt-poller use the same shape) and archive every response on `raw.items` with `kind_hint = search_response` and `normalize = skip` (`web-search-perplexity §5.2 L55`). yt-web-search-bridge, an approved PRD, writes another layout with `query` as a string and no `schema`, `message_id` or class (`yt-web-search-bridge §6.2 L106-L124`); it marks results `handled_by` so that search-hit-router skips them, which the router never reads (`§4 L37`, `search-hit-router §5.2 L55`; CF-023); and it archives nothing although its PRD says raw-archiver does (`yt-web-search-bridge §8 L148`; AU-011). web-commoncrawl-scanner writes under `raw/` directly (`web-commoncrawl-scanner §5.2 L54`; AU-029). web-search-perplexity, also approved, serves `site_search` jobs for the bridge, which sends none and calls Mojeek and Perplexity itself (`web-search-perplexity §3 L25`, `yt-web-search-bridge §5.2 L58`; AU-108). The router emits candidate keys no resolver takes, and the bridge sends `resolve` jobs that bypass poster-resolver (AU-109). Three engines count on the router to judge results Iraqi and to report yields back; the router judges nothing Iraqi (`search-hit-router §5.4 L89`; AU-110). What is at stake: every bridge result parked or routed twice, paid responses never archived, and engine metrics with no source.

**Options**

1. **One results schema, every response archived, one router for YouTube links (recommended).**
   - `search.results/v1` is the engines' message, for all four producers: D2-Q002's metadata, `engine`, `source_id` (the keyword rule, D2-Q004) with the `keyword_ids` and `client_ids` it serves (D2-Q044), `query {text, variant, lang, country, request_id}` (an object everywhere; `lang` is the language asked for, whatever the engine's mechanism, null for GDELT), `result {rank, title, url, snippet, date, last_updated}`, `canonical_url`, `canonical_url_hash` (bare hex, D2-Q036), `raw_ref`, provenance and `retention_class` (D2-Q003); optional `hints` (GDELT). The bridge's `idempotency_key`, `platform_hint`, `handled_by`, `cost` and `extracted` go.
   - Archive: each engine and the bridge write every response to `raw.items` as the archive-only kind `search_response` (D2-Q008), replacing `kind_hint` and `normalize = skip`; since normalize-item skips the kind, an unknown response shape is parked by the engine's adapter. web-commoncrawl-scanner archives its per-host aggregate the same way and writes nothing under `raw/` (D2-Q039). `search.results` is derived data and is not archived.
   - The bridge calls Mojeek (by default) and Perplexity itself through the shared SDK clients, on the tags `mojeek_search` and `perplexity_search` with its own sub-counter (D2-Q042). `site_search` leaves web-search-perplexity, and web-search-mojeek's line about it goes.
   - Routing: search-hit-router routes every YouTube link, the bridge's included, and the bridge sends no jobs. A watch, shorts or youtu.be URL becomes a `first_sight` job on `jobs.yt-video-details-fetcher` with the rule's `source_id` (one id per job, D2-Q065), so the video becomes an item and its channel reaches poster-resolver as keyword-matcher's candidate; `@handle` and `channel/UC…` URLs become `youtube:<handle or id>` candidates; legacy `c/` and `user/` names, and Instagram URLs with no readable handle, end `unroutable`; groups and sites take the typed keys of D2-Q032. The router's 30-day re-route window replaces the bridge's 7-day sent set.
   - Iraqi-ness: judged by the qualifier after resolution. The engines drop `variant_yield`, `iraqi_host_share`, `unique_domain_share` and a reported-back `items_new_total`; yield per engine and variant comes from the router's metrics (`search-hit-router §10 L164`) and a pilot report joining its `search_url_seen` and `search_candidate_seen` rows to the qualifier's `decisions`. Retiring a variant is a manual pilot decision; no feedback loop in v1.

   Consequences: approved PRDs move under D2-Q001 (yt-web-search-bridge loses its jobs and `handled_by`, web-search-perplexity loses `site_search`); search-hit-router replaces the bridge as a producer of `first_sight` jobs in D2-Q012's table, and yt-video-details-fetcher names it; the bridge's spend shows under the engines' caps.

2. **The bridge sends `site_search` jobs to the engines, which call, archive and publish, and keeps routing its own YouTube results, marked `handled_by`, which the router counts and skips (AU-108 option 1, CF-023 option 1).** Consequences: the router learns one skip rule, but two services turn YouTube links into jobs, and the bridge's `resolve` jobs still bypass poster-resolver unless they change too.
3. **The bridge stops writing `search.results` (CF-023 option 2).** Consequences: the router has three producers, the bridge's results reach nothing else, and the bridge must still archive its responses.

**Why the recommendation.** Routing web links is search-hit-router's job, so giving it the YouTube links too removes a second router, the skip marker and the direct resolver jobs; archiving every response through `raw.items` gives every paid result its provenance.

**Phase 2 records.** ADR "Web-search results path" (Applies to: F2, web-search-perplexity, web-search-mojeek, web-gdelt-poller, web-commoncrawl-scanner, yt-web-search-bridge, search-hit-router, yt-video-details-fetcher, raw-archiver). CONVENTIONS v1.1: L26 (the `search.results` message), L281 (engines archive responses; the router routes YouTube links). `DEFERRED.md`: variant retirement from the pilot report, owner W3.

### D2-Q038 · Should web pages that are neither news nor social posts become mentions that clients see?

- **Class:** user (a product-scope choice: whether blogs, forums and other web pages count as mentions in client views)
- **Settles:** CF-110
- **Blocks:** F2, C4, C5, YT9, W1, W2, W3, W4
- **Depends on:** D2-Q008 (the `result` kind), D2-Q037 (the results path), D2-Q054 (the retention class of web results)

**Context.** Web search (Perplexity, Mojeek, GDELT) returns links: social posts, news articles, and other pages such as blogs, forum threads, and company or public bodies' pages. The documents disagree on what happens to that last kind. CONVENTIONS says a search service writes every item it finds into the pipeline, so that it can become a mention (L281), and normalize-item, an approved PRD, already turns a Perplexity or Mojeek result into an item with its title, snippet and date (`normalize-item §5.3 L73`). The web PRDs, though, only archive the engines' responses and send the results to search-hit-router (`web-search-perplexity §5.2 L55`), which turns social links into candidate sources and news links into articles to fetch, and counts everything else as `web` with nothing emitted (`search-hit-router §5.2 L63`). As written, a client never sees a blog or forum page that names its brand, and normalize-item's web mapper has no input. Their share of results is to be measured in the pilot (`search-hit-router §2 L17`).

The choice is wider coverage of the open web against more low-value mentions and a new kind of item in client views. Social posts and news articles found by search are handled alike under every option.

**Options**

1. **Other web pages become mentions, only where nothing else covers them (recommended).** Results still go to search-hit-router; for a Perplexity or Mojeek result it cannot route to a platform or to the news extractor, the router writes a `web:result:<canonical_url_hash>` item (kind `result`, D2-Q008) to `raw.items` with the keyword rule's `source_id`: title, snippet, URL and engine, under `news_excerpt` (D2-Q054), mapped by normalize-item's existing web mapper (`normalize-item §5.3 L73`). keyword-matcher confirms the keyword in the title or snippet before it counts, and raises no candidate for the domain, which the router has already judged. GDELT's unrouted results stay counted only, as no mapper covers them. Consequences: clients see blog, forum and site mentions under the platform `web`; no page appears twice, since links that become posts or articles are never written as web items; storage is a title and a snippet per page; CONVENTIONS L281 names the router as a `raw.items` writer for these results; noise is handled by the client's keywords and exclusions, as for any mention.
2. **Routing only: web results never become mentions themselves.** The web PRDs as written: search finds social sources and news articles, other pages are counted and dropped, and normalize-item's web mapper is removed (an approved PRD moves under D2-Q001). Consequences: the least work and no web noise for clients, but a brand named only on a blog, forum or company page is never shown; CONVENTIONS L281 is reworded for web search.
3. **Every result becomes a mention, as CONVENTIONS reads.** Each engine writes every result as a web item, besides routing it. Consequences: the widest coverage, but a news article or social post found by search also appears as a web snippet, so twice unless a de-duplication rule is added, and item volume grows with every result.

**Why the recommendation.** It shows clients the open-web mentions only search can find, reuses the mapper an approved PRD already has, and never shows a page twice. The terms allow it: Perplexity's customer owns the output, so results "are stored, normalised and shown to clients" (`web-search-perplexity §7 L119`), and Mojeek's results may be stored (CONVENTIONS L95).

**Phase 2 records.** ADR "Web pages as items" (Applies to: F2, search-hit-router, normalize-item, keyword-matcher, the web engines). CONVENTIONS v1.1: L26 and L281 (results become items only through the router, for results it cannot route).

### D2-Q039 · The raw archive: replay, object-storage prefixes and lookups by id

- **Class:** technical
- **Settles:** CF-026, CF-053, AU-010, AU-025, AU-072, AU-073, analysis-media §14 Q3, raw-archiver §14 Q1, raw-archiver §14 Q2, yt-text-purger §14 Q4
- **Blocks:** F2, F8, F4, F6, C2, C4, C5, C6, C7, C13, C14, A1, A2, A3, A4, X7, N6, N8, W5
- **Depends on:** D2-Q012 (who writes `replay` jobs), D2-Q022 (the news cache prefixes), D2-Q035 (the deletion guard)

**Context.** raw-archiver owns a replay topic `raw.replay` that no PRD consumes (`raw-archiver §3 L22`, `§5.3 L71`, `§6.2 L96`). normalize-item replays by reading `raw/` objects on a `replay` job (`normalize-item §5.1 L45`), which skips raw-archiver's deletion and class-clock checks, while raw-archiver proposes the topic as the main path (`raw-archiver §14 Q2 L182`; CF-026, AU-072). The four analysis services re-run from a Parquet archive of normalized items (`analysis-sentiment §5.1 L51`) that raw-archiver does not write: its `archive/` holds `raw.items` envelopes and payloads (`raw-archiver §5.3 L67`; AU-010). Several prefixes have a second writer (CF-053): analysis-media writes `media/<sha256>` directly, without the `.refs` list deletions rely on (`analysis-media §5.2 L52`, `raw-archiver §5.3 L69`; AU-025); x-compliance-sync stores evidence files under `raw/` (`x-compliance-sync §5.2 L56`); web-commoncrawl-scanner writes there directly (AU-029); registry-writer exports `registry_audit` under `archive/registry/` (`registry-writer §12 L140`); two news services write under `cache/news/` (D2-Q022); and batch numbers differ in width (`raw-archiver §14 Q1 L181`). x-compliance-sync expects an archive index by X post and author id that raw-archiver does not keep (`x-compliance-sync §5.1 L43`, `raw-archiver §5.4 L86`; AU-073). What is at stake: replays that bring deleted items back, foreign files compacted as if they were items, and media that outlives its item.

**Options**

1. **One replay path through raw-archiver's reader, no normalized archive, one owner per prefix (recommended).**
   - Replay: no `raw.replay` topic. A replay is a `replay` job on `jobs.normalize-item`, written by the admin API (D2-Q012). normalize-item's worker takes the plan (objects, counts, `run_id`) from raw-archiver's replay API and reads each object through raw-archiver's read endpoint, which drops records of items with an open deletion or a tombstone and records past their class clock; the rate cap and progress stay as written. Replayed items reach keyword-matcher, store-writer and the analysis services on `items.normalized` as new versions; `target = analysis` goes.
   - No Parquet archive of normalized items in v1: analysis re-runs (`kind = rerun`) read ClickHouse `items` and `comments`, and `hits` for the matched keyword, while the text is retained; older content returns through a replay.
   - Prefixes, one writer each. `raw/` (batches, manifests, `raw/_quarantine/`) and `archive/` (Parquet of `raw.items`): raw-archiver only, with six-digit batch numbers fixed in listening-sdk. `media/<sha256>` and `.refs`: only through raw-archiver's media endpoint, analysis-media included. `cache/news/`: news-article-extractor; `cache/news/comments/`: news-comments-fetcher (D2-Q022). `models/<task>/<model_version>/`: the analysis services' release step (D2-Q023). `audit/x-compliance-sync/<yyyy>/<mm>/<dd>/<run_id>.jsonl.zst`: x-compliance-sync's evidence, moved out of `raw/`. `audit/registry-writer/<yyyy>/<mm>/`: registry-writer's export, moved out of `archive/`. web-commoncrawl-scanner writes through `raw.items` (D2-Q037). deletion-propagator reaches `raw/`, `archive/` and `media/` through raw-archiver's rewrite and media endpoints and the caches through the purge registry (D2-Q035); the `audit/` prefixes are kept as long as D2-Q069 decides for audit records.
   - Lookups by X id: no archive index. x-compliance-sync takes post ids from ClickHouse `items` and `comments`, whose rows carry `raw_ref` to the archived copy, and user ids from `sources.platform_id`; individuals keep only `author_ref` (D2-Q010), so their content is checked through the posts job; ids found only in batches parked as `schema_unknown` come from scanning the parked objects that `review_queue` lists (`normalize-item §8 L132`).

   Consequences: one guarded way back into the pipeline; raw-archiver gains a read endpoint and loses the topic; normalize-item reads through raw-archiver rather than the bucket, and its line on a normalized Parquet (`normalize-item §4 L33`) goes, and registry-writer exports to its own prefix (both approved PRDs move under D2-Q001); the analysis services' re-run lines and x-compliance-sync's evidence path change; deletion-propagator's `raw.replay` wording becomes "a replayed record".

2. **`raw.replay` as the one replay path, read by normalize-item and the analysis services, plus a Parquet archive of normalized items written by raw-archiver from `items.normalized` (CF-026 option 1, AU-010 option 1).** Consequences: the replay guards stay as written, but a second archive must be compacted, purged and rewritten on every deletion, and two services gain a topic.
3. **Shared prefixes, every writer registering its objects in the manifests and the purge registry, plus an id index in raw-archiver (CF-053 option 3, AU-073 option 1).** Consequences: fewer moves, but compaction and integrity checks must tell foreign files from items, and the index is one more store deletions must reach.

**Open questions this also answers.** YouTube payloads are archived with their text and rewritten when the 30-day clock removes it, as raw-archiver's purge path does for every class (`yt-text-purger §14 Q4`); the batch number in `raw_ref` is six digits, an SDK constant (`raw-archiver §14 Q1`).

**Why the recommendation.** It keeps one copy of what was fetched and one way back into the pipeline, both guarded by the archive's owner; ClickHouse already holds what re-runs read; and every object in storage has one owner who answers for its lifetime.

**Phase 2 records.** ADR "Raw archive, replay and object storage" (Applies to: F2, raw-archiver, normalize-item, the analysis services, analysis-media, x-compliance-sync, registry-writer, web-commoncrawl-scanner, deletion-propagator). CONVENTIONS v1.1: L31 (the prefix table with owners), L14 to L29 (no `raw.replay`).

## Group 5 · Tables and stores

### D2-Q040 · News tables: who writes `news_sites` and `crawl_policies`, and where the host gate keeps its state

- **Class:** technical
- **Settles:** CF-029, CF-047, CF-048, AU-028, news-comments-fetcher §14 Q3, news-site-resolver §14 Q2
- **Blocks:** F2, F3, F4 (the host gate), C7, C9, N1, N2, N3, N4, N5, N6, N8
- **Depends on:** D2-Q013 (crawl refusals as source-level decisions), D2-Q022 (the host gate's spacing and error rules), D2-Q066 (the pre-allocated `source_id`)

**Context.**

- Crawl permission (CF-029). news-robots-checker expects registry-writer to turn `crawl_allowed = false` into `sources.health = blocked` (`news-robots-checker §5.2 L61`, `§6.2 L117`), but registry-writer reads only `registry.decisions` (`registry-writer §6.1 L86`). The fetchers check the policy themselves before fetching (`news-feed-poller §5.1 L40`, `news-sitemap-poller §5.1 L41`, `news-homepage-differ §5.1 L41`, `news-article-extractor §5.2 L52`).
- `news_sites` (CF-047). news-site-resolver writes it, "one row per host" with `status: candidate` (`news-site-resolver §6.3 L116`, `§5.2 L54`), yet expects registry-writer to write the accepted profile "keyed by `source_id`" (`news-site-resolver §6.2 L112`; also `news-feed-poller §5.1 L48`). registry-writer has no such path, a candidate has no `source_id`, and the resolver asks whether to fold the table into `sources.notes` (`news-site-resolver §14 Q2 L172`).
- `crawl_policies` (CF-048). The row (`news-robots-checker §6.3 L121`) lacks the message's `reason`, `changed_fields` and `requested_by` (`§6.2 L96-L115`). Five services keep the gate's slot in that row (`news-feed-poller §5.3 L66`), which the robots-checker upserts whole and needs before the row exists (`news-robots-checker §5.2 L54`, `L61`); README decision 6 puts the gate, not its state, in listening-sdk (`README L183`).
- Disqus fields (AU-028). news-comments-fetcher needs an identifier template (`news-comments-fetcher §5.1 L49`, `§5.2 L55`) that the resolver parses (`news-site-resolver §5.2 L47`) but does not emit (`§6.2 L102`), and marks "the site's comments `degraded`" (`news-comments-fetcher §8 L139`) with no column to hold it.

At stake: whether an accepted site is ever polled, and whether a policy refresh can erase a slot just taken.

**Options**

1. **One writer per table, crawl refusals sent as registry decisions, the gate in its own table (recommended).**
   - `news_sites`, written only by news-site-resolver: primary key `source_id`, `host` unique. The resolver allocates the `source_id` with the candidate row and sends it as `proposed_source_id` in `proposed_source`; the qualifier's `add` passes it on and registry-writer inserts under it (D2-Q066's rule for owned properties), never writing `news_sites`. Columns: the `site_profile` fields (`news-site-resolver §6.2 L96-L105`), `status` (`candidate`, then `registered` once the `sources` row exists), `resolved_at`, `profile_version`, and the Disqus fields `comments_provider` (the PRDs' spelling), `disqus_shortname`, `disqus_identifier_template` (new) and `comments_health` (`ok` or `degraded`, new). It stays a control-plane table (answers `§14 Q2 L172`). On refresh, identity changes go to registry-writer as `update` decisions (D2-Q013); readers read `news_sites` at each job, so profile changes need no event.
   - Disqus health: a rejected shortname makes news-comments-fetcher stop and send its `refresh` with that reason, a new refresh trigger (`news-site-resolver §5.1 L40`); the resolver re-reads the embed and records a new shortname, `comments_provider = none` if the embed is gone, or `comments_health = degraded`. comment-decay-scheduler opens no Disqus series unless `comments_health = ok`. A per-article `disqus_identifier` from the extractor stays an optional field, N6's choice (`news-comments-fetcher §14 Q3 L186`).
   - `crawl_policies`, written only by news-robots-checker, primary key `host`. Row and `crawl.policies` share one column list (D2-Q070 b)'s flat names): `host`, `status`, `crawl_allowed`, `reason`, `access_mode`, `crawl_delay_seconds`, `robots_status`, `robots_rules` (group, rules, sitemaps, hash), `usage_signals`, `rsl`, `payment`, `checked_at`, `expires_at`, `policy_version`. The message adds the change fields `changed_fields`, `requested_by`, `kind`; the row adds `next_refresh_at`. No slot column.
   - Crawl permission reaches `sources.health` as D2-Q013 has it: when `crawl_allowed` flips for a registered site, or at the `added` event of a site added while disallowed, news-robots-checker sends a source-level `health_change` decision (reason `crawl_disallowed`, back to `ok` once allowed); registry-writer reads no `crawl.policies` (`news-robots-checker §5.2 L61`, `§6.2 L117` reworded). Fetchers still read the policy row before every request, for path rules and the access mode.
   - `host_gate` (`host`, `next_slot_at`, `holder`, `spacing_seconds`), written only by the listening-sdk gate, one conditional update per slot; created on first use, so a first robots check can take a slot.

   Consequences: three tables with one writer each; F4 builds the gate on its own table; the five gate users' state lines and the registry sentences of `news-site-resolver §6.2 L112`, `news-feed-poller §5.1 L48` and news-robots-checker are reworded; the approved news-site-resolver and qualifier (which passes `proposed_source_id` on) move under D2-Q001.

2. **registry-writer as the news path (CF-029 (1), CF-047 (2), CF-048 (1)).** registry-writer consumes `crawl.policies`, maps `crawl_allowed` onto `health` and writes `news_sites` from the decision's profile, keyed by `source_id`, candidates in a resolver table; the slot stays in `crawl_policies.next_slot_at`, which the robots-checker's upsert leaves alone. Consequences: no new decisions, but registry-writer reads a second topic and learns a news schema, a candidate needs a second table, and two writers still share each policy row.
3. **Crawl permission only in `crawl_policies`, the profile as jsonb on `sources`, gate state outside the control plane (CF-029 (3), CF-047 (3), CF-048 (3)).** Consequences: no health decisions and one table fewer, but `health` stays `ok` on a blocked site, every profile refresh becomes a registry decision, and a gate outside Postgres needs a service or shared cache the stack lacks.

**Why the recommendation.** Each table gets one owner, the row several services wrote is split, and a blocked site shows in `health` through the one registry path; the pre-allocated `source_id` lets one row follow a site from candidate to registered.

**Phase 2 records.** ADR "News site, crawl-policy and host-gate tables" (Applies to: F2, F3, every news service, qualifier, registry-writer, comment-decay-scheduler, listening-sdk). CONVENTIONS v1.1: L30 gains `news_sites` and `host_gate`, and the column list of `crawl_policies`, each with its writer; the news fact sheet names the gate's table.

### D2-Q041 · The `cursors` table: its key, its columns, and who may write a row

- **Class:** technical
- **Settles:** CF-034, CF-035, CF-036, tg-discussion-receiver §14 Q3, x-user-timeline-poller §14 Q1
- **Blocks:** F3, F4, F5, F6, C2, C4, C5, C6, C10, C14, C15, A1, A2, A3, A4, FB2, FB3, FB6, VFB3, IG1, IG2, IG4, IG5, VIG1, LI1, X3, X4, X5, W1, W2, W4, YT7, YT9, TG2
- **Depends on:** D2-Q015 (per-service due times), D2-Q020 (the backfill hand-over), D2-Q045 (`service_runs`), D2-Q049 (push coverage)

**Context.** CONVENTIONS keeps one row per source × service, with an opaque `cursor` and three health columns (`CONVENTIONS L30`, `L38`). The PRDs need more:

- Rows with no source, for replays, reruns, recomputes and sweeps (`normalize-item §6.3 L124`, `aggregator §6.3 L97`, `retention-purger §6.3 L114` per class, and eight more in CF-034 b).
- A second dimension: hashtag edge (`ig-hashtag-search §6.3 L127`, against its `§6.1 L87`), X rule (`x-filtered-stream §6.3 L149`), keyword with no source (`fb-page-search §5.1 L42`), a suffixed service name (`li-client-posts-poller §5.1 L48`).
- Typed state: due times (`ig-account-resolver §5.1 L46`; `fb-page-search §5.1 L42`, stored differently at `§5.2 L55`), subscription state (`ig-webhook-receiver §6.3 L129`), job progress (`x-full-archive-search §6.3 L132`), a hashed id set (`yt-web-search-bridge §6.3 L130`), another source's registry data (`tg-discussion-receiver §6.3 L142`).
- Other services' rows: fb-backfill writes fb-page-feed-poller's cursor (`fb-backfill §5.2 L56`, `fb-page-feed-poller §5.1 L48`), x-full-archive-search raises x-user-timeline-poller's (`x-full-archive-search §5.2 L56`), and x-user-timeline-poller reads x-filtered-stream's rows as its coverage list (`x-user-timeline-poller §5.1 L42`, asked at `§14 Q1 L191`).

At stake: F3 needs one key and one column list; today a cursor format change silently breaks the backfill that writes into the poller's row.

**Options**

1. **A widened key, typed due columns, a private `state`, own rows only (recommended).**
   - Key: unique on (`service`, `source_id`, `scope_key`), nulls not distinct. `source_id` is null for service-level rows; `scope_key` is empty for the plain per-source row, else a hashtag edge, an X rule id, a retention class, `reconcile`, a post (`post:<item_id>`, D2-Q046) or a run (`replay:<version>`, `recompute:<job_id>`, `rerun:<model_version>`, `rematch:<job_id>`). fb-page-search's per-keyword rows become plain rows of its keyword-rule sources (D2-Q044).
   - Columns: `cursor` (the opaque read position); `next_due_at` and `last_started_at`, typed and indexed (D2-Q015's rotation state; they replace `refresh_due_at` and `next_search_at`); `last_success_at`, `last_error`, `consecutive_errors`; `state` (jsonb, private to the owning service: subscription state, job progress, id sets); `updated_at`.
   - `service` is the name in the index (`CONVENTIONS L226` to `L236`), never suffixed: `li-client-posts-poller:reconcile` becomes `scope_key = reconcile`.
   - A service writes only its own rows, through the SDK helper, after the producer acknowledges (`CONVENTIONS L71`); another service's rows are never an interface.
   - The cross-service uses go. Backfill services stop writing the pollers' rows: a poller whose row is empty reads one page, newest first, as `x-full-archive-search §5.1 L41` already describes, and normalize-item drops the overlap (the hand-over is D2-Q020's). x-user-timeline-poller takes coverage from `sources.push_covered` (D2-Q049), set by registry-writer from x-filtered-stream's `push_coverage` decisions (D2-Q013), and the stream's state from x-filtered-stream's typed `service_runs` status (D2-Q045); this answers `x-user-timeline-poller §14 Q1 L191`. tg-discussion-receiver's link to its channel moves to the group's registry row (`platform_meta`, D2-Q065).

   Consequences: one migration and one helper; schedulers index `next_due_at`; about twenty PRDs reword their state lines, among them the approved fb-backfill, fb-page-feed-poller, fb-page-search and ig-hashtag-search, which move under D2-Q001.

2. **`cursors` kept source × service, with a separate progress table for service-level and non-source rows, and the two backfill seedings allowed as named cross-writes (CF-034 (2), CF-036 (1)).** Consequences: fewer PRDs change, but one helper serves two tables, due times stay untyped, and a poller's format change still breaks the backfill that writes its row.
3. **Key unchanged; extra dimensions and state encoded in `service` and the `cursor` string (CF-034 (3), CF-035 (3)).** Consequences: no schema change, but schedulers cannot index due times, every service parses strings, and ig-hashtag-search's two edges overwrite one row.

**Why the recommendation.** Every row the PRDs need fits one key, schedulers get the indexed due time D2-Q015 relies on, and a cursor format change can only break the service that owns the row.

**Phase 2 records.** ADR "The cursors table" (Applies to: F3, every service that keeps a cursor, backfill-orchestrator, listening-sdk). CONVENTIONS v1.1: L30 (`cursors` as service × scope) and L38 (the column list, the scope-key forms, the one-owner rule).

### D2-Q042 · Budgets: one writer for the counters, a home for caps, the two ledgers and the tag list

- **Class:** technical
- **Settles:** CF-037, CF-038, CF-099, AU-065, AU-068, tt-keyword-search §14 Q3, yt-channel-resolver §14 Q4
- **Blocks:** F3, F5, C1, C9, A1, A2, A3, A4, FB2, VFB2, IG1, IG2, IG3, IG5, IG6, VIG1, VIG2, VTT1, VTT2, VTT4, VTT5, LI1, VLI1, VLI2, VLI3, VLI4, X1, X2, X3, X4, X5, X6, X7, W1, W5, YT2, YT4, YT7, YT8, YT9, TG1, TG2
- **Depends on:** D2-Q010 (the keyed reference for X user reads), D2-Q018 (priorities and modes), D2-Q023 (`analysis_model_api`), D2-Q057 (what a job does with each answer)

**Context.**

- Writers (CF-037). The governor keeps the counters (`CONVENTIONS L85`), reserving with one conditional update (`quota-governor §5.2 L58`), yet ten PRDs write usage into `budgets` (Meta's headers, `fb-page-feed-poller §5.2 L60`), and nine keep caps, splits and ceilings there that the row (`quota-governor §6.2 L104`) has no column for (per-job caps, `x-full-archive-search §7 L138`; the LinkedIn split, `li-post-search §7 L113`).
- Sub-counters (AU-065). Rule 5 caps vendor spend per source (`CONVENTIONS L246`) and Instagram counts per service (`ig-keyword-search §6.3 L121`); the governor has per-service sub-counters on `tt_vendor` only (`quota-governor §5.3 L82`) and no page cap in its answer (`tt-hashtag-feed-poller §5.1 L50`).
- Ledgers (CF-038). X reads are recorded as bare ids (`quota-governor §6.2 L100`), `x:post:<id>` (`x-replies-fetcher §5.2 L57`) or `user:<id>` and a keyed hash (`x-user-resolver §5.2 L57`), so one post can be paid twice; the hashtag ledger is a table (`quota-governor §6.3 L107`, `README L186`) or rows in `budgets` (`ig-hashtag-search §5.1 L57`).
- Names (CF-099, AU-068). Tags outside the list (`ig_graph_<client_id>`, `ig-hashtag-search §5.2 L65`; `analysis_model_api`, `README L184`), wildcards (`quota-governor §5.3 L82`, `L83`), two placeholder separators (`CONVENTIONS L279`), external calls that ask for nothing (`web-commoncrawl-scanner §7 L111`, `yt-pubsub-receiver §7 L138` and four more), a YouTube `list` bucket (`yt-web-search-bridge §7 L137`), and `budget_80pct` for the governor's `budget_80` (`tt-keyword-search §10 L131`).

At stake: an unknown tag is denied as `flag_off` (`quota-governor §5.3 L67`), and a second writer on a counter double counts or races the reservation.

**Options**

1. **quota-governor the only writer of counters, configuration in its own table, ledgers as tables, one tag list (recommended).**
   - `budgets`, written only by the governor: one row per (`budget_tag`, `sub_counter`, period), with `quota-governor §6.2 L104`'s columns and `reset_rule`, plus `provider_usage` (jsonb: Meta and LinkedIn usage headers, credits left). Services send usage in the SDK `report` (`§5.1 L37`) instead of writing "into `budgets`".
   - Sub-counters `service:<service>` and `source:<source_id>` on every amber tag, and `service:<service>` wherever a share is set (D2-Q037's bridge share), each with its own limit; the request carries the job's `source_id`.
   - `budget_config` (new; `budget_tag`, `scope`, `setting`, value): limits and shares (the LinkedIn split, the bridge's share, per-source caps), per-job and per-run caps (the page cap included, read through the SDK), rate ceilings, YouTube backfill and refresh allowances. Written by ops through the admin console (D3 specifies the writer; audited); values tuned in the pilot. Intervals belong to D2-Q049's cadence table (`li-company-posts-poller §5.1 L43`).
   - `x_read_ledger` (`utc_day`, `resource_type` `post` or `user`, `resource_id`), written only by the governor: posts as bare ids, users as the SDK's keyed reference (D2-Q010), so no individual's clear id is stored yet every read of one user matches; kept until the day is reconciled (`quota-governor §8 L127`). `ig_hashtag_ledger` (`ig_user_id`, `hashtag_id`, `first_queried_at`); a 31st hashtag waits for the window (`§5.3 L81`; amber handling is D2-Q052).
   - Tags: `CONVENTIONS L279` stays canonical, with an id placeholder always after `:` (`ig_graph:<ig_user_id>`, `ig_hashtag:<ig_user_id>`, as three of L279's five id placeholders already have it; Instagram keeps `ig_user_id`), ig-hashtag-search aligned; the listed tags instead of wildcards; `analysis_model_api`, seeded only if a hosted model is chosen; zero-price counting tags, never a gate (`commoncrawl`, `tg_bot_api`, `yt_pubsub_hub`, and sub-counter `compliance` on `x_pay_per_use`, priced only if the pilot shows X meters it); LinkedIn confirmation calls on `linkedin_cm:<client_id>` (`li-org-resolver §5.2 L52`); alerts as the governor names them (`budget_80`).
   - YouTube's four buckets name the call, not the reason: `list` folds into `ingest`, resolver calls use `ingest` (answers `yt-channel-resolver §14 Q4 L199`), backfill and the text refresh draw on their call's bucket within a `budget_config` allowance.
   - `tt_vendor` stays one tag with one sub-counter and monthly share per amber service (`tt-profile-videos-poller §7 L137`), so a comment surge spends only its own share (answers `tt-keyword-search §14 Q3 L160`; six services, `CONVENTIONS L228`).

   Consequences: F3 seeds concrete rows; C1 is the only writer; six approved PRDs (ig-hashtag-search, yt-web-search-bridge, li-org-resolver, fb-page-feed-poller, tt-keyword-search, tt-hashtag-feed-poller) move under D2-Q001.

2. **Services write usage to an observations table the governor folds in; configuration as columns or one `config jsonb` on the tag row; one generic ledger or ledger rows in `budgets` (CF-037 (2), CF-038 (2) or (3)).** Consequences: services keep a direct write, the reservation must also merge observations, and one table mixes counters, settings and ledgers.
3. **Tag-level counters only, wildcard families allowed (AU-065 (3), CF-099 (3)).** Consequences: the simplest governor, but rule 5's per-source cap has nothing to count against, a comment surge can starve TikTok discovery, and F3 cannot seed a wildcard.

**Why the recommendation.** The one-update reservation needs one writer per counter, caps get a typed home, and one ledger key makes X charge a resource once a day whoever reads it.

**Phase 2 records.** ADR "Budgets, ledgers and budget tags" (Applies to: F3, quota-governor, listening-sdk, the admin console, every service with a `budget_tag`). CONVENTIONS v1.1: L30 (`budget_config` and the two ledgers), L85 (usage reported, never written by services), L279 (the separator rule, the added and zero-price tags, the bucket rule, the sub-counters). `DEFERRED.md`: every cap, share and allowance value (C1, after the pilot).

### D2-Q043 · The `clients` table, and where a client's lists live

- **Class:** technical
- **Settles:** CF-039, CF-056, li-client-posts-poller §14 Q4, registry-writer §14 Q3, x-user-resolver §14 Q1
- **Blocks:** F3, C1, C5, C7, C8, C9, C12, C13, C14, A5, FB1, FB2, FB5, FB6, VFB1, VFB2, VFB3, IG1, IG3, IG4, IG5, VIG1, VIG2, TT1, VTT1, VTT4, VTG3, LI1, VLI1, X2, X3, X4, X5, N2, W1, W2, YT7, YT9
- **Depends on:** D2-Q016 (`credentials`), D2-Q050 (the X gate), D2-Q052 (amber acceptance), D2-Q066 (the manual path for client-added candidates)

**Context.**

- `clients` has no columns and no writer (`CONVENTIONS L30`), and the PRDs read it under many names (CF-039): government status as `client_type = government` (`keyword-matcher §5.3 L69`, failing closed when missing at `alert-evaluator §8 L118`), a "government flag" (seven PRDs, e.g. `registry-writer §6.1 L88`) or a "government marker" (four, e.g. `li-post-search §6.1 L79`); amber acceptance as its own value (`ig-comments-fetcher §6.1 L89`) or as "not government" (`tg-channel-posts-poller §5.1 L42`); the X entitlement under two names (`keyword-matcher §5.3 L69`, `x-user-timeline-poller §14 Q5 L195`); token references (`fb-page-feed-poller §6.1 L104` and six more); per-service options (`qualifier_config`, `qualifier §3 L25`; a Perplexity opt-out, `web-search-perplexity §6.1 L86`; engine flags, `yt-web-search-bridge §6.3 L131`; a `yt_text_refresh` entitlement, `yt-text-purger §5.3 L81`).
- A client's lists sit in three places (CF-056): on `clients` (`qualifier §6.1 L77`, `poster-resolver §6.1 L83`), in `client_sources.priority` (`registry-writer §5.3 L77`, `li-client-posts-poller §6.1 L101`) and on `keywords` (`web-search-mojeek §5.1 L45`). They do different jobs. A priority list makes a source tier 1 (`CONVENTIONS L45`) and exempts it from decay (`qualifier §12 L134`). Seed lists and watchlists act on candidates that are not yet sources: as an Iraqi signal (`CONVENTIONS L243`), as a reason an X account qualifies (`CONVENTIONS L242`, `x-user-resolver §5.2 L57`), and as a way through a remembered rejection (`poster-resolver §5.2 L54`).

At stake: every amber, X and government rule reads `clients`; one concept under four names means one filter per service, and a list edited in one place changes nothing for the services that read another.

**Options**

1. **A typed `clients` core with settings and tokens beside it, priority on `client_sources`, seed and watch lists by candidate key (recommended).**
   - `clients`: `client_id` (uuid, D2-Q006), `name`, `status` (`active`, `offboarding` and the rest of D3's list), `client_type` (`commercial` or `government`, the one government marker; a missing value fails closed), `accepts_amber` (D2-Q052, never derived from `client_type`; also what the "contract terms" of `tt-profile-videos-poller §6.1 L101` stand for), `x_end_user_declared` (D2-Q050), `accepted_flagged_vendors` (the flagged vendors the client accepts, `CONVENTIONS L6`: Perplexity today, replacing the opt-out and the engine flags), `created_at`, `updated_at`. No `yt_text_refresh` entitlement, since D2-Q056 makes the refresh part of the service.
   - Tokens, calling accounts and webhook secrets live in `credentials` (D2-Q016). `client_settings` (`client_id`, `service`, `settings` jsonb) holds per-service options; `qualifier_config` becomes the qualifier's row (an approved PRD moves under D2-Q001). Portal users and roles are D3's.
   - Priority: `client_sources.priority`, written by registry-writer from the portal's `add` or `update` decision. A source any client priority-lists is tier 1 whatever its followers and is exempt from decay while listed (`CONVENTIONS L45`, `qualifier §12 L134`); li-client-posts-poller's 30-minute list is this flag (answers `li-client-posts-poller §14 Q4 L190`); its cadence comes from an `owned_by_client` row of D2-Q049's cadence table, as these pages are not `push_covered`. Keyword priority is `keywords.priority` (D2-Q044).
   - Seed lists and watchlists: `client_lists` (`client_id`, `list` `seed` or `watch`, `candidate_key` in D2-Q032's forms, `added_at`, `added_by`), indexed by `candidate_key` and read by poster-resolver, the qualifier, x-user-resolver and news-site-resolver; a new entry also goes down the manual path (D2-Q066).
   - The client portal and admin console write `clients`, `client_settings` and `client_lists` (D3 specifies the writer); services only read them.

   Consequences: F3 creates three tables; about thirty PRDs replace the four names and "token reference" with these columns; the approved qualifier and poster-resolver read their lists from `client_lists`.

2. **A small core plus one `settings jsonb` on `clients`, every list an array on `clients` (CF-039 (2), CF-056 (2)).** Consequences: one table, but each list lookup scans arrays across all clients, token state stays outside `credentials`, and registry-writer's manual add loses its `priority` field.
3. **Lists entered on `clients` and copied by registry-writer into `client_sources.priority` and `sources.tier` (CF-056 (3)).** Consequences: the client edits one place, but two copies must be kept in step, and a seed or watch entry for an account that is not yet a source has no row to copy into.

**Why the recommendation.** Each concept gets one name and one home that fits what it acts on: a policy on the client, a priority on the source, a seed or watch entry on the candidate.

**Phase 2 records.** ADR "Clients and client lists" (Applies to: F3, every service that reads `clients`, registry-writer, poster-resolver, qualifier, the client portal and admin console). CONVENTIONS v1.1: L30 (`clients` with its columns, `client_settings`, `client_lists`), L45, L242 and L243 (where the priority, watch and seed lists live).

### D2-Q044 · The `keywords` table, and the keyword-rule sources the searchers rotate

- **Class:** technical
- **Settles:** CF-040, AU-062, fb-keyword-search §14 Q3, web-search-perplexity §14 Q4
- **Blocks:** F2, F3, C5, C6, C7, C9, FB6, VFB1, IG2, VIG1, VTT1, VLI1, VTG1, X1, X4, X5, YT8, YT9, W1, W2, W4
- **Depends on:** D2-Q004 (jobs keyed by the keyword-rule source), D2-Q013 (registry decisions), D2-Q015 (several services rotating one row), D2-Q049 (tier and lifecycle), D2-Q052 (amber acceptance), D2-Q069 (the X term screen)

**Context.**

- Columns (CF-040). CONVENTIONS names `keywords` without columns (`CONVENTIONS L30`) and expects keyword-rule rows in `sources` (`L36`, `L281`). keyword-matcher proposes the only column list, one client per row (`keyword-matcher §5.3 L56`); the searchers read "variants", "terms", per-script forms, context terms, a priority flag and a `client_ids` list (`fb-page-search §6.1 L89`, `yt-keyword-search §6.1 L92`, `web-search-perplexity §5.1 L44`). No PRD writes `keywords` (`qualifier §3 L32`).
- Creation (AU-062). The web engines expect registry-writer to create a row per keyword (`web-search-perplexity §5.1 L41`, `web-search-mojeek §5.1 L42`), but its decision types and columns never mention keyword rules (`registry-writer §3 L22`, `§3 L27`) and it reads no `keywords` (`§6.1 L88`); fb-page-search keys its jobs by `keyword_id` and expects registry-writer to emit a `seed` job (`fb-page-search §5.1 L40`).
- Sharing. Searchers select rows by platform and type, so several services read one row: the three web engines (`web-gdelt-poller §5.1 L41`), yt-keyword-search for tier 1 and yt-web-search-bridge for tiers 2 and 3 (`yt-keyword-search §3 L23`, `yt-web-search-bridge §3 L21`), x-recent-search and x-full-archive-search (`x-recent-search §5.1 L39`, `x-full-archive-search §5.1 L39`). Identical queries of several clients are one row (`ig-keyword-search §5.1 L41`); fb-keyword-search reads only `route = amber` rows (`fb-keyword-search §5.1 L40`).

At stake: the twelve search services have nothing to rotate, and keyword-matcher and the searchers read different columns for one keyword.

**Options**

1. **Per-client keywords; shared keyword-rule rows per platform, route and query, kept by registry-writer from the portal's saves (recommended).**
   - `keywords`, written by the client portal (D3 specifies the writer): keyword-matcher's list (`keyword_id`, `client_id`, `label`, `forms`, `exclusions`, `purpose`, `enabled`, `version`, `updated_at`, `rematch_days`) plus `context_terms` (they narrow a search and are never matched alone), `priority`, `platforms` (in scope), `query_key` (an SDK hash of the normalised forms and context terms, set on save) and `screening_status` (the X sensitive-event screening result, set on save, D2-Q069). "Variants", "terms" and per-script forms are `forms` entries.
   - `screened_terms` (new, D2-Q069): the X blocked and sensitive-event terms that a save is screened against and that x-filtered-stream and x-recent-search read; owned by the admin console (D3 specifies the writer).
   - Keyword-rule rows: one `sources` row per (`platform`, `route`, `query_key`), with `platform_id = <route>:<query_key>` so registry-writer's identity holds (`registry-writer §2 L15`), `client_ids` = every client with an enabled keyword of that query (one paid search for all), and `tier` 1 if any of them has `priority`, else 2 (D2-Q049). Every searcher of that platform and route reads the row and keeps its own cursor and due time (D2-Q015, D2-Q041). Facebook gets a green row (fb-page-search) and an amber row (fb-keyword-search); amber rows carry only clients that accept amber, never government clients (D2-Q052, `registry-writer §5.2 L61`). Hashtag forms make `hashtag` rows the same way. A keyword whose `screening_status` flags it joins no X row (D2-Q069).
   - Searchers take the forms from the row's keywords and `client_ids` from the row; exclusions stay per client, applied by keyword-matcher, never in a shared query.
   - Each save sends registry-writer an `add` or `update` decision naming the keyword (D2-Q013); registry-writer reads `keywords`, upserts the rows for each platform in scope, adds or removes the client, retires a row with no keyword left (D2-Q049) and emits `source.events`.
   - fb-page-search's own scheduler makes a green Facebook rule row due at once on its `added` or `updated` event, the old `seed`, and runs it as a `rotation` (D2-Q011, D2-Q012); its jobs carry the row's `source_id` (D2-Q004), not `keyword_id`.

   Consequences: F3 creates `keywords` and `screened_terms`; F2 adds the `query_key` helper with golden vectors; the approved registry-writer (a decision path and a read of `keywords`) and fb-page-search (jobs keyed by source) move under D2-Q001.

2. **One keyword-rule row per keyword and search service.** Consequences: each row has one reader, but rows shared today stop being shared, registry-writer's identity needs the service inside `platform_id`, and the approved web engines, YouTube searchers and x-recent-search change their selection.
3. **The searchers rotate `keywords` rows directly, keyed by `keyword_id` (CF-040 (3)).** Consequences: no keyword-rule rows, against `CONVENTIONS L36` and `L281`; identical queries of two clients are searched and paid twice; search finds have no registered `source_id`.

**Why the recommendation.** It is what most searchers already assume, it pays once for a query several clients share, and it keeps the government and amber rules on the rows the amber services select.

**Phase 2 records.** ADR "Keywords and keyword-rule sources" (Applies to: F2, F3, registry-writer, keyword-matcher, every search service, x-filtered-stream, the client portal and admin console). CONVENTIONS v1.1: L30 (`keywords` columns, `screened_terms`), L36 (the keyword-rule identity and `client_ids`), L281 (searchers read the rule row). F2: the `query_key` helper.

### D2-Q045 · The other shared tables: run status, retention classes, the review queue, decisions, resolver caches and audit trails

- **Class:** technical
- **Settles:** CF-041, CF-042, CF-043, CF-044, CF-046, CF-054, AU-024, fb-page-resolver §14 Q5, ig-account-resolver §14 Q3, poster-resolver §14 Q1, registry-writer §14 Q1
- **Blocks:** F3, F8, F4, F6, C2, C4, C6, C7, C8, C9, C11, C12, C13, C14, C15, A1, A2, A3, A4, A5, FB1, FB6, IG1, IG3, TT1, VTT3, VTG1, VTG2, LI3, VLI1, VLI2, X1, X2, X3, X4, X7, N2, N7, N8, W1, W2, W3, W4, W5, YT1, YT5, YT6, YT7, YT8, YT9
- **Depends on:** D2-Q010 (individuals' keys), D2-Q017 (`jobs.completed`), D2-Q025 (the naming rule and the purge registry), D2-Q032 (poster-resolver's cache), D2-Q054 to D2-Q056 (the class clocks)

**Context.** Six control-plane names cover several shapes each:

- `service_runs` (CF-041) is "last run, lag, errors per service" (`CONVENTIONS L30`) but also holds per-job results (`news-comments-fetcher §5.2 L59`), per-page state (`li-notification-receiver §6.3 L137`), connection state and checkpoints (`x-filtered-stream §6.3 L149`, `web-commoncrawl-scanner §6.3 L107`), and is read by other services (`x-user-timeline-poller §6.1 L108`, `alert-evaluator §5.1 L40`).
- `retention_classes` (CF-042) has TTL columns for store-writer (`store-writer §5.3 L71`), a clock table for retention-purger (`retention-purger §5.2 L49`), and no writer.
- `review_queue` (CF-043) has columns only for the qualifier's cards (`qualifier §6.3 L90`), whose 24-hour default reject (`§5.2 L61`) would hit the parked batches, annotation tasks and holds of seventeen other PRDs (e.g. `normalize-item §5.2 L50`, `analysis-entities §5.3 L71`).
- `decisions` (CF-044) is the qualifier's log (`qualifier §5.2 L63`) and also fb-page-search's emitted-id set (`fb-page-search §6.3 L123`), poster-resolver's hit counter (`poster-resolver §5.2 L54`) and news-dedup's ops log (`news-dedup §8 L123`).
- Resolver caches (CF-046): four `profile_cache` tables with four keys (e.g. `ig-account-resolver §6.3 L131`, `x-user-resolver §6.3 L136`) and `tt_user_cache` (`tt-user-resolver §6.3 L115`) sit behind `poster_profiles`, which answers every candidate resolved within 30 days (`poster-resolver §5.2 L53`).
- Audit (CF-054, AU-024): `registry_audit` is append-only (`registry-writer §9 L123`) yet updated as the outbox (`§5.2 L59`); the canary's trail has no table (`source-health-canary §6.3 L108`); `retention_audit` has two writers with different columns (`retention-purger §6.2 L110`, `yt-text-purger §6.2 L159`).

At stake: F3 must create each table once, with one key and one owner for every row.

**Options**

1. **One pattern: typed shared columns, `kind` and `payload` where uses vary, private state with its owner (recommended).**

   | Table               | Shape                                                                                                                                                                                                                                                                                                                                   | Writers and readers                                                                                                                                                                                                                                                                                                      |
   | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
   | `service_runs`      | key (`service`, `instance`); typed `status` (`ok`, `degraded`, `down`), `last_run_at`, `last_success_at`, `lag_seconds`, `error_count`, `last_error`; private `state` jsonb                                                                                                                                                             | each service for itself, through the SDK; two named reads of typed columns, the only cross-service reads (alert-evaluator: aggregator's `last_success_at`; x-user-timeline-poller: x-filtered-stream's `status`, D2-Q041); per-job results to `jobs.completed` (D2-Q017), per-page and per-post state to `cursors`       |
   | `retention_classes` | key (`class`, `part`, `vendor`): `part` is `text`, `row`, `raw`, `derived` or `cache`; `vendor` empty, or a vendor override; `anchor`, `clock`, `mode`, `executor`; `content_ttl` and `row_ttl` derived from the `text` and `row` clocks                                                                                                | seeded by F3 with D2-Q054 to D2-Q056's clocks, changed only by reviewed migration (`retention-purger §12 L150`); read by normalize-item, store-writer, aggregator, raw-archiver and the purgers                                                                                                                          |
   | `review_queue`      | `review_id`, `kind`, `service`, `subject_key`, `status`, `opened_at`, `deadline_at`, `reviewer`, `answer`, `payload` jsonb, `closed_at`                                                                                                                                                                                                 | each service owns and closes its kinds; a deadline only where a kind sets one (the 24-hour reject: the qualifier's cards); answers through n8n or the admin console (D3); ig-account-resolver opens none (`§5.2 L62`); rows with item ids join the purge registry                                                        |
   | `decisions`         | the qualifier's columns and outbox `published_at` (`qualifier §5.2 L63`)                                                                                                                                                                                                                                                                | the qualifier only; five services read rejections by `candidate_key`. fb-page-search's set moves to `fb_page_search_emitted`, the hit count to `poster_profiles.hits_30d`, news-dedup's splits to the admin API's audit (D2-Q012); before and after values stay in `registry_audit` (answers `registry-writer §14 L158`) |
   | `poster_profiles`   | `poster-resolver §6.3 L96` plus `platform`; a row per key form a resolver reports (id, handle)                                                                                                                                                                                                                                          | the one resolver cache, kept by poster-resolver from `poster.profiles` (D2-Q032); the four `profile_cache` tables and `tt_user_cache` go; individuals' rows hold only what D2-Q010 allows                                                                                                                                |
   | audit               | `registry_audit` append-only, plus a separate `registry_outbox` written in the same transaction and marked by the relay; `canary_audit`, append-only; one `retention_audit` shape: retention-purger's columns plus `executor`, `parent_run_id`, `trigger`, `refreshed`, `text_deleted`, `derived_deleted`, `failures`, `refresh_missed` | each executor writes its own `retention_audit` rows; retention-purger takes yt-text-purger's row with its `parent_run_id` as confirmation; `x_compliance_audit` stays x-compliance-sync's, deletion-propagator's record D2-Q035's; no platform-wide `audit_log`                                                          |

   Consequences: F3 creates these shapes and drops five resolver caches; registry-writer's outbox no longer breaks its own grant; the approved registry-writer, poster-resolver and fb-page-search move under D2-Q001.

2. **A table per use, each defined by its PRD (CF-041 (3), CF-042 (3), CF-043 (2), CF-046 (2), CF-054 (2)).** Consequences: no shared shape, but a dozen more tables, retention clocks in two tables, resolver caches that can disagree with `poster_profiles` for 30 days, and `registry_audit` no longer append-only.
3. **Generic logs (CF-041 (2), CF-044 (2), CF-054 (3)).** `service_runs` as an append-only run log, `decisions` as a generic log with `kind` and `scope_key`, one platform-wide `audit_log`. Consequences: fewest tables, but every reader filters on `kind`, a 7-day prune shares a table with the 180-day memory, and all services' audit rows share one retention.

**Why the recommendation.** Each name keeps its CONVENTIONS meaning, variety goes into `kind` and `payload`, and every row has one writer.

**Phase 2 records.** ADR "Shared control-plane tables" (Applies to: F3, F8, every service writing `service_runs` or `review_queue`, qualifier, poster-resolver and the resolvers, registry-writer, source-health-canary, retention-purger, yt-text-purger). CONVENTIONS v1.1: L30 (each table with its key and writer; `poster_profiles`, `registry_outbox`, `canary_audit` and `retention_audit` added), L73 to L81 (the classes as rows of `retention_classes`).

### D2-Q046 · Comment state for change detection, and the keys of `comment_series`

- **Class:** technical
- **Settles:** CF-045, AU-020, RN-16, tt-video-comments-fetcher §14 Q2
- **Blocks:** F2, F3, F8, C6, C11, FB5, VFB3, IG6, VIG2, VTT5, YT5, YT6, X6, LI2, VLI4, N8
- **Depends on:** D2-Q009 (one content hash; edits), D2-Q041 (per-post `cursors` rows), D2-Q060 (the replies job), D2-Q062 (deletion on absence)

**Context.**

- One job, five designs (CF-045). Telling new, edited and deleted comments from stored ones (`CONVENTIONS L62`, `L63`) runs on `comment_ledger`, owned by fb-post-comments-fetcher and "shared" by fb-group-comments-fetcher with other columns and another edit rule (`fb-post-comments-fetcher §6.3 L129`, `§5.2 L68`; `fb-group-comments-fetcher §6.3 L132`, `§5.2 L65`); on `tt_comment_state` (`tt-video-comments-fetcher §6.3 L123`), whose PRD asks for a shared `comment_state` (`§14 Q2 L182`); on yt-comments-fetcher's comment index, which yt-replies-fetcher reads beside its own (`yt-comments-fetcher §6.3 L140`, `yt-replies-fetcher §5.1 L42`); on x-replies-fetcher's reply index (`x-replies-fetcher §6.3 L138`); and on ClickHouse `comments`, read by six fetchers (for example `ig-comments-fetcher §6.3 L119`, `news-comments-fetcher §6.3 L124`), where the stored hash is normalize-item's (`normalize-item §5.2 L51`) and LinkedIn rows go at 48 hours (`store-writer §5.3 L77`).
- Per-post markers (AU-020). The LinkedIn fetchers keep `newest_comment_at` and a running total "in the series state owned by comment-decay-scheduler" (`li-post-comments-fetcher §5.1 L50`, `li-own-comments-fetcher §6.3 L130`), and news-comments-fetcher passes its thread id through the scheduler (`news-comments-fetcher §6.3 L124`); `comment_series`, the job and the report carry neither (`comment-decay-scheduler §6.3 L147`, `§6.2 L141`, `§5.4 L127`).
- RN-16. The inventory gives `comment_series` the key (`item_id`, `lane`) (`INVENTORY L1871`) and omits "one `comment_series` row per post" (`x-replies-fetcher §5.1 L41`) and "exactly one `comment_series` row per lane" (`comment-decay-scheduler §13 L188`).

At stake: D2-Q062's confirmed-absence rule and D2-Q009's single hash need stored state every fetcher can rely on; built five ways, it is built, tested and purged five times.

**Options**

1. **One shared `comment_state` table behind one SDK helper; per-post state in the fetcher's `cursors` rows; `comment_series` keyed by post and lane (recommended).**
   - `comment_state`, one row per (`service`, `post_item_id`, `comment_key`): `parent_key`, `content_hash` (D2-Q009), `version`, `state` (`live`, `missing` after one miss, `deleted`), `first_seen_at`, `last_seen_at`, `reply_count` (as last seen, for reply thresholds); no text, no author. Only the service named in the row writes it, through an SDK helper that compares a fetch with the stored set and returns new comments, new versions and deletions confirmed under D2-Q062. Edits follow D2-Q009 (same key and a new version where the platform gives ids, otherwise a new key and the old key's deletion), so `superseded_by` and `edit_of` go. Rows are kept while the post can still be fetched (a margin set in the pilot) and always removed with it through the purge registry (D2-Q035); a `linkedin_48h` post's rows go at 48 hours.
   - Per-post fetch state (last complete fetch, stored count, partial bounds, `newest_comment_at`, the Disqus thread id) lives in the fetcher's own `cursors` row for the post (`scope_key = post:<item_id>`, D2-Q041), dropped when the series ends. The LinkedIn marker survives the 48-hour purge there; the running total stays the scheduler's `last_total`.
   - This replaces `comment_ledger`, `tt_comment_state`, the comment index, both reply indexes and the six ClickHouse reads. yt-replies-fetcher's skip rule, which D2-Q060 keeps (`yt-replies-fetcher §5.1 L42`), reads the parent comment's `reply_count` and `last_seen_at` in yt-comments-fetcher's rows through the helper, the table's one named cross-service read.
   - `comment_series` stays comment-decay-scheduler's, primary key (`item_id`, `lane`), lanes `comments` and `metrics` (`comment-decay-scheduler §6.3 L147`, `§5.1 L68`). x-replies-fetcher's "one row per post" is the comments lane, since X has no metrics lane (D2-Q058). RN-16 closes by recording the key with both statements.

   Consequences: F3 creates one table, partitioned by service if volume needs it (a setting); eleven comment and replies PRDs reword their state lines; `tt-video-comments-fetcher §14 Q2 L182` and `fb-post-comments-fetcher §14 Q6 L192` are answered.

2. **Per-service tables of one design (CF-045 (2)).** The same columns in a table per service under the naming rule, through the same helper. Consequences: no rows shared between services and separate purges, but eleven tables to create, migrate and register.
3. **ClickHouse `comments` as the only state (CF-045 (3)), with the markers in `comment_series` or carried as an opaque `fetch_state` on job and report (AU-020 (1), (3)).** Consequences: no Postgres table, but D2-Q062's first-miss mark has nowhere to live, a LinkedIn post's rows are gone before its +3 d fetch, fetchers depend on store-writer's write delay, and fetcher data sits in the scheduler's table.

**Why the recommendation.** One helper and one table do the same job once; Postgres state gives D2-Q062 its first-miss mark, and per-post markers in `cursors` follow D2-Q041's single cursor rule.

**Phase 2 records.** ADR "Comment state and comment series" (Applies to: F3, every comment and replies fetcher, comment-decay-scheduler, deletion-propagator, listening-sdk). CONVENTIONS v1.1: L30 (`comment_state` and `comment_series` with their keys), L62 and L63 (the stored state named). `DEFERRED.md`: the row-keeping margin (C11, after the pilot).

### D2-Q047 · ClickHouse: the column names readers use, what a purge empties, and the tables beyond CONVENTIONS

- **Class:** technical
- **Settles:** CF-049, CF-051, CF-052, keyword-matcher §14 Q1, store-writer §14 Q1
- **Blocks:** F8, F4 (the per-class purge lists), C4, C5, C6, C8, C9, C13, C14, C15, A5, FB6, VIG2, X7, W3, W5, YT5, YT7
- **Depends on:** D2-Q010 (`author_ref`), D2-Q011 (`post_ref.url`), D2-Q031 (item hits), D2-Q035 (tombstones and the guard), D2-Q056 (what YouTube's 30-day rule covers)

**Context.**

- Purges (CF-049). deletion-propagator's `purge_text` empties `text`, `text_norm`, `author_hash` and `url` (`deletion-propagator §5.3 L62`); store-writer's content TTL blanks eleven columns, `title` among them (`store-writer §5.3 L71`); yt-text-purger nulls `text`, `text_norm` and the author reference and counts a video's title and description as `text` (`yt-text-purger §5.3 L108`, `L69`), while normalize-item maps `snippet.title` to `title` (`normalize-item §5.3 L71`). So a purged YouTube video keeps its title. The author column is `author_ref` in store-writer (`store-writer §6.2 L110`) and `author_hash` in deletion-propagator, x-compliance-sync and retention-purger (`deletion-propagator §5.3 L60`, `x-compliance-sync §5.3 L81`, `retention-purger §5.3 L78`).
- Tables (CF-051). `CONVENTIONS L32` lists seven. store-writer adds `hits`, keyed (`client_id`, `keyword_id`, `item_id`) and fed by both hit topics (`store-writer §5.3 L63`, `§14 Q1 L181`), though source finders send discovery hits with no item (`CONVENTIONS L281`); aggregator writes daily and monthly tables and a refreshable view (`aggregator §6.2 L77`, `§5.3 L59`); alert-evaluator reads `_v` views no PRD defines (`alert-evaluator §6.1 L78`).
- Names (CF-052). The qualifier's daily sweep reads `max(published_at)` (`qualifier §5.3 L67`) and ig-comments-fetcher a `permalink` (`ig-comments-fetcher §5.2 L58`); store-writer creates neither, and the message has `created_at` and `url` (`normalize-item §6.2 L105-L106`). yt-comments-fetcher calls `comments` "keyed by `parent_id`" (`yt-comments-fetcher §4 L34`) where `item_id` is the key (`store-writer §5.3 L60`, `CONVENTIONS L70`).

At stake: the sweep that drives dormancy for every source queries a column that does not exist, a YouTube title outlives the 30-day rule, and F8 needs one list.

**Options**

1. **store-writer's columns are the contract, one purge list per class, `hits` for item hits only, aggregates and views in the contract (recommended).**
   - Names: F8 publishes store-writer's list (`store-writer §5.3 L60` to `L67`, example `§6.2 L99-L119`) as the contract, with its flattenings stated once (`author` into `author_ref`, `author_type`, `author_source_id`; `expires_at` as `content_expires_at`; `row_expires_at`; counts projected from `metrics_snapshot`). Readers use those names: the sweep reads `max(created_at)` (the approved qualifier moves under D2-Q001), ig-comments-fetcher takes the post's `url` from `post_ref` (D2-Q011) rather than a `permalink` column, and "keyed by `parent_id`" means looked up through the bloom index.
   - The author column is `author_ref` everywhere (D2-Q010): deletion-propagator selects by it, and x-compliance-sync and retention-purger send `author_ref` targets.
   - Purges: the SDK holds one field list per class, used by every executor (store-writer's column TTL, deletion-propagator's `purge_text`, yt-text-purger). For `youtube_30d_text` it is `text`, `title`, `text_norm`, `hashtags`, `at_mentions`, `links` and `author_ref`, so titles and descriptions go with the text (D2-Q056); `platform_id` and `url` stay, because the refresh re-reads by id, and counts follow the derived data. For the other classes with a content clock it is store-writer's full list (`store-writer §5.3 L71`). deletion-propagator's step (c) uses the item's class list. Tombstones and the resurrection guard are D2-Q035's.
   - `hits` holds item hits only, from `item.hits`, keyed as store-writer proposes. Every match a client sees is an item hit, whoever the poster is (D2-Q031); `discovery.hits` carry candidates only, for poster-resolver, and stay out of ClickHouse.
   - `aggregates_daily`, `aggregates_monthly` and `mv_aggregates_hourly` (aggregator) and the `_v` views (aggregator's over the aggregate tables; store-writer's `items_v` and `comments_v`, `store-writer §5.3 L82`) join the CONVENTIONS list, and F8 creates them. A `_v` view returns the latest version per key, and the item views blank expired content. alert-evaluator reads the aggregate views, not `hits` or `items` (`store-writer §4 L30` corrected).

   Consequences: F8 has one list; nine PRDs reword a column name, a field list or a reader line (the approved qualifier among them).

2. **Readers' names added as alias columns (`published_at`, `permalink`), and two purge lists kept on purpose, both written into CONVENTIONS (CF-052 (2), CF-049 (2)).** Consequences: no reader edits, but two names for one fact, and the YouTube title still needs a rule for which list it is on.
3. **One `hits` table with a nullable `item_id` and a `candidate_key` (CF-051 (2)), and no `_v` views, readers querying with `FINAL` (CF-051 (3)).** Consequences: candidate evidence becomes countable beside client hits and collapses under one key, and every reader repeats the version logic a view would hold once.

**Why the recommendation.** One published list ends the name drift, one per-class purge list empties the same fields whoever runs it, and keeping candidates out of `hits` keeps client counts to matches on items.

**Phase 2 records.** ADR "ClickHouse columns, purges and tables" (Applies to: F8, listening-sdk, store-writer, aggregator, alert-evaluator, deletion-propagator, retention-purger, yt-text-purger, x-compliance-sync, qualifier, keyword-matcher, ig-comments-fetcher, yt-comments-fetcher). CONVENTIONS v1.1: L32 (every table and view with its owner), L70 (where the column list lives), and the purge list per class beside the classes (L73 to L81).

### D2-Q048 · What clients can slice and be alerted on in v1

- **Class:** user (the views, alerts and history promised to clients are product choices)
- **Settles:** AU-014, AU-081, AU-083, aggregator §14 Q2, aggregator §14 Q3, aggregator §14 Q5, ig-hashtag-search §14 Q2, news-dedup §14 Q4
- **Blocks:** F8, then C15, A5, A1, A2, A3, A4, C3, N7, YT4, YT5, LI2, LI3, VLI4, FB4, VTT6
- **Depends on:** D2-Q008 (item kinds), D2-Q023 (analysis keys), D2-Q056 (YouTube and LinkedIn rollup lifetimes)

**Context.** aggregator rolls hits up by `(hour, client_id, keyword_id, platform, source_id, sentiment, topic_id, retention_class)` into mentions, reach, engagement and views kept ten years (`aggregator §5.3 L55`, `L57`); alert-evaluator has five rule types over those rows (`alert-evaluator §3 L22`). Items are purged after hours to months, so a slice missing here has no history. Other PRDs promise more (AU-081, AU-083):

- Slices: language (`lang-dialect-id §4 L37`); governorate, institution, brand and media tags (`analysis-entities §4 L33`, `analysis-media §4 L34`); unique stories (`news-dedup §4 L35`, `§14 Q4 L170`); YouTube channel owners kept apart (`yt-video-details-fetcher §4 L35`, `CONVENTIONS L76`); per-post LinkedIn comment rollups kept ten years (`li-notification-receiver §7 L142`, `li-own-comments-fetcher §7 L135`, `li-post-comments-fetcher §7 L139`).
- Labels (AU-014): `mixed` (`analysis-sentiment §2 L15`) is left out of the negative share (`aggregator §5.3 L57`, `alert-evaluator §5.3 L58`); topics come per taxonomy (`analysis-topics §5.2 L60`), so global and client topics collide under one `topic_id`.
- Alerts no rule type implements: engagement spikes (`fb-reactions-fetcher §4 L33`, `tt-video-stats-refresher §4 L36`), topic spikes (`analysis-topics §4 L37`), entities and logos, stories.
- Open: reach as of the rebuild or frozen, posts and comments apart, label names (`aggregator §14 Q2 L157`, `Q3 L158`, `Q5 L160`); a `top_media` "trending" score (`ig-hashtag-search §14 Q2 L188`); a minute grain, who approves alert defaults, `keyword_first_seen` for government clients (`alert-evaluator §14 Q2 L164`, `Q4 L166`, `Q5 L167`).

At stake: what a client can filter and be alerted on, and how far back.

**Options**

1. **Every promised slice in the aggregates now; the five built alert types in v1 (recommended).** Each part can be changed alone:
   - (a) The main grain gains `lang`, `dialect`, `route` and the item `kind` (`post`, `comment`, `article`, D2-Q008), so posts and comments count apart (aggregator Q3), and, on YouTube rows, the video's channel (`video_channel_id`), so YouTube figures stay per channel owner except where the carve-out allows totals (D2-Q056 sets their lifetime).
   - (b) `mixed` counts in every share's denominator and shows as its own share: negative share = negative ÷ (positive + neutral + negative + mixed), so the four shares add up to 100%; `pending` and `unscored` stay out; aggregator and alert-evaluator alike.
   - (c) `topic_id` = `<taxonomy_id>:<node_id>` (`global:outage`); a client taxonomy's topics appear only on that client's rows; label names as in `items.analysis/v1` (aggregator Q5).
   - (d) Entities, brands and media tags in their own aggregator rollup, keyed like the main table with that id in place of the topic, so two multi-valued slices never multiply rows; filled once A3 and A4 run.
   - (e) A `stories` measure: mentions of items with `is_origin = true`, one per story (`news-dedup §13 L160`), items outside news counting as their own story (news-dedup Q4: yes).
   - (f) No per-post LinkedIn rollup: per-post views read the base rows while they exist (48 hours); afterwards LinkedIn lives in the hourly grain like every platform.
   - (g) Reach as of the rebuild, as drafted, settling after an hour's +31 d pass (aggregator Q2); no `top_media` trending score in v1 (ig-hashtag-search Q2); campaign views are keyword slices (D2-Q031).
   - (h) Alerts: the five types. Engagement, topic, entity or logo and story alerts wait for A1 to A4 and D3, and their seven PRDs mark them for a later release (one approved, fb-reactions-fetcher, D2-Q001). No minute grain until the pilot shows missed spikes (`alert-evaluator §12 L138`, Q2); the user approves the defaults the pilot's backtests propose, account managers tune them (Q4); `keyword_first_seen` stays allowed for government clients on reputation and service-quality keywords, aggregate-only (`§5.3 L65`, Q5).

   Consequences: F8 adds five columns, a rollup table and a measure; rows multiply with the language and kind splits (measured in the pilot); every promised view except per-post LinkedIn history has a ten-year source; A5 still needs only C15, C5 and G1.

2. **The grain as written, plus the YouTube owner column**, the promises withdrawn (AU-081 option 3, AU-083 option 2). Consequences: least work for C15 and F8; language, entity and story views read base tables, so they stop at each platform's purge (48 hours on LinkedIn) and can never be rebuilt for past months.
3. **Everything now:** option 1 plus per-post LinkedIn rollups kept ten years and the four extra alert types (AU-081 and AU-083 option 1). Consequences: every promise kept; A5 waits for A1 to A4 and for metrics velocity; counsel must first confirm that per-post counts of member activity may outlive LinkedIn's 48-hour and six-week limits (`CONVENTIONS L192`).

**Open questions this also answers.** Reach is recomputed at each rebuild, as drafted (`aggregator §14 Q2`), and posts and comments are counted apart through the item `kind` dimension (`aggregator §14 Q3`).

**Why the recommendation.** A slice left out of the aggregates can never be added for past months, so the slices go in now; alert types can come later without changing the tables, and per-post LinkedIn history needs counsel's reading first.

**Phase 2 records.** ADR "Aggregate slices and alert types in v1" (Applies to: aggregator, alert-evaluator, store-writer, analysis services, news-dedup, LinkedIn and YouTube comment services). CONVENTIONS v1.1: the grain, measures and shares beside the analytics store (L32). `DEFERRED.md`: the four alert types (A5, after A1 to A4 and D3), the minute grain (A5, after the pilot), a trending score (U3), reach frozen at first sight (C15).

## Group 6 · Values, flags, vendors and clients

### D2-Q049 · What `tier` holds, and what "push" means

- **Class:** technical
- **Settles:** CF-095, CF-096, ig-account-media-poller §14 Q2
- **Blocks:** F3 (the column types), F5 (the scheduler's cadence lookup), C1, C7, C9, then TT1, VTT4, TG1, TG2, LI1, LI3, YT2, YT3, FB2, FB7, IG3, IG4, X3, X4, W1, W2, W4, N2, N3, N4, N5, X1, YT8, YT9, IG2, IG5, VLI3

**Context.** CONVENTIONS gives `tier` six values, `1`, `2`, `3`, `push`, `dormant`, `retired` (L36), with cadences for reach sources (L45 to L50); the examples write numbers (`"tier":2`, `qualifier §6.2 L84`) while registry-writer compares `tier = 'retired'` and calls `least_tier(...)` (`registry-writer §5.3 L72`). Two other meanings share the column (CF-095): for keyword rules, tier is a priority with its own cadences (`web-search-perplexity §5.1 L41`, `x-recent-search §5.1 L41`, `yt-keyword-search §5.1 L46`, `web-gdelt-poller §5.1 L41`); for news sites it comes from publishing rate (`news-site-resolver §5.2 L53`, `news-feed-poller §5.1 L42`). `push` mixes in a third meaning (CF-096): CONVENTIONS defines it for client-owned properties with "no polling for new posts; one reconciliation poll a day" (L48), but client TikTok accounts are read hourly while marked `push`, LinkedIn client pages are polled and "the generic push tier does not apply" (`li-client-posts-poller §5.1 L42`), every YouTube channel with a PubSubHubbub lease "sits in the push tier, client-owned or not" while its reach tier is still needed as "the secondary sort key and the quota priority" (`yt-uploads-reconciler §5.1 L45`, `yt-pubsub-receiver §5.1 L40`), and X treats stream coverage as push "while `sources.tier` keeps the reach tier" (`x-filtered-stream §5.1 L42`). A dormant source also needs its reach tier back when it posts again (L49).

**Options**

1. **Three columns: `tier` (1, 2, 3, always kept), `lifecycle` (`active`, `dormant`, `retired`) and `push_covered` (boolean), with one cadence table per source type in CONVENTIONS (recommended).**
   - `tier` is the reach tier for pages, accounts, channels and groups; a source on a client's priority list is tier 1 whatever its followers (CONVENTIONS L45, D2-Q043; `registry-writer §14 Q3 L160`), and rule 6 (L247) is reworded to say so. For keyword rules and hashtags it is the client priority, and for news sites the client priority or publishing rate (`news-site-resolver §5.2 L53`).
   - For keyword rules, hashtags and news sites, `tier` sets cadence only. The quota priority always comes from D2-Q018's table, which gives client keyword and hashtag searches priority 2 whatever their tier (`quota-governor §5.1 L44`); F5's helper reads the table, never `tier`, for these source types.
   - `lifecycle` replaces `dormant` and `retired` as tier values.
   - `push_covered` is true only when new posts arrive by webhook, PubSubHubbub, bot or stream; the poller then makes one reconciliation read a day instead of its tier cadence. It is false for client TikTok accounts and LinkedIn client pages, which are polled (`tt-client-videos-fetcher §5.1 L43`, `li-client-posts-poller §5.1 L42`); their cadence comes from an `owned_by_client` row of the cadence table (TikTok hourly, LinkedIn every 30 to 60 minutes).
   - A Telegram bot channel is `push_covered` with its reach tier used only for ordering ("tiered by nothing", `tg-bot-channel-receiver §5.1 L44`); its daily job is the receiver's own health check that the bot is still an administrator, not a reconciliation read, since the Bot API has no history method (CONVENTIONS L196).
   - The cadence table, read by F5's scheduler helper, has a row per source type (reach, `owned_by_client` per platform, keyword rules per engine, hashtags, news sites per poller).

   Consequences: F3 types `tier` as a small integer; registry-writer's `least_tier` becomes a plain minimum and its `'retired'` test reads `lifecycle`, and qualifier rule 6 and news-site-resolver's tier keep numbers (approved PRDs move under D2-Q001); `tier_change` events keep numbers; README decision 8's "`tier = push`" becomes `owned_by_client` plus the hourly row (D2-Q024), and the amber poller never reconciles these accounts (D2-Q052).

2. **One text enum as written (`1`, `2`, `3`, `push`, `dormant`, `retired`) with an ordering function, plus the cadence table per source type.** Consequences: no schema change from CONVENTIONS, but a pushed YouTube or X source loses its reach tier, and a dormant source must recompute its tier from followers when it wakes.
3. **The reach tier only for accounts, pages and channels; keyword rules and news sites get a separate `cadence` field and no tier.** Consequences: clean for searches, but `push` and the lifecycle states still share the column, so CF-096 stays open.

**Open questions this also answers.** Volume and publishing rate still set cadence, through the cadence table, not through `tier`: a hashtag's or news site's observed volume or rate picks its row (thresholds are pilot values), and a client's priority sets `tier` (`ig-hashtag-search §14 Q3`, `tt-hashtag-feed-poller §14 Q3`, `news-site-resolver §14 Q3`, `news-feed-poller §14 Q1`, `yt-web-search-bridge §14 Q4`, where tier 1 keeps the API search). A client-owned Instagram account is not `push_covered`, since its webhooks announce comments and mentions but not posts; it is polled at its tier's cadence (`ig-account-media-poller §14 Q2`).

**Why the recommendation.** Each of the three meanings gets its own column, so no service overloads one value; `push_covered` keeps one meaning, so F3 and F5 can trust it; the cadences the PRDs need become rows of one table; and priority stays with D2-Q018 alone.

**Phase 2 records.** ADR "Tier, lifecycle and push coverage" (Applies to: F3, F5, all pollers, receivers and searchers, registry-writer, qualifier, quota-governor, listening-sdk). CONVENTIONS v1.1: L36 (the three columns), L44 to L51 and L276 (the cadence table per source type, with its `owned_by_client` rows), L247 (rule 6 sets `tier`, a priority-listed source tier 1, and `push_covered`).

### D2-Q050 · Where the vendor flags live, what happens while one is off, and the X plan gate

- **Class:** technical
- **Settles:** CF-102, AU-095, quota-governor §14 Q3, x-user-timeline-poller §14 Q5
- **Blocks:** F3, F4, F5, F6, C1, C5, C7, C8, C9, C10, C11, C12, IG2, VTT1, VTT2, VTT4, X1 to X7, and every amber service
- **Depends on:** D2-Q016 and D2-Q021 (health and fallback), D2-Q017 (`skipped_flag_off`), D2-Q042 (`source_id` on the governor's request), D2-Q051 (vendor values), D2-Q053 (X before Enterprise)

**Context.**

- Storage (CF-102 a, b). CONVENTIONS configures by environment variables (`CONVENTIONS L12`) yet reads the flag "at the start of every job" (`L102`), with no default (`L238`; `CLAUDE.md` L9: off). Five shared services read other services' flags (e.g. `quota-governor §6.1 L94`, `poster-resolver §5.2 L56`), so a flip redeploys them all.
- Flag off and fallback (CF-102 c, d). tt-profile-videos-poller's scheduler "emits nothing" while the flag is off (`tt-profile-videos-poller §5.1 L41`); its own test and two approved siblings count a day of jobs as `flag_off` (`tt-profile-videos-poller §13 L177`, `tt-keyword-search §13 L145`, `tt-hashtag-feed-poller §13 L154`). `fallback_on` is a flag the canary sets (`CONVENTIONS L102`), `fallback` a `health` value (`L36`); ig-hashtag-search sends `fallback_on` for a budget wait (`ig-hashtag-search §5.1 L57`).
- X gate (AU-095). A government end user and a multi-client product both need Enterprise, and a government end user must be named at use-case review (`CONVENTIONS L87`, `L113`, `L188`). The X services test a `clients` entitlement (`x-user-timeline-poller §5.2 L55` and two more), an app-wide `X_PLAN` (`x-user-resolver §5.2 L54` and one more) or `clients.x_enterprise` (`keyword-matcher §5.3 L69`); x-recent-search relies on a registry refusal registry-writer lacks (`x-recent-search §12 L175`). Open: the column (`x-user-timeline-poller §14 Q5 L195`) and a governor deny for government-only sources (`quota-governor §14 Q3 L172`, proposed yes).

At stake: amber code off in one service and on in another during a rollout, and X data reaching a client X's plan does not cover.

**Options**

1. **Flags in a table read per job, nothing emitted while off, fallback a health state, a plan setting plus a per-client declaration (recommended).**
   - `feature_flags` (`name`, `value`, `changed_by`, `changed_at`, `reason`): one row per amber flag of `CONVENTIONS L238` and `L280`, one per override D2-Q051 allows (fb-keyword-search's vendor), and one for `X_PLAN`. F3 seeds every flag `off` and `X_PLAN = pay_per_use`; the audited admin API makes every change (D3 specifies the writer).
   - The SDK reads the row at the start of every job, never cached; the environment variable counts only where the table has no row (local and test runs), and a missing one means `off`. Shared readers read the same rows, so nothing is redeployed.
   - While a flag is `off`, schedulers emit nothing; a queued job ends `skipped_flag_off` at its start (D2-Q017), not an attempt; the governor's `flag_off` deny is the second line (`quota-governor §5.3 L67`). The three tests are rewritten (two approved PRDs move under D2-Q001); backfill-orchestrator keeps an amber source `pending` until its flag is on, not `done` with a note.
   - `fallback` is only a `sources.health` value, set from the canary's route-level `health_change` (D2-Q016, D2-Q021) and announced as `fallback_on` and `fallback_off` events (D2-Q014), never a flag. While health is `fallback` and the flag is not `off`, a reader uses the alternate vendor in the vendor rows of `credentials` (D2-Q051; `source-health-canary §13 L152` reworded to "not `off`"); a budget wait never triggers it (D2-Q052).
   - X gate, as D2-Q053 sets it: `X_PLAN` (`pay_per_use` or `enterprise`) and `clients.x_end_user_declared` (true once X has named the client at use-case review; answers `x-user-timeline-poller §14 Q5 L195`). A government client gets X data only when `X_PLAN = enterprise` and it is declared (`CONVENTIONS L113`); before Enterprise, any client needs the declaration; after it, X data joins the shared pool for other clients. Every X content reader drops gate-closed clients from `client_ids`, skipping a job left with none (five already do); x-recent-search (approved; moves under D2-Q001) does so instead of the registry refusal; keyword-matcher gates X items on the same settings; x-compliance-sync is never gated. Second line: quota-governor denies an X request whose source has only gate-closed clients (answers `quota-governor §14 Q3 L172`: yes) and keeps `x_enterprise_required` (`quota-governor §5.3 L85`).

   Consequences: F3 creates `feature_flags` and the column; F4 gives every service one flag reader; the approved li-org-resolver and li-post-search stop reading `LI_VENDOR_ROUTE` from the environment (`li-org-resolver §6.1 L75`, `li-post-search §6.1 L79`).

2. **Environment variables as written, every reading service listed, a restart on change; the X gate as a per-client column only (CF-102 (2), AU-095 (1)).** Consequences: no table, but every flip is a coordinated redeploy of at least six services, and a column alone cannot record the company's plan.
3. **Flags in the environment, the canary's fallback state in the control plane; a registry refusal of gate-closed X rules, fetch-time checks second (CF-102 (3), AU-095 (3)).** Consequences: fallback changes at run time but flags need redeploys, and a registry refusal cannot handle a rule shared by open and gate-closed clients (D2-Q044), so the fetch-time drop stays.

**Why the recommendation.** Only a flag read per job from one table makes "at the start of every job" hold across shared services; one plan setting and one declaration per client give every X reader one test.

**Phase 2 records.** ADR "Flags, fallback and the X plan gate" (Applies to: F3, every amber and X service, keyword-matcher, quota-governor and the other shared flag readers, listening-sdk). CONVENTIONS v1.1: L12 (flags and `X_PLAN` in `feature_flags`, the environment a local default), L102 (fallback a health state set by the canary), L87 and L113 (the gate, for every client before Enterprise), L238 (default `off`, nothing emitted while off).

### D2-Q051 · Vendors: which vendor serves which role, how they are screened, how they are named

- **Class:** user (which vendors are paid, which is primary, and clearing them under the first hard constraint are vendor and compliance choices)
- **Settles:** CF-097, CF-103, fb-group-posts-poller §14 Q3, fb-group-posts-poller §14 Q4, fb-keyword-search §14 Q1, li-company-posts-poller §14 Q4, li-post-comments-fetcher §14 Q6, tg-channel-resolver §14 Q3, tg-message-search §14 Q2
- **Blocks:** F2, F3, then F4, C7, C12, the vendor probes VFB0, VIG0, VTT0, VLI0 and VTG0, VFB1 to VFB3, VTT1 to VTT6, VLI1 to VLI4, VTG1 to VTG3, W1, W2, W4, YT9, X1 to X6
- **Depends on:** D2-Q050 (flags in a control-plane table, fallback set only by the canary, the X plan gate)

**Context.** CONVENTIONS lists five flags, each "off, or the vendor name" (L238), adds `TG_POSTS_ACTOR` with Actor names (L280), and spells those Actors `apify_tugelbay` and `apify_sovereigntaylor` in the registry (L36), as tg-channel-posts-poller's records do (`§6.2 L112`). D1 found:

- One value per flag where two roles or a fallback need two: the approved Telegram PRDs treat any value but `off` as on, since Telemetrio serves search and stats and an Actor serves posts (`tg-message-search §14 Q2 L153`, `tg-channel-resolver §14 Q3 L166`); EnsembleData is "primary or fallback per the flag" (L177); ScrapeCreators may have no keyword search (`fb-keyword-search §5.3 L63`, `§14 Q1 L181`), while fb-group-posts-poller proposes it as primary (`§14 Q3 L195`).
- Engines in `vendor` on green records (`web-search-perplexity §6.2 L97`, `web-search-mojeek §6.2 L96`, `web-gdelt-poller §6.2 L99`), other green records `null`; a Telegram channel's row says `telemetrio` (`tg-channel-resolver §4 L34`) while an Actor reads its posts.
- Clearance: SociaVault, ScrapeCreators and TikHub are listed as "Weakly cleared (country known, owner not verified)", and the Actor publishers harvestapi, tugelbay and sovereigntaylor are not listed (L6, L190, L199); three PRDs ask who verifies them, and when (`fb-group-posts-poller §14 Q4 L196`, `li-company-posts-poller §14 Q4 L187`, `li-post-comments-fetcher §14 Q6 L197`).
- The X plan gate under three names (CF-103 e).

At stake: which vendor is paid and named to clients, and whether an unverified owner slips past the no-Israeli-vendor rule.

**Options**

1. **One setting per vendor role, the cleared vendor first, owners verified before any spend (recommended).**
   - (a) Primaries. Facebook: `FB_VENDOR_ROUTE = scrapecreators` (groups, group comments) with an override `fb-keyword-search = sociavault` while ScrapeCreators has no search (fb-keyword-search Q1); ScrapeCreators costs half of SociaVault or less per request (USD 0.99 against 1.99 and USD 1.88 against 4.83 per 1,000 at each end of the ranges, one SociaVault credit per request, L92; fb-group-posts-poller Q3). Instagram: `sociavault`. TikTok: `ensembledata` (cleared, Singapore, already contracted, L6, L177) unless VTT0, which compares cost since its contract price is not in the fact sheet, shows otherwise; TikHub the fallback once its owner is verified. LinkedIn: `harvestapi`. Telegram: `TG_VENDOR_ROUTE = telemetrio` for search and stats and `TG_POSTS_ACTOR` for posts, as L280 already splits them, each service reading its own flag's value (tg-message-search Q2, tg-channel-resolver Q3); the primary Actor chosen by the one-week, 50-channel comparison tg-channel-posts-poller proposes (Q3), run in staging after VTG0 on a budget the user sets (the VTG0 brief caps spend at USD 5), the other Actor the fallback.
   - (b) Fallback order per role in the vendor rows of `credentials` (D2-Q016, which absorbs `vendor_keys`), switched only by the canary (D2-Q050).
   - (c) One lower-case spelling in flags, `sources.vendor` and `provenance.vendor`, naming who collects: `sociavault`, `scrapecreators`, `tikhub`, `ensembledata`, `harvestapi`, `telemetrio`, `tugelbay`, `sovereigntaylor` (Actor paths and the Apify account in configuration). On green records `vendor` names the licensed engine (`perplexity`, `mojeek`, `gdelt`), else `null`; amber filters read `route`, never `vendor`.
   - (d) `sources.vendor` names the vendor that reads the source's posts (a Telegram channel: its Actor; a Telegram keyword rule: `telemetrio`); registry-writer updates a role's rows when its primary changes; during a fallback each record names the vendor that returned it.
   - (e) The user, or counsel for the user, verifies the owner and country of each weakly cleared vendor and Actor publisher before its probe (VFB0, VIG0, VTT0, VLI0 and VTG0 already need the contract and the flag value) and at each renewal, recorded in `docs/dependencies.md` and the CONVENTIONS list; until then its flag value cannot be set (fb-group-posts-poller Q4, li-company-posts-poller Q4, li-post-comments-fetcher Q6). Perplexity, flagged "client decides" (L6), keeps `vendor = perplexity` so a client may decline it (D3 specifies the setting).
   - (f) The X plan gate: as D2-Q050 recommends.

   Consequences: two Facebook vendors to contract and screen; TikTok starts on a cleared vendor; CONVENTIONS L6, L36, L238 and L280 aligned; tg-channel-resolver and tg-message-search (approved) change under D2-Q001; values are renamed before any data exists.

2. **One vendor per platform where possible:** SociaVault for all amber Facebook and Instagram services, EnsembleData alone for TikTok. Consequences: fewer contracts and owner checks; Facebook group and comment requests cost about twice as much or more; no TikTok fallback.
3. **Flags as on/off switches per platform; vendors and fallback order only in the vendor rows of `credentials`** (CF-103 option 2). Consequences: ops switch vendors without touching flags; the flag no longer says who is paid, so an audit reads two places.

**Why the recommendation.** It uses the cheaper vendor where it has the endpoint and the cleared one where there is a choice, and it makes the owner check a condition of any spend.

**Phase 2 records.** ADR "Vendor roles, values and screening" (Applies to: every amber service, qualifier, registry-writer, quota-governor, source-health-canary, the web engines). CONVENTIONS v1.1: L6 (the Actor publishers and the verification rule), L36 (vendor values), L238 and L280 (one flag list with roles and the override). `DEFERRED.md`: the Telegram Actor comparison (VTG3), TikHub's verification (VTT0).

### D2-Q052 · Amber data and clients: consent, the 31st hashtag, and clients' own properties

- **Class:** user (whether a client receives vendor-bought data, and whether its own properties may be read through a vendor, are consent choices)
- **Settles:** AU-038, AU-060, AU-071, AU-087, AU-091, AU-092, fb-group-comments-fetcher §14 Q4, tg-bot-channel-receiver §14 Q6, tt-profile-videos-poller §14 Q3
- **Blocks:** F2, F3, then C1, C5, C7, C9, C11, C12, IG2, TT1, TG1, VIG1, VIG2, VFB1 to VFB3, VTT1 to VTT6, VTG3, and the other amber sessions (VTG1, VTG2, VLI1 to VLI4)
- **Depends on:** D2-Q021 (the government exclusion), D2-Q050 (flags and the canary-only fallback)

**Context.** CONVENTIONS makes amber services optional, flagged, disclosed and "excluded from government contracts" (L7), with no per-client consent and no `clients` columns (L30). The PRDs split (AU-092): four check that a client "accepted the amber provenance" or that its contract allows amber (`ig-comments-fetcher §5.1 L41`, `ig-keyword-search §5.2 L58`, `tt-profile-videos-poller §5.1 L43`, `tt-client-videos-fetcher §3 L27`); the Telegram, other TikTok and Facebook amber services check only the government flag (`tg-channel-posts-poller §5.1 L42`, `tt-keyword-search §5.2 L48`, `fb-group-posts-poller §5.1 L40`). Also:

- comment-decay-scheduler opens amber series whenever the flag is on, reads no `clients` and never cancels on flag-off (`comment-decay-scheduler §5.1 L44`, `§6.1 L135`), unlike `fb-group-comments-fetcher §5.1 L42` (AU-038).
- A client's 31st Instagram hashtag is queued under rule 5 (`ig-hashtag-search §12 L168`, `qualifier §5.2 L56`) or registered amber (`ig-keyword-search §3 L20`, `§13 L169`) (AU-060); budget waits are announced as `fallback_on`, which nothing applies or ends (`ig-hashtag-search §5.1 L57`; AU-087); the canary has no Instagram alternate (`source-health-canary §5.1 L47`) though `ig-hashtag-search §8 L144` expects one (AU-071).
- Client-owned TikTok accounts and Telegram bot channels are green rows (`tg-bot-channel-receiver §5.2 L70`) relying on a daily amber reconciliation that selects only amber rows (`tt-client-videos-fetcher §8 L132`, `tg-channel-posts-poller §5.1 L44`) (AU-091); asked in `tt-profile-videos-poller §14 Q3 L188` and, for 90 days of pre-join history, `tg-bot-channel-receiver §14 Q6 L199`.

At stake: a commercial client receiving vendor-bought data it never agreed to, and vendor money spent on data no client may use.

**Options**

1. **Amber by explicit consent, never on a client's own properties (recommended).**
   - (a) `clients.accepts_amber`, off by default, set when the client's contract allows vendor data (D3 specifies the screen), always off for `client_type = government` (a check in F3). Amber schedulers select a source only if one of its clients accepts amber; amber jobs re-check at run time and end without a call if none does; amber records list only accepting clients in `client_ids`; keyword-matcher fans amber items out to accepting clients only (D2-Q053).
   - (b) comment-decay-scheduler, which then reads `clients`, opens an amber series only while the flag is on, an accepting client watches the source and its vendor spend is under the cap (rule 5, the per-source sub-counter of D2-Q042); it cancels open series when the flag goes off or the last accepting client leaves (its catch-up rule, `§5.1 L44`, applies if the flag returns).
   - (c) Rule 5 gains the Instagram cap (30 hashtags per business account per 7 days, L89). Over the cap of a client's account, the hashtag is registered `route = amber`, `vendor = sociavault` (read by ig-keyword-search) if that client accepts amber and `IG_VENDOR_ROUTE` is on; otherwise it is queued and the client told. ig-hashtag-search reports budget waits as `updated` with `budget_wait`, never `fallback_on` (qualifier and ig-hashtag-search, both approved, move under D2-Q001).
   - (d) The canary fallback for green hashtags is declared in `canary_targets` (`alternate_vendor = sociavault`, `flag_name = IG_VENDOR_ROUTE`, `scope = non_government`), as ig-hashtag-search expects; while it lasts, only accepting clients receive the items.
   - (e) A client's own green properties (TikTok Display accounts, Telegram bot channels, owned Pages and accounts) are never read through a vendor: no daily amber reconciliation, no outage gap fill, no pre-join history (tt-profile-videos-poller Q3 and tg-bot-channel-receiver Q6: no). The green read counts as complete; outages are reported to the client.

   Consequences: one column and one SDK check for the 18 amber services (README L16), replacing the government-only check in most and touching six approved PRDs (D2-Q001); vendor money only for data a client accepted; a client's Telegram posts missed in a receiver outage longer than Telegram keeps updates (24 hours, to be confirmed, `tg-bot-channel-receiver §5.1 L52`) are lost and reported; TikTok completeness rests on `video.list` returning every video (`tt-client-videos-fetcher §14 Q1 L176`).

2. **Option 1, but an accepting client's own properties may also be read through the vendor:** daily reconciliation and outage gap fill (the amber pollers also select green push sources of accepting clients, AU-091 option 1) and an opt-in 90-day Telegram pre-join history, marked amber. Consequences: no lost Telegram posts after a long outage, history for new channels, and the view counts the bot lacks (`tg-bot-channel-receiver §5.4 L103`); a daily vendor read per owned property; mixed provenance on a client's own channel.
3. **Government flag only, as CONVENTIONS L7 says.** Consequences: no consent column; every non-government client receives amber data while a flag is on, even one whose contract excludes it.

**Why the recommendation.** Amber data rests on the vendor's contract, not ours, so a client should take it knowingly; a property authorised through the platform's own route should not be quietly re-read through a scraper.

**Phase 2 records.** ADR "Amber data and client consent" (Applies to: every amber service, comment-decay-scheduler, keyword-matcher, qualifier, registry-writer, source-health-canary, tt-client-videos-fetcher, tg-bot-channel-receiver). CONVENTIONS v1.1: L7 (consent beside disclosure and the government exclusion), rule 5 (L246, the Instagram cap). `DEFERRED.md`: option 2 for Telegram, once the pilot has measured receiver outages (TG1).

### D2-Q053 · Who may see an item: a shared pool or per-client data

- **Class:** user (who may see data fetched under another client's grant rests on platform terms and on what clients are promised)
- **Settles:** keyword-matcher §14 Q4, tg-message-search §14 Q3, tt-client-videos-fetcher §14 Q4, x-recent-search §14 Q3
- **Blocks:** F2 (each producer's visibility), F3 (owners recorded apart from watchers), then C5, C13, Q1, U2, FB2, FB7, IG4, LI1, TT1, TG1, X1 to X7 (the X plan gate)
- **Depends on:** D2-Q043 (`client_sources`), D2-Q050 (the X plan gate), D2-Q052 (amber consent)

**Context.** keyword-matcher decides which clients an item is matched for: items from `owned_by_client` sources, or classed `meta_on_request` or `linkedin_48h`, go only to the source's `client_ids`; "Everything else is the shared pool", government rules aside (`keyword-matcher §5.3 L68` to `L70`). It asks whether Meta items may join the pool ("The draft says no", `§14 Q4 L183`); tt-client-videos-fetcher proposes showing its items only to the authorising client (`§14 Q4 L179`, `§9 L142`). The platforms:

- Meta: "Tech Provider processes only on behalf of its client", "no sale or licensing of Platform Data" (`CONVENTIONS L163`); our PPCA calls are made "on behalf of the client whose keyword triggered it" (`fb-page-search §5.3 L67`), with a watching client's token (`fb-page-feed-poller §5.2 L55`).
- Client grants: LinkedIn Community Management covers client-administered pages, and "member data cannot be exported to customers" (L90, L192); TikTok Display reads the client's own videos (L176); our Telegram bot reads channels whose owners, "client staff, or a cooperating outlet", invite it (`tg-bot-channel-receiver §4 L33`).
- Our licences: X through our company app, though "a multi-client product requires an Enterprise plan" (L87); YouTube through our company key (L12); our news crawler; web results we may store (L218, L219).

At stake: a client seeing data it has no right to, or every client re-adding sources the registry already reads.

**Options**

1. **Visibility follows the grant the data was fetched under (recommended).** Each producing service declares one value in the contracts package; keyword-matcher's gate reads it through `provenance.service`, not the retention class:
   - `owner`: a client's own grant (Page or Instagram account token and webhooks, LinkedIn Community Management, TikTok Display, our bot in the client's own channel): the authorising client only, even if others watch the property (tt-client-videos-fetcher Q4: yes).
   - `watchers`: Meta data under PPCA or Instagram Public Content Access: the clients in the source's `client_ids` only (keyword-matcher Q4: no).
   - `pool`: our own licences and the open web (X under the point below, YouTube, news, web search, Telegram channels a non-client owner opened to the product): every client whose keywords match.
   - Amber: the pool, limited to accepting clients (D2-Q052).
   - X before Enterprise: X's self-serve plan serves "a limited number of end users" and "a multi-client product requires an Enterprise plan" (CONVENTIONS L87, L188; `x-recent-search §7 L146`). So X joins the pool only once `X_PLAN = enterprise`; until then X data reaches only the clients declared to X at use-case review (`clients.x_end_user_declared`, D2-Q050), and quota-governor's `x_enterprise_required` alert (`quota-governor §13 L164`) fires when a further client would receive it. The move to Enterprise comes at the first government end user or the second paying client on X, whichever is first (`x-recent-search §14 Q3 L194`); its price is not in the fact sheets and must be quoted by X. Alternative for this point alone: pool X on pay-per-use from the start and accept the risk that X objects at use-case review.

   Consequences: a new client sees every pooled source from day one; Meta coverage grows with each client's own registered sources; a property one client owns reaches another only through a public-route read on that client's behalf, so F3 records owners apart from watchers; offboarding deletes data held only for the departing client (`deletion-propagator §13 L165`); the query API and portal (D3) apply the same rule.

2. **Per client for everything.** Consequences: the simplest story for a platform; a client sees no site, channel or account until it is on its own list, so discovery and share of voice shrink to its own registry.
3. **Pool everything except `owner` data, Meta PPCA included.** Consequences: the widest coverage; it contradicts L163 and the approved fb-page-search, and risks PPCA, the only green route to Facebook Pages, at Meta's annual Data Use Checkup (L154).

**Open questions this also answers.** Mentions found on channels the qualifier rejected stay visible as mentions (the item matched a client's keyword; rejecting the channel only keeps it out of the registry), on every search route (`tg-message-search §14 Q3`).

**Why the recommendation.** Meta and client-authorised APIs bind data to a client; our licences and the open web do not, so pooling those gives every client the full registry at no extra cost.

**Phase 2 records.** ADR "Who may see an item" (Applies to: F2, F3, keyword-matcher, deletion-propagator, quota-governor, every producer, every X service, the query API and portal). The X point also rewords CONVENTIONS L113 and the X service index so that the plan gate covers every client, not only government ones. CONVENTIONS v1.1: each route's visibility in the service index (L224 to L236). `DEFERRED.md`: counsel confirms that one PPCA read may serve every client watching a Page (FB2, before App Review).

## Group 7 · Retention

### D2-Q054 · Retention classes for the routes CONVENTIONS gives none: TikTok Display, the Telegram bot, web-search results

- **Class:** user (a reading of platform terms and of what clients may be promised; counsel confirms before production)
- **Settles:** CF-104, retention-purger §14 Q3, tg-bot-channel-receiver §14 Q5, tg-discussion-receiver §14 Q5, tt-client-videos-fetcher §14 Q2
- **Blocks:** F3 (it seeds `retention_classes`), F8 (TTLs by class), C6, C14, then TT1, TG1, TG2, W1, W2, W3, W4, YT9

**Context.** Every record carries a `retention_class` chosen by route (`CONVENTIONS L247`), and the six classes (`CONVENTIONS L75` to `L80`) name none for three routes:

- TikTok Display API (green, client-authorised accounts): README decision 8 proposes `tiktok_display` (`README L185`); tt-client-videos-fetcher writes it, "proposed and not yet in `retention_classes`" (`tt-client-videos-fetcher §6.2 L106`, `L115`), kept "while the authorisation is active and deleted on revocation, client offboarding or TikTok's request, as `meta_on_request` does" (`§14 Q2 L177`).
- Telegram Bot API (green, channels and groups whose owners added the bot): both receivers write `vendor_agreed` (`tg-bot-channel-receiver §6.2 L125`, `tg-discussion-receiver §6.2 L129`), a class defined "per the vendor contract" with a default of 24 months for raw text (`CONVENTIONS L79`), although no vendor is involved; both ask for a dedicated class (`tg-bot-channel-receiver §14 Q5 L198`, `tg-discussion-receiver §14 Q5 L202`).
- Web-search results (Perplexity, Mojeek, GDELT): they carry `news_excerpt` (`web-search-perplexity §6.2 L106`, `web-search-mojeek §6.2 L105`, `web-gdelt-poller §6.2 L109`), whose only clock is the 7-day full-text cache (`retention-purger §5.3 L67`), for records that hold a title, a snippet and a URL but no full text; retention-purger leaves both open "to be set with counsel" (`retention-purger §14 Q3 L172`).

**Options**

1. **Add `tiktok_display` and `telegram_bot`; keep web results under `news_excerpt` (recommended).** `tiktok_display`: kept while the client's authorisation is active; deleted on revocation, client offboarding or TikTok's request (the `meta_on_request` clock under TikTok's name). `telegram_bot`: kept while the bot stays in the channel; for a client's own channel also only while the client relationship lasts, and for a cooperating channel whose owner agreed to add the bot (`tg-bot-channel-receiver §1 L9`) until the owner removes it or asks; deleted on the owner's or client's request, on offboarding, or on a member's request; commenters' identities are already hashed at the edge (D2-Q010). Web results stay `news_excerpt`, with CONVENTIONS stating that the class keeps excerpts and metadata and that its 7-day clock applies only where full text is cached. Consequences: F3 seeds two more classes; each route's clock matches its terms; counsel reviews the two new clocks before production (G4).
2. **Add all three, with a `web_result` class of its own.** Consequences: as option 1, plus a clock for web snippets that can differ from news excerpts (for example a shorter one if a search provider's terms require it).
3. **Map each route to an existing class.** `tiktok_display` as `meta_on_request`, Telegram bot data as `vendor_agreed`, web results as `news_excerpt`, with the mapping written in CONVENTIONS. Consequences: no new classes, but Telegram bot data keeps a vendor-contract clock with no vendor behind it (24 months by default), and the provenance statement names Meta's rule for TikTok data.

**Why the recommendation.** The two green routes rest on the property owner's consent, so their data should go when that consent or the client relationship ends, which neither `vendor_agreed` nor a Meta-named class says; web snippets fit `news_excerpt` once its clock is worded for records without full text.

**Phase 2 records.** ADR "Retention classes for TikTok Display, the Telegram bot and web search" (Applies to: F3, F8, retention-purger, store-writer, tt-client-videos-fetcher, tg-bot-channel-receiver, tg-discussion-receiver, the web engines). CONVENTIONS v1.1, retention classes (L73 to L81): the two new classes and the `news_excerpt` wording. `DEFERRED.md`: counsel's confirmation of both clocks, owner G4.

### D2-Q055 · LinkedIn data: which class holds what, and the 24-hour and six-week rules

- **Class:** user (a reading of LinkedIn's terms, which `li-company-posts-poller`, `li-post-search` and `li-post-comments-fetcher` leave "until legal decides")
- **Settles:** CF-105, AU-078, li-client-posts-poller §14 Q2, li-company-posts-poller §14 Q5, li-own-comments-fetcher §14 Q2, li-own-comments-fetcher §14 Q3, li-post-comments-fetcher §14 Q1, li-post-search §14 Q2
- **Blocks:** F3, F8, C4, C6, C13, C14, then LI1, LI2, LI3, VLI1, VLI2, VLI3, VLI4

**Context.** CONVENTIONS defines `linkedin_48h` ("member social-activity data purged after 48 hours; organization data as the API terms allow", L77) and quotes the terms: "member social-activity data stored at most 48 hours; most member profile data 24 hours; organization social activity data six weeks (six months if authenticated)" (L192). Classes follow the route (L247), so amber LinkedIn would get `vendor_agreed` (24 months by default, L79). The PRDs split:

- Amber: posts carry `vendor_agreed` (`li-post-search §6.2 L92`, `li-company-posts-poller §6.2 L114`), but member reposts are held as `linkedin_48h` until legal decides (`li-company-posts-poller §7 L133`), and vendor comments carry `linkedin_48h`, "the stricter option, until legal decides" (`li-post-comments-fetcher §6.2 L120`, `§7 L139`); each asks the question the other way round (`li-post-search §14 Q2 L164`, `li-company-posts-poller §14 Q5 L188`, `li-post-comments-fetcher §14 Q1 L192`).
- Green: one class, `linkedin_48h`, for organization posts and member fields, which retention-purger should apply "by field" (`li-client-posts-poller §7 L135`), while retention-purger purges by kind and has no field-level mode (`retention-purger §5.3 L64`, `L70`; AU-078). Whether six weeks or six months applies is open and also sets the backfill cap (`li-client-posts-poller §5.1 L50`, `§14 Q2 L188`).
- Member profile data at 24 hours (`li-post-search §7 L115`, `li-org-resolver §7 L115`, `li-company-posts-poller §7 L133`) has no class.

**Options**

1. **LinkedIn's terms apply whatever the route: class by content, the stricter reading for members, `linkedin_org` for organizations on green and amber (recommended).** The LinkedIn PRDs say the restricted uses "are carried on every LinkedIn item regardless of route", organization data included (`li-post-search §7 L115`, `li-org-resolver §7 L115`). Member-authored content (comments, member posts, reposts of member posts) is `linkedin_48h` on every route, counted from `fetched_at`. Organization-authored posts and their counts get a new class `linkedin_org` on both routes: six weeks, or six months if counsel confirms that our access counts as "authenticated". Member fields inside an organization post (a mentioned member, an administrator) are hashed or dropped by the adapter before the first write (option 2 of AU-078, consistent with D2-Q010), so no field-level purge is needed. Member profile data is never stored (CONVENTIONS L114), except a member poster's id held until poster-resolver classes it, which must happen within 24 hours or the id is dropped (L192). Consequences: one class per record, which retention-purger and the ClickHouse TTLs can apply; the green backfill cap is six weeks for now; amber organization history beyond six weeks survives only as aggregates; li-post-search's member posts, an approved PRD, move under D2-Q001; class by route (CONVENTIONS L247) gains a LinkedIn exception.
2. **As option 1, but `vendor_agreed` (24 months by default, L79) for organization posts on the amber route.** Consequences: two years of amber organization posts for trend and search; but the vendor buys data from the same platform whose terms cap organization social activity at six weeks (L192), so keeping it 24 months is the same exposure as keeping member comments past 48 hours, unless the vendor contract and counsel say LinkedIn's terms do not bind data bought from a vendor.
3. **`linkedin_48h` on every LinkedIn record, green and amber, with field-level rules in retention-purger** (organization fields six weeks, member fields 48 hours, profile fields 24 hours). Consequences: one class, but retention-purger and F8 need per-field purges that no other platform needs.
4. **Class by route as CONVENTIONS says:** `vendor_agreed` on every amber record and `linkedin_48h` on every green one, after legal confirms the vendor contract. Consequences: the simplest, but member comments bought from a vendor would be kept 24 months against LinkedIn's 48-hour rule for the same data, and green organization posts would be deleted at 48 hours unless the purger works per field.

**Why the recommendation.** LinkedIn's PRDs already say its terms follow the data, not the route; option 1 applies them the same way to members and to organizations, and avoids a field-level purge by not storing member fields in organization records. Option 2 keeps more history at a legal risk the user should weigh with counsel.

**Phase 2 records.** ADR "LinkedIn retention" (Applies to: F3, F8, every LinkedIn service, retention-purger, store-writer, poster-resolver). CONVENTIONS v1.1: `linkedin_org` added; L77 reworded (member content and organization content, every route, from `fetched_at`); L247 gains the exception that LinkedIn records take their class by content, not route; L192 cross-referenced. `DEFERRED.md`: counsel on "authenticated" (six weeks or six months), owner LI1.

### D2-Q056 · How long derived data lives: ten years, YouTube's 36 months, LinkedIn's 48 hours, and what YouTube's 30-day rule covers

- **Class:** user (a reading of the YouTube and LinkedIn terms, which sets what clients can see after three years)
- **Settles:** CF-106, AU-080, li-own-comments-fetcher §14 Q4, store-writer §14 Q3, yt-comments-fetcher §14 Q5, yt-text-purger §14 Q1, yt-text-purger §14 Q3, yt-video-details-fetcher §14 Q4
- **Blocks:** F3, F8 (TTLs), C6, C13, C14, C15, then YT1, YT4, YT5, YT7, LI2, VLI4

**Context.** CONVENTIONS keeps "Aggregates and derived scores: ten years, all classes" (L81) while `youtube_30d_text` keeps "derived metrics ... up to 36 months" (L76), from the YouTube fact sheet: "raw comment text no longer than 30 days (delete or refresh), derived metrics up to 36 months for 'Analytics & Reporting' clients, no aggregation across channels of different owners except under the carve-out" (L209). The PRDs apply it three ways: store-writer expires YouTube item rows at "created + 36 months" (`store-writer §5.3 L76`); yt-text-purger deletes items, `analysis` and hit rows when "the last `fetched_at` is older than 36 months" and leaves aggregates (`yt-text-purger §5.3 L118`, `§13 L259`); retention-purger never selects aggregates (`retention-purger §5.3 L68`; AU-080); the question is still open in `yt-comments-fetcher §14 Q5 L207` and `yt-video-details-fetcher §14 Q4 L218`. For LinkedIn, store-writer deletes `linkedin_48h` rows "with its `analysis` rows" (`store-writer §5.3 L77`, asked in `§14 Q3 L183`), the comment fetchers test the same (`li-own-comments-fetcher §13 L178`), while li-client-posts-poller keeps derived scores ten years (`li-client-posts-poller §7 L135`). And the 30-day clock covers "raw comment text" in CONVENTIONS, but yt-text-purger also runs it on video titles and descriptions (`yt-text-purger §3 L19`, `§5.3 L120`, open in `§14 Q1 L266`) and yt-channel-resolver on channel profiles (`yt-channel-resolver §6.2 L113`).

**Options**

1. **Item-level derived rows follow their item's class; aggregates keep ten years except per-channel YouTube rollups; the 30-day rule covers all stored YouTube text (recommended).** Analysis scores, hits and metrics time series of a YouTube item expire 36 months after the item's creation (store-writer's anchor); those of a LinkedIn member item go with it at 48 hours. Rollups keep ten years, except rollups at the level of one YouTube channel, which follow the 36 months (AU-080 option 3). Rollups across channels of different owners exist only under the carve-out the fact sheet names (CONVENTIONS L209); where they exist they keep ten years, which counsel confirms (that they are not "derived metrics" capped at 36 months). The 30-day refresh-or-delete clock applies to comment text, video titles and descriptions and channel profile text, as yt-text-purger and yt-channel-resolver assume. CONVENTIONS L76 and L81 are reworded accordingly. Refresh is part of the service, not an option clients buy: yt-text-purger refreshes the text of comments on client-watched sources within a share of the `comments` bucket set in the pilot and deletes, at 30 days, the text it cannot refresh in time (metrics stay), so no `yt_text_refresh` entitlement is added to `clients` in v1 (`yt-text-purger §14 Q3`). Consequences: one anchor (creation); YouTube trends older than three years survive only as cross-channel rollups; more refresh calls on the YouTube quota for titles and profiles (yt-text-purger already budgets them).
2. **Ten years for every derived row and aggregate, as CONVENTIONS L81 says;** the YouTube and LinkedIn limits apply only to raw text and identities. Consequences: the longest history for clients; per-item YouTube scores and metrics outlive the 36 months the fact sheet quotes, a risk at YouTube's audit ("audit at any time", L209).
3. **Per-class lifetimes for both item rows and aggregates:** every YouTube-derived aggregate also capped at 36 months. Consequences: the most conservative; YouTube disappears from ten-year trend lines after three years.

**Why the recommendation.** It follows the fact sheet's wording where it is specific (36 months, 30 days, no cross-owner aggregation), keeps the ten-year promise for everything else, and gives retention-purger one anchor per class.

**Phase 2 records.** ADR "Lifetimes of derived data" (Applies to: F3, F8, store-writer, aggregator, retention-purger, yt-text-purger, yt-channel-resolver, deletion-propagator). CONVENTIONS v1.1: L76 (what the 30-day clock covers, the 36-month anchor), L81 (the exceptions). `DEFERRED.md`: counsel's confirmation of the YouTube reading, including ten years for cross-owner rollups, before G3 for YouTube, owner YT7.

## Group 8 · Rules, series and platform specifics

### D2-Q057 · What a job does with a quota answer, when it reaches the DLQ, and who stretches amber rotation

- **Class:** technical
- **Settles:** CF-090, CF-091, AU-066, AU-113
- **Blocks:** F4 (the job wrapper), F5 (the scheduling kit), F6, C1, C10, C11, C12, then FB2, FB3, VFB2, VIG1, VIG2, TT1, VTT1, VTT2, VTT3, VTT4, VTT5, X5, X6, YT5, YT7, YT8, VLI3, VLI4, VTG1, VTG3, W1, W2, N8
- **Depends on:** D2-Q011 (the job envelope), D2-Q016 and D2-Q021 (credential state, 401 and 403), D2-Q017 (`quota_denied`), D2-Q018 (priorities and modes), D2-Q050 (flag off)

**Context.** The governor answers allow, wait-until or deny (`CONVENTIONS L85`); a deny (`flag_off`, `period_full`, `priority_gate` on monthly tags) lasts until the period resets or the mode changes (`quota-governor §5.3 L67`, `L70`, `L71`). The callers disagree:

- Deny (CF-090): five TikTok services and fb-backfill requeue with `attempt + 1` (`tt-hashtag-feed-poller §5.2 L56`, `fb-backfill §5.2 L55`), dead-lettering a whole tag within five tries once a month is full; others keep `next_poll_at` (`tt-client-videos-fetcher §5.2 L57`), finish `quota_denied` (`yt-comments-fetcher §5.2 L53`), wait (`tg-message-search §13 L147`), drop a step after 24 hours against README decision 2's held +24 h step (`li-post-comments-fetcher §5.1 L52`, `README L179`), end `capped` (`x-full-archive-search §5.1 L43`) or delete (`yt-text-purger §8 L193`). On wait-until two TikTok services sleep in the worker (`tt-keyword-search §5.2 L50`).
- DLQ (CF-091): "after 5 attempts" (`CONVENTIONS L100`), but five criteria test "the sixth failure" (for example `tg-channel-posts-poller §13 L186`); error 80001 is both a one-interval deferral and a counted retry (`fb-page-feed-poller §7 L138`, `§8 L145`).
- Provider failures (AU-066) never reach the governor's counters (`quota-governor §5.1 L37`), so after out-of-credits or a YouTube `quotaExceeded` other services still get `allow` (`ig-comments-fetcher §8 L131`, `yt-keyword-search §8 L139`).
- Stretch (AU-113): the governor publishes `stretch_factor` for "every amber poller's scheduler" (`quota-governor §4 L30`, `§5.1 L51`); the pollers say the governor stretches them (`fb-group-posts-poller §5.1 L46`); tg-channel-posts-poller wants a fixed order (`§5.1 L52`).

At stake: as written, a full budget fills the DLQs with alerts while nothing slows down.

**Options**

1. **Quota answers are never failures: one rule in the SDK wrapper and scheduling kit (recommended).**
   - `deny`: no call; the job ends `quota_denied` (D2-Q017), never an attempt or DLQ entry (`flag_off` ends `skipped_flag_off`, D2-Q050), and its producer retries: rotation sets the next due time from the denied run's start (the cursor has not moved); comment-decay-scheduler holds the step until the tag's mode admits it, on every route's tag, merging it with the next step as it merges hot extras (`§5.1 L62`), so the +24 h step is never dropped (li-post-comments-fetcher's 24-hour drop goes); a backfill ends `capped` with `capped_reason = budget` (`backfill-orchestrator §5.3 L81`); yt-text-purger deletes, as the 30-day rule requires; poster-resolver keeps the candidate `pending`, as for a degraded resolver (`poster-resolver §8 L108`).
   - `wait-until`: requeue for that time, `attempt` unchanged; no worker sleeps. A job may carry `must_finish_by` (yt-text-purger's field, `§5.3 L102`): the next due time for rotation, the next step's for comment steps, the deadline for backfills; a later `wait_until` counts as a deny, as x-full-archive-search and yt-text-purger already rule.
   - Attempts count provider failures only (429 and vendor rate limits after backoff, 5xx, timeouts), from 1; the fifth failed attempt goes to `dlq.<service>` with an alert; the five criteria are corrected.
   - 80001, a throttle on one Page: a wait (until Meta's estimated time to regain access, otherwise one rotation interval, `fb-page-feed-poller §7 L138`), never an attempt, counted per Page for the alert (`quota-governor §5.3 L80`).
   - `report` carries an error class: `quota_exceeded` sets `youtube_data_api` to `exhausted` until the provider's reset, `out_of_credits` sets the vendor tag to `exhausted` until an audited ops raise (`quota-governor §5.1 L49`); a 403 whose reason is quota counts as `quota_exceeded`; only an authorisation 401 or 403 goes to credential and health state, not the governor (D2-Q016, D2-Q021).
   - Stretch, amber tags only (D2-Q018): the F5 scheduling kit applies `min(tier_interval × stretch_factor, 24 h)` with the factor the governor publishes in `budgets`, so no poller code reads it. Telegram's order follows: backfill (priority 5) stops at 80%, and Tier 2 (6 h) reaches the 24-hour ceiling at factor 4 while Tier 1 (60 min) is at 4 hours.

   Consequences: one implementation and test set in F4 and F5; D2-Q011's envelope gains the optional `must_finish_by`; six approved PRDs move under D2-Q001 (fb-backfill, fb-page-feed-poller, tt-hashtag-feed-poller, tt-keyword-search, tg-message-search, web-search-perplexity) among about thirty aligned lines; a long budget pause costs freshness and backfill depth, never DLQ noise.

2. **As option 1, but the governor stretches by answering `wait_until` at the stretched due time** (AU-113 option 2). Consequences: one enforcement point and the pollers' wording stands, but the governor needs each job's interval and last start (its request has neither, `quota-governor §5.1 L37`), each stretched poll costs a requeue and a second call, and rotation-lag alerts fire for merely stretched sources.
3. **`deny` parks the job until the period or mode changes** (CF-090 option 2). Consequences: steps are held with no scheduler change, but parked jobs pile up for weeks on monthly tags and are released in one burst at the reset.
4. **Per-route rules as written** (CF-090 option 3), the sixth failure kept by rewording `CONVENTIONS L100`, 80001 a counted retry, a counter-only governor. Consequences: the least editing; a dozen behaviours to test; services keep calling after `quotaExceeded`.

**Why the recommendation.** A budget answer is not a failure, so it should never burn retries or fill a DLQ; leaving the retry to the producer keeps each schedule's own rule (held steps, capped backfills, YouTube deletion). The stretch is applied where intervals are computed, as the governor's PRD designs it, at no extra call.

**Phase 2 records.** ADR "Quota answers, attempts and the DLQ" (Applies to: listening-sdk, quota-governor, comment-decay-scheduler, backfill-orchestrator, every service with a `budget_tag`). CONVENTIONS v1.1: L85 (the handling of each answer, `must_finish_by`, error classes), L100 (five attempts; quota answers and 80001 are not attempts), L51 (the stretch formula, applied by the SDK scheduling kit).

### D2-Q058 · Engagement-count refreshes on X, LinkedIn, Telegram and Facebook groups

- **Class:** user (a cost choice: on X each refresh is a paid post read)
- **Settles:** CF-082, AU-032, comment-decay-scheduler §14 Q6, fb-group-posts-poller §14 Q6, li-company-posts-poller §14 Q3, tg-channel-posts-poller §14 Q5
- **Blocks:** C11, VTG3, LI1, VLI3, VFB2, X1, X3, X4

**Context.** CONVENTIONS refreshes likes, shares, views and comment counts at +24 h and +7 d on every route (L65). The README records counts on X, LinkedIn and Telegram at first sight only, leaving refreshes as an open question (`README L25`); comment-decay-scheduler does the same and asks (`comment-decay-scheduler §5.1 L68`, `§14 Q6 L207`). tg-channel-posts-poller expects a +24 h views refresh for tier-1 posts on a `metrics` job that the scheduler never emits, and asks whether it is worth its cost (`tg-channel-posts-poller §5.1 L56`, `§14 Q5 L195`; AU-032); li-company-posts-poller leaves it open (`li-company-posts-poller §5.4 L92`, `§14 Q3 L186`). Prices from the fact sheets: X USD 0.005 per post read (about 0.6 million X posts a month, CONVENTIONS L3), Apify Telegram Actors about USD 2,900 to 7,200 a month at 2.4 million items, harvestapi about USD 225 to 300 a month at 0.15 million LinkedIn items (L87, L93, L94).

**Options**

1. **First-sight counts only on X, LinkedIn and Telegram in v1 (recommended).** CONVENTIONS L65 is amended to name the routes that refresh (Facebook Pages, Instagram, TikTok, YouTube) and those that record counts at first sight (X, LinkedIn, Telegram, news, as `comment-decay-scheduler §5.1 L68` already says, and amber Facebook groups, whose post counts no service refreshes either, `fb-group-posts-poller §14 Q6`); tg-channel-posts-poller drops its `metrics` job. Consequences: no extra spend; trend charts on these three platforms show counts as first seen; the question can come back after the pilot with measured costs.
2. **A Telegram tier-1 +24 h views refresh only**, as tg-channel-posts-poller describes, first sight elsewhere. Consequences: one more lane in comment-decay-scheduler; Apify charges per item re-read.
3. **+24 h and +7 d refreshes on every route, as CONVENTIONS says.** Consequences: about two extra paid reads per X post (at 0.6 million posts a month, roughly USD 6,000 a month more at list price) and two extra vendor reads per LinkedIn and Telegram item.

**Why the recommendation.** It matches the README and the scheduler as written and avoids a cost that is large on X before the pilot shows clients need it.

**Phase 2 records.** ADR "Count refreshes on X, LinkedIn and Telegram" (Applies to: comment-decay-scheduler, tg-channel-posts-poller, li-company-posts-poller, fb-group-posts-poller, the X pollers). CONVENTIONS v1.1, L65. `DEFERRED.md`: revisit after G2 with measured costs, owner C11.

### D2-Q059 · Coverage bought by default: history on add and extra comment fetches

- **Class:** user (each default spends quota or vendor money before any client asks)
- **Settles:** AU-037, AU-040, AU-044, AU-045, AU-094, AU-098, AU-103, fb-backfill §14 Q1, ig-comments-fetcher §14 Q3, li-post-comments-fetcher §14 Q4, tt-video-comments-fetcher §14 Q3, x-full-archive-search §14 Q5, x-replies-fetcher §14 Q7
- **Blocks:** F2, then C4, C10, C11, X1, X5, X6, N2, N3, N4, N6, N8, W3, W5, IG2, IG3, VIG2, LI2, LI3, VLI1, VLI4, VTT5
- **Depends on:** D2-Q018 (priorities), D2-Q052 (amber consent)

**Context.** CONVENTIONS backfills 90 days (L53) and fetches comments on a series, nothing after day 30 unless a client asks (L56, L61). The PRDs disagree:

- Backfilled posts: one `once` fetch each (`comment-decay-scheduler §5.1 L66`); none beyond day 30, "Abdullah to decide" (`fb-backfill §5.1 L47`, `§14 Q1 L170`); one job per post of the last 30 days from backfill-orchestrator (`li-own-comments-fetcher §5.1 L52`, `li-post-comments-fetcher §5.1 L54`) (AU-045).
- X: keyword rules get a backfill that x-full-archive-search refuses, and a `keyword_history` job on a stale cursor that it takes only on a client request (`backfill-orchestrator §5.3 L72`, `x-full-archive-search §13 L183`, `x-recent-search §5.1 L45`, `x-full-archive-search §5.1 L39`) (AU-094); replies after day 7 have no emitter (`comment-decay-scheduler §5.1 L53`) (AU-040).
- News: backfill goes to news-feed-poller, which takes none, and the remainder to web-commoncrawl-scanner, which lists hosts, not articles (`backfill-orchestrator §5.3 L78`, `news-sitemap-poller §5.1 L51`, `web-commoncrawl-scanner §5.1 L44`) (AU-044, AU-103).
- Series: opened for every post with a comment route (`comment-decay-scheduler §2 L13`), while fetchers expect gates on `comments_count`, Disqus, keyword hits and individuals (`ig-comments-fetcher §13 L164`, `news-article-extractor §5.1 L47`, `tt-video-comments-fetcher §5.1 L50`) (AU-037); LinkedIn keyword finds by default (`li-post-search §5.1 L50`) or "only if the budget allows" (`li-post-comments-fetcher §5.1 L40`) (AU-098); none on X posts about protests, and terms screened before X history (`x-replies-fetcher §14 Q7 L205`, `x-full-archive-search §14 Q4 L192`, `CONVENTIONS L188`).

At stake: what each new source and found post costs before a client asks.

**Options**

1. **Green history and comments by default, none on amber; older X history and replies on request (recommended).** Each default can be changed alone:
   - (a) Every backfilled post on a green comment route gets one `once` fetch at priority 5, whatever its age (fb-backfill Q1: yes; LinkedIn through the scheduler, not the orchestrator); none on amber in v1. Cost: about 150 comment calls per added Facebook Page (90 days at 600 ranked posts a year, L86), paid in quota (`fb-page-feed-poller §7 L141`); 1 YouTube unit a page (L88); on X USD 0.005 a reply, only the last 7 days visible (`x-replies-fetcher §5.1 L49`).
   - (b) X keyword rules: 7 days from the first recent-search pass (`x-recent-search §5.1 L49`); older history only on a client's request (`keyword_history` from backfill-orchestrator), never on a stale cursor (D2-Q064).
   - (c) News: backfill only through news-sitemap-poller, from regular sitemaps; a site whose sitemaps reach less than 90 days, or that has none, ends `capped`; no Common Crawl URL lister; news pollers start at `added`. Up to about 2,250 article fetches per site (25 a day for 90 days, L212), no per-request price.
   - (d) No X replies for posts older than 7 days in v1; x-full-archive-search drops `replies`.
   - (e) LinkedIn keyword finds get no series unless a client asks (li-post-comments-fetcher Q4).
   - (f) A series opens for posts of registered sources and client-owned properties (amber ones per D2-Q052 and only with a first-sight `comments_count` above zero where given), for keyword finds on green routes and for Disqus sites' articles; never for an X post containing a term on the blocked-terms list x-filtered-stream screens rules with (`x-filtered-stream §5.2 L52`), the F3 table `screened_terms` of D2-Q069, marked by normalize-item on `items.normalized` (x-replies-fetcher Q7). The same screen checks every X term, live or history; refusals go to `review_queue` (`x_terms_screen`) for the account manager's recorded decision; the list is the user's (x-full-archive-search Q4). Budget order unchanged (`comment-decay-scheduler §5.1 L62`).

   Consequences: the scheduler reads `clients`, `news_sites` and the new marker (F2); backfill-orchestrator sends news to news-sitemap-poller only and X keyword rules nowhere; fb-backfill, x-recent-search, li-post-search and news-site-resolver (approved) move under D2-Q001; unless they ask, clients get 7 days of X history and conversation and no comments on backfilled vendor posts.

2. **Comment fetches on amber too:** a `once` fetch per backfilled amber post and series for amber keyword finds with a client hit, within each source's vendor cap. Consequences: vendor-route comment history; at one page per fetch, USD 0.50 to 1.00 (TikHub), 0.99 to 1.88 (ScrapeCreators) or 1.99 to 4.83 (SociaVault) per 1,000 backfilled posts (L91, L92), LinkedIn USD 1.50 to 2.00 per 1,000 items (USD 225 to 300 a month for 0.15 million, L94); a five-step TikTok series USD 0.0025 to 0.0050 a video (`comment-decay-scheduler §7 L153`).
3. **More history on X and news:** automatic `keyword_history` for new X rules, X replies to day 30, a Common Crawl URL lister (AU-103 option 2). Consequences: fuller history; if keyword rules found all 0.6 million X posts a month (L3), 90 days for the whole set would be about 1.8 million post reads, USD 9,000 and 60% of one cycle's 3,000,000-read cap (L87); old replies USD 0.005 each; a new mode in web-commoncrawl-scanner.

**Open questions this also answers.** A client's X `keyword_history` read is history only: its items are stored and matched for that client (keyword-matcher writes the hits, D2-Q031) but feed no discovery or backfill, recognised by `job_kind = backfill` (`x-full-archive-search §14 Q5`). The sensitive-events mark of (f) is set by normalize-item from D2-Q069's screened-terms list, as a boolean `sensitive_event` on `items.normalized` (`x-replies-fetcher §14 Q7`).

**Why the recommendation.** Green history costs quota, not money, and gives every new source a past; vendor and X reads cost money per item, so they wait for client requests until the pilot shows demand.

**Phase 2 records.** ADR "Coverage bought by default" (Applies to: backfill-orchestrator, comment-decay-scheduler, normalize-item, the X, news and comment services). CONVENTIONS v1.1: L53 (backfill per source type), L61 (the `once` fetch), the addendum L255 to L271 (which posts open a series). `DEFERRED.md`: amber comment history and X replies to day 30, after G2 with pilot costs (C11, X5).

### D2-Q060 · When comment and metrics steps fall due, and how reply threads are fetched

- **Class:** technical
- **Settles:** AU-030, AU-035, ig-own-comments-fetcher §14 Q2, tt-video-stats-refresher §14 Q3, yt-video-details-fetcher §14 Q3
- **Blocks:** F2 (the `replies` job), F3 (`comment_series`), C10, C11, then FB3, FB4, VFB3, IG6, VTT5, VTT6, YT4, YT5, YT6
- **Depends on:** D2-Q005 (the backfill marker), D2-Q011 (`post_ref`), D2-Q034 (metrics jobs), D2-Q046 (`comment_series`), D2-Q059 (which backfilled posts get a fetch)

**Context.**

- Anchor (AU-030): comment-decay-scheduler counts steps "from the post's first-seen time ... not its creation time" (`§5.1 L60`), as CONVENTIONS does (L56), and gives backfilled posts, or posts first seen when older than the profile's last step, one `once` fetch (`§5.1 L66`). The approved fb-backfill aligns the comment series to `created_time` (`fb-backfill §5.1 L47`); fb-reactions-fetcher and yt-video-details-fetcher set metrics due at creation plus 24 hours or 7 days (`fb-reactions-fetcher §5.1 L41`, `yt-video-details-fetcher §5.1 L45`); ig-own-comments-fetcher proposes the media's timestamp when first sight lags by over an hour (`§14 Q2 L193`); tt-video-stats-refresher counts from first sight but expects no metrics jobs after day 7 (`§5.1 L44`, `L48`).
- Replies (AU-035): comment-decay-scheduler sends one `replies` job per post with `thread_ids` (`§5.3 L94`), though its table says per comment (`§5.1 L52`); three fetchers read one thread in `post_ref` (`fb-group-comments-fetcher §5.1 L40`, `tt-video-comments-fetcher §5.1 L41`, `yt-replies-fetcher §5.1 L38`); yt-replies-fetcher runs a per-thread series (`§5.1 L40`) that `comment_series`, one row per post and lane (`comment-decay-scheduler §6.3 L147`), cannot hold; ig-own-comments-fetcher expects `replies` jobs (`§5.1 L51`) where the profile says "no job" (`comment-decay-scheduler §5.1 L50`).

At stake: a late or backfilled post is scheduled differently on each side, metrics land at different post ages, and reply jobs do not parse.

**Options**

1. **Comments from first sight, metrics from creation, one `replies` job per post (recommended).**
   - Comment steps count from first sight, so a post found late still gets its whole series; one first seen after its profile's last step gets the `once` fetch; ig-own-comments-fetcher's threshold is not adopted.
   - Backfilled posts (`job_kind = backfill`) get no series: on green comment routes one `once` fetch at priority 5, whatever the post's age, and on amber routes none in v1 (D2-Q059 a); fb-backfill's alignment sentence goes (an approved PRD moves under D2-Q001).
   - Metrics count from the platform's creation time, and steps already past at first sight are not emitted (D2-Q034); tt-video-stats-refresher moves to that clock (its §14 Q3: yes).
   - Replies: one `replies` job per post, `post_ref` carrying `thread_ids` (the parent comments' platform ids, capped by a setting tuned in the pilot); the fetcher loops over them and reports per thread; further candidates wait for the next job, so a post keeps one job in flight (`comment-decay-scheduler §5.1 L62`).
   - Reply jobs only on the addendum's profiles: `fb_group` (vendor comment ids), `tt` (more than 10 replies), `yt` (more than 5, to yt-replies-fetcher); ig-own-comments-fetcher pages nested replies inside its `comments` job and drops kind `replies`.
   - No per-thread series: a thread is a candidate again whenever a comment step reports more replies than are stored (`comment-decay-scheduler §5.3 L94`, `yt-comments-fetcher §5.2 L60`), so growing threads are re-read at the post's steps; yt-replies-fetcher keeps only its skip rule (`§5.1 L42`).

   Consequences: `comment_series` keeps one row per post and lane (D2-Q046); one reply-job shape, so three fetchers change their trigger lines; fb-backfill, tt-video-stats-refresher and yt-replies-fetcher rewrite their series text.

2. **Creation time for both lanes** (AU-030 option 2). Consequences: one clock, but a post found three days late gets its first comment fetch at +3 d at best.
3. **First sight unless it lags creation by a threshold** (AU-030 option 4). Consequences: two clocks and a threshold to tune, for a case the first fetch already catches up.
4. **One `replies` job per thread, with a YouTube replies lane** (AU-035 options 2 and 3). Consequences: the fetchers keep their trigger lines; the scheduler loses its one-job-in-flight rule and needs per-thread rows.

**Why the recommendation.** Comment coverage is about not missing a conversation, so its clock starts at first sight; engagement counts are compared across posts, so they are read at the same post age. One job per post keeps the scheduler's one-in-flight rule, and re-reading only grown threads does the per-thread series' work for less quota.

**Phase 2 records.** ADR "Series anchors and reply jobs" (Applies to: comment-decay-scheduler, the comment, reply and metrics services, backfill-orchestrator). CONVENTIONS v1.1: L56 (first sight; backfilled posts one `once` fetch), L65 (metrics from creation), L60 and the addendum's Replies column (one job per post with `thread_ids`).

### D2-Q061 · The Disqus comment series

- **Class:** technical
- **Settles:** CF-108, AU-041, AU-107
- **Blocks:** C11, N2, N8

**Context.** Four documents give Disqus sites the short series +6 h, +24 h, +3 d (`CONVENTIONS L269`, `comment-decay-scheduler §5.1 L58`, `news-comments-fetcher §5.1 L43`, `news-article-extractor §5.1 L47`); news-site-resolver, an approved PRD, promises the full decay series (+1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30) when it onboards a site (`news-site-resolver §5.1 L41`). AU-041 and AU-107 put the same question from the two audit passes.

**Options**

1. **The short series, as CONVENTIONS, the scheduler and the fetcher say; news-site-resolver's sentence corrected (recommended).** Disqus threads get +6 h, +24 h and +3 d, threaded in the same call (`CONVENTIONS L269`). The general rules still apply on this row: the extension rule (CONVENTIONS L271) extends a thread that still adds 20% or more at its last scheduled fetch, +3 d, every 2 days to day 30, so a thread that keeps growing is followed; early stop is armed as D2-Q019 says. news-site-resolver promises the short series when it onboards a Disqus site. Consequences: no change to the `news_disqus` budget estimate; the scheduler profile stays as written; an approved PRD gets a one-line edit under D2-Q001.
2. **The full decay series for Disqus.** Consequences: CONVENTIONS, the scheduler profile and news-comments-fetcher change, and `news_disqus` is re-estimated for five more steps per article on every thread, steps the extension rule already adds where a thread is still growing.

**Why the recommendation.** Three of the four documents, including the two PRDs that own the code, agree; the extension rule already gives growing threads the later steps, so the full series would spend Disqus calls on every thread to catch what extension already catches on the threads that need it.

**Phase 2 records.** ADR "Disqus series" (Applies to: comment-decay-scheduler, news-comments-fetcher, news-site-resolver). No CONVENTIONS change (L269 and L271 stand); news-site-resolver §5.1 L41 corrected, citing the ADR.

### D2-Q062 · When a missing post or comment becomes a deletion

- **Class:** technical
- **Settles:** CF-113, AU-085, fb-group-comments-fetcher §14 Q5, yt-comments-fetcher §14 Q3, yt-replies-fetcher §14 Q5
- **Blocks:** F4 (the shared rule in the SDK), C13, then FB4, FB5, VFB3, YT4, YT5, VTT5, VTT6, X6, VIG2, IG3, IG6, LI1, LI2, VLI3
- **Depends on:** D2-Q035 (the `deletions` message)

**Context.** CONVENTIONS turns missing comments into `deletions` with reason `platform_sync` "when the API is complete" (L63) and has no rule for posts. The PRDs differ (CF-113): fb-reactions-fetcher deletes a post on one "not found" (`fb-reactions-fetcher §8 L144`) while the two Facebook comment fetchers never delete a post on one error (`fb-post-comments-fetcher §8 L143`, `fb-group-comments-fetcher §8 L145`); yt-video-details-fetcher and tt-video-stats-refresher confirm with a second request (`yt-video-details-fetcher §5.2 L62`, `tt-video-stats-refresher §5.2 L60`); tt-video-comments-fetcher waits for two consecutive full reads (`§8 L138`); X replies and Instagram vendor comments never delete on absence (`x-replies-fetcher §8 L154`, `ig-comments-fetcher §13 L171`). A post that a comment fetcher finds deleted is handed to a poller that cannot detect it on Instagram, or on LinkedIn after day 7 (AU-085). deletion-propagator acts on the first message it receives, so the strictest reader decides.

**Options**

1. **One rule in the SDK: absence becomes a deletion only after a confirmed second miss, or on a platform deletion signal; and routes whose reads are not complete listings never delete on absence (recommended).** A fetcher that misses an item records a suspicion; the next read (or one confirming request within the job) that misses it again emits `deletions` with `platform_sync`. A platform signal (a webhook `remove`, X compliance, a 404 on the item's own endpoint where the platform documents it as deleted) counts as confirmation. Routes listed in CONVENTIONS as "no deletion on absence": X replies (x-compliance-sync is the deletion source), Instagram vendor comments (about 15 visible comments), li-company-posts-poller's vendor posts ("an absent post cannot be told from a post the Actor did not return", `li-company-posts-poller §5.4 L92`), keyword and hashtag searches. li-client-posts-poller's daily reconciliation reads back over the class's retention period, six weeks under D2-Q055, instead of 7 days (`li-client-posts-poller §5.1 L48`, `§13 L179`; AU-085 option 1), so a green post deleted after its comment series is still mirrored. A comment fetcher that finds the post itself gone emits the post's deletion under the same rule rather than handing it to a poller. Consequences: one implementation and one test in F4; fb-reactions-fetcher, an approved PRD, is aligned under D2-Q001; a deleted post stays visible for one more read cycle; the LinkedIn reconciliation reads up to six weeks of posts a day, a quota cost rather than money.
2. **CONVENTIONS extended to posts: one complete read that misses the item is enough.** Consequences: faster removal, but a transient error or a partial page on one service erases a post others still see.
3. **Per route as written**, with fb-reactions-fetcher aligned to the other Facebook readers and the never-delete routes recorded. Consequences: the least change, but five behaviours to build and test.

**Open questions this also answers.** Removed YouTube replies are detected by yt-replies-fetcher's own thread read while the thread is a reply candidate, and by yt-comments-fetcher's thread read (a complete listing at 5 replies or fewer) after (`yt-replies-fetcher §14 Q5`).

**Why the recommendation.** Deletion is irreversible downstream (deletion-propagator removes derived rows and recomputes aggregates), so one confirmation costs little; listing the routes where absence means nothing removes the false deletions D1 found.

**Phase 2 records.** ADR "Deletion on absence" (Applies to: every fetcher that refetches, deletion-propagator, listening-sdk). CONVENTIONS v1.1, L63 extended to posts with the confirmation rule, the list of routes that never delete on absence and li-client-posts-poller's reconciliation window.

### D2-Q063 · Which X keyword rules go on the filtered stream

- **Class:** technical
- **Settles:** CF-115, x-filtered-stream §14 Q4
- **Blocks:** X1, X4

**Context.** The filtered stream holds up to 1,000 rules (`CONVENTIONS L87`). x-filtered-stream fills them in order: "client brand keyword sets (one rule each, priority 1), tier-1 accounts (priority 1), tier-2 (2), tier-3 (3)" (`x-filtered-stream §5.1 L40`, `§13 L191`); x-recent-search says "Tier-1 keyword rules also run as stream rules on x-filtered-stream; the 15-minute search stays on as the safety net" (`x-recent-search §5.1 L47`), without saying whether other keyword rules are streamed. How many rules keyword coverage takes decides how many accounts get real-time coverage, and how cost splits between stream and search (both are paid per post read).

**Options**

1. **Streamed rules chosen by priority within a fixed share (recommended).** Tier-1 keyword rules come first, up to a configured share of the capacity left after the headroom reserve (`x-filtered-stream §5.1 L40`), set in the pilot; tier-1 accounts fill the rest, then tier 2 and 3; x-recent-search keeps searching every keyword rule, the tier-1 ones every 15 minutes as the safety net. Both PRDs state the same order and the share (x-recent-search, an approved PRD, moves under D2-Q001). Consequences: keyword coverage can never crowd out tier-1 accounts; the share is a setting the pilot tunes; client brand keyword sets below tier 1 are not streamed and rely on 60-minute search.
2. **Every client brand keyword set on the stream**, as x-filtered-stream says. Consequences: accounts get only the rules keywords leave over; x-recent-search's cost split is rewritten.
3. **Only tier-1 keyword rules on the stream**, the narrow reading of x-recent-search. Consequences: lower stream volume; brand sets below tier 1 rely on 60-minute search.

**Why the recommendation.** It honours both PRDs' order and puts the trade-off in one number that can change without a contract change.

**Phase 2 records.** ADR "X stream rule allocation" (Applies to: x-filtered-stream, x-recent-search). No CONVENTIONS change beyond a note under the X fact sheet.

### D2-Q064 · Filling X stream gaps, X history jobs, and the key of an X reply

- **Class:** technical
- **Settles:** CF-084, AU-093, AU-096, x-filtered-stream §14 Q3, x-full-archive-search §14 Q2
- **Blocks:** F2, then F4, C4, C10, X1, X3, X4, X5, X6
- **Depends on:** D2-Q004 (the gap job's key), D2-Q007 (X keys), D2-Q010 (identities), D2-Q011 (kinds), D2-Q017 (`jobs.completed`), D2-Q020 (backfill job fields), D2-Q059 (X history and older replies)

**Context.** After a stream drop, x-filtered-stream emits one `reconciliation` job per affected rule on `jobs.x-recent-search` with `query`, `source_ids`, `client_ids`, `window_start` and `window_end`, sends parts older than recent search's 7 days to x-full-archive-search, and closes the gap when `jobs.completed` arrives for all its jobs (`x-filtered-stream §5.2 L70`, `L71`, `§14 Q3 L207`). The approved x-recent-search claims "gap backfill for x-filtered-stream" (`x-recent-search §3 L22`) but reads only `reason` = rotation | first_run | gap_backfill | ops_force, builds queries from `keywords` and writes no completion (`x-recent-search §5.2 L53`, `§6.2 L98`); account rules are `from:` buckets of several accounts (`x-filtered-stream §5.1 L40`); x-full-archive-search has no gap kind (`§5.1 L39`). `keyword_history` comes from x-recent-search on a cursor older than 7 days (`§5.1 L45`, `§13 L188`) and from backfill-orchestrator on a client request (`x-recent-search §5.1 L49`), whose route table has no such kind (`backfill-orchestrator §5.3 L72`). A reply is `x:comment:<id>` in x-replies-fetcher (`§6.2 L115`) and `x:post:<id>` in the other readers (`normalize-item §5.3 L68`); x-full-archive-search's `replies` jobs have no producer and no agreed hand-back (`§6.2 L128`, `§14 Q2 L190`). At stake: every gap job is rejected and no gap closes, and one reply becomes two items.

**Options**

1. **x-recent-search fills recent gaps, history only on a client's request, one key per tweet (recommended).**
   - Gap job: `kind = reconciliation` (no `reason`, D2-Q011) with the kind fields `query`, `window_start`, `window_end`, `source_ids` and `client_ids`, partitioned as D2-Q004 decides. x-recent-search reads exactly that window with the API's start and end times, never moves the rule's `since_id`, files each post under its author's source when the author is in `source_ids` (a `from:` bucket) and under the keyword rule otherwise (the registry lookup of `§5.2 L57`), and is reported by the job wrapper (D2-Q017), so the gap closes. `reason` goes with its values `first_run` and `gap_backfill` (D2-Q011).
   - Gap parts older than 7 days are reported with `gap_unfilled` and their window, not filled, in v1; x-full-archive-search gets no gap kind.
   - `keyword_history` stays a kind of its own, since a client's history read runs at priority 1 and `backfill` is always 5 (D2-Q018). Only backfill-orchestrator emits it, on a client request through the admin API (D2-Q012), with `run_id`, `window_start`, `window_end`, `cap` and `reason = client` (D2-Q020), which answers `x-full-archive-search §14 Q1`. x-recent-search stops emitting it: a cursor older than 7 days resumes at the window's edge and reports the uncovered span (status `partial`). New keyword rules get no automatic history (D2-Q059 b).
   - Every X post, reply or not, is `x:post:<id>` with its parent link (D2-Q007); x-replies-fetcher adopts it (its `ledger_key` becomes the same value), and identities are replaced at the edge on every X reader (D2-Q010), which answers `x-replies-fetcher §14 Q5 L203`.
   - x-full-archive-search's `replies` kind is removed until D2-Q059 (d) grants older replies; the hand-back is designed then, its boundary a field of x-replies-fetcher's reply index (`§6.3 L138`).

   Consequences: the approved x-recent-search gains a window path and loses `reason` and its stale-cursor trigger (it moves under D2-Q001); X1, X4 and X5 share one job type; a stream outage longer than 7 days needs an ops decision.

2. **x-filtered-stream re-reads its own gaps** through the SDK's recent-search client (CF-084 option 3, AU-093 option 2). Consequences: no cross-service job, but a second searcher and a second writer of the same posts.
3. **Gaps go to the services that own the cursors** (AU-093 option 3): account buckets become `reconciliation` polls on x-user-timeline-poller, keyword gaps wait for x-recent-search's next run. Consequences: no new query path; slower filling, and reading back to each cursor can pay again for posts the stream delivered on an earlier UTC day.
4. **`x:comment:<id>` for every reply**, through one SDK X mapper (AU-096 option 1). Consequences: x-replies-fetcher keeps its key, but the approved normalize-item mapper and the other readers change, and each reader must classify a tweet before keying it.

**Why the recommendation.** It uses the job x-filtered-stream already emits and the role the approved x-recent-search already claims, pays only for the gap itself, gives `keyword_history` one emitter, and keeps one tweet one item however it was found.

**Phase 2 records.** ADR "X gaps, history and replies" (Applies to: x-filtered-stream, x-recent-search, x-full-archive-search, x-replies-fetcher, backfill-orchestrator, normalize-item). CONVENTIONS v1.1: L277 (`keyword_history`; the `reconciliation` window fields). `DEFERRED.md`: gap parts older than 7 days and the replies hand-back, owner X5.

### D2-Q065 · YouTube: details jobs, partial records, the uploads playlist id, channels without push, and the text refresh

- **Class:** technical
- **Settles:** CF-083, AU-027, AU-051, AU-100, AU-101, AU-102, yt-text-purger §14 Q2, yt-uploads-reconciler §14 Q3, yt-video-details-fetcher §14 Q2
- **Blocks:** F2, F3, then C1, C4, C6, C7, C9, C11, YT1, YT2, YT3, YT4, YT5, YT6, YT7, YT8, YT9
- **Depends on:** D2-Q007 and D2-Q008 (key and kind), D2-Q012 (producer rows), D2-Q013 (registry columns), D2-Q018 (priority), D2-Q049 (push coverage), D2-Q056 (who gets the refresh)

**Context.**

- Details jobs (CF-083, AU-101): yt-video-details-fetcher reads `post_ref` as one id and marks backfill ids `series_step = backfill` (`§6.1 L86`, `§5.1 L44`); yt-pubsub-receiver sends one id (`§6.2 L127`), yt-uploads-reconciler lists of up to 50 with `origin_kind` (`§6.2 L133`), yt-keyword-search every id of a run in one message (`§5.2 L59`), yt-web-search-bridge lists with `origin = web_bridge` on a `list` bucket that does not exist (`§6.2 L126`, `§7 L137`; `CONVENTIONS L279`).
- Partial records (AU-051): three PRDs expect normalize-item to hold `partial: true` records until the details record (`yt-pubsub-receiver §6.2 L124`, `yt-keyword-search §6.2 L123`, `yt-video-details-fetcher §4 L33`); normalize-item has no hold and maps only the three fetchers (`§5.2 L52`, `§5.3 L71`).
- Playlist id (AU-027): yt-uploads-reconciler selects only channels with a stored uploads playlist id (`§5.1 L43`); yt-channel-resolver returns it and says registry-writer stores it (`yt-channel-resolver §6.2 L126`, `§6.3 L138`); no column exists (`registry-writer §5.3 L68`), so no channel is reconciled.
- Cadence (AU-100): an unsubscribed channel keeps its reach-tier cadence, dormant weekly (`yt-pubsub-receiver §5.1 L40`), against one daily read for every channel (`yt-uploads-reconciler §5.1 L45`, `§14 Q3 L200`).
- Refresh (AU-102): no fetcher accepts yt-text-purger's `refresh` jobs (`§5.3 L96` to `L102`), and normalize-item turns an unchanged re-read into metrics only (`§5.2 L52`), so the 30-day clock never resets.

At stake: as written, YouTube reconciles no channel, parks or double-publishes every video, and spends refresh quota that resets nothing.

**Options**

1. **One video per job, partial versions, a registry column, tier cadence when push fails, refresh as a version (recommended).**
   - a) Every job on `jobs.yt-video-details-fetcher` carries one video in `post_ref` (D2-Q011); producers split their lists, and only the consumer's collector batches (`yt-video-details-fetcher §5.1 L48`), 50 ids for 1 unit (`CONVENTIONS L205`). `first_sight` (a producer row for the four finders, D2-Q012) carries `origin_kind`, the kind of the job that found the id; the SDK derives priority from it (`backfill` 5, otherwise 1, D2-Q018), so `series_step = backfill` and `origin` go. The bridge's `list` bucket is `ingest`.
   - b) A finder's record is version 1, keyed `youtube:post:<id>` with kind `post` (D2-Q007, D2-Q008) and `partial: true` in its `context` (D2-Q005), through a normalize-item mapper per finder; the details record is the next version of the same key, published even when the content hash is equal because the stored version is partial. No hold: a stalled details fetcher leaves partial videos visible, not missing.
   - c) `sources` gains `platform_meta` (jsonb, typed per platform in F2; YouTube: `uploads_playlist_id`), written only by registry-writer from the decision carrying yt-channel-resolver's profile; copied, never derived (`yt-channel-resolver §5.2 L62`).
   - d) A channel whose own subscription failed loses push coverage (yt-pubsub-receiver's decision, D2-Q013, D2-Q049) and is read at its reach-tier cadence (`CONVENTIONS L45` to `L47`), with `subscription_failed` to ops (`yt-pubsub-receiver §8 L145`); a hub-wide failure moves no channel, so all stay daily while ops decides (`§8 L146`); dormant channels are read weekly (`CONVENTIONS L49`). Quota: an hourly read costs 24 `playlistItems.list` units a channel a day against 1 (`CONVENTIONS L204`); at the 99% verified-lease target (`yt-pubsub-receiver §2 L13`), even an all-Tier-1 worst case adds at most 0.23 units per registered channel a day (1% of channel-days × 23), under a quarter of the 1 unit per channel that daily reconciliation already costs.
   - e) yt-text-purger is the named producer of `refresh` on the three YouTube queues (D2-Q012), with `post_ref` (and its `thread_ids`), `run_id`, `must_finish_by` and `refresh_for_client_ids`, one video per job. The fetcher re-reads what is listed and writes every returned item, changed or not, with `job_kind = refresh`; normalize-item publishes each as a new version with the new `fetched_at` even when the hash is equal, which resets the clock (`yt-text-purger §5.3 L102`). Who gets refresh is D2-Q056's.

   Consequences: the approved yt-keyword-search, yt-web-search-bridge, normalize-item and registry-writer move under D2-Q001; normalize-item's equal-hash rule gains two named exceptions (completing a partial version, a refresh); F3 adds `platform_meta`.

2. **The YouTube PRDs as written: lists of up to 50 ids, and a hold in normalize-item with a timeout** (CF-083 option 2, AU-051 option 1). Consequences: one version per video, but dedup, retries and the DLQ work per id inside a message, one bad id retries 49 others, and normalize-item gains held state.
3. **Refresh as a store-side update** (AU-102 option 2): the fetcher reports refreshed ids and `fetched_at` moves without a new version. Consequences: no reprocessing of unchanged text, but a second write path into ClickHouse beside store-writer's item flow.
4. **One daily read for every channel without a working subscription** (AU-100 option 2). Consequences: 1 unit a channel a day whatever its tier, but a Tier 1 channel whose subscription failed can be 24 hours stale until ops repairs it.

**Open questions this also answers.** The `series_step` values on `jobs.yt-video-details-fetcher` are those of D2-Q034 (`+24h`, `+7d`, `refresh:<request_id>`); a backfilled first sight is marked by `job_kind = backfill`, not by a step (`yt-video-details-fetcher §14 Q2`).

**Why the recommendation.** One id per job keeps the queue contract simple while the collector still pays 1 unit per 50 ids; a partial version fails visibly; the playlist id sits with the identity columns its one writer owns; one failed subscription should not quietly break a tier's freshness promise at so small a cost; and a refresh that creates no version cannot reset the clock.

**Phase 2 records.** ADR "YouTube details, partial records and refresh" (Applies to: the nine YouTube services, normalize-item, registry-writer, store-writer). CONVENTIONS v1.1: L36 (`platform_meta`), L277 (`first_sight`, `refresh`), L279 (no `list` bucket), L48 and L49 (lost push coverage means tier cadence; dormant weekly), L76 (a refresh is a new version).

### D2-Q066 · How a client's own properties, and the sources it asks for, enter the registry

- **Class:** technical
- **Settles:** AU-018, AU-026, AU-057, tg-bot-channel-receiver §14 Q4
- **Blocks:** F3, then C7, C8, C9, IG4, TG1, TG2, VLI2
- **Depends on:** D2-Q013 (decision producers), D2-Q014 (`added`), D2-Q020 (`backfill_status`), D2-Q032 (`resolve` jobs), D2-Q049 (push coverage)

**Context.** registry-writer leaves subscriptions to the receivers, which "react to `added` themselves" (`registry-writer §3 L32`), as three do (`fb-client-webhook-receiver §5.1 L46`, `li-notification-receiver §5.1 L42`, `yt-pubsub-receiver §5.2 L50`); ig-webhook-receiver reads no `source.events` and subscribes when "an account is connected", with no trigger (`§5.1 L45`, `§6.1 L99`; AU-018). Telegram onboarding (AU-026, AU-057) rests on "an onboarding record with a one-time code and a pre-allocated `source_id`" that no table holds (`tg-bot-channel-receiver §5.2 L67`), then a `discovery.hits` candidate with `origin = client_onboarding` and `proposed_source_id` that poster-resolver and the qualifier should treat as always qualifying (`tg-bot-channel-receiver §5.2 L70`; `tg-discussion-receiver §5.2 L67`); both receivers set `backfill_status = capped` (`tg-bot-channel-receiver §5.1 L50`, `tg-discussion-receiver §5.1 L51`). registry-writer inserts with `gen_random_uuid()` and sends manual adds to poster-resolver as `origin: manual` (`registry-writer §5.3 L69`, `§5.2 L61`), the only origins poster-resolver and the qualifier know besides `discovery` (`poster-resolver §3 L27`, `qualifier §3 L27`); li-org-resolver expects onboarding candidates from registry-writer as `seed` (`li-org-resolver §5.1 L44`). At stake: a client's own Telegram channel can be typed as an individual or looked up through a paid vendor, early posts are orphaned under an unused id, and a connected Instagram account may get no webhook.

**Options**

1. **Owned properties as direct `add` decisions, requested sources through the manual path, nothing through `discovery.hits` (recommended).**
   - Client-owned properties (Facebook Pages, Instagram accounts, LinkedIn pages, TikTok accounts, YouTube channels, Telegram channels and their linked groups) are added by whoever establishes ownership: the client portal or admin console (D3 specifies the flow) or, for Telegram, tg-bot-channel-receiver and tg-discussion-receiver once the bot's role is verified, since a private channel's chat id is known only then (`tg-bot-channel-receiver §5.2 L69`). The `add` decision (a named producer, D2-Q013) carries `owned_by_client = true`, `added_by = client`, the client id, route `green`, the reach tier from the count the connection returns (rule 6, `CONVENTIONS L247`) and a pre-allocated `source_id`; no resolver or qualifier runs.
   - registry-writer inserts with that `proposed_source_id` instead of `gen_random_uuid()`; for a property already registered, the sender uses the existing id from the start and the add sets `owned_by_client`.
   - Receivers subscribe on `added` (`owned_by_client = true`) for their platform, ig-webhook-receiver included (it adds `source.events` to its reads), and turn push coverage on once the subscription is verified (D2-Q049), as fb-client-webhook-receiver and yt-pubsub-receiver already order it (`fb-client-webhook-receiver §5.1 L46`, `yt-pubsub-receiver §5.1 L44`).
   - Telegram: the one-time code and the channel's pre-allocated id live in a small onboarding table owned by tg-bot-channel-receiver (for example `tg_onboarding`, under D2-Q025's naming rule), created by the portal through the receiver's endpoint; tg-discussion-receiver allocates the group's id when it verifies the group. Neither receiver writes `backfill_status`: backfill-orchestrator sets `capped` with `capped_reason = no_history` (D2-Q020). This answers `tg-bot-channel-receiver §14 Q4 L197`: yes to the id, no to `discovery.hits`.
   - Third-party sources a client asks for take registry-writer's manual path as written (`§5.2 L61`): poster-resolver with `origin: manual` and the seed-list flag, then the qualifier with rules 2, 4 and 10 skipped. li-org-resolver receives them from poster-resolver like any `resolve` job (D2-Q032), not as `seed` from registry-writer.

   Consequences: the approved poster-resolver and qualifier stay as written; the approved registry-writer gains the `proposed_source_id` rule and the new `add` producers, and the approved li-org-resolver loses origin `seed` (both move under D2-Q001); `discovery.hits` carries no onboarding fields (D2-Q031).

2. **Onboarding through `discovery.hits`** (AU-057 option 2): poster-resolver accepts `origin = client_onboarding`, carries `proposed_source_id` and `owned_by_client`, and types groups as qualifying. Consequences: the Telegram PRDs stand and two approved PRDs change; owned properties pass a resolver, which for Telegram is the amber tg-channel-resolver, so a client's own green channel would be looked up through a vendor (against D2-Q052).
3. **Every client addition through the manual path** (AU-057 option 3, AU-026 option 3), the receivers mapping chats only after `added`. Consequences: no new producer, but resolver and qualifier work for properties the client has already proved it owns, and posts that arrive before the row exists are lost unless the receiver buffers them (AU-026 option 2).

**Why the recommendation.** Ownership proved by an authorisation or a bot's administrator role needs no discovery, resolution or Iraqi-signal check; sending it straight to the one registry writer leaves the approved discovery path untouched and avoids the paid and amber lookups the Telegram onboarding would trigger.

**Phase 2 records.** ADR "Client-owned property onboarding" (Applies to: registry-writer, backfill-orchestrator, li-org-resolver, the receivers of every platform, the client portal and admin console). CONVENTIONS v1.1: L36 (an owned add may carry a pre-allocated `source_id`), L21 (receivers subscribe on `added`). `DEFERRED.md`: the portal's onboarding screens, owner D3.

### D2-Q067 · One interface for the n8n flows, and who specifies and builds them

- **Class:** technical
- **Settles:** AU-097
- **Blocks:** F2, then A5, C1, C7, C9, C12, VLI2, X7
- **Depends on:** D2-Q012 (ops and client requests through the admin API)

**Context.** Seven services call n8n, each its own way. alert-evaluator delivers email, Telegram and Slack alerts through "an n8n flow reached by a signed webhook call" with payload `alert/v1` (`alert-evaluator §3 L24`, `§5.3 L69`, `§6.2 L87`); the qualifier posts review cards to `POST /qualifier/review` with three buttons and a signed callback (`qualifier §5.3 L67`, `§9 L116`); source-health-canary sends state-change alerts and the approval card for `blocked` that README decision 5 requires (`source-health-canary §5.2 L57`, `§5.3 L77`; `README L182`); quota-governor's alerts, registry-writer's request notifications and li-org-resolver's review cards go through n8n (`quota-governor §4 L31`, `registry-writer §11 L133`, `li-org-resolver §6.2 L79`); x-compliance-sync takes ops' export requests through n8n (`x-compliance-sync §6.2 L130`). CONVENTIONS names n8n in the stack and for review cards (L3, L251). No document defines the flows, endpoints, payloads or signing, and no session builds them: D3 specifies the query API, client portal, dashboard and admin console (`build-plan/sessions/D3-specs-for-the-parts-with-no-prd.md` L7); I2 routes only the Prometheus alerts through n8n (`build-plan/sessions/I2-observability.md` L7, L31); C9 may stub the card webhook (`build-plan/sessions/C9-qualifier.md` L28). At stake: every caller invents its own endpoint, and nothing tests the far side.

**Options**

1. **One documented n8n interface, the flows specified by D3, the build assigned by the orchestrator (recommended).**
   - Outbound: every service calls n8n through one SDK client with one HMAC scheme (a signature over the body with a timestamp and an idempotency key, as alert-evaluator already signs client webhooks, `§5.3 L69`; secrets in Vault).
   - Two payload schemas in F2: `n8n.alert/v1` for one-way notices (client alerts, ops alerts, request notifications; alert-evaluator's `alert/v1` becomes it) and `n8n.card/v1` for decision requests, with buttons, default action and timeout (review cards, the `blocked` approval card, missing-grant cards).
   - Inbound: a button press or an ops request returns only through the admin API (D3), signed the same way and audited, which hands it to the owning service (the qualifier's review answer, the canary's fallback approval, x-compliance-sync's export request), as D2-Q012 routes every ops and client request.
   - D3 specifies the flows alongside the admin console (one flow per channel and per card type, with the Telegram-to-email fall-through `alert-evaluator §5.3 L69` requires). The build plan names no session to build them, so the orchestrator assigns one (I2, which already deploys n8n routes, is the nearest fit); until then services test against a fake n8n endpoint.

   Consequences: F2 gains two schemas and the signing helper; the qualifier's callback moves from its own endpoint to the admin API (an approved PRD moves under D2-Q001); D3's brief gains the flows; x-compliance-sync's exports become an admin console action.

2. **Each caller owns its flow and documents it in its PRD** (AU-097 option 2). Consequences: no shared work, but seven payloads and signing schemes, and each build session must also build and test a flow it does not run.
3. **Direct email, Slack and Telegram clients in alert-evaluator; n8n for cards only** (AU-097 option 3). Consequences: client alerts no longer depend on n8n, but alert-evaluator carries three delivery clients and their dependency lines, and ops alerts and cards still need option 1's interface.

**Why the recommendation.** The callers already share one pattern, a signed webhook out and a signed callback in; fixing it once in F2 and sending people's answers through the admin API gives one audited path for human decisions, the path D2-Q012 already sets for ops and client requests.

**Phase 2 records.** ADR "The n8n interface" (Applies to: alert-evaluator, qualifier, source-health-canary, quota-governor, registry-writer, li-org-resolver, x-compliance-sync, listening-sdk, the admin console). CONVENTIONS v1.1: L3 and L251 (n8n's role, the two schemas, one signing rule, callbacks through the admin API). `DEFERRED.md`: the build of the n8n flows, owner assigned by the orchestrator.

## Group 9 · Legal policies and the editorial pass

### D2-Q068 · Using platform content for models and media: training and evaluation data, Content Signals, stored media

- **Class:** user (readings of the platforms' terms, the vendor contracts and Iraqi copyright law; counsel confirms)
- **Settles:** analysis-entities §14 Q7, analysis-media §14 Q2, analysis-sentiment §14 Q3, analysis-topics §14 Q7, news-article-extractor §14 Q2, news-robots-checker §14 Q1, news-robots-checker §14 Q2
- **Blocks:** F2 (the declared `usage_signals` field on `items.normalized`), A0 (its splits need only D2, A0 brief), then C4, C13, A1, A2, A3, A4, N1, N6

**Context.** Three analysis PRDs ask the same question: "May each platform's content and vendor data be used to train and evaluate in-house models, and for how long? Legal to confirm" (`analysis-sentiment §14 Q3`; the same in `analysis-entities §14 Q7` and `analysis-topics §14 Q7`). A0 freezes train, dev and test splits from staging samples (A0 brief, "Builds"). The terms in CONVENTIONS pull different ways: Meta's Tech Provider "processes only on behalf of its client" (L163); TikTok forbids databases on individuals (L178); LinkedIn keeps member data 48 hours (L192); Instagram allows only "aggregated, de-identified output" (L171); news is stored as excerpts under Law No. 3 of 1971 (L213). The news PRDs ask whether Content-Signal `search = no` is a stop (`news-robots-checker §14 Q1`, proposed yes) and what `ai-input = no` does to model analysis (`news-robots-checker §14 Q2`, `news-article-extractor §14 Q2`). analysis-media asks whether media may be stored, and whether YouTube thumbnails only is right (`analysis-media §14 Q2`), as README decision 7 proposes "pending legal review" (`README L184`).

**Options**

1. **Evaluate on de-identified platform content; train only on data cleared for training; honour Content Signals; store media only where the terms allow (recommended).**
   - (a) Evaluation: A0's dev and test sets may hold de-identified platform items (author references only, D2-Q010), never shared outside the service. A frozen split outlives some classes (CONVENTIONS L75 to L77), so only these may enter: `meta_on_request`, `vendor_agreed`, `tiktok_display`, `telegram_bot` and `news_excerpt` (the excerpt, never cached full text); `x_24h_sync` items only because deletions reach the set within 24 hours; `youtube_30d_text` items with their comment text only until day 30, after which the split keeps the id and the label; no `linkedin_48h` or `linkedin_org` item at all. The sets are registered holders in the SDK purge registry (D2-Q035), and A0 re-versions a split when a deletion removes one of its items. The splits committed under `fixtures/eval/` (A0 brief) hold ids and labels only; the text sits in the registered store, so no deletion rewrites git history.
   - (b) Training and fine-tuning without counsel: licensed or public datasets, and synthetic and annotator-written examples. Everything else waits for counsel's confirmation source by source (`DEFERRED.md`, owners A1 to A4): platform content from Meta, TikTok, X, LinkedIn and YouTube; client-owned content, Meta's included, since a model shared by all clients is not processing "on behalf of its client" (L163), consent or not; news text, kept as excerpts for copyright (L213), where a missing `ai-train = no` is not a licence; Telegram data from the bot and the vendor; Disqus comments; and vendor data, whose platform's terms still apply. `ai-train = no` always keeps a host's text out.
   - (c) Content Signals: `search = no` means no article fetch and no excerpt stored for that host, while the site row stays (news-robots-checker's proposal); `ai-input = no` keeps that host's excerpts and cached text out of model analysis while keyword matching still runs; `ai-train = no` as in (b). news-article-extractor already carries `usage_signals` in the raw envelope's `context` (`news-article-extractor §6.2 L103-L104`, D2-Q005); normalize-item copies it into a declared field of `items.normalized`, which F2 adds, so the analysis services can skip the item.
   - (d) Media: images are stored under `media/<sha256>` only where the platform's terms and the vendor contract allow, under the item's retention class; YouTube stays thumbnails only in v1 (README decision 7); audio and video are downloaded nowhere until counsel confirms per platform. So analysis-media runs on images and thumbnails only in v1: no speech-to-text and no video-frame OCR (`analysis-media §3 L23`, `§5.2 L54`, `§13 L156`); A4 builds them behind a setting left off.

   Consequences: A0 starts on real Iraqi samples after G2, with no LinkedIn items; models are fine-tuned on public and annotated data at first; video analysis waits for counsel.

   Variant of (d): the no-download rule stays YouTube-only, as README decision 7 wrote it, and other platforms' audio and video are downloaded "where the terms allow" like images. Consequences: speech-to-text and frame OCR run in v1 where the team reads the terms as allowing it, before counsel confirms.

2. **Train and evaluate on all collected content, de-identified, within each item's retention class.** Consequences: the best dialect models soonest, but an exposure under Meta's "on behalf of its client" and TikTok's database rule that counsel may force the platform to unwind, with retraining.
3. **No platform content in any model set,** evaluation included. Consequences: no exposure, but an evaluation set unlike the data clients see; A0's plan changes.

**Why the recommendation.** Evaluation on de-identified samples is how an analytics product measures itself, and it holds nothing longer than retention allows; training is where terms and copyright bite, so real content waits for counsel.

**Phase 2 records.** ADR "AI and media use of platform content" (Applies to: F2, A0, the four analysis services, normalize-item, news-robots-checker, news-article-extractor, deletion-propagator). CONVENTIONS v1.1, "Security and compliance in every service": the evaluation and training rules, the three Content-Signal rules, the media rule. `DEFERRED.md`: counsel's per-source confirmation of training use (owners A1 to A4) and of media storage and audio and video download (owner A4).

### D2-Q069 · Legal policies the deletion and audit paths need: author requests, deadlines, backups, audit retention, the X rules

- **Class:** user (each point is a legal policy; the recommendation gives a buildable default for counsel to confirm before G4)
- **Settles:** AU-079, deletion-propagator §14 Q1, deletion-propagator §14 Q3, deletion-propagator §14 Q6, raw-archiver §14 Q3, retention-purger §14 Q1, retention-purger §14 Q4, x-compliance-sync §14 Q1, x-compliance-sync §14 Q6, x-compliance-sync §14 Q7, x-filtered-stream §14 Q6, x-full-archive-search §14 Q4
- **Blocks:** F2, F3, then C7, C13, C14, X7, I1, D3, U2, X1, X5, G4

**Context.** The deletion and audit services leave several policies "to be agreed with counsel": who verifies the identity of an author who files a request (`retention-purger §14 Q1`, proposed: a confirmation sent to the platform account's public contact); the grace period of the `meta_on_request` necessity clock and how long audit records are kept (`retention-purger §14 Q4`); deletion deadlines for non-X `platform_sync` and for `legal` requests (`deletion-propagator §14 Q6`); backups and snapshots, which "must expire inside the shortest deadline or be excluded" (`deletion-propagator §14 Q1`); whether X's 24-hour clock runs from X's compliance signal or from the event on X (`x-compliance-sync §14 Q1`; CONVENTIONS L186 says "deletions must be mirrored within 24 hours"); how long identifiable X items, evidence files and audit records are kept (`x-compliance-sync §14 Q7`); and who screens client keyword terms for "sensitive events (protests, rallies)", which X forbids monitoring (`x-full-archive-search §14 Q4`; CONVENTIONS L188). One entry adds a registry question: an erasure request from someone whose account is a registered source has no producer for the registry decision and no reason value for it (`deletion-propagator §14 Q3`, proposed: retention-purger emits it; AU-079).

**Options**

1. **Defaults that can be built now, the strictest where a deadline is at stake, each confirmed by counsel before G4 (recommended).**
   - (a) In plain words: an author's request deletes what they asked for, but stops monitoring of their public account only if they ask. A matching registered source's items are deleted like any other; if the request asks, retention-purger sends a `retire` decision with the new reason `owner_request` on `registry.decisions` (F2), which registry-writer applies and audits (AU-079; registry-writer, an approved PRD, gains the reason value under D2-Q001). That retirement is sticky: discovery never re-qualifies the source, and a later sighting does not bring it back as `updated` (D2-Q020); only a person can re-add it through the admin console, with the request on record.
   - (b) Identity check: a confirmation sent to the account's public contact on the platform, as retention-purger proposes; the admin console (D3) records the request and the confirmation.
   - (c) Deadlines: every deletion is engineered to the strictest documented deadline, X's 24 hours from a verified request or signal, on every route, until counsel sets per-reason deadlines; the X clock is read from X's compliance signal, with the compliance stream reconsidered at X's Enterprise review.
   - (d) Backups may live longer than the deadline only if every restore re-applies the deletion log (`deletion_requests` and the tombstones of D2-Q035) before any data is served; I1 builds the restore procedure that way.
   - (e) Audit and evidence rows hold ids, hashes, reasons and timestamps only, never content or clear identities, and are kept for the life of the client contract until counsel sets a period; the `meta_on_request` grace period is counsel's. X's `user_ids` arrive as X sends them and travel in the deletion target only so the archives can be searched (`x-compliance-sync §5.3 L81`); the evidence row keeps `author_ref`, not the id; identifiable X items follow `x_24h_sync`.
   - (f) X sensitive events: client keyword terms are screened when they are entered, against the list of sensitive-event terms in a new F3 table, `screened_terms`, owned by the admin console (D3 specifies the writer) and kept by the user's compliance owner; the result is a new column `keywords.screening_status` (D2-Q044), written by the client portal (D3); a flagged term is not run on X.

   Consequences: C13, C14 and X7 have a target to build and test; F2 adds the reason, F3 the table and column; I1 designs backups around replay-after-restore; a few lines in the portal and admin console specs (D3).

2. **Leave every point to counsel before the services are built.** Consequences: no guess to unwind, but C13, C14 and X7 cannot finish their acceptance tests, and I1 cannot design backups.
3. **Per-route deadlines now, from each platform's terms as read by the team** (X 24 hours; others longer), with backups excluded from deletion entirely. Consequences: less engineering pressure, but a restore could resurface deleted data, and the team, not counsel, reads the terms.

**Open questions this also answers.** Also: (g) envelope-only archive files follow the text clock of their class, deleted with the item at 36 months for YouTube and on deletion for `meta_on_request` (`raw-archiver §14 Q3`); (h) at a client's offboarding retention-purger owns the deletion of data held only for that client, and yt-text-purger stops refreshing that client's YouTube text at once (`yt-text-purger §14 Q2`, offboarding hand-off); (i) the X blocked-terms list of (f) is the F3 table `screened_terms`, owned by the admin console (D3 specifies the writer), read by x-filtered-stream and x-recent-search (`x-filtered-stream §14 Q6`).

**Why the recommendation.** The strictest documented deadline and replay-after-restore are safe whatever counsel decides, so building to them loses nothing; the points that only counsel can settle stay open without blocking the build.

**Phase 2 records.** ADR "Legal policies for deletions and audits" (Applies to: F2, F3, deletion-propagator, retention-purger, x-compliance-sync, registry-writer, qualifier, the X searchers, I1, D3). CONVENTIONS v1.1, "Security and compliance in every service": the defaults (a) to (f). `DEFERRED.md`: counsel's confirmation of each point, owner G4.

### D2-Q070 · One editorial pass: the documents that disagree with themselves

- **Class:** technical
- **Settles:** CF-027, CF-117, RN-17
- **Blocks:** F2 first (one spelling per field), then F5, C1, C2, C4, C5, FB3, N1, N6, TG1, W1, W2, W4, W5, YT5, YT6 (and every session that quotes CONVENTIONS or the README literally)

**Context.** CF-027 lists nine places where one PRD names a message field two ways, prose against its own example: a) keyword-matcher's `set_version` (`keyword-matcher §5.3 L58`) against `keyword_set_version`, rendered `"cs:3f9a1c"` while the `message_id` embeds `cs3f9a1c` (`§6.2 L100`, `L107`); b) news-robots-checker's `robots_status` (`§5.3 L71`) against `robots.status` (`§6.2 L102`), with `ai-input` and `ai-train` mapped to `ai_input` and `ai_train` unstated (`§5.3 L73`); c) the web engines' `normalize = skip` on records whose envelope lists have no such field (`web-search-perplexity §5.2 L55`, `§6.2 L89`, and the other two engines); d) `lang_pending`, `text_full_ref` and `author_followers` missing from normalize-item's example (`normalize-item §8 L133`, `§5.3 L72`, `§5.4 L79`); e) fb-backfill's envelope "identical to fb-page-feed-poller's" yet with a `window` object (`fb-backfill §6.2 L88`, `L104`); f) tg-bot-channel-receiver's "the `channel_post` object unchanged" while edits arrive as `edited_channel_post` (`§6.2 L113`, `§5.2 L59`); g) raw-archiver's `raw.replay` example short of its own field list (`raw-archiver §6.2 L98-L115`); h) news-article-extractor's promised code version, shown as `"extractor": "trafilatura"` (`§12 L167`, `§6.2 L120`); i) web-commoncrawl-scanner's `accept_rate` "from `source.events`", which its reads omit (`§10 L136`, `§6.1 L80`).

CF-117 collects five inconsistencies sessions would quote literally: a) replies "through the same service with job kind `replies`" (`CONVENTIONS L60`) against YouTube's own yt-replies-fetcher (`L265`); b) the X cap "per billing cycle" (`CONVENTIONS L87`; `quota-governor §5.3 L78`) against "per month on pay-per-use" (`CONVENTIONS L187`; `x-full-archive-search §7 L139`); c) route values "GREEN", "AMBER", "RED" (`L7`), green or amber (`L36`), `shared` in the PRD header template, with six lanes (`L122`) against seven in the addendum (`L275`); d) the platform prefix rule (`L11`) against search-hit-router under Web (`L234`); e) README sentences on Google results (`README L18` against `L143` to `L147` and `CONVENTIONS L217`), tt-hashtag-feed-poller (`L70` against `L22`, `L30`) and the nine decisions being "consistent" (`L176`). D1's review note 17 adds that `docs/contracts/INVENTORY.md` lists "Known corrections from the review" (L20 to L34) without applying them to its rows.

**Options**

1. **One editorial pass, each point decided here so F2 has one spelling (recommended).**
   - CF-027: a) `keyword_set_version`, rendered `cs:<hex>`, with keyword-matcher's replay-stable `message_id` derived from it (D2-Q002, D2-Q006); b) `crawl.policies` uses the flat names of the `crawl_policies` row (D2-Q040), `robots_status`, each Content-Signal directive mapped by replacing the hyphen with an underscore (`ai_input`, `ai_train`, `search`), stated once; c) `normalize = skip` disappears, the engines' responses taking the archive-only record kind of D2-Q008; d) `lang_pending` and `text_full_ref` join `items.normalized/v1`, and `author_followers` only for registered sources (D2-Q010); e) `window` is a declared `context` field (D2-Q005); f) each update is written as returned, an edit reusing the post's key (D2-Q009); g) moot, there is no `raw.replay` topic (D2-Q039); h) `extractor` and `extractor_version`; i) web-commoncrawl-scanner's reads gain `source.events`.
   - CF-117 a): replies are job kind `replies` on the comment service's queue, except where a route has a dedicated replies service, which CONVENTIONS lists (YouTube). Rejected: a replies service on every route, services with no API of their own.
   - b): the cap is "per billing cycle", the term of CONVENTIONS L87 and `quota-governor §5.3 L78`, and quota-governor's period follows the cycle; L187 is aligned. Rejected: per calendar month, which would mis-time the cap whenever the cycle does not start on the 1st.
   - c): lower-case `green` and `amber` in data; "RED" stays prose for what is never built; `shared` is a header label only; seven lanes, the template updated. Rejected: `shared` as a `route` value, which no data record needs since every fetch is green or amber, and six lanes, which would re-label tt-video-stats-refresher.
   - d): search-hit-router keeps its name as the one listed exception to the prefix rule, since it routes results of several platforms. Rejected: `web-search-hit-router`, which edits every PRD naming it and implies web only.
   - e): the README's sentences reworded to match the service lists and point to D2. RN-17: `INVENTORY.md` stays D1's record "as written in the PRDs"; CONVENTIONS v1.1 names the ADRs, CONVENTIONS, F2's `VERSIONING.md` and F3's `TABLE-OWNERS.md` as the contract, the inventory as background.

   Consequences: one pass by phase 2; nothing in the contracts changes except the route enum's case.

2. **A blanket rule for CF-027: the section 6.2 example always wins** (or the prose always wins), with CF-117 as in option 1. Consequences: simpler to state, but the example rule deletes `text_full_ref` and `lang_pending`, which D2-Q022 relies on, and the prose rule keeps `set_version` beside a message id that no longer embeds it.
3. **Leave the documents and let each owning session pick.** Consequences: no edits now, but F2 freezes before those sessions run, so it would guess, and sessions keep quoting the inconsistent lines.

**Why the recommendation.** Each answer matches how the PRDs behave and what the other decisions recommend, and F2 needs one spelling before it freezes; fixing the text once is cheaper than every session asking.

**Phase 2 records.** ADR "Editorial corrections" (Applies to: all; the nine CF-027 PRDs by name). The CF-027 spellings go to F2 through the ADR; the PRD lines are corrected citing it. CONVENTIONS v1.1 L7, L11, L60, L87 and L187, L122, L234, L275, and the sentence on the contract documents; README L18, L22, L30, L70 and L176, each edit citing the ADR.

## Appendix A · Every CF and AU entry and its decision

| Entry  | Decision | Entry  | Decision | Entry  | Decision |
| ------ | -------- | ------ | -------- | ------ | -------- |
| CF-001 | D2-Q002  | CF-002 | D2-Q003  | CF-003 | D2-Q004  |
| CF-004 | D2-Q005  | CF-005 | D2-Q005  | CF-006 | D2-Q005  |
| CF-007 | D2-Q009  | CF-008 | D2-Q008  | CF-009 | D2-Q031  |
| CF-010 | D2-Q031  | CF-011 | D2-Q031  | CF-012 | D2-Q032  |
| CF-013 | D2-Q033  | CF-014 | D2-Q033  | CF-015 | D2-Q013  |
| CF-016 | D2-Q014  | CF-017 | D2-Q023  | CF-018 | D2-Q034  |
| CF-019 | D2-Q034  | CF-020 | D2-Q035  | CF-021 | D2-Q035  |
| CF-022 | D2-Q036  | CF-023 | D2-Q037  | CF-024 | D2-Q017  |
| CF-025 | D2-Q022  | CF-026 | D2-Q039  | CF-027 | D2-Q070  |
| CF-028 | D2-Q036  | CF-029 | D2-Q040  | CF-030 | D2-Q020  |
| CF-031 | D2-Q015  | CF-032 | D2-Q016  | CF-033 | D2-Q013  |
| CF-034 | D2-Q041  | CF-035 | D2-Q041  | CF-036 | D2-Q041  |
| CF-037 | D2-Q042  | CF-038 | D2-Q042  | CF-039 | D2-Q043  |
| CF-040 | D2-Q044  | CF-041 | D2-Q045  | CF-042 | D2-Q045  |
| CF-043 | D2-Q045  | CF-044 | D2-Q045  | CF-045 | D2-Q046  |
| CF-046 | D2-Q045  | CF-047 | D2-Q040  | CF-048 | D2-Q040  |
| CF-049 | D2-Q047  | CF-050 | D2-Q023  | CF-051 | D2-Q047  |
| CF-052 | D2-Q047  | CF-053 | D2-Q039  | CF-054 | D2-Q045  |
| CF-055 | D2-Q035  | CF-056 | D2-Q043  | CF-057 | D2-Q016  |
| CF-058 | D2-Q023  | CF-059 | D2-Q025  | CF-060 | D2-Q006  |
| CF-061 | D2-Q007  | CF-062 | D2-Q007  | CF-063 | D2-Q007  |
| CF-064 | D2-Q007  | CF-065 | D2-Q007  | CF-066 | D2-Q007  |
| CF-067 | D2-Q009  | CF-068 | D2-Q008  | CF-069 | D2-Q010  |
| CF-070 | D2-Q006  | CF-071 | D2-Q006  | CF-072 | D2-Q006  |
| CF-073 | D2-Q032  | CF-074 | D2-Q011  | CF-075 | D2-Q023  |
| CF-076 | D2-Q035  | CF-077 | D2-Q011  | CF-078 | D2-Q012  |
| CF-079 | D2-Q012  | CF-080 | D2-Q012  | CF-081 | D2-Q034  |
| CF-082 | D2-Q058  | CF-083 | D2-Q065  | CF-084 | D2-Q064  |
| CF-085 | D2-Q032  | CF-086 | D2-Q011  | CF-087 | D2-Q004  |
| CF-088 | D2-Q020  | CF-089 | D2-Q017  | CF-090 | D2-Q057  |
| CF-091 | D2-Q057  | CF-092 | D2-Q022  | CF-093 | D2-Q035  |
| CF-094 | D2-Q021  | CF-095 | D2-Q049  | CF-096 | D2-Q049  |
| CF-097 | D2-Q051  | CF-098 | D2-Q014  | CF-099 | D2-Q042  |
| CF-100 | D2-Q018  | CF-101 | D2-Q018  | CF-102 | D2-Q050  |
| CF-103 | D2-Q051  | CF-104 | D2-Q054  | CF-105 | D2-Q055  |
| CF-106 | D2-Q056  | CF-107 | D2-Q019  | CF-108 | D2-Q061  |
| CF-109 | D2-Q010  | CF-110 | D2-Q038  | CF-111 | D2-Q022  |
| CF-112 | D2-Q028  | CF-113 | D2-Q062  | CF-114 | D2-Q015  |
| CF-115 | D2-Q063  | CF-116 | D2-Q001  | CF-117 | D2-Q070  |
| CF-118 | D2-Q036  | AU-001 | D2-Q017  | AU-002 | D2-Q005  |
| AU-003 | D2-Q022  | AU-004 | D2-Q034  | AU-005 | D2-Q031  |
| AU-006 | D2-Q031  | AU-007 | D2-Q032  | AU-008 | D2-Q031  |
| AU-009 | D2-Q033  | AU-010 | D2-Q039  | AU-011 | D2-Q037  |
| AU-012 | D2-Q031  | AU-013 | D2-Q035  | AU-014 | D2-Q048  |
| AU-015 | D2-Q005  | AU-016 | D2-Q013  | AU-017 | D2-Q020  |
| AU-018 | D2-Q066  | AU-019 | D2-Q004  | AU-020 | D2-Q046  |
| AU-021 | D2-Q013  | AU-022 | D2-Q035  | AU-023 | D2-Q023  |
| AU-024 | D2-Q045  | AU-025 | D2-Q039  | AU-026 | D2-Q066  |
| AU-027 | D2-Q065  | AU-028 | D2-Q040  | AU-029 | D2-Q037  |
| AU-030 | D2-Q060  | AU-031 | D2-Q034  | AU-032 | D2-Q058  |
| AU-033 | D2-Q012  | AU-034 | D2-Q012  | AU-035 | D2-Q060  |
| AU-036 | D2-Q011  | AU-037 | D2-Q059  | AU-038 | D2-Q052  |
| AU-039 | D2-Q018  | AU-040 | D2-Q059  | AU-041 | D2-Q061  |
| AU-042 | D2-Q020  | AU-043 | D2-Q020  | AU-044 | D2-Q059  |
| AU-045 | D2-Q059  | AU-046 | D2-Q020  | AU-047 | D2-Q020  |
| AU-048 | D2-Q010  | AU-049 | D2-Q009  | AU-050 | D2-Q007  |
| AU-051 | D2-Q065  | AU-052 | D2-Q008  | AU-053 | D2-Q007  |
| AU-054 | D2-Q031  | AU-055 | D2-Q022  | AU-056 | D2-Q032  |
| AU-057 | D2-Q066  | AU-058 | D2-Q013  | AU-059 | D2-Q032  |
| AU-060 | D2-Q052  | AU-061 | D2-Q031  | AU-062 | D2-Q044  |
| AU-063 | D2-Q013  | AU-064 | D2-Q021  | AU-065 | D2-Q042  |
| AU-066 | D2-Q057  | AU-067 | D2-Q018  | AU-068 | D2-Q042  |
| AU-069 | D2-Q016  | AU-070 | D2-Q016  | AU-071 | D2-Q052  |
| AU-072 | D2-Q039  | AU-073 | D2-Q039  | AU-074 | D2-Q028  |
| AU-075 | D2-Q028  | AU-076 | D2-Q035  | AU-077 | D2-Q035  |
| AU-078 | D2-Q055  | AU-079 | D2-Q069  | AU-080 | D2-Q056  |
| AU-081 | D2-Q048  | AU-082 | D2-Q035  | AU-083 | D2-Q048  |
| AU-084 | D2-Q034  | AU-085 | D2-Q062  | AU-086 | D2-Q012  |
| AU-087 | D2-Q052  | AU-088 | D2-Q015  | AU-089 | D2-Q010  |
| AU-090 | D2-Q009  | AU-091 | D2-Q052  | AU-092 | D2-Q052  |
| AU-093 | D2-Q064  | AU-094 | D2-Q059  | AU-095 | D2-Q050  |
| AU-096 | D2-Q064  | AU-097 | D2-Q067  | AU-098 | D2-Q059  |
| AU-099 | D2-Q012  | AU-100 | D2-Q065  | AU-101 | D2-Q065  |
| AU-102 | D2-Q065  | AU-103 | D2-Q059  | AU-104 | D2-Q022  |
| AU-105 | D2-Q036  | AU-106 | D2-Q036  | AU-107 | D2-Q061  |
| AU-108 | D2-Q037  | AU-109 | D2-Q037  | AU-110 | D2-Q037  |
| AU-111 | D2-Q032  | AU-112 | D2-Q032  | AU-113 | D2-Q057  |

## Appendix B · README decisions, foundation choices and review notes

| Id    | Decision                   |
| ----- | -------------------------- |
| RD-1  | D2-Q017                    |
| RD-2  | D2-Q018                    |
| RD-3  | D2-Q019                    |
| RD-4  | D2-Q020                    |
| RD-5  | D2-Q021                    |
| RD-6  | D2-Q022                    |
| RD-7  | D2-Q023                    |
| RD-8  | D2-Q024                    |
| RD-9  | D2-Q025                    |
| FC-01 | no decision needed (below) |
| FC-02 | D2-Q013                    |
| FC-03 | D2-Q006                    |
| FC-04 | D2-Q002                    |
| FC-05 | D2-Q026                    |
| FC-06 | D2-Q027                    |
| FC-07 | D2-Q027                    |
| FC-08 | D2-Q028                    |
| FC-09 | D2-Q029                    |
| FC-10 | D2-Q030                    |
| FC-11 | D2-Q030                    |
| FC-12 | D2-Q029                    |
| FC-13 | D2-Q030                    |
| RN-08 | D2-Q025                    |
| RN-09 | D2-Q025                    |
| RN-10 | D2-Q036                    |
| RN-11 | D2-Q011                    |
| RN-12 | D2-Q017                    |
| RN-13 | D2-Q009                    |
| RN-16 | D2-Q046                    |
| RN-17 | D2-Q070                    |

### No decision needed

| Id    | Reason                                                                                                                                               |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| FC-01 | D1 found conflicts against all nine README proposals, so each is decided on its own in Group 2 (D2-Q017 to D2-Q025); the row itself needs no answer. |

## Appendix C · Open questions: placement

Each of the 387 top-level questions of `docs/prds/OPEN-QUESTIONS.md` (section 14 of every PRD; the six PRDs that list their questions as bullets are numbered in order), placed in the decision that settles it or marked `none` with the reason and the session that settles it. Phase 2 lists every `none` that is still open in `docs/decisions/DEFERRED.md`.

| Question                          | Decision | Reason or owner                                                                                                                                                       |
| --------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| fb-backfill §14 Q1                | D2-Q059  | one `once` comment fetch (priority 5) for each backfilled post older than 30 days on green routes; none on amber in v1                                                |
| fb-backfill §14 Q2                | none     | pilot: `capped` posting-rate-gap threshold measured in G3-facebook (owner FB3)                                                                                        |
| fb-backfill §14 Q3                | none     | later user choice: client-requested backfill re-runs in the first release, asked by D3 (the job already allows `reason = client`, D2-Q020)                            |
| fb-client-webhook-receiver §14 Q1 | none     | pilot: whether comment events arrive in `feed` or `comments`, measured in FB0                                                                                         |
| fb-client-webhook-receiver §14 Q2 | none     | pilot: full content or ids only in events, measured in FB0                                                                                                            |
| fb-client-webhook-receiver §14 Q3 | none     | pilot: Meta's retry schedule and response deadline measured in FB0                                                                                                    |
| fb-client-webhook-receiver §14 Q4 | none     | local: settled by FB7 in its build (proposed: `hide` and `unhide` ignored in v1)                                                                                      |
| fb-client-webhook-receiver §14 Q5 | none     | local: settled by FB7 in its build (missed pushes counted from reconciliation)                                                                                        |
| fb-group-comments-fetcher §14 Q1  | none     | pilot: vendor comment ids, reply counts, replies call and order measured in VFB0                                                                                      |
| fb-group-comments-fetcher §14 Q2  | none     | local: settled by VFB3 in its build (initial value, tuned after the pilot)                                                                                            |
| fb-group-comments-fetcher §14 Q3  | D2-Q018  | extensions are later comment steps (priority 3): kept at 80%, shed from 95%                                                                                           |
| fb-group-comments-fetcher §14 Q4  | D2-Q052  | amber series stop when the flag goes off, so missed steps are not caught up                                                                                           |
| fb-group-comments-fetcher §14 Q5  | D2-Q062  | a deletion needs a confirmed second miss; none on absence where the vendor read is not a complete listing                                                             |
| fb-group-posts-poller §14 Q1      | none     | pilot: vendor parameters, page size, ordering and depth measured in VFB0                                                                                              |
| fb-group-posts-poller §14 Q2      | none     | pilot: member count and per-post counts in the response, measured in VFB0                                                                                             |
| fb-group-posts-poller §14 Q3      | D2-Q051  | ScrapeCreators primary for groups and comments                                                                                                                        |
| fb-group-posts-poller §14 Q4      | D2-Q051  | the user verifies vendor owners before each vendor probe; flags stay off until then                                                                                   |
| fb-group-posts-poller §14 Q5      | D2-Q010  | yes: once a poster is classed individual, raw-archiver replaces the id in the archived batch                                                                          |
| fb-group-posts-poller §14 Q6      | D2-Q058  | first-sight counts only for amber group posts in v1                                                                                                                   |
| fb-keyword-search §14 Q1          | D2-Q051  | a per-service vendor override: SociaVault for keyword search where ScrapeCreators has none                                                                            |
| fb-keyword-search §14 Q2          | none     | pilot: vendor search sort, date filter, page size, depth and Kurdish coverage measured in VFB0                                                                        |
| fb-keyword-search §14 Q3          | D2-Q044  | the variants live in the one `keywords` column list, written through the client portal (D3)                                                                           |
| fb-keyword-search §14 Q4          | none     | later user choice: a faster cadence for priority keywords on the vendor route (proposed: not in v1), asked by VFB1                                                    |
| fb-keyword-search §14 Q5          | D2-Q031  | no: keyword-matcher emits the early `discovery.hits`                                                                                                                  |
| fb-page-feed-poller §14 Q1        | none     | pilot: whether `since` filters on `created_time` or `updated_time`, measured in FB0 (edits become versions either way, D2-Q009)                                       |
| fb-page-feed-poller §14 Q2        | none     | local: settled by FB2 in its build (proposed: the Page token)                                                                                                         |
| fb-page-resolver §14 Q1           | D2-Q032  | no: each resolver refreshes its registered sources on its own rotation, so the loop stays                                                                             |
| fb-page-resolver §14 Q2           | none     | pilot: PPCA fields for third-party Pages measured in FB0                                                                                                              |
| fb-page-resolver §14 Q3           | none     | local: settled by FB1 in its build (field list after FB0)                                                                                                             |
| fb-page-resolver §14 Q4           | none     | pilot: Graph batching of candidates measured in FB0                                                                                                                   |
| fb-page-resolver §14 Q5           | D2-Q045  | resolvers keep no cache: negative answers live in `poster_profiles` under its expiry                                                                                  |
| fb-page-search §14 Q1             | none     | pilot: useful result depth per variant measured in G3-facebook (owner FB6)                                                                                            |
| fb-page-search §14 Q2             | none     | later user choice: a client "never suggest again" control, asked by D3 (`decisions` stays the qualifier's log, D2-Q045)                                               |
| fb-page-search §14 Q3             | none     | local: settled by FB6 in its build (proposed: yes)                                                                                                                    |
| fb-post-comments-fetcher §14 Q1   | none     | pilot: byte-identical `message` and returned reply parents measured in FB0                                                                                            |
| fb-post-comments-fetcher §14 Q2   | D2-Q019  | the +24 h step always runs: early stop is armed only after 5 stored comments or the +24 h step                                                                        |
| fb-post-comments-fetcher §14 Q3   | none     | pilot: whether `total_count` under `filter=stream` includes replies, measured in FB0                                                                                  |
| fb-post-comments-fetcher §14 Q4   | none     | local: settled by FB5 in its build (proposed: not in v1)                                                                                                              |
| fb-post-comments-fetcher §14 Q5   | D2-Q021  | no amber fallback for green Page comments while PPCA is pending                                                                                                       |
| fb-post-comments-fetcher §14 Q6   | D2-Q017  | the report is a `jobs.completed` record from the SDK wrapper; `comment_ledger` stays in the control plane (D2-Q046)                                                   |
| fb-reactions-fetcher §14 Q1       | D2-Q034  | the scheduler emits `metrics` jobs at `+24h` and `+7d` (sole emitter, D2-Q012); no due-time table here                                                                |
| fb-reactions-fetcher §14 Q2       | none     | pilot: `ids=` batching ceiling and its bucket cost measured in FB0                                                                                                    |
| ig-account-media-poller §14 Q1    | none     | pilot: `media` edge page size, order, cursor and depth measured in FB0                                                                                                |
| ig-account-media-poller §14 Q2    | D2-Q049  | push coverage only where new posts are pushed, so owned accounts keep their tier cadence (tier 1 through the priority list); the own-username read is measured in FB0 |
| ig-account-media-poller §14 Q3    | D2-Q034  | who writes the count observation of a re-read post (the `item.metrics` writer)                                                                                        |
| ig-account-resolver §14 Q1        | none     | pilot: Business Discovery error table built in FB0                                                                                                                    |
| ig-account-resolver §14 Q2        | none     | pilot: `id`, `username` and business or creator type in the response, measured in FB0                                                                                 |
| ig-account-resolver §14 Q3        | D2-Q045  | no `profile_cache`: `poster_profiles` is the one cache; `resolve` is the one job schema (D2-Q032)                                                                     |
| ig-account-resolver §14 Q4        | D2-Q033  | the resolver computes `lang_share` through lang-dialect-id                                                                                                            |
| ig-comments-fetcher §14 Q1        | none     | pilot: SociaVault comments endpoint, fields, paging, billing and price measured in VIG0                                                                               |
| ig-comments-fetcher §14 Q2        | D2-Q010  | one SDK `author_ref`, computed at the edge, one reference per person across services                                                                                  |
| ig-comments-fetcher §14 Q3        | D2-Q059  | which posts open a series (registered and client-owned sources); the order within the budget is C11's                                                                 |
| ig-comments-fetcher §14 Q4        | D2-Q018  | extensions are priority 3: kept at 80%, shed from 95%                                                                                                                 |
| ig-hashtag-search §14 Q1          | none     | pilot: `recent_media` and `top_media` page size and depth measured in FB0                                                                                             |
| ig-hashtag-search §14 Q2          | D2-Q048  | no `top_media` trending dimension in the v1 grain                                                                                                                     |
| ig-hashtag-search §14 Q3          | none     | pilot: hashtag media-volume thresholds measured in G3-instagram (owner IG2)                                                                                           |
| ig-hashtag-search §14 Q4          | none     | counsel: one tag list spread across a client's Instagram accounts, before IG2 (ledger per account, D2-Q042)                                                           |
| ig-keyword-search §14 Q1          | none     | pilot: SociaVault search endpoints, filters and fields measured in VIG0                                                                                               |
| ig-keyword-search §14 Q2          | D2-Q007  | one cross-route Instagram key (shortcode the candidate; the Graph id an attribute)                                                                                    |
| ig-keyword-search §14 Q3          | none     | later user choice: the monthly `ig_vendor` budget and per-source cap, asked by VIG0                                                                                   |
| ig-mentions-fetcher §14 Q1        | none     | pilot: whether `mentioned_media` and `mentioned_comment` can be listed, measured in FB0 (reads by id from the receiver: D2-Q012)                                      |
| ig-mentions-fetcher §14 Q2        | none     | pilot: page sizes, cursors and depth of the mentions edges measured in FB0                                                                                            |
| ig-mentions-fetcher §14 Q3        | D2-Q007  | the key uses the cross-route id, so deduplication does not rest on equal Graph ids                                                                                    |
| ig-mentions-fetcher §14 Q4        | none     | pilot: per-account limits measured in G3-instagram (hourly until then, owner IG5)                                                                                     |
| ig-own-comments-fetcher §14 Q1    | none     | pilot: comments edge order and replies paging measured in FB0                                                                                                         |
| ig-own-comments-fetcher §14 Q2    | D2-Q060  | no: the series anchors on first sight                                                                                                                                 |
| ig-own-comments-fetcher §14 Q3    | none     | pilot: whether comment text can be edited, measured in FB0                                                                                                            |
| ig-webhook-receiver §14 Q1        | none     | pilot: Meta's deadline, retry count and re-delivery measured in FB0                                                                                                   |
| ig-webhook-receiver §14 Q2        | none     | pilot: `comments` and `mentions` payloads, subscription call and permissions measured in FB0                                                                          |
| ig-webhook-receiver §14 Q3        | D2-Q012  | whether the scheduler acts on pushed counts (reconciliation from pushed counts)                                                                                       |
| tt-client-videos-fetcher §14 Q1   | none     | pilot: `video.list` limits, page size and completeness measured in TT0                                                                                                |
| tt-client-videos-fetcher §14 Q2   | D2-Q054  | a new class `tiktok_display`                                                                                                                                          |
| tt-client-videos-fetcher §14 Q3   | D2-Q035  | revocation deletes through `deletions`; the reason value joins the closed list                                                                                        |
| tt-client-videos-fetcher §14 Q4   | D2-Q053  | client-authorised items are visible only to the authorising clients                                                                                                   |
| tt-client-videos-fetcher §14 Q5   | D2-Q012  | the fetcher is the named producer of its own metrics (D2-Q024), so green videos never reach tt-video-stats-refresher                                                  |
| tt-hashtag-feed-poller §14 Q1     | none     | pilot: tag name or platform id per vendor, measured in VTT0                                                                                                           |
| tt-hashtag-feed-poller §14 Q2     | none     | pilot: feed depth and ordering per vendor measured in VTT0                                                                                                            |
| tt-hashtag-feed-poller §14 Q3     | none     | pilot: the posting-rate promotion threshold measured in G3-tiktok (owner VTT2)                                                                                        |
| tt-hashtag-feed-poller §14 Q4     | D2-Q031  | yes: hits for the hashtag's keyword, with a `matched_by` marker                                                                                                       |
| tt-keyword-search §14 Q1          | none     | pilot: recency sort and a stable cursor measured in VTT0                                                                                                              |
| tt-keyword-search §14 Q2          | none     | pilot: search backfill depth per vendor measured in VTT0                                                                                                              |
| tt-keyword-search §14 Q3          | D2-Q042  | one `tt_vendor` tag with per-service sub-counters                                                                                                                     |
| tt-profile-videos-poller §14 Q1   | none     | pilot: user-posts depth and the pinned flag measured in VTT0                                                                                                          |
| tt-profile-videos-poller §14 Q2   | none     | pilot: video ids and `create_time` precision across TikHub and EnsembleData measured in VTT0                                                                          |
| tt-profile-videos-poller §14 Q3   | D2-Q052  | no: client-owned green accounts are never reconciled through the amber vendor                                                                                         |
| tt-user-resolver §14 Q1           | none     | local: settled by VTT3 in its build (proposed: one 20-video read for one-signal creators; `lang_share` per D2-Q033)                                                   |
| tt-user-resolver §14 Q2           | D2-Q032  | tt-user-resolver refreshes its registered creators on its own rotation                                                                                                |
| tt-user-resolver §14 Q3           | D2-Q010  | no: the lookup key stays clear until the candidate is classed; an individual's answer carries `author_ref` only                                                       |
| tt-user-resolver §14 Q4           | none     | pilot: region and bio link per vendor measured in VTT0                                                                                                                |
| tt-video-comments-fetcher §14 Q1  | none     | pilot: comment order and a sort parameter measured in VTT0                                                                                                            |
| tt-video-comments-fetcher §14 Q2  | D2-Q046  | one shared comment-state table or one per-service design, decided on the evidence                                                                                     |
| tt-video-comments-fetcher §14 Q3  | D2-Q059  | series for registered and client-owned sources; amber keyword or hashtag finds get none in v1                                                                         |
| tt-video-comments-fetcher §14 Q4  | D2-Q010  | yes: the edge-computed `author_ref` passes through; no handle downstream                                                                                              |
| tt-video-stats-refresher §14 Q1   | none     | pilot: a batch video-detail form measured in VTT0                                                                                                                     |
| tt-video-stats-refresher §14 Q2   | D2-Q034  | closed steps `+24h`, `+7d`, `refresh:<request_id>`: no +30 d in v1                                                                                                    |
| tt-video-stats-refresher §14 Q3   | D2-Q060  | metrics anchor on creation and past steps are skipped (D2-Q034): no metrics jobs for a video first seen after 7 days                                                  |
| tt-video-stats-refresher §14 Q4   | D2-Q034  | the fixed count names of the `metrics` object (saves in or out)                                                                                                       |
| x-compliance-sync §14 Q1          | D2-Q069  | what starts the 24-hour clock, and a stream against daily batches                                                                                                     |
| x-compliance-sync §14 Q2          | none     | pilot: compliance endpoints, formats, job limits and withheld country codes measured in X0                                                                            |
| x-compliance-sync §14 Q3          | D2-Q018  | where compliance jobs sit in the priority table (proposed: reserved, never denied)                                                                                    |
| x-compliance-sync §14 Q4          | D2-Q035  | the `withhold` mode (countries carried) hides content from Iraqi clients only; content withheld elsewhere is recorded only                                            |
| x-compliance-sync §14 Q5          | D2-Q035  | every X reader requests `withheld`; recorded on the item, never a deletion                                                                                            |
| x-compliance-sync §14 Q6          | D2-Q069  | pausing X ingestion when no complete compliance run in 24 hours (government contracts)                                                                                |
| x-compliance-sync §14 Q7          | D2-Q069  | how long identifiable X items, evidence files and audit records are kept                                                                                              |
| x-filtered-stream §14 Q1          | none     | pilot: rule and tag lengths, rules per request, the listing call and numeric `from:` measured in X0                                                                   |
| x-filtered-stream §14 Q2          | none     | pilot: a stream recovery option on pay-per-use, measured in X0                                                                                                        |
| x-filtered-stream §14 Q3          | D2-Q064  | the gap job is `reconciliation` with `window_start`, `window_end`, `query`, `source_ids`, `client_ids`                                                                |
| x-filtered-stream §14 Q4          | D2-Q063  | no: x-recent-search keeps searching every keyword rule, tier 1 every 15 minutes as the safety net                                                                     |
| x-filtered-stream §14 Q5          | none     | pilot: `author_id` expansion billing measured in X0                                                                                                                   |
| x-filtered-stream §14 Q6          | D2-Q069  | who keeps ops' blocked-terms list (sensitive-events screening); the Enterprise timing is D2-Q053's, with x-recent-search Q3                                           |
| x-full-archive-search §14 Q1      | D2-Q011  | `keyword_history` stays a kind of its own in the closed list, emitted only by backfill-orchestrator on a client's request (D2-Q064)                                   |
| x-full-archive-search §14 Q2      | D2-Q064  | no hand-back for replies older than 7 days in v1, so no boundary to store                                                                                             |
| x-full-archive-search §14 Q3      | none     | pilot: `author_id` expansion billing measured in X0                                                                                                                   |
| x-full-archive-search §14 Q4      | D2-Q069  | who screens client terms for sensitive events, and where that is recorded                                                                                             |
| x-full-archive-search §14 Q5      | D2-Q059  | whether a client's history read also buys discovery (candidates and backfills); `job_kind` marks history (D2-Q005)                                                    |
| x-full-archive-search §14 Q6      | none     | later user choice: re-requesting capped X history in the next billing cycle, asked by C10                                                                             |
| x-recent-search §14 Q1            | none     | pilot: maximum query length and `lang:ckb` measured in X0                                                                                                             |
| x-recent-search §14 Q2            | none     | pilot: plain handle terms against mentions measured in X0                                                                                                             |
| x-recent-search §14 Q3            | D2-Q053  | when X moves to Enterprise, and who sees X data before then                                                                                                           |
| x-replies-fetcher §14 Q1          | none     | pilot: `author_id` expansion billing measured in X0                                                                                                                   |
| x-replies-fetcher §14 Q2          | none     | pilot: quote-post capture measured in X0                                                                                                                              |
| x-replies-fetcher §14 Q3          | none     | pilot: the page cap and `until_id` gap closing measured in X0                                                                                                         |
| x-replies-fetcher §14 Q4          | D2-Q017  | the closed status list; posts first seen after day 7 get no replies (D2-Q059); deleted parents end the series through `deletions`; the extension count is C11's       |
| x-replies-fetcher §14 Q5          | D2-Q007  | every tweet is `x:post:<id>`; a reply is a post with a parent link                                                                                                    |
| x-replies-fetcher §14 Q6          | D2-Q010  | no: repliers are hashed at the edge; only registered sources keep an identity                                                                                         |
| x-replies-fetcher §14 Q7          | D2-Q059  | no series on posts flagged as sensitive events on X                                                                                                                   |
| x-user-resolver §14 Q1            | D2-Q043  | watchlists are flags on `client_sources`; the review rule for watchlist-only passes is C9's                                                                           |
| x-user-resolver §14 Q2            | none     | pilot: extra `user.fields` at no extra price measured in X0                                                                                                           |
| x-user-resolver §14 Q3            | none     | pilot: a readable verification type measured in X0                                                                                                                    |
| x-user-resolver §14 Q4            | none     | pilot: expansion billing measured in X0 (X1 and X4 then choose their `user.fields`)                                                                                   |
| x-user-resolver §14 Q5            | none     | answered: CONVENTIONS L243 (rule 2 needs an Iraqi city or governorate)                                                                                                |
| x-user-resolver §14 Q6            | D2-Q032  | no: each resolver refreshes its registered sources, so the loop stays                                                                                                 |
| x-user-timeline-poller §14 Q1     | D2-Q041  | no: another service's `cursors` rows are never a contract; coverage travels as push coverage (D2-Q049, D2-Q014)                                                       |
| x-user-timeline-poller §14 Q2     | none     | pilot: the share of reposts and own replies measured in X0                                                                                                            |
| x-user-timeline-poller §14 Q3     | none     | pilot: `author_id` expansion billing measured in X0                                                                                                                   |
| x-user-timeline-poller §14 Q4     | none     | answered: quota-governor §5.2 L59 (the governor settles and releases unused units)                                                                                    |
| x-user-timeline-poller §14 Q5     | D2-Q050  | a per-client declared-end-user column beside the global `x_plan`                                                                                                      |
| li-client-posts-poller §14 Q1     | none     | pilot: whether notifications announce new posts, measured in LI0                                                                                                      |
| li-client-posts-poller §14 Q2     | D2-Q055  | six weeks (`linkedin_org`) until counsel confirms six months; this sets the backfill cap                                                                              |
| li-client-posts-poller §14 Q3     | none     | pilot: counts in the Posts API measured in LI0                                                                                                                        |
| li-client-posts-poller §14 Q4     | D2-Q043  | yes: the priority flag on `client_sources` makes the source tier 1                                                                                                    |
| li-company-posts-poller §14 Q1    | none     | pilot: per-run overhead and the cost of an empty run measured in VLI0                                                                                                 |
| li-company-posts-poller §14 Q2    | none     | later user choice: the Tier 1 interval and the pages `li_vendor_company_posts` affords, asked by VLI3                                                                 |
| li-company-posts-poller §14 Q3    | D2-Q058  | first-sight counts only on LinkedIn in v1                                                                                                                             |
| li-company-posts-poller §14 Q4    | D2-Q051  | the user verifies the harvestapi publisher before the vendor probe                                                                                                    |
| li-company-posts-poller §14 Q5    | D2-Q055  | reposts of member posts are member content: `linkedin_48h`                                                                                                            |
| li-notification-receiver §14 Q1   | none     | pilot: event types, payloads, retries, signature and handshake measured in LI0                                                                                        |
| li-notification-receiver §14 Q2   | none     | pilot: the subscription's tie to the administrator's token measured in LI0                                                                                            |
| li-notification-receiver §14 Q3   | none     | pilot: replies and reaction removal in notifications measured in LI0                                                                                                  |
| li-notification-receiver §14 Q4   | D2-Q034  | no counter increments: absolute observations only                                                                                                                     |
| li-notification-receiver §14 Q5   | D2-Q010  | edge hashing is the rule: `raw.items` holds the record as returned, minus identities                                                                                  |
| li-org-resolver §14 Q1            | none     | pilot: follower count and location from `linkedin-company-posts` measured in VLI0 (another Actor passes D2-Q051's screen first)                                       |
| li-org-resolver §14 Q2            | none     | later user choice: the refresh interval of registered pages against vendor cost, asked by VLI2 (the refresh loop itself: D2-Q032)                                     |
| li-org-resolver §14 Q3            | D2-Q033  | the resolver computes it through lang-dialect-id before it answers                                                                                                    |
| li-own-comments-fetcher §14 Q1    | none     | pilot: Comments API ordering, paging and reply expansion measured in LI0                                                                                              |
| li-own-comments-fetcher §14 Q2    | D2-Q055  | counted from `fetched_at`                                                                                                                                             |
| li-own-comments-fetcher §14 Q3    | D2-Q055  | member profile data is never stored, so the application shows none (the returned fields are recorded in LI0)                                                          |
| li-own-comments-fetcher §14 Q4    | D2-Q056  | purged with the member item at 48 hours                                                                                                                               |
| li-post-comments-fetcher §14 Q1   | D2-Q055  | `linkedin_48h`: member content on every route                                                                                                                         |
| li-post-comments-fetcher §14 Q2   | none     | pilot: Actor comment ids, timestamps and sort measured in VLI0                                                                                                        |
| li-post-comments-fetcher §14 Q3   | none     | pilot: whether a short run is a complete thread, measured in VLI0 (no deletion on absence otherwise, D2-Q062)                                                         |
| li-post-comments-fetcher §14 Q4   | D2-Q059  | no series for keyword-found LinkedIn posts unless a client asks                                                                                                       |
| li-post-comments-fetcher §14 Q5   | D2-Q010  | accepted: `raw.items` holds the record minus identities                                                                                                               |
| li-post-comments-fetcher §14 Q6   | D2-Q051  | the user verifies the harvestapi publisher before the vendor probe                                                                                                    |
| li-post-search §14 Q1             | none     | pilot: date window and order measured in VLI0                                                                                                                         |
| li-post-search §14 Q2             | D2-Q055  | yes: member-authored posts are `linkedin_48h`                                                                                                                         |
| li-post-search §14 Q3             | none     | pilot: active rules, items per rule and per-run overhead measured in VLI0                                                                                             |
| tg-bot-channel-receiver §14 Q1    | none     | pilot: `channel_post` under the lowest admin rights and `my_chat_member` measured in TG0                                                                              |
| tg-bot-channel-receiver §14 Q2    | none     | pilot: views and forwards in the Bot API measured in TG0                                                                                                              |
| tg-bot-channel-receiver §14 Q3    | none     | local: settled by TG1 in its build (proposed: two bots)                                                                                                               |
| tg-bot-channel-receiver §14 Q4    | D2-Q066  | a client-added channel is an `add` decision with a pre-allocated `source_id`, not a `discovery.hits` record                                                           |
| tg-bot-channel-receiver §14 Q5    | D2-Q054  | a dedicated class `telegram_bot`                                                                                                                                      |
| tg-bot-channel-receiver §14 Q6    | D2-Q052  | no: client-owned green sources are never read through an amber vendor                                                                                                 |
| tg-channel-posts-poller §14 Q1    | none     | pilot: Actor field names, views and forwards measured in VTG0                                                                                                         |
| tg-channel-posts-poller §14 Q2    | none     | pilot: whether `since` takes a time or a date, measured in VTG0                                                                                                       |
| tg-channel-posts-poller §14 Q3    | none     | pilot: the primary posts Actor from a one-week comparison on 50 channels, measured in VTG3 (publishers screened under D2-Q051)                                        |
| tg-channel-posts-poller §14 Q4    | D2-Q007  | `telegram:post:<chat_id>:<message_id>` on every route (chat ids, not usernames)                                                                                       |
| tg-channel-posts-poller §14 Q5    | D2-Q058  | first-sight counts only on Telegram in v1                                                                                                                             |
| tg-channel-resolver §14 Q1        | none     | pilot: Telemetrio stats path, parameters and channel allowance measured in VTG0                                                                                       |
| tg-channel-resolver §14 Q2        | none     | later user choice: buying a 20-post sample per one-signal candidate, asked by VTG2                                                                                    |
| tg-channel-resolver §14 Q3        | D2-Q051  | `TG_VENDOR_ROUTE` for Telemetrio search and stats, `TG_POSTS_ACTOR` for posts                                                                                         |
| tg-channel-resolver §14 Q4        | none     | pilot: the channel description in the stats response, measured in VTG0                                                                                                |
| tg-discussion-receiver §14 Q1     | none     | pilot: `message_thread_id` and `reply_to_message` measured in TG0                                                                                                     |
| tg-discussion-receiver §14 Q2     | none     | local: settled by TG2 in its build (proposed: privacy mode off)                                                                                                       |
| tg-discussion-receiver §14 Q3     | D2-Q041  | in the receiver's own `cursors` row `state`, which no other service reads                                                                                             |
| tg-discussion-receiver §14 Q4     | D2-Q010  | yes: the edge `author_ref` is accepted as given                                                                                                                       |
| tg-discussion-receiver §14 Q5     | D2-Q054  | the `telegram_bot` class; the bot count is TG1's                                                                                                                      |
| tg-message-search §14 Q1          | none     | pilot: per-request and per-keyword prices measured in VTG0                                                                                                            |
| tg-message-search §14 Q2          | D2-Q051  | split by role: `TG_VENDOR_ROUTE` (Telemetrio) and `TG_POSTS_ACTOR` (Apify)                                                                                            |
| tg-message-search §14 Q3          | D2-Q053  | whether mentions from qualifier-rejected channels reach any client                                                                                                    |
| tg-message-search §14 Q4          | none     | pilot: Telemetrio parameters, page size, rate limit and alpha terms measured in VTG0                                                                                  |
| tg-message-search §14 Q5          | none     | later user choice: the vendor route during an Iraq block (a `client_settings` row if per client, D2-Q043), asked by VTG1                                              |
| yt-channel-resolver §14 Q1        | D2-Q031  | yes: comment authors are never candidates, only `author_ref`                                                                                                          |
| yt-channel-resolver §14 Q2        | none     | pilot: `forHandle` cost and handle form measured in YT0                                                                                                               |
| yt-channel-resolver §14 Q3        | none     | pilot: the made-for-kids part and its cost measured in YT0                                                                                                            |
| yt-channel-resolver §14 Q4        | D2-Q042  | `ingest` (the `list` bucket is folded into it)                                                                                                                        |
| yt-channel-resolver §14 Q5        | D2-Q032  | no: each resolver refreshes its registered sources, so the loop stays                                                                                                 |
| yt-channel-resolver §14 Q6        | none     | local: settled by YT1 in its build                                                                                                                                    |
| yt-comments-fetcher §14 Q1        | none     | pilot: `textOriginal` for public comments measured in YT0                                                                                                             |
| yt-comments-fetcher §14 Q2        | D2-Q018  | client refresh at priority 1, not 3, label `refresh:<request_id>`; status values in D2-Q017                                                                           |
| yt-comments-fetcher §14 Q3        | D2-Q062  | the comment fetcher emits the video's deletion after a confirmed miss; the propagator cascades to its comments                                                        |
| yt-comments-fetcher §14 Q4        | D2-Q010  | one unscoped reference per platform; cross-owner rollups are blocked on the query side                                                                                |
| yt-comments-fetcher §14 Q5        | D2-Q056  | per-channel rollups follow 36 months; cross-channel rollups keep ten years under the carve-out                                                                        |
| yt-keyword-search §14 Q1          | none     | later user choice: the 20 to 30 launch priority terms and who signs off changes, asked by YT8                                                                         |
| yt-keyword-search §14 Q2          | none     | pilot: `relevanceLanguage=ku` against Sorani recall measured in YT0                                                                                                   |
| yt-keyword-search §14 Q3          | none     | later user choice: a quota extension after the pilot, asked by YT8 (aligning the run to the quota day is YT8's)                                                       |
| yt-pubsub-receiver §14 Q1         | none     | pilot: the hub's maximum and granted lease measured in YT0                                                                                                            |
| yt-pubsub-receiver §14 Q2         | none     | pilot: `hub.secret` signing measured in YT0                                                                                                                           |
| yt-pubsub-receiver §14 Q3         | none     | pilot: hub retries, deadline and subscribe limits measured in YT0                                                                                                     |
| yt-pubsub-receiver §14 Q4         | none     | local: settled by YT2 in its build (proposed: counted and ignored in v1)                                                                                              |
| yt-pubsub-receiver §14 Q5         | D2-Q011  | `first_sight` joins the closed kind list (its shape in D2-Q065)                                                                                                       |
| yt-replies-fetcher §14 Q1         | none     | pilot: `comments.list` order and page-token lifetime measured in YT0                                                                                                  |
| yt-replies-fetcher §14 Q2         | none     | pilot: `textOriginal` for public replies measured in YT0                                                                                                              |
| yt-replies-fetcher §14 Q3         | D2-Q011  | `post_ref` is the scheduler's object plus thread ids; status values D2-Q017, client refresh at priority 1 D2-Q018; the one-job rule after early stop is C11's         |
| yt-replies-fetcher §14 Q4         | D2-Q035  | yes: a deleted parent comment removes its replies                                                                                                                     |
| yt-replies-fetcher §14 Q5         | D2-Q062  | the reader that still lists those replies detects removals after a confirmed second miss                                                                              |
| yt-text-purger §14 Q1             | D2-Q056  | the 30-day clock covers titles, descriptions and channel text, not statistics (36 months); the 36-month clock runs from creation                                      |
| yt-text-purger §14 Q2             | D2-Q065  | yt-text-purger is a named producer of `refresh` jobs the fetchers accept (purge modes D2-Q035, `retention_audit` D2-Q045)                                             |
| yt-text-purger §14 Q3             | D2-Q056  | refresh for every client, not sold separately, so no entitlement column; the bucket share is quota-governor configuration                                             |
| yt-text-purger §14 Q4             | D2-Q039  | what raw-archiver keeps of YouTube payloads (text dropped at write time or rewritten daily)                                                                           |
| yt-uploads-reconciler §14 Q1      | none     | pilot: uploads order, the stop timestamp and scheduled videos measured in YT0                                                                                         |
| yt-uploads-reconciler §14 Q2      | none     | pilot: Shorts and live streams in the uploads playlist measured in YT0                                                                                                |
| yt-uploads-reconciler §14 Q3      | D2-Q065  | dormant channels weekly; channels without a working subscription daily with an ops alert                                                                              |
| yt-uploads-reconciler §14 Q4      | D2-Q014  | a `push_coverage_change` event with a reason such as `lease_lapsed`                                                                                                   |
| yt-video-details-fetcher §14 Q1   | D2-Q018  | the first sight of a new item at priority 1 on every tier                                                                                                             |
| yt-video-details-fetcher §14 Q2   | D2-Q065  | the `first_sight` job's fields and steps; series close on `deletions` in the scheduler                                                                                |
| yt-video-details-fetcher §14 Q3   | D2-Q060  | +24 h and +7 d anchor on creation time, not the stream's end; the live re-check interval is YT4's                                                                     |
| yt-video-details-fetcher §14 Q4   | D2-Q056  | per-video observations expire 36 months after creation; only cross-channel rollups keep ten years                                                                     |
| yt-web-search-bridge §14 Q1       | none     | pilot: `OR` and exact-phrase Arabic operators on Mojeek and Perplexity measured in W0                                                                                 |
| yt-web-search-bridge §14 Q2       | none     | later user choice: the bridge's share of the 60,000 monthly queries (its sub-counter, D2-Q037), asked by YT9                                                          |
| yt-web-search-bridge §14 Q3       | none     | local: settled by YT9 in its build (after W0)                                                                                                                         |
| yt-web-search-bridge §14 Q4       | none     | local: settled by YT9 in its build (promotion thresholds)                                                                                                             |
| news-article-extractor §14 Q1     | D2-Q022  | yes, within the 7 days and derived values only; counsel confirms before G2                                                                                            |
| news-article-extractor §14 Q2     | D2-Q068  | how `ai-input = no` binds analysis of the excerpt                                                                                                                     |
| news-article-extractor §14 Q3     | D2-Q022  | the extractor owns `cache/news/` and passes `text_full_ref`                                                                                                           |
| news-article-extractor §14 Q4     | none     | pilot: `news_urls` row lifetime measured in G2 (owner N6)                                                                                                             |
| news-comments-fetcher §14 Q1      | none     | counsel: Disqus API terms for forums we do not administer (with the rate limit and price), before N8                                                                  |
| news-comments-fetcher §14 Q2      | none     | pilot: the share of Iraqi sites on Disqus measured in N0                                                                                                              |
| news-comments-fetcher §14 Q3      | D2-Q040  | `news_sites` gains the Disqus fields (identifier template); an optional extractor field is N6's                                                                       |
| news-comments-fetcher §14 Q4      | D2-Q010  | the author-reference key is not rotated except after a compromise (a new key for new data only)                                                                       |
| news-dedup §14 Q1                 | D2-Q022  | `news.dedup` kept and consumed by store-writer; no wait in normalize-item                                                                                             |
| news-dedup §14 Q2                 | none     | pilot: Hamming distance, overlap, excerpt length and window measured in G2 (owner N7)                                                                                 |
| news-dedup §14 Q3                 | D2-Q036  | keep the ledger sweep: copies get `duplicate_canonical` and their own `url_key`                                                                                       |
| news-dedup §14 Q4                 | D2-Q048  | the news story is a dimension of the aggregate grain                                                                                                                  |
| news-feed-poller §14 Q1           | none     | pilot: the publishing-rate to interval mapping measured in G2 (owner N3)                                                                                              |
| news-feed-poller §14 Q2           | none     | local: settled by N3 as a later optimisation (proposed: WebSub where a site declares a hub)                                                                           |
| news-feed-poller §14 Q3           | none     | local: settled by N3 in its build (proposed: emit)                                                                                                                    |
| news-homepage-differ §14 Q1       | none     | pilot: link floor, section cap and anchor length measured in N0                                                                                                       |
| news-homepage-differ §14 Q2       | none     | pilot: sites with neither feed nor sitemap, and the Cloudflare share, measured in N0                                                                                  |
| news-homepage-differ §14 Q3       | none     | local: settled by N5 in its build (proposed: in the cursor's `sections`)                                                                                              |
| news-robots-checker §14 Q1        | D2-Q068  | whether `search = no` is a stop                                                                                                                                       |
| news-robots-checker §14 Q2        | D2-Q068  | how `ai-input = no` binds analysis of excerpts and of the 7-day cache                                                                                                 |
| news-robots-checker §14 Q3        | none     | pilot: the RSL mapping and RSL or pay-per-crawl hosts measured in N0                                                                                                  |
| news-robots-checker §14 Q4        | none     | pilot: refresh margin and unreachable-file limit measured in G2 (owner N1)                                                                                            |
| news-robots-checker §14 Q5        | none     | later user choice: joining Cloudflare's pay-per-crawl (a flagged vendor), asked by N1                                                                                 |
| news-site-resolver §14 Q1         | none     | later user choice: the venture name and contact mailbox for `CRAWLER_USER_AGENT`, asked by N0 (before any real crawl)                                                 |
| news-site-resolver §14 Q2         | D2-Q040  | a control-plane table keyed by `source_id`, written only by news-site-resolver                                                                                        |
| news-site-resolver §14 Q3         | none     | pilot: the hot-tier publishing-rate threshold measured in G2 (owner N2)                                                                                               |
| news-site-resolver §14 Q4         | none     | later user choice: regional outlets on a client seed list accepted or sent to review, asked by N2                                                                     |
| news-sitemap-poller §14 Q1        | none     | local: settled by N4 in its build (proposed: here)                                                                                                                    |
| news-sitemap-poller §14 Q2        | none     | pilot: news sitemaps and reliable `lastmod` measured in N0                                                                                                            |
| news-sitemap-poller §14 Q3        | none     | pilot: long news sitemaps usable for backfill measured in N0                                                                                                          |
| search-hit-router §14 Q1          | D2-Q037  | only keys a resolver accepts: profile URLs as Instagram accounts; short links stay `web`                                                                              |
| search-hit-router §14 Q2          | none     | pilot: re-route window, parking period and news-like rule measured in G2 (owner W3)                                                                                   |
| search-hit-router §14 Q3          | D2-Q031  | the `discovery.hits/v1` field set (`article.urls/v1`: D2-Q036)                                                                                                        |
| search-hit-router §14 Q4          | D2-Q037  | no feedback loop in v1; yield is measured from qualifier outcomes                                                                                                     |
| web-commoncrawl-scanner §14 Q1    | none     | pilot: index API or columnar reads measured in W0                                                                                                                     |
| web-commoncrawl-scanner §14 Q2    | none     | pilot: per-capture language and the `.iq` zone list measured in W0                                                                                                    |
| web-commoncrawl-scanner §14 Q3    | D2-Q031  | the `discovery.hits/v1` field set; cap, weights and accept-rate target measured in G2                                                                                 |
| web-commoncrawl-scanner §14 Q4    | none     | local: settled by W5 in a later version                                                                                                                               |
| web-commoncrawl-scanner §14 Q5    | none     | local: settled by W5 in its build                                                                                                                                     |
| web-gdelt-poller §14 Q1           | none     | pilot: GDELT DOC API specifics measured in W0                                                                                                                         |
| web-gdelt-poller §14 Q2           | none     | pilot: mixed Arabic and Latin OR queries measured in W0                                                                                                               |
| web-gdelt-poller §14 Q3           | none     | answered: search-hit-router §5.4 L89 reads GDELT's optional `hints`                                                                                                   |
| web-gdelt-poller §14 Q4           | none     | counsel: GDELT attribution in the provenance statement, before G4                                                                                                     |
| web-gdelt-poller §14 Q5           | none     | pilot: an Arabic or Iraqi-source second pass measured in W0                                                                                                           |
| web-search-mojeek §14 Q1          | none     | pilot: Mojeek API specifics measured in W0                                                                                                                            |
| web-search-mojeek §14 Q2          | none     | pilot: a Sorani language boost measured in W0                                                                                                                         |
| web-search-mojeek §14 Q3          | none     | local: settled by W2 in its build (with W1: the second run's variant set)                                                                                             |
| web-search-mojeek §14 Q4          | D2-Q037  | no: the bridge queries the engines itself; `site_search` jobs are dropped                                                                                             |
| web-search-perplexity §14 Q1      | none     | pilot: `ckb` acceptance measured in W0                                                                                                                                |
| web-search-perplexity §14 Q2      | none     | local: settled by W1 in its build (with W2: the second run's variant set)                                                                                             |
| web-search-perplexity §14 Q3      | none     | pilot: date filter against no filter compared in G2 (owner W1)                                                                                                        |
| web-search-perplexity §14 Q4      | D2-Q044  | the attributes take the names of the one `keywords` column list                                                                                                       |
| web-search-perplexity §14 Q5      | D2-Q008  | `search_response` is an archive-only kind that normalize-item skips by rule                                                                                           |
| aggregator §14 Q1                 | none     | local: settled by C15 in its build against the pinned ClickHouse release                                                                                              |
| aggregator §14 Q2                 | D2-Q048  | what reach means for clients (frozen at first sight needs a column on `hits`, D2-Q047)                                                                                |
| aggregator §14 Q3                 | D2-Q048  | whether the grain splits posts and comments                                                                                                                           |
| aggregator §14 Q4                 | none     | pilot: hourly-grain row growth measured in G2 (owner C15)                                                                                                             |
| aggregator §14 Q5                 | D2-Q048  | `mixed` counted apart from the negative share; topic ids namespaced by taxonomy                                                                                       |
| alert-evaluator §14 Q1            | D2-Q025  | yes: the alert tables the apps read join CONVENTIONS                                                                                                                  |
| alert-evaluator §14 Q2            | none     | local: settled by A5 in its build (with C15; a minute-grain table would be additive)                                                                                  |
| alert-evaluator §14 Q3            | D2-Q035  | closed reasons and `item_id` in `deletions/v1`; the watch set is in the purge registry                                                                                |
| alert-evaluator §14 Q4            | none     | later user choice: who approves the alert defaults the pilot gives, asked by A5                                                                                       |
| alert-evaluator §14 Q5            | none     | counsel: `keyword_first_seen` alerts for government clients, before A5                                                                                                |
| analysis-entities §14 Q1          | D2-Q023  | `model_versions` and keys with re-runs side by side (a KB release as a version or in place)                                                                           |
| analysis-entities §14 Q2          | none     | later user choice: who curates the global KB and whether clients add global entries, asked by A3                                                                      |
| analysis-entities §14 Q3          | none     | counsel: who counts as a public figure for `person_public`, before A3                                                                                                 |
| analysis-entities §14 Q4          | none     | local: settled by A3 in its build                                                                                                                                     |
| analysis-entities §14 Q5          | none     | local: settled by A3 in its build (GPU or API is A1 to A4's, build plan L65)                                                                                          |
| analysis-entities §14 Q6          | none     | local: settled by A1 in a later version                                                                                                                               |
| analysis-entities §14 Q7          | D2-Q068  | training and evaluation use of platform content                                                                                                                       |
| analysis-media §14 Q1             | none     | local: settled by A4 in its build, on its evaluation sets                                                                                                             |
| analysis-media §14 Q2             | D2-Q068  | storing platform media, and YouTube thumbnails only                                                                                                                   |
| analysis-media §14 Q3             | D2-Q039  | `media/<sha256>` only through raw-archiver's endpoint with `.refs`, which the purge reads                                                                             |
| analysis-media §14 Q4             | D2-Q023  | a second input deferred to A4 with an additive field                                                                                                                  |
| analysis-media §14 Q5             | none     | local: settled by A4 in its build (build plan L65)                                                                                                                    |
| analysis-media §14 Q6             | none     | pilot: frame interval, caps and tier rules measured in A4                                                                                                             |
| analysis-media §14 Q7             | none     | later user choice: who uploads and approves logo sets, asked by D3 (the `brand_assets` writer is D3's, D2-Q025)                                                       |
| analysis-sentiment §14 Q1         | none     | local: settled by A1 in its build, on its evaluation set                                                                                                              |
| analysis-sentiment §14 Q2         | none     | local: settled by A1 in its build, on its evaluation set                                                                                                              |
| analysis-sentiment §14 Q3         | D2-Q068  | training and evaluation use of platform and vendor data, and for how long                                                                                             |
| analysis-sentiment §14 Q4         | none     | later user choice: the annotation tool and annotators, asked by A0                                                                                                    |
| analysis-sentiment §14 Q5         | none     | later user choice: GPU or model API and full-model coverage (a cost lever), asked by A1                                                                               |
| analysis-sentiment §14 Q6         | D2-Q023  | OCR second pass deferred to A4; the priority lane for tier-1 sources                                                                                                  |
| analysis-sentiment §14 Q7         | D2-Q031  | the hit field is `matched_term`; `lang` codes and the Latin-script flag in D2-Q028                                                                                    |
| analysis-topics §14 Q1            | none     | local: settled by A2 in its build, on its evaluation set                                                                                                              |
| analysis-topics §14 Q2            | none     | local: settled by A2 in its build                                                                                                                                     |
| analysis-topics §14 Q3            | none     | local: settled by A2 in its build, on its evaluation set                                                                                                              |
| analysis-topics §14 Q4            | none     | later user choice: who staffs the weekly review and whether a client approves its own nodes, asked by A2                                                              |
| analysis-topics §14 Q5            | D2-Q023  | OCR and transcript text deferred to A4 with an additive field                                                                                                         |
| analysis-topics §14 Q6            | none     | later user choice: separate default taxonomies for government clients, asked by A2                                                                                    |
| analysis-topics §14 Q7            | D2-Q068  | training use of platform content                                                                                                                                      |
| backfill-orchestrator §14 Q1      | D2-Q020  | yes: Facebook groups go to fb-group-posts-poller in the route table                                                                                                   |
| backfill-orchestrator §14 Q2      | D2-Q020  | the orchestrator is the only writer of `backfill_status`                                                                                                              |
| backfill-orchestrator §14 Q3      | none     | pilot: backfill deadline and per-source X read cap measured in G3-x (owner C10)                                                                                       |
| backfill-orchestrator §14 Q4      | none     | local: settled by C10 in its build (proposed: yes, in tier order)                                                                                                     |
| comment-decay-scheduler §14 Q1    | D2-Q017  | `jobs.completed`, written only by the SDK job wrapper                                                                                                                 |
| comment-decay-scheduler §14 Q2    | D2-Q019  | yes: armed after 5 stored comments or the +24 h step                                                                                                                  |
| comment-decay-scheduler §14 Q3    | none     | local: settled by C11 in its build (series tuning after G2, build plan L65)                                                                                           |
| comment-decay-scheduler §14 Q4    | D2-Q018  | gating on every tag: hot extras stop at 80% on X and YouTube too; stretching on amber only                                                                            |
| comment-decay-scheduler §14 Q5    | none     | later user choice: a per-post X reply read cap after the pilot, asked by C11                                                                                          |
| comment-decay-scheduler §14 Q6    | D2-Q058  | first-sight counts only on X, LinkedIn and Telegram in v1                                                                                                             |
| deletion-propagator §14 Q1        | D2-Q069  | backups and snapshots inside the deletion deadlines                                                                                                                   |
| deletion-propagator §14 Q2        | D2-Q035  | one `deletions/v1` shape for every producer; tombstones written by the propagator, read by store-writer                                                               |
| deletion-propagator §14 Q3        | D2-Q069  | the registry decision for an author request that matches a registered source                                                                                          |
| deletion-propagator §14 Q4        | D2-Q004  | author-scope deletions keyed by `author_ref`, a named exception                                                                                                       |
| deletion-propagator §14 Q5        | none     | pilot: forced-merge and rewrite cost at full scale measured in G4 (owner C13)                                                                                         |
| deletion-propagator §14 Q6        | D2-Q069  | SLAs for non-X `platform_sync` and `legal` deletions                                                                                                                  |
| keyword-matcher §14 Q1            | D2-Q047  | `hits` holds item hits only; discovery hits stay on the topic                                                                                                         |
| keyword-matcher §14 Q2            | D2-Q031  | the `discovery.hits/v1` fields, `candidate_pending` included (how the poster id reaches keyword-matcher: with D2-Q010)                                                |
| keyword-matcher §14 Q3            | D2-Q031  | yes: comment hits on individuals are item hits with `author_ref`, never candidates                                                                                    |
| keyword-matcher §14 Q4            | D2-Q053  | which clients may see Meta-origin items                                                                                                                               |
| keyword-matcher §14 Q5            | none     | local: settled by C5 in its build                                                                                                                                     |
| keyword-matcher §14 Q6            | none     | pilot: clitic and suffix coverage measured in G2's keyword-hit sample (owner C5)                                                                                      |
| lang-dialect-id §14 Q1            | D2-Q028  | Python, with the fold also in TypeScript                                                                                                                              |
| lang-dialect-id §14 Q2            | D2-Q028  | Kurmanji stays `other` in v1, a documented gap; label after the pilot                                                                                                 |
| lang-dialect-id §14 Q3            | D2-Q028  | a script flag for Arabic in Latin letters; no Arabizi class or transliteration in v1                                                                                  |
| lang-dialect-id §14 Q4            | D2-Q028  | top class and confidence on items.normalized; vector in the service's log                                                                                             |
| lang-dialect-id §14 Q5            | none     | later user choice: who labels the Iraqi sample and its size, asked by A0 (release thresholds from it, C3)                                                             |
| normalize-item §14 Q1             | D2-Q010  | hashed: only registered sources keep a name downstream                                                                                                                |
| normalize-item §14 Q2             | D2-Q022  | news-article-extractor owns the cache and passes `text_full_ref`                                                                                                      |
| normalize-item §14 Q3             | none     | local: settled by C4 in its build                                                                                                                                     |
| normalize-item §14 Q4             | none     | pilot: peak records a second and worker count measured in G2 (owner C4)                                                                                               |
| poster-resolver §14 Q1            | D2-Q045  | yes: `poster_profiles` is the one shared cache                                                                                                                        |
| poster-resolver §14 Q2            | D2-Q032  | the resolvers answer on `poster.profiles` themselves, so each archives its own raw `profile` record (D2-Q008)                                                         |
| poster-resolver §14 Q3            | D2-Q028  | an HTTP call to lang-dialect-id, no in-process classifier; a batch form is C3's                                                                                       |
| poster-resolver §14 Q4            | D2-Q033  | one shared reference table read through the SDK                                                                                                                       |
| qualifier §14 Q1                  | none     | later user choice: client admins answering review cards, asked by D3                                                                                                  |
| qualifier §14 Q2                  | D2-Q033  | one shared reference table read through the SDK                                                                                                                       |
| qualifier §14 Q3                  | none     | later user choice: queued candidates and their position in the client app, asked by D3                                                                                |
| quota-governor §14 Q1             | none     | pilot: YouTube bucket sizes and reset time measured in G3-youtube (owner C1)                                                                                          |
| quota-governor §14 Q2             | D2-Q018  | gating on every tag, green included; stretching on amber only                                                                                                         |
| quota-governor §14 Q3             | D2-Q050  | yes: government data on X only when `x_plan` and the client's declared end user allow                                                                                 |
| quota-governor §14 Q4             | none     | local: settled by C1 in its build (proposed: the upper price)                                                                                                         |
| quota-governor §14 Q5             | none     | local: settled by C1 in its build                                                                                                                                     |
| raw-archiver §14 Q1               | D2-Q039  | raw-archiver owns the `raw/` layout; the batch width is an SDK constant                                                                                               |
| raw-archiver §14 Q2               | D2-Q039  | no `raw.replay`: replay is a `replay` job reading through raw-archiver's read API                                                                                     |
| raw-archiver §14 Q3               | D2-Q069  | how long envelope-only archive files outlive the text clock (the YouTube clock with D2-Q056)                                                                          |
| raw-archiver §14 Q4               | none     | pilot: `raw.items` topic retention measured in G2 (owner C2)                                                                                                          |
| registry-writer §14 Q1            | D2-Q045  | `registry_audit` joins CONVENTIONS: append-only, with a separate outbox                                                                                               |
| registry-writer §14 Q2            | D2-Q020  | yes: a re-added source returns as `updated` with its `source_id`                                                                                                      |
| registry-writer §14 Q3            | D2-Q043  | yes: a priority-listed source is tier 1 regardless of followers                                                                                                       |
| registry-writer §14 Q4            | D2-Q013  | on `registry.decisions`: one type field and a closed type list                                                                                                        |
| retention-purger §14 Q1           | D2-Q069  | who verifies an author's identity                                                                                                                                     |
| retention-purger §14 Q2           | D2-Q035  | the one resurrection guard (tombstones read by store-writer), not a normalize-item check                                                                              |
| retention-purger §14 Q3           | D2-Q054  | `telegram_bot` for bot content; web results stay `news_excerpt`                                                                                                       |
| retention-purger §14 Q4           | D2-Q069  | the `meta_on_request` grace period and how long audit records are kept                                                                                                |
| source-health-canary §14 Q1       | D2-Q013  | the fields of the `health_change` decision                                                                                                                            |
| source-health-canary §14 Q2       | D2-Q021  | registry-writer enforces it when it applies a route-wide change                                                                                                       |
| source-health-canary §14 Q3       | none     | pilot: targets per route and `CANARY_MIN_SAMPLES` measured in G2 (owner C12)                                                                                          |
| source-health-canary §14 Q4       | D2-Q021  | yes: vendor key or plan errors `degraded` (may fall back); a platform 401 or 403 `blocked`                                                                            |
| store-writer §14 Q1               | D2-Q047  | `hits` (item hits only) and `keywords_dim` in store-writer's column list; the TTL columns in `retention_classes` (D2-Q045)                                            |
| store-writer §14 Q2               | D2-Q029  | one node in staging, a replicated pair before production                                                                                                              |
| store-writer §14 Q3               | D2-Q056  | no: LinkedIn member `analysis` rows go with the item at 48 hours                                                                                                      |
| store-writer §14 Q4               | none     | pilot: bytes per row measured in G2 (owner C6); the ceiling per class is D2-Q056's                                                                                    |
| store-writer §14 Q5               | D2-Q034  | the `item.metrics` field list; provenance and `retention_class` yes (D2-Q003)                                                                                         |
