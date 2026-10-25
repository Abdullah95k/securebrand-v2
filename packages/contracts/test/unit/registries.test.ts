import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  D3_WRITERS,
  INDEX_SERVICES,
  PLATFORM_SERVICES,
  contextKeyRegistry,
  decisionRows,
  extrasKeyRegistry,
  isKnownService,
  isKnownVendor,
  producerRows,
  queueService,
  rawItemsKinds,
  requiredFieldRows,
  topicWriters,
} from "../../src/registries/index.ts";
import {
  DECISION_TYPES,
  HEALTHS,
  JOB_KINDS,
  RECORD_KINDS,
  REGISTRY_REASONS,
} from "../../src/vocabulary.ts";
import { createBuilder } from "../../src/builder.ts";
import { context, extras } from "../../src/context.ts";
import { validate } from "../../src/validate.ts";
import { PACKAGE_DIR, copyOf, fixture, samePath } from "../helpers.ts";

// The service index as CONVENTIONS v1.1 L372 to L384 writes it: "Group (n): a, b (amber), ...".
function conventionsIndex(): { group: string; count: number; services: string[] }[] {
  const text = readFileSync(`${PACKAGE_DIR}../../docs/prds/_shared/CONVENTIONS.md`, "utf8");
  const start = text.indexOf("## Service index");
  const block = text.slice(start, text.indexOf("\n## ", start + 1));
  const groups: { group: string; count: number; services: string[] }[] = [];
  for (const line of block.split("\n")) {
    const m = /^([A-Z][A-Za-z ,]*) \((\d+)\): (.+)\.$/.exec(line);
    if (!m) continue;
    // Drop the parenthetical notes ("(amber)", "(the one exception to the prefix rule, ADR-0070)").
    const services = (m[3] ?? "")
      .replace(/\s*\([^)]*\)/g, "")
      .split(", ")
      .map((s) => s.trim());
    groups.push({ group: m[1] ?? "", count: Number(m[2]), services });
  }
  return groups;
}

const SPECIAL = new Set(["@queue", "@platform", "@service", "*"]);

describe("the service index (A23, Q4)", () => {
  it("equals CONVENTIONS v1.1's service index, 86 services in 11 groups", () => {
    const groups = conventionsIndex();
    expect(groups).toHaveLength(11);
    for (const g of groups) expect(g.services, g.group).toHaveLength(g.count);
    const fromDoc = groups.flatMap((g) => g.services);
    expect(fromDoc).toHaveLength(86);
    expect([...INDEX_SERVICES].sort()).toEqual([...fromDoc].sort());
  });

  it("the platform services are the 66 of the Facebook to Web groups", () => {
    const groups = conventionsIndex().slice(0, 9);
    expect(groups.map((g) => g.group)).toEqual([
      "Facebook",
      "Instagram",
      "TikTok",
      "X",
      "LinkedIn",
      "Telegram",
      "YouTube",
      "News",
      "Web",
    ]);
    expect([...PLATFORM_SERVICES].sort()).toEqual(groups.flatMap((g) => g.services).sort());
    expect(PLATFORM_SERVICES).toHaveLength(66);
  });

  it("knows the index services and the three D3 writers, nothing else", () => {
    expect(isKnownService("fb-page-feed-poller")).toBe(true);
    for (const w of D3_WRITERS) expect(isKnownService(w)).toBe(true);
    expect(isKnownService("admin")).toBe(false);
    expect(isKnownService("FB-PAGE-FEED-POLLER")).toBe(false);
  });
});

describe("vendors by route (ADR-0051 (c))", () => {
  it("an amber record names an amber vendor; a green one a licensed engine or none", () => {
    expect(isKnownVendor("amber", "ensembledata")).toBe(true);
    expect(isKnownVendor("amber", null)).toBe(false);
    expect(isKnownVendor("amber", "mojeek")).toBe(false);
    expect(isKnownVendor("green", null)).toBe(true);
    expect(isKnownVendor("green", "gdelt")).toBe(true);
    expect(isKnownVendor("green", "sociavault")).toBe(false);
    expect(isKnownVendor("green", "apify_tugelbay")).toBe(false);
  });
});

