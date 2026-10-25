-- F3 · comments (plan "Comments and backfill"; ADR-0009, ADR-0046, ADR-0060; comment-decay-scheduler
-- §6.3; Question 4).

-- One row per service, post and comment, written only by the service the row names through the SDK
-- helper (ADR-0046): no text and no author.
create table public.comment_state (
  service text not null check (service ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  post_item_id uuid not null,
  comment_key text not null check (comment_key <> ''),
  parent_key text check (parent_key <> ''),
  content_hash text not null check (content_hash ~ '^sha256:[0-9a-f]{64}$'),
  version integer not null default 1 check (version >= 1),
  state text not null check (state in ('live', 'missing', 'deleted')),
  first_seen_at timestamptz not null,
  last_seen_at timestamptz not null,
  -- As last seen, for the reply thresholds (ADR-0060).
  reply_count integer check (reply_count >= 0),
  primary key (service, post_item_id, comment_key)
);

create index comment_state_post_item_id on public.comment_state (post_item_id);

-- comment-decay-scheduler's series, one row per post and lane (ADR-0046, ADR-0060).
create table public.comment_series (
  item_id uuid not null,
  lane text not null check (lane in ('comments', 'metrics')),
  source_id uuid not null,
  route text not null check (route in ('green', 'amber')),
  profile text not null check (profile in (
    'fb_page', 'fb_group', 'ig_own', 'ig_other', 'tt', 'x', 'yt', 'li_own', 'li_other', 'tg_own',
    'news')),
  anchor_at timestamptz not null,
  next_step text check (
    next_step ~ '^(\+[1-9][0-9]*[hd]|once|hot:[1-9][0-9]*|refresh:[0-7][0-9A-HJKMNP-TV-Z]{25})$'),
  next_due_at timestamptz,
  status text not null check (status in (
    'scheduled', 'in_flight', 'done', 'stopped_early', 'cancelled')),
  in_flight_job_id text check (in_flight_job_id ~ '^[0-7][0-9A-HJKMNP-TV-Z]{25}$'),
  last_fetched_at timestamptz,
  last_new_count integer check (last_new_count >= 0),
  last_total integer check (last_total >= 0),
  extended boolean not null default false,
  hot_count integer not null default 0 check (hot_count >= 0),
  hot_next_at timestamptz,
  hot_until timestamptz,
  primary key (item_id, lane)
);

create index comment_series_due on public.comment_series (status, next_due_at);

-- The comment series profiles of CONVENTIONS L405 to L421, generated from that table (plan T5;
-- Question 4): reference data, changed only by migration.
create table public.comment_series_profiles (
  profile text primary key check (profile in (
    'fb_page', 'fb_group', 'ig_own', 'ig_other', 'tt', 'x', 'yt', 'li_own', 'li_other', 'tg_own',
    'news')),
  route_label text not null check (route_label <> ''),
  platform text not null check (platform in (
    'facebook', 'instagram', 'tiktok', 'x', 'linkedin', 'telegram', 'youtube', 'news', 'web')),
  route text not null check (route in ('green', 'amber')),
  comment_services text[] not null check (
    cardinality(comment_services) >= 1
    and public.all_match(comment_services, '^[a-z0-9]+(-[a-z0-9]+)*$')),
  series_text text not null check (series_text <> ''),
  -- F2 seriesStep labels; empty for the push row.
  steps text[] not null check (public.all_match(steps, '^\+[1-9][0-9]*[hd]$')),
  push boolean not null default false,
  replies_text text not null check (replies_text <> ''),
  constraint comment_series_profiles_route_label unique (route_label),
  constraint comment_series_profiles_push check (push = (cardinality(steps) = 0))
);
