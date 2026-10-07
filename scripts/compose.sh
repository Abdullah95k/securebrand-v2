#!/usr/bin/env bash
# docker compose for the local stack, with the image pins of stack/versions.env (and
# IMAGE_REGISTRY) set: scripts/compose.sh ps, scripts/compose.sh logs redpanda, ...
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

cd "$(sb_repo_root)"
eval "$("$SB_SCRIPTS_DIR/stack-images.sh")"
exec docker compose "$@"
