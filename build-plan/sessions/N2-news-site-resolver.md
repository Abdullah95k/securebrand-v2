# N2 · news-site-resolver

Wave 3 · First real data, and the Meta review build · track News · size M (1 to 2 days with review) · kind service

## Builds

Resolves candidate domains into news sources.

Service `news-site-resolver` · PRD `docs/prds/news/news-site-resolver.md` · lane Discover and qualify · route green · 9 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- N1 news-robots-checker: `docs/handoffs/N1.md`
- C8 poster-resolver: `docs/handoffs/C8.md`
- C9 qualifier: `docs/handoffs/C9.md`
- C3 lang-dialect-id: `docs/handoffs/C3.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/news/news-site-resolver.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: News websites
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of N1: `docs/handoffs/N1.md`
6. Handoff of C8: `docs/handoffs/C8.md`
7. Handoff of C9: `docs/handoffs/C9.md`
8. Handoff of C3: `docs/handoffs/C3.md`
9. The N0 probe report `docs/probes/news.md` and the fixtures in `fixtures/news/`
10. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)
11. C8 resolver dispatch contract

## Contracts it touches (from PRD section 6)

- Topics read: `crawl.policies`
- Topics written: `poster.profiles`
- Job queues in: `jobs.news-site-resolver`; out: `jobs.news-robots-checker`
- Tables read: `sources`, `clients`, `client_sources`, `cursors`, `decisions`, `crawl_policies`, `service_runs`, `news_sites`; written or updated: `sources`, `cursors`, `service_runs`, `news_sites`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/news-site-resolver/`
- `docs/handoffs/N2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/N2.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree N2 --permission-mode plan`, then `/plan-session N2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session N2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree N2`, then `/review-session N2`
- Fix: `claude --worktree N2` (or the build terminal), `/fix-session N2`; then a fresh session runs `/review-session N2 recheck`; merge when the review has no open blocker or should-fix
