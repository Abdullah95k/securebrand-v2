# X1 · x-recent-search

Wave 4 · YouTube, X, and Facebook in development mode · track X · size L (3 to 5 days with review) · kind service

## Builds

Keyword search on rotation; the read ledger; the X mapper.

Service `x-recent-search` · PRD `docs/prds/x/x-recent-search.md` · lane Discover and qualify · route green · 10 acceptance criteria (section 13) · 3 open questions (section 14)

## Needs first (merged, with a closed review)

- X0 X probe: `docs/handoffs/X0.md`
- C1 quota-governor: `docs/handoffs/C1.md`
- C5 keyword-matcher: `docs/handoffs/C5.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/x/x-recent-search.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: X
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of X0: `docs/handoffs/X0.md`
6. Handoff of C1: `docs/handoffs/C1.md`
7. Handoff of C5: `docs/handoffs/C5.md`
8. The X0 probe report `docs/probes/x.md` and the fixtures in `fixtures/x/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `discovery.hits`
- Job queues in: `jobs.x-recent-search`; out: none
- Tables read: `sources`, `keywords`, `clients`, `cursors`, `budgets`; written or updated: `sources`, `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/x-recent-search/`
- `docs/handoffs/X1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/X1.md` from the fresh-session review
- x_read_ledger semantics used by every X service
- X mapper in normalize-item

## Watch for

- Charges deduplicate per resource per UTC day; 3,000,000 post reads per billing cycle
- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

X7

## How to run it

- Plan: `claude --worktree X1 --permission-mode plan`, then `/plan-session X1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session X1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree X1`, then `/review-session X1`
- Fix: `claude --worktree X1` (or the build terminal), `/fix-session X1`; then a fresh session runs `/review-session X1 recheck`; merge when the review has no open blocker or should-fix
