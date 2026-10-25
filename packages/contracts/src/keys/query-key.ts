// query_key (ADR-0044; Q10): a hash of a keyword's forms and context terms, normalised under the
// row's platform folding profile, set on save. No folding service is called, so both languages agree.
import { canonicalJson } from "../canonical-json.ts";
import { ContractError } from "../errors.ts";
import { loadRegistry } from "../registries/load.ts";
import { PLATFORMS, type Platform } from "../vocabulary.ts";
import { compareCodePoints, lowerCase, nfc, requireString, sha256Hex } from "./text.ts";

export type FoldingProfile = "exact" | "folded";

const profiles = (
  loadRegistry("query-folding.json") as { profiles: Record<string, FoldingProfile> }
).profiles;

const TATWEEL = 0x0640;
const isTashkeel = (cp: number): boolean => (cp >= 0x064b && cp <= 0x065f) || cp === 0x0670;
const FOLD: ReadonlyMap<number, number> = new Map([
  [0x0623, 0x0627],
  [0x0625, 0x0627],
  [0x0622, 0x0627],
  [0x0629, 0x0647],
  [0x0649, 0x064a],
  [0x06a9, 0x0643],
  [0x06cc, 0x064a],
]);

export function foldingProfile(platform: Platform): FoldingProfile {
  if (!(PLATFORMS as readonly string[]).includes(platform))
    throw new ContractError("bad_platform", platform);
  const profile = profiles[platform];
  if (profile !== "exact" && profile !== "folded")
    throw new ContractError("bad_registry", `no profile for ${platform}`);
  return profile;
}

export function normaliseQueryText(profile: FoldingProfile, text: string): string {
  const lowered = lowerCase(nfc(requireString(text, "form")));
  if (profile === "exact") return lowered;
  let out = "";
  for (const ch of lowered) {
    const cp = ch.codePointAt(0) ?? 0;
    if (cp === TATWEEL || isTashkeel(cp)) continue;
    out += String.fromCodePoint(FOLD.get(cp) ?? cp);
  }
  return out;
}

function normaliseList(profile: FoldingProfile, texts: readonly string[], what: string): string[] {
  const set = new Set<string>();
  for (const text of texts) {
    const n = normaliseQueryText(profile, text);
    if (n === "") throw new ContractError("bad_keyword", `an empty ${what}`);
    set.add(n);
  }
  return [...set].sort(compareCodePoints);
}

export function queryKeyWithProfile(
  profile: FoldingProfile,
  forms: readonly string[],
  contextTerms: readonly string[],
): string {
  if (profile !== "exact" && profile !== "folded")
    throw new ContractError("bad_profile", String(profile));
  if (forms.length === 0)
    throw new ContractError("bad_keyword", "a keyword needs at least one form");
  const value = {
    context_terms: normaliseList(profile, contextTerms, "context term"),
    forms: normaliseList(profile, forms, "form"),
  };
  return sha256Hex(canonicalJson(value));
}

export function queryKey(
  platform: Platform,
  forms: readonly string[],
  contextTerms: readonly string[],
): string {
  return queryKeyWithProfile(foldingProfile(platform), forms, contextTerms);
}
