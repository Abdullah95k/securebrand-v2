#!/usr/bin/env bash
# Lint, type-check and test every package that differs from main, plus its dependants, in
# TypeScript and Python, then check the fixtures. Used by `make check`, the Stop hook and CI.
#
#   scripts/check-changed.sh [--plan] [--acceptance]
#
#   --plan        print the steps and stop; nothing runs
#   --acceptance  also run the acceptance suites (CI runs them with the local stack up)
#   CHECK_BASE    compare with this ref instead of the merge base with origin/main or main
#
# With no merge base (a shallow clone, an unrelated history) it checks everything and says so:
# make check never passes silently. Every step runs even after a failure; the exit status is
# non-zero when any step failed.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

PLAN=0
ACCEPTANCE=0
for arg in "$@"; do
  case "$arg" in
    --plan) PLAN=1 ;;
    --acceptance) ACCEPTANCE=1 ;;
    *)
      echo "usage: scripts/check-changed.sh [--plan] [--acceptance]" >&2
      exit 2
      ;;
  esac
done

ROOT="$(sb_repo_root)"
cd "$ROOT"

BASE="$(sb_merge_base)"
if [ -z "$BASE" ]; then
  echo "warning: no merge base with main (origin/main or main): running the full check" >&2
  CHANGED="$(git ls-files --cached --others --exclude-standard)"
else
  CHANGED="$(sb_changed_files "$BASE")"
fi

# Root tooling that tools/repo-checks tests: a change to any of it runs repo-checks too.
ROOT_TOOLING='^(Makefile|compose\.ya?ml|package\.json|pnpm-workspace\.yaml|turbo\.json|tsconfig\.base\.json|eslint\.config\.js|\.prettierrc\.json|\.prettierignore|\.npmrc|\.node-version|\.python-version|uv\.toml|ruff\.toml|\.gitignore|\.gitattributes|CLAUDE\.md|supabase/config\.toml)$|^(scripts|stack|\.github|\.claude|tools/new-service|services/_template[^/]*)/|^(docs/[a-z]+|tests/e2e|tools/gates|tools/probes|fixtures|infra)/README\.md$'

# --- TypeScript: Turborepo resolves the changed workspaces and their dependants. -----------------
TASKS=(lint typecheck test)
[ "$ACCEPTANCE" = 1 ] && TASKS+=(test:acceptance)
TS_PACKAGES=""
TURBO_FILTERS=()
if [ -f package.json ] && [ -f turbo.json ]; then
  if [ -n "$BASE" ]; then
    TURBO_FILTERS+=("--filter=...[$BASE]")
    if printf '%s\n' "$CHANGED" | grep -qE "$ROOT_TOOLING" && [ -f tools/repo-checks/package.json ]; then
      TURBO_FILTERS+=("--filter=repo-checks")
    fi
  fi
  TS_PACKAGES="$(pnpm exec turbo ls ${TURBO_FILTERS[@]+"${TURBO_FILTERS[@]}"} --output json 2>/dev/null |
    node -e 'const j = JSON.parse(require("fs").readFileSync(0, "utf8"));
             console.log(j.packages.items.map((p) => p.name).sort().join(" "));')" ||
    sb_die "turbo could not list the workspaces (run pnpm install)"
fi

# --- Python: the nearest pyproject.toml above each changed file, plus path dependants. ----------
PY_CHANGED=()
if [ -n "$BASE" ]; then
  declare -A SEEN=()
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    dir="$(dirname "$file")"
    while [ "$dir" != "." ] && [ "$dir" != "/" ]; do
      if [ -f "$dir/pyproject.toml" ]; then
        if [ -z "${SEEN[$dir]:-}" ]; then
          SEEN[$dir]=1
          PY_CHANGED+=("$dir")
        fi
        break
      fi
      dir="$(dirname "$dir")"
    done
  done <<<"$CHANGED"
  if [ "${#PY_CHANGED[@]}" -gt 0 ]; then
    PY_PROJECTS="$(python3 "$SB_LIB_DIR/py_projects.py" "$ROOT" "${PY_CHANGED[@]}")"
  else
    PY_PROJECTS=""
  fi
else
  PY_PROJECTS="$(python3 "$SB_LIB_DIR/py_projects.py" "$ROOT" --all)"
fi

pytest_args() {
  if [ "$ACCEPTANCE" = 0 ] && [ -d "$1/tests/unit" ]; then
    echo "-q tests/unit"
  else
    echo "-q"
  fi
}

python_steps() {
  echo "uv sync --locked; uv run ruff check .; uv run ruff format --check .; uv run pyright; uv run pytest $(pytest_args "$1")"
}

# --- The plan. ------------------------------------------------------------------------------------
echo "base ${BASE:-none}"
if [ -n "$TS_PACKAGES" ]; then
  echo "step turbo ${TASKS[*]} :: $TS_PACKAGES"
else
  echo "step turbo none"
fi
while IFS= read -r project; do
  [ -n "$project" ] || continue
  echo "step python $project :: $(python_steps "$project")"
done <<<"$PY_PROJECTS"
echo "step fixtures :: scripts/check-fixtures.sh"
[ "$PLAN" = 1 ] && exit 0

# --- Run every step. ------------------------------------------------------------------------------
FAILED=()

if [ -n "$TS_PACKAGES" ]; then
  echo "== turbo ${TASKS[*]}"
  filters=()
  for pkg in $TS_PACKAGES; do filters+=("--filter=$pkg"); done
  if ! pnpm exec turbo run lint typecheck test "${filters[@]}" --continue --output-logs=errors-only; then
    FAILED+=("turbo")
  fi
  # Acceptance suites share one local stack, so they run one package at a time.
  if [ "$ACCEPTANCE" = 1 ] &&
    ! pnpm exec turbo run test:acceptance "${filters[@]}" --concurrency=1 --continue --output-logs=full; then
    FAILED+=("turbo test:acceptance")
  fi
fi

while IFS= read -r project; do
  [ -n "$project" ] || continue
  echo "== python $project"
  if [ ! -f "$project/uv.lock" ]; then
    echo "$project has no uv.lock: run uv lock in $project and commit it" >&2
    FAILED+=("python $project")
    continue
  fi
  # shellcheck disable=SC2046 # pytest_args prints separate arguments on purpose
  if ! (cd "$project" &&
    uv sync --locked --quiet &&
    uv run ruff check . &&
    uv run ruff format --check . &&
    uv run pyright &&
    uv run pytest $(pytest_args .)); then
    FAILED+=("python $project")
  fi
done <<<"$PY_PROJECTS"

echo "== fixtures"
if ! "$SB_SCRIPTS_DIR/check-fixtures.sh"; then
  FAILED+=("fixtures")
fi

if [ "${#FAILED[@]}" -gt 0 ]; then
  echo "make check failed: ${FAILED[*]}" >&2
  exit 1
fi
echo "make check passed (base ${BASE:-none})"
