#!/usr/bin/env bash
# Copies to this repository's GHCR mirror the pinned tag of every stack image whose <NAME>_REPO in
# stack/versions.env points there, from its <NAME>_UPSTREAM, for every platform the upstream
# publishes. Images with an anonymous upstream are left alone. Run by
# .github/workflows/mirror-images.yml after logging in to ghcr.io (and to Docker Hub when its
# secrets exist); needs docker buildx.
#
# A tag already in the mirror is compared with its upstream by manifest digest (a copy keeps the
# digest). When they differ (the upstream was retagged, or a branch copied from a wrong upstream),
# it fails and names both digests; only MIRROR_REPLACE=1, which the workflow sets on main, where
# stack/versions.env is reviewed, copies the upstream over it.
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

ROOT="$(sb_repo_root)"
cd "$ROOT"
[ -n "${GITHUB_REPOSITORY:-}" ] || sb_die "GITHUB_REPOSITORY is not set (owner/repository of the mirror)"
PREFIX="ghcr.io/$(printf '%s' "$GITHUB_REPOSITORY" | tr '[:upper:]' '[:lower:]')/"

declare -A PIN=()
NAMES=()
while IFS='=' read -r key value; do
  PIN[$key]="$value"
  case "$key" in *_TAG) NAMES+=("${key%_TAG}") ;; esac
done < <(grep -E '^[A-Z0-9_]+=' stack/versions.env)

# The manifest digest of an image reference; nothing when the registry does not have it.
digest() {
  docker buildx imagetools inspect "$1" --format '{{.Manifest.Digest}}' 2>/dev/null || true
}

MIRRORED=0
for name in "${NAMES[@]}"; do
  repo="${PIN[${name}_REPO]}"
  tag="${PIN[${name}_TAG]}"
  upstream="${PIN[${name}_UPSTREAM]:-}"
  case "$repo" in
    "$PREFIX"*) ;;
    ghcr.io/*/securebrand-v2/*) sb_die "${name}_REPO=$repo mirrors into another repository than $GITHUB_REPOSITORY" ;;
    *)
      echo "mirror: $name comes from $repo (anonymous upstream); nothing to copy"
      continue
      ;;
  esac
  [ -n "$upstream" ] || sb_die "stack/versions.env names no ${name}_UPSTREAM to copy $repo from"
  want="$(digest "$upstream:$tag")"
  if [ -z "$want" ]; then
    docker buildx imagetools inspect "$upstream:$tag" >/dev/null || true # the registry's answer
    sb_die "cannot read $upstream:$tag (${name}_UPSTREAM and ${name}_TAG in stack/versions.env)"
  fi
  have="$(digest "$repo:$tag")"
  if [ "$have" = "$want" ]; then
    echo "mirror: $repo:$tag is already there ($want)"
  elif [ -n "$have" ] && [ "${MIRROR_REPLACE:-}" != 1 ]; then
    sb_die "$repo:$tag holds $have, but $upstream:$tag is $want; check which is right, then run the mirror workflow on main, which replaces it"
  else
    echo "mirror: $upstream:$tag ($want) -> $repo:$tag${have:+ (replacing $have)}"
    docker buildx imagetools create --tag "$repo:$tag" "$upstream:$tag"
  fi
  MIRRORED=$((MIRRORED + 1))
done
echo "mirror: $MIRRORED image(s) in $PREFIX. New packages are private: make them public once (see docs/handoffs/F1.md)."
