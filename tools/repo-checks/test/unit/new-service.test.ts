import {
  existsSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join, relative } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { cleanEnv, ROOT, run, TempRepo } from "../helpers/repo.js";

const GENERATOR = join(ROOT, "tools", "new-service", "index.mjs");

function generate(target: TempRepo, args: string[]): ReturnType<typeof run> {
  return run("node", [GENERATOR, ...args, "--root", target.dir, "--no-install"], {
    cwd: target.dir,
    env: cleanEnv(),
  });
}

/** Runs the generator with its install step, against the pnpm and uv stand-ins in `bin`. */
function generateAndInstall(target: TempRepo, args: string[], bin: string): ReturnType<typeof run> {
  return run("node", [GENERATOR, ...args, "--root", target.dir], {
    cwd: target.dir,
    env: cleanEnv({ PATH: `${bin}:${process.env.PATH ?? ""}` }),
  });
}

/** A stand-in for pnpm or uv that records the arguments of each call and exits with `code`. */
function standIn(bin: string, tool: string, code: number): () => string[] {
  const log = join(bin, `${tool}.calls`);
  writeFileSync(join(bin, tool), `#!/bin/sh\necho "$*" >> "${log}"\nexit ${String(code)}\n`, {
    mode: 0o755,
  });
  return () => (existsSync(log) ? readFileSync(log, "utf8").split("\n").filter(Boolean) : []);
}

// The shape of pnpm-lock.yaml: the template is a workspace, so its entry holds the dependencies
// a generated service starts with.
const LOCKFILE = `lockfileVersion: '9.0'

importers:

  .:
    devDependencies:
      turbo:
        specifier: 'catalog:'
        version: 2.10.13

  services/_template:
    devDependencies:
      typescript:
        specifier: 'catalog:'
        version: 6.0.3

  tools/new-service: {}

packages:

  typescript@6.0.3:
    resolution: {integrity: sha512-0}
`;

function files(dir: string): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      out.push(...files(full));
    } else {
      out.push(full);
    }
  }
  return out;
}

