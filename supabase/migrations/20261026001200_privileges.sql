-- F3 · row-level security, the read policies and the privilege matrix (plan T7, T16, T17; S4, S9,
-- S10; Questions 1 and 2). The plan's "Privilege matrix" table is the specification and
-- supabase/tests/fixtures/expected-privileges.json its test.
--
-- Every grant is explicit, after a revoke of everything, so a database built with CREATE DATABASE
-- (the tests' fresh one) and the stack's Supabase database, whose default ACLs give the API roles
-- every privilege on new objects in public, end with the same privileges.

-- 1. Nothing by default.
revoke all on all tables in schema public from anon, authenticated, service_role, admin_api;
revoke all on all sequences in schema public from anon, authenticated, service_role, admin_api;
revoke all on all functions in schema public from public, anon, authenticated, service_role, admin_api;

-- A table, sequence or function a later migration creates gets no privilege until that migration
-- grants it: Supabase's default ACLs in public are taken back, and a new function is no longer
-- executable by PUBLIC (granted per function instead, T16).
alter default privileges for role postgres in schema public
  revoke all on tables from anon, authenticated, service_role;
alter default privileges for role postgres in schema public
  revoke all on sequences from anon, authenticated, service_role;
alter default privileges for role postgres in schema public
  revoke all on functions from anon, authenticated, service_role;
alter default privileges for role postgres revoke execute on functions from public;

-- 2. Row-level security on every table in public (A5). service_role and admin_api bypass it; a
-- client user (authenticated) reads only what the policies below allow; anon reads nothing.
alter table public.clients enable row level security;
alter table public.client_settings enable row level security;
alter table public.client_members enable row level security;
alter table public.admin_audit enable row level security;
alter table public.sources enable row level security;
alter table public.client_sources enable row level security;
alter table public.client_lists enable row level security;
alter table public.registry_audit enable row level security;
alter table public.registry_outbox enable row level security;
alter table public.decisions enable row level security;
alter table public.poster_profiles enable row level security;
alter table public.instagram_id_map enable row level security;
alter table public.iq_reference enable row level security;
alter table public.cursors enable row level security;
alter table public.service_runs enable row level security;
alter table public.review_queue enable row level security;
alter table public.feature_flags enable row level security;
alter table public.credentials enable row level security;
alter table public.canary_targets enable row level security;
alter table public.canary_audit enable row level security;
alter table public.budgets enable row level security;
alter table public.budget_reservations enable row level security;
alter table public.budget_history enable row level security;
alter table public.budget_config enable row level security;
alter table public.x_read_ledger enable row level security;
alter table public.ig_hashtag_ledger enable row level security;
alter table public.keywords enable row level security;
alter table public.screened_terms enable row level security;
alter table public.comment_state enable row level security;
alter table public.comment_series enable row level security;
alter table public.comment_series_profiles enable row level security;
alter table public.backfill_runs enable row level security;
alter table public.news_sites enable row level security;
alter table public.crawl_policies enable row level security;
alter table public.host_gate enable row level security;
alter table public.news_urls enable row level security;
alter table public.news_stories enable row level security;
alter table public.news_story_members enable row level security;
alter table public.retention_classes enable row level security;
alter table public.retention_audit enable row level security;
alter table public.deletion_requests enable row level security;
alter table public.deletion_propagations enable row level security;
alter table public.deletion_propagation_items enable row level security;
alter table public.permitted_uses enable row level security;
alter table public.x_compliance_audit enable row level security;
alter table public.model_versions enable row level security;
alter table public.taxonomy_nodes enable row level security;
alter table public.kb_entities enable row level security;
alter table public.kb_aliases enable row level security;
alter table public.brand_assets enable row level security;
alter table public.alert_rules enable row level security;
alter table public.alerts enable row level security;

-- 3. The client-facing tables (class C): read-only for a client user, limited to the clients of
-- its client-role memberships (current_client_ids(), T17), and to the global rows of the
-- knowledge tables. The function is called once per statement, not per row.
create policy clients_client_read on public.clients for select to authenticated
  using (client_id = any ((select public.current_client_ids())::uuid[]));
create policy client_settings_client_read on public.client_settings for select to authenticated
  using (client_id = any ((select public.current_client_ids())::uuid[]));
create policy client_lists_client_read on public.client_lists for select to authenticated
  using (client_id = any ((select public.current_client_ids())::uuid[]));
create policy keywords_client_read on public.keywords for select to authenticated
  using (client_id = any ((select public.current_client_ids())::uuid[]));
create policy brand_assets_client_read on public.brand_assets for select to authenticated
  using (client_id = any ((select public.current_client_ids())::uuid[]));
create policy alert_rules_client_read on public.alert_rules for select to authenticated
  using (client_id = any ((select public.current_client_ids())::uuid[]));
create policy alerts_client_read on public.alerts for select to authenticated
  using (client_id = any ((select public.current_client_ids())::uuid[]));
create policy client_sources_client_read on public.client_sources for select to authenticated
  using (client_id = any ((select public.current_client_ids())::uuid[]));
create policy taxonomy_nodes_client_read on public.taxonomy_nodes for select to authenticated
  using (taxonomy_id = 'global'
    or taxonomy_id = any ((select public.current_client_ids())::text[]));
create policy kb_entities_client_read on public.kb_entities for select to authenticated
  using (scope = 'global' or scope = any ((select public.current_client_ids())::text[]));
-- A source the client follows (client_sources), never by sources.client_ids, which the client
-- may not read (C12).
create policy sources_client_read on public.sources for select to authenticated
  using (exists (
    select 1 from public.client_sources cs
    where cs.source_id = sources.source_id
      and cs.client_id = any ((select public.current_client_ids())::uuid[])));

-- 4. The privilege matrix (T16). No role holds TRUNCATE, REFERENCES or TRIGGER.

-- C, admin-written: the client portal and the admin console write through admin_api;
-- deletion-propagator removes client_lists entries (the purge registry, ADR-0043).
grant select on public.clients, public.client_settings, public.client_lists, public.keywords,
  public.taxonomy_nodes, public.kb_entities, public.brand_assets, public.alert_rules
  to authenticated, service_role;
grant select, insert, update, delete on public.clients, public.client_settings,
  public.client_lists, public.keywords, public.taxonomy_nodes, public.kb_entities,
  public.brand_assets, public.alert_rules
  to admin_api;
grant delete on public.client_lists to service_role;

-- C, service-written. A client user reads sources without client_ids, notes, health_set_by,
-- platform_meta and country_signals (C12, S3).
grant select on public.client_sources, public.alerts to authenticated;
grant select (source_id, platform, source_type, platform_id, handle, url, display_name, route,
  vendor, tier, lifecycle, push_covered, retention_class, owned_by_client, followers, lang_share,
  added_by, added_at, last_hit_at, last_polled_at, next_poll_at, backfill_status, health,
  health_reason, health_changed_at, retired_reason)
  on public.sources to authenticated;
grant select, insert, update, delete on public.sources, public.client_sources, public.alerts
  to service_role;
grant select on public.sources, public.client_sources, public.alerts to admin_api;

-- S, service-written.
grant select, insert, update, delete on public.registry_outbox, public.decisions,
  public.poster_profiles, public.instagram_id_map, public.cursors, public.service_runs,
  public.review_queue, public.canary_targets, public.budgets, public.budget_reservations,
  public.budget_history, public.x_read_ledger, public.ig_hashtag_ledger, public.comment_state,
  public.comment_series, public.backfill_runs, public.news_sites, public.crawl_policies,
  public.host_gate, public.news_urls, public.news_stories, public.news_story_members,
  public.deletion_requests, public.deletion_propagations, public.deletion_propagation_items,
  public.model_versions
  to service_role;
grant select on public.registry_outbox, public.decisions, public.poster_profiles,
  public.instagram_id_map, public.cursors, public.service_runs, public.review_queue,
  public.canary_targets, public.budgets, public.budget_reservations, public.budget_history,
  public.x_read_ledger, public.ig_hashtag_ledger, public.comment_state, public.comment_series,
  public.backfill_runs, public.news_sites, public.crawl_policies, public.host_gate,
  public.news_urls, public.news_stories, public.news_story_members, public.deletion_requests,
  public.deletion_propagations, public.deletion_propagation_items, public.model_versions
  to admin_api;

-- S, admin-written: the audited admin API, never a service (Question 2).
grant select on public.client_members, public.feature_flags, public.budget_config,
  public.screened_terms, public.permitted_uses, public.iq_reference, public.kb_aliases
  to service_role;
grant select, insert, update, delete on public.client_members, public.feature_flags,
  public.budget_config, public.screened_terms, public.permitted_uses, public.iq_reference,
  public.kb_aliases
  to admin_api;

-- S, both: the SDK credential client, called by services and by the admin API (ADR-0016).
grant select, insert, update, delete on public.credentials to service_role, admin_api;

-- A: append-only (T7). The writer inserts and reads; the trigger refuses UPDATE, DELETE and
-- TRUNCATE for everyone; purge_audit_rows() is the one delete path.
grant select, insert on public.registry_audit, public.canary_audit, public.retention_audit,
  public.x_compliance_audit
  to service_role;
grant select on public.registry_audit, public.canary_audit, public.retention_audit,
  public.x_compliance_audit
  to admin_api;
grant select on public.admin_audit to service_role;
grant select, insert on public.admin_audit to admin_api;

-- R: reference data, changed only by migration (S4).
grant select on public.retention_classes, public.comment_series_profiles, public.retention_ttls
  to service_role, admin_api;

-- 5. Functions (T16, T17). Trigger functions need no EXECUTE to fire; a CHECK's helper needs it
-- for the role that writes the row.
grant execute on function public.current_client_ids() to authenticated, service_role, admin_api;
grant execute on function public.leader_lock_key(text), public.use_permitted(text, text, text),
  public.all_match(text[], text), public.audit_snapshot_ok(jsonb), public.is_route_scope(jsonb)
  to service_role, admin_api;
grant execute on function public.purge_audit_rows(text, text[], text) to service_role;
