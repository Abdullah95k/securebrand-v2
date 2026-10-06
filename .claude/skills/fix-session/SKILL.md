---
name: fix-session
description: Fix the blockers and should-fix findings of a session's review, test-first, touching nothing else. Run after /review-session.
argument-hint: <session ID>
disable-model-invocation: true
effort: max
---

# Fix session $0

The stop gate is armed for this session: you can finish only when the checks for the changed packages pass.

1. Read `docs/reviews/$0.md`, the brief (`ls build-plan/sessions/$0-*`) and `docs/plans/$0.md`.
2. For every open blocker and should-fix, in order: first a test that fails because of the finding, then the fix, then show the test passing. One commit per finding, its message starting `$0 fix: <finding title>`.
3. Touch nothing the review did not raise. If a finding is wrong, do not "fix" it: explain why with evidence in the handoff, and leave it for me to decide.
4. Run `make check` and show the output.
5. Update the "Review" section of `docs/handoffs/$0.md`: each finding with its fixing commit, or why it was declined.
6. Stop and tell me the next step: a fresh session, `claude --worktree $0`, then `/review-session $0 recheck`.
