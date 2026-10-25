// Byte rules shared by every key and hash (ADR-0006): NFC, UTF-8, SHA-256 in lower-case hex.
import { createHash, createHmac } from "node:crypto";
import { ContractError } from "../errors.ts";

export const nfc = (s: string): string => s.normalize("NFC");

export function assertWellFormed(s: string, what: string): void {
  if (!s.isWellFormed()) throw new ContractError("not_unicode", `${what} holds a lone surrogate`);
}

export function sha256Hex(s: string): string {
  return createHash("sha256").update(s, "utf8").digest("hex");
}

export function sha256Bytes(s: string): Uint8Array {
  return new Uint8Array(createHash("sha256").update(s, "utf8").digest());
}

export function hmacSha256Hex(key: Uint8Array, s: string): string {
  return createHmac("sha256", key).update(s, "utf8").digest("hex");
}

/** Orders strings by Unicode code point, as Python does; the default sort compares UTF-16 units. */
export function compareCodePoints(a: string, b: string): number {
  const ia = a[Symbol.iterator]();
  const ib = b[Symbol.iterator]();
  for (;;) {
    const ca = ia.next();
    const cb = ib.next();
    if (ca.done) return cb.done ? 0 : -1;
    if (cb.done) return 1;
    const da = ca.value.codePointAt(0) ?? 0;
    const db = cb.value.codePointAt(0) ?? 0;
    if (da !== db) return da < db ? -1 : 1;
  }
}

export function requireString(value: unknown, what: string): string {
  if (typeof value !== "string") throw new ContractError("not_string", `${what} must be a string`);
  assertWellFormed(value, what);
  return value;
}
