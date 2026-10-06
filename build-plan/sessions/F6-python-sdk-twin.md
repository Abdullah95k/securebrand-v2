# F6 · Python SDK twin

Wave 1 · Foundation · track Foundation · size M (1 to 2 days with review) · kind foundation

## Builds

The Python subset of the SDK: consumer and producer, envelope, job wrapper, DLQ, jobs.completed, logs, metrics, health, config.

## Needs first (merged, with a closed review)

- F2 Contracts package: `docs/handoffs/F2.md`
- F4 SDK runtime (Node): `docs/handoffs/F4.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of F2: `docs/handoffs/F2.md`
5. Handoff of F4: `docs/handoffs/F4.md`
6. F4 handoff
7. Contracts JSON Schemas and the conformance suite

## Hands on

- `docs/handoffs/F6.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/F6.md` from the fresh-session review
- `py/listening_sdk` v0.1 passing the shared conformance suite

## Watch for

- Same retry, DLQ and cursor semantics as Node, proved by shared tests, not by reading

## Done when

- The definition of done in `build-plan/README.md` holds.
- The package README shows a service using it, with a runnable example.
- Conformance or golden tests named in this brief pass in every language involved.

## Runs alongside

F5, F8

## How to run it

- Plan: `claude --worktree F6 --permission-mode plan`, then `/plan-session F6`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session F6` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree F6`, then `/review-session F6`
- Fix: `claude --worktree F6` (or the build terminal), `/fix-session F6`; then a fresh session runs `/review-session F6 recheck`; merge when the review has no open blocker or should-fix
