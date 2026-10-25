// validate(): the contract check every producer and consumer runs (ADR-0002, ADR-0012). Three layers,
// each reported as issues with the path of the field at fault:
// 1. the message as JSON (well-formed Unicode, finite numbers, at most 64 levels below a top-level
//    field, no `__proto__` key; D-5), then the Zod schema of the mode (producer strict, consumer
//    tolerant of unknown fields);
// 2. the rules a schema cannot state, in both modes: keys equal to the key helpers' output, fields that
//    go together, a control message refusing provenance (ADR-0003, ADR-0006);
// 3. the registry data, in producer mode only, because it grows inside the version (Q1, F-09): known
//    service names, vendors by route, topic writers, the decision rows and their Provenance column
//    (F-14), the keys each producer declares in `context` and `extras`. A job's producer-table row,
//    required fields and partition key are checked in both modes when the queue is given: the
//    consumer's job wrapper dead-letters a job with no row (ADR-0012). A jobs.completed report's
//    partition key and X fields are checked in consumer mode only for a service the package knows
//    (D-9), so a report from a service a newer package adds is not refused.
// Layer 3 runs only when layer 2 found nothing, so an issue names the first rule broken.
import type { z } from "zod";
import { createBuilder, type Mode } from "./builder.ts";
import { catalogueId, schemaFor } from "./catalogue.ts";
import { REPORT_KIND_FIELDS } from "./jobs-completed.ts";
import { provenance, signalProvenance } from "./metadata.ts";
import { PATTERNS } from "./primitives.ts";
import {
  analysisKey,
  articleKey,
  cardId,
  canonicalUrlHash,
  deletionId,
  hitId,
  hitMessageId,
  idempotencyKey,
  itemId,
  parseCandidateKey,
  parseKey,
  parseRawRef,
  urlHash,
  urlKey,
} from "./keys/index.ts";
import {
  PLATFORM_GROUPS,
  allowedProducers,
  declaredContextKeys,
  declaredExtrasKeys,
  decisionRow,
  dlqService,
  getPath,
  hasValue,
  isAllowedTopicWriter,
  isKnownService,
  isKnownVendor,
  isListedVendor,
  jobKeyFields,
  queueService,
  refusedJobFields,
  requiredJobFields,
  writerConditions,
  type DecisionSubject,
} from "./registries/index.ts";
import {
  CLIENT_TYPES,
  CONTENT_KINDS,
  FETCH_DELETION_REASONS,
  FLAG_REASONS,
  GOVERNMENT_ALERT_RULE_TYPES,
  ORGANISATION_ACCOUNT_TYPES,
  PERSON_ACCOUNT_TYPES,
  PERSON_UNLISTABLE_PLATFORMS,
  PROFILE_REVIEW_REASONS,
  PROFILE_UNRESOLVABLE_REASONS,
  RETENTION_CLASSES,
  type ContentKind,
  type Platform,
} from "./vocabulary.ts";

export type IssuePath = (string | number)[];

export interface ValidationIssue {
  readonly path: IssuePath;
  readonly code: string;
  readonly message: string;
}

export type ValidationResult =
  | { readonly ok: true; readonly value: unknown }
  | { readonly ok: false; readonly issues: readonly ValidationIssue[] };

export type ClientType = "commercial" | "government";

export interface ValidateOptions {
  /** The queue a job goes to or came from, which job/v1's producer-table row and key depend on. */
  readonly queue?: string;
  /** The client type of an n8n notice's client, which the government rule depends on. */
  readonly clientType?: ClientType;
}

type Json = Record<string, unknown>;

const isRecord = (v: unknown): v is Json =>
  typeof v === "object" && v !== null && !Array.isArray(v);
const rec = (v: unknown): Json => (isRecord(v) ? v : {});
const str = (v: unknown): string | undefined => (typeof v === "string" ? v : undefined);
const includes = (list: readonly string[], v: unknown): boolean =>
  typeof v === "string" && list.includes(v);

/** Structural JSON equality, key order aside; it walks without recursion and never throws. */
function jsonEqual(a: unknown, b: unknown): boolean {
  const pending: [unknown, unknown][] = [[a, b]];
  for (let pair = pending.pop(); pair !== undefined; pair = pending.pop()) {
    const [x, y] = pair;
    if (Array.isArray(x) || Array.isArray(y)) {
      if (!Array.isArray(x) || !Array.isArray(y) || x.length !== y.length) return false;
      x.forEach((v, i) => pending.push([v, y[i]]));
    } else if (isRecord(x) || isRecord(y)) {
      if (!isRecord(x) || !isRecord(y)) return false;
      const keys = Object.keys(x);
      if (keys.length !== Object.keys(y).length) return false;
      for (const k of keys) {
        if (!Object.hasOwn(y, k)) return false;
        pending.push([x[k], y[k]]);
      }
    } else if (x !== y) return false;
  }
  return true;
}

/** The value a key helper derives, or undefined when the helper refuses its input. */
function derive<T>(f: () => T): T | undefined {
  try {
    return f();
  } catch {
    return undefined;
  }
}

class Issues {
  readonly list: ValidationIssue[] = [];
  add(path: IssuePath, code: string, message: string): void {
    this.list.push({ path, code, message });
  }
}

// --- JSON values -----------------------------------------------------------------------------------

const isPlainObject = (v: unknown): v is Json =>
  isRecord(v) && [Object.prototype, null].includes(Object.getPrototypeOf(v) as object | null);

const NOT_UNICODE =
  "a string or key is well-formed Unicode, UTF-8 encodable (ADR-0006); this one holds a lone surrogate";

// A container nested deeper below a message's top-level field, a free-form payload, body or dead
// letter's message counted from that value, is refused (D-5).
const MAX_DEPTH = 64;

/**
 * What a message must be as JSON before its schema runs, as Python checks it on reading: every string
 * and key is well-formed Unicode, so a lone surrogate (what a UTF-16 slice through an emoji leaves) is
 * refused alike in both languages (review finding 5); a number is finite; no container is nested
 * more than MAX_DEPTH levels below a top-level field; and no key is `__proto__` (D-5). Depth first,
 * an object's keys before its values, without recursion; it never throws.
 */
