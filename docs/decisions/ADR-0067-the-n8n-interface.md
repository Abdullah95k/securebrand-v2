# ADR-0067 · The n8n interface

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, listening-sdk, alert-evaluator, qualifier, source-health-canary, quota-governor, registry-writer, li-org-resolver, x-compliance-sync, I2, D3 (the admin console)
Source: D2-Q067 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

Seven services call n8n, each its own way. alert-evaluator delivers email, Telegram and Slack alerts through "an n8n flow reached by a signed webhook call" with payload `alert/v1` (`alert-evaluator §3 L24`, `§5.3 L69`, `§6.2 L87`); the qualifier posts review cards to `POST /qualifier/review` with three buttons and a signed callback (`qualifier §5.3 L67`, `§9 L116`); source-health-canary sends state-change alerts and the approval card for `blocked` that README decision 5 requires (`source-health-canary §5.2 L57`, `§5.3 L77`; `README L182`); quota-governor's alerts, registry-writer's request notifications and li-org-resolver's review cards go through n8n (`quota-governor §4 L31`, `registry-writer §11 L133`, `li-org-resolver §6.2 L79`); x-compliance-sync takes ops' export requests through n8n (`x-compliance-sync §6.2 L130`). CONVENTIONS names n8n in the stack and for review cards (L3, L251). No document defines the flows, endpoints, payloads or signing, and no session builds them: D3 specifies the query API, client portal, dashboard and admin console (`build-plan/sessions/D3-specs-for-the-parts-with-no-prd.md` L7); I2 routes only the Prometheus alerts through n8n (`build-plan/sessions/I2-observability.md` L7, L31); C9 may stub the card webhook (`build-plan/sessions/C9-qualifier.md` L28). At stake: every caller invents its own endpoint, and nothing tests the far side.

Settles: AU-097.
Depends on: ADR-0012 (ops and client requests through the admin API).

## Options

1. **One documented n8n interface, the flows specified by D3, the build assigned by the orchestrator** (chosen): its rules are under Decision.
2. **Each caller owns its flow and documents it in its PRD** (AU-097 option 2). Consequences: no shared work, but seven payloads and signing schemes, and each build session must also build and test a flow it does not run.
3. **Direct email, Slack and Telegram clients in alert-evaluator; n8n for cards only** (AU-097 option 3). Consequences: client alerts no longer depend on n8n, but alert-evaluator carries three delivery clients and their dependency lines, and ops alerts and cards still need option 1's interface.

## Decision

Every service calls n8n through one SDK client with one signing scheme and two payload schemas, `n8n.alert/v1` for notices and `n8n.card/v1` for decision requests; every answer returns only through the audited admin API; D3 specifies the flows, and the orchestrator assigns their build.

- Outbound: every service calls n8n through one SDK client with one HMAC scheme (a signature over the body with a timestamp and an idempotency key, as alert-evaluator already signs client webhooks, `§5.3 L69`; secrets in Vault).
- Two payload schemas in F2: `n8n.alert/v1` for one-way notices (client alerts, ops alerts, request notifications, the automatic-fallback notices of ADR-0021; alert-evaluator's `alert/v1` becomes it) and `n8n.card/v1` for decision requests, with buttons, default action and timeout (review cards and missing-grant cards; the approval card for `blocked` that README decision 5 required is gone, since ADR-0021 replaces it with a notice).
- Inbound: a button press or an ops request returns only through the admin API (D3), signed the same way and audited, which hands it to the owning service (the qualifier's review answer, x-compliance-sync's export request), as ADR-0012 routes every ops and client request.
- D3 specifies the flows alongside the admin console (one flow per channel and per card type, with the Telegram-to-email fall-through `alert-evaluator §5.3 L69` requires). The build plan names no session to build them, so the orchestrator assigns one (I2, which already deploys n8n routes, is the nearest fit); until then services test against a fake n8n endpoint.

Why: The callers already share one pattern, a signed webhook out and a signed callback in; fixing it once in F2 and sending people's answers through the admin API gives one audited path for human decisions, the path ADR-0012 already sets for ops and client requests.

## Consequences

F2 gains two schemas and the signing helper; the qualifier's callback moves from its own endpoint to the admin API (an approved PRD moves under ADR-0001); D3's brief gains the flows; x-compliance-sync's exports become an admin console action.

- CONVENTIONS v1.1: n8n's role, the two schemas, one signing rule and callbacks through the admin API (v1 L3, L251).
- F2 types both schemas and the signing helper; D3's brief gains the flows (the build plan, citing this ADR).
- `DEFERRED.md`: the session that builds the n8n flows, which the orchestrator assigns (I2 is the nearest fit).

Sessions that must read this: F2, then A5, C1, C7, C9, C12, VLI2, X7, I2, D3.
