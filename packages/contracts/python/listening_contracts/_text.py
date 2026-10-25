"""Byte rules shared by every key and hash (ADR-0006): NFC, UTF-8, SHA-256 in lower-case hex."""

import hashlib
import hmac
import unicodedata

from listening_contracts.errors import ContractError


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


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
