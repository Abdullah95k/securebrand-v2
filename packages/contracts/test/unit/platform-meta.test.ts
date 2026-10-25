// A25: platform_meta keys per platform and source type (ADR-0065 c), ADR-0013 c), ADR-0041).
import { describe, expect, it } from "vitest";
import { validate } from "../../src/validate.ts";
import { copyOf, fixture, samePath } from "../helpers.ts";

type Json = Record<string, unknown>;
const ID = "registry.decisions/v1";
const failsAt = (r: ReturnType<typeof validate>, path: (string | number)[]): boolean =>
  !r.ok && r.issues.some((i) => samePath(i.path, path));

// One registered source per (platform, source type) that has platform_meta keys.
const CASES: [string, string, Json][] = [
  ["youtube", "channel", { uploads_playlist_id: "UUx3Kp9vQ2mLwR7tYb4nJ8sA" }],
  ["instagram", "hashtag", { ig_user_id: "17841400112233445" }],
  [
    "telegram",
    "group",
    {
      linked_channel_source_id: "8a3f1c6e-2b9d-4e70-b5a4-f0c9d2e1b7a8",
      linked_chat_id: "-1001987650000",
    },
  ],
];

function addWith(platform: string, sourceType: string, meta: Json): Json {
  const value = copyOf(fixture(ID, "valid", "add-telegram-group.json"));
  const source = (value.add as Json).source as Json;
  Object.assign(source, { platform, source_type: sourceType, platform_meta: meta });
  return value;
}

describe("platform_meta (A25)", () => {
  it("accepts each platform's keys", () => {
    for (const [platform, type, meta] of CASES) {
      const r = validate(ID, addWith(platform, type, meta));
      expect(r.ok ? [] : r.issues, `${platform} ${type}`).toEqual([]);
    }
    expect(validate(ID, fixture(ID, "valid", "add-keyword.json").value).ok).toBe(true);
    expect(
      validate(
        "source.events/v1",
        fixture("source.events/v1", "valid", "push-coverage-change.json").value,
      ).ok,
    ).toBe(true);
  });

  it("rejects another platform's key", () => {
    for (const [platform, type] of CASES) {
      for (const [, , meta] of CASES.filter(([p]) => p !== platform)) {
        for (const key of Object.keys(meta)) {
          const r = validate(ID, addWith(platform, type, { [key]: meta[key] }));
          expect(
            failsAt(r, ["add", "source", "platform_meta", key]),
            `${key} on ${platform} ${type}`,
          ).toBe(true);
        }
      }
    }
    // A page has no platform_meta keys at all.
    expect(
      failsAt(validate(ID, addWith("facebook", "page", { ig_user_id: "1" })), [
        "add",
        "source",
        "platform_meta",
        "ig_user_id",
      ]),
    ).toBe(true);
    const event = copyOf(fixture("source.events/v1", "valid", "prd-registry-writer.json"));
    event.platform_meta = { uploads_playlist_id: "UUx3" };
    expect(
      failsAt(validate("source.events/v1", event), ["platform_meta", "uploads_playlist_id"]),
    ).toBe(true);
  });
});
