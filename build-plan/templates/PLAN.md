# Plan · <ID> <service or package>

Brief: build-plan/sessions/<ID>-<slug>.md · PRD: docs/prds/<platform>/<service>.md · Approved by: <name, date>

## Acceptance map

| PRD 13 | Criterion (short) | Test (file :: name) | Level | Fixture |
|---|---|---|---|---|
| 1 | | | unit / contract / acceptance / e2e | |

## Uncovered behaviours (PRD sections 5 and 8)

| Behaviour | Test | Fixture or fake-platform scenario |
|---|---|---|
| Rotation or series timing | | |
| Catch-up when behind | | |
| 429 backoff, 401 and 403 degrade and stop, empty 200 counted | | |
| 5xx in the middle of pagination | | |
| DLQ after five attempts | | |
| Replay changes nothing | | |

## Contracts

| Kind | Name | Version | Read or write | Exists? |
|---|---|---|---|---|
| topic | | | | yes / proposal needed |
| job queue (kinds) | | | | |
| table (columns) | | | | |

Proposals needed: none | list

## Build outline

- Files to create:
- SDK features used:
- Mapper added to normalize-item: none | record shapes
- Budget tag and priority:
- Metrics and alerts (PRD 10):

## Risks (PRD 12) and their tests

| Risk | Covered by |
|---|---|

## Questions and answers

| # | Question | Answer | Decided by | ADR |
|---|---|---|---|---|
