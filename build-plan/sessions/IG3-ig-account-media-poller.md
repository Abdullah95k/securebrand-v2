# IG3 · ig-account-media-poller

Wave 5 · Approval-gated platforms and the client portal · track Instagram · size L (3 to 5 days with review) · kind service

## Builds

Account media on rotation and metrics; the Instagram mapper.

Service `ig-account-media-poller` · PRD `docs/prds/instagram/ig-account-media-poller.md` · lane Fetch posts · route green · 12 acceptance criteria (section 13) · 3 open questions (section 14)

## Needs first (merged, with a closed review)

- IG1 ig-account-resolver: `docs/handoffs/IG1.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/instagram/ig-account-media-poller.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: Instagram
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of IG1: `docs/handoffs/IG1.md`
6. Handoff of C11: `docs/handoffs/C11.md`
7. The FB0 probe report `docs/probes/meta.md` and the fixtures in `fixtures/instagram/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `source.events`
- Job queues in: `jobs.ig-account-media-poller`; out: none
- Tables read: `sources`, `clients`, `cursors`, `budgets`; written or updated: `sources`, `cursors`, `budgets`, `review_queue`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/ig-account-media-poller/`
- `docs/handoffs/IG3.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/IG3.md` from the fresh-session review
- Instagram mapper in normalize-item

## Watch for

- next_poll_at is set from the start of the last poll; order by next_poll_at then tier; most stale first when behind, with rotation_behind
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

IG2

## How to run it

- Plan: `claude --worktree IG3 --permission-mode plan`, then `/plan-session IG3`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session IG3` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree IG3`, then `/review-session IG3`
- Fix: `claude --worktree IG3` (or the build terminal), `/fix-session IG3`; then a fresh session runs `/review-session IG3 recheck`; merge when the review has no open blocker or should-fix
