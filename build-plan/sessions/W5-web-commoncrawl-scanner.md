# W5 · web-commoncrawl-scanner

Wave 3 · First real data, and the Meta review build · track Web · size M (1 to 2 days with review) · kind service

## Builds

Monthly Common Crawl scan for new Iraqi sites.

Service `web-commoncrawl-scanner` · PRD `docs/prds/web/web-commoncrawl-scanner.md` · lane Discover and qualify · route green · 10 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- W3 search-hit-router: `docs/handoffs/W3.md`
- N2 news-site-resolver: `docs/handoffs/N2.md`

Any-time track: earliest after W3 and N2; deadline none.

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/web/web-commoncrawl-scanner.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: Web search
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of W3: `docs/handoffs/W3.md`
6. Handoff of N2: `docs/handoffs/N2.md`
7. The W0 probe report `docs/probes/web.md` and the fixtures in `fixtures/web/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`, `discovery.hits`, `search.results`
- Job queue: `jobs.web-commoncrawl-scanner` if the PRD's section 5.1 schedules jobs
- Tables read: `sources`, `service_runs`; written or updated: `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/web-commoncrawl-scanner/`
- `docs/handoffs/W5.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/W5.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Any session (any-time track)

## How to run it

- Plan: `claude --worktree W5 --permission-mode plan`, then `/plan-session W5`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session W5` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree W5`, then `/review-session W5`
- Fix: `claude --worktree W5` (or the build terminal), `/fix-session W5`; then a fresh session runs `/review-session W5 recheck`; merge when the review has no open blocker or should-fix
