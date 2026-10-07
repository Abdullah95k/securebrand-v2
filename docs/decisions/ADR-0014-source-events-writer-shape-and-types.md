# ADR-0014 · `source.events`: writer, shape and types

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q014 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

CONVENTIONS names no writer and spells one type with a space: "added, updated, tier change, dormant, retired, fallback_on, fallback_off" (L21). registry-writer describes itself as the one path that emits "one `source.events` message per change" (`registry-writer §1 L9`), with `tier_change` (`§3 L24`) and the only defined shape (`§6.2 L95`: `message_id`, `schema_version`, `event`, the source's columns, `previous`, `decision_id`, `actor`, `at`). About twenty services publish events themselves (CF-016 b): `tier change` when a dormant source posts (`fb-page-feed-poller §6.2 L129`, `ig-account-media-poller §6.2 L125`), `updated` on a health or grant change (`li-client-posts-poller §6.2 L126`, `x-user-timeline-poller §8 L151`), `updated` with `backfill_status` (`fb-backfill §6.2 L110`), budget waits (`ig-hashtag-search §5.1 L57`). Readers wait for types nobody emits (CF-098 b): a `route` change (`li-client-posts-poller §6.1 L101`) and `reason = push_lease_lapsed` (`yt-uploads-reconciler §5.1 L51`). A route `blocked` has no event: registry-writer maps health only to `fallback_on`, `fallback_off` or `updated` (`registry-writer §5.2 L54`; CF-098 c). At stake: about 46 consumers rebuild their registry caches from this topic (CF-016).

Settles: CF-016, CF-098, yt-uploads-reconciler §14 Q4.
Depends on: ADR-0013 (changes arrive as decisions), ADR-0049 (`lifecycle`, `push_covered`).

## Options

1. **registry-writer is the only writer, from its outbox, with one closed list** (chosen): its rules are under Decision.
2. **Direct writes stay for operational events, in registry-writer's shape (CF-016 option 2).** Consequences: no extra decisions, but events with no audit row or `decision_id`, and an event that says "promoted" while the column says dormant (CF-033).
3. **Two topics: `source.events` for registry changes and an operational-signals topic for pollers' observations (CF-016 option 3).** Consequences: a clean separation, but a new topic, schema and readers, and the observations still need a path into the registry.
4. **CONVENTIONS' list in underscores, everything else as `updated` with a free `reason` (CF-098 option 1).** Consequences: the smallest change, but `blocked`, lifecycle and push coverage hide inside `updated`, and every consumer parses reasons.

## Decision

registry-writer is the only writer of `source.events`. It publishes from its outbox one event per applied decision and source, in one shape that carries `previous`, from a closed list of snake_case types.

- Writers (CF-016): every change a PRD published directly becomes a decision (ADR-0013) or leaves the topic. Promotion, dormancy, source health, grants and push coverage are decisions. `backfill_status` changes are not events: pollers read the column, and completion travels on `jobs.completed` (ADR-0020). A budget wait is not a registry change: the job ends `quota_denied` (ADR-0057), the portal shows it (D3), and a hashtag beyond the cap is ADR-0052's.
- Shape `source.events/v1`: ADR-0002's metadata, `event`, `reason`, `source_id`, the source's identity and policy columns after the change, `previous` (the old value of every changed column), `decision_id`, `actor` (the decision's `requested_by`), `at`. One event per applied decision and source; its `message_id` is kept on the `registry_audit` row, so an outbox re-publish repeats it. Consumers follow a column through `previous`, not through the type alone.
- Types (CF-098), in snake_case: `added`; `updated` (an identity or policy change, route and vendor included, shown in `previous`; clients added or removed; a re-added retired source, never one retired at its owner's request, ADR-0069); `tier_change`; `lifecycle_change` (to `dormant` or `retired`, or reactivated to `active`; replaces `dormant` and `retired`); `health_change` (`ok`, `degraded` or `blocked`, route or source level); `fallback_on` and `fallback_off` (they change provenance); `push_coverage_change`. `reason` values are one closed list in F2 (for example `lease_lapsed`, `subscription_failed`, `bot_removed`, `client_removed`).

Why: One writer gives every event an audit row, a `decision_id` and `previous`, so caches can be rebuilt and a replay changes nothing; typed events for the states consumers act on spare them from parsing free text.

## Consequences

One shape for every consumer; registry-writer (approved, ADR-0001) replaces two types and adds three; about twenty PRDs drop their direct events; yt-uploads-reconciler listens for `push_coverage_change` with `reason = lease_lapsed`, li-client-posts-poller for `updated` with `previous.route`.

- CONVENTIONS v1.1: `source.events` (its writer, its shape and the closed type list).
- `fallback_on` and `fallback_off` also mark one source's automatic fallback under ADR-0021, with the source-level `reason`.
- F2 types `source.events/v1` and the closed `reason` list.

Sessions that must read this: F2, then C6, C7, C10, C11, C12, FB2, FB3, FB7, VFB2, IG2, IG3, IG4, IG5, LI1, LI3, VLI3, N2, N3, TG1, TG2, VTG3, TT1, VTT4, X3, X5, YT2, YT3, and every `source.events` consumer.
