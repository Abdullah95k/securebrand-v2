// The fixtures' chains (review note 21): the ids a consumer copies, the keys the helpers derive, and
// individuals present only as references under the published test key, from invented ids (D-8).
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { authorRef, itemId } from "../../src/keys/index.ts";
import {
  FIXTURES_DIR,
  fixture,
  fixtures,
  golden,
  schemaDirs,
  type FixtureKind,
} from "../helpers.ts";

type Json = Record<string, unknown>;
const value = (dir: string, file: string): Json => fixture(dir, "valid", file).value as Json;
const at = (v: unknown, ...path: string[]): unknown =>
  path.reduce<unknown>((cur, k) => (cur as Json | undefined)?.[k], v);

// The invented authors of the fixture generator (scripts/fixtures/); a fixture carries their
// references only. Any other author_ref in a fixture is a literal, which D-8 rules out.
const INVENTED_AUTHORS: readonly [string, string][] = [
  ["facebook", "1234567890"],
  ["facebook", "1000000000000000011"],
  ["facebook", "1000000000000000012"],
  ["facebook", "1000000000000000013"],
  ["instagram", "17841455555555555"],
  ["instagram", "17841466666666666"],
  ["linkedin", "ACoAAB1234567"],
  ["linkedin", "urn:li:person:Ab12Cd34"],
  ["linkedin", "urn:li:person:Ef56Gh78"],
  ["linkedin", "urn:li:person:Ij90Kl12"],
  ["news", "disqus:9418273650"],
  ["telegram", "5210987654"],
  ["tiktok", "6800000000000000999"],
  ["x", "1000000000000000001"],
  ["x", "1290000000000000077"],
  ["youtube", "UCaaaaaaaaaaaaaaaaaaaaaa"],
  ["youtube", "UCbbbbbbbbbbbbbbbbbbbbbb"],
];

/** Every reference under an `author_ref` key, anywhere in `v` (a malformed one is a format case). */
function authorRefs(v: unknown, out: string[] = []): string[] {
  if (Array.isArray(v)) for (const x of v) authorRefs(x, out);
  else if (typeof v === "object" && v !== null)
    for (const [k, x] of Object.entries(v)) {
      if (k === "author_ref" && typeof x === "string" && /^[0-9a-f]{64}$/.test(x)) out.push(x);
      else authorRefs(x, out);
    }
  return out;
}

describe("the fixtures' chains (note 21)", () => {
  it("a topic consumer copies its input's producer.job_id along the poster chain (F-17)", () => {
    const profile = value("poster.profiles/v1", "prd-poster-resolver.json");
    const decision = value("registry.decisions/v1", "prd-qualifier.json");
    const event = value("source.events/v1", "prd-registry-writer.json");
    expect(at(decision, "producer", "job_id")).toBe(at(profile, "producer", "job_id"));
    expect(at(event, "producer", "job_id")).toBe(at(decision, "producer", "job_id"));
  });

  it("each first_sight job carries the job_id of its sibling raw record (F-17)", () => {
    const jobs = fixtures("job/v1", "valid").filter((f) => at(f.value, "kind") === "first_sight");
    expect(jobs.length).toBeGreaterThan(0);
    for (const job of jobs) {
      const raw = value("raw.items/v1", job.file);
      expect(at(job.value, "producer", "job_id"), job.name).toBe(at(raw, "envelope", "job_id"));
    }
  });

  it("news.dedup's duplicate names the extractor's article by its key", () => {
    const verdict = value("news.dedup/v1", "prd-news-dedup.json");
    const article = value("raw.items/v1", "prd-news-article-extractor.json");
    expect(at(verdict, "duplicate_of")).toBe(at(article, "envelope", "idempotency_key"));
  });

  it("a public person's url is its own handle's", () => {
    const person = value("poster.profiles/v1", "public-person-individual.json");
    expect(String(person.url).endsWith(`/${String(person.handle)}`)).toBe(true);
  });

  it("a container candidate is the group its item's raw record names (ADR-0031 L34)", () => {
    const hit = value("discovery.hits/v1", "container-group.json");
    // The record keyword-matcher read: the hit's item, from the service its provenance names.
    const raw = fixtures("raw.items/v1", "valid").filter((f) => {
      const key = at(f.value, "envelope", "idempotency_key");
      const service = at(f.value, "envelope", "provenance", "service");
      return (
        typeof key === "string" &&
        itemId(key) === hit.item_id &&
        service === at(hit, "provenance", "service")
      );
    });
    expect(raw.length, "a raw record of the hit's item").toBeGreaterThan(0);
    for (const f of raw) {
      expect(at(f.value, "payload", "context", "type"), f.name).toBe("group");
      expect(at(f.value, "payload", "context", "id"), f.name).toBe(
        at(hit, "candidate", "platform_id"),
      );
      expect(at(f.value, "payload", "context", "name"), f.name).toBe(at(hit, "evidence", "name"));
    }
  });

  it("every author_ref in the fixtures is derived under the published test key from an invented id (D-8)", () => {
    const g = golden<{ test_key_utf8: string }>("author-ref.json");
    const key = new TextEncoder().encode(g.test_key_utf8);
    const known = new Set(INVENTED_AUTHORS.map(([platform, id]) => authorRef(key, platform, id)));
    const unknown: string[] = [];
    for (const dir of schemaDirs())
      for (const kind of ["valid", "invalid", "tolerant"] as FixtureKind[])
        for (const f of fixtures(dir, kind))
          for (const ref of authorRefs(f.value))
            if (!known.has(ref)) unknown.push(`${f.name} ${ref}`);
    const partitionKeys = JSON.parse(
      readFileSync(`${FIXTURES_DIR}golden/partition-keys.json`, "utf8"),
    ) as unknown;
    for (const ref of authorRefs(partitionKeys))
      if (!known.has(ref)) unknown.push(`golden/partition-keys.json ${ref}`);
    expect(unknown).toEqual([]);
  });
});
