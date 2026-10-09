# ADR-0069 · Legal policies for deletions and audits

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, I1, D3, U2, G4, deletion-propagator, retention-purger, x-compliance-sync, registry-writer, qualifier, raw-archiver, yt-text-purger, x-recent-search, x-filtered-stream, x-full-archive-search
Source: D2-Q069 (user decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

The deletion and audit services leave several policies "to be agreed with counsel": who verifies the identity of an author who files a request (`retention-purger §14 Q1`, proposed: a confirmation sent to the platform account's public contact); the grace period of the `meta_on_request` necessity clock and how long audit records are kept (`retention-purger §14 Q4`); deletion deadlines for non-X `platform_sync` and for `legal` requests (`deletion-propagator §14 Q6`); backups and snapshots, which "must expire inside the shortest deadline or be excluded" (`deletion-propagator §14 Q1`); whether X's 24-hour clock runs from X's compliance signal or from the event on X (`x-compliance-sync §14 Q1`; CONVENTIONS L186 says "deletions must be mirrored within 24 hours"); how long identifiable X items, evidence files and audit records are kept (`x-compliance-sync §14 Q7`); and who screens client keyword terms for "sensitive events (protests, rallies)", which X forbids monitoring (`x-full-archive-search §14 Q4`; CONVENTIONS L188). One entry adds a registry question: an erasure request from someone whose account is a registered source has no producer for the registry decision and no reason value for it (`deletion-propagator §14 Q3`, proposed: retention-purger emits it; AU-079).

Settles: AU-079, deletion-propagator §14 Q1, deletion-propagator §14 Q3, deletion-propagator §14 Q6, raw-archiver §14 Q3, retention-purger §14 Q1, retention-purger §14 Q4, x-compliance-sync §14 Q1, x-compliance-sync §14 Q6, x-compliance-sync §14 Q7, x-filtered-stream §14 Q6, x-full-archive-search §14 Q4.

## Options

1. **Defaults that can be built now, the strictest where a deadline is at stake, each confirmed by counsel before G4** (chosen): its rules are under Decision.
2. **Leave every point to counsel before the services are built.** Consequences: no guess to unwind, but C13, C14 and X7 cannot finish their acceptance tests, and I1 cannot design backups.
3. **Per-route deadlines now, from each platform's terms as read by the team** (X 24 hours; others longer), with backups excluded from deletion entirely. Consequences: less engineering pressure, but a restore could resurface deleted data, and the team, not counsel, reads the terms.

## Decision

Defaults that can be built now, the strictest where a deadline is at stake, each confirmed by counsel before G4: an author's request deletes what it names and retires the author's account only if asked; identity is checked through the account's public contact; every deletion is engineered to X's 24 hours; a restore re-applies the deletion log first; audit rows hold no content or clear identities; client keyword terms are screened against a sensitive-events list before they run on X.

- (a) In plain words: an author's request deletes what they asked for, but stops monitoring of their public account only if they ask. A matching registered source's items are deleted like any other; if the request asks, retention-purger sends a `retire` decision with the new reason `owner_request` on `registry.decisions` (F2), which registry-writer applies and audits (AU-079; registry-writer, an approved PRD, gains the reason value under ADR-0001). That retirement is sticky: discovery never re-qualifies the source, and a later sighting does not bring it back as `updated` (ADR-0020); only a person can re-add it through the admin console, with the request on record.
- (b) Identity check: a confirmation sent to the account's public contact on the platform, as retention-purger proposes; the admin console (D3) records the request and the confirmation.
- (c) Deadlines: every deletion is engineered to the strictest documented deadline, X's 24 hours from a verified request or signal, on every route, until counsel sets per-reason deadlines; the X clock is read from X's compliance signal, with the compliance stream reconsidered at X's Enterprise review.
- (d) Backups may live longer than the deadline only if every restore re-applies the deletion log (`deletion_requests` and the tombstones of ADR-0035) before any data is served; I1 builds the restore procedure that way.
- (e) Audit and evidence rows hold ids, hashes, reasons and timestamps only, never content or clear identities, and are kept for the life of the client contract until counsel sets a period; the `meta_on_request` grace period is counsel's. X's `user_ids` arrive as X sends them and travel in the deletion target only so the archives can be searched (`x-compliance-sync §5.3 L81`); the evidence row keeps `author_ref`, not the id; identifiable X items follow `x_24h_sync`.
- (f) X sensitive events: client keyword terms are screened when they are entered, against the list of sensitive-event terms in a new F3 table, `screened_terms`, owned by the admin console (D3 specifies the writer) and kept by the user's compliance owner; the result is a new column `keywords.screening_status` (ADR-0044), written by the client portal (D3); a flagged term is not run on X.

It also answers: Also: (g) envelope-only archive files follow the text clock of their class, deleted with the item at 36 months for YouTube and on deletion for `meta_on_request` (`raw-archiver §14 Q3`); (h) at a client's offboarding retention-purger owns the deletion of data held only for that client, and yt-text-purger stops refreshing that client's YouTube text at once (`yt-text-purger §14 Q2`, offboarding hand-off); (i) the X blocked-terms list of (f) is the F3 table `screened_terms`, owned by the admin console (D3 specifies the writer), read by x-filtered-stream and x-recent-search (`x-filtered-stream §14 Q6`).

The screen of (f) also covers the automatic X keyword history of ADR-0059: a flagged term joins no X rule (ADR-0044), so no history is read for it.

Why: The strictest documented deadline and replay-after-restore are safe whatever counsel decides, so building to them loses nothing; the points that only counsel can settle stay open without blocking the build.

## Consequences

C13, C14 and X7 have a target to build and test; F2 adds the reason, F3 the table and column; I1 designs backups around replay-after-restore; a few lines in the portal and admin console specs (D3).

- CONVENTIONS v1.1, "Security and compliance in every service": the defaults (a) to (f), with (g) to (i).
- F2 adds the reason `owner_request`; F3 creates `screened_terms` and `keywords.screening_status` (ADR-0044); I1 designs backups so that a restore re-applies the deletion log before any data is served.
- The user's compliance owner keeps the sensitive-events list in `screened_terms`, before any client keyword runs on X.
- `DEFERRED.md`: counsel confirms each of (a) to (f), and the audit retention period and the `meta_on_request` grace period of (e), before production (owner G4).

Sessions that must read this: F2, F3, then C7, C13, C14, X7, I1, D3, U2, X1, X5, G4.
