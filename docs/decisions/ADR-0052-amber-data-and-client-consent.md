# ADR-0052 · Amber data and client consent

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, quota-governor, comment-decay-scheduler, keyword-matcher, qualifier, registry-writer, source-health-canary, ig-hashtag-search, tt-client-videos-fetcher, tg-bot-channel-receiver, D3, and every amber service: fb-keyword-search, fb-group-posts-poller, fb-group-comments-fetcher, ig-keyword-search, ig-comments-fetcher, tt-keyword-search, tt-hashtag-feed-poller, tt-user-resolver, tt-profile-videos-poller, tt-video-comments-fetcher, tt-video-stats-refresher, li-post-search, li-org-resolver, li-company-posts-poller, li-post-comments-fetcher, tg-message-search, tg-channel-resolver, tg-channel-posts-poller
Source: D2-Q052 (user decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS makes amber services optional, flagged, disclosed and "excluded from government contracts" (L7), with no per-client consent and no `clients` columns (L30). The PRDs split (AU-092): four check that a client "accepted the amber provenance" or that its contract allows amber (`ig-comments-fetcher §5.1 L41`, `ig-keyword-search §5.2 L58`, `tt-profile-videos-poller §5.1 L43`, `tt-client-videos-fetcher §3 L27`); the Telegram, other TikTok and Facebook amber services check only the government flag (`tg-channel-posts-poller §5.1 L42`, `tt-keyword-search §5.2 L48`, `fb-group-posts-poller §5.1 L40`). Also:

- comment-decay-scheduler opens amber series whenever the flag is on, reads no `clients` and never cancels on flag-off (`comment-decay-scheduler §5.1 L44`, `§6.1 L135`), unlike `fb-group-comments-fetcher §5.1 L42` (AU-038).
- A client's 31st Instagram hashtag is queued under rule 5 (`ig-hashtag-search §12 L168`, `qualifier §5.2 L56`) or registered amber (`ig-keyword-search §3 L20`, `§13 L169`) (AU-060); budget waits are announced as `fallback_on`, which nothing applies or ends (`ig-hashtag-search §5.1 L57`; AU-087); the canary has no Instagram alternate (`source-health-canary §5.1 L47`) though `ig-hashtag-search §8 L144` expects one (AU-071).
- Client-owned TikTok accounts and Telegram bot channels are green rows (`tg-bot-channel-receiver §5.2 L70`) relying on a daily amber reconciliation that selects only amber rows (`tt-client-videos-fetcher §8 L132`, `tg-channel-posts-poller §5.1 L44`) (AU-091); asked in `tt-profile-videos-poller §14 Q3 L188` and, for 90 days of pre-join history, `tg-bot-channel-receiver §14 Q6 L199`.

At stake: a commercial client receiving vendor-bought data it never agreed to, and vendor money spent on data no client may use.

Settles: AU-038, AU-060, AU-071, AU-087, AU-091, AU-092, fb-group-comments-fetcher §14 Q4, tg-bot-channel-receiver §14 Q6, tt-profile-videos-poller §14 Q3.
Depends on: ADR-0021 (the government exclusion, and the automatic fallback of one blocked source), ADR-0050 (flags, and fallback as a health state).

## Options

1. **Amber by explicit consent, never on a client's own properties** (chosen, with ADR-0021's automatic fallback of a blocked client-owned property): its rules are under Decision.
2. **Option 1, but an accepting client's own properties may also be read through the vendor:** daily reconciliation and outage gap fill (the amber pollers also select green push sources of accepting clients, AU-091 option 1) and an opt-in 90-day Telegram pre-join history, marked amber. Consequences: no lost Telegram posts after a long outage, history for new channels, and the view counts the bot lacks (`tg-bot-channel-receiver §5.4 L103`); a daily vendor read per owned property; mixed provenance on a client's own channel.
3. **Government flag only, as CONVENTIONS L7 says.** Consequences: no consent column; every non-government client receives amber data while a flag is on, even one whose contract excludes it.

## Decision

