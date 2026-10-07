import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { parse } from "yaml";
import { readEnvFile, readText, requiredUv, satisfies } from "../helpers/pins.js";
import { cleanEnv, ROOT, script } from "../helpers/repo.js";

const ANONYMOUS = ["public.ecr.aws/", "ghcr.io/", "quay.io/"];
const MIRROR = "ghcr.io/abdullah95k/securebrand-v2/";
const EXACT_TAG = /^v?\d+(\.\d+){1,3}$/;

describe("version pins", () => {
  const versions = readEnvFile("stack/versions.env");
  const nodeVersion = readText(".node-version").trim();
  const pythonVersion = readText(".python-version").trim();
  const uvRange = requiredUv(readText("uv.toml")) ?? "";
  const uvFloor = /^>=(\d+\.\d+\.\d+)/.exec(uvRange)?.[1] ?? "";

  it("every image in compose.yaml is pinned to an exact tag from stack/versions.env", () => {
    const compose = parse(readText("compose.yaml")) as {
      services: Record<string, { image?: string }>;
    };
    const services = Object.entries(compose.services);
    expect(services.length).toBeGreaterThanOrEqual(3);
    for (const [name, service] of services) {
      const match = /^\$\{([A-Z0-9_]+)_REPO\}:\$\{\1_TAG\}$/.exec(service.image ?? "");
      expect(match, `${name}: ${service.image ?? "(no image)"}`).not.toBeNull();
      const key = match?.[1] ?? "";
      const tag = versions[`${key}_TAG`] ?? "";
      const repo = versions[`${key}_REPO`] ?? "";
      const upstream = versions[`${key}_UPSTREAM`] ?? "";
      expect(tag, `${key}_TAG`).toMatch(EXACT_TAG);
      expect(
        ANONYMOUS.some((host) => repo.startsWith(host)),
        `${key}_REPO=${repo}`,
      ).toBe(true);
      expect(upstream, `${key}_UPSTREAM`).not.toBe("");
      if (repo.startsWith(MIRROR)) {
        // A mirrored image names the publisher's registry it is copied from.
        expect(upstream).not.toContain(MIRROR);
      }
    }
  });

  it("pins the base images of the service templates to the toolchain versions", () => {
    expect(readText("services/_template/Dockerfile")).toContain(
      `public.ecr.aws/docker/library/node:${nodeVersion}-bookworm-slim`,
    );
    const py = readText("services/_template-py/Dockerfile");
    expect(py).toContain(`public.ecr.aws/docker/library/python:${pythonVersion}-slim-bookworm`);
    expect(py).toContain(`ghcr.io/astral-sh/uv:${uvFloor}`);
  });

  it("engines and packageManager agree with .node-version and the pnpm pin", () => {
    const pkg = JSON.parse(readText("package.json")) as {
      packageManager: string;
      engines: { node: string; pnpm: string };
      devDependencies: Record<string, string>;
    };
    expect(nodeVersion).toMatch(/^24\.\d+\.\d+$/);
    expect(satisfies(nodeVersion, pkg.engines.node)).toBe(true);
    const pnpm = /^pnpm@(\d+\.\d+\.\d+)$/.exec(pkg.packageManager)?.[1] ?? "";
    expect(pnpm).toMatch(/^10\./);
    expect(satisfies(pnpm, pkg.engines.pnpm)).toBe(true);
    for (const [name, version] of Object.entries(pkg.devDependencies)) {
      expect(version, name).toBe("catalog:");
    }
    const workspace = parse(readText("pnpm-workspace.yaml")) as { catalog: Record<string, string> };
    for (const [name, version] of Object.entries(workspace.catalog)) {
      expect(String(version), name).toMatch(/^\d+\.\d+\.\d+$/);
    }
    expect(workspace.catalog.typescript).toMatch(/^6\./);
  });

  it("pins uv the same way in uv.toml, every [tool.uv] table and CI", () => {
    expect(uvRange).toMatch(/^>=0\.12\.\d+,<0\.13$/);
    const template = readText("services/_template-py/pyproject.toml");
    expect(requiredUv(template)).toBe(uvRange);
    const ci = parse(readText(".github/workflows/ci.yml")) as {
      jobs: Record<string, { steps: { uses?: string; with?: { version?: string } }[] }>;
    };
    const setups = Object.values(ci.jobs).flatMap((job) =>
      job.steps.filter((step) => step.uses?.startsWith("astral-sh/setup-uv")),
    );
    expect(setups.length).toBeGreaterThan(0);
    for (const step of setups) {
      expect(step.with?.version).toBe(uvFloor);
    }
  });

  it("the Python version in .python-version satisfies every requires-python range", () => {
    expect(pythonVersion).toMatch(/^3\.13\.\d+$/);
    const range = /requires-python = "([^"]+)"/.exec(
      readText("services/_template-py/pyproject.toml"),
    )?.[1];
    expect(satisfies(pythonVersion, range ?? "")).toBe(true);
  });

  it("turbo.json declares TEST_* and stack variables in env so caching cannot return stale results", () => {
    const turbo = JSON.parse(readText("turbo.json")) as {
      tasks: Record<string, { env?: string[]; cache?: boolean; inputs?: string[] }>;
    };
    expect(turbo.tasks.test?.env).toContain("TEST_*");
    expect(turbo.tasks.test?.inputs).toContain("$TURBO_ROOT$/fixtures/**");
    const acceptance = turbo.tasks["test:acceptance"];
    expect(acceptance?.cache).toBe(false);
    for (const name of ["TEST_*", "KAFKA_*", "CLICKHOUSE_*", "S3_*", "SUPABASE_*"]) {
      expect(acceptance?.env).toContain(name);
    }
  });

  it("make doctor fails when the Node on PATH differs from .node-version (PATH shim)", () => {
    const shim = mkdtempSync(join(tmpdir(), "shim-"));
    const realNode = process.execPath;
    writeFileSync(
      join(shim, "node"),
      `#!/bin/sh\nif [ "$1" = "--version" ] || [ "$1" = "-v" ]; then echo v22.0.0; exit 0; fi\nexec "${realNode}" "$@"\n`,
      { mode: 0o755 },
    );
    const result = script("doctor.sh", [], {
      cwd: ROOT,
      env: cleanEnv({ PATH: `${shim}:${process.env.PATH ?? ""}`, NODE_AUTOSELECT: "0" }),
    });
    expect(result.code).not.toBe(0);
    expect(result.output).toMatch(/node/i);
    expect(result.output).toContain(nodeVersion);
    expect(result.output).toContain("22.0.0");
  });
});
