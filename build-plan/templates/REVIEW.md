# Review · <ID> <service or package>

Reviewer session · date · diff reviewed: <base>..<head>

Verdict: ready to merge | needs fixes (N blockers, M should-fix)

## Acceptance criteria

| PRD 13 | Test | Command | Result | Evidence |
|---|---|---|---|---|
| 1 | | | pass / fail / untested | |

## Findings

| # | Severity | File:line | Finding | Demonstrated by | Status |
|---|---|---|---|---|---|
| 1 | blocker / should-fix / note | | | failing test or command | open / fixed in <commit> / declined |

## Conventions checklist

- [ ] Replay changes nothing
- [ ] Cursors advance after producer acknowledgement
- [ ] Error policy: 429, 401 and 403, empty 200, DLQ after five attempts
- [ ] Rotation or comment series as PRD 5.1
- [ ] Budget tag and priority
- [ ] Outputs validate; provenance and retention_class present
- [ ] Metric names as PRD 10
- [ ] No secrets or private names in code, logs or fixtures
- [ ] Dependencies listed and clear of the vendor screen
- [ ] No contract edits; scope limited to this service (plus an allowed mapper)
- [ ] Amber code only behind its flag
