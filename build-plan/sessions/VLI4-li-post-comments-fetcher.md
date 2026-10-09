# VLI4 · li-post-comments-fetcher

Wave 7 · Amber vendor routes (optional) · track Amber · size M (1 to 2 days with review) · kind service

## Builds

Vendor comments on company posts.

Service `li-post-comments-fetcher` · PRD `docs/prds/linkedin/li-post-comments-fetcher.md` · lane Comments · route amber · 12 acceptance criteria (section 13) · 6 open questions (section 14)

## Needs first (merged, with a closed review)

- VLI3 li-company-posts-poller: `docs/handoffs/VLI3.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/linkedin/li-post-comments-fetcher.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; Rotation policy (the comments part); Addendum: Comment series profiles; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: LinkedIn
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of VLI3: `docs/handoffs/VLI3.md`
6. Handoff of C11: `docs/handoffs/C11.md`
7. The VLI0 probe report `docs/probes/li-vendor.md` and the fixtures in `fixtures/linkedin-vendor/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`, `deletions`
- Job queues in: `jobs.li-post-comments-fetcher`; out: none
- Tables read: `sources`, `clients`, `client_sources`, `cursors`, `budgets`, `vendor_keys`; written or updated: `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/li-post-comments-fetcher/`
- `docs/handoffs/VLI4.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/VLI4.md` from the fresh-session review

## Watch for

- Only comment-decay-scheduler emits comment, reply and metrics jobs; this service never schedules its own
- Return new_count, seen_count, pages, cost_units and reply_candidates to the SDK job wrapper, which reports them on jobs.completed; the scheduler decides early stop and extension from them (ADR-0017, ADR-0019)
- Compare with the stored set through the SDK comment-state helper: an edit is a new version where the platform gives comment ids, a new comment otherwise; a missing comment is a deletion (platform_sync) only after a confirmed second miss or a platform signal, never on a route whose reads are not complete listings (ADR-0009, ADR-0046, ADR-0062)
- Amber: runs only behind its flag (off by default); provenance says route = amber and names the vendor; only clients that accept amber receive its data, never government clients (ADR-0052), and a source a government client watches or a client-owned property never falls back to it (ADR-0021); from 80% of budget the SDK scheduling kit stretches its intervals by the governor's factor (ADR-0057)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree VLI4 --permission-mode plan`, then `/plan-session VLI4`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session VLI4` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree VLI4`, then `/review-session VLI4`
- Fix: `claude --worktree VLI4` (or the build terminal), `/fix-session VLI4`; then a fresh session runs `/review-session VLI4 recheck`; merge when the review has no open blocker or should-fix
