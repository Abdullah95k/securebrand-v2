# C14 · retention-purger

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

Time-based purges per retention class, client offboarding, retention audit.

Service `retention-purger` · PRD `docs/prds/shared/retention-purger.md` · lane Support · route shared · 10 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- C13 deletion-propagator: `docs/handoffs/C13.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/retention-purger.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes; Quotas, budgets and the quota governor
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of C13: `docs/handoffs/C13.md`
6. Retention classes (CONVENTIONS)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`, `deletions`
- Topics written: `registry.decisions`, `deletions`
- Job queues in: its own `jobs.retention-purger`; out: `jobs.yt-text-purger`
- Tables read: `sources`, `clients`, `client_sources`, `cursors`, `deletion_requests`, `retention_classes`, `vendor_keys`; written or updated: `cursors`, `deletion_requests`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/retention-purger/`
- `docs/handoffs/C14.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C14.md` from the fresh-session review

## Watch for

- linkedin_48h, youtube_30d_text, news_excerpt and x_24h_sync each work differently
- Purge raw text, never aggregates and derived scores
- Deletion and retention actions are audited before they run, so a replay changes nothing

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C12, C15

## How to run it

- Plan: `claude --worktree C14 --permission-mode plan`, then `/plan-session C14`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C14` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C14`, then `/review-session C14`
- Fix: `claude --worktree C14` (or the build terminal), `/fix-session C14`; then a fresh session runs `/review-session C14 recheck`; merge when the review has no open blocker or should-fix
