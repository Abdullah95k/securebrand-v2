"""validate(): the contract check every producer and consumer runs (ADR-0002, ADR-0012), the twin
of src/validate.ts. Three layers, each reported as issues with the path of the field at fault:

1. the generated Pydantic model of the mode (models/strict refuses unknown fields, models/consumer
   drops them), validated strictly, as JSON values (an integral float counts as an integer, as in
   JavaScript, and a non-finite number is refused);
2. the rules a schema cannot state, in both modes: keys equal to the key helpers' output, fields
   that go together, a control message refusing provenance (ADR-0003, ADR-0006);
3. the registry data, in producer mode only, because it grows inside the version (Q1, F-09): known
   service names, vendors by route, topic writers, the decision rows and their Provenance column
   (F-14), the keys each producer declares in `context` and `extras`. A job's producer-table row,
   required fields and partition key are checked in both modes when the queue is given: the
   consumer's job wrapper dead-letters a job with no row (ADR-0012). A jobs.completed report's
   partition key and X fields are checked in consumer mode only for a service the package knows
   (D-9), so a report from a service a newer package adds is not refused.

Layer 3 runs only when layer 2 found nothing, so an issue names the first rule broken. The codes of
layer 1 are the validator's own (Pydantic's here, Zod's in TypeScript); the paths and the codes of
layers 2 and 3 are the same in both languages.
"""

import importlib
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cache
from typing import Any, Literal, NamedTuple, TypedDict, cast

from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails

from listening_contracts._artefacts import artefact
from listening_contracts.errors import ContractError
from listening_contracts.keys import (
    analysis_key,
    card_id,
    deletion_id,
    hit_id,
    idempotency_key,
    item_id,
    parse_candidate_key,
    parse_key,
    parse_raw_ref,
)
from listening_contracts.models.consumer import deletions_v1 as consumer_deletions
from listening_contracts.models.strict import deletions_v1 as strict_deletions
from listening_contracts.patterns import matches
from listening_contracts.registries import (
    PLATFORM_GROUPS,
    DecisionQuery,
    allowed_producers,
    decision_row,
    declared_context_keys,
    declared_extras_keys,
    dlq_service,
    get_path,
    has_value,
    is_allowed_topic_writer,
    is_known_service,
    is_known_vendor,
    is_listed_vendor,
    job_key_fields,
    queue_service,
    required_job_fields,
    writer_conditions,
)
from listening_contracts.ulid import hit_message_id
from listening_contracts.url import canonical_url_hash, url_hash, url_key
from listening_contracts.versions import REPORT_KIND_FIELDS, catalogue_entry, catalogue_id
from listening_contracts.vocabulary import VOCABULARY

Mode = Literal["producer", "consumer"]
ClientType = Literal["commercial", "government"]
IssuePath = list[str | int]
Json = dict[str, Any]


class ValidationIssue(TypedDict):
    path: IssuePath
    code: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    """`ok` with the parsed message as JSON in `value` (in consumer mode without the fields the
    schema does not know), or not `ok` with the `issues`."""

    ok: bool
    value: Any = None
    issues: list[ValidationIssue] = field(default_factory=lambda: [])


CONTENT_KINDS = VOCABULARY["CONTENT_KINDS"]
FETCH_DELETION_REASONS = VOCABULARY["FETCH_DELETION_REASONS"]
FLAG_REASONS = VOCABULARY["FLAG_REASONS"]
ORGANISATION_ACCOUNT_TYPES = VOCABULARY["ORGANISATION_ACCOUNT_TYPES"]
PERSON_ACCOUNT_TYPES = VOCABULARY["PERSON_ACCOUNT_TYPES"]
PERSON_UNLISTABLE_PLATFORMS = VOCABULARY["PERSON_UNLISTABLE_PLATFORMS"]
PROFILE_REVIEW_REASONS = VOCABULARY["PROFILE_REVIEW_REASONS"]
PROFILE_UNRESOLVABLE_REASONS = VOCABULARY["PROFILE_UNRESOLVABLE_REASONS"]
GOVERNMENT_ALERT_RULE_TYPES = VOCABULARY["GOVERNMENT_ALERT_RULE_TYPES"]
RETENTION_CLASSES = VOCABULARY["RETENTION_CLASSES"]
X_SERVICES = PLATFORM_GROUPS.get("x", ())


def _rec(value: object) -> Json:
    return cast(Json, value) if isinstance(value, dict) else {}


def _str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _json_equal(a: object, b: object) -> bool:
    """Structural JSON equality, key order aside, as JavaScript compares values: a boolean is never
    a number. It walks without recursion and never raises."""
    pending: list[tuple[object, object]] = [(a, b)]
    while pending:
        x, y = pending.pop()
        if isinstance(x, list) or isinstance(y, list):
            if not (isinstance(x, list) and isinstance(y, list)):
                return False
            xs, ys = cast(list[object], x), cast(list[object], y)
            if len(xs) != len(ys):
                return False
            pending.extend(zip(xs, ys, strict=True))
        elif isinstance(x, dict) or isinstance(y, dict):
            if not (isinstance(x, dict) and isinstance(y, dict)):
                return False
            xd, yd = cast(dict[str, object], x), cast(dict[str, object], y)
            if xd.keys() != yd.keys():
                return False
            pending.extend((xd[k], yd[k]) for k in xd)
        elif isinstance(x, bool) or isinstance(y, bool):
            if x is not y:
                return False
        elif x != y:
            return False
    return True


def _derive(f: Callable[[], str]) -> str | None:
    """The value a key helper derives, or None when the helper refuses its input."""
    try:
        return f()
    except (ContractError, TypeError, ValueError, KeyError, AttributeError):
        return None


class _Issues:
    def __init__(self) -> None:
        self.list: list[ValidationIssue] = []

    def add(self, path: IssuePath, code: str, message: str) -> None:
        self.list.append({"path": path, "code": code, "message": message})


# --- JSON values --------------------------------------------------------------------------------


NOT_UNICODE = (
    "a string or key is well-formed Unicode, UTF-8 encodable (ADR-0006); this one holds a lone"
    " surrogate"
)


def _well_formed(s: str) -> bool:
    try:
        s.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _as_json(value: object, path: IssuePath, out: _Issues) -> object:
    """The value as JavaScript reads JSON: an integral float is an integer; NaN and the infinities
    are not JSON; every string and key is well-formed Unicode, so a lone surrogate is refused alike
    in both languages (review finding 5). Depth first, an object's keys before its values."""
    if isinstance(value, str):
        if not _well_formed(value):
            out.add(path, "not_unicode", NOT_UNICODE)
        return value
    if isinstance(value, bool) or value is None or isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            out.add(path, "not_json", "a number is finite")
            return value
        return int(value) if value.is_integer() else value
    if isinstance(value, list):
        return [_as_json(v, [*path, i], out) for i, v in enumerate(cast(list[object], value))]
    if isinstance(value, dict):
        items = cast(dict[str, object], value)
        for k in items:
            if not _well_formed(k):
                out.add([*path, k], "not_unicode", NOT_UNICODE)
        return {k: _as_json(v, [*path, k], out) for k, v in items.items()}
    out.add(path, "not_json", f"{type(value).__name__} is not a JSON value")
    return value


