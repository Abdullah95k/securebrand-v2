// G0 check 1 in a copy of the working tree: `pnpm new:service <name>` produces a service that
// passes make check and its own unit and acceptance suites without edits. CHECK_BASE=HEAD makes
// make check look only at the generated service (the copy's single commit is the working tree).
//
// No network (A27): pnpm and uv run offline throughout, so a step that needed the registry would
// fail instead of fetching. The generator installs from pnpm's store and uv's cache, which the
// working copy's install and CI's install step fill; pnpm's metadata cache is empty, as on a fresh
// CI runner, so pnpm cannot resolve anything either.
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { copyWorkingTree, type WorkingCopy } from "../helpers/worktree-copy.js";

const MINUTES = 60_000;
const OFFLINE = { npm_config_offline: "true", UV_OFFLINE: "1" };

describe("pnpm new:service in a clean copy of the repository", () => {
  let copy: WorkingCopy;
  let coldCache: string;

  beforeAll(() => {
    copy = copyWorkingTree();
    coldCache = mkdtempSync(join(tmpdir(), "pnpm-cache-"));
  }, 10 * MINUTES);

  afterAll(() => {
    copy.cleanup();
    rmSync(coldCache, { recursive: true, force: true });
  });

  it(
    "generates a TypeScript service that passes lint, typecheck and both test suites without edits",
    () => {
      // CI=true as in GitHub Actions, where pnpm defaults to a frozen lockfile.
      const generated = copy.run("pnpm", ["new:service", "demo"], {
        CI: "true",
        ...OFFLINE,
        npm_config_cache_dir: coldCache,
      });
      expect(generated.code, generated.output).toBe(0);

      const check = copy.run("make", ["--no-print-directory", "check"], {
        CHECK_BASE: "HEAD",
        ...OFFLINE,
      });
      expect(check.code, check.output).toBe(0);
      expect(check.output).toMatch(/step turbo lint typecheck test :: demo$/m);

      const tests = copy.run("make", ["--no-print-directory", "test", "SERVICE=demo"], OFFLINE);
      expect(tests.code, tests.output).toBe(0);
      expect(tests.output).toMatch(/test\/acceptance\//);
    },
    15 * MINUTES,
  );

  it(
    "generates a Python service that passes ruff, pyright and pytest without edits",
    () => {
      const generated = copy.run("pnpm", ["new:service", "demo-py", "--lang", "python"], {
        CI: "true",
        ...OFFLINE,
      });
      expect(generated.code, generated.output).toBe(0);

      const check = copy.run("make", ["--no-print-directory", "check"], {
        CHECK_BASE: "HEAD",
        ...OFFLINE,
      });
      expect(check.code, check.output).toBe(0);
      expect(check.output).toMatch(/^step python services\/demo-py :: /m);

      const tests = copy.run("make", ["--no-print-directory", "test", "SERVICE=demo-py"], OFFLINE);
      expect(tests.code, tests.output).toBe(0);
      expect(tests.output).toMatch(/tests\/acceptance\//);
    },
    15 * MINUTES,
  );
});
