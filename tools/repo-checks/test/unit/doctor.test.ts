import { mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { readText } from "../helpers/pins.js";
import { cleanEnv, ROOT, script } from "../helpers/repo.js";

const NODE_PIN = readText(".node-version").trim();

/** A node that answers --version with `version` and runs everything else on the real node. */
function nodeShim(dir: string, version: string): void {
  mkdirSync(dir, { recursive: true });
  writeFileSync(
    join(dir, "node"),
    `#!/bin/sh\nif [ "$1" = "--version" ] || [ "$1" = "-v" ]; then echo v${version}; exit 0; fi\nexec "${process.execPath}" "$@"\n`,
    { mode: 0o755 },
  );
}

describe("make doctor (scripts/doctor.sh)", () => {
  it("names each missing or mismatched tool and exits non-zero", () => {
    const shim = mkdtempSync(join(tmpdir(), "shim-"));
    nodeShim(shim, "20.1.0");
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

  it("fails naming the shell's node and the switch when only the make targets run the pinned node", () => {
    // The cloud container: nvm holds the pin, which the scripts put first on their own PATH, but
    // the shell that typed `make doctor` runs another node, and pnpm commands typed there refuse it.
    const dir = mkdtempSync(join(tmpdir(), "doctor-"));
    nodeShim(join(dir, "nvm", "versions", "node", `v${NODE_PIN}`, "bin"), NODE_PIN);
    nodeShim(join(dir, "shell"), "22.22.0");
    const result = script("doctor.sh", [], {
      cwd: ROOT,
      env: cleanEnv({
        PATH: `${join(dir, "shell")}:${process.env.PATH ?? ""}`,
        NVM_DIR: join(dir, "nvm"),
      }),
    });
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(new RegExp(`^ok +node ${NODE_PIN.replaceAll(".", "\\.")}`, "m"));
    expect(result.output).toMatch(/^FAIL +node on your PATH: 22\.22\.0 /m);
    expect(result.output).toContain(`nvm use ${NODE_PIN}`);
  });
});

describe("make bootstrap (scripts/bootstrap.sh)", () => {
  it("makes the pinned node nvm's default when the shell runs another, and ends saying how to switch", () => {
    // Stand-ins for nvm, pnpm and uv record their calls, so bootstrap installs nothing for real.
    const dir = mkdtempSync(join(tmpdir(), "bootstrap-"));
    const nvm = join(dir, "nvm");
    nodeShim(join(nvm, "versions", "node", `v${NODE_PIN}`, "bin"), NODE_PIN);
    writeFileSync(join(nvm, "nvm.sh"), `nvm() { echo "nvm $*" >> "${join(dir, "calls")}"; }\n`);
    const shell = join(dir, "shell");
    nodeShim(shell, "22.22.0");
    const pnpmPin = /"pnpm@([\d.]+)"/.exec(readText("package.json"))?.[1] ?? "";
    const uvFloor = /required-version = ">=([\d.]+)/.exec(readText("uv.toml"))?.[1] ?? "";
    for (const [tool, version] of [
      ["pnpm", pnpmPin],
      ["uv", `uv ${uvFloor}`],
    ] as const) {
      writeFileSync(
        join(shell, tool),
        `#!/bin/sh\nif [ "$1" = "--version" ]; then echo "${version}"; exit 0; fi\necho "${tool} $*" >> "${join(dir, "calls")}"\n`,
        { mode: 0o755 },
      );
    }
    const result = script("bootstrap.sh", [], {
      cwd: ROOT,
      env: cleanEnv({ PATH: `${shell}:${process.env.PATH ?? ""}`, NVM_DIR: nvm }),
      timeoutMs: 120_000,
    });
    const calls = readFileSync(join(dir, "calls"), "utf8").split("\n");
    expect(calls, result.output).toContain(`nvm alias default ${NODE_PIN}`);
    expect(calls).toContain("pnpm install --frozen-lockfile");
    // It cannot switch the shell that ran it, so it says how instead of failing over it.
    expect(result.output).not.toContain("node on your PATH");
    expect(result.output).toMatch(
      new RegExp(`this shell runs v22\\.22\\.0.*\\n?.*nvm use ${NODE_PIN}`),
    );
  });
});
