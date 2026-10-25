"""RFC 8785 canonical JSON through the `rfc8785` library; values JSON cannot carry, and strings
holding a lone surrogate, are refused first with the package's own errors, as in TypeScript."""

import math
from typing import Any, cast

import rfc8785

from listening_contracts._text import require_str
from listening_contracts.errors import ContractError


def _check(value: object, path: str) -> None:
    if value is None or isinstance(value, (bool, int)):
        return
    if isinstance(value, str):
        require_str(value, path)
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractError("not_json", f"{path} is not a finite number")
        return
    if isinstance(value, list):
        for i, v in enumerate(cast(list[object], value)):
            _check(v, f"{path}[{i}]")
        return
    if isinstance(value, dict):
        for k, v in cast(dict[object, object], value).items():
            if not isinstance(k, str):
                raise ContractError("not_json", f"{path} has a key that is not a string")
            require_str(k, f"a key of {path}")
            _check(v, f"{path}.{k}")
        return
    raise ContractError("not_json", f"{path} is not a JSON value")


def canonical_json(value: object) -> str:
    _check(value, "$")
    try:
        # _check has proved `value` a JSON value; rfc8785 types its input with a private alias.
        return rfc8785.dumps(cast(Any, value)).decode("utf-8")
    except rfc8785.CanonicalizationError as e:
        raise ContractError("not_json", str(e)) from None
