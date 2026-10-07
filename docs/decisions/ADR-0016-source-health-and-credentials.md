# ADR-0016 · Source health and credentials

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, listening-sdk (F4, F6), source-health-canary, registry-writer, and the lanes Discover and qualify, Fetch posts, Comments and Comments and stats (every fetcher and receiver)
Source: D2-Q016 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

registry-writer owns `health` (`registry-writer §3 L27`) and applies the canary's route-level `health_change` as a bulk update of every source on the route (`§5.2 L54`); the canary works per route (`source-health-canary §2 L15`, `§5.3 L66`). A dozen fetchers set one source's health themselves (CF-032 b): a removed bot (`tg-bot-channel-receiver §5.2 L72`), privacy mode (`tg-discussion-receiver §5.2 L69`), a lost administrator role (`li-client-posts-poller §8 L142`), a suspended account (`x-user-timeline-poller §8 L151`), a rejected query (`x-recent-search §8 L154`). Others ask the canary for per-source flips it cannot make (AU-070: `x-compliance-sync §5.3 L83`, `news-feed-poller §12 L156`, `web-commoncrawl-scanner §8 L122`, `ig-webhook-receiver §8 L144`). The receivers expect the canary to watch push heartbeats (`tg-bot-channel-receiver §8 L152`, `tg-discussion-receiver §8 L156`, `yt-pubsub-receiver §8 L146`), which it leaves out of scope (`source-health-canary §3 L30`; AU-069). Separately, 40 PRDs mark a token or key `degraded` and expect later calls to skip it (`CONVENTIONS L101`; `fb-page-feed-poller §5.2 L55`, `§13 L183`), but only one names a store (`tt-keyword-search §8 L117`, `vendor_keys`), and tt-client-videos-fetcher writes refreshed tokens to Vault itself (`tt-client-videos-fetcher §5.2 L56`; CF-057). At stake: a route-wide return to `ok` clears a source that a fetcher set to `blocked`, with no audit row, and the other services that share a revoked client token keep calling with it.

Settles: CF-032, CF-057, AU-069, AU-070.
Depends on: ADR-0021 (what a 401 or 403 means), ADR-0013 (health changes as decisions).

## Options

1. **Two levels, each with one writer** (chosen): its rules are under Decision.
2. **Direct source-level writes with a guard (CF-032 option 2):.** fetchers write `health` and `health_set_by`; the route-wide update skips rows a fetcher set. Consequences: fewer messages, but no audit row and no event for those writes.
3. **Two columns, route health and source health (CF-032 option 3), with token state in `vendor_keys` and a client-token table (CF-057 option 1).** Consequences: a clean separation, but every reader combines two columns and two token stores.
4. **No token-level mark (CF-057 option 3):.** a revoked token degrades the sources that use it. Consequences: the simplest schema, but every service sharing the token keeps calling until each fails on its own.

## Decision

Health has two levels, each with one writer. `sources.health` is written only by registry-writer, from the canary's route-level decisions and from source-level decisions of the service that saw the problem; credential state lives in one `credentials` table, read and written only through the SDK's credential client.

- Source health (CF-032, AU-070): `sources.health` (`ok`, `degraded`, `fallback`, `blocked`) with `health_reason`, `health_set_by` and `health_changed_at`, written only by registry-writer from `health_change` decisions (ADR-0013). Route level comes from the canary (`platform`, `route`, `vendor`, `health`, the `fallback` object, `scope`, `reason`, `evidence`, as `source-health-canary §6.2 L102`) and is applied, within ADR-0021's exclusions (no government-watched green source and no client-owned property ever moves to a vendor), to sources whose state is `ok` or was set at route level. Source level comes from the service that saw it: `source_id`, `health` and a `reason` from a closed list (`bot_removed`, `privacy_mode`, `grant_missing`, `account_unavailable`, `credential_revoked`, `not_found`, `uploads_playlist_missing`, `query_rejected`, `feed_gone`, `push_gap`, `crawl_disallowed`). A source-level state is cleared only by a source-level decision (the service that set it, or ops), and the source then takes its route's current state. x-compliance-sync, the news pollers, web-commoncrawl-scanner and ig-webhook-receiver send their own source-level decisions; per-site publishing-rate checks are not the canary's in v1.
- Push and stream routes (AU-069): the canary reads the receivers' heartbeat counters (the Telegram canary channel and test group, PubSubHubbub renewals and notifications, Instagram webhook deliveries, the X stream's canary accounts) beside the SDK route counters it already reads (`source-health-canary §6.1 L96`), and flips the route; its `§3 L30` exclusion goes. Reconnecting the stream stays x-filtered-stream's own job.
- Credentials (CF-057): one `credentials` table for every client token, company-app key and vendor key: owner (client, app or vendor), Vault reference, scope, `state` (`ok`, `degraded`, `revoked`), `reason`, `changed_at`, `plan`; `vendor_keys` becomes its vendor rows. It is read and written only through the SDK's credential client, which injects the credential per job (`CONVENTIONS L12`), never hands out a `revoked` one, picks the first healthy token among the source's clients (`fb-page-feed-poller §5.2 L55`), stores refreshed OAuth tokens, and on a revoked platform credential sends a source-level `health_change` (`credential_revoked`) for each source no other credential can read (ADR-0021), which registry-writer applies as `blocked`, or as `fallback` where ADR-0021's automatic fallback allows. A new grant or key returns a credential to `ok`; a successful call clears `degraded`.

Why: Every health change gets one writer and one audit row, a route recovery can no longer erase a source's own problem, and token state lives where every service already gets its token, in the SDK.

## Consequences

Registry-writer (approved, ADR-0001) applies source-level decisions and keeps them apart from route changes; F3 adds the health columns and `credentials`; about forty section 8 lines name one store; the canary's scope grows to push heartbeats.

- CONVENTIONS v1.1: `credentials` replaces `vendor_keys` in the table list; the registry gains `health_reason`, `health_set_by` and `health_changed_at`; the 401, 403 and fallback rules are ADR-0021's.
- F3 creates `credentials` (owner, Vault reference, scope, `state`, `reason`, `changed_at`, `plan`) and the health columns; F4 and F6 build the credential client.

Sessions that must read this: F2, F3, then F4, F6, C7, C12, FB1, FB2, FB3, FB4, FB5, FB6, FB7, IG1, IG2, IG3, IG4, IG5, IG6, LI1, LI2, LI3, VLI3, TT1, VTT1, VTT2, TG1, TG2, VTG3, X1, X3, X4, X5, X6, X7, YT1, YT2, YT3, YT4, YT5, YT6, YT8, YT9, N2, N3, N8, W1, W2, W4, W5.
