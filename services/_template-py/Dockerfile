# One image per service. Build from the repository root:
#   docker build -f services/service-template/Dockerfile -t service-template .
# Base images come from anonymous registries; the tags follow .python-version and uv.toml.
FROM ghcr.io/astral-sh/uv:0.12.23 AS uv

FROM public.ecr.aws/docker/library/python:3.13.16-slim-bookworm AS build
COPY --from=uv /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY services/service-template/pyproject.toml services/service-template/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY services/service-template/ ./
RUN uv sync --locked --no-dev --no-editable

FROM public.ecr.aws/docker/library/python:3.13.16-slim-bookworm
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
USER 65534
EXPOSE 8080
CMD ["python", "-m", "service_template"]
