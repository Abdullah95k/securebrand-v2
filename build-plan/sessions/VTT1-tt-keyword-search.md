# VTT1 · tt-keyword-search

Wave 7 · Amber vendor routes (optional) · track Amber · size M (1 to 2 days with review) · kind service

## Builds

Vendor keyword search on TikTok.

Service `tt-keyword-search` · PRD `docs/prds/tiktok/tt-keyword-search.md` · lane Discover and qualify · route amber · 10 acceptance criteria (section 13) · 3 open questions (section 14)

## Needs first (merged, with a closed review)

- VTT0 TikTok vendor probe: `docs/handoffs/VTT0.md`
- C5 keyword-matcher: `docs/handoffs/C5.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/tiktok/tt-keyword-search.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: TikTok
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of VTT0: `docs/handoffs/VTT0.md`
6. Handoff of C5: `docs/handoffs/C5.md`
7. The VTT0 probe report `docs/probes/tt-vendor.md` and the fixtures in `fixtures/tiktok-vendor/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`
- Job queues in: `jobs.tt-keyword-search`; out: none
- Tables read: `sources`, `keywords`, `clients`, `cursors`, `budgets`, `vendor_keys`, `canary_targets`; written or updated: `sources`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/tt-keyword-search/`
- `docs/handoffs/VTT1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/VTT1.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Individuals are never profiled: a mention keeps a hashed author reference
- Amber: runs only behind its flag (off by default); provenance says route = amber and names the vendor; its data is excluded from government contracts, and a source a government client watches never falls back to it; the quota governor stretches it from 80% of budget

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree VTT1 --permission-mode plan`, then `/plan-session VTT1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session VTT1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree VTT1`, then `/review-session VTT1`
- Fix: `claude --worktree VTT1` (or the build terminal), `/fix-session VTT1`; then a fresh session runs `/review-session VTT1 recheck`; merge when the review has no open blocker or should-fix
