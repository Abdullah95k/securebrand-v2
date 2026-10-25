// The brief's "Done when": the package README shows a service using it, with a runnable example
// (examples/normalize-fallback.ts) whose output is the one the README shows.
import { execFileSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { describe, expect, it } from "vitest";
import { PACKAGE_DIR } from "../helpers.ts";

const README = join(PACKAGE_DIR, "README.md");
const EXAMPLE = join(PACKAGE_DIR, "examples/normalize-fallback.ts");

function read(path: string): string {
  expect(existsSync(path), `${path} exists`).toBe(true);
  return readFileSync(path, "utf8");
}

/** The body of the first fenced block of the README whose info string is `lang`. */
function block(lang: string): string {
  const m = new RegExp("^```" + lang + "\\n([\\s\\S]*?)^```$", "m").exec(read(README));
  if (m?.[1] === undefined) throw new Error(`README.md has no \`\`\`${lang} block`);
  return m[1];
}

describe("README example (the brief's Done when)", () => {
  it("the README shows examples/normalize-fallback.ts as it is", () => {
    expect(block("ts")).toBe(read(EXAMPLE));
  });

  it("the README's example runs and prints what the README shows", () => {
    // A service imports "text"; here the specifier points at the package's source entry.
    const entry = pathToFileURL(join(PACKAGE_DIR, "src/index.ts")).href;
    const code = read(EXAMPLE).replaceAll('from "text"', `from "${entry}"`);
    expect(code).toContain(entry);
    const dir = mkdtempSync(join(tmpdir(), "text-readme-"));
    try {
      const file = join(dir, "example.ts");
      writeFileSync(file, code);
      const out = execFileSync(process.execPath, ["--disable-warning=ExperimentalWarning", file], {
        encoding: "utf8",
      });
      expect(out).toBe(block("text"));
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
