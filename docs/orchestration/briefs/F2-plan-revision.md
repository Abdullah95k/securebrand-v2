# F2 plan revision: role and brief

Written by the orchestrator on 25 Oct 2026 for the F2 plan-revision session on `sb/F2`. The session's system prompt names this file and its commit; it is part of that session's instructions.

## Role

You revise `docs/plans/F2.md` (at `5fd54a4` on `sb/F2`) before the build. A fresh plan session wrote it and asked 12 questions. The orchestrator then had five independent readers check it against the ADRs, CONVENTIONS v1.1, `docs/contracts/INVENTORY.md` and the PRD 6.2 examples, and a sixth agent re-checked their findings. That check confirmed 54 findings (2 blockers, 32 should-fix, 20 notes) and rejected 13, and it answered the 12 questions plus 4 new ones. The user answered the two questions that are theirs on 25 Oct 2026.

Apply everything below to the plan, and nothing else:

- Write no code and no tests. Change only `docs/plans/F2.md`.

- Keep the header `Approved by: pending (orchestrator)`.

- Before applying each finding, check its evidence against the files yourself. If a finding or a correction is wrong, do not apply it. Record it under a new section "Revision notes" with your evidence, and the orchestrator decides.

- Apply every blocker and should-fix. For a note, apply the correction when it is small and plainly right. Otherwise record it under "Open items for the build", with what the build must decide or check.

- Record every answer in the plan's "Questions and answers" table with its attribution, exactly as given below. Add Q13 to Q16 as new rows.

- Where an answer or finding changes a field set, a helper, a golden vector, the acceptance map or the build outline, update every place in the plan that depends on it, so the plan stays self-consistent.

- Commit in a few groups (`F2 plan: <what> (orchestrator's check of 25 Oct)`) and push after each commit.

- Run `nvm use 24.21.0 >/dev/null && pnpm exec prettier --check docs/plans/F2.md` and `make check` (after `make bootstrap`, with the uv workaround if bootstrap stops at the uv step).

- End with ORCHESTRATOR: DONE and a table of every finding F-01 to F-54 and every question Q1 to Q16, each with its disposition (applied, recorded as an open item, or not applied and why) and the commit. Give the pushed SHA.

## The user's answers (25 Oct 2026)

Record each as "decided by the user, relayed by the orchestrator on 25 Oct 2026".

### Q2: the form of `deletion_id`

The orchestrator's question to the user, in plain words:

> Every deletion request (a person asks to be forgotten, a client leaves, X tells us a post was deleted) gets an ID, so the system can safely ignore an exact duplicate of the same message. Your decision (ADR-0035) says the ID is built from 'what is being deleted'. Taken literally, two different people's requests, or two clients leaving, could get the same ID, and the second would be silently skipped. How should the ID be built?

The user chose **"Who + kind + day"**: "Build it from who or what is deleted, the kind of deletion, and the day the request arrived. Every separate request is carried out; an exact repeat of the same message is still ignored."

In the contract: `deletion_id` = `del:<reason>:<scope>:` followed by the hex SHA-256 of the RFC 8785 canonical JSON of `{key, mode, signal_day, target}`. `key` is the scope's top-level key value (`author_ref`, `source_id` or `client_id`; for item scope, the item's `source_id`), and every array in `target` is sorted. `signal_day` is the UTC date the signal arrived (the day the person's request, the client's offboarding or the platform's compliance signal was received, as each producer's PRD names it).

Record that this reads ADR-0035 L24's "whole sorted target" as including the subject key ADR-0035 itself moved to the top, plus the mode and the day, as the user chose. Update the A15 golden vectors, the helper and finding F-01.

### Q10: how `query_key` normalises a keyword's forms and context terms

The orchestrator's question to the user, in plain words:

> When two clients track the same search words, we search, and pay, only once. How strictly should 'the same words' be judged? Arabic is often typed with small spelling differences: أ, ا or إ; ة or ه; ى or ي; Persian versus Arabic letters; vowel marks.

The user answered in their own words: **"Depends on the platform as some are variants sensitive and others are not."**

The rule this records: on a platform whose own search treats those spelling variants as the same, `query_key` treats them as the same search; on a platform whose search distinguishes them, each spelling stays a separate search.

The mechanism is the orchestrator's technical choice, so label it as the orchestrator's, not the user's:

- The contracts package holds a per-platform folding profile with two profiles, both with golden vectors:

  - `exact`: Unicode NFC and lower case only;

  - `folded`: NFC, lower case, tashkeel and tatweel removed, alef forms (أ إ آ) merged to ا, ة to ه, ى to ي, and Persian ک and ی to Arabic ك and ي.

- `query_key` hashes the forms and context terms under the row's platform profile: normalised, deduplicated and sorted, with no service call.

- Every platform starts at `exact`, which never merges two searches its platform would answer differently. A platform moves to `folded` only when its probe session records that its search treats those variants as the same, through a `/contract-change`, since the keys change.

- Record a DEFERRED-style open item per platform: "probe: does the platform's search fold Arabic spelling variants?".

- Searchers still query every form of every keyword on a row (ADR-0044 L31), so neither profile loses coverage.

## The orchestrator's answers

Record each as "decided by the orchestrator on 25 Oct 2026". Each was checked against the ADRs by the orchestrator's verification; the evidence is given.

### Q1: How may a closed list gain a value inside a version?

Reject option (a). A new enum value is not 'a change that only adds an optional field' (ADR-0002 L21, L23), and (a) would have v1 consumers read unknown values as 'other' instead of reading, skipping or parking a version. Follow ADR-0002 as written (option b), and cut its cost with choices that stay inside it. (1) Service names, D3 writer names and vendors are not schema enums: `producer.service`, `provenance.service`, service-valued `requested_by` and `actor`, and `provenance.vendor` are lower-case patterned strings, checked in producer mode against registry data, as the producer table already is (plan L424). The amber reader the user asked for (D2-SUMMARY L252) then adds registry rows, not a version of every schema (F-09). (2) `context`, `extras` and `evidence` keys are optional fields, which ADR-0002 already lets grow inside the version. (3) Every other closed list (registry and event reasons, profile reasons and review_flags, completion reasons and statuses, kinds, scopes, modes, observation labels, `found_via`, `evidence_type`, the lang-dialect-id labels) gains a value only through a new version with the dual-publish window. VERSIONING.md states both mechanisms.

Evidence: ADR-0002 L21, L23. D2-SUMMARY L218 (Approve all), L252. DEFERRED L79. Plan L114, L424, L628.

### Q3: Where does an edge-computed `author_ref` travel on `raw.items`?

Option (a), tightened. `author_ref` is a conditional envelope field. It is present on every `comment` and `reaction` record (null where the platform gives no author id), and optional on any other record whose author identity the adapter replaced, with the replaced payload paths listed in `redacted_fields`. It is absent where the payload keeps a discovery poster's clear id, in which case normalize-item computes it. ADR-0010 L22 names the raw.items envelope as the carrier, and ADR-0005 L26 keeps the payload for the platform record. Record for F4 that the registry cache needs an `author_ref` index, because L164 drops `author_source_id` from the envelope and normalize-item can then find a registered commenter only by its reference.

Evidence: ADR-0010 L22, L47. ADR-0005 L26, L29. ADR-0035 L24. Plan L164, L630.

### Q4: Which service names do the D3 writers use in the producer table and in `producer.service`?

Option (a): three names, `admin-api`, `client-portal` and `admin-console`, which D3 adopts. The ADRs name each surface as a sender. ADR-0012 L34 names the admin API for ops and client requests and `client_request` deletions. ADR-0043 L29 and ADR-0044 L32 have the portal send keyword-save and priority decisions. ADR-0066 L24 has 'the client portal or admin console' send owned-property adds. ADR-0069 L22 says re-adding happens through the admin console. Option (b) would re-route decisions the ADRs give to the portal and console. Also note for the orchestrator: ADR-0012 L34 says 'D3 specifies' the admin API, but D3's brief plans no admin API spec (build-plan/sessions/D3-specs-for-the-parts-with-no-prd.md L7, L27-L30), so add it to D3's brief.

Evidence: ADR-0012 L34. ADR-0043 L29. ADR-0044 L32. ADR-0066 L24. ADR-0069 L22. CONVENTIONS L51-L54. D3 brief L7, L27-L30.

### Q5: Should F2 type the dead-letter record?

Option (a): F2 defines it, because F4 and F6 must write identical records and no ADR gives the shape. Amendments: `schema: "dlq.<service>/v1"` per ADR-0002 L23, one shared definition (F-52); `stage` (`consume`, `produce`), with `original.partition`, `original.offset` and `consumer.group` nullable on produce-side entries (F-21); one record per message of a failed batch; the existing `error.class` list; classified under ADR-0003, copying `provenance` and `retention_class` from `message` when it parses as a data message (F-42); keyed by the original key, or for a produce-side entry by the key the SDK would have set.

