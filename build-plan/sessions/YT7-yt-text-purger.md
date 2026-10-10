# YT7 · yt-text-purger

Wave 4 · YouTube, X, and Facebook in development mode · track YouTube · size M (1 to 2 days with review) · kind service

## Builds

30-day deletion or refresh of YouTube text.

Service `yt-text-purger` · PRD `docs/prds/youtube/yt-text-purger.md` · lane Support · route green · 12 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- YT5 yt-comments-fetcher: `docs/handoffs/YT5.md`
- C14 retention-purger: `docs/handoffs/C14.md`

Any-time track: earliest when the above are met; deadline before YouTube data reaches staging.

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/youtube/yt-text-purger.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes; Quotas, budgets and the quota governor; Per-platform fact sheets: YouTube
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of YT5: `docs/handoffs/YT5.md`
6. Handoff of C14: `docs/handoffs/C14.md`
7. The YT0 probe report `docs/probes/youtube.md` and the fixtures in `fixtures/youtube/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `registry.decisions`
- Topics written: `deletions`
- Job queues in: `jobs.yt-text-purger`; out: `jobs.yt-comments-fetcher`, `jobs.yt-replies-fetcher`, `jobs.yt-video-details-fetcher`
- Tables read: `sources`, `clients`, `client_sources`, `deletion_requests`, `retention_classes`; written or updated: `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/yt-text-purger/`
- `docs/handoffs/YT7.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/YT7.md` from the fresh-session review

## Watch for

- Comment text, titles and descriptions have no exemption from the 30 days
- Deletion and retention actions are audited before they run, so a replay changes nothing

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

YT6, YT8

## How to run it

- Plan: `claude --worktree YT7 --permission-mode plan`, then `/plan-session YT7`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session YT7` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree YT7`, then `/review-session YT7`
- Fix: `claude --worktree YT7` (or the build terminal), `/fix-session YT7`; then a fresh session runs `/review-session YT7 recheck`; merge when the review has no open blocker or should-fix
