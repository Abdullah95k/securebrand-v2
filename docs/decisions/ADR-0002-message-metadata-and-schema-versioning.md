# ADR-0002 · Message metadata and schema versioning

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q002 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

The PRDs version their messages three ways (CF-001): a string `schema` such as `"items.normalized/v1"` beside `message_id`, `produced_at` and a `producer {service, version, job_id}` block (`normalize-item §6.2 L95-L98`, `keyword-matcher §6.2 L99-L102`, the four analysis services); a string `schema` with a flat `service` field (news-dedup, news-robots-checker, news-site-resolver, tg-channel-resolver, tg-message-search, search-hit-router, web-commoncrawl-scanner, the web engines, the `jobs.completed` examples in comment-decay-scheduler and backfill-orchestrator, `comment-decay-scheduler §5.4 L127`, `backfill-orchestrator §5.4 L92`); an integer `schema_version` (`poster-resolver §6.2 L89`, `qualifier §6.2 L84`, `registry-writer §6.2 L95`); or nothing at all (every `raw.items` envelope, `item.metrics`, `deletions`, the news pollers' `article.urls`, the resolvers' `poster.profiles`, several `discovery.hits`). Two consumers branch on the string: store-writer parks any message whose `schema` it does not know (`store-writer §5.2 L46`) and search-hit-router parks a message without `schema = search.results/v1` (`search-hit-router §5.2 L55`), so as written store-writer would park every `item.metrics` and `source.events` message. CONVENTIONS puts "topic schemas" in listening-sdk (L12) but names no field. The build plan's foundation choice is "additive changes within a version; a breaking change is a new version with a dual-publish window" (FC-04), and `.claude/rules/contracts.md` already points to F2's `docs/contracts/VERSIONING.md`.

Settles: FC-04, CF-001.

## Options

1. **A `schema` string on every message, with one metadata block, and the build plan's versioning rule** (chosen): its rules are under Decision.
2. **An integer `schema_version` on every message, the topic implied by the topic name, with `message_id`, `produced_at` and a flat `service`.** Consequences: shorter, but a message copied out of its topic (the raw archive, a DLQ, a replay) no longer says what it is, and store-writer and search-hit-router change.
3. **The version in a Kafka header set by the SDK, nothing in the body.** Consequences: clean bodies, but the archive and the DLQ lose the version unless they copy headers, and every PRD example changes.

## Decision

Every message carries `schema: "<topic>/v<n>"` and every job `schema: "job/v<n>"`, with `message_id`, `produced_at` and `producer {service, version, job_id}`, all four stamped by the SDK. A change that only adds an optional field stays in its version; anything else is a new version, published beside the old one for a dual-publish window.

Every message on every topic carries `schema: "<topic>/v<n>"`, and every job on every queue `schema: "job/v<n>"` (one job envelope for all queues, its kind-specific fields validated by `kind`, ADR-0011); each also carries `message_id` (a ULID, derived deterministically where a replay must reproduce the same id, as ADR-0006 describes for `job_id`), `produced_at`, and `producer {service, version, job_id}`; the SDK stamps all four, so no service writes them by hand. Versioning: a change that only adds an optional field stays in the version; anything else (a removed or renamed field, a changed type or meaning) is a new version, published on the same topic beside the old one for a dual-publish window long enough for every consumer to move (F2's `VERSIONING.md` sets its length). The contracts package ships the new version before any producer emits it, so a consumer skips a known version it does not read and keeps reading the old one; it parks only versions the contracts package does not know, as store-writer does.

Why: It is what most producers and both branching consumers already do, it survives archiving and replay, and the SDK can stamp it in one place.

## Consequences

The majority form, and the one the two branching consumers already read; three approved PRDs (poster-resolver, qualifier, registry-writer) change `schema_version` to `schema` under ADR-0001; a message archived to object storage still says what it is, without its Kafka headers.

- CONVENTIONS v1.1, event bus: the four metadata fields and the versioning rule.
- F2 writes `docs/contracts/VERSIONING.md` from this ADR and sets the length of the dual-publish window there. The contracts package ships a new version before any producer emits it.
- F4 and F6 stamp the four fields; no service writes them by hand. A consumer skips a known version it does not read and parks only a version the contracts package does not know.

Sessions that must read this: F2 first, F4, F6, then C6, C7, C8, C9, W3 and every producer of a topic.
