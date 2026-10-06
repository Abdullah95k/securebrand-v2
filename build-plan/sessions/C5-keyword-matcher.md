# C5 · keyword-matcher

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

Keyword compile through /v1/fold, matching on text_norm, item.hits versus discovery.hits by registry membership.

Service `keyword-matcher` · PRD `docs/prds/shared/keyword-matcher.md` · lane Processing · route shared · 12 acceptance criteria (section 13) · 6 open questions (section 14)

## Needs first (merged, with a closed review)

- F4 SDK runtime (Node): `docs/handoffs/F4.md`
- F7 Text fold and golden corpus: `docs/handoffs/F7.md`
- F8 ClickHouse schema: `docs/handoffs/F8.md`
- G0 Gate: foundation: `docs/gates/G0.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/keyword-matcher.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of F4: `docs/handoffs/F4.md`
6. Handoff of F7: `docs/handoffs/F7.md`
7. Handoff of F8: `docs/handoffs/F8.md`
8. C3 /v1/fold contract
9. Keywords table (F3)

## Contracts it touches (from PRD section 6)

- Topics read: `items.normalized`, `source.events`
- Topics written: `item.hits`, `discovery.hits`
- Job queues in: `jobs.keyword-matcher`; out: `jobs.keyword-matcher`
- Tables read: `sources`, `keywords`, `clients`, `cursors`, `service_runs`; written or updated: `sources`, `cursors`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/keyword-matcher/`
- `docs/handoffs/C5.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C5.md` from the fresh-session review

## Watch for

- keyword-matcher is the canonical writer of item.hits and discovery.hits for items (search output rule)
- Stateless where the PRD says so; replay from raw-archiver must reproduce the same output for the same model version

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C4, C6

## How to run it

- Plan: `claude --worktree C5 --permission-mode plan`, then `/plan-session C5`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C5` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C5`, then `/review-session C5`
- Fix: `claude --worktree C5` (or the build terminal), `/fix-session C5`; then a fresh session runs `/review-session C5 recheck`; merge when the review has no open blocker or should-fix
