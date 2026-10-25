import { describe, expect, it } from "vitest";
import {
  NS_CARDS,
  NS_HITS,
  analysisKey,
  cardId,
  commentDecayJobId,
  deterministicUlid,
  hitId,
  hitMessageId,
} from "../../src/keys/index.ts";
import { golden } from "../helpers.ts";

interface IdsGolden {
  ns_hits: string;
  ns_cards: string;
  hit_ids: { input: { item_id: string; client_id: string; keyword_id: string }; hit_id: string }[];
  card_ids: { input: { card_type: string; subject_key: string; ref: string }; card_id: string }[];
  ulids: { name: string; input: { time: string; fields: string[] }; ulid: string }[];
  hit_message_ids: {
    input: { hit_at: string; hit_id: string; item_version: number; keyword_set_version: string };
    message_id: string;
  }[];
  comment_decay_job_ids: {
    input: { due_at: string; item_id: string; lane: string; series_step: string };
    job_id: string;
  }[];
  analysis_keys: { input: { item_id: string; task: string; model_version: string }; analysis_key: string }[];
  analysis_rejects: { name: string; input: { item_id: string; task: string; model_version: string } }[];
}

const g = golden<IdsGolden>("ids.json");

describe("deterministic ids (ADR-0006)", () => {
  it("freezes the namespaces the golden file records", () => {
    expect(NS_HITS).toBe(g.ns_hits);
    expect(NS_CARDS).toBe(g.ns_cards);
  });

  it("derives the golden uuid v5 ids and deterministic ULIDs", () => {
    for (const c of g.hit_ids) expect(hitId(c.input.item_id, c.input.client_id, c.input.keyword_id)).toBe(c.hit_id);
    for (const c of g.card_ids) expect(cardId(c.input.card_type, c.input.subject_key, c.input.ref)).toBe(c.card_id);
    for (const c of g.ulids) expect(deterministicUlid(c.input.time, c.input.fields)).toBe(c.ulid);
    for (const c of g.hit_message_ids) expect(hitMessageId(c.input)).toBe(c.message_id);
    for (const c of g.comment_decay_job_ids) expect(commentDecayJobId(c.input)).toBe(c.job_id);
  });

  it("a replayed input gives the same id", () => {
    const c = g.hit_message_ids[0];
    expect(c).toBeDefined();
    if (!c) return;
    expect(hitMessageId({ ...c.input })).toBe(hitMessageId({ ...c.input }));
    expect(deterministicUlid("2026-10-06T08:51:40Z", ["a"])).toBe(deterministicUlid("2026-10-06T08:51:40Z", ["a"]));
  });

  it("a new item version gives a new hit message id", () => {
    const [v1, v2] = g.hit_message_ids;
    expect(v1?.message_id).not.toBe(v2?.message_id);
  });

  it("the ULID's time part is the event's own time", () => {
    const id = deterministicUlid("2026-10-06T08:51:40.123Z", ["a"]);
    const other = deterministicUlid("2026-10-06T08:51:40.123Z", ["b"]);
    expect(id.slice(0, 10)).toBe(other.slice(0, 10));
    expect(id).toMatch(/^[0-7][0-9A-HJKMNP-TV-Z]{25}$/);
  });

  it("refuses a time that is not a UTC timestamp", () => {
    expect(() => deterministicUlid("2026-10-06T08:51:40+03:00", ["a"])).toThrow();
    expect(() => deterministicUlid("2026-10-06", ["a"])).toThrow();
  });
});

describe("analysis keys (ADR-0023)", () => {
  it("builds the analysis key", () => {
    for (const c of g.analysis_keys) {
      expect(analysisKey(c.input.item_id, c.input.task, c.input.model_version)).toBe(c.analysis_key);
    }
  });

  it.each(g.analysis_rejects.map((c) => [c.name, c] as const))("refuses a task holding a colon: %s", (_n, c) => {
    expect(() => analysisKey(c.input.item_id, c.input.task, c.input.model_version)).toThrow();
  });
});
