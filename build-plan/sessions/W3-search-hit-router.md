# W3 · search-hit-router

Wave 3 · First real data, and the Meta review build · track Web · size M (1 to 2 days with review) · kind service

## Builds

Routes search results to poster-resolver, news-site-resolver and article.urls.

Service `search-hit-router` · PRD `docs/prds/web/search-hit-router.md` · lane Discover and qualify · route green · 10 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- W1 web-search-perplexity: `docs/handoffs/W1.md`
- C8 poster-resolver: `docs/handoffs/C8.md`
- N2 news-site-resolver: `docs/handoffs/N2.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/web/search-hit-router.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: Web search
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of W1: `docs/handoffs/W1.md`
6. Handoff of C8: `docs/handoffs/C8.md`
7. Handoff of N2: `docs/handoffs/N2.md`
8. The W0 probe report `docs/probes/web.md` and the fixtures in `fixtures/web/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`, `search.results`
- Topics written: `discovery.hits`, `article.urls`
- Job queue: `jobs.search-hit-router` if the PRD's section 5.1 schedules jobs
- Tables read: `sources`, `clients`; written or updated: `clients`, `review_queue`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/search-hit-router/`
- `docs/handoffs/W3.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/W3.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

W2

## How to run it

- Plan: `claude --worktree W3 --permission-mode plan`, then `/plan-session W3`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session W3` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree W3`, then `/review-session W3`
- Fix: `claude --worktree W3` (or the build terminal), `/fix-session W3`; then a fresh session runs `/review-session W3 recheck`; merge when the review has no open blocker or should-fix
