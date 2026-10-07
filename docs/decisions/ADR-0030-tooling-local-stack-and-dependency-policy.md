# ADR-0030 · Tooling, local stack and dependency policy

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all
Source: D2-Q030 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

F1 merged with the tooling, local stack and dependency policy of the build plan (FC-10, FC-11, FC-13): pnpm 10.34.6 and Turborepo 2.10.13 with strict TypeScript 6.0.3, ESLint and Vitest 4.1.11; uv 0.12.23 with ruff, pyright and pytest 9.1.1; a docker compose stack with Redpanda v26.1.18, the Supabase CLI 2.120.0, ClickHouse 26.3.38.2 and SeaweedFS 4.48 as local S3; and `docs/dependencies.md` with a CI policy check (`docs/handoffs/F1.md`, "Decisions made here" and "For the sessions that depend on this"). One part of FC-10 is not built yet: "Zod 4 to JSON Schema to Pydantic", which is F2's pipeline (F2 brief: "Zod schemas for every topic, job and envelope; JSON Schema export; Pydantic models for Python").

Settles: FC-10, FC-11, FC-13.

## Options

1. **Ratify what F1 built, and fix F2's pipeline as Zod 4 to JSON Schema to Pydantic** (chosen): its rules are under Decision.
2. **JSON Schema as the hand-written source, generating Zod and Pydantic from it.** Consequences: a language-neutral source, but every schema is written in a format nobody runs, and Zod types lose the refinements Zod expresses directly.
3. **A schema registry with Avro or Protobuf (Redpanda ships one).** Consequences: compatibility checks enforced by the broker, but every PRD example and the SDKs move from JSON to a binary format; a larger change than the PRDs assume.

## Decision

What F1 built is ratified: pnpm and Turborepo, strict TypeScript, ESLint and Vitest; uv, ruff, pyright and pytest; the docker compose stack; `docs/dependencies.md` with its CI check. F2's schema pipeline is Zod 4 to JSON Schema to Pydantic, as follows.

F2 writes the schemas in Zod 4, exports JSON Schema (draft 2020-12) with Zod's own exporter, and generates Pydantic v2 models from it (for example with `datamodel-code-generator`, recorded in `docs/dependencies.md`); conformance tests in both languages run the same valid and invalid fixtures.

Why: It ratifies a merged, tested foundation and keeps F2's pipeline as the build plan wrote it.

## Consequences

No change to anything merged; TypeScript is the source of truth, which matches the Node majority of services.

- CONVENTIONS v1.1 names the schema pipeline in the repository section (v1 L12).
- F2 records its model generator (for example `datamodel-code-generator`) in `docs/dependencies.md`, and its conformance tests in both languages run the same valid and invalid fixtures.

Sessions that must read this: F2 (the schema pipeline) and every session (the toolchain).
