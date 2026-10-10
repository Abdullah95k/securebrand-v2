# F7 · Text fold and golden corpus

Wave 1 · Foundation · track Foundation · size M (1 to 2 days with review) · kind foundation · on the critical path

## Builds

The Arabic and Sorani folds in TypeScript exactly as lang-dialect-id section 5.3 C defines them, tokenizer helpers, and a golden corpus both languages' code must pass.

## Needs first (merged, with a closed review)

- D2 Decisions and contract freeze: `docs/handoffs/D2.md`
- F1 Repository, toolchain, local stack, CI, Claude kit: `docs/handoffs/F1.md`

## Give the session (read in this order)

1. This brief
2. CONVENTIONS v1.1 (`docs/prds/_shared/CONVENTIONS.md`), these sections: Naming, repository, deployment
3. The ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session
4. Handoff of D2: `docs/handoffs/D2.md`
5. Handoff of F1: `docs/handoffs/F1.md`
6. Lang-dialect-id PRD (detection, fold table, /v1/fold)
7. Keyword-matcher and normalize-item PRDs (text_norm use)

## Hands on

- `docs/handoffs/F7.md` from `build-plan/templates/HANDOFF.md`
- `docs/reviews/F7.md` from the fresh-session review
- `packages/text` v1
- `fixtures/text/golden.jsonl` (500 or more cases: Iraqi Arabic, MSA, Sorani, mixed, English, emoji, URLs, hashtags, digits)

## Watch for

- Language is decided on the raw text first; the fold depends on it (yaa folds in opposite directions for Arabic and Sorani)
- Sorani-only letters (ڕ ڵ ۆ ێ ە) must survive the fold
- Arabizi is not transliterated (documented gap)

## Done when

- The definition of done in `build-plan/README.md` holds.
- The package README shows a service using it, with a runnable example.
- Conformance or golden tests named in this brief pass in every language involved.

## Runs alongside

F2, F3, F4, F5, F8

## Your part

An Iraqi Arabic and Sorani reader reviews the golden file.

## How to run it

- Plan: `claude --worktree F7 --permission-mode plan`, then `/plan-session F7`; read the plan (Ctrl+G), approve with auto mode or accept-edits
- Build: `/clear`, then `/build-session F7` (the mode you approved with); optionally keep it going with `/goal` (see `build-plan/README.md`)
- Review: a new terminal, `claude --worktree F7`, then `/review-session F7`
- Fix: `claude --worktree F7` (or the build terminal), `/fix-session F7`; then a fresh session runs `/review-session F7 recheck`; merge when the review has no open blocker or should-fix
