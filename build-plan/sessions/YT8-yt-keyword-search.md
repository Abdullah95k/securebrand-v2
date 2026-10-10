# YT8 · yt-keyword-search

Wave 4 · YouTube, X, and Facebook in development mode · track YouTube · size M (1 to 2 days with review) · kind service

## Builds

search.list within the 100-a-day bucket.

Service `yt-keyword-search` · PRD `docs/prds/youtube/yt-keyword-search.md` · lane Discover and qualify · route green · 9 acceptance criteria (section 13) · 0 open questions (section 14)

## Needs first (merged, with a closed review)

- YT1 yt-channel-resolver: `docs/handoffs/YT1.md`
- YT4 yt-video-details-fetcher: `docs/handoffs/YT4.md`
- C1 quota-governor: `docs/handoffs/C1.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/youtube/yt-keyword-search.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: YouTube
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of YT1: `docs/handoffs/YT1.md`
6. Handoff of YT4: `docs/handoffs/YT4.md`
7. Handoff of C1: `docs/handoffs/C1.md`
8. The YT0 probe report `docs/probes/youtube.md` and the fixtures in `fixtures/youtube/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`
- Job queues in: its own `jobs.yt-keyword-search`; out: `jobs.yt-video-details-fetcher`
- Tables read: `sources`, `keywords`, `cursors`, `budgets`, `service_runs`; written or updated: `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/yt-keyword-search/`
- `docs/handoffs/YT8.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/YT8.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

YT5, YT6, YT7

## How to run it

- Plan: `claude --worktree YT8 --permission-mode plan`, then `/plan-session YT8`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session YT8` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree YT8`, then `/review-session YT8`
- Fix: `claude --worktree YT8` (or the build terminal), `/fix-session YT8`; then a fresh session runs `/review-session YT8 recheck`; merge when the review has no open blocker or should-fix
