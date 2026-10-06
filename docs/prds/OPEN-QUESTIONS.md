# Open questions across the service PRDs

Collected from section 14 of every PRD on 6 Oct 2026, grouped by platform. Each question is answered in its own PRD once decided; this file is regenerated, not edited by hand.

## Facebook

### [fb-backfill](facebook/fb-backfill.md)

1. Comment fetches for backfilled posts: the policy gives no automatic fetches beyond day 30, which leaves 60 of the 90 backfilled days without comment text. Proposal for comment-decay-scheduler: one comment fetch per backfilled post older than 30 days, budget permitting; Abdullah to decide against the quota measured in the pilot.
2. The `capped` heuristic (posting-rate gap) needs a threshold: to be measured in the pilot against Pages with known histories.
3. Whether on-demand re-runs are exposed to clients or stay an ops action in the first release.

### [fb-client-webhook-receiver](facebook/fb-client-webhook-receiver.md)

1. Do comment events arrive inside `feed` or as a separate `comments` field, and must the subscription add it?
2. Do events carry full content, or only ids that need a follow-up fetch?
3. What are Meta's retry schedule and response deadline?
4. Should hidden comments (`hide`, `unhide`) be treated as deletions? Proposed: ignored in v1.
5. How are missed pushes measured? Proposed: reconciliation items whose key was not yet seen.

### [fb-group-comments-fetcher](facebook/fb-group-comments-fetcher.md)

1. Does the vendor return comment ids, reply counts and a replies call, and in which order does it return comments?
2. What initial value for `FB_GROUP_REPLY_THRESHOLD`?
3. Should extension fetches be dropped second, after hot-post fetches, at 80% of the budget?
4. What happens to steps missed while the flag is off: no catch-up, or one complete fetch for posts still inside their 3-day window?
5. On this route, should a deletion require two consecutive complete reads?

### [fb-group-posts-poller](facebook/fb-group-posts-poller.md)

1. Vendor parameters, page size, ordering and pagination depth: to be confirmed in the pilot.
2. Does the vendor's response carry member count for tiering and counts per post?
3. Which vendor is primary? Proposed: ScrapeCreators, at USD 0.99 to 1.88 per 1,000 requests against USD 1.99 to 4.83 per 1,000 credits.
4. Who verifies the owners of both vendors, and by when?
5. Should raw-archiver redact the plain poster id and name once the poster is classed as an individual?
6. Should post counts be refreshed after the first read, and by which service?

### [fb-keyword-search](facebook/fb-keyword-search.md)

1. If ScrapeCreators has no keyword search, should all amber Facebook services run on `sociavault`, or should a per-service override exist?
2. Which sort order, date filter, page size and depth does the vendor search offer, and how well does it cover Kurdish and dialect spellings?
3. Who ranks the variants, and where is the list kept: the `keywords` table?
4. Should a client's priority keywords run more often than daily, at higher cost? Proposed: not in v1.
5. Should this service also emit early `discovery.hits` for unregistered Pages and groups, as x-recent-search does? Proposed: no, keyword-matcher does.

### [fb-page-feed-poller](facebook/fb-page-feed-poller.md)

1. Whether `since` on `/feed` filters on `created_time` or `updated_time`: to be confirmed in the pilot; if `updated_time`, edited old posts reappear and normalize-item must treat them as versions.
2. Should the push-tier reconciliation poll use the Page access token or the system-user token? Proposed: the Page token, since the data belongs to the client.

### [fb-page-resolver](facebook/fb-page-resolver.md)

1. Does poster-resolver already own refreshing registered Pages? If so, this service's loop is removed.
2. Does PPCA alone return `fan_count`, `location`, `website` and `about` for third-party Pages?
3. Should `followers_count` be added to the fixed field list?
4. Can several candidates be resolved in one call (Graph batching) to save quota?
5. Should the negative cache last 30 days, as for Pages, or 180 days like the qualifier's rejections? Proposed: 30.

### [fb-page-search](facebook/fb-page-search.md)

1. Depth: how many pages of results per variant are worth following before relevance decays into noise; to be measured in the pilot and then fixed in configuration.
2. Whether a client should be able to mark a candidate "never suggest again" directly from the product, which would feed the rejected memory without a qualifier round-trip.
3. Whether weekly rediscovery should run for keyword sets whose clients have Facebook in scope but no Facebook Pages registered yet (proposed: yes, that is exactly when discovery matters most).

### [fb-post-comments-fetcher](facebook/fb-post-comments-fetcher.md)

1. Does Graph return `message` byte-identical across fetches, and is a reply's parent returned? To be confirmed in the pilot.
2. Should the +24 h sweep be exempt from early stop? Proposed: yes, because it is the only catch for late comments.
3. Does `comments.summary(total_count)` under `filter=stream` include replies? If so, it gives a cheap completeness check.
4. Should the `like_count` of stored comments be refreshed on sweeps through `item.metrics`? Not in v1.
5. While PPCA is pending, should the vendor's post-comments endpoint serve as an amber fallback for Page posts?
6. Is the fetch report sent to comment-decay-scheduler as a job-result record, and does `comment_ledger` stay in Postgres rather than ClickHouse?

### [fb-reactions-fetcher](facebook/fb-reactions-fetcher.md)

1. Confirm in the comment-decay-scheduler PRD that it emits the +24 h and +7 d metrics refresh jobs for Facebook; the alternative is a small due-time table owned by this service.
2. Whether to batch refreshes with `ids=`: the per-call ceiling and its effect on the Pages bucket are to be measured in the pilot.

## Instagram

### [ig-account-media-poller](instagram/ig-account-media-poller.md)

1. Page size, ordering and cursor syntax of the `media` edge nested in `business_discovery`, and how far back it can be read (this fixes the backfill cap): to be confirmed in the pilot.
2. Whether Business Discovery can be pointed at the calling client's own username. For owned accounts the webhooks (`comments`, `mentions`) do not announce new posts, so under the push rule an owned account's own posts would be found within 24 hours; proposed: clients who need hourly freshness put their account on the priority list (Tier 1).
3. Whether normalize-item records a re-emitted post as a new count observation rather than a duplicate, which the `metrics` jobs rely on: to be confirmed with its owner.

### [ig-account-resolver](instagram/ig-account-resolver.md)

