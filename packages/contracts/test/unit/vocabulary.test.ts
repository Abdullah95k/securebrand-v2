import { describe, expect, it } from "vitest";
import { AMBER_VENDORS, D3_WRITERS, GREEN_VENDORS } from "../../src/registries/index.ts";
import * as vocabulary from "../../src/vocabulary.ts";
import { golden } from "../helpers.ts";

interface Entry {
  values: (string | number)[];
  from: string;
}
interface VocabularyGolden {
  lists: Record<string, Entry>;
  registry: Record<"VENDORS_AMBER" | "VENDORS_GREEN" | "D3_WRITERS", Entry>;
}

const g = golden<VocabularyGolden>("vocabulary.json");
const exported = Object.entries(vocabulary) as [string, readonly (string | number)[]][];

describe("closed lists (A23)", () => {
  it.each(Object.entries(g.lists))(
    "each closed list equals the values its ADR names: %s",
    (name, entry) => {
      const list = (vocabulary as Record<string, readonly (string | number)[] | undefined>)[name];
      expect(list, `${name} (${entry.from})`).toEqual(entry.values);
    },
  );

  it("every exported list has a recorded source", () => {
    expect(exported.map(([name]) => name).filter((name) => !(name in g.lists))).toEqual([]);
  });

  it("routes are lower case and the platforms are the nine of CONVENTIONS", () => {
    expect(vocabulary.ROUTES).toEqual(["green", "amber"]);
    expect(vocabulary.PLATFORMS).toHaveLength(9);
  });

  it("marks every account_type an organisation kind or a person kind, never both", () => {
    const org: readonly string[] = vocabulary.ORGANISATION_ACCOUNT_TYPES;
    const person: readonly string[] = vocabulary.PERSON_ACCOUNT_TYPES;
    expect(org.filter((t) => person.includes(t))).toEqual([]);
    expect([...org, ...person].sort()).toEqual([...vocabulary.ACCOUNT_TYPES].sort());
  });

  it("the registry reason list holds flag_off, flag_on and owner_request", () => {
    expect(vocabulary.REGISTRY_REASONS).toEqual(
      expect.arrayContaining(["flag_off", "flag_on", "owner_request"]),
    );
    expect(new Set(vocabulary.REGISTRY_REASONS).size).toBe(vocabulary.REGISTRY_REASONS.length);
  });
});

describe("registry name lists (A23)", () => {
  it("ADR-0051's vendors and the D3 writer names equal their sources", () => {
    expect(AMBER_VENDORS).toEqual(g.registry.VENDORS_AMBER.values);
    expect(GREEN_VENDORS).toEqual(g.registry.VENDORS_GREEN.values);
    expect(D3_WRITERS).toEqual(g.registry.D3_WRITERS.values);
  });
});
