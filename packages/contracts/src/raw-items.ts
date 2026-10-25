// raw.items/v1: one nested {envelope, payload} message for every producer (ADR-0005). The payload is
// the platform record as returned, minus identities (ADR-0010); news-article-extractor's `article`
// payload is our own extract and is typed (F-30). The envelope is discriminated by the record kind
// (ADR-0008); a content kind carries its key, a comment its parent and root (ADR-0009).
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { context } from "./context.ts";
import { metadataShape, provenance, retentionClass } from "./metadata.ts";
import {
  authorRef,
  candidateKey,
  count,
  httpUrl,
  idempotencyKey,
  nonEmpty,
  platformId,
  rawRef,
  sha256Hex,
  timestamp,
  token,
  ulid,
  uuid,
} from "./primitives.ts";
import { JOB_KIND_VALUES, PLATFORMS } from "./vocabulary.ts";

export const RAW_ITEMS = "raw.items/v1";

const envelopeShape = (b: SchemaBuilder) => ({
  ...metadataShape(b, RAW_ITEMS),
  platform: z.enum(PLATFORMS),
  provenance: provenance(b),
  retention_class: retentionClass(),
  client_ids: z.array(uuid()),
  job_id: ulid(),
  attempt: count().min(1),
  job_kind: z.enum(JOB_KIND_VALUES),
  api_version: token().max(64),
  raw_ref: rawRef(),
  // Exactly one of the two, checked by validate(): a record about a candidate not yet a source
  // carries its candidate key, of any record kind (ADR-0005 L28, ADR-0004 L29; F-03, Q14).
  source_id: uuid().optional(),
  candidate_key: candidateKey().optional(),
  // An author identity the adapter replaced; present on every comment and reaction (Q3).
  author_ref: authorRef().optional(),
  // The payload paths an adapter removed or replaced (ADR-0009).
  redacted_fields: z.array(nonEmpty()).optional(),
  context: context(b).optional(),
});

const itemShape = () => ({ platform_id: platformId(), idempotency_key: idempotencyKey() });

/** The envelope of every record kind but `article`, discriminated by `kind`. */
const recordEnvelope = (b: SchemaBuilder) =>
  z.discriminatedUnion("kind", [
    b.titled(
      "PostEnvelope",
      b.obj({ ...envelopeShape(b), kind: z.literal("post"), ...itemShape() }),
    ),
    b.titled(
      "VideoEnvelope",
      b.obj({ ...envelopeShape(b), kind: z.literal("video"), ...itemShape() }),
    ),
    b.titled(
      "CommentEnvelope",
      b.obj({
        ...envelopeShape(b),
        kind: z.literal("comment"),
        ...itemShape(),
        parent_id: uuid(),
        root_id: uuid(),
        author_ref: authorRef().nullable(),
      }),
    ),
    b.titled(
      "ResultEnvelope",
      b.obj({ ...envelopeShape(b), kind: z.literal("result"), ...itemShape() }),
    ),
    b.titled("ProfileEnvelope", b.obj({ ...envelopeShape(b), kind: z.literal("profile") })),
    b.titled(
      "ReactionEnvelope",
      b.obj({
        ...envelopeShape(b),
        kind: z.literal("reaction"),
        platform_id: platformId(),
        author_ref: authorRef().nullable(),
      }),
    ),
    b.titled(
      "SearchResponseEnvelope",
      b.obj({ ...envelopeShape(b), kind: z.literal("search_response") }),
    ),
    b.titled("MetricsEnvelope", b.obj({ ...envelopeShape(b), kind: z.literal("metrics") })),
  ]);

/** news-article-extractor's extract (ADR-0070 L25 (h) spellings; news-article-extractor §6.2). */
export const articlePayload = (b: SchemaBuilder) =>
  b.def("ArticlePayload", () =>
    b.obj({
      url: httpUrl(),
      final_url: httpUrl(),
      canonical_url: httpUrl().nullable(),
      title: z.string().nullable(),
      excerpt: z.string().nullable(),
      published_at: timestamp().nullable(),
      text_full_ref: nonEmpty().nullable(),
      text_expires_at: timestamp().nullable(),
      text_sha256: sha256Hex().nullable(),
      title_sha256: sha256Hex().nullable(),
      extractor: nonEmpty(),
      extractor_version: nonEmpty(),
      excerpt_chars: count().optional(),
      word_count: count().optional(),
      author: z.string().nullable().optional(),
      language: z.string().nullable().optional(),
      image_urls: z.array(httpUrl()).optional(),
      http_status: count().optional(),
    }),
  );

export function buildRawItems(b: SchemaBuilder) {
  const articleMessage = b.titled(
    "ArticleMessage",
    b.obj({
      envelope: b.titled(
        "ArticleEnvelope",
        b.obj({ ...envelopeShape(b), kind: z.literal("article"), ...itemShape() }),
      ),
      payload: articlePayload(b),
    }),
  );
  const recordMessage = b.titled(
    "RecordMessage",
    b.obj({
      envelope: recordEnvelope(b),
      // The platform record as returned, minus identities (ADR-0005, ADR-0010).
      payload: z.record(z.string(), z.unknown()),
    }),
  );
  return b.titled("RawItemsV1", z.union([articleMessage, recordMessage]));
}

export type RawItem = z.infer<ReturnType<typeof buildRawItems>>;
