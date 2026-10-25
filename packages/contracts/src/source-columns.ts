// A source's identity and policy columns (registry-writer §3 L27 and ADR-0013's additions), as the
// registry.decisions `add` and `update` blocks and the source.events messages carry them.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { countrySignals, langShare, platformMeta, retentionClass } from "./metadata.ts";
import {
  actor,
  count,
  httpUrl,
  nonEmpty,
  platformId,
  timestamp,
  uuid,
  vendorName,
} from "./primitives.ts";
import {
  ADDED_BY,
  FLAG_REASONS,
  HEALTHS,
  LIFECYCLES,
  PLATFORMS,
  ROUTE_HEALTH_REASONS,
  ROUTES,
  SOURCE_HEALTH_REASONS,
  SOURCE_TYPES,
  TIERS,
} from "./vocabulary.ts";

export const tier = () => z.literal(TIERS);

/** The columns a decision may set: every identity and policy column of ADR-0013 L25. */
export const sourceColumnShape = (b: SchemaBuilder) => ({
  platform: z.enum(PLATFORMS),
  source_type: z.enum(SOURCE_TYPES),
  platform_id: platformId().nullable(),
  handle: nonEmpty().nullable(),
  url: httpUrl().nullable(),
  display_name: z.string().nullable(),
  route: z.enum(ROUTES),
  vendor: vendorName().nullable(),
  tier: tier(),
  lifecycle: z.enum(LIFECYCLES),
  push_covered: z.boolean(),
  retention_class: retentionClass(),
  client_ids: z.array(uuid()),
  owned_by_client: z.boolean(),
  added_by: z.enum(ADDED_BY),
  followers: count().nullable(),
  country_signals: countrySignals(b).nullable(),
  lang_share: langShare(b).nullable(),
  platform_meta: platformMeta(b),
});

/** The columns registry-writer keeps beside them: when added, health (ADR-0016) and the notes. */
export const registryColumnShape = () => ({
  added_at: timestamp(),
  health: z.enum(HEALTHS),
  health_reason: z
    .enum([...SOURCE_HEALTH_REASONS, ...FLAG_REASONS, ...ROUTE_HEALTH_REASONS])
    .nullable(),
  health_set_by: actor().nullable(),
  health_changed_at: timestamp().nullable(),
  notes: z.string().nullable(),
});

/** Every key of a shape made optional: a partial object over its columns. */
export function optionalShape<T extends z.ZodRawShape>(shape: T) {
  return z.object(shape).partial().shape;
}
