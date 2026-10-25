// article.urls/v1: one flat schema for every news finder (ADR-0036, ADR-0059). The article key is
// the extractor's to derive from the page's canonical URL, so none travels here.
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { dataShape, metadataShape } from "./metadata.ts";
import { PATTERNS, httpUrl, nonEmpty, sha256Hex, timestamp, uuid } from "./primitives.ts";
import { FOUND_VIA, SEARCH_ENGINES } from "./vocabulary.ts";

export const ARTICLE_URLS = "article.urls/v1";

export function buildArticleUrls(b: SchemaBuilder) {
  return b.titled(
    "ArticleUrlsV1",
    b.obj({
      ...metadataShape(b, ARTICLE_URLS),
      source_id: uuid(), // the site
      url: httpUrl(),
      url_key: z.string().regex(PATTERNS.urlKey),
      found_via: z.enum(FOUND_VIA),
      found_at: timestamp(),
      title: z.string().optional(),
      published_at: timestamp().nullable().optional(),
      feed_url: httpUrl().optional(),
      feed_format: nonEmpty().optional(),
      canonical_url: httpUrl().optional(),
      canonical_url_hash: sha256Hex().optional(),
      snippet: z.string().optional(),
      engines: z.array(z.enum(SEARCH_ENGINES)).optional(),
      keyword_ids: z.array(uuid()).optional(),
      client_ids: z.array(uuid()).optional(),
      ...dataShape(b),
    }),
  );
}

export type ArticleUrl = z.infer<ReturnType<typeof buildArticleUrls>>;
