# FB1 · fb-page-resolver

Wave 3 · First real data, and the Meta review build · track Facebook · size M (1 to 2 days with review) · kind service · on the critical path

## Builds

Resolves Facebook Page candidates into profiles.

Service `fb-page-resolver` · PRD `docs/prds/facebook/fb-page-resolver.md` · lane Discover and qualify · route green · 11 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- FB0 Meta probe (development mode): `docs/handoffs/FB0.md`
- C8 poster-resolver: `docs/handoffs/C8.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/facebook/fb-page-resolver.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: Facebook
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of FB0: `docs/handoffs/FB0.md`
6. Handoff of C8: `docs/handoffs/C8.md`
7. The FB0 probe report `docs/probes/meta.md` and the fixtures in `fixtures/facebook/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `poster.profiles`
- Job queues in: `jobs.fb-page-resolver`; out: none
- Tables read: `sources`, `clients`, `budgets`, `profile_cache`; written or updated: `sources`, `service_runs`, `profile_cache`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/fb-page-resolver/`
- `docs/handoffs/FB1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/FB1.md` from the fresh-session review

## Watch for

- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Individuals are never profiled: a mention keeps a hashed author reference

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree FB1 --permission-mode plan`, then `/plan-session FB1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session FB1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree FB1`, then `/review-session FB1`
- Fix: `claude --worktree FB1` (or the build terminal), `/fix-session FB1`; then a fresh session runs `/review-session FB1 recheck`; merge when the review has no open blocker or should-fix
