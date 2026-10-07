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

# The PATH of the shell that started these scripts, before sb_select_node changes it (exported, so
# a script started by another sees the shell's): make doctor also checks the node that the pnpm
# commands a user types run on.
export SB_CALLER_PATH="${SB_CALLER_PATH:-$PATH}"

# Puts the pinned Node (.node-version) first on PATH when an nvm directory has it, so make
# targets and the kit's hooks run the pinned toolchain even where the default node differs (the
# cloud container ships another version). NODE_AUTOSELECT=0 keeps PATH as it is.
sb_select_node() {
  [ "${NODE_AUTOSELECT:-1}" = "0" ] && return 0
  local want dir bin
  # A copy of scripts/ alone (the policy job runs the base branch's) has no .node-version.
  [ -r "$SB_KIT_ROOT/.node-version" ] || return 0
  want="$(tr -d '[:space:]' <"$SB_KIT_ROOT/.node-version")" || return 0
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
# origin/main, else with main. Prints nothing when there is no merge base, and when CHECK_BASE is
# not a commit here (CI passes the commit before a push, which a force push can make unreachable
# and which is all zeros for a new branch); the callers then check everything.
sb_merge_base() {
  local ref base
  if [ -n "${CHECK_BASE:-}" ]; then
    if base="$(git rev-parse --verify -q "${CHECK_BASE}^{commit}")"; then
      echo "$base"
    else
      echo "warning: CHECK_BASE=$CHECK_BASE is not a commit of this repository" >&2
    fi
    return 0
  fi
  for ref in origin/main main; do
    git rev-parse --verify -q "${ref}^{commit}" >/dev/null || continue
    base="$(git merge-base HEAD "$ref" 2>/dev/null || true)"
    if [ -n "$base" ]; then
      echo "$base"
      return 0
    fi
  done
}

# The base commit of a pull request check (scripts/policy/): the merge base of HEAD and <ref>, or
# <ref> itself when they share no history; with no <ref>, sb_merge_base. Exits when there is none.
sb_policy_base() {
  local ref="${1:-}" base
  if [ -z "$ref" ]; then
    base="$(sb_merge_base)"
    [ -n "$base" ] || sb_die "no merge base with main; pass --base <ref>"
  else
    base="$(git merge-base HEAD "$ref" 2>/dev/null || git rev-parse --verify -q "$ref^{commit}")" ||
      sb_die "$ref is not a commit of this repository; fetch it or pass another --base"
  fi
  echo "$base"
}

# Files that differ from a base commit: committed, staged, unstaged and untracked (not ignored).
# A moved file counts at both of its paths (--no-renames), so a file moved out of a frozen path
# is seen.
sb_changed_files() {
  { git diff --no-renames --name-only "$1"; git ls-files --others --exclude-standard; } | sort -u
}

# Prints shell-quoted `export KEY='value'` lines.
sb_export() {
  local key="$1" value="$2"
  printf "export %s='%s'\n" "$key" "${value//\'/\'\\\'\'}"
}
