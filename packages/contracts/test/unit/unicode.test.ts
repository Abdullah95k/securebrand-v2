import { describe, expect, it } from "vitest";
import { checkUnicodeVersion, lowerCase, nfc } from "../../src/keys/text.ts";
import { loadRegistry } from "../../src/registries/load.ts";

// D-2: NFC and lower case are those of Unicode 15.1.0. The helpers keep the code points 15.1 leaves
// unassigned, and rely on a later runtime giving 15.1's result for the runs between them.
const registry = loadRegistry("unicode-15.1-unassigned.json") as {
  unicode_version: string;
  ranges: [number, number][];
};
const listed = new Set<number>();
for (const [first, last] of registry.ranges)
  for (let cp = first; cp <= last; cp += 1) listed.add(cp);

const hex = (cp: number): string => `U+${cp.toString(16).toUpperCase().padStart(4, "0")}`;
const holdsListed = (s: string): boolean => [...s].some((ch) => listed.has(ch.codePointAt(0) ?? 0));

function* scalarValues(): Generator<number> {
  for (let cp = 0; cp < 0x110000; cp += 1) if (cp < 0xd800 || cp > 0xdfff) yield cp;
}

describe("the code points Unicode 15.1 leaves unassigned (D-2)", () => {
  it("lists the ranges of Unicode 15.1.0, surrogates excluded", () => {
    expect(registry.unicode_version).toBe("15.1.0");
    expect(registry.ranges).toHaveLength(707);
    expect([...listed].some((cp) => cp >= 0xd800 && cp <= 0xdfff)).toBe(false);
  });

  it("holds every code point the runtime leaves unassigned", () => {
    const missing: string[] = [];
    for (const cp of scalarValues()) {
      if (/\p{Cn}/u.test(String.fromCodePoint(cp)) && !listed.has(cp)) missing.push(hex(cp));
    }
    expect(missing).toEqual([]);
  });

  it("a code point Unicode 15.1 assigns never decomposes, composes or lower-cases into a listed one", () => {
    const bad: string[] = [];
    for (const cp of scalarValues()) {
      const c = String.fromCodePoint(cp);
      if (!listed.has(cp)) {
        if (holdsListed(c.normalize("NFD") + c.normalize("NFC") + c.toLowerCase()))
          bad.push(hex(cp));
        continue;
      }
      // A later composite whose parts 15.1 assigns would let NFC of 15.1 text yield it.
      const parts = c.normalize("NFD");
      if (parts !== c && !holdsListed(parts) && holdsListed(parts.normalize("NFC")))
        bad.push(hex(cp));
    }
    expect(bad).toEqual([]);
  });

  it("passes a listed code point through NFC and lower case unchanged", () => {
    // ARABIC PEPET (Unicode 16.0) between a kasra and its letter: no reordering across it.
    expect(nfc("\u0628\u0897\u0650\u0631")).toBe("\u0628\u0897\u0650\u0631");
    // TODHRI LETTER I and a combining dot above, which Unicode 16.0 composes into TODHRI LETTER EI.
    expect(nfc("\u{105D2}\u0307")).toBe("\u{105D2}\u0307");
    // LATIN CAPITAL LETTER RAMS HORN (Unicode 16.0) keeps its case.
    expect(lowerCase("\uA7CB")).toBe("\uA7CB");
  });

  it("normalises and lower-cases the text either side of a listed code point as Unicode 15.1 does", () => {
    expect(nfc("e\u0301\u{1FAE9}e\u0301")).toBe("\u00E9\u{1FAE9}\u00E9");
    expect(nfc("\u0627\u0654\u0897\u0627\u0654")).toBe("\u0623\u0897\u0623");
    expect(lowerCase("ABC\uA7CBDEF")).toBe("abc\uA7CBdef");
    // A listed code point is neither cased nor case-ignorable in 15.1: a sigma before it is final.
    expect(lowerCase("A\u03A3\uA7CB")).toBe("a\u03C2\uA7CB");
    expect(lowerCase("A\uA7CB\u03A3")).toBe("a\uA7CB\u03C3");
  });
});

describe("the runtime's Unicode version (D-2)", () => {
  it("refuses a Unicode version below 15.1", () => {
    for (const version of ["15.0", "15.0.0", "14.0", "9.0", "", "unicode", undefined]) {
      expect(() => checkUnicodeVersion(version), String(version)).toThrow(/unicode_version/);
    }
  });

  it("accepts Unicode 15.1 and later, and the runtime's own version", () => {
    for (const version of ["15.1", "15.1.0", "16.0", "17.0", "17.0.0", process.versions.unicode]) {
      expect(() => checkUnicodeVersion(version), String(version)).not.toThrow();
    }
  });
});
