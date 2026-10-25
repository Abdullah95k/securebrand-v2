// author_ref = HMAC-SHA256(key, UTF-8(NFC("<platform>:<author platform id>"))) (ADR-0010). The key
// is an argument: Vault holds the real one, and the package never reads a key itself.
import { ContractError } from "../errors.ts";
import { PLATFORMS } from "../vocabulary.ts";
import { hmacSha256Hex, nfc, requireString } from "./text.ts";

export function authorRef(key: Uint8Array, platform: string, authorPlatformId: string): string {
  if (!(key instanceof Uint8Array) || key.length === 0) throw new ContractError("bad_key", "the HMAC key is empty");
  if (!(PLATFORMS as readonly string[]).includes(platform)) throw new ContractError("bad_platform", platform);
  if (requireString(authorPlatformId, "author platform id") === "") {
    throw new ContractError("bad_author_id", "the author platform id is empty");
  }
  return hmacSha256Hex(key, nfc(`${platform}:${authorPlatformId}`));
}

/** True when the reference matches under any key still covering retained data (ADR-0010). */
export function matchesAuthorRef(
  ref: string,
  platform: string,
  authorPlatformId: string,
  keys: readonly Uint8Array[],
): boolean {
  return keys.some((key) => authorRef(key, platform, authorPlatformId) === ref);
}