function jsonIssues(value: unknown): ValidationIssue[] {
  const out: ValidationIssue[] = [];
  const pending: [unknown, IssuePath][] = [[value, []]];
  for (let next = pending.pop(); next !== undefined; next = pending.pop()) {
    const [v, path] = next;
    if (typeof v === "string") {
      if (!v.isWellFormed()) out.push({ path, code: "not_unicode", message: NOT_UNICODE });
    } else if (typeof v === "number") {
      if (!Number.isFinite(v)) out.push({ path, code: "not_json", message: "a number is finite" });
    } else if ((Array.isArray(v) || isPlainObject(v)) && path.length > MAX_DEPTH) {
      out.push({ path, code: "not_json", message: `nested deeper than ${MAX_DEPTH} levels` });
    } else if (Array.isArray(v)) {
      for (let i = v.length - 1; i >= 0; i--) pending.push([v[i], [...path, i]]);
    } else if (isPlainObject(v)) {
      const entries = Object.entries(v);
      for (const [key] of entries) {
        if (!key.isWellFormed())
          out.push({ path: [...path, key], code: "not_unicode", message: NOT_UNICODE });
        else if (key === "__proto__")
          out.push({ path: [...path, key], code: "not_json", message: "no key is __proto__" });
      }
      // undefined is no JSON value: JSON.stringify drops it, and the schema judges a missing field.
      for (const [key, x] of entries.reverse())
        if (x !== undefined && key !== "__proto__") pending.push([x, [...path, key]]);
    }
  }
  return out;
}

// --- Zod issues ------------------------------------------------------------------------------------

/** One issue per failing field: a union's branches are listed, and each unknown key gets its path. */
function zodIssues(issues: readonly z.core.$ZodIssue[], base: IssuePath = []): ValidationIssue[] {
  const out: ValidationIssue[] = [];
  for (const issue of issues) {
    const path = [...base, ...(issue.path as IssuePath)];
    if (issue.code === "invalid_union" && issue.errors.length > 0) {
      for (const branch of issue.errors) out.push(...zodIssues(branch, path));
    } else if (issue.code === "unrecognized_keys") {
      for (const key of issue.keys) {
        out.push({ path: [...path, key], code: issue.code, message: `unknown field ${key}` });
      }
    } else out.push({ path, code: issue.code, message: issue.message });
  }
  return out;
}

// --- shared rules ----------------------------------------------------------------------------------

/** An item key equals the key helper's output for its platform, kind and id (ADR-0006). */
function checkItemKey(
  out: Issues,
  path: IssuePath,
  platform: unknown,
  kind: unknown,
  platformId: unknown,
  key: unknown,
): void {
  const want = derive(() =>
    idempotencyKey(platform as Platform, kind as ContentKind, platformId as string),
  );
  if (want !== key)
    out.add(path, "key_mismatch", `the key is the helper's output, ${want ?? "none"}`);
}

/** platform_meta keys belong to one platform and source type (ADR-0065 c), ADR-0013 c), ADR-0041). */
function platformMetaKeys(platform: unknown, sourceType: unknown): readonly string[] {
  if (platform === "youtube" && sourceType === "channel") return ["uploads_playlist_id"];
  if (platform === "instagram" && sourceType === "hashtag") return ["ig_user_id"];
  if (platform === "telegram" && sourceType === "group")
    return ["linked_channel_source_id", "linked_chat_id"];
  return [];
}

function checkPlatformMeta(out: Issues, path: IssuePath, columns: Json): void {
  if (!isRecord(columns.platform_meta)) return;
  if (columns.platform === undefined || columns.source_type === undefined) return; // a partial update
  const allowed = platformMetaKeys(columns.platform, columns.source_type);
  for (const key of Object.keys(columns.platform_meta)) {
    if (!allowed.includes(key)) {
      out.add(
        [...path, key],
        "platform_meta_key",
        `${key} is no ${str(columns.platform) ?? ""} ${str(columns.source_type) ?? ""} key`,
      );
    }
  }
}

/**
 * The keys of the open maps (reaction types, metric names, languages) are snake_case (F-34): a rule
 * here because a key pattern is a construct the Python generator cannot render (ADR-0030).
 */
function checkSnakeKeys(out: Issues, path: IssuePath, map: unknown): void {
  if (!isRecord(map)) return;
  for (const key of Object.keys(map)) {
    if (!PATTERNS.snakeName.test(key))
      out.add([...path, key], "key_pattern", `${key} is not snake_case`);
  }
}

/** provenance and retention_class travel together (ADR-0003). */
function checkPairing(out: Issues, m: Json, prefix: IssuePath = []): void {
  const p = m.provenance !== undefined;
  const c = m.retention_class !== undefined;
  if (p && !c)
    out.add(
      [...prefix, "retention_class"],
      "class_without_provenance",
      "provenance travels with retention_class",
    );
  if (c && !p)
    out.add(
      [...prefix, "provenance"],
      "provenance_without_class",
      "retention_class travels with provenance",
    );
}

/** A control message carries producer and no provenance (ADR-0003), in either mode. */
function refuseProvenance(out: Issues, raw: Json): void {
  if (raw.provenance !== undefined)
    out.add(["provenance"], "provenance_refused", "a control message carries producer only");
}

// --- per-schema rules (both modes) -----------------------------------------------------------------

type Rule = (
  m: Json,
  out: Issues,
  ctx: { schemaId: string; mode: Mode; options: ValidateOptions },
) => void;

const rawItems: Rule = (m, out) => {
  const env = rec(m.envelope);
  const hasSource = env.source_id !== undefined;
  const hasCandidate = env.candidate_key !== undefined;
  if (!hasSource && !hasCandidate)
    out.add(
      ["envelope", "source_id"],
      "missing_subject",
      "a record carries source_id or candidate_key (ADR-0005 L28)",
    );
  if (hasSource && hasCandidate)
    out.add(
      ["envelope", "candidate_key"],
      "two_subjects",
      "a record carries source_id or candidate_key, never both",
    );
  if (includes(CONTENT_KINDS, env.kind))
    checkItemKey(
      out,
      ["envelope", "idempotency_key"],
      env.platform,
      env.kind,
      env.platform_id,
      env.idempotency_key,
    );
  // Plan L165 (D-10): only web-commoncrawl-scanner's aggregate is keyed by a candidate; every other
  // search response by its rule's source_id.
  if (env.kind === "search_response") {
    const aggregate = rec(env.provenance).service === "web-commoncrawl-scanner";
    if (aggregate && !hasCandidate)
      out.add(
        ["envelope", "candidate_key"],
        "missing_subject",
        "web-commoncrawl-scanner's aggregate is keyed by its candidate (plan L165)",
      );
    if (!aggregate && hasCandidate)
      out.add(
        ["envelope", "source_id"],
        "missing_subject",
        "a search response is keyed by its rule's source_id (plan L165)",
      );
  }
  // An article is keyed by its canonical URL (plan L165; ADR-0036); a null one is not checked.
  const canonical = rec(m.payload).canonical_url;
  if (env.kind === "article" && typeof canonical === "string") {
    const want = derive(() => articleKey(canonical));
    if (want !== env.idempotency_key)
      out.add(
        ["envelope", "idempotency_key"],
        "key_mismatch",
        `an article is keyed by its canonical URL, ${want ?? "none"}`,
      );
  }
  const ref = derive(() => parseRawRef(str(env.raw_ref) ?? ""));
  if (ref !== undefined) {
    if (ref.route !== rec(env.provenance).route || ref.platform !== env.platform)
      out.add(
        ["envelope", "raw_ref"],
        "raw_ref_mismatch",
        "raw_ref names the record's own route and platform",
      );
  }
};

