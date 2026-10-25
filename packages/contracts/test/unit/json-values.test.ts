// The JSON-level rules validate() applies to a whole message before its schema, in both languages:
// every string and key is well-formed Unicode (finding 5).
import { describe, expect, it } from "vitest";
import { validate } from "../../src/validate.ts";
import { copyOf, fixture } from "../helpers.ts";

type Json = Record<string, unknown>;
const LONE = JSON.parse('"\\ud83d"') as string; // a high surrogate alone, as slicing an emoji leaves it
const EMOJI = "😀";

// Where a lone surrogate may land: a constrained string, a free-form payload's value, an array
// element and an object key. Each case sets `odd` there and gives the path it is reported at.
const PLACES: [string, string, string, (m: Json, odd: string) => (string | number)[]][] = [
  [
    "dlq.<service>/v1",
    "dlq/v1",
    "consume-data-message.json",
    (m, odd) => {
      (m.error as Json).message = `could not parse: ${odd}`;
      return ["error", "message"];
    },
  ],
  [
    "item.hits/v1",
    "item.hits/v1",
    "prd-keyword-matcher.json",
    (m, odd) => {
      m.matched_term = `${String(m.matched_term)}${odd}`;
      return ["matched_term"];
    },
  ],
  [
    "raw.items/v1",
    "raw.items/v1",
    "prd-fb-page-feed-poller.json",
    (m, odd) => {
      (m.payload as Json).note = odd;
      return ["payload", "note"];
    },
  ],
  [
    "raw.items/v1",
    "raw.items/v1",
    "prd-fb-page-feed-poller.json",
    (m, odd) => {
      (m.payload as Json).tags = ["ok", odd];
      return ["payload", "tags", 1];
    },
  ],
  [
    "raw.items/v1",
    "raw.items/v1",
    "prd-fb-page-feed-poller.json",
    (m, odd) => {
      (m.payload as Json)[odd] = 1;
      return ["payload", odd];
    },
  ],
];

describe("JSON values (findings 5 and note 17)", () => {
  it("refuses a lone surrogate anywhere in a message with not_unicode, in both modes, without throwing", () => {
    for (const [id, dir, file, place] of PLACES) {
      const m = copyOf(fixture(dir, "valid", file));
      const path = place(m, LONE);
      for (const mode of ["producer", "consumer"] as const) {
        let r: ReturnType<typeof validate> | undefined;
        expect(() => (r = validate(id, m, mode)), `${file} ${JSON.stringify(path)}`).not.toThrow();
        const issues = r?.ok === false ? r.issues.map((i) => ({ path: i.path, code: i.code })) : [];
        expect(issues, `${file} ${mode}`).toEqual([{ path, code: "not_unicode" }]);
      }
    }
  });

  it("accepts a well-formed emoji in the same place", () => {
    for (const [id, dir, file, place] of PLACES) {
      const m = copyOf(fixture(dir, "valid", file));
      place(m, EMOJI);
      for (const mode of ["producer", "consumer"] as const) {
        const r = validate(id, m, mode);
        expect(r.ok ? [] : r.issues, `${file} ${mode}`).toEqual([]);
      }
    }
  });
});