Evidence: CONVENTIONS L41. ADR-0002 L23. ADR-0057 L34. ADR-0012 L31. retention-purger.md L128. raw-archiver.md L118. ADR-0010 L49.

### Q6: What does an `analyze` job carry?

Option (b). Option (a) puts platform data and a `provenance` object in a job, against ADR-0003 L23 and L27, a user decision; only the user could allow that by amending ADR-0003. `analyze` carries `item_id`, `item_version` and `content_hash`, with `source_id` as the key. The worker reads the item from ClickHouse `items` or `comments`, skips it on a version or hash mismatch, and copies `provenance` and `retention_class` from the stored row. A row that is not yet visible is requeued without counting an attempt (ADR-0057 L34). Record in the handoff that the A-sessions measure store-writer's insert delay against the 15-minute tier-1 target (not verified).

Evidence: ADR-0003 L23, L25, L27. Plan L37, L416. ADR-0011 L29. analysis-media.md L41. ADR-0022 L29.

### Q7: What are the `account_type` values, and how is each marked?

Option (a). Organisation kinds: `page`, `group`, `business`, `organization`, `channel`, `company_page`, `site`. Person kinds: `creator`, `public_figure`, `individual`, `business_or_creator`, `organization_or_public_figure`. ADR-0010 L55 gives F2 the marks, and marking uncertain values as person kinds is the only choice that satisfies ADR-0010 L55-L56 and L70-L72 together with the user's words at D2-SUMMARY L222 and L236. Add one line: ADR-0010's 'media' is covered by the organisation kinds (`site` for news domains, outlets' pages and channels by their kind). Record the consequences in the handoff for the user: until Instagram business and creator accounts can be told apart (DEFERRED pilot row) and counsel answers, no unregistered Instagram account is listable; no TikTok person account is listable; and an unverified X `organization_or_public_figure` becomes listable only once the follower threshold is set.

Evidence: ADR-0010 L55-L56, L70, L72. D2-SUMMARY L222, L236. CONVENTIONS L392. ig-account-resolver.md L92, L112. x-user-resolver.md L57, L116.

### Q8: Should the drafted closed-list values and fields that no ADR names be approved?

Option (a): approve them as drafted. The spot-checked values match the PRD tokens and prose they cite, and ADR-0017 L27 confirms the status mappings. Add the two analysis skip reasons ADR-0068 requires (`ai_input_refused`, `use_not_permitted`, F-26), the four new alert rule-type names (F-22) and `severity` (F-48) as drafts. A list later found short grows under Q1's answer, through a new version.

Evidence: Plan L635. ADR-0017 L27. ADR-0068 L47, L53. ADR-0048 L58-L65.

### Q9: What are the rules of the one URL normaliser?

Option (a) as drafted (plan L551), with four additions. (1) Name the four search.results producers and search-hit-router as users of the same function, since the router parks any hash mismatch (F-45). (2) Record that ADR-0036 fixes the normaliser for `url_hash`, and that using it for `canonical_url_hash` and the `news:article` and `web:result` keys is F2's choice, consistent with ADR-0036 L24-L26. (3) Add golden vectors from the finders' and engines' examples. (4) Record the known limit: http/https and www/bare forms of one page hash differently, which news-dedup's own key catches for articles only.

Evidence: ADR-0036 L24, L26. search-hit-router.md L57. web-search-perplexity.md L56, L101-L102. news-dedup.md L64.

### Q11: What fields should `n8n.alert/v1` and `n8n.card/v1` have?

Option (a), amended. `alert` is an open snake_case name, with the names ADRs fix exported as constants. `details` is discriminated on a closed nine-value `rule_type`, each type with its metrics and a `scope` that can name `item_id`, `topic_id`, `entity_id` or `brand_id`, and `story_id` (F-22). The fallback notice is typed: subject, a reason from the registry list, and vendor. Add `channel` and `fallthrough_channel` (F-23). `audience` gains `account_manager`, or account managers' notices are documented as going to `ops` (F-46). The government rule extends to `subject` (F-50). Each `card_type` lists its required fields, with inputs for `manual_url`, a re-grant link for `grant_missing` and a deterministic `card_id` (F-47). `severity` is sourced or marked as drafted (F-48). Signing: `verify(body, headers, secret, now, tolerance)`, with the header names and signed string recorded in VERSIONING.md (F-49). All of these are technical choices inside ADR-0067 and ADR-0048.

Evidence: ADR-0067 L24-L27. ADR-0048 L42, L58-L65. D2-SUMMARY L224. alert-evaluator.md L56-L69, L86-L102. ADR-0021 L58-L61.

### Q12: May ops clear a source-level health state through the admin API?

Option (a), tightened. The admin API may send a source-level `health_change` with health `ok` and `reason` equal to the source's current `health_reason` (one of ADR-0016's eleven non-flag reasons, never `flag_off` or `flag_on`), with the person in `requested_by` and no provenance. registry-writer audits it, and the source takes its route's current state (ADR-0016 L25). The admin API sends no other source-level health value besides `flag_off` and `flag_on` with `blocked`. This applies ADR-0016 L25 and ADR-0021 L61 ('the service that set it, or ops, still clears it') through the only channel ADR-0012 L34 and ADR-0067 L26 give ops. ADR-0013 L26's 'rejects any other' follows the sentence handing the allowed producers to F2's table, so it does not forbid this. Drop option (b), which misquotes ADR-0013.

Evidence: ADR-0016 L25. ADR-0021 L61. ADR-0013 L26. ADR-0012 L34. ADR-0067 L26. Plan L639.

### Q13 (new): How does the admin API hand a button press or an ops request (the qualifier's review answer, x-compliance-sync's export request) to the owning service?

Through job kinds, as ADR-0067 L26 requires ('as ADR-0012 routes every ops and client request', meaning one SDK call with a schema per kind, ADR-0012 L34). Add `review_answer` on a new `jobs.qualifier` queue, keyed by `candidate_key`, with `card_id`, `decision_id`, `action`, `request_id` and `requested_by`. Add `export` on `jobs.x-compliance-sync`, with `client_id` (null for X), `from`, `to`, `request_id` and `requested_by`. The admin API is the producer of both. Record that this extends ADR-0011's kind list as ADR-0067 L26 and L33 require. A URL that ops supply to li-org-resolver takes the existing manual path (`manual_candidate`).

Evidence: ADR-0067 L26, L33. ADR-0012 L34. ADR-0011 L25. qualifier.md L46, L61. x-compliance-sync.md L132. Plan L125, L386, L457.

### Q14 (new): What happens to a candidate's sampled posts (li-org-resolver) after raw.items?

raw.items accepts `candidate_key` on any record kind about a candidate (F-03), but items.normalized and its derived topics keep `source_id` required, so v1 has no item without a source. normalize-item maps a candidate's sampled posts once the candidate is registered (looking it up by `candidate_key` in the registry cache); until then they stay in the archive, and the later backfill re-reads them (li-org-resolver.md L161). This keeps every downstream contract unchanged and is C4's implementation, recorded in the handoff.

Evidence: ADR-0005 L28. ADR-0004 L29. ADR-0008 L29. li-org-resolver.md L57, L161. Plan L193, L487.

### Q15 (new): What payload do clients' own alert webhooks receive?

The same `n8n.alert/v1` message with `audience = client`, signed with the same helper. ADR-0067 L25 says alert-evaluator's `alert/v1`, the payload clients' systems consume (alert-evaluator.md L34, L69), 'becomes it', and one schema keeps the government rule in one place. State this at plan L10 and L384.

Evidence: ADR-0067 L25. alert-evaluator.md L34, L69, L102. Plan L10.

### Q16 (new): Where does tt-profile-videos-poller find the revocation cut-off behind the user's 'Only new videos'?

No F2 field. The poller records the cut-off in its own `cursors` state (ADR-0041): the `at` of the source's first `fallback_on` event with reason `credential_revoked`. `health_changed_at` can move on flag flips (ADR-0021 L61 keeps only `health_reason` and `health_set_by`). Record this in the handoff for VTT4.

Evidence: D2-SUMMARY L251. ADR-0035 L33. ADR-0021 L61. ADR-0041 L29-L31.

## Confirmed findings

Line numbers are those of `docs/plans/F2.md` at `5fd54a4` unless stated.

### F-01 (blocker) · docs/plans/F2.md L34 (A15), L207-L208, L211, L537, L629 (Q2)

