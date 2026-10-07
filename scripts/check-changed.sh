#!/usr/bin/env bash
# Lint, type-check and test every package that differs from main, plus its dependants, in
# TypeScript and Python, then check the fixtures. Used by `make check`, the Stop hook and CI.
#
#   scripts/check-changed.sh [--plan] [--acceptance]
#
#   --plan        print the steps and stop; nothing runs
#   --acceptance  also run the acceptance suites, with the stack variables (stack-env.sh) and
#                 this checkout's test namespace (test-namespace.sh) exported; CI runs them with
#                 the local stack up
#   CHECK_BASE    compare with this commit instead of the merge base with origin/main or main
#                 (CI passes the commit before a push to main)
#
# With no merge base (a shallow clone, an unrelated history) or a CHECK_BASE that is not a commit
# here, it checks everything and says so: make check never passes silently. A change to the
# shared Python configuration (ruff.toml, .python-version, uv.toml) checks every Python project,
# and a change under fixtures/ (other than a README) every workspace and Python project.
# Every step runs even after a failure; the exit status is non-zero when any step failed.
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
  [ -n "${CHECK_BASE:-}" ] || echo "warning: no merge base with main (origin/main or main)" >&2
  echo "warning: nothing to compare with: running the full check" >&2
  CHANGED="$(git ls-files --cached --others --exclude-standard)"
else
  CHANGED="$(sb_changed_files "$BASE")"
fi

# Services read recorded responses from fixtures/<platform>/ (turbo.json lists fixtures/ among the
# inputs of every test task), but no package holds fixtures/, so a change there selects nothing by
# itself: every workspace and Python project is checked. A README there is read by no test.
FIXTURES_CHANGED=0
fixture_files="$(grep -E '^fixtures/' <<<"$CHANGED" || true)"
if [ -n "$BASE" ] && [ -n "$fixture_files" ] && grep -qvE '(^|/)README\.md$' <<<"$fixture_files"; then
  FIXTURES_CHANGED=1
  echo "note: fixtures changed: checking every workspace and Python project, whose tests read them" >&2
fi

# Root tooling that tools/repo-checks tests: a change to any of it runs repo-checks too.
ROOT_TOOLING='^(Makefile|compose\.ya?ml|package\.json|pnpm-workspace\.yaml|turbo\.json|tsconfig\.base\.json|eslint\.config\.js|\.prettierrc\.json|\.prettierignore|\.npmrc|\.node-version|\.python-version|uv\.toml|ruff\.toml|\.gitignore|\.gitattributes|CLAUDE\.md|supabase/config\.toml)$|^(scripts|stack|\.github|\.claude|tools/new-service|services/_template[^/]*)/|^(docs/[a-z]+|tests/e2e|tools/gates|tools/probes|fixtures|infra)/README\.md$'

# --- TypeScript: Turborepo resolves the changed workspaces and their dependants. -----------------
# The turbo that ships with these scripts (the pnpm catalog pin); pnpm's when it is not installed.
if [ -x "$SB_KIT_ROOT/node_modules/.bin/turbo" ]; then
  TURBO=("$SB_KIT_ROOT/node_modules/.bin/turbo" --skip-infer)
else
  TURBO=(pnpm exec turbo)
fi
TASKS=(lint typecheck test)
[ "$ACCEPTANCE" = 1 ] && TASKS+=(test:acceptance)
TS_PACKAGES=""
TURBO_FILTERS=()
if [ -f package.json ] && [ -f turbo.json ]; then
  if [ -n "$BASE" ] && [ "$FIXTURES_CHANGED" = 0 ]; then
    TURBO_FILTERS+=("--filter=...[$BASE]")
    # A here-string, not a pipe: grep -q stops at the first match, and a writer still holding
    # more than a pipe buffer of names would die of SIGPIPE and turn the match into a miss.
    if grep -qE "$ROOT_TOOLING" <<<"$CHANGED" && [ -f tools/repo-checks/package.json ]; then
      TURBO_FILTERS+=("--filter=repo-checks")
    fi
  fi
  TS_PACKAGES="$("${TURBO[@]}" ls ${TURBO_FILTERS[@]+"${TURBO_FILTERS[@]}"} --output json 2>/dev/null |
    node -e 'const j = JSON.parse(require("fs").readFileSync(0, "utf8"));
             console.log(j.packages.items.map((p) => p.name).sort().join(" "));')" ||
    sb_die "turbo could not list the workspaces (run pnpm install)"
fi

# --- Python: the nearest pyproject.toml above each changed file, plus path dependants. ----------
# Every project extends ruff.toml and follows .python-version and uv.toml.
PY_SHARED='^(ruff\.toml|\.python-version|uv\.toml)$'
PY_CHANGED=()
if [ -z "$BASE" ] || [ "$FIXTURES_CHANGED" = 1 ] || grep -qE "$PY_SHARED" <<<"$CHANGED"; then
  PY_PROJECTS="$(python3 "$SB_LIB_DIR/py_projects.py" "$ROOT" --all)"
else
  declare -A SEEN=()
  while IFS= read -r file; do
    # Parameter expansion, not dirname: a large change list must not fork per file.
    dir="$file"
    while [[ "$dir" == */* ]]; do
      dir="${dir%/*}"
      if [ -f "$dir/pyproject.toml" ]; then
        if [ -z "${SEEN[$dir]:-}" ]; then
          SEEN[$dir]=1
          PY_CHANGED+=("$dir")
        fi
        break
      fi
    done
  done <<<"$CHANGED"
  if [ "${#PY_CHANGED[@]}" -gt 0 ]; then
    PY_PROJECTS="$(python3 "$SB_LIB_DIR/py_projects.py" "$ROOT" "${PY_CHANGED[@]}")"
  else
    PY_PROJECTS=""
  fi
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

# The acceptance suites talk to the local stack, each under this checkout's test namespace.
if [ "$ACCEPTANCE" = 1 ]; then
  exports="$("$SB_SCRIPTS_DIR/test-namespace.sh")" || sb_die "scripts/test-namespace.sh failed"
  eval "$exports"
  exports="$("$SB_SCRIPTS_DIR/stack-env.sh")" || sb_die "scripts/stack-env.sh failed"
  eval "$exports"
fi

if [ -n "$TS_PACKAGES" ]; then
  echo "== turbo ${TASKS[*]}"
  filters=()
  for pkg in $TS_PACKAGES; do filters+=("--filter=$pkg"); done
  if ! "${TURBO[@]}" run lint typecheck test "${filters[@]}" --continue --output-logs=errors-only; then
    FAILED+=("turbo")
  fi
  # Acceptance suites share one local stack, so they run one package at a time.
  if [ "$ACCEPTANCE" = 1 ] &&
    ! "${TURBO[@]}" run test:acceptance "${filters[@]}" --concurrency=1 --continue --output-logs=full; then
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
