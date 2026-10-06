# VLI2 · li-org-resolver

Wave 7 · Amber vendor routes (optional) · track Amber · size M (1 to 2 days with review) · kind service

## Builds

Company page resolution.

Service `li-org-resolver` · PRD `docs/prds/linkedin/li-org-resolver.md` · lane Discover and qualify · route amber · 11 acceptance criteria (section 13) · 3 open questions (section 14)

## Needs first (merged, with a closed review)

- VLI0 LinkedIn vendor probe: `docs/handoffs/VLI0.md`
- C8 poster-resolver: `docs/handoffs/C8.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/linkedin/li-org-resolver.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: LinkedIn
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of VLI0: `docs/handoffs/VLI0.md`
6. Handoff of C8: `docs/handoffs/C8.md`
7. The VLI0 probe report `docs/probes/li-vendor.md` and the fixtures in `fixtures/linkedin-vendor/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `raw.items`, `poster.profiles`
- Job queues in: `jobs.li-org-resolver`; out: none
- Tables read: `sources`, `clients`, `client_sources`, `budgets`, `decisions`, `vendor_keys`, `service_runs`; written or updated: `budgets`, `decisions`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/li-org-resolver/`
- `docs/handoffs/VLI2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/VLI2.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Individuals are never profiled: a mention keeps a hashed author reference
- Amber: runs only behind its flag (off by default); provenance says route = amber and names the vendor; its data is excluded from government contracts, and a source a government client watches never falls back to it; the quota governor stretches it from 80% of budget

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree VLI2 --permission-mode plan`, then `/plan-session VLI2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session VLI2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree VLI2`, then `/review-session VLI2`
- Fix: `claude --worktree VLI2` (or the build terminal), `/fix-session VLI2`; then a fresh session runs `/review-session VLI2 recheck`; merge when the review has no open blocker or should-fix
