# Contracts

The documents behind the frozen contracts. D1 writes the inventory and its conflicts
(`/decide-session D1`), F2 writes the versioning rules with `packages/contracts`, and F3 writes the
table ownership map with `supabase/migrations`. The contracts themselves live in
`packages/contracts`, `supabase/migrations` and `clickhouse/migrations`, which only F2, F3, F8 and
contract-change sessions edit (see `docs/proposals/`).
