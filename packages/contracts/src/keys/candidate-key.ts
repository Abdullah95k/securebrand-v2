// The four candidate key forms (ADR-0032): `<platform>:<platform_id>`, `<platform>:<handle>`,
// `facebook:group:<id>` and `news:site:<registrable domain>`. Routers map every other form first.
// A LinkedIn organisation's id is its URN (`urn:li:organization:<n>`), so a LinkedIn value may hold
// colons; on the other platforms a colon would make the form ambiguous.
import { ContractError } from "../errors.ts";
import { nfc, requireString } from "./text.ts";

const ACCOUNT_PLATFORMS = [
  "facebook",
  "instagram",
  "tiktok",
  "x",
  "linkedin",
  "telegram",
  "youtube",
] as const;
type AccountPlatform = (typeof ACCOUNT_PLATFORMS)[number];
// eslint-disable-next-line no-control-regex -- control characters are what the pattern refuses
const VALUE = /^[^\x00-\x20:]+$/;
// eslint-disable-next-line no-control-regex -- control characters are what the pattern refuses
const URN_VALUE = /^[^\x00-\x20]+$/;

function validValue(platform: AccountPlatform, value: string): boolean {
  return (platform === "linkedin" ? URN_VALUE : VALUE).test(value);
}
const DOMAIN = /^[a-z0-9-]+(\.[a-z0-9-]+)+$/;

function accountPlatform(platform: string): AccountPlatform {
  if (!(ACCOUNT_PLATFORMS as readonly string[]).includes(platform)) {
    throw new ContractError("bad_platform", `${platform} has no account candidates`);
  }
  return platform as AccountPlatform;
}

/** An id keeps its case. */
export function candidateKeyFromId(platform: string, id: string): string {
  const p = accountPlatform(platform);
  if (!validValue(p, requireString(id, "id"))) throw new ContractError("bad_candidate", id);
  return `${p}:${id}`;
}

/** A handle is stored lower case without a leading '@'. */
export function candidateKeyFromHandle(platform: string, handle: string): string {
  const p = accountPlatform(platform);
  const h = nfc(requireString(handle, "handle").replace(/^@/, "")).toLowerCase();
  if (!validValue(p, h)) throw new ContractError("bad_candidate", handle);
  return `${p}:${h}`;
}

export function facebookGroupCandidateKey(groupId: string): string {
  if (!/^[0-9]+$/.test(requireString(groupId, "group id")))
    throw new ContractError("bad_candidate", groupId);
  return `facebook:group:${groupId}`;
}

/** The registrable domain is computed by the caller: the package holds no public-suffix list. */
export function newsSiteCandidateKey(registrableDomain: string): string {
  const d = requireString(registrableDomain, "domain").toLowerCase();
  if (!DOMAIN.test(d)) throw new ContractError("bad_candidate", registrableDomain);
  return `news:site:${d}`;
}

export interface ParsedCandidateKey {
  platform: string;
  form: "account" | "group" | "site";
  value: string;
}

export function parseCandidateKey(key: string): ParsedCandidateKey {
  requireString(key, "candidate_key");
  let m = /^facebook:group:([0-9]+)$/.exec(key);
  if (m) return { platform: "facebook", form: "group", value: m[1] ?? "" };
  m = /^news:site:([a-z0-9-]+(\.[a-z0-9-]+)+)$/.exec(key);
  if (m) return { platform: "news", form: "site", value: m[1] ?? "" };
  const colon = key.indexOf(":");
  const platform = colon < 0 ? "" : key.slice(0, colon);
  const value = colon < 0 ? "" : key.slice(colon + 1);
  if (!validValue(accountPlatform(platform), value)) throw new ContractError("bad_candidate", key);
  return { platform, form: "account", value };
}
