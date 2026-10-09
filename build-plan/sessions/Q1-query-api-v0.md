# Q1 · Query API v0

Wave 3 · First real data, and the Meta review build · track Apps · size M (1 to 2 days with review) · kind app · on the critical path

## Builds

Read endpoints over ClickHouse with client scoping through Supabase Auth.

## Needs first (merged, with a closed review)

- D3 Specs for the parts with no PRD: `docs/handoffs/D3.md`
- C6 store-writer: `docs/handoffs/C6.md`
- C15 aggregator: `docs/handoffs/C15.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Retention classes; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of D3: `docs/handoffs/D3.md`
5. Handoff of C6: `docs/handoffs/C6.md`
6. Handoff of C15: `docs/handoffs/C15.md`
7. Query-api PRD (D3)
8. F8 schema

## Hands on

- `docs/handoffs/Q1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/Q1.md` from the fresh-session review

## Watch for

- Nothing beyond this brief and its PRD.

## Done when

- The definition of done in `build-plan/README.md` holds.
- Screens checked in a browser against the PRD; a test proves a user never sees another client's data.

## Runs alongside

FB2

## How to run it

- Plan: `claude --worktree Q1 --permission-mode plan`, then `/plan-session Q1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session Q1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree Q1`, then `/review-session Q1`
- Fix: `claude --worktree Q1` (or the build terminal), `/fix-session Q1`; then a fresh session runs `/review-session Q1 recheck`; merge when the review has no open blocker or should-fix
