# F2 fix round: the orchestrator's decisions and verified approaches

Brief for the F2 fix session. It is context written by the orchestrator, not evidence. The review, `docs/reviews/F2.md` at `96f1db0`, states what is wrong. This file records the orchestrator's decisions on the review's open choices, and an approach for each item. Seven independent verifiers checked every approach against `sb/F2` at `96f1db0`, reading only and running nothing from the package's suites.

Status of the items:
- The verifiers confirmed every finding, 1 to 10, every note, 11 to 22, and the review's late item. None was refuted.
- They judged the severities right. Finding 3 and note 14 touch the non-negotiable on private individuals, and they recommend treating both as merge-blocking.

Use the approaches as guidance. Where the code shows a better way that meets the same decision, take it, and record why in the handoff's Review section. For line numbers, see "How to work".

## Scope of this round (decided by the orchestrator on 25 Oct 2026)

The contracts freeze when this lane merges. After that, ADR-0002 L23 and VERSIONING.md L13 make any narrowing, any changed type or meaning, and any changed golden vector a new version with a dual-publish window, through `/contract-change`. Most of the notes cost little now and a new version later. So this round fixes:
- every blocker and should-fix finding, 1 to 10;
- every note, 11 to 22;
- the review's late item: the Instagram-hashtag fixtures with `vendor: ensembledata` (review L1166);
- one item the verifiers found while checking note 12, which the review does not hold. The orchestrator adds it to scope: government-keyword-level's `details.fingerprint` uses the person-and-source prefix as its scope key, but its scope is the keyword, and alert-evaluator.md L63 makes the keyword the scope key (D-11);
- three doc corrections the verifiers found, which the orchestrator also adds: VERSIONING.md L95, and handoff L107 and L185.

`/fix-session` covers blockers and should-fix findings only. This round widens it, by the orchestrator's decision, to the notes, the late item and the orchestrator-added items. Record each orchestrator-added item in the handoff's Review section as orchestrator-added. The skill's other rules apply to every item in scope:
- test first;
- commits per finding;
- touch nothing else;
- if you find an item is wrong, explain it with evidence in the Review section and leave it.

Two items are records only, with no code change in this lane:
- **Python packaging** (a wheel carries no `registries/` or `schemas/` JSON). Keep plan L11's editable install. Add a line to the handoff for F6 and for the Python service template: they copy the contracts package into the image at the path the editable install points to, and install it editable.
- **F1's `scripts/check-fixtures.sh` L38 Telegram-token pattern** (false positives on full-length Facebook and Instagram ids). This is outside F2's scope, so do not edit it. Record it as a bullet "**For the orchestrator**: ..." under the handoff's "Open items", with the review's evidence (review L1168), for a kit follow-up lane.

Nothing else is in scope. Do not change what the review did not raise.

## The orchestrator's decisions

All are technical choices inside the ADRs and the approved plan, decided by the orchestrator on 25 Oct 2026.
- Record each one in the plan, in a new "Fix-round decisions" list under "Revision notes" with the D-number.
- Record each one in the handoff's "Decisions made here", and in VERSIONING.md where it states a rule.
- None credits the user.

- **D-1 (findings 1 and 4, the dead-letter copy rule).** The record copies the original's provenance under the original's own type.
  - That type is the signal provenance, with a nullable route, for an author-, source- or client-scope deletion, and the data provenance otherwise.
  - `retention_class` is copied only when the original has a valid one.
  - Null, absent and unknown classes are alike in both languages.
  - The rule never throws.
  - This is the verifiers' option (ii), which keeps plan L119 and ADR-0003 L28 exact.
- **D-2 (finding 7, Unicode version).** NFC and lower-casing are frozen at Unicode 15.1.0 in both languages. Code points unassigned in 15.1 pass through unchanged and are never refused. A runtime below 15.1 is refused at import.
  - Do not refuse newer code points: that would throw on every post holding a recent emoji.
  - Do not try to pin both runtimes to one Unicode version: Python 3.13 stays on 15.1, and no supported Node line has it.
- **D-3 (finding 8, provenance on tier_change and dormant).** Bind the decision-producer row to `rule_hit`:
  - a `tier_change` under rules 6 and 10 requires provenance (it applies a resolver profile, ADR-0003 L26);
  - a `tier_change` or `dormant` under rule 9 (the sweep over stored statistics) refuses provenance;
  - a `dormant` under rule 3 keeps provenance optional, because rule 3 runs both in the sweep and on a profile and the message does not say which;
  - any other `rule_hit` for these two decisions is refused (plan L291 to L292).

  This is the verifiers' option (a), with rule 10 included.
- **D-4 (finding 10, issue paths).** Option A:
  - exact path parity for the 13 discriminated unions;
  - the branch-label fix in Python's `_path`;
  - TypeScript's `?? null` fix so absent equals null;
  - a stated residual for the six plain unions (registry.decisions, poster.profiles, items.analysis, raw.items, n8n.alert `details`, a push job's `body`), where the two path sets may differ in either direction:
    - on a shape error, Python lists every failing branch;
    - on a constant given as the other JSON type (finding 6), Python reports only the matched branch's path, while TypeScript also lists the other branch's errors;
  - a required golden, `fixtures/contracts/golden/issue-paths.json`, holding TypeScript's path set for every invalid and tolerant fixture in both modes.
    - Produce it with a committed script that runs TypeScript's `validate()`, after the round's last `gen:fixtures`.
    - Check a sample of each union's entries by hand against the fixtures' `expected.json`, and record the sample in the handoff.
    - Under the discriminated unions, both suites assert equality with it. Under the plain unions, both suites assert that their set contains every path in the fixture's `expected.json`; neither asserts a superset.

  Do not emulate Zod's internal plain-union rule.
- **D-5 (note 17, edge inputs).**
  - Both `validate()`s refuse a free-form value (a payload, body, metrics or details map) nested deeper than 64 levels, counted from that value, not from the message root. The code is `not_json`, at the path of the 65th container, in both languages.
  - Both refuse a `__proto__` key anywhere in a message, with `not_json` at `[..., "__proto__"]`.
  - Both return issues and never throw on any JSON input. The `constructor` and `toString` lookups use own-property checks.
- **D-6 (note 19, VERSIONING.md L21, the `account_type` marks).** ADR-0002 L23 makes a change of meaning a new version, and `validate()` enforces the marks and `PERSON_UNLISTABLE_PLATFORMS` in both modes. So changing a mark or that list, as counsel's answer on Instagram creators may, is a new version of `poster.profiles` with the dual-publish window.
  - State that in L21, and list the two mark sets and `PERSON_UNLISTABLE_PLATFORMS` with the closed lists of L19.
  - Whether Instagram creators may be listed at all stays the user's question with counsel (Q7, the plan's DEFERRED rows).
  - The verifiers recommended a `/contract-change` inside v1. The orchestrator chose the ADR's reading instead (ADR-0001).
