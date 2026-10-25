"""Byte rules shared by every key and hash (ADR-0006): NFC, UTF-8, SHA-256 in lower-case hex.
NFC and lower case are those of Unicode 15.1.0 in both languages (D-2): a code point 15.1 leaves
unassigned is a starter with no mapping there, so it passes through both unchanged, and a runtime
with a later Unicode version gives 15.1's result for the runs of text between them."""

import hashlib
import hmac
import re
import unicodedata
from collections.abc import Callable
from typing import cast

from listening_contracts._artefacts import registry
from listening_contracts.errors import ContractError


def check_unicode_version(version: str) -> None:
    """Refuses a Unicode version below 15.1, which would normalise 15.1's text differently."""
    m = re.fullmatch(r"([0-9]+)\.([0-9]+)(\.[0-9]+)?", version)
    if m is None or (int(m[1]), int(m[2])) < (15, 1):
        raise ContractError("unicode_version", f"Unicode {version} is below 15.1")


check_unicode_version(unicodedata.unidata_version)

_UNASSIGNED = "".join(
    f"\\U{first:08x}-\\U{last:08x}"
    for first, last in cast(dict[str, list[list[int]]], registry("unicode-15.1-unassigned.json"))[
        "ranges"
    ]
)
_UNASSIGNED_RUNS = re.compile(f"([{_UNASSIGNED}]+)")


def _by_runs(s: str, f: Callable[[str], str]) -> str:
    """Applies f to each run between code points unassigned in Unicode 15.1 and keeps those
    unchanged."""
    parts = _UNASSIGNED_RUNS.split(s)
    if len(parts) == 1:
        return f(s)
    return "".join(f(part) if i % 2 == 0 else part for i, part in enumerate(parts))


def nfc(s: str) -> str:
    return _by_runs(s, lambda run: unicodedata.normalize("NFC", run))


def lower_case(s: str) -> str:
    return _by_runs(s, str.lower)


def require_str(value: object, what: str) -> str:
    if not isinstance(value, str):
        raise ContractError("not_string", f"{what} must be a string")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise ContractError("not_unicode", f"{what} holds a lone surrogate") from None
    return value


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_bytes(s: str) -> bytes:
    return hashlib.sha256(s.encode("utf-8")).digest()


def hmac_sha256_hex(key: bytes, s: str) -> str:
    return hmac.new(key, s.encode("utf-8"), hashlib.sha256).hexdigest()
