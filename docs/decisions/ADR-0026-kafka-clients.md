# ADR-0026 · Kafka clients

2026-10-07 · decided by: the user, relayed by the orchestrator on 2026-10-07 · status: accepted
Applies to: all, listening-sdk (F4, F6)
Source: D2-Q026 (technical decision; the recommended option, approved) in `docs/decisions/D2-PROPOSALS.md` · ratification: the user's merge of Abdullah95k/securebrand-v2#6 · line references are to CONVENTIONS v1 and the PRDs as they stood before D2's edits

## Context

The build plan proposes `@confluentinc/kafka-javascript` for Node and `confluent-kafka` for Python, both on librdkafka (build plan L55). F1 already uses the Node client in the stack acceptance tests (`docs/handoffs/F1.md` L81) and recorded it in `docs/dependencies.md` (MIT, bundling librdkafka under BSD-2-Clause; Confluent, Inc., US; screen "clear"); its prebuilt binary installs on the pinned Node 24 (`onlyBuiltDependencies` in `pnpm-workspace.yaml`, `docs/handoffs/F1.md` L81). Redpanda speaks the Kafka API, so any Kafka client works. What matters for the contracts is that the Node SDK (F4) and the Python SDK (F6) produce and consume identically: "partitioned by `source_id` so one source is never worked twice at once" (CONVENTIONS L28) holds only if both SDKs put the same key on the same partition, and the cursor rule ("cursors advance only after the batch is acknowledged by Redpanda", CONVENTIONS L71) needs the same acknowledgement and idempotent-producer semantics in both.

Settles: FC-05.

## Options

1. **Both clients on librdkafka, as proposed, with the partitioner set explicitly** (chosen): its rules are under Decision.
2. **Pure-language clients: KafkaJS for Node and aiokafka for Python.** Consequences: no native binary, but two unrelated implementations whose default partitioners differ, so both SDKs must pin one by hand; KafkaJS's maintenance status would have to be checked before relying on it.
3. **`node-rdkafka` for Node with `confluent-kafka` for Python.** Consequences: also librdkafka, but `node-rdkafka` is a separate binding with its own release cadence; F1's tests would move to it.

## Decision

Both SDKs use clients on librdkafka, with the partitioner and the producer settings fixed, so that both languages put a key on the same partition with the same delivery guarantees.

F4 uses `@confluentinc/kafka-javascript`, F6 uses `confluent-kafka`; both SDKs set `partitioner = murmur2_random` (the Java-compatible hash, which Redpanda's own tools and other Kafka clients also use), `enable.idempotence = true` and `acks = all`, and a shared conformance test proves a key lands on the same partition from both languages.

Why: Option 1 is what F1 already proved, keeps one engine under both SDKs and fixes the one setting (the partitioner) that would otherwise break per-source ordering between languages.

## Consequences

One underlying library, so retries, batching and error codes match across languages; the explicit partitioner avoids librdkafka's default (`consistent_random`, a CRC32 hash) disagreeing with any non-librdkafka producer, for example a tool or an n8n flow that writes to a topic. F6 adds `confluent-kafka` (Apache-2.0, Confluent, Inc., US) to `docs/dependencies.md`.

- CONVENTIONS v1.1, event bus: the client per language and the three producer settings.

Sessions that must read this: F4, F6, and every service through them.
