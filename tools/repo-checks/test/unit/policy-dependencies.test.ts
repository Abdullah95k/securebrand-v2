import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { script, TempRepo } from "../helpers/repo.js";

const REGISTER_HEAD = [
  "# Runtime dependencies",
  "",
  "| Name | Kind | Version | Licence | Owner or maintainer | Country | Used by | Added in session | Screen result |",
  "|---|---|---|---|---|---|---|---|---|",
  "| `pg` | npm | 8.23.1 | MIT | Brian Carlson | US | services/base | F1 | clear |",
  "",
].join("\n");

function row(name: string, kind: string): string {
  return `| \`${name}\` | ${kind} | 1.0.0 | MIT | Someone | US | services/x | T1 | clear |\n`;
}

describe("scripts/policy/check-dependencies.sh", () => {
  let repo: TempRepo;

  function check(): ReturnType<typeof script> {
    return script("policy/check-dependencies.sh", ["--base", "main"], { cwd: repo.dir });
  }

  function addRow(name: string, kind: string): void {
    repo.write("docs/dependencies.md", repo.read("docs/dependencies.md") + row(name, kind));
  }

  beforeEach(() => {
    repo = new TempRepo("policy-deps-");
    repo
      .write("docs/dependencies.md", REGISTER_HEAD)
      .writeJson("services/base/package.json", {
        name: "base",
        dependencies: { pg: "8.23.1" },
        devDependencies: { vitest: "4.1.11" },
      })
      // A dependency from before the register existed: it has no row, and it is not new.
      .writeJson("services/legacy/package.json", {
        name: "legacy",
        dependencies: { "legacy-lib": "2.0.0" },
      })
      .write(
        "services/py-base/pyproject.toml",
        '[project]\nname = "py-base"\nversion = "0.0.0"\ndependencies = []\n',
      )
      .write("compose.yaml", "services:\n  db:\n    image: ${DB_REPO}:${DB_TAG}\n")
      .write(
        "stack/versions.env",
        "DB_TAG=1.0\nDB_REPO=public.ecr.aws/example/db\nDB_UPSTREAM=docker.io/example/db\n",
      )
      .commit("base");
    repo.branch("sb/T1");
  });

  afterEach(() => {
    repo.cleanup();
  });

  it("fails for a new npm runtime dependency without a row", () => {
    repo.writeJson("services/x/package.json", { name: "x", dependencies: { "left-pad": "1.3.0" } });
    repo.commit();
    const result = check();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("left-pad");
    expect(result.output).toContain("services/x/package.json");
  });

  it("fails for a new Python dependency", () => {
    repo.write(
      "services/py-x/pyproject.toml",
      '[project]\nname = "py-x"\nversion = "0.0.0"\ndependencies = ["trafilatura==2.0.0", "httpx[http2]>=0.28"]\n',
    );
    repo.commit();
    const result = check();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("trafilatura");
    expect(result.output).toContain("httpx");
  });

  it("fails for a new container image", () => {
    repo.write("services/x/Dockerfile", 'FROM ghcr.io/example/runtime:2.1 AS run\nCMD ["run"]\n');
    repo.commit();
    const result = check();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("ghcr.io/example/runtime");
  });

  it("fails for a new image in stack/versions.env, upstream included", () => {
    repo.write(
      "stack/versions.env",
      `${repo.read("stack/versions.env")}CACHE_TAG=7.0\nCACHE_REPO=ghcr.io/example/cache\nCACHE_UPSTREAM=docker.io/example/cache\n`,
    );
    repo.commit();
    const result = check();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("ghcr.io/example/cache");
    expect(result.output).toContain("docker.io/example/cache");
  });

  it("reads image names behind Dockerfile build arguments", () => {
    repo.write(
      "services/x/Dockerfile",
      "ARG BASE_IMAGE=public.ecr.aws/example/base:3.0\nFROM ${BASE_IMAGE}\n",
    );
    repo.commit();
    const result = check();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("public.ecr.aws/example/base");
  });

  it("ignores devDependencies and dependency groups", () => {
    repo.writeJson("services/base/package.json", {
      name: "base",
      dependencies: { pg: "8.23.1" },
      devDependencies: { vitest: "4.1.11", "left-pad": "1.3.0" },
    });
    repo.write(
      "services/py-base/pyproject.toml",
      '[project]\nname = "py-base"\nversion = "0.0.0"\ndependencies = []\n\n[dependency-groups]\ndev = ["pytest==9.1.1"]\n',
    );
    repo.commit();
    const result = check();
    expect(result.code, result.output).toBe(0);
  });

  it("ignores workspace and path dependencies", () => {
    repo.writeJson("services/x/package.json", {
      name: "x",
      dependencies: { base: "workspace:*", "listening-sdk": "workspace:^" },
    });
    repo.write(
      "services/py-x/pyproject.toml",
      [
        "[project]",
        'name = "py-x"',
        'version = "0.0.0"',
        'dependencies = ["listening-sdk"]',
        "",
        "[tool.uv.sources]",
        'listening-sdk = { path = "../../py/listening_sdk", editable = true }',
        "",
      ].join("\n"),
    );
    repo.commit();
    const result = check();
    expect(result.code, result.output).toBe(0);
  });

  it("passes when every new dependency has its row", () => {
    repo.writeJson("services/x/package.json", { name: "x", dependencies: { "left-pad": "1.3.0" } });
    repo.write(
      "services/py-x/pyproject.toml",
      '[project]\nname = "py-x"\nversion = "0.0.0"\ndependencies = ["Trafilatura_Lib>=2"]\n',
    );
    repo.write("services/x/Dockerfile", "FROM ghcr.io/example/runtime:2.1\n");
    addRow("left-pad", "npm");
    addRow("trafilatura-lib", "PyPI");
    addRow("ghcr.io/example/runtime", "image");
    repo.commit();
    const result = check();
    expect(result.code, result.output).toBe(0);
  });

  it("a removed dependency never fails the check", () => {
    repo.writeJson("services/base/package.json", { name: "base", dependencies: {} });
    repo.write("compose.yaml", "services: {}\n");
    repo.commit();
    const result = check();
    expect(result.code, result.output).toBe(0);
  });

  it("a renamed one is a new dependency", () => {
    repo.writeJson("services/base/package.json", {
      name: "base",
      dependencies: { "pg-native": "3.0.0" },
    });
    repo.commit();
    const result = check();
    expect(result.code).not.toBe(0);
    expect(result.output).toContain("pg-native");
  });

  it("a dependency already used elsewhere in the repository is not new", () => {
    repo.writeJson("services/y/package.json", {
      name: "y",
      dependencies: { "legacy-lib": "2.0.0" },
    });
    repo.commit();
    const result = check();
    expect(result.code, result.output).toBe(0);
  });
});
