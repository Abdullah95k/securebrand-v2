"""D-4: both languages report a shape error at the same paths under the discriminated unions;
fixtures/contracts/golden/issue-paths.json records TypeScript's (scripts/issue-paths.ts)."""

import importlib
import inspect
from typing import Any, cast

import pytest
from pydantic import BaseModel

# The unions the validator found, to check them against the generated classes.
from listening_contracts.validate import _unions, validate  # pyright: ignore[reportPrivateUsage]
from listening_contracts.versions import catalogue_entry, catalogue_id

from conftest import fixture, fixtures, golden, schema_dirs, schema_id_of

G = golden("issue-paths.json")
MODES = ("producer", "consumer")


def _paths(result: Any) -> set[tuple[str | int, ...]]:
    return set() if result.ok else {tuple(i["path"]) for i in result.issues}


def _class_names(schema_id: str) -> set[str]:
    entry = catalogue_entry(schema_id)
    assert entry is not None
    names: set[str] = set()
    for variant in ("strict", "consumer"):
        module = importlib.import_module(f"listening_contracts.models.{variant}.{entry['module']}")
        names |= {
            n for n, c in inspect.getmembers(module, inspect.isclass) if issubclass(c, BaseModel)
        }
    return names


def test_finds_the_13_discriminated_unions_and_each_branch_is_a_generated_class() -> None:
    found = 0
    for directory in schema_dirs():
        schema_id = schema_id_of(directory)
        unions = _unions(catalogue_id(schema_id))
        assert set(unions) <= _class_names(schema_id), directory
        found += len({tuple(u.tags) for u in unions.values()})
    assert found == 13


def test_reports_only_the_selected_branch_of_a_discriminated_union() -> None:
    deletion = fixture("deletions/v1", "valid", "author-request.json").value
    result = validate("deletions/v1", {**deletion, "batch_size": 500}, "producer")
    assert sorted(_paths(result)) == [("batch_size",)]
    job = fixture("job/v1", "invalid", "carries-priority.json")
    result = validate("job/v1", job.value, "producer", **job.options)
    assert sorted(_paths(result)) == [("priority",)]


def test_reports_a_bad_discriminator_at_the_discriminator() -> None:
    deletion = fixture("deletions/v1", "valid", "author-request.json").value
    for mode in MODES:
        result = validate("deletions/v1", {**deletion, "scope": "nobody"}, mode)
        assert sorted(_paths(result)) == [("scope",)], mode


def test_no_path_names_a_branch_and_every_inner_step_is_in_the_message() -> None:
    """Over every invalid and tolerant fixture in both modes."""
    bad: list[tuple[str, str, list[str | int]]] = []
    for directory in schema_dirs():
        labels = _class_names(schema_id_of(directory)) | {"missing-sentinel"}
        for kind in ("invalid", "tolerant"):
            for f in fixtures(directory, kind):
                for mode in MODES:
                    result = validate(schema_id_of(directory), f.value, mode, **f.options)
                    for issue in [] if result.ok else result.issues:
                        path = issue["path"]
                        node: object = f.value
                        for step in path[:-1]:
                            if isinstance(node, dict) and step in node:
                                node = cast(dict[str | int, object], node)[step]
                            elif isinstance(node, list) and isinstance(step, int):
                                items = cast(list[object], node)
                                if not 0 <= step < len(items):
                                    bad.append((f.name, mode, path))
                                    break
                                node = items[step]
                            else:
                                bad.append((f.name, mode, path))
                                break
                        if any(step in labels for step in path if isinstance(step, str)):
                            bad.append((f.name, mode, path))
    assert bad == []


@pytest.mark.parametrize(
    "c", [pytest.param(c, id=f"{c['schema']}/{c['file']} {c['mode']}") for c in G["cases"]]
)
def test_reports_the_golden_paths_or_under_a_plain_union_the_verdict_and_the_expected_path(
    c: dict[str, Any],
) -> None:
    kind, file = c["file"].split("/")
    f = fixture(c["schema"], kind, file)
    got = _paths(validate(schema_id_of(c["schema"]), f.value, c["mode"], **f.options))
    if c["check"] == "equal":
        assert got == {tuple(p) for p in c["paths"]}
        return
    assert (len(got) == 0) == (len(c["paths"]) == 0), "the verdict"
    if kind == "invalid" and c["mode"] == "producer":
        assert tuple(f.path or []) in got, got


def test_records_every_invalid_and_tolerant_fixture_in_both_modes() -> None:
    recorded = {f"{c['schema']}/{c['file']} {c['mode']}" for c in G["cases"]}
    every = [
        f"{directory}/{kind}/{f.file} {mode}"
        for directory in schema_dirs()
        for kind in ("invalid", "tolerant")
        for f in fixtures(directory, kind)
        for mode in MODES
    ]
    assert [c for c in every if c not in recorded] == []
    assert len(recorded) == len(every)
