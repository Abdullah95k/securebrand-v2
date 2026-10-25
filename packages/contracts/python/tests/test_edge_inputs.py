"""Edge inputs (review note 17, D-5): validate() returns issues and never raises on any JSON input,
and a registry lookup by a name that is an Object property in JavaScript finds nothing."""

import math
from typing import Any

import pytest

from listening_contracts.errors import ContractError
from listening_contracts.registries import partition_key
from listening_contracts.validate import ValidationResult, validate

from conftest import fixture


def _issues(result: ValidationResult) -> list[list[Any]]:
    return [] if result.ok else [[i["path"], i["code"]] for i in result.issues]


def _nested(levels: int) -> list[Any]:
    """`levels` lists, one inside the other."""
    value: list[Any] = []
    for _ in range(levels - 1):
        value = [value]
    return value


def test_names_a_producer_called_constructor_an_unknown_service() -> None:
    raw = fixture("raw.items/v1", "valid", "metrics.json").copy()
    raw["envelope"]["producer"]["service"] = "constructor"
    assert _issues(validate("raw.items/v1", raw, "producer")) == [
        [["envelope", "producer", "service"], "unknown_service"]
    ]


@pytest.mark.parametrize("schema_id", ["toString", "constructor"])
def test_finds_no_partition_key_under_an_object_property_name(schema_id: str) -> None:
    with pytest.raises(ContractError, match="unknown_schema"):
        partition_key(schema_id, {})


def test_refuses_a_non_finite_number_a_value_nested_past_64_levels_and_a_proto_key() -> None:
    base = fixture("raw.items/v1", "valid", "prd-fb-page-feed-poller.json").copy()
    for n in (math.inf, -math.inf, math.nan):
        value = {**base, "payload": {**base["payload"], "like_count": n}}
        assert _issues(validate("raw.items/v1", value, "consumer")) == [
            [["payload", "like_count"], "not_json"]
        ], n
    deep = {**base, "payload": {**base["payload"], "attachments": _nested(64)}}
    assert _issues(validate("raw.items/v1", deep, "consumer")) == [
        [["payload", "attachments", *([0] * 63)], "not_json"]
    ]
    proto = {**base, "payload": {**base["payload"], "extra": {"__proto__": {"x": 1}, "id": "1"}}}
    assert _issues(validate("raw.items/v1", proto, "consumer")) == [
        [["payload", "extra", "__proto__"], "not_json"]
    ]


@pytest.mark.parametrize("mode", ["producer", "consumer"])
def test_returns_issues_for_a_value_nested_255_levels_deep_and_never_raises(mode: str) -> None:
    base = fixture("raw.items/v1", "valid", "prd-fb-page-feed-poller.json").copy()
    for value in (
        {**base, "payload": {**base["payload"], "attachments": _nested(255)}},
        {**base, "extra": _nested(255)},
    ):
        assert not validate("raw.items/v1", value, mode).ok  # type: ignore[arg-type]
