// The closed lists of the contracts, each with the decision that fixes it. A closed list gains a value
// only through a new schema version with its dual-publish window (ADR-0002, Q1); service names and
// vendors are registry data instead (registries/*.json).

export const PLATFORMS = [
  "facebook",
  "instagram",
  "tiktok",
  "x",
  "linkedin",
  "telegram",
  "youtube",
  "news",
  "web",
] as const; // CONVENTIONS v1.1 L105
export type Platform = (typeof PLATFORMS)[number];

export const ROUTES = ["green", "amber"] as const; // ADR-0070 c)
export type Route = (typeof ROUTES)[number];

export const RETENTION_CLASSES = [
  "meta_on_request",
  "vendor_agreed",
  "x_24h_sync",
  "news_excerpt",
  "telegram_bot",
  "tiktok_display",
  "linkedin_48h",
  "linkedin_org",
  "youtube_30d_text",
] as const; // ADR-0054, ADR-0055, ADR-0056
export type RetentionClass = (typeof RETENTION_CLASSES)[number];

export const SOURCE_TYPES = [
  "page",
  "group",
  "account",
  "creator",
  "channel",
  "company_page",
  "site",
  "hashtag",
  "keyword_rule",
] as const; // CONVENTIONS v1.1 L105
export type SourceType = (typeof SOURCE_TYPES)[number];

// A candidate is a poster or a container, never a hashtag or a keyword rule (search-hit-router §5.3).
export const CANDIDATE_TYPES = [
  "page",
  "group",
  "account",
  "creator",
  "channel",
  "company_page",
  "site",
] as const;

export const CONTENT_KINDS = ["post", "video", "comment", "article", "result"] as const; // ADR-0008
export type ContentKind = (typeof CONTENT_KINDS)[number];
export const ARCHIVE_ONLY_KINDS = ["profile", "reaction", "search_response", "metrics"] as const; // ADR-0008
export type ArchiveOnlyKind = (typeof ARCHIVE_ONLY_KINDS)[number];
export const RECORD_KINDS = [...CONTENT_KINDS, ...ARCHIVE_ONLY_KINDS] as const;
export type RecordKind = (typeof RECORD_KINDS)[number];

// ADR-0011's closed list, with review_answer and export added as ADR-0067 L26 and L33 require (Q13).
export const JOB_KINDS = [
  "rotation",
  "reconciliation",
  "backfill",
  "keyword_history",
  "comments",
  "replies",
  "metrics",
  "first_sight",
  "refresh",
  "resolve",
  "manual_candidate",
  "first_check",
  "recheck",
  "ops_force",
  "push",
  "replay",
  "rerun",
  "rematch",
  "recompute",
  "retention_sweep",
  "analyze",
  "candidate_retry",
  "review_answer",
  "export",
] as const;
export type JobKind = (typeof JOB_KINDS)[number];

// Why a record was read: the job's kind, or push and stream for jobless receivers (ADR-0005).
export const JOB_KIND_VALUES = [...JOB_KINDS, "stream"] as const;
export type JobKindValue = (typeof JOB_KIND_VALUES)[number];

export const LIFECYCLES = ["active", "dormant", "retired"] as const; // ADR-0049
export const HEALTHS = ["ok", "degraded", "fallback", "blocked"] as const; // ADR-0016
export const TIERS = [1, 2, 3] as const; // ADR-0049
export const ADDED_BY = ["qualifier", "client", "ops"] as const; // CONVENTIONS v1.1 L105
export const VISIBILITIES = ["owner", "watchers", "pool"] as const; // ADR-0053
export type Visibility = (typeof VISIBILITIES)[number];

// lang-dialect-id's labels (ADR-0033); lang_share adds the keys ar_iraqi and sample.
export const LANG_LABELS = ["ar", "ckb", "en", "mixed", "other", "und"] as const;

