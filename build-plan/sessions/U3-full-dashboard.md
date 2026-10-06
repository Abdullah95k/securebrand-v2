# U3 · Full dashboard

Wave 6 · Insight layer · track Apps · size L (3 to 5 days with review) · kind app

## Builds

The client dashboard over the query API, with analysis views.

## Needs first (merged, with a closed review)

- Q1 Query API v0: `docs/handoffs/Q1.md`
- U2 Client portal: `docs/handoffs/U2.md`
- A1 analysis-sentiment: `docs/handoffs/A1.md`
- A2 analysis-topics: `docs/handoffs/A2.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Retention classes; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of Q1: `docs/handoffs/Q1.md`
5. Handoff of U2: `docs/handoffs/U2.md`
6. Handoff of A1: `docs/handoffs/A1.md`
7. Handoff of A2: `docs/handoffs/A2.md`

## Hands on

- `docs/handoffs/U3.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/U3.md` from the fresh-session review

## Watch for

- Nothing beyond this brief and its PRD.

## Done when

- The definition of done in `build-plan/README.md` holds.
- Screens checked in a browser against the PRD; a test proves a user never sees another client's data.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree U3 --permission-mode plan`, then `/plan-session U3`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session U3` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree U3`, then `/review-session U3`
- Fix: `claude --worktree U3` (or the build terminal), `/fix-session U3`; then a fresh session runs `/review-session U3 recheck`; merge when the review has no open blocker or should-fix
