"""Which rows of the fold table and which D-lines a case exercises, read from its input with the
specification's steps (docs/plans/F7.md). gen_golden.py fills a non-anchor case's `rows` with them
and checks that every row an anchor claims by hand is one its input exercises. Rows 0 and 11 are not
detected: row 0 is D-S1, and row 11 only recomposes what earlier rows decomposed.
"""

import json
import re
import unicodedata
from pathlib import Path

from corpus.model import AE, HEH, HEH_DO, KAF_AR, KAF_FA, MAKSURA, YEH_AR, YEH_FA, ZWNJ

_TABLE = json.loads(
    (Path(__file__).resolve().parents[2] / "data" / "fold-table.json").read_text(encoding="utf-8")
)


def _cp(written: str) -> int:
    return int(written[2:], 16)


def _range_set(written: list[list[str]]) -> set[int]:
    return {cp for first, last in written for cp in range(_cp(first), _cp(last) + 1)}


ROW1 = _range_set(_TABLE["row1_deleted"])
ROW2 = _range_set(_TABLE["row2_deleted"])
D1 = {0x061C, *range(0x2060, 0x2065)}
SPACE_INSTEAD = _range_set(_TABLE["row10"]["space_instead"])
SORANI_ONLY = {chr(_cp(u)) for u in _TABLE["sorani_only_letters"]}
ALEF_VARIANTS = {chr(_cp(u)) for u in _TABLE["row3_alef"]["letters"]}
KEPT_ARABIC = set("چگپڤژؤئء")
KEPT_SORANI = set("ڕڵۆێەچگپڤژئ")
WHITE_SPACE = {
    *range(0x09, 0x0E),
    0x20,
    0x85,
    0xA0,
    0x1680,
    *range(0x2000, 0x200B),
    0x2028,
    0x2029,
    0x202F,
    0x205F,
    0x3000,
}
_URL_PREFIX = re.compile(r"https?://|www\.", re.IGNORECASE | re.ASCII)
_BARE_DOMAIN = re.compile(r"[A-Za-z0-9-]+\.(?:com|org|net|iq)\b")


def kept(ch: str) -> bool:
    return unicodedata.category(ch)[0] in "LMN" and ord(ch) not in SPACE_INSTEAD


def _tokens(s: str) -> list[tuple[int, int, bool]]:
    """(start, end, is_tag) spans by D5 and D7's rules."""
    out: list[tuple[int, int, bool]] = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        if (
            ch in "#@"
            and (i == 0 or not kept(s[i - 1]))
            and i + 1 < n
            and (kept(s[i + 1]) or s[i + 1] == "_")
        ):
            j = i + 1
            while j < n and (kept(s[j]) or s[j] == "_"):
                j += 1
            out.append((i, j, True))
            i = j
        elif kept(ch):
            j = i
            while j < n and kept(s[j]):
                j += 1
            out.append((i, j, False))
            i = j
        else:
            i += 1
    return out


def _without_urls(s: str) -> tuple[str, bool]:
    out: list[str] = []
    i, found = 0, False
    while i < len(s):
        if (i == 0 or not kept(s[i - 1])) and _URL_PREFIX.match(s, i):
            found = True
            while i < len(s) and ord(s[i]) not in WHITE_SPACE:
                i += 1
            continue
        out.append(s[i])
        i += 1
    return "".join(out), found


def _rows_of_one(sorani_mode: bool, raw: str) -> set[int | str]:
    found: set[int | str] = set()
    s = raw
    if sorani_mode and HEH + ZWNJ in s:
        found.add("D-S1")
        s = s.replace(HEH + ZWNJ, AE)
    if any(0x0653 <= ord(ch) <= 0x0655 for ch in raw):
        found.add("D2")
    n = unicodedata.normalize("NFKC", s)
    if n != s or any(ord(ch) in ROW1 for ch in n):
        found.add(1)
    if any(ord(ch) in D1 for ch in n):
        found.add("D1")
    n = "".join(ch for ch in n if ord(ch) not in ROW1)
    n, url = _without_urls(n)
    if url or _BARE_DOMAIN.search(n):
        found.add("D3")
    if any(ord(ch) in ROW2 for ch in n):
        found.add(2)
    deleted = "".join(ch for ch in n if ord(ch) not in ROW2)
    n = unicodedata.normalize("NFKC", deleted)
    if n != deleted:
        found.add("D7")  # the second NFKC changed what tokens are found on
    spans = _tokens(n)
    for start, end, is_tag in spans:
        token = n[start:end]
        sorani = sorani_mode or any(ch in SORANI_ONLY for ch in token)
        if not sorani_mode and sorani:
            found.add("D7")  # the Sorani-token override
        if is_tag:
            found.add("D5")
        if any(ch in ALEF_VARIANTS for ch in token) or re.search(
            "\N{ARABIC LETTER ALEF}[\N{ARABIC MADDAH ABOVE}-\N{ARABIC HAMZA BELOW}]", token
        ):
            found.add(3)
        if "\N{ARABIC LETTER TEH MARBUTA}" in token:
            found.add(4)
        if sorani and HEH_DO in token:
            found.update({4, "D-S2"})
        if (KAF_FA if not sorani else KAF_AR) in token:
            found.add(5)
        if any(ch in token for ch in ((YEH_FA, MAKSURA) if not sorani else (YEH_AR, MAKSURA))):
            found.add(6)
        if any(ch in (KEPT_SORANI if sorani else KEPT_ARABIC) for ch in token):
            found.add(7)
        if any(0x0660 <= ord(ch) <= 0x0669 or 0x06F0 <= ord(ch) <= 0x06F9 for ch in token):
            found.add(8)
        if token.casefold() != token:
            found.add(9)
    joined = " ".join(n[a:b] for a, b, _ in spans)
    if any(ch in n for ch in "#@_"):
        found.add("D5")  # the hashtag and mention rule decides what #, @ and _ become
    # Row 10 is the token rules: URLs, hashtags and mentions, and the separators.
    if joined != n or url or "D5" in found:
        found.add(10)
    if any(
        unicodedata.category(ch)[0] == "S"
        or ord(ch) in SPACE_INSTEAD
        or unicodedata.category(ch) in ("Cn", "Co", "Cf")
        or (unicodedata.category(ch) == "Cc" and ord(ch) not in WHITE_SPACE)
        for ch in n
    ):
        found.add("D4")
    if "_" in n and any(
        not is_tag and end < len(n) and n[end] == "_" for _start, end, is_tag in spans
    ):
        found.add("D7")  # _ joins tokens only inside a hashtag or mention
    if any(ord(ch) in WHITE_SPACE and ch != " " for ch in raw) or "  " in raw or raw != raw.strip():
        found.add("D6")
    if not spans:
        found.add("D8")
    return found


def rows_of(lang: str, title: str | None, text: str) -> tuple[int | str, ...]:
    found: set[int | str] = set()
    for part in (title, text):
        if part:
            found |= _rows_of_one(lang == "ckb", part)
    numbers = sorted(r for r in found if isinstance(r, int))
    order = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D-S1", "D-S2"]
    return (*numbers, *(d for d in order if d in found))
