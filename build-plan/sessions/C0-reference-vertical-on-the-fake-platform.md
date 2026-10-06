# C0 · Reference vertical on the fake platform

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind core · on the critical path

## Builds

ref-poller, ref-comments-fetcher, ref-resolver and ref-search against the fake platform, using every SDK feature once; the adapter pattern note.

## Needs first (merged, with a closed review)

- F5 SDK scheduling, quota client, adapter kit, fake platform: `docs/handoffs/F5.md`
- G0 Gate: foundation: `docs/gates/G0.md` is green

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Rotation policy; Idempotency and deduplication; Error handling, canaries and fallback; Addendum: Comment series profiles; Addendum: Other shared decisions
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of F5: `docs/handoffs/F5.md`
5. Fb-page-feed-poller and fb-post-comments-fetcher PRDs as the models
6. F5 handoff

## Hands on

- `docs/handoffs/C0.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C0.md` from the fresh-session review
- `services/ref-*` (test-only, never deployed)
- `docs/patterns/ADAPTER-PATTERN.md:` the copy-me guide for every platform session

## Watch for

- Every behaviour a platform service needs (rotation, catch-up, quota wait, 429, 401, empty 200, DLQ, backfill hand-over, comment-series report) appears here once

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C1, C2, C3, C7

## How to run it

- Plan: `claude --worktree C0 --permission-mode plan`, then `/plan-session C0`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C0` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C0`, then `/review-session C0`
- Fix: `claude --worktree C0` (or the build terminal), `/fix-session C0`; then a fresh session runs `/review-session C0 recheck`; merge when the review has no open blocker or should-fix
