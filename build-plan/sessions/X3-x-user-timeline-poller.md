# X3 · x-user-timeline-poller

Wave 4 · YouTube, X, and Facebook in development mode · track X · size M (1 to 2 days with review) · kind service

## Builds

Registered accounts' timelines on rotation.

Service `x-user-timeline-poller` · PRD `docs/prds/x/x-user-timeline-poller.md` · lane Fetch posts · route green · 10 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- X1 x-recent-search: `docs/handoffs/X1.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/x/x-user-timeline-poller.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: X
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of X1: `docs/handoffs/X1.md`
6. The X0 probe report `docs/probes/x.md` and the fixtures in `fixtures/x/`
7. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `source.events`, `jobs.completed`
- Job queues in: `jobs.x-user-timeline-poller`; out: `jobs.completed`
- Tables read: `sources`, `clients`, `cursors`, `budgets`, `service_runs`; written or updated: `sources`, `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/x-user-timeline-poller/`
- `docs/handoffs/X3.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/X3.md` from the fresh-session review

## Watch for

- The due time is next_due_at in this service's own cursors row, set from the start of the last poll; order by it then tier; most stale first when behind, with rotation_behind (ADR-0015)
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

X2, X7

## How to run it

- Plan: `claude --worktree X3 --permission-mode plan`, then `/plan-session X3`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session X3` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree X3`, then `/review-session X3`
- Fix: `claude --worktree X3` (or the build terminal), `/fix-session X3`; then a fresh session runs `/review-session X3 recheck`; merge when the review has no open blocker or should-fix
