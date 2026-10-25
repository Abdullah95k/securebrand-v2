#!/usr/bin/env bash
# make up: the local stack in one command (Redpanda, ClickHouse and SeaweedFS through compose.yaml,
# Supabase through its CLI), waiting until every service answers. Running it again leaves a
# running stack as it is.
#
#   IMAGE_REGISTRY=upstream  pull the compose images from their publishers (see stack-images.sh)
#   SUPABASE_FULL=1          start every Supabase service (default: db, kong, auth and rest only)
#   IMAGE_PULL_WAIT_SECONDS  keep retrying a failed pull of this repository's GHCR mirror this long (default 300; 0 tries once)
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

# A failed pull of this repository's GHCR mirror is retried for IMAGE_PULL_WAIT_SECONDS (default 300;
# CI sets 600): the minute or two the mirror workflow needs to copy a new tag. Another registry's
# short throttle ("Rate exceeded", a 5xx) is retried up to 3 times; a data limit or any other refusal
# does not pass within minutes, so it fails at once with the registry's answer.
# IMAGE_PULL_RETRY_SECONDS spaces the attempts (20).
PULL_WAIT="${IMAGE_PULL_WAIT_SECONDS:-300}"
PULL_ERROR=""
pull() {
  local deadline=$((SECONDS + PULL_WAIT)) tries=0 more
  until PULL_ERROR="$(docker pull --quiet "$1" 2>&1 >/dev/null)"; do
    PULL_ERROR="$(printf '%s\n' "$PULL_ERROR" | tail -1)"
    tries=$((tries + 1))
    case "$1" in
      ghcr.io/abdullah95k/*)
        [ "$SECONDS" -lt "$deadline" ] || return 1
        more=", for up to $((deadline - SECONDS)) s more (IMAGE_PULL_WAIT_SECONDS=$PULL_WAIT)"
        ;;
      *)
        case "$PULL_ERROR" in
          *"Rate exceeded"* | *"unexpected HTTP status: 5"*) [ "$tries" -le 3 ] || return 1 ;;
          *) return 1 ;;
        esac
        more=" (attempt $((tries + 1)) of 4)"
        ;;
    esac
    echo "make up: pulling $1 failed (${PULL_ERROR:-no answer}); retrying in ${IMAGE_PULL_RETRY_SECONDS:-20} s$more" >&2
    sleep "${IMAGE_PULL_RETRY_SECONDS:-20}"
  done
}

for image in "$REDPANDA_IMAGE" "$CLICKHOUSE_IMAGE" "$SEAWEEDFS_IMAGE"; do
  docker image inspect "$image" >/dev/null 2>&1 && continue
  if ! pull "$image"; then
    echo "make up: could not pull $image; the registry answered: ${PULL_ERROR:-nothing} (IMAGE_PULL_WAIT_SECONDS=$PULL_WAIT s applies to this repository's mirror)" >&2
    case "$image" in
      ghcr.io/abdullah95k/*)
        echo "  This repository's GHCR mirror packages must be public (a one-time user action, see docs/handoffs/F1.md)," >&2
        echo "  or log in first: docker login ghcr.io. Meanwhile: IMAGE_REGISTRY=upstream make up" >&2
        echo "  (Docker Hub may answer 429 to anonymous pulls from shared addresses)." >&2
        ;;
      *)
        echo "  Run make up again later (a data limit, toomanyrequests: Data limit exceeded, can last hours)," >&2
        echo "  or IMAGE_REGISTRY=upstream make up to pull from the publishers instead (Docker Hub may answer 429" >&2
        echo "  to anonymous pulls)." >&2
        ;;
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

"$SB_SCRIPTS_DIR/supabase-start.sh"

"$SB_SCRIPTS_DIR/wait-for-stack.sh"
echo "make up: the local stack is up. Connection variables: eval \"\$(scripts/stack-env.sh)\"; a quick round trip: make smoke"
