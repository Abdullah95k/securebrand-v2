# ADR-0041 · The cursors table

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all (every service that keeps a cursor), F3, listening-sdk (F4, F5, F6), backfill-orchestrator
Source: D2-Q041 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS keeps one row per source × service, with an opaque `cursor` and three health columns (`CONVENTIONS L30`, `L38`). The PRDs need more:

- Rows with no source, for replays, reruns, recomputes and sweeps (`normalize-item §6.3 L124`, `aggregator §6.3 L97`, `retention-purger §6.3 L114` per class, and eight more in CF-034 b).
- A second dimension: hashtag edge (`ig-hashtag-search §6.3 L127`, against its `§6.1 L87`), X rule (`x-filtered-stream §6.3 L149`), keyword with no source (`fb-page-search §5.1 L42`), a suffixed service name (`li-client-posts-poller §5.1 L48`).
- Typed state: due times (`ig-account-resolver §5.1 L46`; `fb-page-search §5.1 L42`, stored differently at `§5.2 L55`), subscription state (`ig-webhook-receiver §6.3 L129`), job progress (`x-full-archive-search §6.3 L132`), a hashed id set (`yt-web-search-bridge §6.3 L130`), another source's registry data (`tg-discussion-receiver §6.3 L142`).
- Other services' rows: fb-backfill writes fb-page-feed-poller's cursor (`fb-backfill §5.2 L56`, `fb-page-feed-poller §5.1 L48`), x-full-archive-search raises x-user-timeline-poller's (`x-full-archive-search §5.2 L56`), and x-user-timeline-poller reads x-filtered-stream's rows as its coverage list (`x-user-timeline-poller §5.1 L42`, asked at `§14 Q1 L191`).

At stake: F3 needs one key and one column list; today a cursor format change silently breaks the backfill that writes into the poller's row.

Settles: CF-034, CF-035, CF-036, tg-discussion-receiver §14 Q3, x-user-timeline-poller §14 Q1.
Depends on: ADR-0015 (per-service due times), ADR-0020 (the backfill hand-over), ADR-0045 (`service_runs`), ADR-0049 (push coverage).

## Options

1. **A widened key, typed due columns, a private `state`, own rows only** (chosen): its rules are under Decision.
2. **`cursors` kept source × service, with a separate progress table for service-level and non-source rows, and the two backfill seedings allowed as named cross-writes (CF-034 (2), CF-036 (1)).** Consequences: fewer PRDs change, but one helper serves two tables, due times stay untyped, and a poller's format change still breaks the backfill that writes its row.
3. **Key unchanged; extra dimensions and state encoded in `service` and the `cursor` string (CF-034 (3), CF-035 (3)).** Consequences: no schema change, but schedulers cannot index due times, every service parses strings, and ig-hashtag-search's two edges overwrite one row.

## Decision

`cursors` is keyed by service, source and scope, with typed due columns and a private `state` per row. A service writes only its own rows, through the SDK helper, after the producer acknowledges; another service's rows are never an interface.

- Key: unique on (`service`, `source_id`, `scope_key`), nulls not distinct. `source_id` is null for service-level rows; `scope_key` is empty for the plain per-source row, else a hashtag edge, an X rule id, a retention class, `reconcile`, a post (`post:<item_id>`, ADR-0046) or a run (`replay:<version>`, `recompute:<job_id>`, `rerun:<model_version>`, `rematch:<job_id>`). fb-page-search's per-keyword rows become plain rows of its keyword-rule sources (ADR-0044).
- Columns: `cursor` (the opaque read position); `next_due_at` and `last_started_at`, typed and indexed (ADR-0015's rotation state; they replace `refresh_due_at` and `next_search_at`); `last_success_at`, `last_error`, `consecutive_errors`; `state` (jsonb, private to the owning service: subscription state, job progress, id sets); `updated_at`.
- `service` is the name in the index (`CONVENTIONS L226` to `L236`), never suffixed: `li-client-posts-poller:reconcile` becomes `scope_key = reconcile`.
- A service writes only its own rows, through the SDK helper, after the producer acknowledges (`CONVENTIONS L71`); another service's rows are never an interface.
- The cross-service uses go. Backfill services stop writing the pollers' rows: a poller whose row is empty reads one page, newest first, as `x-full-archive-search §5.1 L41` already describes, and normalize-item drops the overlap (the hand-over is ADR-0020's). x-user-timeline-poller takes coverage from `sources.push_covered` (ADR-0049), set by registry-writer from x-filtered-stream's `push_coverage` decisions (ADR-0013), and the stream's state from x-filtered-stream's typed `service_runs` status (ADR-0045); this answers `x-user-timeline-poller §14 Q1 L191`. tg-discussion-receiver's link to its channel moves to the group's registry row (`platform_meta`, ADR-0065).

Why: Every row the PRDs need fits one key, schedulers get the indexed due time ADR-0015 relies on, and a cursor format change can only break the service that owns the row.

## Consequences

One migration and one helper; schedulers index `next_due_at`; about twenty PRDs reword their state lines, among them the approved fb-backfill, fb-page-feed-poller, fb-page-search and ig-hashtag-search, which move under ADR-0001.

- CONVENTIONS v1.1: `cursors` as service × source × scope among the control-plane tables (v1 L30); its column list, the scope-key forms and the one-owner rule (v1 L38).
- F3 creates the key, nulls not distinct, and indexes `next_due_at`; F4, F5 and F6 build the one cursor helper.

Sessions that must read this: F3, F4, F5, F6, C2, C4, C5, C6, C10, C14, C15, A1, A2, A3, A4, FB2, FB3, FB6, VFB3, IG1, IG2, IG4, IG5, VIG1, LI1, X3, X4, X5, W1, W2, W4, YT7, YT9, TG2.
