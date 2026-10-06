---
name: plan-session
description: Plan one build session from its brief, PRD, conventions, ADRs and handoffs, interviewing the user on every ambiguity. Run at the start of every build session, in plan mode.
argument-hint: <session ID, for example FB2>
disable-model-invocation: true
effort: max
---

# Plan session $0

Plan only. Write no code and no tests in this session.

## 1. Load the context, in this order

1. The brief: `ls build-plan/sessions/$0-*` finds it. If there is none, stop and tell me.
2. The PRD or PRDs the brief names, in full.
3. Only the CONVENTIONS sections the brief lists (`docs/prds/_shared/CONVENTIONS.md`), and the ADRs in `docs/decisions/` whose "Applies to" line names this service, its platform, its lane or "all".
4. The handoff note of every session in the brief's "Needs first" (`docs/handoffs/<ID>.md`). If one is missing, stop: that session is not finished.
5. The brief's "Give the session" items. For a platform session also the probe report and fixtures it names, and `docs/patterns/ADAPTER-PATTERN.md`.

Use subagents to read long material and report back, and tell them to keep exact field names, numbers and quotes.

## 2. Draft the plan, following build-plan/templates/PLAN.md

- **Acceptance map:** every criterion in PRD section 13, the test that will prove it (unit, contract, acceptance or e2e) and the fixture it uses.
- **Uncovered behaviours:** what PRD sections 5 and 8 require that no criterion tests (rotation or series timing, catch-up, 429, 401 and 403, empty 200, a 5xx in the middle of pagination, DLQ after five attempts, replay idempotency), each with its own test.
- **Contracts:** every topic (with version), job queue and kind, table and column the service reads or writes. Confirm each one exists in `packages/contracts` and the migrations. Anything missing goes under "Proposals needed"; never invent it.
- **Build outline:** files to create; the SDK features used (never re-implement retries, DLQ, cursors, quota, canary, logs or metrics); the mapper to add to normalize-item, if this service emits a new record shape.
- **Risks:** each risk in PRD section 12 and the test that covers it.
- **Questions:** every ambiguity or conflict between the PRD, CONVENTIONS, the ADRs and the handoffs, and every PRD section 14 question this build depends on.

## 3. Interview me

Ask each question with AskUserQuestion, one at a time, your recommended answer first. Do not ask what the PRD, an ADR or a handoff already answers. Put each answer into the plan.

## 4. Present the plan for approval

When I approve it, save it exactly as approved to `docs/plans/$0.md` and stop. The build starts in a clean context: `/clear`, then `/build-session $0`.
