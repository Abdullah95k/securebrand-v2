// D10: the fold table is data, and it is read strictly, as the Python twin reads it: a key the fold
// does not know, or one it needs and does not find, is refused at import, so a row added to or
// renamed in the table cannot leave the fold silently folding by the old rules.
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { checkFoldTable } from "../../src/data.ts";
import { PACKAGE_DIR } from "../helpers.ts";

type Json = Record<string, unknown>;

const table = (): Json =>
  JSON.parse(readFileSync(`${PACKAGE_DIR}data/fold-table.json`, "utf8")) as Json;

describe("the fold table is read strictly (D10)", () => {
  it("accepts the committed fold-table.json", () => {
    expect(checkFoldTable(table())).toEqual(table());
  });

  it("refuses a key the fold does not know, at the top or inside a row", () => {
    expect(() => checkFoldTable({ ...table(), row7_kept: [] })).toThrow(/row7_kept/u);
    const t = table();
    (t.row10 as Json).tag_end = "U+0020";
    expect(() => checkFoldTable(t)).toThrow(/row10.*tag_end/u);
  });

  it("refuses a table missing a key the fold needs", () => {
    const t = table();
    delete (t.row3_alef as Json).marks_deleted_after;
    expect(() => checkFoldTable(t)).toThrow(/row3_alef.*marks_deleted_after/u);
    const d = table();
    delete ((d.row8_digits as Json[])[0] as Json).becomes_first;
    expect(() => checkFoldTable(d)).toThrow(/row8_digits\[0\].*becomes_first/u);
  });

  it("refuses a table that is not an object", () => {
    expect(() => checkFoldTable([])).toThrow(/fold-table.json/u);
    expect(() => checkFoldTable(null)).toThrow(/fold-table.json/u);
  });
});
