# D2 summary · The decisions that need you

D2 phase 1 · 7 Oct 2026 · Status: **answered by the user on 7 Oct 2026, with follow-ups on 9 Oct 2026** (see "Answers" at the end); the decisions are ADR-0001 to ADR-0070. The full text of every decision (context, citations, every option with its consequences) is in `docs/decisions/D2-PROPOSALS.md`; this page lists only what you need to answer.

D2 grouped D1's 231 conflict entries (118 in `docs/contracts/CONFLICTS.md`, 113 in `CONFLICTS-ASSUMPTIONS.md`), the README's nine proposed decisions, the build plan's thirteen foundation choices, the 387 open questions of the PRDs and the eight review notes D1 left open into 70 decisions:

- 19 need you: a business, product, vendor, legal or cost choice. They are below, each with its options in one line and the recommendation first.
- 51 are technical: an engineer's choice on the evidence. Their recommendation stands unless you object; they are in the table at the end, so you can object to any by its id.

How to answer: for each user decision, give the option number (or "recommended"), and any change in your own words. "Accept every recommendation" is a valid answer. For the technical table, name the ids you object to, if any. Phase 2 (a fresh session) then writes one ADR per decision, CONVENTIONS v1.1 and `docs/decisions/DEFERRED.md` from your answers.

F2 (contracts), F3 (control-plane schema) and F8 (ClickHouse schema) wait on these answers; the decisions that block them most directly are D2-Q001 to D2-Q016 and the README decisions.

## Decisions that need you

### D2-Q001 · How D2's decisions apply to the twenty "already approved" PRDs

CONVENTIONS L282 says twenty PRDs are "already approved; do not rewrite", but they sit on one side of many conflicts, and in nine places two approved PRDs contradict each other.

- **Recommended (1):** each decision says which side moves; L282 is reworded so that an ADR wins over any PRD, approved or not, and every PRD edit cites its ADR.
- (2) The approved PRDs always win; CONVENTIONS adopts their versions (two spellings of some contracts survive, and the nine approved-against-approved conflicts stay open).
- (3) CONVENTIONS always wins; the approved PRDs are revised (CONVENTIONS is silent on most points, so most entries still need their own answer).

### D2-Q003 · Provenance and `retention_class` on every message

Your rule in `CLAUDE.md` says "every output carries provenance (route, vendor, service, fetched_at) and `retention_class`". Read literally, it also covers job messages and completion reports, which carry no platform data.

