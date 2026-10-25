import { describe, expect, it } from "vitest";
import {
  jobKeyFields,
  partitionKey,
  producerRows,
  topicKeyFields,
  topicWriters,
} from "../../src/registries/index.ts";
import { golden } from "../helpers.ts";

interface KeyCase {
  name: string;
  schema: string;
  queue?: string;
  message: Record<string, unknown>;
  key?: string;
}
const g = golden<{ cases: KeyCase[]; refusals: KeyCase[] }>("partition-keys.json");

describe("partition keys (ADR-0004, A19)", () => {
  it("every topic and queue has one declared key", () => {
    for (const schema of Object.keys(topicWriters())) {
      if (schema === "jobs.completed/v1") continue; // the key of the job it reports
      expect(topicKeyFields(schema), schema).not.toBeNull();
    }
    expect(topicKeyFields("registry.decisions/v1")).toEqual([
      "candidate_key",
      "author_ref",
      "source_id",
      "platform",
      "keyword_id",
    ]);
    for (const row of producerRows()) {
      expect(jobKeyFields(row.queue, row.kind).length, `${row.queue} ${row.kind}`).toBeGreaterThan(
        0,
      );
    }
  });

  it.each(g.cases.map((c) => [c.name, c] as const))(
    "returns the key of every golden message: %s",
    (_n, c) => {
      expect(
        partitionKey(c.schema, c.message, c.queue === undefined ? {} : { queue: c.queue }),
      ).toBe(c.key);
    },
  );

  it.each(g.refusals.map((c) => [c.name, c] as const))(
    "refuses a message with no key: %s",
    (_n, c) => {
      expect(() =>
        partitionKey(c.schema, c.message, c.queue === undefined ? {} : { queue: c.queue }),
      ).toThrow();
    },
  );
});
