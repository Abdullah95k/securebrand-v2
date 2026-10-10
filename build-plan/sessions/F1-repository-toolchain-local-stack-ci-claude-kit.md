# F1 · Repository, toolchain, local stack, CI, Claude kit

Wave 1 · Foundation · track Foundation · size M (1 to 2 days with review) · kind foundation · on the critical path

## Builds

pnpm and Turborepo monorepo, TypeScript strict, Vitest, uv with ruff and pytest, docker compose (Redpanda, Supabase local, ClickHouse, SeaweedFS for S3), CI, the docs tree; fits the kit's check script, make targets and hooks to the toolchain.

## Needs first (merged, with a closed review)

- Nothing. This session can start on day one.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. The kit and the PRDs, committed to main on day zero (KIT-README.md)

## Hands on

- `docs/handoffs/F1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/F1.md` from the fresh-session review
- make up, make check, make test, make e2e
- `services/_template`
- `docs/` tree with the PRDs, conventions and the kit's templates
- CI on every pull request: make check on changed packages; handoff and closed review present for service changes; contract paths only on a contract-change label; a docs/dependencies.md line for each new dependency; scripts/check-fixtures.sh for scrubbed fixtures
- Per-worktree test namespaces (topic prefix, Postgres schema, ClickHouse database)

## Watch for

- Pin versions: Node LTS, pnpm, Python, uv, Redpanda, ClickHouse, Supabase CLI
- Tests in parallel worktrees share one local stack: derive a TEST_NAMESPACE from the worktree name for topics, Postgres schemas and ClickHouse databases
- MinIO's community edition is no longer published; use SeaweedFS or Garage for local S3

## Done when

- The definition of done in `build-plan/README.md` holds.
- The package README shows a service using it, with a runnable example.
- Conformance or golden tests named in this brief pass in every language involved.

## Runs alongside

D1, D2

## How to run it

- Plan: `claude --worktree F1 --permission-mode plan`, then `/plan-session F1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session F1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree F1`, then `/review-session F1`
- Fix: `claude --worktree F1` (or the build terminal), `/fix-session F1`; then a fresh session runs `/review-session F1 recheck`; merge when the review has no open blocker or should-fix
