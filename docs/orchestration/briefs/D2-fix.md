# D2 fix session: role and brief

Written by the orchestrator on 9 Oct 2026 for the D2 fix session on `sb/D2` (pull request Abdullah95k/securebrand-v2#6). The session's system prompt names this file and its commit; it is part of that session's instructions.

## Role: fix (D2 · Decisions and contract freeze)

The independent review, `docs/reviews/D2.md` at `387d844`, found 0 blockers, 14 should-fix findings and 10 notes. The user then ruled on its open points on 9 Oct 2026. The orchestrator verified every finding against the branch with a team of agents, swept every place the user's two changed answers (Q021 and Q068) touch, and had a critic resolve 27 conflicts between the proposed edits. The result is the fix brief below. Your job is to apply it, carefully and completely.

Follow `.claude/skills/fix-session/SKILL.md`, adapted to a decision lane. D2 has almost no code, so there is no test to write first. Instead:
- Confirm each edit against the file before making it. Match the edit's quoted current text, not its line number.
- Apply each file's edits from the bottom up, as the brief's "How to apply" says.

### Rules

- **The brief is your scope.** Touch nothing it does not name, except the follow-on edits it asks for: counts, the handoff's Review section and regenerated briefs.
- **The brief records the user's decisions.** Never add a decision the user has not made.
  - If an edit's current text is not in the file, apply the edit's intent to the text that is there and note it in the handoff's Review section.
  - If you believe an edit is wrong (it contradicts an ADR, the user's answers or another edit), do not apply it. Explain why with file and line evidence in the handoff's Review section, and list it in your final message. The orchestrator takes it to the user.
- **Changed decisions.** Every edit to an ADR's Decision section that follows a 9 Oct answer cites "the user's answer of 9 Oct 2026" (`D2-SUMMARY.md`, "Answers"). Leave each ADR's decision line (L3) and Source line unchanged.
- **Records.** Do not edit `docs/reviews/D2.md`. The recheck session appends to it.
- **Frozen paths.** Never touch the frozen contract paths the brief lists, or `docs/contracts/*.md`. Never edit `build-plan/sessions/*.md` by hand; regenerate them with the generator command the brief gives.
- **Commits.** Commit one brief section at a time (sections 0 and 1 together, then 2, 3, 4, 5, 6 and 7), with messages `D2 fix: <section title> (review findings <numbers>)`. Push after every commit, so the work survives a cut-off.
- **Progress.** Keep a "Progress" note at the top of the handoff's Review section: which sections are applied, with their SHAs. If you are cut off, a successor session continues from it.

### Finish

- Run `make bootstrap` first; Docker is needed (see "Cloud container").
- Run every check in the brief's section 8, then `make check`, then `nvm use 24.21.0 >/dev/null && pnpm exec prettier --check` on the changed Markdown files outside `docs/prds/` and `docs/contracts/`.
- Update the Review section of `docs/handoffs/D2.md`. List each review finding (1 to 24) and each sweep item with its fixing commit, or the reason it was not applied, and add the 9 Oct answers to the handoff where the brief says.
- Push, then read the check runs of your pushed head over REST, read-only. The `check` job sometimes fails in `make up` because the Supabase database cannot bind port 54322 on the GitHub runner. That is a known CI infrastructure problem, not yours to fix. Any other failure your changes cause, fix.
- End with ORCHESTRATOR: DONE. Give:
  - each finding and sweep group with its commit;
  - the edits you did not apply, and why;
  - the section 8 check results;
  - the `make check` result;
  - the pushed SHA.

### The fix brief



# D2 fix brief

Branch `sb/D2` at `387d844`. Every line number is at that commit.

## How to apply

- Match every edit on its quoted current text, not its line number. Apply the edits in each file from the bottom up: insertions in DEFERRED.md, CONVENTIONS and the handoff shift later lines.
- Edits marked **[N#]** depend on that `needs_user` answer. They are written for the recommended option; change them if the user answers otherwise.
- Never touch the frozen paths: `packages/contracts`, `supabase/migrations`, `clickhouse/migrations`, `docs/contracts/*.md`.
- Never edit `build-plan/sessions/*.md` by hand.
- When done, run:
  - `make fmt` (Prettier formats `docs/decisions/` and `docs/handoffs/`, and realigns the tables);
  - `python3 build-plan/tools/gen_briefs.py . build-plan/tools/prd_index.json build-plan/tools/prd_io.json` (expect `briefs 125`);
  - `python3 build-plan/tools/validate.py`;
  - the checks in section 8.

Standard notes, referred to by name below:

- **NOTE-ID**: `Ids in this example follow ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).`
- **NOTE-ID2**: `Ids in this example follow ADR-0002 and ADR-0006; where its other fields differ from an ADR, the ADR wins (ADR-0001).`
- **NOTE-RCV**: ``Ids in this example follow ADR-0006: a ULID `job_id` made at receipt, with `attempt = 1`, and the delivery id in `context` (ADR-0005). Where its other fields differ from an ADR, the ADR wins (ADR-0001).``

"Add NOTE-x after Ln" means: keep the closing fence at Ln, then add a blank line and the note.

---

## 0. The user's answers to the [N#] markers (9 Oct 2026, after this brief was drafted)

The orchestrator put the brief's open points to the user. Every answer is the recommended option, so every edit marked **[N#]** is applied as written, with the additions below. Record these answers in `D2-SUMMARY.md` as part of the 9 Oct follow-up of section 1: add the lines below to the end of that inserted block, before L227's text.

~~~
Asked again on 9 Oct 2026 about the consequences of these answers, the user chose, with these exact wordings:

- Client-owned properties in fallback: "Same as any source". A client-owned property falls back when any client watching it accepts amber data and no government client watches it, even if its owner does not accept amber; the owner then receives nothing from the vendor. While it is in fallback, its vendor-read posts are amber `pool` data: they reach every accepting client whose rules match, not only the owner (ADR-0021, ADR-0052, ADR-0053).
- A client's own TikTok revocation: "Read it via vendor". After a client revokes its TikTok Display grant and the `authorization_revoked` deletion TikTok's terms require, the account's public videos may be read again through the vendor route, where an accepting client watches it and no government client does. Counsel is told when it confirms the `tiktok_display` reading (ADR-0021, ADR-0035, ADR-0054; `DEFERRED.md` section 1).
- Training on Facebook and Instagram content: "Start as not allowed". The register of permitted uses is seeded "not allowed" for training on Facebook and Instagram content, client-owned Pages and accounts included; the user or the compliance owner may change it (ADR-0068).
- Two technical points: "Accept both". The primary poller of a news site is the poller of its first surface in the order feed, sitemap, homepage: news-feed-poller if the site has a feed, else news-sitemap-poller, else news-homepage-differ; the primary poller of a web keyword rule is web-search-mojeek (ADR-0049). A client's LinkedIn page falls back through li-company-posts-poller only if LI0 finds the activity URN on the green LinkedIn API; otherwise it stays `blocked` and the client gets the missing-grant card (ADR-0007, ADR-0021).
~~~

How each marker is resolved:

- **[N1]**, answer (a) for both. Replace the two "named by F5" cells in the new CONVENTIONS primary-poller table:
  - News site: `news-feed-poller if the site has a feed, else news-sitemap-poller, else news-homepage-differ (ADR-0049)`.
  - Web keyword rule: `web-search-mojeek (ADR-0049)`.

  Then:
  - Replace ADR-0049 L29's last sentence with the same rule, citing the user's answer of 9 Oct 2026 (`D2-SUMMARY.md`, "Answers").
  - Delete DEFERRED.md section 3's L52 row.
  - Drop the F5 clause from the handoff's L121.
  - Section 4's "Section 3, L52" edit becomes "delete the row".
- **[N2]**, answer (a), as the brief has it.
- **[N3]**, confirmed as written. No extra edit beyond the D2-SUMMARY lines above.
- **[N4]**, answer (a). Add two minimal edits:
  1. In ADR-0035, next to the `authorization_revoked` reason, add: "it removes the `tiktok_display` records of that grant only; records a vendor route reads afterwards, under ADR-0021's fallback, are `vendor_agreed` and are not removed by it (the user's answer of 9 Oct 2026)".
  2. In DEFERRED.md section 1's `tiktok_display` row (L18), add to the question for counsel: "and that after a client's revocation the account's public videos may be read again through the vendor route (ADR-0021)".

  In the handoff's F2 deliverables, add a short clause that the `authorization_revoked` deletion is scoped to `tiktok_display` records (ADR-0035).
- **[N5]**, answer (a). Apply the Meta texts at every **[N5 (a)]** marker. These are the critic's texts, verbatim:
  - In ADR-0068's new seed bullet, after "(YouTube's terms forbid downloading video without its prior written permission, above)", insert `; Facebook and Instagram, training (Meta's Tech Provider "processes only on behalf of its client", CONVENTIONS v1 L163, which a model shared by all clients does not do, as option 1 (b) reads it; Instagram Public Content Access allows only "aggregated, de-identified output", v1 L171)`.
  - In ADR-0068 L41, append `Facebook and Instagram are seeded "not allowed", client-owned Pages and accounts included.`
  - In ADR-0068 L65, after "from every source the register does not exclude", insert ` (Facebook and Instagram stay out while their seeded rows stand)`.
  - In CONVENTIONS L230, DEFERRED L37, handoff L75, L113 and L134, and the sessions.py F3 trap, add "training on Facebook and Instagram content" beside "YouTube video and audio downloads".
- **[N6]**, approved. The user's answer to the review's point 4 covers "the kit's rule and skill files" generally: "Accept all three", with the fix session updating CLAUDE.md and the kit's rule and skill files so that sessions follow the ADRs. Apply section 5d, and name the further lines in the handoff's kit bullet (section 7).
- **The critic's new_decisions 2 and 3** are already resolved in the brief:
  - D3 owns the order of the register's screen, so it is left to D3.
  - The government exclusion reads "A green source a government client watches never falls back, whoever owns it."

Counts: deleting DEFERRED's L52 row changes the section 3 count. After all edits, count the rows of DEFERRED.md sections 1 to 4 from the file itself. Use those numbers in the handoff's L164 and in section 8's check, instead of the brief's 26, 10, 30 and 191.

---

## 1. The record (finding 13; rulings 1, 2 and 5)

### docs/decisions/D2-SUMMARY.md

**L3**

Current:
~~~
Status: **answered by the user on 7 Oct 2026** (see "Answers" at the end)
~~~
Replace:
~~~
Status: **answered by the user on 7 Oct 2026, with follow-ups on 9 Oct 2026** (see "Answers" at the end)
~~~

**Insert after L225** (`- Q059: "Maximum history". This is option 3.`), before L227:
~~~

On 9 Oct 2026 the orchestrator put two of its own readings and the D2 review's open points back to the user. The two readings were relayed to the user on 7 Oct 2026 and recorded in ADR-0021 and ADR-0068, but not written in this section:

- the limits on Q021's automatic switching: a 401 or 403 classified by reason; a blocked source falling back to its vendor where that route's flag is on; never for a government-watched green source or a client-owned property; an n8n notice to ops for every automatic fallback;
- for Q068, a register of permitted uses for training and downloads, whose entries the user or the user's compliance owner sets. ADR-0068 recorded every entry as "not allowed" until set.

The review's points are in `docs/reviews/D2.md`, "For the user", points 2 to 6. The user chose, with these exact wordings:

- Q021: "Make client page to be read through the scrapper as well". The limits are confirmed except the client-owned exclusion. A client's own pages and accounts (client-owned properties) also fall back to the vendor (amber) route automatically when green access is lost, under the same conditions as any other source. A government-watched green source still never switches, and ops still get an n8n notice for every automatic fallback (ADR-0021).
- Q068: "Allowed by default". In the register of permitted uses, a use (training on a source's content; downloading its images, audio or video) is allowed unless the register says it is not, and `ai-train = no` still always excludes a host. The orchestrator reads the 7 Oct words "if it does not break any rules" to mean that the register is seeded with "not allowed" rows for every use a platform's terms or a vendor contract already forbids. YouTube's terms forbid downloading video, so YouTube stays thumbnails only (ADR-0068).
- Review points 5 and 6: "Keep both until counsel". Rollups of a single YouTube channel are kept 36 months (ADR-0056), and Instagram creator accounts are not listed (ADR-0010), both until counsel answers (`DEFERRED.md` section 1).
- Review points 2, 3 and 4: "Accept all three":
  - X `withheld` status comes from the daily compliance run, and ADR-0035 says it departs from `D2-PROPOSALS.md` L1120 and L2397;
  - the X reply hand-back keeps `window_start` on `replies` jobs, and ADR-0064 marks it as phase 2's technical choice for X5 to confirm;
  - the D2 fix session applies the review's replacement texts for `CLAUDE.md`, `.claude/rules/services.md` L12 and the review, plan and reviewer skills.
~~~

**L227**

Current:
~~~
D2 phase 2 recorded them as follows, one ADR per decision (ADR-nnnn records D2-Qnnn):
~~~
Replace:
~~~
D2 recorded them as follows, the 9 Oct follow-up included, one ADR per decision (ADR-nnnn records D2-Qnnn):
~~~

**L231**, second cell of the first table row. This replaces the optional new rows that items 3 and 4 suggested, so no count changes.

Current:
~~~
the recommended option, as written in `D2-PROPOSALS.md`
~~~
Replace:
~~~
the recommended option, as written in `D2-PROPOSALS.md`; for D2-Q035, the option's rule that X `withheld` status comes from the daily compliance run (L1108), not its contradicting answer (L1120, L2397), and for D2-Q064, the X replies hand-back by `window_start`, phase 2's technical choice for X5 to confirm, both accepted by the user on 9 Oct 2026 (ADR-0035, ADR-0064)
~~~

**L233**, the D2-Q021 row. Match on the cell text.

Replace:
~~~
| D2-Q021 | option 3 with limits: a 401 or 403 classified by reason, and a blocked source, a client-owned property included, falling back to its vendor automatically where that route's flag is on, never for a government-watched green source, with an n8n notice to ops (ADR-0021; the limits confirmed with that change on 9 Oct 2026) |
~~~

**L237**, the D2-Q068 row.

Replace:
~~~
| D2-Q068 | evaluation and Content Signals as recommended; training and media downloads follow a register of permitted uses, allowed unless an entry says "not allowed" (9 Oct 2026: "Allowed by default"), and seeded "not allowed" for every use a platform's terms or a vendor contract already forbids, so YouTube stays thumbnails only (ADR-0068) |
~~~

### ADR-0021 L11 (ruling 5)

Current: the whole paragraph `The user's answer, 7 Oct 2026: "Q021 automatic switching should be considered." The orchestrator put the limits below to the user, who approved them as the answer: … and route-wide states from the canary only.`

Replace:
~~~
The user's answer, 7 Oct 2026: "Q021 automatic switching should be considered." The limits below were the orchestrator's reading of that answer, relayed to the user on 7 Oct 2026: option 3, a 403 classified by reason first, option 1's two levels, automatic fallback wherever the route's vendor flag is on except for government-watched green sources and client-owned properties, an n8n notice to ops for every automatic fallback, and route-wide states from the canary only. On 9 Oct 2026 the user confirmed them with one change: "Make client page to be read through the scrapper as well". A client-owned property now also falls back to its vendor route automatically when green access is lost, under the same conditions as any other source. A government-watched green source still never switches, and ops still get an n8n notice for every automatic fallback (`D2-SUMMARY.md`, "Answers", the follow-up of 9 Oct 2026).
~~~

Leave the decision line (L3) and the Source line unchanged.

### ADR-0068 L11 (ruling 5; the review said L12, but L12 is blank)

Current: the whole paragraph `The user's answer, 7 Oct 2026: "Q068 we will download … use it for training as well." The orchestrator relayed it as: … whose entries the user or the user's compliance owner sets.`

Replace:
~~~
The user's answer, 7 Oct 2026: "Q068 we will download some of the content and if it does not break any rules then we will use it for training as well." The register was the orchestrator's reading of that answer, relayed to the user on 7 Oct 2026: evaluation sets as (a) and Content Signals as (c), as proposed; training and downloads governed by a register of permitted uses, whose entries the user or the user's compliance owner sets, each "not allowed" until set. On 9 Oct 2026 the user changed its default: "Allowed by default". A use (training on a source's content; downloading its images, audio or video) is allowed unless the register says it is not, and `ai-train = no` still always excludes a host. The orchestrator reads the 7 Oct words "if it does not break any rules" to mean that the register is seeded with "not allowed" rows for every use a platform's terms or a vendor contract already forbids. YouTube's terms forbid downloading video, so YouTube stays thumbnails only (`D2-SUMMARY.md`, "Answers", the follow-up of 9 Oct 2026).
~~~

Leave L3 and L5 unchanged (Q068-1 is dropped).

---

## 2. The ADRs, in number order

### ADR-0001 (finding 8; ruling 4a)

**Insert a bullet after L39** (`- D2 edits a PRD line only where an ADR names the edit, …`):
~~~
- The kit follows this rule, each line citing this ADR (the user's answer of 9 Oct 2026 to the D2 review's point 4, in the Answers section of `D2-SUMMARY.md`): `CLAUDE.md` L43, L48 and L58; `.claude/skills/review-session/SKILL.md` L17, L21 and L22; `.claude/agents/prd-reviewer.md` L13 and L15; `.claude/skills/plan-session/SKILL.md` L17, L25 and L30; `build-plan/README.md` L9, L36, L37 and L41; `build-plan/templates/REVIEW.md` L24 and L27; the routing line of `build-plan/tools/gen_briefs.py`. Sessions, plans and reviews read PRD sections 5, 8, 10 and 13 as amended by the ADRs that apply, and they follow a conflict an ADR settles and name it in the plan, without asking the user again.
~~~
**[N6]**: if the user approves, add `.claude/rules/services.md` L14 and plan-session L26 to the list.

### ADR-0004 L29 (finding 19)

Current:
~~~
`discovery.hits` and `poster.profiles` by `candidate_key` (ADR-0031, ADR-0033), as are
~~~
Replace:
~~~
`discovery.hits` and `poster.profiles` by `candidate_key` (ADR-0031, ADR-0033; an ordinary individual's answer on `poster.profiles` by `author_ref`, ADR-0033), as are
~~~

### ADR-0005

**L4** (finding 12)

Current: `normalize-item, and the lanes`

Replace: `normalize-item, backfill-orchestrator, comment-decay-scheduler, and the lanes`

**L28**, end of the bullet (finding 6f)

Current:
~~~
on a comment, `parent_id`, `root_id` and the optional `redacted_fields`, as ADR-0009 defines them.
~~~
Replace:
~~~
on a comment, `parent_id`, `root_id` and the optional `redacted_fields`, as ADR-0009 defines them; `redacted_fields` is optional on any record, comments included (ADR-0009).
~~~

### ADR-0006 L42 (finding 7a)

Current:
~~~
- PRD examples that show other id formats (`cl_17`, `kw_0412`, `job_…`, composites, `null`) are example errors; the formats above win under ADR-0001, approved PRDs included.
~~~
Replace:
~~~
- PRD examples that show other id formats (`cl_17`, `kw_0412`, `job_…`, UUID and dated job ids, composites, `null`, ULIDs as deletion `item_ids`) are corrected in this pull request, approved PRDs among them under ADR-0001, each corrected example citing this ADR.
~~~

### ADR-0008 L4 (finding 12)

Current: `raw-archiver, and the lanes`

Replace: `raw-archiver, poster-resolver, and the lanes`

### ADR-0009 (finding 12)

**L4**

Current: `ig-webhook-receiver, and the lanes`

Replace: `ig-webhook-receiver, tg-bot-channel-receiver, the probes FB0, VFB0, VIG0 and VLI0, and the lanes`

**L42**

Current: `N8, TG1, TG2.`

Replace: ``N8, TG1, TG2, and the probes FB0, VFB0, VIG0 and VLI0 (creation times, above; `DEFERRED.md`).``

### ADR-0010

**Insert after L62** (the `saved` bullet), before L63 `- D3 specifies the lists` (finding 1):
~~~
- Deletions reach these records: `poster_profiles`, `public_accounts_dim` and `client_lists` are in the SDK purge registry, so an author-scope deletion, from an author's request or an X compliance result, removes the account's rows (ADR-0035, ADR-0069), and x-compliance-sync submits every X user id `poster_profiles` holds, as it submits `sources.platform_id` (ADR-0039).
~~~

**Insert after L88** (the `CLAUDE.md` L10 bullet, which stays) (finding 24):
~~~
- The review check follows it, citing this ADR: in `.claude/skills/review-session/SKILL.md` L25, "private individuals keyed (`author_ref`), never profiled, listed or backfilled, and only public accounts listed (ADR-0010)" replaces "individuals hashed".
~~~

### ADR-0011 L26 (finding 4)

Current: ``a `replies` job on `jobs.x-full-archive-search` also carries `window_start`, ADR-0059);``

Replace: ``a `replies` job on `jobs.x-full-archive-search` also carries `window_start`, ADR-0059, ADR-0064);``

### ADR-0012 L34 (finding 2)

Current:
~~~
`rematch` (also on a keyword change), `recompute`. A request touching a post's schedule
~~~
Replace:
~~~
`rematch` (also on a keyword change), `recompute`. It also writes a client's deletion request, about data held only for that client, as a `deletions` message with reason `client_request`, built through the SDK (ADR-0035, ADR-0054). A request touching a post's schedule
~~~

### ADR-0013

**L4** (finding 12)

Current: `yt-text-purger, listening-sdk,`

Replace: `yt-text-purger, quota-governor, keyword-matcher, backfill-orchestrator, listening-sdk,`

**L39** (ruling 1)

Current:
~~~
on every route-wide change it enforces ADR-0021's exclusions (government-watched green sources and client-owned properties never move to a vendor).
~~~
Replace:
~~~
on every route-wide change it enforces ADR-0021's exclusion (a government-watched green source never moves to a vendor).
~~~

### ADR-0015 L4 (finding 12)

Current: `Applies to: listening-sdk (F5),`

Replace: `Applies to: F3, registry-writer, backfill-orchestrator, listening-sdk (F5),`

### ADR-0016

**L4** (finding 12)

Current: `registry-writer, and the lanes`

Replace: `registry-writer, x-compliance-sync, and the lanes`

**L17** (finding 19)

Current: `(CF-032 option 2):.**`

Replace: `(CF-032 option 2):**`

**L19** (finding 19)

Current: `(CF-057 option 3):.**`

Replace: `(CF-057 option 3):**`

**L25** (ruling 1)

Current:
~~~
within ADR-0021's exclusions (no government-watched green source and no client-owned property ever moves to a vendor)
~~~
Replace:
~~~
within ADR-0021's exclusion (no government-watched green source ever moves to a vendor)
~~~

### ADR-0017 L28 (finding 4)

Current: ``(`window_start`, ADR-0059), not from a report.``

Replace: ``(`window_start`, ADR-0059, ADR-0064), not from a report.``

### ADR-0020 L4 (finding 12)

Two replacements:
- `Applies to: F2, F3, backfill-orchestrator,` → `Applies to: F2, F3, listening-sdk (F4, F5), backfill-orchestrator,`
- `web-commoncrawl-scanner, and the lanes` → `web-commoncrawl-scanner, tg-discussion-receiver, and the lanes`

### ADR-0021 (ruling 1; finding 15). L11 is in section 1.

**L18**

Current:
~~~
_Not taken as a whole: its classification of a 403 by reason and its two levels are kept (see Decision); its rule of no automatic fallback, with an approval card, is not._
~~~
Replace:
~~~
_Not taken as a whole: its classification of a 403 by reason, its two levels and its government exclusion are kept (see Decision); its rule of no automatic fallback, with an approval card, and its exclusion of client-owned properties are not._
~~~

**L34**

Current:
~~~
a blocked source falls back to its vendor route automatically wherever that route's vendor flag is on, never for a government-watched green source or a client-owned property, and every automatic fallback sends ops an n8n notice, not an approval card.
~~~
Replace:
~~~
a blocked source, a client-owned property included, falls back to its vendor route automatically wherever that route's vendor flag is on, never for a government-watched green source, and every automatic fallback sends ops an n8n notice, not an approval card.
~~~

**L54**: delete the line `  - the source is not a client-owned property (ADR-0052);`.

**Insert after L55** (`  - at least one client watching the source accepts amber data, …`), before `- Route-wide states`:
~~~
- A client-owned property falls back under these same conditions (the user's answer of 9 Oct 2026). ADR-0052 (e) still keeps it from every other vendor read: no reconciliation, gap fill or pre-join history. The amber services that read its type are its alternates in `canary_targets`: tt-profile-videos-poller for a TikTok account (`TT_VENDOR_ROUTE`) and tg-channel-posts-poller for a public Telegram channel (`TG_POSTS_ACTOR`); li-company-posts-poller (`LI_VENDOR_ROUTE`) for a LinkedIn page only if LI0 finds the activity URN on the green API, since otherwise no amber route reads a client-administered page (ADR-0007). No amber service reads a Facebook Page, an Instagram account or a YouTube channel, so those stay `blocked`. Its vendor records take the amber visibility of ADR-0053, the pool limited to clients that accept amber, so its owner receives them only if its own contract accepts amber, and a government client never does. A green source a government client watches never falls back, whoever owns it.
~~~
**[N2]**: under (b), replace the LinkedIn clause with "li-company-posts-poller for a LinkedIn page (`LI_VENDOR_ROUTE`)".

**L56**

Current: the whole bullet `- Route-wide states (`degraded`, `fallback`, back to `ok`) come only from the canary, … and only the canary sets it.`

Replace:
~~~
- Route-wide states (`degraded`, `fallback`, back to `ok`) come only from the canary, from evidence across targets. The canary falls a route back automatically wherever its alternate's flag is on; registry-writer applies a route-wide `fallback` to every source on the route, except that a government-watched green source takes `degraded` instead and never moves to the vendor. While a route is in `fallback`, its amber reads follow ADR-0052 (a) as any amber read does: a source is selected only if a client that accepts amber watches it, and an amber job re-checks at run time and ends without a call if none does, so no vendor read is bought for a source that no accepting client watches. The canary's route-wide `blocked`, when every active target and every token in use returns 401 or 403 (`source-health-canary §5.3 L72`, `§13 L151`), is kept, and only the canary sets it.
~~~

**L58**

Current:
~~~
- A source that is `blocked` and cannot fall back also sends ops a notice; for a client-owned property the client gets the missing-grant card of ADR-0067, so it can grant access again.
~~~
Replace:
~~~
- A source that is `blocked` and cannot fall back also sends ops a notice. For a client-owned property, whether it stays `blocked` or falls back, the client gets the missing-grant card of ADR-0067, so it can grant access again; the new grant ends the fallback (below).
~~~

**L66**

Current:
~~~
The limits keep the two promises the platform makes: a government client's green sources never turn into vendor data, and a client's own property is never read through a scraper.
~~~
Replace:
~~~
On 9 Oct 2026 the user asked that a client's own pages be read through the vendor as well, so a client's own property keeps its coverage while its grant is restored. The government exclusion keeps the promise the platform makes to government clients: their green sources never turn into vendor data.
~~~

**L70**

Current:
~~~
the compliance section gains "a government-watched green source and a client-owned property never move to an amber route; registry-writer enforces it".
~~~
Replace:
~~~
the compliance section gains "a government-watched green source never moves to an amber route, even when a client owns it; registry-writer enforces it".
~~~

**L71**, inside the quoted `CLAUDE.md` L47 text

Current:
~~~
a blocked source falls back to its vendor route automatically where that route's flag is on, never for a government-watched green source or a client-owned property, with an n8n notice to ops (ADR-0021).
~~~
Replace:
~~~
a blocked source falls back to its vendor route automatically where that route's flag is on, never for a government-watched green source, with an n8n notice to ops (ADR-0021).
~~~

**Insert after L73** (`- F3: the credential state and reason …`):
~~~
- The PRD lines that refuse a fallback for a client's own property are overridden and stay as written (ADR-0001): `tt-client-videos-fetcher §8 L132`, `li-client-posts-poller §8 L144`, `li-own-comments-fetcher §8 L144`, `tg-bot-channel-receiver §8 L152`. So are the alternates' exclusions of a client-owned source in `fallback`: `li-company-posts-poller §3 L26`, `§5.1 L41`; `tt-profile-videos-poller §3 L27`; `tg-channel-posts-poller §3 L28`. The green fetchers still call no vendor; registry-writer sets the fallback. F3 declares the client-owned alternates named under Decision in `canary_targets`, as ADR-0052 (d) declares Instagram hashtags'.
~~~

### ADR-0023 L36 (ruling 2)

Current: `and other media is downloaded where that register allows it (ADR-0068).`

Replace: `and other media is downloaded unless that register marks the download "not allowed" (ADR-0068).`

### ADR-0024 L27 (ruling 1; optional, kept)

Current: `a green client account is never reconciled through tt-profile-videos-poller (ADR-0052).`

Replace: `a green client account is never reconciled through tt-profile-videos-poller (ADR-0052), though, when its grant is lost, it falls back to it as ADR-0021 allows.`

### ADR-0031

**L4** (finding 12)

Current: `Applies to: F2, keyword-matcher, poster-resolver, store-writer, analysis-sentiment,`

Replace: `Applies to: F2, listening-sdk (F4), keyword-matcher, poster-resolver, store-writer, analysis-sentiment, normalize-item, registry-writer, qualifier, alert-evaluator, fb-group-posts-poller,`

**L33** (finding 17)

Current:
~~~
- Writers: keyword-matcher, once a poster's identity is readable (the `candidate_pending` message goes, since the mention is already out);
~~~
Replace:
~~~
- Writers: keyword-matcher, once a poster's identity is readable (the `candidate_pending` message goes, since the mention is already out), except for the items of an X `keyword_history` read, which are history only and feed no discovery (`job_kind = keyword_history`, ADR-0059);
~~~

### ADR-0032 L4 (finding 12)

Current: `news-comments-fetcher, and the eight resolvers`

Replace: `news-comments-fetcher, web-gdelt-poller, ig-hashtag-search, tt-video-stats-refresher, li-company-posts-poller, tg-channel-posts-poller, and the eight resolvers`

### ADR-0033 L4 (finding 12)

Current: `lang-dialect-id, and the eight resolvers`

Replace: `lang-dialect-id, x-full-archive-search, and the eight resolvers`

### ADR-0034

**L4**, end of line (finding 12)

Current: `li-notification-receiver, li-own-comments-fetcher`

Replace: `li-notification-receiver, li-own-comments-fetcher, fb-page-feed-poller, tg-channel-posts-poller`

**L27** (finding 17)

Current:
~~~
- Labels, closed: `first_sight` (an item's first observation), `poll`, `backfill`, `refresh` (`step` `+24h`, `+7d` or `refresh:<request_id>`),
~~~
Replace:
~~~
- Labels, closed: `first_sight` (an item's first observation), `poll`, `backfill` (also for the items of an X `keyword_history` read, which counts as a backfill read, ADR-0059), `refresh` (`step` `+24h`, `+7d` or `refresh:<request_id>`),
~~~

### ADR-0035

**L4** (findings 2 and 12, merged)

Current: ``news-comments-fetcher, analysis-media, A0, and every `deletions` producer:``

Replace: ``news-comments-fetcher, normalize-item, analysis-sentiment, analysis-topics, analysis-entities, analysis-media, A0, D3 (the admin API writes `client_request` deletions), and every `deletions` producer:``

**L25** (finding 2)

Current: ``and `client_request`, a client's request about data held only for it, which the class `telegram_bot` needs (ADR-0054).``

Replace: ``and `client_request`, a client's request about data held only for it, which the class `telegram_bot` needs and the admin API writes (ADR-0054, ADR-0012).``

**L27** (finding 1)

Current: `poster-resolver's cache and every service-private table under ADR-0025's rule.`

Replace: ``poster-resolver's cache (`poster_profiles`, ADR-0045), the stores of ADR-0010's public-account records, `public_accounts_dim` (ADR-0047) and `client_lists` (ADR-0043), and every service-private table under ADR-0025's rule.``

**L33**, end of the paragraph (finding 3; ruling 2a)

Current:
~~~
the X readers add the `withheld` field only if the pilot shows that the compliance results carry no country codes (`x-compliance-sync §14 Q5`, `Q2`).
~~~
Replace:
~~~
the X readers add the `withheld` field only if the pilot shows that the compliance results carry no country codes (`x-compliance-sync §14 Q5`, `Q2`). This departs from the proposal's answer to `x-compliance-sync §14 Q5`, "X `withheld` status is requested by every X reader and recorded on the item, never as a deletion" (`D2-PROPOSALS.md` L1120; Appendix C L2397), which contradicted its own option's rule (L1108). Phase 2 kept the rule, and the user accepted that on 9 Oct 2026 (`D2-SUMMARY.md`, Answers).
~~~

**L45** (finding 2)

Current: `YT6, YT7, N8.`

Replace: `YT6, YT7, N8, D3.`

### ADR-0036 L4 (finding 12)

Current: `news-dedup, news-site-resolver` (end of line)

Replace: `news-dedup, news-site-resolver, news-comments-fetcher`

### ADR-0037 L4 (finding 12)

Current: `Applies to: F2, raw-archiver, search-hit-router,`

Replace: `Applies to: F2, raw-archiver, quota-governor, normalize-item, poster-resolver, fb-page-resolver, ig-account-resolver, yt-channel-resolver, search-hit-router,`

### ADR-0038 L4 (finding 12)

Current: `keyword-matcher, and web:`

Replace: `keyword-matcher, yt-web-search-bridge, and web:`

### ADR-0039

**L4** (finding 12)

Current: `raw-archiver, normalize-item, analysis-sentiment`

Replace: `raw-archiver, normalize-item, keyword-matcher, store-writer, retention-purger, analysis-sentiment`

**L27** (finding 1)

Current:
~~~
and user ids from `sources.platform_id`; individuals keep only `author_ref` (ADR-0010), so their content is checked through the posts job;
~~~
Replace:
~~~
and user ids from `sources.platform_id` and from every `poster_profiles` row that holds one, the public accounts' rows included (ADR-0010, ADR-0045); ordinary individuals keep only `author_ref` (ADR-0010), so their content is checked through the posts job;
~~~

### ADR-0043

**L15** (finding 19)

Current: ``Depends on: ADR-0016 (`credentials`), ADR-0050 (the X gate), ADR-0052 (amber acceptance), ADR-0066 (the manual path for client-added candidates).``

Replace: ``Depends on: ADR-0010 (public accounts and the `saved` list), ADR-0016 (`credentials`), ADR-0050 (the X gate), ADR-0052 (amber acceptance), ADR-0056 (the YouTube text refresh, part of the service), ADR-0066 (the manual path for client-added candidates).``

**L31** (finding 1)

Current: `(D3 specifies the writer); services only read them.`

Replace: ``(D3 specifies the writer); services only read them, except that deletion-propagator removes the `client_lists` entries of an account a deletion removes, through the SDK purge registry (ADR-0035).``

### ADR-0044 L4 (finding 12)

Current: `keyword-matcher, x-filtered-stream, D3`

Replace: `keyword-matcher, store-writer, qualifier, x-filtered-stream, x-full-archive-search, D3`

### ADR-0046 L4 (finding 12)

Current: `deletion-propagator, and the lanes`

Replace: `deletion-propagator, store-writer, and the lanes`

### ADR-0047

**L4**, end of line (finding 12)

Current: `ig-comments-fetcher, yt-comments-fetcher`

Replace: `ig-comments-fetcher, yt-comments-fetcher, normalize-item, poster-resolver, search-hit-router, web-commoncrawl-scanner, fb-page-search`

**L16** (finding 19)

Current: ``Depends on: ADR-0010 (`author_ref`), ADR-0011 (`post_ref.url`), ADR-0031 (item hits), ADR-0035 (tombstones and the guard), ADR-0056 (what YouTube's 30-day rule covers).``

Replace: ``Depends on: ADR-0010 (`author_ref` and `public_accounts_dim`), ADR-0011 (`post_ref.url`), ADR-0031 (item hits), ADR-0035 (tombstones and the guard), ADR-0048 (the alert types that read `metrics_timeseries` and `item_stories`), ADR-0056 (what YouTube's 30-day rule covers).``

### ADR-0048

**L4**, end of line (finding 12)

Current: `li-post-comments-fetcher, D3`

Replace: `li-post-comments-fetcher, D3, U3`

**L46**, the Decision bullet only; L26 has the same words and stays (finding 19)

Current: ``the item `kind` (`post`, `comment`, `article`, ADR-0008)``

Replace: ``the item `kind` (`post`, `video`, `comment`, `article`, `result`, ADR-0008)``

**L62** (finding 16)

Current: the sub-bullet ending ``X, LinkedIn, Telegram and Facebook-group counts are recorded at first sight only (ADR-0058);``

Replace that ending with:
~~~
X, LinkedIn, Telegram and Facebook-group counts are recorded at first sight only (ADR-0058), so those routes give no velocity, and in v1 an engagement spike fires only on Facebook Pages, Instagram, TikTok and YouTube, whose counts are refreshed at +24 h and +7 d (ADR-0034, ADR-0058);
~~~

**L84** (finding 12)

Current: `VTT6, D3.`

Replace: ``VTT6, D3, U3 (the trending score, `DEFERRED.md`).``

### ADR-0049

**L4** (finding 12)

Current: `quota-governor, and the lanes`

Replace: `quota-governor, li-notification-receiver, tg-discussion-receiver, and the lanes`

**L29** (finding 5). The last sentence is **[N1]**.

Current: the bullet `- It also names each source type's primary poller, … F5 names the primary when it builds the table (`DEFERRED.md`).`

Replace:
~~~
- It also names each source type's primary poller, the one service that writes the `sources.last_polled_at` and `next_poll_at` summary (ADR-0015): the service that rotates that source type, for example fb-page-feed-poller for a Facebook Page or tg-channel-posts-poller for an amber Telegram channel (a bot channel's is tg-bot-channel-receiver, the only service that rotates it). Where another service also reads the row, the PRD names the primary: ig-account-media-poller for an Instagram account (`ig-mentions-fetcher §5.1 L45`) and ig-hashtag-search for a green Instagram hashtag (`ig-keyword-search §5.1 L45`). Where several services rotate one source type and no PRD names the primary (news sites, and the web keyword-rule rows the three web engines read, ADR-0044), F5 names the primary when it builds the table (`DEFERRED.md`).
~~~

### ADR-0050

**L4** (finding 12)

Current: `poster-resolver, backfill-orchestrator,`

Replace: `poster-resolver, qualifier, ig-hashtag-search, backfill-orchestrator,`

**L16** (finding 19)

Current: `Depends on: ADR-0016 and ADR-0021 (health and fallback), ADR-0017 …`

Replace:
~~~
Depends on: ADR-0010 (the follower threshold, a row of `feature_flags`), ADR-0016 and ADR-0021 (health and the automatic fallback), ADR-0017 (`skipped_flag_off`), ADR-0042 (`source_id` on the governor's request), ADR-0051 (vendor values), ADR-0053 (X before Enterprise).
~~~

### ADR-0051 L4 (finding 12)

Two replacements:
- `Applies to: F2, F3, qualifier,` → `Applies to: F2, F3, listening-sdk (F4), qualifier,`
- `web-gdelt-poller, D3, and every amber service` → `web-gdelt-poller, yt-web-search-bridge, x (x-recent-search, x-user-resolver, x-user-timeline-poller, x-filtered-stream, x-full-archive-search, x-replies-fetcher), the vendor probes VFB0, VIG0, VTT0, VLI0 and VTG0, D3, and every amber service`

### ADR-0052 (finding 12; ruling 1; finding 15)

**L4**

Current: `Applies to: F2, F3, comment-decay-scheduler,`

Replace: `Applies to: F2, F3, quota-governor, comment-decay-scheduler,`

**L22**

Current: `1. **Amber by explicit consent, never on a client's own properties** (chosen): its rules are under Decision.`

Replace: `1. **Amber by explicit consent, never on a client's own properties** (chosen, with ADR-0021's automatic fallback of a blocked client-owned property): its rules are under Decision.`

**L28**

Current: `a client's own properties are never read through a vendor;`

Replace: `a client's own properties are read through a vendor only in ADR-0021's automatic fallback, once their green access is lost;`

**L34**

Current: the bullet `- (e) A client's own green properties (TikTok Display accounts, Telegram bot channels, owned Pages and accounts) are never read through a vendor: … outages are reported to the client.`

Replace:
~~~
- (e) A client's own green properties (TikTok Display accounts, Telegram bot channels, owned Pages and accounts) are not read through a vendor beside their green read: no daily amber reconciliation, no outage gap fill, no pre-join history (tt-profile-videos-poller Q3 and tg-bot-channel-receiver Q6: no). The green read counts as complete; outages are reported to the client. When a property's green access is lost, ADR-0021's automatic fallback reads it through the vendor like any other source (the user's answer of 9 Oct 2026).
~~~

**L35** (findings 15 and Q021-6, merged)

Current: `- With ADR-0021's automatic fallback, (a) and (e) hold: a blocked green source moves to its amber route only when a client that accepts amber watches it, and a client-owned property never does.`

Replace:
~~~
- With ADR-0021's automatic fallback, (a) holds for one source and for a whole route: a blocked green source, a client-owned property included (the user's answer of 9 Oct 2026), moves to its amber route only when a client that accepts amber watches it and no government client does, and while a route is in `fallback` its amber reads take only the sources an accepting client watches; only accepting clients receive the records, so a property's owner receives them only if its own contract accepts amber (ADR-0021).
~~~

**L37**

Current: `a property authorised through the platform's own route should not be quietly re-read through a scraper.`

Replace: `a property authorised through the platform's own route should not be re-read through a scraper while that route works; when it is lost, the fallback is announced to ops and the client is asked to grant access again (ADR-0021).`

### ADR-0054 L57 (finding 2)

Current: `a client's request reaches deletion-propagator through the admin API (ADR-0012),`

Replace: ``a client's request reaches deletion-propagator as a `deletions` message the admin API writes (ADR-0012),``

### ADR-0055 L4, end of line (finding 12)

Current: `store-writer, poster-resolver`

Replace: `store-writer, poster-resolver, normalize-item, deletion-propagator`

### ADR-0056

**L4**, end of line (finding 12)

Current: `li-client-posts-poller, li-own-comments-fetcher`

Replace: `li-client-posts-poller, li-own-comments-fetcher, li-post-comments-fetcher`

**L39** (finding 6a)

Current: `aggregates and derived scores ten years, with the per-channel YouTube exception (v1 L81).`

Replace: `item-level derived rows following their item's class, and aggregates and rollups ten years with the per-channel YouTube exception (v1 L81).`

### ADR-0058 L29 (finding 16)

Current: `No extra spend; trend charts on these three platforms show counts as first seen; the question can come back after the pilot with measured costs.`

Replace: `No extra spend; trend charts on these routes show counts as first seen, and the engagement-spike alerts of ADR-0048 have no count velocity on them in v1; the question can come back after the pilot with measured costs.`

### ADR-0059

**L4** (finding 12)

Current: `web-commoncrawl-scanner, x (every X service)`

Replace: `web-commoncrawl-scanner, search-hit-router, ig-hashtag-search, ig-account-media-poller, li-post-search, x (every X service)`

**L51** (finding 4; ruling 3a)

Current: ``and x-full-archive-search reads `conversation_id:<root id>` from there to the job's start (ADR-0011, ADR-0017);``

Replace: ``and x-full-archive-search reads `conversation_id:<root id>` from there to the job's start (ADR-0011, ADR-0017; this hand-back is phase 2's technical choice, recorded in ADR-0064 for X5 to confirm);``

### ADR-0060

**L4** (finding 12)

Current: `backfill-orchestrator, and the lanes`

Replace: `backfill-orchestrator, fb-backfill, fb-reactions-fetcher, yt-video-details-fetcher, and the lanes`

**L29** (finding 17)

Current: ``- Backfilled posts (`job_kind = backfill`) get no series:``

Replace: ``- Backfilled posts (`job_kind = backfill`, and the posts of an X `keyword_history` read, which count as backfill reads, ADR-0059) get no series:``

**L32** (finding 4)

Current: ``that read the whole conversation from `window_start` rather than `thread_ids` (ADR-0059);``

Replace: ``that read the whole conversation from `window_start` rather than `thread_ids` (ADR-0059, ADR-0064);``

### ADR-0064 (finding 4; ruling 3a; finding 12)

**L4** (items 4 and 12, merged)

Current: `Applies to: F2, backfill-orchestrator, normalize-item, x-filtered-stream, x-recent-search, x-full-archive-search, x-replies-fetcher`

Replace: `Applies to: F2, listening-sdk (F4), backfill-orchestrator, comment-decay-scheduler, normalize-item, x-filtered-stream, x-recent-search, x-user-timeline-poller, x-full-archive-search, x-replies-fetcher`

**L29**

Current: the bullet `- x-full-archive-search keeps its `replies` kind, … x-replies-fetcher's reply index becomes `comment_state` (ADR-0046).`

Replace:
~~~
- x-full-archive-search keeps its `replies` kind, since ADR-0059 follows X replies to day 30: comment-decay-scheduler emits the steps after +3 d on its queue, each carrying `window_start`, the start of the previous step's read, so no hand-back through the report is needed (ADR-0011, ADR-0017), which answers `x-full-archive-search §14 Q2`; x-replies-fetcher's reply index becomes `comment_state` (ADR-0046). This hand-back is phase 2's technical choice, not the proposal's: the proposal left it for X5 to design once older replies were bought (`D2-PROPOSALS.md` L1977, L1987; Appendix C L2407). ADR-0059 bought them, F2 types the job's fields now, and the reply index the proposal pointed to is gone (ADR-0046). The user accepted the choice on 9 Oct 2026 (`D2-SUMMARY.md`, Answers); X5 confirms it in its build (`DEFERRED.md` section 3).
~~~

**L38**

Current: ``- `DEFERRED.md`: filling stream-gap parts older than 7 days, reported `gap_unfilled` in v1 (owner X5).``

Replace: ``- `DEFERRED.md`: filling stream-gap parts older than 7 days, reported `gap_unfilled` in v1 (owner X5); confirming the replies hand-back by `window_start`, phase 2's choice (owner X5).``

**L40**

Current: `Sessions that must read this: F2, then F4, C4, C10, X1, X3, X4, X5, X6.`

Replace: `Sessions that must read this: F2, then F4, C4, C10, C11, X1, X3, X4, X5, X6.`

### ADR-0065

**L4** (finding 12)

Current: `search-hit-router, youtube (`

Replace: `search-hit-router, quota-governor, qualifier, comment-decay-scheduler, youtube (`

**L32** (finding 19)

Current: `No hold: a stalled details fetcher leaves partial videos visible, not missing.`

Replace: ``No hold: a stalled details fetcher leaves partial videos visible, not missing. The proposal wrote this key as `youtube:post:<id>` with kind `post` (D2-PROPOSALS L2010); ADR-0007 and ADR-0008 make every YouTube video `youtube:video:` with kind `video`, as recorded here.``

### ADR-0067 L12 (finding 19)

Current: `Depends on: ADR-0012 (ops and client requests through the admin API).`

Replace: ``Depends on: ADR-0012 (ops and client requests through the admin API), ADR-0021 (the automatic-fallback notices that replace the `blocked` approval card).``

### ADR-0068 (ruling 2). L11 is in section 1; L3 and L5 stay.

**L27**

Current: `_Not taken: training uses only what the register permits._`

Replace: `_Not taken: evaluation follows (a), and training leaves out every use the register marks "not allowed" and every host with `ai-train = no`._`

**L32**, from `Training and media downloads follow`

Current: `Training and media downloads follow a register of permitted uses: … an entry defaults to "not allowed", and `ai-train = no` always excludes a host.`

Replace:
~~~
Training and media downloads follow a register of permitted uses, allowed by default: platform, vendor, client-owned, news and Telegram content may train models, and images, audio and video may be downloaded, unless the register marks that use "not allowed" for the item's platform, vendor or news host. The register is seeded with a "not allowed" row for every use a platform's terms or a vendor contract already forbids (below). The user or the user's compliance owner reviews and changes the entries, and `ai-train = no` always excludes a host.
~~~

**L41**

Current: `- Platform, vendor, client-owned, news and Telegram content may be used for training when the register's entry for that source says the source's terms allow it. Until an entry says so, the source's content stays out of every training set.`

Replace:
~~~
- Platform, vendor, client-owned, news and Telegram content may be used for training unless the register marks training "not allowed" for the item's platform, vendor or news host.
~~~
**[N5 (a)]**: append the Meta sentence given in new_decisions 1.

**L51**

Current: `- Images, audio and video are downloaded wherever the register says the platform's terms and the vendor contract allow it, and stored under `media/<sha256>``

Replace: `- Images, audio and video are downloaded unless the register marks that download "not allowed" for the item's platform or vendor, and stored under `media/<sha256>``

**L52**

Current: `- YouTube stays thumbnails only unless the register says otherwise, because YouTube's terms forbid downloading video without YouTube's prior written permission (and the rights holders', where they apply); an entry that allows it names that permission as the clause relied on.`

Replace:
~~~
- YouTube stays thumbnails only: its video and audio downloads are seeded "not allowed", because YouTube's terms forbid downloading video without YouTube's prior written permission (and the rights holders', where they apply); an entry that allows them names that permission as the clause relied on.
~~~
Keep the rest of L52.

**L53**

Current: `and they process nothing the register did not allow.`

Replace: `and they process nothing whose download the register marks "not allowed".`

**L57**

Current: `with whether the use is allowed (false by default, and false for a missing row), the terms or contract clause relied on, and who set it and when.`

Replace:
~~~
with whether the use is allowed (true by default, and true for a missing row), the terms or contract clause relied on, and who set it and when. A use is not allowed when the row of the item's platform, vendor or news host says so.
- F3 seeds a "not allowed" row, with its clause, for every use a platform's terms or a vendor contract already forbids as recorded in CONVENTIONS and the ADRs: YouTube, downloading video and downloading audio (YouTube's terms forbid downloading video without its prior written permission, above). A row is added as each further term or contract is read and found to forbid a use, such as each vendor contract and the Disqus terms counsel reads (`DEFERRED.md` section 1); news hosts are excluded by `ai-train = no` at run time, not by rows.
~~~
**[N5 (a)]**: insert the Meta clause given in new_decisions 1.

**L58**

Current: `- Its owner is the admin console, which writes it audited (D3 specifies the writer); the user, or the user's compliance owner, sets every entry.`

Replace: `- Its owner is the admin console, which writes it audited (D3 specifies the writer); after F3's seed, the user, or the user's compliance owner, reviews the rows and sets or changes every entry.`

**L61**

Current: the paragraph `Why: The user wants content downloaded … defaulting to "not allowed" keeps everything out until someone has checked. Evaluation on de-identified samples and the Content Signals stay as proposed.`

Replace:
~~~
Why: The user wants content downloaded and used for training wherever that breaks no rule, and on 9 Oct 2026 chose "Allowed by default". A register makes "no rule broken" a recorded decision per source, made by the user or the compliance owner, rather than a reading each build session makes; seeding it with every use a recorded term or contract forbids keeps the default from breaking a known rule. Evaluation on de-identified samples and the Content Signals stay as proposed.
~~~

**L65**

Current: `Models can train on real Iraqi content as soon as the register allows a source; … no media beyond YouTube thumbnails is downloaded.`

Replace:
~~~
Models can train on real Iraqi content from the start, from every source the register does not exclude; media analysis covers images, audio and video wherever the register does not exclude them, and YouTube thumbnails only; a use the register excludes stays out until the user changes its row.
~~~
**[N5 (a)]**: insert the Meta parenthesis given in new_decisions 1.

**L68**

Current: ``- F3 creates `permitted_uses`; F2 adds the declared `usage_signals` field to `items.normalized`; D3 specifies the admin console's register screen.``

Replace: ``- F3 creates `permitted_uses` with its seeded "not allowed" rows; F2 adds the declared `usage_signals` field to `items.normalized`; D3 specifies the admin console's register screen, where the user reviews them.``

**L69**

Current: `A1 to A4 train on public and annotated data first, then on the sources the register allows;`

Replace: `A1 to A4 train on public and annotated data and on every source the register does not exclude;`

**L70**

Current: ``- `DEFERRED.md`: filling the register, owned by the user (or the user's compliance owner), before any training on platform content and any download beyond YouTube thumbnails; with each entry, what deleting a training item requires of a model already trained on it.``

Replace: ``- `DEFERRED.md`: reviewing the seeded register, owned by the user (or the user's compliance owner), before training on platform content and media downloads begin, though no session waits for it; with each source whose content trains a model, what deleting a training item requires of a model already trained on it.``

### ADR-0069 L4 (finding 12)

Current: `I1, D3, U2, deletion-propagator`

Replace: `I1, D3, U2, G4, deletion-propagator`

### ADR-0070 L26 (finding 6e)

Current: `which CONVENTIONS lists (YouTube). Rejected:`

Replace: ``which CONVENTIONS lists (YouTube); X's reply steps after +3 d go to `jobs.x-full-archive-search` with `window_start` (ADR-0059, ADR-0060). Rejected:``

### docs/decisions/README.md L7 (finding 12)

Current: `session reads the ADRs whose "Applies to" names its service, platform, lane or "all".`

Replace:
~~~
session reads the ADRs whose "Applies to" line names its session ID, service, platform, lane or "all", or whose "Sessions that must read this" line names it (ADR-0001), and the rows of `DEFERRED.md` that name it. Every session an ADR names in "Sessions that must read this" is also reached by its "Applies to" line, by ID, service, platform, lane or "all".
~~~

---

## 3. docs/prds/_shared/CONVENTIONS.md (v1.1)

**L7** (finding 6a; ruling 3)

Current: `aggregates and derived scores ten years, YouTube's per-channel figures excepted (ADR-0054, ADR-0056).`

Replace: `item-level derived rows (analysis scores, hits, metrics time series) follow their item's class; aggregates and rollups ten years, except rollups of one YouTube channel, which keep 36 months (ADR-0054, ADR-0056).`

**L13** (ruling 1). Anchor with the leading "and ".

Current: `and a client's own properties are never read through a vendor (ADR-0052).`

Replace: `and a client's own properties are read through a vendor only in the automatic fallback of a blocked source (ADR-0052, ADR-0021).`

**L25** (finding 6f)

Current: ``by condition `source_id` (or `candidate_key`), `platform_id` and `idempotency_key` for item kinds, `parent_id`, `root_id` and `redacted_fields` on comments; optional a typed `context` declared per producer.``

Replace: ``by condition `source_id` (or `candidate_key`), `platform_id` and `idempotency_key` for item kinds, `parent_id` and `root_id` on comments; optional a typed `context` declared per producer, and `redacted_fields` on any record, the payload paths an adapter removed or replaced (ADR-0009).``

**L28** (finding 17, the item's optional extra (a))

Current: `Writers: keyword-matcher; x-recent-search and tg-message-search as early signals;`

Replace: ``Writers: keyword-matcher (never for the items of an X `keyword_history` read, which feed no discovery, ADR-0059); x-recent-search and tg-message-search as early signals;``

**L43** (finding 20; ruling 3a)

Current: ```post_ref` is the scheduler's object `{item_id, platform, platform_id, url}`, with `thread_ids` on replies jobs.``

Replace: ``…, with `thread_ids` on replies jobs, except X's `replies` jobs on `jobs.x-full-archive-search`, which carry `window_start` instead (below; ADR-0060).``

**L67** (finding 20)

Current: ``| `deletion_requests` (people's requests only) | created through the admin console's deletion channel; intake and status by retention-purger | ADR-0035, ADR-0069 |``

Replace:
~~~
| `deletion_requests` (people's requests only) | retention-purger, its one writer: a person's request and its confirmation, recorded in the admin console, reach its deletion channel through the admin API, and it keeps intake, hashing and status | ADR-0035, ADR-0067, ADR-0069 |
~~~

**L82** (ruling 2)

Current: ``| `permitted_uses` (the register of permitted uses) | the admin console; entries set by the user or the user's compliance owner | ADR-0068 |``

Replace:
~~~
| `permitted_uses` (the register of permitted uses) | F3 seed (the "not allowed" rows of ADR-0068), then the admin console; entries reviewed and set by the user or the user's compliance owner | ADR-0068 |
~~~

**L101**, after its last sentence (finding 20)

Current: `…, engagement spike, topic spike, entity or logo, story (ADR-0048).`

Append:
~~~
 Government clients keep the allowed types of `alert-evaluator §5.3 C` (volume spike, negative share and keyword first seen, on reputation and service-quality keywords, aggregate-only); the four new types are refused for them unless the user and counsel add one (ADR-0048, `DEFERRED.md`).
~~~

**L142** (finding 6e)

Current: ``except where a route has a dedicated replies service, which this document lists (YouTube's yt-replies-fetcher) (ADR-0070). One `replies` job per post, `post_ref` carrying `thread_ids```

Replace: ``except where a route has a dedicated replies service, which this document lists (YouTube's yt-replies-fetcher) (ADR-0070), and X, whose reply steps after +3 d are `replies` jobs on `jobs.x-full-archive-search` that read the whole conversation from `window_start` rather than `thread_ids` (ADR-0059, ADR-0060, ADR-0064). Elsewhere, one `replies` job per post, `post_ref` carrying `thread_ids```

**L147** (finding 20)

Current: `X, LinkedIn, Telegram and Facebook groups record counts at first sight only in v1 (ADR-0058).`

Replace: `X, LinkedIn, Telegram, news and Facebook groups record counts at first sight only in v1 (ADR-0058).`

**L158** (finding 2)

Current: `A deletion request (a person's, a client's or a platform's) removes what it names in any class.`

Replace: `A deletion request (a person's or a platform's, or a client's about data held only for that client) removes what it names in any class; the admin API writes a client's request, with reason `client_request` (ADR-0012, ADR-0035, ADR-0054).`

**L165** (finding 20)

Current: ``- `tiktok_display`: a client's own TikTok videos and stats, kept while the client's authorisation lasts; deleted on revocation, at offboarding and on TikTok's request (ADR-0054).``

Replace: ``- `tiktok_display`: a client's own TikTok videos and stats, kept while the client's authorisation lasts, within the ten years; deleted on revocation (reason `authorization_revoked`, ADR-0035), at offboarding and on TikTok's request (ADR-0054).``

**L211** (ruling 1). The LinkedIn clause is **[N2]**.

Current: the bullet `- Automatic fallback (ADR-0021): … for a client-owned property the client gets a missing-grant card.`

Replace:
~~~
- Automatic fallback (ADR-0021): when registry-writer applies a source-level `blocked`, it moves the source to `fallback` instead, so its posts are read through the amber route, wherever an amber route reads that source type (declared in `canary_targets`), that route's flag is not `off`, no government client watches the source, and a watching client accepts amber; otherwise the source stays `blocked`. A client-owned property falls back under the same conditions (a TikTok account through tt-profile-videos-poller, a public Telegram channel through tg-channel-posts-poller, a LinkedIn page through li-company-posts-poller only if LI0 finds the activity URN on the green API, ADR-0007), and its owner receives the vendor's records only if its contract accepts amber. Every automatic fallback, of one source or of a route, and every source that is blocked and cannot fall back, sends ops an n8n notice, never an approval card; for a client-owned property, blocked or fallen back, the client gets a missing-grant card so it can grant access again.
~~~

**L212**, first sentence (finding 15 with ruling 1)

Current: `… applied by registry-writer, never moving a government-watched green source or a client-owned property to a vendor (ADR-0021, ADR-0016).`

Replace: `… applied by registry-writer, never moving a government-watched green source to a vendor; while a route is in `fallback`, its amber reads still take only the sources a client that accepts amber watches (ADR-0021, ADR-0016, ADR-0052).`

**L223** (ruling 1)

Current: `A government-watched green source and a client-owned property never move to an amber route; registry-writer enforces it (ADR-0021).`

Replace: `A government-watched green source never moves to an amber route, even when a client owns it; registry-writer enforces it (ADR-0021).`

**L226** (ruling 1). Anchor: `amber records list only accepting clients; a client's own properties are never read through a vendor (ADR-0052).`

Replace the part after "accepting clients; " with:
~~~
a client's own properties are read through a vendor only in ADR-0021's automatic fallback, never for reconciliation, gap fill or pre-join history (ADR-0052, ADR-0021).
~~~

**L228**, end of the line (finding 1)

Current: `and the X terms screen applies; Facebook lists Pages and groups.`

Replace: ``and the X terms screen applies; Facebook lists Pages and groups. An author-scope deletion removes a public account's records, since `poster_profiles`, `public_accounts_dim` and `client_lists` are in the SDK purge registry (ADR-0035), and x-compliance-sync submits every X user id `poster_profiles` holds, beside `sources.platform_id` (ADR-0039).``

**L230** (ruling 2). Two replacements.

First:
- Current: ``and platform, vendor, client-owned, news and Telegram content only where the register of permitted uses (`permitted_uses`) allows that source; entries default to "not allowed", and `ai-train = no` always excludes a host.``
- Replace: ``and platform, vendor, client-owned, news and Telegram content unless the register of permitted uses (`permitted_uses`) marks that use "not allowed" for the item's platform, vendor or news host. A use is allowed by default; the register is seeded with a "not allowed" row for every use a platform's terms or a vendor contract already forbids (downloading YouTube video and audio); and `ai-train = no` always excludes a host.``
- **[N5 (a)]**: add "training on Facebook and Instagram content;" inside the parenthesis.

Second:
- Current: `Images, audio and video are downloaded wherever the register allows; YouTube stays thumbnails only unless the register says otherwise; speech-to-text and frame OCR run on media downloaded under the register.`
- Replace: `Images, audio and video are downloaded unless the register marks that download "not allowed"; YouTube stays thumbnails only unless an entry naming YouTube's written permission allows more; speech-to-text and frame OCR run on media downloaded under the register.`

**L280** (finding 6b)

Current: `Vendor data includes poster names and ids, replaced at the edge (ADR-0010).`

Replace: `Vendor data includes poster names and ids: commenters' identities are replaced at the edge; a post's poster keeps its platform id until poster-resolver classes it, and raw-archiver then redacts an ordinary individual's id from the archive (ADR-0010).`

**L292** (finding 20)

Current: `### TikTok (amber = EnsembleData, TikHub the fallback once its owner is verified; green only for the client's own account through the Display API)`

Replace: `### TikTok (amber = EnsembleData, TikHub the fallback once its owner is verified, ADR-0051; green only for the client's own account through the Display API)`

**L294** (ruling 1)

Current: `and is never read through a vendor (ADR-0024, ADR-0049, ADR-0052).`

Replace: `and is read through a vendor only in ADR-0021's automatic fallback, never reconciled through one (ADR-0021, ADR-0024, ADR-0049, ADR-0052).`

**L316** (finding 20)

Current: `` `TG_VENDOR_ROUTE = telemetrio` for search and stats.``

Replace: `` `TG_VENDOR_ROUTE = telemetrio` for search and stats (ADR-0051).``

**L333** (finding 6c)

Current: `a 401, 402, 403, 451, any other 4xx, or a challenge page sends one `recheck` per host and stops the batch; a 404 or 410 on a feed, sitemap or homepage sends `refresh` to news-site-resolver (ADR-0022).`

Replace: `a 401, 402, 403, 451, any other 4xx not named here, or a challenge page whatever its status (Cloudflare's can be a 503) sends one `recheck` per host (coalesced) and stops the batch; a 404 or 410 on a feed, sitemap or homepage sends `refresh` to news-site-resolver; a 404 or 410 on an article does neither (ADR-0022).`

**L370** (finding 20)

Current: `7. Individuals: never sources, never profiled, never listed; … Public accounts may be listed as the compliance section says (ADR-0010).`

Replace:
~~~
7. Individuals: never sources, never profiled; the matched post is a mention with an `author_ref`; no backfill; re-qualified as a creator only when resolver numbers cross the creator threshold. An ordinary individual (`public_account` false) is never listed; an individual's account that passes the public test (verified, or at or above the follower threshold) is a public account and may be listed as the compliance section says (ADR-0010, ADR-0033).
~~~

**L382, L385, L387** (finding 20). Add ` (ADR-0060)` before the closing ` |` of each Replies cell:
- `| one `replies` job per post, by comment id when the vendor exposes it (ADR-0060) |`
- `| one `replies` job per post for comments with more than 10 replies (ADR-0060) |`
- `| one `replies` job per post to yt-replies-fetcher for threads with more than 5 replies (ADR-0060) |`

**L400** (finding 6d)

Current: `as described in fb-page-feed-poller, with the job fields this document defines (ADR-0001).`

Replace: `as described in fb-page-feed-poller, with the job fields and the rotation state this document defines: due times in the service's own `cursors` rows, ordered by `next_due_at` then tier, never by `sources.next_poll_at` (ADR-0001, ADR-0015).`

**Insert after L134** (finding 5). L134 is the bullet `- Backfill: when a source is added, …`, the last of the Posts bullets; insert before the blank line and `Comments (comment fetchers, …`. Apply this insertion last. The two "named by F5" cells are **[N1]**.
~~~

Primary pollers. The cadence table also names each source type's primary poller, the one service that writes the `sources.last_polled_at` and `next_poll_at` summary: the service that rotates that source type (ADR-0049, ADR-0015). Any other service that reads the row, a fallback alternate included, writes only its own `cursors` row (ADR-0015, ADR-0041).

| Source type | Primary poller |
|---|---|
| Facebook Page, a client's own included | fb-page-feed-poller (ADR-0049; `fb-client-webhook-receiver §5.1 L42`) |
| Facebook group | fb-group-posts-poller |
| Facebook keyword rule | green row: fb-page-search; amber row: fb-keyword-search (ADR-0044) |
| Instagram account or creator | ig-account-media-poller (`ig-mentions-fetcher §5.1 L45`) |
| Instagram hashtag | green row: ig-hashtag-search, in fallback too (`ig-keyword-search §5.1 L45`); amber row: ig-keyword-search |
| Instagram keyword rule | ig-keyword-search |
| TikTok creator | tt-profile-videos-poller |
| TikTok client account | tt-client-videos-fetcher |
| TikTok hashtag | tt-hashtag-feed-poller |
| TikTok keyword rule | tt-keyword-search |
| X account | x-user-timeline-poller, stream-covered accounts included (`x-user-timeline-poller §5.1 L42`) |
| X keyword rule | x-recent-search; x-full-archive-search has no scheduler (`x-full-archive-search §5.1 L39`) |
| LinkedIn client page | li-client-posts-poller |
| LinkedIn company page (amber) | li-company-posts-poller |
| LinkedIn keyword rule | li-post-search |
| Telegram channel (amber) | tg-channel-posts-poller (ADR-0049) |
| Telegram bot channel | tg-bot-channel-receiver, through its daily check (ADR-0049) |
| Telegram discussion group | tg-discussion-receiver, through its daily check (ADR-0012) |
| Telegram keyword rule | tg-message-search |
| YouTube channel | yt-uploads-reconciler (ADR-0015; `yt-pubsub-receiver §5.1 L40`) |
| YouTube keyword rule | tier 1: yt-keyword-search; tiers 2 and 3: yt-web-search-bridge (`yt-keyword-search §5.1 L46`, `yt-web-search-bridge §5.1 L50`) |
| News site | named by F5 (ADR-0049, `DEFERRED.md`) |
| Web keyword rule | named by F5 (ADR-0049, `DEFERRED.md`) |
~~~

---

## 4. The PRDs, README and DEFERRED.md

### 4a. The PRDs (findings 7 and 23)

The early-stop rewrites, owner lines, reader lines and gate lines are those that ADR-0019, ADR-0024, ADR-0025, ADR-0031, ADR-0040, ADR-0047, ADR-0050 and ADR-0057 name.

**facebook/fb-post-comments-fetcher.md**
- L48
  - Current: `- Early stop: a fetch that adds fewer than 5% new comments and fewer than 5 in absolute cancels the rest of the series.`
  - Replace: `- Early stop: comment-decay-scheduler applies it from this service's report; this service never stops a series itself (ADR-0019).`
- L166
  - Current: `- Early stop can cancel the +24 h sweep on a quiet post, leaving late comments and edits unseen (open question 2).`
  - Replace: `- Late comments and edits on a quiet post: the +24 h sweep always runs, even after early stop, so they are caught (ADR-0019).`

**facebook/fb-group-comments-fetcher.md**
- L46: the same current text as fb-post-comments-fetcher L48, and the same replacement.

**facebook/fb-backfill.md**
- L88
  - Current: ``envelope identical to fb-page-feed-poller's except `service` and `metrics_observation`, with``
  - Replace: ``envelope identical to fb-page-feed-poller's except `service` and `job_kind` (`backfill`), with``
- L103-L104
  - Current:
    ~~~
        "metrics_observation": "backfill",
        "window": {"start": "2026-07-08T11:00:00Z", "end": "2026-10-06T11:00:00Z"}
    ~~~
  - Replace:
    ~~~
        "job_kind": "backfill",
        "context": {"window": {"start": "2026-07-08T11:00:00Z", "end": "2026-10-06T11:00:00Z"}}
    ~~~
- L165
  - Current: `8. Every message carries `metrics_observation = backfill`, `retention_class = meta_on_request`, `route = green`, `fetched_at`, and the window.`
  - Replace: `8. Every message carries `job_kind = backfill`, `retention_class = meta_on_request`, `route = green`, `fetched_at`, and the window in `context` (ADR-0005, ADR-0070).`

**instagram/ig-comments-fetcher.md**
- L45, first sentence only
  - Current: `**Early stop.** When a fetch adds fewer than 5% new comments (new share = `new_count` over the comments stored before the fetch) and fewer than 5 absolute, the remaining series is cancelled; with about 15 visible comments this in practice means a fetch with no new comment.`
  - Replace: `**Early stop.** comment-decay-scheduler applies it from this service's report (`new_count` and the comments stored before the fetch); this service never stops a series itself (ADR-0019).`
- L167
  - Current: `5. A fetch with `new_count = 0` cancels the rest of the series; a fetch with 1 new comment against 15 stored does not.`
  - Replace: `5. A fetch with `new_count = 0` reports it with the comments stored before the fetch and cancels nothing itself; comment-decay-scheduler applies early stop (ADR-0019).`

**instagram/ig-own-comments-fetcher.md**
- L45
  - Current: `**Early stop.** When a fetch adds fewer than 5% new comments (new share = `new_count` over the comments stored before the fetch) and fewer than 5 in absolute terms, comment-decay-scheduler cancels the rest of the series.`
  - Replace: `**Early stop.** comment-decay-scheduler applies it from this service's report; this service never stops a series itself (ADR-0019).`
- L179
  - Current: `3. A fetch that adds 2 new comments to 100 stored is reported as under 5% and under 5 absolute, and the remaining series is cancelled.`
  - Replace: `3. A fetch that adds 2 new comments to 100 stored reports both counts and cancels nothing itself; comment-decay-scheduler applies early stop (ADR-0019).`

**instagram/ig-hashtag-search.md**
- L36
  - Current: `- poster-resolver and qualifier consume `discovery.hits` to find candidate business and creator accounts.`
  - Replace: `- No `discovery.hits`: this service's media name no poster, so they reach clients only as mentions in keyword-matcher's `item.hits` (ADR-0031).`
- L37
  - Current: `- normalize-item, lang-dialect-id, keyword-matcher and store-writer consume `raw.items`.`
  - Replace: `- normalize-item and raw-archiver consume `raw.items`; keyword-matcher and store-writer read what normalize-item publishes (ADR-0031).`

**linkedin/li-own-comments-fetcher.md**
- L42
  - Current: `**Early stop.** From the second fetch of a post onward, … because held comments expire at 48 hours.`
  - Replace: `**Early stop.** comment-decay-scheduler applies it from this service's report; this service never stops a series itself. On this route the report carries the post's total comment count as the API reports it, and growth is measured over that count rather than over the comments held, because held comments expire at 48 hours (ADR-0019).`
- L174
  - Current: `2. A +24 h fetch adding 3 new of 100 total cancels the +3 d step; adding 4 of 40 does not; adding 5 of 200 does not (absolute threshold).`
  - Replace: `2. A +24 h fetch adding 3 new comments reports them with the API's total count of 100 and cancels nothing itself; comment-decay-scheduler applies early stop over that count (ADR-0019).`

**linkedin/li-post-comments-fetcher.md**
- L44
  - Current: `**Early stop.** From the second fetch of a post onward, … so in practice the rule ends an extension early.`
  - Replace: `**Early stop.** comment-decay-scheduler applies it from this service's report; this service never stops a series itself. On this route growth is measured over this service's running total of comments seen, which the report carries (ADR-0019).`
- L180
  - Current: `an extension fetch adding 2 of 100 cancels the remaining extensions.`
  - Replace: `an extension fetch adding 2 of 100 reports them and cancels nothing itself, comment-decay-scheduler applying early stop (ADR-0019).`

**linkedin/li-post-search.md**
- L15
  - Current: `normalize-item and keyword-matcher then place posts by registered company pages in `item.hits` and posts by unknown posters in `discovery.hits` for poster-resolver and li-org-resolver.`
  - Replace: `normalize-item and keyword-matcher then write every matching post to `item.hits`, and a candidate for each unregistered poster to `discovery.hits` for poster-resolver and li-org-resolver (ADR-0031).`
- L90: `"job_id": "f3a9c2b1-5d7e-4c0a-9b2f-1e6d8a4c7b30",` → `"job_id": "01M4871WM0G35N2F2R5GBPWABM",`
- Add NOTE-ID after L103.

**linkedin/li-org-resolver.md**
- L103: `"job_id": "2b6f0d9c-7a1e-4f3b-8c5d-9e0a1b2c3d4e"` → `"job_id": "01M48AMMG0BSDJZYJZ2V3SKTWF"`
- Add NOTE-ID after L105.

**news/news-comments-fetcher.md**
- L43
  - Current: `The general rules of the addendum apply: early stop (when a fetch adds fewer than 5% new comments and fewer than 5 absolute, the remaining steps are cancelled); extension`
  - Replace: `The general rules of the addendum apply, each applied by comment-decay-scheduler from this service's report: early stop (this service never stops a series itself; ADR-0019); extension`
- L171
  - Current: `2. A fetch adding fewer than 5% new comments and fewer than 5 in absolute cancels the remaining steps; a +3 d fetch adding 20% or more extends the series every 2 days to day 30.`
  - Replace: `2. A fetch reports its new comments and the comments stored before it and cancels no step itself, comment-decay-scheduler applying early stop (ADR-0019); a +3 d fetch adding 20% or more extends the series every 2 days to day 30.`

**news/news-site-resolver.md**
- L92: `"seed_list": ["client_17"]` → `"seed_list": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]`
- L107: `"job_id": "job_01JA5X7R2M",` → `"job_id": "01M486K7W0KPR5FKH5ET9K2SFS",`
- Add NOTE-ID after L110.
- L112
  - Current: `registry-writer maps `proposed_source` onto the `sources` row (`tier` from the qualifier, `health = ok`, `backfill_status = pending`) and `site_profile` onto `news_sites`, keyed by `source_id`.`
  - Replace: `registry-writer maps `proposed_source` onto the `sources` row, inserting it under the `proposed_source_id` this service allocated with the candidate row (`tier` from the qualifier, `health = ok`, `backfill_status` at its default, `pending`). `site_profile` stays in `news_sites`, which only this service writes, keyed by that `source_id` (ADR-0040, ADR-0020).`

**news/news-feed-poller.md**
- L48
  - Current: `the qualifier accepts, registry-writer writes the `sources` row and the `news_sites` profile and emits `source.events` `added`;`
  - Replace: `the qualifier accepts, registry-writer writes the `sources` row under the `source_id` news-site-resolver allocated and emits `source.events` `added` (the `news_sites` profile is news-site-resolver's own row, ADR-0040);`
- L66
  - Current: `slot state in `crawl_policies.next_slot_at`.`
  - Replace: `slot state in the gate's own table, `host_gate`, written only by the SDK gate (ADR-0040).`
- L119
  - Current: `` `crawl_policies.next_slot_at` (host gate).``
  - Replace: `Host-gate slots live in `host_gate`, written only by the SDK gate (ADR-0040).`

**news/news-sitemap-poller.md**
- L131
  - Current: `` `crawl_policies.next_slot_at`.``
  - Replace: `Host-gate slots live in `host_gate`, written only by the SDK gate (ADR-0040).`

**news/news-homepage-differ.md**
- L122
  - Current: `` `crawl_policies.next_slot_at`. No page HTML is stored.``
  - Replace: `Host-gate slots live in `host_gate`, written only by the SDK gate (ADR-0040). No page HTML is stored.`

**news/news-article-extractor.md**
- L89, append to the sentence
  - Current: `` `raw.items` kind `article`, one message per article, envelope plus the record. Hosts in the example are illustrative.``
  - Replace: `` `raw.items` kind `article`, one message per article, envelope plus the record. Hosts in the example are illustrative. The extraction code is versioned as `extractor` and `extractor_version` (ADR-0070); where the example's other fields differ from an ADR, the ADR wins (ADR-0001).``
- L129
  - Current: ``…`status` = done | gone | not_article | paywalled | skipped_policy | failed, `canonical_url_hash`, `fetched_at`), pruned after a period set in the pilot; `crawl_policies.next_slot_at`;``
  - Replace: ``…`status` = done | gone | not_article | paywalled | skipped_policy | failed | duplicate_canonical (ADR-0036), `canonical_url_hash`, `fetched_at`), pruned after a period set in the pilot; host-gate slots in `host_gate`, written only by the SDK gate (ADR-0040);``

**news/news-robots-checker.md**
- L61
  - Current: `9. Upsert `crawl_policies`; on first check or any change, produce `crawl.policies`; on `crawl_allowed` flipping, registry-writer updates `sources.health`.`
  - Replace: `9. Upsert `crawl_policies`; on first check or any change, produce `crawl.policies`. When `crawl_allowed` flips for a registered site, or at the `added` event of a site added while disallowed, send a source-level `health_change` decision on `registry.decisions` (reason `crawl_disallowed`, back to `ok` once allowed), which registry-writer applies; registry-writer reads no `crawl.policies` (ADR-0013, ADR-0040).`
- L93, append to the sentence
  - Current: `` `crawl.policies`, one message per host on first check and on every change, keyed by `host`. Hosts in the example are illustrative.``
  - Replace: `` `crawl.policies`, one message per host on first check and on every change, keyed by `host`. Hosts in the example are illustrative. Its fields take the flat names of the `crawl_policies` row (ADR-0040, ADR-0070); where its other fields differ from an ADR, the ADR wins (ADR-0001).``
- L118
  - Current: `Also the `crawl_policies` row (same fields plus `next_refresh_at` and `next_slot_at`), `service_runs`, `dlq.news-robots-checker` after 5 failed attempts. registry-writer maps `crawl_allowed = false` onto `sources.health = blocked`.`
  - Replace: `Also the `crawl_policies` row (the message's columns without its change fields `changed_fields`, `requested_by` and `kind`, plus `next_refresh_at`; no slot column), `service_runs`, `dlq.news-robots-checker` after 5 failed attempts, and the source-level `health_change` decisions of step 9 on `registry.decisions`; registry-writer reads no `crawl.policies` (ADR-0013, ADR-0040).`
- L122
  - Current: `` `crawl_policies` (one row per host: `status`, … `policy_version`, `next_slot_at`); job `attempt`; per-host cooldown timers in memory.``
  - Replace: `` `crawl_policies`, written only by this service, one row per host: `host`, `status`, `crawl_allowed`, `reason`, `access_mode`, `crawl_delay_seconds`, `robots_status`, `robots_rules` (group, compiled rules, sitemaps, hash), `usage_signals`, `rsl`, `payment`, `checked_at`, `expires_at`, `next_refresh_at`, `policy_version`. There is no slot column, since the host gate keeps its slots in `host_gate` (ADR-0040, ADR-0070). Also job `attempt`, and per-host cooldown timers in memory.``
- L147 (finding 23)
  - Current: `every policy keeps its `robots.sha256` as evidence.`
  - Replace: `every policy keeps its `robots_rules.sha256` as evidence (ADR-0070).`

**shared/keyword-matcher.md**
- L95
  - Current: `` `item.hits` and `discovery.hits` (key `source_id`, the source that produced the item), `jobs.keyword-matcher`, `dlq.keyword-matcher`; `sources.last_hit_at`.``
  - Replace: `` `item.hits` (key `source_id`, the source that produced the item) and `discovery.hits` (key `candidate_key`; ADR-0004, ADR-0031), `jobs.keyword-matcher`, `dlq.keyword-matcher`; `sources.last_hit_at`. In the example, `message_id`, `producer.job_id` and `keyword_set_version` follow ADR-0006 and ADR-0070; where its other fields differ from an ADR, the ADR wins (ADR-0001, ADR-0031):``
- L100 (finding 23): `"message_id": "01J9N4B2C6D8E0F2G4H6J8K0MA",` → `"message_id": "01M486JMB0K5QZM1RWBPZ5NJ95",`. Its time part is `hit_at`, 2026-10-06T08:51:40Z.
- L102: `"job_id": null},` → `"job_id": "01M4871WM0NJ5SWYGET3ZGFGSP"},` (inside the `producer` object).

**shared/store-writer.md**
- L30
  - Current: `- aggregator builds `aggregates_hourly` from the tables written here; alert-evaluator reads `hits`, `items` and `aggregates_hourly`.`
  - Replace: `- aggregator builds `aggregates_hourly` from the tables written here. alert-evaluator reads the aggregate views, not `hits` or `items`; for the alert types ADR-0048 adds, it also reads `metrics_timeseries` and `item_stories` (ADR-0047).`
- L39
  - Current: `Trigger: topics `items.normalized`, `items.analysis`, `item.metrics`, `item.hits`, `discovery.hits` and `source.events`, one consumer group `store-writer`. Partitions follow `source_id` (ADR-0004), so one worker handles one source in order;`
  - Replace: `Trigger: topics `items.normalized`, `items.analysis`, `item.metrics`, `item.hits`, `news.dedup` and `source.events`, one consumer group `store-writer`. `discovery.hits` carries candidates for poster-resolver only and stays out of ClickHouse (ADR-0022, ADR-0031, ADR-0047). Partitions follow `source_id` (ADR-0004; `news.dedup` follows `story_id`), so one worker handles one source in order;`
- L63
  - Current: ``| `hits` | `row_version` | `client_id, keyword_id, item_id` | `toYYYYMM(hit_at)` | `item.hits`, `discovery.hits`; `status` active or retracted |``
  - Replace: ``| `hits` | `row_version` | `client_id, keyword_id, item_id` | `toYYYYMM(hit_at)` | `item.hits` only (ADR-0031, ADR-0047); `status` active or retracted |``

**shared/registry-writer.md**
- L95: `"client_ids":["cl_17"]` → `"client_ids":["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]`
- Add NOTE-ID after L96.
- After L103 (`- No cursors.`), add the list item: ``- Owners (ADR-0025): `registry_audit` and `registry_outbox` are shared control-plane tables whose one writer is this service (ADR-0045).``

**shared/poster-resolver.md**
- L67: `"job_id":"res:x:1234567890"` → `"job_id":"01M48B92SGPW37317W8KMVR3EE"`
- Add NOTE-ID after L68.
- L89: `"keywords":["kw_0412"],"client_ids":["cl_17"]` → `"keywords":["0cd402b6-9015-45f8-86b4-d90cc086d320"],"client_ids":["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]`
- Add NOTE-ID after L90.

**shared/qualifier.md**
- L84: `"client_ids":["cl_17"]` → `"client_ids":["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"]`
- Add NOTE-ID after L85.

**shared/analysis-entities.md, analysis-sentiment.md, analysis-topics.md, analysis-media.md**
- entities L97: `"job_id": "analysis-entities:priority:0009"` → `"job_id": "01M4886GG00N55MK92G5KMGQ7G"`; add NOTE-ID after L116.
- sentiment L96: `"job_id": "analysis-sentiment:priority:0007"` → `"job_id": "01M4886GG018V1FH131HTSP75D"`; add NOTE-ID after L112.
- topics L100: `"job_id": "analysis-topics:priority:0011"` → `"job_id": "01M4886GG040V4RTSSHFBF6ADK"`; add NOTE-ID after L119.
- media L94: `"job_id": "analysis-media:priority:0003"` → `"job_id": "01M4886GG0GDQ0Y9RD0QSBJD30"`; add NOTE-ID after L111.

**shared/normalize-item.md**
- L98: `"job_id": "fb-page-feed-poller:2026-10-06T09:00Z:7c1e"` → `"job_id": "01J9N2Q7Z4T8X1V6M3K0H5R2WB"`. This is fb-page-feed-poller's own example job id (its L118).
- L123
  - Current: `which this example omits (ADR-0070).`
  - Replace: `which this example omits (ADR-0070). Its `producer.job_id` follows ADR-0006.`

**shared/alert-evaluator.md**
- After L105, add a paragraph: ``Owners (ADR-0025): `alerts` is a shared control-plane table whose one writer is this service. `alert_rules` is shared; this service reads it, and the rule editor that D3 specifies writes it. `alert_deliveries` and `alert_watch_items` are private to this service: no other service reads them, F3's `TABLE-OWNERS.md` lists them, and they are registered in the SDK purge registry where they hold item ids, hashes or URLs.``

**shared/retention-purger.md**
- L102: `"item_ids": ["01J9N2Q7Z4T8X1V6M3K0H5R2WB"]` → `"item_ids": ["3287bad6-f64e-566f-a071-6fdd4aca57dd"]`
- Add NOTE-ID after L108.

**shared/source-health-canary.md**
- L152
  - Current: `6. TikHub `degraded` with a clean EnsembleData canary and `TT_VENDOR_ROUTE` on yields `fallback_on` for every TikTok source; with the flag `off` the route stays `degraded`.`
  - Replace: `6. TikHub `degraded` with a clean EnsembleData canary and `TT_VENDOR_ROUTE` not `off` yields `fallback_on` for every TikTok source; with the flag `off` the route stays `degraded` (ADR-0050).`

**telegram/tg-message-search.md**
- L34
  - Current: `- poster-resolver and qualifier consume `discovery.hits`; normalize-item, lang-dialect-id and keyword-matcher consume `raw.items`; store-writer, aggregator and alert-evaluator sit downstream.`
  - Replace: `- poster-resolver consumes `discovery.hits`; normalize-item and raw-archiver consume `raw.items`, and keyword-matcher reads what normalize-item publishes (ADR-0031); store-writer, aggregator and alert-evaluator sit downstream.`
- L84-L85
  - Current:
    ~~~
    "keyword_ids": ["kw_7f3a"],
      "client_ids": ["cl_a1b2"],
    ~~~
  - Replace:
    ~~~
    "keyword_ids": ["c6f2f07f-9f2c-48b8-a5bf-b265fdb569d1"],
      "client_ids": ["c7f12d45-b7c5-467d-aa82-e7826ed8abf2"],
    ~~~
- Add NOTE-ID after L92.
- L126
  - Current: `poster-resolver and qualifier (consumers of `discovery.hits`); normalize-item, lang-dialect-id, keyword-matcher, raw-archiver (consumers of `raw.items`);`
  - Replace: `poster-resolver (consumer of `discovery.hits`) and the qualifier; normalize-item and raw-archiver (consumers of `raw.items`) and keyword-matcher (reads `items.normalized`; ADR-0031);`

**telegram/tg-bot-channel-receiver.md**
- L123: `"update_id": 704118532, "attempt": 1,` → `"job_id": "01M487XDFG8JDZ667B758J62C2", "attempt": 1, "context": {"update_id": 704118532},`
- Add NOTE-RCV after L132.

**telegram/tg-discussion-receiver.md**
- L127: `"update_id": 704118977, "attempt": 1,` → `"job_id": "01M4886V7RNKF111FA2SGP78XR", "attempt": 1, "context": {"update_id": 704118977},`
- Add NOTE-RCV after L136.
- After L142, add a paragraph: ``Owner (ADR-0025): `tg_thread_map` is private to this service. No other service reads it, F3's `TABLE-OWNERS.md` lists it, and it is registered in the SDK purge registry where it holds item ids, hashes or URLs.``

**telegram/tg-channel-posts-poller.md**
- L186
  - Current: `the sixth failure lands in `dlq.tg-channel-posts-poller` with an alert.`
  - Replace: `the fifth failed attempt lands in `dlq.tg-channel-posts-poller` with an alert (ADR-0057).`

**tiktok/tt-video-comments-fetcher.md**
- L44
  - Current: `- **Early stop.** When a fetch adds fewer than 5% new comments (against the comments already stored) and fewer than 5 in absolute terms, the remaining steps are cancelled.`
  - Replace: `- **Early stop.** comment-decay-scheduler applies it from this service's report; this service never stops a series itself (ADR-0019).`
- L168
  - Current: `2. A fetch that adds 2 comments to 100 stored (2%, fewer than 5) cancels the remaining steps; one that adds 4 to 20 stored (20%) does not.`
  - Replace: `2. A fetch that adds 2 comments to 100 stored reports both counts and cancels no step itself; comment-decay-scheduler applies early stop (ADR-0019).`

**tiktok/tt-client-videos-fetcher.md**
- L43
  - Current: `The registry marks these accounts `tier = push`, so tt-profile-videos-poller makes only its one reconciliation poll a day for them.`
  - Replace: `The account keeps `push_covered = false` and its reach tier, and takes this hourly cadence from the `owned_by_client` row of the cadence table (ADR-0049); tt-profile-videos-poller never reconciles it (ADR-0052, ADR-0024).`
- L51
  - Current: `(tt-video-stats-refresher is an amber, vendor-paid service).`
  - Replace: `(tt-video-stats-refresher is an amber, vendor-paid service; ADR-0012, ADR-0034, ADR-0024).`
- After L115, add a paragraph: `Decided since: `retention_class = tiktok_display` is ADR-0054's class, kept while the client's authorisation lasts and deleted when it is revoked, which answers question 2 (ADR-0024). Where this section differs from another ADR, that ADR wins (ADR-0001).`
- After L119, add a paragraph: ``Owner (ADR-0025): `tt_client_video_state` is private to this service. No other service reads it, F3's `TABLE-OWNERS.md` lists it, and it is registered in the SDK purge registry where it holds item ids, hashes or URLs.``
- §8 L132 stays as written; ADR-0021's new Consequences bullet names it.

**tiktok/tt-keyword-search.md**
- L33
  - Current: `- normalize-item reads the messages; keyword-matcher confirms the hit and splits it into `item.hits` or `discovery.hits`; poster-resolver consumes discovery hits and asks tt-user-resolver for the profile.`
  - Replace: `- normalize-item reads the messages; keyword-matcher confirms the hit and writes it to `item.hits` whoever the poster is, with a `discovery.hits` candidate for an unregistered poster (ADR-0031); poster-resolver consumes the candidates and asks tt-user-resolver for the profile.`
- L86: `"job_id": "job_01J9Q7M3K2",` → `"job_id": "01M48RGBQ08KKPCN8S96112V4X",`
- L90: `"keyword_id": "kw_zain_4g"` → `"keyword_id": "a2beaeb7-80aa-47d7-99dc-f276c8aa6678"`
- Add NOTE-ID after L101.
- L145
  - Current: `1. With `TT_VENDOR_ROUTE = off`, no vendor call is made during a day of scheduled jobs and every job is counted as `flag_off`.`
  - Replace: `1. With `TT_VENDOR_ROUTE = off`, no vendor call is made during a day: the scheduler emits no job, and a job already queued ends `skipped_flag_off` at its start, never as an attempt (ADR-0050, ADR-0017).`
- L152
  - Current: `the sixth failure lands the job in `dlq.tt-keyword-search` with an alert.`
  - Replace: `the fifth failed attempt lands the job in `dlq.tt-keyword-search` with an alert (ADR-0057).`

**tiktok/tt-hashtag-feed-poller.md**
- L34
  - Current: `- normalize-item and keyword-matcher: a video from a hashtag source counts as a hit for the hashtag's clients without text matching, split into `item.hits` or `discovery.hits` by whether the poster is registered; poster-resolver takes the discovery hits.`
  - Replace: `- normalize-item and keyword-matcher: a video from a hashtag source is a hit for each of the hashtag's clients who passes the client gate, under the source's keyword, with `matched_by = source` when the text does not match. Every hit goes to `item.hits`, with a `discovery.hits` candidate for an unregistered poster (ADR-0031, ADR-0044); poster-resolver takes the candidates.`
- L92: `"job_id": "job_01J9QA4N7X",` → `"job_id": "01M4872SXGZPDRA21SXW1ZYD7N",`
- Add NOTE-ID after L106.
- L154: the same current text as tt-keyword-search L145, and the same replacement.
- L162
  - Current: `the sixth failure lands the job in `dlq.tt-hashtag-feed-poller` with an alert.`
  - Replace: `the fifth failed attempt lands the job in `dlq.tt-hashtag-feed-poller` with an alert (ADR-0057).`

**tiktok/tt-profile-videos-poller.md**
- L177
  - Current: `6. With `TT_VENDOR_ROUTE = off`, no vendor call is made in a day of scheduled jobs and each job is counted as `flag_off`.`
  - Replace: `6. With `TT_VENDOR_ROUTE = off`, no vendor call is made in a day: the scheduler emits no job, and a job already queued ends `skipped_flag_off` at its start, never as an attempt (ADR-0050, ADR-0017).`

**web/web-search-perplexity.md**
- L89: `partition key `web:<source_id>`.` → `partition key `source_id` (ADR-0004).`
- L95: `"message_id": "sr:perplexity:sha256:9c1e4b…:wsp-20261006-0117",` → `"message_id": "01M47K8KZ82WKA5373HTZ515SS",`
- L98: `"job_id": "wsp-20261006-0117",` → `"job_id": "01M47K8B60RM3M56CMJWGZ9C6G",`
- L99: `"keyword_id": "kw_0412", "client_ids": ["cl_17"],` → `"keyword_id": "0cd402b6-9015-45f8-86b4-d90cc086d320", "client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],`
- Add NOTE-ID2 after L108.
- L163: `the sixth failure lands in `dlq.web-search-perplexity` with an alert.` → `the fifth failed attempt lands in `dlq.web-search-perplexity` with an alert (ADR-0057).`

**web/web-search-mojeek.md**
- L88: `partition key `web:<source_id>`.` → `partition key `source_id` (ADR-0004).`
- L94: `"message_id": "sr:mojeek:sha256:4be07a…:wsm-20261006-0231",` → `"message_id": "01M47P1SFRP93VMPD2QC6WP5HA",`
- L97: `"job_id": "wsm-20261006-0231",` → `"job_id": "01M47P07P0M1V49VADF6SRK5BM",`
- L98: `"keyword_id": "kw_0412", "client_ids": ["cl_17"],` → the same UUIDs as perplexity L99.
- Add NOTE-ID2 after L107.
- L162: `the sixth failure lands in `dlq.web-search-mojeek` with an alert;` → `the fifth failed attempt lands in `dlq.web-search-mojeek` with an alert (ADR-0057);`

**web/web-gdelt-poller.md**
- L91: `partition key `web:<source_id>`.` → `partition key `source_id` (ADR-0004).`
- L97: `"message_id": "sr:gdelt:sha256:b27d93…:wgd-20261006-0905",` → `"message_id": "01M487CCJ069ZBDAYY9MKFA4FY",`
- L100: `"job_id": "wgd-20261006-0905",` → `"job_id": "01M487B1K0HD8T2YTQZB9XYNWZ",`
- L101: `"keyword_id": "kw_0412", "client_ids": ["cl_17"],` → the same UUIDs as perplexity L99.
- Add NOTE-ID2 after L111.

**web/search-hit-router.md**
- L112 and L129: `"client_ids": ["cl_17"],` → `"client_ids": ["0b6b8c7e-2d1a-4e0f-9c3a-5f2d1e8a7b60"],`
- Add NOTE-ID after L115 and after L132.
- After L138, add a paragraph: ``Owner (ADR-0025): `search_url_seen`, `search_candidate_seen` and `search_parked_urls` are private to this service. No other service reads them, F3's `TABLE-OWNERS.md` lists them, and they are registered in the SDK purge registry where they hold item ids, hashes or URLs.``

**web/web-commoncrawl-scanner.md**
- After L107, add a paragraph: ``Owner (ADR-0025): `cc_hosts_seen` is private to this service. No other service reads it, F3's `TABLE-OWNERS.md` lists it, and it is registered in the SDK purge registry where it holds item ids, hashes or URLs.``

**x/x-recent-search.md**
- L111: `"job_id": "job_01J9R4V2PX",` → `"job_id": "01M487XBH07GQE33JRM29CMCMZ",`
- Add NOTE-ID after L131.

**x/x-filtered-stream.md**
- L121: `"job_id": null, "attempt": null, "connection_id": "01J9PB7XQ3M8D2V6K0R4T1H5ZW",` → `"job_id": "01M48B5V90W8B91YHW3K3BNVR2", "attempt": 1, "context": {"connection_id": "01J9PB7XQ3M8D2V6K0R4T1H5ZW"},`
- Add NOTE-RCV after L134.

**x/x-replies-fetcher.md**
- L45
  - Current: `Early stop: a fetch adding under 5% new replies and under 5 absolute cancels the rest; armed only once the post has 5 or more stored replies or after the +24 h step.`
  - Replace: `Early stop: comment-decay-scheduler applies it from this service's report; this service never stops a series itself (ADR-0019). Where this paragraph differs from ADR-0059, ADR-0060 or ADR-0064 (X steps after +3 d run as `replies` jobs on `jobs.x-full-archive-search`), those ADRs win (ADR-0001).`

**x/x-compliance-sync.md**
- L105: `"item_ids": ["01J9M4T6R8W2Y5B7D9F1H3K5N7"]` → `"item_ids": ["537431ce-a994-5eee-93f1-30613cbc46a9"]`
- Add NOTE-ID after L111.
- After L134, add a paragraph: ``Owners (ADR-0025): `x_compliance_audit` is a shared control-plane table whose one writer is this service. `x_compliance_runs` is private to this service: no other service reads it, F3's `TABLE-OWNERS.md` lists it, and it is registered in the SDK purge registry where it holds item ids, hashes or URLs.``

**youtube/yt-comments-fetcher.md**
- L44
  - Current: `Early stop: a fetch adding fewer than 5% new comments and fewer than 5 absolute cancels the rest; armed only once the video has 5 or more stored comments or after the +24 h step.`
  - Replace: `Early stop: comment-decay-scheduler applies it from this service's report; this service never stops a series itself (ADR-0019).`

**youtube/yt-replies-fetcher.md**
- L40
  - Current: `Early stop: a fetch adding fewer than 5% new replies and fewer than 5 absolute cancels the thread's remaining steps; armed after the +24 h step or once 5 replies are stored.`
  - Replace: `Early stop: comment-decay-scheduler applies it from this service's report; this service never stops a series itself (ADR-0019). Where this paragraph differs from ADR-0060 (no per-thread series; one `replies` job per video carrying `thread_ids`), ADR-0060 wins (ADR-0001).`

**youtube/yt-keyword-search.md**
- L37
  - Current: `- normalize-item deduplicates the raw video records; keyword-matcher turns them into `item.hits` (channel registered) or `discovery.hits` (channel unknown).`
  - Replace: `- normalize-item deduplicates the raw video records; keyword-matcher turns every match into `item.hits`, with a `discovery.hits` candidate when the channel is unknown (ADR-0031).`
- L113: `"job_id": "yks-20261006-0042",` → `"job_id": "01M47JP18081JQQZ19WYHA1ZH3",`
- Add NOTE-ID after L121.

**youtube/yt-web-search-bridge.md**
- L118: `"job_id": "ywb-20261006-0117",` → `"job_id": "01M47F78AGDCFWH3S8DKZZJENT",`
- Add NOTE-ID after L124.

**youtube/yt-text-purger.md**
- L149: `"item_ids": ["01J8Q4M2C7R5T9V3X6Z0B8D1FG", "01J8Q4M2C9K4N7P1S5W8Y2A6HJ"]` → `"item_ids": ["e68d6e4b-56fd-52b1-9f72-f7018e8fe162", "3ed679f4-bac6-52e0-ba34-8d00cf816ef4"]`
- Add NOTE-ID after L157.

**youtube/yt-pubsub-receiver.md**
- After L134, add a paragraph: ``Owner (ADR-0025): `yt_subscriptions` is private to this service. No other service reads it, F3's `TABLE-OWNERS.md` lists it, and it is registered in the SDK purge registry where it holds item ids, hashes or URLs.``

**youtube/yt-video-details-fetcher.md**
- After L159, add a paragraph: ``Owner (ADR-0025): `yt_live_watch` is private to this service. No other service reads it, F3's `TABLE-OWNERS.md` lists it, and it is registered in the SDK purge registry where it holds item ids, hashes or URLs.``

All new ULIDs were checked: valid Crockford characters, time parts in the example's day. `docs/prds/` is outside Prettier.

### 4b. docs/prds/README.md (finding 21; ruling 1)

**L3**, the opening sentence only

Current: `Draft v1, 6 Oct 2026; decided in D2 on 7 Oct 2026: where this page, a PRD and an ADR in `docs/decisions/` differ, the ADR wins, and `_shared/CONVENTIONS.md` v1.1 carries every decision (ADR-0001, ADR-0070).`

Replace: `Draft v1, 6 Oct 2026; decided in D2 on 7 Oct 2026: where this page or a PRD differs from an ADR in `docs/decisions/`, the ADR wins (ADR-0001, ADR-0070); `_shared/CONVENTIONS.md` v1.1 folds the decisions in, each changed rule citing its ADR, which holds the full rule (CONVENTIONS v1.1 L3).`

**L22**, from "Every registered page" to "raises `rotation_behind`."

Replace:
~~~
Every registered page, group, account, creator, channel, company page and site is re-checked on its tier: tier 1 (100,000+ followers or a client priority) every 60 minutes, tier 2 every 6 hours, tier 3 every 24 hours, dormant sources weekly. Each service that rotates a source keeps the source's due time in its own `cursors` row, set from the start of its last run; jobs are ordered so no source is skipped twice in a row, and a poller that falls behind polls the most stale sources first and raises `rotation_behind`. `sources.next_poll_at` is only a summary for the admin view, written by the source's primary poller (ADR-0015, ADR-0049).
~~~

**L23**, the whole bullet

Replace:
~~~
- **Push where the platform offers it, with a daily safety net.** What a platform pushes arrives in seconds (fb-client-webhook-receiver, ig-webhook-receiver, li-notification-receiver, tg-bot-channel-receiver, tg-discussion-receiver, yt-pubsub-receiver, x-filtered-stream). A source whose new posts are pushed (`push_covered`) is reconciled once a day by its poller, so a missed push is never lost; a Telegram bot channel's daily job is instead the receiver's check that the bot is still an administrator, since the Bot API has no history method. Client TikTok accounts, LinkedIn client pages and client Instagram accounts are polled, not pushed (ADR-0049).
~~~

**L176**

Current: `the proposals stay below as they were made, and the ADR named after each one is the decision (ADR-0070):`

Replace: `the proposals stay below as they were made, except decision 8, which ADR-0024 rewords to the decisions that shape it, and the ADR named after each one is the decision (ADR-0070, ADR-0024):`

**L182**, the "Superseded by ADR-0021" sentence

Replace:
~~~
Superseded by ADR-0021: a 401 or 403 is classified by reason first, and a blocked source, a client-owned property included, falls back to its vendor automatically where the flag is on, never for a government-watched green source, with an n8n notice to ops instead of an approval card (the user's answer of 9 Oct 2026).
~~~

**L185**

Current: `is read hourly (ADR-0049) and is never read through a vendor (ADR-0052). Decided in ADR-0024.`

Replace: `is read hourly (ADR-0049) and is never reconciled through a vendor (ADR-0052), though, like any other source, it falls back to its vendor route under ADR-0021's conditions when its green access is lost (ADR-0021). Decided in ADR-0024.`

### 4c. docs/decisions/DEFERRED.md

Match on row text. Prettier realigns the tables.

**Section 1, L14** (finding 22): replace the `vendor_agreed` row with eight rows.
~~~
| `vendor_agreed`, SociaVault: the contract's limit on keeping vendor data | ten years where the contract allows it, otherwise the contract's limit (ADR-0054) | before VFB0 and VIG0, and before production (G4) | C14, F3, VFB0, VIG0 |
| `vendor_agreed`, ScrapeCreators: the contract's limit on keeping vendor data | ten years where the contract allows it, otherwise the contract's limit (ADR-0054) | before VFB0, and before production (G4) | C14, F3, VFB0 |
| `vendor_agreed`, TikHub: the contract's limit on keeping vendor data | ten years where the contract allows it, otherwise the contract's limit (ADR-0054) | before VTT0, and before production (G4) | C14, F3, VTT0 |
| `vendor_agreed`, EnsembleData: the contract's limit on keeping vendor data | ten years where the contract allows it, otherwise the contract's limit (ADR-0054) | before VTT0, and before production (G4) | C14, F3, VTT0 |
| `vendor_agreed`, Telemetrio: the contract's limit on keeping vendor data | ten years where the contract allows it, otherwise the contract's limit (ADR-0054) | before VTG0, and before production (G4) | C14, F3, VTG0 |
| `vendor_agreed`, tugelbay's Apify Actor: the contract's limit on keeping vendor data | ten years where the contract allows it, otherwise the contract's limit (ADR-0054) | before VTG0, and before production (G4) | C14, F3, VTG0 |
| `vendor_agreed`, sovereigntaylor's Apify Actor: the contract's limit on keeping vendor data | ten years where the contract allows it, otherwise the contract's limit (ADR-0054) | before VTG0, and before production (G4) | C14, F3, VTG0 |
| `vendor_agreed`, harvestapi's Apify Actor: the contract's limit on keeping vendor data; its LinkedIn data follows ADR-0055 unless the contract is shorter | ten years where the contract allows it, otherwise the contract's limit (ADR-0054) | before VLI0, and before production (G4) | C14, F3, VLI0 |
~~~

**Section 1, L19** (finding 22): replace the LinkedIn row with two rows.
~~~
| LinkedIn: whether our access counts as "authenticated", so `linkedin_org` keeps six months, not six weeks (this also sets the green backfill cap) | six weeks (ADR-0055) | before LinkedIn's go-live (G3) | LI1, F3, C14 |
| LinkedIn: the readings of ADR-0055 as a whole, the registry columns filled from an organisation's profile, kept while the source exists, included (ADR-0003) | as ADR-0055 and ADR-0003 state | before production (G4) | LI1, F3, C14 |
~~~

**Section 2, L37** (ruling 2)

Replace the register row with:
~~~
| The register of permitted uses, `permitted_uses` (ADR-0068), reviewed by the user or the user's compliance owner: the "not allowed" rows F3 seeds for the uses a platform's terms or a vendor contract already forbid, and a row for any further use a term or contract forbids (such as a vendor contract counsel reads, section 1) | which sources' content may train models, and where images, audio and video may be downloaded; a use is allowed unless its row says "not allowed", and the seeded rows (YouTube video and audio downloads) stand until changed | before training on platform content and media downloads begin; no session waits for it | A1, A2, A3, A4 and the fetch services that download media read it |
~~~
**[N5 (a)]**: add "; Facebook and Instagram training" inside "(YouTube video and audio downloads…)".

**Section 2, L38**
~~~
| With each source whose content trains a model: what deleting a training item requires of a model already trained on it | whether a deletion is enough or a model must be retrained at its next release | with the review of the register | A1 to A4 |
~~~

**Section 2, insert after L40** (the staging-cap row) (finding 11):
~~~
| The G2 data-quality targets: the pass marks that language, dialect, duplicate stories, extraction completeness and keyword-hit precision must meet on the 200-item sample you label (`build-plan/GATES.md`, G2 check 3). D2 set none; lang-dialect-id and keyword-matcher set their own release gates from the pilot sample (`lang-dialect-id §2 L17`, `keyword-matcher §2 L17`) | whether G2 check 3 passes | before G2 | G2, and E2's script for that check |
~~~

**Section 3, insert after L50** (the `public_accounts_dim` row) (finding 18):
~~~
| Where a producer session writes its normalize-item mapper: ADR-0008 puts the mappers in a registry in listening-sdk keyed `(service, api_version)`, as `normalize-item §9 L146` does, while the kit adds them under `services/normalize-item/src/mappers/<platform>/` (`.claude/skills/build-session/SKILL.md` L36, `build-plan/tools/gen_doc.py` L90) and review-session's scope rule allows only "an allowed normalize-item mapper" (L23). `docs/patterns/MAPPERS.md` names the one place, and the kit lines are reworded to match it | C4, with F4 | C4, before the first platform mapper (N6 and FB2, wave 3) |
~~~

**Section 3, L52** (finding 5; delete the row if N1 is answered (a) or (b)):
~~~
| The primary poller, which writes the `sources` rotation summary, of the source types several services rotate and no PRD names a primary for: news sites and web keyword-rule rows (ADR-0015, ADR-0049) | F5 | F5 |
~~~

**Section 3, insert after L66** (the X stream-gap row) (finding 4):
~~~
| Confirming the X replies hand-back: each `replies` job on `jobs.x-full-archive-search` carries `window_start`, phase 2's technical choice, accepted by the user on 9 Oct 2026 (ADR-0064) | X5 | X5 |
~~~

**Section 3, insert after L70** (the `latn` row) (finding 11):
~~~
| A Kurmanji (Badini) label: Kurmanji stays `other` in v1, a documented gap like Arabizi (ADR-0028, `lang-dialect-id §14 Q2`) | C3 | after the pilot |
~~~

**Section 3, L71** (ruling 1, the Q021 sweep's miss) **[N2]**

Current first cell: `Where the green LinkedIn API gives the activity URN (ADR-0007)`

Replace: `Where the green LinkedIn API gives the activity URN (ADR-0007); it also decides whether a LinkedIn client page can fall back to li-company-posts-poller (ADR-0021)`

**Section 4, L137**, third cell (finding 3)

Current: `compliance endpoints, formats, job limits and withheld country codes measured in X0`

Replace: `compliance endpoints, formats, job limits and withheld country codes measured in X0; if the results carry no country codes, the X readers add `withheld` (ADR-0035)`

**Section 4, L236**, third cell (finding 22)

Current: `settled by A5 in its build (with C15; a minute-grain table would be additive)`

Replace: `settled by A5 after the pilot: a minute-grain table (additive, with C15) only if the pilot shows missed spikes (ADR-0048; section 3)`

---

## 5. The kit (the user's files; ruling 4a, ruling 1)

### 5a. CLAUDE.md

**L43**

Replace: `- Acceptance tests from PRD section 13, as amended by the ADRs that apply (ADR-0001), first, then code. Show test output; never claim a result you did not run.`

**L47** (ruling 1)

Current: `never for a government-watched green source or a client-owned property, with an n8n notice to ops (ADR-0021)`

Replace: `never for a government-watched green source, with an n8n notice to ops (ADR-0021)`

**L48**

Replace: `- When the PRD and an ADR disagree, the ADR wins (ADR-0001): follow it and name it in the plan. When the PRD, CONVENTIONS or a handoff disagree in a way no ADR settles, or the PRD is silent: ask me with AskUserQuestion. Do not guess. Record the answer in the plan and the handoff.`

**L58**

Replace: `- Logs are structured JSON with `job_id`, `source_id`, `route`, `vendor`; metric names are the ones in the PRD's section 10, less any an ADR drops or renames (ADR-0001).`

### 5b. .claude/rules/services.md L12 (finding 9; the review's text, verbatim)

Replace:
~~~
- Rotation: each rotating service keeps its due time per source in its own `cursors` row (`next_due_at`, `last_started_at`), set from the start of the last run; a source with no row is due at once; jobs are ordered by `next_due_at` then tier, most stale first when behind (ADR-0015, ADR-0041). `sources.last_polled_at` and `next_poll_at` are a summary only the source type's primary poller writes, and no scheduler reads them (ADR-0015, ADR-0049). Comment, reply and metrics jobs come only from comment-decay-scheduler, the X reply steps to day 30 included; backfill and `keyword_history` jobs only from backfill-orchestrator; F2's producer table names every allowed producer (ADR-0012, ADR-0059).
~~~

### 5c. The review, plan and reviewer skills (finding 8, the review's texts; finding 12 for plan-session L17)

**.claude/skills/review-session/SKILL.md**
- L17: replace the opening `The brief (`ls build-plan/sessions/$0-*`), the PRD, `docs/plans/$0.md` and `docs/handoffs/$0.md`.` with `The brief (`ls build-plan/sessions/$0-*`), the PRD, the ADRs in `docs/decisions/` whose "Applies to" line names this service, its platform, its lane or "all" (an ADR wins over the PRD, ADR-0001), `docs/plans/$0.md` and `docs/handoffs/$0.md`.` The rest of the line is unchanged.
- L21: after `For each criterion in PRD section 13`, insert `, as amended by the ADRs that apply (ADR-0001),`.
- L22: after `Rotation or the comment series behave as PRD section 5.1 says`, insert `, as amended by the ADRs (ADR-0001)`. After `Metric names match PRD section 10`, insert `, as amended by the ADRs (ADR-0001)`.

**.claude/agents/prd-reviewer.md**
- L13: replace with `1. Read the session brief in `build-plan/sessions/`, the PRD it names (sections 5, 6, 8, 12 and 13 above all), the ADRs whose "Applies to" line names its service, platform, lane or "all" (an ADR wins over the PRD, ADR-0001), and the relevant parts of `docs/prds/_shared/CONVENTIONS.md`.`
- L15: replace with `3. For each acceptance criterion in PRD section 13, as amended by the ADRs that apply (ADR-0001), find the test that proves it and run it. Report pass, fail or untested.`

**.claude/skills/plan-session/SKILL.md**
- L17: replace with `3. Only the CONVENTIONS sections the brief lists (`docs/prds/_shared/CONVENTIONS.md`), and the ADRs in `docs/decisions/` whose "Applies to" line names this session's ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001).` This is the review's approved text plus the ID and the citation. The DEFERRED rows reach plans through the brief (gen_briefs.py L260).
- L25: replace with `- **Acceptance map:** every criterion in PRD section 13, as amended by the ADRs that apply (ADR-0001), the test that will prove it (unit, contract, acceptance or e2e) and the fixture it uses.`
- L30: replace with `- **Questions:** every ambiguity or conflict between the PRD, CONVENTIONS, the ADRs and the handoffs that no ADR settles (an ADR wins over the PRD, ADR-0001), and every PRD section 14 question this build depends on.`

### 5d. Pending the user's go-ahead [N6]

Apply only on a yes; otherwise list them in the handoff for the user.
- `.claude/rules/services.md` L14: `- Metric and alert names are exactly those in the PRD's section 10, less any an ADR drops or renames (ADR-0001); logs carry `job_id`, `source_id`, `route`, `vendor`.`
- plan-session L26: `- **Uncovered behaviours:** what PRD sections 5 and 8, as amended by the ADRs (ADR-0001), require that no criterion tests (rotation or series timing, catch-up, 429, 401 and 403, empty 200, a 5xx in the middle of pagination, DLQ after five attempts, replay idempotency), each with its own test.`
- `.claude/rules/python.md` L9: replace `lang-dialect-id (if D2 keeps it in Python).` with `lang-dialect-id (ADR-0028).`
- `.claude/rules/contracts.md` L11: `- Versioning follows `docs/contracts/VERSIONING.md` (ADR-0002): a change that only adds an optional field stays within its version; anything else is a new version with a dual-publish window.`
- `.claude/skills/contract-change/SKILL.md` L13: replace `Follow `docs/contracts/VERSIONING.md`: additive changes stay in the version; a breaking change is a new version with a dual-publish window.` with `Follow `docs/contracts/VERSIONING.md` (ADR-0002): a change that only adds an optional field stays in the version; anything else is a new version with a dual-publish window.`
- `.claude/skills/decide-session/SKILL.md` L23: append ` Alongside the admin console, specify the n8n flows: one per channel and per card type, with the Telegram-to-email fall-through `alert-evaluator §5.3 L69` requires (ADR-0067).`

---

## 6. The build plan (generator input, then regenerate)

**build-plan/README.md** (finding 8)
- L9: `3. **Tests come from PRD section 13 first,** and no test calls a live platform.` → `3. **Tests come from PRD section 13 first,** as amended by the ADRs that apply (ADR-0001), and no test calls a live platform.`
- L36: after `1. Every acceptance criterion in PRD section 13`, insert `, as amended by the ADRs that apply (ADR-0001),`.
- L37: after `2. The behaviours in PRD sections 5 and 8`, insert `, as amended by the ADRs (ADR-0001),`.
- L41: `6. The metrics and alerts named in PRD section 10 exist under those names.` → `6. The metrics and alerts named in PRD section 10, as amended by the ADRs (ADR-0001), exist under those names.`

**build-plan/templates/PLAN.md L17** (finding 10)

Replace: `| 429 backoff; 401 and 403 classified by reason: a quota one waits, an item-scoped one ends that item, an authorisation one revokes the credential or blocks the source and stops the batch (ADR-0021); empty 200 counted | | |`

**build-plan/templates/REVIEW.md** (findings 8 and 10)
- L23: `- [ ] Error policy: 429, 401 and 403 classified by reason (ADR-0021), empty 200, DLQ after five attempts`
- L24: `- [ ] Rotation or comment series as PRD 5.1, as amended by the ADRs (ADR-0001)`
- L26: `- [ ] Outputs validate; every data output carries provenance and retention_class, jobs and control messages `producer`, an author-, source- or client-scope deletion no retention_class (ADR-0003)`
- L27: `- [ ] Metric names as PRD 10, as amended by the ADRs (ADR-0001)`

**build-plan/templates/PROPOSAL.md L17** (finding 24)

Replace: `- Kind of change (ADR-0002): only adds an optional field (same version) | anything else (new version, dual-publish window)`

**build-plan/GATES.md**
- L23 (ruling 1)
  - Current: `a source a government client watches, or a client-owned property, never falls back to amber (ADR-0021).`
  - Replace: `a green source a government client watches never falls back to amber, and a client-owned property falls back under the same conditions as any other source (ADR-0021).`
- L34 (finding 11)
  - Replace: `3. On a 200-item sample you label, language, dialect, duplicate stories, extraction completeness and keyword-hit precision meet the targets you set before G2 (`docs/decisions/DEFERRED.md`, section 2).`
  - No ADR sets these targets; that is the finding. The edit cites DEFERRED, as the review's text does.
- L44 (finding 10)
  - Replace: `4. A canary flip rehearsed on staging: the canary moves a route to `degraded` or `fallback` and back to `ok`, with its alert; and a revoked client token turns its credential `revoked` and the sources only it reads `blocked`, or `fallback` where ADR-0021 allows, with the n8n notice to ops (ADR-0021).`

**build-plan/tools/sessions.py**
- L53 (D3 traps) (ruling 2): append a second string, `"The admin console's register screen shows every `permitted_uses` row for the user's review and writes each change audited; a use with no row is allowed (ADR-0068)"`.
- L86 (F3 traps) (ruling 2): after the last string, add `"Seed `permitted_uses` with the 'not allowed' rows ADR-0068 lists (YouTube video and audio downloads), each with its clause: a missing row means allowed, so only the seed keeps a forbidden use out (ADR-0068)"`. **[N5 (a)]**: add "; Facebook and Instagram training" inside the parenthesis.
- L96 (F4 traps) (finding 18; finding 24's template note): after `"Prove with a test that no token or secret can reach a log line"`, add two strings:
  - `"ADR-0008's mapper registry, keyed (service, api_version), is in listening-sdk; agree with C4 where producers' mappers sit (DEFERRED.md section 3)"`
  - `"The comment in services/_template/src/adapter.ts L3-L4 still says 401 and 403 mark the route degraded; reword it to ADR-0021's rule: 401 and 403 are classified by reason, an authorisation one setting credential or source state, never a route state, and stopping the batch (ADR-0021)"`
- L133 (F8 trap) (finding 10): `"Raw text TTLs differ by retention class; aggregates are kept ten years"` → `"Raw text TTLs differ by retention class; item-level derived rows follow their item's class; aggregates keep ten years, per-channel YouTube rollups 36 months (ADR-0054, ADR-0056)"`
- L192 (C4 traps) (finding 18): after `"Unknown shapes are archived and parked as schema_unknown, never dropped"`, add `"Where mappers live: ADR-0008 puts the registry keyed (service, api_version) in listening-sdk, the kit puts mappers under services/normalize-item/src/mappers/<platform>/; MAPPERS.md names the one place, agreed with F4, before wave 3 (DEFERRED.md section 3)"`.
- L193 (C5 summary) (finding 10): `item.hits versus discovery.hits by registry membership"` → `every keyword hit on item.hits, discovery.hits for candidates only (ADR-0031)"`
- L196 (C5 trap) (finding 10): `"keyword-matcher is the canonical writer of item.hits and discovery.hits for items (search output rule)"` → `"keyword-matcher is the only writer of item.hits, one per item, client and keyword whoever the poster is; it writes discovery.hits only for candidates, beside the other candidate writers (ADR-0031)"`
- L203 (C8 trap) (finding 10, corrected): `"Individuals are never profiled"` → `"Private individuals are never profiled: an ordinary individual's poster.profiles answer (account_type individual, not public) is minimised and keyed by author_ref, with no handle, name or URL; a public account's, creator's or public figure's answer carries its identity fields (ADR-0010, ADR-0033)"`
- L220 (C12 give) (finding 10): `"ADR on fallback scope (decision 5)"` → `"ADR-0021 (fallback scope; it supersedes README decision 5)"`
- L221 (C12 trap) (ruling 1): `"A source a government client watches, or a client-owned property, never falls back to amber (ADR-0021)"` → `"A green source a government client watches never falls back to amber; a client-owned property falls back under the same conditions as any other source, with the n8n notice to ops (ADR-0021)"`
- L228 (C14 trap) (finding 10): `"Purge raw text, never aggregates and derived scores"` → `"Purge by class: raw text on its class's clock, item-level derived rows (scores, hits, metrics) with their item; aggregates keep ten years and per-channel YouTube rollups 36 months, by F8's TTLs (ADR-0054, ADR-0056)"`
- L231 (C15 trap) (finding 10; ruling 3): `"Keep per-channel YouTube aggregates separable (cross-owner aggregation question is open)"` → `"YouTube figures stay per channel owner except where the carve-out allows totals; per-channel YouTube rollups keep 36 months and cross-owner ones ten years until counsel answers (ADR-0048, ADR-0056)"`
- L349 (X5 summary) (finding 10): `"Backfill and gap fill from the full archive"` → `"Backfill, keyword history and the X reply steps to day 30 from the full archive (ADR-0059, ADR-0064)"`
- L403 (A4 summary) (ruling 2): `"Images, thumbnails, OCR; no YouTube audio or video download in v1"` → `"Images, thumbnails, OCR, frame OCR and speech-to-text on media the register of permitted uses does not exclude; YouTube thumbnails only (ADR-0068)"`
- L404 (A5 summary) (finding 10): `"Alert rules over aggregates and hits, routed through n8n"` → `"Alert rules over the aggregate views, metrics_timeseries and item_stories, routed through n8n (ADR-0047, ADR-0048)"`

**build-plan/tools/gen_briefs.py**
- L163 (finding 10, `vendor_keys` to `credentials`, ADR-0016 L27): replace the `rows.append(f"- Tables read: …")` line with:
  ~~~
      def tbl(t):
          return "`credentials` (the PRD's `vendor_keys`, read and written only through the SDK's credential client, ADR-0016)" if t == 'vendor_keys' else f'`{t}`'
      rows.append(f"- Tables read: {', '.join(tbl(t) for t in io['reads_tables']) or 'see 6.1'}; written or updated: {', '.join(tbl(t) for t in io['writes_tables']) or 'see 6.2 and 6.3'}")
  ~~~
- L260 (finding 12): `items.append('The ADRs in `docs/decisions/` whose "Applies to" line names this session\'s ID, service, platform, lane or "all", or whose "Sessions that must read this" line names this session (ADR-0001); and the rows of `docs/decisions/DEFERRED.md` that name this session')`
- L307 (amber trap) (ruling 1)
  - Current: `and a source a government client watches or a client-owned property never falls back to it (ADR-0021);`
  - Replace: `and a green source a government client watches never falls back to it, while a client-owned property falls back under the same conditions as any other source (ADR-0021);`

**Regenerate the briefs:** `python3 build-plan/tools/gen_briefs.py . build-plan/tools/prd_index.json build-plan/tools/prd_io.json` (expect `briefs 125`), then `python3 build-plan/tools/validate.py`. Never edit `build-plan/sessions/*.md` or `SESSIONS.md` by hand.

---

## 7. docs/handoffs/D2.md

**L44** (finding 7c)

Current: `Every edited PRD passage cites its ADR, in the line or in the sentence that introduces the edited example.`

Replace: `Every edited PRD passage cites its ADR, in the line, in the sentence that introduces the edited example, or in a note right after the example.`

**L65** (finding 14; ruling 5)

Current: `The 70 decisions are the ADRs, all decided by the user on 7 Oct 2026, relayed by the orchestrator.`

Replace: ``The 70 decisions are the ADRs, all decided by the user on 7 Oct 2026, relayed by the orchestrator, with the user's follow-ups of 9 Oct 2026 on Q021, Q068 and the review's points (`D2-SUMMARY.md`, "Answers").``

**L71** (ruling 1)

Current: `A blocked source falls back to its vendor automatically where that route's flag is on, never for a government-watched green source or a client-owned property, and every`

Replace: `A blocked source, a client-owned property included (the user's follow-up of 9 Oct 2026), falls back to its vendor automatically where that route's flag is on, never for a government-watched green source, and every`

**L74** (finding 14)

Current: `All of it runs at budget priority 5, and the X sensitive-terms screen applies to every X term.`

Replace: `The X and news history runs at budget priority 5, and the X reply steps after +3 d at priority 3 (ADR-0018); the X sensitive-terms screen applies to every X term.`

**L75** (ruling 2), from `(an F3 table` to the end of the bullet

Replace:
~~~
(an F3 table written through the admin console; its entries are reviewed and set by the user or the user's compliance owner). A use is allowed unless its row says "not allowed" (the user's answer of 9 Oct 2026, "Allowed by default"), and F3 seeds a "not allowed" row for every use a platform's terms or a vendor contract already forbids, such as YouTube's video and audio downloads. `ai-train = no` always excludes a host, and YouTube stays thumbnails only unless an entry names YouTube's written permission.
~~~

**L83** (finding 4): append ``The `window_start` hand-back replaces the design the proposal left to X5 (`D2-PROPOSALS.md` L1977, L1987); the user accepted it on 9 Oct 2026, and X5 confirms it (`DEFERRED.md`).``

**Insert after L84** (finding 3):
~~~
- X `withheld` status comes from the daily compliance run alone, the rule of the recommended option (`D2-PROPOSALS.md` L1108), not the proposal's answer that every X reader requests it (L1120, L2397). The user accepted this on 9 Oct 2026 (ADR-0035).
~~~

**L90** (finding 7): after `fb-backfill; tg-bot-channel-receiver.`, append:
~~~
 The D2 fix session made the edits that ADR-0006, ADR-0019, ADR-0024, ADR-0025, ADR-0031, ADR-0040, ADR-0047, ADR-0050 and ADR-0057 name:
  - the id formats of the PRD examples (ADR-0006);
  - the early-stop text of the eleven comment and replies fetchers (ADR-0019);
  - tt-client-videos-fetcher's citations (ADR-0024);
  - an owner line in registry-writer, x-compliance-sync, alert-evaluator, tg-discussion-receiver, yt-pubsub-receiver, yt-video-details-fetcher, tt-client-videos-fetcher, web-commoncrawl-scanner and search-hit-router (ADR-0025);
  - the reader lines of tg-message-search, ig-hashtag-search, tt-keyword-search, tt-hashtag-feed-poller, li-post-search and yt-keyword-search (ADR-0031);
  - the gate state lines and registry sentences of the news services (ADR-0040);
  - `store-writer §4 L30` (ADR-0047);
  - three flag tests and `source-health-canary §13 L152` (ADR-0050);
  - five DLQ criteria (ADR-0057).

  An edited sentence carries no rule another ADR overrides. The rest of an edited paragraph, and every other overridden line, stays as written (ADR-0001).
~~~

**L92**: append ` After the review, the fix session also corrected the lines review finding 10 names (PLAN L17, REVIEW L23 and L26, G3 check 4, and the C5, C8, C12, C14, C15, F8, X5 and A5 lines of `sessions.py`) and the `vendor_keys` table name in the briefs (ADR-0016); G1 check 7, the C12 trap and the amber lane trap for your Q021 answer (ADR-0021); G2 check 3 (`DEFERRED.md`); the ADR routing line of the briefs (ADR-0001); and traps for F3, F4, C4, D3 and A4 (ADR-0068, ADR-0008, ADR-0021). The briefs were regenerated.`

**L94**: append ` After the D2 review, the fix session edited some of them: ADR-0021 for your Q021 answer of 9 Oct 2026, and others only to correct, cite or route them (`docs/reviews/D2.md`).`

**L99** (finding 12): two replacements.
- `names your service, platform, lane or "all"` → `names your session ID, service, platform, lane or "all"`
- `and the line "Sessions that must read this" at the end of each.` → ``and the line "Sessions that must read this" at the end of each. Then read the rows of `docs/decisions/DEFERRED.md` that name your session.``

**L111** (finding 1)

Current: `` `poster_profiles` with its public rows (ADR-0045, ADR-0010).``

Replace: `` `poster_profiles` with its public rows (ADR-0045, ADR-0010); both `client_lists` and `poster_profiles` are in the SDK purge registry, so deletion-propagator removes their rows (ADR-0035, ADR-0043).``

**L113** (ruling 2)

Current: `` `permitted_uses`, every row "not allowed" (ADR-0068);``

Replace: `` `permitted_uses`, allowed by default and seeded with the "not allowed" rows ADR-0068 lists, each with its clause, such as YouTube's video and audio downloads (ADR-0068);``

**L117** (finding 1)

Current: `and `public_accounts_dim` as the only way to list an author (ADR-0010, ADR-0047).`

Replace: `and `public_accounts_dim` as the only way to list an author, in the SDK purge registry (ADR-0010, ADR-0047, ADR-0035).`

**L121** (finding 5; drop the F5 clause if N1 is answered)

Replace: `F3 and F5: CONVENTIONS v1.1's cadence table names each source type's primary poller, the one writer of the `sources` rotation summary, which F3's `TABLE-OWNERS.md` records (ADR-0013, ADR-0015, ADR-0049); for news sites and web keyword-rule rows, which several services rotate, F5 names it (`DEFERRED.md`).`

**L123** (finding 2)

Current: `a client's deletion request (ADR-0054),`

Replace: ``a client's deletion request, which the admin API writes as a `deletions` message with reason `client_request` (ADR-0012, ADR-0054),``

**L132** (finding 11)

Replace: `2. Before G2, set a spending cap for staging on each vendor and API budget tag (ADR-0029), and the targets your 200-item labelled sample must meet in G2 check 3 (`DEFERRED.md` section 2).`

**L134** (ruling 2)

Replace:
~~~
4. Review the register of permitted uses, yourself or through your compliance owner, before training on platform content and media downloads begin; nothing waits for it. Every use is allowed unless the register says it is not. The register starts with a "not allowed" row for each use the platforms' terms already forbid: downloading YouTube video and audio. Change any row, and add one wherever a platform's terms or a vendor contract forbids a use. For each source we train on, say what deleting a training item requires (ADR-0068; your answer of 9 Oct 2026).
~~~

**L136** (finding 14, corrected for finding 22's split)

Replace:
~~~
6. Have counsel confirm the readings in `DEFERRED.md` section 1, each before its deadline. Several fall due well before production:
   - keyword matching over the 7-day news cache, before G2;
   - each vendor contract's limit, before that vendor's probe;
   - one PPCA read serving every client that watches a Page, before Meta App Review;
   - one tag list across a client's Instagram accounts, before IG2;
   - the Disqus API's terms, before N8;
   - who counts as a public figure, before A3;
   - whether Instagram creator accounts may be listed, before the first lane that shows author lists;
   - the new alert types for government clients, before A5.

   TikTok's and YouTube's readings, whether our LinkedIn access counts as "authenticated", and per-post LinkedIn history are due before each platform's go-live (G3). The rest are due before production (G4): the ten-year retention per class, each vendor contract's limit again, TikTok's reading again, LinkedIn's readings as a whole, GDELT's attribution, and the legal defaults for deletions and audits. Until counsel answers, the sessions build each ADR's default. As you confirmed on 9 Oct 2026, that means rollups of one YouTube channel keep 36 months and no Instagram creator account is listed.
~~~

**Insert after L148** (findings 8 and 9; ruling 4a):
~~~
- After the review, on your answers of 9 Oct 2026 (the review's point 4, "Accept all three", and Q021), the D2 fix session applied the review's texts to `CLAUDE.md` L43, L48 and L58, `.claude/rules/services.md` L12, `.claude/skills/review-session/SKILL.md` L17, L21 and L22, `.claude/agents/prd-reviewer.md` L13 and L15, and `.claude/skills/plan-session/SKILL.md` L17, L25 and L30 (ADR-0001, ADR-0015), and reworded `CLAUDE.md` L47 to drop the client-owned exclusion (ADR-0021).
~~~
**[N6]**: name the further lines applied, or list them there as left for the user.

**L150-L156** (finding 9): replace the whole subsection with:
~~~
### Applied after the review: `.claude/rules/services.md` L12

This rule loads for every service and SDK file. On your answer of 9 Oct 2026 to the review's point 4 ("Accept all three"), the fix applied the review's text (`docs/reviews/D2.md` L154). Each rotating service schedules from its own `cursors` row (`next_due_at`, `last_started_at`), and `sources.last_polled_at` and `next_poll_at` are a summary only the primary poller writes (ADR-0015, ADR-0041, ADR-0049). F2's producer table names every allowed producer, the X reply steps to day 30 and `keyword_history` included (ADR-0012, ADR-0059).
~~~

**L164** (final counts)

Current: `18 counsel confirmations, 9 settings and actions you own, 27 questions for the build sessions, and 191 PRD questions`

Replace: `26 counsel confirmations, 10 settings and actions you own, 30 questions for the build sessions, and 191 PRD questions`

**L177** (finding 3)

Current: `now resolved by the ADR's own rule. All in `303140e`, with CONVENTIONS.`

Replace: `now resolved by the ADR's own rule, which departs from the proposal's answer (`D2-PROPOSALS.md` L1120, L2397) and which the user accepted on 9 Oct 2026. All in `303140e`, with CONVENTIONS.`

---

## 8. Checks after applying

- `make fmt`, then `pnpm exec prettier --check` on the changed files under `docs/decisions/` and `docs/handoffs/`.
- `git diff --name-only origin/main...HEAD -- packages/contracts supabase/migrations clickhouse/migrations docs/contracts` prints nothing.
- `grep -rn "client-owned property never\|or a client-owned property\|own properties are never read" docs/decisions/ADR-*.md docs/prds/_shared/CONVENTIONS.md docs/prds/README.md CLAUDE.md build-plan` prints only option text (ADR-0021 L20, L24, L30; ADR-0052 L13, L23) and nothing in build-plan.
- `grep -rn 'not allowed" until\|every row "not allowed"\|defaults to "not allowed"' docs build-plan CLAUDE.md .claude` prints only the D2-SUMMARY follow-up and ADR-0068 L11, which are records.
- `grep -rln "degrade and stop\|see \`degraded\`\|and gap fill\|never aggregates and derived\|aggregates are kept ten years\|over aggregates and hits\|versus discovery.hits\|canonical writer of item.hits\|aggregation question is open\|fallback scope (decision 5)\|provenance and retention_class present" build-plan/` prints nothing.
- `grep -n '\`vendor_keys\`[,;]' build-plan/sessions/*.md` prints nothing.
- `grep -l "the PRD's \`vendor_keys\`" build-plan/sessions/*.md | wc -l` gives 26.
- `grep -n 'robots\.\|next_slot_at\|`robots`' docs/prds/news/*.md` prints nothing.
- `grep -c "kurmanji\|badini" -i docs/decisions/DEFERRED.md` gives 1 or more.
- The row counts in DEFERRED sections 1 to 4 are 26, 10, 30 and 191.
- Item 12's routing script (R12a and R12b), run from the repository root with `python3 -B`, prints `unrouted 0`.
