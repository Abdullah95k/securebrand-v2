# G3 · Gate: platform go-live (repeat per platform)

Wave 4 · YouTube, X, and Facebook in development mode · track Gates · size M (1 to 2 days with review) · kind gate

## Builds

Per-platform go-live checklist on staging.

## Needs first (merged, with a closed review)

- G2 Gate: staging with real data: `docs/gates/G2.md` is green

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Rotation policy; Observability and SLOs; Retention classes; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session

## Hands on

- `docs/gates/G3-<platform>.md`

## Watch for

- Nothing beyond this brief and its PRD.

## Done when

- `docs/gates/G3-<platform>.md` shows every check in `build-plan/GATES.md` with evidence.
- Each failure names its failing command and the session that owns it.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Start: a fresh session on an up-to-date main: `git pull`, then `claude`
- Run: `/integration-gate G3-<platform>`
