# ADR-0032 · Resolvers and the resolve job

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, listening-sdk (F4, F6), poster-resolver, qualifier, registry-writer, search-hit-router, web-commoncrawl-scanner, yt-web-search-bridge, news-feed-poller, news-sitemap-poller, news-homepage-differ, news-comments-fetcher, and the eight resolvers: fb-page-resolver, ig-account-resolver, tt-user-resolver, x-user-resolver, li-org-resolver, tg-channel-resolver, yt-channel-resolver, news-site-resolver
Source: D2-Q032 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

poster-resolver, an approved PRD, sends each candidate a `resolve` job with `"reply_to":"jobs.poster-resolver"`, waits there for `resolved` or `unresolvable`, merges the answers into `poster.profiles`, and after 5 unanswered attempts marks the candidate `unresolvable: timeout` (`poster-resolver §1 L9`, `§5.3 L67`, `L70`, `§8 L107`). No resolver writes that queue: all eight publish `poster.profiles` themselves (`fb-page-resolver §6.2 L99`, `ig-account-resolver §6.2 L102`, `tt-user-resolver §6.2 L86`, `x-user-resolver §6.2 L101`, `li-org-resolver §6.2 L79`, `tg-channel-resolver §6.2 L77`, `yt-channel-resolver §6.2 L103`, `news-site-resolver §6.2 L79`), so as written every candidate times out (CF-012, AU-007). The job differs per queue (CF-085, AU-056, AU-111): most resolvers read `client_ids`, which poster-resolver's job lacks; li-org-resolver re-keys candidates as `linkedin:org:<handle>` (`li-org-resolver §5.2 L50`); a flag that is off ends three ways (`poster-resolver §5.2 L56`, `tt-user-resolver §5.2 L53`, `li-org-resolver §5.2 L53`). Routers emit keys no resolver parses (`search-hit-router §5.3 L74-L83`; CF-073), and some producers that resolvers name emit nothing (CF-085 d, e). Six resolvers refresh registered sources on their own loops under two kind names; tt-user-resolver has no loop, and li-org-resolver waits for `refresh` jobs from the qualifier, which emits none (`li-org-resolver §5.1 L44`, `qualifier §6.2 L81`; AU-059, AU-112). What is at stake: as written no candidate is ever resolved, and tiers on TikTok and LinkedIn go stale.

Settles: CF-012, CF-073, CF-085, AU-007, AU-056, AU-059, AU-111, AU-112, fb-page-resolver §14 Q1, poster-resolver §14 Q2, tt-user-resolver §14 Q2, x-user-resolver §14 Q6, yt-channel-resolver §14 Q5.
Depends on: ADR-0017 (`jobs.completed`), ADR-0033 (the profile schema), ADR-0050 (flags).

## Options

1. **Resolvers publish their own profiles; poster-resolver dispatches, deduplicates and caches** (chosen): its rules are under Decision.
2. **Resolvers answer on `jobs.poster-resolver` and only poster-resolver writes `poster.profiles`, as its PRD says.** Consequences: eight resolver PRDs change their writes and need an answer schema; poster-resolver keeps merging and stays the single writer, at the cost of one more hop; the job, key, flag and refresh points stand as in option 1.
3. **Both write, each message marked answer or merged profile, and the qualifier decides only on merged ones.** Consequences: two layouts on one topic and twice the messages for the same facts.

## Decision

The eight resolvers publish their own profiles on `poster.profiles`; poster-resolver dispatches one `resolve` job per candidate, deduplicates and caches, and learns from `jobs.completed` that a job ended without a profile. Every resolver refreshes its registered sources on its own 30-day loop.

