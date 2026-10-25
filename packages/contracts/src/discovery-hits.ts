// discovery.hits/v1: one schema for every candidate (ADR-0031), discriminated by `evidence_type`,
// each with its own optional `evidence` block (the keys are Q8's). The candidate key takes ADR-0032's
// four forms and is echoed as issued.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { countDef, dataShape, day, metadataShape, shareDef } from "./metadata.ts";
import {
  PATTERNS,
  candidateKey,
  count,
  httpUrl,
  nonEmpty,
  platformId,
  sha256Hex,
  share,
  snakeName,
  timestamp,
  token,
  uuid,
} from "./primitives.ts";
import { CANDIDATE_TYPES, PLATFORMS, SEARCH_ENGINES } from "./vocabulary.ts";

export const DISCOVERY_HITS = "discovery.hits/v1";

export const candidate = (b: SchemaBuilder) =>
  b.def("Candidate", () =>
    b.obj({
      candidate_key: candidateKey(),
      platform: z.enum(PLATFORMS),
      // A poster kind, or null where the producer cannot tell (keyword-matcher §6.2 L111).
      type: z.enum(CANDIDATE_TYPES).nullable(),
      platform_id: platformId().nullable(),
      handle: nonEmpty().nullable(),
      url: httpUrl().nullable(),
    }),
  );

const shape = (b: SchemaBuilder) => ({
  ...metadataShape(b, DISCOVERY_HITS),
  candidate: candidate(b),
  // Exactly one of item_id and url, checked by validate().
  item_id: uuid().nullable(),
  url: httpUrl().nullable(),
  source_id: uuid(),
  keyword_ids: z.array(uuid()),
  client_ids: z.array(uuid()),
  hit_at: timestamp(),
  ...dataShape(b),
});

export function buildDiscoveryHits(b: SchemaBuilder) {
  const branch = <E extends z.ZodType>(type: string, title: string, evidence: E) =>
    b.titled(
      title,
      b.obj({ ...shape(b), evidence_type: z.literal(type), evidence: evidence.optional() }),
    );
  return b.titled(
    "DiscoveryHitsV1",
    z.discriminatedUnion("evidence_type", [
      branch(
        "keyword_hit",
        "KeywordHitDiscovery",
        b.def("KeywordHitEvidence", () =>
          b.obj({
            hit_id: uuid().optional(),
            matched_term: nonEmpty().optional(),
            form_id: nonEmpty().optional(),
            keyword_set_version: z.string().regex(PATTERNS.keywordSetVersion).optional(),
          }),
        ),
      ),
      branch(
        "container",
        "ContainerDiscovery",
        b.def("ContainerEvidence", () => b.obj({ name: nonEmpty().optional() })),
      ),
      branch(
        "early_signal",
        "EarlySignalDiscovery",
        b.def("EarlySignalEvidence", () =>
          b.obj({
            matched_terms: z.array(nonEmpty()).optional(),
            lang: token().optional(),
            // The platform's counts under its own names.
            public_metrics: z.record(z.string(), countDef(b)).optional(), // snake_case keys, validate()
            display_name: z.string().optional(),
          }),
        ),
      ),
      branch(
        "page_search",
        "PageSearchDiscovery",
        b.def("PageSearchEvidence", () =>
          b.obj({
            query: nonEmpty().optional(),
            name: z.string().optional(),
            is_verified: z.boolean().optional(),
            location: b
              .def("SearchLocation", () =>
                b.obj({ city: z.string().nullable(), country: z.string().nullable() }),
              )
              .optional(),
          }),
        ),
      ),
      branch(
        "web_search",
        "WebSearchDiscovery",
        b.def("WebSearchEvidence", () =>
          b.obj({
            canonical_url_hash: sha256Hex().optional(),
            engines: z.array(z.enum(SEARCH_ENGINES)).optional(),
            sightings: count().optional(),
            first_seen_at: timestamp().optional(),
            title: z.string().optional(),
            snippet: z.string().optional(),
          }),
        ),
      ),
      // web-commoncrawl-scanner's hit has no producing source (web-commoncrawl-scanner.md L99; F-31).
      b.titled(
        "CommoncrawlDiscovery",
        b.obj({
          ...shape(b),
          source_id: uuid().nullable(),
          evidence_type: z.literal("commoncrawl"),
          evidence: b
            .def("CommoncrawlEvidence", () =>
              b.obj({
                crawl_id: token().optional(),
                captures: count().optional(),
                first_capture: day().optional(),
                last_capture: day().optional(),
                sample_urls: z.array(httpUrl()).optional(),
                path_signals: z.array(snakeName()).optional(),
                // Shares keyed by the index's language codes, for example `ara`.
                language_share: z.record(z.string(), shareDef(b)).optional(), // snake_case keys, validate()
                news_score: share().optional(),
              }),
            )
            .optional(),
        }),
      ),
    ]),
  );
}

export type DiscoveryHit = z.infer<ReturnType<typeof buildDiscoveryHits>>;
