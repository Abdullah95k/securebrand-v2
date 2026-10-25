from typing import Any

import pytest

from listening_contracts.keys import NS_CARDS, NS_HITS, analysis_key, card_id, hit_id
from listening_contracts.ulid import comment_decay_job_id, deterministic_ulid, hit_message_id

from conftest import golden

G = golden("ids.json")


def test_freezes_the_namespaces_the_golden_file_records() -> None:
    assert G["ns_hits"] == NS_HITS
    assert G["ns_cards"] == NS_CARDS


def test_derives_the_golden_uuid_v5_ids_and_deterministic_ulids() -> None:
    for c in G["hit_ids"]:
        i = c["input"]
        assert hit_id(i["item_id"], i["client_id"], i["keyword_id"]) == c["hit_id"]
    for c in G["card_ids"]:
        i = c["input"]
        assert card_id(i["card_type"], i["subject_key"], i["ref"]) == c["card_id"]
    for c in G["ulids"]:
        assert deterministic_ulid(c["input"]["time"], c["input"]["fields"]) == c["ulid"]
    for c in G["hit_message_ids"]:
        i = c["input"]
        assert (
            hit_message_id(i["hit_at"], i["hit_id"], i["item_version"], i["keyword_set_version"])
            == c["message_id"]
        )
    for c in G["comment_decay_job_ids"]:
        i = c["input"]
        assert (
            comment_decay_job_id(i["due_at"], i["item_id"], i["lane"], i["series_step"])
            == c["job_id"]
        )


def test_a_replayed_input_gives_the_same_id() -> None:
    i = G["hit_message_ids"][0]["input"]
    args = (i["hit_at"], i["hit_id"], i["item_version"], i["keyword_set_version"])
    assert hit_message_id(*args) == hit_message_id(*args)
    assert deterministic_ulid("2026-10-06T08:51:40Z", ["a"]) == deterministic_ulid(
        "2026-10-06T08:51:40Z", ["a"]
    )


def test_a_new_item_version_gives_a_new_hit_message_id() -> None:
    v1, v2 = G["hit_message_ids"][:2]
    assert v1["message_id"] != v2["message_id"]


def test_the_ulid_s_time_part_is_the_event_s_own_time() -> None:
    a = deterministic_ulid("2026-10-06T08:51:40.123Z", ["a"])
    b = deterministic_ulid("2026-10-06T08:51:40.123Z", ["b"])
    assert a[:10] == b[:10]
    assert a != b


def test_refuses_a_time_that_is_not_a_utc_timestamp() -> None:
    for t in ("2026-10-06T08:51:40+03:00", "2026-10-06"):
        with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
            deterministic_ulid(t, ["a"])


def test_builds_the_analysis_key() -> None:
    for c in G["analysis_keys"]:
        i = c["input"]
        assert analysis_key(i["item_id"], i["task"], i["model_version"]) == c["analysis_key"]


@pytest.mark.parametrize("c", [pytest.param(c, id=c["name"]) for c in G["analysis_rejects"]])
def test_refuses_a_task_holding_a_colon(c: dict[str, Any]) -> None:
    i = c["input"]
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        analysis_key(i["item_id"], i["task"], i["model_version"])
