"""The JSON-level rules validate() applies to a whole message before its schema, in both languages:
every string and key is well-formed Unicode (finding 5); the twin of
test/unit/json-values.test.ts."""

from collections.abc import Callable
from typing import Any

from listening_contracts.validate import validate

from conftest import fixture

LONE = "\ud83d"  # a high surrogate alone, as slicing an emoji leaves it
EMOJI = "😀"


def _error_message(m: dict[str, Any], odd: str) -> list[str | int]:
    m["error"]["message"] = f"could not parse: {odd}"
    return ["error", "message"]


def _matched_term(m: dict[str, Any], odd: str) -> list[str | int]:
    m["matched_term"] = f"{m['matched_term']}{odd}"
    return ["matched_term"]


def _payload_value(m: dict[str, Any], odd: str) -> list[str | int]:
    m["payload"]["note"] = odd
    return ["payload", "note"]


def _array_element(m: dict[str, Any], odd: str) -> list[str | int]:
    m["payload"]["tags"] = ["ok", odd]
    return ["payload", "tags", 1]


def _object_key(m: dict[str, Any], odd: str) -> list[str | int]:
    m["payload"][odd] = 1
    return ["payload", odd]


# Where a lone surrogate may land: a constrained string, a free-form payload's value, an array
# element and an object key. Each case sets `odd` there and gives the path it is reported at.
PLACES: list[tuple[str, str, str, Callable[[dict[str, Any], str], list[str | int]]]] = [
    ("dlq.<service>/v1", "dlq/v1", "consume-data-message.json", _error_message),
    ("item.hits/v1", "item.hits/v1", "prd-keyword-matcher.json", _matched_term),
    ("raw.items/v1", "raw.items/v1", "prd-fb-page-feed-poller.json", _payload_value),
    ("raw.items/v1", "raw.items/v1", "prd-fb-page-feed-poller.json", _array_element),
    ("raw.items/v1", "raw.items/v1", "prd-fb-page-feed-poller.json", _object_key),
]


def test_refuses_a_lone_surrogate_anywhere_with_not_unicode_in_both_modes_without_raising() -> None:
    for sid, directory, file, place in PLACES:
        m = fixture(directory, "valid", file).copy()
        path = place(m, LONE)
        for mode in ("producer", "consumer"):
            result = validate(sid, m, mode)  # never raises
            issues = [{"path": i["path"], "code": i["code"]} for i in result.issues]
            assert issues == [{"path": path, "code": "not_unicode"}], (file, mode)


def test_accepts_a_well_formed_emoji_in_the_same_place() -> None:
    for sid, directory, file, place in PLACES:
        m = fixture(directory, "valid", file).copy()
        place(m, EMOJI)
        for mode in ("producer", "consumer"):
            assert validate(sid, m, mode).issues == [], (file, mode)
