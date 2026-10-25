"""The Unicode version the fold is defined on (D-2, D11 of docs/plans/F7.md), and the one property
of it the standard library does not expose.

Every general category, NFKC and case folding the twin uses comes from Python 3.13's unicodedata and
str.casefold, which follow Unicode 15.1.0. The package refuses to import on any other version, so it
never folds by another Unicode's rules.
"""

import unicodedata
from collections.abc import Iterable

from text_fold.errors import TextError

UNICODE_VERSION = "15.1.0"

# White_Space from Unicode 15.1's PropList.txt: unicodedata has no property lists, and str.isspace()
# is not White_Space (it also counts the information separators U+001C to U+001F).
WHITE_SPACE: tuple[tuple[int, int], ...] = (
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
)


def check_unicode_version(version: str) -> None:
    """Refuse a Unicode version other than the fold's (TextError unicode_version)."""
    if version != UNICODE_VERSION:
        raise TextError(
            "unicode_version",
            f"the runtime's Unicode is {version or 'unknown'}, the fold's is {UNICODE_VERSION} "
            "(run it on Python 3.13)",
        )


check_unicode_version(unicodedata.unidata_version)


def char_class(ranges: Iterable[tuple[int, int]]) -> str:
    """A regular-expression character class of code-point ranges, every bound escaped."""
    return "[" + "".join(f"\\U{first:08x}-\\U{last:08x}" for first, last in ranges) + "]"
