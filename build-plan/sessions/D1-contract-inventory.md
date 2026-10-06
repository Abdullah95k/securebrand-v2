# D1 · Contract inventory

Wave 0 · Decide and freeze · track Decide · size M (1 to 2 days with review) · kind decision · on the critical path

## Builds

One inventory of every topic, job queue, table, column, budget tag, flag and retention class the 86 PRDs use, with every conflict between them.

## Needs first (merged, with a closed review)

- Nothing. This session can start on day one.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: the whole file
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. All 86 PRDs in `docs/prds/`
5. The nine proposed decisions in `docs/prds/README.md`
6. `docs/prds/OPEN-QUESTIONS.md`

## Hands on

- `docs/handoffs/D1.md` from `build-plan/templates/HANDOFF.md`
- `docs/contracts/INVENTORY.md` (each topic: producers, consumers, fields per PRD; each table: columns, writers, readers; each job queue: producer and consumer)
- `docs/contracts/CONFLICTS.md` (each disagreement, where it appears, the options)

## Watch for

- Have one subagent per PRD folder extract its rows, then merge and cross-check in the main session
- Several pollers publish tier changes on source.events, while registry-writer otherwise owns that topic: list every writer of every topic
- Tables or columns named in a single PRD (for example retention_audit, profile_cache, news_sites) must appear in the inventory
- The same field under different names in different PRDs is a conflict, not a synonym

## Done when

- Every deliverable listed under "Hands on" exists and you have read it.

## Runs alongside

F1, the day-one approval applications (see the approvals table in `build-plan/README.md`)

## How to run it

- Start: `claude --worktree D1` (it writes documents, so not plan mode)
- Run: `/decide-session D1`
- Review: read every file it produced yourself before merging, then ask a fresh session to check them against the PRDs
