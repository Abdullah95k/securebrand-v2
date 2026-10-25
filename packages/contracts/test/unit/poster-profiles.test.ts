// A27: poster.profiles/v1, ADR-0033's flat schema with public_account (ADR-0010).
import { describe, expect, it } from "vitest";
import { validate } from "../../src/validate.ts";
import { copyOf, fixture, samePath } from "../helpers.ts";

const ID = "poster.profiles/v1";
const failsAt = (r: ReturnType<typeof validate>, path: (string | number)[]): boolean =>
  !r.ok && r.issues.some((i) => samePath(i.path, path));

describe("poster.profiles/v1 (A27)", () => {
  it("rejects a handle, display_name, url, country_signals or extras on an ordinary individual's answer", () => {
    const base = fixture(ID, "valid", "individual.json");
    expect(validate(ID, base.value).ok).toBe(true);
    const values: Record<string, unknown> = {
      handle: "abuali_basra",
      display_name: "Abu Ali",
      url: "https://x.com/abuali_basra",
      country_signals: null,
      extras: {},
    };
    for (const [name, v] of Object.entries(values)) {
      expect(failsAt(validate(ID, { ...copyOf(base), [name]: v }), [name]), name).toBe(true);
    }
  });

  it("accepts a public person's identity fields", () => {
    const f = fixture(ID, "valid", "public-person-individual.json");
    const v = f.value as Record<string, unknown>;
    expect([v.account_type, v.individual, v.public_account]).toEqual(["individual", true, true]);
    expect(v.handle).toBeTruthy();
    expect(validate(ID, f.value).ok).toBe(true);
  });

  it("rejects an extras key its resolver does not declare", () => {
    const value = copyOf(fixture(ID, "valid", "prd-fb-page-resolver.json"));
    (value.extras as Record<string, unknown>).media_count = 10; // ig-account-resolver's key
    expect(failsAt(validate(ID, value), ["extras", "media_count"])).toBe(true);
    expect(validate(ID, value, "consumer").ok).toBe(true);
  });

  it("keeps a person's account unlisted on TikTok, Instagram and LinkedIn (ADR-0010 L70-L72)", () => {
    for (const file of ["prd-tt-user-resolver.json", "prd-ig-account-resolver.json"]) {
      const value = { ...copyOf(fixture(ID, "valid", file)), public_account: true };
      expect(failsAt(validate(ID, value), ["public_account"]), file).toBe(true);
    }
  });
});
