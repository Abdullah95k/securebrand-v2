# F1 follow-up: role and brief

Written by the orchestrator on 24 Oct 2026, and revised the same day after the critic's review.

## Role and scope

You are the build session of lane **F1b**, the toolkit follow-up after D1 and D2. F1 merged as a747275 on 7 Oct, D1 as 73179c3, and D2 as 6c0f953 on 24 Oct. This is one session on one lane, branch `sb/F1b`. You fix what is still open in the repository toolkit after the F1 recheck, D1, D2 and the CI history since 7 Oct.

**Your scope:**
- the Makefile, `scripts/`, `.github/`, `.claude/` (hooks, rules and skills), `tools/repo-checks`, `stack/` and `compose.yaml`
- F1's records (`docs/handoffs/F1.md`, `docs/plans/F1.md`; how depends on Q15) and this lane's own handoff
- `CLAUDE.md`, `README.md`, `stack/README.md`, `docs/issues/README.md`, `KIT-README.md`, `build-plan/README.md`, `build-plan/tools/gen_briefs.py` and the briefs it regenerates (`build-plan/sessions/F2-*.md`, `F3-*.md`, `F8-*.md`, with Q2 (6) only), but only where an item below names them and its decision row allows it

**Never:**
- Touch `packages/contracts`, `supabase/migrations` or `clickhouse/migrations`. On `sb/F1b` the guard blocks them anyway (`.claude/hooks/guard-contracts.sh:16-19` lets only `sb/F2|sb/F3|sb/F8|sb/CC-*` through).
- Add a runtime dependency or image without a row appended at the end of `docs/dependencies.md` (`docs/dependencies.md:5`: append-only, never reformatted). The only new image this brief allows is W9's GHCR mirror of ClickHouse.

**Ground rules:**
- Facts are at origin/main 6c0f953 unless stated otherwise.
- Every item goes test first: write the repo-checks test, show it failing for the stated reason, make the change, then show it passing.
- Never claim a result you did not run.

## Preconditions and setup

