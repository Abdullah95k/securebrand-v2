# Contract conflicts: assumptions one PRD makes about another

D1 · 7 Oct 2026 · Status: **open, none resolved.** Companion to `docs/contracts/CONFLICTS.md` (same entry format and reading rules). Every cross-service assumption the extraction recorded (about 770) was checked against the PRD of the service it is about; these entries are the ones that PRD contradicts, or does not support where a contract element depends on it. Overlaps with CF entries are named in each entry.

## Index

| ID | Conflict | Type | Blocks |
|---|---|---|---|
| [AU-001](#au-001) | Completion events: `jobs.completed` or `service_runs`, which report fields, and which status values end a series | names, shape, enum | F2, F4, C11, C10, N8, YT5, YT6, X5, X6, VFB3, VIG2 |
| [AU-002](#au-002) | Backfill marker: `job_kind = backfill` carried onto `items.normalized`, or `metrics_observation = backfill` on `raw.items` | names, shape | F2, C4, C10, C11, FB3, IG3, IG5, VIG1, X5 |
| [AU-003](#au-003) | `news.dedup` and the story fields: normalize-item neither reads the topic nor carries the fields | writers, shape | F2, C4, N7, C6, C15, A5 |
| [AU-004](#au-004) | LinkedIn reaction events as counter increments: `item.metrics` has only absolute observations | shape, rule | F2, C4, LI3, LI1, C6 |
| [AU-005](#au-005) | Early discovery hits: `context.discovery_hit_emitted` against keyword-matcher emitting anyway | shape, writers | C5, C4, C8, X1 |
| [AU-006](#au-006) | Hit field read by analysis-sentiment: `matched_text` or `matched_term` | names | F2, C5, A1 |
| [AU-007](#au-007) | Resolver answers: on `jobs.poster-resolver` to poster-resolver, or straight onto `poster.profiles` by each resolver | writers, shape | F2, C8, C9, FB1, IG1, VTT3, X2, VLI2, VTG2, YT1, N2 |
| [AU-008](#au-008) | `discovery.hits` fields: the "approved poster-resolver schema" other PRDs defer to is not defined, and poster-resolver ignores `candidate_pending` and caption handles | shape, partition | F2, C5, C8, W3, W5, IG2 |
| [AU-009](#au-009) | `poster.profiles` fields the qualifier's rules need, which poster-resolver does not emit; resolver signals the qualifier never reads | shape, enum | F2, C8, C9, VLI2, VTG2, X2 |
| [AU-010](#au-010) | A Parquet archive of normalized items: normalize-item and the four analysis services expect one; raw-archiver archives `raw.items` only | writers, shape | C2, C4, F8, A1, A2, A3, A4 |
| [AU-011](#au-011) | `search.results`: neither archived nor normalized, though yt-web-search-bridge relies on both | writers | C2, C4, YT9 |
| [AU-012](#au-012) | Readers named for `raw.items` and `discovery.hits`: keyword-matcher, lang-dialect-id, store-writer and the qualifier read other inputs | writers, names | F2, C4, IG2, VTG1 |
| [AU-013](#au-013) | `item_id` on `deletions`: optional in the propagator's minimum shape, required by alert-evaluator | shape | F2, C13, A5 |
| [AU-014](#au-014) | Analysis outputs as aggregate dimensions: topic ids from several taxonomies, and the `mixed` label in the negative share | names, enum, shape | C15, A1, A2, A5, F8 |
| [AU-015](#au-015) | How a backfilled record is marked: `job_kind = backfill` is expected, `metrics_observation = backfill` (or nothing) is written | names; shape; rule | F2, F4, C4, C10, C11, FB3, VFB1, VFB2, IG3, X5. |
| [AU-016](#au-016) | Push-tier changes asked of registry-writer by the receivers have no input path, and the `push_lease_lapsed` event yt-uploads-reconciler waits for is never emitted | writers; shape; enum | F2, C7, FB7, YT2, YT3. |
| [AU-017](#au-017) | Backfill completion: backfill-orchestrator waits for a `jobs.completed` report with `oldest_item_at`, `capped` and `capped_reason`; fb-backfill sends none, the others send other fields, and several services write `backfill_status` themselves (Telegram's receivers `capped` where the orchestrator sets `done`) | shape; writers; enum | F2, F4, C10, FB3, VFB2, IG3, VTT1, VTT2, VTT4, X5, TG1, TG2, VTG3, ... |
| [AU-018](#au-018) | Subscribing a client-owned Instagram account: registry-writer leaves it to the receiver on `added`; ig-webhook-receiver reads no `source.events` and subscribes "on connecting", with no trigger defined | writers; rule | C7, IG4. |
| [AU-019](#au-019) | Partition key of search finds on `raw.items`: normalize-item expects the producer to key them on the poster, while CONVENTIONS and the producers key them on the rule's `source_id` | partition; key | F2, F4, C4, IG2, VTT1, VTT2, YT8, W1, W2, W4. |
| [AU-020](#au-020) | comment_series columns that fetchers keep their per-post cursor in (`newest_comment_at`, thread id) | shape, writers | F3, F2, C11, LI2, VLI4, N8 |
| [AU-021](#au-021) | Stores and columns other PRDs expect registry-writer to write: `news_sites`, crawl-policy health, uploads playlist id, hashtag binding, ownership flip, client flags | writers, single-PRD | F3, C7, N1, N2, N3, YT1, IG2, VLI3, C1 |
| [AU-022](#au-022) | Tombstones against the resurrection guard: deletion-propagator's `is_deleted` rows and store-writer's `deletion_requests` check and version formula | writers, key, rule | F8, C6, C13, C14, C2 |
| [AU-023](#au-023) | ClickHouse `analysis` key: (`item_id`, `model`) with the newer version replacing the older, against `item_id:task:model_version` with re-runs side by side | key, shape | F8, C6, A1, A2, A3, A4, C15, A5 |
| [AU-024](#au-024) | `retention_audit`: written by retention-purger and by yt-text-purger, with different columns | writers, shape | F3, C14, YT7 |
| [AU-025](#au-025) | `media/<sha256>`: stored through raw-archiver's media endpoint with `.refs`, or written directly by analysis-media | writers, rule | C2, A4, C13, C14 |
| [AU-026](#au-026) | Telegram onboarding: onboarding records, one-time codes and a pre-allocated `source_id` that no table, registry path or admin-page document defines | single-PRD; writers; shape | F3, C7, C8, TG1, TG2. |
| [AU-027](#au-027) | The YouTube uploads playlist id: no `sources` column, and each side says the other stores it | single-PRD; writers | F3, C7, C9, YT1, YT3. |
| [AU-028](#au-028) | Disqus site fields: news-comments-fetcher needs an identifier template that news-site-resolver parses but does not emit, and marks "the site's comments degraded" with no column to hold it | single-PRD; writers | F3, C7, N2, N6, N8. |
| [AU-029](#au-029) | Raw responses outside `raw.items`: web-commoncrawl-scanner writes the raw path itself, and yt-web-search-bridge archives nothing although its PRD says raw-archiver does | writers | C2, W5, YT9. |
| [AU-030](#au-030) | Series anchor: the post's first-seen time or its platform creation time, and what a backfilled post gets | rule, job kind | C11, C10, FB3, FB4, IG6, YT4, VTT6 |
| [AU-031](#au-031) | Metrics jobs: `metrics` kind with `+24h` steps, or `refresh_24h` / `refresh_7d` kinds and `24h` / `7d` / `client` labels | job kind, enum | F2, C11, FB4, YT4 |
| [AU-032](#au-032) | Telegram views refresh: tg-channel-posts-poller expects a +24 h `metrics` job that the scheduler never emits | job kind, rule | C11, VTG3 |
| [AU-033](#au-033) | Telegram own channels: a daily `health` job, or no jobs at all | job kind | F2, C11, TG2 |
| [AU-034](#au-034) | Reconciliation jobs and pushed counts: LinkedIn and Instagram push services expect the scheduler to act on counts it never reads | job kind, writers, rule | C11, LI2, LI3, IG4, IG6 |
| [AU-035](#au-035) | Replies jobs: one job per post with `thread_ids`, or one per thread; which profiles get them; per-thread series | job kind, shape, rule | F2, F3, C11, VFB3, VTT5, YT5, YT6, IG6 |
| [AU-036](#au-036) | post_ref in comment, reply and metrics jobs: the scheduler's object against what each fetcher reads | shape, names | F2, C11, N8, VFB3, VTT5, VTT6, YT6, IG6, LI2 |
| [AU-037](#au-037) | Which posts get a series: signals the fetchers expect the scheduler to read, which it never reads | rule, shape | C11, C4, IG2, IG3, VIG2, N6, N8, VLI1, VLI4, VTT5, X6 |
| [AU-038](#au-038) | Client and flag conditions on amber series: amber acceptance, government clients, spend cap, cancellation | rule, flag | C11, F3, VIG2, VFB3 |
| [AU-039](#au-039) | Client refresh: priority and step label | budget, enum | C11, C1, C10, YT4, YT6 |
| [AU-040](#au-040) | X replies of older posts: the scheduler as emitter of `replies` jobs to x-full-archive-search | job kind, writers | C11, X5, X6 |
| [AU-041](#au-041) | Disqus comment series on news sites: +6 h, +24 h, +3 d, or the full decay series | rule | C11, N2, N8 |
| [AU-042](#au-042) | Backfill targets missing from the orchestrator's route table: keyword rules, hashtags, client-authorised TikTok accounts, Instagram mentions | job kind, writers | C10, F2, VFB1, VIG1, VLI1, IG2, IG4, IG5, TT1, X5 |
| [AU-043](#au-043) | Backfill job fields: `cap` and `run_id`, or `window_start`, `window_end` and `reason`; report fields | shape, names | F2, C10, FB3, N4 |
| [AU-044](#au-044) | News sites: which service backfills, and whether rotation waits for the backfill | writers, rule | C10, N2, N3, N4, W5 |
| [AU-045](#au-045) | One-off comment jobs for backfilled LinkedIn posts: emitted by backfill-orchestrator, or the scheduler's `once` fetch | writers, job kind | C10, C11, LI2, LI3, VLI4 |
| [AU-046](#au-046) | Sequencing: whether the orchestrator waits for a source's tier before it emits | rule | C10, C7, IG1 |
| [AU-047](#au-047) | Re-added retired sources: `added` or `updated`, and a run id the orchestrator would deduplicate | rule, key | C7, C10, F2 |
| [AU-048](#au-048) | Author hashing: in normalize-item from the platform id, or at the edge with the result passed through | rule, names | F2, F4, C4, C2, VTT5, VIG2, TG2 |
| [AU-049](#au-049) | Facebook PPCA comment edits: a new version of the old item, or a new item | key, rule | C4, FB5, F2 |
| [AU-050](#au-050) | X replies: `x:comment:<id>` or `x:post:<id>` | key | C4, X1, X4, X6, X7, C13 |
| [AU-051](#au-051) | YouTube partial records: a hold in normalize-item that it does not have, and the video key and kind | rule, key, shape | F2, C4, C11, YT2, YT3, YT4, YT8 |
| [AU-052](#au-052) | `raw.items` producers with no mapper in normalize-item; web results attributed to search-hit-router | writers, rule | F2, C4, VIG1, LI3, VLI2, N8, W1, W2, W3, W4, VTG3 |
| [AU-053](#au-053) | Instagram cross-route duplicates: vendor media ids against Graph ids | key | C4, VIG1, IG2, IG3, IG5 |
| [AU-054](#au-054) | Hashtag-source videos as hits "without text matching" | rule | C5, VTT2 |
| [AU-055](#au-055) | News keyword matching on the 200 to 300 character excerpt, or on the 7-day full text | rule | C5, N6, A1, A2, A3 |
| [AU-056](#au-056) | Resolve job fields and outcomes: `client_ids`, priority, `url_or_handle`, and `skipped_flag_off` against `unresolvable: route_off` | shape, enum, job kind | F2, C8, IG1, VTT3, VLI2 |
| [AU-057](#au-057) | Client-added candidates through `discovery.hits`: `origin = client_onboarding`, `proposed_source_id`, Telegram groups | enum, shape, rule | C7, C8, C9, TG1, TG2, VLI2 |
| [AU-058](#au-058) | Dormant sources that post again: promoted by the qualifier's daily sweep, or by the poller through `source.events` | writers, rule | C9, C7, X3 |
| [AU-059](#au-059) | Work assumed to flow from or to the qualifier: `refresh` jobs to resolvers, unreadable-channel reports | job kind, writers | C9, VLI2, VTG3 |
| [AU-060](#au-060) | Instagram hashtags beyond the 30-tag cap: queued under rule 5, or registered on the amber route | rule, writers | C9, C1, IG2, VIG1 |
| [AU-061](#au-061) | Group candidates from hits inside unwatched Facebook groups: no service emits them | rule, writers | C5, C8, C9, VFB1, VFB2 |
| [AU-062](#au-062) | Keyword-rule and hashtag sources: no registry-writer path creates them, and no seed job is emitted on a keyword change | writers, job kind | C7, F3, W1, W2, W4, VFB1, FB6, IG2 |
| [AU-063](#au-063) | Requests to registry-writer from receivers and pollers: promotion to push, return to reach tier, `next_poll_at`, retirement | writers, rule | C7, C9, YT2, YT3, FB7 |
| [AU-064](#au-064) | `health_change` and the government exclusion: registry-writer's bulk update has no `scope` | rule, shape | C7, C12 |
| [AU-065](#au-065) | Per-source vendor spend caps, per-service sub-counters and page caps: quota-governor keeps none of them (except per-service on `tt_vendor`) | budget, shape | C1, C9, F3, F5, VIG1, VIG2, VTT1, VTT2 |
| [AU-066](#au-066) | Provider-side failures: does quota-governor deny or exhaust a tag on 401/403, out-of-credits or YouTube `quotaExceeded` | rule, budget | C1, C12, F5, VIG1, VIG2, YT8 |
| [AU-067](#au-067) | Priorities and the 80% rules: first sight, metrics order, and X's cascade against the governor's table | budget, rule | C1, F5, YT4, FB4, X1, X5, X6, VLI1, VTG1 |
| [AU-068](#au-068) | Budget tag, bucket, ledger and alert names that the governor does not have | budget, names | C1, F3, F5, IG2, YT7, YT8, VTT1, VTT2 |
| [AU-069](#au-069) | Push routes: receivers expect the canary to flip health on missing heartbeats, which it excludes | rule, writers | C12, TG1, TG2, IG4, YT2 |
| [AU-070](#au-070) | Per-source health flips attributed to the canary, which works per route | rule, shape | C12, C7, N2, N3, IG4, X4, X7, W5 |
| [AU-071](#au-071) | Instagram hashtag fallback to ig-keyword-search is not among the canary's alternates | flag, rule | C12, IG2, VIG1 |
| [AU-072](#au-072) | Replay path: the `raw.replay` topic, or normalize-item reading `raw/` objects directly | writers, rule | C2, C4, C5, F4, A1, A2, A3, A4 |
| [AU-073](#au-073) | Archive lookups by X post id and author id: x-compliance-sync expects an index raw-archiver does not keep | shape, single-PRD | C2, X7, C13 |
| [AU-074](#au-074) | Callers of lang-dialect-id: "normalize-item: the only caller of `/v1/detect`", while poster-resolver, li-org-resolver and analysis-media send it text | writers, rule | C3, C8, VLI2, A4, F4, F6 |
| [AU-075](#au-075) | Arabic in Latin letters (Arabizi): analysis-sentiment routes on a signal lang-dialect-id does not produce | enum, rule | C3, A1 |
| [AU-076](#au-076) | Deletion modes and scopes the propagator does not have: `withhold`, `text_only`, `derived`/`purge_derived`, `fetched_before`, `user_ids` | enum, shape | C13, F2, X7, YT7 |
| [AU-077](#au-077) | Stores outside deletion-propagator's purge registry: annotation text, service-private indexes, analysis media | rule, writers | C13, C14, F4, A1, A2, A3, A4, X6 |
| [AU-078](#au-078) | LinkedIn 48-hour clock: applied by field inside organization posts, or by kind | retention, rule | C14, C13, LI1 |
| [AU-079](#au-079) | Registry decision for an author request that matches a registered source: no producer and no decision type | writers, enum | C14, C7, C13 |
| [AU-080](#au-080) | YouTube derived metrics and aggregates: ten years, or 36 months | retention, document | C14, C15, YT5, F8 |
| [AU-081](#au-081) | Aggregate grain: language, entities, brand appearance, per-post LinkedIn rollups, stories and channel owners are promised but not in the grain | shape, rule | C15, F8, C3, LI2, LI3, VLI4, YT4, YT5, N7, A3, A4 |
| [AU-082](#au-082) | Recompute after deletions: deletion-propagator's bucket jobs and `done`, against aggregator's date-range job and its own `deletions` reconciliation | job kind, shape, writers | C15, C13, C14, F2 |
| [AU-083](#au-083) | Alert features other PRDs promise that no alert-evaluator rule type implements | enum, rule | A5, C15, A2, A3, A4, N7, FB4, VTT6 |
| [AU-084](#au-084) | `metrics_observation = webhook_reconcile` has no producer, and webhook-delivered Facebook posts carry no summaries | enum; rule | F2, FB2, FB4, FB7. |
| [AU-085](#au-085) | A deleted post found by a comment fetcher is handed to a poller that does not detect it (Instagram; LinkedIn after day 7) | writers; rule | IG3, IG6, LI1, LI2, C13. |
| [AU-086](#au-086) | ig-webhook-receiver's reconciliation and targeted jobs: fields and a report the two fetchers do not define | job kind; shape; rule | F2, F4, IG4, IG5, IG6, C11. |
| [AU-087](#au-087) | Hashtag budget waits sent as `fallback_on`: who sets `health = fallback`, who ends it, and how a 31st hashtag reaches the amber route | enum; rule; writers | F2, IG2, VIG1, C7, C12. |
| [AU-088](#au-088) | `jobs.ig-hashtag-search` rotation jobs come from a "shared scheduler" no document defines | job kind; rule; single-PRD | IG2, F5, C10. |
| [AU-089](#au-089) | Which authors keep their identity downstream: "business or creator accounts" against "registered sources" | rule | C4, IG4, IG5. |
| [AU-090](#au-090) | A comment's `content_hash`: text only in the Instagram fetchers, title + text + media URLs in the stored rows they compare against | key; rule | F2, F4, C4, C6, IG6, VIG2. |
| [AU-091](#au-091) | A green push source is one registry row (`route = green`), yet the amber poller's daily reconciliation that both sides count on selects `route = amber` (TikTok, Telegram) | rule; enum | TT1, VTT4, TG1, VTG3, C7, C9. |
| [AU-092](#au-092) | Per-client acceptance of amber data: some amber services filter on it, others only on the government flag | rule; single-PRD | F3, IG2, VIG1, VIG2, VTT1 to VTT6, VFB1 to VFB3, VTG3, TT1, C11. |
| [AU-093](#au-093) | x-filtered-stream's gap jobs: a kind, fields, attribution and a report that x-recent-search and x-full-archive-search do not define | job kind; shape; rule | F2, F4, X1, X4, X5. |
| [AU-094](#au-094) | Who emits `backfill` and `keyword_history` jobs for an X keyword rule | job kind; rule | F2, X1, X5, C10. |
| [AU-095](#au-095) | The X Enterprise gate for government clients: checked in five places under three representations, and not where x-recent-search expects it | flag; rule; single-PRD | F3, X1 to X7, C5, C7. |
| [AU-096](#au-096) | An X reply: `x:comment:<id>` from x-replies-fetcher, `x:post:<id>` from the other X readers, and no agreed hand-back for replies older than 7 days | key; shape; rule | F2, C4, X1, X3, X4, X5, X6. |
| [AU-097](#au-097) | The n8n flows: several PRDs call them by signed webhook, no document defines the flows, their endpoints, payloads or signing (follow-up assumption) | document; single-PRD | F2, A5, C1, C7, C9, C12, VLI2, X7. |
| [AU-098](#au-098) | LinkedIn posts found by keyword search: comment series by default (li-post-search) or only if the budget allows, default no (li-post-comments-fetcher) | rule | C11, VLI1, VLI4. |
| [AU-099](#au-099) | The Telegram daily health check: a `health` job from comment-decay-scheduler, or tg-discussion-receiver's own `reconciliation` job | job kind; writers | F2, C11, TG2. |
| [AU-100](#au-100) | YouTube channels without a working subscription: reach-tier polling (yt-pubsub-receiver) or one daily read (yt-uploads-reconciler); dormant channels weekly or daily | rule; schedule | YT2, YT3, C1. |
| [AU-101](#au-101) | `first_sight` jobs on `jobs.yt-video-details-fetcher`: one id or a list, `series_step = backfill` or `origin_kind`, and a `list` bucket that does not exist | shape; job kind; budget | F2, C1, YT2, YT3, YT4, YT8, YT9. |
| [AU-102](#au-102) | yt-text-purger's `refresh` jobs: no fetcher accepts the kind, and a refresh as the fetchers and normalize-item work would not reset the 30-day clock | job kind; shape; rule | F2, C4, C6, YT4, YT5, YT6, YT7. |
| [AU-103](#au-103) | News backfill: backfill-orchestrator routes it to news-feed-poller, which takes no backfill jobs, and three PRDs send the remainder to web-commoncrawl-scanner, which emits hosts, never article URLs (`found_via = commoncrawl` has no writer) | job kind; enum; rule | C10, N2, N3, N4, N6, W3, W5. |
| [AU-104](#au-104) | Which host errors send `recheck`: news-robots-checker counts 429 and feed or sitemap 404/410; the fetchers back off on 429 and send 404/410 to news-site-resolver as `refresh` | rule; job kind | N1, N2, N3, N4, N5, N6. |
| [AU-105](#au-105) | `not_article` feedback: four news PRDs count on news-site-resolver refining URL patterns from extractor outcomes; no message carries them, and the resolver reads none | rule; job kind | N2, N3, N4, N5, N6, N8. |
| [AU-106](#au-106) | Same-canonical copies: `duplicate_canonical` is not a `news_urls.status` value, and a copy that news-dedup's sweep adds has no key of its own | enum; key | F3, N6, N7. |
| [AU-107](#au-107) | Disqus comment series: news-site-resolver states eight steps to day 30; comment-decay-scheduler, CONVENTIONS and the fetcher run +6 h, +24 h, +3 d | rule | N2, N8, C11. |
| [AU-108](#au-108) | `site_search`: web-search-perplexity expects jobs from yt-web-search-bridge, web-search-mojeek expects none, and the bridge sends none: it queries both engines itself, Mojeek by default | job kind; budget; rule | C1, W1, W2, YT9. |
| [AU-109](#au-109) | Web-search candidates no resolver can take (`youtube:video:<id>`, legacy YouTube names, `instagram:post:<shortcode>`, `facebook:group:<id>`), the bridge's own `resolve` jobs, and a `handled_by` that search-hit-router never reads | key; job kind; rule | C8, W3, FB1, IG1, YT1, YT9. |
| [AU-110](#au-110) | Iraqi verification of web results: three engines count on search-hit-router to judge results Iraqi and report yields back; the router judges nothing Iraqi and reports nothing back | rule | W1, W2, W3, W4. |
| [AU-111](#au-111) | The `resolve` job: poster-resolver's job has no `client_ids` or seed-list flag, which every resolver reads; a vendor flag that is off is handled three ways; li-org-resolver re-keys the candidate; news-site-resolver names other producers | job kind; key; enum | F2, C8, C9, FB1, IG1, VTT3, X2, VLI2, VTG2, YT1, N2. |
| [AU-112](#au-112) | Refreshing registered sources' profiles: TikTok creators have no refresher, li-org-resolver waits for qualifier jobs the qualifier never sends, and Instagram's first due time needs a cursor row nobody writes at registration | job kind; writers | C7, C8, C9, FB1, IG1, VTT3, VTT6, X2, VLI2, VLI3, VTG2, YT1, N2. |
| [AU-113](#au-113) | Budget stretch: quota-governor publishes `stretch_factor` for each amber poller to apply; the pollers say the governor stretches them and read no factor, and tg-channel-posts-poller stretches in a fixed order instead | rule; budget | F5, C1, VFB2, VIG1, VTT4, VLI3, VTG3. |

## 1. Topics and messages

### AU-001

**Completion events: `jobs.completed` or `service_runs`, which report fields, and which status values end a series**

- **Type:** names, shape, enum
- **Where:**
  - a) Channel. Target: `comment-decay-scheduler §5.1 L42` and `§6.1 L135` read `jobs.completed`; `§14 Q1 L202` proposes the topic (alternative "poll `service_runs`"); `README L178` (decision 1). `news-comments-fetcher §3 L21`, `§5.2 L59`, `§6.2 L120` write the result row "to `service_runs` for the scheduler".
  - b) Report fields. Target `comment-decay-scheduler §5.4 L127`: `new_count`, `seen_count`, `pages`, `cost_units`, `reply_candidates`. Others: `fb-group-comments-fetcher §5.1 L53` lists threads as `reply_threads`; `yt-replies-fetcher §5.2 L57` adds `stored_count`, `complete`; `news-comments-fetcher §5.2 L59` adds `thread_id`, `newest_comment_at`; `li-own-comments-fetcher §5.2 L64` adds `newest_comment_at`.
  - c) Status values. The target's only example is `"status": "ok"` (`comment-decay-scheduler §5.4 L127`) and it names no status that ends a series. `yt-comments-fetcher §8 L155` finishes "with status `comments_disabled` so comment-decay-scheduler ends the series"; `§8 L156` "status `video_not_found`, series ends"; `x-replies-fetcher §14 Q4 L202` statuses `quota_denied`, `not_root`, `outside_window`, `not_permitted`, `cursor_rejected` "must be aligned with comment-decay-scheduler"; `ig-comments-fetcher §5.1 L41` completes "as `skipped`"; `yt-replies-fetcher §14 Q3 L192` "Status values ... align with comment-decay-scheduler".
  - d) A completion for a job the scheduler did not emit: `x-full-archive-search §6.2 L128` writes `jobs.completed` "for replies with `post_ref`, `series_step` and the window's `end_time`, which comment-decay-scheduler records as that step"; the target only matches completions to its own `in_flight_job_id` (`comment-decay-scheduler §5.3 L106`) and has no `end_time`; `x-full-archive-search §14 Q2 L190` leaves "where the boundary `end_time` is stored" open.
- **At stake:** news series never advance if the scheduler reads only `jobs.completed`; series on disabled or deleted videos keep emitting steps; fields outside the five-field report are dropped by a typed consumer.
- **Options:** (1) `jobs.completed/v1` as the only channel, with a closed status list (including terminal statuses) and a fixed report plus named optional fields; (2) `service_runs` result rows as the channel (target's Q1 alternative); (3) a small required core and a free `extra` object the scheduler stores but does not interpret.
- **Blocks:** F2, F4, C11, C10, N8, YT5, YT6, X5, X6, VFB3, VIG2

### AU-002

**Backfill marker: `job_kind = backfill` carried onto `items.normalized`, or `metrics_observation = backfill` on `raw.items`**

- **Type:** names, shape
- **Where:**
  - a) Consumers of the marker: `comment-decay-scheduler §5.1 L66` "Posts with `job_kind = backfill` (carried from the raw envelope)"; `backfill-orchestrator §3 L25`, `§5.1 L48` ("Backfilled posts travel as ordinary traffic with `job_kind = backfill`"), `§13 L157` (criterion 9).
  - b) Target: `normalize-item §5.1 L45` "Backfill traffic from fb-backfill and backfill-orchestrator is ordinary live traffic with `job_kind = backfill` in the envelope"; `§5.2 L49` reads `job_kind` from the envelope; the `items.normalized/v1` record (`§6.2 L95`-`L119`) has no `job_kind` and the PRD never says it is copied.
  - c) Producers: only `x-full-archive-search §6.2 L106`/`L112` writes `"job_kind": "backfill"`; `fb-backfill §6.2 L88`/`L103` marks backfill with `"metrics_observation": "backfill"`; `ig-account-media-poller §5.1 L50`, `ig-keyword-search §5.1 L51`, `ig-mentions-fetcher §5.1 L49` "carry `metrics_observation = backfill`".
- **At stake:** the scheduler cannot tell backfilled posts from live ones and opens a full series for 90 days of history; backfill-orchestrator's criterion 9 cannot pass.
- **Options:** (1) every backfill service writes `job_kind` in the raw envelope and normalize-item copies it onto `items.normalized/v1`; (2) normalize-item derives the marker from `metrics_observation = backfill` and publishes one field; (3) the scheduler reads `metrics_observation` from `items.normalized` (the field added there).
- **Blocks:** F2, C4, C10, C11, FB3, IG3, IG5, VIG1, X5

### AU-003

**`news.dedup` and the story fields: normalize-item neither reads the topic nor carries the fields**

- **Type:** writers, shape
- **Where:**
  - a) `news-dedup §1 L9`, `§4 L35`, `§6.2 L104` "normalize-item copies `story_id`, `is_origin` and `duplicate_of` onto the normalized item and re-emits the story fields as a new version when an update arrives"; `§8 L119` "normalize-item proceeds with a null verdict"; `§14 Q1 L167` "with a bounded wait in normalize-item". `README L183` (decision 6) "a new topic `news.dedup` from news-dedup to normalize-item".
  - b) Target: `normalize-item §6.1 L86` reads `raw.items`, `jobs.normalize-item`, `source.events` only; the `items.normalized/v1` record (`§6.2 L95`-`L119`) has no `story_id`, `is_origin` or `duplicate_of`; no wait step in `§5.2`; a new version only when the content hash changes (`§5.2 L52`), which a story update does not do.
- **At stake:** unique-story counts and story-level alerts need the three fields on every news item; as written the verdict is never applied and a `story_update` cannot produce a version.
- **Options:** (1) normalize-item consumes `news.dedup` with a bounded wait and adds the three fields to `items.normalized/v1`; (2) a table-only join on `news_story_members` by store-writer and aggregator (news-dedup's fallback in Q1), topic dropped; (3) news-dedup publishes story records that consumers join on `item_id`.
- **Blocks:** F2, C4, N7, C6, C15, A5

### AU-004

**LinkedIn reaction events as counter increments: `item.metrics` has only absolute observations**

- **Type:** shape, rule
- **Where:**
  - a) `li-notification-receiver §14 Q4 L201`: "Should normalize-item turn reaction events into counter increments ... Proposed: both, with the poller's absolute counts as the baseline".
  - b) Target: `normalize-item §5.2 L56` publishes "one `item.metrics` observation per record that carries counts", from the record's `metrics_snapshot` (`§6.2 L114`); there is no increment or delta form, and li-notification-receiver has no mapper (AU-052).
- **At stake:** an increment published as an observation overwrites the absolute count in `metrics_timeseries`; mixing both needs a field saying which one a message is.
- **Options:** (1) absolute observations only, from li-client-posts-poller's reads; (2) a delta form of `item.metrics` with a marker field, applied on top of the latest absolute value; (3) reaction events update an in-memory running count in normalize-item, published as absolute observations.
- **Blocks:** F2, C4, LI3, LI1, C6

### AU-005

**Early discovery hits: `context.discovery_hit_emitted` against keyword-matcher emitting anyway**

- **Type:** shape, writers
- **Where:**
  - a) `x-recent-search §5.2 L58`: one `discovery.hits` message per unregistered author, "flagging the envelope `context.discovery_hit_emitted = true` so keyword-matcher does not emit a second one".
  - b) Target: `keyword-matcher §5.1 L40` reads `items.normalized` (whose `items.normalized/v1` record, `normalize-item §6.2 L95`-`L119`, has no `context`) and says "x-recent-search and tg-message-search may emit an early `discovery.hits` for the same candidate; poster-resolver deduplicates by `candidate_key`, so both paths are safe"; `CONVENTIONS L281` says the same.
- **At stake:** the flag never reaches keyword-matcher, so two discovery hits are emitted per candidate (harmless only if poster-resolver deduplicates, as CONVENTIONS says); x-recent-search's single-hit expectation fails.
- **Options:** (1) both emit and poster-resolver deduplicates (target, CONVENTIONS); (2) normalize-item carries the flag onto `items.normalized` and keyword-matcher skips flagged candidates; (3) only keyword-matcher emits discovery hits.
- **Blocks:** C5, C4, C8, X1

### AU-006

**Hit field read by analysis-sentiment: `matched_text` or `matched_term`**

- **Type:** names
- **Where:**
  - a) `analysis-sentiment §5.2 L59`: "cut the sentence window around `matched_text`"; `§14 Q7 L174` "hit field names with keyword-matcher" to confirm.
  - b) Target: `keyword-matcher §5.3 L65` "`matched_term` is the longest matching form as the client wrote it", with `offsets` as code-point spans in `text_norm`; `§6.2 L108` `"matched_term"`.
- **At stake:** the aspect path reads a field that is not on the hit; the client's spelling in `matched_term` is not the text as it appears in the item, so the window has to come from `offsets`.
- **Options:** (1) `matched_term` plus `offsets` (target); analysis-sentiment cuts the window from `offsets`; (2) add `matched_text` (the matched span of `text_norm`) to both hit topics.
- **Blocks:** F2, C5, A1

### AU-007

**Resolver answers: on `jobs.poster-resolver` to poster-resolver, or straight onto `poster.profiles` by each resolver**

- **Type:** writers, shape
- **Where:**
  - a) Target: `poster-resolver §4 L37` resolvers "receive `resolve` jobs on `jobs.<resolver>`, answer on `jobs.poster-resolver`"; `poster-resolver §5.3 L70` "The resolver answers on `jobs.poster-resolver` with `kind: resolved` ... or `kind: unresolvable`"; `§1 L9` it "merges their answers into one `poster.profiles` schema"; it alone writes `poster.profiles` (`§6.2 L86`), applies the cache, the individuals gate and `lang_share` (`§5.2 L53`-`L59`).
  - b) Each resolver writes `poster.profiles` itself and none mentions `jobs.poster-resolver`: `fb-page-resolver §6.2 L99`, `ig-account-resolver §6.2 L102`, `tt-user-resolver §6.2 L86` ("the topic's own schema"), `x-user-resolver §6.2 L101`, `li-org-resolver §6.2 L79`, `tg-channel-resolver §6.2 L77`, `yt-channel-resolver §6.2 L103`, `news-site-resolver §6.2 L79`; `li-org-resolver §4 L38` "poster-resolver dispatches candidates and reads the result".
- **At stake:** poster-resolver waits on a queue no resolver writes (15-minute timeout, five attempts, then DLQ for every candidate), while the qualifier receives eight resolver shapes that skipped the cache, the individuals gate and `lang_share`.
- **Options:** (1) resolvers answer on `jobs.poster-resolver` and only poster-resolver writes `poster.profiles` (target); (2) resolvers write `poster.profiles` and poster-resolver only dispatches, deduplicates and caches by consuming that topic; (3) resolvers write `poster.profiles` in poster-resolver's single schema and poster-resolver stops emitting.
- **Blocks:** F2, C8, C9, FB1, IG1, VTT3, X2, VLI2, VTG2, YT1, N2

### AU-008

**`discovery.hits` fields: the "approved poster-resolver schema" other PRDs defer to is not defined, and poster-resolver ignores `candidate_pending` and caption handles**

- **Type:** shape, partition
- **Where:**
  - a) `search-hit-router §6.2 L134` "The field set beyond `candidate_key`, `platform` and `type` follows poster-resolver's approved schema where it differs" and `§14 Q3 L196`; `web-commoncrawl-scanner §6.2 L103` (same words) and `§14 Q3 L168`.
  - b) Target: `poster-resolver §6.1 L81` defines no fields, only "partition key: the keyword or hashtag source that produced the hit; the candidate is in the payload"; it has no `type`; the only field-level definition is `keyword-matcher §6.2 L99`-`L116` (`discovery.hits/v1`, keyed by `source_id`, `§6.2 L95`).
  - c) `keyword-matcher §14 Q2 L181` "poster-resolver must treat `candidate_pending = true` as mention-only" (a pending hit has `candidate.platform_id` null, `§8 L132`); the target never mentions `candidate_pending`.
  - d) `ig-hashtag-search §12 L169` "discovery hits carry caption handles and the permalink; poster-resolver matches them against the registry"; the target matches only the hit's candidate against `sources` (`poster-resolver §6.1 L83`) and has no caption-handle step.
- **At stake:** producers emit different shapes while pointing at a schema nobody wrote; a pending hit yields no buildable `candidate_key`; Instagram hashtag posters are never resolved.
- **Options:** (1) keyword-matcher's `discovery.hits/v1` is the schema and other producers conform, with poster-resolver listing the fields it requires (including `candidate_pending`); (2) poster-resolver's PRD defines the schema (candidate block, `type`, `origin`, evidence) and keyword-matcher conforms; (3) two message types under one topic, item hits and source candidates, told apart by `type`.
- **Blocks:** F2, C5, C8, W3, W5, IG2

### AU-009

**`poster.profiles` fields the qualifier's rules need, which poster-resolver does not emit; resolver signals the qualifier never reads**

- **Type:** shape, enum
- **Where:**
  - a) Target: `qualifier §5.4 L71` "From `poster.profiles`: every field listed in the `poster-resolver` PRD"; rule 4 (`§5.2 L55`) "More than 50 posts a day with over 60% duplicate text → `reject`. Default avatar on an account under 30 days old → `review`"; rule 6 (`§5.2 L57`) "`push` when `owned_by_client`"; the decision carries `source_type` and `owned_by_client` (`§6.2 L84`).
  - b) `poster-resolver §6.2 L89` profile: `posts_30d`, `last_post_at`, `location_text`, `country_signals` (`iraqi_place`, `phone_964`, `iq_domain`, `outlet_link`, `seed_list`), `lang_share`, and no posts-per-day peak, duplicate-text share, avatar flag, account age (`created_at` is received, `§5.4 L74`, but not emitted), `owned_by_client` or `source_type`.
  - c) Resolver promises the qualifier does not support: `li-org-resolver §8 L124` "the profile is emitted with `posts_sampled = 0` and the qualifier treats it as inactive"; `tg-channel-resolver §5.4 L67` the vendor's country "counts as one Iraqi signal, not two" (not among rule 2's signals, `qualifier §5.2 L53`); `x-user-resolver §12 L171` "watchlist-only passes carry `qualifies_by = ["watchlist"]` for review" (no such review rule); `tg-channel-resolver §8 L120` "Not indexed by the vendor: `unresolved: not_indexed`; the qualifier raises a review card", while rule 1 sends every `unresolvable` to `reject` (`qualifier §5.2 L52`).
- **At stake:** rules 4 and 6 cannot be evaluated from the profile as specified, and four resolvers expect outcomes (inactive, one signal, review) the qualifier's rules do not produce.
- **Options:** (1) extend poster-resolver's profile with the rule-4 and rule-6 fields and fix closed lists of signals and unresolvable reasons the qualifier maps; (2) the qualifier drops or rewrites the rules it cannot evaluate from the profile; (3) per-platform profile extensions that the qualifier reads by platform.
- **Blocks:** F2, C8, C9, VLI2, VTG2, X2

### AU-010

**A Parquet archive of normalized items: normalize-item and the four analysis services expect one; raw-archiver archives `raw.items` only**

- **Type:** writers, shape
- **Where:**
  - a) `normalize-item §4 L33` raw-archiver consumes `items.normalized` for a "monthly Parquet of normalized items".
  - b) Re-runs read "normalized items from raw-archiver's Parquet archive (`archive/<platform>/<yyyy>/<mm>/`)": `analysis-sentiment §5.1 L51` ("Models read only fields present in the archive (`title`, `text`, language fields, matched keyword)"), `analysis-topics §5.1 L50`, `analysis-entities §5.1 L46`, `analysis-media §5.1 L47`.
  - c) Target: consumes `raw.items` only (`raw-archiver §3 L19`, `§6.1 L92`); compaction writes, per platform and day, `archive/<platform>/<yyyy>/<mm>/<dd>-<part>.envelope.parquet` ("flattened envelope fields, `item_id`, `content_hash` of the payload, `raw_ref`") and `.payload.parquet` ("the payload as a JSON string column") (`§5.3 L67`, `§6.2 L96`); no normalized text, language fields or matched keyword; `linkedin_48h` is never compacted and `youtube_30d_text` payloads expire at 30 days (`§5.3 L67`, `L78`).
- **At stake:** model re-runs read fields that are not in the archive, so they must re-normalize and re-match raw payloads (and cannot reproduce live inputs) or have no source at all.
- **Options:** (1) raw-archiver also consumes `items.normalized` and writes a normalized Parquet with the fields the models read; (2) re-runs go through `raw.replay` with `target = analysis` (`raw-archiver §5.3 L71`) and normalize-item re-normalizes; (3) re-runs read ClickHouse `items` and `comments`.
- **Blocks:** C2, C4, F8, A1, A2, A3, A4

### AU-011

**`search.results`: neither archived nor normalized, though yt-web-search-bridge relies on both**

- **Type:** writers
- **Where:**
  - a) `yt-web-search-bridge §8 L148` "the raw response is archived by raw-archiver; the normaliser for `search.results` raises `schema_unknown` and parks the batch"; its PRD never mentions `raw.items`.
  - b) Target: raw-archiver consumes `raw.items` only (`raw-archiver §3 L19`, `§6.1 L92`); `normalize-item §6.1 L86` reads `raw.items`, `jobs.normalize-item` and `source.events`; neither reads `search.results`.
- **At stake:** the bridge's engine responses have no archive copy (no replay, no provenance record) and no parking on a shape change.
- **Options:** (1) yt-web-search-bridge also writes its responses to `raw.items`, as the web search services do; (2) raw-archiver also consumes `search.results`; (3) accept `search.results` as unarchived derived data and drop the claim.
- **Blocks:** C2, C4, YT9

### AU-012

**Readers named for `raw.items` and `discovery.hits`: keyword-matcher, lang-dialect-id, store-writer and the qualifier read other inputs**

- **Type:** writers, names
- **Where:**
  - a) `tg-message-search §4 L34` "normalize-item, lang-dialect-id and keyword-matcher consume `raw.items`" and "poster-resolver and qualifier consume `discovery.hits`"; `§11 L126` (with raw-archiver); `ig-hashtag-search §4 L37` "normalize-item, lang-dialect-id, keyword-matcher and store-writer consume `raw.items`"; `ig-hashtag-search §4 L36` "poster-resolver and qualifier consume `discovery.hits`".
  - b) Targets: keyword-matcher reads `items.normalized` (`keyword-matcher §5.1 L40`, `§6.1 L90`); lang-dialect-id has "no topic, consumer group, cursor or rotation" (`lang-dialect-id §5.1 L43`); store-writer reads `items.normalized`, `items.analysis`, `item.metrics`, `item.hits`, `discovery.hits`, `source.events` (`store-writer §3 L22`); the qualifier reads `poster.profiles` (`qualifier §6.1 L76`). Only normalize-item and raw-archiver read `raw.items`.
- **At stake:** fields these producers put on `raw.items` for those consumers (for example x-recent-search's flag in AU-005) never reach them unless normalize-item carries them; schema changes on `raw.items` are coordinated with the wrong services.
- **Options:** (1) correct the producers' lists: `raw.items` is read by normalize-item and raw-archiver only, `discovery.hits` by poster-resolver (and store-writer); (2) in addition, list in contracts which raw fields normalize-item must carry onto `items.normalized` for downstream use.
- **Blocks:** F2, C4, IG2, VTG1

### AU-013

**`item_id` on `deletions`: optional in the propagator's minimum shape, required by alert-evaluator**

- **Type:** shape
- **Where:**
  - a) `alert-evaluator §14 Q3 L165` "deletion-propagator must name the deletion reasons and carry `item_id`"; `§11 L134` lists "deletion-propagator (`deletions`)" as its source; it consumes `deletions` for the deletion rule (`§5.1 L40`).
  - b) Target: deletion-propagator consumes `deletions`, it does not emit them (`deletion-propagator §3 L19`); its minimum shape requires `reason`, `scope` and a target given as `platform`, `kind` and `platform_id` or `item_ids`, or `author_hash`, `source_id` or `client_id` (`§5.4 L80`), so `item_id` is optional; the reasons are named (`§3 L19`).
- **At stake:** alert-evaluator's deletion rule cannot match its watch set for messages that identify items by key, author, source or client.
- **Options:** (1) every producer adds `item_ids` (derived with the SDK helper) to every item-scope message; (2) alert-evaluator derives `item_id` from the key itself and ignores non-item scopes; (3) deletion-propagator publishes a completion message with resolved item ids that alert-evaluator consumes instead.
- **Blocks:** F2, C13, A5

### AU-014

**Analysis outputs as aggregate dimensions: topic ids from several taxonomies, and the `mixed` label in the negative share**

- **Type:** names, enum, shape
- **Where:**
  - a) `aggregator §5.3 L55` `sentiment` "takes the labels of analysis-sentiment plus `pending` ... and `unscored`", `topic_id` "comes from analysis-topics"; example `"topic_id": "tp_0042"` (`§6.2 L87`); `§14 Q5 L160` "names follow `items.analysis/v1`; confirm"; the negative share is "negative mentions divided by positive, neutral and negative mentions (`pending` and `unscored` left out)" (`§5.3 L57`), and `alert-evaluator §5.3 L58` uses the same denominator.
  - b) Target analysis-sentiment: four labels "positive, negative, neutral, mixed" (`analysis-sentiment §2 L15`).
  - c) Target analysis-topics: one message "per item per taxonomy (`task = topics:<taxonomy_id>`)" (`analysis-topics §5.2 L60`); topics are `node_id`s inside a taxonomy (`§5.3 L68`, `§5.3 L72`; example `"task": "topics:global"`, `"node_id": "outage"`, `§6.2 L105`-`L111`); the aggregate grain has no taxonomy column (`aggregator §5.3 L55`).
- **At stake:** `mixed` mentions silently leave the negative share and its alert; topic counts from the global and a client taxonomy collide or double count under one `topic_id`.
- **Options:** (1) `topic_id` as `<taxonomy_id>:<node_id>` and `mixed` added to the share denominator; (2) only the global taxonomy feeds aggregates (client taxonomies queried separately) and `mixed` excluded on purpose, documented; (3) a taxonomy column in the grain.
- **Blocks:** C15, A1, A2, A5, F8

### AU-015

**How a backfilled record is marked: `job_kind = backfill` is expected, `metrics_observation = backfill` (or nothing) is written**

- **Type:** names; shape; rule
- **Where:**
  - Readers that expect `job_kind`: normalize-item §5.1 L45 "Backfill traffic from fb-backfill and backfill-orchestrator is ordinary live traffic with `job_kind = backfill` in the envelope", §5.2 L49 reads `job_kind` from the envelope; comment-decay-scheduler §5.1 L66 "Posts with `job_kind = backfill` (carried from the raw envelope) ... get one fetch (`series_step = once`)"; backfill-orchestrator §3 L25 ("Making backfilled posts recognisable (`job_kind = backfill`)"), §5.1 L48 and §13 L157 "A backfilled fixture post arrives with `job_kind = backfill`".
  - fb-backfill (the producer normalize-item names) writes no `job_kind`: its envelope differs from the poller's only in `service` and `metrics_observation` (§6.2 L88), with `"metrics_observation": "backfill"` and a `window` (L103-L104); §13 L165 makes `metrics_observation = backfill` the acceptance criterion.
  - Other backfill producers: ig-account-media-poller §5.1 L50 "Messages from a backfill read carry `metrics_observation = backfill`" (no `job_kind`); fb-group-posts-poller §5.1 L50 writes backfill "to `raw.items` like any poll" (envelope `"metrics_observation": "poll"`, L118); fb-keyword-search §5.1 L48 backfill, envelope `"metrics_observation": "search"` (L114). Only x-full-archive-search writes both (`"job_kind": "backfill"` L112 and `"metrics_observation": "backfill"` L122, §6.2 L128).
- **At stake:** comment-decay-scheduler gives backfilled posts one `once` fetch only when it sees `job_kind = backfill`; with fb-backfill's envelope as written, a backfilled post younger than the last series step is not recognised and opens a normal series (fb-backfill §5.1 L47 itself expects a series aligned to `created_time`), and normalize-item finds no `job_kind` to carry.
- **Options:** (1) `job_kind` becomes a required envelope field written by the SDK job wrapper from the job's `kind` for every producer; (2) `metrics_observation = backfill` is the marker and normalize-item, comment-decay-scheduler and backfill-orchestrator read it; (3) both, with `metrics_observation` kept only for the counts label.
- **Blocks:** F2, F4, C4, C10, C11, FB3, VFB1, VFB2, IG3, X5.

### AU-016

**Push-tier changes asked of registry-writer by the receivers have no input path, and the `push_lease_lapsed` event yt-uploads-reconciler waits for is never emitted**

- **Type:** writers; shape; enum
- **Where:**
  - yt-uploads-reconciler §5.1 L51: "yt-pubsub-receiver flags the channel on `source.events` (`updated`, `reason = push_lease_lapsed`)"; §6.1 L104; §13 L189; §14 Q4 L201: "The lapse flag's shape must match yt-pubsub-receiver's PRD when it is written."
  - yt-pubsub-receiver writes no `source.events`: a lapsed lease means "registry-writer sets the channel's `next_poll_at` to now" (§5.1 L42), through "requests to registry-writer (push, promotion, `next_poll_at`, `health`)" (§6.2 L130).
  - fb-client-webhook-receiver also "asks registry-writer" to promote a dormant Page back to push (§5.1 L42, §13 L189) and to return a Page to its reach tier when its subscription fails (§5.2 L59).
  - registry-writer's inputs are `registry.decisions`, its manual endpoint and the canary's health change (§5.4 L81); it owns `tier` and `health` but not `next_poll_at` after insert (§3 L27), and lists no request from a receiver.
- **At stake:** a lapsed YouTube lease is never caught up at once, a failed Facebook subscription never drops the Page back to reach-tier polling, and dormant push sources are never promoted, because the signal has no carrier.
- **Options:** (1) receivers emit `registry.decisions` (`tier_change`, `promote`, `update`) that registry-writer applies, and registry-writer emits `source.events` `updated` with a `reason` (`push_lease_lapsed`); (2) receivers write `source.events` themselves with an agreed `reason` vocabulary; (3) a registry-writer request endpoint for receivers, named in F2.
- **Blocks:** F2, C7, FB7, YT2, YT3.

### AU-017

**Backfill completion: backfill-orchestrator waits for a `jobs.completed` report with `oldest_item_at`, `capped` and `capped_reason`; fb-backfill sends none, the others send other fields, and several services write `backfill_status` themselves (Telegram's receivers `capped` where the orchestrator sets `done`)**

- **Type:** shape; writers; enum
- **Where:**
  - backfill-orchestrator §5.2 L59 ("Consume the completion event from `jobs.completed`; write `done` or `capped`, `backfill_runs` counters, and `next_poll_at = now()`"), §5.4 L92 (example event from `"service": "fb-backfill"` with `report` `{new_count, pages, cost_units, oldest_item_at, capped, capped_reason}`), §5.3 L81 (`capped_reason`: `route_cap`, `budget`, `deadline`, `failed`), §5.2 L60 and §13 L158 (no completion by the timeout: re-emit with the same `job_id`).
  - What the backfill services report: x-full-archive-search §5.2 L57 (status, `new_count`, `seen_count`, `pages`, `cost_units`); yt-uploads-reconciler §5.2 L66 (`new_count`, `seen_count`, `pages`, `cost_units`); tt-profile-videos-poller §5.1 L51 (`oldest_seen` and `pages`); news-sitemap-poller §6.2 L127 (`coverage_days`, `urls_emitted`); fb-backfill writes no `jobs.completed` (§6.2 L110). None reports `oldest_item_at` or `capped_reason`.
  - Who writes `backfill_status`: fb-backfill sets `done`/`capped` and `next_poll_at` itself (§5.2 L56), which backfill-orchestrator accepts "until its next revision" (§14 Q2 L163); fb-group-posts-poller (§5.1 L50) and tg-channel-posts-poller (§5.1 L54, "the service sets `done` or `capped`") do too; tt-keyword-search (§5.1 L44) and tt-hashtag-feed-poller (§5.1 L48) run their own backfill and move the status themselves; ig-account-media-poller "reports `done` or `capped`" (§5.1 L50). tg-bot-channel-receiver (§5.1 L50) and tg-discussion-receiver (§5.1 L51) set `capped` at onboarding, while backfill-orchestrator sets `done` at once for a green Telegram channel (§5.3 L76).
  - The topic and its other names are CF-089; the extra writers of the `sources.backfill_status` column are a B question.
- **At stake:** backfill-orchestrator never hears that fb-backfill finished, so the run stays `running` until the timeout re-emits it and the Page is read again; `capped_reason` and `backfill_runs` coverage cannot be filled from any report; the same Telegram case ends `done` or `capped` depending on which writer runs last.
- **Options:** (1) one backfill report in `jobs.completed/v1` with required `status` (`done`/`capped`), `capped_reason`, `oldest_item_at` and the counts, and backfill-orchestrator the only writer of `backfill_status`; (2) the services set `backfill_status` themselves and backfill-orchestrator records `backfill_runs` from `source.events` `updated`; (3) as (1), with route extras (`coverage_days`, `oldest_seen`, `seen_count`) optional and the green Telegram value fixed in the route table.
- **Blocks:** F2, F4, C10, FB3, VFB2, IG3, VTT1, VTT2, VTT4, X5, TG1, TG2, VTG3, YT3, N4.

### AU-018

**Subscribing a client-owned Instagram account: registry-writer leaves it to the receiver on `added`; ig-webhook-receiver reads no `source.events` and subscribes "on connecting", with no trigger defined**

- **Type:** writers; rule
- **Where:**
  - registry-writer §3 L32: "`fb-client-webhook-receiver`, `ig-webhook-receiver`, `li-notification-receiver`, `yt-pubsub-receiver` and `tg-bot-channel-receiver` react to `added` themselves".
  - ig-webhook-receiver §5.1 L45: "Connecting an account creates its subscription here"; it reads Meta's requests, `jobs.ig-webhook-receiver`, `sources`, `clients`, `cursors`, Vault and the fetchers' job results (§6.1 L99), no `source.events`; its only later subscription action is the daily re-check (§5.2 L60).
  - The others subscribe on `added`: fb-client-webhook-receiver §5.1 L46 and §6.1 L105; li-notification-receiver §5.1 L42; yt-pubsub-receiver §5.1 L38 and §5.2 L50.
- **At stake:** IG4 has no event that tells it an account was connected, so a client's account can be registered as push with no webhook subscription until the daily check notices the absence, if it does.
- **Options:** (1) ig-webhook-receiver consumes `source.events` `added` (`owned_by_client = true`) like the other receivers; (2) the client-portal connection flow calls ig-webhook-receiver directly, and registry-writer's line is corrected; (3) the daily check also subscribes any owned account that has no subscription yet.
- **Blocks:** C7, IG4.

### AU-019

**Partition key of search finds on `raw.items`: normalize-item expects the producer to key them on the poster, while CONVENTIONS and the producers key them on the rule's `source_id`**

- **Type:** partition; key
- **Where:**
  - normalize-item §5.1 L41: "records without a `source_id` (keyword searches, hashtag feeds, search results) are keyed by the producer on `<platform>:<poster platform_id>`, which keeps a poster's post and its later comments together"; §6.2 L91 (`items.normalized` "keyed by `source_id` or poster key").
  - CONVENTIONS L281: a search service writes `raw.items` "with `source_id` = the keyword-rule or hashtag source that produced the query".
  - Producers key on that rule or hashtag: ig-hashtag-search §6.2 L91; tt-keyword-search §6.2 L73; tt-hashtag-feed-poller §6.2 L79; yt-keyword-search §6.2 L96; web-search-perplexity §6.2 L89 (`web:<source_id>`).
  - Extends PART, which lists the `items.normalized` and web `raw.items` keys but not this rule.
- **At stake:** the ordering normalize-item relies on (a poster's post and its comments on one worker) does not hold for search finds, and the same post found by two rules lands on two partitions; code written to normalize-item's text waits for a key no producer sets.
- **Options:** (1) search finds keep the rule's `source_id` as partition key (CONVENTIONS L281) and normalize-item drops the poster-key rule; (2) search producers partition on `<platform>:<poster platform_id>` while the envelope keeps the rule's `source_id`; (3) the item's own `idempotency_key` as partition key for search finds.
- **Blocks:** F2, F4, C4, IG2, VTT1, VTT2, YT8, W1, W2, W4.


## 2. Tables, columns and storage

### AU-020

**comment_series columns that fetchers keep their per-post cursor in (`newest_comment_at`, thread id)**

- **Type:** shape, writers
- **Where:**
  - a) `li-own-comments-fetcher §6.3 L130` "the marker and running total sit in the series state owned by comment-decay-scheduler"; `§5.2 L64` reports "the new `newest_comment_at` to comment-decay-scheduler".
  - b) `li-post-comments-fetcher §5.1 L50` "The newest-seen marker (`newest_comment_at`) and the running total of comments seen live in the series state owned by comment-decay-scheduler"; `§6.3 L133`.
  - c) `news-comments-fetcher §6.3 L124` "the job carries the newest stored comment time and the thread id; the result row returns them to comment-decay-scheduler"; `§5.1 L41`.
  - d) Target: `comment-decay-scheduler §6.3 L147` `comment_series` columns (item_id, source_id, route, profile, next_step, next_due_at, last_new_count, last_total, status, plus proposed lane, anchor_at, last_fetched_at, extended, hot_next_at, hot_until, hot_count, in_flight_job_id): no `newest_comment_at`, no thread id; the report (`§5.4 L127`) and the job (`§6.2 L141`) carry neither.
- **At stake:** the LinkedIn fetchers have no cursor of their own and their held comments expire at 48 h; if the scheduler neither stores nor sends the marker, each fetch re-reads or cannot stop at the right comment; news cannot pass its thread id between fetches.
- **Options:** (1) add `newest_comment_at` and an opaque per-post cursor (thread id) to `comment_series`, the completion report and the job; (2) each fetcher keeps a per-post cursor in its own table; (3) a generic `fetch_state` object carried from report to next job and stored by the scheduler without interpretation.
- **Blocks:** F3, F2, C11, LI2, VLI4, N8

### AU-021

**Stores and columns other PRDs expect registry-writer to write: `news_sites`, crawl-policy health, uploads playlist id, hashtag binding, ownership flip, client flags**

- **Type:** writers, single-PRD
- **Where:**
  - a) News: `news-site-resolver §6.2 L112` "registry-writer maps `proposed_source` onto the `sources` row ... and `site_profile` onto `news_sites`, keyed by `source_id`"; `§5.2 L46` sites with `crawl_allowed: false` are "registered with `health = blocked`"; `§5.2 L55` profile changes go to registry-writer; `news-feed-poller §5.1 L48` ("registry-writer writes the `sources` row and the `news_sites` profile"); `news-robots-checker §4 L35`, `§5.2 L61`, `§6.2 L117` "registry-writer maps `crawl_allowed = false` onto `sources.health = blocked`".
  - b) `yt-channel-resolver §3 L27` and `§6.3 L138` "the stored uploads playlist id are written by registry-writer".
  - c) `ig-hashtag-search §5.1 L57` "Hashtags are bound to a client account at registration".
  - d) `li-company-posts-poller §3 L26` and `§13 L180` "registry-writer flips it to `route = green`" when a client starts administering a page.
  - e) `quota-governor §11 L143` "registry-writer (client flags)".
  - f) Target: owns the `sources` columns of `registry-writer §3 L27` (no uploads playlist id, no bound account); writes `sources`, `client_sources`, `registry_audit` only (`§6.2 L91`), neither `news_sites` nor `clients` (which it reads, `§6.1 L88`); `add` always sets `health = ok` (`§5.2 L52`); an `add` on an existing row merges only `client_ids`, tier, followers, display name and handle (`§5.3 L70`-`L73`), so route and `owned_by_client` stay; a route change needs an `update` decision (`§5.2 L56`) that no PRD says who sends.
- **At stake:** news site profiles, crawl-blocked health, YouTube uploads playlist ids and Instagram hashtag bindings have no writer, and a page a client starts administering stays on the amber route.
- **Options:** (1) registry-writer takes these fields into its decision schema (site profile, crawl health, uploads playlist id, bound account, ownership flip); (2) each producing service keeps its own table (`news_sites` by news-site-resolver, playlist id in yt-channel-resolver's cache) and registry-writer stays as written; (3) identity-level fields through registry-writer, platform profiles in service tables.
- **Blocks:** F3, C7, N1, N2, N3, YT1, IG2, VLI3, C1

### AU-022

**Tombstones against the resurrection guard: deletion-propagator's `is_deleted` rows and store-writer's `deletion_requests` check and version formula**

- **Type:** writers, key, rule
- **Where:**
  - a) `deletion-propagator §5.3 L62` (a): "Insert tombstone rows into `items` and `comments` with `is_deleted = 1` and a version greater than any content version (deletion time) ... store-writer drops upserts for an id that has a tombstone"; `§4 L37` "store-writer (must honour tombstones)"; `§14 Q2 L172` "store-writer's tombstone rule need[s] to be aligned"; `raw-archiver §12 L162` "the ReplacingMergeTree tombstone version outranks replayed content".
  - b) Target: the guard drops rows "whose `item_id` is in `deletion_requests` with status done" (`store-writer §5.2 L49`, `§13 L174`); `items` and `comments` have no `is_deleted` column (`§5.3 L67`); `row_version = (version << 32) | produced_at` and "for equal versions the later production ... wins" (`§5.3 L67`), so a tombstone versioned by deletion time ranks below every content row and a later replay outranks it; store-writer is "the single writer of the analytics store" (`§1 L9`).
  - c) The guard's input: store-writer drops by "`item_id` ... in `deletion_requests` with status done" (`store-writer §5.2 L49`), but deletion-propagator keys `deletion_requests` by `deletion_id` (`deletion-propagator §5.2 L47`), ends at status `completed` (`§5.3 L76`), stores only counts (`items_resolved`, `found`) in `verification` (`§6.2 L98`), and author- or client-scope deletions name no items (`§5.3 L60`).
  - d) Re-ingestion: `retention-purger §14 Q2 L171` proposes "a check in normalize-item against `deletion_requests` hashes"; normalize-item reads no `deletion_requests` (`normalize-item §6.1 L86`-`L88`).
- **At stake:** two writers of `items` and `comments` with incompatible version rules: a tombstone is collapsed away by the next content upsert, and only the `deletion_requests` check (which depends on deletion-propagator marking rows done) keeps deleted items out.
- **Options:** (1) the `deletion_requests` guard only, with deletion-propagator deleting rows but writing no tombstones; (2) tombstones with an `is_deleted` column and a `row_version` from the shared SDK formula set above any content version, checked by store-writer; (3) both, with the version formula and guard in listening-sdk.
- **Blocks:** F8, C6, C13, C14, C2

### AU-023

**ClickHouse `analysis` key: (`item_id`, `model`) with the newer version replacing the older, against `item_id:task:model_version` with re-runs side by side**

- **Type:** key, shape
- **Where:**
  - a) Target: `store-writer §5.3 L61` `analysis` version `analyzed_at` (ms), sorting key `item_id, model`, "a newer model version replaces the older"; `§5.3 L67` it "carries `model`, `model_version`, the `output` JSON and typed projections".
  - b) `README L184` (decision 7) "`items.analysis/v1` keyed by `item_id:task:model_version`"; `analysis-sentiment §6.2 L89` "logical key `item_id` + `task` + `model_version`", with tasks `sentiment` and `sentiment_aspect`; the message carries `task`, `model_version`, `produced_at` and `result`, not `model` or `analyzed_at` (`§6.2 L95`-`L105`); `§5.1 L51` "New rows sit beside the old; nothing is overwritten until the switch-over".
  - c) `analysis-entities §4 L33` "store-writer persists entity rows"; the target stores one `analysis` row per item and model with "entity ids" as a projection (`store-writer §5.3 L67`), no entity table.
  - d) Read side: `aggregator §5.3 L53` uses "the latest `analysis` row per item and model" and reads no `model_versions` (`§6.1 L72`-`L74`), while `analysis-sentiment §5.3 L76` says "Switch-over flips one row; aggregator then reads the new version" (delta assumption of analysis-sentiment).
- **At stake:** with (`item_id`, `model`) as the ReplacingMergeTree key a re-run row replaces the live row at once (no side-by-side, no switch-over), two tasks of one item may collapse if `model` is not task-specific, and the version column the table needs is not in the message.
- **Options:** (1) sorting key (`item_id`, `task`, `model_version`) with version `produced_at`, the active version chosen at read time; (2) the target's key, with re-runs written to a separate table until switch-over; (3) one table per task with `model_version` in the key.
- **Blocks:** F8, C6, A1, A2, A3, A4, C15, A5

### AU-024

**`retention_audit`: written by retention-purger and by yt-text-purger, with different columns**

- **Type:** writers, shape
- **Where:**
  - a) `yt-text-purger §6.2 L159` "The audit record is a `retention_audit` row. retention-purger treats this row as the delegate's confirmation"; columns `failures`, `refresh_missed` (`L159`) and `parent_run_id` (`§13 L261`); `§4 L33` retention-purger "reads the audit row as confirmation".
  - b) Target: `retention-purger §6.2 L94` "the new append-only table `retention_audit`"; columns `run_id`, `started_at`, `finished_at`, `class`, `clock`, `cutoff`, `candidates`, `emitted`, `completed`, `delegated_to`, `verification`, `oldest_remaining_age_seconds`, `status`, `holds` (`§6.2 L110`); it waits on `deletion_requests` and its own verification (`§5.2 L51`-`L53`) and raises `delegate_unresponsive` on "no confirmation" (`§8 L127`) without naming the delegate's row.
- **At stake:** two services write one append-only table with different column sets, and the confirmation signal the target waits for is not defined.
- **Options:** (1) one `retention_audit` schema with the union of columns and a `writer` column; (2) yt-text-purger writes its own audit table and confirms through `deletion_requests` or a job result; (3) retention-purger writes every row, from a result yt-text-purger reports.
- **Blocks:** F3, C14, YT7

### AU-025

**`media/<sha256>`: stored through raw-archiver's media endpoint with `.refs`, or written directly by analysis-media**

- **Type:** writers, rule
- **Where:**
  - a) `raw-archiver §3 L21` "Media storage by content hash under `media/<sha256>`, with a reference list per hash"; `§3 L29` "downloading media (analysis-media and the fetch services; this service only stores what they hand over)"; `§5.3 L69` "`PUT` on the media endpoint takes bytes plus `item_id`, `retention_class`, `expires_at`" and appends the reference to `media/<sha256>.refs`; `deletion-propagator §5.3 L66` removes references through raw-archiver's media endpoint.
  - b) Target: `analysis-media §5.2 L52` "Fetch each media URL once ..., compute `sha256`, store `media/<sha256>` if absent"; `§6.2 L87` writes "`media/<sha256>` objects"; `§6.3 L114` "the url-to-`sha256` lookup via `media_fetch` rows in ClickHouse `analysis`"; `§14 Q3 L170` "Where does the url-to-hash and reference-count index live".
- **At stake:** two writers of `media/<sha256>`; objects written directly carry no `.refs`, so reference-based deletion never removes them and media outlives the item's retention class.
- **Options:** (1) analysis-media stores through raw-archiver's media endpoint, which keeps the references; (2) analysis-media owns `media/` and its own reference index, and deletion-propagator calls it; (3) one SDK media store that writes object and reference together for every writer.
- **Blocks:** C2, A4, C13, C14

### AU-026

**Telegram onboarding: onboarding records, one-time codes and a pre-allocated `source_id` that no table, registry path or admin-page document defines**

- **Type:** single-PRD; writers; shape
- **Where:**
  - tg-bot-channel-receiver §5.2 L67: "The control plane creates an onboarding record with a one-time code and a pre-allocated `source_id`"; L70: a `discovery.hits` candidate with `origin = client_onboarding` and `proposed_source_id`, after which "registry-writer creates the row (`route = green`, `vendor` null, `tier = push`, `added_by = client`). Because the id was pre-allocated, posts arriving before the row exists already land under the right `source_id`"; §6.1 L109 reads "the onboarding records"; §5.1 L50 sets `backfill_status = capped` at onboarding; §14 Q4 L197 asks whether registry-writer accepts `proposed_source_id`.
  - tg-discussion-receiver §5.2 L67: the group row comes from "a `discovery.hits` candidate with a pre-allocated `proposed_source_id`"; §5.1 L51 `backfill_status` is `capped` from onboarding.
  - registry-writer inserts with `source_id = gen_random_uuid()` and `backfill_status = 'pending'` (§5.3 L68-L69); its client and admin path is `POST /registry/sources`, which publishes a `manual_candidate` to `jobs.poster-resolver` (§5.2 L61); it names no onboarding record.
  - CONVENTIONS L30 lists no onboarding table; the admin page has no PRD.
- **At stake:** posts stored under the pre-allocated id are orphaned when registry-writer creates the row under a random id, and two writers set `backfill_status` to different values at creation.
- **Options:** (1) an `onboarding_requests` table in F3 and a registry-writer rule that adopts `proposed_source_id`; (2) the receiver buffers posts of a not-yet-registered chat and writes them once `source.events` `added` arrives; (3) onboarding goes through `POST /registry/sources` like any manual add and the receiver maps chats only after `added`.
- **Blocks:** F3, C7, C8, TG1, TG2.

### AU-027

**The YouTube uploads playlist id: no `sources` column, and each side says the other stores it**

- **Type:** single-PRD; writers
- **Where:**
  - yt-uploads-reconciler selects only channels with "a stored uploads playlist id" (§5.1 L43), reads "`sources` (with the uploads playlist id)" (§6.1 L104), calls `playlistItems` with the "uploads playlist id stored by yt-channel-resolver" (§5.3 L73, L78), and puts "Storing the uploads playlist id (yt-channel-resolver)" out of scope (§3 L30); on a playlist 404 "ops re-runs yt-channel-resolver" (§8 L154).
  - yt-channel-resolver returns `uploads_playlist_id` in `poster.profiles` (§6.2 L126) and puts "registering and storing the uploads playlist id (registry-writer)" out of scope (§3 L27); "`sources.followers` and the stored uploads playlist id are written by registry-writer, not here" (§6.3 L138).
  - registry-writer's owned columns (§3 L27) and its insert (§5.3 L68) have no such column; CONVENTIONS L36 lists none.
- **At stake:** no YouTube channel ever passes yt-uploads-reconciler's selector, so there is no backfill and no daily reconciliation for any channel; F3 has no column to add and no writer to give it.
- **Options:** (1) a `sources` column (for example `uploads_playlist_id`) written by registry-writer from the qualifier's decided row; (2) a YouTube side table keyed by `source_id`, written by yt-channel-resolver; (3) derive it at read time from the channel id (yt-channel-resolver §5.2 L62 forbids this: "never derive it from the channel id").
- **Blocks:** F3, C7, C9, YT1, YT3.

### AU-028

**Disqus site fields: news-comments-fetcher needs an identifier template that news-site-resolver parses but does not emit, and marks "the site's comments degraded" with no column to hold it**

- **Type:** single-PRD; writers
- **Where:**
  - news-comments-fetcher §5.1 L49 (onboarding needs `comments_provider = disqus`, the `disqus_shortname` "and an identifier template if the site uses one"), §5.2 L55 (thread lookup "by `ident:<identifier>` when the resolver's template yields one").
  - news-site-resolver parses "the `disqus_config` identifier template" (§5.2 L47; §3 L20 "identifier scheme"), but its profile carries only `comments_provider` and `disqus_shortname` (§6.2 L102; §5.4 L69 "comment provider and shortname"), and registry-writer maps that profile onto `news_sites` (§6.2 L112).
  - news-comments-fetcher §8 L139: a shortname Disqus rejects "marks the site's comments `degraded` and sends news-site-resolver a `refresh`"; neither `news_sites` nor `sources` has a comments-only state, and the resolver's refresh triggers (§5.1 L40) do not include this one.
- **At stake:** the template never reaches `news_sites`, so every thread lookup falls back to the URL forms; the comments `degraded` mark can only land in `sources.health`, which governs the whole site.
- **Options:** (1) `site_profile` and `news_sites` gain `disqus_identifier_template` and a comments health field; (2) template added; a rejected shortname instead sets `comments_provider = none` through a resolver refresh; (3) the extractor captures `disqus_identifier` per article (news-comments-fetcher §14 Q3 L186) and no template is stored.
- **Blocks:** F3, C7, N2, N6, N8.

### AU-029

**Raw responses outside `raw.items`: web-commoncrawl-scanner writes the raw path itself, and yt-web-search-bridge archives nothing although its PRD says raw-archiver does**

- **Type:** writers
- **Where:**
  - raw-archiver consumes `raw.items` and writes batches plus a manifest (§3 L19), runs integrity checks and lifecycle rules (§3 L23), and takes each `raw_ref` from the SDK's raw emit helper (§5.3 L61); search-hit-router counts on "the engines archive their raw responses" (§3 L33).
  - web-commoncrawl-scanner §5.2 L54: "Write the scan's per-host aggregate to object storage under the standard raw path (a direct write; this service has no `raw.items`)"; §6.2 L84.
  - yt-web-search-bridge writes no `raw.items` (§6.2 L102) yet states "the raw response is archived by raw-archiver" (§8 L148); the engines whose clients it shares archive every response to `raw.items` (web-search-perplexity §5.2 L55, web-search-mojeek §5.2 L57).
- **At stake:** the bridge's paid responses are never archived, so its provenance and replay rest on nothing; the scanner writes into raw-archiver's tree outside its manifests, integrity checks and lifecycle clock.
- **Options:** (1) both write `raw.items` records (`kind_hint`, `normalize = skip`, as the engines do) and raw-archiver stays the only writer under `raw/`; (2) direct writes allowed for non-item artefacts, with a path and manifest rule in raw-archiver; (3) the bridge's responses archived by the engines through `site_search` (AU-108 option 1), the scanner as (1) or (2).
- **Blocks:** C2, W5, YT9.


## 3. Keys, jobs, values, budgets, flags, retention and rules

### AU-030

**Series anchor: the post's first-seen time or its platform creation time, and what a backfilled post gets**

- **Type:** rule, job kind
- **Where:**
  - a) Target: `comment-decay-scheduler §5.1 L60` "Step offsets are measured from the post's first-seen time (`fetched_at` of its first `items.normalized` message), not its creation time"; `§5.1 L66` posts with `job_kind = backfill` "get one fetch (`series_step = once`) at the lowest priority, then `done`"; `CONVENTIONS L56` "Series after a post is first seen". `backfill-orchestrator §5.1 L48` agrees ("opens one `once` fetch for each and closes the series").
  - b) `fb-backfill §5.1 L47`: the series "is aligned to `created_time`, so a post 10 days old on arrival enters at the weekly step and a post older than 30 days gets no automatic fetch"; `§12 L153`.
  - c) `fb-reactions-fetcher §5.1 L41`: refresh jobs "due at `created_time + 24 h`" and "`created_time + 7 d`"; `§5.1 L45`: for backfilled posts the scheduler "emits refresh jobs only for the steps still in the future relative to `created_time`".
  - d) `yt-video-details-fetcher §5.1 L45`: metrics steps "due at `publishedAt` plus 24 h or 7 d"; "steps already past at first sight are not emitted".
  - e) `ig-own-comments-fetcher §14 Q2 L193`: series "counted from the media's own `timestamp` when first-seen lags it by more than 1 hour? Proposed: yes, a decision for comment-decay-scheduler".
  - f) `tt-video-stats-refresher §5.1 L44` uses the first-seen clock (agrees with the target), but `§5.1 L48` and `§14 Q3 L175` assume the scheduler "opens no metrics jobs" for a video first seen more than 7 days after publication; the target's metrics paragraph (`comment-decay-scheduler §5.1 L68`) has no age rule and the `once` rule (`comment-decay-scheduler §5.1 L66`) is stated for comments only.
- **At stake:** The scheduler computes `next_due_at` from `fetched_at`; three services expect due times from `created_time` or `publishedAt`, so every backfilled or late-seen post is scheduled differently on each side (one `once` fetch against a partial series), and metrics points land at different post ages.
- **Options:** (1) first-seen anchor for both lanes, backfilled posts get one `once` comment fetch (target, CONVENTIONS); (2) creation-time anchor (`created_time`, `publishedAt`, `timestamp`) for both lanes, skipping steps already past; (3) first-seen for comments, creation time for metrics; (4) first-seen unless it lags creation by more than a set threshold (ig-own-comments-fetcher's proposal), with an explicit age rule for the metrics lane.
- **Blocks:** C11, C10, FB3, FB4, IG6, YT4, VTT6

### AU-031

**Metrics jobs: `metrics` kind with `+24h` steps, or `refresh_24h` / `refresh_7d` kinds and `24h` / `7d` / `client` labels**

- **Type:** job kind, enum
- **Where:**
  - a) Target: `comment-decay-scheduler §5.1 L68` "`metrics` jobs at +24 h and +7 d"; step labels in the form `"series_step": "+6h"` (`§5.4 L127`, `§6.2 L141`); client refresh `series_step = refresh:<request_id>` (`§5.1 L70`). `CONVENTIONS L277` job kinds: rotation, reconciliation, backfill, comments, replies, `metrics`, ops_force.
  - b) `fb-reactions-fetcher §5.1 L41`: "`kind = refresh_24h`" and "`kind = refresh_7d`"; `§14 Q1 L186` asks the scheduler's PRD to confirm it emits them (alternative: "a small due-time table owned by this service").
  - c) `yt-video-details-fetcher §5.1 L45`: "`metrics` from comment-decay-scheduler, `series_step` `24h` or `7d` ... or `client`".
  - d) `tt-video-stats-refresher §5.1 L42`: `kind = metrics`, `series_step` (`+24h` or `+7d`), which matches the target.
- **At stake:** fb-reactions-fetcher dispatches on `kind` and has no `metrics` branch; yt-video-details-fetcher labels observations `24h`, `7d`, `client`, which never equal the scheduler's `+24h`, `+7d`, `refresh:<request_id>`, so idempotency keys and observation labels built from the step differ per side.
- **Options:** (1) `kind = metrics` with `series_step` `+24h`, `+7d`, `refresh:<request_id>` (target, CONVENTIONS kind list); (2) add `refresh_24h` and `refresh_7d` to the kind list; (3) `kind = metrics` with bare labels `24h`, `7d`, `client`.
- **Blocks:** F2, C11, FB4, YT4

### AU-032

**Telegram views refresh: tg-channel-posts-poller expects a +24 h `metrics` job that the scheduler never emits**

- **Type:** job kind, rule
- **Where:**
  - a) `tg-channel-posts-poller §5.1 L56`: "refreshes only Tier 1 posts, once, at +24 h, on a `metrics` job from comment-decay-scheduler"; `§6.1 L103` consumes kinds `rotation`, `reconciliation`, `backfill`, `metrics`, `ops_force`; `§4 L36` "comment-decay-scheduler (views-refresh jobs)".
  - b) Target: `comment-decay-scheduler §5.1 L68` metrics lane only on "Facebook green, Instagram green, TikTok amber and YouTube"; "On X, LinkedIn, Telegram and news the counts are recorded at first sight; whether to add +24 h and +7 d refreshes there is open question 6" (`§14 Q6 L207`); `§6.2 L138` writes no `jobs.tg-channel-posts-poller`; the metrics lane has no tier condition.
- **At stake:** the poller's `metrics` path has no producer, so Tier 1 Telegram views are never refreshed; if the scheduler adds the lane it needs a Tier-1-only, +24-h-only rule it does not have.
- **Options:** (1) the scheduler adds a Telegram metrics row (+24 h, Tier 1 only) to `jobs.tg-channel-posts-poller`; (2) no Telegram refresh in v1 (target as written) and the poller drops `metrics`; (3) the poller schedules its own refresh (departs from `CONVENTIONS L278`, "comment, reply and metrics jobs are emitted only by comment-decay-scheduler").
- **Blocks:** C11, VTG3

### AU-033

**Telegram own channels: a daily `health` job, or no jobs at all**

- **Type:** job kind
- **Where:**
  - a) Target: `comment-decay-scheduler §5.1 L57` tg_own: "push; one daily `health` job"; `CONVENTIONS L268` "push (live), daily health check".
  - b) `tg-discussion-receiver §4 L37` "comment-decay-scheduler holds a `push` row for this route and emits nothing for it"; `§5.1 L45` "comment-decay-scheduler emits no jobs for this route"; `§6.1 L110` its queue takes kinds `reconciliation`, `ops_force` only. `CONVENTIONS L277` has no `health` kind.
- **At stake:** a `health` job produced onto `jobs.tg-discussion-receiver` is a kind its consumer does not accept (ends in the DLQ), or the daily check named in CONVENTIONS runs nowhere.
- **Options:** (1) the scheduler emits the daily check under an existing kind the receiver accepts (`reconciliation`); (2) add `health` to the kind list and to tg-discussion-receiver; (3) no job: the daily check belongs to source-health-canary's canary channel and the scheduler only holds the push row.
- **Blocks:** F2, C11, TG2

### AU-034

**Reconciliation jobs and pushed counts: LinkedIn and Instagram push services expect the scheduler to act on counts it never reads**

- **Type:** job kind, writers, rule
- **Where:**
  - a) `li-own-comments-fetcher §5.1 L48`: "comment-decay-scheduler emits one reconciliation job a day when the latest comment count for the post (from li-client-posts-poller, through `item.metrics`) differs from its running total"; `§13 L183` (criterion 11).
  - b) `li-notification-receiver §5.1 L44`: "When a post's comment count differs from the running total of comments seen, comment-decay-scheduler emits a reconciliation job for li-own-comments-fetcher"; `§4 L34` the scheduler "counts comments from `items.normalized`, measures velocity"; `§5.1 L46` "Live events give comment-decay-scheduler the velocity between fetches".
  - c) `ig-webhook-receiver §5.1 L47`: the worker "exposes the count so comment-decay-scheduler can include it in the early-stop, extension and hot-post rules"; `§14 Q3 L191` "Proposed: yes".
  - d) Target: `comment-decay-scheduler §3 L21` emits `comments`, `replies` and `metrics` jobs only; `§6.1 L135` reads `items.normalized`, `jobs.completed`, `source.events`, `deletions` (not `item.metrics`, not live comment events); `§5.1 L42` consumes only `kind = post` from `items.normalized`; velocity comes from the completion report (`§5.3 L87`).
  - e) On Instagram the same daily reconciliation has another emitter: `ig-own-comments-fetcher §5.1 L41` "`reconciliation` jobs are emitted once a day per owned account by ig-webhook-receiver's scheduler".
- **At stake:** nobody emits LinkedIn reconciliation jobs, which li-notification-receiver calls its safety net for missed webhooks; the push count has no message or field to travel in; the two platforms put the same job under different emitters.
- **Options:** (1) the scheduler consumes `item.metrics` and pushed counts and emits `reconciliation` jobs for push routes; (2) each push receiver's own scheduler emits the daily reconciliation (as on Instagram) and the scheduler stays as written; (3) no count-based reconciliation; the regular series is the only safety net.
- **Blocks:** C11, LI2, LI3, IG4, IG6

### AU-035

**Replies jobs: one job per post with `thread_ids`, or one per thread; which profiles get them; per-thread series**

- **Type:** job kind, shape, rule
- **Where:**
  - a) Target: `comment-decay-scheduler §5.3 L94` "one `replies` job per post carries up to a configured number of `thread_ids`", threshold "TikTok 10, YouTube 5"; but `§5.1 L52` tt "`replies` job per comment with more than 10 replies" and `§5.1 L49` fb_group "`replies` job by comment id"; `§5.1 L50` ig_own "field expansion; no job"; replies are emitted only after a comments completion (`§5.2 L78`); state is one row per (`item_id`, `lane`) (`§6.3 L147`).
  - b) One job per thread: `fb-group-comments-fetcher §5.1 L53` "a `replies` job per thread", threshold `FB_GROUP_REPLY_THRESHOLD`, and `§5.1 L40` `post_ref` "for `replies` also the parent `comment_id`"; `tt-video-comments-fetcher §5.1 L47` "a `replies` job for each one" and `§5.1 L41` `post_ref` "the parent comment's key for replies"; `yt-comments-fetcher §5.2 L60` "comment-decay-scheduler sends each candidate to yt-replies-fetcher"; `yt-replies-fetcher §5.1 L38` `post_ref` "(video id and thread id)".
  - c) Per-thread series: `yt-replies-fetcher §5.1 L38` "a reply series opens when yt-comments-fetcher first lists a thread"; `§5.1 L40` per-thread early stop, extension, hot threads and "one job at that step" after an early stop. The target has no per-thread state or rules.
  - d) Instagram owned media: `ig-own-comments-fetcher §5.1 L51` "the job result lists that comment so comment-decay-scheduler can emit a `replies` job for this service", against `comment-decay-scheduler §5.1 L50` "no job".
- **At stake:** the job shape (`thread_ids` list against a single thread in `post_ref`), the number of jobs, and whether `comment_series` needs a row per thread; Instagram owned-media replies would never be fetched.
- **Options:** (1) one job per post with `thread_ids` (`comment-decay-scheduler §5.3 L94`), fetchers loop over threads; (2) one job per thread with the thread in `post_ref`, the scheduler's rule revised; (3) per-thread reply rows in `comment_series` (a replies lane) for YouTube, one-shot jobs elsewhere; separately, ig_own replies: field expansion only, or a `replies` job.
- **Blocks:** F2, F3, C11, VFB3, VTT5, YT5, YT6, IG6

### AU-036

**post_ref in comment, reply and metrics jobs: the scheduler's object against what each fetcher reads**

- **Type:** shape, names
- **Where:**
  - a) Target: `comment-decay-scheduler §6.2 L141` `"post_ref": {"item_id": ..., "platform": "facebook", "platform_id": ...}`; it knows only `items.normalized` fields and `owned_by_client` (`§5.4 L124`). `CONVENTIONS L277` names `post_ref` with no shape.
  - b) `news-comments-fetcher §5.1 L41` `post_ref` = "article item id, canonical URL, `disqus_shortname`, thread identifier or thread id when known, newest stored comment time".
  - c) `fb-group-comments-fetcher §5.1 L40` "the post's platform id and permalink; for `replies` also the parent `comment_id`".
  - d) `tt-video-comments-fetcher §5.1 L41` "`tiktok:video:<id>`, or the parent comment's key for replies"; `tt-video-stats-refresher §5.1 L42` "`tiktok:video:<id>`".
  - e) `yt-replies-fetcher §5.1 L38` "(video id and thread id)" and `§14 Q3 L192` "`post_ref` shape ... align with comment-decay-scheduler"; `ig-own-comments-fetcher §5.1 L41` "`post_ref` = media id"; `li-own-comments-fetcher §5.1 L38` "`post_ref` (the post URN)".
- **At stake:** one contracts type has to deserialise every job; the scheduler never reads `news_sites` (Disqus shortname) or permalinks, so it cannot fill what news and FB-group fetchers expect; a string key and an object do not parse as each other.
- **Options:** (1) the target's object, fetchers look up the rest by `item_id`; (2) the idempotency key string (`<platform>:<kind>:<id>`); (3) a base object plus per-profile extensions defined in contracts (news, fb_group, replies).
- **Blocks:** F2, C11, N8, VFB3, VTT5, VTT6, YT6, IG6, LI2

### AU-037

**Which posts get a series: signals the fetchers expect the scheduler to read, which it never reads**

- **Type:** rule, shape
- **Where:**
  - a) Target: `comment-decay-scheduler §2 L13` "Every post that has a comment route has a series"; `§5.1 L44` profile "Chosen from the post's platform, `owned_by_client` and route"; `§5.2 L74` skip only "if no profile applies or the source is `retired`"; `§5.4 L124` input fields (item_id, source_id, platform, route, vendor, `fetched_at`, `owned_by_client`).
  - b) `comments_count`: `ig-account-media-poller §5.1 L54` series for ig-comments-fetcher "only when `IG_VENDOR_ROUTE` is on and `comments_count` is above zero", and the scheduler "uses `comments_count` to decide how many pages to budget"; `§4 L36`; `ig-hashtag-search §4 L38`; `ig-comments-fetcher §5.1 L41` and `§13 L164` ("a post with `comments_count = 0` gets none").
  - c) Disqus: `news-article-extractor §5.1 L47` series "when the site's `comments_provider` is `disqus`" (the target reads no `news_sites`; its news profile is `comment-decay-scheduler §5.1 L58`).
  - d) Hits and individuals: `li-post-search §5.1 L50` jobs "only for keyword hits and posts of registered sources; posts by individuals get no comment fetch"; `li-post-comments-fetcher §5.1 L40` keyword-matched posts "get one only if the budget allows"; `tt-video-comments-fetcher §5.1 L50` "the videos found by search that comment-decay-scheduler selects (proposed: those with an `item.hits` or `discovery.hits` match, or from a client's priority hashtag)".
  - e) Protests: `x-replies-fetcher §14 Q7 L205` "How posts about protests or rallies are marked so comment-decay-scheduler never opens a series on them".
  - f) Order within a budget: `ig-comments-fetcher §14 Q3 L180` "proposed order by `comments_count`, then source tier; for comment-decay-scheduler to confirm", against `comment-decay-scheduler §5.1 L62` "most overdue first, then by source tier".
- **At stake:** as written the scheduler opens amber series on posts with no comments, on news sites without Disqus, on unconfirmed search results and on individuals' posts, spending vendor money the fetchers assume is never spent; each gate needs a field on `items.normalized` or a table read that no contract defines.
- **Options:** (1) the scheduler reads the signals (`comments_count` and a hit or individual marker on `items.normalized`, `news_sites.comments_provider`) and gates per profile; (2) fetchers complete such jobs as `skipped` without a request and the scheduler ends the series; (3) the producing service marks the item "no series" with one agreed field the scheduler honours.
- **Blocks:** C11, C4, IG2, IG3, VIG2, N6, N8, VLI1, VLI4, VTT5, X6

### AU-038

**Client and flag conditions on amber series: amber acceptance, government clients, spend cap, cancellation**

- **Type:** rule, flag
- **Where:**
  - a) `ig-comments-fetcher §5.1 L41`: a series opens only when "at least one client watching the source has accepted the amber provenance, no client on the source is a government client for this data, and the source's vendor spend is under its cap (qualifier rule 5)"; `§13 L165`.
  - b) `fb-group-comments-fetcher §5.1 L42`: a series "is cancelled if the flag turns off or the last non-government client leaves the group".
  - c) Target: `comment-decay-scheduler §5.1 L44` amber profiles "open only when the platform flag ... is not `off`" (no client condition and no cancellation when the flag turns off); series are cancelled only by `retired` and `deletions` (`§5.1 L42`, `§13 L198`); it reads `sources`, `client_sources`, `budgets`, `comment_series` (`§6.1 L135`), not `clients`.
- **At stake:** the scheduler emits amber jobs for sources watched only by government clients or by clients who did not accept amber provenance, and keeps them going after the flag is switched off; ig-comments-fetcher's acceptance criteria assume no such job exists.
- **Options:** (1) the scheduler reads the clients' government flag, amber acceptance and per-source spend, gates on them and cancels on flag-off or loss of the last eligible client; (2) fetchers re-check at run time and complete `skipped` (ig-comments-fetcher already does), and the scheduler ends the series on `skipped`; (3) registry-writer reflects the change on the source (route or retire) and the scheduler reacts to `source.events` only.
- **Blocks:** C11, F3, VIG2, VFB3

### AU-039

**Client refresh: priority and step label**

- **Type:** budget, enum
- **Where:**
  - a) Target: `comment-decay-scheduler §5.1 L70` a client refresh "creates one `comments` job (`series_step = refresh:<request_id>`), priority tier 1 (client-facing)"; `§13 L196`; `README L179` (decision 2) puts "client refresh" at priority 1.
  - b) `backfill-orchestrator §5.1 L48`: after a client asks, "each backfilled post then gets a refresh through the scheduler, at lowest priority".
  - c) `yt-replies-fetcher §14 Q3 L192` "client-refresh priority (proposed 3)".
  - d) `yt-video-details-fetcher §5.1 L45` labels the refresh step `client`, not `refresh:<request_id>`.
- **At stake:** quota-governor admits by priority; the same client action is priority 1, 3 or 5 depending on the PRD, and the YouTube metrics consumer does not recognise the scheduler's label.
- **Options:** (1) priority 1 for every client refresh (target, README decision 2); (2) priority 1 except refreshes of backfilled posts, which run at backfill priority; (3) priority 3 for client refreshes; and separately one label, `refresh:<request_id>` or `client`.
- **Blocks:** C11, C1, C10, YT4, YT6

### AU-040

**X replies of older posts: the scheduler as emitter of `replies` jobs to x-full-archive-search**

- **Type:** job kind, writers
- **Where:**
  - a) `x-full-archive-search §5.1 L39`: "comment-decay-scheduler, the only emitter of reply jobs, emits `replies` when a client asks for the replies of a post older than 7 days"; `§6.2 L128` hands the result back through `jobs.completed` with `end_time`.
  - b) `x-replies-fetcher §5.1 L45`: "After the window, nothing is automatic; older replies come only through x-full-archive-search on a client request"; `§5.1 L41` "X needs no separate `replies` jobs".
  - c) Target: `comment-decay-scheduler §5.1 L53` X replies "by `conversation_id:`; no job", window ends at 7 d; client refresh exists only "After day 30" as one `comments` job to the comment service (`§5.1 L70`); `§6.2 L138` writes no `jobs.x-full-archive-search`.
- **At stake:** a client request for replies of an X post between day 7 and day 30 has no emitter and no queue, and x-full-archive-search's `replies` kind has no producer.
- **Options:** (1) the scheduler emits `replies` to `jobs.x-full-archive-search` for X posts outside the 7-day window on client request; (2) the client app or x-full-archive-search's own endpoint creates the job (exception to `CONVENTIONS L278`); (3) no X replies beyond 7 days in v1.
- **Blocks:** C11, X5, X6

### AU-041

**Disqus comment series on news sites: +6 h, +24 h, +3 d, or the full decay series**

- **Type:** rule
- **Where:**
  - a) Target: `comment-decay-scheduler §5.1 L58` news (Disqus) "+6 h, +24 h, +3 d"; `CONVENTIONS L269` "News (Disqus sites), green | news-comments-fetcher | +6 h, +24 h, +3 d"; `news-article-extractor §5.1 L47` and `news-comments-fetcher §5.1 L49` ("6 hours after the article is first seen") agree.
  - b) `news-site-resolver §5.1 L41` step (6): "for Disqus sites comments on the decay series (+1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30)".
- **At stake:** the onboarding contract of an approved PRD (`CONVENTIONS L282`) promises clients a series the scheduler will not run; the `news_disqus` budget is sized on one of the two.
- **Options:** (1) +6 h, +24 h, +3 d (target, CONVENTIONS); (2) the general series to day 30 for Disqus sites.
- **Blocks:** C11, N2, N8

### AU-042

**Backfill targets missing from the orchestrator's route table: keyword rules, hashtags, client-authorised TikTok accounts, Instagram mentions**

- **Type:** job kind, writers
- **Where:**
  - a) Target: `backfill-orchestrator §3 L28` names ten backfill services; `§5.3 L79` "Hashtag or keyword rule without a history route; web | none | `done` at once, note `no_history_route`"; `§13 L150` "a Telegram own channel and a hashtag source go to `done` with no job"; `§5.3 L70` Instagram account → ig-account-media-poller only; `§5.3 L71` TikTok creator, amber → tt-profile-videos-poller only; `§2 L15` "exactly one initial backfill job" per source. `CONVENTIONS L53`: when a source is added, the last 90 days are fetched once.
  - b) Keyword rules expecting a `backfill` job: `fb-keyword-search §5.1 L48`; `ig-keyword-search §5.1 L51`; `li-post-search §3 L27`, `§5.1 L48`, `§13 L158`.
  - c) Hashtags: `ig-hashtag-search §5.1 L45` (a job "by backfill-orchestrator when a hashtag is added") and `§5.1 L59`.
  - d) Client-authorised TikTok accounts: `tt-client-videos-fetcher §3 L21`, `§5.1 L49` ("backfill-orchestrator emits a `kind = backfill` job"), `§13 L171`.
  - e) Instagram mentions: `ig-mentions-fetcher §5.1 L49` ("backfill-orchestrator emits one `backfill` job" to this service) and `ig-webhook-receiver §5.1 L45` ("mentions through ig-mentions-fetcher"); the target sends a connected Instagram account to ig-account-media-poller only, one job per source.
  - f) X keyword rules: `x-full-archive-search §5.1 L39` expects `keyword_history` "on a client request (source = the client's `keyword_rule` row)", while the target sends "X account or keyword rule" a `backfill` job on `added` (`backfill-orchestrator §5.3 L72`) and emits no other kind (`backfill-orchestrator §1 L9`); `keyword_history` is not in `CONVENTIONS L277`.
- **At stake:** six services (fb-keyword-search, ig-keyword-search, li-post-search, ig-hashtag-search, tt-client-videos-fetcher, ig-mentions-fetcher) wait for a `backfill` job the orchestrator never emits (it marks the source `done` with `no_history_route`, or sends the only job elsewhere), so these sources start with no history; X keyword history runs on add in one PRD and only on request in the other.
- **Options:** (1) extend the route table to every service named (one job per service, several per Instagram account); (2) keep the table: those sources get `no_history_route` and the services drop their backfill path; (3) search and hashtag services backfill on their first rotation run (ig-hashtag-search's design) and the orchestrator marks them `done`; for X keyword rules, separately, `backfill` on add or `keyword_history` on request.
- **Blocks:** C10, F2, VFB1, VIG1, VLI1, IG2, IG4, IG5, TT1, X5

### AU-043

**Backfill job fields: `cap` and `run_id`, or `window_start`, `window_end` and `reason`; report fields**

- **Type:** shape, names
- **Where:**
  - a) Target: `backfill-orchestrator §6.2 L106` job `{"job_id", "source_id", "kind": "backfill", "due_at", "attempt", "run_id": "initial", "cap": {"max_age_days": 90, "max_items": 600}, "route", "vendor"}`; re-runs use "the same route cap (or a smaller window)" (`§5.1 L50`); who asked (`requested_by`) lives in `backfill_runs` (`§6.3 L112`), not in the job. Completion report `§5.4 L92`: `new_count`, `pages`, `cost_units`, `oldest_item_at`, `capped`, `capped_reason`.
  - b) `fb-backfill §5.1 L41`: the job carries "`window_start = added_at − 90 days`, `window_end = added_at`, `reason = add`"; on-demand jobs "`reason = ops | client`" carry an explicit window.
  - c) `news-sitemap-poller §5.1 L51` reports `coverage_days` and relies on the orchestrator to turn it into `capped` (`§13 L181`); the target's report has `oldest_item_at`, not `coverage_days`.
- **At stake:** fb-backfill (an approved PRD, `CONVENTIONS L282`) reads fields the orchestrator never writes; a window anchored on `added_at` and a cap counted from emission differ whenever a run waits in `pending`; the news coverage figure has no field.
- **Options:** (1) the target's `cap` and `run_id`, with fb-backfill deriving the window and news reporting `oldest_item_at`; (2) the job carries `window_start`, `window_end` and `reason` (cap kept for item limits); (3) both forms, the window only on re-runs.
- **Blocks:** F2, C10, FB3, N4

### AU-044

**News sites: which service backfills, and whether rotation waits for the backfill**

- **Type:** writers, rule
- **Where:**
  - a) Target: `backfill-orchestrator §5.3 L78` "News site | news-feed-poller and news-sitemap-poller (whichever the site has)"; `§3 L28` lists no web-commoncrawl-scanner; `§5.1 L46` "the poller's scheduler, which selects only `done` or `capped` sources, picks the source up".
  - b) `news-feed-poller §5.1 L48`: the orchestrator "schedules the 90-day backfill through news-sitemap-poller or web-commoncrawl-scanner. This scheduler does not wait for the backfill".
  - c) `news-site-resolver §5.1 L41` (5): "through news-sitemap-poller (or web-commoncrawl-scanner where there is no sitemap)".
  - d) `news-sitemap-poller §5.1 L41` selects due sites with no `backfill_status` condition; `§5.1 L49` the orchestrator "sends one `backfill` job in parallel"; `§5.1 L51` if coverage is under 90 days "backfill-orchestrator sets `backfill_status = capped` and asks web-commoncrawl-scanner for the remainder".
- **At stake:** the orchestrator would send news-feed-poller backfill jobs it has no handler for, never asks web-commoncrawl-scanner, and the news pollers rotate `pending` sites the orchestrator assumes are held back.
- **Options:** (1) the target's table and wait-for-`done` rule, news PRDs revised; (2) a news exception: rotation starts at `added`, backfill runs in parallel through news-sitemap-poller, the remainder through web-commoncrawl-scanner as an eleventh target; (3) news sites get `no_history_route` and news-sitemap-poller backfills on its own first pass.
- **Blocks:** C10, N2, N3, N4, W5

### AU-045

**One-off comment jobs for backfilled LinkedIn posts: emitted by backfill-orchestrator, or the scheduler's `once` fetch**

- **Type:** writers, job kind
- **Where:**
  - a) `li-own-comments-fetcher §3 L19` and `§5.1 L52` "For posts of a newly added page (last 30 days) backfill-orchestrator emits one comments job each"; `li-post-comments-fetcher §3 L19`, `§5.1 L54`; `li-notification-receiver §5.1 L48` ("one-off li-own-comments-fetcher jobs").
  - b) Target: `backfill-orchestrator §1 L9` emits only `backfill` jobs; `§3 L29` comment series out of scope; `§5.1 L48` comment-decay-scheduler "opens one `once` fetch for each" backfilled post. `CONVENTIONS L278` "comment, reply and metrics jobs are emitted only by comment-decay-scheduler"; `comment-decay-scheduler §5.1 L66` gives every backfilled post one `once` fetch, with no 30-day limit.
- **At stake:** the LinkedIn fetchers expect an emitter that does not emit comment jobs; the scheduler would fetch comments for all 90 days of backfilled posts where LinkedIn plans for 30.
- **Options:** (1) the scheduler's `once` fetch for every backfilled post (target, CONVENTIONS); (2) the same, limited to posts younger than 30 days on LinkedIn; (3) the orchestrator emits LinkedIn comment jobs (exception to `CONVENTIONS L278`).
- **Blocks:** C10, C11, LI2, LI3, VLI4

### AU-046

**Sequencing: whether the orchestrator waits for a source's tier before it emits**

- **Type:** rule
- **Where:**
  - a) `ig-account-resolver §4 L36` "backfill-orchestrator (waits for a source's tier)"; `§5.1 L52` a client- or ops-added source "is resolved immediately so that its tier is known before backfill-orchestrator schedules the 90-day read"; `§13 L184` criterion 8 "resolved before backfill-orchestrator starts its backfill".
  - b) Target: `backfill-orchestrator §5.1 L42` an `added` message "creates a run"; `§5.1 L44` orders pending runs by tier; `§5.2 L54`-`L58` load the row and emit, with no wait for a tier or a resolver.
