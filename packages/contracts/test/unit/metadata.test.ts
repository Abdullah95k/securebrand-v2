// A17: the four metadata fields on every message (ADR-0002), and the version classifier.
import { describe, expect, it } from "vitest";
import { CATALOGUE } from "../../src/catalogue.ts";
import { validate } from "../../src/validate.ts";
import { classifyVersion } from "../../src/versions.ts";
import { copyOf, fixtures, samePath, schemaDirs, schemaIdOf } from "../helpers.ts";

const FIELDS = ["schema", "message_id", "produced_at", "producer"] as const;
const dirOf = new Map(schemaDirs().map((d) => [schemaIdOf(d), d]));

describe("message metadata (ADR-0002, A17)", () => {
  it("every message schema requires the four fields", () => {
    for (const { id } of CATALOGUE) {
      const dir = dirOf.get(id);
      expect(dir, id).toBeDefined();
      const [f] = fixtures(dir ?? "", "valid");
      expect(f, id).toBeDefined();
      if (!f) continue;
      // raw.items carries the metadata in its envelope (ADR-0005).
      const prefix = id === "raw.items/v1" ? ["envelope"] : [];
      for (const name of FIELDS) {
        const value = copyOf(f);
        const holder = (prefix.length ? value.envelope : value) as Record<string, unknown>;
        delete holder[name];
        const r = validate(id, value, "producer", f.options);
        expect(r.ok, `${id} without ${name}`).toBe(false);
        if (!r.ok)
          expect(
            r.issues.some((i) => samePath(i.path, [...prefix, name])),
            `${id} ${name}`,
          ).toBe(true);
      }
      const named = fixtures(dir ?? "", "invalid").filter((x) => x.file.startsWith("no-metadata-"));
      expect(named.length, `${id}: the four no-metadata-* fixtures`).toBe(4);
    }
  });

  it("refuses a producer without its service, version or job", () => {
    const f = fixtures("item.hits/v1", "valid")[0];
    if (!f) throw new Error("no item.hits fixture");
    for (const name of ["service", "version", "job_id"]) {
      const value = copyOf(f);
      delete (value.producer as Record<string, unknown>)[name];
      expect(validate("item.hits/v1", value).ok, name).toBe(false);
    }
  });

  it("classifies a known-unread version as skip and an unknown one as park", () => {
    expect(classifyVersion("raw.items/v1", ["raw.items/v1"])).toBe("read");
    expect(classifyVersion("item.hits/v1", ["raw.items/v1"])).toBe("skip");
    expect(classifyVersion("raw.items/v2", ["raw.items/v1"])).toBe("park");
    expect(classifyVersion("job/v2", ["job/v1"])).toBe("park");
    // dlq.<service>/v1 is one schema id whatever the service (F-52).
    expect(classifyVersion("dlq.store-writer/v1", ["dlq.<service>/v1"])).toBe("read");
    expect(classifyVersion("dlq.normalize-item/v1", ["raw.items/v1"])).toBe("skip");
    expect(classifyVersion("dlq.normalize-item/v2", ["raw.items/v1"])).toBe("park");
  });
});
