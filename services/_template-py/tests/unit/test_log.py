import json
from datetime import UTC, datetime

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
