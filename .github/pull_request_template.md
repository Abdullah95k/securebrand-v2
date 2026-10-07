## Session

<!-- The lane's session ID, its brief and its plan. -->

ID: · brief: `build-plan/sessions/<ID>-*.md` · plan: `docs/plans/<ID>.md`

## What changed

## Checks

- [ ] `make check` passes; the acceptance tests and their results are in `docs/handoffs/<ID>.md`
- [ ] `docs/reviews/<ID>.md` ends with "ready to merge" (a fresh-session review)
- [ ] Every new runtime dependency has its row in `docs/dependencies.md`, checked against the vendor screen
- [ ] No change under the contract paths, or the `contract-change` label with an applied proposal
- [ ] Fixtures are scrubbed (`scripts/check-fixtures.sh`)