describe("pnpm new:service (tools/new-service)", () => {
  let target: TempRepo;

  beforeEach(() => {
    target = new TempRepo("new-service-");
  });

  afterEach(() => {
    target.cleanup();
  });

  it.each([
    "Fb-Poller",
    "fb",
    "news",
    "fb_page_feed_poller",
    "-poller",
    "poller-",
    "page--poller",
    "1poller",
    "_template",
    "service-template",
    "poller.v2",
    "a".repeat(64),
  ])("rejects %s, a name outside the naming convention", (name) => {
    const result = generate(target, [name]);
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/CONVENTIONS|naming/i);
    expect(target.exists(`services/${name}`)).toBe(false);
  });

  it.each(["fb-page-feed-poller", "news-article-extractor", "x-search", "normalize-item", "demo"])(
    "accepts %s, a per-source or shared name",
    (name) => {
      const result = generate(target, [name]);
      expect(result.code, result.output).toBe(0);
      expect(target.exists(`services/${name}/package.json`)).toBe(true);
    },
  );

  it("refuses to overwrite an existing service", () => {
    target.write("services/demo/keep.txt", "mine\n");
    const result = generate(target, ["demo"]);
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/already exists/i);
    expect(target.read("services/demo/keep.txt")).toBe("mine\n");
    expect(target.exists("services/demo/package.json")).toBe(false);
  });

  it("leaves no template placeholder behind in the generated tree", () => {
    expect(generate(target, ["fb-page-feed-poller"]).code).toBe(0);
    expect(generate(target, ["news-demo-extractor", "--lang", "python"]).code).toBe(0);
    for (const file of files(target.path("services"))) {
      const text = readFileSync(file, "utf8");
      expect(text, relative(target.dir, file)).not.toMatch(/service[-_]template/);
      expect(relative(target.dir, file)).not.toMatch(/service[-_]template/);
    }
    const pkg = JSON.parse(target.read("services/fb-page-feed-poller/package.json")) as {
      name: string;
    };
    expect(pkg.name).toBe("fb-page-feed-poller");
    expect(target.read("services/news-demo-extractor/pyproject.toml")).toContain(
      'name = "news-demo-extractor"',
    );
    expect(target.exists("services/news-demo-extractor/src/news_demo_extractor/__init__.py")).toBe(
      true,
    );
    expect(target.read("services/news-demo-extractor/uv.lock")).toContain(
      'name = "news-demo-extractor"',
    );
  });

  it("copies no dependencies, build output, virtualenv or cache from the template", () => {
    expect(generate(target, ["demo"]).code).toBe(0);
    expect(generate(target, ["demo-py", "--lang", "python"]).code).toBe(0);
    const generated = files(target.path("services")).map((f) => relative(target.dir, f));
    for (const forbidden of [
      "node_modules",
      "dist",
      ".turbo",
      ".venv",
      "__pycache__",
      ".pytest_cache",
      ".ruff_cache",
    ]) {
      expect(generated.filter((f) => f.split("/").includes(forbidden))).toEqual([]);
    }
  });

  it("rejects an unknown language", () => {
    const result = generate(target, ["demo", "--lang", "go"]);
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/--lang/);
  });

  it("prints the next commands", () => {
    const result = generate(target, ["demo"]);
    expect(result.output).toContain("make test SERVICE=demo");
  });

  describe("the install, which never needs the network", () => {
    let bin: string;

    beforeEach(() => {
      bin = mkdtempSync(join(tmpdir(), "new-service-bin-"));
      target.write("pnpm-lock.yaml", LOCKFILE);
    });

    afterEach(() => {
      rmSync(bin, { recursive: true, force: true });
    });

    it("adds a TypeScript service to pnpm-lock.yaml with the template's dependencies and installs it offline from the frozen lockfile", () => {
      const pnpm = standIn(bin, "pnpm", 0);
      const result = generateAndInstall(target, ["fb-page-feed-poller"], bin);
      expect(result.code, result.output).toBe(0);
      // Nothing left to resolve, so pnpm needs no registry metadata, only its store.
      expect(pnpm()).toEqual(["install --offline --frozen-lockfile"]);
      expect(target.read("pnpm-lock.yaml")).toBe(
        LOCKFILE.replace(
          "  tools/new-service: {}",
          [
            "  services/fb-page-feed-poller:",
            "    devDependencies:",
            "      typescript:",
            "        specifier: 'catalog:'",
            "        version: 6.0.3",
            "",
            "  tools/new-service: {}",
          ].join("\n"),
        ),
      );
    });

    it("replaces a stale lockfile entry of the same name and appends after the last importer", () => {
      standIn(bin, "pnpm", 0);
      const lockfile = LOCKFILE.replace(
        "  tools/new-service: {}\n\n",
        "  services/demo:\n    dependencies:\n      gone:\n        specifier: 1.0.0\n        version: 1.0.0\n\n",
      );
      target.write("pnpm-lock.yaml", lockfile);
      const template = [
        "    devDependencies:",
        "      typescript:",
        "        specifier: 'catalog:'",
        "        version: 6.0.3",
      ];
      expect(generateAndInstall(target, ["demo"], bin).code).toBe(0);
      expect(generateAndInstall(target, ["web-search"], bin).code).toBe(0);
      const importers = target.read("pnpm-lock.yaml").split("\npackages:")[0] ?? "";
      expect(importers.endsWith(["  services/web-search:", ...template, ""].join("\n"))).toBe(true);
      expect(importers).toContain(["  services/demo:", ...template, "", ""].join("\n"));
      expect(importers).not.toContain("gone");
    });

    it("installs a Python service offline from uv's cache and its copied lockfile", () => {
      const uv = standIn(bin, "uv", 0);
      const result = generateAndInstall(target, ["news-demo-extractor", "--lang", "python"], bin);
      expect(result.code, result.output).toBe(0);
      expect(uv()).toEqual(["sync --locked --offline"]);
      expect(target.read("pnpm-lock.yaml")).toBe(LOCKFILE);
    });

    it("stops and says what to run when an offline install fails, without trying the registry", () => {
      const pnpm = standIn(bin, "pnpm", 1);
      const uv = standIn(bin, "uv", 1);

      const ts = generateAndInstall(target, ["demo"], bin);
      expect(ts.code).not.toBe(0);
      expect(pnpm()).toEqual(["install --offline --frozen-lockfile"]);
      expect(ts.output).toMatch(/services\/demo was created.*\n?.*pnpm install/);

      const py = generateAndInstall(target, ["demo-py", "--lang", "python"], bin);
      expect(py.code).not.toBe(0);
      expect(uv()).toEqual(["sync --locked --offline"]);
      expect(py.output).toMatch(/services\/demo-py was created.*\n?.*uv sync --locked/);
    });
  });
});