**Problem.** Every Q2 option hashes only the target (option (a) adds mode). But L208 takes the subject of an author, source or client scope out of `target` and puts it in the top-level key. So deletions about different subjects that share reason, scope, mode and target get the same `deletion_id`, and deletion-propagator drops the second one as a repeat. Three cases: two client offboardings; two authors on one platform; one author under two HMAC keys (one message per key, all with the same id). retention-purger's client-scope messages, sent 'one per affected source_id', also have no field to carry the source, so they collide as well. With no time element, a later and separate request about the same subject is dropped too. Golden vectors never change inside a version (L575), so a wrong form would stay frozen for all of v1.

**Evidence.** Plan L208: 'the subject of an author, source or client scope is the top-level key field ... never repeated in `target`'. ADR-0035 L24: '`deletion_id` (an SDK hash of the whole sorted target)'; 'source_id appears once, at the top, as the partition key (author scope author_ref, client scope client_id)'. deletion-propagator.md L47: 'A repeat of a completed id is acknowledged and dropped.' retention-purger.md L72 uses `sha256(target, class, cut-off day)` and L76 says 'one per affected source_id'. x-compliance-sync.md L81 uses `sha256(platform_id, status, signal day)`. yt-text-purger.md L114. ADR-0010 L45: 'a deletion by author tries every key still covering retained data'. ADR-0069 L22 (a): monitoring stops only if the author asks, so the same author can need a second deletion later.

**Correction.** Do not write golden/deletion-id.json until Q2 is answered (a user question). Recommended form: `del:<reason>:<scope>:<64 lower-case hex SHA-256 of the RFC 8785 JSON of {key, mode, signal_day, target}>`, where `key` is the scope's top-level key value, `signal_day` is the UTC date of `signal_at`, and every target array is sorted. Also state whether a client-scope deletion is one message per client, or carries an optional `source_id` that the hash also covers. Add golden vectors for: two clients with equal targets, two authors with equal targets, purge_text then delete of one item, one author under two keys, and a same-day replay that keeps its id.

### F-02 (blocker) · docs/plans/F2.md L416 (`analyze` kind fields), L633 (Q6 option (a))

**Problem.** The drafted `analyze` job carries `item`, the whole items.normalized/v1 message. That puts platform data (text, title, author_ref) and a nested `provenance` and `retention_class` inside a job. ADR-0003, a user decision, makes job queues control messages that carry no platform data. The plan's own A18 says no control schema accepts provenance. The only exception any ADR names is the `push` job's `body`. The job also cannot be built from a hit-triggered re-enqueue, which knows only an `item_id`.

**Evidence.** ADR-0003 L23: 'Job and control messages carry only `producer`'. ADR-0003 L27: 'Control messages, `producer` only: the job queues ... which carry no platform data'. CONVENTIONS L22. D2-SUMMARY L218: 'Approve all', which covers D2-Q003, a user decision. Plan L37 (A18: 'no control schema accepts provenance') and L152. ADR-0011 L29: `push` with `body`, the only named exception. ADR-0023 gives `analyze` no fields. analysis-media.md L41: 'A hit ... for an item skipped earlier enqueues it again'.

**Correction.** Adopt Q6 (b). `analyze` carries `item_id`, `item_version` and `content_hash`, with `source_id` as the envelope key. The worker reads the item from ClickHouse `items` or `comments`, skips it if the stored version or hash differs, and copies `provenance` and `retention_class` from the stored row (ADR-0003 L25). A row that is not yet visible is requeued without counting an attempt (ADR-0057 L34). Add an invalid fixture: an `analyze` job carrying `item` or `provenance` is rejected.

### F-03 (should-fix) · docs/plans/F2.md L39 (A20 test name), L160, L163, L165, L193, L487

**Problem.** `candidate_key` may replace `source_id` only on a `profile` record. But li-org-resolver also publishes its sampled `post` records for candidates that are not yet sources, and the plan lists them as raw.items output with `pool` visibility (L513). Those records fail validation, so A6 cannot pass for li-org-resolver. ADR-0005 and ADR-0004 set no kind limit on this rule. Downstream, items.normalized requires `source_id` and is keyed by it, and the plan says nothing about how a candidate's post becomes an item.

**Evidence.** Plan L160: '(a resolver's `profile`)'. L163: '`profile` requires `candidate_key` or `source_id`'. L39: 'accepts candidate_key instead of source_id only for a profile record'. ADR-0005 L28: '`source_id`, or `candidate_key` for a record about a candidate that is not yet a source'. ADR-0004 L29: 'as are `raw.items` records about a candidate not yet a source'. ADR-0008 L29 and L39 add a new mapper for 'li-org-resolver's sampled posts'. li-org-resolver.md L57 ('Publish the 20 sampled posts to `raw.items`') and L161.

**Correction.** Allow `candidate_key` in place of `source_id` on any raw.items record kind about a candidate, keyed by `candidate_key`, and rename the A20 test to match. Keep `source_id` required on items.normalized and the topics derived from it, and record Q14's answer: normalize-item maps a candidate's sampled posts only once the candidate is registered. Add a valid fixture for li-org-resolver's sampled post.

### F-04 (should-fix) · docs/plans/F2.md L159 ('stamps `retention_class` from the source row, else the route and platform default')

**Problem.** The stamping rule copies ADR-0005 but leaves out the later ADRs that qualify it. LinkedIn's class follows the content, not the source, so a member comment on a company page would be stamped `linkedin_org` instead of `linkedin_48h`. And a record read on a route other than the source's own, such as a client's revoked TikTok account read by the vendor in fallback, would be stamped with the source row's `tiktok_display` instead of `vendor_agreed`.

**Evidence.** ADR-0054 L43: 'A record's class still follows its route ..., except LinkedIn's, which follows its content (ADR-0055)'. CONVENTIONS L186 says the same. ADR-0055 L30: 'Member-authored content ... is `linkedin_48h` on every route'. ADR-0035 L33: in fallback after a revocation, tt-profile-videos-poller's records 'are `vendor_agreed`'. li-notification-receiver.md L125 already shows `linkedin_48h` on a comment.

**Correction.** Restate the rule in L159 and VERSIONING.md. Use the source row's class only when the record is read on the source's own route; otherwise use the default for the route actually used and the platform. LinkedIn records take `linkedin_48h` (member content) or `linkedin_org` (organisation content), as the adapter declares. Cite ADR-0054, ADR-0055 and ADR-0035, and add a fixture for each case.

### F-05 (should-fix) · docs/plans/F2.md L126, L150, L159-L160, L223, L457

**Problem.** news-article-extractor (reading article.urls) and search-hit-router (reading search.results) write raw.items from topics, with no job of their own. ADR-0005 makes `job_id`, `attempt` and `job_kind` always required. The plan defines `job_kind` only as a job's kind or `push`/`stream`, and drops `job_kind` from search.results (L223), so neither producer has a defined value. The loss matters for news: backfilled article URLs (`sitemap_backfill`, `commoncrawl`) must be recognised as backfill, so that Disqus articles get the single `once` fetch and not a full series.

