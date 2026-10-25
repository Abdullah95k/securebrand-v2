// A30: n8n.alert/v1 and n8n.card/v1 with Q11's fields (ADR-0067, ADR-0048).
import { describe, expect, it } from "vitest";
import { cardId } from "../../src/keys/index.ts";
import { validate } from "../../src/validate.ts";
import { ALERT_RULE_TYPES, CARD_TYPES } from "../../src/vocabulary.ts";
import { copyOf, fixture, fixtures, golden, samePath } from "../helpers.ts";

type Json = Record<string, unknown>;
const ALERT = "n8n.alert/v1";
const CARD = "n8n.card/v1";
const failsAt = (r: ReturnType<typeof validate>, path: (string | number)[]): boolean =>
  !r.ok && r.issues.some((i) => samePath(i.path, path));

describe("n8n.alert/v1 and n8n.card/v1 (ADR-0067, A30)", () => {
  it("accepts each of the nine rule_type branches", () => {
    const seen = new Set<unknown>();
    for (const f of fixtures(ALERT, "valid")) {
      const details = (f.value as Json).details as Json;
      if (details.rule_type === undefined) continue;
      seen.add(details.rule_type);
      expect(validate(ALERT, f.value, "producer", f.options).ok, f.name).toBe(true);
    }
    expect([...seen].sort()).toEqual([...ALERT_RULE_TYPES].sort());
  });

  it("rejects an open details object", () => {
    const f = fixture(ALERT, "valid", "facts-budget.json");
    const value = { ...copyOf(f), details: { note: "free text", level: 3 } };
    expect(failsAt(validate(ALERT, value), ["details", "note"])).toBe(true);
    expect(validate(ALERT, value, "consumer").ok).toBe(false);
  });

  it("rejects a government client's alert with subject.source_id or subject.platform", () => {
    const f = fixture(ALERT, "valid", "government-keyword-level.json");
    expect(validate(ALERT, f.value, "producer", { clientType: "government" }).ok).toBe(true);
    for (const [name, v] of [
      ["source_id", "a3c0f1e2-5b6d-4c7e-9f80-112233445566"],
      ["platform", "facebook"],
    ]) {
      const value = copyOf(f);
      (value.subject as Json)[name as string] = v;
      expect(
        failsAt(validate(ALERT, value, "producer", { clientType: "government" }), [
          "subject",
          name as string,
        ]),
        name,
      ).toBe(true);
      expect(
        validate(ALERT, value, "producer", { clientType: "commercial" }).ok,
        `${name}, commercial`,
      ).toBe(true);
    }
    // The producer passes the client type of a client's alert, or the alert fails closed.
    expect(validate(ALERT, f.value).ok).toBe(false);
    expect(validate(ALERT, f.value, "consumer").ok).toBe(true);
  });

  it("requires each card_type's fields", () => {
    const required: Record<string, string> = {
      qualifier_review: "buttons",
      grant_missing: "regrant_url",
      manual_url: "inputs",
    };
    const seen = new Set<unknown>();
    for (const f of fixtures(CARD, "valid")) {
      const type = (f.value as Json).card_type as string;
      seen.add(type);
      const field = required[type] ?? "";
      const value = copyOf(f);
      delete value[field];
      expect(failsAt(validate(CARD, value), [field]), `${f.name} without ${field}`).toBe(true);
    }
    expect([...seen].sort()).toEqual([...CARD_TYPES].sort());
  });

  it("derives the golden card_ids", () => {
    const g = golden<{
      card_ids: {
        input: { card_type: string; subject_key: string; ref: string };
        card_id: string;
      }[];
    }>("ids.json");
    for (const { input, card_id } of g.card_ids)
      expect(cardId(input.card_type, input.subject_key, input.ref)).toBe(card_id);
    for (const f of fixtures(CARD, "valid")) {
      const v = f.value as Json;
      const subject = v.subject as Record<string, string>;
      const key = subject.candidate_key ?? subject.source_id ?? "";
      const ref = subject.decision_id ?? subject.request_id ?? "";
      expect(v.card_id, f.name).toBe(cardId(v.card_type as string, key, ref));
    }
  });
});
