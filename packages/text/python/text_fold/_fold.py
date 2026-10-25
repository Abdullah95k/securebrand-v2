"""fold and text_norm, as docs/plans/F7.md "Fold specification v1" defines them: rows 0 to 11 of the
fold table and the detail lines D1 to D11, the E1 lines included. The steps run in this order:

    checks (D8), row 0 (Sorani mode), row 1 (NFKC, deletions), D3 (URLs deleted),
    row 2 (deletions, then NFKC again), tokens (D5, D7), rows 3 to 9 on each token,
    assembly (D6), row 11 (NFKC again)

Every map, range and label comes from fold-table.json and contracts' LANG_LABELS; every Unicode
property from Python 3.13's Unicode 15.1.0 (text_fold.unicode).
"""

import re
import unicodedata
from collections.abc import Iterable, Mapping

from text_fold._data import LANG_LABELS, TABLE
from text_fold.errors import TextError
from text_fold.unicode import UNICODE_VERSION, WHITE_SPACE, char_class

if TABLE.unicode != UNICODE_VERSION:
    raise TextError(
        "unicode_version",
        f"fold-table.json is for Unicode {TABLE.unicode}, the twin for {UNICODE_VERSION}",
    )

SORANI_ONLY_LETTERS: tuple[str, ...] = TABLE.sorani_only_letters

_LANG_LABELS = frozenset(LANG_LABELS)
_SORANI_LABELS = frozenset(TABLE.sorani_labels)
_SORANI_LETTERS = frozenset(TABLE.sorani_only_letters)
_ALEF_MARKS = frozenset(
    chr(cp) for first, last in TABLE.alef_marks_deleted for cp in range(first, last + 1)
)


def _deleting(ranges: Iterable[tuple[int, int]]) -> dict[int, None]:
    return dict.fromkeys((cp for first, last in ranges for cp in range(first, last + 1)), None)


_ROW1_DELETED = _deleting(TABLE.row1_deleted)
_ROW2_DELETED = _deleting(TABLE.row2_deleted)


def _digit(ch: str) -> str:
    cp = ord(ch)
    for digits in TABLE.digits:
        if digits.first <= cp <= digits.last:
            return chr(digits.becomes_first + cp - digits.first)
    return ch


def _letter_table(letters: Mapping[str, str]) -> dict[int, str]:
    """Rows 3 (the alef letters to alef U+0627), 4 to 6 (one fold's letters) and 8 (digits),
    composed in that order into one translation table: each maps one code point to one, so they
    compose per code point."""
    alefs = frozenset(TABLE.alef_letters)
    digits = (chr(cp) for d in TABLE.digits for cp in range(d.first, d.last + 1))
    table: dict[int, str] = {}
    for ch in {*alefs, *letters, *digits}:
        mapped = TABLE.alef if ch in alefs else ch
        mapped = _digit(letters.get(mapped, mapped))
        if mapped != ch:
            table[ord(ch)] = mapped
    return table


_ARABIC_FOLD = _letter_table(TABLE.arabic)
_SORANI_FOLD = _letter_table(TABLE.sorani)

# Each code point's class for the token rules: one str.translate gives a text's classes, and a
# regular expression over them finds its tokens. Kept (D4) is general category L*, M* or N*, less
# row 10's space_instead ranges; the tag signs and the joiner have classes of their own (D5).
_KEPT, _SIGN, _JOINER, _OTHER = "k", "#", "_", " "


def _class_table() -> str:
    table = bytearray(_OTHER * 0x110000, "ascii")
    kept = ord(_KEPT)
    for cp in range(0x110000):
        if unicodedata.category(chr(cp))[0] in "LMN":
            table[cp] = kept
    for first, last in TABLE.space_instead:
        table[first : last + 1] = bytes(_OTHER * (last + 1 - first), "ascii")
    for sign in TABLE.tag_signs:
        table[ord(sign)] = ord(_SIGN)
    table[ord(TABLE.tag_joiner)] = ord(_JOINER)
    return table.decode("ascii")


_CLASSES = _class_table()
# D5: a hashtag or mention is a sign that no kept character precedes, then a run of kept characters
# and joiners (at least one). D7: else a word, a run of kept characters; the joiner joins no word.
_TOKENS = re.compile(r"(?<!k)#[k_]+|k+")
# D3: compared without ASCII case. After row 1's NFKC no other character case-folds to a letter of
# a prefix (long s U+017F and the Kelvin sign are gone), so ASCII case is all the case there is.
_URL_START = re.compile("|".join(map(re.escape, TABLE.url_prefixes)), re.IGNORECASE | re.ASCII)
_WHITE_SPACE = re.compile(char_class(WHITE_SPACE))
_SURROGATE = re.compile(r"[\ud800-\udfff]")


