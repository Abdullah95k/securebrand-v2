import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import {
  accountSegments,
  parseAllowlist,
  scrubValue,
  shapeOnly,
  stableFake,
  type ScrubContext,
} from "../src/scrub.ts";

const ctx = (allow: string[] = []): ScrubContext => ({
  allow: new Set(allow),
  replaced: new Set(),
});

describe("scrubValue", () => {
  it("replaces a private individual's handle, title name and snippet on a social result", () => {
    const c = ctx();
    const out = scrubValue(
      {
        results: [
          {
            url: "https://www.instagram.com/some.private.person/",
            title: "Some Private Person (@some.private.person) • Instagram",
            snippet: "Some Private Person posted about FiberX",
          },
        ],
      },
      c,
    );
    const text = JSON.stringify(out);
    expect(text).not.toContain("some.private.person");
    expect(text).not.toContain("Some Private Person");
    expect(text).toContain("Instagram");
  });

  it("gives the same fake to the same person everywhere", () => {
    expect(stableFake("acct", "Same.Person")).toBe(stableFake("acct", "same.person"));
    const out = scrubValue(
      [
        { url: "https://x.com/same_person", title: "same_person" },
        { url: "https://x.com/same_person/status/1", title: "same_person" },
      ],
      ctx(),
    ) as { url: string }[];
    const a = /acct-[0-9a-f]{8}/.exec(out[0]?.url ?? "")?.[0];
    const b = /acct-[0-9a-f]{8}/.exec(out[1]?.url ?? "")?.[0];
    expect(a).toBeDefined();
    expect(a).toBe(b);
  });

  it("keeps an allow-listed public account and a news outlet", () => {
    const out = scrubValue(
      [
        { url: "https://www.facebook.com/fiberx.iq", title: "FiberX" },
        { url: "https://www.rudaw.net/arabic/business/1", title: "FiberX expands" },
      ],
      ctx(["fiberx.iq"]),
    );
    expect(JSON.stringify(out)).toContain("fiberx.iq");
    expect(JSON.stringify(out)).toContain("rudaw.net/arabic/business/1");
  });

  it("removes tokens, signed URLs and keys from any string", () => {
    const out = JSON.stringify(
      scrubValue(
        {
          u: "https://cdn.example.com/a.jpg?X-Amz-Signature=abcdef123456&oh=deadbeef12",
          k: "https://api.mojeek.com/search?api_key=KEY123456",
        },
        ctx(),
      ),
    );
    expect(out).not.toMatch(/abcdef123456|deadbeef12|KEY123456/);
  });

  it("finds the account segment of a social URL and skips page-type words", () => {
    expect(accountSegments("https://www.tiktok.com/@user.name/video/123")).toEqual(["user.name"]);
  });
});

describe("shapeOnly (Mojeek Startup plan)", () => {
  it("keeps counts and field names and no value", () => {
    const out = JSON.stringify(
      shapeOnly({ response: { results: [{ title: "secret title", url: "https://a.example/x" }] } }),
    );
    expect(out).toContain('"length":1');
    expect(out).toContain('"title"');
    expect(out).not.toContain("secret title");
    expect(out).not.toContain("a.example");
  });
});

describe("parseAllowlist", () => {
  it("reads handles, ignoring comments and a leading @", () => {
    expect([...parseAllowlist("# c\n@FiberX\n\nrudaw\n")]).toEqual(["fiberx", "rudaw"]);
  });
});

// The scrubbing test of the brief: committed fixtures hold no token and none of the private
// identifiers the scrubber replaced. It runs on whatever is in fixtures/web/ and, while raw/ still
// exists in the probe session, also checks every replaced original against every fixture.
const fixtures = join(import.meta.dirname, "..", "..", "..", "..", "fixtures", "web");
const TOKENS = [
  /EAA[A-Za-z0-9]{20,}/,
  /AIza[0-9A-Za-z_-]{35}/,
  /eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}/,
  /[Bb]earer\s+[A-Za-z0-9._~+/=-]{20,}/,
  /pplx-[A-Za-z0-9]{8,}/,
  /(api_?key|access_token)(=|%3D)(?!REDACTED)[A-Za-z0-9._%-]{6,}/i,
  /[?&](x-amz-signature|x-goog-signature|signature|sig|oh)=(?!REDACTED)[A-Za-z0-9%._~+/=-]{8,}/i,
];

describe("committed fixtures", () => {
  const files = existsSync(fixtures)
    ? readdirSync(fixtures).filter((f) => f.endsWith(".json"))
    : [];

  it("hold no token, API key or signed URL", () => {
    for (const f of files) {
      const text = readFileSync(join(fixtures, f), "utf8");
      for (const re of TOKENS) expect(text, `${f} matches ${re.source}`).not.toMatch(re);
    }
  });

  it("hold none of the private identifiers recorded in raw/replaced.json", () => {
    const replacedPath = join(fixtures, "raw", "replaced.json");
    if (!existsSync(replacedPath)) return; // raw/ is deleted after the scrubbing test passes
    const replaced = (JSON.parse(readFileSync(replacedPath, "utf8")) as string[]).filter(
      (s) => s.length >= 3,
    );
    for (const f of files) {
      const text = readFileSync(join(fixtures, f), "utf8");
      for (const original of replaced)
        expect(text.includes(original), `${f} still holds a replaced original`).toBe(false);
    }
  });

  it("hold no result text for Mojeek when the manifest says the Startup plan was used", () => {
    const manifestPath = join(fixtures, "manifest.json");
    if (!existsSync(manifestPath)) return;
    const manifest = JSON.parse(readFileSync(manifestPath, "utf8")) as { mojeekPlan?: string };
    if (manifest.mojeekPlan !== "startup") return;
    for (const f of files.filter((n) => n.startsWith("mojeek-"))) {
      const doc = JSON.parse(readFileSync(join(fixtures, f), "utf8")) as { body: unknown };
      expect(JSON.stringify(doc.body), f).not.toMatch(/https?:\/\//);
    }
  });
});
