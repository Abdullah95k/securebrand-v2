# X0 · X probe

Wave 4 · YouTube, X, and Facebook in development mode · track X · size S (one sitting) · kind probe

## Builds

Recorded responses for every X call shape, with a spending cap.

## Needs first (merged, with a closed review)

- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`

Any-time track: earliest after F1; deadline before X1.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Quotas, budgets and the quota governor; Security and compliance in every service; Per-platform fact sheets: X
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of F1: `docs/handoffs/F1.md`
5. X developer app on pay-per-use, with a spending cap
6. 20 Iraqi accounts and 10 keywords

## Hands on

- `docs/handoffs/X0.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/X0.md` from the fresh-session review
- `docs/probes/x.md`
- Scrubbed fixtures in `fixtures/x/`
- The probe script and its scrubbing test in `tools/probes/x/`

## Watch for

- Every read costs money: cap the probe
- Cap: at most 2,000 post reads and 200 user reads (about USD 12 at list price)
- Scrub before anything is committed: tokens, signed URLs, private individuals' names, handles, ids and avatars

## Done when

- Every PRD assumption in sections 5.3 and 7 is marked confirmed, different or not tested, with evidence.
- Fixtures are scrubbed, documented in their README and committed; the scrubbing test passes; `raw/` is deleted.
- Spend stayed under the cap (at most 2,000 post reads and 200 user reads (about USD 12 at list price)).
- Each difference is listed as a question for its PRD.

## Runs alongside

Any session (any-time track)

## How to run it

- Start: `claude --worktree X0 --permission-mode default` (Manual mode: you approve every real call; credentials only in `.env`)
- Run: `/probe-platform x at most 2,000 post reads and 200 user reads (about USD 12 at list price)`
- Review: a fresh session (`claude --worktree X0`) checks the scrubbing test and the report against the brief; then merge
