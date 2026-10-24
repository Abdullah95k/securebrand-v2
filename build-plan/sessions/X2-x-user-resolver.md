# X2 · x-user-resolver

Wave 4 · YouTube, X, and Facebook in development mode · track X · size M (1 to 2 days with review) · kind service

## Builds

Resolves account candidates.

Service `x-user-resolver` · PRD `docs/prds/x/x-user-resolver.md` · lane Discover and qualify · route green · 11 acceptance criteria (section 13) · 6 open questions (section 14)

## Needs first (merged, with a closed review)

- X1 x-recent-search: `docs/handoffs/X1.md`
- C8 poster-resolver: `docs/handoffs/C8.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/x/x-user-resolver.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: X
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of X1: `docs/handoffs/X1.md`
6. Handoff of C8: `docs/handoffs/C8.md`
7. The X0 probe report `docs/probes/x.md` and the fixtures in `fixtures/x/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`, `deletions`
- Topics written: `poster.profiles`
- Job queues in: `jobs.x-user-resolver`; out: none
- Tables read: `sources`, `clients`, `budgets`, `profile_cache`; written or updated: `sources`, `service_runs`, `profile_cache`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/x-user-resolver/`
- `docs/handoffs/X2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/X2.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

X3, X7

## How to run it

- Plan: `claude --worktree X2 --permission-mode plan`, then `/plan-session X2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session X2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree X2`, then `/review-session X2`
- Fix: `claude --worktree X2` (or the build terminal), `/fix-session X2`; then a fresh session runs `/review-session X2 recheck`; merge when the review has no open blocker or should-fix
