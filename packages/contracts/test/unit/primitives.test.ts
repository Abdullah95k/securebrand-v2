import { describe, expect, it } from "vitest";
import {
  candidateKeyFromHandle,
  candidateKeyFromId,
  facebookGroupCandidateKey,
  newsSiteCandidateKey,
  parseCandidateKey,
  parseRawRef,
  rawRef,
  renderKeyTime,
} from "../../src/keys/index.ts";
import { PATTERNS } from "../../src/primitives.ts";

describe("primitives", () => {
  it("rejects a non-UTC timestamp", () => {
    expect(PATTERNS.timestamp.test("2026-10-06T09:15:42Z")).toBe(true);
    expect(PATTERNS.timestamp.test("2026-10-06T09:15:42.123Z")).toBe(true);
    expect(PATTERNS.timestamp.test("2026-10-06T09:15:42+03:00")).toBe(false);
    expect(PATTERNS.timestamp.test("2026-10-06T09:15Z")).toBe(false);
    expect(PATTERNS.timestamp.test("2026-10-06T09:15:42.1234Z")).toBe(false);
    expect(PATTERNS.timestamp.test("2026-10-06 09:15:42Z")).toBe(false);
    expect(PATTERNS.timestamp.test("2026-10-06T09:15:42Z\n")).toBe(false);
  });

  it("the id-less comment hash renders created_time as YYYY-MM-DDTHH:MM:SSZ", () => {
    expect(renderKeyTime("2026-10-06T09:15:42+0000")).toBe("2026-10-06T09:15:42Z");
    expect(renderKeyTime("2026-10-06T12:15:42+03:00")).toBe("2026-10-06T09:15:42Z");
    expect(renderKeyTime("2026-10-06T01:15:42-08:00")).toBe("2026-10-06T09:15:42Z");
    expect(renderKeyTime("2026-10-06T09:15:42.999Z")).toBe("2026-10-06T09:15:42Z");
    expect(renderKeyTime("2026-01-01T02:00:00+03:00")).toBe("2025-12-31T23:00:00Z");
    expect(() => renderKeyTime("2026-10-06T09:15Z")).toThrow();
    expect(() => renderKeyTime("2026-10-06T09:15:42")).toThrow();
    expect(() => renderKeyTime("2026-02-30T09:15:42Z")).toThrow();
  });

  it("types ids, ULIDs and hashes by their canonical forms", () => {
    expect(PATTERNS.uuid.test("6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11")).toBe(true);
    expect(PATTERNS.uuid.test("6F1C2E3A-8B4D-4C7E-9A21-0D5E7F3B9C11")).toBe(false);
    expect(PATTERNS.ulid.test("01J9N2Q7Z4T8X1V6M3K0H5R2WB")).toBe(true);
    expect(PATTERNS.ulid.test("81J9N2Q7Z4T8X1V6M3K0H5R2WB")).toBe(false);
    expect(PATTERNS.ulid.test("01J9N2Q7Z4T8X1V6M3K0H5R2WI")).toBe(false);
    expect(PATTERNS.prefixedSha256.test(`sha256:${"a".repeat(64)}`)).toBe(true);
    expect(PATTERNS.sha256Hex.test("A".repeat(64))).toBe(false);
  });
});

describe("candidate keys (ADR-0032)", () => {
  it("builds the four forms", () => {
    expect(candidateKeyFromId("x", "1234567890")).toBe("x:1234567890");
    expect(candidateKeyFromId("youtube", "UCabcDEF123")).toBe("youtube:UCabcDEF123");
    expect(candidateKeyFromHandle("instagram", "@Example_Store_IQ")).toBe("instagram:example_store_iq");
    expect(facebookGroupCandidateKey("123456789012345")).toBe("facebook:group:123456789012345");
    expect(newsSiteCandidateKey("Example-Daily.IQ")).toBe("news:site:example-daily.iq");
  });

  it("parses each form", () => {
    expect(parseCandidateKey("facebook:group:123")).toEqual({ platform: "facebook", form: "group", value: "123" });
    expect(parseCandidateKey("news:site:example.iq")).toEqual({ platform: "news", form: "site", value: "example.iq" });
    expect(parseCandidateKey("x:1234567890")).toEqual({ platform: "x", form: "account", value: "1234567890" });
  });

  it("refuses keys outside the four forms", () => {
    expect(() => parseCandidateKey("news:example.iq")).toThrow();
    expect(() => parseCandidateKey("instagram:post:Cx4kQ2LsT9m")).toThrow();
    expect(() => candidateKeyFromHandle("web", "x")).toThrow();
    expect(() => newsSiteCandidateKey("localhost")).toThrow();
  });
});

describe("raw_ref (ADR-0005, ADR-0039)", () => {
  it("builds and parses an archive reference with a six-digit batch", () => {
    const ref = rawRef({ route: "green", platform: "facebook", date: "2026-10-06", service: "fb-page-feed-poller", batch: 123, line: 42 });
    expect(ref).toBe("raw/green/facebook/2026/10/06/fb-page-feed-poller/000123.jsonl.zst#42");
    expect(parseRawRef(ref)).toEqual({ route: "green", platform: "facebook", date: "2026-10-06", service: "fb-page-feed-poller", batch: 123, line: 42 });
  });

  it("refuses a batch beyond six digits and a malformed reference", () => {
    expect(() => rawRef({ route: "green", platform: "x", date: "2026-10-06", service: "x-recent-search", batch: 1_000_000, line: 1 })).toThrow();
    expect(() => parseRawRef("raw/green/x/2026/10/06/x-recent-search/0042.jsonl.zst#310")).toThrow();
  });
});
