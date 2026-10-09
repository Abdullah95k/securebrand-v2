# ADR-0043 · Clients and client lists

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all (every service that reads `clients`), F3, registry-writer, poster-resolver, qualifier, x-user-resolver, news-site-resolver, li-client-posts-poller, D3 (the client portal and admin console)
Source: D2-Q043 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

- `clients` has no columns and no writer (`CONVENTIONS L30`), and the PRDs read it under many names (CF-039): government status as `client_type = government` (`keyword-matcher §5.3 L69`, failing closed when missing at `alert-evaluator §8 L118`), a "government flag" (seven PRDs, e.g. `registry-writer §6.1 L88`) or a "government marker" (four, e.g. `li-post-search §6.1 L79`); amber acceptance as its own value (`ig-comments-fetcher §6.1 L89`) or as "not government" (`tg-channel-posts-poller §5.1 L42`); the X entitlement under two names (`keyword-matcher §5.3 L69`, `x-user-timeline-poller §14 Q5 L195`); token references (`fb-page-feed-poller §6.1 L104` and six more); per-service options (`qualifier_config`, `qualifier §3 L25`; a Perplexity opt-out, `web-search-perplexity §6.1 L86`; engine flags, `yt-web-search-bridge §6.3 L131`; a `yt_text_refresh` entitlement, `yt-text-purger §5.3 L81`).
- A client's lists sit in three places (CF-056): on `clients` (`qualifier §6.1 L77`, `poster-resolver §6.1 L83`), in `client_sources.priority` (`registry-writer §5.3 L77`, `li-client-posts-poller §6.1 L101`) and on `keywords` (`web-search-mojeek §5.1 L45`). They do different jobs. A priority list makes a source tier 1 (`CONVENTIONS L45`) and exempts it from decay (`qualifier §12 L134`). Seed lists and watchlists act on candidates that are not yet sources: as an Iraqi signal (`CONVENTIONS L243`), as a reason an X account qualifies (`CONVENTIONS L242`, `x-user-resolver §5.2 L57`), and as a way through a remembered rejection (`poster-resolver §5.2 L54`).

At stake: every amber, X and government rule reads `clients`; one concept under four names means one filter per service, and a list edited in one place changes nothing for the services that read another.

Settles: CF-039, CF-056, li-client-posts-poller §14 Q4, registry-writer §14 Q3, x-user-resolver §14 Q1.
Depends on: ADR-0016 (`credentials`), ADR-0050 (the X gate), ADR-0052 (amber acceptance), ADR-0066 (the manual path for client-added candidates).

## Options

1. **A typed `clients` core with settings and tokens beside it, priority on `client_sources`, seed and watch lists by candidate key** (chosen): its rules are under Decision.
2. **A small core plus one `settings jsonb` on `clients`, every list an array on `clients` (CF-039 (2), CF-056 (2)).** Consequences: one table, but each list lookup scans arrays across all clients, token state stays outside `credentials`, and registry-writer's manual add loses its `priority` field.
3. **Lists entered on `clients` and copied by registry-writer into `client_sources.priority` and `sources.tier` (CF-056 (3)).** Consequences: the client edits one place, but two copies must be kept in step, and a seed or watch entry for an account that is not yet a source has no row to copy into.

## Decision

`clients` gets a typed core with one government marker and the amber, X and flagged-vendor settings. Tokens live in `credentials` and per-service options in `client_settings`; a client's priority list is `client_sources.priority`, and its seed lists, watchlists and saved lists of public accounts are rows of `client_lists`.

- `clients`: `client_id` (uuid, ADR-0006), `name`, `status` (`active`, `offboarding` and the rest of D3's list), `client_type` (`commercial` or `government`, the one government marker; a missing value fails closed), `accepts_amber` (ADR-0052, never derived from `client_type`; also what the "contract terms" of `tt-profile-videos-poller §6.1 L101` stand for), `x_end_user_declared` (ADR-0050), `accepted_flagged_vendors` (the flagged vendors the client accepts, `CONVENTIONS L6`: Perplexity today, replacing the opt-out and the engine flags), `created_at`, `updated_at`. No `yt_text_refresh` entitlement, since ADR-0056 makes the refresh part of the service.
- Tokens, calling accounts and webhook secrets live in `credentials` (ADR-0016). `client_settings` (`client_id`, `service`, `settings` jsonb) holds per-service options; `qualifier_config` becomes the qualifier's row (an approved PRD moves under ADR-0001). Portal users and roles are D3's.
- Priority: `client_sources.priority`, written by registry-writer from the portal's `add` or `update` decision. A source any client priority-lists is tier 1 whatever its followers and is exempt from decay while listed (`CONVENTIONS L45`, `qualifier §12 L134`); li-client-posts-poller's 30-minute list is this flag (answers `li-client-posts-poller §14 Q4 L190`); its cadence comes from an `owned_by_client` row of ADR-0049's cadence table, as these pages are not `push_covered`. Keyword priority is `keywords.priority` (ADR-0044).
- Seed lists and watchlists: `client_lists` (`client_id`, `list` `seed`, `watch` or `saved`, `candidate_key` in ADR-0032's forms or, for a saved registered source, `source_id`, `added_at`, `added_by`), indexed by `candidate_key` and `source_id` and read by poster-resolver, the qualifier, x-user-resolver and news-site-resolver; a new seed or watch entry also goes down the manual path (ADR-0066).
- The client portal and admin console write `clients`, `client_settings` and `client_lists` (D3 specifies the writer); services only read them.
- Saved lists (ADR-0010): a `saved` entry is a public account a client has saved, keyed by the account's candidate key or `source_id`; the client lists, filters, ranks and saves public accounts and uses a saved list as a segment, as D3 specifies.

Why: Each concept gets one name and one home that fits what it acts on: a policy on the client, a priority on the source, a seed or watch entry on the candidate.

## Consequences

F3 creates three tables; about thirty PRDs replace the four names and "token reference" with these columns; the approved qualifier and poster-resolver read their lists from `client_lists`.

- CONVENTIONS v1.1: `clients` with its columns, `client_settings` and `client_lists` among the control-plane tables (v1 L30); where the priority, watch and seed lists live (v1 L45, L242, L243).
- F3 creates the three tables, with the three list types; the client portal and admin console write them (D3 specifies the writers).

Sessions that must read this: F3, C1, C5, C7, C8, C9, C12, C13, C14, A5, FB1, FB2, FB5, FB6, VFB1, VFB2, VFB3, IG1, IG3, IG4, IG5, VIG1, VIG2, TT1, VTT1, VTT4, VTG3, LI1, VLI1, X2, X3, X4, X5, N2, W1, W2, YT7, YT9, D3, U2.
