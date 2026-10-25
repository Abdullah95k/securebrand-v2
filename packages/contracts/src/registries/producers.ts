// Who may write what: the producer table of the job queues (ADR-0012), the writers of every topic
// (CONVENTIONS v1.1 L25 to L40) and the producers allowed per registry.decisions type (ADR-0013),
// all read from registries/*.json, which the Python package reads too.
import { z } from "zod";
import { ContractError } from "../errors.ts";
import { PATTERNS } from "../primitives.ts";
import { loadRegistry } from "./load.ts";
import { isKnownService, namesService } from "./services.ts";

const ProducersFile = z.object({
  rows: z.array(
    z.object({
      queues: z.array(z.string()),
      kinds: z.array(z.string()),
      producers: z.array(z.string()),
      from: z.string(),
    }),
  ),
  required_fields: z.array(
    z.object({
      queues: z.array(z.string()),
      kinds: z.array(z.string()),
      producers: z.array(z.string()).optional(),
      fields: z.array(z.string()),
      from: z.string(),
    }),
  ),
});
const TopicWritersFile = z.object({
  topics: z.record(z.string(), z.array(z.string())),
  raw_items_kinds: z.record(z.string(), z.array(z.string())),
  conditions: z.array(
    z.object({
      schema: z.string(),
      writer: z.string(),
      field: z.string(),
      equals: z.union([z.string(), z.boolean()]),
      from: z.string(),
    }),
  ),
});
const DecisionFile = z.object({
  rows: z.array(
    z.object({
      decisions: z.array(z.string()),
      subject: z.enum(["candidate_key", "author_ref", "source_id", "platform", "keyword_id"]),
      producers: z.array(z.string()),
      reasons: z.array(z.string().nullable()).optional(),
      healths: z.array(z.string()).optional(),
      provenance: z.enum(["required", "refused", "optional"]),
      from: z.string(),
    }),
  ),
});

const producersFile = ProducersFile.parse(loadRegistry("producers.json"));
const writersFile = TopicWritersFile.parse(loadRegistry("topic-writers.json"));
const decisionFile = DecisionFile.parse(loadRegistry("decision-producers.json"));

export type RequiredFieldRow = z.infer<typeof ProducersFile>["required_fields"][number];
export type DecisionRow = z.infer<typeof DecisionFile>["rows"][number];
export type DecisionSubject = DecisionRow["subject"];
export interface DecisionQuery {
  decision: string;
  subject: DecisionSubject;
  reason: string | null;
  health?: string | undefined;
}
export interface WriterCondition {
  field: string;
  equals: string | boolean;
}

/** One expanded row of the producer table: a queue, a kind and the services allowed to emit it. */
export interface ProducerRow {
  queue: string;
  kind: string;
  producers: string[];
  from: string;
}

/** `jobs.<service>` and `jobs.<service>.priority` belong to `<service>`. */
export function queueService(queue: string): string {
  if (!PATTERNS.queue.test(queue)) throw new ContractError("bad_queue", queue);
  return queue.slice("jobs.".length).replace(/\.priority$/, "");
}

const resolveQueue = (producers: readonly string[], queue: string): string[] =>
  producers.map((p) => (p === "@queue" ? queueService(queue) : p));

const expanded: ProducerRow[] = producersFile.rows.flatMap((row) =>
  row.queues.flatMap((queue) =>
    row.kinds.map((kind) => ({
      queue,
      kind,
      producers: resolveQueue(row.producers, queue),
      from: row.from,
    })),
  ),
);

export function producerRows(): ProducerRow[] {
  return expanded.map((r) => ({ ...r, producers: [...r.producers] }));
}

export function requiredFieldRows(): RequiredFieldRow[] {
  return producersFile.required_fields.map((r) => ({ ...r }));
}

/** The services allowed to emit `kind` on `queue`; none for a (queue, kind) the table does not list. */
export function allowedProducers(queue: string, kind: string): string[] {
  const out: string[] = [];
  for (const row of expanded) {
    if (row.queue !== queue || row.kind !== kind) continue;
    for (const p of row.producers) if (!out.includes(p)) out.push(p);
  }
  return out;
}

