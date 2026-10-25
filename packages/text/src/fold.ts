// The fold of lang-dialect-id 5.3 C, as docs/plans/F7.md's "Fold specification v1" defines it. Its
// rows run in order; the maps and ranges are data (data/fold-table.json, D10), and every
// Unicode-dependent step is Unicode 15.1's (unicode.ts). The Python twin (python/text_fold) follows
// the same specification and reproduces the same golden corpus.
import { LANG_LABELS } from "contracts";
import { codePoint, FOLD_TABLE, ranges, type Range } from "./data.ts";
import { TextError } from "./errors.ts";
import { codePoints, holdsSoraniLetter, spans } from "./tokens.ts";
import { caseFold, isKept, isMark, isWhiteSpace, nfkc } from "./unicode.ts";

export type LangLabel = (typeof LANG_LABELS)[number];

const LABELS: ReadonlySet<string> = new Set(LANG_LABELS);
const SORANI_LABELS: ReadonlySet<string> = new Set(FOLD_TABLE.sorani_labels);

const char = (u: string): string => String.fromCodePoint(codePoint(u));

function charClass(list: readonly Range[]): RegExp {
  const body = list.map(([a, b]) => `\\u{${a.toString(16)}}-\\u{${b.toString(16)}}`).join("");
  return new RegExp(`[${body}]`, "gu");
}

function codeMap(written: Readonly<Record<string, string>>): ReadonlyMap<number, number> {
  return new Map(Object.entries(written).map(([from, to]) => [codePoint(from), codePoint(to)]));
}

const ROW0_FROM = FOLD_TABLE.row0_sorani.sequence.map(char).join("");
const ROW0_TO = char(FOLD_TABLE.row0_sorani.becomes);
const ROW1_DELETED = charClass(ranges(FOLD_TABLE.row1_deleted));
const ROW2_DELETED = charClass(ranges(FOLD_TABLE.row2_deleted));
const ALEF_LETTERS: ReadonlySet<number> = new Set(FOLD_TABLE.row3_alef.letters.map(codePoint));
const ALEF = codePoint(FOLD_TABLE.row3_alef.becomes);
const MARKS_AFTER_ALEF = ranges(FOLD_TABLE.row3_alef.marks_deleted_after);
const ARABIC = codeMap(FOLD_TABLE.rows4to6.arabic);
const SORANI = codeMap(FOLD_TABLE.rows4to6.sorani);
const DIGITS = FOLD_TABLE.row8_digits.map(
  (d) => [codePoint(d.first), codePoint(d.last), codePoint(d.becomes_first)] as const,
);
// ASCII case only: after NFKC no other letter folds to one of the prefixes' letters (D3).
const URL_PREFIXES = new RegExp(
  FOLD_TABLE.row10.url_prefixes.map((p) => p.replace(/[.*+?^${}()|[\]\\/]/gu, "\\$&")).join("|"),
  "gi",
);

const within = (cp: number, list: readonly Range[]): boolean =>
  list.some(([first, last]) => cp >= first && cp <= last);

function digit(cp: number): number {
  for (const [first, last, to] of DIGITS) if (cp >= first && cp <= last) return to + (cp - first);
  return cp;
}

/** The code point that ends just before UTF-16 index i. */
function codePointBefore(s: string, i: number): number {
  const low = s.charCodeAt(i - 1);
  if (low >= 0xdc00 && low <= 0xdfff && i >= 2) {
    const high = s.charCodeAt(i - 2);
    if (high >= 0xd800 && high <= 0xdbff) return s.codePointAt(i - 2) ?? low;
  }
  return low;
}

/**
 * D3: a URL starts where no kept character precedes it, with http://, https:// or www., and runs
 * to the next White_Space; it is deleted whole. Read on the text after row 1.
 */
