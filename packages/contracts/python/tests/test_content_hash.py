from typing import Any

import pytest

from listening_contracts.keys import content_hash

from conftest import golden

G = golden("content-hash.json")


@pytest.mark.parametrize("c", [pytest.param(c, id=c["name"]) for c in G["hashes"]])
def test_derives_the_golden_content_hashes(c: dict[str, Any]) -> None:
    assert content_hash(c["title"], c["text"]) == c["content_hash"]


def test_a_decomposed_text_hashes_as_its_composed_form() -> None:
    by_name = {c["name"]: c["content_hash"] for c in G["hashes"]}
    assert by_name["decomposed text hashes as composed"] == by_name["the same text composed"]
