# A4 · analysis-media

Wave 6 · Insight layer · track Insight · size L (3 to 5 days with review) · kind service

## Builds

Images, thumbnails, OCR; no YouTube audio or video download in v1.

Service `analysis-media` · PRD `docs/prds/shared/analysis-media.md` · lane Processing · route shared · 11 acceptance criteria (section 13) · 7 open questions (section 14)

## Needs first (merged, with a closed review)

- F6 Python SDK twin: `docs/handoffs/F6.md`
- C4 normalize-item (core): `docs/handoffs/C4.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/shared/analysis-media.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Retention classes
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
5. Handoff of F6: `docs/handoffs/F6.md`
6. Handoff of C4: `docs/handoffs/C4.md`
7. A3 brand ids when available

## Contracts it touches (from PRD section 6)

- Topics read: `items.normalized`, `item.hits`, `discovery.hits`, `source.events`
- Topics written: `items.analysis`
- Job queues in: `jobs.analysis-media`; out: none
- Tables read: `sources`, `cursors`, `review_queue`, `retention_classes`, `service_runs`, `model_versions`, `brand_assets`; written or updated: `cursors`, `review_queue`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/analysis-media/`
- `docs/handoffs/A4.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/A4.md` from the fresh-session review

## Watch for

- Stateless where the PRD says so; replay from raw-archiver must reproduce the same output for the same model version

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

A1, A2, A3

## How to run it

- Plan: `claude --worktree A4 --permission-mode plan`, then `/plan-session A4`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session A4` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree A4`, then `/review-session A4`
- Fix: `claude --worktree A4` (or the build terminal), `/fix-session A4`; then a fresh session runs `/review-session A4 recheck`; merge when the review has no open blocker or should-fix