- **Recommended (1):** every message that carries or derives from platform data carries one `provenance` object and `retention_class` (items, hits, metrics, analysis, profiles, deletions, robots.txt policies, decisions based on a fetch); job and control messages carry only the name of the service that sent them. Your rule is reworded to "every data output" (text proposed in the decision).
- (2) The same fields flat rather than as one object (closer to today's examples; easier to confuse "who fetched" with "who sent").
- (3) Provenance on every message, control messages included (your rule word for word; jobs carry a fetch time for data they do not hold).
- (4) Provenance only on raw and normalized items; everything else joins back to them (smaller messages; every reader must join to show provenance).

### D2-Q010 · Individuals' identities: one keyed reference, and where it is computed

The PRDs hash people five different ways, under three names, some per source or per channel, and some keep names in the raw archive.

- **Recommended (1):** one keyed reference per person per platform (`author_ref`), computed in the adapter before anything is stored, on every route; registered sources keep their identity; the raw archive never keeps an individual's id after classification; no client-facing view lists or ranks individuals.
- (2) As (1), plus a second reference scoped per source (per channel on YouTube) for analytics, so one person cannot be linked across sources even internally.
- (3) Keep the raw archive "exactly as returned" with clear ids and hash only in normalize-item (reverses README decision 8 for TikTok).

### D2-Q018 · Budget priorities and modes (README decision 2)

What still runs when a budget reaches 80% and 95% (the X post-read cap, the YouTube daily quota, each vendor's monthly budget).

- **Recommended (1):** the README's five priorities, completed with explicit rows (every client request and the first sight of a new item at priority 1; the 30-day YouTube text refresh at 3; unrequested X history at 5), set only by the SDK, never by callers; priority gating on every budget, green ones included; interval stretching only on amber budgets.
- (2) The README's table exactly as written (new videos from smaller channels and clients' X history requests wait under pressure).
- (3) Per-budget priority profiles, or callers send priorities checked against a maximum (flexible, but behaviour becomes configuration).
- Variant of any option: gate and stretch on amber budgets only, as CONVENTIONS says (nothing on X or YouTube is held back before 100%).

### D2-Q021 · A platform 401 or 403, fallback, and the government exclusion (README decision 5)

When a platform refuses our access, do we stop or switch to a vendor, and how are government clients protected?

- **Recommended (1):** a refusal is classified first (a quota 403 waits for the quota reset; a 403 about one video or post ends only that item); a real authorisation refusal revokes that client credential or blocks that one source, with no automatic switch to vendor data and an approval card to ops (and the client); vendor key or credit problems may fall back, decided only by the canary; government-watched green sources never move to amber, enforced by registry-writer; no vendor stand-in while a green route (for example Meta's PPCA) awaits approval. This also rewords the 401/403 rule in `CLAUDE.md`, which is your file (the text is proposed in the decision).
- (2) CONVENTIONS as written: fetchers mark the token or route `degraded`, and the canary may then fall back to a vendor automatically (government sources aside); no approval card.
- (3) Two levels as in (1), but with automatic fallback wherever a flag is on, except for government-watched sources (most coverage; a client's revoked consent can turn into vendor data about that client's own property).

### D2-Q027 · Where the platform runs: the cluster and object storage

- **Recommended (1):** k3s (small, standard Kubernetes) on Hetzner; Hetzner Object Storage as the primary store; Backblaze B2 as the off-site copy of the raw archive. You open the Hetzner and Backblaze accounts when I1 starts.
- (2) Nomad on Hetzner instead of k3s, only if your team already runs Nomad.
- (3) Hetzner storage only, no off-site copy (cheaper; a provider-level loss would lose every replay).
- (4) Another provider you name (it goes through the vendor screen first).

### D2-Q029 · ClickHouse topology and the three environments

- **Recommended (1):** one ClickHouse node with daily backups in staging; a replicated pair before production; tables written as replicated from the first migration; three environments: local (fake platform), staging (real APIs, each budget capped at a small figure you set per vendor before G2), production.
- (2) Replicated from staging (about twice the ClickHouse cost from G2).
- (3) One node in production too, with backups (cheapest; an outage stops ingestion until a restore).

### D2-Q038 · Should web pages that are neither news nor social posts become mentions that clients see?

Web search finds blogs, forums and company pages that name a brand. Today the web PRDs only use them to find social sources and news articles, while CONVENTIONS reads as if every result were a mention.

- **Recommended (1):** a web page becomes a mention (title, snippet, link, kept as an excerpt) only when no platform or news reader covers it, so nothing appears twice.
- (2) Routing only: web pages are never shown as mentions (least work; a brand named only on a blog or forum is never seen).
- (3) Every search result becomes a mention as well as being routed (widest; articles and posts found by search show twice unless a de-duplication rule is added).

### D2-Q048 · What clients can slice and be alerted on in v1

A slice left out of the aggregate tables can never be added for past months, because the base rows are purged on each platform's clock.

- **Recommended (1):** every promised slice in the aggregates now (language and dialect, route, posts against comments, YouTube per channel owner, topics, entities and brands, stories); `mixed` sentiment counted in every share; no per-post LinkedIn history; the five alert types already built in v1, with engagement, topic, entity and story alerts later.
- (2) The tables as drafted, the extra promises withdrawn (least work; language, entity and story views stop at each platform's purge).
- (3) Everything now: (1) plus per-post LinkedIn history kept ten years and the four extra alert types (needs counsel on LinkedIn's limits first; the alert service waits for the analysis services).

### D2-Q051 · Vendors: which vendor serves which role, how they are screened, how they are named

- **Recommended (1):** one setting per vendor role, the cheaper or cleared vendor first (Facebook groups and comments on ScrapeCreators, Facebook search on SociaVault until ScrapeCreators has it, TikTok on a cleared vendor), with a fallback order switched only by the canary; one lower-case spelling for vendor names everywhere; you (or counsel) verify each weakly cleared vendor's owner and country before its first probe and at each renewal.
- (2) One vendor per platform where possible (SociaVault for Facebook and Instagram, EnsembleData alone for TikTok): fewer contracts, higher prices for Facebook groups and comments, no TikTok fallback.
- (3) Flags as plain on/off switches; vendors and fallback order kept only in the vendor credentials (ops switch vendors freely; an audit must read two places).

### D2-Q052 · Amber data and clients: consent, the 31st hashtag, and clients' own properties

Amber data is bought from vendors who scrape; today only government clients are excluded.

- **Recommended (1):** a client receives amber data only if its contract accepts vendor data (`accepts_amber`, off by default, always off for government clients); a client's own accounts, pages and channels are never read through a vendor; a client's 31st Instagram hashtag in a week goes to the vendor only if that client accepts amber, otherwise it waits.
- (2) As (1), but a client that accepts amber may also have its own properties read through the vendor (outage gap fill, daily reconciliation, 90 days of Telegram history before our bot joined).
- (3) Government flag only, as CONVENTIONS says today (every other client receives amber data while a flag is on, even one whose contract excludes it).

### D2-Q053 · Who may see an item: a shared pool or per-client data

- **Recommended (1):** visibility follows the grant the data was fetched under: data from a client's own grant only to that client; Meta public-content data only to the clients watching that source; our own licences and the open web (X, YouTube, news, web, open Telegram channels) to every client whose keywords match; amber data to that pool, limited to clients who accept amber. X joins the pool only once you move to X's Enterprise plan; until then X data reaches only the clients declared to X, and you move to Enterprise at the first government client or the second paying client on X (its price must be quoted by X).
- (2) Per client for everything (simplest; a client sees no source until it is on its own list, so discovery and share of voice shrink).
- (3) Pool everything except clients' own-grant data, Meta included (widest; against Meta's terms, and risks the only green route to Facebook Pages at Meta's yearly review).
- For the X point alone: pool X on the self-serve plan from the start (more coverage sooner; X may object at use-case review).

### D2-Q054 · Retention classes for TikTok Display, the Telegram bot and web search

These three routes have no retention class in CONVENTIONS. Counsel confirms before production.

- **Recommended (1):** add `tiktok_display` (kept while the client's authorisation lasts; deleted on revocation, offboarding or TikTok's request) and `telegram_bot` (kept while the channel owner and the client relationship last; deleted on request or offboarding); web results stay `news_excerpt`, worded for records with no full text.
- (2) As (1), plus a separate class for web results.
- (3) Map all three to existing classes (Telegram bot data would keep a 24-month vendor-contract clock with no vendor behind it).

### D2-Q055 · LinkedIn data: which class holds what

LinkedIn's PRDs say its restricted uses apply to every LinkedIn item, whichever route fetched it.

- **Recommended (1):** LinkedIn's terms apply on every route: member-written content (comments, member posts, reposts of member posts) is `linkedin_48h`; organization posts get a new class `linkedin_org` (six weeks, six months if counsel confirms the authenticated reading) on green and amber alike, so amber organization history beyond six weeks survives only as aggregates; member profile data is never stored.
- (2) As (1), but amber organization posts kept 24 months under the vendor contract (two years of history; the same exposure as keeping member comments past 48 hours, unless counsel says LinkedIn's terms do not bind vendor-bought data).
- (3) `linkedin_48h` on every LinkedIn record, with per-field purges (one class; per-field deletion work no other platform needs).
- (4) By route only, as CONVENTIONS says: 24 months for all amber data, 48 hours for all green (vendor-bought member comments kept 24 months; green organization posts deleted at 48 hours).

### D2-Q056 · How long derived data lives, and what YouTube's 30-day rule covers

- **Recommended (1):** item-level scores, hits and metrics follow their item's class (YouTube 36 months from creation; LinkedIn member items 48 hours); rollups keep ten years, except per-channel YouTube rollups (36 months); the 30-day refresh-or-delete rule covers all stored YouTube text (comments, titles, descriptions, channel profiles); text refresh is part of the service, not sold separately.
- (2) Ten years for every derived row and rollup, as CONVENTIONS says (longest history; audit risk under YouTube's policy).
- (3) Every YouTube-derived rollup also capped at 36 months (most conservative; YouTube leaves the ten-year trend lines).

### D2-Q058 · Engagement-count refreshes on X, LinkedIn, Telegram and Facebook groups

- **Recommended (1):** counts recorded at first sight only on these routes in v1 (no extra spend); revisit after the pilot with measured costs.
- (2) A +24 h views refresh for tier-1 Telegram posts only.
- (3) +24 h and +7 d refreshes everywhere, as CONVENTIONS says (on X alone about USD 6,000 a month more at list price, from 0.6 million posts a month × 2 reads × USD 0.005).

### D2-Q059 · Coverage bought by default: history on add and extra comment fetches

Each default spends quota or vendor money before any client asks.

- **Recommended (1):** green routes get history and one comment fetch per backfilled post by default (paid in quota, not money); nothing extra on amber; X keyword rules get 7 days of history, older X history and old replies only when a client asks; news history from sitemaps only; LinkedIn keyword finds get comments only on request.
- (2) As (1), plus comment fetches on amber routes for backfilled posts and keyword finds (vendor money per 1,000 posts, figures in the decision).
- (3) More history on X and news: automatic X keyword history on every new rule, X replies to day 30, a Common Crawl news lister (90 days for every rule could reach about 60% of one month's X read cap).

### D2-Q068 · Using platform content for models and media

- **Recommended (1):** evaluation sets may use de-identified platform content, but only from retention classes a frozen set can respect (no LinkedIn items; YouTube comment text only to day 30; X only with deletions applied within 24 hours), and the sets are purged like any store; training only on licensed, public, synthetic or annotator-written data until counsel confirms each source (platform, client-owned, news, Telegram and Disqus content all wait); Content Signals honoured; images stored only where the terms allow, YouTube thumbnails only; no audio or video downloaded anywhere until counsel confirms per platform, so media analysis covers images and thumbnails only in v1.
- Variant: the no-download rule for YouTube only, as README decision 7 wrote it (speech-to-text and video OCR run in v1 where the team reads the terms as allowing it).
- (2) Train and evaluate on all collected content, de-identified (best models soonest; exposure under Meta's and TikTok's terms that counsel may force us to unwind).
- (3) No platform content in any model set, evaluation included (no exposure; evaluation unlike real data; A0's plan changes).

### D2-Q069 · Legal policies for deletions and audits

- **Recommended (1):** strict defaults that can be built now, each confirmed by counsel before G4: an author's request deletes what they asked for, and stops monitoring their public account only if they ask (then for good); identity checked through the account's public contact; every deletion engineered to X's 24-hour deadline on every route, from a verified request; backups may live longer only if every restore re-applies the deletion log first; audit rows hold no content or clear identities and are kept for the contract's life until counsel sets a period; client keyword terms screened against a sensitive-events list kept by your compliance owner, and a flagged term is not run on X.
- (2) Leave every point to counsel before these services are built (C13, C14, X7 and I1's backups wait).
- (3) Per-route deadlines read by the team now, and backups excluded from deletion (a restore could resurface deleted data).

## Technical decisions (the recommendation stands unless you object)

| Id      | Decision                                                                                                              | Recommendation                                                                                                                                                                                 |
| ------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D2-Q002 | Message metadata and schema versioning                                                                                | A `schema` string on every message, with one metadata block, and the build plan's versioning rule                                                                                              |
| D2-Q004 | Partition keys for topics and job queues                                                                              | One declared key per topic and per queue, `source_id` by default, the exceptions named                                                                                                         |
| D2-Q005 | The `raw.items` message: shape, envelope fields, and why a record was read                                            | Nested `{envelope, payload}` for every producer, one envelope type built by the SDK with conditional fields, and one `job_kind`                                                                |
| D2-Q006 | Identifiers: key authority, `item_id`, `job_id`, client and keyword ids                                               | One key helper in the contracts package, run by producers and checked by normalize-item; uuid v5 item ids; ULID job ids; UUID client and keyword ids                                           |
| D2-Q007 | Item keys per platform                                                                                                | The majority form per platform, the kind segment equal to the item kind of D2-Q008                                                                                                             |
| D2-Q008 | Item kinds and normalize-item's mappers                                                                               | Five content kinds, four archive-only record kinds, and a mapper registry                                                                                                                      |
| D2-Q009 | Comment records: fields, content hash, edits                                                                          | One comment field set, one hash helper, versions under one key where the platform gives ids, and a new comment where it gives none                                                             |
| D2-Q011 | The job envelope and the kind list                                                                                    | One envelope, one field `kind`, a closed kind list with declared fields                                                                                                                        |
| D2-Q012 | Who emits which job: the producer table, ops and client requests                                                      | A producer table in F2, checked by the SDK; the single-emitter rules kept with named exceptions; ops and client requests through the admin API                                                 |
| D2-Q013 | Registry ownership: one writer for identity and policy, named owners for operational columns, requests as decisions   | Two ownership classes and one request path                                                                                                                                                     |
| D2-Q014 | `source.events`: one writer and a closed list of event types                                                          | registry-writer is the only writer, from its outbox, with one closed list                                                                                                                      |
| D2-Q015 | Rotation state when several services rotate one row                                                                   | Each service schedules itself from its own row in `cursors`                                                                                                                                    |
| D2-Q016 | Source health and credential state                                                                                    | Two levels, each with one writer                                                                                                                                                               |
| D2-Q017 | How a finished job reports back: `jobs.completed` (README decision 1)                                                 | README decision 1, with one schema and the wrapper as the only writer                                                                                                                          |
| D2-Q019 | Early stop of a comment series (README decision 3)                                                                    | README decision 3 on every profile, applied only by comment-decay-scheduler, with the +24 h step kept and a LinkedIn denominator                                                               |
| D2-Q020 | Backfill: one writer of `backfill_status`, a complete route table, one job and one report (README decision 4)         | README decision 4, completed                                                                                                                                                                   |
| D2-Q022 | News: the `news.dedup` topic, the per-host gate and the 7-day full-text cache (README decision 6)                     | Keep all three, with these precisions                                                                                                                                                          |
| D2-Q023 | Analysis: lanes, the `items.analysis` key, the ClickHouse `analysis` table and `model_versions` (README decision 7)   | The README's key and versioning, with lanes per service                                                                                                                                        |
| D2-Q024 | TikTok: README decision 8 confirmed part by part                                                                      | Confirm each part, as settled elsewhere                                                                                                                                                        |
| D2-Q025 | New tables and stores named in one PRD (README decision 9)                                                            | Decision 9 accepted, stores another service reads join CONVENTIONS, private stores follow one rule (CF-059 option 2)                                                                           |
| D2-Q026 | Kafka client libraries for the two SDKs                                                                               | Both clients on librdkafka, as proposed, with the partitioner set explicitly                                                                                                                   |
| D2-Q028 | lang-dialect-id in Python, its callers, and Arabizi                                                                   | Python service, recorded as the third exception, with the fold also in TypeScript                                                                                                              |
| D2-Q030 | Ratify the tooling, local stack and dependency policy F1 built                                                        | Ratify what F1 built, and fix F2's pipeline as Zod 4 to JSON Schema to Pydantic                                                                                                                |
| D2-Q031 | Keyword hits: what `item.hits` and `discovery.hits` carry, and who writes them                                        | Every keyword hit on `item.hits`; `discovery.hits` carries candidates only                                                                                                                     |
| D2-Q032 | Resolvers: who publishes profiles, one `resolve` job, and refreshes of registered sources                             | Resolvers publish their own profiles; poster-resolver dispatches, deduplicates and caches                                                                                                      |
| D2-Q033 | The `poster.profiles` message and the Iraqi-signal vocabulary                                                         | One flat schema built from the ten rules, closed vocabularies, one shared reference table                                                                                                      |
| D2-Q034 | Engagement counts: one writer per observation, the `item.metrics` message and metrics jobs                            | One observation per read, from one writer; one flat message; steps counted from the post's creation time                                                                                       |
| D2-Q035 | Deletions: one message, one remover, a guard against resurrection, and recompute                                      | One schema, one remover, one guard                                                                                                                                                             |
| D2-Q036 | News URLs and articles: keys, the `article.urls` message and the URL ledger                                           | Bare hex everywhere, one URL key on `article.urls`, one ledger hash                                                                                                                            |
| D2-Q037 | The web-search path: `search.results`, raw archiving, the YouTube bridge and routing                                  | One results schema, every response archived, one router for YouTube links                                                                                                                      |
| D2-Q039 | The raw archive: replay, object-storage prefixes and lookups by id                                                    | One replay path through raw-archiver's reader, no normalized archive, one owner per prefix                                                                                                     |
| D2-Q040 | News tables: who writes `news_sites` and `crawl_policies`, and where the host gate keeps its state                    | One writer per table, crawl refusals sent as registry decisions, the gate in its own table                                                                                                     |
| D2-Q041 | The `cursors` table: its key, its columns, and who may write a row                                                    | A widened key, typed due columns, a private `state`, own rows only                                                                                                                             |
| D2-Q042 | Budgets: one writer for the counters, a home for caps, the two ledgers and the tag list                               | quota-governor the only writer of counters, configuration in its own table, ledgers as tables, one tag list                                                                                    |
| D2-Q043 | The `clients` table, and where a client's lists live                                                                  | A typed `clients` core with settings and tokens beside it, priority on `client_sources`, seed and watch lists by candidate key                                                                 |
| D2-Q044 | The `keywords` table, and the keyword-rule sources the searchers rotate                                               | Per-client keywords; shared keyword-rule rows per platform, route and query, kept by registry-writer from the portal's saves                                                                   |
| D2-Q045 | The other shared tables: run status, retention classes, the review queue, decisions, resolver caches and audit trails | One pattern: typed shared columns, `kind` and `payload` where uses vary, private state with its owner                                                                                          |
| D2-Q046 | Comment state for change detection, and the keys of `comment_series`                                                  | One shared `comment_state` table behind one SDK helper; per-post state in the fetcher's `cursors` rows; `comment_series` keyed by post and lane                                                |
| D2-Q047 | ClickHouse: the column names readers use, what a purge empties, and the tables beyond CONVENTIONS                     | store-writer's columns are the contract, one purge list per class, `hits` for item hits only, aggregates and views in the contract                                                             |
| D2-Q049 | What `tier` holds, and what "push" means                                                                              | Three columns: `tier` (1, 2, 3, always kept), `lifecycle` (`active`, `dormant`, `retired`) and `push_covered` (boolean), with one cadence table per source type in CONVENTIONS                 |
| D2-Q050 | Where the vendor flags live, what happens while one is off, and the X plan gate                                       | Flags in a table read per job, nothing emitted while off, fallback a health state, a plan setting plus a per-client declaration                                                                |
| D2-Q057 | What a job does with a quota answer, when it reaches the DLQ, and who stretches amber rotation                        | Quota answers are never failures: one rule in the SDK wrapper and scheduling kit                                                                                                               |
| D2-Q060 | When comment and metrics steps fall due, and how reply threads are fetched                                            | Comments from first sight, metrics from creation, one `replies` job per post                                                                                                                   |
| D2-Q061 | The Disqus comment series                                                                                             | The short series, as CONVENTIONS, the scheduler and the fetcher say; news-site-resolver's sentence corrected                                                                                   |
| D2-Q062 | When a missing post or comment becomes a deletion                                                                     | One rule in the SDK: absence becomes a deletion only after a confirmed second miss, or on a platform deletion signal; and routes whose reads are not complete listings never delete on absence |
| D2-Q063 | Which X keyword rules go on the filtered stream                                                                       | Streamed rules chosen by priority within a fixed share                                                                                                                                         |
| D2-Q064 | Filling X stream gaps, X history jobs, and the key of an X reply                                                      | x-recent-search fills recent gaps, history only on a client's request, one key per tweet                                                                                                       |
| D2-Q065 | YouTube: details jobs, partial records, the uploads playlist id, channels without push, and the text refresh          | One video per job, partial versions, a registry column, tier cadence when push fails, refresh as a version                                                                                     |
| D2-Q066 | How a client's own properties, and the sources it asks for, enter the registry                                        | Owned properties as direct `add` decisions, requested sources through the manual path, nothing through `discovery.hits`                                                                        |
| D2-Q067 | One interface for the n8n flows, and who specifies and builds them                                                    | One documented n8n interface, the flows specified by D3, the build assigned by the orchestrator                                                                                                |
| D2-Q070 | One editorial pass: the documents that disagree with themselves                                                       | One editorial pass, each point decided here so F2 has one spelling                                                                                                                             |

## Answers

The user answered on 7 Oct 2026, through the orchestrator. Their words, verbatim:

> Approve all. Except Q010 as the client should be able to see a list of individuals and be able to filter or rank them in order then use them later to further understand the segments. Q021 automatic switching should be considered. Expand Q048 more. Q054, Q055, and Q056 data retention should be up to 10 years. I dont understand Q059 question nor recommendation. Q068 we will download some of the content and if it does not break any rules then we will use it for training as well.

The orchestrator then put the open points back to the user, who chose, with these exact wordings:

- Q010: "Public accounts only". Clients can list, filter, rank and save public accounts: pages, channels, media, creators and public figures (verified, or above a follower count the user sets). Ordinary people stay anonymous and show up only in segments, as counts by language, dialect, region, sentiment and topic. The platforms' terms are respected.
- Q054 to Q056: "10 years where allowed". Every item is kept 10 years on X, Meta, Telegram, news, web and vendor routes, with deletion requests honoured. YouTube, LinkedIn and TikTok items are kept as long as their terms allow, and their counts and trends are kept 10 years.
- Q048: "Add 4 alert types in v1". Engagement-spike, topic-spike, entity or logo, and story alerts are also built in v1. Alerts then launch after the analysis services. Per-post LinkedIn history is kept only if counsel says LinkedIn allows it.
- Q059: "Maximum history". This is option 3.

On 9 Oct 2026 the orchestrator put two of its own readings and the D2 review's open points back to the user. The two readings were relayed to the user on 7 Oct 2026 and recorded in ADR-0021 and ADR-0068, but not written in this section:

- the limits on Q021's automatic switching: a 401 or 403 classified by reason; a blocked source falling back to its vendor where that route's flag is on; never for a government-watched green source or a client-owned property; an n8n notice to ops for every automatic fallback;
- for Q068, a register of permitted uses for training and downloads, whose entries the user or the user's compliance owner sets. ADR-0068 recorded every entry as "not allowed" until set.

The review's points are in `docs/reviews/D2.md`, "For the user", points 2 to 6. The user chose, with these exact wordings:

- Q021: "Make client page to be read through the scrapper as well". The limits are confirmed except the client-owned exclusion. A client's own pages and accounts (client-owned properties) also fall back to the vendor (amber) route automatically when green access is lost, under the same conditions as any other source. A government-watched green source still never switches, and ops still get an n8n notice for every automatic fallback (ADR-0021).
- Q068: "Allowed by default". In the register of permitted uses, a use (training on a source's content; downloading its images, audio or video) is allowed unless the register says it is not, and `ai-train = no` still always excludes a host. The orchestrator reads the 7 Oct words "if it does not break any rules" to mean that the register is seeded with "not allowed" rows for every use a platform's terms or a vendor contract already forbids. YouTube's terms forbid downloading video, so YouTube stays thumbnails only (ADR-0068).
- Review points 5 and 6: "Keep both until counsel". Rollups of a single YouTube channel are kept 36 months (ADR-0056), and Instagram creator accounts are not listed (ADR-0010), both until counsel answers (`DEFERRED.md` section 1).
- Review points 2, 3 and 4: "Accept all three":
  - X `withheld` status comes from the daily compliance run, and ADR-0035 says it departs from `D2-PROPOSALS.md` L1120 and L2397;
  - the X reply hand-back keeps `window_start` on `replies` jobs, and ADR-0064 marks it as phase 2's technical choice for X5 to confirm;
  - the D2 fix session applies the review's replacement texts for `CLAUDE.md`, `.claude/rules/services.md` L12 and the review, plan and reviewer skills.

Asked again on 9 Oct 2026 about the consequences of these answers, the user chose, with these exact wordings:

- Client-owned properties in fallback: "Same as any source". A client-owned property falls back when any client watching it accepts amber data and no government client watches it, even if its owner does not accept amber; the owner then receives nothing from the vendor. While it is in fallback, its vendor-read posts are amber `pool` data: they reach every accepting client whose rules match, not only the owner (ADR-0021, ADR-0052, ADR-0053).
- A client's own TikTok revocation: "Read it via vendor". After a client revokes its TikTok Display grant and the `authorization_revoked` deletion TikTok's terms require, the account's public videos may be read again through the vendor route, where an accepting client watches it and no government client does. Counsel is told when it confirms the `tiktok_display` reading (ADR-0021, ADR-0035, ADR-0054; `DEFERRED.md` section 1).
- Training on Facebook and Instagram content: "Start as not allowed". The register of permitted uses is seeded "not allowed" for training on Facebook and Instagram content, client-owned Pages and accounts included; the user or the compliance owner may change it (ADR-0068).
- Two technical points: "Accept both". The primary poller of a news site is the poller of its first surface in the order feed, sitemap, homepage: news-feed-poller if the site has a feed, else news-sitemap-poller, else news-homepage-differ; the primary poller of a web keyword rule is web-search-mojeek (ADR-0049). A client's LinkedIn page falls back through li-company-posts-poller only if LI0 finds the activity URN on the green LinkedIn API; otherwise it stays `blocked` and the client gets the missing-grant card (ADR-0007, ADR-0021).

After the recheck of the D2 fix (`docs/reviews/D2.md`, "Recheck 9 Oct 2026", "For the user", points 1 to 3), the orchestrator put its three points to the user on 9 Oct 2026. The user chose, with these exact wordings:

- A client's own TikTok account after a revocation (the recheck's point 1, finding 25): "Only new videos". After a client revokes its TikTok Display grant and the `authorization_revoked` deletion, the vendor route reads only the videos the account posts after the revocation. Deleted videos stay deleted: the tombstones and store-writer's guard are unchanged. The source is not retired while a client that accepts amber watches it, and no government client watches it. Counsel can widen this later (the `tiktok_display` row of `DEFERRED.md` section 1). This narrows "Read it via vendor" above: the account's earlier videos are not read again (ADR-0021, ADR-0035).
- Client Facebook Pages and Instagram accounts (the recheck's point 2, finding 32): "Add a vendor reader". The user wants a new amber service that reads clients' own Facebook Pages and Instagram accounts through a vendor when their grant is lost. Building it is outside D2. It needs its own PRD, a vendor screen (owner and country, ADR-0051), its flag and a build-plan session, which the orchestrator plans after D2. D2 only records the request: in ADR-0021, where the alternates are listed; in `DEFERRED.md` section 3, as a row owned by the orchestrator, with the user (a new PRD session after D2); in the handoff; and here. Until that service exists, client Facebook Pages and Instagram accounts stay `blocked`, and the client gets the missing-grant card. Client YouTube channels were not part of the answer and stay `blocked` in v1.
- The kit files (the recheck's point 3, findings 30 and 31): "Approve both". The user approves the six further kit lines the D2 fix applied: `.claude/rules/services.md` L14, `.claude/skills/plan-session/SKILL.md` L26, `.claude/rules/python.md` L9, `.claude/rules/contracts.md` L11, `.claude/skills/contract-change/SKILL.md` L13 and `.claude/skills/decide-session/SKILL.md` L23 (ADR-0001, ADR-0002, ADR-0028, ADR-0067). Finding 30's replacement text is applied to `.claude/skills/review-session/SKILL.md` L17 and `.claude/agents/prd-reviewer.md` L13, so reviews read the same ADRs and `DEFERRED.md` rows as plans and briefs (ADR-0001).

D2 recorded them as follows, the 9 Oct follow-ups included, one ADR per decision (ADR-nnnn records D2-Qnnn):

| Decision                                                       | Recorded as                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every decision not named below, the 51 technical ones included | the recommended option, as written in `D2-PROPOSALS.md`; for D2-Q035, the option's rule that X `withheld` status comes from the daily compliance run (L1108), not its contradicting answer (L1120, L2397), and for D2-Q064, the X replies hand-back by `window_start`, phase 2's technical choice for X5 to confirm, both accepted by the user on 9 Oct 2026 (ADR-0035, ADR-0064); and for D2-Q052, the recommended option except its (e), which no longer keeps a client's own property from the vendor once its green access is lost: the user's Q021 answers of 9 Oct 2026 let it fall back like any other source (ADR-0052, ADR-0021) |
| D2-Q010                                                        | option 1 for ordinary people, who appear only in anonymous segments; public accounts may be listed, filtered, ranked and saved, where the platform's terms allow (ADR-0010)                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| D2-Q021                                                        | option 3 with limits: a 401 or 403 classified by reason, and a blocked source, a client-owned property included, falling back to its vendor automatically where that route's flag is on, never for a government-watched green source, with an n8n notice to ops (ADR-0021; the limits confirmed with that change on 9 Oct 2026); after a client's TikTok revocation, the vendor reads only the videos the account posts after it (9 Oct 2026: "Only new videos"; ADR-0035)                                                                                                                                                                |
| D2-Q048                                                        | option 3: every slice of option 1 and all nine alert types in v1, with per-post LinkedIn history only once counsel confirms (ADR-0048)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| D2-Q054, D2-Q055, D2-Q056                                      | ten years wherever the rules allow, otherwise the platform's, vendor's or copyright limit; aggregates ten years, except rollups of one YouTube channel at 36 months (ADR-0054, ADR-0055, ADR-0056)                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| D2-Q059                                                        | option 3: automatic 90-day X keyword history, X replies to day 30 and a Common Crawl URL lister for news, under the budget priorities (ADR-0059)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| D2-Q068                                                        | evaluation and Content Signals as recommended; training and media downloads follow a register of permitted uses, allowed unless an entry says "not allowed" (9 Oct 2026: "Allowed by default"), and seeded "not allowed" for every use a platform's terms or a vendor contract already forbids, so YouTube stays thumbnails only, and, as the user's own choice, for training on Facebook and Instagram content, client-owned Pages and accounts included, until the user or the compliance owner changes it (9 Oct 2026: "Start as not allowed") (ADR-0068)                                                                              |

What still waits on the user or counsel is in `docs/decisions/DEFERRED.md`, sections 1 and 2.
