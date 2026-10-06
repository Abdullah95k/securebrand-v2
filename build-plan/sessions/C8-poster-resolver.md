# C8 · poster-resolver

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

Candidate dedup by candidate_key, dispatch to the platform resolver, poster.profiles.

Service `poster-resolver` · PRD `docs/prds/shared/poster-resolver.md` · lane Registry · route shared · 10 acceptance criteria (section 13) · 0 open questions (section 14)

## Needs first (merged, with a closed review)

- F5 SDK scheduling, quota client, adapter kit, fake platform: `docs/handoffs/F5.md`
- C0 Reference vertical on the fake platform: `docs/handoffs/C0.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/poster-resolver.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Qualifier rules; Quotas, budgets and the quota governor
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of F5: `docs/handoffs/F5.md`
6. Handoff of C0: `docs/handoffs/C0.md`
7. C0 ref-resolver (stands in for platform resolvers)

## Contracts it touches (from PRD section 6)

- Topics read: `discovery.hits`
- Topics written: `raw.items`, `poster.profiles`
- Job queues in: `jobs.poster-resolver`; out: none
- Tables read: `sources`, `keywords`, `clients`, `cursors`, `decisions`, `service_runs`; written or updated: `keywords`, `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/poster-resolver/`
- `docs/handoffs/C8.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C8.md` from the fresh-session review

## Watch for

- Candidates arrive from discovery.hits and from searches that emit directly: dedup by candidate_key
- Individuals are never profiled
- registry-writer is the only writer of the sources table and of source.events (per D2)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C9, C10, C11

## How to run it

- Plan: `claude --worktree C8 --permission-mode plan`, then `/plan-session C8`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C8` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C8`, then `/review-session C8`
- Fix: `claude --worktree C8` (or the build terminal), `/fix-session C8`; then a fresh session runs `/review-session C8 recheck`; merge when the review has no open blocker or should-fix
