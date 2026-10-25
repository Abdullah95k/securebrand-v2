import pytest

from listening_contracts.keys import author_ref, matches_author_ref

from conftest import golden

G = golden("author-ref.json")
KEY_1 = G["test_key_utf8"].encode("utf-8")
KEY_2 = G["second_test_key_utf8"].encode("utf-8")


def test_derives_the_golden_author_refs() -> None:
    for c in G["author_refs"]:
        assert author_ref(KEY_1, c["platform"], c["author_platform_id"]) == c["author_ref"]
    s = G["under_second_key"]
    assert author_ref(KEY_2, s["platform"], s["author_platform_id"]) == s["author_ref"]


def test_an_nfd_author_id_gives_the_reference_of_its_nfc_form() -> None:
    nfd, nfc = G["author_refs"][-2:]
    assert nfd["author_ref"] == nfc["author_ref"]


def test_refuses_an_empty_key() -> None:
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        author_ref(b"", "x", "1234567890")


def test_matches_a_reference_under_any_of_several_keys() -> None:
    s = G["under_second_key"]
    assert matches_author_ref(
        s["author_ref"], s["platform"], s["author_platform_id"], [KEY_1, KEY_2]
    )
    assert not matches_author_ref(s["author_ref"], s["platform"], s["author_platform_id"], [KEY_1])
    assert not matches_author_ref(s["author_ref"], s["platform"], "999", [KEY_1, KEY_2])
