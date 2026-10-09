# Iraq listening platform

Social-media and news listening for the Iraqi market: 86 services, one per PRD in `docs/prds/`, plus shared packages. Built one service per Claude Code session, following `build-plan/README.md`.

## Non-negotiables

- No Israeli-owned or Israel-affiliated vendor, API or hosted service anywhere. The excluded and flagged lists are in the first section of `docs/prds/_shared/CONVENTIONS.md`. Every new runtime dependency gets a line in `docs/dependencies.md` (name, licence, owner, country) in the same pull request.
- Only the routes a PRD names. Never build a red route: no logged-in scraping, no account pools, no CAPTCHA solving, no residential proxies on platform APIs, and never rotate accounts or IPs to get around a block. Proxies exist only in the news crawler, for challenged hosts.
- Amber (vendor) code runs only behind its flag (`FB_VENDOR_ROUTE`, `IG_VENDOR_ROUTE`, `TT_VENDOR_ROUTE`, `LI_VENDOR_ROUTE`, `TG_VENDOR_ROUTE`, `TG_POSTS_ACTOR`), off by default.
- Private individuals are never profiled, listed or backfilled: every author is a keyed reference (`author_ref`). Public accounts as defined in ADR-0010 (registered sources, organisations, pages, channels and media, and verified or widely followed accounts, where the platform's terms allow) may be listed and ranked.
- Every data output (a message that carries or derives from a platform fetch) carries provenance (route, vendor, service, fetched_at) and `retention_class`; job and control messages carry `producer` (ADR-0003).
- IMPORTANT: contracts are frozen. Never edit `packages/contracts`, `supabase/migrations` or `clickhouse/migrations` (a hook blocks it). If you need a change, write `docs/proposals/<session>-<topic>.md` from `build-plan/templates/PROPOSAL.md` and stop.

## Commands

- `make up` / `make down`: local stack (Redpanda, Supabase, ClickHouse, SeaweedFS)
- `make check`: lint, types and tests for the packages that differ from main (`scripts/check-changed.sh`)
- `make test SERVICE=<name>` (pre-approved; runs the service's unit and acceptance tests, TypeScript or Python)
- `pnpm --filter <service> test` and `uv run pytest` work too, but ask for approval each time
- `make e2e GATE=G1`: the end-to-end suite of a gate
- `pnpm new:service <name>`: scaffold a service from `services/_template` (`--lang python`: from `services/_template-py`)
- `make bootstrap` installs the pinned toolchain and dependencies; `make doctor` checks them against the pins
- `make smoke`: a round trip through every stack service; `make ps`, `make logs SERVICE=<name>`
- `make ns-clean`: remove this worktree's test topics, schemas, databases and bucket (`TEST_NAMESPACE`, from `scripts/test-namespace.sh`)
- `make migrate`: apply the migrations to the local stack; `make fmt`: Prettier and ruff format; `make policy`: the pull request checks, locally

## Layout

- `services/<name>/`: one per PRD (TypeScript unless the PRD says Python)
- `packages/contracts`, `packages/listening-sdk`, `packages/text`, `py/listening_sdk`
- `supabase/migrations`, `clickhouse/migrations`
- `fixtures/<platform>/`: recorded, scrubbed responses from probe sessions
- `tools/probes/<platform>/`: the only code allowed to call real platforms
- `compose.yaml`, `stack/` (image pins in `stack/versions.env`), `supabase/config.toml`: the local stack
- `tools/repo-checks` (tests of the toolchain), `tools/new-service`, `tools/gates/` (E2), `tests/e2e/<gate>/` (E1), `infra/` (I1)
- `docs/`: prds, decisions (ADRs), contracts, plans, handoffs, reviews, probes, proposals, issues, gates, patterns
- `build-plan/`: session briefs, gates, templates

## How every session works

- Start from the session brief `build-plan/sessions/<ID>-*.md` and stay inside its scope: one service per session.
- Read the PRD in full, then only the CONVENTIONS sections and ADRs the brief lists, and the handoff notes of the sessions in its "Needs first". Do not read other services' code unless a handoff points to it.
- Acceptance tests from PRD section 13, as amended by the ADRs that apply (ADR-0001), first, then code. Show test output; never claim a result you did not run.
- Use `listening-sdk` for jobs, retries, DLQ, cursors, quota, canary, logging and metrics. Never re-implement them.
- No network in tests: fixtures and the fake-platform harness only.
- Replaying a job or message must change nothing. Cursors advance only after the producer acknowledges.
- Errors: 429 and vendor rate limits back off 30 s to 15 min with jitter. 401 and 403 are classified by reason: a quota one goes to quota-governor and waits, an item-scoped one ends that item only, and an authorisation one marks the credential revoked or the source blocked and stops the batch; a blocked source falls back to its vendor route automatically where that route's flag is on, never for a government-watched green source, with an n8n notice to ops (ADR-0021). Route-wide states come only from the canary. After 5 attempts the job goes to `dlq.<service>`.
- When the PRD and an ADR disagree, the ADR wins (ADR-0001): follow it and name it in the plan. When the PRD, CONVENTIONS or a handoff disagree in a way no ADR settles, or the PRD is silent: ask me with AskUserQuestion. Do not guess. Record the answer in the plan and the handoff.
- If a dependency does not behave as its handoff says: write a failing test, record it in `docs/issues/`, and stop.
- Never print, log or commit secrets. Do not read `.env` files; code reads credentials from the environment at run time.
- Finish with `make check` output, `docs/handoffs/<ID>.md` from `build-plan/templates/HANDOFF.md`, and `/code-review`.

## Code

- TypeScript strict, ES modules; no `any` without a comment saying why. Contract types come from `packages/contracts` only; never redeclare one.
- Python version pinned in `.python-version`; typed; ruff-clean; Pydantic models generated from the contracts.
- Tests: Vitest and pytest. Test names state the behaviour, for example `emits a deletion when a comment disappears from a complete sweep`.
- Logs are structured JSON with `job_id`, `source_id`, `route`, `vendor`; metric names are the ones in the PRD's section 10, less any an ADR drops or renames (ADR-0001).

## When compacting

Keep the session ID and brief path, the plan path, the files changed so far, failing tests with the commands that run them, and any open questions for me.
