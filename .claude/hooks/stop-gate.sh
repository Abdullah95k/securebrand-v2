#!/usr/bin/env bash
# Stop hook. Enforces only in sessions armed by /build-session or /fix-session (arm-stop-gate.sh).
# When code changed on this branch since the last green check, run the checks for the changed packages
# and keep Claude working while they fail (exit 2 shows stderr to Claude), for at most three rounds.
# Lets Claude stop when the session has filed a proposal or an issue, which the build rules require
# before stopping on purpose.

INPUT="$(cat)"
command -v jq >/dev/null 2>&1 || exit 0
MODE="$(printf '%s' "$INPUT" | jq -r '.permission_mode // empty')"
[ "$MODE" = "plan" ] && exit 0
SESSION="$(printf '%s' "$INPUT" | jq -r '.session_id // "unknown"')"
CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // empty')"
[ -n "$CWD" ] || CWD="${CLAUDE_PROJECT_DIR:-.}"

# cwd follows Claude into its worktree; CLAUDE_PROJECT_DIR stays at the main checkout.
ROOT="$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT" || exit 0
STATE="$ROOT/.build-state"
[ -f "$STATE/stop-gate-$SESSION" ] || exit 0          # not a build or fix session
[ -x scripts/check-changed.sh ] || exit 0

BASE="$(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main 2>/dev/null || git rev-parse HEAD)"
ALL="$( { git diff --name-only "$BASE"; git ls-files --others --exclude-standard; } 2>/dev/null)"
COUNT_FILE="$STATE/stop-gate-$SESSION.count"
PASS_FILE="$STATE/stop-gate-$SESSION.pass"
LOG="$STATE/last-check.log"

FILED="$(printf '%s\n' "$ALL" | grep -E '^docs/(proposals|issues)/' | sort -u | tr '\n' ' ')"
if [ -n "$FILED" ]; then
  rm -f "$COUNT_FILE"
  printf '{"systemMessage":"Stopped with a proposal or issue filed: %s. Checks were not enforced."}\n' "${FILED% }"
  exit 0
fi

if ! printf '%s\n' "$ALL" | grep -qE '^(services|packages|py|tools)/'; then
  rm -f "$COUNT_FILE"
  exit 0
fi

# Skip when nothing changed since the last green run in this session.
FP="$( { git diff "$BASE" -- services packages py tools; git ls-files --others --exclude-standard -- services packages py tools | sort | xargs -r sha256sum; } 2>/dev/null | sha256sum | cut -d' ' -f1)"
if [ -f "$PASS_FILE" ] && [ "$(cat "$PASS_FILE")" = "$FP" ]; then
  exit 0
fi

if scripts/check-changed.sh >"$LOG" 2>&1; then
  echo "$FP" > "$PASS_FILE"
  rm -f "$COUNT_FILE"
  exit 0
fi

N=$(( $(cat "$COUNT_FILE" 2>/dev/null || echo 0) + 1 ))
echo "$N" > "$COUNT_FILE"
if [ "$N" -gt 3 ]; then
  rm -f "$COUNT_FILE"
  printf '{"systemMessage":"Checks still fail after 3 rounds, so Claude was allowed to stop. See %s"}\n' "$LOG"
  exit 0
fi

{
  echo "make check failed (round $N of 3). Fix the cause; never weaken or skip a test to pass. If the failure is in a contract or another service, file docs/proposals/ or docs/issues/ and stop. Last lines of $LOG:"
  tail -n 60 "$LOG"
} >&2
exit 2
