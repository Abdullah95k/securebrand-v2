# ADR-0048 · Aggregate slices and all nine alert types in v1

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F8, aggregator, alert-evaluator, store-writer, analysis-sentiment, analysis-topics, analysis-entities, analysis-media, lang-dialect-id, news-dedup, ig-hashtag-search, fb-reactions-fetcher, tt-video-stats-refresher, yt-video-details-fetcher, yt-comments-fetcher, li-notification-receiver, li-own-comments-fetcher, li-post-comments-fetcher, D3, U3
Source: D2-Q048 (user decision; changed by the user's answer) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

aggregator rolls hits up by `(hour, client_id, keyword_id, platform, source_id, sentiment, topic_id, retention_class)` into mentions, reach, engagement and views kept ten years (`aggregator §5.3 L55`, `L57`); alert-evaluator has five rule types over those rows (`alert-evaluator §3 L22`). Items are purged after hours to months, so a slice missing here has no history. Other PRDs promise more (AU-081, AU-083):

- Slices: language (`lang-dialect-id §4 L37`); governorate, institution, brand and media tags (`analysis-entities §4 L33`, `analysis-media §4 L34`); unique stories (`news-dedup §4 L35`, `§14 Q4 L170`); YouTube channel owners kept apart (`yt-video-details-fetcher §4 L35`, `CONVENTIONS L76`); per-post LinkedIn comment rollups kept ten years (`li-notification-receiver §7 L142`, `li-own-comments-fetcher §7 L135`, `li-post-comments-fetcher §7 L139`).
- Labels (AU-014): `mixed` (`analysis-sentiment §2 L15`) is left out of the negative share (`aggregator §5.3 L57`, `alert-evaluator §5.3 L58`); topics come per taxonomy (`analysis-topics §5.2 L60`), so global and client topics collide under one `topic_id`.
- Alerts no rule type implements: engagement spikes (`fb-reactions-fetcher §4 L33`, `tt-video-stats-refresher §4 L36`), topic spikes (`analysis-topics §4 L37`), entities and logos, stories.
- Open: reach as of the rebuild or frozen, posts and comments apart, label names (`aggregator §14 Q2 L157`, `Q3 L158`, `Q5 L160`); a `top_media` "trending" score (`ig-hashtag-search §14 Q2 L188`); a minute grain, who approves alert defaults, `keyword_first_seen` for government clients (`alert-evaluator §14 Q2 L164`, `Q4 L166`, `Q5 L167`).

At stake: what a client can filter and be alerted on, and how far back.

The user's answer, 7 Oct 2026: "Expand Q048 more." Asked again, the user chose "Add 4 alert types in v1": engagement-spike, topic-spike, entity or logo, and story alerts are also built in v1; alerts then launch after the analysis services; per-post LinkedIn history is kept only if counsel says LinkedIn allows it.

Settles: AU-014, AU-081, AU-083, aggregator §14 Q2, aggregator §14 Q3, aggregator §14 Q5, ig-hashtag-search §14 Q2, news-dedup §14 Q4.
Depends on: ADR-0008 (item kinds), ADR-0023 (analysis keys), ADR-0056 (YouTube and LinkedIn rollup lifetimes).

## Options

1. **Every promised slice in the aggregates now; the five built alert types in v1.** _Taken for its slices (a) to (g), with (f) holding until counsel rules on the per-post LinkedIn history; its (h) gives way to option 3's alert types (see Decision)._ Each part can be changed alone:
   - (a) The main grain gains `lang`, `dialect`, `route` and the item `kind` (`post`, `comment`, `article`, ADR-0008), so posts and comments count apart (aggregator Q3), and, on YouTube rows, the video's channel (`video_channel_id`), so YouTube figures stay per channel owner except where the carve-out allows totals (ADR-0056 sets their lifetime).
   - (b) `mixed` counts in every share's denominator and shows as its own share: negative share = negative ÷ (positive + neutral + negative + mixed), so the four shares add up to 100%; `pending` and `unscored` stay out; aggregator and alert-evaluator alike.
   - (c) `topic_id` = `<taxonomy_id>:<node_id>` (`global:outage`); a client taxonomy's topics appear only on that client's rows; label names as in `items.analysis/v1` (aggregator Q5).
   - (d) Entities, brands and media tags in their own aggregator rollup, keyed like the main table with that id in place of the topic, so two multi-valued slices never multiply rows; filled once A3 and A4 run.
   - (e) A `stories` measure: mentions of items with `is_origin = true`, one per story (`news-dedup §13 L160`), items outside news counting as their own story (news-dedup Q4: yes).
   - (f) No per-post LinkedIn rollup: per-post views read the base rows while they exist (48 hours); afterwards LinkedIn lives in the hourly grain like every platform.
   - (g) Reach as of the rebuild, as drafted, settling after an hour's +31 d pass (aggregator Q2); no `top_media` trending score in v1 (ig-hashtag-search Q2); campaign views are keyword slices (ADR-0031).
   - (h) Alerts: the five types. Engagement, topic, entity or logo and story alerts wait for A1 to A4 and D3, and their seven PRDs mark them for a later release (one approved, fb-reactions-fetcher, ADR-0001). No minute grain until the pilot shows missed spikes (`alert-evaluator §12 L138`, Q2); the user approves the defaults the pilot's backtests propose, account managers tune them (Q4); `keyword_first_seen` stays allowed for government clients on reputation and service-quality keywords, aggregate-only (`§5.3 L65`, Q5).

   Consequences: F8 adds five columns, a rollup table and a measure; rows multiply with the language and kind splits (measured in the pilot); every promised view except per-post LinkedIn history has a ten-year source; A5 still needs only C15, C5 and G1.

2. **The grain as written, plus the YouTube owner column**, the promises withdrawn (AU-081 option 3, AU-083 option 2). _Not taken._ Consequences: least work for C15 and F8; language, entity and story views read base tables, so they stop at each platform's purge (48 hours on LinkedIn) and can never be rebuilt for past months.
3. **Everything now:** _Taken, with the per-post LinkedIn history gated by counsel (see Decision)._ option 1 plus per-post LinkedIn rollups kept ten years and the four extra alert types (AU-081 and AU-083 option 1). Consequences: every promise kept; A5 waits for A1 to A4 and for metrics velocity; counsel must first confirm that per-post counts of member activity may outlive LinkedIn's 48-hour and six-week limits (`CONVENTIONS L192`).

## Decision

Option 3, with the per-post LinkedIn history gated by counsel. Every slice of option 1 (a) to (g) goes into the aggregates now, and all nine alert types are built in v1: the five existing ones, and engagement-spike, topic-spike, entity or logo, and story alerts. Per-post LinkedIn rollups are kept ten years only once counsel confirms that LinkedIn's terms allow it; until then none is stored.

**Slices (option 1 (a) to (e) and (g); (f) under the LinkedIn history below)**

- (a) The main grain gains `lang`, `dialect`, `route` and the item `kind` (`post`, `video`, `comment`, `article`, `result`, ADR-0008), so posts and comments count apart (aggregator Q3), and, on YouTube rows, the video's channel (`video_channel_id`), so YouTube figures stay per channel owner except where the carve-out allows totals (ADR-0056 sets their lifetime).
- (b) `mixed` counts in every share's denominator and shows as its own share: negative share = negative ÷ (positive + neutral + negative + mixed), so the four shares add up to 100%; `pending` and `unscored` stay out; aggregator and alert-evaluator alike.
- (c) `topic_id` = `<taxonomy_id>:<node_id>` (`global:outage`); a client taxonomy's topics appear only on that client's rows; label names as in `items.analysis/v1` (aggregator Q5).
- (d) Entities, brands and media tags in their own aggregator rollup, keyed like the main table with that id in place of the topic, so two multi-valued slices never multiply rows; filled once A3 and A4 run. The governorates analysis-entities resolves from the places an item names (`analysis-entities §4 L33`) are entities of this rollup, which gives the anonymous segments of ADR-0010 their region or governorate.
- (e) A `stories` measure: mentions of items with `is_origin = true`, one per story (`news-dedup §13 L160`), items outside news counting as their own story (news-dedup Q4: yes).
- (g) Reach as of the rebuild, as drafted, settling after an hour's +31 d pass (aggregator Q2); no `top_media` trending score in v1 (ig-hashtag-search Q2); campaign views are keyword slices (ADR-0031).

**Per-post LinkedIn history (option 3, gated by counsel)**

- Per-post LinkedIn rollups, the per-post comment rollups that `li-notification-receiver §7 L142`, `li-own-comments-fetcher §7 L135` and `li-post-comments-fetcher §7 L139` promise, are kept ten years once counsel confirms that LinkedIn's terms allow per-post counts of member activity to outlive its 48-hour and six-week limits (`CONVENTIONS L192`).
- Until then none is stored: per-post views read the base rows while they exist (48 hours for member content, ADR-0055), and afterwards LinkedIn lives in the hourly grain like every platform, as option 1 (f) has it.

**Alerts: all nine types in v1**

- The five built types (`alert-evaluator §3 L22`): volume spike, negative share, new high-reach poster, keyword first seen, deletion of a high-reach post.
- Four more, also built in v1:
  - engagement spikes, from the engagement observations of ADR-0034, whose velocity alert-evaluator uses (`fb-reactions-fetcher §4 L33`, `tt-video-stats-refresher §4 L36`); X, LinkedIn, Telegram and Facebook-group counts are recorded at first sight only (ADR-0058), so those routes give no velocity, and in v1 an engagement spike fires only on Facebook Pages, Instagram, TikTok and YouTube, whose counts are refreshed at +24 h and +7 d (ADR-0034, ADR-0058);
  - topic spikes, from the `topic_id` slice of (c) (`analysis-topics §4 L37`);
  - entity or logo alerts, on a named institution or brand or a client's logo in high-reach media, from the rollup of (d) (`analysis-entities §4 L33`, `analysis-media §4 L34`);
  - story alerts, on unique stories rather than copies, from the `stories` measure of (e) and `item_stories` (ADR-0022, `news-dedup §4 L35`).
- A5 waits for A1 to A4 and for metrics velocity. The analysis services fill the topic, entity and media slices the new types read; engagement spikes need the observations of ADR-0034, which C11's metrics lane drives and C6 stores in `metrics_timeseries`, both already behind G1.
- For government clients the allowed types of `alert-evaluator §5.3 C` stand (volume spike, negative share and keyword first seen, aggregate-only), so the four new types are refused for them unless the user and counsel add one (`DEFERRED.md`).
- As option 1 (h) has it: no minute grain until the pilot shows missed spikes (`alert-evaluator §12 L138`, Q2); the user approves the defaults the pilot's backtests propose, and account managers tune them (Q4); `keyword_first_seen` stays allowed for government clients on reputation and service-quality keywords, aggregate-only (`§5.3 L65`, Q5). Each of the three stays in `DEFERRED.md` for its owner to confirm.

It also answers: Reach is recomputed at each rebuild, as drafted (`aggregator §14 Q2`), and posts and comments are counted apart through the item `kind` dimension (`aggregator §14 Q3`).

Why: The user asked for more than option 1 offered: in v1, every alert the PRDs promise, and the per-post LinkedIn history where LinkedIn allows it. A slice left out of the aggregates can never be added for past months, so every slice goes in now; the LinkedIn history waits for counsel because it would keep per-post counts of member activity beyond LinkedIn's limits.

## Consequences

Every view has a ten-year source, the per-post LinkedIn history included once counsel allows it, and every alert the PRDs promise is in v1; rows multiply with the language and kind splits (measured in the pilot); A5 starts later, after A1 to A4.

- CONVENTIONS v1.1: the grain, measures and shares beside the analytics store (v1 L32), with the nine alert types.
- F8 adds the five grain columns, the rollup of entities, brands and media tags, and the `stories` measure; the per-post LinkedIn rollup waits for counsel.
- The build plan: A5's "Needs first" gains A1, A2, A3 and A4 (`build-plan/tools/sessions.py`, the briefs regenerated), citing this ADR.
- The seven PRDs that promise the four alert types (fb-reactions-fetcher, tt-video-stats-refresher, analysis-topics, analysis-entities, analysis-media, news-dedup and alert-evaluator) are not marked for a later release; alert-evaluator's "five rule types" (`alert-evaluator §3 L22`) are nine under this ADR.
- `DEFERRED.md`: counsel on per-post LinkedIn rollups kept ten years (the user with counsel, before LinkedIn's go-live; C15 and F8 act on the answer); the minute grain (A5, after the pilot); a trending score (U3); reach frozen at first sight (C15); who approves alert defaults (the user, asked by A5); `keyword_first_seen` and the four new types for government clients (the user with counsel, before A5).

Sessions that must read this: F8, then C15, A5, A1, A2, A3, A4, C3, N7, YT4, YT5, LI2, LI3, VLI4, FB4, VTT6, D3, U3 (the trending score, `DEFERRED.md`).
