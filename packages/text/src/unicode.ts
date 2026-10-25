// Unicode 15.1.0 in both languages (D-2, D11): the classes, White_Space and full case folding come
// from data/unicode-15.1.json, generated from Python 3.13's unicodedata. NFKC is the runtime's,
// applied to the runs between the code points 15.1 leaves unassigned (contracts' registry, Q6):
// those pass through unchanged, as starters, and the normalisation of every assigned code point is
// stable across versions, so a runtime on a later Unicode gives 15.1's result.
import { FOLD_TABLE, ranges, UNASSIGNED_15_1, UNICODE_15_1, type Range } from "./data.ts";
import { TextError } from "./errors.ts";

/** Refuses a Unicode version below 15.1, which would fold 15.1's text differently. */
export function checkUnicodeVersion(version: string | undefined): void {
  const m = /^([0-9]+)\.([0-9]+)(\.[0-9]+)?$/u.exec(version ?? "");
  const [major, minor] = [Number(m?.[1] ?? 0), Number(m?.[2] ?? 0)];
  if (major < 15 || (major === 15 && minor < 1)) {
    throw new TextError("unicode_version", `Unicode ${version ?? "unknown"} is below 15.1`);
  }
}

checkUnicodeVersion(process.versions.unicode);

const LETTER = 1;
const MARK = 2;
const NUMBER = 4;
const WHITE_SPACE = 8;
const SPACE_INSTEAD = 16; // D4: a mark or symbol the token rules read as a space

// One byte of class bits per code point: 1.1 MB, and a lookup per code point on texts of megabytes.
const CLASSES = new Uint8Array(0x110000);

function mark(list: readonly Range[], bit: number): void {
  for (const [first, last] of list) {
    for (let cp = first; cp <= last; cp += 1) CLASSES[cp] = (CLASSES[cp] ?? 0) | bit;
  }
}

mark(UNICODE_15_1.letters, LETTER);
mark(UNICODE_15_1.marks, MARK);
mark(UNICODE_15_1.numbers, NUMBER);
mark(UNICODE_15_1.white_space, WHITE_SPACE);
mark(ranges(FOLD_TABLE.row10.space_instead), SPACE_INSTEAD);

const at = (cp: number): number => CLASSES[cp] ?? 0;

/** D4: a letter, mark or number of Unicode 15.1, other than the marks and symbols D4 reads as a space. */
export function isKept(cp: number): boolean {
  const c = at(cp);
  return (c & (LETTER | MARK | NUMBER)) !== 0 && (c & SPACE_INSTEAD) === 0;
}

/** A combining mark of Unicode 15.1 (general category M). */
export function isMark(cp: number): boolean {
  return (at(cp) & MARK) !== 0;
}

/** Unicode 15.1's White_Space property. */
export function isWhiteSpace(cp: number): boolean {
  return (at(cp) & WHITE_SPACE) !== 0;
}

const unassigned = UNASSIGNED_15_1.ranges
  .map(([first, last]) => `\\u{${first.toString(16)}}-\\u{${last.toString(16)}}`)
  .join("");
const HAS_UNASSIGNED = new RegExp(`[${unassigned}]`, "u");
const UNASSIGNED_RUNS = new RegExp(`([${unassigned}]+)`, "u");

/** NFKC of Unicode 15.1: the runtime's NFKC on each run between 15.1-unassigned code points. */
export function nfkc(s: string): string {
  if (!HAS_UNASSIGNED.test(s)) return s.normalize("NFKC");
  return s
    .split(UNASSIGNED_RUNS)
    .map((part, i) => (i % 2 === 0 ? part.normalize("NFKC") : part))
    .join("");
}

const CASE_FOLDING = new Map<number, string>(
  UNICODE_15_1.case_folding.map(([cp, folded]) => [cp, String.fromCodePoint(...folded)]),
);

/** Full case folding of Unicode 15.1, one code point at a time (Python's str.casefold). */
export function caseFold(cp: number): string {
  return CASE_FOLDING.get(cp) ?? String.fromCodePoint(cp);
}

if (UNICODE_15_1.unicode !== "15.1.0" || FOLD_TABLE.unicode !== UNICODE_15_1.unicode) {
  throw new Error("data/unicode-15.1.json and data/fold-table.json must both be Unicode 15.1.0");
}
