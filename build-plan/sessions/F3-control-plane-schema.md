# F3 · Control-plane schema

Wave 1 · Foundation · track Foundation · size L (3 to 5 days with review) · kind foundation · on the critical path

## Builds

Supabase migrations for every control-plane table, indexes, row-level security, the column ownership map, generated types and seed data.

## Needs first (merged, with a closed review)

- D2 Decisions and contract freeze: `docs/handoffs/D2.md`
- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: the whole file
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of D2: `docs/handoffs/D2.md`
5. Handoff of F1: `docs/handoffs/F1.md`
6. `docs/contracts/INVENTORY.md` (tables)
7. CONVENTIONS registry, cursors and qualifier sections

## Hands on

- `docs/handoffs/F3.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/F3.md` from the fresh-session review
- `supabase/migrations` v1
- `docs/contracts/TABLE-OWNERS.md` (which service writes which column)
- generated TypeScript types
- seed scripts for tests and staging

## Watch for

- Client users see only their clients' rows; services use the service role
- Advisory-lock keys for leader election must be unique per service
- Seed the comment series profiles and budget tags from the conventions tables, not by hand
- Start this session with ALLOW_CONTRACT_EDITS=1: it is one of the few allowed to write the contract paths

## Done when

- The definition of done in `build-plan/README.md` holds.
- The package README shows a service using it, with a runnable example.
- Conformance or golden tests named in this brief pass in every language involved.

## Runs alongside

F2, F7, F8

## How to run it

- Plan: `ALLOW_CONTRACT_EDITS=1 claude --worktree F3 --permission-mode plan`, then `/plan-session F3`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session F3` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree F3`, then `/review-session F3`
- Fix: `ALLOW_CONTRACT_EDITS=1 claude --worktree F3` (or the build terminal), `/fix-session F3`; then a fresh session runs `/review-session F3 recheck`; merge when the review has no open blocker or should-fix
