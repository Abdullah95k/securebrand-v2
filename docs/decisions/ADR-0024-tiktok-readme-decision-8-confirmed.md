# ADR-0024 · TikTok: README decision 8 confirmed part by part

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: tiktok, tt-client-videos-fetcher, tt-video-comments-fetcher, tt-video-stats-refresher, tt-profile-videos-poller, comment-decay-scheduler, F2, F3
Source: D2-Q024 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

README decision 8: "commenter identity is hashed inside the adapter before the first write (so `raw.items` is not byte-for-byte the vendor payload); tt-client-videos-fetcher writes its own +24 h and +7 d metrics and proposes a retention class `tiktok_display`; client-authorised accounts are `tier = push`" (`README L185`). D1 found a conflict in each part (CONFLICTS.md section 4, row 8): ten other services hash at the edge too (CF-109); the metrics come from outside comment-decay-scheduler and against the README's own list of count refreshers (CF-080 e, CF-082 b; `README L25`); `tiktok_display` is not in the class list (CF-104 b); and `push` sits on an account read hourly (`tt-client-videos-fetcher §5.1 L43`) and reconciled daily by the amber poller (CF-096 b). Each conflict is settled by another decision; this one confirms the README text as those decisions shape it.

Settles: RD-8.
Depends on: ADR-0010, ADR-0012, ADR-0034, ADR-0049, ADR-0052, ADR-0054.

## Options

1. **Confirm each part, as settled elsewhere** (chosen): its rules are under Decision.
2. **Accept the README text literally.** Consequences: TikTok-only hashing, a `push` tier value that ADR-0049 removes, and a daily amber reconciliation of a green account; it contradicts ADR-0010, ADR-0049 and ADR-0052.
3. **Green TikTok metrics through comment-decay-scheduler like every other route (CF-080 option 2), as `metrics` jobs on tt-client-videos-fetcher's queue.** Consequences: no exception to the single emitter of metrics jobs, but a job for counts the hourly read already returns, and the scheduler must route TikTok metrics by `route`.

## Decision

Each part of README decision 8 is confirmed as the decisions it depends on shape it: edge hashing is the rule on every route (ADR-0010), tt-client-videos-fetcher writes its own +24 h and +7 d observations (ADR-0012, ADR-0034), `tiktok_display` is ADR-0054's class, and a client's authorised account is polled hourly with `push_covered = false` (ADR-0049).

- Edge hashing: confirmed and generalised to every route (ADR-0010), so TikTok comments (`tt-video-comments-fetcher §5.3 L68`) are no longer an exception.
- Metrics: tt-client-videos-fetcher is a named producer of its own +24 h and +7 d observations, taken from the first hourly read at or after each mark (`tt-client-videos-fetcher §5.1 L51`; ADR-0012), anchored and published as ADR-0034 decides; comment-decay-scheduler opens no metrics lane for green TikTok videos, so they never reach the amber tt-video-stats-refresher (`tt-client-videos-fetcher §14 Q5 L180`).
- `tiktok_display`: added by ADR-0054, kept while the client's authorisation lasts and deleted when it is revoked.
- "`tier = push`": the Display API is polled, not pushed (`tt-client-videos-fetcher §5.1 L43`), so the account keeps `push_covered = false` and its reach tier, and takes its cadence from the `owned_by_client` row of the cadence table (hourly, ADR-0049); a green client account is never reconciled through tt-profile-videos-poller (ADR-0052), though, when its grant is lost, it falls back to it as ADR-0021 allows.

Why: Each part of the README survives with the precision its conflict needed, and TT1 has nothing left to guess.

## Consequences

Nothing beyond the referenced decisions; tt-client-videos-fetcher's PRD cites them.

- This ADR adds no rule of its own. `D2-PROPOSALS.md` proposed none for it, since every part is settled by another decision; it exists because the orchestrator asked for one ADR per decision, so that README decision 8 has one record.
- README decision 8 is reworded to point to ADR-0010, ADR-0012, ADR-0034, ADR-0049, ADR-0052 and ADR-0054 (with ADR-0070's README edits).

Sessions that must read this: F2, F3, then C11, TT1, VTT4, VTT5, VTT6.
