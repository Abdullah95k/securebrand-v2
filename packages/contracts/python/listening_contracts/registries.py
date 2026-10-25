"""The registries the SDK enforces, read from the same JSON data as the TypeScript package
(packages/contracts/registries/), so the two languages cannot drift: the service index and vendors
(Q1, Q4), the producer table of the job queues (ADR-0012), the writers of every topic, the producers
allowed per registry.decisions type (ADR-0013), the partition keys (ADR-0004), each producer's
visibility (ADR-0053) and the keys each producer declares in `context` and `extras` (ADR-0005,
ADR-0033)."""

import re
from typing import Literal, NotRequired, TypedDict, cast

from listening_contracts._artefacts import registry
from listening_contracts.errors import ContractError

# The service index and the D3 writer names (CONVENTIONS v1.1 L372 to L384; Q4), and the vendors.


class _ServicesFile(TypedDict):
    platform_groups: dict[str, list[str]]
    shared_groups: dict[str, list[str]]
    d3_writers: list[str]


class _VendorsFile(TypedDict):
    amber: list[str]
    green: list[str]


_services = cast(_ServicesFile, registry("services.json"))
_vendors = cast(_VendorsFile, registry("vendors.json"))

PLATFORM_GROUPS: dict[str, tuple[str, ...]] = {
    group: tuple(services) for group, services in _services["platform_groups"].items()
}
PLATFORM_SERVICES: tuple[str, ...] = tuple(
    s for group in _services["platform_groups"].values() for s in group
)
INDEX_SERVICES: tuple[str, ...] = PLATFORM_SERVICES + tuple(
    s for group in _services["shared_groups"].values() for s in group
)
D3_WRITERS: tuple[str, ...] = tuple(_services["d3_writers"])
AMBER_VENDORS: tuple[str, ...] = tuple(_vendors["amber"])
GREEN_VENDORS: tuple[str, ...] = tuple(_vendors["green"])

_KNOWN = frozenset(INDEX_SERVICES + D3_WRITERS)
_PLATFORM = frozenset(PLATFORM_SERVICES)
_INDEX = frozenset(INDEX_SERVICES)


def is_known_service(service: str) -> bool:
    return service in _KNOWN


def is_platform_service(service: str) -> bool:
    return service in _PLATFORM


def is_known_vendor(route: str, vendor: str | None) -> bool:
    """An amber record names an amber vendor; a green one a licensed engine or none
    (ADR-0051 (c))."""
    if route == "amber":
        return vendor is not None and vendor in AMBER_VENDORS
    if route == "green":
        return vendor is None or vendor in GREEN_VENDORS
    return False


def names_service(producers: list[str], service: str) -> bool:
    """Whether `service` is one of `producers`: `@platform` stands for the platform services and `*`
    for any service of the index (the D3 writers have their own rows); `@queue` is resolved by the
    caller, which knows the queue."""
    return any(
        p == service
        or (p == "@platform" and service in _PLATFORM)
        or (p == "*" and service in _INDEX)
        for p in producers
    )


# Dotted paths into plain JSON values, as the registries name fields.


def get_path(value: object, path: str) -> object:
    """The value at `path`, or None when a step is missing; a present null is None too."""
    current: object = value
    for step in path.split("."):
        if not isinstance(current, dict) or step not in current:
            return None
        current = cast(dict[str, object], current)[step]
    return current


def has_value(value: object, path: str) -> bool:
    return get_path(value, path) is not None


# The producer table (ADR-0012).

ProducerRow = TypedDict(
    "ProducerRow", {"queue": str, "kind": str, "producers": list[str], "from": str}
)
_FileRow = TypedDict(
    "_FileRow", {"queues": list[str], "kinds": list[str], "producers": list[str], "from": str}
)
RequiredFieldRow = TypedDict(
    "RequiredFieldRow",
    {
        "queues": list[str],
        "kinds": list[str],
        "producers": NotRequired[list[str]],
        "fields": list[str],
        "from": str,
    },
)


class _ProducersFile(TypedDict):
    rows: list[_FileRow]
    required_fields: list[RequiredFieldRow]


