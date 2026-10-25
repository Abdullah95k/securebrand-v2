# admin-console

**Platform:** Shared · **Route:** shared · **Lane:** Support · **Owner:** Full-stack lead (apps), with ops and the user's compliance owner · **Status:** Draft v0, 25 Oct 2026 (D3 round 1: open points marked `pending (Qn)`, answered in `docs/handoffs/D3.md`)

This PRD covers three parts with one owner: the **admin console** (ops screens), the **admin API** (`admin-api`, the audited writer of every ops and client request, ADR-0012; F2's open item O-13 asks for its spec here) and the **n8n flows** (ADR-0067). Who builds them is pending (Q1).

## 1. Why this service exists

The pipeline runs itself, but people still decide: which amber flags are on (ADR-0050), what each budget allows (ADR-0042), which keyword terms never run on X (ADR-0069 (f)), which uses of platform content are allowed (ADR-0068), which borderline candidate becomes a source (qualifier rule 10), when a client is offboarded, and which person's deletion request is genuine (ADR-0069 (b)). The ADRs give every one of those writes to "the audited admin console" or "the audited admin API", and route every ops and client request through the admin API alone, "through one SDK call with a schema per kind, `request_id`, `requested_by` and an audit record" (ADR-0012). n8n carries every notice and card to people, and every answer comes back only through the admin API (ADR-0067).

Without this, flags would be flipped in SQL, requests would have no audit, answers to cards would reach services by private callbacks, and the services that F2's producer table names `admin-api` as producer for (`ops_force` on 38 queues, `replay`, `rerun`, `rematch`, `recompute`, `export`, `review_answer`, `deletions`, two `health_change` rows) would have no producer.

## 2. Objective (the end state this service delivers)

End state: every human decision and request in the platform is made in one console or arrives through one API, is checked against its contract, is written once by its single writer, and leaves an audit row that names who, when, what and why, holding ids, hashes, reasons and times only (ADR-0069 (e)); every notice and card reaches its audience on a working channel.

Measurable targets: 100% of `admin-api` messages valid against F2 in producer mode, each with `producer.job_id` equal to its ULID `request_id` (F2 handoff, O-12); zero flag changes outside the API; every client alert that fails on Telegram delivered on its fall-through channel (`alert-evaluator §5.3 E L69`).

## 3. Scope

### In scope

- The admin API: requests, deletions, flag-driven decisions, n8n callbacks (5.3 A).
- The console screens of 5.2.
- The n8n flows: one per channel and per card type, with the Telegram-to-email fall-through (5.3 C).
- The writers ADR-0025, ADR-0033, ADR-0042, ADR-0043, ADR-0044, ADR-0050, ADR-0068 and ADR-0069 give D3: `feature_flags`, `budget_config`, `clients` and its contract columns, `client_settings` and `client_lists` (ops side), `screened_terms`, `permitted_uses`, the Iraqi places and outlets reference table, `taxonomy_nodes`, `kb_entities`, `kb_aliases`, `brand_assets` (curation pending (Q26)).

### Out of scope

- The client-side writes (the client portal) and analytics (the dashboard).
- Prometheus alert rules (I2 routes them through n8n, `I2-observability.md` L7); this PRD gives them their channel only.
- Building the reports Abdullah reads, pending (Q28).

## 4. Users and consumers

- Ops: flags, budgets, registry actions, requests, review answers, pipeline health.
- The user's compliance owner: `screened_terms`, `permitted_uses`, people's deletion requests, legal deletions and holds, audit reads (`retention-purger §4 L34`, `x-compliance-sync §9 L165`).
- Account managers: their clients' settings, review cards, notices.
- Abdullah: budgets, coverage and cost (pending (Q28)).
- Consumers of the admin API: every service F2's producer table lists with producer `admin-api`; registry-writer (decisions); deletion-propagator (deletions); retention-purger (people's requests, pending (Q2)); the owners of client requests (comment-decay-scheduler, backfill-orchestrator, pending (Q2)).

## 5. How it works

### 5.1 Trigger and rotation

Interactive console and request-driven API; n8n flows triggered by signed calls. One schedule: re-sending a card while n8n is unreachable is the sender's (`qualifier §8 L107`), not this service's.

### 5.2 Step by step (the console screens)

