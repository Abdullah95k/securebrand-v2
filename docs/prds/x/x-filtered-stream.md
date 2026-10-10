# x-filtered-stream

**Platform:** X · **Route:** green · **Lane:** Fetch posts · **Owner:** Backend lead, X adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

On X, a complaint about a bank, an outage or a ministry statement can spread across Iraq within the hour, and clients want to see it while they can still respond. x-filtered-stream keeps one open connection to the official X API v2 filtered stream: we give X up to 1,000 standing rules (the registered accounts and client brand terms we care about) and X pushes each matching post to us as it is published.

Without it, the freshest X data would be x-user-timeline-poller's hourly poll of tier-1 accounts, and brand mentions would surface only when x-recent-search next runs. Alerts would fire after a story has peaked, and each tier-1 account would need 24 timeline calls a day instead of one daily reconciliation.

## 2. Objective (the end state this service delivers)

Posts from covered accounts and posts matching client brand terms reach `raw.items` seconds after X delivers them; the active rules equal the desired rules; every interruption is closed by gap jobs, so nothing posted during an outage is lost; coverage is published so x-user-timeline-poller reconciles covered accounts daily instead of polling them. Target: p95 from receipt to Redpanda acknowledgement under 5 seconds; active rules equal desired rules within 5 minutes of a change; gap jobs emitted within 60 seconds of each reconnection; standby connected within 2 minutes of leader loss; zero canary posts lost; no post id counted twice in `post_reads` on one UTC day.

## 3. Scope

### In scope

- The single connection: leader election, reading, keep-alive detection, reconnection, standby takeover.
- Rule reconciliation: desired set, priorities, tags, term screening, budget shedding, coverage rows in `cursors`, connection state in `service_runs`.
- `raw.items` (kind `post`, matched rules in the envelope, `public_metrics` as the first metrics observation), ledger settlement, gap jobs.

### Out of scope

- Polling and daily reconciliation (x-user-timeline-poller); history of new accounts (backfill-orchestrator through x-full-archive-search); scheduled keyword search (x-recent-search); replies and quotes (x-replies-fetcher); deletions (x-compliance-sync).
- Hits and discovery (keyword-matcher); deduplication (normalize-item); tiers (qualifier, registry-writer); metrics refreshes; individuals as rule targets.

## 4. Users and consumers

- **Clients** see brand mentions and their top accounts' posts within seconds, so alerts fire while a story is still rising.
- **Ops** watches connection state, rule drift, gap jobs and `x_pay_per_use` spend, clears screened or flooding rules in `review_queue`, and can force a full reconcile or a gap fill for a stated window.
- **Downstream**: normalize-item, keyword-matcher (brand hits; unregistered authors become `discovery.hits`), comment-decay-scheduler (reply series for x-replies-fetcher), x-user-timeline-poller (coverage), x-recent-search (gap jobs), raw-archiver, source-health-canary, quota-governor.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** No job queue: two replicas run, and the one holding a Postgres advisory lock is the leader, owning the only connection (one per app) and the rule reconciler. The standby connects only after taking the lock; a leader that loses its lock session closes the stream at once. A reconcile runs on `source.events`, on Postgres NOTIFY from `sources` (X rows), `keywords` and `client_sources`, on a quota-governor mode change, after each (re)connect and hourly; runs never overlap.

**Coverage order.** Capacity is 1,000 rules minus a headroom reserve (sized in the pilot) for make-before-break swaps, filled in order: client brand keyword sets (one rule each, priority 1), tier-1 accounts (priority 1), tier-2 (2), tier-3 (3), most-followed first. Accounts pass x-user-timeline-poller's filter (`route = green`, `health != blocked`, `backfill_status in (done, capped)`); dormant and retired accounts get no rule, so tier promotion stays with the poller. Account rules OR `from:` handles in buckets keyed by a stable hash of `source_id`, so one change rewrites one rule; handles per rule depend on rule and tag length (to be confirmed in the pilot). Accounts that do not fit stay on x-user-timeline-poller's rotation; `stream_capacity_short` fires if a tier-1 account is left out.

