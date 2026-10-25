-- F3 · the registry (plan "Registry"; ADR-0010, ADR-0013, ADR-0014, ADR-0016, ADR-0033, ADR-0043,
-- ADR-0045, ADR-0049; F2 source-columns.ts, registry-decisions.ts, poster-profiles.ts).

create table public.sources (
  -- Pre-allocated by the sender for a client-owned property or a news site (ADR-0066, ADR-0040).
  source_id uuid primary key default gen_random_uuid(),
  platform text not null check (platform in (
    'facebook', 'instagram', 'tiktok', 'x', 'linkedin', 'telegram', 'youtube', 'news', 'web')),
  source_type text not null check (source_type in (
    'page', 'group', 'account', 'creator', 'channel', 'company_page', 'site', 'hashtag',
    'keyword_rule')),
  platform_id text check (platform_id ~ '^[^\x01-\x20]+$'),
  handle text check (handle <> ''),
  url text check (url ~ '^https?://[^\x01-\x20]+$'),
  display_name text,
  route text not null check (route in ('green', 'amber')),
  vendor text check (vendor in (
    'sociavault', 'scrapecreators', 'tikhub', 'ensembledata', 'harvestapi', 'telemetrio',
    'tugelbay', 'sovereigntaylor', 'perplexity', 'mojeek', 'gdelt')),
  tier smallint not null check (tier in (1, 2, 3)),
  lifecycle text not null default 'active' check (lifecycle in ('active', 'dormant', 'retired')),
  push_covered boolean not null default false,
  retention_class text not null check (retention_class in (
    'meta_on_request', 'vendor_agreed', 'x_24h_sync', 'news_excerpt', 'telegram_bot',
    'tiktok_display', 'linkedin_48h', 'linkedin_org', 'youtube_30d_text')),
  client_ids uuid[] not null default '{}',
  owned_by_client boolean not null default false,
  followers bigint check (followers >= 0),
  country_signals jsonb check (jsonb_typeof(country_signals) = 'object'),
  lang_share jsonb check (jsonb_typeof(lang_share) = 'object'),
  platform_meta jsonb not null default '{}' check (jsonb_typeof(platform_meta) = 'object'),
  added_by text not null check (added_by in ('qualifier', 'client', 'ops')),
  added_at timestamptz not null default now(),
  -- Operational columns, one owner each (ADR-0013): keyword-matcher; the primary poller; the
  -- primary poller; backfill-orchestrator.
  last_hit_at timestamptz,
  last_polled_at timestamptz,
  next_poll_at timestamptz,
  backfill_status text not null default 'pending'
    check (backfill_status in ('pending', 'running', 'done', 'capped')),
  health text not null default 'ok' check (health in ('ok', 'degraded', 'fallback', 'blocked')),
  health_reason text check (health_reason in (
    'bot_removed', 'privacy_mode', 'grant_missing', 'account_unavailable', 'credential_revoked',
    'not_found', 'uploads_playlist_missing', 'query_rejected', 'feed_gone', 'push_gap',
    'crawl_disallowed', 'flag_off', 'flag_on', 'empty_200_rate', 'low_yield', 'server', 'auth')),
  health_set_by text check (length(health_set_by) between 1 and 256),
  health_changed_at timestamptz,
  -- owner_request is sticky: such a source is never re-added (ADR-0069 (a), ADR-0014).
  retired_reason text check (retired_reason in ('owner_request', 'authorization_revoked', 'not_found')),
  notes text,
  constraint sources_platform_id_key unique (platform, platform_id)
);

create index sources_route_health on public.sources (platform, route, vendor);
create index sources_client_ids on public.sources using gin (client_ids);
create index sources_lifecycle on public.sources (lifecycle);

create table public.client_sources (
  client_id uuid not null references public.clients (client_id),
  source_id uuid not null references public.sources (source_id) on delete cascade,
  priority boolean not null default false,
  -- Owners apart from watchers (plan T9, ADR-0053).
  relation text not null default 'watcher' check (relation in ('owner', 'watcher')),
  added_at timestamptz not null default now(),
  added_by text not null check (length(added_by) between 1 and 256),
  primary key (client_id, source_id)
);

create index client_sources_source_id on public.client_sources (source_id);

