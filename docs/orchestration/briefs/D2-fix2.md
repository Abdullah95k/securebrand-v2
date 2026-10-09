# D2 second fix session: role and brief

Written by the orchestrator on 9 Oct 2026 for the D2 second fix session on `sb/D2` (pull request Abdullah95k/securebrand-v2#6). The session's system prompt names this file and its commit; it is part of that session's instructions.

## Role: fix, round 2 (D2 · Decisions and contract freeze)

The recheck in `docs/reviews/D2.md` (L233 onwards, at `c52dac6`) left 8 should-fix findings: 7 (the part still open) and 25 to 31. It also left 3 notes (32 to 34) and three points for the user. The user answered them on 9 Oct 2026, with "Only new videos", "Add a vendor reader" and "Approve both". The orchestrator verified each finding against the branch with a team of agents, and a critic merged their edits and resolved 15 conflicts. The result is the brief below; your job is to apply it carefully and completely.

Follow `.claude/skills/fix-session/SKILL.md`, adapted to a decision lane: there is no test to write first. Confirm each edit against the file before making it, matching its current text rather than its line number, and apply each file's edits from the bottom up.

### Rules

- **The brief is your scope.** Touch nothing it does not name, except its follow-on edits: counts, the handoff's new subsection, and the regenerated briefs.
- **The brief records the user's decisions.** Never add a decision the user has not made.
  - If an edit's current text is not in the file, apply its intent to the text that is there, and record it under "Applied with an adaptation".
  - If you believe an edit is wrong, do not apply it. Explain why with file and line evidence in the handoff, and list it in your final message.
- **Records.** Do not edit `docs/reviews/D2.md`. Leave each ADR's decision line (L3) and Source line unchanged.
- **Frozen paths.** Never touch the frozen contract paths the brief lists or `docs/contracts/*.md`. Never edit `build-plan/sessions/*.md` by hand.
- **Commits.** Commit one brief section at a time, as its "How to apply" step 6 says (section 0's edit goes with section 2). Use messages `D2 fix 2: <section title> (recheck findings <numbers>)`. Push after every commit.
- **Progress.** Keep a "Progress" line at the top of the handoff's new subsection, "The second D2 fix session (9 Oct 2026)", listing the sections applied with their SHAs, so a successor can continue if you are cut off.

### Finish

- Run `make bootstrap` first; Docker is needed (see "Cloud container").
- Run every check in the brief's last section, then `make check`, then `nvm use 24.21.0 >/dev/null && pnpm exec prettier --check` on the changed Markdown outside `docs/prds/` and `docs/contracts/`.
- Push, then read the check runs of your pushed head over REST, read-only. The `check` job sometimes fails in `make up` because the Supabase database cannot bind port 54322 on the GitHub runner. That is a known CI infrastructure problem; fix any other failure your changes cause.
- End with ORCHESTRATOR: DONE. Give:
  - each finding with its commit;
  - the edits you did not apply, and why;
  - the adaptations;
  - the check results;
  - the `make check` result;
  - the pushed SHA.

## 0. Orchestrator's additions (after the brief was compiled)

1. **The critic's new_decisions 1** (the lower bound of the vendor read after a client's TikTok revocation) is resolved as its option (a), which is what the brief already does:
   - ADR-0035 states only the user's rule: no video posted before the revocation is written, and the deleted ones stay deleted.
   - VTT4 chooses how to bound its read in its plan, and asks the user if its PRD and the ADRs leave the choice open.

   Do not write `health_changed_at` or any other mechanism into the ADRs.
2. **One consistency edit the critic found outside the findings.** Make it with section 2's ADR-0021 edits.
   - The problem: 20 PRDs select sources with `health != blocked`, and about 15 of them are green. So a green scheduler would also pick up a source in `fallback`.
   - Why it is not a decision: ADR-0021 L59 already implies the green route does not read a source during its fallback ("the source is read on its green route again" when the fallback ends).
   - The edit: complete ADR-0021 L59 by appending one sentence. "While a source is in `fallback`, its green route does not read it: the green schedulers' selection `health != blocked` also leaves out `fallback`, and those lines are overridden for it (ADR-0001): <list>."
   - The `<list>`: the green PRDs' selection lines, as `<service> §5.1 L<n>`. Find them with `grep -rn 'health != blocked' docs/prds`, and keep only the PRDs whose route class is green (the route line in each PRD's header). Cite the line numbers as at `origin/main`, as ADR-0021 L5 says.
   - Leave out the amber services: their selection follows finding 26's rule in the brief.
   - Record this edit under "Applied" in the handoff's new subsection, as "orchestrator addition, consistency with ADR-0021 L59".

---

## How to apply (the brief)

D2 second fix brief. Branch `sb/D2`, from `c52dac6`. It covers the recheck in `docs/reviews/D2.md` (L233 to L391: finding 7, the part still open, and findings 25 to 34) and the user's answers of 9 Oct 2026 to the recheck's three points ("Only new videos", "Add a vendor reader", "Approve both").

1. Match every edit on its **current** text. Line numbers are at `c52dac6` and only help you find the place. Where a table row is padded by Prettier, the current text is given without the padding: match the cell text.
2. Apply the edits bottom-up within each file. They are listed bottom-up, so the line numbers of the edits not yet applied stay true.
3. Never edit `packages/contracts`, `supabase/migrations`, `clickhouse/migrations` or `docs/contracts/*.md`. Never edit `docs/reviews/D2.md`: it is the record. Never edit `build-plan/sessions/*.md` by hand.
4. After the `build-plan/tools/sessions.py` edits, regenerate the briefs with `python3 build-plan/tools/gen_briefs.py . build-plan/tools/prd_index.json build-plan/tools/prd_io.json`. Only the F3, F4 and C4 briefs change.
5. Run `make fmt` after the edits. It re-pads the tables in `D2-SUMMARY.md`, `DEFERRED.md` and the handoff. `docs/prds/`, `build-plan/`, `CLAUDE.md` and `.claude/` are in `.prettierignore` and stay exactly as typed.
6. Commit one group per section below: 1 the record; 2 the ADRs and the decisions README; 3 CONVENTIONS; 4 the PRDs; 5 DEFERRED; 6 the kit; 7 the build plan, with the briefs regenerated; 8 the handoff. Then replace each `<commit>` in the handoff with the hash of the commit that made that change.
7. No edit here makes a new decision. Each one is the user's answer, an ADR's own rule completed, or a correction. If a current text does not match, or an edit would contradict an ADR or a user answer, stop and report it. If you apply an edit with a difference, record it under "Applied with an adaptation" in the new handoff subsection (8.2).

Every ADR edit that follows a user answer cites "the user's answer of 9 Oct 2026". Every CONVENTIONS, PRD, kit and build-plan edit cites its ADR in the text itself.

---

## 1. `docs/decisions/D2-SUMMARY.md`

### 1.1 L259, the D2-Q068 row, "Recorded as" cell (finding 29; ADR-0068)

Current:
~~~text
evaluation and Content Signals as recommended; training and media downloads follow a register of permitted uses, allowed unless an entry says "not allowed" (9 Oct 2026: "Allowed by default"), and seeded "not allowed" for every use a platform's terms or a vendor contract already forbids, so YouTube stays thumbnails only (ADR-0068)
~~~
Replacement:
~~~text
evaluation and Content Signals as recommended; training and media downloads follow a register of permitted uses, allowed unless an entry says "not allowed" (9 Oct 2026: "Allowed by default"), and seeded "not allowed" for every use a platform's terms or a vendor contract already forbids, so YouTube stays thumbnails only, and, as the user's own choice, for training on Facebook and Instagram content, client-owned Pages and accounts included, until the user or the compliance owner changes it (9 Oct 2026: "Start as not allowed") (ADR-0068)
~~~

### 1.2 L255, the D2-Q021 row, "Recorded as" cell, its end (finding 25; ADR-0035)

Current:
~~~text
(ADR-0021; the limits confirmed with that change on 9 Oct 2026)
~~~
Replacement:
~~~text
(ADR-0021; the limits confirmed with that change on 9 Oct 2026); after a client's TikTok revocation, the vendor reads only the videos the account posts after it (9 Oct 2026: "Only new videos"; ADR-0035)
~~~
The Facebook and Instagram request stays out of this table: it is a request, not a decision D2 records.

