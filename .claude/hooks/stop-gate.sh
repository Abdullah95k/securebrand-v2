#!/usr/bin/env bash
# Stop hook. Enforces only in sessions armed by /build-session or /fix-session (arm-stop-gate.sh).
# When anything outside docs/ and build-plan/ (or a docs lane's README) changed on this branch since
# the last green check, run the checks for the changed packages and keep Claude working while they
# fail (exit 2 shows stderr to Claude), for at most three rounds. With no merge base with main, run
# the full check on every stop. Lets Claude stop when this session has filed a proposal or an issue
# (an open question: docs/issues/<ID>-q<n>.md), which the build rules require before stopping on
# purpose, until the code changes again.

INPUT="$(cat)"
command -v jq >/dev/null 2>&1 || exit 0
MODE="$(printf '%s' "$INPUT" | jq -r '.permission_mode // empty')"
[ "$MODE" = "plan" ] && exit 0
SESSION="$(printf '%s' "$INPUT" | jq -r '.session_id // "unknown"')"
CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // empty')"
[ -n "$CWD" ] || CWD="${CLAUDE_PROJECT_DIR:-.}"
# The kit's shared helpers come from the repository that holds this hook, not from $ROOT: a test
# repository holds only a stub scripts/check-changed.sh.
KIT_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../scripts/lib" 2>/dev/null && pwd)/common.sh"

# cwd follows Claude into its worktree; CLAUDE_PROJECT_DIR stays at the main checkout.
ROOT="$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT" || exit 0
STATE="$ROOT/.build-state"
[ -f "$STATE/stop-gate-$SESSION" ] || exit 0          # not a build or fix session
[ -x scripts/check-changed.sh ] || exit 0

# The merge base with main and the files that differ from it, as make check finds them (a shallow
# clone fetches main first; names are kept as they are, Arabic ones included). No merge base: none.
if [ -r "$KIT_LIB" ]; then
  BASE="$( . "$KIT_LIB" && sb_merge_base 2>/dev/null )"
  ALL="$( [ -n "$BASE" ] && . "$KIT_LIB" && sb_changed_files "$BASE" 2>/dev/null )"
else
  BASE="$(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main 2>/dev/null || true)"
  ALL="$( [ -n "$BASE" ] && { git -c core.quotePath=false diff --no-renames --name-only "$BASE"; git -c core.quotePath=false ls-files --others --exclude-standard; } 2>/dev/null )"
fi
COUNT_FILE="$STATE/stop-gate-$SESSION.count"
PASS_FILE="$STATE/stop-gate-$SESSION.pass"
LOG="$STATE/last-check.log"

# Only a proposal or issue filed in this session lets Claude stop with failing checks: a .md file
# under docs/proposals/ or docs/issues/ (README.md excluded) that exists now, was not there when the
# gate was armed, and is not yet committed or was added after the arm commit by this branch's own
# commits. Files from earlier sessions on the lane, or brought in from main (by a merge or a
# fast-forward), never count. An arm file in the old, empty format gives no exemption.
ARM_FILE="$STATE/stop-gate-$SESSION"
ARM="$(head -n1 "$ARM_FILE" 2>/dev/null)"
SEEN_FILE="$STATE/stop-gate-$SESSION.seen" # the filed files an exemption has covered, one per line
FILED=""
NEW=""
if [ -n "$ARM" ] && [ "$ARM" != none ] && git rev-parse --verify -q "$ARM^{commit}" >/dev/null &&
  [ -f "$ARM_FILE.filed-before" ]; then
  OWN="$(git rev-list --first-parent --no-merges "$ARM..HEAD")"
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    grep -qxF -- "$f" "$ARM_FILE.filed-before" && continue
    if git cat-file -e "HEAD:$f" 2>/dev/null; then
      added_by="$(git log -n1 --format=%H --diff-filter=A HEAD -- "$f")"
      [ -n "$added_by" ] && grep -qxF -- "$added_by" <<<"$OWN" || continue # brought in by a merge
      from_main=0 # a fast-forward of main puts main's commits on the first-parent line too
      for ref in origin/main main; do
        git merge-base --is-ancestor "$added_by" "$ref" 2>/dev/null && from_main=1
      done
      [ "$from_main" = 0 ] || continue
    fi
    FILED="$FILED$f "
    grep -qxF -- "$f" "$SEEN_FILE" 2>/dev/null || NEW="$NEW$f"$'\n'
  done < <({
    git -c core.quotePath=false diff --no-renames --name-only --diff-filter=A "$ARM" -- docs/proposals docs/issues
    git -c core.quotePath=false ls-files --others --exclude-standard -- docs/proposals docs/issues
  } | grep -E '^docs/(proposals|issues)/[^/]+\.md$' | grep -vE '/README\.md$' | sort -u)
fi

# The code by content alone, with or without a merge base, so that staging or committing it
# unchanged changes nothing: every tracked and untracked file outside docs/ and build-plan/, and the
# docs lanes' READMEs, which repo-checks reads (check-changed.sh's ROOT_TOOLING), each with its
# executable bit. Neither the index nor HEAD goes in; a deleted file drops out.
FP="$( {
  git ls-files -z --cached --others --exclude-standard -- . ':(exclude)docs' ':(exclude)build-plan'
  git ls-files -z --cached --others --exclude-standard -- 'docs/*/README.md'
} 2>/dev/null | LC_ALL=C sort -zu |
  xargs -0 -r sh -c 'sha256sum -- "$@"; for f; do [ -x "$f" ] && printf "x %s\n" "$f"; done' sh 2>/dev/null |
  sha256sum | cut -d' ' -f1)"

# The exemption covers the code as it was at the first stop that saw a newly filed file: work that
# goes on afterwards in this session (an answer came in) is checked again, until a file it has not
# seen is filed. Deleting one of the filed files files nothing new.
EXEMPT_FILE="$STATE/stop-gate-$SESSION.exempt"
if [ -n "$FILED" ]; then
  if [ -n "$NEW" ]; then
    printf '%s' "$NEW" >>"$SEEN_FILE"
    echo "$FP" >"$EXEMPT_FILE"
  fi
  if [ "$(cat "$EXEMPT_FILE" 2>/dev/null)" = "$FP" ]; then
    rm -f "$COUNT_FILE"
    printf '{"systemMessage":"Stopped with a proposal or issue filed in this session: %s. Checks were not enforced."}\n' "${FILED% }"
    exit 0
  fi
fi

# Changes under docs/ and build-plan/ alone run nothing, except a docs lane's README; any other
# change runs the checks, and nothing changed since the last green run in this session runs nothing.
# With no merge base there is nothing to compare with: check-changed.sh then checks everything,
# every time.
if [ -n "$BASE" ]; then
  if ! printf '%s\n' "$ALL" | grep -v '^$' | grep -qvE '^(docs|build-plan)/' &&
    ! printf '%s\n' "$ALL" | grep -qE '^docs/[a-z]+/README\.md$'; then
    rm -f "$COUNT_FILE"
    exit 0
  fi
  if [ -f "$PASS_FILE" ] && [ "$(cat "$PASS_FILE")" = "$FP" ]; then
    exit 0
  fi
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