1. `build-plan/sessions/F1b-*.md` exists, and `docs/plans/F1b.md` is approved (`/plan-session F1b` ran). `.claude/skills/build-session/SKILL.md:15` stops without the plan.
2. Run `make bootstrap` once (`docs/orchestration/README.md:42`). Put `nvm use 24.21.0 >/dev/null &&` in front of every pnpm command you type. Start dockerd as `docs/orchestration/README.md:41` says before `make up`.
   - At origin/main, bootstrap stops at the uv step before it installs anything (`scripts/bootstrap.sh:54`, before `pnpm install` at `:59`) when uv cannot update itself, for example a uv that pip installed (the 24 Oct report; the F1-era container had uv 0.11.32, `docs/plans/F1.md:11`). Without node_modules there is no vitest, turbo or `make check` (`scripts/check-changed.sh:84`).
   - If bootstrap stops with "uv could not update itself", run `python3 -m pip install --user --upgrade 'uv==0.12.23'` (the user's reported fix; not run here), then `PATH="$HOME/.local/bin:$PATH" make bootstrap`, and keep that PATH prefix on commands that run uv until W4 is done. Record what you ran in the handoff.
3. Right after the session starts, run `ls -la .build-state/stop-gate-*` and write the result in your handoff. W2 assumes the UserPromptExpansion hook fires when an orchestrated session starts with `/build-session` (`.claude/settings.json:71-81`). Nobody has verified that.
4. **Main's `check` is red** and stays red until W9 lands. ECR Public refuses the ClickHouse image with "toomanyrequests: Data limit exceeded": run 40136503053 on 6c0f953 failed, and its re-run (job 121016302873, 24 Oct 23:20Z) failed the same way. Expect `check` to fail on your pushes for that reason until W9's GHCR mirror is in place. Do W9 as early as its dependencies allow, and say in the handoff which push first had a green `check`. `policy` and `template-smoke` do not pull ClickHouse.
5. If origin/main has moved (for example Dependabot PR #9, which changes `.github/workflows/ci.yml`), run `git fetch origin && git merge origin/main`. Never force-push (`.claude/settings.json:43-44`).
6. **Editing live hooks.** The hooks run on this session's own tool calls and stops (`.claude/settings.json:49-93`). A syntax error makes bash exit 2. In `guard-contracts.sh` that blocks every Edit, Write and Bash call (matcher at `.claude/settings.json:51`), and the session cannot repair it. A broken `stop-gate.sh` blocks every stop. For each hook:
   - write the new version in your scratchpad
   - run `bash -n <copy>`
   - pipe a harmless payload through it and check that it exits 0: `printf '%s' '{"tool_name":"Bash","cwd":"'"$PWD"'","tool_input":{"command":"ls"}}' | bash <copy>; echo $?`
   - only then `cp` it over the hook, in a single Bash call
7. The guard scans Bash commands for writes under contract paths (`guard-contracts.sh:37-58`), and Edit and Write by `file_path` only (`:29-35`). Write test files that mention `packages/contracts` (and the migration paths) with the Write and Edit tools, never with a Bash heredoc or `echo >`.
8. **Decision rows.** The orchestrator fills the decisions table below before this session starts. If a row, or the part of a row an item needs, still reads "pending" or was declined, do not implement that item or sub-item, and leave out the test assertions that check its text. Finish the rest and list it under "Not done" in the handoff.

## Decisions (filled in before the session starts)

The orchestrator fills the last column. A row whose Decider is "the user" is the user's answer, relayed by the orchestrator, recorded as "<answer>; decided by the user, relayed by the orchestrator on <date>"; the others as "<answer>; decided by the orchestrator on <date>" (the format of `docs/orchestration/README.md:11`). Your handoff copies each Answer cell exactly, attribution included.

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

These answers replace W13's generic text for `docs/plans/F1.md:3` and `:194-205`.

## Work items, in commit order

Commit messages start with `F1b <area>: `. W1 comes first because F2 runs `/build-session` and reads these texts.

### W1. Contract lanes: the kit tells F2, F3, F8 and `/contract-change` they may edit, plus the guard's tests (KIT-1, KIT-9 part B)

**Why**
- **The hook already enforces the lanes.**
  - `guard-contracts.sh:16-19` reads the local branch and exits 0 for `sb/F2|sb/F3|sb/F8|sb/CC-*`; `:8` exits 0 when `ALLOW_CONTRACT_EDITS=1`.
  - A verifier's simulation: sb/F2, sb/F3, sb/F8 and sb/CC-F4-topic-x are allowed; sb/F1, sb/F1b, sb/C11, sb/F2-fix and a detached HEAD are blocked with "Contracts are frozen"; the bare branch `sb/CC-` is allowed.
- **The texts say the opposite.**
  - `.claude/skills/build-session/SKILL.md:33`: "Never edit `packages/contracts` or the migrations...". F2 runs this skill.
  - `CLAUDE.md:12` makes no exception for the contract lanes.
  - `.claude/rules/contracts.md:10` names only `ALLOW_CONTRACT_EDITS=1`.
  - `.claude/skills/contract-change/SKILL.md:3` and `:11` (step 1) stop unless the variable prints 1, yet `docs/orchestration/README.md:40` says it cannot be set in a cloud session. So a cloud `/contract-change` on `sb/CC-<proposal>` stops at step 1.
  - The F2 brief relies on the variable too (`build-plan/sessions/F2-contracts-package.md:37`, generated by `build-plan/tools/gen_briefs.py:314`).
- **Step 7 of contract-change does not match the policy parser.** `contract-change/SKILL.md:17` says "Mark the proposal "applied" with the commit". `scripts/policy/check-handoff-review.sh:53-54` takes the SHA only from the start of the `Applied:` value, so `applied (abc1234)` yields an empty SHA and fails at `:57-58` (the sed was tested).
- **plan-session misfits F2, F3 and F8.** `.claude/skills/plan-session/SKILL.md:27` tells every plan to confirm the contracts exist and to file missing ones as proposals, which is wrong for the three sessions that create them.
- **No repo-check covers the hook.** `git grep guard-contracts -- tools/repo-checks` finds nothing. `cleanEnv` does not strip `ALLOW_CONTRACT_EDITS` or `CLAUDE_PROJECT_DIR` (`tools/repo-checks/test/helpers/repo.ts:52-87`), so a test run from a session started with the variable would pass every "blocks" case without testing anything.

**Test first**
- In `tools/repo-checks/test/helpers/repo.ts`, add `"ALLOW_CONTRACT_EDITS"` and `"CLAUDE_PROJECT_DIR"` to the keys `cleanEnv` deletes (the list at `:69-81`).
- New `tools/repo-checks/test/helpers/hooks.ts`:
  - `export const HOOKS = join(ROOT, ".claude", "hooks")`
  - `export function runHook(name: string, payload: object, opts: { cwd: string; env?: NodeJS.ProcessEnv }): RunResult { return run("bash", [join(HOOKS, name)], { cwd: opts.cwd, env: cleanEnv(opts.env), input: JSON.stringify(payload) }); }`
- New `tools/repo-checks/test/unit/guard-contracts.test.ts`, `describe(".claude/hooks/guard-contracts.sh")`.
  - `beforeEach`: `repo = new TempRepo("guard-"); repo.write("README.md","x\n").commit("base"); repo.branch("sb/X")`.
  - Payload: `{ tool_name, cwd: repo.dir, tool_input: {...} }`.
  - First, `expect` jq on PATH. The hook fails open without jq (`:9`).
  - Cases, with P each of `packages/contracts/src/a.ts`, `supabase/migrations/20261007000000_a.sql` and `clickhouse/migrations/0001_a.sql`:
    1. `blocks %s to %s on sb/X`, over Edit, Write and MultiEdit: code 2, and stderr contains "Contracts are frozen" and "docs/proposals/".
    2. `blocks a NotebookEdit whose notebook_path is under a contract path`.
    3. `blocks absolute, relative and backslash paths alike`.
    4. `allows writes outside the frozen paths, near-miss names included`: `services/a/src/x.ts`, `packages/contracts-extra/x.ts`, `supabase/migrations.md` and `docs/proposals/X-a.md` give code 0.
    5. `allows Write and Bash writes to every frozen path on %s`, over sb/F2, sb/F3, sb/F8 and sb/CC-foo.
    6. `still blocks on %s`, over sb/F1, sb/F1b, sb/F2x, sb/F20, sb/CCfoo, main and (with Q2 (5)) `sb/CC-`, plus a detached HEAD. `sb/CC-` fails today: it is the test for (5).
    7. `allows every write when ALLOW_CONTRACT_EDITS=1`.
    8. `blocks the Bash write \`%s\`` for `>`, `>>`, `tee`, `tee -a`, `sed -i`, `sed --in-place`, `cp`, `mv`, `rm`, `touch`, `truncate -s0`, `git checkout -- P`, `git restore P`, `git rm P` and `cd P && echo x > a`, over all three paths.
    9. `blocks a relative write or touch when the cwd is inside a contract path`.
    10. `allows the Bash read \`%s\`` for `cat P/a`, `ls P`, `git diff -- P`, `grep -r x P`, `git commit -m "touch P"` and `echo x > services/a/x.ts`.
    11. Q3 (a): `known gap, CI is the backstop: a quoted target is not matched`. `cp a "P/a"` and `echo x > "P/a"` expect code 0. Add a comment naming `guard-contracts.sh:39-40` and `scripts/policy/check-contract-paths.sh`. Q3 (b): write these as `it.fails` first, then harden the guard.
    12. `the kit tells the contract lanes they may edit`, one assertion per file, matching the texts below:
        - `.claude/rules/contracts.md` contains "F2, F3 and F8", `sb/F2` and `sb/CC-`
        - `.claude/skills/build-session/SKILL.md` contains "F2, F3 and F8", `sb/$0` and `ALLOW_CONTRACT_EDITS=1`
        - `.claude/skills/contract-change/SKILL.md` contains `sb/CC-` and `ALLOW_CONTRACT_EDITS=1`
        - `CLAUDE.md` (Q1 (a) only) contains "F2, F3 and F8" and `sb/CC-`

        Under Q1 (b), leave out the `CLAUDE.md` assertion; under Q1 (c), leave out case 12. Each assertion fails at origin/main: `.claude/rules/contracts.md:10` reads "F2, F3, F8 or" and names no branch, the build-session skill names no lane, and contract-change has no `sb/CC-`.
  - Expected before the change: everything passes except case 6 (`sb/CC-`, with Q2 (5)) and case 12.

**Change** (Q1 and Q2)
1. `.claude/rules/contracts.md:10`, replace with: "- These paths change only in F2, F3 and F8, and in `/contract-change` applying an approved proposal from `docs/proposals/`. Such a session runs on its lane branch, `sb/F2`, `sb/F3`, `sb/F8` or `sb/CC-<proposal>` (the cloud's way, where `ALLOW_CONTRACT_EDITS` cannot be set), or was started with `ALLOW_CONTRACT_EDITS=1`. `.claude/hooks/guard-contracts.sh` blocks every other session, and the policy job fails a pull request that changes these paths without the `contract-change` label."
2. `.claude/skills/build-session/SKILL.md:33`, replace with: "- `packages/contracts`, `supabase/migrations` and `clickhouse/migrations`: F2, F3 and F8 write what their plan names there, on their lane branch `sb/$0` or with `ALLOW_CONTRACT_EDITS=1`, following `.claude/rules/contracts.md`. Every other session never edits them: if you need a change, write `docs/proposals/$0-<topic>.md` from the template and stop."
3. `.claude/skills/contract-change/SKILL.md`:
   - L3, end of the description: "Only on the branch sb/CC-<proposal>, or in a session started with ALLOW_CONTRACT_EDITS=1."
   - L11, step 1: "1. Run `git rev-parse --abbrev-ref HEAD` and `echo \"${ALLOW_CONTRACT_EDITS:-0}\"`. Go on only if the branch is `sb/CC-<proposal>`, where `<proposal>` is the proposal's file name without `.md`, or the second command prints 1. The pull request's branch must be `sb/CC-<proposal>` in both cases, because the policy check reads `docs/proposals/<proposal>.md` from it. Otherwise stop and tell me to restart on that branch, or with `ALLOW_CONTRACT_EDITS=1 claude --worktree CC-<proposal>`."
4. `CLAUDE.md:12` (Q1 (a) only), replace with: "- IMPORTANT: contracts are frozen. Only F2, F3 and F8, which build them, and `/contract-change` applying an approved proposal on `sb/CC-<proposal>` edit `packages/contracts`, `supabase/migrations` or `clickhouse/migrations` (`.claude/rules/contracts.md`). Every other session never edits them (a hook blocks it): if you need a change, write `docs/proposals/<session>-<topic>.md` from `build-plan/templates/PROPOSAL.md` and stop."
5. (Q2 (5)) `guard-contracts.sh:18` becomes `  sb/F2|sb/F3|sb/F8|sb/CC-?*) exit 0 ;;`. Leave the block message at `:25` as it is: it tells a blocked session to write a proposal, and naming the branch names that pass would invite a branch switch instead; the lane rule lives in `.claude/rules/contracts.md`. Apply the live-hook procedure from setup step 6.
6. (Q2 (6)) Add "or runs on its lane branch sb/<ID> (cloud)" to:
   - `KIT-README.md:11`
   - `build-plan/README.md:21` and `:24`
   - `build-plan/tools/gen_briefs.py:314`, the F2, F3 and F8 trap text. That line is a plain string, so make it an f-string and write the branch as `sb/{i}`, for example `f'Start this session with ALLOW_CONTRACT_EDITS=1, or run it on its lane branch sb/{i} (cloud): it is one of the few allowed to write the contract paths'`. Leave `:183` (the "How to run it" lines, F2 brief L51 and L54) as it is: those are local terminal commands, where the variable works.

   Then run `python3 build-plan/tools/gen_briefs.py . build-plan/tools/prd_index.json build-plan/tools/prd_io.json`. At origin/main the generator reproduces all 125 briefs and `SESSIONS.md` byte for byte (checked in memory on 24 Oct: 126 files written, 0 differ; the critic confirmed it). So `git diff --stat build-plan/` must list only `gen_briefs.py`, the F2, F3 and F8 briefs, and the two README lines. Check that each of the three briefs shows `sb/F2`, `sb/F3` or `sb/F8`, not a literal `{i}`. Then run `python3 build-plan/tools/validate.py`, which prints `errors []`.
7. (Q2 (7)) `.claude/skills/plan-session/SKILL.md:27`: append "(F2, F3 and F8: list what this session creates, from the ADRs and CONVENTIONS, instead)".
8. (Q2 (8)) `.claude/skills/contract-change/SKILL.md:17`, replace with: "7. Commit the change; then set the proposal's `Applied:` line to that commit's SHA alone (`Applied: <sha>`), in a second commit on this branch, and stop. The policy check reads the SHA at the start of the line and requires it to be part of the branch."

**Verify:** `bash -n .claude/hooks/guard-contracts.sh`, then `make test SERVICE=repo-checks` (or the unit file alone, if your permissions allow: `nvm use 24.21.0 >/dev/null && pnpm --filter repo-checks exec vitest run test/unit/guard-contracts.test.ts`). All cases pass.

### W2. Stop gate: only a proposal or issue filed in this session lets Claude stop, the gate never passes silently, and the hook tests (KIT-2, KIT-9 parts C and D)

**Why**
- **Arming records nothing.** `.claude/hooks/arm-stop-gate.sh:14` creates an empty marker file (`touch`).
- **Any old proposal or issue switches the gate off.** `stop-gate.sh:29` searches the whole branch diff from the merge base (`:23-24`) for anything under `docs/proposals/` or `docs/issues/`. `:30-34` then exit 0 with "Checks were not enforced".
  - On a lane, fix sessions run on the same branch after the build session (`docs/orchestration/README.md:15`, `:19`), so a fix session that sees an issue the build session filed is never gated. The verifier's probe of the hook at origin/main (case C) gave `exit=0 ... filed: docs/issues/X-1.md`.
  - The same happens for (the verifier's cases):
    - an issue merged in from main while origin/main is stale (case E)
    - an edit to, or deletion of, the README of `docs/issues/` or `docs/proposals/` (cases F and G)
    - an untracked file left over from before arming (case M)
    - a file deleted and re-added (case O)
- **Without a merge base the gate passes silently.**
  - `:23` falls back to `git rev-parse HEAD`, so committed changes become invisible, and `:36-39` exit 0 without running the checks. This was probed in a single-branch clone (case H) and in a depth-1 clone.
  - That contradicts the promise at `scripts/check-changed.sh:14-15`.
- **Quoted file names are missed.** `:24` lists files without `-c core.quotePath=false`, so a quoted name was missed in a demonstration. `scripts/lib/common.sh:91-96` (`sb_changed_files`) does it right.
- **The gate is narrower than `make check`.** `:36` and `:42` look only at `^(services|packages|py|tools)/`. `make check` also tests root tooling (`scripts/check-changed.sh:59`), and the policy gates `tests/` (`check-handoff-review.sh:69`). This was inferred from the code, not run.
- **fix-session's text is missing the exemption.** `.claude/skills/fix-session/SKILL.md:11` lacks the exemption that `arm-stop-gate.sh:15` and `build-session/SKILL.md:11` state.
- **No q-file convention exists.** `docs/issues/README.md:3` defines only `<ID>-<n>.md`, while workers stop with `ORCHESTRATOR: NEEDS-INPUT` (`docs/orchestration/README.md:29-31`). With failing checks, such a stop is held for up to 3 rounds (`stop-gate.sh:53-58`).
- **No behavioural test exists.** `tools/repo-checks/test/unit/kit-fit.test.ts:66-72` only checks that the hook contains a string.

**Test first:** new `tools/repo-checks/test/unit/stop-gate.test.ts`, `describe(".claude/hooks/stop-gate.sh and arm-stop-gate.sh")`.
- `beforeEach` builds a TempRepo on main with:
  - a `.gitignore` containing `.build-state/`
  - `docs/issues/README.md`, `docs/proposals/README.md` and `services/a/index.ts`
  - a stub `scripts/check-changed.sh` (mode 0o755) that appends a line to `.build-state/stub-runs`, prints `stub check` and exits `${STUB_CHECK_EXIT:-1}`. Do not use a `TEST_` prefix: `cleanEnv` strips it.

  Then it commits "base" and branches `sb/X`.
- Helpers:
  - `arm(s)` = `runHook("arm-stop-gate.sh", { session_id: s, cwd: repo.dir, hook_event_name: "UserPromptExpansion" }, { cwd: repo.dir })`
  - `stop(s, exit)` = `runHook("stop-gate.sh", { session_id: s, cwd: repo.dir, permission_mode: "default", hook_event_name: "Stop", stop_hook_active: false }, { cwd: repo.dir, env: { STUB_CHECK_EXIT: String(exit) } })`
- Cases:
  1. arming prints the armed notice and records the commit HEAD is on, and the proposals and issues that exist (fails today)
  2. lets an unarmed session stop while the checks fail, without running them
  3. lets a plan-mode session stop
  4. blocks an armed session while the checks for changed code fail, and shows the log tail: code 2, and stderr contains "make check failed (round 1 of 3)" and "stub check"
  5. lets an armed session stop when the checks pass, and does not rerun them for an unchanged tree: `stub-runs` has 1 line after two stops
  6. reruns the checks after the code changes again
  7. lets Claude stop after three failed rounds, naming the log: the 4th stop gives code 0 and "after 3 rounds"
  8. does not run the checks when only `docs/` changed
  9. `lets Claude stop with a q-file docs/issues/X-q1.md filed after arming (%s)`, over untracked, staged and committed: code 0 and a systemMessage naming the file
  10. lets Claude stop with a proposal filed after arming
  11. ignores an issue an earlier session committed on the lane before arming: code 2 (fails today)
  12. ignores an issue merged in from main even when origin/main is stale, in both merge shapes. Run `repo.git("update-ref","refs/remotes/origin/main", base)` first, and arm before the merge; then a code change, stub failing.
      - (a) a true merge: an own commit on sb/X (for example `services/a/b.ts`), then `docs/issues/Y-1.md` committed on main, then `git merge --no-ff main` on sb/X. Code 2 (fails today).
      - (b) a fast-forward: no own commit, `docs/issues/Y-1.md` committed on main, then `git merge --ff-only main` on sb/X. Code 2 (fails today). A fast-forward puts main's commit on sb/X's first-parent line, so this case fails with an "own first-parent commits" rule alone (shown by the critic on a scratch copy: `exit=0 ... filed: docs/issues/Y-1.md`).
  13. ignores an untracked q-file left in the worktree before arming: code 2 (fails today)
  14. ignores edits to, or the deletion of, the docs/issues and docs/proposals READMEs: code 2 (fails today)
  15. ignores a file that existed at arming and was deleted and re-added: code 2 (fails today)
  16. re-arming in the same session keeps the first arm point
  17. runs the checks when the branch has no merge base with main (an orphan branch with code committed, stub failing): code 2 (fails today)
  18. (Q5) blocks an armed session whose only change is under `scripts/` or `tests/e2e/` while the checks fail: code 2 (fails today)
  19. (KIT-9 part D, optional, in `kit-fit.test.ts`) settings.json wires the contract guard, the arm hook and the stop gate. Assert the PreToolUse matcher `Edit|Write|MultiEdit|NotebookEdit|Bash` runs guard-contracts.sh, UserPromptExpansion `build-session|fix-session` runs arm-stop-gate.sh, and Stop runs stop-gate.sh (`.claude/settings.json:49-93`).

**Change** (apply the live-hook procedure to both hooks)

1. `.claude/hooks/arm-stop-gate.sh:14`, replace with:
```bash
STATE="$ROOT/.build-state"
ARM_FILE="$STATE/stop-gate-$SESSION"
mkdir -p "$STATE" || exit 0
# Record the arm point once per session: the commit HEAD was on, and every proposal and issue that
# already existed (tracked or untracked). Only files filed after this point let Claude stop early.
if [ ! -s "$ARM_FILE" ]; then
  git -C "$ROOT" -c core.quotePath=false ls-files --cached --others --exclude-standard -- docs/proposals docs/issues \
    | sort -u >"$ARM_FILE.filed-before"
  git -C "$ROOT" rev-parse --verify -q HEAD >"$ARM_FILE" || echo none >"$ARM_FILE"
fi
```
   (Q2 (9)) Reword `:15` to say "file a new one under docs/proposals/ or docs/issues/". With Q4 (a), add "(an open question: docs/issues/<ID>-q<n>.md)".

2. `.claude/hooks/stop-gate.sh`:
   - **`:23-24`**: take the base and the file list from the kit's shared helpers. Source them from the hook's own repository, not `$ROOT`, because the test repositories hold only a stub `check-changed.sh`:
```bash
KIT_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../scripts/lib" 2>/dev/null && pwd)/common.sh"
if [ -r "$KIT_LIB" ]; then
  BASE="$( . "$KIT_LIB" && sb_merge_base 2>/dev/null )"
  ALL="$( [ -n "$BASE" ] && . "$KIT_LIB" && sb_changed_files "$BASE" 2>/dev/null )"
else
  BASE="$(git merge-base HEAD origin/main 2>/dev/null || git merge-base HEAD main 2>/dev/null || true)"
  ALL="$( [ -n "$BASE" ] && { git -c core.quotePath=false diff --no-renames --name-only "$BASE"; git -c core.quotePath=false ls-files --others --exclude-standard; } 2>/dev/null )"
fi
```
   - **`:29`**: replace with this block (`:30-34` stay; optionally say "filed in this session"):
```bash
# Only a proposal or issue filed in this session lets Claude stop with failing checks: a .md file
# under docs/proposals/ or docs/issues/ (README.md excluded) that exists now, was not there when the
# gate was armed, and is not yet committed or was added after the arm commit by this branch's own
# commits. Files from earlier sessions on the lane, or brought in from main (by a merge or a
# fast-forward), never count.
ARM_FILE="$STATE/stop-gate-$SESSION"
ARM="$(head -n1 "$ARM_FILE" 2>/dev/null)"
FILED=""
if [ -n "$ARM" ] && [ "$ARM" != none ] && git rev-parse --verify -q "$ARM^{commit}" >/dev/null &&
  [ -f "$ARM_FILE.filed-before" ]; then
  OWN="$(git rev-list --first-parent --no-merges "$ARM..HEAD")"
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    grep -qxF -- "$f" "$ARM_FILE.filed-before" && continue
    if git cat-file -e "HEAD:$f" 2>/dev/null; then
      added_by="$(git log -n1 --format=%H --diff-filter=A HEAD -- "$f")"
      [ -n "$added_by" ] && grep -qxF -- "$added_by" <<<"$OWN" || continue # brought in by a merge
      from_main=0 # a fast-forward of main puts main's commits on the first-parent line too
      for ref in origin/main main; do
        git merge-base --is-ancestor "$added_by" "$ref" 2>/dev/null && from_main=1
      done
      [ "$from_main" = 0 ] || continue
    fi
    FILED="$FILED$f "
  done < <({
    git -c core.quotePath=false diff --no-renames --name-only --diff-filter=A "$ARM" -- docs/proposals docs/issues
    git -c core.quotePath=false ls-files --others --exclude-standard -- docs/proposals docs/issues
  } | grep -E '^docs/(proposals|issues)/[^/]+\.md$' | grep -vE '/README\.md$' | sort -u)
fi
```
   - **`:36-45`**:
     - When `BASE` is empty, skip the path test (`:36`) and the fingerprint shortcut (`:41-45`), and run `scripts/check-changed.sh`, which then checks everything (`check-changed.sh:39-43`). Do not diff against the empty tree: the READMEs would count as changes.
     - With Q5 yes, replace the `:36` test with "any changed path outside `^(docs|build-plan)/`", for example `printf '%s\n' "$ALL" | grep -v '^$' | grep -qvE '^(docs|build-plan)/'`. Widen the `:42` fingerprint the same way: `git diff "$BASE" -- . ':(exclude)docs' ':(exclude)build-plan'`, plus the untracked files outside those two folders.
   - An arm file in the old, empty format gives no filing exemption until the session is armed again; the 3-round escape (`:53-58`) still applies. Your own session was armed by the old hook and nobody can re-type `/build-session` in it (`docs/orchestration/README.md:29`), so for this session only the 3-round escape applies.
3. (Q2 (9)) `.claude/skills/fix-session/SKILL.md:11`: append "or after filing a proposal or an issue in this session".
4. (Q4 (a)) Document the q-file convention:
   - `docs/issues/README.md`: add "An open question that blocks the session is `docs/issues/<ID>-q<n>.md`: the question, the options and a recommendation; it lets the stop gate end the session".
   - `.claude/skills/build-session/SKILL.md:34`: add a sentence naming `docs/issues/$0-q<n>.md` for a question you stop on.
   - `.claude/skills/fix-session/SKILL.md`: the same sentence.

   The orchestrator updates `docs/orchestration/README.md:29-31` itself.

**Verify:** `bash -n` on both hooks, then `make test SERVICE=repo-checks`. Cases 1 to 18 pass; those test results are the only evidence for the new hooks.

### W3. Install step: `make bootstrap`, not a bare `pnpm install` (MS-1)

**Why**
- `.claude/skills/build-session/SKILL.md:17` says "install first: `pnpm install`, and `uv sync`...". This line has been unchanged since day zero.
- A bare `pnpm install` fails on the cloud shell's Node 22: `.npmrc:1` sets `engine-strict=true` and `package.json:7` requires `>=24.21.0 <25`. This was reproduced: `ERR_PNPM_UNSUPPORTED_ENGINE`.
- Other remedies name a bare `pnpm install` too:
  - `scripts/check-changed.sh:84` (shown to Claude by the Stop hook)
  - `scripts/doctor.sh:79` and `:81`
  - `scripts/stack-env.sh:47`
- `make bootstrap` does both installs (`scripts/bootstrap.sh:59-64`).
- When turbo prints nothing, `check-changed.sh:81-84` prints a JSON SyntaxError stack trace before the `sb_die` line (seen in a throwaway clone).

**Test first:** in `kit-fit.test.ts`, add `it("skills, rules, agents and hooks name make bootstrap as the install step, never a bare pnpm install or uv sync")`.
- Read every file under `.claude/skills`, `.claude/rules`, `.claude/agents` and `.claude/hooks`, and expect none to match /`pnpm install`|`uv sync`/.
- Expect `build-session/SKILL.md` to contain "make bootstrap" (with Q2 (10) only).
- Expect `scripts/check-changed.sh` to contain "(run make bootstrap)" and not "(run pnpm install)".
- It fails at `SKILL.md:17` and `check-changed.sh:84`.

**Change**
1. (Q2 (10)) `SKILL.md:17`, replace with: "- In a fresh worktree or a fresh cloud container, run `make bootstrap` first. It installs the pinned Node, pnpm, uv and Python, runs `pnpm install --frozen-lockfile` and `uv sync --locked` in every Python project, and ends with `make doctor`. In a cloud session, put `nvm use 24.21.0 >/dev/null &&` in front of any `pnpm` command you type yourself."
2. `check-changed.sh`:
   - `:84`: change the message to `(run make bootstrap)`.
   - `:81-84`: the script runs under `set -euo pipefail` (`:19`), so a bare assignment from a failing turbo would end it silently. Capture turbo's output with a fallback, then die on an empty answer, so only one line reaches the session:
```bash
  TURBO_JSON="$("${TURBO[@]}" ls ${TURBO_FILTERS[@]+"${TURBO_FILTERS[@]}"} --output json 2>/dev/null || true)"
  [ -n "$TURBO_JSON" ] || sb_die "turbo could not list the workspaces (run make bootstrap)"
  TS_PACKAGES="$(node -e 'const j = JSON.parse(require("fs").readFileSync(0, "utf8"));
           console.log(j.packages.items.map((p) => p.name).sort().join(" "));' <<<"$TURBO_JSON" 2>/dev/null)" ||
    sb_die "turbo's workspace list could not be read (run make bootstrap)"
```
3. Change the remedy to "make bootstrap" in `doctor.sh:79` and `:81` and in `stack-env.sh:47`. No test asserts those strings (`git grep` at origin/main).
4. Leave `.claude/settings.json:24-25` (the `pnpm install` and `uv sync` allows) and `tools/new-service/index.mjs:210` as they are.

### W4. Bootstrap: offline re-run for Node, and uv installed by pip (NOTE-9, UV-SELF-UPDATE)

**Why**
- **Node: every run downloads.**
  - `scripts/bootstrap.sh:19-20` enters the nvm block whenever the caller's node is not the pin, which is every time in the cloud (the shells start on `/opt/node22`, `docs/handoffs/F1.md:134`).
  - `:31` then runs `nvm install` every time. nvm 0.39.7 downloads `index.tab` before it checks for an installed version (`/opt/nvm/nvm.sh` L3271 and L1509, versus L3356).
  - Offline, `nvm install` exits 3 even though v24.21.0 is installed (reproduced). This is recheck note 9 (`docs/reviews/F1.md:204`).
  - `:22` searches `"${NVM_DIR:-}" "$HOME/.nvm" /opt/nvm`; `scripts/lib/common.sh:36` also searches `/usr/local/nvm`.
- **uv: the update only works for the standalone installer.**
  - `bootstrap.sh:51-55` runs `uv self update "$UV_MIN" || sb_die "uv could not update itself; ..."`. That is the error reported on 24 Oct. It fails, with exit 2 (reproduced), for a uv without a standalone install receipt, such as one pip installed.
  - `scripts/doctor.sh:62` gives the same remedy.
  - The pip `--user` fix comes from the user's report and was not run here.

**Test first:** in `tools/repo-checks/test/unit/doctor.test.ts`, under `describe("make bootstrap (scripts/bootstrap.sh)")`, reusing the stand-ins of `:56-90`. Every new test sets `HOME` to a fresh temp directory in `cleanEnv({...})`: `cleanEnv` keeps the developer's HOME (`test/helpers/repo.ts:52-87`), the test runs the real bootstrap in the real checkout (`doctor.test.ts:77-81`), and the new uv step falls back to `$HOME/.local/bin/uv`. In this container that is a real uv 0.12.23 (`/root/.local/bin/uv`), so without a temp HOME test (d) would go on to run the real `uv python install` and `uv sync --locked` in every Python project (`bootstrap.sh:56-64`).
- (a) `runs no nvm command when nvm already holds the pin as its default, so a second run needs no network`.
  - Set up `nvm/versions/node/v$PIN/bin/node`, plus `nvm/alias/default` containing the pin (the format real nvm writes: `/opt/nvm/alias/default` holds `24.21.0`).
  - Stand-in nvm.sh: `nvm() { echo "nvm $*" >> calls; [ "$1" = install ] && return 3; return 0; }`
  - Shell node 22.22.0.
  - Expect no `nvm install` or `nvm alias` line, and output containing `bootstrap: node v${NODE_PIN}`.
  - It fails today.
- (b) `stops naming nodejs.org when nvm lacks the pin and nvm install fails`: expect a non-zero exit and /nvm could not install Node .*nodejs\.org/.
- (c) `installs the pinned uv with pip --user when uv self update fails because pip installed uv`.
  - The uv stand-in answers `--version` from a state file that starts at "uv 0.11.32", exits 2 on `self update`, and records every other call.
  - A python3 stand-in exits 0 on `-m pip show uv`. On `-m pip install ...` it records the call and writes "uv <floor>" to the state file. Anything else goes to the real python3, at an absolute path the test resolves.
  - Expect the calls to contain `python3 -m pip install --user --quiet --upgrade uv==${uvFloor}` and `uv python install ${PYTHON_PIN}`, and the output not to contain "could not update itself".
  - It fails today at `:54`.
- (d) `stops naming the uv it found when uv is still outside the range after the update`: the state file stays at 0.11.32 and the temp HOME has no `.local/bin/uv`. Expect /uv is still 0\.11\.32/.
- (e) `uses ~/.local/bin/uv when pip put the pin there behind another uv on PATH, and says to put ~/.local/bin first`: as (d), plus a recording uv stand-in at `<temp HOME>/.local/bin/uv` that answers "uv <floor>". Expect the output to contain "put ~/.local/bin first" and that stand-in to record `python install ${PYTHON_PIN}`.
- The existing test at `:56-90` must still pass. Its stand-in has the version directory and no `alias/default`, so it still records `nvm alias default`.

**Change**
1. `bootstrap.sh:17-36` (step 1), replace with:
```bash
shell_node="$(PATH="$SB_CALLER_PATH" node --version 2>/dev/null || true)"
if [ "$(node --version 2>/dev/null)" != "v$NODE_PIN" ] || [ "$shell_node" != "v$NODE_PIN" ]; then
  nvm_dir=""
  for dir in "${NVM_DIR:-}" "$HOME/.nvm" /opt/nvm /usr/local/nvm; do
    if [ -n "$dir" ] && [ -s "$dir/nvm.sh" ]; then nvm_dir="$dir"; break; fi
  done
  if [ -n "$nvm_dir" ]; then
    # nvm install downloads nodejs.org's index even for an installed version (nvm 0.39): only when missing.
    if [ ! -x "$nvm_dir/versions/node/v$NODE_PIN/bin/node" ]; then
      echo "bootstrap: installing Node $NODE_PIN with nvm (downloads from nodejs.org)"
      # shellcheck disable=SC1091
      (set +eu && . "$nvm_dir/nvm.sh" && nvm install "$NODE_PIN" >/dev/null) ||
        sb_die "nvm could not install Node $NODE_PIN; it needs nodejs.org: run make bootstrap again with network"
    fi
    if [ "$(tr -d '[:space:]' <"$nvm_dir/alias/default" 2>/dev/null)" != "$NODE_PIN" ]; then
      echo "bootstrap: making Node $NODE_PIN nvm's default"
      # shellcheck disable=SC1091
      (set +eu && . "$nvm_dir/nvm.sh" && nvm alias default "$NODE_PIN" >/dev/null) ||
        sb_die "nvm alias default $NODE_PIN failed"
    fi
    sb_select_node
  elif [ "$(node --version 2>/dev/null)" != "v$NODE_PIN" ]; then
    sb_die "Node $NODE_PIN is needed: install it with nvm, fnm, volta or mise (they read .node-version), then run make bootstrap again"
  fi
fi
```
2. `bootstrap.sh:46-56` (step 3), replace with:
```bash
if ! command -v uv >/dev/null 2>&1; then
  sb_die "uv $UV_MIN is needed: https://docs.astral.sh/uv/getting-started/installation/ (then make bootstrap again)"
fi
version_ge() { [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -1)" = "$2" ]; }
uv_ok() { version_ge "$1" "$UV_MIN" && ! version_ge "$1" "$UV_BELOW"; }
uv_version() { uv --version 2>/dev/null | awk '{print $2}'; }
current="$(uv_version)"
if ! uv_ok "$current"; then
  echo "bootstrap: uv $current -> $UV_MIN"
  if uv self update "$UV_MIN"; then
    :
  elif python3 -m pip show uv >/dev/null 2>&1; then
    echo "bootstrap: uv came from pip; installing uv $UV_MIN with pip --user"
    python3 -m pip install --user --quiet --upgrade "uv==$UV_MIN" ||
      sb_die "pip could not install uv $UV_MIN: run python3 -m pip install --user --upgrade 'uv==$UV_MIN', then make bootstrap again"
  else
    sb_die "uv $current could not update itself and pip does not own it: install uv $UV_MIN with the official installer (curl -LsSf https://astral.sh/uv/$UV_MIN/install.sh | sh) or your package manager, then make bootstrap again"
  fi
  hash -r
  current="$(uv_version)"
  if ! uv_ok "$current" && [ -x "$HOME/.local/bin/uv" ] && uv_ok "$("$HOME/.local/bin/uv" --version | awk '{print $2}')"; then
    PATH="$HOME/.local/bin:$PATH"; export PATH; hash -r; current="$(uv_version)"
    echo "bootstrap: uv $UV_MIN is in ~/.local/bin, behind another uv on your PATH: put ~/.local/bin first"
  fi
  uv_ok "$current" || sb_die "uv is still $current ($(command -v uv)) after the update; install uv $UV_MIN, then make bootstrap again"
fi
echo "bootstrap: uv $current"
uv python install "$PYTHON_PIN"
```
   With Q6 (b), replace the final `else` branch with `curl -LsSf https://astral.sh/uv/$UV_MIN/install.sh | env UV_NO_MODIFY_PATH=1 sh`, followed by the same version check.
3. Update the header comment at `bootstrap.sh:3-5`: nvm is also searched in `/usr/local/nvm`, and uv reaches the pin through `uv self update`, or through `pip --user` when pip installed it.
4. `doctor.sh:62` remedy: "(make bootstrap updates it: uv self update $UV_MIN, or python3 -m pip install --user 'uv==$UV_MIN' when pip installed uv)".

**Not verified:** whether the rest of a second `make bootstrap` is offline (`pnpm --version` switching from 10.28.0 to 10.34.6 at `:44`, `uv python install` at `:56`, `pnpm install` at `:59`). If you can test it, record the result in the handoff; otherwise say "not verified".

### W5. No version checks from pyright-python and the Supabase CLI (A27)

**Why**
- A27 (no network in tests) is "pass for what finding 2 named; not met to the letter" (`docs/reviews/F1.md:196`).
- pyright-python queries pypi.org on every `uv run pyright` (`docs/reviews/F1.md:221`; call site `scripts/check-changed.sh:180`).
- The Supabase CLI asks for its latest release on `supabase --version` (`docs/reviews/F1.md:223`; `scripts/doctor.sh:78`). CI logs show "A new version of Supabase CLI is available" (job 120926594226, log lines 810-811 and 927-928).
- Nothing sets either variable. `git grep` finds them only in `docs/handoffs/F1.md:148` and `docs/reviews/F1.md:221-225`.
- `scripts/lib/common.sh:9` exports only `TURBO_TELEMETRY_DISABLED`, and every script sources common.sh.
- The name `SUPABASE_NO_UPDATE_NOTIFIER` comes from the F1 recheck; the verifier did not check it (the CLI is not installed in its checkout).

**Test first:** new test `every script turns off pyright-python's and the Supabase CLI's version checks` (in `doctor.test.ts` or a new `tools/repo-checks/test/unit/common.test.ts`).
- Run `run("bash", ["-c", `. ${SCRIPTS}/lib/common.sh; printf '%s %s' "$PYRIGHT_PYTHON_IGNORE_WARNINGS" "$SUPABASE_NO_UPDATE_NOTIFIER"`], { cwd: ROOT, env: cleanEnv({ PYRIGHT_PYTHON_IGNORE_WARNINGS: undefined, SUPABASE_NO_UPDATE_NOTIFIER: undefined }) })`.
- Expect `1 1`. It fails today.

**Change:** in `scripts/lib/common.sh`, after `:9`:
```bash
# No version checks from the tools the scripts run (A27, no network in tests): pyright-python asks
# pypi.org for pyright's latest version on every run; the Supabase CLI asks for its latest release.
export PYRIGHT_PYTHON_IGNORE_WARNINGS=1
export SUPABASE_NO_UPDATE_NOTIFIER=1
```

**Verify after merge:** a CI `check` log no longer prints "A new version of Supabase CLI is available".

### W6. Shallow clones find the merge base (SHALLOW-BASE)

**Why**
- `scripts/lib/common.sh:63-70` (`sb_merge_base`) never checks for a shallow clone and never fetches.
- `git clone --depth 1` implies `--single-branch`, so there is no origin/main and `sb_merge_base` prints nothing. With origin/main fetched at depth 1, `git merge-base` still fails. Both cases were reproduced.
- `check-changed.sh:40-42` then warns "no merge base with main" and runs the full check, without naming shallowness or the fix.
- `.claude/skills/review-session/SKILL.md:17` runs `git diff origin/main...HEAD`, which fails in a shallow clone ("fatal: origin/main...HEAD: no merge base", reproduced).
- CI is not affected (`fetch-depth: 0` at `ci.yml:37` and `:105`, and `policy.yml:36`).
- Whether worker containers are shallow is not verified (create_session's `clone_depth` defaults to 50).

**Test first:** in `tools/repo-checks/test/unit/check-changed.test.ts`. There is no network: the origin is a local bare repository reached over file://.
- (a) `fetches main's history in a shallow clone and compares with the real merge base`.
  - Commit a change to `packages/a` on sb/T1.
  - `git clone -q --bare <repo> <tmp>/origin.git`
  - `git -c protocol.file.allow=always clone -q --depth 1 --branch sb/T1 file://<tmp>/origin.git <tmp>/shallow`
  - Run `script("check-changed.sh", ["--plan"], { cwd: shallow })`.
  - Expect `plan.base` to be main's SHA, `plan.ts` toEqual(["a","b"]) (following the existing plan tests), stderr matching /shallow clone/, and `git rev-parse --is-shallow-repository` printing false afterwards.
- (b) `names the shallow clone and git fetch --unshallow when main cannot be fetched`: run `git remote set-url origin file:///nonexistent` first. Expect base "none" and stderr matching /git fetch --unshallow origin main/.
- (c) optional: `SB_NO_FETCH=1 leaves the clone shallow`.
- (d) verify-first: `make policy in a shallow clone compares with the merge base, not main's tip`.
  - `sb_policy_base` (`common.sh:81`) falls back to the ref itself; this is inferred, not run.
  - If (d) fails at origin/main, call `sb_unshallow_for_base` before that fallback. If it passes, drop it and say so in the handoff.

**Change** (Q7 (a); for (b), keep only the warning and never fetch; for (c), `sb_die` instead):
```bash
# A shallow clone (--depth implies --single-branch) may lack origin/main or the commit where the
# branch left it. Fetch main's full history once; SB_NO_FETCH=1 skips the fetch.
sb_unshallow_for_base() {
  [ "$(git rev-parse --is-shallow-repository 2>/dev/null)" = true ] || return 1
  if [ "${SB_NO_FETCH:-0}" = 1 ]; then
    echo "warning: shallow clone without the merge base with main: run git fetch --unshallow origin main" >&2
    return 1
  fi
  echo "note: shallow clone without the merge base with main: git fetch --unshallow origin main" >&2
  git fetch --quiet --unshallow origin "+refs/heads/main:refs/remotes/origin/main" && return 0
  echo "warning: git fetch --unshallow origin main failed (offline?): run it, then make check again" >&2
  return 1
}
```
- In `sb_merge_base`, keep the `CHECK_BASE` branch (`:55-62`) and wrap the `origin/main main` loop (`:63-70`) in `for attempt in 1 2; do ... ; [ "$attempt" = 1 ] && sb_unshallow_for_base || return 0; done`.
- Update the header at `check-changed.sh:14-15`: a shallow clone first fetches main.
- (Q2 (11)) `review-session/SKILL.md:17`: "Then run `git fetch origin` (`git fetch --unshallow origin main` instead when `git rev-parse --is-shallow-repository` prints true) and read the diff with `git diff origin/main...HEAD`."
- W2's stop gate uses `sb_merge_base`, so it gains this too.

### W7. CI: keep the Supabase ports out of the ephemeral range, and retry a port collision once (MS-3; SWEEP A1)

**Why**
- **The failure.** Job 113820378262 (run 37930642448, 9 Oct), log line 611: `failed to bind host port for 0.0.0.0:54322:172.19.0.2:5432/tcp: address already in use`. It came 0.02 s after the CLI's last image pull.
  - Job 112748352761 (7 Oct) failed the same way; its re-run passed with no change.
  - No container held the port (artifact 11616395103, `containers.txt`).
- **The likely cause.**
  - The ports in `supabase/config.toml` (`:10` 54321, `:34` 54322, `:36` 54320, `:48` 54329, `:98` 54323, `:109` 54324, `:391` 54327) lie inside Linux's default ephemeral range, 32768 to 60999.
  - The runner's own range and the socket that held the port were not verified.
  - `docs/reviews/D2.md:188` assigns this to "the F1 follow-up lane".
- **The code today.**
  - `scripts/stack-up.sh:65-74` runs `supabase start` once, with no retry.
  - The failure step at `ci.yml:81-86` saves only `docker ps -a`.

**Test first:**
- `ci-workflow.test.ts`: `reserves every Supabase host port in the check job before any other step opens a connection`.
  - The step whose run matches /sudo sysctl -w net\.ipv4\.ip_local_reserved_ports=54320-54329/ is at index 0 of `jobs.check.steps`, before `make up`.
  - Parse `supabase/config.toml` with /^\s*(?:port|shadow_port)\s*=\s*(\d+)/gm and check that every port >= 32768 lies within 54320 to 54329.
- New `tools/repo-checks/test/unit/supabase-start.test.ts`, in the style of `mirror-images.test.ts`.
  - TempRepo with a fake `node_modules/.bin/supabase` that:
    - logs `$*` to `$SHIM_DIR/calls.log`
    - fails `status`
    - fails the first `FAIL_STARTS` starts with that exact bind error on stderr
  - Run it with `SUPABASE_RETRY_WAIT_SECONDS=0`. Cases:
    - `retries supabase start once, after supabase stop, when a host port is already in use`: calls are `status`, `start --exclude …`, `stop` (`stop --no-backup` with Q8 (B)), `start --exclude …`, and the exit code is 0
    - `fails naming the port when the second start meets it too` (FAIL_STARTS=2): non-zero exit, the output contains `5432[0-9]`, exactly 2 starts
    - `does not retry a start that fails for another reason`
    - `leaves a running Supabase alone`

**Change**
1. In `.github/workflows/ci.yml`, job `check`, insert this as the first step, before `:35` (the checkout):
```yaml
      - name: Keep the Supabase ports out of the ephemeral range
        # supabase/config.toml publishes 54320-54329 (API 54321, database 54322), inside Linux's
        # ephemeral range (32768-60999): an outbound connection (an image pull, pnpm install) can
        # hold one when make up binds it ("address already in use"). First, so no step's sockets do.
        run: sudo sysctl -w net.ipv4.ip_local_reserved_ports=54320-54329
```
2. In the "Stack logs" step (`ci.yml:81-86`), after the `docker ps -a` line, add `sudo ss -tanp > .build-state/sockets.txt 2>&1 || true`.
3. Create the new script `scripts/supabase-start.sh`. Make it executable (`chmod +x`, then check `git ls-files -s scripts/supabase-start.sh` shows 100755).
```bash
#!/usr/bin/env bash
# Starts the local Supabase unless it runs (db, kong, auth and rest; SUPABASE_FULL=1: every service).
# A start that fails because a host port is in use is retried once, after supabase stop and
# SUPABASE_RETRY_WAIT_SECONDS (default 60, a TCP TIME_WAIT): an outbound connection can hold any
# port in 32768-60999, and supabase/config.toml uses 54320-54329 (CI reserves them, ci.yml).
set -euo pipefail
# shellcheck source=lib/common.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
ROOT="$(sb_repo_root)"; cd "$ROOT"
CLI="$ROOT/node_modules/.bin/supabase"
[ -x "$CLI" ] || sb_die "the Supabase CLI is not installed; run make bootstrap"
if "$CLI" status >/dev/null 2>&1; then echo "make up: Supabase is already running"; exit 0; fi
START=(start)
[ "${SUPABASE_FULL:-0}" = 1 ] || START+=(--exclude "realtime,storage-api,imgproxy,mailpit,postgres-meta,studio,edge-runtime,logflare,vector,supavisor")
LOG="$(mktemp)"; trap 'rm -f "$LOG"' EXIT
start() { "$CLI" "${START[@]}" 2>&1 | tee "$LOG"; }
start && exit 0
grep -q 'address already in use' "$LOG" || sb_die "supabase start failed (output above)"
wait="${SUPABASE_RETRY_WAIT_SECONDS:-60}"
echo "make up: a Supabase port is in use (often a short-lived outbound connection); supabase stop, then one more start in ${wait} s" >&2
"$CLI" stop || true
sleep "$wait"
start || sb_die "supabase start failed twice: a port of supabase/config.toml is in use (ss -tanp | grep ':5432[0-9]')"
```
   With Q8 (B), use `stop --no-backup`. If Q8 says to retry on any failure, drop the `grep` line.
4. In `stack-up.sh`, replace `:65-74` with `"$SB_SCRIPTS_DIR/supabase-start.sh"`. Keep the CLI check at `:19-20`.
5. Optional: under the port table in `stack/README.md` (`:37-38`), add one line saying CI reserves 54320 to 54329.

### W8. Image pulls: say why they fail, and wait only where waiting helps (MS-2, CI-HEALTH part 1)

**Why**
- **The wait exists for the mirror.** `scripts/stack-up.sh:8` and `:29` default `IMAGE_PULL_WAIT_SECONDS` to 0. `:26-27` explain the wait as the mirror lag. CI sets 600 (`ci.yml:67`).
- **The messages do not say why.**
  - The retry message (`:32`) says "is not available yet", which is wrong for a 429, and gives neither the registry's answer nor the time left.
  - The non-mirror failure message (`:47`) says only "could not pull".
- **Waiting fixed nothing on 24 Oct.** Main's CI (job 120999039497, 6c0f953, log lines 405-466) spent 600 s on `toomanyrequests: Data limit exceeded` from `public.ecr.aws/docker/library/clickhouse:26.3.38.2`, then failed. PR #11's run did the same on 21 Oct (job 119466242922).
- **A short throttle does pass.** In job 113820378262 (lines 404-437) ECR answered the Supabase CLI's own pulls with `toomanyrequests: Rate exceeded`, and the CLI's retries 4 to 8 s later succeeded. So failing at once on every refusal outside the mirror would make CI more brittle, above all if W9 does not land.
- "Sessions use IMAGE_PULL_WAIT_SECONDS=300" is not backed by any file at origin/main.

**Test first:** new `tools/repo-checks/test/unit/stack-up.test.ts`.
- Build a TempRepo with:
  - a `stack/versions.env` holding the three images under the names `stack-up.sh` reads under `set -u` (`:9`, `:37`): `REDPANDA_*` under `ghcr.io/abdullah95k/securebrand-v2/`, `CLICKHOUSE_*` under `public.ecr.aws/`, and `SEAWEEDFS_*` (each with `_TAG`, `_REPO` and `_UPSTREAM`)
  - a fake `node_modules/.bin/supabase`
  - a fake `docker` on PATH that exits 0 on `info`, fails `image inspect`, logs every `pull` image to `pulls.log`, and fails a `pull` whose image matches `FAIL_MATCH` (a shell case pattern, default `*`) while its count of failed pulls is below `FAIL_PULLS`, printing `PULL_ANSWER` on stderr (default `Error response from daemon: toomanyrequests: Data limit exceeded`). It exits 3 on `compose`, so the script never reaches a real stack.
- Run with `IMAGE_PULL_RETRY_SECONDS=0`. Cases:
  - `retries a failed mirror pull by default and names the registry's answer`: `IMAGE_PULL_WAIT_SECONDS` unset, `FAIL_MATCH='ghcr.io/*'`, `FAIL_PULLS=1`. Expect 2 pulls of the mirror image, and output containing `toomanyrequests: Data limit exceeded` and `IMAGE_PULL_WAIT_SECONDS=300`. It fails today.
  - (Q9 (a)) `fails at once when another registry answers with a data limit, naming its answer and IMAGE_REGISTRY=upstream`: `IMAGE_PULL_WAIT_SECONDS=600`, `FAIL_MATCH='public.ecr.aws/*'`, `FAIL_PULLS=99`. Expect exactly 1 pull of the public.ecr.aws image, a non-zero exit, and output matching /the registry answered: .*Data limit exceeded/ and containing `IMAGE_REGISTRY=upstream`. It fails today.
  - (Q9 (a)) `retries another registry's "Rate exceeded" up to 3 times`: `FAIL_MATCH='public.ecr.aws/*'`, `PULL_ANSWER='Error response from daemon: toomanyrequests: Rate exceeded'`. With `FAIL_PULLS=2`: 3 pulls of that image and no "could not pull". With `FAIL_PULLS=99`: 4 pulls and a non-zero exit naming "Rate exceeded".
  - `gives up after IMAGE_PULL_WAIT_SECONDS naming the wait, the answer and IMAGE_REGISTRY=upstream`: `IMAGE_PULL_WAIT_SECONDS=0`, `FAIL_MATCH='ghcr.io/*'`, `FAIL_PULLS=99`.
  - For Q9 (b) or (c), assert the mirror behaviour for every image instead of the two Q9 (a) cases.

**Change** in `scripts/stack-up.sh`:
- `:8`: `#   IMAGE_PULL_WAIT_SECONDS  keep retrying a failed pull of this repository's GHCR mirror this long (default 300; 0 tries once)`. Adjust the wording for Q9 (b) or (c).
- `:26-35`, replace with:
```bash
# A failed pull of this repository's GHCR mirror is retried for IMAGE_PULL_WAIT_SECONDS (default 300;
# CI sets 600): the minute or two the mirror workflow needs to copy a new tag. Another registry's
# short throttle ("Rate exceeded", a 5xx) is retried up to 3 times; a data limit or any other refusal
# does not pass within minutes, so it fails at once with the registry's answer.
# IMAGE_PULL_RETRY_SECONDS spaces the attempts (20).
PULL_WAIT="${IMAGE_PULL_WAIT_SECONDS:-300}"
PULL_ERROR=""
pull() {
  local deadline=$((SECONDS + PULL_WAIT)) tries=0 more
  until PULL_ERROR="$(docker pull --quiet "$1" 2>&1 >/dev/null)"; do
    PULL_ERROR="$(printf '%s\n' "$PULL_ERROR" | tail -1)"
    tries=$((tries + 1))
    case "$1" in
      ghcr.io/abdullah95k/*) # Q9 (b)/(c): this branch for every image
        [ "$SECONDS" -lt "$deadline" ] || return 1
        more=", for up to $((deadline - SECONDS)) s more (IMAGE_PULL_WAIT_SECONDS=$PULL_WAIT)"
        ;;
      *)
        case "$PULL_ERROR" in
          *"Rate exceeded"* | *"unexpected HTTP status: 5"*) [ "$tries" -le 3 ] || return 1 ;;
          *) return 1 ;;
        esac
        more=" (attempt $((tries + 1)) of 4)"
        ;;
    esac
    echo "make up: pulling $1 failed (${PULL_ERROR:-no answer}); retrying in ${IMAGE_PULL_RETRY_SECONDS:-20} s$more" >&2
    sleep "${IMAGE_PULL_RETRY_SECONDS:-20}"
  done
}
```
  The "Rate exceeded" wording is from job 113820378262 line 405; the 5xx wording ("unexpected HTTP status: 5…") is Docker's registry client's and was not seen in this repository's logs (not verified).
- `:40-48`: start the failure handling with `echo "make up: could not pull $image; the registry answered: ${PULL_ERROR:-nothing} (IMAGE_PULL_WAIT_SECONDS=$PULL_WAIT s applies to this repository's mirror)" >&2`. Keep the GHCR advice (`:42-45`). The `*)` branch becomes `echo "  A data limit (toomanyrequests: Data limit exceeded) can last hours: run make up again later. IMAGE_REGISTRY=upstream make up pulls from the publishers instead (Docker Hub may answer 429 to anonymous pulls)." >&2`. The comment and this message then agree: neither promises that waiting inside `make up` helps.
- Leave `ci.yml:67` at 600.

### W9. Mirror ClickHouse into GHCR (CI-HEALTH part 2; only if Q10 is (a))

**Why**
- Main has been red since the D2 merge, because ECR Public refuses anonymous pulls of ClickHouse: run 40136503053, job 120999039497, lines 405-467.
- The image comes from `stack/versions.env:14-17` (`CLICKHOUSE_REPO=public.ecr.aws/docker/library/clickhouse`). Its `CLICKHOUSE_UPSTREAM=docker.io/clickhouse/clickhouse-server` is a different repository from the Docker Official Image in use.
- `scripts/mirror-images.sh:34-60` copies every pin whose `_REPO` is under this repository's GHCR prefix from its `_UPSTREAM`.
- `tools/repo-checks/test/unit/pins.test.ts:9-10` and `:34-42` accept ghcr.io and require a mirrored upstream outside the mirror. CI already logs in to GHCR (`ci.yml:57-62`).

**Verify first** (never read Docker Hub from the container: it answers 429 to anonymous pulls on the shared address, `docs/plans/F1.md:11`, `docs/orchestration/README.md:41`):
- With dockerd up, read ECR's digest: `docker buildx imagetools inspect public.ecr.aws/docker/library/clickhouse:26.3.38.2 --format '{{.Manifest.Digest}}'`. Write it down for step 4. If it cannot be read, skip W9, push the rest, and report under NEEDS-INPUT with the answer.
- The upstream's digest is read on GitHub's runner by the Mirror images run after the W9 push (step 4).

**Test first:** `pins.test.ts`: `pulls ClickHouse from this repository's GHCR mirror, copied from the Docker Official Image`, expecting `CLICKHOUSE_REPO` to be `ghcr.io/abdullah95k/securebrand-v2/clickhouse` and `CLICKHOUSE_UPSTREAM` to be `docker.io/library/clickhouse`. It fails today.

**Change**
1. `stack/versions.env:14-17`:
   - comment: "ClickHouse's Docker Official Image, mirrored: ECR Public refuses anonymous pulls from shared addresses (toomanyrequests: Data limit exceeded)"
   - `CLICKHOUSE_REPO=ghcr.io/abdullah95k/securebrand-v2/clickhouse`
   - `CLICKHOUSE_UPSTREAM=docker.io/library/clickhouse`
   - keep `CLICKHOUSE_TAG`
2. Append two rows at the end of the table in `docs/dependencies.md`, in the format of the Redpanda rows (`:11-12`): `ghcr.io/abdullah95k/securebrand-v2/clickhouse` (this repository's GHCR mirror of ClickHouse) and `docker.io/library/clickhouse` (upstream of the mirror; `IMAGE_REGISTRY=upstream`). Each is Apache-2.0, ClickHouse, Inc., US, "flagged vendor; open-source server, self-hosted, allowed by CONVENTIONS", added in F1b. Do not edit the existing rows.
3. Texts that say only images without an anonymous upstream are mirrored:
   - `stack/README.md:60-64`: move ClickHouse from the anonymous upstreams to the mirrored images.
   - `stack/versions.env:3-5` (header): the mirror also serves an image whose anonymous upstream refuses shared addresses (ClickHouse).
   - `README.md:86-87` ("copies to GHCR the stack images that have no anonymous upstream"), `.github/workflows/mirror-images.yml:1-2` and `scripts/mirror-images.sh:2-4`: say it copies every stack image whose `_REPO` points to this repository's GHCR (Redpanda, which has no anonymous upstream, and ClickHouse, whose ECR copy refuses CI's pulls). `docs/handoffs/F1.md:79` is W13's.
4. **Push order matters.**
   - Commit W9 and push it alone to `sb/F1b` before you commit W11. At that point the trigger in `mirror-images.yml:10-14` still runs on any branch, so this push mirrors the tag.
   - Then read the run: `gh api 'repos/Abdullah95k/securebrand-v2/actions/workflows/mirror-images.yml/runs?branch=sb/F1b' --jq '.workflow_runs[0] | {id,head_sha,status,conclusion}'`, its job with `gh api repos/Abdullah95k/securebrand-v2/actions/runs/<run_id>/jobs --jq '.jobs[] | [.id,.conclusion] | @tsv'`, and the job log with `gh api repos/Abdullah95k/securebrand-v2/actions/jobs/<job_id>/logs | grep 'mirror: '`.
   - Compare the digest the log prints for `docker.io/library/clickhouse:26.3.38.2` (`scripts/mirror-images.sh:58`, or `:54` when the tag was already there) with ECR's from "Verify first".
   - If the digests differ, or the run fails (for example docker.io answers 429), `git revert` the W9 commit (no force push), push, carry on with the rest, and report under NEEDS-INPUT with both digests or the run's answer. The orchestrator re-runs the mirror, or the user adds the Docker Hub secrets.
5. **The new package starts private** (`mirror-images.yml:5`). Every cloud session's `make up` fails on it until the user makes `securebrand-v2/clickhouse` public, because `stack-up.sh:37-50` inspects, pulls, then exits, and cloud sessions have no GitHub credentials (`docs/handoffs/F1.md:132`).
   - Run your local stack tests (W7, W8, and `make check ACCEPTANCE=1`) before this commit.
   - After the digests match, keep the local stack working with `docker tag public.ecr.aws/docker/library/clickhouse:26.3.38.2 ghcr.io/abdullah95k/securebrand-v2/clickhouse:26.3.38.2` (the ECR image must be local already, from an earlier `make up`). `stack-up.sh:38` then finds the image and does not pull. This local tag proves nothing about the package; CI does, once the package is public.
   - List "make the package public before merge" as a user action in the handoff.

### W10. CI checks formatting (D1PR-4)

**Why**
- `package.json:13` defines `fmt:check`, but no workflow runs it (`ci.yml:51-68`, `:98-128`).
- The only format gate is acceptance test A23 (`tools/repo-checks/test/acceptance/format.test.ts:17-24`). It runs only when root tooling changes (`check-changed.sh:59`, `:77-78`), so a docs-only or service-only pull request is never format-checked.
- D1's pull request failed A23 in its test merge with main until 5d2455c, a D1 lane commit made before D1 merged as 73179c3.
- Main's tree 2ebfdd91 passed A23 as PR #6's test merge (run 40112373694, job log line 867). That tree equals 6c0f953's.
- Dependabot PR #11 bumps Prettier from 3.9.9 to 3.9.10 (its body). Once this step lands, #11's `check` fails if the patch reformats any file; the fix then is `make fmt` on #11's branch.

**Test first:** `ci-workflow.test.ts`: `the check job runs pnpm fmt:check before it starts the stack`. Find the index of the step whose trimmed run is `pnpm fmt:check`, expect it to be greater than -1 and less than the index of `make up`.

**Change:**
- First, `nvm use 24.21.0 >/dev/null && pnpm fmt:check; echo exit=$?` on your branch must print `exit=0`. If it lists files, run `make fmt` in a separate earlier commit.
- Then insert after the Install step (`ci.yml:51-56`), before "Log in to GHCR":
```yaml
      - name: Prettier (pnpm fmt:check)
        run: pnpm fmt:check
```

### W11. Mirror workflow: pushes to main only (CC-3; Q11)

**Why**
- `.github/workflows/mirror-images.yml:8-14` has no `branches:` filter and grants `packages: write` (`:16-18`).
- The approved plan says main (`docs/plans/F1.md:119`).
- sb/D1 ran it only because it merged main (run 37595455426).
- `tools/repo-checks/test/unit/ci-workflow.test.ts:171-175` pins the any-branch behaviour.

**Test first:** rename the test at `ci-workflow.test.ts:171` to "the mirror workflow runs on demand and on pushes to main that change stack/versions.env". Replace `expect(push.branches).toBeUndefined();` with `expect(push.branches).toEqual(["main"]);`. It fails today.

**Change** (Q11 (a); for (b), keep any-branch and add a first step that exits when `git diff --quiet origin/main -- stack/versions.env scripts/mirror-images.sh .github/workflows/mirror-images.yml`):
- `mirror-images.yml:10-14`: `push:` / `branches: [main]` / the same `paths:`.
- Rewrite the comment at `:2-5`: "It runs on every push to main that changes the pins, and on demand (Actions, Mirror images, Run workflow), on any branch, for a lane that changes a mirrored pin and must prove make up before it merges. A run off main never replaces a tag already mirrored."
- Keep `:56` (`MIRROR_REPLACE`) and `workflow_dispatch`.
- Text:
  - `stack/README.md:64`: "on every push to main that changes `versions.env`".
  - `stack/README.md:69-70`: a lane that changes a mirrored pin has the workflow run on its branch (Run workflow) before its CI.
  - `scripts/stack-up.sh` needs nothing here: W8's comment already speaks of the time the mirror workflow needs to copy a new tag.
- Commit this only after W9's push.

### W12. Dependabot (MS-4; Q12)

**Why**
- **docker:**
  - The node check always hits ECR's 429: runs 37580589859, 37681691456 and 38635780053 log `429 https://public.ecr.aws:443/v2/docker/library/node/tags/list`.
  - PR #10 (python 3.13.16 to 3.15.0, uv image 0.12.23 to 0.13.1) failed `pins.test.ts` "pins the base images of the service templates to the toolchain versions" (job 116123773390, line 562). By design, `pins.test.ts:46-52` ties the template images to `.node-version`, `.python-version` and `uv.toml`.
- **uv:**
  - The semver-major ignore (`.github/dependabot.yml:31-33`) lets PR #8 widen uv_build to `>=0.13.0,<0.14`, against `uv.toml:5` `required-version = ">=0.12.23,<0.13"`.
  - The uv update jobs fail with `tool_version_not_supported` (Dependabot's bundled uv is 0.12.18; runs 38635780142 and 39669969058). That cannot be fixed in the repository.
- **npm:** the 7 Oct `turbo unknown_error` was transient (see dropped items).
- **The comment is wrong.** The text "minor and patch updates only" (`dependabot.yml:1-3`, `README.md:86-88`) is untrue for 0.x and Python minors.

**Test first:** in `ci-workflow.test.ts:190` and `:200`, expect the ecosystems `["github-actions", "npm", "uv"]`, and assert that the uv update has an ignore entry `{ "dependency-name": "uv-build", "update-types": ["version-update:semver-minor"] }`. It fails today.

**Change**
1. (Q12 (a)) Delete the docker block (`dependabot.yml:35-46`). Change the header comment (`:1-4`) to say that the stack's tags in `stack/versions.env` and the service templates' base images (which follow `.node-version`, `.python-version` and `uv.toml`) are bumped by hand, and that a minor bump of a 0.x tool or of Python counts as planned too.
2. After `:33`, add:
```yaml
      - dependency-name: "uv-build"
        update-types: ["version-update:semver-minor"]
```
3. (Q12 turbo (b) only) Add a `turbo` semver-minor ignore to the npm block.
4. `README.md:86-88`: match the comment.
5. In your handoff, record that Dependabot cannot update the Python lockfiles until its bundled uv is at least 0.12.23.

### W13. Records: F1's handoff and plan, and the label (HANDOFF, LABEL, SWEEP A2 and A3)

**Why**
- `docs/handoffs/F1.md` has gone stale:
  - `:3` says "recheck pending", although the recheck happened (`docs/reviews/F1.md:155`, verdict at `:227-228`) and PR #1 merged on 7 Oct as a747275.
  - `:24` says 177 and 13 tests, against `:186` and `docs/reviews/F1.md:171` (192 unit, 14 acceptance).
  - `:51` (A24) points to a CI table (`:64-70`) that ends before the final head cc05035. That head passed policy (runs 37579924974 and 37580572282) and check and template-smoke (run 37579925053).
  - `:132` says the Redpanda package is private. It is public: an anonymous token and a HEAD on `v26.1.18` returned 200 on 24 Oct, and `docs/reviews/F1.md:16` agrees.
  - `:133` names only Docker Hub as rate-limited; ECR Public has since refused CI's pulls (W8).
  - `:141` user actions (1) and (3) are done (ruleset 24640268 requires `check`, `template-smoke` and `policy`). Action (2) was never set: the Docker Hub login in Mirror images run 37580584074 was skipped.
  - `:148` names A7, but `scripts/make-test.sh:52` runs only pytest.
  - `:54` omits the Supabase check (`docs/reviews/F1.md:223`).
  - `:19` and `:103` describe `IMAGE_PULL_WAIT_SECONDS` with the old default (W8 changes it); `:79` says Redpanda is the only mirrored image (W9 changes it); `:143`'s upgrade follow-ups lack uv 0.13 and Python 3.15 (Dependabot #8 and #10).
  - `:120` (F8) lacks the ADR-0029 pointer (`docs/decisions/ADR-0029-clickhouse-topology-and-environments.md:23`).
  - The Review section (`:150-186`) stops before the recheck and its note 9.
- `docs/plans/F1.md:3` says "Approved by: pending (orchestrator)", and every Answer cell at `:194-205` reads "pending". The header format is `docs/orchestration/README.md:11`, and `docs/decisions/ADR-0030` ratifies what F1 built. Who answered each question is not recorded in the repository: `:190` says questions 1 to 5, 8 and 9 needed an answer, and the rule in force then sent such questions to the user (`git show 88cb22a:docs/orchestration/README.md`, L9).
- **The `contract-change` label.** `scripts/policy/check-contract-paths.sh:35-55` requires it, and the ruleset makes `policy` a required check. It was missing until the orchestrator created it on 24 Oct 2026 (Q14). Verify it with `gh api repos/Abdullah95k/securebrand-v2/labels/contract-change`; nothing in this lane creates it.

**Change** (docs, plus one optional characterisation test). With Q15 (a), edit F1's records in place as below. With Q15 (b), leave both files as merged and write the same corrections, item by item, in a section "Corrections to F1's records" of `docs/handoffs/F1b.md`.
- `docs/handoffs/F1.md`. Add one dated line under the header: "Corrected 2026-10-<dd> by F1b, after D1 and D2: header, test counts, CI, A24, A27, Operations, Open items, Review". Then:
  1. `:3`: "recheck 2026-10-07 (`docs/reviews/F1.md` L155; verdict ready to merge, L227-L228); merged 2026-10-07 as a747275, the squash of PR head cc05035".
  2. `:24`: "(192 passed, 16 files)" and "(repo-checks 14 passed, 4 files, local stack in this container)".
  3. Add CI rows after `:70`:
     - bf3f6cc (CI runs 37573675741 and 37573675781): passed, passed, policy failed only at the handoff and review step
     - cc05035, the recheck (CI run 37579925053; policy runs 37579924974 and 37580572282): all passed

     Below the table: "On main after the merge (a747275): CI run 37580584189 passed; Mirror images run 37580584074 passed (the Docker Hub login was skipped: no secrets)."
  4. `:51`: "pass locally and in CI: the policy job passed on the final head cc05035 (runs 37579924974, 37580572282)".
  5. `:54`: append the Supabase CLI update check (`docs/reviews/F1.md` L196, L223), and that F1b W5 turns both checks off. If W5 is not done, say so instead.
  6. `:132`: the Redpanda package is public. A package the mirror workflow creates for a new image (ClickHouse, W9) starts private until the user makes it public; meanwhile use `IMAGE_REGISTRY=upstream make up`.
  7. Operations (`:133` and new lines):
     - Extend `:133`: ECR Public, too, answered CI's anonymous pulls with "`toomanyrequests: Data limit exceeded`" (ClickHouse; jobs 119466242922 and 120999039497) and "`Rate exceeded`" (the Supabase CLI's pulls, which its retries got past; job 113820378262), with the fix W8 and W9 made.
     - Add "`failed to bind host port for 0.0.0.0:54322 ... address already in use`" (job 113820378262), with W7's fix and "likely cause, not proven".
  8. `:141`: (1) done (7 Oct); (2) optional and not set, since ECR Public, not Docker Hub, is the limit CI has met; (3) done (ruleset `main`, 7 Oct); (4) the label `contract-change`, named exactly that (`check-contract-paths.sh` matches it exactly, `tools/repo-checks/test/unit/policy-contract-paths.test.ts:47`): created by the orchestrator on 24 Oct 2026.
  9. Delete `:142` once the plan below is updated.
  10. `:148`: replace "(A7, A10)" with "A10, through make check; A7's make test runs only pytest (scripts/make-test.sh L52)". Drop the item if W5 is done.
  11. After `:186`: "Recheck (`docs/reviews/F1.md` L155 to L228, 7 Oct): ready to merge; findings 1 to 4 fixed; notes 5 to 8 open; new note 9 fixed by F1b W4."
  12. `:120`: append "ADR-0029 adds an embedded Keeper and the {shard} and {replica} macros to these configs (local and CI); stack-config.test.ts checks the configs and their labels."
  13. Optional: `:100`, "D1 (5d2455c) also skips docs/contracts/*.md".
  14. `:19` and `:103` (if W8 is done): `IMAGE_PULL_WAIT_SECONDS` retries this repository's mirror (default 300, CI 600); other registries get up to 3 retries of a short throttle and fail at once otherwise (F1b W8).
  15. `:79` (if W9 lands): ClickHouse now comes from this repository's GHCR mirror of `docker.io/library/clickhouse` (F1b W9); Redpanda is no longer the only mirrored image.
  16. `:143`: append "uv 0.13 and Python 3.15 (Dependabot #8 and #10, closed after F1b W12)".
- `docs/plans/F1.md`:
  - `:3`: "Approved by: the orchestrator, under the user's delegation (docs/orchestration/README.md), <Q13 date>". If Q13 is pending, leave `:3` unchanged and report it.
  - `:194-205`: Answer "approved: the recommended option, as built (docs/reviews/F1.md L119-L136)"; Decided by: for each row, exactly what Q13 supplies (who and when), or "not recorded in the repository" where Q13 has nothing for that row, never a guessed name; ADR "ADR-0030". Change nothing else.
- Optional test (LANE-NAME): in `tools/repo-checks/test/unit/policy-handoff-review.test.ts`, add `a follow-up lane is judged by its own review, not its parent's`: a TempRepo with `docs/handoffs/F1.md`, a `docs/reviews/F1.md` whose verdict reads "ready to merge", and a change under `tools/`; with `POLICY_BRANCH=sb/F1b` the check exits non-zero naming `docs/handoffs/F1b.md` and `docs/reviews/F1b.md` (`check-handoff-review.sh:31-32`, `:75-79`). It is expected to pass at origin/main.
- Check the label with `gh api repos/Abdullah95k/securebrand-v2/labels/contract-change --jq .name`. Record the result: `contract-change`, or HTTP 404 if nobody has created it yet.

## Checks (run all; show the output)

- `make check`. Changes under `.claude/`, `scripts/`, `.github/`, `stack/` and `CLAUDE.md` add repo-checks (`scripts/check-changed.sh:59`, `:77-78`).
- `make test SERVICE=repo-checks` (pre-approved). It also runs the acceptance suites, which need the stack: start dockerd and `make up`, before W9, or after it with the local `docker tag` from W9 step 5.
- `TEST_STACK_RESET=1 make check ACCEPTANCE=1` with the stack up. It runs `make down` and `make up` (`tools/repo-checks/test/acceptance/stack.test.ts:238`, `:243`), which exercises W7's `supabase-start.sh`. If you cannot run the stack, say so; CI's `check` then covers it.
- `bash -n` on every changed shell script and hook.
- `nvm use 24.21.0 >/dev/null && pnpm exec prettier --check <changed Markdown and YAML>`: `docs/handoffs/F1.md`, `docs/handoffs/F1b.md`, `README.md`, `stack/README.md`, `docs/issues/README.md`, `.github/workflows/*.yml` and `.github/dependabot.yml`. `.claude/`, `CLAUDE.md`, `KIT-README.md` and `build-plan/` (`.prettierignore:2-7`), `docs/dependencies.md` (`:10`) and `docs/plans/*.md` (`:12`) are Prettier-ignored. Then `pnpm fmt:check` on the whole tree (W10).
- `POLICY_BRANCH=sb/F1b make policy BASE=origin/main`.
  - Before the review exists, check-handoff-review must fail only with "docs/reviews/F1b.md is missing" (`check-handoff-review.sh:78-79`).
  - check-contract-paths passes (no contract path changed).
  - check-dependencies passes (W9's rows).
- If `build-plan/` changed: `python3 build-plan/tools/validate.py` prints `errors []`, and `git diff --stat build-plan/sessions` lists only the briefs you meant to change.
- After each push, read CI over REST:
  - `gh api repos/Abdullah95k/securebrand-v2/commits/<sha>/check-runs --jq '.check_runs[] | [.name,.status,.conclusion,.details_url] | @tsv'`
  - for a failed job, `gh api repos/Abdullah95k/securebrand-v2/actions/jobs/<job_id>/logs`

  CI runs on the pull request, which the orchestrator opens. Until then only the Mirror images run (W9) appears. Report each run's ID and conclusion; never call a run green that you did not read.

## Not in scope

- `packages/contracts`, `supabase/migrations`, `clickhouse/migrations`.
- The comment at `services/_template/src/adapter.ts` L3-5: F4's, per `build-plan/tools/sessions.py:100` and `build-plan/sessions/F4-sdk-runtime.md:38`.
- An embedded Keeper and the `{shard}`/`{replica}` macros in `compose.yaml`, with `stack-config.test.ts`: F8's, per ADR-0029:23 and :31.
- The mapper-location kit lines: C4's with F4, per `docs/decisions/DEFERRED.md:60`.
- `scripts/policy/check-handoff-review.sh`. The policy job runs main's copy (`policy.yml:38-48`), so a change cannot gate this lane. Record as open items:
  - a `sb/CC-*` branch skips the code gate (`:45-64` exit before `:69`; inferred from the code)
  - the guard reads the branch from the tool call's cwd, not from the edited file's repository (`guard-contracts.sh:16`)
- Moving the Supabase ports below 32768 (the Q8 alternative), and a Supabase CLI registry override (not verified).
- `.claude/settings.json` (leave `:24-25` as they are) and `docs/orchestration/README.md` (the orchestrator owns it: `:29-31` q-files, `:43` label).
- Listed in your handoff's Open items, not fixed here:
  - review notes 5 to 8 (`docs/reviews/F1.md:186-189`)
  - `tools/repo-checks/test/acceptance/make-test.test.ts:32-37` covers 4 of the 6 folders `make-test.sh:17` searches
  - pnpm `minimumReleaseAge` (the 7 Oct npm failure)
  - the SeaweedFS telemetry flag (name not verified)
  - the pnpm v11 layout warning
  - `tools/new-service/index.mjs:210` wording
  - the Supabase images still come from public.ecr.aws through the CLI
  - the guard decides by the local branch name (`guard-contracts.sh:16-19`), so a cloud F2, F3, F8 or `sb/CC-*` session that starts on a harness branch (this orchestrator session runs on `claude/keen-brahmagupta-fipkxf`) or a detached HEAD is blocked until it switches to its lane branch. How create_session names a worker's local branch is not verified.
- **User and orchestrator actions:**
  - the `contract-change` label: done by the orchestrator on 24 Oct 2026
  - make the GHCR package `securebrand-v2/clickhouse` public
  - re-run run 40136503053 on main: the orchestrator re-ran its check job on 24 Oct 2026 (job 121016302873); it failed again on ECR's "Data limit exceeded" for ClickHouse
  - merge #9 (CI green); close #8 and #10 after W12; merge #11 once its `make up` passes, running `make fmt` on its branch first if Prettier 3.9.10 reformats files after W10
  - set up the cloud environment to run `make bootstrap` (`docs/handoffs/F1.md:146` suggested `nvm install` and `uv self update`, which W4 shows fail offline and for a uv installed by pip)
  - start F2, F3, F8 and contract-change sessions on their lane branch, or tell them to switch to it first (see the open item above)

## Finish

1. Write `docs/handoffs/F1b.md` from `build-plan/templates/HANDOFF.md`. It contains:
   - an acceptance table W1 to W13: test name, command, result
   - the decisions applied, from Q1 to Q15, each Answer cell copied exactly with its attribution
   - "Not done", with the reason for each
   - the arm-file observation from setup step 3, and what you ran if bootstrap stopped at the uv step (setup step 2)
   - what was verified and what was not
   - Operations: `make bootstrap` in the cloud, W7 and W8 messages, the W9 package visibility and the local `docker tag` stand-in
   - Open items, from "Not in scope"
   - with Q15 (b), the section "Corrections to F1's records"
2. Run `/code-review` on the diff and fix every correctness finding test-first.
3. Run the Checks again and push to `sb/F1b` (`git push origin HEAD:sb/F1b` if your local branch has another name). Do not open the pull request; the orchestrator opens it from `sb/F1b`, so that `policy.yml:31` passes `sb/F1b`.
4. End your turn with `ORCHESTRATOR: DONE`, followed by:
   - the commits (SHA and subject)
   - each check, with its command and result
   - the pushed SHA
   - the CI and Mirror images run IDs and conclusions you read, and the two ClickHouse digests (W9)
   - the decisions applied and the items skipped
   - the user actions still open (label, package visibility, re-run of main, Dependabot pull requests)

   Then a fresh session runs `/review-session F1b`, which writes `docs/reviews/F1b.md`.
5. If a needed decision is missing, or a "verify first" step fails, push what is done and end with `ORCHESTRATOR: NEEDS-INPUT` and numbered questions (with Q4 (a), file `docs/issues/F1b-q<n>.md` first). If you are blocked, file `docs/issues/F1b-<n>.md` and end with `ORCHESTRATOR: BLOCKED`.
