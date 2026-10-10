# C2 · raw-archiver

Wave 2 · Shared core · track Core · size M (1 to 2 days with review) · kind service

## Builds

Archive of raw.items to object storage, raw_ref, replay reader.

Service `raw-archiver` · PRD `docs/prds/shared/raw-archiver.md` · lane Support · route shared · 10 acceptance criteria (section 13) · 4 open questions (section 14)

## Needs first (merged, with a closed review)

- F4 SDK runtime (Node): `docs/handoffs/F4.md`
- G0 Gate: foundation: `docs/gates/G0.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/raw-archiver.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes; Quotas, budgets and the quota governor
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of F4: `docs/handoffs/F4.md`
6. CONVENTIONS object-storage layout
7. Local SeaweedFS bucket

## Contracts it touches (from PRD section 6)

- Topics read: `raw.items`, `source.events`
- Topics written: none named in 6.2
- Job queue: `jobs.raw-archiver` if the PRD's section 5.1 schedules jobs
- Tables read: `clients`, `cursors`, `deletion_requests`, `retention_classes`; written or updated: `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/raw-archiver/`
- `docs/handoffs/C2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/C2.md` from the fresh-session review
- archive reader for replays (normalize-item, lang-dialect-id, analysis)

## Watch for

- Commit offsets only after the object is durable
- Raw payloads can hold personal data: deletions must reach them (C13)
- Deletion and retention actions are audited before they run, so a replay changes nothing

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

C0, C1, C3, C7

## How to run it

- Plan: `claude --worktree C2 --permission-mode plan`, then `/plan-session C2`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session C2` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree C2`, then `/review-session C2`
- Fix: `claude --worktree C2` (or the build terminal), `/fix-session C2`; then a fresh session runs `/review-session C2 recheck`; merge when the review has no open blocker or should-fix
