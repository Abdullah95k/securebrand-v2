#!/usr/bin/env bash
# make new-service NAME=<name> [LANG=python]: tools/new-service on the pinned Node (see
# sb_select_node), so the pnpm install it starts accepts package.json's engines whatever node the
# shell runs. pnpm new:service runs the same generator on the shell's node.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

exec node "$SB_KIT_ROOT/tools/new-service/index.mjs" "$@"