**Evidence.** ADR-0005 L27 (always required) and L31 ('`job_kind` is the job's `kind` (for jobless receivers and the stream, the fixed values `push` and `stream`)'). ADR-0006 L31: '`producer.job_id` ... copied by topic consumers'. news-article-extractor.md L41 ('Every message on `article.urls`'), L43 ('backfill URLs (`sitemap_backfill`, `commoncrawl`)') and example L93-L106, which has no job fields. search-hit-router.md L43. comment-decay-scheduler.md L66. ADR-0060 L29. ADR-0036 L25.

**Correction.** Declare the rule for topic-driven raw.items producers: `job_id` is the input message's `producer.job_id` (ADR-0006 L31), and `attempt` is the consumer's own attempt, starting at 1. `job_kind` for news-article-extractor: `backfill` when `found_via` is `sitemap_backfill` or `commoncrawl`, otherwise `rotation`. `job_kind` for search-hit-router's `result`: `rotation`. Add valid fixtures for both producers.

### F-06 (should-fix) · docs/plans/F2.md L126, L404

**Problem.** Under the plan's rule, `job_kind` is the job's kind, so yt-video-details-fetcher's record for a `first_sight` job whose `origin_kind` is `backfill` carries `job_kind = first_sight`. ADR-0065 says such a backfilled first sight is marked by `job_kind = backfill`. As written, the video would not be recognised as backfilled, and its observation would be labelled `first_sight`.

**Evidence.** ADR-0065 L37: 'a backfilled first sight is marked by `job_kind = backfill`, not by a step'. ADR-0065 L31 (`origin_kind`). ADR-0034 L25-L27: labels derive from `job_kind`.

**Correction.** State in raw.items/v1 and VERSIONING.md that a record read for a `first_sight` job with `origin_kind = backfill` carries `job_kind = backfill`, and add a fixture.

### F-07 (should-fix) · docs/plans/F2.md L207-L208 (item-scope `provenance` and a single `target.kind`)

**Problem.** An item-scope deletion 'copies the item's provenance', and `target` has one `platform` and one `kind`. The main producers chunk many items per `source_id`, taken from both `items` and `comments`. Those items differ in kind, and in provenance service, route and vendor (poll, backfill, webhook, fallback), and every item has its own `fetched_at`. The plan gives no grouping rule. Grouping by full provenance, as one verifier proposed, would mean one message per item, because each `fetched_at` differs.

**Evidence.** ADR-0003 L28: 'an item-scope deletion copies the item's provenance and class'. ADR-0035 L24: target `platform`, `kind`, `platform_ids`, `item_ids`. retention-purger.md L72: candidates selected 'from ClickHouse `items` and `comments`', and 'Ids go out in chunks as one `deletions` message per `source_id`'. x-compliance-sync.md L81.

**Correction.** State that the SDK deletion builder splits item-scope targets so that every message's items share key, `platform`, `kind`, `provenance.route`, `provenance.vendor`, `provenance.service` and `retention_class`, with `provenance.fetched_at` set to the newest `fetched_at` in the chunk. Record this in VERSIONING.md as F2's reading of ADR-0003 for multi-item targets, and add a multi-item fixture.

### F-08 (should-fix) · docs/plans/F2.md L119, L151, L153

**Problem.** An author-, source- or client-scope deletion carries 'the signal's provenance', but `provenance.route` is closed to `green` and `amber`. A person's request entered through the admin console or retention-purger, the admin API's `client_request`, and a client offboarding involve no fetch, so they have no route. As planned, these messages cannot validate.

**Evidence.** ADR-0003 L28: the signal's provenance means 'the service that received the request or compliance signal, its route and vendor, and fetched_at = when the signal arrived'. ADR-0070 L28: the route list is green or amber 'since every fetch is green or amber'. ADR-0012 L34 (the admin API writes `client_request`). ADR-0069 L33 (h).

**Correction.** Allow `provenance.route` and `provenance.vendor` to be null only on non-item deletions whose signal is not a platform fetch (reasons `author_request`, `client_offboarding`, `client_request`, `legal`, `retention`). Keep `provenance.service` (the receiving service) and `fetched_at` (when the signal arrived) required. Add a valid and an invalid fixture.

### F-09 (should-fix) · docs/plans/F2.md L114, L120, L131, L42 (A23), L559

**Problem.** 'Every list is closed and exported ... as a schema enum' includes service names and vendors. These values appear in `producer.service` on every message and in `provenance.service` and `provenance.vendor` on every data message. Under ADR-0002, a new service or vendor would then widen a type in almost every schema, which means a new version of almost every topic. The user has already asked for such a service: an amber reader of clients' own Facebook Pages and Instagram accounts. That service would also add rows to other F2 registries (raw.items writers, producer-table rows, visibility), which L559 understates.

**Evidence.** ADR-0002 L23: 'anything else (a removed or renamed field, a changed type or meaning) is a new version'. D2-SUMMARY L252 ('Add a vendor reader'). DEFERRED L79. ADR-0021 L55: a client-owned property's vendor records take amber `pool` visibility. Plan L424: the producer table is already registry data ('The table is data in the package, read by both SDKs'). No ADR requires service names or vendors to be schema enums: ADR-0012 and ADR-0051 (c) fix the names and spellings, not the encoding.

**Correction.** Type `producer.service`, `provenance.service`, service-valued `requested_by` and `actor`, and `provenance.vendor` as lower-case patterned strings. Have `validate()` check them in producer mode against registry data: the service index, the D3 writer names and ADR-0051's vendor list. Rewrite A23 to check the registries against data, not enums. In L559, list the registry rows the new service adds (writer, producer rows, visibility, possibly a vendor value).

### F-10 (should-fix) · docs/plans/F2.md L283-L284 (`add` and `update` blocks), L301 (update producers), L407 (manual_candidate rationale)

**Problem.** Neither the `add` nor the `update` block carries a per-client priority flag, yet ADR-0043 has registry-writer write `client_sources.priority` from the portal's `add` or `update` decision. The client portal's `update` row does not cover a change to a priority list. On the manual path, L407 drops the request's priority, reasoning that 'priority never travels in a job, ADR-0011'. That ADR-0011 sentence is about the budget priority the SDK derives (ADR-0018), not a client's priority list. And a candidate that is not yet a source has no `client_sources` row for the qualifier to read.

**Evidence.** ADR-0043 L29: 'Priority: `client_sources.priority`, written by registry-writer from the portal's `add` or `update` decision.' CONVENTIONS L53. ADR-0011 L25: 'Priority (derived by the SDK, ADR-0018)'. registry-writer.md L61 (manual add body includes `priority?`) and L77 ('`client_sources` is upserted ... with `added_at`, `priority`, `added_by`'). The plan never cites ADR-0043.

**Correction.** Add optional `client_priority [{client_id, priority}]` to the `add` and `update` blocks, and extend the portal and console `update` row to cover a priority-list change. For manual requests, registry-writer keeps the request's priority with its `request_id` and `candidate_key` and applies it when the qualifier's `add` arrives, so no job carries it. Rewrite L407 so it no longer cites ADR-0011. Add fixtures.

### F-11 (should-fix) · docs/plans/F2.md L291, L307, L315-L316

**Problem.** On source-level decisions the plan does not tie health values to reasons. ADR-0021 fixes the `flag_off` and `flag_on` decisions at health `blocked`. ADR-0016 applies `credential_revoked` as `blocked`. As planned, the schema accepts `flag_off` with `ok` or `degraded`.

**Evidence.** ADR-0021 L61: 'When the flag is turned `off`, the decision has reason `flag_off` and health `blocked` ... When the flag is turned back on, the decision has reason `flag_on` and health `blocked`'. ADR-0016 L27: 'sends a source-level `health_change` (`credential_revoked`) ... which registry-writer applies as `blocked`'.

**Correction.** Add cross-field rules, with invalid fixtures. `flag_off` and `flag_on`: health `blocked` only, sent only by the admin API. Every other ADR-0016 reason: `blocked` or `degraded` to set the state, `ok` to clear it (Q12), never `fallback`. `credential_revoked`: never `degraded`.

### F-12 (should-fix) · docs/plans/F2.md L292 (route-level `health_change` block)

**Problem.** The route-level block names `health` without listing its values, and does not say how `health` relates to the `fallback` object. The sources disagree. The canary's example sends health `degraded` with a non-null fallback; its rules name a `fallback` state; and ADR-0050 says registry-writer sets `fallback` from the canary's route-level decision. The producer (the canary) and the consumer (registry-writer) can read the same message differently.

**Evidence.** source-health-canary.md L102 (`"health": "degraded", "fallback": {...}`), and its rules table ('degraded to fallback'). ADR-0016 L25: health values `ok`, `degraded`, `fallback`, `blocked`, with the route level carrying 'the `fallback` object'. ADR-0050 L31: '`fallback` is only a `sources.health` value, set by registry-writer from the canary's route-level `health_change`'. ADR-0014 L27.

**Correction.** Fix route-level `health` to `ok`, `degraded`, `fallback` or `blocked`. `fallback {route, vendor}` and `scope` are non-null exactly when health is `fallback`, and `reason` is null with `ok`. Map each value to the source.events type it produces, and rewrite the canary's example to match under A6.

### F-13 (should-fix) · docs/plans/F2.md L276, L283, L300-L301

**Problem.** The keyword-save branch of `add` and `update` is not defined. Its subject is `keyword_id`, but the `add` block still has `source {...}` and only sets `origin` to null. Under ADR-0044 the save only names the keyword, and registry-writer reads `keywords` and builds one row per platform. Hashtag rows also come from keyword saves, and ADR-0013 (c) puts a hashtag's bound Instagram account in the `add` decision's `platform_meta`, but the plan does not say where that value travels.

**Evidence.** ADR-0044 L32: 'Each save sends registry-writer an `add` or `update` decision naming the keyword ... registry-writer reads `keywords`, upserts the rows'. ADR-0044 L30: 'Hashtag forms make `hashtag` rows the same way'. ADR-0013 L28 (c): 'a hashtag's bound Instagram account comes with its `add` decision, in `platform_meta`'. ig-hashtag-search.md L45 and L57.

**Correction.** Declare a keyword branch: subject `keyword_id`, no `source` block, no `origin`, and an optional per-platform `platform_meta` (Instagram `ig_user_id`) that registry-writer copies onto the hashtag rows it creates. Add valid and invalid fixtures.

### F-14 (should-fix) · docs/plans/F2.md L277, rows L300-L309

**Problem.** Provenance is required on decisions that derive from a fetch and refused on the D3 writers' decisions. Several allowed producers fit neither group, so neither the schema nor A18 and A22 can tell whether their decisions carry `provenance` and `retention_class`. Examples: retention-purger's `remove_client` and `retire` (`owner_request`), the receivers' `push_coverage` (`lease_lapsed`), the platform services' `promote` and `update`, the qualifier's sweep (`tier_change`, `dormant`), ig-hashtag-search's `budget_wait`, and the credential client's `credential_revoked`.

**Evidence.** Plan L277. ADR-0003 L26 names three fetch-derived cases ('qualifier's decisions from resolver profiles, news-robots-checker's crawl refusal, the canary's `health_change`') and 'A decision entered by a person carries `requested_by` instead'.

**Correction.** Add a provenance column (required, optional or refused) to every decision-producer row, and test it in A18 and A22. Mark which rows follow ADR-0003's named cases and which are F2's choice.

### F-15 (should-fix) · docs/plans/F2.md L250 (poster.profiles fields), L283 (`add.origin`), L406

**Problem.** poster.profiles carries no `origin`. The qualifier reads that topic and its own tables, so it cannot tell a manual candidate's profile from a discovered one. It therefore cannot skip rules 2, 4 and 10 as ADR-0066 requires, or fill `add.origin`.

**Evidence.** ADR-0066 L28: 'poster-resolver with `origin: manual` and the seed-list flag, then the qualifier with rules 2, 4 and 10 skipped'. qualifier.md L27 and L75-L78 (reads: `poster.profiles` and tables). Plan L406 (`resolve` carries `origin`) and L250, which has no `origin`.

**Correction.** Add an optional `origin` (`discovery`, `manual`) to poster.profiles, echoed from the resolve job, recorded as an additive field beyond ADR-0033's list (ADR-0002). Add a fixture.

### F-16 (should-fix) · docs/plans/F2.md L283 (`source {...}` fields), L284 (`update` block)

**Problem.** `source {...}` has no `push_covered`. Yet ADR-0013 (d) says the onboarding flow's `update` for a page a client starts administering carries `route`, `vendor`, `owned_by_client` and `push_covered`. As planned, that update cannot set `push_covered`.

**Evidence.** ADR-0013 L28 (d): 'a page a client starts administering gets an `update` (route, vendor, `owned_by_client`, `push_covered` ...)'. ADR-0013 L25 lists `push_covered` and `lifecycle` among the identity and policy columns.

**Correction.** Define the `update` block as a partial object over every identity and policy column in ADR-0013 L25, including `push_covered`, and add a valid fixture of the onboarding `update`.

### F-17 (should-fix) · docs/plans/F2.md L150

**Problem.** `producer.job_id` must never be a composite or null, but the plan defines it only for jobs and receivers. It gives no value for a job a leader-elected scheduler emits, for messages the D3 writers send (keyword saves, owned adds, flag decisions, `client_request` deletions, requests), or for notices sent from time-driven loops (alert-evaluator, the canary). F4 and F6 must stamp it identically.

**Evidence.** ADR-0006 L31: '`producer.job_id` ... carries the ULID of the job behind the message, copied by topic consumers, never a composite or `null`'. CONVENTIONS L132: each scheduler 'emits a job when it is due'. alert-evaluator.md L40 (time-driven evaluation).

**Correction.** Add the cases to L150 and VERSIONING.md. A topic consumer copies its input's `producer.job_id`. A scheduler-emitted job uses its own `job_id`. A D3 writer's message uses the request's `request_id` ULID. A loop's message uses one ULID per evaluation run. Add a fixture for each case.

### F-18 (should-fix) · docs/plans/F2.md L505, L515; L43 (A24)

**Problem.** The gate reads visibility through `provenance.service`, which is the service that fetched. A `web:result` item is built from a Perplexity or Mojeek result, and the SDK copies the provenance of the search.results message onto the router's record. So its `provenance.service` is web-search-perplexity, web-search-mojeek or yt-web-search-bridge. L505 gives those services no visibility, and L515 gives `pool` to search-hit-router, which the gate never reads. Every web item fails the lookup, and A24 as worded does not catch it.

**Evidence.** ADR-0053 L32: 'keyword-matcher's gate reads it through `provenance.service`'. ADR-0003 L25 (provenance.service is the fetching service; the SDK copies provenance to derived messages). ADR-0038 L26 (the router writes the item for 'a Perplexity or Mojeek result'). Plan L151, L222. CONVENTIONS L386.

**Correction.** Declare `pool` for web-search-perplexity, web-search-mojeek and yt-web-search-bridge, and keep search-hit-router's row only if something reads it. Key the visibility registry by `provenance.service`, and reword A24 to 'every service that can appear as `provenance.service` on a content kind declares a visibility', with a `web:result` fixture.

### F-19 (should-fix) · docs/plans/F2.md L417 (`candidate_retry`)

**Problem.** The retry job carries only `hit_id`, `item_id` and `raw_ref`. From those, keyword-matcher cannot build a valid discovery.hits/v1, which requires `keyword_ids`, `client_ids` and `hit_at`, plus the `keyword_hit` evidence (`matched_term`, `form_id`, `keyword_set_version`). The raw record does not hold them. A candidate is emitted only once the identity is readable, so this retry is the only path for those candidates.

**Evidence.** ADR-0031 L32-L33. keyword-matcher.md L74 ('a `candidate_retry` job ... re-sends it with the same `hit_id`'). Plan L233, L239.

**Correction.** Add `keyword_ids`, `client_ids`, `hit_at`, `matched_term`, `form_id` and `keyword_set_version` to `candidate_retry`. They are ids and the client's own terms, not platform data, so ADR-0003 allows them in a job. Alternatively, declare that the worker re-reads them from ClickHouse `hits` by `item_id`, and list that dependency in the handoff.

### F-20 (should-fix) · docs/plans/F2.md L227-L228 (item.hits/v1)

**Problem.** ADR-0031 creates hits with `matched_by = source` when the text does not match, and such a hit has no matched term, form or offsets. The plan lists `matched_term`, `form_id`, `occurrences`, `offsets` and `offsets_in` as plain fields, with no branch on `matched_by`. So a source hit cannot validate unless the producer invents values.

**Evidence.** ADR-0031 L35: 'with `matched_by = source` when the text does not match'. Plan L227, L228.

**Correction.** Discriminate item.hits on `matched_by`. With `text`, the match fields are required. With `source`, `matched_term`, `form_id` and `offsets_in` are null, `occurrences` is 0 and `offsets` is empty. Add a valid and an invalid fixture per branch.

### F-21 (should-fix) · docs/plans/F2.md L380 (dlq/v1), L632 (Q5)

**Problem.** The drafted DLQ record assumes every entry is one consumed message, with `original {topic, partition, offset, ...}` and `consumer {service, group}`. The PRDs also dead-letter work that failed while producing, and whole batches. retention-purger's produce-failed chunk has no consumed offset at all.

**Evidence.** retention-purger.md L128 ('after 5 attempts ... the chunk goes to `dlq.retention-purger`'). raw-archiver.md L118, L134 (batches). keyword-matcher.md L135. store-writer.md L135.

**Correction.** Add `stage` (`consume`, `produce`). Make `original.topic`, `partition`, `offset` and `consumer.group` nullable for produce-side entries, and key those by the key the SDK would have set. Dead-letter a failed batch as one record per message. Write all of this in VERSIONING.md.

### F-22 (should-fix) · docs/plans/F2.md L384 (`details`), L21 (A2)

**Problem.** `details` types only alert-evaluator's single example, a `volume_spike`, plus 'an open object for other alerts'. ADR-0048 and the user's answer put nine alert types in v1. An open object also contradicts A2's 'additionalProperties false on every object', and typing it later would narrow a type, which is a new version under ADR-0002. `rule_type` is not closed, and the four new types have no names anywhere.

**Evidence.** ADR-0048 L42 ('all nine alert types are built in v1') and L58-L65. D2-SUMMARY L224 ('Add 4 alert types in v1'). alert-evaluator.md L57-L61 (five predicates with different parameters), L63 (scope_key 'the keyword, the keyword and source, or the item id') and L86-L99 (the only example). Plan L21.

**Correction.** Discriminate `details` on a closed `rule_type` of nine values: `volume_spike`, `negative_share`, `new_high_reach_poster`, `keyword_first_seen` and `post_deleted_high_reach` (alert-evaluator §5.3 A), plus four drafted names (for example `engagement_spike`, `topic_spike`, `entity_or_logo`, `story`) marked under Q8. Give each type its metrics, typed where alert-evaluator gives them, and otherwise a typed map of numbers. Give `scope` optional `item_id`, `topic_id`, `entity_id` or `brand_id`, and `story_id`. Add fixtures per type.

### F-23 (should-fix) · docs/plans/F2.md L384 (`idempotency_key` `<alert_id>:<channel>`), L385

**Problem.** The alert's idempotency key is built from a channel, but neither payload has a channel or destination field. alert-evaluator keeps one outbox row per alert and channel, and ADR-0067 has D3 build one flow per channel with a Telegram-to-email fall-through. The flows cannot know which channel they serve or which channel comes next.

**Evidence.** alert-evaluator.md L56 (`channels (jsonb)`) and L69 ('one row per alert and channel ... `Idempotency-Key: <alert_id>:<channel>` ... a Telegram failure falls through'). ADR-0067 L27. Plan L384 field list.

**Correction.** Add `channel` (`email`, `telegram`, `slack`) and `fallthrough_channel` (nullable) to n8n.alert/v1, and `channel` to n8n.card/v1. Record this under Q11.

### F-24 (should-fix) · docs/plans/F2.md L386 ('F2 types no inbound callback'), L457 (no qualifier queue), L125 (job kinds)

**Problem.** ADR-0067 has the admin API hand a button press to the owning service 'as ADR-0012 routes every ops and client request', which means through one SDK call with a schema per kind. ADR-0067 also removes the qualifier's own callback endpoint. The plan types no message for the qualifier's review answer or for x-compliance-sync's export request: no queue, no kind and no producer row. It conflates the leg from n8n to the admin API (D3's HTTP) with the leg from the admin API to the service. Job kinds are a core list, so adding one later costs job/v2.

**Evidence.** ADR-0067 L26 ('hands it to the owning service (the qualifier's review answer, x-compliance-sync's export request), as ADR-0012 routes every ops and client request') and L33 ('the qualifier's callback moves from its own endpoint to the admin API'). ADR-0012 L34 ('through one SDK call with a schema per kind'). qualifier.md L46, L61. x-compliance-sync.md L132.

**Correction.** Apply Q13's answer. Add a `review_answer` kind on a new `jobs.qualifier` queue, keyed by `candidate_key`, with `card_id`, `decision_id`, `action` (the card's button), `request_id` and `requested_by`. Add an `export` kind on `jobs.x-compliance-sync` with `client_id` (null for X), `from`, `to`, `request_id` and `requested_by`. Give both producer rows to the admin API, and add fixtures.

### F-25 (should-fix) · docs/plans/F2.md L174 (context `video_channel_id`), L193-L194 (items.normalized), L227 (item.hits)

**Problem.** ADR-0048 adds the video's channel to the aggregate grain on YouTube rows. The plan declares `video_channel_id` only as a raw.items `context` key of the two comment fetchers. No items.normalized or item.hits field carries it, so it never reaches store-writer or aggregator. For a video found by search, `source_id` is the keyword rule, so the channel cannot be derived from it.

**Evidence.** ADR-0048 L46: 'on YouTube rows, the video's channel (`video_channel_id`)'. CONVENTIONS L101. ADR-0004 L30 (a search find's `source_id` is its keyword-rule row). yt-comments-fetcher.md L34. normalize-item.md L71.

