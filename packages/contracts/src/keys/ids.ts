// Deterministic ids: uuid v5 under frozen namespaces (ADR-0006), and the analysis key (ADR-0023).
import { ContractError } from "../errors.ts";
import { PATTERNS } from "../primitives.ts";
import { CARD_TYPES } from "../vocabulary.ts";
import { parseKey } from "./idempotency.ts";
import { nfc, requireString } from "./text.ts";
import { uuidV5 } from "./uuid.ts";

// Frozen in v1: changing one changes every id derived from it (VERSIONING.md).
export const NS_ITEMS = "b0eeaa44-bf4b-4c44-b977-bb8c9485f06e";
export const NS_HITS = "889d9f7d-7cd6-4556-8f5e-3cebf0938434";
export const NS_CARDS = "68861d52-0265-403a-a35d-493238d31f4b";

function requireUuid(value: string, what: string): string {
  if (!PATTERNS.uuid.test(requireString(value, what))) throw new ContractError("bad_uuid", `${what} ${value}`);
  return value;
}

/** item_id = uuid_v5(ns_items, key), the key taken in its NFC form. */
export function itemId(key: string): string {
  const k = nfc(requireString(key, "key"));
  parseKey(k);
  return uuidV5(NS_ITEMS, k);
}

/** hit_id = uuid_v5(ns_hits, "<item_id>:<client_id>:<keyword_id>") (keyword-matcher §5.3 L77). */
export function hitId(itemIdValue: string, clientId: string, keywordId: string): string {
  return uuidV5(
    NS_HITS,
    `${requireUuid(itemIdValue, "item_id")}:${requireUuid(clientId, "client_id")}:${requireUuid(keywordId, "keyword_id")}`,
  );
}

/** card_id = uuid_v5(ns_cards, "<card_type>:<subject key>:<decision_id or request_id>") (Q11, F-47). */
export function cardId(cardType: string, subjectKey: string, ref: string): string {
  if (!(CARD_TYPES as readonly string[]).includes(cardType)) throw new ContractError("bad_card_type", cardType);
  if (!PATTERNS.token.test(requireString(subjectKey, "subject key"))) throw new ContractError("bad_subject", subjectKey);
  if (!PATTERNS.ulid.test(requireString(ref, "ref"))) throw new ContractError("bad_ulid", `ref ${ref}`);
  return uuidV5(NS_CARDS, `${cardType}:${subjectKey}:${ref}`);
}

/** `<item_id>:<task>:<model_version>`; task and model version hold no colon (ADR-0023). */
export function analysisKey(itemIdValue: string, task: string, modelVersion: string): string {
  requireUuid(itemIdValue, "item_id");
  if (!PATTERNS.analysisTask.test(requireString(task, "task"))) throw new ContractError("bad_task", task);
  if (!PATTERNS.modelVersion.test(requireString(modelVersion, "model_version"))) {
    throw new ContractError("bad_model_version", modelVersion);
  }
  return `${itemIdValue}:${task}:${modelVersion}`;
}
