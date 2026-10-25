"""The data the twin shares with the TypeScript fold, read from the files themselves so that the two
languages cannot drift (D10, Q6): packages/text/data/fold-table.json, and LANG_LABELS from
schemas/vocabulary.json, the artefact contracts publishes for Python. Both are found beside this
source tree, as contracts finds its own.

The fold table is parsed strictly: a key the twin does not know is refused rather than ignored, so a
row added to the table cannot leave the twin silently folding by the old rules.
"""

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast

PACKAGE_DIR = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = PACKAGE_DIR.parent / "contracts"
FOLD_TABLE = PACKAGE_DIR / "data" / "fold-table.json"
UNICODE_DATA = PACKAGE_DIR / "data" / "unicode-15.1.json"
UNASSIGNED = CONTRACTS_DIR / "registries" / "unicode-15.1-unassigned.json"
VOCABULARY = CONTRACTS_DIR / "schemas" / "vocabulary.json"

type Ranges = tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class DigitRange:
    first: int
    last: int
    becomes_first: int


@dataclass(frozen=True)
class FoldTable:
    """fold-table.json, every code point decoded from its U+XXXX spelling."""

    version: str
    unicode: str
    sorani_labels: tuple[str, ...]
    sorani_only_letters: tuple[str, ...]
    row0_sequence: str
    row0_becomes: str
    row1_deleted: Ranges
    row2_deleted: Ranges
    alef_letters: tuple[str, ...]
    alef: str
    alef_marks_deleted: Ranges
    arabic: Mapping[str, str]
    sorani: Mapping[str, str]
    digits: tuple[DigitRange, ...]
    url_prefixes: tuple[str, ...]
    tag_signs: tuple[str, ...]
    tag_joiner: str
    space_instead: Ranges


_CODE_POINT = re.compile(r"U\+([0-9A-F]{4,6})")


def _object(value: object, where: str, keys: set[str] | None = None) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{where} is not an object")
    found = cast("dict[str, object]", value)
    if keys is not None and set(found) != keys:
        raise ValueError(f"{where} has the keys {sorted(found)}, not {sorted(keys)}")
    return found


