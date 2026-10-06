# quota-governor

**Platform:** Shared · **Route:** shared · **Lane:** Support · **Owner:** Platform engineer, budgets and quotas · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Every external call in this product costs something: quota (Meta's Pages bucket, YouTube's daily units, Instagram's hashtag allowance), money (X per read, every vendor per request or per item), or both. More than forty services make those calls independently, and none can see what the others have used. A backfill burst can empty the YouTube day before the Tier 1 polls run. An amber vendor can be spent by the middle of the month. X can pass its hard cap without anyone noticing until the bill.

quota-governor is the one set of counters and the one yes or no. A service asks before every batch, is told to go, to wait until a given time, or to stop, and reports what it actually used. Without it, spend is a surprise, the least important work eats the budget the most important work needs, and there is no graceful way to slow down: the product either runs at full speed or hits a wall.

## 2. Objective (the end state this service delivers)

Every call that costs budget is preceded by a decision; every counter matches the provider's own numbers; no limit is exceeded without a deliberate, audited ops raise; client-facing work is served first and backfill last; and amber rotation slows gently at 80% of a monthly budget, never beyond daily.

Target: 100% of external calls covered by a decision (checked by comparing `cost_units_total` with the ledger); zero breaches of a daily or period limit; alerts at 50%, 80% and 95% fire once per period within one minute; daily drift between counters and provider figures inside a tolerance set in the pilot.

## 3. Scope

### In scope
- Budget tags and counters in `budgets`; the allow, wait-until and deny protocol; reservations and settlement.
- Per-API rules: X read ledger, YouTube buckets, Meta usage headers, Instagram hashtag ledger, vendor monthly spend.
- Priorities, modes (`normal`, `stretch`, `exhausted`) and the `stretch_factor` for amber rotation; resets; dashboards and alerts; the X Enterprise alert; a capacity query for the qualifier.

### Out of scope
- Making calls, retries and backoff (the services); contracts, prices and budget sizes (ops decides, the governor enforces); per-client charge-back (later).

## 4. Users and consumers

- **Every service that calls an external API or vendor**, through the listening-sdk quota hook: pollers, fetchers, searches, resolvers, source-health-canary, backfill services.
- **Readers of the mode:** comment-decay-scheduler, backfill-orchestrator, every amber poller's scheduler, and the qualifier (capacity for new sources under rule 5).
- **Ops and Abdullah** read the dashboards; n8n delivers the alerts.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A synchronous request from the SDK before a batch: `{budget_tag, amount, service, priority}` plus optional `sub_counter`, `resource_ids`, `job_id`, `request_id`. Response: `{decision, wait_until, remaining}` plus `charge` and `reservation_id`. After the call the service sends a `report` with actual units, provider usage headers and whether the call was billed. A leader-elected loop (Postgres advisory lock) handles resets, thresholds and stale reservations.

**Priorities** (derived from job kind and tier by an SDK helper; a caller cannot claim more than its kind allows, so backfill is always 5):

| P | Work |
|---|---|
| 1 | Tier 1 rotation polls, client refresh requests, `ops_force`, canary fetches |
| 2 | Tier 2 rotation, keyword and hashtag searches for client rules, comment steps up to +24 h, metrics at +24 h |
| 3 | Tier 3 and dormant rotation, later comment steps, replies, metrics at +7 d |
| 4 | Hot-post extra fetches, resolvers and discovery lookups |
| 5 | Backfill |

**Modes** from use of the tag's period budget: `normal` below 80%; `stretch` from 80% (admits priority 1 to 3 only, from 95% priority 1 and 2 only); `exhausted` at 100% (everything denied until the reset or an audited ops raise).

**Stretching rotation.** On amber tags in `stretch` the governor publishes `stretch_factor = max(1, projected / limit)`, where `projected = used + used / elapsed_days × remaining_days`. Each amber poller sets its interval to `min(tier_interval × stretch_factor, 24 h)`: Tier 1 and Tier 2 slow down, nothing goes below daily. comment-decay-scheduler drops hot extras first, then lengthens steps after +24 h; the +24 h step is held, never skipped.

**Resets** per tag (`reset_rule`): X read ledger, UTC day; X cap, billing cycle; Meta, rolling 24 hours; Instagram hashtags, rolling 7 days; YouTube, daily at the provider's reset time (to be confirmed in the pilot); vendors, calendar month or contract cycle. A reset zeroes the period, recomputes the mode and re-arms the alerts.

### 5.2 Step by step

1. Authenticate the service; return the stored result if `request_id` was seen.
2. Compute the charge (5.3), evaluate the rules, and reserve with one conditional `UPDATE` on the `budgets` row.
3. Respond. The caller makes the call and sends `report`; the governor settles (releases unused units; releases everything when the call was not billed), updates ledgers and records Meta usage.
4. Re-evaluate mode, `stretch_factor` and thresholds; fire each alert once per period.
5. Expire reservations past their TTL; run resets.

### 5.3 The call it makes

No external call. The logic it runs: `decide(request)`:

1. Tag unknown, disabled, or its platform flag `off` (amber): deny `flag_off`.
2. Charge: X, only the `resource_ids` not yet in today's ledger; Instagram hashtag, 0 if already in the account's 7-day ledger else 1; otherwise `amount`.
3. Pacing rule (GDELT, 1 request per 5 seconds): wait until the last request plus 5 seconds.
4. Window (daily, rolling) would overflow: wait until the window frees; period (month, cycle, cap) would overflow: deny `period_full`.
5. Priority above the mode's admit level: wait until reset on daily tags, deny `priority_gate` on monthly tags.
6. Otherwise allow, reserve, return `remaining` (minimum across windows, in the tag's unit and money).

**Per-API rules:**

| Tag | Rule |
|---|---|
| `x_pay_per_use` | sub-counters `post_reads` (USD 0.005 each) and `user_reads` (USD 0.010 each); a read already in the UTC-day ledger is free; hard cap 3,000,000 post reads per billing cycle (USD 15,000 of reads) |
| `youtube_data_api` | 10,000 units a day in buckets `search` (100 units a call, bought in multiples of 100), `ingest`, `comments`, `reserve`; other calls 1 unit a page; `ingest` and `comments` may borrow from each other, `search` never borrows, `reserve` is for priority 1; bucket sizes set in the pilot |
| `meta_graph_pages:<client_id>` | 4,800 calls × engaged users per 24 h per token; services report `X-App-Usage` and `X-Business-Use-Case-Usage`; use above 80% of the reported bucket gates priority 4 and 5; a throttle with `estimated_time_to_regain_access` becomes `wait_until`; error 80001 counted per Page for the alert |
| `ig_hashtag_<ig_user_id>` | 30 unique hashtags per business account per rolling 7 days; the 31st waits until the oldest leaves the window |
| `fb_vendor`, `ig_vendor`, `tt_vendor`, `li_vendor_<action>`, `tg_*` | monthly spend per tag (`tt_vendor` with per-service sub-counters), in requests, credits or items converted at the prices of section 7 |
| `perplexity_search`, `mojeek_search`, `gdelt_doc_api`, `news_*`, `linkedin_cm:<client_id>`, `tt_display:<client_id>`, `ig_graph_<ig_user_id>`, `meta_*` | quota or spend counters of the same kind |

**Enterprise trigger (X).** When a client flagged as a government body is attached to any X source, or more than one client receives X data, the governor raises `x_enterprise_required` to ops, repeated daily until ops acknowledges.

### 5.4 What it gets

Requests and reports from services, plus provider headers. It never sees platform content.

## 6. Inputs and outputs

### 6.1 Reads
Requests and `report` calls; `budgets`, `clients` (government flag), `client_sources`, `vendor_keys` (plan, no keys), platform flags, ledgers; `source.events` (`added`) for the Enterprise check.

### 6.2 Writes
Decisions (response) and `budgets`. Example exchange for X:

```json
{"request": {"request_id": "01J9R5S3V7W1X4Y8Z0A2B6C9DE", "budget_tag": "x_pay_per_use", "sub_counter": "post_reads", "amount": 100, "service": "x-user-timeline-poller", "priority": 1, "resource_ids": ["1842390117700000001", "1842390117700000002"]},
 "response": {"decision": "allow", "wait_until": null, "charge": 87, "reservation_id": "01J9R5S3V9K2M6P0Q4T8W1ZXYB", "remaining": {"post_reads": 1795882, "usd": 8979.41}}}
```

The `budgets` row behind it: `{"budget_tag": "x_pay_per_use", "sub_counter": "post_reads", "unit": "post_reads", "currency": "USD", "unit_price": 0.005, "period": "billing_cycle", "limit": 3000000, "used": 1204031, "reserved": 87, "mode": "normal", "stretch_factor": 1.0, "warn_50_at": "2026-10-04T08:12:00Z", "warn_80_at": null, "warn_95_at": null}`.

### 6.3 State
`budgets`; proposed tables `x_read_ledger` (UTC day, resource id), `ig_hashtag_ledger` (account, hashtag, first used), `budget_reservations` (id, tag, charge, expires), `budget_history` (closed periods, kept as aggregates). Only a short row cache and the leader lock are in memory.

## 7. Limits, quotas and cost

The governor calls nothing external; its cost is cluster time. Decision rate is one per batch: at about 1,000,000 items a day and pages of 100 (Meta), 50 (Instagram) or 20 (TikHub), fetch calls alone number 10,000 to 50,000 a day, under one a second, before empty polls (to be measured in the pilot). One conditional Postgres update per decision is ample.

The budgets it protects, at full scale:
- X: 0.6M items a month at one read each is USD 3,000 a month, 20% of the 3,000,000-read cap (USD 15,000); user reads USD 0.010 each.
- TikTok amber: 7.5M items at 20 a page need at least 375,000 requests a month, USD 187.50 to USD 375.00 at USD 0.50 to 1.00 per 1,000 (billed on HTTP 200 only; 10 requests a second per endpoint).
- Facebook and Instagram amber: SociaVault USD 1.99 to 4.83 per 1,000 credits (1 credit a request), ScrapeCreators USD 0.99 to 1.88 per 1,000 requests; volumes to be measured in the pilot.
- Telegram: Apify actors USD 2,900 to 7,200 a month at 2.4M items (USD 1.21 to 3.00 per 1,000 items); Telemetrio USD 65 to 499 a month by plan.
- LinkedIn amber: harvestapi USD 225 to 300 a month at 0.15M items.
- Web search: Perplexity USD 5 per 1,000 requests, up to 5 queries each, about USD 60 a month at 60,000 queries; Mojeek GBP 3 per 1,000 queries, about GBP 180 a month; GDELT free.
- YouTube and Meta: no money, only quota.

## 8. Failure handling and fallback

- Governor unreachable: the SDK retries, then fails closed on amber and metered routes (no call without an `allow`); green quota-only routes may run priority 1 under a small local emergency allowance, reconciled on return.
- Crash with open reservations: TTL expiry releases them; counters err on the side of over-counting.
- Caller dies before `report`: reservation expires, charge stays until settled by the provider reconciliation.
- Drift: a daily reconciliation against provider figures (Meta headers, YouTube quota console, X usage, vendor dashboards and remaining-credit fields) raises `drift_detected` above the tolerance.
- Unbilled calls (non-200 on TikHub): `report` with `billed = false` releases the units.

## 9. Non-functional requirements

- Latency: one indexed round trip; p99 to be measured in the pilot.
- Throughput: section 7; stateless replicas, one leader for resets.
- Idempotency: `request_id` returns the same reservation; reports are applied once.
- Security: service-to-service authentication; ops role and audit row for any raise; no tokens or platform data held.

## 10. Metrics and alerts

`decisions_total{tag,decision,reason}`, `budget_used_ratio{tag}`, `budget_remaining{tag,unit}`, `budget_mode{tag}`, `stretch_factor{tag}`, `spend{tag,currency}`, `reservations_open`, `reservation_expired_total`, `x_ledger_dedup_total`, `meta_usage_pct{tag}`, `drift_ratio{tag}`, `decision_latency_seconds`, `jobs_total{status}`, `dlq_total`. Alerts through n8n: `budget_50`, `budget_80`, `budget_95`, `budget_exhausted`, `x_enterprise_required`, `quota_deny_rate`, `drift_detected`, `governor_unreachable`.

## 11. Dependencies

listening-sdk, every calling service, comment-decay-scheduler, backfill-orchestrator, source-health-canary, qualifier, registry-writer (client flags), n8n, Supabase Postgres and Vault, Prometheus and the dashboard tool.

## 12. Risks and mitigations

- Single point of failure: stateless replicas, fail-closed rules, emergency allowance.
- Counter drift from the provider: daily reconciliation, conservative over-counting.
- Priority inflation: priority derived from job kind, validated server-side.
- Stretch weakens the freshness promise on amber routes: disclosed to clients, bounded at daily.
- Vendor price changes: price table versioned; USD figures always from the table.

## 13. Acceptance criteria

1. An allowed request reserves its charge; a `report` of fewer units raises `remaining` by the difference; a `billed = false` report releases all of it.
2. 1,000 parallel requests of 10 units against 5,000 remaining yield exactly 500 allows and no counter above its limit.
3. Two requests for the same 100 X post ids on one UTC day charge 100 once; the next UTC day charges again; the 3,000,000th read is the last allowed, the next is `deny period_full`.
4. A YouTube `search` request beyond its bucket waits until reset and never borrows; `ingest` borrows from `comments`; `reserve` serves only priority 1.
5. A Meta report at 85% of the bucket gates priority 4 and 5; a throttle report yields `wait_until`.
6. The 31st distinct hashtag for one `ig_user_id` within 7 days waits until the oldest expires; a repeated hashtag is free.
7. At 80% of a monthly vendor budget the mode is `stretch`, priority 4 and 5 are denied and one alert fires; at 95% only priority 1 and 2 pass; at 100% all are denied; the reset clears the mode and re-arms the alerts.
8. A backfill request claiming priority 1 is treated as priority 5.
9. For any `stretch_factor`, the computed interval of every amber tier is at most 24 hours.
10. A government-flagged client on an X source, or a second client on X, raises `x_enterprise_required` within one minute.
11. Replaying a `request_id` returns the same reservation and charges once; an expired reservation is released.
12. With the governor stopped, an amber request is not sent.

## 14. Open questions

1. YouTube bucket sizes and the provider's reset time: to be set and confirmed in the pilot.
2. Should the 80% stretch also cover metered green routes (X, YouTube), for hot extras only?
3. Should X reads be denied for sources whose only clients are government bodies until Enterprise is acknowledged? Proposed: yes.
4. Charge TikHub at the upper USD 1.00 per 1,000 until the volume tier is confirmed?
5. Size of the green-route emergency allowance during an outage.
