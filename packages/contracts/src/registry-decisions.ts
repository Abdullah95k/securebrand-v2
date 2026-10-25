// registry.decisions/v1: one schema for every registry change request (ADR-0013), with ADR-0002's
// metadata, `decision_id`, the type in `decision`, `requested_by`, `reason`, exactly one subject (its
// partition key, ADR-0004) and one block named after the type. The allowed producers per type, and
// whether each row requires, accepts or refuses provenance, are registry data
// (registries/decision-producers.json, F-14), checked by validate() in producer mode.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { metadataShape, platformMeta, provenance, retentionClass } from "./metadata.ts";
import { optionalShape, sourceColumnShape, tier } from "./source-columns.ts";
import {
  actor,
  authorRef,
  candidateKey,
  count,
  share,
  timestamp,
  ulid,
  uuid,
  vendorName,
} from "./primitives.ts";
import {
  FLAG_REASONS,
  HEALTHS,
  PLATFORMS,
  PUSH_COVERAGE_REASONS,
  RESOLVE_ORIGINS,
  REVIEW_REASONS,
  ROUTE_HEALTH_REASONS,
  ROUTES,
  SOURCE_HEALTH_REASONS,
} from "./vocabulary.ts";

export const REGISTRY_DECISIONS = "registry.decisions/v1";

/** The qualifier's rule behind a decision (CONVENTIONS v1.1, qualifier rules 1 to 10). */
const ruleHit = () => z.number().int().min(1).max(10);

const common = (b: SchemaBuilder) => ({
  ...metadataShape(b, REGISTRY_DECISIONS),
  decision_id: ulid(),
  // Stored as registry_audit.actor: the producing service, or the person whose answer or request
  // the producer applies (ADR-0013).
  requested_by: actor(),
  // Present or absent together, as the producer's row says (ADR-0003 L26; F-14).
  provenance: provenance(b).optional(),
  retention_class: retentionClass().optional(),
});

const clientPriority = (b: SchemaBuilder) =>
  z
    .array(b.def("ClientPriority", () => b.obj({ client_id: uuid(), priority: z.boolean() })))
    .optional();

/** An `add` about a source: its columns and, for a news site or an owned property, its id. */
const addSourceBlock = (b: SchemaBuilder) =>
  b.def("AddSourceBlock", () =>
    b.obj({
      source: b.def("SourceColumns", () => b.obj(sourceColumnShape(b))),
      // A news site's (ADR-0040) or an owned property's (ADR-0066) pre-allocated id.
      proposed_source_id: uuid().nullable(),
      origin: z.enum(RESOLVE_ORIGINS).nullable(),
      rule_hit: ruleHit().nullable(),
      client_priority: clientPriority(b),
    }),
  );

/** A keyword save: the hashtag's bound account per platform, which registry-writer copies (F-13). */
const keywordBlock = (b: SchemaBuilder) =>
  b.def("KeywordBlock", () =>
    b.obj({
      platform_meta: b
        .def("KeywordPlatformMeta", () => b.obj({ instagram: platformMeta(b).optional() }))
        .optional(),
    }),
  );

const qualifierBlock = (b: SchemaBuilder) =>
  b.def("QualifierBlock", () => b.obj({ rule_hit: ruleHit(), client_ids: z.array(uuid()) }));

