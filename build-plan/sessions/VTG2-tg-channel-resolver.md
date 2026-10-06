# VTG2 · tg-channel-resolver

Wave 7 · Amber vendor routes (optional) · track Amber · size M (1 to 2 days with review) · kind service

## Builds

Channel resolution and stats.

Service `tg-channel-resolver` · PRD `docs/prds/telegram/tg-channel-resolver.md` · lane Discover and qualify · route amber · 11 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- VTG0 Telegram vendor probe: `docs/handoffs/VTG0.md`
- C8 poster-resolver: `docs/handoffs/C8.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/telegram/tg-channel-resolver.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: Telegram
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of VTG0: `docs/handoffs/VTG0.md`
6. Handoff of C8: `docs/handoffs/C8.md`
7. The VTG0 probe report `docs/probes/tg-vendor.md` and the fixtures in `fixtures/telegram-vendor/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `items.normalized`, `poster.profiles`
- Topics written: `raw.items`, `poster.profiles`
- Job queues in: `jobs.tg-channel-resolver`; out: none
- Tables read: `sources`, `clients`, `client_sources`, `cursors`, `budgets`, `decisions`, `vendor_keys`; written or updated: `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/tg-channel-resolver/`
- `docs/handoffs/VTG2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/VTG2.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Individuals are never profiled: a mention keeps a hashed author reference
- Amber: runs only behind its flag (off by default); provenance says route = amber and names the vendor; its data is excluded from government contracts, and a source a government client watches never falls back to it; the quota governor stretches it from 80% of budget

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree VTG2 --permission-mode plan`, then `/plan-session VTG2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session VTG2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree VTG2`, then `/review-session VTG2`
- Fix: `claude --worktree VTG2` (or the build terminal), `/fix-session VTG2`; then a fresh session runs `/review-session VTG2 recheck`; merge when the review has no open blocker or should-fix