// account_type, each value an organisation kind or a person kind (ADR-0010 L55; Q7).
export const ORGANISATION_ACCOUNT_TYPES = [
  "page",
  "group",
  "business",
  "organization",
  "channel",
  "company_page",
  "site",
] as const;
export const PERSON_ACCOUNT_TYPES = [
  "creator",
  "public_figure",
  "individual",
  "business_or_creator",
  "organization_or_public_figure",
] as const;
export const ACCOUNT_TYPES = [...ORGANISATION_ACCOUNT_TYPES, ...PERSON_ACCOUNT_TYPES] as const;
export type AccountType = (typeof ACCOUNT_TYPES)[number];
// Platforms whose terms forbid listing a person's account, so a person kind is never public there
// (ADR-0010 L70-L72).
export const PERSON_UNLISTABLE_PLATFORMS = ["tiktok", "instagram", "linkedin"] as const;

// deletions/v1 (ADR-0035, ADR-0054).
export const DELETION_REASONS = [
  "platform_sync",
  "retention",
  "author_request",
  "client_offboarding",
  "legal",
  "authorization_revoked",
  "client_request",
] as const;
export type DeletionReason = (typeof DELETION_REASONS)[number];
// The reasons whose signal is no platform fetch: route and vendor are null (ADR-0003 L28; F-08).
export const NON_FETCH_DELETION_REASONS = [
  "author_request",
  "client_offboarding",
  "client_request",
  "legal",
  "retention",
] as const;
export const FETCH_DELETION_REASONS = ["platform_sync", "authorization_revoked"] as const;
export const DELETION_SCOPES = ["item", "author", "source", "client"] as const;
export type DeletionScope = (typeof DELETION_SCOPES)[number];
export const DELETION_MODES = ["delete", "purge_text", "purge_derived", "withhold"] as const;
export type DeletionMode = (typeof DELETION_MODES)[number];

// jobs.completed/v1 (ADR-0017, ADR-0020; Q8).
export const COMPLETION_STATUSES = [
  "done",
  "partial",
  "capped",
  "quota_denied",
  "failed",
  "skipped_flag_off",
  "not_allowed",
  "gone",
] as const;
export const CAPPED_REASONS = [
  "route_cap",
  "budget",
  "deadline",
  "failed",
  "no_history",
  "flag_off",
] as const;
export const SKIPPED_FLAG_OFF_REASONS = ["flag_off"] as const;
export const NOT_ALLOWED_REASONS = [
  "amber_excluded_government",
  "outside_window",
  "not_root",
  "not_permitted",
  "no_amber_client",
  "x_gate_closed",
] as const;
export const GONE_REASONS = ["not_found", "comments_disabled", "no_thread"] as const;

export const EVIDENCE_TYPES = [
  "keyword_hit",
  "container",
  "early_signal",
  "page_search",
  "web_search",
  "commoncrawl",
] as const; // ADR-0031
export type EvidenceType = (typeof EVIDENCE_TYPES)[number];

export const FOUND_VIA = [
  "feed",
  "news_sitemap",
  "homepage_diff",
  "sitemap_backfill",
  "web_search",
  "commoncrawl",
] as const; // ADR-0036, ADR-0059

export const OBSERVATION_LABELS = [
  "first_sight",
  "poll",
  "backfill",
  "refresh",
  "ops_force",
  "live_end",
] as const; // ADR-0034

// registry.decisions/v1 and source.events/v1 (ADR-0013, ADR-0014).
export const DECISION_TYPES = [
  "add",
  "update",
  "remove_client",
  "tier_change",
  "dormant",
  "promote",
  "retire",
  "push_coverage",
  "health_change",
  "queued",
  "mention_only",
  "reject",
  "review",
] as const;
export type DecisionType = (typeof DECISION_TYPES)[number];
export const EVENT_TYPES = [
  "added",
  "updated",
  "tier_change",
  "lifecycle_change",
  "health_change",
  "fallback_on",
  "fallback_off",
  "push_coverage_change",
] as const;
export type EventType = (typeof EVENT_TYPES)[number];

