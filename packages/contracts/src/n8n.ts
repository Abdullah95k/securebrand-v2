// n8n.alert/v1 and n8n.card/v1 (ADR-0067, ADR-0048; Q11), and the n8n signing helper. Both are
// producer-only notices: `producer`, no `provenance` (F-51, VERSIONING.md); an alert carries
// aggregates only, never item text, an author_ref or a handle (alert-evaluator.md L65, L128).
import { createHmac, timingSafeEqual } from "node:crypto";
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { ContractError } from "./errors.ts";
import { metadataShape } from "./metadata.ts";
import {
  PATTERNS,
  candidateKey,
  count,
  httpUrl,
  nonEmpty,
  share,
  snakeName,
  timestamp,
  token,
  ulid,
  uuid,
  vendorName,
} from "./primitives.ts";
import {
  ALERT_CHANNELS,
  ALERT_RULE_TYPES,
  ALERT_SEVERITIES,
  CARD_INPUT_KINDS,
  FALLBACK_SUBJECT_KINDS,
  N8N_AUDIENCES,
  N8N_CHANNELS,
  PLATFORMS,
  REGISTRY_REASONS,
  REVIEW_CARD_ACTIONS,
  ROUTES,
} from "./vocabulary.ts";

export const N8N_ALERT = "n8n.alert/v1";
export const N8N_CARD = "n8n.card/v1";

const fact = (b: SchemaBuilder) =>
  b.def("Fact", () => b.obj({ label: nonEmpty(), value: z.string() }));

const pascal = (s: string): string =>
  s
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join("");

export function buildN8nAlert(b: SchemaBuilder) {
  const scope = b.def("AlertScope", () =>
    b.obj({
      level: snakeName().optional(),
      platform: z.enum(PLATFORMS).optional(),
      source: b
        .def("AlertSource", () => b.obj({ source_id: uuid(), display_name: z.string() }))
        .optional(),
      item_id: uuid().optional(),
      topic_id: z.string().regex(PATTERNS.topicId).optional(),
      entity_id: token().optional(),
      brand_id: token().optional(),
      story_id: ulid().optional(),
    }),
  );
  // A client alert's common fields (alert-evaluator §6.2 L86-L99, §5.3 L63).
  const common = () => ({
    rule_id: uuid(),
    renotify: z.boolean(),
    keyword: b
      .def("AlertKeyword", () =>
        b.obj({ keyword_id: uuid(), label: nonEmpty(), purpose: snakeName().nullable() }),
      )
      .optional(),
    scope: scope.optional(),
    window: b.def("AlertWindow", () =>
      b.obj({ hour: timestamp(), elapsed_fraction: share(), evaluated_at: timestamp() }),
    ),
    fingerprint: nonEmpty(),
    cooldown_until: timestamp(),
  });
  const volume = b.def("VolumeSpikeMetrics", () =>
    b.obj({
      mentions_so_far: count(),
      baseline_median_same_hour: z.number().min(0),
      expected_so_far: z.number().min(0),
      ratio: z.number().min(0),
      baseline_days: count(),
    }),
  );
  // The other eight types: a map of numbers in v1; named metrics later are a new version (Q11).
  const branch = (type: (typeof ALERT_RULE_TYPES)[number]) =>
    b.titled(
      `${pascal(type)}Alert`,
      b.obj({
        ...common(),
        rule_type: z.literal(type),
        metrics: type === "volume_spike" ? volume : z.record(z.string(), z.number()),
      }),
    );
  const [first, ...rest] = ALERT_RULE_TYPES.map(branch);
  if (!first) throw new ContractError("no_rule_types", "ALERT_RULE_TYPES is empty");
  const clientAlert = z.discriminatedUnion("rule_type", [first, ...rest]);
  // The automatic-fallback notice (ADR-0021 L58-L61): a source, or a platform's route.
  const fallback = b.titled(
    "FallbackNotice",
    b.obj({
      subject_kind: z.enum(FALLBACK_SUBJECT_KINDS),
      source_id: uuid().optional(),
      platform: z.enum(PLATFORMS).optional(),
      route: z.enum(ROUTES).optional(),
      reason: z.enum(REGISTRY_REASONS),
      vendor: vendorName().nullable(),
    }),
  );
  const facts = b.titled("FactsNotice", b.obj({ facts: z.array(fact(b)) }));
  return b.titled(
    "N8nAlertV1",
    b.obj({
      ...metadataShape(b, N8N_ALERT),
      alert_id: ulid(), // deterministic for its input, so a resend repeats it
      idempotency_key: nonEmpty(), // <alert_id>:<channel>, checked by validate()
      channel: z.enum(ALERT_CHANNELS),
      fallthrough_channel: z.enum(N8N_CHANNELS).nullable(),
      audience: z.enum(N8N_AUDIENCES),
      client_id: uuid().nullable(), // the client of a client or account-manager notice
      alert: snakeName(), // an open name; KNOWN_ALERT_NAMES lists those the ADRs fix
      severity: z.enum(ALERT_SEVERITIES),
      subject: b.def("AlertSubject", () =>
        b.obj({
          source_id: uuid().optional(),
          platform: z.enum(PLATFORMS).optional(),
          route: z.enum(ROUTES).optional(),
          vendor: vendorName().nullable().optional(),
          keyword_id: uuid().optional(),
          candidate_key: candidateKey().optional(),
          request_id: ulid().optional(),
        }),
      ),
      summary: nonEmpty(),
      details: z.union([clientAlert, fallback, facts]),
    }),
  );
}

