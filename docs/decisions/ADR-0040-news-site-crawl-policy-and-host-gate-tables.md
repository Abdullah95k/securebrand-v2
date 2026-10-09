# ADR-0040 · News site, crawl-policy and host-gate tables

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F2, F3, listening-sdk (F4), qualifier, registry-writer, comment-decay-scheduler, and news: news-robots-checker, news-site-resolver, news-feed-poller, news-sitemap-poller, news-homepage-differ, news-article-extractor, news-comments-fetcher
Source: D2-Q040 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

- Crawl permission (CF-029). news-robots-checker expects registry-writer to turn `crawl_allowed = false` into `sources.health = blocked` (`news-robots-checker §5.2 L61`, `§6.2 L117`), but registry-writer reads only `registry.decisions` (`registry-writer §6.1 L86`). The fetchers check the policy themselves before fetching (`news-feed-poller §5.1 L40`, `news-sitemap-poller §5.1 L41`, `news-homepage-differ §5.1 L41`, `news-article-extractor §5.2 L52`).
- `news_sites` (CF-047). news-site-resolver writes it, "one row per host" with `status: candidate` (`news-site-resolver §6.3 L116`, `§5.2 L54`), yet expects registry-writer to write the accepted profile "keyed by `source_id`" (`news-site-resolver §6.2 L112`; also `news-feed-poller §5.1 L48`). registry-writer has no such path, a candidate has no `source_id`, and the resolver asks whether to fold the table into `sources.notes` (`news-site-resolver §14 Q2 L172`).
- `crawl_policies` (CF-048). The row (`news-robots-checker §6.3 L121`) lacks the message's `reason`, `changed_fields` and `requested_by` (`§6.2 L96-L115`). Five services keep the gate's slot in that row (`news-feed-poller §5.3 L66`), which the robots-checker upserts whole and needs before the row exists (`news-robots-checker §5.2 L54`, `L61`); README decision 6 puts the gate, not its state, in listening-sdk (`README L183`).
- Disqus fields (AU-028). news-comments-fetcher needs an identifier template (`news-comments-fetcher §5.1 L49`, `§5.2 L55`) that the resolver parses (`news-site-resolver §5.2 L47`) but does not emit (`§6.2 L102`), and marks "the site's comments `degraded`" (`news-comments-fetcher §8 L139`) with no column to hold it.

At stake: whether an accepted site is ever polled, and whether a policy refresh can erase a slot just taken.

Settles: CF-029, CF-047, CF-048, AU-028, news-comments-fetcher §14 Q3, news-site-resolver §14 Q2.
Depends on: ADR-0013 (crawl refusals as source-level decisions), ADR-0022 (the host gate's spacing and error rules), ADR-0066 (the pre-allocated `source_id`).

## Options

1. **One writer per table, crawl refusals sent as registry decisions, the gate in its own table** (chosen): its rules are under Decision.
2. **registry-writer as the news path (CF-029 (1), CF-047 (2), CF-048 (1)).** registry-writer consumes `crawl.policies`, maps `crawl_allowed` onto `health` and writes `news_sites` from the decision's profile, keyed by `source_id`, candidates in a resolver table; the slot stays in `crawl_policies.next_slot_at`, which the robots-checker's upsert leaves alone. Consequences: no new decisions, but registry-writer reads a second topic and learns a news schema, a candidate needs a second table, and two writers still share each policy row.
3. **Crawl permission only in `crawl_policies`, the profile as jsonb on `sources`, gate state outside the control plane (CF-029 (3), CF-047 (3), CF-048 (3)).** Consequences: no health decisions and one table fewer, but `health` stays `ok` on a blocked site, every profile refresh becomes a registry decision, and a gate outside Postgres needs a service or shared cache the stack lacks.

## Decision

Each news table has one writer. news-site-resolver writes `news_sites`, keyed by a `source_id` it allocates with the candidate row; news-robots-checker writes `crawl_policies` and turns a crawl refusal into a source-level `health_change` decision; the host gate keeps its slots in its own table, `host_gate`, written only by the SDK gate.

- `news_sites`, written only by news-site-resolver: primary key `source_id`, `host` unique. The resolver allocates the `source_id` with the candidate row and sends it as `proposed_source_id` in `proposed_source`; the qualifier's `add` passes it on and registry-writer inserts under it (ADR-0066's rule for owned properties), never writing `news_sites`. Columns: the `site_profile` fields (`news-site-resolver §6.2 L96-L105`), `status` (`candidate`, then `registered` once the `sources` row exists), `resolved_at`, `profile_version`, and the Disqus fields `comments_provider` (the PRDs' spelling), `disqus_shortname`, `disqus_identifier_template` (new) and `comments_health` (`ok` or `degraded`, new). It stays a control-plane table (answers `§14 Q2 L172`). On refresh, identity changes go to registry-writer as `update` decisions (ADR-0013); readers read `news_sites` at each job, so profile changes need no event.
- Disqus health: a rejected shortname makes news-comments-fetcher stop and send its `refresh` with that reason, a new refresh trigger (`news-site-resolver §5.1 L40`); the resolver re-reads the embed and records a new shortname, `comments_provider = none` if the embed is gone, or `comments_health = degraded`. comment-decay-scheduler opens no Disqus series unless `comments_health = ok`. A per-article `disqus_identifier` from the extractor stays an optional field, N6's choice (`news-comments-fetcher §14 Q3 L186`).
- `crawl_policies`, written only by news-robots-checker, primary key `host`. Row and `crawl.policies` share one column list (ADR-0070 b)'s flat names): `host`, `status`, `crawl_allowed`, `reason`, `access_mode`, `crawl_delay_seconds`, `robots_status`, `robots_rules` (group, rules, sitemaps, hash), `usage_signals`, `rsl`, `payment`, `checked_at`, `expires_at`, `policy_version`. The message adds the change fields `changed_fields`, `requested_by`, `kind`; the row adds `next_refresh_at`. No slot column.
- Crawl permission reaches `sources.health` as ADR-0013 has it: when `crawl_allowed` flips for a registered site, or at the `added` event of a site added while disallowed, news-robots-checker sends a source-level `health_change` decision (reason `crawl_disallowed`, back to `ok` once allowed); registry-writer reads no `crawl.policies` (`news-robots-checker §5.2 L61`, `§6.2 L117` reworded). Fetchers still read the policy row before every request, for path rules and the access mode.
- `host_gate` (`host`, `next_slot_at`, `holder`, `spacing_seconds`), written only by the listening-sdk gate, one conditional update per slot; created on first use, so a first robots check can take a slot.

Why: Each table gets one owner, the row several services wrote is split, and a blocked site shows in `health` through the one registry path; the pre-allocated `source_id` lets one row follow a site from candidate to registered.

## Consequences

Three tables with one writer each; F4 builds the gate on its own table; the five gate users' state lines and the registry sentences of `news-site-resolver §6.2 L112`, `news-feed-poller §5.1 L48` and news-robots-checker are reworded; the approved news-site-resolver and qualifier (which passes `proposed_source_id` on) move under ADR-0001.

- CONVENTIONS v1.1: `news_sites` and `host_gate` join the control-plane tables (v1 L30), with the column list of `crawl_policies`, each table with its writer; the news fact sheet names the gate's table.
- F2 types `crawl.policies/v1` with the row's flat names (ADR-0070); F3 creates the three tables; F4 builds the gate on `host_gate`.

Sessions that must read this: F2, F3, F4 (the host gate), C7, C9, N1, N2, N3, N4, N5, N6, N8.
