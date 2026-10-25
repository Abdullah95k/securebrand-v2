// The keys each producer declares inside its open-ended objects: raw.items `context` (ADR-0005) and
// poster.profiles `extras` (ADR-0033). The types are the schemas'; these lists say who may use which.
import { z } from "zod";
import { loadRegistry } from "./load.ts";
import { own } from "./paths.ts";

const Declared = z.object({ keys: z.array(z.string()), required: z.array(z.string()) });
const ContextFile = z.object({
  producers: z.record(z.string(), Declared),
  by_kind: z.record(z.string(), Declared),
});
const ExtrasFile = z.object({ resolvers: z.record(z.string(), z.array(z.string())) });

const context = ContextFile.parse(loadRegistry("context-keys.json"));
const extras = ExtrasFile.parse(loadRegistry("extras-keys.json"));

export function contextKeyRegistry(): z.infer<typeof ContextFile> {
  return structuredClone(context);
}

export function extrasKeyRegistry(): z.infer<typeof ExtrasFile> {
  return structuredClone(extras);
}

/** The `context` keys a raw.items record of `kind` from `service` may carry, and those it must. */
export function declaredContextKeys(service: string, kind: string): z.infer<typeof Declared> {
  const byService = own(context.producers, service) ?? { keys: [], required: [] };
  const byKind = own(context.by_kind, kind) ?? { keys: [], required: [] };
  return {
    keys: [...new Set([...byService.keys, ...byKind.keys])],
    required: [...new Set([...byService.required, ...byKind.required])],
  };
}

/** The `extras` keys a resolver declares, or null for a service that declares none. */
export function declaredExtrasKeys(service: string): string[] | null {
  const keys = own(extras.resolvers, service);
  return keys ? [...keys] : null;
}
