#!/usr/bin/env bash
# Prints the image of every local-stack service as export lines (<NAME>_REPO, <NAME>_TAG,
# <NAME>_IMAGE), from stack/versions.env:
#   IMAGE_REGISTRY unset or "default"  each image from its <NAME>_REPO (an anonymous upstream or
#                                      this repository's GHCR mirror)
#   IMAGE_REGISTRY=upstream            each image from the publisher's registry (<NAME>_UPSTREAM);
#                                      Docker Hub may answer 429 to anonymous pulls
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

case "${IMAGE_REGISTRY:-default}" in
  default) FIELD=REPO ;;
  upstream) FIELD=UPSTREAM ;;
  *) sb_die "IMAGE_REGISTRY must be unset, default or upstream, not '${IMAGE_REGISTRY}'" ;;
esac

VERSIONS="$(sb_repo_root)/stack/versions.env"
[ -f "$VERSIONS" ] || sb_die "$VERSIONS is missing"

declare -A PIN=()
NAMES=()
while IFS='=' read -r key value; do
  PIN[$key]="$value"
  case "$key" in *_TAG) NAMES+=("${key%_TAG}") ;; esac
done < <(grep -E '^[A-Z0-9_]+=' "$VERSIONS")

for name in "${NAMES[@]}"; do
  repo="${PIN[${name}_${FIELD}]:-}"
  [ -n "$repo" ] || sb_die "stack/versions.env has ${name}_TAG but no ${name}_${FIELD}"
  sb_export "${name}_REPO" "$repo"
  sb_export "${name}_TAG" "${PIN[${name}_TAG]}"
  sb_export "${name}_IMAGE" "$repo:${PIN[${name}_TAG]}"
done
