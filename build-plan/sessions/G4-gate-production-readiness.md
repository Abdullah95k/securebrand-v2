# G4 · Gate: production readiness

Wave 5 · Approval-gated platforms and the client portal · track Gates · size M (1 to 2 days with review) · kind gate

## Builds

Security review, restore drill, 24 hours of synthetic load at 1.5 times full scale, counsel sign-off, on-call.

## Needs first (merged, with a closed review)

- G2 Gate: staging with real data: `docs/gates/G2.md` is green
- E2 Gate tooling for staging: `docs/handoffs/E2.md`

Any-time track: earliest after G2 and the first G3; deadline before the first client sees data.

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Rotation policy; Observability and SLOs; Retention classes; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of E2: `docs/handoffs/E2.md`

## Hands on

- `docs/gates/G4.md`

## Watch for

- Nothing beyond this brief and its PRD.

## Done when

- `docs/gates/G4.md` shows every check in `build-plan/GATES.md` with evidence.
- Each failure names its failing command and the session that owns it.

## Runs alongside

Any session (any-time track)

## How to run it

- Start: a fresh session on an up-to-date main: `git pull`, then `claude`
- Run: `/integration-gate G4`
