# Runtime dependencies

Every runtime dependency (library, model, container image, hosted service) gets a row in the pull request that introduces it. The reviewer checks the owner and country against the vendor screen in the first section of `docs/prds/_shared/CONVENTIONS.md`: no Israeli-owned or Israel-affiliated vendor anywhere in the stack, and flagged vendors only with your written approval.

CI enforces it (`scripts/policy/check-dependencies.sh`): a new npm `dependencies` entry, a new PyPI `[project]` dependency or a new container image (compose files, Dockerfiles, `stack/versions.env`) fails the policy check until this table has a row whose first cell is its exact name (an image by repository, without the tag). Development tools and hosted services are listed too, so the screen covers the whole stack. Append new rows at the end of the table; this file is never reformatted (aligned columns would rewrite every row and conflict with the other lanes).

Screened out and not used: Snyk, Trivy (Aqua Security), Wiz, JFrog, Checkmarx and Renovate (Mend.io) are Israeli-founded or Israel-based; Cloudflare is flagged. For the dependency and image scans of G4, use Grype or Syft (Anchore, US) or OSV-Scanner (Google, US).

| Name | Kind | Version | Licence | Owner or maintainer | Country | Used by | Added in session | Screen result |
|---|---|---|---|---|---|---|---|---|
| `ghcr.io/abdullah95k/securebrand-v2/redpanda` | image (this repository's GHCR mirror of Redpanda) | v26.1.18 | BSL-1.1 (Redpanda Community Edition) | Redpanda Data, Inc.; copied by `.github/workflows/mirror-images.yml` | US | local stack (`compose.yaml`), CI | F1 | clear (Redpanda is cleared in CONVENTIONS) |
| `docker.redpanda.com/redpandadata/redpanda` | image (upstream of the mirror; `IMAGE_REGISTRY=upstream`) | v26.1.18 | BSL-1.1 (Redpanda Community Edition) | Redpanda Data, Inc. | US | `stack/versions.env` | F1 | clear |
| `public.ecr.aws/docker/library/clickhouse` | image (ClickHouse's Docker Official Image on ECR Public) | 26.3.38.2 | Apache-2.0 | ClickHouse, Inc. (served by Amazon ECR Public) | US | local stack (`compose.yaml`), CI | F1 | flagged vendor (ClickHouse Inc.); the open-source server, self-hosted, which CONVENTIONS allows |
| `docker.io/clickhouse/clickhouse-server` | image (upstream; `IMAGE_REGISTRY=upstream`) | 26.3.38.2 | Apache-2.0 | ClickHouse, Inc. | US | `stack/versions.env` | F1 | flagged vendor; open-source server, self-hosted, allowed by CONVENTIONS |
| `ghcr.io/chrislusf/seaweedfs` | image (local S3) | 4.48 | Apache-2.0 | Chris Lu (SeaweedFS) | US | local stack (`compose.yaml`), CI | F1 | clear |
| `docker.io/chrislusf/seaweedfs` | image (upstream; `IMAGE_REGISTRY=upstream`) | 4.48 | Apache-2.0 | Chris Lu (SeaweedFS) | US | `stack/versions.env` | F1 | clear |
| `public.ecr.aws/docker/library/node` | image (base of TypeScript service images) | 24.21.0-bookworm-slim | MIT (Node.js; Debian packages under their own licences) | OpenJS Foundation; Docker Official Images | US | `services/_template/Dockerfile` | F1 | clear |
| `public.ecr.aws/docker/library/python` | image (base of Python service images) | 3.13.16-slim-bookworm | PSF-2.0 (Python; Debian packages under their own licences) | Python Software Foundation; Docker Official Images | US | `services/_template-py/Dockerfile` | F1 | clear |
| `ghcr.io/astral-sh/uv` | image (build stage of Python service images) | 0.12.23 | MIT OR Apache-2.0 | Astral Software Inc. | US | `services/_template-py/Dockerfile` | F1 | clear |
| `public.ecr.aws/supabase/postgres` | image (Supabase local; pinned by the Supabase CLI) | 17.11.0.004 | PostgreSQL License; Supabase additions Apache-2.0 | Supabase, Inc. | US (founded in Singapore) | local stack (`supabase start`) | F1 | clear (Supabase is cleared in CONVENTIONS) |
| `public.ecr.aws/supabase/gotrue` | image (Supabase local auth) | v2.197.0 | MIT | Supabase, Inc. | US (founded in Singapore) | local stack (`supabase start`) | F1 | clear |
| `public.ecr.aws/supabase/postgrest` | image (Supabase local REST) | v16.4 | MIT | PostgREST project, published by Supabase | International | local stack (`supabase start`) | F1 | clear |
| `public.ecr.aws/supabase/kong` | image (Supabase local API gateway) | 2.8.1 | Apache-2.0 | Kong Inc., published by Supabase | US | local stack (`supabase start`) | F1 | clear |
| Supabase local, other images | images (Studio, Realtime, Storage, imgproxy, Mailpit, postgres-meta, Edge Runtime, Logflare, Vector, Supavisor; `SUPABASE_FULL=1` only) | pinned by Supabase CLI 2.120.0 | MIT or Apache-2.0 | Supabase, Inc. and the projects it packages | US (founded in Singapore) | local stack (`SUPABASE_FULL=1 make up`) | F1 | clear |
| Node.js | runtime and tool | 24.21.0 (`.node-version`) | MIT | OpenJS Foundation | US | toolchain, service images | F1 | clear |
| pnpm | tool | 10.34.6 (`packageManager`) | MIT | pnpm maintainers (open source) | International | toolchain | F1 | clear |
| `turbo` (Turborepo) | tool | 2.10.13 | MIT | Vercel Inc. | US | `make check`, CI | F1 | clear |
| `typescript` | tool | 6.0.3 | Apache-2.0 | Microsoft | US | every TypeScript workspace | F1 | clear |
| `@types/node` | tool | 24.19.1 | MIT | DefinitelyTyped | US | every TypeScript workspace | F1 | clear |
| `vitest` | tool | 4.1.11 | MIT | VoidZero Inc. | US | every TypeScript workspace | F1 | clear |
| `eslint`, `@eslint/js` | tool | 9.39.5 | MIT | OpenJS Foundation | US | lint | F1 | clear |
| `typescript-eslint` | tool | 8.71.1 | MIT | typescript-eslint maintainers (open source) | International | lint | F1 | clear |
| `@eslint-community/eslint-plugin-eslint-comments` | tool | 4.8.1 | MIT | ESLint Community (open source) | International | lint | F1 | clear |
| `eslint-config-prettier` | tool | 10.1.8 | MIT | Prettier project (open source) | International | lint | F1 | clear |
| `globals` | tool | 17.13.0 | MIT | Sindre Sorhus | Norway | lint | F1 | clear |
| `prettier` | tool | 3.9.9 | MIT | Prettier project (open source) | International | `make fmt`, the kit's format hook | F1 | clear |
| `supabase` (Supabase CLI) | tool | 2.120.0 | MIT | Supabase, Inc. | US (founded in Singapore) | `make up`, `make down`, `scripts/stack-env.sh` | F1 | clear |
| `@confluentinc/kafka-javascript` | tool (dev dependency of `tools/repo-checks`) | 1.10.1 | MIT (bundles librdkafka, BSD-2-Clause) | Confluent, Inc. | US | stack acceptance tests | F1 | clear |
| `pg`, `@types/pg` | tool (dev dependency of `tools/repo-checks`) | 8.23.1 | MIT | Brian Carlson (node-postgres) | US | stack acceptance tests | F1 | clear |
| `@aws-sdk/client-s3` | tool (dev dependency of `tools/repo-checks`) | 3.1147.0 | Apache-2.0 | Amazon Web Services | US | stack acceptance tests | F1 | clear |
| `yaml` | tool (dev dependency of `tools/repo-checks`) | 2.9.1 | ISC | Eemeli Aro | Finland | workflow and compose tests | F1 | clear |
| Python | runtime and tool | 3.13.16 (`.python-version`) | PSF-2.0 | Python Software Foundation | US | Python services, policy scripts | F1 | clear |
| `uv`, `uv-build` | tool | 0.12.23 (`uv.toml`) | MIT OR Apache-2.0 | Astral Software Inc. | US | Python projects | F1 | clear |
| `ruff` | tool | 0.16.10 | MIT | Astral Software Inc. | US | Python projects (dev group), the kit's format hook | F1 | clear |
| `pytest` | tool | 9.1.1 | MIT | pytest-dev (open source) | International | Python projects (dev group) | F1 | clear |
| `pyright` | tool | 1.1.414 | MIT | Microsoft (PyPI wrapper by Robert Craigie) | US | Python projects (dev group) | F1 | clear |
| Docker Engine and Compose | tool | Engine 27 or newer, Compose 2.30 or newer | Apache-2.0 | Docker, Inc. | US | local stack, service images | F1 | clear |
| GitHub Actions, GitHub Container Registry, Dependabot | hosted service | — | proprietary (service) | GitHub, Inc. (Microsoft) | US | CI, image mirror, dependency updates | F1 | clear |
| `actions/checkout`, `actions/setup-node`, `actions/upload-artifact` | CI action | v7.0.1, v7.0.0, v7.0.1 (pinned by commit) | MIT | GitHub, Inc. | US | `.github/workflows/` | F1 | clear |
| `pnpm/action-setup` | CI action | v6.1.0 (pinned by commit) | MIT | pnpm maintainers | International | `.github/workflows/ci.yml` | F1 | clear |
| `astral-sh/setup-uv` | CI action | v10.2.0 (pinned by commit) | MIT | Astral Software Inc. | US | `.github/workflows/ci.yml` | F1 | clear |
| `docker/login-action`, `docker/setup-buildx-action` | CI action | v4.6.0, v4.4.1 (pinned by commit) | Apache-2.0 | Docker, Inc. | US | `.github/workflows/` | F1 | clear |
| GitHub-hosted runner `ubuntu-24.04` | hosted service | 24.04 | proprietary (service); Ubuntu by Canonical | GitHub, Inc.; Canonical Ltd. | US; UK | CI | F1 | clear |
