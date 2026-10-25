"""A26: items.normalized/v1 (ADR-0005, ADR-0031, ADR-0059, ADR-0068, ADR-0070)."""

from listening_contracts.validate import ValidationResult, validate

from conftest import fixture

ID = "items.normalized/v1"


def fails_at(result: ValidationResult, path: list[str | int]) -> bool:
    return not result.ok and path in [i["path"] for i in result.issues]


def test_rejects_author_followers_without_author_source_id() -> None:
    value = fixture(ID, "valid", "post-poster-not-yet-classed.json").copy()
    value["author"]["author_followers"] = 1200
    assert fails_at(validate(ID, value), ["author", "author_followers"])
    source = fixture(ID, "valid", "prd-normalize-item.json").copy()
    source["author"]["author_followers"] = 412000
    assert validate(ID, source).ok


def test_carries_job_kind_lang_pending_and_sensitive_event_on_every_item() -> None:
    for name in ("job_kind", "lang_pending", "sensitive_event"):
        value = fixture(ID, "valid", "prd-normalize-item.json").copy()
        del value[name]
        assert fails_at(validate(ID, value), [name]), name


def test_accepts_text_full_ref_and_usage_signals_on_an_article() -> None:
    value = fixture(ID, "valid", "article.json").value
    assert "text_full_ref" in value
    assert "usage_signals" in value
    assert validate(ID, value).ok


def test_accepts_the_transient_poster_platform_id_only_for_a_poster_not_yet_classed() -> None:
    assert validate(ID, fixture(ID, "valid", "post-poster-not-yet-classed.json").value).ok
    value = fixture(ID, "valid", "prd-normalize-item.json").copy()
    value["poster_platform_id"] = "1234567890"
    assert fails_at(validate(ID, value), ["poster_platform_id"])
