# A1 · analysis-sentiment

Wave 6 · Insight layer · track Insight · size L (3 to 5 days with review) · kind service

## Builds

Two-lane sentiment scoring into items.analysis.

Service `analysis-sentiment` · PRD `docs/prds/shared/analysis-sentiment.md` · lane Processing · route shared · 11 acceptance criteria (section 13) · 7 open questions (section 14)

## Needs first (merged, with a closed review)

- F6 Python SDK twin: `docs/handoffs/F6.md`
- C4 normalize-item (core): `docs/handoffs/C4.md`
- A0 Labelled evaluation set: `docs/handoffs/A0.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/analysis-sentiment.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of F6: `docs/handoffs/F6.md`
6. Handoff of C4: `docs/handoffs/C4.md`
7. Handoff of A0: `docs/handoffs/A0.md`
8. ADR on GPU pool or model API
9. ADR on analysis lanes and items.analysis/v1 (decision 7)

## Contracts it touches (from PRD section 6)

- Topics read: `items.normalized`, `item.hits`, `discovery.hits`, `source.events`
- Topics written: `items.analysis`
- Job queues in: `jobs.analysis-sentiment`; out: none
- Tables read: `sources`, `cursors`, `review_queue`, `retention_classes`, `service_runs`, `model_versions`; written or updated: `cursors`, `review_queue`, `service_runs`, `model_versions`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/analysis-sentiment/`
- `docs/handoffs/A1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/A1.md` from the fresh-session review

## Watch for

- Stateless where the PRD says so; replay from raw-archiver must reproduce the same output for the same model version

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

A2, A3, A4

## How to run it

- Plan: `claude --worktree A1 --permission-mode plan`, then `/plan-session A1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session A1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree A1`, then `/review-session A1`
- Fix: `claude --worktree A1` (or the build terminal), `/fix-session A1`; then a fresh session runs `/review-session A1 recheck`; merge when the review has no open blocker or should-fix