**Push tier and hand-off.** A covered account is in the push tier: no polling for new posts, one reconciliation poll a day by x-user-timeline-poller, while `sources.tier` keeps the reach tier. Coverage is published as this service's `cursors` rows (`cursor` = X rule id) and connection state as its `service_runs` row. A cleared row, or `state = disconnected`, returns accounts to tier cadence on the poller's next scan.

**Catch-up.** A gap replaces rotation lag: after any disconnection or leader change, gap jobs re-read each affected rule over the gap window (5.2 C).

**Backfill on add.** History belongs to backfill-orchestrator through x-full-archive-search; a rule is added only after backfill ends.

### 5.2 Step by step

**A. Reconcile rules**

1. Build the desired set. Government clients without an X Enterprise plan naming them leave every client list; a rule serving only them is not built. Brand keyword sets are screened against ops' blocked-terms list (protests, rallies, sensitive attributes); refusals go to `review_queue` (`x_terms_screen`). Every rule needs a `from:` handle or a brand term: no location-only rules.
2. Drop rules whose priority the governor's mode no longer admits.
3. Read the active rules, diff on (value, tag), add new and changed rules, then delete superseded ones.
4. After X confirms, upsert coverage rows and clear those of uncovered sources; a rejection reason goes to `last_error` and the source stays on poller rotation.

**B. Receive**

