# C13 · deletion-propagator

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

Deletions to every store: ClickHouse, archive, aggregates, alerts.

Service `deletion-propagator` · PRD `docs/prds/shared/deletion-propagator.md` · lane Support · route shared · 11 acceptance criteria (section 13) · 6 open questions (section 14)

## Needs first (merged, with a closed review)

- F8 ClickHouse schema: `docs/handoffs/F8.md`
- C2 raw-archiver: `docs/handoffs/C2.md`
- C6 store-writer: `docs/handoffs/C6.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/deletion-propagator.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes; Quotas, budgets and the quota governor
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of F8: `docs/handoffs/F8.md`
6. Handoff of C2: `docs/handoffs/C2.md`
7. Handoff of C6: `docs/handoffs/C6.md`

## Contracts it touches (from PRD section 6)

- Topics read: `deletions`
- Topics written: none named in 6.2
- Job queues in: its own `jobs.deletion-propagator`; out: `jobs.aggregator`
- Tables read: `clients`, `deletion_requests`; written or updated: `deletion_requests`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/deletion-propagator/`
- `docs/handoffs/C13.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C13.md` from the fresh-session review

## Watch for

- Deletion must reach archive objects (rewrite or tombstone)
- Mode withhold and author scope are needed by x-compliance-sync
- Deletion and retention actions are audited before they run, so a replay changes nothing

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C12, C15

## How to run it

- Plan: `claude --worktree C13 --permission-mode plan`, then `/plan-session C13`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C13` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C13`, then `/review-session C13`
- Fix: `claude --worktree C13` (or the build terminal), `/fix-session C13`; then a fresh session runs `/review-session C13 recheck`; merge when the review has no open blocker or should-fix
