# D2 third fix session: role and brief

Written by the orchestrator on 9 Oct 2026 for the D2 third fix session on `sb/D2` (pull request Abdullah95k/securebrand-v2#6). The session's system prompt names this file and its commit; it is part of that session's instructions.

## Role: fix, round 3 (D2 · Decisions and contract freeze)

The second recheck, "Recheck 2, 9 Oct 2026" in `docs/reviews/D2.md` at `5410fb5`, reads "ready to merge". It leaves two notes:
- finding 35: ADR-0021 L60's list leaves out ig-hashtag-search;
- finding 36: no rule covers an alternate's vendor flag turned `off` during a fallback. This was its "For the user" point 1.

The user answered point 1 on 9 Oct 2026 with "Short fix first". The orchestrator's question and the user's choice, in full:

> If someone turns a vendor's switch off while a page is being read through that vendor (because its normal access was lost), nothing says what happens … Short fix first: Turning the switch off ends the vendor reading: the page goes back to 'paused', ops get a notice, and a client's own page gets the 'please reconnect' card; a whole platform affected goes back to its normal route. I also fix the missing hashtag line.

That is the recheck's option (a). Apply the edits below, and nothing else. They are small, so read each target line before you edit it. Match on the current text; line numbers are at `5410fb5`.

### Rules

- Touch only the lines below, plus the handoff record and any counts they change.
- Add no decision beyond the user's answer and the recheck's option (a).
- Leave `docs/reviews/D2.md`, each ADR's decision line (L3) and Source line, the frozen contract paths, `docs/contracts/*.md` and `build-plan/sessions/*.md` untouched.
- Commit once per numbered edit group below, with messages `D2 fix 3: <what> (recheck 2 findings 35, 36)`. Push after each commit.

### The edits

1. **`docs/decisions/ADR-0021-platform-401-and-403-automatic-fallback-and-its-limits.md`**
   - (a) **Finding 36.** Insert a new bullet directly after L60, the bullet that starts "A fallback ends when its cause does:". Text:

     "- A fallback also ends when its alternate's vendor flag is turned `off` (ADR-0050), since nothing is emitted while a flag is `off` (CONVENTIONS L388). A source in a source-level fallback returns to `blocked`, announced as `fallback_off` with reason `flag_off` (ADR-0014). Ops get the notice of a blocked source, and a client-owned property keeps the missing-grant card (above). A route in a route-wide fallback returns to `degraded`, and its green route reads it again. Turning the flag back on does not restart a fallback by itself: the usual entry conditions apply again (the user's answer of 9 Oct 2026, "Short fix first"). registry-writer applies the source-level change and source-health-canary the route-wide one."
   - (b) **Finding 35.** L60's list of overridden green selection lines ends with `yt-uploads-reconciler §5.1 L43`. Append `ig-hashtag-search §5.1 L45` and `§5.2 L64`, the green hashtag reader. Its jobs come from the shared scheduler with no health filter, and its step 2 returns only a `blocked` hashtag's job. Keep the list's punctuation consistent.
   - (c) If ADR-0021's Consequences bullet that names the F2 deliverables lists `source.events` reasons, add `flag_off` there. Otherwise skip this edit.
2. **`docs/decisions/ADR-0014-source-events-writer-shape-and-types.md`**
   - L36. Append to the bullet: " A `fallback_off` with reason `flag_off` ends a fallback whose alternate's vendor flag was turned `off` (ADR-0021)."
   - L27. In the example list of `reason` values, add `flag_off` after `client_removed`.
3. **`docs/decisions/ADR-0050-*.md`**
   - L31. After "While health is `fallback` and the flag is not `off`, a reader uses the alternate vendor in the vendor rows of `credentials` (ADR-0051; `source-health-canary §13 L152` reworded to "not `off`")", insert "; when the flag is turned `off`, the fallback ends (ADR-0021)". Keep the rest of the sentence.
4. **`docs/prds/_shared/CONVENTIONS.md`**
   - L240. Append at the end of the line: " A fallback also ends when its alternate's flag is turned `off`: a source returns to `blocked` and a route to `degraded` (ADR-0021)." CONVENTIONS is not reformatted, so keep everything on the same line.
5. **`docs/decisions/D2-SUMMARY.md`**
   - Insert a block after L253, the "Approve both" bullet, and before the blank line and "After the recheck of the D2 fix". Text:

     "After the second recheck (`docs/reviews/D2.md`, "Recheck 2, 9 Oct 2026", "For the user", point 1), the orchestrator asked the user on 9 Oct 2026 whether to settle, before merging, what happens when an alternate's vendor flag is turned `off` during a fallback. The user chose "Short fix first": turning the flag off ends the fallback; a source returns to `blocked`, with ops' notice and, for a client's own property, the missing-grant card; a route returns to `degraded`, and its green route reads it again (ADR-0021, ADR-0014, ADR-0050)."
   - In the D2-Q021 row of the table, append the clause "; a fallback ends when its alternate's flag is turned `off` (9 Oct 2026: "Short fix first"; ADR-0021)".
   - Run `make fmt` afterwards to re-pad the table.
6. **`docs/handoffs/D2.md`**
   - Insert a subsection "### The third D2 fix session (9 Oct 2026)" before L363, "### The review before the pull request". It holds a two-row table (finding, commit, what changed) for findings 35 and 36, the user's answer quoted, and the checks you ran.
   - In "For the sessions that depend on this" (from L111), add one bullet: C7 (registry-writer) and C12 (source-health-canary) end a fallback when its alternate's flag is turned `off`, and F2 adds `flag_off` to the closed `reason` list (ADR-0021, ADR-0014).

### Checks

- `grep -n "flag_off" docs/decisions/ADR-0014-*.md docs/decisions/ADR-0021-*.md docs/prds/_shared/CONVENTIONS.md docs/decisions/D2-SUMMARY.md` finds the new lines.
- `grep -c "ig-hashtag-search §5.1 L45" docs/decisions/ADR-0021-*.md` gives at least 1.
- `git diff --name-only 5410fb5 -- packages/contracts supabase/migrations clickhouse/migrations docs/contracts docs/reviews build-plan/sessions` prints nothing.
- `python3 build-plan/tools/validate.py` passes, and `gen_briefs.py` (`python3 build-plan/tools/gen_briefs.py . build-plan/tools/prd_index.json build-plan/tools/prd_io.json`) leaves `git status` clean.
- Start Docker and run `make bootstrap` (see "Cloud container"), then `make check`.
- Run `nvm use 24.21.0 >/dev/null && pnpm exec prettier --check` on the changed files under `docs/decisions/` and `docs/handoffs/`.
- Push, then read the check runs of your head over REST, read-only. A `make up` failure binding port 54322 is the known CI infrastructure problem.

### Finish

End with ORCHESTRATOR: DONE. Give:
- each edit with its commit;
- anything not applied, and why;
- the check results and the `make check` result;
- the pushed SHA.
