"""The data shared with the TypeScript package: the registries under
packages/contracts/registries/ and the artefacts the TypeScript exporter writes under
packages/contracts/schemas/. Both are read from the package directory beside this source tree, so
the two languages cannot drift."""

import json
from functools import cache
from pathlib import Path
from typing import NoReturn

PACKAGE_DIR = Path(__file__).resolve().parents[2]


def _refuse_constant(name: str) -> NoReturn:
    raise ValueError(f"{name} is not JSON")


@cache
def registry(name: str) -> object:
    return json.loads((PACKAGE_DIR / "registries" / name).read_text(encoding="utf-8"))


@cache
def artefact(path: str) -> object:
    text = (PACKAGE_DIR / "schemas" / path).read_text(encoding="utf-8")
    return json.loads(text, parse_constant=_refuse_constant)
