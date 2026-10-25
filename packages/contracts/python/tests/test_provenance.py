"""A18: provenance on data messages, none on control messages, and the deletion, decision and DLQ
cases (ADR-0003; F-08, F-14, F-42)."""

import json
from collections.abc import Callable
from typing import Any, Literal

from listening_contracts.registries import DecisionQuery, decision_row, decision_rows
from listening_contracts.validate import ValidationResult, validate
from listening_contracts.versions import CATALOGUE
from listening_contracts.vocabulary import VOCABULARY

from conftest import fixture, fixtures, schema_dirs, schema_id_of

DIR_OF = {schema_id_of(d): d for d in schema_dirs()}
SAMPLE = {
    "deletions/v1": "prd-retention-purger.json",
    "registry.decisions/v1": "prd-qualifier.json",
}
SUBJECTS = ("candidate_key", "author_ref", "source_id", "keyword_id", "platform")
MODES: tuple[Literal["producer"], Literal["consumer"]] = ("producer", "consumer")
RETENTION_CLASSES = VOCABULARY["RETENTION_CLASSES"]
# The author-, source- and client-scope deletions, whose provenance is the signal's (F-08).
NON_ITEM_DELETIONS = (
    "author-request.json",
    "author-x-compliance.json",
    "client-offboarding.json",
    "client-request.json",
    "source-authorization-revoked.json",
)


def fails_at(result: ValidationResult, path: list[str | int]) -> bool:
    return not result.ok and path in [i["path"] for i in result.issues]


def dead_letter(
    stage: str, service: str, topic: str, message: dict[str, Any], top: dict[str, Any]
) -> dict[str, Any]:
    """A dead letter of `message` on `topic`, written by `service`, with the top-level fields of
    `top`."""
    base = "consume-data-message.json" if stage == "consume" else "produce-chunk.json"
    r: dict[str, Any] = fixture("dlq/v1", "valid", base).copy()
    r.pop("provenance", None)
    r.pop("retention_class", None)
    r["schema"] = f"dlq.{service}/v1"
    r["producer"]["service"] = service
    r["consumer"]["service"] = service
    r["original"].update(
        {"topic": topic, "schema": message["schema"], "message_id": message["message_id"]}
    )
    return {**r, "message": message, **top}


