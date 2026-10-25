import { describe, expect, it } from "vitest";
import { ALLOWED_HOSTS, CAPS } from "../src/config.ts";
import { Ledger } from "../src/http.ts";
import { parseKeywords } from "../src/keywords.ts";
import { commonCrawlCalls, gdeltCalls, mojeekCalls, perplexityCalls } from "../src/plan.ts";

const thirty = parseKeywords(
  [
    ...Array.from({ length: 10 }, (_, i) => `فايبر اكس ${i}`),
    ...Array.from({ length: 10 }, (_, i) => `فایبەر ڕێکلام ${i}`),
    ...Array.from({ length: 10 }, (_, i) => `FiberX ${i}`),
  ].join("\n"),
);

describe("keywords", () => {
  it("detects Arabic, Sorani and English and skips comments and blanks", () => {
    const k = parseKeywords("# note\n\nفايبر اكس\nڕێکلام\nFiberX\nFiberX\n");
    expect(k.map((x) => x.lang)).toEqual(["ar", "ckb", "en"]);
  });
});

describe("call plan", () => {
  it("keeps Perplexity within 30 requests and about USD 0.15 for 30 keywords", () => {
    const calls = perplexityCalls(thirty);
    expect(calls.length).toBeLessThanOrEqual(CAPS.perplexityRequests);
    expect(calls.length * CAPS.perplexityUsdPerRequest).toBeLessThanOrEqual(0.15);
  });

  it("packs every keyword into a Perplexity request of at most 5 queries", () => {
    const packs = perplexityCalls(thirty).filter((c) => c.id.startsWith("pplx-pack-"));
    const queries = packs.flatMap((c) => c.body?.["query"] as string[]);
    expect(queries).toHaveLength(30);
    expect(packs.every((c) => (c.body?.["query"] as string[]).length <= 5)).toBe(true);
  });

  it("keeps Mojeek within 30 queries", () => {
    expect(mojeekCalls(thirty, "business").length).toBeLessThanOrEqual(CAPS.mojeekQueries);
  });

  it("plans the same Mojeek calls on the Startup plan, which only changes what is stored", () => {
    expect(mojeekCalls(thirty, "startup")).toEqual(mojeekCalls(thirty, "business"));
  });

  it("keeps GDELT and Common Crawl within their own ceilings", () => {
    expect(gdeltCalls(thirty).length).toBeLessThanOrEqual(CAPS.gdeltRequests);
    expect(commonCrawlCalls("CC-MAIN-2026-40").length).toBeLessThanOrEqual(
      CAPS.commonCrawlRequests,
    );
  });

  it("sends every planned call to an allow-listed https host and puts no credential in a URL", () => {
    const all = [
      ...perplexityCalls(thirty),
      ...mojeekCalls(thirty, "business"),
      ...gdeltCalls(thirty),
      ...commonCrawlCalls("CC-MAIN-2026-40"),
    ];
    for (const c of all) {
      const u = new URL(c.url);
      expect(u.protocol).toBe("https:");
      expect(ALLOWED_HOSTS as readonly string[]).toContain(u.hostname);
      expect(c.url.toLowerCase()).not.toMatch(/api_?key|token/);
    }
  });
});

describe("ledger", () => {
  it("refuses the request after the cap", async () => {
    const ledger = new Ledger();
    for (let i = 0; i < CAPS.perplexityRequests; i++) await ledger.admit("perplexity");
    await expect(ledger.admit("perplexity")).rejects.toThrow(/cap/);
  });

  it("spaces GDELT requests at least 5 seconds apart", () => {
    expect(new Ledger().gap("gdelt")).toBeGreaterThanOrEqual(5000);
  });

  it("spaces Common Crawl requests apart", () => {
    expect(new Ledger().gap("commoncrawl")).toBeGreaterThanOrEqual(1000);
  });
});
