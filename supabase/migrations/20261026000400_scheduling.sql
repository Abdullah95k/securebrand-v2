-- F3 · scheduling, health, flags and credentials (plan "Scheduling, health, flags and credentials";
-- ADR-0015, ADR-0016, ADR-0021, ADR-0041, ADR-0045, ADR-0050, ADR-0051, ADR-0052).

-- Per service x source x scope rows (ADR-0041): source_id null for service-level rows, scope_key
-- empty for the plain per-source row.
create table public.cursors (
  cursor_id bigint generated always as identity primary key,
  service text not null check (service ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  source_id uuid references public.sources (source_id) on delete cascade,
  scope_key text not null default '',
  cursor text,
  next_due_at timestamptz,
  last_started_at timestamptz,
  last_success_at timestamptz,
  last_error text,
  consecutive_errors integer not null default 0 check (consecutive_errors >= 0),
  state jsonb not null default '{}' check (jsonb_typeof(state) = 'object'),
  updated_at timestamptz not null default now(),
  constraint cursors_key unique nulls not distinct (service, source_id, scope_key)
);

create index cursors_next_due_at on public.cursors (service, next_due_at);
create index cursors_last_started_at on public.cursors (service, last_started_at);

create trigger cursors_updated_at before update on public.cursors
  for each row execute function public.set_updated_at();

create table public.service_runs (
  service text not null check (service ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  instance text not null check (instance <> ''),
  status text not null check (status in ('ok', 'degraded', 'down')),
  last_run_at timestamptz,
  last_success_at timestamptz,
  lag_seconds integer check (lag_seconds >= 0),
  error_count integer not null default 0 check (error_count >= 0),
  last_error text,
  state jsonb not null default '{}' check (jsonb_typeof(state) = 'object'),
  updated_at timestamptz not null default now(),
  primary key (service, instance)
);

create trigger service_runs_updated_at before update on public.service_runs
  for each row execute function public.set_updated_at();

-- Each service owns and closes its kinds; a deadline only where a kind sets one (ADR-0045).
create table public.review_queue (
  review_id text primary key check (review_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  kind text not null check (kind ~ '^[a-z][a-z0-9_]*$'),
  service text not null check (service ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  subject_key text not null check (subject_key <> ''),
  status text not null default 'open' check (status in ('open', 'answered', 'expired', 'closed')),
  opened_at timestamptz not null default now(),
  deadline_at timestamptz,
  reviewer text check (length(reviewer) between 1 and 256),
  answer jsonb,
  payload jsonb not null default '{}' check (jsonb_typeof(payload) = 'object'),
  closed_at timestamptz
);

create unique index review_queue_open_subject on public.review_queue (service, kind, subject_key)
  where status = 'open';
create index review_queue_deadline on public.review_queue (status, deadline_at);

-- Flags, the vendor override, X_PLAN and the follower threshold (ADR-0050, ADR-0051, ADR-0010;
-- plan T10, S12): the closed list of names, each vendor flag's values per CONVENTIONS L430.
create table public.feature_flags (
  name text not null check (name in (
    'FB_VENDOR_ROUTE', 'IG_VENDOR_ROUTE', 'TT_VENDOR_ROUTE', 'LI_VENDOR_ROUTE',
    'TG_VENDOR_ROUTE', 'TG_POSTS_ACTOR', 'X_PLAN', 'PUBLIC_ACCOUNT_FOLLOWER_THRESHOLD')),
  scope text not null default '',
  value text,
  changed_by text not null check (length(changed_by) between 1 and 256),
  changed_at timestamptz not null default now(),
  reason text not null check (reason <> ''),
  primary key (name, scope),
  -- The one override ADR-0051 allows: fb-keyword-search's vendor.
  constraint feature_flags_scope check (
    scope = '' or (name = 'FB_VENDOR_ROUTE' and scope = 'fb-keyword-search')),
  constraint feature_flags_value check (
    case name
      when 'FB_VENDOR_ROUTE' then coalesce(value in ('off', 'scrapecreators', 'sociavault'), false)
      when 'IG_VENDOR_ROUTE' then coalesce(value in ('off', 'sociavault'), false)
      when 'TT_VENDOR_ROUTE' then coalesce(value in ('off', 'ensembledata', 'tikhub'), false)
      when 'LI_VENDOR_ROUTE' then coalesce(value in ('off', 'harvestapi'), false)
      when 'TG_VENDOR_ROUTE' then coalesce(value in ('off', 'telemetrio'), false)
      when 'TG_POSTS_ACTOR' then coalesce(value in ('off', 'tugelbay', 'sovereigntaylor'), false)
      when 'X_PLAN' then coalesce(value in ('pay_per_use', 'enterprise'), false)
      -- NULL is unset: the follower test then admits no account (ADR-0010 L58).
      when 'PUBLIC_ACCOUNT_FOLLOWER_THRESHOLD' then value is null or value ~ '^[1-9][0-9]*$'
      else false
    end)
);

-- Every client token, company-app key and vendor key (ADR-0016), read and written only through
-- the SDK's credential client; vault_ref points into Supabase Vault and is never a secret.
create table public.credentials (
  credential_id uuid primary key default gen_random_uuid(),
  owner_kind text not null check (owner_kind in ('client', 'app', 'vendor')),
  client_id uuid references public.clients (client_id),
  owner_name text check (owner_name ~ '^[a-z0-9]+([_-][a-z0-9]+)*$'),
  platform text check (platform in (
    'facebook', 'instagram', 'tiktok', 'x', 'linkedin', 'telegram', 'youtube', 'news', 'web')),
  role text check (role ~ '^[a-z][a-z0-9_]*$'),
  fallback_rank smallint check (fallback_rank >= 1),
  scope text not null default '',
  vault_ref text check (vault_ref <> ''),
  state text not null default 'ok' check (state in ('ok', 'degraded', 'revoked')),
  reason text check (reason ~ '^[a-z][a-z0-9_]*$'),
  changed_at timestamptz not null default now(),
  plan text,
  constraint credentials_client check ((client_id is not null) = (owner_kind = 'client')),
  -- A vendor row names a vendor of F2's vendors.json, its role and its place in the role's
  -- fallback order (ADR-0051 (b)).
  constraint credentials_vendor check (
    owner_kind <> 'vendor'
    or (coalesce(owner_name in (
          'sociavault', 'scrapecreators', 'tikhub', 'ensembledata', 'harvestapi', 'telemetrio',
          'tugelbay', 'sovereigntaylor', 'perplexity', 'mojeek', 'gdelt'), false)
        and role is not null and fallback_rank is not null)),
  -- A vendor whose owner is not yet verified is never healthy (S13; ADR-0051 (e)).
  constraint credentials_owner_not_verified check (
    reason is distinct from 'owner_not_verified' or state = 'degraded'),
  constraint credentials_owner unique nulls not distinct (
    owner_kind, client_id, owner_name, platform, role, scope)
);

create unique index credentials_vendor_rank on public.credentials (role, fallback_rank)
  where owner_kind = 'vendor';

-- The canary's targets and the alternate declarations of ADR-0021 and ADR-0052 (d).
create table public.canary_targets (
  target_id text primary key check (target_id ~ '^[a-z0-9][a-z0-9_:.-]*$'),
  platform text not null check (platform in (
    'facebook', 'instagram', 'tiktok', 'x', 'linkedin', 'telegram', 'youtube', 'news', 'web')),
  route text not null check (route in ('green', 'amber')),
  vendor text check (vendor in (
    'sociavault', 'scrapecreators', 'tikhub', 'ensembledata', 'harvestapi', 'telemetrio',
    'tugelbay', 'sovereigntaylor', 'perplexity', 'mojeek', 'gdelt')),
  service text not null check (service ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  source_id uuid,
  source_type text check (source_type in (
    'page', 'group', 'account', 'creator', 'channel', 'company_page', 'site', 'hashtag',
    'keyword_rule')),
  call_params jsonb not null default '{}' check (jsonb_typeof(call_params) = 'object'),
  expect_min_items integer check (expect_min_items >= 0),
  alternate_route text check (alternate_route in ('green', 'amber')),
  alternate_vendor text check (alternate_vendor in (
    'sociavault', 'scrapecreators', 'tikhub', 'ensembledata', 'harvestapi', 'telemetrio',
    'tugelbay', 'sovereigntaylor', 'perplexity', 'mojeek', 'gdelt')),
  flag_name text check (flag_name in (
    'FB_VENDOR_ROUTE', 'IG_VENDOR_ROUTE', 'TT_VENDOR_ROUTE', 'LI_VENDOR_ROUTE',
    'TG_VENDOR_ROUTE', 'TG_POSTS_ACTOR')),
  scope text check (scope in ('non_government')),
  active boolean not null default true,
  quarantined_at timestamptz,
  last_ok_at timestamptz
);

-- The canary's trail: one record per fetch and per decision (ADR-0045). Append-only.
create table public.canary_audit (
  audit_id bigint generated always as identity primary key,
  record text not null check (record in ('fetch', 'decision')),
  target_id text,
  decision_id text check (decision_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  platform text not null check (platform in (
    'facebook', 'instagram', 'tiktok', 'x', 'linkedin', 'telegram', 'youtube', 'news', 'web')),
  route text not null check (route in ('green', 'amber')),
  vendor text check (vendor in (
    'sociavault', 'scrapecreators', 'tikhub', 'ensembledata', 'harvestapi', 'telemetrio',
    'tugelbay', 'sovereigntaylor', 'perplexity', 'mojeek', 'gdelt')),
  class text check (class in (
    'ok', 'empty_200', 'low_yield', 'throttled', 'auth', 'server', 'schema_unknown')),
  http integer check (http between 100 and 599),
  items integer check (items >= 0),
  latency_ms integer check (latency_ms >= 0),
  health text check (health in ('ok', 'degraded', 'fallback', 'blocked')),
  reason text check (reason in ('empty_200_rate', 'low_yield', 'server', 'auth', 'flag_off', 'flag_on')),
  evidence jsonb check (jsonb_typeof(evidence) = 'object'),
  at timestamptz not null default now(),
  constraint canary_audit_decision_id unique (decision_id)
);

create index canary_audit_at on public.canary_audit (at);

create trigger canary_audit_append_only before update or delete on public.canary_audit
  for each row execute function public.forbid_change();
create trigger canary_audit_no_truncate before truncate on public.canary_audit
  for each statement execute function public.forbid_change();
