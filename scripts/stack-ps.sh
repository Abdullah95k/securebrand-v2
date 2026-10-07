#!/usr/bin/env bash
# make ps: the local stack's containers and Supabase's status.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

ROOT="$(sb_repo_root)"
cd "$ROOT"
"$SB_SCRIPTS_DIR/compose.sh" ps
"$ROOT/node_modules/.bin/supabase" status || true
