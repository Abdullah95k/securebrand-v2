# source-health-canary

**Platform:** Shared · **Route:** shared · **Lane:** Support · **Owner:** Platform reliability engineer · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The worst failures of a listening platform are quiet. A rate limit is loud: the fetcher sees a 429 and backs off. But a vendor that starts answering 200 with an empty list, a platform that silently stops returning a Page's posts, or a feed that returns three items instead of thirty all look like success. Every job finishes `ok`, the dashboards stay green, and the data simply stops growing. The first person to notice is a client asking why a competitor's Page has been silent for two days.

source-health-canary asks the one question the fetchers cannot ask themselves: "does a source that we know is active still return data on this route?" It asks every few minutes, per route, with known-active sources, so "nothing new" can be told apart from "route broken". When a route breaks it flags it, switches to a declared alternate route where one exists and its flag is on, tells the humans, and moves back when the primary recovers.

Without it, degraded vendors are found by clients, amber fallbacks are never used, and a recovered primary route is never returned to, so the product stays on the dearer, less clean route for good. It also holds one line: it never gets around a block.

## 2. Objective (the end state this service delivers)

Every route (platform, route class, vendor) carries a `health` that matches reality within one 15-minute window. Where an alternate exists and its flag is on, fallback and recovery are automatic and recorded; where none exists, the route stays `degraded` or `blocked` and a human is told through n8n.

Target: a route whose empty-200 rate exceeds 5% in 15 minutes is `degraded` by the end of that window plus one canary cycle; 100% of health flips have an audit row, a `source.events` message and an alert; no route flips more than once per 15-minute window.

## 3. Scope

### In scope
- The `canary_targets` table and its upkeep (candidate proposals, quarantine of stale targets).
- Active canary fetches per route; yield checks; empty-200 rate; 401, 403 and 5xx patterns; passive counters read from the SDK's per-call route metrics.
- The health state machine; `health_change` decisions to registry-writer, which publishes `fallback_on`, `fallback_off` and `updated` on `source.events`.
- Recovery probing back to the primary; alerts through n8n.

### Out of scope
- The fetches that produce data (every poller and fetcher); canary payloads are discarded, never written to `raw.items`.
- Switching flags by hand and buying vendors (ops).
- Heartbeats of push receivers (each receiver reports its own; a later version may read them).
- Any account, token, proxy or IP rotation: never built.

## 4. Users and consumers

