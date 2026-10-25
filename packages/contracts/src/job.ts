// job/v1: one envelope for every queue (ADR-0011), discriminated by a closed `kind` list, each kind
// with its declared fields. Where one kind serves several queues or producers with different fields
// (`refresh`, `reconciliation`, `ops_force`, `recompute`), the producer table's row names the fields
// it requires (registries/producers.json), which validate() checks when it is given the queue.
// Priority, route and vendor never travel in a job (ADR-0011, ADR-0018); `reason` is never the type.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { metadataShape } from "./metadata.ts";
import { tier } from "./source-columns.ts";
import {
  PATTERNS,
  actor,
  candidateKey,
  count,
  host,
  httpUrl,
  metricsStep,
  nonEmpty,
  platformId,
  prefixedSha256,
  rawRef,
  seriesStep,
  snakeName,
  timestamp,
  token,
  ulid,
  uuid,
} from "./primitives.ts";
import {
  BACKFILL_REASONS,
  COMMENT_PROFILES,
  HASHTAG_EDGES,
  JOB_KIND_VALUES,
  KEYWORD_HISTORY_REASONS,
  PLATFORMS,
  REVIEW_CARD_ACTIONS,
  RECONCILIATION_REASONS,
  RESOLVE_ORIGINS,
} from "./vocabulary.ts";

export const JOB = "job/v1";

/** The scheduler's object on every queue (ADR-0011, ADR-0060); a replies job adds `thread_ids`. */
export const postRef = (b: SchemaBuilder) =>
  b.def("PostRef", () =>
    b.obj({
      item_id: uuid(),
      platform: z.enum(PLATFORMS),
      platform_id: platformId(), // the id in the post's key (ADR-0007)
      url: httpUrl().optional(),
      thread_ids: z.array(platformId()).optional(), // the parent comments' platform ids
    }),
  );

const envelope = (b: SchemaBuilder) => ({
  ...metadataShape(b, JOB),
  job_id: ulid(),
  due_at: timestamp(),
  attempt: count().min(1),
  // The default partition key; a queue that keys on another field names it (ADR-0004).
  source_id: uuid().optional(),
  // Ops and client requests (ADR-0012 L34): the admin API's request and the actor it records.
  request_id: ulid().optional(),
  requested_by: actor().optional(),
  must_finish_by: timestamp().optional(), // ADR-0057
});

const window = () => ({ window_start: timestamp(), window_end: timestamp() });
const cap = (b: SchemaBuilder) =>
  b.def("BackfillCap", () => b.obj({ max_age_days: count(), max_items: count().nullable() }));
const request = () => ({ request_id: ulid(), requested_by: actor() });

const resolveShape = () => ({
  candidate_key: candidateKey(), // as issued, echoed (ADR-0032)
  platform: z.enum(PLATFORMS),
  // At least one of the three, checked by validate().
  platform_id: platformId().nullable(),
  handle: nonEmpty().nullable(),
  url: httpUrl().nullable(),
  client_ids: z.array(uuid()),
  seed_list: z.boolean(),
});

