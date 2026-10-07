#!/usr/bin/env bash
# make ns-clean: removes everything tests created under this checkout's TEST_NAMESPACE on the local
# stack: Kafka topics named <namespace>.*, the Postgres schema and database test_<namespace>, the
# ClickHouse database test_<namespace> and the S3 bucket test-<namespace>. Nothing outside the
# namespace is touched. TEST_NAMESPACE=<name> make ns-clean cleans another namespace.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

ROOT="$(sb_repo_root)"
cd "$ROOT"
eval "$("$SB_SCRIPTS_DIR/test-namespace.sh")"
eval "$("$SB_SCRIPTS_DIR/stack-env.sh")"
echo "make ns-clean: namespace $TEST_NAMESPACE"

# Kafka topics with the namespace's prefix (regular expression, dots escaped).
prefix_re="^${TEST_TOPIC_PREFIX//./\\.}"
topics="$("$SB_SCRIPTS_DIR/compose.sh" exec -T redpanda rpk topic list -X brokers=localhost:19092 |
  awk 'NR > 1 { print $1 }' | grep -E "$prefix_re" || true)"
if [ -n "$topics" ]; then
  # shellcheck disable=SC2086 # one argument per topic
  "$SB_SCRIPTS_DIR/compose.sh" exec -T redpanda rpk topic delete -X brokers=localhost:19092 $topics >/dev/null
fi
echo "  topics:     $(printf '%s' "$topics" | grep -c . || true) removed (${TEST_TOPIC_PREFIX}*)"

# Postgres: the schema in the main database, then the namespace's own database.
docker exec supabase_db_securebrand psql -U postgres -d postgres -v ON_ERROR_STOP=1 -q \
  -c "drop schema if exists \"${TEST_PG_SCHEMA}\" cascade" \
  -c "drop database if exists \"${TEST_PG_DATABASE}\" with (force)" >/dev/null
echo "  postgres:   schema ${TEST_PG_SCHEMA} and database ${TEST_PG_DATABASE} removed"

# ClickHouse.
curl -sf -u "$CLICKHOUSE_USER:$CLICKHOUSE_PASSWORD" \
  --data-binary "DROP DATABASE IF EXISTS \`${TEST_CH_DATABASE}\`" "$CLICKHOUSE_URL/" >/dev/null
echo "  clickhouse: database ${TEST_CH_DATABASE} removed"

# S3: the bucket with its objects and its storage collection.
"$SB_SCRIPTS_DIR/compose.sh" exec -T seaweedfs sh -c \
  "echo 's3.bucket.delete -name ${TEST_S3_BUCKET}' | weed shell -master=127.0.0.1:9333" >/dev/null 2>&1 || true
code="$(curl -s -o /dev/null -w '%{http_code}' -I \
  --aws-sigv4 "aws:amz:${S3_REGION}:s3" --user "${S3_ACCESS_KEY_ID}:${S3_SECRET_ACCESS_KEY}" \
  "${S3_ENDPOINT}/${TEST_S3_BUCKET}")"
[ "$code" = 404 ] || sb_die "the S3 bucket ${TEST_S3_BUCKET} is still there (HTTP $code)"
echo "  s3:         bucket ${TEST_S3_BUCKET} removed"
