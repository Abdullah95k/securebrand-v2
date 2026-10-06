# FB6 · fb-page-search

Wave 4 · YouTube, X, and Facebook in development mode · track Facebook · size M (1 to 2 days with review) · kind service

## Builds

Pages Search by keyword into discovery.hits.

Service `fb-page-search` · PRD `docs/prds/facebook/fb-page-search.md` · lane Discover and qualify · route green · 9 acceptance criteria (section 13) · 3 open questions (section 14)

## Needs first (merged, with a closed review)

- FB1 fb-page-resolver: `docs/handoffs/FB1.md`
- C8 poster-resolver: `docs/handoffs/C8.md`

Any-time track: earliest after FB1; deadline none.

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/facebook/fb-page-search.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: Facebook
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of FB1: `docs/handoffs/FB1.md`
6. Handoff of C8: `docs/handoffs/C8.md`
7. The FB0 probe report `docs/probes/meta.md` and the fixtures in `fixtures/facebook/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`, `discovery.hits`
- Job queues in: `jobs.fb-page-search`; out: none
- Tables read: `sources`, `keywords`, `clients`, `cursors`, `budgets`, `decisions`; written or updated: `cursors`, `budgets`, `decisions`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/fb-page-search/`
- `docs/handoffs/FB6.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/FB6.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Individuals are never profiled: a mention keeps a hashed author reference

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

FB3, FB4, FB5

## How to run it

- Plan: `claude --worktree FB6 --permission-mode plan`, then `/plan-session FB6`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session FB6` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree FB6`, then `/review-session FB6`
- Fix: `claude --worktree FB6` (or the build terminal), `/fix-session FB6`; then a fresh session runs `/review-session FB6 recheck`; merge when the review has no open blocker or should-fix
