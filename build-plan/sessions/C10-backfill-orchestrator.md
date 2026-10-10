# C10 · backfill-orchestrator

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

90-day backfill on add, route caps, backfill_status, hand-over to rotation.

Service `backfill-orchestrator` · PRD `docs/prds/shared/backfill-orchestrator.md` · lane Registry · route shared · 10 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- F5 SDK scheduling, quota client, adapter kit, fake platform: `docs/handoffs/F5.md`
- C7 registry-writer: `docs/handoffs/C7.md`
- C1 quota-governor: `docs/handoffs/C1.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/backfill-orchestrator.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Qualifier rules; Quotas, budgets and the quota governor
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of F5: `docs/handoffs/F5.md`
6. Handoff of C7: `docs/handoffs/C7.md`
7. Handoff of C1: `docs/handoffs/C1.md`
8. ADR on backfill_status (decision 4)
9. Fb-backfill PRD (hand-over pattern)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`, `jobs.completed`
- Topics written: none named in 6.2
- Job queues in: `jobs.completed`; out: none
- Tables read: `sources`, `client_sources`, `budgets`, `backfill_runs`; written or updated: `sources`, `service_runs`, `backfill_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/backfill-orchestrator/`
- `docs/handoffs/C10.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C10.md` from the fresh-session review

## Watch for

- Single writer of backfill_status
- A failed or slow backfill ends capped and the source joins the rotation anyway
- registry-writer is the only writer of the registry's identity and policy columns and of source.events; each operational column has one named owner (ADR-0013, ADR-0014)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C8, C9, C11

## How to run it

- Plan: `claude --worktree C10 --permission-mode plan`, then `/plan-session C10`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C10` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C10`, then `/review-session C10`
- Fix: `claude --worktree C10` (or the build terminal), `/fix-session C10`; then a fresh session runs `/review-session C10 recheck`; merge when the review has no open blocker or should-fix
