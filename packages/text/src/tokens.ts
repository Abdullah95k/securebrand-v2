// Tokens as the fold's token rules read them (D5, D7): a hashtag or mention (its sign, then kept
// characters and `_`), or a run of kept characters; `_` joins tokens only inside a hashtag or a
// mention. fold() finds its tokens with spans(); tokenize() reports them in text_norm, with offsets
// in code points, as keyword-matcher's offsets are (ADR-0031, CONVENTIONS L27).
import { codePoint, FOLD_TABLE } from "./data.ts";
import { isKept } from "./unicode.ts";

export interface Token {
  readonly text: string;
  /** Offsets in code points: [start, end). */
  readonly start: number;
  readonly end: number;
  readonly kind: "word" | "hashtag" | "mention";
}

export interface Span {
  readonly start: number;
  readonly end: number;
  readonly kind: Token["kind"];
}

/** ڕ ڵ ۆ ێ ە: a token holding one takes the Sorani fold in Arabic mode (lang-dialect-id 5.3 C). */
export const SORANI_ONLY_LETTERS: readonly string[] = FOLD_TABLE.sorani_only_letters.map((u) =>
  String.fromCodePoint(codePoint(u)),
);
const SORANI = new Set(FOLD_TABLE.sorani_only_letters.map(codePoint));

const [HASH, AT] = FOLD_TABLE.row10.tag_signs.map(codePoint);
const JOINER = codePoint(FOLD_TABLE.row10.tag_joiner);

export function codePoints(s: string): number[] {
  const out: number[] = [];
  for (const ch of s) out.push(ch.codePointAt(0) ?? 0);
  return out;
}

export function hasSoraniLetter(s: string): boolean {
  for (const ch of s) if (SORANI.has(ch.codePointAt(0) ?? 0)) return true;
  return false;
}

/** True when cps[start, end) holds a Sorani-only letter. */
export function holdsSoraniLetter(cps: readonly number[], start: number, end: number): boolean {
  for (let i = start; i < end; i += 1) if (SORANI.has(cps[i] ?? 0)) return true;
  return false;
}

/** The token spans of a text's code points, in order (D5, D7); whatever lies between separates. */
export function spans(cps: readonly number[]): Span[] {
  const out: Span[] = [];
  const n = cps.length;
  const joins = (i: number): boolean => isKept(cps[i] ?? -1) || cps[i] === JOINER;
  let i = 0;
  while (i < n) {
    const c = cps[i] ?? -1;
    if ((c === HASH || c === AT) && (i === 0 || !isKept(cps[i - 1] ?? -1)) && joins(i + 1)) {
      let j = i + 2;
      while (j < n && joins(j)) j += 1;
      out.push({ start: i, end: j, kind: c === HASH ? "hashtag" : "mention" });
      i = j;
    } else if (isKept(c)) {
      let j = i + 1;
      while (j < n && isKept(cps[j] ?? -1)) j += 1;
      out.push({ start: i, end: j, kind: "word" });
      i = j;
    } else {
      i += 1;
    }
  }
  return out;
}

/** The number of code points in s, a lone surrogate counting as one, as for...of and cpSlice count. */
export function cpLength(s: string): number {
  let n = 0;
  for (let i = 0; i < s.length; n += 1) i += (s.codePointAt(i) ?? 0) > 0xffff ? 2 : 1;
  return n;
}

/** s from code point `start` to code point `end` (exclusive), as String.prototype.slice by units. */
export function cpSlice(s: string, start: number, end?: number): string {
  return Array.from(s).slice(start, end).join("");
}

/** The tokens of a text_norm, with code-point offsets, as the fold found them. */
export function tokenize(textNorm: string): Token[] {
  const chars = Array.from(textNorm);
  const cps = chars.map((ch) => ch.codePointAt(0) ?? 0);
  return spans(cps).map(({ start, end, kind }) => ({
    text: chars.slice(start, end).join(""),
    start,
    end,
    kind,
  }));
}
