# ADR-0011 · Jobs: envelope, kinds and `post_ref`

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q011 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS gives a job seven `kind` values and six other fields (L277). The PRDs use about thirty kinds (CF-077 c), name the type `reason` in four approved PRDs (`fb-page-feed-poller §5.2 L54`, `fb-backfill §5.1 L41`, `fb-page-search §5.1 L40`, `x-recent-search §5.2 L53`), send jobs with no type (`tg-message-search §5.2 L51`), and add undeclared fields (CF-077 e). `post_ref` is an object from its only emitter (`comment-decay-scheduler §6.2 L141`) but a different string in each consumer, from `<page-id>_<post-id>` (`fb-post-comments-fetcher §5.1 L42`) to a URN (`li-own-comments-fetcher §5.1 L38`) or nothing (`fb-reactions-fetcher §5.2 L53`) (CF-074, AU-036). Webhook receivers buffer three ways (CF-086): ig-webhook-receiver appends the body as `kind = push` and finds the source afterwards (`§5.2 L55`, `L56`); fb-client-webhook-receiver and yt-pubsub-receiver map the source first and buffer with no kind (`fb-client-webhook-receiver §5.2 L54`, `yt-pubsub-receiver §5.2 L53`); the Telegram and LinkedIn receivers write `raw.items` before answering (`tg-bot-channel-receiver §5.2 L62`). RN-11: `first_run` on `jobs.x-recent-search` has no emitter (`x-recent-search §5.1 L39`). At stake: the SDK wrapper validates every job, so whatever it does not know is refused or slips through.

Settles: CF-074, CF-077, CF-086, AU-036, RN-11, x-full-archive-search §14 Q1, yt-pubsub-receiver §14 Q5, yt-replies-fetcher §14 Q3.
Depends on: ADR-0004 (keys), ADR-0006 (`job_id`), ADR-0007 (the id in `post_ref`), ADR-0012 (producers), and the decisions cited for single kinds.

## Options

1. **One envelope, one field `kind`, a closed kind list with declared fields** (chosen): its rules are under Decision.
2. **CONVENTIONS' seven kinds only, the extra meaning in other fields (CF-077 option 3).** Consequences: the shortest list, but resolver, ops and news jobs have no natural kind, and every consumer dispatches on `series_step` or `reason` itself.
3. **A common envelope plus kinds each service declares for its own queue (CF-077 option 2).** Consequences: nothing to agree centrally, but one word can mean two things on two queues.
4. **As 1, but `post_ref` the post's key string and no push buffer (CF-074 option 3, CF-086 option 3).** Consequences: simpler messages, but `url` and `thread_ids` become loose fields, and three receivers' follow-up work runs before the answer or without retries.

## Decision

One job envelope with one type field, `kind`, drawn from a closed list whose fields F2 declares per kind. `post_ref` is the scheduler's object on every queue, and only the three receivers whose work continues after the answer buffer pushes as `push` jobs.

