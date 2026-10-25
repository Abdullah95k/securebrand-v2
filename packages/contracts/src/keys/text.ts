// Byte rules shared by every key and hash (ADR-0006): NFC, UTF-8, SHA-256 in lower-case hex.
// NFC and lower case are those of Unicode 15.1.0 in both languages (D-2): a code point 15.1 leaves
// unassigned is a starter with no mapping there, so it passes through both unchanged, and a
// runtime with a later Unicode version gives 15.1's result for the runs of text between them.
import { createHash, createHmac } from "node:crypto";
import { ContractError } from "../errors.ts";
import { loadRegistry } from "../registries/load.ts";

/** Refuses a Unicode version below 15.1, which would normalise 15.1's text differently. */
export function checkUnicodeVersion(version: string | undefined): void {
  const m = /^([0-9]+)\.([0-9]+)(\.[0-9]+)?$/.exec(version ?? "");
  const [major, minor] = [Number(m?.[1] ?? 0), Number(m?.[2] ?? 0)];
  if (major < 15 || (major === 15 && minor < 1))
    throw new ContractError("unicode_version", `Unicode ${version ?? "unknown"} is below 15.1`);
}

checkUnicodeVersion(process.versions.unicode);

const unassigned = (
  loadRegistry("unicode-15.1-unassigned.json") as { ranges: [number, number][] }
).ranges
  .map(([first, last]) => `\\u{${first.toString(16)}}-\\u{${last.toString(16)}}`)
  .join("");
const HAS_UNASSIGNED = new RegExp(`[${unassigned}]`, "u");
const UNASSIGNED_RUNS = new RegExp(`([${unassigned}]+)`, "u");

// Applies f to each run between code points unassigned in Unicode 15.1 and keeps those unchanged.
function byRuns(s: string, f: (run: string) => string): string {
  if (!HAS_UNASSIGNED.test(s)) return f(s);
  return s
    .split(UNASSIGNED_RUNS)
    .map((part, i) => (i % 2 === 0 ? f(part) : part))
    .join("");
}

export const nfc = (s: string): string => byRuns(s, (run) => run.normalize("NFC"));

export const lowerCase = (s: string): string => byRuns(s, (run) => run.toLowerCase());

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
