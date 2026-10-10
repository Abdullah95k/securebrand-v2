# G0 · Gate: foundation

Wave 1 · Foundation · track Gates · size S (one sitting) · kind gate · on the critical path

## Builds

Run the foundation gate and write its report.

## Needs first (merged, with a closed review)

- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`
- F2 Contracts package: `docs/handoffs/F2.md`
- F3 Control-plane schema: `docs/handoffs/F3.md`
- F4 SDK runtime (Node): `docs/handoffs/F4.md`
- F5 SDK scheduling, quota client, adapter kit, fake platform: `docs/handoffs/F5.md`
- F6 Python SDK twin: `docs/handoffs/F6.md`
- F7 Text fold and golden corpus: `docs/handoffs/F7.md`
- F8 ClickHouse schema: `docs/handoffs/F8.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Rotation policy; Observability and SLOs; Retention classes; Security and compliance in every service
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of F1: `docs/handoffs/F1.md`
5. Handoff of F2: `docs/handoffs/F2.md`
6. Handoff of F3: `docs/handoffs/F3.md`
7. Handoff of F4: `docs/handoffs/F4.md`
8. Handoff of F5: `docs/handoffs/F5.md`
9. Handoff of F6: `docs/handoffs/F6.md`
10. Handoff of F7: `docs/handoffs/F7.md`
11. Handoff of F8: `docs/handoffs/F8.md`

## Hands on

- `docs/gates/G0.md`

## Watch for

- Nothing beyond this brief and its PRD.

## Done when

- `docs/gates/G0.md` shows every check in `build-plan/GATES.md` with evidence.
- Each failure names its failing command and the session that owns it.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Start: a fresh session on an up-to-date main: `git pull`, then `claude`
- Run: `/integration-gate G0`
