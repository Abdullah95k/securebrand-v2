# X7 · x-compliance-sync

Wave 4 · YouTube, X, and Facebook in development mode · track X · size M (1 to 2 days with review) · kind service

## Builds

Batch compliance mirrored into every store.

Service `x-compliance-sync` · PRD `docs/prds/x/x-compliance-sync.md` · lane Support · route green · 13 acceptance criteria (section 13) · 7 open questions (section 14)

## Needs first (merged, with a closed review)

- X0 X probe: `docs/handoffs/X0.md`
- C13 deletion-propagator: `docs/handoffs/C13.md`
- C14 retention-purger: `docs/handoffs/C14.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

Any-time track: earliest when the above are met; deadline before X data reaches staging.

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/x/x-compliance-sync.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes; Quotas, budgets and the quota governor; Per-platform fact sheets: X
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of X0: `docs/handoffs/X0.md`
6. Handoff of C13: `docs/handoffs/C13.md`
7. Handoff of C14: `docs/handoffs/C14.md`
8. The X0 probe report `docs/probes/x.md` and the fixtures in `fixtures/x/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `deletions`
- Job queues in: `jobs.x-compliance-sync`; out: none
- Tables read: `sources`, `client_sources`, `cursors`, `deletion_requests`; written or updated: `sources`, `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/x-compliance-sync/`
- `docs/handoffs/X7.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/X7.md` from the fresh-session review

## Watch for

- Deletions and withholds mirrored within 24 hours of X's signal
- Deletion and retention actions are audited before they run, so a replay changes nothing

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

X1, X2, X3

## How to run it

- Plan: `claude --worktree X7 --permission-mode plan`, then `/plan-session X7`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session X7` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree X7`, then `/review-session X7`
- Fix: `claude --worktree X7` (or the build terminal), `/fix-session X7`; then a fresh session runs `/review-session X7 recheck`; merge when the review has no open blocker or should-fix
