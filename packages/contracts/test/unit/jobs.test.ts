// A21: job/v1, one envelope with a closed kind list (ADR-0011, ADR-0057, ADR-0060, ADR-0064, ADR-0065).
import { describe, expect, it } from "vitest";
import { validate } from "../../src/validate.ts";
import { JOB_KINDS } from "../../src/vocabulary.ts";
import { copyOf, fixture, fixtures, samePath } from "../helpers.ts";

const ID = "job/v1";
const VALID = fixtures(ID, "valid");
const failsAt = (r: ReturnType<typeof validate>, path: (string | number)[]): boolean =>
  !r.ok && r.issues.some((i) => samePath(i.path, path));

describe("job/v1 (ADR-0011, A21)", () => {
  it("accepts every kind with its declared fields", () => {
    for (const kind of JOB_KINDS) {
      const own = VALID.filter((f) => (f.value as { kind: string }).kind === kind);
      expect(own.length, `a valid ${kind} job`).toBeGreaterThan(0);
      for (const f of own) {
        expect(f.options.queue, `${f.name} names its queue`).toBeDefined();
        const r = validate(ID, f.value, "producer", f.options);
        expect(r.ok ? [] : r.issues, f.name).toEqual([]);
      }
    }
  });

  it("rejects a job carrying priority, route or vendor", () => {
    const f = fixture(ID, "valid", "rotation.json");
    for (const [name, value] of [
      ["priority", 1],
      ["route", "green"],
      ["vendor", null],
    ] as const) {
      expect(
        failsAt(validate(ID, { ...copyOf(f), [name]: value }, "producer", f.options), [name]),
        name,
      ).toBe(true);
    }
  });

  it("rejects a reason used as the type", () => {
    const f = fixture(ID, "valid", "prd-backfill-orchestrator.json");
    for (const reason of ["first_run", "gap_backfill", "seed", "weekly", "refresh_24h", "health"]) {
      expect(
        failsAt(validate(ID, { ...copyOf(f), kind: reason }, "producer", f.options), ["kind"]),
        reason,
      ).toBe(true);
    }
  });

  it("rejects an analyze job carrying item or provenance (Q6)", () => {
    const f = fixture(ID, "valid", "analyze-priority.json");
    const item = { ...copyOf(f), item: { text: "النت منقطع" } };
    expect(failsAt(validate(ID, item, "producer", f.options), ["item"])).toBe(true);
    const prov = {
      ...copyOf(f),
      provenance: {
        route: "green",
        vendor: null,
        service: "fb-page-feed-poller",
        fetched_at: "2026-10-06T09:13:58Z",
      },
    };
    for (const mode of ["producer", "consumer"] as const) {
      expect(failsAt(validate(ID, prov, mode, f.options), ["provenance"]), mode).toBe(true);
    }
  });

  it("checks the producer table in both modes when the queue is given (ADR-0012)", () => {
    const f = fixture(ID, "valid", "rotation.json");
    const other = {
      ...copyOf(f),
      producer: { ...(copyOf(f).producer as object), service: "fb-backfill" },
    };
    for (const mode of ["producer", "consumer"] as const) {
      expect(failsAt(validate(ID, other, mode, f.options), ["producer", "service"]), mode).toBe(
        true,
      );
    }
    // Without the queue the row cannot be found: a producer refuses, a consumer checks the shape.
    expect(validate(ID, other, "consumer").ok).toBe(true);
  });

  it("refuses a job in producer mode without its queue, whose row it cannot check (ADR-0012)", () => {
    const f = fixture(ID, "valid", "rotation.json");
    const r = validate(ID, f.value, "producer");
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.issues.map((i) => i.code)).toEqual(["no_queue"]);
    expect(validate(ID, f.value, "consumer").ok).toBe(true);
  });
});