**Correction.** Add an optional `video_channel_id` to items.normalized/v1: on a YouTube video, the uploading channel; on a YouTube comment, the parent video's channel. Channels are organisation kinds under ADR-0010. Either carry it on item.hits too or name the join F8 uses, and add fixtures.

### F-26 (should-fix) · docs/plans/F2.md L341 (items.analysis skip `reason`)

**Problem.** The closed list of skip reasons has no value for the two skips ADR-0068 creates. Under (c), `ai-input = no` keeps a host's text out of model analysis. Under (d), speech-to-text and OCR process nothing whose download the register marks 'not allowed'. `media_unavailable` means an expired or refused URL, not a policy refusal.

**Evidence.** ADR-0068 L47 ('so the analysis services can skip the item') and L53. analysis-media.md L52. Plan L341.

**Correction.** Add `ai_input_refused` (ADR-0068 c) and `use_not_permitted` (ADR-0068 d) to the skip reasons, with fixtures, under Q8.

### F-27 (should-fix) · docs/plans/F2.md L397 (`rotation`: optional `tier` only), L175, L51 (A32)

**Problem.** Every ig-hashtag-search job names one edge (`recent_media` or `top_media`), and each edge has its own cursors row and due time. A job has no `edge` field, so either producer mode (A32) rejects the job, or the worker cannot tell which edge the job serves.

