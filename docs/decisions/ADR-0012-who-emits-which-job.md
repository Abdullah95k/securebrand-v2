# ADR-0012 · Who emits which job

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q012 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS gives every poller its own scheduler, comment, reply and metrics jobs to comment-decay-scheduler alone, and backfill to backfill-orchestrator alone (L278). Three gaps remain:

- Kinds no producer emits (CF-078), above all the ops and client requests that many consumers accept and nothing writes (CF-078 a).
- Kinds a consumer refuses (CF-079), such as the scheduler's daily `health` job for Telegram groups (`comment-decay-scheduler §5.1 L57`), which tg-discussion-receiver does not accept and already runs as `reconciliation` (`tg-discussion-receiver §5.1 L47`, `§6.1 L110`; AU-033, AU-099).
- Comment work from other services (CF-080): ig-webhook-receiver's reconciliations and targeted reads (`ig-webhook-receiver §5.1 L43`, `§5.2 L57`; AU-086); yt-text-purger's `refresh` jobs (`yt-text-purger §5.3 L96`); backfill-orchestrator's comment jobs for new LinkedIn pages (`li-own-comments-fetcher §5.1 L52`). The LinkedIn daily reconciliation expected from the scheduler (`li-own-comments-fetcher §5.1 L48`, `li-notification-receiver §5.1 L44`) is not there; the scheduler reads no `item.metrics` (`comment-decay-scheduler §6.1 L135`) (CF-078 g, AU-034).

At stake: features nothing triggers, and jobs their consumer parks.

Settles: CF-078, CF-079, CF-080, AU-033, AU-034, AU-086, AU-099, ig-webhook-receiver §14 Q3, tt-client-videos-fetcher §14 Q5.
Depends on: ADR-0011 (the kind list), ADR-0017 (`jobs.completed`), and the decisions cited for single rows.

## Options

1. **A producer table in F2, checked by the SDK; the single-emitter rules kept with named exceptions; ops and client requests through the admin API** (chosen): its rules are under Decision.
2. **The strict rule: every comment, reply and metrics job through comment-decay-scheduler (CF-080 option 2).** Consequences: no exceptions, but the scheduler must take requests from ig-webhook-receiver and yt-text-purger.
3. **No rule: each consumer lists its own producers (CF-080 option 3).** Consequences: least change now, but nothing says who may write a queue, two jobs can be in flight on one post, and ops jobs have no schema or audit.
4. **As 1, but push routes reconcile from their own receiver or poller, or not at all (AU-034 options 2, 3).** Consequences: the scheduler reads no counts, but LinkedIn needs a new scheduler or relies on its series steps to catch missed webhooks.

## Decision

F2 publishes a producer table, one row per queue and `kind` with its allowed producers, which the SDK enforces. CONVENTIONS' single-emitter rules stay, with the cross-service producers named below, and ops and client requests reach a queue only through the admin API.

