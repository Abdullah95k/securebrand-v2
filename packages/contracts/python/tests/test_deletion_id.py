from typing import Any

import pytest

from listening_contracts.errors import ContractError
from listening_contracts.keys import deletion_id

from conftest import golden

G = golden("deletion-id.json")
BY_NAME: dict[str, str] = {c["name"]: c["deletion_id"] for c in G["deletion_ids"]}


@pytest.mark.parametrize("c", [pytest.param(c, id=c["name"]) for c in G["deletion_ids"]])
def test_derives_the_golden_deletion_ids(c: dict[str, Any]) -> None:
    i = c["input"]
    assert (
        deletion_id(i["reason"], i["scope"], i["key"], i["mode"], i["signal_at"], i["target"])
        == c["deletion_id"]
    )


def test_target_order_does_not_change_the_id() -> None:
    assert BY_NAME["item scope, platform sync"] == BY_NAME["target order does not change the id"]


def test_two_clients_with_equal_targets_get_different_ids() -> None:
    assert (
        BY_NAME["client offboarding, client X"]
        != BY_NAME["client offboarding, client Y with an equal target"]
    )


def test_two_authors_with_equal_targets_get_different_ids() -> None:
    assert (
        BY_NAME["author request, author 1"]
        != BY_NAME["author request, author 2 with an equal target"]
    )


def test_purge_text_then_delete_of_one_item_get_different_ids() -> None:
    assert (
        BY_NAME["retention purge_text of one item"] != BY_NAME["retention delete of the same item"]
    )


def test_one_author_under_two_keys_gets_one_id_per_key() -> None:
    assert (
        BY_NAME["author request, author 1"]
        != BY_NAME["author request, author 1 under the second key"]
    )


def test_the_same_signal_on_another_day_gets_a_new_id() -> None:
    assert (
        BY_NAME["item scope, platform sync"]
        != BY_NAME["the same signal on another day gets a new id"]
    )


def test_a_same_day_replay_keeps_its_id() -> None:
    assert BY_NAME["item scope, platform sync"] == BY_NAME["a same-day replay keeps its id"]


def test_refuses_a_signal_at_that_is_not_a_utc_timestamp() -> None:
    i = G["deletion_ids"][0]["input"]
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        deletion_id(i["reason"], i["scope"], i["key"], i["mode"], "2026-10-06", i["target"])


def test_refuses_a_target_holding_a_lone_surrogate_as_typescript_does() -> None:
    i = G["deletion_ids"][0]["input"]
    for extra in ({"kind": "\ud800"}, {"x": ["\udc00"]}):
        target = {**i["target"], **extra}
        with pytest.raises(ContractError, match="not_unicode"):
            deletion_id(i["reason"], i["scope"], i["key"], i["mode"], i["signal_at"], target)
