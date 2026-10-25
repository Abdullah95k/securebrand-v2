// The conformance suite (A4, A6, A28, A29): every fixture under fixtures/contracts/ is validated as
// a producer and as a consumer would. The Python suite (python/tests/test_conformance.py) reads the
// same files and must agree on every one (G0 check 2).
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { validate } from "../../src/validate.ts";
import {
  FIXTURES_DIR,
  REPO_DIR,
  fixtures,
  readJson,
  samePath,
  schemaDirs,
  schemaIdOf,
  type Path,
} from "../helpers.ts";

const DIRS = schemaDirs();

const pathsOf = (r: ReturnType<typeof validate>): Path[] =>
  r.ok ? [] : r.issues.map((i) => i.path);

describe("accepts every valid fixture and rejects every invalid fixture at the expected path (A4)", () => {
  it("finds the schema directories", () => {
    expect(DIRS.length).toBeGreaterThanOrEqual(17);
  });

  for (const dir of DIRS) {
    const id = schemaIdOf(dir);
    describe(dir, () => {
      for (const f of fixtures(dir, "valid")) {
        it(`accepts ${f.file} as a producer and as a consumer`, () => {
          const producer = validate(id, f.value, "producer", f.options);
          expect(producer.ok ? [] : producer.issues).toEqual([]);
          const consumer = validate(id, f.value, "consumer", f.options);
          expect(consumer.ok ? [] : consumer.issues).toEqual([]);
        });
      }
      for (const f of fixtures(dir, "invalid")) {
        const want = f.expected?.path ?? [];
        it(`rejects ${f.file} at ${JSON.stringify(want)} as a producer`, () => {
          const r = validate(id, f.value, "producer", f.options);
          expect(r.ok, `${f.name} was accepted; it breaks: ${f.expected?.rule}`).toBe(false);
          const paths = pathsOf(r);
          expect(
            paths.some((p) => samePath(p, want)),
            `${f.name}: no issue at ${JSON.stringify(want)}; got ${JSON.stringify(paths)}`,
          ).toBe(true);
        });
      }
      for (const f of fixtures(dir, "tolerant")) {
        it(`accepts ${f.file} as a consumer and rejects it as a producer (A32)`, () => {
          expect(validate(id, f.value, "consumer", f.options).ok).toBe(true);
          expect(validate(id, f.value, "producer", f.options).ok).toBe(false);
        });
      }
    });
  }
});

interface ManifestEntry {
  service: string;
  prd: string;
  line: number;
  schema: string | null;
  fixture: string | null;
  rewrites?: string[];
  note?: string;
}

const manifest = (readJson(`${FIXTURES_DIR}prd-examples.json`) as { examples: ManifestEntry[] })
  .examples;

/** The first content line of every JSON block in a PRD's section 6.2. */
function jsonBlocks(prd: string): number[] {
  const lines = readFileSync(`${REPO_DIR}${prd}`, "utf8").split("\n");
  const out: number[] = [];
  let in62 = false;
  let fence = false;
  lines.forEach((line, i) => {
    if (line.startsWith("## ") || line.startsWith("### ")) in62 = line.startsWith("### 6.2");
    if (in62 && line.startsWith("```json")) {
      fence = true;
      out.push(i + 2);
    } else if (fence && line.startsWith("```")) fence = false;
  });
  return out;
}

const metadataOf = (value: unknown): Record<string, unknown> => {
  const v = value as Record<string, unknown>;
  return (v.envelope as Record<string, unknown> | undefined) ?? v;
};

describe("every PRD section 6.2 example, rewritten into its v1 shape, validates (A6)", () => {
  it("lists one entry for every JSON example of every PRD's section 6.2", () => {
    const prds = new Set(manifest.map((e) => e.prd));
    const missing: string[] = [];
    for (const prd of prds) {
      for (const line of jsonBlocks(prd)) {
        if (!manifest.some((e) => e.prd === prd && e.line === line)) missing.push(`${prd}:${line}`);
      }
    }
    expect(missing).toEqual([]);
    for (const e of manifest) expect(jsonBlocks(e.prd), `${e.service}`).toContain(e.line);
  });

  it("covers every PRD: 86 services, each with an entry", () => {
    const services = new Set(manifest.map((e) => e.service));
    expect(services.size).toBe(86);
  });

  it("names a rewritten fixture of the producer itself, or says why the example is no message", () => {
    for (const e of manifest) {
      if (e.fixture === null) {
        expect(e.note, `${e.service}:${e.line} has neither a fixture nor a note`).toBeTruthy();
        continue;
      }
      expect(e.fixture).toMatch(new RegExp(`/valid/prd-${e.service}\\.json$`));
      const value = readJson(`${FIXTURES_DIR}${e.fixture}`);
      const producer = metadataOf(value).producer as { service: string };
      expect(producer.service, e.fixture).toBe(e.service);
      expect(e.rewrites?.length ?? 0, `${e.fixture} lists no rewrites`).toBeGreaterThan(0);
    }
  });

  it("lists every prd-<service>.json fixture", () => {
    const listed = new Set(manifest.map((e) => e.fixture));
    for (const dir of DIRS) {
      for (const f of fixtures(dir, "valid")) {
        if (f.file.startsWith("prd-"))
          expect(listed.has(`${dir}/valid/${f.file}`), f.name).toBe(true);
      }
    }
  });
});
