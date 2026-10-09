# VFB1 · fb-keyword-search

Wave 7 · Amber vendor routes (optional) · track Amber · size M (1 to 2 days with review) · kind service

## Builds

Vendor keyword search of Facebook posts.

Service `fb-keyword-search` · PRD `docs/prds/facebook/fb-keyword-search.md` · lane Discover and qualify · route amber · 11 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- VFB0 Facebook vendor probe: `docs/handoffs/VFB0.md`
- C5 keyword-matcher: `docs/handoffs/C5.md`
- C8 poster-resolver: `docs/handoffs/C8.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/facebook/fb-keyword-search.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: Facebook
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of VFB0: `docs/handoffs/VFB0.md`
6. Handoff of C5: `docs/handoffs/C5.md`
7. Handoff of C8: `docs/handoffs/C8.md`
8. The VFB0 probe report `docs/probes/fb-vendor.md` and the fixtures in `fixtures/facebook-vendor/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `item.hits`, `discovery.hits`
- Job queues in: `jobs.fb-keyword-search`; out: none
- Tables read: `sources`, `keywords`, `clients`, `cursors`, `budgets`, `vendor_keys`, `canary_targets`; written or updated: `sources`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/fb-keyword-search/`
- `docs/handoffs/VFB1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/VFB1.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed
- Amber: runs only behind its flag (off by default); provenance says route = amber and names the vendor; only clients that accept amber receive its data, never government clients (ADR-0052), and a source a government client watches or a client-owned property never falls back to it (ADR-0021); from 80% of budget the SDK scheduling kit stretches its intervals by the governor's factor (ADR-0057)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree VFB1 --permission-mode plan`, then `/plan-session VFB1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session VFB1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree VFB1`, then `/review-session VFB1`
- Fix: `claude --worktree VFB1` (or the build terminal), `/fix-session VFB1`; then a fresh session runs `/review-session VFB1 recheck`; merge when the review has no open blocker or should-fix