def _constant_types(parsed: object, sent: object, out: _Issues) -> None:
    """A constant keeps its JSON type, as in Zod and the JSON Schema `const` (review finding 6).
    Pydantic matches a literal by equality, even in strict mode, and keeps the literal: 0 sent
    for `Literal[False]` parses as False, true for `Literal[1, 2, 3]` as 1. That is the only swap
    between a boolean and a number strict Pydantic makes, so a parsed value and the value sent of
    which one only is a boolean mark one. Unknown fields a consumer drops are not compared."""
    pending: list[tuple[object, object, IssuePath]] = [(parsed, sent, [])]
    while pending:
        a, b, path = pending.pop()
        if isinstance(a, dict) and isinstance(b, dict):
            ad, bd = cast(dict[str, object], a), cast(dict[str, object], b)
            pending.extend((ad[k], bd[k], [*path, k]) for k in ad if k in bd)
        elif isinstance(a, list) and isinstance(b, list):
            al, bl = cast(list[object], a), cast(list[object], b)
            pending.extend((x, y, [*path, i]) for i, (x, y) in enumerate(zip(al, bl, strict=False)))
        elif isinstance(a, bool) != isinstance(b, bool):
            out.add(path, "literal_error", "a constant keeps its JSON type")


# --- Pydantic issues ----------------------------------------------------------------------------


class _Union(NamedTuple):
    """A discriminated union: its discriminator and the tag values each branch takes, by the
    branch's class name."""

    discriminator: str
    tags: dict[str, list[object]]


def _resolve(defs: dict[str, Any], node: object) -> dict[str, Any]:
    while isinstance(node, dict) and "$ref" in node:
        node = defs[cast(str, node["$ref"]).rsplit("/", 1)[-1]]
    return cast(dict[str, Any], node) if isinstance(node, dict) else {}


def _tag_values(prop: object) -> list[object] | None:
    if isinstance(prop, dict):
        p = cast(dict[str, Any], prop)
        if "const" in p:
            return [p["const"]]
        if "enum" in p:
            return list(cast(list[object], p["enum"]))
    return None


@cache
def _unions(schema_id: str) -> dict[str, _Union]:
    """The discriminated unions of a schema by branch class name, read from its exported JSON
    Schema: a `oneOf` is a Zod discriminated union, each branch's `title` is the class name the
    model generator gives it, and the discriminator is the one property that every branch fixes
    with a `const` or an `enum`, to values no two branches share (D-4)."""
    entry = catalogue_entry(schema_id)
    if entry is None:
        return {}
    schema = cast(dict[str, Any], artefact(entry["file"]))
    defs = cast(dict[str, Any], schema.get("$defs", {}))
    out: dict[str, _Union] = {}
    pending: list[object] = [schema]
    while pending:
        node = pending.pop()
        if isinstance(node, list):
            pending.extend(cast(list[object], node))
            continue
        if not isinstance(node, dict):
            continue
        n = cast(dict[str, Any], node)
        pending.extend(n.values())
        if "oneOf" not in n:
            continue
        branches = [_resolve(defs, b) for b in cast(list[object], n["oneOf"])]
        props = [cast(dict[str, object], b.get("properties", {})) for b in branches]
        found: list[tuple[str, list[list[object]]]] = []
        common = set(props[0])
        for p in props[1:]:
            common &= set(p)
        for name in sorted(common):
            values = [_tag_values(p[name]) for p in props]
            tags = [v for v in values if v is not None]
            flat = [repr((type(t), t)) for v in tags for t in v]
            if len(tags) == len(values) and len(flat) == len(set(flat)):
                found.append((name, tags))
        if len(found) == 1:
            name, tags = found[0]
            union = _Union(
                name, {str(b.get("title")): t for b, t in zip(branches, tags, strict=True)}
            )
            out.update((title, union) for title in union.tags)
    return out


def _same_json(a: object, b: object) -> bool:
    return a == b and isinstance(a, bool) == isinstance(b, bool)


_ABSENT = object()
# The errors of a nullable's or an optional's other alternative, which Zod never reports.
_ALTERNATIVES = frozenset({"none_required", "missing_sentinel_error"})


def _locate(
    value: object, loc: tuple[int | str, ...], kind: str, unions: dict[str, _Union]
) -> tuple[IssuePath, str | None] | None:
    """Walks a Pydantic location along the message and returns the path Zod gives the error.
    A discriminated union keeps only the branch its tag selects: another branch's error gives
    None, and a tag that selects none gives the discriminator's path with the code Pydantic
    uses for it. Every other step that names no key of the value is a label (a plain union's
    branch, a type) and is dropped, except a missing or an unknown field's name (D-4)."""
    out: IssuePath = []
    current: object = value
    last = len(loc) - 1
    for i, step in enumerate(loc):
        if isinstance(current, dict):
            node = cast(dict[str, object], current)
            if isinstance(step, str) and step in node:
                out.append(step)
                current = node[step]
                continue
            union = unions.get(step) if isinstance(step, str) else None
            if union is not None:
                tag = node.get(union.discriminator, _ABSENT)
                chosen = next(
                    (
                        b
                        for b, values in union.tags.items()
                        if any(_same_json(tag, v) for v in values)
                    ),
                    None,
                )
                if chosen is None:
                    code = "union_tag_not_found" if tag is _ABSENT else "union_tag_invalid"
                    return [*out, union.discriminator], code
                if chosen != step:
                    return None
            elif i == last and isinstance(step, str) and kind in ("missing", "extra_forbidden"):
                out.append(step)
            continue
        if isinstance(current, list) and isinstance(step, int):
            items = cast(list[object], current)
            out.append(step)
            current = items[step] if 0 <= step < len(items) else None
    return out, None


def _schema_issues(
    schema_id: str, message: object, errors: list[ErrorDetails]
) -> list[ValidationIssue]:
    """Pydantic's errors as issues at Zod's paths (D-4), each (path, code) once."""
    unions = _unions(catalogue_id(schema_id))
    found: list[ValidationIssue] = []
    for e in errors:
        located = _locate(message, e["loc"], e["type"], unions)
        if located is None:
            continue
        path, tag_code = located
        if tag_code is None:
            found.append({"path": path, "code": e["type"], "message": e["msg"]})
        else:
            found.append({"path": path, "code": tag_code, "message": "no branch takes this tag"})
    issues: list[ValidationIssue] = []
    seen: set[str] = set()
    for issue in found:
        path = issue["path"]
        if issue["code"] in _ALTERNATIVES and any(
            o["code"] not in _ALTERNATIVES and o["path"][: len(path)] == path for o in found
        ):
            continue
        key = repr((path, issue["code"]))
        if key not in seen:
            seen.add(key)
            issues.append(issue)
    return issues


# --- shared rules -------------------------------------------------------------------------------


