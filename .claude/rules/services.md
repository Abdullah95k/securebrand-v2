---
paths:
  - "services/**/*.ts"
  - "packages/listening-sdk/**"
---

# Service code

- Layout and patterns come from `docs/patterns/ADAPTER-PATTERN.md`: `src/` with the job handler, the adapter and the mapping; `test/unit`, `test/acceptance`; fixtures referenced from `fixtures/<platform>/`.
- Every external call goes through the SDK's HTTP adapter base, which applies the error policy, the quota client and the canary hook. No direct Kafka or HTTP clients in a service.
- Configuration is read once through the service's config schema; secrets come from the vault through the SDK, never from files in the repo.
- Rotation: `next_poll_at` is set from the start of the last poll; jobs are ordered by `next_poll_at` then tier; most stale first when behind. Comment, reply and metrics jobs come only from comment-decay-scheduler; backfill jobs only from backfill-orchestrator.
- A job is safe to replay. Write idempotently, keyed as CONVENTIONS says; advance cursors only after the producer acknowledges.
- Metric and alert names are exactly those in the PRD's section 10; logs carry `job_id`, `source_id`, `route`, `vendor`.
