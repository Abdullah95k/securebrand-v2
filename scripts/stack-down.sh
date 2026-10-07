#!/usr/bin/env bash
# make down: stops the local stack and removes its volumes, so the next make up starts empty.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

ROOT="$(sb_repo_root)"
cd "$ROOT"
docker info >/dev/null 2>&1 || sb_die "the Docker daemon is not reachable"

"$SB_SCRIPTS_DIR/compose.sh" down --volumes --remove-orphans

CLI="$ROOT/node_modules/.bin/supabase"
if [ -x "$CLI" ]; then
  "$CLI" stop --no-backup
else
  echo "make down: the Supabase CLI is not installed; Supabase containers (if any) left running" >&2
fi
echo "make down: the local stack and its volumes are gone"
