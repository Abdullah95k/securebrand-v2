# Plan · F1b Kit follow-ups after D1 and D2

Brief: build-plan/sessions/F1b-kit-follow-ups-after-d1-and-d2.md · PRD: none (toolkit lane; the requirements are the orchestrator's brief for F1b, W1 to W13 with its decisions table, read from `docs/orchestration/briefs/F1b.md` at commit 8f70987 and given to the build session in its system prompt) · Approved by: the orchestrator, under the user's delegation (docs/orchestration/README.md), 25 Oct 2026

## Context the plan rests on

- **Source.** The orchestrator's brief is the source of this plan: its scope, "Never" list, ground rules, preconditions, work items W1 to W13 (with their code blocks), Checks, "Not in scope" and Finish. This plan does not repeat its code blocks; the build session takes them from the brief, as corrected under "Discrepancies with the brief" below. Where this plan and the brief differ, this plan's corrections apply once the orchestrator approves them.
- **Facts are at origin/main 6c0f953** (the brief's base). `sb/F1b` = 6c0f953 plus the lane's build-plan commit (`build-plan/tools/sessions.py`, `build-plan/sessions/F1b-kit-follow-ups-after-d1-and-d2.md`, `build-plan/SESSIONS.md`).
- **How the brief was checked.** Four read-only subagents checked every file:line, every "current text" and every test of W1 to W13 against origin/main, and ran the brief's proposed hook, bootstrap, stack-up, supabase-start and common.sh code on temp copies with stand-ins (`bash -n`, the stop-gate scenarios 1 to 18, the guard cases 1 to 11, shallow file:// clones, fake docker and supabase shims, the generator in a temp clone). They did not write or run the TypeScript tests. Results that this plan relies on are under "Discrepancies" (what is wrong) and "Confirmed" (what holds).
- **ADRs.** ADR-0030 (tooling, local stack and dependency policy; "every session (the toolchain)") applies: it ratifies what F1 built, which W1 to W13 adjust without changing the toolchain. ADR-0029 matters only for W13's `docs/handoffs/F1.md:120` pointer. The other ADRs whose "Applies to" reads "all" govern messages, tables and services, none of which this lane touches. ADR-0001: no PRD here.
- **Handoffs read.** `docs/handoffs/F1.md`, `docs/handoffs/D2.md` (Needs first), `docs/reviews/F1.md` (Give the session), `docs/reviews/D2.md:188` (assigns the port collision to this lane), `docs/decisions/D2-SUMMARY.md:253` (Q2 (11)'s reference).
- **Frozen paths.** Nothing under `packages/contracts`, `supabase/migrations` or `clickhouse/migrations` changes. On `sb/F1b` the guard blocks them (`guard-contracts.sh:18`). Test files that name those paths are written with Write and Edit, never with a Bash heredoc (brief, setup step 7).
- **Generated brief.** The lane's generated brief carries the generator's generic foundation lines ("The package README shows a service using it", "Conformance or golden tests ... in every language"); its first "Watch for" line says they do not apply. Done is the acceptance table below.

## Acceptance map

No PRD section 13: the criteria are W1 to W13 of the orchestrator's brief, as corrected below. All tests live in `tools/repo-checks` (Vitest); run with `make test SERVICE=repo-checks` (unit and acceptance; the acceptance suites need the stack), or a unit file alone with `nvm use 24.21.0 >/dev/null && pnpm --filter repo-checks exec vitest run test/unit/<file>`.

| W | Criterion (short) | Test (file :: name) | Level | Fixture |
|---|---|---|---|---|
| W1 | The guard blocks Edit, Write, MultiEdit, NotebookEdit and Bash writes to the three contract paths, allows reads and near-miss names, allows the lanes `sb/F2`, `sb/F3`, `sb/F8`, `sb/CC-?*` and `ALLOW_CONTRACT_EDITS=1`, blocks every other branch (including bare `sb/CC-`) and a detached HEAD; the quoted-target gap is characterised (Q3 (a)) | test/unit/guard-contracts.test.ts :: cases 1 to 11 of the brief (`blocks %s to %s on sb/X`, `blocks a NotebookEdit ...`, `blocks absolute, relative and backslash paths alike`, `allows writes outside the frozen paths, near-miss names included`, `allows Write and Bash writes to every frozen path on %s`, `still blocks on %s`, `allows every write when ALLOW_CONTRACT_EDITS=1`, `blocks the Bash write \`%s\``, `blocks a relative write or touch when the cwd is inside a contract path`, `allows the Bash read \`%s\``, `known gap, CI is the backstop: a quoted target is not matched`) | unit | TempRepo; helpers/hooks.ts `runHook` |
| W1 | The kit tells F2, F3, F8 and `/contract-change` they may edit (Q1 (a), Q2 (6) to (8)) | guard-contracts.test.ts :: `the kit tells the contract lanes they may edit` (rules, build-session, contract-change, CLAUDE.md) | unit | repository files |
| W1 | Tests never inherit `ALLOW_CONTRACT_EDITS` or `CLAUDE_PROJECT_DIR` | covered by the "blocks" cases (cleanEnv strips both) | unit | |
| W1 | The regenerated F2, F3 and F8 briefs name `sb/F2`, `sb/F3`, `sb/F8`; nothing else in build-plan/ changes | `python3 build-plan/tools/gen_briefs.py ...`, `git diff --stat build-plan/`, `python3 build-plan/tools/validate.py` (`errors []`) | command | |
| W2 | Arming records the arm commit and the proposals and issues that existed; re-arming keeps the first arm point | test/unit/stop-gate.test.ts :: cases 1 and 16 | unit | TempRepo with stub `scripts/check-changed.sh` |
| W2 | Unarmed and plan-mode sessions stop; an armed one is blocked while checks fail, with the log tail; passes and caches on an unchanged tree; reruns after a change; escapes after 3 rounds; docs-only changes run nothing | stop-gate.test.ts :: cases 2 to 8 | unit | same |
| W2 | Only a q-file or proposal filed in this session lets Claude stop: untracked, staged and committed q-files and proposals count; earlier sessions' issues, issues merged or fast-forwarded from main (stale origin/main), pre-arm untracked files, README edits and deletes, and a deleted and re-added file do not | stop-gate.test.ts :: cases 9 to 15 (12 in shapes a and b) | unit | same |
| W2 | No merge base: the gate runs the full check instead of passing; changes outside `docs/` and `build-plan/` are gated (Q5) | stop-gate.test.ts :: cases 17 and 18 | unit | orphan branch; `scripts/`, `tests/e2e/` changes |
| W2 | settings.json wires the guard, the arm hook and the stop gate (KIT-9 part D, optional) | test/unit/kit-fit.test.ts :: case 19 | unit | `.claude/settings.json` |
| W3 | The kit names `make bootstrap` as the install step; `check-changed.sh` prints one line, `(run make bootstrap)`, when turbo answers nothing | kit-fit.test.ts :: `skills, rules, agents and hooks name make bootstrap as the install step, never a bare pnpm install or uv sync` | unit | repository files |
| W4 | A second bootstrap runs no nvm command when nvm holds the pin as default; nvm failure names nodejs.org; a pip-installed uv is updated with pip --user; a uv still out of range is named; a pinned uv in ~/.local/bin behind another is used and reported | test/unit/doctor.test.ts (`describe("make bootstrap ...")`) :: (a) to (e) of the brief, plus the existing test at :56-90 still passing | unit | stand-in nvm.sh, uv, python3, temp HOME |
| W5 | Every script that runs pyright or the Supabase CLI turns off their version checks | test/unit/common.test.ts (or doctor.test.ts) :: `every script turns off pyright-python's and the Supabase CLI's version checks` | unit | |
| W6 | A shallow clone fetches main once and compares with the real merge base; a failed fetch names `git fetch --unshallow origin main`; `SB_NO_FETCH=1` leaves it shallow; `make policy BASE=origin/main` in a shallow clone uses the merge base | test/unit/check-changed.test.ts :: (a) to (d) of the brief, (d) as corrected below | unit | local bare origin over file:// |
| W7 | The check job reserves 54320-54329 first; every Supabase port >= 32768 lies in that range; `supabase start` is retried once after `supabase stop` only on "address already in use" | test/unit/ci-workflow.test.ts :: `reserves every Supabase host port in the check job before any other step opens a connection`; test/unit/supabase-start.test.ts :: the four cases of the brief | unit | fake `node_modules/.bin/supabase` |
| W8 | The mirror is retried for `IMAGE_PULL_WAIT_SECONDS` (default 300); another registry's "Rate exceeded" or 5xx up to 3 times; any other refusal fails at once naming the registry's answer and `IMAGE_REGISTRY=upstream` (Q9 (a)) | test/unit/stack-up.test.ts :: the four cases of the brief | unit | fake docker, fake supabase, versions.env |
| W9 | ClickHouse comes from this repository's GHCR mirror of the Docker Official Image; two dependency rows appended; the Mirror images run's digest equals ECR's | test/unit/pins.test.ts :: `pulls ClickHouse from this repository's GHCR mirror, copied from the Docker Official Image`; `make policy` (check-dependencies); the run and the two digests in the handoff | unit, CI | |
| W10 | CI's check job runs `pnpm fmt:check` before `make up` | ci-workflow.test.ts :: `the check job runs pnpm fmt:check before it starts the stack`; `pnpm fmt:check` exit 0 | unit, command | |
| W11 | The mirror workflow runs on demand and on pushes to main that change the pins | ci-workflow.test.ts :: `the mirror workflow runs on demand and on pushes to main that change stack/versions.env` | unit | |
| W12 | Dependabot covers github-actions, npm and uv, ignores uv-build minors | ci-workflow.test.ts :: the dependabot test at :190, renamed without docker | unit | |
| W13 | F1's handoff and plan corrected in place with one dated line each (Q15 (a)); the plan's approval record from Q13; the `contract-change` label exists; optional LANE-NAME characterisation | `gh api repos/Abdullah95k/securebrand-v2/labels/contract-change --jq .name`; policy-handoff-review.test.ts :: `a follow-up lane is judged by its own review, not its parent's` (optional) | docs, unit | |
| all | Checks of the brief | `make check`; `make test SERVICE=repo-checks`; `TEST_STACK_RESET=1 make check ACCEPTANCE=1`; `bash -n` on every changed script and hook; Prettier on changed Markdown and YAML, then `pnpm fmt:check`; `POLICY_BRANCH=sb/F1b make policy BASE=origin/main` | command | stack up |

## Uncovered behaviours

Not applicable as written (no platform service). The behaviours the toolkit must keep, beyond the acceptance map:

| Behaviour | Test |
|---|---|
| A live hook never breaks this session (a syntax error in the guard blocks every tool call) | brief setup step 6: scratch copy, `bash -n`, harmless payload exits 0, then one `cp` |
| The stop gate never passes silently (no merge base, quoted names, old empty arm file) | stop-gate.test.ts cases 17, 9 (a non-ASCII q-file name may be added), and the old-format arm file giving no exemption |
| Re-running `make bootstrap` needs no network for Node | doctor.test.ts (a); the rest of a second run offline is "not verified" unless tested (brief W4) |
| No test touches the network | all new tests use TempRepo, stand-ins and file:// remotes |

## Contracts

| Kind | Name | Version | Read or write | Exists? |
|---|---|---|---|---|
| none | | | | |

Proposals needed: none. This lane touches no topic, job queue or table.

## Build outline

Order, commits and test-first steps follow the brief ("Work items, in commit order"); commit messages start with `F1b <area>: `. Each item: write the test, show it failing for the stated reason, make the change, show it passing.

0. **Setup** (brief "Preconditions and setup"): `ls -la .build-state/stop-gate-*` right after the session starts (record it); start dockerd; `make bootstrap` (if it stops at uv, the brief's pip `--user` fallback, with discrepancy D-S2 in mind); merge origin/main if it moved; expect `check` red on ClickHouse pulls until W9.
1. **W1 contract lanes and the guard's tests.** Files: `tools/repo-checks/test/helpers/repo.ts` (cleanEnv), new `test/helpers/hooks.ts`, new `test/unit/guard-contracts.test.ts`; `.claude/rules/contracts.md:10`, `.claude/skills/build-session/SKILL.md:33`, `.claude/skills/contract-change/SKILL.md:3`, `:11`, `:17`, `CLAUDE.md:12`, `.claude/hooks/guard-contracts.sh:18` (`sb/CC-?*`, live-hook procedure), `KIT-README.md:11`, `build-plan/README.md:21`, `:24`, `build-plan/tools/gen_briefs.py:314` (f-string) and the regenerated F2, F3, F8 briefs, `.claude/skills/plan-session/SKILL.md:27`. Corrections D-W1-1 to D-W1-5.
2. **W2 stop gate.** Files: `.claude/hooks/arm-stop-gate.sh:14-15`, `.claude/hooks/stop-gate.sh:23-24`, `:29`, `:36-45` (live-hook procedure for both), `.claude/skills/fix-session/SKILL.md:11` and its q-file sentence, `.claude/skills/build-session/SKILL.md:34`, `docs/issues/README.md`; new `test/unit/stop-gate.test.ts`, kit-fit case 19. Corrections D-W2-1 to D-W2-7.
3. **W3 install step.** Files: `.claude/skills/build-session/SKILL.md:17`, `scripts/check-changed.sh:81-84`, `scripts/doctor.sh:79`, `:81`, `scripts/stack-env.sh:47`; test in kit-fit.test.ts. Correction D-W3-1.
4. **W4 bootstrap.** Files: `scripts/bootstrap.sh` (step 1 and step 3, header `:3-5`), `scripts/doctor.sh:62`; tests (a) to (e) in doctor.test.ts. Corrections D-W4-1 to D-W4-6.
5. **W5 version checks.** File: `scripts/lib/common.sh` after `:9`; test in a new common.test.ts or doctor.test.ts. Corrections D-W5-1 to D-W5-3.
6. **W6 shallow clones.** Files: `scripts/lib/common.sh` (`sb_unshallow_for_base`, `sb_merge_base`), `scripts/check-changed.sh:14-15`, `.claude/skills/review-session/SKILL.md:17` (one sentence); tests (a) to (d) in check-changed.test.ts. Corrections D-W6-1, D-W6-2.
7. **W7 Supabase ports.** Files: `.github/workflows/ci.yml` (first step; "Stack logs" `ss -tanp`), new executable `scripts/supabase-start.sh`, `scripts/stack-up.sh:65-74`, optional `stack/README.md:37-38` line; tests in ci-workflow.test.ts and new supabase-start.test.ts. Corrections D-W7-1 to D-W7-4.
8. **W8 image pulls.** File: `scripts/stack-up.sh:8`, `:26-35`, `:40-48`; new stack-up.test.ts. Corrections D-W8-1 to D-W8-6.
9. **W9 ClickHouse mirror.** Verify ECR's digest first (dockerd up); files: `stack/versions.env:3-5`, `:14-17`, two rows appended to `docs/dependencies.md`, `stack/README.md:60-64`, `README.md:86-87`, `.github/workflows/mirror-images.yml:1-2`, `scripts/mirror-images.sh:2-4`; test in pins.test.ts. Push W9 alone, read the Mirror images run, compare digests, revert on mismatch; local `docker tag` stand-in; "make the package public" as a user action. Run the local stack tests (W7, W8, `make check ACCEPTANCE=1`) before this commit.
10. **W10 formatting in CI.** `pnpm fmt:check` first (a separate `make fmt` commit if it lists files); then the step after Install in ci.yml; test in ci-workflow.test.ts.
11. **W11 mirror trigger** (only after W9's push). `mirror-images.yml:10-14` (`branches: [main]`), the trigger sentence at `:2-4`, `stack/README.md:64`, `:69-70`; test at ci-workflow.test.ts:171. Correction D-W11-1.
12. **W12 Dependabot.** `.github/dependabot.yml` (header, uv-build ignore, delete the docker block), `README.md:87-88`; test at ci-workflow.test.ts:190. Correction D-W12-1.
13. **W13 records.** `docs/handoffs/F1.md` (16 corrections of the brief, one dated line), `docs/plans/F1.md` (L3 approval field and the 12 rows' cells, from Q13; one correction line after L3), label check, optional LANE-NAME test. Corrections D-W13-1 to D-W13-6 and Q16.
14. **Finish** (brief "Finish"): `docs/handoffs/F1b.md` from `build-plan/templates/HANDOFF.md` with the W1 to W13 acceptance table, the decisions Q1 to Q16 copied exactly, Not done, the arm-file observation, verified and not verified, Operations, Open items; `/code-review`; the Checks again; push; `ORCHESTRATOR: DONE`.

- SDK features used: none (toolkit lane).
- Mapper added to normalize-item: none.
- Budget tag and priority: none.
- Metrics and alerts: none.
- New dependency: only W9's GHCR mirror of ClickHouse, with its two rows appended to `docs/dependencies.md`.

## Risks and their tests

| Risk | Covered by |
|---|---|
| A broken live hook blocks every tool call or every stop of the session | setup step 6 procedure for every hook change; `bash -n` in Checks |
| The new stop gate wrongly exempts or wrongly blocks | stop-gate.test.ts cases 1 to 18, including the merge and fast-forward shapes |
| This session's own arm file is in the old empty format, so it gets no filing exemption | brief W2 change 2: only the 3-round escape applies; file a q-file only if needed and accept up to 3 rounds |
| Main's `check` is red on ECR's data limit until W9 | W9 early; handoff names the first push with a green `check` |
| The new GHCR package is private, so every cloud `make up` fails until the user makes it public | local `docker tag` stand-in; user action in the handoff |
| docker.io answers 429 to the mirror run, or the digests differ | W9 step 4: revert, push, report under NEEDS-INPUT with both digests or the answer |
| Prettier 3.9.10 (Dependabot #11) reformats files once W10 lands | user action: `make fmt` on #11's branch |
| The W8 test at origin/main hangs for about 120 s instead of failing fast | D-W8-2: a short `timeoutMs` |
| W4 in a container whose uv is neither self-updatable nor pip-owned stops bootstrap (Q6 (a)) | D-S2; tests (c) and (d); setup fallback |

## Discrepancies with the brief

Each item: where (file:line at origin/main), what the brief says, what is true, the correction this plan proposes. None changes a decision Q1 to Q15.

### Setup and preconditions

- **D-S1** `scripts/bootstrap.sh:31`, `:42`, `:54`, `:59`. Setup step 2 says bootstrap stops at the uv step "before it installs anything". Steps 1 (`nvm install`, `:31`) and 2 (`npm install --global pnpm`, `:42`) run before it. Correction: "before `pnpm install` (`:59`) and the uv syncs".
- **D-S2** This container: `/root/.local/bin/uv` is uv 0.11.32, not 0.12.23 (W4's "Test first" says 0.12.23); `python3 -m pip show uv` finds no package and there is no `~/.config/uv` receipt. So the pip `--user` path of setup step 2 and W4 does not describe this container's uv: `pip install --user uv==0.12.23` would still put a pinned uv into `~/.local/bin` (the fallback works), but after W4 a bootstrap here takes the "pip does not own it" branch (Q6 (a)) when `uv self update` fails. Run in this plan session, 24 Oct 2026: `make bootstrap` installed Node 24.21.0 and pnpm 10.34.6, then stopped at `uv 0.11.32 -> 0.12.23` with "error: Self-update is only available for uv binaries installed via the standalone installation scripts." and "error: uv could not update itself; ...". Then `python3 -m pip install --user --upgrade 'uv==0.12.23'` replaced `~/.local/bin/uv` (now 0.12.23, and `pip show uv` finds it), and `PATH="$HOME/.local/bin:$PATH" make bootstrap` ended with "make doctor: the toolchain matches the pins". So setup step 2's fallback works here. Correction: W4's temp-HOME reason becomes "whatever uv is in `$HOME/.local/bin`" (a fresh container has 0.11.32 there, not pip-owned; after the fallback, a pip-owned 0.12.23). After W4, a fresh container of this kind takes Q6 (a)'s "pip does not own it" branch and stops with the installer command; the setup fallback still works there. Record both in the handoff.

### W1

- **D-W1-1** `.claude/skills/contract-change/SKILL.md:11`. The brief's replacement text shows `echo \"${ALLOW_CONTRACT_EDITS:-0}\"`; the backslashes are the brief's quoting. The skill reads `` `echo "${ALLOW_CONTRACT_EDITS:-0}"` ``, as it does now.
- **D-W1-2** `tools/repo-checks/test/helpers/repo.ts:69-81` is the list of make variables under a MAKEFLAGS comment. Correction: add `ALLOW_CONTRACT_EDITS` and `CLAUDE_PROJECT_DIR` as their own condition with their own comment, before `:69`, so the comment stays true.
- **D-W1-3** Change 6, the generator check. On `sb/F1b` there are 126 briefs (F1b's own), so the generator prints `briefs 126`, not 125; it still reproduces everything byte for byte (checked in a temp clone). `KIT-README.md` is at the root, so `git diff --stat build-plan/` lists `gen_briefs.py`, the three briefs and `build-plan/README.md` (one file, two lines); check `KIT-README.md` with its own diff.
- **D-W1-4** `build-plan/README.md:24` covers both `/contract-change` and F2, F3, F8. "or runs on its lane branch sb/<ID> (cloud)" is wrong for the contract-change half, whose branch is `sb/CC-<proposal>`. Correction: name `sb/CC-<proposal>` for that half.
- **D-W1-5** Verify step: `make test SERVICE=repo-checks` also runs the acceptance suites (stack needed). For the unit file alone use the brief's `pnpm --filter repo-checks exec vitest run ...` form.

### W2

- **D-W2-1** Case 15 fails today only in some shapes: a file present at the merge base re-added with identical content already gives exit 2 at origin/main. Correction: "a `docs/issues/X-1.md` committed on sb/X before arming, deleted and re-added (committed) after arming" (old hook exit 0, new exit 2, checked).
- **D-W2-2** Case 17 fails today only with a clean worktree (an uncommitted change already gives exit 2). Correction: "orphan branch, all code committed, clean worktree".
- **D-W2-3** Case 3 (plan mode) cannot use the `stop(s, exit)` helper, which hard-codes `permission_mode: "default"`. Correction: give the helper a `mode` parameter.
- **D-W2-4** Case 16 passes trivially today if it compares arm-file contents (both empty). Correction: assert the arm file's first line is the SHA HEAD was on at the first arm, after a commit and a second arm.
- **D-W2-5** Case 1: `stop-gate-<s>.filed-before` also lists `docs/issues/README.md` and `docs/proposals/README.md` (tracked files); expect them.
- **D-W2-6** Change 2, `:36-45`, is prose only. Two points the code must handle: initialise `FP=""` when BASE is empty (`:48` writes it to the pass file), and with BASE empty every stop reruns the full check (no fingerprint shortcut). A version that passes every case: `FP=""; if [ -n "$BASE" ]; then <path test with exit 0>; FP="$(<widened fingerprint>)"; [ -f "$PASS_FILE" ] && [ "$(cat "$PASS_FILE")" = "$FP" ] && exit 0; fi`.
- **D-W2-7** Minor: the new gate sources `common.sh` twice (once per subshell), and `sb_merge_base` honours `CHECK_BASE`, so a session with `CHECK_BASE` set changes the gate's base. Acceptable; record it in the handoff.

### W3

- **D-W3-1** The test regex must include the backtick characters (/\`pnpm install\`|\`uv sync\`/): the new `SKILL.md:17` text contains "runs `pnpm install --frozen-lockfile` and `uv sync --locked`", which a regex without backticks would match, keeping the test red. Today `build-session/SKILL.md:17` is the only match under the four `.claude` folders.

### W4

- **D-W4-1** `/opt/nvm/nvm.sh`: the remote lookup in `nvm install` is L3278, not L3271 (L1509 and L3356 are right).
- **D-W4-2** `/opt/nvm/alias/default` does not exist in this container (no `/opt/nvm/alias/`, no `/opt/nvm/versions/node`). The format holds from the code: `nvm_make_alias` (nvm.sh L1076) writes the target as typed. Reword the claim.
- **D-W4-3** The ranges `bootstrap.sh:17-36` and `:46-56` include the step comments (`:17-18` "# 1. Node. ...", `:46` "# 3. uv and Python."). Correction: replace `:19-36` and `:47-56`, keeping the comments.
- **D-W4-4** Bug: `uv_version() { uv --version 2>/dev/null | awk '{print $2}'; }` under `pipefail` makes `current="$(uv_version)"` end the script silently (rc 127) when no uv is left on PATH. Correction: `... | awk '{print $2}' || true; }`.
- **D-W4-5** `tr -d '[:space:]' <"$nvm_dir/alias/default" 2>/dev/null` still prints "No such file or directory" for a missing file (redirections apply left to right); the existing test at `:56-90` has no `alias/default`. Correction: `2>/dev/null <"$nvm_dir/alias/default"`, or test `[ -f ]` first.
- **D-W4-6** Wording and test detail: the "~/.local/bin" message prints `$UV_MIN`, not the version found (use `$current`); test (d)'s python3 stand-in must not write the state file on `pip install` (say it explicitly).

### W5

- **D-W5-1** "every script sources common.sh" is false: `scripts/check-fixtures.sh`, `scripts/policy/run-all.sh`, `scripts/migrate/clickhouse.sh` and `scripts/migrate/postgres.sh` do not. None runs pyright or the Supabase CLI; every call site (`check-changed.sh:180`, `doctor.sh:78`, `stack-up.sh:19`, `stack-env.sh:45`, `stack-down.sh:13`) is in a script that does. Correction: "every script that runs pyright or the Supabase CLI sources common.sh". The test name may stay.
- **D-W5-2** `doctor.test.ts:6` imports only `cleanEnv, ROOT, script`; the test needs `run` and `SCRIPTS` too (both exported by helpers/repo.ts).
- **D-W5-3** Confirmed: pyright-python 1.1.414 (`pyright/_utils.py:125`) returns before its PyPI lookup when `PYRIGHT_PYTHON_IGNORE_WARNINGS` is truthy. `SUPABASE_NO_UPDATE_NOTIFIER` could not be checked here (no CLI installed, GitHub blocked), but the brief's "the verifier did not check it" should cite `docs/reviews/F1.md:223`, where the F1 reviewer traced it ("with `SUPABASE_NO_UPDATE_NOTIFIER=1`, none and no file").

### W6

- **D-W6-1** Test (d)'s mechanism is wrong. `make policy` without BASE calls `sb_policy_base ""`, which goes to `sb_merge_base` (`common.sh:78`), not the `:81` fallback; in a shallow clone at origin/main it dies with "error: no merge base with main; pass --base <ref>". The `:81` fallback to main's tip happens only with an explicit ref (`sb_policy_base origin/main` in a depth-1 clone printed main's tip, rc 0). Correction: (d) runs `make policy BASE=origin/main` (or `--base origin/main`) to test `:81`, and fixes it with `sb_unshallow_for_base` there if it fails; optionally a second case without BASE, which W6's `sb_merge_base` change alone fixes.
- **D-W6-2** `.claude/skills/review-session/SKILL.md:17` is one long line whose first part is the context list the user approved in D2 (finding 30, `docs/decisions/D2-SUMMARY.md:253`). Replace only the sentence "Then run `git fetch origin` and read the diff with `git diff origin/main...HEAD`.", keeping the context list and the closing sentence "Worktrees branch from the remote's main, ...". Optional: send `git fetch` output in `sb_unshallow_for_base` to stderr (`>&2`) as a safeguard.

### W7

- **D-W7-1** `ci.yml:81-86` saves the compose logs (`:85`) and `docker ps -a` (`:86`), not only `docker ps -a`.
- **D-W7-2** The config.toml half of the ci-workflow test cannot fail today: the regex matches 7 ports (54321, 54322, 54320, 54329, 54323, 54324, 54327), all in range; `inspector_port = 8083` (`:382`) and the commented smtp/pop3 ports are not matched. The test fails today only through the sysctl step at index 0 (today the checkout). Keep it as a regression guard; do not count it as red.
- **D-W7-3** supabase-start.test.ts: the fake CLI "fails `status`" unconditionally, so `leaves a running Supabase alone` cannot be written. Correction: a toggle (for example `STATUS_OK=1`) makes `status` exit 0; then the calls are just `status`, exit 0, output "Supabase is already running".
- **D-W7-4** `fails naming the port when the second start meets it too`: the script tees the CLI's output, so the fake's own `0.0.0.0:54322` already matches /5432[0-9]/. Correction: assert the script's own text, `supabase start failed twice` and the literal `':5432[0-9]'`. Also: the new script drops "(or pnpm install)" from the CLI-missing message and merges the CLI's stderr into stdout; both acceptable.

### W8

- **D-W8-1** `FAIL_MATCH='ghcr.io/*'` also matches SeaweedFS (`SEAWEEDFS_REPO=ghcr.io/chrislusf/seaweedfs`). With a per-image counter SeaweedFS takes the non-mirror branch and `make up` fails at once. Correction: `FAIL_MATCH='ghcr.io/abdullah95k/*'` in the mirror cases (default and give-up).
- **D-W8-2** At origin/main the "fails at once ... data limit" case hangs: the script sleeps a hard-coded 20 s (`:33`) and ignores `IMAGE_PULL_RETRY_SECONDS`; with `IMAGE_PULL_WAIT_SECONDS=600` it runs into `run()`'s 120 s spawnSync timeout. Correction: pass a short `timeoutMs` (for example 15 000) to `script()` in these tests, so they fail fast before the change.
- **D-W8-3** `gives up after IMAGE_PULL_WAIT_SECONDS ...` is red today only through the wait text: the output already contains the registry's answer (docker's stderr is not redirected at `:30`) and `IMAGE_REGISTRY=upstream` (`:44`). Correction: assert `IMAGE_PULL_WAIT_SECONDS=0` explicitly.
- **D-W8-4** `cleanEnv` strips `IMAGE_REGISTRY` but not `IMAGE_PULL_WAIT_SECONDS`, `IMAGE_PULL_RETRY_SECONDS`, `SUPABASE_FULL` or `SUPABASE_RETRY_WAIT_SECONDS`. The "unset" case must delete `IMAGE_PULL_WAIT_SECONDS` explicitly (pass `undefined`).
- **D-W8-5** The fixture: stack-up.sh reads `$REDPANDA_IMAGE`, `$CLICKHOUSE_IMAGE`, `$SEAWEEDFS_IMAGE` (`:37`), built by `scripts/stack-images.sh` from `<NAME>_REPO:<NAME>_TAG` (it dies on a `_TAG` without `_REPO`, `stack-images.sh:30`); `:9` is `set -euo pipefail`, not the names. Docker calls before compose: `docker info` (`:17`), `docker image inspect` (`:38`), `docker pull --quiet <img>` (`:30`), so the fake takes the image from the last argument. The fake supabase CLI is required (`:19-20`).
- **D-W8-6** Messages: keeping the GHCR advice at `:42` repeats "could not pull ..." right after the new "could not pull ...; the registry answered:" line; keep `:43-45` only, or reword `:42`. The new `*)` text always says "A data limit ... can last hours", inaccurate after 4 "Rate exceeded" answers; word it as "a refusal that is not a short throttle (a data limit can last hours) ...".

### W9

- Nothing wrong found at origin/main. mirror-images.sh handles a `docker.io/library/...` upstream; the new `_REPO` falls under its prefix; pins.test.ts accepts it; `scripts/policy/dependencies.py:13` scans both `_REPO` and `_UPSTREAM`, so both new rows are needed; the trigger at `mirror-images.yml:10-14` has no branch filter and lists `stack/versions.env`. Not verifiable here: the Docker Hub tag and its digest.

### W11

- **D-W11-1** `mirror-images.yml:2-5`: the trigger sentence is L2 (mid-line) to L4; L4-5 go on with "It pulls from Docker Hub anonymously unless the DOCKERHUB_USERNAME and DOCKERHUB_TOKEN secrets exist. New packages are private until the user makes them public (docs/handoffs/F1.md)." Correction: rewrite only the trigger sentence and keep those two.

### W12

- **D-W12-1** `ci-workflow.test.ts:190` is the title "dependabot covers npm, uv, docker and github-actions weekly and grouped with a low limit": rename it without docker. The inline type at L191-198 has no `ignore` field; add `ignore?: { "dependency-name": string; "update-types"?: string[] }[]`. Ecosystems are sorted (L199), so `["github-actions", "npm", "uv"]` fits. Not verified: whether Dependabot normalises the name as `uv-build` or `uv_build` (`services/_template-py/pyproject.toml:16` writes `uv_build`); the build session checks Dependabot's documentation or PR #8's title and uses the name it matches.
- `README.md:86-88`: the Dependabot text is at L87-88; L86 is the mirror sentence (W9).

### W13

- **D-W13-1** `docs/plans/F1.md:3` is one line: "Brief: ... · PRD: none (...) · Approved by: pending (orchestrator)". Replace only the trailing `Approved by:` field; keep the Brief and PRD parts.
- **D-W13-2** Not every Answer cell reads "pending": rows 1-5, 8 and 9 read `pending`; rows 6, 7, 10, 11 and 12 read `pending (plan default)`; the Decided by and ADR cells are empty in all 12 rows (L194-205; header L192).
- **D-W13-3** W13's generic text for `docs/plans/F1.md` (Answer "approved: the recommended option, as built ...", ADR "ADR-0030", "If Q13 is pending, leave :3 unchanged") contradicts Q13 (per-row answers, ADR "none", "Do not write ADR-0030 there"). Q13 says its answers replace W13's text, so the brief is consistent; the plan applies Q13 only and drops W13's generic text.
- **D-W13-4** Q15 says only the approval header and the "Answer" and "Decided by" cells are filled in; Q13 also fills the ADR cell with "none". See question Q16.
- **D-W13-5** `docs/handoffs/F1.md:19` and `:103` state no default: L19 lists the switch, L103 says "`make up` waits up to `IMAGE_PULL_WAIT_SECONDS` (CI: 600) for a freshly mirrored tag"; the old default (0) is at `scripts/stack-up.sh:8`. Item 14's new text applies as written; only the "Why" is off.
- **D-W13-6** The optional LANE-NAME test: the file's helper is `check(branch)`, which passes `--branch`, and `--branch` overrides `POLICY_BRANCH` (`check-handoff-review.sh:19-23`). Correction: call `check("sb/F1b")`; the `beforeEach` starts on `sb/C11` with a `services/` change, which gates like a `tools/` change (`:69`). Expected to pass at origin/main (confirmed from the code: `sb/F1b` gives ID F1b, `:31-32`, `:75-79`).

### The lane's generated brief

- `build-plan/sessions/F1b-kit-follow-ups-after-d1-and-d2.md`: the generator lists the give items as "Docs/handoffs/F1.md" and "Docs/reviews/F1.md" (capitalised, and F1's handoff twice), lists `docs/handoffs/F1b.md` twice under "Hands on", and adds the generic package lines under "Done when". Cosmetic and covered by the first "Watch for" line; left as generated (changing `gen_briefs.py` for it is outside the brief).

## Confirmed

Line references and current texts not listed above match origin/main, among them: guard-contracts.sh `:8`, `:9`, `:16-19`, `:25`, `:29-35`, `:37-58`; every W1 replacement target and every case-12 string; the guard cases 1 to 11 on the real hook (case 11's gap is real; bare `sb/CC-` gives 0 today, 2 with `sb/CC-?*`); `check-handoff-review.sh:53-58` (`applied (abc1234)` gives an empty SHA); `gen_briefs.py:314` and `:183` (`i` in scope); every stop-gate and arm-hook line, with the brief's code passing cases 4 to 18 in bash scenarios (old hook vs new hook); common.sh `sb_merge_base` and `sb_changed_files`; the W3 grep and snippet; W4 tests (a) to (c) failing today for the stated reasons and (c) to (e) passing on a simulation; W6's wrapper (fetch, failed fetch, `SB_NO_FETCH=1`); the W7 lines and `supabase-start.sh` reproducing `stack-up.sh:65-74` (same `--exclude` list, status check and message); W8's `pull()` under `set -euo pipefail` (4 pulls at most, all cases passing on a patched copy); W9 and W10 lines; W11 and W12 tests failing today and passing after; the docs/handoffs/F1.md and docs/reviews/F1.md facts of W13; `.prettierignore:11` ("# Plans are kept exactly as approved."); ADR-0029 `:23`, `:31`.

Not verifiable in this session: the CI run, job and log IDs; PR states #8 to #11; the ruleset; the label; GHCR visibility; the Docker Hub tag and digest; whether UserPromptExpansion fires in orchestrated sessions (setup step 3); the runner's ephemeral range; whether `ip_local_reserved_ports` prevents the collision.

## Questions and answers

The orchestrator's decisions table, copied exactly (columns as in the brief), then the questions this plan adds.

| # | Item | Question | Recommended | Decider | Answer (decided by, date) |
|---|---|---|---|---|---|
| Q1 | W1 | Approve kit texts (1) to (4) as worded? (a) all four; (b) the `.claude/` texts only, `CLAUDE.md:12` unchanged; (c) none, rely on the hook alone | (a) | the user | (a) all four; decided by the user, relayed by the orchestrator on 24 Oct 2026 (the user's answer: "Approve all") |
| Q2 | W1, W2, W3, W6 | Optional parts and further kit lines: (5) hook pattern `sb/CC-?*`; (6) KIT-README, build-plan README and gen_briefs with regenerated F2, F3 and F8 briefs; (7) the plan-session F2/F3/F8 line; (8) the contract-change step 7 wording; (9) the fix-session L11 exemption and the arm hook's L15 notice (W2); (10) the build-session L17 install step (W3); (11) the review-session L17 shallow-clone fetch (W6; a line the user approved in D2, `docs/decisions/D2-SUMMARY.md:253`) | yes to all | the user | yes to all. (6), (7), (8) and (9) put the user's approved changes into words, and (10) and (11) are two of those changes: decided by the user, relayed by the orchestrator on 24 Oct 2026 (the user's answer: "Approve all", to the question naming the contract-lane wording, the install step, the shallow-clone fetch and the q-file convention). (5) is a technical tightening of the hook: decided by the orchestrator on 24 Oct 2026 |
| Q3 | W1 | Guard quoted-target gap: (a) a characterisation test and a documented gap; (b) harden the guard | (a) | the orchestrator | (a); decided by the orchestrator on 24 Oct 2026 |
| Q4 | W2 | Q-file convention `docs/issues/<ID>-q<n>.md` for open questions: (a) adopt; (b) none | (a) | the user | (a) adopt; decided by the user, relayed by the orchestrator on 24 Oct 2026 (the user's answer: "Approve all") |
| Q5 | W2 | Should the stop gate enforce on any change outside `docs/` and `build-plan/`, not only services, packages, py and tools? | yes | the orchestrator | yes; decided by the orchestrator on 24 Oct 2026 |
| Q6 | W4 | `uv self update` fails and pip does not own uv: (a) stop and print the installer command; (b) run the installer | (a) | the orchestrator | (a); decided by the orchestrator on 24 Oct 2026 |
| Q7 | W6 | Shallow clone without a merge base: (a) fetch main once automatically (`SB_NO_FETCH=1` opts out); (b) never fetch, better warning; (c) fail | (a) | the orchestrator | (a); decided by the orchestrator on 24 Oct 2026 |
| Q8 | W7 | Supabase start retry: (A) `supabase stop` before the retry; (B) `supabase stop --no-backup`. Retry only on "address already in use" (yes) or on any failure | (A), only on "address already in use" | the orchestrator | (A), only on "address already in use"; decided by the orchestrator on 24 Oct 2026 |
| Q9 | W8 | Image pull wait: (a) this repository's mirror images are retried for `IMAGE_PULL_WAIT_SECONDS` (default 300); another registry's short throttle ("Rate exceeded", a 5xx) is retried up to 3 times, and any other refusal, "Data limit exceeded" included, fails at once naming its answer; (b) wait for every image, default 300 s; (c) wait for every image, default 120 s | (a) | the orchestrator | (a); decided by the orchestrator on 24 Oct 2026 |
| Q10 | W9 | ECR Public data limit: (a) mirror ClickHouse into GHCR, and the user makes the new package public before merge; (b) an actions/cache of the images; (c) authenticated ECR pulls | (a) | the user | (a) mirror ClickHouse into GHCR; the user makes the new package public before F1b merges (the orchestrator sends the steps once the package exists); decided by the user, relayed by the orchestrator on 24 Oct 2026 (the user's answer: "Copy it to GitHub") |
| Q11 | W11 | Mirror workflow trigger: (a) pushes to main only, plus manual dispatch for lanes; (b) any branch, with a first step that exits unless the pins changed; (c) leave it as is | (a) | the orchestrator | (a); decided by the orchestrator on 24 Oct 2026 |
| Q12 | W12 | Dependabot docker ecosystem: (a) remove, and close #10; (b) keep it with ignores; (c) leave it as is. uv-build minors: ignore them, and close #8. Turborepo 2.11: (a) let PR #11 bring it; (b) ignore turbo minor updates | (a), yes, (a) | the orchestrator | (a), yes, (a): remove the docker ecosystem, ignore uv-build minors, and let PR #11 bring Turborepo 2.11 once its CI is green. The orchestrator closes #10 and #8 after F1b merges; decided by the orchestrator on 24 Oct 2026 |
| Q13 | W13 | `docs/plans/F1.md`: the approval date for L3, and for each of the 12 rows at L194-205 who decided and when (the repository does not record it; L190 says questions 1 to 5, 8 and 9 needed an answer) | the orchestrator supplies them from its records, and "not recorded in the repository" where it has none | the orchestrator | see "Q13: the F1 plan's approval record" below; decided by the orchestrator on 24 Oct 2026 |
| Q14 | W13 | Who creates the `contract-change` label before F2 opens its pull request: (a) the user (repository Settings, Labels); (b) the orchestrator, with a token that can write labels; (c) rely on adding the label to F2's pull request to create it (not verified) | (a) | the orchestrator | done: the orchestrator created the label `contract-change` on 24 Oct 2026, since `docs/orchestration/README.md:43` makes the orchestrator apply it; decided by the orchestrator on 24 Oct 2026. W13 only verifies it exists (`gh api repos/Abdullah95k/securebrand-v2/labels/contract-change`) |
| Q15 | W13 | F1's records: (a) correct `docs/handoffs/F1.md` and `docs/plans/F1.md` in place, with a dated correction line; (b) leave them as merged and record the corrections only in `docs/handoffs/F1b.md` (the verifiers disagreed; `.prettierignore:11` says plans are "kept exactly as approved") | (a) | the orchestrator | (a) for both files, each with one dated correction line. The plan's body and its questions' wording stay unchanged; only its approval header and its "Answer" and "Decided by" cells are filled in, from the record the orchestrator kept; decided by the orchestrator on 24 Oct 2026 |
| Q16 | W13 | `docs/plans/F1.md` ADR cells: Q13 fills each row's ADR cell with "none"; Q15 says only the approval header and the "Answer" and "Decided by" cells are filled in. (a) write "none" in the 12 ADR cells, as Q13 says; (b) leave them empty, as Q15 says | (a) | the orchestrator | (a) write "none" in all 12 ADR cells of `docs/plans/F1.md`; decided by the orchestrator on 25 Oct 2026 |

### Q13: the F1 plan's approval record

From the orchestrator's record of 6 Oct 2026 (its approval of the draft plan at commit `7269511`, sent to the F1 build session in its system prompt, which could not fold it into the plan):

- `docs/plans/F1.md:3`: "Approved by: the orchestrator, under the user's delegation (docs/orchestration/README.md), 6 Oct 2026".
- The "Decided by" cell of each row in L194-L205:
  - Row 2 (registry) and row 4 (CI and branch protection): "the user, relayed by the orchestrator on 6 Oct 2026". The user chose anonymous upstreams where the publisher offers them, a GHCR mirror for the rest with the user making the mirrored packages public, and branch protection set by the user once the checks exist on main.
  - Every other row: "the orchestrator, under the user's delegation, 6 Oct 2026".
- The "Answer" cell of each row:
  - Row 1: "accepted as recommended".
  - Row 2: "(a), adjusted: per image, an upstream that serves anonymous pulls where the publisher offers one, and the GHCR mirror only for images with none; the Docker Hub token only if runner pulls hit 429".
  - Row 3: "minimal set, with `SUPABASE_FULL=1` for the rest".
  - Row 4: "GitHub Actions; `check` always brings the stack up; branch protection is the user's action".
  - Row 5: "the `contract-change` label only; the orchestrator labels the F2, F3, F8 and CC pull requests".
  - Row 8: "yes".
  - Row 9: "yes, minimal".
  - Rows 6, 7, 10, 11 and 12: "plan default accepted".
- The ADR cell: "none" for every row, since the approval came before D2. Do not write ADR-0030 there.
- The correction line, after L3: "Approval record added on 24 Oct 2026 by lane F1b from the orchestrator's record of 6 Oct 2026; the plan's body is unchanged."
