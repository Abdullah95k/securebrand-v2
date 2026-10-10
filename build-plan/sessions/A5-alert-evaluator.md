# A5 · alert-evaluator

Wave 6 · Insight layer · track Insight · size M (1 to 2 days with review) · kind service

## Builds

Alert rules over the aggregate views, metrics_timeseries and item_stories, routed through n8n (ADR-0047, ADR-0048).

Service `alert-evaluator` · PRD `docs/prds/shared/alert-evaluator.md` · lane Processing · route shared · 12 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- C15 aggregator: `docs/handoffs/C15.md`
- C5 keyword-matcher: `docs/handoffs/C5.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green
- A1 analysis-sentiment: `docs/handoffs/A1.md`
- A2 analysis-topics: `docs/handoffs/A2.md`
- A3 analysis-entities: `docs/handoffs/A3.md`
- A4 analysis-media: `docs/handoffs/A4.md`

Any-time track: earliest after C15, C5, G1 and A1 to A4 (ADR-0048); deadline none.

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/alert-evaluator.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of C15: `docs/handoffs/C15.md`
6. Handoff of C5: `docs/handoffs/C5.md`
7. Handoff of A1: `docs/handoffs/A1.md`
8. Handoff of A2: `docs/handoffs/A2.md`
9. Handoff of A3: `docs/handoffs/A3.md`
10. Handoff of A4: `docs/handoffs/A4.md`

## Contracts it touches (from PRD section 6)

- Topics read: `item.hits`, `source.events`, `deletions`
- Topics written: none named in 6.2
- Job queue: `jobs.alert-evaluator` if the PRD's section 5.1 schedules jobs
- Tables read: `clients`, `service_runs`; written or updated: `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/alert-evaluator/`
- `docs/handoffs/A5.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/A5.md` from the fresh-session review

## Watch for

- Stateless where the PRD says so; replay from raw-archiver must reproduce the same output for the same model version

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Any session (any-time track)

## How to run it

- Plan: `claude --worktree A5 --permission-mode plan`, then `/plan-session A5`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session A5` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree A5`, then `/review-session A5`
- Fix: `claude --worktree A5` (or the build terminal), `/fix-session A5`; then a fresh session runs `/review-session A5 recheck`; merge when the review has no open blocker or should-fix
