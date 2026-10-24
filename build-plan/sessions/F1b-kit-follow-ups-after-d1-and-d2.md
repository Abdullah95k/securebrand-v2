# F1b · Kit follow-ups after D1 and D2

Wave 1 · Foundation · track Foundation · size M (1 to 2 days with review) · kind foundation

## Builds

The repository toolkit's follow-up after D1 and D2: the contract lanes' kit wording and the guard's tests; a stop gate that counts only proposals and issues filed in the session, with tests; make bootstrap as the install step; bootstrap re-runs offline and with a uv that pip installed; no version checks from pyright and the Supabase CLI; shallow clones find the merge base; CI keeps the Supabase ports out of the ephemeral range and retries a port collision once; image pulls fail fast on a registry limit; ClickHouse mirrored into GHCR; CI checks formatting; the mirror workflow runs on main; Dependabot settings; F1's records corrected.

## Needs first (merged, with a closed review)

- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`
- D2 Decisions and contract freeze: `docs/handoffs/D2.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment; Idempotency and deduplication; Error handling, canaries and fallback; Observability and SLOs; Security and compliance in every service; Addendum: Other shared decisions
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of F1: `docs/handoffs/F1.md`
5. Handoff of D2: `docs/handoffs/D2.md`
6. Docs/handoffs/F1.md
7. Docs/reviews/F1.md
8. The orchestrator's brief for this lane (W1 to W13 and its decisions table), in the session's system prompt

## Hands on

- `docs/handoffs/F1b.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/F1b.md` from the fresh-session review
- the toolkit changes W1 to W13 with their repo-checks tests
- `docs/handoffs/F1b.md`

## Watch for

- Done when the acceptance table W1 to W13 of the orchestrator's brief passes. This lane changes the repository toolkit, not a package: the generic lines about a package README with a runnable example and conformance tests in every language do not apply
- The hooks run on this session's own tool calls: check a new hook copy with bash -n and a harmless payload before copying it over the live one

## Done when

- The definition of done in `build-plan/README.md` holds.
- The package README shows a service using it, with a runnable example.
- Conformance or golden tests named in this brief pass in every language involved.

## Runs alongside

Nothing in particular; see the wave table

## How to run it

- Plan: `claude --worktree F1b --permission-mode plan`, then `/plan-session F1b`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session F1b` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree F1b`, then `/review-session F1b`
- Fix: `claude --worktree F1b` (or the build terminal), `/fix-session F1b`; then a fresh session runs `/review-session F1b recheck`; merge when the review has no open blocker or should-fix
