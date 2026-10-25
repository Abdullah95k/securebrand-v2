// A5: every schema and every branch of it has at least one valid and one invalid fixture. A branch is
// a value of the schema's discriminator; an invalid fixture counts for the branch its discriminator
// names, so one with an unknown value (a reason used as a job kind) counts for none.
import { describe, expect, it } from "vitest";
import { CATALOGUE } from "../../src/catalogue.ts";
import {
  ANALYSIS_FIXED_TASKS,
  COMPLETION_STATUSES,
  CONTENT_KINDS,
  DECISION_TYPES,
  DELETION_MODES,
  DELETION_SCOPES,
  DLQ_STAGES,
  EVENT_TYPES,
  EVIDENCE_TYPES,
  JOB_KINDS,
  MATCHED_BY,
  RECORD_KINDS,
} from "../../src/vocabulary.ts";
import { fixtures, schemaDirs, schemaIdOf, type FixtureKind } from "../helpers.ts";

type Json = Record<string, unknown>;
const field = (v: unknown, ...path: string[]): unknown =>
  path.reduce<unknown>((cur, k) => (cur as Json | undefined)?.[k], v);

/** Each schema's branch dimensions: a name, the expected branches, and the branch of a message. */
const DIMENSIONS: Record<string, [string, readonly string[], (m: unknown) => unknown][]> = {
  "raw.items/v1": [["record kind", RECORD_KINDS, (m) => field(m, "envelope", "kind")]],
  "items.normalized/v1": [["kind", CONTENT_KINDS, (m) => field(m, "kind")]],
  "item.hits/v1": [["matched_by", MATCHED_BY, (m) => field(m, "matched_by")]],
  "discovery.hits/v1": [["evidence_type", EVIDENCE_TYPES, (m) => field(m, "evidence_type")]],
  "poster.profiles/v1": [
    [
      "answer",
      ["individual", "profile"],
      (m) => (field(m, "candidate_key") === undefined ? "individual" : "profile"),
    ],
  ],
  "registry.decisions/v1": [
    [
      "decision type",
      [
        ...DECISION_TYPES.filter((d) => d !== "health_change"),
        "health_change:source",
        "health_change:route",
      ],
      (m) => {
        const d = field(m, "decision");
        if (d !== "health_change") return d;
        return field(m, "platform") === undefined ? "health_change:source" : "health_change:route";
      },
    ],
  ],
  "source.events/v1": [["event type", EVENT_TYPES, (m) => field(m, "event")]],
  "items.analysis/v1": [
    [
      "task",
      [...ANALYSIS_FIXED_TASKS, "topics"],
      (m) => {
        const task = field(m, "task");
        return typeof task === "string" && task.startsWith("topics.") ? "topics" : task;
      },
    ],
  ],
  "item.metrics/v1": [
    [
      "observation",
      ["refresh", "read"],
      (m) => (field(m, "observation", "label") === "refresh" ? "refresh" : "read"),
    ],
  ],
  "deletions/v1": [
    ["scope", DELETION_SCOPES, (m) => field(m, "scope")],
    ["mode", DELETION_MODES, (m) => field(m, "mode")],
  ],
  "jobs.completed/v1": [["status", COMPLETION_STATUSES, (m) => field(m, "status")]],
  "job/v1": [["kind", JOB_KINDS, (m) => field(m, "kind")]],
  "dlq.<service>/v1": [["stage", DLQ_STAGES, (m) => field(m, "stage")]],
};

const dirOf = new Map(schemaDirs().map((d) => [schemaIdOf(d), d]));

describe("fixture coverage (A5)", () => {
  it("every schema of the catalogue has a fixture directory", () => {
    for (const entry of CATALOGUE) expect(dirOf.has(entry.id), entry.id).toBe(true);
  });

  it("every schema branch has a valid and an invalid fixture", () => {
    const missing: string[] = [];
    for (const entry of CATALOGUE) {
      const dir = dirOf.get(entry.id);
      if (dir === undefined) continue;
      for (const kind of ["valid", "invalid"] as FixtureKind[]) {
        const values = fixtures(dir, kind).map((f) => f.value);
        if (values.length === 0) missing.push(`${entry.id}: no ${kind} fixture`);
        for (const [name, branches, branchOf] of DIMENSIONS[entry.id] ?? []) {
          const seen = new Set(values.map(branchOf));
          for (const b of branches)
            if (!seen.has(b)) missing.push(`${entry.id}: ${name} ${b} has no ${kind} fixture`);
        }
      }
    }
    expect(missing).toEqual([]);
  });

  it("every schema has a tolerant fixture (A32)", () => {
    for (const entry of CATALOGUE) {
      const dir = dirOf.get(entry.id);
      expect(dir === undefined ? 0 : fixtures(dir, "tolerant").length, entry.id).toBeGreaterThan(0);
    }
  });
});