def _check_item_key(
    out: _Issues, path: IssuePath, platform: object, kind: object, pid: object, key: object
) -> None:
    """An item key equals the key helper's output for its platform, kind and id (ADR-0006)."""
    want = _derive(lambda: idempotency_key(cast(str, platform), cast(str, kind), cast(str, pid)))
    if want != key:
        out.add(path, "key_mismatch", f"the key is the helper's output, {want or 'none'}")


def _platform_meta_keys(platform: object, source_type: object) -> tuple[str, ...]:
    """platform_meta keys belong to one platform and source type (ADR-0065 c), ADR-0013 c),
    ADR-0041)."""
    if platform == "youtube" and source_type == "channel":
        return ("uploads_playlist_id",)
    if platform == "instagram" and source_type == "hashtag":
        return ("ig_user_id",)
    if platform == "telegram" and source_type == "group":
        return ("linked_channel_source_id", "linked_chat_id")
    return ()


def _check_platform_meta(out: _Issues, path: IssuePath, columns: Json) -> None:
    meta = columns.get("platform_meta")
    if not isinstance(meta, dict):
        return
    if "platform" not in columns or "source_type" not in columns:
        return  # a partial update
    allowed = _platform_meta_keys(columns["platform"], columns["source_type"])
    for key in cast(dict[str, object], meta):
        if key not in allowed:
            out.add(
                [*path, key],
                "platform_meta_key",
                f"{key} is no {columns['platform']} {columns['source_type']} key",
            )


def _check_snake_keys(out: _Issues, path: IssuePath, value: object) -> None:
    """The keys of the open maps (reaction types, metric names, languages) are snake_case (F-34): a
    rule here because a key pattern is a construct the Python generator cannot render (ADR-0030)."""
    if not isinstance(value, dict):
        return
    for key in cast(dict[str, object], value):
        if not matches("snakeName", key):
            out.add([*path, key], "key_pattern", f"{key} is not snake_case")


def _check_pairing(out: _Issues, m: Json) -> None:
    """provenance and retention_class travel together (ADR-0003)."""
    p, c = "provenance" in m, "retention_class" in m
    if p and not c:
        out.add(
            ["retention_class"],
            "class_without_provenance",
            "provenance travels with retention_class",
        )
    if c and not p:
        out.add(
            ["provenance"], "provenance_without_class", "retention_class travels with provenance"
        )


def _refuse_provenance(out: _Issues, raw: Json) -> None:
    """A control message carries producer and no provenance (ADR-0003), in either mode."""
    if "provenance" in raw:
        out.add(["provenance"], "provenance_refused", "a control message carries producer only")


# --- per-schema rules (both modes) --------------------------------------------------------------


@dataclass(frozen=True)
class _Context:
    schema_id: str
    mode: Mode
    queue: str | None
    client_type: ClientType | None


Rule = Callable[[Json, _Issues, _Context], None]


def _raw_items(m: Json, out: _Issues, ctx: _Context) -> None:
    env = _rec(m.get("envelope"))
    has_source, has_candidate = "source_id" in env, "candidate_key" in env
    if not has_source and not has_candidate:
        out.add(
            ["envelope", "source_id"],
            "missing_subject",
            "a record carries source_id or candidate_key (ADR-0005 L28)",
        )
    if has_source and has_candidate:
        out.add(
            ["envelope", "candidate_key"],
            "two_subjects",
            "a record carries source_id or candidate_key, never both",
        )
    if env.get("kind") in CONTENT_KINDS:
        _check_item_key(
            out,
            ["envelope", "idempotency_key"],
            env.get("platform"),
            env.get("kind"),
            env.get("platform_id"),
            env.get("idempotency_key"),
        )
    try:
        ref = parse_raw_ref(cast(str, env.get("raw_ref")))
    except (ContractError, TypeError):
        return
    if ref["route"] != _rec(env.get("provenance")).get("route") or ref["platform"] != env.get(
        "platform"
    ):
        out.add(
            ["envelope", "raw_ref"],
            "raw_ref_mismatch",
            "raw_ref names the record's own route and platform",
        )


def _items_normalized(m: Json, out: _Issues, ctx: _Context) -> None:
    _check_item_key(
        out,
        ["idempotency_key"],
        m.get("platform"),
        m.get("kind"),
        m.get("platform_id"),
        m.get("idempotency_key"),
    )
    _check_snake_keys(
        out,
        ["metrics_snapshot", "reactions_by_type"],
        _rec(m.get("metrics_snapshot")).get("reactions_by_type"),
    )
    if _derive(lambda: item_id(cast(str, m.get("idempotency_key")))) != m.get("item_id"):
        out.add(
            ["item_id"],
            "item_id_mismatch",
            "item_id = uuid_v5(ns_items, idempotency_key) (ADR-0006)",
        )
    author = _rec(m.get("author"))
    registered = author.get("author_source_id") is not None
    for name in ("display_name", "author_followers"):
        if name in author and not registered:
            out.add(
                ["author", name],
                "source_only",
                f"{name} only for a registered source (ADR-0010, ADR-0070 d))",
            )
    if author.get("author_type") == "source" and not registered:
        out.add(
            ["author", "author_source_id"],
            "source_without_id",
            "author_type source names its registered source",
        )
    if author.get("author_type") != "source" and registered:
        out.add(["author", "author_type"], "id_without_source", "an author_source_id is a source's")
    if "poster_platform_id" in m and registered:
        out.add(
            ["poster_platform_id"],
            "poster_of_source",
            "poster_platform_id never beside author_source_id (ADR-0031)",
        )


def _item_hits(m: Json, out: _Issues, ctx: _Context) -> None:
    want = _derive(
        lambda: hit_id(
            cast(str, m.get("item_id")),
            cast(str, m.get("client_id")),
            cast(str, m.get("keyword_id")),
        )
    )
    if want != m.get("hit_id"):
        out.add(
            ["hit_id"],
            "hit_id_mismatch",
            "hit_id = uuid_v5(ns_hits, item:client:keyword) (ADR-0006)",
        )
    message = _derive(
        lambda: hit_message_id(
            cast(str, m.get("hit_at")),
            cast(str, m.get("hit_id")),
            cast(int, m.get("item_version")),
            cast(str, m.get("keyword_set_version")),
        )
    )
    if message != m.get("message_id"):
        out.add(
            ["message_id"],
            "message_id_mismatch",
            "a hit's message_id is the deterministic ULID (ADR-0006)",
        )


def _discovery_hits(m: Json, out: _Issues, ctx: _Context) -> None:
    evidence = _rec(m.get("evidence"))
    _check_snake_keys(out, ["evidence", "public_metrics"], evidence.get("public_metrics"))
    _check_snake_keys(out, ["evidence", "language_share"], evidence.get("language_share"))
    if m.get("item_id") is not None and m.get("url") is not None:
        out.add(["url"], "item_and_url", "exactly one of item_id and url (ADR-0031)")
    if m.get("item_id") is None and m.get("url") is None:
        out.add(["item_id"], "neither_item_nor_url", "exactly one of item_id and url (ADR-0031)")
    candidate = _rec(m.get("candidate"))
    platform = _derive(
        lambda: parse_candidate_key(cast(str, candidate.get("candidate_key")))["platform"]
    )
    if platform != candidate.get("platform"):
        out.add(
            ["candidate", "platform"], "candidate_platform", "the candidate's platform is its key's"
        )


