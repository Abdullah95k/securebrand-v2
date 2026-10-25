-- F3 · budgets (plan "Budgets"; ADR-0018, ADR-0042, ADR-0057; quota-governor §5.3, §6.2, §6.3).
-- quota-governor is the only writer of everything here but budget_config, which ops write through
-- the audited admin console.

-- One row per tag, sub-counter and period (ADR-0042 L29). sub_counter is '' for the tag row, a
-- bucket or ledger name, service:<service> or source:<source_id>. limit: 0 closed, NULL
-- count-only and never a gate on its own, a positive value a cap (plan T18).
create table public.budgets (
  budget_tag text not null check (budget_tag ~ '^[a-z][a-z0-9_]*(:[0-9a-z-]+)?$'),
  sub_counter text not null default '' check (
    sub_counter ~ '^([a-z][a-z0-9_]*|service:[a-z0-9]+(-[a-z0-9]+)*|source:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})?$'),
  -- 1970-01-01: no period opened yet; quota-governor's first reset opens the current one.
  period_start timestamptz not null,
  unit text not null check (unit ~ '^[a-z][a-z0-9_]*$'),
  currency text check (currency ~ '^[A-Z]{3}$'),
  unit_price numeric check (unit_price >= 0),
  period text not null check (period ~ '^[a-z][a-z0-9_]*$'),
  reset_rule text not null check (reset_rule in (
    'utc_day', 'billing_cycle', 'rolling_24h', 'rolling_7d', 'provider_daily_reset',
    'calendar_month', 'contract_cycle')),
  "limit" bigint check ("limit" >= 0),
  used bigint not null default 0,
  reserved bigint not null default 0,
  mode text not null default 'normal' check (mode in ('normal', 'stretch', 'exhausted')),
  exhausted_until timestamptz,
  stretch_factor numeric check (stretch_factor >= 1),
  warn_50_at timestamptz,
  warn_80_at timestamptz,
  warn_95_at timestamptz,
  provider_usage jsonb not null default '{}' check (jsonb_typeof(provider_usage) = 'object'),
  primary key (budget_tag, sub_counter, period_start),
  -- The listed tags instead of wildcards, an id placeholder never stored (ADR-0042 L33).
  constraint budgets_no_placeholder check (
    strpos(budget_tag || sub_counter, '*') = 0 and strpos(budget_tag || sub_counter, '<') = 0),
  constraint budgets_used check (used + reserved >= 0)
);

create table public.budget_reservations (
  reservation_id text primary key check (reservation_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  request_id text not null check (request_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  budget_tag text not null check (budget_tag ~ '^[a-z][a-z0-9_]*(:[0-9a-z-]+)?$'),
  sub_counter text not null default '',
  service text not null check (service ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  job_id text check (job_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  charge bigint not null check (charge >= 0),
  resource_ids text[],
  expires_at timestamptz not null,
  settled_at timestamptz,
  constraint budget_reservations_request_id unique (request_id)
);

create index budget_reservations_expires_at on public.budget_reservations (expires_at);

-- Closed periods, kept as aggregates (quota-governor §6.3).
create table public.budget_history (
  budget_tag text not null check (budget_tag ~ '^[a-z][a-z0-9_]*(:[0-9a-z-]+)?$'),
  sub_counter text not null default '',
  period_start timestamptz not null,
  period_end timestamptz not null,
  "limit" bigint check ("limit" >= 0),
  used bigint not null,
  cost numeric,
  currency text check (currency ~ '^[A-Z]{3}$'),
  closed_at timestamptz not null default now(),
  primary key (budget_tag, sub_counter, period_start)
);

-- Limits, shares, per-source caps, per-job and per-run caps, rate ceilings, allowances and the
-- family rows from which quota-governor creates per-id tags and sub-counters (ADR-0042 L31).
-- budget_tag is a tag or a family name; scope is '' for the tag itself, 'family' for a family row,
-- or the sub-counter a setting is about.
create table public.budget_config (
  budget_tag text not null check (budget_tag ~ '^[a-z][a-z0-9_]*(:[0-9a-z-]+)?$'),
  scope text not null default '' check (scope ~ '^[a-z0-9_:-]*$'),
  setting text not null check (setting ~ '^[a-z][a-z0-9_]*$'),
  value jsonb not null,
  changed_by text not null check (length(changed_by) between 1 and 256),
  changed_at timestamptz not null default now(),
  reason text not null check (reason <> ''),
  primary key (budget_tag, scope, setting)
);

-- X reads, deduplicated per resource per UTC day: posts as bare ids, users as the SDK's keyed
-- reference, so no individual's clear id is stored (ADR-0042 L32, ADR-0010).
create table public.x_read_ledger (
  utc_day date not null,
  resource_type text not null check (resource_type in ('post', 'user')),
  resource_id text not null,
  first_read_at timestamptz not null default now(),
  primary key (utc_day, resource_type, resource_id),
  constraint x_read_ledger_resource check (
    case resource_type
      when 'post' then resource_id ~ '^[0-9]+$'
      else resource_id ~ '^[0-9a-f]{64}$'
    end)
);

-- 30 unique hashtags per Instagram business account per rolling 7 days (ADR-0042 L32).
create table public.ig_hashtag_ledger (
  ig_user_id text not null check (ig_user_id ~ '^[0-9]+$'),
  hashtag_id text not null check (hashtag_id ~ '^[0-9]+$'),
  first_queried_at timestamptz not null default now(),
  primary key (ig_user_id, hashtag_id)
);

create index ig_hashtag_ledger_window on public.ig_hashtag_ledger (ig_user_id, first_queried_at);
