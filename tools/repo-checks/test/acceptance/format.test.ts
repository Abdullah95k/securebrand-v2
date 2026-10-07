import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { copyWorkingTree, type WorkingCopy } from "../helpers/worktree-copy.js";

const MINUTES = 60_000;

describe("make fmt", () => {
  let copy: WorkingCopy;

  beforeAll(() => {
    copy = copyWorkingTree();
  }, 10 * MINUTES);

  afterAll(() => {
    copy.cleanup();
  });

  it(
    "make fmt on a clean checkout leaves git status empty",
    () => {
      const fmt = copy.run("make", ["--no-print-directory", "fmt"]);
      expect(fmt.code, fmt.output).toBe(0);
      const status = copy.run("git", ["status", "--porcelain"]);
      expect(status.stdout.trim()).toBe("");
    },
    10 * MINUTES,
  );
});
