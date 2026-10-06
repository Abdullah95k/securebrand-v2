# Iraq listening platform

Social-media and news listening for the Iraqi market: 86 services, one per PRD in `docs/prds/`, plus shared packages. Built one service per Claude Code session, following `build-plan/README.md`.

## Non-negotiables

- No Israeli-owned or Israel-affiliated vendor, API or hosted service anywhere. The excluded and flagged lists are in the first section of `docs/prds/_shared/CONVENTIONS.md`. Every new runtime dependency gets a line in `docs/dependencies.md` (name, licence, owner, country) in the same pull request.
- Only the routes a PRD names. Never build a red route: no logged-in scraping, no account pools, no CAPTCHA solving, no residential proxies on platform APIs, and never rotate accounts or IPs to get around a block. Proxies exist only in the news crawler, for challenged hosts.
- Amber (vendor) code runs only behind its flag (`FB_VENDOR_ROUTE`, `IG_VENDOR_ROUTE`, `TT_VENDOR_ROUTE`, `LI_VENDOR_ROUTE`, `TG_VENDOR_ROUTE`, `TG_POSTS_ACTOR`), off by default.
- Individuals are never profiled: authors are hashed references, and individuals are never backfilled.
- Every output carries provenance (route, vendor, service, fetched_at) and `retention_class`.
- IMPORTANT: contracts are frozen. Never edit `packages/contracts`, `supabase/migrations` or `clickhouse/migrations` (a hook blocks it). If you need a change, write `docs/proposals/<session>-<topic>.md` from `build-plan/templates/PROPOSAL.md` and stop.

## Commands

- `make up` / `make down`: local stack (Redpanda, Supabase, ClickHouse, SeaweedFS)
- `make check`: lint, types and tests for the packages that differ from main (`scripts/check-changed.sh`)
- `make test SERVICE=<name>` (pre-approved; runs the service's unit and acceptance tests, TypeScript or Python)
- `pnpm --filter <service> test` and `uv run pytest` work too, but ask for approval each time
- `make e2e GATE=G1`: the end-to-end suite of a gate
- `pnpm new:service <name>`: scaffold a service from `services/_template`

## Layout

- `services/<name>/`: one per PRD (TypeScript unless the PRD says Python)
- `packages/contracts`, `packages/listening-sdk`, `packages/text`, `py/listening_sdk`
- `supabase/migrations`, `clickhouse/migrations`
- `fixtures/<platform>/`: recorded, scrubbed responses from probe sessions
- `tools/probes/<platform>/`: the only code allowed to call real platforms
- `docs/`: prds, decisions (ADRs), contracts, plans, handoffs, reviews, probes, proposals, issues, gates, patterns
- `build-plan/`: session briefs, gates, templates

## How every session works

- Start from the session brief `build-plan/sessions/<ID>-*.md` and stay inside its scope: one service per session.
- Read the PRD in full, then only the CONVENTIONS sections and ADRs the brief lists, and the handoff notes of the sessions in its "Needs first". Do not read other services' code unless a handoff points to it.
- Acceptance tests from PRD section 13 first, then code. Show test output; never claim a result you did not run.
- Use `listening-sdk` for jobs, retries, DLQ, cursors, quota, canary, logging and metrics. Never re-implement them.
- No network in tests: fixtures and the fake-platform harness only.
- Replaying a job or message must change nothing. Cursors advance only after the producer acknowledges.
- Errors: 429 and vendor rate limits back off 30 s to 15 min with jitter; 401 and 403 mark the route degraded and stop the batch; after 5 attempts the job goes to `dlq.<service>`.
- When the PRD, CONVENTIONS, an ADR or a handoff disagree, or the PRD is silent: ask me with AskUserQuestion. Do not guess. Record the answer in the plan and the handoff.
- If a dependency does not behave as its handoff says: write a failing test, record it in `docs/issues/`, and stop.
- Never print, log or commit secrets. Do not read `.env` files; code reads credentials from the environment at run time.
- Finish with `make check` output, `docs/handoffs/<ID>.md` from `build-plan/templates/HANDOFF.md`, and `/code-review`.

## Code

- TypeScript strict, ES modules; no `any` without a comment saying why. Contract types come from `packages/contracts` only; never redeclare one.
- Python version pinned in `.python-version`; typed; ruff-clean; Pydantic models generated from the contracts.
- Tests: Vitest and pytest. Test names state the behaviour, for example `emits a deletion when a comment disappears from a complete sweep`.
- Logs are structured JSON with `job_id`, `source_id`, `route`, `vendor`; metric names are the ones in the PRD's section 10.

## When compacting

Keep the session ID and brief path, the plan path, the files changed so far, failing tests with the commands that run them, and any open questions for me.
