# D2 fourth fix session: role and brief

Written by the orchestrator on 10 Oct 2026 for the D2 fourth fix session on `sb/D2` (pull request Abdullah95k/securebrand-v2#6). The session's system prompt names this file and its commit; it is part of that session's instructions.

## Role: fix, round 4 (D2 · Decisions and contract freeze)

The third recheck, "Recheck 3, 10 Oct 2026" in `docs/reviews/D2.md` at `6cff2f7`, found 0 blockers and 2 should-fix:
- finding 37: no one is named to request the source-level change when a vendor flag is turned `off`;
- finding 38: ADR-0021 L61 credits the user with a rule they never gave, that turning the flag back on resumes nothing.

### The user's answer

The orchestrator asked the user on 10 Oct 2026 (the third recheck's "For the user", point 1). The question:

> When a vendor's switch is turned back ON, what should happen to the pages that were paused when it was turned off? Example: a client disconnected its TikTok account, so we were reading its new videos through the vendor. Then the vendor switch was turned off and the account went back to paused. Now the switch is on again.

The user chose "Resume automatically", the third recheck's option (b). The option's text:

> Matches your rule that a paused source switches to the vendor automatically whenever that vendor's switch is on. Coverage comes back by itself, with ops notified. Cost: when a switch is turned on, every paused source that qualifies starts vendor reading at once. Budget limits still apply.

### Finding 37

Finding 37 is technical, and the orchestrator takes the third recheck's recommended requester. The audited admin API is the only writer of flags (CONVENTIONS v1.1 L51; ADR-0050 L28). When it changes an amber flag, it sends registry-writer the source-level decisions, the same way news-robots-checker sends its decisions when crawl permission flips (ADR-0040 L32). Under the user's answer it does this on both flips.

### Rules

- Touch only the lines below, the handoff record, and any count they change. Add nothing beyond the user's answer and the requester above.
- Leave `docs/reviews/D2.md`, each ADR's decision line (L3) and Source line, the frozen contract paths, `docs/contracts/*.md` and `build-plan/sessions/*.md` untouched.
- Match each edit on its current text; line numbers are at `6cff2f7`.
- Commit once per numbered group, with messages `D2 fix 4: <what> (recheck 3 findings 37, 38)`, and push after each commit.

### The edits

1. **`docs/decisions/ADR-0021-platform-401-and-403-automatic-fallback-and-its-limits.md`**
   - L61. Replace the last two sentences. The current text:

     > Turning the flag back on does not restart a fallback by itself: the usual entry conditions apply again (the user's answer of 9 Oct 2026, "Short fix first"). registry-writer applies the source-level change and source-health-canary the route-wide one.

     The replacement:

     > Turning the flag back on resumes them (the user's answer of 10 Oct 2026, "Resume automatically"). Every `blocked` source of a type that alternate reads, those the flag returned to `blocked` included, falls back again wherever the conditions above hold. Each is announced as `fallback_on` with reason `flag_on`, with ops' notice (above). A route still `degraded` falls back again at the canary's next decision (above). The audited admin API, the only writer of flags (CONVENTIONS v1.1 L51, ADR-0050), sends registry-writer a source-level `health_change` decision for each affected source when it changes the flag, as news-robots-checker does when crawl permission flips (ADR-0040). When the flag is turned `off`, the decision has reason `flag_off` and health `blocked`, for each source in a source-level `fallback` on that alternate. When the flag is turned back on, the decision has reason `flag_on` and health `blocked`, for each `blocked` source of a type that alternate reads; registry-writer applies it as any source-level `blocked`, moving the source to `fallback` wherever the conditions above hold. In both cases the source keeps the `health_reason` of the decision that blocked it; `flag_off` and `flag_on` are the reasons of these decisions and of the `fallback_off` and `fallback_on` events (ADR-0014, ADR-0016). source-health-canary decides the route-wide change, and registry-writer applies it (above).
   - In "Sessions that must read this", add D3 if it is not there: D3 specifies the admin API.
2. **`docs/decisions/ADR-0016-*.md`** (source health)
   - L25. In the closed list of source-level `reason` values, add `flag_off` and `flag_on` after `crawl_disallowed`.
   - L25. In the sentence that names who sends their own source-level decisions ("x-compliance-sync, the news pollers, web-commoncrawl-scanner and ig-webhook-receiver send their own source-level decisions"), add the audited admin API: "and the audited admin API sends the `flag_off` and `flag_on` decisions when it changes an amber flag (ADR-0021)".
3. **`docs/decisions/ADR-0013-*.md`**
   - Read L23 to L26, where the producers allowed per decision type are F2's producer table.
   - If no line there already allows the audited admin API to send source-level `health_change` decisions, add one clause where the producer rows are described: "the audited admin API may send source-level `health_change` decisions with reason `flag_off` or `flag_on` (ADR-0021)".
   - If the ADR leaves the table entirely to F2, without describing rows, skip this edit and say so in the handoff.
4. **`docs/decisions/ADR-0014-source-events-writer-shape-and-types.md`**
   - L27. In the example `reason` values, add `flag_on` after `flag_off`.
   - L36. Replace the sentence the third fix added, "A `fallback_off` with reason `flag_off` ends a fallback whose alternate's vendor flag was turned `off` (ADR-0021).", with: "A `fallback_off` with reason `flag_off` ends a fallback whose alternate's vendor flag was turned `off`, and a `fallback_on` with reason `flag_on` resumes one when the flag is turned back on (ADR-0021)."
5. **`docs/decisions/ADR-0050-*.md`**
   - L31. Replace "; when the flag is turned `off`, the fallback ends (ADR-0021)" with "; when the flag is turned `off`, the fallback ends, and when it is turned back on, it resumes wherever ADR-0021's conditions hold, the audited admin API sending the source-level decisions for both (ADR-0021)".
6. **`docs/prds/_shared/CONVENTIONS.md`**
   - L240. The current end of the line: "A fallback also ends when its alternate's flag is turned `off`: a source returns to `blocked` and a route to `degraded` (ADR-0021)."
   - Append to the same line: " Turning the flag back on resumes them wherever ADR-0021's conditions hold; the audited admin API sends the source-level decisions, reasons `flag_off` and `flag_on` (ADR-0021, ADR-0016)."
7. **`docs/decisions/D2-SUMMARY.md`**
   - L3. Change "with follow-ups on 9 Oct 2026" to "with follow-ups on 9 and 10 Oct 2026".
   - After the paragraph at L255 (the "Short fix first" one), insert a blank line and this paragraph:

     > After the third recheck (`docs/reviews/D2.md`, "Recheck 3, 10 Oct 2026", "For the user", point 1), the orchestrator asked the user on 10 Oct 2026 what happens to these sources when the flag is turned back on. The user chose "Resume automatically": "Matches your rule that a paused source switches to the vendor automatically whenever that vendor's switch is on. Coverage comes back by itself, with ops notified. Cost: when a switch is turned on, every paused source that qualifies starts vendor reading at once. Budget limits still apply." Turning an amber flag back on resumes the fallback of every `blocked` source of a type that alternate reads, wherever ADR-0021's conditions hold, those the flag returned to `blocked` included. A route still `degraded` falls back again at the canary's next decision. The audited admin API sends the source-level decisions on both flips (ADR-0021, ADR-0016, ADR-0014, ADR-0050).
   - In the D2-Q021 row, after "a fallback ends when its alternate's flag is turned `off` (9 Oct 2026: "Short fix first"; ADR-0021)", append "and resumes when it is turned back on (10 Oct 2026: "Resume automatically"; ADR-0021)".
   - Run `make fmt` afterwards.
8. **`docs/handoffs/D2.md`**
   - L143. Replace the entry with: "C7, C12, D3 and F2: when an amber flag changes, the audited admin API (D3) sends registry-writer (C7) a source-level `health_change` decision for each affected source, reason `flag_off` or `flag_on`. registry-writer ends the fallback, or resumes it wherever ADR-0021's conditions hold, and keeps each source's own `health_reason`. source-health-canary (C12) decides the route-wide change. F2 adds `flag_off` and `flag_on` to the closed `reason` list, and the admin API's row to the producer table (ADR-0021, ADR-0016, ADR-0014, ADR-0013)."
   - In the third fix session's table (L372), the finding 36 row says "turning the flag back on restarts nothing by itself". Append to that cell: " (superseded by the user's answer of 10 Oct 2026, "Resume automatically"; see the fourth fix session)".
   - Insert a subsection "### The fourth D2 fix session (10 Oct 2026)" before "### The review before the pull request" (L406). It holds:
     - a table of findings 37 and 38, with their commits and what changed;
     - the user's answer, quoted as above;
     - the orchestrator's choice of requester;
     - any edit skipped, with the reason;
     - the checks you ran.

### Checks

- `grep -n "flag_on" docs/decisions/ADR-0014-*.md docs/decisions/ADR-0016-*.md docs/decisions/ADR-0021-*.md docs/prds/_shared/CONVENTIONS.md docs/decisions/D2-SUMMARY.md docs/handoffs/D2.md` finds the new lines.
- `grep -rn "does not restart a fallback" docs/decisions docs/prds/_shared` prints nothing.
- `git diff --name-only 6cff2f7 -- packages/contracts supabase/migrations clickhouse/migrations docs/contracts docs/reviews build-plan/sessions` prints nothing.
- `python3 build-plan/tools/validate.py` passes, and `python3 build-plan/tools/gen_briefs.py . build-plan/tools/prd_index.json build-plan/tools/prd_io.json` leaves `git status` clean.
- Start Docker and run `make bootstrap` (see "Cloud container"), then `make check`.
- Run `nvm use 24.21.0 >/dev/null && pnpm exec prettier --check` on the changed files under `docs/decisions/` and `docs/handoffs/`.
- Push, then read your head's check runs over REST, read-only. A `make up` failure binding port 54322 is the known CI infrastructure problem.

### Finish

End with ORCHESTRATOR: DONE. Give:
- each edit with its commit;
- anything skipped, and why;
- the check results and the `make check` result;
- the pushed SHA.