1. Open the connection (5.3); write `state = connected`, `connection_id` (ULID) and `connected_at` to `service_runs`.
2. Read lines into a bounded buffer that never waits on Redpanda (overflow spills to a spool on the pod's volume); keep-alives reset the stall timer.
3. Per post: `source_id` = the covered account whose `platform_id` is `author_id`, else the first matched brand rule's keyword-rule source; `client_ids` = the author source's clients plus matched brand rules' clients.
4. Settle each micro-batch with quota-governor `{budget_tag: x_pay_per_use, amount: <posts>, service: x-filtered-stream, priority: <highest matched>, sub_counter: post_reads, resource_ids: [<post ids>]}`. A delivered post cannot be refused, so this settles rather than asks: ids already in today's ledger get `paid = false`, the rest `paid = true`.
5. Produce to `raw.items`; raw-archiver lands batches under `raw/green/x/<yyyy>/<mm>/<dd>/x-filtered-stream/`. Advance the high-water mark (receipt time up to which every post is acknowledged) and persist it with each `service_runs` heartbeat.
6. A rule whose hourly delivery exceeds its flood threshold (from its pilot baseline) is dropped at the next reconcile and sent to `review_queue` (`x_rule_flood`).

**C. Reconnect and gap fill**

1. On a drop, keep-alive stall or 5xx: `state = reconnecting`, reconnect with exponential backoff and full jitter; past a grace period (from pilot data), `state = disconnected`.
2. Window = [high-water mark − margin, first message on the new connection + margin]; margin = delivery latency p99 from the pilot.
3. Emit one job per affected rule on `jobs.x-recent-search`: `kind = reconciliation` (backfill jobs come only from backfill-orchestrator), `source_id` = the rule's first source, `query` = rule value, `source_ids`, `client_ids`, `window_start`, `window_end`, the rule's priority. Any part older than recent search's 7 days goes to `jobs.x-full-archive-search`.
4. The gap closes when `jobs.completed` arrives for all its jobs; otherwise `gap_unfilled` alerts.

### 5.3 The call it makes

```
GET /2/tweets/search/stream
  ?tweet.fields=created_at,public_metrics,conversation_id,lang,geo,entities
  &expansions=author_id,attachments.media_keys
Authorization: Bearer <company X app bearer token, from Supabase Vault>

/2/tweets/search/stream/rules    add and delete; up to 1,000 rules
```

The connection stays open and carries posts and keep-alive lines. To be confirmed in the pilot: base URL; method and body for add and delete; listing active rules; rule length, rules per request and tag length; whether `from:` accepts numeric ids; keep-alive interval; X's reconnect guidance; connections allowed per app; any recovery option for missed posts.

### 5.4 What it gets

One JSON object per line: `data` with the requested fields, `includes` (author, media keys) and `matching_rules` (id and tag of each rule matched):

```json
{
  "data": {"id": "2107413571090333696", "text": "عروض الافتتاح في فرع مجموعة البصرة للتجزئة الجديد تبدأ الخميس",
    "created_at": "2026-10-06T10:12:02.000Z", "author_id": "1172893456012345344",
    "conversation_id": "2107413571090333696", "lang": "ar",
    "public_metrics": {"retweet_count": 0, "reply_count": 0, "like_count": 0, "quote_count": 0, "bookmark_count": 0, "impression_count": 0}},
  "includes": {"users": [{"id": "1172893456012345344", "name": "Basra Retail Group", "username": "basraretailgrp"}]},
  "matching_rules": [{"id": "1843102937465028608", "tag": "v1|acct|p1|s=…"}, {"id": "1843103311892615168", "tag": "v1|brand|p1|s=…"}]
}
```

Counts are near zero at delivery. Not returned: deletions (x-compliance-sync), replies that match no rule (x-replies-fetcher), follower counts, place details, media URLs. Whether an edited post arrives again is to be confirmed in the pilot.

## 6. Inputs and outputs

### 6.1 Reads

The stream; `source.events`; `sources`, `keywords`, `client_sources`, `clients` (X Enterprise entitlement), the blocked-terms list, own `cursors` and `service_runs` rows; `jobs.completed` (own gap jobs); quota-governor mode and ledger.

### 6.2 Writes

`raw.items`, one message per post, in x-user-timeline-poller's envelope plus `matching_rules` and `connection_id`:

```json
{
  "envelope": {
    "platform": "x", "kind": "post", "route": "green", "vendor": null,
    "service": "x-filtered-stream",
    "source_id": "a4d2c9e1-5b7f-4e3a-8c60-2f1b9d7e4a35",
    "platform_id": "2107413571090333696",
    "idempotency_key": "x:post:2107413571090333696",
    "job_id": "01M48B5V90W8B91YHW3K3BNVR2", "attempt": 1, "context": {"connection_id": "01J9PB7XQ3M8D2V6K0R4T1H5ZW"},
    "fetched_at": "2026-10-06T10:12:04Z",
    "paid": true,
    "retention_class": "x_24h_sync",
    "client_ids": ["3e8f1a2b-7c4d-4b9e-a1f0-6d2c5e8b7a14"],
    "matching_rules": [
      {"id": "1843102937465028608", "tag": "v1|acct|p1|s=a4d2c9e1-5b7f-4e3a-8c60-2f1b9d7e4a35,0b6e2d71-93c4-4f8a-b215-7d40e9c3a6f2|c=3e8f1a2b-7c4d-4b9e-a1f0-6d2c5e8b7a14,9d27c4e0-1f6a-4b83-8e5d-c0a2b7f41936"},
      {"id": "1843103311892615168", "tag": "v1|brand|p1|s=6c19f0a4-2e8b-4d57-9a3c-b1e7d52f8064|c=3e8f1a2b-7c4d-4b9e-a1f0-6d2c5e8b7a14"}],
    "batch": "raw/green/x/2026/10/06/x-filtered-stream/000412.jsonl.zst",
    "metrics_observation": "stream"
  },
  "payload": { "...": "the line from 5.4, unchanged" }
}
```

Ids in this example follow ADR-0006: a ULID `job_id` made at receipt, with `attempt = 1`, and the delivery id in `context` (ADR-0005). Where its other fields differ from an ADR, the ADR wins (ADR-0001).

The second client watches only the other account in the bucket, so it is not attributed. The two rules behind it:

```json
[
  {"value": "from:basraretailgrp OR from:wasitnewsnet", "tag": "v1|acct|p1|s=a4d2c9e1-…,0b6e2d71-…|c=3e8f1a2b-…,9d27c4e0-…"},
  {"value": "(\"بصرة ريتيل\" OR \"مجموعة البصرة للتجزئة\") lang:ar -is:retweet", "tag": "v1|brand|p1|s=6c19f0a4-…|c=3e8f1a2b-…"}
]
```

Tags are `v1|<acct|brand>|p<priority>|s=<source ids>|c=<client ids>`. Account rules carry no filters, so they deliver what x-user-timeline-poller reads; brand rules add `-is:retweet`, and `lang:ar` when the keyword set is Arabic. Also written: `jobs.x-recent-search`, `jobs.x-full-archive-search`, `cursors`, `service_runs`, `review_queue`, ledger entries, and `dlq.x-filtered-stream` for unparseable lines.

### 6.3 State

Rules live at X. Coverage rows hold `cursor` = rule id, `last_success_at`, `last_error`. `service_runs` holds `state` (connected, reconnecting, disconnected), `reason`, `connection_id`, high-water mark, last keep-alive and open gaps with job ids. In memory: the lock, buffer, author map and per-rule rates; on disk: the spool.

## 7. Limits, quotas and cost

- Price: USD 0.005 per post read and USD 0.010 per user read, deduplicated per resource per UTC day. Every streamed post is a post read, paid unless today's ledger holds its id; a brand rule delivering 1,000 new posts a day costs USD 5.00 a day, USD 152.50 a month. Whether rules or connection time are billed is to be confirmed in the pilot.
- Re-reads by gap jobs or the 22:00 to 23:59 UTC reconciliation polls are free on the same UTC day and paid again after midnight.
- Cap: 3,000,000 post reads a month, shared by the seven x-* services. A push cannot be refused, so the rule set is the brake: stretch from 80% admits priorities 1 to 3 (no change), from 95% only 1 and 2 (tier-3 rules deleted); exhausted at 100% deletes every rule, closes the connection and writes `state = disconnected`, `reason = budget`. With the budget at the cap, the bands start at 2,400,000 and 2,850,000 reads.
- Terms: no surveillance, no monitoring of sensitive events (protests, rallies), no profiling on sensitive attributes; a Government End User requires an Enterprise plan, must be named at use-case review, and X may refuse; deletions mirrored within 24 hours (`x_24h_sync`, through x-compliance-sync).

## 8. Failure handling and fallback

- Drop, stall or 5xx: backoff with jitter (initial delay and ceiling to be confirmed in the pilot, ceiling at most 15 min), then gap jobs.
- HTTP 429 on connect or on rules: 30 s to 15 min with jitter; never a second connection; alert after 5 consecutive failures.
- HTTP 401 and 403: mark the app token `degraded`, close, stop, alert, `state = disconnected`; never rotate tokens or IPs.
- Rule rejected: `last_error`, the sources stay on poller rotation, `rule_rejected` alerts.
- Redpanda or quota-governor unavailable: keep reading into the spool; if it fills, close on purpose and let gap jobs recover the window.
- Schema change: payload archived; normalize-item raises `schema_unknown`. X has no amber route: `fallback_on` is never set.

## 9. Non-functional requirements

- Throughput: X is 0.6M items a month at full scale, about 19,700 a day or 0.23 a second; the stream's share and peaks are to be measured in the pilot.
- Latency: p95 receipt to acknowledgement under 5 s. Idempotency: `x:post:<id>`; overlapping gap reads are deduplicated by normalize-item.
- Scaling: one leader, one standby; downstream scales on partition lag.
- Security: token from Supabase Vault, never logged or tagged; no account pools or proxies; account rules only for qualifier-admitted organizations and public figures.

## 10. Metrics and alerts

`items_fetched_total`, `items_new_total`, `fetch_latency_seconds` (receipt to acknowledgement), `cost_units_total`, `quota_denied_total` (rules shed), `dlq_total`, plus `stream_connected`, `stream_reconnects_total{reason}`, `rules_active{kind,priority}`, `rules_desired{kind,priority}`, `accounts_covered`, `gap_jobs_open`, `post_reads_total{paid,kind}`, `spool_bytes`. Alerts: `stream_down` (past grace), `stream_silent`, `token_degraded`, `rules_drift` (above 5 minutes), `stream_capacity_short`, `rule_rejected`, `rule_flood`, `gap_unfilled`, `spool_high`, `dlq_nonempty`.

## 11. Dependencies

listening-sdk, quota-governor (read ledger defined by x-recent-search), x-user-timeline-poller, x-recent-search, x-full-archive-search, x-user-resolver (handles), backfill-orchestrator, registry-writer, keyword-matcher, normalize-item, comment-decay-scheduler, x-replies-fetcher, x-compliance-sync, source-health-canary, raw-archiver; Supabase Postgres and Vault, Redpanda, a persistent volume; an X pay-per-use developer app.

## 12. Risks and mitigations

- A brand word that is also an everyday word (زين means "good" in Iraqi Arabic) floods the stream and the cap: single common words need a qualifying phrase at set-up; the flood guard and governor modes cap the damage.
- Connected but silent stream: source-health-canary checks canary accounts' posts and raises `stream_silent`, forcing a reconnect; daily reconciliation polls catch the rest.
- Sensitive-event monitoring through entered terms: screening, `review_queue`, no location-only rules.
- A renamed account breaks `from:<handle>`: x-user-resolver's update rewrites the rule; the daily poll by numeric id covers the interval.

## 13. Acceptance criteria

1. With 1,500 fixture accounts and 20 brand keyword sets on a simulated X API, active rules never exceed 1,000; every brand set and tier-1 account is covered before any tier-2 account; dormant, retired and `pending` accounts have no rule.
2. A `retired` event removes the account from its rule and clears its coverage row within 5 minutes; a dormant account promoted by `tier change` is covered within 5 minutes.
3. Changing one account in a bucket adds the new rule before deleting the old; a post from another account in that bucket during the swap is written exactly once.
4. A post matching an account rule and a brand rule yields one `raw.items` message with the author's `source_id` and both rules in `matching_rules`.
5. A post read earlier that UTC day by x-user-timeline-poller is written `paid = false` and leaves `post_reads` unchanged; after 00:00 UTC it is `paid = true`.
6. After a 10-minute network cut, one `reconciliation` job per active rule is on `jobs.x-recent-search` within 60 seconds of reconnecting, covering the cut; every fixture post created during it reaches `raw.items`; beyond the grace period `service_runs` showed `disconnected`.
7. Killing the leader pod: the standby connects within 2 minutes, the simulated API never sees two open connections, and the handover window gets gap jobs.
8. At 95% of the period budget, tier-3 rules are deleted and their coverage rows cleared; at 100%, no rule remains and the connection is closed.
9. A keyword set containing a blocked protest or sensitive-attribute term never reaches X and appears in `review_queue`; a government client without X Enterprise entitlement appears in no tag or envelope.
10. Redpanda down for 5 minutes loses no post; the spool drains in receipt order and normalize-item stores each post once.
11. Every message carries `route = green`, `vendor = null`, `paid`, `retention_class = x_24h_sync`, `matching_rules` and `metrics_observation = stream`; the token never appears in logs, tags or envelopes.

## 14. Open questions

1. Pilot: rule length, rules per request, tag length, the listing call, and whether `from:` takes numeric ids (which would survive renames).
2. Does pay-per-use offer a stream recovery option that would shorten gap jobs?
3. Confirm with x-recent-search's owner the `reconciliation` job shape and that account-rule results get the author's `source_id`.
4. Should x-recent-search skip scheduled queries for keyword rules covered here, as x-user-timeline-poller does for accounts?
5. Is the `author_id` expansion billed as a user read? Decide once with x-user-timeline-poller.
6. Brand rules serve several clients: when does the X plan move to Enterprise, and who owns the blocked-terms list?
