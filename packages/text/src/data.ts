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

export const FOLD_TABLE = json(0) as FoldTableFile;
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
