# N1 · news-robots-checker

Wave 3 · First real data, and the Meta review build · track News · size M (1 to 2 days with review) · kind service

## Builds

Crawl policies per host (robots, Content Signals, RSL, 402) and the host gate wiring.

Service `news-robots-checker` · PRD `docs/prds/news/news-robots-checker.md` · lane Discover and qualify · route green · 11 acceptance criteria (section 13) · 5 open questions (section 14)

## Needs first (merged, with a closed review)

- F5 SDK scheduling, quota client, adapter kit, fake platform: `docs/handoffs/F5.md`
- N0 News probe and seed list: `docs/handoffs/N0.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/news/news-robots-checker.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Qualifier rules; Quotas, budgets and the quota governor; Per-platform fact sheets: News websites
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of F5: `docs/handoffs/F5.md`
6. Handoff of N0: `docs/handoffs/N0.md`
7. The N0 probe report `docs/probes/news.md` and the fixtures in `fixtures/news/`
8. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)
9. N0 report and fixtures
10. ADR on the host gate (decision 6)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `crawl.policies`
- Job queues in: `jobs.news-robots-checker`; out: none
- Tables read: `sources`, `crawl_policies`, `news_sites`; written or updated: `sources`, `crawl_policies`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/news-robots-checker/`
- `docs/handoffs/N1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/N1.md` from the fresh-session review

## Watch for

- Policy precedence exactly as the PRD orders it
- Every news service reads crawl.policies before fetching
- Searches write items to raw.items with source_id = the keyword rule (search output rule); candidates are deduplicated by candidate_key downstream
- Private individuals are never profiled, listed or backfilled: a mention keeps a keyed author reference (author_ref); only public accounts, as ADR-0010 defines them, may be listed

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree N1 --permission-mode plan`, then `/plan-session N1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session N1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree N1`, then `/review-session N1`
- Fix: `claude --worktree N1` (or the build terminal), `/fix-session N1`; then a fresh session runs `/review-session N1 recheck`; merge when the review has no open blocker or should-fix