def _poster_profiles(m: Json, out: _Issues, ctx: _Context) -> None:
    status, reason = m.get("status"), m.get("reason")
    if status == "resolved" and reason is not None:
        out.add(["reason"], "reason_with_resolved", "a resolved answer carries no reason")
    if status == "review" and reason not in PROFILE_REVIEW_REASONS:
        out.add(["reason"], "review_reason", "a review answer names a review reason (ADR-0033)")
    if status == "unresolvable" and reason not in PROFILE_UNRESOLVABLE_REASONS:
        out.add(
            ["reason"],
            "unresolvable_reason",
            "an unresolvable answer names an unresolvable reason (ADR-0033)",
        )
    if "candidate_key" not in m:
        return  # an ordinary individual's minimised answer
    key_platform = _derive(
        lambda: parse_candidate_key(cast(str, m.get("candidate_key")))["platform"]
    )
    if key_platform != m.get("platform"):
        out.add(
            ["candidate_key"], "candidate_platform", "the candidate key's platform is the profile's"
        )
    account_type = m.get("account_type")
    if account_type is None:
        if m.get("individual") is not None:
            out.add(
                ["individual"],
                "individual_without_type",
                "no individual flag without an account_type",
            )
        if m.get("public_account") is not None:
            out.add(
                ["public_account"],
                "public_without_type",
                "no public_account without an account_type",
            )
        return
    if m.get("public_account") is None:
        out.add(
            ["public_account"],
            "public_unmarked",
            "a typed account is marked public or not (ADR-0010 L59, ADR-0033 L26)",
        )
    if m.get("individual") is not (account_type == "individual"):
        out.add(
            ["individual"],
            "individual_flag",
            "individual is true exactly when account_type is individual (ADR-0033)",
        )
    if account_type == "individual" and m.get("public_account") is False:
        out.add(
            ["public_account"],
            "individual_full_set",
            "an ordinary individual's answer is the minimised one (ADR-0033)",
        )
    if account_type in ORGANISATION_ACCOUNT_TYPES and m.get("public_account") is not True:
        out.add(
            ["public_account"],
            "organisation_public",
            "an organisation kind is a public account (ADR-0010)",
        )
    if (
        account_type in PERSON_ACCOUNT_TYPES
        and m.get("platform") in PERSON_UNLISTABLE_PLATFORMS
        and m.get("public_account") is not False
    ):
        out.add(
            ["public_account"],
            "person_unlistable",
            "no person's account is listable on this platform (ADR-0010 L70-L72)",
        )


SUBJECTS = ("candidate_key", "author_ref", "source_id", "keyword_id", "platform")


def _registry_decisions(m: Json, out: _Issues, ctx: _Context) -> None:
    present = [s for s in SUBJECTS if s in m]
    for s in present[1:]:
        out.add([s], "two_subjects", "a decision carries exactly one subject (ADR-0013)")
    _check_pairing(out, m)
    decision = _str(m.get("decision")) or ""
    block = _rec(m.get(decision))
    if decision in ("add", "update") and isinstance(block.get("source"), dict):
        _check_platform_meta(out, [decision, "source", "platform_meta"], _rec(block.get("source")))
    if (
        decision == "add"
        and "source_id" in m
        and block.get("proposed_source_id") != m.get("source_id")
    ):
        out.add(
            ["add", "proposed_source_id"],
            "owned_id",
            "an owned property's add carries its pre-allocated id as the subject (ADR-0066; F-39)",
        )
    if (
        decision in ("add", "update")
        and "keyword_id" in m
        and isinstance(block.get("platform_meta"), dict)
    ):
        for key in _rec(_rec(block.get("platform_meta")).get("instagram")):
            if key != "ig_user_id":
                out.add(
                    [decision, "platform_meta", "instagram", key],
                    "platform_meta_key",
                    "a keyword's Instagram platform_meta names its bound account only (F-13)",
                )
    if (
        decision == "push_coverage"
        and m.get("reason") is not None
        and block.get("push_covered") is not False
    ):
        out.add(
            ["push_coverage", "push_covered"],
            "coverage_reason",
            "a lapsed lease or failed subscription turns coverage off (ADR-0013)",
        )
    if decision != "health_change":
        return
    health = block.get("health")
    if "platform" not in m:
        if m.get("reason") in FLAG_REASONS and health != "blocked":
            out.add(
                ["health_change", "health"],
                "flag_health",
                "flag_off and flag_on take health blocked (ADR-0021 L61; F-11)",
            )
        if m.get("reason") == "credential_revoked" and health == "degraded":
            out.add(
                ["health_change", "health"],
                "credential_degraded",
                "credential_revoked is never degraded (ADR-0016 L27; F-11)",
            )
        return
    fallback = block.get("fallback")
    if (health == "fallback") != (fallback is not None):
        out.add(
            ["health_change", "fallback"],
            "fallback_target",
            "fallback is non-null exactly when health is fallback (R-2)",
        )
    scope = (
        "non_government"
        if health == "fallback"
        and m.get("route") == "green"
        and _rec(fallback).get("route") == "amber"
        else None
    )
    if block.get("scope") != scope:
        out.add(
            ["health_change", "scope"],
            "fallback_scope",
            "scope: non_government for a green-to-amber alternate, else null (R-2)",
        )
    if (m.get("reason") is None) != (health == "ok"):
        out.add(["reason"], "route_reason", "a route-level state names its reason, and ok none")
    if m.get("reason") == "flag_off" and health != "degraded":
        out.add(
            ["health_change", "health"],
            "flag_off_degraded",
            "the canary's flag_off returns a route to degraded (ADR-0021 L61; F-40)",
        )


def _source_events(m: Json, out: _Issues, ctx: _Context) -> None:
    _check_platform_meta(out, ["platform_meta"], m)
    if m.get("event") == "fallback_on" and m.get("health") != "fallback":
        out.add(
            ["health"],
            "fallback_on_health",
            "entering fallback gives fallback_on (ADR-0014 L27, ADR-0050 L31)",
        )
    if m.get("event") in ("health_change", "fallback_off") and m.get("health") == "fallback":
        out.add(
            ["health"],
            "fallback_health",
            "entering fallback gives fallback_on, never another event",
        )


def _items_analysis(m: Json, out: _Issues, ctx: _Context) -> None:
    want = _derive(
        lambda: analysis_key(
            cast(str, m.get("item_id")), cast(str, m.get("task")), cast(str, m.get("model_version"))
        )
    )
    if want != m.get("analysis_key"):
        out.add(
            ["analysis_key"],
            "analysis_key_mismatch",
            "analysis_key = item_id:task:model_version (ADR-0023)",
        )
    if m.get("status") == "ok":
        if m.get("result") is None:
            out.add(["result"], "ok_without_result", "an ok analysis carries its result")
        if m.get("reason") is not None:
            out.add(["reason"], "ok_with_reason", "an ok analysis carries no reason")
    if m.get("status") == "skipped":
        if m.get("reason") is None:
            out.add(["reason"], "skip_without_reason", "a skipped analysis names its reason (Q8)")
        if m.get("result") is not None:
            out.add(["result"], "skip_with_result", "a skipped analysis carries no result")
    # The person guard: a person mention is linked to a public person or dropped, never kept with
    # offsets and a surface but no entity (analysis-entities §5.3 L69).
    entities = _rec(m.get("result")).get("entities") if m.get("task") == "entities" else None
    if isinstance(entities, list):
        for i, e in enumerate(cast(list[object], entities)):
            entity = _rec(e)
            unlinked = "entity_id" in entity and entity["entity_id"] is None
            if entity.get("type") == "person_public" and unlinked:
                out.add(
                    ["result", "entities", i, "entity_id"],
                    "person_unlinked",
                    "a person mention is linked or dropped, never kept unlinked"
                    " (analysis-entities §5.3 L69)",
                )


