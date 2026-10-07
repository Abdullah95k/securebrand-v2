# service-template

TypeScript service created with `pnpm new:service service-template` from `services/_template`.
Fill it in from its PRD in `docs/prds/` and the session brief in `build-plan/sessions/`.

## Layout

| Path               | What goes there                                                                                                             |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `src/handler.ts`   | The job handler: one job in, its outputs out; safe to replay                                                                |
| `src/adapter.ts`   | The only code that talks to the outside, through listening-sdk's HTTP adapter base (see `docs/patterns/ADAPTER-PATTERN.md`) |
| `src/mapping.ts`   | Pure mapping from adapter records to contract outputs, with provenance and `retention_class`                                |
| `src/config.ts`    | Configuration read once from the environment; secrets come from the vault                                                   |
| `src/log.ts`       | JSON log lines with `job_id`, `source_id`, `route`, `vendor`                                                                |
| `src/index.ts`     | Entry point: health endpoints (`/healthz`, `/readyz`) and shutdown on SIGTERM                                               |
| `test/unit/`       | Unit tests (`make check` runs them)                                                                                         |
| `test/acceptance/` | The PRD section 13 acceptance tests (`make test SERVICE=service-template`)                                                  |

Until F4 lands, `src/log.ts`, `src/config.ts` and the health server are placeholders; F4 replaces them
with listening-sdk and wires the job wrapper, retries, DLQ, cursors, metrics and health.

## Commands

```bash
make test SERVICE=service-template      # unit and acceptance suites
make check                              # lint, types and unit tests of everything that changed
pnpm --filter service-template build    # compile to dist/
docker build -f services/service-template/Dockerfile -t service-template .
```

## Configuration

| Variable    | Default | Meaning                            |
| ----------- | ------- | ---------------------------------- |
| `PORT`      | `8080`  | Port of the health endpoints       |
| `LOG_LEVEL` | `info`  | `debug`, `info`, `warn` or `error` |
