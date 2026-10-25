"""Shared by the Python suites: the fixtures under fixtures/contracts/ are the record both languages
test against."""

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

FIXTURES_DIR = Path(__file__).resolve().parents[4] / "fixtures" / "contracts"
PACKAGE_DIR = Path(__file__).resolve().parents[2]
REPO_DIR = Path(__file__).resolve().parents[4]

FixtureKind = Literal["valid", "invalid", "tolerant"]
# The sidecars of a fixture directory are not fixtures.
SIDECARS = {"expected.json", "options.json"}


def golden(name: str) -> Any:
    """A golden file, read field by field in the tests."""
    return read_json(FIXTURES_DIR / "golden" / name)


def _refuse_constant(name: str) -> Any:
    raise ValueError(f"{name} is not JSON")


def read_json(path: Path) -> Any:
    # NaN and Infinity are not JSON; JavaScript's parser refuses them, so this one does too.
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=_refuse_constant)


@dataclass(frozen=True)
class Fixture:
    """A fixture: its value, the queue and client type it is validated with, and for an invalid
    one the path of the error it must raise and the rule it breaks."""

    name: str
    file: str
    value: Any
    options: dict[str, Any] = field(default_factory=lambda: {})
    path: list[str | int] | None = None
    rule: str | None = None

    def copy(self) -> Any:
        return copy.deepcopy(self.value)


def schema_dirs() -> list[str]:
    """Every schema directory: `<topic>/v1`, `job/v1`, and `dlq/v1` for dlq.<service>/v1."""
    return sorted(
        f"{topic.name}/{version.name}"
        for topic in FIXTURES_DIR.iterdir()
        if topic.is_dir() and topic.name != "golden"
        for version in topic.iterdir()
    )


def schema_id_of(directory: str) -> str:
    return "dlq.<service>/v1" if directory == "dlq/v1" else directory


def _options(entry: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if "queue" in entry:
        out["queue"] = entry["queue"]
    if "client_type" in entry:
        out["client_type"] = entry["client_type"]
    return out


def fixtures(directory: str, kind: FixtureKind) -> list[Fixture]:
    base = FIXTURES_DIR / directory / kind
    if not base.exists():
        return []
    sidecar_path = base / ("expected.json" if kind == "invalid" else "options.json")
    sidecar: dict[str, Any] = read_json(sidecar_path) if sidecar_path.exists() else {}
    out: list[Fixture] = []
    for path in sorted(base.glob("*.json")):
        if path.name in SIDECARS:
            continue
        entry: dict[str, Any] = sidecar.get(path.name, {})
        if kind == "invalid" and ("path" not in entry or "rule" not in entry):
            raise AssertionError(f"{directory}/{kind}/{path.name} has no entry in expected.json")
        out.append(
            Fixture(
                name=f"{directory}/{kind}/{path.name}",
                file=path.name,
                value=read_json(path),
                options=_options(entry),
                path=entry.get("path"),
                rule=entry.get("rule"),
            )
        )
    return out


def fixture(directory: str, kind: FixtureKind, file: str) -> Fixture:
    found = [f for f in fixtures(directory, kind) if f.file == file]
    if not found:
        raise AssertionError(f"no fixture {directory}/{kind}/{file}")
    return found[0]
