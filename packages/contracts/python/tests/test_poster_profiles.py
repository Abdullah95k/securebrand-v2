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
        "handle": "example_poster_x",
        "display_name": "Abu Ali",
        "url": "https://x.com/example_poster_x",
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


# The platforms where a person kind may be listed, so only the marking rule refuses null there.
LISTABLE = {
    "x": "prd-x-user-resolver.json",
    "facebook": "prd-fb-page-resolver.json",
    "youtube": "prd-yt-channel-resolver.json",
    "telegram": "prd-tg-channel-resolver.json",
}
STATUSES = {"resolved": None, "review": "age_gated", "unresolvable": "not_found"}


def test_rejects_a_typed_account_whose_public_account_is_null() -> None:
    """ADR-0010 L59, ADR-0033 L26: a typed account is marked public or not."""
    for platform, file in LISTABLE.items():
        for account_type in ("individual", "creator"):
            for status, reason in STATUSES.items():
                value = {
                    **fixture(ID, "valid", file).copy(),
                    "account_type": account_type,
                    "individual": account_type == "individual",
                    "public_account": None,
                    "status": status,
                    "reason": reason,
                }
                for mode in ("producer", "consumer"):
                    result = validate(ID, value, mode)
                    assert fails_at(result, ["public_account"]), (platform, account_type, status)


def test_accepts_public_account_null_only_with_account_type_null() -> None:
    for file in ("review-age-gated.json", "unresolvable-not-found.json"):
        f = fixture(ID, "valid", file)
        v = f.value
        assert [v["account_type"], v["individual"], v["public_account"]] == [None, None, None]
        for mode in ("producer", "consumer"):
            assert validate(ID, f.value, mode).ok, (file, mode)
        typed = {**f.copy(), "account_type": "page", "individual": False}
        assert fails_at(validate(ID, typed), ["public_account"]), file
