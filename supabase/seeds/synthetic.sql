-- F3 · synthetic data for local work, CI and staging (plan T4; C10, S11). Loaded by supabase start
-- and supabase db reset (supabase/config.toml), and in staging by scripts/migrate/postgres.sh
-- --seed. Every name, handle, id and address is synthetic; no Auth user here (local-auth.sql adds
-- them, locally only). Fixed ids and ON CONFLICT DO NOTHING: a re-run changes nothing.

-- Two clients: a commercial one that accepts amber, and a government one, which never does.
insert into public.clients (client_id, name, client_type, accepts_amber, x_end_user_declared) values
  ('5e7d0000-0000-4000-8000-00000000c001', 'synthetic-client-a', 'commercial', true, false),
  ('5e7d0000-0000-4000-8000-00000000c002', 'synthetic-client-b', 'government', false, false)
on conflict do nothing;

-- Thirteen sources across the platforms and both routes.
insert into public.sources (source_id, platform, source_type, platform_id, handle, url, display_name,
    route, vendor, tier, retention_class, client_ids, owned_by_client, followers, added_by) values
  ('5e7d0000-0000-4000-8000-00000000a001', 'facebook', 'page', 'synthetic-fb-page-a',
   'synthetic.fb.page.a', 'https://facebook.example.invalid/synthetic.fb.page.a',
   'Synthetic Facebook Page A', 'green', null, 2, 'meta_on_request',
   '{5e7d0000-0000-4000-8000-00000000c001,5e7d0000-0000-4000-8000-00000000c002}', false, 25000, 'client'),
  ('5e7d0000-0000-4000-8000-00000000a002', 'facebook', 'group', 'synthetic-fb-group-a',
   'synthetic.fb.group.a', 'https://facebook.example.invalid/groups/synthetic.fb.group.a',
   'Synthetic Facebook Group A', 'amber', 'scrapecreators', 3, 'vendor_agreed',
   '{5e7d0000-0000-4000-8000-00000000c001}', false, 4000, 'qualifier'),
  ('5e7d0000-0000-4000-8000-00000000a003', 'instagram', 'account', 'synthetic-ig-account-a',
   'synthetic.ig.account.a', 'https://instagram.example.invalid/synthetic.ig.account.a',
   'Synthetic Instagram Account A', 'green', null, 1, 'meta_on_request',
   '{5e7d0000-0000-4000-8000-00000000c001}', false, 150000, 'client'),
  ('5e7d0000-0000-4000-8000-00000000a004', 'instagram', 'hashtag', 'synthetic-ig-hashtag-a',
   'synthetic_hashtag_a', null, null, 'green', null, 3, 'meta_on_request',
   '{5e7d0000-0000-4000-8000-00000000c002}', false, null, 'client'),
  ('5e7d0000-0000-4000-8000-00000000a005', 'tiktok', 'creator', 'synthetic-tt-creator-a',
   'synthetic.tt.creator.a', 'https://tiktok.example.invalid/synthetic.tt.creator.a',
   'Synthetic TikTok Creator A', 'amber', 'ensembledata', 2, 'vendor_agreed',
   '{5e7d0000-0000-4000-8000-00000000c001}', false, 60000, 'qualifier'),
  ('5e7d0000-0000-4000-8000-00000000a006', 'tiktok', 'account', 'synthetic-tt-account-a',
   'synthetic.tt.account.a', 'https://tiktok.example.invalid/synthetic.tt.account.a',
   'Synthetic TikTok Account A', 'green', null, 1, 'tiktok_display',
   '{5e7d0000-0000-4000-8000-00000000c001}', true, 12000, 'client'),
  ('5e7d0000-0000-4000-8000-00000000a007', 'x', 'account', 'synthetic-x-account-a',
   'synthetic_x_account_a', 'https://x.example.invalid/synthetic_x_account_a',
   'Synthetic X Account A', 'green', null, 2, 'x_24h_sync',
   '{5e7d0000-0000-4000-8000-00000000c001,5e7d0000-0000-4000-8000-00000000c002}', false, 30000, 'qualifier'),
  ('5e7d0000-0000-4000-8000-00000000a008', 'x', 'keyword_rule',
   'green:5e7d00000000000000000000000000000000000000000000000000000000a008', 'synthetic.x.rule.a',
   null, 'Synthetic X Keyword Rule A', 'green', null, 2, 'x_24h_sync',
   '{5e7d0000-0000-4000-8000-00000000c001}', false, null, 'client'),
  ('5e7d0000-0000-4000-8000-00000000a009', 'linkedin', 'company_page', 'synthetic-li-page-a',
   'synthetic-li-page-a', 'https://linkedin.example.invalid/company/synthetic-li-page-a',
   'Synthetic LinkedIn Page A', 'green', null, 3, 'linkedin_org',
   '{5e7d0000-0000-4000-8000-00000000c001}', true, 3000, 'client'),
  ('5e7d0000-0000-4000-8000-00000000a010', 'telegram', 'channel', 'synthetic-tg-channel-a',
   'synthetic_tg_channel_a', 'https://telegram.example.invalid/synthetic_tg_channel_a',
   'Synthetic Telegram Channel A', 'amber', 'tugelbay', 2, 'vendor_agreed',
   '{5e7d0000-0000-4000-8000-00000000c001}', false, 45000, 'qualifier'),
  ('5e7d0000-0000-4000-8000-00000000a011', 'youtube', 'channel', 'synthetic-yt-channel-a',
   'synthetic.yt.channel.a', 'https://youtube.example.invalid/synthetic.yt.channel.a',
   'Synthetic YouTube Channel A', 'green', null, 1, 'youtube_30d_text',
   '{5e7d0000-0000-4000-8000-00000000c001,5e7d0000-0000-4000-8000-00000000c002}', false, 210000, 'qualifier'),
  ('5e7d0000-0000-4000-8000-00000000a012', 'news', 'site', 'synthetic-news.example.invalid',
   'synthetic-news.example.invalid', 'https://synthetic-news.example.invalid/',
   'Synthetic News Site A', 'green', null, 2, 'news_excerpt',
   '{5e7d0000-0000-4000-8000-00000000c002}', false, null, 'ops'),
  ('5e7d0000-0000-4000-8000-00000000a013', 'web', 'keyword_rule',
   'green:5e7d00000000000000000000000000000000000000000000000000000000a013', 'synthetic.web.rule.a',
   null, 'Synthetic Web Keyword Rule A', 'green', 'mojeek', 3, 'news_excerpt',
   '{5e7d0000-0000-4000-8000-00000000c002}', false, null, 'client')
