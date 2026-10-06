# tg-channel-resolver

**Platform:** Telegram · **Route:** amber (optional, flag `TG_VENDOR_ROUTE`) · **Lane:** Discover and qualify · **Owner:** Ingestion lead, Telegram · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The qualifier cannot decide anything about a Telegram channel it knows only by username. It needs reach (subscribers, for the tier), a country signal (for the Iraqi-signals rule), a category and a growth figure (for activity and spam hints), and the channel's title. The Bot API provides those facts only for channels the bot has been added to as an administrator, through `getChat` and `getChatMemberCount`, and tg-bot-channel-receiver fills them in itself at onboarding. For every other channel, the ones tg-message-search finds or a client pastes as a t.me link, there is no official call: bots see nothing in channels they are not added to, and Telegram's Content Licensing Terms prohibit access "for any purpose other than ordinary, legitimate, and intended use of the Telegram platform as its user", which on our reading bars user-account readers and t.me preview scraping. We build neither.

So channel facts about third-party channels are bought from Telemetrio (Estonia, cleared), whose channel stats give subscribers, category, country and growth. That makes this an amber service: the collection and any breach sit with the vendor; it is optional and gated by `TG_VENDOR_ROUTE`; its provenance is disclosed to clients; and it is excluded from government contracts. It is politically exposed as well: after Iraq's blocks of Telegram in August 2023 and from 3 April to 9 May 2026, a vendor-fed map of Iraqi channels is an asset the product must be able to switch off.

Without tg-channel-resolver every Telegram candidate from search or from a client link lands on the qualifier with no reach and no country, goes to a review card and is rejected by default after 24 hours. The registry never grows from Telegram discovery and tg-channel-posts-poller has nothing to rotate. The resolver is also the gate on Actor spend: every channel it resolves and the qualifier accepts becomes a channel the poller pays for.

## 2. Objective (the end state this service delivers)

Every Telegram candidate placed on `jobs.tg-channel-resolver` is answered with a `poster.profiles` message, a profile or an `unresolved` verdict with a reason, before the qualifier's 24-hour review default expires. Measurable target: 100% of candidates answered within 24 hours; registry channels on the amber route re-resolved every 30 days so tiers track reach; vendor use kept inside the plan's channel allowance by quota-governor. Country accuracy and the share of candidates the vendor does not index are to be measured in the pilot.

## 3. Scope

### In scope
- Resolving public third-party channels by username or t.me link through Telemetrio channel stats.
- Attaching the language share lang-dialect-id computed on the candidate's hit items, so the qualifier can apply the 40% Iraqi Arabic or Sorani rule.
- A 30-day subscriber refresh for registry channels on the amber route, feeding tier changes through the qualifier.
- Caching: a profile younger than 30 days is reused without a vendor call.

### Out of scope
- Channels where our bot is an administrator: tg-bot-channel-receiver resolves them through the Bot API at onboarding and at its daily check.
- Posts (tg-channel-posts-poller), search (tg-message-search), comments (no route on third-party channels).
- Private channels and invite links (`t.me/+...`): no vendor can see them; they are answered `unresolved: private`.
- Individuals: this service only resolves `source_type = channel`; a user who comments in a discussion group is never looked up.
- Candidates owned by government clients: answered `unresolved: amber_excluded`, and the client is told to ask the channel owner to add the bot.

## 4. Users and consumers

- qualifier consumes `poster.profiles` and writes `registry.decisions`; registry-writer turns accepted profiles into `sources` rows with `route = amber`, `vendor = telemetrio` and a tier.
- poster-resolver is the caller: it fans Telegram candidates from `discovery.hits` out to this service.
- Clients see the resolved channel with its subscriber count and the amber provenance statement; ops sees unresolved reasons in `review_queue`.

## 5. How it works

### 5.1 Trigger and rotation

The service is job-driven, with one scheduled refresh.

- Triggers: poster-resolver emits a job for every Telegram poster on `discovery.hits` that is not in `sources` and not rejected in `decisions` within 180 days; client and ops adds emit a job; the scheduler emits a `refresh` job for every registry channel with `route = amber` whose profile is older than 30 days.
- Ordering: jobs on `jobs.tg-channel-resolver` are partitioned by `source_id` (or by handle for candidates without a row), ordered by job age, with `refresh` jobs behind discovery and client jobs.
- Catch-up: after an outage the queue drains oldest first; a late refresh is not an incident.
- Budget: `refresh` jobs are stretched by quota-governor at 80% of the plan's channel allowance; discovery and client jobs are never stretched, only denied with a reason the client sees.
- Flag: read at the start of every job; `off` answers `unresolved: route_off` without a vendor call.

