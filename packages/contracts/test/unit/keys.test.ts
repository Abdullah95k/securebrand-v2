import { describe, expect, it } from "vitest";
import {
  idempotencyKey,
  idlessCommentKey,
  instagramPostKey,
  instagramShortcodeId,
  itemId,
  linkedinCommentId,
  linkedinPostId,
  parseKey,
  telegramCommentId,
  telegramPostId,
  type InstagramMapRow,
} from "../../src/keys/index.ts";
import type { ContentKind, Platform } from "../../src/vocabulary.ts";
import { golden } from "../helpers.ts";

interface KeyCase {
  name: string;
  input: { platform: Platform; kind: ContentKind; platform_id: string };
  key: string;
  item_id: string;
}
interface KeysGolden {
  ns_items: string;
  keys: KeyCase[];
  builders: { name: string; helper: string; input: Record<string, string>; platform_id: string }[];
  parse: { key: string; platform: string; kind: string; platform_id: string }[];
  idless_comments: {
    name: string;
    input: { platform: Platform; post_id: string; created_time: string; text: string };
    rendered_time: string;
    key: string;
    item_id: string;
  }[];
  instagram_id_map: {
    name: string;
    map: InstagramMapRow[];
    read: { route: "graph" | "vendor"; media_id: string | null; shortcode: string };
    key: string;
    map_row: InstagramMapRow;
  }[];
  rejects: { name: string; input: { platform: string; kind: string; platform_id: unknown } }[];
  parse_rejects: { name: string; key: string }[];
  idless_rejects: {
    name: string;
    input: { platform: Platform; post_id: string; created_time: string; text: string };
  }[];
}

const g = golden<KeysGolden>("keys.json");

describe("idempotency keys (ADR-0006, ADR-0007)", () => {
  it.each(g.keys.map((c) => [c.name, c] as const))(
    "builds every golden key byte for byte: %s",
    (_name, c) => {
      expect(idempotencyKey(c.input.platform, c.input.kind, c.input.platform_id)).toBe(c.key);
    },
  );

  it.each(g.keys.map((c) => [c.name, c] as const))(
    "derives every golden item_id: %s",
    (_name, c) => {
      expect(itemId(c.key)).toBe(c.item_id);
    },
  );

  it("an NFD input yields the NFC key and the same item_id", () => {
    const nfd = g.keys.find((c) => c.name === "NFD id yields the NFC key");
    expect(nfd).toBeDefined();
    if (!nfd) return;
    expect(nfd.input.platform_id).not.toBe(nfd.input.platform_id.normalize("NFC"));
    const key = idempotencyKey(nfd.input.platform, nfd.input.kind, nfd.input.platform_id);
    expect(key).toBe(key.normalize("NFC"));
    expect(itemId(key.normalize("NFD"))).toBe(nfd.item_id);
  });

  it.each(g.builders.map((c) => [c.name, c] as const))(
    "builds the platform id part: %s",
    (_name, c) => {
      const i = c.input;
      const built = {
        telegram_post_id: () => telegramPostId(i.channel ?? "", i.message_id ?? ""),
        telegram_comment_id: () => telegramCommentId(i.group_chat_id ?? "", i.message_id ?? ""),
        linkedin_post_id: () => linkedinPostId(i.post_id ?? "", i.urn as "activity" | "share"),
        linkedin_comment_id: () =>
          linkedinCommentId(i.post_id ?? "", i.comment_id ?? "", i.urn as "activity" | "share"),
        instagram_shortcode_id: () => instagramShortcodeId(i.shortcode ?? ""),
      }[c.helper];
      expect(built).toBeDefined();
      expect(built?.()).toBe(c.platform_id);
    },
  );

  it.each(g.parse.map((c) => [c.key, c] as const))(
    "parses a key on its first two colons, ids holding colons and slashes included: %s",
    (_key, c) => {
      expect(parseKey(c.key)).toEqual({
        platform: c.platform,
        kind: c.kind,
        platform_id: c.platform_id,
      });
    },
  );

  it.each(g.rejects.map((c) => [c.name, c] as const))(
    "refuses a key it cannot build: %s",
    (_name, c) => {
      expect(() =>
        idempotencyKey(
          c.input.platform as Platform,
          c.input.kind as ContentKind,
          c.input.platform_id as string,
        ),
      ).toThrow();
    },
  );

  it.each(g.parse_rejects.map((c) => [c.name, c] as const))(
    "refuses to parse a malformed key: %s",
    (_name, c) => {
      expect(() => parseKey(c.key)).toThrow();
    },
  );

  it("keeps ids as strings, never numbers", () => {
    const big = "7429384756102938475";
    expect(Number(big).toString()).not.toBe(big);
    expect(idempotencyKey("tiktok", "video", big)).toBe(`tiktok:video:${big}`);
    expect(() =>
      idempotencyKey("tiktok", "video", Number(big) as unknown as string),
    ).toThrow();
  });
});

describe("id-less comment keys (ADR-0009)", () => {
  it.each(g.idless_comments.map((c) => [c.name, c] as const))(
    "builds the golden id-less key: %s",
    (_name, c) => {
      const i = c.input;
      expect(idlessCommentKey(i.platform, i.post_id, i.created_time, i.text)).toBe(c.key);
      expect(itemId(c.key)).toBe(c.item_id);
    },
  );

  it("an NFD text yields the same key as its NFC form", () => {
    const nfd = g.idless_comments.find((c) => c.name.startsWith("decomposed Arabic"));
    const nfc = g.idless_comments.find((c) => c.name === "the same text composed");
    expect(nfd?.key).toBeDefined();
    expect(nfd?.key).toBe(nfc?.key);
  });

  it("one comment read with two offsets keeps one key", () => {
    const [first, second, fractional] = g.idless_comments;
    expect(first?.key).toBe(second?.key);
    expect(first?.key).toBe(fractional?.key);
  });

  it.each(g.idless_rejects.map((c) => [c.name, c] as const))(
    "refuses a created_time: %s",
    (_name, c) => {
      const i = c.input;
      expect(() => idlessCommentKey(i.platform, i.post_id, i.created_time, i.text)).toThrow();
    },
  );
});

describe("the Instagram id map (ADR-0007)", () => {
  it.each(g.instagram_id_map.map((c) => [c.name, c] as const))("%s", (_name, c) => {
    const lookup = (shortcode: string): InstagramMapRow | null =>
      c.map.find((r) => r.shortcode === shortcode) ?? null;
    const got = instagramPostKey(
      { route: c.read.route, media_id: c.read.media_id, shortcode: c.read.shortcode },
      lookup,
    );
    expect(got.key).toBe(c.key);
    expect(got.map_row).toEqual(c.map_row);
  });

  it("a post with only a shortcode keys instagram:post:sc:<shortcode>", () => {
    const got = instagramPostKey(
      { route: "vendor", media_id: null, shortcode: "Ab_c-1" },
      () => null,
    );
    expect(got.key).toBe("instagram:post:sc:Ab_c-1");
  });

  it("a Graph read of a shortcode already mapped reuses that key", () => {
    const row: InstagramMapRow = {
      shortcode: "Ab_c-1",
      graph_media_id: null,
      key: "instagram:post:sc:Ab_c-1",
    };
    const got = instagramPostKey(
      { route: "graph", media_id: "17895695668004551", shortcode: "Ab_c-1" },
      () => row,
    );
    expect(got.key).toBe("instagram:post:sc:Ab_c-1");
  });
});
