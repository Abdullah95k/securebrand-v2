// Caps and hosts of the web probe (build-plan/sessions/W0-web-search-probe.md). Nothing here is a secret.

export const CAPS = {
  /** Brief: at most 30 Perplexity requests (about USD 0.15 at USD 5 per 1,000). */
  perplexityRequests: 30,
  perplexityUsdPerRequest: 0.005,
  /** Brief: 30 Mojeek queries. */
  mojeekQueries: 30,
  mojeekGbpPerQuery: 0.003,
  /** Brief: GDELT at 1 request per 5 s. We wait longer than that, and set our own request ceiling. */
  gdeltMinGapMs: 5500,
  gdeltRequests: 60,
  /** Common Crawl: slow and polite, sequential, with a pause; no number in the brief, so ours. */
  commonCrawlMinGapMs: 4000,
  commonCrawlRequests: 20,
} as const;

/** The only hosts the probe may contact. Anything else is refused before a request is made. */
export const ALLOWED_HOSTS = [
  "api.perplexity.ai",
  "api.mojeek.com",
  "api.gdeltproject.org",
  "index.commoncrawl.org",
] as const;

export type Vendor = "perplexity" | "mojeek" | "gdelt" | "commoncrawl";

/** Mojeek Startup plan terms forbid storing results: only counts, timings and field names may be kept. */
export type MojeekPlan = "business" | "startup";

export const FIXTURE_DIR = "fixtures/web";
export const RAW_DIR = "fixtures/web/raw";
export const KEYWORDS_FILE = "tools/probes/web/keywords.txt";
export const PLACEHOLDER_KEYWORD = "PLACEHOLDER-KEYWORD";
