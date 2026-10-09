# ADR-0061 · Disqus series

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: comment-decay-scheduler, news-comments-fetcher, news-site-resolver
Source: D2-Q061 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

Four documents give Disqus sites the short series +6 h, +24 h, +3 d (`CONVENTIONS L269`, `comment-decay-scheduler §5.1 L58`, `news-comments-fetcher §5.1 L43`, `news-article-extractor §5.1 L47`); news-site-resolver, an approved PRD, promises the full decay series (+1 h, +6 h, +24 h, +3 d, +7 d, then weekly to day 30) when it onboards a site (`news-site-resolver §5.1 L41`). AU-041 and AU-107 put the same question from the two audit passes.

Settles: CF-108, AU-041, AU-107.

## Options

1. **The short series, as CONVENTIONS, the scheduler and the fetcher say; news-site-resolver's sentence corrected** (chosen): its rules are under Decision.
2. **The full decay series for Disqus.** Consequences: CONVENTIONS, the scheduler profile and news-comments-fetcher change, and `news_disqus` is re-estimated for five more steps per article on every thread, steps the extension rule already adds where a thread is still growing.

## Decision

Disqus threads keep the short series, +6 h, +24 h and +3 d, as CONVENTIONS, the scheduler and the fetcher already say; news-site-resolver's onboarding sentence is corrected.

Disqus threads get +6 h, +24 h and +3 d, threaded in the same call (`CONVENTIONS L269`). The general rules still apply on this row: the extension rule (CONVENTIONS L271) extends a thread that still adds 20% or more at its last scheduled fetch, +3 d, every 2 days to day 30, so a thread that keeps growing is followed; early stop is armed as ADR-0019 says. news-site-resolver promises the short series when it onboards a Disqus site.

Why: Three of the four documents, including the two PRDs that own the code, agree; the extension rule already gives growing threads the later steps, so the full series would spend Disqus calls on every thread to catch what extension already catches on the threads that need it.

## Consequences

No change to the `news_disqus` budget estimate; the scheduler profile stays as written; an approved PRD gets a one-line edit under ADR-0001.

- No CONVENTIONS change: v1 L269 and L271 stand.
- `news-site-resolver §5.1 L41` is corrected in this pull request, citing this ADR.

Sessions that must read this: C11, N2, N8.
