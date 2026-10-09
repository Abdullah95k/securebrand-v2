# IG5 · ig-mentions-fetcher

Wave 5 · Approval-gated platforms and the client portal · track Instagram · size M (1 to 2 days with review) · kind service

## Builds

Mentions of client accounts.

Service `ig-mentions-fetcher` · PRD `docs/prds/instagram/ig-mentions-fetcher.md` · lane Fetch posts · route green · 12 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- IG4 ig-webhook-receiver: `docs/handoffs/IG4.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/instagram/ig-mentions-fetcher.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: Instagram
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of IG4: `docs/handoffs/IG4.md`
6. The FB0 probe report `docs/probes/meta.md` and the fixtures in `fixtures/instagram/`
7. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`
- Job queues in: `jobs.ig-mentions-fetcher`; out: none
- Tables read: `sources`, `clients`, `cursors`, `budgets`; written or updated: `sources`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/ig-mentions-fetcher/`
- `docs/handoffs/IG5.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/IG5.md` from the fresh-session review

## Watch for

- The due time is next_due_at in this service's own cursors row, set from the start of the last poll; order by it then tier; most stale first when behind, with rotation_behind (ADR-0015)
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

IG6

## How to run it

- Plan: `claude --worktree IG5 --permission-mode plan`, then `/plan-session IG5`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session IG5` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree IG5`, then `/review-session IG5`
- Fix: `claude --worktree IG5` (or the build terminal), `/fix-session IG5`; then a fresh session runs `/review-session IG5 recheck`; merge when the review has no open blocker or should-fix
