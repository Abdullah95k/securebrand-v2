#!/usr/bin/env bash
# make doctor: checks the toolchain against the pins and names every tool that is missing or at the
# wrong version. Pins: .node-version, package.json packageManager, uv.toml required-version,
# .python-version, the supabase entry of the pnpm catalog; Docker Engine >= 27 with Compose >= 2.30;
# jq (the kit's hooks), git and python3 >= 3.11 (the policy scripts).
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

cd "$SB_KIT_ROOT"
PROBLEMS=0
ok() { printf 'ok    %s\n' "$*"; }
bad() {
  printf 'FAIL  %s\n' "$*"
  PROBLEMS=$((PROBLEMS + 1))
}
# version_ge A B: A >= B for dotted versions
version_ge() { [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -1)" = "$2" ]; }

NODE_PIN="$(tr -d '[:space:]' <.node-version)"
PNPM_PIN="$(sed -n 's/.*"packageManager": *"pnpm@\([0-9.]*\)".*/\1/p' package.json)"
UV_RANGE="$(sed -n 's/^required-version *= *"\(.*\)"/\1/p' uv.toml)"
UV_MIN="$(printf '%s' "$UV_RANGE" | sed -n 's/^>=\([0-9.]*\).*/\1/p')"
UV_BELOW="$(printf '%s' "$UV_RANGE" | sed -n 's/.*<\([0-9.]*\)$/\1/p')"
PYTHON_PIN="$(tr -d '[:space:]' <.python-version)"
SUPABASE_PIN="$(sed -n 's/^ *supabase: *\([0-9.]*\).*/\1/p' pnpm-workspace.yaml)"

if ! command -v node >/dev/null 2>&1; then
  bad "node: missing (expected $NODE_PIN; make bootstrap installs it with nvm)"
else
  found="$(node --version 2>/dev/null | sed 's/^v//')"
  if [ "$found" = "$NODE_PIN" ]; then ok "node $found"; else bad "node: expected $NODE_PIN, found $found (make bootstrap, or nvm install $NODE_PIN)"; fi
fi

# The make targets run the node above (nvm's pin when the shell runs another), but the pnpm
# commands a user types (pnpm new:service, pnpm --filter) run the shell's, and pnpm refuses a node
# outside package.json's engines.
shell_node="$(PATH="$SB_CALLER_PATH" command -v node 2>/dev/null || true)"
if [ "$shell_node" != "$(command -v node 2>/dev/null || true)" ]; then
  found="$([ -n "$shell_node" ] && "$shell_node" --version 2>/dev/null | sed 's/^v//' || true)"
  if [ "$found" = "$NODE_PIN" ]; then
    ok "node $found on your PATH"
  else
    bad "node on your PATH: ${found:-none}${shell_node:+ ($shell_node)}, not $NODE_PIN; the make targets use nvm's, but pnpm commands you run yourself refuse it: nvm use $NODE_PIN switches this shell"
  fi
fi

if ! command -v pnpm >/dev/null 2>&1; then
  bad "pnpm: missing (expected $PNPM_PIN; corepack enable, or npm install -g pnpm@$PNPM_PIN)"
else
  found="$(pnpm --version 2>/dev/null || echo unknown)"
  if [ "$found" = "$PNPM_PIN" ]; then ok "pnpm $found"; else bad "pnpm: expected $PNPM_PIN, found $found"; fi
fi

if ! command -v uv >/dev/null 2>&1; then
  bad "uv: missing (expected $UV_RANGE; https://docs.astral.sh/uv/getting-started/installation/)"
else
  found="$(uv --version 2>/dev/null | awk '{print $2}')"
  if version_ge "$found" "$UV_MIN" && ! version_ge "$found" "$UV_BELOW"; then
    ok "uv $found"
  else
    bad "uv: expected $UV_RANGE, found $found (uv self update $UV_MIN)"
  fi
  if uv python find "$PYTHON_PIN" >/dev/null 2>&1; then
    ok "python $PYTHON_PIN (uv)"
  else
    bad "python: $PYTHON_PIN not installed (uv python install $PYTHON_PIN)"
  fi
fi

if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
  ok "python3 $(python3 -c 'import platform; print(platform.python_version())') (policy scripts)"
else
  bad "python3: 3.11 or newer missing (the policy and check scripts use its tomllib)"
fi

if [ -x node_modules/.bin/supabase ]; then
  found="$(node_modules/.bin/supabase --version 2>/dev/null | tail -1 || echo unknown)"
  if [ "$found" = "$SUPABASE_PIN" ]; then ok "supabase CLI $found"; else bad "supabase CLI: expected $SUPABASE_PIN, found $found (pnpm install)"; fi
else
  bad "supabase CLI: missing (pnpm install puts $SUPABASE_PIN in node_modules/.bin)"
fi

if ! command -v docker >/dev/null 2>&1; then
  bad "docker: missing (Docker Engine 27 or newer with the compose plugin)"
elif ! server="$(docker version --format '{{.Server.Version}}' 2>/dev/null)"; then
  bad "docker: the daemon is not reachable (start Docker; cloud sessions: docs/orchestration/README.md)"
else
  if version_ge "$server" 27; then ok "docker $server"; else bad "docker: expected 27 or newer, found $server"; fi
  compose="$(docker compose version --short 2>/dev/null | sed 's/^v//' || true)"
  if [ -n "$compose" ] && version_ge "$compose" 2.30; then ok "docker compose $compose"; else bad "docker compose: expected 2.30 or newer, found ${compose:-none}"; fi
fi

for tool in git jq curl; do
  if command -v "$tool" >/dev/null 2>&1; then ok "$tool"; else bad "$tool: missing"; fi
done

if [ "$PROBLEMS" -gt 0 ]; then
  echo "make doctor: $PROBLEMS problem(s)" >&2
  exit 1
fi
echo "make doctor: the toolchain matches the pins"
