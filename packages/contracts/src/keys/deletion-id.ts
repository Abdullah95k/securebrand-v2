// deletion_id (ADR-0035; Q2, decided by the user): who or what is deleted, the kind of deletion and
// the day the signal arrived, so every separate request is carried out and only an exact repeat of
// the same message keeps its id.
import { canonicalJson } from "../canonical-json.ts";
import { ContractError } from "../errors.ts";
import { PATTERNS } from "../primitives.ts";
import {
  DELETION_MODES,
  DELETION_REASONS,
  DELETION_SCOPES,
  type DeletionMode,
  type DeletionReason,
  type DeletionScope,
} from "../vocabulary.ts";
import { compareCodePoints, requireString, sha256Hex } from "./text.ts";
import { messageTimeMillis } from "./time.ts";

export interface DeletionIdInput {
  reason: DeletionReason;
  scope: DeletionScope;
  /** The scope's top-level key: author_ref, source_id or client_id; the item's source_id for items. */
  key: string;
  mode: DeletionMode;
  signal_at: string;
  target: Readonly<Record<string, string | readonly string[]>>;
}

export function deletionId(input: DeletionIdInput): string {
  if (!(DELETION_REASONS as readonly string[]).includes(input.reason)) throw new ContractError("bad_reason", input.reason);
  if (!(DELETION_SCOPES as readonly string[]).includes(input.scope)) throw new ContractError("bad_scope", input.scope);
  if (!(DELETION_MODES as readonly string[]).includes(input.mode)) throw new ContractError("bad_mode", input.mode);
  const keyPattern = input.scope === "author" ? PATTERNS.sha256Hex : PATTERNS.uuid;
  if (!keyPattern.test(requireString(input.key, "key"))) {
    throw new ContractError("bad_key", `${input.scope} scope takes ${input.scope === "author" ? "an author_ref" : "a UUID"}`);
  }
  messageTimeMillis(requireString(input.signal_at, "signal_at"));
  const target: Record<string, string | string[]> = {};
  for (const [name, value] of Object.entries(input.target)) {
    if (typeof value === "string") target[name] = value;
    else if (Array.isArray(value)) target[name] = value.map((v, i) => requireString(v, `${name}[${i}]`)).sort(compareCodePoints);
    else throw new ContractError("bad_target", `${name} must be a string or an array of strings`);
  }
  const text = canonicalJson({ key: input.key, mode: input.mode, signal_day: input.signal_at.slice(0, 10), target });
  return `del:${input.reason}:${input.scope}:${sha256Hex(text)}`;
}
