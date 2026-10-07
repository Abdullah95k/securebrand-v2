#!/usr/bin/env bash
# make test SERVICE=<name>: the unit and acceptance suites of one service or package, TypeScript or
# Python (or both, for a package that holds both, like packages/contracts). The stack's variables
# and the test namespace are set first, so acceptance tests that need the local stack find it.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

NAME="${1:-}"
if [ -z "$NAME" ]; then
  echo "usage: make test SERVICE=<name>   (a directory under services/, packages/, py/ or tools/)" >&2
  exit 2
fi

ROOT="$(sb_repo_root)"
cd "$ROOT"
SEARCHED=("services/$NAME" "packages/$NAME" "py/$NAME" "tools/$NAME" "tools/probes/$NAME" "tests/e2e/$NAME")
DIR=""
for candidate in "${SEARCHED[@]}"; do
  if [ -d "$candidate" ]; then
    DIR="$candidate"
    break
  fi
done
if [ -z "$DIR" ]; then
  echo "make test: no service or package named $NAME; searched: ${SEARCHED[*]}" >&2
  exit 1
fi

eval "$("$SB_SCRIPTS_DIR/stack-env.sh" 2>/dev/null)"
eval "$("$SB_SCRIPTS_DIR/test-namespace.sh")"

RAN=0
FAILED=0
if [ -f "$DIR/package.json" ]; then
  for task in test test:acceptance; do
    if node -e 'const s = require(process.argv[1]).scripts ?? {}; process.exit(s[process.argv[2]] ? 0 : 1)' \
      "$ROOT/$DIR/package.json" "$task"; then
      RAN=1
      echo "== $DIR: pnpm run $task"
      (cd "$DIR" && pnpm run "$task") || FAILED=1
    fi
  done
fi
if [ -f "$DIR/pyproject.toml" ]; then
  RAN=1
  echo "== $DIR: pytest"
  if [ ! -f "$DIR/uv.lock" ]; then
    echo "$DIR has no uv.lock: run uv lock in $DIR and commit it" >&2
    FAILED=1
  else
    (cd "$DIR" && uv sync --locked --quiet && uv run pytest -v) || FAILED=1
  fi
fi
[ "$RAN" = 1 ] || sb_die "$DIR has neither a test script in package.json nor a pyproject.toml"
exit "$FAILED"
