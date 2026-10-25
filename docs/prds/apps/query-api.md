# query-api

**Platform:** Shared · **Route:** shared · **Lane:** Support · **Owner:** Backend lead (apps) · **Status:** Draft v0, 25 Oct 2026 (D3 round 1: open points marked `pending (Qn)`, answered in `docs/handoffs/D3.md`)

## 1. Why this service exists

Every number and every item a client sees comes out of ClickHouse and the control plane, and every one of them is bound by rules the pipeline already enforces upstream: who may see an item (ADR-0053), that ordinary people are never listed (ADR-0010), that government clients get no amber data and only allowed views (ADR-0052, CONVENTIONS v1.1 "Security and compliance"), that expired content is blank (ADR-0047), that YouTube figures stay per channel owner (ADR-0056), and that LinkedIn member content is never exported (ADR-0055). If the dashboard, the client portal and any later client integration each queried ClickHouse themselves, each would have to re-implement those rules, and one forgotten filter would show one client another client's data.

query-api is the one read path. It authenticates a person through Supabase Auth, resolves which client they act for and in which role, and answers a fixed set of read endpoints whose SQL it owns. Brief Q1 builds v0 of it (`build-plan/sessions/Q1-query-api-v0.md` L7); the dashboard (U1, U3) and the client portal (U2) are its only callers in v1.

## 2. Objective (the end state this service delivers)

End state: a signed-in person can read, for the client they belong to, every aggregate, item, source, public account, story and alert the dashboard and portal show, and nothing else; every response carries the provenance and retention facts the provenance statement needs.

Measurable targets:

- Zero responses that contain another client's rows: a test runs every endpoint as two clients over one fixture set and compares (`Q1 brief`, "Done when").
- Zero responses that list, rank or export an `author_ref` absent from `public_accounts_dim` (ADR-0010, ADR-0047).
- p95 latency below 1 s for aggregate endpoints over 90 days of hourly rows and below 2 s for item lists of 50 rows, at full scale (about 1,000,000 new items a day): targets for Q1's load test, confirmed in the pilot.

## 3. Scope

### In scope

- Authentication by Supabase Auth JWT; membership and role lookup; client scoping on every query (section 5.2).
- Read endpoints over `aggregates_hourly_v`, `aggregates_daily_v`, `aggregates_monthly_v`, the entity, brand and media-tag rollup, `hits`, `items_v`, `comments_v`, `analysis`, `metrics_timeseries`, `item_stories`, `sources_dim`, `keywords_dim` and `public_accounts_dim` (ADR-0047, ADR-0048), and over the control-plane tables a client may read: `keywords`, `client_lists`, `client_sources`, `alerts`, `alert_rules`, `clients` (its own row), `review_queue` rows a client may answer (pending (Q20)).
- Public-account lists, rankings, saved lists and segments (ADR-0010).
- Source views: the posts and engagement of a named source the client watches (pending (Q6)).
- Provenance on every item and the data for the client's provenance statement (ADR-0003).
- Exports, within platform limits (pending (Q9)).

### Out of scope

- Every write: the client portal and admin console write their tables and send `registry.decisions`; the admin API writes requests, deletions and flags (ADR-0012, ADR-0043, ADR-0044; `admin-console.md`).
- Computing aggregates (aggregator), matching (keyword-matcher), alerts (alert-evaluator).
- Ops views of the pipeline (admin console).
- An API for clients' own systems with API keys (pending (Q10)); alert webhooks stay alert-evaluator's (ADR-0067).

## 4. Users and consumers

- The dashboard (U1 slice, U3 full) reads every analytics endpoint.
- The client portal (U2) reads keywords, lists, sources, review items and the provenance statement.
- Client users act through those apps only; roles are those of section 9 (pending (Q5)).
- Account managers read a client's data under that client's scope when the client has granted them access (pending (Q5)).
- No service reads query-api.

## 5. How it works

### 5.1 Trigger and rotation

Request-driven; no rotation, no schedule, no jobs. Stateless replicas behind the cluster's ingress (ADR-0027), scaled on request rate.

