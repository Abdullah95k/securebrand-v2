# X6 · x-replies-fetcher

Wave 4 · YouTube, X, and Facebook in development mode · track X · size M (1 to 2 days with review) · kind service

## Builds

Replies and quotes by conversation_id on the X series.

Service `x-replies-fetcher` · PRD `docs/prds/x/x-replies-fetcher.md` · lane Comments · route green · 12 acceptance criteria (section 13) · 7 open questions (section 14)

## Needs first (merged, with a closed review)

- X3 x-user-timeline-poller: `docs/handoffs/X3.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/x/x-replies-fetcher.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; Rotation policy (the comments part); Addendum: Comment series profiles; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: X
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of X3: `docs/handoffs/X3.md`
6. Handoff of C11: `docs/handoffs/C11.md`
7. The X0 probe report `docs/probes/x.md` and the fixtures in `fixtures/x/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`, `discovery.hits`, `deletions`
- Job queues in: `jobs.x-replies-fetcher`; out: none
- Tables read: `sources`, `clients`, `cursors`, `budgets`; written or updated: `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/x-replies-fetcher/`
- `docs/handoffs/X6.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/X6.md` from the fresh-session review

## Watch for

- Only comment-decay-scheduler emits comment, reply and metrics jobs; this service never schedules its own
- Return new_count, seen_count, pages, cost_units and reply_candidates to the SDK job wrapper, which reports them on jobs.completed; the scheduler decides early stop and extension from them (ADR-0017, ADR-0019)
- Compare with the stored set through the SDK comment-state helper: an edit is a new version where the platform gives comment ids, a new comment otherwise; a missing comment is a deletion (platform_sync) only after a confirmed second miss or a platform signal, never on a route whose reads are not complete listings (ADR-0009, ADR-0046, ADR-0062)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

X4, X5

## How to run it

- Plan: `claude --worktree X6 --permission-mode plan`, then `/plan-session X6`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session X6` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree X6`, then `/review-session X6`
- Fix: `claude --worktree X6` (or the build terminal), `/fix-session X6`; then a fresh session runs `/review-session X6 recheck`; merge when the review has no open blocker or should-fix