def _item_metrics(m: Json, out: _Issues, ctx: _Context) -> None:
    _check_snake_keys(
        out, ["metrics", "reactions_by_type"], _rec(m.get("metrics")).get("reactions_by_type")
    )
    key = _str(m.get("idempotency_key")) or ""
    if _derive(lambda: item_id(key)) != m.get("item_id"):
        out.add(
            ["item_id"],
            "item_id_mismatch",
            "item_id = uuid_v5(ns_items, idempotency_key) (ADR-0006)",
        )
    try:
        parsed = parse_key(key)
    except (ContractError, TypeError):
        return
    if parsed["platform"] != m.get("platform"):
        out.add(["platform"], "key_platform", "the platform is the key's")
    if parsed["platform_id"] != m.get("platform_id"):
        out.add(["platform_id"], "key_platform_id", "the platform id is the key's")


def _deletions(m: Json, out: _Issues, ctx: _Context) -> None:
    scope = m.get("scope")
    key = (
        m.get("author_ref")
        if scope == "author"
        else m.get("client_id")
        if scope == "client"
        else m.get("source_id")
    )
    want = _derive(
        lambda: deletion_id(
            cast(str, m.get("reason")),
            cast(str, scope),
            cast(str, key),
            cast(str, m.get("mode")),
            cast(str, m.get("signal_at")),
            cast(dict[str, str | list[str]], m.get("target")),
        )
    )
    if want != m.get("deletion_id"):
        out.add(
            ["deletion_id"], "deletion_id_mismatch", "deletion_id from the helper (Q2; ADR-0035)"
        )
    if scope == "item":
        return
    prov = _rec(m.get("provenance"))
    fetch = m.get("reason") in FETCH_DELETION_REASONS
    if fetch and prov.get("route") is None:
        out.add(
            ["provenance", "route"],
            "fetch_without_route",
            "a signal that is a platform fetch names its route (F-08)",
        )
    if not fetch and prov.get("route") is not None:
        out.add(
            ["provenance", "route"],
            "route_without_fetch",
            "a signal that is no fetch has a null route (F-08)",
        )
    if prov.get("route") is None and prov.get("vendor") is not None:
        out.add(
            ["provenance", "vendor"], "vendor_without_route", "no vendor without a route (F-08)"
        )


def _article_urls(m: Json, out: _Issues, ctx: _Context) -> None:
    if _derive(lambda: url_key(cast(str, m.get("url")))) != m.get("url_key"):
        out.add(
            ["url_key"],
            "url_key_mismatch",
            "url_key = news:url:<url_hash of the normalised URL> (ADR-0036)",
        )
    canonical = m.get("canonical_url")
    if canonical is not None and _derive(lambda: url_hash(cast(str, canonical))) != m.get(
        "canonical_url_hash"
    ):
        out.add(
            ["canonical_url_hash"],
            "canonical_hash_mismatch",
            "canonical_url_hash from the one normaliser (Q9)",
        )


def _search_results(m: Json, out: _Issues, ctx: _Context) -> None:
    if _derive(lambda: canonical_url_hash(cast(str, m.get("canonical_url")))) != m.get(
        "canonical_url_hash"
    ):
        out.add(
            ["canonical_url_hash"],
            "canonical_hash_mismatch",
            "canonical_url_hash from the one normaliser (Q9)",
        )
    if _rec(m.get("provenance")).get("vendor") != m.get("engine"):
        out.add(
            ["provenance", "vendor"],
            "engine_vendor",
            "a result names its engine as provenance.vendor (ADR-0051 (c), (e))",
        )


def _crawl_policies(m: Json, out: _Issues, ctx: _Context) -> None:
    allowed = m.get("status") == "allowed"
    if allowed != (m.get("reason") is None):
        out.add(["reason"], "status_reason", "reason null exactly when allowed")
    if allowed != (m.get("crawl_allowed") is True):
        out.add(["crawl_allowed"], "status_crawl", "crawl_allowed exactly when allowed")
    asked = m.get("kind") in ("recheck", "ops_force")
    if asked and m.get("requested_by") is None:
        out.add(
            ["requested_by"], "requester_missing", "a recheck or ops_force names who asked (F-43)"
        )
    if not asked and m.get("requested_by") is not None:
        out.add(
            ["requested_by"], "requester_extra", "a refresh or first check has no requester (F-43)"
        )
    # A recheck's requester is the service whose host gate asked, never a person (F-43).
    requester = m.get("requested_by")
    is_recheck = m.get("kind") == "recheck"
    if is_recheck and isinstance(requester, str) and not matches("service", requester):
        out.add(["requested_by"], "requester_not_service", "a recheck names the service that asked")


def _news_dedup(m: Json, out: _Issues, ctx: _Context) -> None:
    if _derive(lambda: item_id(cast(str, m.get("idempotency_key")))) != m.get("item_id"):
        out.add(
            ["item_id"],
            "item_id_mismatch",
            "item_id = uuid_v5(ns_items, idempotency_key) (ADR-0006)",
        )
    if m.get("is_origin") is True and m.get("duplicate_of") is not None:
        out.add(["duplicate_of"], "origin_duplicate", "an origin duplicates nothing")
    if m.get("is_origin") is False and m.get("duplicate_of") is None:
        out.add(["duplicate_of"], "copy_without_origin", "a copy names its origin")


def _check_job_key(out: _Issues, m: Json, queue: str, kind: str) -> None:
    """A job's partition key is present: the first of its queue's key fields (ADR-0004)."""
    fields = job_key_fields(queue, kind)
    if not any(has_value(m, f) for f in fields):
        first = fields[0] if fields else "source_id"
        out.add(
            cast(IssuePath, first.split(".")),
            "missing_key",
            f"a {kind} on {queue} carries {' or '.join(fields)} (ADR-0004)",
        )