### 5.2 Step by step

1. Verify the Supabase Auth JWT (signature, expiry, audience) and read the user id.
2. Load the user's memberships (`client_id`, role) from the portal's membership table (section 6.1) and the `client_id` the request names; refuse with 403 if the user is not a member. The client id is never taken from the URL alone.
3. Load the client's policy row once per request: `client_type` (a missing value fails closed, CONVENTIONS v1.1 L84), `accepts_amber`, `x_end_user_declared`, `accepted_flagged_vendors`, `status` (a client whose status is past `active` reads nothing: section 9); and `X_PLAN` and the public-account follower threshold from `feature_flags` (ADR-0050).
4. Build the query from the endpoint's fixed template with bound parameters; the client predicate is added by one function every template calls, and a linter test fails any template that lacks it.
5. Apply the item rules of 5.3 B to item-level results.
6. Return JSON with a `provenance` block per item, `as_of` (the aggregator watermark, `service_runs.last_success_at`, ADR-0045) on aggregate results, and a cursor for the next page.

### 5.3 The call it makes (the processing it performs)

**A. Client scope.**

- Mentions and every aggregate are scoped by `client_id`, which keyword-matcher set on each hit after its client gate: owner, watchers, pool, amber limited to accepting clients, the X gate (ADR-0053, ADR-0050, ADR-0052). A hit row for this client is the permission to show its item.
- Source views read items by `source_id` for a source in the client's `client_sources` (pending (Q6)); the item's visibility is then checked here with the same rule keyword-matcher applies, read from the contracts package's per-service visibility (`registries/visibility.json` on F2's branch, ADR-0053): `owner` only for the authorising client, `watchers` only for a client in the source's `client_ids`, `pool` for any watching client, amber only if `accepts_amber`, X only through the X gate.
- Government clients: no amber item, no X item unless `X_PLAN = enterprise` and declared (CONVENTIONS v1.1 L252); what else they may see is pending (Q7).

**B. Items.**

- Read only `items_v` and `comments_v`, which blank expired content (ADR-0047); an item with `is_deleted` or withheld for Iraq (mode `withhold`) is not returned (ADR-0035).
- Authors: every item carries `author_ref` only. Handle, display name and followers come from `public_accounts_dim` joined on `author_ref`; an author not in it is shown as "individual" with no identity, and is never a row of a list, a ranking or an export (ADR-0010).
- Platform exceptions (ADR-0010): TikTok and LinkedIn list organisation accounts only, Instagram business accounts only; `public_accounts_dim` already excludes the others.
- LinkedIn: comment text and commenter references of `linkedin_48h` items are returned to the in-app views only, never to an export, report or alert payload (`li-own-comments-fetcher §7 L136`, `§13 L179`; `li-notification-receiver §7 L142`); no endpoint returns a browsable feed of LinkedIn posts (`li-client-posts-poller §7 L134`); per-post LinkedIn views read base rows while they exist (ADR-0048).
- YouTube: a comment past its 30-day text clock is returned with `text_state = expired` and its scores (`yt-text-purger §4 L35`; ADR-0056); counts hidden by the platform are `null`, never 0 (`yt-video-details-fetcher §5.4 L78`).
- Links to individuals' own posts and comments: pending (Q11).

**C. YouTube across owners.** Aggregates carry `video_channel_id` on YouTube rows (ADR-0048). An endpoint that would sum YouTube views, likes or comment counts over channels of different owners returns them per channel instead, outside the carve-out (ADR-0056); whether keyword mention counts may be summed across channels is pending (Q8).

**D. Endpoints (v1).** All under `/v1/clients/{client_id}`; JSON; keyset pagination; time in UTC, shown in Asia/Baghdad by the apps.

