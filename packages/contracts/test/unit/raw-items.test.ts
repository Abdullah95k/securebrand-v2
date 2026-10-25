// A20: raw.items/v1's envelope, record kinds and declared context (ADR-0005, ADR-0008, ADR-0009).
import { describe, expect, it } from "vitest";
import { contextKeyRegistry } from "../../src/registries/index.ts";
import { validate } from "../../src/validate.ts";
import { CONTENT_KINDS } from "../../src/vocabulary.ts";
import { copyOf, fixture, fixtures, samePath } from "../helpers.ts";

type Json = Record<string, unknown>;
const ID = "raw.items/v1";
const VALID = fixtures(ID, "valid");
const env = (v: unknown): Json => (v as Json).envelope as Json;
const failsAt = (r: ReturnType<typeof validate>, path: (string | number)[]): boolean =>
  !r.ok && r.issues.some((i) => samePath(i.path, path));

describe("raw.items/v1 (ADR-0005, A20)", () => {
  it("accepts each producer's declared context", () => {
    const registry = contextKeyRegistry();
    for (const [service, declared] of Object.entries(registry.producers)) {
      const own = VALID.filter((f) => (env(f.value).producer as Json).service === service);
      expect(own.length, `${service} has a valid fixture`).toBeGreaterThan(0);
      const seen = new Set(
        own.flatMap((f) => Object.keys((env(f.value).context as Json | undefined) ?? {})),
      );
      seen.delete("item_key");
      expect([...seen].sort(), service).toEqual([...declared.keys].sort());
    }
    const metrics = VALID.filter((f) => env(f.value).kind === "metrics");
    expect(metrics.length).toBeGreaterThan(0);
    for (const f of metrics)
      expect(Object.keys(env(f.value).context as Json), f.name).toContain("item_key");
  });

  it("rejects an undeclared context key", () => {
    const f = fixture(ID, "valid", "prd-fb-page-feed-poller.json");
    const value = copyOf(f);
    env(value).context = { query_arm: "brand" }; // x-recent-search's key
    expect(failsAt(validate(ID, value), ["envelope", "context", "query_arm"])).toBe(true);
    // Context types hold in both modes; who may use a key is producer-mode registry data.
    expect(validate(ID, value, "consumer").ok).toBe(true);
  });

  it("requires platform_id and idempotency_key on item kinds", () => {
    for (const kind of CONTENT_KINDS) {
      const f = VALID.find((x) => env(x.value).kind === kind);
      if (!f) throw new Error(`no valid ${kind} record`);
      for (const name of ["platform_id", "idempotency_key"]) {
        const value = copyOf(f);
        delete env(value)[name];
        expect(failsAt(validate(ID, value), ["envelope", name]), `${kind} ${name}`).toBe(true);
      }
    }
  });

  it("requires parent_id and root_id on comments", () => {
    const f = fixture(ID, "valid", "prd-yt-replies-fetcher.json");
    expect(env(f.value).kind).toBe("comment");
    for (const name of ["parent_id", "root_id"]) {
      const value = copyOf(f);
      delete env(value)[name];
      expect(failsAt(validate(ID, value), ["envelope", name]), name).toBe(true);
    }
  });

  it("accepts candidate_key instead of source_id on any record kind about a candidate, li-org-resolver's sampled post included (F-03)", () => {
    const about = VALID.filter((f) => env(f.value).candidate_key !== undefined);
    const kinds = new Set(about.map((f) => env(f.value).kind));
    expect(kinds).toContain("profile");
    expect(kinds).toContain("post");
    const post = fixture(ID, "valid", "post-about-a-candidate.json");
    expect((env(post.value).producer as Json).service).toBe("li-org-resolver");
    expect(env(post.value).source_id).toBeUndefined();
    expect(validate(ID, post.value).ok).toBe(true);
  });

  it("requires author_ref, null allowed, on comment and reaction records (Q3)", () => {
    for (const file of ["prd-ig-own-comments-fetcher.json", "reaction.json"]) {
      const f = fixture(ID, "valid", file);
      const missing = copyOf(f);
      delete env(missing).author_ref;
      expect(failsAt(validate(ID, missing), ["envelope", "author_ref"]), file).toBe(true);
      const nulled = copyOf(f);
      env(nulled).author_ref = null;
      expect(validate(ID, nulled).ok, file).toBe(true);
    }
  });
});
