# YT0 · YouTube probe

Wave 4 · YouTube, X, and Facebook in development mode · track YouTube · size S (one sitting) · kind probe

## Builds

Recorded Data API and PubSubHubbub responses, with quota costs observed.

## Needs first (merged, with a closed review)

- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`

Any-time track: earliest after F1; deadline before YT1.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Quotas, budgets and the quota governor; Security and compliance in every service; Per-platform fact sheets: YouTube
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of F1: `docs/handoffs/F1.md`
5. The API key
6. 10 Iraqi channels you will watch

## Hands on

- `docs/handoffs/YT0.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/YT0.md` from the fresh-session review
- `docs/probes/youtube.md`
- Scrubbed fixtures in `fixtures/youtube/`
- The probe script and its scrubbing test in `tools/probes/youtube/`

## Watch for

- Cap: at most 2,000 quota units, of which at most 10 search.list calls
- Scrub before anything is committed: tokens, signed URLs, private individuals' names, handles, ids and avatars

## Done when

- Every PRD assumption in sections 5.3 and 7 is marked confirmed, different or not tested, with evidence.
- Fixtures are scrubbed, documented in their README and committed; the scrubbing test passes; `raw/` is deleted.
- Spend stayed under the cap (at most 2,000 quota units, of which at most 10 search.list calls).
- Each difference is listed as a question for its PRD.

## Runs alongside

Any session (any-time track)

## How to run it

- Start: `claude --worktree YT0 --permission-mode default` (Manual mode: you approve every real call; credentials only in `.env`)
- Run: `/probe-platform youtube at most 2,000 quota units, of which at most 10 search.list calls`
- Review: a fresh session (`claude --worktree YT0`) checks the scrubbing test and the report against the brief; then merge
