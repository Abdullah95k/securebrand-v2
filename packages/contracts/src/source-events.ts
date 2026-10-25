// source.events/v1: registry-writer's one event per applied decision and source (ADR-0014): the
// source's identity and policy columns after the change, `previous` (the old value of every changed
// column, null on `added`), the decision and its actor. A control message: `producer` only, and its
// `retention_class` is the source's registry column (ADR-0003). Discriminated by `event`, each type
// with the reasons the one closed list allows it.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { metadataShape } from "./metadata.ts";
import { optionalShape, registryColumnShape, sourceColumnShape } from "./source-columns.ts";
import { actor, timestamp, ulid, uuid } from "./primitives.ts";
import {
  PUSH_COVERAGE_REASONS,
  ROUTE_HEALTH_REASONS,
  SOURCE_HEALTH_REASONS,
} from "./vocabulary.ts";

export const SOURCE_EVENTS = "source.events/v1";

export function buildSourceEvents(b: SchemaBuilder) {
  const columns = () => ({ ...sourceColumnShape(b), ...registryColumnShape() });
  const previous = () =>
    b.def("PreviousColumns", () =>
      b.obj(optionalShape({ ...sourceColumnShape(b), ...registryColumnShape() })),
    );
  const shape = () => ({
    ...metadataShape(b, SOURCE_EVENTS),
    source_id: uuid(),
    ...columns(),
    decision_id: ulid(),
    actor: actor(),
    at: timestamp(),
  });
  const event = (name: string, title: string, reason: z.ZodType) =>
    b.titled(title, b.obj({ ...shape(), event: z.literal(name), reason, previous: previous() }));
  const health = [...SOURCE_HEALTH_REASONS, ...ROUTE_HEALTH_REASONS] as const;
  return b.titled(
    "SourceEventsV1",
    z.discriminatedUnion("event", [
      b.titled(
        "AddedEvent",
        b.obj({ ...shape(), event: z.literal("added"), reason: z.null(), previous: z.null() }),
      ),
      event("updated", "UpdatedEvent", z.enum(["budget_wait", "client_removed"]).nullable()),
      event("tier_change", "TierChangeEvent", z.null()),
      event(
        "lifecycle_change",
        "LifecycleChangeEvent",
        z.enum(["not_found", "owner_request", "authorization_revoked"]).nullable(),
      ),
      event("health_change", "HealthChangeEvent", z.enum(health).nullable()),
      event("fallback_on", "FallbackOnEvent", z.enum([...health, "flag_on"]).nullable()),
      event("fallback_off", "FallbackOffEvent", z.enum([...health, "flag_off"]).nullable()),
      event(
        "push_coverage_change",
        "PushCoverageChangeEvent",
        z.enum(PUSH_COVERAGE_REASONS).nullable(),
      ),
    ]),
  );
}

export type SourceEvent = z.infer<ReturnType<typeof buildSourceEvents>>;
