# C9 · qualifier

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

The ten qualifier rules, review cards through n8n, registry.decisions.

Service `qualifier` · PRD `docs/prds/shared/qualifier.md` · lane Registry · route shared · 10 acceptance criteria (section 13) · 0 open questions (section 14)

## Needs first (merged, with a closed review)

- F4 SDK runtime (Node): `docs/handoffs/F4.md`
- F3 Control-plane schema: `docs/handoffs/F3.md`
- C1 quota-governor: `docs/handoffs/C1.md`
- G0 Gate: foundation: `docs/gates/G0.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/qualifier.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Qualifier rules; Quotas, budgets and the quota governor
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of F4: `docs/handoffs/F4.md`
6. Handoff of F3: `docs/handoffs/F3.md`
7. Handoff of C1: `docs/handoffs/C1.md`
8. Qualifier rules (CONVENTIONS)
9. N8n webhook for review cards, or a stub

## Contracts it touches (from PRD section 6)

- Topics read: `poster.profiles`
- Topics written: `registry.decisions`
- Job queue: `jobs.qualifier` if the PRD's section 5.1 schedules jobs
- Tables read: `sources`, `keywords`, `clients`, `client_sources`, `budgets`, `decisions`, `review_queue`, `service_runs`; written or updated: `clients`, `decisions`, `review_queue`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/qualifier/`
- `docs/handoffs/C9.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C9.md` from the fresh-session review

## Watch for

- A review left 24 h defaults to reject
- Route caps and budgets are checked through quota-governor
- registry-writer is the only writer of the registry's identity and policy columns and of source.events; each operational column has one named owner (ADR-0013, ADR-0014)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C8, C10, C11

## How to run it

- Plan: `claude --worktree C9 --permission-mode plan`, then `/plan-session C9`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C9` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C9`, then `/review-session C9`
- Fix: `claude --worktree C9` (or the build terminal), `/fix-session C9`; then a fresh session runs `/review-session C9 recheck`; merge when the review has no open blocker or should-fix
