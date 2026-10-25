from typing import Any

import pytest

from listening_contracts.registries import (
    job_key_fields,
    partition_key,
    producer_rows,
    topic_key_fields,
    topic_writers,
)

from conftest import golden

G = golden("partition-keys.json")


def _named(cases: list[dict[str, Any]]) -> list[Any]:
    return [pytest.param(c, id=c["name"]) for c in cases]


def test_every_topic_and_queue_has_one_declared_key() -> None:
    for schema in topic_writers():
        if schema == "jobs.completed/v1":
            continue  # the key of the job it reports
        assert topic_key_fields(schema) is not None, schema
    assert topic_key_fields("registry.decisions/v1") == [
        "candidate_key",
        "author_ref",
        "source_id",
        "platform",
        "keyword_id",
    ]
    for row in producer_rows():
        assert job_key_fields(row["queue"], row["kind"]), (row["queue"], row["kind"])


@pytest.mark.parametrize("c", _named(G["cases"]))
def test_returns_the_key_of_every_golden_message(c: dict[str, Any]) -> None:
    assert partition_key(c["schema"], c["message"], queue=c.get("queue")) == c["key"]


@pytest.mark.parametrize("c", _named(G["refusals"]))
def test_refuses_a_message_with_no_key(c: dict[str, Any]) -> None:
    with pytest.raises(ValueError):  # noqa: PT011 - every refusal is a ContractError, a ValueError
        partition_key(c["schema"], c["message"], queue=c.get("queue"))