const itemsNormalized: Rule = (m, out) => {
  checkItemKey(out, ["idempotency_key"], m.platform, m.kind, m.platform_id, m.idempotency_key);
  checkSnakeKeys(
    out,
    ["metrics_snapshot", "reactions_by_type"],
    rec(m.metrics_snapshot).reactions_by_type,
  );
  if (derive(() => itemId(str(m.idempotency_key) ?? "")) !== m.item_id)
    out.add(
      ["item_id"],
      "item_id_mismatch",
      "item_id = uuid_v5(ns_items, idempotency_key) (ADR-0006)",
    );
  const author = rec(m.author);
  const registered = author.author_source_id !== null && author.author_source_id !== undefined;
  for (const name of ["display_name", "author_followers"]) {
    if (author[name] !== undefined && !registered)
      out.add(
        ["author", name],
        "source_only",
        `${name} only for a registered source (ADR-0010, ADR-0070 d))`,
      );
  }
  if (author.author_type === "source" && !registered)
    out.add(
      ["author", "author_source_id"],
      "source_without_id",
      "author_type source names its registered source",
    );
  if (author.author_type !== "source" && registered)
    out.add(["author", "author_type"], "id_without_source", "an author_source_id is a source's");
  if (m.poster_platform_id !== undefined && registered)
    out.add(
      ["poster_platform_id"],
      "poster_of_source",
      "poster_platform_id never beside author_source_id (ADR-0031)",
    );
};

const itemHits: Rule = (m, out) => {
  const want = derive(() =>
    hitId(str(m.item_id) ?? "", str(m.client_id) ?? "", str(m.keyword_id) ?? ""),
  );
  if (want !== m.hit_id)
    out.add(
      ["hit_id"],
      "hit_id_mismatch",
      "hit_id = uuid_v5(ns_hits, item:client:keyword) (ADR-0006)",
    );
  const id = derive(() =>
    hitMessageId({
      hit_at: str(m.hit_at) ?? "",
      hit_id: str(m.hit_id) ?? "",
      item_version: m.item_version as number,
      keyword_set_version: str(m.keyword_set_version) ?? "",
    }),
  );
  if (id !== m.message_id)
    out.add(
      ["message_id"],
      "message_id_mismatch",
      "a hit's message_id is the deterministic ULID (ADR-0006)",
    );
};

const discoveryHits: Rule = (m, out) => {
  const evidence = rec(m.evidence);
  checkSnakeKeys(out, ["evidence", "public_metrics"], evidence.public_metrics);
  checkSnakeKeys(out, ["evidence", "language_share"], evidence.language_share);
  if (m.item_id !== null && m.url !== null)
    out.add(["url"], "item_and_url", "exactly one of item_id and url (ADR-0031)");
  if (m.item_id === null && m.url === null)
    out.add(["item_id"], "neither_item_nor_url", "exactly one of item_id and url (ADR-0031)");
  const candidate = rec(m.candidate);
  const platform = derive(() => parseCandidateKey(str(candidate.candidate_key) ?? "").platform);
  if (platform !== candidate.platform)
    out.add(
      ["candidate", "platform"],
      "candidate_platform",
      "the candidate's platform is its key's",
    );
};

const posterProfiles: Rule = (m, out) => {
  const status = m.status;
  if (status === "resolved" && m.reason !== null)
    out.add(["reason"], "reason_with_resolved", "a resolved answer carries no reason");
  if (status === "review" && !includes(PROFILE_REVIEW_REASONS, m.reason))
    out.add(["reason"], "review_reason", "a review answer names a review reason (ADR-0033)");
  if (status === "unresolvable" && !includes(PROFILE_UNRESOLVABLE_REASONS, m.reason))
    out.add(
      ["reason"],
      "unresolvable_reason",
      "an unresolvable answer names an unresolvable reason (ADR-0033)",
    );
  if (m.candidate_key === undefined) return; // an ordinary individual's minimised answer
  const keyPlatform = derive(() => parseCandidateKey(str(m.candidate_key) ?? "").platform);
  if (keyPlatform !== m.platform)
    out.add(
      ["candidate_key"],
      "candidate_platform",
      "the candidate key's platform is the profile's",
    );
  const type = m.account_type;
  if (type === null) {
    if (m.individual !== null)
      out.add(
        ["individual"],
        "individual_without_type",
        "no individual flag without an account_type",
      );
    if (m.public_account !== null)
      out.add(
        ["public_account"],
        "public_without_type",
        "no public_account without an account_type",
      );
    return;
  }
  if (m.public_account === null)
    out.add(
      ["public_account"],
      "public_unmarked",
      "a typed account is marked public or not (ADR-0010 L59, ADR-0033 L26)",
    );
  if (m.individual !== (type === "individual"))
    out.add(
      ["individual"],
      "individual_flag",
      "individual is true exactly when account_type is individual (ADR-0033)",
    );
  if (type === "individual" && m.public_account === false)
    out.add(
      ["public_account"],
      "individual_full_set",
      "an ordinary individual's answer is the minimised one (ADR-0033)",
    );
  if (includes(ORGANISATION_ACCOUNT_TYPES, type) && m.public_account !== true)
    out.add(
      ["public_account"],
      "organisation_public",
      "an organisation kind is a public account (ADR-0010)",
    );
  if (
    includes(PERSON_ACCOUNT_TYPES, type) &&
    includes(PERSON_UNLISTABLE_PLATFORMS, m.platform) &&
    m.public_account !== false
  )
    out.add(
      ["public_account"],
      "person_unlistable",
      "no person's account is listable on this platform (ADR-0010 L70-L72)",
    );
};

const SUBJECTS: readonly DecisionSubject[] = [
  "candidate_key",
  "author_ref",
  "source_id",
  "keyword_id",
  "platform",
];