export function isAllowedProducer(queue: string, kind: string, service: string): boolean {
  return allowedProducers(queue, kind).includes(service);
}

/** The kind fields a (queue, kind) row requires of a job from `service` (dotted for nested fields). */
export function requiredJobFields(queue: string, kind: string, service: string): string[] {
  const out: string[] = [];
  for (const row of producersFile.required_fields) {
    if (!row.queues.includes(queue) || !row.kinds.includes(kind)) continue;
    if (row.producers && !resolveQueue(row.producers, queue).includes(service)) continue;
    for (const f of row.fields) if (!out.includes(f)) out.push(f);
  }
  return out;
}

/** The writers of every topic, keyed by schema id (registry.decisions: see the decision rows). */
export function topicWriters(): Record<string, string[]> {
  return Object.fromEntries(Object.entries(writersFile.topics).map(([k, v]) => [k, [...v]]));
}

/** The record kinds a raw.items writer may write, or null for a service that writes none. */
export function rawItemsKinds(service: string): string[] | null {
  const kinds = writersFile.raw_items_kinds[service];
  return kinds ? [...kinds] : null;
}

/** The service whose dead-letter topic a `dlq.<service>/v1` schema id names, or null. */
const dlqService = (schemaId: string): string | null =>
  PATTERNS.dlqSchema.test(schemaId) ? schemaId.slice("dlq.".length, -"/v1".length) : null;

/** The schema id under which the registries file a concrete id (`dlq.<service>/v1` is one entry). */
export function registrySchemaId(schemaId: string): string {
  return dlqService(schemaId) === null ? schemaId : "dlq.<service>/v1";
}

export function decisionRows(): DecisionRow[] {
  return decisionFile.rows.map((r) => ({ ...r }));
}

const rowMatches = (row: DecisionRow, q: DecisionQuery, service: string): boolean =>
  row.decisions.includes(q.decision) &&
  row.subject === q.subject &&
  namesService(row.producers, service) &&
  (row.reasons === undefined || row.reasons.includes(q.reason)) &&
  (row.healths === undefined || (q.health !== undefined && row.healths.includes(q.health)));

/** The decision row that allows `service` to send this decision, or null when none does. */
export function decisionRow(q: DecisionQuery, service: string): DecisionRow | null {
  return decisionFile.rows.find((row) => rowMatches(row, q, service)) ?? null;
}

export function isAllowedDecisionProducer(q: DecisionQuery, service: string): boolean {
  return decisionRow(q, service) !== null;
}

/**
 * Whether `service` may write `schemaId`; a raw.items writer only its record kinds (`detail.kind`),
 * a jobs.completed report only the service that ran the job (`detail.queue`).
 */
export function isAllowedTopicWriter(
  schemaId: string,
  service: string,
  detail: { kind?: string; queue?: string } = {},
): boolean {
  if (!isKnownService(service)) return false;
  const dlq = dlqService(schemaId);
  if (dlq !== null) return dlq === service;
  if (schemaId === "registry.decisions/v1")
    return decisionFile.rows.some((r) => namesService(r.producers, service));
  if (schemaId === "jobs.completed/v1")
    return detail.queue !== undefined && queueService(detail.queue) === service;
  const writers = writersFile.topics[schemaId];
  if (!writers?.includes(service)) return false;
  if (schemaId === "raw.items/v1" && detail.kind !== undefined) {
    return (writersFile.raw_items_kinds[service] ?? []).includes(detail.kind);
  }
  return true;
}

/** The field values a writer's messages on `schemaId` must carry (ADR-0032, ADR-0012 L34). */
export function writerConditions(schemaId: string, service: string): WriterCondition[] {
  return writersFile.conditions
    .filter((c) => c.schema === schemaId && c.writer === service)
    .map((c) => ({ field: c.field, equals: c.equals }));
}
