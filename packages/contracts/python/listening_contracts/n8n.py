"""The n8n signing helper (ADR-0067: one HMAC scheme over the body with a timestamp and an
idempotency key), the twin of signN8n and verifyN8n. The header names, the signed string and the
tolerance are F2's (Q11, F-49)."""

import hashlib
import hmac
import math
import re
from typing import Literal, NotRequired, TypedDict

from listening_contracts.errors import ContractError

Reason = Literal[
    "missing_header", "bad_idempotency_key", "bad_timestamp", "stale_timestamp", "bad_signature"
]


class Verification(TypedDict):
    ok: bool
    reason: NotRequired[Reason]


# An idempotency key is a header value, so it holds no control character or space, and it holds no
# dot, which separates the fields of the signed string: "a.b" over "c" and "a" over "b.c" would
# otherwise sign alike.
_IDEMPOTENCY_KEY = re.compile(r"[^\x00-\x20\x7f.]+")
_TIMESTAMP = re.compile(r"[0-9]{1,15}")


def _bytes(value: bytes | str) -> bytes:
    return value.encode() if isinstance(value, str) else value


def _seconds(value: object) -> int:
    """Unix seconds: a whole non-negative number (a bool is no number here)."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContractError("bad_timestamp", "Unix seconds, a whole non-negative number")
    return value


def _idempotency_key(value: object) -> str:
    if not isinstance(value, str) or _IDEMPOTENCY_KEY.fullmatch(value) is None:
        raise ContractError("bad_idempotency_key", "a non-empty header value without a dot")
    return value


def _finite_seconds(value: object, code: str, what: str) -> float:
    """A finite non-negative number of seconds (a bool is no number here)."""
    if (
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(value)
        or value < 0
    ):
        raise ContractError(code, f"{what}, a finite non-negative number of seconds")
    return value


def _mac(body: bytes, secret: bytes, timestamp: str, key: str) -> str:
    """Hex HMAC-SHA256 under `secret` of the UTF-8 of "<timestamp>.<key>." and the body bytes."""
    return hmac.new(secret, f"{timestamp}.{key}.".encode() + body, hashlib.sha256).hexdigest()


def sign_n8n(
    body: bytes | str, secret: bytes | str, timestamp: int, idempotency_key: str
) -> dict[str, str]:
    """Signs a notice's body for n8n or a client's alert webhook (ADR-0067, Q15): `timestamp` in
    Unix seconds, given by the caller, and the notice's idempotency key. The SDK signs again at
    each send."""
    ts = str(_seconds(timestamp))
    idempotency_key = _idempotency_key(idempotency_key)
    key = _bytes(secret)
    if not key:
        raise ContractError("empty_secret", "the signing secret is empty")
    return {
        "X-SB-Timestamp": ts,
        "Idempotency-Key": idempotency_key,
        "X-SB-Signature": f"v1={_mac(_bytes(body), key, ts, idempotency_key)}",
    }


def verify_n8n(
    body: bytes | str,
    headers: dict[str, str],
    secret: bytes | str,
    now: float,
    tolerance_seconds: float = 300,
) -> Verification:
    """Verifies a signed notice: the headers by name in any case, the timestamp no further than
    `tolerance_seconds` from `now` (Unix seconds, given by the caller: no helper reads a clock). A
    clock or a tolerance that is not a finite non-negative number is the caller's error and raises,
    so a NaN can never switch the staleness check off."""
    now = _finite_seconds(now, "bad_now", "now is Unix seconds")
    tolerance_seconds = _finite_seconds(tolerance_seconds, "bad_tolerance", "the tolerance")
    by_name = {k.lower(): v for k, v in headers.items()}
    ts = by_name.get("x-sb-timestamp")
    key = by_name.get("idempotency-key")
    signature = by_name.get("x-sb-signature")
    if ts is None or key is None or signature is None:
        return {"ok": False, "reason": "missing_header"}
    if _IDEMPOTENCY_KEY.fullmatch(key) is None:
        return {"ok": False, "reason": "bad_idempotency_key"}
    if _TIMESTAMP.fullmatch(ts) is None:
        return {"ok": False, "reason": "bad_timestamp"}
    if abs(now - int(ts)) > tolerance_seconds:
        return {"ok": False, "reason": "stale_timestamp"}
    secret_bytes = _bytes(secret)
    if not secret_bytes or not signature.startswith("v1="):
        return {"ok": False, "reason": "bad_signature"}
    want = _mac(_bytes(body), secret_bytes, ts, key)
    if not hmac.compare_digest(signature[3:].encode(), want.encode()):
        return {"ok": False, "reason": "bad_signature"}
    return {"ok": True}
