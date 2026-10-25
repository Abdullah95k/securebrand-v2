#!/usr/bin/env bash
# make bootstrap: installs the pinned toolchain and every dependency, then runs make doctor.
# Safe to run again. Node comes through nvm when it is installed (NVM_DIR, ~/.nvm, /opt/nvm or
# /usr/local/nvm), which downloads only when the pin is missing; pnpm switches itself to
# package.json's packageManager; uv reaches the pinned version through uv self update, or through
# pip --user when pip installed it; Python comes through uv.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

cd "$SB_KIT_ROOT"
NODE_PIN="$(tr -d '[:space:]' <.node-version)"
PNPM_PIN="$(sed -n 's/.*"packageManager": *"pnpm@\([0-9.]*\)".*/\1/p' package.json)"
UV_MIN="$(sed -n 's/^required-version *= *">=\([0-9.]*\).*/\1/p' uv.toml)"
UV_BELOW="$(sed -n 's/^required-version *= *".*<\([0-9.]*\)"$/\1/p' uv.toml)"
PYTHON_PIN="$(tr -d '[:space:]' <.python-version)"

# 1. Node. The scripts find nvm's pin by themselves (sb_select_node); the shell that runs make
#    bootstrap starts on it in new shells that load nvm once it is nvm's default.
shell_node="$(PATH="$SB_CALLER_PATH" node --version 2>/dev/null || true)"
if [ "$(node --version 2>/dev/null)" != "v$NODE_PIN" ] || [ "$shell_node" != "v$NODE_PIN" ]; then
  nvm_dir=""
  for dir in "${NVM_DIR:-}" "$HOME/.nvm" /opt/nvm /usr/local/nvm; do
    if [ -n "$dir" ] && [ -s "$dir/nvm.sh" ]; then nvm_dir="$dir"; break; fi
  done
  if [ -n "$nvm_dir" ]; then
    # nvm install downloads nodejs.org's index even for an installed version (nvm 0.39): only when missing.
    if [ ! -x "$nvm_dir/versions/node/v$NODE_PIN/bin/node" ]; then
      echo "bootstrap: installing Node $NODE_PIN with nvm (downloads from nodejs.org)"
      # shellcheck disable=SC1090
      (set +eu && . "$nvm_dir/nvm.sh" && nvm install "$NODE_PIN" >/dev/null) ||
        sb_die "nvm could not install Node $NODE_PIN; it needs nodejs.org: run make bootstrap again with network"
    fi
    if [ "$(tr -d '[:space:]' 2>/dev/null <"$nvm_dir/alias/default")" != "$NODE_PIN" ]; then
      echo "bootstrap: making Node $NODE_PIN nvm's default"
      # shellcheck disable=SC1090
      (set +eu && . "$nvm_dir/nvm.sh" && nvm alias default "$NODE_PIN" >/dev/null) ||
        sb_die "nvm alias default $NODE_PIN failed"
    fi
    sb_select_node
  elif [ "$(node --version 2>/dev/null)" != "v$NODE_PIN" ]; then
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
uv_ok() { version_ge "$1" "$UV_MIN" && ! version_ge "$1" "$UV_BELOW"; }
uv_version() { uv --version 2>/dev/null | awk '{print $2}' || true; }
current="$(uv_version)"
if ! uv_ok "$current"; then
  echo "bootstrap: uv $current -> $UV_MIN"
  if uv self update "$UV_MIN"; then
    :
  elif python3 -m pip show uv >/dev/null 2>&1; then
    echo "bootstrap: uv came from pip; installing uv $UV_MIN with pip --user"
    python3 -m pip install --user --quiet --upgrade "uv==$UV_MIN" ||
      sb_die "pip could not install uv $UV_MIN: run python3 -m pip install --user --upgrade 'uv==$UV_MIN', then make bootstrap again"
  else
    sb_die "uv $current could not update itself and pip does not own it: install uv $UV_MIN with the official installer (curl -LsSf https://astral.sh/uv/$UV_MIN/install.sh | sh) or your package manager, then make bootstrap again"
  fi
  hash -r
  current="$(uv_version)"
  if ! uv_ok "$current" && [ -x "$HOME/.local/bin/uv" ] && uv_ok "$("$HOME/.local/bin/uv" --version | awk '{print $2}')"; then
    PATH="$HOME/.local/bin:$PATH"; export PATH; hash -r; current="$(uv_version)"
    echo "bootstrap: uv $current is in ~/.local/bin, behind another uv on your PATH: put ~/.local/bin first"
  fi
  uv_ok "$current" || sb_die "uv is still $current ($(command -v uv)) after the update; install uv $UV_MIN, then make bootstrap again"
fi
echo "bootstrap: uv $current"
uv python install "$PYTHON_PIN"

# 4. Dependencies.
pnpm install --frozen-lockfile
while IFS= read -r project; do
  [ -n "$project" ] || continue
  echo "bootstrap: uv sync in $project"
  (cd "$project" && uv sync --locked --quiet)
done < <(python3 "$SB_LIB_DIR/py_projects.py" "$SB_KIT_ROOT" --all)

# A script cannot switch the shell that started it: doctor checks the toolchain the scripts run,
# and the switch for the shell comes last (make doctor, run from the shell, checks both).
status=0
SB_CALLER_PATH="$PATH" "$SB_SCRIPTS_DIR/doctor.sh" || status=$?
if [ "$shell_node" != "v$NODE_PIN" ]; then
  echo "bootstrap: this shell runs ${shell_node:-no node}, and the pnpm commands you type need" \
    "$NODE_PIN: nvm use $NODE_PIN switches it"
fi
exit "$status"
