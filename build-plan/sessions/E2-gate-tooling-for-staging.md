# E2 · Gate tooling for staging

Wave 3 · First real data, and the Meta review build · track Infra · size M (1 to 2 days with review) · kind infra

## Builds

Scripts and queries the G2 to G4 checks run: SLO reports, cost reconciliation, crawl-policy audit, restore drill, per-platform compliance checks, synthetic load at 1.5 times full scale through the fake platform.

## Needs first (merged, with a closed review)

- G1 Gate: fake platform end to end: `docs/gates/G1.md` is green
- I1 Infrastructure (staging first): `docs/handoffs/I1.md`
- I2 Observability: `docs/handoffs/I2.md`

Any-time track: earliest after G1, I1 and I2; deadline before G2.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Observability and SLOs; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's service, platform, lane or "all"
4. Handoff of I1: `docs/handoffs/I1.md`
5. Handoff of I2: `docs/handoffs/I2.md`
6. Build-plan/GATES.md (G2, G3 and G4 checks)
7. I1 and I2 handoffs
8. CONVENTIONS observability and retention sections

## Hands on

- `docs/handoffs/E2.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/E2.md` from the fresh-session review
- `tools/gates/` with one runnable script or query per check
- make gate-report GATE=<G>

## Watch for

- Read-only against staging except the load generator and the restore drill, which run only in a scratch environment
- Each platform's compliance check is a stub until that platform's session fills it in; G3 fails while a stub remains

## Done when

- The definition of done in `build-plan/README.md` holds.
- Every G2, G3 and G4 check in `build-plan/GATES.md` has a script or query in `tools/gates/`, and a dry run against staging produces a report.
- Everything is in `infra/` as code; a deploy, a rollback and a restore were each rehearsed on staging.

## Runs alongside

Any session (any-time track)

## How to run it

- Plan: `claude --worktree E2 --permission-mode plan`, then `/plan-session E2`; read the plan (Ctrl+G), approve with "Yes, manually approve edits" so you review every command and change
- Build: `/clear`, then `/build-session E2` (Manual mode); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree E2`, then `/review-session E2`
- Fix: `claude --worktree E2` (or the build terminal), `/fix-session E2`; then a fresh session runs `/review-session E2 recheck`; merge when the review has no open blocker or should-fix
