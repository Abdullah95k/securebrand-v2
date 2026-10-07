// G0 check 1 in a copy of the working tree: `pnpm new:service <name>` produces a service that
// passes make check and its own unit and acceptance suites without edits. CHECK_BASE=HEAD makes
// make check look only at the generated service (the copy's single commit is the working tree).
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { copyWorkingTree, type WorkingCopy } from "../helpers/worktree-copy.js";

const MINUTES = 60_000;

describe("pnpm new:service in a clean copy of the repository", () => {
  let copy: WorkingCopy;

  beforeAll(() => {
    copy = copyWorkingTree();
  }, 10 * MINUTES);

  afterAll(() => {
    copy.cleanup();
  });

  it(
    "generates a TypeScript service that passes lint, typecheck and both test suites without edits",
    () => {
      const generated = copy.run("pnpm", ["new:service", "demo"]);
      expect(generated.code, generated.output).toBe(0);

      const check = copy.run("make", ["--no-print-directory", "check"], { CHECK_BASE: "HEAD" });
      expect(check.code, check.output).toBe(0);
      expect(check.output).toMatch(/step turbo lint typecheck test :: demo$/m);

      const tests = copy.run("make", ["--no-print-directory", "test", "SERVICE=demo"]);
      expect(tests.code, tests.output).toBe(0);
      expect(tests.output).toMatch(/test\/acceptance\//);
    },
    15 * MINUTES,
  );

  it(
    "generates a Python service that passes ruff, pyright and pytest without edits",
    () => {
      const generated = copy.run("pnpm", ["new:service", "demo-py", "--lang", "python"]);
      expect(generated.code, generated.output).toBe(0);

      const check = copy.run("make", ["--no-print-directory", "check"], { CHECK_BASE: "HEAD" });
      expect(check.code, check.output).toBe(0);
      expect(check.output).toMatch(/^step python services\/demo-py :: /m);

      const tests = copy.run("make", ["--no-print-directory", "test", "SERVICE=demo-py"]);
      expect(tests.code, tests.output).toBe(0);
      expect(tests.output).toMatch(/tests\/acceptance\//);
    },
    15 * MINUTES,
  );
});
