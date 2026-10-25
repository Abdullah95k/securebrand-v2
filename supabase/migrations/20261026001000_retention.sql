-- F3 · retention, deletion and permitted uses (plan "Retention, deletion and permitted uses";
-- ADR-0035, ADR-0045, ADR-0054 to ADR-0056, ADR-0068, ADR-0069; retention-purger §5.3, §6.2;
-- deletion-propagator §5.3, §6.2; x-compliance-sync §6.2, §9).

-- The class clocks, one row per class and part (ADR-0045 L36; C8, S5): reference data, seeded by
-- F3 and changed only by reviewed migration (CONVENTIONS L63; S4). A clock purges with purge_text
-- or purge_derived, never with delete, which recomputes the aggregates (plan T20).
create table public.retention_classes (
  class text not null check (class in (
    'meta_on_request', 'vendor_agreed', 'x_24h_sync', 'news_excerpt', 'telegram_bot',
    'tiktok_display', 'linkedin_48h', 'linkedin_org', 'youtube_30d_text')),
  part text not null check (part in ('text', 'row', 'raw', 'derived', 'cache')),
  -- '' for the class's own clock, or a vendor whose contract sets another (none seeded).
  vendor text not null default '' check (vendor = '' or vendor in (
    'sociavault', 'scrapecreators', 'tikhub', 'ensembledata', 'harvestapi', 'telemetrio',
    'tugelbay', 'sovereigntaylor', 'perplexity', 'mojeek', 'gdelt')),
  anchor text not null check (anchor in ('created_at', 'fetched_at', 'signal_at', 'event')),
  clock interval,
  -- F2 DELETION_MODES, plus none for a part nothing purges by time (C3).
  mode text not null check (mode in ('delete', 'purge_text', 'purge_derived', 'withhold', 'none')),
  executor text not null check (executor ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  note text not null check (note <> ''),
  primary key (class, part, vendor),
  constraint retention_classes_clock check ((anchor = 'event') = (clock is null))
);

-- store-writer's TTLs, derived from the text and row clocks (ADR-0045 L36).
create view public.retention_ttls with (security_invoker = true) as
select c.class,
       c.vendor,
       t.clock as content_ttl,
       t.anchor as content_anchor,
       r.clock as row_ttl,
       r.anchor as row_anchor
from (select distinct class, vendor from public.retention_classes) c
left join public.retention_classes t
  on t.class = c.class and t.vendor = c.vendor and t.part = 'text'
left join public.retention_classes r
  on r.class = c.class and r.vendor = c.vendor and r.part = 'row';

-- One shape for every purger's runs (ADR-0045 L40): retention-purger's columns plus executor,
-- parent_run_id, trigger, refreshed, text_deleted, derived_deleted, failures, refresh_missed.
-- Append-only.
create table public.retention_audit (
  run_id text primary key check (run_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  parent_run_id text check (parent_run_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  executor text not null check (executor ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  trigger text not null check (trigger ~ '^[a-z][a-z0-9_]*$'),
  class text check (class in (
    'meta_on_request', 'vendor_agreed', 'x_24h_sync', 'news_excerpt', 'telegram_bot',
    'tiktok_display', 'linkedin_48h', 'linkedin_org', 'youtube_30d_text')),
  clock interval,
  cutoff timestamptz,
  started_at timestamptz not null,
  finished_at timestamptz,
  candidates integer not null default 0 check (candidates >= 0),
  emitted integer not null default 0 check (emitted >= 0),
  completed integer not null default 0 check (completed >= 0),
  refreshed integer not null default 0 check (refreshed >= 0),
  text_deleted integer not null default 0 check (text_deleted >= 0),
  derived_deleted integer not null default 0 check (derived_deleted >= 0),
  refresh_missed integer not null default 0 check (refresh_missed >= 0),
  failures jsonb not null default '[]' check (jsonb_typeof(failures) = 'array'),
  delegated_to text check (delegated_to ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  verification jsonb check (jsonb_typeof(verification) in ('object', 'array')),
  oldest_remaining_age_seconds bigint check (oldest_remaining_age_seconds >= 0),
  status text not null check (status in ('pass', 'fail')),
  holds jsonb not null default '[]' check (jsonb_typeof(holds) = 'array')
);

create trigger retention_audit_append_only before update or delete on public.retention_audit
  for each row execute function public.forbid_change();
create trigger retention_audit_no_truncate before truncate on public.retention_audit
  for each statement execute function public.forbid_change();

-- People's deletion requests only (ADR-0035, ADR-0069 (b)): the handle is erased once hashed.
create table public.deletion_requests (
  request_id text primary key check (request_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  received_at timestamptz not null default now(),
  requester_contact text not null check (requester_contact <> ''),
  subject_handle text check (subject_handle <> ''),
  author_ref text check (author_ref ~ '^[0-9a-f]{64}$'),
  confirmation jsonb check (jsonb_typeof(confirmation) = 'object'),
  status text not null default 'received' check (status in (
    'received', 'confirmed', 'hashed', 'emitted', 'completed', 'rejected')),
  deletion_ids text[] not null default '{}' check (public.all_match(deletion_ids,
    '^del:(platform_sync|retention|author_request|client_offboarding|legal|authorization_revoked|client_request):(item|author|source|client):[0-9a-f]{64}$')),
  updated_at timestamptz not null default now(),
  constraint deletion_requests_handle_or_ref check (subject_handle is null or author_ref is null)
);

create trigger deletion_requests_updated_at before update on public.deletion_requests
  for each row execute function public.set_updated_at();

-- The propagation of one deletions message, keyed by its deletion_id (plan T8; ADR-0035 L30).
create table public.deletion_propagations (
  deletion_id text primary key check (deletion_id ~ '^del:(platform_sync|retention|author_request|client_offboarding|legal|authorization_revoked|client_request):(item|author|source|client):[0-9a-f]{64}$'),
  reason text not null check (reason in (
    'platform_sync', 'retention', 'author_request', 'client_offboarding', 'legal',
    'authorization_revoked', 'client_request')),
  scope text not null check (scope in ('item', 'author', 'source', 'client')),
  mode text not null check (mode in ('delete', 'purge_text', 'purge_derived', 'withhold')),
  retention_class text check (retention_class in (
    'meta_on_request', 'vendor_agreed', 'x_24h_sync', 'news_excerpt', 'telegram_bot',
    'tiktok_display', 'linkedin_48h', 'linkedin_org', 'youtube_30d_text')),
  signal_at timestamptz not null,
  due_at timestamptz not null,
  state text not null default 'received' check (state in (
    'received', 'resolved', 'hidden', 'erased', 'recomputed', 'notified', 'verified',
    'completed', 'rejected')),
  items_resolved integer not null default 0 check (items_resolved >= 0),
  found integer not null default 0 check (found >= 0),
  verification jsonb check (jsonb_typeof(verification) in ('object', 'array')),
  notices jsonb not null default '[]' check (jsonb_typeof(notices) = 'array'),
  sla_met boolean,
  completed_at timestamptz,
  reject_reason text check (reject_reason ~ '^[a-z][a-z0-9_]*$'),
  -- Only an item-scope deletion carries a retention class (ADR-0035 L24, ADR-0003).
  constraint deletion_propagations_class check (scope = 'item' or retention_class is null)
);

create index deletion_propagations_state_due on public.deletion_propagations (state, due_at);

create table public.deletion_propagation_items (
  deletion_id text not null references public.deletion_propagations (deletion_id) on delete cascade,
  item_id uuid not null,
  source_id uuid,
  raw_ref text check (raw_ref ~ '^raw/(green|amber)/(facebook|instagram|tiktok|x|linkedin|telegram|youtube|news|web)/[0-9]{4}/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/[a-z0-9]+(-[a-z0-9]+)*/[0-9]{6}\.jsonl\.zst#[0-9]+$'),
  resolved_at timestamptz not null default now(),
  primary key (deletion_id, item_id)
);

-- raw-archiver's replay filter reads by item.
create index deletion_propagation_items_item_id on public.deletion_propagation_items (item_id);

-- The register of permitted uses (ADR-0068): a missing row means allowed, so only the seed keeps
-- an excluded use out.
create table public.permitted_uses (
  subject_kind text not null check (subject_kind in ('platform', 'vendor', 'news_host')),
  subject text not null,
  use text not null check (use in ('train', 'download_image', 'download_audio', 'download_video')),
  allowed boolean not null default true,
  clause text not null check (clause <> ''),
  set_by text not null check (length(set_by) between 1 and 256),
  set_at timestamptz not null default now(),
  primary key (subject_kind, subject, use),
  constraint permitted_uses_subject check (
    case subject_kind
      when 'platform' then subject in (
        'facebook', 'instagram', 'tiktok', 'x', 'linkedin', 'telegram', 'youtube', 'news', 'web',
        'disqus')
      when 'vendor' then subject in (
        'sociavault', 'scrapecreators', 'tikhub', 'ensembledata', 'harvestapi', 'telemetrio',
        'tugelbay', 'sovereigntaylor', 'perplexity', 'mojeek', 'gdelt')
      else subject ~ '^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'
    end)
);

-- Whether a use is permitted for a subject (ADR-0068): true for a missing row. An unknown kind or
-- use, or a subject outside its closed list (a mistyped or wrongly cased platform), is an error, so
-- a typo never reads as "allowed" (S14).
create function public.use_permitted(kind text, subject text, use text) returns boolean
language plpgsql
stable
set search_path = ''
as $$
declare
  found_allowed boolean;
begin
  if kind is null or kind not in ('platform', 'vendor', 'news_host') then
    raise exception 'use_permitted: % is not a subject kind', coalesce(kind, 'null')
      using errcode = '22023';
  end if;
  if use is null or use not in ('train', 'download_image', 'download_audio', 'download_video') then
    raise exception 'use_permitted: % is not a use', coalesce(use, 'null') using errcode = '22023';
  end if;
  if subject is null or not (case kind
      when 'platform' then subject in (
        'facebook', 'instagram', 'tiktok', 'x', 'linkedin', 'telegram', 'youtube', 'news', 'web',
        'disqus')
      when 'vendor' then subject in (
        'sociavault', 'scrapecreators', 'tikhub', 'ensembledata', 'harvestapi', 'telemetrio',
        'tugelbay', 'sovereigntaylor', 'perplexity', 'mojeek', 'gdelt')
      else subject ~ '^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'
    end) then
    raise exception 'use_permitted: % is not a known % subject', coalesce(subject, 'null'), kind
      using errcode = '22023';
  end if;
  select p.allowed into found_allowed
  from public.permitted_uses p
  where p.subject_kind = kind and p.subject = use_permitted.subject and p.use = use_permitted.use;
  return coalesce(found_allowed, true);
end
$$;

-- x-compliance-sync's runs (x-compliance-sync §6.2, §9): ids and statuses only. Append-only.
create table public.x_compliance_audit (
  run_id text primary key check (run_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  trigger text not null check (trigger in ('daily', 'ops_force')),
  started_at timestamptz not null,
  finished_at timestamptz,
  x_jobs jsonb not null default '[]' check (jsonb_typeof(x_jobs) = 'array'),
  ids_submitted jsonb not null default '{}' check (jsonb_typeof(ids_submitted) = 'object'),
  ids_returned jsonb not null default '{}' check (jsonb_typeof(ids_returned) = 'object'),
  withheld_in_iq integer not null default 0 check (withheld_in_iq >= 0),
  class_mismatch integer not null default 0 check (class_mismatch >= 0),
  ids_actioned integer not null default 0 check (ids_actioned >= 0),
  ids_completed integer not null default 0 check (ids_completed >= 0),
  signal_to_deleted_seconds jsonb check (jsonb_typeof(signal_to_deleted_seconds) = 'object'),
  evidence jsonb not null default '[]' check (jsonb_typeof(evidence) = 'array'),
  status text not null check (status in ('pass', 'fail'))
);

create trigger x_compliance_audit_append_only before update or delete on public.x_compliance_audit
  for each row execute function public.forbid_change();
create trigger x_compliance_audit_no_truncate before truncate on public.x_compliance_audit
  for each statement execute function public.forbid_change();

-- The one sanctioned delete path of the append-only audit tables (plan T7, S8): retention-purger's
-- contract-end retention and deletion-propagator's erasure delete the named rows, and only when
-- `evidence` names a recorded retention run or deletion. A definer function with the search path
-- pinned; only service_role may execute it.
create function public.purge_audit_rows(audit_table text, ids text[], evidence text)
returns integer
language plpgsql
security definer
set search_path = ''
as $$
declare
  removed integer;
begin
  if evidence is null or not (
    exists (select 1 from public.retention_audit r where r.run_id = evidence)
    or exists (select 1 from public.deletion_propagations d where d.deletion_id = evidence)
  ) then
    raise exception 'purge_audit_rows: % names no recorded retention run or deletion',
      coalesce(evidence, 'null') using errcode = '42501';
  end if;
  perform set_config('securebrand.audit_purge', 'on', true);
  case audit_table
    when 'registry_audit' then
      delete from public.registry_audit a where a.audit_id::text = any (ids);
    when 'canary_audit' then
      delete from public.canary_audit a where a.audit_id::text = any (ids);
    when 'admin_audit' then
      delete from public.admin_audit a where a.audit_id::text = any (ids);
    when 'retention_audit' then
      delete from public.retention_audit a where a.run_id = any (ids);
    when 'x_compliance_audit' then
      delete from public.x_compliance_audit a where a.run_id = any (ids);
    else
      raise exception 'purge_audit_rows: % is not an audit table', coalesce(audit_table, 'null')
        using errcode = '22023';
  end case;
  get diagnostics removed = row_count;
  perform set_config('securebrand.audit_purge', 'off', true);
  return removed;
end
$$;
