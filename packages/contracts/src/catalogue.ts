// The catalogue: every schema id of the package and its Zod schema, built once per mode from one
// definition each (ADR-0002: producers validate strictly, consumers tolerate unknown fields of a known
// version). Built lazily, so importing the package costs nothing until a schema is used.
import type { z } from "zod";
import { buildArticleUrls } from "./article-urls.ts";
import { createBuilder, type Mode, type SchemaBuilder, type SchemaMeta } from "./builder.ts";
import { buildCrawlPolicies } from "./crawl-policies.ts";
import { buildDeletions } from "./deletions.ts";
import { buildDiscoveryHits } from "./discovery-hits.ts";
import { buildDlq } from "./dlq.ts";
import { buildItemHits } from "./item-hits.ts";
import { buildItemMetrics } from "./item-metrics.ts";
import { buildItemsAnalysis } from "./items-analysis.ts";
import { buildItemsNormalized } from "./items-normalized.ts";
import { buildJob } from "./job.ts";
import { buildJobsCompleted } from "./jobs-completed.ts";
import { buildN8nAlert, buildN8nCard } from "./n8n.ts";
import { buildNewsDedup } from "./news-dedup.ts";
import { buildPosterProfiles } from "./poster-profiles.ts";
import { PATTERNS } from "./primitives.ts";
import { buildRawItems } from "./raw-items.ts";
import { buildRegistryDecisions } from "./registry-decisions.ts";
import { buildSearchResults } from "./search-results.ts";
import { buildSourceEvents } from "./source-events.ts";

/**
 * Data messages carry provenance and a retention class; control messages carry neither (ADR-0003),
 * except the dead letter, which copies a data original's provenance and class (F-42).
 */
export type SchemaClass = "data" | "control";

export interface CatalogueEntry {
  readonly id: string;
  readonly class: SchemaClass;
  readonly build: (b: SchemaBuilder) => z.ZodType;
}

export const CATALOGUE: readonly CatalogueEntry[] = [
  { id: "raw.items/v1", class: "data", build: buildRawItems },
  { id: "items.normalized/v1", class: "data", build: buildItemsNormalized },
  { id: "item.hits/v1", class: "data", build: buildItemHits },
  { id: "discovery.hits/v1", class: "data", build: buildDiscoveryHits },
  { id: "poster.profiles/v1", class: "data", build: buildPosterProfiles },
  { id: "registry.decisions/v1", class: "data", build: buildRegistryDecisions },
  { id: "source.events/v1", class: "control", build: buildSourceEvents },
  { id: "items.analysis/v1", class: "data", build: buildItemsAnalysis },
  { id: "item.metrics/v1", class: "data", build: buildItemMetrics },
  { id: "deletions/v1", class: "data", build: buildDeletions },
  { id: "article.urls/v1", class: "data", build: buildArticleUrls },
  { id: "search.results/v1", class: "data", build: buildSearchResults },
  { id: "crawl.policies/v1", class: "data", build: buildCrawlPolicies },
  { id: "news.dedup/v1", class: "data", build: buildNewsDedup },
  { id: "jobs.completed/v1", class: "control", build: buildJobsCompleted },
  { id: "job/v1", class: "control", build: buildJob },
  // Control, but a record copies its data original's provenance and class (F-42).
  { id: "dlq.<service>/v1", class: "control", build: buildDlq },
  // Producer-only notices over HTTP, not topics: producer, no provenance (F-51).
  { id: "n8n.alert/v1", class: "control", build: buildN8nAlert },
  { id: "n8n.card/v1", class: "control", build: buildN8nCard },
];

const built = new Map<Mode, Map<string, z.ZodType>>();

/** The schema of `id` (a concrete `dlq.<service>/v1` maps to the shared definition) in `mode`. */
export function schemaFor(id: string, mode: Mode): z.ZodType | undefined {
  let schemas = built.get(mode);
  if (!schemas) {
    const b = createBuilder(mode);
    schemas = new Map(CATALOGUE.map((e) => [e.id, e.build(b)]));
    built.set(mode, schemas);
  }
  return schemas.get(catalogueId(id));
}

/** The catalogue id of a concrete schema id. */
export function catalogueId(id: string): string {
  return PATTERNS.dlqSchema.test(id) ? "dlq.<service>/v1" : id;
}

export function catalogueEntry(id: string): CatalogueEntry | undefined {
  const key = catalogueId(id);
  return CATALOGUE.find((e) => e.id === key);
}

/** The producer-mode schemas with their JSON Schema metadata, for the exporter. */
export function exportCatalogue(registry: z.core.$ZodRegistry<SchemaMeta>): Map<string, z.ZodType> {
  const b = createBuilder("producer", registry);
  return new Map(CATALOGUE.map((e) => [e.id, e.build(b)]));
}
