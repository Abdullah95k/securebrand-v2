# ADR-0025 · New tables and service-private stores

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q025 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

README decision 9 lists new control-plane tables proposed by single PRDs: `comment_series`, `backfill_runs`, `x_read_ledger`, `ig_hashtag_ledger`, `budget_reservations`, `budget_history`, `canary_targets` columns, `news_urls`, `news_stories`, `news_story_members`, `model_versions`, `taxonomy_nodes`, `kb_entities`, `kb_aliases`, `brand_assets` (`README L186`). CONVENTIONS lists the shared stores (Postgres L30, object storage L31, ClickHouse L32). D1 found the ledgers' keys and `model_versions` disputed (CF-038, CF-058; CONFLICTS.md section 4 row 9) and, counting CF-059's lines, 31 Postgres stores, seven ClickHouse names and twelve object-storage entries that only one PRD names, several holding item ids, hashes or URLs, plus stores several PRDs name that neither list has (CF-059 e). D1's review notes add `tg_thread_map`, "a service-private table" of tg-discussion-receiver (`tg-discussion-receiver §6.1 L110`) missing from INVENTORY §4.1 (RN-08), and lang-dialect-id's "registry `country_signals`" (`lang-dialect-id §3 L28`, `§5.3 L69`), a table name CF-059 does not list (RN-09). At stake: F3 and F8 create only what is agreed; anything else is invented by a build session, with no review of its key, its retention or its place in the purge registry.

Settles: RD-9, CF-059, RN-08, RN-09, alert-evaluator §14 Q1.
Depends on: ADR-0023, ADR-0036, ADR-0039, ADR-0040, ADR-0042, ADR-0045, ADR-0046, ADR-0047.

## Options

1. **Decision 9 accepted, stores another service reads join CONVENTIONS, private stores follow one rule (CF-059 option 2)** (chosen): its rules are under Decision.
2. **Every listed store joins CONVENTIONS with its PRD's columns, private ones marked private (CF-059 option 1).** Consequences: one complete list, but F3 freezes every private schema before its service exists, duplicates included (the resolver caches, the comment indexes).
3. **Each store reviewed one by one in D2 (CF-059 option 3).** Consequences: the most precise, but D2 designs tables that belong to build sessions, and the duplicates are ADR-0045's and ADR-0046's anyway.

## Decision

README decision 9's tables are accepted with their owning PRDs' columns. Every other store that another service or an app reads joins CONVENTIONS with a named owner, and everything else is service-private under one rule for naming, ownership and the purge registry.

- Decision 9's tables, with the owning PRD's columns: `comment_series` (`comment-decay-scheduler §6.3 L147`, key per ADR-0046), `backfill_runs` (`backfill-orchestrator §6.3 L112`, plus ADR-0020's window and reason), the two ledgers, `budget_reservations` and `budget_history` (`quota-governor §6.3 L107`, keys per ADR-0042), the `canary_targets` columns of `source-health-canary §6.3 L108`, `news_urls` (news-article-extractor's, ADR-0036), `news_stories` and `news_story_members` (`news-dedup §6.3 L108`), `model_versions` (ADR-0023), `taxonomy_nodes` (`analysis-topics §5.3 L68`), `kb_entities` and `kb_aliases` (`analysis-entities §5.3 L61`), `brand_assets` (`analysis-media §5.3 L68`).
- Other stores that another service or an app reads join CONVENTIONS with a named owner: `registry_audit` (registry-writer, audit shape per ADR-0045), `x_compliance_audit` (x-compliance-sync), `alerts` (alert-evaluator) and `alert_rules` (read by alert-evaluator); the ClickHouse aggregates and views (ADR-0047); object-storage prefixes with one owner each (ADR-0039), model artefacts under `models/` written by each model's release step. Where a PRD names a writer only as an app, an admin page or curators (`alert_rules`, `brand_assets`, `kb_entities`, `kb_aliases`, x-filtered-stream's blocked-terms list, `x-filtered-stream §14 Q6 L210`), D3 specifies the writer.
- Everything else is service-private: named with its owner's platform prefix or a short form of its name, read by no other service, listed in F3's `TABLE-OWNERS.md`, and registered in the SDK's purge registry (`deletion-propagator §5.3 L68`) when it holds item ids, hashes or URLs. Today: `tg_thread_map`, `yt_subscriptions`, `yt_live_watch`, `tt_client_video_state`, `x_compliance_runs`, `cc_hosts_seen`, `search_url_seen`, `search_candidate_seen`, `search_parked_urls`, `alert_deliveries`, `alert_watch_items`.
- Settled by other decisions: the resolver caches (`profile_cache`, `poster_profiles`, `tt_user_cache`), `retention_audit` and the canary's audit trail (ADR-0045); the reply indexes, `comment_ledger` and `tt_comment_state` (ADR-0046); `news_sites` (ADR-0040); `hits` and the other ClickHouse names (ADR-0047); the Telegram onboarding records (ADR-0066). fb-reactions-fetcher's due-time table is not needed (ADR-0015, ADR-0046); aggregator's minute-grain table is not built in v1, and a later need goes through a proposal.
- RN-08: `tg_thread_map` is tg-discussion-receiver's private table under the rule; INVENTORY stays D1's record (ADR-0070). RN-09: "registry" there means `sources` (`CONVENTIONS L30`), so the PRD reads `sources.country_signals`, a wording fix.

Why: Only stores another service reads need to be contract; a naming rule, an owner list and the purge registry keep private state reviewable and deletable without freezing it early.

## Consequences

F3 and F8 build the shared list and nothing else; each build session creates its private tables under the rule, and its review checks them; the PRDs that name these stores gain an owner line; registry-writer's `registry_audit` (approved) is confirmed.

- CONVENTIONS v1.1: the shared Postgres tables with their owners, the object-storage prefixes and the analytics tables (with ADR-0039 and ADR-0047), and the rule for private stores (naming, `TABLE-OWNERS.md`, the purge registry). The tables later ADRs add, such as `permitted_uses` (ADR-0068) and `public_accounts_dim` (ADR-0010), join the same lists.
- PRD edit made by D2, citing this ADR: `lang-dialect-id §3 L28` and `§5.3 L69` read `sources.country_signals` where they said "registry `country_signals`".
- RN-08 and RN-09 are closed by this record; `INVENTORY.md` stays D1's record (ADR-0070).

Sessions that must read this: F3, F8, then F4, C1, C2, C3, C6, C7, C10, C12, C13, C15, A1, A2, A3, A4, A5, FB4, TT1, VTT3, VTT5, X4, X6, X7, YT2, YT4, YT6, TG1, TG2, N6, N7, N8, W3, W5.
