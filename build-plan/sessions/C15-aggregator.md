# C15 · aggregator

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

Hourly and daily aggregates from base tables and derived scores, watermark for alerts.

Service `aggregator` · PRD `docs/prds/shared/aggregator.md` · lane Processing · route shared · 12 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- C6 store-writer: `docs/handoffs/C6.md`
- F8 ClickHouse schema: `docs/handoffs/F8.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/aggregator.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of C6: `docs/handoffs/C6.md`
6. Handoff of F8: `docs/handoffs/F8.md`

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`, `deletions`
- Topics written: none named in 6.2
- Job queues in: `jobs.aggregator`; out: none
- Tables read: `cursors`, `retention_classes`, `service_runs`; written or updated: `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/aggregator/`
- `docs/handoffs/C15.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C15.md` from the fresh-session review

## Watch for

- Aggregates rebuild from base tables after deletions
- Keep per-channel YouTube aggregates separable (cross-owner aggregation question is open)
- Stateless where the PRD says so; replay from raw-archiver must reproduce the same output for the same model version

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C12, C13, C14

## How to run it

- Plan: `claude --worktree C15 --permission-mode plan`, then `/plan-session C15`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C15` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C15`, then `/review-session C15`
- Fix: `claude --worktree C15` (or the build terminal), `/fix-session C15`; then a fresh session runs `/review-session C15 recheck`; merge when the review has no open blocker or should-fix
