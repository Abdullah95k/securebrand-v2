"""D10: the fold table is data, read strictly, as the TypeScript fold reads it (data.ts): a key
the twin does not know, or one it needs and does not find, is refused, so a row added to or renamed
in the table cannot leave the twin silently folding by the old rules."""

import json
from typing import Any

import pytest

from text_fold._data import parse_fold_table

from conftest import FOLD_TABLE


def _table() -> dict[str, Any]:
    return json.loads(FOLD_TABLE.read_text(encoding="utf-8"))


def _raw(table: dict[str, Any]) -> bytes:
    return json.dumps(table).encode("utf-8")


def test_accepts_the_committed_fold_table() -> None:
    assert parse_fold_table(FOLD_TABLE.read_bytes()).version == "fold-1"


def test_refuses_a_key_the_twin_does_not_know_at_the_top_or_inside_a_row() -> None:
    with pytest.raises(ValueError, match="row7_kept"):
        parse_fold_table(_raw({**_table(), "row7_kept": []}))
    table = _table()
    table["row10"]["tag_end"] = "U+0020"
    with pytest.raises(ValueError, match="tag_end"):
        parse_fold_table(_raw(table))


def test_refuses_a_table_missing_a_key_the_twin_needs() -> None:
    table = _table()
    del table["row3_alef"]["marks_deleted_after"]
    with pytest.raises(ValueError, match="marks_deleted_after"):
        parse_fold_table(_raw(table))
    digits = _table()
    del digits["row8_digits"][0]["becomes_first"]
    with pytest.raises(ValueError, match="becomes_first"):
        parse_fold_table(_raw(digits))
