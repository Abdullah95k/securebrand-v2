---
name: contract-change
description: Apply one approved contract proposal to packages/contracts and the migrations, regenerate the derived artefacts and report which services break. Only on the branch sb/CC-<proposal>, or in a session started with ALLOW_CONTRACT_EDITS=1.
argument-hint: <path to docs/proposals/... file>
disable-model-invocation: true
effort: max
---

# Contract change: $ARGUMENTS

1. Run `git rev-parse --abbrev-ref HEAD` and `echo "${ALLOW_CONTRACT_EDITS:-0}"`. Go on only if the branch is `sb/CC-<proposal>`, where `<proposal>` is the proposal's file name without `.md`, or the second command prints 1. The pull request's branch must be `sb/CC-<proposal>` in both cases, because the policy check reads `docs/proposals/<proposal>.md` from it. Otherwise stop and tell me to restart on that branch, or with `ALLOW_CONTRACT_EDITS=1 claude --worktree CC-<proposal>`.
2. Read the proposal. If its "Decision" line is not "approved" with a date and a name, stop.
3. Change only what the proposal names in `packages/contracts`, `supabase/migrations` and `clickhouse/migrations`. Follow `docs/contracts/VERSIONING.md` (ADR-0002): a change that only adds an optional field stays in the version; anything else is a new version with a dual-publish window.
4. Regenerate the JSON Schemas and the Python models; add or update the valid and invalid fixtures; update `docs/contracts/TABLE-OWNERS.md` if ownership changed.
5. Run the conformance suites in TypeScript and Python, and the migrations from zero.
6. Run every service's tests and list each service whose tests now fail, with the failing test names. Do not edit service code in this session.
7. Commit the change; then set the proposal's `Applied:` line to that commit's SHA alone (`Applied: <sha>`), in a second commit on this branch, and stop. The policy check reads the SHA at the start of the line and requires it to be part of the branch.
