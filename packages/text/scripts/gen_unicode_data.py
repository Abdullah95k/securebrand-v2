"""Writes packages/text/data/unicode-15.1.json, the Unicode 15.1 data the TypeScript fold needs and
its runtime cannot give it: Node 24 follows Unicode 17.0, and the fold's classes, White_Space and
case folding are those of 15.1 in both languages (D-2, D11 of docs/plans/F7.md). The code points
15.1 leaves unassigned are contracts' (registries/unicode-15.1-unassigned.json, Q6), so they are not
repeated here; NFKC is the runtime's, applied between them.

It uses only the standard library and refuses to run unless unicodedata is Unicode 15.1.0 (Python
3.13). It is run by hand, once per Unicode change; unicode.test.ts regenerates it and compares.

    python3 scripts/gen_unicode_data.py            # write data/unicode-15.1.json
    python3 scripts/gen_unicode_data.py --stdout   # print it instead
"""

import json
import sys
import unicodedata
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "unicode-15.1.json"

# PropList.txt's White_Space for Unicode 15.1; unicodedata has no property lists. main() checks it
# against str.isspace(), which also counts the information separators U+001C to U+001F.
WHITE_SPACE = [
    (0x0009, 0x000D),
    (0x0020, 0x0020),
    (0x0085, 0x0085),
    (0x00A0, 0x00A0),
    (0x1680, 0x1680),
    (0x2000, 0x200A),
    (0x2028, 0x2029),
    (0x202F, 0x202F),
    (0x205F, 0x205F),
    (0x3000, 0x3000),
]


def code_points() -> range:
    return range(0x110000)


def ranges(members: list[int]) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for cp in members:
        if out and out[-1][1] == cp - 1:
            out[-1] = (out[-1][0], cp)
        else:
            out.append((cp, cp))
    return out


def by_class(major: str) -> list[tuple[int, int]]:
    return ranges([cp for cp in code_points() if unicodedata.category(chr(cp))[0] == major])


def case_folding() -> list[tuple[int, list[int]]]:
    out: list[tuple[int, list[int]]] = []
    for cp in code_points():
        if 0xD800 <= cp <= 0xDFFF:
            continue
        folded = chr(cp).casefold()
        if folded != chr(cp):
            out.append((cp, [ord(ch) for ch in folded]))
    return out


def check_white_space() -> None:
    spaces = {cp for cp in code_points() if chr(cp).isspace()} - set(range(0x1C, 0x20))
    listed = {cp for first, last in WHITE_SPACE for cp in range(first, last + 1)}
    if spaces != listed:
        sys.exit(
            f"gen_unicode_data: White_Space differs from str.isspace(): {sorted(spaces ^ listed)}"
        )


def render() -> str:
    """One range or mapping per line, so that a Unicode change reads as a small diff."""

    def block(name: str, rows: list[str], last: bool = False) -> str:
        body = ",\n".join(f"    {row}" for row in rows)
        return f'  "{name}": [\n{body}\n  ]' + ("" if last else ",")

    lines = [
        "{",
        f'  "unicode": "{unicodedata.unidata_version}",',
        '  "generator": "packages/text/scripts/gen_unicode_data.py",',
        block("letters", [json.dumps(list(r)) for r in by_class("L")]),
        block("marks", [json.dumps(list(r)) for r in by_class("M")]),
        block("numbers", [json.dumps(list(r)) for r in by_class("N")]),
        block("white_space", [json.dumps(list(r)) for r in WHITE_SPACE]),
        block("case_folding", [json.dumps([cp, cps]) for cp, cps in case_folding()], last=True),
        "}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    if unicodedata.unidata_version != "15.1.0":
        sys.exit(
            f"gen_unicode_data: unicodedata is Unicode {unicodedata.unidata_version}, not 15.1.0; "
            "run it with Python 3.13"
        )
    check_white_space()
    text = render()
    if "--stdout" in sys.argv[1:]:
        sys.stdout.write(text)
    else:
        OUT.write_text(text, encoding="utf-8")
        print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
