"""jobs.completed/v1's rules that read registry data (note 11, D-9): always in producer mode, and in
consumer mode only for a service the package knows, so a report from a service that a newer
package adds inside the version is not refused."""

from typing import Any

from listening_contracts.validate import validate

from conftest import fixture


def _report(file: str, service: str) -> dict[str, Any]:
    m: dict[str, Any] = fixture("jobs.completed/v1", "valid", file).value
    return {**m, "producer": {**m["producer"], "service": service}, "queue": f"jobs.{service}"}


def _codes(result: Any) -> list[str]:
    return [] if result.ok else [i["code"] for i in result.issues]


def test_accepts_in_consumer_mode_a_new_x_services_report_carrying_paid_user_reads() -> None:
    # gap_unfilled is the X gap job's own field, checked by its queue name, not the registry.
    report = _report("done-x-gap.json", "x-newsvc")
    del report["gap_unfilled"]
    assert validate("jobs.completed/v1", report, "consumer").ok
    assert "x_field" in _codes(validate("jobs.completed/v1", report, "producer"))


def test_accepts_in_consumer_mode_a_report_keyed_by_crawl_id_on_a_new_services_queue() -> None:
    report = _report("done-commoncrawl-rotation.json", "web-newscanner")
    assert validate("jobs.completed/v1", report, "consumer").ok
    assert "missing_key" in _codes(validate("jobs.completed/v1", report, "producer"))


def test_still_checks_a_known_services_report_in_consumer_mode() -> None:
    report = {**fixture("jobs.completed/v1", "valid", "done-rotation.json").value}
    report["paid_user_reads"] = 3
    assert "x_field" in _codes(validate("jobs.completed/v1", report, "consumer"))
