#!/usr/bin/env bash
# make smoke: one quick round trip through every service of the running local stack, using only
# the variables scripts/stack-env.sh prints. CI runs it after make check.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

ROOT="$(sb_repo_root)"
cd "$ROOT"
eval "$("$SB_SCRIPTS_DIR/stack-env.sh")"
[ -n "${SUPABASE_URL:-}" ] || sb_die "Supabase is not running; run make up first"
ID="smoke_$(date +%s)_$$"

ok() {
  echo "smoke: ok   $*"
}

# Redpanda: a topic, one record produced and consumed through the external listener, the HTTP
# proxy and the schema registry from the host.
rpk() {
  "$SB_SCRIPTS_DIR/compose.sh" exec -T redpanda rpk -X brokers=localhost:19092 "$@"
}
rpk topic create "$ID" --partitions 1 >/dev/null
echo "hello" | rpk topic produce "$ID" >/dev/null
got="$(rpk topic consume "$ID" --num 1 --format '%v')"
rpk topic delete "$ID" >/dev/null
[ "$got" = "hello" ] || sb_die "redpanda: produced hello, consumed '$got'"
curl -sf "$KAFKA_HTTP_PROXY_URL/topics" >/dev/null || sb_die "redpanda: the HTTP proxy does not answer"
curl -sf "$SCHEMA_REGISTRY_URL/subjects" >/dev/null || sb_die "redpanda: the schema registry does not answer"
ok "redpanda ($KAFKA_BROKERS): produce and consume, HTTP proxy, schema registry"

# ClickHouse over HTTP with the stack's user.
got="$(curl -sf -u "$CLICKHOUSE_USER:$CLICKHOUSE_PASSWORD" --data-binary 'SELECT 1' "$CLICKHOUSE_URL/")"
[ "$got" = "1" ] || sb_die "clickhouse: SELECT 1 returned '$got'"
ok "clickhouse ($CLICKHOUSE_URL): SELECT 1"

# S3 (SeaweedFS): put, get and delete an object in the stack's bucket.
s3() {
  curl -sf --aws-sigv4 "aws:amz:${S3_REGION}:s3" --user "${S3_ACCESS_KEY_ID}:${S3_SECRET_ACCESS_KEY}" "$@"
}
s3 -X PUT --data-binary "hello" "$S3_ENDPOINT/$S3_BUCKET/$ID.txt" >/dev/null
got="$(s3 "$S3_ENDPOINT/$S3_BUCKET/$ID.txt")"
s3 -X DELETE "$S3_ENDPOINT/$S3_BUCKET/$ID.txt" >/dev/null
[ "$got" = "hello" ] || sb_die "s3: wrote hello, read '$got'"
ok "seaweedfs ($S3_ENDPOINT, bucket $S3_BUCKET): put, get, delete"

# Supabase: Postgres, the auth service and the REST API through the gateway.
got="$(docker exec supabase_db_securebrand psql -U postgres -d postgres -tAc 'select 1')"
[ "$got" = "1" ] || sb_die "postgres: select 1 returned '$got'"
curl -sf -H "apikey: $SUPABASE_ANON_KEY" "$SUPABASE_URL/auth/v1/health" >/dev/null ||
  sb_die "supabase: the auth service does not answer"
curl -sf -H "apikey: $SUPABASE_ANON_KEY" -H "Authorization: Bearer $SUPABASE_ANON_KEY" "$SUPABASE_URL/rest/v1/" >/dev/null ||
  sb_die "supabase: the REST API does not answer"
ok "supabase ($SUPABASE_URL): postgres select 1, auth health, REST"
