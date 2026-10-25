-- F3 · two synthetic Auth users for local work and CI, and their memberships (plan T4; Question 1;
-- S11). Loaded only by supabase start and supabase db reset, never by scripts/migrate/postgres.sh
-- --seed, so staging gets no Auth user. Neither user has a credential, so nobody can sign in as
-- one: tests take a user by its id in the JWT claims instead. Each is a client_viewer of one
-- synthetic client (synthetic.sql). A re-run changes nothing.

insert into auth.users (instance_id, id, aud, role, email, email_confirmed_at, raw_app_meta_data,
    raw_user_meta_data, created_at, updated_at) values
  ('00000000-0000-0000-0000-000000000000', '5e7d0000-0000-4000-8000-00000000e001', 'authenticated',
   'authenticated', 'synthetic-user-a@example.invalid', now(), '{}', '{}', now(), now()),
  ('00000000-0000-0000-0000-000000000000', '5e7d0000-0000-4000-8000-00000000e002', 'authenticated',
   'authenticated', 'synthetic-user-b@example.invalid', now(), '{}', '{}', now(), now())
on conflict do nothing;

insert into public.client_members (user_id, client_id, role, added_by) values
  ('5e7d0000-0000-4000-8000-00000000e001', '5e7d0000-0000-4000-8000-00000000c001', 'client_viewer', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000e002', '5e7d0000-0000-4000-8000-00000000c002', 'client_viewer', 'F3 seed')
on conflict do nothing;
