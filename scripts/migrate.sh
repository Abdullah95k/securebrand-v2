#!/usr/bin/env bash
# make migrate [ENGINE=postgres|clickhouse]: applies the migrations to the running local stack.
# Each engine has its own hook so F3 (Postgres) and F8 (ClickHouse) each change one file.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

case "${1:-all}" in
  all) ENGINES=(postgres clickhouse) ;;
  postgres | clickhouse) ENGINES=("$1") ;;
  *) echo "usage: make migrate [ENGINE=postgres|clickhouse]" >&2; exit 2 ;;
esac
for engine in "${ENGINES[@]}"; do
  "$SB_SCRIPTS_DIR/migrate/$engine.sh"
done
