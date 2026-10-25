/* eslint-disable no-control-regex -- the patterns exclude control characters on purpose */
// Primitive value types. Patterns avoid \d, \w and \s (Unicode-aware in some regex engines) and
// lookarounds, so the exported JSON Schema means the same in Zod, Pydantic and any validator.
import { z } from "zod";
import { CONTENT_KINDS, PLATFORMS } from "./vocabulary.ts";

const PLATFORM_GROUP = PLATFORMS.join("|");

export const PATTERNS = {
  // Lower-case canonical UUID (ADR-0006, ADR-0042).
  uuid: /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/,
  // ULID: 26 Crockford base32 characters, the first at most 7 (ADR-0006).
  ulid: /^[0-7][0-9A-HJKMNP-TV-Z]{25}$/,
  // RFC 3339 in UTC with Z, seconds required, up to three fractional digits (VERSIONING.md).
  timestamp:
    /^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]{1,3})?Z$/,
  date: /^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/,
  sha256Hex: /^[0-9a-f]{64}$/,
  prefixedSha256: /^sha256:[0-9a-f]{64}$/,
  keywordSetVersion: /^cs:[0-9a-f]{64}$/,
  // Service names and vendors are registry data, typed as patterned strings (Q1, F-09).
  service: /^[a-z0-9]+(-[a-z0-9]+)*$/,
  snakeName: /^[a-z][a-z0-9_]*$/,
  // The four candidate key forms (ADR-0032); a LinkedIn id is an organisation URN, colons included.
  candidateKey:
    /^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\x00-\x20:]+|linkedin:[^\x00-\x20]+)$/,
  // Item keys per platform (ADR-0007, ADR-0036, ADR-0038); the kind segment of an X reply is post.
  idempotencyKey:
    /^(((facebook|instagram|linkedin|telegram):(post|comment)|(tiktok|youtube):(video|comment)|x:post|news:comment):[^\x00-\x20]+|(news:article|web:result):[0-9a-f]{64})$/,
  rawRef: new RegExp(
    `^raw/(green|amber)/(${PLATFORM_GROUP})/[0-9]{4}/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/[a-z0-9]+(-[a-z0-9]+)*/[0-9]{6}\\.jsonl\\.zst#[0-9]+$`,
  ),
  httpUrl: /^https?:\/\/[^\x00-\x20]+$/,
  host: /^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\.?$/,
  token: /^[^\x00-\x20]+$/,
  // comment-decay-scheduler's steps (§5.1, §6.2; ADR-0011, ADR-0060).
  seriesStep: /^(\+[1-9][0-9]*[hd]|once|hot:[1-9][0-9]*|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$/,
  // A metrics job's step and an observation's refresh step (ADR-0034).
  metricsStep: /^(\+24h|\+7d|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$/,
  // Analysis task names hold no colon (ADR-0023).
  analysisTask:
    /^(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\.[A-Za-z0-9_.-]+)$/,
  modelVersion: /^[^\x00-\x20:]+$/,
  topicsTask: /^topics\.[A-Za-z0-9_.-]+$/,
  analysisKey:
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\.[A-Za-z0-9_.-]+):[^\x00-\x20:]+$/,
  topicId: /^[A-Za-z0-9_.-]+:[^\x00-\x20]+$/,
  urlKey: /^news:url:[0-9a-f]{64}$/,
  // del:<reason>:<scope>:<hex> (Q2; ADR-0035).
  deletionId:
    /^del:(platform_sync|retention|author_request|client_offboarding|legal|authorization_revoked|client_request):(item|author|source|client):[0-9a-f]{64}$/,
  // The one schema id that is a pattern (Q5, F-52).
  dlqSchema: /^dlq\.[a-z0-9]+(-[a-z0-9]+)*\/v1$/,
  digits: /^[0-9]+$/,
  // A job queue: jobs.<service>, or an analysis service's jobs.<service>.priority lane (ADR-0023).
  queue: /^jobs\.[a-z0-9]+(-[a-z0-9]+)*(\.priority)?$/,
  base64: /^[A-Za-z0-9+/]*={0,2}$/,
  // A Telegram chat id: a group's or channel's is negative.
  chatId: /^-?[0-9]+$/,
  // An ISO 3166-1 alpha-2 country code.
  country: /^[A-Z]{2}$/,
} as const;
/* eslint-enable no-control-regex -- end of the patterns */

export const CONTENT_KIND_GROUP = CONTENT_KINDS.join("|");

export const uuid = (): z.ZodString => z.string().regex(PATTERNS.uuid);
export const ulid = (): z.ZodString => z.string().regex(PATTERNS.ulid);
export const timestamp = (): z.ZodString => z.string().regex(PATTERNS.timestamp);
export const date = (): z.ZodString => z.string().regex(PATTERNS.date);
export const sha256Hex = (): z.ZodString => z.string().regex(PATTERNS.sha256Hex);
export const prefixedSha256 = (): z.ZodString => z.string().regex(PATTERNS.prefixedSha256);
export const authorRef = (): z.ZodString => z.string().regex(PATTERNS.sha256Hex);
export const serviceName = (): z.ZodString => z.string().regex(PATTERNS.service);
export const vendorName = (): z.ZodString => z.string().regex(PATTERNS.service);
export const snakeName = (): z.ZodString => z.string().regex(PATTERNS.snakeName);
export const candidateKey = (): z.ZodString => z.string().regex(PATTERNS.candidateKey);
export const idempotencyKey = (): z.ZodString => z.string().regex(PATTERNS.idempotencyKey);
export const rawRef = (): z.ZodString => z.string().regex(PATTERNS.rawRef);
export const httpUrl = (): z.ZodString => z.string().regex(PATTERNS.httpUrl);
export const host = (): z.ZodString => z.string().regex(PATTERNS.host);
export const token = (): z.ZodString => z.string().regex(PATTERNS.token);
export const seriesStep = (): z.ZodString => z.string().regex(PATTERNS.seriesStep);
export const metricsStep = (): z.ZodString => z.string().regex(PATTERNS.metricsStep);
export const nonEmpty = (): z.ZodString => z.string().min(1);
// A platform id is a string, never a number: X and TikTok ids exceed 2^53 (ADR-0007).
export const platformId = (): z.ZodString => z.string().regex(PATTERNS.token);
export const count = (): z.ZodNumber => z.number().int().min(0);
export const share = (): z.ZodNumber => z.number().min(0).max(1);
// D3 sets the form of a person's reference; a service writes its own name (ADR-0012).
export const actor = (): z.ZodString => z.string().min(1).max(256);
