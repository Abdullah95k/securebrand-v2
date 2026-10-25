from typing import Any

import pytest

from listening_contracts.url import (
    article_key,
    canonical_url_hash,
    normalise_url,
    url_hash,
    url_key,
    web_result_key,
)

from conftest import golden

G = golden("urls.json")
BY_NAME: dict[str, dict[str, Any]] = {c["name"]: c for c in G["urls"]}


@pytest.mark.parametrize("c", [pytest.param(c, id=c["name"]) for c in G["urls"]])
def test_normalises_every_golden_url(c: dict[str, Any]) -> None:
    assert normalise_url(c["input"], c.get("base")) == c["normalised"]


@pytest.mark.parametrize("c", [pytest.param(c, id=c["name"]) for c in G["urls"]])
def test_derives_url_hash_url_key_and_the_article_and_web_result_keys(c: dict[str, Any]) -> None:
    assert url_hash(c["input"], c.get("base")) == c["url_hash"]
    assert url_key(c["input"], c.get("base")) == c["url_key"]
    assert canonical_url_hash(c["normalised"]) == c["url_hash"]
    assert article_key(c["normalised"]) == c["article_key"]
    assert web_result_key(c["normalised"]) == c["web_result_key"]


def test_normalising_twice_changes_nothing() -> None:
    for c in G["urls"]:
        assert normalise_url(c["normalised"]) == c["normalised"]


def test_http_and_https_forms_of_one_page_hash_differently() -> None:
    assert (
        BY_NAME["http, the known limit"]["url_hash"]
        != BY_NAME["https, the known limit"]["url_hash"]
    )
    assert BY_NAME["www kept"]["url_hash"] != BY_NAME["bare host"]["url_hash"]


@pytest.mark.parametrize("c", [pytest.param(c, id=c["name"]) for c in G["rejects"]])
def test_refuses_a_url(c: dict[str, Any]) -> None:
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        normalise_url(c["input"], c.get("base"))
