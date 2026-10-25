// lang-dialect-id 13 criterion 12 and E7: any change to the fold's data or to a golden expectation is
// a new FOLD_VERSION, and a released version's hashes never change.
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { FOLD_DATA_SHA256, FOLD_VERSION } from "../../src/index.ts";
import { corpus, PACKAGE_DIR, readJson, REPO_DIR } from "../helpers.ts";

interface VersionEntry {
  readonly version: string;
  readonly fold_data_sha256: string;
  readonly golden_sha256: string;
}

// The released versions, pinned here as well as in data/fold-versions.json: changing a released
// entry there fails this test, so a fold change has to be a new version (E7).
const RELEASED: readonly VersionEntry[] = [
  {
    version: "fold-1",
    fold_data_sha256: "af7a968e27aeb75e501723896308cd9fe8c091ce32755997510ca7edb84646ca",
    golden_sha256: "8896ff8675e5ef461e24739d7f20a8e81cf9b6e20e2e67fd136d221facbdc86c",
  },
];

const DATA_FILES = [
  ["fold-table.json", `${PACKAGE_DIR}data/fold-table.json`],
  ["unicode-15.1.json", `${PACKAGE_DIR}data/unicode-15.1.json`],
  [
    "unicode-15.1-unassigned.json",
    `${REPO_DIR}packages/contracts/registries/unicode-15.1-unassigned.json`,
  ],
] as const;

const sha256 = (data: string | Buffer): string => createHash("sha256").update(data).digest("hex");

/** D10: the hash of the fold table, F7's 15.1 data and contracts' unassigned ranges. */
function foldDataSha256(): string {
  return sha256(
    DATA_FILES.map(([name, path]) => `${name} ${sha256(readFileSync(path))}\n`).join(""),
  );
}

/** E7: the hash of the golden expectations, each case's id, lang, title, text and text_norm. */
function goldenSha256(): string {
  const lines = corpus()
    .map((c) => JSON.stringify([c.id, c.lang, c.title, c.text, c.text_norm]))
    .sort();
  return sha256(lines.join("\n"));
}

function history(): VersionEntry[] {
  const path = `${PACKAGE_DIR}data/fold-versions.json`;
  expect(existsSync(path), `${path} exists`).toBe(true);
  return (readJson(path) as { versions: VersionEntry[] }).versions;
}

describe("criterion 12: the fold's version (D10, E7)", () => {
  it("FOLD_VERSION is the fold table's version", () => {
    const table = readJson(`${PACKAGE_DIR}data/fold-table.json`) as { version: string };
    expect(FOLD_VERSION).toBe(table.version);
    expect(FOLD_VERSION).toMatch(/^fold-[1-9][0-9]*$/u);
  });

  it("FOLD_DATA_SHA256 hashes the fold table, the 15.1 data and contracts' unassigned ranges", () => {
    expect(FOLD_DATA_SHA256).toBe(foldDataSha256());
  });

  it("the fold data and the golden expectations hash to the current FOLD_VERSION's entry in fold-versions.json", () => {
    const entry = history().find((e) => e.version === FOLD_VERSION);
    expect(entry).toEqual({
      version: FOLD_VERSION,
      fold_data_sha256: foldDataSha256(),
      golden_sha256: goldenSha256(),
    });
  });

  it("no released version's hashes change", () => {
    expect(history().slice(0, RELEASED.length)).toEqual(RELEASED);
  });

  it("package.json and pyproject.toml declare the same package version", () => {
    const pkg = readJson(`${PACKAGE_DIR}package.json`) as { version: string };
    const pyproject = readFileSync(`${PACKAGE_DIR}pyproject.toml`, "utf8");
    expect(/^version = "([^"]+)"$/mu.exec(pyproject)?.[1]).toBe(pkg.version);
  });
});
