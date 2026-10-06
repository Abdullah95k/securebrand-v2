# FB0 · Meta probe (development mode)

Wave 3 · First real data, and the Meta review build · track Facebook · size M (1 to 2 days with review) · kind probe · on the critical path

## Builds

Recorded Graph API responses for every Facebook and Instagram call shape the PRDs use.

## Needs first (merged, with a closed review)

- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`

Any-time track: earliest after F1 and the Meta app exist; deadline before FB1.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Quotas, budgets and the quota governor; Security and compliance in every service; Per-platform fact sheets: Facebook and Instagram
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of F1: `docs/handoffs/F1.md`
5. The Meta app (Business Verification under way)
6. Team test Pages and Instagram professional accounts with roles on the app
7. FB and IG PRDs section 5.3

## Hands on

- `docs/handoffs/FB0.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/FB0.md` from the fresh-session review
- `docs/probes/meta.md`
- Scrubbed fixtures in `fixtures/facebook/`
- Scrubbed fixtures in `fixtures/instagram/`
- The probe script and its scrubbing test in `tools/probes/meta/`

## Watch for

- Unapproved features work only for people with a role on the app
- Record /feed pagination at limit=100, comments with filter=stream (no ids), reactions summaries, Pages Search, Business Discovery, webhook payloads
- Scrub commenter names and ids before saving
- Cap: at most 300 Graph API calls, development mode, team accounts and test Pages only
- Scrub before anything is committed: tokens, signed URLs, private individuals' names, handles, ids and avatars

## Done when

- Every PRD assumption in sections 5.3 and 7 is marked confirmed, different or not tested, with evidence.
- Fixtures are scrubbed, documented in their README and committed; the scrubbing test passes; `raw/` is deleted.
- Spend stayed under the cap (at most 300 Graph API calls, development mode, team accounts and test Pages only).
- Each difference is listed as a question for its PRD.

## Runs alongside

Any session (any-time track)

## How to run it

- Start: `claude --worktree FB0 --permission-mode default` (Manual mode: you approve every real call; credentials only in `.env`)
- Run: `/probe-platform meta at most 300 Graph API calls, development mode, team accounts and test Pages only`
- Review: a fresh session (`claude --worktree FB0`) checks the scrubbing test and the report against the brief; then merge
