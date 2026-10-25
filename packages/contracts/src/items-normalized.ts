// items.normalized/v1: normalize-item's message (normalize-item §6.2, an approved PRD) as the ADRs
// reshape it (ADR-0003, ADR-0005, ADR-0009, ADR-0031, ADR-0059, ADR-0068, ADR-0070). A comment
// carries its parent and root; a top-level item carries neither.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { dataShape, metadataShape, metrics, usageSignals } from "./metadata.ts";
import {
  PATTERNS,
  authorRef,
  count,
  httpUrl,
  idempotencyKey,
  nonEmpty,
  platformId,
  prefixedSha256,
  rawRef,
  share,
  snakeName,
  timestamp,
  token,
  uuid,
} from "./primitives.ts";
import { AUTHOR_TYPES, JOB_KIND_VALUES, LANG_LABELS, PLATFORMS } from "./vocabulary.ts";

export const ITEMS_NORMALIZED = "items.normalized/v1";

/** An item's author: always a keyed reference, the registered source's id where there is one (ADR-0010). */
export const itemAuthor = (b: SchemaBuilder) =>
  b.def("ItemAuthor", () =>
    b.obj({
      author_ref: authorRef().nullable(),
      author_type: z.enum(AUTHOR_TYPES),
      author_source_id: uuid().nullable(),
      // Only for a registered source (ADR-0070 d), ADR-0010), checked by validate().
      display_name: z.string().optional(),
      author_followers: count().optional(),
    }),
  );

const shape = (b: SchemaBuilder) => ({
  ...metadataShape(b, ITEMS_NORMALIZED),
  item_id: uuid(),
  idempotency_key: idempotencyKey(),
  platform: z.enum(PLATFORMS),
  source_id: uuid(),
  parent_seen: z.boolean(),
  content_hash: prefixedSha256(),
  version: count().min(1),
  platform_id: platformId(),
  url: httpUrl().nullable(),
  created_at: timestamp().nullable(),
  title: z.string().nullable(),
  text: z.string().nullable(),
  text_norm: z.string().nullable(),
  lang: z.enum(LANG_LABELS).nullable(),
  lang_conf: share().nullable(),
  dialect: snakeName().nullable(),
  dialect_conf: share().nullable(),
  script: snakeName().nullable(),
  lang_model_version: token().nullable(),
  lang_pending: z.boolean(),
  author: itemAuthor(b),
  media: z.array(
    b.def("Media", () => b.obj({ type: z.string().regex(PATTERNS.snakeName), url: httpUrl() })),
  ),
  hashtags: z.array(nonEmpty()),
  at_mentions: z.array(nonEmpty()),
  links: z.array(nonEmpty()),
  metrics_snapshot: metrics(b),
  expires_at: timestamp().nullable(),
  normalizer_version: token(),
  raw_ref: rawRef(),
  job_kind: z.enum(JOB_KIND_VALUES),
  sensitive_event: z.boolean(),
  text_full_ref: nonEmpty().optional(),
  usage_signals: usageSignals(b).optional(),
  // Transient: set only for posters not yet classed, never stored (ADR-0031).
  poster_platform_id: platformId().optional(),
  quoted_id: uuid().optional(),
  video_channel_id: token().optional(),
  // Copied from the raw envelope (ADR-0005 L27), for ClickHouse `items.client_ids`, which
  // deletion-propagator reads and nothing else fills (O-10, F-38).
  client_ids: z.array(uuid()).optional(),
  ...dataShape(b),
});

export function buildItemsNormalized(b: SchemaBuilder) {
  const topLevel = (kind: "post" | "video" | "article" | "result", title: string) =>
    b.titled(
      title,
      b.obj({ ...shape(b), kind: z.literal(kind), parent_id: z.null(), root_id: z.null() }),
    );
  return b.titled(
    "ItemsNormalizedV1",
    z.discriminatedUnion("kind", [
      topLevel("post", "NormalizedPost"),
      topLevel("video", "NormalizedVideo"),
      b.titled(
        "NormalizedComment",
        b.obj({ ...shape(b), kind: z.literal("comment"), parent_id: uuid(), root_id: uuid() }),
      ),
      topLevel("article", "NormalizedArticle"),
      topLevel("result", "NormalizedResult"),
    ]),
  );
}

export type NormalizedItem = z.infer<ReturnType<typeof buildItemsNormalized>>;
