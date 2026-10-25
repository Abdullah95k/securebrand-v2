// The corpus itself: its size and categories (the brief), each line's shape (golden.schema.json),
// and the rules that keep any private person's text or name out of it (DoD item 7, ADR-0010).
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { CATEGORIES, GoldenCase, goldenSchemaJson, PLANNED_COUNTS } from "../golden-case.ts";
import { corpus, corpusLines, FIXTURES_DIR } from "../helpers.ts";

const cases = corpus();

// Reserved names (RFC 2606) and the plan's invented handles and fictional phone numbers.
const RESERVED_HOST = /^(?:[a-z0-9-]+\.)*example\.(?:com|org|net)$/u;
const RESERVED_HANDLE = /^example(?:_[\p{L}\p{N}]+)*$/u;
const FICTIONAL_PHONE = /^(?:\+964[ -]?|0)7[0-9]{2}[ -]?000[ -]?0000$/u;
const ARABIC_INDIC = /[٠-٩۰-۹]/gu;

/** The input of a case as one string, with fullwidth forms and Arabic-Indic digits made plain. */
function plain(title: string | null, text: string): string {
  return `${title ?? ""} ${text}`.normalize("NFKC").replace(ARABIC_INDIC, (d) => {
    const cp = d.codePointAt(0) ?? 0;
    return String(cp >= 0x06f0 ? cp - 0x06f0 : cp - 0x0660);
  });
}

describe("the brief: 500 or more cases in the named categories", () => {
  it("holds at least 500 cases in all", () => {
    expect(cases.length).toBeGreaterThanOrEqual(500);
  });

  it("each category holds at least its planned count", () => {
    const short: string[] = [];
    for (const category of CATEGORIES) {
      const n = cases.filter((c) => c.category === category).length;
      if (n < PLANNED_COUNTS[category]) {
        short.push(`${category}: ${String(n)} of ${String(PLANNED_COUNTS[category])}`);
      }
    }
    expect(short).toEqual([]);
  });

  it("every line validates against golden.schema.json", () => {
    const bad: string[] = [];
    corpusLines().forEach((line, i) => {
      const result = GoldenCase.safeParse(line);
      if (!result.success) {
        const paths = result.error.issues.map((issue) => issue.path.join(".")).join(", ");
        bad.push(`line ${String(i + 1)}: ${paths}`);
      }
    });
    expect(bad).toEqual([]);
  });

  it("the committed golden.schema.json is the export of the case schema", () => {
    expect(readFileSync(`${FIXTURES_DIR}golden.schema.json`, "utf8")).toBe(goldenSchemaJson());
  });

  it("ids are unique", () => {
    const ids = cases.map((c) => c.id);
    expect(ids.filter((id, i) => ids.indexOf(id) !== i)).toEqual([]);
  });
});

describe("DoD 7: no private person's text or name in the fixtures", () => {
  it("every case records its origin, and public-domain cases name their work", () => {
    const bad: string[] = [];
    for (const c of cases) {
      if (c.origin === "invented" && c.source !== null)
        bad.push(`${c.id}: an invented case names a source`);
      // "<work>, <author>, <year>"
      if (c.origin === "public_domain" && !/^.+, .+, [0-9]{3,4}$/u.test(c.source ?? "")) {
        bad.push(`${c.id}: a public-domain case must name its work, author and year`);
      }
    }
    expect(bad).toEqual([]);
  });

  it("handles, URLs and phone-like digits follow the reserved patterns", () => {
    const bad: string[] = [];
    for (const c of cases) {
      const s = plain(c.title, c.text);
      for (const m of s.matchAll(/(?:https?:\/\/|www\.)([^\s/?#،؛]+)/giu)) {
        const host = (m[1] ?? "").toLowerCase().replace(/^www\./u, "");
        if (!RESERVED_HOST.test(host)) bad.push(`${c.id}: URL host ${host}`);
      }
      for (const m of s.matchAll(/(?<=^|[^\p{L}\p{M}\p{N}_])@([\p{L}\p{M}\p{N}_]+)/gu)) {
        if (!RESERVED_HANDLE.test(m[1] ?? "")) bad.push(`${c.id}: handle @${m[1] ?? ""}`);
      }
      for (const m of s.matchAll(/(?<=[\p{L}\p{N}])@([\p{L}\p{N}-]+(?:\.[\p{L}\p{N}-]+)+)/gu)) {
        if (!RESERVED_HOST.test((m[1] ?? "").toLowerCase()))
          bad.push(`${c.id}: e-mail domain ${m[1] ?? ""}`);
      }
      for (const m of s.matchAll(/\+?[0-9](?:[ -]?[0-9]){9,}/gu)) {
        if (!FICTIONAL_PHONE.test(m[0])) bad.push(`${c.id}: phone-like ${m[0]}`);
      }
    }
    expect(bad).toEqual([]);
  });
});
