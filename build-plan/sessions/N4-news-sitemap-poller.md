# N4 · news-sitemap-poller

Wave 3 · First real data, and the Meta review build · track News · size M (1 to 2 days with review) · kind service

## Builds

News and regular sitemaps on rotation into article.urls.

Service `news-sitemap-poller` · PRD `docs/prds/news/news-sitemap-poller.md` · lane Fetch posts · route green · 11 acceptance criteria (section 13) · 3 open questions (section 14)

## Needs first (merged, with a closed review)

- N1 news-robots-checker: `docs/handoffs/N1.md`
- N2 news-site-resolver: `docs/handoffs/N2.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/news/news-sitemap-poller.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: News websites
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of N1: `docs/handoffs/N1.md`
6. Handoff of N2: `docs/handoffs/N2.md`
7. The N0 probe report `docs/probes/news.md` and the fixtures in `fixtures/news/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)
9. N0 sitemap fixtures

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`, `crawl.policies`
- Topics written: `article.urls`
- Job queues in: `jobs.news-sitemap-poller`; out: `jobs.news-robots-checker`, `jobs.news-site-resolver`
- Tables read: `sources`, `cursors`, `crawl_policies`, `news_urls`, `news_sites`; written or updated: `sources`, `cursors`, `crawl_policies`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/news-sitemap-poller/`
- `docs/handoffs/N4.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/N4.md` from the fresh-session review

## Watch for

- next_poll_at is set from the start of the last poll; order by next_poll_at then tier; most stale first when behind, with rotation_behind
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

N3, N5, N6, N7

## How to run it

- Plan: `claude --worktree N4 --permission-mode plan`, then `/plan-session N4`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session N4` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree N4`, then `/review-session N4`
- Fix: `claude --worktree N4` (or the build terminal), `/fix-session N4`; then a fresh session runs `/review-session N4 recheck`; merge when the review has no open blocker or should-fix
