# alert-evaluator

**Platform:** Shared · **Route:** shared · **Lane:** Processing · **Owner:** Backend lead (alerts) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A dashboard answers a question when someone opens it. A communications team needs the opposite: to be told within minutes that mentions of its brand jumped, that a service complaint wave is turning negative, that a 400,000-follower page has just written about it for the first time, or that such a post has been taken down. Nobody can watch hundreds of keyword and source combinations all day.

alert-evaluator turns the aggregates into those signals. It evaluates each client's rules every time the aggregates change, decides whether the condition is new, suppresses repeats, and hands the alert to the channel the client chose. It is also where the government-client restriction is enforced: reputation and service-quality signals only, nothing about sensitive events or individuals.

Without it the product is a report, not a monitor; and every client would build crude alerting on the dashboard's API with no shared de-duplication or compliance rules.

## 2. Objective (the end state this service delivers)

End state: every rule condition that becomes true on the aggregates produces one alert, delivered on the rule's channels, within 5 minutes of the aggregate update that made it true; it is not repeated inside its cool-down; and no government client ever receives a sensitive-event or individual-level alert.

Measurable target: p95 aggregate-update-to-first-delivery-attempt below 5 minutes at full scale (about 1,000,000 items a day, about 12 a second, peaks to be measured in the pilot); zero duplicate alerts for one fingerprint inside its cool-down; zero blocked-type alerts reaching a government client; 100% of alerts with a recorded delivery outcome.

## 3. Scope

### In scope
- Five rule types: volume spike against a 7-day baseline per keyword and source, negative-share threshold, new high-reach poster, keyword first seen, deletion of a high-reach post.
- Evaluation on every aggregate update (at least every 5 minutes); de-duplication, cool-down, open and resolved states.
- Delivery through n8n flows (email, Telegram, Slack) and signed client webhooks; the government-client policy.

### Out of scope
- Computing aggregates (aggregator); rule editing screens (React app, with validation shared through `listening-sdk`); sentiment (analysis-sentiment); sending email, Telegram or Slack messages themselves (the n8n flows); incident handling by the client.

## 4. Users and consumers

- Client communications and customer-service teams receive the alerts; account managers tune rules.
- Government clients receive reputation and service-quality alerts only.
- Ops receive internal alerts (stale aggregates, delivery failures) and read the DLQ.
- Clients' own systems consume the webhook payload.

## 5. How it works

### 5.1 Trigger and rotation

Time-driven with two event feeds. A loop polls the aggregator's `service_runs.last_success_at` every `ALERT_POLL_SECONDS` (default 30) and evaluates when it has moved; it also evaluates at least every 300 s whatever happens. One active instance, chosen by a Postgres advisory lock; delivery workers are stateless. Event feeds, consumer group `alert-evaluator`: `item.hits` (partitioned by `source_id`) builds a watch set of items from high-reach sources; `deletions` triggers the deletion rule. Ordering across topics is not needed.

Replay: a model or rule change re-runs the backlog from the raw archive through raw-archiver's replay path and the aggregator rebuilds the hours. The evaluator looks only at the open window and at events younger than `ALERT_MAX_AGE_HOURS` (default 3), so rebuilt history, rematches and backfills fire nothing. A `backtest` job (dry run, no delivery) runs a rule over stored hourly aggregates and reports how many alerts it would have fired.

### 5.2 Step by step

1. Check freshness: if the watermark is older than three aggregator cycles, mark the evaluation `stale`, alert ops, skip.
2. Load enabled rules (cached `ALERT_RULE_POLL_SECONDS`, default 30) and apply the government policy (5.3 C).
3. Run one batched ClickHouse query per rule type over `aggregates_hourly_v` for the open hour, the previous closed hour and the baseline hours.
4. Apply each rule's predicate (5.3 A) and build candidates with a fingerprint.
5. Run de-duplication and cool-down against `alerts` (5.3 D); insert new alerts and delivery rows in one transaction.
6. Deliver pending rows (5.3 E); record outcomes.
7. Write `service_runs` (evaluation time, rules evaluated, alerts fired).

### 5.3 The call it makes (the processing it performs)

