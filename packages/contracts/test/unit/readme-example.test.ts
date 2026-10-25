// A34: the package README's TypeScript example runs as written, against the package's source entry
// point, and prints the output the README shows (the Python twin runs the Python example).
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { describe, expect, it } from "vitest";
import { PACKAGE_DIR } from "../helpers.ts";

const readme = readFileSync(join(PACKAGE_DIR, "README.md"), "utf8");

/** The body of the first fenced block whose info string is `lang`. */
function block(lang: string): string {
  const m = new RegExp("^```" + lang + "\\n([\\s\\S]*?)^```$", "m").exec(readme);
  if (m?.[1] === undefined) throw new Error(`README.md has no \`\`\`${lang} block`);
  return m[1];
}

describe("README example (A34)", () => {
  it("the README's TypeScript example runs", () => {
    const entry = pathToFileURL(join(PACKAGE_DIR, "src/index.ts")).href;
    // A service imports "contracts"; here the specifier points at the package's source.
    const code = block("ts").replaceAll('from "contracts"', `from "${entry}"`);
    expect(code).toContain(entry);
    const dir = mkdtempSync(join(tmpdir(), "contracts-readme-"));
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
