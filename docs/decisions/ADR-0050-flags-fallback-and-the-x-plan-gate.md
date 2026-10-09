# ADR-0050 · Flags, fallback and the X plan gate

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F3, listening-sdk (F4, F5, F6), keyword-matcher, quota-governor, poster-resolver, qualifier, ig-hashtag-search, backfill-orchestrator, comment-decay-scheduler, source-health-canary, registry-writer, x (every X service), and every amber service: fb-keyword-search, fb-group-posts-poller, fb-group-comments-fetcher, ig-keyword-search, ig-comments-fetcher, tt-keyword-search, tt-hashtag-feed-poller, tt-user-resolver, tt-profile-videos-poller, tt-video-comments-fetcher, tt-video-stats-refresher, li-post-search, li-org-resolver, li-company-posts-poller, li-post-comments-fetcher, tg-message-search, tg-channel-resolver, tg-channel-posts-poller
Source: D2-Q050 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

- Storage (CF-102 a, b). CONVENTIONS configures by environment variables (`CONVENTIONS L12`) yet reads the flag "at the start of every job" (`L102`), with no default (`L238`; `CLAUDE.md` L9: off). Five shared services read other services' flags (e.g. `quota-governor §6.1 L94`, `poster-resolver §5.2 L56`), so a flip redeploys them all.
- Flag off and fallback (CF-102 c, d). tt-profile-videos-poller's scheduler "emits nothing" while the flag is off (`tt-profile-videos-poller §5.1 L41`); its own test and two approved siblings count a day of jobs as `flag_off` (`tt-profile-videos-poller §13 L177`, `tt-keyword-search §13 L145`, `tt-hashtag-feed-poller §13 L154`). `fallback_on` is a flag the canary sets (`CONVENTIONS L102`), `fallback` a `health` value (`L36`); ig-hashtag-search sends `fallback_on` for a budget wait (`ig-hashtag-search §5.1 L57`).
- X gate (AU-095). A government end user and a multi-client product both need Enterprise, and a government end user must be named at use-case review (`CONVENTIONS L87`, `L113`, `L188`). The X services test a `clients` entitlement (`x-user-timeline-poller §5.2 L55` and two more), an app-wide `X_PLAN` (`x-user-resolver §5.2 L54` and one more) or `clients.x_enterprise` (`keyword-matcher §5.3 L69`); x-recent-search relies on a registry refusal registry-writer lacks (`x-recent-search §12 L175`). Open: the column (`x-user-timeline-poller §14 Q5 L195`) and a governor deny for government-only sources (`quota-governor §14 Q3 L172`, proposed yes).

At stake: amber code off in one service and on in another during a rollout, and X data reaching a client X's plan does not cover.

