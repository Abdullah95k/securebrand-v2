"""A17: the four metadata fields on every message (ADR-0002), and the version classifier."""

from listening_contracts.validate import validate
from listening_contracts.versions import CATALOGUE, classify_version

from conftest import fixtures, schema_dirs, schema_id_of

FIELDS = ("schema", "message_id", "produced_at", "producer")
DIR_OF = {schema_id_of(d): d for d in schema_dirs()}


def test_every_message_schema_requires_the_four_fields() -> None:
    for entry in CATALOGUE:
        sid = entry["id"]
        directory = DIR_OF[sid]
        f = fixtures(directory, "valid")[0]
        prefix: list[str | int] = ["envelope"] if sid == "raw.items/v1" else []
        for name in FIELDS:
            value = f.copy()
            holder = value["envelope"] if prefix else value
            del holder[name]
            result = validate(sid, value, "producer", **f.options)
            assert not result.ok, f"{sid} without {name}"
            assert [*prefix, name] in [i["path"] for i in result.issues], f"{sid} {name}"
        named = [x for x in fixtures(directory, "invalid") if x.file.startswith("no-metadata-")]
        assert len(named) == 4, sid


def test_refuses_a_producer_without_its_service_version_or_job() -> None:
    f = fixtures("item.hits/v1", "valid")[0]
    for name in ("service", "version", "job_id"):
        value = f.copy()
        del value["producer"][name]
        assert not validate("item.hits/v1", value).ok, name


def test_classifies_a_known_unread_version_as_skip_and_an_unknown_one_as_park() -> None:
    assert classify_version("raw.items/v1", ["raw.items/v1"]) == "read"
    assert classify_version("item.hits/v1", ["raw.items/v1"]) == "skip"
    assert classify_version("raw.items/v2", ["raw.items/v1"]) == "park"
    assert classify_version("job/v2", ["job/v1"]) == "park"
    # dlq.<service>/v1 is one schema id whatever the service (F-52).
    assert classify_version("dlq.store-writer/v1", ["dlq.<service>/v1"]) == "read"
    assert classify_version("dlq.normalize-item/v1", ["raw.items/v1"]) == "skip"
    assert classify_version("dlq.normalize-item/v2", ["raw.items/v1"]) == "park"