- **At stake:** ig-account-resolver's acceptance test cannot pass unless the orchestrator holds runs for sources without a resolved tier, or registry-writer emits `added` only after resolution; neither PRD says so.
- **Options:** (1) the orchestrator holds runs whose source has no followers value or tier until resolved; (2) registry-writer emits `added` only after the resolver's first answer; (3) no wait: a source added without a tier is backfilled in its default tier and the criterion is dropped.
- **Blocks:** C10, C7, IG1

### AU-047

**Re-added retired sources: `added` or `updated`, and a run id the orchestrator would deduplicate**

- **Type:** rule, key
- **Where:**
  - a) `registry-writer §5.2 L52`: for an existing row ("re-add of a retired source ...") "emit `updated` plus `tier_change` instead of `added`", and in the same step "A re-added retired source emits `added` so `backfill-orchestrator` fills the gap".
  - b) Target: `backfill-orchestrator §5.1 L42` runs start on `event = added`; `§5.2 L57` inserts `run_id = initial`; `§5.3 L85` job id from `sha256(source_id | backfill | run_id)`, so a second `initial` run for the same source repeats the first job id, and `§13 L151` "Replaying the same `added` event produces no second job (same `job_id`)"; `§5.3 L81` "no transition leaves `done` or `capped` except a re-run, which does not touch the column". The target never mentions a gap since retirement.
