"""Helpers for the twin's tests. The files are located here, independently of text_fold, so that the
tests check the twin against the files themselves."""

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from text_fold import fold

PACKAGE_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = PACKAGE_DIR.parents[1]
GOLDEN = REPO_ROOT / "fixtures" / "text" / "golden.jsonl"
FOLD_TABLE = PACKAGE_DIR / "data" / "fold-table.json"
UNICODE_DATA = PACKAGE_DIR / "data" / "unicode-15.1.json"
FOLD_VERSIONS = PACKAGE_DIR / "data" / "fold-versions.json"
UNASSIGNED = REPO_ROOT / "packages" / "contracts" / "registries" / "unicode-15.1-unassigned.json"


@dataclass(frozen=True)
class GoldenCase:
    id: str
    lang: str
    title: str | None
    text: str | None
    text_norm: str


def golden_lines() -> list[dict[str, object]]:
    lines = GOLDEN.read_text(encoding="utf-8").splitlines()
    return [cast("dict[str, object]", json.loads(line)) for line in lines if line.strip()]


def _str(value: object) -> str:
    assert isinstance(value, str), f"{value!r} is not a string"
    return value


def _optional_str(value: object) -> str | None:
    return None if value is None else _str(value)


def golden_cases() -> list[GoldenCase]:
    return [
        GoldenCase(
            id=_str(line["id"]),
            lang=_str(line["lang"]),
            title=_optional_str(line["title"]),
            text=_optional_str(line["text"]),
            text_norm=_str(line["text_norm"]),
        )
        for line in golden_lines()
    ]


def golden_sha256() -> str:
    """The hash of the golden expectations (E7): each case's id, lang, title, text and text_norm as
    compact JSON, the lines sorted and joined by newlines."""
    keys = sorted(
        json.dumps(
            [line["id"], line["lang"], line["title"], line["text"], line["text_norm"]],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        for line in golden_lines()
    )
    return hashlib.sha256("\n".join(keys).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chars(*cps: int) -> str:
    """A text written as its code points, as the specification writes them (U+0671 U+0654)."""
    return "".join(map(chr, cps))


def code_points(text: str) -> str:
    """A text as its code points, so that a failure shows what no font shows."""
    return " ".join(f"U+{ord(ch):04X}" for ch in text) or "(empty)"


def idempotence_failures(inputs: Iterable[str], lang: str, limit: int = 20) -> list[str]:
    """The first `limit` inputs whose fold a second fold changes, each with both folds."""
    failures: list[str] = []
    for text in inputs:
        once = fold(text, lang)
        twice = fold(once, lang)
        if twice != once:
            failures.append(f"{code_points(text)} -> {code_points(once)} -> {code_points(twice)}")
            if len(failures) == limit:
                break
    return failures
