# F5 · SDK scheduling, quota client, adapter kit, fake platform

Wave 1 · Foundation · track Foundation · size L (3 to 5 days with review) · kind foundation · on the critical path

## Builds

Rotation scheduler with leader election, quota client, HTTP adapter base with the error policy, canary hook, per-host gate, fake clock, and a scriptable fake-platform server.

## Needs first (merged, with a closed review)

- F4 SDK runtime (Node): `docs/handoffs/F4.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Rotation policy; Quotas, budgets and the quota governor; Error handling, canaries and fallback; Addendum: Other shared decisions
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of F4: `docs/handoffs/F4.md`
5. Fb-page-feed-poller section 5.1 (the rotation reference)
6. Quota-governor section 6 (allowance API)
7. Source-health-canary section 5 (canary hook)
8. News-robots-checker (host gate)
9. CONVENTIONS rotation and error sections

## Hands on

- `docs/handoffs/F5.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/F5.md` from the fresh-session review
- listening-sdk v0.2
- fake-platform harness with scenarios: pagination, 429, 401 and 403, empty 200, schema drift, edits, deletions

## Watch for

- Each service's due time is next_due_at in its own cursors row, set from the start of the last poll; order by it then tier; most stale first when behind, with rotation_behind (ADR-0015, ADR-0041)
- 401 and 403 are classified by reason: a quota one waits for the reset, an item-scoped one ends that item, an authorisation one marks the credential revoked or the source blocked and stops the batch, never a route state (ADR-0021); the kit never rotates accounts or IPs
- Empty-200 responses are counted per route for the canary

## Done when

- The definition of done in `build-plan/README.md` holds.
- The package README shows a service using it, with a runnable example.
- Conformance or golden tests named in this brief pass in every language involved.

## Runs alongside

F6, F7, F8

## How to run it

- Plan: `claude --worktree F5 --permission-mode plan`, then `/plan-session F5`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session F5` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree F5`, then `/review-session F5`
- Fix: `claude --worktree F5` (or the build terminal), `/fix-session F5`; then a fresh session runs `/review-session F5 recheck`; merge when the review has no open blocker or should-fix
