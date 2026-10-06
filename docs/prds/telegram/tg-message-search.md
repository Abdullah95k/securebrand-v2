# tg-message-search

**Platform:** Telegram · **Route:** amber (optional, flag `TG_VENDOR_ROUTE`) · **Lane:** Discover and qualify · **Owner:** Ingestion lead, Telegram · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

Telegram carries 2.4M of the 30.5M items a month in the full-scale target, and in Iraq it is where news channels and political movements publish first. The product promises that a mention of a client's brand is found wherever it appears, not only on channels somebody already registered. On Telegram there is no official way to keep that promise: the Bot API only sees channels and discussion groups the bot has been added to (as an administrator in channels, as a member in groups), with no history method and no search. Telegram's Content Licensing Terms prohibit access "for any purpose other than ordinary, legitimate, and intended use of the Telegram platform as its user", which on our reading covers user-account readers and t.me preview scraping alike, so we build neither.

The only remaining route is to buy search results from a screened vendor that does the collection itself. Telemetrio (Estonia, cleared under the 6 Oct 2026 vendor rule) sells keyword search over its index of public channels through `/v1/search/messages`. That makes this an amber service: the breach, if any, sits in the vendor's contract rather than ours; the service is optional, switched on per deployment by `TG_VENDOR_ROUTE`; its provenance is disclosed to every client that sees its output; and it is excluded from government contracts. It is also politically exposed: Iraq blocked Telegram in August 2023 and again from 3 April to 9 May 2026, and an Iraqi company paying a foreign vendor to index Telegram during a block is a headline we do not want.

Without it the product loses Telegram discovery entirely: the registry grows only from client seed lists and channels that add our bot, a brand crisis that starts on an unknown channel stays invisible until a client pastes the link, and the qualifier never sees a Telegram candidate. tg-channel-posts-poller would still fetch known channels, but nothing would tell it which channels matter.

## 2. Objective (the end state this service delivers)

Every enabled Telegram keyword set is searched once a day against Telemetrio; every returned message lands on `raw.items` with full provenance; every hit is routed to `item.hits` when the channel is in the registry or to `discovery.hits` when it is not, where poster-resolver and the qualifier take over. Measurable target: one successful run per keyword set per UTC day, with search lag below one day for 99% of enabled sets; zero jobs lost, DLQ reviewed daily; monthly spend held inside the Telemetrio budget by quota-governor. Results per request and hit precision against keyword-matcher are to be measured in the pilot.

## 3. Scope

### In scope
- Daily keyword search through Telemetrio `/v1/search/messages` for every keyword set that includes Telegram and belongs to a non-government client.
- A 90-day first run per new keyword set (the search backfill), then daily 7-day windows.
- Routing of each result to `item.hits` or `discovery.hits`; archival of every result on `raw.items`.
- Budget accounting through quota-governor; canary, schema-change and flag handling.

### Out of scope
- Resolving the channels found (tg-channel-resolver), fetching their later posts (tg-channel-posts-poller), and channels that add our bot (tg-bot-channel-receiver, tg-discussion-receiver).
- Comments on the messages found: no route exists to comments on third-party Telegram channels.
- Any collection by us, and any second search vendor not on the cleared list.
- Keyword sets of government clients: never submitted, since the output could not reach them and the keywords would leave our contract boundary.

## 4. Users and consumers

- Clients (brands and companies) see Telegram mentions and newly discovered channels, each carrying the amber provenance statement naming Telemetrio.
- poster-resolver and qualifier consume `discovery.hits`; normalize-item, lang-dialect-id and keyword-matcher consume `raw.items`; store-writer, aggregator and alert-evaluator sit downstream.
- Ops reads `/metrics` and the DLQ; Abdullah reads vendor spend and hit counts to decide whether the flag stays on.

## 5. How it works

### 5.1 Trigger and rotation

The rotation unit is the keyword set, a registry row of `source_type = keyword_rule` with its own `cursors` row for `service = tg-message-search`.

- Cadence: once per UTC day per enabled set. The scheduler keeps `next_poll_at` and emits a job to `jobs.tg-message-search` when due; jobs are ordered by `next_poll_at` then by the owning client's priority list, so a set is never skipped twice in a row; the next run is set from the start of the last run.
- Window: 7 days, the vendor minimum, so each run overlaps the previous six and duplicates drop out by idempotency key. A new set's first run uses 90 days, the vendor maximum and the backfill rule.
- Catch-up: more than one day behind, the most-stale sets run first and `rotation_behind` fires.
- Budget: a daily cadence cannot be stretched below daily, so at 80% of the monthly budget quota-governor answers wait-until for the sets lowest on client priority lists and at 100% denies; a denied set is reported to its client.
- Flag: read at the start of every job; `off` acknowledges the job as `skipped_flag_off` without a vendor call.

