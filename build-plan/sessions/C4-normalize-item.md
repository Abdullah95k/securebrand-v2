# C4 · normalize-item (core)

Wave 2 · Shared core · track Core · size L (3 to 5 days with review) · kind service · on the critical path

## Builds

Mapper registry, one schema for every platform, the lang call with fallback, dedup, edits and versions, parking of unknown shapes.

Service `normalize-item` · PRD `docs/prds/shared/normalize-item.md` · lane Processing · route shared · 11 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- F4 SDK runtime (Node): `docs/handoffs/F4.md`
- F7 Text fold and golden corpus: `docs/handoffs/F7.md`
- C2 raw-archiver: `docs/handoffs/C2.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/normalize-item.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of F4: `docs/handoffs/F4.md`
6. Handoff of F7: `docs/handoffs/F7.md`
7. Handoff of C2: `docs/handoffs/C2.md`
8. C3 API contract (stub it until C3 merges)
9. C0 record shapes

## Contracts it touches (from PRD section 6)

- Topics read: `raw.items`, `source.events`
- Topics written: `items.normalized`, `item.metrics`
- Job queues in: `jobs.normalize-item`; out: none
- Tables read: `sources`, `cursors`, `review_queue`, `retention_classes`, `service_runs`; written or updated: `cursors`, `review_queue`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/normalize-item/`
- `docs/handoffs/C4.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C4.md` from the fresh-session review
- items.normalized
- `docs/patterns/MAPPERS.md:` how each platform session adds its mapper

## Watch for

- Only the fake platform's mapper here; each platform session adds its own
- When lang-dialect-id is down: lang = und with the TypeScript fold and lang_pending
- Unknown shapes are archived and parked as schema_unknown, never dropped
- Where mappers live: ADR-0008 puts the registry keyed (service, api_version) in listening-sdk, the kit puts mappers under services/normalize-item/src/mappers/<platform>/; MAPPERS.md names the one place, decided from F4's handoff, before wave 3 (DEFERRED.md section 3)
- Stateless where the PRD says so; replay from raw-archiver must reproduce the same output for the same model version

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C5, C6

## How to run it

- Plan: `claude --worktree C4 --permission-mode plan`, then `/plan-session C4`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C4` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C4`, then `/review-session C4`
- Fix: `claude --worktree C4` (or the build terminal), `/fix-session C4`; then a fresh session runs `/review-session C4 recheck`; merge when the review has no open blocker or should-fix
