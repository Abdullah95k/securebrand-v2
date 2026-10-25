"""The conformance suite (A4, A6, A28, A29): every fixture under fixtures/contracts/ validated as a
producer and as a consumer would, as test/conformance/fixtures.test.ts does; both must agree on
every file (G0 check 2)."""

import pytest

from listening_contracts.validate import validate

from conftest import Fixture, fixtures, schema_dirs, schema_id_of

CASES = [(d, f) for d in schema_dirs() for f in fixtures(d, "valid")]
INVALID = [(d, f) for d in schema_dirs() for f in fixtures(d, "invalid")]
TOLERANT = [(d, f) for d in schema_dirs() for f in fixtures(d, "tolerant")]


def test_finds_the_schema_directories() -> None:
    assert len(schema_dirs()) >= 17


@pytest.mark.parametrize(("directory", "f"), CASES, ids=[f.name for _, f in CASES])
def test_accepts_every_valid_fixture(directory: str, f: Fixture) -> None:
    for mode in ("producer", "consumer"):
        result = validate(schema_id_of(directory), f.value, mode, **f.options)
        assert result.issues == [], f"{f.name} as a {mode}"
        assert result.ok


@pytest.mark.parametrize(("directory", "f"), INVALID, ids=[f.name for _, f in INVALID])
def test_rejects_every_invalid_fixture_at_the_expected_path(directory: str, f: Fixture) -> None:
    result = validate(schema_id_of(directory), f.value, "producer", **f.options)
    assert not result.ok, f"{f.name} was accepted; it breaks: {f.rule}"
    paths = [i["path"] for i in result.issues]
    assert f.path in paths, f"{f.name}: no issue at {f.path}; got {paths}"


@pytest.mark.parametrize(("directory", "f"), TOLERANT, ids=[f.name for _, f in TOLERANT])
def test_accepts_a_tolerant_fixture_as_a_consumer_and_rejects_it_as_a_producer(
    directory: str, f: Fixture
) -> None:
    assert validate(schema_id_of(directory), f.value, "consumer", **f.options).ok
    assert not validate(schema_id_of(directory), f.value, "producer", **f.options).ok