- **At stake:** a re-added retired source either gets no backfill (event `updated`, or the job deduplicated by id) or a second `initial` run that collides in `backfill_runs`; the window to fill is undefined.
- **Options:** (1) `added` on re-add, and the orchestrator opens a run with a new `run_id` covering the time since retirement (capped at 90 days); (2) `updated` plus `tier_change` on re-add and no gap fill; (3) the re-add becomes a system re-run (`requested_by = system`) that leaves `backfill_status` alone.
- **Blocks:** C7, C10, F2

### AU-048

**Author hashing: in normalize-item from the platform id, or at the edge with the result passed through**

- **Type:** rule, names
- **Where:**
  - a) Target: `normalize-item §5.2 L54` "`author_ref = hmac_sha256(AUTHOR_HASH_KEY, platform + ':' + author_platform_id)`"; the mappers hash `username` (`§5.3 L66`), `author.uid` (`§5.3 L67`), member actors (`§5.3 L69`), `authorChannelId` (`§5.3 L71`); key in Vault (`§9 L144`). Nothing says a record that arrives already hashed is accepted.
  - b) `tt-video-comments-fetcher §14 Q4 L184` "Does normalize-item accept a pre-computed `author_hash` and never expect a handle?"; `README L185` (decision 8) "commenter identity is hashed inside the adapter before the first write".
  - c) `ig-comments-fetcher §14 Q2 L179` "Hash at this service (proposed ...) or in normalize-item, and sharing the key so one person keeps one reference across services".
  - d) `tg-discussion-receiver §14 Q4 L201` "confirm with normalize-item and raw-archiver that `author_ref` is accepted as given".
  - e) A second formula for the same people: `poster-resolver §5.2 L59` "`author_hash = sha256(platform || platform_id || salt)` with the salt from Supabase Vault" for individual candidates, against normalize-item's HMAC `author_ref` (a), so an individual's reference in `poster_profiles` never equals the one on their items.
  - f) Edge hashing also departs from `CONVENTIONS L15` ("`raw.items` — every record exactly as a fetch or push returned it"): `li-notification-receiver §14 Q5 L202` and `li-post-comments-fetcher §14 Q5 L196` ask raw-archiver's owners to accept minimised records; raw-archiver stores each message "exactly as produced" (`raw-archiver §2 L13`) and never parses payloads (`§8 L137`), so the question is the CONVENTIONS rule, not the archiver.
  - g) Name in ClickHouse: `x-compliance-sync §5.2 L52` "mentions keep only `author_hash` in ClickHouse" and `deletion-propagator §5.3 L62` empties `author_hash`, while store-writer's row carries `author_ref` (`store-writer §6.2 L110`).
