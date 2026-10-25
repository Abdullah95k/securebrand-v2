-- F3 · backfill runs (plan "Comments and backfill"; ADR-0017, ADR-0020, ADR-0025, ADR-0064;
-- backfill-orchestrator §6.3; F2 job/v1 backfill and keyword_history).

create table public.backfill_runs (
  run_id text primary key check (run_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  source_id uuid not null references public.sources (source_id),
  service text not null check (service ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  job_kind text not null check (job_kind in ('backfill', 'keyword_history')),
  -- F2 BACKFILL_REASONS; a keyword_history run's are KEYWORD_HISTORY_REASONS.
  reason text not null check (reason in ('add', 'client', 'ops')),
  requested_by text check (length(requested_by) between 1 and 256),
  window_start timestamptz not null,
  window_end timestamptz not null,
  -- {max_age_days, max_items} as the job carries it.
  cap jsonb not null check (jsonb_typeof(cap) = 'object'),
  status text not null default 'pending' check (status in ('pending', 'running', 'done', 'capped')),
  capped_reason text check (capped_reason in (
    'route_cap', 'budget', 'deadline', 'failed', 'no_history', 'flag_off')),
  oldest_item_at timestamptz,
  started_at timestamptz,
  finished_at timestamptz,
  items_new integer not null default 0 check (items_new >= 0),
  cost_units numeric not null default 0 check (cost_units >= 0),
  attempt integer not null default 1 check (attempt >= 1),
  -- One entry per job the run waits for: {service, job_id, status}.
  jobs jsonb not null default '[]' check (jsonb_typeof(jobs) = 'array'),
  constraint backfill_runs_window check (window_start <= window_end),
  constraint backfill_runs_keyword_history_reason check (
    job_kind <> 'keyword_history' or reason in ('add', 'client')),
  constraint backfill_runs_capped check ((status = 'capped') = (capped_reason is not null))
);

create index backfill_runs_source_status on public.backfill_runs (source_id, status);
