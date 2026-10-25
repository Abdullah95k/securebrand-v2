#!/usr/bin/env bash
# Starts the local Supabase unless it runs (db, kong, auth and rest; SUPABASE_FULL=1: every service).
# A start that fails because a host port is in use is retried once, after supabase stop and
# SUPABASE_RETRY_WAIT_SECONDS (default 60, a TCP TIME_WAIT): an outbound connection can hold any
# port in 32768-60999, and supabase/config.toml uses 54320-54329 (CI reserves them, ci.yml).
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
ROOT="$(sb_repo_root)"; cd "$ROOT"
CLI="$ROOT/node_modules/.bin/supabase"
[ -x "$CLI" ] || sb_die "the Supabase CLI is not installed; run make bootstrap"
if "$CLI" status >/dev/null 2>&1; then echo "make up: Supabase is already running"; exit 0; fi
START=(start)
[ "${SUPABASE_FULL:-0}" = 1 ] || START+=(--exclude "realtime,storage-api,imgproxy,mailpit,postgres-meta,studio,edge-runtime,logflare,vector,supavisor")
LOG="$(mktemp)"; trap 'rm -f "$LOG"' EXIT
start() { "$CLI" "${START[@]}" 2>&1 | tee "$LOG"; }
start && exit 0
grep -q 'address already in use' "$LOG" || sb_die "supabase start failed (output above)"
wait="${SUPABASE_RETRY_WAIT_SECONDS:-60}"
echo "make up: a Supabase port is in use (often a short-lived outbound connection); supabase stop, then one more start in ${wait} s" >&2
"$CLI" stop || true
sleep "$wait"
start || sb_die "supabase start failed twice: a port of supabase/config.toml is in use (ss -tanp | grep ':5432[0-9]')"
