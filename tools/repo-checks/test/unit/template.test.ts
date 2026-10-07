import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { ROOT } from "../helpers/repo.js";

const TS = join(ROOT, "services", "_template");
const PY = join(ROOT, "services", "_template-py");

function read(file: string): string {
  return readFileSync(file, "utf8");
}

function testFiles(dir: string, suffix: string): string[] {
  return existsSync(dir) ? readdirSync(dir).filter((f) => f.endsWith(suffix)) : [];
}

describe("services/_template", () => {
  it("the TypeScript template exposes the directories and scripts the kit expects", () => {
    for (const file of [
      "src/index.ts",
      "src/handler.ts",
      "src/adapter.ts",
      "src/mapping.ts",
      "src/log.ts",
      "src/config.ts",
      "tsconfig.json",
      "tsconfig.build.json",
      "vitest.config.ts",
      "Dockerfile",
      "README.md",
    ]) {
      expect(existsSync(join(TS, file)), file).toBe(true);
    }
    expect(testFiles(join(TS, "test", "unit"), ".test.ts").length).toBeGreaterThan(0);
    expect(testFiles(join(TS, "test", "acceptance"), ".test.ts").length).toBeGreaterThan(0);

    const pkg = JSON.parse(read(join(TS, "package.json"))) as {
      name: string;
      type: string;
      scripts: Record<string, string>;
    };
    expect(pkg.type).toBe("module");
    expect(Object.keys(pkg.scripts)).toEqual(
      expect.arrayContaining(["build", "lint", "typecheck", "test", "test:acceptance"]),
    );

    const tsconfig = JSON.parse(read(join(TS, "tsconfig.json"))) as { extends: string };
    expect(tsconfig.extends).toBe("../../tsconfig.base.json");
    const base = JSON.parse(read(join(ROOT, "tsconfig.base.json"))) as {
      compilerOptions: Record<string, unknown>;
    };
    expect(base.compilerOptions).toMatchObject({
      strict: true,
      module: "NodeNext",
      verbatimModuleSyntax: true,
    });

    const log = read(join(TS, "src", "log.ts"));
    for (const field of ["job_id", "source_id", "route", "vendor"]) {
      expect(log).toContain(field);
    }
    expect(read(join(TS, "src", "adapter.ts"))).toContain("docs/patterns/ADAPTER-PATTERN.md");
    expect(read(join(TS, "Dockerfile"))).toMatch(/^FROM public\.ecr\.aws\/docker\/library\/node:/m);
  });

  it("the Python template exposes tests/unit, tests/acceptance and the dev group", () => {
    for (const file of [
      "pyproject.toml",
      "uv.lock",
      "src/service_template/__init__.py",
      "src/service_template/__main__.py",
      "src/service_template/log.py",
      "src/service_template/config.py",
      "src/service_template/handler.py",
      "Dockerfile",
      "README.md",
    ]) {
      expect(existsSync(join(PY, file)), file).toBe(true);
    }
    expect(testFiles(join(PY, "tests", "unit"), ".py").length).toBeGreaterThan(0);
    expect(testFiles(join(PY, "tests", "acceptance"), ".py").length).toBeGreaterThan(0);

    const pyproject = read(join(PY, "pyproject.toml"));
    expect(pyproject).toContain('name = "service-template"');
    expect(pyproject).toMatch(/requires-python = ">=3\.13,<3\.14"/);
    const dev = /\[dependency-groups\]\s*\ndev = \[([^\]]*)\]/.exec(pyproject)?.[1] ?? "";
    for (const tool of ["pytest", "ruff", "pyright"]) {
      expect(dev).toContain(`"${tool}==`);
    }
    expect(pyproject).toMatch(/typeCheckingMode = "strict"/);
    expect(pyproject).toMatch(/extend = "\.\.\/\.\.\/ruff\.toml"/);

    const log = read(join(PY, "src", "service_template", "log.py"));
    for (const field of ["job_id", "source_id", "route", "vendor"]) {
      expect(log).toContain(field);
    }
    expect(read(join(PY, "Dockerfile"))).toMatch(
      /^FROM public\.ecr\.aws\/docker\/library\/python:/m,
    );
  });
});
