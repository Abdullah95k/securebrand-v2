# li-org-resolver

**Platform:** LinkedIn · **Route:** amber (optional, flag `LI_VENDOR_ROUTE`) · **Lane:** Discover and qualify · **Owner:** Registry lead (Node) · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

The registry admits a LinkedIn company page only when the qualifier can apply its rules: Iraqi signals (any two of an Iraqi city or governorate in the location, a +964 number, an .iq domain or Iraqi outlet link, at least 40% Iraqi Arabic or Sorani on the last 20 posts, membership of a client seed list), activity in the last 30 days, the spam test, and a tier by reach. Candidates arrive from three directions: author pages on `discovery.hits` found by li-post-search, seed lists a client supplies at onboarding, and pages ops type in. None of them comes with the facts the qualifier needs. li-org-resolver turns a URL or handle into a `poster.profiles` record carrying those facts.

The Community Management API, our green route, reaches only pages the client administers: with the client's token it can confirm the client's own organization URN and that access was granted, but it cannot look up any third-party page. harvestapi Actors on Apify are the optional route to third-party pages: the resolver runs `linkedin-company-posts` for the page URL with a small max items and reads the page identity and its last 20 posts from the result. The route is gated by `LI_VENDOR_ROUTE`, disclosed to clients in the provenance statement, and excluded from government contracts.

Without this service every LinkedIn candidate lands in the review queue with empty fields, defaults to reject after 24 hours, and the registry never grows beyond pages typed in by hand; the discovery chain from li-post-search would end in dead candidates, and tiering, which sets how often li-company-posts-poller polls a page, would be guesswork.

## 2. Objective (the end state this service delivers)

End state: every LinkedIn candidate is resolved into one `poster.profiles` record with identity, reach, country signals, language share, activity and route, or marked unresolvable with a reason, before the qualifier's 24-hour review window closes; registered pages are re-resolved on request so tier and dormancy stay current.

Target: 99% of candidates resolved or marked unresolvable within 24 hours of the job; vendor items spent on resolution kept to 20 per candidate; zero jobs lost, `dlq.li-org-resolver` reviewed daily. Resolution latency and candidate volume are to be measured in the pilot.

## 3. Scope

### In scope

- Resolving a LinkedIn company page URL or handle into a `poster.profiles` record.
- Confirming client-administered pages through the Posts API with the client's token (green).
- Resolving third-party pages through harvestapi `linkedin-company-posts` with max items 20 (amber).
- Computing language share, Iraqi signals, last post time and posts per day from the sampled posts.
- Remembering rejections for 180 days and skipping them; refresh on request.

### Out of scope

- The decision itself (qualifier) and the registry write (registry-writer).
- Resolving members: individuals are never sources and never profiled; a member author is returned as `type = individual` with no lookup.
- Polling and backfill after admission (li-client-posts-poller, li-company-posts-poller, backfill-orchestrator).
- Name-only lookups with no URL or handle: queued to an n8n card for ops to supply the URL.

## 4. Users and consumers

qualifier consumes every profile; poster-resolver dispatches candidates and reads the result; registry-writer applies decisions; backfill-orchestrator, li-company-posts-poller and li-client-posts-poller act on admitted pages. Ops see the review cards; Abdullah and product see how many LinkedIn candidates become sources and what each costs. Clients see only the outcome: a page appears in their watchlist, labelled green or "amber, harvestapi".

## 5. How it works

### 5.1 Trigger and rotation

The resolver is on demand. `jobs.li-org-resolver` receives `{candidate_key, url_or_handle, origin, client_ids, seed_list, kind, attempt}` from poster-resolver (origin `discovery`, raised by a hit on `discovery.hits`), from registry-writer on client onboarding (origin `seed`), from ops (origin `manual`) and from qualifier (`kind: refresh`) when a dormant source gets a new hit, when a source reaches its 90-day decay review, or when a source retires at 180 days. A candidate rejected within the last 180 days (`decisions`) is answered from memory without a vendor call unless `force` is set. Partitioning by `candidate_key` keeps one candidate from resolving twice at once. The refresh cadence for registered pages is to be measured in the pilot; the resolver never polls on its own.

