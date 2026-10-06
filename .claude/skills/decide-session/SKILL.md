---
name: decide-session
description: Run a decision or specification session (D1 inventory, D2 decisions, D3 missing PRDs) as its brief describes, interviewing the user where decisions are needed.
argument-hint: <D1 | D2 | D3>
disable-model-invocation: true
effort: max
---

# Decision session $ARGUMENTS

Read the brief first (`ls build-plan/sessions/$ARGUMENTS-*`). Write no service code in this session. This session writes documents, so it does not run in plan mode.

## D1 · Contract inventory

Use one subagent per folder under `docs/prds/` (and one for `docs/prds/_shared/`). Each extracts, for every PRD, each topic, job queue and job kind, table and column, budget tag, flag and retention class it reads or writes, with section references. Merge the results into `docs/contracts/INVENTORY.md` (by topic, by table, by job queue, by budget tag). Then list every conflict in `docs/contracts/CONFLICTS.md`: two writers of one topic or column, two names for one field, one field with two types, a table named in only one PRD, a job kind no producer emits. Do not resolve anything.

## D2 · Decisions and contract freeze

Interview me with AskUserQuestion, one decision at a time, through `docs/contracts/CONFLICTS.md`, the nine decisions in `docs/prds/README.md` and the foundation choices in `build-plan/README.md`. For each one: the options, your recommendation first, and the consequences. Record each decision as `docs/decisions/ADR-<nnnn>-<slug>.md` from the template, with its "Applies to" line. Finish by producing CONVENTIONS v1.1 (every change citing its ADR) and `docs/decisions/DEFERRED.md` (every open question not decided now, with the session that must settle it).

## D3 · PRDs for the parts with no PRD

For the query API, the client portal, the dashboard (including the slice for Meta's App Review) and the admin console, in turn: read every PRD whose section 4 names it as a consumer, interview me with AskUserQuestion, then write `docs/prds/apps/<name>.md` in the 14-section template of CONVENTIONS, with testable acceptance criteria.
