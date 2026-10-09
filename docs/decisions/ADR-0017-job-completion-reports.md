# ADR-0017 · Job completion reports

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q017 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

README decision 1 proposes a completion topic `jobs.completed` (`jobs.completed/v1`), "written by the listening-sdk job wrapper after every job with a report (`new_count`, `seen_count`, `pages`, `cost_units`, `reply_candidates`)", read by comment-decay-scheduler and backfill-orchestrator (`README L178`; `comment-decay-scheduler §14 Q1 L202`). CONVENTIONS has no such topic; a fetch only "reports" four counts (L62). D1 found (CF-024, CF-089, AU-001): three services publish the topic themselves (`yt-uploads-reconciler §5.2 L66`, `yt-video-details-fetcher §5.2 L63`, `x-full-archive-search §6.2 L128`); others report through `service_runs` (`news-comments-fetcher §5.2 L59`, `li-post-search §5.2 L61`), "the job result" (`ig-comments-fetcher §5.2 L63`) or "the completion message" (`tt-video-stats-refresher §6.2 L112`); the two consumers' examples carry different report blocks (`comment-decay-scheduler §5.4 L127`, `backfill-orchestrator §5.4 L92`); `seen_count` means "posts with `paid = false`" in one PRD and "edits included" in another (`x-user-timeline-poller §5.2 L61`, `x-replies-fetcher §5.2 L62`); no document lists the statuses or says which end a series (`yt-comments-fetcher §8 L155`, `L156`; `x-replies-fetcher §14 Q4 L202`); and x-recent-search, whose reports two services read (`x-filtered-stream §5.2 L71`, `x-full-archive-search §5.2 L52`), never names the topic. D1's review note 12 adds that CONFLICTS.md section 4 row 1 cites CF-089 and AU-001 but not CF-024. At stake: a series or a backfill advances only on a report its consumer can read.

Settles: RD-1, CF-024, CF-089, AU-001, RN-12, comment-decay-scheduler §14 Q1, fb-post-comments-fetcher §14 Q6, x-replies-fetcher §14 Q4.
Depends on: ADR-0002 (message metadata), ADR-0011 (the job envelope), ADR-0057 (quota answers and the DLQ).

## Options

1. **README decision 1, with one schema and the wrapper as the only writer** (chosen): its rules are under Decision.
2. **As 1, and services may also publish completions the wrapper does not see (CF-089 option 2).** Consequences: x-full-archive-search's hand-back could stay as written, but two writers can report one job twice and the once-per-job guarantee is lost.
3. **No topic: result rows in `service_runs` or a job-results table that the consumers poll (`comment-decay-scheduler §14 Q1 L202`).** Consequences: no new topic, but polling delay on every series step and a hot table with one row per job.
4. **A small required core plus a free `extra` object stored uninterpreted (AU-001 option 3).** Consequences: flexible, but consumers cannot validate the fields they act on.

## Decision

README decision 1 stands: the SDK job wrapper writes exactly one `jobs.completed/v1` report per job, a job that ends in the DLQ included, with a closed list of statuses whose meanings are fixed. Services return a report object and never publish a completion themselves.

- Writer: the SDK job wrapper, exactly once per job, a job that ends in the DLQ included. Services return a report object and never publish themselves; a service that serves several jobs with one call (yt-video-details-fetcher's collector) returns one report per job.
- Common fields: ADR-0002's metadata, `job_id`, `queue`, `kind`, `source_id`, `post_ref` and `series_step` where the job had them, `attempt`, `status`, `finished_at`, and `report {new_count, seen_count, pages, cost_units, reply_candidates}`. `new_count` counts items not stored before; `seen_count` items read that were already stored, edits included; billing detail (X's free re-reads, `paid_user_reads`) goes in kind fields.
- `status`, closed, one meaning each: `done`, `partial` (stopped early, what was read is stored) and `capped` (with `capped_reason`) advance the series; `quota_denied` is never an attempt (a series step is held, a backfill ends `capped`, ADR-0057); `failed` (the DLQ) marks the step missed or ends a backfill `capped`; `skipped_flag_off`, `not_allowed` (government client, outside the route's window, not a conversation root) and `gone` (video or post not found, comments disabled) end the series, each with a `reason`. `ok` gives way to `done`.
- Kind fields, declared per kind in F2: backfill `oldest_item_at` and `capped_reason` (replacing `coverage_days`, `oldest_seen`, `urls_emitted`); comments and replies `complete`, with every thread list (`reply_threads`, incomplete threads) folded into `reply_candidates`. Per-post markers (`newest_comment_at`, `thread_id`) live in the fetcher's `cursors` rows (ADR-0046), not in reports; x-full-archive-search's reply steps after day 7 take their starting point from the job (`window_start`, ADR-0059, ADR-0064), not from a report.
- Keyed like the job it reports on (ADR-0004). Readers: comment-decay-scheduler, backfill-orchestrator, x-filtered-stream, x-full-archive-search, and deletion-propagator for recomputes (ADR-0035). `service_runs` keeps per-service status only (ADR-0045).
- RN-12: CF-024 is settled here with CF-089 and AU-001; CONFLICTS.md stays D1's record.

Why: The wrapper already runs after every job, so it is the one place that can guarantee exactly one report per job, and a closed status list with fixed meanings is what lets comment-decay-scheduler and backfill-orchestrator end a series or a run correctly.

## Consequences

X-recent-search (approved, ADR-0001) reports through the wrapper with no code of its own; li-post-search and ig-hashtag-search (approved) move or rename their counters; F2 defines the schema and the status table; F4 and F6 build it once.

- CONVENTIONS v1.1: the topic list gains `jobs.completed`, and the comment fetch's report (v1 L62) points to it.
- F2 defines `jobs.completed/v1`, its closed status table and the fields of each kind; F4 and F6 build the writer once, in the wrapper.
- RN-12 is closed by this record: CF-024 is settled here with CF-089 and AU-001, and `CONFLICTS.md` stays D1's record.

Sessions that must read this: F2, F3, then F4, F5, F6, C10, C11, FB3, FB5, VFB3, IG2, IG6, VIG2, LI2, VLI4, VTT5, VTT6, X1, X3, X4, X5, X6, YT3, YT4, YT5, YT6, N4, N8.
