#!/usr/bin/env bash
# A lane's pull request merges only after its handoff and a closed review.
#
#   scripts/policy/check-handoff-review.sh [--base <ref>] [--branch <name>]
#
# On a lane branch sb/<ID> that changes services/, packages/, py/, tools/ or tests/, it needs
# docs/handoffs/<ID>.md and docs/reviews/<ID>.md, and the review's latest verdict (the last
# "Recheck" section's when there is one) must be "ready to merge". On sb/CC-<proposal> it needs
# docs/proposals/<proposal>.md approved and applied instead. Other branches (Dependabot, hotfixes)
# are skipped with a notice: the user merges those.
#
# Defaults: POLICY_BASE, else the merge base with origin/main or main; POLICY_BRANCH, else
# GITHUB_HEAD_REF, else the current branch.
set -euo pipefail
# shellcheck source=../lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

BASE_REF="${POLICY_BASE:-}"
BRANCH="${POLICY_BRANCH:-${GITHUB_HEAD_REF:-}}"
while [ $# -gt 0 ]; do
  case "$1" in
    --base) BASE_REF="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    *) echo "usage: $0 [--base <ref>] [--branch <name>]" >&2; exit 2 ;;
  esac
done

cd "$(sb_repo_root)"
[ -n "$BRANCH" ] || BRANCH="$(git symbolic-ref --short -q HEAD || true)"

case "$BRANCH" in
  sb/?*) ID="${BRANCH#sb/}" ;;
  *)
    echo "check-handoff-review: skipped: '${BRANCH:-detached HEAD}' is not a lane branch (sb/<ID>)"
    exit 0
    ;;
esac

FAILED=0
fail() {
  echo "check-handoff-review: $*" >&2
  FAILED=1
}

if [ "${ID#CC-}" != "$ID" ]; then
  PROPOSAL="docs/proposals/${ID#CC-}.md"
  if [ ! -f "$PROPOSAL" ]; then
    fail "$BRANCH applies a proposal, but $PROPOSAL does not exist"
  else
    grep -qiE '^Decision:[[:space:]]*approved' "$PROPOSAL" ||
      fail "$PROPOSAL is not approved (its Decision line must read: approved (<name>, <date>))"
    # The Applied line names the commit of this branch that applies the proposal.
    applied="$(grep -iE '^Applied:' "$PROPOSAL" | tail -1 | sed -E 's/^Applied:[[:space:]]*//I' || true)"
    sha="$(sed -nE 's/^`?([0-9a-fA-F]{7,40})`?([^0-9A-Za-z].*)?$/\1/p' <<<"$applied")"
    if ! grep -qiE '^Applied:' "$PROPOSAL"; then
      fail "$PROPOSAL has no Applied line (Applied: <commit> names the commit that applies it)"
    elif [ -z "$sha" ]; then
      fail "$PROPOSAL is not applied yet: its Applied line must name the commit that applies it, not \"$applied\""
    elif ! git merge-base --is-ancestor "$sha" HEAD 2>/dev/null; then
      fail "$PROPOSAL names commit $sha on its Applied line, but that commit is not part of this branch"
    fi
  fi
  [ "$FAILED" = 0 ] && echo "check-handoff-review: $PROPOSAL is approved and applied"
  exit "$FAILED"
fi

BASE="$(sb_policy_base "$BASE_REF")"

GATED="$(sb_changed_files "$BASE" | grep -E '^(services|packages|py|tools|tests)/' || true)"
if [ -z "$GATED" ]; then
  echo "check-handoff-review: $BRANCH changes no code (services, packages, py, tools, tests); nothing to check"
  exit 0
fi

HANDOFF="docs/handoffs/$ID.md"
REVIEW="docs/reviews/$ID.md"
[ -f "$HANDOFF" ] || fail "$HANDOFF is missing: write it from build-plan/templates/HANDOFF.md (/build-session $ID)"
if [ ! -f "$REVIEW" ]; then
  fail "$REVIEW is missing: a fresh session runs /review-session $ID"
else
  # The latest verdict, read from the last "Recheck" section when there is one, else from the whole
  # review. Its verdict lines are the "Verdict: ..." lines and the lines that start with a verdict
  # (the two-line verdict the review ends with). The lane passes only when every one of them reads
  # exactly "ready to merge" (optionally "(0 blockers, ...)"); one that starts with "needs fixes"
  # or "not ready to merge" fails it, and so does any other wording ("ready to merge once finding
  # 1 is fixed", "not yet ready to merge", the template's "ready to merge | needs fixes").
  verdict="$(awk '
    function clean(s) {
      gsub(/[*_`]/, "", s)
      sub(/^[[:space:]]+/, "", s)
      sub(/[[:space:]]+$/, "", s)
      return tolower(s)
    }
    function kind(v) {
      sub(/\.$/, "", v)
      if (v ~ /^ready to merge( \(0 blockers?[^)]*\))?$/) return "ready"
      if (v ~ /^(needs fixes|not ready to merge)/) return "fixes"
      return "unreadable"
    }
    { lines[NR] = $0 }
    /^#+[[:space:]].*[Rr]echeck/ { start = NR }
    END {
      if (!start) start = 1
      fixes = ""; unreadable = ""; ready = 0
      for (i = start; i <= NR; i++) {
        l = clean(lines[i])
        if (l ~ /^verdict[[:space:]]*:/) {
          v = l
          sub(/^verdict[[:space:]]*:[[:space:]]*/, "", v)
        } else if (l ~ /^(ready to merge|needs fixes|not ready to merge)/) {
          v = l
        } else {
          continue
        }
        k = kind(v)
        if (k == "ready") ready++
        else if (k == "fixes" && fixes == "") fixes = "line " i ": " lines[i]
        else if (k == "unreadable" && unreadable == "") unreadable = "line " i ": " lines[i]
      }
      if (fixes != "") print "needs fixes|" fixes
      else if (unreadable != "") print "unreadable|" unreadable
      else if (ready > 0) print "ready to merge|"
      else print "none|"
    }' "$REVIEW")"
  where="${verdict#*|}"
  case "${verdict%%|*}" in
    "ready to merge") ;;
    "needs fixes") fail "$REVIEW: the latest verdict is needs fixes ($where); /fix-session $ID, then /review-session $ID recheck" ;;
    unreadable) fail "$REVIEW: a verdict line is neither \"ready to merge\" nor \"needs fixes: N blockers, M should-fix\" ($where)" ;;
    *) fail "$REVIEW has no readable verdict (\"Verdict: ready to merge\" or \"Verdict: needs fixes ...\")" ;;
  esac
fi

if [ "$FAILED" = 0 ]; then
  echo "check-handoff-review: $HANDOFF present; $REVIEW says ready to merge"
fi
exit "$FAILED"
