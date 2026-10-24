# I2 · Observability

Wave 1 · Foundation · track Infra · size M (1 to 2 days with review) · kind infra

## Builds

Prometheus, Grafana dashboards per service family, logs, alert rules for the SLOs, alert routing through n8n.

## Needs first (merged, with a closed review)

- I1 Infrastructure (staging first): `docs/handoffs/I1.md`
- F4 SDK runtime (Node): `docs/handoffs/F4.md`

Any-time track: earliest after I1 and F4; deadline before G2.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Observability and SLOs; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of I1: `docs/handoffs/I1.md`
5. Handoff of F4: `docs/handoffs/F4.md`
6. CONVENTIONS observability section
7. Each PRD's section 10 (metrics and alerts)

## Hands on

- `docs/handoffs/I2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/I2.md` from the fresh-session review
- dashboards: rotation lag, staleness p95, DLQ, quota denied, cost units
- alert routes to Telegram or Slack through n8n

## Watch for

- Nothing beyond this brief and its PRD.

## Done when

- The definition of done in `build-plan/README.md` holds.
- Everything is in `infra/` as code; a deploy, a rollback and a restore were each rehearsed on staging.

## Runs alongside

Any session (any-time track)

## How to run it

- Plan: `claude --worktree I2 --permission-mode plan`, then `/plan-session I2`; read the plan (Ctrl+G), approve with "Yes, manually approve edits" so you review every command and change
- Build: `/clear`, then `/build-session I2` (Manual mode); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree I2`, then `/review-session I2`
- Fix: `claude --worktree I2` (or the build terminal), `/fix-session I2`; then a fresh session runs `/review-session I2 recheck`; merge when the review has no open blocker or should-fix
