// A30: the n8n signing helper, one HMAC scheme over the body with a timestamp and an idempotency
// key (ADR-0067; Q11, F-49). The clock is an argument: no helper reads one.
import { describe, expect, it } from "vitest";
import { signN8n, verifyN8n } from "../../src/n8n.ts";
import { golden, utf8 } from "../helpers.ts";

interface SignCase {
  body: string;
  timestamp: number;
  idempotency_key: string;
  headers: Record<string, string>;
}
interface VerifyCase {
  case: string;
  body: string;
  headers: Record<string, string>;
  now: number;
  tolerance_seconds: number;
  ok: boolean;
  reason?: string;
}

const g = golden<{ secret: string; sign: SignCase[]; verify: VerifyCase[] }>("n8n-signing.json");

describe("n8n signing (ADR-0067, A30)", () => {
  it("signs the golden requests byte for byte", () => {
    for (const c of g.sign) {
      expect(signN8n(utf8(c.body), utf8(g.secret), c.timestamp, c.idempotency_key)).toEqual(
        c.headers,
      );
      expect(
        signN8n(c.body, g.secret, c.timestamp, c.idempotency_key),
        "strings are UTF-8",
      ).toEqual(c.headers);
    }
  });

  it("rejects a changed body, a timestamp outside the tolerance of the given now, and a wrong key", () => {
    for (const c of g.verify) {
      const result = verifyN8n(utf8(c.body), c.headers, utf8(g.secret), c.now, c.tolerance_seconds);
      expect(result, c.case).toEqual(c.ok ? { ok: true } : { ok: false, reason: c.reason });
    }
  });

  it("verifies what it signs, with a tolerance of 300 seconds by default", () => {
    const headers = signN8n("{}", g.secret, 1_791_275_832, "k:email");
    expect(verifyN8n("{}", headers, g.secret, 1_791_276_132)).toEqual({ ok: true });
    expect(verifyN8n("{}", headers, g.secret, 1_791_276_133)).toEqual({
      ok: false,
      reason: "stale_timestamp",
    });
  });

  it("refuses to sign with a timestamp that is no whole second or an empty idempotency key", () => {
    expect(() => signN8n("{}", g.secret, 1.5, "k:email")).toThrow(/bad_timestamp/);
    expect(() => signN8n("{}", g.secret, -1, "k:email")).toThrow(/bad_timestamp/);
    expect(() => signN8n("{}", g.secret, 1, "")).toThrow(/bad_idempotency_key/);
    expect(() => signN8n("{}", "", 1, "k:email")).toThrow(/empty_secret/);
  });
});
