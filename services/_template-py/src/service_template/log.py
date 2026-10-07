"""Structured JSON log lines; every line can carry job_id, source_id, route and vendor.

A placeholder: F6 replaces it with py/listening_sdk's logger, which also scrubs secrets and
tokens before anything is written.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import Literal

Level = Literal["debug", "info", "warn", "error"]
LEVELS: tuple[Level, ...] = ("debug", "info", "warn", "error")
JOB_FIELDS = ("job_id", "source_id", "route", "vendor")
_ORDER: dict[Level, int] = {"debug": 10, "info": 20, "warn": 30, "error": 40}


def _stdout(line: str) -> None:
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Logger:
    def __init__(
        self,
        service: str,
        *,
        level: Level = "info",
        write: Callable[[str], None] = _stdout,
        now: Callable[[], datetime] = _utcnow,
        base: Mapping[str, object] | None = None,
    ) -> None:
        self._service: str = service
        self._level: Level = level
        self._write: Callable[[str], None] = write
        self._now: Callable[[], datetime] = now
        self._base: dict[str, object] = dict(base or {})

    def child(self, **fields: object) -> Logger:
        """A logger that adds `fields` to every line, for example the fields of one job."""
        return Logger(
            self._service,
            level=self._level,
            write=self._write,
            now=self._now,
            base={**self._base, **fields},
        )

    def log(self, level: Level, msg: str, **fields: object) -> None:
        if _ORDER[level] < _ORDER[self._level]:
            return
        ts = self._now().isoformat(timespec="milliseconds").replace("+00:00", "Z")
        entry = {"ts": ts, "level": level, "service": self._service, "msg": msg}
        self._write(json.dumps({**entry, **self._base, **fields}, ensure_ascii=False))

    def debug(self, msg: str, **fields: object) -> None:
        self.log("debug", msg, **fields)

    def info(self, msg: str, **fields: object) -> None:
        self.log("info", msg, **fields)

    def warn(self, msg: str, **fields: object) -> None:
        self.log("warn", msg, **fields)

    def error(self, msg: str, **fields: object) -> None:
        self.log("error", msg, **fields)