1. The table of Business Discovery error codes and messages that separates a personal account, an age-gated account, a renamed or deleted account and the rest: to be built in the pilot.
2. Whether the response carries the discovered account's `id` and `username`, and whether business and creator accounts can be told apart (registry `source_type` account or creator).
3. Control-plane additions: the `profile_cache` table, and `kind = resolve` in the SDK job schema. Proposed: yes to both.
4. How the qualifier gets the language share of the last 20 posts for an Instagram candidate: proposed from the matched item, then from the first backfill read after registration.

### [ig-comments-fetcher](instagram/ig-comments-fetcher.md)

1. SociaVault endpoint, response fields (ids, timestamps, likes), whether one request can page beyond about 15 comments, whether empty 200s are billed, and the credit price of this endpoint: to be confirmed in the pilot and the contract.
2. Hash at this service (proposed, so usernames never enter the pipeline) or in normalize-item, and sharing the key so one person keeps one reference across services.
3. Which selected posts deserve a series within the monthly budget: proposed order by `comments_count`, then source tier; for comment-decay-scheduler to confirm.
4. Beyond dropping hot-post extras at 80% of the budget, should extension steps be dropped next?

### [ig-hashtag-search](instagram/ig-hashtag-search.md)

- The maximum page size and depth of `recent_media` and `top_media`: to be measured in the pilot.
- Whether `top_media` membership should feed a "trending" score in aggregator.
- The tier-2 and tier-3 media-volume thresholds for hashtags: to be measured in the pilot.
- Whether a client with several Instagram business accounts may spread one tag list across them (ledger per account suggests yes; confirm with legal reading of the per-account allowance).

### [ig-keyword-search](instagram/ig-keyword-search.md)

1. SociaVault's search endpoints: whether results can be ordered by recency or filtered by date, page size and pagination, whether captions are searched, whether any country filter exists, and which fields (author handle, ids) come back: to be confirmed in the pilot.
2. Cross-route deduplication: vendor media ids may differ from Graph ids. Proposed: normalize-item also joins on the shortcode in `permalink`; to be confirmed with its owner.
3. The monthly `ig_vendor` budget in USD and the per-source monthly cap (qualifier rule 5): to be decided with Abdullah.

### [ig-mentions-fetcher](instagram/ig-mentions-fetcher.md)

1. Whether `mentioned_media` and `mentioned_comment` can be listed or are read only by an id supplied in a webhook event; this decides whether the hourly poll covers them or only `/tags`: to be confirmed in the pilot.
2. Page sizes, cursor syntax and depth of each edge, and so the real backfill cap and the reconciliation window.
3. Whether the ids returned here equal the ids from Business Discovery and the webhook, which the deduplication relies on.
4. Proposed: hourly for every connected account until the per-account limits are measured; Tier 3 relief only if they force it.

### [ig-own-comments-fetcher](instagram/ig-own-comments-fetcher.md)

1. Order of the comments edge, and the nested replies page size and cursor syntax: to be confirmed in the pilot.
2. Should the series be counted from the media's own `timestamp` when first-seen lags it by more than 1 hour? Proposed: yes, a decision for comment-decay-scheduler.
3. Whether Instagram allows comment text to be edited; the hash mechanism is built either way.

### [ig-webhook-receiver](instagram/ig-webhook-receiver.md)

1. Meta's response deadline, retry count and re-delivery schedule: to be confirmed in the pilot.
2. Exact payloads of the `comments` and `mentions` events, which carry items and which identifiers only, and the subscription call and permissions: to be confirmed in the pilot.
3. Does comment-decay-scheduler accept a pushed count per post for its early-stop, extension and hot-post rules? Proposed: yes.

## TikTok

### [tt-client-videos-fetcher](tiktok/tt-client-videos-fetcher.md)

1. TikTok's request limits for `video.list` per token and per app, its page size, and whether it returns every video: to be confirmed in the pilot.
2. Which retention class applies to Display API data? Proposed: a new `tiktok_display` class, data kept while the authorisation is active and deleted on revocation, client offboarding or TikTok's request, as `meta_on_request` does.
3. When a client revokes access, are stored items deleted through `deletions` (reason `authorization_revoked`)? Proposed: yes, unless TikTok's terms allow keeping them.
4. May green items be shown only to the authorising client? Proposed: yes, since the permission is the client's.
5. Should comment-decay-scheduler route TikTok metrics jobs by the video's `route`, so green videos never reach tt-video-stats-refresher? Proposed: yes.

### [tt-hashtag-feed-poller](tiktok/tt-hashtag-feed-poller.md)

1. Does either vendor's hashtag feed accept a tag name, or only the platform id? This decides whether step 4 needs the stored-video lookup at all.
2. What is the feed's effective depth (backfill cap) and ordering per vendor?
3. What posting-rate threshold should promote a Tier 2 campaign tag to Tier 1 automatically?
4. Should keyword-matcher treat hashtag-source videos as hits by construction (this PRD assumes yes), or require a text match as well for noisy tags?

### [tt-keyword-search](tiktok/tt-keyword-search.md)

1. Does the vendor's keyword search offer sort by recency and a stable cursor, or only ranked pages?
2. What is the effective backfill depth of search per vendor (pilot measurement)?
3. Does one `tt_vendor` budget tag serve all five amber TikTok services, or should discovery and comments have separate lines so a comment surge cannot starve discovery?

### [tt-profile-videos-poller](tiktok/tt-profile-videos-poller.md)

1. How far back the vendor's user-posts listing reaches (the backfill cap), and the name of its pinned-video flag: to be confirmed in the pilot.
2. Do TikHub and EnsembleData return identical video ids and `create_time` precision? If not, the cursor needs a small overlap to survive a vendor switch.
3. Should the daily reconciliation of client-authorised creators run through the amber vendor at all, or is the hourly Display API read treated as complete? Proposed: run it only where the client's contract allows amber data.

### [tt-user-resolver](tiktok/tt-user-resolver.md)

1. Should the resolver also read the candidate's latest 20 videos (one request) for the language-share signal of rule 2, for creator candidates with exactly one Iraqi signal? Proposed: yes, creators only, never individuals.
2. Who refreshes the follower counts of registered creators so tiers stay right? Proposed: poster-resolver re-queues each registered creator here when its cache entry expires, and the qualifier applies rule 6.
3. Should poster-resolver replace `candidate_key` by its hash for individuals before sending jobs? The lookup identifier would still travel in the job and be discarded after the call.
4. Do both vendors return the account's region and bio link? To be confirmed in the pilot.

### [tt-video-comments-fetcher](tiktok/tt-video-comments-fetcher.md)

