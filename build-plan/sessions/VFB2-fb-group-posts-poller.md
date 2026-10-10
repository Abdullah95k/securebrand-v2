# VFB2 · fb-group-posts-poller

Wave 7 · Amber vendor routes (optional) · track Amber · size M (1 to 2 days with review) · kind service

## Builds

Vendor-sourced group posts on rotation.

Service `fb-group-posts-poller` · PRD `docs/prds/facebook/fb-group-posts-poller.md` · lane Fetch posts · route amber · 11 acceptance criteria (section 13) · 6 open questions (section 14)

## Needs first (merged, with a closed review)

- VFB0 Facebook vendor probe: `docs/handoffs/VFB0.md`
- C10 backfill-orchestrator: `docs/handoffs/C10.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/facebook/fb-group-posts-poller.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: Facebook
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of VFB0: `docs/handoffs/VFB0.md`
6. Handoff of C10: `docs/handoffs/C10.md`
7. Handoff of C11: `docs/handoffs/C11.md`
8. The VFB0 probe report `docs/probes/fb-vendor.md` and the fixtures in `fixtures/facebook-vendor/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `source.events`
- Job queues in: `jobs.fb-group-posts-poller`; out: none
- Tables read: `sources`, `clients`, `cursors`, `budgets`, `credentials` (the PRD's `vendor_keys`, read and written only through the SDK's credential client, ADR-0016); written or updated: `sources`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/fb-group-posts-poller/`
- `docs/handoffs/VFB2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/VFB2.md` from the fresh-session review

## Watch for

- The due time is next_due_at in this service's own cursors row, set from the start of the last poll; order by it then tier; most stale first when behind, with rotation_behind (ADR-0015)
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch
- Amber: runs only behind its flag (off by default); provenance says route = amber and names the vendor; only clients that accept amber receive its data, never government clients (ADR-0052), and a green source a government client watches never falls back to it, while a client-owned property falls back under the same conditions as any other source (ADR-0021); from 80% of budget the SDK scheduling kit stretches its intervals by the governor's factor (ADR-0057)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree VFB2 --permission-mode plan`, then `/plan-session VFB2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session VFB2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree VFB2`, then `/review-session VFB2`
- Fix: `claude --worktree VFB2` (or the build terminal), `/fix-session VFB2`; then a fresh session runs `/review-session VFB2 recheck`; merge when the review has no open blocker or should-fix
