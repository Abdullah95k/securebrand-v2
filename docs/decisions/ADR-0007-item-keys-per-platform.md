# ADR-0007 · Item keys per platform

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, facebook, instagram, tiktok, x, linkedin, telegram, youtube, news, web, normalize-item, deletion-propagator, x-compliance-sync, listening-sdk
Source: D2-Q007 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS keys an item `<platform>:<kind>:<platform_id>` (L69) without fixing the kind word or the id. On six platforms the PRDs differ, so one object read by two routes becomes two items, and what points at it misses:

- YouTube (CF-061): `youtube:post:<id>` in yt-pubsub-receiver, yt-uploads-reconciler and yt-video-details-fetcher (`yt-video-details-fetcher §9 L180`); `youtube:video:<id>` on the approved side: yt-keyword-search (`§6.2 L102`), normalize-item (`§5.3 L71`), yt-web-search-bridge's `extracted.kind` (`§6.2 L121`).
- TikTok (CF-062): `tiktok:video:<id>` in six PRDs, under envelope `kind` `post` (`tt-client-videos-fetcher §6.2 L99`) or `video`; `tiktok:post:<aweme_id>` in normalize-item (`§5.3 L67`).
- X (CF-065, AU-050): `x:post:<id>` in five readers, the approved x-recent-search (`§5.2 L57`) and normalize-item (`§5.3 L68`) among them; `x:comment:<id>` in x-replies-fetcher (`§6.2 L115`).
- Telegram (CF-063): `telegram:post:<username>/<id>` and `telegram:comment:<group chat id>/<id>` in the four content PRDs (`tg-message-search §5.2 L54`); `telegram:message:<chat_id>:<id>` in normalize-item (`§5.3 L70`).
- LinkedIn (CF-064): a share URN on the green route (`li-client-posts-poller §6.2 L114`), an activity URN or a URL hash (`li-post-search §6.2 L91`, `L105`), a bare id (`li-company-posts-poller §6.2 L111`).
- Instagram (CF-066, AU-053): Graph media ids on the green routes and in normalize-item (`ig-hashtag-search §6.2 L91`, `normalize-item §5.3 L66`); vendor ids that "may differ from Graph ids" (`ig-keyword-search §9 L144`).

Settles: CF-061, CF-062, CF-063, CF-064, CF-065, CF-066, AU-050, AU-053, ig-keyword-search §14 Q2, ig-mentions-fetcher §14 Q3, tg-channel-posts-poller §14 Q4, x-replies-fetcher §14 Q5.
Depends on: ADR-0006 (the key helper), ADR-0008 (the kind list), ADR-0009 (the key of a comment without an id).

## Options

1. **The majority form per platform, the kind segment equal to the item kind of ADR-0008** (chosen): its rules are under Decision.
2. **Keys from the record alone: the Instagram shortcode (AU-053 option 1) and the Telegram chat id (CF-063 option 2).** Consequences: no id map and rename-proof Telegram keys, but both approved Instagram parties move, Graph-only paths must look the shortcode up, and the Telegram vendor routes need a chat id no PRD shows them receiving.
3. **Route-specific keys joined in normalize-item (CF-064 option 3, CF-065 option 3, CF-066 option 1).** Consequences: no producer changes, but `item_id` stops being a function of one key, so the deletion paths and replays of ADR-0006 cannot derive it.

## Decision

Item keys take the majority form per platform, with the kind segment equal to the item kind of ADR-0008 (an X reply is the one exception): `youtube:video:`, `tiktok:video:`, `x:post:` for every tweet, Telegram keys on the lower-case username, LinkedIn activity URNs, and Instagram Graph media ids through a shared id map.

Keys split on the first two colons only, so the id may hold `:` or `/`; adapters build them with the shared helper (ADR-0006).