**Evidence.** ig-hashtag-search.md L45: 'Each job names one hashtag source, one edge (`recent_media` or `top_media`)'. ADR-0041 L31: '`scope_key` is ... a hashtag edge'. ADR-0015 (due times per keyword or edge). Plan L51.

**Correction.** Declare an optional `edge` (`recent_media`, `top_media`) on `rotation`, `backfill` and `ops_force`, required by the producer-table rows of `jobs.ig-hashtag-search`. `ig_user_id` comes from `platform_meta`. Add a fixture.

### F-28 (should-fix) · docs/plans/F2.md L527 (LinkedIn key forms), L575, L557-L559

**Problem.** ADR-0007 freezes LinkedIn activity-URN keys only if LI0 finds the activity URN on the green API; otherwise green records keep share-URN keys. The helper and its golden vectors cover only the activity form, and the plan does not record the contingency.

**Evidence.** ADR-0007 L37 ('if nowhere, green keeps share-URN keys') and L48. DEFERRED L83. Plan L575 ('a golden vector never changes inside a version').

**Correction.** Add the share-URN post and comment forms to the helper now, selected by an explicit argument, with golden vectors. Record that LI0 decides which form green adapters use, and list the LI0 row under the DEFERRED rows.

### F-29 (should-fix) · docs/plans/F2.md L557-L559 (DEFERRED rows that touch an F2 shape), L7

**Problem.** The list is presented as the rows that touch an F2 shape, but it leaves out several that would change shapes or helpers F2 freezes. X5's confirmation of `window_start` on `replies` jobs: replacing that field is not additive. An Arabizi class and a Kurmanji label: both are new values in the closed lang-dialect-id label list (L132), which Q1 does not classify. VIG0 and creation-time stability, which the Instagram and id-less key helpers rest on. Count refreshes under ADR-0058. Reversing an X withholding, which may need a new mode. L559 also attributes `disqus_identifier` to DEFERRED, which has no such row; it is ADR-0040 L30's.

**Evidence.** DEFERRED L63, L72, L76, L81, L82, L84, L85 (L83 is in F-28). D2-SUMMARY L238-L239 (window_start 'for X5 to confirm'). ADR-0040 L30. Plan L132, L628.

**Correction.** Add these rows, each with its consequence: additive under ADR-0002, a new version, or a helper or golden-vector change. Classify the lang-dialect-id labels as a closed list that grows only through a new version. Cite `disqus_identifier` to ADR-0040 L30.

### F-30 (should-fix) · docs/plans/F2.md L158, L178

**Problem.** ADR-0070 (h) fixes the spellings `extractor` and `extractor_version` for F2 to take, and the plan mentions neither. The news extract payload is our own extract, not a platform record. normalize-item and news-dedup read its fields (`title`, `excerpt`, `published_at`, `text_full_ref`, `text_sha256`, `title_sha256`, `canonical_url`), yet the plan leaves it untyped.

**Evidence.** ADR-0070 L25 (CF-027 h) and L40 ('F2 takes the spellings from here'). news-article-extractor.md L89 and L109-L121. ADR-0031 L37 (raw.items read by normalize-item, raw-archiver and news-dedup). news-dedup.md L41.

**Correction.** Type the payload of news-article-extractor's `article` record (url, final_url, canonical_url, title, excerpt, published_at, text_full_ref, text_expires_at, text_sha256, title_sha256, extractor, extractor_version, plus the optional rest), citing ADR-0070 (h) and ADR-0005 ('an extract by rule').

### F-31 (should-fix) · docs/plans/F2.md L496-L501, L409, L233, L161, L188

**Problem.** Some jobs and records concern no source, and the plan names no key or subject for them. (1) web-commoncrawl-scanner's `rotation` and `ops_force` scan a crawl, yet they fall under the default key `source_id`. (2) `ops_force` on x-compliance-sync (limited to an id list or one client's sources) and on yt-text-purger has no source, and its fields lack `client_id`. (3) The scanner's discovery.hits has no producing source, but `source_id` is required. (4) The scanner archives its per-host aggregate as `search_response`, whose only defined key is the rule's `source_id`, and the scanner has no rule.

**Evidence.** ADR-0004 L27, and its Consequences ('a message or job about no source names its key in the contract'). web-commoncrawl-scanner.md L40-L41 and L99 (`keyword_rule_id: null, client_ids: []`). ADR-0037 L25. ADR-0005 L28. ADR-0031 L32. x-compliance-sync.md L45. yt-text-purger.md L46.

