# ADR-0037 · Web-search results path

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, raw-archiver, search-hit-router, yt-web-search-bridge, yt-video-details-fetcher, and web: web-search-perplexity, web-search-mojeek, web-gdelt-poller, web-commoncrawl-scanner
Source: D2-Q037 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

The three engines write `search.results/v1` with a `query` object, a `result` object, `canonical_url_hash` and `retention_class` (`web-search-perplexity §6.2 L92-L108`; web-search-mojeek and web-gdelt-poller use the same shape) and archive every response on `raw.items` with `kind_hint = search_response` and `normalize = skip` (`web-search-perplexity §5.2 L55`). yt-web-search-bridge, an approved PRD, writes another layout with `query` as a string and no `schema`, `message_id` or class (`yt-web-search-bridge §6.2 L106-L124`); it marks results `handled_by` so that search-hit-router skips them, which the router never reads (`§4 L37`, `search-hit-router §5.2 L55`; CF-023); and it archives nothing although its PRD says raw-archiver does (`yt-web-search-bridge §8 L148`; AU-011). web-commoncrawl-scanner writes under `raw/` directly (`web-commoncrawl-scanner §5.2 L54`; AU-029). web-search-perplexity, also approved, serves `site_search` jobs for the bridge, which sends none and calls Mojeek and Perplexity itself (`web-search-perplexity §3 L25`, `yt-web-search-bridge §5.2 L58`; AU-108). The router emits candidate keys no resolver takes, and the bridge sends `resolve` jobs that bypass poster-resolver (AU-109). Three engines count on the router to judge results Iraqi and to report yields back; the router judges nothing Iraqi (`search-hit-router §5.4 L89`; AU-110). What is at stake: every bridge result parked or routed twice, paid responses never archived, and engine metrics with no source.

Settles: CF-023, AU-011, AU-029, AU-108, AU-109, AU-110, search-hit-router §14 Q1, search-hit-router §14 Q4, web-search-mojeek §14 Q4.
Depends on: ADR-0008 (the archive-only `search_response` kind), ADR-0032 (candidate keys), ADR-0036 (hash rendering).

## Options

1. **One results schema, every response archived, one router for YouTube links** (chosen): its rules are under Decision.
2. **The bridge sends `site_search` jobs to the engines, which call, archive and publish, and keeps routing its own YouTube results, marked `handled_by`, which the router counts and skips (AU-108 option 1, CF-023 option 1).** Consequences: the router learns one skip rule, but two services turn YouTube links into jobs, and the bridge's `resolve` jobs still bypass poster-resolver unless they change too.
3. **The bridge stops writing `search.results` (CF-023 option 2).** Consequences: the router has three producers, the bridge's results reach nothing else, and the bridge must still archive its responses.

## Decision

The four producers write one `search.results/v1` message and archive every response on `raw.items` as the archive-only kind `search_response`. search-hit-router routes every YouTube link, the bridge's included; the bridge calls the engines itself and sends no jobs.

- `search.results/v1` is the engines' message, for all four producers: ADR-0002's metadata, `engine`, `source_id` (the keyword rule, ADR-0004) with the `keyword_ids` and `client_ids` it serves (ADR-0044), `query {text, variant, lang, country, request_id}` (an object everywhere; `lang` is the language asked for, whatever the engine's mechanism, null for GDELT), `result {rank, title, url, snippet, date, last_updated}`, `canonical_url`, `canonical_url_hash` (bare hex, ADR-0036), `raw_ref`, provenance and `retention_class` (ADR-0003); optional `hints` (GDELT). The bridge's `idempotency_key`, `platform_hint`, `handled_by`, `cost` and `extracted` go.
- Archive: each engine and the bridge write every response to `raw.items` as the archive-only kind `search_response` (ADR-0008), replacing `kind_hint` and `normalize = skip`; since normalize-item skips the kind, an unknown response shape is parked by the engine's adapter. web-commoncrawl-scanner archives its per-host aggregate the same way and writes nothing under `raw/` (ADR-0039). `search.results` is derived data and is not archived.
- The bridge calls Mojeek (by default) and Perplexity itself through the shared SDK clients, on the tags `mojeek_search` and `perplexity_search` with its own sub-counter (ADR-0042). `site_search` leaves web-search-perplexity, and web-search-mojeek's line about it goes.
- Routing: search-hit-router routes every YouTube link, the bridge's included, and the bridge sends no jobs. A watch, shorts or youtu.be URL becomes a `first_sight` job on `jobs.yt-video-details-fetcher` with the rule's `source_id` (one id per job, ADR-0065), so the video becomes an item and its channel reaches poster-resolver as keyword-matcher's candidate; `@handle` and `channel/UC…` URLs become `youtube:<handle or id>` candidates; legacy `c/` and `user/` names, and Instagram URLs with no readable handle, end `unroutable`; groups and sites take the typed keys of ADR-0032. The router's 30-day re-route window replaces the bridge's 7-day sent set.
- Iraqi-ness: judged by the qualifier after resolution. The engines drop `variant_yield`, `iraqi_host_share`, `unique_domain_share` and a reported-back `items_new_total`; yield per engine and variant comes from the router's metrics (`search-hit-router §10 L164`) and a pilot report joining its `search_url_seen` and `search_candidate_seen` rows to the qualifier's `decisions`. Retiring a variant is a manual pilot decision; no feedback loop in v1.

Why: Routing web links is search-hit-router's job, so giving it the YouTube links too removes a second router, the skip marker and the direct resolver jobs; archiving every response through `raw.items` gives every paid result its provenance.

## Consequences

Approved PRDs move under ADR-0001 (yt-web-search-bridge loses its jobs and `handled_by`, web-search-perplexity loses `site_search`); search-hit-router replaces the bridge as a producer of `first_sight` jobs in ADR-0012's table, and yt-video-details-fetcher names it; the bridge's spend shows under the engines' caps.

- CONVENTIONS v1.1: the `search.results` message (v1 L26); the search output rule (v1 L281): the engines and the bridge archive every response, and search-hit-router routes YouTube links.
- F2 types `search.results/v1`; ADR-0012's producer table names search-hit-router for `first_sight` jobs on `jobs.yt-video-details-fetcher`.
- `DEFERRED.md`: retiring a query variant, a manual decision from the pilot report (owner W3).

Sessions that must read this: F2, C1, C2, C4, C8, FB1, IG1, YT1, YT4, YT9, W1, W2, W3, W4, W5.
