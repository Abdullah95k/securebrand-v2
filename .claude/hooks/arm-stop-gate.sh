#!/usr/bin/env bash
# UserPromptExpansion hook for /build-session and /fix-session: arms the stop gate for this session only.
# Review, plan, probe, gate, decision and contract-change sessions are never gated.
# On this event, plain stdout is added to Claude's context.

INPUT="$(cat)"
command -v jq >/dev/null 2>&1 || exit 0
SESSION="$(printf '%s' "$INPUT" | jq -r '.session_id // empty')"
CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // empty')"
[ -n "$SESSION" ] || exit 0
[ -n "$CWD" ] || CWD="${CLAUDE_PROJECT_DIR:-.}"
ROOT="$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null)" || exit 0

mkdir -p "$ROOT/.build-state" && touch "$ROOT/.build-state/stop-gate-$SESSION"
echo "Stop gate armed for this session: when you finish, make check must pass for the changed packages. If you stop on purpose to wait for a contract change or an upstream fix, file it under docs/proposals/ or docs/issues/ first; the gate then lets you stop."
exit 0
