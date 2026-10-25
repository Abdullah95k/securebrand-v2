-- F3 · analysis and alerts (plan "Analysis and alerts"; ADR-0023, ADR-0025, ADR-0048;
-- analysis-topics §5.3, analysis-entities §5.3, analysis-media §5.3, alert-evaluator §5.3).

create table public.model_versions (
  -- F2 analysisTask: a task name holds no colon (ADR-0023).
  task text not null check (task ~ '^(sentiment|sentiment_aspect|topic_cluster|entities|media_fetch|media_ocr|media_tags|media_asr|media_logo|topics\.[A-Za-z0-9_.-]+)$'),
  model_version text not null check (model_version ~ '^[^\x01-\x20:]+$'),
  service text not null check (service ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  status text not null check (status in ('candidate', 'shadow', 'active', 'retired')),
  thresholds jsonb not null default '{}' check (jsonb_typeof(thresholds) = 'object'),
  -- Under the models/ prefix the release step writes (ADR-0039).
  artefact_path text not null check (artefact_path ~ '^models/'),
  evaluation jsonb not null default '{}' check (jsonb_typeof(evaluation) = 'object'),
  created_at timestamptz not null default now(),
  activated_at timestamptz,
  retired_at timestamptz,
  primary key (task, model_version)
);

create unique index model_versions_one_active on public.model_versions (task)
  where status = 'active';

-- taxonomy_id is global or a client's UUID in its lower-case canonical form.
create table public.taxonomy_nodes (
  taxonomy_id text not null check (taxonomy_id = 'global'
    or taxonomy_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'),
  node_id text not null check (node_id ~ '^[^\x01-\x20]+$'),
  label_ar text,
  label_ckb text,
  label_en text,
  description text,
  examples jsonb not null default '[]' check (jsonb_typeof(examples) = 'array'),
  status text not null check (status in ('zero_shot', 'supervised', 'retired')),
  taxonomy_version integer not null default 1 check (taxonomy_version >= 1),
  primary key (taxonomy_id, node_id)
);

create table public.kb_entities (
  entity_id text primary key check (entity_id ~ '^[^\x01-\x20]+$'),
  type text not null check (type in (
    'brand', 'company', 'institution', 'place', 'product', 'person_public')),
  name_ar text,
  name_ckb text,
  name_en text,
  parent_id text references public.kb_entities (entity_id),
  scope text not null check (scope = 'global'
    or scope ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'),
  status text not null check (status ~ '^[a-z][a-z0-9_]*$'),
  kb_version integer not null default 1 check (kb_version >= 1),
  -- Persons only (analysis-entities §5.3).
  public_role text,
  role_terms jsonb check (jsonb_typeof(role_terms) = 'array'),
  constraint kb_entities_person_fields check (
    type = 'person_public' or (public_role is null and role_terms is null))
);

create table public.kb_aliases (
  alias_id uuid primary key default gen_random_uuid(),
  entity_id text not null references public.kb_entities (entity_id) on delete cascade,
  text text not null check (text <> ''),
  lang text check (lang in ('ar', 'ckb', 'en', 'mixed', 'other', 'und')),
  script text check (script ~ '^[A-Za-z]{4}$'),
  folded text not null check (folded <> ''),
  kind text not null check (kind in (
    'official', 'colloquial', 'abbreviation', 'misspelling', 'transliteration')),
  ambiguous boolean not null default false,
  context_cues jsonb not null default '[]' check (jsonb_typeof(context_cues) = 'array')
);

create index kb_aliases_folded on public.kb_aliases (folded);

-- A client's brands and their logo sets, in object storage under object_prefix (analysis-media).
create table public.brand_assets (
  brand_id text primary key check (brand_id ~ '^[^\x01-\x20]+$'),
  client_id uuid not null references public.clients (client_id),
  name text not null check (name <> ''),
  object_prefix text not null check (object_prefix <> ''),
  status text not null check (status ~ '^[a-z][a-z0-9_]*$'),
  added_at timestamptz not null default now()
);

create table public.alert_rules (
  rule_id uuid primary key default gen_random_uuid(),
  client_id uuid not null references public.clients (client_id),
  type text not null check (type in (
    'volume_spike', 'negative_share', 'new_high_reach_poster', 'keyword_first_seen',
    'post_deleted_high_reach', 'engagement_spike', 'topic_spike', 'entity_or_logo', 'story')),
  keyword_id uuid references public.keywords (keyword_id),
  scope text not null check (scope in ('keyword', 'keyword_source')),
  platform text check (platform in (
    'facebook', 'instagram', 'tiktok', 'x', 'linkedin', 'telegram', 'youtube', 'news', 'web')),
  params jsonb not null default '{}' check (jsonb_typeof(params) = 'object'),
  severity text not null check (severity in ('info', 'warning', 'high')),
  channels jsonb not null default '[]' check (jsonb_typeof(channels) = 'array'),
  cooldown_minutes integer not null default 60 check (cooldown_minutes >= 0),
  enabled boolean not null default true
);

-- A government client's rule types are F2's GOVERNMENT_ALERT_RULE_TYPES (ADR-0048).
create function public.alert_rules_government_type() returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if new.type not in ('volume_spike', 'negative_share', 'keyword_first_seen') and exists (
    select 1 from public.clients c
    where c.client_id = new.client_id and c.client_type = 'government'
  ) then
    raise exception 'a government client''s alert rule is volume_spike, negative_share or keyword_first_seen, not %',
      new.type using errcode = '23514';
  end if;
  return new;
end
$$;

create trigger alert_rules_government_type before insert or update of type, client_id
  on public.alert_rules for each row execute function public.alert_rules_government_type();

-- A client that becomes a government client keeps no keyword or alert rule a government client
-- may not hold, so the two triggers above cannot be gone round by changing the client.
create function public.clients_government_rules() returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if new.client_type = 'government' and old.client_type is distinct from 'government' and (
    exists (select 1 from public.keywords k where k.client_id = new.client_id
            and k.purpose not in ('reputation', 'service_quality'))
    or exists (select 1 from public.alert_rules r where r.client_id = new.client_id
            and r.type not in ('volume_spike', 'negative_share', 'keyword_first_seen'))
  ) then
    raise exception 'client % holds keywords or alert rules a government client may not hold',
      new.client_id using errcode = '23514';
  end if;
  return new;
end
$$;

create trigger clients_government_rules before update of client_type on public.clients
  for each row execute function public.clients_government_rules();

create table public.alerts (
  alert_id text primary key check (alert_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  rule_id uuid not null references public.alert_rules (rule_id),
  client_id uuid not null references public.clients (client_id),
  fingerprint text not null check (fingerprint <> ''),
  window_key text not null check (window_key <> ''),
  status text not null default 'open' check (status in ('open', 'resolved')),
  renotify boolean not null default false,
  payload jsonb not null default '{}' check (jsonb_typeof(payload) = 'object'),
  opened_at timestamptz not null default now(),
  resolved_at timestamptz,
  cooldown_until timestamptz,
  constraint alerts_fingerprint_window unique (fingerprint, window_key)
);
