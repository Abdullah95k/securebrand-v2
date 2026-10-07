import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { cleanEnv, FIXTURES, ROOT, run, TempRepo } from "../helpers/repo.js";

function makeE2e(args: string[], env: NodeJS.ProcessEnv = {}): ReturnType<typeof run> {
  return run("make", ["--no-print-directory", "e2e", ...args], { cwd: ROOT, env: cleanEnv(env) });
}

describe("make e2e", () => {
  it("fails naming E1 while tests/e2e/G1 is missing", () => {
    const empty = mkdtempSync(join(tmpdir(), "e2e-empty-"));
    const result = makeE2e(["GATE=G1"], { E2E_DIR: empty });
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/\bE1\b/);
    expect(result.output).toContain("G1");
  });

  it("runs the suite runner when the directory exists (E2E_DIR override)", () => {
    const stub = new TempRepo("e2e-stub-");
    stub.copyIn(join(FIXTURES, "e2e-stub", "G1"), "G1");
    const result = makeE2e(["GATE=G1"], { E2E_DIR: stub.dir });
    expect(result.code, result.output).toBe(0);
    expect(result.output).toContain("stub suite ran for G1");
    stub.cleanup();
  });

  it("names E2 and tools/gates for the gates after G1", () => {
    const empty = mkdtempSync(join(tmpdir(), "e2e-empty-"));
    const result = makeE2e(["GATE=G2"], { E2E_DIR: empty });
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/\bE2\b/);
    expect(result.output).toContain("tools/gates");
  });

  it("asks for a gate when none is given", () => {
    const result = makeE2e([]);
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("GATE=");
  });
});
