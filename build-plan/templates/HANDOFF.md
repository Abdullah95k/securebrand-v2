# Handoff · <ID> <service or package>

Date · PR · model · sessions (plan, build, review, fix)

## What it does now

Two or three sentences, and the entry points a reader should open first.

## Contracts

- Reads: <topic>@<version>; <table>(<columns>); <job queue> (<kinds>)
- Writes: <topic>@<version> (example in fixtures/contracts/valid/...); <table>(<columns>)
- Contract changes: none | docs/proposals/<file> (status)
- normalize-item mapper added: none | <platform>/<record shape>

## Run and test

- Commands: `pnpm --filter <name> test`; `pnpm --filter <name> test:acceptance`
- Config and secrets: names only, never values
- Fixtures used and where they came from

## Acceptance criteria

| PRD 13 | Test | Result |
|---|---|---|
| 1 | test/acceptance/<file> :: <name> | pass |

## Decisions made here

Each PRD ambiguity, the answer, who decided, and the ADR if one was written.

## Deviations from the PRD

None, or each one with its reason and who approved it.

## For the sessions that depend on this

Formats, ids, ordering and edge cases they must know.

## Operations

Metrics and alerts added (names), failure modes and what to do about each.

## Open items

Deferred questions (DEFERRED.md ids), known limits, follow-ups.

## Review

Review file, each finding and its fixing commit, or why it was declined.
