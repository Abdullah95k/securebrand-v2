# C6 · store-writer

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

Upserts of items, comments, analysis and metrics into ClickHouse; dimensions from the control plane.

Service `store-writer` · PRD `docs/prds/shared/store-writer.md` · lane Processing · route shared · 11 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- F4 SDK runtime (Node): `docs/handoffs/F4.md`
- F8 ClickHouse schema: `docs/handoffs/F8.md`
- G0 Gate: foundation: `docs/gates/G0.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/store-writer.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of F4: `docs/handoffs/F4.md`
6. Handoff of F8: `docs/handoffs/F8.md`

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `items.normalized`
- Job queue: `jobs.store-writer` if the PRD's section 5.1 schedules jobs
- Tables read: `sources`, `keywords`, `clients`, `cursors`, `deletion_requests`, `retention_classes`, `service_runs`; written or updated: `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/store-writer/`
- `docs/handoffs/C6.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C6.md` from the fresh-session review

## Watch for

- A deleted item never reappears on replay
- Retention fields set on every row
- Stateless where the PRD says so; replay from raw-archiver must reproduce the same output for the same model version

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C4, C5

## How to run it

- Plan: `claude --worktree C6 --permission-mode plan`, then `/plan-session C6`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C6` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C6`, then `/review-session C6`
- Fix: `claude --worktree C6` (or the build terminal), `/fix-session C6`; then a fresh session runs `/review-session C6 recheck`; merge when the review has no open blocker or should-fix