- YouTube: `youtube:video:<videoId>`, `youtube:comment:<id>`; partial and full records share the key (ADR-0065); the three `youtube:post:` PRDs move. search-hit-router's candidate key and the bridge's `extracted.kind` are not item keys.
- TikTok: `tiktok:video:<id>`, `tiktok:comment:<cid>`; normalize-item, the two `kind: post` envelopes and retention-purger's TikTok target (`§6.2 L102`) move.
- X: `x:post:<id>` for every tweet; x-replies-fetcher and x-full-archive-search's replies move. Compliance signals name a tweet by its id alone (`x-compliance-sync §5.3 L81`), so the key never depends on whether it is a reply; the reply link is `parent_id` (ADR-0009) and its item kind `comment` (ADR-0008), the one exception to the segment rule.
- Telegram: `telegram:post:<lowercase username>/<message_id>` for channel posts, `telegram:comment:<group chat id>/<message_id>` for discussion messages; a channel without a username uses its chat id. Every route has the username: the Apify Actors are fed usernames (`tg-channel-posts-poller §5.2 L62`), Telemetrio returns the username (`tg-channel-resolver §5.4 L67`), the bot knows both (`tg-bot-channel-receiver §5.2 L60`); VTG0, which could show otherwise, runs after F2 freezes keys. Risks: a renamed channel's posts can duplicate on a re-read (`tg-message-search §5.1 L44`), and a reused username can collide with the old channel's posts. normalize-item moves.
- LinkedIn: the activity URN, `linkedin:post:urn:li:activity:<id>` and `linkedin:comment:urn:li:comment:(urn:li:activity:<post id>,<comment id>)`. Every amber route has it (`li-post-search §5.4 L71`; li-company-posts-poller's `id` is the number in its post URL, `§5.4 L83-L84`), so the URL hash and the bare ids go. The green adapter converts its share URN, kept as an attribute. LI0 confirms where the green API gives the activity URN; if nowhere, green keeps share-URN keys and no amber route reads a client-administered page (li-company-posts-poller already stops, `§3 L26`; li-post-search drops such posts). normalize-item moves.
- Instagram: `instagram:post:<Graph media id>`, as both approved parties key posts, and `instagram:comment:<id>`. Vendor records map to the Graph id through a shared Instagram id map (shortcode, Graph media id, key), written only by the key helper and fed by the `permalink` of Graph reads (CONVENTIONS L166, L167); VIG0 checks whether the vendor returns Graph ids. A post only the vendor has seen gets a proposed shortcode key, `instagram:post:sc:<shortcode>`, from its `permalink` (`ig-keyword-search §5.4 L78`), which a Graph route that later reads the shortcode reuses. Instagram keys therefore depend on the map, not on the record alone; their golden vectors test the lookup rule. An id-less vendor comment takes ADR-0009's hash key.
- Unchanged here: Facebook; news (ADR-0036); web items `web:result:<canonical_url_hash>` (ADR-0038).

Why: It keeps the forms most PRDs and the approved ones use, picks the id every route can see, and confines the one stateful fallback to Instagram, pending the vendor probe.

## Consequences

F2 writes golden vectors per platform; the PRDs named above change, normalize-item (approved) under ADR-0001; F3 creates the Instagram id map.

- CONVENTIONS v1.1: the key section gains the per-platform table and the parse rule (split on the first two colons only); the Instagram id map joins the control-plane tables.
- LI0 confirms where the green LinkedIn API gives the activity URN, and VIG0 whether the vendor returns Graph media ids (`DEFERRED.md`); the fallback for each is in the rules above.
- Appendix C of `D2-PROPOSALS.md` summarised three open questions from an earlier draft: `tg-channel-posts-poller §14 Q4` as chat-id keys, and `ig-keyword-search §14 Q2` and `ig-mentions-fetcher §14 Q3` as a shortcode key with the Graph id as an attribute. The rules above are the answer: Telegram keys use the lower-case username (the chat id only for a channel without one), and Instagram keys use the Graph media id through the id map, with the shortcode form only for a post no Graph route has read.

Sessions that must read this: F2, F3 (the Instagram id map), then C4, C13, IG2, IG3, IG5, VIG1, VIG2, TT1, VTT1, VTT2, VTT4, VTT5, VTT6, X1, X4, X5, X6, X7, LI1, LI2, LI3, VLI1, VLI3, VLI4, TG1, TG2, VTG1, VTG3, YT2, YT3, YT4, YT8, YT9, W3.
