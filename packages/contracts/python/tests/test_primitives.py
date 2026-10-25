import re

import pytest

from listening_contracts._time import message_time_millis
from listening_contracts.errors import ContractError
from listening_contracts.keys import (
    candidate_key_from_handle,
    candidate_key_from_id,
    facebook_group_candidate_key,
    news_site_candidate_key,
    parse_candidate_key,
    parse_raw_ref,
    raw_ref,
    render_key_time,
)
from listening_contracts.patterns import PATTERNS


def _matches(name: str, value: str) -> bool:
    return re.fullmatch(PATTERNS[name], value) is not None


def test_takes_calendar_dates_only_from_0001_to_9999() -> None:
    """Note 18."""
    for date in ("2024-02-29", "2000-02-29", "0001-01-01", "9999-12-31"):
        assert _matches("date", date), date
        assert _matches("timestamp", f"{date}T09:15:42Z"), date
    for date in ("2100-02-29", "2026-02-30", "2026-04-31", "0000-01-01", "2026-02-29"):
        assert not _matches("date", date), date
        assert not _matches("timestamp", f"{date}T09:15:42Z"), date
    with pytest.raises(ContractError, match="bad_raw_ref"):
        raw_ref("green", "facebook", "2026-02-30", "fb-page-feed-poller", 1, 1)


def test_rejects_a_non_utc_timestamp() -> None:
    assert _matches("timestamp", "2026-10-06T09:15:42Z")
    assert _matches("timestamp", "2026-10-06T09:15:42.123Z")
    for bad in (
        "2026-10-06T09:15:42+03:00",
        "2026-10-06T09:15Z",
        "2026-10-06T09:15:42.1234Z",
        "2026-10-06 09:15:42Z",
        "2026-10-06T09:15:42Z\n",
    ):
        assert not _matches("timestamp", bad)


def test_reads_the_years_0001_to_0099_as_written_and_refuses_a_time_outside_0001_to_9999() -> None:
    assert message_time_millis("0050-01-01T00:00:00Z") == -60_589_296_000_000
    assert message_time_millis("0001-01-01T00:00:00.123Z") == -62_135_596_799_877
    assert render_key_time("0050-06-01T10:00:00+03:00") == "0050-06-01T07:00:00Z"
    assert render_key_time("0100-01-01T00:30:00+01:00") == "0099-12-31T23:30:00Z"
    with pytest.raises(ContractError, match="bad_time"):
        message_time_millis("0000-01-01T00:00:00Z")
    for t in ("0000-01-01T00:00:00Z", "0001-01-01T00:00:00+01:00", "9999-12-31T23:30:00-01:00"):
        with pytest.raises(ContractError, match="bad_time"):
            render_key_time(t)


def test_the_id_less_comment_hash_renders_created_time_as_yyyy_mm_ddthh_mm_ssz() -> None:
    assert render_key_time("2026-10-06T09:15:42+0000") == "2026-10-06T09:15:42Z"
    assert render_key_time("2026-10-06T12:15:42+03:00") == "2026-10-06T09:15:42Z"
    assert render_key_time("2026-10-06T01:15:42-08:00") == "2026-10-06T09:15:42Z"
    assert render_key_time("2026-10-06T09:15:42.999Z") == "2026-10-06T09:15:42Z"
    assert render_key_time("2026-01-01T02:00:00+03:00") == "2025-12-31T23:00:00Z"
    for bad in ("2026-10-06T09:15Z", "2026-10-06T09:15:42", "2026-02-30T09:15:42Z"):
        with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
            render_key_time(bad)


def test_types_ids_ulids_and_hashes_by_their_canonical_forms() -> None:
    assert _matches("uuid", "6f1c2e3a-8b4d-4c7e-9a21-0d5e7f3b9c11")
    assert not _matches("uuid", "6F1C2E3A-8B4D-4C7E-9A21-0D5E7F3B9C11")
    assert _matches("ulid", "01J9N2Q7Z4T8X1V6M3K0H5R2WB")
    assert not _matches("ulid", "81J9N2Q7Z4T8X1V6M3K0H5R2WB")
    assert not _matches("ulid", "01J9N2Q7Z4T8X1V6M3K0H5R2WI")
    assert _matches("prefixedSha256", "sha256:" + "a" * 64)
    assert not _matches("sha256Hex", "A" * 64)


def test_builds_the_four_forms() -> None:
    assert candidate_key_from_id("x", "1234567890") == "x:1234567890"
    assert candidate_key_from_id("youtube", "UCabcDEF123") == "youtube:UCabcDEF123"
    assert (
        candidate_key_from_handle("instagram", "@Example_Store_IQ") == "instagram:example_store_iq"
    )
    assert facebook_group_candidate_key("123456789012345") == "facebook:group:123456789012345"
    assert news_site_candidate_key("Example-Daily.IQ") == "news:site:example-daily.iq"


def test_parses_each_form() -> None:
    assert parse_candidate_key("facebook:group:123") == {
        "platform": "facebook",
        "form": "group",
        "value": "123",
    }
    assert parse_candidate_key("news:site:example.iq") == {
        "platform": "news",
        "form": "site",
        "value": "example.iq",
    }
    assert parse_candidate_key("x:1234567890") == {
        "platform": "x",
        "form": "account",
        "value": "1234567890",
    }


def test_keeps_a_linkedin_organisation_urn_colons_included_as_the_id_form() -> None:
    assert (
        candidate_key_from_id("linkedin", "urn:li:organization:1234567")
        == "linkedin:urn:li:organization:1234567"
    )
    assert parse_candidate_key("linkedin:urn:li:organization:1234567") == {
        "platform": "linkedin",
        "form": "account",
        "value": "urn:li:organization:1234567",
    }
    assert _matches("candidateKey", "linkedin:urn:li:organization:1234567")
    assert not _matches("candidateKey", "x:12:34")
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        candidate_key_from_id("x", "12:34")


def test_refuses_keys_outside_the_four_forms() -> None:
    for bad in ("news:example.iq", "instagram:post:Cx4kQ2LsT9m"):
        with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
            parse_candidate_key(bad)
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        candidate_key_from_handle("web", "x")
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        news_site_candidate_key("localhost")


def test_builds_and_parses_an_archive_reference_with_a_six_digit_batch() -> None:
    ref = raw_ref("green", "facebook", "2026-10-06", "fb-page-feed-poller", 123, 42)
    assert ref == "raw/green/facebook/2026/10/06/fb-page-feed-poller/000123.jsonl.zst#42"
    assert parse_raw_ref(ref) == {
        "route": "green",
        "platform": "facebook",
        "date": "2026-10-06",
        "service": "fb-page-feed-poller",
        "batch": 123,
        "line": 42,
    }


def test_refuses_a_batch_beyond_six_digits_and_a_malformed_reference() -> None:
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        raw_ref("green", "x", "2026-10-06", "x-recent-search", 1_000_000, 1)
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        parse_raw_ref("raw/green/x/2026/10/06/x-recent-search/0042.jsonl.zst#310")
