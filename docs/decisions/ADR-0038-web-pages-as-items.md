# ADR-0038 · Web pages as items

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, search-hit-router, normalize-item, keyword-matcher, and web: web-search-perplexity, web-search-mojeek, web-gdelt-poller
Source: D2-Q038 (user decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

Web search (Perplexity, Mojeek, GDELT) returns links: social posts, news articles, and other pages such as blogs, forum threads, and company or public bodies' pages. The documents disagree on what happens to that last kind. CONVENTIONS says a search service writes every item it finds into the pipeline, so that it can become a mention (L281), and normalize-item, an approved PRD, already turns a Perplexity or Mojeek result into an item with its title, snippet and date (`normalize-item §5.3 L73`). The web PRDs, though, only archive the engines' responses and send the results to search-hit-router (`web-search-perplexity §5.2 L55`), which turns social links into candidate sources and news links into articles to fetch, and counts everything else as `web` with nothing emitted (`search-hit-router §5.2 L63`). As written, a client never sees a blog or forum page that names its brand, and normalize-item's web mapper has no input. Their share of results is to be measured in the pilot (`search-hit-router §2 L17`).

The choice is wider coverage of the open web against more low-value mentions and a new kind of item in client views. Social posts and news articles found by search are handled alike under every option.

Settles: CF-110.
Depends on: ADR-0008 (the `result` kind), ADR-0037 (the results path), ADR-0054 (the retention class of web results).

## Options

1. **Other web pages become mentions, only where nothing else covers them** (chosen): its rules are under Decision.
2. **Routing only: web results never become mentions themselves.** The web PRDs as written: search finds social sources and news articles, other pages are counted and dropped, and normalize-item's web mapper is removed (an approved PRD moves under ADR-0001). Consequences: the least work and no web noise for clients, but a brand named only on a blog, forum or company page is never shown; CONVENTIONS L281 is reworded for web search.
3. **Every result becomes a mention, as CONVENTIONS reads.** Each engine writes every result as a web item, besides routing it. Consequences: the widest coverage, but a news article or social post found by search also appears as a web snippet, so twice unless a de-duplication rule is added, and item volume grows with every result.

## Decision

Other web pages become mentions, only where nothing else covers them: for a Perplexity or Mojeek result that search-hit-router cannot route to a platform or to the news extractor, the router writes a `web` item that reaches clients like any mention.

Results still go to search-hit-router; for a Perplexity or Mojeek result it cannot route to a platform or to the news extractor, the router writes a `web:result:<canonical_url_hash>` item (kind `result`, ADR-0008) to `raw.items` with the keyword rule's `source_id`: title, snippet, URL and engine, under `news_excerpt` (ADR-0054), mapped by normalize-item's existing web mapper (`normalize-item §5.3 L73`). keyword-matcher confirms the keyword in the title or snippet before it counts, and raises no candidate for the domain, which the router has already judged. GDELT's unrouted results stay counted only, as no mapper covers them.

Why: It shows clients the open-web mentions only search can find, reuses the mapper an approved PRD already has, and never shows a page twice. The terms allow it: Perplexity's customer owns the output, so results "are stored, normalised and shown to clients" (`web-search-perplexity §7 L119`), and Mojeek's results may be stored (CONVENTIONS L95).

## Consequences

Clients see blog, forum and site mentions under the platform `web`; no page appears twice, since links that become posts or articles are never written as web items; storage is a title and a snippet per page; CONVENTIONS L281 names the router as a `raw.items` writer for these results; noise is handled by the client's keywords and exclusions, as for any mention.

- CONVENTIONS v1.1: the `search.results` line (v1 L26) and the search output rule (v1 L281): web results become items only through search-hit-router, for the results it cannot route.
- F2 types the `result` kind (ADR-0008); normalize-item keeps its web mapper (`normalize-item §5.3 L73`); the class is `news_excerpt` as ADR-0054 words it.

Sessions that must read this: F2, C4, C5, YT9, W1, W2, W3, W4.