def dead_letter_of_item(
    change: Callable[[dict[str, Any]], None],
    top: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    """store-writer's dead letter of its items.normalized original, changed by `change`."""
    message: dict[str, Any] = fixture(
        "items.normalized/v1", "valid", "prd-normalize-item.json"
    ).copy()
    change(message)
    return dead_letter("consume", "store-writer", "items.normalized", message, top(message))


def copy_both(m: dict[str, Any]) -> dict[str, Any]:
    return {"provenance": m["provenance"], "retention_class": m["retention_class"]}


def copy_nothing(m: dict[str, Any]) -> dict[str, Any]:
    return {}


def test_every_data_schema_requires_provenance_and_retention_class() -> None:
    for entry in (e for e in CATALOGUE if e["class"] == "data"):
        sid = entry["id"]
        directory = DIR_OF[sid]
        sample = SAMPLE.get(sid)
        f = fixture(directory, "valid", sample) if sample else fixtures(directory, "valid")[0]
        prefix: list[str | int] = ["envelope"] if sid == "raw.items/v1" else []
        for name in ("provenance", "retention_class"):
            value = f.copy()
            del (value["envelope"] if prefix else value)[name]
            assert fails_at(validate(sid, value, "producer", **f.options), [*prefix, name]), (
                f"{sid} {name}"
            )


def test_no_control_schema_accepts_provenance() -> None:
    provenance = {
        "route": "green",
        "vendor": None,
        "service": "fb-page-feed-poller",
        "fetched_at": "2026-10-06T09:13:58Z",
    }
    for sid in ("source.events/v1", "jobs.completed/v1", "job/v1"):
        f = fixtures(DIR_OF[sid], "valid")[0]
        value = {**f.copy(), "provenance": provenance}
        for mode in ("producer", "consumer"):
            assert fails_at(validate(sid, value, mode, **f.options), ["provenance"]), (sid, mode)


def test_a_non_item_deletion_rejects_retention_class() -> None:
    for file in (
        "author-request.json",
        "source-authorization-revoked.json",
        "client-offboarding.json",
    ):
        value = {**fixture("deletions/v1", "valid", file).copy(), "retention_class": "x_24h_sync"}
        assert fails_at(validate("deletions/v1", value), ["retention_class"]), file


def test_a_non_item_deletion_whose_signal_is_no_fetch_accepts_null_route_and_vendor() -> None:
    for file in ("author-request.json", "client-offboarding.json", "client-request.json"):
        value = fixture("deletions/v1", "valid", file).value
        assert [value["provenance"]["route"], value["provenance"]["vendor"]] == [None, None]
        assert validate("deletions/v1", value).ok, file
    revoked = fixture("deletions/v1", "valid", "source-authorization-revoked.json").copy()
    revoked["provenance"]["route"] = None
    assert fails_at(validate("deletions/v1", revoked), ["provenance", "route"])


def test_each_registry_decisions_row_requires_or_refuses_provenance_as_the_rows_say() -> None:
    rows = decision_rows()
    exercised: set[int] = set()
    for f in fixtures("registry.decisions/v1", "valid"):
        m: dict[str, Any] = f.value
        subject = next(s for s in SUBJECTS if s in m)
        block: dict[str, Any] = m.get(m["decision"]) or {}
        query: DecisionQuery = {
            "decision": m["decision"],
            "subject": subject,
            "reason": m["reason"],
        }
        if "health" in block:
            query["health"] = block["health"]
        row = decision_row(query, m["producer"]["service"])
        assert row is not None, f.name
        exercised.add(next(i for i, r in enumerate(rows) if json.dumps(r) == json.dumps(row)))
        without = f.copy()
        without.pop("provenance", None)
        without.pop("retention_class", None)
        with_it = {
            **f.copy(),
            "provenance": {
                "route": "green",
                "vendor": None,
                "service": "ig-account-resolver",
                "fetched_at": "2026-10-06T10:13:58Z",
            },
            "retention_class": "meta_on_request",
        }
        r1 = validate("registry.decisions/v1", without)
        r2 = validate("registry.decisions/v1", with_it)
        if row["provenance"] == "required":
            assert fails_at(r1, ["provenance"]), f.name
        if row["provenance"] == "refused":
            assert fails_at(r2, ["provenance"]), f.name
        if row["provenance"] == "optional":
            assert [r1.ok, r2.ok] == [True, True], f.name
    unexercised = [r["from"] for i, r in enumerate(rows) if i not in exercised]
    assert unexercised == [], "every decision row has a valid fixture"


def test_the_n8n_notices_accept_no_provenance() -> None:
    provenance = {
        "route": "green",
        "vendor": None,
        "service": "quota-governor",
        "fetched_at": "2026-10-04T08:12:00Z",
    }
    for sid, file in (
        ("n8n.alert/v1", "facts-budget.json"),
        ("n8n.card/v1", "qualifier-review.json"),
    ):
        f = fixture(sid, "valid", file)
        for mode in ("producer", "consumer"):
            value = {**f.copy(), "provenance": provenance}
            assert fails_at(validate(sid, value, mode, **f.options), ["provenance"]), (sid, mode)


def test_an_n8n_alert_accepts_no_item_text_author_ref_or_handle() -> None:
    f = fixture("n8n.alert/v1", "valid", "facts-budget.json")
    cases: list[tuple[list[str | int], str]] = [
        (["text"], "النت منقطع"),
        (["author_ref"], "a" * 64),
        (["subject", "handle"], "abuali_basra"),
    ]
    for path, v in cases:
        value = f.copy()
        holder = value["subject"] if len(path) == 2 else value
        holder[path[-1]] = v
        assert fails_at(validate("n8n.alert/v1", value), path), path


def test_a_dead_letter_copies_provenance_and_retention_class_from_a_parsed_data_message() -> None:
    f = fixture("dlq/v1", "valid", "consume-data-message.json")
    assert validate("dlq.<service>/v1", f.value).ok
    changed = f.copy()
    changed["provenance"]["service"] = "x-recent-search"
    assert fails_at(validate("dlq.<service>/v1", changed), ["provenance"])
    raw = fixture("dlq/v1", "valid", "consume-unparsed.json")
    assert "provenance" not in raw.value
    assert validate("dlq.<service>/v1", raw.value).ok


def test_a_dead_letter_of_a_non_item_deletion_copies_its_provenance_and_no_class() -> None:
    """An author-, source- or client-scope deletion's dead letter (F-42, F-08)."""
    for file in NON_ITEM_DELETIONS:
        deletion: dict[str, Any] = fixture("deletions/v1", "valid", file).copy()
        provenance = deletion["provenance"]
        for stage in ("consume", "produce"):
            # deletion-propagator consumes the deletions; the producing service dead-letters a
            # failed send.
            service = (
                "deletion-propagator" if stage == "consume" else deletion["producer"]["service"]
            )
            sid = f"dlq.{service}/v1"

            def record(
                top: dict[str, Any],
                stage: str = stage,
                service: str = service,
                deletion: dict[str, Any] = deletion,
            ) -> Any:
                return dead_letter(stage, service, "deletions", deletion, top)

            for mode in MODES:
                name = f"{file} {stage} {mode}"
                faithful = validate(sid, record({"provenance": provenance}), mode)
                assert faithful.issues == [], name
                for cls in RETENTION_CLASSES:
                    with_class = record({"provenance": provenance, "retention_class": cls})
                    assert fails_at(validate(sid, with_class, mode), ["retention_class"]), (
                        name,
                        cls,
                    )
                assert fails_at(validate(sid, record({}), mode), ["provenance"]), name


def test_never_raises_on_a_dead_letter_whose_original_holds_a_lone_surrogate_or_inf() -> None:
    """validate() returns issues and never raises on a dead letter whose original's provenance
    holds a lone surrogate or a non-finite number (finding 4)."""
    for key, odd in (("note", "\ud800"), ("x", float("inf"))):

        def four_fields(m: dict[str, Any], key: str = key) -> dict[str, Any]:
            rest = {k: v for k, v in m["provenance"].items() if k != key}
            return {"provenance": rest, "retention_class": m["retention_class"]}

        def change(m: dict[str, Any], key: str = key, odd: object = odd) -> None:
            m["provenance"][key] = odd

        variants: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
            "copies the four fields": four_fields,
            "copies the whole provenance": copy_both,
            "copies nothing": copy_nothing,
        }
        for label, top in variants.items():
            record = dead_letter_of_item(change, top)
            for mode in MODES:
                result = validate("dlq.store-writer/v1", record, mode)  # never raises
                # A copy of the four fields is no copy of the original's provenance.
                if label == "copies the four fields":
                    assert not result.ok, (key, mode)


