# U1 · Dashboard slice for Meta App Review

Wave 3 · First real data, and the Meta review build · track Apps · size M (1 to 2 days with review) · kind app · on the critical path

## Builds

Screens comparing named Pages, engagement over time and post lists; the screencast script.

## Needs first (merged, with a closed review)

- Q1 Query API v0: `docs/handoffs/Q1.md`
- FB2 fb-page-feed-poller: `docs/handoffs/FB2.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Retention classes; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of Q1: `docs/handoffs/Q1.md`
5. Handoff of FB2: `docs/handoffs/FB2.md`
6. Dashboard PRD (D3)
7. Meta review requirements (the approvals table in `build-plan/README.md`)

## Hands on

- `docs/handoffs/U1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/U1.md` from the fresh-session review
- the analytics screens Meta must see
- `docs/approvals/meta-screencast.md`

## Watch for

- Nothing beyond this brief and its PRD.

## Done when

- The definition of done in `build-plan/README.md` holds.
- Screens checked in a browser against the PRD; a test proves a user never sees another client's data.

## Runs alongside

Nothing in particular; see the wave table

## Your part

You record the screencast and submit App Review the day this merges.

## How to run it

- Plan: `claude --worktree U1 --permission-mode plan`, then `/plan-session U1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session U1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree U1`, then `/review-session U1`
- Fix: `claude --worktree U1` (or the build terminal), `/fix-session U1`; then a fresh session runs `/review-session U1 recheck`; merge when the review has no open blocker or should-fix