### 5.2 Step by step

1. The scheduler emits `{job_id, set_id, keyword_ids, window_start, window_end, attempt}` to `jobs.tg-message-search`.
2. The worker reads `TG_VENDOR_ROUTE`, confirms in `clients` that the owner is not a government body, and asks quota-governor for allowance under `budget_tag = tg_telemetrio_search`.
3. For each keyword and each spelling variant it calls `/v1/search/messages` and pages until the vendor reports no more results or the per-run page cap (set in the pilot) is reached.
4. For each message it builds `idempotency_key = telegram:post:<channel_username>/<message_id>`, looks the channel up in `sources` (`platform = telegram`, `platform_id = username`), and checks `decisions` for a rejection inside the last 180 days.
5. It emits the message to `raw.items`, then a hit to `item.hits` (registered channel) or `discovery.hits` (unknown channel). A channel rejected within 180 days gets `raw.items` only and a `hits_total{kind=suppressed}` count.
6. After Redpanda acknowledges the batch it advances the cursor, writes `service_runs` and reports `cost_units`.

### 5.3 The call it makes

Telemetrio `/v1/search/messages` (alpha). Authentication: the Telemetrio API key from `vendor_keys` in Supabase Vault. Parameters: the keyword or quoted phrase; the window start and end, which must span between 7 and 90 days; a pagination cursor. Exact parameter names, page size and maximum results per request come from the vendor reference, pinned in the adapter and covered by a contract test. Pricing is per request and per keyword; each spelling variant counts as a keyword, so the adapter reports requests made and keywords submitted as two `cost_units` counters. Keyword text never appears in logs; the log line carries `keyword_id`.

### 5.4 What it gets

Per message: channel username and title, message id, publication date, text, and the views and forwards the index holds; media is flagged, not downloaded. It does not get comments (no route), reactions, subscriber counts (the channel stats call belongs to tg-channel-resolver), private channels, messages older than 90 days, or anything Telemetrio has not indexed. A response of unknown shape is archived and parked as `schema_unknown`.

## 6. Inputs and outputs

### 6.1 Reads
- Queue: `jobs.tg-message-search`.
- Control plane: `keywords`, `clients`, `client_sources`, `sources`, `decisions`, `cursors`, `budgets`, `vendor_keys`, `canary_targets`.

### 6.2 Writes
- `raw.items` (every result as returned, plus envelope), `item.hits`, `discovery.hits`, `service_runs`, `dlq.tg-message-search`.

Example `discovery.hits` message:

```json
{
  "schema": "discovery.hits/v1",
  "idempotency_key": "telegram:post:basra_prices/18231",
  "platform": "telegram",
  "kind": "post",
  "poster": {"platform_id": "basra_prices", "handle": "basra_prices", "display_name": "أسعار البصرة", "source_type": "channel"},
  "keyword_ids": ["kw_7f3a"],
  "client_ids": ["cl_a1b2"],
  "route": "amber",
  "vendor": "telemetrio",
  "service": "tg-message-search",
  "fetched_at": "2026-10-06T03:12:44Z",
  "retention_class": "vendor_agreed"
}
```

### 6.3 State
- One `cursors` row per keyword set: `cursor` holds the last window end as an ISO timestamp, plus `last_success_at`, `last_error`, `consecutive_errors`.
- Counters in `budgets` under `tg_telemetrio_search`: requests and keywords this month.

## 7. Limits, quotas and cost

- Telemetrio subscription plans run from USD 65 a month (500 channels) to USD 499 a month (2,500 channels); search is priced per request and per keyword on top.
- Cost driver: keywords × spelling variants × days × pages. The 7-day minimum window means daily runs pay again for six days already seen; a weekly cadence would cut requests sevenfold at the price of seven days of latency (open question 1).
- Comments on third-party channels have no route at any price: Telemetrio returns posts, the Apify preview Actors report comments as mostly unavailable, and the Bot API sees only groups it has been added to. A mention found by search therefore carries no comment thread.

## 8. Failure handling and fallback

