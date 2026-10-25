"""D-2: NFC and lower case are those of Unicode 15.1.0. The helpers keep the code points 15.1 leaves
unassigned, and rely on a later runtime giving 15.1's result for the runs between them."""

import unicodedata
from typing import cast

import pytest

from listening_contracts._artefacts import registry
from listening_contracts._text import check_unicode_version, lower_case, nfc
from listening_contracts.errors import ContractError

REGISTRY = cast(dict[str, object], registry("unicode-15.1-unassigned.json"))
RANGES = cast(list[list[int]], REGISTRY["ranges"])
LISTED = {cp for first, last in RANGES for cp in range(first, last + 1)}


def _holds_listed(s: str) -> bool:
    return any(ord(ch) in LISTED for ch in s)


def test_lists_the_ranges_of_unicode_15_1_surrogates_excluded() -> None:
    assert REGISTRY["unicode_version"] == "15.1.0"
    assert len(RANGES) == 707
    assert not any(0xD800 <= cp <= 0xDFFF for cp in LISTED)


def test_the_list_is_the_unassigned_set_of_unicode_15_1() -> None:
    """Equal to the runtime's Cn set on Unicode 15.1.0; on a later runtime it holds that set."""
    cn = {cp for cp in range(0x110000) if unicodedata.category(chr(cp)) == "Cn"}
    if unicodedata.unidata_version == "15.1.0":
        assert cn == LISTED
    else:
        assert cn <= LISTED


def test_a_code_point_unicode_15_1_assigns_never_maps_into_a_listed_one() -> None:
    """No decomposition, composition or lower case of a 15.1 code point yields a listed one."""
    bad: list[str] = []
    for cp in range(0x110000):
        if 0xD800 <= cp <= 0xDFFF:
            continue
        c = chr(cp)
        if cp not in LISTED:
            nfd, nfc_ = unicodedata.normalize("NFD", c), unicodedata.normalize("NFC", c)
            if _holds_listed(nfd + nfc_ + c.lower()):
                bad.append(f"U+{cp:04X}")
            continue
        # A later composite whose parts 15.1 assigns would let NFC of 15.1 text yield it.
        parts = unicodedata.normalize("NFD", c)
        if (
            parts != c
            and not _holds_listed(parts)
            and _holds_listed(unicodedata.normalize("NFC", parts))
        ):
            bad.append(f"U+{cp:04X}")
    assert bad == []


def test_passes_a_listed_code_point_through_nfc_and_lower_case_unchanged() -> None:
    # ARABIC PEPET (Unicode 16.0) between a kasra and its letter: no reordering across it.
    assert nfc("\u0628\u0897\u0650\u0631") == "\u0628\u0897\u0650\u0631"
    # TODHRI LETTER I and a combining dot above, which Unicode 16.0 composes into TODHRI LETTER EI.
    assert nfc("\U000105d2\u0307") == "\U000105d2\u0307"
    # LATIN CAPITAL LETTER RAMS HORN (Unicode 16.0) keeps its case.
    assert lower_case("\ua7cb") == "\ua7cb"


def test_normalises_and_lower_cases_either_side_of_a_listed_code_point_as_15_1_does() -> None:
    assert nfc("e\u0301\U0001fae9e\u0301") == "\u00e9\U0001fae9\u00e9"
    assert nfc("\u0627\u0654\u0897\u0627\u0654") == "\u0623\u0897\u0623"
    assert lower_case("ABC\ua7cbDEF") == "abc\ua7cbdef"
    # A listed code point is neither cased nor case-ignorable in 15.1: a sigma before it is final.
    assert lower_case("A\u03a3\ua7cb") == "a\u03c2\ua7cb"
    assert lower_case("A\ua7cb\u03a3") == "a\ua7cb\u03c3"


@pytest.mark.parametrize("version", ["15.0", "15.0.0", "14.0", "9.0", "", "unicode"])
def test_refuses_a_unicode_version_below_15_1(version: str) -> None:
    with pytest.raises(ContractError, match="unicode_version"):
        check_unicode_version(version)


@pytest.mark.parametrize(
    "version", ["15.1", "15.1.0", "16.0", "17.0", "17.0.0", unicodedata.unidata_version]
)
def test_accepts_unicode_15_1_and_later_and_the_runtimes_own_version(version: str) -> None:
    check_unicode_version(version)
