# VIG2 · ig-comments-fetcher

Wave 7 · Amber vendor routes (optional) · track Amber · size M (1 to 2 days with review) · kind service

## Builds

Vendor comments on non-client media.

Service `ig-comments-fetcher` · PRD `docs/prds/instagram/ig-comments-fetcher.md` · lane Comments · route amber · 12 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- VIG0 Instagram vendor probe: `docs/handoffs/VIG0.md`
- IG3 ig-account-media-poller: `docs/handoffs/IG3.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/instagram/ig-comments-fetcher.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; Rotation policy (the comments part); Addendum: Comment series profiles; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: Instagram
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of VIG0: `docs/handoffs/VIG0.md`
6. Handoff of IG3: `docs/handoffs/IG3.md`
7. Handoff of C11: `docs/handoffs/C11.md`
8. The VIG0 probe report `docs/probes/ig-vendor.md` and the fixtures in `fixtures/instagram-vendor/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`
- Job queues in: `jobs.ig-comments-fetcher`; out: none
- Tables read: `sources`, `clients`, `cursors`, `budgets`, `vendor_keys`; written or updated: `clients`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/ig-comments-fetcher/`
- `docs/handoffs/VIG2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/VIG2.md` from the fresh-session review

## Watch for

- Only comment-decay-scheduler emits comment, reply and metrics jobs; this service never schedules its own
- Report new_count, seen_count, pages and cost_units on every job: the scheduler decides early stop and extension from them
- Edits become new versions; deletions only when the API response is complete (reason platform_sync)
- Amber: runs only behind its flag (off by default); provenance says route = amber and names the vendor; its data is excluded from government contracts, and a source a government client watches never falls back to it; the quota governor stretches it from 80% of budget

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree VIG2 --permission-mode plan`, then `/plan-session VIG2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session VIG2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree VIG2`, then `/review-session VIG2`
- Fix: `claude --worktree VIG2` (or the build terminal), `/fix-session VIG2`; then a fresh session runs `/review-session VIG2 recheck`; merge when the review has no open blocker or should-fix
