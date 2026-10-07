import { accessSync, constants, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { ROOT, run } from "../helpers/repo.js";

function makeTargets(): string[] {
  const makefile = readFileSync(join(ROOT, "Makefile"), "utf8");
  const targets = new Set<string>();
  for (const line of makefile.split("\n")) {
    const match = /^([a-z][a-z0-9-]*):(?!=)/.exec(line);
    if (match?.[1] !== undefined) {
      targets.add(match[1]);
    }
  }
  return [...targets].sort();
}

function pythonProjects(): string[] {
  const tracked = run("git", ["ls-files", "--cached", "--others", "--exclude-standard"], {
    cwd: ROOT,
  });
  return tracked.stdout
    .split("\n")
    .filter((f) => f.endsWith("/pyproject.toml") && !f.includes("/fixtures/"))
    .map((f) => f.slice(0, -"/pyproject.toml".length));
}

describe("kit fit", () => {
  it("prettier exists where the format hook looks", () => {
    expect(() => {
      accessSync(join(ROOT, "node_modules", ".bin", "prettier"), constants.X_OK);
    }).not.toThrow();
  });

  it("every Python project lists ruff in its dev group, so the format hook can run it", () => {
    const projects = pythonProjects();
    expect(projects).toContain("services/_template-py");
    for (const project of projects) {
      const text = readFileSync(join(ROOT, project, "pyproject.toml"), "utf8");
      const dev = /\[dependency-groups\][^[]*?dev\s*=\s*\[([^\]]*)\]/s.exec(text)?.[1] ?? "";
      expect(dev, project).toMatch(/"ruff[=<>~]/);
    }
  });

  it("no __pycache__ directory is tracked", () => {
    const tracked = run("git", ["ls-files"], { cwd: ROOT }).stdout.split("\n");
    expect(tracked.filter((f) => f.includes("__pycache__/") || f.endsWith(".pyc"))).toEqual([]);
  });

  it("settings.json allows every make target the Makefile defines", () => {
    const settings = JSON.parse(readFileSync(join(ROOT, ".claude", "settings.json"), "utf8")) as {
      permissions: { allow: string[] };
    };
    const allow = new Set(settings.permissions.allow);
    const targets = makeTargets();
    expect(targets).toEqual(
      expect.arrayContaining(["bootstrap", "check", "doctor", "down", "e2e", "test", "up"]),
    );
    for (const target of targets) {
      const allowed = allow.has(`Bash(make ${target})`) || allow.has(`Bash(make ${target} *)`);
      expect(allowed, `Bash(make ${target}) is not in .claude/settings.json`).toBe(true);
    }
    expect(allow.has("Bash(pnpm new:service *)")).toBe(true);
  });

  it("the stop hook still finds scripts/check-changed.sh", () => {
    const hook = readFileSync(join(ROOT, ".claude", "hooks", "stop-gate.sh"), "utf8");
    expect(hook).toContain("scripts/check-changed.sh");
    expect(() => {
      accessSync(join(ROOT, "scripts", "check-changed.sh"), constants.X_OK);
    }).not.toThrow();
  });

  it(".gitignore covers build outputs, virtualenvs and caches", () => {
    const ignore = readFileSync(join(ROOT, ".gitignore"), "utf8").split("\n");
    for (const entry of [
      "node_modules/",
      "dist/",
      ".turbo/",
      "coverage/",
      ".venv/",
      "__pycache__/",
    ]) {
      expect(ignore).toContain(entry);
    }
  });

  it("CLAUDE.md lists the make targets sessions use", () => {
    const claude = readFileSync(join(ROOT, "CLAUDE.md"), "utf8");
    for (const target of [
      "make bootstrap",
      "make doctor",
      "make smoke",
      "make ns-clean",
      "make policy",
    ]) {
      expect(claude).toContain(target);
    }
  });
});