**Correction.** Key the scanner's `rotation` and `ops_force` by `crawl_id`, and key an `ops_force` with no source by `request_id`, adding an optional `client_id`. Allow discovery.hits `source_id` to be null only when `evidence_type = commoncrawl`. Give the scanner's `search_response` a key of `candidate_key` (`news:site:<domain>`) plus `fetched_at`. Add a fixture for each.

### F-32 (should-fix) · docs/plans/F2.md L428-L436 (rotation, reconciliation and refresh rows)

**Problem.** ADR-0012 lets each rotating service's scheduler emit `rotation`, `reconciliation` and `refresh` on its own queue. The plan grants `reconciliation` on only ten own queues, and `refresh` only to the resolvers and news-robots-checker. A rotating service outside those lists that emits either kind would be dead-lettered.

**Evidence.** ADR-0012 L32 ('each rotating service's scheduler emits `rotation`, `reconciliation` and `refresh` on its own queue') and L31 ('the consumer's wrapper dead-letters').

**Correction.** Grant `rotation`, `reconciliation` and `refresh` on each rotating service's own queue, as ADR-0012 L32 reads. For queues where no PRD defines the kind fields, declare them as none.

### F-33 (should-fix) · docs/plans/F2.md L180 (`unthreaded`), L163

**Problem.** The plan declares an `unthreaded` context key for tg-discussion-receiver, which writes an unthreaded comment exactly when no parent can be found. But every `comment` requires `parent_id` and `root_id`, so the case the key exists for can never validate.

**Evidence.** tg-discussion-receiver.md L61 ('When neither works the comment is written with `unthreaded = true`') and L190. ADR-0008 L26 ('`comment` is reply-level and always has a `parent_id`'). ADR-0009 L26.

**Correction.** Remove `unthreaded`. Record in the handoff that, under ADR-0008 and ADR-0009, tg-discussion-receiver does not publish a parentless comment: it counts it and parks it, and its own session settles anything more.

### F-34 (should-fix) · docs/plans/F2.md L193 (`metrics_snapshot`), L200-L202 (item.metrics)

**Problem.** Two writers of Facebook counts disagree. normalize-item's example uses upper-case reaction keys and sets `likes` to the total of all reactions. fb-reactions-fetcher uses lower-case keys and a separate `reactions_total`, which the plan drops. The plan fixes lower case only on item.metrics and defines `likes` nowhere, so one post's series in `metrics_timeseries` would mix two meanings of `likes`.

**Evidence.** normalize-item.md L114 (`likes: 120`, `{"LIKE": 100, "LOVE": 20}`). fb-reactions-fetcher.md L118-L119 (`like: 2210 ... reactions_total: 2421`). ADR-0034 L25-L26 (both write the same item.metrics). Plan L201, L202.

**Correction.** Define `likes` per platform; for Facebook it is the total of all reactions, so fb-reactions-fetcher's `reactions_total` maps to it. Fix lower-case `reactions_by_type` keys on both items.normalized and item.metrics, and add golden fixtures from both producers.

### F-35 (note) · docs/plans/F2.md L182 (tt-keyword-search `context.keyword_id`)

**Problem.** A keyword-rule row serves every client keyword of the same query, so one read serves several `keyword_ids`. A singular `keyword_id` in context is wrong whenever two clients share a query.

**Evidence.** ADR-0044 L30 ('`client_ids` = every client with an enabled keyword of that query'). ADR-0037 L24 (`keyword_ids` on search results). ADR-0006 L32. tt-keyword-search.md L90 (the singular example the plan copied).

**Correction.** Drop `keyword_id` from tt-keyword-search's context, since the rule's `source_id` names the query, or declare `keyword_ids` as an array.

### F-36 (note) · docs/plans/F2.md L164 (envelope fields that go)

**Problem.** The list of envelope fields that go is presented as complete but misses three that appear in producer examples: `event`, `conversation_id` and a top-level `channel_id`. A6 would fail on those examples, with no rule stated.

**Evidence.** tg-bot-channel-receiver.md L119 and tg-discussion-receiver.md L120 (`"event": "new"`). ADR-0009 L29 ('producers send no edit marker'). x-replies-fetcher.md L117 (`conversation_id`). yt-keyword-search.md L105 (`channel_id`).

**Correction.** Add `event` (ADR-0009), and `conversation_id` and `channel_id` (kept in the payload, ADR-0005), to L164.

### F-37 (note) · docs/plans/F2.md L161, L163

**Problem.** The `reaction` archive key is `source_id` plus `platform_id`, but `platform_id` is required only on content kinds, so a valid `reaction` record can lack its key.

**Evidence.** Plan L161, L163. li-notification-receiver.md L161 (`linkedin:reaction:<platform_id>`).

**Correction.** Require `platform_id` on `reaction`, and on each archive-only kind require every field its declared key needs.

### F-38 (note) · docs/plans/F2.md L193 (items.normalized field set)

**Problem.** items.normalized carries no `client_ids`. store-writer copies items.normalized fields into `items`, yet deletion-propagator reads each item's `client_ids` to resolve client-scope deletions and to send client webhooks. Not verified whether F8 fills `items.client_ids` from another source.

**Evidence.** store-writer.md L66 and its items example L104-L116, which has no client_ids. deletion-propagator.md L48, L60, L72. ADR-0005 L27 (`client_ids` on the raw envelope).

**Correction.** Confirm with F8 where `items.client_ids` comes from. If it comes from nowhere, add an optional `client_ids` to items.normalized/v1, copied from the raw envelope.

### F-39 (note) · docs/plans/F2.md L276, L283

**Problem.** An owned property's `add` carries the pre-allocated id twice, as the subject `source_id` and as `add.proposed_source_id`, and nothing requires the two to be equal.

**Evidence.** Plan L276, L283. ADR-0066 L25 ('registry-writer inserts with that `proposed_source_id`').

**Correction.** Require `source_id == add.proposed_source_id` on an owned add, as a cross-field check with an invalid fixture.

### F-40 (note) · docs/plans/F2.md L316-L317

**Problem.** When a flag is turned off during a route-wide fallback, the canary returns the route to `degraded`. The plan's route-level reason list (`empty_200_rate`, `low_yield`, `server`, `auth`) has no value for that decision.

**Evidence.** ADR-0021 L61 ('A route in a route-wide fallback returns to `degraded` ... source-health-canary decides the route-wide change'). ADR-0014 L36.

**Correction.** Allow `flag_off` on the canary's route-level `health_change` back to `degraded`, and on the per-source `fallback_off` events it causes. Add a fixture.

### F-41 (note) · docs/plans/F2.md L301, L320 (`budget_wait`)

**Problem.** ig-hashtag-search's `update` with `budget_wait` does not say which column it changes. An `updated` event with an empty `previous` contradicts ADR-0014's definition of `updated`.

**Evidence.** ADR-0014 L27 ('`updated` (an identity or policy change ... shown in `previous`)'). ADR-0052 L32 (c).

**Correction.** Name the column the `budget_wait` update changes (for example the registered `route` and `vendor` when the hashtag moves to amber, or `notes` when it is queued), so the event carries a `previous`.

### F-42 (note) · docs/plans/F2.md L151-L152, L380

**Problem.** dlq/v1 is classified as neither data nor control under ADR-0003, yet its records embed data messages that can hold individuals' ids.

**Evidence.** ADR-0003 L23. ADR-0010 L49 (discovery posters' ids 'sit in ... DLQs until topic retention expires').

**Correction.** Classify dlq/v1. When `message` parses as a data message, copy its `provenance` and `retention_class` to the top level; otherwise leave them absent. Note in the handoff that DLQ topic retention stays short.

### F-43 (note) · docs/plans/F2.md L360 (crawl.policies `requested_by`)

**Problem.** `requested_by` is typed as 'a service name', but an `ops_force` from the admin API carries a person, and news-robots-checker's own `refresh` jobs carry no `requested_by` at all.

**Evidence.** Plan L390-L391, L408, L455. news-robots-checker.md L53, L113.

**Correction.** Type it as the job's `requested_by` when the job has one (a service name or D3's person reference), else null. Add fixtures for `ops_force` and `refresh`.

### F-44 (note) · docs/plans/F2.md L365 (news.dedup provenance 'copied from the article')

**Problem.** A `story_update` re-emits verdicts for other members of a story, but news-dedup's member state keeps no `route`, `vendor`, `service` or `retention_class`, so it cannot fill those fields for them.

**Evidence.** news-dedup.md L57 ('publish `story_update` for every member whose verdict changed') and L108 (the `news_story_members` columns).

**Correction.** Record in the handoff that news-dedup (N7) must keep each member's provenance and class, so that every `story_update` can carry them.

