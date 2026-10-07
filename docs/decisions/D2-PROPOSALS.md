# D2 proposals · Decisions and contract freeze

D2 phase 1 · 7 Oct 2026 · Status: **proposals for the user; nothing is decided.** The orchestrator puts these decisions to the user. Phase 2, a fresh session, writes the ADRs, CONVENTIONS v1.1 and `docs/decisions/DEFERRED.md` from the answers. Until a decision is answered, a build session that meets one of its entries stops and asks, as `docs/contracts/CONFLICTS.md` says.

`docs/decisions/D2-SUMMARY.md` lists only the decisions that need the user, with one-line options, and the technical decisions as a table to object to.

## What this covers

Every input the D2 brief and `/decide-session D2` name, each placed in exactly one decision or marked "no decision needed" with the reason:

- the 118 entries of `docs/contracts/CONFLICTS.md` (CF-001 to CF-118) and the 113 of `docs/contracts/CONFLICTS-ASSUMPTIONS.md` (AU-001 to AU-113), read with `docs/contracts/INVENTORY.md`;
- the nine decisions proposed in `docs/prds/README.md` (L176 to L186), written RD-1 to RD-9 below;
- the thirteen foundation choices in `build-plan/README.md` (L47 to L63), written FC-01 to FC-13;
- the 365 open questions of `docs/prds/OPEN-QUESTIONS.md` (section 14 of the 86 PRDs), written `<service> §14 Qn`;
- the D1 review notes left open for D2 (`docs/reviews/D1.md`, notes 8 to 13, 16 and 17), written RN-08 to RN-17.

Appendix A maps every CF and AU entry to its decision; Appendix B does the same for the README decisions, the foundation choices and the review notes; Appendix C places every open question.

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