def _jobs_completed(m: Json, out: _Issues, ctx: _Context) -> None:
    queue = _str(m.get("queue")) or ""
    kind = _str(m.get("kind")) or ""
    for name, kinds in REPORT_KIND_FIELDS.items():
        if name in m and kind not in kinds:
            out.add([name], "kind_field", f"{name} is a {' and '.join(kinds)} field (ADR-0017)")
    service = _derive(lambda: queue_service(queue))
    # The rules that read registry data run as a consumer only for a service this package knows,
    # so a service a newer package adds inside the version is not refused (D-9).
    reads_registry = ctx.mode == "producer" or (service is not None and is_known_service(service))
    for name in ("paid_user_reads", "free_rereads"):
        if reads_registry and name in m and service not in X_SERVICES:
            out.add([name], "x_field", f"{name} is an X job's field (ADR-0017)")
    if "gap_unfilled" in m and not (queue == "jobs.x-recent-search" and kind == "reconciliation"):
        out.add(["gap_unfilled"], "gap_field", "gap_unfilled belongs to the X gap job (ADR-0064)")
    if "uncovered" in m and not (queue == "jobs.x-recent-search" and kind == "rotation"):
        out.add(
            ["uncovered"],
            "uncovered_field",
            "uncovered belongs to the rotation on jobs.x-recent-search (ADR-0064)",
        )
    elif m.get("uncovered") is not None and m.get("status") != "partial":
        out.add(
            ["uncovered"],
            "uncovered_status",
            "an uncovered window goes with status partial (ADR-0064)",
        )
    if reads_registry:
        _check_job_key(out, m, queue, kind)


def _job(m: Json, out: _Issues, ctx: _Context) -> None:
    if m.get("kind") == "push" and m.get("due_at") != m.get("received_at"):
        out.add(["due_at"], "push_due", "a push job is due when received (ADR-0011)")
    if (
        m.get("kind") in ("resolve", "manual_candidate")
        and m.get("platform_id") is None
        and m.get("handle") is None
        and m.get("url") is None
    ):
        out.add(
            ["platform_id"],
            "resolve_identity",
            "a resolve job names the account by id, handle or url (ADR-0032)",
        )
    queue = ctx.queue
    if queue is None:
        # A producer refuses a job whose row it cannot check (ADR-0012); a consumer checks shape.
        if ctx.mode == "producer":
            out.add([], "no_queue", "a job is validated against its queue")
        return
    kind = _str(m.get("kind")) or ""
    service = _str(_rec(m.get("producer")).get("service")) or ""
    allowed = allowed_producers(queue, kind)
    if not allowed:
        out.add(["kind"], "kind_not_on_queue", f"{queue} takes no {kind} job (ADR-0012)")
    elif service not in allowed:
        out.add(
            ["producer", "service"],
            "producer_not_allowed",
            f"the producer table lets {', '.join(allowed)} send {kind} on {queue} (ADR-0012)",
        )
    for name in required_job_fields(queue, kind, service):
        if not has_value(m, name):
            out.add(
                cast(IssuePath, name.split(".")),
                "missing_field",
                f"a {kind} on {queue} carries {name}",
            )
    _check_job_key(out, m, queue, kind)


def _original_data(message: object) -> tuple[object | None, object | None]:
    """The provenance and class of an original message, where a data message keeps them."""
    msg = _rec(message)
    if isinstance(msg.get("provenance"), dict):
        return msg.get("provenance"), msg.get("retention_class")
    env = _rec(msg.get("envelope"))
    if isinstance(env.get("provenance"), dict):
        return env.get("provenance"), env.get("retention_class")
    return None, None


_SIGNAL_SCOPES = ("author", "source", "client")


def _own_provenance(message: Json, value: object, mode: Mode) -> bool:
    """Whether an original's provenance passes the original's own type in `mode`: the signal
    provenance, whose route may be null, for an author-, source- or client-scope deletion, else the
    data one (D-1)."""
    if value is None:
        return False
    models = strict_deletions if mode == "producer" else consumer_deletions
    signal = message.get("schema") == "deletions/v1" and message.get("scope") in _SIGNAL_SCOPES
    model: type[BaseModel] = models.SignalProvenance if signal else models.Provenance
    try:
        model.model_validate(value, strict=True)
    except ValidationError:
        return False
    return True


# A dead letter copies its original's provenance when the original's own type takes it, and its
# retention_class only when that is a valid class too; otherwise neither (F-42, D-1, D-12). Null,
# absent and unknown classes count alike. The producer's strict type decides whether a copy is due;
# the mode's type judges a copy made, so a consumer tolerates a field a newer package added.
def _dlq(m: Json, out: _Issues, ctx: _Context) -> None:
    sid = ctx.schema_id
    if sid != "dlq.<service>/v1" and m.get("schema") != sid:
        out.add(["schema"], "schema_mismatch", f"the record's schema is {sid}")
    has_message, has_raw = "message" in m, "raw" in m
    if has_message and has_raw:
        out.add(["raw"], "message_and_raw", "message or raw, exactly one (Q5)")
    if not has_message and not has_raw:
        out.add(["message"], "neither_message_nor_raw", "message or raw, exactly one (Q5)")
    message = _rec(m.get("message"))
    original_provenance, original_class = _original_data(m.get("message"))
    valid_class = original_class in RETENTION_CLASSES
    copyable = _own_provenance(message, original_provenance, "producer")
    takes = _own_provenance(message, original_provenance, ctx.mode)
    if "provenance" in m and not has_message:
        out.add(
            ["provenance"],
            "provenance_without_message",
            "provenance is copied only from a parsed data message (F-42)",
        )
        return
    if "provenance" in m and not (takes and _json_equal(m["provenance"], original_provenance)):
        out.add(
            ["provenance"],
            "provenance_not_copied",
            "the copied provenance equals the message's, which its own type takes (F-42, D-1)",
        )
    if "provenance" not in m and copyable:
        out.add(
            ["provenance"],
            "provenance_not_copied",
            "a data message's provenance is copied to the top (F-42)",
        )
    if "retention_class" in m and "provenance" not in m:
        out.add(
            ["provenance"], "provenance_without_class", "retention_class travels with provenance"
        )
    elif "retention_class" in m and not (
        takes and valid_class and m["retention_class"] == original_class
    ):
        out.add(
            ["retention_class"],
            "class_not_copied",
            "the copied retention_class is the message's valid class (F-42, D-1)",
        )
    elif "retention_class" not in m and "provenance" in m and takes and valid_class:
        out.add(
            ["retention_class"],
            "class_not_copied",
            "a message's valid retention_class is copied with its provenance (F-42, D-1)",
        )


def _check_audience(out: _Issues, m: Json) -> None:
    """A client or account-manager notice names its client; an ops notice none (F-46)."""
    for_client = m.get("audience") in ("client", "account_manager")
    if for_client and m.get("client_id") is None:
        out.add(
            ["client_id"],
            "client_missing",
            "a client or account-manager notice names its client (F-46)",
        )
    if not for_client and m.get("client_id") is not None:
        out.add(["client_id"], "client_extra", "an ops notice names no client (F-46)")