- **D-7 (note 19, VERSIONING.md L29 to L36, the window's reach).** Wording (c):
  - The window covers the topics and the job queues.
  - The n8n notices travel over HTTP and are not covered. The rule for their first new version is set by that version's `/contract-change` proposal.
  - When that proposal comes, the orchestrator takes to the user whether clients' own webhooks get notice or choose their version.
- **D-8 (note 21, individuals' handles and ids in the package).** A plausible handle could belong to a real person, and golden vectors cannot change after the merge.
  - Replace x-recent-search's example poster, `abuali_basra` with id `1290000000000000045`, by an obviously invented handle and id (for example `example_poster_x` and `1000000000000000001`). Do it everywhere the package holds them:
    - the generator;
    - the 22 fixture files that hold the handle, `golden/partition-keys.json` among them;
    - `registry.decisions/v1/invalid/mention-only-two-subjects.json`, which holds the id;
    - the four unit-test files: `test/unit/poster-profiles.test.ts` L15 and L17, `test/unit/provenance.test.ts` L162, `python/tests/test_poster_profiles.py` L22 and L24, and `python/tests/test_provenance.py` L138.
  - Do the same for public-person-individual's `dr_ali_basra` and id `1290000000000000999` (`data_topics.py` L1626 to L1628), and set its `url` from the new handle.
  - Wherever note 21's approach restores a PRD post by a private person (fb-keyword-search's group post), replace that person's id and name with invented ones.
  - Replace the PRD-literal `author_ref` strings with references derived under the published test key from invented ids.
  - Add a rewrite line to `prd-examples.json` for prd-x-recent-search and prd-keyword-matcher: "the poster's handle and id replaced by invented ones (D-8)".
  - Fix the fixtures README so it says truly how individuals appear.
  - Finish the item with `git grep -nE 'abuali|ali_basra|12900000000000000(45|999)' -- packages/contracts fixtures`, which must print nothing.
- **D-9 (note 11, part iv).** The two `jobs.completed` rules that read registry data run in consumer mode only for a service the package knows (`isKnownService`), and always in producer mode. Parts (i), (ii), (iii) and (v) are fixed as the approach below says.
- **D-10 (note 15, part a).** Plan L165's specific `search_response` clause governs over its general "`candidate_key` on any kind": only web-commoncrawl-scanner's aggregate may omit `source_id`.
- **D-11 (the government fixture).** Fold the fingerprint fix into note 12's change.
- **D-12 (dead-letter records of a malformed original, finding 4).** As D-1: when the original's provenance fails its own type, the record carries neither provenance nor class (plan L397, "otherwise both are absent").

## How to work

Follow `/fix-session F2`. Test first: write the failing test or fixture, show it failing for the stated reason, then fix it and show it passing.

Commits:
- One commit per finding, so a recheck can find each fix.
- Notes may share a commit per area, with the note numbers in the message.
- Every commit message starts "F2 fix:" and names its finding or note numbers.

Order:
1. Findings 1 and 4, with note 22's code comment and guard test, in one commit: "F2 fix: findings 1 and 4, note 22: the dead-letter copy rule". Then finding 2.
2. Finding 3, note 14, finding 9, note 21 (with D-8) and the ensembledata item.
3. Findings 5 to 8 and 10, one commit each.
4. Notes 11 to 13 (the government fingerprint with note 12, D-11), then 15 to 18.
5. Notes 19 and 20, with note 22's VERSIONING sentence and the orchestrator-added doc corrections. Write these last, so the handoff and VERSIONING.md describe the code as it ends up.

Throughout:
- **Fixtures.** Every fixture goes through the generator (the package's `scripts/fixtures/`), never by hand: `gen:fixtures` deletes and rewrites every fixture directory except `golden/`.
  - The lone-surrogate fixtures (finding 5) need a writer option in `common.py` that escapes non-ASCII (`ensure_ascii=True`), since the UTF-8 write cannot hold a lone surrogate.
  - The `1e400` fixture (note 17) needs a raw-text writer that emits the token `1e400` (`json.dumps` would write `Infinity`).
  - Where an approach below says "no generator change", it means no JSON Schema or Pydantic model change.
- **Generated files.** JSON Schema and Pydantic models come from the exporters, never by hand.
- **Golden vectors.** They may change only where D-8 says so, or where an approach adds or renames a vector (finding 2's query-key vectors, finding 7's `keys.json` section) or adds a file (D-4's `issue-paths.json`).
  - Recompute each new or changed key or hash vector with a separate standard-library implementation, as the build did.
  - Record each change in the handoff.
- Keep TypeScript and Python in step in every commit.
- **Line numbers.** They are exact in `git show 96f1db0:<path>`. Find each line there, then edit it in the current file by its quoted text, because earlier commits of this round move them.
- **Superseded alternatives.** Where an approach below still offers an alternative that a decision above settles, follow the decision.

If the round does not fit in one session:
1. Stop only at an item boundary: the item's test and fix are committed together and `make check` passes.
   - Never commit or push a test without its fix.
   - If you are mid-item, finish it, or discard its uncommitted changes so the tree equals your last commit.
2. Write the handoff's Progress section: each item done with its commit SHA, the next item, and the commands to resume. Commit it, run `make check`, and push.
3. End with ORCHESTRATOR: NEEDS-INPUT. Say first that this is a continuation and nothing is needed from the user, then give the pushed SHA and the `make check` result.

The stop gate is armed for `/fix-session`. At every stop it reruns the checks and sends you back while they fail; with green checks it lets you stop. So do not file a q-file for a continuation. Only if the checks fail for a cause you cannot fix in this session, file `docs/issues/F2-q<n>.md` (see the protocol) saying so, and write in Progress that the successor removes it with `git rm`.

## Verified approach for each item

### Finding 1 (blocker): the dead-letter record and non-item deletions

Fix findings 1 and 4 in one change. The exact rule is in the 'review shape' item below.

Tests first, in both languages. Add them to test/unit/provenance.test.ts and python/tests/test_provenance.py, and add the fixtures through scripts/fixtures/control_topics.py dlq() (around L3491), then run gen:fixtures.
1. 'a dead letter of an author-, source- or client-scope deletion copies its provenance and no retention_class (F-42, F-08)'. Use the five non-item deletion fixtures as `message`, on the consume and the produce side:
   - a faithful copy (provenance, no class) passes;
   - the same with any retention_class fails at ['retention_class'];
   - copying nothing fails at ['provenance'].
2. New valid fixtures: dlq/v1/valid/consume-author-deletion.json (author-request), produce-client-offboarding.json (retention-purger's chunk) and consume-source-deletion.json (source-authorization-revoked).
3. New invalid fixture: invented-class.json (a non-item deletion with a class added), expected path ['retention_class'].

Then the code:
- src/dlq.ts:27: `provenance: signalProvenance(b).optional()`.
- The validate.ts dlq rule (:725-777) and its Python twin `_dlq` (:798-848), as the rule spec below says.
- Regenerate with export:schemas, gen:python and gen:fixtures. schemas/dlq/v1.json then refers to SignalProvenance, and dlq_v1.py may no longer hold a `Provenance` class, so Python imports both strict types from models/strict/deletions_v1.py, which has both (L58, L92).
- Docs: rewrite VERSIONING.md L111 to say what is copied when. Update handoff L149 the same way, and fix L177 (see finding 4).

No change is needed to registryChecks: it already skips the vendor check on a null route (validate.ts:932, validate.py:996).

### Findings 1 and 4: the copy rule's exact clauses (D-1, D-12)

The rule for both validate()s.

Definitions:
- O is the original's provenance (message.provenance, else message.envelope.provenance, when it is an object).
- C is the retention_class read from the same holder.
- T is the original's own provenance type: SignalProvenance when message.schema is 'deletions/v1' and message.scope is author, source or client; Provenance otherwise. Use TS `signalProvenance`/`provenance` built with createBuilder('producer'), and Python `SignalProvenance`/`Provenance` from models/strict/deletions_v1.py with model_validate(..., strict=True).
- copyable means O is an object that strict T accepts.
- classCopyable means copyable holds and C is one of RETENTION_CLASSES, so null, absent and unknown classes are alike in both languages.

Clauses:
1. provenance present: no message gives provenance_without_message, as today. Otherwise, if T in the validating mode does not accept O, or jsonEqual(m.provenance, O) is false, give provenance_not_copied. The consumer variant tolerates unknown keys, so a producer-valid record is always consumer-valid.
2. provenance absent and copyable: provenance_not_copied.
3. retention_class present: no provenance gives provenance_without_class, as today. Otherwise, if classCopyable is false or the class is not C, give class_not_copied. Skip this clause when clause 1 already reported provenance_without_message, to avoid a double report.
4. retention_class absent, provenance present and classCopyable: class_not_copied. This replaces the dlq rule's call to checkPairing (validate.ts:766, validate.py:838).

Field type: src/dlq.ts:27 becomes `signalProvenance(b).optional()`. Leave `retention_class` as `retentionClass().optional()`.

Tests and fixtures: those listed under findings 1 and 4, plus one invalid fixture, null-route-not-a-deletion.json (an items.normalized original whose route is null, copied), expected path ['provenance'].

Regenerate, then update VERSIONING.md L111 and handoff L149 and L177. Record in the handoff that the record carries a null route only when its original is an author-, source- or client-scope deletion.

### Finding 4: the dead-letter rule throws or splits

This goes in finding 1's change, through the same rule.

Tests first, in both languages:
1. 'validate() returns issues and never throws on a dead letter whose original's provenance holds a lone surrogate or a non-finite number'. Build the inputs with JSON.parse('"\\ud800"') and JSON.parse('1e400') in TypeScript, and "\ud800" and float('inf') in Python. Assert no throw, and that both languages give the same verdict. Python refuses inf up front with not_json; if finding 5's whole-message check lands in the same session, both languages also refuse the surrogate up front.
2. 'a dead letter copies nothing from an original whose provenance fails its own type'. Route RED and a null route on an items.normalized original fail on copy in both modes, and 'both absent' passes. For an original whose provenance has an extra key, producer mode refuses the copy at ['provenance']. Consumer mode accepts both the copy and 'both absent' (clause 1), so a producer-valid record stays consumer-valid.
3. 'an original whose retention_class is null, absent or unknown gives a record with the provenance copied and no class, in both languages'. A record with any class fails at ['retention_class'].
4. Fixtures: valid consume-malformed-provenance.json; invalid null-class-copied.json, expected ['retention_class'].

Code: in validate.ts's dlq rule, replace `sameJson` with a structural JSON equality that ignores key order and never throws (or at least wrap it in try/catch returning false), and apply the copyable checks from the rule spec. Make the Python twin match. Docs: fix handoff L177's claim, or make it true.

### Finding 2 (blocker): A14's NFC half

Test first, both languages, before finding 7.

1. fixtures/contracts/golden/query-key.json:
   - Rename vector 2 to "the same forms in another order". Its key and canonical stay the same.
   - Append two exact vectors. (a) "composed forms and context term": forms ["أحمد","Café"], context_terms ["إنترنت"], canonical {"context_terms":["إنترنت"],"forms":["café","أحمد"]}, query_key ff8961cfc49a761e913a47f4410b08d7822f2ca4e9c3a2baf6b748e5a3531493. (b) "the same forms and context term decomposed": forms ["أحمد","Café"], context_terms ["إنترنت"], with the same canonical and query_key. Write the decomposed strings as \u escapes.
   - Do not use a folded vector: U+0654 and U+0655 fall in the stripped tashkeel range, so the mutant would survive it.
   - Append at the end, because g.keys[0] is used by "every platform starts at exact".
2. Rewrite the A14 test in query-key.test.ts L36-40 and test_query_key.py L24-27, keeping the plan's name:
   - assert every string of the decomposed vector is not NFC;
   - assert queryKeyWithProfile("exact", dec.forms, dec.context_terms) / query_key_with_profile(...) equals the composed vector's stored key;
   - keep the order assertion against the renamed vector.
   The parameterised golden test now also runs the helper on the decomposed input.
3. Show the mutation: remove `nfc(` at query-key.ts:37 and keys.py:304; the new test and the decomposed golden case fail in both suites; restore. Record it in the handoff's A14 row, as A33 records its mutation.

### Finding 3: poster.profiles individuals (non-negotiable)

Test first:
- In packages/contracts/scripts/fixtures/data_topics.py, beside `individual-full-set` (around L1654), add two invalid fixtures, both with expected path ["public_account"]:
  - `individual-public-null`: {**xp, account_type "individual", individual True, public_account None, an invented handle, display_name and url}.
  - `creator-public-null`: {**xp, account_type "creator", individual False, public_account None}.
- Use X for both. On TikTok, Instagram and LinkedIn, `person_unlistable` already fires at the same path, so the test would pass before the fix.
- Add unit tests to test/unit/poster-profiles.test.ts and python/tests/test_poster_profiles.py:
  - "rejects a typed account whose public_account is null", over X, Facebook, YouTube and Telegram, individual and creator, with status resolved, review and unresolvable.
  - "accepts public_account null only with account_type null", using the existing review-age-gated and unresolvable-not-found shapes.
- Run both suites and see them fail.

Fix:
- In src/validate.ts, after the `type === null` return (L368), add `if (m.public_account === null) out.add(["public_account"], "public_unmarked", "a typed account is marked public or not (ADR-0010 L59, ADR-0033 L26)")`.
- Add the same in validate.py after L425.

Docs:
- Plan L257: add "public_account is null exactly when account_type is null (ADR-0010 L59, ADR-0033 L24, L26)".
- Update the header comment in poster-profiles.ts.
- Add a handoff line for F4/F6: the individuals-rule function returns true or false whenever account_type is set. It returns true for an organisation kind, and false for a person kind on TikTok, Instagram or LinkedIn. For any other person kind it returns true when the account is verified, and otherwise true only at or above the follower threshold, which admits no account until its feature_flags row exists (ADR-0010 L56, L58 to L59, L70 to L72).

Then regenerate the fixtures and run both conformance suites.

### Note 14: analysis-entities' person guard (non-negotiable)

Test first: in the generator (data_topics.py, items.analysis section), add two invalid fixtures built from prd-analysis-entities:
- `entities-person-without-id`: appends {type "person_public", entity_id null, start 0, end 9, source "model", surface "…"}, expected path ["result","entities",1,"entity_id"].
- `unlinked-person`: unlinked [{type "person_public", surface, start, end}], expected path ["result","unlinked",0,"type"].

Run conformance in both languages and see both accepted.

Fix:
- In vocabulary.ts, add `UNLINKED_ENTITY_TYPES = ["brand","company","institution","place","product"]` (ENTITY_TYPES less person_public; PRD L67, L71) and use it for UnlinkedEntity.type. Regenerate schemas/vocabulary.json, the JSON Schemas and the Python models.
- In both validate()s, add a rule: for each entities[i] with type "person_public" and entity_id null, refuse at ["result","entities",i,"entity_id"] with "a person mention is linked or dropped, never kept unlinked (analysis-entities §5.3 L69)".
- Keep entities-private-person.json.
- Add one line to plan L365 citing PRD L69, L71 and L131.

### Finding 9: two PRD rewrites

Test first: add a fixture-consistency unit test (in test/unit/fixture-coverage.test.ts or a new file) that asserts:
- (a) every valid poster.profiles fixture whose provenance.service is ig-account-resolver has account_type business_or_creator or null;
- (b) every non-GDELT valid search.results fixture with non-empty client_ids has a non-null query.lang and non-empty keyword_ids.

It fails on the two fixtures today.

Fix in data_topics.py:
- `prp`: set account_type="business_or_creator" and public_account=False (individual stays False). Add a prd() note: "account_type business becomes business_or_creator, public_account false: ig-account-resolver writes business_or_creator (Q7; ig-account-resolver.md L60, L92; ADR-0010 L72)".
- `br`: set query lang "ar" and country "IQ", and drop the `keyword_ids=[]` override so the default ["0cd402b6-9015-45f8-86b4-d90cc086d320"] applies. Add a note: "lang ar and country IQ from the Mojeek call's lb=AR&rb=IQ (L83; ADR-0037 L24); keyword_ids the rule's enabled keyword (ADR-0044 L30)".

Regenerate and run both suites. The derived invalid `cached-reemit-not-cached` (L1720) is still refused for `cached`.

Do not add a validate() rule for lang or keyword_ids. A non-GDELT query may ask no language (Sorani where the engine has no ckb, PRD L78), and a row being retired may briefly carry no keyword, so a rule would narrow the contract beyond what the review raised.

### Note 21: fixture drift (D-8)

Test first: add a fixture-chain unit test in both languages asserting:
- the registry-writer event's producer.job_id equals the qualifier decision's, and the qualifier's equals the poster-resolver profile's;
- each first_sight job's producer.job_id equals its sibling raw record's job_id;
- news.dedup duplicate_of equals the extractor fixture's idempotency_key;
- public-person-individual's url ends with its handle;
- container-group's group is the one its item's raw record names;
- every generated author_ref recomputes under the test key.

It fails today.

Fix in the generator:
- First, D-8: replace `abuali_basra`, `1290000000000000045`, `dr_ali_basra` and `1290000000000000999` with obviously invented handles and ids, everywhere D-8 lists.
- Make the three job_ids copy or share their chain ids.
- Derive duplicate_of from the extractor's key with the helper, not as a literal.
- Set public-person-individual's `url` from its new invented handle (D-8).
- Replace raw_items.py:210, :261 and :311 with ref("<invented id>", "facebook").
- Restore fb-keyword-search's PRD group post: the PRD L76-L83 payload with its group context, the author's id and name replaced by obviously invented ones (D-8), keyed per ADR-0007, and no author_ref (Q3). Point container-group.json at facebook:group:271936048205533 with that post's item_id. Record both in the manifest notes.

README L24 is not generated and not guarded. Rewrite it to say what is true:
- the ids of public pages, channels, groups and outlets are the PRD examples' illustrative ones;
- every individual's id, handle and name is invented, and every `author_ref` is derived under the published test key from an invented id (D-8);
- a discovery poster's clear id and handle appear only on the bus messages ADR-0010 L49 allows, and in reject cases;
- individual.json is x-recent-search's poster, with its invented id, under the test key.

Leave the per-service platform_sync example as a note: it is additive, and the FB comments session writes its own fixtures.

### Late item: Instagram hashtag fixtures with vendor ensembledata

Change control_topics.py L458 and L1534 from "ensembledata" to "sociavault", then regenerate and run both suites.

Test first: a fixture unit test asserting that every valid fixture's amber vendor is one its platform's flag allows (CONVENTIONS L430). Keep the mapping inside the test. It should cover messages that carry `platform` plus the update-budget-wait-amber decision, which can be named or joined by its source_id. It fails today on the source event.

Do not move the platform-to-vendor binding into registries/validate() here. That is note 11's question, not this item's.

### Finding 5: lone surrogates

Write the tests first. Today each fails in one language.

1. Add invalid fixtures, each with an entry in its `expected.json`, writing the escapes as `\ud83d` in the JSON text:
   - `fixtures/contracts/dlq/v1/invalid/error-message-lone-surrogate.json`: `consume-data-message.json` with `error.message` ending in `\ud83d`, path `["error","message"]`. TypeScript fails today.
   - `item.hits/v1/invalid/matched-term-lone-surrogate.json`, path `["matched_term"]`.
   - `raw.items/v1/invalid/payload-lone-surrogate.json`: an unconstrained payload string, which Python also accepts today.
   - One fixture with a lone surrogate in an object key, path `[..., key]`.
   - Rule text: "every string and key is well-formed Unicode (UTF-8 encodable, ADR-0006)".
2. Add unit tests in both languages: `refuses a lone surrogate anywhere in a message with not_unicode, in both modes, without throwing` (issues exactly `[{path, code: "not_unicode"}]`) and `accepts a well-formed emoji in the same place`.

Then the code:
- In `src/validate.ts`, add a pre-walk before `schema.safeParse` (L1098) that returns its issues early, as `validate.py` L1176-1178 does:
  - a string with `!s.isWellFormed()` gets `not_unicode` at its path;
  - an own key of a plain object gets the same check, at `[...path, key]`;
  - recurse only into arrays and plain objects;
  - skip `undefined`, since `JSON.stringify` drops it and Zod judges optional fields.
- In `python/listening_contracts/validate.py` `_as_json` (L131-146), check every `str` value and every dict key with `try: s.encode("utf-8") except UnicodeEncodeError: out.add(path, "not_unicode", ...)`. This is `_text.require_str`'s test, without raising.
- Use the helpers' code and wording: `not_unicode`, as in `keys/text.ts:8` and `_text.py:20`.
- Docs:
  - handoff L127-129: strings are well-formed Unicode in both languages;
  - VERSIONING.md "Producers validate strictly": the same rule;
  - a line for F3 and F6: truncate by code point, with `String.prototype.toWellFormed()` or `Array.from(s).slice(0, n).join("")`.

No JSON Schema or Pydantic model changes. The fixtures go through the generator: give `common.py` a writer option that escapes non-ASCII (`ensure_ascii=True`) for the lone-surrogate fixtures, since the UTF-8 write cannot hold a lone surrogate.

### Finding 6: Pydantic literals 0/1 against false/true

Write the tests first. TypeScript already refuses all of these; Python's conformance suite fails until the fix.

1. Add invalid fixtures:
   - `fixtures/contracts/poster.profiles/v1/invalid/public-account-zero.json`: `individual.json` with `public_account: 0`, path `["public_account"]`.
   - `job/v1/invalid/tier-true.json`: `rotation.json` with `tier: true`, with its queue in `options.json`, path `["tier"]`.
   - `raw.items/v1/invalid/context-partial-one.json`: `prd-yt-keyword-search.json`, path `["envelope","context","partial"]`.
   - `crawl.policies/v1/invalid/rsl-found-one.json`, path `["rsl","found"]`.
   - `item.hits/v1/invalid/occurrences-false.json`, path `["occurrences"]`.
2. Add a Python unit test over the 20 sites in both modes: `refuses a constant given as the other JSON type (0 for false, true for 1)`.

Then the code, in `validate.py` only:
- After `model.model_validate(message, strict=True)` succeeds (L1180), dump once: `dumped = parsed.model_dump(mode="json", by_alias=True)`.
- Walk `dumped` against `message`: dict keys present in both, lists by index.
- Where `isinstance(a, bool) != isinstance(b, bool)`, add an issue at the walked path with code `literal_error` and the message "a constant keeps its JSON type".
- Return those issues before the rules, and reuse `dumped` as the returned value at L1197.

Why the check is sound:
- A coerced literal is the only bool/number swap strict Pydantic makes: strict int and bool fields refuse the other type, and int to float stays a number.
- It also covers future constant sites.
- In consumer mode, unknown fields are absent from the dump and are skipped, as Zod drops them.
- `by_alias` keeps the `schema` alias, so dump keys equal input keys.

Paths:
- They equal TypeScript's under discriminated unions: job `tier` gives `[["tier"]]`.
- Under poster.profiles and raw.items, plain unions, Python reports only the matched branch's path, while TypeScript also lists the other branch's errors (review L560). That is D-4's residual, in the direction where TypeScript lists more (`poster.profiles/v1/invalid/public-account-zero.json`, `raw.items/v1/invalid/context-partial-one.json`).

Add one line to the handoff's "Python's validation semantics".

No generated files change. Do not fix it in the generator: there is no datamodel-code-generator flag for it, rewriting its output contradicts `gen_python.py:6-7`, and `Annotated[Literal[True], Strict()]` fails at class build (review L583).

### Finding 7: Unicode 17 against 15.1 (D-2)

Recommend the review's first remedy (one frozen Unicode 15.1 list in both languages), but pass those code points through instead of refusing them.

Why not "refuse": it would throw in contentHash (content-hash.ts:5) and idlessCommentKey (idempotency.ts:131) for every post or comment carrying a Unicode 16+ emoji such as U+1FAE9, and do so forever inside v1. No ADR allows dropping text, and ADR-0009 hashes every item's text. A list of only the 66 normalisation code points would also miss the lower-case divergences, including the review's own U+A7CB, and whatever Unicode 18 adds.

Why not "pin both": it cannot be done here.
- Python 3.13.x stays on 15.1 for good.
- No supported Node line carries 15.1.
- Matching would mean Python 3.15 project-wide (F1's toolchain and all three Python services, outside the plan) plus an exact Node pin that gives up ICU-bumping minors.
- Every later bump would still re-key data, which VERSIONING L74 makes a new version, in lockstep across 86 services.

The pass-through freeze is exact. Under 15.1, an unassigned code point is a starter with no decomposition, no composition and no case. So NFC_15.1(a u b) = NFC_15.1(a) u NFC_15.1(b), and for runs of assigned characters any runtime ≥ 15.1 gives the 15.1 result (normalisation stability). Python's output is unchanged, Node 24 matches it, and later runtime upgrades change nothing. Plan L74 is the only Unicode mitigation in the plan, and it names a test.

Steps, after finding 2:
1. Failing test first, in both languages: keys.test.ts :: "the golden NFC vectors hold in both runtimes" and test_keys.py :: test_the_golden_nfc_vectors_hold_in_both_runtimes. Add a new section to golden/keys.json, computed with Python 3.13 (the 15.1 reference):
   - (i) U+0628 U+0897 U+0650 U+0631: contentHash sha256:e656da10b1f33c570aeb11e6d96d7ae2add8b1c24763de2356138ac6eb7809cb, queryKey("x") 15c52309fafcb671a2779f87772c91b59ba25b29dbf399ddf9a13072b6629e3f, and idlessCommentKey("facebook","1_2","2026-10-06T09:15:42Z") facebook:comment:1_2:af6222b3f4211df1e70b738fe601b57a009c5f9887763e98cf9c2ae30e700207;
   - (ii) an item key whose platform_id holds U+105D2 U+0307, kept as is;
   - (iii) a urlKey whose host holds U+A7CB, not lower-cased;
   - (iv) text with U+1FAE9, hashed and not refused;
   - (v) the plan's own set: an Arabic presentation form such as U+FEFB, Sorani letters, and a skin-tone ZWJ sequence.
   On Node 24.21.0, (i) to (iii) fail today (the review shows e86a2085... and 5aa43b60...). Python passes before and after; say so in the handoff.
2. Add packages/contracts/registries/unicode-15.1-unassigned.json: the 707 [first,last] ranges of category Cn in 15.1.0, surrogates excluded, generated once from Python 3.13's unicodedata and loaded like query-folding.json.
3. In text.ts and _text.py, nfc(s) and a new lowerCase(s) / lower_case(s) take a fast path when s holds no listed code point. Otherwise they split s into runs at listed code points, normalise or lower-case each run, and keep the listed code points unchanged. Route url.py's `_nfc` through `_text.nfc`. Use the new lower at query-key.ts:37 / keys.py:304, candidate-key.ts:45 / keys.py:411 and url.ts:237 / url.py:188. The ASCII-checked lower-casing (idempotency.ts:85, url.ts:290, candidate-key.ts:58) may stay as it is.
4. At import, refuse a runtime whose Unicode version is below 15.1 (process.versions.unicode, unicodedata.unidata_version) with ContractError("unicode_version"). Test it through an exported checker that takes the version string.
5. Test the list itself:
   - Python: when unidata_version == "15.1.0", the list equals the Cn set;
   - TS: every code point that is \p{Cn} in the runtime is in the list;
   - TS: no 15.1-assigned code point's NFD or lower-case output holds a listed code point.
6. Docs:
   - VERSIONING.md "Frozen namespaces and golden vectors": NFC and lower case are those of Unicode 15.1.0, and unassigned code points pass through unchanged. Moving the version is a new version. Record the final-sigma residuals at U+0295 and U+1171E as a note, with no fix: Node 24 (Unicode 17) and Python 3.13 (Unicode 15.1) lower-case a capital sigma next to either one differently ("AΣʕ" gives σ in Python and ς in Node).
   - Plan L74 and L659: point to the new test.
   - Handoff L92: correct the claim and add the before/after.
No existing golden vector or fixture changes.

### Finding 8: tier_change and dormant provenance (D-3)

For option (a). Tests first in both languages, then data and code, then docs.
1. Tests:
- producer-table.test.ts:230 and test_producer_table.py:197-199: replace the single "optional" case. Queries now carry rule_hit: tier_change 6 -> required, 10 -> required, 9 -> refused; dormant 9 -> refused, 3 -> optional. Add tier_change rule_hit 4 and dormant rule_hit 6 -> decision_not_allowed.
- provenance.test.ts (~L100-130) and test_provenance.py (~L110): pass `rule_hit: block?.rule_hit` into the decisionRow query. Otherwise the per-fixture row lookup finds no row.
- registries.test.ts:184 and test_registries.py:136: `rule_hits`, where present, are integers 1-10.
- Fixtures, through the generator (scripts/fixtures/control_topics.py near L538-611, then gen:fixtures, never hand-edited):
  - valid: `dormant-decay.json` (rule 9, no provenance); `tier-change-review.json` (rule 10, provenance, requested_by a `person:` ref)
  - invalid, with expected.json codes: `tier-change-profile-without-provenance` (provenance_required), `tier-change-sweep-with-provenance` (provenance_refused), `dormant-decay-with-provenance` (provenance_refused), `tier-change-rule-not-allowed` (rule_hit 4, decision_not_allowed)
2. Code:
- src/registries/producers.ts: DecisionFile row gets `rule_hits: z.array(z.number().int().min(1).max(10)).optional()`; DecisionQuery gets `rule_hit?: number | null`; rowMatches adds `(row.rule_hits === undefined || (typeof q.rule_hit === "number" && row.rule_hits.includes(q.rule_hit)))`.
- src/validate.ts:935 checkDecisionRow passes `rule_hit: rec(m[decision]).rule_hit`.
- Python twin: registries.py DecisionRow gets `"rule_hits": NotRequired[list[int]]`, DecisionQuery gets `rule_hit`, `_row_matches` matches; validate.py:1000 `_check_decision_row` sets query["rule_hit"].
3. Data: decision-producers.json L73-80 becomes three rows:
- {tier_change; rule_hits [6,10]; required; from "ADR-0003 L26; qualifier.md L57, L61, L108"}
- {tier_change, dormant; rule_hits [9]; refused; from "F2: rule 9, the sweep over stored statistics, qualifier.md L46, L60"}
- {dormant; rule_hits [3]; optional; from "rule 3 runs in the sweep and on a profile, qualifier.md L46, L54: the message does not say which"}
Add `rule_hits` to the description at L2.
4. Docs:
- Plan L314: reword to the three cells, with a Revision note naming the orchestrator's decision.
- VERSIONING.md: the D-3 sentence in note 19's "Decisions with and without provenance (F-14)" section; no separate entry.
- Handoff L139: as note 20 says.
- Handoff, for the qualifier and registry-writer: set rule_hit truthfully. Copy the profile's provenance and class onto every decision taken on a profile: rules 6 and 10, and a rule-3 dormant decided on a profile. The contract accepts a rule-3 dormant either way, so only the qualifier keeps ADR-0003 L26 there. Never copy them onto a sweep decision: rule 9, or a rule-3 dormant from the sweep.

### Finding 10: Python issue paths (D-4)

This is option A. Write the tests first.

1. Python unit test `reports only the selected branch of a discriminated union`:
   - `deletions/v1/valid/author-request.json` plus `batch_size: 500` gives paths `== [["batch_size"]]`;
   - `job/v1/invalid/carries-priority.json` on `jobs.fb-page-feed-poller` gives `[["priority"]]`.
2. Python unit test `reports a bad discriminator at the discriminator`: a deletion with `scope: "nobody"` gives `[["scope"]]`.
3. Python sweep over every invalid and tolerant fixture in both modes: no path step is a branch label (`missing-sentinel` or a generated class name), and every non-final step exists in the message.
4. TypeScript unit test: the review's consumer-mode source-level `health_change` carrying `platform` gets no `["health_change","fallback"]` or `["health_change","scope"]` issue, as in Python.
5. Required (D-4): a golden `fixtures/contracts/golden/issue-paths.json` with TypeScript's path set for every invalid and tolerant fixture in both modes, produced and checked as D-4 says. Under the discriminated unions both suites assert equality. Under the six plain unions both assert that their set contains every path in the fixture's `expected.json`; neither asserts a superset.

Then the code:
- `_path` (validate.py L152-172): take the error type. Append a trailing step that is absent from the value only for `missing` and `extra_forbidden`; otherwise it is a branch label, so drop it.
- Branch selection in `validate.py` (around L1182), for the 13 discriminated unions:
  - Find each discriminator from the committed schema's `oneOf` (the shared `const` property other than `schema`; each branch's `title` is its class name under `--use-title-as-name`), or by inspecting the generated classes' `Literal` fields.
  - Keep a branch's errors only when the input's tag equals that branch's tag with the same JSON type.
  - When no tag matches, or the tag is absent, replace that union's errors with one issue at the union path plus the discriminator, as Zod does.
  - When the value is not an object, report one issue at the union path.
  - Deduplicate identical paths.
- `src/validate.ts:463-464` and `:474`: `const fallback = block.fallback ?? null;` and `(block.scope ?? null) !== scope`, so absent equals null as in `validate.py`.
- Docs (README L8, handoff L108 and L129): "the same paths, except under the six plain unions (registry.decisions, poster.profiles, items.analysis, raw.items, n8n.alert `details`, a push job's `body`), where the two path sets may differ in either direction, as `golden/issue-paths.json` records: on a shape error Python lists every failing branch, and on a constant given as the other JSON type TypeScript also lists the other branch's errors".

No generated files change. The alternative is to have the exporter write a `discriminator` into each `oneOf` so that datamodel-code-generator emits `Field(discriminator=...)`. That changes the committed schemas and models and needs the generator's support verified, so it is not needed.

### Note 11: registry checks with gaps (D-9)

All five parts are fixed (D-9). Order: (v), (iv), (i), (ii), (iii). Tests first, in both languages.
(v) Bind engine and vendor:
- Generator fixtures for search.results/v1/invalid: `perplexity-vendor-null.json` (engine perplexity, provenance.vendor null) and `mojeek-vendor-perplexity.json`, both refused in both modes with a new code `engine_vendor`.
- validate.ts:598 searchResults and validate.py:672 `_search_results` add: `if (rec(m.provenance).vendor !== m.engine) out.add(["provenance","vendor"], "engine_vendor", "a result names its engine as provenance.vendor (ADR-0051 (c), (e))")`.
- Add one line to the plan's search.results section. All five existing fixtures stay valid.
(iv) Consumer-mode registry reads in jobs.completed:
- Test cases: consumer mode accepts a report from `jobs.x-newsvc` carrying paid_user_reads, and from an unknown queue whose job is keyed by crawl_id with no source_id; producer mode still refuses both (unknown_service, missing_key or x_field).
- jobsCompleted (validate.ts:655-685) and `_jobs_completed` (validate.py:730-745): run the x_field loop and checkJobKey only when `ctx.mode === "producer" || isKnownService(service)`. That keeps every consumer check for the services this package knows, and stops refusing services a newer package adds.
- Update the header comment (validate.ts:6-10 and the Python docstring) and the topic-writers.json L2 wording.
(i) Vendor changed without its route:
- Add `isListedVendor(v)` (amber ∪ green lists) to services.ts and registries.py.
- At validate.ts:1035 and :1041 and validate.py:1104 and :1111: when vendor is present, non-null and route is absent, refuse an unlisted vendor with `unknown_vendor`.
- Invalid fixtures: a registry.decisions `update` with source {vendor: "acme"} and a source.events `updated` with previous {vendor: "acme"}. Valid counterpart: a vendor-only update naming a listed vendor.
(ii) n8n vendors: in registryChecks for n8n.alert/v1, check `subject.vendor` and `details.vendor` with checkVendor when the sibling route is present, else with isListedVendor. One invalid fixture per path.
(iii) Dead letters:
- In registryChecks for dlq, refuse an unknown `consumer.service` (`unknown_service`) and one that differs from the service the schema names (`dlqService(m.schema)`; new code `consumer_mismatch`), per CONVENTIONS L41's one dlq.<service> per service.
- Two invalid fixtures. Add one sentence to VERSIONING.md "Dead letters".

### Note 12: n8n government rule gaps (with D-11)

Tests first in n8n.test.ts and test_n8n.py, plus invalid fixtures in fixtures/contracts/n8n.alert/v1/invalid with expected.json entries:
(a) government-scope-level.json: government-keyword-level.json with details.scope.level `keyword_source`, client_type government. Expected ["details","scope","level"] government_scope.
(b) government-subject-candidate-key.json, and one with subject.route `green`. Expected ["subject","candidate_key"] / ["subject","route"] government_subject.
(c) fallback-to-client.json: source-fallback-notice.json with audience client, a client_id and client_type commercial. Expected ["audience"] fallback_audience.
Code in validate.ts n8nAlert and validate.py _n8n_alert:
(1) Before the audience return at :817: `if (details.subject_kind !== undefined && m.audience !== "ops") out.add(["audience"], "fallback_audience", "an automatic-fallback notice goes to ops (ADR-0021 L58)")`. This also closes the government fallback that names details.source_id or details.platform.
(2) In the government branch, replace the two-name subject loop with an allow-list: every subject key other than keyword_id and request_id gives government_subject. Today that equals adding candidate_key, route and vendor to the two names. It also fails closed for an optional subject field added inside the version.
(3) `if (scope.level !== undefined && scope.level !== "keyword")` gives government_scope at details.scope.level.
Update VERSIONING L118, README L8/L199 and the handoff's A30 line to list the paths.

### Late item: the government fixture's fingerprint (D-11)

Test first: assert that the third part of government-keyword-level's fingerprint is the first 8 hex digits of its keyword_id. Then, in n8n_topics.py, pass `fingerprint="volume_spike:5d0c2b7e:9a8b7c6d"` to that fixture's client_alert(...), through its **extra overrides (L79). Leave the other client alerts alone, and run gen:fixtures. Commit it with note 12.

### Note 13: the government rule fails open

Tests first:
- TypeScript: validate("n8n.alert/v1", prd-alert-evaluator.json, "producer", { clientType: null as never }), and the same with "Government" as never. Both give [["","no_client_type"]].
- Python: client_type="Government" and client_type="" give no_client_type.
Code:
- validate.ts: `const given: unknown = ctx.options.clientType; const clientType = includes(CLIENT_TYPES, given) ? given : undefined;` and keep the existing branches.
- validate.py: `client_type = ctx.client_type if ctx.client_type in VOCABULARY["CLIENT_TYPES"] else None`.
In consumer mode an unknown value then behaves like an absent one, as today. Reword README L199 and VERSIONING L118 to 'without it, or with a value other than commercial or government'. No fixture or schema change.

### Note 15: plan L165 archive keys (D-10)

Invalid fixtures first in fixtures/contracts/raw.items/v1/invalid with expected.json entries:
- search-response-candidate-key.json: search-response.json (web-search-mojeek) with source_id replaced by candidate_key `news:site:example-daily.iq`. Expected ["envelope","source_id"] missing_subject.
- search-response-commoncrawl-source-id.json: search-response-commoncrawl.json with candidate_key replaced by a source_id. Expected ["envelope","candidate_key"] missing_subject.
- article-key-not-the-canonical-urls.json: prd-news-article-extractor.json with payload.canonical_url set to another page. Expected ["envelope","idempotency_key"] key_mismatch.
Code in rawItems and _raw_items (both modes):
(a) `if (env.kind === "search_response") { const aggregate = rec(env.provenance).service === "web-commoncrawl-scanner"; if (aggregate && !hasCandidate) add [envelope,candidate_key] missing_subject; if (!aggregate && hasCandidate) add [envelope,source_id] missing_subject }`
(b) `if (env.kind === "article" && typeof rec(m.payload).canonical_url === "string") { const want = derive(() => articleKey(canonical)); if (want !== env.idempotency_key) out.add(["envelope","idempotency_key"], "key_mismatch", ...) }`
Leave a null canonical_url unchecked: the PRD's extractor always resolves one (L69) and the plan does not cover null. Record both rules in VERSIONING and the handoff. Finding 7's Unicode-version split would carry into (b) for code points assigned after 15.1, and finding 7's fix covers it.

### Note 16: job-shape rules the plan states

Invalid fixtures first in fixtures/contracts/job/v1/invalid, each with its queue in expected.json:
- comments-thread-ids.json (fb-post-comments-fetcher), metrics-thread-ids.json (fb-reactions-fetcher), first-sight-thread-ids.json (yt-video-details-fetcher). Expected ["post_ref","thread_ids"].
- x-replies-thread-ids.json: replies-x-window.json plus thread_ids, on x-full-archive-search. Expected ["post_ref","thread_ids"].
- replies-window-start.json: replies-thread-ids.json plus window_start, on yt-replies-fetcher. Expected ["window_start"].
- x-gap-with-reason.json: reconciliation-x-gap.json plus reason lease_lapsed, on x-recent-search. Expected ["reason"].
All use code field_refused.
Code in both languages:
(1) A kind rule that runs in both modes and needs no queue: comments, metrics and first_sight refuse post_ref.thread_ids. Leave refresh, reconciliation and ops_force alone: they were not raised, and an ops_force may need thread ids on yt-replies-fetcher.
(2) A `refused_fields` list in producers.json with the same row shape as `required_fields`, read beside requiredJobFields (validate.ts:718 and its Python twin), checked in both modes once a queue is given. Rows: x-full-archive-search replies refuse post_ref.thread_ids; fb-group-comments-fetcher, tt-video-comments-fetcher and yt-replies-fetcher replies refuse window_start.
(3) A code rule: reconciliation `reason` is refused unless queueService(queue) is yt-uploads-reconciler. The allowed set is one queue of about 35, so a registry row would list the other 34.
Record the rules in the handoff's 'Decisions made here'.

### Note 17: edge inputs (D-5)

Write the tests first.

1. TypeScript unit tests:
   - `validate("raw.items/v1", ...)` on `metrics.json` with `envelope.producer.service: "constructor"` returns `ok: false` with `[["envelope","producer","service"]]` `unknown_service`, and does not throw;
   - the same for poster.profiles with `provenance.service: "constructor"`;
   - `partitionKey("toString", {})` and `partitionKey("constructor", {})` throw `ContractError` `unknown_schema`;
   - `declaredExtrasKeys`, `rawItemsKinds` and `visibilityRule` return null for "constructor", and `declaredContextKeys` returns empty lists.
2. Fixtures for both suites:
   - `raw.items/v1/invalid/payload-number-1e400.json`: write `1e400` literally, through the generator's raw-text writer (`json.dumps` would write `Infinity`). Python's conftest `parse_constant` refuses only `NaN`/`Infinity`, so it loads as `inf`. Path `["payload","like_count"]`, `not_json`; TypeScript fails today.
   - `raw.items/v1/invalid/payload-nested-too-deep.json`: N is 64, counted from the free-form value (the payload), not from the message root. A payload 65 deep, path of the 65th container, `not_json`; Python throws today.
   - A valid fixture whose payload is exactly 64 deep.
   - Per D-5: `n8n.alert/v1/invalid/metrics-proto-key.json`, `not_json` at `["details","metrics","__proto__"]`.
3. Python unit test: a payload nested 255 levels deep returns issues and does not raise.

Then the code:
- TypeScript registries: replace inherited lookups with own-property ones (`Object.hasOwn(r, k) ? r[k] : undefined`, as `getPath` does) at `declared-keys.ts:26`, `:27`, `:36`; `partition-keys.ts:28`; `producers.ts:142`, `:191`, `:194`; `visibility.ts:19`, `:25`.
- Extend finding 5's pre-walk, with the same codes and paths in both languages:
  - a non-finite number gives `not_json` (new in TypeScript; Python already does it at `validate.py:137-139`);
  - nesting deeper than N containers gives `not_json` at the first container beyond N, in both languages;
  - an own key `__proto__` is refused in both languages.
- `canonicalJson`: no code change. Add one line to the handoff and to the `canonical-json.ts` header: callers pass no numbers; integers beyond plus or minus (2^53 - 1) are refused in Python and already rounded by `JSON.parse` in TypeScript.
- Docs: handoff L128 and L177 and the `validate.py` docstring become true in both languages. Add the depth bound and the `__proto__` rule to VERSIONING.md "Producers validate strictly".

No generated files change.

### Note 18: calendar-invalid times

Tests first, in both languages:
- Pattern tests: 2024-02-29 and 2000-02-29 accepted; 2100-02-29, 2026-02-30, 2026-04-31 and 0000-01-01 refused.
- An invalid fixture, for example job/v1/invalid/produced-at-february-30.json, expecting ["produced_at"].
- rawRef with date 2026-02-30 throws bad_raw_ref.
Then put the verified pattern in PATTERNS.timestamp:
^(([0-9]{3}[1-9]|[0-9]{2}[1-9]0|[0-9][1-9]00|[1-9]000)-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29)T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]{1,3})?Z$
PATTERNS.date takes the same date part between ^ and $. Regenerate schemas/patterns.json, the committed JSON Schemas and the Pydantic models with the package's generator; never edit generated files by hand (.claude/rules/contracts.md L12). Record in VERSIONING L8 that message times are calendar times from 0001 to 9999.

### Note 19: VERSIONING.md L9

Doc only, in docs/contracts/VERSIONING.md. No test is needed; versioning-doc.test.ts still passes because the catalogue is untouched.
(1) Replace L9 with: "- A data message (one that carries or derives from a platform fetch) carries `provenance {route, vendor, service, fetched_at}` and `retention_class`. A control message (`job/v1`, `jobs.completed/v1`, `source.events/v1`, the dead letters and the n8n notices) carries `producer` and no `provenance` (ADR-0003); a source event's `retention_class` is the source's registry column, not a class of the message. Three exceptions, each under \"F2's readings\": an author-, source- or client-scope deletion carries no `retention_class`, and null `provenance.route` and `provenance.vendor` when its signal is no fetch (F-08); a `registry.decisions/v1` message carries `provenance` and `retention_class`, or neither, as its producer row says (F-14); and a dead letter copies a parsed data message's `provenance` and `retention_class` (F-42)."
(2) After "### Multi-item deletions (F-07)", add "### Deletions that involve no fetch (F-08)": "F2's reading of ADR-0003 L28 for signals that involve no fetch (ADR-0070 L28): an author-, source- or client-scope `deletions/v1` message carries the signal's `provenance` and no `retention_class`. When its reason is no platform fetch (`author_request`, `client_offboarding`, `client_request`, `legal`, `retention`), `provenance.route` and `provenance.vendor` are null, while `provenance.service` (the service that received the signal) and `provenance.fetched_at` (when it arrived) stay required; a reason that is a fetch (`platform_sync`, `authorization_revoked`) names its route. `validate()` checks both in both modes (`route_without_fetch`, `fetch_without_route`, `vendor_without_route`). An item-scope deletion carries its items' provenance and class (F-07). Fixtures: `deletions/v1/valid/author-request.json`, `client-offboarding.json`, `client-request.json`, `source-authorization-revoked.json`; `deletions/v1/invalid/route-on-author-request.json`, `null-route-on-platform-sync.json`, `class-on-author-scope.json`."
(3) Add "### Decisions with and without provenance (F-14)": "`registry.decisions/v1` is a data topic, but a decision carries `provenance` and `retention_class`, or neither, as its producer row in `registries/decision-producers.json` says (the plan's producer rows). They are required where the decision reports what a fetch or a platform call returned (ADR-0003 L26 names the qualifier's decisions from resolver profiles, news-robots-checker's crawl refusal and the canary's `health_change`). They are refused where a person entered the decision, which carries `requested_by` instead (the D3 writers, ADR-0003 L26), and where the decision reports state with no fetch behind it (a lease or subscription, a budget, an offboarding, a sweep over stored statistics, except a rule-3 `dormant`, below). The qualifier's `tier_change` and `dormant` are bound to `rule_hit` (`rule_hits` in `registries/decision-producers.json`). A `tier_change` under rule 6 or 10, which applies a resolver profile, requires provenance. A `tier_change` or `dormant` under rule 9, the sweep, refuses it. A `dormant` under rule 3, which runs both in the sweep and on a profile, accepts either, because the message does not say which. Any other `rule_hit` for these two decisions is refused (`decision_not_allowed`, at `["producer", "service"]`). Decided by the orchestrator on 25 Oct 2026 (D-3); review finding 8. The two travel together in both modes. Producer mode checks the row (`provenance_required`, `provenance_refused`, at `provenance`); consumer mode accepts either. Fixtures: `registry.decisions/v1/valid/add-keyword.json` (refused), `prd-source-health-canary.json` (required); `registry.decisions/v1/invalid/provenance-required.json`, `provenance-refused.json`."

### Note 19: VERSIONING.md L25

Replace only the L25 bullet's own text with two bullets. Keep the rules that findings 5 and 17 added to this section earlier in the round (well-formed Unicode; non-finite numbers, nesting deeper than 64, `__proto__`) as separate bullets after the two new ones.
"- `validate(schemaId, value, mode, options)` in TypeScript and `validate(schema_id, value, mode, queue=..., client_type=...)` in Python run the schema, then the cross-field rules JSON Schema cannot express, then, in producer mode, the registry checks: the service, vendor and requester names, the topic writers, the decision producers and the declared `context` and `extras` keys. Producer mode refuses an unknown field. Consumer mode accepts an unknown field of a known version and drops it (A32; the `tolerant/` fixtures)."
"- A few cross-field rules read registry data and so apply in consumer mode too. A job validated with its queue is checked in both modes against its producer-table row, its kind's required and refused fields and its queue's partition-key field (`kind_not_on_queue`, `producer_not_allowed`, `missing_field`, `field_refused`, `missing_key`), since the consumer's wrapper dead-letters a job the table does not list (ADR-0012 L31). A `jobs.completed/v1` report's partition-key field (`missing_key`) and its `paid_user_reads` and `free_rereads` (`x_field`, an X service's queue only) are checked always in producer mode, and in consumer mode only when the report's queue names a service the package knows (`isKnownService`, D-9), so a report from a service that a newer package adds is not refused. So a row added inside the version to the producer table, the required or refused fields, or the partition keys of a service the consumer's package already knows reaches that queue's consumers before any producer sends under it: the consuming service is released on the new package first."
Also append to L17's sentence "... and no schema changes version": "; the rows that consumer mode reads ship consumers first (\"Producers validate strictly, consumers tolerantly\")".

### Note 19: VERSIONING.md L29 to L36 (D-7: use wording (c))

(1) Replace L31 with: "**Decided by the orchestrator on 25 Oct 2026 (Q17), as ADR-0002 L23 and L32 leave to this file.** It covers the topics and the job queues, where a new version is published on the same topic or queue beside the old one (ADR-0002 L23). No schema has a second version yet, so nothing depends on the length until the first one ships."
(2) Add item 5, in wording (c) (D-7): "5. The n8n notices (`n8n.alert`, `n8n.card`) travel over HTTP, with no offsets to switch on, and a notice sent in both versions would reach n8n or a client's own webhook twice under one `Idempotency-Key`. This window does not apply to them; the rule for their first new version (the plan expects `n8n.alert/v2` once the alert metrics are named, Q11) is set by that version's `/contract-change` proposal."

### Note 19: VERSIONING.md L95, the F-17 pair

In L95, replace "`items.normalized/v1/valid/prd-normalize-item.json` from that `raw.items` record" with "`items.normalized/v1/valid/prd-normalize-item.json` carries the `producer.job_id` of `raw.items/v1/valid/prd-fb-page-feed-poller.json` (the two fixtures are of different posts; the pair shows only the copied id)".

### Note 20: handoff statements

Write the handoff last, after the code fixes.
Test first: add the plan-named test from L80 (TS only, as the plan names it) to packages/contracts/test/unit/catalogue.test.ts: `it("schema ids are unique and every id has one version", () => { const ids = CATALOGUE.map((e) => e.id); expect(new Set(ids).size).toBe(ids.length); for (const id of ids) expect(id).toMatch(/\/v\d+$/); })`. Show it failing once by duplicating a CATALOGUE row (mutation), as the handoff does for other rows.
Exact corrected lines:
- L22: "`fixtures/contracts/` holds <N> contract fixtures (<valid> valid, <invalid> invalid, <tolerant> tolerant) and 12 golden files. 85 of the valid ones, `*/valid/prd-<service>.json`, are PRD 6.2 examples rewritten under the ADRs; `prd-examples.json` lists them in 94 entries, with 9 examples that are no messages and why." Fill in the counts by recounting after the last gen:fixtures.
- L58 (A6 result): "85 rewritten examples, one per producer and topic, each with its rewrite notes in `prd-examples.json`, whose 94 entries also say why 9 PRD examples are no messages (93 fenced blocks; keyword-matcher's maps to two topics); pass".
- L86 (A34 result): "before: no README; after: both print the README's output block. The TypeScript test runs the block with Node, which strips types without checking them; no committed check type-checks the block."
- L87 (A35 result): "\"every new runtime dependency has its row in docs/dependencies.md\": the runtime dependencies `zod`, `canonicalize`, `pydantic` and `rfc8785`. `datamodel-code-generator` is in the `dev` dependency group, which the check skips as a tool; it has its row too. All five are cleared against the vendor screen."
- L92: correct it as finding 7 says, with the before and after; the uniqueness test above is added, so L80's case has its own test.
- L107: "A decision-row refusal is reported at `[\"producer\", \"service\"]` when no row lets the producer send the decision (`decision_not_allowed`), and at `[\"provenance\"]` when its row requires or refuses provenance (`provenance_required`, `provenance_refused`)."
- L108: "A shape error's `code` and `message` come from Zod or Pydantic and differ between the languages. Its path is the same in both, except under the six plain unions (registry.decisions, poster.profiles, items.analysis, raw.items, n8n.alert `details`, a push job's `body`), where the path sets may differ as `golden/issue-paths.json` records. The package's own rules use the same codes and paths in both."
- L129: "Error paths drop Pydantic's branch labels and keep only the selected branch of a discriminated union (D-4)."
- L139: "None in the shapes or the helpers. In the registries, the qualifier's `tier_change` and `dormant` row of plan L314 is split by `rule_hit` (D-3, recorded in the plan's revision notes): rules 6 and 10 require provenance, rule 9 refuses it, and a rule-3 `dormant` accepts either, because rule 3 runs both in the sweep and on a profile and the message does not say which (review finding 8)."
- L147: keep it; note 17's own-property lookups make it true.
- L177: "A helper given bad input throws `ContractError`, and `validate()` turns a key helper's refusal into a mismatch issue. `validate()` itself returns issues and never throws on any JSON input (D-5, findings 4 and 5, note 17)."
- L185: "The DEFERRED rows that touch F2's shapes are in the plan (L588 to L606), each with the kind of change it would be under VERSIONING.md's rules."

### Note 22: the dead letter's catalogue class

Fold it into finding 1's change; it is text only, plus one guard test.
- catalogue.ts:26: add 'except the dead letter, which copies a data original's provenance and class (F-42)'. A short inline comment at :52 would also help.
- VERSIONING.md L9: say that the dead letters copy them from a data original (F-42).
- Test first, in both languages: 'validate's control set is the catalogue's control ids except dlq.<service>/v1', which pins the intended difference between the two lists.
- Keep `class: "control"`. Do not add a third class: it widens the public surface for no change in behaviour. 'data' would break A18's 'every data schema requires provenance', because dead letters of jobs carry none.

### Note 19: VERSIONING.md L21 (D-6, the orchestrator's choice, not the verifiers')

Replace L21 with this, keeping its decision and ADR citations: "The marks on `account_type` (organisation kind or person kind, Q7) and `PERSON_UNLISTABLE_PLATFORMS`, the platforms on which no person kind is listable (ADR-0010 L70 to L72), are not part of a message's shape, but `validate()` enforces them in both modes (`organisation_public`, `person_unlistable`), so a consumer's verdict depends on them. Changing a mark or that list, as counsel's answer on Instagram creators may, changes what a message means: it is a new version of `poster.profiles`, with the dual-publish window (ADR-0002 L23; decided by the orchestrator on 25 Oct 2026, D-6)."

In L19, list `ORGANISATION_ACCOUNT_TYPES`, `PERSON_ACCOUNT_TYPES` and `PERSON_UNLISTABLE_PLATFORMS` among the closed lists that grow only through a new version. In the plan's DEFERRED row on Instagram creators (L606), set the consequence to "a change to the marks of Q7 or to `PERSON_UNLISTABLE_PLATFORMS`: a new version of `poster.profiles`, with the dual-publish window (D-6)", and add a revision note naming D-6. Add the same sentence to the handoff's "The user (Q7)" bullet (L160).

## Finish

- Update the handoff's Review section: each finding and note, with its fixing commit, or why it was left; the decisions D-1 to D-12; and the two record-only items.
- Update the counts, the A-rows whose evidence changed, and the Progress line.
- Run, and record the results:
  - `make check`;
  - `make test SERVICE=contracts`;
  - `POLICY_BRANCH=sb/F2 make policy BASE=origin/main PR_LABELS=contract-change`;
  - the regeneration commands, in order, as one command: `source /opt/nvm/nvm.sh && nvm use 24.21.0 >/dev/null && pnpm --filter contracts export:schemas && pnpm --filter contracts gen:python && pnpm --filter contracts gen:fixtures`, then the `issue-paths.json` script (D-4). Then `git status --porcelain`, which must come back empty.
  - Locally, `make policy` should fail only at `check-handoff-review`, because the review still says "needs fixes".
- Run Prettier as one command: `source /opt/nvm/nvm.sh && nvm use "$(cat .node-version)" >/dev/null && pnpm exec prettier --check --ignore-unknown <the files you changed>`.
- Push, then read the head's check runs on Abdullah95k/securebrand-v2#13 over REST, read-only. Fix any failure you cause.
  - `policy` stays red until a recheck reads "ready to merge"; that is expected.
- End with ORCHESTRATOR: DONE, giving:
  - each item and its commit;
  - the `make check` result;
  - the test and fixture counts in both languages;
  - the CI result;
  - the pushed SHA.
