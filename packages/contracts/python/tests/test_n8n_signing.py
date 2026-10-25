"""A30: the n8n signing helper, one HMAC scheme over the body with a timestamp and an idempotency
key (ADR-0067; Q11, F-49). The clock is an argument: no helper reads one."""

import pytest

from listening_contracts.errors import ContractError
from listening_contracts.n8n import sign_n8n, verify_n8n

from conftest import golden

G = golden("n8n-signing.json")


def test_signs_the_golden_requests_byte_for_byte() -> None:
    for c in G["sign"]:
        headers = sign_n8n(
            c["body"].encode(), G["secret"].encode(), c["timestamp"], c["idempotency_key"]
        )
        assert headers == c["headers"]
        assert (
            sign_n8n(c["body"], G["secret"], c["timestamp"], c["idempotency_key"]) == c["headers"]
        )


def test_rejects_a_changed_body_a_timestamp_outside_the_tolerance_and_a_wrong_key() -> None:
    for c in G["verify"]:
        result = verify_n8n(
            c["body"].encode(), c["headers"], G["secret"].encode(), c["now"], c["tolerance_seconds"]
        )
        want = {"ok": True} if c["ok"] else {"ok": False, "reason": c["reason"]}
        assert result == want, c["case"]


def test_verifies_what_it_signs_with_a_tolerance_of_300_seconds_by_default() -> None:
    headers = sign_n8n("{}", G["secret"], 1_791_275_832, "k:email")
    assert verify_n8n("{}", headers, G["secret"], 1_791_276_132) == {"ok": True}
    assert verify_n8n("{}", headers, G["secret"], 1_791_276_133) == {
        "ok": False,
        "reason": "stale_timestamp",
    }


def test_refuses_to_sign_with_a_bad_timestamp_or_an_empty_idempotency_key() -> None:
    with pytest.raises(ContractError, match="bad_timestamp"):
        sign_n8n("{}", G["secret"], -1, "k:email")
    with pytest.raises(ContractError, match="bad_timestamp"):
        sign_n8n("{}", G["secret"], True, "k:email")
    with pytest.raises(ContractError, match="bad_idempotency_key"):
        sign_n8n("{}", G["secret"], 1, "")
    with pytest.raises(ContractError, match="empty_secret"):
        sign_n8n("{}", "", 1, "k:email")
