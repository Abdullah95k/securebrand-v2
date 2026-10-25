import { describe, expect, it } from "vitest";
import { canonicalJson } from "../../src/canonical-json.ts";
import { golden } from "../helpers.ts";

interface CanonicalJsonGolden {
  values: { name: string; value: unknown; canonical: string }[];
  numbers: { json: string; canonical: string }[];
}

const g = golden<CanonicalJsonGolden>("canonical-json.json");

describe("canonical JSON (RFC 8785)", () => {
  it.each(g.values.map((c) => [c.name, c] as const))(
    "canonical JSON of every golden structure is byte-identical: %s",
    (_n, c) => {
      expect(canonicalJson(c.value)).toBe(c.canonical);
    },
  );

  it("key order by UTF-16 code units, escapes, integers and floats as RFC 8785 renders them", () => {
    for (const c of g.numbers) expect(canonicalJson(JSON.parse(c.json) as unknown)).toBe(c.canonical);
  });

  it("refuses values JSON cannot carry", () => {
    expect(() => canonicalJson(Number.NaN)).toThrow();
    expect(() => canonicalJson(Number.POSITIVE_INFINITY)).toThrow();
    expect(() => canonicalJson({ a: undefined })).toThrow();
  });
});
