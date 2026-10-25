import unicodedata
from typing import Any

import pytest

from listening_contracts.keys import folding_profile, query_key, query_key_with_profile
from listening_contracts.vocabulary import PLATFORMS

from conftest import golden

G = golden("query-key.json")


def _find(profile: str, name: str) -> str:
    return next(c["query_key"] for c in G["keys"] if c["profile"] == profile and c["name"] == name)


@pytest.mark.parametrize(
    "c", [pytest.param(c, id=f"{c['profile']}: {c['name']}") for c in G["keys"]]
)
def test_derives_the_golden_query_keys_under_each_profile(c: dict[str, Any]) -> None:
    assert query_key_with_profile(c["profile"], c["forms"], c["context_terms"]) == c["query_key"]


def test_form_order_and_nfc_variants_give_one_key() -> None:
    assert _find("exact", "a keyword with handle, hashtag and context") == _find(
        "exact", "the same forms in another order"
    )
    # The helper itself, on input that is not NFC, gives the composed input's stored key.
    dec = next(c for c in G["keys"] if c["name"] == "the same forms and context term decomposed")
    for s in [*dec["forms"], *dec["context_terms"]]:
        assert unicodedata.normalize("NFC", s) != s
    assert query_key_with_profile("exact", dec["forms"], dec["context_terms"]) == _find(
        "exact", "composed forms and context term"
    )


def test_the_exact_profile_keeps_alef_teh_marbuta_and_yeh_variants_apart() -> None:
    assert _find("exact", "alef with hamza below") != _find("exact", "bare alef")
    assert _find("exact", "teh marbuta") != _find("exact", "heh")
    assert _find("exact", "alef maksura") != _find("exact", "yeh")


def test_the_folded_profile_merges_them() -> None:
    assert _find("folded", "alef with hamza below") == _find("folded", "bare alef")
    assert _find("folded", "teh marbuta") == _find("folded", "heh")
    assert _find("folded", "alef maksura") == _find("folded", "yeh")
    assert _find("folded", "tashkeel removed") == _find("folded", "heh")
    assert _find("folded", "tatweel removed") == _find("folded", "plain zain")
    assert _find("folded", "Persian keheh and yeh") == _find("folded", "Arabic kaf and yeh")


def test_every_platform_starts_at_exact() -> None:
    for platform in PLATFORMS:
        assert folding_profile(platform) == "exact"
        assert G["profiles_v1"][platform] == "exact"
    c = G["keys"][0]
    assert query_key("facebook", c["forms"], c["context_terms"]) == c["query_key"]


@pytest.mark.parametrize("c", [pytest.param(c, id=c["name"]) for c in G["rejects"]])
def test_refuses_a_keyword(c: dict[str, Any]) -> None:
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        query_key_with_profile(c["profile"], c["forms"], c["context_terms"])
