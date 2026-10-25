// A18: provenance on data messages, none on control messages, and the deletion, decision and DLQ
// cases (ADR-0003; F-08, F-14, F-42).
import { describe, expect, it } from "vitest";
import { CATALOGUE } from "../../src/catalogue.ts";
import { decisionRow, decisionRows, type DecisionQuery } from "../../src/registries/index.ts";
import { validate } from "../../src/validate.ts";
import {
  copyOf,
  fixture,
  fixtures,
  samePath,
  schemaDirs,
  schemaIdOf,
  type Fixture,
} from "../helpers.ts";

type Json = Record<string, unknown>;
const dirOf = new Map(schemaDirs().map((d) => [schemaIdOf(d), d]));
const failsAt = (r: ReturnType<typeof validate>, path: (string | number)[]): boolean =>
  !r.ok && r.issues.some((i) => samePath(i.path, path));

// A data message of each data schema that carries provenance (the item scope of deletions/v1).
const SAMPLE: Record<string, string> = {
  "deletions/v1": "prd-retention-purger.json",
  "registry.decisions/v1": "prd-qualifier.json",
};

describe("provenance (ADR-0003, A18)", () => {
  it("every data schema requires provenance and retention_class", () => {
    for (const { id } of CATALOGUE.filter((e) => e.class === "data")) {
      const dir = dirOf.get(id) ?? "";
      const sample = SAMPLE[id];
      const f = sample ? fixture(dir, "valid", sample) : fixtures(dir, "valid")[0];
      if (!f) throw new Error(`no fixture for ${id}`);
      const prefix = id === "raw.items/v1" ? ["envelope"] : [];
      for (const name of ["provenance", "retention_class"]) {
        const value = copyOf(f);
        delete (prefix.length ? (value.envelope as Json) : value)[name];
        expect(
          failsAt(validate(id, value, "producer", f.options), [...prefix, name]),
          `${id} ${name}`,
        ).toBe(true);
      }
    }
  });

  it("no control schema accepts provenance", () => {
    const provenance = {
      route: "green",
      vendor: null,
      service: "fb-page-feed-poller",
      fetched_at: "2026-10-06T09:13:58Z",
    };
    for (const id of ["source.events/v1", "jobs.completed/v1", "job/v1"]) {
      const f = fixtures(dirOf.get(id) ?? "", "valid")[0];
      if (!f) throw new Error(`no fixture for ${id}`);
      const value = { ...copyOf(f), provenance };
      for (const mode of ["producer", "consumer"] as const) {
        expect(failsAt(validate(id, value, mode, f.options), ["provenance"]), `${id} ${mode}`).toBe(
          true,
        );
      }
    }
  });

  it("a non-item deletion rejects retention_class", () => {
    for (const file of [
      "author-request.json",
      "source-authorization-revoked.json",
      "client-offboarding.json",
    ]) {
      const f = fixture("deletions/v1", "valid", file);
      const value = { ...copyOf(f), retention_class: "x_24h_sync" };
      expect(failsAt(validate("deletions/v1", value), ["retention_class"]), file).toBe(true);
    }
  });

  it("a non-item deletion whose signal is no fetch accepts null route and vendor (F-08)", () => {
    for (const file of ["author-request.json", "client-offboarding.json", "client-request.json"]) {
      const f = fixture("deletions/v1", "valid", file);
      const prov = (f.value as Json).provenance as Json;
      expect([prov.route, prov.vendor], file).toEqual([null, null]);
      expect(validate("deletions/v1", f.value).ok, file).toBe(true);
    }
    // A signal that is a platform fetch names its route.
    const revoked = copyOf(fixture("deletions/v1", "valid", "source-authorization-revoked.json"));
    (revoked.provenance as Json).route = null;
    expect(failsAt(validate("deletions/v1", revoked), ["provenance", "route"])).toBe(true);
  });

  it("each registry.decisions row requires or refuses provenance as the producer rows say (F-14)", () => {
    const exercised = new Set<number>();
    const rows = decisionRows();
    for (const f of fixtures("registry.decisions/v1", "valid")) {
      const m = f.value as Json;
      const subject = (
        ["candidate_key", "author_ref", "source_id", "keyword_id", "platform"] as const
      ).find((s) => m[s] !== undefined);
      if (!subject) throw new Error(`${f.name} has no subject`);
      const block = m[m.decision as string] as Json | undefined;
      const q: DecisionQuery = {
        decision: m.decision as string,
        subject,
        reason: m.reason as string | null,
        health: block?.health as string | undefined,
      };
      const row = decisionRow(q, (m.producer as Json).service as string);
      expect(row, f.name).not.toBeNull();
      if (!row) continue;
      exercised.add(rows.findIndex((r) => JSON.stringify(r) === JSON.stringify(row)));
      const without = copyOf(f);
      delete without.provenance;
      delete without.retention_class;
      const withIt: Json = {
        ...copyOf(f),
        provenance: {
          route: "green",
          vendor: null,
          service: "ig-account-resolver",
          fetched_at: "2026-10-06T10:13:58Z",
        },
        retention_class: "meta_on_request",
      };
      const r1 = validate("registry.decisions/v1", without);
      const r2 = validate("registry.decisions/v1", withIt);
      if (row.provenance === "required") expect(failsAt(r1, ["provenance"]), f.name).toBe(true);
      if (row.provenance === "refused") expect(failsAt(r2, ["provenance"]), f.name).toBe(true);
      if (row.provenance === "optional") expect([r1.ok, r2.ok], f.name).toEqual([true, true]);
    }
    const unexercised = rows
      .map((r, i) => (exercised.has(i) ? null : r.from))
      .filter((x) => x !== null);
    expect(unexercised, "every decision row has a valid fixture").toEqual([]);
  });

  it("the n8n notices accept no provenance", () => {
    const provenance = {
      route: "green",
      vendor: null,
      service: "quota-governor",
      fetched_at: "2026-10-04T08:12:00Z",
    };
    for (const [id, file] of [
      ["n8n.alert/v1", "facts-budget.json"],
      ["n8n.card/v1", "qualifier-review.json"],
    ] as const) {
      const f = fixture(id, "valid", file);
      for (const mode of ["producer", "consumer"] as const) {
        expect(
          failsAt(validate(id, { ...copyOf(f), provenance }, mode, f.options), ["provenance"]),
          `${id} ${mode}`,
        ).toBe(true);
      }
    }
  });

  it("an n8n alert accepts no item text, author_ref or handle (F-51)", () => {
    const f = fixture("n8n.alert/v1", "valid", "facts-budget.json");
    for (const [path, v] of [
      [["text"], "النت منقطع"],
      [["author_ref"], "a".repeat(64)],
      [["subject", "handle"], "abuali_basra"],
    ] as const) {
      const value = copyOf(f);
      const holder = (path.length === 2 ? value.subject : value) as Json;
      holder[path[path.length - 1] as string] = v;
      expect(failsAt(validate("n8n.alert/v1", value), [...path]), path.join(".")).toBe(true);
    }
  });

  it("a dead letter copies provenance and retention_class from a parsed data message (F-42)", () => {
    const f: Fixture = fixture("dlq/v1", "valid", "consume-data-message.json");
    expect(validate("dlq.<service>/v1", f.value).ok).toBe(true);
    const changed = copyOf(f);
    (changed.provenance as Json).service = "x-recent-search";
    expect(failsAt(validate("dlq.<service>/v1", changed), ["provenance"])).toBe(true);
    const raw = fixture("dlq/v1", "valid", "consume-unparsed.json");
    expect((raw.value as Json).provenance).toBeUndefined();
    expect(validate("dlq.<service>/v1", raw.value).ok).toBe(true);
  });
});
