from typing import Any

import pytest

from listening_contracts.registries import AMBER_VENDORS, D3_WRITERS, GREEN_VENDORS
from listening_contracts.vocabulary import VOCABULARY

from conftest import golden

G = golden("vocabulary.json")


@pytest.mark.parametrize("name", sorted(G["lists"]))
def test_each_closed_list_equals_the_values_its_adr_names(name: str) -> None:
    entry: dict[str, Any] = G["lists"][name]
    assert list(VOCABULARY[name]) == entry["values"], entry["from"]


def test_every_exported_list_has_a_recorded_source() -> None:
    assert [name for name in VOCABULARY if name not in G["lists"]] == []


def test_marks_every_account_type_an_organisation_kind_or_a_person_kind_never_both() -> None:
    org = set(VOCABULARY["ORGANISATION_ACCOUNT_TYPES"])
    person = set(VOCABULARY["PERSON_ACCOUNT_TYPES"])
    assert not org & person
    assert org | person == set(VOCABULARY["ACCOUNT_TYPES"])


def test_adr_0051s_vendors_and_the_d3_writer_names_equal_their_sources() -> None:
    assert list(AMBER_VENDORS) == G["registry"]["VENDORS_AMBER"]["values"]
    assert list(GREEN_VENDORS) == G["registry"]["VENDORS_GREEN"]["values"]
    assert list(D3_WRITERS) == G["registry"]["D3_WRITERS"]["values"]