Resolution decides the page's rotation. A client-administered page (`owned_by_client = true`, token present) is admitted green: li-client-posts-poller polls it every 30 to 60 minutes and li-notification-receiver carries its social actions. A third-party page is admitted amber and joins the tier rotation in li-company-posts-poller: tier 1 at 100,000 or more followers, tier 2 at 10,000 to 99,999, tier 3 below 10,000, daily on the vendor route, dormant weekly after 30 days without a post. Every page stays on rotation because registry-writer sets `next_poll_at` on admission and the pollers reset it from the start of each poll; a poller that falls behind serves the most-stale pages first. Backfill on add: backfill-orchestrator fetches the last 90 days or the route's cap, whichever is smaller, once. Comments on the page's posts follow comment-decay-scheduler's LinkedIn series: 6 h, 24 h, 3 d for client posts in li-own-comments-fetcher and 24 h, 3 d for vendor posts in li-post-comments-fetcher, with early stop below 5% and 5 new comments. When the follower count is missing, the page is admitted at tier 3 and promoted when a count is observed.

### 5.2 Step by step

1. Consume the job; normalize the URL or handle to `https://www.linkedin.com/company/<handle>/`; compute `candidate_key = linkedin:org:<handle>`.
2. Check `decisions`: a rejection younger than 180 days returns `resolution = remembered_reject` without a call.
3. If a client in `client_ids` holds a token for this organization, call the Posts API with that token (green) to confirm the URN and access; this path needs no flag.
4. Otherwise read `LI_VENDOR_ROUTE`; if `off`, emit `resolution = unresolved, reason = vendor_route_off`. If every client in `client_ids` is a government client, emit `reason = route_unavailable_government` so the client is told.
5. Ask quota-governor for `budget_tag = li_vendor_org_resolver`, 20 units; on wait-until or deny, re-queue.
6. Run `linkedin-company-posts` with the page URL and max items 20; poll the run; read the dataset.
7. Derive: identity fields, followers where returned, `last_post_at`, posts per day over the sample, duplicate-text share, language share through the `listening-sdk` language client (the model lang-dialect-id runs), country signals from location, phone numbers, domains and outlet links in the sampled text.
8. Publish the 20 sampled posts to `raw.items` (so the spend is not wasted; normalize-item deduplicates them against the later backfill), publish the profile to `poster.profiles`, write `service_runs`, report units to quota-governor.

### 5.3 The call it makes

Amber: `POST https://api.apify.com/v2/acts/harvestapi~linkedin-company-posts/runs` with `Authorization: Bearer <Apify token from vendor_keys>`; input, keys per the Actor's published schema pinned in `listening-sdk`: the company page URL and the maximum number of items, set to 20. Then `GET https://api.apify.com/v2/actor-runs/{runId}` until a terminal status and `GET https://api.apify.com/v2/datasets/{defaultDatasetId}/items?format=json&clean=true`. Run time per candidate is to be measured in the pilot.

Green (client pages only): `GET https://api.linkedin.com/rest/posts?author=urn:li:organization:{id}&q=author&count=20` with the client's token under `r_organization_social`, headers `LinkedIn-Version` (monthly version pinned in the SDK) and `X-Restli-Protocol-Version: 2.0.0`. A 200 confirms the URN and that the organization granted ADMINISTRATOR, DIRECT_SPONSORED_CONTENT_POSTER or CONTENT_ADMIN to the authorizing member; a 403 means the grant is missing and the candidate goes to an n8n card for the client.

### 5.4 What it gets

From the Actor: the page's name, URL and handle, an organization id where returned, the follower count where returned, and up to 20 posts with text, posted time and engagement counts. From the Posts API: the organization URN, up to 20 posts with `id`, `commentary`, `createdAt`, `publishedAt`, `lifecycleState`.

