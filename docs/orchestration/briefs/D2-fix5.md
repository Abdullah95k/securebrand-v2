# D2 fifth fix session: role and brief

Written by the orchestrator on 10 Oct 2026 for the D2 fifth fix session on `sb/D2` (pull request Abdullah95k/securebrand-v2#6). The session's system prompt names this file and its commit; it is part of that session's instructions.

## Role: fix, round 5 (D2 · Decisions and contract freeze)

The fourth fix session (`6cff2f7..15b61fa`) applied the orchestrator's fourth brief and raised two points for the recheck. Both come from that brief's text, not from the user's answer. The orchestrator checked them against the files at `15b61fa` and found them real. These are technical corrections, and they are the orchestrator's choice, not the user's. Nothing here changes the user's answer of 10 Oct 2026, "Resume automatically".

1. **Sources the canary blocked with their route.** ADR-0021 L61 sends the source-level `flag_on` decision to "each `blocked` source of a type that alternate reads". That includes sources whose `blocked` was set at route level. ADR-0016 L25 applies route-level states only "to sources whose state is `ok` or was set at route level", and clears a source-level state "only by a source-level decision". So a source-level `flag_on` decision would turn a route-level state into a source-level one, and the source would stay in `fallback` after its route recovers. The `flag_off` decision already covers only source-level fallbacks; `flag_on` must match it. Sources whose state was set at route level follow their route: the canary decides, as L61 already says for a `degraded` route.
2. **Who can still clear the state.** L61 says the source "keeps the `health_reason` of the decision that blocked it". ADR-0016 L25 lets "the service that set it, or ops" clear a source-level state, and `health_set_by` records who set it. If the admin API's decision replaced `health_set_by`, the service that blocked the source could no longer end its fallback, for example on a new grant. The source must keep both.
3. **Repeat notices.** A `flag_on` decision is applied "as any source-level `blocked`". For a source that cannot fall back and stays `blocked`, that would send ops' notice of a blocked source again, and a client-owned property's missing-grant card again, on every flip. A decision that changes no state must change nothing (CLAUDE.md: replaying a message must change nothing).
4. **Two lines that name only the 9 Oct follow-ups**, which the fourth fix session listed in its handoff, item 5: `D2-SUMMARY.md` L259 and the handoff's L65.

### Rules

- Touch only the lines below and the handoff record. Add nothing beyond the four points above.
- Leave `docs/reviews/D2.md`, each ADR's decision line (L3) and Source line, the frozen contract paths, `docs/contracts/*.md` and `build-plan/sessions/*.md` untouched.
- Match each edit on its current text; line numbers are at `15b61fa`.
- Commit once per numbered group, with messages `D2 fix 5: <what> (fix 4's points for the recheck)`, and push after each commit.

### The edits

1. **`docs/decisions/ADR-0021-platform-401-and-403-automatic-fallback-and-its-limits.md`**, L61. Four replacements, each on its exact current text:
   - (a) Replace "Every `blocked` source of a type that alternate reads, those the flag returned to `blocked` included, falls back again wherever the conditions above hold." with "Every source of a type that alternate reads whose `blocked` was set at source level, those the flag returned to `blocked` included, falls back again wherever the conditions above hold."
   - (b) Replace "A route still `degraded` falls back again at the canary's next decision (above)." with "A route still `degraded` falls back again at the canary's next decision (above), and a source whose state was set at route level follows its route (ADR-0016)."
   - (c) Replace "When the flag is turned back on, the decision has reason `flag_on` and health `blocked`, for each `blocked` source of a type that alternate reads; registry-writer applies it as any source-level `blocked`, moving the source to `fallback` wherever the conditions above hold." with "When the flag is turned back on, the decision has reason `flag_on` and health `blocked`, for each source of a type that alternate reads whose `blocked` was set at source level; registry-writer applies it as any source-level `blocked`, moving the source to `fallback` wherever the conditions above hold. A `flag_on` decision that leaves a source `blocked` changes nothing, and sends no new notice or card."
   - (d) Replace "In both cases the source keeps the `health_reason` of the decision that blocked it;" with "In both cases the source keeps the `health_reason` and `health_set_by` of the decision that blocked it, so the service that set it, or ops, still clears it (ADR-0016);".
2. **`docs/decisions/D2-SUMMARY.md`**
   - L257. Replace "resumes the fallback of every `blocked` source of a type that alternate reads, wherever ADR-0021's conditions hold, those the flag returned to `blocked` included." with "resumes the fallback of every source of a type that alternate reads whose `blocked` was set at source level, wherever ADR-0021's conditions hold, those the flag returned to `blocked` included."
   - L259. Replace "the 9 Oct follow-ups included" with "the 9 and 10 Oct follow-ups included".
   - Run `make fmt` afterwards, and check that it changed nothing but whitespace.
3. **`docs/handoffs/D2.md`**
   - L65. Replace "with the user's follow-ups of 9 Oct 2026 on Q021, Q068, the review's points and the recheck's points" with "with the user's follow-ups of 9 and 10 Oct 2026 on Q021, Q068, the review's points and the rechecks' points".
   - L143. Replace "for each affected source, reason `flag_off` or `flag_on`." with "for each affected source whose state was set at source level, reason `flag_off` or `flag_on`." Then replace "and keeps each source's own `health_reason`." with "and keeps each source's own `health_reason` and `health_set_by`; a `flag_on` decision that leaves a source `blocked` changes nothing."
   - In the fourth fix session's subsection, item 5 (L439), append: " (fixed by the fifth fix session)".
   - Insert a subsection "### The fifth D2 fix session (10 Oct 2026)" before "### The review before the pull request" (L457). It holds:
     - a table of the four points above, with their commits and what changed;
     - one sentence saying these corrections are the orchestrator's technical choice, from the fourth fix session's points, and that the user's answer is unchanged;
     - any edit skipped, with the reason;
     - the checks you ran.

### Checks

- `grep -n "whose \`blocked\` was set at source level" docs/decisions/ADR-0021-*.md docs/decisions/D2-SUMMARY.md` finds L61 twice and L257 once.
- `grep -n "health_set_by" docs/decisions/ADR-0021-*.md docs/handoffs/D2.md` finds the new text.
- `grep -rn "each \`blocked\` source of a type\|every \`blocked\` source of a type" docs/decisions docs/handoffs docs/prds/_shared` prints nothing.
- `grep -n "9 Oct follow-ups included\|follow-ups of 9 Oct 2026 on" docs/decisions/D2-SUMMARY.md docs/handoffs/D2.md` prints nothing.
- `git diff --name-only 15b61fa -- packages/contracts supabase/migrations clickhouse/migrations docs/contracts docs/reviews build-plan/sessions` prints nothing.
- `python3 build-plan/tools/validate.py` passes, and `python3 build-plan/tools/gen_briefs.py . build-plan/tools/prd_index.json build-plan/tools/prd_io.json` leaves `git status` clean.
- Start Docker and run `make bootstrap` (see "Cloud container"), then `make check`.
- Run `nvm use 24.21.0 >/dev/null && pnpm exec prettier --check` on the changed files under `docs/decisions/` and `docs/handoffs/`.
- Push, then read your head's check runs over REST, read-only. A `make up` failure binding port 54322 is the known CI infrastructure problem.

### Finish

End with ORCHESTRATOR: DONE. Give:
- each edit with its commit;
- anything skipped, and why;
- the check results and the `make check` result;
- the pushed SHA;
- anything else you notice for the recheck, unchanged.