const registryDecisions: Rule = (m, out) => {
  const present = SUBJECTS.filter((s) => m[s] !== undefined);
  if (present.length > 1)
    for (const s of present.slice(1))
      out.add([s], "two_subjects", "a decision carries exactly one subject (ADR-0013)");
  checkPairing(out, m);
  const decision = str(m.decision) ?? "";
  const block = rec(m[decision]);
  if ((decision === "add" || decision === "update") && isRecord(block.source)) {
    checkPlatformMeta(out, [decision, "source", "platform_meta"], block.source);
  }
  if (decision === "add" && m.source_id !== undefined && block.proposed_source_id !== m.source_id)
    out.add(
      ["add", "proposed_source_id"],
      "owned_id",
      "an owned property's add carries its pre-allocated id as the subject (ADR-0066; F-39)",
    );
  if (
    (decision === "add" || decision === "update") &&
    m.keyword_id !== undefined &&
    isRecord(block.platform_meta)
  ) {
    const instagram = rec(block.platform_meta.instagram);
    for (const key of Object.keys(instagram)) {
      if (key !== "ig_user_id")
        out.add(
          [decision, "platform_meta", "instagram", key],
          "platform_meta_key",
          "a keyword's Instagram platform_meta names its bound account only (F-13)",
        );
    }
  }
  if (decision === "push_coverage" && m.reason !== null && block.push_covered !== false)
    out.add(
      ["push_coverage", "push_covered"],
      "coverage_reason",
      "a lapsed lease or failed subscription turns coverage off (ADR-0013)",
    );
  if (decision !== "health_change") return;
  const health = block.health;
  if (m.platform === undefined) {
    if (includes(FLAG_REASONS, m.reason) && health !== "blocked")
      out.add(
        ["health_change", "health"],
        "flag_health",
        "flag_off and flag_on take health blocked (ADR-0021 L61; F-11)",
      );
    if (m.reason === "credential_revoked" && health === "degraded")
      out.add(
        ["health_change", "health"],
        "credential_degraded",
        "credential_revoked is never degraded (ADR-0016 L27; F-11)",
      );
    return;
  }
  // Absent and null are alike, as in validate.py (D-4).
  const fallback = block.fallback ?? null;
  if ((health === "fallback") !== (fallback !== null))
    out.add(
      ["health_change", "fallback"],
      "fallback_target",
      "fallback is non-null exactly when health is fallback (R-2)",
    );
  const scope =
    health === "fallback" && m.route === "green" && rec(fallback).route === "amber"
      ? "non_government"
      : null;
  if ((block.scope ?? null) !== scope)
    out.add(
      ["health_change", "scope"],
      "fallback_scope",
      "scope: non_government for a green-to-amber alternate, else null (R-2)",
    );
  if ((m.reason === null) !== (health === "ok"))
    out.add(["reason"], "route_reason", "a route-level state names its reason, and ok none");
  if (m.reason === "flag_off" && health !== "degraded")
    out.add(
      ["health_change", "health"],
      "flag_off_degraded",
      "the canary's flag_off returns a route to degraded (ADR-0021 L61; F-40)",
    );
};

const sourceEvents: Rule = (m, out, ctx) => {
  void ctx;
  checkPlatformMeta(out, ["platform_meta"], m);
  if (m.event === "fallback_on" && m.health !== "fallback")
    out.add(
      ["health"],
      "fallback_on_health",
      "entering fallback gives fallback_on (ADR-0014 L27, ADR-0050 L31)",
    );
  if ((m.event === "health_change" || m.event === "fallback_off") && m.health === "fallback")
    out.add(
      ["health"],
      "fallback_health",
      "entering fallback gives fallback_on, never another event",
    );
};

const itemsAnalysis: Rule = (m, out) => {
  const want = derive(() =>
    analysisKey(str(m.item_id) ?? "", str(m.task) ?? "", str(m.model_version) ?? ""),
  );
  if (want !== m.analysis_key)
    out.add(
      ["analysis_key"],
      "analysis_key_mismatch",
      "analysis_key = item_id:task:model_version (ADR-0023)",
    );
  if (m.status === "ok") {
    if (m.result === null)
      out.add(["result"], "ok_without_result", "an ok analysis carries its result");
    if (m.reason !== null)
      out.add(["reason"], "ok_with_reason", "an ok analysis carries no reason");
  }
  if (m.status === "skipped") {
    if (m.reason === null)
      out.add(["reason"], "skip_without_reason", "a skipped analysis names its reason (Q8)");
    if (m.result !== null)
      out.add(["result"], "skip_with_result", "a skipped analysis carries no result");
  }
  // The person guard: a person mention is linked to a public person or dropped, never kept with
  // offsets and a surface but no entity (analysis-entities §5.3 L69).
  const entities = m.task === "entities" ? rec(m.result).entities : undefined;
  if (Array.isArray(entities))
    entities.forEach((e: unknown, i) => {
      if (isRecord(e) && e.type === "person_public" && e.entity_id === null)
        out.add(
          ["result", "entities", i, "entity_id"],
          "person_unlinked",
          "a person mention is linked or dropped, never kept unlinked (analysis-entities §5.3 L69)",
        );
    });
};

const itemMetrics: Rule = (m, out) => {
  checkSnakeKeys(out, ["metrics", "reactions_by_type"], rec(m.metrics).reactions_by_type);
  const key = str(m.idempotency_key) ?? "";
  if (derive(() => itemId(key)) !== m.item_id)
    out.add(
      ["item_id"],
      "item_id_mismatch",
      "item_id = uuid_v5(ns_items, idempotency_key) (ADR-0006)",
    );
  const k = derive(() => parseKey(key));
  if (k === undefined) return;
  if (k.platform !== m.platform) out.add(["platform"], "key_platform", "the platform is the key's");
  if (k.platform_id !== m.platform_id)
    out.add(["platform_id"], "key_platform_id", "the platform id is the key's");
};

const deletions: Rule = (m, out) => {
  const scope = m.scope;
  const key = scope === "author" ? m.author_ref : scope === "client" ? m.client_id : m.source_id;
  const want = derive(() =>
    deletionId({
      reason: m.reason as never,
      scope: scope as never,
      key: key as string,
      mode: m.mode as never,
      signal_at: m.signal_at as string,
      target: m.target as Record<string, string | string[]>,
    }),
  );
  if (want !== m.deletion_id)
    out.add(["deletion_id"], "deletion_id_mismatch", "deletion_id from the helper (Q2; ADR-0035)");
  if (scope === "item") return;
  const prov = rec(m.provenance);
  const fetch = includes(FETCH_DELETION_REASONS, m.reason);
  if (fetch && prov.route === null)
    out.add(
      ["provenance", "route"],
      "fetch_without_route",
      "a signal that is a platform fetch names its route (F-08)",
    );
  if (!fetch && prov.route !== null)
    out.add(
      ["provenance", "route"],
      "route_without_fetch",
      "a signal that is no fetch has a null route (F-08)",
    );
  if (prov.route === null && prov.vendor !== null)
    out.add(["provenance", "vendor"], "vendor_without_route", "no vendor without a route (F-08)");
};