-- Seed lists, watchlists and saved lists of public accounts (ADR-0043, ADR-0010); list_name names
-- a saved list (D3 question 12) and is empty on the others.
create table public.client_lists (
  entry_id uuid primary key default gen_random_uuid(),
  client_id uuid not null references public.clients (client_id) on delete cascade,
  list text not null check (list in ('seed', 'watch', 'saved')),
  list_name text not null default '' check (length(list_name) <= 200),
  candidate_key text check (candidate_key ~ '^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\x01-\x20:]+|linkedin:[^\x01-\x20]+)$'),
  source_id uuid references public.sources (source_id) on delete cascade,
  added_at timestamptz not null default now(),
  added_by text not null check (length(added_by) between 1 and 256),
  constraint client_lists_one_key check (num_nonnulls(candidate_key, source_id) = 1),
  constraint client_lists_named_saved check (list = 'saved' or list_name = ''),
  constraint client_lists_candidate_key unique (client_id, list, list_name, candidate_key),
  constraint client_lists_source_id unique (client_id, list, list_name, source_id)
);

create index client_lists_candidate_key_idx on public.client_lists (candidate_key);
create index client_lists_source_id_idx on public.client_lists (source_id);

-- A registry_audit before or after snapshot holds no clear identity (plan T21, S8; ADR-0069 (e)):
-- no handle, url, display_name or notes key (their sha256 hashes instead), and country_signals
-- without signal_evidence, which quotes the matched text.
create function public.audit_snapshot_ok(snapshot jsonb) returns boolean
language sql
immutable parallel safe
set search_path = ''
as $$
  select case
    when snapshot is null then true
    when jsonb_typeof(snapshot) <> 'object' then false
    else not (snapshot ?| array['handle', 'url', 'display_name', 'notes'])
      and not coalesce(
        jsonb_typeof(snapshot -> 'country_signals') = 'object'
          and (snapshot -> 'country_signals') ? 'signal_evidence', false)
      and coalesce((snapshot ->> 'handle_sha256') ~ '^[0-9a-f]{64}$', true)
      and coalesce((snapshot ->> 'url_sha256') ~ '^[0-9a-f]{64}$', true)
      and coalesce((snapshot ->> 'display_name_sha256') ~ '^[0-9a-f]{64}$', true)
  end
$$;

-- A route-level change's scope: exactly platform, route and vendor (F2 RouteHealthChange). A row
-- with no route scope passes.
create function public.is_route_scope(scope jsonb) returns boolean
language sql
immutable parallel safe
set search_path = ''
as $$
  select case
    when scope is null then true
    when jsonb_typeof(scope) <> 'object' then false
    else (select count(*) from jsonb_object_keys(scope)) = 3
      and scope ?& array['platform', 'route', 'vendor']
      and coalesce((scope ->> 'platform') in (
        'facebook', 'instagram', 'tiktok', 'x', 'linkedin', 'telegram', 'youtube', 'news', 'web'),
        false)
      and coalesce((scope ->> 'route') in ('green', 'amber'), false)
      and (jsonb_typeof(scope -> 'vendor') = 'null' or coalesce((scope ->> 'vendor') in (
        'sociavault', 'scrapecreators', 'tikhub', 'ensembledata', 'harvestapi', 'telemetrio',
        'tugelbay', 'sovereigntaylor', 'perplexity', 'mojeek', 'gdelt'), false))
  end
$$;

