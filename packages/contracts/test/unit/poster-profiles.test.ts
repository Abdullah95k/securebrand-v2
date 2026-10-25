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
      handle: "example_poster_x",
      display_name: "Abu Ali",
      url: "https://x.com/example_poster_x",
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

  // The platforms where a person kind may be listed, so only the marking rule refuses null there.
  const LISTABLE: Record<string, string> = {
    x: "prd-x-user-resolver.json",
    facebook: "prd-fb-page-resolver.json",
    youtube: "prd-yt-channel-resolver.json",
    telegram: "prd-tg-channel-resolver.json",
  };
  const STATUSES: Record<string, string | null> = {
    resolved: null,
    review: "age_gated",
    unresolvable: "not_found",
  };

  it("rejects a typed account whose public_account is null (ADR-0010 L59, ADR-0033 L26)", () => {
    for (const [platform, file] of Object.entries(LISTABLE)) {
      for (const type of ["individual", "creator"]) {
        for (const [status, reason] of Object.entries(STATUSES)) {
          const value = {
            ...copyOf(fixture(ID, "valid", file)),
            account_type: type,
            individual: type === "individual",
            public_account: null,
            status,
            reason,
          };
          for (const mode of ["producer", "consumer"] as const) {
            const r = validate(ID, value, mode);
            expect(failsAt(r, ["public_account"]), `${platform} ${type} ${status} ${mode}`).toBe(
              true,
            );
          }
        }
      }
    }
  });

  it("accepts public_account null only with account_type null", () => {
    for (const file of ["review-age-gated.json", "unresolvable-not-found.json"]) {
      const f = fixture(ID, "valid", file);
      const v = f.value as Record<string, unknown>;
      expect([v.account_type, v.individual, v.public_account], file).toEqual([null, null, null]);
      for (const mode of ["producer", "consumer"] as const)
        expect(validate(ID, f.value, mode).ok, `${file} ${mode}`).toBe(true);
      const typed = { ...copyOf(f), account_type: "page", individual: false };
      expect(failsAt(validate(ID, typed), ["public_account"]), file).toBe(true);
    }
  });
});
