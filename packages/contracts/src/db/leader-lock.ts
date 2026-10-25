// Leader-election lock keys (F3, plan T6): each rotating service's scheduler takes
// pg_try_advisory_lock(leaderLockKey(service)). The key is the first eight bytes of
// sha256("securebrand:leader:" + service), read as a signed big-endian 64-bit integer, which is what
// the database's leader_lock_key(service) returns, so a service may compute it in either place.
import { createHash } from "node:crypto";
import { ContractError } from "../errors.ts";
import { PATTERNS } from "../primitives.ts";

/** The namespace every leader lock key hashes under, apart from any other advisory lock. */
export const LEADER_LOCK_NAMESPACE = "securebrand:leader:";

/** The advisory lock key of `service`'s leader election. */
export function leaderLockKey(service: string): bigint {
  if (!PATTERNS.service.test(service)) throw new ContractError("bad_service", JSON.stringify(service));
  return createHash("sha256")
    .update(LEADER_LOCK_NAMESPACE + service, "utf8")
    .digest()
    .readBigInt64BE(0);
}
