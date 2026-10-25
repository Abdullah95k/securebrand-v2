"""Writes fixtures/text/golden.jsonl from the case lists in scripts/corpus/ (docs/plans/F7.md).

An anchor keeps its hand-written text_norm. Every other case's text_norm is computed by the Python
twin, text_fold, from the specification, never by the TypeScript fold (E2); golden.test.ts then
diffs the TypeScript fold against every line. The twin must also agree with every anchor, or nothing
is written: a disagreement is resolved against the specification, never by copying one side.

    uv run python scripts/gen_golden.py            # write the file
    uv run python scripts/gen_golden.py --check    # exit 1 if the file differs from a generation
"""

import argparse
import json
import sys
import unicodedata
from collections.abc import Callable
from pathlib import Path

from corpus.anchors import ANCHORS
from corpus.iraqi_msa import IRAQI, MSA
from corpus.mixed_english_other import ENGLISH, MIXED, OTHER
from corpus.model import Case, Row
from corpus.rows import rows_of
from corpus.sorani_modes import FOLD_MODE, SORANI, UND
from corpus.technical import DIGITS, EMOJI, HASHTAGS, UNICODE_EDGE, URLS

GOLDEN = Path(__file__).resolve().parents[3] / "fixtures" / "text" / "golden.jsonl"
# The plan's order of categories (docs/plans/F7.md, "Count per category"), as in golden-case.ts.
CATEGORIES = (
    "iraqi_arabic",
    "msa",
    "sorani",
    "mixed",
    "english",
    "emoji",
    "urls",
    "hashtags",
    "digits",
    "unicode_edge",
    "fold_mode",
    "other",
    "und",
)
# One category after another, each in id order, so that its anchors come before the twin's cases.
CASES: list[Case] = sorted(
    [
        *ANCHORS,
        *IRAQI,
        *MSA,
        *SORANI,
        *MIXED,
        *ENGLISH,
        *EMOJI,
        *URLS,
        *HASHTAGS,
        *DIGITS,
        *UNICODE_EDGE,
        *FOLD_MODE,
        *OTHER,
        *UND,
    ],
    key=lambda case: (CATEGORIES.index(case.category), case.id),
)

TextNorm = Callable[[str | None, str | None, str], str]

# Written as \u escapes, so that the file shows them: controls, format characters, unassigned and
# private-use code points, separators other than the space, and the invisible variation selectors.
_HIDDEN_CATEGORIES = {"Cc", "Cf", "Cn", "Co", "Cs", "Zl", "Zp"}


def _hidden(ch: str) -> bool:
    cp = ord(ch)
    if 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF or cp == 0x034F:
        return True
    category = unicodedata.category(ch)
    return category in _HIDDEN_CATEGORIES or (category == "Zs" and ch != " ")


def _escape(ch: str) -> str:
    cp = ord(ch)
    if cp < 0x10000:
        return f"\\u{cp:04x}"
    cp -= 0x10000
    return f"\\u{0xD800 + (cp >> 10):04x}\\u{0xDC00 + (cp & 0x3FF):04x}"


def visible(json_line: str) -> str:
    # Every non-ASCII character of a line sits inside a JSON string, where an escape means the same.
    return "".join(_escape(ch) if _hidden(ch) else ch for ch in json_line)


def record(case: Case, rows: tuple[Row, ...], text_norm: str) -> str:
    value = {
        "id": case.id,
        "category": case.category,
        "lang": case.lang,
        "title": case.title,
        "text": case.text,
        "text_norm": text_norm,
        "rows": list(rows),
        "anchor": case.expect is not None,
        "must_pass": True,
        "origin": "invented",
        "source": None,
        "reviewed": False,
        "note": case.note,
    }
    return visible(json.dumps(value, ensure_ascii=False))


def twin() -> TextNorm | None:
    try:
        from text_fold import text_norm
    except ImportError:
        return None
    return text_norm


def generate() -> str:
    ids = [case.id for case in CASES]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        sys.exit(f"gen_golden: duplicate ids {duplicates}")
    fold = twin()
    lines: list[str] = []
    disagreements: list[str] = []
    false_claims: list[str] = []
    for case in CASES:
        computed = fold(case.title, case.text, case.lang) if fold is not None else None
        detected = rows_of(case.lang, case.title, case.text)
        if case.expect is not None:
            # An anchor's rows are its author's claims; each must be one its input exercises.
            unexercised = [row for row in case.rows if row not in detected]
            if unexercised:
                false_claims.append(f"{case.id}: claims {unexercised}, detected {list(detected)}")
            if computed is not None and computed != case.expect:
                disagreements.append(f"{case.id}: anchor {case.expect!r}, twin {computed!r}")
            lines.append(record(case, case.rows, case.expect))
        elif computed is None:
            sys.exit(f"gen_golden: {case.id} needs the twin (text_fold), which is not installed")
        else:
            lines.append(record(case, case.rows or detected, computed))
    if false_claims:
        sys.exit("gen_golden: anchors claim rows they do not exercise:\n" + "\n".join(false_claims))
    if disagreements:
        sys.exit("gen_golden: the twin disagrees with anchors:\n" + "\n".join(disagreements))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", 1)[0])
    parser.add_argument("--check", action="store_true", help="compare instead of writing")
    args = parser.parse_args()
    text = generate()
    if args.check:
        if GOLDEN.read_text(encoding="utf-8") != text:
            print(f"{GOLDEN} differs from a fresh generation", file=sys.stderr)
            return 1
        print(f"{GOLDEN} is up to date ({len(CASES)} cases)")
        return 0
    GOLDEN.write_text(text, encoding="utf-8")
    print(f"wrote {GOLDEN} ({len(CASES)} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