### F-45 (note) · docs/plans/F2.md L535, L551

**Problem.** The normaliser's users are named as the news finders, the extractor and the router. The four search.results producers also compute `canonical_url_hash` with 'the shared canonicaliser', and search-hit-router parks any message whose hash does not match.

**Evidence.** web-search-perplexity.md L56, web-search-mojeek.md L58, web-gdelt-poller.md L59. search-hit-router.md L57.

**Correction.** Name web-search-perplexity, web-search-mojeek, web-gdelt-poller and yt-web-search-bridge as users of the same function, and add a golden vector from web-search-perplexity.md L101-L102.

### F-46 (note) · docs/plans/F2.md L384-L385 (`audience` `client`, `ops`)

**Problem.** PRDs name account managers as recipients of some notices, but `audience` is closed to `client` and `ops`.

**Evidence.** alert-evaluator.md L117. qualifier.md L119. source-health-canary.md L36, L143.

**Correction.** Add `account_manager` (resolved through `client_id`), or record that these notices go to `ops`. Settle it under Q11.

### F-47 (note) · docs/plans/F2.md L385 (n8n.card/v1)

**Problem.** `buttons`, `default_action` and `timeout_at` are specified only for the review card. The `manual_url` card needs a text input, which buttons cannot carry, and the `grant_missing` card needs a re-grant link. Card idempotency is unspecified, yet ADR-0021 requires that a `flag_on` no-op sends no new card.

**Evidence.** li-org-resolver.md L34. ADR-0021 L59, L61.

**Correction.** For each `card_type`, list the required fields. Add `inputs [{name, label, kind}]` for `manual_url` and a re-grant link for `grant_missing`. Make `card_id` deterministic from its subject.

### F-48 (note) · docs/plans/F2.md L384 (`severity` `info`, `warning`, `high`)

**Problem.** The list is closed without a source. The only value any PRD shows is `high`, and the values come from the per-rule `alert_rules.severity`.

**Evidence.** alert-evaluator.md L56, L90.

**Correction.** Mark the list as drafted under Q8 and Q11, or align it with the rule editor's values that D3 specifies.

### F-49 (note) · docs/plans/F2.md L523, L547 (n8n signing helper)

**Problem.** `verify` rejects timestamps older than five minutes, which needs the current time, yet the plan's own rule is that helpers read no clock. The header names, signed string and tolerance are F2's own choices, beyond ADR-0067.

**Evidence.** Plan L523 ('no environment, clock ...'), L547. ADR-0067 L24.

**Correction.** Define `verify(body, headers, secret, now, tolerance_seconds)`, record in the handoff that the SDK signs again at each send attempt, and list the signing parameters for approval under Q11.

### F-50 (note) · docs/plans/F2.md L384 (`subject {source_id, platform, ...}`)

**Problem.** The government rule (no source and no platform) is applied only inside `details`, so a producer can still put a source and platform in the top-level `subject` of a government client's alert.

**Evidence.** alert-evaluator.md L65 (aggregate-only payloads) and L102 ('For a government client the `source` object and `platform` are absent').

**Correction.** Extend the rule to `subject`: a government client's alert carries no `subject.source_id` and no `subject.platform`. Add an invalid fixture and a `validate()` check.

### F-51 (note) · docs/plans/F2.md L150-L153, L384-L385, L37 (A18)

**Problem.** The two n8n payloads are classified as neither data nor control, so A18 checks neither of them.

**Evidence.** ADR-0003 L26-L27 (the lists of data and control messages). ADR-0003 L31.

**Correction.** Classify both as producer-only notices restricted to aggregate content (no item text, author reference or handle, alert-evaluator.md L128), state it in VERSIONING.md, and test it in A18.

### F-52 (note) · docs/plans/F2.md L20 (A1), L106, L380 (`dlq/v1`)

**Problem.** The schema string `dlq/v1` does not follow ADR-0002's `<topic>/v<n>`. ADR-0002 names only the job envelope as a shared exception.

**Evidence.** ADR-0002 L23 ('Every message on every topic carries `schema: "<topic>/v<n>"`, and every job ... `job/v<n>`'). CONVENTIONS L41 (`dlq.<service>`).

**Correction.** Use `schema: "dlq.<service>/v1"`, one shared Zod definition with a pattern, so that ADR-0002 holds literally, and have `classifyVersion` and the catalogue treat the pattern.

### F-53 (note) · docs/plans/F2.md L209, L473

**Problem.** ADR-0010 has raw-archiver replace an ordinary individual's id 'through the deletions' rewrite path', but no deletions reason or mode fits, and poster-resolver is not a deletions writer. Not verified whether the intended trigger is a deletions message or raw-archiver's rewrite call (C2).

**Evidence.** ADR-0010 L47. ADR-0035 L25.

**Correction.** Record that this redaction is raw-archiver's rewrite call, outside F2 (C2), or type it with a mode and a producer row.

### F-54 (note) · docs/plans/F2.md L473 (deletions writers)

**Problem.** ADR-0062 applies to every fetcher that refetches, and a comment fetcher that finds the post itself gone emits the post's deletion. ig-comments-fetcher and ig-account-media-poller (named by ADR-0062 as VIG2 and IG3) are not deletions writers. Not verified whether their routes can confirm a deletion.

**Evidence.** ADR-0062 L4, L24, L37. ig-comments-fetcher.md L49 (no inference from absence). ig-account-media-poller.md L64.

**Correction.** Check both against ADR-0062 (a documented 404 on the post's own endpoint counts as a signal), then either add them as writers or state why they are excluded.

## Rejected findings (context only; do not apply)

- registry group, budget_wait as an ADR-0014 vs ADR-0052 conflict: rejected. ADR-0014 L25 says 'a hashtag beyond the cap is ADR-0052's', and ADR-0052 L32 (c)'s budget wait is exactly that case, so plan L320 reads the two ADRs correctly. The leftover point, an `updated` event with an empty `previous`, is kept as F-41.
- registry group, source.events top-level retention_class cited to ADR-0003 (plan L332): rejected as a citation point. L332 already says the field is the source's registry column, A18 (L37) tests `provenance`, not `retention_class`, on control schemas, and no producer or consumer reads the contract wrongly.
- registry group, the extra registry.decisions partition keys `author_ref` and `keyword_id`: rejected. Plan L95 and L490 already record both keys and cite ADR-0004's rule for messages about no source; listing them in the handoff is ordinary build work, not a defect.
- n8n group, `disqus_identifier` presented as a DEFERRED row (L559): rejected as a standalone finding. It is a misattributed source with no contract effect (DEFERRED.md has no such row; ADR-0040 L30 does), so it is folded into F-29's correction.
- n8n group, the registry rows the new amber vendor reader would add: merged into F-09.
- Duplicates merged: the li-org-resolver candidate posts (envelope and jobs groups) into F-03; the topic-driven job fields (envelope and coverage groups) into F-05; web-engine visibility (jobs and coverage groups) into F-18; per-client priority (registry and coverage groups) into F-10; provenance per decision producer (registry and coverage groups) into F-14; video_channel_id (n8n and coverage groups) into F-25; the envelope fields that go into F-36; the reaction key into F-37; the LinkedIn share-URN form into F-28; producer.job_id from loops (n8n group) into F-17.
- Envelope group's correction for multi-item deletions, 'one message per (key, kind, provenance, retention_class)': rejected as written, because each item's `provenance.fetched_at` differs, so the rule would produce one message per item. F-07 uses a grouping that leaves out `fetched_at`.
- Envelope group's 'user' verdict on Q1: rejected. ADR-0002 settles the question as written, and the orchestrator can answer by following it (see Q1). Only option (a) would need the user.
- Coverage group's 'user' verdict on Q12: rejected. ADR-0016 L25 and ADR-0021 L61 literally give ops the right to clear, and ADR-0012 L34 makes the admin API ops' only channel. ADR-0013 L26's 'rejects any other' follows a sentence that hands the allowed producers to F2's table, so it is ambiguous, and the plan's option (b) misquotes it.
- Registry group's Q4 option (b), one name `admin-api` for all three surfaces: rejected in favour of (a). ADR-0043 L29, ADR-0044 L32 and ADR-0066 L24 name the client portal and the admin console as the senders of those decisions.
- Coverage group's Q11 variant, typing only volume_spike and leaving the other eight alert bodies as open objects: rejected. An open object contradicts the plan's own A2 (L21), and typing those bodies later would narrow a type, which is a new version under ADR-0002 L23.
- n8n group, where tt-profile-videos-poller reads its revocation cut-off: no F2 defect, since the plan needs no field for it. It is answered as Q16.
- n8n group, the payload clients' own alert webhooks receive: kept as question Q15, not as a separate finding.