- **At stake:** with edge hashing normalize-item has no platform id to hash and must pass a value through; a different key or formula gives one person two references (author dedup, deletion by author and the never-profile rule depend on one reference); the field is `author_hash` in one PRD and `author_ref` in the others.
- **Options:** (1) normalize-item hashes everything (target as written) and edge services send ids in clear; (2) edge services hash with the same Vault key and formula through listening-sdk, and normalize-item passes `author_ref` through when present; (3) edge hashing only on the routes README decision 8 and these PRDs name, normalize-item for the rest.
- **Blocks:** F2, F4, C4, C2, VTT5, VIG2, TG2

### AU-049

**Facebook PPCA comment edits: a new version of the old item, or a new item**

- **Type:** key, rule
- **Where:**
  - a) `fb-post-comments-fetcher §5.2 L68`: "the new message carries `edit_of` (the old idempotency key) and normalize-item stores it as a new version".
  - b) Target: `normalize-item §5.3 L63` PPCA key "`facebook:comment:<post_id>:<sha256(created_time + text)>`"; `§5.2 L51` `item_id = uuid_v5(ns_items, idempotency_key)`; a version is made only for a key "known with a different hash" (`§5.2 L52`); `edit_of` appears nowhere; `§13 L165`.
- **At stake:** an edited PPCA comment has new text, so a new key and a new `item_id`; normalize-item publishes it as a second comment, the old one stays, counts double and the edit link is lost.
- **Options:** (1) normalize-item honours `edit_of` and publishes under the old key's `item_id` with `version + 1`; (2) a new item, and the fetcher emits a `deletions` message for the old key; (3) PPCA edits are not tracked (accepted loss) and the fetcher drops `edit_of`.
- **Blocks:** C4, FB5, F2

### AU-050

**X replies: `x:comment:<id>` or `x:post:<id>`**

- **Type:** key
- **Where:**
  - a) `x-replies-fetcher §6.2 L115` `"idempotency_key": "x:comment:1975210483926617088"`; `§9 L162` "Idempotency: `x:comment:<id>` plus `content_hash`"; `§14 Q5 L203` "normalize-item must decide how it links to `x:comment:<id>`".
  - b) Target: `normalize-item §5.3 L68` X v2 for all five X services, x-replies-fetcher included: "`x:post:<id>`", with "`referenced_tweets` decides `reply`, `quote` or `post`"; normalize-item computes the key itself (`§5.2 L51`).
- **At stake:** a reply fetched by x-replies-fetcher and the same reply found by x-recent-search are one item under the target's key and two under the fetcher's; deletion-propagator and x-compliance-sync must derive the same `item_id` for X deletions.
- **Options:** (1) `x:post:<id>` for every X item, kind from `referenced_tweets` (target); (2) `x:comment:<id>` for replies fetched as replies, linked to any `x:post:<id>` copy; (3) one key, with the reply relation carried only in `parent_id`/`root_id`.
- **Blocks:** C4, X1, X4, X6, X7, C13

### AU-051

**YouTube partial records: a hold in normalize-item that it does not have, and the video key and kind**

- **Type:** rule, key, shape
- **Where:**
  - a) `yt-pubsub-receiver §6.2 L124` "`partial: true` makes normalize-item wait for details: it holds the record until yt-video-details-fetcher's full record under the same key arrives"; `yt-video-details-fetcher §1 L9` ("a partial record that normalize-item never releases"), `§4 L33`, `§12 L196`; `yt-keyword-search §6.2 L123` "`partial: true` tells normalize-item that statistics follow".
  - b) Target: no `partial` field and no hold or release anywhere; outcomes are publish, metrics-only, version or park (`normalize-item §5.2 L52`, `normalize-item §10 L148`); the YouTube mapper names only yt-video-details-fetcher, yt-comments-fetcher and yt-replies-fetcher (`normalize-item §5.3 L71`), so records from `yt-pubsub-receiver §6.2 L102`, `yt-uploads-reconciler §6.2 L108` and `yt-keyword-search §6.2 L96` match no mapper (`normalize-item §5.2 L50`).
  - c) Key: target `normalize-item §5.3 L71` "`youtube:video:<id>`" (`yt-keyword-search §5.1 L48` agrees); `yt-uploads-reconciler §9 L163` "`youtube:post:<video id>`, shared by partial and full records, which normalize-item upserts into one item". The target does not say which `kind` a video carries; its key segment is `video`, and comment-decay-scheduler opens a series only on `kind = post` (`comment-decay-scheduler §5.1 L42`).
- **At stake:** every YouTube video is either published twice (partial, then full, possibly under two keys) or parked as `schema_unknown`; if the published `kind` is not `post`, no YouTube comment or metrics series opens; yt-video-details-fetcher's whole design rests on the hold.
- **Options:** (1) normalize-item holds `partial: true` records until the full record under the same key arrives (with a timeout); (2) partial published as version 1, full record as version 2; (3) partial producers stop writing `raw.items` and only yt-video-details-fetcher writes the record; separately, one key (`youtube:video:<id>` or `youtube:post:<id>`) and `kind = post` for videos.
- **Blocks:** F2, C4, C11, YT2, YT3, YT4, YT8

### AU-052

**`raw.items` producers with no mapper in normalize-item; web results attributed to search-hit-router**

- **Type:** writers, rule
- **Where:**
  - a) Target: `normalize-item §5.2 L50` "Select the mapper by `(service, api_version)`; no match or a missing required field raises `schema_unknown`, parks the batch key in `review_queue` and skips the batch"; mapper list `§5.3 L62`-`L73`; web results "forwarded by search-hit-router" (`§3 L22`, `§5.3 L73`).
  - b) Producers that write `raw.items`, assume normalize-item maps or deduplicates them, and are not in the list: `ig-keyword-search §6.2 L96` (the Instagram line `normalize-item §5.3 L66` names six other IG services); `li-notification-receiver §6.2 L112` and `§8 L151`; `li-org-resolver §6.2 L79`, `§5.2 L57`, `§13 L159` ("deduplicated by normalize-item"); `news-comments-fetcher §6.2 L92` and `§8 L141`; `web-search-perplexity §6.2 L89`, `web-search-mojeek §6.2 L88`, `web-gdelt-poller §6.2 L91`, with `web-search-perplexity §14 Q5 L174` asking whether `kind_hint = search_response` is "archive-only"; the three YouTube producers of AU-051.
  - c) search-hit-router's PRD never mentions `raw.items`.
  - d) Mapper selection: `tg-channel-posts-poller §8 L149` "The envelope's `vendor` tells normalize-item which mapper applies", against the target's `(service, api_version)`.
- **At stake:** every batch from these producers parks as `schema_unknown`: Disqus comments, LinkedIn live comments, the 20 sampled LinkedIn posts and Instagram keyword results never reach `items.normalized`; web search responses park forever unless there is an explicit archive-only outcome.
- **Options:** (1) add a mapper for each producer named and an explicit archive-only outcome for `kind_hint = search_response`; (2) restrict `raw.items` writers to the mapper list (web results only through search-hit-router, as the target says); (3) select mappers by payload family (platform, vendor, kind) rather than by service.
- **Blocks:** F2, C4, VIG1, LI3, VLI2, N8, W1, W2, W3, W4, VTG3

