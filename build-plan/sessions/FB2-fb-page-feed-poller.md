# FB2 · fb-page-feed-poller

Wave 3 · First real data, and the Meta review build · track Facebook · size L (3 to 5 days with review) · kind service · on the critical path

## Builds

Page posts on rotation through /feed; the Facebook mapper.

Service `fb-page-feed-poller` · PRD `docs/prds/facebook/fb-page-feed-poller.md` · lane Fetch posts · route green · 9 acceptance criteria (section 13) · 2 open questions (section 14)

## Needs first (merged, with a closed review)

- FB1 fb-page-resolver: `docs/handoffs/FB1.md`
- C1 quota-governor: `docs/handoffs/C1.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/facebook/fb-page-feed-poller.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: Facebook
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of FB1: `docs/handoffs/FB1.md`
6. Handoff of C1: `docs/handoffs/C1.md`
7. Handoff of C11: `docs/handoffs/C11.md`
8. The FB0 probe report `docs/probes/meta.md` and the fixtures in `fixtures/facebook/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)
10. FB0 fixtures
11. C0 adapter pattern
12. C11 handoff (job kinds, series_step)
13. C4 mapper guide

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `source.events`
- Job queues in: `jobs.fb-page-feed-poller`; out: none
- Tables read: `sources`, `clients`, `cursors`, `budgets`; written or updated: `sources`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/fb-page-feed-poller/`
- `docs/handoffs/FB2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/FB2.md` from the fresh-session review
- Facebook mapper in normalize-item
- post_ref format used by FB3, FB4, FB5

## Watch for

- About 600 ranked posts per Page per year on /feed
- Error 80001 means too many calls to this Page
- System-user token per client, injected per job
- The due time is next_due_at in this service's own cursors row, set from the start of the last poll; order by it then tier; most stale first when behind, with rotation_behind (ADR-0015)
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Q1

## How to run it

- Plan: `claude --worktree FB2 --permission-mode plan`, then `/plan-session FB2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session FB2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree FB2`, then `/review-session FB2`
- Fix: `claude --worktree FB2` (or the build terminal), `/fix-session FB2`; then a fresh session runs `/review-session FB2 recheck`; merge when the review has no open blocker or should-fix
