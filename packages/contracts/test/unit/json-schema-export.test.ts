// A2: JSON Schema draft 2020-12, exported from the Zod schemas with Zod's own exporter, committed
// under schemas/ and equal to a fresh export (ADR-0030).
import { existsSync, readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { CATALOGUE } from "../../src/catalogue.ts";
import { SCHEMAS_DIR, exportArtefacts, rootTitle, schemaFile } from "../../src/export.ts";

type Json = Record<string, unknown>;

/** Every object schema (one with properties) under a JSON Schema node, with its JSON pointer. */
function objects(node: unknown, at = "#"): [string, Json][] {
  if (Array.isArray(node)) return node.flatMap((v, i) => objects(v, `${at}/${i}`));
  if (typeof node !== "object" || node === null) return [];
  const n = node as Json;
  const own: [string, Json][] = n.properties !== undefined ? [[at, n]] : [];
  return [...own, ...Object.entries(n).flatMap(([k, v]) => objects(v, `${at}/${k}`))];
}

describe("the JSON Schema export (ADR-0030, A2)", () => {
  it("the committed JSON Schemas equal a fresh export", async () => {
    const artefacts = await exportArtefacts();
    for (const [path, text] of artefacts) {
      const file = `${SCHEMAS_DIR}${path}`;
      expect(existsSync(file), `${path} is committed`).toBe(true);
      expect(
        readFileSync(file, "utf8"),
        `${path} is stale: run pnpm --filter contracts export:schemas`,
      ).toBe(text);
    }
    for (const { id } of CATALOGUE) expect(artefacts.has(schemaFile(id)), id).toBe(true);
  });

  it("every exported schema declares draft 2020-12 and additionalProperties false on every object", async () => {
    const artefacts = await exportArtefacts();
    for (const { id } of CATALOGUE) {
      const schema = JSON.parse(artefacts.get(schemaFile(id)) ?? "{}") as Json;
      expect(schema.$schema, id).toBe("https://json-schema.org/draft/2020-12/schema");
      expect(schema.title, `${id}: the root title names the Python root class`).toBe(rootTitle(id));
      const found = objects(schema);
      expect(found.length, id).toBeGreaterThan(0);
      for (const [pointer, object] of found) {
        expect(object.additionalProperties, `${id} ${pointer}`).toBe(false);
      }
    }
  });
});
