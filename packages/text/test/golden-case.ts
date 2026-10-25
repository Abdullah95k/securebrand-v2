// The shape of one golden.jsonl line, written once in Zod 4 and exported as JSON Schema draft
// 2020-12 to fixtures/text/golden.schema.json (pnpm --filter text export:schema), as ADR-0030 asks
// of every schema. corpus.test.ts checks both: every line against this schema, and the committed
// file against a fresh export.
import { LANG_LABELS } from "contracts";
import { z } from "zod";

export const CATEGORIES = [
  "iraqi_arabic",
  "msa",
  "sorani",
  "mixed",
  "english",
  "emoji",
  "urls",
  "hashtags",
  "digits",
  "unicode_edge",
  "fold_mode",
  "other",
  "und",
] as const;

/** The plan's count per category (docs/plans/F7.md, "Count per category"). */
export const PLANNED_COUNTS: Readonly<Record<(typeof CATEGORIES)[number], number>> = {
  iraqi_arabic: 100,
  msa: 60,
  sorani: 100,
  mixed: 60,
  english: 40,
  emoji: 30,
  urls: 30,
  hashtags: 30,
  digits: 30,
  unicode_edge: 30,
  fold_mode: 20,
  other: 12,
  und: 12,
};

/** The fold table's rows (1 to 11) and the plan's D-lines a case can claim. */
export const D_LINES = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D-S1", "D-S2"] as const;

export const GoldenCase = z
  .strictObject({
    id: z.string().regex(/^[a-z]+-[0-9]{4}$/),
    category: z.enum(CATEGORIES),
    lang: z.enum(LANG_LABELS),
    title: z.string().nullable(),
    text: z.string(),
    text_norm: z.string(),
    rows: z.array(z.union([z.int().min(1).max(11), z.enum(D_LINES)])).min(1),
    anchor: z.boolean(),
    must_pass: z.literal(true),
    origin: z.enum(["invented", "public_domain"]),
    source: z.string().min(1).nullable(),
    reviewed: z.boolean(),
    note: z.string().min(1).nullable(),
  })
  .meta({
    title: "fixtures/text/golden.jsonl line",
    description:
      "One case of F7's golden fold corpus: an input under a language label and its expected text_norm (docs/plans/F7.md).",
  });

export type GoldenCaseValue = z.infer<typeof GoldenCase>;

/** The JSON Schema export, as committed in fixtures/text/golden.schema.json. */
export function goldenSchemaJson(): string {
  return `${JSON.stringify(z.toJSONSchema(GoldenCase, { target: "draft-2020-12" }), null, 2)}\n`;
}