_producers = cast(_ProducersFile, registry("producers.json"))
_QUEUE = re.compile(r"jobs\.([a-z0-9]+(?:-[a-z0-9]+)*)(?:\.priority)?")


def queue_service(queue: str) -> str:
    """`jobs.<service>` and `jobs.<service>.priority` belong to `<service>`."""
    m = _QUEUE.fullmatch(queue)
    if m is None:
        raise ContractError("bad_queue", queue)
    return m.group(1)


def _resolve_queue(producers: list[str], queue: str) -> list[str]:
    return [queue_service(queue) if p == "@queue" else p for p in producers]


_EXPANDED: list[ProducerRow] = [
    {
        "queue": queue,
        "kind": kind,
        "producers": _resolve_queue(row["producers"], queue),
        "from": row["from"],
    }
    for row in _producers["rows"]
    for queue in row["queues"]
    for kind in row["kinds"]
]


def producer_rows() -> list[ProducerRow]:
    return [
        {
            "queue": r["queue"],
            "kind": r["kind"],
            "producers": list(r["producers"]),
            "from": r["from"],
        }
        for r in _EXPANDED
    ]


def required_field_rows() -> list[RequiredFieldRow]:
    return [cast(RequiredFieldRow, dict(r)) for r in _producers["required_fields"]]


def allowed_producers(queue: str, kind: str) -> list[str]:
    """The services allowed to emit `kind` on `queue`; none for a (queue, kind) the table does not
    list."""
    out: list[str] = []
    for row in _EXPANDED:
        if row["queue"] == queue and row["kind"] == kind:
            out.extend(p for p in row["producers"] if p not in out)
    return out


def is_allowed_producer(queue: str, kind: str, service: str) -> bool:
    return service in allowed_producers(queue, kind)


def required_job_fields(queue: str, kind: str, service: str) -> list[str]:
    """The kind fields a (queue, kind) row requires of a job from `service` (dotted when nested)."""
    out: list[str] = []
    for row in _producers["required_fields"]:
        if queue not in row["queues"] or kind not in row["kinds"]:
            continue
        producers = row.get("producers")
        if producers is not None and service not in _resolve_queue(producers, queue):
            continue
        out.extend(f for f in row["fields"] if f not in out)
    return out


# The topic writers (CONVENTIONS v1.1 L25 to L40) and the decision rows (ADR-0013).


class _Condition(TypedDict):
    schema: str
    writer: str
    field: str
    equals: str | bool


class _WritersFile(TypedDict):
    topics: dict[str, list[str]]
    raw_items_kinds: dict[str, list[str]]
    conditions: list[_Condition]


DecisionSubject = Literal["candidate_key", "author_ref", "source_id", "platform", "keyword_id"]
DecisionRow = TypedDict(
    "DecisionRow",
    {
        "decisions": list[str],
        "subject": DecisionSubject,
        "producers": list[str],
        "reasons": NotRequired[list[str | None]],
        "healths": NotRequired[list[str]],
        "provenance": Literal["required", "refused", "optional"],
        "from": str,
    },
)


class DecisionQuery(TypedDict):
    decision: str
    subject: str
    reason: str | None
    health: NotRequired[str | None]


class WriterCondition(TypedDict):
    field: str
    equals: str | bool


class _DecisionFile(TypedDict):
    rows: list[DecisionRow]


_writers = cast(_WritersFile, registry("topic-writers.json"))
_decisions = cast(_DecisionFile, registry("decision-producers.json"))
_DLQ_SCHEMA = re.compile(r"dlq\.([a-z0-9]+(?:-[a-z0-9]+)*)/v1")


def topic_writers() -> dict[str, list[str]]:
    """The writers of every topic, keyed by schema id (registry.decisions: see the decision
    rows)."""
    return {schema: list(writers) for schema, writers in _writers["topics"].items()}


def raw_items_kinds(service: str) -> list[str] | None:
    """The record kinds a raw.items writer may write, or None for a service that writes none."""
    kinds = _writers["raw_items_kinds"].get(service)
    return list(kinds) if kinds is not None else None


