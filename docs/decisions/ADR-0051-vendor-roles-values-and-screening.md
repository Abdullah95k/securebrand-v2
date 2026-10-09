# ADR-0051 · Vendor roles, values and screening

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, qualifier, registry-writer, quota-governor, source-health-canary, web-search-perplexity, web-search-mojeek, web-gdelt-poller, D3, and every amber service: fb-keyword-search, fb-group-posts-poller, fb-group-comments-fetcher, ig-keyword-search, ig-comments-fetcher, tt-keyword-search, tt-hashtag-feed-poller, tt-user-resolver, tt-profile-videos-poller, tt-video-comments-fetcher, tt-video-stats-refresher, li-post-search, li-org-resolver, li-company-posts-poller, li-post-comments-fetcher, tg-message-search, tg-channel-resolver, tg-channel-posts-poller
Source: D2-Q051 (user decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS lists five flags, each "off, or the vendor name" (L238), adds `TG_POSTS_ACTOR` with Actor names (L280), and spells those Actors `apify_tugelbay` and `apify_sovereigntaylor` in the registry (L36), as tg-channel-posts-poller's records do (`§6.2 L112`). D1 found:

- One value per flag where two roles or a fallback need two: the approved Telegram PRDs treat any value but `off` as on, since Telemetrio serves search and stats and an Actor serves posts (`tg-message-search §14 Q2 L153`, `tg-channel-resolver §14 Q3 L166`); EnsembleData is "primary or fallback per the flag" (L177); ScrapeCreators may have no keyword search (`fb-keyword-search §5.3 L63`, `§14 Q1 L181`), while fb-group-posts-poller proposes it as primary (`§14 Q3 L195`).
- Engines in `vendor` on green records (`web-search-perplexity §6.2 L97`, `web-search-mojeek §6.2 L96`, `web-gdelt-poller §6.2 L99`), other green records `null`; a Telegram channel's row says `telemetrio` (`tg-channel-resolver §4 L34`) while an Actor reads its posts.
- Clearance: SociaVault, ScrapeCreators and TikHub are listed as "Weakly cleared (country known, owner not verified)", and the Actor publishers harvestapi, tugelbay and sovereigntaylor are not listed (L6, L190, L199); three PRDs ask who verifies them, and when (`fb-group-posts-poller §14 Q4 L196`, `li-company-posts-poller §14 Q4 L187`, `li-post-comments-fetcher §14 Q6 L197`).
- The X plan gate under three names (CF-103 e).

At stake: which vendor is paid and named to clients, and whether an unverified owner slips past the no-Israeli-vendor rule.

Settles: CF-097, CF-103, fb-group-posts-poller §14 Q3, fb-group-posts-poller §14 Q4, fb-keyword-search §14 Q1, li-company-posts-poller §14 Q4, li-post-comments-fetcher §14 Q6, tg-channel-resolver §14 Q3, tg-message-search §14 Q2.
Depends on: ADR-0050 (flags in a control-plane table, fallback set only by the canary, the X plan gate).

## Options

1. **One setting per vendor role, the cleared vendor first, owners verified before any spend** (chosen): its rules are under Decision.
2. **One vendor per platform where possible:** SociaVault for all amber Facebook and Instagram services, EnsembleData alone for TikTok. Consequences: fewer contracts and owner checks; Facebook group and comment requests cost about twice as much or more; no TikTok fallback.
3. **Flags as on/off switches per platform; vendors and fallback order only in the vendor rows of `credentials`** (CF-103 option 2). Consequences: ops switch vendors without touching flags; the flag no longer says who is paid, so an audit reads two places.

## Decision

One setting per vendor role, the cheaper vendor where it has the endpoint and the cleared one where there is a choice, with a fallback order that only the canary switches; one lower-case spelling for vendor names everywhere; and no weakly cleared vendor or Actor publisher is paid until the user, or counsel for the user, has verified its owner and country.

- (a) Primaries. Facebook: `FB_VENDOR_ROUTE = scrapecreators` (groups, group comments) with an override `fb-keyword-search = sociavault` while ScrapeCreators has no search (fb-keyword-search Q1); ScrapeCreators costs half of SociaVault or less per request (USD 0.99 against 1.99 and USD 1.88 against 4.83 per 1,000 at each end of the ranges, one SociaVault credit per request, L92; fb-group-posts-poller Q3). Instagram: `sociavault`. TikTok: `ensembledata` (cleared, Singapore, already contracted, L6, L177) unless VTT0, which compares cost since its contract price is not in the fact sheet, shows otherwise; TikHub the fallback once its owner is verified. LinkedIn: `harvestapi`. Telegram: `TG_VENDOR_ROUTE = telemetrio` for search and stats and `TG_POSTS_ACTOR` for posts, as L280 already splits them, each service reading its own flag's value (tg-message-search Q2, tg-channel-resolver Q3); the primary Actor chosen by the one-week, 50-channel comparison tg-channel-posts-poller proposes (Q3), run in staging after VTG0 on a budget the user sets (the VTG0 brief caps spend at USD 5), the other Actor the fallback.
- (b) Fallback order per role in the vendor rows of `credentials` (ADR-0016, which absorbs `vendor_keys`), switched only by the canary (ADR-0050); a blocked green source's automatic move to its amber route is ADR-0021's.
- (c) One lower-case spelling in flags, `sources.vendor` and `provenance.vendor`, naming who collects: `sociavault`, `scrapecreators`, `tikhub`, `ensembledata`, `harvestapi`, `telemetrio`, `tugelbay`, `sovereigntaylor` (Actor paths and the Apify account in configuration). On green records `vendor` names the licensed engine (`perplexity`, `mojeek`, `gdelt`), else `null`; amber filters read `route`, never `vendor`.
- (d) `sources.vendor` names the vendor that reads the source's posts (a Telegram channel: its Actor; a Telegram keyword rule: `telemetrio`); registry-writer updates a role's rows when its primary changes; during a fallback each record names the vendor that returned it.
- (e) The user, or counsel for the user, verifies the owner and country of each weakly cleared vendor and Actor publisher before its probe (VFB0, VIG0, VTT0, VLI0 and VTG0 already need the contract and the flag value) and at each renewal, recorded in `docs/dependencies.md` and the CONVENTIONS list; until then its flag value cannot be set (fb-group-posts-poller Q4, li-company-posts-poller Q4, li-post-comments-fetcher Q6). Perplexity, flagged "client decides" (L6), keeps `vendor = perplexity` so a client may decline it (D3 specifies the setting).
- (f) The X plan gate: as ADR-0050 decides.

Why: It uses the cheaper vendor where it has the endpoint and the cleared one where there is a choice, and it makes the owner check a condition of any spend.

## Consequences

Two Facebook vendors to contract and screen; TikTok starts on a cleared vendor; CONVENTIONS L6, L36, L238 and L280 aligned; tg-channel-resolver and tg-message-search (approved) change under ADR-0001; values are renamed before any data exists.

- CONVENTIONS v1.1: the Actor publishers and the verification rule in the vendor list (v1 L6); the vendor values (v1 L36); one flag list with roles and the override (v1 L238, L280).
- F3 seeds the flag rows `off` (ADR-0050) and the vendor rows of `credentials` with their fallback order.
- `DEFERRED.md`: the user, or counsel, verifies the owner and country of each weakly cleared vendor and Actor publisher before its probe and at each renewal (SociaVault, ScrapeCreators, TikHub before VFB0, VIG0 and VTT0; harvestapi before VLI0; tugelbay and sovereigntaylor before VTG0); the Telegram Actor comparison (VTG3, in staging after VTG0, on a budget the user sets); TikHub as TikTok's fallback once verified (VTT0).

Sessions that must read this: F2, F3, then F4, C7, C12, the vendor probes VFB0, VIG0, VTT0, VLI0 and VTG0, VFB1 to VFB3, VTT1 to VTT6, VLI1 to VLI4, VTG1 to VTG3, W1, W2, W4, YT9, X1 to X6.