A client receives amber data only if its contract accepts vendor data (`clients.accepts_amber`, off by default and always off for government clients); a client's own properties are read through a vendor only in ADR-0021's automatic fallback, once their green access is lost (the user's answer of 9 Oct 2026); a client's 31st Instagram hashtag in a week goes to the vendor only for a client that accepts amber, and otherwise waits.

- (a) `clients.accepts_amber`, off by default, set when the client's contract allows vendor data (D3 specifies the screen), always off for `client_type = government` (a check in F3). Amber schedulers select a source only if one of its clients accepts amber; amber jobs re-check at run time and end without a call if none does; amber records list only accepting clients in `client_ids`; keyword-matcher fans amber items out to accepting clients only (ADR-0053).
- (b) comment-decay-scheduler, which then reads `clients`, opens an amber series only while the flag is on, an accepting client watches the source and its vendor spend is under the cap (rule 5, the per-source sub-counter of ADR-0042); it cancels open series when the flag goes off or the last accepting client leaves (its catch-up rule, `§5.1 L44`, applies if the flag returns).
- (c) Rule 5 gains the Instagram cap (30 hashtags per business account per 7 days, L89). Over the cap of a client's account, the hashtag is registered `route = amber`, `vendor = sociavault` (read by ig-keyword-search) if that client accepts amber and `IG_VENDOR_ROUTE` is on; otherwise it is queued and the client told. ig-hashtag-search reports budget waits as `updated` with `budget_wait`, never `fallback_on` (qualifier and ig-hashtag-search, both approved, move under ADR-0001).
- (d) The canary fallback for green hashtags is declared in `canary_targets` (`alternate_vendor = sociavault`, `flag_name = IG_VENDOR_ROUTE`, `scope = non_government`), as ig-hashtag-search expects; while it lasts, only accepting clients receive the items.
- (e) A client's own green properties (TikTok Display accounts, Telegram bot channels, owned Pages and accounts) are not read through a vendor beside their green read: no daily amber reconciliation, no outage gap fill, no pre-join history (tt-profile-videos-poller Q3 and tg-bot-channel-receiver Q6: no). The green read counts as complete; outages are reported to the client. When a property's green access is lost, ADR-0021's automatic fallback reads it through the vendor like any other source (the user's answer of 9 Oct 2026).
- With ADR-0021's automatic fallback, (a) holds for one source and for a whole route: a blocked green source, a client-owned property included (the user's answer of 9 Oct 2026), moves to its amber route only when a client that accepts amber watches it and no government client does, and while a route is in `fallback` its amber reads take only the sources an accepting client watches; only accepting clients receive the records, so a property's owner receives them only if its own contract accepts amber (ADR-0021).

Why: Amber data rests on the vendor's contract, not ours, so a client should take it knowingly; a property authorised through the platform's own route should not be re-read through a scraper while that route works; when it is lost, the fallback is announced to ops and the client is asked to grant access again (ADR-0021).

## Consequences

One column and one SDK check for the 18 amber services (README L16), replacing the government-only check in most and touching six approved PRDs (ADR-0001); vendor money only for data a client accepted; a client's Telegram posts missed in a receiver outage longer than Telegram keeps updates (24 hours, to be confirmed, `tg-bot-channel-receiver §5.1 L52`) are lost and reported; TikTok completeness rests on `video.list` returning every video (`tt-client-videos-fetcher §14 Q1 L176`).

- CONVENTIONS v1.1: consent beside disclosure and the government exclusion (v1 L7); rule 5 gains the Instagram cap (v1 L246).
- F3 adds `clients.accepts_amber` with the check that keeps it off for government clients; F4 builds the one SDK consent check the 18 amber services use; D3 specifies the screen that sets it.
- `DEFERRED.md`: option 2 for Telegram, an accepting client's own channels gap-filled through the vendor, once the pilot has measured receiver outages (owner TG1).

Sessions that must read this: F2, F3, then C1, C5, C7, C9, C11, C12, IG2, TT1, TG1, VIG1, VIG2, VFB1 to VFB3, VTT1 to VTT6, VTG3, and the other amber sessions (VTG1, VTG2, VLI1 to VLI4).
