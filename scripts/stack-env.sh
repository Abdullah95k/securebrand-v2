#!/usr/bin/env bash
# Prints the connection variables of the local stack as export lines:
#   eval "$(scripts/stack-env.sh)"
#
# Ports are those compose.yaml publishes; the fixed development credentials come from
# stack/local.env. The Supabase URL and keys are read live from `supabase status` and never
# written to a file. With --no-supabase, or when Supabase is not running, SUPABASE_* are left out
# (with a note on stderr). make test, make check, make e2e and make smoke evaluate this.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

SUPABASE=1
for arg in "$@"; do
  case "$arg" in
    --no-supabase) SUPABASE=0 ;;
    *) echo "usage: scripts/stack-env.sh [--no-supabase]" >&2; exit 2 ;;
  esac
done

ROOT="$(sb_repo_root)"
declare -A LOCAL=()
while IFS='=' read -r key value; do
  LOCAL[$key]="$value"
done < <(grep -E '^[A-Z0-9_]+=' "$ROOT/stack/local.env")

sb_export KAFKA_BROKERS "localhost:19092"
sb_export SCHEMA_REGISTRY_URL "http://localhost:18081"
sb_export KAFKA_HTTP_PROXY_URL "http://localhost:18082"
sb_export REDPANDA_ADMIN_URL "http://localhost:9644"
sb_export CLICKHOUSE_URL "http://localhost:8123"
sb_export CLICKHOUSE_NATIVE_ADDR "localhost:9000"
sb_export CLICKHOUSE_USER "${LOCAL[CLICKHOUSE_USER]}"
sb_export CLICKHOUSE_PASSWORD "${LOCAL[CLICKHOUSE_PASSWORD]}"
sb_export S3_ENDPOINT "http://localhost:8333"
sb_export S3_REGION "${LOCAL[S3_REGION]}"
sb_export S3_ACCESS_KEY_ID "${LOCAL[S3_ACCESS_KEY_ID]}"
sb_export S3_SECRET_ACCESS_KEY "${LOCAL[S3_SECRET_ACCESS_KEY]}"
sb_export S3_BUCKET "${LOCAL[S3_BUCKET]}"
sb_export S3_FORCE_PATH_STYLE "true"

[ "$SUPABASE" = 1 ] || exit 0
CLI="$ROOT/node_modules/.bin/supabase"
if [ ! -x "$CLI" ]; then
  echo "stack-env: the Supabase CLI is not installed (pnpm install); SUPABASE_* left out" >&2
  exit 0
fi
if ! STATUS="$(cd "$ROOT" && "$CLI" status -o env 2>/dev/null)"; then
  echo "stack-env: Supabase is not running (make up); SUPABASE_* left out" >&2
  exit 0
fi
status_value() {
  printf '%s\n' "$STATUS" | sed -n "s/^$1=\"\{0,1\}\([^\"]*\)\"\{0,1\}$/\1/p" | head -1
}
sb_export SUPABASE_URL "$(status_value API_URL)"
sb_export SUPABASE_DB_URL "$(status_value DB_URL)"
sb_export SUPABASE_ANON_KEY "$(status_value ANON_KEY)"
sb_export SUPABASE_SERVICE_ROLE_KEY "$(status_value SERVICE_ROLE_KEY)"
