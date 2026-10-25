// Each producing service's visibility, keyed by provenance.service, which keyword-matcher's gate
// reads (ADR-0053 L32; F-18): owner, watchers or pool, or the owned-property rule of CONVENTIONS
// v1.1 L386, resolved against the source's owned_by_client.
import { z } from "zod";
import type { Visibility } from "../vocabulary.ts";
import { loadRegistry } from "./load.ts";
import { own } from "./paths.ts";

const Rule = z.object({
  rule: z.enum(["owner", "watchers", "pool", "owner_or_watchers", "owner_or_pool"]),
  limit: z.enum(["amber", "x_gate"]).nullable(),
});
const VisibilityFile = z.object({ services: z.record(z.string(), Rule) });
export type VisibilityRule = z.infer<typeof Rule>;

const file = VisibilityFile.parse(loadRegistry("visibility.json"));

/** The service's declared rule and client filter, or null for a service that declares none. */
export function visibilityRule(service: string): VisibilityRule | null {
  const rule = own(file.services, service);
  return rule ? { ...rule } : null;
}

/** The visibility of a record `service` fetched from a source that is, or is not, client-owned. */
export function visibilityOf(service: string, ownedByClient: boolean): Visibility | null {
  const rule = own(file.services, service)?.rule;
  switch (rule) {
    case undefined:
      return null;
    case "owner_or_watchers":
      return ownedByClient ? "owner" : "watchers";
    case "owner_or_pool":
      return ownedByClient ? "owner" : "pool";
    case "owner":
    case "watchers":
    case "pool":
      return rule;
  }
}
