# X5 · x-full-archive-search

Wave 4 · YouTube, X, and Facebook in development mode · track X · size M (1 to 2 days with review) · kind service

## Builds

Backfill and gap fill from the full archive.

Service `x-full-archive-search` · PRD `docs/prds/x/x-full-archive-search.md` · lane Fetch posts · route green · 11 acceptance criteria (section 13) · 6 open questions (section 14)

## Needs first (merged, with a closed review)

- X1 x-recent-search: `docs/handoffs/X1.md`
- C10 backfill-orchestrator: `docs/handoffs/C10.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/x/x-full-archive-search.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: X
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of X1: `docs/handoffs/X1.md`
6. Handoff of C10: `docs/handoffs/C10.md`
7. The X0 probe report `docs/probes/x.md` and the fixtures in `fixtures/x/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `jobs.completed`
- Topics written: `raw.items`, `source.events`, `jobs.completed`
- Job queues in: `jobs.completed`, `jobs.x-full-archive-search`; out: `jobs.completed`
- Tables read: `sources`, `keywords`, `clients`, `cursors`, `budgets`; written or updated: `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/x-full-archive-search/`
- `docs/handoffs/X5.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/X5.md` from the fresh-session review

## Watch for

- The due time is next_due_at in this service's own cursors row, set from the start of the last poll; order by it then tier; most stale first when behind, with rotation_behind (ADR-0015)
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

X4, X6

## How to run it

- Plan: `claude --worktree X5 --permission-mode plan`, then `/plan-session X5`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session X5` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree X5`, then `/review-session X5`
- Fix: `claude --worktree X5` (or the build terminal), `/fix-session X5`; then a fresh session runs `/review-session X5 recheck`; merge when the review has no open blocker or should-fix
