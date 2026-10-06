---
name: build-session
description: Build one session's service or package from its approved plan, tests first, then write the handoff and self-check. Run after /plan-session saved docs/plans/<ID>.md.
argument-hint: <session ID>
disable-model-invocation: true
effort: max
---

# Build session $0

The stop gate is armed for this session: you can finish only when the checks for the changed packages pass, or after filing a proposal or an issue.

## 0. Preconditions

- `docs/plans/$0.md` exists. If not, stop and tell me to run `/plan-session $0` in plan mode.
- Every session in the brief's "Needs first" has its handoff in `docs/handoffs/`.
- In a fresh worktree, install first: `pnpm install`, and `uv sync` in each Python project you touch.

## 1. Load the context

The brief (`ls build-plan/sessions/$0-*`), the plan, the PRD, and the handoffs and fixtures the plan lists. Nothing else unless the plan points to it.

## 2. Tests first

Write the acceptance tests from the plan's acceptance map. Run them and show that they fail for the expected reason, not because of an import error or a typo.

## 3. Build

Implement until the acceptance tests pass, then write the tests for the plan's uncovered behaviours and make them pass.

- Use `listening-sdk` (or `py/listening_sdk`) for jobs, retries, DLQ, cursors, quota, canary, logs and metrics.
- No network in tests: fixtures and the fake-platform harness only.
- Never edit `packages/contracts` or the migrations. If you need a change, write `docs/proposals/$0-<topic>.md` from the template and stop.
- If a dependency does not behave as its handoff says: a failing test, `docs/issues/$0-<n>.md` from the template, then stop.
- A new runtime dependency gets its line in `docs/dependencies.md` (licence, owner, country), checked against the vendor screen in CONVENTIONS.
- If this service emits a `raw.items` record shape that normalize-item does not map yet, add the mapper under `services/normalize-item/src/mappers/<platform>/` with fixture tests, as `docs/patterns/MAPPERS.md` describes, and list it in the handoff.
- Ask me questions with AskUserQuestion rather than ending your turn.

## 4. Verify

Run `make check` and the service's acceptance tests, and show the output. Fix causes; never weaken, skip or delete a test to get green.

## 5. Hand off

Write `docs/handoffs/$0.md` from `build-plan/templates/HANDOFF.md`, with the acceptance table filled from real results. Run `/code-review` on the diff and fix every correctness finding test-first. Commit with a message that starts with the session ID: `$0 <service>: <summary>`.

## 6. Stop

Say the session is ready for review and give the exact next step: a new terminal, `claude --worktree $0`, then `/review-session $0`.
