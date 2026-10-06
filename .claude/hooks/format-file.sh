#!/usr/bin/env bash
# PostToolUse: format the file Claude just edited. Formatting only, never lint fixes (a fix can delete an
# import Claude is about to use). Never blocks; formatting problems surface in make check.

INPUT="$(cat)"
command -v jq >/dev/null 2>&1 || exit 0
FILE="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then exit 0; fi

case "$FILE" in
  */node_modules/*|*/.git/*|*/dist/*|*/build/*|*/docs/prds/*|*/fixtures/*) exit 0 ;;
esac

DIR="$(cd "$(dirname "$FILE")" && pwd)" || exit 0
ROOT="$(git -C "$DIR" rev-parse --show-toplevel 2>/dev/null)" || exit 0

case "$FILE" in
  *.ts|*.tsx|*.js|*.mjs|*.cjs|*.json|*.md|*.yml|*.yaml|*.css|*.html)
    if [ -x "$ROOT/node_modules/.bin/prettier" ]; then
      (cd "$ROOT" && node_modules/.bin/prettier --write --ignore-unknown --log-level warn "$FILE" >/dev/null 2>&1) || true
    fi
    ;;
  *.py)
    # Each Python service has its own pyproject.toml: format from the nearest one, up to the repo root.
    P="$DIR"
    while [ "$P" != "/" ] && [ ! -f "$P/pyproject.toml" ] && [ "$P" != "$ROOT" ]; do P="$(dirname "$P")"; done
    if [ -f "$P/pyproject.toml" ] && command -v uv >/dev/null 2>&1; then
      (cd "$P" && uv run --quiet ruff format "$FILE" >/dev/null 2>&1) || true
    fi
    ;;
esac
exit 0
