# U2 · Client portal

Wave 5 · Approval-gated platforms and the client portal · track Apps · size L (3 to 5 days with review) · kind app · on the critical path

## Builds

Onboarding, OAuth connect (Facebook Login for Business, LinkedIn, TikTok), keywords and sources, review queue, provenance statement, deletion requests.

## Needs first (merged, with a closed review)

- D3 Specs for the parts with no PRD: `docs/handoffs/D3.md`
- Q1 Query API v0: `docs/handoffs/Q1.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Retention classes; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of D3: `docs/handoffs/D3.md`
5. Handoff of Q1: `docs/handoffs/Q1.md`
6. Client-portal PRD (D3)
7. LinkedIn and TikTok review requirements (the approvals table in `build-plan/README.md`)

## Hands on

- `docs/handoffs/U2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/U2.md` from the fresh-session review
- OAuth flows the LinkedIn and TikTok screencasts must show

## Watch for

- Nothing beyond this brief and its PRD.

## Done when

- The definition of done in `build-plan/README.md` holds.
- Screens checked in a browser against the PRD; a test proves a user never sees another client's data.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree U2 --permission-mode plan`, then `/plan-session U2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session U2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree U2`, then `/review-session U2`
- Fix: `claude --worktree U2` (or the build terminal), `/fix-session U2`; then a fresh session runs `/review-session U2 recheck`; merge when the review has no open blocker or should-fix
