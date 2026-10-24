---
paths:
  - "packages/contracts/**"
  - "supabase/migrations/**"
  - "clickhouse/migrations/**"
---

# Frozen contracts

- These paths change only in F2, F3, F8 or a contract-change session started with `ALLOW_CONTRACT_EDITS=1`, applying an approved proposal from `docs/proposals/`.
- Versioning follows `docs/contracts/VERSIONING.md` (ADR-0002): a change that only adds an optional field stays within its version; anything else is a new version with a dual-publish window.
- Every change regenerates the JSON Schemas and the Python models, updates the valid and invalid fixtures, and passes the conformance suites in TypeScript and Python.
- Migrations are forward-only, run cleanly from zero and re-run cleanly; every client-facing table has row-level security with a test.
- `docs/contracts/TABLE-OWNERS.md` names the one service that writes each column; keep it true.
