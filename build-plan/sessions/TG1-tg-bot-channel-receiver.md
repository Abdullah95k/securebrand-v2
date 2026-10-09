# TG1 · tg-bot-channel-receiver

Wave 5 · Approval-gated platforms and the client portal · track Telegram · size M (1 to 2 days with review) · kind service

## Builds

Channel posts pushed to our bot; the Telegram mapper.

Service `tg-bot-channel-receiver` · PRD `docs/prds/telegram/tg-bot-channel-receiver.md` · lane Fetch posts · route green · 10 acceptance criteria (section 13) · 6 open questions (section 14)

## Needs first (merged, with a closed review)

- TG0 Telegram probe: `docs/handoffs/TG0.md`
- I1 Infrastructure (staging first): `docs/handoffs/I1.md`
- C8 poster-resolver: `docs/handoffs/C8.md`
- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green

## Give the session (read in this order)

1. This brief
2. The PRD in full: `docs/prds/telegram/tg-bot-channel-receiver.md`
3. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions; The registry; Rotation policy; Quotas, budgets and the quota governor; Retention classes; Per-platform fact sheets: Telegram
4. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
5. Handoff of TG0: `docs/handoffs/TG0.md`
6. Handoff of I1: `docs/handoffs/I1.md`
7. Handoff of C8: `docs/handoffs/C8.md`
8. The TG0 probe report `docs/probes/telegram.md` and the fixtures in `fixtures/telegram/`
9. `docs/patterns/ADAPTER-PATTERN.md` (from C0) and `docs/patterns/MAPPERS.md` (from C4)

## Contracts it touches (from PRD section 6)

- Topics read: `source.events`
- Topics written: `raw.items`, `discovery.hits`, `source.events`
- Job queues in: `jobs.tg-bot-channel-receiver`; out: none
- Tables read: `sources`, `cursors`, `credentials` (the PRD's `vendor_keys`, read and written only through the SDK's credential client, ADR-0016), `canary_targets`; written or updated: `sources`, `cursors`, `service_runs`
- This list is extracted from the PRD's section 6 by name; the plan confirms each item against `packages/contracts` and the migrations, and anything missing becomes a proposal.

## Hands on

- Code and tests in `services/tg-bot-channel-receiver/`
- `docs/handoffs/TG1.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/TG1.md` from the fresh-session review
- Telegram mapper in normalize-item

## Watch for

- The due time is next_due_at in this service's own cursors row, set from the start of the last poll; order by it then tier; most stale first when behind, with rotation_behind (ADR-0015)
- Incremental reads only newer than the cursor; full re-reads happen only in backfill jobs from backfill-orchestrator
- The cursor advances only after the producer acknowledges the batch

## Done when

- The definition of done in `build-plan/README.md` holds.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree TG1 --permission-mode plan`, then `/plan-session TG1`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session TG1` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree TG1`, then `/review-session TG1`
- Fix: `claude --worktree TG1` (or the build terminal), `/fix-session TG1`; then a fresh session runs `/review-session TG1 recheck`; merge when the review has no open blocker or should-fix
