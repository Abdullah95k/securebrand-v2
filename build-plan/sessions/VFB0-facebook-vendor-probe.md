# VFB0 · Facebook vendor probe

Wave 7 · Amber vendor routes (optional) · track Amber · size S (one sitting) · kind probe

## Builds

Recorded vendor responses (SociaVault or ScrapeCreators) and billing behaviour.

## Needs first (merged, with a closed review)

- F5 SDK scheduling, quota client, adapter kit, fake platform: `docs/handoffs/F5.md`
- G2 Gate: staging with real data: `docs/gates/G2.md` is green

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Quotas, budgets and the quota governor; Security and compliance in every service; Per-platform fact sheets: Facebook
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of F5: `docs/handoffs/F5.md`
5. Signed vendor contract
6. FB_VENDOR_ROUTE value

## Hands on

- `docs/handoffs/VFB0.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/VFB0.md` from the fresh-session review
- `docs/probes/fb-vendor.md`
- Scrubbed fixtures in `fixtures/facebook-vendor/`
- The probe script and its scrubbing test in `tools/probes/fb-vendor/`

## Watch for

- Cap: at most USD 5
- Scrub before anything is committed: tokens, signed URLs, private individuals' names, handles, ids and avatars

## Done when

- Every PRD assumption in sections 5.3 and 7 is marked confirmed, different or not tested, with evidence.
- Fixtures are scrubbed, documented in their README and committed; the scrubbing test passes; `raw/` is deleted.
- Spend stayed under the cap (at most USD 5).
- Each difference is listed as a question for its PRD.

## Runs alongside

Any session (any-time track)

## How to run it

- Start: `claude --worktree VFB0 --permission-mode default` (Manual mode: you approve every real call; credentials only in `.env`)
- Run: `/probe-platform fb-vendor at most USD 5`
- Review: a fresh session (`claude --worktree VFB0`) checks the scrubbing test and the report against the brief; then merge