const articleUrls: Rule = (m, out) => {
  if (derive(() => urlKey(str(m.url) ?? "")) !== m.url_key)
    out.add(
      ["url_key"],
      "url_key_mismatch",
      "url_key = news:url:<url_hash of the normalised URL> (ADR-0036)",
    );
  if (m.canonical_url !== undefined && m.canonical_url !== null) {
    if (derive(() => urlHash(str(m.canonical_url) ?? "")) !== m.canonical_url_hash)
      out.add(
        ["canonical_url_hash"],
        "canonical_hash_mismatch",
        "canonical_url_hash from the one normaliser (Q9)",
      );
  }
};

const searchResults: Rule = (m, out) => {
  if (derive(() => canonicalUrlHash(str(m.canonical_url) ?? "")) !== m.canonical_url_hash)
    out.add(
      ["canonical_url_hash"],
      "canonical_hash_mismatch",
      "canonical_url_hash from the one normaliser (Q9)",
    );
  if (rec(m.provenance).vendor !== m.engine)
    out.add(
      ["provenance", "vendor"],
      "engine_vendor",
      "a result names its engine as provenance.vendor (ADR-0051 (c), (e))",
    );
};

const crawlPolicies: Rule = (m, out) => {
  const allowed = m.status === "allowed";
  if (allowed !== (m.reason === null))
    out.add(["reason"], "status_reason", "reason null exactly when allowed");
  if (allowed !== (m.crawl_allowed === true))
    out.add(["crawl_allowed"], "status_crawl", "crawl_allowed exactly when allowed");
  const asked = m.kind === "recheck" || m.kind === "ops_force";
  if (asked && m.requested_by === null)
    out.add(["requested_by"], "requester_missing", "a recheck or ops_force names who asked (F-43)");
  // A recheck's requester is the service whose host gate asked, never a person (F-43).
  const requester = m.requested_by;
  if (m.kind === "recheck" && typeof requester === "string" && !PATTERNS.service.test(requester))
    out.add(["requested_by"], "requester_not_service", "a recheck names the service that asked");
  if (!asked && m.requested_by !== null)
    out.add(
      ["requested_by"],
      "requester_extra",
      "a refresh or first check has no requester (F-43)",
    );
};

const newsDedup: Rule = (m, out) => {
  if (derive(() => itemId(str(m.idempotency_key) ?? "")) !== m.item_id)
    out.add(
      ["item_id"],
      "item_id_mismatch",
      "item_id = uuid_v5(ns_items, idempotency_key) (ADR-0006)",
    );
  if (m.is_origin === true && m.duplicate_of !== null)
    out.add(["duplicate_of"], "origin_duplicate", "an origin duplicates nothing");
  if (m.is_origin === false && m.duplicate_of === null)
    out.add(["duplicate_of"], "copy_without_origin", "a copy names its origin");
};

const X_SERVICES = PLATFORM_GROUPS.x ?? [];

/** A job's partition key is present: the first of its queue's key fields (ADR-0004). */
function checkJobKey(out: Issues, m: Json, queue: string, kind: string): void {
  const fields = jobKeyFields(queue, kind);
  if (!fields.some((f) => hasValue(m, f))) {
    out.add(
      (fields[0] ?? "source_id").split("."),
      "missing_key",
      `a ${kind} on ${queue} carries ${fields.join(" or ")} (ADR-0004)`,
    );
  }
}

const jobsCompleted: Rule = (m, out, ctx) => {
  const queue = str(m.queue) ?? "";
  const kind = str(m.kind) ?? "";
  for (const [name, kinds] of Object.entries(REPORT_KIND_FIELDS)) {
    if (m[name] !== undefined && !includes(kinds, kind))
      out.add([name], "kind_field", `${name} is a ${kinds.join(" and ")} field (ADR-0017)`);
  }
  const service = derive(() => queueService(queue));
  // The rules that read registry data run as a consumer only for a service this package knows, so a
  // service a newer package adds inside the version is not refused (D-9).
  const readsRegistry =
    ctx.mode === "producer" || (service !== undefined && isKnownService(service));
  for (const name of ["paid_user_reads", "free_rereads"]) {
    if (readsRegistry && m[name] !== undefined && !includes(X_SERVICES, service))
      out.add([name], "x_field", `${name} is an X job's field (ADR-0017)`);
  }
  if (
    m.gap_unfilled !== undefined &&
    !(queue === "jobs.x-recent-search" && kind === "reconciliation")
  )
    out.add(["gap_unfilled"], "gap_field", "gap_unfilled belongs to the X gap job (ADR-0064)");
  if (m.uncovered !== undefined && !(queue === "jobs.x-recent-search" && kind === "rotation"))
    out.add(
      ["uncovered"],
      "uncovered_field",
      "uncovered belongs to the rotation on jobs.x-recent-search (ADR-0064)",
    );
  else if (m.uncovered !== undefined && m.uncovered !== null && m.status !== "partial")
    out.add(
      ["uncovered"],
      "uncovered_status",
      "an uncovered window goes with status partial (ADR-0064)",
    );
  if (readsRegistry) checkJobKey(out, m, queue, kind);
};

const WHOLE_ITEM_KINDS = ["comments", "metrics", "first_sight"];