- **Ops and the on-call engineer** receive alerts and approval cards and can pause a target or force a probe.
- **Account managers** are told when a client's source changes provenance through fallback.
- **Consumers of its decisions:** registry-writer (applies `health`, emits events); every poller and fetcher reads `health` and route at the start of each job; quota-governor (canary calls ride the route's budget tag); comment-decay-scheduler (holds steps while a source is degraded or blocked).

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A leader-elected loop (Postgres advisory lock) runs one canary cycle per route. The period is an environment variable, per route, set so that at least three cycles fall in each 15-minute window (a period of 5 minutes or less); metered routes (YouTube, X) may use a longer period and rely more on the passive counters. Targets are taken round-robin, so every active target is fetched once per cycle.

**Targets.** A target is a registered source (Page, channel, creator, company page, site; never an individual) that is known to post at least daily, with the call to make and the number of items to expect. Ops picks targets from candidates the canary proposes: Tier 1 sources that returned a new item at every poll over the last day. Several targets per route are needed so one dead source cannot flip a route.

**Alternates.** Stored per target in `canary_targets` (`alternate_route`, `alternate_vendor`, `flag_name`), filled from the service PRDs. Clear today: TikTok TikHub and EnsembleData for each other (`TT_VENDOR_ROUTE`), Facebook amber SociaVault and ScrapeCreators for each other (`FB_VENDOR_ROUTE`), Telegram channel-post actors tugelbay and sovereigntaylor for each other (`TG_POSTS_ACTOR`). Facebook Page feeds, X, YouTube, LinkedIn, news and web search have no flagged alternate: they go `degraded` and alert.

**Recovery.** While a route is `degraded`, `fallback` or `blocked`, the primary is probed with its canary targets at an interval that backs off exponentially from the normal period up to 60 minutes (the Tier 1 interval).

### 5.2 Step by step

1. Select due targets; ask quota-governor for allowance under the route's own budget tag; on deny or wait, skip the target and count it (a denied canary never flips health).
2. Fetch through the route's real adapter in canary mode (same code path, read-only, small page). Keep only counts, newest timestamp, latency and status.
3. Classify the outcome (5.3) and write it to the rolling window.
4. Every cycle, evaluate each route against the rules in 5.3 and the passive counters.
5. On a state change, write a `health_change` decision to `registry.decisions` and an n8n alert; write the audit row first, so a replay changes nothing.
6. While on fallback or `blocked`, run recovery probes; on a clean window, write the reverse decision.

### 5.3 The call it makes

The calls are the routes' own cheapest read, for example Graph `/feed` with a small `limit` on a known-active Page, YouTube `playlistItems.list` on an uploads playlist (1 unit), X user timeline with `since_id`, a TikTok user-posts call at 20 items a page. The logic it runs:

**Outcome classes.** `ok` (200 and items at or above `expect_min_items`); `empty_200` (200, no data where data is expected, or a vendor error inside a 200 body); `low_yield` (200 but under `expect_min_items`); `throttled` (429, excluded from every rate); `auth` (401 or 403); `server` (5xx, timeout); `schema_unknown` (shape not recognised: archived by the fetchers, here only counted).

**Rules** (per route key, sliding 15-minute window; a minimum sample count `CANARY_MIN_SAMPLES` applies and is to be set in the pilot):

| State | Entered when |
|---|---|
| ok to degraded | `empty_200 / (ok + empty_200 + low_yield)` above 5%; or `low_yield` on every active target; or `server` on every target; or vendor 401, 402 or 403 (our key, balance or plan); or a rise in 401 or 403 on some targets |
| degraded to fallback | degraded, alternate configured, its flag not `off`, the alternate's own canary clean, no government client on the source (below) |
| any to blocked | the platform returns 401 or 403 on every active target and every token in use: the platform has refused our app or token |
| fallback or blocked to ok | the primary's probes are clean (empty-200 rate at or below 5%, yield at expectation) for a full window |

**A target empty for the whole window while its siblings return data** is quarantined (`active = false`, alert `stale_canary_target`) and left out of the rate.

**Block rule.** `blocked` means the platform refused us. There is no automatic fallback from `blocked`: an approval card goes to ops through n8n, default after 24 hours is no fallback. The canary never retries with another token, account, proxy or IP.

**Government rule.** A fallback that moves a green source to an amber vendor changes provenance, and amber data is excluded from government contracts: the decision carries `scope = non_government`, so sources watched by a government client stay green or stop. Amber-to-amber swaps are unaffected.

**Flap guard.** At most one flip per route per 15-minute window; recovery needs a full clean window.

### 5.4 What it gets

Per canary fetch, only this record is kept (rolling window in memory and the audit trail; no payload):

```json
{"target_id": "ct_tt_03", "route": "amber", "vendor": "tikhub", "http": 200, "items": 0, "expect_min_items": 3, "class": "empty_200", "latency_ms": 840, "at": "2026-10-06T11:15:02Z"}
```

It does not get post text, authors or any client data.

## 6. Inputs and outputs

### 6.1 Reads
`canary_targets`, `sources` (tier, health, route, vendor), `clients` (government flag) through `client_sources`, `budgets` through quota-governor, the platform flags, the SDK's per-call route counters (Prometheus), `source.events` (`added`, `retired`) for target hygiene.

### 6.2 Writes
`registry.decisions`, action `health_change`; registry-writer applies it and publishes `fallback_on`, `fallback_off` or `updated` on `source.events`:

```json
{"decision_id": "01J9Q4R8T2V6W0X3Y5Z7A1B9CD", "action": "health_change", "actor": "source-health-canary", "platform": "tiktok", "route": "amber", "vendor": "tikhub", "health": "degraded", "fallback": {"route": "amber", "vendor": "ensembledata"}, "scope": "non_government", "reason": "empty_200_rate", "evidence": {"window_minutes": 15, "samples": 60, "empty_200": 9, "rate": 0.15, "targets": 5}, "at": "2026-10-06T11:20:00Z"}
```

Also n8n webhook alerts, `canary_targets` (state), `service_runs`, `dlq.source-health-canary`.

### 6.3 State
`canary_targets` (proposed columns: `target_id`, `platform`, `route`, `vendor`, `service`, `source_id`, `call_params`, `expect_min_items`, `alternate_route`, `alternate_vendor`, `flag_name`, `active`, `quarantined_at`, `last_ok_at`); per route the current state and last flip time; the 15-minute window is in memory and rebuilt from the audit trail after a restart.

## 7. Limits, quotas and cost

Canary calls ride the route's own budget tag at the highest priority, so detection survives a budget squeeze. At a 5-minute period each target costs 288 calls a day. Examples: TikHub USD 0.144 to 0.288 a day per target (USD 0.50 to 1.00 per 1,000 requests); SociaVault USD 0.573 to 1.391; ScrapeCreators USD 0.285 to 0.541. YouTube: 288 units a day per target, 2.9% of the 10,000-unit day, so one or two targets and a longer period. Meta: each call counts in the Pages bucket (4,800 calls × engaged users per 24 h per token). X: USD 0.005 per post returned, USD 0.010 per user read, once per UTC day: use `since_id` and few targets; cost to be measured in the pilot. Apify actors are priced per item: to be measured in the pilot. Meta, news and web search cost only quota or politeness.

## 8. Failure handling and fallback

- The canary's own fetch errors follow the standard rules (429 backoff 30 s to 15 min); a canary that cannot run raises `canary_blind` rather than reporting healthy.
- A Redpanda or Postgres failure: decisions are retried with the same `decision_id`; registry-writer applies once.
- No alternate or flag off: stay `degraded`, alert; no invented route.
- 401 and 403 from the platform: `blocked`, approval card, no evasion.
- Schema change on a canary response: counted as `schema_unknown`, not as empty.

## 9. Non-functional requirements

- Throughput: targets × cycles per day per route, a few hundred calls per target; negligible next to 1,000,000 items a day.
- Latency: detection within one 15-minute window plus a cycle; events within 10 seconds of a decision (registry-writer's target).
- Idempotency: `decision_id` derived from route, state and window start.
- Scaling: one leader; stateless otherwise.
- Security: tokens from Supabase Vault per call, never logged; canary payloads discarded; no account pools, no proxies.

## 10. Metrics and alerts

`canary_fetch_total{route,vendor,class}`, `canary_empty_200_rate{route,vendor}`, `canary_yield_ratio`, `route_health{route,vendor}`, `canary_auth_errors_total{code}`, `fallback_on_total`, `fallback_off_total`, `recovery_probe_total{result}`, `canary_targets_active{route}`, `canary_cost_units_total`, `quota_denied_total`, `jobs_total{status}`, `dlq_total`. Alerts: `route_degraded`, `route_blocked`, `fallback_on`, `fallback_long` (fallback active for 24 hours), `stale_canary_target`, `canary_blind`, `canary_targets_low`.

## 11. Dependencies

listening-sdk (canary hook, adapters), registry-writer, quota-governor, n8n, every poller and fetcher (as the routes under test), Supabase Postgres and Vault, Prometheus, Redpanda.

## 12. Risks and mitigations

- A false flip moves thousands of sources: sample minimum, quarantine of lone empty targets, one flip per window.
- Canary targets go stale (source stops posting): quarantine and replacement proposals.
- Canary spend on metered routes: longer period, few targets, budget tag.
- Fallback changes provenance: `scope = non_government`, account managers told, provenance on every item.

## 13. Acceptance criteria

1. With 20 canary samples in 15 minutes and 2 empty 200s (10%), the route is `degraded` within one cycle, a `health_change` decision exists, and an n8n alert fired.
2. With 1 empty in 20 (exactly 5%), nothing flips.
3. One target empty for the whole window while the others return data is quarantined and the route stays `ok`.
4. 429 responses are classed `throttled` and never change health.
5. 401 or 403 on every target and token produces `blocked`, no `fallback_on`, an approval card, and no call with any other token, account, proxy or IP.
6. EnsembleData, the primary, `degraded` with a clean canary on TikHub, the fallback once its owner is verified, and `TT_VENDOR_ROUTE` not `off` yields `fallback_on` for every TikTok source; with the flag `off` the route stays `degraded` (ADR-0050, ADR-0051).
7. A green source watched by a government client receives no amber `fallback_on`.
8. A clean primary window yields `fallback_off` and `health = ok`; a second flip inside 15 minutes of the last is refused.
9. Probe intervals back off to at most 60 minutes while the primary stays bad.
10. A denied quota decision skips the canary call, counts `quota_denied_total` and changes no health.
11. Replaying a decision yields one `source.events` message; no canary payload appears in `raw.items`.

## 14. Open questions

1. `health_change` carries `platform`, `route`, `vendor`, `health`, `fallback` today; this PRD adds `scope`, `reason` and `evidence` and makes `fallback` an object. To be aligned with registry-writer.
2. Who enforces the government exclusion: the decision's `scope` read by registry-writer (proposed) or the canary listing sources one by one?
3. Minimum targets per route and `CANARY_MIN_SAMPLES`: to be set in the pilot.
4. Should a vendor-side 403 (key or plan) count as `degraded` and allow fallback, as proposed, while a platform-side 403 means `blocked`?