def _n8n_alert(m: Json, out: _Issues, ctx: _Context) -> None:
    want = f"{_str(m.get('alert_id')) or ''}:{_str(m.get('channel')) or ''}"
    if m.get("idempotency_key") != want:
        out.add(
            ["idempotency_key"],
            "idempotency_key_mismatch",
            "idempotency_key = <alert_id>:<channel> (alert-evaluator §5.3 L69)",
        )
    _check_audience(out, m)
    details = _rec(m.get("details"))
    if details.get("subject_kind") == "source" and "source_id" not in details:
        out.add(
            ["details", "source_id"],
            "fallback_subject",
            "a source's fallback notice names the source (ADR-0021)",
        )
    if details.get("subject_kind") == "route":
        for name in ("platform", "route"):
            if name not in details:
                out.add(
                    ["details", name],
                    "fallback_subject",
                    "a route's fallback notice names the platform and route (ADR-0021)",
                )
    if "subject_kind" in details and m.get("audience") != "ops":
        out.add(
            ["audience"],
            "fallback_audience",
            "an automatic-fallback notice goes to ops (ADR-0021 L58)",
        )
    if m.get("audience") not in ("client", "account_manager"):
        return
    # The government rule (alert-evaluator §6.2 L102; F-50) needs the client's type, which the
    # producer passes; a producer that does not fails closed (CONVENTIONS v1.1 L84).
    if ctx.client_type is None:
        if ctx.mode == "producer":
            out.add([], "no_client_type", "a client's alert is validated with the client's type")
        return
    if ctx.client_type != "government":
        return
    # A government client's alert names its keyword or request only, so a subject field added
    # inside the version is refused too (F-50; note 12).
    for name in _rec(m.get("subject")):
        if name not in ("keyword_id", "request_id"):
            out.add(
                ["subject", name],
                "government_subject",
                f"a government client's alert names no {name} (F-50)",
            )
    scope = _rec(details.get("scope"))
    if "level" in scope and scope["level"] != "keyword":
        out.add(
            ["details", "scope", "level"],
            "government_scope",
            "a government client's alert is at the keyword level (alert-evaluator §6.2 L102)",
        )
    for name in ("source", "platform"):
        if name in scope:
            out.add(
                ["details", "scope", name],
                "government_scope",
                f"a government client's alert names no {name} (alert-evaluator §6.2 L102)",
            )
    if "rule_type" in details and details["rule_type"] not in GOVERNMENT_ALERT_RULE_TYPES:
        out.add(
            ["details", "rule_type"],
            "government_rule_type",
            "a government client receives the keyword-level rule types only"
            " (alert-evaluator §5.3 C L65)",
        )


def _n8n_card(m: Json, out: _Issues, ctx: _Context) -> None:
    want = f"{_str(m.get('card_id')) or ''}:{_str(m.get('channel')) or ''}"
    if m.get("idempotency_key") != want:
        out.add(
            ["idempotency_key"],
            "idempotency_key_mismatch",
            "idempotency_key = <card_id>:<channel> (F-23)",
        )
    _check_audience(out, m)
    # The subject key is the candidate's or the source's; the reference is the decision's or the
    # request's.
    subject = _rec(m.get("subject"))
    key = _str(subject.get("candidate_key")) or _str(subject.get("source_id"))
    ref = _str(subject.get("decision_id")) or _str(subject.get("request_id"))
    if key is None or ref is None:
        out.add(
            ["subject"],
            "card_subject",
            "a card's subject names a candidate or source, and a decision or request (F-47)",
        )
        return
    if _derive(lambda: card_id(_str(m.get("card_type")) or "", key, ref)) != m.get("card_id"):
        out.add(
            ["card_id"],
            "card_id_mismatch",
            "card_id = uuid_v5(ns_cards, <card_type>:<subject key>:<ref>) (F-47)",
        )


RULES: dict[str, Rule] = {
    "raw.items/v1": _raw_items,
    "items.normalized/v1": _items_normalized,
    "item.hits/v1": _item_hits,
    "discovery.hits/v1": _discovery_hits,
    "poster.profiles/v1": _poster_profiles,
    "registry.decisions/v1": _registry_decisions,
    "source.events/v1": _source_events,
    "items.analysis/v1": _items_analysis,
    "item.metrics/v1": _item_metrics,
    "deletions/v1": _deletions,
    "article.urls/v1": _article_urls,
    "search.results/v1": _search_results,
    "crawl.policies/v1": _crawl_policies,
    "news.dedup/v1": _news_dedup,
    "jobs.completed/v1": _jobs_completed,
    "job/v1": _job,
    "dlq.<service>/v1": _dlq,
    "n8n.alert/v1": _n8n_alert,
    "n8n.card/v1": _n8n_card,
}

CONTROL = {"source.events/v1", "jobs.completed/v1", "job/v1", "n8n.alert/v1", "n8n.card/v1"}


# --- registry checks (producer mode) ------------------------------------------------------------


def _check_vendor(out: _Issues, path: IssuePath, route: object, vendor: object) -> None:
    if not isinstance(route, str):
        return
    if not is_known_vendor(route, cast(str | None, vendor)):
        out.add(path, "unknown_vendor", f"{vendor} is no {route} vendor of the registry (ADR-0051)")


def _check_pair(out: _Issues, path: IssuePath, holder: Json) -> None:
    """A (route, vendor) pair a part of the message names: with its route, the vendor is the
    registry's for that route; without it, a vendor it names is on one of the registry's lists
    (note 11)."""
    if "vendor" not in holder:
        return
    vendor = holder["vendor"]
    if "route" in holder:
        _check_vendor(out, path, holder["route"], vendor)
    elif isinstance(vendor, str) and not is_listed_vendor(vendor):
        out.add(path, "unknown_vendor", f"{vendor} is no vendor of the registry")


def _check_provenance(out: _Issues, provenance: object, prefix: IssuePath) -> None:
    if not isinstance(provenance, dict):
        return
    prov = cast(Json, provenance)
    service = _str(prov.get("service"))
    if service is not None and not is_known_service(service):
        out.add(
            [*prefix, "service"], "unknown_service", f"{service} is no service of the index (Q1)"
        )
    if prov.get("route") is not None:
        _check_vendor(out, [*prefix, "vendor"], prov.get("route"), prov.get("vendor"))


def _check_decision_row(out: _Issues, m: Json, service: str) -> None:
    subject = next((s for s in SUBJECTS if s in m), None)
    if subject is None:
        return
    decision = _str(m.get("decision")) or ""
    query: DecisionQuery = {"decision": decision, "subject": subject, "reason": m.get("reason")}
    block = _rec(m.get(decision))
    health = _str(block.get("health"))
    if health is not None:
        query["health"] = health
    rule_hit = block.get("rule_hit")
    query["rule_hit"] = rule_hit if type(rule_hit) is int else None
    row = decision_row(query, service)
    if row is None:
        out.add(
            ["producer", "service"],
            "decision_not_allowed",
            f"no decision row lets {service} send this {decision} (ADR-0012, ADR-0013)",
        )
        return
    if row["provenance"] == "required" and "provenance" not in m:
        out.add(
            ["provenance"],
            "provenance_required",
            f"this {decision} reports a fetch and carries provenance (F-14)",
        )
    if row["provenance"] == "refused" and "provenance" in m:
        out.add(
            ["provenance"],
            "provenance_refused",
            f"this {decision} carries requested_by and no provenance (F-14)",
        )


# The topics whose requester may name a service or a person (Q18), on source events the actor.
_REQUESTER_TOPICS = (
    "registry.decisions/v1",
    "source.events/v1",
    "deletions/v1",
    "job/v1",
    "crawl.policies/v1",
)


