import { describe, expect, it } from "vitest";
import { authorRef, matchesAuthorRef } from "../../src/keys/index.ts";
import { golden, utf8 } from "../helpers.ts";

interface AuthorRefGolden {
  test_key_utf8: string;
  second_test_key_utf8: string;
  author_refs: { platform: string; author_platform_id: string; author_ref: string }[];
  under_second_key: { platform: string; author_platform_id: string; author_ref: string };
}

const g = golden<AuthorRefGolden>("author-ref.json");
const key1 = utf8(g.test_key_utf8);
const key2 = utf8(g.second_test_key_utf8);

describe("author_ref (ADR-0010)", () => {
  it("derives the golden author_refs", () => {
    for (const c of g.author_refs) expect(authorRef(key1, c.platform, c.author_platform_id)).toBe(c.author_ref);
    const s = g.under_second_key;
    expect(authorRef(key2, s.platform, s.author_platform_id)).toBe(s.author_ref);
  });

  it("an NFD author id gives the reference of its NFC form", () => {
    const [nfd, nfc] = g.author_refs.slice(-2);
    expect(nfd?.author_ref).toBe(nfc?.author_ref);
  });

  it("refuses an empty key", () => {
    expect(() => authorRef(new Uint8Array(), "x", "1234567890")).toThrow();
  });

  it("matches a reference under any of several keys", () => {
    const s = g.under_second_key;
    expect(matchesAuthorRef(s.author_ref, s.platform, s.author_platform_id, [key1, key2])).toBe(true);
    expect(matchesAuthorRef(s.author_ref, s.platform, s.author_platform_id, [key1])).toBe(false);
    expect(matchesAuthorRef(s.author_ref, s.platform, "999", [key1, key2])).toBe(false);
  });
});