const job: Rule = (m, out, ctx) => {
  if (m.kind === "push" && m.due_at !== m.received_at)
    out.add(["due_at"], "push_due", "a push job is due when received (ADR-0011)");
  if (
    (m.kind === "resolve" || m.kind === "manual_candidate") &&
    m.platform_id === null &&
    m.handle === null &&
    m.url === null
  )
    out.add(
      ["platform_id"],
      "resolve_identity",
      "a resolve job names the account by id, handle or url (ADR-0032)",
    );
  // Only a replies job names threads, and a refresh, reconciliation or ops_force may; comments,
  // metrics and first_sight jobs read the whole item (plan L415; ADR-0011; review note 16).
  if (includes(WHOLE_ITEM_KINDS, m.kind) && rec(m.post_ref).thread_ids !== undefined)
    out.add(
      ["post_ref", "thread_ids"],
      "field_refused",
      `a ${String(m.kind)} job reads the whole item, never thread_ids (plan L415)`,
    );
  const queue = ctx.options.queue;
  if (queue === undefined) {
    // A producer refuses a job whose row it cannot check (ADR-0012); a consumer checks the shape.
    if (ctx.mode === "producer") out.add([], "no_queue", "a job is validated against its queue");
    return;
  }
  const kind = str(m.kind) ?? "";
  const service = str(rec(m.producer).service) ?? "";
  const allowed = allowedProducers(queue, kind);
  if (allowed.length === 0)
    out.add(["kind"], "kind_not_on_queue", `${queue} takes no ${kind} job (ADR-0012)`);
  else if (!allowed.includes(service))
    out.add(
      ["producer", "service"],
      "producer_not_allowed",
      `the producer table lets ${allowed.join(", ")} send ${kind} on ${queue} (ADR-0012)`,
    );
  for (const field of requiredJobFields(queue, kind, service)) {
    if (!hasValue(m, field))
      out.add(field.split("."), "missing_field", `a ${kind} on ${queue} carries ${field}`);
  }
  for (const field of refusedJobFields(queue, kind, service)) {
    if (hasValue(m, field))
      out.add(field.split("."), "field_refused", `a ${kind} on ${queue} carries no ${field}`);
  }
  // A reconciliation's reason is yt-uploads-reconciler's alone (plan L421; ADR-0064 L25): a rule in
  // code, since a registry row would list the other queues.
  if (
    kind === "reconciliation" &&
    m.reason !== undefined &&
    derive(() => queueService(queue)) !== "yt-uploads-reconciler"
  )
    out.add(["reason"], "field_refused", `a reconciliation on ${queue} carries no reason`);
  checkJobKey(out, m, queue, kind);
};

/** The provenance and class of an original message, where a data message keeps them. */
function originalData(message: unknown): { provenance?: unknown; retention_class?: unknown } {
  const msg = rec(message);
  if (isRecord(msg.provenance))
    return { provenance: msg.provenance, retention_class: msg.retention_class };
  const env = rec(msg.envelope);
  if (isRecord(env.provenance))
    return { provenance: env.provenance, retention_class: env.retention_class };
  return {};
}

const SIGNAL_SCOPES: readonly string[] = ["author", "source", "client"];
const provenanceTypes = new Map<Mode, { data: z.ZodType; signal: z.ZodType }>();

/**
 * Whether an original's provenance passes the original's own type in `mode`: the signal provenance,
 * whose route may be null, for an author-, source- or client-scope deletion, else the data one (D-1).
 */
function ownProvenance(message: Json, value: unknown, mode: Mode): boolean {
  let types = provenanceTypes.get(mode);
  if (!types) {
    const b = createBuilder(mode);
    types = { data: provenance(b), signal: signalProvenance(b) };
    provenanceTypes.set(mode, types);
  }
  const signal = message.schema === "deletions/v1" && includes(SIGNAL_SCOPES, message.scope);
  return value !== undefined && (signal ? types.signal : types.data).safeParse(value).success;
}

// A dead letter copies its original's provenance when the original's own type takes it, and its
// retention_class only when that is a valid class too; otherwise neither (F-42, D-1, D-12). Null,
// absent and unknown classes count alike. The producer's strict type decides whether a copy is due;
// the mode's type judges a copy made, so a consumer tolerates a field a newer package added.
const dlq: Rule = (m, out, ctx) => {
  const id = ctx.schemaId;
  if (id !== "dlq.<service>/v1" && m.schema !== id)
    out.add(["schema"], "schema_mismatch", `the record's schema is ${id}`);
  const hasMessage = m.message !== undefined;
  const hasRaw = m.raw !== undefined;
  if (hasMessage && hasRaw) out.add(["raw"], "message_and_raw", "message or raw, exactly one (Q5)");
  if (!hasMessage && !hasRaw)
    out.add(["message"], "neither_message_nor_raw", "message or raw, exactly one (Q5)");
  const message = rec(m.message);
  const original = originalData(m.message);
  const validClass = includes(RETENTION_CLASSES, original.retention_class);
  const copyable = ownProvenance(message, original.provenance, "producer");
  const takes = ownProvenance(message, original.provenance, ctx.mode);
  if (m.provenance !== undefined && !hasMessage) {
    out.add(
      ["provenance"],
      "provenance_without_message",
      "provenance is copied only from a parsed data message (F-42)",
    );
    return;
  }
  if (m.provenance !== undefined && !(takes && jsonEqual(m.provenance, original.provenance)))
    out.add(
      ["provenance"],
      "provenance_not_copied",
      "the copied provenance equals the message's, which its own type takes (F-42, D-1)",
    );
  if (m.provenance === undefined && copyable)
    out.add(
      ["provenance"],
      "provenance_not_copied",
      "a data message's provenance is copied to the top (F-42)",
    );
  if (m.retention_class !== undefined && m.provenance === undefined)
    out.add(["provenance"], "provenance_without_class", "retention_class travels with provenance");
  else if (
    m.retention_class !== undefined &&
    !(takes && validClass && m.retention_class === original.retention_class)
  )
    out.add(
      ["retention_class"],
      "class_not_copied",
      "the copied retention_class is the message's valid class (F-42, D-1)",
    );
  else if (m.retention_class === undefined && m.provenance !== undefined && takes && validClass)
    out.add(
      ["retention_class"],
      "class_not_copied",
      "a message's valid retention_class is copied with its provenance (F-42, D-1)",
    );
};

/** A client or account-manager notice names its client; an ops notice none (F-46). */
function checkAudience(out: Issues, m: Json): void {
  const forClient = m.audience === "client" || m.audience === "account_manager";
  if (forClient && m.client_id === null)
    out.add(
      ["client_id"],
      "client_missing",
      "a client or account-manager notice names its client (F-46)",
    );
  if (!forClient && m.client_id !== null)
    out.add(["client_id"], "client_extra", "an ops notice names no client (F-46)");
}

