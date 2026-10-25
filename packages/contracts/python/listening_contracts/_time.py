"""Timestamps as the keys and ids read them (ADR-0006)."""

import re
from datetime import UTC, datetime, timedelta

from listening_contracts.errors import ContractError

_KEY_TIME = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?(Z|[+-][0-9]{2}:?[0-9]{2})"
)
_MESSAGE_TIME = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(\.([0-9]{1,3}))?Z"
)


def _utc(groups: tuple[str, ...], t: str) -> datetime:
    y, mo, d, h, mi, s = (int(g) for g in groups)
    try:
        return datetime(y, mo, d, h, mi, s, tzinfo=UTC)
    except ValueError:
        raise ContractError("bad_time", f"{t} names no calendar time") from None


def render_key_time(t: str) -> str:
    """A platform time with seconds and an offset, as YYYY-MM-DDTHH:MM:SSZ (fractions truncated)."""
    m = _KEY_TIME.fullmatch(t)
    if m is None:
        raise ContractError("bad_time", f"{t} is not a time with seconds and an offset")
    when = _utc(m.groups()[:6], t)
    off = m.group(8)
    if off != "Z":
        oh, om = int(off[1:3]), int(off[-2:])
        if oh > 23 or om > 59:
            raise ContractError("bad_time", t)
        sign = 1 if off[0] == "+" else -1
        when -= sign * timedelta(hours=oh, minutes=om)
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def message_time_millis(t: str) -> int:
    """Milliseconds of a message timestamp: RFC 3339 in UTC with Z, up to three fraction digits."""
    m = _MESSAGE_TIME.fullmatch(t)
    if m is None:
        raise ContractError("bad_time", f"{t} is not a UTC timestamp")
    when = _utc(m.groups()[:6], t)
    return int(when.timestamp()) * 1000 + int((m.group(8) or "0").ljust(3, "0"))