export function buildJob(b: SchemaBuilder) {
  const kind = (name: string, title: string, shape: z.ZodRawShape) =>
    b.titled(title, b.obj({ ...envelope(b), kind: z.literal(name), ...shape }));
  return b.titled(
    "JobV1",
    z.discriminatedUnion("kind", [
      kind("rotation", "RotationJob", {
        tier: tier().optional(),
        edge: z.enum(HASHTAG_EDGES).optional(), // jobs.ig-hashtag-search (F-27)
        crawl_id: token().optional(), // jobs.web-commoncrawl-scanner, its key (F-31)
      }),
      kind("reconciliation", "ReconciliationJob", {
        // The X gap on jobs.x-recent-search (ADR-0064).
        query: nonEmpty().optional(),
        window_start: timestamp().optional(),
        window_end: timestamp().optional(),
        source_ids: z.array(uuid()).optional(),
        client_ids: z.array(uuid()).optional(),
        post_ref: postRef(b).optional(), // a whole-thread read
        reason: z.enum(RECONCILIATION_REASONS).optional(), // yt-uploads-reconciler only
      }),
      kind("backfill", "BackfillJob", {
        run_id: ulid(),
        reason: z.enum(BACKFILL_REASONS),
        ...window(),
        cap: cap(b),
        edge: z.enum(HASHTAG_EDGES).optional(),
      }),
      kind("keyword_history", "KeywordHistoryJob", {
        run_id: ulid(),
        reason: z.enum(KEYWORD_HISTORY_REASONS),
        ...window(),
        cap: cap(b),
      }),
      kind("comments", "CommentsJob", {
        post_ref: postRef(b),
        series_step: seriesStep(),
        profile: z.enum(COMMENT_PROFILES),
      }),
      kind("replies", "RepliesJob", {
        post_ref: postRef(b),
        series_step: seriesStep(),
        profile: z.enum(COMMENT_PROFILES),
        window_start: timestamp().optional(), // jobs.x-full-archive-search (ADR-0059, ADR-0064)
      }),
      kind("metrics", "MetricsJob", { post_ref: postRef(b), series_step: metricsStep() }),
      kind("first_sight", "FirstSightJob", {
        post_ref: postRef(b), // one video
        origin_kind: z.enum(JOB_KIND_VALUES), // the kind of the job that found the id (ADR-0065)
      }),
      kind("refresh", "RefreshJob", {
        candidate_key: candidateKey().optional(), // a resolver's own source; news-site-resolver's site
        host: host().optional(), // news-robots-checker
        reason: snakeName().optional(), // news-site-resolver: the trigger
        post_ref: postRef(b).optional(), // yt-text-purger to the YouTube fetchers
        run_id: ulid().optional(),
        refresh_for_client_ids: z.array(uuid()).optional(),
      }),
      kind("resolve", "ResolveJob", { ...resolveShape(), origin: z.enum(RESOLVE_ORIGINS) }),
      kind("manual_candidate", "ManualCandidateJob", {
        ...resolveShape(),
        origin: z.literal("manual"),
        ...request(),
      }),
      kind("first_check", "FirstCheckJob", { host: host() }),
      kind("recheck", "RecheckJob", { host: host(), requested_by: actor() }),
      kind("ops_force", "OpsForceJob", {
        post_ref: postRef(b).optional(),
        target_ids: z.array(platformId()).optional(),
        edge: z.enum(HASHTAG_EDGES).optional(),
        client_id: uuid().optional(), // an ops_force limited to one client's sources (F-31)
        candidate_key: candidateKey().optional(), // the resolver queues' key
        host: host().optional(), // jobs.news-robots-checker's key
        crawl_id: token().optional(), // jobs.web-commoncrawl-scanner's key
      }),
      kind("push", "PushJob", {
        body: z.union([z.string(), z.record(z.string(), z.unknown())]), // as received
        received_at: timestamp(),
        headers: z.record(z.string(), z.string()), // the ones the worker reads
      }),
      kind("replay", "ReplayJob", {
        run_id: ulid(),
        from: timestamp(),
        to: timestamp(),
        platforms: z.array(z.enum(PLATFORMS)).optional(),
        reason: snakeName(),
        ...request(),
      }),
      kind("rerun", "RerunJob", {
        run_id: ulid(),
        task: z.string().regex(PATTERNS.analysisTask),
        model_version: z.string().regex(PATTERNS.modelVersion),
        from: timestamp(),
        to: timestamp(),
        platforms: z.array(z.enum(PLATFORMS)).optional(),
        client_id: uuid().optional(), // a client's new topic
        taxonomy_id: z
          .string()
          .regex(/^[A-Za-z0-9_.-]+$/)
          .optional(),
        ...request(),
      }),
      kind("rematch", "RematchJob", {
        client_id: uuid(),
        keyword_ids: z.array(uuid()),
        window_days: count(), // keywords.rematch_days
        ...request(),
      }),
      kind("recompute", "RecomputeJob", {
        // deletion-propagator's bucket list, or the admin API's range (producers.json).
        run_id: ulid().optional(),
        deletion_id: z.string().regex(PATTERNS.deletionId).optional(),
        buckets: z
          .array(
            b.def("RecomputeBucket", () =>
              b.obj({ source_id: uuid(), hours: z.array(timestamp()) }),
            ),
          )
          .optional(),
        keyword_ids: z.array(uuid()).optional(),
        from: timestamp().optional(),
        to: timestamp().optional(),
      }),
      kind("retention_sweep", "RetentionSweepJob", {
        run_id: ulid(),
        cutoff: timestamp(),
        next_sweep_at: timestamp(),
      }),
      // No item, text or provenance: a job carries no platform data (ADR-0003; Q6).
      kind("analyze", "AnalyzeJob", {
        source_id: uuid(),
        item_id: uuid(),
        item_version: count().min(1),
        content_hash: prefixedSha256(),
      }),
      kind("candidate_retry", "CandidateRetryJob", {
        hit_id: uuid(),
        item_id: uuid(),
        raw_ref: rawRef(),
        keyword_ids: z.array(uuid()),
        client_ids: z.array(uuid()),
        hit_at: timestamp(),
        matched_term: nonEmpty(),
        form_id: nonEmpty(),
        keyword_set_version: z.string().regex(PATTERNS.keywordSetVersion),
      }),
      kind("review_answer", "ReviewAnswerJob", {
        candidate_key: candidateKey(),
        card_id: uuid(),
        decision_id: ulid(),
        action: z.enum(REVIEW_CARD_ACTIONS),
        ...request(),
      }),
      kind("export", "ExportJob", {
        client_id: uuid().nullable(), // null for X's own export
        from: timestamp(),
        to: timestamp(),
        ...request(),
      }),
    ]),
  );
}

export type Job = z.infer<ReturnType<typeof buildJob>>;