const n8nAlert: Rule = (m, out, ctx) => {
  if (m.idempotency_key !== `${str(m.alert_id) ?? ""}:${str(m.channel) ?? ""}`)
    out.add(
      ["idempotency_key"],
      "idempotency_key_mismatch",
      "idempotency_key = <alert_id>:<channel> (alert-evaluator §5.3 L69)",
    );
  checkAudience(out, m);
  const details = rec(m.details);
  if (details.subject_kind === "source" && details.source_id === undefined)
    out.add(
      ["details", "source_id"],
      "fallback_subject",
      "a source's fallback notice names the source (ADR-0021)",
    );
  if (details.subject_kind === "route") {
    for (const name of ["platform", "route"]) {
      if (details[name] === undefined)
        out.add(
          ["details", name],
          "fallback_subject",
          "a route's fallback notice names the platform and route (ADR-0021)",
        );
    }
  }
  if (details.subject_kind !== undefined && m.audience !== "ops")
    out.add(
      ["audience"],
      "fallback_audience",
      "an automatic-fallback notice goes to ops (ADR-0021 L58)",
    );
  if (m.audience !== "client" && m.audience !== "account_manager") return;
  // The government rule (alert-evaluator §6.2 L102; F-50) needs the client's type, which the
  // producer passes; a producer that does not fails closed (CONVENTIONS v1.1 L84).
  // A value other than the two types, null included, counts as absent, so the rule fails closed.
  const given: unknown = ctx.options.clientType;
  const clientType = includes(CLIENT_TYPES, given) ? given : undefined;
  if (clientType === undefined) {
    if (ctx.mode === "producer")
      out.add([], "no_client_type", "a client's alert is validated with the client's type");
    return;
  }
  if (clientType !== "government") return;
  // A government client's alert names its keyword or request only, so a subject field added inside
  // the version is refused too (F-50; note 12).
  for (const name of Object.keys(rec(m.subject))) {
    if (name !== "keyword_id" && name !== "request_id")
      out.add(
        ["subject", name],
        "government_subject",
        `a government client's alert names no ${name} (F-50)`,
      );
  }
  const scope = rec(details.scope);
  if (scope.level !== undefined && scope.level !== "keyword")
    out.add(
      ["details", "scope", "level"],
      "government_scope",
      "a government client's alert is at the keyword level (alert-evaluator §6.2 L102)",
    );
  for (const name of ["source", "platform"]) {
    if (scope[name] !== undefined)
      out.add(
        ["details", "scope", name],
        "government_scope",
        `a government client's alert names no ${name} (alert-evaluator §6.2 L102)`,
      );
  }
  if (details.rule_type !== undefined && !includes(GOVERNMENT_ALERT_RULE_TYPES, details.rule_type))
    out.add(
      ["details", "rule_type"],
      "government_rule_type",
      "a government client receives the keyword-level rule types only (alert-evaluator §5.3 C L65)",
    );
};

const n8nCard: Rule = (m, out) => {
  if (m.idempotency_key !== `${str(m.card_id) ?? ""}:${str(m.channel) ?? ""}`)
    out.add(
      ["idempotency_key"],
      "idempotency_key_mismatch",
      "idempotency_key = <card_id>:<channel> (F-23)",
    );
  checkAudience(out, m);
  // The subject key is the candidate's or the source's; the reference is the decision's or the request's.
  const subject = rec(m.subject);
  const key = str(subject.candidate_key) ?? str(subject.source_id);
  const ref = str(subject.decision_id) ?? str(subject.request_id);
  if (key === undefined || ref === undefined) {
    out.add(
      ["subject"],
      "card_subject",
      "a card's subject names a candidate or source, and a decision or request (F-47)",
    );
    return;
  }
  if (derive(() => cardId(str(m.card_type) ?? "", key, ref)) !== m.card_id)
    out.add(
      ["card_id"],
      "card_id_mismatch",
      "card_id = uuid_v5(ns_cards, <card_type>:<subject key>:<ref>) (F-47)",
    );
};

const RULES: Record<string, Rule> = {
  "raw.items/v1": rawItems,
  "items.normalized/v1": itemsNormalized,
  "item.hits/v1": itemHits,
  "discovery.hits/v1": discoveryHits,
  "poster.profiles/v1": posterProfiles,
  "registry.decisions/v1": registryDecisions,
  "source.events/v1": sourceEvents,
  "items.analysis/v1": itemsAnalysis,
  "item.metrics/v1": itemMetrics,
  "deletions/v1": deletions,
  "article.urls/v1": articleUrls,
  "search.results/v1": searchResults,
  "crawl.policies/v1": crawlPolicies,
  "news.dedup/v1": newsDedup,
  "jobs.completed/v1": jobsCompleted,
  "job/v1": job,
  "dlq.<service>/v1": dlq,
  "n8n.alert/v1": n8nAlert,
  "n8n.card/v1": n8nCard,
};

const CONTROL = new Set([
  "source.events/v1",
  "jobs.completed/v1",
  "job/v1",
  "n8n.alert/v1",
  "n8n.card/v1",
]);

// --- registry checks (producer mode) ---------------------------------------------------------------

function checkVendor(out: Issues, path: IssuePath, route: unknown, vendor: unknown): void {
  if (typeof route !== "string") return;
  if (!isKnownVendor(route, (vendor ?? null) as string | null))
    out.add(
      path,
      "unknown_vendor",
      `${String(vendor)} is no ${route} vendor of the registry (ADR-0051)`,
    );
}

// A (route, vendor) pair a part of the message names: with its route, the vendor is the registry's
// for that route; without it, a vendor it names is on one of the registry's lists (note 11).
function checkPair(out: Issues, path: IssuePath, holder: Json): void {
  if (holder.vendor === undefined) return;
  if (holder.route !== undefined) return checkVendor(out, path, holder.route, holder.vendor);
  const vendor = str(holder.vendor);
  if (vendor !== undefined && !isListedVendor(vendor))
    out.add(path, "unknown_vendor", `${vendor} is no vendor of the registry`);
}

function checkProvenance(out: Issues, prov: unknown, prefix: IssuePath): void {
  if (!isRecord(prov)) return;
  const service = str(prov.service);
  if (service !== undefined && !isKnownService(service))
    out.add(
      [...prefix, "service"],
      "unknown_service",
      `${service} is no service of the index (Q1)`,
    );
  if (prov.route !== null) checkVendor(out, [...prefix, "vendor"], prov.route, prov.vendor);
}

function checkDecisionRow(out: Issues, m: Json, service: string): void {
  const subject = SUBJECTS.find((s) => m[s] !== undefined);
  if (subject === undefined) return;
  const decision = str(m.decision) ?? "";
  const { health, rule_hit: ruleHit } = rec(m[decision]);
  const row = decisionRow(
    {
      decision,
      subject,
      reason: (m.reason ?? null) as string | null,
      health: str(health),
      rule_hit: typeof ruleHit === "number" ? ruleHit : null,
    },
    service,
  );
  if (row === null) {
    out.add(
      ["producer", "service"],
      "decision_not_allowed",
      `no decision row lets ${service} send this ${decision} (ADR-0012, ADR-0013)`,
    );
    return;
  }
  if (row.provenance === "required" && m.provenance === undefined)
    out.add(
      ["provenance"],
      "provenance_required",
      `this ${decision} reports a fetch and carries provenance (F-14)`,
    );
  if (row.provenance === "refused" && m.provenance !== undefined)
    out.add(
      ["provenance"],
      "provenance_refused",
      `this ${decision} carries requested_by and no provenance (F-14)`,
    );
}

// The topics whose requester may name a service or a person (Q18), on source events the actor.
const REQUESTER_TOPICS = new Set([
  "registry.decisions/v1",
  "source.events/v1",
  "deletions/v1",
  "job/v1",
  "crawl.policies/v1",
]);

