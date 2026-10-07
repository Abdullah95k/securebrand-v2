# Proposals

`docs/proposals/<ID>-<topic>.md` from `build-plan/templates/PROPOSAL.md`: a change a session needs in
a frozen contract (`packages/contracts`, `supabase/migrations`, `clickhouse/migrations`). The user
decides. An approved proposal is applied by `/contract-change` on the branch `sb/CC-<ID>-<topic>`,
whose pull request carries the `contract-change` label.
