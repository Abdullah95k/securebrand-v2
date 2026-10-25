// The golden corpus (fixtures/text/golden.jsonl): every case byte for byte, its coverage of the fold
// table (E6) and of hand-written anchors (E2), the Sorani letters, and determinism across workers.
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { describe, expect, it } from "vitest";
import { fold, textNorm } from "../../src/index.ts";
import { corpus, countOf, GOLDEN_FILE, modeOf, PACKAGE_DIR, type RowRef } from "../helpers.ts";

const cases = corpus();
const byId = cases.map((c) => [c.id, c] as const);

// The five Sorani-only letters of lang-dialect-id 5.3 A rule 2: ڕ ڵ ۆ ێ ە.
const SORANI_LETTERS = ["\u{695}", "\u{6B5}", "\u{6C6}", "\u{6CE}", "\u{6D5}"];
// What rows 1 and 2 delete before tokens are found, and a URL as D3 reads it (approximately: this
// test only counts the Sorani letters a URL takes with it).
const DELETED = new Set(
  [
    [0x061c, 0x061c],
    [0x200b, 0x200f],
    [0x202a, 0x202e],
    [0x2060, 0x2064],
    [0x2066, 0x2069],
    [0xfeff, 0xfeff],
    [0x064b, 0x0652],
    [0x0670, 0x0670],
    [0x06d6, 0x06ed],
    [0x0640, 0x0640],
  ].flatMap(([first = 0, last = 0]) =>
    Array.from({ length: last - first + 1 }, (_, i) => first + i),
  ),
);
const URL_LIKE = /(?<![\p{L}\p{M}\p{N}])(?:https?:\/\/|www\.)\S*/giu;

const withoutDeleted = (s: string): string =>
  Array.from(s)
    .filter((ch) => !DELETED.has(ch.codePointAt(0) ?? 0))
    .join("");

const ROWS_1_TO_10 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const D1_TO_D7 = ["D1", "D2", "D3", "D4", "D5", "D6", "D7"];

function claims(mode: "arabic" | "sorani", row: RowRef, anchorsOnly = false): number {
  return cases.filter(
    (c) => modeOf(c.lang) === mode && c.rows.includes(row) && (!anchorsOnly || c.anchor),
  ).length;
}

describe("lang-dialect-id 13, criterion 1: every golden case", () => {
  it.each(byId)("%s reproduces its text_norm byte for byte", (_id, c) => {
    expect(textNorm(c.title, c.text, c.lang)).toBe(c.text_norm);
  });
});

describe("coverage of the fold table (E6) and the anchors (E2)", () => {
  it("rows 1 to 10 and D1 to D7 are each claimed by at least 5 cases in each fold mode, and D-S1 and D-S2 by at least 5 in Sorani mode", () => {
    const short: string[] = [];
    for (const mode of ["arabic", "sorani"] as const) {
      for (const row of [...ROWS_1_TO_10, ...D1_TO_D7]) {
        const n = claims(mode, row);
        if (n < 5) short.push(`${String(row)} in ${mode} mode: ${String(n)}`);
      }
    }
    for (const row of ["D-S1", "D-S2"]) {
      const n = claims("sorani", row);
      if (n < 5) short.push(`${row} in sorani mode: ${String(n)}`);
    }
    expect(short).toEqual([]);
  });

  it("every row 1 to 10 has at least 5 hand-written anchors in each fold mode", () => {
    const short: string[] = [];
    for (const mode of ["arabic", "sorani"] as const) {
      for (const row of ROWS_1_TO_10) {
        const n = claims(mode, row, true);
        if (n < 5) short.push(`row ${String(row)} in ${mode} mode: ${String(n)} anchors`);
      }
    }
    expect(short).toEqual([]);
    expect(cases.filter((c) => c.anchor).length).toBeGreaterThanOrEqual(100);
  });
});

describe("D9: folding again changes nothing", () => {
  it.each(byId)("%s: folding its text_norm again changes nothing", (_id, c) => {
    expect(fold(c.text_norm, c.lang)).toBe(c.text_norm);
  });
});

describe("the brief: Sorani-only letters survive", () => {
  it("every Sorani-only letter of an input survives the fold except where NFKC composes it, in both modes", () => {
    const lost: string[] = [];
    for (const c of cases) {
      const input = `${c.title ?? ""} ${c.text}`.normalize("NFKC").replace(URL_LIKE, " ");
      // Row 2's second NFKC composes what the deletions bring together (ە ـ U+0654 → ۀ), so the
      // letters the fold must keep are those left after it.
      const kept = withoutDeleted(input).normalize("NFKC");
      for (const letter of SORANI_LETTERS) {
        if (countOf(c.text_norm, letter) < countOf(kept, letter))
          lost.push(`${c.id} lost ${letter}`);
      }
    }
    expect(lost).toEqual([]);
  });

  it("a unicode_edge case records ە followed by U+0654 becoming ۀ (E6)", () => {
    const recorded = cases.filter(
      (c) =>
        c.category === "unicode_edge" &&
        withoutDeleted(c.text).includes("\u{6D5}\u{654}") &&
        c.text_norm.includes("\u{6C0}"),
    );
    expect(recorded.length).toBeGreaterThanOrEqual(1);
  });
});

describe("criterion 6: identical results in fresh workers", () => {
  it("folding the corpus in two fresh workers gives byte-identical output", () => {
    const entry = pathToFileURL(`${PACKAGE_DIR}src/index.ts`).href;
    const script = [
      `import { readFileSync } from "node:fs";`,
      `import { textNorm } from ${JSON.stringify(entry)};`,
      `const lines = readFileSync(${JSON.stringify(GOLDEN_FILE)}, "utf8").split("\\n").filter(Boolean);`,
      `process.stdout.write(lines.map((l) => { const c = JSON.parse(l); return textNorm(c.title, c.text, c.lang); }).join("\\n"));`,
    ].join("\n");
    const run = (): string =>
      execFileSync(
        process.execPath,
        ["--disable-warning=ExperimentalWarning", "--input-type=module", "--eval", script],
        { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 },
      );
    const first = run();
    const second = run();
    expect(second).toBe(first);
    expect(first).toBe(cases.map((c) => c.text_norm).join("\n"));
  });
});
