# service-template

Python service created with `pnpm new:service service-template --lang python` from
`services/_template-py`. Fill it in from its PRD in `docs/prds/` and the session brief in
`build-plan/sessions/`. Python is for the services CONVENTIONS names: the analysis workers, the
news extractor, and lang-dialect-id if D2 keeps it in Python.

## Layout

| Path                               | What goes there                                                               |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| `src/service_template/handler.py`  | The job handler (adapter in, mapped outputs out); safe to replay              |
| `src/service_template/config.py`   | Configuration read once from the environment; secrets come from the vault     |
| `src/service_template/log.py`      | JSON log lines with `job_id`, `source_id`, `route`, `vendor`                  |
| `src/service_template/__main__.py` | Entry point: health endpoints (`/healthz`, `/readyz`) and shutdown on SIGTERM |
| `tests/unit/`                      | Unit tests (`make check` runs them)                                           |
| `tests/acceptance/`                | The PRD section 13 acceptance tests (`make test SERVICE=service-template`)    |

Until F6 lands, the logger, the config and the health server are placeholders; F6 replaces them
with `py/listening_sdk`, added as a path dependency in `[tool.uv.sources]`. Message models are the
Pydantic models generated from `packages/contracts`; never hand-write one.

## Commands

```bash
make test SERVICE=service-template   # unit and acceptance suites
make check                           # ruff, ruff format, pyright strict and unit tests
uv run python -m service_template    # run it (from this directory)
docker build -f services/service-template/Dockerfile -t service-template .
```

Dependencies go through uv with the lock file committed (`uv add <name>`, then a row in
`docs/dependencies.md`). The interpreter is pinned in the root `.python-version`.

## Configuration

| Variable    | Default | Meaning                            |
| ----------- | ------- | ---------------------------------- |
| `PORT`      | `8080`  | Port of the health endpoints       |
| `LOG_LEVEL` | `info`  | `debug`, `info`, `warn` or `error` |
