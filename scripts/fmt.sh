#!/usr/bin/env bash
# make fmt: formats the repository the way the kit's format hook formats each edited file:
# Prettier (with .prettierignore) for code, configuration and Markdown, and ruff format in every
# Python project. Formatting only, never lint fixes.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

ROOT="$(sb_repo_root)"
cd "$ROOT"
pnpm exec prettier --write --log-level warn .
while IFS= read -r project; do
  [ -n "$project" ] || continue
  (cd "$project" && uv run --quiet ruff format --quiet .)
done < <(python3 "$SB_LIB_DIR/py_projects.py" "$ROOT" --all)
