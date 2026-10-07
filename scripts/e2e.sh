#!/usr/bin/env bash
# make e2e GATE=<gate>: runs the end-to-end suite in tests/e2e/<gate> (E2E_DIR overrides the
# directory). A suite is a workspace whose package.json has an "e2e" script, or a uv project run
# with pytest. E1 builds tests/e2e/G1; the gates after it run on staging from tools/gates (E2).
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

GATE="${1:-}"
if [ -z "$GATE" ]; then
  echo "usage: make e2e GATE=<gate>   (for example GATE=G1)" >&2
  exit 2
fi

ROOT="$(sb_repo_root)"
cd "$ROOT"
DIR="${E2E_DIR:-$ROOT/tests/e2e}/$GATE"

if [ ! -d "$DIR" ]; then
  case "$GATE" in
    G1) echo "make e2e: $DIR does not exist yet. E1 builds the G1 suite there (build-plan/sessions/E1-*.md)." >&2 ;;
    G0) echo "make e2e: G0 has no end-to-end suite; /integration-gate G0 runs its checks (build-plan/GATES.md)." >&2 ;;
    G2 | G3* | G4) echo "make e2e: $GATE runs on staging from tools/gates, which E2 builds; there is no $DIR." >&2 ;;
    *) echo "make e2e: no suite for '$GATE' in $DIR (gates: build-plan/GATES.md)." >&2 ;;
  esac
  exit 1
fi

eval "$("$SB_SCRIPTS_DIR/stack-env.sh" 2>/dev/null)"
eval "$("$SB_SCRIPTS_DIR/test-namespace.sh")"

if [ -f "$DIR/package.json" ]; then
  exec pnpm --dir "$DIR" run e2e
elif [ -f "$DIR/pyproject.toml" ]; then
  cd "$DIR"
  uv sync --locked --quiet
  exec uv run pytest
fi
sb_die "$DIR holds neither a package.json with an e2e script nor a pyproject.toml"
