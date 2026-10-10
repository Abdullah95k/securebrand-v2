# D3 · Specs for the parts with no PRD

Wave 0 · Decide and freeze · track Decide · size M (1 to 2 days with review) · kind spec

## Builds

PRDs in the same 14-section template for the query API, client portal (onboarding, OAuth connect, keywords and sources, review queue, provenance, deletion requests), dashboard (with the Meta App Review slice) and admin console, with the n8n flows (one per channel and per card type, ADR-0067).

## Needs first (merged, with a closed review)

- D2 Decisions and contract freeze: `docs/handoffs/D2.md`

Any-time track: earliest after D2; deadline before Q1 (Wave 3).

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: the whole file
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of D2: `docs/handoffs/D2.md`
5. The review requirements of Meta, LinkedIn and TikTok (the approvals table in `build-plan/README.md`)
6. The 86 PRDs' section 4 (who consumes what)

## Hands on

- `docs/handoffs/D3.md` from `build-plan/templates/HANDOFF.md`
- `docs/prds/apps/query-api.md`
- `docs/prds/apps/client-portal.md`
- `docs/prds/apps/dashboard.md`
- `docs/prds/apps/admin-console.md`

## Watch for

- The App Review slice must show analytics on named Pages; a raw data pipeline or a 'monitoring' framing fails review
- The admin console's register screen shows every `permitted_uses` row for the user's review and writes each change audited; a use with no row is allowed (ADR-0068)

## Done when

- Each PRD follows the 14-section template with testable acceptance criteria, and is consistent with every PRD that names it in section 4.

## Runs alongside

Any session (any-time track)

## Your part

You, interview mode.

## How to run it

- Start: `claude --worktree D3` (it writes documents, so not plan mode)
- Run: `/decide-session D3`
- Review: read every file it produced yourself before merging, then ask a fresh session to check them against the PRDs
