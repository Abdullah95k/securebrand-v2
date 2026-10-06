# yt-channel-resolver

**Platform:** YouTube · **Route:** green · **Lane:** Discover and qualify · **Owner:** Backend lead, YouTube adapters · **Status:** Draft v1, 6 Oct 2026

## 1. Why this service exists

A keyword hit on a YouTube video names the channel that published it, by channel id or sometimes only by handle, and nothing more. Before the channel can be watched, the qualifier needs its subscriber count (for the tier), its Iraqi signals (country, Iraqi place names, an Arabic or Sorani description, links to .iq sites), whether it hides its count or is made for kids (both need a person's decision), and whether it still exists. Once registered, the channel needs one more fact the hit never carries: its uploads playlist id, which yt-uploads-reconciler reads to reconcile and backfill it. yt-channel-resolver gets all of this from one `channels.list` call for up to 50 channels, at 1 quota unit.

Without it, YouTube discovery stops at the hit. yt-keyword-search and yt-web-search-bridge keep finding Iraqi videos, but their channels cannot be tiered, cannot pass the Iraqi-signals rule and cannot be backfilled or reconciled, and a handle never becomes the channel id yt-pubsub-receiver subscribes to. The registry would grow only by hand, and clients would miss every Iraqi channel nobody thought to add.

## 2. Objective (the end state this service delivers)

Every YouTube candidate from poster-resolver, and every registered channel whose profile is due, leaves as one message on `poster.profiles`: a resolved channel with the facts, signals, review flags and uploads playlist id that the qualifier and registry-writer need, or the verdict `unavailable`. Targets: 100% of jobs answered (or dead-lettered after 5 attempts); 0 units spent on a candidate cached within 30 days; no registered channel's profile older than 30 days plus one scan period for 99% of channels per day. Answer time and average ids per call: targets set in the pilot.

## 3. Scope

### In scope

- Resolving `youtube:<channel id>` candidates in batches of up to 50 ids per call, and `youtube:<handle>` candidates through `forHandle`.
- The 30-day cache, including handle-to-id aliases and `unavailable` verdicts.
- Mapping the profile fields and deriving the Iraqi signals.
- Review flags: hidden subscriber count, made for kids.
- A 30-day refresh loop for registered channels; writing `poster.profiles`.

### Out of scope

- Qualifying (qualifier), registering and storing the uploads playlist id (registry-writer), deduplicating candidates (poster-resolver).
- Videos, uploads and comments (yt-uploads-reconciler and the comment services), PubSubHubbub subscriptions (yt-pubsub-receiver), backfill scheduling (backfill-orchestrator).
- Finding channels with `search.list` (100 units a call).
- Language share of the last 20 posts, latest-upload activity, spam: these come from the item pipeline.
- Comment authors: individuals under qualifier rule 7, never resolved here.

## 4. Users and consumers

- **poster-resolver** sends requests; **qualifier** consumes `poster.profiles`; **registry-writer** applies registrations and tier changes and stores the uploads playlist id.
- **yt-uploads-reconciler**, **yt-pubsub-receiver** and **backfill-orchestrator** use the channel id and uploads playlist id through the registry.
- **Ops** watches refresh lag, key health, review flags and the DLQ, and can force a resolution (`ops_force`). Clients only see channels appear in their registry.
- Also: quota-governor, source-health-canary.

## 5. How it works

### 5.1 Trigger and rotation

**Trigger.** A job on `jobs.yt-channel-resolver`, partitioned by `candidate_key` (a registered channel uses its `source_id`), carrying `job_id`, `kind` (`resolve` from poster-resolver, `rotation` from this service's loop, `ops_force` from ops, which bypasses the cache), `candidate_key`, `source_id`, `client_ids`, `due_at`, `attempt`.

**Batching.** A worker gathers id-keyed cache misses from its partitions into one call that closes at 50 unique ids or when `BATCH_WINDOW_MS` expires (value set in the pilot). Jobs for the same id share one slot. Handles are called one at a time.

**Cache.** Profiles and `unavailable` verdicts are cached for 30 days; a resolved handle is cached under both the handle and the channel id.

**Refresh rotation.** Subscriber counts move slowly, so registered channels are refreshed on one 30-day cycle rather than at poller tier intervals. A leader-elected loop (Postgres advisory lock) selects channels (`platform = youtube`, tier not `retired`) whose profile reaches 30 days, oldest `fetched_at` first and then by tier, so none is skipped twice in a row, and emits `rotation` jobs that fill 50-id calls. The next refresh is set from the START of the last resolution, so the cycle does not drift. Dormant and push channels follow the same cycle. A channel crossing 10,000 or 100,000 subscribers reaches the qualifier, which proposes the tier change through registry-writer.

**Catch-up.** If the loop falls behind (a profile older than 30 days plus one scan period), it works the oldest first and raises `rotation_behind`; tiers go stale, nothing is lost.

**Backfill.** None here. The uploads playlist id this service returns is what lets yt-uploads-reconciler run the backfill that backfill-orchestrator schedules. A channel added by a client or ops is resolved once before its tier is set.

### 5.2 Step by step

1. Consume jobs; look up `profile_cache` by key or alias. On a hit (unless `ops_force`), emit with `cache = hit` and stop.
2. Group misses into batches of up to 50 ids; handles go alone.
3. Ask quota-governor for 1 unit per call under `youtube_data_api` at priority 4; on wait-until or deny the batch waits.
4. Read the company app's API key from Supabase Vault for this call only; call `channels.list` (5.3).
5. For each returned item: parse the string counts to integers; take `country` from `snippet`, else `brandingSettings.channel`, recording which; set `followers` from `subscriberCount`, or null plus flag `hidden_subscriber_count` when `hiddenSubscriberCount` is true; copy `contentDetails.relatedPlaylists.uploads`, never derive it from the channel id; flag `made_for_kids` when the response carries that designation (open question 3).
6. Derive the signals: `country_iq`; `iq_place_names` (Iraqi cities and governorates in the title or description, from the list qualifier rule 2 uses); `description_lang` (`ckb` when the Arabic-script text has Sorani-only letters such as ڕ, ڵ, ێ, ۆ; `ar` for other Arabic script; else `other` or `none`); `website_domains` and `iq_domain` from URLs in the description. Cache for 30 days; emit one message per waiting job.
7. An id missing from a 200 that returned other items is terminated, deleted or wrong: `unavailable`, cached, emitted, never retried. A batch with no `items` at all is an empty 200 (section 8).
8. After Redpanda acknowledges the batch, commit offsets and update `service_runs`.

### 5.3 The call it makes

```
GET https://www.googleapis.com/youtube/v3/channels
  ?part=snippet,statistics,brandingSettings,contentDetails
  &id=<up to 50 channel ids>
```

Authenticated with the company app's API key; no OAuth, public channel data only. 1 unit per call, batched: one call answers its whole batch, so there is no page size or page token. The fact sheet's single-id call gains `contentDetails` here for the uploads playlist id.

A handle-only candidate resolves through the `forHandle` parameter in place of `id`, with the same parts; its answer carries the original `candidate_key` and the resolved `platform_id`. To be confirmed in the pilot: one handle per call at 1 unit, with or without "@", same fields returned; and whether a further part for the made-for-kids designation can be added, at what cost.

### 5.4 What it gets

```json
{"items": [{
  "id": "UC4fE2vQm8bN1kT7yR3pL9sA",
  "snippet": {"title": "قناة المثال الفضائية", "customUrl": "@exampletv",
    "description": "أخبار العراق من بغداد والبصرة https://example-tv.iq/live",
    "publishedAt": "2014-03-09T08:15:22Z", "defaultLanguage": "ar", "country": "IQ"},
  "statistics": {"viewCount": "98000000", "subscriberCount": "412000", "hiddenSubscriberCount": false, "videoCount": "3150"},
  "brandingSettings": {"channel": {"country": "IQ", "defaultLanguage": "ar"}},
  "contentDetails": {"relatedPlaylists": {"uploads": "UU4fE2vQm8bN1kT7yR3pL9sA"}}
}]}
```

Counts arrive as strings. What it does not get: the latest upload date (activity comes from the hit and from yt-uploads-reconciler); videos, comments or their language; About-page links (only URLs in the description are read); owner contact details; anything about commenters.

## 6. Inputs and outputs

### 6.1 Reads

`jobs.yt-channel-resolver`; `profile_cache`, `sources`, `budgets` through quota-governor, `health` through the SDK canary hook; the API key in Supabase Vault; `source.events` (`added`, `tier change`, `retired`).

### 6.2 Writes

`poster.profiles`, one message per answer, partitioned by `source_id` for a registered channel and by `candidate_key` otherwise:

```json
{
  "envelope": {
    "platform": "youtube", "route": "green", "vendor": null,
    "service": "yt-channel-resolver",
    "candidate_key": "youtube:UC4fE2vQm8bN1kT7yR3pL9sA", "source_id": null,
    "job_id": "01J9N7K3F2X6B8R1T5W9C4MZQD", "attempt": 1,
    "fetched_at": "2026-10-06T11:02:47Z", "cached_until": "2026-11-05T11:02:47Z",
    "cache": "miss", "ids_in_call": 37, "retention_class": "youtube_30d_text",
    "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]
  },
  "profile": {
    "resolved_type": "channel", "verdict": "resolved",
    "platform_id": "UC4fE2vQm8bN1kT7yR3pL9sA", "handle": "@exampletv",
    "display_name": "قناة المثال الفضائية",
    "url": "https://www.youtube.com/channel/UC4fE2vQm8bN1kT7yR3pL9sA",
    "description": "أخبار العراق من بغداد والبصرة https://example-tv.iq/live",
    "country": "IQ", "country_source": "snippet", "default_language": "ar",
    "followers": 412000, "subscribers_hidden": false,
    "video_count": 3150, "view_count": 98000000,
    "published_at": "2014-03-09T08:15:22Z",
    "uploads_playlist_id": "UU4fE2vQm8bN1kT7yR3pL9sA",
    "website_domains": ["example-tv.iq"],
    "signals": {"country_iq": true, "iq_place_names": ["بغداد", "البصرة"], "description_lang": "ar", "iq_domain": true},
    "made_for_kids": null, "review_flags": []
  }
}
```

`made_for_kids` stays null (unknown) until open question 3 is settled. An `unavailable` answer carries `profile = {"resolved_type": "channel", "verdict": "unavailable", "platform_id": "<id, or null for an unknown handle>"}`. Also `service_runs`, and `dlq.yt-channel-resolver` after 5 failed attempts.

### 6.3 State

`profile_cache` (control-plane Postgres): `candidate_key`, handle aliases, the profile or verdict, `fetched_at`, `expires_at`. No `cursors` row. `sources.followers` and the stored uploads playlist id are written by registry-writer, not here. In memory: the leader lock, open batches, backoff state.

## 7. Limits, quotas and cost

- One call per batch of up to 50 cache-missed ids, and one per handle (to be confirmed in the pilot), 1 unit each; USD 0 per call. The cost is quota: 10,000 units a day by default, shared with every yt-* service (one `search.list` costs 100), extensions by audit.
- Budget tag `youtube_data_api` (buckets `search`, `ingest`, `comments`, `reserve`) at priority 4; the bucket is open question 4.
- A channel costs at most one id slot per 30 days, however often it is mentioned. Refreshing N registered channels costs N ÷ 50 units (rounded up) per cycle: an illustrative 10,000 channels cost 200 units every 30 days, about 7 units a day.
- Candidate volume, handle share, cache hit rate and ids per call: to be measured in the pilot.

## 8. Failure handling and fallback

- HTTP 429: exponential backoff with jitter from 30 s to 15 min; each job of the batch is requeued with `attempt + 1`; after 5 attempts it goes to `dlq.yt-channel-resolver` and an alert fires.
- HTTP 401 and 403: mark the API key `degraded`, stop the batch, alert; never rotate keys, Google Cloud projects or IPs. A 403 reporting the daily quota spent also tells quota-governor to deny `youtube_data_api` until reset; how it is recognised is to be confirmed in the pilot.
- HTTP 400 on a batch: split in halves and retried until the offending id is isolated; that job goes to the DLQ, the rest are answered.
- Empty 200 (no `items` for a whole batch): retried once, then its ids are `unavailable`; above 5% in 15 minutes source-health-canary flips `health = degraded`. No amber route exists, so `fallback_on` is never set.
- `unavailable`, hidden counts and made-for-kids are answers, not failures. Schema change: the batch is parked in the DLQ with `schema_unknown`. Partial write: the cache entry is written with the emit, so a replay answers identically.

## 9. Non-functional requirements

- Throughput: demand follows the new channels behind YouTube hits (3.0M YouTube items a month at full scale), to be measured in the pilot; 50 ids per call.
- Latency: a miss costs the batch window, one call and any quota wait; a hit is a database read.
- Idempotency and scaling: one answer per `candidate_key` per cache period, replays safe; stateless workers on partition lag, one leader for the refresh loop.
- Security: the API key comes from Supabase Vault per call and is never logged; only the four parts are requested; nothing about commenters; retention class `youtube_30d_text`, profiles refreshed or dropped at 30 days; no profiling on protected attributes; call and unit logs kept for a YouTube audit.

## 10. Metrics and alerts

`jobs_total{status}`, `fetch_latency_seconds`, `cost_units_total`, `quota_denied_total`, `dlq_total`, plus `resolutions_total{verdict}`, `review_flags_total{flag}`, `ids_per_call`, `cache_hits_total`, `cache_misses_total`, `handle_lookups_total`, `refresh_lag_seconds` and `api_error_total{status}`. Alerts: `rotation_behind`, `key_degraded`, `dlq_nonempty`, `empty_200_rate`, `quota_deny_rate`, and `unavailable_rate` above the pilot baseline. SLO: no registered channel profile older than 30 days plus one scan period for 99% of channels per day.

## 11. Dependencies

listening-sdk, poster-resolver, qualifier, registry-writer, quota-governor, source-health-canary; yt-keyword-search, yt-web-search-bridge and search-hit-router (candidate origins, through poster-resolver); yt-uploads-reconciler, yt-pubsub-receiver and backfill-orchestrator (users of the ids, through the registry); Supabase Postgres and Vault; Redpanda. Google: the company app's Cloud project with YouTube Data API v3 enabled, an API key, and compliance with the Developer Policies (audit at any time).

## 12. Risks and mitigations

- Hidden counts leave no tier: sent to review, with view and video counts as context.
- Many Iraqi channels set no country: the other signals still feed rule 2; one-signal cases go to the n8n review card.
- The four parts may not carry the made-for-kids designation: until open question 3 is settled, such channels are not flagged.
- `forHandle` may not behave as assumed: confirmed in the pilot; failing handle jobs go to the DLQ with the reason.
- The script check can read Persian or Urdu as `ar`: one signal among several; the 40% rule on posts stays the main language test.
- A personal vlog channel can qualify (rule 1): only what the channel publishes is read; commenters are never sent here.

## 13. Acceptance criteria

1. A candidate cached less than 30 days ago is answered with `cache = hit` and no API call; `ops_force` makes the call.
2. 120 id-keyed misses in one batch window produce exactly 3 calls (50, 50, 20 ids) with `part=snippet,statistics,brandingSettings,contentDetails`, 3 units on `youtube_data_api`, and 120 messages.
3. Two jobs for one id in a batch take one id slot and receive identical profile content.
4. The 5.4 fixture yields integers `followers = 412000`, `video_count = 3150`, `view_count = 98000000`, and `uploads_playlist_id` equal to `contentDetails.relatedPlaylists.uploads`.
5. Country `IQ` in `snippet` gives `country_source = snippet` and `country_iq = true`; only in `brandingSettings` gives `country_source = brandingSettings`; in neither gives `country = null`, `country_iq = false`.
6. The 5.4 description yields البصرة in `iq_place_names`, `iq_domain = true` and `website_domains = ["example-tv.iq"]`; a description containing ڕ or ێ yields `description_lang = ckb`.
7. `hiddenSubscriberCount: true` yields `followers = null`, `subscribers_hidden = true` and `hidden_subscriber_count` in `review_flags`; a made-for-kids fixture yields `made_for_kids` in `review_flags`.
8. An id missing from a 200 that returned others yields `unavailable`, cached 30 days, not retried, not counted as a failure; on a refresh the message carries its `source_id`.
9. A batch with no `items` counts once toward the empty-200 rate and is retried once before any `unavailable`.
10. A handle-only candidate costs one `forHandle` call; a later request for `youtube:<its channel id>` is a cache hit.
11. With 100 fixture registered channels over 60 days, none is older than 30 days plus one scan period, oldest refreshed first; retired channels are never refreshed; a refresh from 9,500 to 10,400 subscribers emits a message with its `source_id`.
12. HTTP 429 backs off from 30 s to 15 min with `attempt + 1`, reaching the DLQ and an alert after 5 attempts; a 401 marks the key `degraded`, stops the batch and raises `key_degraded`; the key never appears in logs.

## 14. Open questions

1. Does poster-resolver keep comment authors out of this queue, as qualifier rule 7 requires?
2. Does `forHandle` take one handle per call at 1 unit, with or without "@", returning the same parts?
3. Which part carries the made-for-kids designation, and does adding it keep the call at 1 unit?
4. Which `youtube_data_api` bucket carries resolver calls? Proposed: `ingest`.
5. Does poster-resolver already own refreshing registered channels? If so, this loop is removed.
6. Should `defaultLanguage = ar` count as an Arabic-description signal when the description is empty?
