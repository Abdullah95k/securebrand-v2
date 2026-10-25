// A14 (plan T6): the database's leader_lock_key() and the contracts' leaderLockKey() give the same
// key for every name in the service index and the D3 writers, and the SQL function refuses a name
// that is not a service name.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { leaderLockKey } from "contracts/db";
import { describe, expect, it } from "vitest";
import { CONTRACTS_DIR } from "../../tools/paths.ts";
import { asRole } from "../helpers/db.ts";
import { testDatabaseUrl } from "../helpers/env.ts";

const registry = JSON.parse(
  readFileSync(join(CONTRACTS_DIR, "registries/services.json"), "utf8"),
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

describe("leader lock keys", () => {
  it("the SQL function and the TypeScript helper give the same key", async () => {
    const keys = await asRole(testDatabaseUrl(), "service_role", (s) =>
      s.rows<{ name: string; key: string }>(
        "select name, public.leader_lock_key(name)::text as key from unnest($1::text[]) as name",
        [names],
      ),
    );
    expect(keys).toHaveLength(names.length);
    for (const { name, key } of keys) expect(BigInt(key), name).toBe(leaderLockKey(name));
  });

  it("the SQL function refuses a name that is not a service name", async () => {
    const code = await asRole(testDatabaseUrl(), "service_role", (s) =>
      s.failure("select public.leader_lock_key('Registry_Writer')"),
    );
    expect(code).toBe("22023");
  });

  it("a scheduler takes and releases its lock with the key", async () => {
    const result = await asRole(testDatabaseUrl(), "service_role", (s) =>
      s.rows<{ taken: boolean; released: boolean }>(
        `select pg_try_advisory_lock(public.leader_lock_key('fb-page-feed-poller')) as taken,
                pg_advisory_unlock(public.leader_lock_key('fb-page-feed-poller')) as released`,
      ),
    );
    expect(result[0]).toEqual({ taken: true, released: true });
  });
});