export function buildN8nCard(b: SchemaBuilder) {
  const common = () => ({
    ...metadataShape(b, N8N_CARD),
    card_id: uuid(), // uuid v5 of <card_type>:<subject key>:<ref>, checked by validate() (F-47)
    idempotency_key: nonEmpty(), // <card_id>:<channel>
    channel: z.enum(N8N_CHANNELS),
    audience: z.enum(N8N_AUDIENCES),
    client_id: uuid().nullable(),
    subject: b.def("CardSubject", () =>
      b.obj({
        candidate_key: candidateKey().optional(),
        source_id: uuid().optional(),
        decision_id: ulid().optional(),
        request_id: ulid().optional(),
      }),
    ),
    title: nonEmpty(),
    summary: nonEmpty(),
    facts: z.array(fact(b)),
    opened_at: timestamp(),
  });
  return b.titled(
    "N8nCardV1",
    z.discriminatedUnion("card_type", [
      b.titled(
        "QualifierReviewCard",
        b.obj({
          ...common(),
          card_type: z.literal("qualifier_review"),
          buttons: z
            .array(
              b.def("CardButton", () =>
                b.obj({ action: z.enum(REVIEW_CARD_ACTIONS), label: nonEmpty() }),
              ),
            )
            .min(1),
          default_action: z.literal("reject"), // qualifier §5.2 L61
          timeout_at: timestamp(), // 24 hours (qualifier §5.2 L61)
        }),
      ),
      b.titled(
        "ManualUrlCard",
        b.obj({
          ...common(),
          card_type: z.literal("manual_url"),
          inputs: z
            .array(
              b.def("CardInput", () =>
                b.obj({ name: snakeName(), label: nonEmpty(), kind: z.enum(CARD_INPUT_KINDS) }),
              ),
            )
            .min(1),
          timeout_at: timestamp().optional(),
        }),
      ),
      b.titled(
        "GrantMissingCard",
        b.obj({ ...common(), card_type: z.literal("grant_missing"), regrant_url: httpUrl() }),
      ),
    ]),
  );
}

export type N8nAlert = z.infer<ReturnType<typeof buildN8nAlert>>;
export type N8nCard = z.infer<ReturnType<typeof buildN8nCard>>;

// --- signing (ADR-0067: one HMAC scheme over the body with a timestamp and an idempotency key) ---

/** The headers a signed notice carries; the names, the signed string and the tolerance are F2's (F-49). */
export type N8nHeaders = Record<"X-SB-Timestamp" | "Idempotency-Key" | "X-SB-Signature", string>;
export type Verification =
  | { readonly ok: true }
  | {
      readonly ok: false;
      readonly reason:
        | "missing_header"
        | "bad_idempotency_key"
        | "bad_timestamp"
        | "stale_timestamp"
        | "bad_signature";
    };

