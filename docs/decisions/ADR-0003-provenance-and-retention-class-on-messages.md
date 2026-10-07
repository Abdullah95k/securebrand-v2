# ADR-0003 · Provenance and retention class on messages

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q003 (user decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

"Every item carries provenance (route class, vendor, service, fetch time)" (`CONVENTIONS L115`). The repository rules go further: "Every output carries provenance (route, vendor, service, fetched_at) and `retention_class`" (`CLAUDE.md` L11); "Every topic payload carries provenance ... and retention_class" (F2 brief L36); the definition of done and the review checklist say the same (`build-plan/README.md` L40, `.claude/skills/review-session/SKILL.md` L22, `.claude/agents/prd-reviewer.md` L16). The PRDs miss it or rename it (CF-002): `article.urls` carries `found_at` or `first_seen_at` and no fetch time, search-hit-router's no route, vendor or class either; keyword-matcher's hit has no `fetched_at`; analyses carry `item_fetched_at`, profiles `resolved_at`, `item.metrics` `observed_at` flat or nested; the web engines' raw envelopes and yt-web-search-bridge's results have no class. Which `service` is meant varies (the fetching one in keyword-matcher's hit, the analysis service in analyses); only ig-account-resolver nests all four as `provenance {route, vendor, service, fetched_at}` (`ig-account-resolver §6.2 L119-L120`). Two classes are unclear: a profile is "registry metadata about an organization, kept as long as the source exists" for li-org-resolver (`li-org-resolver §7 L115`), while ig-account-resolver's acceptance test gives every message `meta_on_request` (`ig-account-resolver §13 L187`) and its individual message lists no class (`§6.2 L127`).

Settles: CF-002.
Depends on: ADR-0002.

## Options

1. **One nested `provenance {route, vendor, service, fetched_at}` object and a top-level `retention_class` on every message that carries or derives from a platform fetch; `producer` only on internal control messages** (chosen): its rules are under Decision.
2. **The same five fields flat on every data message (`route`, `vendor`, `service`, `fetched_at`, `retention_class`), the producing service only in `producer`.** Consequences: closest to most raw envelopes today; a flat `service` beside `producer.service` invites the confusion D1 found, and the SDK must copy five fields instead of one object.
3. **Provenance on every message, control messages included.** Consequences: the rules hold word for word, but jobs, completions and `source.events` would carry a route and fetch time for data they do not hold.
4. **Provenance only on `raw.items` and `items.normalized`; derived messages carry `item_id` (or `candidate_key`) and readers join.** Consequences: smaller messages, but every consumer that must show provenance or expire by class has to join.

## Decision

Every data output, meaning every message that carries or derives from a platform fetch, carries one nested `provenance {route, vendor, service, fetched_at}` object and a top-level `retention_class`. Job and control messages carry only `producer` (ADR-0002).

- Meaning: `provenance.service` is the service that fetched the data and `fetched_at` the time it was fetched; `producer.service` (ADR-0002) is the service that emitted this message. The SDK copies `provenance` and `retention_class` from the input record to every derived message (normalized item, hit, analysis, metrics, profile, item-scope deletion), so no service rebuilds them; the `raw.items` envelope carries the same object (ADR-0005).
- Data messages, with full provenance: `raw.items`, `items.normalized`, `item.hits`, `discovery.hits`, `poster.profiles`, `item.metrics`, `items.analysis`, `article.urls`, `search.results`, `deletions`, `news.dedup`; `crawl.policies`, since it records a fetch of robots.txt; and `registry.decisions` that derive from a fetch (qualifier's decisions from resolver profiles, news-robots-checker's crawl refusal, the canary's `health_change`). A decision entered by a person carries `requested_by` instead.
- Control messages, `producer` only: the job queues, `jobs.completed` and `source.events`, which carry no platform data.
- Deletions: an item-scope deletion copies the item's provenance and class. An author-, source- or client-scope deletion derives from no single record (`retention-purger §5.3 L78`, `deletion-propagator §5.3 L60`): it carries the signal's provenance (the service that received the request or compliance signal, its route and vendor, and `fetched_at` = when the signal arrived) and no `retention_class`, the one named exception, since it is kept as an audit row (ADR-0069 (e)).
- Profiles: a `poster.profiles` message carries the class of the route that fetched the profile, individuals' messages included. The registry columns filled from a profile of a non-individual (name, followers, signals) are registry metadata, refreshed by re-resolution and kept while the source exists, as li-org-resolver says; counsel confirms that reading for LinkedIn under ADR-0055.

Why: Provenance exists so that whatever reaches a client can say where the data came from and how long it may live; that applies to every message derived from a fetch, and to nothing in a job or a completion report. The nested object is the only form the SDK can stamp, copy and validate as one unit.

## Consequences

One type and one SDK check, and every data message can feed the client-facing provenance statement. The PRD examples change shape (flat to nested) under ADR-0001.

- The user's rule "every output carries provenance" reads "every data output". The user confirmed this reading by approving the decision. This pull request rewords the rule where it appears, each line citing this ADR:
  - `CLAUDE.md` L11: "Every data output (a message that carries or derives from a platform fetch) carries provenance (route, vendor, service, fetched_at) and `retention_class`; job and control messages carry `producer`."
  - The F2 brief's "Watch for" line (in `build-plan/tools/sessions.py`, the briefs regenerated): "Every data payload carries provenance (route, vendor, service, fetched_at) and retention_class; jobs, `jobs.completed` and `source.events` carry `producer` (ADR-0003)."
  - `build-plan/README.md` L40, `.claude/skills/review-session/SKILL.md` L22 and `.claude/agents/prd-reviewer.md` L16: "every data output" in place of "every output" and "outputs".
- CONVENTIONS v1.1: the event bus section and the compliance section carry the object, the field meanings, the lists of data and control messages, and the deletion exception.
- Counsel confirms that registry columns filled from a LinkedIn organisation's profile are registry metadata kept while the source exists (`DEFERRED.md`, with ADR-0055).

Sessions that must read this: F2, F4, F6, then C5, C6, C8, A1, A2, A3, A4, N3, N4, N5, W1, W2, W3, W4, W5, FB6, IG1, IG2, X1, VLI2, YT9.
