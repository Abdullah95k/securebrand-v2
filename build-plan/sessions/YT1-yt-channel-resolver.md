# YT1 · yt-channel-resolver

Wave 4 · YouTube, X, and Facebook in development mode · track YouTube · size M (1 to 2 days with review) · kind service

## Builds

Resolves channel candidates and handles into channel ids.

Service `yt-channel-resolver` · PRD `docs/prds/youtube/yt-channel-resolver.md` · lane Discover and qualify · route green · 12 acceptance criteria (section 13) · 6 open questions (section 14)

## Needs first (merged, with a closed review)

- YT0 YouTube probe: `docs/handoffs/YT0.md`
- C8 poster-resolver: `docs/handoffs/C8.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/youtube/yt-channel-resolver.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: YouTube
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of YT0: `docs/handoffs/YT0.md`
6. Handoff of C8: `docs/handoffs/C8.md`
7. The YT0 probe report `docs/probes/youtube.md` and the fixtures in `fixtures/youtube/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `poster.profiles`
- Job queues in: `jobs.yt-channel-resolver`; out: none
- Tables read: `sources`, `cursors`, `budgets`, `profile_cache`; written or updated: `sources`, `cursors`, `service_runs`, `profile_cache`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/yt-channel-resolver/`
- `docs/handoffs/YT1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/YT1.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Individuals are never profiled: a mention keeps a hashed author reference

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree YT1 --permission-mode plan`, then `/plan-session YT1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session YT1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree YT1`, then `/review-session YT1`
- Fix: `claude --worktree YT1` (or the build terminal), `/fix-session YT1`; then a fresh session runs `/review-session YT1 recheck`; merge when the review has no open blocker or should-fix
