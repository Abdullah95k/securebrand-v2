---
paths:
  - "services/**/*.ts"
  - "packages/listening-sdk/**"
---

# Service code

- Layout and patterns come from `docs/patterns/ADAPTER-PATTERN.md`: `src/` with the job handler, the adapter and the mapping; `test/unit`, `test/acceptance`; fixtures referenced from `fixtures/<platform>/`.
- Every external call goes through the SDK's HTTP adapter base, which applies the error policy, the quota client and the canary hook. No direct Kafka or HTTP clients in a service.
- Configuration is read once through the service's config schema; secrets come from the vault through the SDK, never from files in the repo.
- Rotation: each rotating service keeps its due time per source in its own `cursors` row (`next_due_at`, `last_started_at`), set from the start of the last run; a source with no row is due at once; jobs are ordered by `next_due_at` then tier, most stale first when behind (ADR-0015, ADR-0041). `sources.last_polled_at` and `next_poll_at` are a summary only the source type's primary poller writes, and no scheduler reads them (ADR-0015, ADR-0049). Comment, reply and metrics jobs come only from comment-decay-scheduler, the X reply steps to day 30 included; backfill and `keyword_history` jobs only from backfill-orchestrator; F2's producer table names every allowed producer (ADR-0012, ADR-0059).
- A job is safe to replay. Write idempotently, keyed as CONVENTIONS says; advance cursors only after the producer acknowledges.
- Metric and alert names are exactly those in the PRD's section 10, less any an ADR drops or renames (ADR-0001); logs carry `job_id`, `source_id`, `route`, `vendor`.