describe("producer mode checks the registry data (A23; Q1, F-09)", () => {
  const failsAt = (r: ReturnType<typeof validate>, path: (string | number)[]): boolean =>
    !r.ok && r.issues.some((i) => samePath(i.path, path));

  it("producer mode refuses a producer.service or provenance.vendor the registry data does not list", () => {
    const f = fixture("item.hits/v1", "valid", "prd-keyword-matcher.json");
    const service = copyOf(f);
    (service.producer as Record<string, unknown>).service = "keyword-matcher-v2";
    expect(failsAt(validate("item.hits/v1", service), ["producer", "service"])).toBe(true);
    const fetcher = copyOf(f);
    (fetcher.provenance as Record<string, unknown>).service = "x-searcher";
    expect(failsAt(validate("item.hits/v1", fetcher), ["provenance", "service"])).toBe(true);
    const amber = copyOf(fixture("raw.items/v1", "valid", "prd-tg-channel-posts-poller.json"));
    const env = amber.envelope as Record<string, Record<string, unknown>>;
    if (env.provenance) env.provenance.vendor = "apify";
    expect(failsAt(validate("raw.items/v1", amber), ["envelope", "provenance", "vendor"])).toBe(
      true,
    );
  });

  it("the schemas type service names and vendors as patterned strings, not enums", () => {
    // A name the registry does not list yet passes the consumer, which knows no registry data.
    const f = fixture("item.hits/v1", "valid", "prd-keyword-matcher.json");
    const value = copyOf(f);
    (value.producer as Record<string, unknown>).service = "keyword-matcher-v2";
    (value.provenance as Record<string, unknown>).vendor = "a-new-engine";
    expect(validate("item.hits/v1", value, "consumer").ok).toBe(true);
    (value.producer as Record<string, unknown>).service = "Keyword Matcher";
    expect(validate("item.hits/v1", value, "consumer").ok).toBe(false);
  });

  it("the context and extras schemas hold exactly the keys some producer declares", () => {
    const b = createBuilder("producer");
    const contextKeys = Object.keys(context(b).shape).sort();
    const declared = new Set<string>();
    for (const entry of Object.values(contextKeyRegistry().producers))
      for (const k of entry.keys) declared.add(k);
    for (const entry of Object.values(contextKeyRegistry().by_kind))
      for (const k of entry.keys) declared.add(k);
    expect(contextKeys).toEqual([...declared].sort());
    const extrasKeys = Object.keys(extras(b).shape).sort();
    const resolverKeys = new Set(Object.values(extrasKeyRegistry().resolvers).flat());
    expect(extrasKeys).toEqual([...resolverKeys].sort());
  });
});

describe("the registries name only known services, kinds and values", () => {
  const known = (s: string): boolean => SPECIAL.has(s) || isKnownService(s);

  it("every producer-table row names job kinds, known queues and known producers", () => {
    for (const row of producerRows()) {
      expect(JOB_KINDS as readonly string[]).toContain(row.kind);
      expect(isKnownService(queueService(row.queue)), row.queue).toBe(true);
      for (const p of row.producers)
        expect(isKnownService(p), `${row.queue} ${row.kind} ${p}`).toBe(true);
    }
    for (const r of requiredFieldRows()) {
      for (const q of r.queues) expect(isKnownService(queueService(q)), q).toBe(true);
      for (const k of r.kinds) expect(JOB_KINDS as readonly string[]).toContain(k);
      for (const p of r.producers ?? []) expect(known(p), p).toBe(true);
    }
  });

  it("every topic writer is known, and raw.items lists each writer's record kinds", () => {
    for (const [schema, writers] of Object.entries(topicWriters())) {
      for (const w of writers) expect(known(w), `${schema} ${w}`).toBe(true);
    }
    const raw = topicWriters()["raw.items/v1"] ?? [];
    expect(raw).toHaveLength(56);
    for (const w of raw) {
      const kinds = rawItemsKinds(w);
      expect(kinds, w).not.toBeNull();
      for (const k of kinds ?? []) expect(RECORD_KINDS as readonly string[]).toContain(k);
    }
  });

  it("every decision row names a type, a subject, known producers and listed values", () => {
    for (const row of decisionRows()) {
      for (const d of row.decisions) expect(DECISION_TYPES as readonly string[]).toContain(d);
      expect(["candidate_key", "author_ref", "source_id", "platform", "keyword_id"]).toContain(
        row.subject,
      );
      for (const p of row.producers) expect(known(p), p).toBe(true);
      for (const r of row.reasons ?? [])
        if (r !== null) expect(REGISTRY_REASONS as readonly string[]).toContain(r);
      for (const h of row.healths ?? []) expect(HEALTHS as readonly string[]).toContain(h);
      for (const n of row.rule_hits ?? [])
        expect(Number.isInteger(n) && n >= 1 && n <= 10).toBe(true);
      expect(["required", "refused", "optional"]).toContain(row.provenance);
    }
  });

  it("only raw.items writers declare context keys and only resolvers declare extras keys", () => {
    const raw = topicWriters()["raw.items/v1"] ?? [];
    for (const service of Object.keys(contextKeyRegistry().producers))
      expect(raw).toContain(service);
    const profiles = topicWriters()["poster.profiles/v1"] ?? [];
    for (const service of Object.keys(extrasKeyRegistry().resolvers))
      expect(profiles).toContain(service);
    for (const [service, entry] of Object.entries(contextKeyRegistry().producers)) {
      for (const k of entry.required) expect(entry.keys, service).toContain(k);
    }
  });
});
