# Gates

A gate session verifies; it fixes nothing. Each check gets its command or query, an output excerpt, and pass or fail in `docs/gates/<gate>.md`. The next wave starts only when the gate is green. What a gate runs is built beforehand: E1 builds the G1 suite (`tests/e2e/G1`, `make e2e GATE=G1`) and E2 the scripts for G2 to G4 (`tools/gates/`). Each platform's go-live session fills in its own compliance check in E2's scripts.

## G0 · Foundation (end of Wave 1)

1. `pnpm new:service demo` produces a service that passes `make check` without edits.
2. TypeScript and Python accept and reject the same contract fixtures, and derive identical keys from the golden vectors.
3. Migrations apply on an empty database and rerun cleanly; row-level security tests pass.
4. The fold golden suite passes in TypeScript.
5. `make up` brings the local stack up in one command on a clean machine, and CI is green on main.

## G1 · The core on the fake platform (end of Wave 2)

Built by E1 in `tests/e2e/G1` and kept as the regression suite.

1. A source added by ops is backfilled 90 days, then joins the rotation at its tier's cadence.
2. Over a simulated 48 hours every source stays within its tier's interval; a stalled poller recovers most stale first and raises `rotation_behind`.
3. A new post gets its comment series; early stop and extension follow the comment-series ADRs; a hot post gets its hourly extras.
4. An unknown poster in a keyword hit goes through poster-resolver and qualifier and is added, rejected or sent to review by the rules.
5. Posts and comments are normalized with language, dialect and `text_norm`, matched against keywords, stored in ClickHouse, and the aggregates update.
6. Every job and message replayed twice changes nothing.
7. A burst of 429s backs off; a 401 on a client token revokes that credential, blocks the sources only it reads and stops the batch, and a blocked source falls back to its amber route where ADR-0021 allows, with a notice to ops; a burst of empty 200s flips the canary; a source a government client watches, or a client-owned property, never falls back to amber (ADR-0021).
8. At 80% of a budget, amber intervals stretch and hot-post extras stop; at 95%, only priorities 1 and 2 run.
9. A deletion reaches ClickHouse, the archive and the aggregates; a retention purge removes raw text and keeps aggregates.
10. A record with an unknown shape is archived and parked, never dropped.
11. With lang-dialect-id down, normalize-item falls back, and rescoring catches up after recovery.
12. An hour of synthetic load at 1.5 times the target daily rate keeps lag within one tier interval.

## G2 · Staging with real data (end of Wave 3)

1. 72 hours of news and web on staging with real Iraqi sources and your keywords.
2. The SLOs in CONVENTIONS hold: rotation lag below one tier interval for 99% of sources, comment series on time for 95% of posts, zero lost jobs, the DLQ reviewed daily with nothing unexplained.
3. On a 200-item sample you label, language, dialect, duplicate stories, extraction completeness and keyword-hit precision meet the targets set in D2.
4. The crawl logs show no request against a site's robots, Content Signals, RSL or 402 policy.
5. Cost per 1,000 items is within budget, and the quota governor's counters match the vendors' own dashboards.
6. Restore drill: the control plane and one day of ClickHouse restored from backup into a scratch environment.

## G3 · Platform go-live (one report per platform: `docs/gates/G3-<platform>.md`)

1. Every difference the platform's probe found is resolved in the PRD or an ADR.
2. 72 hours on staging for that platform, meeting the G2 SLOs.
3. Compliance checks for that platform pass: the YouTube 30-day purge in a dry run; an X post deleted on a team account disappears from every store within 24 hours; LinkedIn member data is gone after 48 hours; a Meta deletion request runs end to end; amber flags default to off and provenance is correct.
4. A canary flip rehearsed on staging: revoke a token, see `degraded` and the alert.
5. Runbook and dashboards in place; cost per 1,000 items within budget.

## G4 · Production readiness (before the first client sees data)

1. Security review: secrets only in the vault, row-level security on every client-facing table, every webhook endpoint verifies the platform's signature or secret token, dependency and image scans clean.
2. Backups and a restore drill for Postgres, ClickHouse and object storage, against the recovery targets you set.
3. 24 hours of synthetic load at 1.5 times full scale through the fake platform on staging, with lag, DLQ and insert rates within the SLOs.
4. Provenance statement, client terms and DPA signed off by counsel; government contracts exclude amber.
5. Alerts reach a person, and every service with alerts has a runbook.
