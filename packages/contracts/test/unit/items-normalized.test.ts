// A26: items.normalized/v1 (ADR-0005, ADR-0031, ADR-0059, ADR-0068, ADR-0070).
import { describe, expect, it } from "vitest";
import { validate } from "../../src/validate.ts";
import { copyOf, fixture, samePath } from "../helpers.ts";

type Json = Record<string, unknown>;
const ID = "items.normalized/v1";
const failsAt = (r: ReturnType<typeof validate>, path: (string | number)[]): boolean =>
  !r.ok && r.issues.some((i) => samePath(i.path, path));

describe("items.normalized/v1 (A26)", () => {
  it("rejects author_followers without author_source_id", () => {
    const value = copyOf(fixture(ID, "valid", "post-poster-not-yet-classed.json"));
    (value.author as Json).author_followers = 1200;
    expect(failsAt(validate(ID, value), ["author", "author_followers"])).toBe(true);
    const source = copyOf(fixture(ID, "valid", "prd-normalize-item.json"));
    (source.author as Json).author_followers = 412000;
    expect(validate(ID, source).ok).toBe(true);
  });

  it("carries job_kind, lang_pending and sensitive_event on every item", () => {
    for (const name of ["job_kind", "lang_pending", "sensitive_event"]) {
      const value = copyOf(fixture(ID, "valid", "prd-normalize-item.json"));
      delete value[name];
      expect(failsAt(validate(ID, value), [name]), name).toBe(true);
    }
  });

  it("accepts text_full_ref and usage_signals on an article", () => {
    const value = fixture(ID, "valid", "article.json").value as Json;
    expect(value.text_full_ref).toBeDefined();
    expect(value.usage_signals).toBeDefined();
    expect(validate(ID, value).ok).toBe(true);
  });

  it("accepts the transient poster_platform_id only for a poster not yet classed (ADR-0031)", () => {
    expect(validate(ID, fixture(ID, "valid", "post-poster-not-yet-classed.json").value).ok).toBe(
      true,
    );
    const value = copyOf(fixture(ID, "valid", "prd-normalize-item.json"));
    value.poster_platform_id = "1234567890";
    expect(failsAt(validate(ID, value), ["poster_platform_id"])).toBe(true);
  });
});
