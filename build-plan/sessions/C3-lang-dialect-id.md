# C3 · lang-dialect-id

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

POST /v1/detect and /v1/fold: language ID, dialect scores, Arabic and Sorani folds, model versions.

Service `lang-dialect-id` · PRD `docs/prds/shared/lang-dialect-id.md` · lane Processing · route shared · 12 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- F6 Python SDK twin: `docs/handoffs/F6.md`
- F7 Text fold and golden corpus: `docs/handoffs/F7.md`
- G0 Gate: foundation: `docs/gates/G0.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/lang-dialect-id.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of F6: `docs/handoffs/F6.md`
6. Handoff of F7: `docs/handoffs/F7.md`
7. F7 golden corpus
8. Pinned model bundle (fastText lid.176, CAMeL Tools, KLPT)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `items.normalized`
- Job queue: `jobs.lang-dialect-id` if the PRD's section 5.1 schedules jobs
- Tables read: `service_runs`; written or updated: `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/lang-dialect-id/`
- `docs/handoffs/C3.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C3.md` from the fresh-session review
- service passing the fold conformance suite
- lang_model_version scheme

## Watch for

- Detect on raw text, then fold by language
- dialect describes the text, never the author or the country
- Stateless where the PRD says so; replay from raw-archiver must reproduce the same output for the same model version

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C0, C1, C2, C7

## Your part

A reader of Iraqi Arabic and Sorani checks 50 random outputs.

## How to run it

- Plan: `claude --worktree C3 --permission-mode plan`, then `/plan-session C3`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C3` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C3`, then `/review-session C3`
- Fix: `claude --worktree C3` (or the build terminal), `/fix-session C3`; then a fresh session runs `/review-session C3 recheck`; merge when the review has no open blocker or should-fix
