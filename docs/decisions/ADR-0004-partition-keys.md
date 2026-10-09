# ADR-0004 · Partition keys

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q004 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS partitions every topic "by `source_id` unless noted" and notes nothing (L14), and every job queue by `source_id` "so one source is never worked twice at once" (L28). Writers chose other keys for good reasons (CF-003 b to g, CF-087 b to d): `search.results` by `canonical_url_hash`, so every engine's sighting of a URL reaches one router partition (`web-search-perplexity §6.2 L90`); `crawl.policies` by `host` (`news-robots-checker §6.2 L93`); `news.dedup` by `story_id` (`news-dedup §6.2 L84`); author-scope `deletions` by the author hash (`retention-purger §6.2 L94`); `registry.decisions` by `candidate_key` or `source_id` (`qualifier §6.2 L81`); resolver queues by `candidate_key` (`fb-page-resolver §5.1 L42`); fb-page-search by `keyword_id` (`fb-page-search §5.1 L40`). Others name none: the canary's decisions, tg-message-search's keyword sets (`tg-message-search §5.2 L51`) and the ops jobs.

One point is a real disagreement (CF-003 h, AU-019). normalize-item has search finds "keyed by the producer on `<platform>:<poster platform_id>`" (`normalize-item §5.1 L41`), and keyword-matcher and store-writer follow (`keyword-matcher §5.1 L40`, `store-writer §5.1 L39`); CONVENTIONS sets a find's `source_id` to "the keyword-rule or hashtag source that produced the query" (L281), as the approved search producers do (`ig-hashtag-search §6.2 L91`, `tt-keyword-search §6.2 L73`), while li-post-search sets none (`li-post-search §6.2 L87-L94`) and the web engines write `web:<source_id>` (`web-search-perplexity §6.2 L89`). At stake: the SDK producer sets the key, so a key the contract does not name cannot be produced, and readers that assume `source_id` mis-order the rest.

Settles: CF-003, CF-087, AU-019, deletion-propagator §14 Q4.
Depends on: ADR-0010 (the name `author_ref`), ADR-0031 and ADR-0033 (the keys of `discovery.hits` and `poster.profiles`), ADR-0032 (candidate keys), ADR-0044 (keyword-rule rows).

## Options

1. **One declared key per topic and per queue, `source_id` by default, the exceptions named** (chosen): its rules are under Decision.
2. **As 1, with the poster key also allowed on `items.normalized` and the hit topics when `source_id` is absent (CF-003 option 2).** Consequences: no search producer changes, but three topics carry two keys and every consumer handles both.
3. **`source_id` on everything (CF-003 option 3, CF-087 option 2).** Candidates, hosts, stories, authors and ops runs get a registry row or a synthetic id. Consequences: one key, but registry rows for things that are not sources, and the per-host and per-story order the news services rely on is lost.
4. **A free `partition_key` field set by each producer (CF-087 option 3).** Consequences: flexible, but nothing says which key a queue uses, so its producers can disagree again.

## Decision

Each topic and each job queue has one declared partition key, recorded by F2 and set by the SDK producer, never by the caller: `source_id` by default, with the exceptions below.

F2 records the key of every topic and queue, per scope or kind where one carries several subjects; the SDK producer sets the Kafka key from that record, never from the caller. `source_id` stays required on every message and job about a source.

- Topic exceptions: `search.results` by `canonical_url_hash`; `crawl.policies` by `host`; `news.dedup` by `story_id`; `deletions` by `author_ref` for author scope and `client_id` for client scope; `registry.decisions` by `candidate_key` about a candidate, `source_id` about a source, `platform` for a route-level `health_change`; `discovery.hits` and `poster.profiles` by `candidate_key` (ADR-0031, ADR-0033; an ordinary individual's answer on `poster.profiles` by `author_ref`, ADR-0033), as are `raw.items` records about a candidate not yet a source (ADR-0005); `jobs.completed` by the key of the job it reports.
- Search finds: every search producer sets `source_id` to its keyword-rule or hashtag row (li-post-search adds it, the web engines drop `web:`), and the poster key goes. A found post's comment jobs carry the post's `source_id`, so post and comments still share a partition.
- Queue exceptions: the eight resolver queues and `jobs.poster-resolver` by `candidate_key` on every job, a registered source's `refresh` carrying its `<platform>:<platform_id>` key, so registration does not move an account; `jobs.news-robots-checker` by `host`; `rematch` by `client_id`; `replay`, `rerun`, `recompute` and `retention_sweep` by their `request_id` or `run_id`, since order does not matter there (`aggregator §5.1 L37`). fb-page-search and tg-message-search key on their keyword-rule row's `source_id` (ADR-0044; tg-message-search already calls its set a `keyword_rule` row, `§5.1 L41`), and an X gap job on its rule's first source (`x-filtered-stream §5.2 L70`), so both are the default.

Why: It keeps CONVENTIONS' default and search output rule, records the exceptions the writers chose for good reasons (order per host, story or candidate), and lets the SDK, not each service, set the key.

## Consequences

Five approved PRDs change under ADR-0001 (normalize-item, li-post-search, web-search-perplexity, fb-page-search, tg-message-search); keyword-matcher and store-writer drop the poster key; a post found by two rules can reach two normalize-item workers, which derive the same `item_id` (ADR-0006), so the stores upsert one item.

- CONVENTIONS v1.1: the event bus section carries the key of every topic and queue, and the rule that a message or job about no source names its key in the contract. The search output rule adds that a search find's `source_id` (its keyword-rule or hashtag row) is also its partition key.
- PRD edits made by D2, citing this ADR: normalize-item §5.1 L41 and §6.2 L91, keyword-matcher §5.1 L40 and store-writer §5.1 L39 lose the poster key.
- F2 records the key per topic and per queue, per scope or kind where one carries several subjects; F4 and F6 set the Kafka key from that record.

Sessions that must read this: F2, F4, F5, F6, then C4, C5, C6, C8, C13, C14, A1, A2, A3, A4, FB1, FB6, IG1, IG2, VTT1, VTT2, VTT3, X2, X4, X7, VLI1, VLI2, VTG1, VTG2, YT1, YT7, YT8, N1, N2, N7, W1, W2, W3, W4.
