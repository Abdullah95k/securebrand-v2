# C1 · quota-governor

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

Allowance API, budgets and reservations, priorities 1 to 5, modes normal, stretch and exhausted.

Service `quota-governor` · PRD `docs/prds/shared/quota-governor.md` · lane Support · route shared · 12 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- F5 SDK scheduling, quota client, adapter kit, fake platform: `docs/handoffs/F5.md`
- G0 Gate: foundation: `docs/gates/G0.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/quota-governor.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes; Quotas, budgets and the quota governor
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of F5: `docs/handoffs/F5.md`
6. ADR on priorities and modes (decision 2)
7. Canonical budget tags (CONVENTIONS addendum)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: none named in 6.2
- Job queue: `jobs.quota-governor` if the PRD's section 5.1 schedules jobs
- Tables read: `clients`, `client_sources`, `budgets`, `vendor_keys`, `x_read_ledger`, `ig_hashtag_ledger`, `budget_reservations`, `budget_history`; written or updated: `budgets`, `x_read_ledger`, `ig_hashtag_ledger`, `budget_reservations`, `budget_history`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/quota-governor/`
- `docs/handoffs/C1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C1.md` from the fresh-session review
- budget seed configuration per tag

## Watch for

- The +24 h comment step is held, never cancelled
- Amber intervals stretch but never beyond 24 h
- The X and Instagram ledgers' rules land with X1 and IG2; this session builds the generic ledger support
- Deletion and retention actions are audited before they run, so a replay changes nothing

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C0, C2, C3, C7

## How to run it

- Plan: `claude --worktree C1 --permission-mode plan`, then `/plan-session C1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C1`, then `/review-session C1`
- Fix: `claude --worktree C1` (or the build terminal), `/fix-session C1`; then a fresh session runs `/review-session C1 recheck`; merge when the review has no open blocker or should-fix