def _registry_checks(out: _Issues, sid: str, m: Json) -> None:
    raw = sid == "raw.items/v1"
    head = _rec(m.get("envelope")) if raw else m
    prefix: IssuePath = ["envelope"] if raw else []
    service = _str(_rec(head.get("producer")).get("service")) or ""
    if not is_known_service(service):
        out.add(
            [*prefix, "producer", "service"],
            "unknown_service",
            f"{service} is no service of the index (Q1)",
        )
    elif sid == "registry.decisions/v1":
        _check_decision_row(out, m, service)
    elif sid != "job/v1" and not sid.startswith("n8n."):
        # A job's producers are its queue's row; any service sends n8n notices (ADR-0067).
        target = (_str(m.get("schema")) or sid) if sid == "dlq.<service>/v1" else sid
        allowed = is_allowed_topic_writer(
            target,
            service,
            kind=_str(head.get("kind")) if raw else None,
            queue=_str(m.get("queue")) or "" if sid == "jobs.completed/v1" else None,
        )
        if not allowed:
            out.add(
                [*prefix, "producer", "service"],
                "writer_not_allowed",
                f"{service} does not write {target}",
            )
    for condition in writer_conditions(sid, service):
        if get_path(m, condition["field"]) != condition["equals"]:
            out.add(
                [*prefix, *condition["field"].split(".")],
                "writer_condition",
                f"{service} writes {sid} only with {condition['field']} = {condition['equals']}",
            )
    _check_provenance(out, head.get("provenance"), [*prefix, "provenance"])
    # A requester, checked as producer.service is (F-09). A recheck's is a service by definition,
    # the service whose host gate asked (ADR-0040; F-43). Any other names a service when it matches
    # the service pattern, which D3's person reference never does; a person stays unchecked (Q18).
    where = "actor" if sid == "source.events/v1" else "requested_by"
    if sid in _REQUESTER_TOPICS:
        is_recheck = sid in ("job/v1", "crawl.policies/v1") and m.get("kind") == "recheck"
        requester = _str(m.get(where))
        named = is_recheck or (requester is not None and matches("service", requester))
        if named and not is_known_service(requester or ""):
            out.add(
                [where], "unknown_service", f"{requester or ''} is no service of the index (Q1)"
            )
    # Every other (route, vendor) pair a message names.
    if sid == "poster.profiles/v1" and m.get("route") is not None:
        _check_vendor(out, ["vendor"], m.get("route"), m.get("vendor"))
    if sid == "registry.decisions/v1":
        decision = _str(m.get("decision")) or ""
        block = _rec(m.get(decision))
        if "platform" in m:
            _check_vendor(out, ["vendor"], m.get("route"), m.get("vendor"))
            fallback = block.get("fallback")
            if isinstance(fallback, dict):
                fb = cast(Json, fallback)
                _check_vendor(
                    out, ["health_change", "fallback", "vendor"], fb.get("route"), fb.get("vendor")
                )
        _check_pair(out, [decision, "source", "vendor"], _rec(block.get("source")))
    if sid == "source.events/v1":
        _check_vendor(out, ["vendor"], m.get("route"), m.get("vendor"))
        _check_pair(out, ["previous", "vendor"], _rec(m.get("previous")))
    if sid == "n8n.alert/v1":
        _check_pair(out, ["subject", "vendor"], _rec(m.get("subject")))
        _check_pair(out, ["details", "vendor"], _rec(m.get("details")))
    # A dead letter sits in its consumer's own dlq.<service> topic (CONVENTIONS L41).
    if sid == "dlq.<service>/v1":
        consumer = _str(_rec(m.get("consumer")).get("service"))
        if consumer is not None and not is_known_service(consumer):
            out.add(
                ["consumer", "service"],
                "unknown_service",
                f"{consumer} is no service of the index (Q1)",
            )
        elif consumer is not None and consumer != dlq_service(_str(m.get("schema")) or ""):
            out.add(
                ["consumer", "service"],
                "consumer_mismatch",
                f"a dead letter of {consumer} is in dlq.{consumer}/v1 (CONVENTIONS L41)",
            )
    if raw:
        kind = _str(head.get("kind")) or ""
        declared = declared_context_keys(service, kind)
        context = _rec(head.get("context"))
        for key in context:
            if key not in declared["keys"]:
                out.add(
                    ["envelope", "context", key],
                    "undeclared_context_key",
                    f"{service} declares no context key {key} (ADR-0005)",
                )
        for key in declared["required"]:
            if key not in context:
                out.add(
                    ["envelope", "context", key],
                    "missing_context_key",
                    f"a {kind} record from {service} carries context.{key}",
                )
    if sid == "poster.profiles/v1" and isinstance(m.get("extras"), dict):
        resolver = _str(_rec(m.get("provenance")).get("service")) or ""
        keys = declared_extras_keys(resolver) or []
        for key in _rec(m.get("extras")):
            if key not in keys:
                out.add(
                    ["extras", key],
                    "undeclared_extras_key",
                    f"{resolver} declares no extras key {key} (ADR-0033)",
                )


# --- the entry point ----------------------------------------------------------------------------


def _model(schema_id: str, mode: Mode) -> type[BaseModel] | None:
    entry = catalogue_entry(schema_id)
    if entry is None:
        return None
    variant = "strict" if mode == "producer" else "consumer"
    module = importlib.import_module(f"listening_contracts.models.{variant}.{entry['module']}")
    return cast(type[BaseModel], getattr(module, entry["title"]))


def validate(
    schema_id: str,
    value: object,
    mode: Mode = "producer",
    *,
    queue: str | None = None,
    client_type: ClientType | None = None,
) -> ValidationResult:
    """Validates a message of `schema_id` (a catalogue id, or a concrete `dlq.<service>/v1`) as a
    producer (strict, with the registry checks) or a consumer (tolerant of unknown fields)."""
    model = _model(schema_id, mode)
    if model is None:
        return ValidationResult(
            False,
            issues=[
                {"path": ["schema"], "code": "unknown_schema", "message": f"no schema {schema_id}"}
            ],
        )
    out = _Issues()
    message = _as_json(value, [], out)
    if out.list:
        return ValidationResult(False, issues=out.list)
    try:
        parsed = model.model_validate(message, strict=True)
    except ValidationError as error:
        return ValidationResult(False, issues=_schema_issues(schema_id, message, error.errors()))
    dumped: object = parsed.model_dump(mode="json", by_alias=True)
    _constant_types(dumped, message, out)
    if out.list:
        return ValidationResult(False, issues=out.list)
    sid = catalogue_id(schema_id)
    # The rules read the message as sent: in consumer mode it may hold fields the schema drops.
    raw = _rec(message)
    if sid in CONTROL:
        _refuse_provenance(out, raw)
    RULES[sid](raw, out, _Context(schema_id, mode, queue, client_type))
    if not out.list and mode == "producer":
        _registry_checks(out, sid, raw)
    if out.list:
        return ValidationResult(False, issues=out.list)
    return ValidationResult(True, dumped)
