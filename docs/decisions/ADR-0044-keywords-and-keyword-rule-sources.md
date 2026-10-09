# ADR-0044 · Keywords and keyword-rule sources

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, registry-writer, keyword-matcher, x-filtered-stream, D3 (the client portal and admin console), and the lane Discover and qualify (every search service)
Source: D2-Q044 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

- Columns (CF-040). CONVENTIONS names `keywords` without columns (`CONVENTIONS L30`) and expects keyword-rule rows in `sources` (`L36`, `L281`). keyword-matcher proposes the only column list, one client per row (`keyword-matcher §5.3 L56`); the searchers read "variants", "terms", per-script forms, context terms, a priority flag and a `client_ids` list (`fb-page-search §6.1 L89`, `yt-keyword-search §6.1 L92`, `web-search-perplexity §5.1 L44`). No PRD writes `keywords` (`qualifier §3 L32`).
- Creation (AU-062). The web engines expect registry-writer to create a row per keyword (`web-search-perplexity §5.1 L41`, `web-search-mojeek §5.1 L42`), but its decision types and columns never mention keyword rules (`registry-writer §3 L22`, `§3 L27`) and it reads no `keywords` (`§6.1 L88`); fb-page-search keys its jobs by `keyword_id` and expects registry-writer to emit a `seed` job (`fb-page-search §5.1 L40`).
- Sharing. Searchers select rows by platform and type, so several services read one row: the three web engines (`web-gdelt-poller §5.1 L41`), yt-keyword-search for tier 1 and yt-web-search-bridge for tiers 2 and 3 (`yt-keyword-search §3 L23`, `yt-web-search-bridge §3 L21`), x-recent-search and x-full-archive-search (`x-recent-search §5.1 L39`, `x-full-archive-search §5.1 L39`). Identical queries of several clients are one row (`ig-keyword-search §5.1 L41`); fb-keyword-search reads only `route = amber` rows (`fb-keyword-search §5.1 L40`).

At stake: the twelve search services have nothing to rotate, and keyword-matcher and the searchers read different columns for one keyword.

Settles: CF-040, AU-062, fb-keyword-search §14 Q3, web-search-perplexity §14 Q4.
Depends on: ADR-0004 (jobs keyed by the keyword-rule source), ADR-0013 (registry decisions), ADR-0015 (several services rotating one row), ADR-0049 (tier and lifecycle), ADR-0052 (amber acceptance), ADR-0069 (the X term screen).

## Options

1. **Per-client keywords; shared keyword-rule rows per platform, route and query, kept by registry-writer from the portal's saves** (chosen): its rules are under Decision.
2. **One keyword-rule row per keyword and search service.** Consequences: each row has one reader, but rows shared today stop being shared, registry-writer's identity needs the service inside `platform_id`, and the approved web engines, YouTube searchers and x-recent-search change their selection.
3. **The searchers rotate `keywords` rows directly, keyed by `keyword_id` (CF-040 (3)).** Consequences: no keyword-rule rows, against `CONVENTIONS L36` and `L281`; identical queries of two clients are searched and paid twice; search finds have no registered `source_id`.

## Decision

Keywords are per client, in one `keywords` column list the client portal writes. The searchers rotate shared keyword-rule rows in `sources`, one per platform, route and query, which registry-writer keeps from the portal's saves, so a query several clients share is searched and paid once.

- `keywords`, written by the client portal (D3 specifies the writer): keyword-matcher's list (`keyword_id`, `client_id`, `label`, `forms`, `exclusions`, `purpose`, `enabled`, `version`, `updated_at`, `rematch_days`) plus `context_terms` (they narrow a search and are never matched alone), `priority`, `platforms` (in scope), `query_key` (an SDK hash of the normalised forms and context terms, set on save) and `screening_status` (the X sensitive-event screening result, set on save, ADR-0069). "Variants", "terms" and per-script forms are `forms` entries.
- `screened_terms` (new, ADR-0069): the X blocked and sensitive-event terms that a save is screened against and that x-filtered-stream and x-recent-search read; owned by the admin console (D3 specifies the writer).
- Keyword-rule rows: one `sources` row per (`platform`, `route`, `query_key`), with `platform_id = <route>:<query_key>` so registry-writer's identity holds (`registry-writer §2 L15`), `client_ids` = every client with an enabled keyword of that query (one paid search for all), and `tier` 1 if any of them has `priority`, else 2 (ADR-0049). Every searcher of that platform and route reads the row and keeps its own cursor and due time (ADR-0015, ADR-0041). Facebook gets a green row (fb-page-search) and an amber row (fb-keyword-search); amber rows carry only clients that accept amber, never government clients (ADR-0052, `registry-writer §5.2 L61`). Hashtag forms make `hashtag` rows the same way. A keyword whose `screening_status` flags it joins no X row (ADR-0069).
- Searchers take the forms from the row's keywords and `client_ids` from the row; exclusions stay per client, applied by keyword-matcher, never in a shared query.
- Each save sends registry-writer an `add` or `update` decision naming the keyword (ADR-0013); registry-writer reads `keywords`, upserts the rows for each platform in scope, adds or removes the client, retires a row with no keyword left (ADR-0049) and emits `source.events`.
- fb-page-search's own scheduler makes a green Facebook rule row due at once on its `added` or `updated` event, the old `seed`, and runs it as a `rotation` (ADR-0011, ADR-0012); its jobs carry the row's `source_id` (ADR-0004), not `keyword_id`.

Why: It is what most searchers already assume, it pays once for a query several clients share, and it keeps the government and amber rules on the rows the amber services select.

## Consequences

F3 creates `keywords` and `screened_terms`; F2 adds the `query_key` helper with golden vectors; the approved registry-writer (a decision path and a read of `keywords`) and fb-page-search (jobs keyed by source) move under ADR-0001.

- CONVENTIONS v1.1: the `keywords` columns and `screened_terms` among the control-plane tables (v1 L30); the keyword-rule identity and its `client_ids` (v1 L36); searchers read the rule row (v1 L281).
- F2 ships the `query_key` helper with golden vectors; F3 creates `keywords` and `screened_terms`.

Sessions that must read this: F2, F3, C5, C6, C7, C9, FB6, VFB1, IG2, VIG1, VTT1, VLI1, VTG1, X1, X4, X5, YT8, YT9, W1, W2, W4.
