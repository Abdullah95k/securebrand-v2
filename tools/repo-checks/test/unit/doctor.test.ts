import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { cleanEnv, ROOT, script } from "../helpers/repo.js";

describe("make doctor (scripts/doctor.sh)", () => {
  it("names each missing or mismatched tool and exits non-zero", () => {
    const shim = mkdtempSync(join(tmpdir(), "shim-"));
    const realNode = process.execPath;
    writeFileSync(
      join(shim, "node"),
      `#!/bin/sh\nif [ "$1" = "--version" ]; then echo v20.1.0; exit 0; fi\nexec "${realNode}" "$@"\n`,
      { mode: 0o755 },
    );
    writeFileSync(join(shim, "pnpm"), "#!/bin/sh\necho 9.15.0\n", { mode: 0o755 });
    // Only the shims and the system directories: uv (installed under the home directory) is absent.
    const result = script("doctor.sh", [], {
      cwd: ROOT,
      env: cleanEnv({ PATH: `${shim}:/usr/bin:/bin`, NODE_AUTOSELECT: "0" }),
    });
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/node.*20\.1\.0/i);
    expect(result.output).toMatch(/pnpm.*9\.15\.0/i);
    expect(result.output).toMatch(/uv.*(missing|not found)/i);
  });
});
