# IG2 · ig-hashtag-search

Wave 5 · Approval-gated platforms and the client portal · track Instagram · size M (1 to 2 days with review) · kind service

## Builds

Hashtag search within the 30-per-7-days ledger.

Service `ig-hashtag-search` · PRD `docs/prds/instagram/ig-hashtag-search.md` · lane Discover and qualify · route green · 10 acceptance criteria (section 13) · 0 open questions (section 14)

## Needs first (merged, with a closed review)

- FB0 Meta probe (development mode): `docs/handoffs/FB0.md`
- C1 quota-governor: `docs/handoffs/C1.md`
- C8 poster-resolver: `docs/handoffs/C8.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/instagram/ig-hashtag-search.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: Instagram
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of FB0: `docs/handoffs/FB0.md`
6. Handoff of C1: `docs/handoffs/C1.md`
7. Handoff of C8: `docs/handoffs/C8.md`
8. The FB0 probe report `docs/probes/meta.md` and the fixtures in `fixtures/instagram/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`, `discovery.hits`, `source.events`
- Job queues in: `jobs.ig-hashtag-search`; out: none
- Tables read: `sources`, `clients`, `client_sources`, `cursors`, `budgets`; written or updated: `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/ig-hashtag-search/`
- `docs/handoffs/IG2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/IG2.md` from the fresh-session review

## Watch for

- 30 unique hashtags per Instagram business account per 7 days
- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

IG1, IG3

## How to run it

- Plan: `claude --worktree IG2 --permission-mode plan`, then `/plan-session IG2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session IG2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree IG2`, then `/review-session IG2`
- Fix: `claude --worktree IG2` (or the build terminal), `/fix-session IG2`; then a fresh session runs `/review-session IG2 recheck`; merge when the review has no open blocker or should-fix
