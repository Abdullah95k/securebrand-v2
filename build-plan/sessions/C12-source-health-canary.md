# C12 · source-health-canary

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

Canaries per route, empty-200 rate, health state machine, fallback decisions with government scope.

Service `source-health-canary` · PRD `docs/prds/shared/source-health-canary.md` · lane Support · route shared · 11 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- F5 SDK scheduling, quota client, adapter kit, fake platform: `docs/handoffs/F5.md`
- C7 registry-writer: `docs/handoffs/C7.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/source-health-canary.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes; Quotas, budgets and the quota governor
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of F5: `docs/handoffs/F5.md`
6. Handoff of C7: `docs/handoffs/C7.md`
7. ADR-0021 (fallback scope; it supersedes README decision 5)
8. Canary_targets

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `registry.decisions`, `source.events`
- Job queue: `jobs.source-health-canary` if the PRD's section 5.1 schedules jobs
- Tables read: `sources`, `clients`, `client_sources`, `budgets`, `canary_targets`; written or updated: `canary_targets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/source-health-canary/`
- `docs/handoffs/C12.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C12.md` from the fresh-session review

## Watch for

- Route-wide states come only from the canary; a blocked source falls back to its vendor automatically where that flag is on, with an n8n notice to ops, never an approval card (ADR-0021)
- A green source a government client watches never falls back to amber; a client-owned property falls back under the same conditions as any other source, with the n8n notice to ops (ADR-0021)
- Deletion and retention actions are audited before they run, so a replay changes nothing

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C13, C14, C15

## How to run it

- Plan: `claude --worktree C12 --permission-mode plan`, then `/plan-session C12`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C12` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C12`, then `/review-session C12`
- Fix: `claude --worktree C12` (or the build terminal), `/fix-session C12`; then a fresh session runs `/review-session C12 recheck`; merge when the review has no open blocker or should-fix