// The one closed reason list of registry.decisions and source.events, in the groups each type allows
// (ADR-0014, ADR-0016, ADR-0021, ADR-0069; the values no ADR names are Q8's).
export const SOURCE_HEALTH_REASONS = [
  "bot_removed",
  "privacy_mode",
  "grant_missing",
  "account_unavailable",
  "credential_revoked",
  "not_found",
  "uploads_playlist_missing",
  "query_rejected",
  "feed_gone",
  "push_gap",
  "crawl_disallowed",
] as const;
export const FLAG_REASONS = ["flag_off", "flag_on"] as const;
export const ROUTE_HEALTH_REASONS = ["empty_200_rate", "low_yield", "server", "auth"] as const;
export const PUSH_COVERAGE_REASONS = ["lease_lapsed", "subscription_failed"] as const;
export const RETIRE_REASONS = ["owner_request", "authorization_revoked", "not_found"] as const;
export const REVIEW_REASONS = [
  "age_gated",
  "not_indexed",
  "unclassified",
  "ambiguous",
  "schema_unknown",
  "grant_missing",
] as const;
export const REGISTRY_REASONS = [
  ...SOURCE_HEALTH_REASONS,
  ...FLAG_REASONS,
  ...ROUTE_HEALTH_REASONS,
  ...PUSH_COVERAGE_REASONS,
  "owner_request",
  "authorization_revoked",
  "budget_wait",
  "client_removed",
  "review_timeout",
  "amber_excluded_government",
  "age_gated",
  "not_indexed",
  "unclassified",
  "ambiguous",
  "schema_unknown",
] as const;
export type RegistryReason = (typeof REGISTRY_REASONS)[number];

// poster.profiles/v1 (ADR-0033; Q8).
export const PROFILE_STATUSES = ["resolved", "review", "unresolvable"] as const;
export const PROFILE_REVIEW_REASONS = [
  "age_gated",
  "not_indexed",
  "unclassified",
  "ambiguous",
  "schema_unknown",
  "grant_missing",
] as const;
export const PROFILE_UNRESOLVABLE_REASONS = [
  "not_found",
  "private",
  "suspended",
  "protected",
] as const;
export const REVIEW_FLAGS = ["watchlist_only", "hidden_subscriber_count", "made_for_kids"] as const;
export const COUNTRY_SIGNALS = [
  "iraqi_place",
  "platform_country_iq",
  "phone_964",
  "iq_domain",
  "outlet_link",
  "seed_list",
] as const;

// items.analysis/v1 (ADR-0023, ADR-0068; Q8).
export const ANALYSIS_FIXED_TASKS = [
  "sentiment",
  "sentiment_aspect",
  "topic_cluster",
  "entities",
  "media_fetch",
  "media_ocr",
  "media_tags",
  "media_asr",
  "media_logo",
] as const;
export const ANALYSIS_RUN_KINDS = ["live", "rerun"] as const;
export const ANALYSIS_LANES = ["priority", "standard"] as const;
export const ANALYSIS_STATUSES = ["ok", "skipped"] as const;
export const ANALYSIS_SKIP_REASONS = [
  "no_text",
  "unsupported_lang",
  "low_priority_source",
  "unsupported_media",
  "media_unavailable",
  "ai_input_refused",
  "use_not_permitted",
] as const;
export const SENTIMENT_LABELS = ["positive", "negative", "neutral", "mixed"] as const;
export const INTENT_LABELS = [
  "complaint",
  "question",
  "praise",
  "request",
  "announcement",
  "other",
] as const;
export const TOPIC_SOURCES = ["supervised", "zero_shot"] as const;
export const ENTITY_TYPES = [
  "brand",
  "company",
  "institution",
  "place",
  "product",
  "person_public",
] as const;
// An unlinked form is an organisation's, a place's or a product's, never a person's
// (analysis-entities §5.3 L67, L71): ENTITY_TYPES less person_public.
export const UNLINKED_ENTITY_TYPES = [
  "brand",
  "company",
  "institution",
  "place",
  "product",
] as const;
export const ENTITY_SOURCES = ["model", "gazetteer", "both"] as const;

// item.hits/v1 (ADR-0031).
export const HIT_STATUSES = ["active", "retracted"] as const;
export const MATCHED_BY = ["text", "source"] as const;
export const AUTHOR_TYPES = ["source", "individual"] as const;

// search.results/v1 (ADR-0037).
export const SEARCH_ENGINES = ["perplexity", "mojeek", "gdelt"] as const;