1. Does the vendor return comments newest-first, and does it expose a sort parameter? If it ranks by relevance, the stop rule changes to paging to the end under the page ceiling: to be confirmed in the pilot.
2. Should per-video comment state live in a shared `comment_state` table used by all comment fetchers instead of `tt_comment_state`?
3. Which found videos get a series? Proposed: only those with a keyword hit or from a client's priority hashtag, to bound spend.
4. Does normalize-item accept a pre-computed `author_hash` and never expect a handle? To be agreed before the pilot.

### [tt-video-stats-refresher](tiktok/tt-video-stats-refresher.md)

1. Does the vendor offer a batch video-detail form? If so, the +24 h jobs for many videos could share requests: to be confirmed in the pilot.
2. Should a third observation at +30 d be added for long-tail videos? Proposed: not in version 1.
3. Does comment-decay-scheduler skip metrics jobs for videos older than 7 days at first sight? To be agreed before the pilot.
4. Should saves be promoted to `item.metrics` once the schema allows? Proposed: yes, as a nullable field.

## X

### [x-compliance-sync](x/x-compliance-sync.md)

1. Does the 24-hour clock run from X's signal or from the event on X? To be settled with counsel and at X's Enterprise review, including whether a compliance stream should replace daily batches.
2. Endpoint paths, upload and download formats, job limits, and whether results carry withheld status with country codes: to be confirmed in the pilot.
3. If jobs are metered, should quota-governor reserve compliance ahead of all other X reads and never deny it? Proposed: yes.
4. Handling of content withheld outside Iraq. Proposed: record only.
5. Should the X fetchers add `withheld` to `tweet.fields` and `user.fields`? x-recent-search's approved PRD does not request it.
6. Should X ingestion pause when no complete run has happened for more than 24 hours? Proposed: yes under government contracts.
7. How long should identifiable X items, evidence files and audit records be kept? With counsel.

### [x-filtered-stream](x/x-filtered-stream.md)

1. Pilot: rule length, rules per request, tag length, the listing call, and whether `from:` takes numeric ids (which would survive renames).
2. Does pay-per-use offer a stream recovery option that would shorten gap jobs?
3. Confirm with x-recent-search's owner the `reconciliation` job shape and that account-rule results get the author's `source_id`.
4. Should x-recent-search skip scheduled queries for keyword rules covered here, as x-user-timeline-poller does for accounts?
5. Is the `author_id` expansion billed as a user read? Decide once with x-user-timeline-poller.
6. Brand rules serve several clients: when does the X plan move to Enterprise, and who owns the blocked-terms list?

### [x-full-archive-search](x/x-full-archive-search.md)

1. The addendum's job kinds have no `keyword_history`: add it to the listening-sdk schema, or carry it as `backfill` with a client flag (and a priority exception)?
2. Align the replies hand-back with the x-replies-fetcher PRD: where the boundary `end_time` is stored.
3. Is the `author_id` expansion billed as a user read? keyword_history and replies pages hold many authors.
4. Who screens a client's terms for sensitive events before a history request, and where is that recorded?
5. Should keyword_history posts feed discovery (old authors becoming candidates and new backfills), or be marked history-only for keyword-matcher?
6. Does backfill-orchestrator re-request a `capped` account's missing history when a new billing cycle opens?

### [x-recent-search](x/x-recent-search.md)

1. Maximum query length, and whether `lang:ckb` is accepted on pay-per-use: to be measured in the pilot.
2. Whether plain handle terms match mentions, or a mention operator is needed: to be measured in the pilot.
3. Timing of the Enterprise move: first government end user or second paying client, whichever comes first.

### [x-replies-fetcher](x/x-replies-fetcher.md)

1. Is the `author_id` expansion billed as user reads? If so, request `tweet.fields=author_id` instead and match registered authors by id. To be confirmed in the pilot.
2. Quote posts: capture them with a dedicated query, or leave them to x-recent-search? To be confirmed in the pilot.
3. Page-cap value and gap closing with `until_id` on capped fetches. To be confirmed in the pilot.
4. Status values (`quota_denied`, `not_root`, `outside_window`, `not_permitted`, `cursor_rejected`), the extension count, series for posts first seen after day 7 and for deleted parents must be aligned with comment-decay-scheduler.
5. A reply also delivered as a post by x-recent-search or x-filtered-stream arrives as `x:post:<id>`; normalize-item must decide how it links to `x:comment:<id>`.
6. Should unregistered repliers that may be organizations reach poster-resolver in clear for qualification, against the hash-first rule? Proposed: no.
7. How posts about protests or rallies are marked so comment-decay-scheduler never opens a series on them.

### [x-user-resolver](x/x-user-resolver.md)

1. Where are client X watchlists held, and should a watchlist-only pass (under 500 followers, unverified) always go to review?
2. Add `url`, `protected` and `profile_image_url` to `user.fields` (the `.iq` signal, protected accounts, the default-avatar spam check) at no extra price?
3. Can the verification type be read, so a paid checkmark alone does not qualify?
4. Could x-recent-search and x-filtered-stream request these `user.fields` on their `author_id` expansion, and are expanded users billed as user reads?
5. Does "Iraq" alone count as a location signal? Proposed: no; rule 2 names a city or governorate.
6. Does poster-resolver already own refreshing registered accounts? If so, this loop is removed.

### [x-user-timeline-poller](x/x-user-timeline-poller.md)

1. Confirm with the x-filtered-stream PRD that coverage is published as its `cursors` rows and its connection state in `service_runs`.
2. Should reposts and the account's own replies be excluded to save reads? Decided from their pilot share.
3. Is the `author_id` expansion billed as a user read (at most USD 0.010 per account per UTC day)? If so, drop it.
4. Confirm with quota-governor's owner that a 100-read page reservation is trued up to the ids returned.
5. Which `clients` column records a government client's X Enterprise entitlement?

## LinkedIn

### [li-client-posts-poller](linkedin/li-client-posts-poller.md)

1. Do Organization Social Action Notifications announce new posts? If yes, client pages can move to the push-tier rule (one reconciliation poll a day) by a registry change; to be confirmed in the pilot.
2. Does our access count as "authenticated" for the six-month organization-data allowance, or is it six weeks? Decides the backfill cap; for legal and the pilot.
3. Does the Posts API return counts, or is the second social-metadata call needed? To be confirmed in the pilot.
4. Is the 30-minute priority list the same flag that makes a source Tier 1 in `client_sources`? Proposed: yes.