**A. Rules and predicates.** `alert_rules` (proposed): `rule_id`, `client_id`, `type`, `keyword_id` (null for all keywords), `scope` (`keyword` or `keyword_source`), `platform`, `params` (jsonb), `severity`, `channels` (jsonb), `cooldown_minutes`, `enabled`. Defaults for numeric parameters are set from the pilot.
1. `volume_spike`. Baseline = the median of the same hour of day over the previous 7 days, from `aggregates_hourly_v`, for the keyword (all sources) or the keyword and one source; the median keeps one earlier spike from lifting it. Let `f` be the elapsed fraction of the open hour. Fire when `mentions_so_far >= max(min_mentions, ratio × baseline × f)` and `f >= min_elapsed`. The last closed hour is tested the same way with `f = 1`. For `keyword_source` every source with mentions in the open hour is tested.
2. `negative_share`. Over the last `window_hours`: negative mentions divided by positive, neutral and negative mentions (`pending` and `unscored` excluded). Fire when the share reaches `threshold` and scored mentions reach `min_scored_mentions`.
3. `new_high_reach_poster`. A registered source whose followers are at least `min_followers` (default 100,000, the tier-1 line) has mentions of the keyword in the open window and none in the previous `lookback_days` (default 30, read from `aggregates_daily`). Individuals roll up under the nil source and never match.
4. `keyword_first_seen`. The keyword has mentions in the open window and none in any earlier hour, day or month. A rematch of history lands in old hours, so it cannot fire this.
5. `post_deleted_high_reach`. Not read from ClickHouse: by the time a `deletions` message arrives the rows may be gone, so the evaluator keeps its own `alert_watch_items` (item id, client, keyword, source, followers, hit time, no text), filled from `item.hits` when the source has at least `min_followers` followers (registry cache from `source.events`) and the hit is younger than 7 days. A `deletions` message whose reason means the post disappeared at its platform (`platform_sync`, or the X compliance reason as named by deletion-propagator) and whose item is in the watch set fires. Deletions caused by retention, client offboarding or a user's privacy request never fire.

**B. Fingerprint.** `fingerprint = <type>:<rule_id>:<scope_key>` where `scope_key` is the keyword, the keyword and source, or the item id. One alert per fingerprint and window key is enforced by a unique index, so re-evaluating an unchanged aggregate creates nothing.

**C. Government policy.** For clients with `clients.client_type = government`: allowed types are `volume_spike`, `negative_share` and `keyword_first_seen`, and only on keywords whose `keywords_dim.purpose` is `reputation` or `service_quality`; `new_high_reach_poster` and `post_deleted_high_reach` are refused (individual-level and sensitive-event monitoring). Payloads are aggregate-only: keyword, platform, counts, shares, window; no source name, handle, post URL or author reference; `scope = keyword` is forced. The rule editor rejects violations; the evaluator enforces the same check and fails closed when `client_type` is missing.

**D. De-duplication and cool-down.** `alerts` has status `open`, `resolved`. A candidate with an open alert of the same fingerprint inside `cooldown_minutes` is suppressed. Past the cool-down and still firing, one reminder (`renotify = true`) goes out and the cool-down restarts. After `ALERT_CLEAR_CYCLES` (default 5) evaluations without the condition the alert becomes `resolved`; a new occurrence then opens a new alert.

**E. Delivery.** `alert_deliveries` is the outbox: one row per alert and channel. Email, Telegram and Slack each have an n8n flow reached by a signed webhook call; client webhooks are posted by the service with an HMAC signature, a timestamp and `Idempotency-Key: <alert_id>:<channel>`. Failures back off from 30 s to 15 min, 5 attempts, then `dlq.alert-evaluator` and an ops alert. Telegram can be blocked in Iraq (it was in August 2023 and from 3 Apr to 9 May 2026), so every rule keeps at least one non-Telegram channel and a Telegram failure falls through to it.

### 5.4 What it gets

Hourly, daily and monthly aggregates per client, keyword, source, platform, sentiment and topic; hit events for high-reach sources; deletion events; rules and client types. It does not get item text, author identity or anything below source level.

## 6. Inputs and outputs