export function buildRegistryDecisions(b: SchemaBuilder) {
  const sourceSubject = { source_id: uuid() };
  const candidateSubject = { candidate_key: candidateKey() };
  const keywordSubject = { keyword_id: uuid() };
  const branch = (title: string, shape: z.ZodRawShape) =>
    b.titled(title, b.obj({ ...common(b), ...shape }));
  return b.titled(
    "RegistryDecisionsV1",
    z.union([
      branch("AddCandidate", {
        decision: z.literal("add"),
        reason: z.null(),
        ...candidateSubject,
        add: addSourceBlock(b),
      }),
      branch("AddSource", {
        decision: z.literal("add"),
        reason: z.null(),
        ...sourceSubject,
        add: addSourceBlock(b),
      }),
      branch("AddKeyword", {
        decision: z.literal("add"),
        reason: z.null(),
        ...keywordSubject,
        add: keywordBlock(b),
      }),
      branch("UpdateSource", {
        decision: z.literal("update"),
        reason: z.literal("budget_wait").nullable(),
        ...sourceSubject,
        update: b.def("UpdateSourceBlock", () =>
          b.obj({
            // The changed columns only (ADR-0013 L28 (d); F-16, F-41).
            source: b.def("SourceColumnChanges", () =>
              b.obj({
                ...optionalShape(sourceColumnShape(b)),
                notes: z.string().nullable().optional(),
              }),
            ),
            client_priority: clientPriority(b),
          }),
        ),
      }),
      branch("UpdateKeyword", {
        decision: z.literal("update"),
        reason: z.null(),
        ...keywordSubject,
        update: keywordBlock(b),
      }),
      branch("RemoveClient", {
        decision: z.literal("remove_client"),
        reason: z.literal("client_removed"),
        ...sourceSubject,
        remove_client: b.def("RemoveClientBlock", () => b.obj({ client_id: uuid() })),
      }),
      branch("TierChange", {
        decision: z.literal("tier_change"),
        reason: z.null(),
        ...sourceSubject,
        tier_change: b.def("TierChangeBlock", () => b.obj({ tier: tier(), rule_hit: ruleHit() })),
      }),
      branch("Dormant", {
        decision: z.literal("dormant"),
        reason: z.null(),
        ...sourceSubject,
        dormant: b.def("DormantBlock", () => b.obj({ rule_hit: ruleHit() })),
      }),
      branch("Promote", { decision: z.literal("promote"), reason: z.null(), ...sourceSubject }),
      branch("Retire", {
        decision: z.literal("retire"),
        reason: z.enum(["owner_request", "authorization_revoked", "not_found"]).nullable(),
        ...sourceSubject,
        // The qualifier's rule 9 only; null for the other producers.
        retire: b.def("RetireBlock", () => b.obj({ rule_hit: ruleHit().nullable() })),
      }),
      branch("PushCoverage", {
        decision: z.literal("push_coverage"),
        reason: z.enum(PUSH_COVERAGE_REASONS).nullable(),
        ...sourceSubject,
        push_coverage: b.def("PushCoverageBlock", () => b.obj({ push_covered: z.boolean() })),
      }),
      branch("SourceHealthChange", {
        decision: z.literal("health_change"),
        // Set by the service that met it, cleared with health ok (ADR-0016; Q12).
        reason: z.enum([...SOURCE_HEALTH_REASONS, ...FLAG_REASONS]),
        ...sourceSubject,
        health_change: b.def("SourceHealthBlock", () =>
          b.obj({ health: z.enum(["ok", "degraded", "blocked"]) }),
        ),
      }),
      branch("RouteHealthChange", {
        decision: z.literal("health_change"),
        reason: z.enum([...ROUTE_HEALTH_REASONS, "flag_off"]).nullable(),
        platform: z.enum(PLATFORMS),
        route: z.enum(ROUTES),
        vendor: vendorName().nullable(),
        health_change: b.def("RouteHealthBlock", () =>
          b.obj({
            health: z.enum(HEALTHS),
            fallback: b
              .def("Fallback", () =>
                b.obj({ route: z.enum(ROUTES), vendor: vendorName().nullable() }),
              )
              .nullable(),
            // The alternate's declared scope while in fallback (source-health-canary.md L79,
            // ADR-0052 L33 (d); F-12 as corrected, R-2).
            scope: z.enum(["non_government"]).nullable(),
            evidence: b
              .def("CanaryEvidence", () =>
                b.obj({
                  window_minutes: count(),
                  samples: count(),
                  empty_200: count(),
                  rate: share(),
                  targets: count(),
                }),
              )
              .nullable(),
          }),
        ),
      }),
      branch("Queued", {
        decision: z.literal("queued"),
        reason: z.literal("amber_excluded_government").nullable(),
        ...candidateSubject,
        queued: qualifierBlock(b),
      }),
      branch("MentionOnlyCandidate", {
        decision: z.literal("mention_only"),
        reason: z.null(),
        ...candidateSubject,
        mention_only: qualifierBlock(b),
      }),
      // An ordinary individual's mention, whose profile carries no clear key (ADR-0033).
      branch("MentionOnlyAuthor", {
        decision: z.literal("mention_only"),
        reason: z.null(),
        author_ref: authorRef(),
        mention_only: qualifierBlock(b),
      }),
      branch("Reject", {
        decision: z.literal("reject"),
        reason: z.literal("review_timeout").nullable(),
        ...candidateSubject,
        reject: b.def("RejectBlock", () =>
          b.obj({ rule_hit: ruleHit(), client_ids: z.array(uuid()), expires_at: timestamp() }),
        ),
      }),
      branch("Review", {
        decision: z.literal("review"),
        reason: z.enum(REVIEW_REASONS).nullable(),
        ...candidateSubject,
        review: qualifierBlock(b),
      }),
    ]),
  );
}

export type RegistryDecision = z.infer<ReturnType<typeof buildRegistryDecisions>>;
