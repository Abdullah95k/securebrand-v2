import { describe, expect, it } from "vitest";
import { deletionId, type DeletionIdInput } from "../../src/keys/index.ts";
import { golden } from "../helpers.ts";

interface DeletionIdGolden {
  deletion_ids: { name: string; input: DeletionIdInput; canonical: string; deletion_id: string }[];
}

const g = golden<DeletionIdGolden>("deletion-id.json");
const id = (name: string): string | undefined => g.deletion_ids.find((c) => c.name === name)?.deletion_id;

describe("deletion_id (ADR-0035; Q2)", () => {
  it.each(g.deletion_ids.map((c) => [c.name, c] as const))("derives the golden deletion ids: %s", (_n, c) => {
    expect(deletionId(c.input)).toBe(c.deletion_id);
  });

  it("target order does not change the id", () => {
    expect(id("item scope, platform sync")).toBe(id("target order does not change the id"));
  });

  it("two clients with equal targets get different ids", () => {
    expect(id("client offboarding, client X")).not.toBe(id("client offboarding, client Y with an equal target"));
  });

  it("two authors with equal targets get different ids", () => {
    expect(id("author request, author 1")).not.toBe(id("author request, author 2 with an equal target"));
  });

  it("purge_text then delete of one item get different ids", () => {
    expect(id("retention purge_text of one item")).not.toBe(id("retention delete of the same item"));
  });

  it("one author under two keys gets one id per key", () => {
    expect(id("author request, author 1")).not.toBe(id("author request, author 1 under the second key"));
  });

  it("the same signal on another day gets a new id", () => {
    expect(id("item scope, platform sync")).not.toBe(id("the same signal on another day gets a new id"));
  });

  it("a same-day replay keeps its id", () => {
    expect(id("item scope, platform sync")).toBe(id("a same-day replay keeps its id"));
  });

  it("refuses a signal_at that is not a UTC timestamp", () => {
    const c = g.deletion_ids[0];
    expect(c).toBeDefined();
    if (c) expect(() => deletionId({ ...c.input, signal_at: "2026-10-06" })).toThrow();
  });
});
