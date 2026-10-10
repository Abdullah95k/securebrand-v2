---
name: review-session
description: Independent review of one session's work against its PRD, its plan and the repo conventions; writes docs/reviews/<ID>.md. Run in a fresh session that did not write the code. Add "recheck" to verify fixes against an existing review.
argument-hint: <session ID> [recheck]
disable-model-invocation: true
effort: max
---

# Review session $0

You are reviewing work you did not write. Change nothing except `docs/reviews/$0.md`.

Arguments given: $ARGUMENTS. If they include the word "recheck", this is a recheck: go to the last section.

## Context

The brief (`ls build-plan/sessions/$0-*`), the PRD, the ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (an ADR wins over the PRD, ADR-0001), the rows of `docs/decisions/DEFERRED.md` that name this session, `docs/plans/$0.md` and `docs/handoffs/$0.md`. Then run `git fetch origin` and read the diff with `git diff origin/main...HEAD`. Worktrees branch from the remote's main, so a local `main` may be stale and show other sessions' merged work.

## Checks

1. **Acceptance.** For each criterion in PRD section 13, as amended by the ADRs that apply (ADR-0001), find the test that proves it, run it, and record pass, fail or untested with the command and an output excerpt. A criterion with no test is a blocker.
2. **Conventions.** Replaying a job or a message twice changes nothing. Cursors advance only after the producer acknowledges. 429 backs off from 30 s to 15 min with jitter; 401 and 403 are classified by reason (an authorisation one sets credential or source state, never a route state, and stops the batch; ADR-0021); empty 200s are counted; five failed attempts go to the DLQ. Rotation or the comment series behave as PRD section 5.1 says, as amended by the ADRs (ADR-0001). The budget tag and priority match CONVENTIONS. Every output validates against its contract, and every data output carries provenance and `retention_class` (ADR-0003). Metric names match PRD section 10, as amended by the ADRs (ADR-0001).
3. **Scope.** Nothing outside this service changed, except an allowed normalize-item mapper; no edits under `packages/contracts` or the migrations unless this is F2, F3, F8 or a contract change.
4. **Real tests.** No assertion weakened to pass, no snapshot accepted without inspection, no mock where the SDK or a fixture should be exercised, no network access in tests.
5. **Compliance.** The route class matches the PRD; amber code runs only behind its flag; no account or IP rotation; no proxies on platform APIs; private individuals keyed (`author_ref`), never profiled, listed or backfilled, and only public accounts listed (ADR-0010); no token, secret or private person's name in code, logs or fixtures; every new dependency listed in `docs/dependencies.md` and clear of the vendor screen.

You may ask the `prd-reviewer` subagent for a second opinion on a finding you are unsure of.

## Write docs/reviews/$0.md from build-plan/templates/REVIEW.md

Rank findings blocker, should-fix or note. Each one needs file and line and a failing test or command that demonstrates it. Report only what affects correctness, the PRD or the conventions; no style preferences. A reviewer asked to find gaps will always find some, so flag only what you can demonstrate.

End with a two-line verdict: "ready to merge", or "needs fixes: N blockers, M should-fix".

## Recheck

Keep the existing `docs/reviews/$0.md`. For each finding marked open, find the commit that claims to fix it, run its test, and set its status to fixed or still open with evidence. Then read the diff of the fix commits only, and add any new problem they introduced as a new finding. Append a "Recheck <date>" section with the new verdict. Do not rewrite the original findings.
