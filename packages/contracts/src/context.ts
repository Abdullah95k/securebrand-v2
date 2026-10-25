// The typed open-ended objects: raw.items `context` (ADR-0005: the producer-specific fields go
// there, each defined) and poster.profiles `extras` (ADR-0033). Each holds every key some producer
// declares, all optional; registries/context-keys.json and extras-keys.json say which producer may
// use which, and validate() checks it in producer mode. A new key is an optional field, added inside
// the version (ADR-0002, Q1).
import { z } from "zod";
import type { SchemaBuilder } from "./builder.ts";
import { usageSignals, window } from "./metadata.ts";
import {
  PATTERNS,
  count,
  host,
  httpUrl,
  idempotencyKey,
  nonEmpty,
  seriesStep,
  serviceName,
  timestamp,
  token,
  ulid,
  uuid,
} from "./primitives.ts";
import { ACCESS_MODES, HASHTAG_EDGES, TIERS } from "./vocabulary.ts";

export const MENTION_TYPES = ["tag", "mentioned_media", "mentioned_comment"] as const;
export const LIVE_STATES = ["none", "upcoming", "live"] as const;

export const context = (b: SchemaBuilder) =>
  b.def("Context", () =>
    b.obj({
      window: window(b).optional(), // fb-backfill (ADR-0070 e))
      query: b.def("SearchQuery", () => b.obj({ variant: nonEmpty(), rank: count() })).optional(), // fb-keyword-search
      series_step: seriesStep().optional(), // the comment and replies fetchers
      video_channel_id: token().optional(), // yt-comments-fetcher, yt-replies-fetcher (F-25)
      edge: z.enum(HASHTAG_EDGES).optional(), // ig-hashtag-search
      mention_type: z.enum(MENTION_TYPES).optional(), // ig-mentions-fetcher
      mention_of: z.string().regex(PATTERNS.digits).optional(), // ig-mentions-fetcher: the account's ig-user-id
      received_at: timestamp().optional(), // ig-webhook-receiver
      url_key: z.string().regex(PATTERNS.urlKey).optional(), // news-article-extractor
      access_mode: z.enum(ACCESS_MODES).optional(), // news-article-extractor
      usage_signals: usageSignals(b).optional(), // news-article-extractor (ADR-0068 (c))
      update_id: count().optional(), // the Telegram receivers: the delivery id (ADR-0005, ADR-0006)
      discussion_source_id: uuid().optional(), // tg-discussion-receiver
      hashtag_id: z.string().regex(PATTERNS.digits).optional(), // tt-hashtag-feed-poller
      hashtag_name: nonEmpty().optional(), // tt-hashtag-feed-poller
      page: count().optional(), // tt-hashtag-feed-poller, tt-keyword-search
      variant: nonEmpty().optional(), // tt-keyword-search
      country: z.string().regex(PATTERNS.country).optional(), // tt-keyword-search
      connection_id: ulid().optional(), // x-filtered-stream: the delivery id (ADR-0005)
      matching_rules: z
        .array(
          b.def("MatchingRule", () =>
            b.obj({ id: z.string().regex(PATTERNS.digits), tag: nonEmpty() }),
          ),
        )
        .optional(), // x-filtered-stream
      paid: z.boolean().optional(), // the X readers
      query_arm: token().optional(), // x-recent-search
      matched_terms: z.array(nonEmpty()).optional(), // x-recent-search
      partial: z.literal(true).optional(), // yt-keyword-search, yt-pubsub-receiver, yt-uploads-reconciler (ADR-0065 b))
      live_state: z.enum(LIVE_STATES).optional(), // yt-video-details-fetcher
      call_id: ulid().optional(), // yt-video-details-fetcher
      completes_partial_from: serviceName().optional(), // yt-video-details-fetcher
      crawl_id: token().optional(), // web-commoncrawl-scanner
      host: host().optional(), // web-commoncrawl-scanner
      item_key: idempotencyKey().optional(), // a `metrics` record: the observed item's key (ADR-0034)
    }),
  );

export const extras = (b: SchemaBuilder) =>
  b.def("Extras", () =>
    b.obj({
      category: nonEmpty().optional(), // fb-page-resolver, tg-channel-resolver
      location: b
        .def("PageLocation", () =>
          b.obj({ city: z.string().nullable(), country: z.string().nullable() }),
        )
        .optional(), // fb-page-resolver
      website_domains: z.array(host()).optional(), // fb-page-resolver, yt-channel-resolver
      about: z.string().optional(), // fb-page-resolver
      media_count: count().optional(), // ig-account-resolver
      biography: z.string().optional(), // ig-account-resolver
      website: httpUrl().optional(), // ig-account-resolver
      video_count: count().optional(), // tt-user-resolver, yt-channel-resolver
      region: nonEmpty().optional(), // tt-user-resolver
      bio: z.string().optional(), // tt-user-resolver
      bio_link: nonEmpty().optional(), // tt-user-resolver
      following: count().optional(), // x-user-resolver
      location_text: z.string().optional(), // x-user-resolver
      description: z.string().optional(), // x-user-resolver, yt-channel-resolver
      url_domain: host().optional(), // x-user-resolver
      account_age_days: count().optional(), // x-user-resolver
      posts_sampled: count().optional(), // li-org-resolver
      growth: b.def("Growth", () => b.obj({ subscribers_30d: z.number().int() })).optional(), // tg-channel-resolver
      country: z.string().regex(PATTERNS.country).optional(), // yt-channel-resolver
      country_source: z.enum(["snippet", "brandingSettings"]).optional(), // yt-channel-resolver
      default_language: nonEmpty().optional(), // yt-channel-resolver
      view_count: count().optional(), // yt-channel-resolver
      published_at: timestamp().optional(), // yt-channel-resolver
      uploads_playlist_id: token().optional(), // yt-channel-resolver (ADR-0065 c))
      made_for_kids: z.boolean().nullable().optional(), // yt-channel-resolver (null: unknown)
      description_lang: z.enum(["ckb", "ar", "other", "none"]).optional(), // yt-channel-resolver
      host: host().optional(), // news-site-resolver
      site_profile: b
        .def("SiteProfile", () =>
          b.obj({
            feeds: z.array(
              b.def("Feed", () =>
                b.obj({
                  url: httpUrl(),
                  format: nonEmpty(),
                  items: count(),
                  newest_at: timestamp().nullable(),
                  has_body: z.boolean(),
                }),
              ),
            ),
            news_sitemap: httpUrl().nullable(),
            sitemaps: z.array(httpUrl()),
            homepage_diff: z.boolean(),
            article_url_patterns: z.array(nonEmpty()),
            comments_provider: nonEmpty().nullable(),
            disqus_shortname: nonEmpty().nullable(),
            access_mode: z.enum(ACCESS_MODES),
            articles_per_day_estimate: z.number().min(0),
            last_article_at: timestamp().nullable(),
          }),
        )
        .optional(), // news-site-resolver
      proposed_tier: z.literal(TIERS).optional(), // news-site-resolver
      discovered_by: serviceName().optional(), // news-site-resolver
      crawl_allowed: z.boolean().optional(), // news-site-resolver
    }),
  );
