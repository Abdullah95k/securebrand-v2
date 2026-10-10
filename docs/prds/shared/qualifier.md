# qualifier

**Platform:** Shared · **Route:** shared · **Lane:** Registry · **Owner:** Registry backend engineer · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The registry is the product. Every poller, comment fetcher and backfill works off the `sources` table, and every row in it costs money on a rotation for as long as it stays there. Whether a resolved poster becomes a source, at which tier, under which route and retention class, for which clients, is the most consequential decision the platform makes, and it is made thousands of times a month. Left to each discovery service it would be made ten different ways; left to humans, the registry would stop growing the day ops got busy.

`qualifier` is the one place the ten qualifier rules are applied, in order, to every `poster.profiles` message, and the one place that remembers what was rejected so a candidate is not re-argued every week. It also runs the registry's slow clocks: dormancy after 30 days without a post, decay after 90 days without hits, retirement after 180.

Without it: no automatic growth, no consistent protection of individuals (rule 7 is the compliance line for TikTok, X and Meta), no cap on what a client token or vendor budget can carry, and no audit trail explaining why a source is watched.

## 2. Objective (the end state this service delivers)

Every `poster.profiles` message receives exactly one decision on `registry.decisions` within 5 minutes, traceable to the rule that produced it. Borderline cases reach a human within the same 5 minutes and are closed, by a person or by the 24-hour default, within a day. Every registered source carries the tier, route, vendor, retention class and client list the rules imply, and no individual ever becomes a source.

Targets: 99% of profiles decided within 5 minutes; 100% of decisions carry `rule_hit`; 100% of cards closed within 24 hours (by default rejection if nobody answers); the share of decisions that are reviews is to be measured in the pilot and is the main tuning signal.

## 3. Scope

### In scope
- Consuming `poster.profiles` and applying rules 1 to 10 in order, stopping at the first rule that decides.
- Emitting `registry.decisions`; writing `decisions` (every decision, rejections with a 180-day expiry) and `review_queue`.
- The n8n review card (Telegram or Slack), its callback, the 24-hour default reject.
- Per-client thresholds: `clients.qualifier_config` jsonb overriding defaults within the bounds in section 7.
- The daily sweep over `sources` for rule 3 (dormant), rule 9 (decay, retirement) and promotion back from dormant.
- Manual candidates (`origin: manual`) from ops or clients: rules 2, 4 and 10 are skipped because the choice is explicit; rules 1, 5, 6 and 7 still apply.
- Groups (rule 8).

### Out of scope
- Resolving identities (`poster-resolver`), writing `sources` (`registry-writer`), budget accounting (`quota-governor`), the backfill (`backfill-orchestrator`).
- Keyword and client management screens; the qualifier only reads `keywords` and `clients`.

## 4. Users and consumers

- `registry-writer`: the consumer of `registry.decisions`.
- Ops reviewers and, for their own candidates, client admins: receive review cards through n8n.
- `poster-resolver`: reads `decisions` for the 180-day rejection memory.
- `quota-governor`: answers capacity checks for rule 5.
- Account managers: the `decisions` table explains why a source exists.

## 5. How it works

### 5.1 Trigger and rotation

Three triggers. First, a `poster.profiles` message (event-driven, no rotation). Second, a review callback from n8n or the 24-hour timeout on a `review_queue` row (checked every 15 minutes). Third, a daily sweep over `sources` at 03:00 Baghdad time that applies rules 3 and 9 and promotes dormant sources that posted again. No backfill: earlier profiles are not re-read; sources that pre-date deployment enter the sweep on its first run.

### 5.2 Step by step