function deleteUrls(s: string): string {
  URL_PREFIXES.lastIndex = 0;
  let out = "";
  let copied = 0;
  for (let m = URL_PREFIXES.exec(s); m !== null; m = URL_PREFIXES.exec(s)) {
    const start = m.index;
    if (start > 0 && isKept(codePointBefore(s, start))) continue;
    let end = start;
    while (end < s.length) {
      const cp = s.codePointAt(end) ?? 0;
      if (isWhiteSpace(cp)) break;
      end += cp > 0xffff ? 2 : 1;
    }
    out += s.slice(copied, start);
    copied = end;
    URL_PREFIXES.lastIndex = end;
  }
  return copied === 0 ? s : out + s.slice(copied);
}

/** Rows 3 to 9 on one token, in the token's fold. */
function foldToken(cps: readonly number[], start: number, end: number, sorani: boolean): string {
  const letters = sorani ? SORANI : ARABIC;
  let out = "";
  let afterAlef = false;
  for (let i = start; i < end; i += 1) {
    let cp = cps[i] ?? 0;
    if (ALEF_LETTERS.has(cp)) cp = ALEF; // row 3
    cp = letters.get(cp) ?? cp; // rows 4 to 6
    cp = digit(cp); // row 8
    if (cp === ALEF) {
      afterAlef = true;
    } else if (afterAlef && isMark(cp)) {
      // Row 3, E1: a madda or hamza mark after ا would compose with it on a second fold.
      if (within(cp, MARKS_AFTER_ALEF)) continue;
    } else {
      afterAlef = false;
    }
    out += caseFold(cp); // row 9
  }
  return out;
}

/** Row 10 (D4 to D7): the tokens of the text after row 2, each folded, joined by single spaces. */
function foldTokens(s: string, soraniMode: boolean): string {
  const cps = codePoints(s);
  const parts: string[] = [];
  let previousEnd = -1;
  for (const span of spans(cps)) {
    const sorani = soraniMode || holdsSoraniLetter(cps, span.start, span.end);
    const folded = foldToken(cps, span.start, span.end, sorani);
    if (folded === "") continue;
    // A separator lay between this token and the last one; a tag may touch the token before it.
    if (previousEnd >= 0 && span.start > previousEnd) parts.push(" ");
    parts.push(folded);
    previousEnd = span.end;
  }
  return parts.join("");
}

/**
 * The fold of `text` under its language label: `ckb` takes the Sorani fold, every other label the
 * Arabic fold, except that a token holding a Sorani-only letter takes the Sorani fold. The label is
 * decided on the raw text first (lang-dialect-id 5.3 C), so it is required.
 */
export function fold(text: string, lang: LangLabel): string {
  if (typeof text !== "string")
    throw new TextError("not_string", "the text to fold is not a string");
  checkLang(lang);
  if (!text.isWellFormed()) throw new TextError("not_unicode", "the text holds a lone surrogate");
  const soraniMode = SORANI_LABELS.has(lang);
  let s = soraniMode ? text.replaceAll(ROW0_FROM, ROW0_TO) : text; // row 0 (D-S1)
  s = nfkc(s).replace(ROW1_DELETED, ""); // row 1 (and D1)
  s = deleteUrls(s); // D3
  s = nfkc(s.replace(ROW2_DELETED, "")); // row 2, then E1's second NFKC
  return nfkc(foldTokens(s, soraniMode)); // rows 3 to 10, then row 11 (E1)
}

/** The refusals of a language label: none (no_lang), or one outside contracts' LANG_LABELS. */
function checkLang(lang: LangLabel): void {
  if ((lang as unknown) === undefined || (lang as unknown) === null) {
    throw new TextError("no_lang", "fold needs the text's language label, decided on the raw text");
  }
  if (!LABELS.has(lang))
    throw new TextError("bad_lang", `${String(lang)} is not a LANG_LABELS label`);
}

/**
 * text_norm of a record: the folded title and text, the non-empty ones joined by one space. A
 * missing input is skipped; the label is checked even when both are missing.
 */
export function textNorm(
  title: string | null | undefined,
  text: string | null | undefined,
  lang: LangLabel,
): string {
  const present = [title, text].filter((s) => s !== null && s !== undefined);
  if (present.length === 0) checkLang(lang);
  return present
    .map((s) => fold(s, lang))
    .filter((folded) => folded !== "")
    .join(" ");
}
