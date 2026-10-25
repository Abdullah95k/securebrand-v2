-- F3 · clients and access (plan "Clients and access"; ADR-0043, ADR-0050, ADR-0052; Question 1).
-- client_lists follows sources, in the registry migration, since its entries may name a source.

create table public.clients (
  client_id uuid primary key default gen_random_uuid(),
  name text not null check (name <> ''),
  status text not null default 'active' check (status in ('active', 'offboarding')),
  -- The one government marker; a missing value fails closed (ADR-0043).
  client_type text not null check (client_type in ('commercial', 'government')),
  -- Never derived from client_type (ADR-0052); always off for a government client (below).
  accepts_amber boolean not null default false,
  x_end_user_declared boolean not null default false,
  -- The flagged vendors of F2's vendors.json the client accepts (CONVENTIONS L12: Perplexity).
  accepted_flagged_vendors text[] not null default '{}'
    check (accepted_flagged_vendors <@ array['perplexity']::text[]),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint clients_government_no_amber check (not (client_type = 'government' and accepts_amber))
);

create trigger clients_updated_at before update on public.clients
  for each row execute function public.set_updated_at();

create table public.client_settings (
  client_id uuid not null references public.clients (client_id) on delete cascade,
  service text not null check (service ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  settings jsonb not null check (jsonb_typeof(settings) = 'object'),
  updated_at timestamptz not null default now(),
  primary key (client_id, service)
);

create trigger client_settings_updated_at before update on public.client_settings
  for each row execute function public.set_updated_at();

-- Portal and staff memberships (plan T17, D3 question 5): a client role or account_manager (an
-- assignment) names its client; ops, compliance_owner and admin are global and name none.
create table public.client_members (
  member_id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  client_id uuid references public.clients (client_id) on delete cascade,
  role text not null check (role in (
    'client_admin', 'client_analyst', 'client_viewer',
    'account_manager', 'ops', 'compliance_owner', 'admin')),
  added_at timestamptz not null default now(),
  added_by text not null check (length(added_by) between 1 and 256),
  constraint client_members_scope check (
    (role in ('client_admin', 'client_analyst', 'client_viewer', 'account_manager'))
      = (client_id is not null)),
  constraint client_members_unique unique nulls not distinct (user_id, client_id, role)
);

create index client_members_client_id on public.client_members (client_id);

-- The clients whose rows the calling user may read directly (plan T17, S9): the clients of its
-- client-role memberships only, so an account manager's assignment grants no direct read. A
-- definer function, since client_members is service-only, with the search path pinned.
create function public.current_client_ids() returns uuid[]
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(array_agg(distinct m.client_id), '{}'::uuid[])
  from public.client_members m
  where m.user_id = auth.uid()
    and m.role in ('client_admin', 'client_analyst', 'client_viewer')
$$;

-- The D3 servers' audit (Question 1; admin-console.md L105; ADR-0069 (e)): ids, hashes, a reason
-- and the time, never content or a clear identity. Append-only (plan T7).
create table public.admin_audit (
  audit_id bigint generated always as identity primary key,
  request_id text not null check (request_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  actor text not null check (length(actor) between 1 and 256),
  action text not null check (action ~ '^[a-z][a-z0-9_]*$' and length(action) <= 64),
  subject_ids text[] not null default '{}',
  before_hash text check (before_hash ~ '^[0-9a-f]{64}$'),
  after_hash text check (after_hash ~ '^[0-9a-f]{64}$'),
  reason text check (length(reason) <= 1000),
  at timestamptz not null default now()
);

create index admin_audit_request_id on public.admin_audit (request_id);
create index admin_audit_at on public.admin_audit (at);

create trigger admin_audit_append_only before update or delete on public.admin_audit
  for each row execute function public.forbid_change();
create trigger admin_audit_no_truncate before truncate on public.admin_audit
  for each statement execute function public.forbid_change();
