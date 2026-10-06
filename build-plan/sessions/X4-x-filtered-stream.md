# X4 · x-filtered-stream

Wave 4 · YouTube, X, and Facebook in development mode · track X · size M (1 to 2 days with review) · kind service

## Builds

Filtered stream with up to 1,000 rules.

Service `x-filtered-stream` · PRD `docs/prds/x/x-filtered-stream.md` · lane Fetch posts · route green · 11 acceptance criteria (section 13) · 6 open questions (section 14)

## Needs first (merged, with a closed review)

- X1 x-recent-search: `docs/handoffs/X1.md`
- X3 x-user-timeline-poller: `docs/handoffs/X3.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/x/x-filtered-stream.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: X
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of X1: `docs/handoffs/X1.md`
6. Handoff of X3: `docs/handoffs/X3.md`
7. The X0 probe report `docs/probes/x.md` and the fixtures in `fixtures/x/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`, `jobs.completed`
- Topics written: `raw.items`
- Job queues in: `jobs.completed`; out: `jobs.x-full-archive-search`, `jobs.x-recent-search`
- Tables read: `sources`, `keywords`, `clients`, `client_sources`, `cursors`, `service_runs`; written or updated: `cursors`, `review_queue`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/x-filtered-stream/`
- `docs/handoffs/X4.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/X4.md` from the fresh-session review

## Watch for

- next_poll_at is set from the start of the last poll; order by next_poll_at then tier; most stale first when behind, with rotation_behind
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

X5, X6

## How to run it

- Plan: `claude --worktree X4 --permission-mode plan`, then `/plan-session X4`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session X4` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree X4`, then `/review-session X4`
- Fix: `claude --worktree X4` (or the build terminal), `/fix-session X4`; then a fresh session runs `/review-session X4 recheck`; merge when the review has no open blocker or should-fix
