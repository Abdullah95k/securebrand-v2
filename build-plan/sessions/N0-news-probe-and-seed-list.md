# N0 · News probe and seed list

Wave 3 · First real data, and the Meta review build · track News · size M (1 to 2 days with review) · kind probe

## Builds

Per-site capability report and recorded fixtures for 20 to 30 Iraqi outlets.

## Needs first (merged, with a closed review)

- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`

Any-time track: earliest after F1; deadline before N1.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Quotas, budgets and the quota governor; Security and compliance in every service; Per-platform fact sheets: News websites
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of F1: `docs/handoffs/F1.md`
5. Your list of news websites
6. News PRDs section 5.3

## Hands on

- `docs/handoffs/N0.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/N0.md` from the fresh-session review
- `docs/probes/news.md`
- Scrubbed fixtures in `fixtures/news/`
- The probe script and its scrubbing test in `tools/probes/news/`

## Watch for

- Obey robots.txt, Content Signals, RSL and 402 in the probe too
- One connection per host, 2 to 5 s apart
- Cap: at most 10 requests per site; one connection per host, 2 to 5 s apart
- Scrub before anything is committed: tokens, signed URLs, private individuals' names, handles, ids and avatars

## Done when

- Every PRD assumption in sections 5.3 and 7 is marked confirmed, different or not tested, with evidence.
- Fixtures are scrubbed, documented in their README and committed; the scrubbing test passes; `raw/` is deleted.
- Spend stayed under the cap (at most 10 requests per site; one connection per host, 2 to 5 s apart).
- Each difference is listed as a question for its PRD.

## Runs alongside

Any session (any-time track)

## Your part

You supply the website list.

## How to run it

- Start: `claude --worktree N0 --permission-mode default` (Manual mode: you approve every real call; credentials only in `.env`)
- Run: `/probe-platform news at most 10 requests per site; one connection per host, 2 to 5 s apart`
- Review: a fresh session (`claude --worktree N0`) checks the scrubbing test and the report against the brief; then merge
