import { mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { runHook } from "../helpers/hooks.js";
import { ROOT, run, TempRepo, type RunResult } from "../helpers/repo.js";

// A file under each frozen path, for the tools that name a file, and the directory that holds it,
// for the Bash commands.
const FILES = [
  "packages/contracts/src/a.ts",
  "supabase/migrations/20261007000000_a.sql",
  "clickhouse/migrations/0001_a.sql",
];
const DIRS = FILES.map((file) => dirname(file));

const BASH_WRITES: ((dir: string) => string)[] = [
  (p) => `echo x > ${p}/a`,
  (p) => `echo x >> ${p}/a`,
  (p) => `echo x | tee ${p}/a`,
  (p) => `echo x | tee -a ${p}/a`,
  (p) => `sed -i s/x/y/ ${p}/a`,
  (p) => `sed --in-place s/x/y/ ${p}/a`,
  (p) => `cp a ${p}/a`,
  (p) => `mv a ${p}/a`,
  (p) => `rm ${p}/a`,
  (p) => `touch ${p}/a`,
  (p) => `truncate -s0 ${p}/a`,
  (p) => `git checkout -- ${p}`,
  (p) => `git restore ${p}`,
  (p) => `git rm ${p}/a`,
  (p) => `cd ${p} && echo x > a`,
];

const BASH_READS: ((dir: string) => string)[] = [
  (p) => `cat ${p}/a`,
  (p) => `ls ${p}`,
  (p) => `git diff -- ${p}`,
  (p) => `grep -r x ${p}`,
  (p) => `git commit -m "touch ${p}"`,
];

const ALL_BASH_WRITES = DIRS.flatMap((dir) => BASH_WRITES.map((write) => write(dir)));
const ALL_BASH_READS = [
  ...DIRS.flatMap((dir) => BASH_READS.map((read) => read(dir))),
  "echo x > services/a/x.ts",
];

describe(".claude/hooks/guard-contracts.sh", () => {
  let repo: TempRepo;

  function guard(
    tool: string,
    input: Record<string, unknown>,
    opts: { cwd?: string; env?: NodeJS.ProcessEnv } = {},
  ): RunResult {
    const cwd = opts.cwd ?? repo.dir;
    return runHook(
      "guard-contracts.sh",
      { tool_name: tool, cwd, tool_input: input },
      opts.env === undefined ? { cwd } : { cwd, env: opts.env },
    );
  }

  function write(file: string, env?: NodeJS.ProcessEnv): RunResult {
    return guard("Write", { file_path: file, content: "x\n" }, env === undefined ? {} : { env });
  }

  function bash(command: string, opts: { cwd?: string; env?: NodeJS.ProcessEnv } = {}): RunResult {
    return guard("Bash", { command }, opts);
  }

  function expectBlocked(result: RunResult, what: string): void {
    expect(result.code, `${what}\n${result.output}`).toBe(2);
    expect(result.stderr, what).toContain("Contracts are frozen");
    expect(result.stderr, what).toContain("docs/proposals/");
  }

  function expectAllowed(result: RunResult, what: string): void {
    expect(result.code, `${what}\n${result.output}`).toBe(0);
  }

  beforeEach(() => {
    repo = new TempRepo("guard-");
    repo.write("README.md", "x\n").commit("base");
    repo.branch("sb/X");
  });

  afterEach(() => {
    repo.cleanup();
  });

  it("finds jq on PATH, without which the hook lets every call through", () => {
    // guard-contracts.sh fails open without jq (CI still enforces); every case below needs it.
    expect(run("bash", ["-c", "command -v jq"], { cwd: ROOT }).code).toBe(0);
  });

  it.each(
    ["Edit", "Write", "MultiEdit"].flatMap((tool) => FILES.map((file) => [tool, file] as const)),
  )("blocks %s to %s on sb/X", (tool, file) => {
    const input: Record<string, Record<string, unknown>> = {
      Edit: { file_path: file, old_string: "a", new_string: "b" },
      Write: { file_path: file, content: "x\n" },
      MultiEdit: { file_path: file, edits: [{ old_string: "a", new_string: "b" }] },
    };
    expectBlocked(guard(tool, input[tool] ?? {}), `${tool} ${file}`);
  });

  it("blocks a NotebookEdit whose notebook_path is under a contract path", () => {
    for (const dir of DIRS) {
      const notebook = `${dir}/n.ipynb`;
      expectBlocked(guard("NotebookEdit", { notebook_path: notebook, new_source: "x" }), notebook);
    }
  });

  it("blocks absolute, relative and backslash paths alike", () => {
    for (const file of FILES) {
      for (const path of [
        join(repo.dir, file),
        `./${file}`,
        `../${file}`,
        file.replaceAll("/", "\\"),
        `C:\\work\\repo\\${file.replaceAll("/", "\\")}`,
      ]) {
        expectBlocked(write(path), path);
      }
    }
  });

  it("allows writes outside the frozen paths, near-miss names included", () => {
    for (const file of [
      "services/a/src/x.ts",
      "packages/contracts-extra/x.ts",
      "supabase/migrations.md",
      "docs/proposals/X-a.md",
    ]) {
      expectAllowed(write(file), `Write ${file}`);
      expectAllowed(
        guard("Edit", { file_path: file, old_string: "a", new_string: "b" }),
        `Edit ${file}`,
      );
    }
  });

  it.each(["sb/F2", "sb/F3", "sb/F8", "sb/CC-foo"])(
    "allows Write and Bash writes to every frozen path on %s",
    (branch) => {
      repo.git("checkout", "-q", "-b", branch);
      for (const file of FILES) {
        expectAllowed(write(file), `Write ${file} on ${branch}`);
      }
      for (const command of ALL_BASH_WRITES) {
        expectAllowed(bash(command), `${command} on ${branch}`);
      }
    },
  );

  it.each(["sb/F1", "sb/F1b", "sb/F2x", "sb/F20", "sb/CCfoo", "main", "sb/CC-", "a detached HEAD"])(
    "still blocks on %s",
    (branch) => {
      if (branch === "a detached HEAD") {
        repo.git("checkout", "-q", "--detach");
      } else if (branch === "main") {
        repo.checkout("main");
      } else {
        repo.git("checkout", "-q", "-b", branch);
      }
      for (const file of FILES) {
        expectBlocked(write(file), `Write ${file} on ${branch}`);
      }
      for (const dir of DIRS) {
        expectBlocked(bash(`echo x > ${dir}/a`), `echo x > ${dir}/a on ${branch}`);
      }
    },
  );

  it("allows every write when ALLOW_CONTRACT_EDITS=1", () => {
    const env = { ALLOW_CONTRACT_EDITS: "1" };
    for (const file of FILES) {
      expectAllowed(write(file, env), `Write ${file}`);
    }
    for (const command of ALL_BASH_WRITES) {
      expectAllowed(bash(command, { env }), command);
    }
  });

  it.each(ALL_BASH_WRITES)("blocks the Bash write `%s`", (command) => {
    expectBlocked(bash(command), command);
  });

  it("blocks a relative write or touch when the cwd is inside a contract path", () => {
    for (const dir of DIRS) {
      const cwd = repo.path(dir);
      mkdirSync(cwd, { recursive: true });
      for (const command of ["echo x > a", "touch a"]) {
        expectBlocked(bash(command, { cwd }), `${command} in ${dir}`);
      }
    }
  });

  it.each(ALL_BASH_READS)("allows the Bash read `%s`", (command) => {
    expectAllowed(bash(command), command);
  });

  it("known gap, CI is the backstop: a quoted target is not matched", () => {
    // guard-contracts.sh:39-40 drops quoted text before matching, so that commit messages and echo
    // strings never block; a quoted write target slips through with them. The hook is a heuristic
    // for Bash: scripts/policy/check-contract-paths.sh fails the pull request in CI.
    for (const dir of DIRS) {
      for (const command of [`cp a "${dir}/a"`, `echo x > "${dir}/a"`]) {
        expectAllowed(bash(command), command);
      }
    }
  });

  it("the kit tells the contract lanes they may edit", () => {
    const expected: [string, string[]][] = [
      [".claude/rules/contracts.md", ["F2, F3 and F8", "sb/F2", "sb/CC-"]],
      [
        ".claude/skills/build-session/SKILL.md",
        ["F2, F3 and F8", "sb/$0", "ALLOW_CONTRACT_EDITS=1"],
      ],
      [".claude/skills/contract-change/SKILL.md", ["sb/CC-", "ALLOW_CONTRACT_EDITS=1"]],
      ["CLAUDE.md", ["F2, F3 and F8", "sb/CC-"]],
    ];
    for (const [file, texts] of expected) {
      const body = readFileSync(join(ROOT, file), "utf8");
      expect(
        texts.filter((text) => !body.includes(text)),
        `${file} lacks these texts`,
      ).toEqual([]);
    }
  });
});
