import json
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from service_template.log import Logger


def test_writes_one_json_line_per_entry_carrying_the_job_fields() -> None:
    lines: list[str] = []
    log = Logger(
        "service-template",
        write=lines.append,
        now=lambda: datetime(2026, 10, 7, tzinfo=UTC),
    )
    log.child(job_id="job-1", source_id="src-1", route="green", vendor=None).info(
        "fetched", items=3
    )
    assert [json.loads(line) for line in lines] == [
        {
            "ts": "2026-10-07T00:00:00.000Z",
            "level": "info",
            "service": "service-template",
            "msg": "fetched",
            "job_id": "job-1",
            "source_id": "src-1",
            "route": "green",
            "vendor": None,
            "items": 3,
        }
    ]


def test_drops_entries_below_the_configured_level() -> None:
    lines: list[str] = []
    log = Logger("service-template", level="warn", write=lines.append)
    log.debug("noise")
    log.info("noise")
    log.warn("kept")
    log.error("kept too")
    assert [json.loads(line)["msg"] for line in lines] == ["kept", "kept too"]


def test_keeps_arabic_and_sorani_text_readable() -> None:
    lines: list[str] = []
    Logger("service-template", write=lines.append).info("نص عربي", note="کوردی")
    assert "نص عربي" in lines[0]
    assert "کوردی" in lines[0]


def test_writes_datetimes_uuids_and_decimals_instead_of_failing_the_job() -> None:
    lines: list[str] = []
    Logger("service-template", write=lines.append).info(
        "fetched",
        fetched_at=datetime(2026, 10, 7, 12, 30, tzinfo=UTC),
        item=UUID("12345678-1234-5678-1234-567812345678"),
        score=Decimal("0.25"),
    )
    entry = json.loads(lines[0])
    assert entry["fetched_at"] == "2026-10-07T12:30:00+00:00"
    assert entry["item"] == "12345678-1234-5678-1234-567812345678"
    assert entry["score"] == "0.25"
