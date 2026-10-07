#!/usr/bin/env bash
# Waits until every service of the local stack answers on localhost, or fails after
# STACK_WAIT_SECONDS (default 180) naming the services that did not.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

eval "$("$SB_SCRIPTS_DIR/stack-env.sh")"
DEADLINE=$((SECONDS + ${STACK_WAIT_SECONDS:-180}))

status() {
  curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$@" || true
}

pending() {
  local waiting=()
  [ "$(status "$REDPANDA_ADMIN_URL/v1/status/ready")" = 200 ] || waiting+=("redpanda")
  [ "$(status "$CLICKHOUSE_URL/ping")" = 200 ] || waiting+=("clickhouse")
  [ "$(status "$S3_ENDPOINT/healthz")" = 200 ] || waiting+=("seaweedfs")
  if [ -z "${SUPABASE_URL:-}" ]; then
    waiting+=("supabase")
  else
    [ "$(status -H "apikey: $SUPABASE_ANON_KEY" "$SUPABASE_URL/auth/v1/health")" = 200 ] || waiting+=("supabase-auth")
    [ "$(status -H "apikey: $SUPABASE_ANON_KEY" -H "Authorization: Bearer $SUPABASE_ANON_KEY" "$SUPABASE_URL/rest/v1/")" = 200 ] ||
      waiting+=("supabase-rest")
  fi
  echo "${waiting[*]:-}"
}

while :; do
  left="$(pending)"
  if [ -z "$left" ]; then
    echo "wait-for-stack: redpanda, clickhouse, seaweedfs and supabase answer"
    exit 0
  fi
  if [ "$SECONDS" -ge "$DEADLINE" ]; then
    sb_die "these services did not answer within ${STACK_WAIT_SECONDS:-180} s: $left (make logs SERVICE=<name>)"
  fi
  sleep 2
  # Supabase's keys are known only once it runs.
  [ -n "${SUPABASE_URL:-}" ] || eval "$("$SB_SCRIPTS_DIR/stack-env.sh" 2>/dev/null)"
done
