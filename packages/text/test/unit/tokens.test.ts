// The tokenizer helpers: code-point offsets in text_norm (ADR-0031, CONVENTIONS L27), the token
// spans keyword-matcher's boundary rules start from, and the Sorani-only letters.
import { describe, expect, it } from "vitest";
import {
  cpLength,
  cpSlice,
  hasSoraniLetter,
  SORANI_ONLY_LETTERS,
  tokenize,
  type Token,
} from "../../src/index.ts";
import { corpus } from "../helpers.ts";

const word = (text: string, start: number, end: number): Token => ({
  text,
  start,
  end,
  kind: "word",
});

describe("the Sorani-only letters", () => {
  it("are ڕ ڵ ۆ ێ ە (lang-dialect-id 5.3 A rule 2)", () => {
    expect(SORANI_ONLY_LETTERS).toEqual(["\u{695}", "\u{6B5}", "\u{6C6}", "\u{6CE}", "\u{6D5}"]);
  });

  it("hasSoraniLetter finds one in a token", () => {
    expect(hasSoraniLetter("وڵاتێکی")).toBe(true);
    expect(hasSoraniLetter("جوانە")).toBe(true);
    expect(hasSoraniLetter("کوردستان")).toBe(false);
    expect(hasSoraniLetter("البصره")).toBe(false);
  });
});

describe("code points, not UTF-16 units", () => {
  it("cpLength and cpSlice count code points", () => {
    expect(cpLength("a😀b")).toBe(3);
    expect(cpLength("\u{20000}x")).toBe(2);
    expect(cpSlice("a😀b", 1, 2)).toBe("😀");
    expect(cpSlice("\u{20000}x", 1)).toBe("x");
    expect(cpSlice("زين العراق", 4)).toBe("العراق");
  });

  it("cpLength and cpSlice count a lone surrogate as one code point, as for...of does", () => {
    for (const s of ["a\uDC00b", "a\uD800b", "\uDC00\uD800", "x\uD83D"]) {
      expect(cpLength(s)).toBe([...s].length);
      expect(cpSlice(s, 0, cpLength(s))).toBe(s);
    }
  });
});

describe("tokenize", () => {
  it("reports code-point offsets in text_norm, emoji and astral letters included", () => {
    // keyword-matcher 6.2: "زين العراق" in "خدمه زين العراق ضعيفه اليوم" is at [5, 15).
    expect(tokenize("خدمه زين العراق ضعيفه اليوم")).toEqual([
      word("خدمه", 0, 4),
      word("زين", 5, 8),
      word("العراق", 9, 15),
      word("ضعيفه", 16, 21),
      word("اليوم", 22, 27),
    ]);
    expect(tokenize("😀 \u{20000}\u{20001} #a_b @x y")).toEqual([
      word("\u{20000}\u{20001}", 2, 4),
      { text: "#a_b", start: 5, end: 9, kind: "hashtag" },
      { text: "@x", start: 10, end: 12, kind: "mention" },
      word("y", 13, 14),
    ]);
    // Two hashtags may touch in text_norm (D5): `#a_#b` is two tokens.
    expect(tokenize("#a_#b")).toEqual([
      { text: "#a_", start: 0, end: 3, kind: "hashtag" },
      { text: "#b", start: 3, end: 5, kind: "hashtag" },
    ]);
  });

  it("token starts and ends match the spans keyword-matcher's boundaries need", () => {
    const bad: string[] = [];
    for (const c of corpus()) {
      const tokens = tokenize(c.text_norm);
      let at = 0;
      tokens.forEach((t, i) => {
        const gap = cpSlice(c.text_norm, at, t.start);
        // Nothing before the first token; between tokens one space, or nothing where a hashtag or
        // mention starts right where the one before it ends (D5).
        const ok = i === 0 ? gap === "" : gap === " " || (gap === "" && t.kind !== "word");
        if (!ok) bad.push(`${c.id}: gap ${JSON.stringify(gap)} before ${t.text}`);
        if (cpSlice(c.text_norm, t.start, t.end) !== t.text) bad.push(`${c.id}: span of ${t.text}`);
        at = t.end;
      });
      if (at !== cpLength(c.text_norm)) bad.push(`${c.id}: text after the last token`);
    }
    expect(bad).toEqual([]);
  });
});
