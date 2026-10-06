# VTT6 · tt-video-stats-refresher

Wave 7 · Amber vendor routes (optional) · track Amber · size M (1 to 2 days with review) · kind service

## Builds

+24 h and +7 d video stats.

Service `tt-video-stats-refresher` · PRD `docs/prds/tiktok/tt-video-stats-refresher.md` · lane Comments and stats · route amber · 10 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- VTT4 tt-profile-videos-poller: `docs/handoffs/VTT4.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/tiktok/tt-video-stats-refresher.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; Rotation policy (comments and metrics); Addendum: Comment series profiles; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: TikTok
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of VTT4: `docs/handoffs/VTT4.md`
6. Handoff of C11: `docs/handoffs/C11.md`
7. The VTT0 probe report `docs/probes/tt-vendor.md` and the fixtures in `fixtures/tiktok-vendor/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `item.metrics`, `deletions`
- Job queues in: `jobs.tt-video-stats-refresher`; out: none
- Tables read: `sources`, `clients`, `budgets`, `vendor_keys`, `service_runs`; written or updated: `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/tt-video-stats-refresher/`
- `docs/handoffs/VTT6.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/VTT6.md` from the fresh-session review

## Watch for

- Only comment-decay-scheduler emits these jobs; report counts on every job
- Amber: runs only behind its flag (off by default); provenance says route = amber and names the vendor; its data is excluded from government contracts, and a source a government client watches never falls back to it; the quota governor stretches it from 80% of budget

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

VTT5

## How to run it

- Plan: `claude --worktree VTT6 --permission-mode plan`, then `/plan-session VTT6`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session VTT6` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree VTT6`, then `/review-session VTT6`
- Fix: `claude --worktree VTT6` (or the build terminal), `/fix-session VTT6`; then a fresh session runs `/review-session VTT6 recheck`; merge when the review has no open blocker or should-fix
