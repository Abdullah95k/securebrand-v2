#!/usr/bin/env bash
# PreToolUse guard: blocks edits to the frozen contract paths unless the session was started with
# ALLOW_CONTRACT_EDITS=1 (F2, F3, F8 and contract-change sessions) or runs on one of their orchestrated
# branches (sb/F2, sb/F3, sb/F8, sb/CC-<proposal>). Exit 2 blocks the call and shows
# stderr to Claude. A heuristic for Bash; CI is the hard backstop.

INPUT="$(cat)"
[ "${ALLOW_CONTRACT_EDITS:-0}" = "1" ] && exit 0
command -v jq >/dev/null 2>&1 || exit 0   # fail open without jq; CI still enforces

TOOL="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')"
CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // empty')"

# Orchestrated cloud sessions cannot be started with an environment variable, so the branches of the
# sessions allowed to write contracts (F2, F3, F8 and contract changes) carry the same permission.
BRANCH="$(git -C "${CWD:-.}" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
case "$BRANCH" in
  sb/F2|sb/F3|sb/F8|sb/CC-*) exit 0 ;;
esac

PROTECTED='(packages/contracts|supabase/migrations|clickhouse/migrations)'
PATH_RE="(^|/)${PROTECTED}(/|$)"

block() {
  echo "Blocked: $1. Contracts are frozen: write docs/proposals/<session>-<topic>.md from build-plan/templates/PROPOSAL.md and stop. If this was a read or a build command, rephrase it without writing under that path." >&2
  exit 2
}

case "$TOOL" in
  Edit|Write|MultiEdit|NotebookEdit)
    FILE="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')"
    FILE="${FILE//\\//}"
    if [ -n "$FILE" ] && [[ "$FILE" =~ $PATH_RE ]]; then
      block "$FILE is under a contract path"
    fi
    ;;
  Bash)
    CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"
    # Ignore quoted text (commit messages, echo strings) before matching.
    BARE="$(printf '%s' "$CMD" | sed -E "s/'[^']*'//g; s/\"[^\"]*\"//g")"
    IN_PROTECTED=0
    CD_RE="(^|[;&|[:space:]])cd[[:space:]]+[^;&|]*${PROTECTED}"
    if [[ "$CWD" =~ $PATH_RE ]] || [[ "$BARE" =~ $CD_RE ]]; then
      IN_PROTECTED=1
    fi
    REDIRECT_RE="(^|[^-0-9&])(>>?|tee([[:space:]]+-a)?)[[:space:]]*[^[:space:];&|]*${PROTECTED}"
    MUTATE_RE='(sed[[:space:]]+(-[a-zA-Z]*i|--in-place)|(^|[;&|[:space:]])(mv|cp|rm|truncate|touch)[[:space:]]|git[[:space:]]+(checkout|restore|rm|mv)[[:space:]])'
    LOCAL_WRITE_RE='(^|[^-0-9&])>>?[[:space:]]*[^/[:space:];&|]+|tee[[:space:]]'
    if [[ "$BARE" =~ $REDIRECT_RE ]]; then
      block "the command writes into a contract path"
    fi
    if [[ "$BARE" =~ $PROTECTED ]] && [[ "$BARE" =~ $MUTATE_RE ]]; then
      block "the command changes files under a contract path"
    fi
    if [ "$IN_PROTECTED" = "1" ] && { [[ "$BARE" =~ $MUTATE_RE ]] || [[ "$BARE" =~ $LOCAL_WRITE_RE ]]; }; then
      block "the command changes files while working inside a contract path"
    fi
    ;;
esac
exit 0
