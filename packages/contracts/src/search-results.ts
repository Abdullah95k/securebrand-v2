// search.results/v1: the engines' message for all four producers (ADR-0037, ADR-0036). The job
// travels in producer.job_id (ADR-0003); `canonical_url_hash` is the shared normaliser's (Q9).
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { dataShape, day, metadataShape } from "./metadata.ts";
import {
  PATTERNS,
  count,
  host,
  httpUrl,
  nonEmpty,
  rawRef,
  sha256Hex,
  token,
  uuid,
} from "./primitives.ts";
import { SEARCH_ENGINES } from "./vocabulary.ts";

export const SEARCH_RESULTS = "search.results/v1";

export function buildSearchResults(b: SchemaBuilder) {
  return b.titled(
    "SearchResultsV1",
    b.obj({
      ...metadataShape(b, SEARCH_RESULTS),
      engine: z.enum(SEARCH_ENGINES),
      source_id: uuid(), // the keyword rule
      keyword_ids: z.array(uuid()),
      client_ids: z.array(uuid()),
      query: b.def("SearchRequest", () =>
        b.obj({
          text: nonEmpty(),
          variant: token().nullable(),
          lang: token().nullable(), // null for GDELT
          country: z.string().regex(PATTERNS.country).nullable(),
          request_id: nonEmpty().nullable(), // the engine's id when it returns one
        }),
      ),
      result: b.def("SearchHit", () =>
        b.obj({
          rank: count().min(1),
          title: z.string().nullable(),
          url: httpUrl(),
          snippet: z.string().nullable(),
          date: day().nullable(),
          last_updated: day().nullable(),
        }),
      ),
      canonical_url: httpUrl(),
      canonical_url_hash: sha256Hex(),
      raw_ref: rawRef(),
      hints: b
        .def("GdeltHints", () =>
          b.obj({
            domain: host().nullable(),
            language: z.string().nullable(),
            source_country: z.string().nullable(),
          }),
        )
        .optional(),
      ...dataShape(b),
    }),
  );
}

export type SearchResult = z.infer<ReturnType<typeof buildSearchResults>>;