It does not get member profiles, employee lists, the page's full "about" section, or a guaranteed follower count; whether `linkedin-company-posts` returns followers at all is an open question that decides whether a company-profile Actor must be screened.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.li-org-resolver`; control plane: `sources`, `decisions`, `clients`, `client_sources`, `vendor_keys`, `budgets` through quota-governor; per-client LinkedIn tokens from Supabase Vault; environment `LI_VENDOR_ROUTE`.

### 6.2 Writes

`poster.profiles`, `raw.items` (sampled posts), `service_runs`, `dlq.li-org-resolver`, and an n8n review card for missing grants or name-only candidates.

```json
{
  "candidate_key": "linkedin:org:example-bank",
  "platform": "linkedin",
  "source_type": "company_page",
  "platform_id": "urn:li:organization:1234567",
  "handle": "example-bank",
  "url": "https://www.linkedin.com/company/example-bank/",
  "display_name": "Example Bank",
  "route": "amber",
  "vendor": "harvestapi",
  "owned_by_client": false,
  "followers": 12400,
  "country_signals": { "location": "Baghdad, Iraq", "phone_964": true, "iq_domain": true, "seed_list": false },
  "lang_share": { "ar_iq": 0.65, "ckb": 0.00, "en": 0.35 },
  "last_post_at": "2026-10-04T08:15:00Z",
  "posts_per_day": 0.4,
  "duplicate_text_share": 0.05,
  "posts_sampled": 20,
  "resolution": "resolved",
  "service": "li-org-resolver",
  "resolved_at": "2026-10-06T10:02:51Z",
  "job_id": "2b6f0d9c-7a1e-4f3b-8c5d-9e0a1b2c3d4e"
}
```

### 6.3 State

No cursor. `decisions` supplies the 180-day memory; `service_runs` holds last run and errors; counters in `budgets` under `li_vendor_org_resolver`. Nothing is held between jobs.

## 7. Limits, quotas and cost

Vendor cost: harvestapi is about USD 225 to 300 a month at 0.15M LinkedIn items, about USD 1.50 to 2.00 per 1,000 items, so one resolution at 20 items costs about USD 0.03 to 0.04. The service draws on the shared LinkedIn vendor budget under `budget_tag = li_vendor_org_resolver`; the number of candidates a month, and so the share of the 0.15M, is to be measured in the pilot. Green confirmation calls carry no price; LinkedIn's application and member throttles are to be measured in the pilot.

LinkedIn's restricted uses apply to every LinkedIn item: member social-activity data stored at most 48 hours; most member profile data at most 24 hours; organization social activity data six weeks, or six months if authenticated; no social-feed use; member data never exported to clients. This service fetches no member data: it resolves organizations only, and a member author on a discovery hit is returned as `type = individual` without any lookup. The sampled organization posts go to `raw.items` under `vendor_agreed` on the amber route (default 24 months for raw text) and under `linkedin_48h` on the green route, where retention-purger applies the six-month limit for authenticated organization data. The profile record itself is registry metadata about an organization, kept as long as the source exists.

Amber provenance is disclosed and excluded from government contracts: a candidate wanted only by government clients is answered `route_unavailable_government` and the client is told, as qualifier rule 5 requires when a route cannot serve a request.

## 8. Failure handling and fallback

- HTTP 429 or vendor rate limit: exponential backoff with jitter from 30 s to 15 min, then re-queue with `attempt + 1`; after 5 attempts, `dlq.li-org-resolver` and an alert.
- HTTP 401 or 403 from Apify: route marked `degraded`, batch stopped, alert; no key or IP rotation. HTTP 403 from the Posts API: not a route failure but a missing grant; n8n card to the client.
- Actor run `FAILED`, `TIMED-OUT` or `ABORTED`: transient, same backoff.
- Empty 200 (a run that returns no posts for a page that exists): the profile is emitted with `posts_sampled = 0` and the qualifier treats it as inactive; counted per route for source-health-canary, which flips `health = degraded` above 5% in 15 minutes. There is no alternate LinkedIn route, so no `fallback_on`.
- Schema change: payload archived; `schema_unknown` parks the batch; the candidate is re-queued after review.
- Replay: the candidate key makes the profile an upsert in the qualifier's view; a second run for the same job overwrites the same record.

