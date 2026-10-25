// Shared by the suites: the golden corpus under fixtures/text/ is the record both languages pass.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import type { LANG_LABELS } from "contracts";

export const PACKAGE_DIR = fileURLToPath(new URL("../", import.meta.url));
export const REPO_DIR = fileURLToPath(new URL("../../../", import.meta.url));
export const FIXTURES_DIR = fileURLToPath(new URL("../../../fixtures/text/", import.meta.url));
export const GOLDEN_FILE = `${FIXTURES_DIR}golden.jsonl`;

export type Lang = (typeof LANG_LABELS)[number];
export type RowRef = number | string;

/** One line of golden.jsonl, as golden-case.ts declares it. */
export interface GoldenCase {
  readonly id: string;
  readonly category: string;
  readonly lang: Lang;
  readonly title: string | null;
  readonly text: string;
  readonly text_norm: string;
  readonly rows: readonly RowRef[];
  readonly anchor: boolean;
  readonly must_pass: boolean;
  readonly origin: "invented" | "public_domain";
  readonly source: string | null;
  readonly reviewed: boolean;
  readonly note: string | null;
}

export function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf8")) as unknown;
}

/** Every line of golden.jsonl, parsed; the schema test checks each one's shape. */
export function corpusLines(): unknown[] {
  return readFileSync(GOLDEN_FILE, "utf8")
    .split("\n")
    .filter((line) => line !== "")
    .map((line) => JSON.parse(line) as unknown);
}

export function corpus(): GoldenCase[] {
  return corpusLines() as GoldenCase[];
}

/** The fold mode a label selects: Sorani for ckb, Arabic (with the Sorani-token override) otherwise. */
export function modeOf(lang: Lang): "sorani" | "arabic" {
  return lang === "ckb" ? "sorani" : "arabic";
}

/** How many times `needle` (one code point) occurs in `s`. */
export function countOf(s: string, needle: string): number {
  let n = 0;
  for (const ch of s) if (ch === needle) n += 1;
  return n;
}
