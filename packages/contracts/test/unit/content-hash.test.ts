import { describe, expect, it } from "vitest";
import { contentHash } from "../../src/keys/index.ts";
import { golden } from "../helpers.ts";

interface ContentHashGolden {
  hashes: { name: string; title: string | null; text: string | null; content_hash: string }[];
}

const g = golden<ContentHashGolden>("content-hash.json");

describe("content_hash (ADR-0009)", () => {
  it.each(g.hashes.map((c) => [c.name, c] as const))(
    "derives the golden content hashes: %s",
    (_n, c) => {
      expect(contentHash(c.title, c.text)).toBe(c.content_hash);
    },
  );

  it("a decomposed text hashes as its composed form", () => {
    const nfd = g.hashes.find((c) => c.name === "decomposed text hashes as composed");
    const nfc = g.hashes.find((c) => c.name === "the same text composed");
    expect(nfd?.content_hash).toBe(nfc?.content_hash);
  });
});
