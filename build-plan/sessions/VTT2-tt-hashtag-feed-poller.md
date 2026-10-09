# VTT2 · tt-hashtag-feed-poller

Wave 7 · Amber vendor routes (optional) · track Amber · size M (1 to 2 days with review) · kind service

## Builds

Vendor hashtag feeds on rotation.

Service `tt-hashtag-feed-poller` · PRD `docs/prds/tiktok/tt-hashtag-feed-poller.md` · lane Discover and qualify · route amber · 11 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- VTT0 TikTok vendor probe: `docs/handoffs/VTT0.md`

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/tiktok/tt-hashtag-feed-poller.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: TikTok
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of VTT0: `docs/handoffs/VTT0.md`
6. The VTT0 probe report `docs/probes/tt-vendor.md` and the fixtures in `fixtures/tiktok-vendor/`
7. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `raw.items`
- Topics written: `raw.items`
- Job queues in: `jobs.tt-hashtag-feed-poller`; out: none
- Tables read: `sources`, `clients`, `cursors`, `budgets`, `vendor_keys`, `canary_targets`; written or updated: `sources`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/tt-hashtag-feed-poller/`
- `docs/handoffs/VTT2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/VTT2.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed
- Amber: runs only behind its flag (off by default); provenance says route = amber and names the vendor; only clients that accept amber receive its data, never government clients (ADR-0052), and a source a government client watches or a client-owned property never falls back to it (ADR-0021); from 80% of budget the SDK scheduling kit stretches its intervals by the governor's factor (ADR-0057)

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree VTT2 --permission-mode plan`, then `/plan-session VTT2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session VTT2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree VTT2`, then `/review-session VTT2`
- Fix: `claude --worktree VTT2` (or the build terminal), `/fix-session VTT2`; then a fresh session runs `/review-session VTT2 recheck`; merge when the review has no open blocker or should-fix