### 5.2 Step by step

1. A job arrives: `{job_id, candidate (username or t.me URL), origin (discovery|client|ops|refresh), client_ids, hit_item_keys, attempt}`.
2. The handle is normalised: `t.me/`, `@` and case stripped; `t.me/+` and `joinchat` links are answered `unresolved: private` at once.
3. The flag, the owning clients' government flag, and the cache (`poster.profiles` younger than 30 days) are checked, in that order.
4. quota-governor is asked for one unit under `budget_tag = tg_telemetrio_stats`.
5. The Telemetrio channel stats call is made for the handle.
6. The response is written to `raw.items` with `kind = profile`, then mapped: subscribers to `followers`; country to `country_signals.vendor_country`; category and growth as given; any `+964` number, `.iq` link or Iraqi city or governorate name in the title to `country_signals.text_signals`.
7. The language share over the candidate's hit items is read from `items.normalized`; with fewer than 20 items it is marked `unknown`.
8. The profile is emitted to `poster.profiles`, the batch is acknowledged, `service_runs` and `cost_units` are written.

### 5.3 The call it makes

Telemetrio channel stats, one request per channel, authenticated with the Telemetrio API key from `vendor_keys` in Supabase Vault. The input is the channel username. The response carries subscribers, category, country and growth. The stats path and parameter names come from the vendor reference, pinned in the adapter and covered by a contract test. The call is covered by the subscription plan (USD 65 a month for 500 channels to USD 499 a month for 2,500 channels); whether a request on a channel outside the plan's allowance is billed or refused is to be confirmed in the pilot. No pagination.

### 5.4 What it gets

Subscribers, category, country, growth and the channel's title and username. It does not get posts (tg-channel-posts-poller), administrators or their identities, member lists, private channels, comment counts (comments on third-party channels have no route), or language, which we compute ourselves. Country is the vendor's estimate, not a declared location, so it counts as one Iraqi signal, not two.

## 6. Inputs and outputs

### 6.1 Reads
- Queue: `jobs.tg-channel-resolver`.
- Topics: `items.normalized` (language share of hit items), `poster.profiles` (cache).
- Control plane: `sources`, `decisions`, `clients`, `client_sources`, `budgets`, `vendor_keys`, `cursors`.

### 6.2 Writes
- `raw.items` (the vendor response, `kind = profile`), `poster.profiles`, `service_runs`, `dlq.tg-channel-resolver`.

Example `poster.profiles` message:

```json
{
  "schema": "poster.profiles/v1",
  "idempotency_key": "telegram:profile:basra_prices",
  "platform": "telegram",
  "source_type": "channel",
  "platform_id": "basra_prices",
  "handle": "basra_prices",
  "display_name": "أسعار البصرة",
  "followers": 48210,
  "country_signals": {"vendor_country": "IQ", "text_signals": ["البصرة"]},
  "category": "news",
  "growth": {"subscribers_30d": 1930},
  "lang_share": {"ar-iq": 0.71, "ar": 0.24, "ckb": 0.05, "sample": 34},
  "status": "resolved",
  "route": "amber",
  "vendor": "telemetrio",
  "service": "tg-channel-resolver",
  "fetched_at": "2026-10-06T03:40:12Z",
  "retention_class": "vendor_agreed"
}
```

An unresolved answer carries the same envelope with `status` set to `not_found`, `not_indexed`, `private`, `route_off` or `amber_excluded` and no profile fields.

### 6.3 State
- A `cursors` row per registry channel for `service = tg-channel-resolver`: `cursor` holds the last profile time, driving the 30-day refresh.
- Counters in `budgets` under `tg_telemetrio_stats`: requests this month and distinct channels queried against the plan allowance.

## 7. Limits, quotas and cost

- Telemetrio plans: USD 65 a month at 500 channels up to USD 499 a month at 2,500 channels. The channel allowance is the route cap of qualifier rule 5: over it, new Telegram sources queue by reach and the client is told.
- Every channel resolved and accepted joins the Actor rotation, which costs about USD 2,900 to 7,200 a month at 2.4M items; the resolver is where Telegram spend is decided, and the qualifier's reach and Iraqi-signal rules are the brake.
- Comments on third-party channels have no route: a profile never carries comment counts, and a client adding a third-party channel is told that only posts, views and forwards will follow.

## 8. Failure handling and fallback

