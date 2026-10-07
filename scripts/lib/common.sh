# shellcheck shell=bash
# Sourced by the scripts in scripts/. A script reads its data from the git repository of its
# working directory (sb_repo_root) and its own files from the repository that holds the scripts
# (SB_KIT_ROOT), so tests can run the real scripts inside throwaway repositories.

SB_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SB_SCRIPTS_DIR="$(dirname "$SB_LIB_DIR")"
SB_KIT_ROOT="$(dirname "$SB_SCRIPTS_DIR")"
export TURBO_TELEMETRY_DISABLED=1

sb_repo_root() {
  git rev-parse --show-toplevel
}

sb_die() {
  echo "error: $*" >&2
  exit 1
}

# Puts the pinned Node (.node-version) first on PATH when an nvm directory has it, so make
# targets and the kit's hooks run the pinned toolchain even where the default node differs (the
# cloud container ships another version). NODE_AUTOSELECT=0 keeps PATH as it is.
sb_select_node() {
  [ "${NODE_AUTOSELECT:-1}" = "0" ] && return 0
  local want dir bin
  want="$(tr -d '[:space:]' <"$SB_KIT_ROOT/.node-version" 2>/dev/null)" || return 0
  [ -n "$want" ] || return 0
  [ "$(node --version 2>/dev/null)" = "v$want" ] && return 0
  for dir in "${NVM_DIR:-}" "$HOME/.nvm" /opt/nvm /usr/local/nvm; do
    [ -n "$dir" ] || continue
    bin="$dir/versions/node/v$want/bin"
    if [ -x "$bin/node" ]; then
      PATH="$bin:$PATH"
      export PATH
      return 0
    fi
  done
  return 0
}
sb_select_node

# The ref the current branch is compared with: CHECK_BASE when set, else the merge base with
# origin/main, else with main. Prints nothing when there is no merge base.
sb_merge_base() {
  local ref base
  if [ -n "${CHECK_BASE:-}" ]; then
    git rev-parse --verify "${CHECK_BASE}^{commit}"
    return
  fi
  for ref in origin/main main; do
    git rev-parse --verify -q "${ref}^{commit}" >/dev/null || continue
    base="$(git merge-base HEAD "$ref" 2>/dev/null || true)"
    if [ -n "$base" ]; then
      echo "$base"
      return
    fi
  done
}

# Files that differ from a base commit: committed, staged, unstaged and untracked (not ignored).
sb_changed_files() {
  { git diff --name-only "$1"; git ls-files --others --exclude-standard; } | sort -u
}

# Prints shell-quoted `export KEY='value'` lines.
sb_export() {
  local key="$1" value="$2"
  printf "export %s='%s'\n" "$key" "${value//\'/\'\\\'\'}"
}
