// A14 (F3, plan T6): one leader-election lock key per service, distinct across the service index
// and the D3 writers, and stable: the golden values below are what supabase's leader_lock_key()
// returns for the same names.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { leaderLockKey } from "../../src/db/index.ts";
import { ContractError } from "../../src/errors.ts";
import { PACKAGE_DIR } from "../helpers.ts";

const registry = JSON.parse(
  readFileSync(join(PACKAGE_DIR, "registries/services.json"), "utf8"),
) as {
  platform_groups: Record<string, string[]>;
  shared_groups: Record<string, string[]>;
  d3_writers: string[];
};
const names = [
  ...Object.values(registry.platform_groups).flat(),
  ...Object.values(registry.shared_groups).flat(),
  ...registry.d3_writers,
];

describe("leaderLockKey", () => {
  it("every service in the registry gets a distinct lock key", () => {
    expect(names.length).toBeGreaterThan(86);
    const keys = new Set(names.map((name) => leaderLockKey(name)));
    expect(keys.size).toBe(names.length);
  });

  it("gives the golden keys", () => {
    expect(leaderLockKey("registry-writer")).toBe(GOLDEN["registry-writer"]);
    expect(leaderLockKey("fb-page-feed-poller")).toBe(GOLDEN["fb-page-feed-poller"]);
    expect(leaderLockKey("quota-governor")).toBe(GOLDEN["quota-governor"]);
  });

  it("is a signed 64-bit value", () => {
    for (const name of names) {
      const key = leaderLockKey(name);
      expect(key >= -(2n ** 63n) && key < 2n ** 63n, name).toBe(true);
    }
  });

  it("refuses a name that is not a service name", () => {
    for (const bad of ["", "Registry-Writer", "registry_writer", "registry-writer:reconcile", " x"])
      expect(() => leaderLockKey(bad), JSON.stringify(bad)).toThrow(ContractError);
  });
});

// From the database: select public.leader_lock_key(name), for each name (F3's migrations), on
// the stack's Supabase database, 25 Oct 2026.
const GOLDEN: Record<string, bigint> = {
  "registry-writer": -8259956846045360985n,
  "fb-page-feed-poller": -6202983560647304258n,
  "quota-governor": -5066906981560162251n,
};
