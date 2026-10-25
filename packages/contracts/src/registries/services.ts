// The service index and the D3 writer names (CONVENTIONS v1.1 L372 to L384; Q4), and the vendors by
// route (ADR-0051 (c)). Service names and vendors are registry data, not schema enums: producer mode
// checks them, and a new one adds a name here inside the version (Q1, F-09).
import { z } from "zod";
import { loadRegistry } from "./load.ts";

const ServicesFile = z.object({
  platform_groups: z.record(z.string(), z.array(z.string())),
  shared_groups: z.record(z.string(), z.array(z.string())),
  d3_writers: z.array(z.string()),
});
const VendorsFile = z.object({ amber: z.array(z.string()), green: z.array(z.string()) });

const services = ServicesFile.parse(loadRegistry("services.json"));
const vendors = VendorsFile.parse(loadRegistry("vendors.json"));

/** The platform groups of the service index (Facebook, Instagram, TikTok, X, LinkedIn, Telegram, YouTube, News, Web). */
export const PLATFORM_GROUPS: Readonly<Record<string, readonly string[]>> =
  services.platform_groups;
/** The 66 services of the Facebook to Web groups, which the producer rows call `@platform`. */
export const PLATFORM_SERVICES: readonly string[] = Object.values(services.platform_groups).flat();
/** The 86 services of the index. */
export const INDEX_SERVICES: readonly string[] = [
  ...PLATFORM_SERVICES,
  ...Object.values(services.shared_groups).flat(),
];
/** The D3 writers that produce messages (Q4). */
export const D3_WRITERS: readonly string[] = services.d3_writers;
export const AMBER_VENDORS: readonly string[] = vendors.amber;
export const GREEN_VENDORS: readonly string[] = vendors.green;

const known = new Set<string>([...INDEX_SERVICES, ...D3_WRITERS]);
const platform = new Set<string>(PLATFORM_SERVICES);

export function isKnownService(service: string): boolean {
  return known.has(service);
}

export function isPlatformService(service: string): boolean {
  return platform.has(service);
}

/** An amber record names an amber vendor; a green one a licensed engine or none (ADR-0051 (c)). */
export function isKnownVendor(route: string, vendor: string | null): boolean {
  if (route === "amber") return vendor !== null && AMBER_VENDORS.includes(vendor);
  if (route === "green") return vendor === null || GREEN_VENDORS.includes(vendor);
  return false;
}

/** A vendor of either route's list: the check for a vendor named without its route (note 11). */
export function isListedVendor(vendor: string): boolean {
  return AMBER_VENDORS.includes(vendor) || GREEN_VENDORS.includes(vendor);
}

const index = new Set<string>(INDEX_SERVICES);

/**
 * Whether `service` is one of `producers`, where `@platform` stands for the platform services and
 * `*` for any service of the index (the D3 writers have their own rows); `@queue` is resolved by the
 * caller, which knows the queue.
 */
export function namesService(producers: readonly string[], service: string): boolean {
  return producers.some(
    (p) =>
      p === service ||
      (p === "@platform" && isPlatformService(service)) ||
      (p === "*" && index.has(service)),
  );
}
