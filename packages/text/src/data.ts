// The fold's data, read once at import: the fold table (D10), F7's Unicode 15.1 data (D11) and
// contracts' code points that 15.1 leaves unassigned (Q6). The Python twin reads the same files.
// Each is found beside the package's source or compiled entry, or through contracts' resolution.
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

export type Range = readonly [number, number];

interface FoldTableFile {
  readonly version: string;
  readonly unicode: string;
  readonly sorani_labels: readonly string[];
  readonly sorani_only_letters: readonly string[];
  readonly row0_sorani: { readonly sequence: readonly string[]; readonly becomes: string };
  readonly row1_deleted: readonly (readonly [string, string])[];
  readonly row2_deleted: readonly (readonly [string, string])[];
  readonly row3_alef: {
    readonly letters: readonly string[];
    readonly becomes: string;
    readonly marks_deleted_after: readonly (readonly [string, string])[];
  };
  readonly rows4to6: {
    readonly arabic: Readonly<Record<string, string>>;
    readonly sorani: Readonly<Record<string, string>>;
  };
  readonly row8_digits: readonly {
    readonly first: string;
    readonly last: string;
    readonly becomes_first: string;
  }[];
  readonly row10: {
    readonly url_prefixes: readonly string[];
    readonly tag_signs: readonly string[];
    readonly tag_joiner: string;
    readonly space_instead: readonly (readonly [string, string])[];
  };
}

interface UnicodeFile {
  readonly unicode: string;
  readonly letters: readonly Range[];
  readonly marks: readonly Range[];
  readonly numbers: readonly Range[];
  readonly white_space: readonly Range[];
  readonly case_folding: readonly (readonly [number, readonly number[]])[];
}

interface UnassignedFile {
  readonly ranges: readonly Range[];
}

/** The data files, by the names FOLD_DATA_SHA256 hashes them under (D10). */
export const DATA_FILES: readonly (readonly [string, URL])[] = [
  ["fold-table.json", new URL("../data/fold-table.json", import.meta.url)],
  ["unicode-15.1.json", new URL("../data/unicode-15.1.json", import.meta.url)],
  [
    "unicode-15.1-unassigned.json",
    // The registry ships in contracts' files, in registries/ beside its compiled dist/index.js.
    new URL(
      "../registries/unicode-15.1-unassigned.json",
      pathToFileURL(createRequire(import.meta.url).resolve("contracts")),
    ),
  ],
];

const bytes = DATA_FILES.map(([, url]) => readFileSync(url));
export const DATA_BYTES: readonly Buffer[] = bytes;

function json(i: number): unknown {
  return JSON.parse((bytes[i] ?? Buffer.alloc(0)).toString("utf8")) as unknown;
}

// The keys of each object in fold-table.json. As the twin's parser does, the fold refuses a key it
// does not know and a key it needs and does not find, so that a row added to or renamed in the table
// cannot leave the fold silently folding by the old rules.
const TOP_KEYS = [
  "version",
  "unicode",
  "specification",
  "sorani_labels",
  "sorani_only_letters",
  "row0_sorani",
  "row1_deleted",
  "row2_deleted",
  "row3_alef",
  "rows4to6",
  "row8_digits",
  "row10",
];
const ROW_KEYS: Readonly<Record<string, readonly string[]>> = {
  row0_sorani: ["sequence", "becomes"],
  row3_alef: ["letters", "becomes", "marks_deleted_after"],
  rows4to6: ["arabic", "sorani"],
  row10: ["url_prefixes", "tag_signs", "tag_joiner", "space_instead"],
};
const DIGIT_KEYS = ["first", "last", "becomes_first"];

function object(value: unknown, where: string, keys: readonly string[]): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`fold-table.json: ${where} is not an object`);
  }
  const found = Object.keys(value).sort();
  const wanted = [...keys].sort();
  if (found.join() !== wanted.join()) {
    throw new Error(
      `fold-table.json: ${where} has the keys ${found.join(", ")}, not ${wanted.join(", ")}`,
    );
  }
  return value as Record<string, unknown>;
}

/** The fold table, refused unless each of its objects has exactly the keys the fold reads. */
export function checkFoldTable(raw: unknown): FoldTableFile {
  const top = object(raw, "the table", TOP_KEYS);
  for (const [row, keys] of Object.entries(ROW_KEYS)) object(top[row], row, keys);
  const digits: unknown = top.row8_digits;
  if (!Array.isArray(digits)) throw new Error("fold-table.json: row8_digits is not a list");
  digits.forEach((d: unknown, i) => object(d, `row8_digits[${String(i)}]`, DIGIT_KEYS));
  return raw as FoldTableFile;
}

export const FOLD_TABLE = checkFoldTable(json(0));
export const UNICODE_15_1 = json(1) as UnicodeFile;
export const UNASSIGNED_15_1 = json(2) as UnassignedFile;

/** A code point written "U+XXXX", as the fold table writes them. */
export function codePoint(written: string): number {
  const m = /^U\+([0-9A-F]{4,6})$/u.exec(written);
  if (m?.[1] === undefined)
    throw new Error(`fold-table.json: ${written} is not a U+XXXX code point`);
  return Number.parseInt(m[1], 16);
}

export function ranges(written: readonly (readonly [string, string])[]): Range[] {
  return written.map(([first, last]) => [codePoint(first), codePoint(last)] as const);
}
