// deletions/v1 (ADR-0035, ADR-0054, ADR-0069): discriminated by `scope`. An item-scope deletion
// copies its items' provenance and class; an author-, source- or client-scope one carries the
// signal's provenance and no retention class (ADR-0003 L28), route and vendor null when the signal
// is no platform fetch (F-08). The subject's key field appears once, at the top, never in `target`.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { metadataShape, provenance, retentionClass, signalProvenance } from "./metadata.ts";
import { PATTERNS, actor, authorRef, platformId, timestamp, ulid, uuid } from "./primitives.ts";
import { CONTENT_KINDS, DELETION_MODES, DELETION_REASONS, PLATFORMS } from "./vocabulary.ts";

export const DELETIONS = "deletions/v1";

const targetExtras = () => ({
  fetched_before: timestamp().optional(),
  countries: z.array(z.string().regex(PATTERNS.country)).optional(),
  // X: registered sources and every account a poster_profiles row holds (ADR-0010, ADR-0039).
  user_ids: z.array(platformId()).optional(),
});

const shape = (b: SchemaBuilder) => ({
  ...metadataShape(b, DELETIONS),
  deletion_id: z.string().regex(PATTERNS.deletionId),
  reason: z.enum(DELETION_REASONS),
  mode: z.enum(DELETION_MODES),
  signal_at: timestamp(),
  due_at: timestamp(),
  requested_by: actor().optional(),
  run_id: ulid().optional(),
  event_at: timestamp().optional(),
});

export function buildDeletions(b: SchemaBuilder) {
  const subjectTarget = () =>
    b.def("SubjectTarget", () =>
      b.obj({
        platform: z.enum(PLATFORMS).optional(),
        kind: z.enum(CONTENT_KINDS).optional(),
        platform_ids: z.array(platformId()).optional(),
        item_ids: z.array(uuid()).optional(),
        ...targetExtras(),
      }),
    );
  return b.titled(
    "DeletionsV1",
    z.discriminatedUnion("scope", [
      b.titled(
        "ItemDeletion",
        b.obj({
          ...shape(b),
          scope: z.literal("item"),
          source_id: uuid(),
          target: b.def("ItemTarget", () =>
            b.obj({
              platform: z.enum(PLATFORMS),
              kind: z.enum(CONTENT_KINDS),
              // uuid v5 from the key helper, never ULIDs (ADR-0006).
              item_ids: z.array(uuid()).min(1),
              platform_ids: z.array(platformId()).optional(),
              ...targetExtras(),
            }),
          ),
          retention_class: retentionClass(),
          provenance: provenance(b),
        }),
      ),
      b.titled(
        "AuthorDeletion",
        b.obj({
          ...shape(b),
          scope: z.literal("author"),
          author_ref: authorRef(),
          target: subjectTarget(),
          provenance: signalProvenance(b),
        }),
      ),
      b.titled(
        "SourceDeletion",
        b.obj({
          ...shape(b),
          scope: z.literal("source"),
          source_id: uuid(),
          target: subjectTarget(),
          provenance: signalProvenance(b),
        }),
      ),
      b.titled(
        "ClientDeletion",
        b.obj({
          ...shape(b),
          scope: z.literal("client"),
          client_id: uuid(),
          target: subjectTarget(),
          provenance: signalProvenance(b),
        }),
      ),
    ]),
  );
}

export type Deletion = z.infer<ReturnType<typeof buildDeletions>>;
