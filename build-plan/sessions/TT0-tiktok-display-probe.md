# TT0 · TikTok Display probe (sandbox)

Wave 5 · Approval-gated platforms and the client portal · track TikTok · size S (one sitting) · kind probe

## Builds

Recorded Display API responses from sandbox accounts.

## Needs first (merged, with a closed review)

- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`

Any-time track: earliest after F1; deadline before TT1.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Quotas, budgets and the quota governor; Security and compliance in every service; Per-platform fact sheets: TikTok
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of F1: `docs/handoffs/F1.md`
5. TikTok developer app with a sandbox

## Hands on

- `docs/handoffs/TT0.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/TT0.md` from the fresh-session review
- `docs/probes/tiktok.md`
- Scrubbed fixtures in `fixtures/tiktok/`
- The probe script and its scrubbing test in `tools/probes/tiktok/`

## Watch for

- Cap: at most 100 calls, sandbox accounts only
- Scrub before anything is committed: tokens, signed URLs, private individuals' names, handles, ids and avatars

## Done when

- Every PRD assumption in sections 5.3 and 7 is marked confirmed, different or not tested, with evidence.
- Fixtures are scrubbed, documented in their README and committed; the scrubbing test passes; `raw/` is deleted.
- Spend stayed under the cap (at most 100 calls, sandbox accounts only).
- Each difference is listed as a question for its PRD.

## Runs alongside

Any session (any-time track)

## How to run it

- Start: `claude --worktree TT0 --permission-mode default` (Manual mode: you approve every real call; credentials only in `.env`)
- Run: `/probe-platform tiktok at most 100 calls, sandbox accounts only`
- Review: a fresh session (`claude --worktree TT0`) checks the scrubbing test and the report against the brief; then merge
