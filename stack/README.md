# Local stack

One stack per machine, shared by every worktree: Redpanda, ClickHouse and SeaweedFS (local S3)
from `compose.yaml`, and Supabase (Postgres, auth, REST, the Kong gateway) from the Supabase CLI
with `supabase/config.toml`.

```bash
make up                        # start it and wait until every service answers; a second run changes nothing
eval "$(scripts/stack-env.sh)" # the connection variables below, in your shell
make smoke                     # one round trip through every service
make ps                        # containers and Supabase's status
make logs SERVICE=redpanda     # recent logs (FOLLOW=1 to follow)
make ns-clean                  # remove this worktree's test topics, schema, databases and bucket
make down                      # stop it and remove its volumes; the next make up starts empty
```

`SUPABASE_FULL=1 make up` starts every Supabase service (Studio, Realtime, Storage and the rest);
by default only db, kong, auth and rest run. After `make down`, it starts the full set.

## Ports and variables

Everything listens on 127.0.0.1 only. `scripts/stack-env.sh` prints these variables; tests and
services read only them.

| Service                     | Port                             | Variables                                                                                                                       |
| --------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Redpanda, Kafka API         | 19092 (internal `redpanda:9092`) | `KAFKA_BROKERS=127.0.0.1:19092`                                                                                                 |
| Redpanda, schema registry   | 18081                            | `SCHEMA_REGISTRY_URL`                                                                                                           |
| Redpanda, HTTP proxy        | 18082                            | `KAFKA_HTTP_PROXY_URL`                                                                                                          |
| Redpanda, admin API         | 9644                             | `REDPANDA_ADMIN_URL`                                                                                                            |
| ClickHouse, HTTP            | 8123                             | `CLICKHOUSE_URL`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`                                                                      |
| ClickHouse, native          | 9000                             | `CLICKHOUSE_NATIVE_ADDR`                                                                                                        |
| SeaweedFS, S3               | 8333                             | `S3_ENDPOINT`, `S3_REGION`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET=listening-local`, `S3_FORCE_PATH_STYLE=true` |
| SeaweedFS, master and filer | 9333, 8888                       | (administration only)                                                                                                           |
| Supabase API gateway        | 54321                            | `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`                                                                |
| Supabase Postgres           | 54322                            | `SUPABASE_DB_URL`                                                                                                               |

The ClickHouse and S3 credentials are fixed development values in `stack/local.env` (matching
`clickhouse/users.d/listening.xml` and `seaweedfs/s3.json`); they work on localhost only and guard
nothing. Supabase's URL and keys are read live from `supabase status` and never written to a file.
`make up` creates the `listening-local` bucket.

## Test namespaces

Parallel worktrees share this stack, so every test names what it creates after `TEST_NAMESPACE`
(`scripts/test-namespace.sh`: the worktree name, else the branch, else `local`; `ci_<run id>` in
CI): Kafka topics `<namespace>.*` (`TEST_TOPIC_PREFIX`), the Postgres schema and database
`test_<namespace>` (`TEST_PG_SCHEMA`, `TEST_PG_DATABASE`), the ClickHouse database
`test_<namespace>` (`TEST_CH_DATABASE`) and the S3 bucket `test-<namespace>` (`TEST_S3_BUCKET`).
`make test`, `make check ACCEPTANCE=1` and `make e2e` set these variables and the connection
variables above; `make ns-clean` removes what they name. SeaweedFS has 200 volume slots and every
bucket takes seven, so about 25 test buckets fit at once besides `listening-local`; delete a bucket
when its tests are done (`make ns-clean`, or the S3 DeleteBucket call), which frees its slots.
The SDK (F4, F6) applies the topic prefix in test mode.

## Images

`versions.env` pins every image by exact tag. Each image is pulled from an upstream that serves
anonymous pulls when its publisher offers an official image there (ClickHouse's Docker Official
Image on ECR Public, SeaweedFS's own GHCR image, Supabase's images on ECR Public); Redpanda, which
publishes only on Docker Hub, is copied to this repository's GHCR packages by
`.github/workflows/mirror-images.yml` (on demand, and on every push that changes `versions.env`).
Docker Hub limits anonymous pulls per address and answers 429 on shared addresses such as the
cloud sessions'. `IMAGE_REGISTRY=upstream make up` pulls every image from its publisher's registry
instead. `scripts/compose.sh <command>` runs docker compose with the pins set.

To change a pin, edit `versions.env` (the tag, and for a new image its `_REPO` and `_UPSTREAM`), add
or update its row in `docs/dependencies.md`, and push: the mirror workflow copies a new Redpanda tag.
A tag already in the mirror is compared with its upstream by manifest digest on every run. When they
differ, the run fails and names both digests; only a run on main, where `versions.env` is reviewed,
replaces the mirrored tag.

## Fallbacks

- S3: MinIO's community edition is no longer published. If SeaweedFS ever misbehaves, Garage
  (Deuxfleurs, France, AGPL-3.0) is the fallback: it speaks the same S3 API, so only `compose.yaml`
  and `stack-env.sh` change.
- Images: if the GHCR mirror is private or missing a tag, `docker login ghcr.io` with a token that
  can read packages, or use `IMAGE_REGISTRY=upstream`.
