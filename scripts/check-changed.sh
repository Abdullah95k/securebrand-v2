#!/usr/bin/env bash
# Lint, type-check and test every package that differs from main, plus its dependants.
# Used by `make check`, the Stop hook and CI. F1 adapts the commands to the real toolchain.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
BASE="$(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main 2>/dev/null || git rev-parse HEAD)"

# TypeScript workspaces: Turborepo runs lint, typecheck and test for the packages changed since BASE
# and everything that depends on them ("..." prefix).
if [ -f package.json ] && [ -f turbo.json ]; then
  pnpm turbo run lint typecheck test --filter="...[$BASE]" --output-logs=errors-only
fi

# Python projects (each with its own pyproject.toml) that have changes.
PY_DIRS="$( { git diff --name-only "$BASE"; git ls-files --others --exclude-standard; } \
  | grep -E '^(services|py)/[^/]+/' | cut -d/ -f1-2 | sort -u || true)"
for d in $PY_DIRS; do
  if [ -f "$d/pyproject.toml" ]; then
    echo "== $d"
    (cd "$d" && uv run ruff check . && uv run ruff format --check . && uv run pytest -q)
  fi
done

# Fixtures must stay scrubbed (tokens and private names); F1 implements this check.
if [ -x scripts/check-fixtures.sh ]; then
  scripts/check-fixtures.sh
fi
