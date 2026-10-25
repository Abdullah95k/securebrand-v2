// E1 and D9: folding twice equals folding once, over every single code point, every pair of D9's set
// and a seeded random set, each under ar and ckb (docs/plans/F7.md). The Python twin's
// test_idempotence.py runs the same sets.
import { describe, expect, it } from "vitest";
import { fold } from "../../src/index.ts";

const LANGS = ["ar", "ckb"] as const;

function range(first: number, last: number): number[] {
  return Array.from({ length: last - first + 1 }, (_, i) => first + i);
}

// Row 1's deleted format characters.
const FORMAT = [
  0x061c,
  ...range(0x200b, 0x200f),
  ...range(0x202a, 0x202e),
  ...range(0x2060, 0x2064),
  ...range(0x2066, 0x2069),
  0xfeff,
];
// D9's pair set: the Arabic block (which holds the Sorani letters), Latin, the combining marks and the
// format characters, each code point once (U+061C is in the Arabic block and in row 1's list).
const PAIR_SET = [
  ...new Set([
    ...range(0x0600, 0x06ff),
    ...range(0x0020, 0x007e),
    ...range(0x00a0, 0x017f),
    ...range(0x0300, 0x036f),
    ...FORMAT,
  ]),
].map((cp) => String.fromCodePoint(cp));

// The seeded random set: strings of 1 to 12 symbols, each a letter, mark, sign, URL prefix or emoji.
const SYMBOLS = [
  ..."اأإآٱبتةثجحخدذرزسشصضطظعغفقكکلمنهھوؤيىیئءڕڵۆێەچگپڤژ",
  "\u{653}",
  "\u{654}",
  "\u{655}",
  "\u{640}",
  "\u{64E}",
  "\u{651}",
  "\u{670}",
  "\u{6D6}",
  "\u{200C}",
  "\u{200D}",
  "\u{200F}",
  "\u{61C}",
  "\u{FEFF}",
  ..."aAbBsSkKiIßİıǰΣσς",
  "\u{301}",
  "\u{307}",
  "\u{308}",
  "\u{30C}",
  "\u{345}",
  ..."#@_ .،؛؟/:-«»",
  "\u{A0}",
  "\n",
  ..."٠١٢٣۴۵0129",
  "http://",
  "https://",
  "www.",
  "\u{1F600}",
  "\u{1F44D}",
  "\u{1f3fb}",
  "\u{FE0F}",
  "\u{20E3}",
  "\u{1f1ee}\u{1f1f6}",
  "\u{FB8E}",
  "\u{FBD9}",
  "\u{FEFB}",
  "\u{897}",
];
const RANDOM_STRINGS = 100_000;
const SEED = 20261025;

// mulberry32: a small seeded generator, so that every run draws the same strings.
function generator(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const hex = (s: string): string =>
  [...s]
    .map((ch) => `U+${(ch.codePointAt(0) ?? 0).toString(16).toUpperCase().padStart(4, "0")}`)
    .join(" ");

/** The inputs of `inputs` whose fold changes when folded again (at most 20, for the report). */
function unstable(inputs: Iterable<string>, lang: (typeof LANGS)[number]): string[] {
  const bad: string[] = [];
  for (const x of inputs) {
    const once = fold(x, lang);
    if (fold(once, lang) !== once) {
      bad.push(hex(x));
      if (bad.length >= 20) break;
    }
  }
  return bad;
}

function* singles(): Generator<string> {
  for (let cp = 0; cp <= 0x10ffff; cp += 1) {
    if (cp >= 0xd800 && cp <= 0xdfff) continue; // lone surrogates are refused (D8)
    yield String.fromCodePoint(cp);
  }
}

function* pairs(): Generator<string> {
  for (const a of PAIR_SET) for (const b of PAIR_SET) yield a + b;
}

function* randomStrings(): Generator<string> {
  const next = generator(SEED);
  for (let i = 0; i < RANDOM_STRINGS; i += 1) {
    const length = 1 + Math.floor(next() * 12);
    let s = "";
    for (let j = 0; j < length; j += 1) s += SYMBOLS[Math.floor(next() * SYMBOLS.length)] ?? "";
    yield s;
  }
}

describe("E1: folding twice changes nothing (D9)", () => {
  for (const lang of LANGS) {
    it(`over every single code point under ${lang}`, () => {
      expect(unstable(singles(), lang)).toEqual([]);
    });

    it(`over every pair of D9's set under ${lang}`, () => {
      expect(PAIR_SET.length).toBe(707); // 707 squared: 499,849 ordered pairs
      expect(unstable(pairs(), lang)).toEqual([]);
    });

    it(`over a seeded random set under ${lang}`, () => {
      expect(unstable(randomStrings(), lang)).toEqual([]);
    });
  }

  it("folds the critic's counterexamples to what a second fold keeps", () => {
    // ٱ ٔ: row 3 maps ٱ to ا and deletes the hamza after it, which NFKC would compose into أ.
    expect(fold("\u{671}\u{654}", "ar")).toBe("\u{627}");
    // ا ـ ٔ: row 2's second NFKC composes what the tatweel's deletion brings together.
    expect(fold("\u{627}\u{640}\u{654}", "ckb")).toBe("\u{627}");
    // ß ̇: case folding gives s s ̇, which row 11's NFKC composes into s ṡ.
    expect(fold("\u{DF}\u{307}", "en")).toBe("s\u{1E61}");
    // ڕ_ری: _ joins tokens only inside a hashtag or mention, so ری takes the Arabic fold.
    expect(fold("\u{695}_\u{631}\u{6CC}", "ar")).toBe("\u{695} \u{631}\u{64A}");
    // ە ـ ٔ ی under ar: row 2's second NFKC composes ۀ before the token's fold is chosen, so the token
    // holds no Sorani-only letter and its ی folds to ي (the plan's E1 note).
    expect(fold("\u{6D5}\u{640}\u{654}\u{6CC}", "ar")).toBe("\u{6C0}\u{64A}");
    for (const [x, lang] of [
      ["\u{671}\u{654}", "ar"],
      ["\u{627}\u{640}\u{654}", "ckb"],
      ["\u{DF}\u{307}", "en"],
      ["\u{695}_\u{631}\u{6CC}", "ar"],
      ["\u{6D5}\u{640}\u{654}\u{6CC}", "ar"],
    ] as const) {
      expect(fold(fold(x, lang), lang)).toBe(fold(x, lang));
    }
  });
});
