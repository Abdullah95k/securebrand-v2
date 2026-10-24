# ADR-0029 · ClickHouse topology and environments

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: F8, I1, E2, G2, G4, store-writer
Source: D2-Q029 (user decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

The build plan proposes one ClickHouse node with backups in staging and a replicated pair before production (FC-09), and three environments: local with the fake platform only, staging with real APIs on small budgets, and production (FC-12). The volume target is about 1,000,000 new posts and comments a day and ten years of aggregates (CONVENTIONS L3). F8 writes the migrations. Replication (two ClickHouse servers holding the same data, so one can fail) needs ClickHouse Keeper, a small coordination service that tracks which server has which data, and "replicated" table types, either from the first migration or through a later migration that converts the tables. Staging is where real API keys and vendor spend first appear (G2: "staging with real data"); the probes (FB0, X0, YT0 and the others) and their spend need the user's yes per call list anyway (`docs/orchestration/README.md`).

Settles: FC-09, FC-12, store-writer §14 Q2.

## Options

1. **As proposed** (chosen): its rules are under Decision.
2. **Replicated from staging.** Consequences: a higher ClickHouse cost from G2 (two nodes instead of one, plus Keeper); replication and failover are exercised for longer before production.
3. **One node in production as well, with backups.** Consequences: cheapest; a node loss stops ingestion and dashboards until a restore, and the restore point is the last backup.

## Decision

One ClickHouse node in staging, a replicated pair before production, replicated tables from the first migration, and three environments, as the build plan proposed.

Staging: one ClickHouse node with daily backups. Production: a replicated pair with ClickHouse Keeper (three small Keeper nodes, or Keeper on the cluster's control-plane nodes) before G4. F8 writes the tables with replicated engines from the start, so the same migrations run on one node and on the pair. Prerequisite: an embedded Keeper and the `{shard}` and `{replica}` macros in the local, CI and staging ClickHouse configs, since F1's local stack has neither (`compose.yaml`, `stack/`; F8 changes the `clickhouse-local` config, `docs/handoffs/F1.md` L120). Environments: local (fake platform, no network), staging (real APIs, each budget tag capped at a small figure the user sets per tag before G2), production.

Why: The data volume reaches production scale only in production; one node is enough to prove the pipeline in staging, while writing replicated engines from the first migration keeps the move to a pair a deployment change rather than a schema change.

## Consequences

The lowest cost until production; replication is proven in G4 rather than from day one.

- CONVENTIONS v1.1, analytics store: replicated engines from the first migration; one node in staging and a pair in production; the embedded Keeper and the `{shard}` and `{replica}` macros in the local, CI and staging configs (F8, with I1 for staging).
- The staging cap per budget tag goes into G2's plan; the user sets each one before G2 (`DEFERRED.md`).
- With ADR-0054's ten-year classes, ClickHouse holds up to ten years of items and comments where a class allows it, not only aggregates; I1 sizes the production pair for that, with store-writer's bytes per row measured in G2.

Sessions that must read this: F8 (replication settings in the migrations), I1, E2, G2, G4.