For each profile, build the context (profile, matching `keywords`, the clients whose keywords hit, each client's `qualifier_config`, any open `review_queue` row) and run the rules in order; the first terminal decision ends the run.

1. Type (rule 1). Individual (as classified by `poster-resolver`) → jump to rule 7. `unresolvable` → `reject`, remembered 180 days.
2. Iraqi signals (rule 2). Count: location naming an Iraqi city or governorate, a +964 number, an .iq domain or Iraqi outlet link, at least 40% Iraqi Arabic or Sorani on the last 20 posts, membership of a client seed list. Two or more → continue. One → `review`. None → `reject`.
3. Activity (rule 3). No post in 30 days → still added, but with `tier = dormant` (weekly).
4. Spam (rule 4). More than 50 posts a day with over 60% duplicate text → `reject`. Default avatar on an account under 30 days old → `review`.
5. Route cap and budget (rule 5). Ask `quota-governor` for a capacity check on the route the source would use: PPCA Pages per client token, YouTube quota share, vendor monthly spend per source. Over the cap → `queued` (not written to `sources`); the queue is re-evaluated daily by reach and the client is told through n8n.
6. Tier and retention class (rule 6). Tier 1 at 100,000 followers or more or on a client priority list; tier 2 from 10,000 to 99,999; tier 3 below 10,000; `push` when `owned_by_client`. Retention class by route: `meta_on_request` (Facebook and Instagram green), `x_24h_sync`, `youtube_30d_text`, `linkedin_48h`, `news_excerpt`, `vendor_agreed` (every amber route). → `add`.
7. Individuals (rule 7). Never a source: `mention_only`, carrying only the `author_hash`; the matched post stays a mention; no backfill. A cached individual whose followers now cross the creator threshold (TikTok 2,000, X 500) is re-run from rule 2.
8. Groups (rule 8). `account_type = group` (Facebook, amber only, `FB_VENDOR_ROUTE` not `off`) → `add` with `route = amber`, `vendor` from the flag, `retention_class = vendor_agreed`; the poster arrives as its own profile and is qualified separately.
9. Decay (rule 9). Runs in the sweep: `last_hit_at` and `client_sources` older than 90 days → `tier_down` (1→2, 2→3, 3→dormant); 180 days → `retire`. Rejected candidates stay in `decisions` 180 days.
10. Review (rule 10). Every `review` opens a `review_queue` row and posts the n8n card; the callback yields `add` (with the reviewer's tier), `reject` or `mention_only`; no answer in 24 hours → `reject`, reason `review_timeout`.

Each decision is written to `decisions` (`decision_id`, `candidate_key`, `rule_hit`, `decision`, `reason`, `client_ids`, `payload`, `expires_at`) and published to `registry.decisions` in the same transaction (outbox column `published_at`).

### 5.3 The call it makes

No platform call. Internal calls: `quota-governor` `POST /capacity` with `{route, platform, vendor, client_id, tier}`, answered with `{fits: true|false, reason, queue_position}`; n8n webhook `POST /qualifier/review` with the card payload (candidate summary, signals found, matched keywords, client, three buttons: Approve as tier 1/2/3, Reject, Mention only); ClickHouse query in the sweep: `SELECT source_id, max(published_at) FROM items GROUP BY source_id` restricted to sources not in `retired`.

### 5.4 What it gets

From `poster.profiles`: every field listed in the `poster-resolver` PRD. From the capacity check: whether the route can carry one more source for this client. From n8n: the reviewer's choice, identity and time. Not obtained: anything about individuals beyond the hash, follower count and verified flag; comment text; the content of matched posts (only keyword ids).

## 6. Inputs and outputs

### 6.1 Reads
- Topic `poster.profiles`.
- Tables: `keywords`, `clients` (seed lists, priority lists, `qualifier_config`), `client_sources`, `sources` (sweep), `decisions`, `review_queue`, `budgets` (through the governor).
- ClickHouse `items` in the sweep.

### 6.2 Writes
- Topic `registry.decisions`, partition key `candidate_key` (or `source_id` for sweep decisions):

```json
{"message_id":"01M48BA9VGH96Q50HZX9S88TJC","produced_at":"2026-10-06T10:14:30Z","service":"qualifier","schema_version":1,"decision_id":"01M48B9AKGRHAJW420WYJS5QK3","candidate_key":"instagram:17841400000000000","source_id":null,"decision":"add","rule_hit":6,"reason":"iraqi_signals=2;followers=48200","origin":"discovery","platform":"instagram","source_type":"account","platform_id":"17841400000000000","handle":"baghdad_eats","url":"https://instagram.com/baghdad_eats","display_name":"Baghdad Eats","route":"green","vendor":null,"tier":2,"retention_class":"meta_on_request","client_ids":["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],"owned_by_client":false,"followers":48200,"country_signals":{"iraqi_place":true,"phone_964":false,"iq_domain":false,"outlet_link":false,"seed_list":false},"lang_share":{"ar_iq":0.70,"ckb":0.00,"ar_msa":0.20,"en":0.10},"added_by":"qualifier","review":null,"expires_at":null}
```

Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

- Tables `decisions`, `review_queue`; n8n webhook for cards and client notifications.

### 6.3 State
- `decisions` (with `expires_at` for rejections), `review_queue` (`status`, `opened_at`, `deadline_at`, `reviewer`, `answer`).
- `service_runs`: last sweep time and counts.
- Per-client thresholds in `clients.qualifier_config`.

## 7. Limits, quotas and cost

The qualifier spends nothing on platforms. Its cost is one Postgres transaction per profile, one capacity call per rule-5 check, and one ClickHouse aggregate a day. At 1,000,000 items a day the profile rate equals the discovery rate, to be measured in the pilot; one replica suffices.

Thresholds and bounds (defaults from CONVENTIONS; a client may override within the bound): `iraqi_signals_required` 2 (1 to 3); `lang_share_min` 0.40 (0.30 to 0.80); `dormant_days` 30 (fixed); `spam_posts_per_day` 50 (20 to 200); `spam_duplicate_share` 0.60 (0.40 to 0.90); `tier1_followers` 100,000 and `tier2_followers` 10,000 (raise only); `creator_followers_tiktok` 2,000 and `public_figure_followers_x` 500 (raise only: lowering would turn individuals into sources); `review_timeout_hours` 24 (fixed); `decay_days` 90 and `retire_days` 180 (shorten only).

Rule 5 inherits the fact-sheet caps: PPCA 4,800 calls × engaged users per 24 hours per token and about 600 ranked posts per Page per year; YouTube 10,000 units a day; vendor monthly budgets as entered in `budgets`.

## 8. Failure handling and fallback

- `quota-governor` unreachable: the capacity check is retried with the standard backoff (30 s to 15 min); the profile is not decided until an answer arrives, so a source is never added past a cap.
- n8n unreachable: the `review_queue` row is still written and the card re-sent every 15 minutes; the 24-hour clock starts at `opened_at`, not at delivery.
- Duplicate profile (replay or `cached: true` re-emit): an existing decision for the `candidate_key` is re-published unchanged unless followers crossed a tier boundary, which produces `tier_change`.
- `schema_unknown: true` profiles go to review with the raw fields attached.
- ClickHouse unavailable: the sweep is skipped and retried the next hour; no decay decision is made from stale data; `sweep_missed` alerts after two misses.
- A profile that throws 5 times goes to `dlq.qualifier` with an alert.

## 9. Non-functional requirements

- Throughput: one replica at full scale; horizontal scaling by `poster.profiles` partitions if needed.
- Latency: decision within 5 minutes for 99% of profiles.
- Idempotency: `decision_id` is deterministic for the same `candidate_key` and profile `resolved_at`; replays produce no second `add`.
- Security: review cards never show an individual's data (individuals are never reviewed, only mention-only); the n8n callback is signed with a secret from Supabase Vault; thresholds are editable only by ops or a client admin for their own client.
- Compliance: an amber route is never assigned to a candidate whose only interested client is a government client; the candidate is `queued` with reason `amber_excluded_government` and the account manager is told.

## 10. Metrics and alerts

`profiles_consumed_total`, `decisions_total{decision,rule_hit,platform}`, `decision_latency_seconds`, `review_open`, `review_timeouts_total`, `queued_over_cap{route}`, `sweep_duration_seconds`, `sweep_changes_total{kind}`, `jobs_total{status}`, `dlq_total`. Alerts: `qualifier_behind` (lag above 5 minutes), `review_backlog` (more than 50 open cards older than 12 hours), `queued_growth` (queue growing for 7 days on one route: a budget decision is needed), `sweep_missed`, `qualifier_dlq`.

## 11. Dependencies

- Upstream: `poster-resolver`; `keyword-matcher` (hit context in the profile).
- Sideways: `quota-governor` (capacity), n8n (cards, notifications), ClickHouse (sweep), `clients` and `keywords` tables.
- Downstream: `registry-writer` (decisions), `backfill-orchestrator` and the pollers (through `source.events` once written).
- Flags: `FB_VENDOR_ROUTE`, `IG_VENDOR_ROUTE`, `TT_VENDOR_ROUTE`, `LI_VENDOR_ROUTE`, `TG_VENDOR_ROUTE` decide whether an amber `add` is possible.

## 12. Risks and mitigations

- Too many reviews drown ops: the share of reviews is measured from day one, thresholds are tuned per client, and the card carries enough context to decide in seconds.
- Default reject after 24 hours loses good sources: a timeout rejection is re-opened on the next hit from a client seed list, and the reason is visible to the account manager.
- The sweep demotes a source during a quiet month before a campaign: client priority lists exempt a source from decay; `tier_down` is reversible by a manual add.
- A client lowers thresholds to pull individuals in: the bounds in section 7 are enforced in code, not in the UI.

## 13. Acceptance criteria

1. A profile with two Iraqi signals, 48,200 followers, 22 posts in 30 days and no spam signal produces one `add` decision with `tier = 2`, `rule_hit = 6`, `retention_class = meta_on_request`.
2. A profile with one Iraqi signal opens a `review_queue` row and an n8n card within 5 minutes; with no answer, a `reject` with reason `review_timeout` is published 24 hours after `opened_at`.
3. A profile with `individual: true` produces `mention_only` carrying only `author_hash`, no handle, and no `sources` row afterwards.
4. A profile with no Iraqi signal produces `reject`; the same candidate re-emitted 100 days later is answered from `decisions` without a review; 181 days later it is evaluated again.
5. A Facebook group profile with `FB_VENDOR_ROUTE = sociavault` produces `add` with `route = amber`, `vendor = sociavault`, `retention_class = vendor_agreed`; with the flag `off` it produces `reject` with reason `route_off`.
6. When `quota-governor` answers `fits: false`, the decision is `queued`, no `sources` row is created, and a client notification is sent through n8n.
7. A source with `last_hit_at` 91 days ago and no client interest receives `tier_down` in the next sweep; at 181 days it receives `retire`; a source on a client priority list receives neither.
8. A dormant source with an item published in the last 30 days is promoted to its reach tier in the next sweep.
9. A client config setting `creator_followers_tiktok` to 1,000 is rejected by the API with a bounds error; setting it to 5,000 is accepted.
10. Replaying 1,000 `poster.profiles` messages produces zero duplicate `add` decisions.

## 14. Open questions

- Whether client admins may answer review cards for candidates found through their own keywords, or only ops.
- Where the Iraqi outlet and city/governorate lists live (shared with `poster-resolver`).
- Whether `queued` candidates appear in the client app with their queue position.
