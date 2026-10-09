# YT9 · yt-web-search-bridge

Wave 4 · YouTube, X, and Facebook in development mode · track YouTube · size S (one sitting) · kind service

## Builds

YouTube URLs from the web search engines.

Service `yt-web-search-bridge` · PRD `docs/prds/youtube/yt-web-search-bridge.md` · lane Discover and qualify · route green · 9 acceptance criteria (section 13) · 0 open questions (section 14)

## Needs first (merged, with a closed review)

- W1 web-search-perplexity: `docs/handoffs/W1.md`
- W2 web-search-mojeek: `docs/handoffs/W2.md`
- YT1 yt-channel-resolver: `docs/handoffs/YT1.md`

Any-time track: earliest after W1, W2 and YT1; deadline none.

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/youtube/yt-web-search-bridge.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: YouTube
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of W1: `docs/handoffs/W1.md`
6. Handoff of W2: `docs/handoffs/W2.md`
7. Handoff of YT1: `docs/handoffs/YT1.md`
8. The YT0 probe report `docs/probes/youtube.md` and the fixtures in `fixtures/youtube/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: none named in 6.1
- Topics written: `search.results`
- Job queues in: its own `jobs.yt-web-search-bridge`; out: `jobs.yt-channel-resolver`, `jobs.yt-video-details-fetcher`
- Tables read: `sources`, `keywords`, `clients`, `cursors`, `budgets`, `vendor_keys`, `service_runs`; written or updated: `clients`, `cursors`, `budgets`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/yt-web-search-bridge/`
- `docs/handoffs/YT9.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/YT9.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Any session (any-time track)

## How to run it

- Plan: `claude --worktree YT9 --permission-mode plan`, then `/plan-session YT9`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session YT9` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree YT9`, then `/review-session YT9`
- Fix: `claude --worktree YT9` (or the build terminal), `/fix-session YT9`; then a fresh session runs `/review-session YT9 recheck`; merge when the review has no open blocker or should-fix