### [li-company-posts-poller](linkedin/li-company-posts-poller.md)

1. One run per page or several pages per run: per-run overhead and the cost of an empty run are to be measured in the pilot.
2. The Tier 1 shortened interval: which value, and how many pages the budget affords.
3. Refreshing counts at +24 h and +7 d means re-reading posts, which costs items: restrict it to priority-list pages, or accept first-sight counts?
4. Owner and country of the harvestapi publisher: to be verified before launch.
5. Reposts of member posts: `linkedin_48h` or `vendor_agreed`? For legal, shared with li-post-search.

### [li-notification-receiver](linkedin/li-notification-receiver.md)

1. Event types, payload fields (does an event carry the comment text? announce new posts?), retry behavior, signature header and handshake parameters: all to be confirmed in the pilot.
2. Is the subscription bound to the authorizing administrator's token, and does it lapse when that token expires?
3. Do notifications cover replies and reaction removal? Assumed yes.
4. Should normalize-item turn reaction events into counter increments, or should counts come only from li-client-posts-poller's reads? Proposed: both, with the poller's absolute counts as the baseline.
5. Hashing the reactor at the edge departs from "exactly as received" in `raw.items`, as in li-post-comments-fetcher: to confirm with the raw-archiver owners.

### [li-org-resolver](linkedin/li-org-resolver.md)

1. Does `linkedin-company-posts` return the follower count and location? If not, which company-profile Actor passes the vendor screen?
2. What refresh cadence for registered pages keeps tiers honest at acceptable vendor cost?
3. Should the Iraqi-signal language share be computed in the resolver or deferred to lang-dialect-id on the sampled posts, with the qualifier waiting for it?

### [li-own-comments-fetcher](linkedin/li-own-comments-fetcher.md)

1. Ordering, paging and reply expansion of the Comments API: to be confirmed in the pilot.
2. Does the 48-hour clock run from our `fetched_at` (assumed here) or from the comment's creation? For legal; creation would shorten the window.
3. Which member fields does the API return, and what can the application therefore show?
4. Per-comment derived scores: purged with the text (proposed) or kept as derived scores for ten years? For legal.

### [li-post-comments-fetcher](linkedin/li-post-comments-fetcher.md)

1. Should vendor comment text carry `linkedin_48h` (proposed) or `vendor_agreed` (24 months)? For legal; shared with li-post-search question 2.
2. Does the Actor return comment ids, timestamps and a sort option? This decides the marker and newest-first reading; to be confirmed in the pilot.
3. Is a run below its max items a complete thread? Needed for deletions; to be measured in the pilot.
4. Should posts matched by keyword (li-post-search) get a series? Default no, pending the budget.
5. Are minimized records acceptable in `raw.items` (the one departure from "exactly as returned")? To confirm with the raw-archiver owners.
6. Owner and country of the harvestapi publisher: to be verified before launch.

### [li-post-search](linkedin/li-post-search.md)

1. Does `linkedin-post-search` accept a date window, and in what order does it return items?
2. Should member-authored vendor posts carry `linkedin_48h` rather than `vendor_agreed`? For legal.
3. How many rules will be LinkedIn-active, how many items does one return a day, and does Apify add per-run overhead that makes one run per variant uneconomic?

## Telegram

### [tg-bot-channel-receiver](telegram/tg-bot-channel-receiver.md)

1. Does a bot with the lowest administrator rights still receive `channel_post`, and does `my_chat_member` fire for channel promotions and removals?
2. Does the Bot API expose views or forwards for channel posts at all? If not, this route never has them.
3. One bot or two? Proposed two, because a token has one update consumer; revisit if onboarding friction appears in the pilot.
4. Is a client-added channel accepted by registry-writer with a pre-allocated `source_id` (`proposed_source_id`), and is the `discovery.hits` field set agreed with poster-resolver?
5. Is `vendor_agreed` the right retention class for green Telegram data, or is a dedicated class wanted?
6. Should an opted-in client get 90 days of pre-join history through the amber poller, marked amber on those items?

### [tg-channel-posts-poller](telegram/tg-channel-posts-poller.md)

1. Field names, and whether each Actor returns views and forwards for every post: confirmed in the pilot.
2. Does `since` take a time or only a date? If only a date, hourly Tier 1 reads re-read up to a day of posts and the tier model must be re-costed; the adaptive max-posts cap and saturation rule are the fallback.
3. Which Actor is primary? Proposed: run both on one fixture of 50 channels for a week and compare completeness, USD per 1,000 items and failure rate.
4. Canonical post id when a channel is reached by both routes: proposed `<lowercase username>/<message_id>` on every route, to be agreed with tg-bot-channel-receiver and tg-channel-resolver.
5. Is the Tier 1 +24 h views refresh worth its cost, and should Tier 2 get it?

### [tg-channel-resolver](telegram/tg-channel-resolver.md)

1. The Telemetrio stats path, parameters and the semantics of the plan's channel allowance (tracked channels or distinct channels queried per month).
2. Whether to buy a 20-post Actor sample for candidates with exactly one Iraqi signal, so review cards carry a language share, and at what cost per candidate.
3. `TG_VENDOR_ROUTE` holds one vendor name while Telegram uses Telemetrio and Apify in different roles; this service treats any value other than `off` as on.
4. Whether the stats response includes the channel description, which would add `+964` and `.iq` signals beyond the title.

### [tg-discussion-receiver](telegram/tg-discussion-receiver.md)

1. Is `message_thread_id` set on comment threads in linked groups, and does every top-level comment carry the post copy in `reply_to_message`? The pilot answers both and sets the unthreaded target.
2. Privacy mode off, or administrator rights in the group? Proposed: privacy mode off, since administrator rights are more than a reader needs.
3. Where should the group-to-channel link live: the group row's cursor JSON (proposed), or a registry column?
4. Hashing at the edge departs from the `raw.items` rule of "exactly as returned"; confirm with normalize-item and raw-archiver that `author_ref` is accepted as given.
5. One bot or two, and the retention class for green Telegram data: as in tg-bot-channel-receiver.

### [tg-message-search](telegram/tg-message-search.md)

1. Daily runs with 7-day windows or weekly runs: decide once the pilot gives the per-request and per-keyword prices.
2. `TG_VENDOR_ROUTE` carries one vendor name, but Telegram's amber route uses Telemetrio for search and stats and Apify for posts; this service treats any value other than `off` as on. Confirm or split the flag.
3. Should mentions on channels the qualifier rejected still reach client dashboards?
4. Telemetrio's parameter names, page size, rate limit and alpha support terms.
5. Policy during an Iraq block: pause the vendor route, continue, or let each client choose.

