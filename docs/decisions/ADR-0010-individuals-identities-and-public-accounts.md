# ADR-0010 · Individuals' identities and public accounts

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q010 (user decision; changed by the user's answer) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

Individuals are never profiled and a mention keeps a hashed author reference (CONVENTIONS L114, L248). The PRDs implement it five ways (CF-069):

- normalize-item: `author_ref = hmac_sha256(AUTHOR_HASH_KEY, platform + ':' + author_platform_id)` (`normalize-item §5.2 L54`), stored and carried as `author_ref` (`store-writer §6.2 L110`, `keyword-matcher §6.2 L111`).
- poster-resolver: `author_hash = sha256(platform || platform_id || salt)` (`poster-resolver §5.2 L59`), carried by qualifier and registry-writer; the deletion paths use normalize-item's helper but search a column `author_hash` (`retention-purger §5.3 L78`, `x-compliance-sync §5.3 L81`, `deletion-propagator §5.3 L60`) that no writer fills.
- Eleven fetchers hash at the edge, each with its own name and rendering (CF-069 d, AU-048), against "every record exactly as a fetch or push returned it" (`CONVENTIONS L15`); README decision 8 excepts only TikTok commenters (`README L185`; CF-109 b); other routes keep identities raw (`ig-own-comments-fetcher §7 L139`).
- Some scope the hash, so one person gets several references: per YouTube channel (`yt-comments-fetcher §5.2 L56`, `§14 Q4 L206`), per X source (`x-replies-fetcher §5.2 L59`), per Disqus thread (`news-comments-fetcher §5.3 L76`).
- Resolvers answer for individuals with `candidate_ref`, a plain `candidate_key_hash`, or the clear `candidate_key` (CF-069 f).

ig-comments-fetcher asks for one shared key (`§14 Q2 L179`); tt-video-comments-fetcher and tg-discussion-receiver ask whether normalize-item accepts a reference computed at the edge (`§14 Q4 L184`, `§14 Q4 L201`). Also open: whether unregistered business accounts keep their identity (`ig-webhook-receiver §7 L135` against `normalize-item §5.2 L54`; AU-089), and what `raw.items` holds for services that write an extract or no raw record (`news-article-extractor §5.3 L75`, `tt-user-resolver §13 L165`, `tt-video-stats-refresher §6.2 L112`; CF-109 c, d).

The user's answer, 7 Oct 2026: "Q010 as the client should be able to see a list of individuals and be able to filter or rank them in order then use them later to further understand the segments." Asked again, the user chose "Public accounts only": clients can list, filter, rank and save public accounts (pages, channels, media, creators and public figures, verified or above a follower count the user sets); ordinary people stay anonymous and show up only in segments, as counts by language, dialect, region, sentiment and topic; the platforms' terms are respected.

Settles: CF-069, CF-109, AU-048, AU-089, fb-group-posts-poller §14 Q5, ig-comments-fetcher §14 Q2, li-notification-receiver §14 Q5, li-post-comments-fetcher §14 Q5, news-comments-fetcher §14 Q4, normalize-item §14 Q1, tg-discussion-receiver §14 Q4, tt-user-resolver §14 Q3, tt-video-comments-fetcher §14 Q4, x-replies-fetcher §14 Q6, yt-comments-fetcher §14 Q4.
Depends on: ADR-0005 (the `raw.items` envelope that carries the reference).

## Options

1. **One platform-wide keyed reference, computed at the edge for everyone who can never become a source.** _Taken for ordinary people, with the public-account rule added (see Decision)._
   - One SDK function, in both languages with golden vectors: `author_ref = HMAC-SHA256(AUTHOR_HASH_KEY, "<platform>:<author platform id>")`, 64 lower-case hex; one name, `author_ref`, everywhere (`author_hash`, `candidate_ref` and `candidate_key_hash` renamed; an approved PRD moves under ADR-0001). The key lives in Vault and is rotated only after a compromise; the new key covers new data, and a deletion by author tries every key still covering retained data.
   - Not scoped, so deletion by author and distinct-author counts work. The safeguard is on the query side: no client-facing view, export or query lists or ranks individual references, and YouTube rollups follow ADR-0056.
   - Where: the adapter replaces every commenter's, replier's, reactor's and member's identity before the first write, on every route (README decision 8 widened). normalize-item passes an edge `author_ref` through as given and computes it with the same helper for posters whose ids are still clear (AU-048). Registered sources keep `author_source_id` (an SDK registry-cache lookup) and are the only authors with a name downstream (AU-089 option 1). Discovery posters keep their platform id until poster-resolver classes them; once classed individual, raw-archiver replaces the id in the archive through the deletions' rewrite path, and the resolver's answer carries `author_ref` only, with no clear `candidate_key` (`tt-user-resolver §6.2 L111`, `§14 Q3 L171`).
   - `raw.items` is "the record as returned, minus identities"; news articles are an extract by rule (copyright). tt-user-resolver writes no raw record because its answers are mostly about individuals, whose profiles are never kept; tt-video-stats-refresher writes none because its reads are counts of archived videos, carried by `item.metrics`, so it parks an unknown reading.

   Consequences: no individual's clear identity is stored past classification, except on the event bus: discovery posters' ids sit in `raw.items`, the `discovery.hits` candidate and DLQs until topic retention expires (a setting, kept short). Replays cannot recover identities.

2. **As option 1, plus scoped references for analytics.** _Not taken._ The platform-wide reference serves deletions only, in a column no client query reads; analytics rows carry one scoped per source, as x-replies-fetcher and yt-comments-fetcher propose. Consequences: cross-source linking is impossible, not only forbidden; distinct-author counts work only inside one source; two references per person.
3. **CONVENTIONS as written: `raw.items` keeps every record as returned, and only normalize-item hashes.** _Not taken._ Edge hashing is reverted, TikTok's included. Consequences: replay can re-derive references, but the archive holds individuals' ids and names for its whole retention (24 months under `vendor_agreed`), against README decision 8.

Also not taken: listing every person, the reading of the user's first answer. Asked again, the user chose to list public accounts only, which keeps ordinary people anonymous; the consequence is that a client cannot list or rank people who are neither public nor registered, and sees them only as counts.

## Decision

Option 1 stands for ordinary people: one keyed `author_ref` per person per platform, computed at the edge, no clear identity of an ordinary person stored after classification, and no client view, export or query that lists or ranks them. One rule is added: clients may list, filter, rank and save public accounts, and use the saved lists as segments, except where a platform's terms forbid listing that kind of account.

**Ordinary people (option 1)**

- One SDK function in both languages, with golden vectors: `author_ref = HMAC-SHA256(AUTHOR_HASH_KEY, "<platform>:<author platform id>")`, 64 lower-case hex. One name, `author_ref`, everywhere: `author_hash`, `candidate_ref` and `candidate_key_hash` are renamed (an approved PRD moves under ADR-0001). The key lives in Vault and is rotated only after a compromise; the new key covers new data, and a deletion by author tries every key still covering retained data.
- The reference is not scoped, so deletion by author and distinct-author counts work. The safeguard is on the query side (below).
- Where it is computed: the adapter replaces every commenter's, replier's, reactor's and member's identity before the first write, on every route (README decision 8 widened). normalize-item passes an edge `author_ref` through as given and computes it with the same helper for posters whose ids are still clear (AU-048). Registered sources keep `author_source_id`, an SDK registry-cache lookup (AU-089 option 1). Discovery posters keep their platform id until poster-resolver classes them; once one is classed an ordinary individual, raw-archiver replaces the id in the archive through the deletions' rewrite path, and the resolver's answer carries `author_ref` only, with no clear `candidate_key` (`tt-user-resolver §6.2 L111`, `§14 Q3 L171`).
- `raw.items` is "the record as returned, minus identities"; news articles are an extract by rule (copyright). tt-user-resolver writes no raw record, because its answers are mostly about individuals; tt-video-stats-refresher writes none, because its reads are counts of archived videos carried by `item.metrics`, so it parks an unknown reading.
- No ordinary person's clear identity is stored past classification, except on the event bus: discovery posters' ids sit in `raw.items`, the `discovery.hits` candidate and DLQs until topic retention expires (a setting, kept short). Replays cannot recover identities.

**Public accounts (the rule the user added)**

- A public account is any of:
  - a registered source;
  - a poster that poster-resolver classes as an organisation, page, channel or media (F2's closed `account_type` list marks each value as an organisation kind or a person kind);
  - a person's account, whatever qualifier rule 1 classes it (individual, creator or public figure), that is verified, or whose follower count is at or above the threshold the user sets.
- Clients may list, filter, rank and save public accounts, and use a saved list as a segment.
- The follower threshold is a setting the user sets before the first client-facing lane that shows author lists (`DEFERRED.md`). It is a row of `feature_flags` (ADR-0050), the table that already holds the `X_PLAN` setting, changed only through the audited admin API. Until it is set, the follower test admits no account; verified accounts, registered sources and organisation kinds are public already.
- One SDK function applies the test, extending the individuals rule of ADR-0032: it marks each resolved account `public_account` true or false, false for the kinds a platform's terms forbid listing (below). A public person's answer on `poster.profiles` carries the identity fields an organisation's carries (handle, display name, URL, followers, verified flag); an ordinary individual's answer stays minimised as ADR-0033 says, and only an ordinary individual's id is redacted from the archive.
- Where the identity of a public account lives: a registered source's in `sources`; any other public account's in its `poster_profiles` row (ADR-0045), marked `public_account`. That row stays after the 30-day cache window, which only decides when a repeat hit is resolved again; re-resolution refreshes it. No row about an ordinary person holds a handle, name or URL.
- Items keep every author as `author_ref`, plus `author_source_id` for a registered source; no item row holds a public person's handle. An author is listed only through a public-account record joined on `author_ref`: F8 adds `public_accounts_dim` (`author_ref`, `platform`, kind, `source_id`, handle, display name, followers, verified flag), filled from `sources` and the public rows of `poster_profiles`, less the kinds a platform's terms forbid listing (below), and an `author_ref` that is not in it is never listed, ranked or exported.
- A client's saved lists of public accounts sit beside its seed and watch lists, as `client_lists` entries of a third type, `saved` (ADR-0043), keyed by the account's candidate key or `source_id`.
- Deletions reach these records: `poster_profiles`, `public_accounts_dim` and `client_lists` are in the SDK purge registry, so an author-scope deletion, from an author's request or an X compliance result, removes the account's rows (ADR-0035, ADR-0069), and x-compliance-sync submits every X user id `poster_profiles` holds, as it submits `sources.platform_id` (ADR-0039), and carries it in the deletion target's `user_ids`, so raw-archiver's rewrite also reaches the account's archived `profile` records (ADR-0035, ADR-0032).
- D3 specifies the lists, filters, rankings, saved lists and segments in the query API, client portal and dashboard.

**Platforms whose terms forbid listing a kind of account**

Where a platform's terms forbid listing a kind of account even when it is public, that platform lists organisations and pages only:

- TikTok: "Developer Terms forbid building profiles or databases on any individual" (CONVENTIONS v1 L178). No TikTok person's account is listed, ranked or saved, creators included, registered or verified; TikTok lists organisation accounts only.
- LinkedIn members: "member social-activity data stored at most 48 hours; most member profile data 24 hours; ... member data cannot be exported to customers" (L192; also L90). No member is listed; LinkedIn lists company pages only.
- Instagram: Public Content Access allows analytics "only as aggregated, de-identified output" (L171), and hashtag media of accounts the app does not manage carry no username (L166). No Instagram person's account is listed, creator accounts included; Instagram lists business accounts only. Counsel confirms before the first author-list lane whether creator accounts read through Business Discovery may be listed (`DEFERRED.md`).

Other platforms' terms limit lists and segments without forbidding a kind of public account:

- YouTube forbids aggregation across channels of different owners except under the carve-out (L209): a segment built from a saved list never sums YouTube figures across owners outside the carve-out (ADR-0056).
- X forbids profiling on sensitive attributes and monitoring sensitive events (L188): no list or segment is built or filtered on a sensitive attribute, and ADR-0069's screen of X terms applies.
- Facebook personal profiles are individuals under rule 1 and no resolver reads them, so Facebook lists Pages and groups.

**Ordinary people in client views**

- Ordinary people appear only in anonymous segments: counts in the aggregates by their dimensions (ADR-0048): language, dialect, route, kind, sentiment, topic, and region or governorate where known, which is the governorate analysis-entities resolves from the places an item names. Distinct-author counts are allowed; no client view, export or query lists or ranks an `author_ref` that is not a public account.
- Individuals are never backfilled: a person's account is a source only when rule 1 and the qualifier make it one, and only sources are backfilled (ADR-0020). Being a public account does not make a person a source.

Why: The user wants clients to list, filter and rank the accounts behind a conversation and to reuse those lists as segments; public accounts are the ones whose owners speak in public and whose platforms allow it. Ordinary people keep option 1's protection, which extends what most PRDs and README decision 8 already do, so the archive and the pipeline treat people alike and one reference keeps deletion by author workable.

## Consequences

- The user's non-negotiable in `CLAUDE.md` (L10) is reworded in this pull request, citing this ADR: "Private individuals are never profiled, listed or backfilled: every author is a keyed reference (`author_ref`). Public accounts as defined in ADR-0010 (registered sources, organisations, pages, channels and media, and verified or widely followed accounts, where the platform's terms allow) may be listed and ranked."
- The review check follows it, citing this ADR: in `.claude/skills/review-session/SKILL.md` L25, "private individuals keyed (`author_ref`), never profiled, listed or backfilled, and only public accounts listed (ADR-0010)" replaces "individuals hashed".
- CONVENTIONS v1.1: `raw.items` is "as returned, minus identities"; the compliance section carries the function and its name, edge minimisation, archive redaction, the bus bound, the public-account rule and the platform exceptions; qualifier rule 7 points here; the schema-change rule gains the exception for tt-video-stats-refresher's parked readings. README decision 8's first clause is generalised (with ADR-0070's README edits).
- F2: the `author_ref` function and its golden vectors; `public_account` and a public person's identity fields on `poster.profiles/v1` (ADR-0033); the `account_type` list marked organisation or person.
- F3: `public_account` on `poster_profiles`; the follower-threshold row in `feature_flags`; the `saved` type in `client_lists`. F8: `public_accounts_dim` and the `author_ref` columns of ADR-0047.
- F4 and F6: the registry-cache lookup and the individuals-rule function with the public test.
- D3: the client-facing lists, rankings, saved lists and segments, and the anonymous segment views.
- `DEFERRED.md`: the follower threshold (the user, before the first client-facing lane that shows author lists); counsel on Instagram creator accounts (before that lane).

Sessions that must read this: F2 (the helper and its golden vectors), F3 (`poster_profiles`, the threshold, `client_lists`), F8 (`author_ref`, `public_accounts_dim`), F4, F6, C2, C4, C6, C7, C8, C9, C13, C14, C15, X7, D3, Q1, U2, U3, and every fetcher that writes people's ids: VTT3, VTT5, VTT6, X6, YT5, YT6, FB7, VFB1, VFB2, VFB3, VIG1, VIG2, IG4, IG5, IG6, LI2, LI3, VLI4, TG2, N6, N8.
