"""The primitive patterns, as the TypeScript source exports them (schemas/patterns.json)."""

import re
from typing import cast

from listening_contracts._artefacts import artefact

PATTERNS: dict[str, str] = cast(dict[str, str], artefact("patterns.json"))


def matches(name: str, value: object) -> bool:
    """True when `value` is a string matching the whole pattern `name`."""
    return isinstance(value, str) and re.fullmatch(PATTERNS[name], value) is not None
