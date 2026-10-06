# Listening platform build kit for Claude Code

This kit turns the build plan into files Claude Code loads by itself. Install it at the root of the repository before the first session: every session runs in a git worktree branched from the remote's main, and a worktree only contains what is committed there.

## What is inside

| Path | Purpose |
|---|---|
| `CLAUDE.md` | Instructions Claude reads in every session: non-negotiables, commands, layout, session rules |
| `.claude/settings.json` | Permissions and four hooks |
| `.claude/hooks/guard-contracts.sh` | Blocks edits to `packages/contracts`, `supabase/migrations`, `clickhouse/migrations` unless the session started with `ALLOW_CONTRACT_EDITS=1` |
| `.claude/hooks/format-file.sh` | Formats each edited file (Prettier; `ruff format` from the nearest pyproject) |
| `.claude/hooks/arm-stop-gate.sh` | Arms the stop gate when you type `/build-session` or `/fix-session`, for that session only |
| `.claude/hooks/stop-gate.sh` | In armed sessions, keeps Claude working while the checks for changed packages fail (three rounds at most); lets it stop once a proposal or issue is filed |
| `.claude/skills/` | `/plan-session`, `/build-session`, `/review-session`, `/fix-session`, `/probe-platform`, `/integration-gate`, `/decide-session`, `/contract-change` |
| `.claude/agents/prd-reviewer.md` | Read-only reviewer subagent |
| `.claude/rules/` | Path-scoped rules for contracts, services, Python, fixtures |
| `.worktreeinclude` | Copies `.env` and local files into new worktrees |
| `gitignore-additions.txt` | Lines to add to `.gitignore` |
| `scripts/check-changed.sh` | Lint, types and tests for packages changed against main |
| `docs/dependencies.md` | The dependency register every pull request updates |
| `docs/prds/` | The 86 PRDs, CONVENTIONS, the PRD index and the open questions |
| `build-plan/` | README, SESSIONS.md, GATES.md, one brief per session, templates, and the generator tools |

## Install (day zero, before D1 and F1)

1. Create the repository with its remote (for example on GitHub) and clone it.
2. Unzip the kit at the repository root. Merge `gitignore-additions.txt` into `.gitignore`, then delete it.
3. Install `jq` (the hooks read their input with it) and run `chmod +x .claude/hooks/*.sh scripts/*.sh`.
4. The 86 PRDs are already in `docs/prds/` (with `_shared/CONVENTIONS.md`, `README.md` and `OPEN-QUESTIONS.md`), identical to the PRD zip; the briefs point at those paths.
5. Commit everything and push to `main`. Worktree sessions branch from the remote's main, so anything not pushed is invisible to them.
6. Run `claude` once at the root to accept workspace trust. Check `/hooks` lists the four hooks and `/context` shows `CLAUDE.md` loaded.
7. F1 fits `scripts/check-changed.sh`, the `make` targets (including `make test SERVICE=<name>`) and CI to the toolchain it sets up; from then on the hooks enforce the rules.

## Run a session

Open its brief in `build-plan/sessions/`, then follow its "How to run it" section. The usual loop:

```bash
claude --worktree FB2 --permission-mode plan   # then: /plan-session FB2
# approve the plan, then in the same terminal: /clear and /build-session FB2
claude --worktree FB2                          # in a new terminal: /review-session FB2
# back in the build terminal: /fix-session FB2
# then a fresh session: /review-session FB2 recheck, and merge
```

## Change the plan

Every brief and the plan's wave tables come from `build-plan/tools/sessions.py`. Edit it, then from the repository root:

```bash
python3 build-plan/tools/validate.py
python3 build-plan/tools/gen_briefs.py . build-plan/tools/prd_index.json build-plan/tools/prd_io.json
```