-- One row per applied or refused decision and source (C1; registry-writer §5.2 step 1, §13 #2):
-- the decision's subject (one of candidate_key, author_ref, keyword_id, route_scope, or source_id
-- alone), and source_id, the source the row is about, whose event's message_id it keeps.
create table public.registry_audit (
  audit_id bigint generated always as identity primary key,
  decision_id text not null check (decision_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  decision text not null check (decision in (
    'add', 'update', 'remove_client', 'tier_change', 'dormant', 'promote', 'retire',
    'push_coverage', 'health_change', 'queued', 'mention_only', 'reject', 'review')),
  -- The applied outcome: applied, rejected, no_op, or a rejection name (registry_duplicate).
  action text not null check (action ~ '^[a-z][a-z0-9_]*$' and length(action) <= 64),
  reason text check (reason in (
    'bot_removed', 'privacy_mode', 'grant_missing', 'account_unavailable', 'credential_revoked',
    'not_found', 'uploads_playlist_missing', 'query_rejected', 'feed_gone', 'push_gap',
    'crawl_disallowed', 'flag_off', 'flag_on', 'empty_200_rate', 'low_yield', 'server', 'auth',
    'lease_lapsed', 'subscription_failed', 'owner_request', 'authorization_revoked',
    'budget_wait', 'client_removed', 'review_timeout', 'amber_excluded_government', 'age_gated',
    'not_indexed', 'unclassified', 'ambiguous', 'schema_unknown')),
  candidate_key text check (candidate_key ~ '^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\x01-\x20:]+|linkedin:[^\x01-\x20]+)$'),
  author_ref text check (author_ref ~ '^[0-9a-f]{64}$'),
  keyword_id uuid,
  route_scope jsonb check (public.is_route_scope(route_scope)),
  source_id uuid,
  actor text not null check (length(actor) between 1 and 256),
  before jsonb check (public.audit_snapshot_ok(before)),
  after jsonb check (public.audit_snapshot_ok(after)),
  provenance jsonb check (jsonb_typeof(provenance) = 'object'),
  message_id text check (message_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  applied_at timestamptz not null default now(),
  constraint registry_audit_subject check (
    num_nonnulls(candidate_key, author_ref, keyword_id, route_scope) <= 1
    and (num_nonnulls(candidate_key, author_ref, keyword_id, route_scope) = 1
      or source_id is not null)),
  -- An ordinary individual's mention keeps its reference only (S2; registry-writer §9 L127).
  constraint registry_audit_author_ref_only check (
    author_ref is null
    or (source_id is null and before is null and after is null and provenance is null)),
  constraint registry_audit_decision_source unique nulls not distinct (decision_id, source_id),
  constraint registry_audit_message_id unique (message_id)
);

create index registry_audit_source_id on public.registry_audit (source_id);
create index registry_audit_keyword_id on public.registry_audit (keyword_id);

create trigger registry_audit_append_only before update or delete on public.registry_audit
  for each row execute function public.forbid_change();
create trigger registry_audit_no_truncate before truncate on public.registry_audit
  for each statement execute function public.forbid_change();

-- registry-writer's outbox, written in the decision's transaction and marked by its relay (ADR-0045).
create table public.registry_outbox (
  message_id text primary key check (message_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  decision_id text not null check (decision_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  source_id uuid not null,
  payload jsonb not null check (jsonb_typeof(payload) = 'object'),
  created_at timestamptz not null default now(),
  published_at timestamptz
);

create index registry_outbox_unpublished on public.registry_outbox (created_at)
  where published_at is null;

-- The qualifier's decisions and its outbox column (ADR-0045; qualifier §5.2 L63). One subject per
-- row, as F2 types it (C2): a candidate, an ordinary individual's reference, or a source for the
-- sweep's decisions.
create table public.decisions (
  decision_id text primary key check (decision_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  candidate_key text check (candidate_key ~ '^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\x01-\x20:]+|linkedin:[^\x01-\x20]+)$'),
  author_ref text check (author_ref ~ '^[0-9a-f]{64}$'),
  source_id uuid,
  decision text not null check (decision in (
    'add', 'update', 'remove_client', 'tier_change', 'dormant', 'promote', 'retire',
    'push_coverage', 'health_change', 'queued', 'mention_only', 'reject', 'review')),
  reason text check (reason in (
    'bot_removed', 'privacy_mode', 'grant_missing', 'account_unavailable', 'credential_revoked',
    'not_found', 'uploads_playlist_missing', 'query_rejected', 'feed_gone', 'push_gap',
    'crawl_disallowed', 'flag_off', 'flag_on', 'empty_200_rate', 'low_yield', 'server', 'auth',
    'lease_lapsed', 'subscription_failed', 'owner_request', 'authorization_revoked',
    'budget_wait', 'client_removed', 'review_timeout', 'amber_excluded_government', 'age_gated',
    'not_indexed', 'unclassified', 'ambiguous', 'schema_unknown')),
  rule_hit smallint check (rule_hit between 1 and 10),
  client_ids uuid[] not null default '{}',
  payload jsonb not null check (jsonb_typeof(payload) = 'object'),
  expires_at timestamptz,
  created_at timestamptz not null default now(),
  published_at timestamptz,
  constraint decisions_one_subject check (num_nonnulls(candidate_key, author_ref, source_id) = 1),
  constraint decisions_author_ref_minimal check (
    author_ref is null
    or not (payload ?| array['candidate_key', 'handle', 'url', 'display_name']))
);

create index decisions_candidate_key on public.decisions (candidate_key);
create index decisions_source_id on public.decisions (source_id);
create index decisions_unpublished on public.decisions (created_at) where published_at is null;

-- The one resolver cache (ADR-0045, ADR-0032), with public_account (ADR-0010). An ordinary
-- individual's row is keyed by its author_ref and holds no identity (C4, S1; ADR-0010 L47, L60);
-- resolving and pending are poster-resolver's in-flight states (C5).
create table public.poster_profiles (
  profile_id uuid primary key default gen_random_uuid(),
  platform text not null check (platform in (
    'facebook', 'instagram', 'tiktok', 'x', 'linkedin', 'telegram', 'youtube', 'news', 'web')),
  candidate_key text check (candidate_key ~ '^(facebook:group:[0-9]+|news:site:[a-z0-9-]+(\.[a-z0-9-]+)+|(facebook|instagram|tiktok|x|telegram|youtube):[^\x01-\x20:]+|linkedin:[^\x01-\x20]+)$'),
  author_ref text check (author_ref ~ '^[0-9a-f]{64}$'),
  key_form text not null check (key_form in ('id', 'handle', 'author_ref')),
  status text not null check (status in (
    'resolving', 'pending', 'resolved', 'review', 'unresolvable')),
  reason text check (reason in (
    'age_gated', 'not_indexed', 'unclassified', 'ambiguous', 'schema_unknown', 'grant_missing',
    'not_found', 'private', 'suspended', 'protected')),
  account_type text check (account_type in (
    'page', 'group', 'business', 'organization', 'channel', 'company_page', 'site', 'creator',
    'public_figure', 'individual', 'business_or_creator', 'organization_or_public_figure')),
  individual boolean,
  public_account boolean not null default false,
  followers bigint check (followers >= 0),
  verified boolean,
  profile jsonb not null default '{}' check (jsonb_typeof(profile) = 'object'),
  hits_30d integer not null default 0 check (hits_30d >= 0),
  resolved_at timestamptz,
  expires_at timestamptz,
  retention_class text check (retention_class in (
    'meta_on_request', 'vendor_agreed', 'x_24h_sync', 'news_excerpt', 'telegram_bot',
    'tiktok_display', 'linkedin_48h', 'linkedin_org', 'youtube_30d_text')),
  provenance jsonb check (jsonb_typeof(provenance) = 'object'),
  constraint poster_profiles_candidate_key unique (candidate_key),
  constraint poster_profiles_author_ref unique (author_ref),
  constraint poster_profiles_one_key check (num_nonnulls(candidate_key, author_ref) = 1),
  constraint poster_profiles_key_form check ((key_form = 'author_ref') = (author_ref is not null)),
  -- individual is true exactly when account_type is individual, and null without a type (F2).
  constraint poster_profiles_individual_flag check (
    (individual is null) = (account_type is null)
    and (individual is null or individual = (account_type = 'individual'))),
  constraint poster_profiles_ordinary_individual check (
    case when individual is true and public_account is not true
      then candidate_key is null and author_ref is not null and key_form = 'author_ref'
        and profile = '{}'::jsonb
      else author_ref is null
    end),
  constraint poster_profiles_key_platform check (
    candidate_key is null or split_part(candidate_key, ':', 1) = platform)
);

create index poster_profiles_expires_at on public.poster_profiles (expires_at);

-- The shared Instagram id map (ADR-0007; F2 keys/instagram-id-map.ts), written by the SDK helper.
create table public.instagram_id_map (
  shortcode text primary key check (shortcode ~ '^[A-Za-z0-9_-]+$'),
  graph_media_id text check (graph_media_id ~ '^[0-9]+$'),
  key text not null check (key ~ '^instagram:post:(sc:[A-Za-z0-9_-]+|[0-9]+)$'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint instagram_id_map_graph_media_id unique (graph_media_id),
  constraint instagram_id_map_key unique (key)
);

create trigger instagram_id_map_updated_at before update on public.instagram_id_map
  for each row execute function public.set_updated_at();

-- The Iraqi places and outlets reference (ADR-0033 L29; Question 5): seeded by F3, edited through
-- the admin console only (admin_api).
create table public.iq_reference (
  ref_id uuid primary key default gen_random_uuid(),
  kind text not null check (kind in ('governorate', 'city', 'outlet_domain')),
  name_ar text check (name_ar <> ''),
  name_ckb text check (name_ckb <> ''),
  name_latin text check (name_latin <> ''),
  parent_id uuid references public.iq_reference (ref_id),
  domain text check (domain ~ '^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'),
  added_by text not null check (length(added_by) between 1 and 256),
  added_at timestamptz not null default now(),
  constraint iq_reference_shape check (
    case kind
      when 'outlet_domain' then domain is not null
        and num_nonnulls(name_ar, name_ckb, name_latin, parent_id) = 0
      else domain is null and num_nonnulls(name_ar, name_ckb, name_latin) = 3
    end),
  constraint iq_reference_city_parent check ((kind = 'city') = (parent_id is not null)),
  constraint iq_reference_name unique nulls not distinct (kind, parent_id, name_latin),
  constraint iq_reference_domain unique (domain)
);

create index iq_reference_parent_id on public.iq_reference (parent_id);
