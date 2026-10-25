-- F3 · roles and helpers (plan T1, T6, T7, T16).
--
-- admin_api: the D3 servers' role (the audited admin API, the client portal's server, the admin
-- console). NOLOGIN, so the migrations hold no password; granted to authenticator, so PostgREST can
-- switch to it on a JWT signed with the project's secret; BYPASSRLS like service_role, its reach
-- set by the grants of the privilege migration alone. Roles are cluster-wide, so a second database
-- on the same server (a test database) finds it already there.
do $$
begin
  if not exists (select 1 from pg_catalog.pg_roles where rolname = 'admin_api') then
    create role admin_api nologin noinherit bypassrls;
  end if;
  if exists (select 1 from pg_catalog.pg_roles where rolname = 'authenticator') then
    grant admin_api to authenticator;
  end if;
end
$$;

grant usage on schema public to admin_api;

-- The service-schema runner's record (plan T19): one row per service migration applied to this
-- database, written by scripts/migrate/postgres.sh, later by F4's runner. No API role reads it.
create schema svc_migrations;
revoke all on schema svc_migrations from public;

create table svc_migrations.applied (
  service text not null check (service ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  version text not null check (version ~ '^[0-9]{14}$'),
  name text not null check (name ~ '^[a-z0-9_]+$'),
  checksum text not null check (checksum ~ '^[0-9a-f]{64}$'),
  applied_at timestamptz not null default now(),
  primary key (service, version)
);

-- updated_at, set on every update by the table's own trigger.
create function public.set_updated_at() returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at := now();
  return new;
end
$$;

-- The append-only guard of the audit tables (plan T7): it refuses UPDATE, DELETE and TRUNCATE for
-- every role, the owner included. The one exception is a row DELETE inside purge_audit_rows(),
-- which sets securebrand.audit_purge for its own transaction.
create function public.forbid_change() returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if tg_op = 'DELETE' and tg_level = 'ROW'
     and current_setting('securebrand.audit_purge', true) = 'on' then
    return old;
  end if;
  raise exception '% is append-only: % is refused', tg_table_name, tg_op
    using errcode = '42501';
end
$$;

-- Leader-election lock keys (plan T6): the first eight bytes of
-- sha256('securebrand:leader:' || service), read as a signed bigint, for pg_try_advisory_lock.
-- packages/contracts/src/db/leader-lock.ts computes the same key.
create function public.leader_lock_key(service text) returns bigint
language plpgsql
immutable strict parallel safe
set search_path = ''
as $$
begin
  if service !~ '^[a-z0-9]+(-[a-z0-9]+)*$' then
    raise exception 'leader_lock_key: % is not a service name', service
      using errcode = '22023';
  end if;
  return ('x' || encode(substring(sha256(convert_to('securebrand:leader:' || service, 'UTF8'))
    from 1 for 8), 'hex'))::bit(64)::bigint;
end
$$;

-- True when every element of a text array matches a pattern (CHECKs on array columns).
create function public.all_match(elements text[], pattern text) returns boolean
language sql
immutable parallel safe
set search_path = ''
as $$
  select coalesce(bool_and(e ~ pattern), true) from unnest(elements) as e
$$;
