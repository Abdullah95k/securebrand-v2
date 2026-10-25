// Scrubbing: raw vendor responses in, committable fixture out. Rules (.claude/rules/fixtures.md):
// no tokens or signed URLs; handles, names and ids of private individuals replaced by stable fakes
// (the same input gives the same fake everywhere); ids of public outlets, companies and channels kept.
// A social-media result is a private individual until its handle is in public-accounts.txt.
import { createHash } from "node:crypto";
import { redact } from "./redact.ts";

const SOCIAL_HOSTS = [
  "facebook.com",
  "instagram.com",
  "x.com",
  "twitter.com",
  "tiktok.com",
  "youtube.com",
  "youtu.be",
  "t.me",
  "telegram.me",
  "linkedin.com",
  "snapchat.com",
  "threads.net",
  "threads.com",
  "reddit.com",
];

// Signed-URL parameters, as scripts/check-fixtures.sh knows them, plus API keys.
const SIGNED =
  /([?&;])(x-amz-signature|x-goog-signature|x-signature|signature|sig|oh|access_token|api_key|apikey)=[^&\s"'\\]*/gi;

export function stableFake(kind: string, value: string): string {
  return `${kind}-${createHash("sha256").update(value.toLowerCase()).digest("hex").slice(0, 8)}`;
}

export function parseAllowlist(content: string): Set<string> {
  return new Set(
    content
      .split(/\r?\n/)
      .map((l) => l.trim().toLowerCase().replace(/^@/, ""))
      .filter((l) => l !== "" && !l.startsWith("#")),
  );
}

export function socialHost(url: string): string | undefined {
  let host: string;
  try {
    host = new URL(url).hostname.toLowerCase();
  } catch {
    return undefined;
  }
  return SOCIAL_HOSTS.find((h) => host === h || host.endsWith(`.${h}`));
}

/** Path segments that name a page type, not a person; they stay. */
const STRUCTURAL = new Set([
  "p",
  "reel",
  "reels",
  "tv",
  "watch",
  "status",
  "videos",
  "video",
  "posts",
  "photo",
  "photos",
  "channel",
  "c",
  "user",
  "groups",
  "pages",
  "hashtag",
  "explore",
  "company",
  "in",
  "s",
  "u",
  "r",
]);

/** The account-like segments of a social URL: first non-structural path segment, and an @handle anywhere. */
export function accountSegments(url: string): string[] {
  let u: URL;
  try {
    u = new URL(url);
  } catch {
    return [];
  }
  const out: string[] = [];
  for (const seg of u.pathname.split("/").filter(Boolean)) {
    const s = decodeURIComponent(seg).replace(/^@/, "");
    if (!STRUCTURAL.has(s.toLowerCase()) && !/^\d{1,3}$/.test(s)) out.push(s);
  }
  return out;
}

export interface ScrubContext {
  allow: Set<string>;
  /** Strings that were replaced; the scrubbing test checks none of them survives in a fixture. */
  replaced: Set<string>;
}

function scrubSocialUrl(url: string, ctx: ScrubContext): string {
  const segs = accountSegments(url);
  if (segs.length > 0 && segs.every((s) => ctx.allow.has(s.toLowerCase()))) return url;
  let out = url;
  for (const s of segs) {
    if (ctx.allow.has(s.toLowerCase())) continue;
    ctx.replaced.add(s);
    out = out
      .split(encodeURIComponent(s))
      .join(stableFake("acct", s))
      .split(s)
      .join(stableFake("acct", s));
  }
  return out;
}

/** Keeps the shape of a title ("<name> • Instagram photos and videos") but swaps the name. */
function scrubSocialTitle(title: string, ctx: ScrubContext): string {
  const m = /^(.*?)(\s[•|\-–—]\s.*)?$/su.exec(title);
  const name = (m?.[1] ?? title).trim();
  if (name === "") return title;
  ctx.replaced.add(name);
  return `${stableFake("name", name)}${m?.[2] ?? ""}`;
}

function scrubString(value: string): string {
  return redact(value).replace(SIGNED, "$1$2=REDACTED");
}

/**
 * Walks a parsed JSON response. An object with a `url` on a social host is a social result: its URL
 * account segments, title name and snippet are replaced. Everything else only loses tokens.
 */
export function scrubValue(value: unknown, ctx: ScrubContext): unknown {
  if (typeof value === "string") return scrubString(value);
  if (Array.isArray(value)) return value.map((v) => scrubValue(v, ctx));
  if (value !== null && typeof value === "object") {
    const obj = value as Record<string, unknown>;
    const url = typeof obj["url"] === "string" ? obj["url"] : undefined;
    const social =
      url !== undefined && socialHost(url) !== undefined && scrubSocialUrl(url, ctx) !== url;
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(obj)) {
      if (social && typeof v === "string") {
        if (k === "url") {
          out[k] = scrubString(scrubSocialUrl(v, ctx));
          continue;
        }
        if (k === "title") {
          out[k] = scrubString(scrubSocialTitle(v, ctx));
          continue;
        }
        if (k === "snippet" || k === "desc" || k === "description" || k === "text") {
          ctx.replaced.add(v);
          out[k] = `[scrubbed snippet, ${v.length} chars]`;
          continue;
        }
      }
      out[k] = scrubValue(v, ctx);
    }
    return out;
  }
  return value;
}

/** Counts, timings and field names only: for Mojeek's Startup plan, whose terms forbid storing results. */
export function shapeOnly(value: unknown, depth = 0): unknown {
  if (Array.isArray(value))
    return {
      type: "array",
      length: value.length,
      item: value.length > 0 ? shapeOnly(value[0], depth + 1) : null,
    };
  if (value !== null && typeof value === "object") {
    if (depth > 6) return { type: "object" };
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([k, v]) => [
        k,
        shapeOnly(v, depth + 1),
      ]),
    );
  }
  return { type: value === null ? "null" : typeof value };
}
