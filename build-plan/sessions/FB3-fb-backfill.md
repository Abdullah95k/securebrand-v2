# FB3 · fb-backfill

Wave 4 · YouTube, X, and Facebook in development mode · track Facebook · size M (1 to 2 days with review) · kind service

## Builds

90-day backfill with cursor hand-over to the poller.

Service `fb-backfill` · PRD `docs/prds/facebook/fb-backfill.md` · lane Fetch posts · route green · 9 acceptance criteria (section 13) · 3 open questions (section 14)

## Needs first (merged, with a closed review)

- FB2 fb-page-feed-poller: `docs/handoffs/FB2.md`
- C10 backfill-orchestrator: `docs/handoffs/C10.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/facebook/fb-backfill.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: Facebook
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of FB2: `docs/handoffs/FB2.md`
6. Handoff of C10: `docs/handoffs/C10.md`
7. The FB0 probe report `docs/probes/meta.md` and the fixtures in `fixtures/facebook/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`, `source.events`
- Job queues in: `jobs.fb-backfill`; out: none
- Tables read: `sources`, `clients`, `cursors`, `budgets`; written or updated: `sources`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/fb-backfill/`
- `docs/handoffs/FB3.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/FB3.md` from the fresh-session review

## Watch for

- next_poll_at is set from the start of the last poll; order by next_poll_at then tier; most stale first when behind, with rotation_behind
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

FB4, FB5, FB6

## How to run it

- Plan: `claude --worktree FB3 --permission-mode plan`, then `/plan-session FB3`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session FB3` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree FB3`, then `/review-session FB3`
- Fix: `claude --worktree FB3` (or the build terminal), `/fix-session FB3`; then a fresh session runs `/review-session FB3 recheck`; merge when the review has no open blocker or should-fix
