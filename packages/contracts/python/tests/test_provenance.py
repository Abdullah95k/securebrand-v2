"""A18: provenance on data messages, none on control messages, and the deletion, decision and DLQ
cases (ADR-0003; F-08, F-14, F-42)."""

import json
from typing import Any

from listening_contracts.registries import DecisionQuery, decision_row, decision_rows
from listening_contracts.validate import ValidationResult, validate
from listening_contracts.versions import CATALOGUE

from conftest import fixture, fixtures, schema_dirs, schema_id_of

DIR_OF = {schema_id_of(d): d for d in schema_dirs()}
SAMPLE = {
    "deletions/v1": "prd-retention-purger.json",
    "registry.decisions/v1": "prd-qualifier.json",
}
SUBJECTS = ("candidate_key", "author_ref", "source_id", "keyword_id", "platform")


def fails_at(result: ValidationResult, path: list[str | int]) -> bool:
    return not result.ok and path in [i["path"] for i in result.issues]


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
