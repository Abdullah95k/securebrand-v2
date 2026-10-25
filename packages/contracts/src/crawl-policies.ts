// crawl.policies/v1: the flat column names of the crawl_policies row (ADR-0040, ADR-0070 b)), with
// the change fields and the robots fetch's provenance (ADR-0003). The values are news-robots-checker's
// (Q8).
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { dataShape, metadataShape, usageSignals } from "./metadata.ts";
import { actor, count, host, httpUrl, nonEmpty, sha256Hex, timestamp } from "./primitives.ts";
import {
  ACCESS_MODES,
  CRAWL_JOB_KINDS,
  CRAWL_REASONS,
  CRAWL_STATUSES,
  ROBOTS_STATUSES,
} from "./vocabulary.ts";

export const CRAWL_POLICIES = "crawl.policies/v1";

export function buildCrawlPolicies(b: SchemaBuilder) {
  return b.titled(
    "CrawlPoliciesV1",
    b.obj({
      ...metadataShape(b, CRAWL_POLICIES),
      host: host(),
      status: z.enum(CRAWL_STATUSES),
      crawl_allowed: z.boolean(),
      // Null when allowed (news-robots-checker §5.3 L66-L79), which validate() checks.
      reason: z.enum(CRAWL_REASONS).nullable(),
      access_mode: z.enum(ACCESS_MODES),
      crawl_delay_seconds: count().nullable(),
      robots_status: z.enum(ROBOTS_STATUSES),
      robots_rules: b
        .def("RobotsRules", () =>
          b.obj({
            group: nonEmpty().nullable(),
            rules: b.def("RobotsRuleLists", () =>
              b.obj({ allow: z.array(z.string()), disallow: z.array(z.string()) }),
            ),
            sitemaps: z.array(httpUrl()),
            hash: sha256Hex(), // of the robots.txt bytes
          }),
        )
        .nullable(),
      usage_signals: usageSignals(b),
      rsl: z.discriminatedUnion("found", [
        b.titled("RslAbsent", b.obj({ found: z.literal(false) })),
        b.titled(
          "RslFound",
          b.obj({
            found: z.literal(true),
            url: httpUrl(),
            permits: z.array(nonEmpty()),
            prohibits: z.array(nonEmpty()),
            payment: b
              .def("RslPayment", () =>
                b.obj({ type: nonEmpty(), amount: z.number().min(0).nullable() }),
              )
              .nullable(),
          }),
        ),
      ]),
      payment: b.def("Http402", () =>
        b.obj({ http_402: z.boolean(), price: z.string().nullable() }),
      ),
      checked_at: timestamp(),
      expires_at: timestamp(),
      policy_version: count().min(1),
      changed_fields: z.array(nonEmpty()),
      // The job's requested_by when it has one (F-43): a service on `recheck`, a person on an
      // admin-API `ops_force`; null on `refresh` and `first_check`.
      requested_by: actor().nullable(),
      kind: z.enum(CRAWL_JOB_KINDS),
      ...dataShape(b),
    }),
  );
}

export type CrawlPolicy = z.infer<ReturnType<typeof buildCrawlPolicies>>;