on conflict do nothing;

-- Each client's sources, with client A the owner of its TikTok account (plan T9) and the
-- government client B on green sources only.
insert into public.client_sources (client_id, source_id, priority, relation, added_by) values
  ('5e7d0000-0000-4000-8000-00000000c001', '5e7d0000-0000-4000-8000-00000000a001', false, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c001', '5e7d0000-0000-4000-8000-00000000a002', false, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c001', '5e7d0000-0000-4000-8000-00000000a003', true, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c001', '5e7d0000-0000-4000-8000-00000000a005', false, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c001', '5e7d0000-0000-4000-8000-00000000a006', true, 'owner', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c001', '5e7d0000-0000-4000-8000-00000000a007', false, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c001', '5e7d0000-0000-4000-8000-00000000a008', false, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c001', '5e7d0000-0000-4000-8000-00000000a009', false, 'owner', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c001', '5e7d0000-0000-4000-8000-00000000a010', false, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c001', '5e7d0000-0000-4000-8000-00000000a011', false, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c002', '5e7d0000-0000-4000-8000-00000000a001', false, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c002', '5e7d0000-0000-4000-8000-00000000a004', false, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c002', '5e7d0000-0000-4000-8000-00000000a007', true, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c002', '5e7d0000-0000-4000-8000-00000000a011', false, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c002', '5e7d0000-0000-4000-8000-00000000a012', false, 'watcher', 'F3 seed'),
  ('5e7d0000-0000-4000-8000-00000000c002', '5e7d0000-0000-4000-8000-00000000a013', false, 'watcher', 'F3 seed')
on conflict do nothing;

-- One keyword each: a brand keyword for client A, a reputation keyword for the government client.
insert into public.keywords (keyword_id, client_id, label, forms, purpose, priority, platforms) values
  ('5e7d0000-0000-4000-8000-00000000b001', '5e7d0000-0000-4000-8000-00000000c001',
   'Synthetic Brand A',
   '[{"form_id": "f1", "text": "synthetic brand a", "lang": "en", "kind": "variant", "boundary": "word"}]',
   'brand', true, '{facebook,instagram,x,youtube}'),
  ('5e7d0000-0000-4000-8000-00000000b002', '5e7d0000-0000-4000-8000-00000000c002',
   'Synthetic Service B',
   '[{"form_id": "f1", "text": "synthetic service b", "lang": "en", "kind": "variant", "boundary": "word"}]',
   'reputation', false, '{facebook,x,news,web}')
on conflict do nothing;
