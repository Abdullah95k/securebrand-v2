-- F3 · the hand-written reference seeds every environment needs (plan T4, "Seed sets"). Every
-- insert is ON CONFLICT DO NOTHING, so a re-run never overwrites a value the admin console changed.
-- The seeds generated from CONVENTIONS (budgets, budget tags' config, comment series profiles) are
-- the next migration, written by supabase/tools/gen-seeds.ts (T5).

-- The register of permitted uses (ADR-0068 L52, L57, L58): exactly four "not allowed" rows. A
-- missing row means allowed; no vendor, Disqus or news-host rows.
insert into public.permitted_uses (subject_kind, subject, use, allowed, clause, set_by) values
  ('platform', 'youtube', 'download_video', false,
   'YouTube''s terms forbid downloading video without YouTube''s prior written permission (and the rights holders'', where they apply)',
   'F3 seed (ADR-0068)'),
  ('platform', 'youtube', 'download_audio', false,
   'YouTube''s terms forbid downloading video without YouTube''s prior written permission (and the rights holders'', where they apply)',
   'F3 seed (ADR-0068)'),
  ('platform', 'facebook', 'train', false,
   'The user''s answer of 9 Oct 2026: ''Start as not allowed''', 'F3 seed (ADR-0068)'),
  ('platform', 'instagram', 'train', false,
   'The user''s answer of 9 Oct 2026: ''Start as not allowed''', 'F3 seed (ADR-0068)')
on conflict do nothing;

-- The class clocks (plan T20; C3, C8, S5; ADR-0054 to ADR-0056, ADR-0035 L25): one row per class
-- and part, 37 rows. A clock purges with purge_text (text and cache) or purge_derived (rows, raw
-- and analysis, no recompute); delete, which recomputes aggregates, is left to requests. Not clock
-- rows: tiktok_display's deletion on revocation (an authorization_revoked deletion, ADR-0035), the
-- requests of meta_on_request and telegram_bot, and the X 24-hour compliance deadline (on
-- signal_at, in x-compliance-sync and deletion-propagator, ADR-0069 (c)).
insert into public.retention_classes (class, part, vendor, anchor, clock, mode, executor, note) values
  ('meta_on_request', 'text', '', 'created_at', interval '10 years', 'purge_text', 'deletion-propagator',
   'Ten years where the rules allow (ADR-0054); deletions on request are deletion events'),
  ('meta_on_request', 'row', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054); aggregates are never recomputed by a clock (T20)'),
  ('meta_on_request', 'raw', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('meta_on_request', 'derived', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('vendor_agreed', 'text', '', 'created_at', interval '10 years', 'purge_text', 'deletion-propagator',
   'Ten years, no vendor override until a contract sets one (ADR-0054; DEFERRED L14 to L21)'),
  ('vendor_agreed', 'row', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('vendor_agreed', 'raw', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('vendor_agreed', 'derived', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('x_24h_sync', 'text', '', 'created_at', interval '10 years', 'purge_text', 'deletion-propagator',
   'Ten years; an X deletion signal is a deletion event within 24 hours (ADR-0069 (c))'),
  ('x_24h_sync', 'row', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('x_24h_sync', 'raw', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('x_24h_sync', 'derived', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('telegram_bot', 'text', '', 'created_at', interval '10 years', 'purge_text', 'deletion-propagator',
   'Ten years; requests are deletion events (ADR-0054)'),
  ('telegram_bot', 'row', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('telegram_bot', 'raw', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('telegram_bot', 'derived', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('tiktok_display', 'text', '', 'created_at', interval '10 years', 'purge_text', 'deletion-propagator',
   'Ten years; a revoked authorisation is an authorization_revoked deletion, not a clock (ADR-0035)'),
  ('tiktok_display', 'row', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('tiktok_display', 'raw', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('tiktok_display', 'derived', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('news_excerpt', 'text', '', 'created_at', interval '10 years', 'purge_text', 'deletion-propagator',
   'Ten years for the stored excerpt (ADR-0054)'),
  ('news_excerpt', 'row', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('news_excerpt', 'raw', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('news_excerpt', 'derived', '', 'created_at', interval '10 years', 'purge_derived', 'deletion-propagator',
   'Ten years (ADR-0054)'),
  ('news_excerpt', 'cache', '', 'fetched_at', interval '7 days', 'purge_text', 'deletion-propagator',
   'The full article text is a cache of seven days (CONVENTIONS L186 to L199)'),
  ('linkedin_48h', 'text', '', 'fetched_at', interval '48 hours', 'purge_text', 'deletion-propagator',
   'LinkedIn member content 48 hours (ADR-0055)'),
  ('linkedin_48h', 'row', '', 'fetched_at', interval '48 hours', 'purge_derived', 'deletion-propagator',
   'Rows and analysis removed with no recompute; counts and trends keep ten years (ADR-0055 L28)'),
  ('linkedin_48h', 'raw', '', 'fetched_at', interval '48 hours', 'purge_derived', 'deletion-propagator',
   '48 hours (ADR-0055)'),
  ('linkedin_48h', 'derived', '', 'fetched_at', interval '48 hours', 'purge_derived', 'deletion-propagator',
   '48 hours (ADR-0055)'),
  ('linkedin_org', 'text', '', 'fetched_at', interval '42 days', 'purge_text', 'deletion-propagator',
   'Six weeks; six months only if counsel confirms (ADR-0055; DEFERRED L26)'),
  ('linkedin_org', 'row', '', 'fetched_at', interval '42 days', 'purge_derived', 'deletion-propagator',
   'Six weeks (ADR-0055)'),
  ('linkedin_org', 'raw', '', 'fetched_at', interval '42 days', 'purge_derived', 'deletion-propagator',
   'Six weeks (ADR-0055)'),
  ('linkedin_org', 'derived', '', 'fetched_at', interval '42 days', 'purge_derived', 'deletion-propagator',
   'Six weeks (ADR-0055)'),
  ('youtube_30d_text', 'text', '', 'fetched_at', interval '30 days', 'purge_text', 'yt-text-purger',
   'Text refreshed or removed within 30 days (ADR-0056; yt-text-purger L21)'),
  ('youtube_30d_text', 'row', '', 'created_at', interval '36 months', 'purge_derived', 'yt-text-purger',
   'Rows and analysis 36 months from creation (ADR-0056; yt-text-purger L118); aggregates keep ten years'),
  ('youtube_30d_text', 'raw', '', 'created_at', interval '36 months', 'purge_derived', 'yt-text-purger',
   'Archives are rewritten at 30 days and kept 36 months (ADR-0039, ADR-0056)'),
  ('youtube_30d_text', 'derived', '', 'created_at', interval '36 months', 'purge_derived', 'yt-text-purger',
   '36 months (ADR-0056)')
on conflict do nothing;

-- The flags (ADR-0050, ADR-0051, ADR-0010; plan T10): every amber flag and fb-keyword-search's
-- override off, X on pay-per-use, the follower threshold present and unset. No fallback flag.
insert into public.feature_flags (name, scope, value, changed_by, reason) values
  ('FB_VENDOR_ROUTE', '', 'off', 'F3 seed', 'ADR-0050: every amber flag starts off'),
  ('FB_VENDOR_ROUTE', 'fb-keyword-search', 'off', 'F3 seed',
   'ADR-0051: the one override, fb-keyword-search''s vendor'),
  ('IG_VENDOR_ROUTE', '', 'off', 'F3 seed', 'ADR-0050: every amber flag starts off'),
  ('TT_VENDOR_ROUTE', '', 'off', 'F3 seed', 'ADR-0050: every amber flag starts off'),
  ('LI_VENDOR_ROUTE', '', 'off', 'F3 seed', 'ADR-0050: every amber flag starts off'),
  ('TG_VENDOR_ROUTE', '', 'off', 'F3 seed', 'ADR-0050: every amber flag starts off'),
  ('TG_POSTS_ACTOR', '', 'off', 'F3 seed', 'ADR-0050: every amber flag starts off'),
  ('X_PLAN', '', 'pay_per_use', 'F3 seed', 'ADR-0050: X starts on pay-per-use'),
  ('PUBLIC_ACCOUNT_FOLLOWER_THRESHOLD', '', null, 'F3 seed',
   'ADR-0050, ADR-0010 L58: unset (NULL) until the user sets it; an environment variable cannot')
on conflict do nothing;

-- The vendor rows of the credential register (ADR-0051 (a), (b), (e); C9, S13): one per role and
-- vendor, in the role's fallback order, with no key material (vault_ref NULL; the admin API adds
-- the key). A vendor whose owner is not yet verified is degraded until the user records the
-- verification and the admin API lifts it; ensembledata and telemetrio are cleared.
insert into public.credentials (owner_kind, owner_name, platform, role, fallback_rank, state, reason)
values
  ('vendor', 'scrapecreators', 'facebook', 'facebook_groups', 1, 'degraded', 'owner_not_verified'),
  ('vendor', 'sociavault', 'facebook', 'facebook_groups', 2, 'degraded', 'owner_not_verified'),
  ('vendor', 'sociavault', 'facebook', 'facebook_keyword_search', 1, 'degraded', 'owner_not_verified'),
  ('vendor', 'sociavault', 'instagram', 'instagram', 1, 'degraded', 'owner_not_verified'),
  ('vendor', 'ensembledata', 'tiktok', 'tiktok', 1, 'ok', null),
  ('vendor', 'tikhub', 'tiktok', 'tiktok', 2, 'degraded', 'owner_not_verified'),
  ('vendor', 'harvestapi', 'linkedin', 'linkedin', 1, 'degraded', 'owner_not_verified'),
  ('vendor', 'telemetrio', 'telegram', 'telegram_search_stats', 1, 'ok', null),
  ('vendor', 'tugelbay', 'telegram', 'telegram_posts', 1, 'degraded', 'owner_not_verified'),
  ('vendor', 'sovereigntaylor', 'telegram', 'telegram_posts', 2, 'degraded', 'owner_not_verified')
on conflict do nothing;

-- The alternates of ADR-0021 and ADR-0052 (d) (S16): active, since the vendor flag already gates
-- the fallback. None for a Facebook Page, an Instagram account or a YouTube channel, and none for
-- LinkedIn until LI0 finds the activity URN on the green API (T11).
insert into public.canary_targets (target_id, platform, route, service, source_type,
    alternate_route, alternate_vendor, flag_name, scope, active) values
  ('alternate:tiktok:account', 'tiktok', 'green', 'tt-profile-videos-poller', 'account',
   'amber', null, 'TT_VENDOR_ROUTE', null, true),
  ('alternate:telegram:channel', 'telegram', 'green', 'tg-channel-posts-poller', 'channel',
   'amber', null, 'TG_POSTS_ACTOR', null, true),
  ('alternate:instagram:hashtag', 'instagram', 'green', 'ig-keyword-search', 'hashtag',
   'amber', 'sociavault', 'IG_VENDOR_ROUTE', 'non_government', true)
on conflict do nothing;

-- The 19 governorates (the 18 and Halabja) and their capitals (ADR-0033 L29; Question 5): Arabic
-- as ar.wikipedia's list of Iraq's governorates writes them, Sorani as ckb.wikipedia's pages do,
-- and a common Latin form; listed in docs/handoffs/F3.md for the user to check. Ids are derived
-- from the Latin names, so a re-run finds every row. No outlet domains: the user's news-site list
-- fills them through the admin console.
with places (governorate_ar, governorate_ckb, governorate_latin, capital_ar, capital_ckb, capital_latin) as (
  values
    ('دهوك', 'دھۆک', 'Duhok', 'دهوك', 'دھۆک', 'Duhok'),
    ('نينوى', 'نەینەوا', 'Nineveh', 'الموصل', 'مووسڵ', 'Mosul'),
    ('أربيل', 'ھەولێر', 'Erbil', 'أربيل', 'ھەولێر', 'Erbil'),
    ('السليمانية', 'سلێمانی', 'Sulaymaniyah', 'السليمانية', 'سلێمانی', 'Sulaymaniyah'),
    ('كركوك', 'کەرکووک', 'Kirkuk', 'كركوك', 'کەرکووک', 'Kirkuk'),
    ('حلبجة', 'ھەڵەبجە', 'Halabja', 'حلبجة', 'ھەڵەبجە', 'Halabja'),
    ('صلاح الدين', 'سەلاحەددین', 'Salah al-Din', 'تكريت', 'تکریت', 'Tikrit'),
    ('ديالى', 'دیالە', 'Diyala', 'بعقوبة', 'بەعقووبە', 'Baqubah'),
    ('الأنبار', 'ئەنبار', 'Anbar', 'الرمادي', 'ڕەمادی', 'Ramadi'),
    ('بغداد', 'بەغدا', 'Baghdad', 'بغداد', 'بەغدا', 'Baghdad'),
    ('كربلاء', 'کەربەلا', 'Karbala', 'كربلاء', 'کەربەلا', 'Karbala'),
    ('واسط', 'واسیت', 'Wasit', 'الكوت', 'کووت', 'Kut'),
    ('بابل', 'بابل', 'Babil', 'الحلة', 'حللە', 'Hillah'),
    ('النجف', 'نەجەف', 'Najaf', 'النجف', 'نەجەف', 'Najaf'),
    ('القادسية', 'قادسیە', 'Qadisiyah', 'الديوانية', 'دیوانیە', 'Diwaniyah'),
    ('ميسان', 'میسان', 'Maysan', 'العمارة', 'عەمارە', 'Amarah'),
    ('المثنى', 'موسەنا', 'Muthanna', 'السماوة', 'سەماوە', 'Samawah'),
    ('ذي قار', 'زیقار', 'Dhi Qar', 'الناصرية', 'ناسریە', 'Nasiriyah'),
    ('البصرة', 'بەسرە', 'Basra', 'البصرة', 'بەسرە', 'Basra')
),
governorates as (
  insert into public.iq_reference (ref_id, kind, name_ar, name_ckb, name_latin, added_by)
  select md5('securebrand:iq_reference:governorate:' || governorate_latin)::uuid, 'governorate',
         governorate_ar, governorate_ckb, governorate_latin, 'F3 seed (Question 5)'
  from places
  on conflict do nothing
)
insert into public.iq_reference (ref_id, kind, name_ar, name_ckb, name_latin, parent_id, added_by)
select md5('securebrand:iq_reference:city:' || governorate_latin || ':' || capital_latin)::uuid,
       'city', capital_ar, capital_ckb, capital_latin,
       md5('securebrand:iq_reference:governorate:' || governorate_latin)::uuid,
       'F3 seed (Question 5)'
from places
on conflict do nothing;
