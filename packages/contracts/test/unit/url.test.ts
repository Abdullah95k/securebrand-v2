import { describe, expect, it } from "vitest";
import {
  articleKey,
  canonicalUrlHash,
  normaliseUrl,
  urlHash,
  urlKey,
  webResultKey,
} from "../../src/keys/index.ts";
import { golden } from "../helpers.ts";

interface UrlsGolden {
  urls: {
    name: string;
    input: string;
    base?: string;
    normalised: string;
    url_hash: string;
    url_key: string;
    article_key: string;
    web_result_key: string;
  }[];
  rejects: { name: string; input: string; base?: string }[];
}

const g = golden<UrlsGolden>("urls.json");
const byName = (name: string): UrlsGolden["urls"][number] | undefined =>
  g.urls.find((c) => c.name === name);

describe("the URL normaliser (ADR-0036; Q9)", () => {
  it.each(g.urls.map((c) => [c.name, c] as const))("normalises every golden URL: %s", (_n, c) => {
    expect(normaliseUrl(c.input, c.base)).toBe(c.normalised);
  });

  it.each(g.urls.map((c) => [c.name, c] as const))(
    "derives url_hash, url_key and the article and web-result keys: %s",
    (_n, c) => {
      expect(urlHash(c.input, c.base)).toBe(c.url_hash);
      expect(urlKey(c.input, c.base)).toBe(c.url_key);
      expect(canonicalUrlHash(c.normalised)).toBe(c.url_hash);
      expect(articleKey(c.normalised)).toBe(c.article_key);
      expect(webResultKey(c.normalised)).toBe(c.web_result_key);
    },
  );

  it("normalising twice changes nothing", () => {
    for (const c of g.urls) expect(normaliseUrl(c.normalised)).toBe(c.normalised);
  });

  it("http and https forms of one page hash differently", () => {
    expect(byName("http, the known limit")?.url_hash).not.toBe(
      byName("https, the known limit")?.url_hash,
    );
    expect(byName("www kept")?.url_hash).not.toBe(byName("bare host")?.url_hash);
  });

  it("raw, upper-case and lower-case encodings of one Arabic slug hash alike", () => {
    const raw = byName("raw Arabic slug percent-encoded as UTF-8 with upper-case hex");
    const lower = byName("the same slug encoded with lower-case hex");
    expect(raw?.url_hash).toBeDefined();
    expect(raw?.url_hash).toBe(lower?.url_hash);
  });

  it.each(g.rejects.map((c) => [c.name, c] as const))("refuses a URL: %s", (_n, c) => {
    expect(() => normaliseUrl(c.input, c.base)).toThrow();
  });
});
