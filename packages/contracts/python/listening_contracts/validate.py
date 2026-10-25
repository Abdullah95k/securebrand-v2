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
   consumer's job wrapper dead-letters a job with no row (ADR-0012).

Layer 3 runs only when layer 2 found nothing, so an issue names the first rule broken. The codes of
layer 1 are the validator's own (Pydantic's here, Zod's in TypeScript); the paths and the codes of
layers 2 and 3 are the same in both languages.
"""

import importlib
import json
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict, cast

from pydantic import BaseModel, ValidationError

from listening_contracts.errors import ContractError
from listening_contracts.keys import (
    analysis_key,
    deletion_id,
    hit_id,
    idempotency_key,
    item_id,
    parse_candidate_key,
    parse_key,
    parse_raw_ref,
)
from listening_contracts.patterns import matches
from listening_contracts.registries import (
    PLATFORM_GROUPS,
    DecisionQuery,
    allowed_producers,
    decision_row,
    declared_context_keys,
    declared_extras_keys,
    get_path,
    has_value,
    is_allowed_topic_writer,
    is_known_service,
    is_known_vendor,
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
X_SERVICES = PLATFORM_GROUPS.get("x", ())


def _rec(value: object) -> Json:
    return cast(Json, value) if isinstance(value, dict) else {}


def _str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _same_json(a: object, b: object) -> bool:
    return json.dumps(a, sort_keys=True, ensure_ascii=False) == json.dumps(
        b, sort_keys=True, ensure_ascii=False
    )


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


def _as_json(value: object, path: IssuePath, out: _Issues) -> object:
    """The value as JavaScript reads JSON: an integral float is an integer; NaN and the infinities
    are not JSON."""
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            out.add(path, "not_json", "a number is finite")
            return value
        return int(value) if value.is_integer() else value
    if isinstance(value, list):
        return [_as_json(v, [*path, i], out) for i, v in enumerate(cast(list[object], value))]
    if isinstance(value, dict):
        return {k: _as_json(v, [*path, k], out) for k, v in cast(dict[str, object], value).items()}
    out.add(path, "not_json", f"{type(value).__name__} is not a JSON value")
    return value


# --- Pydantic issues ----------------------------------------------------------------------------


def _path(value: object, loc: tuple[int | str, ...]) -> IssuePath:
    """A Pydantic location as a path into the message: walk the value along it, dropping the
    union branch labels Pydantic inserts (a branch's class name, a tag), which name no key of the
    value."""
    out: IssuePath = []
    current: object = value
    last = len(loc) - 1
    for i, step in enumerate(loc):
        if isinstance(current, dict):
            node = cast(dict[str, object], current)
            if isinstance(step, str) and step in node:
                out.append(step)
                current = node[step]
            elif i == last and isinstance(step, str):
                out.append(step)  # a missing or an unknown field
            continue  # a branch label
        if isinstance(current, list) and isinstance(step, int):
            items = cast(list[object], current)
            out.append(step)
            current = items[step] if 0 <= step < len(items) else None
    return out


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
    for name in ("paid_user_reads", "free_rereads"):
        if name in m and service not in X_SERVICES:
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


def _dlq(m: Json, out: _Issues, ctx: _Context) -> None:
    sid = ctx.schema_id
    if sid != "dlq.<service>/v1" and m.get("schema") != sid:
        out.add(["schema"], "schema_mismatch", f"the record's schema is {sid}")
    has_message, has_raw = "message" in m, "raw" in m
    if has_message and has_raw:
        out.add(["raw"], "message_and_raw", "message or raw, exactly one (Q5)")
    if not has_message and not has_raw:
        out.add(["message"], "neither_message_nor_raw", "message or raw, exactly one (Q5)")
    original_provenance, original_class = _original_data(m.get("message"))
    if "provenance" in m:
        if not has_message:
            out.add(
                ["provenance"],
                "provenance_without_message",
                "provenance is copied only from a parsed data message (F-42)",
            )
        elif original_provenance is None or not _same_json(m["provenance"], original_provenance):
            out.add(
                ["provenance"],
                "provenance_not_copied",
                "the copied provenance equals the message's (F-42)",
            )
    elif original_provenance is not None:
        out.add(
            ["provenance"],
            "provenance_not_copied",
            "a data message's provenance is copied to the top (F-42)",
        )
    _check_pairing(out, m)
    if (
        "retention_class" in m
        and original_class is not None
        and m["retention_class"] != original_class
    ):
        out.add(
            ["retention_class"],
            "class_not_copied",
            "the copied retention_class equals the message's (F-42)",
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
}

CONTROL = {"source.events/v1", "jobs.completed/v1", "job/v1"}


# --- registry checks (producer mode) ------------------------------------------------------------


def _check_vendor(out: _Issues, path: IssuePath, route: object, vendor: object) -> None:
    if not isinstance(route, str):
        return
    if not is_known_vendor(route, cast(str | None, vendor)):
        out.add(path, "unknown_vendor", f"{vendor} is no {route} vendor of the registry (ADR-0051)")


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
    health = _str(_rec(m.get(decision)).get("health"))
    if health is not None:
        query["health"] = health
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
    elif sid != "job/v1":
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
        source = _rec(block.get("source"))
        if "route" in source and "vendor" in source:
            _check_vendor(
                out, [decision, "source", "vendor"], source.get("route"), source.get("vendor")
            )
    if sid == "source.events/v1":
        _check_vendor(out, ["vendor"], m.get("route"), m.get("vendor"))
        previous = _rec(m.get("previous"))
        if "route" in previous and "vendor" in previous:
            _check_vendor(
                out, ["previous", "vendor"], previous.get("route"), previous.get("vendor")
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
        issues: list[ValidationIssue] = [
            {"path": _path(message, e["loc"]), "code": e["type"], "message": e["msg"]}
            for e in error.errors()
        ]
        return ValidationResult(False, issues=issues)
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
    return ValidationResult(True, parsed.model_dump(mode="json", by_alias=True))
