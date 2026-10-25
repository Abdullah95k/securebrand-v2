// jobs.completed/v1: one report per job, written only by the SDK job wrapper, a job that ends in the
// DLQ included (ADR-0017). A control message: `producer` only (ADR-0003). Discriminated by `status`,
// each with the reason it allows (Q8); kind fields are declared per kind, which validate() checks.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { postRef } from "./job.ts";
import { metadataShape } from "./metadata.ts";
import {
  PATTERNS,
  candidateKey,
  count,
  host,
  platformId,
  seriesStep,
  timestamp,
  token,
  ulid,
  uuid,
} from "./primitives.ts";
import { CAPPED_REASONS, GONE_REASONS, JOB_KINDS, NOT_ALLOWED_REASONS } from "./vocabulary.ts";

export const JOBS_COMPLETED = "jobs.completed/v1";

/** The kind fields and the kinds that may carry them (ADR-0017, ADR-0019, ADR-0020, ADR-0064; Q8). */
export const REPORT_KIND_FIELDS = {
  oldest_item_at: ["backfill", "keyword_history"],
  complete: ["comments", "replies"],
  stored_before: ["comments", "replies"],
  comments_total: ["comments", "replies"],
} as const;

const shape = (b: SchemaBuilder) => {
  const span = () =>
    b.def("UncoveredWindow", () => b.obj({ window_start: timestamp(), window_end: timestamp() }));
  return {
    ...metadataShape(b, JOBS_COMPLETED),
    job_id: ulid(),
    queue: z.string().regex(PATTERNS.queue),
    kind: z.enum(JOB_KINDS),
    // The job's partition-key fields as the job had them (ADR-0004).
    source_id: uuid().optional(),
    candidate_key: candidateKey().optional(),
    host: host().optional(),
    crawl_id: token().optional(),
    client_id: uuid().nullable().optional(),
    run_id: ulid().optional(),
    request_id: ulid().optional(),
    post_ref: postRef(b).optional(),
    series_step: seriesStep().optional(),
    attempt: count().min(1),
    finished_at: timestamp(),
    report: b.def("Report", () =>
      b.obj({
        new_count: count(),
        seen_count: count(),
        pages: count(),
        cost_units: z.number().min(0),
        reply_candidates: z.array(
          b.def("ReplyCandidate", () =>
            b.obj({
              thread_id: platformId(), // a parent comment's platform id, as `thread_ids` lists it
              reply_count: count().nullable(), // the platform's count, null where it gives none
            }),
          ),
        ),
      }),
    ),
    oldest_item_at: timestamp().nullable().optional(),
    complete: z.boolean().optional(),
    stored_before: count().optional(),
    comments_total: count().nullable().optional(),
    paid_user_reads: count().optional(), // X jobs
    free_rereads: count().optional(), // X jobs
    gap_unfilled: span().nullable().optional(), // reconciliation on jobs.x-recent-search (ADR-0064)
    uncovered: span().nullable().optional(), // rotation on jobs.x-recent-search, with `partial`
  };
};

export function buildJobsCompleted(b: SchemaBuilder) {
  const status = (name: string, title: string, reason: z.ZodType, extra: z.ZodRawShape = {}) =>
    b.titled(title, b.obj({ ...shape(b), status: z.literal(name), reason, ...extra }));
  return b.titled(
    "JobsCompletedV1",
    z.discriminatedUnion("status", [
      status("done", "DoneReport", z.null()),
      status("partial", "PartialReport", z.null()),
      status("capped", "CappedReport", z.null(), { capped_reason: z.enum(CAPPED_REASONS) }),
      status("quota_denied", "QuotaDeniedReport", z.null()),
      status("failed", "FailedReport", z.null()),
      status("skipped_flag_off", "SkippedFlagOffReport", z.literal("flag_off")),
      status("not_allowed", "NotAllowedReport", z.enum(NOT_ALLOWED_REASONS)),
      status("gone", "GoneReport", z.enum(GONE_REASONS)),
    ]),
  );
}

export type JobCompleted = z.infer<ReturnType<typeof buildJobsCompleted>>;
