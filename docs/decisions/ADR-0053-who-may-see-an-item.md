# ADR-0053 · Who may see an item

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all (every producer declares its visibility), F2, F3, keyword-matcher, deletion-propagator, quota-governor, x (every X service), Q1, U2, D3 (the query API and client portal)
Source: D2-Q053 (user decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

keyword-matcher decides which clients an item is matched for: items from `owned_by_client` sources, or classed `meta_on_request` or `linkedin_48h`, go only to the source's `client_ids`; "Everything else is the shared pool", government rules aside (`keyword-matcher §5.3 L68` to `L70`). It asks whether Meta items may join the pool ("The draft says no", `§14 Q4 L183`); tt-client-videos-fetcher proposes showing its items only to the authorising client (`§14 Q4 L179`, `§9 L142`). The platforms:

- Meta: "Tech Provider processes only on behalf of its client", "no sale or licensing of Platform Data" (`CONVENTIONS L163`); our PPCA calls are made "on behalf of the client whose keyword triggered it" (`fb-page-search §5.3 L67`), with a watching client's token (`fb-page-feed-poller §5.2 L55`).
- Client grants: LinkedIn Community Management covers client-administered pages, and "member data cannot be exported to customers" (L90, L192); TikTok Display reads the client's own videos (L176); our Telegram bot reads channels whose owners, "client staff, or a cooperating outlet", invite it (`tg-bot-channel-receiver §4 L33`).
- Our licences: X through our company app, though "a multi-client product requires an Enterprise plan" (L87); YouTube through our company key (L12); our news crawler; web results we may store (L218, L219).

At stake: a client seeing data it has no right to, or every client re-adding sources the registry already reads.

Settles: keyword-matcher §14 Q4, tg-message-search §14 Q3, tt-client-videos-fetcher §14 Q4, x-recent-search §14 Q3.
Depends on: ADR-0043 (`client_sources`), ADR-0050 (the X plan gate), ADR-0052 (amber consent).

## Options

1. **Visibility follows the grant the data was fetched under** (chosen): its rules are under Decision.
2. **Per client for everything.** Consequences: the simplest story for a platform; a client sees no site, channel or account until it is on its own list, so discovery and share of voice shrink to its own registry.
3. **Pool everything except `owner` data, Meta PPCA included.** Consequences: the widest coverage; it contradicts L163 and the approved fb-page-search, and risks PPCA, the only green route to Facebook Pages, at Meta's annual Data Use Checkup (L154).

Also not taken: option 1's alternative for X alone, to pool X on pay-per-use from the start and accept the risk that X objects at use-case review.

## Decision

Visibility follows the grant the data was fetched under: a client's own grant to that client only, Meta public-content data to the clients watching the source, our own licences and the open web to every client whose keywords match, and amber data to that pool, limited to clients that accept amber. X joins the pool only once the X plan is Enterprise; until then X data reaches only the clients declared to X.

Each producing service declares one value in the contracts package; keyword-matcher's gate reads it through `provenance.service`, not the retention class:

- `owner`: a client's own grant (Page or Instagram account token and webhooks, LinkedIn Community Management, TikTok Display, our bot in the client's own channel): the authorising client only, even if others watch the property (tt-client-videos-fetcher Q4: yes).
- `watchers`: Meta data under PPCA or Instagram Public Content Access: the clients in the source's `client_ids` only (keyword-matcher Q4: no).
- `pool`: our own licences and the open web (X under the point below, YouTube, news, web search, Telegram channels a non-client owner opened to the product): every client whose keywords match.
- Amber: the pool, limited to accepting clients (ADR-0052).
- X before Enterprise: X's self-serve plan serves "a limited number of end users" and "a multi-client product requires an Enterprise plan" (CONVENTIONS L87, L188; `x-recent-search §7 L146`). So X joins the pool only once `X_PLAN = enterprise`; until then X data reaches only the clients declared to X at use-case review (`clients.x_end_user_declared`, ADR-0050), and quota-governor's `x_enterprise_required` alert (`quota-governor §13 L164`) fires when a further client would receive it. The move to Enterprise comes at the first government end user or the second paying client on X, whichever is first (`x-recent-search §14 Q3 L194`); its price is not in the fact sheets and must be quoted by X.

It also answers: Mentions found on channels the qualifier rejected stay visible as mentions (the item matched a client's keyword; rejecting the channel only keeps it out of the registry), on every search route (`tg-message-search §14 Q3`).

Why: Meta and client-authorised APIs bind data to a client; our licences and the open web do not, so pooling those gives every client the full registry at no extra cost.

## Consequences

A new client sees every pooled source from day one; Meta coverage grows with each client's own registered sources; a property one client owns reaches another only through a public-route read on that client's behalf, so F3 records owners apart from watchers; offboarding deletes data held only for the departing client (`deletion-propagator §13 L165`); the query API and portal (D3) apply the same rule.

- CONVENTIONS v1.1: each route's visibility in the service index (v1 L224 to L236); the X plan gate covers every client, not only government ones (v1 L113 and the X service index).
- F2 records each producing service's visibility value in the contracts package; F3 records owners apart from watchers.
- The user moves X to Enterprise at the first government end user or the second paying client on X, whichever comes first; X must quote its price.
- `DEFERRED.md`: counsel confirms that one PPCA read may serve every client watching a Page (owner FB2, before App Review).

Sessions that must read this: F2 (each producer's visibility), F3 (owners recorded apart from watchers), then C5, C13, Q1, U2, FB2, FB7, IG4, LI1, TT1, TG1, X1 to X7 (the X plan gate).
