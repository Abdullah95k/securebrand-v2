// A33: the package is v1.0.0 in both languages, and the two versions are equal.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { PACKAGE_DIR } from "../helpers.ts";

describe("package version (A33)", () => {
  it("package.json and pyproject.toml both declare 1.0.0", () => {
    const manifest = JSON.parse(readFileSync(join(PACKAGE_DIR, "package.json"), "utf8")) as {
      version: string;
    };
    const project = readFileSync(join(PACKAGE_DIR, "pyproject.toml"), "utf8");
    // The [project] table's version: the first `version = "..."` line after the table header.
    const python = /^\[project\]$[\s\S]*?^version = "([^"]+)"$/m.exec(project)?.[1];
    expect(manifest.version).toBe("1.0.0");
    expect(python).toBe("1.0.0");
  });
});