def registry_schema_id(schema_id: str) -> str:
    """The schema id under which the registries file a concrete id (`dlq.<service>/v1` is one
    entry)."""
    return "dlq.<service>/v1" if _DLQ_SCHEMA.fullmatch(schema_id) else schema_id


def decision_rows() -> list[DecisionRow]:
    return [cast(DecisionRow, dict(r)) for r in _decisions["rows"]]


def _row_matches(row: DecisionRow, q: DecisionQuery, service: str) -> bool:
    health = q.get("health")
    return (
        q["decision"] in row["decisions"]
        and row["subject"] == q["subject"]
        and names_service(row["producers"], service)
        and ("reasons" not in row or q["reason"] in row["reasons"])
        and ("healths" not in row or (health is not None and health in row["healths"]))
    )


def decision_row(query: DecisionQuery, service: str) -> DecisionRow | None:
    """The decision row that allows `service` to send this decision, or None when none does."""
    return next((r for r in _decisions["rows"] if _row_matches(r, query, service)), None)


def is_allowed_decision_producer(query: DecisionQuery, service: str) -> bool:
    return decision_row(query, service) is not None


def is_allowed_topic_writer(
    schema_id: str, service: str, *, kind: str | None = None, queue: str | None = None
) -> bool:
    """Whether `service` may write `schema_id`; a raw.items writer only its record kinds (`kind`), a
    jobs.completed report only the service that ran the job (`queue`)."""
    if not is_known_service(service):
        return False
    dlq = _DLQ_SCHEMA.fullmatch(schema_id)
    if dlq is not None:
        return dlq.group(1) == service
    if schema_id == "registry.decisions/v1":
        return any(names_service(r["producers"], service) for r in _decisions["rows"])
    if schema_id == "jobs.completed/v1":
        return queue is not None and queue_service(queue) == service
    writers = _writers["topics"].get(schema_id)
    if writers is None or service not in writers:
        return False
    if schema_id == "raw.items/v1" and kind is not None:
        return kind in _writers["raw_items_kinds"].get(service, [])
    return True


def writer_conditions(schema_id: str, service: str) -> list[WriterCondition]:
    """The field values a writer's messages on `schema_id` must carry (ADR-0032, ADR-0012 L34)."""
    return [
        {"field": c["field"], "equals": c["equals"]}
        for c in _writers["conditions"]
        if c["schema"] == schema_id and c["writer"] == service
    ]


# Partition keys (ADR-0004).


class _Fields(TypedDict):
    fields: list[str]


class _JobRule(TypedDict):
    queues: list[str] | Literal["*"]
    kinds: list[str] | Literal["*"]
    fields: list[str]


class _Jobs(TypedDict):
    default: _Fields
    rules: list[_JobRule]


class _PartitionKeysFile(TypedDict):
    topics: dict[str, _Fields]
    jobs: _Jobs


_keys = cast(_PartitionKeysFile, registry("partition-keys.json"))


def topic_key_fields(schema_id: str) -> list[str] | None:
    """The key fields of a topic, tried in order; None for a schema id the record does not know."""
    entry = _keys["topics"].get(registry_schema_id(schema_id))
    return list(entry["fields"]) if entry is not None else None


def job_key_fields(queue: str, kind: str) -> list[str]:
    """The key fields of a job of `kind` on `queue`: the first matching rule, else the default."""
    for rule in _keys["jobs"]["rules"]:
        if (rule["queues"] == "*" or queue in rule["queues"]) and (
            rule["kinds"] == "*" or kind in rule["kinds"]
        ):
            return list(rule["fields"])
    return list(_keys["jobs"]["default"]["fields"])


def _first_key(message: object, fields: list[str], what: str) -> str:
    for field in fields:
        value = get_path(message, field)
        if value is None:
            continue
        if not isinstance(value, str) or value == "":
            raise ContractError("bad_partition_key", f"{what}: {field}")
        return value
    raise ContractError("no_partition_key", f"{what} carries none of {', '.join(fields)}")


