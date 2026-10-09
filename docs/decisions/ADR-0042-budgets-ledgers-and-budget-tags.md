# ADR-0042 · Budgets, ledgers and budget tags

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all (every service with a `budget_tag`), F3, listening-sdk (F5), quota-governor, D3 (the admin console)
Source: D2-Q042 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

- Writers (CF-037). The governor keeps the counters (`CONVENTIONS L85`), reserving with one conditional update (`quota-governor §5.2 L58`), yet ten PRDs write usage into `budgets` (Meta's headers, `fb-page-feed-poller §5.2 L60`), and nine keep caps, splits and ceilings there that the row (`quota-governor §6.2 L104`) has no column for (per-job caps, `x-full-archive-search §7 L138`; the LinkedIn split, `li-post-search §7 L113`).
- Sub-counters (AU-065). Rule 5 caps vendor spend per source (`CONVENTIONS L246`) and Instagram counts per service (`ig-keyword-search §6.3 L121`); the governor has per-service sub-counters on `tt_vendor` only (`quota-governor §5.3 L82`) and no page cap in its answer (`tt-hashtag-feed-poller §5.1 L50`).
- Ledgers (CF-038). X reads are recorded as bare ids (`quota-governor §6.2 L100`), `x:post:<id>` (`x-replies-fetcher §5.2 L57`) or `user:<id>` and a keyed hash (`x-user-resolver §5.2 L57`), so one post can be paid twice; the hashtag ledger is a table (`quota-governor §6.3 L107`, `README L186`) or rows in `budgets` (`ig-hashtag-search §5.1 L57`).
- Names (CF-099, AU-068). Tags outside the list (`ig_graph_<client_id>`, `ig-hashtag-search §5.2 L65`; `analysis_model_api`, `README L184`), wildcards (`quota-governor §5.3 L82`, `L83`), two placeholder separators (`CONVENTIONS L279`), external calls that ask for nothing (`web-commoncrawl-scanner §7 L111`, `yt-pubsub-receiver §7 L138` and four more), a YouTube `list` bucket (`yt-web-search-bridge §7 L137`), and `budget_80pct` for the governor's `budget_80` (`tt-keyword-search §10 L131`).

At stake: an unknown tag is denied as `flag_off` (`quota-governor §5.3 L67`), and a second writer on a counter double counts or races the reservation.

Settles: CF-037, CF-038, CF-099, AU-065, AU-068, tt-keyword-search §14 Q3, yt-channel-resolver §14 Q4.
Depends on: ADR-0010 (the keyed reference for X user reads), ADR-0018 (priorities and modes), ADR-0023 (`analysis_model_api`), ADR-0057 (what a job does with each answer).

## Options

1. **quota-governor the only writer of counters, configuration in its own table, ledgers as tables, one tag list** (chosen): its rules are under Decision.
2. **Services write usage to an observations table the governor folds in; configuration as columns or one `config jsonb` on the tag row; one generic ledger or ledger rows in `budgets` (CF-037 (2), CF-038 (2) or (3)).** Consequences: services keep a direct write, the reservation must also merge observations, and one table mixes counters, settings and ledgers.
3. **Tag-level counters only, wildcard families allowed (AU-065 (3), CF-099 (3)).** Consequences: the simplest governor, but rule 5's per-source cap has nothing to count against, a comment surge can starve TikTok discovery, and F3 cannot seed a wildcard.

## Decision

quota-governor is the only writer of budget counters; caps, shares and allowances live in one configuration table, `budget_config`; the X read ledger and the Instagram hashtag ledger are tables; CONVENTIONS keeps one canonical list of budget tags, with an id placeholder always after `:`.

- `budgets`, written only by the governor: one row per (`budget_tag`, `sub_counter`, period), with `quota-governor §6.2 L104`'s columns and `reset_rule`, plus `provider_usage` (jsonb: Meta and LinkedIn usage headers, credits left). Services send usage in the SDK `report` (`§5.1 L37`) instead of writing "into `budgets`".
- Sub-counters `service:<service>` and `source:<source_id>` on every amber tag, and `service:<service>` wherever a share is set (ADR-0037's bridge share), each with its own limit; the request carries the job's `source_id`.
- `budget_config` (new; `budget_tag`, `scope`, `setting`, value): limits and shares (the LinkedIn split, the bridge's share, per-source caps), per-job and per-run caps (the page cap included, read through the SDK), rate ceilings, YouTube backfill and refresh allowances. Written by ops through the admin console (D3 specifies the writer; audited); values tuned in the pilot. Intervals belong to ADR-0049's cadence table (`li-company-posts-poller §5.1 L43`).
- `x_read_ledger` (`utc_day`, `resource_type` `post` or `user`, `resource_id`), written only by the governor: posts as bare ids, users as the SDK's keyed reference (ADR-0010), so no individual's clear id is stored yet every read of one user matches; kept until the day is reconciled (`quota-governor §8 L127`). `ig_hashtag_ledger` (`ig_user_id`, `hashtag_id`, `first_queried_at`); a 31st hashtag waits for the window (`§5.3 L81`; amber handling is ADR-0052).
- Tags: `CONVENTIONS L279` stays canonical, with an id placeholder always after `:` (`ig_graph:<ig_user_id>`, `ig_hashtag:<ig_user_id>`, as three of L279's five id placeholders already have it; Instagram keeps `ig_user_id`), ig-hashtag-search aligned; the listed tags instead of wildcards; `analysis_model_api`, seeded only if a hosted model is chosen; zero-price counting tags, never a gate (`commoncrawl`, `tg_bot_api`, `yt_pubsub_hub`, and sub-counter `compliance` on `x_pay_per_use`, priced only if the pilot shows X meters it); LinkedIn confirmation calls on `linkedin_cm:<client_id>` (`li-org-resolver §5.2 L52`); alerts as the governor names them (`budget_80`).
- YouTube's four buckets name the call, not the reason: `list` folds into `ingest`, resolver calls use `ingest` (answers `yt-channel-resolver §14 Q4 L199`), backfill and the text refresh draw on their call's bucket within a `budget_config` allowance.
- `tt_vendor` stays one tag with one sub-counter and monthly share per amber service (`tt-profile-videos-poller §7 L137`), so a comment surge spends only its own share (answers `tt-keyword-search §14 Q3 L160`; six services, `CONVENTIONS L228`).

Why: The one-update reservation needs one writer per counter, caps get a typed home, and one ledger key makes X charge a resource once a day whoever reads it.

## Consequences

F3 seeds concrete rows; C1 is the only writer; six approved PRDs (ig-hashtag-search, yt-web-search-bridge, li-org-resolver, fb-page-feed-poller, tt-keyword-search, tt-hashtag-feed-poller) move under ADR-0001.

- CONVENTIONS v1.1: `budget_config`, `x_read_ledger` and `ig_hashtag_ledger` among the control-plane tables (v1 L30); usage reported through the SDK, never written by services (v1 L85); the tag list (v1 L279) with the separator rule, the added and zero-price tags, the YouTube bucket rule and the sub-counters.
- F3 seeds the `budgets` rows and `budget_config`; ops change values only through the audited admin console (D3 specifies the writer).
- `DEFERRED.md`: every cap, share and allowance value (owner C1, after the pilot).

Sessions that must read this: F3, F5, C1, C9, A1, A2, A3, A4, FB2, VFB2, IG1, IG2, IG3, IG5, IG6, VIG1, VIG2, VTT1, VTT2, VTT4, VTT5, LI1, VLI1, VLI2, VLI3, VLI4, X1, X2, X3, X4, X5, X6, X7, W1, W5, YT2, YT4, YT7, YT8, YT9, TG1, TG2.
