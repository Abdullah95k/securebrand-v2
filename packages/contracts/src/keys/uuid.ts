// uuid v5 (RFC 9562): SHA-1 over the namespace's bytes and the UTF-8 of the name.
import { createHash } from "node:crypto";
import { ContractError } from "../errors.ts";
import { PATTERNS } from "../primitives.ts";

export function uuidV5(namespace: string, name: string): string {
  if (!PATTERNS.uuid.test(namespace)) throw new ContractError("bad_uuid", `namespace ${namespace}`);
  const ns = Buffer.from(namespace.replaceAll("-", ""), "hex");
  const digest = createHash("sha1").update(ns).update(name, "utf8").digest();
  const b = digest.subarray(0, 16);
  b[6] = ((b[6] ?? 0) & 0x0f) | 0x50;
  b[8] = ((b[8] ?? 0) & 0x3f) | 0x80;
  const hex = b.toString("hex");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}
