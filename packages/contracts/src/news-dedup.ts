// news.dedup/v1: news-dedup's verdict (news-dedup §6.2) with the fields item_stories needs
// (ADR-0022). `item_id` and the reading of `dedup_version` as `version` are Q8's.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { dataShape, metadataShape } from "./metadata.ts";
import { count, idempotencyKey, share, timestamp, ulid, uuid } from "./primitives.ts";
import { DEDUP_MATCHED_BY, DEDUP_TYPES } from "./vocabulary.ts";

export const NEWS_DEDUP = "news.dedup/v1";

export function buildNewsDedup(b: SchemaBuilder) {
  return b.titled(
    "NewsDedupV1",
    b.obj({
      ...metadataShape(b, NEWS_DEDUP),
      type: z.enum(DEDUP_TYPES),
      item_id: uuid(),
      idempotency_key: idempotencyKey(),
      story_id: ulid(),
      is_origin: z.boolean(),
      duplicate_of: idempotencyKey().nullable(), // the origin's key
      cluster_size: count().min(1),
      version: count().min(1), // the item's story version, item_stories.version
      rank_in_cluster: count().min(1),
      origin_source_id: uuid(),
      origin_time: timestamp(),
      matched_by: z.enum(DEDUP_MATCHED_BY).nullable(),
      hamming_distance: count().nullable(),
      title_overlap: share().nullable(),
      source_id: uuid(),
      decided_at: timestamp(),
      previous_story_id: ulid().optional(),
      previous_origin: idempotencyKey().optional(),
      ...dataShape(b),
    }),
  );
}

export type NewsDedupVerdict = z.infer<ReturnType<typeof buildNewsDedup>>;
