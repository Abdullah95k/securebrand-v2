"""A27: poster.profiles/v1, ADR-0033's flat schema with public_account (ADR-0010)."""

from typing import Any

from listening_contracts.validate import ValidationResult, validate

from conftest import fixture

ID = "poster.profiles/v1"


def fails_at(result: ValidationResult, path: list[str | int]) -> bool:
    return not result.ok and path in [i["path"] for i in result.issues]


def test_rejects_a_handle_display_name_url_country_signals_or_extras_on_an_individuals_answer() -> (
    None
):
    base = fixture(ID, "valid", "individual.json")
    assert validate(ID, base.value).ok
    values: dict[str, Any] = {
        "handle": "abuali_basra",
        "display_name": "Abu Ali",
        "url": "https://x.com/abuali_basra",
        "country_signals": None,
        "extras": {},
    }
    for name, v in values.items():
        assert fails_at(validate(ID, {**base.copy(), name: v}), [name]), name


def test_accepts_a_public_persons_identity_fields() -> None:
    v = fixture(ID, "valid", "public-person-individual.json").value
    assert [v["account_type"], v["individual"], v["public_account"]] == ["individual", True, True]
    assert v["handle"]
    assert validate(ID, v).ok


def test_rejects_an_extras_key_its_resolver_does_not_declare() -> None:
    value = fixture(ID, "valid", "prd-fb-page-resolver.json").copy()
    value["extras"]["media_count"] = 10  # ig-account-resolver's key
    assert fails_at(validate(ID, value), ["extras", "media_count"])
    assert validate(ID, value, "consumer").ok


def test_keeps_a_persons_account_unlisted_on_tiktok_instagram_and_linkedin() -> None:
    for file in ("prd-tt-user-resolver.json", "prd-ig-account-resolver.json"):
        value = {**fixture(ID, "valid", file).copy(), "public_account": True}
        assert fails_at(validate(ID, value), ["public_account"]), file