function registryChecks(out: Issues, id: string, m: Json): void {
  const head = id === "raw.items/v1" ? rec(m.envelope) : m;
  const prefix: IssuePath = id === "raw.items/v1" ? ["envelope"] : [];
  const service = str(rec(head.producer).service) ?? "";
  if (!isKnownService(service)) {
    out.add(
      [...prefix, "producer", "service"],
      "unknown_service",
      `${service} is no service of the index (Q1)`,
    );
  } else if (id === "registry.decisions/v1") {
    checkDecisionRow(out, m, service);
  } else if (id !== "job/v1" && !id.startsWith("n8n.")) {
    // A job's producers are its queue's row; any service sends n8n notices (ADR-0067).
    const detail =
      id === "raw.items/v1"
        ? { kind: str(head.kind) ?? "" }
        : id === "jobs.completed/v1"
          ? { queue: str(m.queue) ?? "" }
          : {};
    const target = id === "dlq.<service>/v1" ? (str(m.schema) ?? id) : id;
    if (!isAllowedTopicWriter(target, service, detail))
      out.add(
        [...prefix, "producer", "service"],
        "writer_not_allowed",
        `${service} does not write ${target}`,
      );
  }
  for (const c of writerConditions(id, service)) {
    if (getPath(m, c.field) !== c.equals)
      out.add(
        [...prefix, ...c.field.split(".")],
        "writer_condition",
        `${service} writes ${id} only with ${c.field} = ${String(c.equals)}`,
      );
  }
  checkProvenance(out, head.provenance, [...prefix, "provenance"]);
  // A requester, checked as producer.service is (F-09). A recheck's is a service by definition,
  // the service whose host gate asked (ADR-0040; F-43). Any other names a service when it matches
  // the service pattern, which D3's person reference never does; a person stays unchecked (Q18).
  const where = id === "source.events/v1" ? "actor" : "requested_by";
  if (REQUESTER_TOPICS.has(id)) {
    const isRecheck = (id === "job/v1" || id === "crawl.policies/v1") && m.kind === "recheck";
    const requester = str(m[where]);
    const named = isRecheck || (requester !== undefined && PATTERNS.service.test(requester));
    if (named && !isKnownService(requester ?? ""))
      out.add([where], "unknown_service", `${requester ?? ""} is no service of the index (Q1)`);
  }
  // Every other (route, vendor) pair a message names.
  if (id === "poster.profiles/v1" && m.route !== undefined && m.route !== null)
    checkVendor(out, ["vendor"], m.route, m.vendor);
  if (id === "registry.decisions/v1") {
    const block = rec(m[str(m.decision) ?? ""]);
    if (m.platform !== undefined) {
      checkVendor(out, ["vendor"], m.route, m.vendor);
      const fb = block.fallback;
      if (isRecord(fb))
        checkVendor(out, ["health_change", "fallback", "vendor"], fb.route, fb.vendor);
    }
    checkPair(out, [str(m.decision) ?? "", "source", "vendor"], rec(block.source));
  }
  if (id === "source.events/v1") {
    checkVendor(out, ["vendor"], m.route, m.vendor);
    checkPair(out, ["previous", "vendor"], rec(m.previous));
  }
  if (id === "n8n.alert/v1") {
    checkPair(out, ["subject", "vendor"], rec(m.subject));
    checkPair(out, ["details", "vendor"], rec(m.details));
  }
  // A dead letter sits in its consumer's own dlq.<service> topic (CONVENTIONS L41).
  if (id === "dlq.<service>/v1") {
    const consumer = str(rec(m.consumer).service);
    if (consumer !== undefined && !isKnownService(consumer))
      out.add(
        ["consumer", "service"],
        "unknown_service",
        `${consumer} is no service of the index (Q1)`,
      );
    else if (consumer !== undefined && consumer !== dlqService(str(m.schema) ?? ""))
      out.add(
        ["consumer", "service"],
        "consumer_mismatch",
        `a dead letter of ${consumer} is in dlq.${consumer}/v1 (CONVENTIONS L41)`,
      );
  }
  if (id === "raw.items/v1") {
    const declared = declaredContextKeys(service, str(head.kind) ?? "");
    const context = rec(head.context);
    for (const key of Object.keys(context)) {
      if (!declared.keys.includes(key))
        out.add(
          ["envelope", "context", key],
          "undeclared_context_key",
          `${service} declares no context key ${key} (ADR-0005)`,
        );
    }
    for (const key of declared.required) {
      if (context[key] === undefined)
        out.add(
          ["envelope", "context", key],
          "missing_context_key",
          `a ${String(head.kind)} record from ${service} carries context.${key}`,
        );
    }
  }
  if (id === "poster.profiles/v1" && isRecord(m.extras)) {
    const resolver = str(rec(m.provenance).service) ?? "";
    const declared = declaredExtrasKeys(resolver) ?? [];
    for (const key of Object.keys(m.extras)) {
      if (!declared.includes(key))
        out.add(
          ["extras", key],
          "undeclared_extras_key",
          `${resolver} declares no extras key ${key} (ADR-0033)`,
        );
    }
  }
}

// --- the entry point -------------------------------------------------------------------------------

/**
 * Validates a message of `schemaId` (a catalogue id, or a concrete `dlq.<service>/v1`) as a producer
 * (strict, with the registry checks) or a consumer (tolerant of unknown fields). On success `value` is
 * the parsed message: in consumer mode without the fields the schema does not know.
 */
export function validate(
  schemaId: string,
  value: unknown,
  mode: Mode = "producer",
  options: ValidateOptions = {},
): ValidationResult {
  const schema = schemaFor(schemaId, mode);
  if (!schema) {
    return {
      ok: false,
      issues: [{ path: ["schema"], code: "unknown_schema", message: `no schema ${schemaId}` }],
    };
  }
  const json = jsonIssues(value);
  if (json.length > 0) return { ok: false, issues: json };
  const parsed = schema.safeParse(value);
  if (!parsed.success) return { ok: false, issues: zodIssues(parsed.error.issues) };
  const id = catalogueId(schemaId);
  // The rules read the message as sent: in consumer mode it may hold fields the schema drops.
  const raw = rec(value);
  const out = new Issues();
  if (CONTROL.has(id)) refuseProvenance(out, raw);
  RULES[id]?.(raw, out, { schemaId, mode, options });
  if (out.list.length === 0 && mode === "producer") registryChecks(out, id, raw);
  if (out.list.length > 0) return { ok: false, issues: out.list };
  return { ok: true, value: parsed.data };
}
