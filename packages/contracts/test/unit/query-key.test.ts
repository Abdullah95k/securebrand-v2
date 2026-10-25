import { describe, expect, it } from "vitest";
import { foldingProfile, queryKey, queryKeyWithProfile } from "../../src/keys/index.ts";
import { PLATFORMS, type Platform } from "../../src/vocabulary.ts";
import { golden } from "../helpers.ts";

interface QueryKeyGolden {
  profiles_v1: Record<Platform, "exact" | "folded">;
  keys: {
    name: string;
    profile: "exact" | "folded";
    forms: string[];
    context_terms: string[];
    canonical: string;
    query_key: string;
  }[];
  rejects: { name: string; profile: "exact" | "folded"; forms: string[]; context_terms: string[] }[];
}

const g = golden<QueryKeyGolden>("query-key.json");
const find = (profile: string, name: string): string | undefined =>
  g.keys.find((c) => c.profile === profile && c.name === name)?.query_key;

describe("query_key (ADR-0044; Q10)", () => {
  it.each(g.keys.map((c) => [`${c.profile}: ${c.name}`, c] as const))(
    "derives the golden query keys under each profile: %s",
    (_n, c) => {
      expect(queryKeyWithProfile(c.profile, c.forms, c.context_terms)).toBe(c.query_key);
    },
  );

  it("form order and NFC variants give one key", () => {
    expect(find("exact", "a keyword with handle, hashtag and context")).toBe(
      find("exact", "the same forms in another order with a decomposed form"),
    );
  });

  it("the exact profile keeps alef, teh marbuta and yeh variants apart", () => {
    expect(find("exact", "alef with hamza below")).not.toBe(find("exact", "bare alef"));
    expect(find("exact", "teh marbuta")).not.toBe(find("exact", "heh"));
    expect(find("exact", "alef maksura")).not.toBe(find("exact", "yeh"));
  });

  it("the folded profile merges them", () => {
    expect(find("folded", "alef with hamza below")).toBe(find("folded", "bare alef"));
    expect(find("folded", "teh marbuta")).toBe(find("folded", "heh"));
    expect(find("folded", "alef maksura")).toBe(find("folded", "yeh"));
    expect(find("folded", "tashkeel removed")).toBe(find("folded", "heh"));
    expect(find("folded", "tatweel removed")).toBe(find("folded", "plain zain"));
    expect(find("folded", "Persian keheh and yeh")).toBe(find("folded", "Arabic kaf and yeh"));
  });

  it("every platform starts at exact", () => {
    for (const platform of PLATFORMS) {
      expect(foldingProfile(platform)).toBe("exact");
      expect(g.profiles_v1[platform]).toBe("exact");
    }
    const c = g.keys[0];
    expect(c).toBeDefined();
    if (c) expect(queryKey("facebook", c.forms, c.context_terms)).toBe(c.query_key);
  });

  it.each(g.rejects.map((c) => [c.name, c] as const))("refuses a keyword: %s", (_n, c) => {
    expect(() => queryKeyWithProfile(c.profile, c.forms, c.context_terms)).toThrow();
  });
});