### 6.1 Reads
- ClickHouse: `aggregates_hourly_v`, `aggregates_daily_v`, `aggregates_monthly_v`, `keywords_dim`, `sources_dim`.
- Topics: `item.hits`, `deletions`, `source.events`.
- Control plane: `alert_rules`, `alerts`, `alert_deliveries`, `alert_watch_items`, `clients`, `service_runs` (aggregator watermark), Vault (webhook and flow secrets).

### 6.2 Writes
`alerts`, `alert_deliveries`, `alert_watch_items`, `service_runs`; n8n webhook calls and client webhook posts; `dlq.alert-evaluator`.

```json
{
  "schema": "alert/v1",
  "alert_id": "01J9W5A2M7Q0R4T8V1X3Y5Z7B9",
  "rule_id": "5d0c2b7e-8a14-4f63-b9e1-2c7a6d4f0e18",
  "rule_type": "volume_spike", "severity": "high", "renotify": false,
  "client_id": "e2a9d0b1-6c7f-4a38-9d5e-0f1a2b3c4d5e",
  "keyword": {"keyword_id": "9a8b7c6d-5e4f-4321-a0b9-c8d7e6f5a4b3", "label": "زين العراق", "purpose": "service_quality"},
  "scope": {"level": "keyword_source", "platform": "facebook",
            "source": {"source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566", "display_name": "Example Page"}},
  "window": {"hour": "2026-10-06T08:00:00Z", "elapsed_fraction": 0.62, "evaluated_at": "2026-10-06T08:37:12Z"},
  "metrics": {"mentions_so_far": 41, "baseline_median_same_hour": 9.4, "expected_so_far": 5.8, "ratio": 7.1, "baseline_days": 7},
  "fingerprint": "volume_spike:5d0c2b7e:a3c0f1e2",
  "cooldown_until": "2026-10-06T10:37:12Z"
}
```

For a government client the `source` object and `platform` are absent and `scope.level` is `keyword`.

### 6.3 State
Alert state in Postgres (`alerts`, `alert_deliveries`, `alert_watch_items`, pruned when older than 7 days and resolved); consumer offsets; the rule cache; the registry cache (last `source.events` offset); the leader lock. No state is needed in memory to resume.

## 7. Limits, quotas and cost

No external API or vendor is called for detection: no `budget_tag`, no quota-governor round trip. Cost is a few batched ClickHouse queries per cycle over hourly rows, Postgres writes per alert, and the n8n and mail or chat volume. Rules per client, alerts a day and watch-set rows are to be measured in the pilot; each query touches at most the open window plus 7 days of hourly rows for the clients with rules. Email, Telegram and Slack delivery prices and limits belong to the n8n flows; USD costs are confirmed when providers are chosen.

## 8. Failure handling and fallback

- Aggregates stale (watermark older than three cycles) or ClickHouse down: evaluation is marked `stale`, no alert is raised from old data, ops are told; it resumes on the next fresh watermark.
- Postgres unavailable: nothing is sent, because de-duplication cannot be checked; sending twice is worse than sending late.
- n8n or a client endpoint failing: backoff and retry, fall through to the rule's other channel, then DLQ. HTTP 410 from a client webhook disables that endpoint and notifies the account manager.
- Rule with bad parameters: disabled and flagged, other rules continue.
- Recovery storm after an outage: a per-client limit of `ALERT_STORM_LIMIT` new alerts an hour turns the excess into one digest.
- Missing `client_type`: fail closed for that client.

## 9. Non-functional requirements

- Throughput: rules per client and clients are to be measured in the pilot; evaluation cost is batched per rule type, not per rule.
- Latency: the chain is normalize within 60 s of fetch, matching within 60 s of normalization, analysis within 15 min for tier-1 sources, alerts within 5 min of the aggregate update (this service). Evaluation runs within `ALERT_POLL_SECONDS` of the watermark and at least every 5 minutes.
- Idempotency: unique `(fingerprint, window_key)`; outbox rows; `Idempotency-Key` on every delivery; an unchanged aggregate state produces no new alert.
- Scaling: one active evaluator, stateless delivery workers; the topic consumers scale by partition.
- Security: HMAC secrets in Supabase Vault; no item text, author reference or handle in any payload; TLS; Node (TypeScript); rule validation in `listening-sdk` shared with the editor.

## 10. Metrics and alerts

