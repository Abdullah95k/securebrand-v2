// dlq.<service>/v1: the record a dead letter holds (Q5), one shared definition whose `schema` is a
// pattern (F-52). Discriminated by `stage`: a produce-side entry has no consumed offset and no
// consumer group (F-21). `message` holds the original as JSON, or `raw` its bytes in base64 when it
// did not parse, exactly one. When the original's provenance passes the original's own type, it is
// copied to the top level, with the original's class when that is a valid one; otherwise neither
// (F-42, D-1, D-12). A `raw` entry is a stated exception to ADR-0003. The top-level provenance is
// typed as the signal's, so it holds a non-item deletion's null route; validate() binds it to the
// original's own type.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { dlqMetadataShape, retentionClass, signalProvenance } from "./metadata.ts";
import { PATTERNS, count, nonEmpty, serviceName, timestamp, token, ulid } from "./primitives.ts";
import { DLQ_ERROR_CLASSES } from "./vocabulary.ts";

export const DLQ = "dlq.<service>/v1";

const shape = (b: SchemaBuilder) => ({
  ...dlqMetadataShape(b),
  message: z.record(z.string(), z.unknown()).optional(),
  raw: z.string().regex(PATTERNS.base64).optional(),
  error: b.def("DeadLetterError", () =>
    b.obj({
      class: z.enum(DLQ_ERROR_CLASSES),
      message: nonEmpty(),
      attempts: count().min(1),
      first_failed_at: timestamp(),
      last_failed_at: timestamp(),
    }),
  ),
  provenance: signalProvenance(b).optional(),
  retention_class: retentionClass().optional(),
});

export function buildDlq(b: SchemaBuilder) {
  const original = (consumed: boolean) => ({
    topic: token(),
    partition: consumed ? count() : z.null(),
    offset: consumed ? count() : z.null(),
    // The original message's key; for a produce-side entry the key the SDK would have set, null
    // when it could not be computed.
    key: z.string().nullable(),
    schema: token().nullable(),
    message_id: ulid().nullable(),
  });
  return b.titled(
    "DlqV1",
    z.discriminatedUnion("stage", [
      b.titled(
        "ConsumeDeadLetter",
        b.obj({
          ...shape(b),
          stage: z.literal("consume"),
          original: b.def("ConsumedOriginal", () => b.obj(original(true))),
          consumer: b.def("ConsumerGroup", () =>
            b.obj({ service: serviceName(), group: nonEmpty() }),
          ),
        }),
      ),
      b.titled(
        "ProduceDeadLetter",
        b.obj({
          ...shape(b),
          stage: z.literal("produce"),
          original: b.def("ProducedOriginal", () => b.obj(original(false))),
          consumer: b.def("ProducingService", () =>
            b.obj({ service: serviceName(), group: z.null() }),
          ),
        }),
      ),
    ]),
  );
}

export type DeadLetter = z.infer<ReturnType<typeof buildDlq>>;
