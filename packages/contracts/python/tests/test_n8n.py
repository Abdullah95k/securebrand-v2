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


def test_names_a_government_alert_by_keyword_or_request_only_at_the_keyword_level() -> None:
    """Note 12."""
    f = fixture(ALERT, "valid", "government-keyword-level.json")
    cases: list[tuple[list[str], object, str]] = [
        (["subject", "candidate_key"], "x:example_poster_x", "government_subject"),
        (["subject", "route"], "green", "government_subject"),
        (["subject", "vendor"], None, "government_subject"),
        (["details", "scope", "level"], "keyword_source", "government_scope"),
    ]
    for path, v, code in cases:
        value = f.copy()
        node: Any = value
        for step in path[:-1]:
            node = node[step]
        node[path[-1]] = v
        result = validate(ALERT, value, "producer", client_type="government")
        assert [path, code] in [[i["path"], i["code"]] for i in result.issues], path
        assert validate(ALERT, value, "producer", client_type="commercial").ok, path


def test_fails_closed_on_a_client_type_other_than_commercial_or_government() -> None:
    """Note 13."""
    f = fixture(ALERT, "valid", "prd-alert-evaluator.json")
    for client_type in ("Government", "gov", ""):
        result = validate(ALERT, f.value, "producer", client_type=client_type)  # type: ignore[arg-type]
        assert [[i["path"], i["code"]] for i in result.issues] == [[[], "no_client_type"]], (
            client_type
        )
        assert validate(ALERT, f.value, "consumer", client_type=client_type).ok  # type: ignore[arg-type]


def test_sends_an_automatic_fallback_notice_to_ops_only() -> None:
    """ADR-0021 L58; note 12."""
    f = fixture(ALERT, "valid", "source-fallback-notice.json")
    for audience in ("client", "account_manager"):
        value = {
            **f.copy(),
            "audience": audience,
            "client_id": "c7f12d45-b7c5-467d-aa82-e7826ed8abf2",
        }
        result = validate(ALERT, value, "producer", client_type="commercial")
        assert fails_at(result, ["audience"]), audience


def test_keys_the_government_fixtures_fingerprint_on_its_keyword() -> None:
    """alert-evaluator L63; D-11."""
    details = fixture(ALERT, "valid", "government-keyword-level.json").value["details"]
    keyword_id: str = details["keyword"]["keyword_id"]
    assert details["fingerprint"].split(":")[2] == keyword_id[:8]


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
