# C11 · comment-decay-scheduler

Wave 2 · Shared core · track Core · size L (3 to 5 days with review) · kind service · on the critical path

## Builds

Comment series per route, armed early stop, extension, hot posts, reply and metrics jobs, driven by jobs.completed.

Service `comment-decay-scheduler` · PRD `docs/prds/shared/comment-decay-scheduler.md` · lane Registry · route shared · 11 acceptance criteria (section 13) · 6 open questions (section 14)

## Needs first (merged, with a closed review)

- F5 SDK scheduling, quota client, adapter kit, fake platform: `docs/handoffs/F5.md`
- F3 Control-plane schema: `docs/handoffs/F3.md`
- C1 quota-governor: `docs/handoffs/C1.md`
- G0 Gate: foundation: `docs/gates/G0.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/comment-decay-scheduler.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Qualifier rules; Quotas, budgets and the quota governor
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of F5: `docs/handoffs/F5.md`
6. Handoff of F3: `docs/handoffs/F3.md`
7. Handoff of C1: `docs/handoffs/C1.md`
8. Comment series table (CONVENTIONS addendum)
9. ADRs for decisions 1 to 3
10. C0 ref-comments-fetcher reports

## Contracts it touches (from PRD section 6)

- Topics read: `items.normalized`, `source.events`, `deletions`, `jobs.completed`
- Topics written: none named in 6.2
- Job queues in: `jobs.completed`; out: `jobs.fb-reactions-fetcher`, `jobs.ig-account-media-poller`, `jobs.tt-video-stats-refresher`, `jobs.yt-video-details-fetcher`
- Tables read: `sources`, `client_sources`, `budgets`, `comment_series`; written or updated: `service_runs`, `comment_series`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/comment-decay-scheduler/`
- `docs/handoffs/C11.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C11.md` from the fresh-session review
- comment_series rows
- jobs for every comment, reply and metrics service

## Watch for

- Only this service emits comment, reply and metrics jobs
- Early stop is armed after 5 stored comments or the +24 h step
- On amber routes, hot-post extras go first above 80% of budget
- registry-writer is the only writer of the registry's identity and policy columns and of source.events; each operational column has one named owner (ADR-0013, ADR-0014)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C8, C9, C10

## How to run it

- Plan: `claude --worktree C11 --permission-mode plan`, then `/plan-session C11`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C11` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C11`, then `/review-session C11`
- Fix: `claude --worktree C11` (or the build terminal), `/fix-session C11`; then a fresh session runs `/review-session C11 recheck`; merge when the review has no open blocker or should-fix