- Envelope (CF-077 a, b): `job_id` (ADR-0006), `kind`, `source_id` or the queue's declared key (ADR-0004), `due_at`, `attempt` and ADR-0002's metadata; ops and client requests add `request_id` and `requested_by` (ADR-0012); any job may carry the optional `must_finish_by` (ADR-0057). Priority (derived by the SDK, ADR-0018), route and vendor (read from the source row) do not travel in a job. On `raw.items` the job's kind is `job_kind` (ADR-0005). `reason` is never the type; it survives only as a field saying why a job was sent (backfill `add`, `client`, `ops`, ADR-0020; reconciliation `lease_lapsed`, `yt-uploads-reconciler §5.1 L51`).
- Kinds (CF-077 c to e), fields per kind in F2, producers in ADR-0012: `rotation` (optional `tier`); `reconciliation` (X gap fields, ADR-0064; or `post_ref` for a whole-thread read); `backfill` (ADR-0020); `keyword_history` (ADR-0064, ADR-0059); `comments`, `replies` (`post_ref`, `series_step`, `profile`; `thread_ids`, ADR-0060; a `replies` job on `jobs.x-full-archive-search` also carries `window_start`, ADR-0059, ADR-0064); `metrics` (ADR-0034); `first_sight` (ADR-0065); `refresh` (resolvers' own sources, ADR-0032; news-robots-checker's hosts; yt-text-purger, ADR-0065); `resolve` (ADR-0032); `manual_candidate`; `first_check`, `recheck` (ADR-0022); `ops_force` (optional `post_ref` or `target_ids` for a targeted read); `push`; `replay`, `rerun`, `rematch`, `recompute`; `retention_sweep`; `analyze` (ADR-0023); `candidate_retry`. Dropped: `refresh_24h`, `refresh_7d`, `refresh_client` (ADR-0034), `gap_backfill` (ADR-0064), `site_search` (ADR-0037), `resolved`, `unresolvable` (ADR-0032), `health` (ADR-0012), `lang_rescore` (a model change triggers `replay`, `normalize-item §5.1 L45`). A client or ops refresh of one post is a `comments` or `metrics` job with `series_step = refresh:<request_id>` (`comment-decay-scheduler §5.1 L70`).
- RN-11: `first_run` goes; a new rule's first `rotation` is due at once and runs with an empty cursor (ADR-0012).
- `post_ref` (CF-074, AU-036): the scheduler's object `{item_id, platform, platform_id, url}` on every queue; `platform_id` is the id in the post's key (ADR-0007); the optional `url` is the post's `url` on `items.normalized`, needed by ig-comments-fetcher's vendor call (`§5.3 L68`) and fb-group-comments-fetcher (`§5.1 L40`). Replies jobs add `thread_ids`, the parent comments' platform ids. Anything else a fetcher looks up by `item_id` or keeps itself: Disqus data in `news_sites` (ADR-0040), its newest comment time in `cursors` (ADR-0046), a LinkedIn share URN on the item (ADR-0007). The envelope copies of `post_ref` give way to `parent_id` and `root_id` (CF-074 e, ADR-0009).
- `push` (CF-086): only for the three receivers whose work continues after the answer and needs retries (a missing-content fetch, `fb-client-webhook-receiver §5.2 L57`; targeted reads, `ig-webhook-receiver §5.2 L57`; a `first_sight` job, `yt-pubsub-receiver §5.2 L55`). One message per pushed entry, keyed by the `source_id` the receiver finds in its in-memory registry copy before answering, with `body` as received, `received_at`, the headers its worker reads, a `job_id` made at receipt, `attempt` and `due_at = received_at`; the wrapper's retries and DLQ apply. The Telegram and LinkedIn receivers keep writing `raw.items` before answering.

Why: One closed list is what F2 and the SDK wrapper can validate; the scheduler's object is the only `post_ref` anyone emits; the push buffer stays only where work follows the answer.

## Consequences

One job type the SDK validates; four approved PRDs rename `reason`, and tg-message-search and tg-channel-resolver add `kind`, under ADR-0001; every comment and metrics consumer parses the object; ig-webhook-receiver answers Meta after an in-memory lookup.

- CONVENTIONS v1.1: the job section carries the envelope, the closed kind list with its fields, `post_ref` and `push`; push buffers are keyed by `source_id`.
- PRD edit made by D2, citing this ADR: x-recent-search §5.2 L53 loses `first_run` and `gap_backfill` (ADR-0064 gives the gap job its kind).
- F2 declares each kind's fields and the producer table of ADR-0012; F4 and F6 validate every job against them.
- RN-11 is closed by this record.

Sessions that must read this: F2, F4, F5, F6, then C11, FB4, FB5, FB7, VFB3, IG4, IG6, VIG2, LI2, VLI4, VTT5, VTT6, TG2, YT2, YT3, YT4, YT5, YT6, YT7, X1, X5, X6, N8, and every service that consumes or produces a job.
