# VLI3 · li-company-posts-poller

Wave 7 · Amber vendor routes (optional) · track Amber · size M (1 to 2 days with review) · kind service

## Builds

Company page posts on rotation.

Service `li-company-posts-poller` · PRD `docs/prds/linkedin/li-company-posts-poller.md` · lane Fetch posts · route amber · 10 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- VLI2 li-org-resolver: `docs/handoffs/VLI2.md`
- C10 backfill-orchestrator: `docs/handoffs/C10.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`
- C14 retention-purger: `docs/handoffs/C14.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/linkedin/li-company-posts-poller.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: LinkedIn
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of VLI2: `docs/handoffs/VLI2.md`
6. Handoff of C10: `docs/handoffs/C10.md`
7. Handoff of C11: `docs/handoffs/C11.md`
8. Handoff of C14: `docs/handoffs/C14.md`
9. The VLI0 probe report `docs/probes/li-vendor.md` and the fixtures in `fixtures/linkedin-vendor/`
10. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `source.events`
- Job queues in: `jobs.li-company-posts-poller`; out: none
- Tables read: `sources`, `clients`, `client_sources`, `cursors`, `budgets`, `vendor_keys`; written or updated: `sources`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/li-company-posts-poller/`
- `docs/handoffs/VLI3.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/VLI3.md` from the fresh-session review

## Watch for

- The due time is next_due_at in this service's own cursors row, set from the start of the last poll; order by it then tier; most stale first when behind, with rotation_behind (ADR-0015)
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch
- Amber: runs only behind its flag (off by default); provenance says route = amber and names the vendor; only clients that accept amber receive its data, never government clients (ADR-0052), and a source a government client watches or a client-owned property never falls back to it (ADR-0021); from 80% of budget the SDK scheduling kit stretches its intervals by the governor's factor (ADR-0057)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree VLI3 --permission-mode plan`, then `/plan-session VLI3`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session VLI3` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree VLI3`, then `/review-session VLI3`
- Fix: `claude --worktree VLI3` (or the build terminal), `/fix-session VLI3`; then a fresh session runs `/review-session VLI3 recheck`; merge when the review has no open blocker or should-fix
