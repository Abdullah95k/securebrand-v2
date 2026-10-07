import { readFileSync } from "node:fs";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { FIXTURES, script, TempRepo } from "../helpers/repo.js";

function review(name: string): string {
  return readFileSync(join(FIXTURES, "reviews", name), "utf8");
}

describe("scripts/policy/check-handoff-review.sh", () => {
  let repo: TempRepo;

  function check(branch: string): ReturnType<typeof script> {
    return script("policy/check-handoff-review.sh", ["--base", "main", "--branch", branch], {
      cwd: repo.dir,
    });
  }

  beforeEach(() => {
    repo = new TempRepo("policy-review-");
    repo.write("README.md", "x\n").commit("base");
    repo.branch("sb/C11");
    repo.write("services/comment-decay-scheduler/src/index.ts", "export {};\n");
  });

  afterEach(() => {
    repo.cleanup();
  });

  it("fails when the handoff is missing", () => {
    repo.write("docs/reviews/C11.md", review("ready.md")).commit();
    const result = check("sb/C11");
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("docs/handoffs/C11.md");
  });

  it("fails when the review is missing", () => {
    repo.write("docs/handoffs/C11.md", "# Handoff\n").commit();
    const result = check("sb/C11");
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("docs/reviews/C11.md");
  });

  it("fails when the review verdict is needs fixes", () => {
    repo.write("docs/handoffs/C11.md", "# Handoff\n");
    repo.write("docs/reviews/C11.md", review("needs-fixes.md")).commit();
    const result = check("sb/C11");
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/needs fixes/i);
  });

  it("passes when the review verdict is ready to merge", () => {
    repo.write("docs/handoffs/C11.md", "# Handoff\n");
    repo.write("docs/reviews/C11.md", review("ready.md")).commit();
    const result = check("sb/C11");
    expect(result.code, result.output).toBe(0);
  });

  it("passes when the latest recheck verdict is ready to merge", () => {
    repo.write("docs/handoffs/C11.md", "# Handoff\n");
    repo.write("docs/reviews/C11.md", review("recheck-ready.md")).commit();
    const result = check("sb/C11");
    expect(result.code, result.output).toBe(0);
  });

  it("fails when the latest recheck still needs fixes, whatever the first verdict said", () => {
    repo.write("docs/handoffs/C11.md", "# Handoff\n");
    repo.write("docs/reviews/C11.md", review("recheck-needs-fixes.md")).commit();
    const result = check("sb/C11");
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/needs fixes/i);
  });

  it("fails when the review has no readable verdict", () => {
    repo.write("docs/handoffs/C11.md", "# Handoff\n");
    repo.write("docs/reviews/C11.md", review("template-only.md")).commit();
    const result = check("sb/C11");
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/verdict/i);
  });

  it.each([
    "packages/listening-sdk/src/x.ts",
    "py/listening_sdk/x.py",
    "tools/probes/meta/p.ts",
    "tests/e2e/G1/s.ts",
  ])("gates changes under %s", (path) => {
    repo.git("checkout", "-q", "-f", "main");
    repo.git("clean", "-q", "-fd");
    repo.branch("sb/X1");
    repo.write(path, "x\n").commit();
    const result = check("sb/X1");
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("docs/handoffs/X1.md");
  });

  it("passes for changes outside the gated paths", () => {
    repo.git("checkout", "-q", "-f", "main");
    repo.git("clean", "-q", "-fd");
    repo.branch("sb/D2");
    repo.write("docs/decisions/ADR-0001-x.md", "# ADR\n").commit();
    const result = check("sb/D2");
    expect(result.code, result.output).toBe(0);
  });

  it("skips with a notice on branches that are not sb/<ID>", () => {
    repo.commit();
    const result = check("dependabot/npm_and_yarn/vitest-4.2.0");
    expect(result.code, result.output).toBe(0);
    expect(result.output).toMatch(/skip/i);
  });

  it("requires the applied proposal on a contract-change branch", () => {
    repo.git("checkout", "-q", "-f", "main");
    repo.git("clean", "-q", "-fd");
    repo.branch("sb/CC-F4-topic-x");
    repo.write("packages/contracts/src/topics.ts", "export {};\n");
    repo.write(
      "docs/proposals/F4-topic-x.md",
      "# Proposal · F4 · topic x\n\nRaised by: session F4 · 2026-10-07\nDecision: approved (user, 2026-10-07)\nApplied: no\n",
    );
    repo.commit();
    const unapplied = check("sb/CC-F4-topic-x");
    expect(unapplied.code).not.toBe(0);
    expect(unapplied.output).toContain("docs/proposals/F4-topic-x.md");

    repo.write(
      "docs/proposals/F4-topic-x.md",
      "# Proposal · F4 · topic x\n\nRaised by: session F4 · 2026-10-07\nDecision: approved (user, 2026-10-07)\nApplied: 0123abc\n",
    );
    repo.commit();
    const applied = check("sb/CC-F4-topic-x");
    expect(applied.code, applied.output).toBe(0);
  });
});
