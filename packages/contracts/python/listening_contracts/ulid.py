"""The deterministic ULID (ADR-0006): time part the event's own time in milliseconds, random part
the first 10 bytes of SHA-256 over the declared fields' UTF-8, joined by '|'."""

from listening_contracts._text import require_str, sha256_bytes
from listening_contracts._time import message_time_millis
from listening_contracts.errors import ContractError

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def encode_ulid(time_ms: int, random: bytes) -> str:
    """A 48-bit time and 10 bytes of randomness as a ULID's 26 Crockford base32 characters."""
    if isinstance(time_ms, bool) or not 0 <= time_ms < 2**48:
        raise ContractError("bad_time", str(time_ms))
    if len(random) != 10:
        raise ContractError("bad_random", "ULID randomness is 10 bytes")
    value = (time_ms << 80) | int.from_bytes(random, "big")
    return "".join(_CROCKFORD[(value >> (5 * i)) & 31] for i in range(25, -1, -1))


def deterministic_ulid(time: str, fields: list[str]) -> str:
    ms = message_time_millis(require_str(time, "time"))
    joined = "|".join(require_str(f, f"field {i}") for i, f in enumerate(fields))
    return encode_ulid(ms, sha256_bytes(joined)[:10])


def hit_message_id(hit_at: str, hit_id: str, item_version: int, keyword_set_version: str) -> str:
    """keyword-matcher's replay-stable message_id (ADR-0006, ADR-0070 a); §5.3 L77)."""
    if isinstance(item_version, bool) or not isinstance(item_version, int) or item_version < 0:  # pyright: ignore[reportUnnecessaryIsInstance] - callers may pass JSON values
        raise ContractError("bad_version", "item_version must be a non-negative integer")
    return deterministic_ulid(hit_at, [hit_id, str(item_version), keyword_set_version])


def comment_decay_job_id(due_at: str, item_id: str, lane: str, series_step: str) -> str:
    """comment-decay-scheduler's job_id: sha256(item_id | lane | series_step), due_at (§5.3 L84)."""
    return deterministic_ulid(due_at, [item_id, lane, series_step])
