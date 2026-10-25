"""A32: producers validate strictly, consumers tolerantly (ADR-0002)."""

from typing import Any, cast

import pytest

from listening_contracts.validate import validate

from conftest import Fixture, fixtures, schema_dirs, schema_id_of

TOLERANT = [(d, f) for d in schema_dirs() for f in fixtures(d, "tolerant")]


def unknown_keys(value: Any, known: Any) -> list[str]:
    """The keys a tolerant fixture adds to some valid fixture of its schema."""
    if not isinstance(value, dict):
        return []
    known_map = cast(dict[str, Any], known) if isinstance(known, dict) else {}
    out: list[str] = []
    for k, v in cast(dict[str, Any], value).items():
        if k not in known_map:
            out.append(k)
        else:
            out.extend(f"{k}.{x}" for x in unknown_keys(v, known_map[k]))
    return out


def get(value: Any, path: str) -> Any:
    for step in path.split("."):
        if not isinstance(value, dict) or step not in value:
            return None
        value = cast(dict[str, Any], value)[step]
    return value


@pytest.mark.parametrize(("directory", "f"), TOLERANT, ids=[f.name for _, f in TOLERANT])
def test_the_producer_mode_rejects_an_unknown_field(directory: str, f: Fixture) -> None:
    assert not validate(schema_id_of(directory), f.value, "producer", **f.options).ok


@pytest.mark.parametrize(("directory", "f"), TOLERANT, ids=[f.name for _, f in TOLERANT])
def test_the_consumer_mode_accepts_and_drops_it(directory: str, f: Fixture) -> None:
    result = validate(schema_id_of(directory), f.value, "consumer", **f.options)
    assert result.ok
    nearest = min((unknown_keys(f.value, v.value) for v in fixtures(directory, "valid")), key=len)
    assert len(nearest) == 1, f"{f.name} adds one field to a valid fixture"
    for path in nearest:
        assert get(result.value, path) is None, path
