import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { cleanEnv, ROOT, run, SCRIPTS } from "../helpers/repo.js";

describe("scripts/lib/common.sh", () => {
  it("every script turns off pyright-python's and the Supabase CLI's version checks", () => {
    // A27, no network in tests: pyright-python asks pypi.org for pyright's latest version on every
    // run, and the Supabase CLI asks for its latest release. The scripts get both switches from
    // common.sh, so every script that runs pyright or the Supabase CLI must source it.
    const result = run(
      "bash",
      [
        "-c",
        `. ${SCRIPTS}/lib/common.sh; printf '%s %s' "$PYRIGHT_PYTHON_IGNORE_WARNINGS" "$SUPABASE_NO_UPDATE_NOTIFIER"`,
      ],
      {
        cwd: ROOT,
        env: cleanEnv({
          PYRIGHT_PYTHON_IGNORE_WARNINGS: undefined,
          SUPABASE_NO_UPDATE_NOTIFIER: undefined,
        }),
      },
    );
    expect(result.stdout, result.output).toBe("1 1");

    const scripts = run("git", ["ls-files", "--", "scripts"], { cwd: ROOT })
      .stdout.split("\n")
      .filter((file) => file.endsWith(".sh") && !file.startsWith("scripts/lib/"));
    const callers = scripts.filter((file) =>
      /pyright|node_modules\/\.bin\/supabase/.test(readFileSync(join(ROOT, file), "utf8")),
    );
    expect(callers).toEqual(
      expect.arrayContaining(["scripts/check-changed.sh", "scripts/doctor.sh"]),
    );
    for (const file of callers) {
      expect(readFileSync(join(ROOT, file), "utf8"), file).toContain("lib/common.sh");
    }
  });
});
