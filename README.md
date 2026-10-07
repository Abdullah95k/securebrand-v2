# securebrand-v2

Social-media and news listening for the Iraqi market: one service per PRD in `docs/prds/`, built one
session at a time from `build-plan/` (see `CLAUDE.md` and `KIT-README.md`). This page is the
toolchain: how to set it up, run the local stack and work on a service.

## A service from scratch, step by step

```bash
make bootstrap                 # Node 24.21.0 (nvm), pnpm 10, uv 0.12, Python 3.13, every dependency
make doctor                    # check the toolchain against the pins
make up                        # Redpanda, Supabase, ClickHouse and SeaweedFS; waits until they answer
pnpm new:service demo          # services/demo from services/_template (add --lang python for Python)
make test SERVICE=demo         # its unit and acceptance suites
make check                     # lint, types and unit tests of everything that differs from main
make down                      # stop the stack and remove its volumes
```

`pnpm new:service <name>` takes a name that follows CONVENTIONS: `<source>-<action>` for a
per-source service (`fb-page-feed-poller`, `news-article-extractor`) or `<action>` for a shared one
(`normalize-item`). The generated service passes `make check` without edits; its README says what to
fill in.

## Commands

| Command                                             | What it does                                                                                                                                                                         |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `make bootstrap` / `make doctor`                    | install the pinned toolchain and dependencies / check them                                                                                                                           |
| `make up` / `make down`                             | start the local stack (`IMAGE_REGISTRY=upstream`, `SUPABASE_FULL=1`) / stop it and remove its volumes                                                                                |
| `make ps`, `make logs SERVICE=<name>`, `make smoke` | the stack's containers, recent logs, a round trip through every service                                                                                                              |
| `make check`                                        | lint, typecheck and unit tests of the packages that differ from main and their dependants, TypeScript and Python, then the fixture check (`ACCEPTANCE=1` adds the acceptance suites) |
| `make test SERVICE=<name>`                          | the unit and acceptance suites of one service or package                                                                                                                             |
| `make e2e GATE=G1`                                  | the end-to-end suite of a gate (`tests/e2e/G1`, built by E1)                                                                                                                         |
| `make migrate`                                      | apply the migrations to the local stack (F3 and F8 fill it in)                                                                                                                       |
| `make ns-clean`                                     | remove this worktree's test topics, schema, databases and bucket                                                                                                                     |
| `make fmt` / `make policy`                          | Prettier and ruff format / the pull request checks, locally                                                                                                                          |
| `pnpm new:service <name> [--lang python]`           | scaffold a service                                                                                                                                                                   |

## Toolchain

| Tool                                                          | Pin                          | Where                                                     |
| ------------------------------------------------------------- | ---------------------------- | --------------------------------------------------------- |
| Node.js                                                       | 24.21.0 (LTS)                | `.node-version`; `engines` in `package.json`              |
| pnpm                                                          | 10.34.6                      | `packageManager` in `package.json` (pnpm switches itself) |
| TypeScript, Vitest, ESLint, Prettier, Turborepo, Supabase CLI | exact versions               | the `catalog:` in `pnpm-workspace.yaml`                   |
| Python                                                        | 3.13.16                      | `.python-version`                                         |
| uv                                                            | 0.12.23 or newer within 0.12 | `uv.toml`, repeated in each project's `[tool.uv]`         |
| ruff, pytest, pyright                                         | exact versions               | each Python project's `dev` dependency group              |
| Redpanda, ClickHouse, SeaweedFS                               | exact tags                   | `stack/versions.env`                                      |

TypeScript is strict ES modules (`tsconfig.base.json`), linted with typescript-eslint's type-checked
rules (`eslint.config.js`). Python projects are independent uv projects with their own lock file,
checked with ruff, pyright in strict mode and pytest; they share `ruff.toml`. Packages are named
after their directory, so `pnpm --filter <service>` works.

## Layout

| Path                       | What lives there                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------- |
| `services/<name>/`         | one service per PRD; `services/_template` and `services/_template-py` are the templates           |
| `packages/`, `py/`         | shared packages: contracts (F2), listening-sdk (F4), text (F7); the Python SDK (F6)               |
| `supabase/`, `clickhouse/` | migrations (F3, F8); `supabase/config.toml` configures the local Supabase                         |
| `compose.yaml`, `stack/`   | the local stack; ports, variables and images in `stack/README.md`                                 |
| `scripts/`                 | everything the make targets, the kit's hooks and CI run                                           |
| `tools/`                   | `repo-checks` (tests of this toolchain), `new-service`, `probes/` (probe sessions), `gates/` (E2) |
| `tests/e2e/`               | end-to-end suites per gate (E1)                                                                   |
| `fixtures/`                | scrubbed recorded responses (rules in `fixtures/README.md`)                                       |
| `docs/`                    | PRDs, plans, handoffs, reviews, decisions, contracts, gates, patterns, probes, proposals, issues  |
| `infra/`                   | infrastructure (I1, I2)                                                                           |

## CI

`.github/workflows/ci.yml` runs on every pull request and every push to main: `check` (the pinned
toolchain, `make up`, `make check ACCEPTANCE=1`, `make smoke`; on main, compared with the commit
before the push) and `template-smoke` (`pnpm new:service demo && make check`, and the Python twin).
`policy.yml` checks that contract paths change only under the `contract-change` label, that a lane
changing code has its handoff and a closed review, that every new runtime dependency has its row in
`docs/dependencies.md`, and that fixtures are scrubbed; it runs the base branch's copy of the
scripts, so a pull request cannot loosen its own checks. `mirror-images.yml` copies to GHCR the
stack images that have no anonymous upstream. Every action is pinned to a commit; Dependabot
proposes minor and patch updates weekly.