## 9. Non-functional requirements

Throughput: the candidate rate is to be measured in the pilot; one Actor run per candidate is sufficient. Latency: resolution well inside the 24-hour review window; the target per candidate is to be measured in the pilot. Idempotency: `candidate_key` on every record, `attempt` on every job. Scaling: one container image on `jobs.li-org-resolver` partition lag. Security: client tokens and the Apify token injected per job from Supabase Vault; no account pools or proxies; JSON logs with `job_id`, `source_id`, `route`, `vendor`; `/healthz` and `/metrics`.

## 10. Metrics and alerts

`jobs_total{status}` (including `remembered_reject`, `vendor_route_off`, `route_unavailable_government`), `fetch_latency_seconds`, `items_fetched_total`, `cost_units_total`, `quota_denied_total`, `dlq_total`, `profiles_emitted_total{resolution}`, `followers_missing_total`. Alerts: DLQ non-empty, route degraded, vendor budget at 80%, review-window misses (a candidate older than 24 hours without a profile).

## 11. Dependencies

`listening-sdk` (language client, Apify client, LinkedIn client), Redpanda, Supabase Postgres and Vault, poster-resolver, qualifier, registry-writer, quota-governor, source-health-canary, raw-archiver, normalize-item, retention-purger; n8n for review cards; externally Apify, harvestapi `linkedin-company-posts`, and the LinkedIn Posts API for client pages.

## 12. Risks and mitigations

- The Actor does not return a follower count: tier 3 by default, promotion on observation, and screening of a company-profile Actor if the pilot confirms the gap.
- Candidate floods from a broad keyword: the 20-item cap per candidate, governor allowance, and the qualifier's reach queue when the vendor budget is at its cap.
- Mistaken identity (several pages with similar names): the candidate carries the exact URL from the hit; name-only candidates go to ops.
- Vendor withdrawal: resolution of third-party pages pauses; client pages still resolve green.
- Government clients asking for third-party pages: explicit `route_unavailable_government` answer rather than silent failure.

## 13. Acceptance criteria

1. A candidate URL for a third-party page with `LI_VENDOR_ROUTE=harvestapi` yields one `poster.profiles` record with `resolution = resolved`, `route = amber`, `vendor = harvestapi`, `posts_sampled` of at most 20, and `lang_share` summing to 1.0.
2. With `LI_VENDOR_ROUTE=off`, the same candidate yields `resolution = unresolved, reason = vendor_route_off` and no request to `api.apify.com`.
3. A candidate whose `client_ids` are all government clients yields `reason = route_unavailable_government` and no vendor call.
4. A client-administered page with a valid token resolves green through the Posts API with no vendor call and `owned_by_client = true`.
5. A candidate rejected 100 days ago returns `remembered_reject` without a call; the same candidate rejected 200 days ago is resolved afresh.
6. A member author on a discovery hit yields `type = individual` and no outbound call of any kind.
7. `cost_units_total` increases by exactly the number of dataset items read, at most 20 per candidate.
8. A Posts API 403 produces an n8n card and `resolution = grant_missing`, not a `degraded` route.
9. Five consecutive 429 responses send the job to `dlq.li-org-resolver` with the backoff sequence logged and an alert fired.
10. The 20 sampled posts appear on `raw.items` with `service = li-org-resolver` and are deduplicated by normalize-item when the backfill later returns the same posts.
11. A candidate with no follower count is emitted with `followers = null` and `followers_missing_total` incremented.

## 14. Open questions

1. Does `linkedin-company-posts` return the follower count and location? If not, which company-profile Actor passes the vendor screen?
2. What refresh cadence for registered pages keeps tiers honest at acceptable vendor cost?
3. Should the Iraqi-signal language share be computed in the resolver or deferred to lang-dialect-id on the sampled posts, with the qualifier waiting for it?
