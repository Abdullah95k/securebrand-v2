# ADR-0013 · Registry ownership and `registry.decisions`

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, registry-writer, qualifier, source-health-canary, retention-purger, yt-text-purger, quota-governor, keyword-matcher, backfill-orchestrator, listening-sdk, and the lanes Discover and qualify, Fetch posts and Comments (every poller, receiver and resolver)
Source: D2-Q013 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

For "one writer per topic and per column" the build plan proposes "every registry change goes through `registry.decisions` to registry-writer" (build plan L52), yet registry-writer owns only the identity and policy columns (`registry-writer §3 L27`) and leaves `last_hit_at`, `last_polled_at`, `next_poll_at` and `backfill_status` to their owners through the SDK (`§3 L30`). The topic's writers and shape disagree (CF-015): "the qualifier's decisions" (CONVENTIONS L20) against five producers (`registry-writer §4 L36`); `"decision":"add"` with full metadata (`qualifier §6.2 L84`) against the canary's `"action": "health_change"` with a `fallback` object, `scope`, `reason`, `evidence` and no key (`source-health-canary §6.2 L102`, `§14 Q1 L161`). Services change owned columns themselves (CF-033): pollers announce a dormant source's promotion (`fb-page-feed-poller §5.2 L59`) that the qualifier's sweep also makes (`qualifier §5.1 L46`; AU-058); hashtag pollers store `platform_id`, part of the unique key (`ig-hashtag-search §5.2 L66`); x-recent-search writes `last_hit_at` (`x-recent-search §5.2 L59`) beside keyword-matcher (`keyword-matcher §5.3 L79`). Receivers "ask registry-writer" to promote a source, return it to its reach tier, set `next_poll_at` or retire it (`fb-client-webhook-receiver §5.2 L59`, `yt-pubsub-receiver §6.2 L130`, `yt-uploads-reconciler §8 L154`) by a channel that does not exist (AU-016, AU-063), and other PRDs expect registry-writer to write five stores or columns it does not own (AU-021). At stake: one writer and one audit row for every registry change.

Settles: FC-02, CF-015, CF-033, AU-016, AU-021, AU-058, AU-063, registry-writer §14 Q4, source-health-canary §14 Q1.
Depends on: ADR-0002 (message metadata), ADR-0049 (`lifecycle` and `push_covered`).

## Options

1. **Two ownership classes and one request path** (chosen): its rules are under Decision.
2. **FC-02 literally: every `sources` change is a decision, operational columns included.** Consequences: one audit trail, but every poll and hit becomes a decision through one replica and an audit table kept ten years (`registry-writer §7 L107`), reversing the approved `§3 L30`.
3. **Named direct writers, listed in CONVENTIONS (CF-033 option 2).** Consequences: fewer messages, but no audit row for those changes, about twenty producers of `source.events` (CF-016), `platform_id` collisions on the unique key, and a route-wide `ok` that erases a fetcher's `blocked` (CF-032).
4. **A per-source attributes table owned by the resolvers and pollers (CF-033 option 3).** Consequences: platform facts get their own owners, but every scheduler joins a second table, and dormancy and push requests still need a path.

## Decision

registry-writer alone writes the registry's identity and policy columns (tier, lifecycle, push coverage, health and `platform_meta` among them) by applying `registry.decisions`. Each operational column has one named owner that writes it through the SDK, and every request that had no carrier becomes a decision in one schema with a closed type list.

