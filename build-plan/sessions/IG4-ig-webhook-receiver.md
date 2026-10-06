# IG4 · ig-webhook-receiver

Wave 5 · Approval-gated platforms and the client portal · track Instagram · size M (1 to 2 days with review) · kind service

## Builds

Webhooks for client accounts.

Service `ig-webhook-receiver` · PRD `docs/prds/instagram/ig-webhook-receiver.md` · lane Fetch posts · route green · 12 acceptance criteria (section 13) · 3 open questions (section 14)

## Needs first (merged, with a closed review)

- IG3 ig-account-media-poller: `docs/handoffs/IG3.md`
- U2 Client portal: `docs/handoffs/U2.md`
- I1 Infrastructure (staging first): `docs/handoffs/I1.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/instagram/ig-webhook-receiver.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: Instagram
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of IG3: `docs/handoffs/IG3.md`
6. Handoff of U2: `docs/handoffs/U2.md`
7. Handoff of I1: `docs/handoffs/I1.md`
8. The FB0 probe report `docs/probes/meta.md` and the fixtures in `fixtures/instagram/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`, `source.events`
- Job queues in: `jobs.ig-webhook-receiver`; out: `jobs.ig-mentions-fetcher`, `jobs.ig-own-comments-fetcher`
- Tables read: `sources`, `clients`, `cursors`; written or updated: `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/ig-webhook-receiver/`
- `docs/handoffs/IG4.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/IG4.md` from the fresh-session review

## Watch for

- next_poll_at is set from the start of the last poll; order by next_poll_at then tier; most stale first when behind, with rotation_behind
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree IG4 --permission-mode plan`, then `/plan-session IG4`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session IG4` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree IG4`, then `/review-session IG4`
- Fix: `claude --worktree IG4` (or the build terminal), `/fix-session IG4`; then a fresh session runs `/review-session IG4 recheck`; merge when the review has no open blocker or should-fix
