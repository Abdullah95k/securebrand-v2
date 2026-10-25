import { describe, expect, it } from "vitest";
import { redact, registerSecret } from "../src/redact.ts";

describe("redact", () => {
  it("removes a Mojeek api_key from a request URL", () => {
    const url = "https://api.mojeek.com/search?q=test&api_key=abcDEF123456&fmt=json";
    expect(redact(url)).toBe("https://api.mojeek.com/search?q=test&api_key=REDACTED&fmt=json");
  });

  it("removes a registered secret wherever it appears, plain or URL-encoded", () => {
    registerSecret("s3cret/value+1");
    const text = `failed for s3cret/value+1 and ${encodeURIComponent("s3cret/value+1")}`;
    expect(redact(text)).not.toContain("s3cret");
    expect(redact(text)).not.toContain("value");
  });

  it("removes a bearer token and a Perplexity key", () => {
    expect(redact("Authorization: Bearer abcdefghijklmnop1234")).toBe(
      "Authorization: Bearer REDACTED",
    );
    expect(redact("key pplx-AbCdEfGhIjKl1234")).toBe("key pplx-REDACTED");
  });

  it("removes a key that an error message quotes from a failed fetch", () => {
    const err = new Error("fetch failed: https://api.mojeek.com/search?api_key=zzzz9999yyyy&q=x");
    expect(redact(err.message)).not.toContain("zzzz9999yyyy");
  });
});
