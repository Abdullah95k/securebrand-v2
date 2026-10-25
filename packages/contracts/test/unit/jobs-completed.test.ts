// jobs.completed/v1's rules that read registry data (note 11, D-9): always in producer mode, and in
// consumer mode only for a service the package knows, so a report from a service that a newer
// package adds inside the version is not refused.
import { describe, expect, it } from "vitest";
import { validate } from "../../src/validate.ts";
import { copyOf, fixture } from "../helpers.ts";

type Json = Record<string, unknown>;

function reportOf(file: string, service: string): Json {
  const m = copyOf(fixture("jobs.completed/v1", "valid", file));
  return { ...m, producer: { ...(m.producer as Json), service }, queue: `jobs.${service}` };
}

describe("jobs.completed/v1 from a service the package does not know (D-9)", () => {
  it("accepts in consumer mode a new X service's report carrying paid_user_reads", () => {
    // gap_unfilled is the X gap job's own field, checked by its queue name, not the registry.
    const report = reportOf("done-x-gap.json", "x-newsvc");
    delete report.gap_unfilled;
    expect(validate("jobs.completed/v1", report, "consumer").ok).toBe(true);
    const r = validate("jobs.completed/v1", report, "producer");
    expect(r.ok ? [] : r.issues.map((i) => i.code)).toContain("x_field");
  });

  it("accepts in consumer mode a report keyed by crawl_id on a new service's queue", () => {
    const report = reportOf("done-commoncrawl-rotation.json", "web-newscanner");
    expect(validate("jobs.completed/v1", report, "consumer").ok).toBe(true);
    const r = validate("jobs.completed/v1", report, "producer");
    expect(r.ok ? [] : r.issues.map((i) => i.code)).toContain("missing_key");
  });

  it("still checks a known service's report in consumer mode", () => {
    const report = { ...copyOf(fixture("jobs.completed/v1", "valid", "done-rotation.json")) };
    report.paid_user_reads = 3;
    const r = validate("jobs.completed/v1", report, "consumer");
    expect(r.ok ? [] : r.issues.map((i) => i.code)).toContain("x_field");
  });
});