// crawl.policies/v1 (ADR-0040, ADR-0070; news-robots-checker §5.3; Q8).
export const CRAWL_STATUSES = ["allowed", "disallowed", "paywalled", "blocked"] as const;
export const ACCESS_MODES = ["direct", "headless", "proxy", "blocked"] as const;
export const ROBOTS_STATUSES = ["ok", "unavailable"] as const;
export const USAGE_SIGNAL_VALUES = ["yes", "no", "unset"] as const;
export const CRAWL_REASONS = [
  "robots_unreachable",
  "content_signal_search_no",
  "robots_disallowed",
  "rsl_prohibited",
  "rsl_payment",
  "http_402",
  "challenge",
] as const;
export const CRAWL_JOB_KINDS = ["first_check", "refresh", "recheck", "ops_force"] as const;

// news.dedup/v1 (ADR-0022, ADR-0036; Q8).
export const DEDUP_TYPES = ["verdict", "story_update"] as const;
export const DEDUP_MATCHED_BY = ["simhash", "canonical", "text_sha256", "title_sha256"] as const;

// dlq.<service>/v1 (Q5).
export const DLQ_STAGES = ["consume", "produce"] as const;
export const DLQ_ERROR_CLASSES = [
  "schema_unknown",
  "invalid",
  "producer_not_allowed",
  "attempts_exhausted",
  "query_rejected",
] as const;

// job/v1 kind fields (ADR-0011, ADR-0020, ADR-0060; comment-decay-scheduler §5.1).
export const COMMENT_PROFILES = [
  "fb_page",
  "fb_group",
  "ig_own",
  "ig_other",
  "tt",
  "x",
  "yt",
  "li_own",
  "li_other",
  "tg_own",
  "news",
] as const;
export const BACKFILL_REASONS = ["add", "client", "ops"] as const;
export const KEYWORD_HISTORY_REASONS = ["add", "client"] as const;
export const HASHTAG_EDGES = ["recent_media", "top_media"] as const;
export const RESOLVE_ORIGINS = ["discovery", "manual"] as const;
export const RECONCILIATION_REASONS = ["lease_lapsed"] as const;

// n8n.alert/v1 and n8n.card/v1 (ADR-0067, ADR-0048; Q11).
export const N8N_CHANNELS = ["email", "telegram", "slack"] as const;
// An alert may also go to a client's own webhook, which alert-evaluator posts itself (Q15; O-11).
export const ALERT_CHANNELS = [...N8N_CHANNELS, "webhook"] as const;
export const N8N_AUDIENCES = ["client", "ops", "account_manager"] as const;
export const FALLBACK_SUBJECT_KINDS = ["source", "route"] as const; // ADR-0021 L58-L61
export const ALERT_SEVERITIES = ["info", "warning", "high"] as const;
export const ALERT_RULE_TYPES = [
  "volume_spike",
  "negative_share",
  "new_high_reach_poster",
  "keyword_first_seen",
  "post_deleted_high_reach",
  "engagement_spike",
  "topic_spike",
  "entity_or_logo",
  "story",
] as const;
// The rule types a government client may receive (alert-evaluator §5.3 C; ADR-0048).
export const GOVERNMENT_ALERT_RULE_TYPES = [
  "volume_spike",
  "negative_share",
  "keyword_first_seen",
] as const;
export const CLIENT_TYPES = ["commercial", "government"] as const; // CONVENTIONS v1.1 L84
export const CARD_TYPES = ["qualifier_review", "grant_missing", "manual_url"] as const;
export const CARD_INPUT_KINDS = ["url", "text"] as const; // a manual_url card's inputs (F-47)
export const REVIEW_CARD_ACTIONS = [
  "approve_tier_1",
  "approve_tier_2",
  "approve_tier_3",
  "reject",
  "mention_only",
] as const;
// The alert names ADRs fix; `alert` stays an open snake_case name (Q11).
export const KNOWN_ALERT_NAMES = [
  "budget_80",
  "x_enterprise_required",
  "authorization_revoked",
  "registry_duplicate",
  "rotation_behind",
  "subscription_failed",
  "keyword_first_seen",
] as const;
