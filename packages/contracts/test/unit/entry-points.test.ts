// The package's entry points: every path package.json exports has its source, and the root carries what a
// service calls (validate, the helpers, the registries, the n8n signing helper and the message types).
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { PACKAGE_DIR } from "../helpers.ts";

const manifest = JSON.parse(readFileSync(join(PACKAGE_DIR, "package.json"), "utf8")) as {
  exports: Record<string, { types: string; default: string }>;
};

describe("entry points", () => {
  it("every path package.json exports is built from a source file", () => {
    for (const [path, target] of Object.entries(manifest.exports)) {
      const source = target.default.replace(/^\.\/dist\//, "src/").replace(/\.js$/, ".ts");
      expect(existsSync(join(PACKAGE_DIR, source)), `${path} -> ${source}`).toBe(true);
      expect(target.types, path).toBe(target.default.replace(/\.js$/, ".d.ts"));
    }
  });

  it("the package root exports what a service calls", async () => {
    const root = (await import("../../src/index.ts")) as Record<string, unknown>;
    for (const name of [
      "validate",
      "classifyVersion",
      "catalogueId",
      "canonicalJson",
      "idempotencyKey",
      "parseKey",
      "itemId",
      "hitId",
      "cardId",
      "authorRef",
      "contentHash",
      "deletionId",
      "normaliseUrl",
      "queryKey",
      "rawRef",
      "deterministicUlid",
      "partitionKey",
      "isAllowedProducer",
      "isAllowedTopicWriter",
      "isAllowedDecisionProducer",
      "visibilityOf",
      "signN8n",
      "verifyN8n",
    ])
      expect(typeof root[name], name).toBe("function");
    expect(root.SCHEMA_IDS).toEqual(expect.arrayContaining(["raw.items/v1", "n8n.card/v1"]));
    expect(root.NS_ITEMS).toMatch(/^[0-9a-f-]{36}$/);
    expect(root.PLATFORMS).toContain("tiktok");
    expect(root.ContractError).toBeTypeOf("function");
  });

  it("the schemas entry point gives each catalogue schema in both modes", async () => {
    const { schemaFor } = await import("../../src/schemas.ts");
    const { SCHEMA_IDS } = await import("../../src/index.ts");
    for (const id of SCHEMA_IDS) {
      expect(schemaFor(id, "producer"), id).toBeDefined();
      expect(schemaFor(id, "consumer"), id).toBeDefined();
    }
    expect(schemaFor("dlq.normalize-item/v1", "producer")).toBe(
      schemaFor("dlq.<service>/v1", "producer"),
    );
  });

  it("the keys and registries entry points match the root's helpers", async () => {
    const root = await import("../../src/index.ts");
    const keys = await import("../../src/keys/index.ts");
    const registries = await import("../../src/registries/index.ts");
    expect(keys.itemId).toBe(root.itemId);
    expect(registries.partitionKey).toBe(root.partitionKey);
  });
});
