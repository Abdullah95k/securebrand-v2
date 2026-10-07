import json
from collections.abc import Sequence
from dataclasses import dataclass

from service_template.handler import handle
from service_template.log import Logger


@dataclass(frozen=True)
class Record:
    id: str


class FixtureAdapter:
    """The records a recorded response would yield; no network."""

    def fetch(self, request: str) -> Sequence[Record]:
        return [Record("a"), Record("b")] if request == "p1" else []


FIELDS: dict[str, object] = {
    "job_id": "job-7",
    "source_id": "src-3",
    "route": "green",
    "vendor": None,
}


def to_item(record: Record) -> str:
    return f"item:{record.id}"


def test_maps_every_fetched_record_and_logs_the_job_fields() -> None:
    lines: list[str] = []
    log = Logger("service-template", write=lines.append)
    outputs = handle("p1", FIELDS, FixtureAdapter(), to_item, log)
    assert outputs == ["item:a", "item:b"]
    entry = json.loads(lines[0])
    assert entry["msg"] == "job handled"
    assert {key: entry[key] for key in FIELDS} == FIELDS
    assert (entry["records"], entry["outputs"]) == (2, 2)


def test_returns_the_same_outputs_when_a_job_is_replayed() -> None:
    log = Logger("service-template", write=lambda _line: None)
    first = handle("p1", FIELDS, FixtureAdapter(), to_item, log)
    second = handle("p1", FIELDS, FixtureAdapter(), to_item, log)
    assert second == first
