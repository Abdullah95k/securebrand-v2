# ADR-0008 · Item kinds and mappers

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, listening-sdk, normalize-item, store-writer, keyword-matcher, comment-decay-scheduler, raw-archiver, and the lanes Discover and qualify, Fetch posts, Comments and Comments and stats (every `raw.items` producer)
Source: D2-Q008 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS lists no item kinds, and `kind` names both the item in a key (L69) and the job (L277). Three consumers branch on the item kind: store-writer files "`comment` or `reply`" in `comments` (`store-writer §5.2 L47`); keyword-matcher sends unregistered "post, video, article, message, result" to discovery and "Comments, replies" to mentions (`keyword-matcher §5.3 L74`, `L75`); comment-decay-scheduler opens series on `kind = post` (`comment-decay-scheduler §5.1 L42`). Producers write `post` or `video` for a video, `post` or `message` on Telegram, `comment` or `reply` for an X reply, and normalize-item's `quote` fits neither keyword-matcher branch (CF-068 a to d).

normalize-item parks any record without a mapper "by `(service, api_version)`" as `schema_unknown` (`normalize-item §5.2 L50`), yet eight producers have none (CF-008 b, AU-052 b), three record kinds are not content (`profile`, `poster-resolver §6.2 L92`; `reaction`, `li-notification-receiver §5.4 L98`; `search_response`, `web-search-perplexity §5.2 L55`), and partial YouTube records expect a hold normalize-item lacks (`yt-pubsub-receiver §6.2 L124`). At stake: those batches park for ever, and a kind one consumer does not list is dropped or misfiled.

Settles: CF-008, CF-068, AU-052, web-search-perplexity §14 Q5.
Depends on: ADR-0005 (the envelope), ADR-0007 (the keys), ADR-0038 (web items), ADR-0065 (partial YouTube records).

## Options

1. **Five content kinds, four archive-only record kinds, and a mapper registry** (chosen): its rules are under Decision.
2. **`post` for every top-level platform item, `video` only an attribute.** Consequences: consumers test fewer words, but three approved PRDs (tt-keyword-search, tt-hashtag-feed-poller, yt-keyword-search) and normalize-item's YouTube line move, and every video key changes (ADR-0007).
3. **Only content on `raw.items`: profiles, reactions and search responses move to their own paths (CF-008 option 2, CF-068 option 2).** Consequences: normalize-item sees only items, but raw-archiver gains three write paths with their own replay rules, and reactions need a writer on `item.metrics`.

## Decision

Five content kinds (`post`, `video`, `comment`, `article`, `result`), which are also the key's kind segment, and four archive-only record kinds (`profile`, `reaction`, `search_response`, `metrics`) that raw-archiver keeps and normalize-item skips. normalize-item runs mappers from a registry in listening-sdk keyed `(service, api_version)`.

- Content kinds, which are also the key's kind segment (ADR-0007): `post`, `video`, `comment`, `article`, `result`. `post`, `video`, `article` and `result` are top-level; `comment` is reply-level and always has a `parent_id` (ADR-0009). `video` is YouTube's and TikTok's; `result` is ADR-0038's web item, keyed `web:result:<canonical_url_hash>`. Platform nouns become attributes: normalize-item's `reply` is a `comment` with a parent; an X quote is a `post` with the quoted tweet's `item_id` in `quoted_id`; Telegram's `message` is a `post` in a channel and a `comment` in its discussion group. An X reply is a `comment` keyed `x:post:<id>` (ADR-0007), the one place where the key segment and the kind differ: X has one object type for every tweet, and as a `post` a reply would open its own paid series, send its author to discovery and be filed in `items`.
- Consumers: store-writer files `comment` in `comments`, the rest in `items`; keyword-matcher sends unregistered top-level items, quotes included, to discovery and comments to mentions; comment-decay-scheduler opens series on `post` and `video` (and `article` on Disqus sites, ADR-0061).
- Archive-only record kinds: `profile` (each resolver archiving its own lookups, ADR-0032), `reaction` (li-notification-receiver; counts come from li-client-posts-poller's absolute reads, ADR-0034), `search_response` (the web engines; `kind_hint` and `normalize = skip` go, ADR-0037) and `metrics` (a refresh read archived by a metrics service that writes its own `item.metrics`, ADR-0034). raw-archiver keeps them; normalize-item acknowledges and counts them and never parks them.
- Mappers (CF-008 a, b; AU-052 a, b, d): a registry in listening-sdk keyed `(service, api_version)`, each mapper written with its producer's fixtures and run by normalize-item; a record with neither a mapper nor an archive-only kind parks as `schema_unknown`. Where a service reads several vendor schemas, `api_version` names the one used, so `vendor` never selects the mapper (`tg-channel-posts-poller §8 L149`). New mappers: yt-pubsub-receiver, yt-uploads-reconciler, yt-keyword-search, ig-keyword-search, news-comments-fetcher, li-notification-receiver's comments, li-org-resolver's sampled posts (`li-org-resolver §13 L159`) and fb-client-webhook-receiver's posts.
- Partial YouTube records (CF-008 d): the details record completes the partial one as a new version of the same key, with no hold (ADR-0065). Web results (AU-052 c): search-hit-router writes the `result` items of ADR-0038 to `raw.items`, mapped by normalize-item's web line.

Why: It keeps the words most producers and the approved PRDs already use, gives every consumer one rule for top-level and reply-level items, and turns "parked for ever" into an explicit skip for records that were never meant to become items.

## Consequences

One enum in F2 and three consumers aligned; normalize-item (approved) reads its table from the registry, under ADR-0001; each producer's session writes its mapper; web-search-perplexity's question (`§14 Q5 L174`) is answered: archive-only.

- CONVENTIONS v1.1: the content and archive-only kinds beside `raw.items` and the key rule; the schema-change rule adds that an archive-only kind is acknowledged and counted, never parked.
- Each producer's session writes its mapper with its own fixtures. The new mappers are those of yt-pubsub-receiver, yt-uploads-reconciler, yt-keyword-search, ig-keyword-search, news-comments-fetcher, li-notification-receiver's comments, li-org-resolver's sampled posts and fb-client-webhook-receiver's posts. search-hit-router's web `result` items use normalize-item's existing web mapper (ADR-0038).

Sessions that must read this: F2, F4, then C2, C4, C5, C6, C8, FB7, LI3, VLI2, VIG1, VTG2, VTG3, X6, YT2, YT3, YT4, YT8, N8, W1, W2, W3, W4.
