# ADR-0057 · Quota answers, attempts and the DLQ

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all (every service with a `budget_tag`), listening-sdk (F4, F5, F6), quota-governor, comment-decay-scheduler, backfill-orchestrator
Source: D2-Q057 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

The governor answers allow, wait-until or deny (`CONVENTIONS L85`); a deny (`flag_off`, `period_full`, `priority_gate` on monthly tags) lasts until the period resets or the mode changes (`quota-governor §5.3 L67`, `L70`, `L71`). The callers disagree:

- Deny (CF-090): five TikTok services and fb-backfill requeue with `attempt + 1` (`tt-hashtag-feed-poller §5.2 L56`, `fb-backfill §5.2 L55`), dead-lettering a whole tag within five tries once a month is full; others keep `next_poll_at` (`tt-client-videos-fetcher §5.2 L57`), finish `quota_denied` (`yt-comments-fetcher §5.2 L53`), wait (`tg-message-search §13 L147`), drop a step after 24 hours against README decision 2's held +24 h step (`li-post-comments-fetcher §5.1 L52`, `README L179`), end `capped` (`x-full-archive-search §5.1 L43`) or delete (`yt-text-purger §8 L193`). On wait-until two TikTok services sleep in the worker (`tt-keyword-search §5.2 L50`).
- DLQ (CF-091): "after 5 attempts" (`CONVENTIONS L100`), but five criteria test "the sixth failure" (for example `tg-channel-posts-poller §13 L186`); error 80001 is both a one-interval deferral and a counted retry (`fb-page-feed-poller §7 L138`, `§8 L145`).
- Provider failures (AU-066) never reach the governor's counters (`quota-governor §5.1 L37`), so after out-of-credits or a YouTube `quotaExceeded` other services still get `allow` (`ig-comments-fetcher §8 L131`, `yt-keyword-search §8 L139`).
- Stretch (AU-113): the governor publishes `stretch_factor` for "every amber poller's scheduler" (`quota-governor §4 L30`, `§5.1 L51`); the pollers say the governor stretches them (`fb-group-posts-poller §5.1 L46`); tg-channel-posts-poller wants a fixed order (`§5.1 L52`).

At stake: as written, a full budget fills the DLQs with alerts while nothing slows down.

Settles: CF-090, CF-091, AU-066, AU-113.
Depends on: ADR-0011 (the job envelope), ADR-0016 and ADR-0021 (credential state, 401 and 403), ADR-0017 (`quota_denied`), ADR-0018 (priorities and modes), ADR-0050 (flag off).

## Options

1. **Quota answers are never failures: one rule in the SDK wrapper and scheduling kit** (chosen): its rules are under Decision.
2. **As option 1, but the governor stretches by answering `wait_until` at the stretched due time** (AU-113 option 2). Consequences: one enforcement point and the pollers' wording stands, but the governor needs each job's interval and last start (its request has neither, `quota-governor §5.1 L37`), each stretched poll costs a requeue and a second call, and rotation-lag alerts fire for merely stretched sources.
3. **`deny` parks the job until the period or mode changes** (CF-090 option 2). Consequences: steps are held with no scheduler change, but parked jobs pile up for weeks on monthly tags and are released in one burst at the reset.
4. **Per-route rules as written** (CF-090 option 3), the sixth failure kept by rewording `CONVENTIONS L100`, 80001 a counted retry, a counter-only governor. Consequences: the least editing; a dozen behaviours to test; services keep calling after `quotaExceeded`.

## Decision

A quota answer is never a failure. A `deny` ends the job `quota_denied` and its producer retries on its own schedule; a `wait-until` requeues the job with its attempt unchanged; attempts count provider failures only, and the fifth failed attempt goes to the DLQ; the SDK scheduling kit applies the amber stretch.

- `deny`: no call; the job ends `quota_denied` (ADR-0017), never an attempt or DLQ entry (`flag_off` ends `skipped_flag_off`, ADR-0050), and its producer retries: rotation sets the next due time from the denied run's start (the cursor has not moved); comment-decay-scheduler holds the step until the tag's mode admits it, on every route's tag, merging it with the next step as it merges hot extras (`§5.1 L62`), so the +24 h step is never dropped (li-post-comments-fetcher's 24-hour drop goes); a backfill ends `capped` with `capped_reason = budget` (`backfill-orchestrator §5.3 L81`); yt-text-purger deletes, as the 30-day rule requires; poster-resolver keeps the candidate `pending`, as for a degraded resolver (`poster-resolver §8 L108`).
- `wait-until`: requeue for that time, `attempt` unchanged; no worker sleeps. A job may carry `must_finish_by` (yt-text-purger's field, `§5.3 L102`): the next due time for rotation, the next step's for comment steps, the deadline for backfills; a later `wait_until` counts as a deny, as x-full-archive-search and yt-text-purger already rule.
- Attempts count provider failures only (429 and vendor rate limits after backoff, 5xx, timeouts), from 1; the fifth failed attempt goes to `dlq.<service>` with an alert; the five criteria are corrected.
- 80001, a throttle on one Page: a wait (until Meta's estimated time to regain access, otherwise one rotation interval, `fb-page-feed-poller §7 L138`), never an attempt, counted per Page for the alert (`quota-governor §5.3 L80`).
- `report` carries an error class: `quota_exceeded` sets `youtube_data_api` to `exhausted` until the provider's reset, `out_of_credits` sets the vendor tag to `exhausted` until an audited ops raise (`quota-governor §5.1 L49`); a 403 whose reason is quota counts as `quota_exceeded`; only an authorisation 401 or 403 goes to credential and health state, not the governor (ADR-0016, ADR-0021).
- Stretch, amber tags only (ADR-0018): the F5 scheduling kit applies `min(tier_interval × stretch_factor, 24 h)` with the factor the governor publishes in `budgets`, so no poller code reads it. Telegram's order follows: backfill (priority 5) stops at 80%, and Tier 2 (6 h) reaches the 24-hour ceiling at factor 4 while Tier 1 (60 min) is at 4 hours.

Why: A budget answer is not a failure, so it should never burn retries or fill a DLQ; leaving the retry to the producer keeps each schedule's own rule (held steps, capped backfills, YouTube deletion). The stretch is applied where intervals are computed, as the governor's PRD designs it, at no extra call.

## Consequences

One implementation and test set in F4 and F5; ADR-0011's envelope gains the optional `must_finish_by`; six approved PRDs move under ADR-0001 (fb-backfill, fb-page-feed-poller, tt-hashtag-feed-poller, tt-keyword-search, tg-message-search, web-search-perplexity) among about thirty aligned lines; a long budget pause costs freshness and backfill depth, never DLQ noise.

- CONVENTIONS v1.1: the handling of each governor answer, `must_finish_by` and the error classes (v1 L85); five attempts, with quota answers and error 80001 not counted as attempts (v1 L100); the stretch formula, applied by the SDK scheduling kit (v1 L51).
- F4 builds the rule in the job wrapper and F5 in the scheduling kit, with one test set; the job envelope gains the optional `must_finish_by` (ADR-0011).

Sessions that must read this: F4 (the job wrapper), F5 (the scheduling kit), F6, C1, C10, C11, C12, then FB2, FB3, VFB2, VIG1, VIG2, TT1, VTT1, VTT2, VTT3, VTT4, VTT5, X5, X6, YT5, YT7, YT8, VLI3, VLI4, VTG1, VTG3, W1, W2, N8.
