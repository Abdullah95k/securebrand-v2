# A0 · Labelled evaluation set

Wave 6 · Insight layer · track Insight · size M (1 to 2 days with review) · kind data

## Builds

Annotation guide (interviewing you), sampling and export scripts, agreement computation, frozen splits and the evaluation harness; annotators then label 2,000 or more Iraqi items outside Claude Code.

## Needs first (merged, with a closed review)

- D2 Decisions and contract freeze: `docs/handoffs/D2.md`

Any-time track: earliest after D2 (real samples after G2); deadline before A1.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of D2: `docs/handoffs/D2.md`
5. Samples exported from staging (after G2)
6. The analysis PRDs' label sets

## Hands on

- `docs/handoffs/A0.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/A0.md` from the fresh-session review
- `docs/analysis/ANNOTATION-GUIDE.md`
- `tools/eval/` (sampling, export, agreement, split freezing, evaluation harness) with tests
- `fixtures/eval/` with train, dev and test splits once labelling is done

## Watch for

- Nothing beyond this brief and its PRD.

## Done when

- Code done (merge): the guide is versioned; the sampling, export, agreement and evaluation tools are merged with tests.
- Data done (before A1): at least 2,000 items labelled, agreement measured and reported, splits frozen and versioned.

## Runs alongside

Any session (any-time track)

## Your part

Annotators who read Iraqi Arabic, Sorani and Badini.

## How to run it

- Plan: `claude --worktree A0 --permission-mode plan`, then `/plan-session A0`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session A0` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree A0`, then `/review-session A0`
- Fix: `claude --worktree A0` (or the build terminal), `/fix-session A0`; then a fresh session runs `/review-session A0 recheck`; merge when the review has no open blocker or should-fix
