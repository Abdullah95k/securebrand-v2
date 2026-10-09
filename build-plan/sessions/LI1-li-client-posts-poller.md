# LI1 · li-client-posts-poller

Wave 5 · Approval-gated platforms and the client portal · track LinkedIn · size M (1 to 2 days with review) · kind service

## Builds

Client page posts on rotation; the LinkedIn mapper.

Service `li-client-posts-poller` · PRD `docs/prds/linkedin/li-client-posts-poller.md` · lane Fetch posts · route green · 10 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- LI0 LinkedIn probe (Development tier): `docs/handoffs/LI0.md`
- U2 Client portal: `docs/handoffs/U2.md`
- C14 retention-purger: `docs/handoffs/C14.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/linkedin/li-client-posts-poller.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: LinkedIn
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of LI0: `docs/handoffs/LI0.md`
6. Handoff of U2: `docs/handoffs/U2.md`
7. Handoff of C14: `docs/handoffs/C14.md`
8. The LI0 probe report `docs/probes/linkedin.md` and the fixtures in `fixtures/linkedin/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `source.events`, `deletions`
- Job queues in: `jobs.li-client-posts-poller`; out: none
- Tables read: `sources`, `clients`, `client_sources`, `cursors`, `budgets`; written or updated: `sources`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/li-client-posts-poller/`
- `docs/handoffs/LI1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/LI1.md` from the fresh-session review
- LinkedIn mapper in normalize-item

## Watch for

- Member data purged after 48 hours; nothing exported to clients
- The due time is next_due_at in this service's own cursors row, set from the start of the last poll; order by it then tier; most stale first when behind, with rotation_behind (ADR-0015)
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree LI1 --permission-mode plan`, then `/plan-session LI1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session LI1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree LI1`, then `/review-session LI1`
- Fix: `claude --worktree LI1` (or the build terminal), `/fix-session LI1`; then a fresh session runs `/review-session LI1 recheck`; merge when the review has no open blocker or should-fix