### AU-053

**Instagram cross-route duplicates: vendor media ids against Graph ids**

- **Type:** key
- **Where:**
  - a) `ig-keyword-search §14 Q2 L182`: "vendor media ids may differ from Graph ids. Proposed: normalize-item also joins on the shortcode in `permalink`; to be confirmed with its owner".
  - b) Target: dedup is by key only (`normalize-item §5.2 L51`-`L52`, `item_id = uuid_v5(ns_items, idempotency_key)`); the Instagram key is "`instagram:post:<media id>`" (`§5.3 L66`); no shortcode or permalink join.
- **At stake:** the same Instagram post found by the amber keyword route and by a green route becomes two items, double-counting mentions.
- **Options:** (1) key Instagram posts by shortcode on every route; (2) a secondary dedup join on the permalink shortcode in normalize-item; (3) accept duplicates across routes and dedup in aggregation.
- **Blocks:** C4, VIG1, IG2, IG3, IG5

### AU-054

**Hashtag-source videos as hits "without text matching"**

- **Type:** rule
- **Where:**
  - a) `tt-hashtag-feed-poller §4 L34`: "a video from a hashtag source counts as a hit for the hashtag's clients without text matching, split into `item.hits` or `discovery.hits`"; `§14 Q4 L171` "this PRD assumes yes".
  - b) Target: `keyword-matcher §2 L15` every item is "matched ... against the active keyword set"; `§5.2 L49` "Scan `text_norm` with each candidate client's automaton"; `§5.3 L65` a hit exists only when a form matches ("one hit per (item, client, keyword)"); hashtags are matched as forms with `kind: hashtag` (`§5.3 L56`). No rule makes a hit from the source alone.
- **At stake:** a hashtag-feed video whose caption lacks the tag (or spells it differently) produces no hit, so the feed's clients see fewer mentions than the poller promises; a hit by construction would also need a `keyword_id`, which no PRD assigns.
- **Options:** (1) text match always (target as written); (2) hits by construction for the clients in the hashtag source's `client_ids`, with the hashtag's keyword row as `keyword_id`; (3) by construction for a client's priority hashtags only, text match for the rest.
- **Blocks:** C5, VTT2

### AU-055

**News keyword matching on the 200 to 300 character excerpt, or on the 7-day full text**

- **Type:** rule
- **Where:**
  - a) `news-article-extractor §4 L35`: "keyword-matcher and the analysis services (may read the cache within its 7 days)"; `§14 Q1 L187` "Proposed: yes, otherwise a brand named after the first 300 characters is missed; to be confirmed with counsel".
  - b) Target: `keyword-matcher §5.4 L85` "It does not get ... full article text"; it scans `text_norm` only (`§5.2 L49`); `normalize-item §5.3 L72` news `text` is "an excerpt of 200 to 300 characters" with `text_full_ref` to the cache.
  - c) The analysis services, which news-article-extractor's proposal also covers: `analysis-sentiment §5.1 L51` models read "never the 7-day news cache, so a re-run reproduces live analysis" and `§5.4 L80` "Not ... article text beyond the excerpt"; analysis-topics and analysis-entities read `title` and `text` only (`analysis-topics §5.4 L84`, `analysis-entities §5.4 L81`).
- **At stake:** a brand named after the first 300 characters of an article is never a hit, so news recall is bounded by the excerpt.
- **Options:** (1) excerpt only (target as written); (2) keyword-matcher reads `text_full_ref` within 7 days and persists only offsets and terms, subject to counsel.
- **Blocks:** C5, N6, A1, A2, A3

### AU-056

**Resolve job fields and outcomes: `client_ids`, priority, `url_or_handle`, and `skipped_flag_off` against `unresolvable: route_off`**

- **Type:** shape, enum, job kind
- **Where:**
  - a) Target: `poster-resolver §5.3 L67` job `{"job_id","kind":"resolve","candidate_key","platform","platform_id","handle","hit_url","origin","reply_to","attempt","sample_posts"}`; amber resolvers are not called while the flag is `off` and "the candidate is marked `unresolvable: route_off`" (`§5.2 L56`, `§13 L144`); answers are `resolved` or `unresolvable` (`poster-resolver §5.3 L70`).
  - b) `ig-account-resolver §5.1 L42` the job carries "the `client_ids` whose hit produced the candidate"; `tt-user-resolver §5.1 L41` "the `client_ids` whose hits produced it, `attempt` and a priority"; `li-org-resolver §5.1 L44` `{candidate_key, url_or_handle, origin, client_ids, seed_list, kind, attempt}`.
  - c) `tt-user-resolver §5.2 L53` "Flag off: ... return the job as `skipped_flag_off`; poster-resolver keeps the candidate waiting", while the target sends no job when the flag is off and closes the candidate.
- **At stake:** resolvers that gate on clients (government, amber acceptance) or order work by priority receive neither field; a TikTok candidate is closed on one side and parked on the other.
- **Options:** (1) the target's job as written, resolvers look up client context themselves; (2) add `client_ids`, a priority and `seed_list` to the resolve job; (3) a common core plus per-resolver extensions; and separately for flag-off: close as `route_off`, or keep waiting.
- **Blocks:** F2, C8, IG1, VTT3, VLI2

### AU-057

**Client-added candidates through `discovery.hits`: `origin = client_onboarding`, `proposed_source_id`, Telegram groups**

- **Type:** enum, shape, rule
- **Where:**
  - a) `tg-bot-channel-receiver §5.2 L70` emits on `discovery.hits` "(type `channel`, `origin = client_onboarding`, `proposed_source_id`, `owned_by_client`, client id). poster-resolver and the qualifier treat it as always qualifying".
  - b) `tg-discussion-receiver §5.2 L67` registry-writer creates the group row (`source_type = group`) "from a `discovery.hits` candidate with a pre-allocated `proposed_source_id`".
  - c) `li-org-resolver §5.1 L44` takes client-onboarding candidates from registry-writer directly (origin `seed`), not through poster-resolver.
  - d) Target: origins are `discovery` (`poster-resolver §5.3 L67`) and `manual` through registry-writer (`§3 L27`, `§5.1 L46`); no `client_onboarding`, no `proposed_source_id`, no always-qualify path; rule 1 (`§5.2 L57`) says "Telegram channel ... always qualify; everything else is an individual", with no Telegram group; the rejection memory applies unless the hit is "from a client seed list or watchlist" (`§5.2 L54`).
  - e) `qualifier §3 L27`: for manual candidates "rules 2, 4 and 10 are skipped because the choice is explicit; rules 1, 5, 6 and 7 still apply"; the qualifier has no `client_onboarding` origin and no always-qualify path (rule 5 can still queue the source).
  - f) `registry-writer §5.2 L61`: the manual add publishes a `manual_candidate` "to `jobs.poster-resolver` with `origin: manual`"; it sends no `seed` job to li-org-resolver (c).
  - g) `registry-writer §5.3 L68`-`L69` inserts `source_id` as `gen_random_uuid()`; no pre-allocated id is accepted, which `tg-bot-channel-receiver §14 Q4 L197` asks for ("accepted by registry-writer with a pre-allocated `source_id` (`proposed_source_id`)").
- **At stake:** a client's own Telegram channel or discussion group can be typed as an individual, answered from rejection memory or sent through a paid vendor lookup, and the pre-allocated `source_id` has no field to travel in.
- **Options:** (1) client-added sources bypass discovery and reach registry-writer directly (seed or manual path); (2) poster-resolver accepts `origin = client_onboarding`, carries `proposed_source_id` and `owned_by_client` into the profile, and types groups as qualifying; (3) every client addition uses poster-resolver's `manual` origin through registry-writer.
- **Blocks:** C7, C8, C9, TG1, TG2, VLI2

### AU-058

**Dormant sources that post again: promoted by the qualifier's daily sweep, or by the poller through `source.events`**

- **Type:** writers, rule
- **Where:**
  - a) Target: `qualifier §5.1 L46` a daily sweep at 03:00 Baghdad time "promotes dormant sources that posted again"; `§13 L146` criterion 8.
  - b) `x-user-timeline-poller §5.1 L40` "a new post promotes the account back to its reach tier through `source.events` (`tier change`)". `CONVENTIONS L49` "a new post promotes the source back to its reach tier" names no owner.
- **At stake:** two writers of the same tier change (the poller writes `source.events` directly, registry-writer applies the qualifier's decisions); with the sweep alone, a dormant source that posts waits up to a day at weekly cadence.
- **Options:** (1) the sweep only (target); (2) the poller asks for promotion at the first new post through a decision that registry-writer applies; (3) both, deduplicated by decision id.
- **Blocks:** C9, C7, X3

### AU-059

**Work assumed to flow from or to the qualifier: `refresh` jobs to resolvers, unreadable-channel reports**

- **Type:** job kind, writers
- **Where:**
  - a) `li-org-resolver §5.1 L44`: jobs arrive "from qualifier (`kind: refresh`) when a dormant source gets a new hit, when a source reaches its 90-day decay review, or when a source retires at 180 days".
  - b) `tg-channel-posts-poller §8 L148`: repeated unreadable channels "are reported to ops and the qualifier".
  - c) Target: the qualifier writes only `registry.decisions`, `decisions`, `review_queue` and the n8n webhook (`qualifier §6.2 L81`-`L87`); rule 9 decides `tier_down` and `retire` in the sweep from `last_hit_at`, `client_sources` and ClickHouse `items` (`§5.2 L60`, `§5.3 L67`) with no resolver call; its triggers are profiles, review callbacks and the sweep (`§5.1 L46`).
- **At stake:** li-org-resolver's refresh path has no producer, so LinkedIn pages are decayed or retired on hit data alone; the unreadable-channel report has no channel to travel on.
- **Options:** (1) the qualifier emits `refresh` jobs (directly or through poster-resolver) before decay decisions; (2) resolvers refresh on their own schedule (as ig-account-resolver does) and the qualifier decides from data; (3) no refresh before decay, and unreadable channels reach ops through alerts only.
- **Blocks:** C9, VLI2, VTG3

### AU-060

**Instagram hashtags beyond the 30-tag cap: queued under rule 5, or registered on the amber route**

- **Type:** rule, writers
- **Where:**
  - a) `ig-hashtag-search §3 L30` "Deciding which hashtags a client gets when they ask for more than 30 (qualifier rule 5 and the client success team ...)"; `§12 L168` "excess tags queue by tier (qualifier rule 5)".
  - b) `ig-keyword-search §3 L20` "Hashtag mode for hashtags beyond the 30-tag cap (registry `route = amber`)"; `§13 L169` "A client's 31st hashtag (registry `route = amber`) is searched here".
  - c) Target: rule 5 (`qualifier §5.2 L56`) checks "PPCA Pages per client token, YouTube quota share, vendor monthly spend per source"; over the cap the candidate is `queued` and "not written to `sources`"; no Instagram hashtag cap and no rule that moves a capped green source to an amber route; amber is never assigned when only a government client is interested (`§9 L117`).
- **At stake:** a client's 31st hashtag is either not watched at all or watched through a paid vendor with amber provenance; the qualifier has no rule for either.
- **Options:** (1) queued, with the Instagram hashtag cap added to rule 5's capacity check; (2) registered as amber when `IG_VENDOR_ROUTE` is on and no government client is involved; (3) the client chooses per hashtag.
- **Blocks:** C9, C1, IG2, VIG1

### AU-061

**Group candidates from hits inside unwatched Facebook groups: no service emits them**

- **Type:** rule, writers
- **Where:**
  - a) `fb-keyword-search §1 L9` "how a hit inside a group adds that group as a source (qualifier rule 8)"; `§6.2 L120` "(rule 8: the group is a source, the poster is qualified separately)"; `fb-group-posts-poller §6.2 L124` (the poster is a candidate "separately from the group").
  - b) Target: rule 8 (`qualifier §5.2 L59`) acts on a profile with `account_type = group`; keyword-matcher builds a candidate from the item's author only (`keyword-matcher §5.3 L74`); poster-resolver builds `candidate_key` from the hit (`poster-resolver §5.2 L52`). No PRD emits the group itself as a candidate.
- **At stake:** a hit in an unwatched group never adds the group, so fb-keyword-search's discovery of groups does not happen.
- **Options:** (1) keyword-matcher emits a second candidate for the container (the group) of a group post; (2) fb-keyword-search emits group candidates on `discovery.hits` itself (a change to its "writes neither" line and to `CONVENTIONS L281`); (3) groups are added only by clients or ops.
- **Blocks:** C5, C8, C9, VFB1, VFB2

### AU-062

**Keyword-rule and hashtag sources: no registry-writer path creates them, and no seed job is emitted on a keyword change**

- **Type:** writers, job kind
- **Where:**
  - a) `web-search-perplexity §5.1 L41` "Each active `keywords` row has one `sources` row (`platform = web`, `source_type = keyword_rule`) created by registry-writer"; `web-search-mojeek §5.1 L42` (same); `web-gdelt-poller §5.1 L41` and `§11 L150` ("registry-writer (keyword-rule rows)"); `fb-keyword-search §3 L28` "Creating keyword rules (client set-up and registry-writer)"; `ig-hashtag-search §11 L163` "registry-writer (hashtag sources and tiers)". `CONVENTIONS L281`: a search service writes items with "`source_id` = the keyword-rule or hashtag source that produced the query".
  - b) `fb-page-search §5.1 L40`: "a control-plane change to `keywords` (`created` or `variants changed`) for a client with Facebook in scope, emitted by registry-writer, `reason = seed`".
  - c) Target: registry-writer applies `registry.decisions` (`registry-writer §3 L22`) from the qualifier, the canary, ops, client admins and retention-purger (`§4 L36`); it reads `sources`, `client_sources`, `clients`, `registry_audit` (`§6.1 L88`), not `keywords`; its manual add takes `{platform, url_or_handle, ...}` and resolves through poster-resolver and the qualifier (`§5.2 L61`); it writes `sources`, `client_sources`, `registry_audit` and `source.events` only (`§6.2 L91`-`L92`), no jobs.
- **At stake:** the search services rotate over `sources` rows that nobody creates, and fb-page-search's seed job has no emitter; a keyword rule pushed through the manual add would be sent to poster-resolver and the qualifier, which only judge posters.
- **Options:** (1) registry-writer watches `keywords` and keeps one keyword-rule source per active rule (and emits the seed signal); (2) the keyword editor writes keyword-rule sources through a new decision type registry-writer applies; (3) search services rotate on `keywords` directly with no `sources` row.
- **Blocks:** C7, F3, W1, W2, W4, VFB1, FB6, IG2

### AU-063

**Requests to registry-writer from receivers and pollers: promotion to push, return to reach tier, `next_poll_at`, retirement**

- **Type:** writers, rule
- **Where:**
  - a) `yt-pubsub-receiver §6.2 L130` "requests to registry-writer (push, promotion, `next_poll_at`, `health`)"; `§5.1 L42` "registry-writer sets the channel's `next_poll_at` to now"; `§5.1 L40` the first new-video notification "asks registry-writer to promote the channel back to push".
  - b) `fb-client-webhook-receiver §5.1 L42` the first new-post event "asks registry-writer to promote the Page back to push"; `§5.2 L59` "ask registry-writer to return the Page to its reach tier".
  - c) `yt-uploads-reconciler §8 L154` "a vanished channel is retired through registry-writer".
  - d) Target: decision producers are the qualifier, source-health-canary, ops, client admins and retention-purger (`registry-writer §4 L36`); `next_poll_at` is an operational column "written by their owners" (`§3 L30`); per-source `health` changes only through the canary's route-level `health_change` (`§5.2 L54`); no request message or endpoint exists for other services beyond the manual add (`§5.2 L61`).
- **At stake:** promotions, lease-lapse catch-up and retirements asked for by these services have no message type and no accepted producer, so they do not happen, or the services write `sources` directly.
- **Options:** (1) registry-writer accepts decisions (`promote`, `tier_change`, `retire`, `update`) from these services; `next_poll_at` stays with the poller; (2) such requests go to the qualifier, which emits the decision; (3) services update operational columns through the SDK and send only identity changes to registry-writer.
- **Blocks:** C7, C9, YT2, YT3, FB7

### AU-064

**`health_change` and the government exclusion: registry-writer's bulk update has no `scope`**

- **Type:** rule, shape
- **Where:**
  - a) `README L182` (decision 5): "A green source watched by a government client is never moved to an amber fallback (`scope = non_government`)".
  - b) `source-health-canary §14 Q2 L162` "Who enforces the government exclusion: the decision's `scope` read by registry-writer (proposed) or the canary listing sources one by one?"
  - c) Target: `health_change` "carries `platform`, `route`, `vendor`, `health`, `fallback`" and bulk-updates "every source on that route and vendor" (`registry-writer §5.2 L54`); the statement is "`UPDATE ... WHERE route = $1 AND vendor = $2 AND platform = $3`" (`§7 L107`); no `scope` is read.
- **At stake:** a fallback flips government-watched green sources to `fallback` along with the rest, against README decision 5.
- **Options:** (1) registry-writer reads `scope` and excludes sources whose `client_ids` include a government client; (2) the canary sends one decision per eligible source; (3) the fallback is recorded per route only and each fetcher applies the government exclusion at run time.
- **Blocks:** C7, C12

### AU-065

**Per-source vendor spend caps, per-service sub-counters and page caps: quota-governor keeps none of them (except per-service on `tt_vendor`)**

- **Type:** budget, shape
- **Where:**
  - a) Target: `quota-governor §5.3 L82` "`fb_vendor`, `ig_vendor`, `tt_vendor`, `li_vendor_<action>`, `tg_*` | monthly spend per tag (`tt_vendor` with per-service sub-counters)"; `CONVENTIONS L279` gives per-service sub-counters to `tt_vendor` only; the response is `{decision, wait_until, remaining}` plus `charge` and `reservation_id` (`§5.1 L37`); the `budgets` row is keyed by `budget_tag` and `sub_counter` (`§6.2 L104`).
  - b) Per-source spend: `qualifier §5.2 L56` rule 5 checks "vendor monthly spend per source"; `ig-comments-fetcher §5.1 L41` "the source's vendor spend is under its cap (qualifier rule 5)"; `ig-keyword-search §6.3 L121` "a monthly spend counter per source"; `tt-hashtag-feed-poller §7 L118` and `tt-keyword-search §7 L112` "the per-source vendor spend cap applies".
  - c) Per-service sub-counters on `ig_vendor`: `ig-comments-fetcher §6.3 L119` "with a counter per service"; `ig-keyword-search §6.3 L121` "a sub-counter per service".
  - d) Page cap: `tt-hashtag-feed-poller §5.1 L50` "a per-run page cap from quota-governor"; the response carries no such field.
- **At stake:** rule 5's per-source cap and the amber services' cap checks have no counter to read; the governor's capacity answer to the qualifier cannot be computed; the page cap has nowhere to come from.
- **Options:** (1) per-source and per-service sub-counters on every amber tag, read by the capacity query; (2) per-source spend computed from cost reports outside the governor (for example in `service_runs`), the governor keeping tag-level counters only; (3) no per-source caps: tag-level monthly caps only, and the page cap set by each service's own configuration.
- **Blocks:** C1, C9, F3, F5, VIG1, VIG2, VTT1, VTT2

### AU-066

**Provider-side failures: does quota-governor deny or exhaust a tag on 401/403, out-of-credits or YouTube `quotaExceeded`**

- **Type:** rule, budget
- **Where:**
  - a) `ig-comments-fetcher §8 L131` and `ig-keyword-search §8 L134`: on 401, 403 or out-of-credits "the route is marked `degraded`, the batch stops, quota-governor denies `ig_vendor`".
  - b) `yt-keyword-search §8 L139`: on `quotaExceeded` "report to quota-governor (which marks the YouTube budget exhausted for every service)".
  - c) Target: `decide()` denies only for an unknown or disabled tag or a flag `off` (`flag_off`), a full period (`period_full`) and the priority gate (`priority_gate`) (`quota-governor §5.3 L67`-`L72`); `exhausted` means 100% of its own counter (`§5.1 L49`); a provider throttle becomes `wait_until` only for Meta (`§5.3 L80`); reports carry units, usage headers and billing (`§5.1 L37`), not errors.
- **At stake:** after a credential or credit failure other services keep getting `allow` for the same tag; after `quotaExceeded` the counters still show units left, so the other YouTube services keep calling into a refused quota.
- **Options:** (1) the report carries a provider error class and the governor sets the tag to `exhausted` (credits, quota) or denies it until cleared (401/403); (2) the governor stays counter-only and the route's `health` (source-health-canary) stops callers; (3) both: health for 401/403, `exhausted` for credits and quota.
- **Blocks:** C1, C12, F5, VIG1, VIG2, YT8

### AU-067

**Priorities and the 80% rules: first sight, metrics order, and X's cascade against the governor's table**

- **Type:** budget, rule
- **Where:**
  - a) Target: priorities are "derived from job kind and tier by an SDK helper; a caller cannot claim more than its kind allows" (`quota-governor §5.1 L39`), "validated server-side" (`§12 L149`): 1 Tier 1 rotation, client refresh, `ops_force`, canaries; 2 Tier 2, client keyword searches, comment steps up to +24 h, metrics at +24 h; 3 Tier 3, later comment steps, replies, metrics at +7 d; 4 hot extras, resolvers, discovery; 5 backfill (`§5.1 L43`-`L47`; `README L179`, decision 2). `stretch` admits priorities 1 to 3, from 95% only 1 and 2 (`§5.1 L49`); `stretch_factor` applies to amber tags only (`§5.1 L51`); whether metered green routes stretch is open (`§14 Q2 L171`); the Meta bucket gates only priorities 4 and 5 above 80% (`§5.3 L80`).
  - b) `yt-video-details-fetcher §5.1 L50` and `§14 Q1 L215`: first sight from Tier 2, Tier 3, push and keyword-rule sources at priority 1 ("confirm in the quota-governor PRD"); the target names no first-sight priority and derives it from tier.
  - c) `fb-reactions-fetcher §7 L134` "quota-governor orders rotation polls first, comment series second, metrics refreshes third" and `§12 L167` "+7 d refreshes are dropped before +24 h ones"; the target puts +24 h metrics level with Tier 2 rotation and early comment steps, and on the Meta tag gates only 4 and 5.
  - d) `x-recent-search §7 L143`: at 80% of the X cap the governor "cuts x-full-archive-search jobs first, then stretches tier-2 and tier-3 searches to daily, then drops reply steps after +24 h"; the target does not stretch the green X tag and admits priority 3 (later reply steps) until 95%.
  - e) Daily keyword rules at 80%: `li-post-search §5.1 L46` "quota-governor cannot stretch below daily, so it answers wait-until or deny and the rule stays due"; `tg-message-search §5.1 L46` "answers wait-until for the sets lowest on client priority lists"; the target admits client keyword searches (priority 2) until 95% and has no ordering by client priority list.
- **At stake:** the SDK helper computes priorities from the table, so these PRDs' orderings (and their tests) do not hold: YouTube first sight runs at 2 or 3, Facebook metrics compete with rotation, X searches are never stretched.
- **Options:** (1) the target's table everywhere, with the PRDs revised; (2) add explicit rows (first sight at 1; X cascade; Meta metrics order) to the table; (3) per-tag priority profiles configured in `budgets`.
- **Blocks:** C1, F5, YT4, FB4, X1, X5, X6, VLI1, VTG1

### AU-068

**Budget tag, bucket, ledger and alert names that the governor does not have**

- **Type:** budget, names
- **Where:**
  - a) Tag: `ig-hashtag-search §7 L136` "quota-governor meters calls under `ig_graph_<client_id>`", against `quota-governor §5.3 L83` and `CONVENTIONS L279` `ig_graph_<ig_user_id>`.
  - b) YouTube buckets: `yt-keyword-search §5.1 L51` "the governor's backfill allowance (set in `budgets`)"; `yt-text-purger §7 L187` refresh "bucket share is set in quota-governor"; the target's buckets are `search`, `ingest`, `comments`, `reserve` (`quota-governor §5.3 L79`, also `CONVENTIONS L279`).
  - c) Alert: `tt-hashtag-feed-poller §10 L139` and `tt-keyword-search §10 L131` "`budget_80pct` from quota-governor"; the governor's alert is `budget_80` (`quota-governor §10 L139`).
  - d) Hashtag ledger: `ig-hashtag-search §5.1 L57` "The governor keeps, in `budgets`, the ledger ... a hashtag that would be the 31st is denied"; the target keeps it in the proposed table `ig_hashtag_ledger` (`quota-governor §6.3 L107`, `README L186`) and the 31st "waits until the oldest leaves the window" (`quota-governor §5.3 L81`).
- **At stake:** budget requests under a tag the governor does not know are denied (`flag_off` for an unknown tag, `quota-governor §5.3 L67`); YouTube backfill and text refresh have no bucket to draw from; alert routing keys do not match.
- **Options:** (1) the target's names (`ig_graph_<ig_user_id>`, four YouTube buckets, `budget_80`, `ig_hashtag_ledger`), PRDs revised; (2) add `backfill` and `refresh` buckets to `youtube_data_api`; (3) charge YouTube backfill to `ingest` and refresh to `comments`, keeping four buckets.
- **Blocks:** C1, F3, F5, IG2, YT7, YT8, VTT1, VTT2

### AU-069

**Push routes: receivers expect the canary to flip health on missing heartbeats, which it excludes**

- **Type:** rule, writers
- **Where:**
  - a) `tg-bot-channel-receiver §8 L152` a canary channel's hourly timestamp post: "a missing heartbeat above 5% in 15 minutes flips `health = degraded`", with source-health-canary as the dependency (`§11 L169`); `tg-discussion-receiver §8 L156` (hourly test comment, same rule); `ig-webhook-receiver §8 L144` an account flagged `push_gap`: "source-health-canary may flip `health = degraded` for it"; `yt-pubsub-receiver §8 L146` "source-health-canary sees renewals fail or notifications stop across channels".
  - b) Target: `source-health-canary §3 L30` out of scope: "Heartbeats of push receivers (each receiver reports its own; a later version may read them)"; it runs active reads through each route's adapter (`§5.1 L43`-`L45`, `§5.2 L54`).
- **At stake:** no service flips health for the Telegram bot, Instagram webhook and PubSubHubbub routes, so a silent push route stays `ok` and the receivers' failure handling never triggers.
- **Options:** (1) the canary reads receivers' heartbeat counters in v1 and flips push routes; (2) each receiver sends its own `health_change` decision; (3) push silence only alerts ops and health is untouched.
- **Blocks:** C12, TG1, TG2, IG4, YT2

### AU-070

**Per-source health flips attributed to the canary, which works per route**

- **Type:** rule, shape
- **Where:**
  - a) News: `news-site-resolver §5.1 L40` a site is refreshed "at once when source-health-canary flips it to `degraded`" (`§12 L152`); `news-feed-poller §12 L156` "source-health-canary compares expected and observed publishing rate".
  - b) `x-compliance-sync §5.3 L83` "The SDK canary hook asks source-health-canary to set `health = blocked`" for one registered X source and back to `ok`; `§4 L36`.
  - c) `web-commoncrawl-scanner §8 L122` an implausible scan: "source-health-canary is told so it can flip `health = degraded`"; `x-filtered-stream §12 L185` "source-health-canary checks canary accounts' posts and raises `stream_silent`, forcing a reconnect"; `ig-webhook-receiver §8 L144` (one account).
  - d) Target: health is per route (platform, route class, vendor) (`source-health-canary §2 L15`, `§5.3 L66`); its decision is a route-level `health_change` (`§6.2 L102`) that registry-writer applies to every source on the route (`registry-writer §5.2 L54`); inputs are its canary fetches, the SDK's per-call route counters and `source.events` (`source-health-canary §6.1 L96`), with no per-source request; it compares items with `expect_min_items` per target, not publishing rates (`source-health-canary §5.3 L64`); its alerts (`source-health-canary §10 L132`) have no `stream_silent`.
- **At stake:** one site, account or scan cannot be flagged as the PRDs describe, and a per-source `blocked` from X compliance sent as `health_change` would block the whole X route.
- **Options:** (1) the canary accepts per-source health requests (a decision with `source_id`); (2) these services ask registry-writer for per-source health themselves (see AU-063); (3) per-source problems stay in each service's state and alerts; health stays route-level.
- **Blocks:** C12, C7, N2, N3, IG4, X4, X7, W5

### AU-071

**Instagram hashtag fallback to ig-keyword-search is not among the canary's alternates**

