# LI0 · LinkedIn probe (Development tier)

Wave 5 · Approval-gated platforms and the client portal · track LinkedIn · size S (one sitting) · kind probe

## Builds

Recorded Community Management API responses on your own test Page.

## Needs first (merged, with a closed review)

- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`

Any-time track: earliest after F1 and Development tier approval; deadline before LI1.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Quotas, budgets and the quota governor; Security and compliance in every service; Per-platform fact sheets: LinkedIn
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of F1: `docs/handoffs/F1.md`
5. Development tier approval
6. Your test Page with you as super admin

## Hands on

- `docs/handoffs/LI0.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/LI0.md` from the fresh-session review
- `docs/probes/linkedin.md`
- Scrubbed fixtures in `fixtures/linkedin/`
- The probe script and its scrubbing test in `tools/probes/linkedin/`

## Watch for

- Cap: at most 200 calls, on your own test Page only
- Scrub before anything is committed: tokens, signed URLs, private individuals' names, handles, ids and avatars

## Done when

- Every PRD assumption in sections 5.3 and 7 is marked confirmed, different or not tested, with evidence.
- Fixtures are scrubbed, documented in their README and committed; the scrubbing test passes; `raw/` is deleted.
- Spend stayed under the cap (at most 200 calls, on your own test Page only).
- Each difference is listed as a question for its PRD.

## Runs alongside

Any session (any-time track)

## How to run it

- Start: `claude --worktree LI0 --permission-mode default` (Manual mode: you approve every real call; credentials only in `.env`)
- Run: `/probe-platform linkedin at most 200 calls, on your own test Page only`
- Review: a fresh session (`claude --worktree LI0`) checks the scrubbing test and the report against the brief; then merge
