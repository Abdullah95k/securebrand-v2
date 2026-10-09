# TT1 · tt-client-videos-fetcher

Wave 5 · Approval-gated platforms and the client portal · track TikTok · size M (1 to 2 days with review) · kind service

## Builds

Client-authorised accounts' videos and metrics; the TikTok mapper.

Service `tt-client-videos-fetcher` · PRD `docs/prds/tiktok/tt-client-videos-fetcher.md` · lane Fetch posts · route green · 11 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- TT0 TikTok Display probe (sandbox): `docs/handoffs/TT0.md`
- U2 Client portal: `docs/handoffs/U2.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/tiktok/tt-client-videos-fetcher.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: TikTok
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of TT0: `docs/handoffs/TT0.md`
6. Handoff of U2: `docs/handoffs/U2.md`
7. The TT0 probe report `docs/probes/tiktok.md` and the fixtures in `fixtures/tiktok/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `source.events`, `item.metrics`
- Job queues in: `jobs.tt-client-videos-fetcher`; out: none
- Tables read: `sources`, `clients`, `cursors`, `budgets`; written or updated: `sources`, `cursors`, `budgets`, `retention_classes`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/tt-client-videos-fetcher/`
- `docs/handoffs/TT1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/TT1.md` from the fresh-session review
- TikTok mapper in normalize-item

## Watch for

- The due time is next_due_at in this service's own cursors row, set from the start of the last poll; order by it then tier; most stale first when behind, with rotation_behind (ADR-0015)
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree TT1 --permission-mode plan`, then `/plan-session TT1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session TT1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree TT1`, then `/review-session TT1`
- Fix: `claude --worktree TT1` (or the build terminal), `/fix-session TT1`; then a fresh session runs `/review-session TT1 recheck`; merge when the review has no open blocker or should-fix