def partition_key(schema_id: str, message: object, *, queue: str | None = None) -> str:
    """The Kafka key of a message: by its schema id, and for a job (`job/v1`) by the queue it goes
    to. A jobs.completed report takes the key of the job it reports, found by its own `queue` and
    `kind`."""
    if schema_id == "job/v1":
        if queue is None:
            raise ContractError("no_queue", "a job's key depends on its queue")
        kind = get_path(message, "kind")
        if not isinstance(kind, str):
            raise ContractError("no_partition_key", "a job without a kind")
        return _first_key(message, job_key_fields(queue, kind), f"{queue} {kind}")
    if schema_id == "jobs.completed/v1":
        report_queue = get_path(message, "queue")
        kind = get_path(message, "kind")
        if not isinstance(report_queue, str) or not isinstance(kind, str):
            raise ContractError(
                "no_partition_key", "a completion report without its queue and kind"
            )
        return _first_key(
            message, job_key_fields(report_queue, kind), f"jobs.completed for {report_queue} {kind}"
        )
    fields = topic_key_fields(schema_id)
    if fields is None:
        raise ContractError("unknown_schema", schema_id)
    return _first_key(message, fields, schema_id)


# Visibility per producer (ADR-0053).

VisibilityRuleName = Literal["owner", "watchers", "pool", "owner_or_watchers", "owner_or_pool"]


class VisibilityRule(TypedDict):
    rule: VisibilityRuleName
    limit: Literal["amber", "x_gate"] | None


class _VisibilityFile(TypedDict):
    services: dict[str, VisibilityRule]


_visibility = cast(_VisibilityFile, registry("visibility.json"))


def visibility_rule(service: str) -> VisibilityRule | None:
    """The service's declared rule and client filter, or None for a service that declares none."""
    rule = _visibility["services"].get(service)
    return {"rule": rule["rule"], "limit": rule["limit"]} if rule is not None else None


def visibility_of(service: str, *, owned_by_client: bool) -> str | None:
    """The visibility of a record `service` fetched from a source that is, or is not,
    client-owned."""
    rule = _visibility["services"].get(service)
    if rule is None:
        return None
    name = rule["rule"]
    if name == "owner_or_watchers":
        return "owner" if owned_by_client else "watchers"
    if name == "owner_or_pool":
        return "owner" if owned_by_client else "pool"
    return name


# The keys each producer declares in raw.items `context` (ADR-0005) and poster.profiles `extras`
# (ADR-0033).


class DeclaredKeys(TypedDict):
    keys: list[str]
    required: list[str]


class ContextKeyRegistry(TypedDict):
    producers: dict[str, DeclaredKeys]
    by_kind: dict[str, DeclaredKeys]


class ExtrasKeyRegistry(TypedDict):
    resolvers: dict[str, list[str]]


_context = cast(ContextKeyRegistry, registry("context-keys.json"))
_extras = cast(ExtrasKeyRegistry, registry("extras-keys.json"))


def context_key_registry() -> ContextKeyRegistry:
    return {
        "producers": {
            s: {"keys": list(e["keys"]), "required": list(e["required"])}
            for s, e in _context["producers"].items()
        },
        "by_kind": {
            k: {"keys": list(e["keys"]), "required": list(e["required"])}
            for k, e in _context["by_kind"].items()
        },
    }


def extras_key_registry() -> ExtrasKeyRegistry:
    return {"resolvers": {s: list(keys) for s, keys in _extras["resolvers"].items()}}


def declared_context_keys(service: str, kind: str) -> DeclaredKeys:
    """The `context` keys a raw.items record of `kind` from `service` may carry, and those it
    must."""
    empty: DeclaredKeys = {"keys": [], "required": []}
    own = _context["producers"].get(service, empty)
    by_kind = _context["by_kind"].get(kind, empty)
    return {
        "keys": list(dict.fromkeys([*own["keys"], *by_kind["keys"]])),
        "required": list(dict.fromkeys([*own["required"], *by_kind["required"]])),
    }


def declared_extras_keys(service: str) -> list[str] | None:
    """The `extras` keys a resolver declares, or None for a service that declares none."""
    keys = _extras["resolvers"].get(service)
    return list(keys) if keys is not None else None