Settles: CF-102, AU-095, quota-governor §14 Q3, x-user-timeline-poller §14 Q5.
Depends on: ADR-0010 (the follower threshold, a row of `feature_flags`), ADR-0016 and ADR-0021 (health and the automatic fallback), ADR-0017 (`skipped_flag_off`), ADR-0042 (`source_id` on the governor's request), ADR-0051 (vendor values), ADR-0053 (X before Enterprise).

## Options

1. **Flags in a table read per job, nothing emitted while off, fallback a health state, a plan setting plus a per-client declaration** (chosen): its rules are under Decision.
2. **Environment variables as written, every reading service listed, a restart on change; the X gate as a per-client column only (CF-102 (2), AU-095 (1)).** Consequences: no table, but every flip is a coordinated redeploy of at least six services, and a column alone cannot record the company's plan.
3. **Flags in the environment, the canary's fallback state in the control plane; a registry refusal of gate-closed X rules, fetch-time checks second (CF-102 (3), AU-095 (3)).** Consequences: fallback changes at run time but flags need redeploys, and a registry refusal cannot handle a rule shared by open and gate-closed clients (ADR-0044), so the fetch-time drop stays.

## Decision

Every amber flag, vendor override and plan setting, and the follower threshold of ADR-0010, is a row of one table, `feature_flags`, read by the SDK at the start of every job; nothing is emitted while a flag is off; `fallback` is a health state, never a flag; an X reader serves a client only when the plan setting and the client's declaration to X open the gate.

- `feature_flags` (`name`, `value`, `changed_by`, `changed_at`, `reason`): one row per amber flag of `CONVENTIONS L238` and `L280`, one per override ADR-0051 allows (fb-keyword-search's vendor), one for `X_PLAN`, and one for the follower threshold of public accounts (ADR-0010). F3 seeds every flag `off`, `X_PLAN = pay_per_use` and the threshold unset, so the follower test admits no account until the user sets it; the audited admin API makes every change (D3 specifies the writer).
- The SDK reads the row at the start of every job, never cached; the environment variable counts only where the table has no row (local and test runs), and a missing one means `off`. Shared readers read the same rows, so nothing is redeployed.
- While a flag is `off`, schedulers emit nothing; a queued job ends `skipped_flag_off` at its start (ADR-0017), not an attempt; the governor's `flag_off` deny is the second line (`quota-governor §5.3 L67`). The three tests are rewritten (two approved PRDs move under ADR-0001); backfill-orchestrator keeps an amber source `pending` until its flag is on, not `done` with a note.
- `fallback` is only a `sources.health` value, set by registry-writer from the canary's route-level `health_change` or, for one blocked source, by the automatic fallback of ADR-0021 (ADR-0016, ADR-0021), and announced as `fallback_on` and `fallback_off` events (ADR-0014), never a flag. While health is `fallback` and the flag is not `off`, a reader uses the alternate vendor in the vendor rows of `credentials` (ADR-0051; `source-health-canary §13 L152` reworded to "not `off`"); when the flag is turned `off`, the fallback ends (ADR-0021); a budget wait never triggers it (ADR-0052).
- X gate, as ADR-0053 sets it: `X_PLAN` (`pay_per_use` or `enterprise`) and `clients.x_end_user_declared` (true once X has named the client at use-case review; answers `x-user-timeline-poller §14 Q5 L195`). A government client gets X data only when `X_PLAN = enterprise` and it is declared (`CONVENTIONS L113`); before Enterprise, any client needs the declaration; after it, X data joins the shared pool for other clients. Every X content reader drops gate-closed clients from `client_ids`, skipping a job left with none (five already do); x-recent-search (approved; moves under ADR-0001) does so instead of the registry refusal; keyword-matcher gates X items on the same settings; x-compliance-sync is never gated. Second line: quota-governor denies an X request whose source has only gate-closed clients (answers `quota-governor §14 Q3 L172`: yes) and keeps `x_enterprise_required` (`quota-governor §5.3 L85`).

Why: Only a flag read per job from one table makes "at the start of every job" hold across shared services; one plan setting and one declaration per client give every X reader one test.

## Consequences

F3 creates `feature_flags` and the column; F4 gives every service one flag reader; the approved li-org-resolver and li-post-search stop reading `LI_VENDOR_ROUTE` from the environment (`li-org-resolver §6.1 L75`, `li-post-search §6.1 L79`).

- CONVENTIONS v1.1: flags and `X_PLAN` in `feature_flags`, the environment a local default only (v1 L12); fallback a health state (v1 L102); the X gate for every client before Enterprise (v1 L87, L113); default `off`, nothing emitted while off (v1 L238).
- F3 creates `feature_flags`, seeded as above, and `clients.x_end_user_declared`; F4 gives every service one flag reader; changes go through the audited admin API (D3 specifies the writer).
- `DEFERRED.md`: the follower threshold, a row of this table that the user sets before the first client-facing lane that shows author lists (ADR-0010).

Sessions that must read this: F3, F4, F5, F6, C1, C5, C7, C8, C9, C10, C11, C12, IG2, VTT1, VTT2, VTT4, X1 to X7, and every amber service.