- **Type:** flag, rule
- **Where:**
  - a) `ig-hashtag-search §8 L144` "if `IG_VENDOR_ROUTE` is set to a vendor, `fallback_on` lets ig-keyword-search cover the hashtag in hashtag mode until `fallback_off`"; `ig-keyword-search §3 L20` and `§13 L170`.
  - b) Target: `source-health-canary §5.1 L47` alternates "Clear today" are TikTok, Facebook amber and the Telegram Actors; "Facebook Page feeds, X, YouTube, LinkedIn, news and web search have no flagged alternate"; Instagram is in neither list; alternates sit in `canary_targets` (`alternate_route`, `alternate_vendor`, `flag_name`); a green-to-amber move carries `scope = non_government` (`§5.3 L79`).
- **At stake:** without an Instagram alternate in `canary_targets` the canary never emits `fallback_on` for hashtags, so ig-keyword-search's hashtag mode never starts.
- **Options:** (1) declare the Instagram hashtag route's alternate (`ig_vendor`, `IG_VENDOR_ROUTE`) with the non-government scope; (2) no Instagram fallback in v1, and ig-keyword-search drops its fallback mode.
- **Blocks:** C12, IG2, VIG1

### AU-072

**Replay path: the `raw.replay` topic, or normalize-item reading `raw/` objects directly**

- **Type:** writers, rule
- **Where:**
  - a) Target: `raw-archiver §4 L35` "normalize-item reads archived records on replay (`raw.replay`)"; `§5.3 L71` the replay API publishes to `raw.replay` (target `normalize-item`, `analysis` or `all`), skips items "with a pending or in-progress row in `deletion_requests`" and "never reads data past its class clock"; `§14 Q2 L182` "normalize-item reads `raw/` directly on a `replay` job. Proposed: `raw.replay` is the main path".
  - b) `normalize-item §5.1 L45` "The replay worker reads `raw/<route>/<platform>/<yyyy>/<mm>/<dd>/<service>/<batch>.jsonl.zst` from object storage (never Redpanda ...)", started by a `replay` job on `jobs.normalize-item`; it reads no `raw.replay` and no `deletion_requests` (`§6.1 L86`-`L88`). `keyword-matcher §5.1 L42` replays "through raw-archiver's replay path (the one normalize-item uses)".
  - c) The analysis services re-run by reading the Parquet archive directly on a `kind = rerun` job (`analysis-sentiment §5.1 L51`, `analysis-topics §5.1 L50`, `analysis-entities §5.1 L46`, `analysis-media §5.1 L47`) and none reads `raw.replay` (`analysis-sentiment §6.1 L85`), although raw-archiver offers `target = analysis` (`raw-archiver §5.3 L71`) and `store-writer §5.1 L41` says the analysis services "re-score" through raw-archiver's replay path.
- **At stake:** two replay mechanisms; the direct read skips the archiver's deletion and class-clock guards, so a replay can republish deleted or expired items.
- **Options:** (1) `raw.replay` is the only path and normalize-item consumes it; (2) the direct read, with the deletion and clock checks moved into the shared SDK reader; (3) both, with the guards in the SDK reader.
- **Blocks:** C2, C4, C5, F4, A1, A2, A3, A4

### AU-073

**Archive lookups by X post id and author id: x-compliance-sync expects an index raw-archiver does not keep**

- **Type:** shape, single-PRD
- **Where:**
  - a) `x-compliance-sync §4 L37` "raw-archiver (archives and their index)"; `§5.1 L43` "raw-archiver's index of the raw and Parquet archives"; `§5.2 L52` "ids found only in the archive index ... author ids from the archive index"; `§5.3 L81` "The target carries `user_ids` so the archives can be searched".
  - b) Target: no index is described; the envelope Parquet is sorted by `item_id` for item lookups (`raw-archiver §5.3 L67`); the envelope has `platform_id` but "no author identity beyond what the payload holds" (`§5.4 L86`); its endpoints are replay, media and rewrite (`§5.1 L44`).
- **At stake:** X compliance must find every stored X post and author id inside 24 hours; without an index it scans an archive with no time limit (`x_24h_sync`) or misses ids held only there.
- **Options:** (1) raw-archiver keeps an id index (platform, platform id, author id to `raw_ref`); (2) x-compliance-sync scans the envelope Parquet and payloads itself; (3) author ids are hashed into the envelope at archive time and searched by `author_hash`.
- **Blocks:** C2, X7, C13

### AU-074

**Callers of lang-dialect-id: "normalize-item: the only caller of `/v1/detect`", while poster-resolver, li-org-resolver and analysis-media send it text**

- **Type:** writers, rule
- **Where:**
  - a) Target: `lang-dialect-id §4 L34` "normalize-item: the only caller of `/v1/detect`"; `§6.1 L99` callers are normalize-item (`/v1/detect`) and keyword-matcher (`/v1/fold`, and CI tools); `§5.4 L94` it does not get "text inside images or video (analysis-media)"; it is a Python service and `listening-sdk` carries only a TypeScript copy of the fold (`§5.3 L88`, `§9 L150`).
  - b) `poster-resolver §5.2 L58` "send the sample of up to 20 recent post texts to `lang-dialect-id`"; `§14 L155` "Whether `lang-dialect-id` exposes a batch call for profile samples or the SDK bundles the classifier in-process".
  - c) `li-org-resolver §5.2 L56` "language share through the `listening-sdk` language client (the model lang-dialect-id runs)".
  - d) `analysis-media §5.3 L66` "the transcript goes to lang-dialect-id for `lang` and `dialect`".
- **At stake:** the qualifier's language-share signal and transcript languages depend on calls the service does not plan for (pool sized for normalize-item plus replay, latency budget a share of the 60 s target); no SDK language client with the model exists.
- **Options:** (1) open `/v1/detect` to these callers and size the pool for them; (2) bundle the classifier in listening-sdk for profile samples and keep `/v1/detect` for normalize-item; (3) resolvers read `lang` from `items.normalized` where the posts exist, and transcripts take the item's language.
- **Blocks:** C3, C8, VLI2, A4, F4, F6

### AU-075

**Arabic in Latin letters (Arabizi): analysis-sentiment routes on a signal lang-dialect-id does not produce**

- **Type:** enum, rule
- **Where:**
  - a) `analysis-sentiment §5.2 L57` "Arabic in Latin letters through transliteration to it"; `§14 Q7 L174` "Confirm `lang` codes and any Latin-letter Arabic flag with lang-dialect-id".
  - b) Target: labels `ar`, `ckb`, `en`, `mixed`, `other`, `und` (`lang-dialect-id §3 L22`); transliteration of Arabizi is out of scope (`§3 L29`); "It does not produce: Arabizi as Arabic" (`§5.4 L94`); "Arabizi is read as `en` or `und`" (`§12 L164`); `§14 Q3 L189` asks whether to add a Latin-script Arabic class after the pilot.
- **At stake:** the Arabizi branch of sentiment routing never fires; such posts go to the English fallback or are skipped as `und`.
- **Options:** (1) lang-dialect-id adds an Arabizi label or flag in v1; (2) analysis-sentiment detects Arabizi itself on `script = latn` text; (3) no Arabizi route in v1, both PRDs revised.
- **Blocks:** C3, A1

### AU-076

**Deletion modes and scopes the propagator does not have: `withhold`, `text_only`, `derived`/`purge_derived`, `fetched_before`, `user_ids`**

- **Type:** enum, shape
- **Where:**
  - a) `x-compliance-sync §11 L171` "deletion-propagator (needs mode `withhold` and scope `author` with `user_ids`)"; `§5.3 L81` "The target carries `user_ids` so the archives can be searched".
  - b) `yt-text-purger §5.3 L106` scope `text_only`, mode `purge_text`, `fetched_before = S`, and `L108`-`L112` the steps deletion-propagator "must do" (a new version only over versions fetched before `fetched_before`, forced merge, text index, caches, raw-archiver rewrite); `§5.3 L118` scope `derived` and "the new mode `purge_derived`"; `§5.2 L58` waits for `completed`.
  - c) Target: modes `delete` (default) and `purge_text` (`deletion-propagator §5.3 L62`, `§5.4 L80`); scopes `item`, `author` (by `author_hash`), `source`, `client` (`§5.3 L60`); no `fetched_before`; an unknown shape is stored as `rejected` (`§8 L128`).
- **At stake:** X withholding, the YouTube 30-day text purge and the 36-month end are rejected or applied with the wrong semantics (for example a purge that also blanks a refreshed version).
- **Options:** (1) add `withhold` and `purge_derived` modes, `text_only` and `derived` scopes and a `fetched_before` guard to deletion-propagator; (2) producers map onto the two modes and four scopes (withhold as delete, text_only as `purge_text` over listed item ids, derived as delete of analysis rows); (3) yt-text-purger performs its own text purge and deletion-propagator handles only full deletions.
- **Blocks:** C13, F2, X7, YT7

### AU-077

**Stores outside deletion-propagator's purge registry: annotation text, service-private indexes, analysis media**

- **Type:** rule, writers
- **Where:**
  - a) Target: `deletion-propagator §5.3 L68` "Delete by `item_id` in every store registered in the purge registry in `listening-sdk` (today the text index and the 7-day news full-text cache). A store that holds text and is not in the registry is a defect"; media through raw-archiver's reference removal (`§5.3 L66`).
  - b) Annotation tool: `analysis-sentiment §5.3 L72` the example's "text is purged with the item (deletion-propagator, retention-purger)"; `analysis-topics §5.3 L76`; `analysis-entities §5.3 L73`.
  - c) Analysis media: `analysis-media §13 L162` "A `deletions` message removes the item's OCR text, transcript and, when no live item references it, the media object"; `§14 Q3 L170` where the reference index lives is open.
  - d) Service-private index: `x-replies-fetcher §6.3 L138` reply-index rows are "removed by deletion-propagator when x-compliance-sync reports a deletion".
  - e) `fb-post-comments-fetcher §6.3 L129` its `comment_ledger` "is removed by retention-purger with the post's comments"; retention-purger does no deletion itself (`retention-purger §3 L28`), selects only from ClickHouse `items` and `comments` (`§5.3 L72`) and "does not get platform content, text or media" (`§5.4 L84`), while `analysis-media §14 Q3 L170` asks "how does retention-purger find unreferenced `media/<sha256>`".
- **At stake:** labelled copies of item text, OCR text and transcripts, and X reply ids survive deletions, so the "removes the item from every place" guarantee (and X's 24-hour rule) fails.
- **Options:** (1) register the annotation tool, analysis-media's stores and the reply and comment indexes in the purge registry; (2) each owning service consumes `deletions` and purges its own store, reporting to deletion-propagator; (3) these stores keep only `item_id` references, never text.
- **Blocks:** C13, C14, F4, A1, A2, A3, A4, X6

### AU-078

**LinkedIn 48-hour clock: applied by field inside organization posts, or by kind**

- **Type:** retention, rule
- **Where:**
  - a) `li-client-posts-poller §7 L135`: "retention-purger applies it by field: the page's own posts and counts as the organization rule allows (six weeks, six months if authenticated), any member-level field that appears (an administrator or a mentioned member) at 48 hours".
  - b) Target: `retention-purger §5.3 L64` `linkedin_48h`: "48 hours for member social activity; 24 hours for member profile data; organization data as the API terms allow", and the sweep "Emits `deletions` (mode `delete`) by `kind`"; the modes are `delete` (whole item) and `purge_text` (text and author reference) (`§5.3 L70`); no field-level purge.
- **At stake:** member fields inside an organization post either outlive 48 hours (the post is kept) or take the whole post with them (deleted by kind); the store keeps one class per row.
- **Options:** (1) a field-level purge mode for member fields inside organization items; (2) the poller drops or hashes member fields before writing, so organization items hold no member data; (3) organization items take the 48-hour clock whole, and only aggregates survive.
- **Blocks:** C14, C13, LI1

### AU-079

**Registry decision for an author request that matches a registered source: no producer and no decision type**

- **Type:** writers, enum
- **Where:**
  - a) `deletion-propagator §14 Q3 L173`: "An author request that matches a registered source needs a registry decision; no producer for it is listed in registry-writer. Proposed: retention-purger emits it."
  - b) Target: retention-purger emits only `remove_client` on `registry.decisions` (`retention-purger §3 L22`, `§6.2 L94`); author requests become `deletions` with scope `author` (`§5.3 L78`). `registry-writer §3 L22` lists no decision type for it.
- **At stake:** an author who is also a registered source keeps being polled after asking to be forgotten.
- **Options:** (1) retention-purger emits a `retire` (or new) decision for the matching source; (2) ops handles it through the manual path; (3) an author request never touches the registry.
- **Blocks:** C14, C7, C13

### AU-080

**YouTube derived metrics and aggregates: ten years, or 36 months**

- **Type:** retention, document
- **Where:**
  - a) `CONVENTIONS L76` `youtube_30d_text`: "derived metrics kept up to 36 months"; `CONVENTIONS L81` "Aggregates and derived scores: ten years, all classes".
  - b) Target: `retention-purger §5.3 L68` "Aggregates and derived scores | ... | Ten years, all classes | Never selected"; `§3 L30` deleting aggregates or derived scores is out of scope.
  - c) `yt-comments-fetcher §14 Q5 L207` "YouTube allows derived metrics up to 36 months: retention-purger's rule for YouTube aggregates needs a decision"; `store-writer §5.3 L76` deletes `youtube_30d_text` item rows at "created + 36 months" while aggregates stay ten years.
- **At stake:** YouTube-derived aggregates may be kept seven years longer than the YouTube terms quoted in CONVENTIONS allow; nobody deletes them.
- **Options:** (1) ten years for all aggregates (CONVENTIONS L81, target); (2) 36 months for YouTube-derived aggregates and scores, with a purge path; (3) ten years only for aggregates that do not identify a YouTube channel owner, 36 months for the rest.
- **Blocks:** C14, C15, YT5, F8

### AU-081

**Aggregate grain: language, entities, brand appearance, per-post LinkedIn rollups, stories and channel owners are promised but not in the grain**

- **Type:** shape, rule
- **Where:**
  - a) Target: grain "`(hour, client_id, keyword_id, platform, source_id, sentiment, topic_id, retention_class)`", with `source_id` the poster's `author_source_id` (`aggregator §5.3 L55`); measures `mentions` (distinct items), `reach`, `engagement`, `views` (`§5.3 L57`); no other dimension or table besides hourly, daily and monthly (`§6.2 L77`).
  - b) Language: `lang-dialect-id §4 L37` "aggregator and dashboards split by language".
  - c) Entities and media (delta): `analysis-entities §4 L33` "aggregator builds mentions by governorate, institution and brand"; `analysis-media §4 L34` "aggregator builds brand-appearance and tag views".
  - d) Per post, before the 48-hour purge: `li-notification-receiver §7 L142` "hourly aggregates (comments and reactions per post per hour) are computed first and kept ten years"; `li-own-comments-fetcher §7 L135` "(comments per post per hour, sentiment shares, themes)", `§2 L13`; `li-post-comments-fetcher §7 L139` "unique-commenter counts, comment counts and sentiment aggregates per post", `§4 L32`.
  - e) Stories: `news-dedup §14 Q4 L170` "Should unique-story and mention counts both be first-class in aggregator? Proposed: yes, with `is_origin` as the story flag".
  - f) Channel owners: `yt-comments-fetcher §4 L34` "aggregator (cross-owner rule via `video_channel_id`)"; `yt-video-details-fetcher §4 L35` "`channel_id` lets aggregator keep owners apart"; `CONVENTIONS L76` "no aggregation across channel owners except under the analytics carve-out"; the target has no owner dimension or rule.
  - g) Other views: `ig-hashtag-search §14 L188` a "trending" score from `top_media`; `tt-hashtag-feed-poller §4 L35` "aggregator builds the campaign view".
- **At stake:** LinkedIn comment history promised to clients has no table once the 48-hour purge runs; YouTube comment counts can mix channel owners against the terms CONVENTIONS quotes; language, entity, logo and story views have nowhere to come from.
- **Options:** (1) extend the grain (language, channel owner) and add rollup tables owned by aggregator (per-post LinkedIn, entities and brands, stories); (2) the producing services build their own rollups; (3) keep the grain and drop the promises from the other PRDs (per-post and entity views read base tables within retention only).
- **Blocks:** C15, F8, C3, LI2, LI3, VLI4, YT4, YT5, N7, A3, A4

### AU-082

**Recompute after deletions: deletion-propagator's bucket jobs and `done`, against aggregator's date-range job and its own `deletions` reconciliation**

- **Type:** job kind, shape, writers
- **Where:**
  - a) `deletion-propagator §5.3 L70` "collect the distinct (`source_id`, hour) buckets and keyword ids of the removed items and send `recompute` jobs to `jobs.aggregator`; wait for `done`"; verification includes "aggregator job `done`" (`§5.3 L74`, `§6.2 L104`); `retention-purger §5.3 L70` `delete` "triggers an aggregate recompute (aggregator)".
  - b) Target: a `jobs.aggregator` job with `kind = recompute` "(date range, optional client) is the ops entry point" (`aggregator §5.1 L37`); a `deletions` message on its own consumer group "triggers a reconciliation within 5 minutes" (same line); passes are reported in `service_runs` and recompute progress in `cursors` (`§5.2 L49`, `§6.3 L97`), with no per-job `done`; `§11 L128` names "`deletions` (deletion-propagator)" as the source, though deletion-propagator consumes that topic.
  - c) Frozen hours: "Counts of a frozen hour are never reduced by a later deletion" (`aggregator §5.3 L61`), so a recompute without the item cannot happen for a `linkedin_48h` hour older than 48 hours.
- **At stake:** deletion-propagator waits for a `done` aggregator never sends, so deletions stall before `completed` (the X 24-hour deadline included); the job fields do not match; the same deletion triggers two recomputes.
- **Options:** (1) aggregator accepts bucket jobs and reports `done` (on `jobs.completed` or a status row); (2) deletion-propagator drops the recompute step and verifies by query after aggregator's own reconciliation; (3) a shared recompute-request table both read and write.
- **Blocks:** C15, C13, C14, F2

### AU-083

**Alert features other PRDs promise that no alert-evaluator rule type implements**

- **Type:** enum, rule
- **Where:**
  - a) Target: five rule types, "volume spike against a 7-day baseline per keyword and source, negative-share threshold, new high-reach poster, keyword first seen, deletion of a high-reach post" (`alert-evaluator §3 L22`); rule scope is `keyword` or `keyword_source` (`§5.3 L56`); predicates read mentions and sentiment from `aggregates_hourly_v` (`§5.3 L57`-`L60`); the `alert/v1` payload carries keyword, scope, window and metrics, no topic or theme (`§6.2 L87`-`L98`).
  - b) Engagement: `fb-reactions-fetcher §4 L33` "alert-evaluator uses velocity for spike alerts"; `tt-video-stats-refresher §4 L36` "aggregator and alert-evaluator (engagement scores, spike alerts)".
  - c) Topics and themes (delta): `analysis-topics §4 L37` "alert-evaluator reads topic spikes ("outage mentions up")"; `li-own-comments-fetcher §4 L32` "alerts carry counts and themes".
  - d) Entities and logos (delta): `analysis-entities §4 L33` "alert-evaluator can fire on a named institution"; `analysis-media §4 L34` "alert-evaluator can fire on a client logo in high-reach media".
  - e) Stories: `news-dedup §4 L35` "alert-evaluator (alerts on unique stories, not copies)"; the target's volume rule counts `mentions`, which are distinct items (`aggregator §5.3 L57`).
- **At stake:** client-facing features described in seven PRDs have no rule type, and topic, entity and story alerts would also need aggregate dimensions that do not exist (AU-081).
- **Options:** (1) add rule types (engagement spike, topic spike, entity or logo, story-level volume) with their aggregate inputs; (2) keep five types in v1 and remove the claims; (3) express topic and entity alerts as keyword rules over mapped keywords.
- **Blocks:** A5, C15, A2, A3, A4, N7, FB4, VTT6

### AU-084

**`metrics_observation = webhook_reconcile` has no producer, and webhook-delivered Facebook posts carry no summaries**

- **Type:** enum; rule
- **Where:**
  - fb-reactions-fetcher §3 L19: extract mode consumes every `raw.items` post with `platform = facebook`, `route = green` and labels the observation with the envelope's `metrics_observation` "(`poll`, `backfill`, `webhook_reconcile`)"; §5.2 L51 step 4; §8 L146 and §13 L181: a payload with a missing reaction alias raises `schema_unknown` and writes no observation.
  - fb-page-feed-poller, which runs the push-tier reconciliation (§5.1 L42, job `reason` `reconciliation` §5.2 L54), writes `"metrics_observation": "poll"` (§6.2 L123) and never names `webhook_reconcile`.
  - fb-client-webhook-receiver §5.2 L56 drops reaction events because "counts come from fb-reactions-fetcher"; its envelope carries `"delivery": "push"` and no `metrics_observation` (§6.2 L125), and its payload is the webhook change value (`item`, `verb`, `post_id`, `message`, `created_time`; L129), not a `/feed` object with the seven summaries; posts are `kind = post`, `route = green` (L21, L133), so extract mode takes them.
- **At stake:** every webhook-delivered post of a client-owned Page would hit fb-reactions-fetcher's `schema_unknown` path, and the label that should tell reconciliation reads apart from rotation polls is never set.
- **Options:** (1) fb-page-feed-poller writes `webhook_reconcile` on reconciliation jobs and fb-reactions-fetcher skips records with `delivery = push`; (2) drop `webhook_reconcile` from the vocabulary and filter extract mode on records that carry summaries; (3) one `metrics_observation` vocabulary for all platforms in F2 (see CF-019), with the webhook case named.
- **Blocks:** F2, FB2, FB4, FB7.

### AU-085

**A deleted post found by a comment fetcher is handed to a poller that does not detect it (Instagram; LinkedIn after day 7)**

