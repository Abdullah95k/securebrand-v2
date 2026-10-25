// content_hash (ADR-0009): media URLs never enter it, since signed URLs change between reads.
import { nfc, requireString, sha256Hex } from "./text.ts";

export function contentHash(title: string | null, text: string | null): string {
  const body = nfc(text === null ? "" : requireString(text, "text"));
  if (title !== null && requireString(title, "title") !== "") {
    return `sha256:${sha256Hex(`${nfc(title)}\u001f${body}`)}`;
  }
  return `sha256:${sha256Hex(body)}`;
}
