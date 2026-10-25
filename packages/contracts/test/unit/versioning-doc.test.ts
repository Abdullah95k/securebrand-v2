// A31: docs/contracts/VERSIONING.md lists every schema id of the catalogue with its version, and only
// those, so a new schema id or version cannot ship without its line. The rules themselves are read in
// review.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { CATALOGUE } from "../../src/catalogue.ts";
import { NS_CARDS, NS_HITS, NS_ITEMS } from "../../src/keys/ids.ts";
import { REPO_DIR } from "../helpers.ts";

const doc = readFileSync(join(REPO_DIR, "docs/contracts/VERSIONING.md"), "utf8");

/** The rows of the catalogue table: its first cell is a schema id in backticks, its second the version. */
function catalogueRows(): Map<string, string> {
  const section = doc.split(/^## /m).find((s) => s.startsWith("Catalogue of schema ids"));
  if (section === undefined)
    throw new Error("VERSIONING.md has no 'Catalogue of schema ids' section");
  const rows = new Map<string, string>();
  for (const line of section.split("\n")) {
    const m = /^\| `([^`]+)` \| (v\d+) \|/.exec(line);
    if (m?.[1] !== undefined && m[2] !== undefined) rows.set(m[1], m[2]);
  }
  return rows;
}

describe("VERSIONING.md (A31)", () => {
  it("VERSIONING.md lists every schema id and its version", () => {
    const rows = catalogueRows();
    expect([...rows.keys()].sort()).toEqual(CATALOGUE.map((e) => e.id).sort());
    for (const [id, version] of rows) expect(id.endsWith(`/${version}`), id).toBe(true);
  });

  it("names the frozen namespaces with their values", () => {
    for (const [name, value] of [
      ["ns_items", NS_ITEMS],
      ["ns_hits", NS_HITS],
      ["ns_cards", NS_CARDS],
    ])
      expect(doc, name).toContain(`\`${name}\` = \`${value}\``);
  });
});
