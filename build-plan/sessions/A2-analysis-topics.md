# A2 · analysis-topics

Wave 6 · Insight layer · track Insight · size L (3 to 5 days with review) · kind service

## Builds

Topic classification against the taxonomy.

Service `analysis-topics` · PRD `docs/prds/shared/analysis-topics.md` · lane Processing · route shared · 10 acceptance criteria (section 13) · 7 open questions (section 14)

## Needs first (merged, with a closed review)

- F6 Python SDK twin: `docs/handoffs/F6.md`
- C4 normalize-item (core): `docs/handoffs/C4.md`
- A0 Labelled evaluation set: `docs/handoffs/A0.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/analysis-topics.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of F6: `docs/handoffs/F6.md`
6. Handoff of C4: `docs/handoffs/C4.md`
7. Handoff of A0: `docs/handoffs/A0.md`
8. Taxonomy seed

## Contracts it touches (from PRD section 6)

- Topics read: `items.normalized`, `source.events`
- Topics written: `items.analysis`
- Job queues in: `jobs.analysis-topics`; out: none
- Tables read: `sources`, `client_sources`, `cursors`, `review_queue`, `retention_classes`, `service_runs`, `model_versions`, `taxonomy_nodes`; written or updated: `cursors`, `review_queue`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/analysis-topics/`
- `docs/handoffs/A2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/A2.md` from the fresh-session review

## Watch for

- Stateless where the PRD says so; replay from raw-archiver must reproduce the same output for the same model version

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

A1, A3, A4

## How to run it

- Plan: `claude --worktree A2 --permission-mode plan`, then `/plan-session A2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session A2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree A2`, then `/review-session A2`
- Fix: `claude --worktree A2` (or the build terminal), `/fix-session A2`; then a fresh session runs `/review-session A2 recheck`; merge when the review has no open blocker or should-fix
