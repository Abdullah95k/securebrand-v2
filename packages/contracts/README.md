# contracts

The listening platform's message contracts, for TypeScript (`contracts`) and Python (`listening-contracts`, imported as `listening_contracts`). Version 1.0.0 in both languages. Built by F2; how a contract may change is in [`docs/contracts/VERSIONING.md`](../../docs/contracts/VERSIONING.md).

## What it holds

- **Schemas.** One Zod 4 schema per schema id (19 ids: every topic, `job/v1`, the shared `dlq.<service>/v1`, `n8n.alert/v1` and `n8n.card/v1`; the catalogue is in VERSIONING.md). Each is written once and built in two modes: `producer` refuses unknown fields, `consumer` drops them. `schemas/` holds their JSON Schema export (draft 2020-12), and `python/listening_contracts/models/strict/` and `models/consumer/` the Pydantic v2 models generated from it.
- **`validate()`**, in both languages: the schema, then the cross-field rules JSON Schema cannot carry (a key equals the key helper's output, a producer's declared `context` keys, a job's required fields on its queue, the government rule on client alerts), then, in producer mode, the registry checks (a known service and vendor, the producer table, the topic writers, the decision producers). It returns `{ok: true, value}` or `{ok: false, issues}`, each issue a `path`, a `code` and a `message`. A shape error's `code` and `message` come from Zod or Pydantic and differ between the languages. Its path is the same in both, except under the six plain unions (registry.decisions, poster.profiles, items.analysis, raw.items, n8n.alert `details`, a push job's `body`), where the two path sets may differ in either direction, as `fixtures/contracts/golden/issue-paths.json` records: on a shape error Python lists every failing branch, and on a constant given as the other JSON type TypeScript also lists the other branch's errors. The package's own rules use the same codes and paths in both.
- **Key and id helpers**, with TypeScript and Python twins that reproduce the golden vectors in `fixtures/contracts/golden/` byte for byte: `idempotencyKey` and `parseKey`, the platform id forms (Telegram, LinkedIn URNs, Instagram shortcodes, the id-less comment key), the Instagram id-map rule, `itemId`, `hitId`, `cardId`, `analysisKey`, the deterministic ULIDs, `authorRef` and `matchesAuthorRef`, `contentHash`, `normaliseUrl`, `urlHash`, `urlKey` and the article and web-result keys, `queryKey`, `deletionId`, the candidate keys, `rawRef`, `canonicalJson` (RFC 8785).
- **Registries**, as JSON data in `registries/` that both languages read: the services and vendors, the producer table (`isAllowedProducer`, `requiredJobFields`), the topic writers, the decision producers, the partition keys (`partitionKey`), the visibility of each producer (`visibilityOf`), each producer's `context` keys and each resolver's `extras` keys, and the `query_key` folding profiles.
- **Closed lists**, each with its source, in `src/vocabulary.ts` (`schemas/vocabulary.json` for Python), and the message types (`RawItem`, `NormalizedItem`, `ItemMetric`, `Job` and the rest) for TypeScript.
- **The n8n signing helper** (`signN8n`, `verifyN8n`): the headers and signed string are in VERSIONING.md.

Every helper takes all its inputs as arguments. None reads the environment, a clock or the network: the `author_ref` key and the n8n secret are passed in by the caller, who reads them from Vault at run time. The golden files use published test values, never real keys.

## Using it from a service

A TypeScript service depends on `"contracts": "workspace:*"` and imports from `contracts` (the entry points are compiled to `dist/` by `pnpm --filter contracts build`; the Zod schemas are under `contracts/schemas`). A Python service lists `listening-contracts` in its dependencies with `[tool.uv.sources] listening-contracts = { path = "../../packages/contracts", editable = true }`.

A producer builds a message, validates it strictly and keys it; a consumer validates tolerantly and decides what to do with each version. In TypeScript:

```ts
import { classifyVersion, idempotencyKey, itemId, partitionKey, validate } from "contracts";

// tt-video-stats-refresher has read a TikTok video's counts on the vendor route.
const key = idempotencyKey("tiktok", "video", "7421538806219533573");
const metrics = {
  schema: "item.metrics/v1",
  message_id: "01M4AV7WM89CV77W1H3Z8YC6ZR",
  produced_at: "2026-10-07T09:31:17Z",
  producer: {
    service: "tt-video-stats-refresher",
    version: "1.0.0",
    job_id: "01J9N5D6T3K8R2W7Y0A4F1HXQB",
  },
  item_id: itemId(key),
  idempotency_key: key,
  platform: "tiktok",
  platform_id: "7421538806219533573",
  source_id: "3d8a51c2-7e04-4b9f-8c16-2a9e5d70f4b8",
  created_at: "2026-10-06T09:10:00Z",
  observation: { label: "refresh", step: "+24h", observed_at: "2026-10-07T09:31:15Z" },
  metrics: { views: 61250, likes: 4410, comments: 498, shares: 312, reactions_by_type: null },
  provenance: {
    route: "amber",
    vendor: "tikhub",
    service: "tt-video-stats-refresher",
    fetched_at: "2026-10-07T09:31:15Z",
  },
  retention_class: "vendor_agreed",
};

// The producer validates strictly before it sends, and keys the message by its partition key.
const checked = validate("item.metrics/v1", metrics, "producer");
if (!checked.ok) throw new Error(JSON.stringify(checked.issues));
console.log(key, metrics.item_id);
console.log("key", partitionKey("item.metrics/v1", metrics));

// A field this version does not know: a consumer drops it, a producer refuses it.
const later = { ...metrics, trace_id: "4bf92f3577b34da6a3ce929d0e0e4736" };
if (validate("item.metrics/v1", later, "consumer").ok) console.log("consumer reads it");
const refused = validate("item.metrics/v1", later, "producer");
if (!refused.ok)
  console.log("producer refuses", refused.issues.map((i) => i.path.join(".")).join(", "));

// A job is checked against the producer table of its queue and keyed by that queue's field. A job a
// scheduler emits carries its own job_id as producer.job_id (VERSIONING.md, F-17).
const job = {
  schema: "job/v1",
  message_id: "01M487XBH0MTYTTCDSW77CPSTB",
  produced_at: "2026-10-06T09:15:00Z",
  producer: {
    service: "fb-page-feed-poller",
    version: "1.0.0",
    job_id: "01M48DXKW0Q8N3K5D2B7T4W9XC",
  },
  job_id: "01M48DXKW0Q8N3K5D2B7T4W9XC",
  kind: "rotation",
  due_at: "2026-10-06T09:15:00Z",
  attempt: 1,
  source_id: "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
};
const queue = "jobs.fb-page-feed-poller";
const sent = validate("job/v1", job, "producer", { queue });
if (!sent.ok) throw new Error(JSON.stringify(sent.issues));
console.log("job key", partitionKey("job/v1", job, { queue }));
const noQueue = validate("job/v1", job, "producer");
if (!noQueue.ok) console.log("without its queue:", noQueue.issues[0]?.code);

// A consumer of item.metrics/v1 skips a version the package knows and parks one it does not.
for (const id of ["item.hits/v1", "item.metrics/v2"])
  console.log(`${id}: ${classifyVersion(id, ["item.metrics/v1"])}`);
```

The same in Python:

```python
from listening_contracts import (
    classify_version,
    idempotency_key,
    item_id,
    partition_key,
    validate,
)

# tt-video-stats-refresher has read a TikTok video's counts on the vendor route.
key = idempotency_key("tiktok", "video", "7421538806219533573")
metrics = {
    "schema": "item.metrics/v1",
    "message_id": "01M4AV7WM89CV77W1H3Z8YC6ZR",
    "produced_at": "2026-10-07T09:31:17Z",
    "producer": {
        "service": "tt-video-stats-refresher",
        "version": "1.0.0",
        "job_id": "01J9N5D6T3K8R2W7Y0A4F1HXQB",
    },
    "item_id": item_id(key),
    "idempotency_key": key,
    "platform": "tiktok",
    "platform_id": "7421538806219533573",
    "source_id": "3d8a51c2-7e04-4b9f-8c16-2a9e5d70f4b8",
    "created_at": "2026-10-06T09:10:00Z",
    "observation": {"label": "refresh", "step": "+24h", "observed_at": "2026-10-07T09:31:15Z"},
    "metrics": {
        "views": 61250,
        "likes": 4410,
        "comments": 498,
        "shares": 312,
        "reactions_by_type": None,
    },
    "provenance": {
        "route": "amber",
        "vendor": "tikhub",
        "service": "tt-video-stats-refresher",
        "fetched_at": "2026-10-07T09:31:15Z",
    },
    "retention_class": "vendor_agreed",
}

# The producer validates strictly before it sends, and keys the message by its partition key.
checked = validate("item.metrics/v1", metrics, "producer")
if not checked.ok:
    raise ValueError(checked.issues)
print(key, metrics["item_id"])
print("key", partition_key("item.metrics/v1", metrics))

# A field this version does not know: a consumer drops it, a producer refuses it.
later = {**metrics, "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"}
if validate("item.metrics/v1", later, "consumer").ok:
    print("consumer reads it")
refused = validate("item.metrics/v1", later, "producer")
if not refused.ok:
    print("producer refuses", ", ".join(".".join(map(str, i["path"])) for i in refused.issues))

# A job is checked against the producer table of its queue and keyed by that queue's field. A job a
# scheduler emits carries its own job_id as producer.job_id (VERSIONING.md, F-17).
job = {
    "schema": "job/v1",
    "message_id": "01M487XBH0MTYTTCDSW77CPSTB",
    "produced_at": "2026-10-06T09:15:00Z",
    "producer": {
        "service": "fb-page-feed-poller",
        "version": "1.0.0",
        "job_id": "01M48DXKW0Q8N3K5D2B7T4W9XC",
    },
    "job_id": "01M48DXKW0Q8N3K5D2B7T4W9XC",
    "kind": "rotation",
    "due_at": "2026-10-06T09:15:00Z",
    "attempt": 1,
    "source_id": "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11",
}
queue = "jobs.fb-page-feed-poller"
sent = validate("job/v1", job, "producer", queue=queue)
if not sent.ok:
    raise ValueError(sent.issues)
print("job key", partition_key("job/v1", job, queue=queue))
no_queue = validate("job/v1", job, "producer")
if not no_queue.ok:
    print("without its queue:", no_queue.issues[0]["code"])

# A consumer of item.metrics/v1 skips a version the package knows and parks one it does not.
for schema_id in ["item.hits/v1", "item.metrics/v2"]:
    print(f"{schema_id}: {classify_version(schema_id, ['item.metrics/v1'])}")
```

Both print:

```text
tiktok:video:7421538806219533573 87c23e1a-aa3a-5491-b10d-abe0a88b5eee
key 3d8a51c2-7e04-4b9f-8c16-2a9e5d70f4b8
consumer reads it
producer refuses trace_id
job key 6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11
without its queue: no_queue
item.hits/v1: skip
item.metrics/v2: park
```

Two options complete `validate()`. A job's checks depend on its queue, so producer mode refuses a job validated without `queue` (`no_queue`). The government rule on client alerts depends on the client's type, which an alert does not carry, so producer mode refuses a client or account-manager alert validated without `clientType` (`client_type` in Python), with `no_client_type`. Consumer mode skips both checks when the option is missing.

The two examples run as tests (`test/unit/readme-example.test.ts`, `python/tests/test_readme_example.py`), so they stay true.

## Regenerating and testing

The Zod source in `src/` is the one definition; everything else is generated from it and committed, and tests compare the committed files with a fresh generation.

- `pnpm --filter contracts export:schemas`: the JSON Schemas, `schemas/catalogue.json`, `patterns.json` and `vocabulary.json`.
- `pnpm --filter contracts gen:python`: the Pydantic models, from the JSON Schemas (datamodel-code-generator).
- `pnpm --filter contracts gen:fixtures`: the contract fixtures under `fixtures/contracts/`, from `scripts/fixtures/`.
- `make test SERVICE=contracts`: the TypeScript and Python suites; `make check` runs them with lint, types and formatting.

## Who edits it

The contracts are frozen. Only F2, F3 and F8, which build them, and `/contract-change` applying an approved proposal on `sb/CC-<proposal>` edit this package (`.claude/rules/contracts.md`; a hook blocks every other session). A session that needs a change writes `docs/proposals/<session>-<topic>.md` from `build-plan/templates/PROPOSAL.md` and stops.
