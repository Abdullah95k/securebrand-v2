#!/usr/bin/env bash
# make policy: the pull request checks CI runs in the policy job, locally. Every check runs; the
# exit status is non-zero when one failed.
#   BASE=<ref> (default: the merge base with main), PR_LABELS=a,b (default: none),
#   POLICY_BRANCH=<branch> (default: the current branch)
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARGS=()
[ -z "${BASE:-}" ] || ARGS=(--base "$BASE")

FAILED=()
"$DIR/check-contract-paths.sh" "${ARGS[@]}" || FAILED+=("contract paths")
"$DIR/check-handoff-review.sh" "${ARGS[@]}" || FAILED+=("handoff and review")
"$DIR/check-dependencies.sh" "${ARGS[@]}" || FAILED+=("dependencies")
"$DIR/../check-fixtures.sh" || FAILED+=("fixtures")

if [ "${#FAILED[@]}" -gt 0 ]; then
  echo "make policy failed: ${FAILED[*]}" >&2
  exit 1
fi
echo "make policy passed"
