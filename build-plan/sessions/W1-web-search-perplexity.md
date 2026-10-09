# W1 · web-search-perplexity

Wave 3 · First real data, and the Meta review build · track Web · size M (1 to 2 days with review) · kind service

## Builds

Keyword searches on rotation through the Perplexity Search API.

Service `web-search-perplexity` · PRD `docs/prds/web/web-search-perplexity.md` · lane Discover and qualify · route green · 10 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- F5 SDK scheduling, quota client, adapter kit, fake platform: `docs/handoffs/F5.md`
- C1 quota-governor: `docs/handoffs/C1.md`
- W0 Web search probe: `docs/handoffs/W0.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/web/web-search-perplexity.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: Web search
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of F5: `docs/handoffs/F5.md`
6. Handoff of C1: `docs/handoffs/C1.md`
7. Handoff of W0: `docs/handoffs/W0.md`
8. The W0 probe report `docs/probes/web.md` and the fixtures in `fixtures/web/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`, `search.results`
- Job queues in: `jobs.web-search-perplexity`; out: none
- Tables read: `sources`, `keywords`, `clients`, `cursors`, `budgets`, `vendor_keys`, `canary_targets`, `service_runs`; written or updated: `sources`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/web-search-perplexity/`
- `docs/handoffs/W1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/W1.md` from the fresh-session review

## Watch for

- Budget perplexity_search; up to 5 queries per request
- Search output rule: items to raw.items with source_id = the keyword rule
- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

W2

## How to run it

- Plan: `claude --worktree W1 --permission-mode plan`, then `/plan-session W1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session W1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree W1`, then `/review-session W1`
- Fix: `claude --worktree W1` (or the build terminal), `/fix-session W1`; then a fresh session runs `/review-session W1 recheck`; merge when the review has no open blocker or should-fix