| Endpoint | Reads | Notes |
|---|---|---|
| `GET /aggregates/series` | aggregate `_v` views | `measure` = mentions, reach, engagement, views, stories; `grain` = hour, day, month; filters keyword, platform, source, sentiment, topic, lang, dialect, route, kind (ADR-0048) |
| `GET /aggregates/breakdown` | aggregate views, entity rollup | one dimension; shares with `mixed` in the denominator, `pending` and `unscored` out (ADR-0048) |
| `GET /mentions` | `hits` ⋈ `items_v`/`comments_v` ⋈ `analysis` | the mention list; text search folded through lang-dialect-id `/v1/fold` (`store-writer §5.3`, text index) |
| `GET /items/{item_id}` | as above, `metrics_timeseries`, `item_stories` | provenance, analysis, the metrics observations with their labels, the story (`fb-reactions-fetcher §3 L19`) |
| `GET /sources` and `/sources/{source_id}` | `client_sources`, `sources_dim` | the client's watched sources, health, tier, `backfill_status`, route and vendor |
| `GET /sources/{source_id}/posts` and `/engagement` | `items_v`, `metrics_timeseries` | pending (Q6); the App Review slice uses them |
| `GET /public-accounts` | `public_accounts_dim` ⋈ hits | rank by mentions, reach or engagement; filter by platform, kind, saved list |
| `GET /lists` | `client_lists` | seed, watch and saved entries; named lists pending (Q12) |
| `GET /stories` | `item_stories`, `stories` measure | "also published by N outlets", origin named "earliest seen" (`news-dedup §4 L33`, `§12 L146`) |
| `GET /alerts`, `/alert-rules` | `alerts`, `alert_rules` | read only; rules are written by the rule editor (`dashboard.md`) |
| `GET /keywords` | `keywords` | the client's own rows, `screening_status` included |
| `GET /provenance` | `sources_dim`, `clients`, the class table | the provenance statement's data (`client-portal.md` 5.3 F) |
| `GET /exports/...` | as the view exported | pending (Q9) |

Segments: any endpoint takes `segment=saved:<list>` (a saved list of public accounts, ADR-0010, ADR-0043), or an anonymous segment of ordinary people by language, dialect, route, kind, sentiment, topic or governorate (ADR-0010, ADR-0048); a segment is never built on a sensitive attribute (CONVENTIONS v1.1 L256).

### 5.4 What it gets

Rows of the tables in 6.1, through bound queries. It does not get raw payloads, cached full text (only keyword-matcher reads the news cache, ADR-0022), author identities other than public accounts, or another client's rows.

## 6. Inputs and outputs

### 6.1 Reads

