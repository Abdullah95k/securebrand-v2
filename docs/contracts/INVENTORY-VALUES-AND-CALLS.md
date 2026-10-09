# Contract inventory: enumerations and internal calls

D1 · 7 Oct 2026 · Companion to `docs/contracts/INVENTORY.md` (same sources, method and reading rules; see its first sections). Status: inventory of the drafts, nothing decided; disagreements are in `docs/contracts/CONFLICTS.md`.

## Contents

- [9. Enumerations other services see](#9-enumerations-other-services-see)
- [10. Internal calls between services](#10-internal-calls-between-services)

## 9. Enumerations other services see

Every value set a PRD defines for a field other services see, grouped by name as written. Value lists longer than 160 characters are cut; the reference points to the full list.

| Name as written | Values as written (services and first ref) |
|---|---|
| `access_mode` | direct, headless, proxy (news-article-extractor 5.3 L67; news-sitemap-poller 5.3 L71)<br>direct, headless, proxy, blocked (news-feed-poller 5.3 L68; news-homepage-differ 5.3 L69; news-robots-checker 3 L22; news-site-resolver 3 L21) |
| `account_class` | business_or_creator, individual (ig-account-resolver 5.2 L60) |
| `account_type (rule 1)` | page, group, business, creator, public figure, organisation, channel, company page, news domain, individual (poster-resolver 5.2 L57) |
| `action` | rejected (registry-writer 8 L114)<br>health_change (source-health-canary 6.2 L99) |
| `added_by` | client (fb-client-webhook-receiver 5.1 L46; li-client-posts-poller 4 L32; tg-bot-channel-receiver 5.2 L70)<br>qualifier (news-site-resolver 6.2 L94; qualifier 6.2 L84)<br>qualifier, client, ops (registry-writer 5.2 L52) |
| `AGG_MV_MODE` | service (aggregator 5.3 L59) |
| `aggregator job status` | done (deletion-propagator 5.3 L70) |
| `alerts` | backfill_lag, backfill_capped_rate, token_degraded, dlq_nonempty (fb-backfill 10 L143)<br>signature_failed_rate, webhook_5xx_rate, subscription_lost, rotation_behind, dlq_nonempty (fb-client-webhook-receiver 10 L164)<br>series_late, vendor_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate, budget_80_percent (fb-group-comments-fetcher 10 L159)<br>rotation_behind, vendor_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate, budget_80_percent (fb-group-posts-poller 10 L163; fb-keyword-search 10 L150)<br>rotation_behind, token_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate (fb-page-feed-poller 10 L162; fb-page-resolver 10 L159)<br>rotation_behind, token_degraded, dlq_nonempty, empty_200_rate, zero_results_streak (fb-page-search 10 L151)<br>series_late, token_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate, sweep_held (fb-post-comments-fetcher 10 L157)<br>metrics_behind, token_degraded, dlq_nonempty, empty_200_rate, schema_unknown (fb-reactions-fetcher 10 L159)<br>rotation_behind, token_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate, not_returned_spike (ig-account-media-poller 10 L156; ig-account-resolver 10 L161)<br>series_behind, vendor_credits_low, dlq_nonempty, empty_200_rate, quota_deny_rate, budget_80_percent (ig-comments-fetcher 10 L147)<br>rotation_behind, rotation_skipped, hashtag_budget_exhausted{ig_user_id}, token degraded, DLQ non-empty, canary degraded (ig-hashtag-search 10 L159)<br>rotation_behind, vendor_credits_low, dlq_nonempty, empty_200_rate, quota_deny_rate, budget_80_percent (ig-keyword-search 10 L150)<br>rotation_behind, token_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate, missed_push_rising (ig-mentions-fetcher 10 L159)<br>series_behind, token_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate (ig-own-comments-fetcher 10 L161)<br>signature_failed_rate, ack_latency_high, push_gap, subscription_lost, rotation_behind, dlq_nonempty (ig-webhook-receiver 10 L158)<br>router_lag, schema_unknown, dlq_nonempty, unroutable_spike (search-hit-router 10 L164)<br>rotation_behind, token_refresh_failed, authorisation_revoked, dlq_nonempty, empty_200_rate (tt-client-videos-fetcher 5.1 L47)<br>rotation_behind, dlq_total > 0, vendor_degraded, empty_200_ratio > 5%, budget_80pct, hashtag_id_unknown (tt-hashtag-feed-poller 5.1 L44)<br>rotation_behind, dlq_total > 0, vendor_degraded, empty_200_ratio > 5%, budget_80pct, precision_drop (tt-keyword-search 5.1 L42)<br>rotation_behind, vendor_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate (tt-profile-videos-poller 5.1 L47)<br>resolve_backlog, vendor_degraded, dlq_nonempty, empty_200_rate, individual_identity_fields_total non-zero (tt-user-resolver 5.1 L45)<br>rotation_behind, vendor_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate, commenter_identity_leak_total non-zero (tt-video-comments-fetcher 5.1 L52)<br>rotation_behind, vendor_degraded, dlq_nonempty, empty_200_rate, videos_gone_spike (tt-video-stats-refresher 5.1 L46)<br>rotation_behind, key_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate, unavailable_rate (yt-channel-resolver 5.1 L52)<br>series_late, key_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate, deletion_guard_hold (yt-comments-fetcher 8 L158)<br>lease_lapsed, subscription_failed, rotation_behind, notification_silence, push_missed_rate, webhook_5xx_rate, dlq_non... (yt-pubsub-receiver 10 L160)<br>series_late, key_degraded, dlq_nonempty, empty_200_rate, deletion_guard_hold (yt-replies-fetcher 8 L146)<br>yt_text_backlog, yt_text_at_risk, run_missed, audit_failed, dlq_nonempty (yt-text-purger 10 L222-L224)<br>rotation_behind, missed_push_rising, push_silent_channel, key_degraded, uploads_playlist_missing, dlq_nonempty, empty... (yt-uploads-reconciler 5.1 L49)<br>details_behind, key_degraded, quota_exhausted, dlq_nonempty, empty_200_rate, schema_unknown, deletion_spike, low_fill (yt-video-details-fetcher 5.1 L52) |
| `alerts (described, unnamed)` | `search` bucket above 80% of its daily allowance, a term skipped two days running, `quotaExceeded` seen, every term r... (yt-keyword-search 10 L157)<br>parse failure rate above 1% in a run, an engine `degraded`, a rule unqueried for 2 days, monthly spend above 80% of t... (yt-web-search-bridge 10 L163) |
| `alerts and raised conditions` | scan_behind, scan_held_for_review, emission_capped, dlq_nonempty, schema_unknown (web-commoncrawl-scanner 10 L136)<br>rotation_behind, pacing_breach, route_degraded, dlq_nonempty, query_rejected_rules, query_rejected, schema_unknown (web-gdelt-poller 10 L146)<br>rotation_behind, key_degraded, dlq_nonempty, empty_200_rate, quota_deny_rate, plan_not_storable, schema_unknown (web-search-mojeek 10 L140)<br>rotation_behind, schema_unknown (web-search-perplexity 5.1 L46) |
| `alerts status` | open, resolved (alert-evaluator 5.3 L67) |
| `alerts_blocked_total reason` | government_policy (alert-evaluator 10 L130) |
| `alias kind` | official, colloquial, abbreviation, misspelling, transliteration (analysis-entities 5.3 L61) |
| `allowed_updates` | channel_post, edited_channel_post, my_chat_member (tg-bot-channel-receiver 3 L21)<br>message, edited_message, my_chat_member (tg-discussion-receiver 3 L21) |
| `answer kind` | resolved, unresolvable, manual_candidate (poster-resolver 5.1 L46) |
| `Apify run status` | SUCCEEDED, FAILED, TIMED-OUT, ABORTED (li-company-posts-poller 5.3 L70; li-post-comments-fetcher 5.3 L75; li-post-search 5.3 L67)<br>FAILED, TIMED-OUT, ABORTED (li-org-resolver 8 L123) |
| `audit status` | pass, fail (retention-purger 5.2 L53) |
| `author fields dropped` | name, headline, profile link, picture (li-post-comments-fetcher 5.2 L63) |
| `author.author_type` | source, individual (normalize-item 5.2 L54) |
| `author_kind` | registered (news-comments-fetcher 6.2 L110) |
| `author_type` | source, individual (keyword-matcher 5.3 L73) |
| `backfill_status` | pending, running, done, capped (backfill-orchestrator 5.3 L81; fb-backfill 3 L21; li-post-search 5.1 L48; tt-hashtag-feed-poller 5.1 L48; tt-keyword-search 5.1 L44; yt-uploads-reconciler 5.1 L43)<br>pending, done, capped (fb-group-posts-poller 5.1 L40; fb-keyword-search 5.1 L40; fb-page-feed-poller 5.1 L40; ig-account-media-poller 5.1 L42; ig-keyword-search 5.1 L41; ig-mentions-fetcher 5.1 L41; li-client-posts-poller 5.1 L40; li-company-posts-poller 5.1 L41; tg-channel-posts-poller 5.1 L42; tt-client-videos-fetcher 5.1 L41; tt-profile-videos-poller 5.1 L41; x-full-archive-search 5.1 L39)<br>done, capped (ig-hashtag-search 5.1 L59; yt-pubsub-receiver 5.1 L44)<br>pending (news-site-resolver 6.2 L112)<br>capped (news-sitemap-poller 5.1 L51; tg-bot-channel-receiver 5.1 L50; tg-discussion-receiver 5.1 L51) |
| `backfill_status read` | done, capped, pending (x-filtered-stream 5.1 L40; x-user-timeline-poller 5.1 L38) |
| `backfills_total status` | done, capped (fb-backfill 10 L143) |
| `billed` | true, false (quota-governor 8 L128) |
| `bot member status accepted` | member, administrator (tg-discussion-receiver 5.2 L69) |
| `bot member status checked` | administrator (tg-bot-channel-receiver 5.2 L68) |
| `budget mode` | normal, stretch, exhausted (backfill-orchestrator 5.1 L44; comment-decay-scheduler 5.3 L98-L102) |
| `cache` | hit, miss (fb-page-resolver 5.1 L44; x-user-resolver 5.2 L53; yt-channel-resolver 5.2 L58) |
| `candidates_resolved_total outcome` | creator, individual, not_found, private (tt-user-resolver 10 L141) |
| `capacity answer fits` | true, false (qualifier 5.3 L67) |
| `capped_reason` | route_cap, budget, deadline, failed (backfill-orchestrator 5.3 L81) |
| `cc_hosts_seen state` | emitted, pending, suppressed (web-commoncrawl-scanner 6.1 L80) |
| `channels` | email, Telegram, Slack, client webhook (alert-evaluator 3 L24) |
| `class` | ok, empty_200, low_yield, throttled, auth, server, schema_unknown (source-health-canary 5.3 L64) |
| `client status` | active, offboarding (yt-text-purger 5.1 L45) |
| `client_type` | government (keyword-matcher 5.3 L69) |
| `clients.status` | offboarding (retention-purger 5.1 L43) |
| `comment series step` | once (backfill-orchestrator 5.1 L48) |
| `comments_provider` | disqus, none (news-comments-fetcher 2 L13; news-site-resolver 3 L20) |
| `completion message status` | done, skipped_flag_off, video_gone (tt-video-stats-refresher 5.2 L59) |
| `context.query_arm` | ar (x-recent-search 6.2 L119) |
| `context.type` | group (fb-keyword-search 5.4 L82) |
| `country_signals keys` | phone_964, website_tld, city_in_bio (ig-account-resolver 5.2 L61)<br>location, phone_964, iq_domain, seed_list (li-org-resolver 6.2 L94)<br>iraqi_place, phone_964, iq_domain, outlet_link, seed_list (poster-resolver 6.2 L89)<br>vendor_country, text_signals (tg-channel-resolver 5.2 L57) |
| `country_source` | snippet, brandingSettings (yt-channel-resolver 5.2 L62) |
| `curator action` | add an alias, add an entity, discard (analysis-entities 5.3 L71) |
| `decision` | add, reject, review, queued, mention_only, tier_down, retire, tier_change (qualifier 5.2 L52-L61)<br>allow, wait_until, deny (quota-governor 2 L13) |
| `decision type` | add, update, tier_change, tier_down, dormant, promote, retire, health_change, remove_client, queued, mention_only (registry-writer 3 L22)<br>remove_client (yt-text-purger 5.1 L45) |
| `decisions kind` | fb_page_search_emitted (fb-page-search 6.3 L123) |
| `degraded reason` | query_rejected (web-gdelt-poller 5.2 L56) |
| `deletion origins` | client, user, Meta request (ig-comments-fetcher 5.1 L49) |
| `deletion reason` | platform_sync (news-comments-fetcher 5.2 L58; tt-video-comments-fetcher 6.2 L119; tt-video-stats-refresher 3 L22)<br>authorization_revoked (tt-client-videos-fetcher 14.3 L178) |
| `deletion reasons that fire` | platform_sync, X compliance reason (as named by deletion-propagator) (alert-evaluator 5.3 L61) |
| `deletion request states skipped` | pending, in-progress (raw-archiver 5.3 L71) |
| `deletion_requests status` | completed (yt-text-purger 5.2 L58) |
| `deletion_requests status (guard)` | done (store-writer 5.2 L49) |
| `deletions reason` | platform_sync (fb-client-webhook-receiver 5.2 L56; fb-group-comments-fetcher 5.2 L65; fb-post-comments-fetcher 5.2 L69; fb-reactions-fetcher 8 L144; ig-own-comments-fetcher 5.1 L49) |
| `delivery` | push (fb-client-webhook-receiver 6.2 L125; ig-webhook-receiver 6.2 L118; yt-pubsub-receiver 6.2 L118) |
| `deny reason` | flag_off, period_full, priority_gate (quota-governor 5.3 L67-L71) |
| `description_lang` | ckb, ar, other, none (yt-channel-resolver 5.2 L63) |
| `dialect` | iraqi, gulf, levantine, egyptian, maghrebi, msa, other, sorani, null (lang-dialect-id 5.3 L67) |
| `dialect_scores keys` | iraqi, gulf, levantine, egyptian, maghrebi, msa, other, sorani, kurmanji (lang-dialect-id 6.2 L114) |
| `discovered_by` | search-hit-router (news-site-resolver 6.2 L106) |
| `discovery.hits platform` | instagram, facebook, telegram, youtube, x, linkedin, tiktok, news, web (search-hit-router 5.3 L72-L83)<br>news (web-commoncrawl-scanner 6.2 L92) |
| `discovery.hits type` | account, group, page, channel, company_page, creator, site (search-hit-router 5.3 L72-L83)<br>site (web-commoncrawl-scanner 2 L15) |
| `DLQ reason` | query_rejected (x-full-archive-search 8 L147)<br>schema_unknown (yt-channel-resolver 8 L153) |
| `dropped_total reason` | tombstoned (store-writer 13.8 L174) |
| `edge` | recent_media, top_media (ig-hashtag-search 5.1 L45) |
| `engine` | gdelt (web-gdelt-poller 6.2 L99)<br>mojeek (web-search-mojeek 6.2 L96)<br>perplexity (web-search-perplexity 6.2 L97) |
| `engine / vendor` | mojeek, perplexity (yt-web-search-bridge 6.2 L111) |
| `engines` | perplexity, mojeek, gdelt (search-hit-router 6.2 L111) |
| `entities[].level` | city (analysis-entities 6.2 L108) |
| `entities[].source` | both, gazetteer (analysis-entities 6.2 L110) |
| `entity type` | brand, company, institution, place, product, person_public (analysis-entities 5.3 L61) |
| `envelope kind` | post (ig-hashtag-search 3 L24) |
| `envelope.identity` | hashed (li-post-comments-fetcher 6.2 L123) |
| `envelope.kind` | post (ig-account-media-poller 3 L22; li-client-posts-poller 3 L21; li-company-posts-poller 3 L20; li-post-search 6.2 L88)<br>comment (ig-comments-fetcher 3 L22; ig-own-comments-fetcher 3 L22; li-own-comments-fetcher 3 L20; li-post-comments-fetcher 3 L20; tt-video-comments-fetcher 3 L21)<br>post, comment (ig-mentions-fetcher 3 L22)<br>comment, reaction (li-notification-receiver 3 L21)<br>article_url (news-feed-poller 6.2 L97; news-homepage-differ 6.2 L102; news-sitemap-poller 6.2 L109) |
| `envelope.metrics_observation` | poll (li-client-posts-poller 6.2 L120; li-company-posts-poller 6.2 L117) |
| `evaluation status` | stale (alert-evaluator 5.2 L46) |
| `event` | added, updated, tier_change, dormant, retired, fallback_on, fallback_off (registry-writer 3 L24)<br>new, edit (tg-bot-channel-receiver 5.2 L61; tg-discussion-receiver 5.2 L65) |
| `event (names to be confirmed)` | comment created or edited, comment deleted, reaction added, reaction removed, member post mentioning the organization (li-notification-receiver 5.4 L94-L100) |
| `event type (read)` | added, updated, route change, retired (li-client-posts-poller 6.1 L101)<br>added, retired (li-notification-receiver 5.1 L42) |
| `event type (written)` | updated (li-client-posts-poller 6.2 L126; li-notification-receiver 6.2 L133)<br>tier change, updated (li-company-posts-poller 5.1 L43) |
| `evidence.language_share keys` | ara (web-commoncrawl-scanner 6.2 L98) |
| `evidence.path_signals` | date_path, news_path (web-commoncrawl-scanner 6.2 L98) |
| `executor` | deletion-propagator, yt-text-purger, none (retention-purger 5.3 L60-L68) |
| `extracted.kind` | video (yt-web-search-bridge 6.2 L121) |
| `fallback` | on (registry-writer 13.5 L149) |
| `fallback state` | fallback_on, fallback_off (tt-hashtag-feed-poller 5.2 L55; tt-keyword-search 5.2 L49) |
| `fastText labels` | ar, arz, ckb, ku, fa, en (lang-dialect-id 5.3 L59) |
| `FB_VENDOR_ROUTE` | off, scrapecreators, sociavault (fb-group-posts-poller 3 L20)<br>off, sociavault, scrapecreators (fb-keyword-search 5.1 L40) |
| `feed_format` | rss2 (news-feed-poller 6.2 L110) |
| `feeds[].format` | rss2 (news-site-resolver 6.2 L97) |
| `fetch outcome` | media_unavailable (analysis-media 2 L16) |
| `fetch report complete` | true, false (fb-group-comments-fetcher 5.2 L66; fb-post-comments-fetcher 5.2 L70) |
| `fetches_total kind` | incremental, sweep (fb-post-comments-fetcher 10 L157) |
| `field` | feed, comments (fb-client-webhook-receiver 3 L21) |
| `forms[].boundary` | clitic, word, exact (keyword-matcher 5.3 L56) |
| `forms[].kind` | term, handle, hashtag (keyword-matcher 5.3 L56) |
| `forms[].lang` | ar, ckb, en (keyword-matcher 5.3 L56) |
| `found_by` | web_search (search-hit-router 6.2 L124) |
| `found_via` | feed, news_sitemap, homepage_diff, sitemap_backfill, commoncrawl (news-article-extractor 5.1 L42)<br>feed (news-feed-poller 6.2 L102)<br>homepage_diff (news-homepage-differ 6.2 L107)<br>news_sitemap, sitemap_backfill (news-sitemap-poller 6.2 L114) |
| `gap job kind` | reconciliation (x-filtered-stream 5.2 L70) |
| `global taxonomy topics` | service quality, pricing, outage, customer support, product launch, corporate news, others (analysis-topics 3 L25) |
| `government allowed types` | volume_spike, negative_share, keyword_first_seen (alert-evaluator 5.3 L65) |
| `government keyword purposes` | reputation, service_quality (alert-evaluator 5.3 L65) |
| `health` | degraded (fb-client-webhook-receiver 5.2 L59; fb-page-resolver 8 L145; fb-page-search 8 L137; fb-reactions-fetcher 8 L145; ig-account-resolver 8 L147; ig-comments-fetcher 8 L132; ig-webhook-receiver 5.2 L60; tg-channel-resolver 8 L119; tg-message-search 8 L107; tt-hashtag-feed-poller 8 L123; tt-keyword-search 8 L117; tt-user-resolver 8 L126; tt-video-comments-fetcher 8 L135; tt-video-stats-refresher 8 L128; yt-pubsub-receiver 8 L145)<br>blocked, fallback, degraded (fb-group-comments-fetcher 5.2 L59; fb-group-posts-poller 5.2 L56; fb-keyword-search 5.2 L52)<br>blocked, degraded (fb-page-feed-poller 5.1 L40; fb-post-comments-fetcher 5.2 L61; ig-account-media-poller 5.1 L42; ig-hashtag-search 5.2 L64; ig-mentions-fetcher 5.1 L41; ig-own-comments-fetcher 5.2 L57; li-client-posts-poller 5.1 L40; li-company-posts-poller 5.1 L41; li-notification-receiver 8 L153; li-own-comments-fetcher 5.2 L58; tg-channel-posts-poller 5.1 L42; tg-discussion-receiver 5.2 L69; tt-client-videos-fetcher 5.1 L41; tt-profile-videos-poller 5.1 L41; x-full-archive-search 5.2 L49; x-recent-search 5.1 L39; x-replies-fetcher 5.2 L53; x-user-timeline-poller 5.1 L38; yt-comments-fetcher 5.2 L52; yt-replies-fetcher 5.2 L48; yt-uploads-reconciler 5.1 L43)<br>fallback, degraded (ig-keyword-search 5.1 L41)<br>ok, blocked, degraded (news-site-resolver 6.2 L112)<br>ok, degraded, fallback (registry-writer 5.2 L54)<br>ok, degraded, fallback, blocked (source-health-canary 5.3 L68-L73)<br>blocked, ok, degraded (tg-bot-channel-receiver 5.2 L72)<br>blocked, ok (x-compliance-sync 5.3 L83)<br>ok, degraded (yt-text-purger 5.3 L83) |
| `health (source)` | blocked, degraded (comment-decay-scheduler 8 L160) |
| `health reason` | privacy_mode (tg-discussion-receiver 5.2 L69) |
| `health values used` | degraded (web-commoncrawl-scanner 8 L120)<br>blocked, degraded (web-gdelt-poller 5.1 L42; web-search-mojeek 5.1 L43; web-search-perplexity 5.1 L42) |
| `hints keys` | domain, language, source_country (web-gdelt-poller 6.2 L92) |
| `hit_type` | page (fb-page-search 2 L13) |
| `hits status` | active, retracted (store-writer 5.3 L63) |
| `hits_total kind` | registered, discovery, suppressed (tg-message-search 5.2 L55) |
| `HTTP answers` | 200, 403, 500 (ig-webhook-receiver 5.2 L53) |
| `HTTP response` | 2xx after Redpanda acknowledges, 401 signature mismatch, 400 malformed body, 200 unknown organization / unknown shape... (li-notification-receiver 5.2 L53-L57) |
| `HTTP status handling` | 2xx (continue), 404 or 410 (gone, no recheck), 402 (paywalled plus recheck), other 4xx (recheck, stop host batch), 42... (news-article-extractor 5.2 L54)<br>304 (completed poll), 429 (backoff), 401, 402, 403, 451, any other 4xx (recheck), 404 or 410 on a feed URL (refresh) (news-feed-poller 5.2 L54)<br>304 (completed fetch), 429 (backoff), any 4xx other than 404 and 410 (recheck), homepage 404 or 410 (refresh) (news-homepage-differ 5.3 L71)<br>304 (completed poll), 429 (backoff), any 4xx other than 404 and 410 (recheck), 404 or 410 on a sitemap URL (refresh) (news-sitemap-poller 5.2 L57) |
| `hub.mode` | subscribe (fb-client-webhook-receiver 5.2 L52; ig-webhook-receiver 5.2 L53) |
| `identity` | hashed (li-notification-receiver 5.2 L56) |
| `identity-like keys redacted / rejected` | name, headline, picture, any string containing linkedin.com/in/ (li-post-comments-fetcher 8 L148) |
| `ids_returned keys` | deleted, protected, suspended, withheld, deactivated, other (x-compliance-sync 6.2 L122) |
| `IG_VENDOR_ROUTE` | off, sociavault (ig-comments-fetcher 13.1 L163; ig-keyword-search 5.2 L57) |
| `image tag vocabulary (examples)` | screenshot, meme, document, product, storefront, vehicle, cable or equipment, food, landscape (analysis-media 5.3 L64) |
| `inbound message kind` | push (ig-webhook-receiver 5.2 L55) |
| `ingest_mode` | webhook (tg-bot-channel-receiver 6.2 L119; tg-discussion-receiver 6.2 L120) |
| `intent label` | complaint, question, praise, request, announcement, other (analysis-topics 3 L26) |
| `item` | post, comment (fb-client-webhook-receiver 5.2 L56) |
| `job acknowledgement` | skipped_flag_off, skipped_government (li-company-posts-poller 5.2 L55; li-post-comments-fetcher 5.1 L52) |
| `job acknowledgement / jobs_total{status}` | skipped_flag_off, skipped_government (li-post-search 5.2 L55) |
| `job acknowledgement reason` | no_amber_client (tg-channel-posts-poller 5.2 L60) |
| `job acknowledgement status` | skipped_flag_off (fb-group-comments-fetcher 5.2 L59; fb-group-posts-poller 5.2 L56; fb-keyword-search 5.2 L52) |
| `job completion status` | skipped_flag_off, skipped_government (tg-message-search 5.1 L47) |
| `job kind` | recompute (aggregator 5.1 L37)<br>backtest (alert-evaluator 5.1 L42)<br>rerun (analysis-entities 5.1 L46; analysis-media 5.1 L47; analysis-topics 5.1 L50)<br>analyze, rerun (analysis-sentiment 6.1 L85)<br>comments, replies, metrics, health (comment-decay-scheduler 3 L21)<br>rotation, reconciliation, backfill, metrics, ops_force (ig-account-media-poller 5.2 L58)<br>resolve, rotation (ig-account-resolver 5.1 L42)<br>comments, ops_force (ig-comments-fetcher 5.2 L57)<br>rotation, backfill, ops_force (ig-keyword-search 5.2 L57)<br>rotation, reconciliation, backfill, ops_force (ig-mentions-fetcher 5.2 L55)<br>comments, replies, reconciliation, ops_force (ig-own-comments-fetcher 3 L19)<br>rematch, candidate_retry (keyword-matcher 6.1 L90)<br>replay, lang_rescore (normalize-item 6.1 L86)<br>retention_sweep (retention-purger 5.3 L63)<br>rotation, ops_force (web-commoncrawl-scanner 5.1 L41)<br>rotation (web-gdelt-poller 6.1 L86; web-search-mojeek 6.1 L83)<br>rotation, site_search (web-search-perplexity 6.1 L85) |
| `job kinds` | refresh (tg-channel-resolver 5.1 L44) |
| `job kinds consumed` | reconciliation, ops_force (tg-bot-channel-receiver 6.1 L109; tg-discussion-receiver 6.1 L110)<br>rotation, reconciliation, backfill, metrics, ops_force (tg-channel-posts-poller 6.1 L103) |
| `job outcome counters` | gov_excluded, flag_off, skipped_flag_off, cache_hit (tt-user-resolver 5.1 L43) |
| `job outcomes` | gov_excluded, flag_off, skipped_flag_off, video_gone (tt-video-comments-fetcher 5.2 L56) |
| `job priority` | priority tier 1 (client refresh), lowest (backfilled posts once fetch) (comment-decay-scheduler 5.1 L66) |
| `job report fields` | new_count, seen_count, pages, cost_units, newest_comment_at (li-own-comments-fetcher 3 L20)<br>new_count, seen_count, pages, cost_units, new marker (li-post-comments-fetcher 3 L20) |
| `job result fields` | new_count, seen_count, pages, cost_units, incomplete reply threads (ig-own-comments-fetcher 3 L20) |
| `job result status` | skipped (ig-comments-fetcher 5.1 L41; ig-keyword-search 5.2 L57) |
| `job_kind` | backfill (normalize-item 5.1 L45)<br>backfill, keyword_history, replies (x-full-archive-search 6.2 L128) |
| `jobs produced` | reconciliation, ops_force (ig-webhook-receiver 5.1 L43) |
| `jobs_total status` | flag_off (tt-hashtag-feed-poller 13.1 L154; tt-keyword-search 5.1 L42; tt-profile-videos-poller 5.2 L58) |
| `jobs_total{status}` | remembered_reject, vendor_route_off, route_unavailable_government (li-org-resolver 10 L134) |
| `KB scope` | global, (a client) (analysis-entities 5.3 L61) |
| `key and site states` | degraded (news-comments-fetcher 8 L138) |
| `keywords change` | created, variants changed (fb-page-search 5.1 L40) |
| `kind` | post, comment (fb-client-webhook-receiver 3 L21)<br>comments, replies, ops_force (fb-group-comments-fetcher 3 L19)<br>rotation, backfill, ops_force (fb-group-posts-poller 3 L19; fb-keyword-search 3 L19; li-company-posts-poller 5.2 L55; news-sitemap-poller 5.2 L55; tt-client-videos-fetcher 5.2 L55)<br>resolve, rotation, ops_force (fb-page-resolver 5.1 L42; x-user-resolver 5.1 L41; yt-channel-resolver 5.1 L44)<br>comments, ops_force (fb-post-comments-fetcher 3 L19; news-comments-fetcher 3 L19)<br>refresh_24h, refresh_7d, refresh_client (fb-reactions-fetcher 5.1 L41)<br>rotation, reconciliation, backfill, ops_force (li-client-posts-poller 5.2 L56; tt-profile-videos-poller 5.2 L57)<br>refresh (li-org-resolver 5.1 L44; yt-text-purger 5.3 L96)<br>comments (li-own-comments-fetcher 3 L19; li-post-comments-fetcher 3 L19; x-replies-fetcher 3 L19; yt-comments-fetcher 5.1 L40)<br>backfill (li-post-search 5.1 L48)<br>article (news-article-extractor 6.2 L89)<br>rotation, ops_force (news-feed-poller 5.2 L52; news-homepage-differ 5.2 L53)<br>first_check, refresh, recheck, ops_force (news-robots-checker 3 L19)<br>resolve, refresh (news-site-resolver 5.1 L38)<br>site (news-site-resolver 6.2 L84)<br>post, reply, quote (normalize-item 5.3 L68)<br>post (tg-bot-channel-receiver 3 L23; tg-channel-posts-poller 3 L22; tg-message-search 6.2 L82; yt-pubsub-receiver 6.2 L107; yt-uploads-reconciler 3 L24)<br>comment (tg-discussion-receiver 3 L22)<br>comments, replies (tt-video-comments-fetcher 3 L19)<br>metrics, ops_force (tt-video-stats-refresher 4 L35)<br>backfill, keyword_history, replies (x-full-archive-search 3 L19-L21)<br>rotation, reconciliation, ops_force (x-user-timeline-poller 5.2 L54)<br>video (yt-keyword-search 5.2 L59)<br>first_sight (yt-keyword-search 5.2 L59; yt-pubsub-receiver 6.2 L127)<br>replies (yt-replies-fetcher 5.1 L38)<br>retention_sweep, ops_force (yt-text-purger 5.1 L44)<br>reconciliation, backfill, ops_force (yt-uploads-reconciler 3 L21)<br>first_sight, metrics, ops_force (yt-video-details-fetcher 5.1 L44-L46)<br>first_sight, resolve (yt-web-search-bridge 5.2 L61) |
| `kind / origin_kind` | first_sight, reconciliation (yt-uploads-reconciler 6.2 L133) |
| `kind_hint` | search_response (web-gdelt-poller 5.2 L57; web-search-mojeek 5.2 L57; web-search-perplexity 5.2 L55) |
| `label` | positive, negative, neutral, mixed (analysis-sentiment 2 L15) |
| `lane` | priority (analysis-media 6.2 L100)<br>priority, standard (analysis-sentiment 5.1 L47; analysis-topics 5.1 L46)<br>metrics (comment-decay-scheduler 5.1 L68) |
| `lang` | ar, ckb, en, mixed, other, und (lang-dialect-id 3 L22)<br>und (normalize-item 8 L133) |
| `lang (fold input)` | ar, ckb, en (lang-dialect-id 5.3 L88) |
| `lang_share keys` | ar_iq, ckb, en (li-org-resolver 6.2 L95)<br>ar_iq, ckb, ar_msa, en (poster-resolver 6.2 L89) |
| `lang_share sentinel` | unknown (tg-channel-resolver 5.2 L58) |
| `last_error` | hashtag_id_unknown (tt-hashtag-feed-poller 8 L126) |
| `LI_VENDOR_ROUTE` | off, harvestapi (li-company-posts-poller 1 L7; li-org-resolver 5.2 L53; li-post-comments-fetcher 1 L7; li-post-search 1 L9) |
| `live_state` | live, upcoming, none (yt-video-details-fetcher 5.1 L54) |
| `matched_by` | simhash (news-dedup 6.2 L97) |
| `matched_in` | hashtag (ig-hashtag-search 6.2 L124) |
| `media type` | image (analysis-media 6.2 L105) |
| `mention_type` | tag, mentioned_media, mentioned_comment (ig-mentions-fetcher 6.2 L126) |
| `message classification` | post copy (is_automatic_forward), service message, comment (tg-discussion-receiver 5.2 L61) |
| `metrics observation label` | first_sight, plus_24h, plus_7d (tt-client-videos-fetcher 6.2 L109) |
| `metrics_observation` | backfill (fb-backfill 5.1 L47; x-full-archive-search 6.2 L122)<br>poll (fb-group-posts-poller 6.2 L118; fb-page-feed-poller 6.2 L123; x-user-timeline-poller 6.2 L128)<br>search (fb-keyword-search 6.2 L114)<br>poll, backfill (ig-account-media-poller 5.1 L50; ig-keyword-search 5.1 L51; ig-mentions-fetcher 5.1 L49)<br>poll, refresh_24h (tg-channel-posts-poller 6.2 L122)<br>first_sight (tt-profile-videos-poller 5.4 L95)<br>stream (x-filtered-stream 6.2 L130) |
| `metrics_observation (read)` | poll, backfill, webhook_reconcile (fb-reactions-fetcher 3 L19) |
| `minimized` | true (tg-discussion-receiver 5.2 L63) |
| `mode` | delete, purge_text (deletion-propagator 5.3 L62; retention-purger 5.3 L70)<br>extract, refresh (fb-reactions-fetcher 3 L19)<br>normal, stretch, exhausted (quota-governor 3 L22)<br>delete, withhold (x-compliance-sync 5.3 L73-L79)<br>purge_text, purge_derived (yt-text-purger 5.3 L106) |
| `model_route` | ar (analysis-sentiment 6.2 L110) |
| `model_versions status` | candidate, shadow, active, retired (analysis-sentiment 5.3 L76) |
| `news-like signals` | engine is GDELT, result carries a publication date, path has a date segment or a news segment (/news/, /article/, /st... (search-hit-router 5.3 L85) |
| `non-candidate kinds` | comments, replies (keyword-matcher 5.3 L75) |
| `normalize` | skip (web-gdelt-poller 5.2 L57; web-search-mojeek 5.2 L57; web-search-perplexity 5.2 L55) |
| `normalizer error` | schema_unknown (yt-comments-fetcher 8 L159; yt-keyword-search 8 L144; yt-uploads-reconciler 8 L156; yt-web-search-bridge 8 L148) |
| `note` | flag_off, no_history_route (backfill-orchestrator 5.2 L56) |
| `notice_status` | delivered, undelivered (deletion-propagator 5.3 L72) |
| `object` | instagram (ig-webhook-receiver 5.4 L79) |
| `observation` | poll, backfill, webhook_reconcile, refresh_24h, refresh_7d, refresh_client (fb-reactions-fetcher 3 L19)<br>new, edit, seen (x-replies-fetcher 5.2 L58; yt-comments-fetcher 5.2 L55; yt-replies-fetcher 5.2 L52)<br>first_sight, ops_force, refresh_24h, refresh_7d, refresh_client, live_end (yt-video-details-fetcher 5.1 L54) |
| `observation.label` | plus_24h, plus_7d (tt-video-stats-refresher 3 L20) |
| `offsets_in` | text_norm (keyword-matcher 6.2 L109) |
| `onboarding state` | awaiting_channel (tg-discussion-receiver 5.2 L67) |
| `origin` | discovery, seed, manual (li-org-resolver 5.1 L44)<br>discovery, manual (poster-resolver 3 L27; qualifier 3 L27)<br>web_search (search-hit-router 6.2 L110)<br>client_onboarding (tg-bot-channel-receiver 5.2 L70)<br>discovery, client, ops, refresh (tg-channel-resolver 5.2 L52)<br>commoncrawl_index (web-commoncrawl-scanner 6.2 L95)<br>search (yt-keyword-search 5.2 L59)<br>web_bridge (yt-web-search-bridge 5.2 L61) |
| `outcome` | resolved, individual, unresolvable, cached (poster-resolver 10 L123)<br>duplicate, unroutable, already_registered, web, unparseable (search-hit-router 5.2 L58) |
| `outcomes` | not_article, gone, paywalled, skipped_policy, duplicate_canonical (news-article-extractor 3 L22) |
| `park reason` | schema_unknown (news-dedup 8 L121) |
| `parking status` | schema_unknown (li-client-posts-poller 8 L145; li-company-posts-poller 8 L143; li-notification-receiver 8 L150; li-org-resolver 8 L125; li-own-comments-fetcher 8 L145; li-post-comments-fetcher 8 L148; li-post-search 8 L125) |
| `payload.action` | COMMENT (li-notification-receiver 5.4 L86) |
| `payload.author.type` | member, company (li-post-search 5.4 L71) |
| `payload_redacted` | from (fb-client-webhook-receiver 5.2 L58; fb-post-comments-fetcher 5.4 L87)<br>author (fb-group-comments-fetcher 5.4 L94) |
| `period / reset_rule` | billing_cycle, UTC day, rolling 24 hours, rolling 7 days, daily, calendar month, contract cycle (quota-governor 5.1 L53) |
| `platform_status` | deleted, protected, suspended, deactivated, withheld (x-compliance-sync 5.3 L73-L79) |
| `policy states that block fetching` | disallowed, paywalled, blocked (news-article-extractor 2 L13) |
| `policy status (blocking)` | disallowed, paywalled, blocked (news-site-resolver 5.2 L46) |
| `post-gone notice` | post_unavailable (fb-post-comments-fetcher 8 L143) |
| `post-like item kinds` | post, video, article, message, result (keyword-matcher 5.3 L74) |
| `poster.source_type` | channel (tg-message-search 6.2 L83) |
| `poster_profiles.status` | resolving (x-user-resolver 5.1 L41) |
| `priority` | 1: Tier 1 rotation polls, client refresh requests, ops_force, canary fetches, 2: Tier 2 rotation, keyword and hashtag... (quota-governor 5.1 L39-L47)<br>5, 1 (x-full-archive-search 5.2 L53)<br>2, 3, 4 (x-replies-fetcher 7 L145; yt-comments-fetcher 7 L147)<br>1, 2, 3 (x-user-timeline-poller 5.2 L56)<br>3, 4 (yt-replies-fetcher 5.2 L50)<br>1, 2, 3, 5 (yt-uploads-reconciler 5.1 L45; yt-video-details-fetcher 5.1 L50) |
| `private Telegram paths` | t.me/c/…, t.me/+…, t.me/joinchat/… (search-hit-router 5.3 L77) |
| `profile` | fb_page, fb_group, ig_own, ig_other, tt, x, yt, li_own, li_other, tg_own, news (comment-decay-scheduler 5.1 L46-L58) |
| `profile.reason` | not_a_readable_page (fb-page-resolver 6.2 L128) |
| `profile.status` | ok, not_found, private (tt-user-resolver 5.2 L56) |
| `proposed_tier` | 1, 2, 3 (news-site-resolver 5.2 L53) |
| `purpose` | reputation, service_quality (keyword-matcher 5.3 L69) |
| `qualifies_as` | organization_or_public_figure, individual (x-user-resolver 5.2 L57) |
| `qualifies_by` | followers_500, verified, watchlist (x-user-resolver 5.2 L57) |
| `query.variant` | or_group (web-gdelt-poller 6.2 L102)<br>arabic_context (web-search-mojeek 5.1 L46) |
| `query.variant (generator slot order)` | latin_exact, latin_context, arabic_exact, arabic_alt_spelling, arabic_joined_or_split, arabic_context, arabic_intent,... (web-search-perplexity 5.1 L45) |
| `quota mode` | stretch (yt-comments-fetcher 7 L147) |
| `quota-governor answer` | wait-until, deny (fb-page-feed-poller 5.2 L56; ig-account-resolver 5.2 L58; ig-comments-fetcher 5.2 L59; ig-hashtag-search 5.2 L65; ig-keyword-search 5.2 L59; ig-mentions-fetcher 5.2 L57; ig-own-comments-fetcher 5.2 L59; li-client-posts-poller 5.2 L58; li-company-posts-poller 5.2 L58; li-own-comments-fetcher 5.2 L59; li-post-search 5.1 L46; tg-channel-posts-poller 5.2 L61; tg-message-search 5.1 L46; yt-channel-resolver 5.2 L60)<br>allow, wait-until, deny (ig-account-media-poller 5.2 L60; x-recent-search 5.2 L55; yt-keyword-search 5.2 L56)<br>allow, wait_until, deny (x-full-archive-search 5.1 L43)<br>wait_until, deny (x-user-timeline-poller 5.2 L56)<br>Allow, Wait-until, deny (yt-text-purger 5.3 L89-L92) |
| `quota-governor answers` | wait-until, deny (tt-client-videos-fetcher 5.1 L47; tt-hashtag-feed-poller 5.2 L56; tt-keyword-search 5.2 L50; tt-profile-videos-poller 5.2 L59; tt-user-resolver 5.2 L54; tt-video-comments-fetcher 5.2 L58; web-gdelt-poller 5.1 L43; web-search-mojeek 5.2 L55; web-search-perplexity 5.2 L53)<br>allow, wait-until, deny (tt-video-stats-refresher 5.1 L50) |
| `quota-governor mode` | stretch, exhausted (x-filtered-stream 7 L155) |
| `raw.items kind` | profile (tg-channel-resolver 5.2 L57) |
| `reaction aliases` | like, love, haha, wow, sad, angry, care (fb-page-feed-poller 5.3 L69-L70) |
| `reaction types` | like, love, haha, wow, sad, angry, care (fb-reactions-fetcher 1 L7) |
| `reason` | no_text (analysis-entities 5.2 L51; analysis-topics 5.2 L55)<br>low_priority_source, unsupported_media (analysis-media 5.3 L60)<br>no_text, unsupported_lang (analysis-sentiment 5.2 L56-L57)<br>platform_sync, retention, author_request, client_offboarding, legal (deletion-propagator 3 L19)<br>add, ops, client (fb-backfill 5.1 L41)<br>rotation, reconciliation, ops_force (fb-page-feed-poller 5.2 L54)<br>seed, weekly (fb-page-search 5.1 L40)<br>age_gated, unclassified (ig-account-resolver 6.2 L127)<br>platform_sync (li-client-posts-poller 5.1 L48; li-notification-receiver 5.4 L97; li-own-comments-fetcher 5.2 L62; li-post-comments-fetcher 5.2 L64; x-compliance-sync 3 L20; yt-comments-fetcher 5.2 L59; yt-pubsub-receiver 5.2 L55; yt-replies-fetcher 5.2 L56; yt-video-details-fetcher 3 L22)<br>vendor_route_off, route_unavailable_government (li-org-resolver 5.2 L53)<br>robots_unreachable, content_signal_search_no (news-robots-checker 5.3 L71)<br>empty_200_rate (source-health-canary 6.2 L102)<br>budget (x-filtered-stream 6.3 L149)<br>rotation, first_run, gap_backfill, ops_force (x-recent-search 5.2 L53)<br>retention, client_offboarding (yt-text-purger 5.3 L106)<br>lease_lapsed (yt-uploads-reconciler 5.1 L51) |
| `reason (emitted)` | retention, author_request, client_offboarding, legal (retention-purger 3 L20) |
| `reason (named)` | review_timeout, route_off, amber_excluded_government (qualifier 5.2 L61) |
| `reason (not_resolved)` | plan_not_enterprise (x-user-resolver 6.2 L132) |
| `reason (unavailable)` | suspended, protected, not_found (x-user-resolver 6.2 L132) |
| `recheck triggers` | 401, 402, 403, 429, 451, 404 or 410 on a feed or sitemap URL (news-robots-checker 5.1 L47) |
| `reconciliation cadence class` | push, dormant, retired (ig-webhook-receiver 5.1 L41) |
| `referenced_tweets.type` | replied_to (x-replies-fetcher 5.2 L60) |
| `removed_fields` | author_id, in_reply_to_user_id, entities.mentions.id, entities.mentions.username, includes.users (x-replies-fetcher 6.2 L128) |
| `render` | headless (news-homepage-differ 5.3 L73) |
| `replay target` | normalize-item, analysis, all (raw-archiver 5.3 L71) |
| `requested_by` | system, client, ops (backfill-orchestrator 6.3 L112)<br>news-article-extractor (news-robots-checker 5.2 L53)<br>ops (raw-archiver 6.2 L113) |
| `reserved X paths` | /i, /home, /search, /hashtag, /intent, /share, /explore (search-hit-router 5.3 L80) |
| `resolution` | resolved, individual, review (ig-account-resolver 2 L13)<br>resolved, unresolved, remembered_reject, grant_missing (li-org-resolver 5.2 L51) |
| `resolutions_total result` | page, individual, error (fb-page-resolver 10 L159)<br>account, individual, unavailable, not_resolved, error (x-user-resolver 10 L161) |
| `resolved_type` | page, individual (fb-page-resolver 5.2 L58)<br>account, individual, unavailable, not_resolved (x-user-resolver 6.2 L115)<br>channel (yt-channel-resolver 6.2 L117) |
| `resolver health` | degraded, ok, fallback_off (poster-resolver 8 L108) |
| `result` | hit, no_hit, skipped (keyword-matcher 2 L17)<br>new, version, metrics_only, parked (normalize-item 5.2 L52) |
| `result (metric)` | ok, skipped, dlq (analysis-sentiment 10 L139) |
| `retention_class` | x_24h_sync, youtube_30d_text, linkedin_48h, meta_on_request, vendor_agreed, news_excerpt (normalize-item 5.3 L75) |
| `review answer` | add (with the reviewer's tier), reject, mention_only (qualifier 5.2 L61) |
| `review reason` | not_returned (ig-account-media-poller 5.2 L64)<br>schema_unknown (normalize-item 5.2 L50) |
| `review_flags` | hidden_subscriber_count, made_for_kids (yt-channel-resolver 5.2 L62) |
| `review_queue entry` | x_terms_screen, x_rule_flood (x-filtered-stream 5.2 L52) |
| `review_queue kind` | kb_candidate, annotation:entities (analysis-entities 5.3 L71)<br>annotation:media (analysis-media 5.3 L70)<br>annotation:sentiment (analysis-sentiment 5.3 L72)<br>annotation:topics (analysis-topics 5.3 L76) |
| `reviewer action` | accept, merge, discard (analysis-topics 5.3 L74) |
| `robots.status` | ok, unavailable (news-robots-checker 6.2 L102) |
| `role` | (values not listed) (news-dedup 6.3 L108) |
| `roles` | ops, client_admin (registry-writer 6.1 L87) |
| `rotation interval` | 30 minutes (priority list), 60 minutes (other client pages) (li-client-posts-poller 3 L19) |
| `route` | amber, green (li-org-resolver 6.2 L90)<br>green, amber (normalize-item 5.3 L65; poster-resolver 9 L119)<br>green (tg-bot-channel-receiver header L3; tg-discussion-receiver header L3)<br>amber (tg-channel-posts-poller 6.2 L112; tg-channel-resolver 6.2 L96; tg-message-search 6.2 L86) |
| `route health` | degraded (ig-comments-fetcher 8 L131; ig-keyword-search 8 L134; li-company-posts-poller 8 L139; li-post-comments-fetcher 8 L145; li-post-search 8 L122) |
| `route health on 401/403` | degraded (fb-group-comments-fetcher 8 L143) |
| `route state on 401/403` | degraded (x-compliance-sync 8 L146) |
| `routing by kind` | comment -> comments, reply -> comments, everything else -> items (posts, videos, articles, messages, quotes, results) (store-writer 5.2 L47) |
| `rule cadence classes` | priority (hourly; keeps its slot when over capacity), standard (hourly; most-stale-first and at least every 24 hours ... (web-gdelt-poller 5.1 L41) |
| `rule kind (tag)` | acct, brand (x-filtered-stream 6.2 L145) |
| `rule priority` | 1, 2, 3 (x-filtered-stream 5.1 L40) |
| `rule type` | volume_spike, negative_share, new_high_reach_poster, keyword_first_seen, post_deleted_high_reach (alert-evaluator 3 L22) |
| `rule_hit` | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 (qualifier 5.2 L52-L61) |
| `run_kind` | live, rerun (analysis-entities 5.1 L46; analysis-media 5.1 L47; analysis-sentiment 5.1 L51; analysis-topics 5.1 L50) |
| `schema_unknown` | schema_unknown (tg-bot-channel-receiver 8 L153; tg-channel-posts-poller 8 L149; tg-channel-resolver 8 L122; tg-discussion-receiver 8 L157; tg-message-search 5.4 L64) |
| `scope` | keyword, keyword_source (alert-evaluator 5.3 L56)<br>item, author, source, client (deletion-propagator 5.3 L60)<br>item, author, client (retention-purger 5.3 L76)<br>non_government (source-health-canary 5.3 L79)<br>item, author (x-compliance-sync 5.3 L73-L77)<br>text_only, derived (yt-text-purger 5.3 L106) |
| `script` | arab, latn, mixed, none (lang-dialect-id 5.2 L51) |
| `search window` | 7 days, 90 days (tg-message-search 5.1 L44) |
| `sentiment` | (labels of analysis-sentiment), pending, unscored (aggregator 5.3 L55) |
| `series outcome` | no_thread (news-comments-fetcher 5.1 L45) |
| `series steps` | +1 h, +6 h, +24 h, +3 d (x-replies-fetcher 5.1 L45) |
| `series_step` | +1 h, +6 h, +24 h, +3 d, +7 d, +14 d, +21 d, +28 d, +30 d, +9 d to +29 d (every 2 days), once, hot:<n>, refresh:<requ... (comment-decay-scheduler 5.1 L46-L60)<br>+1 h, +6 h, +24 h, +3 d, +1h (fb-group-comments-fetcher 5.1 L44)<br>+1 h, +6 h, +24 h, +3 d, +7 d, weekly to day 30, +6h (fb-post-comments-fetcher 5.1 L46)<br>+6h, +24 h, +3 d, every 2 days to day 30 (extension), hourly for 6 hours (hot post) (ig-comments-fetcher 5.1 L43)<br>+1h, +6 h, +24 h, +3 d, +7 d, +14 d, +21 d, +28 d, every 2 days to day 30 (extension), hourly for 6 hours (hot post) (ig-own-comments-fetcher 5.1 L43)<br>+6h (li-own-comments-fetcher 6.2 L115)<br>+24h (li-post-comments-fetcher 6.2 L117)<br>+6h, +24 h, +3 d (news-comments-fetcher 5.1 L43)<br>+1 h, +6 h, +24 h, +3 d, +7 d (tt-video-comments-fetcher 5.1 L43)<br>+24h, +7d (tt-video-stats-refresher 5.1 L42)<br>+6 h, +24 h, +3 d, +7 d, +30 d, +24h (yt-comments-fetcher 5.1 L44; yt-replies-fetcher 5.1 L40)<br>backfill, 24h, 7d, client (yt-video-details-fetcher 5.1 L44) |
| `service_runs marker` | gap_possible (tg-channel-posts-poller 5.1 L50) |
| `severity` | high (alert-evaluator 6.2 L90) |
| `signals` | region_iq, iraqi_place_in_bio, phone_964, iq_domain (tt-user-resolver 6.2 L106) |
| `sitemap classification` | news sitemap, regular sitemap, index (news-site-resolver 5.2 L49) |
| `sitemap types` | news sitemap, regular sitemap, sitemap index (news-sitemap-poller 3 L19) |
| `skipped_policy reason` | robots_path (news-article-extractor 5.2 L52) |
| `source.events consumed` | added, retired, updated (backfill-orchestrator 3 L22) |
| `source.events event types` | updated, added (fb-backfill 5.1 L41)<br>added, updated, retired (tt-client-videos-fetcher 6.1 L90)<br>added, tier change, retired, fallback_on, fallback_off (tt-profile-videos-poller 5.1 L43) |
| `source.events event types read` | added, updated, tier change, retired (fb-client-webhook-receiver 6.1 L105)<br>fallback_on, fallback_off, retired (fb-group-comments-fetcher 6.1 L100)<br>added, tier change, retired, fallback_on, fallback_off (fb-group-posts-poller 6.1 L98)<br>added, tier change, retired (fb-page-feed-poller 6.1 L104; fb-page-resolver 6.1 L95)<br>retired, updated (fb-post-comments-fetcher 6.1 L95) |
| `source.events event types written` | tier change (fb-group-posts-poller 5.2 L61)<br>tier change, updated (fb-page-feed-poller 5.1 L42) |
| `source.events kind written` | updated (x-full-archive-search 6.2 L128) |
| `source.events kinds read` | added (search-hit-router 5.1 L47)<br>retired, tier change (x-filtered-stream 13.2 L192)<br>added, tier change, retired (x-recent-search 6.1 L94; x-user-resolver 6.1 L97)<br>added, tier change, dormant, retired (x-user-timeline-poller 6.1 L108) |
| `source.events kinds written` | tier change, updated (x-user-timeline-poller 6.2 L134) |
| `source.events note` | budget_wait (ig-hashtag-search 5.1 L57) |
| `source.events reason` | push_lease_lapsed (yt-uploads-reconciler 5.1 L51) |
| `source.events type` | updated (tg-bot-channel-receiver 5.2 L72) |
| `source.events types` | added, retired, updated (ig-mentions-fetcher 6.1 L100)<br>added, updated, tier change, retired (news-feed-poller 6.1 L88)<br>added, updated (news-site-resolver 5.1 L41)<br>tier change, fallback_on, fallback_off (tg-channel-posts-poller 5.1 L44) |
| `source.events types read` | added, tier change, retired (ig-account-media-poller 6.1 L100; news-robots-checker 6.1 L89)<br>added, tier change, retired, fallback_on, fallback_off (ig-keyword-search 6.1 L92)<br>added, updated, retired (yt-pubsub-receiver 5.2 L50)<br>added, updated, tier change, dormant, retired (yt-uploads-reconciler 6.1 L104) |
| `source.events types written` | tier change, dormant, updated (ig-account-media-poller 5.2 L63)<br>fallback_on, updated (ig-hashtag-search 5.1 L57)<br>updated (ig-webhook-receiver 5.2 L60)<br>tier change (yt-uploads-reconciler 5.2 L65) |
| `source_type` | keyword_rule (fb-keyword-search 5.1 L40; tg-message-search 5.1 L41; tt-keyword-search 3 L21; x-recent-search 5.1 L39; yt-keyword-search 3 L23)<br>account, creator (ig-account-media-poller 5.1 L42; ig-mentions-fetcher 5.1 L41)<br>keyword_rule, hashtag (ig-keyword-search 5.1 L41)<br>site (news-site-resolver 6.2 L88)<br>account (qualifier 6.2 L84)<br>channel (tg-channel-resolver 3 L29)<br>group (tg-discussion-receiver 5.2 L67)<br>hashtag (tt-hashtag-feed-poller 6.2 L88) |
| `state` | active, superseded, deleted (fb-group-comments-fetcher 6.3 L132; fb-post-comments-fetcher 6.3 L129)<br>connected, reconnecting, disconnected (x-filtered-stream 5.2 L59)<br>requested, active, lapsed, unsubscribing, unsubscribed, failed (yt-pubsub-receiver 6.3 L134) |
| `status` | ok, skipped (analysis-media 6.2 L100; analysis-sentiment 5.2 L56; analysis-topics 5.2 L55)<br>ok (backfill-orchestrator 5.4 L92; comment-decay-scheduler 5.4 L127)<br>scheduled, in_flight, done, stopped_early, cancelled (comment-decay-scheduler 6.3 L147)<br>received, resolved, hidden, erased, recomputed, notified, verified, completed, rejected (deletion-propagator 5.3 L76)<br>active, retracted (keyword-matcher 2 L15)<br>ok, skipped, error (lang-dialect-id 6.2 L105)<br>done, gone, not_article, paywalled, skipped_policy, failed (news-article-extractor 6.3 L129)<br>allowed, disallowed, paywalled, blocked (news-robots-checker 2 L13)<br>candidate (news-site-resolver 5.2 L54)<br>resolving, pending (poster-resolver 5.2 L55)<br>resolved, not_found, not_indexed, private, route_off, amber_excluded (tg-channel-resolver 6.2 L95)<br>pass, fail (x-compliance-sync 5.2 L59; yt-text-purger 6.2 L173)<br>done, capped (x-full-archive-search 5.1 L41)<br>quota_denied, not_root, outside_window, not_permitted, cursor_rejected (x-replies-fetcher 5.2 L53-L55)<br>quota_denied, comments_disabled, video_not_found (yt-comments-fetcher 5.2 L53)<br>unchanged, quota_denied, comments_disabled, thread_not_found (yt-replies-fetcher 5.1 L42) |
| `step outcome counter` | missed (comment-decay-scheduler 5.3 L106) |
| `strata` | facebook, tiktok, instagram, youtube, telegram, x, linkedin, news, Iraqi, other Arabic, Modern Standard Arabic, Soran... (analysis-sentiment 5.3 L74) |
| `stream state read` | disconnected (x-user-timeline-poller 5.1 L42) |
| `stretch order` | backfill, views refreshes, Tier 2, Tier 1 (tg-channel-posts-poller 5.1 L52) |
| `subscription condition / alert` | subscription_silent, grant_lost (li-notification-receiver 5.1 L42) |
| `task` | media_fetch, media_ocr, media_tags, media_asr, media_logo (analysis-media 5.3 L74)<br>sentiment, sentiment_aspect (analysis-sentiment 6.2 L89)<br>topics:<taxonomy_id>, topics:global, topic_cluster (analysis-topics 5.2 L60) |
| `taxonomy_nodes.status` | zero_shot, supervised, retired (analysis-topics 5.3 L68) |
| `tier` | push, dormant, retired, 1, 2, 3 (fb-client-webhook-receiver 5.1 L42; yt-pubsub-receiver 5.1 L40)<br>1, 2, 3, dormant, retired (fb-group-posts-poller 5.1 L42; ig-hashtag-search 5.1 L47-L53; ig-keyword-search 5.1 L43; news-feed-poller 5.1 L42; x-user-timeline-poller 5.1 L38)<br>dormant, retired (fb-keyword-search 5.1 L42)<br>1, 2, 3, push, dormant, retired (fb-page-feed-poller 5.1 L42; ig-account-resolver 5.1 L44; ig-mentions-fetcher 5.1 L43; tg-channel-posts-poller 3 L19)<br>retired, dormant, push (fb-page-resolver 5.1 L46)<br>Tier 1, Tier 3, dormant, retired (li-company-posts-poller 5.1 L43)<br>1, 2, 3, dormant (li-org-resolver 5.1 L46)<br>1, 2, 3, push, dormant (qualifier 5.2 L54)<br>push, dormant, retired (tg-bot-channel-receiver 5.1 L44; tg-discussion-receiver 5.1 L47)<br>push (tt-client-videos-fetcher 5.1 L43)<br>1, 2, 3, dormant, retired, push (x-filtered-stream 5.1 L40) |
| `tier (creators)` | Tier 1, Tier 2, Tier 3, Push, Dormant, Retired (tt-profile-videos-poller 3 L19) |
| `tier (hashtags)` | Tier 1, Tier 2, Tier 3, Dormant, Retired (tt-hashtag-feed-poller 5.1 L42) |
| `tier (keyword rule)` | 1, 2, 3, dormant, retired (x-recent-search 5.1 L41) |
| `tier (keyword rules)` | Tier 1, Tier 2, Tier 3, Dormant, Retired (tt-keyword-search 5.1 L40)<br>1 (priority, every 12 hours), 2 (standard, every 24 hours), 3 (standard, every 24 hours) (web-search-mojeek 5.1 L42; web-search-perplexity 5.1 L41)<br>1, 2, 3 (yt-keyword-search 5.1 L46)<br>2, 3 (yt-web-search-bridge 3 L21) |
| `tier cadence` | 1, 2, 3, push, dormant, retired (ig-account-media-poller 5.1 L44) |
| `tier_down steps` | 1->2, 2->3, 3->dormant (qualifier 5.2 L60) |
| `token health` | healthy, degraded (fb-page-feed-poller 5.2 L55; fb-page-resolver 5.2 L55; fb-page-search 5.2 L51; fb-reactions-fetcher 5.2 L53)<br>degraded (fb-post-comments-fetcher 8 L141; ig-account-media-poller 8 L141; ig-account-resolver 8 L145; ig-hashtag-search 5.2 L64; ig-mentions-fetcher 8 L143; ig-own-comments-fetcher 8 L145) |
| `token state` | degraded (li-client-posts-poller 8 L142) |
| `topic_id special value` | unassigned (aggregator 5.3 L55) |
| `topics[].source` | supervised, zero_shot (analysis-topics 5.3 L72) |
| `trigger` | daily (x-compliance-sync 5.2 L51)<br>retention_sweep (yt-text-purger 6.2 L164) |
| `type` | individual (li-org-resolver 3 L32)<br>verdict, story_update (news-dedup 6.2 L89)<br>channel (tg-bot-channel-receiver 5.2 L70) |
| `unresolvable reason` | route_off, timeout (poster-resolver 5.2 L56) |
| `unroutable reason` | private_invite (search-hit-router 13.3 L183) |
| `unthreaded` | true, false (tg-discussion-receiver 5.2 L62) |
| `usage_signals values` | yes, no, unset (news-robots-checker 5.3 L73) |
| `variant forms` | Arabic forms, Kurdish (Sorani) forms, brand handles (fb-keyword-search 3 L20) |
| `vendor` | apify_tugelbay, apify_sovereigntaylor (tg-channel-posts-poller 6.2 L112)<br>telemetrio (tg-channel-resolver 4 L34; tg-message-search 6.2 L87)<br>tikhub, ensembledata (tt-hashtag-feed-poller 6.1 L75; tt-keyword-search 6.1 L69; tt-profile-videos-poller 1 L9; tt-user-resolver 1 L9; tt-video-comments-fetcher 1 L9; tt-video-stats-refresher 1 L9) |
| `vendor_keys plan (storable)` | Business, Enterprise (web-search-mojeek 5.1 L50) |
| `verb` | add, edited, remove (fb-client-webhook-receiver 5.2 L56) |
| `verdict` | resolved, unavailable (yt-channel-resolver 2 L13) |
| `verification check` | archive_rewrite, text_index, aggregator_job (deletion-propagator 6.2 L102-L104) |
| `weak input outcome` | dedup_weak_input (news-dedup 8 L120) |
| `webhook event` | deletion.completed (deletion-propagator 5.3 L72) |
| `webhook field` | comments, mentions (ig-webhook-receiver 1 L7) |
| `worker pool` | urgent (platform_sync, legal), bulk (retention, author_request, client_offboarding) (deletion-propagator 5.1 L43) |
| `X compliance job status` | created, in_progress, complete, failed, expired (x-compliance-sync 5.3 L67) |
| `X compliance job type` | tweets, users (x-compliance-sync 5.3 L65) |
| `X sub-counters` | post_reads, user_reads (quota-governor 5.3 L78) |
| `X_PLAN` | enterprise (x-user-resolver 5.2 L54) |
| `YouTube buckets` | search, ingest, comments, reserve (quota-governor 5.3 L79) |
| `YouTube error reason` | quotaExceeded (yt-keyword-search 8 L139) |

## 10. Internal calls between services

Calls that are neither topics nor job queues (allowance requests, health reads, HTTP endpoints, SDK helpers), grouped by the service or component called. Shapes are cut at 160 characters.

| Counterparty | Call as named | Callers or exposers (direction) | Shape as written (first) |
|---|---|---|---|
| (not stated) | /healthz and /metrics | fb-page-search (exposes), tt-hashtag-feed-poller (exposes), tt-keyword-search (exposes) | HTTP health and Prometheus endpoints |
| (not stated) | backfill report | tt-profile-videos-poller (calls) | after a backfill job, reports `oldest_seen` and `pages` |
| (not stated) | client reconnect notice | tt-client-videos-fetcher (calls) | notify the client to reconnect when a refresh fails; authorisation lapsing or revoked is reported to the client |
| (not stated) | cost_units report | tt-hashtag-feed-poller (calls), tt-keyword-search (calls) | reports `cost_units` (HTTP 200 responses) after the batch is acknowledged |
| (not stated) | job report | ig-hashtag-search (calls) | items_fetched, items_new, pages, cost_units (one unit per call) |
| (not stated) | ops and client notification | fb-client-webhook-receiver (calls) |  |
| admin page | admin and coverage page notices | tg-channel-posts-poller (calls) | the admin page tells clients when freshness has been relaxed; the coverage page says when the route is off |
| admin page | budget pause notice | web-search-mojeek (triggers), web-search-perplexity (triggers) | on a monthly deny the admin page tells the client that web coverage is paused for budget (mechanism not stated) |
| aggregator | aggregator job status | deletion-propagator (reads) | wait for recompute job 'done' |
| aggregator | aggregator watermark | alert-evaluator (reads) | poll service_runs.last_success_at every ALERT_POLL_SECONDS; evaluate when it moves; at least every 300 s |
| alert-evaluator | update watermark | aggregator (exposes) | service_runs.last_success_at and hours touched per pass; alert-evaluator evaluates on each move |
| analysis-entities | analysis-entities brand ids | analysis-media (uses) | brand ids for logos (optional) |
| analysis-media | media_url hand-off | ig-hashtag-search (calls) | media_url 'handed to analysis-media promptly' |
| analysis-media and the fetch services | media endpoint (PUT) | raw-archiver (exposes) | bytes plus item_id, retention_class, expires_at -> media/<sha256> and a reference in .refs; path not named |
| Apify platform (vendor) | Apify run completion | tg-channel-posts-poller (calls) | start one Actor run per batch, wait for completion, read the dataset in pages until exhausted; 'Run mode (wait or webhook)' is to be confirmed in the pilot |
| Argilla or Label Studio (self-hosted) | annotation tool | analysis-sentiment (calls) | review_queue rows point to tasks; corrected labels feed a weekly retrain |
| backfill-orchestrator | backfill completion report | ig-account-media-poller (calls), ig-keyword-search (calls), ig-mentions-fetcher (calls) | reports `done` or `capped` after a backfill job |
| backfill-orchestrator | backfill report | news-sitemap-poller (reports_to) | coverage_days, urls_emitted and the done signal (channel not stated) |
| budgets (Postgres) | usage header recording into budgets | fb-page-feed-poller (calls) | X-App-Usage, X-Business-Use-Case-Usage values recorded |
| ClickHouse | ClickHouse sweep query | qualifier (calls) | SELECT source_id, max(published_at) FROM items GROUP BY source_id (sources not retired) |
| client app (client_admin), ops | client re-run endpoint | backfill-orchestrator (exposes) | re-run request for a source; 403 when the source is not in the client's client_sources; path not named |
| client app / ops | qualifier_config API with bounds check | qualifier (exposes) | rejects values outside the section 7 bounds with a bounds error |
| client app, ops | client refresh request | comment-decay-scheduler (receives) | refresh of one post after day 30 -> one comments job with series_step = refresh:<request_id>; path not named |
| client endpoints | client webhook deletion.completed | deletion-propagator (calls) | HMAC-signed; item references the client knows, reason category, time; never text or author data; retries 30 s to 15 min, 5 attempts |
| client systems | client webhooks | alert-evaluator (calls) | POST alert/v1 with HMAC signature, timestamp and Idempotency-Key: <alert_id>:<channel>; HTTP 410 disables the endpoint |
| client token stores / Vault | token revocation | retention-purger (calls) | revoke the client's tokens, delete Vault secrets and vendor_keys rows on offboarding |
| cluster | readiness | lang-dialect-id (exposes) | not ready until all models are loaded; path not named |
| cluster / Prometheus | /healthz and /metrics | li-org-resolver (exposes), yt-keyword-search (exposes), yt-web-search-bridge (exposes) | health and Prometheus metrics endpoints |
| cluster and Prometheus | /healthz and /metrics | web-commoncrawl-scanner (exposes), web-gdelt-poller (exposes), web-search-mojeek (exposes), web-search-perplexity (exposes) | HTTP health and Prometheus metrics endpoints |
| cluster and Prometheus | /healthz, /metrics | news-site-resolver (exposes) | /healthz, /metrics; structured JSON logs with job_id, source_id, route, vendor |
| comment-decay-scheduler | client refresh request | yt-comments-fetcher (mention) | a client can request a refresh of one video through comment-decay-scheduler, budget permitting |
| comment-decay-scheduler | completion message | tt-video-comments-fetcher (calls), tt-video-stats-refresher (calls) | {new_count, seen_count, pages, cost_units, comments above the reply threshold} after Redpanda acknowledges |
| comment-decay-scheduler | fetch report | fb-group-comments-fetcher (calls), fb-post-comments-fetcher (calls) | {new_count, seen_count, pages, cost_units, stored_before, complete, reply_threads} |
| comment-decay-scheduler | job result report | ig-comments-fetcher (calls), li-own-comments-fetcher (calls), li-post-comments-fetcher (calls) | new_count, seen_count, pages, cost_units after Redpanda acknowledges; status skipped when flag off or government client |
| comment-decay-scheduler | job return statuses | tt-video-comments-fetcher (calls) | `skipped_flag_off` (series not marked failed); `video_gone` (series cancelled) |
| comment-decay-scheduler | post-gone notice | fb-group-comments-fetcher (calls) | stop that post's series |
| comment-decay-scheduler | pushed comment count per post | ig-webhook-receiver (exposes) | count of pushed comments per post for the early-stop, extension and hot-post rules |
| comment-decay-scheduler | result row for the scheduler | news-comments-fetcher (reports_to) | service_runs row with new_count, seen_count, pages, cost_units, thread_id, newest_comment_at after Redpanda acknowledges |
| comment-decay-scheduler (and ops) | post_unavailable notice | fb-post-comments-fetcher (calls) | stop that post's series |
| comment-decay-scheduler (via the control-plane client) | job result through the control-plane client | ig-own-comments-fetcher (calls) | new_count, seen_count, pages, cost_units, incomplete reply threads; recorded only after Redpanda acknowledges |
| comment-decay-scheduler, backfill-orchestrator, every amb... | mode and stretch_factor publication | quota-governor (exposes) | readers read the mode (budgets) |
| control plane (account managers, clients) | taxonomy editing | analysis-topics (receives) | edits taxonomy_nodes; validation rejects sensitive nodes |
| control plane (admin page) | admin page onboarding | tg-bot-channel-receiver (uses) | owner enters the channel username or chooses 'private channel'; the control plane creates an onboarding record with a one-time code and a pre-allocated sourc... |
| control plane (admin page) | admin page onboarding step two | tg-discussion-receiver (uses) | after the channel is verified, the page shows the instruction to add the discussion bot to the linked group as a member with read access to all messages |
| control plane (client brand managers) | logo reference upload | analysis-media (receives) | reference logo sets per client |
| CPU workers (gazetteer), Hetzner GPU pool or screened mod... | model serving | analysis-entities (calls) | NER and linking |
| curators (ops, account managers) and clients | KB curation | analysis-entities (receives) | maintain kb_entities and kb_aliases; review kb_candidate rows |
| deletion-propagator | deletion-propagator text_only / derived execution | yt-text-purger (calls) | via deletions: ReplacingMergeTree null version guarded by fetched_before, forced partition merge, text-index removal, cache purge, raw-archiver rewrite; purg... |
| deletion-propagator | rewrite endpoint | raw-archiver (exposes) | rewrite an archive partition; path and shape not named |
| every calling service | report | quota-governor (exposes) | after the call: actual units, provider usage headers (X-App-Usage, X-Business-Use-Case-Usage), billed true\|false -> settle the reservation |
| every calling service via the listening-sdk quota hook | allowance request (decide) | quota-governor (exposes) | request {budget_tag, amount, service, priority} + optional sub_counter, resource_ids, job_id, request_id -> response {decision, wait_until, remaining} + char... |
| FB_VENDOR_ROUTE (configuration) | flag read | fb-group-comments-fetcher (calls), fb-group-posts-poller (calls), fb-keyword-search (calls) | read at the start of every job |
| flag store (not stated) | TG_POSTS_ACTOR flag read | tg-channel-posts-poller (reads) | read at the start of every batch, never cached; switched by ops or by the canary where ops has approved |
| flag store (not stated) | TG_VENDOR_ROUTE flag read | tg-channel-resolver (reads), tg-message-search (reads) | read at the start of every job |
| Hetzner GPU pool or model API (Hugging Face Inference End... | model serving | analysis-sentiment (calls) | inference per route (Arabic, Sorani, aspect) |
| Hetzner GPU pool or screened model API | model serving | analysis-topics (calls) | supervised heads, zero-shot encoder or NLI, clustering |
| ig-own-comments-fetcher, ig-mentions-fetcher | job results of the two fetching services | ig-webhook-receiver (calls) | reconciliation results; next due time set when both report |
| ig-webhook-receiver (what it stored) | webhook-versus-poll comparison | ig-mentions-fetcher (calls) | reconciliation compares its reads with what ig-webhook-receiver stored; the difference goes to missed_push_total |
| Instagram Graph API (external) | Graph hashtag id lookup | ig-hashtag-search (calls) | GET /ig_hashtag_search?user_id=<ig-user-id>&q=<tag>, once per hashtag |
| keyword-matcher (and CI tools) | POST /v1/fold | lang-dialect-id (exposes) | {items: [{text, lang}]} with explicit lang (ar \| ckb \| en), never detects -> text_norm from the same code |
| keyword-matcher, pollers, backfill-orchestrator | SDK control-plane client | registry-writer (mention) | updates only the caller's operational columns with short transactions, never FOR UPDATE |
| lang-dialect-id | lang-dialect-id (transcripts) | analysis-media (calls) | transcript text -> lang and dialect; endpoint not named |
| lang-dialect-id | lang-dialect-id /v1/fold (for search queries) | store-writer (mention) | search terms must be folded with /v1/fold before querying text_norm |
| lang-dialect-id | lang-dialect-id detect | normalize-item (calls) | POST /v1/detect with the batch texts -> lang, lang_conf, dialect, dialect_conf, script, text_norm, lang_model_version |
| lang-dialect-id | lang-dialect-id folding | analysis-entities (uses) | aliases folded with the same folding as text_norm; endpoint not named |
| lang-dialect-id | lang-dialect-id language shares for profile samples | poster-resolver (calls) | send up to 20 recent post texts -> language shares; endpoint not named (14 asks batch call vs in-process SDK classifier) |
| lang-dialect-id | lang-dialect-id POST /v1/fold | keyword-matcher (calls) | fold every keyword form and exclusion under both Arabic and Sorani folds; SDK TypeScript fold when down |
| lang-dialect-id | language share | news-site-resolver (calls) | language share over the last 20 titles (call shape not stated) |
| LinkedIn | webhook validation handshake GET (same path) | li-notification-receiver (exposes) | GET with a challenge parameter -> 200 with the challenge and its HMAC-SHA256 under the app's client secret (parameter names to be confirmed) |
| LinkedIn (Organization Social Action Notifications) | webhook endpoint POST <our webhook host>/linkedin/organization-social-actions | li-notification-receiver (exposes) | HTTPS only, path to be set; signature header (name to be confirmed); body one or more events; responses 2xx after Redpanda ack, 401 bad signature, 400 malfor... |
| listening-sdk | author_hash helper | x-compliance-sync (calls) | author_hash(X user id) with AUTHOR_HASH_KEY from Vault |
| listening-sdk | engine adapter contract | web-search-mojeek (implements), web-search-perplexity (implements) | the engine is one adapter behind the listening-sdk contract |
| listening-sdk | host gate | news-article-extractor (uses), news-feed-poller (uses), news-homepage-differ (uses), news-robots-checker (uses), news-sitemap-poller (uses) | concurrency 1 per host across all news services; 2 to 5 seconds between requests (or Crawl-delay if larger); after a 429 or 503 the spacing for that host dou... |
| listening-sdk | job contract in the SDK | fb-reactions-fetcher (calls) |  |
| listening-sdk | listening-sdk | yt-keyword-search (calls) | adapter contract, envelope, governor client |
| listening-sdk | listening-sdk adapter contract | tg-channel-posts-poller (uses) | each Actor has its own input mapper behind the listening-sdk adapter contract |
| listening-sdk | listening-sdk adapter contract hashtagFeed | tt-hashtag-feed-poller (calls) | hashtagFeed(hashtag_id, cursor) → {items[], next_cursor, raw} |
| listening-sdk | listening-sdk adapter contract search | tt-keyword-search (calls) | search(query, country, cursor) → {items[], next_cursor, raw} |
| listening-sdk | listening-sdk Apify client, LinkedIn client, pinned Actor schema and LinkedIn... | li-org-resolver (calls) | Actor input keys per the published schema pinned in listening-sdk; LinkedIn-Version pinned in the SDK |
| listening-sdk | listening-sdk author_hash / item_id helpers | retention-purger (uses) | same helper as normalize-item |
| listening-sdk | listening-sdk canary hook / adapters in canary mode | source-health-canary (uses) | same code path as the real fetch, read-only, small page; keeps counts, newest timestamp, latency, status |
| listening-sdk | listening-sdk idempotency helper | yt-uploads-reconciler (calls) | check youtube:post:<video id> for newer video ids |
| listening-sdk | listening-sdk idempotency helper (seen ledger) | yt-pubsub-receiver (calls) | per video last_updated and version, kept 90 days |
| listening-sdk | listening-sdk item_id derivation and purge registry | deletion-propagator (uses) | same item_id helper as normalize-item; registry of text-holding stores |
| listening-sdk | listening-sdk job schema | ig-account-resolver (calls) | job schema gains `kind = resolve` |
| listening-sdk | listening-sdk job wrapper | x-replies-fetcher (calls) | writes jobs.completed/v1 when the job finishes |
| listening-sdk | listening-sdk mapper table, key derivation, folding rules, envelope | normalize-item (uses) | mappers versioned by normalizer_version; item_id derivation shared with deletion-propagator and retention-purger |
| listening-sdk | listening-sdk pinned Actor input schema | li-company-posts-poller (calls), li-post-comments-fetcher (calls), li-post-search (calls) | the Actor's input schema is pinned in listening-sdk |
| listening-sdk | listening-sdk rate limiter | tt-hashtag-feed-poller (calls), tt-keyword-search (calls), tt-profile-videos-poller (calls) | enforces 10 requests a second per endpoint |
| listening-sdk | listening-sdk row builders and version formula | store-writer (uses) | row builders and row_version formula |
| listening-sdk | listening-sdk Telegram client | tg-bot-channel-receiver (uses) | a contract test over the SDK client shows the service never calls a method that posts, edits or deletes in a channel |
| listening-sdk | SDK raw emit helper | raw-archiver (uses) | allocates raw_ref; rolls keys below the archiver's limits; strips tokens before emission |
| listening-sdk | shared /feed field list and envelope (SDK constant) | fb-backfill (calls) | field list byte-identical to fb-page-feed-poller's |
| listening-sdk | shared canonicaliser | search-hit-router (uses), web-gdelt-poller (uses), web-search-mojeek (uses), web-search-perplexity (uses) | recompute the canonical URL hash and compare it with the message's |
| listening-sdk | shared classifier | search-hit-router (uses) | URL -> platform, type, poster reference and candidate_key per the 5.3 table |
| listening-sdk | shared query-variant generator | web-search-mojeek (uses), web-search-perplexity (uses) | keywords row -> 9 query variants in the same slot order as web-search-perplexity |
| listening-sdk (analytics store) | stored comment lookup | news-comments-fetcher (calls) | stored comment ids and content hashes for the article, through the SDK |
| listening-sdk (clients shared with web-search-perplexity ... | listening-sdk shared vendor clients | yt-web-search-bridge (calls) | the client owns the exact request shape |
| listening-sdk (model lang-dialect-id runs) | listening-sdk language client | li-org-resolver (calls) | language share of the sampled posts |
| listening-sdk / normalize-item fallback | listening-sdk TypeScript fold | lang-dialect-id (uses) | TypeScript copy of the fold table; conformance suite keeps it identical to /v1/fold |
| listening-sdk / raw-archiver archive | SDK raw reader / per-platform extractor | keyword-matcher (uses) | read platform_id and handle from the raw record at raw_ref |
| listening-sdk / React rule editor | listening-sdk rule validation | alert-evaluator (uses) | same validation in the editor and the evaluator |
| listening-sdk / source-health-canary | SDK canary hook (health read) | yt-channel-resolver (calls), yt-comments-fetcher (calls), yt-replies-fetcher (calls), yt-uploads-reconciler (calls) | reads health |
| listening-sdk / source-health-canary | SDK canary hook (health) | li-client-posts-poller (calls), li-company-posts-poller (calls), li-own-comments-fetcher (calls) | health read through the SDK canary hook |
| listening-sdk job wrapper | jobs.completed/v1 writer | x-full-archive-search (calls), x-user-timeline-poller (calls) | writes jobs.completed/v1 with status, new_count, seen_count, pages, cost_units (+ post_ref, series_step, end_time for replies) |
| listening-sdk job wrapper | listening-sdk job wrapper report | yt-comments-fetcher (calls), yt-replies-fetcher (calls) | service returns {new_count, seen_count, pages, cost_units, reply_candidates, status}; the wrapper writes jobs.completed/v1 |
| Meta | GET /webhooks/instagram (handshake) | ig-webhook-receiver (exposes) | ?hub.mode=subscribe&hub.verify_token=<token>&hub.challenge=<value> -> 200 with body = hub.challenge if the token matches, else 403 |
| Meta | POST /webhooks/instagram (notifications) | ig-webhook-receiver (exposes) | X-Hub-Signature-256 checked -> 200 (empty body) once durably appended to jobs.ig-webhook-receiver; 403 on a bad signature; 500 if the append fails |
| Meta Graph (external) | subscription management | ig-webhook-receiver (calls) | daily check per account of the comments and mentions subscription; re-create a lost one |
| Meta Webhooks | GET /webhooks/facebook | fb-client-webhook-receiver (exposes) | query hub.mode, hub.verify_token, hub.challenge -> 200 with hub.challenge as plain text when hub.mode = subscribe and the token matches; otherwise 403 |
| Meta Webhooks | POST /webhooks/facebook | fb-client-webhook-receiver (exposes) | JSON body {object, entry[]} with X-Hub-Signature-256: sha256=<hex> -> 403 on signature mismatch; 200 only after Redpanda acknowledges each entry; 5xx when Re... |
| n8n | n8n alerts | quota-governor (calls) | budget_50, budget_80, budget_95, budget_exhausted, x_enterprise_required, quota_deny_rate, drift_detected, governor_unreachable |
| n8n | n8n alerts and approval cards | source-health-canary (calls) | alerts on flips; approval card on blocked (default after 24 hours: no fallback) |
| n8n | n8n approval cards | li-post-search (calls) | ops receive rotation and budget alerts and n8n approval cards |
| n8n | n8n client notifications | qualifier (calls) | queued candidates and amber_excluded_government notices to the client / account manager |
| n8n | n8n flows (email, Telegram, Slack) | alert-evaluator (calls) | signed webhook call with the alert/v1 payload |
| n8n | n8n request notifications | registry-writer (calls) | notification of the manual request outcome |
| n8n | n8n review callback | qualifier (receives) | reviewer's choice, identity and time; signed with a secret from Supabase Vault |
| n8n | n8n review card | li-org-resolver (calls) | card for missing grants (Posts API 403, resolution = grant_missing) or name-only candidates for ops to supply the URL |
| n8n | n8n webhook POST /qualifier/review | qualifier (calls) | card payload: candidate summary, signals found, matched keywords, client, buttons Approve as tier 1/2/3, Reject, Mention only |
| n8n (ops) | audit export | x-compliance-sync (receives) | export request for a client or for X and a date range -> CSV and JSON Lines with a SHA-256 manifest |
| n8n / authors | deletion channel (n8n intake form and mailbox) | retention-purger (receives) | creates a deletion_requests row with the requester's contact and the author's handle or profile URL |
| news-robots-checker | policy request | news-site-resolver (calls) | enqueue jobs.news-robots-checker, then wait for the host's crawl.policies message or read an unexpired crawl_policies row |
| news-site-resolver | not_article rate per site | news-article-extractor (reports_to) | outcome counts (not_article rate per site) for pattern refinement (channel not stated) |
| normalize-item (only caller, incl. lang_rescore and replay) | POST /v1/detect | lang-dialect-id (exposes) | request per record {record_id, kind, title, text} (batch up to 500; author, source, client fields rejected) -> {lang_model_version: string, results[]: {recor... |
| not named in this PRD | per-host politeness | news-site-resolver (uses) | per-host concurrency 1; 2 to 5 seconds between requests, or the policy's Crawl-delay if larger; If-None-Match and If-Modified-Since on URLs seen before |
| not stated | client notification | tg-channel-resolver (calls), tg-message-search (calls) | government-owned candidate: the client is told to ask the channel owner to add the bot; over the route cap new sources queue by reach and the client is told;... |
| not stated | ops and client notification | tg-bot-channel-receiver (calls), tg-discussion-receiver (calls) | lost administrator role notifies ops and the client; an unregistered chat alerts ops once per chat |
| ops | GET /v1/replays/{run_id} | raw-archiver (exposes) | progress |
| ops | ops force reconcile / gap fill | x-filtered-stream (receives) | force a full reconcile or a gap fill for a stated window; mechanism not stated |
| ops | ops force step | comment-decay-scheduler (receives) | force a step; mechanism not named |
| ops | ops pause target / force probe | source-health-canary (receives) | pause a target or force a probe; mechanism not named |
| ops | ops split command | news-dedup (called_by) | re-assigns the members of a wrongly merged story and publishes story_update for each; the decision is logged in decisions (shape not stated) |
| ops | POST /v1/replays/{run_id}/cancel | raw-archiver (exposes) | stop a run |
| ops | section pinning | news-homepage-differ (called_by) | ops pin section pages for a site; proposed storage in the cursor's sections |
| ops (control plane) | ops force one rule | x-recent-search (receives) | force one rule from the control plane (job reason ops_force); mechanism not stated |
| ops (n8n flow) | candidate intake from ops | news-site-resolver (called_by) | candidates and seed lists submitted through an n8n flow (shape not stated) |
| ops (Prometheus) | /healthz and /metrics | tg-channel-resolver (exposes), tg-message-search (exposes) | HTTP endpoints |
| ops (Supabase auth) | POST /v1/replays | raw-archiver (exposes) | {platform, service?, route?, from, to (UTC dates), item_ids?, target: normalize-item\|analysis\|all, reason, rate_cap_per_s, dry_run} -> run_id and planned c... |
| ops / account managers | backtest job | alert-evaluator (exposes) | dry run of a rule over stored hourly aggregates, reports how many alerts would have fired; queue not named |
| ops admin page, client app | GET /registry/requests/{request_id} | registry-writer (exposes) | request status (e.g. 'already watched') |
| ops admin page, client app | POST /registry/sources | registry-writer (exposes) | {platform, url_or_handle, client_id, tier_override?, priority?, owned_by_client?, notes} -> request_id; HTTP 422 with the failed rule |
| ops and qualifier | unreadable-channel report | tg-channel-posts-poller (calls) | repeated unreadable-channel failures raise consecutive_errors and are reported to ops and the qualifier |
| platform CDN URLs | media download | analysis-media (calls) | plain HTTP GET of media[].url; no accounts, no proxies, no CAPTCHA solving; 5 attempts |
| poster-resolver | job return status skipped_flag_off | tt-user-resolver (calls) | with the flag off the job is returned as `skipped_flag_off`; poster-resolver keeps the candidate waiting |
| PubSubHubbub hub | GET /webhooks/youtube | yt-pubsub-receiver (exposes) | verification: hub.challenge echoed as plain text with 200 if the topic matches a registered channel with an outstanding request; otherwise 404 |
| PubSubHubbub hub | POST /webhooks/youtube | yt-pubsub-receiver (exposes) | Atom XML; 2xx after Redpanda acknowledgement, 5xx if Redpanda is down, 403 on signature mismatch, bodies above MAX_BODY_BYTES rejected |
| qualifier | capacity query | quota-governor (exposes) | capacity for new sources under rule 5; shape not stated here |
| quota-governor | proxy egress allowance | news-robots-checker (calls) | one egress attempt 'allowed by quota-governor under news_proxy_egress' (call shape not stated) |
| quota-governor | proxy egress metering | news-article-extractor (calls), news-feed-poller (calls), news-homepage-differ (calls), news-site-resolver (calls), news-sitemap-poller (calls) | metered under news_proxy_egress (call shape not stated) |
| quota-governor | quota-governor | yt-pubsub-receiver (mention) | no request ever |
| quota-governor | quota-governor allowance | fb-backfill (calls), fb-client-webhook-receiver (calls), fb-group-comments-fetcher (calls), fb-group-posts-poller (calls), fb-keyword-search (calls), fb-page-feed-poller (calls), fb-page-resolver (calls), fb-page-search (calls), fb-post-comments-fetcher (calls), fb-reactions-fetcher (calls), ig-account-media-poller (calls), ig-account-resolver (calls), ig-comments-fetcher (calls), ig-hashtag-search (calls), ig-keyword-search (calls), ig-mentions-fetcher (calls), ig-own-comments-fetcher (calls), li-client-posts-poller (calls), li-company-posts-poller (calls), li-notification-receiver (calls), li-org-resolver (calls), li-own-comments-fetcher (calls), li-post-comments-fetcher (calls), li-post-search (calls), news-comments-fetcher (calls), source-health-canary (calls), tg-bot-channel-receiver (none), tg-channel-posts-poller (calls), tg-channel-resolver (calls), tg-discussion-receiver (none), tg-message-search (calls), tt-client-videos-fetcher (calls), tt-hashtag-feed-poller (calls), tt-keyword-search (calls), tt-profile-videos-poller (calls), tt-user-resolver (calls), tt-video-comments-fetcher (calls), tt-video-stats-refresher (calls), web-commoncrawl-scanner (none (explicitly not called)), web-search-mojeek (calls), web-search-perplexity (calls), x-compliance-sync (calls), x-full-archive-search (calls), x-recent-search (calls), x-replies-fetcher (calls), x-user-resolver (calls), x-user-timeline-poller (calls), yt-channel-resolver (calls), yt-comments-fetcher (calls), yt-keyword-search (calls), yt-replies-fetcher (calls), yt-text-purger (calls), yt-uploads-reconciler (calls), yt-video-details-fetcher (calls), yt-web-search-bridge (calls) | ask allowance under budget_tag = meta_graph_pages:<client_id> for the first page and before every further page; wait-until -> requeue with that time (Page st... |
| quota-governor | quota-governor allowance (analysis_model_api) | analysis-entities (calls), analysis-media (calls), analysis-sentiment (calls), analysis-topics (calls) | only if a model API is chosen |
| quota-governor | quota-governor allowance (pacing) | web-gdelt-poller (calls) | request under gdelt_doc_api for 1 request -> allowance \| wait-until (holds the job; keeps request starts at least 5 seconds apart across all replicas) \| de... |
| quota-governor | quota-governor budget mode | backfill-orchestrator (reads) | budget mode per route via budgets (mode) |
| quota-governor | quota-governor consumed-items report | li-post-search (calls) | report consumed items after the run |
| quota-governor | quota-governor cost report | li-company-posts-poller (calls), yt-keyword-search (calls) | after Redpanda acknowledges, report cost_units (items returned) |
| quota-governor | quota-governor daily quota report | yt-comments-fetcher (calls) | 403 daily quota exhausted is reported to quota-governor; job requeued at its wait-until |
| quota-governor | quota-governor deny until reset | yt-channel-resolver (calls) | a 403 reporting the daily quota spent tells quota-governor to deny youtube_data_api until reset |
| quota-governor | quota-governor exhausted bucket | yt-video-details-fetcher (calls) | a quota-exhausted 403 is reported as an exhausted bucket; key stays healthy |
| quota-governor | quota-governor mode | x-filtered-stream (calls) | reads the governor's mode; a mode change triggers a reconcile; mechanism not stated |
| quota-governor | quota-governor POST /capacity | qualifier (calls) | {route, platform, vendor, client_id, tier} -> {fits: true\|false, reason, queue_position} |
| quota-governor | quota-governor quotaExceeded report | yt-keyword-search (calls) | 403 quotaExceeded reported; governor marks the YouTube budget exhausted for every service; no retry before the governor's next day boundary |
| quota-governor | quota-governor settle | x-filtered-stream (calls) | {budget_tag: x_pay_per_use, amount: <posts>, service: x-filtered-stream, priority: <highest matched>, sub_counter: post_reads, resource_ids: [<post ids>]} ->... |
| quota-governor | quota-governor unit report | li-org-resolver (calls) | report units after the run |
| quota-governor | quota-governor usage report | web-gdelt-poller (calls), web-search-mojeek (calls), web-search-perplexity (calls) | cost_units = 1 per request after acknowledgement |
| quota-governor | quota-governor wait-until on quota exhausted | yt-replies-fetcher (calls) | 403 quota exhausted requeues at quota-governor's wait-until |
| quota-governor | read ledger check-and-mark | x-replies-fetcher (calls) | mark each returned post (`x:post:<id>`) -> paid = true on first read of the UTC day, false on repeats; user objects under user_reads; atomic |
| quota-governor | read ledger query and report | x-recent-search (calls) | per post: is the id already in today's ledger (paid = false) ; after the ack: report paid and free reads |
| quota-governor | read ledger record | x-user-resolver (calls) | record the read as user:<id> or as the keyed hash |
| quota-governor | read ledger settle | x-full-archive-search (calls), x-user-timeline-poller (calls) | settle each page's post ids -> paid = true \| false per id |
| raw-archiver | raw-archiver archive of unknown response shape | ig-account-resolver (calls) | 'the response is archived through raw-archiver' |
| raw-archiver | raw-archiver item-id lookup | deletion-propagator (calls) | find archive objects by item id when raw_ref is absent; shape not stated |
| raw-archiver | raw-archiver media endpoint (remove reference) | deletion-propagator (calls) | remove the media reference per hash |
| raw-archiver | raw-archiver POST /v1/rewrites | deletion-propagator (calls) | ids and mode -> new object without those lines (or payload emptied), new manifest, earlier version deleted |
| raw-archiver | raw-archiver replay path | aggregator (uses), keyword-matcher (uses), store-writer (uses) | replays reach base tables via store-writer; aggregator rebuilds affected hours |
| raw-archiver | raw-archiver rewrite | yt-text-purger (mention) | rewrites raw/green/youtube/... batches and archive/youtube/<yyyy>/<mm>/ partitions without text, on deletion-propagator's request |
| registry-writer | manual candidate submission | poster-resolver (receives) | manual_candidate on jobs.poster-resolver, same path, origin: manual |
| registry-writer | refresh changes to registry-writer | news-site-resolver (calls) | send changes to registry-writer, which emits source.events updated (channel not stated) |
| registry-writer | registry-writer tier request | fb-client-webhook-receiver (calls) | ask to promote a dormant Page back to push; ask to return the Page to its reach tier |
| registry-writer | requests to registry-writer | yt-pubsub-receiver (calls) | push, promotion, next_poll_at, health |
| retention-purger | lifecycle functions | raw-archiver (exposes) | lifecycle and rewrite functions; not specified |
| retention-purger | retention_audit confirmation | yt-text-purger (exposes) | retention-purger reads the retention_audit row (with parent_run_id) as the delegate's confirmation, then runs its own verification |
| search-hit-router | first-sighting feedback | web-search-perplexity (receives) | items_new_total counts first sightings 'as reported back by search-hit-router' (mechanism not stated) |
| search-hit-router | handled_by skip rule | yt-web-search-bridge (mention) | search-hit-router skips search.results marked handled_by = yt-web-search-bridge |
| search-hit-router | unique-domain feed | web-gdelt-poller (receives) | unique_domain_share: domains no other engine returned, 'from search-hit-router' (mechanism not stated) |
| search-hit-router | variant yield feed | web-search-mojeek (receives) | variant_yield{variant} counts results that search-hit-router classifies as Iraqi (mechanism not stated) |
| self-hosted annotation tool | annotation tool | analysis-entities (calls), analysis-media (calls) | review_queue rows kind = annotation:entities |
| self-hosted annotation tool (as analysis-sentiment) | annotation tool | analysis-topics (calls) | review_queue rows kind = annotation:topics |
| source-health-canary | canary empty-200 searches | x-full-archive-search (relies on) | one-page searches of canary_targets accounts that post daily; above 5% empty in 15 minutes it sets health = degraded |
| source-health-canary | canary empty-200 signal | web-gdelt-poller (reports), web-search-mojeek (reports), web-search-perplexity (reports) | only the canary query's empty answer counts as an empty 200 for the web route (mechanism not stated) |
| source-health-canary | empty-200 event | yt-keyword-search (calls) | a run in which every term returns zero counts as an empty-200 event |
| source-health-canary | implausible-scan notice | web-commoncrawl-scanner (notifies) | source-health-canary 'is told' of an empty or implausible scan so it can flip health = degraded (mechanism not stated) |
| source-health-canary | source-health-canary fallback state | poster-resolver (reads) | waits until source-health-canary emits fallback_off or the route returns to ok |
| source-health-canary | stream_silent reconnect | x-filtered-stream (receives) | checks canary accounts' posts and raises `stream_silent`, forcing a reconnect; mechanism not stated |
| source-health-canary (through listening-sdk) | SDK canary hook (health) | ig-account-media-poller (calls), ig-account-resolver (calls), ig-comments-fetcher (calls), ig-keyword-search (calls), ig-mentions-fetcher (calls), ig-own-comments-fetcher (calls), x-replies-fetcher (calls), x-user-resolver (calls) | reads `health` |
| source-health-canary (through the listening-sdk canary hook) | SDK canary hook | x-compliance-sync (calls) | report a registered X source as suspended, protected or deactivated -> health = blocked; when X stops reporting it -> health = ok |
| source-health-canary (via listening-sdk) | SDK canary hook (health read) | fb-backfill (calls), fb-group-comments-fetcher (calls), fb-group-posts-poller (calls), fb-keyword-search (calls), fb-page-feed-poller (calls), fb-page-resolver (calls), fb-page-search (calls), fb-post-comments-fetcher (calls), fb-reactions-fetcher (calls) |  |
| Supabase Auth | Supabase Auth roles | registry-writer (uses) | ops, client_admin role checks on the manual endpoint |
| Supabase Postgres (sources X rows, keywords, client_sources) | Postgres NOTIFY | x-filtered-stream (receives) | NOTIFY triggers a rule reconcile |
| Supabase Vault | Supabase Vault | li-org-resolver (calls), li-post-comments-fetcher (calls), li-post-search (calls) | per-client LinkedIn tokens and the Apify token injected per job |
| Supabase Vault | Supabase Vault (hub secrets) | yt-pubsub-receiver (calls) | hub secret read if signing is confirmed |
| Supabase Vault | Supabase Vault API key | yt-uploads-reconciler (calls), yt-video-details-fetcher (calls) | company app key per job |
| Supabase Vault | Supabase Vault API key read | yt-channel-resolver (calls) | company app API key read for each call only |
| Supabase Vault | Supabase Vault key fetch | fb-group-comments-fetcher (calls), fb-group-posts-poller (calls), fb-keyword-search (calls) | vendor key for this job only |
| Supabase Vault | Supabase Vault read | li-notification-receiver (calls) | app client secret and client tokens |
| Supabase Vault | Supabase Vault reads | yt-comments-fetcher (calls), yt-replies-fetcher (calls) | API key per job; author-hash key |
| Supabase Vault | Supabase Vault token fetch | fb-backfill (calls), fb-page-feed-poller (calls), fb-page-resolver (calls), fb-page-search (calls), fb-post-comments-fetcher (calls), fb-reactions-fetcher (calls) | token injected for this job |
| Supabase Vault | Supabase Vault token read | li-client-posts-poller (calls), li-own-comments-fetcher (calls) | OAuth token of the client who connected the page, for this job only |
| Supabase Vault | Vault via vendor_keys | li-company-posts-poller (calls) | Apify token from Supabase Vault via vendor_keys |
| Telegram Bot API (inbound updates for the discussion bot) | Telegram webhook endpoint | tg-discussion-receiver (exposes) | HTTPS POST of Update objects; secret-token header checked; HTTP 200 only after Redpanda acknowledges, non-2xx with Redpanda down so Telegram redelivers; path... |
| Telegram Bot API (inbound updates) | Telegram webhook endpoint | tg-bot-channel-receiver (exposes) | HTTPS POST of Update objects; secret-token header checked in constant time; HTTP 200 only after Redpanda acknowledges, non-2xx on a failed produce so Telegra... |
| the shared headless pool | headless fetch | news-sitemap-poller (calls) | when the policy's access_mode is headless |
| the shared headless pool (Playwright) | headless fetch | news-feed-poller (calls) | when the policy's access_mode is headless |
| the shared Playwright Chromium pool | headless fetch | news-site-resolver (calls) | same user agent, no CAPTCHA solving; only when the policy says headless or proxy |
| the shared Playwright Chromium pool | headless render | news-article-extractor (calls), news-homepage-differ (calls) | when access_mode is headless |
| the shared Playwright pool | headless attempt | news-robots-checker (calls) | one attempt on a Cloudflare challenge; success gives headless |
| web-search-perplexity, web-search-mojeek, web-gdelt-polle... | yield feedback | search-hit-router (provides) | metrics only in v1 (proposed): engine_unique_yield{engine}, variant_yield{engine,variant} |
| weekly reviewer | daily clustering batch job | analysis-topics (exposes) | candidates to review_queue; accepted candidates become zero_shot nodes |
| yt-comments-fetcher | yt-comments-fetcher comment index (direct read) | yt-replies-fetcher (calls) | read-only database read of last_seen_at, total_reply_count, parent_comment_id |
| yt-pubsub-receiver's owner | push_silent_channel notice | yt-uploads-reconciler (calls) | alert sent for resubscription |

