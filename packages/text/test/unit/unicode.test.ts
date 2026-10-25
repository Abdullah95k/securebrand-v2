// Unicode 15.1 pinned (D-2, D11, Q6, E7): the version check, code points 15.1 leaves unassigned,
// contracts' ranges, and the committed 15.1 data against a fresh generation.
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { fold, TextError } from "../../src/index.ts";
import { checkUnicodeVersion } from "../../src/unicode.ts";
import { PACKAGE_DIR, readJson, REPO_DIR } from "../helpers.ts";

const REGISTRY = `${REPO_DIR}packages/contracts/registries/unicode-15.1-unassigned.json`;

function textError(f: () => unknown): TextError {
  try {
    f();
  } catch (e) {
    if (e instanceof TextError) return e;
    throw e;
  }
  throw new Error("no TextError was thrown");
}

/** uv's Python 3.13, found without downloading anything (E7); undefined when none is installed. */
function python313(): string | undefined {
  try {
    const found = execFileSync("uv", ["python", "find", "3.13"], {
      cwd: PACKAGE_DIR,
      encoding: "utf8",
      env: { ...process.env, UV_PYTHON_DOWNLOADS: "never" },
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    return found === "" ? undefined : found;
  } catch {
    return undefined;
  }
}

describe("Unicode 15.1 pinned (D-2)", () => {
  it("refuses to import below Unicode 15.1", () => {
    for (const version of ["15.0", "14.0", "9.0", "1.0", "", "x", undefined]) {
      expect(textError(() => checkUnicodeVersion(version)).code).toBe("unicode_version");
    }
    for (const version of ["15.1", "15.1.0", "16.0", "17.0"]) {
      expect(() => checkUnicodeVersion(version)).not.toThrow();
    }
    // The runtime itself passed the check at import, or no test could have run.
    expect(() => checkUnicodeVersion(process.versions.unicode)).not.toThrow();
  });

  it("a code point unassigned in 15.1 and assigned by 17.0 folds as 15.1 says", () => {
    // U+0897 ARABIC PEPET and U+A7CB LATIN CAPITAL LETTER RAMS HORN are Unicode 16.0 characters.
    expect(/\p{Mn}/u.test("\u{897}")).toBe(true);
    expect(/\p{Lu}/u.test("\u{A7CB}")).toBe(true);
    // Under 15.1 they are unassigned: not kept, so a space.
    expect(fold("ب\u{897}ت", "ar")).toBe("ب ت");
    expect(fold("a\u{A7CB}b", "en")).toBe("a b");
    // And a starter for NFKC, so the marks after it stay after it: ا, then U+0655 alone. Runtime
    // NFKC on the whole text would move U+0655 before U+0897 and compose إ, which folds to ا.
    expect(fold("ا\u{897}\u{655}", "ar")).toBe("ا \u{655}");
    expect(fold("a\u{897}\u{316}", "en")).toBe("a \u{316}");
  });

  it("reads the unassigned ranges from contracts' unicode-15.1-unassigned.json, so every code point it lists becomes a space", () => {
    const registry = readJson(REGISTRY) as { ranges: [number, number][] };
    expect(registry.ranges.length).toBeGreaterThan(0);
    const bad: string[] = [];
    for (const [first, last] of registry.ranges) {
      for (const cp of new Set([first, Math.floor((first + last) / 2), last])) {
        if (fold(`a${String.fromCodePoint(cp)}b`, "en") !== "a b") bad.push(cp.toString(16));
      }
    }
    expect(bad).toEqual([]);
  });

  it("the committed 15.1 data equals what gen_unicode_data.py writes", (ctx) => {
    const python = python313();
    if (python === undefined) {
      ctx.skip("no Python 3.13 installed (uv python find 3.13 found none; CI has one)");
      return;
    }
    const generated = execFileSync(
      python,
      ["-I", `${PACKAGE_DIR}scripts/gen_unicode_data.py`, "--stdout"],
      {
        encoding: "utf8",
        maxBuffer: 64 * 1024 * 1024,
      },
    );
    expect(generated).toBe(readFileSync(`${PACKAGE_DIR}data/unicode-15.1.json`, "utf8"));
  });
});
