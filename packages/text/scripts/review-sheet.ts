// Writes fixtures/text/review/golden-review.csv, the reader's sheet, from golden.jsonl, so the two
// never drift (docs/plans/F7.md, "The reader"). One row per case holding Arabic script; the reader
// fills in the last three columns. Invisible characters are shown as ⟨U+XXXX NAME⟩ markers.
//
//   pnpm --filter text review-sheet
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";

interface SheetCase {
  readonly id: string;
  readonly category: string;
  readonly lang: string;
  readonly title: string | null;
  readonly text: string;
  readonly text_norm: string;
  readonly rows: readonly (number | string)[];
  readonly note: string | null;
}

const FIXTURES = fileURLToPath(new URL("../../../fixtures/text/", import.meta.url));
export const SHEET_FILE = `${FIXTURES}review/golden-review.csv`;

const HEADER = [
  "id",
  "category",
  "lang",
  "input",
  "expected text_norm",
  "what the fold changed",
  "verdict (ok, expected wrong, unnatural, remove)",
  "corrected text_norm",
  "comment",
];

// The invisible characters a reader cannot see, by name.
const INVISIBLE: Readonly<Record<number, string>> = {
  0x0009: "TAB",
  0x000a: "LINE BREAK",
  0x00a0: "NO-BREAK SPACE",
  0x061c: "ARABIC LETTER MARK",
  0x200b: "ZERO WIDTH SPACE",
  0x200c: "ZWNJ",
  0x200d: "ZWJ",
  0x200e: "LEFT-TO-RIGHT MARK",
  0x200f: "RIGHT-TO-LEFT MARK",
  0x202b: "RIGHT-TO-LEFT EMBEDDING",
  0x202c: "POP DIRECTIONAL FORMATTING",
  0x2060: "WORD JOINER",
  0x2062: "INVISIBLE TIMES",
  0x2066: "LEFT-TO-RIGHT ISOLATE",
  0x2069: "POP DIRECTIONAL ISOLATE",
  0x3000: "IDEOGRAPHIC SPACE",
  0xfe0e: "TEXT STYLE",
  0xfe0f: "EMOJI STYLE",
  0xfeff: "BOM",
};

function visible(s: string): string {
  let out = "";
  for (const ch of s) {
    const cp = ch.codePointAt(0) ?? 0;
    const name = INVISIBLE[cp];
    const hex = cp.toString(16).toUpperCase().padStart(4, "0");
    if (name !== undefined) out += `⟨U+${hex} ${name}⟩`;
    else if (/[\p{Cc}\p{Cf}\p{Co}\p{Cn}]/u.test(ch)) out += `⟨U+${hex}⟩`;
    else if (/^\p{M}$/u.test(ch) && (cp < 0x064b || cp > 0x0652)) out += `⟨U+${hex}⟩`;
    else out += ch;
  }
  return out;
}

/** The plain-English gloss of a row, under the case's fold mode. */
function gloss(row: number | string, sorani: boolean): string {
  switch (row) {
    case 1:
      return "invisible marks deleted, presentation forms and ligatures made plain (row 1)";
    case 2:
      return "harakat and tatweel deleted (row 2)";
    case 3:
      return "أ إ آ ٱ → ا (row 3)";
    case 4:
      return sorani ? "ة → ە, ھ → ه (row 4)" : "ة → ه (row 4)";
    case 5:
      return sorani ? "ك → ک (row 5)" : "ک → ك (row 5)";
    case 6:
      return sorani ? "ي ى → ی (row 6)" : "ى ی → ي (row 6)";
    case 7:
      return sorani ? "ڕ ڵ ۆ ێ ە چ گ پ ڤ ژ ئ kept (row 7)" : "چ گ پ ڤ ژ ؤ ئ ء kept (row 7)";
    case 8:
      return "Arabic-Indic and Persian digits → 0-9 (row 8)";
    case 9:
      return "Latin letters case-folded (row 9)";
    case 10:
      return "punctuation, emoji and URLs become spaces (row 10)";
    case "D1":
      return "Arabic letter mark or word joiner deleted (D1)";
    case "D2":
      return "a hamza or madda mark: composed where NFKC composes it, else kept (D2)";
    case "D3":
      return "a URL deleted, or a bare domain split at its dots (D3)";
    case "D4":
      return "emoji and symbols become spaces (D4)";
    case "D5":
      return "the hashtag and mention rule: # @ _ kept only inside them (D5)";
    case "D6":
      return "line breaks and extra spaces collapsed (D6)";
    case "D7":
      return sorani
        ? "_ outside a hashtag splits words (D7)"
        : "a word holding ڕ ڵ ۆ ێ ە takes the Sorani fold (D7)";
    case "D8":
      return "nothing is left to match (D8)";
    case "D-S1":
      return "legacy ه + ZWNJ → ە (D-S1)";
    case "D-S2":
      return "ھ → ه (D-S2)";
    default:
      return `row ${String(row)}`;
  }
}

function field(s: string): string {
  return /[",\n\r]/u.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
}

const ARABIC_SCRIPT =
  /[\u{600}-\u{6FF}\u{750}-\u{77F}\u{8A0}-\u{8FF}\u{FB50}-\u{FDFF}\u{FE70}-\u{FEFF}]/u;

/**
 * The sheet's text: a UTF-8 byte order mark (so that spreadsheet programs read it as UTF-8), then
 * the rows, each ending in LF, as the repository stores every text file (.gitattributes).
 */
export function sheet(goldenJsonl: string): string {
  const lines = [HEADER.map(field).join(",")];
  for (const line of goldenJsonl.split("\n")) {
    if (line === "") continue;
    const c = JSON.parse(line) as SheetCase;
    const input = c.title === null ? c.text : `${c.title} ‖ ${c.text}`;
    if (!ARABIC_SCRIPT.test(input)) continue;
    const sorani = c.lang === "ckb";
    const what = [...c.rows.map((row) => gloss(row, sorani)), ...(c.note === null ? [] : [c.note])];
    const cells = [
      c.id,
      c.category,
      c.lang,
      visible(input),
      c.text_norm,
      what.join("; "),
      "",
      "",
      "",
    ];
    lines.push(cells.map(field).join(","));
  }
  return `\u{FEFF}${lines.join("\n")}\n`;
}

if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href) {
  writeFileSync(SHEET_FILE, sheet(readFileSync(`${FIXTURES}golden.jsonl`, "utf8")));
  console.log(`wrote ${SHEET_FILE}`);
}
