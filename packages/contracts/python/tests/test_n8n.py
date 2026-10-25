"""A30: n8n.alert/v1 and n8n.card/v1 with Q11's fields (ADR-0067, ADR-0048)."""

from typing import Any

from listening_contracts.keys import card_id
from listening_contracts.validate import ValidationResult, validate
from listening_contracts.vocabulary import VOCABULARY

from conftest import fixture, fixtures, golden

ALERT = "n8n.alert/v1"
CARD = "n8n.card/v1"


def fails_at(result: ValidationResult, path: list[str | int]) -> bool:
    return not result.ok and path in [i["path"] for i in result.issues]


def test_accepts_each_of_the_nine_rule_type_branches() -> None:
    seen: set[str] = set()
    for f in fixtures(ALERT, "valid"):
        rule_type = f.value["details"].get("rule_type")
        if rule_type is None:
            continue
        seen.add(rule_type)
        assert validate(ALERT, f.value, "producer", **f.options).ok, f.name
    assert sorted(seen) == sorted(VOCABULARY["ALERT_RULE_TYPES"])


def test_rejects_an_open_details_object() -> None:
    value = {
        **fixture(ALERT, "valid", "facts-budget.json").copy(),
        "details": {"note": "x", "level": 3},
    }
    assert fails_at(validate(ALERT, value), ["details", "note"])
    assert not validate(ALERT, value, "consumer").ok


def test_rejects_a_government_clients_alert_with_subject_source_id_or_subject_platform() -> None:
    f = fixture(ALERT, "valid", "government-keyword-level.json")
    assert validate(ALERT, f.value, "producer", client_type="government").ok
    for name, v in (
        ("source_id", "a3c0f1e2-5b6d-4c7e-9f80-112233445566"),
        ("platform", "facebook"),
    ):
        value = f.copy()
        value["subject"][name] = v
        assert fails_at(
            validate(ALERT, value, "producer", client_type="government"), ["subject", name]
        )
        assert validate(ALERT, value, "producer", client_type="commercial").ok, name
    # The producer passes the client type of a client's alert, or the alert fails closed.
    assert not validate(ALERT, f.value).ok
    assert validate(ALERT, f.value, "consumer").ok


def test_requires_each_card_types_fields() -> None:
    required = {
        "qualifier_review": "buttons",
        "grant_missing": "regrant_url",
        "manual_url": "inputs",
    }
    seen: set[str] = set()
    for f in fixtures(CARD, "valid"):
        card_type = f.value["card_type"]
        seen.add(card_type)
        value = f.copy()
        del value[required[card_type]]
        assert fails_at(validate(CARD, value), [required[card_type]]), f.name
    assert sorted(seen) == sorted(VOCABULARY["CARD_TYPES"])


def test_derives_the_golden_card_ids() -> None:
    for case in golden("ids.json")["card_ids"]:
        i = case["input"]
        assert card_id(i["card_type"], i["subject_key"], i["ref"]) == case["card_id"]
    for f in fixtures(CARD, "valid"):
        v: dict[str, Any] = f.value
        subject = v["subject"]
        key = subject.get("candidate_key") or subject["source_id"]
        ref = subject.get("decision_id") or subject["request_id"]
        assert v["card_id"] == card_id(v["card_type"], key, ref), f.name
