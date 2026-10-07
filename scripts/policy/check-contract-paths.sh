#!/usr/bin/env bash
# Contracts are frozen: a pull request that changes anything under packages/contracts,
# supabase/migrations or clickhouse/migrations needs the contract-change label. The orchestrator
# applies it to the F2, F3, F8 and contract-change pull requests; every other session writes a
# proposal instead (build-plan/templates/PROPOSAL.md). CI is the hard backstop behind the
# guard-contracts hook.
#
#   scripts/policy/check-contract-paths.sh [--base <ref>] [--labels <a,b | JSON array>]
#
# Defaults: POLICY_BASE, else the merge base with origin/main or main; PR_LABELS (CI passes the
# pull request's labels as a JSON array).
set -euo pipefail
# shellcheck source=../lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

BASE_REF="${POLICY_BASE:-}"
LABELS="${PR_LABELS:-}"
while [ $# -gt 0 ]; do
  case "$1" in
    --base) BASE_REF="$2"; shift 2 ;;
    --labels) LABELS="$2"; shift 2 ;;
    *) echo "usage: $0 [--base <ref>] [--labels <labels>]" >&2; exit 2 ;;
  esac
done

cd "$(sb_repo_root)"
BASE="$(sb_policy_base "$BASE_REF")"

mapfile -t CHANGED < <(sb_changed_files "$BASE" | grep -E '^(packages/contracts|supabase/migrations|clickhouse/migrations)/' || true)
if [ "${#CHANGED[@]}" -eq 0 ]; then
  echo "check-contract-paths: no contract path changed"
  exit 0
fi

has_label() {
  if [ "${LABELS#\[}" != "$LABELS" ]; then
    python3 -c 'import json, sys; sys.exit(0 if "contract-change" in json.loads(sys.argv[1]) else 1)' "$LABELS"
  else
    printf '%s\n' "${LABELS//,/$'\n'}" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | grep -qx 'contract-change'
  fi
}

if has_label; then
  echo "check-contract-paths: contract paths changed under the contract-change label:"
  printf '  %s\n' "${CHANGED[@]}"
  exit 0
fi

{
  echo "check-contract-paths: these files are under a frozen contract path:"
  printf '  %s\n' "${CHANGED[@]}"
  echo "A pull request that changes them needs the contract-change label (the F2, F3, F8 and"
  echo "contract-change lanes). Any other session writes docs/proposals/<session>-<topic>.md and stops."
} >&2
exit 1
