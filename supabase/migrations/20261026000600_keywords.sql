-- F3 · keywords (plan "Keywords"; ADR-0044, ADR-0069 (f), (i); Question 9, built with the
-- recommended values while the user's answer is pending).

create table public.keywords (
  keyword_id uuid primary key default gen_random_uuid(),
  client_id uuid not null references public.clients (client_id),
  label text not null check (label <> ''),
  -- Variants and per-script forms: {form_id, text, lang, kind, boundary} (keyword-matcher §5.3).
  forms jsonb not null check (jsonb_typeof(forms) = 'array'),
  exclusions jsonb not null default '[]' check (jsonb_typeof(exclusions) = 'array'),
  -- They narrow a search and are never matched alone (ADR-0044).
  context_terms jsonb not null default '[]' check (jsonb_typeof(context_terms) = 'array'),
  -- Government clients: reputation and service_quality only (the trigger below).
  purpose text not null check (purpose in (
    'reputation', 'service_quality', 'brand', 'campaign', 'competitor')),
  priority boolean not null default false,
  platforms text[] not null default '{}' check (platforms <@ array[
    'facebook', 'instagram', 'tiktok', 'x', 'linkedin', 'telegram', 'youtube', 'news', 'web']::text[]),
  enabled boolean not null default true,
  version integer not null default 1 check (version >= 1),
  rematch_days integer check (rematch_days >= 0),
  -- The SDK hash of the normalised forms and context terms, set on save (ADR-0044).
  query_key text check (query_key ~ '^[0-9a-f]{64}$'),
  -- The X sensitive-event screen (ADR-0069 (f)); a keyword waits until it is clear.
  screening_status text not null default 'pending'
    check (screening_status in ('pending', 'clear', 'flagged')),
  updated_at timestamptz not null default now()
);

create index keywords_client_id on public.keywords (client_id);
create index keywords_query_key on public.keywords (query_key);
create index keywords_updated_at on public.keywords (updated_at);

create trigger keywords_updated_at before update on public.keywords
  for each row execute function public.set_updated_at();

create function public.keywords_government_purpose() returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if new.purpose not in ('reputation', 'service_quality') and exists (
    select 1 from public.clients c
    where c.client_id = new.client_id and c.client_type = 'government'
  ) then
    raise exception 'a government client''s keyword is for reputation or service_quality, not %',
      new.purpose using errcode = '23514';
  end if;
  return new;
end
$$;

create trigger keywords_government_purpose before insert or update of purpose, client_id
  on public.keywords for each row execute function public.keywords_government_purpose();

-- The X blocked and sensitive-event terms (ADR-0069 (f), (i)), kept by the user's compliance owner
-- through the admin console; seeded empty.
create table public.screened_terms (
  term_id uuid primary key default gen_random_uuid(),
  term text not null check (term <> ''),
  lang text check (lang in ('ar', 'ckb', 'en')),
  category text check (category <> ''),
  added_by text not null check (length(added_by) between 1 and 256),
  added_at timestamptz not null default now(),
  enabled boolean not null default true,
  constraint screened_terms_term unique nulls not distinct (term, lang)
);
