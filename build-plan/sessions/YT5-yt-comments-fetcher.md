# YT5 · yt-comments-fetcher

Wave 4 · YouTube, X, and Facebook in development mode · track YouTube · size M (1 to 2 days with review) · kind service

## Builds

commentThreads.list on the YouTube comment series.

Service `yt-comments-fetcher` · PRD `docs/prds/youtube/yt-comments-fetcher.md` · lane Comments · route green · 12 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- YT4 yt-video-details-fetcher: `docs/handoffs/YT4.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/youtube/yt-comments-fetcher.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; Rotation policy (the comments part); Addendum: Comment series profiles; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: YouTube
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of YT4: `docs/handoffs/YT4.md`
6. Handoff of C11: `docs/handoffs/C11.md`
7. The YT0 probe report `docs/probes/youtube.md` and the fixtures in `fixtures/youtube/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`, `deletions`
- Job queues in: `jobs.yt-comments-fetcher`; out: none
- Tables read: `sources`, `cursors`, `budgets`; written or updated: `cursors`, `review_queue`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/yt-comments-fetcher/`
- `docs/handoffs/YT5.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/YT5.md` from the fresh-session review

## Watch for

- Only comment-decay-scheduler emits comment, reply and metrics jobs; this service never schedules its own
- Report new_count, seen_count, pages and cost_units on every job: the scheduler decides early stop and extension from them
- Edits become new versions; deletions only when the API response is complete (reason platform_sync)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

YT8

## How to run it

- Plan: `claude --worktree YT5 --permission-mode plan`, then `/plan-session YT5`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session YT5` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree YT5`, then `/review-session YT5`
- Fix: `claude --worktree YT5` (or the build terminal), `/fix-session YT5`; then a fresh session runs `/review-session YT5 recheck`; merge when the review has no open blocker or should-fix
