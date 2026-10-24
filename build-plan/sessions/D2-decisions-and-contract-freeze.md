# D2 · Decisions and contract freeze

Wave 0 · Decide and freeze · track Decide · size M (1 to 2 days with review) · kind decision · on the critical path

## Builds

ADRs for the 9 proposed decisions, the foundation choices and every conflict; CONVENTIONS v1.1.

## Needs first (merged, with a closed review)

- D1 Contract inventory: `docs/handoffs/D1.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: the whole file
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of D1: `docs/handoffs/D1.md`
5. `docs/contracts/INVENTORY.md` and `docs/contracts/CONFLICTS.md`
6. The nine proposed decisions in `docs/prds/README.md`
7. The foundation choices table in `build-plan/README.md`

## Hands on

- `docs/handoffs/D2.md` from `build-plan/templates/HANDOFF.md`
- `docs/decisions/ADR-0001...` (one decision each, with options and consequences)
- `docs/prds/_shared/CONVENTIONS.md` v1.1 with the addendum and decisions folded in
- `docs/decisions/DEFERRED.md` (every open question not decided now, with the session that must settle it)

## Watch for

- Claude interviews you with AskUserQuestion; it proposes, you decide
- Do not let a decision hide in a PRD edit: every change to a PRD cites its ADR

## Done when

- Every deliverable listed under "Hands on" exists and you have read it.

## Runs alongside

F1

## Your part

You, for the whole session.

## How to run it

- Start: `claude --worktree D2` (it writes documents, so not plan mode)
- Run: `/decide-session D2`
- Review: read every file it produced yourself before merging; the decisions are yours