- HTTP 429 or a vendor rate limit: exponential backoff with jitter from 30 s to 15 min, then the job returns to the queue with `attempt + 1`; after 5 attempts it goes to `dlq.tg-message-search` and an alert fires.
- HTTP 401 or 403: the route is marked `degraded`, the batch stops, an alert fires; keys and addresses are never rotated.
- Empty 200 above 5% in 15 minutes: source-health-canary flips `health = degraded`. No alternate route exists for search (the Actors cannot search), so the service pauses.
- Schema change: raw payload archived, `schema_unknown` raised, batch parked for review.
- Iraq block: Iraqi posting drops while the vendor keeps answering; the canary target is a keyword that hits daily on a channel the team owns, so an index outage is told apart from a quiet country.

## 9. Non-functional requirements

- Throughput: the search's share of Telegram's 2.4M items a month is to be measured in the pilot and the worker count sized from it.
- Latency: every enabled set completes inside its UTC day.
- Idempotency: `raw.items` is append-only, normalize-item deduplicates on the key, jobs carry `attempt` and are replayable, cursors advance only after Redpanda acknowledges.
- Scaling: on `jobs.tg-message-search` depth, concurrency capped at the vendor's rate limit.
- Security: vendor key from Supabase Vault only; no government client's keyword leaves the cluster; structured JSON logs with `job_id`, `source_id`, `route`, `vendor`; `/healthz` and `/metrics` exposed.

## 10. Metrics and alerts

Standard: `items_fetched_total`, `items_new_total`, `jobs_total{status}`, `fetch_latency_seconds`, `rotation_lag_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`. Service-specific: `search_requests_total`, `search_keywords_total`, `hits_total{kind=registered|discovery|suppressed}`, `results_per_request`, `empty_200_ratio`. Alerts: `rotation_behind`; `dlq_total` above zero; `quota_denied_total` rising; empty-200 canary; Telemetrio budget at 80% and 100%; route `degraded`.

## 11. Dependencies

`listening-sdk`; quota-governor; source-health-canary; poster-resolver and qualifier (consumers of `discovery.hits`); normalize-item, lang-dialect-id, keyword-matcher, raw-archiver (consumers of `raw.items`); registry-writer (keeps `sources` current for step 4); the Telemetrio contract, including the author notice the `vendor_agreed` retention class requires; the `TG_VENDOR_ROUTE` flag.

## 12. Risks and mitigations

- Alpha endpoint changes without notice: contract test on every deploy, `schema_unknown` parking, adapter pinned to a vendor version.
- Vendor coverage of Iraqi channels unknown: measured in the pilot against the seed list before the flag goes on for paying clients.
- Political exposure after the 2023 and 2026 blocks: flag default `off`, provenance disclosed, no government clients, block policy in open question 5.
- Cost growth through spelling variants: variants per keyword capped per client; governor at 80%.
- Vendor ownership drift: Telemetrio re-screened against constraint 1 at every renewal.

## 13. Acceptance criteria

1. With `TG_VENDOR_ROUTE=off`, a due job completes as `skipped_flag_off` and the vendor mock records zero calls.
2. With the flag on, each enabled set runs once per UTC day and a second run that day is not emitted.
3. Killing the worker between vendor response and Redpanda ack makes the next attempt re-emit the same messages with identical keys, and normalize-item stores one copy.
4. A keyword set owned by a government client ends as `skipped_government` with zero vendor calls.
5. A result from a registered channel produces `item.hits`; from an unknown channel `discovery.hits`; from a channel rejected within 180 days neither, with `raw.items` written and `hits_total{kind=suppressed}` incremented.
6. Every `raw.items` message carries `route=amber`, `vendor=telemetrio`, `service=tg-message-search`, `fetched_at` and a key of the form `telegram:post:<channel_username>/<message_id>`.
7. The first run of a new set requests a 90-day window; later runs request 7-day windows.
8. HTTP 429 triggers backoff from 30 s with a 15 min ceiling, 5 attempts, then `dlq.tg-message-search` and an alert.
9. HTTP 401 or 403 marks the route `degraded`, stops the batch and fires an alert; no other key is tried.
10. A governor deny makes the job wait, not fail; `cost_units` per run equals the mock vendor's request and keyword counts.
11. Empty 200 above 5% in 15 minutes flips `health = degraded` and pauses scheduling until the canary clears.

## 14. Open questions

1. Daily runs with 7-day windows or weekly runs: decide once the pilot gives the per-request and per-keyword prices.
2. `TG_VENDOR_ROUTE` carries one vendor name, but Telegram's amber route uses Telemetrio for search and stats and Apify for posts; this service treats any value other than `off` as on. Confirm or split the flag.
3. Should mentions on channels the qualifier rejected still reach client dashboards?
4. Telemetrio's parameter names, page size, rate limit and alpha support terms.
5. Policy during an Iraq block: pause the vendor route, continue, or let each client choose.
