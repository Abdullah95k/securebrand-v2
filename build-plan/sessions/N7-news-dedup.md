# N7 · news-dedup

Wave 3 · First real data, and the Meta review build · track News · size M (1 to 2 days with review) · kind service

## Builds

Story clustering and duplicates across outlets into news.dedup.

Service `news-dedup` · PRD `docs/prds/news/news-dedup.md` · lane Processing · route green · 12 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- N6 news-article-extractor (Python): `docs/handoffs/N6.md`
- C4 normalize-item (core): `docs/handoffs/C4.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/news/news-dedup.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes; Per-platform fact sheets: News websites
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of N6: `docs/handoffs/N6.md`
6. Handoff of C4: `docs/handoffs/C4.md`
7. The N0 probe report `docs/probes/news.md` and the fixtures in `fixtures/news/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)
9. ADR on news.dedup (decision 6)

## Contracts it touches (from PRD section 6)

- Topics read: `raw.items`
- Topics written: `news.dedup`
- Job queue: `jobs.news-dedup` if the PRD's section 5.1 schedules jobs
- Tables read: `sources`, `news_urls`, `news_stories`, `news_story_members`; written or updated: `service_runs`, `news_stories`, `news_story_members`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/news-dedup/`
- `docs/handoffs/N7.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/N7.md` from the fresh-session review

## Watch for

- Stateless where the PRD says so; replay from raw-archiver must reproduce the same output for the same model version

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

N3, N4, N5, N8

## How to run it

- Plan: `claude --worktree N7 --permission-mode plan`, then `/plan-session N7`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session N7` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree N7`, then `/review-session N7`
- Fix: `claude --worktree N7` (or the build terminal), `/fix-session N7`; then a fresh session runs `/review-session N7 recheck`; merge when the review has no open blocker or should-fix
