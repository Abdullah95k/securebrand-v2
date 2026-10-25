from typing import Any

import pytest

from listening_contracts.keys import (
    InstagramMapRow,
    idempotency_key,
    idless_comment_key,
    instagram_post_key,
    instagram_shortcode_id,
    item_id,
    linkedin_comment_id,
    linkedin_post_id,
    parse_key,
    telegram_comment_id,
    telegram_post_id,
)

from conftest import golden

G = golden("keys.json")


def _named(cases: list[dict[str, Any]]) -> list[Any]:
    return [pytest.param(c, id=str(c.get("name", c.get("key")))) for c in cases]


@pytest.mark.parametrize("c", _named(G["keys"]))
def test_builds_every_golden_key_byte_for_byte(c: dict[str, Any]) -> None:
    i = c["input"]
    assert idempotency_key(i["platform"], i["kind"], i["platform_id"]) == c["key"]


@pytest.mark.parametrize("c", _named(G["keys"]))
def test_derives_every_golden_item_id(c: dict[str, Any]) -> None:
    assert item_id(c["key"]) == c["item_id"]


def test_an_nfd_input_yields_the_nfc_key_and_the_same_item_id() -> None:
    import unicodedata

    nfd = next(c for c in G["keys"] if c["name"] == "NFD id yields the NFC key")
    i = nfd["input"]
    assert i["platform_id"] != unicodedata.normalize("NFC", i["platform_id"])
    key = idempotency_key(i["platform"], i["kind"], i["platform_id"])
    assert key == unicodedata.normalize("NFC", key)
    assert item_id(unicodedata.normalize("NFD", key)) == nfd["item_id"]


@pytest.mark.parametrize("c", _named(G["builders"]))
def test_builds_the_platform_id_part(c: dict[str, Any]) -> None:
    i = c["input"]
    built = {
        "telegram_post_id": lambda: telegram_post_id(i["channel"], i["message_id"]),
        "telegram_comment_id": lambda: telegram_comment_id(i["group_chat_id"], i["message_id"]),
        "linkedin_post_id": lambda: linkedin_post_id(i["post_id"], i["urn"]),
        "linkedin_comment_id": lambda: linkedin_comment_id(i["post_id"], i["comment_id"], i["urn"]),
        "instagram_shortcode_id": lambda: instagram_shortcode_id(i["shortcode"]),
    }[c["helper"]]
    assert built() == c["platform_id"]


@pytest.mark.parametrize("c", _named(G["parse"]))
def test_parses_a_key_on_its_first_two_colons_ids_holding_colons_and_slashes_included(
    c: dict[str, Any],
) -> None:
    assert parse_key(c["key"]) == {
        "platform": c["platform"],
        "kind": c["kind"],
        "platform_id": c["platform_id"],
    }


@pytest.mark.parametrize("c", _named(G["rejects"]))
def test_refuses_a_key_it_cannot_build(c: dict[str, Any]) -> None:
    i = c["input"]
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        idempotency_key(i["platform"], i["kind"], i["platform_id"])


@pytest.mark.parametrize("c", _named(G["parse_rejects"]))
def test_refuses_to_parse_a_malformed_key(c: dict[str, Any]) -> None:
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        parse_key(c["key"])


def test_keeps_ids_as_strings_never_numbers() -> None:
    big = "7429384756102938475"
    assert idempotency_key("tiktok", "video", big) == f"tiktok:video:{big}"
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        idempotency_key("tiktok", "video", int(big))  # type: ignore[arg-type]


@pytest.mark.parametrize("c", _named(G["idless_comments"]))
def test_builds_the_golden_id_less_key(c: dict[str, Any]) -> None:
    i = c["input"]
    assert idless_comment_key(i["platform"], i["post_id"], i["created_time"], i["text"]) == c["key"]
    assert item_id(c["key"]) == c["item_id"]


def test_an_nfd_text_yields_the_same_key_as_its_nfc_form() -> None:
    nfd = next(c for c in G["idless_comments"] if c["name"].startswith("decomposed Arabic"))
    composed = next(c for c in G["idless_comments"] if c["name"] == "the same text composed")
    assert nfd["key"] == composed["key"]


def test_one_comment_read_with_two_offsets_keeps_one_key() -> None:
    first, second, fractional = G["idless_comments"][:3]
    assert first["key"] == second["key"] == fractional["key"]


@pytest.mark.parametrize("c", _named(G["idless_rejects"]))
def test_refuses_a_created_time(c: dict[str, Any]) -> None:
    i = c["input"]
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        idless_comment_key(i["platform"], i["post_id"], i["created_time"], i["text"])


@pytest.mark.parametrize("c", _named(G["instagram_id_map"]))
def test_the_instagram_id_map(c: dict[str, Any]) -> None:
    rows: list[InstagramMapRow] = c["map"]

    def lookup(shortcode: str) -> InstagramMapRow | None:
        return next((r for r in rows if r["shortcode"] == shortcode), None)

    key, row = instagram_post_key(
        c["read"]["route"], c["read"]["media_id"], c["read"]["shortcode"], lookup
    )
    assert key == c["key"]
    assert row == c["map_row"]


def test_a_post_with_only_a_shortcode_keys_instagram_post_sc_shortcode() -> None:
    key, _row = instagram_post_key("vendor", None, "Ab_c-1", lambda _s: None)
    assert key == "instagram:post:sc:Ab_c-1"


def test_a_graph_read_of_a_shortcode_already_mapped_reuses_that_key() -> None:
    row: InstagramMapRow = {
        "shortcode": "Ab_c-1",
        "graph_media_id": None,
        "key": "instagram:post:sc:Ab_c-1",
    }
    key, _row = instagram_post_key("graph", "17895695668004551", "Ab_c-1", lambda _s: row)
    assert key == "instagram:post:sc:Ab_c-1"
