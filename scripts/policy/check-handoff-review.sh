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
    applied="$(grep -iE '^Applied:' "$PROPOSAL" | tail -1 | sed -E 's/^Applied:[[:space:]]*//I')"
    case "$(printf '%s' "$applied" | tr '[:upper:]' '[:lower:]')" in
      "" | no | "no "* | "no|"* | "no |"*) fail "$PROPOSAL is not applied yet (its Applied line must name the commit)" ;;
    esac
  fi
  [ "$FAILED" = 0 ] && echo "check-handoff-review: $PROPOSAL is approved and applied"
  exit "$FAILED"
fi

if [ -n "$BASE_REF" ]; then
  BASE="$(git merge-base HEAD "$BASE_REF" 2>/dev/null || git rev-parse --verify "$BASE_REF^{commit}")"
else
  BASE="$(sb_merge_base)"
fi
[ -n "$BASE" ] || sb_die "no merge base with main; pass --base <ref>"

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
  # The latest verdict: the last line naming one, in the last "Recheck" section when there is one.
  # A line naming both (the template's "ready to merge | needs fixes") is not a verdict.
  verdict="$(awk '
    { lines[NR] = $0 }
    /^#+[[:space:]].*[Rr]echeck/ { start = NR }
    END {
      if (!start) start = 1
      v = ""
      for (i = start; i <= NR; i++) {
        l = tolower(lines[i])
        ready = index(l, "ready to merge") > 0
        fixes = index(l, "needs fixes") > 0
        if (ready && fixes) continue
        if (fixes || index(l, "not ready to merge") > 0) v = "needs fixes"
        else if (ready) v = "ready to merge"
      }
      print v
    }' "$REVIEW")"
  case "$verdict" in
    "ready to merge") ;;
    "needs fixes") fail "$REVIEW: the latest verdict is needs fixes; /fix-session $ID, then /review-session $ID recheck" ;;
    *) fail "$REVIEW has no readable verdict (\"ready to merge\" or \"needs fixes\")" ;;
  esac
fi

if [ "$FAILED" = 0 ]; then
  echo "check-handoff-review: $HANDOFF present; $REVIEW says ready to merge"
fi
exit "$FAILED"
