#!/usr/bin/env bash
# Copies to this repository's GHCR mirror the pinned tag of every stack image whose <NAME>_REPO in
# stack/versions.env points there, from its <NAME>_UPSTREAM, for every platform the upstream
# publishes. Images with an anonymous upstream are left alone. Run by
# .github/workflows/mirror-images.yml after logging in to ghcr.io (and to Docker Hub when its
# secrets exist); needs docker buildx.
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
  if docker buildx imagetools inspect "$repo:$tag" >/dev/null 2>&1; then
    echo "mirror: $repo:$tag is already there"
  else
    echo "mirror: $upstream:$tag -> $repo:$tag"
    docker buildx imagetools create --tag "$repo:$tag" "$upstream:$tag"
  fi
  MIRRORED=$((MIRRORED + 1))
done
echo "mirror: $MIRRORED image(s) in $PREFIX. New packages are private: make them public once (see docs/handoffs/F1.md)."
