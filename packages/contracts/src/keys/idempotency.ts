// The one key helper (ADR-0006) with the per-platform forms of ADR-0007, ADR-0009, ADR-0036 and
// ADR-0038. Keys split on the first two colons only, so an id may hold ':' or '/'.
import { ContractError } from "../errors.ts";
import { PATTERNS } from "../primitives.ts";
import { CONTENT_KINDS, PLATFORMS, type ContentKind, type Platform } from "../vocabulary.ts";
import { nfc, requireString, sha256Hex } from "./text.ts";
import { renderKeyTime } from "./time.ts";

// The kind segments each platform keys; an X reply's item kind is comment, its segment post.
const SEGMENTS: Record<Platform, Partial<Record<ContentKind, string>>> = {
  facebook: { post: "post", comment: "comment" },
  instagram: { post: "post", comment: "comment" },
  tiktok: { video: "video", comment: "comment" },
  x: { post: "post", comment: "post" },
  linkedin: { post: "post", comment: "comment" },
  telegram: { post: "post", comment: "comment" },
  youtube: { video: "video", comment: "comment" },
  news: { article: "article", comment: "comment" },
  web: { result: "result" },
};
const HEX_ID_SEGMENTS = new Set(["news:article", "web:result"]);
// eslint-disable-next-line no-control-regex -- control characters are what the pattern refuses
const ID_CHARS = /^[^\x00-\x20]+$/;

function isPlatform(p: string): p is Platform {
  return (PLATFORMS as readonly string[]).includes(p);
}

/** The kind segment of an item key: the item kind, except an X reply's, which is post. */
export function keySegment(platform: Platform, kind: ContentKind): string {
  if (!isPlatform(platform)) throw new ContractError("bad_platform", String(platform));
  if (!(CONTENT_KINDS as readonly string[]).includes(kind))
    throw new ContractError("bad_kind", String(kind));
  const segment = SEGMENTS[platform][kind];
  if (!segment) throw new ContractError("bad_kind", `${platform} keys no ${kind}`);
  return segment;
}

export function idempotencyKey(platform: Platform, kind: ContentKind, platformId: string): string {
  const segment = keySegment(platform, kind);
  const id = nfc(requireString(platformId, "platform_id"));
  if (!ID_CHARS.test(id))
    throw new ContractError("bad_platform_id", "empty or holds a space or control character");
  if (HEX_ID_SEGMENTS.has(`${platform}:${segment}`) && !PATTERNS.sha256Hex.test(id)) {
    throw new ContractError("bad_platform_id", `${platform}:${segment} takes 64 lower-case hex`);
  }
  return nfc(`${platform}:${segment}:${id}`);
}

export interface ParsedKey {
  platform: Platform;
  kind: string;
  platform_id: string;
}

export function parseKey(key: string): ParsedKey {
  requireString(key, "key");
  const first = key.indexOf(":");
  const second = first < 0 ? -1 : key.indexOf(":", first + 1);
  if (second < 0) throw new ContractError("bad_key", `${key} has fewer than three segments`);
  const platform = key.slice(0, first);
  const kind = key.slice(first + 1, second);
  const id = key.slice(second + 1);
  if (!isPlatform(platform)) throw new ContractError("bad_key", `unknown platform in ${key}`);
  if (!Object.values(SEGMENTS[platform]).includes(kind))
    throw new ContractError("bad_key", `${platform} keys no ${kind}`);
  if (!ID_CHARS.test(id)) throw new ContractError("bad_key", `${key} has an empty or spaced id`);
  if (HEX_ID_SEGMENTS.has(`${platform}:${kind}`) && !PATTERNS.sha256Hex.test(id)) {
    throw new ContractError("bad_key", `${key} needs a 64 lower-case hex id`);
  }
  return { platform, kind, platform_id: id };
}

const USERNAME = /^[A-Za-z][A-Za-z0-9_]*$/;
const CHAT_ID = /^-?[0-9]+$/;
const DIGITS = /^[0-9]+$/;

/** `<lowercase username>/<message_id>`, or the chat id for a channel without a username. */
export function telegramPostId(channel: string, messageId: string): string {
  requireString(channel, "channel");
  if (!DIGITS.test(messageId))
    throw new ContractError("bad_platform_id", "message id must be digits");
  if (CHAT_ID.test(channel)) return `${channel}/${messageId}`;
  if (!USERNAME.test(channel)) throw new ContractError("bad_platform_id", `channel ${channel}`);
  return `${channel.toLowerCase()}/${messageId}`;
}

export function telegramCommentId(groupChatId: string, messageId: string): string {
  if (!CHAT_ID.test(groupChatId))
    throw new ContractError("bad_platform_id", "group chat id must be a number");
  if (!DIGITS.test(messageId))
    throw new ContractError("bad_platform_id", "message id must be digits");
  return `${groupChatId}/${messageId}`;
}

/** The activity or share URN form, chosen by an explicit argument (ADR-0007; LI0 decides). */
export function linkedinPostId(postId: string, urn: "activity" | "share"): string {
  if (!DIGITS.test(postId)) throw new ContractError("bad_platform_id", "post id must be digits");
  if (urn !== "activity" && urn !== "share")
    throw new ContractError("bad_platform_id", `urn ${String(urn)}`);
  return `urn:li:${urn}:${postId}`;
}

export function linkedinCommentId(
  postId: string,
  commentId: string,
  urn: "activity" | "share",
): string {
  if (!DIGITS.test(commentId))
    throw new ContractError("bad_platform_id", "comment id must be digits");
  return `urn:li:comment:(${linkedinPostId(postId, urn)},${commentId})`;
}

const SHORTCODE = /^[A-Za-z0-9_-]+$/;

export function instagramShortcodeId(shortcode: string): string {
  if (!SHORTCODE.test(shortcode))
    throw new ContractError("bad_platform_id", `shortcode ${shortcode}`);
  return `sc:${shortcode}`;
}

/** `<platform>:comment:<post id>:<hex sha256 of NFC(created_time + text)>` (ADR-0009). */
export function idlessCommentKey(
  platform: Platform,
  postId: string,
  createdTime: string,
  text: string,
): string {
  requireString(postId, "post_id");
  requireString(text, "text");
  const hash = sha256Hex(nfc(renderKeyTime(requireString(createdTime, "created_time")) + text));
  return idempotencyKey(platform, "comment", `${postId}:${hash}`);
}

export { renderKeyTime };
