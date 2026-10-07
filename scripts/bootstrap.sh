#!/usr/bin/env bash
# make bootstrap: installs the pinned toolchain and every dependency, then runs make doctor.
# Safe to run again. Node comes through nvm when it is installed (NVM_DIR, ~/.nvm or /opt/nvm);
# pnpm switches itself to package.json's packageManager; uv updates itself to the pinned version;
# Python comes through uv.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

cd "$SB_KIT_ROOT"
NODE_PIN="$(tr -d '[:space:]' <.node-version)"
PNPM_PIN="$(sed -n 's/.*"packageManager": *"pnpm@\([0-9.]*\)".*/\1/p' package.json)"
UV_MIN="$(sed -n 's/^required-version *= *">=\([0-9.]*\).*/\1/p' uv.toml)"
UV_BELOW="$(sed -n 's/^required-version *= *".*<\([0-9.]*\)"$/\1/p' uv.toml)"
PYTHON_PIN="$(tr -d '[:space:]' <.python-version)"

# 1. Node.
if [ "$(node --version 2>/dev/null)" != "v$NODE_PIN" ]; then
  nvm_sh=""
  for dir in "${NVM_DIR:-}" "$HOME/.nvm" /opt/nvm; do
    if [ -n "$dir" ] && [ -s "$dir/nvm.sh" ]; then
      nvm_sh="$dir/nvm.sh"
      break
    fi
  done
  if [ -n "$nvm_sh" ]; then
    echo "bootstrap: installing Node $NODE_PIN with nvm"
    # shellcheck disable=SC1090
    (set +eu && . "$nvm_sh" && nvm install "$NODE_PIN" >/dev/null)
    sb_select_node
  else
    sb_die "Node $NODE_PIN is needed: install it with nvm, fnm, volta or mise (they read .node-version), then run make bootstrap again"
  fi
fi
echo "bootstrap: node $(node --version)"

# 2. pnpm (it then runs the version in packageManager by itself).
if ! command -v pnpm >/dev/null 2>&1; then
  echo "bootstrap: installing pnpm $PNPM_PIN"
  npm install --global --no-fund --no-audit "pnpm@$PNPM_PIN" >/dev/null
fi
echo "bootstrap: pnpm $(pnpm --version)"

# 3. uv and Python.
if ! command -v uv >/dev/null 2>&1; then
  sb_die "uv $UV_MIN is needed: https://docs.astral.sh/uv/getting-started/installation/ (then make bootstrap again)"
fi
version_ge() { [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -1)" = "$2" ]; }
current="$(uv --version | awk '{print $2}')"
if ! version_ge "$current" "$UV_MIN" || version_ge "$current" "$UV_BELOW"; then
  echo "bootstrap: uv $current -> $UV_MIN"
  uv self update "$UV_MIN" || sb_die "uv could not update itself; install uv $UV_MIN by the method you used before"
fi
uv python install "$PYTHON_PIN"

# 4. Dependencies.
pnpm install --frozen-lockfile
while IFS= read -r project; do
  [ -n "$project" ] || continue
  echo "bootstrap: uv sync in $project"
  (cd "$project" && uv sync --locked --quiet)
done < <(python3 "$SB_LIB_DIR/py_projects.py" "$SB_KIT_ROOT" --all)

"$SB_SCRIPTS_DIR/doctor.sh"
