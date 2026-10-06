# E1 · End-to-end suite for G1

Wave 2 · Shared core · track Core · size L (3 to 5 days with review) · kind core · on the critical path

## Builds

tests/e2e/G1: the twelve G1 scenarios against the fake platform, the synthetic-load scenario, and the make e2e GATE=G1 target.

## Needs first (merged, with a closed review)

- C0 Reference vertical on the fake platform: `docs/handoffs/C0.md`
- C1 quota-governor: `docs/handoffs/C1.md`
- C2 raw-archiver: `docs/handoffs/C2.md`
- C3 lang-dialect-id: `docs/handoffs/C3.md`
- C4 normalize-item (core): `docs/handoffs/C4.md`
- C5 keyword-matcher: `docs/handoffs/C5.md`
- C6 store-writer: `docs/handoffs/C6.md`
- C7 registry-writer: `docs/handoffs/C7.md`
- C8 poster-resolver: `docs/handoffs/C8.md`
- C9 qualifier: `docs/handoffs/C9.md`
- C10 backfill-orchestrator: `docs/handoffs/C10.md`
- C11 comment-decay-scheduler: `docs/handoffs/C11.md`
- C12 source-health-canary: `docs/handoffs/C12.md`
- C13 deletion-propagator: `docs/handoffs/C13.md`
- C14 retention-purger: `docs/handoffs/C14.md`
- C15 aggregator: `docs/handoffs/C15.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of C0: `docs/handoffs/C0.md`
5. Handoff of C1: `docs/handoffs/C1.md`
6. Handoff of C2: `docs/handoffs/C2.md`
7. Handoff of C3: `docs/handoffs/C3.md`
8. Handoff of C4: `docs/handoffs/C4.md`
9. Handoff of C5: `docs/handoffs/C5.md`
10. Handoff of C6: `docs/handoffs/C6.md`
11. Handoff of C7: `docs/handoffs/C7.md`
12. Handoff of C8: `docs/handoffs/C8.md`
13. Handoff of C9: `docs/handoffs/C9.md`
14. Handoff of C10: `docs/handoffs/C10.md`
15. Handoff of C11: `docs/handoffs/C11.md`
16. Handoff of C12: `docs/handoffs/C12.md`
17. Handoff of C13: `docs/handoffs/C13.md`
18. Handoff of C14: `docs/handoffs/C14.md`
19. Handoff of C15: `docs/handoffs/C15.md`
20. Build-plan/GATES.md (the G1 checks)
21. C0 handoff (fake-platform scenarios)
22. CONVENTIONS rotation, comment series and SLO sections

## Hands on

- `docs/handoffs/E1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/E1.md` from the fresh-session review
- `tests/e2e/G1` kept as the regression suite
- make e2e GATE=G1

## Watch for

- The suite drives the real core services with the fake platform and the fake clock; no service code changes here, failures become issues for their owners
- Simulated time (48 hours of rotation, 30 days of comment series) runs on the fake clock, not wall time

## Done when

- The definition of done in `build-plan/README.md` holds.
- Every G1 check in `build-plan/GATES.md` has a scenario, and `make e2e GATE=G1` runs them all from a clean `make up`.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree E1 --permission-mode plan`, then `/plan-session E1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session E1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree E1`, then `/review-session E1`
- Fix: `claude --worktree E1` (or the build terminal), `/fix-session E1`; then a fresh session runs `/review-session E1 recheck`; merge when the review has no open blocker or should-fix
