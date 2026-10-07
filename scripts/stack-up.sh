#!/usr/bin/env bash
# make up: the local stack in one command (Redpanda, ClickHouse and SeaweedFS through compose.yaml,
# Supabase through its CLI), waiting until every service answers. Running it again leaves a
# running stack as it is.
#
#   IMAGE_REGISTRY=upstream  pull the compose images from their publishers (see stack-images.sh)
#   SUPABASE_FULL=1          start every Supabase service (default: db, kong, auth and rest only)
#   IMAGE_PULL_WAIT_SECONDS  keep retrying a failed image pull this long (default 0)
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

ROOT="$(sb_repo_root)"
cd "$ROOT"

command -v docker >/dev/null 2>&1 || sb_die "docker is not installed (make doctor)"
docker info >/dev/null 2>&1 ||
  sb_die "the Docker daemon is not reachable; start it (in a cloud session: docs/orchestration/README.md)"
CLI="$ROOT/node_modules/.bin/supabase"
[ -x "$CLI" ] || sb_die "the Supabase CLI is not installed; run make bootstrap (or pnpm install)"

eval "$("$SB_SCRIPTS_DIR/stack-images.sh")"
echo "make up: compose images from the ${IMAGE_REGISTRY:-default} registries in stack/versions.env" \
  "(IMAGE_REGISTRY=upstream pulls from the publishers instead)"

# IMAGE_PULL_WAIT_SECONDS (CI sets it) keeps retrying a pull that fails, for the minute or two the
# mirror workflow needs after a push that changes stack/versions.env.
pull() {
  local deadline=$((SECONDS + ${IMAGE_PULL_WAIT_SECONDS:-0}))
  until docker pull --quiet "$1" >/dev/null; do
    [ "$SECONDS" -lt "$deadline" ] || return 1
    echo "make up: $1 is not available yet; retrying in 20 s" >&2
    sleep 20
  done
}

for image in "$REDPANDA_IMAGE" "$CLICKHOUSE_IMAGE" "$SEAWEEDFS_IMAGE"; do
  docker image inspect "$image" >/dev/null 2>&1 && continue
  if ! pull "$image"; then
    case "$image" in
      ghcr.io/abdullah95k/*)
        echo "make up: could not pull $image from this repository's GHCR mirror." >&2
        echo "  The mirror packages must be public (a one-time user action, see docs/handoffs/F1.md)," >&2
        echo "  or log in first: docker login ghcr.io. Meanwhile: IMAGE_REGISTRY=upstream make up" >&2
        echo "  (Docker Hub may answer 429 to anonymous pulls from shared addresses)." >&2
        ;;
      *) echo "make up: could not pull $image" >&2 ;;
    esac
    exit 1
  fi
done

"$SB_SCRIPTS_DIR/compose.sh" up --detach --wait --wait-timeout 300

# The bucket every service writes its raw archive to (C2), created once and kept until make down.
eval "$("$SB_SCRIPTS_DIR/stack-env.sh" --no-supabase)"
code="$(curl -s -o /dev/null -w '%{http_code}' -X PUT \
  --aws-sigv4 "aws:amz:${S3_REGION}:s3" --user "${S3_ACCESS_KEY_ID}:${S3_SECRET_ACCESS_KEY}" \
  "${S3_ENDPOINT}/${S3_BUCKET}")"
case "$code" in
  200 | 409) ;;
  *) sb_die "could not create the S3 bucket ${S3_BUCKET} (HTTP $code)" ;;
esac

if "$CLI" status >/dev/null 2>&1; then
  echo "make up: Supabase is already running"
else
  EXCLUDE="realtime,storage-api,imgproxy,mailpit,postgres-meta,studio,edge-runtime,logflare,vector,supavisor"
  if [ "${SUPABASE_FULL:-0}" = 1 ]; then
    "$CLI" start
  else
    "$CLI" start --exclude "$EXCLUDE"
  fi
fi

"$SB_SCRIPTS_DIR/wait-for-stack.sh"
echo "make up: the local stack is up. Connection variables: eval \"\$(scripts/stack-env.sh)\"; a quick round trip: make smoke"