## YouTube

### [yt-channel-resolver](youtube/yt-channel-resolver.md)

1. Does poster-resolver keep comment authors out of this queue, as qualifier rule 7 requires?
2. Does `forHandle` take one handle per call at 1 unit, with or without "@", returning the same parts?
3. Which part carries the made-for-kids designation, and does adding it keep the call at 1 unit?
4. Which `youtube_data_api` bucket carries resolver calls? Proposed: `ingest`.
5. Does poster-resolver already own refreshing registered channels? If so, this loop is removed.
6. Should `defaultLanguage = ar` count as an Arabic-description signal when the description is empty?

### [yt-comments-fetcher](youtube/yt-comments-fetcher.md)

1. Is `textOriginal` returned for every public comment with an API key? YouTube documents it as guaranteed only for the author; fallback `textDisplay`. To be confirmed in the pilot.
2. Status values (`quota_denied`, `comments_disabled`, `video_not_found`) and the priority of client refreshes (proposed 3) must be aligned with comment-decay-scheduler.
3. Should a not-found video trigger removal of its stored comments? Proposed: yt-video-details-fetcher owns video state and decides.
4. Author-hash scope: per channel (proposed, blocks linking a commenter across owners) or per owner, so a client with several channels can count unique commenters.
5. CONVENTIONS keeps aggregates ten years for all classes, while YouTube allows derived metrics up to 36 months: retention-purger's rule for YouTube aggregates needs a decision.

### [yt-keyword-search](youtube/yt-keyword-search.md)

