# ADR-0064 · X gaps, history and replies

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, listening-sdk (F4), backfill-orchestrator, comment-decay-scheduler, normalize-item, x-filtered-stream, x-recent-search, x-user-timeline-poller, x-full-archive-search, x-replies-fetcher
Source: D2-Q064 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

After a stream drop, x-filtered-stream emits one `reconciliation` job per affected rule on `jobs.x-recent-search` with `query`, `source_ids`, `client_ids`, `window_start` and `window_end`, sends parts older than recent search's 7 days to x-full-archive-search, and closes the gap when `jobs.completed` arrives for all its jobs (`x-filtered-stream §5.2 L70`, `L71`, `§14 Q3 L207`). The approved x-recent-search claims "gap backfill for x-filtered-stream" (`x-recent-search §3 L22`) but reads only `reason` = rotation | first_run | gap_backfill | ops_force, builds queries from `keywords` and writes no completion (`x-recent-search §5.2 L53`, `§6.2 L98`); account rules are `from:` buckets of several accounts (`x-filtered-stream §5.1 L40`); x-full-archive-search has no gap kind (`§5.1 L39`). `keyword_history` comes from x-recent-search on a cursor older than 7 days (`§5.1 L45`, `§13 L188`) and from backfill-orchestrator on a client request (`x-recent-search §5.1 L49`), whose route table has no such kind (`backfill-orchestrator §5.3 L72`). A reply is `x:comment:<id>` in x-replies-fetcher (`§6.2 L115`) and `x:post:<id>` in the other readers (`normalize-item §5.3 L68`); x-full-archive-search's `replies` jobs have no producer and no agreed hand-back (`§6.2 L128`, `§14 Q2 L190`). At stake: every gap job is rejected and no gap closes, and one reply becomes two items.

Settles: CF-084, AU-093, AU-096, x-filtered-stream §14 Q3, x-full-archive-search §14 Q2.
Depends on: ADR-0004 (the gap job's key), ADR-0007 (X keys), ADR-0010 (identities), ADR-0011 (kinds), ADR-0017 (`jobs.completed`), ADR-0020 (backfill job fields), ADR-0059 (X history and older replies).

## Options

1. **x-recent-search fills recent gaps, history only on a client's request, one key per tweet** (chosen, with the automatic history and the replies to day 30 of ADR-0059): its rules are under Decision.
2. **x-filtered-stream re-reads its own gaps** through the SDK's recent-search client (CF-084 option 3, AU-093 option 2). Consequences: no cross-service job, but a second searcher and a second writer of the same posts.
3. **Gaps go to the services that own the cursors** (AU-093 option 3): account buckets become `reconciliation` polls on x-user-timeline-poller, keyword gaps wait for x-recent-search's next run. Consequences: no new query path; slower filling, and reading back to each cursor can pay again for posts the stream delivered on an earlier UTC day.
4. **`x:comment:<id>` for every reply**, through one SDK X mapper (AU-096 option 1). Consequences: x-replies-fetcher keeps its key, but the approved normalize-item mapper and the other readers change, and each reader must classify a tweet before keying it.

## Decision

x-recent-search fills the recent part of an X stream gap from a `reconciliation` job with an explicit window; `keyword_history` stays its own kind, emitted only by backfill-orchestrator; every X post, reply or not, has one key, `x:post:<id>`. The proposal assumed no automatic history and no replies after day 7; ADR-0059 adds both, and this ADR records them.

- Gap job: `kind = reconciliation` (no `reason`, ADR-0011) with the kind fields `query`, `window_start`, `window_end`, `source_ids` and `client_ids`, partitioned as ADR-0004 decides. x-recent-search reads exactly that window with the API's start and end times, never moves the rule's `since_id`, files each post under its author's source when the author is in `source_ids` (a `from:` bucket) and under the keyword rule otherwise (the registry lookup of `§5.2 L57`), and is reported by the job wrapper (ADR-0017), so the gap closes. `reason` goes with its values `first_run` and `gap_backfill` (ADR-0011).
- Gap parts older than 7 days are reported with `gap_unfilled` and their window, not filled, in v1; x-full-archive-search gets no gap kind.
- `keyword_history` stays a kind of its own, since a client's history read runs at priority 1 and `backfill` is always 5 (ADR-0018). Only backfill-orchestrator emits it, on a client request through the admin API (ADR-0012), with `run_id`, `window_start`, `window_end`, `cap` and `reason = client` (ADR-0020), which answers `x-full-archive-search §14 Q1`, and, as ADR-0059 adds, automatically for every new X keyword rule, 90 days with `reason = add` at priority 5. x-recent-search stops emitting it: a cursor older than 7 days resumes at the window's edge and reports the uncovered span (status `partial`). New keyword rules get their automatic 90 days from backfill-orchestrator, never from x-recent-search (ADR-0059).
- Every X post, reply or not, is `x:post:<id>` with its parent link (ADR-0007); x-replies-fetcher adopts it (its `ledger_key` becomes the same value), and identities are replaced at the edge on every X reader (ADR-0010), which answers `x-replies-fetcher §14 Q5 L203`.
- x-full-archive-search keeps its `replies` kind, since ADR-0059 follows X replies to day 30: comment-decay-scheduler emits the steps after +3 d on its queue, each carrying `window_start`, the start of the previous step's read, so no hand-back through the report is needed (ADR-0011, ADR-0017), which answers `x-full-archive-search §14 Q2`; x-replies-fetcher's reply index becomes `comment_state` (ADR-0046). This hand-back is phase 2's technical choice, not the proposal's: the proposal left it for X5 to design once older replies were bought (`D2-PROPOSALS.md` L1977, L1987; Appendix C L2407). ADR-0059 bought them, F2 types the job's fields now, and the reply index the proposal pointed to is gone (ADR-0046). The user accepted the choice on 9 Oct 2026 (`D2-SUMMARY.md`, Answers); X5 confirms it in its build (`DEFERRED.md` section 3).

Why: It uses the job x-filtered-stream already emits and the role the approved x-recent-search already claims, pays only for the gap itself, gives `keyword_history` one emitter, and keeps one tweet one item however it was found.

## Consequences

The approved x-recent-search gains a window path and loses `reason` and its stale-cursor trigger (it moves under ADR-0001); X1, X4 and X5 share one job type; a stream outage longer than 7 days needs an ops decision.

- CONVENTIONS v1.1: `keyword_history`, automatic and requested, and the `reconciliation` window fields (v1 L277).
- `DEFERRED.md`: filling stream-gap parts older than 7 days, reported `gap_unfilled` in v1 (owner X5); confirming the replies hand-back by `window_start`, phase 2's choice (owner X5).

Sessions that must read this: F2, then F4, C4, C10, C11, X1, X3, X4, X5, X6.