def test_a_dead_letter_copies_nothing_from_an_original_whose_provenance_fails_its_own_type() -> (
    None
):
    def red(m: dict[str, Any]) -> None:
        m["provenance"]["route"] = "RED"

    def null_route(m: dict[str, Any]) -> None:
        m["provenance"]["route"] = None

    for label, change in (
        ("route RED", red),
        ("a null route on an items.normalized original", null_route),
    ):
        for mode in MODES:
            copied = validate("dlq.store-writer/v1", dead_letter_of_item(change, copy_both), mode)
            assert fails_at(copied, ["provenance"]) or fails_at(copied, ["provenance", "route"]), (
                label
            )
            neither = validate(
                "dlq.store-writer/v1", dead_letter_of_item(change, copy_nothing), mode
            )
            assert neither.issues == [], (label, mode)

    # An extra key: the producer's strict type refuses the copy; a consumer tolerates the unknown
    # key, so it accepts the copy as well as a record that copies nothing.
    def extra(m: dict[str, Any]) -> None:
        m["provenance"]["note"] = "a field this package does not know"

    producer = validate("dlq.store-writer/v1", dead_letter_of_item(extra, copy_both), "producer")
    assert not producer.ok
    assert any(i["path"][0] == "provenance" for i in producer.issues)
    consumer = validate("dlq.store-writer/v1", dead_letter_of_item(extra, copy_both), "consumer")
    assert consumer.issues == []
    for mode in MODES:
        neither = validate("dlq.store-writer/v1", dead_letter_of_item(extra, copy_nothing), mode)
        assert neither.issues == [], mode


def test_an_original_with_a_null_absent_or_unknown_class_gives_a_record_with_no_class() -> None:
    """The record copies the provenance and no class, in both languages (D-1)."""

    def null(m: dict[str, Any]) -> None:
        m["retention_class"] = None

    def absent(m: dict[str, Any]) -> None:
        del m["retention_class"]

    def unknown(m: dict[str, Any]) -> None:
        m["retention_class"] = "forever"

    for label, change in (("null", null), ("absent", absent), ("unknown", unknown)):
        for mode in MODES:
            provenance_only = dead_letter_of_item(change, lambda m: {"provenance": m["provenance"]})
            result = validate("dlq.store-writer/v1", provenance_only, mode)
            assert result.issues == [], (label, mode)
            for cls in RETENTION_CLASSES:

                def top(m: dict[str, Any], cls: str = cls) -> dict[str, Any]:
                    return {"provenance": m["provenance"], "retention_class": cls}

                with_class = dead_letter_of_item(change, top)
                assert fails_at(
                    validate("dlq.store-writer/v1", with_class, mode), ["retention_class"]
                ), (
                    label,
                    cls,
                    mode,
                )


def test_validates_control_set_is_the_catalogues_control_ids_except_the_dead_letter() -> None:
    provenance = {
        "route": "green",
        "vendor": None,
        "service": "fb-page-feed-poller",
        "fetched_at": "2026-10-06T09:13:58Z",
    }
    # The schemas whose control rule refuses a provenance (a dead letter's copy rule refuses a
    # provenance that is not its original's, with another code).
    refuses: list[str] = []
    for entry in (e for e in CATALOGUE if e["class"] == "control"):
        f = fixtures(DIR_OF[entry["id"]], "valid")[0]
        result = validate(
            entry["id"], {**f.copy(), "provenance": provenance}, "consumer", **f.options
        )
        if any(i["code"] == "provenance_refused" for i in result.issues):
            refuses.append(entry["id"])
    assert refuses == [
        e["id"] for e in CATALOGUE if e["class"] == "control" and e["id"] != "dlq.<service>/v1"
    ]
    # The dead letter, classed control, still copies a data original's provenance and class.
    dlq = fixture("dlq/v1", "valid", "consume-data-message.json")
    assert "provenance" in dlq.value
    assert validate("dlq.<service>/v1", dlq.value, "consumer").ok