### 1.3 L253, the first row, "Recorded as" cell, its end (finding 34; ADR-0052, ADR-0021)

Current:
~~~text
both accepted by the user on 9 Oct 2026 (ADR-0035, ADR-0064)
~~~
Replacement:
~~~text
both accepted by the user on 9 Oct 2026 (ADR-0035, ADR-0064); and for D2-Q052, the recommended option except its (e), which no longer keeps a client's own property from the vendor once its green access is lost: the user's Q021 answers of 9 Oct 2026 let it fall back like any other source (ADR-0052, ADR-0021)
~~~

### 1.4 L249

Current:
~~~text
D2 recorded them as follows, the 9 Oct follow-up included,
~~~
Replacement:
~~~text
D2 recorded them as follows, the 9 Oct follow-ups included,
~~~

### 1.5 Insert six lines between L247 (ends "the client gets the missing-grant card (ADR-0007, ADR-0021).") and L248, the blank line before "D2 recorded them" (the user's answers of 9 Oct 2026, third set)

Insert, starting with a blank line:
~~~text

After the recheck of the D2 fix (`docs/reviews/D2.md`, "Recheck 9 Oct 2026", "For the user", points 1 to 3), the orchestrator put its three points to the user on 9 Oct 2026. The user chose, with these exact wordings:

- A client's own TikTok account after a revocation (the recheck's point 1, finding 25): "Only new videos". After a client revokes its TikTok Display grant and the `authorization_revoked` deletion, the vendor route reads only the videos the account posts after the revocation. Deleted videos stay deleted: the tombstones and store-writer's guard are unchanged. The source is not retired while a client that accepts amber watches it, and no government client watches it. Counsel can widen this later (the `tiktok_display` row of `DEFERRED.md` section 1). This narrows "Read it via vendor" above: the account's earlier videos are not read again (ADR-0021, ADR-0035).
- Client Facebook Pages and Instagram accounts (the recheck's point 2, finding 32): "Add a vendor reader". The user wants a new amber service that reads clients' own Facebook Pages and Instagram accounts through a vendor when their grant is lost. Building it is outside D2. It needs its own PRD, a vendor screen (owner and country, ADR-0051), its flag and a build-plan session, which the orchestrator plans after D2. D2 only records the request: in ADR-0021, where the alternates are listed; in `DEFERRED.md` section 3, as a row owned by the orchestrator, with the user (a new PRD session after D2); in the handoff; and here. Until that service exists, client Facebook Pages and Instagram accounts stay `blocked`, and the client gets the missing-grant card. Client YouTube channels were not part of the answer and stay `blocked` in v1.
- The kit files (the recheck's point 3, findings 30 and 31): "Approve both". The user approves the six further kit lines the D2 fix applied: `.claude/rules/services.md` L14, `.claude/skills/plan-session/SKILL.md` L26, `.claude/rules/python.md` L9, `.claude/rules/contracts.md` L11, `.claude/skills/contract-change/SKILL.md` L13 and `.claude/skills/decide-session/SKILL.md` L23 (ADR-0001, ADR-0002, ADR-0028, ADR-0067). Finding 30's replacement text is applied to `.claude/skills/review-session/SKILL.md` L17 and `.claude/agents/prd-reviewer.md` L13, so reviews read the same ADRs and `DEFERRED.md` rows as plans and briefs (ADR-0001).
~~~
L245 ("Read it via vendor") and L240 stay as written: they are the record of the earlier answers. The file grows from 261 to 267 lines.

---

## 2. The ADRs and `docs/decisions/README.md`

### 2.1 `ADR-0001-decisions-override-approved-prds.md` L40, the parenthesis after "each line citing this ADR" (finding 31; the user's answer of 9 Oct 2026)

Current:
~~~text
(the user's answer of 9 Oct 2026 to the D2 review's point 4, in the Answers section of `D2-SUMMARY.md`)
~~~
Replacement:
~~~text
(the user's answer of 9 Oct 2026 to the D2 review's point 4; for `.claude/rules/services.md` L14, `.claude/skills/plan-session/SKILL.md` L26 and the wording of `.claude/skills/review-session/SKILL.md` L17 and `.claude/agents/prd-reviewer.md` L13 that the recheck's finding 30 gives, the user's answer of 9 Oct 2026 to the recheck's point 3, "Approve both"; both in the Answers section of `D2-SUMMARY.md`)
~~~

### 2.2 `ADR-0010-individuals-identities-and-public-accounts.md` L63, the end of the bullet "Deletions reach these records:" (finding 28; keeps L63 matching C L256)

Current:
~~~text
and x-compliance-sync submits every X user id `poster_profiles` holds, as it submits `sources.platform_id` (ADR-0039).
~~~
Replacement:
~~~text
and x-compliance-sync submits every X user id `poster_profiles` holds, as it submits `sources.platform_id` (ADR-0039), and carries it in the deletion target's `user_ids`, so raw-archiver's rewrite also reaches the account's archived `profile` records (ADR-0035, ADR-0032).
~~~

### 2.3 `ADR-0021-platform-401-and-403-automatic-fallback-and-its-limits.md` (apply a, then b, then c)

**2.3a L74 (Consequences), its second sentence. This merges findings 26 and 25 (ADR-0001; the user's answer of 9 Oct 2026).**

Current:
~~~text
So are the alternates' exclusions of a client-owned source in `fallback`: `li-company-posts-poller §3 L26`, `§5.1 L41`; `tt-profile-videos-poller §3 L27`; `tg-channel-posts-poller §3 L28`.
~~~
Replacement:
~~~text
So are the alternates' exclusions of a client-owned source in `fallback`, in their scope and in their schedulers' selection: `li-company-posts-poller §3 L26`, `§5.1 L41`, `§13 L180`; `tt-profile-videos-poller §3 L27`, `§5.1 L41`; `tg-channel-posts-poller §3 L28`, `§5.1 L42`; each scheduler also selects the green rows in `fallback` that the Decision names. So are the lines that retire a client's TikTok account when its grant is revoked or expires, since a retired source is not polled (CONVENTIONS v1 L50) and so could not fall back: `tt-client-videos-fetcher §5.1 L43`, `§6.2 L115`, `§8 L131`. An expired grant leaves the account `blocked` or in `fallback`, as `§8 L130` and this ADR say; a revoked one is retired only as ADR-0035 says (the user's answer of 9 Oct 2026).
~~~
The PRD line numbers here use the numbering from before D2, as this ADR's Source line says. `§8 L131` is L135 today and `§8 L130` is L134; L43 and L115 have not moved. The expiry clause makes the ADR consistent with the user's earlier "Same as any source": a retired account could never fall back.

**2.3b Insert a new bullet between L56 (the route-wide bullet, ending "is kept, and only the canary sets it.") and L57 ("- Every automatic fallback, of one source or of a route, ..."). Finding 26 completes ADR-0021 L50 and L55.**

Insert:
~~~text
- An alternate reads a green source in `fallback`, whether the source or its route fell back, beside its own amber rows: its scheduler also selects every green row in `fallback` of a platform and source type it is the alternate for (the alternates named above, declared in `canary_targets`), a client-owned property included (the user's answer of 9 Oct 2026), under ADR-0052 (a)'s checks, as ig-keyword-search holds a green hashtag in fallback (`ig-keyword-search §5.1 L41`, `L45`; `ig-hashtag-search §8 L144`). The filters in its PRD that would exclude such a row (`route = amber`, its vendor, its source type, `owned_by_client = false`) do not apply to it. It keeps the row's due time in its own `cursors` row and writes neither `sources.last_polled_at` nor `next_poll_at`, which stay the primary poller's (ADR-0015, ADR-0041).
~~~

**2.3c L55, inside the client-owned bullet (finding 32; the user's answer of 9 Oct 2026; ADR-0051)**

Current:
~~~text
No amber service reads a Facebook Page, an Instagram account or a YouTube channel, so those stay `blocked`. Its vendor records take the amber visibility of ADR-0053,
~~~
Replacement:
~~~text
No amber service reads a Facebook Page, an Instagram account or a YouTube channel, so those stay `blocked`. The user has asked for a new amber service that reads clients' own Facebook Pages and Instagram accounts through a vendor when their grant is lost (the user's answer of 9 Oct 2026). It needs its own PRD, a vendor screen of its owner and country (ADR-0051), its flag and a build-plan session, which the orchestrator plans after D2 (`DEFERRED.md` section 3). Until that service exists, a client's Facebook Pages and Instagram accounts stay `blocked`, and its YouTube channels stay `blocked` in v1. A client-owned property's vendor records take the amber visibility of ADR-0053,
~~~
The file grows from 76 to 77 lines: the new bullet is L57, and L74 becomes L75.

### 2.4 `ADR-0035-deletions.md` (bottom-up)

**2.4a L45, "Sessions that must read this" (finding 25 routing; VTT4 is in the lane Fetch posts, which L4 names)**

Current: `TT1, VTT5, VTT6` → Replacement: `TT1, VTT4, VTT5, VTT6`

**2.4b L33, the first sentence of the paragraph, from "It also answers:" up to the space before "X `withheld` status comes from". Finding 25; the user's answer of 9 Oct 2026; ADR-0013, ADR-0021.**

Current:
~~~text
It also answers: A client's revocation of a TikTok Display grant deletes its items with reason `authorization_revoked`, one of the closed reasons (`tt-client-videos-fetcher §14 Q3`); it removes the `tiktok_display` records of that grant only; records a vendor route reads afterwards, under ADR-0021's fallback, are `vendor_agreed` and are not removed by it (the user's answer of 9 Oct 2026).
~~~
Replacement:
~~~text
It also answers: A client's revocation of a TikTok Display grant deletes its items with reason `authorization_revoked`, one of the closed reasons (`tt-client-videos-fetcher §14 Q3`); it removes the `tiktok_display` records of that grant only. Afterwards, under ADR-0021's fallback, the vendor route reads only the videos the account posts after the revocation (the user's answer of 9 Oct 2026): tt-profile-videos-poller writes no video the account posted before the revocation, and the records it writes are `vendor_agreed`, which the deletion does not remove. The deleted videos stay deleted: their tombstones outrank every content version, so store-writer drops any vendor version of them (the guard above, unchanged). The account is not retired while a client that accepts amber watches it and no government client does: tt-client-videos-fetcher requests `retire` (ADR-0013) for a revoked account only otherwise, and reads it on its green route again only after a new grant (ADR-0021). Counsel may widen the vendor read to the earlier videos (`DEFERRED.md` section 1).
~~~
How the poller bounds its read is not fixed here. VTT4 settles it in its plan (see new_decisions).

**2.4c L25, the sentence beginning "Target extras:" (finding 28; ADR-0010, ADR-0039, ADR-0032, ADR-0069)**

Current:
~~~text
Target extras: `fetched_before`, `countries`, and `user_ids` for registered X sources only (an individual is targeted by `author_ref`, ADR-0010).
~~~
Replacement:
~~~text
Target extras: `fetched_before`, `countries`, and `user_ids` for registered X sources and for every other X account whose `poster_profiles` row holds its id, public accounts included (ADR-0010, ADR-0039), so that deletion-propagator finds the account's archived `profile` records by that id, as it finds parked raw records (`deletion-propagator §5.3 L64`), and has raw-archiver rewrite them within X's 24 hours (ADR-0032, ADR-0069); an ordinary individual is targeted by `author_ref` only (ADR-0010).
~~~

### 2.5 `ADR-0049-tier-lifecycle-and-push-coverage.md` L29 (finding 34; ADR-0021, ADR-0015; the user's answer of 9 Oct 2026)

Current:
~~~text
(a bot channel's is tg-bot-channel-receiver, the only service that rotates it)
~~~
Replacement:
~~~text
(a bot channel's is tg-bot-channel-receiver; in a fallback, tg-channel-posts-poller reads a public one as its alternate and writes only its own `cursors` row, ADR-0015, ADR-0021, the user's answer of 9 Oct 2026)
~~~

### 2.6 `ADR-0052-amber-data-and-client-consent.md` L22, option 1's parenthesis (finding 27; the user's answer of 9 Oct 2026)

Current:
~~~text
(chosen, with ADR-0021's automatic fallback of a blocked client-owned property)
~~~
Replacement:
~~~text
(chosen, with ADR-0021's automatic fallback of a client-owned property once its green access is lost, of the one source or of its route; the user's answer of 9 Oct 2026)
~~~
The option's bold title stays: it is the option's name in D2-PROPOSALS.

### 2.7 `ADR-0068-ai-and-media-use-of-platform-content.md` (bottom-up; finding 29; the user's answer of 9 Oct 2026)

**2.7a L62 (Why), its last sentence**

Current:
~~~text
seeding it with every use a recorded term or contract forbids keeps the default from breaking a known rule.
~~~
Replacement:
~~~text
seeding it with every use a recorded term or contract forbids keeps the default from breaking a known rule. Training on Facebook and Instagram content starts "not allowed" as the user's own choice, not a known rule, until the user or the user's compliance owner changes it (the user's answer of 9 Oct 2026).
~~~

**2.7b L58, the whole bullet**

Current:
~~~text
- F3 seeds a "not allowed" row, with its clause, for every use a platform's terms or a vendor contract already forbids as recorded in CONVENTIONS and the ADRs: YouTube, downloading video and downloading audio (YouTube's terms forbid downloading video without its prior written permission, above); Facebook and Instagram, training (Meta's Tech Provider "processes only on behalf of its client", CONVENTIONS v1 L163, which a model shared by all clients does not do, as option 1 (b) reads it; Instagram Public Content Access allows only "aggregated, de-identified output", v1 L171). A row is added as each further term or contract is read and found to forbid a use, such as each vendor contract and the Disqus terms counsel reads (`DEFERRED.md` section 1); news hosts are excluded by `ai-train = no` at run time, not by rows.
~~~
Replacement:
~~~text
- F3 seeds a "not allowed" row, with its clause, for every use a platform's terms or a vendor contract already forbids as recorded in CONVENTIONS and the ADRs: YouTube, downloading video and downloading audio (YouTube's terms forbid downloading video without its prior written permission, above). F3 also seeds Facebook and Instagram, training, "not allowed", client-owned Pages and accounts included. Those two rows are the user's own choice, not uses a recorded term forbids: their clause is the user's answer of 9 Oct 2026, "Start as not allowed", and the user or the user's compliance owner may change them like any other row. A row is added as each further term or contract is read and found to forbid a use, such as each vendor contract and the Disqus terms counsel reads (`DEFERRED.md` section 1); news hosts are excluded by `ai-train = no` at run time, not by rows.
~~~

**2.7c L57, the clause on the clause column**

Current:
~~~text
the terms or contract clause relied on, and who set it and when.
~~~
Replacement:
~~~text
the terms or contract clause relied on (for a row that records the user's own choice, that answer), and who set it and when.
~~~

**2.7d L32**

Current:
~~~text
The register is seeded with a "not allowed" row for every use a platform's terms or a vendor contract already forbids (below).
~~~
Replacement:
~~~text
The register is seeded with a "not allowed" row for every use a platform's terms or a vendor contract already forbids, and with "not allowed" rows for training on Facebook and Instagram content, the user's own choice (the user's answer of 9 Oct 2026; below).
~~~

### 2.8 `ADR-0069-legal-policies-for-deletions-and-audits.md` L27, item (e) (finding 28; ADR-0035, ADR-0032)

Current:
~~~text
X's `user_ids` arrive as X sends them and travel in the deletion target only so the archives can be searched (`x-compliance-sync §5.3 L81`);
~~~
Replacement:
~~~text
X's `user_ids` (a registered source's, or one a `poster_profiles` row holds, ADR-0035) arrive as X sends them and travel in the deletion target only so the archives can be searched, the account's archived `profile` records included (ADR-0032; `x-compliance-sync §5.3 L81`);
~~~

### 2.9 `docs/decisions/README.md` L7, its second sentence (finding 34; ADR-0001, cited in the same paragraph)

Current:
~~~text
Every session an ADR names in "Sessions that must read this" is also reached by its "Applies to" line, by ID, service, platform, lane or "all".
~~~
Replacement:
~~~text
Every session an ADR names in "Sessions that must read this" is also reached by its "Applies to" line, by ID, service, platform, lane or "all", or, for F4 to F6, by `listening-sdk`, the SDK they build.
~~~

---

## 3. `docs/prds/_shared/CONVENTIONS.md` (bottom-up; every edit stays within its line)

### 3.1 L322, the TikTok Display API bullet: append (finding 25; ADR-0035)

Current:
~~~text
and is read through a vendor only in ADR-0021's automatic fallback, never reconciled through one (ADR-0021, ADR-0024, ADR-0049, ADR-0052).
~~~
Replacement:
~~~text
and is read through a vendor only in ADR-0021's automatic fallback, never reconciled through one (ADR-0021, ADR-0024, ADR-0049, ADR-0052). After a revocation and its `authorization_revoked` deletion, the account is not retired while a client that accepts amber watches it and no government client does, and the vendor reads only the videos it posts after the revocation; the deleted videos stay deleted (ADR-0035).
~~~

### 3.2 L258 (finding 29; ADR-0068)

Current:
~~~text
A use is allowed by default; the register is seeded with a "not allowed" row for every use a platform's terms or a vendor contract already forbids (training on Facebook and Instagram content; downloading YouTube video and audio); and `ai-train = no` always excludes a host.
~~~
Replacement:
~~~text
A use is allowed by default; the register is seeded with a "not allowed" row for every use a platform's terms or a vendor contract already forbids (downloading YouTube video and audio), and with "not allowed" rows for training on Facebook and Instagram content, client-owned Pages and accounts included, as the user's own choice, which the user or the user's compliance owner may change (ADR-0068); and `ai-train = no` always excludes a host.
~~~

### 3.3 L256, its last sentence (finding 28; ADR-0035, ADR-0032)

Current:
~~~text
and x-compliance-sync submits every X user id `poster_profiles` holds, beside `sources.platform_id` (ADR-0039).
~~~
Replacement:
~~~text
and x-compliance-sync submits every X user id `poster_profiles` holds, beside `sources.platform_id` (ADR-0039), and carries it in the deletion target's `user_ids`, so raw-archiver's rewrite reaches the account's archived `profile` records (ADR-0035, ADR-0032).
~~~

### 3.4 L239, after its first sentence (finding 26; ADR-0021)

Current:
~~~text
and a watching client accepts amber; otherwise the source stays `blocked`. A client-owned property falls back under the same conditions
~~~
Replacement:
~~~text
and a watching client accepts amber; otherwise the source stays `blocked`. The alternate's scheduler also selects a green source while its `health = fallback`, beside its own amber rows, as ig-keyword-search does for a green hashtag (ADR-0021). A client-owned property falls back under the same conditions
~~~

### 3.5 L13, the AMBER definition (finding 27; ADR-0052, ADR-0021)

Current:
~~~text
and a client's own properties are read through a vendor only in the automatic fallback of a blocked source (ADR-0052, ADR-0021).
~~~
Replacement:
~~~text
and a client's own properties are read through a vendor only in ADR-0021's automatic fallback, of the one source or of its route (ADR-0052, ADR-0021).
~~~

---

## 4. The PRDs (finding 7; `docs/prds/` is not reformatted, so keep the indentation shown)

Each new ULID is valid Crockford base32 and starts with 0. Its time part is the example's own event time. Its random part is the first 10 bytes of SHA-256 over a stated input (ADR-0006 L30). All of them were checked by decoding them back.

### 4.1 `docs/prds/facebook/fb-backfill.md` (bottom-up)

a. Insert a note between L109 (blank, after the closing fence at L108) and L110. Current:
~~~text
Also `source.events` `updated` (with `backfill_status`)
~~~
Replacement:
~~~text
Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

Also `source.events` `updated` (with `backfill_status`)
~~~
b. L102 (ADR-0005 L27 and L29; the intro at L88 cites ADR-0005). Current: `    "batch": "raw/green/facebook/2026/10/06/fb-backfill/000007.jsonl.zst",` → Replacement: `    "raw_ref": "raw/green/facebook/2026/10/06/fb-backfill/000007.jsonl.zst#4",`

c. L98 (ADR-0006; time 2026-10-06T11:00:00Z, the window's end). Current: `    "job_id": "01J9N3A1C7Q2W8E5R4T6Y9U0I3", "attempt": 2,` → Replacement: `    "job_id": "01M48DXKW00GHZSJPM5NRWV7R3", "attempt": 2,`

### 4.2 `docs/prds/facebook/fb-page-search.md` (ADR-0006 L42; outside the review's list, same class)

a. Insert a note between L118 (blank) and L119. Current: `Also `service_runs`, `dlq.fb-page-search`.` (start of L119) → Replacement:
~~~text
Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

Also `service_runs`, `dlq.fb-page-search`.
~~~
b. L114 (time 06:30:00Z). Current: `  "job_id": "01J9P7K2H9D4F1G6S8A3L5Z0QX",` → Replacement: `  "job_id": "01M47YF7J0TMKPRYDBNVW3319Z",`

### 4.3 `docs/prds/shared/analysis-sentiment.md` L94 (note at L114; time 09:15:12Z, its `produced_at`)

Current: `  "message_id": "01J9W4Z6D3N8P2Q4R5S6T7U8V9",` → Replacement: `  "message_id": "01M487XQ80XCWC8XCQWNVDW2FK",`

### 4.4 `docs/prds/shared/poster-resolver.md` L91 (note at L94; time 10:13:58Z, `resolved_at`)

Current: `"message_id":"pp:instagram:17841400000000000:2026-10-06T10:13:58Z"` → Replacement: `"message_id":"01M48B9AKGZPWZF64KVNV761WS"`

### 4.5 `docs/prds/shared/qualifier.md` L84 (note at L87), two replacements on the line

- `"message_id":"dec:01J9Z..."` → `"message_id":"01M48BA9VGH96Q50HZX9S88TJC"` (time 10:14:30Z, its `produced_at`)
- `"decision_id":"01J9Z..."` → `"decision_id":"01M48B9AKGRHAJW420WYJS5QK3"` (time 10:13:58Z, the profile's `resolved_at`, per qualifier L117)

### 4.6 `docs/prds/shared/registry-writer.md` L95 (note at L98), two replacements on the line

- `"message_id":"se:7f1c...:added"` → `"message_id":"01M48BAKM0NCCYDSZEC6V1PKHV"` (time 10:14:40Z, the event's `at`)
- `"decision_id":"01J9Z..."` → `"decision_id":"01M48B9AKGRHAJW420WYJS5QK3"` (the same decision as qualifier's example)

### 4.7 `docs/prds/shared/source-health-canary.md` L152, AC 6 (ADR-0051 L31, ADR-0050; C L430)

Current:
~~~text
6. TikHub `degraded` with a clean EnsembleData canary and `TT_VENDOR_ROUTE` not `off` yields `fallback_on` for every TikTok source; with the flag `off` the route stays `degraded` (ADR-0050).
~~~
Replacement:
~~~text
6. EnsembleData, the primary, `degraded` with a clean canary on TikHub, the fallback once its owner is verified, and `TT_VENDOR_ROUTE` not `off` yields `fallback_on` for every TikTok source; with the flag `off` the route stays `degraded` (ADR-0050, ADR-0051).
~~~

### 4.8 `docs/prds/web/search-hit-router.md` (bottom-up; ADR-0036 L25 and L37 name "the router's test and prose")

a. L190, AC 4. Current:
~~~text
4. A news URL on a registered domain yields one `article.urls` message with that site's `source_id` and `idempotency_key = news:article:<canonical_url_hash>`; a second sighting yields none.
~~~
Replacement:
~~~text
4. A news URL on a registered domain yields one `article.urls` message with that site's `source_id`, `found_via = web_search` and no article key (ADR-0036); a second sighting yields none.
~~~
b. L165. Current:
~~~text
- Idempotency: `message_id` is deterministic (`dh:…:<candidate_key>:<canonical_url_hash>`, `au:…:<canonical_url_hash>`); `article.urls` carries `news:article:<canonical_url_hash>`.
~~~
Replacement:
~~~text
- Idempotency: `message_id` is deterministic, a ULID derived as ADR-0006 describes from `candidate_key` and `canonical_url_hash` on `discovery.hits` and from `canonical_url_hash` on `article.urls` (ADR-0002); `article.urls` carries no article key, which the extractor derives from the page's canonical URL (ADR-0036).
~~~
c. L125: delete the whole line `  "idempotency_key": "news:article:sha256:9c1e4b…",`. ADR-0036 L25 says "the router's `idempotency_key` goes"; the note is at L136.

d. L124. Current: `  "message_id": "au:search-hit-router:sha256:9c1e4b…",` → Replacement: `  "message_id": "01M47KA7QGHFH4KH2ZXEXBBCCA",`

e. L104. Current: `  "message_id": "dh:search-hit-router:instagram:example_creator_iq:sha256:5d18c2…",` → Replacement: `  "message_id": "01M47KA7QGXC5Q420EVYV9KKZ5",`

### 4.9 `docs/prds/web/web-commoncrawl-scanner.md` (ADR-0006 L42; outside the review's list, a composite)

a. Insert a note between L102 (blank, after the fence at L101) and L103. Current: `The field set beyond `type`, `platform` and `candidate_key`` (start of L103) → Replacement:
~~~text
Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

The field set beyond `type`, `platform` and `candidate_key`
~~~
b. L89 (time 2026-10-09T02:14:55Z, its `produced_at`). Current: `  "message_id": "dh:web-commoncrawl-scanner:news:example-daily.iq:CC-MAIN-2026-38",` → Replacement: `  "message_id": "01M4F72A8REMR4FEX05GZTT6JA",`

### 4.10 Left as written (ADR-0001; no ADR names them)

poster-resolver L121, the web engines' idempotency lines, web-commoncrawl-scanner L132, the `sha256:` prefixes in the examples' `canonical_url_hash`, the `del:…` prefixes of `deletion_id`, source-health-canary L47, L88 and L102, and the other `"batch"` envelopes.

### 4.11 `docs/prds/youtube/yt-text-purger.md` (bottom-up; ADR-0006 L42)

a. Insert a note between L178 (blank, after the retention_audit example's closing fence at L177) and L179. This example's `run_id` is corrected below and had no note. Current: `Verification runs without `FINAL` so that superseded versions count.` (start of L179) → Replacement:
~~~text
Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).

Verification runs without `FINAL` so that superseded versions count.
~~~
b. L152 and L165: replace every `01J9P9C6E2G8J4L0N5Q1S7U3WY` with `01M47F0V80FZGG928KMD5XX36J` (time 02:00:00Z, the run's `started_at`). `parent_run_id` `01J9P8A3V5N7B2D4F6H0K1M9QS` is valid and stays.

---

## 5. `docs/decisions/DEFERRED.md` (bottom-up; run `make fmt` afterwards)

### 5.1 Section 3: a new row after L78 ("| The session that builds the n8n flows (ADR-0067); I2 is the nearest fit | the orchestrator | …"). Finding 32; the user's answer; ADR-0021, ADR-0051.

Insert:
~~~text
| A new amber service that reads clients' own Facebook Pages and Instagram accounts through a vendor when their grant is lost, asked for by the user on 9 Oct 2026 (ADR-0021): its own PRD, a vendor screen of owner and country (ADR-0051), its flag and a build-plan session. Until it exists, those properties stay `blocked` and the client gets the missing-grant card; client YouTube channels stay `blocked` in v1 | the orchestrator, with the user (a new PRD session after D2) | after D2 |
~~~
Section 3 then has 30 rows.

### 5.2 L60 (finding 34; ADR-0008 L11)

Current: ``as `normalize-item §9 L146` does`` → Replacement: ``as `normalize-item §5.2 L50` (the key) and `§9 L146` (mappers in `listening-sdk`) do``

### 5.3 L45, the first cell of the `permitted_uses` row; the second cell is unchanged (finding 29; ADR-0068)

Current:
~~~text
The register of permitted uses, `permitted_uses` (ADR-0068), reviewed by the user or the user's compliance owner: the "not allowed" rows F3 seeds for the uses a platform's terms or a vendor contract already forbid, and a row for any further use a term or contract forbids (such as a vendor contract counsel reads, section 1)
~~~
Replacement:
~~~text
The register of permitted uses, `permitted_uses` (ADR-0068), reviewed by the user or the user's compliance owner: the "not allowed" rows F3 seeds, for the uses a platform's terms or a vendor contract already forbid and for training on Facebook and Instagram content, the user's own choice of 9 Oct 2026 ("Start as not allowed"), and a row for any further use a term or contract forbids (such as a vendor contract counsel reads, section 1)
~~~

### 5.4 L25, the `tiktok_display` row: replace the whole row (finding 25; the user's answer of 9 Oct 2026; ADR-0035, ADR-0021, ADR-0054)

Current, without padding:
~~~text
| `tiktok_display`: kept while the client's authorisation lasts, deleted on revocation, and that after a client's revocation the account's public videos may be read again through the vendor route (ADR-0021) | as stated (ADR-0054) | before TikTok's go-live (G3) and production (G4) | TT1, C14 |
~~~
Replacement:
~~~text
| `tiktok_display`: kept while the client's authorisation lasts and deleted on revocation; and whether, after a client's revocation, the vendor route may also read the videos the account posted before it (counsel may widen it, the user's answer of 9 Oct 2026) | as stated (ADR-0054); after a revocation the vendor route reads only the videos posted after it, and the deleted ones stay deleted (ADR-0035, ADR-0021) | before TikTok's go-live (G3) and production (G4) | TT1, VTT4, C14; if counsel widens it, also F4, C6 and C13 (the version formula and the tombstone guard) |
~~~

### 5.5 L14 to L21, the eight vendor rows: two replace-all edits (finding 34; ADR-0068 L57 and L58, ADR-0054)

- Column "Reading to confirm", 8 occurrences. `the contract's limit on keeping vendor data` → `the contract's limit on keeping vendor data, and any use it forbids (training on its data; downloading images, audio or video), which becomes a "not allowed" row of `permitted_uses` (ADR-0068)`
- Column "Default built now", 8 occurrences. `ten years where the contract allows it, otherwise the contract's limit (ADR-0054)` → `ten years where the contract allows it, otherwise the contract's limit (ADR-0054); every use allowed until its row says "not allowed" (ADR-0068)`

Row counts after this section: 26, 10, 30 and 191.

---

## 6. The kit (`.claude/` is not reformatted). Findings 30 and 31; ADR-0001; the user's answer of 9 Oct 2026, "Approve both"

### 6.1 `.claude/skills/review-session/SKILL.md` L17, the whole line

Current:
~~~text
The brief (`ls build-plan/sessions/$0-*`), the PRD, the ADRs in `docs/decisions/` whose "Applies to" line names this service, its platform, its lane or "all" (an ADR wins over the PRD, ADR-0001), `docs/plans/$0.md` and `docs/handoffs/$0.md`. Then run `git fetch origin` and read the diff with `git diff origin/main...HEAD`. Worktrees branch from the remote's main, so a local `main` may be stale and show other sessions' merged work.
~~~
Replacement:
~~~text
The brief (`ls build-plan/sessions/$0-*`), the PRD, the ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (an ADR wins over the PRD, ADR-0001), the rows of `docs/decisions/DEFERRED.md` that name this session, `docs/plans/$0.md` and `docs/handoffs/$0.md`. Then run `git fetch origin` and read the diff with `git diff origin/main...HEAD`. Worktrees branch from the remote's main, so a local `main` may be stale and show other sessions' merged work.
~~~

### 6.2 `.claude/agents/prd-reviewer.md` L13, the whole line

Current:
~~~text
1. Read the session brief in `build-plan/sessions/`, the PRD it names (sections 5, 6, 8, 12 and 13 above all), the ADRs whose "Applies to" line names its service, platform, lane or "all" (an ADR wins over the PRD, ADR-0001), and the relevant parts of `docs/prds/_shared/CONVENTIONS.md`.
~~~
Replacement:
~~~text
1. Read the session brief in `build-plan/sessions/`, the PRD it names (sections 5, 6, 8, 12 and 13 above all), the ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (an ADR wins over the PRD, ADR-0001), the rows of `docs/decisions/DEFERRED.md` that name this session, and the relevant parts of `docs/prds/_shared/CONVENTIONS.md`.
~~~
The recheck's text begins "and the rows of …". In both lines it sits inside a list that already ends with "and …", so its leading "and" is dropped. This is the same kind of adaptation as the first fix's 5.

The six further kit lines (services.md L14, plan-session L26, python.md L9, contracts.md L11, contract-change L13, decide-session L23) stay as they are. They are now approved.

---

## 7. The build plan: `build-plan/tools/sessions.py` (bottom-up), then regenerate

### 7.1 L197, the C4 trap (finding 33; ADR-0008; DEFERRED L60)

Current: `MAPPERS.md names the one place, agreed with F4, before wave 3 (DEFERRED.md section 3)"], critical=True),`
Replacement: `MAPPERS.md names the one place, decided from F4's handoff, before wave 3 (DEFERRED.md section 3)"], critical=True),`

### 7.2 L99, the F4 trap (finding 33; ADR-0008)

Current:
~~~text
         "ADR-0008's mapper registry, keyed (service, api_version), is in listening-sdk; agree with C4 where producers' mappers sit (DEFERRED.md section 3)",
~~~
Replacement:
~~~text
         "ADR-0008's mapper registry, keyed (service, api_version), is in listening-sdk; record in your handoff where the registry sits in the package and how a mapper registers in it, so that C4 can decide from it where producers' mappers sit (DEFERRED.md section 3)",
~~~

### 7.3 L88, the F3 `permitted_uses` trap (finding 29; ADR-0068)

Current:
~~~text
         "Seed `permitted_uses` with the 'not allowed' rows ADR-0068 lists (YouTube video and audio downloads; Facebook and Instagram training), each with its clause: a missing row means allowed, so only the seed keeps a forbidden use out (ADR-0068)"],
~~~
Replacement:
~~~text
         "Seed `permitted_uses` with the 'not allowed' rows ADR-0068 lists (YouTube video and audio downloads; Facebook and Instagram training), each with its clause: YouTube's terms for the two downloads; for Facebook and Instagram training, the user's own choice, the user's answer of 9 Oct 2026 ('Start as not allowed'). A missing row means allowed, so only the seed keeps an excluded use out (ADR-0068)"],
~~~

### 7.4 Regenerate

Run `python3 build-plan/tools/gen_briefs.py . build-plan/tools/prd_index.json build-plan/tools/prd_io.json`, then `python3 build-plan/tools/validate.py`. Only `build-plan/sessions/F3-control-plane-schema.md`, `F4-sdk-runtime.md` and `C4-normalize-item.md` change.

---

## 8. `docs/handoffs/D2.md` (bottom-up; run `make fmt` afterwards)

### 8.1 L279 (finding 34; ADR-0049)

Current: ``(`51c948b` and `07aed6f` (F5 names it where several services rotate one source type).`` — match from `` `51c948b` ``.
Replacement:
~~~text
`51c948b` and `07aed6f` (which left the source types several services rotate to F5; the user's answer of 9 Oct 2026 named their primaries instead, in ADR-0049 and CONVENTIONS' primary-poller table, and the F5 row of `DEFERRED.md` was deleted).
~~~

### 8.2 Insert the second fix session's record after L271, the blank line after the first fix's checks; L272 "### The review before the pull request" follows it after one blank line

Insert:
~~~text
### The second D2 fix session (9 Oct 2026)

The recheck (`docs/reviews/D2.md`, "Recheck 9 Oct 2026", at `c52dac6`) found 0 blockers, 8 should-fix findings (finding 7, still open in part, and findings 25 to 31) and 3 notes (32 to 34). The user answered its three points on 9 Oct 2026 (`D2-SUMMARY.md`, "Answers"). The second fix session applied the orchestrator's second fix brief, one commit per group of files. It did not edit `docs/reviews/D2.md`. Line numbers in this subsection are at its final commit. CONVENTIONS keeps its `12070ac` numbers, since every edit to it stayed within a line.

#### The recheck's findings

| # | Rank | Finding | Fixed in |
| --- | --- | --- | --- |
| 7 | should-fix | PRD examples whose ids broke ADR-0006 under a note saying they follow it, and two edited passages that kept an overridden rule | ULIDs in registry-writer L95, qualifier L84, poster-resolver L91, search-hit-router L104 and L124, analysis-sentiment L94, yt-text-purger L152 and L165, fb-page-search L114 and web-commoncrawl-scanner L89, with a note where one was missing; the router's article key, its prose and AC 4 (ADR-0036); source-health-canary AC 6 (ADR-0051); fb-backfill's `job_id`, `raw_ref` and note (`<commit>`) |
| 25 | should-fix | "Read it via vendor" could not work as recorded | the user's answer "Only new videos": ADR-0035 L33 and L45, ADR-0021 L75 (`<commit>`); CONVENTIONS L322 (`<commit>`); the `tiktok_display` row of `DEFERRED.md` section 1 (`<commit>`); `D2-SUMMARY.md` (`<commit>`); "Choices" and "For the sessions that depend on this" above (`<commit>`) |
| 26 | should-fix | The alternates never selected a client-owned source in fallback | ADR-0021 L57 (new) and L75 (`<commit>`); CONVENTIONS L239 (`<commit>`); "For the sessions that depend on this" above (`<commit>`) |
| 27 | should-fix | CONVENTIONS limited the vendor read of a client's property to a blocked source | CONVENTIONS L13 (`<commit>`); ADR-0052 L22 (`<commit>`) |
| 28 | should-fix | An X deletion could not reach a public account's archived profile | ADR-0035 L25, ADR-0069 L27, ADR-0010 L63 (`<commit>`); CONVENTIONS L256 (`<commit>`); the C2, C13 and X7 paragraph above (`<commit>`) |
| 29 | should-fix | Facebook and Instagram training was recorded as forbidden by the platforms' terms | ADR-0068 L32, L57, L58, L62 (`<commit>`); CONVENTIONS L258 (`<commit>`); `DEFERRED.md` section 2 (`<commit>`); `D2-SUMMARY.md`, the D2-Q068 row (`<commit>`); the F3 trap, with the briefs regenerated (`<commit>`); "Decisions made here", the F3 list and the user's action 4 above (`<commit>`) |
| 30 | should-fix | Reviews selected fewer ADRs than plans and briefs | the user's answer "Approve both": review-session L17 and prd-reviewer L13 (`<commit>`); ADR-0001 L40 (`<commit>`) |
| 31 | should-fix | Six kit lines rested on an approval the record did not show | the user's answer "Approve both": `D2-SUMMARY.md` and ADR-0001 L40 (`<commit>`); "Kit rewordings", the progress list, finding 24's row and the answers above (`<commit>`) |
| 32 | note | Client Facebook Pages, Instagram accounts and YouTube channels stay blocked | the user's answer "Add a vendor reader", recorded as a request: ADR-0021 L55 (`<commit>`); a `DEFERRED.md` section 3 row (`<commit>`); `D2-SUMMARY.md` (`<commit>`); "Open items" above (`<commit>`) |
| 33 | note | The F4 trap asked F4 to agree with C4, which starts only after F4 merges | the F4 and C4 traps, with the briefs regenerated (`<commit>`) |
| 34 | note | Records and wording | the line-number note under "The review's findings" and the history lines on C L105 and the F5 row (`<commit>`); `docs/decisions/README.md` L7 and ADR-0049 L29 (`<commit>`); `D2-SUMMARY.md`, the first row of its table (`<commit>`); `DEFERRED.md` L14 to L21 and L60, and the user's action 6 (`<commit>`) |

#### The user's answers after the recheck (9 Oct 2026)

- "Only new videos", for a client's own TikTok account after a revocation (the recheck's point 1, finding 25). After the `authorization_revoked` deletion, the vendor reads only the videos the account posts after the revocation. The tombstones and store-writer's guard, unchanged, keep the deleted videos out. The account is not retired while a client that accepts amber watches it and no government client does, and counsel may widen the read. ADR-0035 L33 records it, and L45 names VTT4. ADR-0021 L75 names `tt-client-videos-fetcher §5.1 L43`, `§6.2 L115` and `§8 L131` (L135 today) as overridden. It is also in CONVENTIONS L322, the `tiktok_display` row of `DEFERRED.md` section 1 and `D2-SUMMARY.md` (`<commit>`).
- "Add a vendor reader", for client Facebook Pages and Instagram accounts (the recheck's point 2, finding 32). It is recorded as a request, not built: ADR-0021 L55, a `DEFERRED.md` section 3 row owned by the orchestrator with the user, `D2-SUMMARY.md` and "Open items" above (`<commit>`). Until the service exists, those properties stay `blocked` and the client gets the missing-grant card. Client YouTube channels stay `blocked` in v1.
- "Approve both", for the kit (the recheck's point 3, findings 30 and 31). The six further kit lines of 5d (`ade0626`) are approved, and the recheck's text replaced `.claude/skills/review-session/SKILL.md` L17 and `.claude/agents/prd-reviewer.md` L13 (`<commit>`). `D2-SUMMARY.md` and ADR-0001 L40 record it (`<commit>`).

#### Applied with an adaptation

<Each edit applied with a difference from the brief's text, with the reason; or "None.">

#### Checks run on the final commit

<One bullet per command of the brief's section 9, with its output.>

~~~
Fill in the two placeholder sections with what actually happened, and replace every `<commit>`.

### 8.3 L263 (finding 34; ADR-0066, ADR-0040)

Current:
~~~text
and CONVENTIONS L105 ("pre-allocated by the sender for a client-owned property or a news site") predates D2.
~~~
Replacement:
~~~text
and CONVENTIONS L105 ("pre-allocated by the sender for a client-owned property or a news site") came with D2's CONVENTIONS v1.1 (`bf8f416`); it says who allocates a `source_id` (ADR-0066, ADR-0040), not how a property is read.
~~~

### 8.4 L242 (finding 31)

Current:
~~~text
- "Accept all three", review points 2 to 4: findings 3, 4, 8 and 9 above, and the further kit lines of 5d (`ade0626`).
~~~
Replacement:
~~~text
- "Accept all three", review points 2 to 4: findings 3, 4, 8 and 9 above. The further kit lines of 5d (`ade0626`) had no answer behind them until the user approved them after the recheck ("Approve both", in the second fix session's record below).
~~~

### 8.5 L239, append to the "Read it via vendor" bullet (finding 25)

Current: ``F2's list (`50f5611`).`` (end of L239) → Replacement:
~~~text
F2's list (`50f5611`). Narrowed after the recheck: "Only new videos", in the second fix session's record below.
~~~

### 8.6 L233, finding 24's "Fixed in" cell (finding 31)

Current: ``decide-session L23, approved under 5d (`ade0626`);`` → Replacement: ``decide-session L23, applied under 5d (`ade0626`) and approved by the user after the recheck ("Approve both");``

### 8.7 Insert a note under L206 "#### The review's findings", before the table (finding 34; ADR-0049)

Current:
~~~text
#### The review's findings

| #   | Rank
~~~
Replacement:
~~~text
#### The review's findings

CONVENTIONS line numbers in this table, in "The user's answers of 9 Oct 2026" and in "Applied with an adaptation" are at `387d844`, as the fix brief gave them: from L136 on, CONVENTIONS at `12070ac` is 28 lines longer (the primary-poller table, ADR-0049), so L228 here is L256 there. "Checks run on the final commit" uses `12070ac` numbers.

| #   | Rank
~~~
L238 ("CONVENTIONS L82, L230") and L253 ("CONVENTIONS L230") stay as they are: under this note they are correct.

### 8.8 L201 (finding 31)

Current: ``- Section 5, the kit (`CLAUDE.md` and `.claude/`), with the lines of 5d the user approved: `ade0626`.``
Replacement: ``- Section 5, the kit (`CLAUDE.md` and `.claude/`), with the further lines of 5d, which the user approved after the recheck ("Approve both", 9 Oct 2026): `ade0626`.``

### 8.9 Open items: a new bullet after L186 ("- The session that builds the n8n flows is not assigned; …"). Finding 32; ADR-0021, ADR-0051.

Insert:
~~~text
- The amber reader of clients' own Facebook Pages and Instagram accounts, which the user asked for on 9 Oct 2026 ("Add a vendor reader"), has no PRD, vendor screen, flag or session yet. The orchestrator plans it with the user after D2 (ADR-0021, ADR-0051; `DEFERRED.md` section 3). Until it exists, those properties stay `blocked` when their grant is lost and the client gets the missing-grant card; client YouTube channels stay `blocked` in v1.
~~~

### 8.10 L185 (the file's count after 5.1)

Current: `29 questions for the build sessions` → Replacement: `30 questions for the build sessions`. L254 and L268 are the first fix's record and stay.

### 8.11 L173, its second sentence (finding 31; ADR-0001, ADR-0002, ADR-0028, ADR-0067)

Current:
~~~text
It also applied the further lines you approved: `.claude/rules/services.md` L14 and `.claude/skills/plan-session/SKILL.md` L26 (ADR-0001), `.claude/rules/python.md` L9 (ADR-0028), `.claude/rules/contracts.md` L11 and `.claude/skills/contract-change/SKILL.md` L13 (ADR-0002), and `.claude/skills/decide-session/SKILL.md` L23, the n8n flows (ADR-0067).
~~~
Replacement:
~~~text
It also applied six further lines, which you approved after the recheck (your answer of 9 Oct 2026 to its point 3, "Approve both"): `.claude/rules/services.md` L14 and `.claude/skills/plan-session/SKILL.md` L26 (ADR-0001), `.claude/rules/python.md` L9 (ADR-0028), `.claude/rules/contracts.md` L11 and `.claude/skills/contract-change/SKILL.md` L13 (ADR-0002), and `.claude/skills/decide-session/SKILL.md` L23, the n8n flows (ADR-0067). On the same answer, the second fix session replaced `.claude/skills/review-session/SKILL.md` L17 and `.claude/agents/prd-reviewer.md` L13 with the recheck's text (its finding 30), so reviews read the ADRs and `DEFERRED.md` rows that plans and briefs read (ADR-0001).
~~~

### 8.12 L151, the user's action 6 (finding 34; ADR-0068; `DEFERRED.md` section 1)

Current: `   - each vendor contract's limit, before that vendor's probe;` → Replacement: `   - each vendor contract's limit, and any training or download it forbids, before that vendor's probe;`

### 8.13 L147, the user's action 4 (finding 29; ADR-0068, already cited at the end of the line)

Current:
~~~text
The register starts with a "not allowed" row for each use the platforms' terms already forbid: downloading YouTube video and audio, and training on Facebook and Instagram content.
~~~
Replacement:
~~~text
The register starts with "not allowed" rows for downloading YouTube video and audio, which YouTube's terms forbid, and for training on Facebook and Instagram content, client-owned Pages and accounts included, which is your own choice ("Start as not allowed"), not a rule recorded from the platforms' terms.
~~~

### 8.14 "For the sessions that depend on this": insert two paragraphs after L137 (the blank line after the D3 paragraph), before L138 "## For the user". Findings 28, 26 and 25.

Insert:
~~~text
C2, C13 and X7: an X user result is an author-scope deletion whose target carries the user's id in `user_ids` when the user is a registered source or a `poster_profiles` row holds the id, public accounts included; deletion-propagator removes the account's items, and finds its archived `profile` records by that id and has raw-archiver rewrite them, within X's 24 hours (ADR-0035, ADR-0039, ADR-0032, ADR-0069).

TT1, VTT4, VTG3 and VLI3: an alternate's scheduler also selects every green source in `fallback` of a platform and source type it is the alternate for, a client-owned property included, beside its own amber rows, and keeps that source's due time in its own `cursors` row (ADR-0021, ADR-0015). After a client revokes its TikTok grant, tt-client-videos-fetcher retires the account only when no client that accepts amber watches it or a government client does, and tt-profile-videos-poller writes no video the account posted before the revocation; the deleted videos stay deleted (ADR-0035).

~~~

### 8.15 L126, the F3 list's `permitted_uses` clause (finding 29; ADR-0068)

Current:
~~~text
each with its clause, such as YouTube's video and audio downloads and training on Facebook and Instagram content (ADR-0068);
~~~
Replacement:
~~~text
each with its clause, such as YouTube's video and audio downloads (YouTube's terms) and training on Facebook and Instagram content (the user's answer of 9 Oct 2026) (ADR-0068);
~~~

### 8.16 "Choices this session made in recording them": a new bullet after L85, the X `withheld` bullet (finding 25; ADR-0021, ADR-0035)

Insert:
~~~text
- ADR-0021 names as overridden the tt-client-videos-fetcher lines that retired a client's TikTok account on revocation or expiry (`§5.1 L43`, `§6.2 L115`, `§8 L131`), since a retired account is never polled and so could not fall back as the user's Q021 answers require. Under the user's answer of 9 Oct 2026, "Only new videos", a revoked account is retired only when no client that accepts amber watches it or a government client does, and the vendor then reads only the videos it posts after the revocation (ADR-0035). How tt-profile-videos-poller keeps to that bound is VTT4's to settle in its plan.
~~~

### 8.17 L75, the ADR-0068 bullet (finding 29; ADR-0068; the user's answer of 9 Oct 2026)

Current:
~~~text
and F3 seeds a "not allowed" row for every use a platform's terms or a vendor contract already forbids, such as YouTube's video and audio downloads and training on Facebook and Instagram content.
~~~
Replacement:
~~~text
and F3 seeds a "not allowed" row for every use a platform's terms or a vendor contract already forbids, such as YouTube's video and audio downloads, and "not allowed" rows for training on Facebook and Instagram content, client-owned Pages and accounts included. Those rows are the user's own choice rather than a rule recorded from the terms, and the user or the user's compliance owner may change them (the user's answer of 9 Oct 2026, "Start as not allowed").
~~~

### 8.18 L65

Current: `with the user's follow-ups of 9 Oct 2026 on Q021, Q068 and the review's points` → Replacement: `with the user's follow-ups of 9 Oct 2026 on Q021, Q068, the review's points and the recheck's points`

---

## 9. Checks

Run on the final commit. Set `E='docs/reviews/D2.md\|docs/decisions/D2-PROPOSALS.md'` first.

**Must print nothing:**

- `grep -rnF "for registered X sources only" docs build-plan CLAUDE.md .claude | grep -v "$E"`
- `grep -rnF "automatic fallback of a blocked" docs build-plan CLAUDE.md .claude | grep -v "$E"`
- `grep -rnF "may be read again" docs build-plan CLAUDE.md .claude | grep -v "$E" | grep -v "docs/decisions/D2-SUMMARY.md:245:"`. L245 is the record of the earlier answer.
- No line may say the platforms' terms forbid Facebook and Instagram training: `grep -rn "already forbid" docs build-plan CLAUDE.md .claude | grep -v "$E" | grep -i "facebook\|instagram" | grep -v "own choice"`
- `grep -rnF -e "as option 1 (b) reads it" -e "platforms' terms already forbid" -e "Facebook and Instagram content; downloading" docs build-plan | grep -v "$E"`
- `grep -rnF -e "the only service that rotates it" -e "predates D2" -e "F5 names it" docs | grep -v "$E"`
- `grep -rnF -e 'names this service, its platform, its lane or "all"' -e 'names its service, platform, lane or "all"' .claude`
- `grep -rnF -e "agree with C4" -e "agreed with F4" build-plan`
- ``grep -nF 'normalize-item §9 L146` does' docs/decisions/DEFERRED.md``
- `grep -nF -e "further lines you approved" -e "lines of 5d the user approved" -e "approved under 5d" docs/handoffs/D2.md`
- `grep -rnoE '"(message_id|decision_id)": ?"[^"]*"' docs/prds | grep -vE '": ?"0[0-9A-HJKMNP-TV-Z]{25}"'`
- `grep -rnoE '\b0[0-9A-Z]{25}\b' docs/prds | grep -E ':[^:]*[ILOU][^:]*$'`
- `grep -nF "news:article" docs/prds/web/search-hit-router.md`; `grep -nF '"batch"' docs/prds/facebook/fb-backfill.md`; `grep -nF "6. TikHub" docs/prds/shared/source-health-canary.md`
- `git diff --name-only origin/main...HEAD -- packages/contracts supabase/migrations clickhouse/migrations docs/contracts`
- Run the recheck's old-rule sweep again (`docs/reviews/D2.md` L296: the 18 patterns, over `docs/`, `build-plan/`, `CLAUDE.md` and `.claude/`, with `$E` excluded). Every hit must be one of the kinds listed at L298 to L301, with ADR-0021 L58 now at L59. None may be a line this fix wrote.

**Counts and content:**

- Rows per `DEFERRED.md` section (one table each): `for s in 1 2 3 4; do awk -v s="## $s." 'index($0,s)==1{f=1;next} /^## /{f=0} f && /^\| /{n++} END{print s, n-2}' docs/decisions/DEFERRED.md; done` prints 26, 10, 30 and 191.
- `grep -c "any use it forbids" docs/decisions/DEFERRED.md` prints 8.
- `grep -rc "Ids in this example follow ADR-0006" docs/prds | awk -F: '{s+=$2} END{print s}'` prints 29 (25 before, plus fb-backfill, fb-page-search, web-commoncrawl-scanner and yt-text-purger's second example).
- `wc -l` prints 77 for ADR-0021, 267 for `D2-SUMMARY.md` and 286 for `DEFERRED.md`.
- `grep -c "Only new videos\|Add a vendor reader\|Approve both" docs/decisions/D2-SUMMARY.md docs/handoffs/D2.md` is non-zero for both files. `grep -n "new amber service" docs/decisions/ADR-0021-*.md docs/decisions/DEFERRED.md` prints ADR-0021 L55 and the new section 3 row.
- The alternates agree: `grep -n "tt-profile-videos-poller\|tg-channel-posts-poller\|li-company-posts-poller" docs/decisions/ADR-0021-*.md docs/decisions/ADR-0049-*.md docs/prds/_shared/CONVENTIONS.md`. Read each hit. Every one must name the same three alternates (a TikTok account, a public Telegram channel, and a LinkedIn page only if LI0 finds the activity URN), with Facebook Pages, Instagram accounts and YouTube channels `blocked`.
- The new ULIDs decode to their event times: `python3 -I -c 'import sys,datetime;A="0123456789ABCDEFGHJKMNPQRSTVWXYZ"` then, on the next line, `[print(u,datetime.datetime.fromtimestamp((sum(A.index(c)*32**i for i,c in enumerate(reversed(u)))>>80)/1000,datetime.timezone.utc).isoformat()) for u in sys.argv[1:]]' 01M48BAKM0NCCYDSZEC6V1PKHV 01M48B9AKGRHAJW420WYJS5QK3 01M48BA9VGH96Q50HZX9S88TJC 01M48B9AKGZPWZF64KVNV761WS 01M47KA7QGXC5Q420EVYV9KKZ5 01M47KA7QGHFH4KH2ZXEXBBCCA 01M487XQ80XCWC8XCQWNVDW2FK 01M47F0V80FZGG928KMD5XX36J 01M47YF7J0TMKPRYDBNVW3319Z 01M4F72A8REMR4FEX05GZTT6JA 01M48DXKW00GHZSJPM5NRWV7R3`. The expected times on 2026-10-06 are 10:14:40, 10:13:58, 10:14:30, 10:13:58, 03:15:02, 03:15:02, 09:15:12, 02:00:00, 06:30:00, then 2026-10-09T02:14:55, then 2026-10-06T11:00:00, all UTC.
- Routing: `grep -n "lane Fetch posts" build-plan/sessions/VTT4-*.md` prints one line, so ADR-0035's "Applies to" reaches VTT4, which its "Sessions that must read this" line now names.

**Tools:**

- `python3 build-plan/tools/gen_briefs.py . build-plan/tools/prd_index.json build-plan/tools/prd_io.json` prints `briefs 125`. A second run changes nothing (`git status --short build-plan` is clean after commit). The build-plan commit changes only `sessions.py` and the F3, F4 and C4 briefs.
- `python3 build-plan/tools/validate.py` prints `sessions 125 services assigned 86 missing []` and `errors []`, and exits 0.
- `make fmt` exits 0, and a second run changes no file.
- `make check` passes.
- Prettier's check on the changed Markdown outside `docs/prds/` and `docs/contracts/`: `nvm use 24.21.0 >/dev/null && git diff --name-only origin/main...HEAD -- '*.md' ':!docs/prds' ':!docs/contracts' | xargs pnpm exec prettier --check` prints "All matched files use Prettier code style!"
- `POLICY_BRANCH=sb/D2 make policy` passes.

Record each command and its output in the handoff's new "Checks run on the final commit" (8.2).
