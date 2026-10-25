// A1: every schema id has a Zod schema, a committed JSON Schema and a generated Python model.
import { existsSync, readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { CATALOGUE, schemaFor } from "../../src/catalogue.ts";
import { SCHEMAS_DIR, pythonModule, schemaFile } from "../../src/export.ts";
import { PACKAGE_DIR } from "../helpers.ts";

// The schema ids the plan's "Contracts" section lists (n8n.alert/v1 and n8n.card/v1 come with A30).
const IDS = [
  "raw.items/v1",
  "items.normalized/v1",
  "item.hits/v1",
  "discovery.hits/v1",
  "poster.profiles/v1",
  "registry.decisions/v1",
  "source.events/v1",
  "items.analysis/v1",
  "item.metrics/v1",
  "deletions/v1",
  "article.urls/v1",
  "search.results/v1",
  "crawl.policies/v1",
  "news.dedup/v1",
  "jobs.completed/v1",
  "job/v1",
  "dlq.<service>/v1",
];

describe("the catalogue (ADR-0002, ADR-0030, A1)", () => {
  it("every schema id in the catalogue has a Zod schema, a committed JSON Schema and a generated Python model", () => {
    expect(CATALOGUE.map((e) => e.id)).toEqual(expect.arrayContaining(IDS));
    for (const { id } of CATALOGUE) {
      expect(schemaFor(id, "producer"), id).toBeDefined();
      expect(schemaFor(id, "consumer"), id).toBeDefined();
      expect(
        existsSync(`${SCHEMAS_DIR}${schemaFile(id)}`),
        `${id}: schemas/${schemaFile(id)}`,
      ).toBe(true);
      for (const mode of ["strict", "consumer"]) {
        const file = `${PACKAGE_DIR}python/listening_contracts/models/${mode}/${pythonModule(id)}.py`;
        expect(existsSync(file), `${id}: ${file}`).toBe(true);
        expect(readFileSync(file, "utf8"), file).toContain(
          `extra="${mode === "strict" ? "forbid" : "ignore"}"`,
        );
      }
    }
  });

  it("names every schema file and Python module after its schema id, dlq.<service>/v1 as dlq/v1", () => {
    expect(schemaFile("raw.items/v1")).toBe("raw.items/v1.json");
    expect(schemaFile("dlq.<service>/v1")).toBe("dlq/v1.json");
    expect(pythonModule("raw.items/v1")).toBe("raw_items_v1");
    expect(pythonModule("dlq.<service>/v1")).toBe("dlq_v1");
  });
});
