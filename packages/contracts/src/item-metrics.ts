// item.metrics/v1: one flat message per engagement read (ADR-0034). normalize-item writes it for
// reads whose records become items, labelled from `job_kind`; the reading service for count-only
// reads (ADR-0034, ADR-0024).
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { LIVE_STATES } from "./context.ts";
import { dataShape, metadataShape, metrics } from "./metadata.ts";
import { idempotencyKey, metricsStep, platformId, timestamp, token, uuid } from "./primitives.ts";
import { PLATFORMS, type OBSERVATION_LABELS } from "./vocabulary.ts";

export const ITEM_METRICS = "item.metrics/v1";

// Every observation label but `refresh`, the one that carries a step.
const READ_LABELS = [
  "first_sight",
  "poll",
  "backfill",
  "ops_force",
  "live_end",
] as const satisfies readonly (typeof OBSERVATION_LABELS)[number][];

export function buildItemMetrics(b: SchemaBuilder) {
  return b.titled(
    "ItemMetricsV1",
    b.obj({
      ...metadataShape(b, ITEM_METRICS),
      item_id: uuid(),
      idempotency_key: idempotencyKey(),
      platform: z.enum(PLATFORMS),
      platform_id: platformId(),
      source_id: uuid(),
      // The post's creation time.
      created_at: timestamp().nullable(),
      // The step is +24h, +7d or refresh:<request_id> with `refresh`, null otherwise (ADR-0034,
      // ADR-0018).
      observation: b.def("Observation", () =>
        z.discriminatedUnion("label", [
          b.titled(
            "RefreshObservation",
            b.obj({ label: z.literal("refresh"), step: metricsStep(), observed_at: timestamp() }),
          ),
          b.titled(
            "ReadObservation",
            b.obj({
              label: z.enum(READ_LABELS),
              step: z.null(),
              observed_at: timestamp(),
            }),
          ),
        ]),
      ),
      metrics: metrics(b),
      channel_id: token().optional(),
      live_state: z.enum(LIVE_STATES).optional(),
      regressed: z.boolean().optional(),
      ...dataShape(b),
    }),
  );
}

export type ItemMetric = z.infer<ReturnType<typeof buildItemMetrics>>;
