#!/usr/bin/env bash
# UserPromptExpansion hook for /build-session and /fix-session: arms the stop gate for this session only,
# and records what was already filed (stop-gate.sh lets Claude stop early only for what it files later).
# Review, plan, probe, gate, decision and contract-change sessions are never gated.
# On this event, plain stdout is added to Claude's context.

INPUT="$(cat)"
command -v jq >/dev/null 2>&1 || exit 0
SESSION="$(printf '%s' "$INPUT" | jq -r '.session_id // empty')"
CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // empty')"
[ -n "$SESSION" ] || exit 0
[ -n "$CWD" ] || CWD="${CLAUDE_PROJECT_DIR:-.}"
ROOT="$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null)" || exit 0

STATE="$ROOT/.build-state"
ARM_FILE="$STATE/stop-gate-$SESSION"
mkdir -p "$STATE" || exit 0
# Record the arm point once per session: the commit HEAD was on, and every proposal and issue that
# already existed (tracked or untracked). Only files filed after this point let Claude stop early.
if [ ! -s "$ARM_FILE" ]; then
  git -C "$ROOT" -c core.quotePath=false ls-files --cached --others --exclude-standard -- docs/proposals docs/issues \
    | sort -u >"$ARM_FILE.filed-before"
  git -C "$ROOT" rev-parse --verify -q HEAD >"$ARM_FILE" || echo none >"$ARM_FILE"
fi
echo "Stop gate armed for this session: when you finish, make check must pass for the changed packages. If you stop on purpose to wait for a contract change or an upstream fix, file a new one under docs/proposals/ or docs/issues/ first (an open question: docs/issues/<ID>-q<n>.md); the gate then lets you stop."
exit 0