- Which 20 to 30 terms form the launch priority list, and who signs off changes (proposal: client success, with Abdullah's approval for additions that displace an existing term)?
- Does `relevanceLanguage=ku` help or hurt Sorani recall? To be measured in the pilot.
- Should a quota extension be requested after the pilot, and should the daily run align to the quota day boundary used by quota-governor rather than a fixed Baghdad time?

### [yt-pubsub-receiver](youtube/yt-pubsub-receiver.md)

1. What is the hub's maximum lease, what happens to a longer request, and does the verification GET return the granted lease?
2. Does the hub sign with `hub.secret`, and how? If not, adopt the callback token.
3. What are its retry schedule, delivery deadline and subscribe rate limits?
4. Edits to videos published over 90 days ago: proposed counted and ignored in v1.
5. `first_sight` is missing from the addendum's job-kind list; add it.

### [yt-replies-fetcher](youtube/yt-replies-fetcher.md)

1. Order of `comments.list` results, and whether a page token stays valid between steps so an oldest-first thread can resume.
2. `textFormat`: is `textOriginal` returned for every public reply with an API key, or only `textDisplay`?
3. Status values, `post_ref` shape, client-refresh priority (proposed 3) and the one-job rule after early stop: align with comment-decay-scheduler.
4. When a parent comment is removed, does deletion-propagator cascade to its replies (proposed) or does this service emit them?
5. A thread falling to 5 replies or fewer leaves `reply_candidates`; who detects later removals of replies stored here?

### [yt-text-purger](youtube/yt-text-purger.md)

1. Policy text, to be confirmed in the pilot:
   - Does the 30-day rule cover video title and description (assumed yes)?
   - Does it cover statistics in `metrics_timeseries`?
   - What anchors the 36-month clock? The design uses the last `fetched_at`.
2. Interface changes to agree:
   - The `refresh` job kind and the fields `must_finish_by` and `refresh_for_client_ids` (addendum and the fetcher PRDs).
   - The `fetched_before` guard, forced merge and `purge_derived` mode (deletion-propagator).
   - The new `retention_audit` columns.
   - The offboarding hand-off (retention-purger's next revision).
3. Where does the `yt_text_refresh` entitlement live on `clients`, and what share of the `comments` bucket may refresh use?
4. Should the YouTube Parquet archive drop text at write time, so the daily rewrite is no longer needed?

### [yt-uploads-reconciler](youtube/yt-uploads-reconciler.md)

1. Are uploads listed strictly newest first, which timestamp should the stop rule use, and do scheduled or premiered videos land behind the cursor? To be confirmed in the pilot.
2. Do Shorts and live streams appear in the uploads playlist? To be confirmed in the pilot.
3. The rotation policy polls dormant sources weekly; this PRD keeps dormant channels daily (1 unit each) because a quiet channel's broken subscription is the hardest to notice. Confirm, or go weekly if quota is tight.
4. The lapse flag's shape must match yt-pubsub-receiver's PRD when it is written.

### [yt-video-details-fetcher](youtube/yt-video-details-fetcher.md)

1. Priority for first sight from Tier 2, Tier 3, push and keyword-rule sources (proposed 1); confirm in the quota-governor PRD.
2. The `series_step` values on this queue and series close on `deletions`: confirm in the comment-decay-scheduler and yt-uploads-reconciler PRDs.
3. Live streams: re-check interval, and whether +24 h and +7 d anchor on the stream's end.
4. Whether YouTube per-video observations may live past 36 months inside ten-year aggregates.

### [yt-web-search-bridge](youtube/yt-web-search-bridge.md)

- Which engine operators are reliable for `OR` and exact-phrase Arabic queries on Mojeek and Perplexity? To be tested in the pilot before variant curation rules are fixed.
- What share of the 60,000 monthly queries does the bridge get once news and general web discovery are budgeted?
- Should Perplexity's domain allow-list be used instead of, or in addition to, the `site:` operator?
- What promotion rule (days with new ids, hits per day) moves a term from the bridge to yt-keyword-search?

## News websites

### [news-article-extractor](news/news-article-extractor.md)

1. May keyword-matcher and the analysis services read the 7-day cache and persist only derived values (hit offsets, scores)? Proposed: yes, otherwise a brand named after the first 300 characters is missed; to be confirmed with counsel on Law No. 3 of 1971.
2. How an `ai-input = no` Content Signal affects analysis of the excerpt: carried in `usage_signals`; the rule is to be decided with news-robots-checker and the analysis services.
3. Does the 7-day cache live under this service (proposed, with `text_full_ref` in the payload) or under a key written by normalize-item? normalize-item's open question 2 asks the same.
4. Retention period of `news_urls` rows: to be set in the pilot.

### [news-comments-fetcher](news/news-comments-fetcher.md)

1. Disqus API terms for reading comments of forums we do not administer, the key's rate limit, and any price: to be confirmed in the pilot.
2. What share of Iraqi news sites use Disqus: to be measured in the pilot; if small, the series could be restricted to tier 1 sites.
3. Does the extractor capture `disqus_identifier` from the page so the thread lookup never needs the URL form? Proposed: yes, as an optional payload field.
4. HMAC key rotation: rotation breaks linkability of commenter hashes across time; proposed policy to be decided with counsel.

### [news-dedup](news/news-dedup.md)

1. The hand-off to normalize-item is proposed as the table `news_story_members` plus the topic `news.dedup` (one topic added to the Redpanda list) with a bounded wait in normalize-item; if normalize-item prefers a table-only join, the topic is dropped.
2. Maximum Hamming distance, title-overlap threshold, minimum excerpt length and lookup window: to be tuned in the pilot on a hand-labelled sample; proposed starting window is 7 days.
3. Should the extractor emit cross-host canonical copies as ordinary `raw.items` so the sweep is unnecessary? Proposed: keep the ledger-based sweep, so `raw.items` stays one message per canonical URL.
4. Should unique-story and mention counts both be first-class in aggregator? Proposed: yes, with `is_origin` as the story flag.

### [news-feed-poller](news/news-feed-poller.md)

1. The mapping from `articles_per_day_estimate` to a 5, 10 or 15-minute interval for hot sites: to be measured in the pilot.
2. Should hot sites' feeds also be read through WebSub (PubSubHubbub) hubs where a site declares one, replacing polling? Proposed: yes, as a later optimisation once the pilot shows which Iraqi hosts declare a hub.
3. Whether entries with `published` far in the past (re-surfaced old articles) should be emitted. Proposed: emit, and let news-dedup and the extractor ledger absorb them.

### [news-homepage-differ](news/news-homepage-differ.md)

1. The link-count floor that triggers the headless switch, the per-site section cap and the anchor-length threshold: to be measured in the pilot.
2. How many Iraqi sites truly lack both feed and sitemap, and what share of them are behind a Cloudflare challenge: to be confirmed in the pilot.
3. Should ops be able to pin a section page per site from the review card? Proposed: yes, stored in the cursor's `sections`.

### [news-robots-checker](news/news-robots-checker.md)

1. Is `search = no` a stop (proposed) or a signal only? A media-monitoring index of excerpts is search-like, so the proposal is conservative; decision with counsel.
2. How `ai-input = no` affects model analysis of excerpts and of the 7-day cache: carried in `usage_signals`; rule to be decided with the analysis services.
3. The RSL usage-category mapping and the number of Iraqi hosts with RSL or pay-per-crawl: to be confirmed in the pilot.
4. The refresh margin and the unreachable-file limit: to be set in the pilot.
5. Whether to join Cloudflare's pay-per-crawl beta for hosts of high client value: a business decision.

### [news-site-resolver](news/news-site-resolver.md)

1. The product token in `CRAWLER_USER_AGENT` is provisional (`ListeningBot`) until the venture's name is fixed; the contact mailbox follows.
2. Does `news_sites` stay a control-plane table or fold into `sources.notes` as jsonb?
3. The hot-tier publishing-rate threshold: to be measured in the pilot.
4. Regional outlets: accept by default when on a client seed list, or always through review?

### [news-sitemap-poller](news/news-sitemap-poller.md)

1. Should regular-sitemap-only sites be polled here (proposed) or by news-homepage-differ? Proposed: here, because `lastmod` ordering is cheaper and more complete than a diff.
2. How many Iraqi sites publish a news sitemap, and how many regular sitemaps carry reliable `lastmod`: to be confirmed in the pilot.
3. Whether the backfill should also use `news:publication_date` older than the two-day rule on sites that keep a long news sitemap: to be confirmed in the pilot.

## Web search

### [search-hit-router](web/search-hit-router.md)

1. Instagram profile URLs (`instagram.com/<handle>/`) and platform short links (`fb.watch`, `vm.tiktok.com`, `instagr.am`) are not in the specified list. Proposed: add profile URLs as Instagram accounts and leave short links as `web` while their share is measured.
2. The 30-day re-route window, the 30-day parking period and the news-like rule are set in the pilot.
3. The exact field sets of `discovery.hits` and `article.urls` are to be aligned with poster-resolver and the news services.
4. Should the router feed variant yield back to the engines automatically, to retire variants that never produce Iraqi results? Proposed: metrics only in v1.

### [web-commoncrawl-scanner](web/web-commoncrawl-scanner.md)

1. Access route: the index API or bulk columnar reads? The pilot measures time and data volume for one scan.
2. Does the index expose language per capture, and what is the exact list of `.iq` second-level zones?
3. Emission cap, score weights and the accept-rate target are set in the pilot; the `discovery.hits` field set is to be aligned with poster-resolver's schema.
4. Is Common Crawl's host-level web graph worth adding in v2, to find non-`.iq` outlets that known outlets link to?
5. Should ops be able to add outlet hosts by hand as seeds, separate from registered news rows?

### [web-gdelt-poller](web/web-gdelt-poller.md)

1. API specifics: parameter names, maximum records, minimum phrase length, query length, maximum span, and how a rejected query is reported. The pilot answers them.
2. Is a combined OR query reliable with mixed Arabic and Latin forms, or must every rule split by form?
3. Does search-hit-router accept the optional `hints` field, or should the hints travel only in `raw.items`?
4. Does GDELT require attribution?
5. Should priority rules get a second pass restricted to Arabic sources or Iraqi source country, if the pilot shows the unfiltered pass hides them?

### [web-search-mojeek](web/web-search-mojeek.md)

1. API specifics: endpoint, parameter names, results per request, a date filter, `site:` support, rate limits, and whether one request can carry several queries. The pilot answers them.
2. Does Mojeek offer a language boost for Sorani? Until then Sorani variants run under `lb=AR`.
3. Should the priority second run use all 9 variants or the shorter set that web-search-perplexity considers? The two engines should decide together.
4. Should `site_search` jobs from yt-web-search-bridge also be served here, once `site:` is confirmed?

### [web-search-perplexity](web/web-search-perplexity.md)

1. Does the Search API accept `ckb`? The start-up probe answers it; until then Sorani variants run under `ar`.
2. Should the priority second run use all 9 variants or a shorter set (1, 3, 6, 8) to hold the month at 60,000 queries if the priority list grows?
3. `search_after_date_filter` on daily runs or no filter: decided after the one-week pilot comparison.
4. Column names in `keywords` for forms, misspellings, context and intent terms belong to the control-plane schema; this PRD names the attributes.
5. Does normalize-item treat `kind_hint = search_response` as archive-only, or does raw-archiver take those records on a separate path?

## Shared services

### [aggregator](shared/aggregator.md)

1. Does the chosen ClickHouse release run refreshable materialized views in production? If not, `AGG_MV_MODE = service` is the default.
2. Reach: gross followers of the posting source as of the rebuild, or frozen at first sight? Frozen values need a stored column on `hits`.
3. Do clients need posts and comments separated in the hourly grain? The draft keeps one `mentions` count.
4. Retention of the hourly grain at ten years versus hourly for a shorter period with daily and monthly for the rest; row growth is to be measured in the pilot.
5. Sentiment labels and topic ids: names follow `items.analysis/v1`; confirm against analysis-sentiment and analysis-topics.

### [alert-evaluator](shared/alert-evaluator.md)

1. `alert_rules`, `alerts`, `alert_deliveries` and `alert_watch_items` are new control-plane tables, absent from CONVENTIONS. Confirm.
2. Is the open-hour pace test enough for outage-style spikes, or should aggregator add a minute-grain recent table?
3. deletion-propagator must name the deletion reasons and carry `item_id`; if it deletes before the evaluator reads the message, the watch set covers it. Confirm both.
4. Defaults for `ratio`, `min_mentions`, `threshold`, `min_scored_mentions`, `cooldown_minutes` and `ALERT_STORM_LIMIT` come from the pilot; who approves them?
5. Is `keyword_first_seen` acceptable for government clients on reputation and service-quality keywords? The draft allows it; confirm with compliance.

### [analysis-entities](shared/analysis-entities.md)

1. Should a KB release create a new `model_version` (clean audit, heavy re-run) or supersede in place as drafted?
2. Who curates the global KB, and may clients add global entries?
3. Does `person_public` need a list of named public officials maintained by ops, and who decides who counts as a public figure?
4. Sorani NER: own model or multilingual fallback?
5. CPU gazetteer plus GPU model, or a model API for linking?
6. Should aspect sentiment in analysis-sentiment use linked entities as targets in a later version?
7. May platform content be used to train and evaluate this model (legal, as analysis-sentiment question 3)?

### [analysis-media](shared/analysis-media.md)

1. Which OCR engine and which ASR baseline win on the Iraqi sets; is a Sorani ASR viable?
2. May platform media be stored under each platform's terms and each vendor contract, and is thumbnail-only right for YouTube? Legal to confirm.
3. Where does the url-to-hash and reference-count index live, and how does retention-purger find unreferenced `media/<sha256>`?
4. Should OCR text and transcripts feed analysis-sentiment, analysis-topics and analysis-entities in a second pass?
5. GPU pool or model API per task?
6. Frame interval, frame cap, duration cap and the tier rules: values from the pilot.
7. Do clients upload logo sets themselves, and who approves them?

### [analysis-sentiment](shared/analysis-sentiment.md)

1. CAMeLBERT-DA or MARBERTv2; one model for Modern Standard Arabic and dialect, or two?
2. Sorani: own model or multilingual fallback, and are there enough labelled examples?
3. May each platform's content and vendor data be used to train and evaluate in-house models, and for how long? Legal to confirm.
4. Argilla or Label Studio, and who staffs annotation?
5. GPU pool or model API per route; full model on every item or only on hits and client-watched sources (a cost lever)?
6. Should OCR and transcript text from analysis-media feed sentiment in a second pass, and should push sources use the priority lane?
7. Confirm `lang` codes and any Latin-letter Arabic flag with lang-dialect-id, and hit field names with keyword-matcher.

### [analysis-topics](shared/analysis-topics.md)

1. Which encoder and zero-shot approach win on held-out topics?
2. Sorani: own route or multilingual fallback?
3. How many labelled examples promote a `zero_shot` node to `supervised`?
4. Who staffs the weekly review, and may a client approve its own nodes?
5. Should text from images and video (analysis-media) feed topics?
6. Is one global taxonomy plus client taxonomies enough, or do government clients need separate defaults?
7. May platform content be used to train these models (legal, as analysis-sentiment question 3)?

### [backfill-orchestrator](shared/backfill-orchestrator.md)

1. fb-group-posts-poller is not in the list of backfill targets; proposed to receive `backfill` jobs, with vendor history depth to be measured in the pilot.
2. fb-backfill's approved PRD also sets `done` or `capped` and `next_poll_at`; proposed that this service becomes the single writer at its next revision (the values are identical meanwhile).
3. Backfill deadline value and the per-source X read cap: to be set in the pilot.
4. Should an amber source added while its flag is off be backfilled automatically when the flag is switched on? Proposed: yes, in tier order.

### [comment-decay-scheduler](shared/comment-decay-scheduler.md)

1. CONVENTIONS lists no completion topic. This PRD proposes `jobs.completed`, written by the listening-sdk job wrapper of every fetcher, partitioned by `source_id`; alternative: poll `service_runs`.
2. Is the early-stop arming rule (section 5.3) accepted? Without it, a post with no comments at +1 h loses its series.
3. Should extension also require at least 5 new comments, mirroring early stop?
4. Should the 80% stretch rule also cover metered green routes (X, YouTube), for hot extras only?
5. X replies cost USD 0.005 each: a per-post read cap is to be decided after the pilot.
6. Should X, LinkedIn and Telegram posts also get +24 h and +7 d count refreshes? Their pollers read incrementally, so counts after first sight change only when a client refreshes a post; on X each refresh is a paid post read.

### [deletion-propagator](shared/deletion-propagator.md)

1. Backups and snapshots of ClickHouse and Postgres are not described in CONVENTIONS; any backup that holds deleted data must expire inside the shortest deadline or be excluded. To be decided with counsel.
2. The producers of `platform_sync` deletions (fb-reactions-fetcher and the comment fetchers) must emit the minimum shape of 5.4; their PRDs and store-writer's tombstone rule need to be aligned.
3. An author request that matches a registered source needs a registry decision; no producer for it is listed in registry-writer. Proposed: retention-purger emits it.
4. Author-scope messages are keyed by `author_hash`, not `source_id`; the topic note in CONVENTIONS needs that exception.
5. Cost and duration of forced merges and archive rewrites at full scale: to be measured in the pilot.
6. SLAs for non-X `platform_sync` and for `legal`: to be set with counsel.

### [keyword-matcher](shared/keyword-matcher.md)

1. CONVENTIONS lists no hits table. This PRD assumes store-writer fills a ClickHouse `hits` table from both hit topics (see store-writer); confirm.
2. normalize-item hashes authors, so candidate identity is read from the raw archive through `raw_ref`. Confirm raw-archiver makes objects readable within the 60 s target, or add a transient candidate field to normalize-item. poster-resolver must treat `candidate_pending = true` as mention-only.
3. Comment hits by unregistered authors go to `item.hits`, not `discovery.hits` (individuals are never candidates). Confirm.
4. May Meta-origin items be fanned out to clients outside `client_ids` (shared pool)? The draft says no.
5. Default `rematch_days` (30 or 90) and whether exclusion changes also rematch history.
6. Does the clitic and suffix list need a morphological analyser before launch, or do the pilot fixtures settle it?

### [lang-dialect-id](shared/lang-dialect-id.md)

1. Python or Node? The convention reserves Python for analysis workers and the news extractor; CAMeL Tools and KLPT make this a third exception. Confirm, or port the fold to TypeScript and keep only fastText and the dialect model in Python.
2. Kurmanji (Badini, Duhok) lands in `other` in v1. Does Kurdistan Region coverage need its own label?
3. Arabizi is common among young Iraqi users. Add a Latin-script Arabic class after the pilot?
4. Should the full `dialect_scores` vector be stored, or only the top class and its confidence (current draft)?
5. Who labels the Iraqi sample, how large is it, and which thresholds gate a release (to be measured in the pilot)?

### [normalize-item](shared/normalize-item.md)

1. Should vendor-supplied poster names on amber routes be kept for creators below the qualifier thresholds, or hashed like individuals from the start (current draft: hashed)?
2. Which service owns the 7-day full-text cache for news: news-article-extractor through the raw payload, or a cache key written here?
3. Is a 60 s registry refresh from `source.events` enough, or should a cache miss query `sources` directly?
4. Peak records a second and worker count are to be measured in the pilot before the replica policy is fixed.

### [poster-resolver](shared/poster-resolver.md)

- `poster_profiles` is a new control-plane table; confirm it joins the CONVENTIONS table list.
- Whether the per-source resolvers archive raw payloads themselves or leave it to this service (assumed here, so the individuals redaction has one owner).
- Whether `lang-dialect-id` exposes a batch call for profile samples or the SDK bundles the classifier in-process.
- Which domains count as an "Iraqi outlet link": a list in `keywords` or a static list in the SDK.

### [qualifier](shared/qualifier.md)

- Whether client admins may answer review cards for candidates found through their own keywords, or only ops.
- Where the Iraqi outlet and city/governorate lists live (shared with `poster-resolver`).
- Whether `queued` candidates appear in the client app with their queue position.

### [quota-governor](shared/quota-governor.md)

1. YouTube bucket sizes and the provider's reset time: to be set and confirmed in the pilot.
2. Should the 80% stretch also cover metered green routes (X, YouTube), for hot extras only?
3. Should X reads be denied for sources whose only clients are government bodies until Enterprise is acknowledged? Proposed: yes.
4. Charge TikHub at the upper USD 1.00 per 1,000 until the volume tier is confirmed?
5. Size of the green-route emergency allowance during an outage.

### [raw-archiver](shared/raw-archiver.md)

1. Batch number width: normalize-item's examples show four digits, fb-page-feed-poller six. Proposed: six, a constant in `listening-sdk`.
2. normalize-item reads `raw/` directly on a `replay` job. Proposed: `raw.replay` is the main path, with a manifest-only mode for direct readers; confirm which one ships first.
3. How long may envelope-only Parquet outlive the text clock for `youtube_30d_text` and `meta_on_request`? To be confirmed with counsel.
4. Redpanda topic retention for `raw.items`, needed for gap repair: to be set after the pilot.

### [registry-writer](shared/registry-writer.md)

- `registry_audit` is a new control-plane table; confirm it joins the CONVENTIONS list, or whether `decisions` should carry the before/after values.
- Whether a source re-added after retirement should keep its old `source_id` (assumed yes, so history joins).
- Whether `tier_override` from a client (priority list) can place a source in tier 1 without the follower threshold (CONVENTIONS allows "on a client's priority list"; assumed yes).
- Whether `health_change` should be carried on `registry.decisions` or on a dedicated topic.

### [retention-purger](shared/retention-purger.md)

1. Who verifies the identity of an author who files a request? Proposed: a confirmation sent to the platform account's public contact, to be agreed with counsel.
2. Completed author requests should block re-ingestion: proposed a check in normalize-item against `deletion_requests` hashes; not in its approved PRD yet.
3. Retention class for Telegram bot content and for web-search results beyond `news_excerpt`: to be set with counsel.
4. Grace period for the `meta_on_request` necessity clock, and how long audit records are kept: to be agreed with counsel.

### [source-health-canary](shared/source-health-canary.md)

1. `health_change` carries `platform`, `route`, `vendor`, `health`, `fallback` today; this PRD adds `scope`, `reason` and `evidence` and makes `fallback` an object. To be aligned with registry-writer.
2. Who enforces the government exclusion: the decision's `scope` read by registry-writer (proposed) or the canary listing sources one by one?
3. Minimum targets per route and `CANARY_MIN_SAMPLES`: to be set in the pilot.
4. Should a vendor-side 403 (key or plan) count as `degraded` and allow fallback, as proposed, while a platform-side 403 means `blocked`?

### [store-writer](shared/store-writer.md)

1. CONVENTIONS lists no `hits` table; this PRD adds it, assumes store-writer also owns `keywords_dim`, and adds `content_ttl` and `row_ttl` to `retention_classes`. Confirm all three.
2. Topology: one ClickHouse node, or a replicated pair with backups on Hetzner Object Storage or Backblaze?
3. May per-item `analysis` rows from LinkedIn member data outlive 48 hours (derived scores are kept ten years elsewhere)? The draft deletes them.
4. Horizon for item-level `metrics_timeseries`: ten years, or shorter with hourly aggregates carrying the long history? Bytes per row decide; to be measured in the pilot.
5. Does `item.metrics` carry `retention_class`, `created_at` and `source_id`? The draft reads them from `items` when absent.
