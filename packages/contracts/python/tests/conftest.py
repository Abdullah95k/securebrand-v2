"""Shared by the Python suites: the fixtures under fixtures/contracts/ are the record both languages
test against."""

import json
from pathlib import Path
from typing import Any

FIXTURES_DIR = Path(__file__).resolve().parents[4] / "fixtures" / "contracts"
PACKAGE_DIR = Path(__file__).resolve().parents[2]


def golden(name: str) -> Any:
    """A golden file, read field by field in the tests."""
    return read_json(FIXTURES_DIR / "golden" / name)


def _refuse_constant(name: str) -> Any:
    raise ValueError(f"{name} is not JSON")


def read_json(path: Path) -> Any:
    # NaN and Infinity are not JSON; JavaScript's parser refuses them, so this one does too.
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=_refuse_constant)
