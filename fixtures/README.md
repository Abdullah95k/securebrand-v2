# Fixtures

Recorded, scrubbed responses, one folder per platform or vendor (`fixtures/<platform>/`), written by
probe sessions; plus `fixtures/contracts/` (F2's valid and invalid contract examples) and
`fixtures/text/` (F7's golden corpus). The rules are in `.claude/rules/fixtures.md`, and
`scripts/check-fixtures.sh` (part of `make check` and the CI policy job) enforces them:

- no token or signed URL anywhere under `fixtures/`;
- raw responses only in `fixtures/<platform>/raw/`, which is gitignored and never tracked;
- every file of a platform folder listed in a `README.md` of its folder (the call, the date, what was
  scrubbed); synthetic fixtures are named `synthetic-*`.