1. **Clients.** Create a client and its first admin (pending (Q17)); set `client_type` (required; a missing value fails closed), `accepts_amber` (refused for `government`, F3's check; ADR-0052 (a)), `x_end_user_declared` (ops only, from X's use-case review; ADR-0050), `accepted_flagged_vendors` (Perplexity today; ADR-0051), who sets the last two client-facing ones pending (Q18). `status` takes D3's list (ADR-0043): `onboarding`, `active`, `suspended`, `offboarding`, `offboarded`; moving to `offboarding` needs the confirm step of 5.3 B and starts retention-purger's offboarding (`retention-purger §5.3 L76`) and yt-text-purger's (`yt-text-purger §5.1 L45`). Per-client caps on client requests (ADR-0018 L52) and per-client service options (`client_settings` rows, such as web-gdelt-poller's keep-or-drop, `web-gdelt-poller §4 L35`).
2. **Users and roles.** Staff and client users, account-manager assignments (pending (Q5)).
3. **Flags.** `feature_flags` rows (ADR-0050): the six amber flags with the values ADR-0051 lists, the fb-keyword-search override, `X_PLAN`, the public-account follower threshold (set by the user, DEFERRED section 2). A weakly cleared vendor's value is not offered until `docs/dependencies.md` records its owner and country (ADR-0051). Each change sends the decisions of 5.3 A (flag flips).
4. **Budgets.** `budgets` read-only (mode, used, reserved, `stretch_factor`); `budget_config` edited (limits, shares, per-source caps, per-job and per-run caps, rate ceilings, YouTube backfill and refresh allowances; ADR-0042); an audited raise lifts `exhausted` (`quota-governor §5.1 L49`); the `x_enterprise_required` alert acknowledged (`quota-governor §5.3 L85`; its path pending (Q2)).
5. **Registry.** Sources with health, tier, lifecycle, `backfill_status`, `registry_audit` history (read-only); manual add through registry-writer's path (`registry-writer §5.2 L61`); re-adding a source retired with `owner_request`, with the request on record (ADR-0069 (a)); clearing a source-level health reason (`health_change` to `ok`, F2's row for `admin-api`; ADR-0016); a Telegram onboarding link for a cooperating outlet (pending (Q24)).
6. **Review queue.** Every open `review_queue` row by kind and owner (ADR-0045); qualifier cards answered here as on n8n (5.3 A); other kinds shown with their owner's evidence (deletion-guard holds, `x_terms_screen`, `x_rule_flood`, `schema_unknown`, `kb_candidate`, `annotation:media`); their answers need contract paths, pending (Q2).
7. **Requests.** Forms for each request kind of 5.3 A, with dry-run counts where the owner offers one (raw-archiver's replay plan, `raw-archiver §5.3 L71`), and each request's status from `jobs.completed`.
8. **Compliance.** `screened_terms` (compliance owner); the register of permitted uses (ADR-0068; the D3 brief's "Watch for"): every `permitted_uses` row shown for review, each with subject, use, allowed, clause relied on, set by and when; a use with no row is shown as "allowed (no row)"; every change written audited with its clause; the seeded rows (YouTube video and audio downloads, Facebook and Instagram training) marked as seeded; the Iraqi places and outlets reference table (ADR-0033); people's deletion requests and their confirmations (5.3 B; intake pending (Q25)); legal deletions and holds (`retention-purger §5.3 L80`); Meta's deletion instructions with `signal_at` (`§5.3 L65`); x-compliance-sync exports (`x-compliance-sync §6.2 L132`); read-only audits (`registry_audit`, `retention_audit`, `x_compliance_audit`, deletion-propagator's record) for ops and the compliance owner only.
9. **Curation.** `taxonomy_nodes` with the validation that rejects nodes inferring a protected attribute or monitoring sensitive events (`analysis-topics §5.3 L68`), `kb_entities` and `kb_aliases` (`analysis-entities §5.3 L61`), `brand_assets` (`analysis-media §5.3 L68`); who writes and approves pending (Q26). A release bumps the version and asks for the owner's `rerun` (`analysis-topics §5.1 L50`).
10. **Pipeline health.** `service_runs`, canary state, DLQ depths, open ops alerts (read-only).

### 5.3 The call it makes (the processing it performs)

**A. The admin API.**

- Authentication: Supabase Auth JWT with a staff role, or the client portal's server identity for client requests; every call re-checks the role against the action (pending (Q5), (Q27)).
- One endpoint per request kind, `POST /v1/requests/<kind>`, validating the body against F2's `job/v1` kind, stamping a ULID `request_id` and `requested_by` (`person:<ULID>`, never matching the service pattern; F2 Q18), writing the audit row, then producing through the SDK with `producer.service = admin-api` and `producer.job_id = request_id` (F2 VERSIONING):
  - `ops_force` on the 38 queues of F2's row (fields as declared per queue: `post_ref`, `target_ids`, `client_id`, `candidate_key`, `host`, `crawl_id`), single or bulk ("all push Pages, most-stale-first", `fb-client-webhook-receiver §5.1 L44`; `yt-pubsub-receiver §8 L149`), each job its own `request_id`;
  - `replay` on `jobs.normalize-item` (ADR-0039); `rerun` on the four analysis queues, a client's new topic included (ADR-0012); `rematch` on `jobs.keyword-matcher`, also on every keyword change the portal reports; `recompute` on `jobs.aggregator` with `from`, `to`; `export` on `jobs.x-compliance-sync` (`client_id` or null for X; ADR-0067); `review_answer` on `jobs.qualifier` (`candidate_key`, `card_id`, `decision_id`, `action`).
- Client requests (post refresh, backfill re-run, X history): handed to their owners, comment-decay-scheduler and backfill-orchestrator (ADR-0012); the carrier is pending (Q2).
- Deletions: `deletions/v1` through the SDK builder, reasons `client_request` (from the portal, ADR-0054) and `legal` (compliance owner), with `requested_by`, `signal_at`, `due_at`.
- Flag flips (ADR-0021 L61, ADR-0050): when an amber flag goes `off`, a source-level `health_change` (health `blocked`, reason `flag_off`) for each source in a source-level `fallback` on that alternate; when it goes back on, one (health `blocked`, reason `flag_on`) for each source of a type the alternate reads whose `blocked` was set at source level. The flag row and the decisions are written together; a crash between them is repaired from the audit row on restart.
- n8n callback, `POST /v1/n8n/callback`: verifies the signature, timestamp and idempotency key with F2's helper (`verifyN8n`), records the answer, and hands it on: a `qualifier_review` button becomes `review_answer`; a `manual_url` answer becomes a manual add through registry-writer's path (`li-org-resolver §3 L34`); a `grant_missing` card has no answer (its link opens the portal). A replayed callback with a known idempotency key changes nothing.
- Meta's data-deletion and deauthorisation callbacks for Facebook Login users (the approvals table: "privacy policy and data deletion URLs"): signed-request check, a status URL, and the follow-up of 5.3 B.

**B. Two-step actions.** Offboarding a client, deleting by `legal`, and a person's deletion request need a confirm step showing the scope (counts per source and class, `retention-purger §12 L155`) before the message is sent; a person's request needs the confirmation sent to the account's public contact recorded first (ADR-0069 (b)). Whether some changes need a second person is pending (Q27).

**C. The n8n flows (ADR-0067).** Services send `n8n.alert/v1` and `n8n.card/v1` through the SDK client, signed with one HMAC scheme (headers `X-SB-Timestamp`, `Idempotency-Key`, `X-SB-Signature`; F2). The flows:

| Flow | Input | Does | Fall-through |
|---|---|---|---|
| `alert-email` | `n8n.alert/v1`, channel `email` | renders the notice per audience and language, sends through the email provider (pending (Q30)) | none (the last resort) |
| `alert-telegram` | channel `telegram` | sends through our alerts bot (not the listening bots) | on failure, sends the same notice to its `fallthrough_channel`, email by default (`alert-evaluator §5.3 E L69`) |
| `alert-slack` | channel `slack` | posts to the audience's Slack channel | to its `fallthrough_channel` |
| `card-qualifier-review` | `n8n.card/v1`, `qualifier_review` | posts the card with the five buttons (approve as tier 1, 2 or 3, reject, mention only) to the reviewers' channel; a press calls the admin API callback | the email version links to the console's review screen |
| `card-grant-missing` | `grant_missing` | sends the client the reconnect notice with `regrant_url` | email |
| `card-manual-url` | `manual_url` | asks ops for the inputs it lists (a URL or text) | email |

- Routing by `audience`: `client` to the channels a client's rule or notification setting names (pending (Q23)); `ops` and reviewers to the ops channel (pending (Q29)); `account_manager` to the assigned manager's email.
- Idempotency: `<alert_id>:<channel>` and `<card_id>:<channel>`; n8n drops a repeat (F2).
- Timeouts and defaults are the sender's: the qualifier applies `reject` at 24 hours from `opened_at` (`qualifier §5.1 L46`); a card answered after its timeout is refused by the owner and the answer is shown as late.
- The notices the PRDs and ADRs name, by audience: ops (every automatic fallback and every blocked source that cannot fall back, ADR-0021; `budget_50`, `budget_80`, `budget_95`, `budget_exhausted`, `x_enterprise_required`, `quota-governor §10 L139`; the canary's route flips; `rotation_behind`, `registry_duplicate`, `subscription_failed`, F2's known names; delivery and DLQ alerts); clients (rule alerts; missing grants; a source blocked, a bot removed, privacy mode on, `tg-bot-channel-receiver §5.2 L72`, `tg-discussion-receiver §5.2 L69`; a candidate or hashtag queued over a cap, `qualifier §5.2 L56`, ADR-0052 (c); coverage paused for budget, `web-search-mojeek §7 L120`; a request denied or rejected, `x-full-archive-search §8 L147`); account managers (a webhook disabled after 410, `alert-evaluator §8 L117`; a client source moved to a vendor by fallback, `source-health-canary §4 L36`; `amber_excluded_government`, `qualifier §9 L119`).

### 5.4 What it gets

Staff input; the client portal's requests; n8n callbacks; Meta's callbacks; the control-plane rows of 6.1. No platform content beyond the evidence a review row already holds.

## 6. Inputs and outputs

### 6.1 Reads

Every table it writes; `budgets`, `sources`, `client_sources`, `registry_audit`, `retention_audit`, `x_compliance_audit`, `review_queue`, `service_runs`, `canary_targets`, `deletion_requests` (status), `jobs.completed` (request status).

### 6.2 Writes

- Postgres: `feature_flags`, `budget_config`, `clients`, `client_settings`, `client_lists` (ops entries), `screened_terms`, `permitted_uses`, the Iraqi places table, `taxonomy_nodes`, `kb_entities`, `kb_aliases`, `brand_assets` (pending (Q26)), its own audit table (`admin_audit`, a name for F3: request id, actor, action, subject ids, before and after hashes, reason, time).
- Topics, as `admin-api`: the job kinds of 5.3 A; `deletions/v1`; `registry.decisions/v1` (`health_change`, flag and clear rows); as `admin-console`: `add`, `update`, `remove_client` (F2's decision producers).
- Calls: registry-writer's manual add; n8n flows.

### 6.3 State

Pending two-step confirmations (24 hours); nothing in memory.

## 7. Limits, quotas and cost

No platform calls. n8n runs self-hosted on the cluster (ADR-0027, I2). Email, Slack and Telegram prices follow the providers chosen (pending (Q30)); USD costs are confirmed when they are.

## 8. Failure handling and fallback

- Producing a request fails: the audit row says `failed`, nothing is retried silently; the console shows it.
- A flag change whose decisions did not all produce: repaired from the audit row on restart (5.3 A).
- n8n down: senders retry with backoff (`alert-evaluator §5.3 E`, `qualifier §8 L107`); the console's review screen still answers cards.
- A callback with a bad or stale signature: 401, logged, nothing written.

## 9. Non-functional requirements

- Access: staff roles only; the console reachable only through the company's sign-in with the factors of Q5.
- Audit: every write, kept for the life of the client contract until counsel sets a period (ADR-0069 (e)).
- Idempotency: a request replayed with its `request_id` produces nothing new.
- Isolation: an account manager sees only assigned clients.

## 10. Metrics and alerts

`admin_requests_total{kind,result}`, `admin_decisions_total{decision,reason}`, `flag_changes_total{flag}`, `n8n_callbacks_total{card_type,result}`, `n8n_deliveries_total{flow,result}`, `n8n_fallthrough_total{from,to}`. Alerts: `admin_produce_failing`, `callback_signature_failed_spike`, `n8n_flow_failing` (a flow failing above 5% for 15 minutes).

## 11. Dependencies

F2 (job kinds, decisions, deletions, the n8n schemas and signing), F3 (tables), the SDK (producers, credential client, deletion builder), registry-writer, the owning services above, n8n (self-hosted), Supabase Auth, the email provider (pending (Q30)), Slack and the Telegram Bot API.

## 12. Risks and mitigations

- A flag flipped while decisions fail: the repair on restart, and the audit.
- A sensitive-event term or a "not allowed" use changed casually: compliance-owner-only screens (pending (Q27)).
- Telegram blocked in Iraq: every client channel set keeps a non-Telegram channel, and the fall-through.

## 13. Acceptance criteria

1. Every `ops_force`, `replay`, `rerun`, `rematch`, `recompute`, `export` and `review_answer` the API produces validates against F2 in producer mode, with `producer.service = admin-api` and `producer.job_id` equal to its `request_id`.
2. Turning `TT_VENDOR_ROUTE` off sends one `health_change` (`blocked`, `flag_off`) per source in a source-level fallback on tt-profile-videos-poller and none for a source whose state was set at route level; turning it on sends `flag_on` decisions for the source-level blocked sources of that type.
3. `accepts_amber` cannot be set on a government client; `client_type` cannot be cleared.
4. A weakly cleared vendor's flag value is refused until `docs/dependencies.md` records its owner.
5. The register screen lists every `permitted_uses` row, shows a missing row as allowed, and writes each change with its clause and author to the audit.
6. A qualifier card answered in Slack and the same card answered in the console produce one `review_answer` between them.
7. A Telegram delivery failure of a client alert is delivered by email.
8. A callback with a wrong signature or a timestamp outside the tolerance writes nothing.
9. Moving a client to `offboarding` requires the confirm step and then shows retention-purger's progress.
10. Every write leaves an audit row with no item text and no clear identity.

## 14. Open questions

Pending the user's answers in `docs/handoffs/D3.md`: Q1, Q2, Q5, Q17, Q18, Q23, Q24, Q25, Q26, Q27, Q28, Q29, Q30.
