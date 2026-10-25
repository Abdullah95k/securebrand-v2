import json
from typing import Any

import pytest

from listening_contracts.canonical_json import canonical_json

from conftest import golden

G = golden("canonical-json.json")


@pytest.mark.parametrize("c", [pytest.param(c, id=c["name"]) for c in G["values"]])
def test_canonical_json_of_every_golden_structure_is_byte_identical(c: dict[str, Any]) -> None:
    assert canonical_json(c["value"]) == c["canonical"]


def test_key_order_by_utf_16_code_units_escapes_integers_and_floats_as_rfc_8785_renders_them() -> (
    None
):
    for c in G["numbers"]:
        assert canonical_json(json.loads(c["json"])) == c["canonical"]


def test_refuses_values_json_cannot_carry() -> None:
    for bad in (float("nan"), float("inf"), {"a": object()}, {1: "x"}):
        with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
            canonical_json(bad)
