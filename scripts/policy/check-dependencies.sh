#!/usr/bin/env bash
# Every new runtime dependency (npm, PyPI, container image) has a row in docs/dependencies.md.
#
#   scripts/policy/check-dependencies.sh [--base <ref>]
#
# Default base: POLICY_BASE, else the merge base with origin/main or main. The rules are in
# scripts/policy/dependencies.py.
set -euo pipefail
# shellcheck source=../lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

BASE_REF="${POLICY_BASE:-}"
while [ $# -gt 0 ]; do
  case "$1" in
    --base) BASE_REF="$2"; shift 2 ;;
    *) echo "usage: $0 [--base <ref>]" >&2; exit 2 ;;
  esac
done

ROOT="$(sb_repo_root)"
cd "$ROOT"
if [ -n "$BASE_REF" ]; then
  BASE="$(git merge-base HEAD "$BASE_REF" 2>/dev/null || git rev-parse --verify "$BASE_REF^{commit}")"
else
  BASE="$(sb_merge_base)"
fi
[ -n "$BASE" ] || sb_die "no merge base with main; pass --base <ref>"

exec python3 "$SB_SCRIPTS_DIR/policy/dependencies.py" "$ROOT" "$BASE"