- **Type:** writers; rule
- **Where:**
  - Instagram: ig-own-comments-fetcher §8 L149: "A deleted post: the edge errors; the series is cancelled and the post is left to ig-account-media-poller's next read." ig-account-media-poller reads only media newer than the cursor (§5.2 L61; a `metrics` job reads back to one post's `timestamp`, §5.1 L52); its writes are `raw.items`, `source.events`, `review_queue`, `service_runs` and the DLQ (§6.2 L104, L125): no `deletions`, and no rule turns a post missing from a re-read into a removal.
  - LinkedIn: li-own-comments-fetcher §8 L143: "A post that no longer exists (404): series cancelled; the deletion is li-client-posts-poller's to mirror"; its series can be extended "every 2 days until day 30" (§5.1 L44). li-client-posts-poller mirrors deletions only in its daily reconciliation of "the last 7 days" (§5.1 L48) and "touches nothing older" (§13 L179), while it keeps the page's posts "as the organization rule allows (six weeks, six months if authenticated)" (§7 L135).
  - Compare CONVENTIONS L63 (missing comments become `deletions` with reason `platform_sync`) and fb-reactions-fetcher §5.4 L92, §8 L144 (a post gone on refresh becomes a `deletions` message).
- **At stake:** a post deleted on a client's own Instagram account, or a LinkedIn post deleted after its first week, stays in `items` and in dashboards, although `meta_on_request` data must go on request (CONVENTIONS L78) and LinkedIn data may be kept only as its terms allow.
- **Options:** (1) the poller emits `deletions` when a `metrics` or reconciliation re-read no longer lists a post it should (Instagram), and the LinkedIn reconciliation window covers the whole retention period; (2) the comment fetcher emits the post's `deletions` on the deleted-object error (404) it already sees; (3) post deletions only through deletion-propagator requests (client, user, platform).
- **Blocks:** IG3, IG6, LI1, LI2, C13.

### AU-086

**ig-webhook-receiver's reconciliation and targeted jobs: fields and a report the two fetchers do not define**

- **Type:** job kind; shape; rule
- **Where:**
  - ig-webhook-receiver §5.1 L43: per due account "two `reconciliation` jobs, one on `jobs.ig-own-comments-fetcher` (comments on media still inside the first 7 days of their series) and one on `jobs.ig-mentions-fetcher` (a read back to 24 hours before its cursor). The account's next due time is set when both report."; §5.2 L57 "a targeted read (`ops_force`, one id) to `jobs.ig-mentions-fetcher`"; L58 "(`ops_force`, `post_ref` = media id) to `jobs.ig-own-comments-fetcher`"; §6.1 L99 reads "job results of the two fetching services".
  - ig-mentions-fetcher: job fields `source_id`, `kind` = rotation | reconciliation | backfill | ops_force, `attempt` (§5.2 L55), no field for an id; its `ops_force` is "force a poll of one account" (§4 L34); it reports no job result (§5.2 L60-L61 move cursors and count `missed_push_total`; §6.2 L126 writes `raw.items`, `service_runs`, DLQ); §12 L167 and §14 Q1 L190 expect webhook-supplied ids without naming a job field.
  - ig-own-comments-fetcher §5.1 L41: "A job names one post (`post_ref` = media id) and one `series_step`", yet the same line has one `reconciliation` job per account covering all media inside their first 7 days; it keeps no per-post state (§6.3 L133) and reads the stored comments of one post (§5.2 L60), so nothing lists the media of a per-account job.
- **At stake:** an owned account's reconciliation never completes (no report from ig-mentions-fetcher, so ig-webhook-receiver never sets the next due time), a targeted mention read has no field for its id, and a per-account comment reconciliation has no media list.
- **Options:** (1) one reconciliation job per media (`post_ref`) for comments and per account for mentions, with the SDK completion record (CF-089) as the report for both; (2) per-account jobs with `post_refs` and `target_ids` lists added to the job schema; (3) ig-webhook-receiver sets the next due time when it emits and waits for no report.
- **Blocks:** F2, F4, IG4, IG5, IG6, C11.

### AU-087

**Hashtag budget waits sent as `fallback_on`: who sets `health = fallback`, who ends it, and how a 31st hashtag reaches the amber route**

- **Type:** enum; rule; writers
- **Where:**
  - ig-hashtag-search §5.1 L57: a hashtag that would be the 31st in the window is denied, its `next_poll_at` set to the earliest window expiry, and "the client is told through `source.events` (`fallback_on` when the amber route is on, otherwise `updated` with a `budget_wait` note)"; §6.2 L93 writes `source.events` (budget waits); §13 L176; §8 L144 has the canary case ("`fallback_on` lets ig-keyword-search cover the hashtag in hashtag mode until `fallback_off`"). No `fallback_off` is described for a window that frees a slot, and the service writes no `health`.
  - ig-keyword-search §5.1 L41 selects sources with `route = amber` and `vendor = sociavault`, "or `health = fallback`"; a client's 31st hashtag is a source with "registry `route = amber`" (§3 L20; §13 L169), not a green source in `fallback_on`.
  - CONVENTIONS L102: `fallback_on` is the canary's move after an empty-200 spike ("the canary flips `health = degraded` and ... `fallback_on`").
- **At stake:** a budget-denied green hashtag either stays dark (no one sets `health = fallback`, so ig-keyword-search never selects it) or, if `fallback_on` is mapped to `health`, stays on the paid route for good, since nothing emits `fallback_off` when the 7-day window frees the slot.
- **Options:** (1) overflow is decided at registration (the 31st tag registered `route = amber`, as ig-keyword-search reads it) and ig-hashtag-search only emits `updated` with `budget_wait`; (2) ig-hashtag-search's `fallback_on` stands: registry-writer sets `health = fallback` and ig-hashtag-search emits `fallback_off` at window expiry; (3) only source-health-canary emits `fallback_on` and `fallback_off`, and a budget wait never moves a hashtag to the vendor.
- **Blocks:** F2, IG2, VIG1, C7, C12.

### AU-088

**`jobs.ig-hashtag-search` rotation jobs come from a "shared scheduler" no document defines**

- **Type:** job kind; rule; single-PRD
- **Where:**
  - ig-hashtag-search §5.1 L45: "a job on `jobs.ig-hashtag-search` emitted by the shared scheduler when a hashtag source's `next_poll_at` is due, or by backfill-orchestrator when a hashtag is added"; §5.1 L55 gives the cadence mechanics but the PRD has no leader-elected loop of its own (the term "shared scheduler" appears in no other PRD).
  - CONVENTIONS addendum L278: "Every service that polls keeps its own rotation scheduler as a leader-elected loop (Postgres advisory lock) that emits due jobs, exactly as described in fb-page-feed-poller".
  - The add-time job: ig-hashtag-search §5.1 L59 makes its first poll the backfill, while backfill-orchestrator §5.3 L79 maps "Hashtag or keyword rule without a history route" to no service ("`done` at once") and §13 L150 has "a hashtag source go to `done` with no job".
- **At stake:** as written nothing emits rotation or first-poll jobs for green hashtags, so the green Instagram discovery lane never starts.
- **Options:** (1) ig-hashtag-search keeps its own scheduler per CONVENTIONS L278 and emits its own first poll on `added`; (2) a shared scheduler becomes an SDK component or service for all pollers, and CONVENTIONS L278 is rewritten.
- **Blocks:** IG2, F5, C10.

### AU-089

**Which authors keep their identity downstream: "business or creator accounts" against "registered sources"**

- **Type:** rule
- **Where:**
  - ig-webhook-receiver §7 L135: "pushed authors keep only a hashed reference downstream unless they are business or creator accounts"; ig-mentions-fetcher §9 L155 and §12 L171 say the same of mention authors.
  - normalize-item §5.2 L55: "An author found in the registry cache (fed by `source.events`) gets `author_type = source`, `author_source_id` and its display name; anyone else is `individual` with no name, handle or avatar."
- **At stake:** a business or creator account that is not a registered source is stored as an anonymous individual, so the IG services' promise does not hold; keeping the IG rule instead needs an account class that no `raw.items` envelope carries.
- **Options:** (1) normalize-item's rule (identity only for registered sources) and the IG PRDs reworded; (2) identity kept for authors that poster-resolver classed non-individual (lookup on `poster_profiles`); (3) a per-platform rule in the mapper.
- **Blocks:** C4, IG4, IG5.

### AU-090

**A comment's `content_hash`: text only in the Instagram fetchers, title + text + media URLs in the stored rows they compare against**

- **Type:** key; rule
- **Where:**
  - ig-own-comments-fetcher §5.1 L49 "Each comment's `content_hash` is the SHA-256 of its `text`"; §5.2 L60 and L62 compare it with "the stored comment ids and content hashes of the post from ClickHouse `comments`". ig-comments-fetcher §5.1 L49 (SHA-256 of its text) and §5.2 L62 do the same.
  - The stored value is normalize-item's: "`content_hash = sha256(title + text + media urls)`" (§5.2 L51); store-writer keeps "every field of `items.normalized/v1` under the same name" (§5.3 L67).
- **At stake:** a comment carrying a media URL (sticker, image) or a title hashes differently on the two sides, so every fetch writes it again as a new version and the edit counts become noise.
- **Options:** (1) one SDK hash helper with one input definition, used by fetchers and normalize-item; (2) fetchers compare against their own envelope hash, stored in its own column; (3) normalize-item uses the text-only hash for comments.
- **Blocks:** F2, F4, C4, C6, IG6, VIG2.

### AU-091

**A green push source is one registry row (`route = green`), yet the amber poller's daily reconciliation that both sides count on selects `route = amber` (TikTok, Telegram)**

- **Type:** rule; enum
- **Where:**
  - tt-client-videos-fetcher §5.1 L41 selects `platform = tiktok`, `route = green`, `owned_by_client = true`; L43 "The registry marks these accounts `tier = push`, so tt-profile-videos-poller makes only its one reconciliation poll a day for them"; §4 L35 and §8 L132 call that reconciliation "the only second route for these accounts".
  - tt-profile-videos-poller §5.1 L41 selects `source_type = creator`, `route = amber`; §5.1 L43 "Push (client-authorised creators whose videos arrive hourly from tt-client-videos-fetcher): ... one reconciliation poll every 24 hours"; §14 Q3 L188.
  - Telegram: tg-bot-channel-receiver registers bot channels with `route = green`, `vendor` null, `tier = push` (§5.2 L70) and counts on "tg-channel-posts-poller's daily reconciliation read" to fill gaps after an outage (§5.1 L52; §12 L175). tg-channel-posts-poller §5.1 L42 selects `route = amber` only, while its §5.1 L44 promises the push channels "one reconciliation read a day, because the bot has no history method".
  - CONVENTIONS L36: `sources.route` is one value per row (green or amber); registry-writer owns `route` (§3 L27).
- **At stake:** with one row per account or channel, the amber pollers' selectors never match a green push source, so the daily reconciliation both sides rely on never runs (and a Telegram receiver outage is never repaired); with two rows, the source has two `source_id`s, two tiers and two cursors, which no PRD describes.
- **Options:** (1) one row (`route = green`), and the amber pollers' selectors add green push sources whose clients accept amber data; (2) a second, amber row per authorised account or bot channel, linked to the green one; (3) drop the amber reconciliation and treat the green read as complete.
- **Blocks:** TT1, VTT4, TG1, VTG3, C7, C9.

### AU-092

**Per-client acceptance of amber data: some amber services filter on it, others only on the government flag**

- **Type:** rule; single-PRD
- **Where:**
  - Filter on acceptance: ig-comments-fetcher §5.1 L41 (a series opens only when "at least one client watching the source has accepted the amber provenance") and §6.1 L89 (`clients` "government flag, amber acceptance"); ig-keyword-search §5.2 L58, §6.1 L92, §6.2 L117; tt-profile-videos-poller §5.1 L43 (reconciliation "skipped where the client's contract excludes amber data") and §6.1 L101 (`clients` "government flag, contract terms"); tt-client-videos-fetcher §3 L27 ("Where the client's contract allows amber data, tt-video-comments-fetcher may read them") and §8 L132.
  - Filter on the government flag only: tg-channel-posts-poller, whose "accepts amber data" is defined as "the government flag in `clients` is false" (§5.1 L42; §6.2 L128); tt-video-comments-fetcher §5.2 L56 (refuses only videos that "belong only to government-contract sources") and §6.1 L93 (`clients` "government flag"); tt-video-stats-refresher §6.1 L81 and §13 L169; tt-keyword-search §5.2 L48 and §6.1 L69; tt-hashtag-feed-poller §5.2 L54 and §6.1 L75; fb-group-posts-poller §5.1 L40 and §6.1 L98 ("government marker"); fb-group-comments-fetcher §6.1 L100; fb-keyword-search §5.1 L40.
  - CONVENTIONS L7: an amber service is "optional, behind a feature flag, and its provenance is disclosed to clients and excluded from government contracts"; no per-client acceptance, and `clients` has no column list (L30).
- **At stake:** a non-government client whose contract excludes amber data still receives amber TikTok comments and stats, Telegram posts and Facebook data, while the same client's amber Instagram data and the amber TikTok reconciliation are withheld; "accepts amber data" means two different things, and F3 has no column to build either check on.
- **Options:** (1) per-client amber acceptance (a `clients` column) checked by every amber service and by comment-decay-scheduler; (2) government flag only, as CONVENTIONS L7 says, and the acceptance checks are removed; (3) acceptance checked once, by keyword-matcher and the client app at read time, not by fetchers.
- **Blocks:** F3, IG2, VIG1, VIG2, VTT1 to VTT6, VFB1 to VFB3, VTG3, TT1, C11.

### AU-093

**x-filtered-stream's gap jobs: a kind, fields, attribution and a report that x-recent-search and x-full-archive-search do not define**

- **Type:** job kind; shape; rule
- **Where:**
  - x-filtered-stream §5.2 C L70: one job per affected rule on `jobs.x-recent-search` with "`kind = reconciliation` ... `source_id` = the rule's first source, `query` = rule value, `source_ids`, `client_ids`, `window_start`, `window_end`, the rule's priority. Any part older than recent search's 7 days goes to `jobs.x-full-archive-search`"; L71 "The gap closes when `jobs.completed` arrives for all its jobs"; §13 L196; §14 Q3 L207 asks x-recent-search's owner to confirm the shape and "that account-rule results get the author's `source_id`". Account rules are `from:` buckets of several accounts (§5.1 L40, §6.2 L140).
  - x-recent-search: a job carries `source_id`, `tier`, `attempt`, `reason` = rotation | first_run | gap_backfill | ops_force (§5.2 L53), runs for `source_type = keyword_rule` rows only (§5.1 L39), reads from the rule's `since_id` cursor (L56) with a query built from `keywords` (L54), writes `source_id` = the keyword rule (§6.2 L106-L107), and writes no `jobs.completed` (§6.2 L98).
  - x-full-archive-search takes `backfill`, `keyword_history` and `replies` jobs from backfill-orchestrator and comment-decay-scheduler only (§3 L19-L21, §5.1 L39); no gap job and no producer x-filtered-stream.
- **At stake:** after every stream disconnect the gap jobs fail on schema or kind, account-rule posts read by a gap job are filed under a keyword rule (or nothing), and no gap ever closes (`gap_unfilled`), because neither consumer writes the completion x-filtered-stream waits for.
- **Options:** (1) x-recent-search adds a `reconciliation` (or `gap_backfill`) job with an explicit `query` and window, attributes `from:` results by `author_id`, and writes `jobs.completed`; x-full-archive-search adds the same kind for parts older than 7 days; (2) x-filtered-stream re-reads gaps itself through recent and full-archive search under its own job queue; (3) gaps of account rules go to x-user-timeline-poller as `reconciliation` polls, keyword gaps to x-recent-search's normal cursor run.
- **Blocks:** F2, F4, X1, X4, X5.

### AU-094

**Who emits `backfill` and `keyword_history` jobs for an X keyword rule**

- **Type:** job kind; rule
- **Where:**
  - x-recent-search §5.1 L45: a cursor older than 7 days "triggers one `keyword_history` job on x-full-archive-search (budget gated) before the rule resumes here" (§13 L188: the rule "produces one `keyword_history` request"); §5.1 L49: a new rule is searched once over 7 days and "older history is a `keyword_history` job on x-full-archive-search, created by backfill-orchestrator on client request".
  - x-full-archive-search §5.1 L39: "backfill-orchestrator emits `backfill` for each X account ... and `keyword_history` on a client request"; §5.2 L50: `keyword_history` only on a requesting client's registered terms; §13 L183: "A backfill for an individual or a keyword rule ... end[s] without an API call".
  - backfill-orchestrator §5.3 L72 routes "X account or keyword rule" to x-full-archive-search on `added`; its job is `kind: backfill` (§6.2 L106); it calls itself "the only service that emits `backfill` jobs" (§1 L9) and names no `keyword_history`.
- **At stake:** every new X keyword rule gets an automatic `backfill` job that x-full-archive-search refuses, a stale x-recent-search cursor emits a `keyword_history` job from a producer x-full-archive-search does not accept, and client-requested history needs a kind backfill-orchestrator does not emit.
- **Options:** (1) backfill-orchestrator sends no job for X keyword rules (x-recent-search's 7-day `first_run` is the backfill) and emits `keyword_history` only on client request; x-recent-search stops emitting it; (2) x-recent-search owns `keyword_history` emission (stale cursor and client request) and x-full-archive-search lists it as a producer; (3) one `backfill` kind with a `scope` (`account` or `keyword`) and a `requested_by`.
- **Blocks:** F2, X1, X5, C10.

### AU-095

**The X Enterprise gate for government clients: checked in five places under three representations, and not where x-recent-search expects it**

- **Type:** flag; rule; single-PRD
- **Where:**
  - x-recent-search §12 L175: "the registry refuses X rules whose `client_ids` carry a government flag until the Enterprise contract is recorded in `clients`"; §7 L146: sensitive-event rules "are rejected at registry review and refused by the builder"; its own steps (§5.2 L53-L59) drop no government client.
  - registry-writer has no such refusal: manual adds (§5.2 L61), `clients` read for "government flag, roles" (§6.1 L88), and its only government test is an amber manual add (§13 L152).
  - Per-client column: keyword-matcher §5.2 L69 `clients.x_enterprise` ("none on X items unless `clients.x_enterprise = true`"); "X Enterprise entitlement" in `clients` for x-filtered-stream (§5.2 A L52, §6.1 L107), x-user-timeline-poller (§5.2 L55, §6.1 L108) and x-full-archive-search (§5.2 L50, §6.1 L102); x-user-timeline-poller §14 Q5 L195: "Which `clients` column records a government client's X Enterprise entitlement?"
  - App-level setting: x-user-resolver §5.2 L54 "unless `X_PLAN = enterprise` with that end user declared"; x-replies-fetcher §5.2 L54 "only when the company app's X plan setting is Enterprise".
- **At stake:** x-recent-search reads and pays for X posts for a rule whose only clients are government end users without Enterprise, because the registry check it relies on does not exist; the other five services cannot share one test while the entitlement is a `clients` column in some and an app-wide setting in others.
- **Options:** (1) one `clients` column (for example `x_enterprise`, or an end-user declaration) checked by every x-* service and keyword-matcher, x-recent-search included; (2) one app-level setting plus a per-client declaration list; (3) a registry-time refusal in registry-writer for government-only X rules, the fetch-time checks kept as a second line.
- **Blocks:** F3, X1 to X7, C5, C7.

### AU-096

**An X reply: `x:comment:<id>` from x-replies-fetcher, `x:post:<id>` from the other X readers, and no agreed hand-back for replies older than 7 days**

- **Type:** key; shape; rule
- **Where:**
  - x-replies-fetcher §6.2 L115: `idempotency_key: "x:comment:<id>"`, `kind: "comment"`, with `ledger_key: "x:post:<id>"` (L116); authors minimized and `includes.users` dropped (§5.2 L59, §6.2 L128, §13 L189); its reply index (§6.3 L138) is the series bookkeeping and is written only by itself; §14 Q5 L203: "A reply also delivered as a post by x-recent-search or x-filtered-stream arrives as `x:post:<id>`; normalize-item must decide how it links to `x:comment:<id>`."
  - x-recent-search §5.2 L57 (`x:post:<id>` for every post it reads, replies included), x-filtered-stream §6.2 L120.
  - x-full-archive-search §6.2 L128: "replies messages add `post_ref` and otherwise match x-replies-fetcher's", while its envelope is "the poller's envelope plus `job_kind`, and the post with its `includes`, unchanged" (L106) and its key example is `x:post:` (L117); the hand-back is a `jobs.completed` with the window's `end_time` that "comment-decay-scheduler records as that step so x-replies-fetcher reads only newer replies" (L128); §14 Q2 L190 "Align the replies hand-back with the x-replies-fetcher PRD". x-replies-fetcher mentions no boundary or `end_time` and reads from "the newest stored reply" in its own index (§5.3 L69).
- **At stake:** one reply becomes two items (one in `items`, one in `comments`) with different ids, so counts, sentiment and deletions split; replies read by x-full-archive-search can carry reply authors' ids and usernames in clear and never enter x-replies-fetcher's index.
- **Options:** (1) every X reader writes replies as `x:comment:<id>` with x-replies-fetcher's minimization (an SDK X mapper), and the boundary is a field of x-replies-fetcher's index; (2) keep `x:post:<id>` for every X post, replies included, and x-replies-fetcher adopts it; (3) keep both keys and have normalize-item map `x:post:<id>` of a reply to `x:comment:<id>`.
- **Blocks:** F2, C4, X1, X3, X4, X5, X6.

### AU-097

**The n8n flows: several PRDs call them by signed webhook, no document defines the flows, their endpoints, payloads or signing (follow-up assumption)**

- **Type:** document; single-PRD
- **Where:**
  - alert-evaluator §3 L24 and L27: delivery "through n8n flows (email, Telegram, Slack)", "sending email, Telegram or Slack messages themselves (the n8n flows)" out of scope; §5.3 L69: "Email, Telegram and Slack each have an n8n flow reached by a signed webhook call"; §6.2 L85-L87: payload `"schema": "alert/v1"`.
  - Other callers, each with its own payload: qualifier §5.3 L67 (`POST /qualifier/review` with the card payload and three buttons, and a signed callback, §9 L116); source-health-canary §5.2 L57 ("an n8n alert") and §5.3 L77 (an approval card for `blocked`); quota-governor §4 L31 ("n8n delivers the alerts"); registry-writer §11 L133 (request notifications); li-org-resolver §6.2 L79 (review cards); x-compliance-sync §6.2 L130 (exports).
  - CONVENTIONS names n8n only as part of the stack (L3) and for the review card (L251, rule 10); no PRD covers n8n, and the session brief for the parts with no PRD lists the query API, client portal, dashboard and admin console only (build-plan `D3-specs-for-the-parts-with-no-prd.md` L7).
- **At stake:** alert delivery, review cards and ops alerts each depend on an n8n endpoint whose path, payload schema, signature scheme and callback no build session owns, so each caller will invent its own and nothing tests the far side.
- **Options:** (1) one internal n8n interface in F2 (endpoints, `alert/v1` and card schemas, HMAC signing, callback contract), with the flows as a named deliverable of an existing session; (2) each caller owns its flow and documents it in its PRD; (3) replace n8n for alert delivery by direct email, Slack and Telegram clients in alert-evaluator, keeping n8n for review cards only.
- **Blocks:** F2, A5, C1, C7, C9, C12, VLI2, X7.

### AU-098

**LinkedIn posts found by keyword search: comment series by default (li-post-search) or only if the budget allows, default no (li-post-comments-fetcher)**

- **Type:** rule
- **Where:**
  - li-post-search §5.1 L50: comment jobs "go to li-post-comments-fetcher only for keyword hits and posts of registered sources; posts by individuals get no comment fetch".
  - li-post-comments-fetcher §5.1 L40: "By default the series opens for posts of registered third-party company pages; posts matched by keyword through li-post-search get one only if the budget allows"; §14 Q4 L195: "Should posts matched by keyword (li-post-search) get a series? Default no, pending the budget."
  - The opening rule is comment-decay-scheduler's profile (CONVENTIONS addendum L267: "LinkedIn other posts, amber | li-post-comments-fetcher | +24 h, +3 d").
- **At stake:** comment-decay-scheduler's LinkedIn amber profile cannot be built from both PRDs: the number of series opened (and so most of `li_vendor_post_comments` spend) depends on which default wins.
- **Options:** (1) keyword-hit posts get a series by default (li-post-search); (2) only posts of registered pages by default, keyword hits on budget headroom (li-post-comments-fetcher); (3) keyword hits only for a client's priority keywords.
- **Blocks:** C11, VLI1, VLI4.

### AU-099

**The Telegram daily health check: a `health` job from comment-decay-scheduler, or tg-discussion-receiver's own `reconciliation` job**

- **Type:** job kind; writers
- **Where:**
  - comment-decay-scheduler §5.1 L57, profile `tg_own`: "push; one daily `health` job" (CONVENTIONS addendum L268: "push (live), daily health check").
  - tg-discussion-receiver §4 L37: "comment-decay-scheduler holds a `push` row for this route and emits nothing for it"; §5.1 L45: "comment-decay-scheduler emits no jobs for this route"; §5.1 L47: its own leader replica "emits one `reconciliation` job per group to `jobs.tg-discussion-receiver`" for the daily check; §6.1 L110 accepts kinds `reconciliation` and `ops_force` only.
  - Overlaps CF-077 (`health` among the kinds outside CONVENTIONS); this entry is the producer question.
- **At stake:** either two producers run the same daily check on one queue, or comment-decay-scheduler emits a `health` kind the consumer rejects.
- **Options:** (1) tg-discussion-receiver's own scheduler emits `reconciliation`, and comment-decay-scheduler's `tg_own` row only records the profile; (2) comment-decay-scheduler emits the daily job and tg-discussion-receiver drops its scheduler and accepts `health`.
- **Blocks:** F2, C11, TG2.

### AU-100

**YouTube channels without a working subscription: reach-tier polling (yt-pubsub-receiver) or one daily read (yt-uploads-reconciler); dormant channels weekly or daily**

- **Type:** rule; schedule
- **Where:**
  - yt-pubsub-receiver §5.1 L40: "A channel whose subscription cannot be established keeps its reach tier by subscribers, polled by yt-uploads-reconciler: Tier 1 ... every 60 minutes, Tier 2 ... every 6 hours, Tier 3 ... every 24 hours"; "Dormant (no video in 30 days): weekly reconciliation"; §8 L145: after 5 failed attempts the channel "keeps its reach tier"; §13 L182.
  - yt-uploads-reconciler §5.1 L45: "Channels sit in the push tier because yt-pubsub-receiver covers them, so each gets one reconciliation every 24 hours, dormant ones included"; the reach tier is only "the secondary sort key and the quota priority"; §5.1 L47 `next_poll_at = run_started_at + 24 h` for every channel; §14 Q3 L200 keeps dormant daily against the rotation policy.
  - CONVENTIONS L45-L49: Tier 1 hourly, Tier 2 6-hourly, Tier 3 daily, dormant weekly.
- **At stake:** a Tier 1 channel whose subscription failed is read once a day instead of hourly, so the freshness promise for it fails silently; quota planning differs by up to 24 units per channel a day.
- **Options:** (1) yt-uploads-reconciler adds reach-tier cadence for channels without a verified lease (reading `yt_subscriptions` or a registry flag) and weekly dormant runs; (2) one daily read for every channel, and yt-pubsub-receiver and the freshness promise are reworded; (3) unsubscribed channels move to a separate poller kind (`rotation`) on the same queue.
- **Blocks:** YT2, YT3, C1.

### AU-101

**`first_sight` jobs on `jobs.yt-video-details-fetcher`: one id or a list, `series_step = backfill` or `origin_kind`, and a `list` bucket that does not exist**

- **Type:** shape; job kind; budget
- **Where:**
  - Consumer: yt-video-details-fetcher reads jobs with "`post_ref` = video id, `due_at`, `attempt`, `series_step`" (§6.1 L86); "ids from a backfill listing carry `series_step = backfill`" (§5.1 L44), which sets priority 5 (§5.1 L50); it calls on bucket `ingest` (§5.2 L59); §14 Q2 L216.
  - yt-pubsub-receiver §6.2 L127: `post_ref` a single id, `due_at`, `series_step: null`.
  - yt-uploads-reconciler §6.2 L133: `"origin_kind": "reconciliation"`, `"post_ref": [<ids>]` (a list of up to 50, §5.2 L64 "carrying the originating kind so details are fetched at the same priority"), no `due_at`, no `series_step`.
  - yt-keyword-search §5.2 L59 and §13 L175: one message per run "listing every video id from the run" (25 terms of 50 results can exceed 50 ids).
  - yt-web-search-bridge §5.2 L61 and §6.2 L126: `origin = web_bridge`, the rule's `source_id`, "the list of video ids"; §7 L137: the ids cost "1 unit per 50 in yt-video-details-fetcher, from the `list` bucket" (CONVENTIONS addendum L279 buckets: `search`, `ingest`, `comments`, `reserve`).
- **At stake:** three producers send shapes the consumer does not parse; backfill first sights are recognised by a field no producer sets, so they run at the wrong priority; quota-governor gets requests on an unknown bucket.
- **Options:** (1) one job per id (`post_ref` string) with an `origin` field (`push`, `reconciliation`, `backfill`, `search`, `web_bridge`) from which the consumer derives priority; (2) `post_refs` lists of at most 50 ids, with `origin`, and the consumer splits them into slots; (3) keep `series_step = backfill` as the backfill marker and require producers to set it.
- **Blocks:** F2, C1, YT2, YT3, YT4, YT8, YT9.

### AU-102

**yt-text-purger's `refresh` jobs: no fetcher accepts the kind, and a refresh as the fetchers and normalize-item work would not reset the 30-day clock**

- **Type:** job kind; shape; rule
- **Where:**
  - yt-text-purger §5.3 L96-L102: `kind = refresh` jobs on `jobs.yt-comments-fetcher` (one per video "listing the due thread ids"), `jobs.yt-replies-fetcher` and `jobs.yt-video-details-fetcher`, carrying `post_ref`, `thread_ids`, `run_id`, `must_finish_by`, `refresh_for_client_ids`; "The fetcher drops a job that is past `must_finish_by`, or whose clients are no longer active"; "The refreshed version reaches ClickHouse through store-writer with new text, new metadata and a new `fetched_at`; that is what resets the clock"; §9 L207 fetchers deduplicate on `post_ref` + `run_id`; §14 Q2 L270 lists the kind and fields as "interface changes to agree".
  - yt-comments-fetcher takes only `comments` jobs, emitted "only" by comment-decay-scheduler (§3 L19, §5.1 L40); an unchanged comment is classified `seen` (§5.2 L55).
  - yt-replies-fetcher takes only `replies` jobs from comment-decay-scheduler (§3 L19, §5.1 L38); yt-video-details-fetcher takes `first_sight`, `metrics` and `ops_force` (§3 L19-L21, §5.1 L44-L46).
  - normalize-item §5.2 L52: a known key "with an equal hash → metrics-only", so an unchanged re-read produces no new version and no new `fetched_at`.
  - Overlaps CF-080 and CF-077 (who may emit into a fetcher's queue); this entry adds the clock-reset dependency.
- **At stake:** every paid refresh either fails on kind or, if accepted, leaves unchanged text with its old `fetched_at` (normalize-item turns an equal-hash re-read into metrics only), so the confirm loop deletes it anyway: quota is spent and the entitlement does nothing.
- **Options:** (1) the three fetchers accept `refresh` with the listed fields, re-emit every returned item, and normalize-item records a refresh as a new version (new `fetched_at`) even when the hash is equal; (2) refresh as a store-side operation: the fetcher reports refreshed ids and store-writer or deletion-propagator updates `fetched_at` without a new version; (3) drop refresh in v1 and delete at 30 days.
- **Blocks:** F2, C4, C6, YT4, YT5, YT6, YT7.

### AU-103

**News backfill: backfill-orchestrator routes it to news-feed-poller, which takes no backfill jobs, and three PRDs send the remainder to web-commoncrawl-scanner, which emits hosts, never article URLs (`found_via = commoncrawl` has no writer)**

- **Type:** job kind; enum; rule
- **Where:**
  - Route table: backfill-orchestrator §5.3 L78 `News site` | "news-feed-poller and news-sitemap-poller (whichever the site has)"; news-feed-poller accepts `kind` = `rotation | ops_force` only (§5.2 L52) and itself says the backfill runs "through news-sitemap-poller or web-commoncrawl-scanner" (§5.1 L48).
  - The remainder through Common Crawl: news-site-resolver §5.1 L41 "(or web-commoncrawl-scanner where there is no sitemap)"; news-sitemap-poller §3 L29 and §5.1 L51 "If coverage is under 90 days, backfill-orchestrator sets `backfill_status = capped` and asks web-commoncrawl-scanner for the remainder"; backfill-orchestrator's steps (§5.2 L54-L60) and route table contain no such request.
  - web-commoncrawl-scanner: "**Backfill on add.** None applies." (§5.1 L44); job kinds `rotation` and `ops_force` (§5.1 L41); it sends hosts as `discovery.hits` of type `site` (§2 L15) and writes "no `raw.items`, no `search.results`" (§6.2 L84), never `article.urls`; past crawls and page bodies are out of scope (§3 L29, L31).
  - news-article-extractor §5.1 L42 orders backfill URLs by `found_via` `sitemap_backfill` and `commoncrawl`; nothing writes `commoncrawl`. search-hit-router writes `"found_by": "web_search"` (§6.2 L124), a value in neither of the extractor's tiers (live: `feed`, `news_sitemap`, `homepage_diff`); the field name itself is CF-022.
  - Hand-over: backfill-orchestrator §5.1 L46 says the poller's scheduler "selects only `done` or `capped` sources"; the news schedulers do not filter on `backfill_status` (news-feed-poller §5.1 L40, news-sitemap-poller §5.1 L41, news-homepage-differ §5.1 L41) and poll at the next tick while the backfill runs (news-feed-poller §5.1 L48, news-sitemap-poller §5.1 L49). Sites with neither feed nor sitemap (news-homepage-differ §5.1 L49) have no backfill route at all.
- **At stake:** the job backfill-orchestrator sends news-feed-poller is a kind it rejects; sites with a short or no sitemap end `capped` with nothing behind the promised remainder; the extractor cannot place `web_search` URLs in a fetch tier.
- **Options:** (1) news backfill goes to news-sitemap-poller only; sites without a usable sitemap end `capped` (`route_cap`), `commoncrawl` leaves the extractor's list, and the news schedulers are exempt from the `done`/`capped` rule; (2) web-commoncrawl-scanner gains a `backfill` kind that lists one host's captured URLs from the index and writes `article.urls` with `found_via = commoncrawl`, requested by backfill-orchestrator; (3) either of these, plus `web_search` added to the extractor's tier list (as live or as backfill).
- **Blocks:** C10, N2, N3, N4, N6, W3, W5.

### AU-104

**Which host errors send `recheck`: news-robots-checker counts 429 and feed or sitemap 404/410; the fetchers back off on 429 and send 404/410 to news-site-resolver as `refresh`**

- **Type:** rule; job kind
- **Where:**
  - news-robots-checker §5.1 L47: "Any news service that receives a 4xx from a host (401, 402, 403, 429, 451, and a 404 or 410 on a feed or sitemap URL) sends `recheck` and stops its batch for that host"; §1 L7 and §2 L13 ("re-checked on every 4xx").
  - 429: news-feed-poller §8 L131, news-sitemap-poller §8 L143, news-homepage-differ §8 L134 and news-article-extractor §5.2 L54 ("429 and 5xx back off") and §8 L140 back off and requeue (CONVENTIONS L100), with no `recheck`; read literally, "Any 4xx other than 404 and 410" (news-homepage-differ §8 L135, news-sitemap-poller §8 L144) and "on every 4xx" (news-feed-poller §3 L22) include 429.
  - Feed or sitemap 404/410: news-feed-poller §8 L132 and §13 L170, news-sitemap-poller §3 L23, §8 L144 and §13 L183 send news-site-resolver a `refresh` and no `recheck`; news-homepage-differ §8 L135 does the same for a homepage 404 or 410; news-site-resolver refreshes on "a feed or sitemap 404 or 410" (§5.1 L40).
- **At stake:** a fetcher built to news-robots-checker's rule stops its batch and asks for a policy re-check on every 429 instead of backing off; one built to its own PRD never sends the feed and sitemap re-checks news-robots-checker sizes its cooldown for.
- **Options:** (1) 429 backs off only and feed or sitemap 404/410 sends `refresh` only; news-robots-checker §5.1 L47 narrows to 401, 402, 403, 451 and challenges; (2) as news-robots-checker says: 429 and feed or sitemap 404/410 also send `recheck`, coalesced by its cooldown; (3) 429 backs off; feed or sitemap 404/410 sends both `refresh` and `recheck`.
- **Blocks:** N1, N2, N3, N4, N5, N6.

### AU-105

**`not_article` feedback: four news PRDs count on news-site-resolver refining URL patterns from extractor outcomes; no message carries them, and the resolver reads none**

- **Type:** rule; job kind
- **Where:**
  - Producer: news-article-extractor §4 L35 (news-site-resolver "receives `not_article` rates for pattern refinement"), §6.2 L125 ("outcome counts to news-site-resolver (`not_article` rate per site)", with no topic, job or table named), §8 L144, §12 L167 ("`not_article` and low-excerpt-length rates per site trigger resolver refresh").
  - Services counting on it: news-homepage-differ §2 L13 (at least 95% accepted, "the rest refine the URL patterns"), §6.1 L93 ("`article.urls` outcomes only through the resolver's pattern refreshes"), §12 L159; news-feed-poller §12 L157; news-sitemap-poller §12 L170; news-site-resolver itself §12 L155.
  - news-site-resolver reads `jobs.news-site-resolver`, `crawl.policies`, `crawl_policies`, `sources`, `decisions`, `clients`, `client_sources` and `news_sites` (§6.1 L75), no outcome; a refresh comes from the 30-day ticker, a canary `degraded` flip or a poller's feed or sitemap 404/410 (§5.1 L40) and repeats steps 3 to 9 (§5.2 L55), where step 6 infers patterns "from feed and sitemap URLs" (§5.2 L50), which a homepage-diff site lacks by definition (§5.4 L69).
  - Further `refresh` senders the resolver does not list: news-homepage-differ on `layout_changed` (§5.2 L60), news-feed-poller on an empty or malformed feed (§5.2 L59), news-comments-fetcher on a rejected Disqus shortname (§8 L139).
- **At stake:** the extractor has nowhere to send the rate, so news-homepage-differ's 95% target and `diff_precision_low` alert have no corrective loop and homepage-diff sites never get patterns.
- **Options:** (1) the extractor sends `refresh` jobs with a `reason` (`not_article_rate`) when a site passes a threshold, and the resolver's refresh gains a step that infers patterns from the site's `news_urls` outcomes; (2) the resolver reads `news_urls` (`status`, `found_via` per `source_id`) on every refresh and no message is added; (3) no refinement in v1: the 95% figure becomes a metric only and the risk lines change.
- **Blocks:** N2, N3, N4, N5, N6, N8.

### AU-106

**Same-canonical copies: `duplicate_canonical` is not a `news_urls.status` value, and a copy that news-dedup's sweep adds has no key of its own**

- **Type:** enum; key
- **Where:**
  - news-dedup §3 L22 (the hourly sweep "adds same-canonical copies the extractor recorded but did not emit"), §5.3 L64 ("it records them as `duplicate_canonical`"; they "are added as members by the hourly sweep from the `news_urls` ledger"), §13 L163; §14 Q3 L169 keeps the ledger-based sweep.
  - news-article-extractor §5.2 L57 ("record both URLs, write nothing new (`duplicate_canonical`)"); `news_urls` `status` = `done | gone | not_article | paywalled | skipped_policy | failed` (§6.3 L129), without `duplicate_canonical`; §13 L177 ("one ledger entry per URL").
  - Key: `news_story_members` is keyed on `idempotency_key` (§6.3 L108, primary key); the extractor's key is `news:article:<canonical_url_hash>` (§9 L152), which a same-canonical copy shares with the origin; the ledger row carries none of the member fields of news-dedup §5.2 L54 beyond `source_id` and `fetched_at` (no title or text hash, language or excerpt).
  - news-dedup §13 L160 ("every copy stays on `raw.items` and reaches normalize-item with `duplicate_of` set") cannot hold for these copies, which never reach `raw.items`.
- **At stake:** the sweep cannot select the copies by status, and inserting one as a member collides with the origin's primary key, so "also published by N outlets" misses every outlet that names the origin as canonical.
- **Options:** (1) add `duplicate_canonical` to `news_urls.status` and key sweep-added members on the copy's `news:url:<url_hash>`, text fields null, `matched_by = canonical`; (2) the extractor emits same-canonical copies to `raw.items` under a per-URL key (the alternative in news-dedup §14 Q3) and the sweep goes; (3) the sweep finds copies as ledger rows whose `canonical_url_hash` belongs to another URL, with a composite member key.
- **Blocks:** F3, N6, N7.

### AU-107

**Disqus comment series: news-site-resolver states eight steps to day 30; comment-decay-scheduler, CONVENTIONS and the fetcher run +6 h, +24 h, +3 d**

- **Type:** rule
- **Where:**
  - news-site-resolver §5.1 L41: "for Disqus sites comments on the decay series (+1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30)".
  - comment-decay-scheduler §5.1 L58 (`news (Disqus)` | news-comments-fetcher | `+6 h, +24 h, +3 d`); CONVENTIONS L269 (same steps); news-comments-fetcher §5.1 L43; news-article-extractor §5.1 L45.
- **At stake:** read as the onboarding contract, the resolver's line promises clients and sizes `news_disqus` for eight fetches per article where the scheduler emits three.
- **Options:** (1) the three-step profile everywhere (the resolver's line follows the scheduler); (2) the longer series for Disqus sites, changing CONVENTIONS L269, the scheduler's profile and the fetcher.
- **Blocks:** N2, N8, C11.

### AU-108

**`site_search`: web-search-perplexity expects jobs from yt-web-search-bridge, web-search-mojeek expects none, and the bridge sends none: it queries both engines itself, Mojeek by default**

- **Type:** job kind; budget; rule
- **Where:**
  - web-search-perplexity: `site_search` jobs "from other services (first user: yt-web-search-bridge, which restricts a query to `youtube.com` and pays from its own `budget_tag`)" (§3 L25); the bridge named as `site_search` producer (§4 L35); kinds `rotation`, `site_search` (§6.1 L85); `search_domain_filter` `["youtube.com"]` only on `site_search` jobs (§5.3 L74); charged to the job's tag, not `perplexity_search` (§5.2 L53, §7 L117, §13 L165).
  - web-search-mojeek: `site_search` out of scope, "yt-web-search-bridge uses web-search-perplexity in v1" (§3 L31, §14 Q4 L172); kind `rotation` only (§6.1 L83).
  - yt-web-search-bridge writes `search.results`, `jobs.yt-video-details-fetcher`, `jobs.yt-channel-resolver`, `cursors`, `service_runs` and no engine job (§6.2 L102); it queries "Mojeek (default) and Perplexity" itself (§3 L21) "through the shared vendor clients" (§5.2 L58; the Mojeek request §5.3 L83), asks allowance on `mojeek_search` and `perplexity_search` (§5.2 L56), defaults government clients to Mojeek only (§7 L139), counts its queries as a share of the engines' 60,000-query plan (§7 L136) and lists the engines as sharing "vendor clients, keys, budget tags" (§11 L167).
  - Overlaps: the budget tag is CF-099; the bridge's `search.results` shape is CF-023; the question is CF-110; the bridge's unarchived responses are AU-029.
- **At stake:** web-search-perplexity's `site_search` path and acceptance test 9 have no producer; the bridge's Mojeek default contradicts Mojeek's "Perplexity in v1"; the bridge's spend lands on the tags the engines cap for their own rotations.
- **Options:** (1) the bridge sends `site_search` jobs to web-search-perplexity (and to web-search-mojeek once `site:` is confirmed), which call, archive and publish to `search.results`, and the bridge reads its results there (search-hit-router no longer the sole consumer); (2) the bridge keeps calling the engines through the shared clients, `site_search` leaves web-search-perplexity, and the bridge gets its own budget tags; (3) as (2), charging the engines' tags with a recorded share.
- **Blocks:** C1, W1, W2, YT9.

### AU-109

**Web-search candidates no resolver can take (`youtube:video:<id>`, legacy YouTube names, `instagram:post:<shortcode>`, `facebook:group:<id>`), the bridge's own `resolve` jobs, and a `handled_by` that search-hit-router never reads**

- **Type:** key; job kind; rule
- **Where:**
  - search-hit-router §5.3 candidate keys: watch URLs as `youtube:video:<id>`, "yt-channel-resolver finds the channel" (L79); `/c/…` and `/user/…` as `youtube:<id or handle>` (L78); `instagram:post:<shortcode>` "when no handle is readable" (L74); `facebook:group:<id or slug>` with `type` `group` (L75). poster-resolver dispatches by `platform` (§5.2 L56) to eight resolvers, none for groups (§3 L23).
  - The resolvers: yt-channel-resolver resolves `youtube:<channel id>` and `youtube:<handle>` through `forHandle` only (§3 L19); ig-account-resolver takes `instagram:<platform_id>` or `instagram:<handle>` (§5.1 L42); fb-page-resolver takes `facebook:<platform_id>` or `facebook:<handle>` (§3 L19), groups are out of scope (§3 L27) and "Groups are never sent here" (§5.1 L42).
  - yt-web-search-bridge sends `resolve` jobs (`origin web_bridge`) straight to `jobs.yt-channel-resolver` for `channel/UC…`, `@handle`, `c/<name>`, `user/<name>` (§5.2 L59, L61; §4 L36); yt-channel-resolver takes `resolve` "from poster-resolver" (§5.1 L44), and poster-resolver inserts the `poster_profiles` row before dispatch (§5.2 L55-L56).
  - yt-web-search-bridge §4 L37 and §13 L182: search-hit-router skips results with `handled_by = yt-web-search-bridge`; search-hit-router's steps (§5.2 L55-L64) contain no such rule, so the same watch URLs would also reach poster-resolver as `youtube:video:<id>` candidates.
- **At stake:** four kinds of web-search candidates reach resolvers that cannot look them up, and the bridge's channel jobs bypass poster-resolver's cache, 180-day rejection memory and `poster_profiles` row.
- **Options:** (1) search-hit-router emits only keys the resolvers accept: a watch URL becomes a `first_sight` for yt-video-details-fetcher (whose answer carries the channel id), shortcode-only and group URLs end `unroutable`, legacy names go to a lookup path added to yt-channel-resolver; (2) the resolvers gain the lookups (video to channel, shortcode to owner, a group path for qualifier rule 8); (3) the bridge's channel references go through `discovery.hits` and poster-resolver like the router's, and search-hit-router honours `handled_by`.
- **Blocks:** C8, W3, FB1, IG1, YT1, YT9.

### AU-110

**Iraqi verification of web results: three engines count on search-hit-router to judge results Iraqi and report yields back; the router judges nothing Iraqi and reports nothing back**

- **Type:** rule
- **Where:**
  - web-search-perplexity §2 L17 (share "Iraqi after search-hit-router's classification"), §5.4 L80 ("`country` is a preference the router verifies"), §10 L141 (`items_new_total` = "first sightings as reported back by search-hit-router"), §12 L150 ("the router's Iraqi-signal check and a per-variant yield metric retire variants"); web-search-mojeek §2 L17, §5.4 L77 ("the router verifies that"), §10 L140 (`variant_yield{variant}` = "results that search-hit-router classifies as Iraqi"), §12 L149; web-gdelt-poller §5.3 L70 ("search-hit-router judges what is Iraqi"), §10 L146 (`iraqi_host_share`, and `unique_domain_share` "from search-hit-router"), §12 L158.
  - search-hit-router §5.4 L89: it gets no "proof that a result is Iraqi: poster-resolver and the qualifier judge that" (also §12 L173); its classification (§5.3 L72-L85) uses `.iq` only inside the news-like rule; it writes `discovery.hits`, `article.urls`, `service_runs`, `review_queue` and its DLQ (§6.2 L97-L134), keeps yield as its own metrics (`engine_unique_yield{engine}`, `variant_yield{engine,variant}`, §10 L164) and proposes "metrics only in v1" for any feedback (§14 Q4 L197).
- **At stake:** the engines' section 10 metrics and Perplexity's variant-retirement rule rest on a classification and a report-back that no service produces.
- **Options:** (1) the router owns web yields: the engines drop `variant_yield`, `iraqi_host_share`, `unique_domain_share` and the reported-back `items_new_total`, and variant retirement reads the router's metrics; (2) the router adds an Iraqi-signal check (`.iq`, script and language of the snippet, GDELT `hints`) and a per-result feedback record the engines read; (3) Iraqi share is measured downstream (qualifier, keyword-matcher) and variant retirement is a manual pilot decision.
- **Blocks:** W1, W2, W3, W4.

### AU-111

**The `resolve` job: poster-resolver's job has no `client_ids` or seed-list flag, which every resolver reads; a vendor flag that is off is handled three ways; li-org-resolver re-keys the candidate; news-site-resolver names other producers**

- **Type:** job kind; key; enum
- **Where:**
  - (a) Fields: poster-resolver's job is `{"job_id","kind":"resolve","candidate_key","platform","platform_id","handle","hit_url","origin","reply_to":"jobs.poster-resolver","attempt","sample_posts":20}` (§5.3 L67), without `client_ids`. The resolvers read `client_ids` from it: fb-page-resolver §5.1 L42 and §5.2 L55 (token of the first client in `client_ids`); ig-account-resolver §5.1 L42 and §5.2 L57 (calling account of the first client); x-user-resolver §5.1 L41 and §5.2 L54 (plan gate drops government clients); tt-user-resolver §5.1 L41 and §5.2 L51 (`gov_excluded`); li-org-resolver §5.1 L44 (`client_ids`, `seed_list`) and §5.2 L52-L53; tg-channel-resolver §5.2 L52 (`candidate`, `client_ids`, `hit_item_keys`); yt-channel-resolver §5.1 L44. ig-account-resolver also needs seed-list membership to send a not-returned candidate to review (§8 L146), which no field carries; poster-resolver derives membership itself "from `keywords` and `clients`" (§5.2 L58).
  - (b) Key: li-org-resolver computes `candidate_key = linkedin:org:<handle>` (§5.2 L50); poster-resolver keys candidates `<platform>:<platform_id>` or `<platform>:<handle>` (§3 L22; CONVENTIONS L281), and search-hit-router issues `linkedin:<slug>` (§5.3 L81).
  - (c) Flag off: poster-resolver calls `tt-user-resolver`, `li-org-resolver` and `tg-channel-resolver` only when their flag is not `off`, "otherwise the candidate is marked `unresolvable: route_off`" (§5.2 L56); tt-user-resolver expects the job and returns `skipped_flag_off`, "poster-resolver keeps the candidate waiting" (§5.2 L53); li-org-resolver expects it and emits `resolution = unresolved, reason = vendor_route_off` (§5.2 L53).
  - (d) Answer content: poster-resolver expects "up to 20 recent post texts" (§5.3 L70) and computes `lang_share` and `country_signals` itself (§3 L24, §5.2 L58); fb-page-resolver reads no posts ("the 40% Iraqi-language signal comes from elsewhere", §3 L28); yt-channel-resolver: language share, activity and spam "come from the item pipeline" (§3 L30); news-site-resolver computes language share and Iraqi signals itself (§5.2 L52) and discards sampled titles (§5.4 L69).
  - (e) Producers: news-site-resolver's `resolve` jobs are "produced by search-hit-router, web-commoncrawl-scanner, web-gdelt-poller, the seed-list flow and the qualifier" (§5.1 L38; §3 L17), never poster-resolver; poster-resolver dispatches to it (§3 L23); search-hit-router (§4 L37) and web-commoncrawl-scanner (§4 L35) send sites through poster-resolver, and web-gdelt-poller emits no candidate at all (§6.2 L91-L92).
  - Where the answer goes (`jobs.poster-resolver` or `poster.profiles`) is CF-012; `resolve` as a kind is CF-077.
- **At stake:** from poster-resolver's job the Facebook and Instagram resolvers have no token to call with and the X, TikTok and LinkedIn government gates nothing to check; a LinkedIn answer carries a key poster-resolver never issued; an amber candidate with its flag off ends in three different states; the qualifier's language and Iraqi-signal inputs are computed twice or not at all.
- **Options:** (1) one resolve-job schema in F2 with `client_ids`, `seed_list` and the issued `candidate_key` echoed unchanged; amber resolvers are called with the flag off and answer `route_off`; resolvers return post texts and poster-resolver computes the shares; (2) as (1), but each resolver computes shares and signals and poster-resolver forwards them; (3) resolvers read `client_ids` and seed-list membership from poster-resolver's `poster_profiles` row by `candidate_key`, and poster-resolver keeps its flag-off rule.
- **Blocks:** F2, C8, C9, FB1, IG1, VTT3, X2, VLI2, VTG2, YT1, N2.

### AU-112

**Refreshing registered sources' profiles: TikTok creators have no refresher, li-org-resolver waits for qualifier jobs the qualifier never sends, and Instagram's first due time needs a cursor row nobody writes at registration**

- **Type:** job kind; writers
- **Where:**
  - TikTok: tt-video-stats-refresher leaves "creator follower counts" to tt-user-resolver (§3 L29); tt-user-resolver "has no scheduler and no rotation of its own" (§5.1 L41) and asks who refreshes them, proposing poster-resolver (§14 Q2 L170); poster-resolver is "Event-driven, no rotation" (§5.1 L46).
  - LinkedIn: li-org-resolver "never polls on its own" and expects `kind: refresh` from qualifier "when a dormant source gets a new hit, when a source reaches its 90-day decay review, or when a source retires at 180 days" (§5.1 L44; cadence §14 Q2 L165); the qualifier writes `registry.decisions`, `decisions`, `review_queue` and an n8n webhook (§6.2 L80-L87) and no job; li-company-posts-poller expects "re-resolution by li-org-resolver" after `source.events` `updated` (§8 L142), and li-org-resolver reads no `source.events` (§6.1 L75).
  - Instagram: ig-account-resolver keeps `refresh_due_at` in its own `cursors` row and counts "the candidate resolution that registered a source" as the first refresh (§5.1 L46), but resolves candidates before any `source_id` exists (§5.1 L42) and reads no `source.events` (§6.1 L98); registry-writer keeps "No cursors" (§6.3 L103).
  - The rest run their own loop under two kind names: `rotation` (fb-page-resolver §5.1 L42, L46; x-user-resolver §5.1 L41, L47; yt-channel-resolver §5.1 L44; ig-account-resolver §5.1 L42) or `refresh` (tg-channel-resolver §5.1 L44; news-site-resolver §5.1 L38, L40); three ask whether poster-resolver owns this instead (fb-page-resolver §14 Q1 L189, x-user-resolver §14 Q6 L196, yt-channel-resolver §14 Q5 L200), which poster-resolver's PRD does not take on.
- **At stake:** TikTok creators' and LinkedIn pages' follower counts, and with them reach tiers, are never refreshed; Instagram accounts get no first due time unless the scheduler also scans for sources without a cursor row.
- **Options:** (1) every resolver runs its own 30-day loop over its registered sources: tt-user-resolver and li-org-resolver gain one, ig-account-resolver seeds missing cursor rows from `sources`; (2) one refresh scheduler (poster-resolver or registry-writer) sends `refresh` jobs to all eight resolvers and the per-resolver loops go; (3) the qualifier's daily sweep emits `refresh` jobs for the sources it reviews, as li-org-resolver expects, with the others as (1).
- **Blocks:** C7, C8, C9, FB1, IG1, VTT3, VTT6, X2, VLI2, VLI3, VTG2, YT1, N2.

### AU-113

**Budget stretch: quota-governor publishes `stretch_factor` for each amber poller to apply; the pollers say the governor stretches them and read no factor, and tg-channel-posts-poller stretches in a fixed order instead**

- **Type:** rule; budget
- **Where:**
  - quota-governor §5.1 L51: "the governor publishes `stretch_factor` ... Each amber poller sets its interval to `min(tier_interval × stretch_factor, 24 h)`"; the factor is a field of the `budgets` row (§6.2 L104); §13 L163.
  - The pollers place the stretch in the governor and name no factor: fb-group-posts-poller §5.1 L46 ("quota-governor may stretch the Tier 1 and Tier 2 intervals"); tt-profile-videos-poller §5.1 L49 ("it may stretch"); li-company-posts-poller §7 L132 ("quota-governor stretches shortened intervals back to 24 hours"); ig-keyword-search §5.1 L49. tg-channel-posts-poller §5.1 L52: "the governor stretches intervals: backfill jobs pause first, then views refreshes, then Tier 2, then Tier 1", and §13 L185 (Tier 2 before Tier 1).
  - README L179 (decision 2): "amber intervals stretched by a factor, never beyond 24 hours".
- **At stake:** with each side leaving the stretch to the other, no amber interval is lengthened and the 80% brake works only through denials; Telegram's ordered stretch cannot be expressed as one factor.
- **Options:** (1) pollers read `stretch_factor` from `budgets` (through the SDK scheduling kit) and apply the formula, Telegram included; (2) the governor answers allowance requests with a `wait_until` at the stretched due time and pollers keep their intervals; (3) as (1), with a factor per tier so Telegram's order fits.
- **Blocks:** F5, C1, VFB2, VIG1, VTT4, VLI3, VTG3.


## Appendix. Candidates the audit passes noted for another category


Seen while auditing; they disagree between PRDs but are not assumptions about a shared service's own behaviour, so they belong to the A, B or C consolidation.

- C · decision value spelled `tier change` (`ig-account-resolver §13 L183`, "the qualifier fixture emits a `tier change`") against `tier_change` (`qualifier §8 L106`, `registry-writer §5.2 L53`); same spelling split as `source.events` in the C entries.
- C · vendor of an amber Telegram channel source: `telemetrio` (`tg-channel-resolver §4 L34`) while its posts are read through `TG_POSTS_ACTOR` Actors (CONVENTIONS L280); vendor-value question, CF-097.
- A · `source.events` written by a service other than registry-writer: `ig-hashtag-search §5.1 L57` tells the client "through `source.events` (`fallback_on` when the amber route is on, otherwise `updated` with a `budget_wait` note)"; `x-user-timeline-poller §5.1 L40` (`tier change`); writers of `source.events` belong to the A entries.
- A · `registry.decisions` message shape: the canary names the type in `"action": "health_change"` with `scope`, `reason`, `evidence` and an object `fallback` (`source-health-canary §6.2 L102`, `§14 Q1 L161`), the qualifier in `"decision": "add"` (`qualifier §6.2 L84`), and registry-writer's `health_change` carries "`platform`, `route`, `vendor`, `health`, `fallback`" (`registry-writer §5.2 L54`).
- A · `item.metrics` message shapes differ (flat `item_idempotency_key` + `observation` in fb-reactions-fetcher and yt-video-details-fetcher, nested `envelope` + `observation{label}` in tt-video-stats-refresher), and store-writer asks whether `item.metrics` carries `retention_class`, `created_at` and `source_id` (`store-writer §14 Q5 L185`); A entries.
- A · `deletions` shapes from fetchers (for example `fb-post-comments-fetcher §6.2 L125` `{"platform", "kind", "idempotency_key", "parent_platform_id", "reason", "service", "job_id", ...}` and `yt-comments-fetcher §6.2 L136` (`idempotency_key`, `parent_video_id`, reason, `job_id`, `detected_at`)) lack `scope` and use `idempotency_key` instead of the target of `deletion-propagator §5.4 L80`; `deletion-propagator §14 Q2 L172` asks for alignment; A entries.

- fb-keyword-search (§13 L174), ig-keyword-search (§5.1 L51) and li-post-search (§5.1 L48) expect `backfill` jobs, and tt-keyword-search (§5.1 L44) and tt-hashtag-feed-poller (§5.1 L48) backfill themselves, while backfill-orchestrator sends keyword and hashtag rules none, `done` at once (§5.3 L79): assumptions about a shared service, for the shared-assumption audit.
- ig-mentions-fetcher (§5.1 L49) and ig-webhook-receiver (§5.1 L45) expect a mentions backfill job; backfill-orchestrator routes an Instagram account to ig-account-media-poller only (§5.3 L70), one job per source (§2 L15): shared-assumption audit.
- li-own-comments-fetcher (§5.1 L52), li-post-comments-fetcher (§5.1 L54) and li-notification-receiver (§5.1 L48) expect backfill-orchestrator to emit one comments job per backfilled post, against CONVENTIONS L278 and backfill-orchestrator §5.1 L48 (one `once` fetch through comment-decay-scheduler): shared-assumption audit, with CF-080.
- `sources.health` writers for suspended X accounts: x-user-timeline-poller §8 L151 sets `blocked` itself, x-compliance-sync §5.3 L83 sets it through the canary hook and back to `ok`, x-full-archive-search §8 L148: section 2 (tables) (column writers).
- Author hashing: the SDK `author_hash` helper (x-compliance-sync §11 L170), one keyed hash for all platforms (tt-video-comments-fetcher §5.3 L68), Telegram's `author_ref` with its secret in `vendor_keys` (tg-discussion-receiver §5.2 L63, §6.1 L110): CF-069.
- Job kinds `resolve` and `push` added to the SDK schema (ig-account-resolver §11 L165, §14 L193; ig-webhook-receiver §11 L162), fb-backfill's job field `reason` (`add`, `ops`, `client`; §5.1 L41) where backfill-orchestrator emits kind `backfill`: CF-077.
- `jobs.ig-own-comments-fetcher` kind `replies` (ig-own-comments-fetcher §3 L19) with no producer: comment-decay-scheduler's `ig_own` profile says "field expansion; no job" (§5.1 L50): section 3 (keys, jobs, values) (job kinds).
- Reposts of member posts on LinkedIn: `linkedin_48h` meanwhile (li-company-posts-poller §7 L133) against `vendor_agreed` (li-post-search §6.2 L92): CF-104.
- `deletions` from fb-reactions-fetcher and fb-client-webhook-receiver have no shape (fb-reactions-fetcher §6.2 L126; fb-client-webhook-receiver §5.2 L56), fb-post-comments-fetcher's deletion event carries no `platform_id` (§6.2 L125; its comment records have `platform_id` null, L107), against deletion-propagator's minimum shape (§14 L172): CF-020.
- yt-pubsub-receiver puts any channel with a verified lease in the push tier, "client-owned or not" (§5.1 L40), against CONVENTIONS L247 (rule 6: "push for client-owned"): section 3 (keys, jobs, values) (push-tier rule).
- yt-video-details-fetcher anchors `metrics` steps on `publishedAt` (§5.1 L45), comment-decay-scheduler on first-seen time (§5.1 L60): CF-081.
- normalize-item maps Perplexity and Mojeek results "forwarded by search-hit-router" (§3 L22, §5.3 L73), which writes only `discovery.hits` and `article.urls` (search-hit-router §6.2 L97-L134): CF-110.
- raw-archiver's required `raw.items` envelope fields (raw-archiver §5.4 L86): CF-004; store-writer letting `item.metrics` producers omit `retention_class`, `created_at` and `source_id` (store-writer §14 L185): CF-019; search-hit-router's expectation that every producer writes `search.results/v1` (§1 L7, §5.4 L89): CF-023.
- `retention_classes` gaining `content_ttl` and `row_ttl` (store-writer §14 Q1 L181; aggregator §6.1 L74): section 2 (tables) (`retention_classes` columns).
- `items.analysis` identity: store-writer keys `analysis` on `item_id, model` (§5.3 L61, L67), the analysis services on `item_id` + `task` + `model_version` (analysis-sentiment §6.2 L89, analysis-topics §6.2 L93): shared services on both sides, section 1 (topics) and the shared-assumption audit.
- raw-archiver expects `raw.replay` consumers to deduplicate on `item_id` (raw-archiver §9 L146); the consumer is normalize-item, a shared service: shared-assumption audit.
- comment-decay-scheduler expects every comment fetcher to report reply candidates in its completion report (§5.2 L78): CF-089.