- Each resolver classifies `account_type` with rule 1 and applies the individuals rule through one SDK function, which also applies ADR-0010's public-account test, then writes `poster.profiles` in ADR-0033's schema, archiving its raw response as `profile` (ADR-0008) except for an ordinary individual (ADR-0010). poster-resolver consumes `poster.profiles` into `poster_profiles` (the one cache, ADR-0045) and drops `reply_to`, the answer kinds, merging and its own signal computation, and tg-channel-resolver stops reading `poster.profiles` as a cache (`tg-channel-resolver §6.1 L73`); it writes the topic only to re-emit a cached profile with `cached: true` on a repeat hit (`poster-resolver §5.2 L53`). It learns from `jobs.completed` that a job ended without a profile, instead of a 15-minute timer: the candidate waits, and the next hit dispatches it again.
- One `resolve` job for all eight queues: `job_id`, `kind`, the issued `candidate_key` (echoed, never re-keyed; poster-resolver aliases a handle to the returned id, `§12 L134`), `platform`, `platform_id`, `handle` or `url`, `origin` (`discovery`, `manual`), `client_ids`, `seed_list`, `attempt`, `due_at`; priority derived by the SDK (ADR-0018). `reply_to`, `hit_url`, `sample_posts`, `url_or_handle` and tg-channel-resolver's `candidate` go. Kinds: `resolve` (poster-resolver), `refresh`, `ops_force` (the admin API, ADR-0012).
- Flag off, one outcome: poster-resolver sends no job (ADR-0050); a queued job ends `skipped_flag_off`; no profile, the candidate waits. `unresolvable: route_off` and `vendor_route_off` go, so no candidate is rejected for 180 days because a flag was off.
- Keys: CONVENTIONS' two forms for accounts, plus `facebook:group:<id>` and `news:site:<registrable domain>` for candidates that are not accounts; routers map every other form before emitting (ADR-0037). Group candidates go to fb-page-resolver, which gains an amber path behind `FB_VENDOR_ROUTE`: one vendor read of the group's recent posts (name, member count where returned, last post, a sample), built after the Facebook vendor probe (VFB0).
- Producers: `resolve` comes only from poster-resolver, which also carries registry-writer's manual candidates (`registry-writer §5.2 L61`; li-org-resolver's `seed` origin goes); the qualifier, web-gdelt-poller and yt-web-search-bridge send none. The event-triggered `refresh` jobs to news-site-resolver from the three news pollers and news-comments-fetcher (`news-comments-fetcher §8 L139`) stay, as named producers (ADR-0012). An unreadable Telegram channel goes to registry-writer as a source-level `health_change` (ADR-0016) and to ops, not to the qualifier.
- Refresh: every resolver refreshes its registered sources on its own 30-day loop with `kind = refresh` (`rotation` renamed); tt-user-resolver and li-org-resolver gain one, its cadence a setting the pilot can lengthen on amber routes; ig-account-resolver seeds a due time for registered accounts that lack one. A refreshed profile carries `source_id`, and the qualifier turns a crossed tier boundary into `tier_change` (`qualifier §8 L106`).

It also answers: Each resolver archives its own raw lookups as `profile` records on `raw.items` (ADR-0008), individuals minimised as ADR-0010 says (`poster-resolver §14 Q2`).

Why: It keeps what eight PRDs already do and changes one, needs no answer queue, and gives every key a router emits a resolver that can parse it.

## Consequences

One decision per resolution; approved PRDs move under ADR-0001 (poster-resolver above all, li-org-resolver, tg-channel-resolver, news-site-resolver, the qualifier, registry-writer, yt-web-search-bridge); the `individual_leak` test moves to the SDK function.

- CONVENTIONS v1.1: the writers of `poster.profiles` (v1 L19), the eight resolvers, and poster-resolver only to re-emit a cached profile; the `resolve` and `refresh` kinds (v1 L277, with ADR-0011); the candidate key forms (v1 L281), the two account forms plus `facebook:group:<id>` and `news:site:<registrable domain>`, which routers map to before they emit.
- F2 types the one `resolve` job; F4 and F6 build the individuals-rule function, with ADR-0010's public-account test.
- fb-page-resolver gains its amber group path behind `FB_VENDOR_ROUTE`, built after VFB0.
- `DEFERRED.md`: the refresh cadence on the amber resolvers (owners VTT3 and VLI2).

Sessions that must read this: F2, F4, C7, C8, C9, FB1, IG1, IG2, VTT3, VTT6, X2, VLI2, VLI3, VTG2, VTG3, YT1, YT9, N2, W3, W4, W5.
