# F8 · ClickHouse schema

Wave 1 · Foundation · track Foundation · size M (1 to 2 days with review) · kind foundation

## Builds

Migrations for items, comments, analysis, metrics_timeseries, aggregates_hourly, sources_dim, keywords_dim and hits; month partitions; TTL by retention class; text index on text_norm; migration runner.

## Needs first (merged, with a closed review)

- D2 Decisions and contract freeze: `docs/handoffs/D2.md`
- F2 Contracts package: `docs/handoffs/F2.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment (analytics store); Retention classes
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of D2: `docs/handoffs/D2.md`
5. Handoff of F2: `docs/handoffs/F2.md`
6. Store-writer, aggregator and retention-purger PRDs
7. CONVENTIONS analytics store and retention classes

## Hands on

- `docs/handoffs/F8.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/F8.md` from the fresh-session review
- `clickhouse/migrations` v1
- query smoke tests

## Watch for

- Upserts keyed on item_id need an explicit version column (ReplacingMergeTree or equivalent) so a replay never wins over a newer edit
- Raw text TTLs differ by retention class; aggregates are kept ten years
- Start this session with ALLOW_CONTRACT_EDITS=1: it is one of the few allowed to write the contract paths

## Done when

- The definition of done in `build-plan/README.md` holds.
- The package README shows a service using it, with a runnable example.
- Conformance or golden tests named in this brief pass in every language involved.

## Runs alongside

F3, F4, F5, F6, F7

## How to run it

- Plan: `ALLOW_CONTRACT_EDITS=1 claude --worktree F8 --permission-mode plan`, then `/plan-session F8`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session F8` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree F8`, then `/review-session F8`
- Fix: `ALLOW_CONTRACT_EDITS=1 claude --worktree F8` (or the build terminal), `/fix-session F8`; then a fresh session runs `/review-session F8 recheck`; merge when the review has no open blocker or should-fix
