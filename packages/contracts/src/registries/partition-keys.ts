// One declared partition key per topic and per queue (ADR-0004), read from
// registries/partition-keys.json. The SDK producer sets the Kafka key from this record, never the
// caller; partitionKey() returns it for a message.
import { z } from "zod";
import { ContractError } from "../errors.ts";
import { loadRegistry } from "./load.ts";
import { getPath } from "./paths.ts";
import { registrySchemaId } from "./producers.ts";

const Fields = z.object({ fields: z.array(z.string()).min(1), from: z.string() });
const PartitionKeysFile = z.object({
  topics: z.record(z.string(), Fields),
  jobs: z.object({
    default: Fields,
    rules: z.array(
      Fields.extend({
        queues: z.union([z.literal("*"), z.array(z.string())]),
        kinds: z.union([z.literal("*"), z.array(z.string())]),
      }),
    ),
  }),
});

const file = PartitionKeysFile.parse(loadRegistry("partition-keys.json"));

/** The key fields of a topic, tried in order; null for a schema id the record does not know. */
export function topicKeyFields(schemaId: string): string[] | null {
  const entry = file.topics[registrySchemaId(schemaId)];
  return entry ? [...entry.fields] : null;
}

/** The key fields of a job of `kind` on `queue`: the first matching rule, else the default. */
export function jobKeyFields(queue: string, kind: string): string[] {
  const rule = file.jobs.rules.find(
    (r) =>
      (r.queues === "*" || r.queues.includes(queue)) && (r.kinds === "*" || r.kinds.includes(kind)),
  );
  return [...(rule ?? file.jobs.default).fields];
}

function firstKey(message: unknown, fields: readonly string[], what: string): string {
  for (const field of fields) {
    const value = getPath(message, field);
    if (value === undefined || value === null) continue;
    if (typeof value !== "string" || value === "")
      throw new ContractError("bad_partition_key", `${what}: ${field}`);
    return value;
  }
  throw new ContractError("no_partition_key", `${what} carries none of ${fields.join(", ")}`);
}

/**
 * The Kafka key of a message: by its schema id, and for a job (`job/v1`) by the queue it goes to.
 * A jobs.completed report takes the key of the job it reports, found by its own `queue` and `kind`.
 */
export function partitionKey(
  schemaId: string,
  message: unknown,
  options: { queue?: string } = {},
): string {
  if (schemaId === "job/v1") {
    if (options.queue === undefined)
      throw new ContractError("no_queue", "a job's key depends on its queue");
    const kind = getPath(message, "kind");
    if (typeof kind !== "string")
      throw new ContractError("no_partition_key", "a job without a kind");
    return firstKey(message, jobKeyFields(options.queue, kind), `${options.queue} ${kind}`);
  }
  if (schemaId === "jobs.completed/v1") {
    const queue = getPath(message, "queue");
    const kind = getPath(message, "kind");
    if (typeof queue !== "string" || typeof kind !== "string") {
      throw new ContractError("no_partition_key", "a completion report without its queue and kind");
    }
    return firstKey(message, jobKeyFields(queue, kind), `jobs.completed for ${queue} ${kind}`);
  }
  const fields = topicKeyFields(schemaId);
  if (fields === null) throw new ContractError("unknown_schema", schemaId);
  return firstKey(message, fields, schemaId);
}