def _check_lang(lang: object) -> None:
    if lang is None:
        raise TextError("no_lang", "a language label is required")
    if not isinstance(lang, str) or lang not in _LANG_LABELS:
        raise TextError("bad_lang", f"the language label must be one of {', '.join(LANG_LABELS)}")


def _sorani_mode(text: object, lang: object) -> bool:
    """The refusals (D8), in this order; then true for Sorani mode, false for Arabic mode."""
    if not isinstance(text, str):
        raise TextError("not_string", f"the text is a {type(text).__name__}, not a str")
    _check_lang(lang)
    if _SURROGATE.search(text):
        raise TextError("not_unicode", "the text holds a lone surrogate")
    return lang in _SORANI_LABELS


def _delete_urls(text: str) -> str:
    """D3: a URL starts at a prefix that no kept character precedes and runs up to the next
    White_Space code point; each is deleted whole, and the scan resumes after it."""
    pieces: list[str] = []
    copied = 0
    url = _URL_START.search(text)
    while url is not None:
        start = url.start()
        if start > 0 and _CLASSES[ord(text[start - 1])] == _KEPT:
            url = _URL_START.search(text, start + 1)
            continue
        space = _WHITE_SPACE.search(text, url.end())
        end = len(text) if space is None else space.start()
        pieces.append(text[copied:start])
        copied = end
        url = _URL_START.search(text, end)
    pieces.append(text[copied:])
    return "".join(pieces)


def _drop_marks_after_alef(token: str) -> str:
    """Row 3 (E1): U+0653 to U+0655 are deleted from the run of combining marks right after an alef
    U+0627. NFKC would compose each with that alef into U+0622, U+0623 or U+0625, which fold back
    to alef; a second fold would otherwise delete them."""
    out: list[str] = []
    after_alef = False
    for ch in token:
        if unicodedata.category(ch)[0] == "M":
            if after_alef and ch in _ALEF_MARKS:
                continue
        else:
            after_alef = ch == TABLE.alef
        out.append(ch)
    return "".join(out)


def _fold_token(token: str, sorani: bool) -> str:
    """Rows 3 to 9 on one token (D7): the Sorani fold in Sorani mode or for a token holding a
    Sorani-only letter, else the Arabic fold; then the alef marks, then full case folding."""
    sorani = sorani or not _SORANI_LETTERS.isdisjoint(token)
    token = token.translate(_SORANI_FOLD if sorani else _ARABIC_FOLD)
    if not _ALEF_MARKS.isdisjoint(token):
        token = _drop_marks_after_alef(token)
    return token.casefold()


def fold(text: str, lang: str) -> str:
    """Fold `text` under `lang`, one of contracts' LANG_LABELS: under ckb every token takes the
    Sorani fold; under the others the Arabic fold, except a token holding a Sorani-only letter.

    Raises TextError: not_string, no_lang, bad_lang or not_unicode (a lone surrogate).
    """
    sorani = _sorani_mode(text, lang)
    if sorani:
        text = text.replace(TABLE.row0_sequence, TABLE.row0_becomes)
    text = unicodedata.normalize("NFKC", text).translate(_ROW1_DELETED)
    text = unicodedata.normalize("NFKC", _delete_urls(text).translate(_ROW2_DELETED))
    pieces: list[str] = []
    end = 0
    for token in _TOKENS.finditer(text.translate(_CLASSES)):
        folded = _fold_token(text[token.start() : token.end()], sorani)
        if not folded:
            continue  # as specified, though unreachable: only marks after an alef are deleted
        if pieces and token.start() > end:
            pieces.append(" ")
        pieces.append(folded)
        end = token.end()
    return unicodedata.normalize("NFKC", "".join(pieces))


def text_norm(title: str | None, text: str | None, lang: str) -> str:
    """A record's text_norm: fold(title) and fold(text), the non-empty ones joined by one space,
    title first. A None input is skipped; the label is checked even when both are None."""
    present = [value for value in (title, text) if value is not None]
    if not present:
        _check_lang(lang)
    return " ".join(folded for folded in (fold(value, lang) for value in present) if folded)
