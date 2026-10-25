// D-4: both languages report a shape error at the same paths under the discriminated unions;
// fixtures/contracts/golden/issue-paths.json records TypeScript's (scripts/issue-paths.ts).
import { describe, expect, it } from "vitest";
import { validate } from "../../src/validate.ts";
import {
  copyOf,
  fixture,
  fixtures,
  golden,
  schemaDirs,
  schemaIdOf,
  type Path,
} from "../helpers.ts";

interface IssuePathCase {
  schema: string;
  file: string;
  mode: "producer" | "consumer";
  check: "equal" | "expected";
  paths: Path[];
}

const g = golden<{ cases: IssuePathCase[] }>("issue-paths.json");
const key = (p: Path): string => JSON.stringify(p);

describe("issue paths (D-4)", () => {
  it.each(g.cases.map((c) => [`${c.schema}/${c.file} ${c.mode}`, c] as const))(
    "reports the golden paths, or under a plain union the verdict and the expected path: %s",
    (_name, c) => {
      const [kind, file] = c.file.split("/") as ["invalid" | "tolerant", string];
      const f = fixture(c.schema, kind, file);
      const r = validate(schemaIdOf(c.schema), f.value, c.mode, f.options);
      const got = new Set(r.ok ? [] : r.issues.map((i) => key(i.path)));
      if (c.check === "equal") {
        expect([...got].sort()).toEqual(c.paths.map(key));
        return;
      }
      expect(got.size === 0, "the verdict").toBe(c.paths.length === 0);
      if (kind === "invalid" && c.mode === "producer" && f.expected)
        expect(got.has(key(f.expected.path)), [...got].join(" ")).toBe(true);
    },
  );

  it("records every invalid and tolerant fixture in both modes", () => {
    const recorded = new Set(g.cases.map((c) => `${c.schema}/${c.file} ${c.mode}`));
    const all: string[] = [];
    for (const dir of schemaDirs()) {
      for (const kind of ["invalid", "tolerant"] as const) {
        for (const f of fixtures(dir, kind)) {
          for (const mode of ["producer", "consumer"]) all.push(`${dir}/${kind}/${f.file} ${mode}`);
        }
      }
    }
    expect(all.filter((c) => !recorded.has(c))).toEqual([]);
    expect(recorded.size).toBe(all.length);
  });

  it("a consumer-mode source-level health_change that carries a platform names no fallback or scope", () => {
    const value = {
      ...copyOf(fixture("registry.decisions/v1", "valid", "source-health-degraded.json")),
      platform: "facebook",
    };
    const r = validate("registry.decisions/v1", value, "consumer");
    const paths = r.ok ? [] : r.issues.map((i) => key(i.path));
    expect(paths).not.toContain(key(["health_change", "fallback"]));
    expect(paths).not.toContain(key(["health_change", "scope"]));
  });
});