- Columns (FC-02, CF-033): registry-writer alone writes the identity and policy columns (those of `registry-writer §3 L27` plus `lifecycle` and `push_covered` (ADR-0049), the health columns (ADR-0016) and `platform_meta` (ADR-0065)), applying `registry.decisions`. Operational columns have one owner each, written through the SDK without row locks (`registry-writer §12 L138`): the rotation summary by the primary poller (ADR-0015); `backfill_status` by backfill-orchestrator, `pending` being the column default (ADR-0020); `last_hit_at` by keyword-matcher only. Backfill reasons move from `notes` to `backfill_runs`.
- One schema (CF-015 a to d): `registry.decisions/v1` with ADR-0002's metadata, `decision_id`, the type in one field `decision` (the canary's `action` moves; `registry_audit.action` keeps the applied outcome), `requested_by` (stored as `registry_audit.actor`), `reason`, the subject, and a block per type (the canary's `fallback` object, `scope` and `evidence` included). Closed types: `add`, `update`, `remove_client`, `tier_change` (absorbs `tier_down`; a decay step below tier 3 is `dormant`), `dormant`, `promote`, `retire`, `push_coverage`, `health_change` (route or source level), and the audit-only `queued`, `mention_only`, `reject`, `review`. Key: `candidate_key`, or `source_id` for a registered source (ADR-0004), and `platform` for a route-level change, so successive states of a platform's routes stay in order (ADR-0004). The producers allowed per type are rows of F2's producer table (ADR-0012); registry-writer audits and rejects any other. It stays the topic's only consumer: yt-text-purger takes offboarding from `source.events` or `clients` (`yt-text-purger §5.1 L45`).
- Requests (AU-016, AU-058, AU-063): a poller or receiver that sees a dormant source post sends `promote` at once; the qualifier's sweep stays as the safety net, and a `promote` of an active source is a no-op. A lapsed lease or failed subscription is `push_coverage` off with a `reason` (`lease_lapsed`, `subscription_failed`), whose event makes the reconciler read at once (ADR-0014, ADR-0015), so no service writes another's `next_poll_at`. A confirmed vanished channel is `retire`. Learned facts (hashtag ids, member counts) are `update`; an id that would duplicate `(platform, platform_id)` is rejected with an audit row and `registry_duplicate`.
- Stores (AU-021): a) `news_sites` is news-site-resolver's (ADR-0040); a crawl refusal reaches `health` as a source-level decision from news-robots-checker (reason `crawl_disallowed`), and registry-writer reads no `crawl.policies`; b) the uploads playlist id goes in `platform_meta`, from yt-channel-resolver's profile (ADR-0065); c) a hashtag's bound Instagram account comes with its `add` decision, in `platform_meta`; d) a page a client starts administering gets an `update` (route, vendor, `owned_by_client`, `push_covered`, which stays false for TikTok Display accounts and LinkedIn client pages, ADR-0049) from the onboarding flow (ADR-0066); e) client flags are written by the client portal and admin console (D3, ADR-0043).

It also answers: The canary's route-level `health_change` carries `scope`, `reason`, `evidence` and the `fallback` object as its type block (`source-health-canary §14 Q1`).

Why: It keeps FC-02's guarantee (one writer, one audit row, one event) for every identity, tier, lifecycle and health change, keeps the approved carve-out for busy columns, and gives requests that had no carrier one schema.

## Consequences

Registry-writer (approved, ADR-0001) accepts more producers, `push_coverage` and source-level `health_change`; the qualifier (approved) sends `tier_change` where it sent `tier_down`; the pollers and receivers of CF-033 b) and AU-063 replace direct writes with decisions; F3's `TABLE-OWNERS.md` names the owner of every `sources` column.

- CONVENTIONS v1.1: `registry.decisions` (producers, schema and closed type list) and the owner of each `sources` column.
- When registry-writer applies a source-level `blocked`, it applies ADR-0021's automatic fallback rule; on every route-wide change it enforces ADR-0021's exclusion (a government-watched green source never moves to a vendor).
- F2 types `registry.decisions/v1`, with the allowed producers per decision type as rows of ADR-0012's table; F3's `docs/contracts/TABLE-OWNERS.md` follows this ADR.

Sessions that must read this: F2, F3, then C1, C5, C7, C9, C10, C12, C14, FB2, FB3, FB7, VFB1, VFB2, IG2, IG3, VTT2, VTT4, X1, X3, VLI3, TG1, VTG3, YT1, YT2, YT3, YT7, N1, N2, N3.
