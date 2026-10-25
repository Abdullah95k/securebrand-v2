// item.hits/v1: keyword-matcher's message, one per (item, client, keyword), whoever the poster is
// (keyword-matcher §6.2; ADR-0031, ADR-0070). Discriminated on `matched_by` (F-20): a text match
// carries where it matched; an item of a watched source whose text does not match carries none.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { dataShape, metadataShape } from "./metadata.ts";
import {
  PATTERNS,
  authorRef,
  count,
  httpUrl,
  nonEmpty,
  rawRef,
  timestamp,
  token,
  uuid,
} from "./primitives.ts";
import { AUTHOR_TYPES, CONTENT_KINDS, HIT_STATUSES, PLATFORMS } from "./vocabulary.ts";

export const ITEM_HITS = "item.hits/v1";

/** The poster of the item behind a hit: a keyed reference, never a handle (ADR-0010, ADR-0031). */
export const hitPoster = (b: SchemaBuilder) =>
  b.def("HitPoster", () =>
    b.obj({
      author_ref: authorRef().nullable(),
      author_type: z.enum(AUTHOR_TYPES),
      author_source_id: uuid().nullable(),
    }),
  );

/** A [start, end) pair of code-point offsets in `text_norm`. */
const offsetPair = () => z.array(count()).length(2);

const shape = (b: SchemaBuilder) => ({
  ...metadataShape(b, ITEM_HITS),
  hit_id: uuid(),
  status: z.enum(HIT_STATUSES),
  item_id: uuid(),
  item_version: count().min(1),
  platform: z.enum(PLATFORMS),
  kind: z.enum(CONTENT_KINDS),
  source_id: uuid(),
  client_id: uuid(),
  keyword_id: uuid(),
  keyword_set_version: z.string().regex(PATTERNS.keywordSetVersion),
  lang_model_version: token().nullable(),
  hit_at: timestamp(),
  url: httpUrl().nullable(),
  poster: hitPoster(b),
  video_channel_id: token().optional(),
  raw_ref: rawRef(),
  expires_at: timestamp().nullable(),
  ...dataShape(b),
});

export function buildItemHits(b: SchemaBuilder) {
  return b.titled(
    "ItemHitsV1",
    z.discriminatedUnion("matched_by", [
      b.titled(
        "TextHit",
        b.obj({
          ...shape(b),
          matched_by: z.literal("text"),
          matched_term: nonEmpty(),
          form_id: nonEmpty(),
          occurrences: count().min(1),
          offsets: z.array(offsetPair()).min(1),
          offsets_in: z.literal("text_norm"),
        }),
      ),
      b.titled(
        "SourceHit",
        b.obj({
          ...shape(b),
          matched_by: z.literal("source"),
          matched_term: z.null(),
          form_id: z.null(),
          occurrences: z.literal(0),
          offsets: z.array(offsetPair()).max(0),
          offsets_in: z.null(),
        }),
      ),
    ]),
  );
}

export type ItemHit = z.infer<ReturnType<typeof buildItemHits>>;