- The table: one row per (queue, `kind`) with its allowed producers; the SDK producer refuses, and the consumer's wrapper dead-letters, a job whose (queue, `kind`, `producer.service`) is not listed; a kind with no row leaves its consumer.
- Rows: each rotating service's scheduler emits `rotation`, `reconciliation` and `refresh` on its own queue, tg-discussion-receiver's daily check per group included (the `tg_own` row emits nothing; no `health` kind), and fb-page-search makes a keyword-rule row due at once when it is `added` or `updated` (its `seed`, ADR-0044). comment-decay-scheduler: `comments`, `replies`, `metrics`; backfill-orchestrator: `backfill` (web-commoncrawl-scanner's queue included, ADR-0059) and `keyword_history` (on a client's request and for every new X keyword rule, ADR-0059); poster-resolver: `resolve`; registry-writer: `manual_candidate`; each analysis service: `analyze`; keyword-matcher: `candidate_retry`; each buffering receiver: `push`.
- Named cross-service producers: ig-webhook-receiver (below); yt-text-purger, `refresh` to the YouTube fetchers (ADR-0065); the three news pollers and news-comments-fetcher, event-triggered `refresh` to news-site-resolver (ADR-0032); x-filtered-stream, `reconciliation` on `jobs.x-recent-search` (ADR-0064); yt-pubsub-receiver, yt-uploads-reconciler, yt-keyword-search and search-hit-router, `first_sight` (ADR-0037, ADR-0065); retention-purger, `retention_sweep`; deletion-propagator, `recompute` (ADR-0035); news-site-resolver, `first_check`, and the news services through the SDK host gate, `recheck` (ADR-0022). tt-client-videos-fetcher's own metrics need no job (ADR-0024).
- Ops and client requests (CF-078 a): the admin API (D3 specifies it) is their only writer, through one SDK call with a schema per kind, `request_id`, `requested_by` and an audit record: `ops_force`, `replay`, `rerun` (a client's new topic included), `rematch` (also on a keyword change), `recompute`. A request touching a post's schedule or a backfill goes to its owner, which emits the job, so one job stays in flight per post (`comment-decay-scheduler §5.1 L62`): post refreshes to comment-decay-scheduler (`series_step = refresh:<request_id>`), backfill re-runs to backfill-orchestrator (`backfill-orchestrator §5.1 L50`).
- Push routes (AU-034): for LinkedIn, comment-decay-scheduler reads li-client-posts-poller's comment counts on `item.metrics` and, while a post is under 7 days old, emits a daily whole-thread `reconciliation` when the count differs from its series' running total; Instagram keeps ig-webhook-receiver's scheduler. Pushed comments in early stop are ADR-0019's.
- ig-webhook-receiver (AU-086, CF-079 d): ig-own-comments-fetcher expands the per-account reconciliation to the account's media inside their first 7 days, from ClickHouse `items`; a targeted read is `ops_force` with `post_ref` (a media) or `target_ids` (mention ids), which ig-mentions-fetcher adds; both fetchers report on `jobs.completed` (ADR-0017); the receiver sets the next due time from the reconciliation's start (CONVENTIONS L51).
- The rest, by decision: CF-078 b, f and CF-079 c (ADR-0032); CF-078 c (ADR-0060); d, `replies` on `jobs.x-full-archive-search` for the X reply steps after day 7, from comment-decay-scheduler (ADR-0059); e (ADR-0037); h and CF-079 e (ADR-0020, ADR-0034, ADR-0058, ADR-0064, ADR-0065); CF-079 a, news backfill through news-sitemap-poller, with web-commoncrawl-scanner listing what the sitemaps do not reach (ADR-0020, ADR-0059); CF-080 d, the scheduler's `once` step (`backfill-orchestrator §5.1 L48`, ADR-0060).

Why: It keeps one owner per post schedule and per backfill, names the few services that rightly write into another's queue, and gives ops and client requests one audited writer.

## Consequences

F2 publishes the table; comment-decay-scheduler gains `item.metrics` as an input; the LinkedIn and Instagram comment fetchers change; approved PRDs change under ADR-0001 (web-search-perplexity loses `site_search`, poster-resolver its answer kinds, li-org-resolver the qualifier as a producer).

- CONVENTIONS v1.1: the single-emitter rule of v1 L278 becomes the producer table with its named exceptions, and the admin API is the only writer of ops and client requests. The Telegram own-channels row's "daily health check" is tg-discussion-receiver's own `reconciliation`.
- D3 specifies the admin API and its request schemas (`request_id`, `requested_by`, one audit record per request).

Sessions that must read this: F2, F4, then C4, C5, C8, C10, C11, C15, A1, A2, A3, A4, FB3, IG4, IG5, IG6, LI2, LI3, VLI2, VLI4, TT1, TG2, VTG2, X5, YT4, YT5, YT6, YT7, YT9, W1, W2, W3, N2, N3, N4, N5, N8, D3.