| Id                  | Decision                                                                                                                | Class     | Settles             | First sessions blocked                                                                             |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------- | ------------------- | -------------------------------------------------------------------------------------------------- |
| [D2-Q001](#d2-q001) | How D2's decisions apply to the twenty "already approved" PRDs                                                          | user      | 1 CF/AU             | F2 first, then every session whose PRD is on the list: FB6, FB2, FB3, FB4, IG2                     |
| [D2-Q002](#d2-q002) | Message metadata and schema versioning                                                                                  | technical | FC-04; 1 CF/AU      | F2 first, F4, F6, then C6, C7, C8                                                                  |
| [D2-Q003](#d2-q003) | Provenance and `retention_class` on every message                                                                       | technical | 1 CF/AU             | F2, F4, F6, then C5, C6, C8                                                                        |
| D2-Q004             | (missing)                                                                                                               |           |                     |                                                                                                    |
| [D2-Q005](#d2-q005) | The `raw.items` message: shape, envelope fields, and why a record was read                                              | technical | 5 CF/AU             | F2, F4, F6, C2, C4, then every `raw.items` producer                                                |
| D2-Q006             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q007             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q008             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q009             | (missing)                                                                                                               |           |                     |                                                                                                    |
| [D2-Q010](#d2-q010) | Individuals' identities: one keyed reference, and where it is computed                                                  | user      | 4 CF/AU             | F2, F4, F6, C2, C4, C6                                                                             |
| D2-Q011             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q012             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q013             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q014             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q015             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q016             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q017             | (missing)                                                                                                               |           |                     |                                                                                                    |
| [D2-Q018](#d2-q018) | Budget priorities and modes (README decision 2)                                                                         | user      | RD-2; 4 CF/AU       | F5, C1, C11, then YT4, YT5, YT6                                                                    |
| [D2-Q019](#d2-q019) | Early stop of a comment series (README decision 3)                                                                      | technical | RD-3; 1 CF/AU       | C11, then FB5, VFB3, IG6, VIG2, VTT5                                                               |
| D2-Q020             | (missing)                                                                                                               |           |                     |                                                                                                    |
| [D2-Q021](#d2-q021) | A platform 401 or 403, fallback, and the government exclusion (README decision 5)                                       | user      | RD-5; 2 CF/AU       | F3, F4, F5, C7, C12, then every green fetcher                                                      |
| [D2-Q022](#d2-q022) | News: the `news.dedup` topic, the per-host gate and the 7-day full-text cache (README decision 6)                       | technical | RD-6; 6 CF/AU       | F2, F4 and F5, C4, C5, C6, C13                                                                     |
| D2-Q023             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q024             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q025             | (missing)                                                                                                               |           |                     |                                                                                                    |
| [D2-Q026](#d2-q026) | Kafka client libraries for the two SDKs                                                                                 | technical | FC-05               | F4, F6                                                                                             |
| [D2-Q027](#d2-q027) | Where the platform runs: the cluster and object storage                                                                 | user      | FC-06, FC-07        | I1, then C2, I2, E2 and the gates G2 to G4; the account itself is something only the user can open |
| [D2-Q028](#d2-q028) | lang-dialect-id in Python                                                                                               | technical | FC-08; 3 CF/AU      | C3, F7, F6, then C8, VLI2, A1                                                                      |
| [D2-Q029](#d2-q029) | ClickHouse topology and the three environments                                                                          | user      | FC-09, FC-12        | I1, F8, E2, G2, G4                                                                                 |
| [D2-Q030](#d2-q030) | Ratify the tooling, local stack and dependency policy F1 built                                                          | technical | FC-10, FC-11, FC-13 | F2, every session                                                                                  |
| D2-Q031             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q032             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q033             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q034             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q035             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q036             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q037             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q038             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q039             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q040             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q041             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q042             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q043             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q044             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q045             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q046             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q047             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q048             | (missing)                                                                                                               |           |                     |                                                                                                    |
| [D2-Q049](#d2-q049) | What `tier` holds, and what "push" means                                                                                | technical | 2 CF/AU             | F3, F5, C1, C7, C9, then TT1                                                                       |
| D2-Q050             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q051             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q052             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q053             | (missing)                                                                                                               |           |                     |                                                                                                    |
| [D2-Q054](#d2-q054) | Retention classes for the routes CONVENTIONS gives none: TikTok Display, the Telegram bot, web-search results           | user      | 1 CF/AU             | F3, F8, C6, C14, then TT1, TG1                                                                     |
| [D2-Q055](#d2-q055) | LinkedIn data: which class holds what, and the 24-hour and six-week rules                                               | user      | 2 CF/AU             | F3, F8, C4, C6, C14, then LI1                                                                      |
| [D2-Q056](#d2-q056) | How long derived data lives: ten years, YouTube's 36 months, LinkedIn's 48 hours, and what YouTube's 30-day rule covers | user      | 2 CF/AU             | F3, F8, C6, C13, C14, C15                                                                          |
| D2-Q057             | (missing)                                                                                                               |           |                     |                                                                                                    |
| [D2-Q058](#d2-q058) | Engagement-count refreshes on X, LinkedIn, Telegram and Facebook groups                                                 | user      | 2 CF/AU             | C11, VTG3, LI1, VLI3, X1, X3                                                                       |
| D2-Q059             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q060             | (missing)                                                                                                               |           |                     |                                                                                                    |
| [D2-Q061](#d2-q061) | The Disqus comment series                                                                                               | technical | 3 CF/AU             | C11, N2, N8                                                                                        |
| [D2-Q062](#d2-q062) | When a missing post or comment becomes a deletion                                                                       | technical | 2 CF/AU             | F4, C13, then FB4, FB5, VFB3, YT4                                                                  |
| [D2-Q063](#d2-q063) | Which X keyword rules go on the filtered stream                                                                         | technical | 1 CF/AU             | X1, X4                                                                                             |
| D2-Q064             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q065             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q066             | (missing)                                                                                                               |           |                     |                                                                                                    |
| D2-Q067             | (missing)                                                                                                               |           |                     |                                                                                                    |
| [D2-Q068](#d2-q068) | Using platform content for models and media: training and evaluation data, Content Signals, stored media                | user      |                     | A0 first, then A1, A2, A3, A4, N1                                                                  |
| [D2-Q069](#d2-q069) | Legal policies the deletion and audit paths need: author requests, deadlines, backups, audit retention, the X rules     | user      | 1 CF/AU             | C13, C14, X7, I1, D3, then G4                                                                      |
| [D2-Q070](#d2-q070) | One editorial pass: the documents that disagree with themselves                                                         | technical | RN-17; 2 CF/AU      | F2 first, then F5, C1, C2, C4, C5                                                                  |

## Group 0 · The ground rule

### D2-Q001 · How D2's decisions apply to the twenty "already approved" PRDs

- **Class:** user
- **Settles:** CF-116
- **Blocks:** F2 first (it builds the contracts package from the ADRs and must know whether an approved PRD's example or the ADR wins), then every session whose PRD is on the list: FB6, FB2, FB3, FB4, IG2, VTT1, VTT2, X1, VLI1, VLI2, VTG1, VTG2, YT8, YT9, N2, W1, C4, C8, C9, C7
- **Depends on:** none. It comes first because every other recommendation in this document assumes its answer.

**Context.** CONVENTIONS L282 lists twenty PRDs "to stay consistent with (already approved; do not rewrite)": fb-page-search, fb-page-feed-poller, fb-backfill, fb-reactions-fetcher, ig-hashtag-search, tt-keyword-search, tt-hashtag-feed-poller, x-recent-search, li-post-search, li-org-resolver, tg-message-search, tg-channel-resolver, yt-keyword-search, yt-web-search-bridge, news-site-resolver, web-search-perplexity, normalize-item, poster-resolver, qualifier and registry-writer. CONVENTIONS L278 also makes fb-page-feed-poller the model every rotation scheduler follows "exactly". D1 found these PRDs on one side of many entries (CF-116):

- Some depart from CONVENTIONS itself. fb-page-feed-poller, fb-backfill, fb-page-search and x-recent-search name the job type `reason`, not `kind` (CF-077 b). fb-page-search keys its queue on `keyword_id` (CF-087 c). fb-reactions-fetcher expects `refresh_24h` and `refresh_7d` kinds (CF-081 b). ig-hashtag-search charges `ig_graph_<client_id>` (CF-099 b). tt-keyword-search, tt-hashtag-feed-poller and tg-message-search backfill on their own first run (CF-088 c). web-search-perplexity and yt-web-search-bridge publish results on `search.results` instead of items on `raw.items` (CF-110 b). registry-writer spells `tier_change` (CF-098 a).
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

**Context.** The PRDs version their messages three ways (CF-001): a string `schema` such as `"items.normalized/v1"` beside `message_id`, `produced_at` and a `producer {service, version, job_id}` block (`normalize-item §6.2 L95-L98`, `keyword-matcher §6.2 L99-L102`, the four analysis services); a string `schema` with a flat `service` field (news-dedup, news-robots-checker, news-site-resolver, tg-channel-resolver, tg-message-search, search-hit-router, web-commoncrawl-scanner, the web engines, the two `jobs.completed` writers); an integer `schema_version` (`poster-resolver §6.2 L89`, `qualifier §6.2 L84`, `registry-writer §6.2 L95`); or nothing at all (every `raw.items` envelope, `item.metrics`, `deletions`, the news pollers' `article.urls`, the resolvers' `poster.profiles`, several `discovery.hits`). Two consumers branch on the string: store-writer parks any message whose `schema` it does not know (`store-writer §5.2 L46`) and search-hit-router parks a message without `schema = search.results/v1` (`search-hit-router §5.2 L55`), so as written store-writer would park every `item.metrics` and `source.events` message. CONVENTIONS puts "topic schemas" in listening-sdk (L12) but names no field. The build plan's foundation choice is "additive changes within a version; a breaking change is a new version with a dual-publish window" (FC-04), and `.claude/rules/contracts.md` already points to F2's `docs/contracts/VERSIONING.md`.

**Options**

1. **A `schema` string on every message, with one metadata block, and the build plan's versioning rule (recommended).** Every message on every topic and job queue carries `schema: "<topic>/v<n>"`, `message_id` (ULID), `produced_at`, and `producer {service, version, job_id}`; the SDK stamps all four, so no service writes them by hand. Versioning: a change that only adds an optional field stays in the version; anything else (a removed or renamed field, a changed type or meaning) is a new version, published beside the old one for a dual-publish window long enough for every consumer to move (F2's `VERSIONING.md` sets its length), with consumers parking unknown versions as store-writer does. Consequences: the majority form, and the one the two branching consumers already read; three approved PRDs (poster-resolver, qualifier, registry-writer) change `schema_version` to `schema` under D2-Q001; a message archived to object storage still says what it is, without its Kafka headers.
2. **An integer `schema_version` on every message, the topic implied by the topic name, with `message_id`, `produced_at` and a flat `service`.** Consequences: shorter, but a message copied out of its topic (the raw archive, a DLQ, a replay) no longer says what it is, and store-writer and search-hit-router change.
3. **The version in a Kafka header set by the SDK, nothing in the body.** Consequences: clean bodies, but the archive and the DLQ lose the version unless they copy headers, and every PRD example changes.

**Why the recommendation.** It is what most producers and both branching consumers already do, it survives archiving and replay, and the SDK can stamp it in one place.

**Phase 2 records.** ADR "Message metadata and schema versioning" (Applies to: all). CONVENTIONS v1.1, event bus section (L14 to L29): the four metadata fields and the versioning rule; F2 writes `VERSIONING.md` from it.

### D2-Q003 · Provenance and `retention_class` on every message

- **Class:** technical (the rule itself is the user's: CLAUDE.md and the F2 brief require it)
- **Settles:** CF-002
- **Blocks:** F2, F4, F6, then C5, C6, C8, A1, A2, A3, A4, N3, N4, N5, W1, W2, W3, W4, W5, FB6, IG1, IG2, X1, VLI2, YT9
- **Depends on:** D2-Q002

**Context.** "Every item carries provenance (route class, vendor, service, fetch time)" (`CONVENTIONS L115`); the repository's non-negotiables say "Every output carries provenance (route, vendor, service, fetched_at) and `retention_class`" (`CLAUDE.md`), and F2's brief says every topic payload does. The PRDs miss it or rename it (CF-002): the news pollers' `article.urls` carry `found_at` and no `fetched_at`; search-hit-router's `article.urls` carries `first_seen_at` and no route, vendor, fetch time or class; keyword-matcher's hit has no `fetched_at`; the analysis messages carry `item_fetched_at`; `poster.profiles` from poster-resolver and li-org-resolver carry `resolved_at`; `item.metrics` carries `observed_at` flat or inside an `observation` object; the web engines' raw envelopes and yt-web-search-bridge's results have no class. Which `service` is meant also varies: keyword-matcher writes the fetching service beside `producer.service`, the analysis messages keep only the analysis service, poster-resolver writes `"service":"poster-resolver"` plus `"resolver"`, and ig-account-resolver nests all four as `provenance {route, vendor, service, fetched_at}` (`ig-account-resolver §6.2 L119-L120`).

**Options**

1. **One nested `provenance {route, vendor, service, fetched_at}` object and a top-level `retention_class` on every message that carries or derives from platform data (recommended).** `provenance.service` is always the service that fetched the data and `fetched_at` the time it was fetched; `producer.service` (D2-Q002) is the service that emitted this message. The SDK copies `provenance` and `retention_class` from the input record to every derived message (normalized item, hit, analysis, metrics, profile, deletion), so no service rebuilds them. The `raw.items` envelope carries the same object (D2-Q005). The data topics are `raw.items`, `items.normalized`, `item.hits`, `discovery.hits`, `poster.profiles`, `item.metrics`, `items.analysis`, `article.urls`, `search.results`, `deletions` and `news.dedup`; control topics (`registry.decisions`, `source.events`, `crawl.policies`, `jobs.completed`, the job queues) carry `producer` only. Consequences: one type, one helper, one check in the SDK; every derived message can feed the client-facing provenance statement; the PRD examples change shape (flat to nested), which the ADR decides under D2-Q001.
2. **The same five fields flat on every data message (`route`, `vendor`, `service`, `fetched_at`, `retention_class`), the producing service only in `producer`.** Consequences: closest to most raw envelopes today; a flat `service` beside `producer.service` invites the confusion D1 found, and the SDK must copy five fields instead of one object.
3. **Provenance only on `raw.items` and `items.normalized`; derived messages carry `item_id` (or `candidate_key`) and readers join.** Consequences: smaller messages, but every consumer that must show provenance or expire by class has to join, and the non-negotiable "every output carries provenance" no longer holds as written.

**Why the recommendation.** The rule is the user's and is not in question; the nested object is the only form the SDK can stamp, copy and validate as one unit, and it separates the fetching service from the emitting one.

**Phase 2 records.** ADR "Provenance and retention class on messages" (Applies to: all). CONVENTIONS v1.1, L115 and the event bus section: the object, the field meanings, the list of data and control topics.

### D2-Q005 · The `raw.items` message: shape, envelope fields, and why a record was read

- **Class:** technical
- **Settles:** CF-004, CF-005, CF-006, AU-002, AU-015
- **Blocks:** F2, F4, F6, C2, C4, then every `raw.items` producer (D1 names FB4, IG2, VTT1, VTT2, X1, YT8, VTG1, W1, W2, W4, N6, TG1, TG2, X4, VLI1, YT4, N8, C10, C11, FB3, FB7, IG4, YT2)
- **Depends on:** D2-Q002, D2-Q003, D2-Q006 (who computes the key)

**Context.** Most producers write a nested `{"envelope": {...}, "payload": {...}}` message (`fb-page-feed-poller §6.2 L110-L126`, `ig-account-media-poller §6.2 L106-L123`, `li-post-search §6.2 L85-L102` and others); ig-hashtag-search and yt-keyword-search write flat fields with the record under `payload`; tt-keyword-search, tt-hashtag-feed-poller and x-recent-search write flat fields with the record under `raw` and `includes`; the web engines and tg-message-search give only a prose list (CF-004). The readers assume nesting: raw-archiver reads `envelope.raw_ref` and writes an envelope file and a payload file (`raw-archiver §5.2 L50`, `§5.3 L67`), normalize-item "read[s] the envelope" (`normalize-item §5.2 L49`). Both shapes are on the approved list. The envelope's fields differ too (CF-005): the usual set (`platform`, `kind`, `route`, `vendor`, `service`, `source_id`, `platform_id`, `idempotency_key`, `job_id`, `attempt`, `fetched_at`, `retention_class`, `client_ids`, `batch`) is missing pieces in a dozen producers; normalize-item selects its mapper by `(service, api_version)` and reads `job_kind`, which two producers write; raw-archiver needs `raw_ref` (`<object key>#<line>`, allocated by the SDK, `raw-archiver §11 L157`) where 33 producers write `batch`; and some twenty producer-specific fields (`edge`, `mention_type`, `received_at`, `query`, `window`, `matching_rules`, `cost_units`, `partial`, `url_key` and others) have no shared definition. Why a record was read travels as `metrics_observation`, `job_kind`, `origin`, `delivery` or `ingest_mode` (CF-006), each read by a different consumer: fb-reactions-fetcher labels observations from `metrics_observation`, comment-decay-scheduler expects `job_kind = backfill` "carried from the raw envelope" onto `items.normalized` (`comment-decay-scheduler §5.1 L66`; AU-002, AU-015), and nobody reads the others.

**Options**

1. **Nested `{envelope, payload}` for every producer, one envelope type built by the SDK, and one `job_kind` (recommended).**
   - Shape: `payload` holds the platform record as returned (minus identities, D2-Q010), with `includes` and other response parts inside it; the envelope holds everything else.
   - Envelope, required: `platform`, `kind` (the item kind, D2-Q007), `source_id`, `platform_id`, `idempotency_key`, `provenance` (D2-Q003), `retention_class`, `client_ids`, `job_id`, `attempt`, `job_kind`, `api_version`, `raw_ref`; plus `schema`, `message_id`, `produced_at`, `producer` (D2-Q002). Optional: a typed `context` object whose keys are declared per producer in the contracts package (the twenty producer-specific fields go there, each with a definition). `batch` is dropped: `raw_ref` names the object and line.
   - The SDK producer fills the envelope from the job and the adapter; services hand it the payload and the adapter's fields, never a hand-built envelope.
   - `job_kind` is the job's `kind` (for jobless receivers and the stream, the fixed values `push` and `stream`); it travels onto `items.normalized`, which is how backfilled records are recognised (AU-002, AU-015). `metrics_observation`, `origin`, `delivery` and `ingest_mode` are dropped; `item.metrics` labels derive from `job_kind` and the series step (D2-Q034).

   Consequences: one contracts type for 48 producers; raw-archiver and normalize-item work as written; the five flat-shape approved PRDs change their examples under D2-Q001; every record is replayable with its mapper chosen by `(service, api_version)`.

2. **Flat records with reserved top-level envelope names and the platform record always under `payload`.** Consequences: shorter messages; raw-archiver and normalize-item change how they split and read; reserved names can collide with platform fields.
3. **Both shapes on the wire, the SDK wrapping flat records before publishing.** Consequences: no PRD changes, but the SDK carries two input shapes forever, and fixtures must cover both.

**Why the recommendation.** It is the majority shape and the one both readers already expect; building the envelope in the SDK removes the missing-field problem at its source; one `job_kind` gives every consumer the same answer to "why was this read".

**Phase 2 records.** ADR "The raw.items message" (Applies to: all `raw.items` producers, raw-archiver, normalize-item, listening-sdk). CONVENTIONS v1.1, L15: the shape, the required and optional envelope fields, `raw_ref`, `job_kind` and its fixed values.

### D2-Q010 · Individuals' identities: one keyed reference, and where it is computed

- **Class:** user (how far the platform can link one person's activity, and whether the raw archive may hold their identity, are privacy choices behind the rule "individuals are never profiled")
- **Settles:** CF-069, CF-109, AU-048, AU-089
- **Blocks:** F2 (the helper and its golden vectors), F4, F6, C2, C4, C6, C7, C8, C9, C13, C14, X7, and every fetcher that writes people's ids: VTT3, VTT5, VTT6, X6, YT5, YT6, FB7, VFB1, VFB2, VFB3, VIG1, VIG2, IG4, IG5, IG6, LI2, LI3, VLI4, TG2, N6, N8
- **Depends on:** D2-Q005 (the `raw.items` envelope that carries the reference)

**Context.** The rule is CONVENTIONS L114 and L248: individuals are never profiled, a mention keeps a hashed author reference, individuals are never backfilled. The PRDs implement it five ways (CF-069):

- normalize-item hashes in the pipeline: `author_ref = hmac_sha256(AUTHOR_HASH_KEY, platform + ':' + author_platform_id)` (`normalize-item §5.2 L54`), stored by store-writer as `author_ref` (`store-writer §6.2 L110`) and carried in hits (`keyword-matcher §6.2 L111`).
- poster-resolver uses another formula and name: `author_hash = sha256(platform || platform_id || salt)` (`poster-resolver §5.2 L59`), carried by qualifier and registry-writer; the deletion paths call normalize-item's helper but look for a column `author_hash` (`retention-purger §5.3 L78`, `x-compliance-sync §5.3 L81`, `deletion-propagator §5.3 L60`, `L62`), which no writer produces.
- Eleven fetchers hash at the edge, before `raw.items`, each with its own name and rendering (`author_ref` as 64 hex, `ah1:` plus 32 hex, `hmac:` plus 16 or 20 hex, `hmac256:`, `{"ref": ...}`; CF-069 d) and AU-048), although CONVENTIONS says `raw.items` holds "every record exactly as a fetch or push returned it" (`CONVENTIONS L15`). README decision 8 makes the TikTok commenter the one exception (`README L185`); D1 found the same minimisation on X replies, YouTube comments and replies, Facebook webhooks and vendor group comments, Instagram vendor comments, LinkedIn vendor comments and reactions, Telegram group comments and Disqus comments (CF-109 b). Other routes keep identities in the raw payload and hash downstream (`ig-own-comments-fetcher §7 L139`, `ig-keyword-search §5.4 L86`, `fb-group-posts-poller §6.2 L124`).
- Some scope the hash so that one person gets different references: per YouTube channel (`yt-comments-fetcher §5.2 L56`, which asks "per channel (proposed, blocks linking a commenter across owners) or per owner, so a client with several channels can count unique commenters", `§14 Q4 L206`), per X source (`x-replies-fetcher §5.2 L59`, `§13 L189`), per Disqus thread for guests (`news-comments-fetcher §5.3 L76`).
- Resolvers answer for individuals with `candidate_ref`, a plain `candidate_key_hash`, or the clear `candidate_key` (CF-069 f).

Three PRDs ask for one shared function (`ig-comments-fetcher §14 Q2 L179`, `tt-video-comments-fetcher §14 Q4 L184`, `tg-discussion-receiver §14 Q4 L201`). As written, an author's deletion request computes one value and searches a column no writer fills, and one person gets several references across routes. Two more points ride on the same choice: whether business or creator accounts that are not registered sources keep their identity (the Instagram receivers say yes, `ig-webhook-receiver §7 L135`; normalize-item keeps identity only for registered sources, `normalize-item §5.2 L55`; AU-089), and what `raw.items` holds for services that write no raw record or an extract (`tt-user-resolver §13 L165`, `tt-video-stats-refresher §6.2 L112`, `news-article-extractor §5.3 L75`; CF-109 c, d).

**Options**

1. **One platform-wide keyed reference, computed at the edge for everyone who can never become a source (recommended).**
   - One function in the SDK, in both languages with golden vectors: `author_ref = HMAC-SHA256(AUTHOR_HASH_KEY, "<platform>:<author platform id>")`, rendered as 64 lower-case hex; one field name, `author_ref`, in every message, table and column (poster-resolver's `author_hash` and the resolvers' `candidate_ref` and `candidate_key_hash` become `author_ref`). The key lives in Vault and is not rotated except after a compromise, which starts a new key for new data only.
   - Not scoped: one person has one reference per platform, so deletion by author and distinct-author counts work. The safeguard moves to the query side: no client-facing view, export or query lists or ranks individual references, and YouTube rollups never combine channels of different owners outside the analytics carve-out (D2-Q056).
   - Where: the adapter replaces the identity of every commenter, replier, reactor, discussion member and mentioned member before the first write, on every route (README decision 8 widened). Registered sources keep `author_source_id` (an SDK lookup in the registry cache), and only registered sources keep a name downstream (AU-089 option 1; the Instagram PRDs reworded). Posters on discovery routes keep their platform id until poster-resolver classes them, since discovery needs it; once classed individual, raw-archiver replaces the id in the archived batch through the rewrite path that deletions already use.
   - `raw.items` is defined as "the record as returned, minus identities"; news articles are an extract by rule (copyright); tt-user-resolver and tt-video-stats-refresher are listed as writing no raw record, with the reason.

   Consequences: no clear identity of an individual is ever stored past classification, in any store, including the archive; replays cannot recover identities (by design); one helper and one name for F2; the scoped variants and their questions disappear.

2. **As option 1, plus scoped references for analytics.** The platform-wide reference is kept only where deletions need it, in a column no client query reads, and analytics rows carry a reference scoped per source (per channel on YouTube), as x-replies-fetcher and yt-comments-fetcher propose. Consequences: cross-source linking is impossible in analytics, not only forbidden; distinct-author counts work only inside one source; two references per person to manage.
3. **CONVENTIONS as written: `raw.items` keeps every record exactly as returned, and only normalize-item hashes.** The edge-hashing PRDs, TikTok's included, are reverted; one function as in option 1 downstream. Consequences: replay can re-derive references, but the raw archive holds individuals' ids and names for its whole retention (24 months under `vendor_agreed`), contradicting README decision 8.

**Why the recommendation.** It is what most PRDs already do and what README decision 8 proposes for TikTok, extended to every route so that the archive and the pipeline treat people the same way; a single reference keeps deletion by author workable, and the profiling rule is enforced where profiling would happen, in what clients can query.

**Phase 2 records.** ADR "Individuals' identities" (Applies to: all). CONVENTIONS v1.1: L15 ("as returned, minus identities"), L114 and L248 (the function, the field name, edge minimisation, archive redaction after classification, no client-facing per-author view); README decision 8's first clause generalised. The function and golden vectors go to F2; the registry-cache lookup to F4 and F6.

## Group 2 · The README's nine proposals

The build plan says to accept the nine proposals "as written unless D1 finds a conflict" (FC-01). D1 found conflicts against all nine (`docs/contracts/CONFLICTS.md` section 4), so each comes here with the entries that contradict it, and FC-01 itself needs no decision of its own (Appendix B). RD-n is README decision n (`docs/prds/README.md` L178 to L186).

### D2-Q018 · Budget priorities and modes (README decision 2)

- **Class:** user (which work keeps running when a budget or quota runs short is a business choice)
- **Settles:** RD-2, CF-100, CF-101, AU-039, AU-067
- **Blocks:** F5 (the SDK priority helper), C1 (quota-governor), C11, then YT4, YT5, YT6, YT7, YT8, X1, X3, X4, X5, X6, FB4, FB6, VLI1, VTG1, VTG2, VTT3
- **Depends on:** D2-Q057 (what a job does with `deny` and `wait-until`)

**Context.** README decision 2 sets five priorities (1 tier-1 rotation, client refresh, ops, canaries; 2 tier-2 rotation, client keyword searches, comment steps up to +24 h; 3 tier-3 and dormant rotation, later comment steps, replies, +7 d metrics; 4 hot-post extras and resolvers; 5 backfill) and three modes (`normal`; `stretch` from 80% of a budget, admitting priorities 1 to 3, and from 95% only 1 and 2, with amber intervals stretched by a factor, never beyond 24 hours; `exhausted` at 100%), and says the +24 h comment step is held, never cancelled (`README L179`). quota-governor implements it: priorities are "derived from job kind and tier by an SDK helper; a caller cannot claim more than its kind allows" (`quota-governor §5.1 L39`, table L43 to L47), "validated server-side" (`§12 L149`). D1 found these disagreements:

- Client refresh: priority 1 in the README, quota-governor and comment-decay-scheduler (`comment-decay-scheduler §5.1 L70`), but 3 in the YouTube and X reply fetchers (`yt-comments-fetcher §14 Q2 L204`, `yt-replies-fetcher §14 Q3 L192`, `x-replies-fetcher §7 L145`) and "at lowest priority" for refreshes of backfilled posts (`backfill-orchestrator §5.1 L48`); the step is labelled `refresh:<request_id>`, `client` or `refresh_client` (AU-039).
- First sight: yt-video-details-fetcher proposes priority 1 for new videos from every tier and keyword rule (`yt-video-details-fetcher §5.1 L50`, `§14 Q1 L215`); the table derives 2 or 3 from the tier.
- A client's X history read at priority 1 (`x-full-archive-search §5.2 L53`); the table has no row for it.
- Priorities set by callers, or orderings outside the table: from `series_step` (`yt-comments-fetcher §5.2 L53`, `x-replies-fetcher §5.2 L55`), the text refresh at 3 (`yt-text-purger §5.3 L84`), priorities carried on jobs (`tt-user-resolver §5.1 L41`, `x-filtered-stream §5.2 L70`), search last among green Facebook services (`fb-page-search §7 L127`), rotation before comments before metrics on the Meta bucket (`fb-reactions-fetcher §7 L134`), resolver discovery "never stretched, only denied" (`tg-channel-resolver §5.1 L47`), and the YouTube `reserve` bucket for priority 1 only (`quota-governor §5.3 L79`) or for catch-up, hot posts and client refreshes (`yt-keyword-search §7 L133`).
- Modes on metered green tags (CF-101): CONVENTIONS stretches intervals and drops hot-post extras only on amber routes (`CONVENTIONS L51`, `L271`); the README gates priorities on every tag, so hot extras (priority 4) stop at 80% on X and YouTube too; the question is still open in `quota-governor §14 Q2 L171` and `comment-decay-scheduler §14 Q4 L205`; x-recent-search expects an X-only cascade at 80% (cut x-full-archive-search first, stretch tier-2 and tier-3 searches to daily, drop reply steps after +24 h, `x-recent-search §7 L143`).

At stake: one number per job, which decides what still runs at 80% and 95% of the X cap (USD 0.005 a post read), the YouTube 10,000 units a day and each vendor's monthly budget.

**Options**

1. **The README's table, completed with explicit rows and derived only by the SDK helper; priority gating on every tag, interval stretching on amber tags only (recommended).**
   - Priority 1: tier-1 rotation, every client request (refreshes, including refreshes of backfilled posts, and history reads), `ops_force`, canaries, and the first sight of a new item on any tier (for YouTube, the details call that turns an id into a record).
   - Priority 2: tier-2 rotation, client keyword searches, comment steps up to +24 h, +24 h metrics.
   - Priority 3: tier-3 and dormant rotation, later comment steps, replies, +7 d metrics, the 30-day text refresh.
   - Priority 4: hot-post extras, resolvers and discovery lookups.
   - Priority 5: backfill, and X history reads nobody asked for.
   - No caller sends a priority; the YouTube `reserve` bucket serves priority 1 only; one label for a client refresh, `refresh:<request_id>`.
   - Modes: `stretch` and `exhausted` gate priorities on every tag, green ones included, so hot extras and resolver lookups stop at 80% on X and YouTube; `stretch_factor` (never beyond 24 hours) applies to amber tags only; x-recent-search's X-only cascade is dropped in favour of the table.

   Consequences: one table, one helper, testable in F5; whatever a client asks for runs first, so the admin console (D3) must cap requests per client; new items are never left half-recorded under pressure (a YouTube details call costs 1 unit for 50 ids); the green X and YouTube budgets keep their last 20% for rotation and early comment steps.

2. **The README's table exactly as written, the PRDs aligned.** Client refresh 1, first sight by tier (2 or 3), X history reads as backfill (5), the text refresh at its tier; modes as in option 1. Consequences: fewer rows; at 95% of the YouTube quota, new videos from tier-2 and tier-3 channels stay partial records, and a client's X history request waits behind all rotation.
3. **Per-tag priority profiles configured in `budgets`, or callers sending priorities checked against a per-kind maximum.** Consequences: each vendor can have its own order (the X cascade, the Meta metrics order), but behaviour becomes configuration rather than contract, and two services can rank the same job differently.

   A narrower variant of any option: keep CONVENTIONS' modes (gating and stretching on amber tags only), so nothing on X or YouTube is gated before 100%; hot extras could then use the last 20% of the X cap.

**Why the recommendation.** It keeps README decision 2, which most PRDs already follow, closes every gap D1 found with a row rather than an exception, and keeps priorities out of callers' hands.

**Phase 2 records.** ADR "Budget priorities and modes" (Applies to: quota-governor, listening-sdk, comment-decay-scheduler, every service with a `budget_tag`). CONVENTIONS v1.1: the priority table and the mode rules under "Quotas, budgets and the quota governor"; L51 and L271 reworded (stretching on amber tags only; gating on every tag).

### D2-Q019 · Early stop of a comment series (README decision 3)

- **Class:** technical
- **Settles:** RD-3, CF-107
- **Blocks:** C11, then FB5, VFB3, IG6, VIG2, VTT5, X6, YT5, YT6, LI2, VLI4, N8

**Context.** CONVENTIONS stops a series "when a fetch adds fewer than 5% new comments (and fewer than 5 absolute)" with no arming condition (`CONVENTIONS L57`, `L271`). README decision 3 arms early stop "only once a post has 5 stored comments or after its +24 h step", so a post with no comments at +1 h keeps its series (`README L180`); comment-decay-scheduler implements it (`comment-decay-scheduler §5.3 L88`, `L89`; asked to confirm in `§14 Q2 L203`), as do `x-replies-fetcher §5.1 L45` and `yt-replies-fetcher §5.1 L40`. The LinkedIn fetchers arm it "from the second fetch of a post onward" (`li-own-comments-fetcher §5.1 L42`; `li-post-comments-fetcher §5.1 L44`); four fetchers restate CONVENTIONS without arming (`fb-post-comments-fetcher §5.1 L48`, which asks whether the +24 h step should be exempt, `§14 Q2 L188`; `news-comments-fetcher §5.1 L43`; `tt-video-comments-fetcher §5.1 L44`; `ig-comments-fetcher §5.1 L45`). The denominator: the scheduler measures growth over the comments stored before the fetch (`comment-decay-scheduler §5.3 L87`), while li-own-comments-fetcher measures over the platform's reported count, "because held comments expire at 48 hours" (`li-own-comments-fetcher §5.1 L42`).

**Options**

1. **README decision 3 on every profile, applied only by comment-decay-scheduler, with a LinkedIn denominator (recommended).** Early stop is armed once the post has 5 stored comments or its +24 h step has run (on shorter profiles, its last step before +24 h); growth is measured over the comments stored before the fetch, except on the LinkedIn profiles, where it is measured over the platform's reported comment count. The fetchers report counts and never stop a series themselves; their PRDs drop their own early-stop text. Consequences: one rule in one service; the +24 h step always runs, which answers fb-post-comments-fetcher's question; the LinkedIn exception is one column in the profile table.
2. **Per-profile arming and denominator columns, filled from each fetcher's PRD.** Consequences: every route keeps what its PRD wrote (LinkedIn from the second fetch, Facebook and news unarmed), so the same post shape stops at different times on different routes with no stated reason.
3. **CONVENTIONS as written (no arming), with the +24 h step exempt.** Consequences: a post with no comments at +1 h loses its series before the +6 h step, the case the README added the arming rule for.

**Why the recommendation.** The README's rule fixes a real failure (quiet posts that pick up comments later), the scheduler already implements it, and LinkedIn's 48-hour purge is the one case where the stored count is the wrong basis.

**Phase 2 records.** ADR "Early stop" (Applies to: comment-decay-scheduler and every comment fetcher). CONVENTIONS v1.1, L57 and L271: the arming condition and the LinkedIn denominator. The thresholds stay as written; tuning them after real data is left to the sessions after G2 (build plan L65).

### D2-Q021 · A platform 401 or 403, fallback, and the government exclusion (README decision 5)

- **Class:** user (whether the platform switches a client's data to a vendor automatically, and the guarantee given to government clients, are product and compliance choices)
- **Settles:** RD-5, CF-094, AU-064
- **Blocks:** F3 (the states the schema holds), F4, F5 (the SDK's error handling), C7, C12, then every green fetcher (TT1, LI1, LI2, IG3, IG5, IG6, X1, X2, YT1, YT3, YT4, TG1, TG2, VLI2 are named in CF-094)
- **Depends on:** D2-Q016 (where token and source state are stored and who writes them)

**Context.** CONVENTIONS says a 401 or 403 makes the service mark "the token or route `degraded`", stop the batch and alert (`CONVENTIONS L101`); the canary sets `fallback_on` "where an amber or alternate route exists and the flag is on" (`CONVENTIONS L102`). README decision 5 changes that: a platform 401 or 403 means `blocked`, with no automatic fallback and an n8n approval card; a vendor key or plan error is `degraded` and may fall back; a green source watched by a government client never moves to an amber fallback (`scope = non_government`) (`README L182`). source-health-canary follows the README per route (`source-health-canary §5.3 L70` to `L72`, `§8 L119`, `§13 L151`); most fetchers follow CONVENTIONS ("a 401 marks the token `degraded`", `x-recent-search §13 L186`, `ig-own-comments-fetcher §13 L187`, `yt-channel-resolver §13 L192`); some set `health = blocked` on one source under their own conditions (`tt-client-videos-fetcher §8 L130`, `li-client-posts-poller §8 L142`, `ig-account-media-poller §8 L141`, `tg-bot-channel-receiver §8 L150`); tt-client-videos-fetcher refuses any amber fallback for a client-owned account, for every client (`tt-client-videos-fetcher §8 L132`); li-org-resolver treats a Posts API 403 as a missing grant and sends the client a card (`li-org-resolver §8 L122`). The government exclusion has no enforcement point: registry-writer's route-wide `health_change` updates every source on the route and reads no `scope` (`registry-writer §5.2 L54`, `§7 L107`; AU-064), and the canary asks who should enforce it (`source-health-canary §14 Q2 L162`).

**Options**

1. **README decision 5, made precise at two levels (recommended).**
   - A platform 401 or 403 on a client token or company app key marks that credential `revoked` (one attempt to refresh it first, where the platform allows) and stops the batch; every source that only that credential could read becomes `blocked`. No automatic fallback: an n8n card goes to ops and, for client-owned properties, to the client.
   - A 403 that concerns one source only (a removed bot, a suspended or private account, a missing page grant) makes that source `blocked`, not the credential.
   - A vendor key or plan error (401, 402, 403 or out of credits from a vendor) marks the key `degraded`; the route may fall back, decided by the canary only.
   - Route-wide states (`degraded`, `fallback`, back to `ok`) come only from the canary, from evidence across targets.
   - No green source watched by a government client ever moves to an amber route; registry-writer enforces it when it applies a route-wide change (option 1 of AU-064), and a client-owned green property never falls back to a vendor for any client, as tt-client-videos-fetcher already says (D2-Q052).
   - A green route that is not yet approved has no amber stand-in: while Page Public Content Access is pending, Facebook Page comments are not read through the vendor's post-comments endpoint (`fb-post-comments-fetcher §14 Q5`); Facebook Pages go live when Meta approves the app.

   Consequences: a revoked client token never silently turns into vendor data; government contracts are protected in one place; F3 needs a credential state and a reason beside `sources.health` (D2-Q016); about forty section 8s and CONVENTIONS L101 are aligned.

2. **CONVENTIONS L101 as written: fetchers mark the token or route `degraded`, and only the canary, from route-wide evidence, sets `blocked`.** Consequences: fewer states; a revoked client token degrades its sources and the canary may then fall back to a vendor automatically, government exclusion aside; the README's approval card disappears.
3. **Two levels without the README's no-fallback rule:** credential state set by fetchers, `blocked` for a lost grant on one source, and automatic fallback wherever a flag is on except for government-watched sources. Consequences: maximum coverage, but a client's own revoked token can lead to vendor-sourced data about that client's property without anyone deciding it.

**Why the recommendation.** A 401 or 403 from a platform usually means a client withdrew consent or a grant lapsed; answering that with vendor data is a compliance risk, while a vendor's credit or key problem is ours to route around. Option 1 keeps both of the README's rules and gives each state one writer.

**Phase 2 records.** ADR "Platform 401/403, fallback and the government exclusion" (Applies to: all fetchers, source-health-canary, registry-writer, listening-sdk). CONVENTIONS v1.1: L101 and L102 rewritten as in option 1; L113 gains "a government-watched green source never moves to an amber route; registry-writer enforces it".

### D2-Q022 · News: the `news.dedup` topic, the per-host gate and the 7-day full-text cache (README decision 6)

- **Class:** technical (counsel confirms the cache reading before G2; see the last point of option 1)
- **Settles:** RD-6, CF-025, CF-092, CF-111, AU-003, AU-055, AU-104
- **Blocks:** F2 (the topic), F4 and F5 (the host gate and the cache client in the SDK), C4, C5, C6, C13, C14, C15, A5, then N1 to N8, A1, A2, A3

**Context.** README decision 6 proposes three things (`README L183`), and D1 found a conflict in each:

- The topic `news.dedup`, from news-dedup "to normalize-item". news-dedup writes it, partitioned by `story_id`, one message per verdict and per `story_update` (`news-dedup §6.2 L84` to `L101`), and expects normalize-item to copy `story_id`, `is_origin` and `duplicate_of` onto the normalized item and re-emit a version on updates (`news-dedup §6.2 L104`), "with a bounded wait in normalize-item; if normalize-item prefers a table-only join, the topic is dropped" (`news-dedup §14 Q1 L167`). normalize-item reads no such topic and its item has no story fields (`normalize-item §6.1 L86`, `§6.2 L93-L120`; CF-025), while aggregator and alert-evaluator expect story fields downstream (AU-003).
- A per-host gate in listening-sdk, one connection and 2 to 5 seconds between requests across all news services. Only news-article-extractor doubles the spacing after a 429 or 503 (`news-article-extractor §5.3 L65`); the other four list the same "lane-wide rules" without it (CF-092 d). Which host errors re-check the crawl policy also differs: news-robots-checker wants a `recheck` on every 4xx, 429 included, and on a feed or sitemap 404/410 (`news-robots-checker §5.1 L47`); the fetchers back off on 429 and send a feed, sitemap or homepage 404/410 to news-site-resolver as `refresh` (`news-feed-poller §8 L131`, `news-sitemap-poller §8 L144`, `news-homepage-differ §8 L135`), and news-feed-poller's own acceptance test says "Any 4xx from a host produces one `recheck` job" (`news-feed-poller §13 L170`; CF-092, AU-104).
- news-article-extractor owns the 7-day full-text cache (`cache/news/<yyyy>/<mm>/<dd>/<canonical_url_hash>.json.zst`, `news-article-extractor §5.3 L75`) and passes `text_full_ref`, yet both it and normalize-item still ask who owns it (`news-article-extractor §14 Q3 L189`, `normalize-item §14 Q2 L179`); news-comments-fetcher writes a second cache under `cache/news/comments/` (`news-comments-fetcher §5.2 L57`, `§6.2 L113`); and whether keyword-matcher and the analysis services may read it is open: "Proposed: yes, otherwise a brand named after the first 300 characters is missed; to be confirmed with counsel on Law No. 3 of 1971" (`news-article-extractor §14 Q1 L187`; CF-111, AU-055).

**Options**

1. **Keep all three, with these precisions (recommended).**
   - `news.dedup` joins the topic list, keyed by `story_id`; store-writer, not normalize-item, consumes it and records `story_id`, `is_origin`, `duplicate_of` and `cluster_size` on the item's row in ClickHouse as a new version (and keeps a story membership table for updates). normalize-item stays a pure mapper with no wait; aggregator and alert-evaluator read story fields from ClickHouse.
   - The host gate lives in the SDK, for every news service: one connection per host, 2 to 5 seconds between requests or the host's `Crawl-delay`, and the spacing doubles after a 429 or 503 until a success. A 429 or 503 backs off and never re-checks the policy; a 401, 402, 403 or 451 sends one `recheck` per host (coalesced) and stops the batch; a 404 or 410 on a feed, sitemap or homepage sends `refresh` to news-site-resolver; a 404 or 410 on an article does neither. news-robots-checker's list and news-feed-poller's test are aligned.
   - Each cache writer owns its prefix: news-article-extractor `cache/news/` for articles, news-comments-fetcher `cache/news/comments/` for Disqus comments; both prefixes are registered in the SDK purge registry with the 7-day clock and deletion by `item_id`. keyword-matcher and the analysis services may read the cache within the 7 days and persist only derived values (hit offsets, scores), so a brand named after the excerpt is still matched (AU-055). Counsel confirms this reading of Law No. 3 of 1971 before G2 (`DEFERRED.md`, owner N6).

   Consequences: one news topic with a consumer; one gate implementation; two registered cache prefixes; full-text matching within the cache window.

2. **README decision 6 exactly as written: normalize-item consumes `news.dedup` with a bounded wait and re-emits story fields as item versions.** Consequences: story fields reach every consumer of `items.normalized`, at the cost of a wait and a second emit in the busiest shared service; the gate and cache points still need option 1's answers.
3. **No topic: store-writer (or readers) join news-dedup's `news_story_members` table when they need stories.** Consequences: one topic fewer, but a cross-database join from ClickHouse readers into Postgres, and story updates are not visible as events; the gate and cache points as in option 1.

**Why the recommendation.** It keeps every part of the README proposal, gives the topic the consumer that already writes item versions, fixes the gate once for all five news services, and lets matching see the article text the cache exists to hold.

**Phase 2 records.** ADR "News: dedup topic, host gate and full-text cache" (Applies to: every news service, normalize-item, store-writer, keyword-matcher, the analysis services, listening-sdk, deletion-propagator, retention-purger). CONVENTIONS v1.1: `news.dedup` in the topic list; the host gate and error rules under the news fact sheet (L215); the cache prefixes and readers under object storage (L31). `DEFERRED.md`: counsel on matching over the cache.

## Group 3 · The foundation choices

The build plan's foundation table (FC-01 to FC-13) lists the choices D2 settles before the foundation sessions start. Three of them are settled inside earlier decisions: FC-02 (one writer per column) in D2-Q013, FC-03 (`item_id` derivation) in D2-Q006 and FC-04 (schema versioning) in D2-Q002. FC-01 ("accept the nine README decisions unless D1 finds a conflict") needs no decision of its own: D1 found conflicts against all nine (CONFLICTS.md section 4), so each is decided on its own in Group 2. The decisions below take the rest. F1, already merged, built three of them (FC-10, FC-11, FC-13), so D2-Q030 only ratifies what exists.

### D2-Q026 · Kafka client libraries for the two SDKs

- **Class:** technical
- **Settles:** FC-05
- **Blocks:** F4, F6 (and every service through them)

**Context.** The build plan proposes `@confluentinc/kafka-javascript` for Node and `confluent-kafka` for Python, both on librdkafka (build plan L55). F1 already uses the Node client in the stack acceptance tests (`docs/handoffs/F1.md` L81) and recorded it in `docs/dependencies.md` (MIT, bundling librdkafka under BSD-2-Clause; Confluent, Inc., US; screen "clear"); its prebuilt binary installs on the pinned Node 24 (`onlyBuiltDependencies` in `pnpm-workspace.yaml`, F1 L121). Redpanda speaks the Kafka API, so any Kafka client works. What matters for the contracts is that the Node SDK (F4) and the Python SDK (F6) produce and consume identically: "partitioned by `source_id` so one source is never worked twice at once" (CONVENTIONS L28) holds only if both SDKs put the same key on the same partition, and the cursor rule ("cursors advance only after the batch is acknowledged by Redpanda", CONVENTIONS L71) needs the same acknowledgement and idempotent-producer semantics in both.

**Options**

1. **Both clients on librdkafka, as proposed, with the partitioner set explicitly (recommended).** F4 uses `@confluentinc/kafka-javascript`, F6 uses `confluent-kafka`; both SDKs set `partitioner = murmur2_random` (the Java-compatible hash, which Redpanda's own tools and other Kafka clients also use), `enable.idempotence = true` and `acks = all`, and a shared conformance test proves a key lands on the same partition from both languages. Consequences: one underlying library, so retries, batching and error codes match across languages; the explicit partitioner avoids librdkafka's default (`consistent_random`, a CRC32 hash) disagreeing with any non-librdkafka producer, for example a tool or an n8n flow that writes to a topic. F6 adds `confluent-kafka` (Apache-2.0, Confluent, Inc., US) to `docs/dependencies.md`.
2. **Pure-language clients: KafkaJS for Node and aiokafka for Python.** Consequences: no native binary, but two unrelated implementations whose default partitioners differ, so both SDKs must pin one by hand; KafkaJS has had no maintained release line for years, a risk for a platform meant to run ten years.
3. **`node-rdkafka` for Node with `confluent-kafka` for Python.** Consequences: also librdkafka, but `node-rdkafka` is a separate binding with its own release cadence; F1's tests would move to it.

**Why the recommendation.** Option 1 is what F1 already proved, keeps one engine under both SDKs and fixes the one setting (the partitioner) that would otherwise break per-source ordering between languages.

**Phase 2 records.** ADR "Kafka clients" (Applies to: F4, F6, all services). CONVENTIONS v1.1, under the event bus: the client per language and the three producer settings.

### D2-Q027 · Where the platform runs: the cluster and object storage

- **Class:** user
- **Settles:** FC-06, FC-07
- **Blocks:** I1 (it cannot start without this), then C2 (raw-archiver's buckets), I2, E2 and the gates G2 to G4; the account itself is something only the user can open (`docs/orchestration/README.md`, "What only the user can supply")

**Context.** CONVENTIONS already names Hetzner servers and "Backblaze B2 or Hetzner Object Storage" (CONVENTIONS L3) and leaves the orchestrator open: "Kubernetes or Nomad; the PRDs say 'the cluster'" (CONVENTIONS L12). The build plan proposes k3s on Hetzner "unless your team already runs Nomad" (FC-06) and Hetzner Object Storage as primary with Backblaze B2 as the off-site copy of the raw archive (FC-07). Both vendors are on CONVENTIONS' cleared list (L6). Constraints from the briefs: TLS from Let's Encrypt with no Cloudflare dependency, and the Telegram webhook endpoint outside Iraq (I1 brief, "Watch for"; CONVENTIONS L200). The raw archive is the platform's replay source (raw-archiver), so losing it loses the ability to reprocess; that is the reason for an off-site copy.

**Options**

1. **k3s on Hetzner, Hetzner Object Storage primary, Backblaze B2 off-site copy of `raw/` (recommended).** Consequences: one vendor for compute and primary storage in the EU, outside Iraq; k3s is a small, standard Kubernetes, so Helm charts, operators (for example for Redpanda and ClickHouse) and ordinary Kubernetes skills apply; the B2 copy covers the loss of a Hetzner region or account; I1 prices both before staging, and the user opens the Hetzner and Backblaze accounts.
2. **Nomad on Hetzner instead of k3s, same storage.** Consequences: worth it only if the team already runs Nomad, as the build plan says; fewer ready-made operators for Redpanda and ClickHouse, so I1 writes more of its own job specifications.
3. **Hetzner Object Storage only, no off-site copy.** Consequences: lower cost and one account fewer; a provider-level loss would lose the raw archive and with it every replay and reprocessing.
4. **Another provider (named by the user).** Consequences: it goes through the vendor screen (CONVENTIONS L6) and `docs/dependencies.md` first; I1's brief, which is written for Hetzner, changes.

**Why the recommendation.** It matches CONVENTIONS and the build plan, uses only cleared vendors, keeps the hosting outside Iraq and protects the one store that cannot be rebuilt.

**Phase 2 records.** ADR "Hosting: cluster and object storage" (Applies to: I1, I2, C2, E2, all services through "the cluster"). CONVENTIONS v1.1, L12: "the cluster" is k3s on Hetzner; L3 and the object storage line (L31): Hetzner Object Storage primary, Backblaze B2 off-site copy of `raw/`.

### D2-Q028 · lang-dialect-id in Python

- **Class:** technical
- **Settles:** FC-08, CF-112, AU-074, AU-075
- **Blocks:** C3, F7 (the fold in both languages), F6 (the Python SDK carries one more service), then C8, VLI2, A1, A4

**Context.** CONVENTIONS allows Python only for the analysis workers and the news extractor (CONVENTIONS L13). lang-dialect-id needs CAMeL Tools and KLPT, which are Python libraries: "Runtime: Python, because CAMeL Tools and KLPT are Python libraries" (`lang-dialect-id §9 L150`), and it asks to confirm a third exception or port the fold to TypeScript (`lang-dialect-id §14 Q1 L187`; CF-112). The build plan proposes Python with a TypeScript copy of the fold for fallback (FC-08), and the session plan already assumes it: C3 needs F6 (the Python SDK) and F7 (the fold and its golden corpus) first (`build-plan/SESSIONS.md`). F7 builds the folds "in TypeScript exactly as lang-dialect-id section 5.3 C defines them" with a golden corpus "both languages' code must pass" (F7 brief). Two smaller points ride on the same service. Its callers: lang-dialect-id names normalize-item as "the only caller of `/v1/detect`" (`lang-dialect-id §4 L34`, `§6.1 L99`), while poster-resolver sends it a sample of up to 20 recent posts per candidate (`poster-resolver §5.2 L58`), li-org-resolver asks the SDK's "language client" for a language share (`li-org-resolver §5.2 L56`) and analysis-media sends transcripts (`analysis-media §5.3 L66`) (AU-074). And Arabic written in Latin letters (Arabizi): analysis-sentiment routes it through transliteration (`analysis-sentiment §5.2 L57`), but lang-dialect-id reads Arabizi "as `en` or `und`" (`lang-dialect-id §12 L164`), keeps transliteration out of scope (`§3 L29`) and asks whether to add a Latin-script Arabic class after the pilot (`§14 Q3 L189`); F7's brief records Arabizi as "not transliterated (documented gap)" (AU-075).

**Options**

1. **Python service, recorded as the third exception, with the fold also in TypeScript (recommended).** lang-dialect-id runs on the Python SDK (F6) with CAMeL Tools, KLPT and fastText; F7's TypeScript fold is byte-identical to the Python one on the golden corpus, so a Node service (keyword-matcher, normalize-item) can fold text locally without a call. Its callers are named: normalize-item, poster-resolver and li-org-resolver (profile samples, through a batch form of `/v1/detect` wrapped by the SDK's language client) and analysis-media (transcripts), and the service's pool is sized for them (AU-074 option 1); keyword-matcher and CI tools call `/v1/fold`. Arabizi gets no route in v1: lang-dialect-id adds a `script` value (`latn` or `arab`) to its answer so the pilot can count Latin-letter Arabic, analysis-sentiment drops its transliteration branch, and a Latin-script Arabic class is considered after the pilot as lang-dialect-id §14 Q3 asks (AU-075 option 3). Consequences: CONVENTIONS L13 gains one exception; one golden corpus guards both implementations; Arabizi posts are scored by the fallback model or left unscored in v1, a known gap that young users' posts make visible.
2. **Port the fold to TypeScript and keep only fastText and the dialect model in Python.** Consequences: the exception narrows to a model server but does not disappear; the CAMeL and KLPT behaviour the PRD relies on must be reimplemented and kept equal by hand.
3. **Node only, with fastText through WebAssembly and no CAMeL Tools or KLPT.** Consequences: no Python exception, but the Iraqi-dialect and Sorani features the PRD names are lost or rebuilt from scratch; not recommended.

**Why the recommendation.** It is the plan the build sequence already follows, it uses the libraries the PRD is built on, and the shared golden corpus removes the risk of two folds drifting. Naming the callers sizes the service for its real load, and the Arabizi gap stays as F7 and lang-dialect-id already planned it, now measured instead of hidden.

**Phase 2 records.** ADR "lang-dialect-id in Python" (Applies to: C3, F6, F7, normalize-item, keyword-matcher, poster-resolver, li-org-resolver, analysis-media, analysis-sentiment). CONVENTIONS v1.1, L13: "... and lang-dialect-id (Python, CAMeL Tools and KLPT; the fold also in TypeScript, both checked against F7's golden corpus)". `DEFERRED.md`: a Latin-script Arabic class after the pilot, owner C3.

### D2-Q029 · ClickHouse topology and the three environments

- **Class:** user
- **Settles:** FC-09, FC-12
- **Blocks:** I1, F8 (replication settings in the migrations), E2, G2, G4

**Context.** The build plan proposes one ClickHouse node with backups in staging and a replicated pair before production (FC-09), and three environments: local with the fake platform only, staging with real APIs on small budgets, and production (FC-12). The volume target is about 1,000,000 new posts and comments a day and ten years of aggregates (CONVENTIONS L3). F8 writes the migrations: a replicated table engine needs a Keeper ensemble and replicated engines from the first migration, or a later migration that converts tables. Staging is where real API keys and vendor spend first appear (G2: "staging with real data"); the probes (FB0, X0, YT0 and the others) and their spend need the user's yes per call list anyway (`docs/orchestration/README.md`).

**Options**

1. **As proposed (recommended).** Staging: one ClickHouse node with daily backups. Production: a replicated pair with ClickHouse Keeper (three small Keeper nodes, or Keeper on the cluster's control-plane nodes) before G4. F8 writes the tables with replicated engines from the start, so the same migrations run on one node and on the pair. Environments: local (fake platform, no network), staging (real APIs, each budget tag capped at a small figure the user sets per tag before G2), production. Consequences: the lowest cost until production; replication is proven in G4 rather than from day one.
2. **Replicated from staging.** Consequences: about twice the ClickHouse cost from G2; replication and failover are exercised for longer before production.
3. **One node in production as well, with backups.** Consequences: cheapest; a node loss stops ingestion and dashboards until a restore, and the restore point is the last backup.

**Why the recommendation.** The data volume reaches production scale only in production; one node is enough to prove the pipeline in staging, while writing replicated engines from the first migration keeps the move to a pair a deployment change rather than a schema change.

**Phase 2 records.** ADR "ClickHouse topology and environments" (Applies to: I1, F8, E2, G2, G4). CONVENTIONS v1.1, analytics store (L32): replicated engines from the first migration; one node in staging, a pair in production. The staging caps per budget tag go into G2's plan.

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

## Group 6 · Values, flags, vendors and clients

### D2-Q049 · What `tier` holds, and what "push" means

- **Class:** technical
- **Settles:** CF-095, CF-096
- **Blocks:** F3 (the column types), F5 (the scheduler's cadence lookup), C1, C7, C9, then TT1, VTT4, TG1, TG2, LI1, LI3, YT2, YT3, FB2, FB7, IG3, IG4, X3, X4, W1, W2, W4, N2, N3, N4, N5, X1, YT8, YT9, IG2, IG5, VLI3

**Context.** CONVENTIONS gives `tier` six values, `1`, `2`, `3`, `push`, `dormant`, `retired` (L36), with cadences for reach sources (L45 to L50); the examples write numbers (`"tier":2`, `qualifier §6.2 L84`) while registry-writer compares `tier = 'retired'` and calls `least_tier(...)` (`registry-writer §5.3 L72`). Two other meanings share the column (CF-095): for keyword rules, tier is a priority with its own cadences (every 12 or 24 hours on the web engines, `web-search-perplexity §5.1 L41`; every 15 or 60 minutes on X, `x-recent-search §5.1 L41`; API search or web bridge on YouTube, `yt-keyword-search §5.1 L46`; hourly whatever the tier on GDELT, `web-gdelt-poller §5.1 L41`); for news sites, tier comes from publishing rate (`news-site-resolver §5.2 L53`) with feed cadences of 5 to 15 minutes or hourly (`news-feed-poller §5.1 L42`). `push` mixes in a third meaning (CF-096): CONVENTIONS defines it for client-owned properties with "no polling for new posts; one reconciliation poll a day" (L48), but tt-client-videos-fetcher reads client TikTok accounts hourly while marking them `push` (`tt-client-videos-fetcher §5.1 L43`), LinkedIn client pages are polled every 30 or 60 minutes and "the generic push tier does not apply" (`li-client-posts-poller §5.1 L42`), every YouTube channel with a PubSubHubbub lease "sits in the push tier, client-owned or not" while its reach tier is still needed as "the secondary sort key and the quota priority" (`yt-uploads-reconciler §5.1 L45`, `yt-pubsub-receiver §5.1 L40`), and X treats stream coverage as push "while `sources.tier` keeps the reach tier" (`x-filtered-stream §5.1 L42`). A dormant source also needs its reach tier back when it posts again (L49). One column cannot hold all of that.

**Options**

1. **Three columns: `tier` (1, 2, 3, always kept), `lifecycle` (`active`, `dormant`, `retired`) and `push_covered` (boolean), with one cadence table per source type in CONVENTIONS (recommended).** `tier` is the reach tier for pages, accounts, channels and groups, and the client priority for keyword rules, hashtags and news sites; quota-governor's priorities read it. `lifecycle` replaces `dormant` and `retired` as tier values. `push_covered` is true when new posts arrive by webhook, PubSubHubbub, bot or stream; the poller then makes one reconciliation read a day instead of its tier cadence, unless the cadence table says otherwise for the source type (client TikTok accounts hourly, LinkedIn client pages every 30 to 60 minutes). The cadence table has one row per source type (reach sources, keyword rules per engine, hashtags, news sites per poller) and is what F5's scheduler helper reads. Consequences: F3 types `tier` as a small integer; registry-writer's `least_tier` becomes a plain minimum; `tier_change` events and qualifier rule 6 keep numbers; README decision 8's "`tier = push`" becomes `push_covered = true` (D2-Q024).
2. **One text enum as written (`1`, `2`, `3`, `push`, `dormant`, `retired`) with an ordering function, plus the cadence table per source type.** Consequences: no schema change from CONVENTIONS, but a pushed YouTube or X source loses its reach tier, and a dormant source must recompute its tier from followers when it wakes.
3. **The reach tier only for accounts, pages and channels; keyword rules and news sites get a separate `cadence` field and no tier.** Consequences: clean for searches, but `push` and the lifecycle states still share the column, so CF-096 stays open.

**Why the recommendation.** Each of the three meanings gets its own column, so no service has to overload one value, and the cadences the PRDs need (hourly TikTok, 30-minute LinkedIn, daily YouTube reconciliation, 15-minute X keywords) all become rows of one table.

**Phase 2 records.** ADR "Tier, lifecycle and push coverage" (Applies to: all pollers, receivers and searchers, registry-writer, qualifier, quota-governor, listening-sdk). CONVENTIONS v1.1: L36 (the three columns), L44 to L51 and L276 (the cadence table per source type), L247 (rule 6 sets `tier` and `push_covered`).

## Group 7 · Retention

### D2-Q054 · Retention classes for the routes CONVENTIONS gives none: TikTok Display, the Telegram bot, web-search results

- **Class:** user (a reading of platform terms and of what clients may be promised; counsel confirms before production)
- **Settles:** CF-104
- **Blocks:** F3 (it seeds `retention_classes`), F8 (TTLs by class), C6, C14, then TT1, TG1, TG2, W1, W2, W3, W4, YT9

**Context.** Every record carries a `retention_class` chosen by route (`CONVENTIONS L247`), and the six classes (`CONVENTIONS L75` to `L80`) name none for three routes:

- TikTok Display API (green, client-authorised accounts): README decision 8 proposes `tiktok_display` (`README L185`); tt-client-videos-fetcher writes it, "proposed and not yet in `retention_classes`" (`tt-client-videos-fetcher §6.2 L106`, `L115`), kept "while the authorisation is active and deleted on revocation, client offboarding or TikTok's request, as `meta_on_request` does" (`§14 Q2 L177`).
- Telegram Bot API (green, channels and groups whose owners added the bot): both receivers write `vendor_agreed` (`tg-bot-channel-receiver §6.2 L125`, `tg-discussion-receiver §6.2 L129`), a class defined "per the vendor contract" with a default of 24 months for raw text (`CONVENTIONS L79`), although no vendor is involved; both ask for a dedicated class (`tg-bot-channel-receiver §14 Q5 L198`, `tg-discussion-receiver §14 Q5 L202`).
- Web-search results (Perplexity, Mojeek, GDELT): they carry `news_excerpt` (`web-search-perplexity §6.2 L106`, `web-search-mojeek §6.2 L105`, `web-gdelt-poller §6.2 L109`), whose only clock is the 7-day full-text cache (`retention-purger §5.3 L67`), for records that hold a title, a snippet and a URL but no full text; retention-purger leaves both open "to be set with counsel" (`retention-purger §14 Q3 L172`).

**Options**

1. **Add `tiktok_display` and `telegram_bot`; keep web results under `news_excerpt` (recommended).** `tiktok_display`: kept while the client's authorisation is active; deleted on revocation, client offboarding or TikTok's request (the `meta_on_request` clock under TikTok's name). `telegram_bot`: kept while the channel's owner keeps the bot and the client relationship lasts; deleted on the owner's or client's request, on offboarding, or on a member's request; commenters' identities are already hashed at the edge (D2-Q010). Web results stay `news_excerpt`, with CONVENTIONS stating that the class keeps excerpts and metadata and that its 7-day clock applies only where full text is cached. Consequences: F3 seeds eight classes; each route's clock matches its terms; counsel reviews the two new clocks before production (G4).
2. **Add all three, with a `web_result` class of its own.** Consequences: as option 1, plus a clock for web snippets that can differ from news excerpts (for example a shorter one if a search provider's terms require it).
3. **Map each route to an existing class.** `tiktok_display` as `meta_on_request`, Telegram bot data as `vendor_agreed`, web results as `news_excerpt`, with the mapping written in CONVENTIONS. Consequences: no new classes, but Telegram bot data keeps a vendor-contract clock with no vendor behind it (24 months by default), and the provenance statement names Meta's rule for TikTok data.

**Why the recommendation.** The two green routes rest on the property owner's consent, so their data should go when that consent or the client relationship ends, which neither `vendor_agreed` nor a Meta-named class says; web snippets fit `news_excerpt` once its clock is worded for records without full text.

**Phase 2 records.** ADR "Retention classes for TikTok Display, the Telegram bot and web search" (Applies to: retention-purger, store-writer, tt-client-videos-fetcher, tg-bot-channel-receiver, tg-discussion-receiver, the web engines). CONVENTIONS v1.1, retention classes (L73 to L81): the two new classes and the `news_excerpt` wording. `DEFERRED.md`: counsel's confirmation of both clocks, owner G4.

### D2-Q055 · LinkedIn data: which class holds what, and the 24-hour and six-week rules

- **Class:** user (a reading of LinkedIn's terms, which `li-company-posts-poller`, `li-post-search` and `li-post-comments-fetcher` leave "until legal decides")
- **Settles:** CF-105, AU-078
- **Blocks:** F3, F8, C4, C6, C14, then LI1, LI2, LI3, VLI1, VLI2, VLI3, VLI4

**Context.** CONVENTIONS defines `linkedin_48h` ("member social-activity data purged after 48 hours; organization data as the API terms allow", L77) and quotes the terms: "member social-activity data stored at most 48 hours; most member profile data 24 hours; organization social activity data six weeks (six months if authenticated)" (L192). Classes follow the route (L247), so amber LinkedIn would get `vendor_agreed` (24 months by default, L79). The PRDs split:

- Amber: posts carry `vendor_agreed` (`li-post-search §6.2 L92`, `li-company-posts-poller §6.2 L114`), but member reposts are held as `linkedin_48h` until legal decides (`li-company-posts-poller §7 L133`), and vendor comments carry `linkedin_48h`, "the stricter option, until legal decides" (`li-post-comments-fetcher §6.2 L120`, `§7 L139`); each asks the question the other way round (`li-post-search §14 Q2 L164`, `li-company-posts-poller §14 Q5 L188`, `li-post-comments-fetcher §14 Q1 L192`).
- Green: one class, `linkedin_48h`, for organization posts and member fields, which retention-purger should apply "by field" (`li-client-posts-poller §7 L135`), while retention-purger purges by kind and has no field-level mode (`retention-purger §5.3 L64`, `L70`; AU-078). Whether six weeks or six months applies is open and also sets the backfill cap (`li-client-posts-poller §5.1 L50`, `§14 Q2 L188`).
- Member profile data at 24 hours (`li-post-search §7 L115`, `li-org-resolver §7 L115`, `li-company-posts-poller §7 L133`) has no class.

**Options**

1. **Class by content, the stricter reading for members, and no member data inside organization records (recommended).** Member-authored content (comments, member posts, reposts of member posts) is `linkedin_48h` on every route, green and amber, counted from `fetched_at`. Organization-authored posts and their counts get a new class `linkedin_org` on the green route (six weeks, until counsel confirms that our access counts as "authenticated" for six months) and `vendor_agreed` on the amber route. Member fields inside an organization post (a mentioned member, an administrator) are hashed or dropped by the adapter before the first write (option 2 of AU-078, consistent with D2-Q010), so no field-level purge is needed. Member profile data is never stored, since individuals are never profiled (CONVENTIONS L114), so no 24-hour class exists. Consequences: one class per record, which retention-purger and the ClickHouse TTLs can apply; the green backfill cap is six weeks for now.
2. **`linkedin_48h` on every LinkedIn record, green and amber, with field-level rules in retention-purger** (organization fields six weeks, member fields 48 hours, profile fields 24 hours). Consequences: one class, but retention-purger and F8 need per-field purges that no other platform needs, and amber organization posts lose their vendor-contract lifetime.
3. **Class by route as CONVENTIONS says:** `vendor_agreed` on every amber record and `linkedin_48h` on every green one, after legal confirms the vendor contract. Consequences: the simplest, but member comments bought from a vendor would be kept 24 months against LinkedIn's 48-hour rule for the same data, and green organization posts would be deleted at 48 hours unless the purger works per field.

**Why the recommendation.** It applies LinkedIn's strictest clocks to members on every route, keeps organization data as long as the terms allow, and avoids a field-level purge by not storing member fields in organization records.

**Phase 2 records.** ADR "LinkedIn retention" (Applies to: every LinkedIn service, retention-purger, store-writer). CONVENTIONS v1.1: `linkedin_org` added; L77 reworded (member content, every route, from `fetched_at`); L192 cross-referenced. `DEFERRED.md`: counsel on "authenticated" (six weeks or six months), owner LI1.

### D2-Q056 · How long derived data lives: ten years, YouTube's 36 months, LinkedIn's 48 hours, and what YouTube's 30-day rule covers

- **Class:** user (a reading of the YouTube and LinkedIn terms, which sets what clients can see after three years)
- **Settles:** CF-106, AU-080
- **Blocks:** F3, F8 (TTLs), C6, C13, C14, C15, then YT1, YT4, YT5, YT7, LI2, VLI4

**Context.** CONVENTIONS keeps "Aggregates and derived scores: ten years, all classes" (L81) while `youtube_30d_text` keeps "derived metrics ... up to 36 months" (L76), from the YouTube fact sheet: "raw comment text no longer than 30 days (delete or refresh), derived metrics up to 36 months for 'Analytics & Reporting' clients, no aggregation across channels of different owners except under the carve-out" (L209). The PRDs apply it three ways: store-writer expires YouTube item rows at "created + 36 months" (`store-writer §5.3 L76`); yt-text-purger deletes items, `analysis` and hit rows when "the last `fetched_at` is older than 36 months" and leaves aggregates (`yt-text-purger §5.3 L118`, `§13 L259`); retention-purger never selects aggregates (`retention-purger §5.3 L68`; AU-080); the question is still open in `yt-comments-fetcher §14 Q5 L207` and `yt-video-details-fetcher §14 Q4 L218`. For LinkedIn, store-writer deletes `linkedin_48h` rows "with its `analysis` rows" (`store-writer §5.3 L77`, asked in `§14 Q3 L183`), the comment fetchers test the same (`li-own-comments-fetcher §13 L178`), while li-client-posts-poller keeps derived scores ten years (`li-client-posts-poller §7 L135`). And the 30-day clock covers "raw comment text" in CONVENTIONS, but yt-text-purger also runs it on video titles and descriptions (`yt-text-purger §3 L19`, `§5.3 L120`, open in `§14 Q1 L266`) and yt-channel-resolver on channel profiles (`yt-channel-resolver §6.2 L113`).

**Options**

1. **Item-level derived rows follow their item's class; aggregates keep ten years except per-channel YouTube rollups; the 30-day rule covers all stored YouTube text (recommended).** Analysis scores, hits and metrics time series of a YouTube item expire 36 months after the item's creation (store-writer's anchor); those of a LinkedIn member item go with it at 48 hours. Rollups keep ten years, except rollups at the level of one YouTube channel, which follow the 36 months (AU-080 option 3); rollups across many channels and owners keep ten years only under the analytics carve-out the fact sheet names. The 30-day refresh-or-delete clock applies to comment text, video titles and descriptions and channel profile text, as yt-text-purger and yt-channel-resolver assume. CONVENTIONS L81 is reworded accordingly. Refresh is part of the service, not an option clients buy: yt-text-purger refreshes the text of comments on client-watched sources within a share of the `comments` bucket set in the pilot and deletes, at 30 days, the text it cannot refresh in time (metrics stay), so no `yt_text_refresh` entitlement is added to `clients` in v1 (`yt-text-purger §14 Q3`). Consequences: one anchor (creation); YouTube trends older than three years survive only as cross-channel rollups; more refresh calls on the YouTube quota for titles and profiles (yt-text-purger already budgets them).
2. **Ten years for every derived row and aggregate, as CONVENTIONS L81 says;** the YouTube and LinkedIn limits apply only to raw text and identities. Consequences: the longest history for clients; per-item YouTube scores and metrics outlive the 36 months the fact sheet quotes, a risk at YouTube's audit ("audit at any time", L209).
3. **Per-class lifetimes for both item rows and aggregates:** every YouTube-derived aggregate also capped at 36 months. Consequences: the most conservative; YouTube disappears from ten-year trend lines after three years.

**Why the recommendation.** It follows the fact sheet's wording where it is specific (36 months, 30 days, no cross-owner aggregation), keeps the ten-year promise for everything else, and gives retention-purger one anchor per class.

**Phase 2 records.** ADR "Lifetimes of derived data" (Applies to: store-writer, aggregator, retention-purger, yt-text-purger, yt-channel-resolver, deletion-propagator). CONVENTIONS v1.1: L76 (what the 30-day clock covers, the 36-month anchor), L81 (the exceptions). `DEFERRED.md`: counsel's confirmation of the YouTube reading before G3 for YouTube.

## Group 8 · Rules, series and platform specifics

### D2-Q058 · Engagement-count refreshes on X, LinkedIn, Telegram and Facebook groups

- **Class:** user (a cost choice: on X each refresh is a paid post read)
- **Settles:** CF-082, AU-032
- **Blocks:** C11, VTG3, LI1, VLI3, X1, X3, X4

**Context.** CONVENTIONS refreshes likes, shares, views and comment counts at +24 h and +7 d on every route (L65). The README records counts on X, LinkedIn and Telegram at first sight only, leaving refreshes as an open question (`README L25`); comment-decay-scheduler does the same and asks (`comment-decay-scheduler §5.1 L68`, `§14 Q6 L207`). tg-channel-posts-poller expects a +24 h views refresh for tier-1 posts on a `metrics` job that the scheduler never emits, and asks whether it is worth its cost (`tg-channel-posts-poller §5.1 L56`, `§14 Q5 L195`; AU-032); li-company-posts-poller leaves it open (`li-company-posts-poller §5.4 L92`, `§14 Q3 L186`). Prices from the fact sheets: X USD 0.005 per post read (about 0.6 million X posts a month, CONVENTIONS L3), Apify Telegram Actors about USD 2,900 to 7,200 a month at 2.4 million items, harvestapi about USD 225 to 300 a month at 0.15 million LinkedIn items (L87, L93, L94).

**Options**

1. **First-sight counts only on X, LinkedIn and Telegram in v1 (recommended).** CONVENTIONS L65 is amended to name the routes that refresh (Facebook Pages, Instagram, TikTok, YouTube) and those that record counts at first sight (X, LinkedIn, Telegram, and amber Facebook groups, whose post counts no service refreshes either, `fb-group-posts-poller §14 Q6`); tg-channel-posts-poller drops its `metrics` job. Consequences: no extra spend; trend charts on these three platforms show counts as first seen; the question can come back after the pilot with measured costs.
2. **A Telegram tier-1 +24 h views refresh only**, as tg-channel-posts-poller describes, first sight elsewhere. Consequences: one more lane in comment-decay-scheduler; Apify charges per item re-read.
3. **+24 h and +7 d refreshes on every route, as CONVENTIONS says.** Consequences: about two extra paid reads per X post (at 0.6 million posts a month, roughly USD 6,000 a month more at list price) and two extra vendor reads per LinkedIn and Telegram item.

**Why the recommendation.** It matches the README and the scheduler as written and avoids a cost that is large on X before the pilot shows clients need it.

**Phase 2 records.** ADR "Count refreshes on X, LinkedIn and Telegram" (Applies to: comment-decay-scheduler, tg-channel-posts-poller, li-company-posts-poller, the X pollers). CONVENTIONS v1.1, L65. `DEFERRED.md`: revisit after G2 with measured costs, owner C11.

### D2-Q061 · The Disqus comment series

- **Class:** technical
- **Settles:** CF-108, AU-041, AU-107
- **Blocks:** C11, N2, N8

**Context.** Four documents give Disqus sites the short series +6 h, +24 h, +3 d (`CONVENTIONS L269`, `comment-decay-scheduler §5.1 L58`, `news-comments-fetcher §5.1 L43`, `news-article-extractor §5.1 L47`); news-site-resolver, an approved PRD, promises the full decay series (+1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30) when it onboards a site (`news-site-resolver §5.1 L41`). AU-041 and AU-107 put the same question from the two audit passes.

**Options**

1. **The short series, as CONVENTIONS, the scheduler and the fetcher say; news-site-resolver's sentence corrected (recommended).** Consequences: no change to the `news_disqus` estimate; news comments, which arrive mostly in the first days, are fetched three times; an approved PRD gets a one-line edit under D2-Q001.
2. **The full decay series for Disqus.** Consequences: CONVENTIONS, the scheduler profile and news-comments-fetcher change, and `news_disqus` is re-estimated for five more steps per article.

**Why the recommendation.** Three of the four documents and the code-owning PRDs agree, and the extra steps would cost Disqus calls for comment threads that are usually quiet after three days.

**Phase 2 records.** ADR "Disqus series" (Applies to: comment-decay-scheduler, news-comments-fetcher, news-site-resolver). No CONVENTIONS change (L269 stands).

### D2-Q062 · When a missing post or comment becomes a deletion

- **Class:** technical
- **Settles:** CF-113, AU-085
- **Blocks:** F4 (the shared rule in the SDK), C13, then FB4, FB5, VFB3, YT4, YT5, VTT5, VTT6, X6, VIG2, IG3, IG6, LI1, LI2
- **Depends on:** D2-Q035 (the `deletions` message)

**Context.** CONVENTIONS turns missing comments into `deletions` with reason `platform_sync` "when the API is complete" (L63) and has no rule for posts. The PRDs differ (CF-113): fb-reactions-fetcher deletes a post on one "not found" (`fb-reactions-fetcher §8 L144`) while the two other Facebook readers of the same posts never delete on one error (`fb-post-comments-fetcher §8 L143`, `fb-group-comments-fetcher §8 L145`); yt-video-details-fetcher and tt-video-stats-refresher confirm with a second request (`yt-video-details-fetcher §5.2 L62`, `tt-video-stats-refresher §5.2 L60`); tt-video-comments-fetcher waits for two consecutive full reads (`§8 L138`); X replies and Instagram vendor comments never delete on absence (`x-replies-fetcher §8 L154`, `ig-comments-fetcher §13 L171`). A post that a comment fetcher finds deleted is handed to a poller that cannot detect it on Instagram, or on LinkedIn after day 7 (AU-085). deletion-propagator acts on the first message it receives, so the strictest reader decides.

**Options**

1. **One rule in the SDK: absence becomes a deletion only after a confirmed second miss, or on a platform deletion signal; and routes whose reads are not complete listings never delete on absence (recommended).** A fetcher that misses an item records a suspicion; the next read (or one confirming request within the job) that misses it again emits `deletions` with `platform_sync`. A platform signal (a webhook `remove`, X compliance, a 404 on the item's own endpoint where the platform documents it as deleted) counts as confirmation. Routes listed in CONVENTIONS as "no deletion on absence": X replies (x-compliance-sync is the deletion source), Instagram vendor comments (about 15 visible comments), keyword and hashtag searches. A comment fetcher that finds the post itself gone emits the post's deletion under the same rule rather than handing it to a poller. Consequences: one implementation and one test in F4; fb-reactions-fetcher is aligned; a deleted post stays visible for one more read cycle.
2. **CONVENTIONS extended to posts: one complete read that misses the item is enough.** Consequences: faster removal, but a transient error or a partial page on one service erases a post others still see.
3. **Per route as written**, with fb-reactions-fetcher aligned to the other Facebook readers and the never-delete routes recorded. Consequences: the least change, but five behaviours to build and test.

**Why the recommendation.** Deletion is irreversible downstream (deletion-propagator removes derived rows and recomputes aggregates), so one confirmation costs little; listing the routes where absence means nothing removes the false deletions D1 found.

**Phase 2 records.** ADR "Deletion on absence" (Applies to: every fetcher that refetches, deletion-propagator, listening-sdk). CONVENTIONS v1.1, L63 extended to posts with the confirmation rule and the list of routes that never delete on absence.

### D2-Q063 · Which X keyword rules go on the filtered stream

- **Class:** technical
- **Settles:** CF-115
- **Blocks:** X1, X4

**Context.** The filtered stream holds up to 1,000 rules (`CONVENTIONS L87`). x-filtered-stream fills them in order: "client brand keyword sets (one rule each, priority 1), tier-1 accounts (priority 1), tier-2 (2), tier-3 (3)" (`x-filtered-stream §5.1 L40`, `§13 L191`); x-recent-search says "Tier-1 keyword rules also run as stream rules on x-filtered-stream; the 15-minute search stays on as the safety net" (`x-recent-search §5.1 L47`), without saying whether other keyword rules are streamed. How many rules keyword coverage takes decides how many accounts get real-time coverage, and how cost splits between stream and search (both are paid per post read).

**Options**

1. **Streamed rules chosen by priority within a fixed share (recommended).** Tier-1 keyword rules (a client's brand and priority terms) come first, up to a configured share of the 1,000 rules (half, as the starting value); tier-1 accounts fill the rest, then tier 2 and 3; x-recent-search keeps searching every keyword rule, the tier-1 ones every 15 minutes as the safety net. Both PRDs state the same order and the share. Consequences: keyword coverage can never crowd out tier-1 accounts; the share is a setting the pilot tunes.
2. **Every client brand keyword set on the stream**, as x-filtered-stream says. Consequences: accounts get only the rules keywords leave over; x-recent-search's cost split is rewritten.
3. **Only tier-1 keyword rules on the stream**, the narrow reading of x-recent-search. Consequences: lower stream volume; brand sets below tier 1 rely on 60-minute search.

**Why the recommendation.** It honours both PRDs' order and puts the trade-off in one number that can change without a contract change.

**Phase 2 records.** ADR "X stream rule allocation" (Applies to: x-filtered-stream, x-recent-search). No CONVENTIONS change beyond a note under the X fact sheet.

## Group 9 · Legal policies and the editorial pass

### D2-Q068 · Using platform content for models and media: training and evaluation data, Content Signals, stored media

- **Class:** user (readings of the platforms' terms, the vendor contracts and Iraqi copyright law; counsel confirms)
- **Settles:** (none)
- **Blocks:** A0 first (it labels 2,000 or more Iraqi items into train, dev and test splits and needs only D2, A0 brief), then A1, A2, A3, A4, N1, N6

**Context.** The four analysis PRDs ask the same question: "May each platform's content and vendor data be used to train and evaluate in-house models, and for how long? Legal to confirm" (`analysis-sentiment §14 Q3`; the same in `analysis-entities §14 Q7` and `analysis-topics §14 Q7`). A0 builds the labelled evaluation set from staging samples and freezes train, dev and test splits (A0 brief, "Builds"). The terms quoted in CONVENTIONS pull in different directions: Meta allows no sale or licensing of Platform Data, and a Tech Provider "processes only on behalf of its client" (L163); TikTok forbids "building profiles or databases on any individual" (L178); X forbids surveillance and profiling on sensitive attributes (L188); LinkedIn keeps member data 48 hours and forbids export to customers (L192); Instagram allows analytics "only as aggregated, de-identified output" (L171); news is stored as excerpts under Iraqi copyright law (Law No. 3 of 1971), with full text only in a 7-day cache (L213). Two more questions of the same kind sit in the news PRDs: whether a host's Content-Signal `search = no` stops indexing or is a signal only (`news-robots-checker §14 Q1`, proposed: a stop), and how `ai-input = no` affects model analysis of excerpts and of the cache (`news-robots-checker §14 Q2`, `news-article-extractor §14 Q2`). And analysis-media asks whether platform media may be stored under each platform's terms and each vendor contract, and whether thumbnails only is right for YouTube (`analysis-media §14 Q2`), which README decision 7 proposes "pending legal review" (`README L184`).

**Options**

1. **Evaluate on de-identified platform content; train only on data cleared for training; honour Content Signals; store media only where the terms allow (recommended).**
   - (a) Evaluation: A0's dev and test sets may hold de-identified platform items (no names or handles, author references only, D2-Q010), each kept no longer than its retention class allows, never shared outside the service.
   - (b) Training and fine-tuning: only data whose terms allow it: news text not marked `ai-train = no`, client-owned content with the client's written consent, licensed or public datasets, and vendor data whose contract allows training. Platform content from Meta, TikTok, X, LinkedIn and YouTube is not used to train until counsel confirms it platform by platform (`DEFERRED.md`, owners A1 to A4).
   - (c) Content Signals: `search = no` stops indexing that host (news-robots-checker's proposal); `ai-input = no` keeps that host's excerpts and cached text out of model analysis (sentiment, topics, entities), while keyword matching, which is not a model, still runs; the signal travels on the item so the analysis services can skip it; `ai-train = no` keeps the text out of every training set.
   - (d) Media: images are stored under `media/<sha256>` only where the platform's terms and the vendor contract allow, under the item's retention class; YouTube stays thumbnails only in v1 (README decision 7); audio and video are downloaded nowhere until counsel confirms per platform.

   Consequences: A0 can start on real Iraqi-dialect samples after G2; models are fine-tuned on a smaller, cleaner set at first; the `ai-input` signal needs one field on `items.normalized` (D2-Q005's `context` or a declared field), which F2 adds.

2. **Train and evaluate on all collected content, de-identified, within each item's retention class.** Consequences: the best Iraqi-dialect models soonest, but a legal exposure under several platforms' terms (Meta's "on behalf of its client", TikTok's database rule) that counsel may later force the platform to unwind, with retraining.
3. **No platform content in any model set:** public datasets, synthetic and annotator-written examples only. Consequences: no exposure, but weaker dialect models and an evaluation set that does not look like the data clients see; A0's plan changes.

**Why the recommendation.** Evaluation on de-identified samples is what any analytics product needs to measure itself, and it creates no new store beyond what retention already allows; training is where the terms bite, so it waits for counsel per platform, and the news signals are honoured as their publishers set them.

**Phase 2 records.** ADR "AI and media use of platform content" (Applies to: A0, the four analysis services, news-robots-checker, news-article-extractor). CONVENTIONS v1.1, "Security and compliance in every service": the evaluation and training rules, the three Content-Signal rules, the media rule. `DEFERRED.md`: counsel's per-platform confirmation of training use (owners A1 to A4) and of media storage (owner A4).

### D2-Q069 · Legal policies the deletion and audit paths need: author requests, deadlines, backups, audit retention, the X rules

- **Class:** user (each point is a legal policy; the recommendation gives a buildable default for counsel to confirm before G4)
- **Settles:** AU-079
- **Blocks:** C13, C14, X7, I1 (backups), D3 (the admin console's intake of requests), then G4

**Context.** The deletion and audit services leave several policies "to be agreed with counsel": who verifies the identity of an author who files a request (`retention-purger §14 Q1`, proposed: a confirmation sent to the platform account's public contact); the grace period of the `meta_on_request` necessity clock and how long audit records are kept (`retention-purger §14 Q4`); deletion deadlines for non-X `platform_sync` and for `legal` requests (`deletion-propagator §14 Q6`); backups and snapshots, which "must expire inside the shortest deadline or be excluded" (`deletion-propagator §14 Q1`); whether X's 24-hour clock runs from X's compliance signal or from the event on X (`x-compliance-sync §14 Q1`; CONVENTIONS L186 says "deletions must be mirrored within 24 hours"); how long identifiable X items, evidence files and audit records are kept (`x-compliance-sync §14 Q7`); and who screens client keyword terms for "sensitive events (protests, rallies)", which X forbids monitoring (`x-full-archive-search §14 Q4`; CONVENTIONS L188). One entry adds a registry question: an erasure request from someone whose account is a registered source has no producer for the registry decision and no reason value for it (`deletion-propagator §14 Q3`, proposed: retention-purger emits it; AU-079).

**Options**

1. **Strict defaults that can be built now, each confirmed by counsel before G4 (recommended).**
   - (a) An author request that matches a registered source deletes the requested items like any other; the source stops being monitored only if the request asks for that, through a `retire` decision with reason `owner_request` that retention-purger sends and registry-writer audits (AU-079).
   - (b) Identity check: a confirmation sent to the account's public contact on the platform, as retention-purger proposes; the admin console (D3) records the request and the confirmation.
   - (c) Deadlines: every deletion is engineered to the strictest documented deadline, X's 24 hours, on every route, until counsel sets per-reason deadlines; the X clock is read from X's compliance signal, with the compliance stream reconsidered at X's Enterprise review.
   - (d) Backups may live longer than the deadline only if every restore re-applies the deletion log (`deletion_requests` and the tombstones of D2-Q035) before any data is served; I1 builds the restore procedure that way.
   - (e) Audit and evidence rows hold ids, hashes, reasons and timestamps only, never content or clear identities, and are kept for the life of the client contract until counsel sets a period; the `meta_on_request` grace period is counsel's.
   - (f) X sensitive events: client keyword terms are screened when they are entered, against a list of sensitive-event terms that the user's compliance owner keeps; a flagged term is not run on X; the screening result is a column on `keywords` (D2-Q044), written by the client portal (D3).

   Consequences: C13, C14 and X7 have a target to build and test; I1 designs backups around replay-after-restore; a few lines in the portal and admin console specs (D3).

2. **Leave every point to counsel before the services are built.** Consequences: no guess to unwind, but C13, C14 and X7 cannot finish their acceptance tests, and I1 cannot design backups.
3. **Per-route deadlines now, from each platform's terms as read by the team** (X 24 hours; others longer), with backups excluded from deletion entirely. Consequences: less engineering pressure, but a restore could resurface deleted data, and the team, not counsel, reads the terms.

**Why the recommendation.** The strictest documented deadline and replay-after-restore are safe whatever counsel decides, so building to them loses nothing; the points that only counsel can settle stay open without blocking the build.

**Phase 2 records.** ADR "Legal policies for deletions and audits" (Applies to: deletion-propagator, retention-purger, x-compliance-sync, registry-writer, I1, D3). CONVENTIONS v1.1, "Security and compliance in every service": the defaults (a) to (f). `DEFERRED.md`: counsel's confirmation of each point, owner G4.

### D2-Q070 · One editorial pass: the documents that disagree with themselves

- **Class:** technical
- **Settles:** CF-027, CF-117, RN-17
- **Blocks:** F2 first (one spelling per field), then F5, C1, C2, C4, C5, FB3, N1, N6, TG1, W1, W2, W4, W5, YT5, YT6 (and every session that quotes CONVENTIONS or the README literally)

**Context.** CF-027 lists nine places where one PRD names a message field two ways, its prose against its own example: a) keyword-matcher's set hash is `set_version` in prose (`keyword-matcher §5.3 L58`, `L77`) and `keyword_set_version` in the example, rendered `"cs:3f9a1c"` while the `message_id` embeds `cs3f9a1c` (`§6.2 L100`, `L107`); b) news-robots-checker writes `robots_status` (`§5.3 L71`) and `robots.status` (`§13 L168`, `§6.2 L102`), and maps the Content-Signal values `ai-input` and `ai-train` to fields `ai_input` and `ai_train` without saying so (`§5.3 L73`, `§6.2 L107`); c) the web engines set `normalize = skip` on records whose envelope lists have no such field (`web-search-perplexity §5.2 L55`, `§6.2 L89`, and the same in web-search-mojeek and web-gdelt-poller); d) normalize-item names `lang_pending`, `text_full_ref` and `author_followers`, which its example lacks (`normalize-item §8 L133`, `§5.3 L72`, `§5.4 L79`); e) fb-backfill's envelope is "identical to fb-page-feed-poller's except `service` and `metrics_observation`" yet adds a `window` object (`fb-backfill §6.2 L88`, `L104`); f) tg-bot-channel-receiver writes "the `channel_post` object unchanged" while edits arrive as `edited_channel_post` (`tg-bot-channel-receiver §6.2 L113`, `§5.2 L59`); g) raw-archiver's `raw.replay` example lacks envelope fields its own list has (`raw-archiver §6.2 L98-L115`, `§5.4 L86`); h) news-article-extractor promises the extraction code version in the payload but shows only `"extractor": "trafilatura"` (`§12 L167`, `§6.2 L120`); i) web-commoncrawl-scanner computes `accept_rate` "from `source.events`", which its reads omit (`§10 L136`, `§6.1 L80`).

CF-117 collects five inconsistencies that break nothing alone but that build sessions would quote literally:

- a) Replies "through the same service with job kind `replies`" (`CONVENTIONS L60`), while YouTube replies have their own service, yt-replies-fetcher (`CONVENTIONS L265`).
- b) The X cap "per billing cycle" (`CONVENTIONS L87`; `quota-governor §5.1 L53`, `§5.3 L78`) against "per month on pay-per-use" (`CONVENTIONS L187`; `x-full-archive-search §7 L139`).
- c) Route values written "GREEN", "AMBER", "RED" (`CONVENTIONS L7`), `route` green or amber in the registry (L36), and `shared` in the PRD header template (L122); six lanes in the template (L122), seven in the addendum, which adds "Comments and stats" (L275).
- d) Service names take a platform prefix (L11), yet search-hit-router is listed under Web without `web-` (L234).
- e) The README lists "Google search results" among things only amber services reach (`README L18`) though every web-search service is green (`README L143` to `L147`) and CONVENTIONS has no Google route (L217); it calls tt-hashtag-feed-poller a hashtag poller (L70) but lists it among the search services (L22, L30); it says the nine decisions are "consistent across the PRDs that use them" (L176) while D1 found conflicts against all nine.

D1's review note 17 adds one: `docs/contracts/INVENTORY.md` lists "Known corrections from the review" (L20 to L34) without applying them to its rows.

**Options**

1. **One editorial pass, each point decided here so F2 has one spelling (recommended).** For CF-027: a) the field is `keyword_set_version`, one rendering (`cs:<hex>`), and keyword-matcher's replay-stable `message_id` is derived from it as D2-Q002 and D2-Q006 describe; b) `crawl.policies` uses the flat names of the `crawl_policies` row (D2-Q040), `robots_status`, with each Content-Signal directive mapped to a field by replacing the hyphen with an underscore (`ai_input`, `ai_train`, `search`), stated once; c) `normalize = skip` disappears: the engines' raw responses use the archive-only record kind of D2-Q008; d) `lang_pending` and `text_full_ref` join `items.normalized/v1`, and `author_followers` too but only for authors who are registered sources (individuals carry no profile data, D2-Q010); e) fb-backfill's `window` is a declared field of the envelope's `context` (D2-Q005); f) the receiver writes each update as returned, `channel_post` or `edited_channel_post`, and an edit reuses the post's key (D2-Q009); g) moot, since there is no `raw.replay` topic (D2-Q039); h) the payload carries `extractor` and `extractor_version`; i) web-commoncrawl-scanner's reads gain `source.events`. For CF-117: a) Replies are job kind `replies` on the comment service's queue, except where a route has a dedicated replies service (YouTube's yt-replies-fetcher), which CONVENTIONS lists. b) The X cap is "per billing cycle", the term X's pay-per-use plan uses; quota-governor's period follows the billing cycle. c) Route values are lower case `green` and `amber` in data; "RED" stays prose for what is never built; `shared` is a PRD header label only, never a `route` value; seven lanes, with the template updated. d) search-hit-router keeps its name, recorded as the one listed exception to the prefix rule (it routes results of several platforms, not only web). e) The README's sentences are reworded to match the service lists and to point to D2's decisions. RN-17: `INVENTORY.md` stays D1's record "as written in the PRDs" and its rows are not edited; CONVENTIONS v1.1 says, where it lists the contract documents, that the ADRs, CONVENTIONS itself, F2's `VERSIONING.md` and F3's `TABLE-OWNERS.md` are the contract and the inventory is background. Consequences: one pass by phase 2; nothing in the contracts changes except the route enum's case.
2. **A blanket rule for CF-027: the section 6.2 example always wins** (or the prose always wins), with CF-117 as in option 1. Consequences: simpler to state, but the example rule deletes `normalize = skip` and `text_full_ref`, which other decisions rely on, and the prose rule keeps `set_version` beside a message id that no longer embeds it.
3. **Leave the documents and let each owning session pick, recording the readings only in its handoff.** Consequences: no edits now, but F2 freezes before those sessions run, so it would have to guess, and every session keeps quoting the inconsistent lines.

**Why the recommendation.** Each point has an answer that matches how the PRDs already behave and what the other decisions recommend, and F2 needs one spelling before it freezes; fixing the text once is cheaper than every session asking.

**Phase 2 records.** ADR "Editorial corrections" (Applies to: all; the nine CF-027 PRDs by name). The CF-027 spellings go to F2 through the ADR; the PRD lines are corrected citing it. CONVENTIONS v1.1 L7, L11, L60, L87 and L187, L122, L234, L275, and the sentence on the contract documents; README L18, L22, L30, L70 and L176, each edit citing the ADR.

## Appendix A · Every CF and AU entry and its decision

| Entry  | Decision     | Entry  | Decision     | Entry  | Decision     |
| ------ | ------------ | ------ | ------------ | ------ | ------------ |
| CF-001 | D2-Q002      | CF-002 | D2-Q003      | CF-003 | **unplaced** |
| CF-004 | D2-Q005      | CF-005 | D2-Q005      | CF-006 | D2-Q005      |
| CF-007 | **unplaced** | CF-008 | **unplaced** | CF-009 | **unplaced** |
| CF-010 | **unplaced** | CF-011 | **unplaced** | CF-012 | **unplaced** |
| CF-013 | **unplaced** | CF-014 | **unplaced** | CF-015 | **unplaced** |
| CF-016 | **unplaced** | CF-017 | **unplaced** | CF-018 | **unplaced** |
| CF-019 | **unplaced** | CF-020 | **unplaced** | CF-021 | **unplaced** |
| CF-022 | **unplaced** | CF-023 | **unplaced** | CF-024 | **unplaced** |
| CF-025 | D2-Q022      | CF-026 | **unplaced** | CF-027 | D2-Q070      |
| CF-028 | **unplaced** | CF-029 | **unplaced** | CF-030 | **unplaced** |
| CF-031 | **unplaced** | CF-032 | **unplaced** | CF-033 | **unplaced** |
| CF-034 | **unplaced** | CF-035 | **unplaced** | CF-036 | **unplaced** |
| CF-037 | **unplaced** | CF-038 | **unplaced** | CF-039 | **unplaced** |
| CF-040 | **unplaced** | CF-041 | **unplaced** | CF-042 | **unplaced** |
| CF-043 | **unplaced** | CF-044 | **unplaced** | CF-045 | **unplaced** |
| CF-046 | **unplaced** | CF-047 | **unplaced** | CF-048 | **unplaced** |
| CF-049 | **unplaced** | CF-050 | **unplaced** | CF-051 | **unplaced** |
| CF-052 | **unplaced** | CF-053 | **unplaced** | CF-054 | **unplaced** |
| CF-055 | **unplaced** | CF-056 | **unplaced** | CF-057 | **unplaced** |
| CF-058 | **unplaced** | CF-059 | **unplaced** | CF-060 | **unplaced** |
| CF-061 | **unplaced** | CF-062 | **unplaced** | CF-063 | **unplaced** |
| CF-064 | **unplaced** | CF-065 | **unplaced** | CF-066 | **unplaced** |
| CF-067 | **unplaced** | CF-068 | **unplaced** | CF-069 | D2-Q010      |
| CF-070 | **unplaced** | CF-071 | **unplaced** | CF-072 | **unplaced** |
| CF-073 | **unplaced** | CF-074 | **unplaced** | CF-075 | **unplaced** |
| CF-076 | **unplaced** | CF-077 | **unplaced** | CF-078 | **unplaced** |
| CF-079 | **unplaced** | CF-080 | **unplaced** | CF-081 | **unplaced** |
| CF-082 | D2-Q058      | CF-083 | **unplaced** | CF-084 | **unplaced** |
| CF-085 | **unplaced** | CF-086 | **unplaced** | CF-087 | **unplaced** |
| CF-088 | **unplaced** | CF-089 | **unplaced** | CF-090 | **unplaced** |
| CF-091 | **unplaced** | CF-092 | D2-Q022      | CF-093 | **unplaced** |
| CF-094 | D2-Q021      | CF-095 | D2-Q049      | CF-096 | D2-Q049      |
| CF-097 | **unplaced** | CF-098 | **unplaced** | CF-099 | **unplaced** |
| CF-100 | D2-Q018      | CF-101 | D2-Q018      | CF-102 | **unplaced** |
| CF-103 | **unplaced** | CF-104 | D2-Q054      | CF-105 | D2-Q055      |
| CF-106 | D2-Q056      | CF-107 | D2-Q019      | CF-108 | D2-Q061      |
| CF-109 | D2-Q010      | CF-110 | **unplaced** | CF-111 | D2-Q022      |
| CF-112 | D2-Q028      | CF-113 | D2-Q062      | CF-114 | **unplaced** |
| CF-115 | D2-Q063      | CF-116 | D2-Q001      | CF-117 | D2-Q070      |
| CF-118 | **unplaced** | AU-001 | **unplaced** | AU-002 | D2-Q005      |
| AU-003 | D2-Q022      | AU-004 | **unplaced** | AU-005 | **unplaced** |
| AU-006 | **unplaced** | AU-007 | **unplaced** | AU-008 | **unplaced** |
| AU-009 | **unplaced** | AU-010 | **unplaced** | AU-011 | **unplaced** |
| AU-012 | **unplaced** | AU-013 | **unplaced** | AU-014 | **unplaced** |
| AU-015 | D2-Q005      | AU-016 | **unplaced** | AU-017 | **unplaced** |
| AU-018 | **unplaced** | AU-019 | **unplaced** | AU-020 | **unplaced** |
| AU-021 | **unplaced** | AU-022 | **unplaced** | AU-023 | **unplaced** |
| AU-024 | **unplaced** | AU-025 | **unplaced** | AU-026 | **unplaced** |
| AU-027 | **unplaced** | AU-028 | **unplaced** | AU-029 | **unplaced** |
| AU-030 | **unplaced** | AU-031 | **unplaced** | AU-032 | D2-Q058      |
| AU-033 | **unplaced** | AU-034 | **unplaced** | AU-035 | **unplaced** |
| AU-036 | **unplaced** | AU-037 | **unplaced** | AU-038 | **unplaced** |
| AU-039 | D2-Q018      | AU-040 | **unplaced** | AU-041 | D2-Q061      |
| AU-042 | **unplaced** | AU-043 | **unplaced** | AU-044 | **unplaced** |
| AU-045 | **unplaced** | AU-046 | **unplaced** | AU-047 | **unplaced** |
| AU-048 | D2-Q010      | AU-049 | **unplaced** | AU-050 | **unplaced** |
| AU-051 | **unplaced** | AU-052 | **unplaced** | AU-053 | **unplaced** |
| AU-054 | **unplaced** | AU-055 | D2-Q022      | AU-056 | **unplaced** |
| AU-057 | **unplaced** | AU-058 | **unplaced** | AU-059 | **unplaced** |
| AU-060 | **unplaced** | AU-061 | **unplaced** | AU-062 | **unplaced** |
| AU-063 | **unplaced** | AU-064 | D2-Q021      | AU-065 | **unplaced** |
| AU-066 | **unplaced** | AU-067 | D2-Q018      | AU-068 | **unplaced** |
| AU-069 | **unplaced** | AU-070 | **unplaced** | AU-071 | **unplaced** |
| AU-072 | **unplaced** | AU-073 | **unplaced** | AU-074 | D2-Q028      |
| AU-075 | D2-Q028      | AU-076 | **unplaced** | AU-077 | **unplaced** |
| AU-078 | D2-Q055      | AU-079 | D2-Q069      | AU-080 | D2-Q056      |
| AU-081 | **unplaced** | AU-082 | **unplaced** | AU-083 | **unplaced** |
| AU-084 | **unplaced** | AU-085 | D2-Q062      | AU-086 | **unplaced** |
| AU-087 | **unplaced** | AU-088 | **unplaced** | AU-089 | D2-Q010      |
| AU-090 | **unplaced** | AU-091 | **unplaced** | AU-092 | **unplaced** |
| AU-093 | **unplaced** | AU-094 | **unplaced** | AU-095 | **unplaced** |
| AU-096 | **unplaced** | AU-097 | **unplaced** | AU-098 | **unplaced** |
| AU-099 | **unplaced** | AU-100 | **unplaced** | AU-101 | **unplaced** |
| AU-102 | **unplaced** | AU-103 | **unplaced** | AU-104 | D2-Q022      |
| AU-105 | **unplaced** | AU-106 | **unplaced** | AU-107 | D2-Q061      |
| AU-108 | **unplaced** | AU-109 | **unplaced** | AU-110 | **unplaced** |
| AU-111 | **unplaced** | AU-112 | **unplaced** | AU-113 | **unplaced** |

## Appendix B · README decisions, foundation choices and review notes

| Id    | Decision                   |
| ----- | -------------------------- |
| RD-1  | **unplaced**               |
| RD-2  | D2-Q018                    |
| RD-3  | D2-Q019                    |
| RD-4  | **unplaced**               |
| RD-5  | D2-Q021                    |
| RD-6  | D2-Q022                    |
| RD-7  | **unplaced**               |
| RD-8  | **unplaced**               |
| RD-9  | **unplaced**               |
| FC-01 | no decision needed (below) |
| FC-02 | **unplaced**               |
| FC-03 | **unplaced**               |
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
| RN-08 | **unplaced**               |
| RN-09 | **unplaced**               |
| RN-10 | **unplaced**               |
| RN-11 | **unplaced**               |
| RN-12 | **unplaced**               |
| RN-13 | **unplaced**               |
| RN-16 | **unplaced**               |
| RN-17 | D2-Q070                    |

### No decision needed

| Id    | Reason                                                                                                                                               |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| FC-01 | D1 found conflicts against all nine README proposals, so each is decided on its own in Group 2 (D2-Q017 to D2-Q025); the row itself needs no answer. |

## Appendix C · Open questions: placement

(placement table pending)
