// Writes fixtures/contracts/golden/issue-paths.json (D-4): TypeScript's issue paths for every
// invalid and tolerant fixture, as a producer and as a consumer. Run it after gen:fixtures. Both
// suites assert their paths equal these, except under the six plain unions (below), where they
// assert only the verdict and that their paths hold the fixture's expected.json path.
import { writeFileSync } from "node:fs";
import { validate } from "../src/validate.ts";
import { FIXTURES_DIR, fixtures, schemaDirs, schemaIdOf, type Path } from "../test/helpers.ts";

type Json = Record<string, unknown>;

// The plain z.unions, where the languages may list different branches' paths (D-4): the whole of
// four schemas, n8n.alert's `details` and a push job's `body`.
const PLAIN_SCHEMAS = new Set([
  "registry.decisions/v1",
  "poster.profiles/v1",
  "items.analysis/v1",
  "raw.items/v1",
]);

function check(dir: string, value: unknown, paths: Path[]): "equal" | "expected" {
  if (PLAIN_SCHEMAS.has(dir)) return "expected";
  const under = (step: string): boolean => paths.some((p) => p[0] === step);
  if (dir === "n8n.alert/v1" && under("details")) return "expected";
  if (dir === "job/v1" && (value as Json).kind === "push" && under("body")) return "expected";
  return "equal";
}

const key = (p: Path): string => JSON.stringify(p);
const cases: string[] = [];
for (const dir of schemaDirs()) {
  for (const kind of ["invalid", "tolerant"] as const) {
    for (const f of fixtures(dir, kind)) {
      for (const mode of ["producer", "consumer"] as const) {
        const r = validate(schemaIdOf(dir), f.value, mode, f.options);
        const unique = new Map((r.ok ? [] : r.issues).map((i) => [key(i.path), i.path]));
        const paths = [...unique.keys()].sort().map((k) => unique.get(k) as Path);
        const entry = {
          schema: dir,
          file: `${kind}/${f.file}`,
          mode,
          check: check(dir, f.value, paths),
          paths,
        };
        cases.push(JSON.stringify(entry));
      }
    }
  }
}

const description =
  "TypeScript's issue paths (D-4) for every invalid and tolerant fixture, as a producer and as a " +
  "consumer, each set sorted and without repeats; written by packages/contracts/scripts/" +
  "issue-paths.ts after gen:fixtures. Under `check: equal` both suites assert that their path " +
  "set equals `paths`. `check: expected` marks the six plain z.unions, where the languages may " +
  "report different branches (registry.decisions, poster.profiles, items.analysis and raw.items " +
  "as a whole, n8n.alert's `details` and a push job's `body`): there both suites assert only the " +
  "verdict and, for an invalid fixture as a producer, that their paths hold its expected.json path.";
writeFileSync(
  `${FIXTURES_DIR}golden/issue-paths.json`,
  `{\n  "description": ${JSON.stringify(description)},\n  "cases": [\n    ${cases.join(",\n    ")}\n  ]\n}\n`,
);
console.log(`wrote ${cases.length} cases`);
