// The deterministic ULID (ADR-0006): time part the event's own time in milliseconds, random part the
// first 10 bytes of SHA-256 over the declared fields' UTF-8, joined by '|'.
import { ContractError } from "../errors.ts";
import { requireString, sha256Bytes } from "./text.ts";
import { messageTimeMillis } from "./time.ts";

const CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";

/** Encodes a 48-bit time and 10 bytes of randomness as a ULID's 26 Crockford base32 characters. */
export function encodeUlid(timeMs: number, random: Uint8Array): string {
  if (!Number.isInteger(timeMs) || timeMs < 0 || timeMs >= 2 ** 48)
    throw new ContractError("bad_time", String(timeMs));
  if (random.length !== 10) throw new ContractError("bad_random", "ULID randomness is 10 bytes");
  let value = BigInt(timeMs);
  for (const byte of random) value = (value << 8n) | BigInt(byte);
  let out = "";
  for (let i = 25; i >= 0; i -= 1) out += CROCKFORD[Number((value >> BigInt(5 * i)) & 31n)];
  return out;
}

export function deterministicUlid(time: string, fields: readonly string[]): string {
  const ms = messageTimeMillis(requireString(time, "time"));
  const joined = fields.map((f, i) => requireString(f, `field ${i}`)).join("|");
  return encodeUlid(ms, sha256Bytes(joined).subarray(0, 10));
}

export interface HitMessageIdInput {
  hit_at: string;
  hit_id: string;
  item_version: number;
  keyword_set_version: string;
}

/** keyword-matcher's replay-stable message_id (ADR-0006, ADR-0070 a); keyword-matcher §5.3 L77). */
export function hitMessageId(input: HitMessageIdInput): string {
  if (!Number.isInteger(input.item_version) || input.item_version < 0) {
    throw new ContractError("bad_version", "item_version must be a non-negative integer");
  }
  return deterministicUlid(input.hit_at, [
    input.hit_id,
    String(input.item_version),
    input.keyword_set_version,
  ]);
}

export interface CommentDecayJobIdInput {
  due_at: string;
  item_id: string;
  lane: string;
  series_step: string;
}

/** comment-decay-scheduler's job_id: sha256(item_id | lane | series_step), time due_at (§5.3 L84). */
export function commentDecayJobId(input: CommentDecayJobIdInput): string {
  return deterministicUlid(input.due_at, [input.item_id, input.lane, input.series_step]);
}
