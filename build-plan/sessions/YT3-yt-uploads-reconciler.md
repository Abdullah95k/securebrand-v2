# YT3 · yt-uploads-reconciler

Wave 4 · YouTube, X, and Facebook in development mode · track YouTube · size M (1 to 2 days with review) · kind service

## Builds

Uploads-playlist reconciliation on rotation.

Service `yt-uploads-reconciler` · PRD `docs/prds/youtube/yt-uploads-reconciler.md` · lane Fetch posts · route green · 11 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- YT1 yt-channel-resolver: `docs/handoffs/YT1.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/youtube/yt-uploads-reconciler.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: YouTube
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of YT1: `docs/handoffs/YT1.md`
6. The YT0 probe report `docs/probes/youtube.md` and the fixtures in `fixtures/youtube/`
7. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `source.events`, `jobs.completed`
- Job queues in: `jobs.yt-uploads-reconciler`; out: `jobs.completed`, `jobs.yt-video-details-fetcher`
- Tables read: `sources`, `cursors`, `budgets`; written or updated: `sources`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/yt-uploads-reconciler/`
- `docs/handoffs/YT3.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/YT3.md` from the fresh-session review

## Watch for

- next_poll_at is set from the start of the last poll; order by next_poll_at then tier; most stale first when behind, with rotation_behind
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

YT2, YT4

## How to run it

- Plan: `claude --worktree YT3 --permission-mode plan`, then `/plan-session YT3`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session YT3` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree YT3`, then `/review-session YT3`
- Fix: `claude --worktree YT3` (or the build terminal), `/fix-session YT3`; then a fresh session runs `/review-session YT3 recheck`; merge when the review has no open blocker or should-fix
