import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { cleanEnv, parseExports, script, TempRepo } from "../helpers/repo.js";

const SHAPE = /^[a-z][a-z0-9_]{0,31}$/;

function namespace(cwd: string, env: NodeJS.ProcessEnv = {}): Record<string, string> {
  const result = script("test-namespace.sh", [], { cwd, env: cleanEnv(env) });
  expect(result.code, result.output).toBe(0);
  return parseExports(result.stdout);
}

describe("scripts/test-namespace.sh", () => {
  let repo: TempRepo;

  beforeEach(() => {
    repo = new TempRepo("ns-");
    repo.write("README.md", "x\n").commit("base");
  });

  afterEach(() => {
    repo.cleanup();
  });

  it("derives the namespace from the linked worktree name", () => {
    const wt = join(mkdtempSync(join(tmpdir(), "wts-")), "FB2");
    repo.git("worktree", "add", "-q", "-b", "sb/FB2", wt);
    expect(namespace(wt).TEST_NAMESPACE).toBe("fb2");
  });

  it("derives it from the branch outside a linked worktree", () => {
    repo.branch("sb/C11");
    expect(namespace(repo.dir).TEST_NAMESPACE).toBe("sb_c11");
  });

  it("honours TEST_NAMESPACE", () => {
    repo.branch("sb/C11");
    expect(namespace(repo.dir, { TEST_NAMESPACE: "mine" }).TEST_NAMESPACE).toBe("mine");
  });

  it("uses the run id in CI", () => {
    const vars = namespace(repo.dir, { GITHUB_RUN_ID: "987654321", GITHUB_RUN_ATTEMPT: "2" });
    expect(vars.TEST_NAMESPACE).toBe("ci_987654321_2");
  });

  it("sanitizes to the allowed shape", () => {
    repo.branch("Feature/Ünïcode--X_Very-Long-Branch-Name-That-Goes-On-And-On-");
    const long = namespace(repo.dir).TEST_NAMESPACE ?? "";
    expect(long).toMatch(SHAPE);
    expect(long.endsWith("_")).toBe(false);

    repo.branch("123-fix");
    const digits = namespace(repo.dir).TEST_NAMESPACE ?? "";
    expect(digits).toMatch(SHAPE);
    expect(digits).toContain("123_fix");

    expect(namespace(repo.dir, { TEST_NAMESPACE: "My-NS!" }).TEST_NAMESPACE).toBe("my_ns");
  });

  it("gives two worktrees different namespaces", () => {
    const base = mkdtempSync(join(tmpdir(), "wts-"));
    repo.git("worktree", "add", "-q", "-b", "sb/F1", join(base, "F1"));
    repo.git("worktree", "add", "-q", "-b", "sb/F2", join(base, "F2"));
    const one = namespace(join(base, "F1")).TEST_NAMESPACE;
    const two = namespace(join(base, "F2")).TEST_NAMESPACE;
    expect(one).not.toBe(two);
  });

  it("keeps long names apart after truncation", () => {
    const base = mkdtempSync(join(tmpdir(), "wts-"));
    const prefix = "a-very-long-worktree-name-shared-by-both-";
    repo.git("worktree", "add", "-q", "--detach", join(base, `${prefix}one`));
    repo.git("worktree", "add", "-q", "--detach", join(base, `${prefix}two`));
    const one = namespace(join(base, `${prefix}one`)).TEST_NAMESPACE ?? "";
    const two = namespace(join(base, `${prefix}two`)).TEST_NAMESPACE ?? "";
    expect(one).toMatch(SHAPE);
    expect(two).toMatch(SHAPE);
    expect(one).not.toBe(two);
  });

  it("falls back to the worktree name, then local, on a detached HEAD", () => {
    repo.git("checkout", "-q", "--detach");
    expect(namespace(repo.dir).TEST_NAMESPACE).toBe("local");

    const wt = join(mkdtempSync(join(tmpdir(), "wts-")), "VFB1");
    repo.git("worktree", "add", "-q", "--detach", wt);
    expect(namespace(wt).TEST_NAMESPACE).toBe("vfb1");
  });

  it("exports the topic prefix, schema, database and bucket derived from the namespace", () => {
    const vars = namespace(repo.dir, { TEST_NAMESPACE: "abc_1" });
    expect(vars).toMatchObject({
      TEST_NAMESPACE: "abc_1",
      TEST_TOPIC_PREFIX: "abc_1.",
      TEST_PG_SCHEMA: "test_abc_1",
      TEST_PG_DATABASE: "test_abc_1",
      TEST_CH_DATABASE: "test_abc_1",
      TEST_S3_BUCKET: "test-abc-1",
    });
  });
});
