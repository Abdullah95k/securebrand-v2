# client-portal

**Platform:** Shared · **Route:** shared · **Lane:** Support · **Owner:** Full-stack lead (apps) · **Status:** Draft v0, 25 Oct 2026 (D3 round 1: open points marked `pending (Qn)`, answered in `docs/handoffs/D3.md`)

## 1. Why this service exists

Everything the pipeline does for a client starts from something the client sets: the keywords it searches (ADR-0044), the sources it watches and priority-lists (ADR-0043), the properties it owns and connects (ADR-0066), the amber data its contract accepts (ADR-0052), and the requests it makes beyond the automatic schedule (ADR-0012). The PRDs name the client app for each: "clients connect LinkedIn by OAuth and choose which administered pages to add" (`li-client-posts-poller §4 L32`), TikTok's consent screen and first token exchange (`tt-client-videos-fetcher §3 L26`), the Telegram onboarding page with its one-time code (`tg-bot-channel-receiver §5.2 L67`), client refreshes "budget permitting" (`comment-decay-scheduler §5.1 L70`), the deletion screen (ADR-0054), the provenance statement every amber PRD discloses its route in.

The client portal is that app: the client-side writer of `keywords`, `client_settings`, `client_lists` and `alert_rules` (ADR-0043, ADR-0044, ADR-0025), a named producer of `registry.decisions` (`add`, `update`, `remove_client`; F2's decision producers), and the only way a client's request reaches the admin API. Brief U2 builds it (`build-plan/sessions/U2-client-portal.md` L7), with the OAuth flows the LinkedIn and TikTok screencasts must show.

## 2. Objective (the end state this service delivers)

End state: a client admin can, without help from ops, connect the client's own properties, set up and change keywords and watched sources, answer what the client may answer, make the requests its plan allows, ask for deletion of data held only for it, and read the provenance statement that says where its data comes from; every change reaches the owning service through its contract and is audited.

Measurable targets:

- Connecting a Facebook Page, Instagram business account, LinkedIn page or TikTok account takes one OAuth round trip and the property is `added` within 60 s of the grant (registry-writer's apply time, to be measured in U2).
- A keyword save reaches keyword-matcher within its poll interval plus compile time (`keyword-matcher §9 L141`) and registry-writer's keyword-rule rows within one decision.
- Every write carries a ULID `request_id`, which its messages' `producer.job_id` takes (F2 handoff, O-12), and one audit row.

## 3. Scope

### In scope

- Onboarding and users: pending (Q17), roles pending (Q5).
- Connections (OAuth and the Telegram bot), disconnection (pending (Q21)) and the missing-grant flow (ADR-0021, ADR-0067).
- Keywords; sources, priority, seed, watch and saved lists; hashtags and their Instagram binding.
- The client review queue (pending (Q20)).
- Client requests through the admin API (pending (Q19)).
- Deletion requests about data held only for the client (ADR-0012, ADR-0054).
- The provenance statement (ADR-0003).
- Client settings: the qualifier's bounded thresholds, alert and deletion webhooks, notification preferences (pending (Q23)).

### Out of scope

- Analytics views (the dashboard), ops screens and every ops-only setting (the admin console), `clients` contract columns (`client_type`, `accepts_amber`, `x_end_user_declared`, `accepted_flagged_vendors`; pending (Q18)).
- Author (person) deletion requests: the deletion channel, recorded in the admin console (ADR-0069 (b); pending (Q25)).

## 4. Users and consumers

- Client admins: everything in scope; client analysts and viewers: read and, where Q5 allows, requests.
- Account managers act in a client's portal under assignment (pending (Q5)).
- Channel owners outside client staff (cooperating outlets) for Telegram onboarding only (`tg-bot-channel-receiver §4 L33`; pending (Q24)).
- LinkedIn's and TikTok's reviewers see the OAuth flows and each use case in the recordings (`build-plan/README.md`, approvals table).
- Consumers of its writes: registry-writer (`registry.decisions`; the manual-add endpoint), keyword-matcher and the searchers (`keywords`), poster-resolver, the qualifier and the resolvers (`client_lists`, the qualifier's `client_settings` row), alert-evaluator (`alert_rules`), the receivers (`source.events` after the `add`), the admin API (requests, deletions).

## 5. How it works

### 5.1 Trigger and rotation

Interactive web app with a server part (the "client-portal" producer, F2's D3 writer names); no schedule. A daily job lists tokens near expiry for the notices of 5.2 C.

### 5.2 Step by step

**A. Onboarding** (DEFERRED section 3, "the client portal's onboarding screens", owner D3). Proposed, pending (Q17): ops create the client and its first admin in the admin console with its contract settings; the admin signs in, invites users, then walks a checklist: connect own properties (B), enter keywords (D), add watched sources and seed lists (E), set notification channels, read and acknowledge the provenance statement (G).

**B. Connections.** Each ends with an `add` decision for a new property, or an `update` for one already registered, carrying `owned_by_client = true`, `added_by = client`, the client id, route `green`, the reach tier from the count the connection returns and a pre-allocated `source_id` (ADR-0066, ADR-0013 (d)); no resolver or qualifier runs. Tokens are stored through the SDK's credential client in `credentials`, never in portal tables (ADR-0016).

- Facebook Login for Business: Pages and Instagram business accounts the user administers; the Page access token per Page, the Instagram account's long-lived token and its `ig_user_id` (`ig-account-media-poller §5.3 L73`); the permission list follows App Review (`fb-client-webhook-receiver §5.3 L73`). The receivers subscribe on the `added` event (ADR-0066).
- LinkedIn: OAuth with `r_organization_social`; the user picks pages on which it holds ADMINISTRATOR, DIRECT_SPONSORED_CONTENT_POSTER or CONTENT_ADMIN (`li-client-posts-poller §1 L7`, `§5.3 L66`); the authorising member is recorded, since the notification subscription may be bound to that token (`li-notification-receiver §14 Q2`).
- TikTok Display: scopes `user.info.basic,video.list`; the whole token response is stored, with `expires_in` and `refresh_expires_in` (`tt-client-videos-fetcher §5.3 L65`, `L67`).
- YouTube channels: ownership proof pending (Q22).
- Telegram: the owner enters the channel username or picks "private channel"; the portal calls tg-bot-channel-receiver's onboarding endpoint, which keeps the one-time code and the pre-allocated id in its own table (ADR-0066); the page shows the add-the-bot instruction (fewest administrator rights), the code for a private channel, then the discussion-group step (`tg-bot-channel-receiver §5.2 L67`, `L69`; `tg-discussion-receiver §5.2 L67`), a status per channel (`§12 L175`), "history from the day the bot is added" (`§12 L176`), and steps for owners inside Iraq during a Telegram block (`§12 L178`).

**C. Missing grant and disconnection.** A client-owned property that is `blocked` or in `fallback` gets the missing-grant card (`n8n.card/v1`, `card_type = grant_missing`, with `regrant_url`; F2) and a banner here; the re-grant link opens B for that property, and the new grant ends the block or fallback (ADR-0021). Disconnecting is pending (Q21); a TikTok revocation always deletes that grant's `tiktok_display` records (reason `authorization_revoked`, ADR-0035).

**D. Keywords.** The editor writes `keywords` (ADR-0044): `label`, `forms` (variants and per-script forms: Arabic, Sorani, Latin, handles with `@`, hashtags with `#`, each with its boundary; `keyword-matcher §5.3 A L56`), `exclusions`, `context_terms`, `purpose`, `priority`, `platforms`, `enabled`, `rematch_days`. On save, in one transaction: `version` and `updated_at` move; `query_key` is set with the SDK helper (ADR-0044); `screening_status` is set by screening the forms against `screened_terms` (ADR-0069 (f)), and a flagged keyword is saved but joins no X rule and runs no X history (ADR-0044, ADR-0059); then the `add` or `update` decision naming the keyword goes to registry-writer (ADR-0044), and a changed keyword asks the admin API for a `rematch` (ADR-0012). Rules shown to the user: a government client's keywords take `purpose` `reputation` or `service_quality` only (`keyword-matcher §5.3 D L69`); a single common word needs a qualifying phrase (`x-filtered-stream §12 L186`); forms generated from the transliteration table are marked for the client to confirm (`web-search-perplexity §5.1 L45`); a rule a search engine rejected (`query_rejected`) shows until its forms are edited (`web-gdelt-poller §8 L133`).

**E. Sources and lists.**

- The client's watched sources from `client_sources`, with tier, freshness, health, `backfill_status` ("your source's last 90 days are loading", `backfill-orchestrator §4 L34`), route and vendor.
- Add a third-party source: registry-writer's manual path (`POST /registry/sources`, `registry-writer §5.2 L61`; ADR-0066), which refuses an individual, an amber route for a government client and another client's source (`§13 L154`); request status, "already watched" included, comes back by `request_id` (`§12 L144`).
- Priority: `client_sources.priority` through an `update` decision (ADR-0043); seed and watch entries are `client_lists` rows and also go down the manual path (ADR-0043, ADR-0066); saved lists of public accounts (ADR-0010; named lists pending (Q12)).
- Remove: a `remove_client` decision (F2's decision producers).
- Hashtags: bound to one of the client's Instagram business accounts at registration, with the account's 30-tags-per-7-days use shown (`ig-hashtag-search §5.1 L57`, `§12 L168`); a 31st tag is queued and the client told, or goes to the vendor if the client accepts amber and `IG_VENDOR_ROUTE` is on (ADR-0052 (c)).
- Queued candidates over a route cap and their position: pending (Q20).

**F. Requests** (pending (Q19)). Each goes to the admin API, which gives it a `request_id` and hands it to the owning service (ADR-0012): a post's comment refresh to comment-decay-scheduler (`series_step = refresh:<request_id>`), a backfill re-run or an X history window to backfill-orchestrator (ADR-0020, ADR-0064), only for keywords registered for the client, never free text (`x-full-archive-search §5.2 L50`). The status shown is the owner's answer: queued for budget (`comment-decay-scheduler §5.1 L70`), `capped`, `outside_window` (`x-replies-fetcher §5.2 L53`), `query_rejected`, done. Client requests run at priority 1 (ADR-0018) within the per-client cap the admin console sets (ADR-0018 L52).

**G. Provenance statement.** One page per client, from query-api's `/provenance`: each route and vendor that serves the client's data, green or amber, with the amber disclosure (CONVENTIONS v1.1 constraint 2); the retention class of each and what it means; the coverage limits the PRDs require stated: Facebook `/feed` ranked and `capped` histories (`fb-backfill §7 L122`), Instagram business and creator accounts only, no age-gated accounts, no Stories mentions (`ig-account-media-poller §12 L164`, `ig-mentions-fetcher §12 L169`), vendor search a sample (`fb-keyword-search §12 L160`), TikTok `video.list` not complete (`tt-client-videos-fetcher §12 L160`), vendor counts may differ (`tt-video-stats-refresher §12 L152`), X reply coverage (`x-replies-fetcher §12 L177`), Telegram deleted comments kept until a request (`tg-discussion-receiver §12 L184`), the news crawler obeying robots.txt, Content Signals, RSL and HTTP 402 (`news-robots-checker §4 L33`); GDELT's attribution once counsel sets it (DEFERRED section 1). Each version is dated; the acknowledgement of A is recorded with the version read.

**H. Deletion requests.** A client admin asks to delete data held only for the client (reason `client_request`, ADR-0035, ADR-0054): one item, one source's data, or all its data of one class (Telegram bot data is the case `telegram_bot` needs). The admin API writes the `deletions` message through the SDK (ADR-0012); data another client also holds survives with this client's id removed (`retention-purger §13 L164`). The request's progress follows deletion-propagator's status chain (`deletion-propagator §5.3 L76`); a member's request about Telegram comments is entered here by the channel's client (`tg-discussion-receiver §12 L183`).

**I. Settings.** The qualifier's row of `client_settings` within its bounds (`qualifier §3 L25`, `§12 L137`; ADR-0043): `iraqi_signals_required` 1 to 3, `lang_share_min` 0.30 to 0.80, the spam limits, the tier and creator thresholds raise-only, decay and retirement shorten-only; out-of-bounds values are refused. Alert and `deletion.completed` webhooks: URL here, secret through the credential client (`alert-evaluator §6.1 L80`, `deletion-propagator §6.1 L86`); a webhook disabled after HTTP 410 is re-enabled here (`alert-evaluator §8 L117`).

### 5.3 The call it makes (the processing it performs)

Writes go through the portal's server, never from the browser to a table: Postgres with the server's role (row-level security on `client_id` as a second line), `registry.decisions/v1` produced through the SDK with `producer.service = client-portal` and `producer.job_id = request_id` (F2 VERSIONING, D3 writer rule), and `requested_by` a person reference `person:<ULID>`, the person id the portal assigns each user at invitation, which never matches the service pattern `^[a-z0-9]+(-[a-z0-9]+)*$` (F2 handoff, Q18). Requests and deletions go to the admin API, signed and audited (ADR-0067).

### 5.4 What it gets

The client's own rows, query-api's reads, the OAuth providers' token responses (passed to the credential client and not kept), registry-writer's request statuses, the admin API's request statuses.

## 6. Inputs and outputs

### 6.1 Reads

query-api; `clients` (own row), `client_settings`, `client_lists`, `client_sources`, `keywords`, `screened_terms` (screening only), `review_queue` (the kinds a client may answer, pending (Q20)); registry-writer and admin API status endpoints.

### 6.2 Writes

- Postgres: `keywords`, `client_settings`, `client_lists`, `alert_rules`, the membership table (pending (Q5)), and its own audit rows (ids, actor, `request_id`, before and after hashes, no content; ADR-0069 (e)).
- `registry.decisions/v1`: `add` and `update` (owned properties; keywords; priority), `remove_client`, as F2's producer rows allow.
- Calls: registry-writer `POST /registry/sources`; tg-bot-channel-receiver's onboarding endpoint; the SDK credential client; the admin API (requests, deletions, rematch).

Example decision for a connected Page, the shape of F2's fixture `registry.decisions/v1/valid/add-owned-property.json` (abridged):

```json
{
  "schema": "registry.decisions/v1",
  "producer": {"service": "client-portal", "version": "1.0.0", "job_id": "01M481X54G0556ETKT1PT8FKEW"},
  "decision_id": "01M481X54G2TQT3GMDWFDM5R0K",
  "decision": "add",
  "requested_by": "person:01J9P2R4T6V8X0Z2B4D6F8H0KM",
  "reason": null,
  "source_id": "4b9e2c71-8d3a-4f56-a0e1-7c2d9b8f3a64",
  "add": {
    "source": {"platform": "facebook", "source_type": "page", "platform_id": "104998877665544", "route": "green", "vendor": null, "tier": 1, "retention_class": "meta_on_request", "owned_by_client": true, "added_by": "client", "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]},
    "proposed_source_id": "4b9e2c71-8d3a-4f56-a0e1-7c2d9b8f3a64",
    "client_priority": [{"client_id": "0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60", "priority": true}]
  }
}
```

### 6.3 State

Sessions (Supabase Auth); the OAuth `state` and PKCE verifier per connection attempt, for 10 minutes; nothing else.

## 7. Limits, quotas and cost

No platform reads of its own beyond the OAuth exchanges and the account lookup each connection needs (the follower count for the tier). Client requests cost what their owner's budget tag says, within the per-client cap (ADR-0018).

## 8. Failure handling and fallback

- OAuth error or refused permission: nothing is written; the screen names the missing permission.
- registry-writer refuses a decision (`registry_duplicate`, a 422 rule): shown with the rule; the property's id is reused if it already exists (ADR-0066).
- Admin API unreachable: the request is not queued in the browser; the user retries.
- `screened_terms` unreadable: the save is refused (fail closed), since an unscreened term must not run on X.

## 9. Non-functional requirements

- Isolation: every write checks the user's membership of the client; the two-client test of the brief.
- Audit: every write has a `request_id` and an audit row; audit rows hold ids, hashes, reasons and times only, kept for the life of the client contract (ADR-0069 (e)).
- Security: Supabase Auth with the factors of Q5; CSRF protection on the server; tokens never reach the browser after the exchange.
- Languages: pending (Q4).

## 10. Metrics and alerts

`connections_total{platform,result}`, `decisions_produced_total{decision}`, `keyword_saves_total{screening_status}`, `requests_total{kind,result}`, `oauth_errors_total{platform,reason}`. Alerts: `oauth_error_rate_high` (above 20% of attempts in an hour per platform), `decision_produce_failing`.

## 11. Dependencies

F2 (`registry.decisions/v1`, the key and query-key helpers), F3 (the tables), the SDK credential client (F4), registry-writer (C7), tg-bot-channel-receiver (TG1), the admin API (pending (Q1)), query-api (Q1), Supabase Auth, the Meta, LinkedIn and TikTok OAuth endpoints.

## 12. Risks and mitigations

- A client adds an individual: registry-writer's rule 7 refusal, shown to the user.
- A sensitive-event term runs on X: screening at save, fail closed.
- Platform reviewers reject the OAuth flow: U2 records every scope in use in the screencasts.

## 13. Acceptance criteria

1. Connecting a Facebook Page sends one `add` (or `update` for a registered Page) with `owned_by_client = true`, `added_by = client`, route `green`, a pre-allocated `source_id`, and `producer.job_id` equal to the request's ULID.
2. No token appears in a portal table, log or browser storage after the exchange; it is in `credentials`.
3. A keyword save sets `query_key` and `screening_status`, bumps `version`, sends one decision naming the keyword and one `rematch` request.
4. A keyword whose form matches a `screened_terms` entry is saved with a flagged `screening_status`; with `screened_terms` unreadable the save is refused.
5. A government client cannot save a keyword with a `purpose` other than `reputation` or `service_quality`, nor add a source on an amber route.
6. A user of client A cannot read or write client B's keywords, lists, settings or requests.
7. A qualifier setting outside its bounds is refused with the bound named.
8. A TikTok disconnection produces an `authorization_revoked` deletion for that grant's `tiktok_display` records.
9. The Telegram flow creates the onboarding record through tg-bot-channel-receiver and shows the one-time code for a private channel.
10. A client deletion request reaches the admin API as one request and shows deletion-propagator's status until `completed`.
11. Every `requested_by` written is `person:<ULID>` and never matches the service-name pattern.

## 14. Open questions

Pending the user's answers in `docs/handoffs/D3.md`: Q1, Q3, Q4, Q5, Q12, Q17, Q18, Q19, Q20, Q21, Q22, Q23, Q24, Q25.
