import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { readText } from "../helpers/pins.js";
import { cleanEnv, ROOT, run, script, type RunResult } from "../helpers/repo.js";

const NODE_PIN = readText(".node-version").trim();
const PYTHON_PIN = readText(".python-version").trim();
const PNPM_PIN = /"pnpm@([\d.]+)"/.exec(readText("package.json"))?.[1] ?? "";
const UV_FLOOR = /required-version = ">=([\d.]+)/.exec(readText("uv.toml"))?.[1] ?? "";

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

  // Stand-ins for nvm, the shell's node 22, pnpm, uv and python3's pip, with a fresh HOME: bootstrap
  // runs for real in this checkout, and its uv step falls back to $HOME/.local/bin/uv, which here is
  // whatever uv the developer has there.
  interface Rig {
    dir: string;
    shell: string;
    home: string;
    bootstrap: () => RunResult;
    calls: () => string[];
  }

  function rig(opts: { nvmHasPin?: boolean; uv?: "pinned" | "pip"; shellNode?: string } = {}): Rig {
    const dir = mkdtempSync(join(tmpdir(), "bootstrap-"));
    const callsFile = join(dir, "calls");
    const nvm = join(dir, "nvm");
    mkdirSync(nvm);
    if (opts.nvmHasPin ?? true) {
      nodeShim(join(nvm, "versions", "node", `v${NODE_PIN}`, "bin"), NODE_PIN);
      // As nvm alias default writes it.
      mkdirSync(join(nvm, "alias"));
      writeFileSync(join(nvm, "alias", "default"), `${NODE_PIN}\n`);
    }
    // nvm install answers 3 the way nvm 0.39 does offline, even for an installed version.
    writeFileSync(
      join(nvm, "nvm.sh"),
      `nvm() { echo "nvm $*" >> "${callsFile}"; [ "$1" = install ] && return 3; return 0; }\n`,
    );
    const shell = join(dir, "shell");
    nodeShim(shell, opts.shellNode ?? "22.22.0");
    writeFileSync(
      join(shell, "pnpm"),
      `#!/bin/sh\nif [ "$1" = "--version" ]; then echo "${PNPM_PIN}"; exit 0; fi\necho "pnpm $*" >> "${callsFile}"\n`,
      { mode: 0o755 },
    );
    if ((opts.uv ?? "pinned") === "pinned") {
      writeFileSync(
        join(shell, "uv"),
        `#!/bin/sh\nif [ "$1" = "--version" ]; then echo "uv ${UV_FLOOR}"; exit 0; fi\necho "uv $*" >> "${callsFile}"\n`,
        { mode: 0o755 },
      );
    } else {
      // A uv that pip installed: it answers --version from a state file and cannot update itself.
      const state = join(dir, "uv-version");
      writeFileSync(state, "uv 0.11.32\n");
      writeFileSync(
        join(shell, "uv"),
        `#!/bin/sh\nif [ "$1" = "--version" ]; then cat "${state}"; exit 0; fi\nif [ "$1" = "self" ]; then echo "error: Self-update is only available for uv binaries installed via the standalone installation scripts." >&2; exit 2; fi\necho "uv $*" >> "${callsFile}"\n`,
        { mode: 0o755 },
      );
    }
    const home = join(dir, "home");
    mkdirSync(home);
    return {
      dir,
      shell,
      home,
      bootstrap: () =>
        script("bootstrap.sh", [], {
          cwd: ROOT,
          env: cleanEnv({ PATH: `${shell}:${process.env.PATH ?? ""}`, NVM_DIR: nvm, HOME: home }),
          timeoutMs: 120_000,
        }),
      calls: () => (existsSync(callsFile) ? readFileSync(callsFile, "utf8").split("\n") : []),
    };
  }

  /** A python3 whose pip says it owns uv and records installs; `upgrades` makes the install
   * replace the uv stand-in's version with the pin. Everything else runs on the real python3. */
  function pipShim(r: Rig, upgrades: boolean): void {
    const python3 = run("bash", ["-c", "command -v python3"], { cwd: ROOT }).stdout.trim();
    const upgrade = upgrades ? `echo "uv ${UV_FLOOR}" > "${join(r.dir, "uv-version")}"` : ":";
    writeFileSync(
      join(r.shell, "python3"),
      [
        "#!/bin/sh",
        'if [ "$1 $2 $3" = "-m pip show" ]; then exit 0; fi',
        `if [ "$1 $2 $3" = "-m pip install" ]; then echo "python3 $*" >> "${join(r.dir, "calls")}"; ${upgrade}; exit 0; fi`,
        `exec "${python3}" "$@"`,
        "",
      ].join("\n"),
      { mode: 0o755 },
    );
  }

  it("runs no nvm command when nvm already holds the pin as its default, so a second run needs no network", () => {
    const r = rig();
    const result = r.bootstrap();
    expect(
      r.calls().filter((line) => /^nvm (install|alias)/.test(line)),
      result.output,
    ).toEqual([]);
    expect(result.output).toContain(`bootstrap: node v${NODE_PIN}`);
  });

  it("stops naming nodejs.org when nvm lacks the pin and nvm install fails", () => {
    const r = rig({ nvmHasPin: false });
    const result = r.bootstrap();
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/nvm could not install Node .*nodejs\.org/);
  });

  // The uv cases run in a shell already on the pinned node, so the Node step does nothing.
  it("installs the pinned uv with pip --user when uv self update fails because pip installed uv", () => {
    const r = rig({ uv: "pip", shellNode: NODE_PIN });
    pipShim(r, true);
    const result = r.bootstrap();
    expect(r.calls(), result.output).toContain(
      `python3 -m pip install --user --quiet --upgrade uv==${UV_FLOOR}`,
    );
    expect(r.calls(), result.output).toContain(`uv python install ${PYTHON_PIN}`);
    expect(result.output).not.toContain("could not update itself");
  });

  it("stops naming the uv it found when uv is still outside the range after the update", () => {
    const r = rig({ uv: "pip", shellNode: NODE_PIN });
    pipShim(r, false); // pip "installs" uv, but the uv on PATH stays 0.11.32
    const result = r.bootstrap();
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/uv is still 0\.11\.32/);
  });

  it("uses ~/.local/bin/uv when pip put the pin there behind another uv on PATH, and says to put ~/.local/bin first", () => {
    const r = rig({ uv: "pip", shellNode: NODE_PIN });
    pipShim(r, false);
    const localBin = join(r.home, ".local", "bin");
    const localCalls = join(r.dir, "local-calls");
    mkdirSync(localBin, { recursive: true });
    writeFileSync(
      join(localBin, "uv"),
      `#!/bin/sh\nif [ "$1" = "--version" ]; then echo "uv ${UV_FLOOR}"; exit 0; fi\necho "$*" >> "${localCalls}"\n`,
      { mode: 0o755 },
    );
    const result = r.bootstrap();
    expect(result.output).toContain("put ~/.local/bin first");
    const recorded = existsSync(localCalls) ? readFileSync(localCalls, "utf8").split("\n") : [];
    expect(recorded, result.output).toContain(`python install ${PYTHON_PIN}`);
  });
});
