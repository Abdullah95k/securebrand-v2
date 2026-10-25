// The contracts package (F2): validate() in both modes, the version catalogue, the key and id helpers,
// the registries the SDK enforces, the closed lists, the n8n signing helper and the message types. The
// Zod schemas themselves are under "contracts/schemas"; most services need only validate().
export type { Mode } from "./builder.ts";
export { canonicalJson } from "./canonical-json.ts";
export {
  CATALOGUE,
  catalogueEntry,
  catalogueId,
  type CatalogueEntry,
  type SchemaClass,
} from "./catalogue.ts";
export { ContractError } from "./errors.ts";
export * from "./keys/index.ts";
export { signN8n, verifyN8n, type N8nHeaders, type Verification } from "./n8n.ts";
export { PATTERNS } from "./primitives.ts";
export * from "./registries/index.ts";
export {
  validate,
  type ClientType,
  type IssuePath,
  type ValidateOptions,
  type ValidationIssue,
  type ValidationResult,
} from "./validate.ts";
export { SCHEMA_IDS, classifyVersion, type VersionVerdict } from "./versions.ts";
export * from "./vocabulary.ts";

// Each schema id as a constant, and the type of a message that passes it (producer mode).
export { ARTICLE_URLS, type ArticleUrl } from "./article-urls.ts";
export { CRAWL_POLICIES, type CrawlPolicy } from "./crawl-policies.ts";
export { DELETIONS, type Deletion } from "./deletions.ts";
export { DISCOVERY_HITS, type DiscoveryHit } from "./discovery-hits.ts";
export { DLQ, type DeadLetter } from "./dlq.ts";
export { ITEM_HITS, type ItemHit } from "./item-hits.ts";
export { ITEM_METRICS, type ItemMetric } from "./item-metrics.ts";
export { ITEMS_ANALYSIS, type ItemAnalysis } from "./items-analysis.ts";
export { ITEMS_NORMALIZED, type NormalizedItem } from "./items-normalized.ts";
export { JOB, type Job } from "./job.ts";
export { JOBS_COMPLETED, REPORT_KIND_FIELDS, type JobCompleted } from "./jobs-completed.ts";
export { N8N_ALERT, N8N_CARD, type N8nAlert, type N8nCard } from "./n8n.ts";
export { NEWS_DEDUP, type NewsDedupVerdict } from "./news-dedup.ts";
export { POSTER_PROFILES, type PosterProfile } from "./poster-profiles.ts";
export { RAW_ITEMS, type RawItem } from "./raw-items.ts";
export { REGISTRY_DECISIONS, type RegistryDecision } from "./registry-decisions.ts";
export { SEARCH_RESULTS, type SearchResult } from "./search-results.ts";
export { SOURCE_EVENTS, type SourceEvent } from "./source-events.ts";
