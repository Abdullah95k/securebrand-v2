import { cpSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { cleanEnv, run, SCRIPTS, script, TempRepo } from "../helpers/repo.js";

describe("scripts/policy/check-contract-paths.sh", () => {
  let repo: TempRepo;

  function check(args: string[], env: NodeJS.ProcessEnv = {}): ReturnType<typeof script> {
    return script("policy/check-contract-paths.sh", ["--base", "main", ...args], {
      cwd: repo.dir,
      env: cleanEnv(env),
    });
  }

  beforeEach(() => {
    repo = new TempRepo("policy-contracts-");
    repo.write("README.md", "x\n").commit("base");
    repo.branch("sb/F4");
  });

  afterEach(() => {
    repo.cleanup();
  });

  it.each([
    "packages/contracts/src/topics/raw-items.ts",
    "supabase/migrations/20261007000000_sources.sql",
    "clickhouse/migrations/0001_items.sql",
  ])("fails on a contract path change without the label: %s", (path) => {
    repo.write(path, "-- change\n").commit();
    const result = check(["--labels", "enhancement"]);
    expect(result.code).not.toBe(0);
    expect(result.output).toContain(path);
    expect(result.output).toContain("contract-change");
  });

  it("passes with the label", () => {
    repo.write("supabase/migrations/20261007000000_sources.sql", "-- change\n").commit();
    expect(check(["--labels", "contract-change"]).code).toBe(0);
  });

  it("reads the labels as the JSON array CI passes", () => {
    repo.write("packages/contracts/package.json", "{}\n").commit();
    expect(check([], { PR_LABELS: '["documentation","contract-change"]' }).code).toBe(0);
    const near = check([], { PR_LABELS: '["contract-change-later"]' });
    expect(near.code).not.toBe(0);
    expect(near.output).toContain("packages/contracts/package.json");
  });

  it("counts a deleted contract file as a change", () => {
    repo.git("checkout", "-q", "main");
    repo.write("clickhouse/migrations/0001_items.sql", "-- v1\n").commit("contract on main");
    repo.git("branch", "-q", "-f", "sb/F4", "HEAD");
    repo.checkout("sb/F4");
    repo.remove("clickhouse/migrations/0001_items.sql").commit("delete");
    const result = check([]);
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("clickhouse/migrations/0001_items.sql");
  });

  it("counts a file moved out of a contract path as a change", () => {
    repo.git("checkout", "-q", "main");
    repo
      .write("packages/contracts/src/topics.ts", "export const topics = [];\n")
      .commit("contract on main");
    repo.git("branch", "-q", "-f", "sb/F4", "HEAD");
    repo.checkout("sb/F4");
    repo.write("packages/other/README.md", "x\n");
    repo.git("mv", "packages/contracts/src/topics.ts", "packages/other/topics.ts");
    repo.commit("move it out");
    const result = check([]);
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("packages/contracts/src/topics.ts");
  });

  it("runs quietly from a copy of scripts/ alone, as the policy job runs the base branch's copy", () => {
    const kit = mkdtempSync(join(tmpdir(), "policy-kit-"));
    try {
      cpSync(SCRIPTS, join(kit, "scripts"), { recursive: true });
      repo.write("services/demo/src/index.ts", "export {};\n").commit();
      const result = run(
        "bash",
        [join(kit, "scripts", "policy", "check-contract-paths.sh"), "--base", "main"],
        { cwd: repo.dir },
      );
      expect(result.code, result.output).toBe(0);
      expect(result.stderr).toBe("");
    } finally {
      rmSync(kit, { recursive: true, force: true });
    }
  });

  it("passes when no contract path changed", () => {
    repo.write("services/demo/src/index.ts", "export {};\n");
    repo.write("docs/contracts/README.md", "# Contracts\n").commit();
    const result = check([]);
    expect(result.code, result.output).toBe(0);
  });
});
