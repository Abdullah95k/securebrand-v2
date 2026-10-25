"""A21: job/v1, one envelope with a closed kind list (ADR-0011, ADR-0057, ADR-0060, ADR-0064,
ADR-0065)."""

from listening_contracts.validate import ValidationResult, validate
from listening_contracts.vocabulary import JOB_KINDS

from conftest import fixture, fixtures

ID = "job/v1"
VALID = fixtures(ID, "valid")


def fails_at(result: ValidationResult, path: list[str | int]) -> bool:
    return not result.ok and path in [i["path"] for i in result.issues]


def test_accepts_every_kind_with_its_declared_fields() -> None:
    for kind in JOB_KINDS:
        own = [f for f in VALID if f.value["kind"] == kind]
        assert own, f"a valid {kind} job"
        for f in own:
            assert "queue" in f.options, f"{f.name} names its queue"
            assert validate(ID, f.value, "producer", **f.options).issues == [], f.name


def test_rejects_a_job_carrying_priority_route_or_vendor() -> None:
    f = fixture(ID, "valid", "rotation.json")
    for name, value in (("priority", 1), ("route", "green"), ("vendor", None)):
        assert fails_at(validate(ID, {**f.copy(), name: value}, "producer", **f.options), [name])


def test_rejects_a_reason_used_as_the_type() -> None:
    f = fixture(ID, "valid", "prd-backfill-orchestrator.json")
    for reason in ("first_run", "gap_backfill", "seed", "weekly", "refresh_24h", "health"):
        value = {**f.copy(), "kind": reason}
        assert fails_at(validate(ID, value, "producer", **f.options), ["kind"]), reason


def test_rejects_an_analyze_job_carrying_item_or_provenance() -> None:
    f = fixture(ID, "valid", "analyze-priority.json")
    item = {**f.copy(), "item": {"text": "النت منقطع"}}
    assert fails_at(validate(ID, item, "producer", **f.options), ["item"])
    prov = {
        **f.copy(),
        "provenance": {
            "route": "green",
            "vendor": None,
            "service": "fb-page-feed-poller",
            "fetched_at": "2026-10-06T09:13:58Z",
        },
    }
    for mode in ("producer", "consumer"):
        assert fails_at(validate(ID, prov, mode, **f.options), ["provenance"]), mode


def test_checks_the_producer_table_in_both_modes_when_the_queue_is_given() -> None:
    f = fixture(ID, "valid", "rotation.json")
    other = f.copy()
    other["producer"]["service"] = "fb-backfill"
    for mode in ("producer", "consumer"):
        assert fails_at(validate(ID, other, mode, **f.options), ["producer", "service"]), mode
    # Without the queue the row cannot be found: a producer refuses, a consumer checks the shape.
    assert validate(ID, other, "consumer").ok


def test_refuses_a_job_in_producer_mode_without_its_queue_whose_row_it_cannot_check() -> None:
    f = fixture(ID, "valid", "rotation.json")
    result = validate(ID, f.value, "producer")
    assert not result.ok
    assert [i["code"] for i in result.issues] == ["no_queue"]
    assert validate(ID, f.value, "consumer").ok
