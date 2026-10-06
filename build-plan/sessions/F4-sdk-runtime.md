# F4 · SDK runtime (Node)

Wave 1 · Foundation · track Foundation · size L (3 to 5 days with review) · kind foundation · on the critical path

## Builds

listening-sdk core: producer and consumer partitioned by source_id, envelope validation, job wrapper with retries and DLQ, cursor advance after ack, jobs.completed reports, structured logs, Prometheus metrics, health, config and Vault, control-plane client, service generator.

## Needs first (merged, with a closed review)

- F2 Contracts package: `docs/handoffs/F2.md`
- F3 Control-plane schema: `docs/handoffs/F3.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of F2: `docs/handoffs/F2.md`
5. Handoff of F3: `docs/handoffs/F3.md`
6. CONVENTIONS idempotency, error-handling and observability sections
7. ADRs on the Kafka client and jobs.completed
8. Fb-page-feed-poller PRD as the reference consumer

## Hands on

- `docs/handoffs/F4.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/F4.md` from the fresh-session review
- `packages/listening-sdk` v0.1
- pnpm new:service <name> generating a service that passes make check

## Watch for

- A cursor never advances before the producer acknowledges the batch
- Backoff 30 s to 15 min with jitter, 5 attempts, then dlq.<service> and an alert
- Prove with a test that no token or secret can reach a log line

## Done when

- The definition of done in `build-plan/README.md` holds.
- The package README shows a service using it, with a runnable example.
- Conformance or golden tests named in this brief pass in every language involved.

## Runs alongside

F7, F8

## How to run it

- Plan: `claude --worktree F4 --permission-mode plan`, then `/plan-session F4`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session F4` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree F4`, then `/review-session F4`
- Fix: `claude --worktree F4` (or the build terminal), `/fix-session F4`; then a fresh session runs `/review-session F4 recheck`; merge when the review has no open blocker or should-fix
