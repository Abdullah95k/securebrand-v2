# F2 · Contracts package

Wave 1 · Foundation · track Foundation · size L (3 to 5 days with review) · kind foundation · on the critical path

## Builds

Zod schemas for every topic, job and envelope; JSON Schema export; Pydantic models for Python; valid and invalid fixtures; idempotency key and item_id derivation with golden vectors; TypeScript and Python conformance tests.

## Needs first (merged, with a closed review)

- D2 Decisions and contract freeze: `docs/handoffs/D2.md`
- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: the whole file
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of D2: `docs/handoffs/D2.md`
5. Handoff of F1: `docs/handoffs/F1.md`
6. `docs/contracts/INVENTORY.md`
7. Every PRD's section 6.2 example message

## Hands on

- `docs/handoffs/F2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/F2.md` from the fresh-session review
- `packages/contracts` v1.0.0
- `fixtures/contracts/` with valid and invalid examples for every topic
- `docs/contracts/VERSIONING.md` (additive within a version; breaking change = new version with a dual-publish window)

## Watch for

- When PRD examples disagree on a field, the ADR decides, never a majority of examples
- Keys must be byte-identical in TypeScript and Python: fix Unicode normalisation and JSON canonicalisation in the golden vectors
- Every data payload carries provenance (route, vendor, service, fetched_at) and retention_class; jobs, `jobs.completed` and `source.events` carry `producer` (ADR-0003)
- Start this session with ALLOW_CONTRACT_EDITS=1: it is one of the few allowed to write the contract paths

## Done when

- The definition of done in `build-plan/README.md` holds.
- The package README shows a service using it, with a runnable example.
- Conformance or golden tests named in this brief pass in every language involved.

## Runs alongside

F3, F7

## How to run it

- Plan: `ALLOW_CONTRACT_EDITS=1 claude --worktree F2 --permission-mode plan`, then `/plan-session F2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session F2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree F2`, then `/review-session F2`
- Fix: `ALLOW_CONTRACT_EDITS=1 claude --worktree F2` (or the build terminal), `/fix-session F2`; then a fresh session runs `/review-session F2 recheck`; merge when the review has no open blocker or should-fix