- ClickHouse (read-only user): the tables and views of 5.3 D, F8's names (ADR-0047).
- Postgres (read-only role): `clients`, `client_settings`, `client_lists`, `client_sources`, `keywords`, `alerts`, `alert_rules`, `feature_flags`, `service_runs` (aggregator's `last_success_at`, a typed column ADR-0045 lets apps read), `retention_classes`; the portal's membership table (`client_members`, a name for F3 or the portal's own table, pending (Q5)).
- Supabase Auth: JWT verification keys.

### 6.2 Writes

None to any shared table or topic. Structured JSON logs with `request_id`, `user_id`, `client_id`, endpoint and row counts, never item text or identities.

Example response (one mention):

```json
{
  "item_id": "6f1c2a9e-3b4d-5e6f-8a9b-0c1d2e3f4a5b",
  "kind": "post", "platform": "facebook", "created_at": "2026-10-20T09:14:00Z",
  "text": "…", "text_state": "present",
  "author": {"public": true, "display_name": "Example Page", "source_id": "a3c0f1e2-5b6d-4c7e-9f80-112233445566"},
  "sentiment": "negative", "topics": ["global:outage"],
  "metrics": {"likes": 120, "comments": 14, "shares": 9, "observed_at": "2026-10-21T09:14:00Z", "label": "plus_24h"},
  "provenance": {"route": "green", "vendor": null, "service": "fb-page-feed-poller", "fetched_at": "2026-10-20T09:31:12Z"},
  "retention_class": "meta_on_request"
}
```

### 6.3 State

None beyond a per-replica cache of verification keys and of each client's policy row (at most 30 s, so a change of `accepts_amber` or `client_type` applies within 30 s).

## 7. Limits, quotas and cost

No external API or vendor; no `budget_tag`. Cost is ClickHouse CPU: every template is bounded by a time window (at most 400 days on hourly rows, ten years on monthly rows) and a page size (at most 200 items). A per-user rate limit protects ClickHouse; its value is set in Q1's load test.

## 8. Failure handling and fallback

- ClickHouse unavailable or slow past 10 s: 503 with `retry_after`; no partial result is returned as complete.
- Aggregator watermark older than three cycles: aggregate responses carry `stale = true` (`alert-evaluator §5.2 L46` uses the same test).
- Missing `client_type`, unknown role, or a membership lookup error: 403 (fail closed).
- A template that returns an `author_ref` without a public-account match in a list or ranking: the row is dropped and `author_leak_blocked_total` counts it; any non-zero value alerts.

## 9. Non-functional requirements

- Isolation: the client predicate of 5.2 step 4 in every template, tested per endpoint with two clients; Postgres reads through row-level security on `client_id` as a second line.
- Client status: a client whose `status` is `offboarding` or later reads nothing; its users are told to ask their account manager for the offboarding evidence (`retention-purger §4 L35`).
- Roles: pending (Q5); until answered, Q1 builds `client_admin` and `client_viewer`, both read-only here.
- Idempotent and side-effect free: every endpoint is a GET.
- Languages: responses carry data as stored; labels are the apps' concern (pending (Q4)).
- Security: TLS only; no secret in logs; the ClickHouse and Postgres users have read grants on the listed objects only.

## 10. Metrics and alerts

`http_requests_total{endpoint,status}`, `request_latency_seconds{endpoint}`, `clickhouse_query_seconds{template}`, `rows_returned_total{endpoint}`, `cross_client_rejected_total`, `author_leak_blocked_total`, `stale_responses_total`. Alerts: `author_leak_blocked` (any), `latency_p95_high` (above the section 2 targets for 15 minutes), `error_rate_high` (5xx above 1% for 5 minutes).

## 11. Dependencies

F8's ClickHouse tables and views; F3's tables; store-writer (C6) and aggregator (C15) filling them; keyword-matcher's gate (C5); lang-dialect-id `/v1/fold` (C3) for text search; Supabase Auth; the contracts package's visibility registry (F2).

## 12. Risks and mitigations

- A new endpoint forgets the client predicate: the template linter and the two-client test run in CI.
- An author list leaks an ordinary person: lists join only `public_accounts_dim`, and the drop-and-count guard of section 8.
- Heavy ad-hoc filters overload ClickHouse: fixed templates, bounded windows, the rate limit.

## 13. Acceptance criteria

1. Every endpoint, run as client A and client B over one fixture set with overlapping sources, returns no row of the other client.
2. A request naming a client the user is not a member of returns 403 and reads nothing.
3. A client with `client_type` null receives 403 on every endpoint.
4. An `owner` item (a client-owned Page's webhook post) is returned to its owner and not to a second client that watches the same Page (ADR-0053).
5. An amber item is never returned to a client with `accepts_amber = false`, nor to a government client.
6. An X item is not returned to a client while `X_PLAN = pay_per_use` and `x_end_user_declared = false`.
7. `/public-accounts` never returns an `author_ref` absent from `public_accounts_dim`; a TikTok person account, an Instagram creator account and a LinkedIn member are never returned.
8. A YouTube comment past 30 days is returned with `text_state = expired` and no text; a hidden count is `null`.
9. A `linkedin_48h` comment's text appears in `/mentions` while it exists and never in an export.
10. A deleted item (`is_deleted`) and an item withheld for Iraq are absent from every endpoint.
11. Shares from `/aggregates/breakdown` count `mixed` in the denominator and add up to 100%.
12. Every item returned carries `provenance {route, vendor, service, fetched_at}` and `retention_class`.
13. Aggregate responses carry `as_of`; with the watermark three cycles old they carry `stale = true`.
14. YouTube views summed over two channels of different owners are returned per channel (5.3 C).

## 14. Open questions

Pending the user's answers in `docs/handoffs/D3.md`: Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q20; Q1 (who builds the admin API it does not depend on) and Q3 (front-end) affect its callers only.
