-- F3 · news (plan "News"; ADR-0022, ADR-0036, ADR-0040, ADR-0070; news-site-resolver §6.3,
-- news-robots-checker §6.3, news-article-extractor §6.3, news-dedup §6.3; F2 crawl-policies.ts).

-- Keyed by the source_id allocated with the candidate (ADR-0040); no foreign key, since the site
-- row exists before its sources row (plan T13).
create table public.news_sites (
  source_id uuid primary key,
  host text not null check (host ~ '^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'),
  status text not null default 'candidate' check (status in ('candidate', 'registered')),
  feeds jsonb not null default '[]' check (jsonb_typeof(feeds) = 'array'),
  news_sitemap text check (news_sitemap ~ '^https?://[^\x01-\x20]+$'),
  sitemaps jsonb not null default '[]' check (jsonb_typeof(sitemaps) = 'array'),
  homepage_diff boolean not null default false,
  article_url_patterns jsonb not null default '[]' check (jsonb_typeof(article_url_patterns) = 'array'),
  access_mode text not null check (access_mode in ('direct', 'headless', 'proxy', 'blocked')),
  articles_per_day_estimate numeric check (articles_per_day_estimate >= 0),
  last_article_at timestamptz,
  comments_provider text not null default 'none' check (comments_provider in ('disqus', 'none')),
  disqus_shortname text check (disqus_shortname ~ '^[A-Za-z0-9_-]+$'),
  disqus_identifier_template text check (disqus_identifier_template <> ''),
  comments_health text not null default 'ok' check (comments_health in ('ok', 'degraded')),
  resolved_at timestamptz,
  profile_version integer not null default 1 check (profile_version >= 1),
  constraint news_sites_host unique (host)
);

-- Per-host crawl permissions, written only by news-robots-checker, with crawl.policies' names
-- (ADR-0040, ADR-0070); no slot column (the gate keeps its slots in host_gate).
create table public.crawl_policies (
  host text primary key check (host ~ '^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'),
  status text not null check (status in ('allowed', 'disallowed', 'paywalled', 'blocked')),
  crawl_allowed boolean not null,
  reason text check (reason in (
    'robots_unreachable', 'content_signal_search_no', 'robots_disallowed', 'rsl_prohibited',
    'rsl_payment', 'http_402', 'challenge')),
  access_mode text not null check (access_mode in ('direct', 'headless', 'proxy', 'blocked')),
  crawl_delay_seconds integer check (crawl_delay_seconds >= 0),
  robots_status text not null check (robots_status in ('ok', 'unavailable')),
  robots_rules jsonb check (jsonb_typeof(robots_rules) = 'object'),
  -- Content-Signal directives, the hyphen as an underscore: search, ai_input, ai_train.
  usage_signals jsonb not null check (jsonb_typeof(usage_signals) = 'object'),
  rsl jsonb not null check (jsonb_typeof(rsl) = 'object'),
  payment jsonb check (jsonb_typeof(payment) = 'object'),
  checked_at timestamptz not null,
  expires_at timestamptz not null,
  policy_version integer not null check (policy_version >= 1),
  next_refresh_at timestamptz
);

-- The SDK per-host gate's slots (ADR-0040, ADR-0022), a row created on first use.
create table public.host_gate (
  host text primary key check (host ~ '^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'),
  next_slot_at timestamptz not null,
  holder text check (holder <> ''),
  spacing_seconds numeric not null check (spacing_seconds >= 0)
);

-- news-article-extractor's URL set (ADR-0036): url_hash the SDK's sha256 of the normalised URL.
create table public.news_urls (
  url_hash text primary key check (url_hash ~ '^[0-9a-f]{64}$'),
  source_id uuid not null,
  url text not null check (url ~ '^https?://[^\x01-\x20]+$'),
  found_via text not null check (found_via in (
    'feed', 'news_sitemap', 'homepage_diff', 'sitemap_backfill', 'web_search', 'commoncrawl')),
  first_seen_at timestamptz not null default now(),
  status text check (status in (
    'done', 'gone', 'not_article', 'paywalled', 'skipped_policy', 'failed',
    'duplicate_canonical')),
  canonical_url_hash text check (canonical_url_hash ~ '^[0-9a-f]{64}$'),
  fetched_at timestamptz,
  extractor text check (extractor <> ''),
  extractor_version text check (extractor_version <> '')
);

create index news_urls_canonical_url_hash on public.news_urls (canonical_url_hash);
create index news_urls_source_status on public.news_urls (source_id, status);

-- news-dedup's stories and members (news-dedup §6.3): hashes and ids only, never text.
create table public.news_stories (
  story_id text primary key check (story_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  origin_key text not null check (origin_key ~ '^news:article:[0-9a-f]{64}$'),
  origin_source_id uuid not null,
  origin_time timestamptz not null,
  cluster_size integer not null default 1 check (cluster_size >= 1),
  first_seen_at timestamptz not null default now(),
  last_member_at timestamptz not null,
  merged_into text references public.news_stories (story_id)
);

create table public.news_story_members (
  idempotency_key text primary key check (idempotency_key ~ '^news:article:[0-9a-f]{64}$'),
  story_id text not null references public.news_stories (story_id),
  source_id uuid not null,
  canonical_key text check (canonical_key ~ '^news:article:[0-9a-f]{64}$'),
  simhash bigint,
  block_1 integer,
  block_2 integer,
  block_3 integer,
  block_4 integer,
  -- Null on a member matched by its canonical URL alone (ADR-0036).
  title_sha256 text check (title_sha256 ~ '^[0-9a-f]{64}$'),
  text_sha256 text check (text_sha256 ~ '^[0-9a-f]{64}$'),
  language text check (language in ('ar', 'ckb', 'en', 'mixed', 'other', 'und')),
  origin_time timestamptz not null,
  fetched_at timestamptz not null,
  role text not null check (role in ('origin', 'member')),
  matched_by text check (matched_by in ('simhash', 'canonical', 'text_sha256', 'title_sha256')),
  hamming_distance integer check (hamming_distance between 0 and 64)
);

create index news_story_members_block_1 on public.news_story_members (block_1, fetched_at);
create index news_story_members_block_2 on public.news_story_members (block_2, fetched_at);
create index news_story_members_block_3 on public.news_story_members (block_3, fetched_at);
create index news_story_members_block_4 on public.news_story_members (block_4, fetched_at);
create index news_story_members_canonical_key on public.news_story_members (canonical_key);
create index news_story_members_text_sha256 on public.news_story_members (text_sha256);
