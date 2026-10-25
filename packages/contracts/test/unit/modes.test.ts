// A32: producers validate strictly, consumers tolerantly (ADR-0002).
import { describe, expect, it } from "vitest";
import { validate } from "../../src/validate.ts";
import { fixtures, schemaDirs, schemaIdOf } from "../helpers.ts";

type Json = Record<string, unknown>;

/** The keys a tolerant fixture adds to some valid fixture of its schema. */
function unknownKeys(value: unknown, known: unknown): string[] {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return [];
  const out: string[] = [];
  for (const [k, v] of Object.entries(value as Json)) {
    const other = (known as Json | undefined)?.[k];
    if (other === undefined) out.push(k);
    else out.push(...unknownKeys(v, other).map((x) => `${k}.${x}`));
  }
  return out;
}

const get = (v: unknown, path: string): unknown =>
  path.split(".").reduce<unknown>((cur, k) => (cur as Json | undefined)?.[k], v);

describe("producer and consumer modes (A32)", () => {
  for (const dir of schemaDirs()) {
    const id = schemaIdOf(dir);
    const valid = fixtures(dir, "valid");
    for (const f of fixtures(dir, "tolerant")) {
      it(`${f.name}: the producer mode rejects an unknown field`, () => {
        expect(validate(id, f.value, "producer", f.options).ok).toBe(false);
      });
      it(`${f.name}: the consumer mode accepts and drops it`, () => {
        const r = validate(id, f.value, "consumer", f.options);
        expect(r.ok).toBe(true);
        if (!r.ok) return;
        const nearest = valid
          .map((v) => ({ v, extra: unknownKeys(f.value, v.value) }))
          .sort((a, b) => a.extra.length - b.extra.length)[0];
        const extra = nearest?.extra ?? [];
        expect(extra.length, `${f.name} adds one field to a valid fixture`).toBe(1);
        for (const path of extra) expect(get(r.value, path), path).toBeUndefined();
      });
    }
  }
});