const bytes = (v: Uint8Array | string): Uint8Array =>
  typeof v === "string" ? new TextEncoder().encode(v) : v;

/** Hex HMAC-SHA256 under `secret` of the UTF-8 of "<timestamp>.<idempotency key>." and the body bytes. */
function mac(body: Uint8Array, secret: Uint8Array, timestamp: string, key: string): string {
  return createHmac("sha256", secret)
    .update(`${timestamp}.${key}.`, "utf8")
    .update(body)
    .digest("hex");
}

// An idempotency key is a header value, so it holds no control character or space, and it holds no
// dot, which separates the fields of the signed string: "a.b" over "c" and "a" over "b.c" would
// otherwise sign alike.
// eslint-disable-next-line no-control-regex -- the control characters are what the class refuses
const IDEMPOTENCY_KEY = /^[^\x00-\x20\x7f.]+$/;

/**
 * Signs a notice's body for n8n or a client's alert webhook (ADR-0067, Q15): `timestamp` in Unix
 * seconds, given by the caller, and the notice's idempotency key. The SDK signs again at each send.
 */
export function signN8n(
  body: Uint8Array | string,
  secret: Uint8Array | string,
  timestamp: number,
  idempotencyKey: string,
): N8nHeaders {
  if (!Number.isSafeInteger(timestamp) || timestamp < 0)
    throw new ContractError("bad_timestamp", "Unix seconds, a whole non-negative number");
  if (typeof idempotencyKey !== "string" || !IDEMPOTENCY_KEY.test(idempotencyKey))
    throw new ContractError("bad_idempotency_key", "a non-empty header value without a dot");
  const key = bytes(secret);
  if (key.length === 0) throw new ContractError("empty_secret", "the signing secret is empty");
  const ts = String(timestamp);
  return {
    "X-SB-Timestamp": ts,
    "Idempotency-Key": idempotencyKey,
    "X-SB-Signature": `v1=${mac(bytes(body), key, ts, idempotencyKey)}`,
  };
}

/**
 * Verifies a signed notice: the headers by name in any case, the timestamp no further than
 * `toleranceSeconds` from `now` (Unix seconds, given by the caller: no helper reads a clock). A clock
 * or a tolerance that is not a finite non-negative number is the caller's error and throws, so a
 * NaN can never switch the staleness check off.
 */
export function verifyN8n(
  body: Uint8Array | string,
  headers: Readonly<Record<string, string>>,
  secret: Uint8Array | string,
  now: number,
  toleranceSeconds = 300,
): Verification {
  if (!Number.isFinite(now) || now < 0)
    throw new ContractError("bad_now", "now is Unix seconds, a finite non-negative number");
  if (!Number.isFinite(toleranceSeconds) || toleranceSeconds < 0)
    throw new ContractError("bad_tolerance", "a finite non-negative number of seconds");
  const byName = new Map(Object.entries(headers).map(([k, v]) => [k.toLowerCase(), v]));
  const ts = byName.get("x-sb-timestamp");
  const key = byName.get("idempotency-key");
  const signature = byName.get("x-sb-signature");
  if (ts === undefined || key === undefined || signature === undefined)
    return { ok: false, reason: "missing_header" };
  if (!IDEMPOTENCY_KEY.test(key)) return { ok: false, reason: "bad_idempotency_key" };
  if (!/^[0-9]{1,15}$/.test(ts)) return { ok: false, reason: "bad_timestamp" };
  if (Math.abs(now - Number(ts)) > toleranceSeconds)
    return { ok: false, reason: "stale_timestamp" };
  const secretBytes = bytes(secret);
  if (secretBytes.length === 0 || !signature.startsWith("v1="))
    return { ok: false, reason: "bad_signature" };
  const want = Buffer.from(mac(bytes(body), secretBytes, ts, key), "utf8");
  const got = Buffer.from(signature.slice(3), "utf8");
  if (got.length !== want.length || !timingSafeEqual(got, want))
    return { ok: false, reason: "bad_signature" };
  return { ok: true };
}
