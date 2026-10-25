import { existsSync, readFileSync } from "node:fs";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { runHook } from "../helpers/hooks.js";
import { TempRepo, type RunResult } from "../helpers/repo.js";

// Stands in for the real checks: counts its runs, prints a line for the log tail and exits with
// STUB_CHECK_EXIT (1 when unset). Not TEST_STUB_...: cleanEnv strips the TEST_ prefix.
const STUB_CHECK = `#!/usr/bin/env bash
mkdir -p .build-state
echo run >> .build-state/stub-runs
echo "stub check"
exit "\${STUB_CHECK_EXIT:-1}"
`;

describe(".claude/hooks/stop-gate.sh and arm-stop-gate.sh", () => {
  let repo: TempRepo;
  let base: string;

  function arm(session = "s1"): RunResult {
    return runHook(
      "arm-stop-gate.sh",
      { session_id: session, cwd: repo.dir, hook_event_name: "UserPromptExpansion" },
      { cwd: repo.dir },
    );
  }

  function stop(session = "s1", checkExit = 1, mode = "default"): RunResult {
    return runHook(
      "stop-gate.sh",
      {
        session_id: session,
        cwd: repo.dir,
        permission_mode: mode,
        hook_event_name: "Stop",
        stop_hook_active: false,
      },
      { cwd: repo.dir, env: { STUB_CHECK_EXIT: String(checkExit) } },
    );
  }

  function stubRuns(): number {
    const file = repo.path(".build-state/stub-runs");
    return existsSync(file) ? readFileSync(file, "utf8").trim().split("\n").length : 0;
  }

  function systemMessage(result: RunResult): string {
    return (JSON.parse(result.stdout) as { systemMessage: string }).systemMessage;
  }

  function changeCode(): void {
    repo.write("services/a/index.ts", `export const changed = ${Date.now()};\n`);
  }

  function expectBlocked(result: RunResult): void {
    expect(result.code, result.output).toBe(2);
    expect(result.stderr).toContain("make check failed (round");
  }

  beforeEach(() => {
    repo = new TempRepo("stop-gate-");
    repo
      .write(".gitignore", ".build-state/\n")
      .write("docs/issues/README.md", "# Issues\n")
      .write("docs/proposals/README.md", "# Proposals\n")
      .write("services/a/index.ts", "export {};\n")
      .write("scripts/check-changed.sh", STUB_CHECK, 0o755);
    base = repo.commit("base");
    repo.branch("sb/X");
  });

  afterEach(() => {
    repo.cleanup();
  });

  it("arming prints the armed notice and records the commit HEAD is on, and the proposals and issues that exist", () => {
    repo.write("docs/issues/X-1.md", "# Issue\n");
    const head = repo.commit("an earlier session's issue");
    repo.write("docs/proposals/X-a.md", "# Proposal\n"); // untracked
    const result = arm();
    expect(result.code, result.output).toBe(0);
    expect(result.stdout).toContain("Stop gate armed for this session");
    expect(repo.read(".build-state/stop-gate-s1").split("\n")[0]).toBe(head);
    expect(repo.read(".build-state/stop-gate-s1.filed-before").trim().split("\n")).toEqual([
      "docs/issues/README.md",
      "docs/issues/X-1.md",
      "docs/proposals/README.md",
      "docs/proposals/X-a.md",
    ]);
  });

  it("lets an unarmed session stop while the checks fail, without running them", () => {
    changeCode();
    const result = stop();
    expect(result.code, result.output).toBe(0);
    expect(stubRuns()).toBe(0);
  });

  it("lets a plan-mode session stop", () => {
    arm();
    changeCode();
    const result = stop("s1", 1, "plan");
    expect(result.code, result.output).toBe(0);
    expect(stubRuns()).toBe(0);
  });

  it("blocks an armed session while the checks for changed code fail, and shows the log tail", () => {
    arm();
    changeCode();
    const result = stop();
    expect(result.code, result.output).toBe(2);
    expect(result.stderr).toContain("make check failed (round 1 of 3)");
    expect(result.stderr).toContain("stub check");
  });

  it("lets an armed session stop when the checks pass, and does not rerun them for an unchanged tree", () => {
    arm();
    changeCode();
    expect(stop("s1", 0).code).toBe(0);
    expect(stop("s1", 0).code).toBe(0);
    expect(stubRuns()).toBe(1);
  });

  it("reruns the checks after the code changes again", () => {
    arm();
    changeCode();
    expect(stop("s1", 0).code).toBe(0);
    repo.write("services/a/other.ts", "export {};\n");
    expect(stop("s1", 0).code).toBe(0);
    expect(stubRuns()).toBe(2);
  });

  it("lets Claude stop after three failed rounds, naming the log", () => {
    arm();
    changeCode();
    for (let round = 1; round <= 3; round++) {
      const result = stop();
      expect(result.code, result.output).toBe(2);
      expect(result.stderr).toContain(`make check failed (round ${round} of 3)`);
    }
    const result = stop();
    expect(result.code, result.output).toBe(0);
    expect(systemMessage(result)).toContain("after 3 rounds");
    expect(systemMessage(result)).toContain(".build-state/last-check.log");
  });

  it("does not run the checks when only docs/ changed", () => {
    arm();
    repo.write("docs/notes.md", "# Notes\n");
    const result = stop();
    expect(result.code, result.output).toBe(0);
    expect(stubRuns()).toBe(0);
  });

  it.each(["untracked", "staged", "committed"])(
    "lets Claude stop with a q-file docs/issues/X-q1.md filed after arming (%s)",
    (state) => {
      arm();
      changeCode();
      repo.write("docs/issues/X-q1.md", "# Question for the user: x\n");
      if (state === "staged") {
        repo.git("add", "docs/issues/X-q1.md");
      } else if (state === "committed") {
        repo.git("add", "docs/issues/X-q1.md");
        repo.git("commit", "-q", "-m", "X: question");
      }
      const result = stop();
      expect(result.code, result.output).toBe(0);
      expect(systemMessage(result)).toContain("docs/issues/X-q1.md");
      expect(stubRuns()).toBe(0);
    },
  );

  it("lets Claude stop with a q-file whose name is not ASCII", () => {
    arm();
    changeCode();
    repo.write("docs/issues/X-q2-سؤال.md", "# Question for the user: y\n");
    const result = stop();
    expect(result.code, result.output).toBe(0);
    expect(systemMessage(result)).toContain("docs/issues/X-q2-سؤال.md");
  });

  it("lets Claude stop with a proposal filed after arming", () => {
    arm();
    changeCode();
    repo.write("docs/proposals/X-topic.md", "# Proposal\n");
    repo.git("add", "docs/proposals/X-topic.md");
    repo.git("commit", "-q", "-m", "X: proposal");
    const result = stop();
    expect(result.code, result.output).toBe(0);
    expect(systemMessage(result)).toContain("docs/proposals/X-topic.md");
  });

  it("ignores an issue an earlier session committed on the lane before arming", () => {
    repo.write("docs/issues/X-1.md", "# Issue\n").commit("the build session's issue");
    arm();
    changeCode();
    expectBlocked(stop());
  });

  it.each(["a true merge", "a fast-forward"])(
    "ignores an issue merged in from main even when origin/main is stale (%s)",
    (shape) => {
      repo.git("update-ref", "refs/remotes/origin/main", base);
      arm();
      if (shape === "a true merge") {
        repo.write("services/a/b.ts", "export {};\n").commit("X: own work");
      }
      repo.checkout("main");
      repo.write("docs/issues/Y-1.md", "# Another lane's issue\n").commit("Y: issue");
      repo.checkout("sb/X");
      if (shape === "a true merge") {
        repo.git("merge", "-q", "--no-ff", "-m", "merge main", "main");
      } else {
        repo.git("merge", "-q", "--ff-only", "main");
      }
      changeCode();
      expectBlocked(stop());
    },
  );

  it("ignores an untracked q-file left in the worktree before arming", () => {
    repo.write("docs/issues/X-q1.md", "# Question for the user: old\n");
    arm();
    changeCode();
    expectBlocked(stop());
  });

  it.each(["edited", "deleted"])(
    "ignores the docs/issues and docs/proposals READMEs when they are %s",
    (how) => {
      arm();
      changeCode();
      for (const readme of ["docs/issues/README.md", "docs/proposals/README.md"]) {
        if (how === "edited") {
          repo.write(readme, "# Changed\n");
        } else {
          repo.remove(readme);
        }
      }
      expectBlocked(stop());
    },
  );

  it("ignores a file that existed at arming and was deleted and re-added", () => {
    repo.write("docs/issues/X-1.md", "# Issue\n").commit("the build session's issue");
    arm();
    repo.git("rm", "-q", "docs/issues/X-1.md");
    repo.git("commit", "-q", "-m", "drop the issue");
    repo.write("docs/issues/X-1.md", "# Issue\n").commit("the issue again");
    changeCode();
    expectBlocked(stop());
  });

  it("re-arming in the same session keeps the first arm point", () => {
    arm();
    const first = repo.git("rev-parse", "HEAD");
    repo.write("docs/issues/X-q1.md", "# Question for the user: x\n"); // filed after arming
    repo.write("services/a/b.ts", "export {};\n").commit("X: work");
    arm();
    expect(repo.read(".build-state/stop-gate-s1").split("\n")[0]).toBe(first);
    expect(repo.read(".build-state/stop-gate-s1.filed-before")).not.toContain("X-q1.md");
  });

  it("gives an arm file in the old empty format no filing exemption", () => {
    repo.write(".build-state/stop-gate-s1", "");
    changeCode();
    repo.write("docs/issues/X-q1.md", "# Question for the user: x\n");
    expectBlocked(stop());
  });

  it("runs the checks when the branch has no merge base with main", () => {
    repo.git("checkout", "-q", "--orphan", "sb/O");
    changeCode();
    repo.commit("an unrelated history");
    expect(repo.git("status", "--porcelain")).toBe("");
    arm();
    expectBlocked(stop());
  });

  it.each(["scripts/new.sh", "tests/e2e/G1/a.test.ts"])(
    "blocks an armed session whose only change is %s while the checks fail",
    (file) => {
      arm();
      repo.write(file, "x\n");
      expectBlocked(stop());
    },
  );
});
