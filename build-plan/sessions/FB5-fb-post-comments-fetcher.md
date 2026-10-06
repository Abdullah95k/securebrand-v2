# FB5 · fb-post-comments-fetcher

Wave 4 · YouTube, X, and Facebook in development mode · track Facebook · size L (3 to 5 days with review) · kind service

## Builds

Comment series with hash keys (no ids under PPCA), edits and sweeps.

Service `fb-post-comments-fetcher` · PRD `docs/prds/facebook/fb-post-comments-fetcher.md` · lane Comments · route green · 11 acceptance criteria (section 13) · 6 open questions (section 14)

## Needs first (merged, with a closed review)

- FB2 fb-page-feed-poller: `docs/handoffs/FB2.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/facebook/fb-post-comments-fetcher.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; Rotation policy (the comments part); Addendum: Comment series profiles; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: Facebook
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of FB2: `docs/handoffs/FB2.md`
6. Handoff of C11: `docs/handoffs/C11.md`
7. The FB0 probe report `docs/probes/meta.md` and the fixtures in `fixtures/facebook/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `deletions`
- Job queues in: `jobs.fb-post-comments-fetcher`; out: none
- Tables read: `sources`, `clients`, `cursors`, `budgets`; written or updated: `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/fb-post-comments-fetcher/`
- `docs/handoffs/FB5.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/FB5.md` from the fresh-session review

## Watch for

- Identical comments in the same second collide by design: measure, do not hide
- Only comment-decay-scheduler emits comment, reply and metrics jobs; this service never schedules its own
- Report new_count, seen_count, pages and cost_units on every job: the scheduler decides early stop and extension from them
- Edits become new versions; deletions only when the API response is complete (reason platform_sync)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

FB3, FB4, FB6

## How to run it

- Plan: `claude --worktree FB5 --permission-mode plan`, then `/plan-session FB5`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session FB5` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree FB5`, then `/review-session FB5`
- Fix: `claude --worktree FB5` (or the build terminal), `/fix-session FB5`; then a fresh session runs `/review-session FB5 recheck`; merge when the review has no open blocker or should-fix
