# The repository's commands; `make` lists them. Every recipe is a script in scripts/, so the kit's
# hooks and CI run exactly what a session runs.
SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
MAKEFLAGS += --no-print-directory

.PHONY: help bootstrap doctor up down ps logs smoke migrate check test e2e fmt policy ns-clean new-service

help: ## list the targets
	@awk 'BEGIN { FS = ":.*## " } /^[a-z][a-z0-9-]*:.*## / { printf "  make %-12s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

bootstrap: ## install the pinned toolchain (Node, pnpm, uv, Python) and every dependency
	@scripts/bootstrap.sh

doctor: ## check the toolchain against the pins; names whatever is missing or wrong
	@scripts/doctor.sh

up: ## start the local stack (Redpanda, Supabase, ClickHouse, SeaweedFS) and wait until it answers
	@scripts/stack-up.sh

down: ## stop the local stack and remove its volumes
	@scripts/stack-down.sh

ps: ## the local stack's containers and Supabase's status
	@scripts/stack-ps.sh

logs: ## recent logs of the stack: make logs [SERVICE=redpanda|clickhouse|seaweedfs] [FOLLOW=1]
	@scripts/compose.sh logs --tail=200 $(if $(filter 1,$(FOLLOW)),--follow) $(SERVICE)

smoke: ## one round trip through every service of the running stack
	@scripts/smoke-stack.sh

migrate: ## apply the migrations to the local stack: make migrate [ENGINE=postgres|clickhouse]
	@scripts/migrate.sh $(ENGINE)

check: ## lint, types and unit tests of what differs from main (ACCEPTANCE=1 adds acceptance suites)
	@scripts/check-changed.sh $(if $(filter 1,$(ACCEPTANCE)),--acceptance)

test: ## unit and acceptance suites of one service or package: make test SERVICE=<name>
	@scripts/make-test.sh "$(SERVICE)"

e2e: ## the end-to-end suite of a gate: make e2e GATE=G1
	@scripts/e2e.sh "$(GATE)"

fmt: ## format everything (Prettier, ruff format)
	@scripts/fmt.sh

policy: ## the pull request policy checks: make policy [BASE=<ref>] [PR_LABELS=a,b]
	@BASE="$(BASE)" scripts/policy/run-all.sh

ns-clean: ## remove this checkout's test topics, schema, databases and bucket from the stack
	@scripts/ns-clean.sh

# LANG is also the locale variable, so only a LANG given on the command line counts.
new-service: ## scaffold a service: make new-service NAME=<name> [LANG=python]
	@node tools/new-service/index.mjs "$(NAME)" $(if $(filter command line,$(origin LANG)),--lang $(LANG))
