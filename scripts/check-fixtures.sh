#!/usr/bin/env bash
# Fixtures must stay scrubbed (.claude/rules/fixtures.md). Over the files under fixtures/ that git
# tracks or would add (ignored ones excluded):
#   - no token or signed URL (Meta, Google, JWT, bearer, AWS, Telegram bot, access_token=,
#     X-Amz-Signature=, X-Goog-Signature=, Signature=, sig=, oh=); findings name the file and
#     line, never the match;
#   - no tracked raw/ directory (raw responses stay local and are deleted after scrubbing);
#   - every file of a platform folder is listed in a README.md of its directory or of a parent
#     folder up to fixtures/<platform>/. synthetic-* files and the non-platform folders
#     fixtures/contracts/ (F2) and fixtures/text/ (F7) need no per-file entry.
# Used by make check, make policy and CI.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
[ -d fixtures ] || exit 0

# Tracked files and new ones that are not ignored (what the next commit would hold).
mapfile -d '' FILES < <(git ls-files -z --cached --others --exclude-standard -- fixtures)
[ "${#FILES[@]}" -gt 0 ] || exit 0

PROBLEMS=0
problem() {
  echo "check-fixtures: $*" >&2
  PROBLEMS=$((PROBLEMS + 1))
}

# 1. Tokens and signed URLs.
PATTERNS=(
  'a Meta access token|EAA[A-Za-z0-9]{20,}'
  'a Google API key|AIza[0-9A-Za-z_-]{35}'
  'a JWT|eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}'
  'a bearer token|[Bb]earer[[:space:]]+[A-Za-z0-9._~+/=-]{20,}'
  'an AWS access key|(AKIA|ASIA)[0-9A-Z]{16}'
  'a Telegram bot token|[0-9]{8,10}:[A-Za-z0-9_-]{35}'
  'an access_token parameter|access_token=[A-Za-z0-9._%-]{16,}'
  'a signed URL|[?&](X-Amz-Signature|X-Goog-Signature|Signature|sig|oh)=[A-Za-z0-9%._~+/=-]{8,}'
)
for entry in "${PATTERNS[@]}"; do
  kind="${entry%%|*}"
  regex="${entry#*|}"
  while IFS= read -r hit; do
    [ -n "$hit" ] || continue
    problem "${hit%%:*}:$(echo "$hit" | cut -d: -f2): $kind (remove it or replace it with a stable fake)"
  done < <(printf '%s\0' "${FILES[@]}" | xargs -0 grep -HnIE -o -- "$regex" 2>/dev/null | cut -d: -f1,2 | sort -u || true)
done

# 2. Raw responses must never be tracked.
for file in "${FILES[@]}"; do
  case "/$file" in
    */raw/*) problem "$file: raw responses must stay local and ignored (fixtures/<platform>/raw/); git rm --cached it" ;;
  esac
done

# 3. A README lists every file of a platform folder.
listed_in_readme() {
  local file="$1" top="$2" dir rel
  dir="$(dirname "$file")"
  while :; do
    if [ -f "$dir/README.md" ]; then
      rel="${file#"$dir"/}"
      if grep -qF -- "$rel" "$dir/README.md" || grep -qF -- "$(basename "$file")" "$dir/README.md"; then
        return 0
      fi
    fi
    [ "$dir" = "$top" ] && return 1
    dir="$(dirname "$dir")"
  done
}

declare -A NO_README=()
for file in "${FILES[@]}"; do
  [ -f "$file" ] || continue
  top="$(echo "$file" | cut -d/ -f1-2)"
  [ "$top" != "$file" ] || continue # a file directly under fixtures/
  case "$top" in fixtures/contracts | fixtures/text) continue ;; esac
  name="$(basename "$file")"
  case "$name" in README.md | synthetic-*) continue ;; esac
  case "/$file" in */raw/*) continue ;; esac
  if [ ! -f "$top/README.md" ] && [ ! -f "$(dirname "$file")/README.md" ]; then
    if [ -z "${NO_README[$top]:-}" ]; then
      NO_README[$top]=1
      problem "$top has no README.md listing its files (call, date, what was scrubbed)"
    fi
    continue
  fi
  listed_in_readme "$file" "$top" || problem "$file is not listed in a README.md of its folder"
done

if [ "$PROBLEMS" -gt 0 ]; then
  echo "check-fixtures: $PROBLEMS problem(s); see .claude/rules/fixtures.md" >&2
  exit 1
fi
echo "check-fixtures: ${#FILES[@]} fixture file(s) clean"
