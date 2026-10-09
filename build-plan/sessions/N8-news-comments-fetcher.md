# N8 · news-comments-fetcher

Wave 3 · First real data, and the Meta review build · track News · size M (1 to 2 days with review) · kind service

## Builds

Disqus comment series for the sites that use it.

Service `news-comments-fetcher` · PRD `docs/prds/news/news-comments-fetcher.md` · lane Comments · route green · 11 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- N6 news-article-extractor (Python): `docs/handoffs/N6.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`

Any-time track: earliest after N6 and C11; deadline before news go-live, if your sites use Disqus.

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/news/news-comments-fetcher.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; Rotation policy (the comments part); Addendum: Comment series profiles; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: News websites
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of N6: `docs/handoffs/N6.md`
6. Handoff of C11: `docs/handoffs/C11.md`
7. The N0 probe report `docs/probes/news.md` and the fixtures in `fixtures/news/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`, `deletions`
- Job queues in: `jobs.news-comments-fetcher`; out: none
- Tables read: `sources`, `budgets`, `crawl_policies`, `vendor_keys`, `news_sites`; written or updated: `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/news-comments-fetcher/`
- `docs/handoffs/N8.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/N8.md` from the fresh-session review

## Watch for

- Only comment-decay-scheduler emits comment, reply and metrics jobs; this service never schedules its own
- Return new_count, seen_count, pages, cost_units and reply_candidates to the SDK job wrapper, which reports them on jobs.completed; the scheduler decides early stop and extension from them (ADR-0017, ADR-0019)
- Compare with the stored set through the SDK comment-state helper: an edit is a new version where the platform gives comment ids, a new comment otherwise; a missing comment is a deletion (platform_sync) only after a confirmed second miss or a platform signal, never on a route whose reads are not complete listings (ADR-0009, ADR-0046, ADR-0062)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

N7

## How to run it

- Plan: `claude --worktree N8 --permission-mode plan`, then `/plan-session N8`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session N8` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree N8`, then `/review-session N8`
- Fix: `claude --worktree N8` (or the build terminal), `/fix-session N8`; then a fresh session runs `/review-session N8 recheck`; merge when the review has no open blocker or should-fix
