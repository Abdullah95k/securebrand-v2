// Edge inputs (review note 17, D-5): validate() returns issues and never throws on any JSON input,
// and a registry lookup by a name that is an Object property finds nothing.
import { describe, expect, it } from "vitest";
import {
  declaredContextKeys,
  declaredExtrasKeys,
  isAllowedTopicWriter,
  partitionKey,
  rawItemsKinds,
  visibilityOf,
  visibilityRule,
} from "../../src/registries/index.ts";
import { validate } from "../../src/validate.ts";
import { copyOf, fixture } from "../helpers.ts";

type Json = Record<string, unknown>;
const issuesOf = (r: ReturnType<typeof validate>): [unknown, string][] =>
  r.ok ? [] : r.issues.map((i) => [i.path, i.code]);

/** `levels` arrays, one inside the other. */
function nested(levels: number): unknown[] {
  let value: unknown[] = [];
  for (let i = 1; i < levels; i += 1) value = [value];
  return value;
}

describe("edge inputs (note 17, D-5)", () => {
  it("names a producer called constructor an unknown service, and does not throw", () => {
    const raw = copyOf(fixture("raw.items/v1", "valid", "metrics.json"));
    const envelope = raw.envelope as Json;
    envelope.producer = { ...(envelope.producer as Json), service: "constructor" };
    expect(issuesOf(validate("raw.items/v1", raw, "producer"))).toEqual([
      [["envelope", "producer", "service"], "unknown_service"],
    ]);
    const profile = copyOf(fixture("poster.profiles/v1", "valid", "prd-fb-page-resolver.json"));
    (profile.provenance as Json).service = "constructor";
    expect(issuesOf(validate("poster.profiles/v1", profile, "producer"))).toContainEqual([
      ["provenance", "service"],
      "unknown_service",
    ]);
  });

  it("finds no registry entry under a name that is an Object property", () => {
    for (const id of ["toString", "constructor"])
      expect(() => partitionKey(id, {}), id).toThrow(/unknown_schema/);
    expect(declaredExtrasKeys("constructor")).toBeNull();
    expect(rawItemsKinds("constructor")).toBeNull();
    expect(visibilityRule("constructor")).toBeNull();
    expect(visibilityOf("toString", true)).toBeNull();
    expect(declaredContextKeys("constructor", "constructor")).toEqual({ keys: [], required: [] });
    expect(isAllowedTopicWriter("constructor", "fb-page-feed-poller")).toBe(false);
  });

  it("refuses a non-finite number, a value nested past 64 levels and a __proto__ key", () => {
    const base = copyOf(fixture("raw.items/v1", "valid", "prd-fb-page-feed-poller.json"));
    const payload = base.payload as Json;
    for (const n of [Infinity, -Infinity, NaN]) {
      const value = { ...base, payload: { ...payload, like_count: n } };
      expect(issuesOf(validate("raw.items/v1", value, "consumer")), String(n)).toEqual([
        [["payload", "like_count"], "not_json"],
      ]);
    }
    const deep = { ...base, payload: { ...payload, attachments: nested(64) } };
    expect(issuesOf(validate("raw.items/v1", deep, "consumer"))).toEqual([
      [["payload", "attachments", ...Array<number>(63).fill(0)], "not_json"],
    ]);
    const proto = JSON.parse('{"__proto__": {"x": 1}, "id": "1"}') as Json;
    const withProto = { ...base, payload: { ...payload, extra: proto } };
    expect(issuesOf(validate("raw.items/v1", withProto, "consumer"))).toEqual([
      [["payload", "extra", "__proto__"], "not_json"],
    ]);
  });

  it("returns issues for a value nested 255 levels deep, anywhere, and never throws", () => {
    const base = copyOf(fixture("raw.items/v1", "valid", "prd-fb-page-feed-poller.json"));
    const values = [
      { ...base, payload: { ...(base.payload as Json), attachments: nested(255) } },
      { ...base, extra: nested(255) },
    ];
    for (const value of values) {
      for (const mode of ["producer", "consumer"] as const) {
        expect(() => validate("raw.items/v1", value, mode), mode).not.toThrow();
        expect(validate("raw.items/v1", value, mode).ok).toBe(false);
      }
    }
  });
});