def _list(value: object, where: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{where} is not a list")
    return cast("list[object]", value)


def _str(value: object, where: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{where} is not a string")
    return value


def _strs(value: object, where: str) -> tuple[str, ...]:
    return tuple(_str(item, f"{where}[{i}]") for i, item in enumerate(_list(value, where)))


def _char(value: object, where: str) -> str:
    """One code point, written U+XXXX."""
    match = _CODE_POINT.fullmatch(_str(value, where))
    cp = int(match.group(1), 16) if match else -1
    if not 0 <= cp <= 0x10FFFF or 0xD800 <= cp <= 0xDFFF:
        raise ValueError(f"{where} is not a code point written U+XXXX")
    return chr(cp)


def _chars(value: object, where: str) -> tuple[str, ...]:
    return tuple(_char(item, f"{where}[{i}]") for i, item in enumerate(_list(value, where)))


def _ranges(value: object, where: str) -> Ranges:
    out: list[tuple[int, int]] = []
    for i, item in enumerate(_list(value, where)):
        pair = _chars(item, f"{where}[{i}]")
        if len(pair) != 2 or pair[0] > pair[1]:
            raise ValueError(f"{where}[{i}] is not a [first, last] range")
        out.append((ord(pair[0]), ord(pair[1])))
    return tuple(out)


def _char_map(value: object, where: str) -> dict[str, str]:
    found = _object(value, where)
    return {
        _char(key, f"{where} key {key}"): _char(to, f"{where}.{key}") for key, to in found.items()
    }


def _digits(value: object, where: str) -> tuple[DigitRange, ...]:
    out: list[DigitRange] = []
    for i, item in enumerate(_list(value, where)):
        row = _object(item, f"{where}[{i}]", {"first", "last", "becomes_first"})
        first = ord(_char(row["first"], f"{where}[{i}].first"))
        last = ord(_char(row["last"], f"{where}[{i}].last"))
        becomes_first = ord(_char(row["becomes_first"], f"{where}[{i}].becomes_first"))
        if first > last:
            raise ValueError(f"{where}[{i}] runs backwards")
        out.append(DigitRange(first, last, becomes_first))
    return tuple(out)


_TOP_KEYS = {
    "version",
    "unicode",
    "specification",
    "sorani_labels",
    "sorani_only_letters",
    "row0_sorani",
    "row1_deleted",
    "row2_deleted",
    "row3_alef",
    "rows4to6",
    "row8_digits",
    "row10",
}


def parse_fold_table(raw: bytes) -> FoldTable:
    try:
        top = _object(json.loads(raw), "the table", _TOP_KEYS)
        row0 = _object(top["row0_sorani"], "row0_sorani", {"sequence", "becomes"})
        row3 = _object(top["row3_alef"], "row3_alef", {"letters", "becomes", "marks_deleted_after"})
        rows4to6 = _object(top["rows4to6"], "rows4to6", {"arabic", "sorani"})
        row10_keys = {"url_prefixes", "tag_signs", "tag_joiner", "space_instead"}
        row10 = _object(top["row10"], "row10", row10_keys)
        return FoldTable(
            version=_str(top["version"], "version"),
            unicode=_str(top["unicode"], "unicode"),
            sorani_labels=_strs(top["sorani_labels"], "sorani_labels"),
            sorani_only_letters=_chars(top["sorani_only_letters"], "sorani_only_letters"),
            row0_sequence="".join(_chars(row0["sequence"], "row0_sorani.sequence")),
            row0_becomes=_char(row0["becomes"], "row0_sorani.becomes"),
            row1_deleted=_ranges(top["row1_deleted"], "row1_deleted"),
            row2_deleted=_ranges(top["row2_deleted"], "row2_deleted"),
            alef_letters=_chars(row3["letters"], "row3_alef.letters"),
            alef=_char(row3["becomes"], "row3_alef.becomes"),
            alef_marks_deleted=_ranges(
                row3["marks_deleted_after"], "row3_alef.marks_deleted_after"
            ),
            arabic=_char_map(rows4to6["arabic"], "rows4to6.arabic"),
            sorani=_char_map(rows4to6["sorani"], "rows4to6.sorani"),
            digits=_digits(top["row8_digits"], "row8_digits"),
            url_prefixes=_strs(row10["url_prefixes"], "row10.url_prefixes"),
            tag_signs=_chars(row10["tag_signs"], "row10.tag_signs"),
            tag_joiner=_char(row10["tag_joiner"], "row10.tag_joiner"),
            space_instead=_ranges(row10["space_instead"], "row10.space_instead"),
        )
    except ValueError as error:
        raise ValueError(f"{FOLD_TABLE.name}: {error}") from None


def _lang_labels() -> tuple[str, ...]:
    try:
        vocabulary = _object(json.loads(VOCABULARY.read_text(encoding="utf-8")), "the vocabulary")
        labels = _strs(vocabulary.get("LANG_LABELS"), "LANG_LABELS")
    except ValueError as error:
        raise ValueError(f"{VOCABULARY.name}: {error}") from None
    if not labels:
        raise ValueError(f"{VOCABULARY.name}: LANG_LABELS is empty")
    return labels


def _data_sha256(fold_table: bytes) -> str:
    """FOLD_DATA_SHA256 (D10): one "<file name> <sha256 hex>" line per file, and the hash of those
    lines. The 15.1 data and the unassigned ranges are the TypeScript fold's; hashing them here
    makes the version guard cover the same data in both languages."""
    digests = (
        (FOLD_TABLE.name, hashlib.sha256(fold_table).hexdigest()),
        (UNICODE_DATA.name, hashlib.sha256(UNICODE_DATA.read_bytes()).hexdigest()),
        (UNASSIGNED.name, hashlib.sha256(UNASSIGNED.read_bytes()).hexdigest()),
    )
    lines = "".join(f"{name} {digest}\n" for name, digest in digests)
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


# Read once: the bytes hashed are the bytes parsed.
_RAW_TABLE = FOLD_TABLE.read_bytes()
TABLE = parse_fold_table(_RAW_TABLE)
LANG_LABELS = _lang_labels()
DATA_SHA256 = _data_sha256(_RAW_TABLE)
