# LI3 · li-notification-receiver

Wave 5 · Approval-gated platforms and the client portal · track LinkedIn · size M (1 to 2 days with review) · kind service

## Builds

Webhook notifications for client pages.

Service `li-notification-receiver` · PRD `docs/prds/linkedin/li-notification-receiver.md` · lane Comments · route green · 12 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- LI1 li-client-posts-poller: `docs/handoffs/LI1.md`
- LI2 li-own-comments-fetcher: `docs/handoffs/LI2.md`
- I1 Infrastructure (staging first): `docs/handoffs/I1.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/linkedin/li-notification-receiver.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; Rotation policy (the comments part); Addendum: Comment series profiles; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: LinkedIn
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of LI1: `docs/handoffs/LI1.md`
6. Handoff of LI2: `docs/handoffs/LI2.md`
7. Handoff of I1: `docs/handoffs/I1.md`
8. The LI0 probe report `docs/probes/linkedin.md` and the fixtures in `fixtures/linkedin/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`, `item.metrics`
- Topics written: `raw.items`, `source.events`, `deletions`
- Job queue: `jobs.li-notification-receiver` if the PRD's section 5.1 schedules jobs
- Tables read: `sources`, `clients`, `budgets`, `service_runs`; written or updated: `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/li-notification-receiver/`
- `docs/handoffs/LI3.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/LI3.md` from the fresh-session review

## Watch for

- Only comment-decay-scheduler emits comment, reply and metrics jobs; this service never schedules its own
- Return new_count, seen_count, pages, cost_units and reply_candidates to the SDK job wrapper, which reports them on jobs.completed; the scheduler decides early stop and extension from them (ADR-0017, ADR-0019)
- Compare with the stored set through the SDK comment-state helper: an edit is a new version where the platform gives comment ids, a new comment otherwise; a missing comment is a deletion (platform_sync) only after a confirmed second miss or a platform signal, never on a route whose reads are not complete listings (ADR-0009, ADR-0046, ADR-0062)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree LI3 --permission-mode plan`, then `/plan-session LI3`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session LI3` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree LI3`, then `/review-session LI3`
- Fix: `claude --worktree LI3` (or the build terminal), `/fix-session LI3`; then a fresh session runs `/review-session LI3 recheck`; merge when the review has no open blocker or should-fix