Prometheus: `alert_eval_cycles_total{status}`, `alert_eval_seconds`, `alert_eval_staleness_seconds`, `alerts_fired_total{rule_type}`, `alerts_suppressed_total{reason}`, `alerts_blocked_total{reason}`, `alert_delivery_total{channel,status}`, `alert_delivery_latency_seconds`, `watch_set_size`, `dlq_total`. Internal alerts: no evaluation completed for 5 minutes; staleness above three cycles; a channel failing above its baseline for 10 minutes; DLQ non-empty; any `alerts_blocked_total{reason="government_policy"}` (audit).

## 11. Dependencies

aggregator (tables and watermark), store-writer (`keywords_dim`, `sources_dim`), keyword-matcher (`item.hits`), deletion-propagator (`deletions`), registry-writer (`source.events`), n8n, ClickHouse, Supabase Postgres and Vault, Redpanda, `listening-sdk`.

## 12. Risks and mitigations

- Hourly grain limits spike detection to a pace test inside the open hour; `min_elapsed` and `min_mentions` damp early noise; a minute-grain table is the next step if the pilot shows missed spikes.
- Seasonality (Fridays, religious holidays): the same-hour median covers the weekly pattern only; thresholds are tuned per client in the pilot.
- Alert fatigue: cool-down, resolved state, digest on storms, backtests before enabling a rule.
- Government breach: type refusal, aggregate-only payloads, fail-closed check, an audit alert and an acceptance test.
- Telegram blocked in Iraq: a mandatory second channel.
- Watch-set growth: only high-reach hits, no text, pruned at 7 days.
- Replays paging clients: age guard and open-window evaluation.

## 13. Acceptance criteria

1. A `volume_spike` fixture (same-hour baseline median 9.4 over 7 days, 41 mentions at `f = 0.62`) fires with ratio about 7; one just under `ratio` or under `min_mentions` does not.
2. A fixture with one earlier spike day in the 7 days gives the same median and still fires.
3. A `negative_share` fixture over the threshold with enough scored mentions fires; one with too few scored mentions, or only `pending` items, does not.
4. A source with 100,000 followers writing about the keyword for the first time in 30 days fires `new_high_reach_poster`; one with 99,999 does not; an individual never does.
5. `keyword_first_seen` fires once for a keyword with no history, and not when a rematch fills old hours.
6. A `deletions` message with reason `platform_sync` for a watched item fires `post_deleted_high_reach` with no item text; one with a retention, offboarding or privacy reason does not.
7. The same condition over 10 consecutive cycles gives one notification; after the cool-down, if still true, one `renotify`; five clear cycles resolve it.
8. After the aggregator watermark moves, evaluation runs within `ALERT_POLL_SECONDS`; with the aggregator stopped, evaluation still runs every 5 minutes, marks `stale` and raises no alert.
9. Each of the email, Telegram and Slack flows and a client webhook receives the payload with an `Idempotency-Key` and, for the webhook, a valid HMAC; a failed Telegram delivery falls through to the rule's other channel; 5 failures reach the DLQ and ops are alerted.
10. A government client cannot create `new_high_reach_poster` or `post_deleted_high_reach`; its `volume_spike` payload has no source, handle, URL or author reference; a rule on a keyword with another `purpose` is blocked; a missing `client_type` blocks everything.
11. A replay and rematch of 7 days of history fires zero alerts.
12. Re-running evaluation on an unchanged aggregate state creates no second alert row.

## 14. Open questions

1. `alert_rules`, `alerts`, `alert_deliveries` and `alert_watch_items` are new control-plane tables, absent from CONVENTIONS. Confirm.
2. Is the open-hour pace test enough for outage-style spikes, or should aggregator add a minute-grain recent table?
3. deletion-propagator must name the deletion reasons and carry `item_id`; if it deletes before the evaluator reads the message, the watch set covers it. Confirm both.
4. Defaults for `ratio`, `min_mentions`, `threshold`, `min_scored_mentions`, `cooldown_minutes` and `ALERT_STORM_LIMIT` come from the pilot; who approves them?
5. Is `keyword_first_seen` acceptable for government clients on reputation and service-quality keywords? The draft allows it; confirm with compliance.
