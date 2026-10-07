#!/usr/bin/env bash
# Prints the test namespace of this checkout as `export` lines, for
#   eval "$(scripts/test-namespace.sh)"
#
# Parallel worktrees share one local stack, so every test names its Kafka topics, Postgres
# schema and database, ClickHouse database and S3 bucket after TEST_NAMESPACE. The namespace is,
# in order: TEST_NAMESPACE when set by hand; ci_<run id>_<attempt> in GitHub Actions; the name of
# the linked worktree (claude --worktree FB2 gives fb2); the branch (sb/C11 gives sb_c11); else
# "local". It is lowercase [a-z0-9_], starts with a letter, has at most 32 characters, and long
# names end in a short hash so two worktrees never share one.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

sanitize() {
  local raw="$1" s hash
  s="$(printf '%s' "$raw" | LC_ALL=C tr '[:upper:]' '[:lower:]' | LC_ALL=C sed -E 's/[^a-z0-9]+/_/g; s/^_+//; s/_+$//')"
  [ -n "$s" ] || return 0
  case "$s" in [a-z]*) ;; *) s="ns_$s" ;; esac
  if [ "${#s}" -gt 32 ]; then
    hash="$(printf '%s' "$raw" | git hash-object --stdin | cut -c1-6)"
    s="$(printf '%s' "${s:0:25}" | sed -E 's/_+$//')_$hash"
  fi
  printf '%s' "$s"
}

ns=""
if [ -n "${TEST_NAMESPACE:-}" ]; then
  ns="$(sanitize "$TEST_NAMESPACE")"
elif [ -n "${GITHUB_RUN_ID:-}" ]; then
  ns="$(sanitize "ci_${GITHUB_RUN_ID}_${GITHUB_RUN_ATTEMPT:-1}")"
elif git rev-parse --git-dir >/dev/null 2>&1; then
  git_dir="$(cd "$(git rev-parse --git-dir)" && pwd -P)"
  common_dir="$(cd "$(git rev-parse --git-common-dir)" && pwd -P)"
  if [ "$git_dir" != "$common_dir" ]; then
    ns="$(sanitize "$(basename "$(git rev-parse --show-toplevel)")")"
  else
    branch="$(git symbolic-ref --short -q HEAD || true)"
    [ -z "$branch" ] || ns="$(sanitize "$branch")"
  fi
fi
[ -n "$ns" ] || ns="local"

sb_export TEST_NAMESPACE "$ns"
sb_export TEST_TOPIC_PREFIX "$ns."
sb_export TEST_PG_SCHEMA "test_$ns"
sb_export TEST_PG_DATABASE "test_$ns"
sb_export TEST_CH_DATABASE "test_$ns"
sb_export TEST_S3_BUCKET "test-${ns//_/-}"