- HTTP 429 or a vendor rate limit: exponential backoff with jitter from 30 s to 15 min, then the job returns to the queue with `attempt + 1`; after 5 attempts it goes to `dlq.tg-channel-resolver` and an alert fires.
- HTTP 401 or 403: route marked `degraded`, batch stopped, alert; no key rotation.
- Channel not found: `unresolved: not_found`; the qualifier rejects and remembers for 180 days. Not indexed by the vendor: `unresolved: not_indexed`; the qualifier raises a review card, where ops may ask the owner to add the bot.
- Empty 200 above 5% in 15 minutes: source-health-canary flips `health = degraded`; no alternate stats route exists, so jobs wait rather than fail.
- Schema change: raw archived, `schema_unknown`, batch parked.
- Iraq block: no effect on resolution (vendor and cluster sit outside Iraq); growth figures drop, and the qualifier's activity rule decides dormancy.

## 9. Non-functional requirements

- Throughput: candidates per day follow tg-message-search hits and client adds, to be measured in the pilot; one vendor request per candidate.
- Latency: a discovery or client job is answered inside the 24-hour review default; p95 measured in the pilot.
- Idempotency: `telegram:profile:<username>`; profiles are versioned by `fetched_at`; a replayed job re-emits the same profile.
- Scaling: on `jobs.tg-channel-resolver` depth, capped by the vendor's rate limit.
- Security: vendor key from Supabase Vault; no government client's candidate is sent to the vendor; no individual is ever resolved; structured JSON logs with `job_id`, `source_id`, `route`, `vendor`; `/healthz` and `/metrics`.

## 10. Metrics and alerts

Standard: `jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`. Service-specific: `resolve_total{status=resolved|not_found|not_indexed|private|route_off|amber_excluded}`, `cache_hits_total`, `plan_channels_used`, `refresh_age_seconds_p95`. Alerts: `dlq_total` above zero; `plan_channels_used` at 80% and 100% of the allowance; `not_indexed` share rising; route `degraded`.

## 11. Dependencies

`listening-sdk`; poster-resolver (caller) and qualifier (consumer); registry-writer; lang-dialect-id and normalize-item (language share); quota-governor; source-health-canary; raw-archiver; tg-bot-channel-receiver (resolves bot channels instead); the Telemetrio contract and the author notice required by `vendor_agreed`; the `TG_VENDOR_ROUTE` flag.

## 12. Risks and mitigations

- Plan allowance exhausted by discovery noise: the qualifier's reach rule and the 180-day rejection memory limit repeat lookups; `plan_channels_used` alerts at 80%.
- Vendor country wrong for Iraqi channels run from abroad: the language share and text signals give the qualifier two further signals; borderline cases go to review.
- Vendor does not index small Iraqi channels: measured in the pilot; the fallback offered to clients is the green route.
- Political exposure: flag default `off`, disclosure, no government clients.

## 13. Acceptance criteria

1. With `TG_VENDOR_ROUTE=off`, a candidate is answered `unresolved: route_off` within the job and the vendor mock records zero calls.
2. A `t.me/+` or `joinchat` link is answered `unresolved: private` with zero vendor calls.
3. A candidate whose only owning client is flagged government is answered `unresolved: amber_excluded` with zero vendor calls.
4. A candidate resolved within the last 30 days is answered from `poster.profiles` without a vendor call and `cache_hits_total` increments.
5. A resolved profile carries `followers`, `country_signals.vendor_country`, `category`, `growth`, `route=amber`, `vendor=telemetrio`, `service=tg-channel-resolver`, `fetched_at` and the key `telegram:profile:<username>`.
6. With fewer than 20 normalised hit items, `lang_share` is `unknown`; with 20 or more it carries shares that sum to 1 and the sample size.
7. The vendor response is on `raw.items` with `kind = profile` before the profile is on `poster.profiles`.
8. A registry channel with `route = amber` and a profile older than 30 days receives a `refresh` job whose profile reaches the qualifier.
9. HTTP 429 backs off from 30 s to a 15 min ceiling, 5 attempts, then `dlq.tg-channel-resolver` and an alert.
10. HTTP 401 or 403 marks the route `degraded`, stops the batch and alerts; no other key is tried.
11. A response of unknown shape is archived and parked as `schema_unknown` with nothing on `poster.profiles`.

## 14. Open questions

1. The Telemetrio stats path, parameters and the semantics of the plan's channel allowance (tracked channels or distinct channels queried per month).
2. Whether to buy a 20-post Actor sample for candidates with exactly one Iraqi signal, so review cards carry a language share, and at what cost per candidate.
3. `TG_VENDOR_ROUTE` holds one vendor name while Telegram uses Telemetrio and Apify in different roles; this service treats any value other than `off` as on.
4. Whether the stats response includes the channel description, which would add `+964` and `.iq` signals beyond the title.
